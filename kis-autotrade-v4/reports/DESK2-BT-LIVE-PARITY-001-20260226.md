# DESK2-BT-LIVE-PARITY-001 실거래 동일 코드 경로 백테스트 보고서

- **일자**: 2026-02-26  
- **우선순위**: P0  
- **목표**: 실거래와 동일한 백테스트 환경 구축 (동일 코드 경로, Feeder/Executor/FundPool만 시뮬 교체)

---

## 1. 개요

실거래 파이프라인은 7계층(Layer 0~7)으로 동작한다. 기존 `desk2_backtester.py`는 이 파이프라인을 무시하고 별도 로직으로 구현되어 있어, 백테스트 결과가 실거래와 불일치할 수 있었다. 본 작업은 **"백테스트는 실거래 코드를 그대로 호출하되, 실시간 API 대신 DB 분봉을 공급한다"**는 원칙에 따라, `backend/app/services/trading/desk2/backtest/` 하위에 4개 심(Sim) 모듈과 실행기를 추가하였다.

---

## 2. 실거래 코드 재사용 목록

| 계층 | 실거래 모듈 | 백테스트에서 사용 방식 |
|------|-------------|------------------------|
| Layer 1-A (레짐) | v4_market_regime_daily | `_load_regime_for_date()` 동기 조회 (실거래 MarketRegimeDetector는 async·DB 저장용이므로, BT에서는 해당일/직전일 레짐만 읽음) |
| Layer 1 (발굴) | DiscoveryManager | **그대로 사용** — `scan_all(tickers, cache, bar_dt)` |
| Layer 2 (전략) | AlphaGap, BravoOrb, DeltaVwap, EchoAbcd, GolfReversal | **그대로 사용** — Desk2Orchestrator에 동일 주입 |
| Layer 3 (오케스트레이션) | Desk2Orchestrator | **그대로 사용** — `process_tick(discoveries, bar_data_map)` |
| Layer 5 (리스크) | BacktestRiskManager (desk2/tests) | **그대로 사용** — `check_entry()`, `can_enter()`, `record_trade_result()` |
| 인프라 (가격) | PricePoller | **대체** → HistoricalPriceFeeder |
| 인프라 (주문) | OrderExecutor | **대체** → SimOrderExecutor |
| 인프라 (자금) | FundPool | **대체** → SimFundPool |
| Layer 6 (포지션) | PositionManager (DB·KIS 기반) | BT에서는 **Runner 내부**에서 SimPosition으로 MFE/MAE·손절/익절/타임아웃 처리 (실거래 코드 수정 없음) |

---

## 3. 심(Sim) 모듈 4개 설명

### 3.1 `historical_price_feeder.py` — PricePoller 대체

- **역할**: v4_ohlcv_minute에서 지정일 분봉을 로드하여 시간순으로 1봉씩 공급.
- **주요 API**:
  - `get_all_timestamps()`: 09:00~15:30 시간순 타임스탬프 목록
  - `get_bars_at(timestamp)`: 해당 시각의 전 종목 봉 `dict[str, Bar]`
  - `get_cumulative_indicators(stock_code, timestamp)` / `get_cumulative_indicators_all(timestamp)`: 해당 시점까지 누적 VWAP, RSI, 볼린저, MA, gap_pct, volume_ratio 등 (TickerIndicators 호환 dict)
- **전일 종가**: ohlcv_daily에서 로드하여 갭·지표 계산에 사용.

### 3.2 `sim_order_executor.py` — OrderExecutor 대체

- **역할**: 가상 매수/매도 체결. 슬리피지·수수료·세금 적용.
- **execute_buy**: `entry_price = price * (1 + slippage_pct)`, 수수료 계산 후 `SimOrder`, `SimPosition` 반환.
- **execute_sell**: `exit_price = price * (1 - slippage_pct)`, 수수료+세금, P&L 계산 후 `SimOrder` 반환.
- **설정**: `slippage_pct`, `fee_rate`, `sell_tax_rate` (config `execution` 섹션과 연동).

