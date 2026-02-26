# KIS AutoTrade V4.1 — 시스템 아키텍처 문서

```
================================================================
KIS AutoTrade V4.1 자동매매 시스템
시스템 아키텍처 문서
================================================================
문서 버전: 1.2
작성일: 2026-02-23
작성자: Claude Code (자동 생성)
상태: 현행 운영 기준 (phase-2c-command-center 브랜치)
================================================================
```

---

## CHANGELOG (v1.1 → v1.2)

| 항목 | v1.1 | v1.2 |
|------|------|------|
| strategy_cards | 59건 | 62건(문서 기준) / DB 실제 65건 |
| v4_positions OPEN | — | 5건 (ID 49, 51, 53, 55, 61) |
| 분할매매/이관 | 미반영 | split_transfer_engine, v4_position_transfers 반영 |
| NXT 거래소 | 미반영 | EXCHANGE_MAP NXT, broker_base exchange, API 레지스트리 반영 |
| 백테스트 v2 | 일부 | v4_backtest_trades 36컬럼(분할/이관/레짐 등) 확장 반영 |
| 코드 검수 파이프라인 | 미반영 | review/, push_review.sh, clean_review.sh 반영 |
| GO100 프론트엔드 | 미반영 | go100-frontend.service, go100.service 통합 현황 |
| DB 테이블 목록 | 요약 | public 전 테이블 카테고리별 정리 |
| 서비스 상태 | v1.1 시점 | 2026-02-23 기준 kis / go100 서비스 목록 |

---

## 1. 전체 매핑 테이블 (기획 원본 vs 실제 구현)

ORIGINAL-20260213 문서 20개 LAYER/INFRA + 추가 발견 기능 기준.

| 구분 | 항목 | 상태 | 관련 파일/테이블 |
|------|------|------|------------------|
| LAYER 0 | System Orchestrator | ✅ 구현완료 | v4_pipeline_orchestrator.py, lifecycle, v4_system_heartbeat, v4_system_state_log |
| LAYER 1-A | Market Regime Detector | ✅ 구현완료 | regime_detector, v4_market_regime_daily |
| LAYER 1-B | Market Calendar | ✅ 구현완료 | v4_market_calendar, 기재부 공휴일 |
| LAYER 2-A | Chief Analyst | 🔧 부분구현 | 유니버스/리서치 경로 일부 |
| LAYER 2-B | Fund Commander | ✅ 구현완료 | fund/, v4_desk_fund, v4_fund_pool_snapshot, v4_reservations |
| LAYER 3 | Market Brain / 5 DESK | ✅ 구현완료 | strategy_cards desk_id 1~5, DESK_CONFIGS (split_transfer_engine) |
| LAYER 4 | Strategy Engine | ✅ 구현완료 | strategy_engine.py, strategies/, v4_signals |
| LAYER 5-A | Risk Manager 2계층 | ✅ 구현완료 | v4_risk_manager.py, risk_params |
| LAYER 5-B | Order Executor | ✅ 구현완료 | v4_order_executor.py, kis_order_service.py, v4_trade_bridge |
| LAYER 5-C | Fund Pool + Reservation | ✅ 구현완료 | v4_fund_pool_snapshot, v4_reservations, v4_desk_fund |
| LAYER 6 | Position Manager | ✅ 구현완료 | position_manager, v4_position_monitor, lifecycle |
| LAYER 7 | Adaptive Engine | 🔧 부분구현 | adaptive/ (weekly_scoring, fund_rebalancer, param_optimizer, regime_weight) |
| INFRA-A | Data Provider + Price Poller | ✅ 구현완료 | data_pipeline, collectors, v4_ohlcv_minute, ohlcv_daily |
| INFRA-B | Data Quality Tracker | 🔧 부분구현 | 데이터 품질 검사 일부 |
| INFRA-C | Fault Injection | ❌ 미구현 | — |
| INFRA-D | 운영 지표 + 알림 | ✅ 구현완료 | v4_alerts, v4_notifications, monitoring, notification |
| 🆕 | 분할매매/이관 | ✅ 구현완료 | split_transfer_engine.py, v4_position_transfers, v4_positions.split_phase |
| 🆕 | NXT 거래소 통합 | 🔧 부분구현 | broker_base OrderRequest.exchange, broker_kiwoom EXCHANGE_MAP, kis_api_registry NXT 6종 |
| 🆕 | 코드 검수 파이프라인 | ✅ 구현완료 | project-docs/kis-autotrade-v4/review/, scripts/push_review.sh, clean_review.sh |
| 🆕 | GO100 프론트엔드 | ✅ 구현완료 | go100-frontend.service, go100.service (8002) |
| 🆕 | 백테스트 엔진 v2 확장 | ✅ 구현완료 | backtest_engine_v2.py, v4_backtest_trades 36컬럼 |

