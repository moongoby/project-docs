---
project: AADS
task_id: AADS-186E-2
completed_at: 2026-03-09T09:01:48+09:00
---

# AADS-186E-2 작업 결과 보고서
## Extended Thinking 활성화 + Programmatic Tool Calling + 4계층 영속 메모리

---

## FIND — 현황 파악

### 기존 파일 상태 (작업 전)
- `model_selector.py`: `_stream_anthropic()` 내 `budget_tokens=8000`, `max_tokens=8192` 하드코딩
- `intent_router.py`: `cto_code_analysis/cto_verify/cto_impact` thinking 미설정, sonnet 사용
- `tool_registry.py` / `tool_executor.py`: 메모리·PTC 도구 미존재
- `context_builder.py`: CKP 레이어만 존재, 메모리 레이어 미존재
- `memory_manager.py`: 미존재
- `ptc_executor.py`: 미존재
- `024_memory_tables.sql`: 미존재

### 발견 사항
- AADS-186D 커밋(4587714)에 `intent_router.py`, `context_builder.py`, `tool_registry.py`, `tool_executor.py` 의 일부 기반 코드가 이미 포함되어 있었음
- 컨테이너는 소스를 볼륨 마운트하지 않음 → 테스트 시 `docker cp` 필요

---

## LAYOUT — 설계

### Part 1: Extended Thinking
- 목표: CTO 인텐트 4개(cto_strategy/cto_code_analysis/cto_verify/cto_impact)에서 Opus + 사고 활성화
- 설계: `intent_router.py` thinking:True + claude-opus 라우팅, `model_selector.py` Opus-only guard + env 스위치

### Part 2: Programmatic Tool Calling
- 목표: 다중 도구 병렬 실행으로 토큰 37% 절감
- 설계: `PTCExecutor` 클래스, 읽기 전용 `CALLABLE_TOOLS` 화이트리스트, tool_registry code_execution 도구

### Part 3: 4계층 영속 메모리
- 목표: 세션 간 전략적 맥락 완전 보존
- 설계:
  - Layer 2: `session_notes` 테이블 + `MemoryManager.save_session_note()` (Haiku 자동 요약)
  - Layer 4: `ai_meta_memory` 테이블 + `learn/recall` (CEO 선호도, 패턴)
  - Context 주입: `<recent_sessions>` + `<learned_patterns>` XML 태그 (186B의 `<codebase_knowledge>`와 충돌 없음)

---

## OPERATE — 실행 내역

### 1. intent_router.py 수정 (기존 내용 확인 후 수정)
```
# 변경 전
"cto_code_analysis":{"model": "claude-sonnet", "tools": True, "group": "action"},
"cto_verify":       {"model": "claude-sonnet", "tools": True, "group": "system"},
"cto_impact":       {"model": "claude-sonnet", "tools": True, "group": "action"},

# 변경 후
"cto_code_analysis":{"model": "claude-opus", "tools": True, "group": "action",  "thinking": True},
"cto_verify":       {"model": "claude-opus", "tools": True, "group": "system",  "thinking": True},
"cto_impact":       {"model": "claude-opus", "tools": True, "group": "action",  "thinking": True},
```

### 2. model_selector.py 수정
- `_EXTENDED_THINKING_ENABLED` 환경변수 추가 (기본 true)
- `use_thinking = enabled AND use_extended_thinking AND model_alias == "claude-opus"` 조건
- `budget_tokens` 변경: 8000 → **10000**
- `max_tokens` 변경: 8192 → **16000** (thinking 활성화 시)

### 3. ptc_executor.py 신규 생성 (/root/aads/aads-server/app/services/ptc_executor.py)
```python
class PTCExecutor:
    CALLABLE_TOOLS = ["list_remote_dir", "read_remote_file", "health_check",
                      "query_database", "task_history", "cost_report",
                      "get_all_service_status", "inspect_service", "server_status",
                      "dashboard_query", "web_search_brave", "read_github_file"]

    async def execute_parallel(self, tool_calls: List[PTCToolCall]) -> PTCResult:
        """읽기 전용 도구만 허용, 병렬 실행, 토큰 절감 추정"""

    async def execute_ptc_code(self, code: str, tool_calls: List[Dict]) -> PTCResult:
        """코드 블록 기반 실행"""

    def run_parallel_health_check():
        """6개 서버 병렬 헬스체크 편의 함수"""
```

### 4. tool_registry.py 수정
메모리 도구 3개 + PTC code_execution 도구 추가:
- `code_execution` (type: code_execution_20250825)
- `save_note` (defer_loading: True)
- `recall_notes` (defer_loading: True)
- `learn_pattern` (defer_loading: True)
그룹 `"memory"` 추가: ["save_note", "recall_notes", "learn_pattern"]

