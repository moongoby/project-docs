# CUR-GO100-P3-R2: 고급 기술 지표 20개 추가 (총 33개 필터)

- **날짜**: 2026-02-27
- **레포**: kis-autotrade-v4 (GO100)
- **목표**: screening_engine + orderbook_backtest_engine(SignalEvaluator)에 pandas-ta 연동 고급 기술 지표 20개 추가

## 개요

기존 13개 필터에 **20개 고급 기술 지표 필터**를 추가하여 **총 33개** 스크리닝 필터를 지원한다. pandas-ta를 사용해 MACD, ADX, 볼린저밴드, 스토캐스틱, CCI, Supertrend, MFI, OBV, ATR, A/D Line 등을 계산하고, 각 필터를 `TechnicalFilterEngine._filter_xxx(df)` 및 `screen_xxx(db)` 형태로 구현했다. 호가창 백테스트 엔진의 `SignalEvaluator.indicator_precompute` 및 `Go100MinuteDataLoader.calc_minute_indicators`에도 동일 지표를 추가했다.

## 수정/추가 파일

| 파일 | 변경 내용 |
|------|------------|
| `backend/app/services/go100/screening_engine.py` | pandas_ta 선택 로드, VALID_FILTERS 33개, TechnicalFilterEngine 20개 _filter_xxx, _add_ta_indicators_single, _load_ohlcv_recent, _run_ta_screening, run_ta_screening_sync, screen_xxx 20개, FILTER_REGISTRY_TA, combined/run_screening/라벨/포맷 반영 |
| `backend/app/services/go100/ai/intent_router.py` | STOCK_SCREENING_KEYWORDS에 P3-R2 키워드(macd, adx, cci, 볼린저, 스토캐스틱, mfi, obv, vwap, 삼병사, 장악형 등) 추가 |
| `backend/app/services/go100/ai/tool_executors.py` | VALID_SCREEN_FILTERS 33개, _TA_FILTER_NAMES, run_ta_screening_sync 호출 분기, combined valid_filters 및 라벨 확장 |
| `backend/app/services/go100/backtest/signal_evaluator.py` | pandas_ta 선택 로드, indicator_precompute에 ADX, BB, Stoch, CCI, Supertrend, Williams %R, MFI, OBV, ATR, A/D Line 추가 |
| `backend/app/services/go100/backtest/minute_data_loader.py` | pandas_ta 선택 로드, calc_minute_indicators에 adx, bb_lower/bb_upper, stoch_k/stoch_d, atr 추가 |

## 신규 필터 목록 (20개)

### 추세 지표 (6개)
| 필터 ID | 조건 | 설명 |
|---------|------|------|
| macd_bullish | MACD > Signal 이전봉 대비 전환 | MACD 골든크로스 |
| macd_bearish | MACD < Signal 이전봉 대비 전환 | MACD 데드크로스 |
| adx_strong_trend | ADX > 25 | 강한 추세 |
| cci_oversold | CCI < -100 | 과매도 |
| cci_overbought | CCI > 100 | 과매수 |
| supertrend_buy | Supertrend 방향 = 1 | Supertrend 매수 |

### 변동성 지표 (4개)
| 필터 ID | 조건 |
|---------|------|
| bb_lower_touch | close <= BB 하단 |
| bb_upper_touch | close >= BB 상단 |
| bb_squeeze | bandwidth < 기준(0.05) |
| atr_breakout | \|close - prev_close\| > 2*ATR |

### 모멘텀 지표 (5개)
| 필터 ID | 조건 |
|---------|------|
| stoch_oversold | K < 20 AND D < 20 |
| stoch_overbought | K > 80 AND D > 80 |
| stoch_golden_cross | K > D 전환 |
| williams_r_oversold | Williams %R < -80 |
| mfi_oversold | MFI < 20 |

### 거래량 지표 (3개)
| 필터 ID | 조건 |
|---------|------|
| obv_rising | OBV 3일 연속 상승 |
| vwap_above | 현재가 > 전봉 종가 (상승) |
| ad_line_rising | A/D Line 직전봉 대비 상승 |

