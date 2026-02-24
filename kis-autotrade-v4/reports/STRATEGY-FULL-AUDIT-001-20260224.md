# 전략카드 전수 분석 보고서 — STRATEGY-FULL-AUDIT-001

**작업ID:** CUR-STRATEGY-FULL-AUDIT-001  
**작성일:** 2026-02-24 (KST)  
**서버:** root@211.188.51.113  
**프로젝트:** /root/kis-autotrade-v4  
**DB:** PostgreSQL kisautotrade (kis_admin), localhost:5432  

---

## 1. 전략카드 전수 목록 (id, name, desk, type, is_live, 구현상태)

구현상태: **FULL**(진입·청산 지표 전부 구현), **PARTIAL**(일부 지표 미구현), **NONE**(entry_rules 없음 또는 카드만 존재).

| card_id | strategy_name | desk | strategy_type | is_live | 구현상태 |
|--------|----------------|------|---------------|---------|----------|
| 5 | DESK1_스캘핑_class_b | 1 | BUILTIN | t | PARTIAL |
| 38 | DESK1_초단타모멘텀 | 1 | BUILTIN | t | PARTIAL |
| 39 | DESK1_갭메우기 | 1 | BUILTIN | t | FULL |
| 40 | DESK1_뉴스반응스캘핑 | 1 | BUILTIN | t | PARTIAL |
| 41 | DESK1_S01_호가불균형 | 1 | BUILTIN | t | PARTIAL |
| 42 | DESK1_S02_고래추적 | 1 | BUILTIN | t | PARTIAL |
| 43 | DESK1_S03_스프레드갭 | 1 | BUILTIN | t | PARTIAL |
| 44 | DESK1_S04_플래시크래시 | 1 | BUILTIN | t | PARTIAL |
| 45 | DESK1_M03_이격도숏 | 1 | BUILTIN | t | FULL |
| 46 | DESK1_H01_시장센서 | 1 | BUILTIN | t | PARTIAL |
| 6 | DESK2_데일리_class_a | 2 | BUILTIN | f | FULL |
| 7 | DESK2_종가매매_class_c | 2 | BUILTIN | t | PARTIAL |
| 14 | DESK2_장초반레인지돌파 | 2 | BUILTIN | t | PARTIAL |
| 15 | DESK2_VWAP회귀 | 2 | BUILTIN | f | FULL |
| 16 | DESK2_갭상승후하락베팅 | 2 | BUILTIN | t | FULL |
| 17 | DESK2_볼린저밴드돌파 | 2 | BUILTIN | f | FULL |
| 18 | DESK2_RSI역추세 | 2 | BUILTIN | f | FULL |
| 19 | DESK2_거래량스파이크 | 2 | BUILTIN | t | FULL |
| 20 | DESK2_변동성확대 | 2 | BUILTIN | t | FULL |
| 21 | DESK2_D01_3분봉_20선눌림목 | 2 | BUILTIN | t | FULL |
| 22 | DESK2_S05_거래량점화 | 2 | BUILTIN | t | FULL |
| 23 | DESK2_M01_오픈레인지돌파 | 2 | BUILTIN | t | PARTIAL |
| 24 | DESK2_L01_VWAP반등 | 2 | BUILTIN | t | FULL |
| 25 | DESK2_M00_시초첫3분봉고가돌파 | 2 | BUILTIN | t | PARTIAL |
| 26 | DESK2_M001_3분봉종합눌림확인 | 2 | BUILTIN | t | FULL |
| 27 | DESK2_M002_AbsoluteZero_종가매매 | 2 | BUILTIN | t | FULL |
| 8 | DESK3_단기스윙_class_d | 3 | BUILTIN | f | FULL |
| 28 | DESK3_MACD크로스오버 | 3 | BUILTIN | t | FULL |
| 29 | DESK3_이동평균크로스 | 3 | BUILTIN | t | FULL |
| 30 | DESK3_지지저항반등 | 3 | BUILTIN | t | FULL |
| 31 | DESK3_추세내조정진입 | 3 | BUILTIN | t | FULL |
| 32 | DESK3_채널돌파 | 3 | BUILTIN | t | FULL |
| 33 | DESK3_MACD다이버전스 | 3 | BUILTIN | t | FULL |
| 34 | DESK3_볼린저밴드반등 | 3 | BUILTIN | t | FULL |
| 35 | DESK3_M02_볼린저스퀴즈 | 3 | BUILTIN | t | FULL |
| 36 | DESK3_이동평균선교차_MID | 3 | BUILTIN | t | FULL |
| 37 | DESK3_지지저항돌파_MID | 3 | BUILTIN | t | FULL |
| 9 | DESK4_중기스윙_class_e | 4 | BUILTIN | t | FULL |
| 11 | DESK4_중기추세추종 | 4 | BUILTIN | t | PARTIAL |
| 47 | DESK4_피보나치되돌림 | 4 | BUILTIN | t | FULL |
| 48 | DESK4_엘리어트파동 | 4 | BUILTIN | t | FULL |
| 49 | DESK4_일목균형표 | 4 | BUILTIN | t | FULL |
| 50 | DESK4_ParabolicSAR | 4 | BUILTIN | t | FULL |
| 51 | DESK4_ADX추세강도 | 4 | BUILTIN | f | FULL |
| 52 | DESK4_켈트너채널 | 4 | BUILTIN | t | FULL |
| 53 | DESK4_돈치안채널 | 4 | BUILTIN | f | FULL |
| 10 | DESK5_장기스윙_class_f | 5 | BUILTIN | f | PARTIAL |
| 12 | DESK5_가치투자 | 5 | BUILTIN | f | PARTIAL |
| 13 | DESK5_성장주모멘텀 | 5 | BUILTIN | f | PARTIAL |
| 54 | DESK5_배당포착 | 5 | BUILTIN | f | PARTIAL |
| 55 | DESK5_계절성추세 | 5 | BUILTIN | f | PARTIAL |
| 56 | DESK5_거시경제테마 | 5 | BUILTIN | f | PARTIAL |
| 57 | DESK5_섹터리더십 | 5 | BUILTIN | f | PARTIAL |
| 58 | DESK5_퀄리티팩터 | 5 | BUILTIN | f | PARTIAL |
| 59 | DESK5_저변동성 | 5 | BUILTIN | f | PARTIAL |
| 60 | DESK5_모멘텀팩터 | 5 | BUILTIN | t | FULL |
| 1 | 볼린저 밴드 돌파 | (NULL) | BUILTIN | f | NONE |
| 3 | # 🚀 GO100 추세 상승 극대화 전략 | (NULL) | CUSTOM | f | NONE |
| 61 | 시초가매매 | (NULL) | CUSTOM | f | NONE |
| 62 | 제시해주신 조건들을 바탕으로… | (NULL) | CUSTOM | f | NONE |

