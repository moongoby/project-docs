# DESK-STRATEGY-OPTIMIZATION-RESEARCH 보고

**작업명:** DESK-STRATEGY-OPTIMIZATION-RESEARCH (DESK × 전략 × 종목 × 타이밍 원천 최적화 연구)  
**서버:** 211.188.51.113  
**경로:** /root/kis-autotrade-v4  
**보고일:** 2026-02-22  

---

## 사전 확인 결과

| 항목 | 기준 | 결과 |
|------|------|------|
| strategy_cards COUNT | 59 | **59** ✓ |
| v4_positions OPEN | 5 | **5** ✓ |
| kis-v41-api | active | **active (running)** ✓ |
| kis-v41-monitor | active | **active (running)** ✓ |
| kis-v41-scheduler | active | **active** ✓ |
| 디스크 / | - | 46% 사용 (52G 가용) ✓ |

---

## [PART A: 전략별 실증 성과]

**세션 61** ([DB] V2_BT-TUNE-DESK2-3M, DESK2 일봉 3M):

| 구분 | 전략명 | trades | avg_pnl | win_rate | best_trade | worst_trade |
|------|--------|--------|---------|----------|------------|-------------|
| **최고** | DESK3_단기스윙_class_d | 143 | **2.55** | 31.5 | 49.88 | -7.49 |
| | DESK2_종가매매_class_c | 14 | 2.38 | 57.1 | 26.77 | -8.57 |
| | DESK2_S05_거래량점화 | 28 | 1.95 | 42.9 | 28.31 | -12.77 |
| **최악** | DESK2_D01_3분봉_20선눌림목 | 5 | **-1.07** | 60.0 | 0.36 | -5.37 |
| | DESK2_장초반레인지돌파 | 63 | -0.51 | 36.5 | 31.83 | -17.11 |

**세션 47** (DESK1 3M): 전략 정보 대부분 card_id 미연결로 **NULL** (trades 1,555, avg_pnl 1.77, win_rate 45.7).

**세션 62** ([DB] V2_BT-MIN-DESK2-2M, -23.25% 손실 구간) **손실 주도 전략:**

| 전략명 | trades | avg_pnl | win_rate | total_pnl_contribution |
|--------|--------|---------|----------|------------------------|
| **DESK2_변동성확대** | 706 | -0.22 | 32.6 | **-155.24** |
| DESK2_장초반레인지돌파 | 179 | -0.17 | 33.0 | -30.66 |
| DESK2_D01_3분봉_20선눌림목 | 31 | -0.35 | 32.3 | -10.70 |
| DESK2_S05_거래량점화 | 62 | -0.13 | 38.7 | -7.89 |
| DESK2_거래량스파이크 | 113 | -0.06 | 40.7 | -6.76 |

**요약:**  
- **최고 전략:** DESK3_단기스윙_class_d (avg_pnl 2.55, win_rate 31.5, trades 143)  
- **최악 전략:** DESK2_D01_3분봉_20선눌림목 (avg_pnl -1.07)  
- **세션62 손실 주도:** DESK2_변동성확대 (total_pnl_contribution -155.24)

---

## [PART B: 종목 × 전략 매칭]

**종목별 수익 TOP 5 (세션 61, 거래 3회 이상):**

| 종목코드 | 종목명 | trades | avg_pnl | win_rate |
|----------|--------|--------|---------|----------|
| 187660 | 현대ADM | 3 | 19.02 | 66.7 |
| 437730 | 삼현 | 3 | 11.45 | 66.7 |
| 058610 | 에스피지 | 3 | 11.36 | 100.0 |
| 065170 | 비엘팜텍 | 3 | 10.04 | 33.3 |
| 249420 | 일동제약 | 4 | 8.01 | 75.0 |

**종목×전략 최고 조합 TOP 5:**

| 종목 | 전략 | avg_pnl | trades |
|------|------|---------|--------|
| 비엘팜텍 | DESK3_단기스윙_class_d | 21.20 | 2 |
| 대한광통신 | DESK3_단기스윙_class_d | 17.87 | 2 |
| 원익홀딩스 | DESK2_거래량스파이크 | 12.13 | 2 |
| 에스피지 | DESK2_변동성확대 | 11.08 | 2 |
| 아이로보틱스 | DESK3_단기스윙_class_d | 11.04 | 2 |

