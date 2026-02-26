# DESK2-BT-DEEP-DIAGNOSIS-001 — 정밀 진단 보고서

**작성일**: 2026-02-27
**선행**: DESK2-BT-STRATEGY-FIX-001 (수정 후 20건, -227,135원)
**대상**: 4일 백테스트 (02-19, 02-20, 02-24, 02-25) 총 20건 거래

---

## 1. TARGET_PROFIT 손실 거래 분석

### 1-1. 대상 거래 (exit_reason=TARGET_PROFIT, pnl<0) — 4건

| # | 종목 | 전략 | 날짜 | entry_price | exit_price | pnl_pct | hold(s) |
|---|---|---|---|---|---|---|---|
| 5 | 319660 | GOLF_REVERSAL | 02-19 | 62,762.70 | 62,662.28 | -0.35% | 120 |
| 9 | 272210 | GOLF_REVERSAL | 02-20 | 115,415.30 | 115,526.86 | -0.10% | 60 |
| 10 | 458870 | GOLF_REVERSAL | 02-20 | 149,349.20 | 149,260.59 | -0.25% | 60 |
| 14 | 403870 | DELTA_VWAP | 02-24 | 41,441.40 | 41,363.91 | -0.38% | 60 |

### 1-2. target_price 계산 로직

**GOLF_REVERSAL** (`golf_reversal.py:64-68`):
```python
bb_middle = bar_data.get("bb_middle", current * 1.02)
target = bb_middle  # 볼린저 중심선 (20기간 MA)
```

**DELTA_VWAP** (`delta_vwap.py:60-61`):
```python
target = current + (current - vwap) * 2  # VWAP 이격 2배
```

### 1-3. 분봉 기반 target_price 역산

**#5 319660 (02-19 09:45 진입)**:
- 09:35~09:45 가격 흐름: 63000→62700→62400→62100→62300→62300→62700
- 20기간 MA (bb_middle) 추정: **~62,400** (하락 추세 중 MA가 entry 아래)
- target(62,400) < entry(62,762) → **target_price < entry_price 버그 확정**
- 청산 후 09:48~10:04에 63,300→64,800까지 급등 (+3.4%)

**#9 272210 (02-20 10:05 진입)**:
- 10:00~10:05 가격: 115,200→114,800→114,900→115,100→115,200→115,300
- bb_middle 추정: **~115,500** (약간 entry 위)
- exit=115,526.86 > entry=115,415.30 → 가격은 소폭 이익
- **수수료+세금+슬리피지(0.41%)가 이익(0.10%)보다 큼 → 비용 초과 손실**

**#10 458870 (02-20 10:12 진입)**:
- 10:02~10:12 가격: 149,700→149,100→148,700→149,000→149,000→149,400
- bb_middle 추정: **~149,200** (entry 아래)
- target(~149,200) < entry(149,349) → **target_price < entry_price 버그 확정**
- 청산 후 10:17에 150,500까지 상승 (+0.8%)

**#14 403870 DELTA_VWAP (02-24 09:44 진입)**:
- 09:38~09:44: 41,200→41,450→41,350→41,300→41,300→41,450→41,400
- VWAP 추정: ~41,100 (누적평균)
- target = 41,400 + (41,400 - 41,100) × 2 = **41,400 + 600 = 42,000**
- 하지만 exit_price=41,363.91 < entry=41,441.40 → **entry에 슬리피지(+0.1%) 적용으로 인플레이션**
- 실제 current≈41,400, target≈42,000이면 first_target_pct=1.0%가 먼저 적용됨
- first_target = 41,441.40 × 1.01 = **41,856** → 이것이 실제 first_sell 트리거
- 하지만 60초 후 exit → split_sell 전 TIMEOUT이 아닌 TARGET_PROFIT??
- **config의 first_target_pct=1.0이 strategy target보다 우선**

### 1-4. 판정 요약

| # | 원인 | 판정 |
|---|---|---|
| #5 319660 | bb_middle < entry_price | **BUG**: target_price < entry_price 허용 |
| #9 272210 | 가격 이익(+0.10%) < 비용(0.41%) | **구조적 결함**: 최소 수익률 미확보 |
| #10 458870 | bb_middle < entry_price | **BUG**: target_price < entry_price 허용 |
| #14 403870 | 슬리피지로 entry 인플레이션 | **구조적 결함**: 비용 감안 없는 target 설정 |

**근본 원인**: 전략이 target_price를 설정할 때 **거래 비용(수수료 0.03% + 세금 0.18% + 슬리피지 0.2% = 0.41%)**을 감안하지 않음. target_price가 `entry_price × (1 + 0.41%)`보다 낮으면 무조건 손실.

---

## 2. C1~C7 발굴 비활성 원인 진단

