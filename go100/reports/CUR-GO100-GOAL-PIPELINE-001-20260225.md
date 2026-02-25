# CUR-GO100-GOAL-PIPELINE-001 실행 보고서

**작성일:** 2026-02-25 (KST)  
**작업 ID:** CUR-GO100-GOAL-PIPELINE-001  
**브랜치:** feat/CUR-GO100-GOAL-PIPELINE-001 → phase-2c-command-center  
**목표:** Goal→Strategy 파이프라인 — 2턴 대화 플로우 및 플랜 기반 전략 카드 자동 생성

---

## 1. 사전확인 결과 (SKIP 판단)

| 항목 | 결과 | 비고 |
|------|------|------|
| ai_router goal_setup | 기존 1턴 스텁(목표 저장 후 텍스트 응답) | **교체** — 2턴 플로우로 전면 구현 |
| GoalEngine 메서드 | calculate_required_cagr, classify_risk_appetite, generate_plan_phases, run_monte_carlo, create_goal, parse_goal_from_message, format_goal_for_llm | **기반영** — 기존 메서드 유지, 신규만 추가 |
| BaseOrchestrator | process_message → UNDERSTAND → DESIGN → _run_full_pipeline | **기반영** — _run_full_pipeline 시그니처 변경 없음, run_from_intent 신규 추가 |
| UserIntent 스키마 | investment_style, risk_tolerance, target_sectors, target_keywords, confidence, needs_clarification 등 | **기반영** — generate_strategy_intents 출력을 해당 필드에 매핑 |
| go100_goals 테이블 | INSERT에 current_phase(숫자 1), strategy_portfolio_id 등 | **기반영** — update_goal에서 status, current_phase 등 허용 필드만 업데이트 |
| intent_router | goal_setup 우선순위 (optimize_existing → help → goal_setup → …) | **기반영** — 변경 없음 |
| design_agent.design | (user_intent, user_message, regime_context) | **기반영** — run_from_intent에서 그대로 호출 |

**DB 접속:** 사전확인 시 `psql` Peer 인증 이슈로 로컬 컬럼 조회는 미실행. 스키마는 기존 GoalEngine INSERT/UPDATE 및 마이그레이션 참고.

---

## 2. 구현 내역

### 2.1 GoalEngine (goal_engine.py)

- **generate_plan_phases**  
  - **기존 유지.** 연도별 목표 자산 리스트 반환 형태 변경 없음.

- **신규: _strategy_allocation_by_cagr(cagr)**  
  - CAGR 구간별 전략 배분:
    - CAGR ≥ 80%: SCALPING 40% + DAILY 35% + SHORT_SWING 25%
    - 40% ≤ CAGR < 80%: DAILY 30% + SHORT_SWING 40% + MID_SWING 30%
    - 20% ≤ CAGR < 40%: SHORT_SWING 35% + MID_SWING 35% + LONG_POSITION 30%
    - CAGR < 20%: MID_SWING 30% + LONG_POSITION 50% + 배당 20%
  - 각 항목: type, weight_pct, description, risk_level, preferred_sectors

- **신규: generate_plan_phases_with_strategies(initial, target, years, cagr)**  
  - 반환: `{ "phase_a": { name, duration_years, target_cagr, strategies }, "phase_b": { … } }`  
  - 2턴에서 목표 저장 시 plan_phases(jsonb)에 이 구조 저장.

- **신규: generate_strategy_intents(goal, phase_key="phase_a")**  
  - goal의 plan_phases에서 해당 phase의 strategies를 읽어, UserIntent 호환 dict 리스트로 변환.  
  - 매핑: type → investment_style, risk_level → risk_tolerance, preferred_sectors → target_sectors, description → specific_conditions 등.

- **create_goal 확장**  
  - 키워드 인자: `risk_appetite=None`, `required_cagr=None`.  
  - `required_cagr`가 주어지면 해당 cagr 사용 및 `generate_plan_phases_with_strategies`로 plan_phases 생성; 그 외는 기존대로 연도별 phases.

- **신규: update_goal(db, goal_id, data)**  
  - 허용 필드: status, current_phase, strategy_portfolio_id, progress_pct, current_capital.  
  - 해당 키만 UPDATE.

### 2.2 BaseOrchestrator (base_orchestrator.py)

- **신규: run_from_intent(user_intent, user_id, db, goal_context="")**  
  - UserIntent(dict) → DESIGN → _run_full_pipeline 호출. UNDERSTAND 단계 없음.  
  - 반환: strategy_card_id, strategy_name, backtest_summary, evaluation, status.  
  - _run_full_pipeline 시그니처/동작 변경 없음.

### 2.3 ai_router.py — goal_setup 2턴 플로우

- **handle_goal_setup**  
  - `_check_pending_goal(conversation_history)`로 1턴/2턴 구분.  
  - 1턴: _handle_goal_first_turn  
  - 2턴: _handle_goal_second_turn  

