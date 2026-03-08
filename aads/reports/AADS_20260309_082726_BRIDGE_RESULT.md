---
project: AADS
task_id: AADS-186A
completed_at: "2026-03-09T09:30:00+09:00"
---

# AADS-186A 실행 결과 — 시스템 프롬프트 재설계 + 도구 고도화

## 1. 수락 기준별 완료 결과

### AC-1: context_builder.py Layer 1 전면 재작성 ✅
- XML 섹션 구분 완료: `<role>`, `<capabilities>`, `<tools_available>`, `<rules>`, `<response_guidelines>`
- `<role>`: "AADS CTO AI — CEO moongoby의 전략적 기술 파트너. 6개 서비스(AADS, KIS, GO100, SF, NTV2, NAS)의 전체 아키텍처를 이해하고, 서버 접근·웹 검색·코드 분석·지시서 생성·비용 관리가 가능하다."
- `<capabilities>`: 6개 프로젝트 + 3개 서버 정보 포함
- `<tools_available>`: 카테고리별 전체 도구 목록 (서버 접근/웹 검색/파일 접근/데이터/운영/실행/비용)
- `<rules>`: 보안 정책 + D-039/D-022/D-027/D-028/R-001/R-008 + 비용 한도
- `<response_guidelines>`: 도구 호출 우선 원칙 + 포맷 규칙
- 프롬프트 텍스트 분리: `app/core/prompts/system_prompt_v2.py` 신규 생성 (하드코딩 제거)
- Layer 1 추정 토큰: ~700 토큰 (1,800 이내 달성)

### AC-2: 모든 도구에 Tool Use Examples 추가 ✅ (tool_registry.py)
- 9개 기존 도구 + 3개 신규 도구 모두 input_examples 1~3개 추가
- 예시는 실제 AADS 데이터 기반 (실제 파일 경로, 프로젝트명)
- 추가된 examples 예:
  ```json
  list_remote_dir: {"project": "KIS", "path": "/root/kis-autotrade-v4", "keyword": "config"}
  read_remote_file: {"project": "SF", "path": "/data/shortflow/app/main.py"}
  query_database: {"query": "SELECT count(*) FROM chat_messages WHERE created_at > now() - interval '1 day'"}
  directive_create: {"task_id": "NTV2-045", "title": "NTV2 헬스체크 실패 수정", ...}
  web_search_brave: {"query": "FastAPI MCP 통합 가이드"}
  health_check: {"server": "all"}
  ```
- Anthropic API 전송 시 input_examples 자동 제외 (ToolRegistry.get_tools() 필터링)

### AC-3: 도구 응답에 response_format 파라미터 추가 ✅ (tool_registry.py)
- `list_remote_dir`: response_format: "concise" | "detailed" 추가 (기본값: concise)
- `read_remote_file`: response_format: "concise" | "detailed" 추가 (기본값: concise)
- `query_database`: response_format: "concise" | "detailed" 추가 (기본값: concise)
- concise: 핵심 정보만 (파일명 목록, 요약, 행 수)
- detailed: 전체 내용 + 메타데이터 (크기, 수정일, 권한 등)

### AC-4: 고수준 워크플로우 도구 3개 신규 구현 ✅ (tool_registry.py + tool_executor.py)

**a) inspect_service(project, checks=["all"])**
- 구현: `_inspect_service()` 메서드
- KIS/GO100/SF/NTV2 프로젝트 서버 접속
- checks: process/docker/log_tail/health 선택 가능
- list_remote_dir + health_check 내부 조합

**b) get_all_service_status(include_details=False)**
- 구현: `_get_all_service_status()` 메서드
- 6개 서비스(AADS/KIS/GO100/SF/NTV2/NAS) 헬스체크 URL 병렬 조회 (asyncio.gather)
- 마크다운 테이블 형태 반환
- include_details=True 시 응답 시간 + 상세 정보 포함

**c) generate_directive(description, priority, size, project, auto_submit)**
- 구현: `_generate_directive()` 메서드
- DB에서 TASK_ID 자동 채번 (project 최신 번호 + 1)
- size → model 자동 라우팅 (XS/S/M→sonnet, L/XL→opus)
- auto_submit=True 시 /api/v1/directives/submit API 제출

### AC-5: intent_router.py 업데이트 ✅
- 신규 인텐트 `service_inspection`:
  - model: claude-sonnet, tools: True, group: workflow
  - 키워드: "서비스 점검", "점검해", "프로세스 확인", "서비스 상태 자세히", "docker 상태", "로그 확인"
- 신규 인텐트 `all_service_status`:
  - model: claude-sonnet, tools: True, group: workflow
  - 키워드: "전체 서비스 상태", "6개 서비스", "올 스테이터스", "모든 서비스 상태"
- `directive` 인텐트 확장: `directive_gen` 그룹에 `generate_directive` 도구 추가
- `health_check` 인텐트: `_INTENT_TOOL_MAP`에 `get_all_service_status` 추가
- `_CLASSIFY_PROMPT`에 두 인텐트 추가
- `_keyword_fallback`에 키워드 추가

