# CUR-GO100-P5-4-PERSONALIZATION — P5-4 사용자 개인화 시스템

**일시:** 2026-02-27  
**작업 ID:** CUR-GO100-P5-4-PERSONALIZATION (P5-4)  
**목적:** 에피소드 메모리(P4-1)와 사용자 프로파일을 결합하여 백억이 응답을 개인화하는 시스템 구현

---

[인계 확인]
- 직전 완료: (P5-4 선행 작업)
- 현재 단계: Phase 5 (개인화)
- CEO 지시 적용: HANDOVER 보고서 push, 인계서 갱신
- strategy_cards: (기존 유지)
- open_positions: (기존 유지)

---

## 1. 요약

- **DB:** `go100_user_preferences` 테이블 추가 (마이그레이션 045).
- **서비스:** `personalization_engine.py` — `get_user_context`, `personalize_screening`, `personalize_response`, `update_preferences` 구현.
- **Agent Core:** 시스템 프롬프트에 사용자 컨텍스트(선호 섹터/전략/리스크) 주입, 응답 후 `personalize_response`로 에피소드 맥락 보강.
- **Agent 도구:** `get_my_preferences`, `update_my_preferences` 추가.
- **스크리닝:** `screen_stocks` 호출 시 사용자 선호 섹터 기반 결과 정렬 적용.

---

## 2. 구현 범위

### 2.1 DB (backend/migrations/045_go100_user_preferences.sql)

- `go100_user_preferences`: pref_id, user_id(UNIQUE), risk_tolerance, preferred_sectors(TEXT[]), preferred_strategy_types(TEXT[]), investment_horizon, notification_settings(JSONB), custom_filters(JSONB), updated_at.
- risk_tolerance: CONSERVATIVE | MODERATE | AGGRESSIVE.
- preferred_strategy_types: SCALP | SWING | VALUE | MOMENTUM.
- investment_horizon: SHORT | MEDIUM | LONG.

### 2.2 서비스 (backend/app/services/go100/personalization_engine.py)

| 함수 | 설명 |
|------|------|
| get_user_context(user_id) | go100_user_preferences + go100_user_memory(에피소드) + go100_usage_logs 최근 검색 이력 통합 |
| personalize_screening(user_id, base_results) | 선호 섹터/전략 기반 스크리닝 결과 정렬·가중치 |
| personalize_response(user_id, response_text) | 에피소드 메모리 기반 맥락 보강 (예: "지난번 삼성전자 관심 있으셨는데...") |
| update_preferences(user_id, **prefs) | 프로파일 UPSERT |

### 2.3 Agent Core 연동

- **agent_memory_wrapper.py:** `get_user_context(user_id)`로 [투자 선호] 블록 구성 후 `system_prompt_extra`에 추가. 응답 수신 후 `personalize_response(user_id, response_text)` 적용.
- **agent_core.py:** 시스템 프롬프트 사용자 도구 목록에 `get_my_preferences`, `update_my_preferences` 명시.

### 2.4 Agent Tools

- **get_my_preferences()** — 내 투자 성향/선호 조회 (go100_user_preferences 기반).
- **update_my_preferences(risk_tolerance, sectors, ...)** — 성향 업데이트.

### 2.5 스크리닝 개인화

- **tool_executors.execute_tool:** `screen_stocks` 호출 후 `status==ok`이고 `context.user_id`가 있으면 `personalize_screening(user_id, results)`로 `data.results` 재정렬.

---

## 3. 생성/수정 파일

| 경로 | 내용 |
|------|------|
| backend/migrations/045_go100_user_preferences.sql | 신규 테이블·인덱스·코멘트 |
| backend/app/services/go100/personalization_engine.py | 신규 (get_user_context, personalize_screening, personalize_response, update_preferences) |
| backend/app/services/go100/ai/agent_memory_wrapper.py | get_user_context/personalize_response import 및 system_prompt_extra·응답 보강 |
| backend/app/services/go100/ai/agent_core.py | SYSTEM_PROMPT 도구 목록에 get_my_preferences, update_my_preferences 추가 |
| backend/app/services/go100/ai/agent_tools.py | get_my_preferences, update_my_preferences 도구 정의 추가 |
| backend/app/services/go100/ai/tool_executors.py | get_user_profile(user_id from context), get_my_preferences, update_my_preferences 구현·등록, execute_tool에서 screen_stocks 개인화 |
| scripts/go100/test_p5_4_personalization.py | P5-4 테스트 스크립트 |

---

## 4. 테스트 결과

- **user_id=2** 로 preferences 생성: AGGRESSIVE, 반도체+AI, SWING — OK.
- **personalize_screening:** 반도체/AI 섹터 우선 정렬 확인 (반도체B, AI테마C, 기타A 순).
- **personalize_response:** 에피소드 메모리 반영 (에피소드 없을 때는 원문 유지).
- **Agent 도구:** get_my_preferences 조회, update_my_preferences(CONSERVATIVE) 후 재조회·원복(AGGRESSIVE) — OK.
- **screen_stocks + user_id=2:** 결과 수 반환, personalize_screening 적용 경로 동작 확인.

---

## 5. Git 및 보고서 push

- **코드 레포:** (필요 시) kis-autotrade-v4 에서 해당 파일 add/commit.
- **project-docs:** 본 보고서를 `/root/project-docs/go100/reports/CUR-GO100-P5-4-PERSONALIZATION-20260227.md` 에 저장 후 `git add -A && git commit -m "[GO100] P5-4 사용자 개인화 시스템 보고서" && git push origin master` 수행.

---

## 6. 체크리스트

- [x] DB 마이그레이션 045 적용
- [x] personalization_engine 구현 및 연동
- [x] Agent Core 시스템 프롬프트·메모리 래퍼 연동
- [x] get_my_preferences, update_my_preferences 도구 추가 및 실행
- [x] screen_stocks 개인화, personalize_response 적용
- [x] 테스트 스크립트 실행 통과
- [ ] project-docs 보고서 push 완료