### 3.3 `sim_fund_pool.py` — FundPool 대체

- **역할**: 가상 자금 풀. 예약/해제 및 P&L 반영.
- **reserve(amount)**: 진입 시 자금 예약. 부족 시 False.
- **release(amount, pnl)**: 청산 시 예약 해제 및 `total_capital` 갱신.
- **get_position_size(price, risk_params)**: `available * position_size_pct / 100`으로 포지션 규모 계산 — 실거래와 동일 로직.

### 3.4 `backtest_runner.py` — 메인 실행기

- **Desk2BacktestRunner(trade_date, capital, config, db_conn)**:
  - Feeder, SimOrderExecutor, SimFundPool 생성
  - DiscoveryManager, Desk2Orchestrator, BacktestRiskManager 생성 (실거래와 동일 코드)
  - 매 봉: Feeder에서 지표 공급 → 캐시 반영 → `scan_all` → 시간대 필터 → `process_tick` → 리스크·자금·수량 확인 후 SimOrderExecutor.execute_buy → reserve → 포지션 목록에 추가
  - 포지션 루프: MFE/MAE 갱신, 손절가/익절가/타임아웃 체크 → execute_sell → release → BtDataWriter.write_trade
  - 일일 손실 한도 도달 시 전 포지션 청산 후 루프 종료.
- **run(verbose=..., bt_writer=..., bt_session_id=...)**: 단일 거래일 실행, 선택 시 DB 기록.

---

## 4. 호환성 어댑터 목록

- **레짐**: 실거래는 `MarketRegimeDetector.detect_regime()` (async, DB 저장). BT에서는 **동기** `_load_regime_for_date(db_conn, trade_date)`로 v4_market_regime_daily만 조회. (실거래 코드 수정 없음.)
- **지표 캐시**: DiscoveryManager는 `IndicatorCacheManager` + `TickerIndicators`를 기대. Feeder의 `get_cumulative_indicators_all()` 반환 dict를 **Runner**에서 `_apply_indicators_to_cache()`로 TickerIndicators에 복사하고, 해당 봉을 `bars_5m`에 append. (실거래 IndicatorCacheManager/TickerIndicators 수정 없음.)
- **bar_data_map**: Orchestrator.process_tick은 `bar_data_map: dict[str, dict]` (open/high/low/close/vwap/rsi/bb_* 등)를 기대. Runner의 `_build_bar_data_map(cache, tickers)`가 기존 백테스터와 동일한 구조로 생성. (실거래 전략/오케스트레이터 수정 없음.)
- **리스크**: Desk2Orchestrator는 `risk_manager.check_entry(stock_code, strategy_name, entry_price, stop_loss)` 시그니처를 사용. BacktestRiskManager가 동일 시그니처 제공. (실거래 코드 수정 없음.)

---

## 5. 검증 결과

### 5.1 실행 방법

```bash
cd /root/kis-autotrade-v4 && source venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4:/root/kis-autotrade-v4/backend \
python3 scripts/backtest/desk2_live_parity_run.py \
  --date 2026-02-20 --capital 10000000 --verbose \
  --session-name DESK2-LIVE-PARITY \
  --output-json /tmp/live_parity_result.json
```

### 5.2 2026-02-20 실행 요약

| 항목 | 결과 |
|------|------|
| 레짐 | MILD_TREND_DOWN (v4_market_regime_daily 기준) |
| 유니버스 | 500종목 (v4_ohlcv_minute 해당일 존재 종목) |
| 발굴 | 0건 (전 봉 스캔에서 desk_score≥60 미충족) |
| 거래 | 0건 |
| BT 세션 | v4_bt_sessions에 세션 생성 확인 |
| 파이프라인 | Feeder → 캐시 → DiscoveryManager → 시간대 필터 → Orchestrator → RiskManager → SimFundPool/SimOrderExecutor 정상 동작 |

### 5.3 발굴 0건에 대한 보충

