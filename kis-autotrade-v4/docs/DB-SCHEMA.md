# DB 스키마 문서 (kisautotrade)
> 자동 생성일: 2026-02-23
> 서버: root@[SERVER-IP]
> DB: PostgreSQL 16, kisautotrade / kis_admin

⚠️ **보안 주의**: 이 문서에는 테이블 구조(컬럼명, 타입)만 포함됩니다.
실제 데이터, 비밀번호, 토큰, 암호화 키 등 민감 정보는 포함되지 않습니다.

## 1. 테이블 요약

| # | 테이블명 | 프로젝트 | 행 수 | 크기 |
|---|---------|---------|-------|------|
| 1 | account_rate_quotas | COMMON | 7 | 72 kB |
| 2 | account_snapshots | COMMON | 466 | 104 kB |
| 3 | accounts | SHARED | 7 | 144 kB |
| 4 | auto_trade_positions | COMMON | 41 | 56 kB |
| 5 | autotrade_positions | COMMON | 84 | 144 kB |
| 6 | backtest_params | COMMON | 341 | 120 kB |
| 7 | backtest_results | COMMON | 0 | 24 kB |
| 8 | backtests | COMMON | 1 | 112 kB |
| 9 | compound_trades | COMMON | 2970 | 688 kB |
| 10 | daily_trading_stats | COMMON | 1 | 88 kB |
| 11 | daily_trading_summary | COMMON | 0 | 32 kB |
| 12 | financial_ratios | COMMON | 45870 | 6688 kB |
| 13 | go100_account_reconciliation | GO100 | 0 | 32 kB |
| 14 | go100_backtest_runs | GO100 | 0 | 80 kB |
| 15 | go100_desk_allocation | GO100 | 2 | 32 kB |
| 16 | go100_fit_analysis | GO100 | 40 | 80 kB |
| 17 | go100_orders | GO100 | 0 | 80 kB |
| 18 | go100_portfolio_snapshots | GO100 | 0 | 56 kB |
| 19 | go100_portfolios | GO100 | 0 | 56 kB |
| 20 | go100_positions | GO100 | 0 | 72 kB |
| 21 | go100_risk_disclaimers | GO100 | 0 | 64 kB |
| 22 | go100_strategy_cards | GO100 | 6 | 224 kB |
| 23 | go100_trades | GO100 | 0 | 88 kB |
| 24 | index_daily | COMMON | 1467 | 400 kB |
| 25 | kis_configs | COMMON | 5 | 88 kB |
| 26 | liquidation_logs | COMMON | 0 | 32 kB |
| 27 | liquidation_orders | COMMON | 0 | 32 kB |
| 28 | liquidation_sessions | COMMON | 0 | 32 kB |
| 29 | live_positions | COMMON | 11 | 96 kB |
| 30 | live_trading_results | COMMON | 7986 | 1688 kB |
| 31 | llm_cost_daily | COMMON | 1 | 104 kB |
| 32 | llm_requests | COMMON | 89 | 136 kB |
| 33 | market_data_min | COMMON | 1204346 | 231 MB |
| 34 | market_turnover_daily | COMMON | 26148 | 3264 kB |
| 35 | ohlcv_1m_history | COMMON | 1204346 | 285 MB |
| 36 | ohlcv_daily | COMMON | 2596474 | 671 MB |
| 37 | ohlcv_monthly | COMMON | 89307 | 13 MB |
| 38 | ohlcv_weekly | COMMON | 357381 | 50 MB |
| 39 | orderbook_snapshots | COMMON | 35894 | 42 MB |
| 40 | orders | COMMON | 29 | 128 kB |
| 41 | payments | COMMON | 0 | 32 kB |
| 42 | pending_orders | COMMON | 6830 | 1688 kB |
| 43 | portfolios | COMMON | 5 | 56 kB |
| 44 | positions | COMMON | 2919 | 456 kB |
| 45 | price_tick_snapshots | COMMON | 35865 | 4640 kB |
| 46 | real_trades | COMMON | 132506 | 39 MB |
| 47 | scalping_features_daily | COMMON | 45 | 88 kB |
| 48 | social_accounts | COMMON | 5 | 64 kB |
| 49 | stock_fundamentals | COMMON | 4249 | 744 kB |
| 50 | stock_universe | COMMON | 3844 | 1624 kB |
| 51 | strategies | COMMON | 51 | 72 kB |
| 52 | strategy_allocations | COMMON | 0 | 24 kB |
| 53 | strategy_cards | COMMON | 60 | 312 kB |
| 54 | strategy_performance | COMMON | 0 | 32 kB |
| 55 | trade_comparisons | COMMON | 132506 | 23 MB |
| 56 | trade_verifications | COMMON | 88 | 136 kB |
| 57 | trades | COMMON | 1 | 96 kB |
| 58 | trading_events | COMMON | 9 | 96 kB |
| 59 | trading_signals | COMMON | 136544 | 26 MB |
| 60 | user_push_subscriptions | COMMON | 0 | 24 kB |
| 61 | user_sessions | COMMON | 157 | 200 kB |
| 62 | user_settings | COMMON | 10 | 80 kB |
| 63 | user_strategies | COMMON | 181 | 104 kB |
| 64 | users | SHARED | 12 | 80 kB |
| 65 | v4_account_config | V4.1 | 1 | 64 kB |
| 66 | v4_account_holdings | V4.1 | 52719 | 15 MB |
| 67 | v4_account_sync_log | V4.1 | 15244 | 3432 kB |
| 68 | v4_alerts | V4.1 | 94 | 144 kB |
| 69 | v4_api_error_log | V4.1 | 0 | 24 kB |
| 70 | v4_api_tokens | V4.1 | 0 | 24 kB |
| 71 | v4_backtest_daily | V4.1 | 3573 | 2096 kB |
| 72 | v4_backtest_desk_detail | V4.1 | 12 | 72 kB |
| 73 | v4_backtest_equity | V4.1 | 175 | 80 kB |
| 74 | v4_backtest_profile | V4.1 | 0 | 16 kB |
| 75 | v4_backtest_results | V4.1 | 0 | 40 kB |
| 76 | v4_backtest_results_desk_run | V4.1 | 39 | 56 kB |
| 77 | v4_backtest_runs | V4.1 | 4 | 112 kB |
| 78 | v4_backtest_runs_legacy | V4.1 | 3 | 72 kB |
| 79 | v4_backtest_sessions | V4.1 | 67 | 256 kB |
| 80 | v4_backtest_summary | V4.1 | 43 | 96 kB |
| 81 | v4_backtest_trade_log | V4.1 | 1084 | 256 kB |
| 82 | v4_backtest_trades | V4.1 | 172147 | 26 MB |
| 83 | v4_bet_history | V4.1 | 0 | 8192 bytes |
| 84 | v4_broker_trades | V4.1 | 0 | 24 kB |
| 85 | v4_chat_messages | V4.1 | 53 | 160 kB |
| 86 | v4_chat_sessions | V4.1 | 15 | 72 kB |
| 87 | v4_condition_search | V4.1 | 0 | 24 kB |
| 88 | v4_credit_balance | V4.1 | 0 | 24 kB |
| 89 | v4_daily_portfolio | V4.1 | 3 | 48 kB |
| 90 | v4_daily_reports | V4.1 | 5 | 96 kB |
| 91 | v4_desk_fund | V4.1 | 5 | 120 kB |
| 92 | v4_desk_strategy_mapping | V4.1 | 56 | 104 kB |
| 93 | v4_fund_lending | V4.1 | 12 | 88 kB |
| 94 | v4_fund_pool_snapshot | V4.1 | 1 | 24 kB |
| 95 | v4_investor_daily | V4.1 | 166921 | 138 MB |
| 96 | v4_llm_usage | V4.1 | 0 | 24 kB |
| 97 | v4_market_calendar | V4.1 | 52 | 80 kB |
| 98 | v4_market_investor_daily | V4.1 | 3610 | 1776 kB |
| 99 | v4_market_ranking | V4.1 | 240 | 232 kB |
| 100 | v4_market_regime_daily | V4.1 | 59 | 88 kB |
| 101 | v4_migration_history | V4.1 | 2 | 80 kB |
| 102 | v4_minute_collect_progress | V4.1 | 672 | 864 kB |
| 103 | v4_notification_channel_config | V4.1 | 0 | 16 kB |
| 104 | v4_notification_settings | V4.1 | 2 | 72 kB |
| 105 | v4_notifications | V4.1 | 0 | 112 kB |
| 106 | v4_ohlcv_minute | V4.1 | 0 | 0 bytes |
| 107 | v4_ohlcv_minute_2025_01 | V4.1 | 0 | 48 kB |
| 108 | v4_ohlcv_minute_2025_02 | V4.1 | 986894 | 253 MB |
| 109 | v4_ohlcv_minute_2025_03 | V4.1 | 3116230 | 793 MB |
| 110 | v4_ohlcv_minute_2025_04 | V4.1 | 3388304 | 860 MB |
| 111 | v4_ohlcv_minute_2025_05 | V4.1 | 2977108 | 755 MB |
| 112 | v4_ohlcv_minute_2025_06 | V4.1 | 3107632 | 790 MB |
| 113 | v4_ohlcv_minute_2025_07 | V4.1 | 3722669 | 945 MB |
| 114 | v4_ohlcv_minute_2025_08 | V4.1 | 3232713 | 824 MB |
| 115 | v4_ohlcv_minute_2025_09 | V4.1 | 3664550 | 935 MB |
| 116 | v4_ohlcv_minute_2025_10 | V4.1 | 3083800 | 789 MB |
| 117 | v4_ohlcv_minute_2025_11 | V4.1 | 25078 | 6832 kB |
| 118 | v4_ohlcv_minute_2025_12 | V4.1 | 1930426 | 519 MB |
| 119 | v4_ohlcv_minute_2026_01 | V4.1 | 3723824 | 999 MB |
| 120 | v4_ohlcv_minute_2026_02 | V4.1 | 2141382 | 558 MB |
| 121 | v4_ohlcv_minute_2026_03 | V4.1 | 0 | 48 kB |
| 122 | v4_order_executions | V4.1 | 0 | 48 kB |
| 123 | v4_order_requests | V4.1 | 0 | 104 kB |
| 124 | v4_orderbook_realtime | V4.1 | 0 | 24 kB |
| 125 | v4_pick_reasons | V4.1 | 50 | 152 kB |
| 126 | v4_position_extended | V4.1 | 3 | 80 kB |
| 127 | v4_position_transfers | V4.1 | 0 | 32 kB |
| 128 | v4_positions | V4.1 | 24 | 200 kB |
| 129 | v4_positions_backup_20260218 | V4.1 | 20 | 40 kB |
| 130 | v4_program_trades | V4.1 | 0 | 24 kB |
| 131 | v4_reports | V4.1 | 0 | 32 kB |
| 132 | v4_reservations | V4.1 | 2 | 128 kB |
| 133 | v4_scalping_signals | V4.1 | 0 | 40 kB |
| 134 | v4_scalping_universe | V4.1 | 708 | 216 kB |
| 135 | v4_scoring_weights | V4.1 | 1 | 64 kB |
| 136 | v4_sector_daily | V4.1 | 14725 | 9000 kB |
| 137 | v4_sector_price | V4.1 | 0 | 24 kB |
| 138 | v4_signals | V4.1 | 101274 | 34 MB |
| 139 | v4_stage_transitions | V4.1 | 1 | 32 kB |
| 140 | v4_stock_sector | V4.1 | 4225 | 472 kB |
| 141 | v4_strategy_performance | V4.1 | 0 | 32 kB |
| 142 | v4_strategy_registry | V4.1 | 77 | 120 kB |
| 143 | v4_system_heartbeat | V4.1 | 1 | 96 kB |
| 144 | v4_system_state_log | V4.1 | 0 | 16 kB |
| 145 | v4_theme_activity_daily | V4.1 | 0 | 16 kB |
| 146 | v4_theme_daily | V4.1 | 0 | 32 kB |
| 147 | v4_theme_detail | V4.1 | 0 | 16 kB |
| 148 | v4_theme_master | V4.1 | 0 | 32 kB |
| 149 | v4_theme_stock | V4.1 | 0 | 32 kB |
| 150 | v4_theme_stock_mapping | V4.1 | 0 | 16 kB |
| 151 | v4_tick_data | V4.1 | 0 | 16 kB |
| 152 | v4_trade_analysis | V4.1 | 0 | 8192 bytes |
| 153 | v4_trade_executions | V4.1 | 5 | 112 kB |
| 154 | v4_trade_schedules | V4.1 | 3 | 88 kB |
| 155 | v4_trade_strength_history | V4.1 | 0 | 16 kB |
| 156 | v4_trades | V4.1 | 32 | 136 kB |
| 157 | v4_trades_backup_20260218 | V4.1 | 0 | 0 bytes |
| 158 | v4_universe_version | V4.1 | 16 | 112 kB |
| 159 | v4_user_settings | V4.1 | 0 | 24 kB |
| 160 | v4_user_strategies | V4.1 | 0 | 32 kB |
| 161 | v4_users | V4.1 | 6 | 96 kB |
| 162 | v4_vkospi_daily | V4.1 | 1504 | 392 kB |
| 163 | virtual_trades | COMMON | 132506 | 26 MB |