**종목×전략 최악 조합 TOP 5:**

| 종목 | 전략 | avg_pnl | total_pnl |
|------|------|---------|-----------|
| 삼표시멘트 | DESK2_장초반레인지돌파 | -10.97 | -32.91 |
| 세아베스틸지주 | DESK2_변동성확대 | -8.21 | -16.43 |
| JW신약 | DESK2_변동성확대 | -6.42 | -12.83 |
| 대덕전자 | DESK2_변동성확대 | -5.75 | -11.49 |
| 한온시스템 | DESK2_장초반레인지돌파 | -5.52 | -11.03 |

**종목 특성(크기×변동성)별 수익:**

| size_group | vol_group | stocks | avg_pnl | total_trades |
|------------|-----------|--------|---------|--------------|
| 소형(5-10B) | 고변동(4%+) | 27 | **3.10** | 36 |
| 초소형(<5B) | 고변동(4%+) | 43 | 1.70 | 49 |
| 중형(10-50B) | 중변동(2-4%) | 9 | 1.44 | 12 |
| 대형(50B+) | 고변동(4%+) | 50 | 1.17 | 175 |
| 대형(50B+) | 중변동(2-4%) | 18 | 1.03 | 52 |
| 대형(50B+) | 저변동(<2%) | 6 | 0.31 | 13 |
| 중형(10-50B) | 고변동(4%+) | 91 | 0.08 | 152 |
| 소형(5-10B) | 중변동(2-4%) | 2 | 0.06 | 3 |
| **초소형(<5B)** | **중변동(2-4%)** | 11 | **-3.09** | 11 |

**요약:**  
- **최고 조합:** 비엘팜텍 × DESK3_단기스윙_class_d (avg_pnl 21.20)  
- **최악 조합:** 삼표시멘트 × DESK2_장초반레인지돌파 (avg_pnl -10.97)  
- **종목 특성:** 소형·고변동에서 평균 수익 최고(3.10); 초소형·중변동에서 최악(-3.09).

---

## [PART C: 타이밍 분석]

**진입 시간대:**  
- `v4_backtest_trades`에 **entry_time(또는 entry_datetime) 컬럼 없음**. 일별(entry_date)만 존재.  
- **결과:** 진입 시간대별 분석 **데이터 부족/스키마 불일치** → 생략.

**요일별 수익률 (세션 61):**

| weekday | dow | trades | avg_pnl | win_rate |
|---------|-----|--------|---------|----------|
| Thu | 4 | 104 | **1.91** | 42.3 |
| Fri | 5 | 106 | **1.66** | 47.2 |
| Mon | 1 | 99 | 0.73 | 42.4 |
| Wed | 3 | 95 | 0.43 | 34.7 |
| Tue | 2 | 99 | **0.03** | 40.4 |

**보유 기간별 (세션 47+61):**

| hold_period | trades | avg_pnl | win_rate | daily_alpha |
|-------------|--------|---------|----------|-------------|
| 4-7일 | 39 | **4.86** | 53.8 | 0.886 |
| 1-3일 | 1,040 | 2.95 | 45.4 | **1.920** |
| 8-14일 | 1 | 1.50 | 100.0 | 0.187 |
| 15-30일 | 3 | -0.18 | 33.3 | -0.008 |
| 당일(0일) | 975 | -0.02 | 43.5 | - |

**요약:**  
- **최적 진입 시간대:** 데이터 없음 (entry_time 미존재).  
- **최적 요일:** Thu (avg_pnl 1.91), Fri (1.66). **최악:** Tue (0.03).  
- **최적 보유 기간:** 4-7일(평균 수익 4.86), 1-3일(일일알파 1.920 최고).

---

## [PART D: DESK 시간축 분석]

**DESK별 종합 성과 (전 세션, SELL만):**