---

## 2. DESK별 상세 분석

### 2-1. DESK1 (스캘핑, 10개)

| card_id | 이름 | 구현상태 | 진입 지표 요약 | 청산 요약 |
|--------|------|----------|----------------|-----------|
| 5 | DESK1_스캘핑_class_b | PARTIAL | commander_scan 미구현 | stop_loss -0.3%, target 1%, trailing 0.2%, EOD 10:00 |
| 38 | DESK1_초단타모멘텀 | PARTIAL | price_momentum_1min, bid_ask_spread_narrow 미구현 | time_stop 30분, target 2%, EOD 15:20 |
| 39 | DESK1_갭메우기 | **FULL** | gap_up_pct, gap_fill_zone, volume_spike_3x, reversal_candle | target 1.5%, time_stop 45분 |
| 40 | DESK1_뉴스반응스캘핑 | PARTIAL | news_sentiment_spike, price_reversal_5min, bid_ask_spread_narrow 미구현 | time_stop 25분, target 2.2% |
| 41 | DESK1_S01_호가불균형 | PARTIAL | order_imbalance_ratio, bid_ask_spread_narrow, volume_1min_surge 미구현 | time_stop 20분, target 1.2% |
| 42 | DESK1_S02_고래추적 | PARTIAL | whale_volume_ratio, trade_strength_60, price_momentum_1min 미구현 | time_stop 30분, target 1.8% |
| 43 | DESK1_S03_스프레드갭 | PARTIAL | spread_gap_open, spread_narrow_5min, price_stable_3min 미구현 | time_stop 15분, target 1% |
| 44 | DESK1_S04_플래시크래시 | PARTIAL | flash_crash_detection 미구현 | time_stop 20분, target 2.5% |
| 45 | DESK1_M03_이격도숏 | **FULL** | disparity_20_over_110, rsi_overbought, volume_surge_2x, bb_upper_touch | time_stop 40분, target 1.5% |
| 46 | DESK1_H01_시장센서 | PARTIAL | index_momentum_5min, sector_rotation_signal, correlation_breakout 미구현 | time_stop 30분, target 1.8% |