### 5. migrations/024_memory_tables.sql 신규 생성
```sql
CREATE TABLE IF NOT EXISTS session_notes (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    summary TEXT NOT NULL,
    key_decisions TEXT[],
    action_items TEXT[],
    unresolved_issues TEXT[],
    projects_discussed VARCHAR(50)[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_meta_memory (
    id SERIAL PRIMARY KEY,
    category VARCHAR(30) NOT NULL,
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6. memory_manager.py 신규 생성 (/root/aads/aads-server/app/services/memory_manager.py)
```python
class MemoryManager:
    # Layer 2: Working Memory
    async def save_session_note(session_id, messages, summary=None, ...) -> SessionNote
    async def get_recent_notes(count=5) -> List[SessionNote]  # 1,500 토큰 제한

    # Layer 4: Meta Memory
    async def learn(category, key, value) -> None  # UPSERT + confidence 증가
    async def recall(category=None, query=None) -> List[Memory]  # 검색 + last_used_at
    async def get_meta_context(max_tokens=500) -> str  # 압축 텍스트

    # 자동 요약
    async def _auto_summarize(messages, ...) -> tuple  # Claude Haiku ~$0.001
```

### 7. tool_executor.py 수정
메모리 도구 핸들러 3개 추가:
- `_save_note()`: summary 필수 검증 후 memory_manager.save_session_note()
- `_recall_notes()`: query 있으면 recall(), 없으면 get_recent_notes()
- `_learn_pattern()`: category+key 필수 검증 후 memory_manager.learn()

### 8. context_builder.py 수정
`_build_memory_layer()` 함수 추가:
```python
async def _build_memory_layer() -> str:
    # <recent_sessions>: 최근 3개 세션 노트 (Layer 2)
    # <learned_patterns>: CEO 선호도+알려진이슈+결정이력 (Layer 4)
    # 186B <codebase_knowledge>와 별도 태그
```
- `build_messages_context()`: memory_layer 주입
- `build()`: layer2_full += memory_layer, Prompt Caching 시 함께 포함

### 9. system_prompt_v2.py 수정
`LAYER1_TOOLS`에 기억 관리 섹션 추가:
```
### 기억 관리 (AADS-186E-2)
- save_note: 현재 대화 중요 결정·이슈·액션 아이템을 영구 저장.
- recall_notes: 이전 세션 기록 검색.
- learn_pattern: CEO 선호도, 프로젝트 패턴, 반복 이슈를 기억.
```
`LAYER1_RULES`에 기억 규칙 추가:
```
## 기억 규칙 (AADS-186E-2)
- 중요한 결정이나 이슈가 나오면 save_note로 영구 저장한다.
- 세션 시작 시 이전 맥락을 <recent_sessions>로 자동 불러온다.
- CEO 선호도·반복 패턴은 learn_pattern으로 기억한다.
```

### 10. chat_service.py 수정
20턴 이상 대화 시 자동 세션 노트 저장 (비동기, 응답 지연 없음):
```python
# 11. 20턴 이상 시 세션 노트 자동 저장
if msg_count >= 20 and msg_count % 20 == 0:
    asyncio.create_task(_auto_save_session_note(session_id, raw_messages))
