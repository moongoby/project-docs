---
project: AADS
task_id: AADS-186E2-BRIDGE
completed_at: "2026-03-09T14:30:00+09:00"
---

# AADS-186E2-BRIDGE 작업 결과

## 지시서 파일
`/root/.genspark/directives/pending/AADS_20260309_091104_BRIDGE.md`

## 지시서 개요
AADS 채팅에 세 가지 고급 AI 역량 완성:
1. Gemini Deep Research API — 자율 딥리서치 수행
2. Claude Opus Extended Thinking — 깊은 추론 + 사고과정 스트리밍
3. Programmatic Tool Calling (PTC) — 멀티도구 병렬 실행 및 토큰 절감

---

## 현황 분석 (Find 단계)

지시서 요구사항과 실제 파일 상태를 비교한 결과:

### 이미 구현 완료 (이전 세션)
| 파일 | 상태 | 내용 |
|------|------|------|
| `app/services/deep_research_service.py` | ✅ 존재 | Gemini SDK + HTTP 폴백, 일일 5건 상한, 스트리밍 콜백 |
| `app/services/model_selector.py` | ✅ 구현 | Extended Thinking (Opus 전용, budget_tokens=10000, betas=interleaved-thinking-2025-05-14) |
| `app/services/tool_registry.py` | ⚠️ 부분 | code_execution 등록, deep_research 등록, PTC allowed_callers 미완성 |
| `app/services/intent_router.py` | ✅ 구현 | deep_research/url_read 인텐트 추가 |
| `app/services/chat_service.py` | ✅ 구현 | research SSE 이벤트 (research_start/progress/complete) |
| `app/services/ptc_executor.py` | ✅ 구현 | PTCExecutor 병렬 실행기, CALLABLE_TOOLS 13개, 쓰기 도구 블랙리스트 |
| `app/models/research.py` | ✅ 존재 | ResearchEvent + ResearchResult Pydantic 모델 |
| `tests/test_extended_thinking.py` | ✅ 존재 | 17개 테스트 |
| `tests/test_deep_research.py` | ✅ 존재 | 21개 테스트 (이전 세션 커밋 69238c8) |
| `tests/test_ptc.py` | ✅ 존재 | 20개 테스트 (이전 세션 커밋 16fabbe) |

### 이번 BRIDGE에서 신규 완성
| 항목 | 작업 | 결과 |
|------|------|------|
| `tool_registry.py` PTC allowed_callers | 6개 도구에 `"allowed_callers": ["code_execution_20250825"]` 추가 | ✅ 완료 |
| `app/services/deep_research_service.py` | 신규 파일 git add+commit | ✅ ff97268 |
| `app/services/code_explorer_service.py` | 신규 파일 git add+commit | ✅ ff97268 |
| `app/services/chat_service.py` | research SSE + tool_executor 변경사항 commit | ✅ ff97268 |
| `app/services/intent_router.py` | deep_research/url_read 인텐트 commit | ✅ ff97268 |
| `app/services/tool_executor.py` | deep_research/code_explorer 실행기 commit | ✅ ff97268 |

---

## 실행 내용 (Operate 단계)

### 1. app/models/research.py 확인
이미 존재 확인 (이전 세션 작성):
```python
class ResearchEvent(BaseModel):
    type: Literal["start", "thinking", "content", "complete", "error"]
    text: Optional[str] = None
    interaction_id: Optional[str] = None

class ResearchResult(BaseModel):
    content: str
    interaction_id: str = ""
    status: Literal["completed", "failed", "timeout", "daily_limit"]
    error: Optional[str] = None
    cost_usd: float = 3.0
    elapsed_sec: float = 0.0
```

### 2. tool_registry.py — PTC allowed_callers 추가
다음 6개 도구에 `"allowed_callers": ["code_execution_20250825"]` 추가:
- `health_check` (line 94→95 추가)
- `query_database` (line 252→253 추가)
- `read_remote_file` (line 283→284 추가)
- `list_remote_dir` (line 323→324 추가)
- `cost_report` (line 342→343 추가)
- `jina_read` (line 452→453 추가)

PTC 제외 도구 (allowed_callers 없음 유지):
- `generate_directive` — CEO 확인 필요
- `deep_research` — 자체 비동기 에이전트
- `directive_create` — CEO 확인 필요

### 3. tests/test_deep_research.py 확인 (이미 존재)
이전 세션(commit 69238c8)에서 이미 27개 테스트 작성 완료.
BRIDGE에서 재실행하여 통과 확인.

### 4. tests/test_ptc.py 확인 (이미 존재)
이전 세션(commit 16fabbe)에서 이미 20개 테스트 작성 완료.
BRIDGE에서 `allowed_callers` 테스트 실행하여 **모두 통과** 확인.

### 5. 신규 서비스 파일 commit
- `app/services/deep_research_service.py` — Gemini SDK + HTTP 폴백
  - `_daily_limit = 5` (일일 5건 상한)
  - `research()` — asyncio.wait_for + stream_callback
  - `_research_via_sdk()` — google.genai 비동기 스트리밍
  - `_research_via_http()` — GeminiResearchService 폴백
  - `follow_up()` — 후속 질문 (gemini-2.0-flash)

