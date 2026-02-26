# KIS AutoTrade V4.1 — DB 스키마 문서

> 최종 업데이트: 2026-02-23  
> DB: PostgreSQL 16 / kisautotrade  
> 자동 추출 (SELECT 전용 쿼리) · 코드·문서 기반 정리  
> ⚠️ 실데이터(계좌, 잔고, API키, 토큰, IP, 비밀번호) 미포함

---

## 1. 테이블 개요

### 카테고리별 테이블 수

| 카테고리 | 설명 | 테이블 수(참고) |
|----------|------|-----------------|
| V4.1 | v4_ 접두사 | 80+ |
| GO100 | go100_ 접두사 | 11 |
| LEGACY/OTHER | 그 외 공유·레거시 | 40+ |

*정확한 수치는 서버에서 `pg_tables` + CASE WHEN 카테고리 쿼리로 확인.*

### 전체 테이블 목록 (카테고리별 요약)

**V4.1 — 시장 데이터**  
stock_universe, ohlcv_daily, ohlcv_weekly, ohlcv_monthly, v4_ohlcv_minute(파티션), v4_investor_daily, v4_stock_sector, v4_vkospi_daily, index_daily, market_data_min, market_turnover_daily, scalping_features_daily

**V4.1 — 사용자/계좌**  
v4_users, users, accounts, account_rate_quotas, user_sessions, v4_account_holdings, v4_account_sync_log, v4_account_config, account_snapshots

**V4.1 — 전략/트레이딩**  
strategy_cards, v4_desk_strategy_mapping, v4_positions, v4_position_transfers, v4_trades, v4_desk_fund, v4_signals, v4_orders, v4_order_executions, v4_order_requests, v4_reservations, v4_fund_pool_snapshot, v4_fund_lending

**V4.1 — 백테스트**  
v4_backtest_runs, v4_backtest_sessions, v4_backtest_daily, v4_backtest_trades, v4_backtest_trade_log, v4_backtest_results, v4_backtest_equity, v4_backtest_profile, v4_backtest_summary, v4_backtest_desk_detail, v4_backtest_results_desk_run, v4_backtest_runs_legacy

**V4.1 — 시스템**  
v4_alerts, v4_notifications, v4_reports, v4_api_error_log, v4_api_tokens, v4_system_heartbeat, v4_system_state_log, v4_market_regime_daily, v4_market_calendar, v4_migration_history, v4_minute_collect_progress, v4_notification_channel_config, v4_notification_settings, llm_requests, llm_cost_daily

**GO100**  
go100_account_reconciliation, go100_backtest_runs, go100_desk_allocation, go100_fit_analysis, go100_orders, go100_portfolio_snapshots, go100_portfolios, go100_positions, go100_risk_disclaimers, go100_strategy_cards, go100_trades

**기타/레거시**  
v4_chat_messages, v4_chat_sessions, v4_condition_search, v4_credit_balance, v4_daily_portfolio, v4_daily_reports, v4_theme_*, v4_tick_data, v4_trade_analysis, v4_trade_executions, v4_trade_schedules, v4_trade_strength_history, v4_scalping_signals, v4_scalping_universe, v4_scoring_weights, v4_sector_daily, v4_sector_price, v4_stage_transitions, v4_strategy_performance, v4_strategy_registry, v4_bet_history, v4_broker_trades, v4_pick_reasons, v4_position_extended, v4_program_trades, v4_universe_version, v4_user_settings, v4_user_strategies, v4_market_*, kis_configs

---

## 2. V4.1 핵심 테이블 상세

*컬럼·타입은 ORM 및 코드 기준. 실제 DB는 `information_schema.columns`로 확인.*

### 2-1. 매매

**v4_positions**  
id(BIGINT PK), user_id, ticker(VARCHAR 20), quantity, entry_price, status(VARCHAR 20), desk_id, peak_price, stop_loss_price, trailing_pct, target_pct, max_hold_days, entry_date, reservation_id, exit_reason, exit_price, exited_at, created_at, updated_at.  
*분할/이관: split_phase, remaining_qty, original_desk_id, buy_phase 등 (스키마 확인).*