### 복합 패턴 (2개)
| 필터 ID | 조건 |
|---------|------|
| three_white_soldiers | 양봉 3연속 + 각 봉 전봉 고가 돌파 |
| engulfing_bullish | 상승 장악형 (전봉 음봉, 당봉 양봉 몸통 감쌈) |

## 구현 요약

- **screening_engine**
  - `_add_ta_indicators_single(df)`: 단일 종목 OHLCV에 pandas_ta로 MACD, ADX, BB, Stoch, CCI, Supertrend, WillR, MFI, OBV, ATR, A/D 추가.
  - `TechnicalFilterEngine`: 20개 정적 메서드 `_filter_xxx(df)` → 마지막 행 기준 조건 만족 여부 반환.
  - `FILTER_REGISTRY_TA`: filter_id → (함수, min_bars).
  - `_load_ohlcv_recent(db)`: 최근 60일 일봉 OHLCV DataFrame 로드 (universe 3000종 목).
  - `_run_ta_screening(db, filter_id, limit)`: OHLCV 로드 → 종목별 지표 계산 → 필터 적용 → 상위 limit건 상세 조회.
  - `run_ta_screening_sync(conn, filter_id, limit)`: Agent Core(tool_executors)용 동기 버전.
  - 20개 `screen_xxx` 래퍼 및 combined/run_screening/라벨/포맷/ detect_screening_type 패턴 반영.

- **SignalEvaluator / minute_data_loader**
  - `indicator_precompute`: pandas_ta 사용 시 adx, bb_lower/bb_middle/bb_upper, stoch_k/stoch_d, cci, supertrend_d, willr, mfi, obv, atr, ad_line 컬럼 추가.
  - `calc_minute_indicators`: 분봉에 adx, bb_lower/bb_upper, stoch_k/stoch_d, atr 추가.

## 테스트

- [x] 신규 20개 필터 엔진 단위 테스트: `TechnicalFilterEngine`, `_add_ta_indicators_single`, `FILTER_REGISTRY_TA` 20개, `VALID_FILTERS` 35개 확인.
- [ ] 신규 20개 필터 각각 단독 실행 → 결과 10건 이내 반환 확인 (DB 연동).
- [ ] combined: macd_bullish + volume_surge → 교차 결과 확인.
- [ ] Agent Chat "MACD 골든크로스 종목 찾아줘" → macd_bullish 필터 호출.
- [ ] Agent Chat "볼린저밴드 하단 터치 + 거래량 급증" → combined 호출.
- [ ] 필터별 응답 시간 기록 (목표: 단일 < 5초, combined < 15초).

## 필터 목록 전체 (33개)

기존 13개: golden_cross, death_cross, ma_align_bull, rsi_oversold, rsi_overbought, value_low_per, institution_buy, volume_surge, gap_up, trade_strength, momentum_up, foreign_buy, theme.

신규 20개: macd_bullish, macd_bearish, adx_strong_trend, cci_oversold, cci_overbought, supertrend_buy, bb_lower_touch, bb_upper_touch, bb_squeeze, atr_breakout, stoch_oversold, stoch_overbought, stoch_golden_cross, williams_r_oversold, mfi_oversold, obv_rising, vwap_above, ad_line_rising, three_white_soldiers, engulfing_bullish.

(* gap_up_today, gap_down_today 등 추가 필터로 인해 VALID_FILTERS는 35개로 표시될 수 있음.)

## 의존성

- **pandas-ta**: `.venv`에 설치 (`pip install pandas-ta`). 없으면 TA 필터는 스킵되며 기존 13개 필터는 그대로 동작.

## Git

- 코드 레포: `cd /root/kis-autotrade-v4 && git add -A && git status`
- 문서 레포: `cd /root/project-docs && git add -A && git commit -m "[GO100] P3-R2 고급 기술 지표 20개 추가 (총 33개 필터)" && git push origin master`