---

## 2. DESK별 현황 (2026-02-23 스캔)

| desk_id | is_live=true | is_live=false | 합계 | OPEN 포지션 |
|---------|--------------|---------------|------|-------------|
| 1 | 10 | 0 | 10 | 1 (221800) |
| 2 | 10 | 6 | 16 | 2 (001510, 001290) |
| 3 | 9 | 3 | 12 | 1 (373110) |
| 4 | 6 | 3 | 9 | 1 (360140) |
| 5 | 1 | 9 | 10 | 0 |
| NULL | 0 | 8 | 8 | — |
| **합계** | **36** | **29** | **65** | **5** |

- 문서 기준 strategy_cards 62건은 과거 스냅샷; 현재 DB count(*) = 65.
- v4_positions OPEN 5건: id 49(ticker 221800), 51(001510), 53(001290), 55(373110), 61(360140).

---

## 3. 분할매매/이관 구현 현황

| 구분 | 내용 |
|------|------|
| 테이블 | v4_position_transfers (이관 이력), v4_positions.split_phase / remaining_qty / original_desk_id / buy_phase |
| 코드 | backend/app/services/trading/split_transfer_engine.py (DESK_CONFIGS, SPLIT_SELL/TRANSFER_UP/TRANSFER_DOWN, execute_split_sell, execute_transfer) |
| 오케스트레이터 | v4_pipeline_orchestrator: _desk3_receive_transfers, _desk4_receive_transfers, _desk5_receive_transfers, split_transfer_engine 호출 |
| 백테스트 | v4_backtest_trades 컬럼: split_phase, transfer_to |
| 동작 | 오케스트레이터 60초 사이클 내 분할매도·DESK 인계 실행, v4_position_transfers INSERT 및 v4_desk_fund 조정 |

---

## 4. NXT 거래소 통합 현황

| 구분 | 내용 |
|------|------|
| 주문 파라미터 | OrderRequest.exchange = "KRX" \| "NXT" \| "SOR" (broker_base.py) |
| 키움 클라이언트 | EXCHANGE_MAP = {"KRX": ("KRX",""), "NXT": ("NXT","_NX"), "SOR": ("SOR","_AL")}, stk_cd 접미사 _NX (broker_kiwoom_client.py) |
| KIS API 레지스트리 | NXT실시간체결가, NXT실시간호가, NXT시간외체결가, NXT시간외호가, NXT VI발동, NXT체결통보 (kis_api_registry.py) |
| 계좌 동기화 | account_sync_manager: NXT 시장 08:00~20:00, 동기화 가능 07:55~20:05 KST |
| 실계좌 NXT 주문 | kis_order_service 경유 시 base_url/실전 도메인 사용; NXT 주문 시 exchange 전달 필요 |

---

## 5. 백테스트 엔진 v2 확장 (v4_backtest_trades)

- 건수: 176,896행.
- 컬럼 (36개): id, session_id, desk_id, stock_code, trade_date, trade_type, quantity, price, amount, **split_phase, transfer_to**, pnl, pnl_pct, reason, card_id, exit_reason, entry_date, exit_date, hold_days, **entry_datetime, exit_datetime**, entry_price, exit_price, **mfe_pct, mae_pct**, mfe_price, mae_price, **regime_at_entry**, **indicator_snapshot**, **slippage_pct**, **commission**, **sector**, **strategy_name**, **entry_volume**, **entry_spread_pct**.

---

## 6. DB 테이블 총 목록 (카테고리별)