- **1턴 (_handle_goal_first_turn)**  
  - 메시지/body에서 목표 파싱(또는 initial/target/years).  
  - 파싱 실패 시 "목표를 구체적으로 알려주세요" 응답.  
  - CAGR 계산 → _generate_three_scenarios(공격적 0.7·초공격적 1.0·균형 0.4) → 시나리오별 몬테카를로.  
  - LLM(call_reply)으로 시나리오 설명 + 선택 안내.  
  - 응답에 `data`: parsed_goal, required_cagr, scenarios.  
  - Redis `goal_pending:{user_id}` 에 동일 data 저장 (TTL 30분).

- **2턴 (_handle_goal_second_turn)**  
  - _parse_scenario_selection(message) → aggressive / ultra_aggressive / moderate / conservative.  
  - _extract_goal_data_from_history(conversation_history) 또는 Redis에서 이전 data 복원.  
  - create_goal(risk_appetite=selection, required_cagr=prev_data["required_cagr"]) → go100_goals INSERT.  
  - generate_strategy_intents(goal, "phase_a") → 각 intent에 대해 orchestrator.run_from_intent() 호출.  
  - 생성된 카드 수만큼 전략 카드 + 백테스트 생성.  
  - update_goal(status=ACTIVE, current_phase=phase_a).  
  - LLM으로 결과 요약 응답.  
  - 응답에 strategy_card_ids, goal_id, data(goal, created_cards) 포함.

- **헬퍼**  
  - _generate_three_scenarios(initial, years, required_cagr)  
  - _check_pending_goal(conversation_history)  
  - _parse_scenario_selection(message)  
  - _extract_goal_data_from_history(conversation_history)  
  - _format_money(val)  

### 2.4 프롬프트 (prompts.py)

- **GOAL_CONTEXT_SECTION**  
  - DESIGN 시: 목표 CAGR에 맞는 공격성, 연 50%+/20~50%/20% 미만별 설계 지침, 전략 설명에 목표 연결 문구 포함.

- **GOAL_REPLY_SECTION**  
  - REPLY 시: 목표 금액 언급, 시나리오별 예상 자산, "불가능" 대신 "가장 공격적으로 가면 …", 전략 생성 시 백테스트 요약, 다음 액션 제시.

- DESIGN_SYSTEM_PROMPT / REPLY_SYSTEM_PROMPT 끝에 각각 위 섹션을 붙여 재할당.

### 2.5 스키마 (schemas.py)

- **OrchestrationResult**  
  - 필드 추가: `data: Optional[dict] = None` (goal_setup 1턴 시나리오 등 클라이언트 재전송용).

---

## 3. 변경 파일 목록

| 구분 | 경로 |
|------|------|
| 수정 | backend/app/services/go100/goal/goal_engine.py |
| 수정 | backend/app/services/go100/ai/base_orchestrator.py |
| 수정 | backend/app/services/go100/ai/prompts.py |
| 수정 | backend/app/services/go100/ai/schemas.py |
| 수정 | backend/app/routers/go100/ai_router.py |

---

## 4. 검증

- **pre-commit:** `bash scripts/pre-commit-check.sh` 통과 (Python/TypeScript).
- **린트:** 수정 파일 대상 린트 에러 없음.
- **Import:** 서버 venv/환경에서 GoalEngine, BaseOrchestrator import 및 generate_strategy_intents, run_from_intent 존재 확인 (로컬에서 sqlalchemy 미설치로 인한 ModuleNotFoundError는 환경 이슈).
- **실제 대화 테스트:** 토큰 획득 후 1턴/2턴 curl 테스트 및 go100_goals·go100_strategy_cards·go100_backtest_runs 확인은 배포 후 수행 권장.

---

## 5. 비고

- **kis-v41-*** 서비스 재시작 금지. go100만 필요 시 재시작.
- **go100_goals.current_phase:** INSERT는 숫자 1 사용. update_goal에서 "phase_a" 문자열로 업데이트. DB 컬럼이 integer면 타입 오류 가능 — 필요 시 1/2 등 숫자 매핑으로 변경.
- **2턴 데이터 복원:** 대화 히스토리에서 assistant 메시지의 `data` 필드 우선 사용, 없으면 Redis `goal_pending:{user_id}` 사용. 클라이언트는 1턴 응답 전체(또는 최소 data)를 히스토리에 포함해 전송하는 것이 안전.

---

## 6. 커밋 및 보고서 push

- **코드 레포:** feat/CUR-GO100-GOAL-PIPELINE-001 브랜치에 커밋 후 phase-2c-command-center 머지 및 push.
- **문서 레포:** /root/project-docs 에서 본 보고서 커밋 후 `git push origin master`, `git log --oneline -1` 로 push 확인.