## 2. 테이블별 컬럼 구조

### account_rate_quotas (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| quota_id | bigint | NO | HAS_DEFAULT |
| account_id | bigint | NO |  |
| broker_type | character varying(10) | NO |  |
| max_rps | numeric | NO |  |
| min_rps | numeric | NO | HAS_DEFAULT |
| burst_limit | integer | NO | HAS_DEFAULT |
| version | integer | NO | HAS_DEFAULT |
| last_reset_at | timestamp with time zone | NO | HAS_DEFAULT |

### account_snapshots (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| total_assets | integer | YES | HAS_DEFAULT |
| total_deposit | integer | YES | HAS_DEFAULT |
| total_purchase | integer | YES | HAS_DEFAULT |
| total_evaluation | integer | YES | HAS_DEFAULT |
| total_profit | integer | YES | HAS_DEFAULT |
| profit_rate | real | YES | HAS_DEFAULT |
| snapshot_time | timestamp without time zone | NO |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### accounts (SHARED)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| account_id | bigint | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| broker_type | character varying(10) | NO |  |
| account_number | character varying(30) | NO |  |
| account_alias | character varying(50) | YES |  |
| is_mock | boolean | NO | HAS_DEFAULT |
| enc_app_key | text | NO | 🔒 암호화/민감 |
| enc_app_secret | text | NO | 🔒 암호화/민감 |
| enc_token | text | YES | 🔒 암호화/민감 |
| token_expires_at | timestamp with time zone | YES | 🔒 암호화/민감 |
| kis_config_id | integer | YES |  |
| daily_order_limit | numeric | NO | HAS_DEFAULT |
| buy_blocked | boolean | NO | HAS_DEFAULT |
| buy_blocked_at | timestamp with time zone | YES |  |
| buy_block_reason | character varying(100) | YES |  |
| is_active | boolean | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |

### auto_trade_positions (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_id | integer | NO |  |
| symbol | character varying(20) | NO |  |
| quantity | integer | NO |  |
| entry_price | real | NO |  |
| current_price | real | NO |  |
| stop_loss | real | YES |  |
| take_profit | real | YES |  |
| unrealized_pnl | real | YES | HAS_DEFAULT |
| status | character varying(20) | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

### autotrade_positions (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_id | character varying(50) | NO |  |
| ticker | character varying(20) | NO |  |
| side | character varying(10) | NO |  |
| quantity | integer | NO |  |
| entry_price | real | NO |  |
| current_price | real | YES |  |
| exit_price | real | YES |  |
| unrealized_pnl | real | YES | HAS_DEFAULT |
| realized_pnl | real | YES |  |
| stop_loss_price | real | YES |  |
| take_profit_price | real | YES |  |
| status | character varying(20) | NO | HAS_DEFAULT |
| order_id | character varying(100) | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |
| closed_at | timestamp without time zone | YES |  |
| max_holding_minutes | integer | YES |  |
| force_close_at_market_end | boolean | YES | HAS_DEFAULT |
| owner_strategy_id | character varying(50) | YES |  |
| closed_reason | character varying(50) | YES |  |

### backtest_params (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| strategy_id | character varying(50) | NO |  |
| objective | text | YES | HAS_DEFAULT |
| score | real | YES | HAS_DEFAULT |
| params_json | text | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### backtest_results (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| strategy_id | character varying(50) | NO |  |
| strategy_name | character varying(255) | YES |  |
| period_start | date | NO |  |
| period_end | date | NO |  |
| universe_tag | text | YES | HAS_DEFAULT |
| total_return | real | YES | HAS_DEFAULT |
| win_rate | real | YES | HAS_DEFAULT |
| max_drawdown | real | YES | HAS_DEFAULT |
| total_trades | integer | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### backtests (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_combo | text | NO |  |
| scenario | character varying(50) | NO |  |
| initial_capital | real | NO |  |
| final_capital | real | NO |  |
| total_return | real | NO |  |
| annual_return | real | YES |  |
| sharpe_ratio | real | YES |  |
| max_drawdown | real | YES |  |
| win_rate | real | YES |  |
| total_trades | integer | YES |  |
| market_regime | character varying(50) | YES |  |
| start_date | timestamp without time zone | NO |  |
| end_date | timestamp without time zone | NO |  |
| execution_plan | jsonb | YES |  |
| trade_history | jsonb | YES |  |
| equity_curve | jsonb | YES |  |
| status | character varying(9) | NO |  |
| error_message | text | YES |  |
| executed_at | timestamp without time zone | YES | HAS_DEFAULT |
| completed_at | timestamp without time zone | YES |  |

### compound_trades (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| portfolio_id | integer | NO |  |
| user_id | integer | NO |  |
| strategy_name | character varying(100) | NO |  |
| strategy_category | character varying(50) | NO |  |
| symbol | character varying(20) | YES |  |
| side | character varying(10) | NO |  |
| quantity | integer | NO |  |
| price | real | NO |  |
| commission | real | YES |  |
| allocated_capital | real | NO |  |
| realized_pnl | real | YES |  |
| roi | real | YES |  |
| order_id | character varying(100) | YES |  |
| execution_time | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### daily_trading_stats (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| trade_date | date | NO |  |
| account_email | character varying(255) | NO |  |
| real_total_trades | integer | YES | HAS_DEFAULT |
| real_filled_trades | integer | YES | HAS_DEFAULT |
| real_failed_trades | integer | YES | HAS_DEFAULT |
| real_total_commission | real | YES | HAS_DEFAULT |
| real_total_slippage | real | YES | HAS_DEFAULT |
| real_total_pnl | real | YES | HAS_DEFAULT |
| virtual_total_trades | integer | YES | HAS_DEFAULT |
| virtual_filled_trades | integer | YES | HAS_DEFAULT |
| virtual_total_pnl | real | YES | HAS_DEFAULT |
| avg_price_diff | real | YES | HAS_DEFAULT |
| max_price_diff | real | YES | HAS_DEFAULT |
| total_cost_diff | real | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### daily_trading_summary (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_email | text | NO |  |
| trade_date | date | NO |  |
| total_trades | integer | YES | HAS_DEFAULT |
| winning_trades | integer | YES | HAS_DEFAULT |
| losing_trades | integer | YES | HAS_DEFAULT |
| win_rate | real | YES | HAS_DEFAULT |
| total_pnl | real | YES | HAS_DEFAULT |
| total_pnl_pct | real | YES | HAS_DEFAULT |
| starting_capital | real | YES |  |
| ending_capital | real | YES |  |
| strategy_performance | text | YES |  |
| best_trade_pnl | real | YES |  |
| worst_trade_pnl | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### financial_ratios (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| stac_yymm | character varying(6) | NO |  |
| grs | real | YES |  |
| bsop_prfi_inrt | real | YES |  |
| ntin_inrt | real | YES |  |
| roe_val | real | YES |  |
| eps | real | YES |  |
| sps | real | YES |  |
| bps | real | YES |  |
| rsrv_rate | real | YES |  |
| lblt_rate | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### go100_account_reconciliation (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| account_id | integer | NO |  |
| system_cash | numeric | YES |  |
| system_position_count | integer | YES |  |
| system_total_eval | numeric | YES |  |
| actual_cash | numeric | YES |  |
| actual_position_count | integer | YES |  |
| actual_total_eval | numeric | YES |  |
| external_buy_count | integer | YES | HAS_DEFAULT |
| external_sell_count | integer | YES | HAS_DEFAULT |
| qty_mismatch_count | integer | YES | HAS_DEFAULT |
| cash_diff | numeric | YES |  |
| reconcile_status | character varying(20) | YES | HAS_DEFAULT |
| detail | jsonb | YES |  |
| synced_at | timestamp with time zone | YES | HAS_DEFAULT |

### go100_backtest_runs (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| go100_card_id | bigint | YES |  |
| strategy_name | character varying(200) | YES |  |
| stock_codes_used | ARRAY | YES |  |
| universe_filter_snapshot | jsonb | YES |  |
| start_date | date | NO |  |
| end_date | date | NO |  |
| initial_capital | bigint | YES | HAS_DEFAULT |
| total_return | numeric | YES |  |
| annualized_return | numeric | YES |  |
| max_drawdown | numeric | YES |  |
| sharpe_ratio | numeric | YES |  |
| win_rate | numeric | YES |  |
| total_trades | integer | YES |  |
| profit_factor | numeric | YES |  |
| avg_holding_days | numeric | YES |  |
| optimization_round | integer | YES | HAS_DEFAULT |
| parent_run_id | bigint | YES |  |
| optimization_log | jsonb | YES |  |
| status | character varying(20) | YES | HAS_DEFAULT |
| error_message | text | YES |  |
| result_detail | jsonb | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| completed_at | timestamp with time zone | YES |  |

### go100_desk_allocation (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| total_capital | numeric | NO |  |
| card_allocations | jsonb | NO |  |
| overlap_resolved | jsonb | YES |  |
| portfolio_metrics | jsonb | YES |  |
| period_days | integer | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### go100_fit_analysis (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| go100_card_id | bigint | NO |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| total_return | numeric | YES |  |
| win_rate | numeric | YES |  |
| profit_factor | numeric | YES |  |
| max_drawdown | numeric | YES |  |
| sharpe_ratio | numeric | YES |  |
| total_trades | integer | YES |  |
| avg_holding_days | numeric | YES |  |
| fit_score | numeric | YES |  |
| entry_timing | jsonb | YES |  |
| period_days | integer | YES |  |
| analysis_date | date | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### go100_orders (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| portfolio_id | bigint | NO |  |
| user_id | integer | NO |  |
| account_id | integer | NO |  |
| go100_card_id | bigint | NO |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| side | character varying(10) | NO |  |
| order_type | character varying(20) | NO | HAS_DEFAULT |
| requested_price | numeric | YES |  |
| requested_qty | integer | NO |  |
| filled_price | numeric | YES |  |
| filled_qty | integer | YES | HAS_DEFAULT |
| status | character varying(20) | YES | HAS_DEFAULT |
| broker_order_no | character varying(50) | YES |  |
| is_paper | boolean | YES | HAS_DEFAULT |
| error_message | text | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### go100_portfolio_snapshots (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| portfolio_id | bigint | NO |  |
| snapshot_date | date | NO |  |
| total_equity | numeric | YES |  |
| current_cash | numeric | YES |  |
| total_invested | numeric | YES |  |
| total_eval | numeric | YES |  |
| open_positions | integer | YES | HAS_DEFAULT |
| daily_pnl | numeric | YES |  |
| total_return_pct | numeric | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### go100_portfolios (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| portfolio_id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| account_id | integer | YES |  |
| go100_card_id | bigint | NO |  |
| initial_capital | numeric | NO |  |
| current_cash | numeric | NO |  |
| total_invested | numeric | YES | HAS_DEFAULT |
| total_eval | numeric | YES | HAS_DEFAULT |
| is_paper | boolean | YES | HAS_DEFAULT |
| status | character varying(20) | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |
| is_live | boolean | YES | HAS_DEFAULT |
| risk_tolerance | character varying(20) | YES | HAS_DEFAULT |
| last_run_date | date | YES |  |

### go100_positions (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| portfolio_id | bigint | NO |  |
| user_id | integer | NO |  |
| account_id | integer | NO |  |
| go100_card_id | bigint | NO |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| quantity | integer | NO |  |
| remaining_qty | integer | NO |  |
| entry_price | numeric | NO |  |
| current_price | numeric | YES |  |
| status | character varying(20) | YES | HAS_DEFAULT |
| source | character varying(20) | YES | HAS_DEFAULT |
| stop_loss_price | numeric | YES |  |
| take_profit_price | numeric | YES |  |
| trailing_pct | numeric | YES |  |
| peak_price | numeric | YES |  |
| entry_date | date | YES |  |
| exit_date | date | YES |  |
| pnl_amount | numeric | YES |  |
| pnl_pct | numeric | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### go100_risk_disclaimers (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_card_id | bigint | YES |  |
| disclaimer_type | character varying(50) | NO |  |
| exceeded_field | character varying(50) | NO |  |
| default_value | numeric | NO |  |
| user_value | numeric | NO |  |
| agreed_at | timestamp with time zone | NO | HAS_DEFAULT |
| ip_address | character varying(45) | YES |  |
| user_agent | text | YES |  |

