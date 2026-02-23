# KIS AutoTrade V4.1 — 시스템 아키텍처 문서 v1.2

```
================================================================
KIS AutoTrade V4.1 자동매매 시스템 — 아키텍처 문서 v1.2
================================================================
문서 버전: 1.2
작성일: 2026-02-23
작성자: Cursor AI + Claude (ARCHITECTURE-FULL-SCAN-V1.2, CEO 지시)
상태: 현행 운영 기준 (phase-2c-command-center 브랜치)
기반: 기획 원본(ORIGINAL-20260213) 전수조사 + v1.1 업데이트
================================================================
```

---

## 1. CHANGELOG (v1.1 → v1.2)

| 날짜 | 변경 항목 | 사유 |
|------|-----------|------|
| 2026-02-23 | 기획 원본 대비 20개 모듈 구현 현황 테이블 추가 | CEO 지시 전수조사 |
| 2026-02-23 | 기획 이후 추가된 기능 목록(테이블 2) 추가 | 분할매매/이관/NXT 등 정리 |
| 2026-02-23 | DB 테이블 기획 vs 현행 매핑(테이블 3) 추가 | v4_* 테이블 전수 반영 |
| 2026-02-23 | 매매 실행 흐름: buy_phases / sell_phases / 승격·강등 흐름도 | 분할매매·이관 명시 |
| 2026-02-23 | Token Manager, Account Sync, Fund Pool Snapshot 상세 | v1.1 보완 |
| 2026-02-23 | strategy_cards 65건, DESK별 카드 수, v4_desk_fund 현황 | DB 스캔 반영 |
| 2026-02-23 | 서비스·크론·API 엔드포인트 현행화 | kis-v41-*, go100, 크론 목록 |

---

## 2. 기획 원본(ORIGINAL-20260213) 대비 구현 현황

### [테이블 1] 기획 20개 LAYER/INFRA 모듈 구현 현황