**v4_trades**  
체결/매매 이력. (컬럼은 DB 메타데이터 참조.)

**v4_orders**  
주문 마스터. (컬럼은 DB 메타데이터 참조.)

**v4_order_requests**  
id(BIGSERIAL PK), idempotency_key(UNIQUE), user_id, desk_id, strategy_id, ticker, side(BUY/SELL), quantity, price_type, limit_price, signal_id, position_id, reservation_id, status, created_at, updated_at, submitted_at, filled_quantity, order_no, message, reject_reason, source, note.  
FK: v4_reservations.order_request_id → v4_order_requests.id.

### 2-2. 전략

**strategy_cards**  
전략 카드 마스터. (ALTER/DROP/DELETE 금지.)  
무결성 기준: 65건 (2026-02-23).

**v4_signals**  
시그널 이력.

**v4_desk_fund**  
DESK별 자금 할당.

**v4_desk_strategy_mapping**  
DESK–전략 매핑.

### 2-3. 자금

**v4_fund_pool_snapshot**  
id(BIGINT PK), user_id, total_capital, available, reserved, invested, desk1_used ~ desk5_used, fund_mode, created_at.

**v4_reservations**  
id(VARCHAR PK), order_request_id(FK → v4_order_requests.id), user_id, desk_id, ticker, amount, status(RESERVED/ORDER_SUBMITTED/FILLED/…), created_at, expires_at, updated_at, order_no, reason, strategy_id, signal_id.

### 2-4. 시장 데이터

**v4_ohlcv_minute**  
분봉 OHLCV. (파티션 테이블.)  
*추정 행 수: 약 19M (문서 기준).*

**v4_market_regime_daily**  
id(BIGINT PK), date(DATE), market_type(VARCHAR 10) DEFAULT 'KOSPI', regime(VARCHAR 30), regime_score, kospi_ret_20d, ma5/ma20/ma60, ma_alignment, bull_ratio_20d, vkospi, foreign_flow_20d, previous_regime, transition_note, hysteresis_up_count, hysteresis_down_count, pending_regime.  
UNIQUE(date, market_type). 코스피/코스닥 이원 레짐 (CUR-STRATEGY-REGIME-BT-VIZ-001).

**v4_market_calendar**  
id(BIGINT PK), date(DATE), event_type, event_name, bet_modifier, desk1_active ~ desk5_active, class_restrictions(JSON), note, source.  
UNIQUE(date, event_type).

**v4_investor_daily**  
일별 투자자 통계.

**v4_vkospi_daily**  
id(BIGINT PK), date(VARCHAR 8 UNIQUE), open, high, low, close, change_rate, source, created_at.

### 2-5. 시스템

**v4_system_heartbeat**  
id(BIGINT PK), state, previous_state, transition_reason, module_status(JSON), cycle_id, last_cycle_duration_ms, order_success_count, order_fail_count, order_reject_count, max_price_staleness_ms, active_positions_count, available_capital, error_message, created_at.

**v4_system_state_log**  
id(BIGINT PK), state, previous_state, transition_reason, module_status(JSON).

**v4_api_tokens**  
API 토큰 메타. (실제 토큰 값·키 미기록.)

### 2-6. 이관/분할

**v4_position_transfers**  
이관 이력. split_transfer_engine에서 INSERT.

### 2-7. 계좌 동기화

**v4_account_holdings**  
계좌 보유 종목 스냅샷.

**v4_account_sync_log**  
동기화 로그.

### 2-8. 백테스트

**v4_backtest_sessions**  
세션 메타.

**v4_backtest_trades**  
36컬럼 확장 반영 (BT-ENGINE-UPGRADE 2026-02-23): session_id, stock_code, trade_type, price, quantity, pnl, trade_date, card_id, exit_reason, entry_date, exit_date, hold_days, entry_datetime, exit_datetime, entry_price, exit_price, mfe_pct, mae_pct, mfe_price, mae_price, regime_at_entry, indicator_snapshot(jsonb), slippage_pct, commission, sector, strategy_name, entry_volume, entry_spread_pct, split_phase, transfer_to 등.  
*추정 행 수: 약 176,896 (문서 기준).*

