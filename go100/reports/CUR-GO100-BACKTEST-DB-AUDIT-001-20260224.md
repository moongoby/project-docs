# CUR-GO100-BACKTEST-DB-AUDIT-001 — 백테스트 DB 저장 + 최적화 연동 + 리포트 페이지 현황

**발행:** 2026-02-24 15:20 KST  
**우선순위:** P0

---

## 1. 백테스트 결과 DB 저장 현황

### 1.1 go100_backtest_runs

| 항목 | 내용 |
|------|------|
| **스키마** | 25컬럼: id, user_id, go100_card_id, strategy_name, stock_codes_used, universe_filter_snapshot, start_date, end_date, initial_capital(기본 10000000), total_return, annualized_return, max_drawdown, sharpe_ratio, win_rate, total_trades, profit_factor, avg_holding_days, optimization_round(0), parent_run_id, optimization_log, status(기본 'PENDING'), error_message, result_detail, created_at(now()), completed_at |
| **행 수** | **0건** |
| **최근 데이터** | 없음 (테이블 비어 있음) |

- DB 접속: `PGPASSWORD='...' psql -h localhost -U kis_admin -d kisautotrade` (소켓 Peer 인증 실패 시 `-h localhost` 사용)

### 1.2 저장 로직

| 위치 | DB INSERT/저장 여부 | 상세 |
|------|---------------------|------|
| **backtest_service.py** | **있음** | `run_backtest()`: 카드 조회 → **INSERT go100_backtest_runs (status='RUNNING')** → 시뮬레이션(daily 또는 minute) 실행 → 성공 시 **UPDATE (status='COMPLETED', total_return, max_drawdown, sharpe_ratio, win_rate, total_trades, result_detail, completed_at)** → 카드의 last_backtest_* 업데이트 → commit. 실패 시 UPDATE status='FAILED', error_message, completed_at 후 commit. |
| **backtest_router.py** | **API에서 저장 호출 있음** | `POST /run` → `svc.run_backtest(current_user["user_id"], req, db)` 호출. 서비스 내부에서 INSERT/UPDATE 수행. |

- **결론:** GO100 백테스트 API(`POST /api/go100/backtest/run`)를 통해 실행하면 `go100_backtest_runs`에 정상 저장되는 구조이다. 현재 0건인 것은 해당 API로 백테스트를 실행한 이력이 없거나, 실행 경로가 프론트/다른 진입점일 가능성을 의미한다.

### 1.3 백테스트 관련 기타 테이블 (pg_stat_user_tables 기준)

| 테이블명 | row_count |
|----------|-----------|
| go100_backtest_runs | 0 |
| backtest_params | 341 |
| backtest_results | 0 |
| backtests | 1 |
| v4_backtest_daily | 5,075 |
| v4_backtest_desk_detail | 12 |
| v4_backtest_equity | 175 |
| v4_backtest_profile | 0 |
| v4_backtest_regime_analysis | 0 |
| v4_backtest_results | 0 |
| v4_backtest_results_desk_run | 39 |
| v4_backtest_runs | 4 |
| v4_backtest_runs_legacy | 3 |
| v4_backtest_sessions | 76 |
| v4_backtest_summary | 47 |
| v4_backtest_trade_log | 1,084 |
| v4_backtest_trades | 187,410 |

- **v4_backtest_regime_analysis**: 행 수 0건.

---

## 2. 최적화(optimizer) — 백테스트 결과 활용 현황

