# STRAT-DETAIL 완료 보고서 — 2026-02-21

## 1. 진입 조건 구조

### entry_rules JSON 구조
```json
{
  "indicators": ["sma5_above_sma20", "volume_surge_2x", ...],  // 진입 지표 배열
  "min_strength": 40~75,        // 시그널 강도 최소 기준
  "min_conditions": 1~4,        // 충족해야 할 최소 조건 수
  "time_window": {"start": "09:05", "end": "15:20"},  // 진입 허용 시간 (일부 카드)
  "logic": "설명문"              // 일부 카드에 텍스트 로직 설명 포함
}
```

### 범위 요약
| 항목 | 범위 | 비고 |
|------|------|------|
| min_strength | 40~75 | DESK1: 40~75, DESK2: 40~75, DESK3: 50~55, DESK4: 58~62, DESK5: 60~70 |
| min_conditions | 1~4 | DESK1: 1~2, DESK2: 1~4, DESK3: 1~3, DESK4: 3, DESK5: 3~4 |
| indicator 종류 | **총 114종** (고유 명칭 기준) | 범용 11종 + DESK별 특화 지표 |

### exit_rules JSON 구조
```json
{
  "stop_loss_pct": -0.3 ~ -7.0,       // 손절 %
  "trailing_stop_pct": 0.2 ~ 5.0,     // 트레일링 스탑 %
  "target_profit_pct": 0.5 ~ 85.0,    // 목표 수익 %
  "max_hold_days": 0 ~ 120,           // 최대 보유일
  "eod_force_exit": true/false,        // 장마감 강제 청산
  "eod_force_exit_time": "15:00",      // 강제 청산 시각
  "time_stop_minutes": 15~45,          // 시간 기반 청산 (DESK1만)
  "logic": "조건설명"                   // 일부 카드에 텍스트 설명
}
```

### exit_rules 키 사용 빈도
| 키 | 사용 카드수 |
|----|-----------|
| stop_loss_pct | 56 |
| target_profit_pct | 55 |
| max_hold_days | 47 |
| eod_force_exit | 47 |
| trailing_stop_pct | 47 |
| eod_force_exit_time | 16 |
| logic | 13 |
| time_stop_minutes | 9 (DESK1만) |

**참고**: exit_rules에는 indicators 배열이 없음 (0개). 모든 청산은 수치 파라미터 기반.

---

## 2. DESK별 진입/청산 조건 요약

### DESK1 (스캘핑, 10카드)
| card | name | indicators | min_str | min_cond | SL% | TS% | TP% | hold | EOD | time_stop |
|------|------|-----------|---------|----------|-----|-----|-----|------|-----|-----------|
| 5 | 스캘핑_class_b | commander_scan | 40 | 1 | -0.3 | 0.2 | 1.0 | 1 | Y | - |
| 38 | 초단타모멘텀 | vol_spike_5x, price_mom_1m, bid_ask | 70 | 2 | -0.7 | 0.3 | 2.0 | 0 | Y | 30m |
| 39 | 갭메우기 | gap_up, gap_fill, vol_3x, reversal | 65 | 2 | -0.8 | 0.25 | 1.5 | 0 | Y | 45m |
| 40 | 뉴스반응스캘핑 | news_spike, vol_5x, rev_5m, bid_ask | 68 | 2 | -1.0 | 0.35 | 2.2 | 0 | Y | 25m |
| 41 | S01_호가불균형 | order_imbal, bid_ask, vol_1m | 72 | 2 | -0.6 | 0.2 | 1.2 | 0 | Y | 20m |
| 42 | S02_고래추적 | whale_vol, trade_str, mom_1m, vol_5x | 70 | 2 | -0.7 | 0.3 | 1.8 | 0 | Y | 30m |
| 43 | S03_스프레드갭 | spread_gap, narrow_5m, vol_5, stable | 68 | 2 | -0.5 | 0.2 | 1.0 | 0 | Y | 15m |
| 44 | S04_플래시크래시 | flash_crash, vol_10x, reversal, support | 75 | 2 | -1.0 | 0.4 | 2.5 | 0 | Y | 20m |
| 45 | M03_이격도숏 | disparity_110, rsi_ob, vol_2x, bb_up | 70 | 2 | -0.8 | 0.3 | 1.5 | 0 | Y | 40m |
| 46 | H01_시장센서 | idx_mom_5m, sector_rot, vol_3x, corr | 68 | 2 | -0.7 | 0.3 | 1.8 | 0 | Y | 30m |

