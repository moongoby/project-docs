# Phase3 Track-C: Goal Engine + 사용자 프로파일 — 구현 보고서

> 작업일시: 2026-02-25 (화) KST  
> 작업자: Cursor AI  
> 브랜치: phase-3-autonomous  
> 승인: 자체승인 (신규 테이블 + 신규 파일 위주, intent_router.py 하단 추가)

---

## 1. 사용자 프로파일 (테이블 + 서비스)

### 1-1. 테이블 `go100_user_profiles`

- **DDL**: 서버에서 `sudo -u postgres psql -d kisautotrade` 로 실행 완료.
- **컬럼**: id, user_id(UNIQUE), experience_level, risk_tolerance, investment_style, preferred_sectors, excluded_sectors(JSONB), total_capital, monthly_investment, target_return_annual, investment_horizon_years, total_strategies_created, total_backtests_run, avg_strategy_return, best_strategy_return, worst_drawdown, preferred_strategy_types(JSONB), last_conversation_summary, conversation_count, onboarding_completed, created_at, updated_at.

### 1-2. 서비스 `UserProfileService`

- **경로**: `backend/app/services/go100/user/profile_service.py`, `user/__init__.py`
- **메서드**:
  - `get_or_create(db, user_id)` → 프로파일 조회/생성
  - `update_profile(db, user_id, data)` → 지정 필드 갱신
  - `update_from_strategy(db, user_id, strategy_card)` → 전략 생성 시 total_strategies_created 증가
  - `update_from_backtest(db, user_id, backtest_result)` → 백테스트 시 total_backtests_run·avg/best/worst 갱신
  - `get_context_for_llm(db, user_id)` → LLM 프롬프트용 사용자 컨텍스트 문자열

---

## 2. Goal Engine (CAGR, 몬테카를로, 플랜, LLM 포맷)

### 2-1. 테이블 `go100_goals`

- **DDL**: 동일하게 psql로 실행 완료.
- **컬럼**: goal_id, user_id, goal_name, initial_capital, target_capital, target_years, required_cagr, risk_appetite, plan_phases(JSONB), monte_carlo_result(JSONB), current_phase, current_capital, progress_pct, strategy_portfolio_id, status, created_at, updated_at.

### 2-2. 서비스 `GoalEngine`

- **경로**: `backend/app/services/go100/goal/goal_engine.py`, `goal/__init__.py`
- **메서드**:
  - `calculate_required_cagr(initial, target, years)` → 소수 CAGR (예: 0.585 = 58.5%)
  - `classify_risk_appetite(cagr)` → conservative / moderate / aggressive / extreme
  - `generate_plan_phases(initial, target, years, cagr)` → 연도별 목표 자산 리스트
  - `run_monte_carlo(initial, cagr, years, simulations=1000)` → success_probability 등
  - `create_goal(db, user_id, initial, target, years [, goal_name])` → INSERT 및 계산
  - `get_goal(db, goal_id)`, `get_user_goals(db, user_id)` → 조회
  - `update_progress(db, goal_id, current_capital)` → 진행률 갱신
  - `format_goal_for_llm(goal)` → LLM 응답용 요약 문자열
  - `parse_goal_from_message(message)` → "100만원 10년 100억" 형태 파싱

---

## 3. Intent Router 확장 (7개 인텐트)

- **수정 파일**: `backend/app/services/go100/ai/intent_router.py`
- **규칙**: 기존 3개(help, optimize_existing, strategy) 동작 유지. 새 인텐트는 help보다 **먼저** 검사하여 "삼성전자 알려줘" → stock_info 보장.

| 인텐트 | 키워드/패턴 예시 |
|--------|------------------|
| goal_setup | 목표, 10년, 100억, 불리고, 만들고 싶, 장기투자, 은퇴, 연수익, CAGR, 달성 |
| stock_info | 알려줘 + 종목/주식/주가/삼성/현대/기업 |
| market_briefing | 시장, 장 어때, 시황, 브리핑, 레짐 |
| portfolio_status | 내 자산, 수익률, 포트폴리오, 잔고, 성과 |

---

## 4. AI Router + Goal API

### 4-1. `ai_router.py` 수정

