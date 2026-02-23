# ARCHITECTURE-FULL-SCAN-V1.2 — 전체 모듈 전수조사 보고서

**작업 ID:** ARCHITECTURE-FULL-SCAN-V1.2  
**일시:** 2026-02-23 17:00 KST  
**서버:** root@211.188.51.113  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  
**작업자:** Cursor AI (읽기전용)  
**승인:** 자체승인 (CEO 지시)

---

## 1. Phase A 수집 결과 요약

### A-1. 서비스 Python 파일

- `backend/app/services/` 하위 **약 220개** .py 파일 (trading, execution, strategy, position, brain, market, adaptive, backtest, go100, monitoring, notification 등).

### A-2. 핵심 트레이딩 모듈

| 모듈 | 경로 | 비고 |
|------|------|------|
| Split Transfer Engine | trading/split_transfer_engine.py | class SplitTransferEngine, TransferResult, DESK_CONFIGS, DEMOTION_* |
| Fund Commander / Fund Pool | brain/fund_commander.py, execution/fund_pool.py, reservation.py | FundPool.rebuild_from_db, can_allocate, desk_limits |
| Position / Lifecycle | position/position_manager.py, lifecycle.py | check_positions, CriticalRiskKernel, 승격/이관 |
| Risk Manager | execution/risk_manager.py, risk/risk_manager.py, risk/critical_risk_kernel.py | pre_trade_check, 일일손실한도 |
| Strategy Engine | strategy/strategy_engine.py | generate_signals, register_strategy |
| Order Executor | execution/order_executor.py | execute_buy, execute_sell, FundPool 연동 |
| V4 Trade Bridge | trading/v4_trade_bridge.py | process_signal, execute_sell_for_position, check_stop_loss/take_profit/trailing_stop |
| V4 Pipeline Orchestrator | trading/v4_pipeline_orchestrator.py | run_desk*_cycle, run_card_pipeline, split_engine 연동, check_all_positions |
| Adaptive Engine | adaptive/engine.py, fund_rebalancer.py, regime_weight.py, param_optimizer.py, weekly_scoring.py | |
| Regime Detector | market/regime_detector.py | RegimeIndicators, 5단계 레짐 |
| Market Brain / Chief Analyst | brain/chief_analyst.py | |
| Account Sync Manager | trading/account_sync_manager.py | sync_balance, reconcile_positions, save_snapshot |
| Token Manager | core/token_manager.py | get_token, Redis, 만료 1시간 전 갱신 |

### A-3. DB 현황

- **v4_* 테이블:** 80개 이상 (파티션 제외 시 약 60개). v4_ohlcv_minute_2025_01 등 월별 파티션 포함.
- **strategy_cards:** 65건. desk_id별: 1(10), 2(16), 3(12), 4(9), 5(10), NULL(8).
- **strategy_cards 스키마:** card_id, user_id, account_id, strategy_name, strategy_type, strategy_params, allocated_amount, max_stocks, is_live, is_active, desk_id, entry_rules, exit_rules, risk_params, **buy_phases, sell_phases, promotion_rules, demotion_rules**, backtest_compatible, priority, version 등. (split_transfer_rules 컬럼 없음 — 코드는 DESK_CONFIGS 하드코딩)
- **v4_positions 컬럼:** id, user_id, ticker, quantity, entry_price, status, desk_id, peak_price, stop_loss_price, trailing_pct, target_pct, max_hold_days, entry_date, reservation_id, exit_*, created_at, updated_at, **current_price, pnl_pct, price_updated_at, account_id, card_id, split_phase, remaining_qty, original_desk_id, buy_phase, signal_id** (분할/이관 관련 컬럼 있음).
- **v4_desk_fund:** 5행 (DESK1~5). allocation_pct, allocated_amount, used_amount, available_amount, max_positions, current_positions, daily_loss_limit 등.
- **v4_fund_pool_snapshot:** 최근 1건 예시 (total_capital, available, reserved, invested, desk1~5_used, fund_mode).
- **v4_desk_strategy_mapping:** DESK별 card_id 매핑 다수.