| 항목 | 내용 |
|------|------|
| **backtest_optimizer.py** | **go100_backtest_runs 참조 있음 (폴백)**. 주 흐름: `_run_backtest(card_id)`로 **매번 새 백테스트 실행** → 결과를 메모리(`backtest_result`)로 사용해 LLM 분석·카드 생성·`_create_opt_run` 등 수행. 백테스트 실행 **실패 시**에만 `go100_backtest_runs`에서 해당 카드의 최신 1건을 SELECT(id, total_return, max_drawdown, sharpe_ratio, win_rate, total_trades)하여 폴백으로 사용. |
| **optimizer_service.py** | `go100_backtest_runs` 직접 조회 없음. `run_fit_analysis`, `get_fit_result`, `run_exit_optimize`, `run_desk_allocation` 등은 별도 fit/exit/desk 로직이며 백테스트는 내부 `_run_single_stock_backtest` 등으로 실행. |
| **go100_optimization_runs** | **테이블 존재**. 22컬럼(opt_run_id, original_card_id, iteration, parent_run_id, parameters_before/after, change_description, **backtest_run_id**, total_return, mdd, sharpe_ratio, win_rate, trade_count, optimization_goal, llm_analysis, llm_recommendation, status, is_best, optimized_card_id, created_at, updated_at, user_id). **행 수 0건**. |

- **정리:** 최적화는 “실행 시마다 새 백테스트”를 기본으로 하며, 그 결과는 서비스 내에서만 사용하고 DB에는 `go100_backtest_runs`가 run_backtest 경로로 쌓일 때만 저장된다. `go100_optimization_runs`는 최적화 실행 기록용으로 정의되어 있으나 현재 0건.

---

## 3. 백억이 AI — 백테스트 결과 활용

| 구성요소 | 백테스트 결과 조회/활용 |
|----------|--------------------------|
| **base_orchestrator** | DB에서 `go100_backtest_runs` 직접 조회하지 않음. `_run_backtest()`(daily 또는 minute) 호출로 **메모리 결과**를 받아 `evaluate_agent.evaluate(bt_result)`, `optimize_agent.optimize()` 등에 전달. 최종 선택 시 `_finalize_card()`에서 카드의 last_backtest_id, last_backtest_return, last_backtest_mdd, last_backtest_sharpe, last_backtest_at 업데이트. |
| **evaluate_agent** | **결과 평가 있음.** `evaluate(backtest_result, risk_tolerance)` — 수익률/MDD/승률/샤프 기준 임계값 비교, 점수·메트릭·LLM 요약 반환. |
| **optimize_agent** | **결과 기반 최적화 제안 있음.** 전략+평가 결과를 받아 LLM으로 파라미터 조정 제안(profit_target_pct, stop_loss_pct, max_stocks 등). |
| **prompts** | **백테스트 결과 참조 있음.** 평가/최적화 관련 설명에 “백테스트 결과”, “수익률, MDD, 승률, Sharpe Ratio” 등 언급. |
| **ai_router** | **go100_backtest_runs 조회 있음.** `POST /evaluate`에서 `backtest_run_id`만 넘길 경우 `SELECT result_detail FROM go100_backtest_runs WHERE id = :id`로 조회 후 evaluate. |

- **정리:** 오케스트레이터/에이전트는 주로 “실행된 백테스트 결과(dict)”를 인메모리로 사용하고, DB 저장 결과는 API `/evaluate`의 run_id 기반 조회 시에만 사용된다.

---

## 4. 문제점 및 개선 필요 사항

1. **go100_backtest_runs 0건**  
   - 저장 로직은 구현되어 있으나, GO100 백테스트를 `POST /api/go100/backtest/run`으로 실행한 이력이 없거나, 프론트/실제 사용 경로가 해당 API를 타지 않을 수 있음.  
   - **권장:** 프론트에서 “백테스트 실행” 시 해당 API 호출 여부 확인 및, 필요 시 1회 실행해 DB 적재를 검증.

2. **최적화 실행 시 DB 기록 미사용**  
   - `BacktestOptimizer`는 매번 새 백테스트를 돌리고, 그 결과로 `_create_opt_run` 등에서 `go100_optimization_runs` INSERT를 할 수 있는 구조이나, 현재 optimization_runs도 0건.  
   - **권장:** 최적화 API/진입점이 실제로 `BacktestOptimizer`를 타는지, 및 `_create_opt_run` 호출·commit 여부 확인.

3. **AI 오케스트레이터와 go100_backtest_runs 미연결**  
   - 오케스트레이터는 자체 `_run_backtest` 결과만 사용하며, 기존에 DB에 저장된 `go100_backtest_runs`를 재사용하지 않음.  
   - **선택 개선:** “같은 카드·동일 기간 재실행 없이 최근 run 재사용” 정책이 필요하면, 오케스트레이터에서 run_id/기간 조건으로 `go100_backtest_runs` 조회 후 재사용하는 분기 추가 검토.