**DESK1 특성**: SL -0.3~-1.0%, TS 0.2~0.4%, TP 1.0~2.5%, 당일 강제 청산, time_stop 15~45분, 포지션 2~3개, 단일종목 30~50%

### DESK2 (데일리, 16카드)
| card | name | indicators수 | min_str | min_cond | SL% | TS% | TP% | hold | EOD |
|------|------|-------------|---------|----------|-----|-----|-----|------|-----|
| 6 | 데일리_class_a | 5 | 40 | 2 | -1.5 | 1.0 | 6.0 | 1 | Y |
| 7 | 종가매매_class_c | 3 | 40 | 2 | -1.5 | 1.0 | 6.0 | 2 | N |
| 14 | 장초반레인지돌파 | 4 | 50 | 3 | -2.0 | 1.0 | 6.0 | 1 | Y |
| 15 | VWAP회귀 | 2 | 65 | 2 | -2.0 | 1.0 | 6.0 | 1 | Y |
| 16 | 갭상승후하락베팅 | 4 | 40 | 4 | -5.0 | - | 0.5 | - | - |
| 17 | 볼린저밴드돌파 | 2 | 75 | 2 | -2.0 | - | 6.0 | - | - |
| 18 | RSI역추세 | 1 | 70 | 1 | -2.0 | - | 6.0 | - | - |
| 19 | 거래량스파이크 | 4 | 50 | 4 | -2.0 | - | 6.0 | - | - |
| 20 | 변동성확대 | 2 | 68 | 2 | -2.0 | 1.0 | 6.0 | 1 | Y |
| 21 | D01_3분봉눌림목 | 4 | 75 | 4 | -2.0 | - | - | - | - |
| 22 | S05_거래량점화 | 4 | 50 | 4 | -2.0 | - | 6.0 | - | - |
| 23 | M01_오픈레인지돌파 | 4 | 50 | 3 | -2.0 | 1.0 | 6.0 | 1 | Y |
| 24 | L01_VWAP반등 | 2 | 65 | 2 | -2.0 | 1.0 | 6.0 | 1 | Y |
| 25 | M00_시초첫3분봉 | 1 | 72 | 1 | -1.0 | - | 1.5 | - | - |
| 26 | M001_3분봉종합눌림 | 4 | 75 | 4 | -0.5 | - | 1.0 | - | - |
| 27 | M002_AbsoluteZero | 2 | 65 | 2 | -0.8 | - | 1.2 | - | - |

**DESK2 특성**: SL -0.5~-5.0%, TS 1.0%(있는 경우), TP 0.5~6.0%, 보유 0~2일, 포지션 6개, 단일종목 20%. **7개 카드에 trailing_stop 없음 → 수익 확보 불리**

### DESK3 (단기스윙, 10카드) — 핵심 수익원
| card | name | indicators | min_str | min_cond | SL% | TS% | TP% | hold |
|------|------|-----------|---------|----------|-----|-----|-----|------|
| 8 | 단기스윙_class_d | sma5>20, sma20>60, vol_2x, rsi<70, macd_gc | 50 | 3 | -3.0 | 2.0 | 16.0 | 10 |
| 28 | MACD크로스오버 | gap_down_2pct_recovery, vol>ma20 | 50 | 2 | -3.0 | 2.0 | 16.0 | 10 |
| 29 | 이동평균크로스 | ma5_ma20_golden_cross | 55 | 1 | -3.0 | 2.0 | 16.0 | 10 |
| 30 | 지지저항반등 | support_touch, bullish, vol_1.2x, rsi_30_50 | 50 | 3 | -3.0 | 2.0 | 16.0 | 10 |
| 31 | 추세내조정진입 | ma5>20, ma20>60, vol_1.5x | 55 | 3 | -3.0 | 2.0 | 16.0 | 10 |
| 32 | 채널돌파 | price<ma20_5%, rsi<35, vol_1.2 | 50 | 3 | -3.0 | 2.0 | 16.0 | 10 |
| 33 | MACD다이버전스 | high3_break, vol_1.5x, ma5>20 | 50 | 3 | -3.0 | 2.0 | 16.0 | 10 |
| 34 | 볼린저밴드반등 | double_bottom_20d, rsi_rising, neckline | 50 | 3 | -3.0 | 2.0 | 16.0 | 10 |
| 35 | M02_볼린저스퀴즈 | double_bottom_20d, rsi_rising, neckline | 50 | 3 | -3.0 | 2.0 | 16.0 | 10 |
| 36 | 이동평균선교차_MID | ma5_ma20_golden_cross | 55 | 1 | -3.0 | 2.0 | 16.0 | 10 |
| 37 | 지지저항돌파_MID | support_res_break, vol_1.2, ma5>20 | 50 | 2 | -3.0 | 2.0 | 16.0 | 10 |