### go100_strategy_cards (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| go100_card_id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| account_id | integer | YES |  |
| strategy_name | character varying(200) | NO |  |
| strategy_type | character varying(20) | NO | HAS_DEFAULT |
| universe_filter | jsonb | YES | HAS_DEFAULT |
| entry_rules | jsonb | YES | HAS_DEFAULT |
| exit_rules | jsonb | YES | HAS_DEFAULT |
| risk_params | jsonb | YES | HAS_DEFAULT |
| strategy_params | jsonb | YES | HAS_DEFAULT |
| allocated_amount | numeric | YES | HAS_DEFAULT |
| max_stocks | integer | YES | HAS_DEFAULT |
| card_status | character varying(20) | NO | HAS_DEFAULT |
| is_active | boolean | YES | HAS_DEFAULT |
| is_live | boolean | YES | HAS_DEFAULT |
| source_type | character varying(20) | YES | HAS_DEFAULT |
| source_store_card_id | bigint | YES |  |
| source_user_id | integer | YES |  |
| llm_session_id | character varying(100) | YES |  |
| last_backtest_id | bigint | YES |  |
| last_backtest_return | numeric | YES |  |
| last_backtest_mdd | numeric | YES |  |
| last_backtest_sharpe | numeric | YES |  |
| last_backtest_at | timestamp with time zone | YES |  |
| paper_total_return | numeric | YES |  |
| paper_start_date | date | YES |  |
| paper_days | integer | YES | HAS_DEFAULT |
| disclaimer_agreed | boolean | YES | HAS_DEFAULT |
| disclaimer_agreed_at | timestamp with time zone | YES |  |
| dedicated_account | boolean | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |
| is_featured | boolean | NO | HAS_DEFAULT |
| is_public | boolean | NO | HAS_DEFAULT |
| featured_order | integer | NO | HAS_DEFAULT |

### go100_trades (GO100)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| order_id | bigint | YES |  |
| portfolio_id | bigint | NO |  |
| user_id | integer | NO |  |
| account_id | integer | NO |  |
| go100_card_id | bigint | NO |  |
| position_id | bigint | YES |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| side | character varying(10) | NO |  |
| price | numeric | NO |  |
| quantity | integer | NO |  |
| amount | numeric | YES |  |
| pnl_amount | numeric | YES |  |
| pnl_pct | numeric | YES |  |
| is_paper | boolean | YES | HAS_DEFAULT |
| trade_date | date | YES |  |
| traded_at | timestamp with time zone | YES | HAS_DEFAULT |

### index_daily (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| index_code | character varying(10) | NO |  |
| index_name | character varying(20) | YES |  |
| date | character varying(8) | NO |  |
| open | real | YES |  |
| high | real | YES |  |
| low | real | YES |  |
| close | real | YES |  |
| volume | bigint | YES |  |
| trade_amount | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### kis_configs (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| app_key | character varying(255) | NO |  |
| app_secret | text | NO | 🔒 암호화/민감 |
| account_number | character varying(50) | NO |  |
| account_product_code | character varying(10) | YES |  |
| is_production | boolean | YES |  |
| access_token | text | YES | 🔒 암호화/민감 |
| token_expires_at | timestamp without time zone | YES | 🔒 암호화/민감 |
| is_active | boolean | YES |  |
| is_verified | boolean | YES |  |
| last_verified_at | timestamp without time zone | YES |  |
| last_error | text | YES |  |
| error_count | integer | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES |  |

### liquidation_logs (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| log_id | bigint | NO | HAS_DEFAULT |
| session_id | bigint | NO |  |
| order_id | bigint | YES |  |
| log_level | character varying(10) | NO | HAS_DEFAULT |
| event_type | character varying(30) | NO |  |
| message | text | NO |  |
| raw_data | jsonb | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### liquidation_orders (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| order_id | bigint | NO | HAS_DEFAULT |
| session_id | bigint | NO |  |
| stock_code | character varying(10) | NO |  |
| stock_name | character varying(50) | YES |  |
| target_qty | integer | NO |  |
| sold_qty | integer | NO | HAS_DEFAULT |
| remaining_qty | integer | NO |  |
| attempt_count | integer | NO | HAS_DEFAULT |
| max_attempts | integer | NO | HAS_DEFAULT |
| avg_sell_price | numeric | NO | HAS_DEFAULT |
| total_sell_amount | numeric | NO | HAS_DEFAULT |
| status | character varying(20) | NO | HAS_DEFAULT |
| last_kis_order_id | character varying(50) | YES |  |
| error_message | text | YES |  |
| position_id | bigint | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |

### liquidation_sessions (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| session_id | bigint | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| account_id | bigint | YES |  |
| card_id | bigint | YES |  |
| trigger_type | character varying(20) | NO |  |
| status | character varying(20) | NO | HAS_DEFAULT |
| target_count | integer | NO | HAS_DEFAULT |
| success_count | integer | NO | HAS_DEFAULT |
| fail_count | integer | NO | HAS_DEFAULT |
| skip_count | integer | NO | HAS_DEFAULT |
| total_sold_amount | numeric | NO | HAS_DEFAULT |
| buy_block_active | boolean | NO | HAS_DEFAULT |
| timeout_at | timestamp with time zone | NO |  |
| started_at | timestamp with time zone | NO | HAS_DEFAULT |
| completed_at | timestamp with time zone | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### live_positions (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_email | text | NO |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(255) | NO |  |
| quantity | integer | NO |  |
| entry_price | real | NO |  |
| entry_time | timestamp without time zone | NO |  |
| strategy | text | NO |  |
| current_price | real | YES |  |
| unrealized_pnl | real | YES |  |
| unrealized_pnl_pct | real | YES |  |
| session_id | text | NO |  |
| account_number | text | YES |  |
| status | text | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### live_trading_results (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_email | text | NO |  |
| timestamp | timestamp without time zone | YES | HAS_DEFAULT |
| session_id | text | NO |  |
| stock_code | text | NO |  |
| stock_name | text | NO |  |
| strategy | text | NO |  |
| entry_price | real | NO |  |
| exit_price | real | YES |  |
| quantity | integer | NO |  |
| pnl | real | YES |  |
| pnl_pct | real | YES |  |
| result | text | YES |  |
| capital_tier | text | YES | HAS_DEFAULT |
| account_number | text | YES |  |
| trading_mode | text | YES | HAS_DEFAULT |
| entry_time | timestamp without time zone | YES |  |
| exit_time | timestamp without time zone | YES |  |
| exit_reason | character varying(100) | YES | HAS_DEFAULT |

### llm_cost_daily (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| date | date | NO |  |
| user_id | bigint | NO |  |
| request_type | character varying(32) | NO |  |
| vendor | character varying(16) | NO |  |
| model | character varying(64) | NO |  |
| total_calls | integer | NO | HAS_DEFAULT |
| total_input_tokens | bigint | NO | 🔒 암호화/민감 |
| total_output_tokens | bigint | NO | 🔒 암호화/민감 |
| total_cost_usd | numeric | NO | HAS_DEFAULT |
| cache_hit_count | integer | NO | HAS_DEFAULT |
| failover_count | integer | NO | HAS_DEFAULT |
| avg_latency_ms | integer | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### llm_requests (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| session_id | character varying(64) | NO |  |
| request_type | character varying(32) | NO |  |
| vendor | character varying(16) | NO |  |
| model | character varying(64) | NO |  |
| input_tokens | integer | NO | 🔒 암호화/민감 |
| output_tokens | integer | NO | 🔒 암호화/민감 |
| cache_creation_tokens | integer | NO | 🔒 암호화/민감 |
| cache_read_tokens | integer | NO | 🔒 암호화/민감 |
| cost_usd | numeric | NO | HAS_DEFAULT |
| is_cache_hit | boolean | NO | HAS_DEFAULT |
| is_failover | boolean | NO | HAS_DEFAULT |
| is_batch | boolean | NO | HAS_DEFAULT |
| latency_ms | integer | NO | HAS_DEFAULT |
| error_code | character varying(32) | YES |  |
| failover_from_vendor | character varying(16) | YES |  |
| failover_from_model | character varying(64) | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### market_data_min (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | text | NO |  |
| ts | text | NO |  |
| open | real | YES |  |
| high | real | YES |  |
| low | real | YES |  |
| close | real | YES |  |
| volume | real | YES |  |
| acml_tr_pbmn | real | YES |  |
| chgh_rate | real | YES |  |
| volume_power | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### market_turnover_daily (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| trade_date | date | NO |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(255) | YES |  |
| turnover_value | real | YES | HAS_DEFAULT |
| rank | integer | YES | HAS_DEFAULT |
| source | text | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### ohlcv_1m_history (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| stock_code | text | NO |  |
| stock_name | text | YES |  |
| date | text | NO |  |
| time | text | NO |  |
| open | real | YES |  |
| high | real | YES |  |
| low | real | YES |  |
| close | real | YES |  |
| volume | real | YES |  |

### ohlcv_daily (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| date | character varying(8) | NO |  |
| open | real | YES |  |
| high | real | YES |  |
| low | real | YES |  |
| close | real | YES |  |
| volume | bigint | YES |  |
| trade_amount | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### ohlcv_monthly (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| date | character varying(8) | NO |  |
| open | real | YES |  |
| high | real | YES |  |
| low | real | YES |  |
| close | real | YES |  |
| volume | bigint | YES |  |
| trade_amount | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### ohlcv_weekly (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| date | character varying(8) | NO |  |
| open | real | YES |  |
| high | real | YES |  |
| low | real | YES |  |
| close | real | YES |  |
| volume | bigint | YES |  |
| trade_amount | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### orderbook_snapshots (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(20) | NO |  |
| snapshot_time | timestamp without time zone | NO |  |
| best_ask_price | real | YES | HAS_DEFAULT |
| best_bid_price | real | YES | HAS_DEFAULT |
| total_ask_volume | real | YES | HAS_DEFAULT |
| total_bid_volume | real | YES | HAS_DEFAULT |
| asks_json | text | YES |  |
| bids_json | text | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### orders (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| signal_id | integer | YES |  |
| strategy_id | character varying(50) | NO |  |
| symbol | character varying(20) | NO |  |
| side | character varying(10) | NO |  |
| quantity | integer | NO |  |
| price | real | YES |  |
| order_type | character varying(20) | NO | HAS_DEFAULT |
| status | character varying(20) | NO | HAS_DEFAULT |
| kis_order_no | character varying(100) | YES |  |
| error_message | text | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| filled_at | timestamp without time zone | YES |  |

### payments (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| plan_type | character varying(20) | NO |  |
| billing_cycle | character varying(7) | NO |  |
| amount | real | NO |  |
| imp_uid | character varying(100) | YES |  |
| merchant_uid | character varying(100) | YES |  |
| status | character varying(9) | YES |  |
| pg_response | text | YES |  |
| fail_reason | character varying(255) | YES |  |
| completed_at | timestamp without time zone | YES |  |
| refunded_at | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### pending_orders (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| strategy_name | character varying(100) | NO |  |
| order_type | character varying(10) | NO |  |
| target_price | real | NO |  |
| quantity | integer | NO |  |
| priority | integer | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| expires_at | timestamp without time zone | YES |  |
| executed_at | timestamp without time zone | YES |  |
| status | character varying(20) | YES | HAS_DEFAULT |
| execution_price | real | YES |  |
| notes | text | YES |  |
| updated_at | timestamp without time zone | YES |  |

### portfolios (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| initial_capital | real | NO |  |
| current_capital | real | NO |  |
| total_return | real | YES |  |
| scenario | character varying(50) | NO |  |
| kelly_fraction | real | YES |  |
| market_regime | character varying(50) | YES |  |
| status | character varying(6) | NO |  |
| sharpe_ratio | real | YES |  |
| max_drawdown | real | YES |  |
| win_rate | real | YES |  |
| total_trades | integer | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES |  |

### positions (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| portfolio_id | integer | NO |  |
| strategy_name | character varying(100) | NO |  |
| strategy_category | character varying(50) | NO |  |
| symbol | character varying(20) | YES |  |
| quantity | integer | YES |  |
| entry_price | real | YES |  |
| current_price | real | YES |  |
| allocated_capital | real | NO |  |
| pnl | real | YES |  |
| pnl_percent | real | YES |  |
| status | character varying(6) | NO |  |
| opened_at | timestamp without time zone | YES | HAS_DEFAULT |
| closed_at | timestamp without time zone | YES |  |