4. **v4_backtest_* 와 go100_backtest_runs 이원화**  
   - V4 백테스트 테이블(v4_backtest_runs 등)과 GO100 전용 go100_backtest_runs가 공존.  
   - **권장:** GO100 UI/API는 go100_backtest_runs만 사용하도록 라우팅이 명확한지 정리하고, 필요 시 V4와의 차이를 문서화.

---

## 5. 오전 차트 작업 (2026-02-24 00:00 ~ 15:00)

- **대표 커밋:** `34c56604` — feat(chart): V4 차트 Phase1+2 - API 클라이언트, Lightweight Charts, StockDetailModal 일봉/분봉 탭 + CHART-DEVELOPMENT-STATUS-REPORT (20260224).
- **차트/프론트 관련 변경 파일 예시:**  
  - `frontend/src/components/market/StockChart.tsx`, `StockDetailModal.tsx`  
  - `frontend/src/components/backtest-analysis/EquityCurveChart.tsx`, `RegimePerformanceBarChart.tsx`, `RegimeTimelineChart.tsx`, `StrategyRegimeHeatmap.tsx`, `DeskRadarChart.tsx`  
  - `frontend/src/app/(protected)/backtest/page.tsx`, `backtest/analysis/page.tsx`  
  - 기타: `frontend/src/app/(protected)/stock/[code]/page.tsx`, `go100/strategies/[id]/page.tsx`, `portfolio/page.tsx`, `strategy-cards/page.tsx` 등.

---

## 6. 리포트(/reports) 페이지 현재 상태

| 항목 | 내용 |
|------|------|
| **/reports 페이지** | `frontend/src/app/(protected)/reports/page.tsx`. 일간/주간 성과 목록, 상세 조회(HTML 렌더), 수동 생성, 재발송. `getReports`, `getReport`, `generateReport`, `resendReport` 사용 (CUR-AUTO-REPORT-v1, 2026-02-20). |
| **reports API** | `backend/app/routers/report_router.py` — prefix `/reports`, `list_reports`(GET), `get_report`(GET /{report_id}), v4_reports 뷰 기반. 생성/재발송 등 추가 엔드포인트 존재. |
| **reports 서비스** | `backend/app/services/report/report_generator.py`, `report_sender.py` 존재. |

- **정리:** 리포트 페이지·API·서비스는 구현되어 있으며, v4_reports 뷰와 연동된 상태.

---

## 7. 권장 조치

1. **GO100 백테스트 1회 실행 검증**  
   - 프론트 또는 API로 `POST /api/go100/backtest/run` 호출 후 `go100_backtest_runs`에 1건 INSERT·UPDATE 되는지 확인.  
   - 실패 시 에러 메시지(서비스/DB 로그)로 INSERT/UPDATE/commit 구간 점검.

2. **최적화 플로우 점검**  
   - 최적화 실행 시 `BacktestOptimizer.start_optimization` 및 `_create_opt_run` 호출 여부 확인.  
   - `go100_optimization_runs`에 행이 쌓이도록 트랜잭션 commit 및 에러 핸들링 확인.

3. **오케스트레이터와 DB 백테스트 연동 (선택)**  
   - “최근 run 재사용” 요구 시, base_orchestrator에서 카드·기간 조건으로 `go100_backtest_runs` 조회 후 재사용 로직 추가 검토.

4. **문서화**  
   - GO100 백테스트 저장 테이블은 `go100_backtest_runs`이며, V4 백테스트(v4_backtest_*)와 용도 구분을 문서에 명시.

---

**보고서 작성:** CUR-GO100-BACKTEST-DB-AUDIT-001  
**저장 경로:** `/root/project-docs/go100/reports/CUR-GO100-BACKTEST-DB-AUDIT-001-20260224.md`  
**GitHub:** https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-BACKTEST-DB-AUDIT-001-20260224.md