**DESK3 특성**: **모든 카드 동일 청산 조건** (SL -3%, TS 2%, TP 16%, hold 10일). 진입 조건만 차이. 포지션 5개, 단일종목 25%.

### DESK4 (중기, 9카드)
| card | name | indicators | min_str | min_cond | SL% | TS% | TP% | hold |
|------|------|-----------|---------|----------|-----|-----|-----|------|
| 9 | 중기스윙_class_e | sma20>60, sma60>120, vol_trend, macd, rsi>50 | 60 | 3 | -5.0 | 3.0 | 41.0 | 40 |
| 11 | 중기추세추종 | ma20>60, inst_5d, macd_gc, sector_top30 | 60 | 3 | -5.0 | 3.0 | 41.0 | 40 |
| 47 | 피보나치되돌림 | fib_0382, fib_0500, ma20>60, vol, rsi | 60 | 3 | -5.0 | 4.0 | 40.0 | 20 |
| 48 | 엘리어트파동 | wave_corr, ma20>60, macd, vol_5d, rsi>50 | 62 | 3 | -5.0 | 4.0 | 42.0 | 22 |
| 49 | 일목균형표 | ichimoku, price>cloud, vol, rsi_40_60, macd | 58 | 3 | -5.0 | 3.5 | 38.0 | 20 |
| 50 | ParabolicSAR | psar_flip, ma20>60, vol, rsi>50 | 60 | 3 | -5.0 | 4.0 | 40.0 | 20 |
| 51 | ADX추세강도 | adx>25, +di>-di, ma20>60, vol_5d, rsi>50 | 60 | 3 | -5.0 | 4.0 | 42.0 | 22 |
| 52 | 켈트너채널 | keltner_break, ma20>60, vol, macd, rsi>50 | 58 | 3 | -5.0 | 3.5 | 38.0 | 20 |
| 53 | 돈치안채널 | donchian_break, ma20>60, vol, rsi>50, macd | 58 | 3 | -5.0 | 4.0 | 40.0 | 20 |

**DESK4 특성**: SL -5%, TS 3.0~4.0%, TP 38~42%, 보유 20~40일. 포지션 3~5개, 단일종목 25~35%.

### DESK5 (장기, 10카드)
| card | name | indicators | min_str | min_cond | SL% | TS% | TP% | hold |
|------|------|-----------|---------|----------|-----|-----|-----|------|
| 10 | 장기스윙_class_f | sma60>120, sma120_up, vol_20d, macd_w, sector | 70 | 4 | -7.0 | 5.0 | 75.0 | 120 |
| 12 | 가치투자 | per<10, pbr<1, roe>10, ma120_up, inst_60d | 60 | 3 | -7.0 | 5.0 | 75.0 | 120 |
| 13 | 성장주모멘텀 | revenue_20%, earnings, ma120, rel_str, sector | 60 | 3 | -7.0 | 5.0 | 75.0 | 120 |
| 54 | 배당포착 | div_yield>3, div_growth, ma60>120, sector, vol | 68 | 4 | -7.0 | 5.0 | 70.0 | 120 |
| 55 | 계절성추세 | seasonal, ma60>120, vol_20d, sector, rsi>50 | 65 | 4 | -7.0 | 5.0 | 68.0 | 90 |
| 56 | 거시경제테마 | macro_theme, ma60>120, sector, vol, rsi>50 | 70 | 4 | -7.0 | 5.0 | 75.0 | 120 |
| 57 | 섹터리더십 | sector_top20%, ma60>120, sma120_up, vol, macd_w | 70 | 4 | -7.0 | 5.0 | 75.0 | 120 |
| 58 | 퀄리티팩터 | quality_roe>15, op_margin, ma60>120, sector, vol | 70 | 4 | -7.0 | 5.0 | 72.0 | 120 |
| 59 | 저변동성 | low_vol_20d, ma60>120, sector, vol, rsi_40_60 | 65 | 4 | -7.0 | 5.0 | 64.0 | 120 |
| 60 | 모멘텀팩터 | mom_6m+, ma60>120, sma120_up, vol, rsi>50 | 68 | 4 | -7.0 | 5.0 | 85.0 | 120 |

**DESK5 특성**: SL -7%, TS 5%, TP 64~85%, 보유 90~120일. 포지션 2개, 단일종목 40~50%. **min_strength 60~70으로 가장 높은 기준**.