**v4_backtest_regime_analysis**  
레짐별 백테스트 성과 (CUR-STRATEGY-REGIME-BT-VIZ-001, CUR-FULLBT-REGIME-003): session_id, card_id, strategy_name, desk_id, market_type, regime, regime_mapped(BULL/NEUTRAL/BEAR/CRISIS), total_trades, win_count, loss_count, win_rate, profit_factor, total_pnl, avg_pnl, max_pnl, min_pnl, avg_hold_days, avg_mfe_pct, avg_mae_pct, max_drawdown_pct, sharpe_ratio, benchmark_return_pct, strategy_return_pct, alpha_pct, pass_win_rate, pass_pf, pass_alpha, pass_mdd, pass_sharpe, overall_pass, backtest_period_start, backtest_period_end, created_at.

---

## 3. GO100 테이블 상세

go100_account_reconciliation, go100_backtest_runs, go100_desk_allocation, go100_fit_analysis, go100_orders, go100_portfolio_snapshots, go100_portfolios, go100_positions, go100_risk_disclaimers, go100_strategy_cards, go100_trades.  
상세 컬럼은 서버에서 `information_schema.columns` 조회.

---

## 4. 레거시 테이블 (DROP 예정 표기)

다음은 레거시·공유 테이블. DROP 시 CEO 승인 및 스키마 문서 변경 이력 반영 필수.

- ohlcv_1m (v4_ohlcv_minute로 이관 후 검토)
- daily_investor_stats (v4_investor_daily 등으로 대체 검토)
- 기타 문서화된 레거시

---

## 5. 제약조건 / 인덱스 요약

- **PK**: 각 테이블 id 또는 명시된 PK.  
- **UNIQUE**: v4_order_requests.idempotency_key, v4_market_regime_daily.date, v4_vkospi_daily.date, v4_market_calendar(date, event_type) 등.  
- **FK**: v4_reservations.order_request_id → v4_order_requests.id (ondelete SET NULL) 등.  
- **인덱스**: 서버에서 `pg_indexes` (schemaname='public') 조회하여 목록 유지.

*전체 목록: STEP 1의 1-4(PK/UNIQUE/FK), 1-5(인덱스), 1-6(CHECK) 쿼리 결과로 채움.*

---

## 6. 파티션 테이블

- **v4_ohlcv_minute**: 날짜 기준 파티션.  
  `pg_inherits` 조회: parent → partition 목록 유지.

*서버 쿼리: `SELECT inhparent::regclass AS parent, inhrelid::regclass AS partition FROM pg_inherits ORDER BY 1,2;`*

---

## 7. 테이블별 추정 행 수

*통계값만 기재. 실데이터 아님.*

| 테이블 | 추정 행 수(참고) |
|--------|------------------|
| v4_ohlcv_minute | 약 19,468,781 |
| v4_backtest_trades | 약 176,896 |
| v4_scalping_universe | 약 708 |
| v4_market_regime_daily | 약 59 |
| strategy_cards | 65 (무결성 기준) |
| v4_positions (OPEN) | 5 (무결성 기준) |

*전체: `pg_stat_user_tables.n_live_tup` (schemaname='public') 조회.*

---

## 8. 보안 필터링 체크리스트

- [x] .env 값 미포함
- [x] 실계좌/잔고/토큰 미포함
- [x] 접속 정보(IP/포트/유저) 미포함

---

## 9. 변경 이력

| 날짜 | 변경 내용 |
|------|-----------|
| 2026-02-23 | 초판 생성 (DB-SCHEMA-EXPORT, 코드·문서 기반) |
| 2026-02-24 | v4_market_regime_daily에 market_type VARCHAR(10) DEFAULT 'KOSPI' 컬럼 추가, UNIQUE(date, market_type) 제약 추가 — CUR-REGIME-BACKFILL-002 |
| 2026-02-24 | v4_backtest_regime_analysis 테이블 생성·regime_mapped 컬럼 추가 — CUR-FULLBT-REGIME-003 |

---

## 10. 유지보수 규칙

DB ALTER TABLE 수행 시 반드시 이 문서도 함께 업데이트하고 project-docs에 push한다.