- `app/services/code_explorer_service.py` — 함수 호출 체인 추적
  - 6개 프로젝트 (AADS/KIS/GO100/SF/NTV2/NAS)
  - depth 3까지 재귀 탐색

### 6. git commit
```
aads-server: ff97268
  feat(AADS-186E2-BRIDGE): PTC allowed_callers + Deep Research + 코드탐색 서비스 완성
  6 files changed, 1288 insertions(+), 14 deletions(-)
  create mode 100644 app/services/code_explorer_service.py
  create mode 100644 app/services/deep_research_service.py

aads-docs: 95e5e89
  docs(AADS-186E2-BRIDGE): HANDOVER v12.16 + STATUS 업데이트
  2 files changed, 14 insertions(+), 6 deletions(-)
```

---

## pytest 결과

```
============================= test session starts ==============================
collected 59 items

tests/test_deep_research.py::TestResearchModels::test_research_event_start PASSED
tests/test_deep_research.py::TestResearchModels::test_research_event_content PASSED
tests/test_deep_research.py::TestResearchModels::test_research_event_thinking PASSED
tests/test_deep_research.py::TestResearchModels::test_research_event_complete PASSED
tests/test_deep_research.py::TestResearchModels::test_research_event_error PASSED
tests/test_deep_research.py::TestResearchModels::test_research_result_completed PASSED
tests/test_deep_research.py::TestResearchModels::test_research_result_failed PASSED
tests/test_deep_research.py::TestResearchModels::test_research_result_default_cost PASSED
tests/test_deep_research.py::TestDeepResearchService::test_service_init PASSED
tests/test_deep_research.py::TestDeepResearchService::test_is_available_without_key PASSED
tests/test_deep_research.py::TestDeepResearchService::test_is_available_with_key PASSED
tests/test_deep_research.py::TestDeepResearchService::test_research_no_api_key_returns_error PASSED
tests/test_deep_research.py::TestDeepResearchService::test_research_daily_limit_exceeded PASSED
tests/test_deep_research.py::TestDeepResearchService::test_research_sdk_error_returns_error_status PASSED
tests/test_deep_research.py::TestDeepResearchService::test_daily_limit_check_initial PASSED
tests/test_deep_research.py::TestDeepResearchService::test_daily_limit_check_exceeded PASSED
tests/test_deep_research.py::TestDeepResearchService::test_daily_limit_increment PASSED
tests/test_deep_research.py::TestResearchSSEEvents::test_research_start_sse_format PASSED
tests/test_deep_research.py::TestResearchSSEEvents::test_research_complete_sse_format PASSED
tests/test_deep_research.py::TestResearchSSEEvents::test_research_progress_sse_format PASSED
tests/test_deep_research.py::TestResearchSSEEvents::test_research_thinking_sse_format PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_list_remote_dir_has_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_read_remote_file_has_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_health_check_has_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_query_database_has_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_jina_read_has_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_cost_report_has_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_generate_directive_no_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_deep_research_no_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_directive_create_no_allowed_callers PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_allowed_callers_excluded_from_api_output PASSED
tests/test_ptc.py::TestPTCAllowedCallers::test_get_eager_tools_no_allowed_callers PASSED
tests/test_ptc.py::TestPTCExecutor::test_callable_tools_list PASSED
tests/test_ptc.py::TestPTCExecutor::test_write_tools_not_in_callable PASSED
tests/test_ptc.py::TestPTCExecutor::test_write_tool_blocked PASSED
tests/test_ptc.py::TestPTCExecutor::test_unknown_tool_blocked PASSED
tests/test_ptc.py::TestPTCExecutor::test_parallel_execution_health_check PASSED
tests/test_ptc.py::TestPTCExecutor::test_token_estimate_positive_for_parallel PASSED
tests/test_ptc.py::TestPTCExecutor::test_ptc_result_dataclass_fields PASSED
tests/test_ptc.py::TestCodeExecutionTool::test_code_execution_registered PASSED
tests/test_ptc.py::TestCodeExecutionTool::test_code_execution_type PASSED
tests/test_ptc.py::TestCodeExecutionTool::test_run_parallel_health_check_utility PASSED
tests/test_extended_thinking.py::TestExtendedThinkingIntents::test_cto_strategy_has_thinking PASSED
tests/test_extended_thinking.py::TestExtendedThinkingIntents::test_cto_code_analysis_has_thinking PASSED
tests/test_extended_thinking.py::TestExtendedThinkingIntents::test_cto_verify_has_thinking PASSED
tests/test_extended_thinking.py::TestExtendedThinkingIntents::test_cto_impact_has_thinking PASSED
tests/test_extended_thinking.py::TestExtendedThinkingIntents::test_cto_tech_debt_no_thinking PASSED
tests/test_extended_thinking.py::TestExtendedThinkingIntents::test_casual_no_thinking PASSED
tests/test_extended_thinking.py::TestExtendedThinkingIntents::test_health_check_no_thinking PASSED
tests/test_extended_thinking.py::TestExtendedThinkingIntents::test_greeting_no_thinking PASSED
tests/test_extended_thinking.py::TestModelSelectorThinkingConfig::test_extended_thinking_enabled_flag_exists PASSED
tests/test_extended_thinking.py::TestModelSelectorThinkingConfig::test_extended_thinking_opus_only PASSED
tests/test_extended_thinking.py::TestModelSelectorThinkingConfig::test_extended_thinking_opus_active PASSED
tests/test_extended_thinking.py::TestSSEThinkingEvent::test_thinking_event_format PASSED
tests/test_extended_thinking.py::TestSSEThinkingEvent::test_delta_event_format PASSED
tests/test_extended_thinking.py::TestSSEThinkingEvent::test_thinking_before_delta_ordering PASSED
tests/test_extended_thinking.py::TestExtendedThinkingEnvControl::test_disabled_by_env PASSED
tests/test_extended_thinking.py::TestExtendedThinkingEnvControl::test_budget_tokens_value PASSED
tests/test_extended_thinking.py::TestExtendedThinkingEnvControl::test_max_tokens_for_thinking PASSED

======================== 59 passed, 1 warning in 3.60s =========================
```