### price_tick_snapshots (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(20) | NO |  |
| ts | timestamp without time zone | NO |  |
| price | real | YES | HAS_DEFAULT |
| cumulative_volume | real | YES | HAS_DEFAULT |
| volume_delta | real | YES | HAS_DEFAULT |
| change_rate | real | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### real_trades (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| timestamp | timestamp without time zone | NO |  |
| account_email | character varying(255) | NO |  |
| strategy_id | character varying(50) | NO |  |
| strategy_name | character varying(255) | NO |  |
| ticker | character varying(20) | NO |  |
| signal | character varying(10) | NO |  |
| order_id | character varying(100) | YES |  |
| price | real | NO |  |
| quantity | integer | NO |  |
| position_size | real | NO |  |
| filled_price | real | YES |  |
| filled_quantity | integer | YES |  |
| commission | real | YES | HAS_DEFAULT |
| slippage | real | YES | HAS_DEFAULT |
| status | character varying(20) | NO |  |
| error_message | text | YES |  |
| entry_price | real | YES |  |
| exit_price | real | YES |  |
| realized_pnl | real | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### scalping_features_daily (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(20) | NO |  |
| feature_date | date | NO |  |
| avg_spread_pct | real | YES | HAS_DEFAULT |
| avg_imbalance | real | YES | HAS_DEFAULT |
| avg_volume_delta | real | YES | HAS_DEFAULT |
| avg_change_rate | real | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### social_accounts (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| provider | character varying(50) | NO |  |
| provider_user_id | character varying(255) | NO |  |
| email | character varying(255) | YES |  |
| name | character varying(100) | YES |  |
| profile_image | character varying(500) | YES |  |
| access_token | character varying(500) | YES | 🔒 암호화/민감 |
| refresh_token | character varying(500) | YES | 🔒 암호화/민감 |
| token_expires_at | timestamp without time zone | YES | 🔒 암호화/민감 |
| is_active | boolean | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES |  |
| last_login_at | timestamp without time zone | YES |  |

### stock_fundamentals (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| date | character varying(8) | NO |  |
| per | real | YES |  |
| pbr | real | YES |  |
| eps | real | YES |  |
| bps | real | YES |  |
| market_cap | bigint | YES |  |
| shares_outstanding | bigint | YES |  |
| face_value | real | YES |  |
| capital | bigint | YES |  |
| loan_remain_rate | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### stock_universe (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | NO |  |
| market | character varying(10) | NO |  |
| market_cap | bigint | YES |  |
| trade_volume | bigint | YES |  |
| trade_amount | bigint | YES |  |
| sector | character varying(100) | YES |  |
| rank_market_cap | integer | YES |  |
| rank_trade_amount | integer | YES |  |
| collected_at | timestamp without time zone | YES | HAS_DEFAULT |
| is_active | boolean | YES | HAS_DEFAULT |
| per | numeric | YES |  |
| pbr | numeric | YES |  |
| eps | numeric | YES |  |
| dividend_yield | numeric | YES |  |
| market_cap_value | bigint | YES |  |
| sector_large | character varying(100) | YES |  |
| sector_mid | character varying(100) | YES |  |
| sector_small | character varying(100) | YES |  |

### strategies (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | character varying(50) | NO |  |
| name | character varying(255) | NO |  |
| description | text | YES |  |
| category | character varying(50) | YES |  |
| is_premium | boolean | YES |  |
| avg_win_rate | real | YES |  |
| avg_return | real | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| holding_period | real | YES |  |
| sharpe | real | YES |  |
| mdd | real | YES |  |
| risk_level | text | YES |  |
| is_approved | boolean | YES | HAS_DEFAULT |
| approval_date | timestamp without time zone | YES |  |
| optimization_score | real | YES | HAS_DEFAULT |
| sortino_ratio | real | YES | HAS_DEFAULT |
| settings | text | YES |  |
| strategy_key | text | YES |  |
| is_active | boolean | YES | HAS_DEFAULT |

### strategy_allocations (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_id | character varying(50) | NO |  |
| allocated_capital | real | NO |  |
| capital_pct | real | NO |  |
| position_size | real | NO |  |
| position_size_pct | real | NO |  |
| stop_loss_pct | real | NO |  |
| take_profit_pct | real | NO |  |
| max_daily_trades | integer | NO |  |
| max_position_count | integer | NO |  |
| priority | integer | NO |  |
| risk_level | text | NO |  |
| is_active | boolean | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### strategy_cards (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| card_id | bigint | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| account_id | bigint | NO |  |
| strategy_name | character varying(100) | NO |  |
| strategy_type | character varying(30) | NO | HAS_DEFAULT |
| strategy_params | jsonb | NO | HAS_DEFAULT |
| allocated_amount | numeric | NO | HAS_DEFAULT |
| max_stocks | integer | NO | HAS_DEFAULT |
| is_live | boolean | NO | HAS_DEFAULT |
| is_active | boolean | NO | HAS_DEFAULT |
| desk_id | character varying(10) | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |
| entry_rules | jsonb | YES | HAS_DEFAULT |
| exit_rules | jsonb | YES | HAS_DEFAULT |
| risk_params | jsonb | YES | HAS_DEFAULT |
| buy_phases | jsonb | YES | HAS_DEFAULT |
| sell_phases | jsonb | YES | HAS_DEFAULT |
| promotion_rules | jsonb | YES | HAS_DEFAULT |
| demotion_rules | jsonb | YES | HAS_DEFAULT |
| backtest_compatible | boolean | YES | HAS_DEFAULT |
| priority | integer | YES | HAS_DEFAULT |
| version | integer | YES | HAS_DEFAULT |

### strategy_performance (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| strategy_id | character varying(50) | NO |  |
| strategy_name | character varying(255) | NO |  |
| trade_date | date | NO |  |
| real_trades | integer | YES | HAS_DEFAULT |
| real_wins | integer | YES | HAS_DEFAULT |
| real_losses | integer | YES | HAS_DEFAULT |
| real_pnl | real | YES | HAS_DEFAULT |
| real_win_rate | real | YES | HAS_DEFAULT |
| virtual_trades | integer | YES | HAS_DEFAULT |
| virtual_wins | integer | YES | HAS_DEFAULT |
| virtual_losses | integer | YES | HAS_DEFAULT |
| virtual_pnl | real | YES | HAS_DEFAULT |
| virtual_win_rate | real | YES | HAS_DEFAULT |
| performance_diff | real | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### trade_comparisons (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| timestamp | timestamp without time zone | NO |  |
| strategy_id | character varying(50) | NO |  |
| strategy_name | character varying(255) | NO |  |
| real_trade_id | integer | YES |  |
| real_executed | boolean | YES |  |
| real_price | real | YES |  |
| real_quantity | integer | YES |  |
| real_commission | real | YES |  |
| real_slippage | real | YES |  |
| virtual_trade_id | integer | YES |  |
| virtual_executed | boolean | YES |  |
| virtual_price | real | YES |  |
| virtual_quantity | integer | YES |  |
| price_diff | real | YES | HAS_DEFAULT |
| quantity_diff | integer | YES | HAS_DEFAULT |
| cost_diff | real | YES | HAS_DEFAULT |
| execution_time_diff | real | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### trade_verifications (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| real_trade_id | integer | NO |  |
| order_id | character varying(50) | YES |  |
| verification_date | timestamp without time zone | NO | HAS_DEFAULT |
| verification_status | character varying(20) | NO |  |
| kis_verified | boolean | YES | HAS_DEFAULT |
| kis_order_no | character varying(50) | YES |  |
| kis_filled_qty | integer | YES |  |
| kis_filled_price | real | YES |  |
| kis_filled_amount | real | YES |  |
| mismatch_reasons | text | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### trades (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_id | character varying(50) | YES |  |
| symbol | character varying(20) | NO |  |
| symbol_name | character varying(100) | YES |  |
| trade_type | character varying(4) | NO | HAS_DEFAULT |
| quantity | integer | NO |  |
| price | real | NO |  |
| total_amount | real | NO |  |
| profit_loss | real | YES |  |
| profit_loss_rate | real | YES |  |
| status | character varying(9) | YES |  |
| order_number | character varying(50) | YES |  |
| kis_response | character varying(500) | YES |  |
| executed_at | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| side | character varying(10) | YES |  |
| order_id | character varying(100) | YES |  |
| order_type | character varying(20) | YES |  |
| realized_pnl | real | YES | HAS_DEFAULT |
| commission | real | YES | HAS_DEFAULT |
| tax | real | YES | HAS_DEFAULT |
| net_pnl | real | YES | HAS_DEFAULT |
| signal_confidence | real | YES |  |
| signal_reason | text | YES |  |
| ticker | character varying(20) | YES |  |

### trading_events (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_email | text | NO |  |
| event_type | text | NO |  |
| timestamp | timestamp without time zone | YES | HAS_DEFAULT |
| stock_code | text | YES |  |
| message | text | YES |  |
| details | text | YES |  |

### trading_signals (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| strategy_name | character varying(100) | NO |  |
| signal_type | character varying(10) | NO |  |
| signal_strength | real | YES | HAS_DEFAULT |
| detected_at | timestamp without time zone | YES | HAS_DEFAULT |
| executed_at | timestamp without time zone | YES |  |
| status | character varying(20) | YES | HAS_DEFAULT |
| execution_price | real | YES |  |
| execution_quantity | integer | YES |  |
| notes | text | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES |  |

### user_push_subscriptions (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| endpoint | text | NO |  |
| p256dh | text | NO |  |
| auth | text | NO |  |
| expiration_time | integer | YES |  |
| is_active | integer | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### user_sessions (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| session_id | bigint | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| refresh_token | character varying(512) | NO | 🔒 암호화/민감 |
| device_info | character varying(255) | YES |  |
| ip_address | inet | YES |  |
| expires_at | timestamp with time zone | NO |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### user_settings (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| telegram_bot_token | character varying(255) | YES | 🔒 암호화/민감 |
| telegram_chat_id | character varying(100) | YES |  |
| telegram_buy_alert | boolean | YES |  |
| telegram_sell_alert | boolean | YES |  |
| telegram_daily_report | boolean | YES |  |
| telegram_error_alert | boolean | YES |  |
| email_address | character varying(255) | YES |  |
| email_weekly_report | boolean | YES |  |
| email_monthly_report | boolean | YES |  |
| email_loss_alert | boolean | YES |  |
| auto_trading_enabled | boolean | YES |  |
| max_investment_amount | integer | YES |  |
| max_positions | integer | YES |  |
| trading_start_time | character varying(10) | YES |  |
| trading_end_time | character varying(10) | YES |  |
| use_market_order | boolean | YES |  |
| stop_loss_percent | real | YES |  |
| daily_loss_limit | real | YES |  |
| take_profit_percent | real | YES |  |
| use_trailing_stop | boolean | YES |  |
| trailing_stop_percent | real | YES |  |
| investment_experience | character varying(50) | YES |  |
| risk_tolerance | character varying(50) | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |
| ai_auto_trading_enabled | boolean | YES | HAS_DEFAULT |
| unfilled_mode | character varying(50) | YES | HAS_DEFAULT |
| unfilled_timeout | integer | YES | HAS_DEFAULT |
| notify_trade | boolean | YES | HAS_DEFAULT |
| notify_stop_loss | boolean | YES | HAS_DEFAULT |
| notify_take_profit | boolean | YES | HAS_DEFAULT |
| notify_daily_report | boolean | YES | HAS_DEFAULT |
| default_stop_loss_pct | numeric | YES | HAS_DEFAULT |
| default_take_profit_pct | numeric | YES | HAS_DEFAULT |
| default_invest_amount | numeric | YES | HAS_DEFAULT |
| theme | character varying(50) | YES | HAS_DEFAULT |

### user_strategies (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_id | character varying(50) | NO |  |
| is_active | boolean | YES |  |
| rank | integer | YES |  |
| win_rate | real | YES |  |
| avg_return | real | YES |  |
| total_trades | integer | YES |  |
| last_executed | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES |  |
| dynamic_weight | real | YES | HAS_DEFAULT |
| last_rebalance_at | timestamp without time zone | YES |  |
| performance_score | real | YES | HAS_DEFAULT |
| is_pinned | integer | YES | HAS_DEFAULT |
| weight | numeric | YES | HAS_DEFAULT |

### users (SHARED)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| email | character varying(255) | NO |  |
| name | character varying(255) | NO |  |
| phone | character varying(50) | YES |  |
| hashed_password | character varying(255) | YES | 🔒 암호화/민감 |
| role | character varying(11) | YES |  |
| plan_type | character varying(10) | YES |  |
| is_active | boolean | YES |  |
| is_verified | boolean | YES |  |
| agreed_terms | boolean | YES |  |
| agreed_privacy | boolean | YES |  |
| agreed_marketing | boolean | YES |  |
| subscription_end | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES |  |
| last_login | timestamp without time zone | YES |  |