| desk | sessions | total_trades | avg_pnl | win_rate |
|------|----------|--------------|---------|----------|
| DESK5 | 1 | 37 | **5.82** | 59.5 |
| DESK3 | 4 | 1,324 | **3.52** | 42.9 |
| DESK4 | 1 | 136 | 2.37 | 47.1 |
| DESK1 | 1 | 1,555 | 1.77 | 45.7 |
| ALL/OTHER | 24 | 48,056 | 1.76 | 46.0 |
| DESK2 | 8 | 2,863 | **0.17** | 38.7 |

**동일 전략 DESK 간 성과 차이 (대표):**

- **DESK3_단기스윙_class_d:** DESK3 avg_pnl **3.29** (win 42.7) vs DESK2 **2.55** (win 31.5) → DESK3 배치 시 더 유리.  
- **DESK2_종가매매_class_c:** DESK2 **0.63** (43.4) vs OTHER -0.79 (32.5) → DESK2에서만 수익.  
- **DESK2_장초반레인지돌파:** OTHER 0.45 vs DESK2 **-0.17** → DESK2 배치 시 손실.  
- **DESK4_중기스윙_class_e:** DESK3 **4.07** > DESK4 2.66 > OTHER 2.95.

**DESK별 exit_rules 비교 (요약):**

- **stop_loss / take_profit / trailing_stop:** 전략 카드에는 **비어 있음**. (실제 동작은 백엔드 기본값 또는 stage_config 추정.)  
- **max_hold_days:**  
  - DESK1: 0~1일  
  - DESK2: 1~3일  
  - DESK3: 10일  
  - DESK4: 20~40일  
  - DESK5: 120일  
- **time_limit_minutes:** 전부 NULL.

---

## [PART E: Promotion 분석]

**인계했으면 추가 수익 가능했던 케이스:**  
- `v4_backtest_trades`에는 **진입가/청산가가 행 단위로 분리되어 있지 않음** (BUY/SELL 각각 price만 존재).  
- “청산 후 N일 보유 시 수익” 시뮬레이션(E1)에 필요한 **entry_price/exit_price 매칭 불가** → **해당 분석 생략**.

**현재 promotion 기준 (split_transfer_engine.py DESK_CONFIGS):**

| FROM→TO | min_profit_pct | 기타 조건 |
|---------|----------------|-----------|
| 1→2 | 0.5% | volume_ratio_min 1.5, macd_5min_bullish |
| 2→3 | 2.0% | above_ma20, institutional_buy_days 2 |
| 3→4 | 5.0% | min_hold_days 5, weekly_macd_golden, institutional_buy_days 5 |
| 4→5 | 8.0% | min_hold_days 15, monthly_trend_up, earnings_growth |
| 5 | - | promotion_target None (최상위) |

**실제 코드 (_meets_promotion_criteria):**  
- 현재는 **min_profit_pct**만 검사. above_ma20, institutional_buy_days 등은 **미구현** (항상 True로 통과 가능).

**개선 제안:**  
- 백테스트에서 “가상 인계” 구간(보유 5일/15일 등) 수익률 집계 테이블 또는 뷰 도입 후, min_profit_pct·min_hold_days 조합별 시뮬레이션.  
- promotion_criteria의 나머지 조건(above_ma20, institutional_buy_days 등) 구현 또는 조건 단순화(데이터 가용성에 맞춤).

---

## [PART F: entry_rules 분석]

**동일 indicators 사용 전략 (2건):**

| indicators | strategy_count | strategies |
|------------|----------------|------------|
| double_bottom_20d, rsi_rising, neckline_break | 2 | DESK3_볼린저밴드반등, DESK3_M02_볼린저스퀴즈 |
| three_consecutive_up, volume_increasing, close_above_prev_high, macd_above_signal_positive | 2 | DESK2_거래량스파이크, DESK2_S05_거래량점화 |

**차별화 부족 전략:**  
- DESK2_거래량스파이크 vs DESK2_S05_거래량점화: **entry_rules.indicators 동일**.  
- DESK3_볼린저밴드반등 vs DESK3_M02_볼린저스퀴즈: **entry_rules.indicators 동일**.  
- time_window, conditions, filters 등으로 구분되어 있는지는 카드별 추가 확인 필요.

---

## [PART G: Market Regime 분석]

**v4_market_regime_daily:**  
- 데이터 적고, **MILD_TREND_UP**만 존재 → BULL/BEAR/SIDEWAYS 구간 분석에는 **index_daily** 사용.