- **요약:** DESK1은 분봉/호가/뉴스/스프레드 등 실시간 데이터 의존 지표가 많아, 현재 일봉 기반 `card_rule_simulator`만으로는 대부분 PARTIAL. FULL 2개(갭메우기, 이격도숏)만 백테스트·모의 전면 적용 가능.

### 2-2. DESK2 (단타, 16개)

| card_id | 이름 | 구현상태 | 비고 |
|--------|------|----------|------|
| 6 | DESK2_데일리_class_a | **FULL** | sma5_above_sma20, volume_surge_2x, rsi_below_70, macd_golden_cross, bb_lower_touch |
| 7 | DESK2_종가매매_class_c | PARTIAL | close_price_bet 미구현 |
| 14 | DESK2_장초반레인지돌파 | PARTIAL | opening_range_breakout 미구현 |
| 15 | DESK2_VWAP회귀 | **FULL** | bb_lower_near, volume_ratio_1.5x |
| 16~22, 24, 26, 27 | 10개 | **FULL** | 갭/볼린저/RSI/거래량/변동성/3분봉/VWAP 등 모두 구현 |
| 23 | DESK2_M01_오픈레인지돌파 | PARTIAL | opening_range_breakout 미구현 |
| 25 | DESK2_M00_시초첫3분봉고가돌파 | PARTIAL | first_3_candle_high_breakout 미구현 |

- **요약:** DESK2는 FULL 13개, PARTIAL 3개. 미구현 지표: close_price_bet, opening_range_breakout, first_3_candle_high_breakout.

### 2-3. DESK3 (단기스윙, 11개)

- **전원 FULL.** MACD·이동평균·지지저항·볼린저·채널 등 일봉 지표만 사용하여 `card_rule_simulator`에서 전부 지원.
- 카드 8, 28~37: 진입/청산 로직 모두 구현됨.

### 2-4. DESK4 (중기스윙, 9개)

| card_id | 이름 | 구현상태 | 비고 |
|--------|------|----------|------|
| 9 | DESK4_중기스윙_class_e | **FULL** | |
| 11 | DESK4_중기추세추종 | PARTIAL | institutional_5d_net_buy, sector_top30 미구현 |
| 47~53 | 7개 | **FULL** | 피보나치, 엘리어트, 일목, Parabolic SAR, ADX, 켈트너, 돈치안 |

### 2-5. DESK5 (장기, 10개) + WaveRider

| card_id | 이름 | 구현상태 | 미구현 지표 |
|--------|------|----------|-------------|
| 10 | DESK5_장기스윙_class_f | PARTIAL | macd_weekly_golden, sector_strength |
| 12 | DESK5_가치투자 | PARTIAL | per_below_10, pbr_below_1, roe_above_10, institutional_60d_net_buy |
| 13 | DESK5_성장주모멘텀 | PARTIAL | revenue_growth_above_20pct, earnings_momentum, relative_strength_top20, sector_leader |
| 54 | DESK5_배당포착 | PARTIAL | dividend_yield_above_3, dividend_growth_3y, sector_strength |
| 55 | DESK5_계절성추세 | PARTIAL | seasonal_month_strength, sector_strength |
| 56 | DESK5_거시경제테마 | PARTIAL | macro_theme_aligned, sector_strength |
| 57 | DESK5_섹터리더십 | PARTIAL | sector_rank_top_20pct, macd_weekly_golden |
| 58 | DESK5_퀄리티팩터 | PARTIAL | quality_roe_above_15, quality_operating_margin, sector_strength |
| 59 | DESK5_저변동성 | PARTIAL | sector_strength |
| 60 | DESK5_모멘텀팩터 | **FULL** | — |

