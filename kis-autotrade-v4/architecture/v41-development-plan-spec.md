# KIS AutoTrade V4.1 — 개발 실전 기획서

**문서 목적:** Phase 2-B ~ Phase 6 전체를 개발 관점에서 "무엇을 어떤 순서로, 어떤 구조로, 어떤 파일에" 만들 것인가  
**작성일:** 2026-02-13  
**기준:** V4.1 아키텍처 기술서 + 모듈별 세부 역할 기획서

---

## 목차

1. [현재 프로젝트 구조 기준선](#0-현재-프로젝트-구조-기준선)
2. [Phase 2-B: Market Calendar](#1-phase-2-b-market-calendar)
3. [Phase 2-C: Command Center](#2-phase-2-c-command-center)
4. [Phase 2-D: DESK 2/3 + 스코어링](#3-phase-2-d-desk-23--스코어링)
5. [Phase 3 ~ 6 요약 및 역할별 기획](#phase-3--6-요약)
6. [수익 극대화 입증 프레임워크](#수익-입증-프레임워크)
7. [Phase A: 최초 기대값 입증 (Task A-2 ~ A-7)](#phase-a-task-a-2--a-7)

---

## 0. 현재 프로젝트 구조 기준선

Phase 1 완료 + Phase 2-A 완료 기준 디렉토리 구조:

```
kis_autotrade/
├── main.py
├── config/           (settings, constants, critical_risk_config.yaml)
├── core/              (orchestrator, fund_pool, rate_limiter)
├── market/            (regime_detector, calendar_manager, mood_calculator, theme_analyzer)
├── analysis/          (chief_analyst, desk_manager, desks/, scoring/)
├── strategy/          (engine, signal_aggregator, strategies/, reentry_guard)
├── execution/         (fund_commander, risk_manager, critical_risk_kernel, order_executor, reservation_manager)
├── position/          (position_manager, sell_retry_strategy, fallback_executor)
├── adaptive/          (weight_optimizer, param_optimizer, desk_allocator, trade_analyzer, overfit_guard)
├── data/              (provider, live_provider, backtest_provider, price_poller, quality_tracker)
├── infra/             (fault_injection, alert_manager, report_generator, watchdog)
├── models/            (db_models, v4_models, schemas, enums)
├── db/                (session, migrations, queries/)
├── kis/               (client, auth, websocket)
└── tests/
```

---

## 1. Phase 2-B: Market Calendar

**예상 기간:** 4~5일 | **진행률:** 10%

### 작업 목록

| # | 작업 | 파일 | 예상 |
|---|------|------|------|
| 1 | Enum 및 스키마 | `models/enums.py`, `models/schemas.py` | 0.5일 |
| 2 | DB 모델 + 마이그레이션 | `models/v4_models.py`, Alembic | 0.5일 |
| 3 | CalendarManager 핵심 로직 | `market/calendar_manager.py` | 1.5일 |
| 4 | 연간 자동 생성 스크립트 | `market/calendar_generator.py` | 1일 |
| 5 | DB 쿼리 | `db/queries/calendar_queries.py` | 0.5일 |
| 6 | Orchestrator 연동 | `core/orchestrator.py` | 0.5일 |
| 7 | 단위 테스트 | `tests/unit/test_calendar_manager.py` | 0.5일 |

### 핵심 스펙

- **CalendarEventType:** FOMC, BOK_RATE, FUTURES_EXPIRY, QUAD_WITCHING, MSCI_REBALANCE, FTSE_REBALANCE, INDEX_REBALANCE, LARGE_IPO, LOCKUP_EXPIRY, EX_DIVIDEND, EARNINGS, YEAR_END, YEAR_START, HOLIDAY_ADJACENT, USER_CUSTOM
- **합산 규칙:** `bet_modifier = min(이벤트들)`, `desk_active = all(이벤트별 desk 활성)`, CLASS 제한은 DISABLED > RESTRICTED > NORMAL 병합
- **종목 제한:** `target_ticker`로 시장 전체 vs 종목 단위 이벤트 구분, `is_stock_restricted(ticker, date)` 반환 (제한여부, 사유)

### Phase 2-B 완료 기준 (DoD)

- CalendarManager가 당일 CalendarAdjustment 정확 반환
- 복수 이벤트 합산 규칙 정상
- 종목 단위 restriction 정상
- 2026년 연간 캘린더 자동 생성 완료
- Orchestrator PRE_MARKET에서 calendar 조회 연동, READY 전이 시 calendar_checked 포함
- 단위 테스트 9건 통과

---

## 2. Phase 2-C: Command Center

**예상 기간:** 7~8일 | **V4.1 핵심 변경 대부분 구현**

### V4.1 신규 항목

1. v4_reservations + ReservationState 상태 머신  
2. v4_order_requests + idempotency_key UNIQUE  
3. v4_universe_version + universe 버전화  
4. FundPool DB=SoT (rebuild_from_db)  
5. Regime 히스테리시스 (상향 3일/하향 2일)  
6. Chief Analyst + Fund Commander  

### 작업 목록

| # | 작업 | 파일 | 예상 |
|---|------|------|------|
| 1 | V4.1 신규 DB 테이블 3개 | `models/v4_models.py`, Alembic | 1일 |
| 2 | FundPool DB=SoT 리팩토링 | `core/fund_pool.py` | 1.5일 |
| 3 | ReservationManager | `execution/reservation_manager.py` | 0.5일 |
| 4 | Regime 히스테리시스 | `market/regime_detector.py` | 0.5일 |
| 5 | Chief Analyst | `analysis/chief_analyst.py` | 1.5일 |
| 6 | Fund Commander | `execution/fund_commander.py` | 1일 |
| 7 | 단위 테스트 | test_fund_pool, test_reservation, test_idempotency, test_chief_analyst, test_fund_commander | 1일 |

### Phase 2-C 완료 기준

- v4_reservations, v4_order_requests, v4_universe_version 생성 및 사용
- FundPool DB=SoT + rebuild_from_db 동작
- ReservationState 전이 검증
- idempotency_key UNIQUE 동작
- 레짐 히스테리시스 적용
- ChiefAnalyst universe 생성·버전화
- FundCommander 6단계 bet_size 계산
- 단위 테스트 20건 통과

---

## 3. Phase 2-D: DESK 2/3 + 스코어링

**예상 기간:** 5~6일

- UniverseScorer: 5개 스코어러 조합, 레짐 조건부 가중치, 데이터 없음 시 가중치 재분배
- 5개 스코어러 병렬(asyncio.gather), 가중치는 PRE_MARKET 1회 로드 후 캐싱

---

## Phase 3 ~ 6 요약

- **Phase 3:** Strategy Engine(CLASS 실행, idempotency), Risk 2계층(CRK + Full), Order Executor(비동기 배치, rate limit), Position Manager(CRK sweep, SELL_FAILED 재시도, fallback)
- **Phase 4:** Adaptive Engine(주간 가중치, 레짐 조건부, 과적합 방지), Data Quality Tracker(소스 상태, 등급)
- **Phase 5:** CRK 독립 경로 검증, Observability(4대 지표, 알림 3단계)
- **Phase 6:** Backtest FutureDataGuard, 슬리피지/거래량 충격, Paper Trading, Go-Live 체크리스트

---

## 수익 극대화 입증 프레임워크

**원론:** E = (Win% × Avg_Win) − (Loss% × Avg_Loss) > 0

- **목표 파라미터:** Win% 55%, Avg_Win +3.5%, Avg_Loss −2.5%, RRR 1.4:1 → E ≈ +0.80% per trade
- **실전 목표:** 월 8~12%, MDD −10% 이내, Calmar ≥ 2.0, Profit Factor ≥ 1.5
- **Edge 입증:** 수급 필터 ON/OFF, 레짐 적응 ON/OFF, 변동성 돌파 파라미터 그리드, 5-CLASS 포트폴리오 효과 검증
- **Walk-Forward:** 6개월 학습 → 3개월 검증 슬라이딩, 모든 OOS 구간 E > 0, OOS/IS ratio ≥ 0.6

---

## Phase A: Task A-2 ~ A-7

Phase A는 **수익의 뼈대**를 만든 뒤 최초 기대값 입증을 목표로 한다.

### Task A-2: 백테스트 데이터 파이프라인

- **파일:** `backtest/data_provider.py`
- **핵심:** `FutureDataGuard` 데코레이터로 sim_date 이후 데이터 참조 차단
- **지표:** OHLCV 기반 MA, RSI, MACD, BB, ATR, ADX, volume_ma20 벡터화 사전 계산

### Task A-3: 5대 스코어링 엔진

- **파일:** `scoring/base_scorer.py`, `supply_demand.py`, `sector.py`, `theme.py`, `volume.py`, `technical.py`, `composite_scorer.py`
- **구조:** 각 카테고리 0~20점, 가중 합산 최대 100점, 데이터 없을 때 가중치 재분배

### Task A-4: CLASS-A 모멘텀 추종

- **파일:** `strategy/base_strategy.py`, `strategy/class_a_momentum.py`
- **조건(AND):** 현재가 > 전일종가, > MA20, 거래량 ≥ MA20×1.5, 외국인 순매수, RSI 35~65
- **손익비:** 1.2 미만이면 진입 거부

### Task A-5: 포지션 관리 + 손절/익절/Trailing

- **파일:** `position/position_manager.py`
- **청산 우선순위:** 손절 → 목표가 → Trailing Stop → 최대 보유일
- **Re-Entry Guard:** 당일 손절 종목·당일 3회 초과 재진입 차단

### Task A-6: 백테스트 엔진 + 성과 측정

- **파일:** `backtest/engine.py`, `backtest/metrics.py`
- **지표:** 기대값, 승률, Avg_Win/Loss, RRR, PF, CAGR, MDD, Calmar, Sharpe, 최대 연패, 월별 수익월 비율

### Task A-7: 최초 기대값 입증 실행

- **파일:** `main_backtest.py`
- **흐름:** 데이터 로드 → 전체 기간 백테스트 → Walk-Forward → Ablation Study → 5대 조건 판정
- **통과 기준:** E > +0.3%, Calmar > 1.5, PF > 1.3, Walk-Forward 전 구간 E > 0

### Phase A 완료 판정

- Task A-1 ~ A-7 코드 완성
- `python main_backtest.py` 실행 시 3년 백테스트 → Walk-Forward → Ablation → 판정까지 일괄 실행
- 데이터는 `data/` (OHLCV, flow 등) 준비 후 즉시 실행 가능
- **✅ PROFITABLE SYSTEM** 판정 후 Phase B(리스크 인프라) 착수

---

## 문서 변경 이력

- 2026-02-13: 최초 작성 (Phase 2-B~6 실전 기획, 역할별 기획, 수익 입증 프레임워크, Phase A Task A-2~A-7 명세)

---

*상세 코드 블록·ASCII 다이어그램·DESK별 CONFIG·REGIME_OPERATION_MATRIX·전체 Python 스니펫은 동일 제목의 "실전 기획서 전문" 또는 원본 채팅 기록을 참조하세요.*