- **시장 데이터:** stock_universe, ohlcv_daily, ohlcv_weekly, ohlcv_monthly, v4_ohlcv_minute(파티션), v4_investor_daily, v4_stock_sector, v4_vkospi_daily, index_daily, market_data_min, market_turnover_daily, scalping_features_daily
- **사용자/계좌:** v4_users, users, accounts, account_rate_quotas, user_sessions, v4_account_holdings, v4_account_sync_log, v4_account_config, account_snapshots
- **전략/트레이딩:** strategy_cards, v4_desk_strategy_mapping, v4_positions, v4_position_transfers, v4_trades, v4_desk_fund, v4_signals, v4_orders, v4_order_executions, v4_order_requests, v4_reservations, v4_fund_pool_snapshot, v4_fund_lending
- **백테스트:** v4_backtest_runs, v4_backtest_sessions, v4_backtest_daily, v4_backtest_trades, v4_backtest_trade_log, v4_backtest_results, v4_backtest_equity, v4_backtest_profile, v4_backtest_summary, v4_backtest_desk_detail, v4_backtest_results_desk_run, v4_backtest_runs_legacy
- **시스템:** v4_alerts, v4_notifications, v4_reports, v4_api_error_log, v4_api_tokens, v4_system_heartbeat, v4_system_state_log, v4_market_regime_daily, v4_market_calendar, v4_migration_history, v4_minute_collect_progress, v4_notification_channel_config, v4_notification_settings, llm_requests, llm_cost_daily
- **데스크/분할·이관:** v4_desk_fund, v4_desk_strategy_mapping, v4_position_transfers
- **GO100:** go100_account_reconciliation, go100_backtest_runs, go100_desk_allocation, go100_fit_analysis, go100_orders, go100_portfolio_snapshots, go100_portfolios, go100_positions, go100_risk_disclaimers, go100_strategy_cards, go100_trades
- **기타:** v4_chat_messages, v4_chat_sessions, v4_condition_search, v4_credit_balance, v4_daily_portfolio, v4_daily_reports, v4_theme_*, v4_tick_data, v4_trade_analysis, v4_trade_executions, v4_trade_schedules, v4_trade_strength_history, v4_scalping_signals, v4_scalping_universe, v4_scoring_weights, v4_sector_daily, v4_sector_price, v4_stage_transitions, v4_strategy_performance, v4_strategy_registry, v4_bet_history, v4_broker_trades, v4_pick_reasons, v4_position_extended, v4_program_trades, v4_universe_version, v4_user_settings, v4_user_strategies, v4_market_*, kis_configs, 기타 레거시

(v4_split_* 전용 테이블 없음; 분할/이관은 v4_positions + v4_position_transfers로 처리.)

---

## 7. systemd 서비스 상태 (2026-02-23)

| 서비스 | 상태 | 비고 |
|--------|------|------|
| kis-v41-api | active (running) | 포트 8003 |
| kis-v41-monitor | active | 포지션 모니터 |
| kis-v41-position-monitor | active | 포지션 리스크 모니터 |
| kis-v41-scheduler | active | 매매 스케줄러 |
| go100.service | active (running) | GO100 API (8002) |
| go100-frontend.service | active (running) | GO100 V4.1 Frontend (Next.js) |
| kis-scalping.service | active | 스캘핑 스케줄러 |
| kis-trading-engine.service | active | 통합 트레이딩 엔진 |
| kis-webapp-api.service | active | 레거시 Web API |

---

## 8. 코드 검수 파이프라인

| 항목 | 경로/용도 |
|------|------------|
| 검수 디렉토리 | /root/project-docs/kis-autotrade-v4/review/ (파일명: *__REVIEW__&lt;작업ID&gt;.*) |
| 업로드 스크립트 | /root/project-docs/scripts/push_review.sh &lt;작업ID&gt; (보안검사 후 git commit/push) |
| 정리 스크립트 | /root/project-docs/scripts/clean_review.sh (승인 후 __REVIEW__* 파일 삭제 후 push) |
| 규칙 | .cursor/rules/kis-v41-rules.md, report/v41/CODE-REVIEW-PIPELINE-20260223.md |

---

## 9. GO100 프론트엔드 통합 현황

- go100-frontend.service: Next.js 프론트엔드, active.
- go100.service: 백엔드 API 8002, active.
- Nginx: /api/v4/*, /ws/* → 8002 연동.
- 도메인: trading41.newtalk.kr.

---

## 10. 알려진 이슈 목록

- strategy_cards DB 65건 vs 문서 기준 62건 (추가 카드 반영 여부 확인 권장).
- v4_positions 컬럼명: stock_code 없음, ticker 사용.
- Redis token 키: token:kis:kis:4 등 (account_id = "kis:config_id"); TTL -2 시 만료 상태.
- NXT 실전 주문: 2/24 NXT 프리마켓 08:00 이후 실행 예정, 사전 준비만 완료.

---

## 11. 버전 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0 | 2026-02-20 | 초판 (architecture-v1.0.md 통합 형태) |
| 1.1 | 2026-02-21 | V4.1 전용 분리, SECIND-V2, strategy_cards 59건, 서비스 상태 |
| 1.2 | 2026-02-23 | 분할매매/이관/NXT/BT 확장/검수 파이프라인/GO100 반영, DESK 현황, DB 테이블 목록, OPEN 5건 |

================================================================
문서 끝 (v41-architecture-v1.2.md)
================================================================