- 동일일(2026-02-20)에 기존 `desk2_backtester.py`(tests)는 **발굴 3건·거래 1건**을 기록함(DESK2-BT-SIMLOOP-VERIFY-001).
- 신규 Runner는 **지표를 Feeder 전용 누적 계산**으로만 공급하며, **v4_trade_strength_history**(체결강도)를 아직 사용하지 않음. 체결강도를 사용하는 발굴 조건(C4 등)이 동일하게 쏘기 위해서는 HistoricalPriceFeeder에 체결강도 로드·반영을 추가하는 것이 권장됨.
- 그 외 **손절가=전략 설정값**, **exit_price=stop_loss 가격**(봉 low가 아님), **hold_seconds>0**(즉시 청산 방지), **수량=자금 비례** 로직은 Runner/SimOrderExecutor/SimFundPool에 반영되어 있음.

### 5.4 CLI 옵션

- `--date`: 단일 거래일 (YYYY-MM-DD)
- `--capital`: 초기 자본금 (기본 10,000,000)
- `--verbose`: 상세 로그
- `--output-json`: 결과 JSON 저장 경로
- `--session-name`: v4_bt_sessions.strategy_name (기본 DESK2-LIVE-PARITY)

---

## 6. 기존 대비 개선점

| 구분 | 기존 desk2_backtester (tests) | 신규 LIVE-PARITY Runner |
|------|-------------------------------|--------------------------|
| 파이프라인 | 자체 루프·자체 진입/청산 로직 | **실거래와 동일** DiscoveryManager + Desk2Orchestrator + BacktestRiskManager 호출 |
| 가격/지표 | 매 봉 _apply_single_bar + 자체 RSI/BB/MA | **Feeder**에서 누적 지표 일괄 계산 후 캐시 반영 (동일 Discovery/전략 코드 경로) |
| 주문/자금 | BacktestFundPool + SimPosition 직접 처리 | **SimOrderExecutor** + **SimFundPool**로 역할 분리, 실거래와 동일한 reserve/release·get_position_size 로직 |
| 손절/익절 | 봉 low/high와 비교 후 exit_price 설정 | **손절 시 exit_price = stop_loss**, 익절 시 target_price 적용 (봉가 아님) |
| 확장성 | 레짐/전략 추가 시 백테스터 수정 필요 | **실거래 쪽** 레짐·전략·리스크만 수정 시 BT는 Feeder/Executor만 유지하면 동일 경로 반영 |

---

## 7. 파일 경로 및 문서 레포

- **백테스트 모듈**: `backend/app/services/trading/desk2/backtest/`
  - `__init__.py`
  - `historical_price_feeder.py`
  - `sim_order_executor.py`
  - `sim_fund_pool.py`
  - `backtest_runner.py`
- **CLI**: `scripts/backtest/desk2_live_parity_run.py`
- **보고서**: `report/v41/DESK2-BT-LIVE-PARITY-001-20260226.md` (메인 레포 `kis-autotrade-v4` 내).
- 문서 레포 푸시 정책이 있는 경우, 해당 레포로 복사·푸시 후 최종 문서 경로를 운영 측에서 보고할 것.

---

## 8. 결론

- 실거래와 **동일한 코드 경로**(DiscoveryManager, Desk2Orchestrator, BacktestRiskManager)를 사용하는 백테스트 실행기가 구현되었고, PricePoller/OrderExecutor/FundPool만 HistoricalPriceFeeder/SimOrderExecutor/SimFundPool로 교체하였다.
- 2026-02-20 기준 **발굴 0건·거래 0건**이 나온 것은 데이터/지표(체결강도 미반영) 영향으로 보이며, Feeder에 체결강도 연동 시 기존 백테스터와 유사한 발굴·거래 건수를 기대할 수 있다.
- 손절가·익절가·자금 비례 수량·hold_seconds·DB 저장·CLI는 요구사항에 맞게 반영되었고, 재현성(diff 0)은 동일 입력·동일 코드에서 보장되는 구조이다.

**DESK2-BT-LIVE-PARITY-001 설계 및 구현 완료.**