### v4_account_config (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| account_type | character varying(10) | NO |  |
| account_no | character varying(20) | NO |  |
| product_code | character varying(4) | NO | HAS_DEFAULT |
| app_key | text | NO |  |
| app_secret | text | NO | 🔒 암호화/민감 |
| base_url | character varying(100) | NO |  |
| hts_id | character varying(20) | YES |  |
| is_active | boolean | YES | HAS_DEFAULT |
| daily_order_limit | bigint | YES | HAS_DEFAULT |
| single_stock_max_pct | numeric | YES | HAS_DEFAULT |
| consecutive_loss_halt | integer | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_account_holdings (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| config_id | integer | NO |  |
| snapshot_at | timestamp with time zone | NO | HAS_DEFAULT |
| d2_deposit | bigint | YES |  |
| total_deposit | bigint | YES |  |
| total_eval | bigint | YES |  |
| total_pnl | bigint | YES |  |
| total_pnl_pct | numeric | YES |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| qty | integer | YES | HAS_DEFAULT |
| avg_price | numeric | YES |  |
| current_price | numeric | YES |  |
| eval_amount | bigint | YES |  |
| pnl_amount | bigint | YES |  |
| pnl_pct | numeric | YES |  |
| source | character varying(20) | NO | HAS_DEFAULT |
| position_id | bigint | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_account_sync_log (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| config_id | integer | NO |  |
| synced_at | timestamp with time zone | NO | HAS_DEFAULT |
| actual_cash | bigint | YES |  |
| v41_cash | bigint | YES |  |
| deficit | bigint | YES | HAS_DEFAULT |
| surplus | bigint | YES | HAS_DEFAULT |
| total_holdings | integer | YES | HAS_DEFAULT |
| matched_v41 | integer | YES | HAS_DEFAULT |
| external_count | integer | YES | HAS_DEFAULT |
| missing_v41 | integer | YES | HAS_DEFAULT |
| qty_mismatch | integer | YES | HAS_DEFAULT |
| action_taken | text | YES |  |
| fund_adjusted | boolean | YES | HAS_DEFAULT |
| positions_fixed | integer | YES | HAS_DEFAULT |
| alert_generated | boolean | YES | HAS_DEFAULT |
| alert_ids | ARRAY | YES |  |
| sync_duration_ms | integer | YES |  |
| error_message | text | YES |  |

### v4_alerts (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| alert_id | bigint | NO | HAS_DEFAULT |
| alert_type | character varying(50) | NO |  |
| severity | character varying(20) | NO | HAS_DEFAULT |
| title | character varying(200) | NO |  |
| message | text | YES |  |
| desk_id | integer | YES |  |
| ticker | character varying(20) | YES |  |
| data | jsonb | YES |  |
| is_read | boolean | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_api_error_log (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| account_config_id | integer | YES |  |
| endpoint | character varying(200) | YES |  |
| tr_id | character varying(20) | YES |  |
| error_code | character varying(20) | YES |  |
| error_message | text | YES |  |
| request_body | jsonb | YES |  |
| response_body | jsonb | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_api_tokens (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| account_config_id | integer | YES |  |
| access_token | text | NO | 🔒 암호화/민감 |
| token_type | character varying(20) | YES | 🔒 암호화/민감 |
| expires_at | timestamp with time zone | NO |  |
| issued_at | timestamp with time zone | YES | HAS_DEFAULT |
| is_valid | boolean | YES | HAS_DEFAULT |
| issue_count_today | integer | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_backtest_daily (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| session_id | bigint | YES |  |
| trade_date | date | NO |  |
| total_asset | numeric | YES |  |
| cash_balance | numeric | YES |  |
| holding_value | numeric | YES |  |
| daily_pnl | numeric | YES |  |
| daily_pnl_pct | numeric | YES |  |
| cumulative_pct | numeric | YES |  |
| current_stage | integer | YES |  |
| desk_allocation | jsonb | YES |  |
| open_positions | integer | YES |  |
| trades_today | integer | YES |  |

### v4_backtest_desk_detail (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| run_id | character varying(50) | YES |  |
| desk_id | integer | NO |  |
| class_type | character varying(10) | YES |  |
| total_trades | integer | YES |  |
| win_trades | integer | YES |  |
| lose_trades | integer | YES |  |
| win_rate_pct | numeric | YES |  |
| total_return_pct | numeric | YES |  |
| avg_return_pct | numeric | YES |  |
| max_win_pct | numeric | YES |  |
| max_loss_pct | numeric | YES |  |
| avg_holding_days | numeric | YES |  |
| profit_factor | numeric | YES |  |
| upgrade_count | integer | YES | HAS_DEFAULT |

### v4_backtest_equity (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| run_id | character varying(50) | YES |  |
| trade_date | character varying(8) | NO |  |
| equity | bigint | NO |  |
| daily_return_pct | numeric | YES |  |
| open_positions | integer | YES |  |
| daily_trades | integer | YES |  |
| daily_pnl | bigint | YES |  |

### v4_backtest_profile (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| profile_id | integer | NO | HAS_DEFAULT |
| card_id | integer | YES |  |
| desk_id | integer | NO |  |
| profile_name | character varying(100) | NO |  |
| engine_version | character varying(10) | NO | HAS_DEFAULT |
| params | jsonb | NO | HAS_DEFAULT |
| is_active | boolean | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | NO | HAS_DEFAULT |
| updated_at | timestamp without time zone | NO | HAS_DEFAULT |

### v4_backtest_results (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| strategy_name | character varying(100) | NO |  |
| start_date | date | NO |  |
| end_date | date | NO |  |
| initial_capital | numeric | NO |  |
| final_capital | numeric | YES |  |
| total_return_pct | numeric | YES |  |
| max_drawdown_pct | numeric | YES |  |
| sharpe_ratio | numeric | YES |  |
| win_rate | numeric | YES |  |
| total_trades | integer | YES | HAS_DEFAULT |
| avg_holding_days | numeric | YES |  |
| parameters | jsonb | YES |  |
| daily_snapshots | jsonb | YES |  |
| trade_records | jsonb | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| user_id | integer | YES |  |

### v4_backtest_results_desk_run (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| strategy_name | character varying(80) | NO |  |
| stock_code | character varying(10) | NO |  |
| desk_id | integer | YES |  |
| start_date | date | YES |  |
| end_date | date | YES |  |
| total_trades | integer | YES |  |
| win_rate | numeric | YES |  |
| total_return | numeric | YES |  |
| max_drawdown | numeric | YES |  |
| sharpe_ratio | numeric | YES |  |
| profit_factor | numeric | YES |  |
| avg_hold_days | numeric | YES |  |
| tested_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_backtest_runs (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_card_id | integer | YES |  |
| strategy_name | character varying(100) | YES |  |
| stock_codes | ARRAY | YES |  |
| start_date | date | NO |  |
| end_date | date | NO |  |
| initial_capital | bigint | YES | HAS_DEFAULT |
| total_return | numeric | YES |  |
| annualized_return | numeric | YES |  |
| max_drawdown | numeric | YES |  |
| sharpe_ratio | numeric | YES |  |
| win_rate | numeric | YES |  |
| total_trades | integer | YES | HAS_DEFAULT |
| winning_trades | integer | YES | HAS_DEFAULT |
| losing_trades | integer | YES | HAS_DEFAULT |
| avg_profit_per_trade | numeric | YES |  |
| max_consecutive_wins | integer | YES | HAS_DEFAULT |
| max_consecutive_losses | integer | YES | HAS_DEFAULT |
| profit_factor | numeric | YES |  |
| status | character varying(20) | YES | HAS_DEFAULT |
| error_message | text | YES |  |
| params | jsonb | YES |  |
| result_detail | jsonb | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| completed_at | timestamp with time zone | YES |  |

### v4_backtest_runs_legacy (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| run_id | character varying(50) | NO |  |
| start_date | character varying(8) | NO |  |
| end_date | character varying(8) | NO |  |
| initial_capital | bigint | NO |  |
| desks_tested | character varying(20) | NO |  |
| use_minute_data | boolean | YES | HAS_DEFAULT |
| slippage_pct | numeric | YES |  |
| commission_pct | numeric | YES |  |
| risk_management | boolean | YES | HAS_DEFAULT |
| total_return_pct | numeric | YES |  |
| cagr_pct | numeric | YES |  |
| mdd_pct | numeric | YES |  |
| sharpe_ratio | numeric | YES |  |
| total_trades | integer | YES |  |
| win_rate_pct | numeric | YES |  |
| profit_factor | numeric | YES |  |
| avg_holding_days | numeric | YES |  |
| final_equity | bigint | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_backtest_sessions (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| session_id | bigint | NO | HAS_DEFAULT |
| session_name | character varying(100) | NO |  |
| start_date | date | NO |  |
| end_date | date | NO |  |
| initial_capital | numeric | NO |  |
| stage_config | jsonb | NO |  |
| desk_configs | jsonb | NO |  |
| split_configs | jsonb | NO |  |
| status | character varying(20) | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| completed_at | timestamp with time zone | YES |  |

### v4_backtest_summary (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| session_id | bigint | YES |  |
| total_days | integer | YES |  |
| total_trades | integer | YES |  |
| winning_trades | integer | YES |  |
| losing_trades | integer | YES |  |
| win_rate | numeric | YES |  |
| total_return_pct | numeric | YES |  |
| annualized_return | numeric | YES |  |
| max_drawdown_pct | numeric | YES |  |
| sharpe_ratio | numeric | YES |  |
| profit_factor | numeric | YES |  |
| avg_win_pct | numeric | YES |  |
| avg_loss_pct | numeric | YES |  |
| max_consecutive_wins | integer | YES |  |
| max_consecutive_losses | integer | YES |  |
| final_capital | numeric | YES |  |
| desk_performance | jsonb | YES |  |
| stage_transitions | integer | YES |  |
| total_transfers | integer | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_backtest_trade_log (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| run_id | character varying(50) | YES |  |
| desk_id | integer | NO |  |
| class_type | character varying(10) | YES |  |
| stock_code | character varying(10) | NO |  |
| stock_name | character varying(50) | YES |  |
| entry_date | character varying(8) | YES |  |
| entry_price | numeric | YES |  |
| exit_date | character varying(8) | YES |  |
| exit_price | numeric | YES |  |
| quantity | integer | YES |  |
| return_pct | numeric | YES |  |
| pnl | bigint | YES |  |
| exit_reason | character varying(30) | YES |  |
| holding_days | integer | YES |  |
| sector | character varying(50) | YES |  |

### v4_backtest_trades (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| session_id | bigint | YES |  |
| desk_id | integer | NO |  |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_type | character varying(10) | NO |  |
| quantity | integer | NO |  |
| price | numeric | NO |  |
| amount | numeric | NO |  |
| split_phase | integer | YES | HAS_DEFAULT |
| transfer_to | integer | YES |  |
| pnl | numeric | YES |  |
| pnl_pct | numeric | YES |  |
| reason | character varying(100) | YES |  |
| card_id | integer | YES |  |
| exit_reason | character varying(30) | YES | HAS_DEFAULT |
| entry_date | date | YES |  |
| exit_date | date | YES |  |
| hold_days | integer | YES |  |
| entry_datetime | timestamp without time zone | YES |  |
| exit_datetime | timestamp without time zone | YES |  |
| entry_price | numeric | YES |  |
| exit_price | numeric | YES |  |
| mfe_pct | numeric | YES |  |
| mae_pct | numeric | YES |  |
| mfe_price | numeric | YES |  |
| mae_price | numeric | YES |  |
| regime_at_entry | character varying(30) | YES |  |
| indicator_snapshot | jsonb | YES |  |
| slippage_pct | numeric | YES |  |
| commission | numeric | YES |  |
| sector | character varying(50) | YES |  |
| strategy_name | character varying(100) | YES |  |
| entry_volume | bigint | YES |  |
| entry_spread_pct | numeric | YES |  |

### v4_bet_history (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| ticker | character varying(20) | YES |  |
| desk_id | integer | YES |  |
| universe_score | numeric | YES |  |
| base_bet | bigint | YES |  |
| mood_modifier | numeric | YES |  |
| regime_modifier | numeric | YES |  |
| streak_modifier | numeric | YES |  |
| calendar_modifier | numeric | YES |  |
| risk_cap | bigint | YES |  |
| final_bet | bigint | YES |  |
| confidence | character varying(10) | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_broker_trades (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| broker_name | character varying(50) | YES |  |
| buy_amount | bigint | YES | HAS_DEFAULT |
| sell_amount | bigint | YES | HAS_DEFAULT |
| net_amount | bigint | YES | HAS_DEFAULT |
| buy_volume | bigint | YES | HAS_DEFAULT |
| sell_volume | bigint | YES | HAS_DEFAULT |
| net_volume | bigint | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_chat_messages (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| session_id | integer | NO |  |
| role | character varying(20) | NO |  |
| content | text | NO |  |
| model | character varying(50) | YES |  |
| tokens_used | integer | YES | 🔒 암호화/민감 |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_chat_sessions (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| title | character varying(200) | YES |  |
| model | character varying(50) | YES |  |
| category | character varying(50) | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_condition_search (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| condition_name | character varying(100) | NO |  |
| condition_id | integer | YES |  |
| stock_code | character varying(10) | NO |  |
| stock_name | character varying(50) | YES |  |
| signal_type | character varying(10) | YES |  |
| signal_time | timestamp with time zone | NO |  |
| current_price | integer | YES |  |
| volume | bigint | YES |  |
| change_rate | numeric | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_credit_balance (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| credit_balance | bigint | YES |  |
| credit_amount | bigint | YES |  |
| credit_rate | numeric | YES |  |
| short_balance | bigint | YES |  |
| short_amount | bigint | YES |  |
| short_rate | numeric | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_daily_portfolio (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| snapshot_date | date | NO |  |
| total_asset | numeric | NO |  |
| cash_balance | numeric | NO |  |
| holding_value | numeric | NO |  |
| daily_pnl | numeric | YES | HAS_DEFAULT |
| daily_pnl_pct | numeric | YES | HAS_DEFAULT |
| cumulative_pnl | numeric | YES | HAS_DEFAULT |
| cumulative_pct | numeric | YES | HAS_DEFAULT |
| current_stage | integer | NO | HAS_DEFAULT |
| stage_changed | boolean | YES | HAS_DEFAULT |
| desk_allocation | jsonb | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_daily_reports (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| report_date | date | NO |  |
| total_trades | integer | YES |  |
| buy_trades | integer | YES |  |
| sell_trades | integer | YES |  |
| realized_pnl | bigint | YES |  |
| unrealized_pnl | bigint | YES |  |
| open_positions | integer | YES |  |
| desk_summary | jsonb | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_desk_fund (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| desk_id | integer | NO |  |
| desk_name | character varying(30) | YES |  |
| allocation_pct | numeric | NO |  |
| allocated_amount | bigint | YES |  |
| used_amount | bigint | YES | HAS_DEFAULT |
| available_amount | bigint | YES |  |
| max_positions | integer | YES |  |
| current_positions | integer | YES | HAS_DEFAULT |
| daily_loss_limit | numeric | YES |  |
| daily_loss_current | numeric | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |
| user_id | bigint | YES |  |
| account_id | bigint | YES |  |
| card_id | bigint | YES |  |

### v4_desk_strategy_mapping (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| mapping_id | integer | NO | HAS_DEFAULT |
| desk_id | integer | NO |  |
| card_id | integer | NO |  |
| stage_id | integer | NO | HAS_DEFAULT |
| allocation_pct | numeric | NO | HAS_DEFAULT |
| priority | integer | NO | HAS_DEFAULT |
| is_active | boolean | NO | HAS_DEFAULT |
| valid_from | timestamp without time zone | NO | HAS_DEFAULT |
| valid_until | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | NO | HAS_DEFAULT |
| updated_at | timestamp without time zone | NO | HAS_DEFAULT |

### v4_fund_lending (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| lending_id | bigint | NO | HAS_DEFAULT |
| from_desk_id | integer | NO |  |
| to_desk_id | integer | NO |  |
| amount | numeric | NO |  |
| lending_reason | character varying(50) | NO |  |
| status | character varying(20) | NO | HAS_DEFAULT |
| lent_at | timestamp with time zone | YES | HAS_DEFAULT |
| return_by | timestamp with time zone | NO |  |
| returned_at | timestamp with time zone | YES |  |
| returned_amount | numeric | YES |  |

### v4_fund_pool_snapshot (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| total_capital | bigint | YES |  |
| available | bigint | YES |  |
| reserved | bigint | YES |  |
| invested | bigint | YES |  |
| desk1_used | bigint | YES |  |
| desk2_used | bigint | YES |  |
| desk3_used | bigint | YES |  |
| desk4_used | bigint | YES |  |
| desk5_used | bigint | YES |  |
| fund_mode | character varying(20) | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_investor_daily (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(12) | NO |  |
| trade_date | date | NO |  |
| foreign_buy_qty | bigint | YES | HAS_DEFAULT |
| foreign_sell_qty | bigint | YES | HAS_DEFAULT |
| foreign_net_qty | bigint | YES | HAS_DEFAULT |
| foreign_net_amount | bigint | YES | HAS_DEFAULT |
| institution_buy_qty | bigint | YES | HAS_DEFAULT |
| institution_sell_qty | bigint | YES | HAS_DEFAULT |
| institution_net_qty | bigint | YES | HAS_DEFAULT |
| institution_net_amount | bigint | YES | HAS_DEFAULT |
| individual_net_qty | bigint | YES | HAS_DEFAULT |
| individual_net_amount | bigint | YES | HAS_DEFAULT |
| foreign_hold_qty | bigint | YES | HAS_DEFAULT |
| foreign_hold_ratio | numeric | YES | HAS_DEFAULT |
| program_buy_amount | bigint | YES | HAS_DEFAULT |
| program_sell_amount | bigint | YES | HAS_DEFAULT |
| program_net_amount | bigint | YES | HAS_DEFAULT |
| consecutive_foreign_buy_days | integer | YES | HAS_DEFAULT |
| consecutive_institution_buy_days | integer | YES | HAS_DEFAULT |
| collected_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_llm_usage (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| category | character varying(50) | NO |  |
| used_count | integer | NO | HAS_DEFAULT |
| daily_limit | integer | NO |  |
| usage_date | date | NO | HAS_DEFAULT |

### v4_market_calendar (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| date | date | NO |  |
| event_type | character varying(50) | YES |  |
| event_name | character varying(200) | YES |  |
| bet_modifier | numeric | NO |  |
| desk1_active | boolean | NO |  |
| desk2_active | boolean | NO |  |
| desk3_active | boolean | NO |  |
| desk4_active | boolean | NO |  |
| desk5_active | boolean | NO |  |
| class_restrictions | json | YES |  |
| note | text | YES |  |
| source | character varying(20) | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES |  |

### v4_market_investor_daily (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| market | character varying(10) | NO |  |
| trade_date | date | NO |  |
| index_close | numeric | YES |  |
| foreign_net_qty | bigint | YES |  |
| institution_net_qty | bigint | YES |  |
| individual_net_qty | bigint | YES |  |
| foreign_net_amount | bigint | YES |  |
| institution_net_amount | bigint | YES |  |

### v4_market_ranking (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| ranking_type | character varying(30) | NO |  |
| trade_date | date | NO |  |
| rank_no | integer | NO |  |
| stock_code | character varying(12) | NO |  |
| stock_name | character varying(100) | YES |  |
| current_price | bigint | YES |  |
| change_rate | numeric | YES |  |
| volume | bigint | YES |  |
| trade_amount | bigint | YES |  |
| market_cap | bigint | YES |  |
| extra_data | jsonb | YES |  |
| collected_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_market_regime_daily (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| date | date | NO |  |
| regime | character varying(30) | YES |  |
| regime_score | numeric | YES |  |
| kospi_ret_20d | numeric | YES |  |
| ma5 | numeric | YES |  |
| ma20 | numeric | YES |  |
| ma60 | numeric | YES |  |
| ma_alignment | character varying(20) | YES |  |
| bull_ratio_20d | numeric | YES |  |
| vkospi | numeric | YES |  |
| foreign_flow_20d | bigint | YES |  |
| previous_regime | character varying(30) | YES |  |
| transition_note | text | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES |  |
| hysteresis_up_count | integer | YES | HAS_DEFAULT |
| hysteresis_down_count | integer | YES | HAS_DEFAULT |
| pending_regime | character varying(30) | YES | HAS_DEFAULT |

### v4_migration_history (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| migration_name | character varying(200) | NO |  |
| applied_at | timestamp with time zone | YES | HAS_DEFAULT |
| description | text | YES |  |
| checksum | character varying(64) | YES |  |

### v4_minute_collect_progress (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| stock_code | character varying(10) | NO |  |
| stock_name | character varying(50) | YES |  |
| last_collected_date | date | YES |  |
| last_collected_time | time without time zone | YES |  |
| total_rows_collected | integer | YES | HAS_DEFAULT |
| status | character varying(20) | YES | HAS_DEFAULT |
| started_at | timestamp with time zone | YES |  |
| completed_at | timestamp with time zone | YES |  |
| error_message | text | YES |  |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_notification_channel_config (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| user_id | bigint | NO |  |
| config | jsonb | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_notification_settings (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| trade_executed | boolean | YES | HAS_DEFAULT |
| trade_failed | boolean | YES | HAS_DEFAULT |
| stop_loss_triggered | boolean | YES | HAS_DEFAULT |
| take_profit_triggered | boolean | YES | HAS_DEFAULT |
| system_error | boolean | YES | HAS_DEFAULT |
| daily_summary | boolean | YES | HAS_DEFAULT |
| login_alert | boolean | YES | HAS_DEFAULT |
| push_enabled | boolean | YES | HAS_DEFAULT |
| email_enabled | boolean | YES | HAS_DEFAULT |
| sound_enabled | boolean | YES | HAS_DEFAULT |
| quiet_hours_start | time without time zone | YES |  |
| quiet_hours_end | time without time zone | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_notifications (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| type | character varying(50) | NO |  |
| title | character varying(200) | NO |  |
| message | text | NO |  |
| data | jsonb | YES | HAS_DEFAULT |
| is_read | boolean | YES | HAS_DEFAULT |
| is_pushed | boolean | YES | HAS_DEFAULT |
| priority | character varying(20) | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| read_at | timestamp with time zone | YES |  |

### v4_ohlcv_minute (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_01 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_02 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_03 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_04 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_05 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_06 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_07 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_08 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_09 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_10 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_11 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2025_12 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2026_01 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2026_02 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_ohlcv_minute_2026_03 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| trade_time | time without time zone | NO |  |
| open_price | integer | NO |  |
| high_price | integer | NO |  |
| low_price | integer | NO |  |
| close_price | integer | NO |  |
| volume | bigint | NO | HAS_DEFAULT |
| trade_amount | bigint | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_order_executions (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| position_id | bigint | YES |  |
| desk_id | integer | NO |  |
| config_id | integer | NO |  |
| stock_code | character varying(20) | NO |  |
| order_type | character varying(10) | NO |  |
| order_subtype | character varying(20) | YES |  |
| order_price | numeric | YES |  |
| order_qty | integer | NO |  |
| order_time | timestamp with time zone | NO |  |
| exec_price | numeric | YES |  |
| exec_qty | integer | YES |  |
| exec_time | timestamp with time zone | YES |  |
| exec_status | character varying(20) | NO | HAS_DEFAULT |
| slippage_pct | numeric | YES |  |
| slippage_amt | numeric | YES |  |
| market_bid | numeric | YES |  |
| market_ask | numeric | YES |  |
| spread_pct | numeric | YES |  |
| market_volume_at_order | bigint | YES |  |
| kis_order_no | character varying(50) | YES |  |
| error_msg | text | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_order_requests (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| idempotency_key | character varying(64) | NO |  |
| user_id | bigint | NO |  |
| desk_id | integer | NO |  |
| strategy_id | character varying(20) | YES |  |
| ticker | character varying(20) | NO |  |
| side | character varying(4) | NO |  |
| quantity | integer | NO |  |
| price_type | character varying(10) | NO | HAS_DEFAULT |
| limit_price | numeric | YES |  |
| signal_id | character varying(100) | YES |  |
| position_id | bigint | YES |  |
| reservation_id | character varying(64) | YES |  |
| status | character varying(20) | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |
| submitted_at | timestamp with time zone | YES |  |
| filled_quantity | integer | NO | HAS_DEFAULT |
| order_no | character varying(50) | YES |  |
| message | text | YES |  |
| reject_reason | text | YES |  |
| source | character varying(20) | YES | HAS_DEFAULT |
| note | text | YES |  |

### v4_orderbook_realtime (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(20) | NO |  |
| captured_at | timestamp without time zone | NO |  |
| ask_price_1 | integer | YES |  |
| ask_qty_1 | integer | YES |  |
| ask_price_2 | integer | YES |  |
| ask_qty_2 | integer | YES |  |
| ask_price_3 | integer | YES |  |
| ask_qty_3 | integer | YES |  |
| ask_price_4 | integer | YES |  |
| ask_qty_4 | integer | YES |  |
| ask_price_5 | integer | YES |  |
| ask_qty_5 | integer | YES |  |
| ask_price_6 | integer | YES |  |
| ask_qty_6 | integer | YES |  |
| ask_price_7 | integer | YES |  |
| ask_qty_7 | integer | YES |  |
| ask_price_8 | integer | YES |  |
| ask_qty_8 | integer | YES |  |
| ask_price_9 | integer | YES |  |
| ask_qty_9 | integer | YES |  |
| ask_price_10 | integer | YES |  |
| ask_qty_10 | integer | YES |  |
| bid_price_1 | integer | YES |  |
| bid_qty_1 | integer | YES |  |
| bid_price_2 | integer | YES |  |
| bid_qty_2 | integer | YES |  |
| bid_price_3 | integer | YES |  |
| bid_qty_3 | integer | YES |  |
| bid_price_4 | integer | YES |  |
| bid_qty_4 | integer | YES |  |
| bid_price_5 | integer | YES |  |
| bid_qty_5 | integer | YES |  |
| bid_price_6 | integer | YES |  |
| bid_qty_6 | integer | YES |  |
| bid_price_7 | integer | YES |  |
| bid_qty_7 | integer | YES |  |
| bid_price_8 | integer | YES |  |
| bid_qty_8 | integer | YES |  |
| bid_price_9 | integer | YES |  |
| bid_qty_9 | integer | YES |  |
| bid_price_10 | integer | YES |  |
| bid_qty_10 | integer | YES |  |
| total_ask_qty | bigint | YES |  |
| total_bid_qty | bigint | YES |  |
| bid_ask_ratio | numeric | YES |  |
| spread_pct | numeric | YES |  |
| last_price | integer | YES |  |
| last_volume | integer | YES |  |
| accumulated_volume | bigint | YES |  |

### v4_pick_reasons (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| pick_date | character varying(8) | NO |  |
| desk_id | integer | NO |  |
| class_type | character varying(20) | NO |  |
| stock_code | character varying(10) | NO |  |
| stock_name | character varying(50) | YES |  |
| total_score | numeric | NO |  |
| score_detail | jsonb | NO |  |
| reason_summary | text | NO |  |
| market_regime | character varying(20) | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_position_extended (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| position_id | integer | NO |  |
| user_id | integer | NO | HAS_DEFAULT |
| desk_id | integer | NO |  |
| strategy_id | character varying(50) | NO | HAS_DEFAULT |
| signal_id | character varying(100) | YES |  |
| reservation_id | character varying(100) | YES |  |
| entry_reason | text | YES |  |
| universe_score_at_entry | double precision | YES |  |
| mood_score_at_entry | double precision | YES |  |
| regime_at_entry | character varying(50) | YES |  |
| bet_amount | bigint | YES |  |
| confidence_at_entry | character varying(20) | YES |  |
| exit_reason | character varying(50) | YES |  |
| exit_price | bigint | YES |  |
| realized_pnl | bigint | YES |  |
| realized_pnl_pct | double precision | YES |  |
| hold_days | integer | YES |  |
| stop_loss_pct | double precision | YES | HAS_DEFAULT |
| stop_loss_price | bigint | YES |  |
| take_profit_pct | double precision | YES | HAS_DEFAULT |
| take_profit_price | bigint | YES |  |
| trailing_activated | integer | YES | HAS_DEFAULT |
| trailing_high_price | bigint | YES |  |
| max_hold_days | integer | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |
| closed_at | timestamp with time zone | YES |  |

### v4_position_transfers (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| transfer_id | bigint | NO | HAS_DEFAULT |
| position_id | bigint | NO |  |
| from_desk_id | integer | NO |  |
| to_desk_id | integer | NO |  |
| transferred_qty | integer | NO |  |
| remaining_qty | integer | NO | HAS_DEFAULT |
| transfer_type | character varying(20) | NO |  |
| trigger_conditions | jsonb | YES |  |
| pnl_at_transfer | numeric | YES |  |
| transferred_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_positions (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | bigint | NO | HAS_DEFAULT |
| ticker | character varying(20) | NO |  |
| quantity | integer | NO |  |
| entry_price | bigint | NO |  |
| status | character varying(20) | NO | HAS_DEFAULT |
| desk_id | integer | NO | HAS_DEFAULT |
| peak_price | bigint | NO | HAS_DEFAULT |
| stop_loss_price | bigint | YES |  |
| trailing_pct | numeric | YES | HAS_DEFAULT |
| target_pct | numeric | YES | HAS_DEFAULT |
| max_hold_days | integer | YES | HAS_DEFAULT |
| entry_date | date | YES | HAS_DEFAULT |
| reservation_id | character varying(100) | YES |  |
| exit_reason | character varying(50) | YES |  |
| exit_price | bigint | YES |  |
| exited_at | timestamp with time zone | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |
| current_price | numeric | YES | HAS_DEFAULT |
| pnl_pct | numeric | YES | HAS_DEFAULT |
| price_updated_at | timestamp with time zone | YES |  |
| account_id | bigint | YES |  |
| card_id | bigint | YES |  |
| split_phase | integer | YES | HAS_DEFAULT |
| remaining_qty | integer | YES |  |
| original_desk_id | integer | YES |  |
| buy_phase | integer | YES | HAS_DEFAULT |
| signal_id | bigint | YES |  |

### v4_positions_backup_20260218 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | YES |  |
| user_id | bigint | YES |  |
| ticker | character varying(20) | YES |  |
| quantity | integer | YES |  |
| entry_price | bigint | YES |  |
| status | character varying(20) | YES |  |
| desk_id | integer | YES |  |
| peak_price | bigint | YES |  |
| stop_loss_price | bigint | YES |  |
| trailing_pct | numeric | YES |  |
| target_pct | numeric | YES |  |
| max_hold_days | integer | YES |  |
| entry_date | date | YES |  |
| reservation_id | character varying(100) | YES |  |
| exit_reason | character varying(50) | YES |  |
| exit_price | bigint | YES |  |
| exited_at | timestamp with time zone | YES |  |
| created_at | timestamp with time zone | YES |  |
| updated_at | timestamp with time zone | YES |  |

### v4_program_trades (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| trade_date | date | NO |  |
| program_buy_amount | bigint | YES | HAS_DEFAULT |
| program_sell_amount | bigint | YES | HAS_DEFAULT |
| program_net_amount | bigint | YES | HAS_DEFAULT |
| arbitrage_buy_amount | bigint | YES | HAS_DEFAULT |
| arbitrage_sell_amount | bigint | YES | HAS_DEFAULT |
| non_arbitrage_buy_amount | bigint | YES | HAS_DEFAULT |
| non_arbitrage_sell_amount | bigint | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_reports (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| report_type | character varying(20) | NO |  |
| report_date | date | NO |  |
| total_trades | integer | YES | HAS_DEFAULT |
| winning_trades | integer | YES | HAS_DEFAULT |
| losing_trades | integer | YES | HAS_DEFAULT |
| total_profit | numeric | YES | HAS_DEFAULT |
| total_loss | numeric | YES | HAS_DEFAULT |
| net_profit | numeric | YES | HAS_DEFAULT |
| win_rate | numeric | YES |  |
| profit_factor | numeric | YES |  |
| max_drawdown | numeric | YES |  |
| portfolio_value | bigint | YES |  |
| cash_balance | bigint | YES |  |
| daily_return | numeric | YES |  |
| cumulative_return | numeric | YES |  |
| report_data | jsonb | YES |  |
| html_content | text | YES |  |
| sent_channels | ARRAY | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_reservations (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | character varying(64) | NO |  |
| order_request_id | bigint | YES |  |
| user_id | bigint | NO |  |
| desk_id | integer | NO |  |
| ticker | character varying(20) | NO |  |
| amount | bigint | NO |  |
| status | character varying(20) | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| expires_at | timestamp with time zone | NO |  |
| order_no | character varying(50) | YES |  |
| reason | text | YES |  |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |
| strategy_id | character varying(20) | YES |  |
| signal_id | character varying(100) | YES |  |

### v4_scalping_signals (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(20) | NO |  |
| signal_time | timestamp without time zone | NO |  |
| signal_type | character varying(30) | NO |  |
| direction | character varying(4) | NO |  |
| current_price | integer | YES |  |
| vwap_price | numeric | YES |  |
| open_price | integer | YES |  |
| prev_close | integer | YES |  |
| gap_pct | numeric | YES |  |
| atr_breakout_pct | numeric | YES |  |
| volume_ratio | numeric | YES |  |
| volume_5min | bigint | YES |  |
| bid_ask_ratio | numeric | YES |  |
| spread_pct | numeric | YES |  |
| signal_strength | numeric | YES |  |
| status | character varying(20) | YES | HAS_DEFAULT |
| executed_at | timestamp without time zone | YES |  |

### v4_scalping_universe (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| market | character varying(10) | YES |  |
| avg_trade_value_20d | bigint | YES |  |
| avg_atr_pct_20d | numeric | YES |  |
| avg_volume_20d | bigint | YES |  |
| close_price | integer | YES |  |
| market_cap | bigint | YES |  |
| is_active | boolean | YES | HAS_DEFAULT |
| created_date | date | NO |  |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### v4_scoring_weights (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| effective_from | date | NO |  |
| supply_demand_w | numeric | YES |  |
| sector_momentum_w | numeric | YES |  |
| theme_w | numeric | YES |  |
| volume_w | numeric | YES |  |
| technical_w | numeric | YES |  |
| source | character varying(20) | YES |  |
| validation_score | numeric | YES |  |
| note | text | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES |  |

### v4_sector_daily (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| sector_code | character varying(20) | NO |  |
| sector_name | character varying(100) | YES |  |
| trade_date | date | NO |  |
| open_index | numeric | YES |  |
| high_index | numeric | YES |  |
| low_index | numeric | YES |  |
| close_index | numeric | YES |  |
| change_rate | numeric | YES |  |
| volume | bigint | YES | HAS_DEFAULT |
| trade_amount | bigint | YES | HAS_DEFAULT |
| change_rate_5d | numeric | YES |  |
| change_rate_20d | numeric | YES |  |
| sector_rank | integer | YES |  |
| collected_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_sector_price (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| sector_code | character varying(10) | NO |  |
| sector_name | character varying(50) | YES |  |
| trade_date | date | NO |  |
| close_price | numeric | YES |  |
| change_rate | numeric | YES |  |
| volume | bigint | YES |  |
| trade_amount | bigint | YES |  |
| advance_count | integer | YES |  |
| decline_count | integer | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_signals (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| signal_id | bigint | NO | HAS_DEFAULT |
| desk_id | integer | NO |  |
| stock_code | character varying(10) | NO |  |
| stock_name | character varying(50) | YES |  |
| signal_date | date | NO |  |
| signal_type | character varying(10) | NO |  |
| signal_strength | integer | YES |  |
| expected_return | numeric | YES |  |
| expected_risk | numeric | YES |  |
| risk_reward | numeric | YES |  |
| entry_price | numeric | YES |  |
| target_price | numeric | YES |  |
| stop_loss_price | numeric | YES |  |
| holding_days | character varying(20) | YES |  |
| conditions_met | jsonb | YES |  |
| explanation | text | YES |  |
| indicator_data | jsonb | YES |  |
| risk_factors | jsonb | YES |  |
| status | character varying(20) | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| result_position_id | integer | YES |  |
| result_status | character varying(20) | YES | HAS_DEFAULT |
| source | character varying(20) | YES |  |
| strategy_card_id | integer | YES |  |
| strategy_version | integer | YES | HAS_DEFAULT |

### v4_stage_transitions (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| transition_date | date | NO |  |
| from_stage | integer | NO |  |
| to_stage | integer | NO |  |
| total_asset | numeric | NO |  |
| old_allocation | jsonb | NO |  |
| new_allocation | jsonb | NO |  |
| reason | text | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_stock_sector (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| stock_code | character varying(10) | NO |  |
| sector_code | character varying(10) | NO |  |
| sector_name | character varying(50) | NO |  |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_strategy_performance (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| perf_id | integer | NO | HAS_DEFAULT |
| card_id | integer | NO |  |
| desk_id | integer | NO |  |
| calc_date | date | NO |  |
| period_type | character varying(10) | NO | HAS_DEFAULT |
| total_trades | integer | YES | HAS_DEFAULT |
| win_trades | integer | YES | HAS_DEFAULT |
| loss_trades | integer | YES | HAS_DEFAULT |
| total_pnl | numeric | YES | HAS_DEFAULT |
| total_pnl_pct | numeric | YES | HAS_DEFAULT |
| max_drawdown | numeric | YES | HAS_DEFAULT |
| sharpe_ratio | numeric | YES | HAS_DEFAULT |
| profit_factor | numeric | YES | HAS_DEFAULT |
| avg_hold_days | numeric | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | NO | HAS_DEFAULT |

### v4_strategy_registry (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| strategy_code | character varying(50) | NO |  |
| name | character varying(100) | NO |  |
| category | character varying(30) | NO |  |
| source_strategy_id | integer | YES |  |
| parameters | jsonb | YES | HAS_DEFAULT |
| entry_logic | text | YES |  |
| exit_logic | text | YES |  |
| is_active | boolean | YES | HAS_DEFAULT |
| performance_score | numeric | YES | HAS_DEFAULT |
| total_return_pct | numeric | YES | HAS_DEFAULT |
| win_rate | numeric | YES | HAS_DEFAULT |
| max_drawdown_pct | numeric | YES | HAS_DEFAULT |
| trade_count | integer | YES | HAS_DEFAULT |
| last_backtest_at | timestamp with time zone | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_system_heartbeat (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| state | character varying(20) | YES |  |
| cycle_count | integer | YES |  |
| last_cycle_duration_ms | integer | YES |  |
| open_positions | integer | YES |  |
| data_quality | character varying(10) | YES |  |
| error_count | integer | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| previous_state | character varying(20) | YES |  |
| transition_reason | text | YES |  |
| module_status | jsonb | YES | HAS_DEFAULT |
| cycle_id | integer | YES | HAS_DEFAULT |
| order_success_count | integer | YES | HAS_DEFAULT |
| order_fail_count | integer | YES | HAS_DEFAULT |
| order_reject_count | integer | YES | HAS_DEFAULT |
| max_price_staleness_ms | integer | YES | HAS_DEFAULT |
| active_positions_count | integer | YES | HAS_DEFAULT |
| available_capital | bigint | YES | HAS_DEFAULT |
| error_message | text | YES |  |

### v4_system_state_log (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| state | character varying(20) | NO |  |
| previous_state | character varying(20) | YES |  |
| transition_reason | text | YES |  |
| module_status | json | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES |  |

### v4_theme_activity_daily (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| date | date | NO |  |
| theme_code | character varying(20) | NO |  |
| activity_score | numeric | YES |  |
| status | character varying(10) | YES |  |
| avg_volume_ratio | numeric | YES |  |
| avg_return_pct | numeric | YES |  |
| supply_positive_ratio | numeric | YES |  |
| stock_count | integer | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_theme_daily (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| theme_code | character varying(20) | NO |  |
| trade_date | date | NO |  |
| theme_change_rate | numeric | YES |  |
| theme_volume | bigint | YES | HAS_DEFAULT |
| theme_trade_amount | bigint | YES | HAS_DEFAULT |
| leader_stock_code | character varying(12) | YES |  |
| leader_change_rate | numeric | YES |  |
| leader_volume | bigint | YES | HAS_DEFAULT |
| consecutive_up_days | integer | YES | HAS_DEFAULT |
| stock_count | integer | YES | HAS_DEFAULT |
| up_stock_count | integer | YES | HAS_DEFAULT |
| collected_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_theme_detail (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| theme_code | character varying(20) | NO |  |
| theme_name | character varying(100) | YES |  |
| detail | jsonb | YES |  |
| collected_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_theme_master (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| theme_code | character varying(20) | NO |  |
| theme_name | character varying(100) | NO |  |
| description | text | YES |  |
| is_active | boolean | YES | HAS_DEFAULT |
| first_seen_date | date | YES |  |
| last_updated | timestamp with time zone | YES | HAS_DEFAULT |

### v4_theme_stock (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| theme_code | character varying(20) | NO |  |
| stock_code | character varying(12) | NO |  |
| stock_name | character varying(100) | YES |  |
| is_leader | boolean | YES | HAS_DEFAULT |
| mapped_date | date | NO |  |
| collected_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_theme_stock_mapping (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| theme_code | character varying(20) | NO |  |
| theme_name | character varying(50) | YES |  |
| ticker | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| is_leader | boolean | NO |  |
| relevance | integer | NO |  |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_tick_data (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| tick_time | timestamp with time zone | NO |  |
| price | integer | NO |  |
| volume | integer | NO |  |
| cum_volume | bigint | YES |  |
| buy_sell | character(1) | YES |  |
| strength | numeric | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_trade_analysis (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| position_id | integer | NO |  |
| ticker | character varying(20) | YES |  |
| entry_date | date | YES |  |
| entry_time | time without time zone | YES |  |
| entry_price | integer | YES |  |
| universe_score | numeric | YES |  |
| supply_score | numeric | YES |  |
| sector_score | numeric | YES |  |
| theme_score | numeric | YES |  |
| volume_score | numeric | YES |  |
| technical_score | numeric | YES |  |
| stock_class | character varying(20) | YES |  |
| class_confidence | character varying(20) | YES |  |
| desk_id | integer | YES |  |
| strategy_id | character varying(20) | YES |  |
| market_mood_score | integer | YES |  |
| market_regime | character varying(30) | YES |  |
| regime_score | numeric | YES |  |
| bet_confidence | character varying(10) | YES |  |
| bet_size_pct | numeric | YES |  |
| bet_amount | bigint | YES |  |
| data_quality | character varying(10) | YES |  |
| time_reliability | character varying(20) | YES |  |
| max_profit_pct | numeric | YES |  |
| max_profit_date | date | YES |  |
| max_loss_pct | numeric | YES |  |
| max_loss_date | date | YES |  |
| hold_days | integer | YES |  |
| supply_change | character varying(20) | YES |  |
| regime_changed | boolean | NO |  |
| mood_min_during | numeric | YES |  |
| class_transferred | boolean | NO |  |
| transfer_log_id | integer | YES |  |
| exit_date | date | YES |  |
| exit_time | time without time zone | YES |  |
| exit_price | integer | YES |  |
| exit_reason | character varying(30) | YES |  |
| realized_pnl | bigint | YES |  |
| realized_pnl_pct | numeric | YES |  |
| slippage_pct | numeric | YES |  |
| commission | bigint | YES |  |
| price_after_1h | integer | YES |  |
| price_after_1d | integer | YES |  |
| return_after_1h | numeric | YES |  |
| return_after_1d | numeric | YES |  |
| early_exit | boolean | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |

### v4_trade_executions (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | bigint | YES |  |
| account_id | bigint | YES |  |
| strategy_id | integer | YES |  |
| stock_code | character varying(20) | NO |  |
| stock_name | character varying(100) | YES |  |
| order_type | character varying(10) | NO |  |
| order_method | character varying(20) | YES | HAS_DEFAULT |
| quantity | integer | NO |  |
| price | numeric | YES |  |
| executed_price | numeric | YES |  |
| executed_quantity | integer | YES | HAS_DEFAULT |
| status | character varying(20) | YES | HAS_DEFAULT |
| broker_type | character varying(20) | YES |  |
| broker_order_id | character varying(100) | YES |  |
| error_message | text | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| executed_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### v4_trade_schedules (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | bigint | YES |  |
| strategy_id | integer | NO |  |
| account_id | bigint | YES |  |
| is_active | boolean | YES | HAS_DEFAULT |
| run_interval | character varying(20) | YES | HAS_DEFAULT |
| market_open_only | boolean | YES | HAS_DEFAULT |
| invest_amount | numeric | YES |  |
| max_stocks | integer | YES | HAS_DEFAULT |
| max_per_stock_pct | numeric | YES | HAS_DEFAULT |
| stop_loss_pct | numeric | YES | HAS_DEFAULT |
| take_profit_pct | numeric | YES | HAS_DEFAULT |
| last_run_at | timestamp without time zone | YES |  |
| next_run_at | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

### v4_trade_strength_history (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| stock_code | character varying(10) | NO |  |
| recorded_at | timestamp with time zone | NO |  |
| strength | numeric | YES |  |
| buy_count | integer | YES |  |
| sell_count | integer | YES |  |
| buy_amount | bigint | YES |  |
| sell_amount | bigint | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_trades (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| desk_id | integer | NO |  |
| class_name | character varying(20) | NO |  |
| stock_code | character varying(10) | NO |  |
| stock_name | character varying(50) | YES |  |
| side | character varying(4) | NO |  |
| price | integer | NO |  |
| qty | integer | NO |  |
| amount | bigint | NO |  |
| order_no | character varying(20) | YES |  |
| strategy_name | character varying(50) | YES |  |
| signal_confidence | numeric | YES |  |
| trade_date | timestamp with time zone | NO |  |
| position_id | integer | YES |  |
| pnl_amount | bigint | YES |  |
| pnl_pct | numeric | YES |  |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| user_id | bigint | YES |  |
| account_id | bigint | YES |  |
| card_id | bigint | YES |  |

### v4_trades_backup_20260218 (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | YES |  |
| desk_id | integer | YES |  |
| class_name | character varying(20) | YES |  |
| stock_code | character varying(10) | YES |  |
| stock_name | character varying(50) | YES |  |
| side | character varying(4) | YES |  |
| price | integer | YES |  |
| qty | integer | YES |  |
| amount | bigint | YES |  |
| order_no | character varying(20) | YES |  |
| strategy_name | character varying(50) | YES |  |
| signal_confidence | numeric | YES |  |
| trade_date | timestamp with time zone | YES |  |
| position_id | integer | YES |  |
| pnl_amount | bigint | YES |  |
| pnl_pct | numeric | YES |  |
| created_at | timestamp with time zone | YES |  |

### v4_universe_version (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| version_name | character varying(80) | NO |  |
| effective_from | date | NO |  |
| effective_to | date | YES |  |
| source | character varying(40) | NO | HAS_DEFAULT |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |
| stock_count | integer | NO | HAS_DEFAULT |
| criteria_json | jsonb | YES |  |
| note | text | YES |  |
| is_active | boolean | NO | HAS_DEFAULT |
| created_by | character varying(40) | YES |  |
| approved_at | timestamp with time zone | YES |  |
| checksum_sha256 | character varying(64) | YES |  |
| published_at | timestamp with time zone | YES |  |
| config_snapshot | jsonb | YES |  |
| row_count | integer | NO | HAS_DEFAULT |

### v4_user_settings (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | bigint | NO |  |
| telegram_enabled | boolean | YES | HAS_DEFAULT |
| telegram_chat_id | character varying(100) | YES |  |
| email_notifications | boolean | YES | HAS_DEFAULT |
| trade_alert | boolean | YES | HAS_DEFAULT |
| daily_report | boolean | YES | HAS_DEFAULT |
| error_alert | boolean | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_user_strategies (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| user_id | integer | NO |  |
| strategy_name | character varying(100) | NO |  |
| desk | character varying(20) | YES |  |
| is_active | boolean | YES | HAS_DEFAULT |
| parameters | jsonb | YES |  |
| allocation_pct | numeric | YES | HAS_DEFAULT |
| created_at | timestamp with time zone | YES | HAS_DEFAULT |
| updated_at | timestamp with time zone | YES | HAS_DEFAULT |

### v4_users (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| user_id | bigint | NO | HAS_DEFAULT |
| email | character varying(255) | NO |  |
| nickname | character varying(50) | NO |  |
| hashed_password | character varying(255) | NO | 🔒 암호화/민감 |
| tier | character varying(20) | NO | HAS_DEFAULT |
| is_active | boolean | NO | HAS_DEFAULT |
| last_login_at | timestamp with time zone | YES |  |
| created_at | timestamp with time zone | NO | HAS_DEFAULT |
| updated_at | timestamp with time zone | NO | HAS_DEFAULT |
| phone | character varying(50) | YES |  |

### v4_vkospi_daily (V4.1)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | bigint | NO | HAS_DEFAULT |
| date | character varying(8) | NO |  |
| open | real | YES |  |
| high | real | YES |  |
| low | real | YES |  |
| close | real | NO |  |
| change_rate | real | YES |  |
| source | character varying(20) | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |

### virtual_trades (COMMON)

| 컬럼 | 타입 | Nullable | 비고 |
|------|------|----------|------|
| id | integer | NO | HAS_DEFAULT |
| timestamp | timestamp without time zone | NO |  |
| account_email | character varying(255) | NO |  |
| strategy_id | character varying(50) | NO |  |
| strategy_name | character varying(255) | NO |  |
| ticker | character varying(20) | NO |  |
| signal | character varying(10) | NO |  |
| price | real | NO |  |
| quantity | integer | NO |  |
| position_size | real | NO |  |
| filled_price | real | NO |  |
| filled_quantity | integer | NO |  |
| entry_price | real | YES |  |
| exit_price | real | YES |  |
| realized_pnl | real | YES | HAS_DEFAULT |
| created_at | timestamp without time zone | YES | HAS_DEFAULT |
| updated_at | timestamp without time zone | YES | HAS_DEFAULT |

## 3. 무결성 기준값 (2026-02-23)

| 항목 | 값 |
|------|---|
| strategy_cards | 62건 (기준) |
| v4_positions OPEN | 5건 |
| go100_strategy_cards | 확인 필요 |

## 4. 갱신 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-23 | 최초 스키마 문서 생성 (CUR-DB-SCHEMA-DOC-001) |