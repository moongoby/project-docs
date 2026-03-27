# DB 스키마 카탈로그 -- KIS AutoTrade (GO100 + V4.1 통합)

> 자동 생성: 2026-03-28 06:00 KST
> 생성기: scripts/generate_db_catalog.py
> DB: PostgreSQL kisautotrade @ localhost (peer auth)
> 총 테이블: 320개 | 뷰: 9개 | 합계: 329개

---

## 범례

| 프로젝트 | 테이블 수 | 설명 |
|---------|----------|------|
| [V4.1] | 170 | KIS AutoTrade V4.1 전용 |
| [GO100] | 82 | GO100 AI Agent 전용 |
| [공통] | 68 | 양 프로젝트 공유 |

| 카테고리 | 테이블 수 | 설명 |
|---------|----------|------|
| MARKET | 30 | 시세/가격 데이터 |
| INVESTOR | 8 | 수급/투자자 데이터 |
| STRATEGY | 25 | 전략/조건/카드/시그널 |
| POSITION | 56 | 포지션/거래/주문 |
| RISK | 6 | 리스크/시장 레짐 |
| NEWS | 1 | 뉴스/공시 |
| AI | 28 | AI/ML 모델/백테스트/캘리브레이션 |
| INFRA | 55 | 계정/설정/시스템/알림 |
| GLOBAL | 1 | 글로벌 시장 지표 |
| UNIVERSE | 28 | 종목 유니버스/섹터/테마/펀더멘탈 |
| ETC | 82 | 기타 (갭분석/메모리/데스크/포트폴리오 등) |

---

## 1. 테이블 총괄표

| # | 테이블 | 프로젝트 | 카테고리 | 행 수 | 크기 | 최신 데이터 |
|---|--------|---------|---------|-------|------|------------|
| 1 | `go100_backtest_runs` | [GO100] | AI | 20 | 200 kB | 2026-01-15 |
| 2 | `go100_calibration_params` | [GO100] | AI | 12 | 48 kB | 2026-02-26 |
| 3 | `go100_fit_analysis` | [GO100] | AI | 40 | 88 kB | 2026-02-21 |
| 4 | `go100_gap_calibrator` | [GO100] | AI | 110,735 | 33 MB | 2026-03-03 |
| 5 | `go100_optimization_runs` | [GO100] | AI | 0 | 48 kB | - |
| 6 | `go100_portfolio_optimizations` | [GO100] | AI | 17 | 64 kB | 2026-03-04 |
| 7 | `v4_backtest_daily` | [V4.1] | AI | 6,170 | 3368 kB | 2026-03-06 |
| 8 | `v4_backtest_desk_detail` | [V4.1] | AI | 12 | 72 kB | - |
| 9 | `v4_backtest_equity` | [V4.1] | AI | 175 | 80 kB | - |
| 10 | `v4_backtest_profile` | [V4.1] | AI | 0 | 16 kB | - |
| 11 | `v4_backtest_results` | [V4.1] | AI | 60 | 808 kB | 2026-02-19 |
| 12 | `v4_backtest_results_desk_run` | [V4.1] | AI | 39 | 56 kB | 2025-11-01 |
| 13 | `v4_backtest_runs` | [V4.1] | AI | 5 | 112 kB | 2026-01-24 |
| 14 | `v4_backtest_runs_legacy` | [V4.1] | AI | 3 | 72 kB | 2026-02-18 |
| 15 | `v4_backtest_sessions` | [V4.1] | AI | 164 | 960 kB | 2026-02-25 |
| 16 | `v4_backtest_strategies` | [V4.1] | AI | 0 | 24 kB | - |
| 17 | `v4_backtest_summary` | [V4.1] | AI | 132 | 136 kB | 2026-03-07 |
| 18 | `v4_backtest_v2_sessions` | [V4.1] | AI | 0 | 40 kB | - |
| 19 | `v4_bt_discoveries` | [V4.1] | AI | 6,931 | 2944 kB | 2026-02-20 |
| 20 | `v4_bt_discovery_log` | [V4.1] | AI | 776,636 | 518 MB | 2026-02-26 |
| 21 | `v4_bt_sessions` | [V4.1] | AI | 67 | 256 kB | 2026-02-25 |
| 22 | `v4_bt_versions` | [V4.1] | AI | 0 | 24 kB | - |
| 23 | `v4_desk_backtest_results` | [V4.1] | AI | 102 | 176 kB | 2025-12-19 |
| 24 | `v4_optimization_results` | [V4.1] | AI | 1,996 | 856 kB | 2026-03-19 |
| 25 | `backtest_params` | [공통] | AI | 341 | 120 kB | 2026-02-04 |
| 26 | `backtest_results` | [공통] | AI | 3 | 48 kB | 2024-01-02 |
| 27 | `backtests` | [공통] | AI | 0 | 112 kB | - |
| 28 | `scalping_features_daily` | [공통] | AI | 45 | 88 kB | 2026-02-03 |
| 29 | `go100_agent_experience_log` | [GO100] | ETC | 1 | 88 kB | 2026-02-27 |
| 30 | `go100_agent_performance` | [GO100] | ETC | 81 | 104 kB | 2026-03-07 |
| 31 | `go100_agent_self_review` | [GO100] | ETC | 2 | 80 kB | 2026-02-16 |
| 32 | `go100_ai_predictions` | [GO100] | ETC | 506 | 504 kB | 2026-03-05 |
| 33 | `go100_commander_decisions` | [GO100] | ETC | 0 | 40 kB | - |
| 34 | `go100_data_integrity_log` | [GO100] | ETC | 134,117 | 32 MB | 2026-03-27 |
| 35 | `go100_debate_log` | [GO100] | ETC | 5 | 64 kB | 2026-03-04 |
| 36 | `go100_derivatives_daily` | [GO100] | ETC | 0 | 16 kB | - |
| 37 | `go100_desk_allocation` | [GO100] | ETC | 2 | 64 kB | 2026-02-21 |
| 38 | `go100_episodic_memory` | [GO100] | ETC | 1 | 96 kB | 2026-02-27 |
| 39 | `go100_error_log` | [GO100] | ETC | 249 | 584 kB | 2026-03-23 |
| 40 | `go100_events` | [GO100] | ETC | 25 | 96 kB | 2026-02-27 |
| 41 | `go100_evolution_loops` | [GO100] | ETC | 0 | 16 kB | - |
| 42 | `go100_experience_log` | [GO100] | ETC | 0 | 40 kB | - |
| 43 | `go100_gap_analysis` | [GO100] | ETC | 0 | 16 kB | - |
| 44 | `go100_goals` | [GO100] | ETC | 6 | 72 kB | 2026-02-26 |
| 45 | `go100_live_daily_summary` | [GO100] | ETC | 0 | 16 kB | - |
| 46 | `go100_paper_archive` | [GO100] | ETC | 0 | 48 kB | - |
| 47 | `go100_paper_snapshots` | [GO100] | ETC | 380 | 120 kB | 2026-03-27 |
| 48 | `go100_portfolio_allocations` | [GO100] | ETC | 0 | 32 kB | - |
| 49 | `go100_portfolio_snapshots` | [GO100] | ETC | 96 | 112 kB | 2026-03-27 |
| 50 | `go100_portfolios` | [GO100] | ETC | 6 | 88 kB | 2026-03-06 |
| 51 | `go100_program_trading_daily` | [GO100] | ETC | 0 | 16 kB | - |
| 52 | `go100_research_iterations` | [GO100] | ETC | 3 | 64 kB | 2026-03-06 |
| 53 | `go100_short_selling_daily` | [GO100] | ETC | 0 | 16 kB | - |
| 54 | `go100_stock_profiles` | [GO100] | ETC | 0 | 16 kB | - |
| 55 | `go100_trading_cost_params` | [GO100] | ETC | 3 | 40 kB | 2026-02-26 |
| 56 | `v4_bet_history` | [V4.1] | ETC | 0 | 8192 bytes | - |
| 57 | `v4_compound_growth_daily` | [V4.1] | ETC | 0 | 24 kB | - |
| 58 | `v4_daily_portfolio` | [V4.1] | ETC | 35 | 80 kB | 2026-03-27 |
| 59 | `v4_desk1_candidates` | [V4.1] | ETC | 50 | 56 kB | 2026-03-27 |
| 60 | `v4_desk2_candidates` | [V4.1] | ETC | 2,348 | 888 kB | 2026-03-27 |
| 61 | `v4_desk2_daily_summary` | [V4.1] | ETC | 1 | 40 kB | 2026-03-03 |
| 62 | `v4_desk3_explosion_log` | [V4.1] | ETC | 0 | 16 kB | - |
| 63 | `v4_desk3_explosion_watch` | [V4.1] | ETC | 0 | 16 kB | - |
| 64 | `v4_desk3_pool` | [V4.1] | ETC | 1,213 | 776 kB | 2026-03-27 |
| 65 | `v4_desk4_harvest_log` | [V4.1] | ETC | 0 | 16 kB | - |
| 66 | `v4_desk4_harvest_pool` | [V4.1] | ETC | 0 | 16 kB | - |
| 67 | `v4_desk4_watchlist` | [V4.1] | ETC | 38 | 88 kB | 2026-03-23 |
| 68 | `v4_desk5_watchlist` | [V4.1] | ETC | 59 | 104 kB | 2026-03-27 |
| 69 | `v4_desk5_weekly_review` | [V4.1] | ETC | 0 | 16 kB | - |
| 70 | `v4_desk_fund` | [V4.1] | ETC | 5 | 120 kB | 2026-03-27 |
| 71 | `v4_desk_portfolio_summary` | [V4.1] | ETC | 0 | 16 kB | - |
| 72 | `v4_desk_promotion_log` | [V4.1] | ETC | 3 | 48 kB | 2026-03-19 |
| 73 | `v4_evolution_candidates` | [V4.1] | ETC | 0 | 32 kB | - |
| 74 | `v4_excluded_stocks` | [V4.1] | ETC | 248 | 64 kB | 2026-03-18 |
| 75 | `v4_fund_lending` | [V4.1] | ETC | 63 | 88 kB | 2026-03-26 |
| 76 | `v4_fund_pool_snapshot` | [V4.1] | ETC | 1 | 56 kB | 2026-02-23 |
| 77 | `v4_hav_drift_events` | [V4.1] | ETC | 0 | 16 kB | - |
| 78 | `v4_hav_hypotheses` | [V4.1] | ETC | 285 | 33 MB | 2026-03-28 |
| 79 | `v4_hav_validation_runs` | [V4.1] | ETC | 0 | 24 kB | - |
| 80 | `v4_macro_daily` | [V4.1] | ETC | 746 | 424 kB | 2026-03-27 |
| 81 | `v4_meta_rules` | [V4.1] | ETC | 214 | 752 kB | 2026-03-27 |
| 82 | `v4_minute_collect_progress` | [V4.1] | ETC | 840 | 3960 kB | 2026-03-26 |
| 83 | `v4_node_history` | [V4.1] | ETC | 33,100 | 4496 kB | 2026-02-27 |
| 84 | `v4_node_realtime` | [V4.1] | ETC | 12 | 136 kB | - |
| 85 | `v4_peak_exits` | [V4.1] | ETC | 12 | 40 kB | 2026-03-19 |
| 86 | `v4_pick_reasons` | [V4.1] | ETC | 2,265 | 1720 kB | 2026-03-19 |
| 87 | `v4_pyramid_chain` | [V4.1] | ETC | 1 | 72 kB | 2026-03-05 |
| 88 | `v4_pyramid_chain_log` | [V4.1] | ETC | 5 | 40 kB | 2026-03-05 |
| 89 | `v4_reservations` | [V4.1] | ETC | 2 | 128 kB | 2026-02-13 |
| 90 | `v4_smart_entries` | [V4.1] | ETC | 12 | 72 kB | 2026-03-19 |
| 91 | `v4_stage_history` | [V4.1] | ETC | 0 | 32 kB | - |
| 92 | `v4_stage_transitions` | [V4.1] | ETC | 4 | 64 kB | 2026-03-05 |
| 93 | `v4_top20_history` | [V4.1] | ETC | 0 | 24 kB | - |
| 94 | `v4_trajectory_labels` | [V4.1] | ETC | 58 | 80 kB | 2026-02-27 |
| 95 | `v4_vi_history` | [V4.1] | ETC | 0 | 16 kB | - |
| 96 | `v4_vi_occurrences` | [V4.1] | ETC | 319 | 96 kB | 2026-02-25 |
| 97 | `v4_virtual_monitor_snapshots` | [V4.1] | ETC | 1,804 | 416 kB | 2026-03-23 |
| 98 | `v4_volume_retention` | [V4.1] | ETC | 9,170 | 3656 kB | 2026-03-18 |
| 99 | `daily_trading_stats` | [공통] | ETC | 1 | 88 kB | 2026-01-29 |
| 100 | `daily_trading_summary` | [공통] | ETC | 0 | 32 kB | - |
| 101 | `data_crypto_daily` | [공통] | ETC | 860 | 248 kB | 2026-03-26 |
| 102 | `data_fx_daily` | [공통] | ETC | 863 | 336 kB | 2026-03-27 |
| 103 | `desk5_seeds` | [공통] | ETC | 0 | 80 kB | - |
| 104 | `live_trading_results` | [공통] | ETC | 7,986 | 1688 kB | 2026-02-06 |
| 105 | `portfolios` | [공통] | ETC | 5 | 56 kB | 2026-01-25 |
| 106 | `stock_lifecycle` | [공통] | ETC | 3,428 | 1384 kB | 2026-03-16 |
| 107 | `stock_price_snapshot` | [공통] | ETC | 3,588 | 66 MB | 2026-03-27 |
| 108 | `strategies` | [공통] | ETC | 51 | 72 kB | 2026-02-07 |
| 109 | `trading_events` | [공통] | ETC | 9 | 96 kB | 2026-01-27 |
| 110 | `waverider_performance` | [공통] | ETC | 0 | 16 kB | - |
| 111 | `go100_global_market` | [GO100] | GLOBAL | 318 | 232 kB | 2026-03-26 |
| 112 | `go100_account_reconciliation` | [GO100] | INFRA | 0 | 32 kB | - |
| 113 | `go100_agent_reports` | [GO100] | INFRA | 124 | 248 kB | 2026-03-07 |
| 114 | `go100_alerts` | [GO100] | INFRA | 3,698 | 1656 kB | 2026-03-27 |
| 115 | `go100_daily_briefings` | [GO100] | INFRA | 23 | 360 kB | 2026-03-27 |
| 116 | `go100_live_trading_config` | [GO100] | INFRA | 1 | 40 kB | 2026-03-03 |
| 117 | `go100_notification_settings` | [GO100] | INFRA | 2 | 72 kB | 2026-03-03 |
| 118 | `go100_notifications` | [GO100] | INFRA | 20 | 160 kB | 2026-02-27 |
| 119 | `go100_paper_accounts` | [GO100] | INFRA | 190 | 128 kB | 2026-03-26 |
| 120 | `go100_paper_trading_sessions` | [GO100] | INFRA | 25 | 96 kB | 2026-03-26 |
| 121 | `go100_pending_configs` | [GO100] | INFRA | 0 | 24 kB | - |
| 122 | `go100_push_subscriptions` | [GO100] | INFRA | 2 | 80 kB | 2026-02-24 |
| 123 | `go100_reports` | [GO100] | INFRA | 1,139 | 424 kB | 2026-03-28 |
| 124 | `go100_usage_logs` | [GO100] | INFRA | 124 | 88 kB | 2026-03-03 |
| 125 | `go100_user_memory` | [GO100] | INFRA | 1,620 | 3664 kB | 2026-03-27 |
| 126 | `go100_user_preferences` | [GO100] | INFRA | 1 | 64 kB | 2026-02-27 |
| 127 | `go100_user_profile` | [GO100] | INFRA | 1 | 48 kB | 2026-02-26 |
| 128 | `go100_user_profiles` | [GO100] | INFRA | 0 | 24 kB | - |
| 129 | `v4_account_config` | [V4.1] | INFRA | 1 | 64 kB | 2026-02-13 |
| 130 | `v4_account_holdings` | [V4.1] | INFRA | 793,771 | 218 MB | 2026-03-27 |
| 131 | `v4_account_sync_log` | [V4.1] | INFRA | 135,213 | 29 MB | 2026-03-27 |
| 132 | `v4_alerts` | [V4.1] | INFRA | 1,005 | 632 kB | 2026-03-27 |
| 133 | `v4_api_error_log` | [V4.1] | INFRA | 0 | 24 kB | - |
| 134 | `v4_api_tokens` | [V4.1] | INFRA | 1 | 48 kB | 2026-03-04 |
| 135 | `v4_chat_messages` | [V4.1] | INFRA | 211 | 248 kB | 2026-03-22 |
| 136 | `v4_chat_sessions` | [V4.1] | INFRA | 42 | 72 kB | 2026-03-22 |
| 137 | `v4_credit_balance` | [V4.1] | INFRA | 558 | 288 kB | 2026-02-26 |
| 138 | `v4_daily_reports` | [V4.1] | INFRA | 37 | 144 kB | 2026-03-27 |
| 139 | `v4_desk_config` | [V4.1] | INFRA | 5 | 48 kB | 2026-03-23 |
| 140 | `v4_llm_usage` | [V4.1] | INFRA | 0 | 24 kB | - |
| 141 | `v4_migration_history` | [V4.1] | INFRA | 2 | 80 kB | 2026-02-13 |
| 142 | `v4_notification_channel_config` | [V4.1] | INFRA | 0 | 16 kB | - |
| 143 | `v4_notification_settings` | [V4.1] | INFRA | 3 | 72 kB | 2026-02-24 |
| 144 | `v4_notifications` | [V4.1] | INFRA | 8 | 112 kB | 2026-03-04 |
| 145 | `v4_reports` | [V4.1] | INFRA | 0 | 32 kB | - |
| 146 | `v4_stage_config` | [V4.1] | INFRA | 4 | 32 kB | 2026-03-05 |
| 147 | `v4_system_heartbeat` | [V4.1] | INFRA | 2,098,766 | 888 MB | 2026-03-27 |
| 148 | `v4_system_state_log` | [V4.1] | INFRA | 0 | 16 kB | - |
| 149 | `v4_user_settings` | [V4.1] | INFRA | 0 | 24 kB | - |
| 150 | `v4_user_strategies` | [V4.1] | INFRA | 0 | 32 kB | - |
| 151 | `v4_users` | [V4.1] | INFRA | 9 | 96 kB | 2026-03-22 |
| 152 | `account_rate_quotas` | [공통] | INFRA | 8 | 72 kB | 2026-03-27 |
| 153 | `account_snapshots` | [공통] | INFRA | 470 | 104 kB | 2026-03-03 |
| 154 | `accounts` | [공통] | INFRA | 8 | 144 kB | 2026-02-20 |
| 155 | `claude_usage_log` | [공통] | INFRA | 388 | 152 kB | 2026-03-09 |
| 156 | `kis_configs` | [공통] | INFRA | 5 | 328 kB | 2026-03-28 |
| 157 | `llm_cost_daily` | [공통] | INFRA | 83 | 112 kB | 2026-03-27 |
| 158 | `llm_requests` | [공통] | INFRA | 1,004 | 512 kB | 2026-03-27 |
| 159 | `payments` | [공통] | INFRA | 0 | 32 kB | - |
| 160 | `social_accounts` | [공통] | INFRA | 5 | 64 kB | - |
| 161 | `user_push_subscriptions` | [공통] | INFRA | 0 | 24 kB | - |
| 162 | `user_sessions` | [공통] | INFRA | 2 | 248 kB | 2026-03-29 |
| 163 | `user_settings` | [공통] | INFRA | 10 | 88 kB | 2026-02-11 |
| 164 | `user_strategies` | [공통] | INFRA | 181 | 104 kB | - |
| 165 | `users` | [공통] | INFRA | 13 | 80 kB | 2099-12-31 |
| 166 | `waverider_configs` | [공통] | INFRA | 0 | 24 kB | - |
| 167 | `go100_etf_flow_daily` | [GO100] | INVESTOR | 0 | 16 kB | - |
| 168 | `v4_capital_flow` | [V4.1] | INVESTOR | 1 | 64 kB | 2026-03-05 |
| 169 | `v4_investor_daily` | [V4.1] | INVESTOR | 2,641,752 | 1116 MB | 2026-03-27 |
| 170 | `v4_market_investor_daily` | [V4.1] | INVESTOR | 3,658 | 1792 kB | 2026-03-27 |
| 171 | `v4_program_trades` | [V4.1] | INVESTOR | 287 | 120 kB | 2026-02-25 |
| 172 | `v4_supply_chain` | [V4.1] | INVESTOR | 1,012 | 176 kB | 2026-03-07 |
| 173 | `daily_investor_stats` | [공통] | INVESTOR | 0 | 48 kB | - |
| 174 | `market_turnover_daily` | [공통] | INVESTOR | 26,148 | 3264 kB | 2026-02-05 |
| 175 | `go100_delisted_ohlcv` | [GO100] | MARKET | 24,127 | 4336 kB | 2026-02-20 |
| 176 | `go100_nxt_ohlcv_daily` | [GO100] | MARKET | 136,891 | 55 MB | 2026-03-25 |
| 177 | `go100_tick_daily_stats` | [GO100] | MARKET | 465 | 152 kB | 2026-03-27 |
| 178 | `v4_ohlcv_minute` | [V4.1] | MARKET | 209,842,343 | 0 bytes | 2026-03-27 |
| 179 | `v4_ohlcv_minute_2025_01` | [V4.1] | MARKET | 0 | 48 kB | - |
| 180 | `v4_ohlcv_minute_2025_02` | [V4.1] | MARKET | 2,414,556 | 607 MB | 2025-02-28 |
| 181 | `v4_ohlcv_minute_2025_03` | [V4.1] | MARKET | 13,955,932 | 3523 MB | 2025-03-31 |
| 182 | `v4_ohlcv_minute_2025_04` | [V4.1] | MARKET | 16,029,505 | 4055 MB | 2025-04-30 |
| 183 | `v4_ohlcv_minute_2025_05` | [V4.1] | MARKET | 14,089,169 | 3569 MB | 2025-05-30 |
| 184 | `v4_ohlcv_minute_2025_06` | [V4.1] | MARKET | 15,400,724 | 3882 MB | 2025-06-30 |
| 185 | `v4_ohlcv_minute_2025_07` | [V4.1] | MARKET | 18,004,785 | 4525 MB | 2025-07-31 |
| 186 | `v4_ohlcv_minute_2025_08` | [V4.1] | MARKET | 14,960,494 | 3763 MB | 2025-08-29 |
| 187 | `v4_ohlcv_minute_2025_09` | [V4.1] | MARKET | 17,128,273 | 4310 MB | 2025-09-30 |
| 188 | `v4_ohlcv_minute_2025_10` | [V4.1] | MARKET | 15,050,700 | 3786 MB | 2025-10-31 |
| 189 | `v4_ohlcv_minute_2025_11` | [V4.1] | MARKET | 16,240,539 | 4062 MB | 2025-11-28 |
| 190 | `v4_ohlcv_minute_2025_12` | [V4.1] | MARKET | 16,855,245 | 4256 MB | 2025-12-30 |
| 191 | `v4_ohlcv_minute_2026_01` | [V4.1] | MARKET | 18,295,639 | 4648 MB | 2026-01-30 |
| 192 | `v4_ohlcv_minute_2026_02` | [V4.1] | MARKET | 15,563,870 | 3968 MB | 2026-02-27 |
| 193 | `v4_ohlcv_minute_2026_03` | [V4.1] | MARKET | 15,853,285 | 4044 MB | 2026-03-27 |
| 194 | `v4_sector_index_daily` | [V4.1] | MARKET | 4,080 | 648 kB | 2026-03-07 |
| 195 | `v4_tick_data` | [V4.1] | MARKET | 1,054,292 | 214 MB | 2026-03-27 |
| 196 | `v4_vkospi_daily` | [V4.1] | MARKET | 1,529 | 400 kB | 2026-03-27 |
| 197 | `data_global_index_daily` | [공통] | MARKET | 2,878 | 680 kB | 2026-03-27 |
| 198 | `index_daily` | [공통] | MARKET | 2,151 | 536 kB | 2026-03-27 |
| 199 | `market_data_min` | [공통] | MARKET | 18,058,246 | 3373 MB | 2026-03-12 |
| 200 | `ohlcv_1m_history` | [공통] | MARKET | 18,058,246 | 3951 MB | - |
| 201 | `ohlcv_daily` | [공통] | MARKET | 2,687,617 | 887 MB | 2026-03-27 |
| 202 | `ohlcv_monthly` | [공통] | MARKET | 89,307 | 13 MB | 2026-02-11 |
| 203 | `ohlcv_weekly` | [공통] | MARKET | 357,381 | 50 MB | 2026-02-11 |
| 204 | `price_tick_snapshots` | [공통] | MARKET | 35,865 | 4640 kB | 2026-02-05 |
| 205 | `go100_news_items` | [GO100] | NEWS | 2,782,216 | 2499 MB | 2026-03-27 |
| 206 | `go100_live_orders` | [GO100] | POSITION | 57 | 136 kB | 2026-03-27 |
| 207 | `go100_orderbook_backtest_runs` | [GO100] | POSITION | 9 | 96 kB | 2026-02-24 |
| 208 | `go100_orderbook_daily_stats` | [GO100] | POSITION | 81 | 72 kB | 2026-03-18 |
| 209 | `go100_orders` | [GO100] | POSITION | 49 | 96 kB | 2026-03-26 |
| 210 | `go100_paper_orders` | [GO100] | POSITION | 0 | 32 kB | - |
| 211 | `go100_paper_positions` | [GO100] | POSITION | 0 | 24 kB | - |
| 212 | `go100_paper_trades` | [GO100] | POSITION | 150 | 104 kB | 2026-03-27 |
| 213 | `go100_position_sizing` | [GO100] | POSITION | 1 | 64 kB | 2026-02-28 |
| 214 | `go100_positions` | [GO100] | POSITION | 60 | 112 kB | 2026-03-27 |
| 215 | `go100_trades` | [GO100] | POSITION | 88 | 120 kB | 2026-03-27 |
| 216 | `v4_backtest_trade_log` | [V4.1] | POSITION | 1,084 | 256 kB | - |
| 217 | `v4_backtest_trades` | [V4.1] | POSITION | 213,096 | 45 MB | 2026-03-18 |
| 218 | `v4_broker_trades` | [V4.1] | POSITION | 0 | 24 kB | - |
| 219 | `v4_bt_trades` | [V4.1] | POSITION | 330 | 504 kB | 2026-02-25 |
| 220 | `v4_desk2_trades` | [V4.1] | POSITION | 6 | 48 kB | 2026-03-03 |
| 221 | `v4_desk_paper_trades` | [V4.1] | POSITION | 0 | 32 kB | - |
| 222 | `v4_desk_positions` | [V4.1] | POSITION | 1 | 144 kB | 2026-02-28 |
| 223 | `v4_desk_trade_history` | [V4.1] | POSITION | 0 | 24 kB | - |
| 224 | `v4_desk_trade_log` | [V4.1] | POSITION | 0 | 24 kB | - |
| 225 | `v4_mock_trades` | [V4.1] | POSITION | 218 | 184 kB | 2026-03-23 |
| 226 | `v4_mock_trades_bak_20260324` | [V4.1] | POSITION | 298 | 136 kB | 2026-03-23 |
| 227 | `v4_order_executions` | [V4.1] | POSITION | 0 | 48 kB | - |
| 228 | `v4_order_requests` | [V4.1] | POSITION | 14 | 128 kB | 2026-03-02 |
| 229 | `v4_orderbook_realtime` | [V4.1] | POSITION | 6,261,154 | 2134 MB | 2026-03-27 |
| 230 | `v4_paper_trades` | [V4.1] | POSITION | 7 | 32 kB | 2026-03-01 |
| 231 | `v4_position_extended` | [V4.1] | POSITION | 3 | 80 kB | 2026-02-12 |
| 232 | `v4_position_transfers` | [V4.1] | POSITION | 12 | 64 kB | 2026-03-03 |
| 233 | `v4_positions` | [V4.1] | POSITION | 35 | 240 kB | 2026-03-03 |
| 234 | `v4_positions_backup_20260218` | [V4.1] | POSITION | 20 | 40 kB | 2026-02-18 |
| 235 | `v4_trade_analysis` | [V4.1] | POSITION | 0 | 8192 bytes | - |
| 236 | `v4_trade_executions` | [V4.1] | POSITION | 13 | 112 kB | 2026-03-04 |
| 237 | `v4_trade_schedules` | [V4.1] | POSITION | 5 | 88 kB | 2026-03-27 |
| 238 | `v4_trade_strength_history` | [V4.1] | POSITION | 10,993,630 | 1551 MB | 2026-03-27 |
| 239 | `v4_trades` | [V4.1] | POSITION | 40 | 136 kB | 2026-03-03 |
| 240 | `v4_trades_backup_20260218` | [V4.1] | POSITION | 0 | 0 bytes | - |
| 241 | `v4_virtual_trades_full` | [V4.1] | POSITION | 250 | 336 kB | 2026-03-23 |
| 242 | `v4_virtual_trades_full_bak_20260324` | [V4.1] | POSITION | 281 | 136 kB | 2026-03-23 |
| 243 | `auto_trade_positions` | [공통] | POSITION | 41 | 56 kB | 2026-02-02 |
| 244 | `autotrade_positions` | [공통] | POSITION | 84 | 144 kB | 2026-02-13 |
| 245 | `compound_trades` | [공통] | POSITION | 2,970 | 688 kB | 2026-01-26 |
| 246 | `dummy_trades_archive` | [공통] | POSITION | 132,452 | 42 MB | 2026-02-01 |
| 247 | `liquidation_logs` | [공통] | POSITION | 0 | 32 kB | - |
| 248 | `liquidation_orders` | [공통] | POSITION | 0 | 32 kB | - |
| 249 | `liquidation_sessions` | [공통] | POSITION | 0 | 32 kB | - |
| 250 | `live_positions` | [공통] | POSITION | 11 | 96 kB | 2026-02-06 |
| 251 | `orderbook_snapshots` | [공통] | POSITION | 35,894 | 42 MB | 2026-02-05 |
| 252 | `orders` | [공통] | POSITION | 48 | 144 kB | 2026-03-04 |
| 253 | `pending_orders` | [공통] | POSITION | 7,471 | 1976 kB | 2026-03-04 |
| 254 | `positions` | [공통] | POSITION | 2,919 | 456 kB | 2026-01-26 |
| 255 | `real_trades` | [공통] | POSITION | 54 | 15 MB | 2026-01-29 |
| 256 | `real_trades_archive` | [공통] | POSITION | 0 | 19 MB | - |
| 257 | `trade_comparisons` | [공통] | POSITION | 54 | 6864 kB | 2026-01-29 |
| 258 | `trade_verifications` | [공통] | POSITION | 0 | 104 kB | - |
| 259 | `trades` | [공통] | POSITION | 1 | 96 kB | 2026-01-27 |
| 260 | `virtual_trades` | [공통] | POSITION | 132,506 | 26 MB | 2026-02-01 |
| 261 | `waverider_positions` | [공통] | POSITION | 0 | 24 kB | - |
| 262 | `go100_risk_disclaimers` | [GO100] | RISK | 0 | 72 kB | - |
| 263 | `go100_risk_events` | [GO100] | RISK | 180 | 96 kB | 2026-03-27 |
| 264 | `go100_risk_rules` | [GO100] | RISK | 3 | 88 kB | 2026-03-27 |
| 265 | `v4_backtest_regime_analysis` | [V4.1] | RISK | 230 | 480 kB | 2025-01-01 |
| 266 | `v4_bt_daily_risk_log` | [V4.1] | RISK | 32 | 96 kB | 2026-02-20 |
| 267 | `v4_market_regime_daily` | [V4.1] | RISK | 1,135 | 560 kB | 2026-03-27 |
| 268 | `go100_cross_market_signals` | [GO100] | STRATEGY | 27 | 64 kB | 2026-03-27 |
| 269 | `go100_signal_performance` | [GO100] | STRATEGY | 0 | 8192 bytes | - |
| 270 | `go100_strategy_cards` | [GO100] | STRATEGY | 71 | 408 kB | 2026-03-09 |
| 271 | `go100_strategy_edit_history` | [GO100] | STRATEGY | 0 | 40 kB | - |
| 272 | `go100_strategy_hypotheses` | [GO100] | STRATEGY | 1,385 | 4624 kB | 2026-03-27 |
| 273 | `go100_strategy_knowledge` | [GO100] | STRATEGY | 17 | 176 kB | 2026-03-04 |
| 274 | `go100_strategy_portfolio_snapshots` | [GO100] | STRATEGY | 0 | 40 kB | - |
| 275 | `go100_strategy_portfolios` | [GO100] | STRATEGY | 23 | 56 kB | 2026-03-26 |
| 276 | `v4_condition_search` | [V4.1] | STRATEGY | 0 | 24 kB | - |
| 277 | `v4_desk1_signals` | [V4.1] | STRATEGY | 7 | 40 kB | 2026-03-27 |
| 278 | `v4_desk2_signals` | [V4.1] | STRATEGY | 801 | 168 kB | 2026-03-27 |
| 279 | `v4_desk_signal_history` | [V4.1] | STRATEGY | 0 | 24 kB | - |
| 280 | `v4_desk_strategy_mapping` | [V4.1] | STRATEGY | 56 | 112 kB | 2026-03-20 |
| 281 | `v4_explosion_signals` | [V4.1] | STRATEGY | 38 | 56 kB | 2026-03-19 |
| 282 | `v4_scalping_signals` | [V4.1] | STRATEGY | 0 | 40 kB | - |
| 283 | `v4_scoring_weights` | [V4.1] | STRATEGY | 1 | 64 kB | 2026-02-12 |
| 284 | `v4_signals` | [V4.1] | STRATEGY | 127,362 | 42 MB | 2026-03-13 |
| 285 | `v4_strategy_performance` | [V4.1] | STRATEGY | 0 | 32 kB | - |
| 286 | `v4_strategy_registry` | [V4.1] | STRATEGY | 77 | 120 kB | - |
| 287 | `v4_strategy_stage_log` | [V4.1] | STRATEGY | 13 | 32 kB | 2026-03-20 |
| 288 | `strategy_allocations` | [공통] | STRATEGY | 0 | 24 kB | - |
| 289 | `strategy_cards` | [공통] | STRATEGY | 60 | 312 kB | 2026-02-22 |
| 290 | `strategy_performance` | [공통] | STRATEGY | 0 | 32 kB | - |
| 291 | `trading_signals` | [공통] | STRATEGY | 137,185 | 30 MB | 2026-03-04 |
| 292 | `waverider_signals` | [공통] | STRATEGY | 0 | 32 kB | - |
| 293 | `go100_delisted_stocks` | [GO100] | UNIVERSE | 100 | 72 kB | 2024-08-22 |
| 294 | `go100_fundamentals` | [GO100] | UNIVERSE | 2,720 | 1904 kB | 2026-02-27 |
| 295 | `go100_fundamentals_pit` | [GO100] | UNIVERSE | 32,920 | 6264 kB | 2025-12-31 |
| 296 | `go100_sector_correlation` | [GO100] | UNIVERSE | 1,624 | 536 kB | 2026-02-26 |
| 297 | `go100_sector_price` | [GO100] | UNIVERSE | 7,615 | 1352 kB | 2026-03-27 |
| 298 | `v4_fundamental_quarterly` | [V4.1] | UNIVERSE | 10,271 | 3992 kB | 2026-03-27 |
| 299 | `v4_market_calendar` | [V4.1] | UNIVERSE | 129 | 96 kB | 2026-12-30 |
| 300 | `v4_market_ranking` | [V4.1] | UNIVERSE | 3,300 | 2296 kB | 2026-03-27 |
| 301 | `v4_scalping_universe` | [V4.1] | UNIVERSE | 1,354 | 368 kB | 2026-03-02 |
| 302 | `v4_sector_correlation` | [V4.1] | UNIVERSE | 0 | 24 kB | - |
| 303 | `v4_sector_daily` | [V4.1] | UNIVERSE | 15,608 | 12 MB | 2026-03-27 |
| 304 | `v4_sector_mapping` | [V4.1] | UNIVERSE | 3,844 | 5376 kB | 2026-03-07 |
| 305 | `v4_sector_price` | [V4.1] | UNIVERSE | 0 | 24 kB | - |
| 306 | `v4_sector_stock_mapping` | [V4.1] | UNIVERSE | 2,770 | 616 kB | 2026-02-26 |
| 307 | `v4_stock_master` | [V4.1] | UNIVERSE | 3,844 | 624 kB | 2026-03-18 |
| 308 | `v4_stock_sector` | [V4.1] | UNIVERSE | 4,225 | 840 kB | 2026-02-27 |
| 309 | `v4_theme_activity_daily` | [V4.1] | UNIVERSE | 34,122 | 5048 kB | 2026-02-27 |
| 310 | `v4_theme_daily` | [V4.1] | UNIVERSE | 34,122 | 11 MB | 2026-02-27 |
| 311 | `v4_theme_detail` | [V4.1] | UNIVERSE | 142 | 328 kB | 2026-03-27 |
| 312 | `v4_theme_mapping` | [V4.1] | UNIVERSE | 551 | 1784 kB | 2026-03-07 |
| 313 | `v4_theme_master` | [V4.1] | UNIVERSE | 142 | 120 kB | 2026-03-10 |
| 314 | `v4_theme_stock` | [V4.1] | UNIVERSE | 7,496 | 1792 kB | 2026-03-25 |
| 315 | `v4_theme_stock_backup_20260228` | [V4.1] | UNIVERSE | 2,106 | 192 kB | 2026-02-27 |
| 316 | `v4_theme_stock_mapping` | [V4.1] | UNIVERSE | 0 | 16 kB | - |
| 317 | `v4_universe_version` | [V4.1] | UNIVERSE | 16 | 112 kB | 2026-02-14 |
| 318 | `financial_ratios` | [공통] | UNIVERSE | 45,870 | 6688 kB | 2026-02-11 |
| 319 | `stock_fundamentals` | [공통] | UNIVERSE | 33,831 | 5528 kB | 2026-02-26 |
| 320 | `stock_universe` | [공통] | UNIVERSE | 3,844 | 2704 kB | 2026-02-20 |

### 뷰 (9개)

| # | 뷰 이름 |
|---|--------|
| 1 | `go100_investor_flow` |
| 2 | `go100_minute_bars` |
| 3 | `go100_orderbook_snapshot` |
| 4 | `go100_strategy_store` |
| 5 | `go100_tick_data` |
| 6 | `v4_ohlcv_clean` |
| 7 | `vw_fund_ledger` |
| 8 | `vw_llm_daily_total` |
| 9 | `vw_llm_user_monthly` |

---

## 2. 카테고리별 상세 스키마


### [AI]

#### `go100_backtest_runs` [GO100]

행 수: 20 | 크기: 200 kB | 최신: 2026-01-15

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_backtest_runs_i |
| 2 | `user_id` | integer | N |  |  |
| 3 | `go100_card_id` | bigint | Y |  |  |
| 4 | `strategy_name` | character varying(200) | Y |  |  |
| 5 | `stock_codes_used` | ARRAY | Y |  |  |
| 6 | `universe_filter_snapshot` | jsonb | Y |  |  |
| 7 | `start_date` | date | N |  |  |
| 8 | `end_date` | date | N |  |  |
| 9 | `initial_capital` | bigint | Y |  | 10000000 |
| 10 | `total_return` | numeric | Y |  |  |
| 11 | `annualized_return` | numeric | Y |  |  |
| 12 | `max_drawdown` | numeric | Y |  |  |
| 13 | `sharpe_ratio` | numeric | Y |  |  |
| 14 | `win_rate` | numeric | Y |  |  |
| 15 | `total_trades` | integer | Y |  |  |
| 16 | `profit_factor` | numeric | Y |  |  |
| 17 | `avg_holding_days` | numeric | Y |  |  |
| 18 | `optimization_round` | integer | Y |  | 0 |
| 19 | `parent_run_id` | bigint | Y |  |  |
| 20 | `optimization_log` | jsonb | Y |  |  |
| 21 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 22 | `error_message` | text | Y |  |  |
| 23 | `result_detail` | jsonb | Y |  |  |
| 24 | `created_at` | timestamp with time zone | Y |  | now() |
| 25 | `completed_at` | timestamp with time zone | Y |  |  |
| 26 | `params_hash` | character varying(12) | Y |  |  |
| 27 | `gross_return` | numeric | Y |  |  |
| 28 | `total_commission` | numeric | Y |  |  |
| 29 | `total_tax` | numeric | Y |  |  |
| 30 | `total_slippage` | numeric | Y |  |  |
| 31 | `net_return` | numeric | Y |  |  |
| 32 | `slippage_model` | character varying(20) | Y |  | 'none'::character varying |

**인덱스:**

- `go100_backtest_runs_pkey`
- `idx_go100_bt_user`
- `idx_go100_bt_card`
- `idx_go100_bt_status`

---

#### `go100_calibration_params` [GO100]

행 수: 12 | 크기: 48 kB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_calibration_par |
| 2 | `param_name` | character varying(50) | N |  |  |
| 3 | `param_value` | numeric | Y |  |  |
| 4 | `stock_type` | character varying(20) | Y |  |  |
| 5 | `last_calibrated` | timestamp without time zone | Y |  | now() |
| 6 | `notes` | text | Y |  |  |

**인덱스:**

- `go100_calibration_params_pkey`
- `go100_calibration_params_param_name_stock_type_key`

---

#### `go100_fit_analysis` [GO100]

행 수: 40 | 크기: 88 kB | 최신: 2026-02-21

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_fit_analysis_id |
| 2 | `user_id` | integer | N |  |  |
| 3 | `go100_card_id` | bigint | N |  |  |
| 4 | `stock_code` | character varying(20) | N |  |  |
| 5 | `stock_name` | character varying(100) | Y |  |  |
| 6 | `total_return` | numeric | Y |  |  |
| 7 | `win_rate` | numeric | Y |  |  |
| 8 | `profit_factor` | numeric | Y |  |  |
| 9 | `max_drawdown` | numeric | Y |  |  |
| 10 | `sharpe_ratio` | numeric | Y |  |  |
| 11 | `total_trades` | integer | Y |  |  |
| 12 | `avg_holding_days` | numeric | Y |  |  |
| 13 | `fit_score` | numeric | Y |  |  |
| 14 | `entry_timing` | jsonb | Y |  |  |
| 15 | `period_days` | integer | Y |  |  |
| 16 | `analysis_date` | date | N |  | CURRENT_DATE |
| 17 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_fit_analysis_pkey`
- `idx_go100_fit_card`

---

#### `go100_gap_calibrator` [GO100]

행 수: 110,735 | 크기: 33 MB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `gap_id` | integer | N | PK | nextval('go100_gap_calibrator_ |
| 2 | `ticker` | character varying(20) | N |  |  |
| 3 | `gap_date` | date | N |  |  |
| 4 | `gap_type` | character varying(10) | N |  |  |
| 5 | `gap_pct` | numeric | N |  |  |
| 6 | `prev_close` | numeric | Y |  |  |
| 7 | `open_price` | numeric | Y |  |  |
| 8 | `day_high` | numeric | Y |  |  |
| 9 | `day_low` | numeric | Y |  |  |
| 10 | `day_close` | numeric | Y |  |  |
| 11 | `gap_filled` | boolean | Y |  |  |
| 12 | `fill_time_minutes` | integer | Y |  |  |
| 13 | `day_return` | numeric | Y |  |  |
| 14 | `next_day_return` | numeric | Y |  |  |
| 15 | `volume_ratio` | numeric | Y |  |  |
| 16 | `sector` | character varying(50) | Y |  |  |
| 17 | `cluster` | character varying(30) | Y |  |  |
| 18 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_gap_calibrator_pkey`
- `go100_gap_calibrator_ticker_gap_date_key`
- `idx_gap_cal_ticker`
- `idx_gap_cal_type`
- `idx_gap_cal_date`

---

#### `go100_optimization_runs` [GO100]

행 수: 0 | 크기: 48 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `opt_run_id` | integer | N | PK | nextval('go100_optimization_ru |
| 2 | `original_card_id` | bigint | N |  |  |
| 3 | `iteration` | integer | N |  | 0 |
| 4 | `parent_run_id` | integer | Y |  |  |
| 5 | `parameters_before` | jsonb | Y |  |  |
| 6 | `parameters_after` | jsonb | Y |  |  |
| 7 | `change_description` | text | Y |  |  |
| 8 | `backtest_run_id` | bigint | Y |  |  |
| 9 | `total_return` | numeric | Y |  |  |
| 10 | `mdd` | numeric | Y |  |  |
| 11 | `sharpe_ratio` | numeric | Y |  |  |
| 12 | `win_rate` | numeric | Y |  |  |
| 13 | `trade_count` | integer | Y |  |  |
| 14 | `optimization_goal` | text | Y |  |  |
| 15 | `llm_analysis` | text | Y |  |  |
| 16 | `llm_recommendation` | text | Y |  |  |
| 17 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 18 | `is_best` | boolean | Y |  | false |
| 19 | `optimized_card_id` | bigint | Y |  |  |
| 20 | `created_at` | timestamp with time zone | Y |  | now() |
| 21 | `updated_at` | timestamp with time zone | Y |  | now() |
| 22 | `user_id` | integer | N |  |  |

**인덱스:**

- `go100_optimization_runs_pkey`
- `idx_opt_runs_card`
- `idx_opt_runs_user`
- `idx_opt_runs_status`
- `idx_opt_runs_best`

---

#### `go100_portfolio_optimizations` [GO100]

행 수: 17 | 크기: 64 kB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `optimization_id` | integer | N | PK | nextval('go100_portfolio_optim |
| 2 | `user_id` | integer | N |  |  |
| 3 | `method` | character varying(30) | N |  |  |
| 4 | `tickers` | ARRAY | N |  |  |
| 5 | `weights` | ARRAY | N |  |  |
| 6 | `expected_return` | numeric | Y |  |  |
| 7 | `expected_risk` | numeric | Y |  |  |
| 8 | `sharpe_ratio` | numeric | Y |  |  |
| 9 | `constraints` | jsonb | Y |  |  |
| 10 | `input_params` | jsonb | Y |  |  |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_portfolio_optimizations_pkey`
- `idx_po_user`
- `idx_po_created`

---

#### `v4_backtest_daily` [V4.1]

행 수: 6,170 | 크기: 3368 kB | 최신: 2026-03-06

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_backtest_daily_id_ |
| 2 | `session_id` | bigint | Y |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `total_asset` | numeric | Y |  |  |
| 5 | `cash_balance` | numeric | Y |  |  |
| 6 | `holding_value` | numeric | Y |  |  |
| 7 | `daily_pnl` | numeric | Y |  |  |
| 8 | `daily_pnl_pct` | numeric | Y |  |  |
| 9 | `cumulative_pct` | numeric | Y |  |  |
| 10 | `current_stage` | integer | Y |  |  |
| 11 | `desk_allocation` | jsonb | Y |  |  |
| 12 | `open_positions` | integer | Y |  |  |
| 13 | `trades_today` | integer | Y |  |  |

**인덱스:**

- `v4_backtest_daily_pkey`
- `v4_backtest_daily_session_id_trade_date_key`
- `idx_v4_bt_daily_session`
- `idx_v4bt_daily_session`

---

#### `v4_backtest_desk_detail` [V4.1]

행 수: 12 | 크기: 72 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_desk_deta |
| 2 | `run_id` | character varying(50) | Y |  |  |
| 3 | `desk_id` | integer | N |  |  |
| 4 | `class_type` | character varying(10) | Y |  |  |
| 5 | `total_trades` | integer | Y |  |  |
| 6 | `win_trades` | integer | Y |  |  |
| 7 | `lose_trades` | integer | Y |  |  |
| 8 | `win_rate_pct` | numeric | Y |  |  |
| 9 | `total_return_pct` | numeric | Y |  |  |
| 10 | `avg_return_pct` | numeric | Y |  |  |
| 11 | `max_win_pct` | numeric | Y |  |  |
| 12 | `max_loss_pct` | numeric | Y |  |  |
| 13 | `avg_holding_days` | numeric | Y |  |  |
| 14 | `profit_factor` | numeric | Y |  |  |
| 15 | `upgrade_count` | integer | Y |  | 0 |

**인덱스:**

- `v4_backtest_desk_detail_pkey`
- `idx_bt_desk_run`

---

#### `v4_backtest_equity` [V4.1]

행 수: 175 | 크기: 80 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_equity_id |
| 2 | `run_id` | character varying(50) | Y |  |  |
| 3 | `trade_date` | character varying(8) | N |  |  |
| 4 | `equity` | bigint | N |  |  |
| 5 | `daily_return_pct` | numeric | Y |  |  |
| 6 | `open_positions` | integer | Y |  |  |
| 7 | `daily_trades` | integer | Y |  |  |
| 8 | `daily_pnl` | bigint | Y |  |  |

**인덱스:**

- `v4_backtest_equity_pkey`
- `idx_bt_equity_run`

---

#### `v4_backtest_profile` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `profile_id` | integer | N | PK | nextval('v4_backtest_profile_p |
| 2 | `card_id` | integer | Y |  |  |
| 3 | `desk_id` | integer | N |  |  |
| 4 | `profile_name` | character varying(100) | N |  |  |
| 5 | `engine_version` | character varying(10) | N |  | 'v2'::character varying |
| 6 | `params` | jsonb | N |  | '{}'::jsonb |
| 7 | `is_active` | boolean | Y |  | true |
| 8 | `created_at` | timestamp without time zone | N |  | now() |
| 9 | `updated_at` | timestamp without time zone | N |  | now() |

**인덱스:**

- `v4_backtest_profile_pkey`

---

#### `v4_backtest_results` [V4.1]

행 수: 60 | 크기: 808 kB | 최신: 2026-02-19

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_results_i |
| 2 | `strategy_name` | character varying(100) | N |  |  |
| 3 | `start_date` | date | N |  |  |
| 4 | `end_date` | date | N |  |  |
| 5 | `initial_capital` | numeric | N |  |  |
| 6 | `final_capital` | numeric | Y |  |  |
| 7 | `total_return_pct` | numeric | Y |  |  |
| 8 | `max_drawdown_pct` | numeric | Y |  |  |
| 9 | `sharpe_ratio` | numeric | Y |  |  |
| 10 | `win_rate` | numeric | Y |  |  |
| 11 | `total_trades` | integer | Y |  | 0 |
| 12 | `avg_holding_days` | numeric | Y |  |  |
| 13 | `parameters` | jsonb | Y |  |  |
| 14 | `daily_snapshots` | jsonb | Y |  |  |
| 15 | `trade_records` | jsonb | Y |  |  |
| 16 | `created_at` | timestamp with time zone | Y |  | now() |
| 17 | `user_id` | integer | Y |  |  |

**인덱스:**

- `v4_backtest_results_pkey`
- `idx_v4_backtest_user`
- `idx_v4_backtest_strategy`
- `idx_v4_backtest_created`

---

#### `v4_backtest_results_desk_run` [V4.1]

행 수: 39 | 크기: 56 kB | 최신: 2025-11-01

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_results_d |
| 2 | `strategy_name` | character varying(80) | N |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `desk_id` | integer | Y |  |  |
| 5 | `start_date` | date | Y |  |  |
| 6 | `end_date` | date | Y |  |  |
| 7 | `total_trades` | integer | Y |  |  |
| 8 | `win_rate` | numeric | Y |  |  |
| 9 | `total_return` | numeric | Y |  |  |
| 10 | `max_drawdown` | numeric | Y |  |  |
| 11 | `sharpe_ratio` | numeric | Y |  |  |
| 12 | `profit_factor` | numeric | Y |  |  |
| 13 | `avg_hold_days` | numeric | Y |  |  |
| 14 | `tested_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_backtest_results_desk_run_pkey`

---

#### `v4_backtest_runs` [V4.1]

행 수: 5 | 크기: 112 kB | 최신: 2026-01-24

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_runs_id_s |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_card_id` | integer | Y |  |  |
| 4 | `strategy_name` | character varying(100) | Y |  |  |
| 5 | `stock_codes` | ARRAY | Y |  |  |
| 6 | `start_date` | date | N |  |  |
| 7 | `end_date` | date | N |  |  |
| 8 | `initial_capital` | bigint | Y |  | 10000000 |
| 9 | `total_return` | numeric | Y |  |  |
| 10 | `annualized_return` | numeric | Y |  |  |
| 11 | `max_drawdown` | numeric | Y |  |  |
| 12 | `sharpe_ratio` | numeric | Y |  |  |
| 13 | `win_rate` | numeric | Y |  |  |
| 14 | `total_trades` | integer | Y |  | 0 |
| 15 | `winning_trades` | integer | Y |  | 0 |
| 16 | `losing_trades` | integer | Y |  | 0 |
| 17 | `avg_profit_per_trade` | numeric | Y |  |  |
| 18 | `max_consecutive_wins` | integer | Y |  | 0 |
| 19 | `max_consecutive_losses` | integer | Y |  | 0 |
| 20 | `profit_factor` | numeric | Y |  |  |
| 21 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 22 | `error_message` | text | Y |  |  |
| 23 | `params` | jsonb | Y |  |  |
| 24 | `result_detail` | jsonb | Y |  |  |
| 25 | `created_at` | timestamp with time zone | Y |  | now() |
| 26 | `completed_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_backtest_runs_pkey1`
- `idx_backtest_runs_user`
- `idx_backtest_runs_strategy`
- `idx_backtest_runs_status`

---

#### `v4_backtest_runs_legacy` [V4.1]

행 수: 3 | 크기: 72 kB | 최신: 2026-02-18

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_runs_id_s |
| 2 | `run_id` | character varying(50) | N |  |  |
| 3 | `start_date` | character varying(8) | N |  |  |
| 4 | `end_date` | character varying(8) | N |  |  |
| 5 | `initial_capital` | bigint | N |  |  |
| 6 | `desks_tested` | character varying(20) | N |  |  |
| 7 | `use_minute_data` | boolean | Y |  | false |
| 8 | `slippage_pct` | numeric | Y |  |  |
| 9 | `commission_pct` | numeric | Y |  |  |
| 10 | `risk_management` | boolean | Y |  | true |
| 11 | `total_return_pct` | numeric | Y |  |  |
| 12 | `cagr_pct` | numeric | Y |  |  |
| 13 | `mdd_pct` | numeric | Y |  |  |
| 14 | `sharpe_ratio` | numeric | Y |  |  |
| 15 | `total_trades` | integer | Y |  |  |
| 16 | `win_rate_pct` | numeric | Y |  |  |
| 17 | `profit_factor` | numeric | Y |  |  |
| 18 | `avg_holding_days` | numeric | Y |  |  |
| 19 | `final_equity` | bigint | Y |  |  |
| 20 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_backtest_runs_pkey`
- `v4_backtest_runs_run_id_key`

---

#### `v4_backtest_sessions` [V4.1]

행 수: 164 | 크기: 960 kB | 최신: 2026-02-25

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `session_id` | bigint | N | PK | nextval('v4_backtest_sessions_ |
| 2 | `session_name` | character varying(100) | N |  |  |
| 3 | `start_date` | date | N |  |  |
| 4 | `end_date` | date | N |  |  |
| 5 | `initial_capital` | numeric | N |  |  |
| 6 | `stage_config` | jsonb | N |  |  |
| 7 | `desk_configs` | jsonb | N |  |  |
| 8 | `split_configs` | jsonb | N |  |  |
| 9 | `status` | character varying(20) | Y |  | 'RUNNING'::character varying |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |
| 11 | `completed_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_backtest_sessions_pkey`

---

#### `v4_backtest_strategies` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_strategie |
| 2 | `strategy_key` | character varying(50) | N |  |  |
| 3 | `strategy_name` | character varying(100) | Y |  |  |
| 4 | `category` | character varying(30) | Y |  |  |
| 5 | `description` | text | Y |  |  |
| 6 | `min_bars` | integer | Y |  | 60 |
| 7 | `params` | jsonb | Y |  | '{}'::jsonb |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_backtest_strategies_pkey`
- `v4_backtest_strategies_strategy_key_key`

---

#### `v4_backtest_summary` [V4.1]

행 수: 132 | 크기: 136 kB | 최신: 2026-03-07

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_backtest_summary_i |
| 2 | `session_id` | bigint | Y |  |  |
| 3 | `total_days` | integer | Y |  |  |
| 4 | `total_trades` | integer | Y |  |  |
| 5 | `winning_trades` | integer | Y |  |  |
| 6 | `losing_trades` | integer | Y |  |  |
| 7 | `win_rate` | numeric | Y |  |  |
| 8 | `total_return_pct` | numeric | Y |  |  |
| 9 | `annualized_return` | numeric | Y |  |  |
| 10 | `max_drawdown_pct` | numeric | Y |  |  |
| 11 | `sharpe_ratio` | numeric | Y |  |  |
| 12 | `profit_factor` | numeric | Y |  |  |
| 13 | `avg_win_pct` | numeric | Y |  |  |
| 14 | `avg_loss_pct` | numeric | Y |  |  |
| 15 | `max_consecutive_wins` | integer | Y |  |  |
| 16 | `max_consecutive_losses` | integer | Y |  |  |
| 17 | `final_capital` | numeric | Y |  |  |
| 18 | `desk_performance` | jsonb | Y |  |  |
| 19 | `stage_transitions` | integer | Y |  |  |
| 20 | `total_transfers` | integer | Y |  |  |
| 21 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_backtest_summary_pkey`
- `v4_backtest_summary_session_id_key`

---

#### `v4_backtest_v2_sessions` [V4.1]

행 수: 0 | 크기: 40 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_v2_sessio |
| 2 | `session_id` | character varying(32) | N |  |  |
| 3 | `user_id` | integer | N |  |  |
| 4 | `stock_code` | character varying(20) | N |  |  |
| 5 | `start_date` | character varying(10) | Y |  |  |
| 6 | `end_date` | character varying(10) | Y |  |  |
| 7 | `initial_capital` | bigint | Y |  | 10000000 |
| 8 | `strategies` | jsonb | Y |  |  |
| 9 | `result_json` | jsonb | Y |  |  |
| 10 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_backtest_v2_sessions_pkey`
- `v4_backtest_v2_sessions_session_id_key`
- `idx_bt_v2_sessions_user`
- `idx_bt_v2_sessions_sid`

---

#### `v4_bt_discoveries` [V4.1]

행 수: 6,931 | 크기: 2944 kB | 최신: 2026-02-20

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_bt_discoveries_id_ |
| 2 | `session_id` | character varying(64) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `trade_time` | character varying(10) | Y |  |  |
| 5 | `stock_code` | character varying(20) | N |  |  |
| 6 | `stock_name` | character varying(100) | Y |  |  |
| 7 | `condition_code` | character varying(10) | N |  |  |
| 8 | `condition_name` | character varying(50) | Y |  |  |
| 9 | `condition_score` | numeric | Y |  | 0 |
| 10 | `desk_score` | numeric | Y |  | 0 |
| 11 | `cs_score` | numeric | Y |  | 0 |
| 12 | `c1_gap_pct` | numeric | Y |  |  |
| 13 | `c2_volume_ratio` | numeric | Y |  |  |
| 14 | `c3_vi_triggered` | boolean | Y |  |  |
| 15 | `c4_rsi` | numeric | Y |  |  |
| 16 | `c5_bb_position` | numeric | Y |  |  |
| 17 | `c6_sector_rank` | integer | Y |  |  |
| 18 | `c7_strength_drop` | numeric | Y |  |  |
| 19 | `passed_to_strategy` | boolean | Y |  | false |
| 20 | `strategy_name` | character varying(50) | Y |  |  |
| 21 | `reject_reason` | character varying(200) | Y |  |  |
| 22 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_bt_discoveries_pkey`
- `idx_bt_discoveries_session`
- `idx_bt_discoveries_stock`
- `idx_bt_discoveries_condition`

---

#### `v4_bt_discovery_log` [V4.1]

행 수: 776,636 | 크기: 518 MB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_bt_discovery_log_i |
| 2 | `bt_session_id` | integer | N |  |  |
| 3 | `discovered_at` | timestamp with time zone | N |  |  |
| 4 | `trade_date` | date | N |  |  |
| 5 | `stock_code` | character varying(20) | N |  |  |
| 6 | `stock_name` | character varying(100) | Y |  |  |
| 7 | `condition_id` | character varying(10) | N |  |  |
| 8 | `desk_score` | numeric | Y |  |  |
| 9 | `score_detail` | jsonb | Y |  |  |
| 10 | `concurrent_count` | integer | Y |  |  |
| 11 | `rank_in_concurrent` | integer | Y |  |  |
| 12 | `primary_strategy` | character varying(30) | Y |  |  |
| 13 | `cross_strategies` | ARRAY | Y |  |  |
| 14 | `passed` | boolean | N |  | false |
| 15 | `reject_reason` | character varying(200) | Y |  |  |
| 16 | `indicator_snapshot` | jsonb | Y |  |  |
| 17 | `regime_at_discovery` | character varying(30) | Y |  |  |
| 18 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_bt_discovery_log_pkey`
- `idx_bt_discovery_log_session`
- `idx_bt_discovery_log_date`
- `idx_bt_discovery_log_condition`

---

#### `v4_bt_sessions` [V4.1]

행 수: 67 | 크기: 256 kB | 최신: 2026-02-25

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_bt_sessions_id_seq |
| 2 | `session_id` | character varying(64) | N |  |  |
| 3 | `desk_id` | character varying(10) | N |  | '2'::character varying |
| 4 | `strategy_name` | character varying(50) | N |  |  |
| 5 | `status` | character varying(20) | N |  | 'RUNNING'::character varying |
| 6 | `start_date` | date | N |  |  |
| 7 | `end_date` | date | N |  |  |
| 8 | `capital` | bigint | N |  | 10000000 |
| 9 | `total_trades` | integer | Y |  | 0 |
| 10 | `win_trades` | integer | Y |  | 0 |
| 11 | `loss_trades` | integer | Y |  | 0 |
| 12 | `win_rate` | numeric | Y |  | 0 |
| 13 | `avg_return_pct` | numeric | Y |  | 0 |
| 14 | `total_return_pct` | numeric | Y |  | 0 |
| 15 | `max_drawdown_pct` | numeric | Y |  | 0 |
| 16 | `calmar_ratio` | numeric | Y |  | 0 |
| 17 | `profit_factor` | numeric | Y |  | 0 |
| 18 | `max_daily_loss_pct` | numeric | Y |  | 0 |
| 19 | `avg_trades_per_day` | numeric | Y |  | 0 |
| 20 | `oos_is_ratio` | numeric | Y |  | 0 |
| 21 | `sharpe_ratio` | numeric | Y |  | 0 |
| 22 | `pass_criteria` | boolean | Y |  | false |
| 23 | `fail_reasons` | jsonb | Y |  | '[]'::jsonb |
| 24 | `parameters` | jsonb | Y |  | '{}'::jsonb |
| 25 | `risk_params` | jsonb | Y |  | '{}'::jsonb |
| 26 | `started_at` | timestamp with time zone | Y |  | now() |
| 27 | `completed_at` | timestamp with time zone | Y |  |  |
| 28 | `created_at` | timestamp with time zone | Y |  | now() |
| 29 | `updated_at` | timestamp with time zone | Y |  | now() |
| 30 | `metadata` | jsonb | Y |  | '{}'::jsonb |

**인덱스:**

- `v4_bt_sessions_pkey`
- `v4_bt_sessions_session_id_key`
- `idx_bt_sessions_strategy`
- `idx_bt_sessions_status`

---

#### `v4_bt_versions` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_bt_versions_id_seq |
| 2 | `version_tag` | character varying(30) | N |  |  |
| 3 | `strategy_name` | character varying(50) | N |  |  |
| 4 | `session_id` | character varying(64) | Y |  |  |
| 5 | `change_type` | character varying(30) | N |  |  |
| 6 | `change_description` | text | Y |  |  |
| 7 | `parameters_before` | jsonb | Y |  | '{}'::jsonb |
| 8 | `parameters_after` | jsonb | Y |  | '{}'::jsonb |
| 9 | `return_before` | numeric | Y |  |  |
| 10 | `return_after` | numeric | Y |  |  |
| 11 | `calmar_before` | numeric | Y |  |  |
| 12 | `calmar_after` | numeric | Y |  |  |
| 13 | `pf_before` | numeric | Y |  |  |
| 14 | `pf_after` | numeric | Y |  |  |
| 15 | `improvement` | boolean | Y |  |  |
| 16 | `improvement_pct` | numeric | Y |  |  |
| 17 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_bt_versions_pkey`
- `idx_bt_versions_strategy`

---

#### `v4_desk_backtest_results` [V4.1]

행 수: 102 | 크기: 176 kB | 최신: 2025-12-19

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_desk_backtest_resu |
| 2 | `run_id` | uuid | N |  |  |
| 3 | `desk_level` | character varying(16) | N |  |  |
| 4 | `param_key` | character varying(128) | N |  | ''::character varying |
| 5 | `param_value` | numeric | N |  | 0 |
| 6 | `param_snapshot` | jsonb | N |  | '{}'::jsonb |
| 7 | `backtest_start` | date | N |  |  |
| 8 | `backtest_end` | date | N |  |  |
| 9 | `total_signals` | integer | N |  | 0 |
| 10 | `triggered_signals` | integer | N |  | 0 |
| 11 | `win_rate` | numeric | Y |  |  |
| 12 | `profit_factor` | numeric | Y |  |  |
| 13 | `avg_pnl_pct` | numeric | Y |  |  |
| 14 | `max_drawdown_pct` | numeric | Y |  |  |
| 15 | `sharpe_ratio` | numeric | Y |  |  |
| 16 | `notes` | text | N |  | ''::text |
| 17 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_desk_backtest_results_pkey`
- `idx_v4_desk_bt_run_id`
- `idx_v4_desk_bt_desk_level`
- `idx_v4_desk_bt_profit_factor`
- `idx_v4_desk_bt_param_key`

---

#### `v4_optimization_results` [V4.1]

행 수: 1,996 | 크기: 856 kB | 최신: 2026-03-19

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_optimization_resul |
| 2 | `desk_id` | integer | N |  |  |
| 3 | `strategy_name` | text | N |  |  |
| 4 | `params` | jsonb | N |  |  |
| 5 | `exit_rules` | jsonb | N |  |  |
| 6 | `total_return_pct` | double precision | Y |  |  |
| 7 | `win_rate_pct` | double precision | Y |  |  |
| 8 | `total_trades` | integer | Y |  |  |
| 9 | `avg_return_per_trade` | double precision | Y |  |  |
| 10 | `max_drawdown_pct` | double precision | Y |  |  |
| 11 | `sharpe_ratio` | double precision | Y |  |  |
| 12 | `profit_factor` | double precision | Y |  |  |
| 13 | `avg_holding_days` | double precision | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_optimization_results_pkey`
- `idx_opt_desk_strategy`

---

#### `backtest_params` [공통]

행 수: 341 | 크기: 120 kB | 최신: 2026-02-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('backtest_params_id_se |
| 2 | `strategy_id` | character varying(50) | N |  |  |
| 3 | `objective` | text | Y |  | 'return'::text |
| 4 | `score` | real | Y |  | 0 |
| 5 | `params_json` | text | Y |  |  |
| 6 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `backtest_params_pkey`
- `idx_backtest_params_strategy`

---

#### `backtest_results` [공통]

행 수: 3 | 크기: 48 kB | 최신: 2024-01-02

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('backtest_results_id_s |
| 2 | `strategy_id` | character varying(50) | N |  |  |
| 3 | `strategy_name` | character varying(255) | Y |  |  |
| 4 | `period_start` | date | N |  |  |
| 5 | `period_end` | date | N |  |  |
| 6 | `universe_tag` | text | Y |  | 'top100_daily_union'::text |
| 7 | `total_return` | real | Y |  | 0 |
| 8 | `win_rate` | real | Y |  | 0 |
| 9 | `max_drawdown` | real | Y |  | 0 |
| 10 | `total_trades` | integer | Y |  | 0 |
| 11 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `backtest_results_pkey`
- `idx_backtest_strategy`

---

#### `backtests` [공통]

행 수: 0 | 크기: 112 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('backtests_id_seq'::re |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_combo` | text | N |  |  |
| 4 | `scenario` | character varying(50) | N |  |  |
| 5 | `initial_capital` | real | N |  |  |
| 6 | `final_capital` | real | N |  |  |
| 7 | `total_return` | real | N |  |  |
| 8 | `annual_return` | real | Y |  |  |
| 9 | `sharpe_ratio` | real | Y |  |  |
| 10 | `max_drawdown` | real | Y |  |  |
| 11 | `win_rate` | real | Y |  |  |
| 12 | `total_trades` | integer | Y |  |  |
| 13 | `market_regime` | character varying(50) | Y |  |  |
| 14 | `start_date` | timestamp without time zone | N |  |  |
| 15 | `end_date` | timestamp without time zone | N |  |  |
| 16 | `execution_plan` | jsonb | Y |  |  |
| 17 | `trade_history` | jsonb | Y |  |  |
| 18 | `equity_curve` | jsonb | Y |  |  |
| 19 | `status` | character varying(9) | N |  |  |
| 20 | `error_message` | text | Y |  |  |
| 21 | `executed_at` | timestamp without time zone | Y |  | now() |
| 22 | `completed_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `backtests_pkey`

---

#### `scalping_features_daily` [공통]

행 수: 45 | 크기: 88 kB | 최신: 2026-02-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('scalping_features_dai |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `feature_date` | date | N |  |  |
| 4 | `avg_spread_pct` | real | Y |  | 0 |
| 5 | `avg_imbalance` | real | Y |  | 0 |
| 6 | `avg_volume_delta` | real | Y |  | 0 |
| 7 | `avg_change_rate` | real | Y |  | 0 |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `scalping_features_daily_pkey`
- `scalping_features_daily_stock_code_feature_date_key`
- `uidx_scalping_features_code_date`

---


### [ETC]

#### `go100_agent_experience_log` [GO100]

행 수: 1 | 크기: 88 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_agent_experienc |
| 2 | `user_id` | integer | N |  |  |
| 3 | `event_type` | character varying(50) | N |  |  |
| 4 | `context` | jsonb | Y |  | '{}'::jsonb |
| 5 | `action` | jsonb | Y |  | '{}'::jsonb |
| 6 | `outcome` | jsonb | Y |  | '{}'::jsonb |
| 7 | `confidence` | double precision | Y |  | 0 |
| 8 | `notes` | text | Y |  |  |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_agent_experience_log_pkey`
- `idx_agent_exp_event`
- `idx_agent_exp_user_date`
- `idx_agent_exp_context`

---

#### `go100_agent_performance` [GO100]

행 수: 81 | 크기: 104 kB | 최신: 2026-03-07

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_agent_performan |
| 2 | `eval_date` | date | N |  |  |
| 3 | `agent_name` | character varying(50) | N |  |  |
| 4 | `total_signals` | integer | N |  | 0 |
| 5 | `correct_signals` | integer | N |  | 0 |
| 6 | `accuracy` | numeric | Y |  |  |
| 7 | `contribution_score` | numeric | Y |  |  |
| 8 | `weight_adjustment` | numeric | Y |  |  |
| 9 | `created_at` | timestamp with time zone | N |  | now() |
| 10 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_agent_performance_pkey`
- `idx_go100_agent_perf_date_agent`
- `idx_go100_agent_performance_user_id`

---

#### `go100_agent_self_review` [GO100]

행 수: 2 | 크기: 80 kB | 최신: 2026-02-16

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `review_id` | integer | N | PK | nextval('go100_agent_self_revi |
| 2 | `review_period` | character varying(20) | N |  |  |
| 3 | `period_start` | date | N |  |  |
| 4 | `period_end` | date | N |  |  |
| 5 | `total_recommendations` | integer | Y |  |  |
| 6 | `successful_recommendations` | integer | Y |  |  |
| 7 | `accuracy_rate` | numeric | Y |  |  |
| 8 | `strategy_performance` | jsonb | Y |  |  |
| 9 | `user_feedback_summary` | jsonb | Y |  |  |
| 10 | `improvement_suggestions` | jsonb | Y |  |  |
| 11 | `model_used` | character varying(50) | Y |  |  |
| 12 | `raw_analysis` | text | Y |  |  |
| 13 | `created_at` | timestamp with time zone | Y |  | now() |
| 14 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_agent_self_review_pkey`
- `idx_self_review_period`
- `idx_self_review_created`
- `idx_go100_agent_self_review_user_id`

---

#### `go100_ai_predictions` [GO100]

행 수: 506 | 크기: 504 kB | 최신: 2026-03-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_ai_predictions_ |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `predicted_date` | date | N |  |  |
| 4 | `clf_prob_up` | numeric | N |  | 0.0 |
| 5 | `mfe_60min_pred` | numeric | N |  | 0.0 |
| 6 | `mfe_3d_pred` | numeric | N |  | 0.0 |
| 7 | `gap_d1_pred` | numeric | N |  | 0.0 |
| 8 | `conviction_score` | numeric | N |  | 0.0 |
| 9 | `regime_used` | character varying(20) | N |  | 'unified'::character varying |
| 10 | `model_version` | character varying(10) | N |  | 'v3'::character varying |
| 11 | `created_at` | timestamp with time zone | N |  | now() |
| 12 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_ai_predictions_pkey`
- `go100_ai_predictions_stock_code_predicted_date_key`
- `idx_go100_ai_predictions_date`
- `idx_go100_ai_predictions_conviction`
- `idx_go100_ai_predictions_stock`
- `idx_go100_ai_pred_date`
- `idx_go100_ai_pred_stock_date`
- `idx_go100_ai_pred_conviction`
- `idx_go100_ai_predictions_user_id`

---

#### `go100_commander_decisions` [GO100]

행 수: 0 | 크기: 40 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_commander_decis |
| 2 | `session_date` | date | N |  |  |
| 3 | `decision_type` | character varying(20) | N |  |  |
| 4 | `ticker` | character varying(20) | Y |  |  |
| 5 | `agent_scores` | jsonb | Y |  |  |
| 6 | `weighted_score` | numeric | Y |  |  |
| 7 | `conviction` | numeric | Y |  |  |
| 8 | `reasoning` | text | Y |  |  |
| 9 | `action_taken` | boolean | Y |  | false |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |
| 11 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_commander_decisions_pkey`
- `idx_commander_decisions_date`
- `idx_commander_decisions_ticker`
- `idx_go100_commander_decisions_user_id`

---

#### `go100_data_integrity_log` [GO100]

행 수: 134,117 | 크기: 32 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_data_integrity_ |
| 2 | `check_time` | timestamp with time zone | N |  | now() |
| 3 | `check_type` | character varying(50) | N |  |  |
| 4 | `target_table` | character varying(100) | N |  |  |
| 5 | `expected_value` | text | Y |  |  |
| 6 | `actual_value` | text | Y |  |  |
| 7 | `is_pass` | boolean | N |  |  |
| 8 | `severity` | character varying(20) | N |  | 'WARNING'::character varying |
| 9 | `message` | text | Y |  |  |
| 10 | `resolved_at` | timestamp with time zone | Y |  |  |
| 11 | `resolved_by` | character varying(50) | Y |  |  |

**인덱스:**

- `go100_data_integrity_log_pkey`
- `idx_integrity_log_time`
- `idx_integrity_log_fail`

---

#### `go100_debate_log` [GO100]

행 수: 5 | 크기: 64 kB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_debate_log_id_s |
| 2 | `debate_date` | date | N |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `round_num` | integer | N |  | 1 |
| 5 | `bull_argument` | text | Y |  |  |
| 6 | `bear_argument` | text | Y |  |  |
| 7 | `winner` | character varying(10) | Y |  |  |
| 8 | `commander_decision` | character varying(20) | Y |  |  |
| 9 | `created_at` | timestamp with time zone | N |  | now() |
| 10 | `bull_confidence` | integer | Y |  |  |
| 11 | `bear_confidence` | integer | Y |  |  |
| 12 | `bull_key_evidence` | text | Y |  |  |
| 13 | `bear_key_evidence` | text | Y |  |  |
| 14 | `debate_elapsed_sec` | numeric | Y |  | NULL::numeric |

**인덱스:**

- `go100_debate_log_pkey`
- `idx_go100_debate_log_date_stock`

---

#### `go100_derivatives_daily` [GO100]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_derivatives_dai |
| 2 | `trade_date` | date | N |  |  |
| 3 | `product` | character varying(50) | N |  |  |
| 4 | `basis` | double precision | Y |  |  |
| 5 | `open_interest` | bigint | Y |  |  |
| 6 | `foreign_net` | bigint | Y |  |  |
| 7 | `institution_net` | bigint | Y |  |  |
| 8 | `put_call_ratio` | double precision | Y |  |  |
| 9 | `iv_skew` | double precision | Y |  |  |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_derivatives_daily_pkey`
- `go100_derivatives_daily_trade_date_product_key`

---

#### `go100_desk_allocation` [GO100]

행 수: 2 | 크기: 64 kB | 최신: 2026-02-21

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_desk_allocation |
| 2 | `user_id` | integer | N |  |  |
| 3 | `total_capital` | numeric | N |  |  |
| 4 | `card_allocations` | jsonb | N |  |  |
| 5 | `overlap_resolved` | jsonb | Y |  |  |
| 6 | `portfolio_metrics` | jsonb | Y |  |  |
| 7 | `period_days` | integer | Y |  |  |
| 8 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_desk_allocation_pkey`

---

#### `go100_episodic_memory` [GO100]

행 수: 1 | 크기: 96 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `episode_id` | bigint | N | PK | nextval('go100_episodic_memory |
| 2 | `user_id` | integer | N |  |  |
| 3 | `session_id` | character varying(100) | N |  |  |
| 4 | `episode_date` | date | N |  | CURRENT_DATE |
| 5 | `summary` | text | N |  |  |
| 6 | `key_decisions` | jsonb | Y |  | '[]'::jsonb |
| 7 | `mentioned_stocks` | ARRAY | Y |  | '{}'::character varying[] |
| 8 | `mentioned_stock_names` | ARRAY | Y |  | '{}'::character varying[] |
| 9 | `topics` | ARRAY | Y |  | '{}'::character varying[] |
| 10 | `user_sentiment` | character varying(20) | Y |  | 'NEUTRAL'::character varying |
| 11 | `data_context` | jsonb | Y |  | '{}'::jsonb |
| 12 | `turn_count` | integer | Y |  | 0 |
| 13 | `tools_used` | ARRAY | Y |  | '{}'::character varying[] |
| 14 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_episodic_memory_pkey`
- `idx_episodic_user_date`
- `idx_episodic_stocks`
- `idx_episodic_topics`

---

#### `go100_error_log` [GO100]

행 수: 249 | 크기: 584 kB | 최신: 2026-03-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_error_log_id_se |
| 2 | `endpoint` | text | Y |  |  |
| 3 | `status_code` | integer | Y |  |  |
| 4 | `error_message` | text | Y |  |  |
| 5 | `traceback` | text | Y |  |  |
| 6 | `request_body` | jsonb | Y |  |  |
| 7 | `created_at` | timestamp with time zone | Y |  | now() |
| 8 | `error_type` | character varying(100) | Y |  |  |
| 9 | `error_category` | character varying(50) | Y |  | 'SYSTEM'::character varying |
| 10 | `auto_resolved` | boolean | Y |  | false |
| 11 | `resolution_detail` | jsonb | Y |  |  |

**인덱스:**

- `go100_error_log_pkey`
- `idx_go100_error_log_created_at`
- `idx_go100_error_log_status_code`

---

#### `go100_events` [GO100]

행 수: 25 | 크기: 96 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `event_id` | integer | N | PK | nextval('go100_events_event_id |
| 2 | `ticker` | character varying(20) | Y |  |  |
| 3 | `event_type` | character varying(50) | N |  |  |
| 4 | `event_date` | date | N |  |  |
| 5 | `title` | text | N |  |  |
| 6 | `content` | text | Y |  |  |
| 7 | `source` | character varying(50) | Y |  |  |
| 8 | `impact_score` | numeric | Y |  |  |
| 9 | `related_strategy_ids` | ARRAY | Y |  |  |
| 10 | `raw_data` | jsonb | Y |  |  |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_events_pkey`
- `idx_events_ticker_date`
- `idx_events_date`

---

#### `go100_evolution_loops` [GO100]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_evolution_loops |
| 2 | `loop_seq` | integer | N |  | 1 |
| 3 | `hypothesis_id` | integer | Y |  |  |
| 4 | `round_num` | integer | N |  | 1 |
| 5 | `round_status` | character varying(50) | Y |  | 'running'::character varying |
| 6 | `pf` | numeric | Y |  |  |
| 7 | `sharpe` | numeric | Y |  |  |
| 8 | `mdd` | numeric | Y |  |  |
| 9 | `win_rate` | numeric | Y |  |  |
| 10 | `total_trades` | integer | Y |  |  |
| 11 | `wf_validated` | boolean | Y |  | false |
| 12 | `profiler_result` | jsonb | Y |  |  |
| 13 | `analyst_result` | jsonb | Y |  |  |
| 14 | `revised_hypothesis` | jsonb | Y |  |  |
| 15 | `notes` | text | Y |  |  |
| 16 | `created_at` | timestamp with time zone | Y |  | now() |
| 17 | `updated_at` | timestamp with time zone | Y |  | now() |
| 18 | `validator_result` | jsonb | Y |  | '{}'::jsonb |
| 19 | `validator_grade` | character varying(2) | Y |  | NULL::character varying |

**인덱스:**

- `go100_evolution_loops_pkey`

---

#### `go100_experience_log` [GO100]

행 수: 0 | 크기: 40 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_experience_log_ |
| 2 | `source` | character varying(20) | N |  | 'backtest'::character varying |
| 3 | `strategy_card_id` | integer | Y |  |  |
| 4 | `stock_code` | character varying(20) | Y |  |  |
| 5 | `action` | character varying(20) | Y |  |  |
| 6 | `entry_date` | date | Y |  |  |
| 7 | `exit_date` | date | Y |  |  |
| 8 | `entry_price` | numeric | Y |  |  |
| 9 | `exit_price` | numeric | Y |  |  |
| 10 | `return_pct` | numeric | Y |  |  |
| 11 | `regime` | character varying(20) | Y |  |  |
| 12 | `sector` | character varying(50) | Y |  |  |
| 13 | `market_snapshot` | jsonb | Y |  |  |
| 14 | `slippage_expected` | numeric | Y |  |  |
| 15 | `slippage_actual` | numeric | Y |  |  |
| 16 | `fill_rate` | numeric | Y |  |  |
| 17 | `time_to_fill_sec` | integer | Y |  |  |
| 18 | `overnight_gap_pct` | numeric | Y |  |  |
| 19 | `volume_participation_pct` | numeric | Y |  |  |
| 20 | `market_impact_pct` | numeric | Y |  |  |
| 21 | `notes` | text | Y |  |  |
| 22 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_experience_log_pkey`
- `idx_exp_log_source`
- `idx_exp_log_stock`
- `idx_exp_log_date`

---

#### `go100_gap_analysis` [GO100]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_gap_analysis_id |
| 2 | `strategy_card_id` | integer | Y |  |  |
| 3 | `period_start` | date | Y |  |  |
| 4 | `period_end` | date | Y |  |  |
| 5 | `backtest_return` | numeric | Y |  |  |
| 6 | `paper_return` | numeric | Y |  |  |
| 7 | `live_return` | numeric | Y |  |  |
| 8 | `gap_pct` | numeric | Y |  |  |
| 9 | `gap_source` | character varying(50) | Y |  |  |
| 10 | `details` | jsonb | Y |  |  |
| 11 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_gap_analysis_pkey`

---

#### `go100_goals` [GO100]

행 수: 6 | 크기: 72 kB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `goal_id` | bigint | N | PK | nextval('go100_goals_goal_id_s |
| 2 | `user_id` | integer | N |  |  |
| 3 | `goal_name` | character varying(200) | Y |  |  |
| 4 | `initial_capital` | numeric | N |  |  |
| 5 | `target_capital` | numeric | N |  |  |
| 6 | `target_years` | integer | N |  |  |
| 7 | `required_cagr` | numeric | Y |  |  |
| 8 | `risk_appetite` | character varying(20) | Y |  |  |
| 9 | `plan_phases` | jsonb | Y |  |  |
| 10 | `monte_carlo_result` | jsonb | Y |  |  |
| 11 | `current_phase` | integer | Y |  | 1 |
| 12 | `current_capital` | numeric | Y |  |  |
| 13 | `progress_pct` | numeric | Y |  | 0 |
| 14 | `strategy_portfolio_id` | bigint | Y |  |  |
| 15 | `status` | character varying(20) | Y |  | 'PLANNING'::character varying |
| 16 | `created_at` | timestamp with time zone | Y |  | now() |
| 17 | `updated_at` | timestamp with time zone | Y |  | now() |
| 18 | `scenarios` | jsonb | Y |  |  |
| 19 | `recommended_strategies` | jsonb | Y |  |  |

**인덱스:**

- `go100_goals_pkey`

---

#### `go100_live_daily_summary` [GO100]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `summary_id` | integer | N | PK | nextval('go100_live_daily_summ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `summary_date` | date | N |  |  |
| 4 | `total_orders` | integer | Y |  | 0 |
| 5 | `total_buy_amount` | bigint | Y |  | 0 |
| 6 | `total_sell_amount` | bigint | Y |  | 0 |
| 7 | `realized_pnl` | bigint | Y |  | 0 |
| 8 | `realized_pnl_pct` | real | Y |  | 0 |
| 9 | `is_circuit_broken` | boolean | Y |  | false |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_live_daily_summary_pkey`
- `go100_live_daily_summary_user_id_summary_date_key`

---

#### `go100_paper_archive` [GO100]

행 수: 0 | 크기: 48 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_paper_archive_i |
| 2 | `source` | character varying(30) | N |  |  |
| 3 | `paper_id` | character varying(100) | N |  |  |
| 4 | `title` | text | N |  |  |
| 5 | `authors` | ARRAY | Y |  | '{}'::text[] |
| 6 | `abstract` | text | Y |  |  |
| 7 | `published_date` | date | Y |  |  |
| 8 | `categories` | ARRAY | Y |  | '{}'::text[] |
| 9 | `citation_count` | integer | Y |  | 0 |
| 10 | `relevance_score` | integer | Y |  | 0 |
| 11 | `extracted_hypotheses` | jsonb | Y |  | '[]'::jsonb |
| 12 | `processed` | boolean | Y |  | false |
| 13 | `added_date` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_paper_archive_pkey`
- `idx_pa_source_paperid`
- `idx_pa_processed`
- `idx_pa_relevance`
- `idx_pa_added_date`

---

#### `go100_paper_snapshots` [GO100]

행 수: 380 | 크기: 120 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `snapshot_id` | integer | N | PK | nextval('go100_paper_snapshots |
| 2 | `account_id` | integer | N |  |  |
| 3 | `snapshot_date` | date | N |  |  |
| 4 | `total_value` | bigint | Y |  |  |
| 5 | `cash` | bigint | Y |  |  |
| 6 | `positions_value` | bigint | Y |  |  |
| 7 | `daily_pnl` | bigint | Y |  |  |
| 8 | `daily_pnl_pct` | real | Y |  |  |
| 9 | `cumulative_pnl_pct` | real | Y |  |  |
| 10 | `drawdown_pct` | real | Y |  |  |
| 11 | `peak_value` | bigint | Y |  |  |
| 12 | `position_count` | integer | Y |  |  |

**인덱스:**

- `go100_paper_snapshots_pkey`
- `go100_paper_snapshots_account_id_snapshot_date_key`
- `idx_go100_paper_snapshots_account_date`

---

#### `go100_portfolio_allocations` [GO100]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `allocation_id` | integer | N | PK | nextval('go100_portfolio_alloc |
| 2 | `portfolio_id` | integer | N |  |  |
| 3 | `card_id` | bigint | N |  |  |
| 4 | `allocation_pct` | real | N |  |  |
| 5 | `allocation_amount` | bigint | N |  |  |
| 6 | `strategy_type` | character varying(30) | Y |  |  |
| 7 | `max_mdd_limit` | real | Y |  |  |
| 8 | `is_active` | boolean | Y |  | true |
| 9 | `created_at` | timestamp without time zone | Y |  | now() |
| 10 | `updated_at` | timestamp without time zone | Y |  | now() |
| 11 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_portfolio_allocations_pkey`
- `idx_go100_portfolio_allocations_portfolio`
- `idx_go100_portfolio_allocations_port_card`
- `idx_go100_portfolio_allocations_user_id`

---

#### `go100_portfolio_snapshots` [GO100]

행 수: 96 | 크기: 112 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_portfolio_snaps |
| 2 | `portfolio_id` | bigint | N |  |  |
| 3 | `snapshot_date` | date | N |  |  |
| 4 | `total_equity` | numeric | Y |  |  |
| 5 | `current_cash` | numeric | Y |  |  |
| 6 | `total_invested` | numeric | Y |  |  |
| 7 | `total_eval` | numeric | Y |  |  |
| 8 | `open_positions` | integer | Y |  | 0 |
| 9 | `daily_pnl` | numeric | Y |  |  |
| 10 | `total_return_pct` | numeric | Y |  |  |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |
| 12 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_portfolio_snapshots_pkey`
- `go100_portfolio_snapshots_portfolio_id_snapshot_date_key`
- `idx_go100_snapshots_portfolio`
- `idx_go100_portfolio_snapshots_user_id`

---

#### `go100_portfolios` [GO100]

행 수: 6 | 크기: 88 kB | 최신: 2026-03-06

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `portfolio_id` | bigint | N | PK | nextval('go100_portfolios_port |
| 2 | `user_id` | integer | N |  |  |
| 3 | `account_id` | integer | Y |  |  |
| 4 | `go100_card_id` | bigint | N |  |  |
| 5 | `initial_capital` | numeric | N |  |  |
| 6 | `current_cash` | numeric | N |  |  |
| 7 | `total_invested` | numeric | Y |  | 0 |
| 8 | `total_eval` | numeric | Y |  | 0 |
| 9 | `is_paper` | boolean | Y |  | true |
| 10 | `status` | character varying(20) | Y |  | 'ACTIVE'::character varying |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |
| 12 | `updated_at` | timestamp with time zone | Y |  | now() |
| 13 | `is_live` | boolean | Y |  | false |
| 14 | `risk_tolerance` | character varying(20) | Y |  | 'medium'::character varying |
| 15 | `last_run_date` | date | Y |  |  |

**인덱스:**

- `go100_portfolios_pkey`
- `idx_go100_port_user`
- `idx_go100_port_card`

---

#### `go100_program_trading_daily` [GO100]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_program_trading |
| 2 | `trade_date` | date | N |  |  |
| 3 | `market` | character varying(20) | N |  |  |
| 4 | `arbitrage_buy` | bigint | Y |  |  |
| 5 | `arbitrage_sell` | bigint | Y |  |  |
| 6 | `non_arbitrage_buy` | bigint | Y |  |  |
| 7 | `non_arbitrage_sell` | bigint | Y |  |  |
| 8 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_program_trading_daily_pkey`
- `go100_program_trading_daily_trade_date_market_key`

---

#### `go100_research_iterations` [GO100]

행 수: 3 | 크기: 64 kB | 최신: 2026-03-06

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_research_iterat |
| 2 | `hypothesis_id` | integer | Y |  |  |
| 3 | `iteration_num` | integer | N |  | 1 |
| 4 | `phase` | character varying(30) | N |  | 'data-refresh'::character vary |
| 5 | `params` | jsonb | N |  | '{}'::jsonb |
| 6 | `result` | jsonb | N |  | '{}'::jsonb |
| 7 | `profit_factor` | numeric | Y |  |  |
| 8 | `win_rate` | numeric | Y |  |  |
| 9 | `max_drawdown` | numeric | Y |  |  |
| 10 | `total_trades` | integer | Y |  |  |
| 11 | `converge_status` | character varying(20) | Y |  | 'IMPROVING'::character varying |
| 12 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_research_iterations_pkey`
- `idx_research_iters_hypothesis`
- `idx_research_iters_converge`

---

#### `go100_short_selling_daily` [GO100]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_short_selling_d |
| 2 | `trade_date` | date | N |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `short_volume` | bigint | Y |  |  |
| 5 | `short_balance` | bigint | Y |  |  |
| 6 | `short_ratio` | double precision | Y |  |  |
| 7 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_short_selling_daily_pkey`
- `go100_short_selling_daily_trade_date_stock_code_key`

---

#### `go100_stock_profiles` [GO100]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_stock_profiles_ |
| 2 | `evolution_loop_id` | integer | Y |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `stock_type` | character varying(10) | Y |  |  |
| 6 | `market_cap` | bigint | Y |  |  |
| 7 | `volatility_20d` | numeric | Y |  |  |
| 8 | `ma_aligned` | boolean | Y |  |  |
| 9 | `high52w_proximity` | numeric | Y |  |  |
| 10 | `foreign_net_5d` | bigint | Y |  |  |
| 11 | `inst_net_5d` | bigint | Y |  |  |
| 12 | `foreign_net_20d` | bigint | Y |  |  |
| 13 | `inst_net_20d` | bigint | Y |  |  |
| 14 | `news_7d_count` | integer | Y |  | 0 |
| 15 | `desk_path` | character varying(50) | Y |  |  |
| 16 | `pnl_pct` | numeric | Y |  |  |
| 17 | `is_winner` | boolean | Y |  |  |
| 18 | `entry_date` | date | Y |  |  |
| 19 | `profile_data` | jsonb | Y |  |  |
| 20 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_stock_profiles_pkey`

---

#### `go100_trading_cost_params` [GO100]

행 수: 3 | 크기: 40 kB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_trading_cost_pa |
| 2 | `broker` | character varying(20) | N |  |  |
| 3 | `account_type` | character varying(20) | Y |  |  |
| 4 | `commission_buy` | numeric | Y |  | 0.00015 |
| 5 | `commission_sell` | numeric | Y |  | 0.00015 |
| 6 | `tax_sell` | numeric | Y |  | 0.0018 |
| 7 | `slippage_default` | numeric | Y |  | 0.001 |
| 8 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_trading_cost_params_pkey`
- `go100_trading_cost_params_broker_account_type_key`

---

#### `v4_bet_history` [V4.1]

행 수: 0 | 크기: 8192 bytes

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_bet_history_id_seq |
| 2 | `user_id` | integer | N |  |  |
| 3 | `ticker` | character varying(20) | Y |  |  |
| 4 | `desk_id` | integer | Y |  |  |
| 5 | `universe_score` | numeric | Y |  |  |
| 6 | `base_bet` | bigint | Y |  |  |
| 7 | `mood_modifier` | numeric | Y |  |  |
| 8 | `regime_modifier` | numeric | Y |  |  |
| 9 | `streak_modifier` | numeric | Y |  |  |
| 10 | `calendar_modifier` | numeric | Y |  |  |
| 11 | `risk_cap` | bigint | Y |  |  |
| 12 | `final_bet` | bigint | Y |  |  |
| 13 | `confidence` | character varying(10) | Y |  |  |
| 14 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_bet_history_pkey`

---

#### `v4_compound_growth_daily` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_compound_growth_da |
| 2 | `date` | date | N |  |  |
| 3 | `total_capital` | bigint | N |  | 0 |
| 4 | `stage` | integer | N |  | 1 |
| 5 | `cvr` | numeric | Y |  | 0 |
| 6 | `cir` | numeric | Y |  | 0 |
| 7 | `cgr` | numeric | Y |  | 0 |
| 8 | `node_hit_rate` | numeric | Y |  | 0 |
| 9 | `pcr` | numeric | Y |  | 0 |
| 10 | `daily_pnl_pct` | numeric | Y |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_compound_growth_daily_pkey`
- `v4_compound_growth_daily_date_key`
- `idx_compound_growth_date`

---

#### `v4_daily_portfolio` [V4.1]

행 수: 35 | 크기: 80 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_daily_portfolio_id |
| 2 | `snapshot_date` | date | N |  |  |
| 3 | `total_asset` | numeric | N |  |  |
| 4 | `cash_balance` | numeric | N |  |  |
| 5 | `holding_value` | numeric | N |  |  |
| 6 | `daily_pnl` | numeric | Y |  | 0 |
| 7 | `daily_pnl_pct` | numeric | Y |  | 0 |
| 8 | `cumulative_pnl` | numeric | Y |  | 0 |
| 9 | `cumulative_pct` | numeric | Y |  | 0 |
| 10 | `current_stage` | integer | N |  | 1 |
| 11 | `stage_changed` | boolean | Y |  | false |
| 12 | `desk_allocation` | jsonb | Y |  |  |
| 13 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_daily_portfolio_pkey`
- `v4_daily_portfolio_snapshot_date_key`

---

#### `v4_desk1_candidates` [V4.1]

행 수: 50 | 크기: 56 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk1_candidates_i |
| 2 | `target_date` | date | N |  | CURRENT_DATE |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `stock_name` | character varying(50) | Y |  |  |
| 5 | `confidence` | integer | N |  | 0 |
| 6 | `price_change_pct` | numeric | Y |  |  |
| 7 | `volume_ratio` | numeric | Y |  |  |
| 8 | `kill_zone` | boolean | Y |  | false |
| 9 | `market_type` | character varying(10) | Y |  | 'KOSDAQ'::character varying |
| 10 | `market_cap` | bigint | Y |  |  |
| 11 | `entry_price` | numeric | Y |  |  |
| 12 | `stop_loss` | numeric | Y |  |  |
| 13 | `target_price` | numeric | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk1_candidates_pkey`
- `idx_desk1_cand_date`
- `idx_desk1_cand_stock`

---

#### `v4_desk2_candidates` [V4.1]

행 수: 2,348 | 크기: 888 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk2_candidates_i |
| 2 | `target_date` | date | N |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `stock_name` | character varying(50) | Y |  |  |
| 5 | `score` | numeric | N |  |  |
| 6 | `score_rank` | integer | N |  |  |
| 7 | `f3_vol_ratio` | numeric | Y |  |  |
| 8 | `f2_vol_change` | numeric | Y |  |  |
| 9 | `f1_news_count` | integer | Y |  |  |
| 10 | `f4_close_pos` | numeric | Y |  |  |
| 11 | `market_cap` | bigint | Y |  |  |
| 12 | `sector` | character varying(100) | Y |  |  |
| 13 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk2_candidates_pkey`
- `v4_desk2_candidates_target_date_stock_code_key`
- `idx_desk2_cand_date`
- `idx_v4_desk2_cand_code`
- `idx_v4_desk2_cand_status`
- `idx_desk2_cand_stock`

---

#### `v4_desk2_daily_summary` [V4.1]

행 수: 1 | 크기: 40 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk2_daily_summar |
| 2 | `trade_date` | date | N |  |  |
| 3 | `total_trades` | integer | Y |  |  |
| 4 | `win_count` | integer | Y |  |  |
| 5 | `loss_count` | integer | Y |  |  |
| 6 | `win_rate` | numeric | Y |  |  |
| 7 | `gross_pnl` | numeric | Y |  |  |
| 8 | `net_pnl` | numeric | Y |  |  |
| 9 | `avg_pnl_pct` | numeric | Y |  |  |
| 10 | `max_loss_pct` | numeric | Y |  |  |
| 11 | `trend_count` | integer | Y |  |  |
| 12 | `reversal_count` | integer | Y |  |  |
| 13 | `border_count` | integer | Y |  |  |
| 14 | `market_regime` | character varying(10) | Y |  |  |
| 15 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk2_daily_summary_pkey`
- `v4_desk2_daily_summary_trade_date_key`

---

#### `v4_desk3_explosion_log` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk3_explosion_lo |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `trigger_type` | character varying(50) | Y |  |  |
| 5 | `change_pct` | numeric | Y |  |  |
| 6 | `volume_ratio` | numeric | Y |  |  |
| 7 | `detected_at` | timestamp without time zone | Y |  | now() |
| 8 | `action_taken` | character varying(50) | Y |  |  |

**인덱스:**

- `v4_desk3_explosion_log_pkey`
- `idx_v4_desk3_code`

---

#### `v4_desk3_explosion_watch` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk3_explosion_wa |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `trigger_type` | character varying(50) | Y |  |  |
| 5 | `score` | numeric | Y |  |  |
| 6 | `volume_surge_ratio` | numeric | Y |  |  |
| 7 | `price_change_pct` | numeric | Y |  |  |
| 8 | `sector_surge` | boolean | Y |  | false |
| 9 | `news_flag` | boolean | Y |  | false |
| 10 | `detected_at` | timestamp without time zone | Y |  | now() |
| 11 | `status` | character varying(20) | Y |  | 'watching'::character varying |
| 12 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk3_explosion_watch_pkey`
- `idx_desk3_stock`

---

#### `v4_desk3_pool` [V4.1]

행 수: 1,213 | 크기: 776 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk3_pool_id_seq' |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `market` | character varying(10) | Y |  |  |
| 5 | `sector_code` | character varying(20) | Y |  |  |
| 6 | `sector_name` | character varying(100) | Y |  |  |
| 7 | `pool_entry_date` | date | N |  |  |
| 8 | `pool_exit_date` | date | Y |  |  |
| 9 | `status` | character varying(20) | Y |  | 'ACTIVE'::character varying |
| 10 | `total_score` | numeric | Y |  |  |
| 11 | `layer1_structure` | numeric | Y |  | 0 |
| 12 | `layer2_supply_demand` | numeric | Y |  | 0 |
| 13 | `layer3_market_attention` | numeric | Y |  | 0 |
| 14 | `layer4_repeat_pattern` | numeric | Y |  | 0 |
| 15 | `layer5_sequence` | numeric | Y |  | 0 |
| 16 | `consecutive_below_days` | integer | Y |  | 0 |
| 17 | `dwell_days` | integer | Y |  | 0 |
| 18 | `max_dwell_days` | integer | Y |  | 10 |
| 19 | `exit_reason` | character varying(50) | Y |  |  |
| 20 | `source` | character varying(20) | Y |  | 'SCAN'::character varying |
| 21 | `promoted_from` | character varying(20) | Y |  |  |
| 22 | `promoted_to` | character varying(20) | Y |  |  |
| 23 | `promotion_date` | date | Y |  |  |
| 24 | `confidence_boost` | numeric | Y |  | 0 |
| 25 | `theme_cycle_score` | numeric | Y |  | 0 |
| 26 | `dual_flow_score` | numeric | Y |  | 0 |
| 27 | `force_acc_score` | numeric | Y |  | 0 |
| 28 | `sec_leader_flag` | boolean | Y |  | false |
| 29 | `created_at` | timestamp with time zone | Y |  | now() |
| 30 | `updated_at` | timestamp with time zone | Y |  | now() |
| 31 | `growth_axis2` | character varying(20) | Y |  | 'NONE'::character varying |
| 32 | `growth_score_adj` | numeric | Y |  | 0 |

**인덱스:**

- `v4_desk3_pool_pkey`
- `v4_desk3_pool_stock_code_pool_entry_date_key`
- `idx_desk3_pool_status`
- `idx_desk3_pool_date`
- `idx_desk3_pool_score`
- `idx_desk3_pool_sector`

---

#### `v4_desk4_harvest_log` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk4_harvest_log_ |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `trigger_type` | character varying(50) | Y |  |  |
| 5 | `ma_alignment_score` | numeric | Y |  |  |
| 6 | `sector` | character varying(50) | Y |  |  |
| 7 | `detected_at` | timestamp without time zone | Y |  | now() |
| 8 | `status` | character varying(20) | Y |  | 'watching'::character varying |

**인덱스:**

- `v4_desk4_harvest_log_pkey`
- `idx_v4_desk4_code`

---

#### `v4_desk4_harvest_pool` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk4_harvest_pool |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `trigger_type` | character varying(50) | Y |  |  |
| 5 | `ma_aligned` | boolean | Y |  | false |
| 6 | `near_high` | boolean | Y |  | false |
| 7 | `sector_leader` | boolean | Y |  | false |
| 8 | `score` | numeric | Y |  |  |
| 9 | `detected_at` | timestamp without time zone | Y |  | now() |
| 10 | `status` | character varying(20) | Y |  | 'pool'::character varying |
| 11 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk4_harvest_pool_pkey`
- `idx_desk4_stock`

---

#### `v4_desk4_watchlist` [V4.1]

행 수: 38 | 크기: 88 kB | 최신: 2026-03-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk4_watchlist_id |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `scan_date` | date | N |  |  |
| 5 | `status` | character varying(20) | Y |  | 'WATCHING'::character varying |
| 6 | `total_score` | numeric | Y |  |  |
| 7 | `ma_growth_score` | numeric | Y |  |  |
| 8 | `box_squeeze_score` | numeric | Y |  |  |
| 9 | `staircase_score` | numeric | Y |  |  |
| 10 | `mid_supply_score` | numeric | Y |  |  |
| 11 | `catalyst_score` | numeric | Y |  |  |
| 12 | `trigger_t4_1` | boolean | Y |  | false |
| 13 | `trigger_t4_2` | boolean | Y |  | false |
| 14 | `trigger_t4_3` | boolean | Y |  | false |
| 15 | `trigger_t4_4` | boolean | Y |  | false |
| 16 | `triggers_met` | integer | Y |  | 0 |
| 17 | `promoted_from_desk5` | boolean | Y |  | false |
| 18 | `desk5_position_id` | integer | Y |  |  |
| 19 | `created_at` | timestamp with time zone | Y |  | now() |
| 20 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_desk4_watchlist_pkey`
- `v4_desk4_watchlist_stock_code_scan_date_key`
- `idx_desk4_watch_status`

---

#### `v4_desk5_watchlist` [V4.1]

행 수: 59 | 크기: 104 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk5_watchlist_id |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `scan_date` | date | N |  |  |
| 5 | `status` | character varying(20) | Y |  | 'WATCHING'::character varying |
| 6 | `bottom_escape_score` | numeric | Y |  |  |
| 7 | `slow_accumulation_score` | numeric | Y |  |  |
| 8 | `ma_convergence_score` | numeric | Y |  |  |
| 9 | `structural_catalyst_score` | numeric | Y |  |  |
| 10 | `institutional_flow_score` | numeric | Y |  |  |
| 11 | `total_score` | numeric | Y |  |  |
| 12 | `trigger_t5_1` | boolean | Y |  | false |
| 13 | `trigger_t5_2` | boolean | Y |  | false |
| 14 | `trigger_t5_3` | boolean | Y |  | false |
| 15 | `triggers_met` | integer | Y |  | 0 |
| 16 | `theme_alive_flag` | character varying(10) | Y |  | 'ALIVE'::character varying |
| 17 | `theme_news_count_30d` | integer | Y |  | 0 |
| 18 | `weekly_ma20` | numeric | Y |  |  |
| 19 | `weekly_ma10` | numeric | Y |  |  |
| 20 | `weekly_close` | numeric | Y |  |  |
| 21 | `created_at` | timestamp with time zone | Y |  | now() |
| 22 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_desk5_watchlist_pkey`
- `v4_desk5_watchlist_stock_code_scan_date_key`
- `idx_desk5_watch_status`

---

#### `v4_desk5_weekly_review` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk5_weekly_revie |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `review_date` | date | N |  |  |
| 4 | `weekly_close` | numeric | Y |  |  |
| 5 | `weekly_ma20` | numeric | Y |  |  |
| 6 | `weekly_ma10` | numeric | Y |  |  |
| 7 | `weekly_volume` | bigint | Y |  |  |
| 8 | `weekly_volume_ma20` | bigint | Y |  |  |
| 9 | `ma20_break_weeks` | integer | Y |  | 0 |
| 10 | `theme_alive_flag` | character varying(10) | Y |  | 'ALIVE'::character varying |
| 11 | `theme_news_30d` | integer | Y |  | 0 |
| 12 | `cumulative_return_pct` | numeric | Y |  |  |
| 13 | `action` | character varying(20) | Y |  | 'HOLD'::character varying |

**인덱스:**

- `v4_desk5_weekly_review_pkey`
- `v4_desk5_weekly_review_stock_code_review_date_key`

---

#### `v4_desk_fund` [V4.1]

행 수: 5 | 크기: 120 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk_fund_id_seq': |
| 2 | `desk_id` | integer | N |  |  |
| 3 | `desk_name` | character varying(30) | Y |  |  |
| 4 | `allocation_pct` | numeric | N |  |  |
| 5 | `allocated_amount` | bigint | Y |  |  |
| 6 | `used_amount` | bigint | Y |  | 0 |
| 7 | `available_amount` | bigint | Y |  |  |
| 8 | `max_positions` | integer | Y |  |  |
| 9 | `current_positions` | integer | Y |  | 0 |
| 10 | `daily_loss_limit` | numeric | Y |  |  |
| 11 | `daily_loss_current` | numeric | Y |  | 0 |
| 12 | `updated_at` | timestamp with time zone | Y |  | now() |
| 13 | `user_id` | bigint | Y |  |  |
| 14 | `account_id` | bigint | Y |  |  |
| 15 | `card_id` | bigint | Y |  |  |

**인덱스:**

- `v4_desk_fund_pkey`
- `v4_desk_fund_desk_id_key`
- `idx_v4fund_user`
- `idx_v4fund_account`
- `idx_v4fund_card`

---

#### `v4_desk_portfolio_summary` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk_portfolio_sum |
| 2 | `summary_date` | date | N |  |  |
| 3 | `desk_level` | integer | N |  |  |
| 4 | `active_count` | integer | Y |  | 0 |
| 5 | `total_capital` | numeric | Y |  | 0 |
| 6 | `total_pnl_pct` | numeric | Y |  | 0 |
| 7 | `win_count` | integer | Y |  | 0 |
| 8 | `loss_count` | integer | Y |  | 0 |
| 9 | `risk_reward_ratio` | numeric | Y |  | 0 |
| 10 | `avg_holding_days` | numeric | Y |  | 0 |

**인덱스:**

- `v4_desk_portfolio_summary_pkey`
- `v4_desk_portfolio_summary_summary_date_desk_level_key`

---

#### `v4_desk_promotion_log` [V4.1]

행 수: 3 | 크기: 48 kB | 최신: 2026-03-19

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk_promotion_log |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `from_desk` | integer | N |  |  |
| 4 | `to_desk` | integer | N |  |  |
| 5 | `direction` | character varying(10) | N |  |  |
| 6 | `trigger_reason` | text | Y |  |  |
| 7 | `desk2_bonus_score` | numeric | Y |  | 0 |
| 8 | `promoted_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_desk_promotion_log_pkey`
- `idx_desk_promotion_log_stock`

---

#### `v4_evolution_candidates` [V4.1]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_evolution_candidat |
| 2 | `created_at` | timestamp without time zone | Y |  | now() |
| 3 | `stage` | character varying(20) | N |  | 'discovered'::character varyin |
| 4 | `source` | character varying(30) | Y |  |  |
| 5 | `params` | jsonb | Y |  |  |
| 6 | `pf` | numeric | Y |  |  |
| 7 | `sharpe` | numeric | Y |  |  |
| 8 | `max_dd` | numeric | Y |  |  |
| 9 | `win_rate` | numeric | Y |  |  |
| 10 | `trade_count` | integer | Y |  |  |
| 11 | `paper_start` | date | Y |  |  |
| 12 | `paper_end` | date | Y |  |  |
| 13 | `paper_dcs` | numeric | Y |  |  |
| 14 | `paper_win_days` | integer | Y |  |  |
| 15 | `paper_total_days` | integer | Y |  |  |
| 16 | `grade` | character varying(5) | Y |  |  |
| 17 | `live_start` | date | Y |  |  |
| 18 | `live_capital_pct` | numeric | Y |  |  |
| 19 | `hav_hypothesis_id` | character varying(30) | Y |  |  |
| 20 | `notes` | text | Y |  |  |

**인덱스:**

- `v4_evolution_candidates_pkey`
- `idx_evo_cand_stage`
- `idx_evo_cand_hav`

---

#### `v4_excluded_stocks` [V4.1]

행 수: 248 | 크기: 64 kB | 최신: 2026-03-18

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `stock_code` | character varying(10) | N | PK |  |
| 2 | `reason` | text | Y |  |  |
| 3 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_excluded_stocks_pkey`

---

#### `v4_fund_lending` [V4.1]

행 수: 63 | 크기: 88 kB | 최신: 2026-03-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `lending_id` | bigint | N | PK | nextval('v4_fund_lending_lendi |
| 2 | `from_desk_id` | integer | N |  |  |
| 3 | `to_desk_id` | integer | N |  |  |
| 4 | `amount` | numeric | N |  |  |
| 5 | `lending_reason` | character varying(50) | N |  |  |
| 6 | `status` | character varying(20) | N |  | 'ACTIVE'::character varying |
| 7 | `lent_at` | timestamp with time zone | Y |  | now() |
| 8 | `return_by` | timestamp with time zone | N |  |  |
| 9 | `returned_at` | timestamp with time zone | Y |  |  |
| 10 | `returned_amount` | numeric | Y |  |  |

**인덱스:**

- `v4_fund_lending_pkey`
- `idx_v4_fl_status`
- `idx_v4_fl_return`

---

#### `v4_fund_pool_snapshot` [V4.1]

행 수: 1 | 크기: 56 kB | 최신: 2026-02-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_fund_pool_snapshot |
| 2 | `user_id` | integer | N |  |  |
| 3 | `total_capital` | bigint | Y |  |  |
| 4 | `available` | bigint | Y |  |  |
| 5 | `reserved` | bigint | Y |  |  |
| 6 | `invested` | bigint | Y |  |  |
| 7 | `desk1_used` | bigint | Y |  |  |
| 8 | `desk2_used` | bigint | Y |  |  |
| 9 | `desk3_used` | bigint | Y |  |  |
| 10 | `desk4_used` | bigint | Y |  |  |
| 11 | `desk5_used` | bigint | Y |  |  |
| 12 | `fund_mode` | character varying(20) | Y |  |  |
| 13 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_fund_pool_snapshot_pkey`

---

#### `v4_hav_drift_events` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_hav_drift_events_i |
| 2 | `detected_at` | timestamp without time zone | Y |  | now() |
| 3 | `drift_type` | character varying(50) | N |  |  |
| 4 | `current_value` | numeric | Y |  |  |
| 5 | `baseline_value` | numeric | Y |  |  |
| 6 | `delta` | numeric | Y |  |  |
| 7 | `threshold` | numeric | Y |  |  |
| 8 | `triggered_search` | boolean | Y |  | false |
| 9 | `search_hypothesis_id` | character varying(30) | Y |  |  |

**인덱스:**

- `v4_hav_drift_events_pkey`
- `idx_hav_drift_dt_type`

---

#### `v4_hav_hypotheses` [V4.1]

행 수: 285 | 크기: 33 MB | 최신: 2026-03-28

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_hav_hypotheses_id_ |
| 2 | `hypothesis_id` | character varying(30) | N |  |  |
| 3 | `created_at` | timestamp without time zone | Y |  | now() |
| 4 | `stage` | character varying(20) | N |  | 'coarse'::character varying |
| 5 | `params` | jsonb | N |  |  |
| 6 | `coarse_pf` | numeric | Y |  |  |
| 7 | `coarse_sharpe` | numeric | Y |  |  |
| 8 | `coarse_trades` | integer | Y |  |  |
| 9 | `fine_pf` | numeric | Y |  |  |
| 10 | `fine_sharpe` | numeric | Y |  |  |
| 11 | `fine_max_dd` | numeric | Y |  |  |
| 12 | `wf_results` | jsonb | Y |  |  |
| 13 | `wf_pass_count` | smallint | Y |  |  |
| 14 | `oos_pf` | numeric | Y |  |  |
| 15 | `verdict` | character varying(15) | Y |  |  |
| 16 | `parent_id` | integer | Y |  |  |
| 17 | `drift_trigger` | character varying(50) | Y |  |  |
| 18 | `rank` | integer | Y |  |  |
| 19 | `notes` | text | Y |  |  |
| 20 | `parent_hypothesis_id` | text | Y |  |  |

**인덱스:**

- `v4_hav_hypotheses_pkey`
- `v4_hav_hypotheses_hypothesis_id_key`
- `idx_hav_hyp_stage_verdict`
- `idx_hav_hyp_created`
- `idx_hav_parent`

---

#### `v4_hav_validation_runs` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_hav_validation_run |
| 2 | `hypothesis_id` | character varying(30) | Y |  |  |
| 3 | `run_at` | timestamp without time zone | Y |  | now() |
| 4 | `validation_type` | character varying(20) | N |  |  |
| 5 | `result` | jsonb | Y |  |  |
| 6 | `passed` | boolean | Y |  |  |
| 7 | `error_log` | text | Y |  |  |

**인덱스:**

- `v4_hav_validation_runs_pkey`
- `idx_hav_valrun_hyp`

---

#### `v4_macro_daily` [V4.1]

행 수: 746 | 크기: 424 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_macro_daily_id_seq |
| 2 | `date` | date | N |  |  |
| 3 | `us_fed_rate` | numeric | Y |  |  |
| 4 | `us_10y_yield` | numeric | Y |  |  |
| 5 | `us_vix` | numeric | Y |  |  |
| 6 | `kr_base_rate` | numeric | Y |  |  |
| 7 | `kr_usd_krw` | numeric | Y |  |  |
| 8 | `kr_kospi` | numeric | Y |  |  |
| 9 | `kr_kosdaq` | numeric | Y |  |  |
| 10 | `macro_regime` | character varying(20) | Y |  |  |
| 11 | `collected_at` | timestamp with time zone | Y |  | now() |
| 12 | `kospi_ma60` | numeric | Y |  |  |
| 13 | `kospi_ma120` | numeric | Y |  |  |

**인덱스:**

- `v4_macro_daily_pkey`
- `v4_macro_daily_date_key`
- `idx_macro_date`

---

#### `v4_meta_rules` [V4.1]

행 수: 214 | 크기: 752 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_meta_rules_id_seq' |
| 2 | `rule_type` | character varying(50) | N |  | 'avoid'::character varying |
| 3 | `category` | character varying(100) | N |  |  |
| 4 | `rule_content` | jsonb | N |  |  |
| 5 | `confidence` | double precision | Y |  | 0.5 |
| 6 | `hit_count` | integer | Y |  | 0 |
| 7 | `is_active` | boolean | Y |  | true |
| 8 | `source_hypothesis_ids` | ARRAY | Y |  |  |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |
| 10 | `updated_at` | timestamp with time zone | Y |  | now() |
| 11 | `source_fail_count` | integer | Y |  | 0 |

**인덱스:**

- `v4_meta_rules_pkey`
- `idx_meta_rules_active`
- `idx_meta_rules_category`

---

#### `v4_minute_collect_progress` [V4.1]

행 수: 840 | 크기: 3960 kB | 최신: 2026-03-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `stock_code` | character varying(10) | N | PK |  |
| 2 | `stock_name` | character varying(50) | Y |  |  |
| 3 | `last_collected_date` | date | Y |  |  |
| 4 | `last_collected_time` | time without time zone | Y |  |  |
| 5 | `total_rows_collected` | integer | Y |  | 0 |
| 6 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 7 | `started_at` | timestamp with time zone | Y |  |  |
| 8 | `completed_at` | timestamp with time zone | Y |  |  |
| 9 | `error_message` | text | Y |  |  |
| 10 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_minute_collect_progress_pkey`

---

#### `v4_node_history` [V4.1]

행 수: 33,100 | 크기: 4496 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_node_history_id_se |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `desk_level` | integer | N |  |  |
| 4 | `node_number` | integer | N |  | 1 |
| 5 | `node_start_date` | date | N |  |  |
| 6 | `node_end_date` | date | Y |  |  |
| 7 | `node_pnl_pct` | numeric | Y |  |  |
| 8 | `pullback_depth_pct` | numeric | Y |  |  |
| 9 | `pullback_days` | integer | Y |  |  |
| 10 | `node_size_category` | character varying(20) | Y |  |  |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_node_history_pkey`
- `idx_node_history_stock_desk`
- `idx_node_history_start_date`

---

#### `v4_node_realtime` [V4.1]

행 수: 12 | 크기: 136 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_node_realtime_id_s |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `desk_level` | integer | N |  |  |
| 4 | `current_phase` | character varying(20) | N |  |  |
| 5 | `phase_confidence` | integer | N |  | 0 |
| 6 | `next_node_est_date` | date | Y |  |  |
| 7 | `next_node_est_size_pct` | numeric | Y |  |  |
| 8 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_node_realtime_pkey`
- `v4_node_realtime_stock_code_desk_level_key`
- `idx_node_realtime_phase`
- `idx_node_realtime_confidence`
- `idx_v4_node_rt_id`
- `idx_node_rt_stock`

---

#### `v4_peak_exits` [V4.1]

행 수: 12 | 크기: 40 kB | 최신: 2026-03-19

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_peak_exits_id_seq' |
| 2 | `entry_id` | integer | Y |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `peak_price` | numeric | Y |  |  |
| 5 | `peak_time` | timestamp without time zone | Y |  |  |
| 6 | `peak_volume` | bigint | Y |  |  |
| 7 | `current_trail_pct` | numeric | Y |  |  |
| 8 | `vol_from_peak_ratio` | numeric | Y |  |  |
| 9 | `price_momentum` | numeric | Y |  |  |
| 10 | `rsi_1m` | numeric | Y |  |  |
| 11 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_peak_exits_pkey`
- `uq_peak_exits_entry_id`

---

#### `v4_pick_reasons` [V4.1]

행 수: 2,265 | 크기: 1720 kB | 최신: 2026-03-19

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_pick_reasons_id_se |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `desk` | character varying(10) | N |  |  |
| 5 | `pick_date` | date | N |  | CURRENT_DATE |
| 6 | `expire_date` | date | Y |  |  |
| 7 | `candle_date` | date | Y |  |  |
| 8 | `candle_close` | numeric | Y |  |  |
| 9 | `change_pct` | numeric | Y |  |  |
| 10 | `trade_amount_eok` | numeric | Y |  |  |
| 11 | `current_close` | numeric | Y |  |  |
| 12 | `ma5` | numeric | Y |  |  |
| 13 | `ma20` | numeric | Y |  |  |
| 14 | `ma60` | numeric | Y |  |  |
| 15 | `ma120` | numeric | Y |  |  |
| 16 | `ma5_status` | character varying(20) | Y |  |  |
| 17 | `reason` | text | Y |  |  |
| 18 | `is_active` | boolean | Y |  | true |
| 19 | `created_at` | timestamp without time zone | Y |  | now() |
| 20 | `desk_type` | character varying(20) | Y |  |  |
| 21 | `score` | numeric | Y |  |  |
| 22 | `indicators` | jsonb | Y |  | '{}'::jsonb |
| 23 | `picked_at` | timestamp without time zone | Y |  | now() |
| 24 | `news_score` | numeric | Y |  | 0 |

**인덱스:**

- `v4_pick_reasons_pkey`
- `idx_pick_reasons_desk`
- `idx_pick_reasons_stock`
- `idx_pick_reasons_date`
- `idx_vpr_stock_code`
- `idx_vpr_desk_type`
- `idx_vpr_picked_at`

---

#### `v4_pyramid_chain` [V4.1]

행 수: 1 | 크기: 72 kB | 최신: 2026-03-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_pyramid_chain_id_s |
| 2 | `chain_id` | uuid | N |  | gen_random_uuid() |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `chain_status` | character varying(20) | N |  | 'ACTIVE'::character varying |
| 5 | `desk5_entry_price` | numeric | Y |  |  |
| 6 | `desk5_entry_date` | date | Y |  |  |
| 7 | `desk5_qty` | integer | Y |  | 0 |
| 8 | `desk4_entry_price` | numeric | Y |  |  |
| 9 | `desk4_entry_date` | date | Y |  |  |
| 10 | `desk4_qty` | integer | Y |  | 0 |
| 11 | `desk3_entry_price` | numeric | Y |  |  |
| 12 | `desk3_entry_date` | date | Y |  |  |
| 13 | `desk3_qty` | integer | Y |  | 0 |
| 14 | `desk2_entry_price` | numeric | Y |  |  |
| 15 | `desk2_entry_date` | date | Y |  |  |
| 16 | `desk2_qty` | integer | Y |  | 0 |
| 17 | `avg_cost` | numeric | Y |  |  |
| 18 | `total_qty` | integer | Y |  | 0 |
| 19 | `total_unrealized_pnl_pct` | numeric | Y |  | 0 |
| 20 | `max_pnl_pct` | numeric | Y |  | 0 |
| 21 | `created_at` | timestamp with time zone | Y |  | now() |
| 22 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_pyramid_chain_pkey`
- `v4_pyramid_chain_chain_id_key`
- `idx_pyramid_chain_stock`
- `idx_pyramid_chain_status`

---

#### `v4_pyramid_chain_log` [V4.1]

행 수: 5 | 크기: 40 kB | 최신: 2026-03-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_pyramid_chain_log_ |
| 2 | `chain_id` | uuid | N |  |  |
| 3 | `event_type` | character varying(20) | N |  |  |
| 4 | `desk_level` | integer | Y |  |  |
| 5 | `price` | numeric | Y |  |  |
| 6 | `qty` | integer | Y |  |  |
| 7 | `pnl_pct` | numeric | Y |  |  |
| 8 | `routed_to` | character varying(50) | Y |  |  |
| 9 | `event_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_pyramid_chain_log_pkey`
- `idx_pyramid_chain_log_chain`

---

#### `v4_reservations` [V4.1]

행 수: 2 | 크기: 128 kB | 최신: 2026-02-13

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | character varying(64) | N | PK |  |
| 2 | `order_request_id` | bigint | Y |  |  |
| 3 | `user_id` | bigint | N |  |  |
| 4 | `desk_id` | integer | N |  |  |
| 5 | `ticker` | character varying(20) | N |  |  |
| 6 | `amount` | bigint | N |  |  |
| 7 | `status` | character varying(20) | N |  | 'ACTIVE'::character varying |
| 8 | `created_at` | timestamp with time zone | N |  | CURRENT_TIMESTAMP |
| 9 | `expires_at` | timestamp with time zone | N |  |  |
| 10 | `order_no` | character varying(50) | Y |  |  |
| 11 | `reason` | text | Y |  |  |
| 12 | `updated_at` | timestamp with time zone | N |  | CURRENT_TIMESTAMP |
| 13 | `strategy_id` | character varying(20) | Y |  |  |
| 14 | `signal_id` | character varying(100) | Y |  |  |

**인덱스:**

- `v4_reservations_pkey`
- `ix_v4_reservations_order_request_id`
- `ix_v4_reservations_user_id`
- `ix_v4_reservations_desk_id`
- `ix_v4_reservations_status`

---

#### `v4_smart_entries` [V4.1]

행 수: 12 | 크기: 72 kB | 최신: 2026-03-19

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_smart_entries_id_s |
| 2 | `signal_id` | integer | Y |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `entry_type` | character varying(20) | N |  |  |
| 5 | `entry_price` | numeric | Y |  |  |
| 6 | `entry_time` | timestamp without time zone | Y |  |  |
| 7 | `entry_volume` | bigint | Y |  |  |
| 8 | `stock_atr_20` | numeric | Y |  |  |
| 9 | `stock_volatility` | numeric | Y |  |  |
| 10 | `typical_range` | numeric | Y |  |  |
| 11 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 12 | `exit_price` | numeric | Y |  |  |
| 13 | `exit_time` | timestamp without time zone | Y |  |  |
| 14 | `exit_reason` | character varying(200) | Y |  |  |
| 15 | `pnl_pct` | numeric | Y |  |  |
| 16 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_smart_entries_pkey`
- `idx_smart_entries_code`
- `idx_v4_smart_entries_status`
- `idx_v4_smart_entries_stock`

---

#### `v4_stage_history` [V4.1]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_stage_history_id_s |
| 2 | `stage_from` | smallint | N |  |  |
| 3 | `stage_to` | smallint | N |  |  |
| 4 | `capital` | bigint | N |  | 0 |
| 5 | `trailing_pf` | numeric | N |  | 1.0 |
| 6 | `max_dd` | numeric | N |  | 0.0 |
| 7 | `trigger_reason` | text | N |  | ''::text |
| 8 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_stage_history_pkey`
- `idx_v4_stage_history_created`
- `idx_v4_stage_history_stages`

---

#### `v4_stage_transitions` [V4.1]

행 수: 4 | 크기: 64 kB | 최신: 2026-03-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_stage_transitions_ |
| 2 | `transition_date` | date | N |  |  |
| 3 | `from_stage` | integer | N |  |  |
| 4 | `to_stage` | integer | N |  |  |
| 5 | `total_asset` | numeric | N |  |  |
| 6 | `old_allocation` | jsonb | N |  |  |
| 7 | `new_allocation` | jsonb | N |  |  |
| 8 | `reason` | text | Y |  |  |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_stage_transitions_pkey`

---

#### `v4_top20_history` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_top20_history_id_s |
| 2 | `stock_code` | character varying(10) | Y |  |  |
| 3 | `trade_date` | date | Y |  |  |
| 4 | `rank_position` | integer | Y |  |  |
| 5 | `trade_amount` | numeric | Y |  |  |
| 6 | `sector_code` | character varying(20) | Y |  |  |
| 7 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_top20_history_pkey`
- `idx_v4_top20_date`
- `idx_top20_date`

---

#### `v4_trajectory_labels` [V4.1]

행 수: 58 | 크기: 80 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_trajectory_labels_ |
| 2 | `ticker` | character varying(20) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `tj_type` | character varying(10) | N |  |  |
| 5 | `confidence` | double precision | Y |  |  |
| 6 | `features` | jsonb | Y |  |  |
| 7 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_trajectory_labels_pkey`
- `v4_trajectory_labels_ticker_trade_date_key`

---

#### `v4_vi_history` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_vi_history_id_seq' |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `vi_date` | date | N |  |  |
| 4 | `vi_trigger_time` | time without time zone | Y |  |  |
| 5 | `vi_release_time` | time without time zone | Y |  |  |
| 6 | `vi_type` | character varying(10) | Y |  |  |
| 7 | `vi_direction` | character varying(10) | Y |  |  |
| 8 | `trigger_price` | real | Y |  |  |
| 9 | `pre_vi_price` | real | Y |  |  |
| 10 | `post_vi_first_price` | real | Y |  |  |
| 11 | `pre_vi_volume_5min` | bigint | Y |  |  |
| 12 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_vi_history_pkey`
- `idx_vi_stock_date`

---

#### `v4_vi_occurrences` [V4.1]

행 수: 319 | 크기: 96 kB | 최신: 2026-02-25

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_vi_occurrences_id_ |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `vi_time` | timestamp without time zone | N |  |  |
| 4 | `vi_type` | character varying(20) | Y |  | 'STATIC'::character varying |
| 5 | `trigger_price` | numeric | Y |  |  |
| 6 | `release_price` | numeric | Y |  |  |
| 7 | `pre_vi_volume` | bigint | Y |  |  |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_vi_occurrences_pkey`
- `idx_vi_occ_code_time`

---

#### `v4_virtual_monitor_snapshots` [V4.1]

행 수: 1,804 | 크기: 416 kB | 최신: 2026-03-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_virtual_monitor_sn |
| 2 | `snapshot_time` | timestamp without time zone | N |  |  |
| 3 | `trade_id` | integer | N |  |  |
| 4 | `ticker` | character varying(20) | N |  |  |
| 5 | `strategy_id` | character varying(20) | N |  |  |
| 6 | `entry_price` | numeric | Y |  |  |
| 7 | `current_price` | numeric | Y |  |  |
| 8 | `unrealized_pnl` | numeric | Y |  |  |
| 9 | `price_source` | character varying(20) | Y |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_virtual_monitor_snapshots_pkey`
- `idx_vvms_time`
- `idx_vvms_trade`

---

#### `v4_volume_retention` [V4.1]

행 수: 9,170 | 크기: 3656 kB | 최신: 2026-03-18

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_volume_retention_i |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `calc_date` | date | N |  |  |
| 4 | `price_level` | integer | N |  |  |
| 5 | `total_volume` | bigint | Y |  | 0 |
| 6 | `total_amount` | bigint | Y |  | 0 |
| 7 | `retention_pct` | numeric | Y |  |  |
| 8 | `is_support` | boolean | Y |  | false |
| 9 | `is_resistance` | boolean | Y |  | false |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_volume_retention_pkey`
- `v4_volume_retention_stock_code_calc_date_price_level_key`
- `idx_vr_stock_date`
- `idx_vr_support`
- `idx_v4_volume_retention_stock`
- `idx_v4_volume_retention_date`

---

#### `daily_trading_stats` [공통]

행 수: 1 | 크기: 88 kB | 최신: 2026-01-29

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('daily_trading_stats_i |
| 2 | `trade_date` | date | N |  |  |
| 3 | `account_email` | character varying(255) | N |  |  |
| 4 | `real_total_trades` | integer | Y |  | 0 |
| 5 | `real_filled_trades` | integer | Y |  | 0 |
| 6 | `real_failed_trades` | integer | Y |  | 0 |
| 7 | `real_total_commission` | real | Y |  | 0.0 |
| 8 | `real_total_slippage` | real | Y |  | 0.0 |
| 9 | `real_total_pnl` | real | Y |  | 0.0 |
| 10 | `virtual_total_trades` | integer | Y |  | 0 |
| 11 | `virtual_filled_trades` | integer | Y |  | 0 |
| 12 | `virtual_total_pnl` | real | Y |  | 0.0 |
| 13 | `avg_price_diff` | real | Y |  | 0.0 |
| 14 | `max_price_diff` | real | Y |  | 0.0 |
| 15 | `total_cost_diff` | real | Y |  | 0.0 |
| 16 | `created_at` | timestamp without time zone | Y |  | now() |
| 17 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `daily_trading_stats_pkey`
- `daily_trading_stats_trade_date_key`
- `idx_daily_stats_date`

---

#### `daily_trading_summary` [공통]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('daily_trading_summary |
| 2 | `user_email` | text | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `total_trades` | integer | Y |  | 0 |
| 5 | `winning_trades` | integer | Y |  | 0 |
| 6 | `losing_trades` | integer | Y |  | 0 |
| 7 | `win_rate` | real | Y |  | 0 |
| 8 | `total_pnl` | real | Y |  | 0 |
| 9 | `total_pnl_pct` | real | Y |  | 0 |
| 10 | `starting_capital` | real | Y |  |  |
| 11 | `ending_capital` | real | Y |  |  |
| 12 | `strategy_performance` | text | Y |  |  |
| 13 | `best_trade_pnl` | real | Y |  |  |
| 14 | `worst_trade_pnl` | real | Y |  |  |
| 15 | `created_at` | timestamp without time zone | Y |  | now() |
| 16 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `daily_trading_summary_pkey`
- `daily_trading_summary_user_email_trade_date_key`
- `idx_daily_user_date`

---

#### `data_crypto_daily` [공통]

행 수: 860 | 크기: 248 kB | 최신: 2026-03-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('data_crypto_daily_id_ |
| 2 | `symbol` | character varying(20) | N |  |  |
| 3 | `date` | date | N |  |  |
| 4 | `open` | numeric | Y |  |  |
| 5 | `high` | numeric | Y |  |  |
| 6 | `low` | numeric | Y |  |  |
| 7 | `close` | numeric | N |  |  |
| 8 | `volume` | numeric | Y |  |  |
| 9 | `market_cap` | numeric | Y |  |  |
| 10 | `change_pct` | numeric | Y |  |  |
| 11 | `source` | character varying(20) | Y |  | 'COINGECKO'::character varying |
| 12 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `data_crypto_daily_pkey`
- `data_crypto_daily_symbol_date_key`

---

#### `data_fx_daily` [공통]

행 수: 863 | 크기: 336 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('data_fx_daily_id_seq' |
| 2 | `currency_pair` | character varying(10) | N |  |  |
| 3 | `date` | date | N |  |  |
| 4 | `open` | numeric | Y |  |  |
| 5 | `high` | numeric | Y |  |  |
| 6 | `low` | numeric | Y |  |  |
| 7 | `close` | numeric | N |  |  |
| 8 | `change_pct` | numeric | Y |  |  |
| 9 | `source` | character varying(20) | Y |  | 'YAHOO'::character varying |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `data_fx_daily_pkey`
- `data_fx_daily_currency_pair_date_key`

---

#### `desk5_seeds` [공통]

행 수: 0 | 크기: 80 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('desk5_seeds_id_seq':: |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `detected_at` | character varying | N |  | now() |
| 5 | `trigger_type` | character varying(50) | N |  |  |
| 6 | `score` | integer | N |  |  |
| 7 | `close_price` | double precision | Y |  |  |
| 8 | `volume` | double precision | Y |  |  |
| 9 | `change_pct` | double precision | Y |  |  |
| 10 | `is_active` | boolean | Y |  |  |
| 11 | `note` | text | Y |  |  |
| 12 | `created_at` | character varying | Y |  | now() |
| 13 | `status` | character varying(20) | Y |  | 'WATCHING'::character varying |
| 14 | `ma10_weekly` | real | Y |  |  |
| 15 | `volume_ratio` | real | Y |  |  |

**인덱스:**

- `desk5_seeds_pkey`
- `ix_desk5_seeds_id`
- `ix_desk5_seeds_detected_at`
- `ix_desk5_seeds_stock_code`

---

#### `live_trading_results` [공통]

행 수: 7,986 | 크기: 1688 kB | 최신: 2026-02-06

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('live_trading_results_ |
| 2 | `user_email` | text | N |  |  |
| 3 | `timestamp` | timestamp without time zone | Y |  | now() |
| 4 | `session_id` | text | N |  |  |
| 5 | `stock_code` | text | N |  |  |
| 6 | `stock_name` | text | N |  |  |
| 7 | `strategy` | text | N |  |  |
| 8 | `entry_price` | real | N |  |  |
| 9 | `exit_price` | real | Y |  |  |
| 10 | `quantity` | integer | N |  |  |
| 11 | `pnl` | real | Y |  |  |
| 12 | `pnl_pct` | real | Y |  |  |
| 13 | `result` | text | Y |  |  |
| 14 | `capital_tier` | text | Y |  | 'SMALL'::text |
| 15 | `account_number` | text | Y |  |  |
| 16 | `trading_mode` | text | Y |  | 'LIVE'::text |
| 17 | `entry_time` | timestamp without time zone | Y |  |  |
| 18 | `exit_time` | timestamp without time zone | Y |  |  |
| 19 | `exit_reason` | character varying(100) | Y |  | NULL::character varying |

**인덱스:**

- `live_trading_results_pkey`

---

#### `portfolios` [공통]

행 수: 5 | 크기: 56 kB | 최신: 2026-01-25

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('portfolios_id_seq'::r |
| 2 | `user_id` | integer | N |  |  |
| 3 | `initial_capital` | real | N |  |  |
| 4 | `current_capital` | real | N |  |  |
| 5 | `total_return` | real | Y |  |  |
| 6 | `scenario` | character varying(50) | N |  |  |
| 7 | `kelly_fraction` | real | Y |  |  |
| 8 | `market_regime` | character varying(50) | Y |  |  |
| 9 | `status` | character varying(6) | N |  |  |
| 10 | `sharpe_ratio` | real | Y |  |  |
| 11 | `max_drawdown` | real | Y |  |  |
| 12 | `win_rate` | real | Y |  |  |
| 13 | `total_trades` | integer | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  | now() |
| 15 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `portfolios_pkey`

---

#### `stock_lifecycle` [공통]

행 수: 3,428 | 크기: 1384 kB | 최신: 2026-03-16

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('stock_lifecycle_id_se |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `desk5_entry_date` | date | Y |  |  |
| 5 | `desk5_entry_price` | real | Y |  |  |
| 6 | `surge_start_date` | date | Y |  |  |
| 7 | `surge_start_price` | real | Y |  |  |
| 8 | `surge_peak_date` | date | Y |  |  |
| 9 | `surge_peak_price` | real | Y |  |  |
| 10 | `surge_volume_peak` | bigint | Y |  |  |
| 11 | `surge_volume_avg` | bigint | Y |  |  |
| 12 | `surge_pct` | real | Y |  |  |
| 13 | `pullback_start_date` | date | Y |  |  |
| 14 | `pullback_depth_pct` | real | Y |  |  |
| 15 | `pullback_duration_days` | integer | Y |  |  |
| 16 | `volume_retention_pct` | real | Y |  |  |
| 17 | `ma20_above_ma60` | boolean | Y |  |  |
| 18 | `ma60_above_ma120` | boolean | Y |  |  |
| 19 | `ma120_above_ma240` | boolean | Y |  |  |
| 20 | `current_price` | real | Y |  |  |
| 21 | `current_vs_ma60_pct` | real | Y |  |  |
| 22 | `wave_count` | integer | Y |  | 1 |
| 23 | `fibo_target_2nd` | real | Y |  |  |
| 24 | `fibo_target_3rd` | real | Y |  |  |
| 25 | `fibo_target_4th` | real | Y |  |  |
| 26 | `status` | character varying(20) | Y |  | 'watching'::character varying |
| 27 | `desk_level` | character varying(10) | Y |  |  |
| 28 | `notes` | text | Y |  |  |
| 29 | `last_updated` | date | Y |  |  |
| 30 | `created_at` | timestamp without time zone | Y |  | now() |
| 31 | `updated_at` | timestamp without time zone | Y |  | now() |
| 32 | `current_desk` | character varying(10) | Y |  | 'WATCH'::character varying |
| 33 | `desk_entered_at` | timestamp without time zone | Y |  |  |
| 34 | `first_surge_date` | date | Y |  |  |
| 35 | `first_surge_pct` | numeric | Y |  |  |
| 36 | `first_surge_volume_peak` | bigint | Y |  |  |
| 37 | `peak_price` | numeric | Y |  |  |
| 38 | `peak_date` | date | Y |  |  |
| 39 | `pullback_pct` | numeric | Y |  |  |
| 40 | `pullback_days` | integer | Y |  |  |
| 41 | `desk_type` | character varying(20) | Y |  |  |
| 42 | `discovered_at` | timestamp without time zone | Y |  | now() |
| 43 | `entry_price` | numeric | Y |  |  |
| 44 | `highest_price` | numeric | Y |  |  |
| 45 | `score` | numeric | Y |  |  |
| 46 | `exit_at` | timestamp without time zone | Y |  |  |
| 47 | `exit_reason` | character varying(100) | Y |  |  |
| 48 | `profit_pct` | numeric | Y |  |  |
| 49 | `metadata` | jsonb | Y |  | '{}'::jsonb |

**인덱스:**

- `stock_lifecycle_pkey`
- `stock_lifecycle_stock_code_desk5_entry_date_key`
- `idx_lifecycle_status`
- `idx_lifecycle_code`
- `idx_lifecycle_desk`
- `idx_lifecycle_updated`
- `idx_lifecycle_stock`
- `idx_sl_stock_code`
- `idx_sl_status`
- `idx_sl_desk_type`

---

#### `stock_price_snapshot` [공통]

행 수: 3,588 | 크기: 66 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `stock_code` | character varying(10) | N | PK |  |
| 2 | `price` | real | Y |  |  |
| 3 | `open_price` | real | Y |  |  |
| 4 | `high_price` | real | Y |  |  |
| 5 | `low_price` | real | Y |  |  |
| 6 | `change_pct` | real | Y |  |  |
| 7 | `volume` | bigint | Y |  |  |
| 8 | `trade_amount` | real | Y |  |  |
| 9 | `market_cap` | bigint | Y |  |  |
| 10 | `snapshot_time` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `stock_price_snapshot_pkey`
- `idx_snapshot_time`
- `idx_sps_change_pct`
- `idx_sps_trade_amount`
- `idx_sps_snapshot_time`
- `idx_sps_code`
- `idx_sps_time`
- `idx_snapshot_stock`

---

#### `strategies` [공통]

행 수: 51 | 크기: 72 kB | 최신: 2026-02-07

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | character varying(50) | N | PK |  |
| 2 | `name` | character varying(255) | N |  |  |
| 3 | `description` | text | Y |  |  |
| 4 | `category` | character varying(50) | Y |  |  |
| 5 | `is_premium` | boolean | Y |  |  |
| 6 | `avg_win_rate` | real | Y |  |  |
| 7 | `avg_return` | real | Y |  |  |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |
| 9 | `holding_period` | real | Y |  |  |
| 10 | `sharpe` | real | Y |  |  |
| 11 | `mdd` | real | Y |  |  |
| 12 | `risk_level` | text | Y |  |  |
| 13 | `is_approved` | boolean | Y |  | false |
| 14 | `approval_date` | timestamp without time zone | Y |  |  |
| 15 | `optimization_score` | real | Y |  | 0.0 |
| 16 | `sortino_ratio` | real | Y |  | 0.0 |
| 17 | `settings` | text | Y |  |  |
| 18 | `strategy_key` | text | Y |  |  |
| 19 | `is_active` | boolean | Y |  | false |

**인덱스:**

- `strategies_pkey`

---

#### `trading_events` [공통]

행 수: 9 | 크기: 96 kB | 최신: 2026-01-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('trading_events_id_seq |
| 2 | `user_email` | text | N |  |  |
| 3 | `event_type` | text | N |  |  |
| 4 | `timestamp` | timestamp without time zone | Y |  | now() |
| 5 | `stock_code` | text | Y |  |  |
| 6 | `message` | text | Y |  |  |
| 7 | `details` | text | Y |  |  |

**인덱스:**

- `idx_events_type`
- `idx_events_user_time`
- `trading_events_pkey`

---

#### `waverider_performance` [공통]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('waverider_performance |
| 2 | `user_id` | integer | N |  |  |
| 3 | `period_type` | character varying(20) | N |  |  |
| 4 | `period_start` | timestamp without time zone | N |  |  |
| 5 | `period_end` | timestamp without time zone | N |  |  |
| 6 | `total_signals` | integer | Y |  |  |
| 7 | `total_trades` | integer | Y |  |  |
| 8 | `winning_trades` | integer | Y |  |  |
| 9 | `losing_trades` | integer | Y |  |  |
| 10 | `win_rate` | double precision | Y |  |  |
| 11 | `total_return` | double precision | Y |  |  |
| 12 | `total_return_pct` | double precision | Y |  |  |
| 13 | `avg_return_per_trade` | double precision | Y |  |  |
| 14 | `sharpe_ratio` | double precision | Y |  |  |
| 15 | `max_drawdown` | double precision | Y |  |  |
| 16 | `max_drawdown_pct` | double precision | Y |  |  |
| 17 | `intro_signals` | integer | Y |  |  |
| 18 | `growth_signals` | integer | Y |  |  |
| 19 | `maturity_signals` | integer | Y |  |  |
| 20 | `decline_signals` | integer | Y |  |  |
| 21 | `created_at` | timestamp without time zone | Y |  |  |
| 22 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `waverider_performance_pkey`
- `ix_waverider_performance_id`

---


### [GLOBAL]

#### `go100_global_market` [GO100]

행 수: 318 | 크기: 232 kB | 최신: 2026-03-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_global_market_i |
| 2 | `data_date` | date | N |  |  |
| 3 | `usd_krw` | real | Y |  |  |
| 4 | `vix` | real | Y |  |  |
| 5 | `sp500` | real | Y |  |  |
| 6 | `sp500_change_pct` | real | Y |  |  |
| 7 | `nasdaq` | real | Y |  |  |
| 8 | `nasdaq_change_pct` | real | Y |  |  |
| 9 | `dow` | real | Y |  |  |
| 10 | `dow_change_pct` | real | Y |  |  |
| 11 | `us10y_yield` | real | Y |  |  |
| 12 | `created_at` | timestamp without time zone | Y |  | now() |
| 13 | `sox` | real | Y |  |  |
| 14 | `sox_change_pct` | real | Y |  |  |
| 15 | `csi300` | real | Y |  |  |
| 16 | `csi300_change_pct` | real | Y |  |  |
| 17 | `wti_crude` | real | Y |  |  |
| 18 | `wti_crude_change_pct` | real | Y |  |  |
| 19 | `copper` | real | Y |  |  |
| 20 | `copper_change_pct` | real | Y |  |  |
| 21 | `vkospi` | real | Y |  |  |

**인덱스:**

- `go100_global_market_pkey`
- `go100_global_market_data_date_key`
- `idx_go100_global_market_data_date`

---


### [INFRA]

#### `go100_account_reconciliation` [GO100]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_account_reconci |
| 2 | `user_id` | integer | N |  |  |
| 3 | `account_id` | integer | N |  |  |
| 4 | `system_cash` | numeric | Y |  |  |
| 5 | `system_position_count` | integer | Y |  |  |
| 6 | `system_total_eval` | numeric | Y |  |  |
| 7 | `actual_cash` | numeric | Y |  |  |
| 8 | `actual_position_count` | integer | Y |  |  |
| 9 | `actual_total_eval` | numeric | Y |  |  |
| 10 | `external_buy_count` | integer | Y |  | 0 |
| 11 | `external_sell_count` | integer | Y |  | 0 |
| 12 | `qty_mismatch_count` | integer | Y |  | 0 |
| 13 | `cash_diff` | numeric | Y |  |  |
| 14 | `reconcile_status` | character varying(20) | Y |  | 'OK'::character varying |
| 15 | `detail` | jsonb | Y |  |  |
| 16 | `synced_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_account_reconciliation_pkey`
- `idx_go100_recon_user`
- `idx_go100_recon_status`

---

#### `go100_agent_reports` [GO100]

행 수: 124 | 크기: 248 kB | 최신: 2026-03-07

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_agent_reports_i |
| 2 | `report_date` | date | N |  |  |
| 3 | `agent_name` | character varying(50) | N |  |  |
| 4 | `stock_code` | character varying(20) | Y |  |  |
| 5 | `report_json` | jsonb | N |  |  |
| 6 | `conviction` | integer | Y |  |  |
| 7 | `signal` | character varying(20) | Y |  |  |
| 8 | `created_at` | timestamp with time zone | N |  | now() |
| 9 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_agent_reports_pkey`
- `idx_go100_agent_reports_date_agent`
- `idx_go100_agent_reports_stock`
- `idx_go100_agent_reports_user_id`

---

#### `go100_alerts` [GO100]

행 수: 3,698 | 크기: 1656 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_alerts_id_seq': |
| 2 | `created_at` | timestamp with time zone | N |  | now() |
| 3 | `alert_type` | character varying(50) | N |  |  |
| 4 | `severity` | character varying(20) | N |  |  |
| 5 | `title` | character varying(200) | N |  |  |
| 6 | `message` | text | N |  |  |
| 7 | `source` | character varying(100) | Y |  |  |
| 8 | `is_sent` | boolean | Y |  | false |
| 9 | `sent_at` | timestamp with time zone | Y |  |  |
| 10 | `acknowledged_at` | timestamp with time zone | Y |  |  |
| 11 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_alerts_pkey`
- `idx_alerts_unsent`
- `idx_go100_alerts_user_id`

---

#### `go100_daily_briefings` [GO100]

행 수: 23 | 크기: 360 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_daily_briefings |
| 2 | `briefing_date` | date | N |  |  |
| 3 | `market_summary` | text | Y |  |  |
| 4 | `top_movers` | jsonb | Y |  | '[]'::jsonb |
| 5 | `sector_highlights` | jsonb | Y |  | '[]'::jsonb |
| 6 | `regime_info` | jsonb | Y |  | '{}'::jsonb |
| 7 | `ai_commentary` | text | Y |  |  |
| 8 | `generated_at` | timestamp with time zone | Y |  | now() |
| 9 | `source` | character varying(50) | Y |  | 'gemini_flash'::character vary |

**인덱스:**

- `go100_daily_briefings_pkey`
- `go100_daily_briefings_briefing_date_key`
- `idx_briefing_date`

---

#### `go100_live_trading_config` [GO100]

행 수: 1 | 크기: 40 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `config_id` | integer | N | PK | nextval('go100_live_trading_co |
| 2 | `user_id` | integer | N |  |  |
| 3 | `is_enabled` | boolean | Y |  | false |
| 4 | `max_order_amount` | bigint | Y |  | 1000000 |
| 5 | `max_daily_amount` | bigint | Y |  | 5000000 |
| 6 | `max_daily_orders` | integer | Y |  | 10 |
| 7 | `max_loss_pct` | real | Y |  | 3.0 |
| 8 | `allowed_hours_start` | time without time zone | Y |  | '09:05:00'::time without time  |
| 9 | `allowed_hours_end` | time without time zone | Y |  | '15:20:00'::time without time  |
| 10 | `paper_min_days` | integer | Y |  | 14 |
| 11 | `paper_min_winrate` | real | Y |  | 40.0 |
| 12 | `require_confirmation` | boolean | Y |  | true |
| 13 | `created_at` | timestamp with time zone | Y |  | now() |
| 14 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_live_trading_config_pkey`
- `go100_live_trading_config_user_id_key`

---

#### `go100_notification_settings` [GO100]

행 수: 2 | 크기: 72 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_notification_se |
| 2 | `user_id` | integer | N |  |  |
| 3 | `in_app_enabled` | boolean | Y |  | true |
| 4 | `email_enabled` | boolean | Y |  | false |
| 5 | `push_enabled` | boolean | Y |  | false |
| 6 | `trade_executed` | boolean | Y |  | true |
| 7 | `stop_loss_triggered` | boolean | Y |  | true |
| 8 | `take_profit_triggered` | boolean | Y |  | true |
| 9 | `backtest_completed` | boolean | Y |  | true |
| 10 | `optimize_completed` | boolean | Y |  | true |
| 11 | `daily_summary` | boolean | Y |  | true |
| 12 | `scheduler_error` | boolean | Y |  | true |
| 13 | `system_alert` | boolean | Y |  | true |
| 14 | `email_override` | character varying(200) | Y |  |  |
| 15 | `created_at` | timestamp with time zone | Y |  | now() |
| 16 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_notification_settings_pkey`
- `go100_notification_settings_user_id_key`

---

#### `go100_notifications` [GO100]

행 수: 20 | 크기: 160 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_notifications_i |
| 2 | `user_id` | integer | N |  |  |
| 3 | `type` | character varying(50) | N |  |  |
| 4 | `title` | character varying(200) | N |  |  |
| 5 | `message` | text | N |  |  |
| 6 | `data` | jsonb | Y |  | '{}'::jsonb |
| 7 | `priority` | character varying(10) | Y |  | 'NORMAL'::character varying |
| 8 | `is_read` | boolean | Y |  | false |
| 9 | `is_email_sent` | boolean | Y |  | false |
| 10 | `is_push_sent` | boolean | Y |  | false |
| 11 | `channel` | character varying(20) | Y |  | 'IN_APP'::character varying |
| 12 | `created_at` | timestamp with time zone | Y |  | now() |
| 13 | `read_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `go100_notifications_pkey`
- `idx_go100_notif_user_read`
- `idx_go100_notif_user_type`
- `idx_go100_notif_created`
- `idx_noti_user_read`
- `idx_noti_user_type`
- `idx_noti_created`

---

#### `go100_paper_accounts` [GO100]

행 수: 190 | 크기: 128 kB | 최신: 2026-03-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `account_id` | integer | N | PK | nextval('go100_paper_accounts_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `portfolio_id` | integer | Y |  |  |
| 4 | `initial_capital` | bigint | N |  |  |
| 5 | `current_cash` | bigint | N |  |  |
| 6 | `current_value` | bigint | N |  |  |
| 7 | `total_pnl` | bigint | Y |  | 0 |
| 8 | `total_pnl_pct` | real | Y |  | 0.0 |
| 9 | `status` | character varying(20) | Y |  | 'ACTIVE'::character varying |
| 10 | `started_at` | timestamp without time zone | Y |  | now() |
| 11 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_paper_accounts_pkey`
- `idx_go100_paper_accounts_user`
- `idx_go100_paper_accounts_status`

---

#### `go100_paper_trading_sessions` [GO100]

행 수: 25 | 크기: 96 kB | 최신: 2026-03-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `session_id` | integer | N | PK | nextval('go100_paper_trading_s |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_card_id` | integer | Y |  |  |
| 4 | `initial_capital` | numeric | Y |  | 10000000 |
| 5 | `current_capital` | numeric | Y |  |  |
| 6 | `start_date` | date | N |  |  |
| 7 | `end_date` | date | Y |  |  |
| 8 | `status` | character varying(20) | Y |  | 'ACTIVE'::character varying |
| 9 | `total_return` | numeric | Y |  |  |
| 10 | `max_drawdown` | numeric | Y |  |  |
| 11 | `win_rate` | numeric | Y |  |  |
| 12 | `total_trades` | integer | Y |  | 0 |
| 13 | `sharpe_ratio` | numeric | Y |  |  |
| 14 | `result_summary` | jsonb | Y |  |  |
| 15 | `created_at` | timestamp with time zone | Y |  | now() |
| 16 | `hypothesis_id` | character varying(30) | Y |  |  |

**인덱스:**

- `go100_paper_trading_sessions_pkey`
- `idx_pt30_session_user`
- `idx_pt30_session_status`
- `idx_pt30_session_dates`
- `idx_paper_sessions_hypothesis_id`

---

#### `go100_pending_configs` [GO100]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_pending_configs |
| 2 | `evolution_loop_id` | integer | Y |  |  |
| 3 | `hypothesis_id` | integer | Y |  |  |
| 4 | `config_type` | character varying(100) | Y |  |  |
| 5 | `config_key` | character varying(200) | Y |  |  |
| 6 | `config_value` | jsonb | Y |  |  |
| 7 | `param_adjustments` | jsonb | Y |  |  |
| 8 | `discovery_feedback` | jsonb | Y |  |  |
| 9 | `status` | character varying(50) | Y |  | 'pending'::character varying |
| 10 | `ceo_decision` | character varying(50) | Y |  |  |
| 11 | `ceo_decided_at` | timestamp with time zone | Y |  |  |
| 12 | `applied_at` | timestamp with time zone | Y |  |  |
| 13 | `notes` | text | Y |  |  |
| 14 | `created_at` | timestamp with time zone | Y |  | now() |
| 15 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_pending_configs_pkey`
- `idx_go100_pending_configs_user_id`

---

#### `go100_push_subscriptions` [GO100]

행 수: 2 | 크기: 80 kB | 최신: 2026-02-24

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_push_subscripti |
| 2 | `user_id` | integer | N |  |  |
| 3 | `endpoint` | text | N |  |  |
| 4 | `p256dh` | text | N |  |  |
| 5 | `auth` | text | N |  |  |
| 6 | `user_agent` | character varying(500) | Y |  |  |
| 7 | `is_active` | boolean | Y |  | true |
| 8 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_push_subscriptions_pkey`
- `go100_push_subscriptions_user_id_endpoint_key`

---

#### `go100_reports` [GO100]

행 수: 1,139 | 크기: 424 kB | 최신: 2026-03-28

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `report_id` | integer | N | PK | nextval('go100_reports_report_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `report_type` | character varying(30) | N |  |  |
| 4 | `title` | character varying(200) | N |  |  |
| 5 | `content` | text | N |  |  |
| 6 | `priority` | character varying(10) | Y |  | 'normal'::character varying |
| 7 | `is_read` | boolean | Y |  | false |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_reports_pkey`
- `idx_go100_reports_user_unread`
- `idx_go100_reports_user_created`

---

#### `go100_usage_logs` [GO100]

행 수: 124 | 크기: 88 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `log_id` | integer | N | PK | nextval('go100_usage_logs_log_ |
| 2 | `user_id` | integer | Y |  |  |
| 3 | `session_id` | character varying(50) | Y |  |  |
| 4 | `intent` | character varying(30) | Y |  |  |
| 5 | `message_preview` | character varying(100) | Y |  |  |
| 6 | `response_length` | integer | Y |  |  |
| 7 | `latency_ms` | integer | Y |  |  |
| 8 | `llm_model` | character varying(50) | Y |  |  |
| 9 | `llm_tokens_in` | integer | Y |  |  |
| 10 | `llm_tokens_out` | integer | Y |  |  |
| 11 | `is_error` | boolean | Y |  | false |
| 12 | `error_type` | character varying(50) | Y |  |  |
| 13 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_usage_logs_pkey`
- `idx_go100_usage_logs_date`
- `idx_go100_usage_logs_user`

---

#### `go100_user_memory` [GO100]

행 수: 1,620 | 크기: 3664 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `memory_id` | integer | N | PK | nextval('go100_user_memory_mem |
| 2 | `user_id` | integer | N |  |  |
| 3 | `memory_type` | character varying(50) | N |  |  |
| 4 | `content` | jsonb | N |  |  |
| 5 | `importance` | numeric | Y |  | 5.0 |
| 6 | `last_accessed` | timestamp with time zone | Y |  | now() |
| 7 | `access_count` | integer | Y |  | 0 |
| 8 | `expires_at` | timestamp with time zone | Y |  |  |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_user_memory_pkey`
- `idx_user_memory_user`
- `idx_user_memory_importance`
- `idx_user_memory_last_accessed`

---

#### `go100_user_preferences` [GO100]

행 수: 1 | 크기: 64 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `pref_id` | integer | N | PK | nextval('go100_user_preference |
| 2 | `user_id` | integer | N |  |  |
| 3 | `risk_tolerance` | character varying(20) | Y |  | 'MODERATE'::character varying |
| 4 | `preferred_sectors` | ARRAY | Y |  |  |
| 5 | `preferred_strategy_types` | ARRAY | Y |  |  |
| 6 | `investment_horizon` | character varying(20) | Y |  | 'MEDIUM'::character varying |
| 7 | `notification_settings` | jsonb | Y |  | '{}'::jsonb |
| 8 | `custom_filters` | jsonb | Y |  | '{}'::jsonb |
| 9 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_user_preferences_pkey`
- `go100_user_preferences_user_id_key`
- `idx_up_user`

---

#### `go100_user_profile` [GO100]

행 수: 1 | 크기: 48 kB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `user_id` | integer | N | PK |  |
| 2 | `risk_tolerance` | character varying(20) | Y |  | 'aggressive'::character varyin |
| 3 | `preferred_style` | character varying(20) | Y |  | 'swing'::character varying |
| 4 | `preferred_sectors` | jsonb | Y |  | '["반도체", "자동차", "2차전지"]'::json |
| 5 | `avoided_sectors` | jsonb | Y |  | '[]'::jsonb |
| 6 | `max_drawdown_tolerance` | real | Y |  | 15.0 |
| 7 | `trading_frequency` | character varying(20) | Y |  | 'daily'::character varying |
| 8 | `market_hours_active` | boolean | Y |  | true |
| 9 | `notes` | text | Y |  |  |
| 10 | `learned_preferences` | jsonb | Y |  | '{}'::jsonb |
| 11 | `created_at` | timestamp without time zone | Y |  | now() |
| 12 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_user_profile_pkey`
- `idx_user_profile_user`

---

#### `go100_user_profiles` [GO100]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_user_profiles_i |
| 2 | `user_id` | integer | N |  |  |
| 3 | `experience_level` | character varying(20) | Y |  | 'beginner'::character varying |
| 4 | `risk_tolerance` | character varying(20) | Y |  | 'moderate'::character varying |
| 5 | `investment_style` | character varying(30) | Y |  |  |
| 6 | `preferred_sectors` | jsonb | Y |  | '[]'::jsonb |
| 7 | `excluded_sectors` | jsonb | Y |  | '[]'::jsonb |
| 8 | `total_capital` | numeric | Y |  | 0 |
| 9 | `monthly_investment` | numeric | Y |  | 0 |
| 10 | `target_return_annual` | numeric | Y |  |  |
| 11 | `investment_horizon_years` | integer | Y |  |  |
| 12 | `total_strategies_created` | integer | Y |  | 0 |
| 13 | `total_backtests_run` | integer | Y |  | 0 |
| 14 | `avg_strategy_return` | numeric | Y |  |  |
| 15 | `best_strategy_return` | numeric | Y |  |  |
| 16 | `worst_drawdown` | numeric | Y |  |  |
| 17 | `preferred_strategy_types` | jsonb | Y |  | '[]'::jsonb |
| 18 | `last_conversation_summary` | text | Y |  |  |
| 19 | `conversation_count` | integer | Y |  | 0 |
| 20 | `onboarding_completed` | boolean | Y |  | false |
| 21 | `created_at` | timestamp with time zone | Y |  | now() |
| 22 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_user_profiles_pkey`
- `go100_user_profiles_user_id_key`

---

#### `v4_account_config` [V4.1]

행 수: 1 | 크기: 64 kB | 최신: 2026-02-13

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_account_config_id_ |
| 2 | `account_type` | character varying(10) | N |  |  |
| 3 | `account_no` | character varying(20) | N |  |  |
| 4 | `product_code` | character varying(4) | N |  | '01'::character varying |
| 5 | `app_key` | text | N |  |  |
| 6 | `app_secret` | text | N |  |  |
| 7 | `base_url` | character varying(100) | N |  |  |
| 8 | `hts_id` | character varying(20) | Y |  |  |
| 9 | `is_active` | boolean | Y |  | false |
| 10 | `daily_order_limit` | bigint | Y |  | 10000000 |
| 11 | `single_stock_max_pct` | numeric | Y |  | 10.00 |
| 12 | `consecutive_loss_halt` | integer | Y |  | 3 |
| 13 | `created_at` | timestamp with time zone | Y |  | now() |
| 14 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_account_config_pkey`

---

#### `v4_account_holdings` [V4.1]

행 수: 793,771 | 크기: 218 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_account_holdings_i |
| 2 | `config_id` | integer | N |  |  |
| 3 | `snapshot_at` | timestamp with time zone | N |  | now() |
| 4 | `d2_deposit` | bigint | Y |  |  |
| 5 | `total_deposit` | bigint | Y |  |  |
| 6 | `total_eval` | bigint | Y |  |  |
| 7 | `total_pnl` | bigint | Y |  |  |
| 8 | `total_pnl_pct` | numeric | Y |  |  |
| 9 | `stock_code` | character varying(20) | N |  |  |
| 10 | `stock_name` | character varying(100) | Y |  |  |
| 11 | `qty` | integer | Y |  | 0 |
| 12 | `avg_price` | numeric | Y |  |  |
| 13 | `current_price` | numeric | Y |  |  |
| 14 | `eval_amount` | bigint | Y |  |  |
| 15 | `pnl_amount` | bigint | Y |  |  |
| 16 | `pnl_pct` | numeric | Y |  |  |
| 17 | `source` | character varying(20) | N |  | 'UNKNOWN'::character varying |
| 18 | `position_id` | bigint | Y |  |  |
| 19 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_account_holdings_pkey`
- `idx_v4_ah_config_snapshot`
- `idx_v4_ah_config_stock`
- `idx_v4_ah_source`

---

#### `v4_account_sync_log` [V4.1]

행 수: 135,213 | 크기: 29 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_account_sync_log_i |
| 2 | `config_id` | integer | N |  |  |
| 3 | `synced_at` | timestamp with time zone | N |  | now() |
| 4 | `actual_cash` | bigint | Y |  |  |
| 5 | `v41_cash` | bigint | Y |  |  |
| 6 | `deficit` | bigint | Y |  | 0 |
| 7 | `surplus` | bigint | Y |  | 0 |
| 8 | `total_holdings` | integer | Y |  | 0 |
| 9 | `matched_v41` | integer | Y |  | 0 |
| 10 | `external_count` | integer | Y |  | 0 |
| 11 | `missing_v41` | integer | Y |  | 0 |
| 12 | `qty_mismatch` | integer | Y |  | 0 |
| 13 | `action_taken` | text | Y |  |  |
| 14 | `fund_adjusted` | boolean | Y |  | false |
| 15 | `positions_fixed` | integer | Y |  | 0 |
| 16 | `alert_generated` | boolean | Y |  | false |
| 17 | `alert_ids` | ARRAY | Y |  |  |
| 18 | `sync_duration_ms` | integer | Y |  |  |
| 19 | `error_message` | text | Y |  |  |

**인덱스:**

- `v4_account_sync_log_pkey`
- `idx_v4_asl_config_time`

---

#### `v4_alerts` [V4.1]

행 수: 1,005 | 크기: 632 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `alert_id` | bigint | N | PK | nextval('v4_alerts_alert_id_se |
| 2 | `alert_type` | character varying(50) | N |  |  |
| 3 | `severity` | character varying(20) | N |  | 'INFO'::character varying |
| 4 | `title` | character varying(200) | N |  |  |
| 5 | `message` | text | Y |  |  |
| 6 | `desk_id` | integer | Y |  |  |
| 7 | `ticker` | character varying(20) | Y |  |  |
| 8 | `data` | jsonb | Y |  |  |
| 9 | `is_read` | boolean | Y |  | false |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_alerts_pkey`
- `idx_v4_alerts_type`
- `idx_v4_alerts_created`
- `idx_v4_alerts_unread`

---

#### `v4_api_error_log` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_api_error_log_id_s |
| 2 | `account_config_id` | integer | Y |  |  |
| 3 | `endpoint` | character varying(200) | Y |  |  |
| 4 | `tr_id` | character varying(20) | Y |  |  |
| 5 | `error_code` | character varying(20) | Y |  |  |
| 6 | `error_message` | text | Y |  |  |
| 7 | `request_body` | jsonb | Y |  |  |
| 8 | `response_body` | jsonb | Y |  |  |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_api_error_log_pkey`
- `idx_api_error_log_created`

---

#### `v4_api_tokens` [V4.1]

행 수: 1 | 크기: 48 kB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_api_tokens_id_seq' |
| 2 | `account_config_id` | integer | Y |  |  |
| 3 | `access_token` | text | N |  |  |
| 4 | `token_type` | character varying(20) | Y |  | 'Bearer'::character varying |
| 5 | `expires_at` | timestamp with time zone | N |  |  |
| 6 | `issued_at` | timestamp with time zone | Y |  | now() |
| 7 | `is_valid` | boolean | Y |  | true |
| 8 | `issue_count_today` | integer | Y |  | 1 |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_api_tokens_pkey`
- `idx_api_tokens_config_valid`

---

#### `v4_chat_messages` [V4.1]

행 수: 211 | 크기: 248 kB | 최신: 2026-03-22

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_chat_messages_id_s |
| 2 | `session_id` | integer | N |  |  |
| 3 | `role` | character varying(20) | N |  |  |
| 4 | `content` | text | N |  |  |
| 5 | `model` | character varying(50) | Y |  |  |
| 6 | `tokens_used` | integer | Y |  | 0 |
| 7 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_chat_messages_pkey`
- `idx_v4_chat_messages_session_created`

---

#### `v4_chat_sessions` [V4.1]

행 수: 42 | 크기: 72 kB | 최신: 2026-03-22

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_chat_sessions_id_s |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `title` | character varying(200) | Y |  |  |
| 4 | `model` | character varying(50) | Y |  |  |
| 5 | `category` | character varying(50) | N |  | 'free-chat'::character varying |
| 6 | `created_at` | timestamp with time zone | N |  | now() |
| 7 | `updated_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_chat_sessions_pkey`
- `idx_v4_chat_sessions_user_updated`

---

#### `v4_credit_balance` [V4.1]

행 수: 558 | 크기: 288 kB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_credit_balance_id_ |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `credit_balance` | bigint | Y |  |  |
| 5 | `credit_amount` | bigint | Y |  |  |
| 6 | `credit_rate` | numeric | Y |  |  |
| 7 | `short_balance` | bigint | Y |  |  |
| 8 | `short_amount` | bigint | Y |  |  |
| 9 | `short_rate` | numeric | Y |  |  |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_credit_balance_pkey`
- `v4_credit_balance_stock_code_trade_date_key`
- `idx_credit_balance_code_date`

---

#### `v4_daily_reports` [V4.1]

행 수: 37 | 크기: 144 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_daily_reports_id_s |
| 2 | `report_date` | date | N |  |  |
| 3 | `total_trades` | integer | Y |  |  |
| 4 | `buy_trades` | integer | Y |  |  |
| 5 | `sell_trades` | integer | Y |  |  |
| 6 | `realized_pnl` | bigint | Y |  |  |
| 7 | `unrealized_pnl` | bigint | Y |  |  |
| 8 | `open_positions` | integer | Y |  |  |
| 9 | `desk_summary` | jsonb | Y |  |  |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_daily_reports_pkey`
- `v4_daily_reports_report_date_key`
- `ix_v4_daily_reports_report_date`

---

#### `v4_desk_config` [V4.1]

행 수: 5 | 크기: 48 kB | 최신: 2026-03-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk_config_id_seq |
| 2 | `desk` | character varying(10) | N |  |  |
| 3 | `max_stocks` | integer | Y |  | 20 |
| 4 | `max_allocation` | numeric | Y |  | 10000000 |
| 5 | `risk_limit_pct` | numeric | Y |  | '-5.0'::numeric |
| 6 | `is_active` | boolean | Y |  | true |
| 7 | `config_json` | jsonb | Y |  |  |
| 8 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk_config_pkey`
- `v4_desk_config_desk_key`

---

#### `v4_llm_usage` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_llm_usage_id_seq': |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `category` | character varying(50) | N |  |  |
| 4 | `used_count` | integer | N |  | 0 |
| 5 | `daily_limit` | integer | N |  |  |
| 6 | `usage_date` | date | N |  | CURRENT_DATE |

**인덱스:**

- `v4_llm_usage_pkey`
- `v4_llm_usage_user_id_category_usage_date_key`
- `idx_v4_llm_usage_user_date`

---

#### `v4_migration_history` [V4.1]

행 수: 2 | 크기: 80 kB | 최신: 2026-02-13

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_migration_history_ |
| 2 | `migration_name` | character varying(200) | N |  |  |
| 3 | `applied_at` | timestamp with time zone | Y |  | now() |
| 4 | `description` | text | Y |  |  |
| 5 | `checksum` | character varying(64) | Y |  |  |

**인덱스:**

- `v4_migration_history_pkey`
- `v4_migration_history_migration_name_key`

---

#### `v4_notification_channel_config` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `user_id` | bigint | N | PK |  |
| 2 | `config` | jsonb | Y |  | '{}'::jsonb |
| 3 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_notification_channel_config_pkey`

---

#### `v4_notification_settings` [V4.1]

행 수: 3 | 크기: 72 kB | 최신: 2026-02-24

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_notification_setti |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `trade_executed` | boolean | Y |  | true |
| 4 | `trade_failed` | boolean | Y |  | true |
| 5 | `stop_loss_triggered` | boolean | Y |  | true |
| 6 | `take_profit_triggered` | boolean | Y |  | true |
| 7 | `system_error` | boolean | Y |  | true |
| 8 | `daily_summary` | boolean | Y |  | true |
| 9 | `login_alert` | boolean | Y |  | false |
| 10 | `push_enabled` | boolean | Y |  | false |
| 11 | `email_enabled` | boolean | Y |  | false |
| 12 | `sound_enabled` | boolean | Y |  | true |
| 13 | `quiet_hours_start` | time without time zone | Y |  |  |
| 14 | `quiet_hours_end` | time without time zone | Y |  |  |
| 15 | `created_at` | timestamp with time zone | Y |  | now() |
| 16 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_notification_settings_pkey`
- `v4_notification_settings_user_id_key`

---

#### `v4_notifications` [V4.1]

행 수: 8 | 크기: 112 kB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_notifications_id_s |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `type` | character varying(50) | N |  |  |
| 4 | `title` | character varying(200) | N |  |  |
| 5 | `message` | text | N |  |  |
| 6 | `data` | jsonb | Y |  | '{}'::jsonb |
| 7 | `is_read` | boolean | Y |  | false |
| 8 | `is_pushed` | boolean | Y |  | false |
| 9 | `priority` | character varying(20) | Y |  | 'normal'::character varying |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |
| 11 | `read_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_notifications_pkey`
- `idx_v4_notifications_user_unread`
- `idx_v4_notifications_user_created`
- `idx_v4_notifications_type`

---

#### `v4_reports` [V4.1]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_reports_id_seq'::r |
| 2 | `user_id` | integer | N |  |  |
| 3 | `report_type` | character varying(20) | N |  |  |
| 4 | `report_date` | date | N |  |  |
| 5 | `total_trades` | integer | Y |  | 0 |
| 6 | `winning_trades` | integer | Y |  | 0 |
| 7 | `losing_trades` | integer | Y |  | 0 |
| 8 | `total_profit` | numeric | Y |  | 0 |
| 9 | `total_loss` | numeric | Y |  | 0 |
| 10 | `net_profit` | numeric | Y |  | 0 |
| 11 | `win_rate` | numeric | Y |  |  |
| 12 | `profit_factor` | numeric | Y |  |  |
| 13 | `max_drawdown` | numeric | Y |  |  |
| 14 | `portfolio_value` | bigint | Y |  |  |
| 15 | `cash_balance` | bigint | Y |  |  |
| 16 | `daily_return` | numeric | Y |  |  |
| 17 | `cumulative_return` | numeric | Y |  |  |
| 18 | `report_data` | jsonb | Y |  |  |
| 19 | `html_content` | text | Y |  |  |
| 20 | `sent_channels` | ARRAY | Y |  |  |
| 21 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_reports_pkey`
- `v4_reports_user_id_report_type_report_date_key`
- `idx_reports_user_date`

---

#### `v4_stage_config` [V4.1]

행 수: 4 | 크기: 32 kB | 최신: 2026-03-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `stage` | smallint | N | PK |  |
| 2 | `desk_allocation` | jsonb | N |  | '{}'::jsonb |
| 3 | `active` | boolean | N |  | false |
| 4 | `updated_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_stage_config_pkey`

---

#### `v4_system_heartbeat` [V4.1]

행 수: 2,098,766 | 크기: 888 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_system_heartbeat_i |
| 2 | `state` | character varying(20) | Y |  |  |
| 3 | `cycle_count` | integer | Y |  |  |
| 4 | `last_cycle_duration_ms` | integer | Y |  |  |
| 5 | `open_positions` | integer | Y |  |  |
| 6 | `data_quality` | character varying(10) | Y |  |  |
| 7 | `error_count` | integer | Y |  | 0 |
| 8 | `created_at` | timestamp with time zone | N |  | now() |
| 9 | `previous_state` | character varying(20) | Y |  |  |
| 10 | `transition_reason` | text | Y |  |  |
| 11 | `module_status` | jsonb | Y |  | '{}'::jsonb |
| 12 | `cycle_id` | integer | Y |  | 0 |
| 13 | `order_success_count` | integer | Y |  | 0 |
| 14 | `order_fail_count` | integer | Y |  | 0 |
| 15 | `order_reject_count` | integer | Y |  | 0 |
| 16 | `max_price_staleness_ms` | integer | Y |  | 0 |
| 17 | `active_positions_count` | integer | Y |  | 0 |
| 18 | `available_capital` | bigint | Y |  | 0 |
| 19 | `error_message` | text | Y |  |  |

**인덱스:**

- `v4_system_heartbeat_pkey`
- `idx_v4_heartbeat_created`
- `idx_v4_heartbeat_state`

---

#### `v4_system_state_log` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_system_state_log_i |
| 2 | `state` | character varying(20) | N |  |  |
| 3 | `previous_state` | character varying(20) | Y |  |  |
| 4 | `transition_reason` | text | Y |  |  |
| 5 | `module_status` | json | Y |  |  |
| 6 | `created_at` | timestamp with time zone | N |  | now() |
| 7 | `updated_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_system_state_log_pkey`

---

#### `v4_user_settings` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_user_settings_id_s |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `telegram_enabled` | boolean | Y |  | false |
| 4 | `telegram_chat_id` | character varying(100) | Y |  |  |
| 5 | `email_notifications` | boolean | Y |  | true |
| 6 | `trade_alert` | boolean | Y |  | true |
| 7 | `daily_report` | boolean | Y |  | false |
| 8 | `error_alert` | boolean | Y |  | true |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |
| 10 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_user_settings_pkey`
- `v4_user_settings_user_id_key`
- `idx_v4_user_settings_user_id`

---

#### `v4_user_strategies` [V4.1]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_user_strategies_id |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_name` | character varying(100) | N |  |  |
| 4 | `desk` | character varying(20) | Y |  |  |
| 5 | `is_active` | boolean | Y |  | true |
| 6 | `parameters` | jsonb | Y |  |  |
| 7 | `allocation_pct` | numeric | Y |  | 0 |
| 8 | `created_at` | timestamp with time zone | Y |  | now() |
| 9 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_user_strategies_pkey`
- `idx_v4_user_strat_user`
- `idx_v4_user_strat_active`

---

#### `v4_users` [V4.1]

행 수: 9 | 크기: 96 kB | 최신: 2026-03-22

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `user_id` | bigint | N | PK | nextval('v4_users_user_id_seq' |
| 2 | `email` | character varying(255) | N |  |  |
| 3 | `nickname` | character varying(50) | N |  |  |
| 4 | `hashed_password` | character varying(255) | N |  |  |
| 5 | `tier` | character varying(20) | N |  | 'FREE'::character varying |
| 6 | `is_active` | boolean | N |  | true |
| 7 | `last_login_at` | timestamp with time zone | Y |  |  |
| 8 | `created_at` | timestamp with time zone | N |  | now() |
| 9 | `updated_at` | timestamp with time zone | N |  | now() |
| 10 | `phone` | character varying(50) | Y |  |  |
| 11 | `agreed_terms` | boolean | Y |  | false |
| 12 | `agreed_privacy` | boolean | Y |  | false |
| 13 | `terms_agreed_at` | timestamp with time zone | Y |  |  |
| 14 | `privacy_agreed_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_users_pkey`
- `v4_users_email_key`
- `idx_v4_users_email`

---

#### `account_rate_quotas` [공통]

행 수: 8 | 크기: 72 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `quota_id` | bigint | N | PK | nextval('account_rate_quotas_q |
| 2 | `account_id` | bigint | N |  |  |
| 3 | `broker_type` | character varying(10) | N |  |  |
| 4 | `max_rps` | numeric | N |  |  |
| 5 | `min_rps` | numeric | N |  | 1.0 |
| 6 | `burst_limit` | integer | N |  | 5 |
| 7 | `version` | integer | N |  | 1 |
| 8 | `last_reset_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `account_rate_quotas_pkey`
- `account_rate_quotas_account_id_key`

---

#### `account_snapshots` [공통]

행 수: 470 | 크기: 104 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('account_snapshots_id_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `total_assets` | integer | Y |  | 0 |
| 4 | `total_deposit` | integer | Y |  | 0 |
| 5 | `total_purchase` | integer | Y |  | 0 |
| 6 | `total_evaluation` | integer | Y |  | 0 |
| 7 | `total_profit` | integer | Y |  | 0 |
| 8 | `profit_rate` | real | Y |  | 0.0 |
| 9 | `snapshot_time` | timestamp without time zone | N |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `account_snapshots_pkey`

---

#### `accounts` [공통]

행 수: 8 | 크기: 144 kB | 최신: 2026-02-20

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `account_id` | bigint | N | PK | nextval('accounts_account_id_s |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `broker_type` | character varying(10) | N |  |  |
| 4 | `account_number` | character varying(30) | N |  |  |
| 5 | `account_alias` | character varying(50) | Y |  |  |
| 6 | `is_mock` | boolean | N |  | true |
| 7 | `enc_app_key` | text | N |  |  |
| 8 | `enc_app_secret` | text | N |  |  |
| 9 | `enc_token` | text | Y |  |  |
| 10 | `token_expires_at` | timestamp with time zone | Y |  |  |
| 11 | `kis_config_id` | integer | Y |  |  |
| 12 | `daily_order_limit` | numeric | N |  | 0 |
| 13 | `buy_blocked` | boolean | N |  | false |
| 14 | `buy_blocked_at` | timestamp with time zone | Y |  |  |
| 15 | `buy_block_reason` | character varying(100) | Y |  |  |
| 16 | `is_active` | boolean | N |  | true |
| 17 | `created_at` | timestamp with time zone | N |  | now() |
| 18 | `updated_at` | timestamp with time zone | N |  | now() |
| 19 | `total_deposit` | numeric | Y |  | 0 |
| 20 | `total_evaluation` | numeric | Y |  | 0 |

**인덱스:**

- `accounts_pkey`
- `accounts_user_id_broker_type_account_number_key`
- `idx_accounts_user`
- `idx_accounts_broker`
- `idx_accounts_kis_config`
- `idx_accounts_active_broker`

---

#### `claude_usage_log` [공통]

행 수: 388 | 크기: 152 kB | 최신: 2026-03-09

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('claude_usage_log_id_s |
| 2 | `created_at` | timestamp without time zone | Y |  | now() |
| 3 | `project` | character varying(50) | Y |  |  |
| 4 | `filename` | character varying(255) | Y |  |  |
| 5 | `model` | character varying(100) | Y |  |  |
| 6 | `input_tokens` | integer | Y |  | 0 |
| 7 | `output_tokens` | integer | Y |  | 0 |
| 8 | `cache_read_tokens` | integer | Y |  | 0 |
| 9 | `cache_create_tokens` | integer | Y |  | 0 |
| 10 | `cost_usd` | numeric | Y |  | 0 |
| 11 | `duration_ms` | integer | Y |  | 0 |
| 12 | `session_id` | character varying(100) | Y |  |  |
| 13 | `account` | character varying(50) | Y |  |  |

**인덱스:**

- `claude_usage_log_pkey`
- `idx_claude_usage_project`
- `idx_claude_usage_created`

---

#### `kis_configs` [공통]

행 수: 5 | 크기: 328 kB | 최신: 2026-03-28

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('kis_configs_id_seq':: |
| 2 | `user_id` | integer | N |  |  |
| 3 | `app_key` | character varying(255) | N |  |  |
| 4 | `app_secret` | text | N |  |  |
| 5 | `account_number` | character varying(50) | N |  |  |
| 6 | `account_product_code` | character varying(10) | Y |  |  |
| 7 | `is_production` | boolean | Y |  |  |
| 8 | `access_token` | text | Y |  |  |
| 9 | `token_expires_at` | timestamp without time zone | Y |  |  |
| 10 | `is_active` | boolean | Y |  |  |
| 11 | `is_verified` | boolean | Y |  |  |
| 12 | `last_verified_at` | timestamp without time zone | Y |  |  |
| 13 | `last_error` | text | Y |  |  |
| 14 | `error_count` | integer | Y |  |  |
| 15 | `created_at` | timestamp without time zone | Y |  | now() |
| 16 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `kis_configs_pkey`
- `kis_configs_user_id_key`

---

#### `llm_cost_daily` [공통]

행 수: 83 | 크기: 112 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('llm_cost_daily_id_seq |
| 2 | `date` | date | N |  |  |
| 3 | `user_id` | bigint | N |  |  |
| 4 | `request_type` | character varying(32) | N |  |  |
| 5 | `vendor` | character varying(16) | N |  |  |
| 6 | `model` | character varying(64) | N |  |  |
| 7 | `total_calls` | integer | N |  | 0 |
| 8 | `total_input_tokens` | bigint | N |  | 0 |
| 9 | `total_output_tokens` | bigint | N |  | 0 |
| 10 | `total_cost_usd` | numeric | N |  | 0 |
| 11 | `cache_hit_count` | integer | N |  | 0 |
| 12 | `failover_count` | integer | N |  | 0 |
| 13 | `avg_latency_ms` | integer | N |  | 0 |
| 14 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `llm_cost_daily_pkey`
- `llm_cost_daily_date_user_id_request_type_vendor_model_key`
- `idx_llm_cost_daily_date`
- `idx_llm_cost_daily_user`

---

#### `llm_requests` [공통]

행 수: 1,004 | 크기: 512 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('llm_requests_id_seq': |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `session_id` | character varying(64) | N |  |  |
| 4 | `request_type` | character varying(32) | N |  |  |
| 5 | `vendor` | character varying(16) | N |  |  |
| 6 | `model` | character varying(64) | N |  |  |
| 7 | `input_tokens` | integer | N |  | 0 |
| 8 | `output_tokens` | integer | N |  | 0 |
| 9 | `cache_creation_tokens` | integer | N |  | 0 |
| 10 | `cache_read_tokens` | integer | N |  | 0 |
| 11 | `cost_usd` | numeric | N |  | 0 |
| 12 | `is_cache_hit` | boolean | N |  | false |
| 13 | `is_failover` | boolean | N |  | false |
| 14 | `is_batch` | boolean | N |  | false |
| 15 | `latency_ms` | integer | N |  | 0 |
| 16 | `error_code` | character varying(32) | Y |  |  |
| 17 | `failover_from_vendor` | character varying(16) | Y |  |  |
| 18 | `failover_from_model` | character varying(64) | Y |  |  |
| 19 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `llm_requests_pkey`
- `idx_llm_req_user_created`
- `idx_llm_req_type_created`
- `idx_llm_req_vendor_created`
- `idx_llm_req_monthly_cost`

---

#### `payments` [공통]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('payments_id_seq'::reg |
| 2 | `user_id` | integer | N |  |  |
| 3 | `plan_type` | character varying(20) | N |  |  |
| 4 | `billing_cycle` | character varying(7) | N |  |  |
| 5 | `amount` | real | N |  |  |
| 6 | `imp_uid` | character varying(100) | Y |  |  |
| 7 | `merchant_uid` | character varying(100) | Y |  |  |
| 8 | `status` | character varying(9) | Y |  |  |
| 9 | `pg_response` | text | Y |  |  |
| 10 | `fail_reason` | character varying(255) | Y |  |  |
| 11 | `completed_at` | timestamp without time zone | Y |  |  |
| 12 | `refunded_at` | timestamp without time zone | Y |  |  |
| 13 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `payments_imp_uid_key`
- `payments_merchant_uid_key`
- `payments_pkey`

---

#### `social_accounts` [공통]

행 수: 5 | 크기: 64 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('social_accounts_id_se |
| 2 | `user_id` | integer | N |  |  |
| 3 | `provider` | character varying(50) | N |  |  |
| 4 | `provider_user_id` | character varying(255) | N |  |  |
| 5 | `email` | character varying(255) | Y |  |  |
| 6 | `name` | character varying(100) | Y |  |  |
| 7 | `profile_image` | character varying(500) | Y |  |  |
| 8 | `access_token` | character varying(500) | Y |  |  |
| 9 | `refresh_token` | character varying(500) | Y |  |  |
| 10 | `token_expires_at` | timestamp without time zone | Y |  |  |
| 11 | `is_active` | boolean | Y |  |  |
| 12 | `created_at` | timestamp without time zone | Y |  | now() |
| 13 | `updated_at` | timestamp without time zone | Y |  |  |
| 14 | `last_login_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `social_accounts_pkey`

---

#### `user_push_subscriptions` [공통]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('user_push_subscriptio |
| 2 | `user_id` | integer | N |  |  |
| 3 | `endpoint` | text | N |  |  |
| 4 | `p256dh` | text | N |  |  |
| 5 | `auth` | text | N |  |  |
| 6 | `expiration_time` | integer | Y |  |  |
| 7 | `is_active` | integer | Y |  | 1 |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |
| 9 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `user_push_subscriptions_endpoint_key`
- `user_push_subscriptions_pkey`

---

#### `user_sessions` [공통]

행 수: 2 | 크기: 248 kB | 최신: 2026-03-29

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `session_id` | bigint | N | PK | nextval('user_sessions_session |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `refresh_token` | character varying(512) | N |  |  |
| 4 | `device_info` | character varying(255) | Y |  |  |
| 5 | `ip_address` | inet | Y |  |  |
| 6 | `expires_at` | timestamp with time zone | N |  |  |
| 7 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `user_sessions_pkey`
- `user_sessions_refresh_token_key`
- `idx_sessions_user`
- `idx_sessions_token`
- `idx_sessions_expires`

---

#### `user_settings` [공통]

행 수: 10 | 크기: 88 kB | 최신: 2026-02-11

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('user_settings_id_seq' |
| 2 | `user_id` | integer | N |  |  |
| 3 | `telegram_bot_token` | character varying(255) | Y |  |  |
| 4 | `telegram_chat_id` | character varying(100) | Y |  |  |
| 5 | `telegram_buy_alert` | boolean | Y |  |  |
| 6 | `telegram_sell_alert` | boolean | Y |  |  |
| 7 | `telegram_daily_report` | boolean | Y |  |  |
| 8 | `telegram_error_alert` | boolean | Y |  |  |
| 9 | `email_address` | character varying(255) | Y |  |  |
| 10 | `email_weekly_report` | boolean | Y |  |  |
| 11 | `email_monthly_report` | boolean | Y |  |  |
| 12 | `email_loss_alert` | boolean | Y |  |  |
| 13 | `auto_trading_enabled` | boolean | Y |  |  |
| 14 | `max_investment_amount` | integer | Y |  |  |
| 15 | `max_positions` | integer | Y |  |  |
| 16 | `trading_start_time` | character varying(10) | Y |  |  |
| 17 | `trading_end_time` | character varying(10) | Y |  |  |
| 18 | `use_market_order` | boolean | Y |  |  |
| 19 | `stop_loss_percent` | real | Y |  |  |
| 20 | `daily_loss_limit` | real | Y |  |  |
| 21 | `take_profit_percent` | real | Y |  |  |
| 22 | `use_trailing_stop` | boolean | Y |  |  |
| 23 | `trailing_stop_percent` | real | Y |  |  |
| 24 | `investment_experience` | character varying(50) | Y |  |  |
| 25 | `risk_tolerance` | character varying(50) | Y |  |  |
| 26 | `created_at` | timestamp without time zone | Y |  |  |
| 27 | `updated_at` | timestamp without time zone | Y |  |  |
| 28 | `ai_auto_trading_enabled` | boolean | Y |  | false |
| 29 | `unfilled_mode` | character varying(50) | Y |  | 'MANUAL'::character varying |
| 30 | `unfilled_timeout` | integer | Y |  | 60 |
| 31 | `notify_trade` | boolean | Y |  | true |
| 32 | `notify_stop_loss` | boolean | Y |  | true |
| 33 | `notify_take_profit` | boolean | Y |  | true |
| 34 | `notify_daily_report` | boolean | Y |  | false |
| 35 | `default_stop_loss_pct` | numeric | Y |  | 5.00 |
| 36 | `default_take_profit_pct` | numeric | Y |  | 10.00 |
| 37 | `default_invest_amount` | numeric | Y |  | 1000000 |
| 38 | `theme` | character varying(50) | Y |  | 'light'::character varying |

**인덱스:**

- `user_settings_pkey`
- `user_settings_user_id_key`

---

#### `user_strategies` [공통]

행 수: 181 | 크기: 104 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('user_strategies_id_se |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_id` | character varying(50) | N |  |  |
| 4 | `is_active` | boolean | Y |  |  |
| 5 | `rank` | integer | Y |  |  |
| 6 | `win_rate` | real | Y |  |  |
| 7 | `avg_return` | real | Y |  |  |
| 8 | `total_trades` | integer | Y |  |  |
| 9 | `last_executed` | timestamp without time zone | Y |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |
| 11 | `updated_at` | timestamp without time zone | Y |  |  |
| 12 | `dynamic_weight` | real | Y |  | 1.0 |
| 13 | `last_rebalance_at` | timestamp without time zone | Y |  |  |
| 14 | `performance_score` | real | Y |  | 50.0 |
| 15 | `is_pinned` | integer | Y |  | 0 |
| 16 | `weight` | numeric | Y |  | 0.3333 |

**인덱스:**

- `idx_user_strategies_strategy_id`
- `idx_user_strategies_user_id`
- `user_strategies_pkey`

---

#### `users` [공통]

행 수: 13 | 크기: 80 kB | 최신: 2099-12-31

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('users_id_seq'::regcla |
| 2 | `email` | character varying(255) | N |  |  |
| 3 | `name` | character varying(255) | N |  |  |
| 4 | `phone` | character varying(50) | Y |  |  |
| 5 | `hashed_password` | character varying(255) | Y |  |  |
| 6 | `role` | character varying(11) | Y |  |  |
| 7 | `plan_type` | character varying(10) | Y |  |  |
| 8 | `is_active` | boolean | Y |  |  |
| 9 | `is_verified` | boolean | Y |  |  |
| 10 | `agreed_terms` | boolean | Y |  |  |
| 11 | `agreed_privacy` | boolean | Y |  |  |
| 12 | `agreed_marketing` | boolean | Y |  |  |
| 13 | `subscription_end` | timestamp without time zone | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  | now() |
| 15 | `updated_at` | timestamp without time zone | Y |  |  |
| 16 | `last_login` | timestamp without time zone | Y |  |  |

**인덱스:**

- `ix_users_email`
- `users_pkey`

---

#### `waverider_configs` [공통]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('waverider_configs_id_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `total_capital` | double precision | Y |  |  |
| 4 | `max_position_ratio` | double precision | Y |  |  |
| 5 | `min_confidence` | double precision | Y |  |  |
| 6 | `stop_loss_pct` | double precision | Y |  |  |
| 7 | `take_profit_pct` | double precision | Y |  |  |
| 8 | `intro_allocation` | double precision | Y |  |  |
| 9 | `growth_allocation` | double precision | Y |  |  |
| 10 | `maturity_allocation` | double precision | Y |  |  |
| 11 | `decline_allocation` | double precision | Y |  |  |
| 12 | `max_daily_loss` | double precision | Y |  |  |
| 13 | `max_consecutive_losses` | integer | Y |  |  |
| 14 | `is_active` | boolean | Y |  |  |
| 15 | `is_auto_trading` | boolean | Y |  |  |
| 16 | `created_at` | timestamp without time zone | Y |  |  |
| 17 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `waverider_configs_pkey`
- `waverider_configs_user_id_key`
- `ix_waverider_configs_id`

---


### [INVESTOR]

#### `go100_etf_flow_daily` [GO100]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_etf_flow_daily_ |
| 2 | `trade_date` | date | N |  |  |
| 3 | `etf_code` | character varying(20) | N |  |  |
| 4 | `etf_name` | character varying(100) | Y |  |  |
| 5 | `nav` | double precision | Y |  |  |
| 6 | `fund_flow` | bigint | Y |  |  |
| 7 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_etf_flow_daily_pkey`
- `go100_etf_flow_daily_trade_date_etf_code_key`

---

#### `v4_capital_flow` [V4.1]

행 수: 1 | 크기: 64 kB | 최신: 2026-03-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_capital_flow_id_se |
| 2 | `flow_id` | uuid | N |  | gen_random_uuid() |
| 3 | `from_stock` | character varying(20) | Y |  |  |
| 4 | `from_desk` | integer | Y |  |  |
| 5 | `to_stock` | character varying(20) | Y |  |  |
| 6 | `to_desk` | integer | Y |  |  |
| 7 | `amount` | bigint | N |  | 0 |
| 8 | `flow_reason` | text | Y |  |  |
| 9 | `priority_score` | numeric | Y |  |  |
| 10 | `executed_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_capital_flow_pkey`
- `idx_capital_flow_executed`
- `idx_capital_flow_to_stock`

---

#### `v4_investor_daily` [V4.1]

행 수: 2,641,752 | 크기: 1116 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_investor_daily_id_ |
| 2 | `stock_code` | character varying(12) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `foreign_buy_qty` | bigint | Y |  | 0 |
| 5 | `foreign_sell_qty` | bigint | Y |  | 0 |
| 6 | `foreign_net_qty` | bigint | Y |  | 0 |
| 7 | `foreign_net_amount` | bigint | Y |  | 0 |
| 8 | `institution_buy_qty` | bigint | Y |  | 0 |
| 9 | `institution_sell_qty` | bigint | Y |  | 0 |
| 10 | `institution_net_qty` | bigint | Y |  | 0 |
| 11 | `institution_net_amount` | bigint | Y |  | 0 |
| 12 | `individual_net_qty` | bigint | Y |  | 0 |
| 13 | `individual_net_amount` | bigint | Y |  | 0 |
| 14 | `foreign_hold_qty` | bigint | Y |  | 0 |
| 15 | `foreign_hold_ratio` | numeric | Y |  | 0 |
| 16 | `program_buy_amount` | bigint | Y |  | 0 |
| 17 | `program_sell_amount` | bigint | Y |  | 0 |
| 18 | `program_net_amount` | bigint | Y |  | 0 |
| 19 | `consecutive_foreign_buy_days` | integer | Y |  | 0 |
| 20 | `consecutive_institution_buy_days` | integer | Y |  | 0 |
| 21 | `collected_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_investor_daily_pkey`
- `v4_investor_daily_stock_code_trade_date_key`
- `idx_v4_investor_daily_stock_date`
- `idx_v4_investor_daily_date`
- `idx_v4_investor_daily_foreign_net`
- `idx_v4_investor_daily_inst_net`
- `idx_investor_daily_stock_date`

---

#### `v4_market_investor_daily` [V4.1]

행 수: 3,658 | 크기: 1792 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_market_investor_da |
| 2 | `market` | character varying(10) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `index_close` | numeric | Y |  |  |
| 5 | `foreign_net_qty` | bigint | Y |  |  |
| 6 | `institution_net_qty` | bigint | Y |  |  |
| 7 | `individual_net_qty` | bigint | Y |  |  |
| 8 | `foreign_net_amount` | bigint | Y |  |  |
| 9 | `institution_net_amount` | bigint | Y |  |  |

**인덱스:**

- `v4_market_investor_daily_pkey`
- `v4_market_investor_daily_market_trade_date_key`

---

#### `v4_program_trades` [V4.1]

행 수: 287 | 크기: 120 kB | 최신: 2026-02-25

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_program_trades_id_ |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `program_buy_amount` | bigint | Y |  | 0 |
| 5 | `program_sell_amount` | bigint | Y |  | 0 |
| 6 | `program_net_amount` | bigint | Y |  | 0 |
| 7 | `arbitrage_buy_amount` | bigint | Y |  | 0 |
| 8 | `arbitrage_sell_amount` | bigint | Y |  | 0 |
| 9 | `non_arbitrage_buy_amount` | bigint | Y |  | 0 |
| 10 | `non_arbitrage_sell_amount` | bigint | Y |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_program_trades_pkey`
- `v4_program_trades_stock_code_trade_date_key`
- `idx_program_trades_date`

---

#### `v4_supply_chain` [V4.1]

행 수: 1,012 | 크기: 176 kB | 최신: 2026-03-07

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_supply_chain_id_se |
| 2 | `supplier_symbol` | character varying(20) | N |  |  |
| 3 | `customer_symbol` | character varying(20) | Y |  |  |
| 4 | `customer_name` | character varying(200) | Y |  |  |
| 5 | `relationship_type` | character varying(50) | Y |  |  |
| 6 | `revenue_share` | numeric | Y |  |  |
| 7 | `source` | character varying(50) | Y |  |  |
| 8 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_supply_chain_pkey`
- `idx_supply_supplier`

---

#### `daily_investor_stats` [공통]

행 수: 0 | 크기: 48 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('daily_investor_stats_ |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `date` | character varying(8) | N |  |  |
| 4 | `foreign_net_buy` | double precision | Y |  |  |
| 5 | `inst_net_buy` | double precision | Y |  |  |
| 6 | `trust_net_buy` | double precision | Y |  |  |
| 7 | `pension_net_buy` | double precision | Y |  |  |
| 8 | `credit_ratio` | double precision | Y |  |  |
| 9 | `program_net_buy` | double precision | Y |  |  |
| 10 | `created_at` | character varying | Y |  | now() |

**인덱스:**

- `daily_investor_stats_pkey`
- `ix_daily_investor_stats_date`
- `idx_daily_investor_stats_code_date`
- `ix_daily_investor_stats_id`
- `ix_daily_investor_stats_stock_code`

---

#### `market_turnover_daily` [공통]

행 수: 26,148 | 크기: 3264 kB | 최신: 2026-02-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('market_turnover_daily |
| 2 | `trade_date` | date | N |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `stock_name` | character varying(255) | Y |  |  |
| 5 | `turnover_value` | real | Y |  | 0 |
| 6 | `rank` | integer | Y |  | 0 |
| 7 | `source` | text | Y |  | 'KIS'::text |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_turnover_date`
- `market_turnover_daily_pkey`
- `idx_turnover_code`

---


### [MARKET]

#### `go100_delisted_ohlcv` [GO100]

행 수: 24,127 | 크기: 4336 kB | 최신: 2026-02-20

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_delisted_ohlcv_ |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `open_price` | integer | Y |  |  |
| 5 | `high_price` | integer | Y |  |  |
| 6 | `low_price` | integer | Y |  |  |
| 7 | `close_price` | integer | Y |  |  |
| 8 | `volume` | bigint | Y |  | 0 |
| 9 | `change_pct` | real | Y |  |  |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_delisted_ohlcv_pkey`
- `go100_delisted_ohlcv_stock_code_trade_date_key`
- `idx_go100_delisted_ohlcv_code`
- `idx_go100_delisted_ohlcv_date`

---

#### `go100_nxt_ohlcv_daily` [GO100]

행 수: 136,891 | 크기: 55 MB | 최신: 2026-03-25

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `stock_code` | character varying(12) | N | PK |  |
| 2 | `trade_date` | character(8) | N | PK |  |
| 3 | `open_price` | bigint | Y |  |  |
| 4 | `high_price` | bigint | Y |  |  |
| 5 | `low_price` | bigint | Y |  |  |
| 6 | `close_price` | bigint | Y |  |  |
| 7 | `volume` | bigint | Y |  |  |
| 8 | `trade_amount` | bigint | Y |  |  |
| 9 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_nxt_ohlcv_daily_pkey`
- `idx_go100_nxt_daily_date`
- `idx_go100_nxt_daily_stock`

---

#### `go100_tick_daily_stats` [GO100]

행 수: 465 | 크기: 152 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_tick_daily_stat |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `date` | character varying(8) | N |  |  |
| 4 | `tick_count` | integer | Y |  |  |
| 5 | `avg_trade_size` | numeric | Y |  |  |
| 6 | `large_trade_count` | integer | Y |  |  |
| 7 | `vwap` | numeric | Y |  |  |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_tick_daily_stats_pkey`
- `go100_tick_daily_stats_stock_code_date_key`

---

#### `v4_ohlcv_minute` [V4.1]

행 수: 209,842,343 | 크기: 0 bytes | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_pkey`
- `idx_v4_ohlcv_min_stock_date`
- `idx_v4_ohlcv_min_date`
- `idx_v4_ohlcv_minute_stock_date`
- `idx_v4_ohlcv_minute_date`
- `uq_v4_ohlcv_minute_stock_date_time`

---

#### `v4_ohlcv_minute_2025_01` [V4.1]

행 수: 0 | 크기: 48 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_01_pkey`
- `v4_ohlcv_minute_2025_01_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_01_trade_date_idx`
- `v4_ohlcv_minute_2025_01_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_01_trade_date_idx1`
- `v4_ohlcv_minute_2025_01_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_02` [V4.1]

행 수: 2,414,556 | 크기: 607 MB | 최신: 2025-02-28

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_02_pkey`
- `v4_ohlcv_minute_2025_02_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_02_trade_date_idx`
- `v4_ohlcv_minute_2025_02_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_02_trade_date_idx1`
- `v4_ohlcv_minute_2025_02_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_03` [V4.1]

행 수: 13,955,932 | 크기: 3523 MB | 최신: 2025-03-31

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_03_pkey`
- `v4_ohlcv_minute_2025_03_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_03_trade_date_idx`
- `v4_ohlcv_minute_2025_03_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_03_trade_date_idx1`
- `v4_ohlcv_minute_2025_03_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_04` [V4.1]

행 수: 16,029,505 | 크기: 4055 MB | 최신: 2025-04-30

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_04_pkey`
- `v4_ohlcv_minute_2025_04_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_04_trade_date_idx`
- `v4_ohlcv_minute_2025_04_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_04_trade_date_idx1`
- `v4_ohlcv_minute_2025_04_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_05` [V4.1]

행 수: 14,089,169 | 크기: 3569 MB | 최신: 2025-05-30

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_05_pkey`
- `v4_ohlcv_minute_2025_05_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_05_trade_date_idx`
- `v4_ohlcv_minute_2025_05_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_05_trade_date_idx1`
- `v4_ohlcv_minute_2025_05_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_06` [V4.1]

행 수: 15,400,724 | 크기: 3882 MB | 최신: 2025-06-30

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_06_pkey`
- `v4_ohlcv_minute_2025_06_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_06_trade_date_idx`
- `v4_ohlcv_minute_2025_06_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_06_trade_date_idx1`
- `v4_ohlcv_minute_2025_06_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_07` [V4.1]

행 수: 18,004,785 | 크기: 4525 MB | 최신: 2025-07-31

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_07_pkey`
- `v4_ohlcv_minute_2025_07_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_07_trade_date_idx`
- `v4_ohlcv_minute_2025_07_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_07_trade_date_idx1`
- `v4_ohlcv_minute_2025_07_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_08` [V4.1]

행 수: 14,960,494 | 크기: 3763 MB | 최신: 2025-08-29

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_08_pkey`
- `v4_ohlcv_minute_2025_08_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_08_trade_date_idx`
- `v4_ohlcv_minute_2025_08_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_08_trade_date_idx1`
- `v4_ohlcv_minute_2025_08_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_09` [V4.1]

행 수: 17,128,273 | 크기: 4310 MB | 최신: 2025-09-30

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_09_pkey`
- `v4_ohlcv_minute_2025_09_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_09_trade_date_idx`
- `v4_ohlcv_minute_2025_09_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_09_trade_date_idx1`
- `v4_ohlcv_minute_2025_09_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_10` [V4.1]

행 수: 15,050,700 | 크기: 3786 MB | 최신: 2025-10-31

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_10_pkey`
- `v4_ohlcv_minute_2025_10_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_10_trade_date_idx`
- `v4_ohlcv_minute_2025_10_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_10_trade_date_idx1`
- `v4_ohlcv_minute_2025_10_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_11` [V4.1]

행 수: 16,240,539 | 크기: 4062 MB | 최신: 2025-11-28

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_11_pkey`
- `v4_ohlcv_minute_2025_11_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_11_trade_date_idx`
- `v4_ohlcv_minute_2025_11_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_11_trade_date_idx1`
- `v4_ohlcv_minute_2025_11_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2025_12` [V4.1]

행 수: 16,855,245 | 크기: 4256 MB | 최신: 2025-12-30

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2025_12_pkey`
- `v4_ohlcv_minute_2025_12_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2025_12_trade_date_idx`
- `v4_ohlcv_minute_2025_12_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2025_12_trade_date_idx1`
- `v4_ohlcv_minute_2025_12_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2026_01` [V4.1]

행 수: 18,295,639 | 크기: 4648 MB | 최신: 2026-01-30

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2026_01_pkey`
- `v4_ohlcv_minute_2026_01_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2026_01_trade_date_idx`
- `v4_ohlcv_minute_2026_01_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2026_01_trade_date_idx1`
- `v4_ohlcv_minute_2026_01_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2026_02` [V4.1]

행 수: 15,563,870 | 크기: 3968 MB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2026_02_pkey`
- `v4_ohlcv_minute_2026_02_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2026_02_trade_date_idx`
- `v4_ohlcv_minute_2026_02_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2026_02_trade_date_idx1`
- `v4_ohlcv_minute_2026_02_stock_code_trade_date_trade_time_key`

---

#### `v4_ohlcv_minute_2026_03` [V4.1]

행 수: 15,853,285 | 크기: 4044 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N |  | nextval('v4_ohlcv_minute_id_se |
| 2 | `stock_code` | character varying(10) | N | PK |  |
| 3 | `trade_date` | date | N | PK |  |
| 4 | `trade_time` | time without time zone | N | PK |  |
| 5 | `open_price` | integer | N |  |  |
| 6 | `high_price` | integer | N |  |  |
| 7 | `low_price` | integer | N |  |  |
| 8 | `close_price` | integer | N |  |  |
| 9 | `volume` | bigint | N |  | 0 |
| 10 | `trade_amount` | bigint | N |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_ohlcv_minute_2026_03_pkey`
- `v4_ohlcv_minute_2026_03_stock_code_trade_date_idx`
- `v4_ohlcv_minute_2026_03_trade_date_idx`
- `v4_ohlcv_minute_2026_03_stock_code_trade_date_idx1`
- `v4_ohlcv_minute_2026_03_trade_date_idx1`
- `v4_ohlcv_minute_2026_03_stock_code_trade_date_trade_time_key`

---

#### `v4_sector_index_daily` [V4.1]

행 수: 4,080 | 크기: 648 kB | 최신: 2026-03-07

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_sector_index_daily |
| 2 | `trade_date` | date | N |  |  |
| 3 | `sector_code` | character varying(20) | N |  |  |
| 4 | `sector_name` | character varying(100) | Y |  |  |
| 5 | `close_price` | numeric | Y |  |  |
| 6 | `change_pct` | numeric | Y |  |  |
| 7 | `volume` | bigint | Y |  |  |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_sector_index_daily_pkey`
- `idx_sector_index_date`

---

#### `v4_tick_data` [V4.1]

행 수: 1,054,292 | 크기: 214 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_tick_data_id_seq': |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `tick_time` | timestamp with time zone | N |  |  |
| 4 | `price` | integer | N |  |  |
| 5 | `volume` | integer | N |  |  |
| 6 | `cum_volume` | bigint | Y |  |  |
| 7 | `buy_sell` | character(1) | Y |  |  |
| 8 | `strength` | numeric | Y |  |  |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_tick_data_pkey`
- `idx_tick_data_code_time`

---

#### `v4_vkospi_daily` [V4.1]

행 수: 1,529 | 크기: 400 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_vkospi_daily_id_se |
| 2 | `date` | character varying(8) | N |  |  |
| 3 | `open` | real | Y |  |  |
| 4 | `high` | real | Y |  |  |
| 5 | `low` | real | Y |  |  |
| 6 | `close` | real | N |  |  |
| 7 | `change_rate` | real | Y |  |  |
| 8 | `source` | character varying(20) | Y |  | 'DATA_GO_KR'::character varyin |
| 9 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_vkospi_daily_pkey`
- `v4_vkospi_daily_date_key`
- `idx_v4_vkospi_daily_date`

---

#### `data_global_index_daily` [공통]

행 수: 2,878 | 크기: 680 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('data_global_index_dai |
| 2 | `index_code` | character varying(20) | N |  |  |
| 3 | `index_name` | character varying(50) | Y |  |  |
| 4 | `date` | date | N |  |  |
| 5 | `open` | numeric | Y |  |  |
| 6 | `high` | numeric | Y |  |  |
| 7 | `low` | numeric | Y |  |  |
| 8 | `close` | numeric | N |  |  |
| 9 | `volume` | bigint | Y |  |  |
| 10 | `change_pct` | numeric | Y |  |  |
| 11 | `source` | character varying(20) | Y |  | 'YAHOO'::character varying |
| 12 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `data_global_index_daily_pkey`
- `data_global_index_daily_index_code_date_key`

---

#### `index_daily` [공통]

행 수: 2,151 | 크기: 536 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('index_daily_id_seq':: |
| 2 | `index_code` | character varying(10) | N |  |  |
| 3 | `index_name` | character varying(20) | Y |  |  |
| 4 | `date` | character varying(8) | N |  |  |
| 5 | `open` | real | Y |  |  |
| 6 | `high` | real | Y |  |  |
| 7 | `low` | real | Y |  |  |
| 8 | `close` | real | Y |  |  |
| 9 | `volume` | bigint | Y |  |  |
| 10 | `trade_amount` | real | Y |  |  |
| 11 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `index_daily_index_code_date_key`
- `index_daily_pkey`
- `idx_index_daily_code_date`

---

#### `market_data_min` [공통]

행 수: 18,058,246 | 크기: 3373 MB | 최신: 2026-03-12

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('market_data_min_id_se |
| 2 | `stock_code` | text | N |  |  |
| 3 | `ts` | text | N |  |  |
| 4 | `open` | real | Y |  |  |
| 5 | `high` | real | Y |  |  |
| 6 | `low` | real | Y |  |  |
| 7 | `close` | real | Y |  |  |
| 8 | `volume` | real | Y |  |  |
| 9 | `acml_tr_pbmn` | real | Y |  |  |
| 10 | `chgh_rate` | real | Y |  |  |
| 11 | `volume_power` | real | Y |  |  |
| 12 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `market_data_min_pkey1`
- `market_data_min_stock_code_ts_key1`

---

#### `ohlcv_1m_history` [공통]

행 수: 18,058,246 | 크기: 3951 MB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `stock_code` | text | N |  |  |
| 2 | `stock_name` | text | Y |  |  |
| 3 | `date` | text | N |  |  |
| 4 | `time` | text | N |  |  |
| 5 | `open` | real | Y |  |  |
| 6 | `high` | real | Y |  |  |
| 7 | `low` | real | Y |  |  |
| 8 | `close` | real | Y |  |  |
| 9 | `volume` | real | Y |  |  |

**인덱스:**

- `idx_ohlcv_1m_history_code_date_time`
- `ohlcv_1m_history_stock_code_date_time_key1`

---

#### `ohlcv_daily` [공통]

행 수: 2,687,617 | 크기: 887 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('ohlcv_daily_id_seq':: |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `date` | character varying(8) | N |  |  |
| 4 | `open` | real | Y |  |  |
| 5 | `high` | real | Y |  |  |
| 6 | `low` | real | Y |  |  |
| 7 | `close` | real | Y |  |  |
| 8 | `volume` | bigint | Y |  |  |
| 9 | `trade_amount` | real | Y |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `ohlcv_daily_pkey`
- `ohlcv_daily_stock_code_date_key`
- `idx_ohlcv_daily_code_date`
- `idx_ohlcv_stock_date`

---

#### `ohlcv_monthly` [공통]

행 수: 89,307 | 크기: 13 MB | 최신: 2026-02-11

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('ohlcv_monthly_id_seq' |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `date` | character varying(8) | N |  |  |
| 4 | `open` | real | Y |  |  |
| 5 | `high` | real | Y |  |  |
| 6 | `low` | real | Y |  |  |
| 7 | `close` | real | Y |  |  |
| 8 | `volume` | bigint | Y |  |  |
| 9 | `trade_amount` | real | Y |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `ohlcv_monthly_pkey`
- `ohlcv_monthly_stock_code_date_key`

---

#### `ohlcv_weekly` [공통]

행 수: 357,381 | 크기: 50 MB | 최신: 2026-02-11

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('ohlcv_weekly_id_seq': |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `date` | character varying(8) | N |  |  |
| 4 | `open` | real | Y |  |  |
| 5 | `high` | real | Y |  |  |
| 6 | `low` | real | Y |  |  |
| 7 | `close` | real | Y |  |  |
| 8 | `volume` | bigint | Y |  |  |
| 9 | `trade_amount` | real | Y |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `ohlcv_weekly_pkey`
- `ohlcv_weekly_stock_code_date_key`

---

#### `price_tick_snapshots` [공통]

행 수: 35,865 | 크기: 4640 kB | 최신: 2026-02-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('price_tick_snapshots_ |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `ts` | timestamp without time zone | N |  |  |
| 4 | `price` | real | Y |  | 0 |
| 5 | `cumulative_volume` | real | Y |  | 0 |
| 6 | `volume_delta` | real | Y |  | 0 |
| 7 | `change_rate` | real | Y |  | 0 |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_price_tick_code_time`
- `price_tick_snapshots_pkey`

---


### [NEWS]

#### `go100_news_items` [GO100]

행 수: 2,782,216 | 크기: 2499 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_news_items_id_s |
| 2 | `srno` | character varying(30) | N |  |  |
| 3 | `provider_code` | character varying(2) | N |  |  |
| 4 | `provider_name` | character varying(30) | Y |  |  |
| 5 | `data_date` | date | N |  |  |
| 6 | `data_time` | time without time zone | N |  |  |
| 7 | `title` | text | N |  |  |
| 8 | `category_code` | character varying(20) | Y |  |  |
| 9 | `stock_code1` | character varying(12) | Y |  |  |
| 10 | `stock_code2` | character varying(12) | Y |  |  |
| 11 | `stock_code3` | character varying(12) | Y |  |  |
| 12 | `stock_name1` | character varying(40) | Y |  |  |
| 13 | `stock_name2` | character varying(40) | Y |  |  |
| 14 | `stock_name3` | character varying(40) | Y |  |  |
| 15 | `is_disclosure` | boolean | Y |  | false |
| 16 | `raw_json` | jsonb | Y |  |  |
| 17 | `collected_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_news_items_pkey`
- `go100_news_items_srno_key`
- `idx_go100_news_date`
- `idx_go100_news_stock`
- `idx_go100_news_provider`
- `idx_go100_news_disclosure`

---


### [POSITION]

#### `go100_live_orders` [GO100]

행 수: 57 | 크기: 136 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `order_id` | integer | N | PK | nextval('go100_live_orders_ord |
| 2 | `user_id` | integer | N |  |  |
| 3 | `account_id` | character varying(20) | Y |  |  |
| 4 | `card_id` | integer | Y |  |  |
| 5 | `stock_code` | character varying(10) | N |  |  |
| 6 | `stock_name` | character varying(50) | Y |  |  |
| 7 | `order_type` | character varying(10) | N |  |  |
| 8 | `quantity` | integer | N |  |  |
| 9 | `target_price` | integer | Y |  |  |
| 10 | `order_price` | integer | Y |  |  |
| 11 | `filled_price` | integer | Y |  |  |
| 12 | `filled_quantity` | integer | Y |  | 0 |
| 13 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 14 | `kis_order_id` | character varying(50) | Y |  |  |
| 15 | `safety_check_passed` | boolean | Y |  | false |
| 16 | `safety_check_detail` | jsonb | Y |  |  |
| 17 | `error_message` | text | Y |  |  |
| 18 | `created_at` | timestamp with time zone | Y |  | now() |
| 19 | `filled_at` | timestamp with time zone | Y |  |  |
| 20 | `side` | character varying(10) | Y |  |  |

**인덱스:**

- `go100_live_orders_pkey`
- `idx_go100_live_orders_user_date`
- `idx_live_orders_user`
- `idx_live_orders_status`
- `idx_live_orders_stock_code`

---

#### `go100_orderbook_backtest_runs` [GO100]

행 수: 9 | 크기: 96 kB | 최신: 2026-02-24

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `run_id` | integer | N | PK | nextval('go100_orderbook_backt |
| 2 | `strategy_card_id` | integer | Y |  |  |
| 3 | `ticker` | character varying(20) | N |  |  |
| 4 | `timeframe` | character varying(10) | Y |  | '1m'::character varying |
| 5 | `start_date` | date | N |  |  |
| 6 | `end_date` | date | N |  |  |
| 7 | `total_trades` | integer | Y |  | 0 |
| 8 | `win_rate` | numeric | Y |  |  |
| 9 | `total_return` | numeric | Y |  |  |
| 10 | `max_drawdown` | numeric | Y |  |  |
| 11 | `avg_holding_minutes` | integer | Y |  |  |
| 12 | `slippage_model` | character varying(20) | Y |  | 'fixed_bps'::character varying |
| 13 | `slippage_bps` | integer | Y |  | 10 |
| 14 | `result_detail` | jsonb | Y |  |  |
| 15 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 16 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_orderbook_backtest_runs_pkey`
- `idx_go100_ob_bt_card`
- `idx_go100_ob_bt_ticker`
- `idx_go100_ob_bt_status`
- `idx_go100_ob_bt_created`

---

#### `go100_orderbook_daily_stats` [GO100]

행 수: 81 | 크기: 72 kB | 최신: 2026-03-18

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_orderbook_daily |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `date` | character varying(8) | N |  |  |
| 4 | `avg_spread_pct` | numeric | Y |  |  |
| 5 | `avg_bid_depth` | bigint | Y |  |  |
| 6 | `avg_ask_depth` | bigint | Y |  |  |
| 7 | `max_spread_pct` | numeric | Y |  |  |
| 8 | `snapshot_count` | integer | Y |  |  |
| 9 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_orderbook_daily_stats_pkey`
- `go100_orderbook_daily_stats_stock_code_date_key`

---

#### `go100_orders` [GO100]

행 수: 49 | 크기: 96 kB | 최신: 2026-03-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_orders_id_seq': |
| 2 | `portfolio_id` | bigint | N |  |  |
| 3 | `user_id` | integer | N |  |  |
| 4 | `account_id` | integer | N |  |  |
| 5 | `go100_card_id` | bigint | N |  |  |
| 6 | `stock_code` | character varying(20) | N |  |  |
| 7 | `stock_name` | character varying(100) | Y |  |  |
| 8 | `side` | character varying(10) | N |  |  |
| 9 | `order_type` | character varying(20) | N |  | 'MARKET'::character varying |
| 10 | `requested_price` | numeric | Y |  |  |
| 11 | `requested_qty` | integer | N |  |  |
| 12 | `filled_price` | numeric | Y |  |  |
| 13 | `filled_qty` | integer | Y |  | 0 |
| 14 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 15 | `broker_order_no` | character varying(50) | Y |  |  |
| 16 | `is_paper` | boolean | Y |  | false |
| 17 | `error_message` | text | Y |  |  |
| 18 | `created_at` | timestamp with time zone | Y |  | now() |
| 19 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_orders_pkey`
- `idx_go100_orders_user`
- `idx_go100_orders_card`
- `idx_go100_orders_portfolio`

---

#### `go100_paper_orders` [GO100]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `order_id` | integer | N | PK | nextval('go100_paper_orders_or |
| 2 | `account_id` | integer | N |  |  |
| 3 | `card_id` | bigint | Y |  |  |
| 4 | `stock_code` | character varying(10) | N |  |  |
| 5 | `stock_name` | character varying(50) | Y |  |  |
| 6 | `order_type` | character varying(10) | N |  |  |
| 7 | `order_reason` | character varying(30) | Y |  |  |
| 8 | `quantity` | integer | N |  |  |
| 9 | `target_price` | real | N |  |  |
| 10 | `filled_price` | real | Y |  |  |
| 11 | `filled_at` | timestamp without time zone | Y |  |  |
| 12 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 13 | `signal_data` | jsonb | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_paper_orders_pkey`
- `idx_go100_paper_orders_account`
- `idx_go100_paper_orders_status`

---

#### `go100_paper_positions` [GO100]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `position_id` | integer | N | PK | nextval('go100_paper_positions |
| 2 | `account_id` | integer | N |  |  |
| 3 | `card_id` | bigint | Y |  |  |
| 4 | `stock_code` | character varying(10) | N |  |  |
| 5 | `stock_name` | character varying(50) | Y |  |  |
| 6 | `quantity` | integer | N |  |  |
| 7 | `avg_price` | real | N |  |  |
| 8 | `current_price` | real | Y |  |  |
| 9 | `unrealized_pnl` | real | Y |  | 0 |
| 10 | `unrealized_pnl_pct` | real | Y |  | 0 |
| 11 | `entry_date` | timestamp without time zone | N |  |  |
| 12 | `status` | character varying(10) | Y |  | 'OPEN'::character varying |
| 13 | `closed_at` | timestamp without time zone | Y |  |  |
| 14 | `realized_pnl` | real | Y |  |  |
| 15 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_paper_positions_pkey`
- `idx_go100_paper_positions_account`
- `idx_go100_paper_positions_status`

---

#### `go100_paper_trades` [GO100]

행 수: 150 | 크기: 104 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `trade_id` | integer | N | PK | nextval('go100_paper_trades_tr |
| 2 | `session_id` | integer | N |  |  |
| 3 | `ticker` | character varying(20) | N |  |  |
| 4 | `trade_type` | character varying(10) | N |  |  |
| 5 | `quantity` | integer | N |  |  |
| 6 | `price` | numeric | N |  |  |
| 7 | `slippage_bps` | numeric | Y |  | 0 |
| 8 | `commission` | numeric | Y |  | 0 |
| 9 | `executed_at` | timestamp with time zone | Y |  | now() |
| 10 | `signal_source` | character varying(50) | Y |  |  |
| 11 | `pnl` | numeric | Y |  |  |
| 12 | `notes` | text | Y |  |  |

**인덱스:**

- `go100_paper_trades_pkey`
- `idx_pt30_trades_session`
- `idx_pt30_trades_executed`

---

#### `go100_position_sizing` [GO100]

행 수: 1 | 크기: 64 kB | 최신: 2026-02-28

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_position_sizing |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_id` | integer | Y |  |  |
| 4 | `sizing_method` | character varying(30) | N |  | 'FIXED'::character varying |
| 5 | `base_allocation_pct` | numeric | Y |  | 10.00 |
| 6 | `max_allocation_pct` | numeric | Y |  | 25.00 |
| 7 | `take_profit_pct` | numeric | Y |  | 3.00 |
| 8 | `take_profit_ratio` | numeric | Y |  | 50.00 |
| 9 | `stop_loss_pct` | numeric | Y |  | 5.00 |
| 10 | `strategy_weight` | jsonb | Y |  | '{}'::jsonb |
| 11 | `mfe_lookback_days` | integer | Y |  | 60 |
| 12 | `is_active` | boolean | Y |  | true |
| 13 | `created_at` | timestamp with time zone | Y |  | now() |
| 14 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_position_sizing_pkey`
- `idx_go100_position_sizing_user`
- `idx_go100_position_sizing_strategy`

---

#### `go100_positions` [GO100]

행 수: 60 | 크기: 112 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_positions_id_se |
| 2 | `portfolio_id` | bigint | N |  |  |
| 3 | `user_id` | integer | N |  |  |
| 4 | `account_id` | integer | N |  |  |
| 5 | `go100_card_id` | bigint | N |  |  |
| 6 | `stock_code` | character varying(20) | N |  |  |
| 7 | `stock_name` | character varying(100) | Y |  |  |
| 8 | `quantity` | integer | N |  |  |
| 9 | `remaining_qty` | integer | N |  |  |
| 10 | `entry_price` | numeric | N |  |  |
| 11 | `current_price` | numeric | Y |  |  |
| 12 | `status` | character varying(20) | Y |  | 'OPEN'::character varying |
| 13 | `source` | character varying(20) | Y |  | 'SYSTEM'::character varying |
| 14 | `stop_loss_price` | numeric | Y |  |  |
| 15 | `take_profit_price` | numeric | Y |  |  |
| 16 | `trailing_pct` | numeric | Y |  |  |
| 17 | `peak_price` | numeric | Y |  |  |
| 18 | `entry_date` | date | Y |  |  |
| 19 | `exit_date` | date | Y |  |  |
| 20 | `pnl_amount` | numeric | Y |  |  |
| 21 | `pnl_pct` | numeric | Y |  |  |
| 22 | `created_at` | timestamp with time zone | Y |  | now() |
| 23 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_positions_pkey`
- `idx_go100_pos_portfolio`
- `idx_go100_pos_user`
- `idx_go100_pos_card`

---

#### `go100_trades` [GO100]

행 수: 88 | 크기: 120 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_trades_id_seq': |
| 2 | `order_id` | bigint | Y |  |  |
| 3 | `portfolio_id` | bigint | N |  |  |
| 4 | `user_id` | integer | N |  |  |
| 5 | `account_id` | integer | N |  |  |
| 6 | `go100_card_id` | bigint | N |  |  |
| 7 | `position_id` | bigint | Y |  |  |
| 8 | `stock_code` | character varying(20) | N |  |  |
| 9 | `stock_name` | character varying(100) | Y |  |  |
| 10 | `side` | character varying(10) | N |  |  |
| 11 | `price` | numeric | N |  |  |
| 12 | `quantity` | integer | N |  |  |
| 13 | `amount` | numeric | Y |  |  |
| 14 | `pnl_amount` | numeric | Y |  |  |
| 15 | `pnl_pct` | numeric | Y |  |  |
| 16 | `is_paper` | boolean | Y |  | false |
| 17 | `trade_date` | date | Y |  |  |
| 18 | `traded_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_trades_pkey`
- `idx_go100_trades_user`
- `idx_go100_trades_card`
- `idx_go100_trades_portfolio`
- `idx_go100_trades_date`

---

#### `v4_backtest_trade_log` [V4.1]

행 수: 1,084 | 크기: 256 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_backtest_trade_log |
| 2 | `run_id` | character varying(50) | Y |  |  |
| 3 | `desk_id` | integer | N |  |  |
| 4 | `class_type` | character varying(10) | Y |  |  |
| 5 | `stock_code` | character varying(10) | N |  |  |
| 6 | `stock_name` | character varying(50) | Y |  |  |
| 7 | `entry_date` | character varying(8) | Y |  |  |
| 8 | `entry_price` | numeric | Y |  |  |
| 9 | `exit_date` | character varying(8) | Y |  |  |
| 10 | `exit_price` | numeric | Y |  |  |
| 11 | `quantity` | integer | Y |  |  |
| 12 | `return_pct` | numeric | Y |  |  |
| 13 | `pnl` | bigint | Y |  |  |
| 14 | `exit_reason` | character varying(30) | Y |  |  |
| 15 | `holding_days` | integer | Y |  |  |
| 16 | `sector` | character varying(50) | Y |  |  |

**인덱스:**

- `v4_backtest_trade_log_pkey`
- `idx_bt_trade_run`

---

#### `v4_backtest_trades` [V4.1]

행 수: 213,096 | 크기: 45 MB | 최신: 2026-03-18

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_backtest_trades_id |
| 2 | `session_id` | bigint | Y |  |  |
| 3 | `desk_id` | integer | N |  |  |
| 4 | `stock_code` | character varying(10) | N |  |  |
| 5 | `trade_date` | date | N |  |  |
| 6 | `trade_type` | character varying(10) | N |  |  |
| 7 | `quantity` | integer | N |  |  |
| 8 | `price` | numeric | N |  |  |
| 9 | `amount` | numeric | N |  |  |
| 10 | `split_phase` | integer | Y |  | 0 |
| 11 | `transfer_to` | integer | Y |  |  |
| 12 | `pnl` | numeric | Y |  |  |
| 13 | `pnl_pct` | numeric | Y |  |  |
| 14 | `reason` | character varying(100) | Y |  |  |
| 15 | `card_id` | integer | Y |  |  |
| 16 | `exit_reason` | character varying(30) | Y |  | NULL::character varying |
| 17 | `entry_date` | date | Y |  |  |
| 18 | `exit_date` | date | Y |  |  |
| 19 | `hold_days` | integer | Y |  |  |
| 20 | `entry_datetime` | timestamp without time zone | Y |  |  |
| 21 | `exit_datetime` | timestamp without time zone | Y |  |  |
| 22 | `entry_price` | numeric | Y |  |  |
| 23 | `exit_price` | numeric | Y |  |  |
| 24 | `mfe_pct` | numeric | Y |  |  |
| 25 | `mae_pct` | numeric | Y |  |  |
| 26 | `mfe_price` | numeric | Y |  |  |
| 27 | `mae_price` | numeric | Y |  |  |
| 28 | `regime_at_entry` | character varying(30) | Y |  |  |
| 29 | `indicator_snapshot` | jsonb | Y |  |  |
| 30 | `slippage_pct` | numeric | Y |  |  |
| 31 | `commission` | numeric | Y |  |  |
| 32 | `sector` | character varying(50) | Y |  |  |
| 33 | `strategy_name` | character varying(100) | Y |  |  |
| 34 | `entry_volume` | bigint | Y |  |  |
| 35 | `entry_spread_pct` | numeric | Y |  |  |
| 36 | `buy_at` | timestamp with time zone | Y |  |  |
| 37 | `sell_at` | timestamp with time zone | Y |  |  |
| 38 | `result_id` | integer | Y |  |  |
| 39 | `stock_name` | character varying(100) | Y |  |  |
| 40 | `return_pct` | real | Y |  |  |
| 41 | `holding_days` | integer | Y |  | 0 |

**인덱스:**

- `v4_backtest_trades_pkey`
- `idx_v4_bt_trades_session`
- `idx_bt_trades_buy_at`
- `idx_bt_trades_sell_at`
- `idx_v4bt_trades_session`
- `idx_v4bt_trades_desk`
- `idx_bt_trades_result`

---

#### `v4_broker_trades` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_broker_trades_id_s |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `broker_name` | character varying(50) | Y |  |  |
| 5 | `buy_amount` | bigint | Y |  | 0 |
| 6 | `sell_amount` | bigint | Y |  | 0 |
| 7 | `net_amount` | bigint | Y |  | 0 |
| 8 | `buy_volume` | bigint | Y |  | 0 |
| 9 | `sell_volume` | bigint | Y |  | 0 |
| 10 | `net_volume` | bigint | Y |  | 0 |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_broker_trades_pkey`
- `v4_broker_trades_stock_code_trade_date_broker_name_key`
- `idx_broker_trades_code_date`

---

#### `v4_bt_trades` [V4.1]

행 수: 330 | 크기: 504 kB | 최신: 2026-02-25

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_bt_trades_id_seq': |
| 2 | `session_id` | character varying(64) | N |  |  |
| 3 | `trade_id` | character varying(64) | N |  |  |
| 4 | `stock_code` | character varying(20) | N |  |  |
| 5 | `stock_name` | character varying(100) | Y |  |  |
| 6 | `strategy_name` | character varying(50) | N |  |  |
| 7 | `entry_date` | date | N |  |  |
| 8 | `entry_time` | character varying(10) | N |  |  |
| 9 | `entry_price` | numeric | N |  |  |
| 10 | `entry_quantity` | integer | N |  | 0 |
| 11 | `entry_amount` | bigint | N |  | 0 |
| 12 | `entry_reason` | character varying(200) | Y |  |  |
| 13 | `entry_signals` | jsonb | Y |  | '{}'::jsonb |
| 14 | `exit_date` | date | Y |  |  |
| 15 | `exit_time` | character varying(10) | Y |  |  |
| 16 | `exit_price` | numeric | Y |  |  |
| 17 | `exit_quantity` | integer | Y |  | 0 |
| 18 | `exit_amount` | bigint | Y |  | 0 |
| 19 | `exit_reason` | character varying(50) | Y |  |  |
| 20 | `exit_type` | character varying(20) | Y |  |  |
| 21 | `pnl` | bigint | Y |  | 0 |
| 22 | `pnl_pct` | numeric | Y |  | 0 |
| 23 | `hold_seconds` | integer | Y |  | 0 |
| 24 | `max_profit_pct` | numeric | Y |  | 0 |
| 25 | `max_loss_pct` | numeric | Y |  | 0 |
| 26 | `intended_entry` | boolean | Y |  | true |
| 27 | `intended_exit` | boolean | Y |  | true |
| 28 | `intent_match_score` | numeric | Y |  | 100 |
| 29 | `intent_notes` | character varying(500) | Y |  |  |
| 30 | `created_at` | timestamp with time zone | Y |  | now() |
| 31 | `regime_at_entry` | character varying(30) | Y |  |  |
| 32 | `composite_score` | numeric | Y |  |  |
| 33 | `cs_score` | numeric | Y |  |  |
| 34 | `slot_name` | character varying(20) | Y |  |  |
| 35 | `gross_pnl_pct` | numeric | Y |  |  |
| 36 | `fee_amount` | numeric | Y |  |  |
| 37 | `tax_amount` | numeric | Y |  |  |
| 38 | `slippage_amount` | numeric | Y |  |  |
| 39 | `net_pnl_pct` | numeric | Y |  |  |
| 40 | `is_partial` | boolean | Y |  | false |
| 41 | `partial_sequence` | integer | Y |  | 0 |
| 42 | `remaining_ratio` | numeric | Y |  | 1.0 |
| 43 | `relay_from_strategy` | character varying(30) | Y |  |  |
| 44 | `daily_halted` | boolean | Y |  | false |
| 45 | `fund_available_at_entry` | numeric | Y |  |  |

**인덱스:**

- `v4_bt_trades_pkey`
- `v4_bt_trades_trade_id_key`
- `idx_bt_trades_session`
- `idx_bt_trades_strategy`
- `idx_bt_trades_stock`
- `idx_bt_trades_exit_type`

---

#### `v4_desk2_trades` [V4.1]

행 수: 6 | 크기: 48 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk2_trades_id_se |
| 2 | `trade_date` | date | N |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `stock_type` | character varying(10) | Y |  |  |
| 5 | `signal_name` | character varying(20) | Y |  |  |
| 6 | `entry_time` | timestamp without time zone | Y |  |  |
| 7 | `entry_price` | numeric | Y |  |  |
| 8 | `exit_time` | timestamp without time zone | Y |  |  |
| 9 | `exit_price` | numeric | Y |  |  |
| 10 | `exit_reason` | character varying(20) | Y |  |  |
| 11 | `quantity` | integer | Y |  |  |
| 12 | `gross_pnl` | numeric | Y |  |  |
| 13 | `net_pnl` | numeric | Y |  |  |
| 14 | `gross_pnl_pct` | numeric | Y |  |  |
| 15 | `net_pnl_pct` | numeric | Y |  |  |
| 16 | `commission` | numeric | Y |  |  |
| 17 | `holding_minutes` | integer | Y |  |  |
| 18 | `score` | numeric | Y |  |  |
| 19 | `score_rank` | integer | Y |  |  |
| 20 | `metadata` | jsonb | Y |  |  |
| 21 | `created_at` | timestamp without time zone | Y |  | now() |
| 22 | `peak_price` | numeric | Y |  |  |
| 23 | `trailing_pct` | numeric | Y |  | 30.0 |

**인덱스:**

- `v4_desk2_trades_pkey`
- `idx_desk2_trade_date`

---

#### `v4_desk_paper_trades` [V4.1]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_desk_paper_trades_ |
| 2 | `trade_id` | uuid | N |  |  |
| 3 | `trade_date` | character varying(8) | N |  |  |
| 4 | `stock_code` | character varying(20) | N |  |  |
| 5 | `stock_name` | character varying(100) | Y |  |  |
| 6 | `desk_level` | integer | N |  |  |
| 7 | `action` | character varying(10) | N |  |  |
| 8 | `trigger_type` | character varying(50) | Y |  |  |
| 9 | `trigger_details` | jsonb | Y |  | '{}'::jsonb |
| 10 | `price` | numeric | Y |  |  |
| 11 | `volume` | bigint | Y |  |  |
| 12 | `weight_pct` | numeric | Y |  |  |
| 13 | `pnl_pct` | numeric | Y |  |  |
| 14 | `cumulative_pnl` | numeric | Y |  |  |
| 15 | `notes` | text | Y |  |  |
| 16 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_desk_paper_trades_pkey`
- `idx_paper_trades_date`
- `idx_paper_trades_stock`

---

#### `v4_desk_positions` [V4.1]

행 수: 1 | 크기: 144 kB | 최신: 2026-02-28

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk_positions_id_ |
| 2 | `desk_level` | integer | N |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `entry_date` | date | N |  |  |
| 6 | `entry_price` | numeric | N |  |  |
| 7 | `current_price` | numeric | Y |  |  |
| 8 | `allocated_capital` | numeric | N |  |  |
| 9 | `quantity` | integer | N |  | 0 |
| 10 | `current_return_pct` | numeric | Y |  | 0 |
| 11 | `cumulative_return_pct` | numeric | Y |  | 0 |
| 12 | `stop_loss_price` | numeric | Y |  |  |
| 13 | `exit_trigger` | character varying(50) | Y |  |  |
| 14 | `status` | character varying(10) | N |  | 'ACTIVE'::character varying |
| 15 | `partial_exit_pct` | numeric | Y |  | 0 |
| 16 | `trigger_detail` | jsonb | Y |  |  |
| 17 | `promotion_from` | integer | Y |  |  |
| 18 | `created_at` | timestamp without time zone | Y |  | now() |
| 19 | `updated_at` | timestamp without time zone | Y |  | now() |
| 20 | `desk` | character varying(10) | Y |  |  |
| 21 | `entry_qty` | integer | Y |  |  |
| 22 | `unrealized_pnl_pct` | numeric | Y |  |  |
| 23 | `peak_price` | numeric | Y |  |  |
| 24 | `peak_pnl_pct` | numeric | Y |  |  |
| 25 | `exit_date` | date | Y |  |  |
| 26 | `exit_price` | numeric | Y |  |  |
| 27 | `exit_reason` | character varying(50) | Y |  |  |
| 28 | `realized_pnl_pct` | numeric | Y |  |  |
| 29 | `trigger_codes` | character varying(50) | Y |  |  |
| 30 | `strategy_card_id` | integer | Y |  |  |
| 31 | `promoted_from_desk` | character varying(10) | Y |  |  |
| 32 | `promoted_from_position_id` | integer | Y |  |  |
| 33 | `confidence_score` | numeric | Y |  | 0 |
| 34 | `weekly_ma20_below_weeks` | integer | Y |  | 0 |
| 35 | `theme_alive_flag` | character varying(10) | Y |  | 'ALIVE'::character varying |

**인덱스:**

- `v4_desk_positions_pkey`
- `idx_desk_pos_stock`
- `idx_desk_pos_status`
- `idx_desk_positions_stock`
- `idx_desk_positions_desk`
- `idx_v4_desk_pos_desk`
- `idx_v4_desk_pos_code`
- `idx_v4_desk_pos_status`

---

#### `v4_desk_trade_history` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk_trade_history |
| 2 | `desk` | character varying(10) | N |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `trade_type` | character varying(10) | Y |  |  |
| 6 | `price` | numeric | Y |  |  |
| 7 | `quantity` | integer | Y |  |  |
| 8 | `pnl` | numeric | Y |  |  |
| 9 | `pnl_pct` | numeric | Y |  |  |
| 10 | `traded_at` | timestamp without time zone | Y |  | now() |
| 11 | `strategy` | character varying(50) | Y |  |  |
| 12 | `notes` | text | Y |  |  |

**인덱스:**

- `v4_desk_trade_history_pkey`
- `idx_v4_trade_hist_desk`

---

#### `v4_desk_trade_log` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk_trade_log_id_ |
| 2 | `desk_id` | character varying(10) | N |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `action` | character varying(10) | N |  |  |
| 6 | `price` | numeric | Y |  |  |
| 7 | `quantity` | integer | Y |  |  |
| 8 | `amount` | numeric | Y |  |  |
| 9 | `reason` | text | Y |  |  |
| 10 | `trigger_id` | character varying(50) | Y |  |  |
| 11 | `executed_at` | timestamp without time zone | Y |  | now() |
| 12 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk_trade_log_pkey`
- `idx_trade_log_desk`

---

#### `v4_mock_trades` [V4.1]

행 수: 218 | 크기: 184 kB | 최신: 2026-03-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_mock_trades_id_seq |
| 2 | `trade_date` | date | N |  |  |
| 3 | `ticker` | character varying(20) | N |  |  |
| 4 | `strategy_id` | character varying(20) | N |  |  |
| 5 | `direction` | character varying(4) | N |  | 'BUY'::character varying |
| 6 | `quantity` | integer | Y |  |  |
| 7 | `entry_price` | numeric | Y |  |  |
| 8 | `exit_price` | numeric | Y |  |  |
| 9 | `pnl_pct` | numeric | Y |  |  |
| 10 | `cost_pct` | numeric | Y |  | 0.47 |
| 11 | `slippage_pct` | numeric | Y |  |  |
| 12 | `kis_order_id` | character varying(50) | Y |  |  |
| 13 | `notes` | text | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_mock_trades_pkey`

---

#### `v4_mock_trades_bak_20260324` [V4.1]

행 수: 298 | 크기: 136 kB | 최신: 2026-03-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | Y |  |  |
| 2 | `trade_date` | date | Y |  |  |
| 3 | `ticker` | character varying(20) | Y |  |  |
| 4 | `strategy_id` | character varying(20) | Y |  |  |
| 5 | `direction` | character varying(4) | Y |  |  |
| 6 | `quantity` | integer | Y |  |  |
| 7 | `entry_price` | numeric | Y |  |  |
| 8 | `exit_price` | numeric | Y |  |  |
| 9 | `pnl_pct` | numeric | Y |  |  |
| 10 | `cost_pct` | numeric | Y |  |  |
| 11 | `slippage_pct` | numeric | Y |  |  |
| 12 | `kis_order_id` | character varying(50) | Y |  |  |
| 13 | `notes` | text | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  |  |

---

#### `v4_order_executions` [V4.1]

행 수: 0 | 크기: 48 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_order_executions_i |
| 2 | `position_id` | bigint | Y |  |  |
| 3 | `desk_id` | integer | N |  |  |
| 4 | `config_id` | integer | N |  |  |
| 5 | `stock_code` | character varying(20) | N |  |  |
| 6 | `order_type` | character varying(10) | N |  |  |
| 7 | `order_subtype` | character varying(20) | Y |  |  |
| 8 | `order_price` | numeric | Y |  |  |
| 9 | `order_qty` | integer | N |  |  |
| 10 | `order_time` | timestamp with time zone | N |  |  |
| 11 | `exec_price` | numeric | Y |  |  |
| 12 | `exec_qty` | integer | Y |  |  |
| 13 | `exec_time` | timestamp with time zone | Y |  |  |
| 14 | `exec_status` | character varying(20) | N |  | 'PENDING'::character varying |
| 15 | `slippage_pct` | numeric | Y |  |  |
| 16 | `slippage_amt` | numeric | Y |  |  |
| 17 | `market_bid` | numeric | Y |  |  |
| 18 | `market_ask` | numeric | Y |  |  |
| 19 | `spread_pct` | numeric | Y |  |  |
| 20 | `market_volume_at_order` | bigint | Y |  |  |
| 21 | `kis_order_no` | character varying(50) | Y |  |  |
| 22 | `error_msg` | text | Y |  |  |
| 23 | `created_at` | timestamp with time zone | Y |  | now() |
| 24 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_order_executions_pkey`
- `idx_v4_oe_position`
- `idx_v4_oe_stock_time`
- `idx_v4_oe_desk`
- `idx_v4_oe_status`

---

#### `v4_order_requests` [V4.1]

행 수: 14 | 크기: 128 kB | 최신: 2026-03-02

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_order_requests_id_ |
| 2 | `idempotency_key` | character varying(64) | N |  |  |
| 3 | `user_id` | bigint | N |  |  |
| 4 | `desk_id` | integer | N |  |  |
| 5 | `strategy_id` | character varying(20) | Y |  |  |
| 6 | `ticker` | character varying(20) | N |  |  |
| 7 | `side` | character varying(4) | N |  |  |
| 8 | `quantity` | integer | N |  |  |
| 9 | `price_type` | character varying(10) | N |  | 'MARKET'::character varying |
| 10 | `limit_price` | numeric | Y |  |  |
| 11 | `signal_id` | character varying(100) | Y |  |  |
| 12 | `position_id` | bigint | Y |  |  |
| 13 | `reservation_id` | character varying(64) | Y |  |  |
| 14 | `status` | character varying(20) | N |  | 'PENDING'::character varying |
| 15 | `created_at` | timestamp with time zone | N |  | CURRENT_TIMESTAMP |
| 16 | `updated_at` | timestamp with time zone | N |  | CURRENT_TIMESTAMP |
| 17 | `submitted_at` | timestamp with time zone | Y |  |  |
| 18 | `filled_quantity` | integer | N |  | 0 |
| 19 | `order_no` | character varying(50) | Y |  |  |
| 20 | `message` | text | Y |  |  |
| 21 | `reject_reason` | text | Y |  |  |
| 22 | `source` | character varying(20) | Y |  | 'ORCHESTRATOR'::character vary |
| 23 | `note` | text | Y |  |  |

**인덱스:**

- `v4_order_requests_pkey`
- `ix_v4_order_requests_idempotency`
- `ix_v4_order_requests_user_id`
- `ix_v4_order_requests_created_at`
- `ix_v4_order_requests_status`

---

#### `v4_orderbook_realtime` [V4.1]

행 수: 6,261,154 | 크기: 2134 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_orderbook_realtime |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `captured_at` | timestamp without time zone | N |  |  |
| 4 | `ask_price_1` | integer | Y |  |  |
| 5 | `ask_qty_1` | integer | Y |  |  |
| 6 | `ask_price_2` | integer | Y |  |  |
| 7 | `ask_qty_2` | integer | Y |  |  |
| 8 | `ask_price_3` | integer | Y |  |  |
| 9 | `ask_qty_3` | integer | Y |  |  |
| 10 | `ask_price_4` | integer | Y |  |  |
| 11 | `ask_qty_4` | integer | Y |  |  |
| 12 | `ask_price_5` | integer | Y |  |  |
| 13 | `ask_qty_5` | integer | Y |  |  |
| 14 | `ask_price_6` | integer | Y |  |  |
| 15 | `ask_qty_6` | integer | Y |  |  |
| 16 | `ask_price_7` | integer | Y |  |  |
| 17 | `ask_qty_7` | integer | Y |  |  |
| 18 | `ask_price_8` | integer | Y |  |  |
| 19 | `ask_qty_8` | integer | Y |  |  |
| 20 | `ask_price_9` | integer | Y |  |  |
| 21 | `ask_qty_9` | integer | Y |  |  |
| 22 | `ask_price_10` | integer | Y |  |  |
| 23 | `ask_qty_10` | integer | Y |  |  |
| 24 | `bid_price_1` | integer | Y |  |  |
| 25 | `bid_qty_1` | integer | Y |  |  |
| 26 | `bid_price_2` | integer | Y |  |  |
| 27 | `bid_qty_2` | integer | Y |  |  |
| 28 | `bid_price_3` | integer | Y |  |  |
| 29 | `bid_qty_3` | integer | Y |  |  |
| 30 | `bid_price_4` | integer | Y |  |  |
| 31 | `bid_qty_4` | integer | Y |  |  |
| 32 | `bid_price_5` | integer | Y |  |  |
| 33 | `bid_qty_5` | integer | Y |  |  |
| 34 | `bid_price_6` | integer | Y |  |  |
| 35 | `bid_qty_6` | integer | Y |  |  |
| 36 | `bid_price_7` | integer | Y |  |  |
| 37 | `bid_qty_7` | integer | Y |  |  |
| 38 | `bid_price_8` | integer | Y |  |  |
| 39 | `bid_qty_8` | integer | Y |  |  |
| 40 | `bid_price_9` | integer | Y |  |  |
| 41 | `bid_qty_9` | integer | Y |  |  |
| 42 | `bid_price_10` | integer | Y |  |  |
| 43 | `bid_qty_10` | integer | Y |  |  |
| 44 | `total_ask_qty` | bigint | Y |  |  |
| 45 | `total_bid_qty` | bigint | Y |  |  |
| 46 | `bid_ask_ratio` | double precision | Y |  |  |
| 47 | `spread_pct` | double precision | Y |  |  |
| 48 | `last_price` | integer | Y |  |  |
| 49 | `last_volume` | integer | Y |  |  |
| 50 | `accumulated_volume` | bigint | Y |  |  |

**인덱스:**

- `v4_orderbook_realtime_pkey`
- `idx_ob_rt_stock_time`
- `idx_ob_rt_time`

---

#### `v4_paper_trades` [V4.1]

행 수: 7 | 크기: 32 kB | 최신: 2026-03-01

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_paper_trades_id_se |
| 2 | `strategy` | character varying(10) | N |  |  |
| 3 | `stock_code` | character varying(12) | N |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `buy_date` | date | Y |  |  |
| 6 | `sell_date` | date | Y |  |  |
| 7 | `buy_price` | integer | Y |  |  |
| 8 | `sell_price` | integer | Y |  |  |
| 9 | `quantity` | integer | Y |  |  |
| 10 | `pnl_pct` | real | Y |  |  |
| 11 | `condition_tag` | character varying(64) | Y |  |  |
| 12 | `market_state` | character varying(10) | Y |  |  |
| 13 | `notes` | text | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_paper_trades_pkey`

---

#### `v4_position_extended` [V4.1]

행 수: 3 | 크기: 80 kB | 최신: 2026-02-12

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_position_extended_ |
| 2 | `position_id` | integer | N |  |  |
| 3 | `user_id` | integer | N |  | 1 |
| 4 | `desk_id` | integer | N |  |  |
| 5 | `strategy_id` | character varying(50) | N |  | 'M00'::character varying |
| 6 | `signal_id` | character varying(100) | Y |  |  |
| 7 | `reservation_id` | character varying(100) | Y |  |  |
| 8 | `entry_reason` | text | Y |  |  |
| 9 | `universe_score_at_entry` | double precision | Y |  |  |
| 10 | `mood_score_at_entry` | double precision | Y |  |  |
| 11 | `regime_at_entry` | character varying(50) | Y |  |  |
| 12 | `bet_amount` | bigint | Y |  |  |
| 13 | `confidence_at_entry` | character varying(20) | Y |  |  |
| 14 | `exit_reason` | character varying(50) | Y |  |  |
| 15 | `exit_price` | bigint | Y |  |  |
| 16 | `realized_pnl` | bigint | Y |  |  |
| 17 | `realized_pnl_pct` | double precision | Y |  |  |
| 18 | `hold_days` | integer | Y |  |  |
| 19 | `stop_loss_pct` | double precision | Y |  | 3.0 |
| 20 | `stop_loss_price` | bigint | Y |  |  |
| 21 | `take_profit_pct` | double precision | Y |  | 5.0 |
| 22 | `take_profit_price` | bigint | Y |  |  |
| 23 | `trailing_activated` | integer | Y |  | 0 |
| 24 | `trailing_high_price` | bigint | Y |  |  |
| 25 | `max_hold_days` | integer | Y |  | 5 |
| 26 | `created_at` | timestamp with time zone | Y |  | now() |
| 27 | `updated_at` | timestamp with time zone | Y |  | now() |
| 28 | `closed_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_position_extended_pkey`
- `ix_v4_position_extended_position_id`

---

#### `v4_position_transfers` [V4.1]

행 수: 12 | 크기: 64 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `transfer_id` | bigint | N | PK | nextval('v4_position_transfers |
| 2 | `position_id` | bigint | N |  |  |
| 3 | `from_desk_id` | integer | N |  |  |
| 4 | `to_desk_id` | integer | N |  |  |
| 5 | `transferred_qty` | integer | N |  |  |
| 6 | `remaining_qty` | integer | N |  | 0 |
| 7 | `transfer_type` | character varying(20) | N |  |  |
| 8 | `trigger_conditions` | jsonb | Y |  |  |
| 9 | `pnl_at_transfer` | numeric | Y |  |  |
| 10 | `transferred_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_position_transfers_pkey`
- `idx_v4_pt_position`
- `idx_v4_pt_date`

---

#### `v4_positions` [V4.1]

행 수: 35 | 크기: 240 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_positions_id_seq': |
| 2 | `user_id` | bigint | N |  | 1 |
| 3 | `ticker` | character varying(20) | N |  |  |
| 4 | `quantity` | integer | N |  |  |
| 5 | `entry_price` | bigint | N |  |  |
| 6 | `status` | character varying(20) | N |  | 'OPEN'::character varying |
| 7 | `desk_id` | integer | N |  | 2 |
| 8 | `peak_price` | bigint | N |  | 0 |
| 9 | `stop_loss_price` | bigint | Y |  |  |
| 10 | `trailing_pct` | numeric | Y |  | 3.0 |
| 11 | `target_pct` | numeric | Y |  | 5.0 |
| 12 | `max_hold_days` | integer | Y |  | 5 |
| 13 | `entry_date` | date | Y |  | CURRENT_DATE |
| 14 | `reservation_id` | character varying(100) | Y |  |  |
| 15 | `exit_reason` | character varying(50) | Y |  |  |
| 16 | `exit_price` | bigint | Y |  |  |
| 17 | `exited_at` | timestamp with time zone | Y |  |  |
| 18 | `created_at` | timestamp with time zone | Y |  | now() |
| 19 | `updated_at` | timestamp with time zone | Y |  | now() |
| 20 | `current_price` | numeric | Y |  | NULL::numeric |
| 21 | `pnl_pct` | numeric | Y |  | NULL::numeric |
| 22 | `price_updated_at` | timestamp with time zone | Y |  |  |
| 23 | `account_id` | bigint | Y |  |  |
| 24 | `card_id` | bigint | Y |  |  |
| 25 | `split_phase` | integer | Y |  | 0 |
| 26 | `remaining_qty` | integer | Y |  |  |
| 27 | `original_desk_id` | integer | Y |  |  |
| 28 | `buy_phase` | integer | Y |  | 1 |
| 29 | `signal_id` | bigint | Y |  |  |
| 30 | `chain_id` | uuid | Y |  |  |
| 31 | `buy_at` | timestamp with time zone | Y |  |  |
| 32 | `sell_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_positions_pkey`
- `ix_v4_positions_status`
- `ix_v4_positions_ticker`
- `ix_v4_positions_desk_id`
- `ix_v4_positions_entry_date`
- `idx_v4pos_user`
- `idx_v4pos_account`
- `idx_v4pos_card`
- `idx_v4pos_user_status`
- `idx_v4_positions_signal_id`
- `idx_positions_buy_at`
- `idx_positions_sell_at`

---

#### `v4_positions_backup_20260218` [V4.1]

행 수: 20 | 크기: 40 kB | 최신: 2026-02-18

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | Y |  |  |
| 2 | `user_id` | bigint | Y |  |  |
| 3 | `ticker` | character varying(20) | Y |  |  |
| 4 | `quantity` | integer | Y |  |  |
| 5 | `entry_price` | bigint | Y |  |  |
| 6 | `status` | character varying(20) | Y |  |  |
| 7 | `desk_id` | integer | Y |  |  |
| 8 | `peak_price` | bigint | Y |  |  |
| 9 | `stop_loss_price` | bigint | Y |  |  |
| 10 | `trailing_pct` | numeric | Y |  |  |
| 11 | `target_pct` | numeric | Y |  |  |
| 12 | `max_hold_days` | integer | Y |  |  |
| 13 | `entry_date` | date | Y |  |  |
| 14 | `reservation_id` | character varying(100) | Y |  |  |
| 15 | `exit_reason` | character varying(50) | Y |  |  |
| 16 | `exit_price` | bigint | Y |  |  |
| 17 | `exited_at` | timestamp with time zone | Y |  |  |
| 18 | `created_at` | timestamp with time zone | Y |  |  |
| 19 | `updated_at` | timestamp with time zone | Y |  |  |

---

#### `v4_trade_analysis` [V4.1]

행 수: 0 | 크기: 8192 bytes

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_trade_analysis_id_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `position_id` | integer | N |  |  |
| 4 | `ticker` | character varying(20) | Y |  |  |
| 5 | `entry_date` | date | Y |  |  |
| 6 | `entry_time` | time without time zone | Y |  |  |
| 7 | `entry_price` | integer | Y |  |  |
| 8 | `universe_score` | numeric | Y |  |  |
| 9 | `supply_score` | numeric | Y |  |  |
| 10 | `sector_score` | numeric | Y |  |  |
| 11 | `theme_score` | numeric | Y |  |  |
| 12 | `volume_score` | numeric | Y |  |  |
| 13 | `technical_score` | numeric | Y |  |  |
| 14 | `stock_class` | character varying(20) | Y |  |  |
| 15 | `class_confidence` | character varying(20) | Y |  |  |
| 16 | `desk_id` | integer | Y |  |  |
| 17 | `strategy_id` | character varying(20) | Y |  |  |
| 18 | `market_mood_score` | integer | Y |  |  |
| 19 | `market_regime` | character varying(30) | Y |  |  |
| 20 | `regime_score` | numeric | Y |  |  |
| 21 | `bet_confidence` | character varying(10) | Y |  |  |
| 22 | `bet_size_pct` | numeric | Y |  |  |
| 23 | `bet_amount` | bigint | Y |  |  |
| 24 | `data_quality` | character varying(10) | Y |  |  |
| 25 | `time_reliability` | character varying(20) | Y |  |  |
| 26 | `max_profit_pct` | numeric | Y |  |  |
| 27 | `max_profit_date` | date | Y |  |  |
| 28 | `max_loss_pct` | numeric | Y |  |  |
| 29 | `max_loss_date` | date | Y |  |  |
| 30 | `hold_days` | integer | Y |  |  |
| 31 | `supply_change` | character varying(20) | Y |  |  |
| 32 | `regime_changed` | boolean | N |  |  |
| 33 | `mood_min_during` | numeric | Y |  |  |
| 34 | `class_transferred` | boolean | N |  |  |
| 35 | `transfer_log_id` | integer | Y |  |  |
| 36 | `exit_date` | date | Y |  |  |
| 37 | `exit_time` | time without time zone | Y |  |  |
| 38 | `exit_price` | integer | Y |  |  |
| 39 | `exit_reason` | character varying(30) | Y |  |  |
| 40 | `realized_pnl` | bigint | Y |  |  |
| 41 | `realized_pnl_pct` | numeric | Y |  |  |
| 42 | `slippage_pct` | numeric | Y |  |  |
| 43 | `commission` | bigint | Y |  |  |
| 44 | `price_after_1h` | integer | Y |  |  |
| 45 | `price_after_1d` | integer | Y |  |  |
| 46 | `return_after_1h` | numeric | Y |  |  |
| 47 | `return_after_1d` | numeric | Y |  |  |
| 48 | `early_exit` | boolean | Y |  |  |
| 49 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_trade_analysis_pkey`

---

#### `v4_trade_executions` [V4.1]

행 수: 13 | 크기: 112 kB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_trade_executions_i |
| 2 | `user_id` | bigint | Y |  |  |
| 3 | `account_id` | bigint | Y |  |  |
| 4 | `strategy_id` | integer | Y |  |  |
| 5 | `stock_code` | character varying(20) | N |  |  |
| 6 | `stock_name` | character varying(100) | Y |  |  |
| 7 | `order_type` | character varying(10) | N |  |  |
| 8 | `order_method` | character varying(20) | Y |  | 'market'::character varying |
| 9 | `quantity` | integer | N |  |  |
| 10 | `price` | numeric | Y |  |  |
| 11 | `executed_price` | numeric | Y |  |  |
| 12 | `executed_quantity` | integer | Y |  | 0 |
| 13 | `status` | character varying(20) | Y |  | 'pending'::character varying |
| 14 | `broker_type` | character varying(20) | Y |  |  |
| 15 | `broker_order_id` | character varying(100) | Y |  |  |
| 16 | `error_message` | text | Y |  |  |
| 17 | `created_at` | timestamp without time zone | Y |  | now() |
| 18 | `executed_at` | timestamp without time zone | Y |  |  |
| 19 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_trade_executions_pkey`
- `idx_trade_exec_user`
- `idx_trade_exec_status`
- `idx_trade_exec_account`

---

#### `v4_trade_schedules` [V4.1]

행 수: 5 | 크기: 88 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_trade_schedules_id |
| 2 | `user_id` | bigint | Y |  |  |
| 3 | `strategy_id` | integer | N |  |  |
| 4 | `account_id` | bigint | Y |  |  |
| 5 | `is_active` | boolean | Y |  | true |
| 6 | `run_interval` | character varying(20) | Y |  | 'daily'::character varying |
| 7 | `market_open_only` | boolean | Y |  | true |
| 8 | `invest_amount` | numeric | Y |  |  |
| 9 | `max_stocks` | integer | Y |  | 10 |
| 10 | `max_per_stock_pct` | numeric | Y |  | 10 |
| 11 | `stop_loss_pct` | numeric | Y |  | '-5'::integer |
| 12 | `take_profit_pct` | numeric | Y |  | 15 |
| 13 | `last_run_at` | timestamp without time zone | Y |  |  |
| 14 | `next_run_at` | timestamp without time zone | Y |  |  |
| 15 | `created_at` | timestamp without time zone | Y |  | now() |
| 16 | `updated_at` | timestamp without time zone | Y |  | now() |
| 17 | `card_source` | character varying(10) | N |  | 'v41'::character varying |

**인덱스:**

- `v4_trade_schedules_pkey`
- `idx_trade_sched_active`
- `idx_trade_sched_user`

---

#### `v4_trade_strength_history` [V4.1]

행 수: 10,993,630 | 크기: 1551 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_trade_strength_his |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `recorded_at` | timestamp with time zone | N |  |  |
| 4 | `strength` | numeric | Y |  |  |
| 5 | `buy_count` | integer | Y |  |  |
| 6 | `sell_count` | integer | Y |  |  |
| 7 | `buy_amount` | bigint | Y |  |  |
| 8 | `sell_amount` | bigint | Y |  |  |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_trade_strength_history_pkey`
- `idx_strength_hist_code_date`

---

#### `v4_trades` [V4.1]

행 수: 40 | 크기: 136 kB | 최신: 2026-03-03

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_trades_id_seq'::re |
| 2 | `desk_id` | integer | N |  |  |
| 3 | `class_name` | character varying(20) | N |  |  |
| 4 | `stock_code` | character varying(10) | N |  |  |
| 5 | `stock_name` | character varying(50) | Y |  |  |
| 6 | `side` | character varying(4) | N |  |  |
| 7 | `price` | integer | N |  |  |
| 8 | `qty` | integer | N |  |  |
| 9 | `amount` | bigint | N |  |  |
| 10 | `order_no` | character varying(20) | Y |  |  |
| 11 | `strategy_name` | character varying(50) | Y |  |  |
| 12 | `signal_confidence` | numeric | Y |  |  |
| 13 | `trade_date` | timestamp with time zone | N |  |  |
| 14 | `position_id` | integer | Y |  |  |
| 15 | `pnl_amount` | bigint | Y |  |  |
| 16 | `pnl_pct` | numeric | Y |  |  |
| 17 | `created_at` | timestamp with time zone | Y |  | now() |
| 18 | `user_id` | bigint | Y |  |  |
| 19 | `account_id` | bigint | Y |  |  |
| 20 | `card_id` | bigint | Y |  |  |

**인덱스:**

- `v4_trades_pkey`
- `idx_v4trades_user`
- `idx_v4trades_account`
- `idx_v4trades_card`
- `idx_trades_card`
- `idx_trades_desk_card`

---

#### `v4_trades_backup_20260218` [V4.1]

행 수: 0 | 크기: 0 bytes

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | Y |  |  |
| 2 | `desk_id` | integer | Y |  |  |
| 3 | `class_name` | character varying(20) | Y |  |  |
| 4 | `stock_code` | character varying(10) | Y |  |  |
| 5 | `stock_name` | character varying(50) | Y |  |  |
| 6 | `side` | character varying(4) | Y |  |  |
| 7 | `price` | integer | Y |  |  |
| 8 | `qty` | integer | Y |  |  |
| 9 | `amount` | bigint | Y |  |  |
| 10 | `order_no` | character varying(20) | Y |  |  |
| 11 | `strategy_name` | character varying(50) | Y |  |  |
| 12 | `signal_confidence` | numeric | Y |  |  |
| 13 | `trade_date` | timestamp with time zone | Y |  |  |
| 14 | `position_id` | integer | Y |  |  |
| 15 | `pnl_amount` | bigint | Y |  |  |
| 16 | `pnl_pct` | numeric | Y |  |  |
| 17 | `created_at` | timestamp with time zone | Y |  |  |

---

#### `v4_virtual_trades_full` [V4.1]

행 수: 250 | 크기: 336 kB | 최신: 2026-03-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_virtual_trades_ful |
| 2 | `session_date` | date | N |  |  |
| 3 | `signal_time` | timestamp without time zone | N |  |  |
| 4 | `ticker` | character varying(20) | N |  |  |
| 5 | `strategy_id` | character varying(20) | N |  |  |
| 6 | `approved` | boolean | N |  | false |
| 7 | `blocking_layer` | character varying(50) | Y |  |  |
| 8 | `blocking_reason` | text | Y |  |  |
| 9 | `cs_score` | integer | Y |  |  |
| 10 | `eqs_score` | integer | Y |  |  |
| 11 | `entry_price` | numeric | Y |  |  |
| 12 | `entry_time` | timestamp without time zone | Y |  |  |
| 13 | `quantity` | integer | Y |  |  |
| 14 | `exit_price` | numeric | Y |  |  |
| 15 | `exit_time` | timestamp without time zone | Y |  |  |
| 16 | `exit_reason` | character varying(100) | Y |  |  |
| 17 | `pnl_pct` | numeric | Y |  |  |
| 18 | `pnl_raw_pct` | numeric | Y |  |  |
| 19 | `cost_pct` | numeric | Y |  | 0.47 |
| 20 | `hold_minutes` | integer | Y |  |  |
| 21 | `max_pnl_pct` | numeric | Y |  |  |
| 22 | `min_pnl_pct` | numeric | Y |  |  |
| 23 | `market_regime` | character varying(20) | Y |  |  |
| 24 | `kosdaq_chg_pct` | numeric | Y |  |  |
| 25 | `vkospi_close` | numeric | Y |  |  |
| 26 | `signal_params` | jsonb | Y |  |  |
| 27 | `source` | character varying(20) | Y |  | 'VIRTUAL_KIS_MOCK'::character  |
| 28 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_virtual_trades_full_pkey`
- `idx_vvtf_date`
- `idx_vvtf_ticker`
- `idx_vvtf_strategy`
- `idx_vvtf_approved`

---

#### `v4_virtual_trades_full_bak_20260324` [V4.1]

행 수: 281 | 크기: 136 kB | 최신: 2026-03-23

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | Y |  |  |
| 2 | `session_date` | date | Y |  |  |
| 3 | `signal_time` | timestamp without time zone | Y |  |  |
| 4 | `ticker` | character varying(20) | Y |  |  |
| 5 | `strategy_id` | character varying(20) | Y |  |  |
| 6 | `approved` | boolean | Y |  |  |
| 7 | `blocking_layer` | character varying(50) | Y |  |  |
| 8 | `blocking_reason` | text | Y |  |  |
| 9 | `cs_score` | integer | Y |  |  |
| 10 | `eqs_score` | integer | Y |  |  |
| 11 | `entry_price` | numeric | Y |  |  |
| 12 | `entry_time` | timestamp without time zone | Y |  |  |
| 13 | `quantity` | integer | Y |  |  |
| 14 | `exit_price` | numeric | Y |  |  |
| 15 | `exit_time` | timestamp without time zone | Y |  |  |
| 16 | `exit_reason` | character varying(100) | Y |  |  |
| 17 | `pnl_pct` | numeric | Y |  |  |
| 18 | `pnl_raw_pct` | numeric | Y |  |  |
| 19 | `cost_pct` | numeric | Y |  |  |
| 20 | `hold_minutes` | integer | Y |  |  |
| 21 | `max_pnl_pct` | numeric | Y |  |  |
| 22 | `min_pnl_pct` | numeric | Y |  |  |
| 23 | `market_regime` | character varying(20) | Y |  |  |
| 24 | `kosdaq_chg_pct` | numeric | Y |  |  |
| 25 | `vkospi_close` | numeric | Y |  |  |
| 26 | `signal_params` | jsonb | Y |  |  |
| 27 | `source` | character varying(20) | Y |  |  |
| 28 | `created_at` | timestamp without time zone | Y |  |  |

---

#### `auto_trade_positions` [공통]

행 수: 41 | 크기: 56 kB | 최신: 2026-02-02

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('auto_trade_positions_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_id` | integer | N |  |  |
| 4 | `symbol` | character varying(20) | N |  |  |
| 5 | `quantity` | integer | N |  |  |
| 6 | `entry_price` | real | N |  |  |
| 7 | `current_price` | real | N |  |  |
| 8 | `stop_loss` | real | Y |  |  |
| 9 | `take_profit` | real | Y |  |  |
| 10 | `unrealized_pnl` | real | Y |  | 0 |
| 11 | `status` | character varying(20) | Y |  | 'OPEN'::character varying |
| 12 | `created_at` | timestamp without time zone | Y |  |  |
| 13 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `auto_trade_positions_pkey`

---

#### `autotrade_positions` [공통]

행 수: 84 | 크기: 144 kB | 최신: 2026-02-13

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('autotrade_positions_i |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_id` | character varying(50) | N |  |  |
| 4 | `ticker` | character varying(20) | N |  |  |
| 5 | `side` | character varying(10) | N |  |  |
| 6 | `quantity` | integer | N |  |  |
| 7 | `entry_price` | real | N |  |  |
| 8 | `current_price` | real | Y |  |  |
| 9 | `exit_price` | real | Y |  |  |
| 10 | `unrealized_pnl` | real | Y |  | 0.0 |
| 11 | `realized_pnl` | real | Y |  |  |
| 12 | `stop_loss_price` | real | Y |  |  |
| 13 | `take_profit_price` | real | Y |  |  |
| 14 | `status` | character varying(20) | N |  | 'OPEN'::character varying |
| 15 | `order_id` | character varying(100) | Y |  |  |
| 16 | `created_at` | timestamp without time zone | Y |  | now() |
| 17 | `updated_at` | timestamp without time zone | Y |  | now() |
| 18 | `closed_at` | timestamp without time zone | Y |  |  |
| 19 | `max_holding_minutes` | integer | Y |  |  |
| 20 | `force_close_at_market_end` | boolean | Y |  | true |
| 21 | `owner_strategy_id` | character varying(50) | Y |  |  |
| 22 | `closed_reason` | character varying(50) | Y |  |  |

**인덱스:**

- `ix_autotrade_positions_ticker`
- `ix_autotrade_positions_status`
- `ix_autotrade_positions_user_id`
- `autotrade_positions_pkey`
- `ix_autotrade_positions_created_at`
- `ix_autotrade_positions_strategy_id`

---

#### `compound_trades` [공통]

행 수: 2,970 | 크기: 688 kB | 최신: 2026-01-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('compound_trades_id_se |
| 2 | `portfolio_id` | integer | N |  |  |
| 3 | `user_id` | integer | N |  |  |
| 4 | `strategy_name` | character varying(100) | N |  |  |
| 5 | `strategy_category` | character varying(50) | N |  |  |
| 6 | `symbol` | character varying(20) | Y |  |  |
| 7 | `side` | character varying(10) | N |  |  |
| 8 | `quantity` | integer | N |  |  |
| 9 | `price` | real | N |  |  |
| 10 | `commission` | real | Y |  |  |
| 11 | `allocated_capital` | real | N |  |  |
| 12 | `realized_pnl` | real | Y |  |  |
| 13 | `roi` | real | Y |  |  |
| 14 | `order_id` | character varying(100) | Y |  |  |
| 15 | `execution_time` | timestamp without time zone | Y |  |  |
| 16 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `compound_trades_pkey`
- `idx_compound_trades_execution_time`
- `idx_compound_trades_user_id`

---

#### `dummy_trades_archive` [공통]

행 수: 132,452 | 크기: 42 MB | 최신: 2026-02-01

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('real_trades_id_seq':: |
| 2 | `timestamp` | timestamp without time zone | N |  |  |
| 3 | `account_email` | character varying(255) | N |  |  |
| 4 | `strategy_id` | character varying(50) | N |  |  |
| 5 | `strategy_name` | character varying(255) | N |  |  |
| 6 | `ticker` | character varying(20) | N |  |  |
| 7 | `signal` | character varying(10) | N |  |  |
| 8 | `order_id` | character varying(100) | Y |  |  |
| 9 | `price` | real | N |  |  |
| 10 | `quantity` | integer | N |  |  |
| 11 | `position_size` | real | N |  |  |
| 12 | `filled_price` | real | Y |  |  |
| 13 | `filled_quantity` | integer | Y |  |  |
| 14 | `commission` | real | Y |  | 0.0 |
| 15 | `slippage` | real | Y |  | 0.0 |
| 16 | `status` | character varying(20) | N |  |  |
| 17 | `error_message` | text | Y |  |  |
| 18 | `entry_price` | real | Y |  |  |
| 19 | `exit_price` | real | Y |  |  |
| 20 | `realized_pnl` | real | Y |  | 0.0 |
| 21 | `created_at` | timestamp without time zone | Y |  | now() |
| 22 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `dummy_trades_archive_account_email_idx`
- `dummy_trades_archive_account_email_idx1`
- `dummy_trades_archive_account_email_created_at_status_idx`
- `dummy_trades_archive_created_at_idx`
- `dummy_trades_archive_timestamp_idx`
- `dummy_trades_archive_signal_idx`
- `dummy_trades_archive_status_idx`
- `dummy_trades_archive_strategy_id_idx`
- `dummy_trades_archive_pkey`

---

#### `liquidation_logs` [공통]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `log_id` | bigint | N | PK | nextval('liquidation_logs_log_ |
| 2 | `session_id` | bigint | N |  |  |
| 3 | `order_id` | bigint | Y |  |  |
| 4 | `log_level` | character varying(10) | N |  | 'INFO'::character varying |
| 5 | `event_type` | character varying(30) | N |  |  |
| 6 | `message` | text | N |  |  |
| 7 | `raw_data` | jsonb | Y |  |  |
| 8 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `liquidation_logs_pkey`
- `idx_liq_log_session`
- `idx_liq_log_created`

---

#### `liquidation_orders` [공통]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `order_id` | bigint | N | PK | nextval('liquidation_orders_or |
| 2 | `session_id` | bigint | N |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `stock_name` | character varying(50) | Y |  |  |
| 5 | `target_qty` | integer | N |  |  |
| 6 | `sold_qty` | integer | N |  | 0 |
| 7 | `remaining_qty` | integer | N |  |  |
| 8 | `attempt_count` | integer | N |  | 0 |
| 9 | `max_attempts` | integer | N |  | 4 |
| 10 | `avg_sell_price` | numeric | N |  | 0 |
| 11 | `total_sell_amount` | numeric | N |  | 0 |
| 12 | `status` | character varying(20) | N |  | 'PENDING'::character varying |
| 13 | `last_kis_order_id` | character varying(50) | Y |  |  |
| 14 | `error_message` | text | Y |  |  |
| 15 | `position_id` | bigint | Y |  |  |
| 16 | `created_at` | timestamp with time zone | N |  | now() |
| 17 | `updated_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `liquidation_orders_pkey`
- `idx_liq_ord_session`
- `idx_liq_ord_status`

---

#### `liquidation_sessions` [공통]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `session_id` | bigint | N | PK | nextval('liquidation_sessions_ |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `account_id` | bigint | Y |  |  |
| 4 | `card_id` | bigint | Y |  |  |
| 5 | `trigger_type` | character varying(20) | N |  |  |
| 6 | `status` | character varying(20) | N |  | 'INITIATED'::character varying |
| 7 | `target_count` | integer | N |  | 0 |
| 8 | `success_count` | integer | N |  | 0 |
| 9 | `fail_count` | integer | N |  | 0 |
| 10 | `skip_count` | integer | N |  | 0 |
| 11 | `total_sold_amount` | numeric | N |  | 0 |
| 12 | `buy_block_active` | boolean | N |  | false |
| 13 | `timeout_at` | timestamp with time zone | N |  |  |
| 14 | `started_at` | timestamp with time zone | N |  | now() |
| 15 | `completed_at` | timestamp with time zone | Y |  |  |
| 16 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `liquidation_sessions_pkey`
- `idx_liq_sess_user`
- `idx_liq_sess_status`
- `idx_liq_sess_active`

---

#### `live_positions` [공통]

행 수: 11 | 크기: 96 kB | 최신: 2026-02-06

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('live_positions_id_seq |
| 2 | `user_email` | text | N |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `stock_name` | character varying(255) | N |  |  |
| 5 | `quantity` | integer | N |  |  |
| 6 | `entry_price` | real | N |  |  |
| 7 | `entry_time` | timestamp without time zone | N |  |  |
| 8 | `strategy` | text | N |  |  |
| 9 | `current_price` | real | Y |  |  |
| 10 | `unrealized_pnl` | real | Y |  |  |
| 11 | `unrealized_pnl_pct` | real | Y |  |  |
| 12 | `session_id` | text | N |  |  |
| 13 | `account_number` | text | Y |  |  |
| 14 | `status` | text | Y |  | 'OPEN'::text |
| 15 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_live_pos_session`
- `idx_live_pos_user_status`
- `live_positions_pkey`

---

#### `orderbook_snapshots` [공통]

행 수: 35,894 | 크기: 42 MB | 최신: 2026-02-05

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('orderbook_snapshots_i |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `snapshot_time` | timestamp without time zone | N |  |  |
| 4 | `best_ask_price` | real | Y |  | 0 |
| 5 | `best_bid_price` | real | Y |  | 0 |
| 6 | `total_ask_volume` | real | Y |  | 0 |
| 7 | `total_bid_volume` | real | Y |  | 0 |
| 8 | `asks_json` | text | Y |  |  |
| 9 | `bids_json` | text | Y |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_orderbook_code_time`
- `orderbook_snapshots_pkey`

---

#### `orders` [공통]

행 수: 48 | 크기: 144 kB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('orders_id_seq'::regcl |
| 2 | `user_id` | integer | N |  |  |
| 3 | `signal_id` | integer | Y |  |  |
| 4 | `strategy_id` | character varying(50) | N |  |  |
| 5 | `symbol` | character varying(20) | N |  |  |
| 6 | `side` | character varying(10) | N |  |  |
| 7 | `quantity` | integer | N |  |  |
| 8 | `price` | real | Y |  |  |
| 9 | `order_type` | character varying(20) | N |  | 'MARKET'::character varying |
| 10 | `status` | character varying(20) | N |  | 'PENDING'::character varying |
| 11 | `kis_order_no` | character varying(100) | Y |  |  |
| 12 | `error_message` | text | Y |  |  |
| 13 | `created_at` | timestamp without time zone | Y |  | now() |
| 14 | `filled_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `idx_orders_created_at`
- `idx_orders_status`
- `idx_orders_symbol`
- `idx_orders_user_id`
- `orders_pkey`

---

#### `pending_orders` [공통]

행 수: 7,471 | 크기: 1976 kB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('pending_orders_id_seq |
| 2 | `user_id` | integer | N |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `strategy_name` | character varying(100) | N |  |  |
| 6 | `order_type` | character varying(10) | N |  |  |
| 7 | `target_price` | real | N |  |  |
| 8 | `quantity` | integer | N |  |  |
| 9 | `priority` | integer | Y |  | 0 |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |
| 11 | `expires_at` | timestamp without time zone | Y |  |  |
| 12 | `executed_at` | timestamp without time zone | Y |  |  |
| 13 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 14 | `execution_price` | real | Y |  |  |
| 15 | `notes` | text | Y |  |  |
| 16 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `idx_pending_orders_priority`
- `idx_pending_orders_user_status`
- `pending_orders_pkey`

---

#### `positions` [공통]

행 수: 2,919 | 크기: 456 kB | 최신: 2026-01-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('positions_id_seq'::re |
| 2 | `portfolio_id` | integer | N |  |  |
| 3 | `strategy_name` | character varying(100) | N |  |  |
| 4 | `strategy_category` | character varying(50) | N |  |  |
| 5 | `symbol` | character varying(20) | Y |  |  |
| 6 | `quantity` | integer | Y |  |  |
| 7 | `entry_price` | real | Y |  |  |
| 8 | `current_price` | real | Y |  |  |
| 9 | `allocated_capital` | real | N |  |  |
| 10 | `pnl` | real | Y |  |  |
| 11 | `pnl_percent` | real | Y |  |  |
| 12 | `status` | character varying(6) | N |  |  |
| 13 | `opened_at` | timestamp without time zone | Y |  | now() |
| 14 | `closed_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `positions_pkey`

---

#### `real_trades` [공통]

행 수: 54 | 크기: 15 MB | 최신: 2026-01-29

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('real_trades_id_seq':: |
| 2 | `timestamp` | timestamp without time zone | N |  |  |
| 3 | `account_email` | character varying(255) | N |  |  |
| 4 | `strategy_id` | character varying(50) | N |  |  |
| 5 | `strategy_name` | character varying(255) | N |  |  |
| 6 | `ticker` | character varying(20) | N |  |  |
| 7 | `signal` | character varying(10) | N |  |  |
| 8 | `order_id` | character varying(100) | Y |  |  |
| 9 | `price` | real | N |  |  |
| 10 | `quantity` | integer | N |  |  |
| 11 | `position_size` | real | N |  |  |
| 12 | `filled_price` | real | Y |  |  |
| 13 | `filled_quantity` | integer | Y |  |  |
| 14 | `commission` | real | Y |  | 0.0 |
| 15 | `slippage` | real | Y |  | 0.0 |
| 16 | `status` | character varying(20) | N |  |  |
| 17 | `error_message` | text | Y |  |  |
| 18 | `entry_price` | real | Y |  |  |
| 19 | `exit_price` | real | Y |  |  |
| 20 | `realized_pnl` | real | Y |  | 0.0 |
| 21 | `created_at` | timestamp without time zone | Y |  | now() |
| 22 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_real_trades_account_email`
- `idx_real_trades_signal`
- `idx_real_trades_strategy`
- `real_trades_pkey`
- `idx_real_trades_composite`
- `idx_real_trades_date`
- `idx_real_trades_account`
- `idx_real_trades_created_at`
- `idx_real_trades_status`

---

#### `real_trades_archive` [공통]

행 수: 0 | 크기: 19 MB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('real_trades_id_seq':: |
| 2 | `timestamp` | timestamp without time zone | N |  |  |
| 3 | `account_email` | character varying(255) | N |  |  |
| 4 | `strategy_id` | character varying(50) | N |  |  |
| 5 | `strategy_name` | character varying(255) | N |  |  |
| 6 | `ticker` | character varying(20) | N |  |  |
| 7 | `signal` | character varying(10) | N |  |  |
| 8 | `order_id` | character varying(100) | Y |  |  |
| 9 | `price` | real | N |  |  |
| 10 | `quantity` | integer | N |  |  |
| 11 | `position_size` | real | N |  |  |
| 12 | `filled_price` | real | Y |  |  |
| 13 | `filled_quantity` | integer | Y |  |  |
| 14 | `commission` | real | Y |  | 0.0 |
| 15 | `slippage` | real | Y |  | 0.0 |
| 16 | `status` | character varying(20) | N |  |  |
| 17 | `error_message` | text | Y |  |  |
| 18 | `entry_price` | real | Y |  |  |
| 19 | `exit_price` | real | Y |  |  |
| 20 | `realized_pnl` | real | Y |  | 0.0 |
| 21 | `created_at` | timestamp without time zone | Y |  | now() |
| 22 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `real_trades_archive_account_email_idx`
- `real_trades_archive_account_email_idx1`
- `real_trades_archive_account_email_created_at_status_idx`
- `real_trades_archive_created_at_idx`
- `real_trades_archive_timestamp_idx`
- `real_trades_archive_signal_idx`
- `real_trades_archive_status_idx`
- `real_trades_archive_strategy_id_idx`
- `real_trades_archive_pkey`

---

#### `trade_comparisons` [공통]

행 수: 54 | 크기: 6864 kB | 최신: 2026-01-29

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('trade_comparisons_id_ |
| 2 | `timestamp` | timestamp without time zone | N |  |  |
| 3 | `strategy_id` | character varying(50) | N |  |  |
| 4 | `strategy_name` | character varying(255) | N |  |  |
| 5 | `real_trade_id` | integer | Y |  |  |
| 6 | `real_executed` | boolean | Y |  |  |
| 7 | `real_price` | real | Y |  |  |
| 8 | `real_quantity` | integer | Y |  |  |
| 9 | `real_commission` | real | Y |  |  |
| 10 | `real_slippage` | real | Y |  |  |
| 11 | `virtual_trade_id` | integer | Y |  |  |
| 12 | `virtual_executed` | boolean | Y |  |  |
| 13 | `virtual_price` | real | Y |  |  |
| 14 | `virtual_quantity` | integer | Y |  |  |
| 15 | `price_diff` | real | Y |  | 0.0 |
| 16 | `quantity_diff` | integer | Y |  | 0 |
| 17 | `cost_diff` | real | Y |  | 0.0 |
| 18 | `execution_time_diff` | real | Y |  | 0.0 |
| 19 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_comparisons_strategy`
- `trade_comparisons_pkey`
- `idx_comparisons_date`

---

#### `trade_verifications` [공통]

행 수: 0 | 크기: 104 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('trade_verifications_i |
| 2 | `real_trade_id` | integer | N |  |  |
| 3 | `order_id` | character varying(50) | Y |  |  |
| 4 | `verification_date` | timestamp without time zone | N |  | now() |
| 5 | `verification_status` | character varying(20) | N |  |  |
| 6 | `kis_verified` | boolean | Y |  | false |
| 7 | `kis_order_no` | character varying(50) | Y |  |  |
| 8 | `kis_filled_qty` | integer | Y |  |  |
| 9 | `kis_filled_price` | real | Y |  |  |
| 10 | `kis_filled_amount` | real | Y |  |  |
| 11 | `mismatch_reasons` | text | Y |  |  |
| 12 | `created_at` | timestamp without time zone | Y |  | now() |
| 13 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_verification_date`
- `idx_verification_order_id`
- `idx_verification_status`
- `idx_verification_trade_id`
- `trade_verifications_pkey`

---

#### `trades` [공통]

행 수: 1 | 크기: 96 kB | 최신: 2026-01-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('trades_id_seq'::regcl |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_id` | character varying(50) | Y |  |  |
| 4 | `symbol` | character varying(20) | N |  |  |
| 5 | `symbol_name` | character varying(100) | Y |  |  |
| 6 | `trade_type` | character varying(4) | N |  | 'UNKNOWN'::character varying |
| 7 | `quantity` | integer | N |  |  |
| 8 | `price` | real | N |  |  |
| 9 | `total_amount` | real | N |  |  |
| 10 | `profit_loss` | real | Y |  |  |
| 11 | `profit_loss_rate` | real | Y |  |  |
| 12 | `status` | character varying(9) | Y |  |  |
| 13 | `order_number` | character varying(50) | Y |  |  |
| 14 | `kis_response` | character varying(500) | Y |  |  |
| 15 | `executed_at` | timestamp without time zone | Y |  |  |
| 16 | `created_at` | timestamp without time zone | Y |  | now() |
| 17 | `side` | character varying(10) | Y |  |  |
| 18 | `order_id` | character varying(100) | Y |  |  |
| 19 | `order_type` | character varying(20) | Y |  |  |
| 20 | `realized_pnl` | real | Y |  | 0.0 |
| 21 | `commission` | real | Y |  | 0.0 |
| 22 | `tax` | real | Y |  | 0.0 |
| 23 | `net_pnl` | real | Y |  | 0.0 |
| 24 | `signal_confidence` | real | Y |  |  |
| 25 | `signal_reason` | text | Y |  |  |
| 26 | `ticker` | character varying(20) | Y |  |  |

**인덱스:**

- `idx_trades_created_at`
- `idx_trades_user_id`
- `trades_pkey`

---

#### `virtual_trades` [공통]

행 수: 132,506 | 크기: 26 MB | 최신: 2026-02-01

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('virtual_trades_id_seq |
| 2 | `timestamp` | timestamp without time zone | N |  |  |
| 3 | `account_email` | character varying(255) | N |  |  |
| 4 | `strategy_id` | character varying(50) | N |  |  |
| 5 | `strategy_name` | character varying(255) | N |  |  |
| 6 | `ticker` | character varying(20) | N |  |  |
| 7 | `signal` | character varying(10) | N |  |  |
| 8 | `price` | real | N |  |  |
| 9 | `quantity` | integer | N |  |  |
| 10 | `position_size` | real | N |  |  |
| 11 | `filled_price` | real | N |  |  |
| 12 | `filled_quantity` | integer | N |  |  |
| 13 | `entry_price` | real | Y |  |  |
| 14 | `exit_price` | real | Y |  |  |
| 15 | `realized_pnl` | real | Y |  | 0.0 |
| 16 | `created_at` | timestamp without time zone | Y |  | now() |
| 17 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_virtual_trades_date`
- `idx_virtual_trades_strategy`
- `idx_virtual_trades_account`
- `virtual_trades_pkey`

---

#### `waverider_positions` [공통]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('waverider_positions_i |
| 2 | `user_id` | integer | N |  |  |
| 3 | `signal_id` | integer | Y |  |  |
| 4 | `ticker` | character varying(20) | N |  |  |
| 5 | `ticker_name` | character varying(100) | Y |  |  |
| 6 | `entry_phase` | USER-DEFINED | N |  |  |
| 7 | `entry_price` | double precision | N |  |  |
| 8 | `entry_quantity` | integer | N |  |  |
| 9 | `entry_amount` | double precision | N |  |  |
| 10 | `entry_date` | timestamp without time zone | N |  |  |
| 11 | `exit_phase` | USER-DEFINED | Y |  |  |
| 12 | `exit_price` | double precision | Y |  |  |
| 13 | `exit_quantity` | integer | Y |  |  |
| 14 | `exit_amount` | double precision | Y |  |  |
| 15 | `exit_date` | timestamp without time zone | Y |  |  |
| 16 | `realized_pnl` | double precision | Y |  |  |
| 17 | `realized_pnl_pct` | double precision | Y |  |  |
| 18 | `unrealized_pnl` | double precision | Y |  |  |
| 19 | `unrealized_pnl_pct` | double precision | Y |  |  |
| 20 | `is_open` | boolean | Y |  |  |
| 21 | `is_profitable` | boolean | Y |  |  |
| 22 | `created_at` | timestamp without time zone | Y |  |  |
| 23 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `waverider_positions_pkey`
- `ix_waverider_positions_id`
- `ix_waverider_positions_ticker`

---


### [RISK]

#### `go100_risk_disclaimers` [GO100]

행 수: 0 | 크기: 72 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_risk_disclaimer |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_card_id` | bigint | Y |  |  |
| 4 | `disclaimer_type` | character varying(50) | N |  |  |
| 5 | `exceeded_field` | character varying(50) | N |  |  |
| 6 | `default_value` | numeric | N |  |  |
| 7 | `user_value` | numeric | N |  |  |
| 8 | `agreed_at` | timestamp with time zone | N |  | now() |
| 9 | `ip_address` | character varying(45) | Y |  |  |
| 10 | `user_agent` | text | Y |  |  |

**인덱스:**

- `go100_risk_disclaimers_pkey`
- `idx_go100_disclaimers_user`
- `idx_go100_disclaimers_card`

---

#### `go100_risk_events` [GO100]

행 수: 180 | 크기: 96 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `event_id` | integer | N | PK | nextval('go100_risk_events_eve |
| 2 | `user_id` | integer | N |  |  |
| 3 | `rule_id` | integer | Y |  |  |
| 4 | `event_type` | character varying(30) | Y |  |  |
| 5 | `details` | jsonb | Y |  |  |
| 6 | `action_taken` | character varying(50) | Y |  |  |
| 7 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_risk_events_pkey`
- `idx_risk_events_user`

---

#### `go100_risk_rules` [GO100]

행 수: 3 | 크기: 88 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `rule_id` | integer | N | PK | nextval('go100_risk_rules_rule |
| 2 | `user_id` | integer | N |  |  |
| 3 | `rule_type` | character varying(30) | N |  |  |
| 4 | `threshold` | jsonb | N |  |  |
| 5 | `is_active` | boolean | Y |  | true |
| 6 | `triggered_count` | integer | Y |  | 0 |
| 7 | `last_triggered_at` | timestamp with time zone | Y |  |  |
| 8 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_risk_rules_pkey`
- `idx_risk_rules_user`

---

#### `v4_backtest_regime_analysis` [V4.1]

행 수: 230 | 크기: 480 kB | 최신: 2025-01-01

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_backtest_regime_an |
| 2 | `session_id` | bigint | N |  |  |
| 3 | `card_id` | integer | N |  |  |
| 4 | `strategy_name` | character varying(100) | Y |  |  |
| 5 | `desk_id` | character varying(10) | Y |  |  |
| 6 | `market_type` | character varying(10) | N |  | 'KOSPI'::character varying |
| 7 | `regime` | character varying(30) | N |  |  |
| 8 | `total_trades` | integer | Y |  |  |
| 9 | `win_count` | integer | Y |  |  |
| 10 | `loss_count` | integer | Y |  |  |
| 11 | `win_rate` | numeric | Y |  |  |
| 12 | `profit_factor` | numeric | Y |  |  |
| 13 | `total_pnl` | numeric | Y |  |  |
| 14 | `avg_pnl` | numeric | Y |  |  |
| 15 | `max_pnl` | numeric | Y |  |  |
| 16 | `min_pnl` | numeric | Y |  |  |
| 17 | `avg_hold_days` | numeric | Y |  |  |
| 18 | `avg_mfe_pct` | numeric | Y |  |  |
| 19 | `avg_mae_pct` | numeric | Y |  |  |
| 20 | `max_drawdown_pct` | numeric | Y |  |  |
| 21 | `sharpe_ratio` | numeric | Y |  |  |
| 22 | `benchmark_return_pct` | numeric | Y |  |  |
| 23 | `strategy_return_pct` | numeric | Y |  |  |
| 24 | `alpha_pct` | numeric | Y |  |  |
| 25 | `pass_win_rate` | boolean | Y |  |  |
| 26 | `pass_pf` | boolean | Y |  |  |
| 27 | `pass_alpha` | boolean | Y |  |  |
| 28 | `pass_mdd` | boolean | Y |  |  |
| 29 | `pass_sharpe` | boolean | Y |  |  |
| 30 | `overall_pass` | boolean | Y |  |  |
| 31 | `backtest_period_start` | date | Y |  |  |
| 32 | `backtest_period_end` | date | Y |  |  |
| 33 | `created_at` | timestamp without time zone | Y |  | now() |
| 34 | `regime_mapped` | character varying(10) | Y |  |  |

**인덱스:**

- `v4_backtest_regime_analysis_pkey`
- `idx_bt_regime_analysis_card`
- `idx_bt_regime_analysis_desk`
- `idx_bt_regime_analysis_session`
- `idx_regime_analysis_card`
- `idx_regime_analysis_desk`

---

#### `v4_bt_daily_risk_log` [V4.1]

행 수: 32 | 크기: 96 kB | 최신: 2026-02-20

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_bt_daily_risk_log_ |
| 2 | `bt_session_id` | integer | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `regime` | character varying(30) | Y |  |  |
| 5 | `daily_pnl_pct` | numeric | Y |  |  |
| 6 | `weekly_pnl_pct` | numeric | Y |  |  |
| 7 | `daily_trade_count` | integer | Y |  |  |
| 8 | `daily_halted` | boolean | Y |  | false |
| 9 | `halted_reason` | character varying(100) | Y |  |  |
| 10 | `open_positions_count` | integer | Y |  |  |
| 11 | `fund_available` | numeric | Y |  |  |
| 12 | `fund_total` | numeric | Y |  |  |
| 13 | `slot_pnl` | jsonb | Y |  |  |
| 14 | `slot_halted` | jsonb | Y |  |  |
| 15 | `adaptive_adjustment` | jsonb | Y |  |  |
| 16 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_bt_daily_risk_log_pkey`
- `idx_bt_daily_risk_session`
- `idx_bt_daily_risk_date`

---

#### `v4_market_regime_daily` [V4.1]

행 수: 1,135 | 크기: 560 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_market_regime_dail |
| 2 | `date` | date | N |  |  |
| 3 | `regime` | character varying(30) | Y |  |  |
| 4 | `regime_score` | numeric | Y |  |  |
| 5 | `kospi_ret_20d` | numeric | Y |  |  |
| 6 | `ma5` | numeric | Y |  |  |
| 7 | `ma20` | numeric | Y |  |  |
| 8 | `ma60` | numeric | Y |  |  |
| 9 | `ma_alignment` | character varying(20) | Y |  |  |
| 10 | `bull_ratio_20d` | numeric | Y |  |  |
| 11 | `vkospi` | numeric | Y |  |  |
| 12 | `foreign_flow_20d` | bigint | Y |  |  |
| 13 | `previous_regime` | character varying(30) | Y |  |  |
| 14 | `transition_note` | text | Y |  |  |
| 15 | `created_at` | timestamp with time zone | N |  | now() |
| 16 | `updated_at` | timestamp with time zone | Y |  |  |
| 17 | `hysteresis_up_count` | integer | Y |  | 0 |
| 18 | `hysteresis_down_count` | integer | Y |  | 0 |
| 19 | `pending_regime` | character varying(30) | Y |  | NULL::character varying |
| 20 | `market_type` | character varying(10) | N |  | 'KOSPI'::character varying |

**인덱스:**

- `v4_market_regime_daily_pkey`
- `v4_market_regime_daily_date_market_key`

---


### [STRATEGY]

#### `go100_cross_market_signals` [GO100]

행 수: 27 | 크기: 64 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_cross_market_si |
| 2 | `signal_date` | date | N |  |  |
| 3 | `signal_type` | character varying(50) | N |  |  |
| 4 | `source_market` | character varying(50) | N |  |  |
| 5 | `target_market` | character varying(50) | Y |  |  |
| 6 | `direction` | character varying(10) | Y |  |  |
| 7 | `strength` | numeric | Y |  |  |
| 8 | `description` | text | Y |  |  |
| 9 | `raw_data` | jsonb | Y |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_cross_market_signals_pkey`
- `go100_cross_market_signals_signal_date_signal_type_source_m_key`
- `idx_cross_signal_date`

---

#### `go100_signal_performance` [GO100]

행 수: 0 | 크기: 8192 bytes

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_signal_performa |
| 2 | `signal_id` | integer | Y |  |  |
| 3 | `signal_type` | character varying(50) | Y |  |  |
| 4 | `predicted_direction` | character varying(10) | Y |  |  |
| 5 | `actual_direction` | character varying(10) | Y |  |  |
| 6 | `predicted_magnitude` | numeric | Y |  |  |
| 7 | `actual_magnitude` | numeric | Y |  |  |
| 8 | `is_correct` | boolean | Y |  |  |
| 9 | `evaluated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_signal_performance_pkey`

---

#### `go100_strategy_cards` [GO100]

행 수: 71 | 크기: 408 kB | 최신: 2026-03-09

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `go100_card_id` | bigint | N | PK | nextval('go100_strategy_cards_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `account_id` | integer | Y |  |  |
| 4 | `strategy_name` | character varying(200) | N |  |  |
| 5 | `strategy_type` | character varying(20) | N |  | 'CUSTOM'::character varying |
| 6 | `universe_filter` | jsonb | Y |  | '{}'::jsonb |
| 7 | `entry_rules` | jsonb | Y |  | '[]'::jsonb |
| 8 | `exit_rules` | jsonb | Y |  | '[]'::jsonb |
| 9 | `risk_params` | jsonb | Y |  | '{}'::jsonb |
| 10 | `strategy_params` | jsonb | Y |  | '{}'::jsonb |
| 11 | `allocated_amount` | numeric | Y |  | 0 |
| 12 | `max_stocks` | integer | Y |  | 5 |
| 13 | `card_status` | character varying(20) | N |  | 'IDEA'::character varying |
| 14 | `is_active` | boolean | Y |  | true |
| 15 | `is_live` | boolean | Y |  | false |
| 16 | `source_type` | character varying(20) | Y |  | 'CUSTOM'::character varying |
| 17 | `source_store_card_id` | bigint | Y |  |  |
| 18 | `source_user_id` | integer | Y |  |  |
| 19 | `llm_session_id` | character varying(100) | Y |  |  |
| 20 | `last_backtest_id` | bigint | Y |  |  |
| 21 | `last_backtest_return` | numeric | Y |  |  |
| 22 | `last_backtest_mdd` | numeric | Y |  |  |
| 23 | `last_backtest_sharpe` | numeric | Y |  |  |
| 24 | `last_backtest_at` | timestamp with time zone | Y |  |  |
| 25 | `paper_total_return` | numeric | Y |  |  |
| 26 | `paper_start_date` | date | Y |  |  |
| 27 | `paper_days` | integer | Y |  | 0 |
| 28 | `disclaimer_agreed` | boolean | Y |  | false |
| 29 | `disclaimer_agreed_at` | timestamp with time zone | Y |  |  |
| 30 | `dedicated_account` | boolean | Y |  | false |
| 31 | `created_at` | timestamp with time zone | Y |  | now() |
| 32 | `updated_at` | timestamp with time zone | Y |  | now() |
| 33 | `is_featured` | boolean | N |  | false |
| 34 | `is_public` | boolean | N |  | false |
| 35 | `featured_order` | integer | N |  | 0 |
| 36 | `version` | integer | Y |  | 1 |
| 37 | `parent_card_id` | bigint | Y |  |  |
| 38 | `optimization_source` | character varying(20) | Y |  | 'MANUAL'::character varying |
| 39 | `description` | text | Y |  |  |
| 40 | `card_code` | character varying(20) | Y |  |  |
| 41 | `card_name` | character varying(50) | Y |  |  |
| 42 | `desk_id` | smallint | Y |  |  |
| 43 | `situation_code` | character varying(3) | Y |  |  |
| 44 | `condition_code` | character varying(3) | Y |  |  |
| 45 | `card_version` | smallint | Y |  | 1 |
| 46 | `parent_card_code` | character varying(20) | Y |  |  |
| 47 | `relay_order` | smallint | Y |  |  |
| 48 | `bar_timeframe` | character varying(10) | Y |  |  |
| 49 | `deactivated_at` | timestamp without time zone | Y |  |  |
| 50 | `deactivation_reason` | text | Y |  |  |
| 51 | `legacy_strategy_id` | character varying(10) | Y |  |  |
| 52 | `hypothesis_id` | character varying(30) | Y |  |  |
| 53 | `paper_session_id` | integer | Y |  |  |
| 54 | `stage` | integer | Y |  | 0 |
| 55 | `backtest_result` | jsonb | Y |  | '{}'::jsonb |
| 56 | `paper_result` | jsonb | Y |  | '{}'::jsonb |
| 57 | `why_json` | jsonb | Y |  | '{}'::jsonb |
| 58 | `card_type` | character varying(20) | Y |  | 'MANUAL'::character varying |
| 59 | `stage_id` | integer | Y |  | 1 |
| 60 | `bounce_conditions` | jsonb | Y |  | '{}'::jsonb |
| 61 | `trigger_tactic` | jsonb | Y |  | '[]'::jsonb |
| 62 | `broker_config` | jsonb | Y |  | '{}'::jsonb |
| 63 | `data_requirements` | jsonb | Y |  | '[]'::jsonb |
| 64 | `metadata` | jsonb | Y |  | '{}'::jsonb |

**인덱스:**

- `idx_go100_cards_featured`
- `idx_go100_cards_public`
- `go100_strategy_cards_pkey`
- `idx_go100_cards_user`
- `idx_go100_cards_account`
- `idx_go100_cards_status`
- `idx_go100_cards_live`
- `idx_go100_cards_source`
- `idx_strategy_cards_hypothesis_id`
- `idx_go100_cards_engine_active`
- `idx_go100_cards_type`

---

#### `go100_strategy_edit_history` [GO100]

행 수: 0 | 크기: 40 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `edit_id` | integer | N | PK | nextval('go100_strategy_edit_h |
| 2 | `strategy_card_id` | bigint | N |  |  |
| 3 | `user_id` | integer | N |  |  |
| 4 | `edit_instruction` | text | N |  |  |
| 5 | `before_rules` | jsonb | N |  |  |
| 6 | `after_rules` | jsonb | N |  |  |
| 7 | `field_changed` | character varying(50) | N |  |  |
| 8 | `approved` | boolean | Y |  | false |
| 9 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_strategy_edit_history_pkey`
- `idx_edit_history_card`
- `idx_edit_history_user`
- `idx_edit_history_approved`

---

#### `go100_strategy_hypotheses` [GO100]

행 수: 1,385 | 크기: 4624 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `hypothesis_id` | integer | N | PK | nextval('go100_strategy_hypoth |
| 2 | `source_type` | character varying(50) | N |  |  |
| 3 | `hypothesis_text` | text | N |  |  |
| 4 | `filters` | jsonb | N |  | '{}'::jsonb |
| 5 | `target_return` | numeric | Y |  |  |
| 6 | `target_days` | integer | Y |  |  |
| 7 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 8 | `validation_result` | jsonb | Y |  |  |
| 9 | `created_card_id` | bigint | Y |  |  |
| 10 | `created_at` | timestamp with time zone | Y |  | now() |
| 11 | `updated_at` | timestamp with time zone | Y |  | now() |
| 12 | `score_axis_a` | smallint | Y |  |  |
| 13 | `score_axis_b` | smallint | Y |  |  |
| 14 | `score_axis_c` | smallint | Y |  |  |
| 15 | `score_axis_d` | smallint | Y |  |  |
| 16 | `score_axis_e` | smallint | Y |  |  |
| 17 | `score_total` | smallint | Y |  |  |
| 18 | `score_grade` | character varying(2) | Y |  | NULL::character varying |
| 19 | `score_detail` | jsonb | Y |  | '{}'::jsonb |
| 20 | `ceo_override_reason` | text | Y |  |  |
| 21 | `iteration_count` | integer | Y |  | 0 |
| 22 | `best_pf` | numeric | Y |  |  |
| 23 | `converge_status` | character varying(20) | Y |  | 'IMPROVING'::character varying |
| 24 | `why_json` | jsonb | Y |  | '{}'::jsonb |
| 25 | `stock_universe` | jsonb | Y |  | '{}'::jsonb |
| 26 | `entry_signal` | jsonb | Y |  | '{}'::jsonb |
| 27 | `exit_signal` | jsonb | Y |  | '{}'::jsonb |
| 28 | `user_id` | bigint | Y |  |  |
| 29 | `parent_hypothesis_id` | integer | Y |  |  |
| 30 | `generation` | integer | Y |  | 0 |
| 31 | `feedback_status` | character varying(20) | Y |  | NULL::character varying |
| 32 | `feedback_json` | jsonb | Y |  |  |
| 33 | `desk_id` | integer | Y |  |  |

**인덱스:**

- `go100_strategy_hypotheses_pkey`
- `idx_hypothesis_status`
- `idx_hypothesis_created_at`
- `idx_hypotheses_why_json`
- `idx_go100_strategy_hypotheses_user_id`
- `idx_hypotheses_parent_id`
- `idx_hypotheses_feedback_status`
- `idx_hypotheses_desk_id`

---

#### `go100_strategy_knowledge` [GO100]

행 수: 17 | 크기: 176 kB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_strategy_knowle |
| 2 | `source_type` | character varying(20) | N |  |  |
| 3 | `source_name` | character varying(500) | N |  |  |
| 4 | `source_url` | text | Y |  |  |
| 5 | `strategy_name` | character varying(200) | N |  |  |
| 6 | `category` | character varying(50) | Y |  |  |
| 7 | `description` | text | Y |  |  |
| 8 | `conditions` | jsonb | Y |  | '[]'::jsonb |
| 9 | `applicable_desk` | character varying(10) | Y |  |  |
| 10 | `applicable_signals` | ARRAY | Y |  | '{}'::text[] |
| 11 | `hypothesis` | text | Y |  |  |
| 12 | `parameter_changes` | jsonb | Y |  | '[]'::jsonb |
| 13 | `backtest_result` | jsonb | Y |  |  |
| 14 | `status` | character varying(20) | Y |  | 'hypothesis'::character varyin |
| 15 | `confidence` | integer | Y |  | 50 |
| 16 | `validation_count` | integer | Y |  | 0 |
| 17 | `rejection_count` | integer | Y |  | 0 |
| 18 | `added_date` | timestamp without time zone | Y |  | now() |
| 19 | `updated_date` | timestamp without time zone | Y |  | now() |
| 20 | `added_by` | character varying(20) | Y |  | 'agent'::character varying |
| 21 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_strategy_knowledge_pkey`
- `idx_sk_source_strategy`
- `idx_sk_status`
- `idx_sk_desk`
- `idx_sk_category`
- `idx_sk_source_type`
- `idx_go100_strategy_knowledge_user_id`

---

#### `go100_strategy_portfolio_snapshots` [GO100]

행 수: 0 | 크기: 40 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `snapshot_id` | integer | N | PK | nextval('go100_strategy_portfo |
| 2 | `portfolio_id` | integer | N |  |  |
| 3 | `snapshot_date` | date | N |  |  |
| 4 | `total_value` | bigint | Y |  |  |
| 5 | `total_pnl` | bigint | Y |  |  |
| 6 | `total_pnl_pct` | real | Y |  |  |
| 7 | `drawdown_pct` | real | Y |  |  |
| 8 | `peak_value` | bigint | Y |  |  |
| 9 | `allocation_detail` | jsonb | Y |  |  |
| 10 | `created_at` | timestamp without time zone | Y |  | now() |
| 11 | `user_id` | bigint | Y |  |  |

**인덱스:**

- `go100_strategy_portfolio_snapshots_pkey`
- `go100_strategy_portfolio_snapsho_portfolio_id_snapshot_date_key`
- `idx_go100_strategy_portfolio_snapshots_port_date`
- `idx_go100_strategy_portfolio_snapshots_user_id`

---

#### `go100_strategy_portfolios` [GO100]

행 수: 23 | 크기: 56 kB | 최신: 2026-03-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `portfolio_id` | integer | N | PK | nextval('go100_strategy_portfo |
| 2 | `user_id` | integer | N |  |  |
| 3 | `goal_id` | bigint | Y |  |  |
| 4 | `portfolio_name` | character varying(100) | N |  | '기본 포트폴리오'::character varying |
| 5 | `total_capital` | bigint | N |  |  |
| 6 | `status` | character varying(20) | N |  | 'ACTIVE'::character varying |
| 7 | `created_at` | timestamp without time zone | Y |  | now() |
| 8 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_strategy_portfolios_pkey`
- `idx_go100_strategy_portfolios_user`
- `idx_go100_strategy_portfolios_status`

---

#### `v4_condition_search` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_condition_search_i |
| 2 | `condition_name` | character varying(100) | N |  |  |
| 3 | `condition_id` | integer | Y |  |  |
| 4 | `stock_code` | character varying(10) | N |  |  |
| 5 | `stock_name` | character varying(50) | Y |  |  |
| 6 | `signal_type` | character varying(10) | Y |  |  |
| 7 | `signal_time` | timestamp with time zone | N |  |  |
| 8 | `current_price` | integer | Y |  |  |
| 9 | `volume` | bigint | Y |  |  |
| 10 | `change_rate` | numeric | Y |  |  |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_condition_search_pkey`
- `idx_condition_search_name_time`
- `idx_condition_search_code`

---

#### `v4_desk1_signals` [V4.1]

행 수: 7 | 크기: 40 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk1_signals_id_s |
| 2 | `signal_date` | date | N |  | CURRENT_DATE |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `signal_type` | character varying(30) | N |  |  |
| 5 | `confidence` | integer | Y |  | 0 |
| 6 | `entry_price` | numeric | Y |  |  |
| 7 | `stop_loss` | numeric | Y |  |  |
| 8 | `target_price` | numeric | Y |  |  |
| 9 | `max_hold_minutes` | integer | Y |  | 30 |
| 10 | `status` | character varying(20) | Y |  | 'DETECTED'::character varying |
| 11 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk1_signals_pkey`
- `idx_desk1_sig_date`

---

#### `v4_desk2_signals` [V4.1]

행 수: 801 | 크기: 168 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk2_signals_id_s |
| 2 | `signal_date` | date | N |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `stock_type` | character varying(10) | N |  |  |
| 5 | `signal_name` | character varying(20) | N |  |  |
| 6 | `signal_time` | timestamp without time zone | N |  |  |
| 7 | `signal_price` | numeric | N |  |  |
| 8 | `dip_pct` | numeric | Y |  |  |
| 9 | `entry_price` | numeric | Y |  |  |
| 10 | `status` | character varying(10) | Y |  | 'NEW'::character varying |
| 11 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk2_signals_pkey`
- `idx_desk2_sig_date`

---

#### `v4_desk_signal_history` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_desk_signal_histor |
| 2 | `desk_id` | character varying(10) | Y |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `signal_type` | character varying(50) | Y |  |  |
| 5 | `direction` | character varying(10) | Y |  |  |
| 6 | `strength` | numeric | Y |  |  |
| 7 | `price_at_signal` | numeric | Y |  |  |
| 8 | `metadata` | jsonb | Y |  |  |
| 9 | `generated_at` | timestamp without time zone | Y |  | now() |
| 10 | `acted_on` | boolean | Y |  | false |
| 11 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_desk_signal_history_pkey`
- `idx_signal_hist_stock`

---

#### `v4_desk_strategy_mapping` [V4.1]

행 수: 56 | 크기: 112 kB | 최신: 2026-03-20

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `mapping_id` | integer | N | PK | nextval('v4_desk_strategy_mapp |
| 2 | `desk_id` | integer | N |  |  |
| 3 | `card_id` | integer | N |  |  |
| 4 | `stage_id` | integer | N |  | 1 |
| 5 | `allocation_pct` | numeric | N |  | 0 |
| 6 | `priority` | integer | N |  | 0 |
| 7 | `is_active` | boolean | N |  | true |
| 8 | `valid_from` | timestamp without time zone | N |  | now() |
| 9 | `valid_until` | timestamp without time zone | Y |  |  |
| 10 | `created_at` | timestamp without time zone | N |  | now() |
| 11 | `updated_at` | timestamp without time zone | N |  | now() |

**인덱스:**

- `v4_desk_strategy_mapping_pkey`
- `v4_desk_strategy_mapping_desk_id_card_id_stage_id_key`
- `idx_dsm_desk_active`
- `idx_dsm_stage`

---

#### `v4_explosion_signals` [V4.1]

행 수: 38 | 크기: 56 kB | 최신: 2026-03-19

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_explosion_signals_ |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `detected_at` | timestamp without time zone | N |  | now() |
| 4 | `signal_type` | character varying(20) | N |  |  |
| 5 | `explosion_score` | numeric | N |  | 0 |
| 6 | `current_price` | numeric | Y |  |  |
| 7 | `vol_ratio_5m` | numeric | Y |  |  |
| 8 | `vol_ratio_1m` | numeric | Y |  |  |
| 9 | `price_change_5m` | numeric | Y |  |  |
| 10 | `price_change_1m` | numeric | Y |  |  |
| 11 | `consecutive_up` | integer | Y |  | 0 |
| 12 | `support_distance` | numeric | Y |  |  |
| 13 | `retention_at_price` | numeric | Y |  |  |
| 14 | `status` | character varying(20) | Y |  | 'DETECTED'::character varying |
| 15 | `confirmed_at` | timestamp without time zone | Y |  |  |
| 16 | `expired_at` | timestamp without time zone | Y |  |  |
| 17 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_explosion_signals_pkey`
- `idx_explosion_signals_code_date`
- `idx_explosion_signals_status`

---

#### `v4_scalping_signals` [V4.1]

행 수: 0 | 크기: 40 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_scalping_signals_i |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `signal_time` | timestamp without time zone | N |  |  |
| 4 | `signal_type` | character varying(30) | N |  |  |
| 5 | `direction` | character varying(4) | N |  |  |
| 6 | `current_price` | integer | Y |  |  |
| 7 | `vwap_price` | numeric | Y |  |  |
| 8 | `open_price` | integer | Y |  |  |
| 9 | `prev_close` | integer | Y |  |  |
| 10 | `gap_pct` | numeric | Y |  |  |
| 11 | `atr_breakout_pct` | numeric | Y |  |  |
| 12 | `volume_ratio` | numeric | Y |  |  |
| 13 | `volume_5min` | bigint | Y |  |  |
| 14 | `bid_ask_ratio` | numeric | Y |  |  |
| 15 | `spread_pct` | numeric | Y |  |  |
| 16 | `signal_strength` | numeric | Y |  |  |
| 17 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 18 | `executed_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `v4_scalping_signals_pkey`
- `v4_scalping_signals_stock_code_signal_time_signal_type_key`
- `idx_scalp_sig_time`
- `idx_scalp_sig_stock`
- `idx_scalp_sig_status`

---

#### `v4_scoring_weights` [V4.1]

행 수: 1 | 크기: 64 kB | 최신: 2026-02-12

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_scoring_weights_id |
| 2 | `effective_from` | date | N |  |  |
| 3 | `supply_demand_w` | numeric | Y |  |  |
| 4 | `sector_momentum_w` | numeric | Y |  |  |
| 5 | `theme_w` | numeric | Y |  |  |
| 6 | `volume_w` | numeric | Y |  |  |
| 7 | `technical_w` | numeric | Y |  |  |
| 8 | `source` | character varying(20) | Y |  |  |
| 9 | `validation_score` | numeric | Y |  |  |
| 10 | `note` | text | Y |  |  |
| 11 | `created_at` | timestamp with time zone | N |  | now() |
| 12 | `updated_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_scoring_weights_pkey`

---

#### `v4_signals` [V4.1]

행 수: 127,362 | 크기: 42 MB | 최신: 2026-03-13

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `signal_id` | bigint | N | PK | nextval('v4_signals_signal_id_ |
| 2 | `desk_id` | integer | N |  |  |
| 3 | `stock_code` | character varying(10) | N |  |  |
| 4 | `stock_name` | character varying(50) | Y |  |  |
| 5 | `signal_date` | date | N |  |  |
| 6 | `signal_type` | character varying(10) | N |  |  |
| 7 | `signal_strength` | integer | Y |  |  |
| 8 | `expected_return` | numeric | Y |  |  |
| 9 | `expected_risk` | numeric | Y |  |  |
| 10 | `risk_reward` | numeric | Y |  |  |
| 11 | `entry_price` | numeric | Y |  |  |
| 12 | `target_price` | numeric | Y |  |  |
| 13 | `stop_loss_price` | numeric | Y |  |  |
| 14 | `holding_days` | character varying(20) | Y |  |  |
| 15 | `conditions_met` | jsonb | Y |  |  |
| 16 | `explanation` | text | Y |  |  |
| 17 | `indicator_data` | jsonb | Y |  |  |
| 18 | `risk_factors` | jsonb | Y |  |  |
| 19 | `status` | character varying(20) | Y |  | 'ACTIVE'::character varying |
| 20 | `created_at` | timestamp with time zone | Y |  | now() |
| 21 | `result_position_id` | integer | Y |  |  |
| 22 | `result_status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 23 | `source` | character varying(20) | Y |  |  |
| 24 | `strategy_card_id` | integer | Y |  |  |
| 25 | `strategy_version` | integer | Y |  | 1 |

**인덱스:**

- `v4_signals_pkey`
- `v4_signals_desk_id_stock_code_signal_date_key`
- `idx_v4_signals_date`
- `idx_v4_signals_desk_date`
- `idx_signals_card`

---

#### `v4_strategy_performance` [V4.1]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `perf_id` | integer | N | PK | nextval('v4_strategy_performan |
| 2 | `card_id` | integer | N |  |  |
| 3 | `desk_id` | integer | N |  |  |
| 4 | `calc_date` | date | N |  |  |
| 5 | `period_type` | character varying(10) | N |  | 'daily'::character varying |
| 6 | `total_trades` | integer | Y |  | 0 |
| 7 | `win_trades` | integer | Y |  | 0 |
| 8 | `loss_trades` | integer | Y |  | 0 |
| 9 | `total_pnl` | numeric | Y |  | 0 |
| 10 | `total_pnl_pct` | numeric | Y |  | 0 |
| 11 | `max_drawdown` | numeric | Y |  | 0 |
| 12 | `sharpe_ratio` | numeric | Y |  | 0 |
| 13 | `profit_factor` | numeric | Y |  | 0 |
| 14 | `avg_hold_days` | numeric | Y |  | 0 |
| 15 | `created_at` | timestamp without time zone | N |  | now() |

**인덱스:**

- `v4_strategy_performance_pkey`
- `v4_strategy_performance_card_id_desk_id_calc_date_period_ty_key`
- `idx_sp_card_date`
- `idx_sp_desk_date`

---

#### `v4_strategy_registry` [V4.1]

행 수: 77 | 크기: 120 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_strategy_registry_ |
| 2 | `strategy_code` | character varying(50) | N |  |  |
| 3 | `name` | character varying(100) | N |  |  |
| 4 | `category` | character varying(30) | N |  |  |
| 5 | `source_strategy_id` | integer | Y |  |  |
| 6 | `parameters` | jsonb | Y |  | '{}'::jsonb |
| 7 | `entry_logic` | text | Y |  |  |
| 8 | `exit_logic` | text | Y |  |  |
| 9 | `is_active` | boolean | Y |  | false |
| 10 | `performance_score` | numeric | Y |  | 0 |
| 11 | `total_return_pct` | numeric | Y |  | 0 |
| 12 | `win_rate` | numeric | Y |  | 0 |
| 13 | `max_drawdown_pct` | numeric | Y |  | 0 |
| 14 | `trade_count` | integer | Y |  | 0 |
| 15 | `last_backtest_at` | timestamp with time zone | Y |  |  |
| 16 | `created_at` | timestamp with time zone | Y |  | now() |
| 17 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_strategy_registry_pkey`
- `v4_strategy_registry_strategy_code_key`
- `idx_strategy_registry_active`
- `idx_strategy_registry_performance`

---

#### `v4_strategy_stage_log` [V4.1]

행 수: 13 | 크기: 32 kB | 최신: 2026-03-20

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_strategy_stage_log |
| 2 | `card_id` | integer | N |  |  |
| 3 | `desk_id` | integer | Y |  |  |
| 4 | `from_stage` | integer | Y |  |  |
| 5 | `to_stage` | integer | Y |  |  |
| 6 | `reason` | text | Y |  |  |
| 7 | `metrics` | jsonb | Y |  |  |
| 8 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_strategy_stage_log_pkey`

---

#### `strategy_allocations` [공통]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('strategy_allocations_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `strategy_id` | character varying(50) | N |  |  |
| 4 | `allocated_capital` | real | N |  |  |
| 5 | `capital_pct` | real | N |  |  |
| 6 | `position_size` | real | N |  |  |
| 7 | `position_size_pct` | real | N |  |  |
| 8 | `stop_loss_pct` | real | N |  |  |
| 9 | `take_profit_pct` | real | N |  |  |
| 10 | `max_daily_trades` | integer | N |  |  |
| 11 | `max_position_count` | integer | N |  |  |
| 12 | `priority` | integer | N |  |  |
| 13 | `risk_level` | text | N |  |  |
| 14 | `is_active` | boolean | Y |  | true |
| 15 | `created_at` | timestamp without time zone | Y |  | now() |
| 16 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `strategy_allocations_pkey`
- `strategy_allocations_user_id_strategy_id_key`

---

#### `strategy_cards` [공통]

행 수: 60 | 크기: 312 kB | 최신: 2026-02-22

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `card_id` | bigint | N | PK | nextval('strategy_cards_card_i |
| 2 | `user_id` | bigint | N |  |  |
| 3 | `account_id` | bigint | N |  |  |
| 4 | `strategy_name` | character varying(100) | N |  |  |
| 5 | `strategy_type` | character varying(30) | N |  | 'CUSTOM'::character varying |
| 6 | `strategy_params` | jsonb | N |  | '{}'::jsonb |
| 7 | `allocated_amount` | numeric | N |  | 0 |
| 8 | `max_stocks` | integer | N |  | 5 |
| 9 | `is_live` | boolean | N |  | false |
| 10 | `is_active` | boolean | N |  | true |
| 11 | `desk_id` | character varying(10) | Y |  |  |
| 12 | `created_at` | timestamp with time zone | N |  | now() |
| 13 | `updated_at` | timestamp with time zone | N |  | now() |
| 14 | `entry_rules` | jsonb | Y |  | '{}'::jsonb |
| 15 | `exit_rules` | jsonb | Y |  | '{}'::jsonb |
| 16 | `risk_params` | jsonb | Y |  | '{}'::jsonb |
| 17 | `buy_phases` | jsonb | Y |  | '[]'::jsonb |
| 18 | `sell_phases` | jsonb | Y |  | '[]'::jsonb |
| 19 | `promotion_rules` | jsonb | Y |  | '{}'::jsonb |
| 20 | `demotion_rules` | jsonb | Y |  | '{}'::jsonb |
| 21 | `backtest_compatible` | boolean | Y |  | false |
| 22 | `priority` | integer | Y |  | 0 |
| 23 | `version` | integer | Y |  | 1 |

**인덱스:**

- `strategy_cards_pkey`
- `idx_strategy_cards_user`
- `idx_strategy_cards_account`
- `idx_strategy_cards_live`

---

#### `strategy_performance` [공통]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('strategy_performance_ |
| 2 | `strategy_id` | character varying(50) | N |  |  |
| 3 | `strategy_name` | character varying(255) | N |  |  |
| 4 | `trade_date` | date | N |  |  |
| 5 | `real_trades` | integer | Y |  | 0 |
| 6 | `real_wins` | integer | Y |  | 0 |
| 7 | `real_losses` | integer | Y |  | 0 |
| 8 | `real_pnl` | real | Y |  | 0.0 |
| 9 | `real_win_rate` | real | Y |  | 0.0 |
| 10 | `virtual_trades` | integer | Y |  | 0 |
| 11 | `virtual_wins` | integer | Y |  | 0 |
| 12 | `virtual_losses` | integer | Y |  | 0 |
| 13 | `virtual_pnl` | real | Y |  | 0.0 |
| 14 | `virtual_win_rate` | real | Y |  | 0.0 |
| 15 | `performance_diff` | real | Y |  | 0.0 |
| 16 | `created_at` | timestamp without time zone | Y |  | now() |
| 17 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `idx_strategy_perf_date`
- `idx_strategy_perf_strategy`
- `strategy_performance_pkey`
- `strategy_performance_strategy_id_trade_date_key`

---

#### `trading_signals` [공통]

행 수: 137,185 | 크기: 30 MB | 최신: 2026-03-04

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('trading_signals_id_se |
| 2 | `user_id` | integer | N |  |  |
| 3 | `stock_code` | character varying(20) | N |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `strategy_name` | character varying(100) | N |  |  |
| 6 | `signal_type` | character varying(10) | N |  |  |
| 7 | `signal_strength` | real | Y |  | 0.0 |
| 8 | `detected_at` | timestamp without time zone | Y |  | now() |
| 9 | `executed_at` | timestamp without time zone | Y |  |  |
| 10 | `status` | character varying(20) | Y |  | 'PENDING'::character varying |
| 11 | `execution_price` | real | Y |  |  |
| 12 | `execution_quantity` | integer | Y |  |  |
| 13 | `notes` | text | Y |  |  |
| 14 | `created_at` | timestamp without time zone | Y |  | now() |
| 15 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `idx_trading_signals_detected_at`
- `idx_trading_signals_user_status`
- `trading_signals_pkey`

---

#### `waverider_signals` [공통]

행 수: 0 | 크기: 32 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('waverider_signals_id_ |
| 2 | `user_id` | integer | N |  |  |
| 3 | `ticker` | character varying(20) | N |  |  |
| 4 | `ticker_name` | character varying(100) | Y |  |  |
| 5 | `phase` | USER-DEFINED | N |  |  |
| 6 | `action` | USER-DEFINED | N |  |  |
| 7 | `confidence` | double precision | N |  |  |
| 8 | `current_price` | double precision | N |  |  |
| 9 | `target_price` | double precision | N |  |  |
| 10 | `stop_loss` | double precision | N |  |  |
| 11 | `take_profit` | double precision | N |  |  |
| 12 | `position_size_ratio` | double precision | N |  |  |
| 13 | `position_size_amount` | double precision | Y |  |  |
| 14 | `reason` | text | Y |  |  |
| 15 | `is_active` | boolean | Y |  |  |
| 16 | `is_executed` | boolean | Y |  |  |
| 17 | `executed_at` | timestamp without time zone | Y |  |  |
| 18 | `created_at` | timestamp without time zone | Y |  |  |
| 19 | `updated_at` | timestamp without time zone | Y |  |  |

**인덱스:**

- `waverider_signals_pkey`
- `ix_waverider_signals_id`
- `ix_waverider_signals_ticker`

---


### [UNIVERSE]

#### `go100_delisted_stocks` [GO100]

행 수: 100 | 크기: 72 kB | 최신: 2024-08-22

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_delisted_stocks |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `stock_name` | character varying(50) | Y |  |  |
| 4 | `market` | character varying(10) | Y |  |  |
| 5 | `listing_date` | date | Y |  |  |
| 6 | `delisting_date` | date | Y |  |  |
| 7 | `industry` | character varying(50) | Y |  |  |
| 8 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_delisted_stocks_pkey`
- `go100_delisted_stocks_stock_code_key`

---

#### `go100_fundamentals` [GO100]

행 수: 2,720 | 크기: 1904 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('go100_fundamentals_id |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `trade_date` | character varying(8) | N |  |  |
| 4 | `per` | numeric | Y |  |  |
| 5 | `pbr` | numeric | Y |  |  |
| 6 | `eps` | numeric | Y |  |  |
| 7 | `bps` | numeric | Y |  |  |
| 8 | `div_yield` | numeric | Y |  |  |
| 9 | `roe` | numeric | Y |  |  |
| 10 | `roa` | numeric | Y |  |  |
| 11 | `debt_ratio` | numeric | Y |  |  |
| 12 | `current_ratio` | numeric | Y |  |  |
| 13 | `op_margin` | numeric | Y |  |  |
| 14 | `net_margin` | numeric | Y |  |  |
| 15 | `revenue_growth` | numeric | Y |  |  |
| 16 | `market_cap` | bigint | Y |  |  |
| 17 | `source` | character varying(20) | Y |  | 'pykrx'::character varying |
| 18 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `go100_fundamentals_pkey`
- `go100_fundamentals_stock_code_trade_date_key`
- `idx_fundamentals_code_date`
- `idx_fundamentals_per`
- `idx_fundamentals_pbr`

---

#### `go100_fundamentals_pit` [GO100]

행 수: 32,920 | 크기: 6264 kB | 최신: 2025-12-31

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_fundamentals_pi |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `report_date` | date | N |  |  |
| 4 | `fiscal_year` | integer | Y |  |  |
| 5 | `fiscal_quarter` | integer | Y |  |  |
| 6 | `revenue` | bigint | Y |  |  |
| 7 | `operating_profit` | bigint | Y |  |  |
| 8 | `net_income` | bigint | Y |  |  |
| 9 | `total_assets` | bigint | Y |  |  |
| 10 | `total_equity` | bigint | Y |  |  |
| 11 | `total_debt` | bigint | Y |  |  |
| 12 | `per` | numeric | Y |  |  |
| 13 | `pbr` | numeric | Y |  |  |
| 14 | `roe` | numeric | Y |  |  |
| 15 | `debt_ratio` | numeric | Y |  |  |
| 16 | `source` | character varying(20) | Y |  | 'DART'::character varying |
| 17 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_fundamentals_pit_pkey`
- `go100_fundamentals_pit_stock_code_report_date_fiscal_quarte_key`
- `idx_fund_pit_code`
- `idx_fund_pit_date`

---

#### `go100_sector_correlation` [GO100]

행 수: 1,624 | 크기: 536 kB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_sector_correlat |
| 2 | `sector_a` | character varying(50) | N |  |  |
| 3 | `sector_b` | character varying(50) | N |  |  |
| 4 | `period` | character varying(10) | N |  |  |
| 5 | `correlation` | numeric | Y |  |  |
| 6 | `calculated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_sector_correlation_pkey`
- `go100_sector_correlation_sector_a_sector_b_period_key`

---

#### `go100_sector_price` [GO100]

행 수: 7,615 | 크기: 1352 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('go100_sector_price_id |
| 2 | `sector_name` | character varying(50) | N |  |  |
| 3 | `date` | character varying(8) | N |  |  |
| 4 | `avg_change_pct` | numeric | Y |  |  |
| 5 | `total_volume` | bigint | Y |  |  |
| 6 | `stock_count` | integer | Y |  |  |
| 7 | `top_gainer_code` | character varying(20) | Y |  |  |
| 8 | `top_gainer_pct` | numeric | Y |  |  |
| 9 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `go100_sector_price_pkey`
- `go100_sector_price_sector_name_date_key`

---

#### `v4_fundamental_quarterly` [V4.1]

행 수: 10,271 | 크기: 3992 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_fundamental_quarte |
| 2 | `symbol` | character varying(20) | N |  |  |
| 3 | `fiscal_year` | integer | N |  |  |
| 4 | `fiscal_quarter` | integer | N |  |  |
| 5 | `revenue` | bigint | Y |  |  |
| 6 | `operating_profit` | bigint | Y |  |  |
| 7 | `net_income` | bigint | Y |  |  |
| 8 | `eps` | numeric | Y |  |  |
| 9 | `bps` | numeric | Y |  |  |
| 10 | `roe` | numeric | Y |  |  |
| 11 | `per` | numeric | Y |  |  |
| 12 | `pbr` | numeric | Y |  |  |
| 13 | `operating_margin` | numeric | Y |  |  |
| 14 | `revenue_growth_yoy` | numeric | Y |  |  |
| 15 | `op_growth_yoy` | numeric | Y |  |  |
| 16 | `consensus_eps` | numeric | Y |  |  |
| 17 | `earnings_surprise` | numeric | Y |  |  |
| 18 | `data_source` | character varying(50) | Y |  | 'KIS_API'::character varying |
| 19 | `collected_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_fundamental_quarterly_pkey`
- `v4_fundamental_quarterly_symbol_fiscal_year_fiscal_quarter_key`
- `idx_fundamental_symbol`
- `idx_fundamental_quarter`
- `idx_fundamental_growth`

---

#### `v4_market_calendar` [V4.1]

행 수: 129 | 크기: 96 kB | 최신: 2026-12-30

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_market_calendar_id |
| 2 | `date` | date | N |  |  |
| 3 | `event_type` | character varying(50) | Y |  |  |
| 4 | `event_name` | character varying(200) | Y |  |  |
| 5 | `bet_modifier` | numeric | N |  |  |
| 6 | `desk1_active` | boolean | N |  |  |
| 7 | `desk2_active` | boolean | N |  |  |
| 8 | `desk3_active` | boolean | N |  |  |
| 9 | `desk4_active` | boolean | N |  |  |
| 10 | `desk5_active` | boolean | N |  |  |
| 11 | `class_restrictions` | json | Y |  |  |
| 12 | `note` | text | Y |  |  |
| 13 | `source` | character varying(20) | Y |  |  |
| 14 | `created_at` | timestamp with time zone | N |  | now() |
| 15 | `updated_at` | timestamp with time zone | Y |  |  |

**인덱스:**

- `v4_market_calendar_pkey`
- `uq_v4_calendar_date_event`

---

#### `v4_market_ranking` [V4.1]

행 수: 3,300 | 크기: 2296 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_market_ranking_id_ |
| 2 | `ranking_type` | character varying(30) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `rank_no` | integer | N |  |  |
| 5 | `stock_code` | character varying(12) | N |  |  |
| 6 | `stock_name` | character varying(100) | Y |  |  |
| 7 | `current_price` | bigint | Y |  |  |
| 8 | `change_rate` | numeric | Y |  |  |
| 9 | `volume` | bigint | Y |  |  |
| 10 | `trade_amount` | bigint | Y |  |  |
| 11 | `market_cap` | bigint | Y |  |  |
| 12 | `extra_data` | jsonb | Y |  |  |
| 13 | `collected_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_market_ranking_pkey`
- `v4_market_ranking_ranking_type_trade_date_rank_no_key`
- `idx_v4_market_ranking_type_date`
- `idx_v4_market_ranking_stock`

---

#### `v4_scalping_universe` [V4.1]

행 수: 1,354 | 크기: 368 kB | 최신: 2026-03-02

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_scalping_universe_ |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | Y |  |  |
| 4 | `market` | character varying(10) | Y |  |  |
| 5 | `avg_trade_value_20d` | bigint | Y |  |  |
| 6 | `avg_atr_pct_20d` | numeric | Y |  |  |
| 7 | `avg_volume_20d` | bigint | Y |  |  |
| 8 | `close_price` | integer | Y |  |  |
| 9 | `market_cap` | bigint | Y |  |  |
| 10 | `is_active` | boolean | Y |  | true |
| 11 | `created_date` | date | N |  |  |
| 12 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_scalping_universe_pkey`
- `v4_scalping_universe_stock_code_created_date_key`
- `idx_scalp_univ_date`
- `idx_scalp_univ_active`

---

#### `v4_sector_correlation` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_sector_correlation |
| 2 | `stock_code_a` | character varying(20) | N |  |  |
| 3 | `stock_code_b` | character varying(20) | N |  |  |
| 4 | `sector_code` | character varying(20) | Y |  |  |
| 5 | `period_days` | integer | Y |  | 60 |
| 6 | `correlation` | real | Y |  |  |
| 7 | `calc_date` | date | N |  |  |
| 8 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_sector_correlation_pkey`
- `v4_sector_correlation_stock_code_a_stock_code_b_calc_date_key`
- `idx_sc_sector`

---

#### `v4_sector_daily` [V4.1]

행 수: 15,608 | 크기: 12 MB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_sector_daily_id_se |
| 2 | `sector_code` | character varying(20) | N |  |  |
| 3 | `sector_name` | character varying(100) | Y |  |  |
| 4 | `trade_date` | date | N |  |  |
| 5 | `open_index` | numeric | Y |  |  |
| 6 | `high_index` | numeric | Y |  |  |
| 7 | `low_index` | numeric | Y |  |  |
| 8 | `close_index` | numeric | Y |  |  |
| 9 | `change_rate` | numeric | Y |  |  |
| 10 | `volume` | bigint | Y |  | 0 |
| 11 | `trade_amount` | bigint | Y |  | 0 |
| 12 | `change_rate_5d` | numeric | Y |  |  |
| 13 | `change_rate_20d` | numeric | Y |  |  |
| 14 | `sector_rank` | integer | Y |  |  |
| 15 | `collected_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_sector_daily_pkey`
- `v4_sector_daily_sector_code_trade_date_key`
- `idx_v4_sector_daily_date`
- `idx_v4_sector_daily_rank`

---

#### `v4_sector_mapping` [V4.1]

행 수: 3,844 | 크기: 5376 kB | 최신: 2026-03-07

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_sector_mapping_id_ |
| 2 | `symbol` | character varying(20) | N |  |  |
| 3 | `company_name` | character varying(100) | Y |  |  |
| 4 | `market` | character varying(10) | Y |  |  |
| 5 | `krx_sector_code` | character varying(10) | Y |  |  |
| 6 | `krx_sector_name` | character varying(50) | Y |  |  |
| 7 | `theme_tags` | ARRAY | Y |  |  |
| 8 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_sector_mapping_pkey`
- `v4_sector_mapping_symbol_key`
- `idx_sector_symbol`
- `idx_sector_krx`

---

#### `v4_sector_price` [V4.1]

행 수: 0 | 크기: 24 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_sector_price_id_se |
| 2 | `sector_code` | character varying(10) | N |  |  |
| 3 | `sector_name` | character varying(50) | Y |  |  |
| 4 | `trade_date` | date | N |  |  |
| 5 | `close_price` | numeric | Y |  |  |
| 6 | `change_rate` | numeric | Y |  |  |
| 7 | `volume` | bigint | Y |  |  |
| 8 | `trade_amount` | bigint | Y |  |  |
| 9 | `advance_count` | integer | Y |  |  |
| 10 | `decline_count` | integer | Y |  |  |
| 11 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_sector_price_pkey`
- `v4_sector_price_sector_code_trade_date_key`
- `idx_sector_price_date`

---

#### `v4_sector_stock_mapping` [V4.1]

행 수: 2,770 | 크기: 616 kB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_sector_stock_mappi |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `sector_code` | character varying(20) | N |  |  |
| 4 | `sector_name` | character varying(100) | Y |  |  |
| 5 | `market` | character varying(10) | Y |  |  |
| 6 | `market_cap_rank` | integer | Y |  |  |
| 7 | `created_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_sector_stock_mapping_pkey`
- `v4_sector_stock_mapping_stock_code_sector_code_key`
- `idx_ssm_stock`
- `idx_ssm_sector`

---

#### `v4_stock_master` [V4.1]

행 수: 3,844 | 크기: 624 kB | 최신: 2026-03-18

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `stock_code` | character varying(20) | N | PK |  |
| 2 | `stock_name` | character varying(100) | N |  |  |
| 3 | `market` | character varying(10) | Y |  |  |
| 4 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_stock_master_pkey`
- `idx_sm_name`

---

#### `v4_stock_sector` [V4.1]

행 수: 4,225 | 크기: 840 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `stock_code` | character varying(10) | N | PK |  |
| 2 | `sector_code` | character varying(10) | N |  |  |
| 3 | `sector_name` | character varying(50) | N |  |  |
| 4 | `updated_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_stock_sector_pkey`
- `idx_v4_stock_sector_code`

---

#### `v4_theme_activity_daily` [V4.1]

행 수: 34,122 | 크기: 5048 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_theme_activity_dai |
| 2 | `date` | date | N |  |  |
| 3 | `theme_code` | character varying(20) | N |  |  |
| 4 | `activity_score` | numeric | Y |  |  |
| 5 | `status` | character varying(10) | Y |  |  |
| 6 | `avg_volume_ratio` | numeric | Y |  |  |
| 7 | `avg_return_pct` | numeric | Y |  |  |
| 8 | `supply_positive_ratio` | numeric | Y |  |  |
| 9 | `stock_count` | integer | Y |  |  |
| 10 | `created_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_theme_activity_daily_pkey`
- `uq_v4_theme_activity_date`

---

#### `v4_theme_daily` [V4.1]

행 수: 34,122 | 크기: 11 MB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_theme_daily_id_seq |
| 2 | `theme_code` | character varying(20) | N |  |  |
| 3 | `trade_date` | date | N |  |  |
| 4 | `theme_change_rate` | numeric | Y |  |  |
| 5 | `theme_volume` | bigint | Y |  | 0 |
| 6 | `theme_trade_amount` | bigint | Y |  | 0 |
| 7 | `leader_stock_code` | character varying(12) | Y |  |  |
| 8 | `leader_change_rate` | numeric | Y |  |  |
| 9 | `leader_volume` | bigint | Y |  | 0 |
| 10 | `consecutive_up_days` | integer | Y |  | 0 |
| 11 | `stock_count` | integer | Y |  | 0 |
| 12 | `up_stock_count` | integer | Y |  | 0 |
| 13 | `collected_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_theme_daily_pkey`
- `v4_theme_daily_theme_code_trade_date_key`
- `idx_v4_theme_daily_date`
- `idx_v4_theme_daily_rate`

---

#### `v4_theme_detail` [V4.1]

행 수: 142 | 크기: 328 kB | 최신: 2026-03-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `theme_code` | character varying(20) | N | PK |  |
| 2 | `theme_name` | character varying(100) | Y |  |  |
| 3 | `detail` | jsonb | Y |  |  |
| 4 | `collected_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_theme_detail_pkey`

---

#### `v4_theme_mapping` [V4.1]

행 수: 551 | 크기: 1784 kB | 최신: 2026-03-07

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_theme_mapping_id_s |
| 2 | `symbol` | character varying(20) | N |  |  |
| 3 | `theme_name` | character varying(200) | N |  |  |
| 4 | `theme_code` | character varying(20) | Y |  |  |
| 5 | `source` | character varying(50) | Y |  |  |
| 6 | `is_leader` | boolean | Y |  | false |
| 7 | `updated_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `v4_theme_mapping_pkey`
- `idx_theme_symbol`
- `idx_theme_name`
- `uq_theme_symbol_name`

---

#### `v4_theme_master` [V4.1]

행 수: 142 | 크기: 120 kB | 최신: 2026-03-10

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('v4_theme_master_id_se |
| 2 | `theme_code` | character varying(20) | N |  |  |
| 3 | `theme_name` | character varying(100) | N |  |  |
| 4 | `description` | text | Y |  |  |
| 5 | `is_active` | boolean | Y |  | true |
| 6 | `first_seen_date` | date | Y |  |  |
| 7 | `last_updated` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_theme_master_pkey`
- `v4_theme_master_theme_code_key`
- `idx_v4_theme_master_active`

---

#### `v4_theme_stock` [V4.1]

행 수: 7,496 | 크기: 1792 kB | 최신: 2026-03-25

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_theme_stock_id_seq |
| 2 | `theme_code` | character varying(20) | N |  |  |
| 3 | `stock_code` | character varying(12) | N |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `is_leader` | boolean | Y |  | false |
| 6 | `mapped_date` | date | N |  |  |
| 7 | `collected_at` | timestamp with time zone | Y |  | now() |

**인덱스:**

- `v4_theme_stock_pkey`
- `v4_theme_stock_theme_code_stock_code_mapped_date_key`
- `idx_v4_theme_stock_theme`
- `idx_v4_theme_stock_stock`

---

#### `v4_theme_stock_backup_20260228` [V4.1]

행 수: 2,106 | 크기: 192 kB | 최신: 2026-02-27

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | Y |  |  |
| 2 | `theme_code` | character varying(20) | Y |  |  |
| 3 | `stock_code` | character varying(12) | Y |  |  |
| 4 | `stock_name` | character varying(100) | Y |  |  |
| 5 | `is_leader` | boolean | Y |  |  |
| 6 | `mapped_date` | date | Y |  |  |
| 7 | `collected_at` | timestamp with time zone | Y |  |  |

---

#### `v4_theme_stock_mapping` [V4.1]

행 수: 0 | 크기: 16 kB

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_theme_stock_mappin |
| 2 | `theme_code` | character varying(20) | N |  |  |
| 3 | `theme_name` | character varying(50) | Y |  |  |
| 4 | `ticker` | character varying(20) | N |  |  |
| 5 | `stock_name` | character varying(100) | Y |  |  |
| 6 | `is_leader` | boolean | N |  |  |
| 7 | `relevance` | integer | N |  |  |
| 8 | `updated_at` | timestamp with time zone | N |  | now() |

**인덱스:**

- `v4_theme_stock_mapping_pkey`
- `uq_v4_theme_ticker`

---

#### `v4_universe_version` [V4.1]

행 수: 16 | 크기: 112 kB | 최신: 2026-02-14

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | bigint | N | PK | nextval('v4_universe_version_i |
| 2 | `version_name` | character varying(80) | N |  |  |
| 3 | `effective_from` | date | N |  |  |
| 4 | `effective_to` | date | Y |  |  |
| 5 | `source` | character varying(40) | N |  | 'SYSTEM'::character varying |
| 6 | `created_at` | timestamp with time zone | N |  | CURRENT_TIMESTAMP |
| 7 | `updated_at` | timestamp with time zone | N |  | CURRENT_TIMESTAMP |
| 8 | `stock_count` | integer | N |  | 0 |
| 9 | `criteria_json` | jsonb | Y |  |  |
| 10 | `note` | text | Y |  |  |
| 11 | `is_active` | boolean | N |  | true |
| 12 | `created_by` | character varying(40) | Y |  |  |
| 13 | `approved_at` | timestamp with time zone | Y |  |  |
| 14 | `checksum_sha256` | character varying(64) | Y |  |  |
| 15 | `published_at` | timestamp with time zone | Y |  |  |
| 16 | `config_snapshot` | jsonb | Y |  |  |
| 17 | `row_count` | integer | N |  | 0 |

**인덱스:**

- `v4_universe_version_pkey`
- `uq_v4_universe_version_name`
- `ix_v4_universe_version_effective_from`
- `ix_v4_universe_version_is_active`

---

#### `financial_ratios` [공통]

행 수: 45,870 | 크기: 6688 kB | 최신: 2026-02-11

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('financial_ratios_id_s |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `stac_yymm` | character varying(6) | N |  |  |
| 4 | `grs` | real | Y |  |  |
| 5 | `bsop_prfi_inrt` | real | Y |  |  |
| 6 | `ntin_inrt` | real | Y |  |  |
| 7 | `roe_val` | real | Y |  |  |
| 8 | `eps` | real | Y |  |  |
| 9 | `sps` | real | Y |  |  |
| 10 | `bps` | real | Y |  |  |
| 11 | `rsrv_rate` | real | Y |  |  |
| 12 | `lblt_rate` | real | Y |  |  |
| 13 | `created_at` | timestamp without time zone | Y |  | now() |

**인덱스:**

- `financial_ratios_pkey`
- `financial_ratios_stock_code_stac_yymm_key`

---

#### `stock_fundamentals` [공통]

행 수: 33,831 | 크기: 5528 kB | 최신: 2026-02-26

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('stock_fundamentals_id |
| 2 | `stock_code` | character varying(10) | N |  |  |
| 3 | `date` | character varying(8) | N |  |  |
| 4 | `per` | real | Y |  |  |
| 5 | `pbr` | real | Y |  |  |
| 6 | `eps` | real | Y |  |  |
| 7 | `bps` | real | Y |  |  |
| 8 | `market_cap` | bigint | Y |  |  |
| 9 | `shares_outstanding` | bigint | Y |  |  |
| 10 | `face_value` | real | Y |  |  |
| 11 | `capital` | bigint | Y |  |  |
| 12 | `loan_remain_rate` | real | Y |  |  |
| 13 | `created_at` | timestamp without time zone | Y |  | now() |
| 14 | `roe` | real | Y |  |  |
| 15 | `dividend_yield` | real | Y |  |  |
| 16 | `revenue` | bigint | Y |  |  |
| 17 | `operating_profit` | bigint | Y |  |  |

**인덱스:**

- `stock_fundamentals_pkey`
- `stock_fundamentals_stock_code_date_key`

---

#### `stock_universe` [공통]

행 수: 3,844 | 크기: 2704 kB | 최신: 2026-02-20

| # | 컬럼 | 타입 | NULL | PK | 기본값 |
|---|------|------|------|----|--------|
| 1 | `id` | integer | N | PK | nextval('stock_universe_id_seq |
| 2 | `stock_code` | character varying(20) | N |  |  |
| 3 | `stock_name` | character varying(100) | N |  |  |
| 4 | `market` | character varying(10) | N |  |  |
| 5 | `market_cap` | bigint | Y |  |  |
| 6 | `trade_volume` | bigint | Y |  |  |
| 7 | `trade_amount` | bigint | Y |  |  |
| 8 | `sector` | character varying(100) | Y |  |  |
| 9 | `rank_market_cap` | integer | Y |  |  |
| 10 | `rank_trade_amount` | integer | Y |  |  |
| 11 | `collected_at` | timestamp without time zone | Y |  | now() |
| 12 | `is_active` | boolean | Y |  | true |
| 13 | `per` | numeric | Y |  |  |
| 14 | `pbr` | numeric | Y |  |  |
| 15 | `eps` | numeric | Y |  |  |
| 16 | `dividend_yield` | numeric | Y |  |  |
| 17 | `market_cap_value` | bigint | Y |  |  |
| 18 | `sector_large` | character varying(100) | Y |  |  |
| 19 | `sector_mid` | character varying(100) | Y |  |  |
| 20 | `sector_small` | character varying(100) | Y |  |  |
| 21 | `is_nxt` | boolean | Y |  | false |

**인덱스:**

- `stock_universe_pkey`
- `idx_stock_universe_code_date`
- `idx_stock_universe_active_code`
- `idx_stock_universe_collected`
- `idx_stock_universe_nxt`

---

## 3. 테이블 관계 (Foreign Keys)

| From 테이블 | From 컬럼 | -> To 테이블 | To 컬럼 |
|-----------|---------|-----------|--------|
| `account_rate_quotas` | `account_id` | `accounts` | `account_id` |
| `account_snapshots` | `user_id` | `users` | `id` |
| `accounts` | `user_id` | `v4_users` | `user_id` |
| `auto_trade_positions` | `user_id` | `users` | `id` |
| `autotrade_positions` | `user_id` | `users` | `id` |
| `backtests` | `user_id` | `users` | `id` |
| `compound_trades` | `portfolio_id` | `portfolios` | `id` |
| `compound_trades` | `user_id` | `users` | `id` |
| `go100_agent_performance` | `user_id` | `v4_users` | `user_id` |
| `go100_agent_reports` | `user_id` | `v4_users` | `user_id` |
| `go100_agent_self_review` | `user_id` | `v4_users` | `user_id` |
| `go100_ai_predictions` | `user_id` | `v4_users` | `user_id` |
| `go100_alerts` | `user_id` | `v4_users` | `user_id` |
| `go100_backtest_runs` | `go100_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_commander_decisions` | `user_id` | `v4_users` | `user_id` |
| `go100_evolution_loops` | `hypothesis_id` | `go100_strategy_hypotheses` | `hypothesis_id` |
| `go100_fit_analysis` | `go100_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_optimization_runs` | `parent_run_id` | `go100_optimization_runs` | `opt_run_id` |
| `go100_optimization_runs` | `optimized_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_optimization_runs` | `original_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_orderbook_backtest_runs` | `strategy_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_paper_accounts` | `user_id` | `v4_users` | `user_id` |
| `go100_paper_orders` | `card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_paper_positions` | `card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_paper_trading_sessions` | `strategy_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_pending_configs` | `user_id` | `v4_users` | `user_id` |
| `go100_pending_configs` | `evolution_loop_id` | `go100_evolution_loops` | `id` |
| `go100_portfolio_allocations` | `card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_portfolio_allocations` | `user_id` | `v4_users` | `user_id` |
| `go100_portfolio_snapshots` | `user_id` | `v4_users` | `user_id` |
| `go100_portfolios` | `go100_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_portfolios` | `account_id` | `accounts` | `account_id` |
| `go100_portfolios` | `user_id` | `v4_users` | `user_id` |
| `go100_position_sizing` | `strategy_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_research_iterations` | `hypothesis_id` | `go100_strategy_hypotheses` | `hypothesis_id` |
| `go100_risk_disclaimers` | `strategy_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_stock_profiles` | `evolution_loop_id` | `go100_evolution_loops` | `id` |
| `go100_strategy_cards` | `parent_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_strategy_cards` | `user_id` | `v4_users` | `user_id` |
| `go100_strategy_cards` | `account_id` | `accounts` | `account_id` |
| `go100_strategy_hypotheses` | `created_card_id` | `go100_strategy_cards` | `go100_card_id` |
| `go100_strategy_hypotheses` | `user_id` | `v4_users` | `user_id` |
| `go100_strategy_knowledge` | `user_id` | `v4_users` | `user_id` |
| `go100_strategy_portfolio_snapshots` | `user_id` | `v4_users` | `user_id` |
| `go100_strategy_portfolios` | `user_id` | `v4_users` | `user_id` |
| `kis_configs` | `user_id` | `users` | `id` |
| `liquidation_logs` | `session_id` | `liquidation_sessions` | `session_id` |
| `liquidation_orders` | `session_id` | `liquidation_sessions` | `session_id` |
| `orders` | `user_id` | `users` | `id` |
| `orders` | `signal_id` | `trading_signals` | `id` |
| `payments` | `user_id` | `users` | `id` |
| `pending_orders` | `user_id` | `users` | `id` |
| `portfolios` | `user_id` | `users` | `id` |
| `positions` | `portfolio_id` | `portfolios` | `id` |
| `social_accounts` | `user_id` | `users` | `id` |
| `strategy_allocations` | `strategy_id` | `strategies` | `id` |
| `strategy_allocations` | `user_id` | `users` | `id` |
| `strategy_cards` | `user_id` | `v4_users` | `user_id` |
| `strategy_cards` | `account_id` | `accounts` | `account_id` |
| `trade_comparisons` | `virtual_trade_id` | `virtual_trades` | `id` |
| `trade_comparisons` | `real_trade_id` | `real_trades` | `id` |
| `trade_verifications` | `real_trade_id` | `real_trades` | `id` |
| `trades` | `user_id` | `users` | `id` |
| `trades` | `strategy_id` | `strategies` | `id` |
| `trading_signals` | `user_id` | `users` | `id` |
| `user_push_subscriptions` | `user_id` | `users` | `id` |
| `user_sessions` | `user_id` | `v4_users` | `user_id` |
| `user_settings` | `user_id` | `users` | `id` |
| `user_strategies` | `strategy_id` | `strategies` | `id` |
| `user_strategies` | `user_id` | `users` | `id` |
| `v4_api_error_log` | `account_config_id` | `v4_account_config` | `id` |
| `v4_api_tokens` | `account_config_id` | `v4_account_config` | `id` |
| `v4_backtest_daily` | `session_id` | `v4_backtest_sessions` | `session_id` |
| `v4_backtest_results` | `user_id` | `users` | `id` |
| `v4_backtest_runs` | `strategy_card_id` | `strategy_cards` | `card_id` |
| `v4_backtest_summary` | `session_id` | `v4_backtest_sessions` | `session_id` |
| `v4_backtest_trades` | `result_id` | `v4_backtest_results` | `id` |
| `v4_backtest_trades` | `session_id` | `v4_backtest_sessions` | `session_id` |
| `v4_bt_daily_risk_log` | `bt_session_id` | `v4_bt_sessions` | `id` |
| `v4_bt_discoveries` | `session_id` | `v4_bt_sessions` | `session_id` |
| `v4_bt_discovery_log` | `bt_session_id` | `v4_bt_sessions` | `id` |
| `v4_bt_trades` | `session_id` | `v4_bt_sessions` | `session_id` |
| `v4_bt_versions` | `session_id` | `v4_bt_sessions` | `session_id` |
| `v4_chat_messages` | `session_id` | `v4_chat_sessions` | `id` |
| `v4_chat_sessions` | `user_id` | `v4_users` | `user_id` |
| `v4_llm_usage` | `user_id` | `v4_users` | `user_id` |
| `v4_notification_channel_config` | `user_id` | `v4_users` | `user_id` |
| `v4_notification_settings` | `user_id` | `v4_users` | `user_id` |
| `v4_notifications` | `user_id` | `v4_users` | `user_id` |
| `v4_order_executions` | `position_id` | `v4_positions` | `id` |
| `v4_peak_exits` | `entry_id` | `v4_smart_entries` | `id` |
| `v4_positions` | `signal_id` | `v4_signals` | `signal_id` |
| `v4_positions` | `chain_id` | `v4_pyramid_chain` | `chain_id` |
| `v4_pyramid_chain_log` | `chain_id` | `v4_pyramid_chain` | `chain_id` |
| `v4_reservations` | `order_request_id` | `v4_order_requests` | `id` |
| `v4_smart_entries` | `signal_id` | `v4_explosion_signals` | `id` |
| `v4_trade_executions` | `user_id` | `v4_users` | `user_id` |
| `v4_trade_executions` | `account_id` | `accounts` | `account_id` |
| `v4_trade_schedules` | `user_id` | `v4_users` | `user_id` |
| `v4_trade_schedules` | `account_id` | `accounts` | `account_id` |
| `v4_trades` | `position_id` | `v4_positions` | `id` |
| `v4_user_settings` | `user_id` | `v4_users` | `user_id` |
| `v4_user_strategies` | `user_id` | `users` | `id` |
| `waverider_configs` | `user_id` | `users` | `id` |
| `waverider_performance` | `user_id` | `users` | `id` |
| `waverider_positions` | `signal_id` | `waverider_signals` | `id` |
| `waverider_positions` | `user_id` | `users` | `id` |
| `waverider_signals` | `user_id` | `users` | `id` |

---

## 4. 프로젝트 간 규칙

### 소유권
- `go100_*` 테이블: GO100 프로젝트 소유. V4.1은 bridge.py를 통해서만 접근.
- `v4_*` 테이블: V4.1 프로젝트 소유. GO100은 직접 접근 금지.
- 접두어 없는 테이블 (ohlcv_daily, accounts 등): 공통. 양쪽 READ 허용.

### 보호 규칙 (CEO 절대 규칙)
- `strategy_cards`: ALTER / DROP / DELETE 금지 (UPDATE는 CEO 승인 후)
- `v4_positions`: 직접 편집 금지
- `accounts` id 5, 6: 실계좌 -- FORBIDDEN_ACCOUNT_IDS {5, 6}
- 원본 테이블: READ ONLY

### 논리적 조인 키 (FK 미설정이지만 코드에서 사용)
- `ohlcv_daily.ticker` <-> `v4_investor_daily.ticker` (종목코드)
- `strategy_cards.id` <-> `v4_positions.strategy_id` (전략ID)
- `accounts.account_id` <-> `v4_positions.account_id` (계좌ID)
- `ohlcv_daily.ticker` <-> `v4_ohlcv_minute.ticker` (종목코드)

### 대형 테이블 주의
- `v4_ohlcv_minute`: 84M+ rows -- 풀스캔 금지, 반드시 ticker+datetime 인덱스 사용
- `ohlcv_daily`: 2.6M+ rows -- ticker+date 인덱스 사용
- `go100_news_items`: 2.1M+ rows -- 날짜 필터 필수

## 5. 자동 최신화

- 생성기: `/root/kis-autotrade-v4/scripts/generate_db_catalog.py`
- 쉘 래퍼: `/root/kis-autotrade-v4/scripts/update_db_catalog.sh`
- cron: 매일 06:00 자동 실행
- 변경 이력: `/root/project-docs/shared/DB-SCHEMA-CHANGELOG.md`
- 변경 감지 시 자동 git push
