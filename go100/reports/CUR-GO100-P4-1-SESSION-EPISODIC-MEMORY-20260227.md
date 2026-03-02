# CUR-GO100-P4-1-SESSION-EPISODIC-MEMORY-20260227

**작성일**: 2026-02-27  
**태스크**: P4-1 세션 메모리(Redis) + 에피소드 기억 DB  
**상태**: 완료

---

## 1. 목표

백억이가 "기억하는 AI"로 진화 — 대화 컨텍스트 유지 + 장기 기억

- **세션 메모리(Redis)**: 턴 저장, 최근 N턴 컨텍스트, 언급 종목 추출, TTL 30분
- **에피소드 기억(DB)**: 선호/질문/전략관심/피드백 저장, 중요도 순 조회, 시스템 프롬프트용 요약
- **대명사 해석**: "그 종목", "아까 그거", "더 알려줘" 규칙 기반 치환 (LLM 호출 없음)
- **Agent 통합**: 대화 시작 시 컨텍스트 로드, 대화 종료 시 중요 정보 remember, 도구 get_my_memory / remember_this

---

## 2. 구현 요약

### 2.1 세션 메모리 (Redis)

| 파일 | 내용 |
|------|------|
| `backend/app/services/go100/memory/session_memory.py` | `SessionMemory` |

- **save_turn(session_id, role, content, metadata=None)**  
  - Redis key: `go100:session:{session_id}:turns` (List), JSON append, TTL 1800초(30분) 갱신
- **get_context(session_id, last_n=10)**  
  - 최근 N턴 대화 반환
- **get_mentioned_tickers(session_id)**  
  - 대화에서 6자리 종목코드 정규식 추출 + `stock_universe` ILIKE 검증 후 유효 종목코드만 반환  
  - Redis Set `go100:session:{id}:tickers` 보조 저장
- **clear_session(session_id)**  
  - 해당 세션 모든 키 삭제
- 기존 API 호환: `add_message`, `get_messages`, `push_stock`, `get_current_stock`, `build_context_prompt` 등 유지

### 2.2 대명사 해석 (규칙 기반)

| 파일 | 내용 |
|------|------|
| `backend/app/services/go100/memory/coreference_resolver.py` | `resolve(message, session_memory, session_id)` |

- "그 종목" 등 → `session_memory.get_current_stock(session_id)` 종목명으로 치환
- 후속 질문(주어 생략) → 해당 종목명을 문장 앞에 붙임 (예: "외국인 수급은?" → "삼성전자 외국인 수급은?")
- "아까 그거", "더 알려줘" → 이전 대화의 마지막 user 메시지로 컨텍스트 보강

### 2.3 에피소드 기억 DB

| 파일 | 내용 |
|------|------|
| `backend/migrations/039_go100_episodic_memory.sql` | `go100_user_memory` 테이블 생성 |
| `backend/app/services/go100/memory/episodic_memory.py` | `EpisodicMemory` (P4-1 스펙) |

- **테이블**: `go100_user_memory`  
  - `memory_id`, `user_id`, `memory_type`, `content`(JSONB), `importance`, `last_accessed`, `access_count`, `expires_at`, `created_at`
- **remember(user_id, memory_type, content, importance=5.0)**  
  - INSERT, importance 1.0~10.0 클램프
- **recall(user_id, memory_type=None, limit=20)**  
  - 중요도 순 조회, 조회 시 `access_count++`, `last_accessed` 갱신
- **recall_for_context(user_id)**  
  - Agent system prompt에 넣을 사용자 요약 텍스트 생성 (선호/전략관심/최근 질문/피드백)
- **forget(memory_id)**  
  - DELETE
- **decay()**  
  - 30일 이상 미접근 행의 `importance`를 0.5 감소 (크론 주기)
- 호환: `save_episode` → `remember(..., 'feedback', content)`, `build_episodic_context` → `recall_for_context`

### 2.4 Agent 메모리 래퍼 및 연동

| 파일 | 내용 |
|------|------|
| `backend/app/services/go100/ai/agent_memory_wrapper.py` | `run_agent_with_memory`, `end_session_and_save_episode` |

- 대화 시작: `save_turn(user)` + `resolve(message, sm, session_id)` + `get_context` + `recall_for_context` → `system_prompt_extra`
- Agent Core 호출 후: `save_turn(assistant)` + 종목 스택/`tickers` Set 갱신
- `ai_router.py`: 기존대로 `session_id` 생성/전달, `_run_agent_core` = `run_agent_with_memory`

### 2.5 Agent 도구

| 도구 | 설명 |
|------|------|
| **get_my_memory** | 내 기억/선호도 조회 (memory_type, limit 파라미터) |
| **remember_this** | 사용자가 직접 기억시키기 (content, memory_type, importance) |

- `backend/app/services/go100/ai/agent_tools.py`: 도구 정의 추가
- `backend/app/services/go100/ai/tool_executors.py`: `get_my_memory`, `remember_this` 실행 함수 및 `TOOL_EXECUTORS` 등록

### 2.6 크론 (기억 감쇠)

- **주기**: 매주 일요일 04:00
- **명령 예시**:  
  `0 4 * * 0 cd /root/kis-autotrade-v4 && PYTHONPATH=/root/kis-autotrade-v4 venv/bin/python3 -c "from backend.app.services.go100.memory.episodic_memory import EpisodicMemory; EpisodicMemory().decay()" >> /var/log/go100/memory_decay.log 2>&1`
- 로그 디렉터리: `/var/log/go100` (필요 시 생성)

---

## 3. 테스트 결과

- **Redis 세션**: `save_turn` 3턴 → `get_context(last_n=3)` 3건 반환, `clear_session` 정상 동작
- **대명사 해석**: "삼성전자 알려줘" → "그 종목 외국인 수급은?" → "삼성전자 외국인 수급은?" 치환 확인
- **에피소드**: `remember` → `recall` 중요도 순 조회, `recall_for_context` 사용자 요약 텍스트 생성 확인
- **decay**: `venv/bin/python3`로 실행 시 0건 업데이트 정상 (데이터 없음)

---

## 4. 참고 사항

- 기존 `go100_episodic_memory` 테이블(세션 에피소드용 구 스키마)은 유지. P4-1 사용자 기억은 `go100_user_memory` 사용.
- `get_mentioned_tickers`: 현재 6자리 종목코드 정규식 + `stock_universe` 검증. 한글 종목명 추출 확장 시 대화 텍스트에서 후보 추출 후 ILIKE 검증 추가 가능.
- Agent 호출 시 `user_id`는 `ai_router`에서 전달; 도구 실행은 기본 `user_id=2` 사용 (필요 시 context로 전달 가능).

---

## 5. 체크리스트

- [x] 코드 레포 커밋 (kis-autotrade-v4)
- [ ] project-docs 보고서 push (본 문서)