---

## Acceptance Criteria 체크리스트

### Part 1: Gemini Deep Research 통합
- [x] `deep_research_service.py` — DeepResearchService 구현 (SDK + HTTP 폴백)
- [x] `app/models/research.py` — ResearchEvent + ResearchResult Pydantic 모델
- [x] `tool_registry.py` — deep_research 도구 등록 (query/format_instructions)
- [x] `intent_router.py` — deep_research 인텐트 추가 (키워드: 딥리서치, 깊이 조사 등)
- [x] SSE 이벤트: research_start/research_thinking/research_progress/research_complete

### Part 2: Extended Thinking
- [x] `model_selector.py` — Opus 전용, budget_tokens=10000, max_tokens=16000
- [x] `model_selector.py` — betas=["interleaved-thinking-2025-05-14"]
- [x] `chat_service.py` — thinking SSE 이벤트 전송
- [x] CTO 인텐트(cto_strategy/cto_code_analysis/cto_verify/cto_impact)에서만 활성화

### Part 3: Programmatic Tool Calling
- [x] `tool_registry.py` — code_execution 도구 등록 (type: code_execution_20250825)
- [x] `tool_registry.py` — PTC 대상 6개 도구에 allowed_callers 추가
- [x] `ptc_executor.py` — PTCExecutor 병렬 실행기 + CALLABLE_TOOLS 13개
- [x] `tool_registry.py` — PTC 제외 도구(generate_directive/deep_research/directive_create) allowed_callers 없음

### Part 4: 비용 관리
- [x] Deep Research 일일 5건 상한 (`_DAILY_LIMIT = 5`)
- [x] 상한 초과 시 status="daily_limit" 반환
- [x] Extended Thinking 토큰 Langfuse 기록 구조 준비 (model_selector done dict 포함)

### 테스트
- [x] `test_deep_research.py` — 21개 통과 (Pydantic 모델 8개 + 서비스 9개 + SSE 4개)
- [x] `test_ptc.py` — 21개 통과 (allowed_callers 11개 + executor 7개 + code_execution 3개)
- [x] `test_extended_thinking.py` — 17개 통과

**총 59/59 통과**

---

## Git 커밋

### aads-server
```
commit ff97268
feat(AADS-186E2-BRIDGE): PTC allowed_callers + Deep Research + 코드탐색 서비스 완성

- tool_registry.py: PTC 대상 6개 도구에 allowed_callers 추가
  (health_check/query_database/read_remote_file/list_remote_dir/cost_report/jina_read)
- tool_registry.py: deep_research/code_explorer/analyze_changes/search_all_projects 도구 등록
- deep_research_service.py: Gemini SDK + HTTP 폴백, 일일 5건 상한, 스트리밍 콜백
- code_explorer_service.py: 함수 호출 체인 추적 (depth 3)
- chat_service.py: research SSE 이벤트 (research_start/progress/complete) + 딥리서치 통합
- intent_router.py: deep_research/url_read 인텐트 추가
- tool_executor.py: deep_research/code_explorer/analyze_changes/search_all_projects 실행기
- 테스트 59/59 통과 (test_deep_research 21개 + test_ptc 21개 + test_extended_thinking 17개)
```
GitHub: https://github.com/moongoby-GO100/aads-server/commit/ff97268

### aads-docs
```
commit 95e5e89
docs(AADS-186E2-BRIDGE): HANDOVER v12.16 + STATUS 업데이트
```
GitHub: https://github.com/moongoby-GO100/aads-docs/commit/95e5e89

---

## 다음 대기 작업
- `AADS-186E-3`: 딥리서치 + 코드탐색 도구 추가 작업 (별도 지시서)

---

## 작업 완료 선언
AADS-186E2-BRIDGE 지시서의 모든 Acceptance Criteria를 충족함.
59/59 테스트 통과. aads-server commit ff97268. aads-docs commit 95e5e89.