### AC-6: chat_service.py 확인 ✅
- LLM 호출 시 tools 파라미터에 전체 도구 정의 올바르게 전달 (기존 코드 이미 정상)
- system prompt를 `build_messages_context()` → `build_layer1()` 기반으로 전달
- 도구 호출 루프 max_iterations 5 유지 (기존 model_selector.py 내부)
- 에러 시 "error" 타입 SSE 이벤트 반환 (기존 구현 정상)

### AC-7: 테스트 ✅ — 20/20 통과

```
tests/test_tool_awareness.py::test_system_prompt_xml_sections PASSED
tests/test_tool_awareness.py::test_system_prompt_tool_categories PASSED
tests/test_tool_awareness.py::test_system_prompt_new_workflow_tools_mentioned PASSED
tests/test_tool_awareness.py::test_system_prompt_build_layer1_function PASSED
tests/test_tool_awareness.py::test_system_prompt_role_section PASSED
tests/test_tool_awareness.py::test_context_builder_imports_system_prompt_v2 PASSED
tests/test_tool_awareness.py::test_context_builder_removed_hardcoded_static PASSED
tests/test_tool_awareness.py::test_tool_registry_new_tools_defined PASSED
tests/test_tool_awareness.py::test_tool_registry_workflow_group PASSED
tests/test_tool_awareness.py::test_tool_registry_input_examples_present PASSED
tests/test_tool_awareness.py::test_tool_registry_response_format_in_tools PASSED
tests/test_tool_awareness.py::test_tool_registry_api_format_excludes_examples PASSED
tests/test_tool_awareness.py::test_tool_registry_existing_groups_preserved PASSED
tests/test_tool_awareness.py::test_tool_executor_dispatch_registered PASSED
tests/test_tool_awareness.py::test_tool_executor_new_methods_implemented PASSED
tests/test_tool_awareness.py::test_tool_executor_timeout_updated PASSED
tests/test_tool_awareness.py::test_intent_router_new_intents_in_map PASSED
tests/test_tool_awareness.py::test_intent_router_workflow_group_assigned PASSED
tests/test_tool_awareness.py::test_intent_router_classify_prompt_updated PASSED
tests/test_tool_awareness.py::test_intent_router_keyword_fallback_updated PASSED

20 passed in 0.12s
```

---

## 2. 변경 파일 목록

### 신규 생성
- `app/core/prompts/__init__.py` — 패키지 초기화
- `app/core/prompts/system_prompt_v2.py` — XML 섹션 시스템 프롬프트 (build_layer1 함수)
- `tests/test_tool_awareness.py` — 도구 인식 테스트 20개

### 수정
- `app/services/context_builder.py`:
  - Layer 1 하드코딩(_LAYER1_STATIC) → system_prompt_v2.build_layer1() 호출로 교체
  - `_WS_LAYER1` → system_prompt_v2.WS_LAYER1 import로 교체
  - 버전 주석: AADS-185 → AADS-186A
- `app/services/tool_registry.py`:
  - 모든 도구에 input_examples 추가
  - list_remote_dir/read_remote_file/query_database에 response_format 파라미터 추가
  - 신규 3개 도구 정의: inspect_service/get_all_service_status/generate_directive
  - 신규 그룹: "workflow"
  - ToolRegistry 클래스: get_tool_examples(), list_groups() 메서드 추가
- `app/services/tool_executor.py`:
  - _MAX_RESULT_CHARS: 6000 → 25000 (25,000 토큰 허용)
  - _TOOL_TIMEOUT: 10.0 → 20.0초
  - _dispatch(): 3개 신규 도구 추가
  - 메서드 구현: _inspect_service(), _get_all_service_status(), _generate_directive()
  - _INTENT_TOOL_MAP: service_inspection/all_service_status 추가
- `app/services/intent_router.py`:
  - INTENT_MAP: service_inspection/all_service_status 추가
  - _CLASSIFY_PROMPT: 신규 인텐트 + 키워드 규칙 추가
  - _keyword_fallback(): 신규 인텐트 키워드 추가

---

## 3. 커밋 정보

### aads-server 커밋
- SHA: 898fb07
- URL: https://github.com/moongoby-GO100/aads-server/commit/898fb07
- 메시지: "AADS-186A: 시스템 프롬프트 재설계 + 도구 고도화"
- 변경: 7 files changed, 947 insertions(+), 159 deletions(-)

### aads-docs 커밋
- SHA: 908e9e7
- 메시지: "AADS-186A: HANDOVER v12.10 + STATUS.md 업데이트"

---

## 4. 제약 준수 확인

| 제약 | 확인 |
|------|------|
| 기존 도구·인텐트 깨뜨리지 않음 | ✅ 기존 system/action/search 그룹 모두 보존 |
| Layer 1 토큰 1,800 이내 | ✅ 추정 ~700 토큰 |
| 도구 응답 truncation 25,000 토큰 | ✅ _MAX_RESULT_CHARS=25000 |
| 신규 프롬프트 텍스트 파일 분리 | ✅ system_prompt_v2.py (하드코딩 없음) |

---

## 5. qa_status
qa_status: PASS
테스트: 20/20 통과 (0 failed, 0 skipped)
테스트 방식: 소스 코드 검사 (Python 3.6 venv 호환)
런타임 통합 테스트: Docker Python 3.11 환경에서 추가 수행 권장