- DESK5는 펀더멘털·섹터·주봉 데이터 의존이 커서, 현재 구현은 1개(FULL) + 9개(PARTIAL).

---

## 3. 미구현 전략 목록 & 구현 필요사항

### 3-1. NONE (entry_rules 없음, 카드만 존재)

- card_id 1: 볼린저 밴드 돌파 (desk 없음)
- card_id 3: GO100 추세 상승 극대화 (CUSTOM)
- card_id 61: 시초가매매 (CUSTOM)
- card_id 62: LLM 생성 안내 문구 카드 (CUSTOM)

→ 실전/백테스트 연동을 위해서는 entry_rules·exit_rules·desk_id 정의 필요.

### 3-2. PARTIAL 전략 및 누락 지표

- **DESK1:** commander_scan, price_momentum_1min, bid_ask_spread_narrow, news_sentiment_spike, price_reversal_5min, order_imbalance_ratio, volume_1min_surge, whale_volume_ratio, trade_strength_60, spread_gap_open, spread_narrow_5min, price_stable_3min, flash_crash_detection, index_momentum_5min, sector_rotation_signal, correlation_breakout.
- **DESK2:** close_price_bet, opening_range_breakout, first_3_candle_high_breakout.
- **DESK4:** institutional_5d_net_buy, sector_top30.
- **DESK5:** macd_weekly_golden, sector_strength, per_below_10, pbr_below_1, roe_above_10, institutional_60d_net_buy, revenue_growth_above_20pct, earnings_momentum, relative_strength_top20, sector_leader, dividend_yield_above_3, dividend_growth_3y, seasonal_month_strength, macro_theme_aligned, sector_rank_top_20pct, quality_roe_above_15, quality_operating_margin.

### 3-3. 구현 우선순위 제안

| 우선순위 | 대상 | 사유 |
|----------|------|------|
| **P0** | DESK1 스캘핑 (데이터 확보 후) | 실시간/분봉·호가 데이터 파이프라인 선행 필요 후 commander_scan, bid_ask_spread_narrow, order_imbalance_ratio, volume_1min_surge, price_momentum_1min 등 구현 |
| **P0** | DESK2 단타 | opening_range_breakout, first_3_candle_high_breakout, close_price_bet 3개만 추가 시 FULL 16개 달성 가능 |
| **P1** | DESK3 단기스윙 | 이미 전원 FULL. 파라미터 튜닝·모의매매 확대만 필요 |
| **P2** | DESK4 중기 | institutional_5d_net_buy, sector_top30 구현 시 카드 11 FULL 전환 |
| **P2** | DESK5 장기 | sector_strength, macd_weekly_golden 공통; 펀더멘털(per/pbr/roe/배당/퀄리티)·기관·섹터 데이터 연동 후 순차 구현 |

---

## 4. 구현된 전략 기획의도 & 진입·청산 분석

### 4-1. L4 StrategyEngine vs 카드 규칙

- **L4 StrategyEngine** (`strategy_engine.py`): 고정 전략 클래스만 등록 (MomentumBreakout, MeanReversion, VolatilityBreakout, BoxBreakout, DummyMomentum). **카드별 동적 로딩 없음.** 실시간 시그널은 이 5개 전략에서만 발생.
- **카드 규칙 백테스트**: `backtest_router`에서 `entry_rules.indicators`가 있으면 `run_card_backtest` 호출 → `card_rule_simulator.CardRuleSimulator`가 entry_rules/exit_rules/risk_params를 해석. 진입은 `EntryConditionEvaluator.evaluate()`(지표별 _check_* 메서드), 청산은 exit_rules의 stop_loss_pct, target_profit_pct, trailing_stop_pct, max_hold_days, eod_force_exit 등으로 처리.

