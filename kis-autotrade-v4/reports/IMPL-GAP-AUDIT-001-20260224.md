# IMPL-GAP-AUDIT-001: V4.1 기획 vs 실제 구현 갭 전수 감사

**작업ID:** IMPL-GAP-AUDIT-001  
**작업명:** V4.1 기획 vs 실제 구현 갭 전수 감사  
**일자:** 2026-02-24 KST  
**성격:** 읽기 전용 분석 (코드 수정·서비스 재시작 없음)  
**기준 문서:**  
- `v41-adaptive-architecture-spec.md`  
- `v41-development-plan-spec.md`  
- `v41-architecture-v1.2.md`  

---

## 1. LAYER별 구현 상태표

| LAYER | 기획 항목 | 파일/경로 존재 | 코드 완성도 | 미구현/부분구현 사유 |
|-------|-----------|----------------|-------------|----------------------|
| **LAYER 0** | System Orchestrator (상태머신, Invariants, 60초 사이클) | ✅ `backend/app/services/trading/v4_pipeline_orchestrator.py` (29개 함수) | ✅ 구현완료 | DESK별 cycle 기반 동작. 상태 전이 불변조건(Invariants) 코드 레벨 강제·PRE_MARKET/READY/TRADING 명시적 상태명은 미확인. |
| **LAYER 1-A** | Market Regime Detector (5대 레짐, 히스테리시스 상향3일/하향2일) | ✅ `backend/app/services/market/regime_detector.py` | ✅ 구현완료 | `hysteresis_up_count`, `hysteresis_down_count`, `pending_regime` DB 연동 및 `_get_hysteresis_counters`, `_save_hysteresis_counters`, `HYSTERESIS_UP_DAYS`/`HYSTERESIS_DOWN_DAYS` 로직 존재. |
| **LAYER 1-B** | Market Calendar (CalendarEventType, 합산규칙, is_stock_restricted) | 🔧 부분구현 | 🔧 부분 | **파일:** `calendar_service.py` 존재, `calendar_manager.py` 없음. **Enum:** 기획서 `CalendarEventType` → 현행 `EVENT_TYPES` dict. **미존재:** `calendar_generator.py`, `calendar_queries.py`. v4_market_calendar·MarketCalendar 모델·당일 조정값 산출 구현됨. |
| **LAYER 2-A** | Chief Analyst (today_universe, 버전화, 5대 스코어러) | 🔧 부분구현 | 🔧 부분 | ChiefAnalyst(`chief_analyst.py`)·today_universe·inputs_hash 존재. **5대 스코어러:** 기획 `scoring/supply_demand.py`, `sector.py`, `theme.py`, `volume.py`, `technical.py`, `composite_scorer.py` **별도 모듈 없음** — 수급/업종/테마/거래량/기술적 점수는 `desk1/2/3_commander` 및 data provider(`get_supply_demand` 등)에 분산. v4_scoring_weights(supply_demand_w 등) 컬럼 존재. |
| **LAYER 2-B** | Fund Commander | ✅ 구현완료 | ✅ 구현완료 | `brain/fund_commander.py`, `execution/fund_commander.py`, fund_service, v4_desk_fund, v4_fund_pool_snapshot, v4_reservations 사용. |
| **LAYER 3** | Market Brain / DESK configs | ✅ 구현완료 | ✅ 구현완료 | `DESK_CONFIGS`, `desk_id` 사용: split_transfer_engine, v4_pipeline_orchestrator, v4_risk_manager 등 다수 파일. |
| **LAYER 4** | Strategy Engine (idempotency_key, CLASS) | ✅ 구현완료 | ✅ 구현완료 | `backend/app/services/strategy/strategy_engine.py` 및 `strategies/` 다수 전략 파일 존재. |
| **LAYER 5** | Risk Manager 2계층 (CriticalRiskKernel + Full) | ✅ 구현완료 | ✅ 구현완료 | `CriticalRiskKernel`: `backend/app/services/risk/critical_risk_kernel.py`. `risk_manager.py`가 critical_kernel 주입·사용. `v4_risk_manager.py`(trading)는 DESK별 자금/한도 담당, CRK는 position/lifecycle·factory에서 사용. |
| **LAYER 6** | Position Manager + fallback, SELL_FAILED 재시도 | ✅ 구현완료 | ✅ 구현완료 | **position_manager:** `position/position_manager.py`(모니터링·청산우선순위). **lifecycle:** `position/lifecycle.py`에 CriticalRiskKernel 내장, `fallback_sell`, SELL_FAILED 단계적 재시도(지정가→IOC→시장가), `_mark_position_sell_failed` 구현. |
| **LAYER 7** | Adaptive Engine (weekly_scoring, fund_rebalancer, param_optimizer, regime_weight) | 🔧 부분구현 | 🔧 부분 | **파일 모두 존재:** `adaptive/weekly_scoring.py`, `fund_rebalancer.py`, `param_optimizer.py`, `regime_weight.py`, `engine.py`. v4_scoring_weights가 유니버스용이라 주간 전략 스코어링 가중치는 기본값 반환 등 연동 완전성은 추가 검증 필요. |
| **INFRA** | Data Quality Tracker | 🔧 부분구현 | 🔧 부분 | DataQuality 스키마·get_data_quality (base/live/backtest_provider) 존재. 전용 `data_quality_tracker` 모듈·운영 4종 지표 집계는 미확인. |
| **INFRA** | Fault Injection | ❌ 미구현 | ❌ | 경량 Fault Injection 도입 스펙 대비 전용 모듈/스크립트 없음. |
| **Phase A** | FutureDataGuard, Walk-Forward, Ablation | ❌ 미구현 | ❌ | `FutureDataGuard` 데코레이터·`walk_forward`·`ablation` 검색 시 백엔드/스크립트 전역 매칭 없음. |