### A-4. buy_phases / sell_phases / promotion_rules

- strategy_cards에 buy_phases, sell_phases, promotion_rules, demotion_rules JSONB 존재. 실행 로직은 v4_pipeline_orchestrator + split_transfer_engine (DESK별 DESK_CONFIGS로 phase 비율·승격/강등 규칙 적용).

### A-5. 서비스·크론

- **kis-v41-api:** active (8003)  
- **kis-v41-scheduler, kis-v41-monitor, kis-v41-position-monitor:** active  
- **kis-v41-minute-collector:** inactive  
- **go100.service, go100-frontend.service:** active (8002 등)  
- **크론:** VKOSPI, 토큰갱신, 디스크, DB백업, 알림, stock_universe, 일봉, index_daily, market_investor, 분봉배치, 업종, 레거시 DROP 등.

### A-6. Git

- 2026-02-13 이후 커밋 다수: 토큰 매니저, GO100 수정, CONTEXT v4_positions ID, 분봉 수집, 트레이드 브릿지 수정 등.

---

## 2. Phase B 분석 테이블 (요약)

### [테이블 1] 기획 20개 모듈 구현 현황

- **완료 15개:** Orchestrator, Regime Detector, Market Calendar, Chief Analyst, Fund Commander, Market Brain, Strategy Engine, Risk 2계층, Order Executor, Fund Pool+Reservation, Position Manager, Adaptive Engine, Data Provider+Price Poller, 운영지표+알림.
- **부분 1개:** Data Quality Tracker (INFRA-B).
- **미착수 1개:** Fault Injection (INFRA-C).

### [테이블 2] 기획에 없는 추가 기능

- Split Transfer Engine, Token Manager, GO100 공유, Fund Pool Snapshot, Account Sync Manager, buy_phases/sell_phases, promotion_rules/demotion_rules, V4 Trade Bridge, V4 Pipeline Orchestrator, Desk Recommend API, v4_position_transfers. (NXT는 코드 상 미사용.)

### [테이블 3] DB 테이블 기획 vs 현행

- 기획 언급 테이블은 모두 현행 존재. v4_position_transfers, v4_desk_strategy_mapping, v4_account_holdings, v4_account_sync_log, v4_api_tokens 등 기획 후 추가. v4_positions에 split_phase, remaining_qty, original_desk_id, buy_phase, signal_id 등 컬럼 추가됨.

---

## 3. 핵심 발견사항

1. **분할매매·이관:** split_transfer_engine.py가 단일 엔진으로 분할매수/매도와 DESK 승격·강등 통합. strategy_cards의 buy_phases/sell_phases/promotion_rules/demotion_rules와 연동되며, DESK별 상세 규칙은 코드 내 DESK_CONFIGS에도 정의.
2. **strategy_cards 65건:** CONTEXT 62건에서 증가. desk_id NULL 8건 존재.
3. **v4_positions:** 분할·이관용 컬럼(split_phase, remaining_qty, original_desk_id, buy_phase, signal_id) 보유.
4. **Token Manager:** Redis 기반, 만료 1시간 전 갱신 규칙 문서화됨.
5. **NXT:** order_executor에 NXT 전용 파라미터 미노출. KRX 기준 현행.
6. **코드/DB/서비스 변경 없음:** 본 작업은 읽기전용 스캔만 수행.

---

## 4. 산출물

- **project-docs:** `kis-autotrade-v4/architecture/v41-architecture-v1.2.md`, `architecture/README.md` (v1.2 행 추가).
- **kis-autotrade-v4:** `report/v41/ARCHITECTURE-FULL-SCAN-V1.2-20260223.md` (본 보고서).

---

**문서 끝**