### 미배정 카드 (2개)
| card | name | entry_rules | exit_rules | 비고 |
|------|------|------------|-----------|------|
| 3 | GO100 추세상승극대화 | NULL | NULL | GO100 전용, is_active=true |
| 61 | 시초가매매 | NULL | NULL | 커스텀, is_active=true |

---

## 3. 수익 카드 vs 손실 카드 조건 비교

### 수익 TOP 5
| card | desk | min_str | min_cond | ind수 | SL% | TS% | TP% | hold | 특징 |
|------|------|---------|----------|-------|-----|-----|-----|------|------|
| 37 | 3 | 50 | 2 | 3 | -3.0 | **2.0** | 16.0 | 10 | 넓은 진입+트레일링 |
| 8 | 3 | 50 | 3 | 5 | -3.0 | **2.0** | 16.0 | 10 | 다중 조건+트레일링 |
| 34 | 3 | 50 | 3 | 3 | -3.0 | **2.0** | 16.0 | 10 | 더블바텀+트레일링 |
| 19 | 2 | 50 | 4 | 4 | -2.0 | **없음** | 6.0 | - | 엄격한 진입 4조건 |
| 35 | 3 | 50 | 3 | 3 | -3.0 | **2.0** | 16.0 | 10 | =card34 동일 조건 |

### 손실 TOP 5
| card | desk | min_str | min_cond | ind수 | SL% | TS% | TP% | hold | 특징 |
|------|------|---------|----------|-------|-----|-----|-----|------|------|
| 6 | 2 | **40** | **2** | 5 | -1.5 | 1.0 | 6.0 | 1 | **가장 낮은 진입 기준** |
| 23 | 2 | 50 | 3 | 4 | -2.0 | 1.0 | 6.0 | 1 | 레인지돌파 (당일 청산) |
| 18 | 2 | 70 | **1** | **1** | -2.0 | **없음** | 6.0 | - | **단일 조건, TS 없음** |
| 24 | 2 | 65 | 2 | 2 | -2.0 | 1.0 | 6.0 | 1 | 조건 불충분 |
| 31 | 3 | 55 | 3 | 3 | -3.0 | 2.0 | 16.0 | 10 | DESK3이나 조건 약함 |

### 핵심 패턴
1. **수익 카드 공통점**: DESK3 카드 4/5, TS 2.0% 있음, hold 10일, TP 16% — **트레일링으로 이익 극대화**
2. **손실 카드 공통점**: DESK2 카드 4/5, min_strength 낮음(40), trailing_stop 없거나 1.0%, 당일 청산
3. **결정적 차이**: **trailing_stop 존재 여부** + **보유 기간**이 수익/손실의 핵심 구분자

---

## 4. 엔진의 조건 평가 방식

### 백테스트 엔진 V2 (`backtest_engine_v2.py`)
- entry_rules를 **사용하지 않음**
- DESK별 하드코딩된 _run_premarket_scan() 로직으로 종목 선별
- 별도의 `CardRuleSimulator` (card_rule_simulator.py)가 entry_rules.indicators를 실제 평가

### CardRuleSimulator (`card_rule_simulator.py`)
- `EntryConditionEvaluator` 클래스가 indicator → 평가 메서드 매핑
- 지원 indicator: sma5_above_sma20, volume_surge_2x, rsi_below_30, macd_golden_cross 등 ~20종
- entry_rules.min_conditions 기준으로 충족 조건 수 체크
- **min_strength는 저장만 하고 실제 평가에 사용하지 않음**

### LiveSignalGenerator (`live_signal_generator.py`)
- DESK별 고유 평가자 (evaluate_desk1~5)
- entry_rules를 **참조하지 않음** — 자체 하드코딩 조건 사용

| DESK | 조건수 | 최소 충족 | 강도 공식 |
|------|--------|----------|----------|
| DESK1 | 6 (a~f) | 1 | `min(100, max(40, n * 18))` |
| DESK2 | 5 (a~e) | 2 | `max(40, min(100, n/5 * 100))` |
| DESK3 | 5 (a~e) | 2 | `max(40, min(100, n/5 * 100))` |
| DESK4 | 5 (a~e) | 2 | `max(40, min(100, n/5 * 100))` |
| DESK5 | 5 (a~e) | 2 | `max(40, min(100, n/5 * 100))` |

강도 범위: 40~100 (최소 40 보장)

### 실매매 파이프라인 (`v4_pipeline_orchestrator.py`)
- `_execute_card_buy_signals()`: v4_signals에서 `signal_strength >= min_strength` 필터링만 수행
- **entry_rules.indicators는 검증하지 않음**
- **conditions_met (v4_signals JSONB)는 조회하지 않음**