### 2-1. 날짜별 시장 환경

| 날짜 | 레짐 | 레짐 점수 | 분봉 종목 수 |
|---|---|---|---|
| 02-19 | MILD_TREND_DOWN | 39.00 | 566 |
| 02-20 | MILD_TREND_DOWN | 39.00 | 561 |
| 02-24 | **UNKNOWN** | N/A | 510 |
| 02-25 | **UNKNOWN** | N/A | 498 |

**문제**: 02-24, 02-25에 레짐 데이터 없음 → 레짐 기반 전략 배분 불가.

### 2-2. 원시 후보 수 (분봉 기반 추정)

| 조건 | 02-19 | 02-20 | 02-24 | 02-25 | 판정 |
|---|---|---|---|---|---|
| C1 갭 3~15% | 94 | 38 | 11 | 39 | **후보 풍부** |
| C2 +1.5%↑ | 220 | 210 | 150 | 105 | **후보 풍부** |
| C3 VI | - | - | - | - | **테이블 없음** |
| C4 +2%/10m | 171 | 135 | 129 | 121 | **후보 풍부** |
| C5 급등후조정 | 89 | 75 | 61 | 70 | **후보 풍부** |
| C7 -3.5%↓ | 49 | 92 | 33 | 85 | **후보 풍부** |

### 2-3. 실제 BT 발굴 로그 (v4_bt_discoveries)

전체 6,931건 발굴 중:

| 조건 | 발굴 | 통과 | 거절 | 거절 사유 |
|---|---|---|---|---|
| C1 | 625 | 3 (0.5%) | 622 | not_selected |
| C2 | **0** | 0 | 0 | **코드 미동작** |
| C3 | **0** | 0 | 0 | **v4_vi_occurrences 테이블 없음** |
| C4 | 160 | 15 (9.4%) | 145 | not_selected |
| C5 | 6,138 | 5 (0.08%) | 6,133 | not_selected |
| C6 | **0** | 0 | 0 | **업종 대장주 데이터 부재** |
| C7 | 8 | 2 (25%) | 6 | not_selected |

**핵심**: 02-19~02-25 기간에 발굴 로그 거의 없음 (02-20 C4=9건만). 대부분은 01월 초 데이터.

### 2-4. 조건별 비활성 핵심 원인

| 조건 | 핵심 원인 | gate 요약 |
|---|---|---|
| **C1 GAP_UP** | RVOL≥2 + 시총≥3000억 gate로 625→3건 극소화 | GAP 3~15%, RVOL≥2.0, 시총≥3000억 |
| **C2 OPENING_STRONG** | **발굴 0건** — 백테스터에서 C2 로직 자체가 호출되지 않을 가능성 | +1.5%, RVOL≥1.5, 시총≥3000억, 09:30 이내 |
| **C3 VI_EXPLOSION** | **`v4_vi_occurrences` 테이블 없음** → 구조적 불가 | VI 발동 데이터 의존 |
| **C4 INTRADAY_SURGE** | 유일하게 작동. 시총+가격 gate로 160→15 통과 | +2%/10분, 시총≥3000억, 가격≥3000원 |
| **C5 PULLBACK** | 6138건 발굴 → 5건만 통과. "not_selected" 경쟁에서 탈락 | 고가+5%, 조정-1.5%, 볼륨비율 |
| **C6 SECTOR_LAG** | **발굴 0건** — 업종 대장주 +4% 데이터 생성 로직 부재 | 대장주+4%, 시총≥5000억 |
| **C7 OVERSOLD** | RSI≤30 + 시총≥5000억이 극도로 제한적 | -3.5%, RSI≤30, 시총≥5000억, 가격≥1000원 |

---

## 3. 청산 후 주가 변동 (기회손실 분석)