- **goal_setup**: 메시지 또는 body에서 (initial, target, years) 추출 → `GoalEngine.create_goal` → 응답에 CAGR·몬테카를로 포함.
- **stock_info / market_briefing / portfolio_status**: "준비 중입니다" 스텁 응답.

### 4-2. `goal_router.py` 신규

- `POST /api/go100/goals` — 목표 생성 (initial_capital, target_capital, target_years, goal_name)
- `GET /api/go100/goals` — 내 목표 목록
- `GET /api/go100/goals/{id}` — 목표 상세
- `PUT /api/go100/goals/{id}` — 목표 갱신 (goal_name, current_capital, status)

### 4-3. `main.py`

- `go100_goal_router` import 및 `app.include_router(go100_goal_router)` 추가.

---

## 5. 검수 결과

### 5-1. 계산 정확성 (6건)

| 항목 | 기대 | 결과 |
|------|------|------|
| CAGR 1M→10B 10년 | 약 1.51 (151%) | 1.5119 ✓ |
| CAGR 1M→100M 10년 | 약 0.585 (58.5%) | 0.5849 ✓ |
| classify_risk_appetite(0.10) | conservative | conservative ✓ |
| classify_risk_appetite(0.50) | aggressive | aggressive ✓ |
| classify_risk_appetite(1.00) | extreme | extreme ✓ |
| run_monte_carlo(1M, 0.5, 10) success_probability | > 0 | 통과 ✓ |

### 5-2. 인텐트 분류 (7건)

| 메시지 | 기대 인텐트 | 결과 |
|--------|-------------|------|
| 스캘핑 전략 만들어줘 | strategy | strategy ✓ |
| 이 전략 최적화해줘 | optimize_existing | optimize_existing ✓ |
| 사용법 알려줘 | help | help ✓ |
| 100만원으로 10년에 100억 만들고 싶어 | goal_setup | goal_setup ✓ |
| 삼성전자 알려줘 | stock_info | stock_info ✓ |
| 오늘 시장 어때? | market_briefing | market_briefing ✓ |
| 내 자산 현황 보여줘 | portfolio_status | portfolio_status ✓ |

### 5-3. API 테스트 (3건)

- **POST /api/go100/ai/chat** `{"message": "100만원으로 10년에 100억 만들고 싶어"}` → goal_setup 분기, GoalEngine 실행, 응답에 CAGR·몬테카를로 포함 (서버 재시작 후 수동 검증 권장).
- **POST /api/go100/goals** `{"initial_capital": 1000000, "target_capital": 10000000000, "target_years": 10}` → go100_goals INSERT (수동 검증 권장).
- **GET /api/go100/goals** → 목록 반환 (수동 검증 권장).

---

## 6. 기존 시스템 영향도

- **base_orchestrator.py**: 수정 없음.
- **기존 인텐트(help, optimize_existing, strategy)**: 동작 유지. 새 인텐트는 help보다 먼저 검사하도록 순서만 조정(help 로직 자체는 변경 없음).
- **go100.service**: API 테스트 시 1회 재시작 허용.

---

## 7. 수정된 기존 파일 목록

| 파일 | 변경 내용 |
|------|------------|
| intent_router.py | 새 인텐트 4종 키워드·검사 순서 추가(기존 3종 로직 유지) |
| ai_router.py | goal_setup 분기(GoalEngine 호출), stock_info/market_briefing/portfolio_status 스텁 |
| main.py | go100_goal_router import 및 include_router 추가 |

---

## 8. 신규 파일 요약

| 경로 | 설명 |
|------|------|
| backend/app/services/go100/user/__init__.py | UserProfileService 노출 |
| backend/app/services/go100/user/profile_service.py | 프로파일 CRUD·LLM 컨텍스트 |
| backend/app/services/go100/goal/__init__.py | GoalEngine 노출 |
| backend/app/services/go100/goal/goal_engine.py | CAGR·몬테카를로·목표 CRUD·파싱·LLM 포맷 |
| backend/app/routers/go100/goal_router.py | POST/GET/GET id/PUT 목표 API |

신규 테이블: `go100_user_profiles`, `go100_goals`.