```
`_auto_save_session_note()` 백그라운드 함수 추가.

### 11. data/ai_memory.json 신규 생성
Layer 4 메타 메모리 초기값 8개:
- CEO 선호도 3개 (response_language, plan_before_execute, no_completion_without_verification)
- 프로젝트 패턴 2개 (aads_deployment, db_connection)
- 알려진 이슈 2개 (server_211_ssh, proc_grep_blocking)
- 결정 이력 1개 (extended_thinking_budget)

### 12. 테스트 생성 및 실행
**test_extended_thinking.py** (17개):
- TestExtendedThinkingIntents: cto_strategy/code_analysis/verify/impact → opus+thinking=True 확인
- TestModelSelectorThinkingConfig: Opus-only guard, budget_tokens=10000, max_tokens=16000
- TestSSEThinkingEvent: thinking/delta 이벤트 포맷, thinking 우선 순서
- TestExtendedThinkingEnvControl: EXTENDED_THINKING_ENABLED=false 비활성화 확인

**test_memory.py** (24개):
- TestSaveSessionNote: SessionNote 데이터클래스 확인
- TestGetRecentNotes: 1,500 토큰 이내, 최대 count 제한
- TestLearnAndRecall: Memory 데이터클래스, 유효 카테고리, UPSERT confidence, value 완전 교체
- TestGetMetaContext: 500 토큰 이내
- TestToolExecutorMemoryTools: save_note/recall_notes/learn_pattern 입력 검증
- TestContextBuilderMemoryLayer: XML 태그 분리 확인
- TestExtractProjects: 프로젝트명 추출 (대소문자 무관)

**테스트 결과**: 41/41 PASSED ✅

---

## WRAP UP — 완료 확인

### Git 커밋
- aads-server: `004508e` feat(AADS-186E-2): Extended Thinking + PTC + 4계층 영속 메모리
  - https://github.com/moongoby-GO100/aads-server/commit/004508e
- aads-docs: `a39365f` docs(AADS-186E-2): HANDOVER v12.14 + STATUS 업데이트

### 생성/수정된 파일 목록

| 파일 | 상태 | 변경 내용 |
|------|------|-----------|
| app/services/intent_router.py | 수정 | cto_code_analysis/verify/impact → opus+thinking:True |
| app/services/model_selector.py | 수정 | EXTENDED_THINKING_ENABLED + Opus guard + budget=10000 + max=16000 |
| app/services/ptc_executor.py | 신규 | PTCExecutor 병렬 실행기 |
| app/services/tool_registry.py | 수정 | code_execution+save_note+recall_notes+learn_pattern+memory 그룹 |
| app/services/memory_manager.py | 신규 | MemoryManager Layer2+Layer4 |
| app/services/tool_executor.py | 수정 | _save_note/_recall_notes/_learn_pattern 핸들러 |
| app/services/context_builder.py | 수정 | _build_memory_layer() + build/build_messages_context 연동 |
| app/core/prompts/system_prompt_v2.py | 수정 | 기억 관리 도구 안내 + 기억 규칙 추가 |
| app/services/chat_service.py | 수정 | 20턴 자동 세션 노트 저장 |
| migrations/024_memory_tables.sql | 신규 | session_notes + ai_meta_memory 테이블 |
| data/ai_memory.json | 신규 | Layer 4 메타 메모리 초기값 8개 |
| tests/test_extended_thinking.py | 신규 | 17개 테스트 |
| tests/test_memory.py | 신규 | 24개 테스트 |

### ACCEPTANCE CRITERIA 검증

| 항목 | 상태 | 비고 |
|------|------|------|
| CTO 인텐트 Extended Thinking 활성화 | ✅ | cto_strategy/code_analysis/verify/impact → opus+thinking:True |
| budget_tokens = 10000 | ✅ | model_selector.py |
| max_tokens = 16000 (thinking 시) | ✅ | model_selector.py |
| Interleaved thinking | ✅ | betas=["interleaved-thinking-2025-05-14"] (기존 코드) |
| 비-CTO 인텐트 thinking 비활성화 | ✅ | Opus-only guard |
| EXTENDED_THINKING_ENABLED 환경변수 | ✅ | 기본 true |
| SSE thinking 이벤트 | ✅ | chat_service.py 기존 코드 + 테스트 확인 |
| PTCExecutor 구현 | ✅ | ptc_executor.py |
| CALLABLE_TOOLS 7+개 | ✅ | 12개 읽기 전용 도구 |
| tool_registry code_execution 도구 | ✅ | code_execution_20250825 타입 |
| session_notes 테이블 | ✅ | 024_memory_tables.sql |
| ai_meta_memory 테이블 | ✅ | 024_memory_tables.sql |
| save_session_note (Haiku 자동요약) | ✅ | memory_manager.py |
| get_recent_notes (1,500 토큰 제한) | ✅ | memory_manager.py |
| learn (UPSERT + confidence 증가) | ✅ | memory_manager.py |
| recall (카테고리/쿼리 검색) | ✅ | memory_manager.py |
| get_meta_context (500 토큰) | ✅ | memory_manager.py |
| save_note 도구 (tool_registry) | ✅ | defer_loading: True |
| recall_notes 도구 | ✅ | defer_loading: True |
| learn_pattern 도구 | ✅ | defer_loading: True |
| context_builder <recent_sessions> | ✅ | _build_memory_layer() |
| context_builder <learned_patterns> | ✅ | _build_memory_layer() |
| 186B <codebase_knowledge>와 충돌 없음 | ✅ | 별도 XML 태그 |
| 20턴 자동 session_note 저장 | ✅ | chat_service.py 비동기 |
| system_prompt 메모리 도구 안내 | ✅ | LAYER1_TOOLS 기억 관리 섹션 |
| system_prompt 기억 규칙 | ✅ | LAYER1_RULES 기억 규칙 추가 |
| test_extended_thinking.py 17개 | ✅ | 17/17 PASSED |
| test_memory.py 24개 | ✅ | 24/24 PASSED |
| 전체 테스트 41/41 | ✅ | PASSED |
| HANDOVER.md 업데이트 | ✅ | v12.14 |
| STATUS.md 업데이트 | ✅ | AADS-186E-2 |
| Git 커밋 | ✅ | 004508e (server) + a39365f (docs) |

### 제약사항 준수 확인

| 제약 | 준수 여부 |
|------|-----------|
| Extended Thinking Opus 전용 | ✅ `model_alias == "claude-opus"` guard |
| budget_tokens 10,000 제한 | ✅ |
| PTC 읽기 전용 도구만 | ✅ _WRITE_TOOLS 블랙리스트 |
| Meta Memory UPSERT = 완전 교체 | ✅ `SET value = EXCLUDED.value` |
| session_notes 자동 저장 비동기 | ✅ `asyncio.create_task()` |
| 186B XML 태그 충돌 없음 | ✅ 별도 태그명 사용 |

### STATUS
- qa_status: PASS (41/41 테스트 통과)
- design_status: N/A
- 비용 절감 근거: PTC 병렬 실행 시 메시지 왕복 횟수 감소, 토큰 절감 추정 ~37%