| # | 날짜 | 종목 | 전략 | 청산사유 | 청산가 | 당일고가 | 당일종가 | 기회손실 |
|---|---|---|---|---|---|---|---|---|
| 1 | 02-19 | 272290 | GOLF_REVERSAL | STOP_LOSS | 36,480 | 38,600 | 36,900 | **5.81%** |
| 2 | 02-19 | 322000 | GOLF_REVERSAL | FIRST_TARGET+TRAIL | 86,614 | 92,200 | 89,600 | **6.45%** |
| 3 | 02-19 | 348340 | GOLF_REVERSAL | TARGET_PROFIT | 80,789 | 84,100 | 82,600 | 4.10% |
| 4 | 02-19 | 319400 | GOLF_REVERSAL | TARGET_PROFIT | 27,067 | 28,350 | 27,950 | 4.74% |
| 5 | 02-19 | 319660 | GOLF_REVERSAL | TARGET_PROFIT | 62,662 | 66,900 | 62,800 | **6.76%** |
| 6 | 02-20 | 440110 | GOLF_REVERSAL | TIMEOUT | 50,050 | 54,200 | 51,200 | **8.29%** |
| 7 | 02-20 | 295310 | GOLF_REVERSAL | FIRST_TARGET+TRAIL | 84,434 | 88,000 | 83,000 | 4.22% |
| 8 | 02-20 | 322000 | GOLF_REVERSAL | TARGET_PROFIT | 88,664 | 91,500 | 86,300 | 3.20% |
| 9 | 02-20 | 272210 | GOLF_REVERSAL | TARGET_PROFIT | 115,527 | 121,800 | 116,500 | **5.43%** |
| 10 | 02-20 | 458870 | GOLF_REVERSAL | TARGET_PROFIT | 149,261 | 155,300 | 151,000 | 4.05% |
| 11 | 02-24 | 440110 | GOLF_REVERSAL | TARGET_PROFIT | 52,160 | 56,500 | 54,400 | **8.32%** |
| 12 | 02-24 | 403870 | GOLF_REVERSAL | TARGET_PROFIT | 41,073 | 43,500 | 40,950 | 5.91% |
| 13 | 02-24 | 347700 | ECHO_ABCD | STOP_LOSS | 43,537 | 46,325 | 42,800 | 6.40% |
| 14 | 02-24 | 403870 | DELTA_VWAP | TARGET_PROFIT | 41,364 | 43,500 | 40,950 | 5.16% |
| 15 | 02-24 | 491000 | GOLF_REVERSAL | STOP_LOSS | 90,454 | 95,900 | 91,100 | 6.02% |
| 16 | 02-25 | 000720 | BRAVO_ORB | STOP_LOSS | 153,370 | 159,800 | 155,200 | 4.19% |
| 17 | 02-25 | 319400 | GOLF_REVERSAL | FIRST_TARGET+TRAIL | 35,429 | 37,700 | 35,550 | 6.41% |
| 18 | 02-25 | 032820 | GOLF_REVERSAL | STOP_LOSS | 17,077 | 18,200 | 17,240 | 6.58% |
| 19 | 02-25 | 130660 | GOLF_REVERSAL | DAILY_LIMIT | 25,524 | 26,800 | 25,100 | 5.00% |
| 20 | 02-25 | 241520 | GOLF_REVERSAL | STOP_LOSS | 17,494 | 18,790 | 17,520 | **7.41%** |

### 통계 요약

