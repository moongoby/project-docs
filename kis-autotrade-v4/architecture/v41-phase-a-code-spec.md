# KIS AutoTrade V4.1 — Phase A 코드 명세 (Task A-2 ~ A-7)

**목적:** 최초 기대값 입증을 위한 백테스트·스코어링·CLASS-A·포지션·엔진·검증 코드 구조 및 핵심 로직 정리  
**기준 문서:** v41-development-plan-spec.md

---

## 1. Task A-2: 백테스트 데이터 파이프라인

**파일:** `backtest/data_provider.py`

- `FutureDataLeakError` 예외 정의
- `future_data_guard` 데코레이터: `result['trade_date'] > sim_date` 검사 시 위반 시 예외
- `BacktestDataProvider`: `load_all(tickers, start_date, end_date)` → OHLCV/flow 로드, `_calculate_indicators(ohlcv)` 벡터화(MA5/10/20/60/120, RSI14, MACD, BB, ATR14, ADX14, volume_ma20)
- `set_sim_date(sim_date)`, `get_ohlcv(ticker, as_of_date, lookback_days)`, `get_investor_flow`, `get_indicators`, `get_today_price`, `get_prev_close`, `get_trading_days`

---

## 2. Task A-3: 5대 스코어링 엔진

**공통:** `BaseScorer(ABC)`, `score(ticker, trade_date) -> (float 0~20, detail: dict)`

| 스코어러 | 파일 | 핵심 항목 (0~20점) |
|----------|------|---------------------|
| SupplyDemandScorer | scoring/supply_demand.py | 외국인 5일 순매수(0~8), 기관 5일(0~6), 쌍끌이 보너스(0~4), 연속 순매수일(0~2) |
| SectorScorer | scoring/sector.py | 5일 상대수익률(0~8), 20일 수익률(0~6), MA20 기울기(0~4), 시총(0~2) |
| ThemeScorer | scoring/theme.py | 거래대금 비율(0~8), 연속 상승일(0~6), 과열 감점(0~-4) |
| VolumeScorer | scoring/volume.py | 거래량 비율(0~8), 추세(0~4), 가격-거래량 동조(0~4), 유동성(0~4) |
| TechnicalScorer | scoring/technical.py | MA 배열(0~6), RSI(0~4), MACD(0~4), BB 위치(0~3), ATR(0~3) |

**CompositeScorer:** `score_ticker` → 가중 합산 `total_score`(최대 100), `score_universe` → 내림차순 정렬

---

## 3. Task A-4: CLASS-A 모멘텀 추종

**파일:** `strategy/base_strategy.py`, `strategy/class_a_momentum.py`

**진입 조건 (AND):**

1. `scoring.total_score >= min_total_score` (기본 65)
2. `today.close > prev_close`
3. `today.close > ma20`
4. `volume_ratio >= volume_ratio_min` (1.5)
5. 최근 N일 외국인 순매수 > 0
6. `rsi_min <= rsi_14 <= rsi_max` (35~65)

**신호 강도:** volume_ratio, foreign_net_total, rsi 구간, macd_hist > 0, ma5 > ma10 → 0~1.0  
**거부:** `reward/risk < 1.2` 이면 None 반환

---

## 4. Task A-5: 포지션 관리

**파일:** `position/position_manager.py`

- `open_position(signal, trade_date, quantity, invested_amount)` → Position 생성, `_today_trade_count` 증가
- `check_and_close_positions(trade_date)`: (1) 손절 `today.low <= stop_loss_price`, (2) 목표가 `today.high >= target_price`, (3) Trailing Stop 활성화 후 `today.low <= trailing_stop_price`, (4) max_hold_days 초과
- `_determine_exit_price`: 손절 시 `stop_loss_price * 0.998` (슬리피지), 목표/트레일링 시 해당가, max_hold 시 종가
- `_calc_trailing_stop`: `high_watermark * (1 - trail_distance_pct/100)`, 단조 증가만 허용
- `is_reentry_blocked(ticker)`: 당일 손절 set, 당일 3회 이상 시 True

---

## 5. Task A-6: 백테스트 엔진 + 성과 측정

**엔진:** `backtest/engine.py`

- `run(start_date, end_date, universe)`: 매 거래일 (1) 포지션 청산 검사 (2) 유니버스 스코어링 (3) 매수 신호 생성 (4) 신호 실행(자금/슬리피지/수량) (5) equity_curve 기록
- 수수료·세·슬리피지 반영, 잔여 포지션 마지막 날 강제 청산

**지표:** `backtest/metrics.py` — `calculate_metrics(trades, equity_curve, initial_capital)` → BacktestResult(expectancy_per_trade, win_rate, avg_win_pct, avg_loss_pct, risk_reward_ratio, profit_factor, total_return_pct, cagr_pct, max_drawdown_pct, calmar_ratio, max_consecutive_losses, monthly_positive_rate, sharpe_ratio)

---

## 6. Task A-7: 검증 및 실행

**파일:** `backtest/validator.py`, `main_backtest.py`

- **EdgeValidator.walk_forward:** 6개월 학습 → 3개월 검증 슬라이딩, 각 구간 `test_expectancy > 0` 여부, oos_ratio
- **ablation_study:** 조건별 OFF 후 기대값/승률 변화 (price_above_prev_close, price_above_ma20, volume_ratio_min, foreign_net_positive_days_min, rsi_min)
- **main_backtest.py:** 데이터 로드 → 전체 백테스트 → 5대 조건 판정 → Walk-Forward → Ablation → 최종 보고

**통과 기준:** 기대값 > +0.3%, 승률 > 45%, RRR > 1.2, PF > 1.3, MDD > -20%, Walk-Forward 전 구간 E > 0

---

*실제 구현 시 config/system_config.py, config/desk_config.py, models/signal.py, models/position.py, models/backtest_result.py, models/scoring.py, models/market_data.py 등이 필요하며, 개발 실전 기획서 본문의 Python 스니펫을 참고한다.*