---

## 2. Phase A Task별 구현 상태

| Task | 기획 내용 | 구현 상태 | 비고 |
|------|-----------|-----------|------|
| **A-2** | 백테스트 데이터 파이프라인, FutureDataGuard, OHLCV 지표 사전 계산 | 🔧 부분 | FutureDataGuard 미구현. OHLCV/지표 계산은 signal_generator·backtest_provider 등에 분산 존재. |
| **A-3** | 5대 스코어링 엔진 (base_scorer, supply_demand, sector, theme, volume, technical, composite) | 🔧 부분 | 5개 독립 스코어러 파일 없음. 수급/업종/테마/거래량/기술적 점수는 commander·provider에 분산. |
| **A-4** | CLASS-A 모멘텀 추종 (조건 AND, 손익비 1.2 미만 거부) | ✅ | strategy_engine·CLASS 필터·전략 카드 기반 구현. |
| **A-5** | 포지션 관리 + 손절/익절/Trailing, Re-Entry Guard | ✅ | position_manager·lifecycle에 청산 우선순위·CRK·fallback·SELL_FAILED 재시도 구현. |
| **A-6** | 백테스트 엔진 + 성과 측정 (기대값, 승률, Avg_Win/Loss, RRR, PF, CAGR, MDD, Calmar, Sharpe 등) | 🔧 부분 | **있음:** report_generator: total_return_pct, annualized_return(CAGR 유사), max_drawdown_pct(MDD), sharpe_ratio, profit_factor, avg_win_pct, avg_loss_pct, 연속승패. **없음:** Calmar, 기대값(E) 명시 산출, RRR, Kelly. backtest_engine_v2.py 내 직접 지표 계산은 미확인. |
| **A-7** | main_backtest 일괄 실행 (3년 BT → Walk-Forward → Ablation → 판정) | ❌ | Walk-Forward·Ablation 스크립트/진입점 없음. |

---

## 3. 데이터 갭 (스코어링 필요 데이터 vs 현재 DB)

| 데이터 용도 | 기획/필요 테이블 | 현재 상태 | 비고 |
|-------------|------------------|-----------|------|
| 수급 (supply_demand) | v4_investor_daily | ✅ 170,760행 | 사용 가능. |
| 업종 (sector) | v4_sector_daily, v4_sector_price, v4_stock_sector | ✅ v4_sector_daily 14,754행, v4_stock_sector 4,225행 / ⚠️ v4_sector_price **0행** | v4_sector_price 비어 있음. |
| 테마 (theme) | v4_theme_activity, v4_theme_stocks (기획서 명칭) | ❌ **테이블 없음** (v4_theme_activity, v4_theme_stocks) | 실제 존재: v4_theme_master, v4_theme_stock, v4_theme_activity_daily, v4_theme_daily 등, **전부 0행**. |
| 거래량 (volume) | v4_ohlcv_minute | ✅ 39,295,643행 | 사용 가능. |
| 기술적 (technical) | ohlcv_daily, scalping_features_daily | ✅ ohlcv_daily 2,600,387행 / scalping_features_daily 45행 | scalping_features_daily 행수 적음. |