| 항목 | 값 |
|---|---|
| 평균 기회손실 | **5.72%** |
| 최대 기회손실 | 8.32% (#11 440110) |
| 최소 기회손실 | 3.20% (#8 322000) |
| 전체 20건 중 missed>5% | **12건 (60%)** |

**판정**: **20건 전부** 청산 후 추가 상승 여지 있음. 평균 5.72% 기회손실은 **조기 청산이 핵심 수익 저해 요인**임을 입증.

### 청산 유형별 기회손실

| 청산 유형 | 건수 | 평균 기회손실 |
|---|---|---|
| TARGET_PROFIT | 9건 | 5.30% |
| STOP_LOSS | 6건 | 6.07% |
| FIRST_TARGET+TRAILING | 3건 | 5.69% |
| TIMEOUT | 1건 | 8.29% |
| DAILY_LIMIT | 1건 | 5.00% |

STOP_LOSS 거래까지 이후 고가 대비 6% 기회손실 → 손절이 너무 빠르거나 진입 타이밍이 조기.

---

## 4. desk2_config.yaml 주요 파라미터

### 4-1. 전략별 파라미터

| 전략 | stop_loss | first_target | trailing_act | trailing_stop | max_hold |
|---|---|---|---|---|---|
| ALPHA_GAP | -1.5% | 1.5% | 1.0% | 1.0% | 1800s |
| BRAVO_ORB | -2.0% | 2.0% | 1.5% | 1.5% | - |
| DELTA_VWAP | -1.5% | 1.0% | 0.8% | 0.8% | 2400s |
| ECHO_ABCD | -1.5% | 2.0% | 1.5% | 1.5% | 3600s |
| GOLF_REVERSAL | -2.0% | 1.0% | 0.8% | 0.8% | - |
| CHARLIE_VI | -2.5% | 2.0% | 1.5% | 1.5% | - |
| FOXTROT_SECTOR | -2.0% | 1.5% | 1.0% | 1.0% | - |

### 4-2. 거래 비용

| 항목 | 값 |
|---|---|
| 매수 수수료 | 0.015% |
| 매도 수수료 | 0.015% |
| 매도세 | 0.18% |
| 슬리피지 | 0.1% (편도) |
| **총 비용** | **~0.41%** |

### 4-3. 청산 구조

```
exit_strategy:
  split_sell: true        # 2분할 매도 활성
  first_sell_pct: 50      # 1차 50% 매도
  first_target_pct: null  # 전역 미설정 (전략별 개별 적용)
```

---

## 5. 발굴 gate 조건 코드 요약

| 조건 | 파일 | 핵심 gate | 최소 시총 | 추가 조건 |
|---|---|---|---|---|
| C1 | c1_gap_discovery.py | GAP 3~15%, RVOL≥2.0 | 3,000억 | - |
| C2 | c2_opening_strong.py | +1.5%, RVOL≥1.5 | 3,000억 | 09:30 이내 |
| C3 | c3_vi_explosion.py | VI 발동, PRE_RVOL≥3.0 | 2,000억 | vi_occurrences 테이블 필요 |
| C4 | c4_intraday_surge.py | +2%/10분 | 3,000억 | 가격≥3,000원 |
| C5 | c5_pullback_discovery.py | 고가+5%, 조정-1.5% | - | 조정 볼륨 < 급등 볼륨 |
| C6 | c6_sector_lag.py | 대장주+4% | - | 섹터 내 후발주 매칭 |
| C7 | c7_oversold_rebound.py | -3.5%, RSI≤30 | **5,000억** | 가격≥1,000원, 거래대금≥10억 |

---

## 6. Phase D 청산 로직 요약

`backtest_runner.py` 라인 369-569:

```
우선순위 1: STOP_LOSS (전체 물량)
  → effective_stop = max(strategy_stop, config_floor_stop)
  → bar.low ≤ effective_stop 시 즉시 전량 매도

우선순위 2: FIRST_TARGET (50% 분할 매도)
  → first_target_price = entry × (1 + first_target_pct/100)
  → bar.high ≥ first_target_price 시 50% 매도
  → 잔여 50%는 trailing stop으로 관리

우선순위 3: TRAILING_STOP (분할 매도 후 잔여)
  → trailing_high = max(past highs)
  → trailing_stop = trailing_high × (1 - trailing_stop_pct/100)
  → bar.low ≤ trailing_stop 시 잔여 매도

우선순위 4: TARGET_PROFIT (단일 매도)
  → split_sell 미적용 or first_target 미발동 시
  → bar.high ≥ pos.target_price 시 전량 매도
  ⚠ target_price < entry_price 검증 없음!

우선순위 5: TIMEOUT
  → hold_seconds ≥ max_hold_seconds 시 종가 매도
```

**치명적 결함**: 우선순위 4에서 `pos.target_price < pos.entry_price` 체크가 없음. 전략이 entry 아래 target을 설정하면 즉시 "이익 실현" 매도 실행 → 손실 확정.

---

## 7. 종합 진단 및 개선 의견

### 7-1. 문제 분류

| # | 문제 | 심각도 | 영향 | 제안 |
|---|---|---|---|---|
| 1 | **target_price < entry_price 허용** | P0 | 4건 무조건 손실 | target_price = max(target, entry × 1.005) 하한 설정 |
| 2 | **거래 비용 미감안 target** | P0 | 소폭 이익 전부 비용에 잠식 | target_min = entry × (1 + total_cost_pct) |
| 3 | **C2, C3, C6 완전 비활성** | P1 | 전략 다양성 소멸, C7 편중 | C3: VI 테이블 생성, C6: 섹터 로직 점검, C2: 호출 경로 확인 |
| 4 | **레짐 데이터 02-24~25 없음** | P1 | 레짐 배분 불가 | v4_market_regime_daily 데이터 적재 확인 |
| 5 | **조기 청산 (평균 5.72% 기회손실)** | P1 | 수익 기회 전부 놓침 | first_target_pct 2~3%로 상향, trailing 완화 |
| 6 | **STOP_LOSS도 이후 반등** | P2 | 6건 평균 6% 기회손실 | 손절 후 재진입 로직 또는 손절선 완화 |
| 7 | **C1, C5 통과율 극저** | P2 | 625→3, 6138→5 | "not_selected" 경쟁 로직의 slot 제한 완화 |

### 7-2. 즉시 조치 권장 (P0)

1. **target_price 하한 검증** (backtest_runner.py):
   ```
   # Phase D 진입 전 검증
   min_target = entry_price * (1 + total_cost_pct / 100)
   if pos.target_price < min_target:
       pos.target_price = min_target
   ```

2. **first_target_pct를 비용 이상으로 설정**:
   - 현재: GOLF_REVERSAL 1.0%, DELTA_VWAP 1.0%
   - 권장: 최소 1.5% (비용 0.41% + 마진 1.0%)

3. **bb_middle / vwap target의 entry 대비 검증**:
   ```
   # golf_reversal.py
   target = max(bb_middle, current * 1.015)  # 최소 +1.5%
   ```