| # | LAYER | 기획명 | 구현 상태 | 파일 경로 | 비고 |
|---|-------|--------|-----------|-----------|------|
| 0 | LAYER 0 | System Orchestrator | ✅ | backend/app/services/orchestrator/, system/orchestrator.py, trading/v4_pipeline_orchestrator.py | 상태전이·사이클·복구 |
| 1-A | LAYER 1-A | Market Regime Detector | ✅ | backend/app/services/market/regime_detector.py | 5단계 레짐, v4_market_regime_daily |
| 1-B | LAYER 1-B | Market Calendar | ✅ | backend/app/services/market/calendar_service.py | v4_market_calendar |
| 2-A | LAYER 2-A | Chief Analyst | ✅ | backend/app/services/brain/chief_analyst.py | 유니버스·CLASS |
| 2-B | LAYER 2-B | Fund Commander | ✅ | backend/app/services/brain/fund_commander.py, execution/fund_commander.py | 베팅·레짐반영 |
| 3 | LAYER 3 | Market Brain / 5 DESK | ✅ | strategy/desk1~5_commander.py, v4_pipeline_orchestrator run_desk*_cycle | DESK1~5 |
| 4 | LAYER 4 | Strategy Engine | ✅ | backend/app/services/strategy/strategy_engine.py, strategies/*.py | 시그널 생성·필터 |
| 5-A | LAYER 5-A | Risk Manager 2계층 | ✅ | execution/risk_manager.py, risk/risk_manager.py, risk/critical_risk_kernel.py | pre_trade·일일한도 |
| 5-B | LAYER 5-B | Order Executor | ✅ | backend/app/services/execution/order_executor.py, trading/v4_order_executor.py | KIS 주문·체결 |
| 5-C | LAYER 5-C | Fund Pool + Reservation | ✅ | execution/fund_pool.py, reservation.py, fund_pool_sync.py | DB=SoT·예약금 |
| 6 | LAYER 6 | Position Manager / Lifecycle | ✅ | position/position_manager.py, lifecycle.py, sell_failure_handler.py | 청산·승격·이관 |
| 7 | LAYER 7 | Adaptive Engine | ✅ | adaptive/engine.py, fund_rebalancer.py, regime_weight.py, param_optimizer.py, weekly_scoring.py | 학습·재배분 |
| 8 | INFRA-A | Data Provider + Price Poller | ✅ | data_pipeline/*.py, infra/price_poller.py, data/live_provider.py | 시세·분봉 |
| 9 | INFRA-B | Data Quality Tracker | 🔧 | infra/data_monitor.py, metrics_collector.py | 품질 등급 부분 |
| 10 | INFRA-C | Fault Injection | ❌ | — | 기획만, 미구현 |
| 11 | INFRA-D | 운영 지표 + 알림 | ✅ | monitoring/*.py, notification/*.py, v4_alert_api.py | heartbeat·알림 |

**구현률 요약:** 완료 15개 / 부분 1개(INFRA-B) / 미착수 1개(INFRA-C Fault Injection)

---

## 3. 기획 이후 추가된 기능 (신규)

### [테이블 2] 기획에 없었지만 추가된 기능

| # | 기능명 | 설명 | 파일 경로 | 비고 |
|---|--------|------|-----------|------|
| 1 | Split Transfer Engine | 분할매수·분할매도 + DESK 간 승격·강등 통합 엔진 | backend/app/services/trading/split_transfer_engine.py | CUR-20260220-A STEP2 |
| 2 | Token Manager | KIS/키움 토큰 Redis 캐시, 만료 1시간 전 선제 갱신 | backend/app/core/token_manager.py | v4_api_tokens 연동 |
| 3 | NXT 거래소 지원 | (코드 상 NXT 전용 파라미터 미노출; order_executor는 KRX 기준) | — | 확장 대비 |
| 4 | GO100 공유 아키텍처 | 동일 서버/DB에서 GO100(백억이)·V4.1 API 공존 | backend/app/services/go100/, main.py include_router | go100.service:8002 |
| 5 | Fund Pool Snapshot | 자금 풀 스냅샷 기록·조회 | v4_fund_pool_snapshot, adaptive/fund_rebalancer.py, regime_weight.py | INSERT·대시보드 |
| 6 | Account Sync Manager | 계좌 보유종목·잔고 동기화, KIS 실잔고 vs DB 대조 | backend/app/services/trading/account_sync_manager.py | v4_account_holdings |
| 7 | buy_phases / sell_phases | 단계별 매수·매도(카드별 JSONB) | strategy_cards.buy_phases, sell_phases, v4_pipeline_orchestrator | DESK별 phase 실행 |
| 8 | promotion_rules / demotion_rules | DESK 승격·강등 규칙(카드별 JSONB) | strategy_cards, split_transfer_engine.py DEMOTION_* | 3회 강등 시 전량청산 등 |
| 9 | V4 Trade Bridge | 시그널→포지션/체결 기록, 손절·익절·트레일링 체크 | backend/app/services/trading/v4_trade_bridge.py | v4_positions, v4_trades |
| 10 | V4 Pipeline Orchestrator | DESK별 사이클·카드 파이프라인·분할매매/이관 오케스트레이션 | backend/app/services/trading/v4_pipeline_orchestrator.py | split_engine 연동 |
| 11 | Desk Recommend API | 파이프라인 요약·시그널·타임라인·DESK 요약 | backend/app/api/v4_desk_recommend.py | /api/v4/desk-recommend/* |
| 12 | v4_position_transfers | 포지션 이관(승격/강등) 이력 | DB 테이블 v4_position_transfers | split_transfer_engine 기록 |

### 상세 설명 (요약)

- **분할매매 (Split Transfer Engine):** DESK별 buy_phases/sell_phases 비율에 따라 분할매수·분할매도 실행. phase2 잔량은 상위 DESK 승격 또는 시장가 매도.
- **DESK 간 이관/승격/강등:** promotion_rules/demotion_rules 기반. 강등 3회 초과 시 전량 청산, 강등 후 24시간 재승격 금지(핑퐁 방지).
- **buy_phases / sell_phases:** strategy_cards JSONB로 단계별 비율·조건 정의. 오케스트레이터가 split_engine과 연동해 실행.
- **Token Manager:** Redis 캐시, 만료 1시간 전 갱신 규칙. get_token / _issue_token_kis / _save_token.
- **NXT 거래소:** 현재 order_executor는 KRX 기준; NXT 전용 파라미터는 코드에서 미사용. 확장 시 market_div 등 추가 예정.
- **GO100 공유:** go100.service(8002), kis-v41-api(8003). Nginx에서 /api/v4/* 등 라우팅. 동일 venv/DB.
- **Fund Pool Snapshot:** v4_fund_pool_snapshot에 total_capital, available, reserved, invested, desk*_used 등 기록. FundRebalancer·RegimeWeight에서 INSERT.
- **Account Sync Manager:** fetch_account_balance, reconcile_positions, save_snapshot, sync_balance. v4_account_holdings, v4_account_sync_log.

---

## 4. 서비스 개요 (v1.1 업데이트)

V4.1은 KIS(한국투자증권) API 기반 한국 주식 자동매매 엔진이다. 5개 DESK(전략 단위)가 독립·연계 운영되며, 각 DESK는 고유 투자 스타일(초단기/데일리/단기스윙/중기스윙/장기스윙)에 맞는 전략 카드를 실행한다. 분할매매·DESK 간 승격·강등을 지원한다.

- **프로젝트 경로:** /root/kis-autotrade-v4  
- **운영 서버:** 211.188.51.113 (Ubuntu)  
- **브랜치:** phase-2c-command-center  
- **DB:** PostgreSQL 16 / kisautotrade  
- **전략 카드:** 65건 (DESK1: 10, DESK2: 16, DESK3: 12, DESK4: 9, DESK5: 10, desk_id NULL: 8)

---

## 5. 시스템 전체 구조 (ASCII 다이어그램)

```
┌─────────────────────────────────────────────────────────────────┐
│ 외부 데이터 소스                                                  │
│ KIS API (실시간 시세, 주문, 계좌)  pykrx (일봉)                   │
│ 한국거래소 (업종/종목)  기재부 (공휴일 캘린더)                    │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 데이터 수집 파이프라인 (크론/타이머)                              │
│ 일봉/분봉/투자자/업종/지수/VKOSPI/stock_universe                  │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ PostgreSQL kisautotrade (v4_* + go100_* + 레거시)                │
└────────────────────────┬────────────────────────────────────────┘
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌──────────────────┐  ┌──────────────┐
│ 스케줄러    │  │ V4 Pipeline      │  │ 모니터       │
│ kis-v41-   │  │ Orchestrator     │  │ kis-v41-    │
│ scheduler  │  │ + SplitTransfer   │  │ monitor     │
└─────────────┘  │ Engine           │  └──────────────┘
                 │ Strategy→Risk→   │
                 │ Order→Position   │
                 └──────────────────┘
```

---

## 6. DESK 구조 (현재 카드 수량/라이브 현황)

| DESK | 역할 | 카드 수 | 비고 |
|------|------|---------|------|
| DESK1 | 초단타/스캘핑 | 10 | 분봉 기반 |
| DESK2 | 데일리 | 16 | 1~5일 |
| DESK3 | 단기스윙 | 12 | 5~20일 |
| DESK4 | 중기스윙 | 9 | 20~60일 |
| DESK5 | 장기스윙 | 10 | 60일+ |
| (미배정) | — | 8 | desk_id NULL |

**v4_desk_fund (예시):** DESK1~5별 allocation_pct, allocated_amount, used_amount, available_amount, max_positions, current_positions, daily_loss_limit 등 관리.

---

## 7. 매매 실행 흐름 (분할매매/이관 포함)

### buy_phases 흐름

1. 오케스트레이터가 활성 카드 조회 → Strategy Engine 시그널 생성  
2. 시그널별 Risk·FundPool 확인 → Order Executor 매수  
3. **카드에 buy_phases 있으면:** phase 1 비율만 매수 → phase 2는 조건(시간/확인) 충족 시 추가 매수 (split_transfer_engine 또는 오케스트레이터 로직)  
4. 체결 → V4TradeBridge로 v4_positions INSERT, reservation 정리  

### sell_phases 흐름

1. check_all_positions → SplitTransferEngine.evaluate_position()  
2. phase별 목표가·트레일링·최대손실 판정 → SPLIT_SELL / TRANSFER_UP / TRAILING_SELL 등  
3. phase1 비율 매도 체결 후, phase2 잔량은 **승격 대상 DESK로 이관** 또는 시장가 매도  
4. execute_partial_demotion (강등 시) → 일부만 하위 DESK로, 나머지 유지  

### 승격/강등 흐름

1. **승격:** promotion_criteria 충족 시 SplitTransferEngine.execute_transfer() → lifecycle 포지션 이관(desk_id·파라미터 갱신), v4_position_transfers INSERT  
2. **강등:** demotion_criteria 충족 시 execute_partial_demotion 또는 전량 청산. 강등 3회 초과 시 FORCE_EXIT_STOCK. 강등 후 24시간 재승격 금지(can_promote_after_demotion).  
3. 스케줄러: 09:30 CLASS-A→DESK3 이관 체크, 15:00 DESK3 강등, 16:00 DESK4/DESK5 강등·D→E/E→F 승격 체크  

---

## 8. 데이터베이스 ([테이블 3] 기획 vs 현행)

### [테이블 3] DB 테이블 기획 vs 현행 매핑

| 테이블명 | 기획 | 현행 | 비고 |
|----------|------|------|------|
| v4_system_state_log | ✅ | ✅ | 상태 전이 이력 |
| v4_system_heartbeat | ✅ | ✅ | heartbeat·운영지표 |
| v4_market_regime_daily | ✅ | ✅ | 레짐 일별 |
| v4_market_calendar | ✅ | ✅ | 개장일·이벤트 |
| v4_ohlcv_minute | ✅ | ✅ | 분봉(파티션) |
| v4_investor_daily | ✅ | ✅ | 투자자 동향 |
| v4_vkospi_daily | ✅ | ✅ | VKOSPI |
| v4_positions | ✅ | ✅ | split_phase, remaining_qty, original_desk_id, buy_phase, signal_id 등 컬럼 추가 |
| v4_trades | ✅ | ✅ | 체결 |
| v4_orders / v4_order_requests | ✅ | ✅ | 주문·멱등성 |
| v4_signals | ✅ | ✅ | 시그널 |
| v4_desk_fund | ✅ | ✅ | DESK별 자금 |
| v4_fund_pool_snapshot | ✅ | ✅ | 자금 풀 스냅샷 |
| v4_position_transfers | — | ✅ | 승격/강등 이관 이력 (기획 후 추가) |
| v4_desk_strategy_mapping | — | ✅ | DESK-카드 매핑 (기획 후 추가) |
| v4_reservations | ✅ | ✅ | 예약금 상태머신 |
| v4_universe_version | ✅ | ✅ | 유니버스 버전 |
| v4_account_holdings, v4_account_sync_log | — | ✅ | 계좌 동기화 |
| v4_api_tokens | — | ✅ | 토큰 캐시(또는 Redis) |
| 기타 v4_* (백테스트·알림·리포트·테마 등) | 부분 | ✅ | 80개 이상 v4_* 테이블 존재 |

---

## 9. 핵심 서비스 모듈 (실제 파일 트리)

```
backend/app/services/
├── trading/
│   ├── split_transfer_engine.py   # 분할매매·승격·강등
│   ├── v4_pipeline_orchestrator.py
│   ├── v4_trade_bridge.py
│   ├── v4_order_executor.py
│   ├── v4_risk_manager.py
│   ├── account_sync_manager.py
│   └── ...
├── execution/
│   ├── order_executor.py
│   ├── fund_pool.py
│   ├── fund_commander.py
│   ├── risk_manager.py
│   ├── reservation.py
│   └── fund_pool_sync.py
├── position/
│   ├── position_manager.py
│   ├── lifecycle.py
│   └── sell_failure_handler.py
├── strategy/
│   ├── strategy_engine.py
│   └── strategies/ (desk2~5 전략)
├── brain/
│   ├── chief_analyst.py
│   └── fund_commander.py
├── market/
│   ├── regime_detector.py
│   └── calendar_service.py
├── adaptive/
│   ├── engine.py
│   ├── fund_rebalancer.py
│   ├── regime_weight.py
│   └── param_optimizer.py
├── orchestrator/
├── infra/ (price_poller, data_monitor 등)
├── monitoring/
├── notification/
└── ...
```

---

## 10. 토큰 관리

- **위치:** backend/app/core/token_manager.py  
- **역할:** Redis 캐시 기반 KIS/키움 API 토큰. get_token 시 유효하면 반환, 만료 1시간 전이면 선제 갱신(_needs_renewal). _issue_token_kis / _save_token.  
- **규칙:** CEO 지시 만료 1시간 전 갱신. v4_api_tokens 또는 Redis 키 저장.

---

## 11. NXT/KRX 시장 운영

- **현행:** 주문 실행은 KRX 기준. order_executor에는 NXT 전용 파라미터(market_div 등) 미노출.  
- **확장:** NXT 거래소 지원 시 market_div·exchange 등 파라미터 추가 예정.

---

## 12. systemd / 크론

| 서비스 | 상태 | 역할 |
|--------|------|------|
| kis-v41-api | active | KIS V4.1 API (8003) |
| kis-v41-scheduler | active | 매매 스케줄 |
| kis-v41-monitor | active | 포지션 모니터 |
| kis-v41-position-monitor | active | 포지션 리스크 |
| kis-v41-minute-collector | inactive | 분봉 수집(월요일 장전 등) |
| go100.service | active | GO100 API (8002) |
| go100-frontend.service | active | Next.js 프론트 |

**크론 요약:** VKOSPI 18:30, 토큰 갱신 14:30, 디스크 6h, DB 백업 03:00, 알림 5min/30min, stock_universe 19:00, 일봉 18:00, index_daily 18:30, market_investor 18:40, 분봉 배치 16:00·토 02:00, 업종 토 03:00, 레거시 DROP 일 04:00.

---

## 13. API 엔드포인트

- **/api/v4/** — system, trading, backtest, dashboard, chart, orders, emergency, liquidation, ai-trading, admin, auth, kis, settings, data-pipeline, reports, notifications, social-auth, desk-recommend (pipeline-summary, signals, timeline, desk-summary)  
- **/api/go100/** — strategy-cards, portfolios, backtest, ai, paper-trading, live-trading, scheduler, risk, optimizer  
- **/api/v1/** — dashboard, auth, account, monitoring, backtest, report 등  
- **WebSocket:** /ws/live-trade, /ws/ticks  

---

## 14. 환경변수

v1.1과 동일. APP_*, DATABASE_*, REDIS_*, JWT_*, ENCRYPTION_*, KIS_*, KIWOOM_*, RATE_LIMIT_*, LLM_*, SMTP_*, DRY_RUN, TRADING_CONFIG_ID, ALLOWED_IPS 등. (.env 커밋 금지)

---

## 15. 알려진 이슈 + 기술 부채

- **Fault Injection (INFRA-C):** 기획만 있고 미구현.  
- **Data Quality 등급:** INFRA-B 부분 구현.  
- **strategy_cards:** 65건(CONTEXT 62→65). desk_id NULL 8건 처리 정책 확인 필요.  
- **NXT:** 코드 상 미사용, 확장 시 반영.  
- **venv vs .venv:** go100·크론은 venv 사용.  
- **레거시 테이블 DROP:** 일요일 04:00 크론 등록됨.

---

## 16. 문서 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0 | 2026-02-20 | 초판 |
| 1.1 | 2026-02-21 | V4.1 전용 분리, SECIND-V2, strategy_cards 59건, 서비스 상태 |
| 1.2 | 2026-02-23 | 기획 원본 전수조사, 테이블 1·2·3, 분할매매/이관/NXT/Token/Fund Snapshot/Account Sync, strategy_cards 65건, DESK·서비스·크론 현행화 |

================================================================
문서 끝 (v41-architecture-v1.2.md)
================================================================