**요약:** 수급·일봉·분봉 데이터는 충분. 업종 가격(v4_sector_price) 0행, 테마 계열 테이블명 불일치·전부 0행으로 테마/업종 가격 기반 스코어링은 데이터 보강 필요.

---

## 4. 구현 갭 해소 우선순위 제안

(수익 영향도 × 구현 난이도 고려)

| 순위 | 갭 항목 | 수익 영향도 | 구현 난이도 | 제안 |
|------|---------|-------------|-------------|------|
| P1 | **Phase A-6 보강** (Calmar, 기대값 E, RRR, Kelly in report/summary) | 높음 | 낮음 | 백테스트 판정 및 모니터링에 직결. report_generator·v4_backtest_summary 확장. |
| P2 | **FutureDataGuard** (백테스트 시 sim_date 이후 데이터 차단) | 높음 | 중간 | 백테스트 결과 신뢰도 직결. backtest_provider 또는 데코레이터 도입. |
| P3 | **5대 스코어러 모듈화** (supply_demand, sector, theme, volume, technical + composite) | 중간 | 중간 | Chief Analyst·DESK 스코어 일원화, 재사용 및 테스트 용이. |
| P4 | **Walk-Forward + Ablation** (A-7 일괄 실행) | 높음 | 높음 | 기획서 통과 기준(E>0, Calmar>1.5 등) 검증 경로. |
| P5 | **Market Calendar 완성** (calendar_generator, calendar_queries, Enum, Orchestrator 연동) | 중간 | 중간 | PRE_MARKET calendar_checked 등 연동 명세 확인 후 구현. |
| P6 | **테마/업종 데이터 채우기** (v4_theme_*·v4_sector_price 수집) | 중간 | 데이터/파이프라인 | 스코어링 품질 향상. |
| P7 | **경량 Fault Injection** | 낮음 | 중간 | Phase 5 스펙. 운영 안정성 검증용. |
| P8 | **Data Quality Tracker 전용 모듈·운영 4종 지표** | 중간 | 중간 | 기획서 “운영 최소 지표 4종” 명세에 맞춰 구현. |

---

## 5. 결론

- **기획은 탄탄하다.** 아키텍처 기술서·개발 실전 기획서에 정의된 LAYER 0~7·INFRA 대부분이 파일/코드 수준으로 존재하며, 레짐 히스테리시스, CRK 2계층, Position Lifecycle(fallback·SELL_FAILED 재시도), Adaptive(weekly_scoring·fund_rebalancer·param_optimizer·regime_weight) 등 핵심 요소가 구현되어 있다.
- **구현 갭은 다음이 핵심이다.**  
  - **Phase A:** FutureDataGuard·Walk-Forward·Ablation 미구현, A-6 지표(Calmar·기대값·RRR·Kelly) 미보강.  
  - **스코어링:** 5대 스코어러 독립 모듈 부재(commander/provider 분산).  
  - **캘린더:** calendar_generator·calendar_queries·Enum·Orchestrator 연동 불완전.  
  - **데이터:** 테마·업종 가격(v4_sector_price·v4_theme_*) 0행 또는 테이블명 불일치.  
  - **INFRA:** Fault Injection 미구현, Data Quality Tracker 전용 모듈·운영 4종 미확인.
- **갭 N개 해소 시:** 위 P1~P8 순으로 N개 항목(최소 P1~P4)을 해소하면 기획 의도대로 “수익 극대화 입증 프레임워크” 및 백테스트 판정·실전 연동이 가능해진다.

**갭 항목 수 요약:** 전수 감사 기준 **약 12~15개** 세부 갭(Phase A 4개, 스코어링 1개, 캘린더 2~3개, 데이터 2개, INFRA 2개). 이 중 **4~6개 핵심(P1~P4 위주) 해소**로 기획 의도 달성 가능.

---

*문서 끝 (IMPL-GAP-AUDIT-001-20260224)*