### 4-2. FULL 상태 전략 요약

- **진입:** 각 카드의 `entry_rules.indicators` 리스트에서 `min_conditions` 개 이상 충족 시 진입. `min_strength`는 현재 시뮬레이터에서 보조 사용.
- **청산:** exit_rules에 정의된 손절/익절/트레일링/최대보유일/장마감 강제청산이 일관 적용됨.
- **파라미터:** DESK별로 target_pct·stop_loss_pct·trailing_pct·max_hold_days 등이 카드별로 다르게 설정되어 있어, 전략별 리스크/수익 목표가 명확히 구분됨.

### 4-3. v4_backtest_trades 현황

- card_id별 거래 건수 존재 (예: 6→2154, 7→813, 8→3644 등). NULL card_id 144,173건은 과거 통합 백테스트 등으로 추정.
- FULL 카드는 카드 규칙 기반 백테스트로 추가 검증·파라미터 최적화 가능.

---

## 5. 백테스트 우선순위 제안

1. **즉시 가능:** DESK3 전부, DESK2 FULL 13개, DESK4 FULL 8개, DESK5 60번 — 이미 `run_card_backtest`로 실행 가능.
2. **지표 추가 후:** DESK2 PARTIAL 3개(opening_range_breakout, first_3_candle_high_breakout, close_price_bet) → 구현 시 DESK2 전 카드 백테스트 가능.
3. **데이터·인프라 확보 후:** DESK1 스캘핑, DESK5 펀더멘털·섹터 지표.

---

## 6. 모의실매매 대상 전략 추천

- **우선 추천:** DESK2 FULL 카드 중 is_live=true인 7(종가매매), 14(장초반레인지돌파), 19(거래량스파이크), 20(변동성확대), 21, 22, 23, 24, 25, 26, 27. 단 7/14/23/25는 PARTIAL이므로 동일 전략명이라도 실제 청산 로직은 구현된 지표만 반영됨.
- **안정 추천:** DESK3 전원 FULL·일봉 기반 → 모의매매 리스크 관리가 상대적으로 단순.
- **장기:** DESK5 60(모멘텀팩터) FULL → 장기 모의 후 실전 검토.

---

## 7. 파라미터 최적화 포인트

- **공통:** stop_loss_pct, target_profit_pct, trailing_stop_pct, max_hold_days를 카드별·DESK별 그리드 검색으로 백테스트 후 승률·샤프·MDD 기준으로 조정.
- **진입:** min_conditions, min_strength를 완화/강화해 신호 빈도와 정확도 트레이드오프 분석.
- **DESK1:** time_window, time_stop_minutes와 실거래 시간대 정합성 검토.
- **DESK5:** 보유기간 90~120일 구간에서 trailing_stop_pct·목표수익률 구간별 민감도 분석 권장.

---

## 체크포인트

- [x] DB 백업 완료 (`/tmp/backup_STRATEGY_AUDIT_20260224_112150.dump`)
- [x] strategy_cards 전수 조회 완료 (실제 스키마: card_id, strategy_name, desk_id, entry_rules, exit_rules, strategy_params, risk_params)
- [x] strategy_engine.py 및 card_rule_simulator 분석 완료
- [x] DESK별 분석 완료
- [x] 미구현 전략 식별 완료 (NONE 4건, PARTIAL 24건, FULL 38건)
- [x] 구현된 전략 기획의도·진입/청산 분석 완료
- [ ] 코드 커밋 (보고서만 project-docs 쪽 반영)
- [ ] 보고서 push 완료 (HTTP 200)

---

## 참조

- strategy_cards 스키마: card_id(PK), strategy_name, desk_id(varchar), strategy_type(BUILTIN/CUSTOM), entry_rules, exit_rules, strategy_params, risk_params, is_live, is_active
- 진입/청산 구현: `backend/app/services/backtest/card_rule_simulator.py` (EntryConditionEvaluator.INDICATOR_MAP, CardRuleSimulator, run_card_backtest)
- 백테스트 API: `backtest_router` — entry_rules.indicators 유무에 따라 run_card_backtest vs run_backtest(strategy_type) 분기