**KOSPI 5일 대비 구간별 (BULL/BEAR/SIDEWAYS) 수익률 (세션 47+61):**

| regime | trades | avg_pnl | win_rate |
|--------|--------|---------|----------|
| BEAR | 170 | **1.90** | 41.8 |
| SIDEWAYS | 1,828 | 1.52 | 44.6 |
| BULL | 29 | 0.91 | 41.4 |

**레짐×전략 (거래 5회 이상):**

- **BEAR:** NULL(2.30), DESK3_단기스윙_class_d(1.96), DESK2_변동성확대(1.76).  
- **SIDEWAYS:** DESK3_단기스윙_class_d(2.64), DESK2_S05_거래량점화(2.03), DESK2_종가매매_class_c(1.79); DESK2_변동성확대(-0.09), DESK2_장초반레인지돌파(-0.41).  
- **BULL:** 샘플 소수(29건), NULL 0.54.

**요약:**  
- **BEAR 시:** 전략별로 NULL·DESK3_단기스윙·DESK2_변동성확대가 상대적으로 양호.  
- **SIDEWAYS 시:** DESK3_단기스윙, DESK2_S05_거래량점화, DESK2_종가매매_class_c 유리; DESK2_변동성확대·장초반레인지돌파 부진.  
- **BULL 시:** 데이터 적어 통계적 결론 유보.

---

## [원천 최적화 프레임워크 제안]

1. **종목 선택 최적화**  
   - 소형(5–10B)·고변동(4%+) 구간에서 평균 수익 최고(3.10).  
   - 초소형·중변동 구간(-3.09)은 진입 제한 또는 전략 배제 검토.  
   - 종목×전략 최악 조합(삼표시멘트×장초반레인지돌파 등) 블랙리스트 또는 가중치 감소.

2. **전략 매칭 최적화**  
   - DESK3_단기스윙_class_d를 고수익 종목(비엘팜텍, 대한광통신 등)에 우선 매칭.  
   - DESK2_변동성확대는 세션62에서 손실 주도 → 분봉/단기 DESK2 구간에서 비중 축소 또는 조건 강화.  
   - DESK2_장초반레인지돌파·D01_3분봉_20선눌림목은 성과 부진 → 재검토 또는 OFF.

3. **타이밍 최적화**  
   - 요일: 목·금요일 진입 비중 확대, 화요일 축소 검토.  
   - 보유 기간: 1–7일 구간이 일일알파·평균 수익 모두 유리; 당일 청산(-0.02) 비중 감소.  
   - 진입 시간대 최적화를 위해 **entry_time(또는 entry_datetime)** 컬럼 추가 권장.

4. **DESK 배치 최적화**  
   - DESK2는 전 DESK 중 avg_pnl 최저(0.17) → 변동성확대·장초반레인지돌파 등 손실 전략 비중 조정.  
   - DESK3_단기스윙은 DESK3 배치 시 DESK2 대비 성과 우수 → DESK3 중심 배치 유지.  
   - DESK5(5.82), DESK3(3.52) 상위 → 단기 수익 극대화 시 DESK5·DESK3 파라미터 재조정 검토.

5. **Promotion 최적화**  
   - min_profit_pct·min_hold_days는 유지하되, 실제 DB/백테스트로 “가상 인계” 수익률 집계 후 임계값 튜닝.  
   - above_ma20, institutional_buy_days 등 조건은 데이터 확보 후 구현 또는 제거해 일관성 확보.

6. **시장 레짐 대응**  
   - BEAR/SIDEWAYS 구간: DESK3_단기스윙, DESK2_S05_거래량점화, DESK2_종가매매_class_c 비중 유지.  
   - SIDEWAYS에서 DESK2_변동성확대·장초반레인지돌파 비중 축소.  
   - v4_market_regime_daily 확충 시 레짐별 전략 스위칭 룰 도입 검토.

---

## 최종 확인

| 항목 | 값 |
|------|-----|
| strategy_cards COUNT | **59** ✓ |
| v4_positions OPEN | **5** ✓ |

---

**보고 끝.** (본 작업은 읽기 전용 연구이며, DB/파일 수정 없음.)