---

## 5. 핵심 발견 및 최적화 가능 포인트

### 발견 1: 진입 조건 평가 단절 (Critical)
| 계층 | entry_rules.indicators 사용 | min_strength 사용 |
|------|---------------------------|------------------|
| 백테스트 (CardRuleSimulator) | **Y** (indicator별 평가) | N (저장만) |
| 시그널 생성 (LiveSignalGenerator) | **N** (DESK 평가자 사용) | N |
| 실매매 (PipelineOrchestrator) | **N** (조회 안 함) | **Y** (필터링) |

**결과**: 백테스트 결과와 실매매 진입이 다를 수 있음. 백테스트는 카드별 indicators를 평가하지만, 실매매는 DESK 공통 시그널의 strength만 필터링.

### 발견 2: DESK3 카드 동질성
DESK3 10개 카드의 exit_rules가 **완전히 동일** (SL -3%, TS 2%, TP 16%, hold 10일). 카드 간 차이는 진입 indicators뿐이나, 실매매에서는 indicators가 평가되지 않으므로 **사실상 동일하게 동작**.

### 발견 3: trailing_stop 부재 카드 = 손실 카드
DESK2의 16개 중 **9개 카드에 trailing_stop 없음** (16~27번 중 일부). BT-OPTIMIZE에서 식별된 손실 카드 대부분이 trailing_stop 없는 카드.

### 발견 4: DESK1 분봉 전용 지표
DESK1의 indicators (order_imbalance, whale_volume, flash_crash 등)는 분봉 데이터 전용. LiveSignalGenerator의 DESK1 평가자는 일봉 기반이므로 **DESK1 카드의 진입 indicators와 실제 시그널 생성 조건이 불일치**.

### 발견 5: risk_params 키 이름 불일치
- strategy_cards.risk_params: `max_positions`, `max_single_stock_pct`, `daily_loss_limit_pct`
- CARD-BUY 코드: `max_concurrent_positions`, `max_capital_usage_pct`, `max_single_position_pct`
- **키 이름이 다르므로 실매매에서 카드별 risk_params가 적용되지 않고 기본값 사용**

### 최적화 권고
1. **risk_params 키 이름 통일**: `max_positions` → `max_concurrent_positions` 등 (DB UPDATE 필요)
2. **DESK3 카드 차별화**: exit_rules를 카드별로 다르게 설정 (high-conviction 카드에 TS 3%, hold 15일 등)
3. **trailing_stop 추가**: DESK2 손실 카드(16,17,18,19,21,22)에 trailing_stop 1.0% 추가
4. **entry_rules.indicators 실매매 연동**: conditions_met를 조회하여 카드별 indicator 매칭 (중장기)
5. **DESK5 min_strength 하향 검토**: 현재 60~70인데 시그널 강도 범위가 40~100이므로, DESK5 시그널이 60 이상이면 이미 조건 3/5 이상 충족 → 적절한 기준

---

## 6. 진입 지표 사용 빈도 TOP 15

| 지표명 | 사용 카드수 | DESK |
|--------|-----------|------|
| rsi_above_50 | 11 | 2,4,5 |
| ma20_above_ma60 | 8 | 3,4 |
| volume_20d_above_avg | 8 | 5 |
| ma60_above_ma120 | 7 | 5 |
| sector_strength | 6 | 5 |
| volume_ratio_20 | 5 | 4 |
| volume_surge_2x | 4 | 1,2,3 |
| volume_spike_5x | 3 | 1 |
| bid_ask_spread_narrow | 3 | 1 |
| sma5_above_sma20 | 3 | 2,3 |
| macd_golden_cross | 3 | 2,3,4 |
| bb_lower_near | 3 | 2 |
| rsi_below_30 | 3 | 2 |
| ma5_above_ma20 | 3 | 3 |
| macd_above_signal | 3 | 4 |

---

## 7. 사전/사후 확인

- strategy_cards: 59 (불변, active 58)
- v4_positions OPEN: 5 (불변)
- 서비스 재시작: 없음 (읽기 전용)
- DB 스키마 변경: 없음
- 코드 수정: 없음

## 컴플라이언스 체크리스트

| .env/.bak 커밋 | strategy_cards 59건 | v4_positions OPEN 5건 | 파일헤더 | DB스키마변경 | 서비스재시작 | V4.1파일수정 |
|---|---|---|---|---|---|---|
| 없음 | 59 | 5 | CC-STRAT-DETAIL | 없음 | 없음 | 없음 (읽기 전용) |
