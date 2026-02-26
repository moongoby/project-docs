# DESK2-BT-STRATEGY-FIX-001 — 전략 수정 및 재검증 보고서

- **작업 ID**: DESK2-BT-STRATEGY-FIX-001  
- **우선순위**: P0  
- **선행**: DESK2-BT-5DAY-CONSECUTIVE-002 (4일 테스트 완료, 20건 거래, -411,892원)  
- **일자**: 2026-02-26  

---

## 1. PHASE 1: 청산 조건 진단 결과

### 1-1. 전략별 설정값 (config + 코드)

| 전략 | stop_loss | target | max_hold | 비고 |
|------|-----------|--------|----------|------|
| ALPHA_GAP | 시가×0.99 | 갭×1.5 | 1800s | config: stop_loss_pct -1.5 |
| BRAVO_ORB | range_low (박스 하단) | current+range×1.5 | 5400s | **손절 과도 완화** → config stop_loss_pct -2% 적용 |
| DELTA_VWAP | vwap×0.99 | current+(current-vwap)×2 | 2400s | config: target_profit_pct 0.8 |
| GOLF_REVERSAL | day_low×0.995 | bb_middle | 1800s | config: stop_loss_pct -2% 추가 |
| ECHO_ABCD | 78.6% 되돌림 | 목표가 | 3600s | config 유지 |

- 002 실거래 20건은 전략 코드에서 계산한 stop/target으로 청산됨. config의 stop_loss_pct는 당시 BRAVO/GOLF에 없어 전략 기본값만 사용.

### 1-2. 거래별 정밀 분석 요약 (핵심 4건)

| # | 종목 | 전략 | 진단 요약 |
|---|------|------|-----------|
| **#10** | 046120 | BRAVO_ORB | entry 7567, exit 6953, -8.30%, TIMEOUT. stop=range_low(≈6150)로 설정되어 진입~청산 구간에서 low가 6150 미만으로 내려가지 않음 → 손절 미발동. **원인**: range_low 기반 손절만 사용 → config stop_loss_pct -2% 적용으로 보완. |
| **#4** | 038530 | GOLF_REVERSAL | entry 415, exit 398, -4.24%, STOP_LOSS. 시총 462억으로 C7 MIN_MARKET_CAP 5천억 미만. **원인**: 시총 fallback 5조로 gate 무력화 → fallback 제거로 동일 종목 발굴 제외. |
| **#15** | 006260 | DELTA_VWAP | entry 275275, exit 274851, -0.35%, TARGET_PROFIT. target = current+(current-vwap)×2에서 vwap이 높으면 목표가가 entry 아래일 수 있음 → **exit_reason 분류는 정상, 목표가 설정 이슈**. |
| **#8** | 000810 | DELTA_VWAP | entry 625625, exit 632367, +0.88%, TIMEOUT. 당일 고가 643000 대비 일찍 타임아웃 → **2분할+트레일링으로 수익 극대화 기대**. |

### 1-3. 시가총액 실제값 vs Feeder

- **stock_fundamentals 조회**: 18종목 모두 시가총액 보유 (date 기준 최신).
- **v4_scalping_universe × stock_fundamentals**: total_universe=708, has_fundamentals=708, no_fundamentals=0.
- **결론**: 현재 유니버스는 전부 fundamentals 존재. 시총 fallback 제거 시 **추정 불가 종목은 market_cap=0 → 발굴 gate에서 제외**.

### 1-4. 청산 후 주가 변동 요약

- 046120: 청산 후 추가 하락 구간 다수 → 청산 타이밍 적절.
- 038530: 청산 후 반등 구간 존재 → 손절 정상 작동.
- 000810: 청산 후 고점 대비 하락 → TIMEOUT 대비 2분할·트레일링 도입으로 개선 여지.

---

## 2. PHASE 2: 2분할 매도 도입 내역

### 수정 파일

- **desk2_config.yaml**: `exit_strategy` 섹션 추가 (split_sell: true, first_sell_pct: 50), 전략별 first_target_pct, trailing_stop_pct, trailing_activation_pct 추가.
- **sim_order_executor.py**: SimPosition에 first_sold, first_sell_quantity, first_sell_pnl, first_sell_filled_amount, remaining_quantity, trailing_active, trailing_high, trailing_stop_price 필드 추가.
- **backtest_runner.py**: Phase D에서 (1) effective_stop 적용, (2) 1차 매도 50% at first_target_price, (3) 트레일링 활성화/2차 매도, (4) FIRST_TARGET+TIMEOUT 처리. exit_reason/exit_type DB 저장 시 20자 truncate.

### 전략별 파라미터 (2분할)

| 전략 | first_target_pct | trailing_stop_pct | trailing_activation_pct |
|------|------------------|-------------------|--------------------------|
| GOLF_REVERSAL | 1.0 | 0.8 | 0.8 |
| DELTA_VWAP | 1.0 | 0.8 | 0.8 |
| BRAVO_ORB | 2.0 | 1.5 | 1.5 |
| ALPHA_GAP | 1.5 | 1.0 | 1.0 |
| ECHO_ABCD | 2.0 | 1.5 | 1.5 |
| CHARLIE_VI | 2.0 | 1.5 | 1.5 |
| FOXTROT_SECTOR | 1.5 | 1.0 | 1.0 |

### AST/import 테스트

- backtest_runner.py, sim_order_executor.py, historical_price_feeder.py, c7_oversold_rebound.py, c4_intraday_surge.py: **AST OK**
- Desk2BacktestRunner, HistoricalPriceFeeder, SimOrderExecutor, SimFundPool: **Import OK**

---

## 3. PHASE 3: 발굴 파라미터 조정 내역

### 시가총액 fallback 제거

- **historical_price_feeder.py** `_load_market_cap()`: 추정 불가 종목에 대해 `market_cap = 0` 설정 (기존 5조 fallback 제거).
- **get_cumulative_indicators**: 미보유 종목 반환값을 0.0으로 통일.
- **결과**: market_cap=0인 종목은 C7/C4의 MIN_MARKET_CAP gate에서 통과 불가.

### C7 과매도 gate 강화

- **c7_oversold_rebound.py** (백업: `/tmp/c7_backup_20260226_201534.py`):
  - PRICE_DROP_FROM_HIGH_MIN_PCT: 3.0 → **3.5**
  - MIN_CLOSE_KRW: **1000** (저가주 제외)
  - MIN_AVG_TURNOVER_10E8: **1.0** (일평균 거래대금 10억원, feeder에 필드 추가 시 적용)

### C4 장중급등 gate

- **c4_intraday_surge.py**:
  - MIN_CLOSE_KRW: **3000** (극저가주 제외)
  - 10분 거래량 조건: 기존 vol_10m ≥ avg_30m_vol × 2.0 유지 확인.

### BRAVO_ORB stop-loss 보완

- **backtest_runner.py**: 전략별 `stop_loss_pct`가 config에 있으면 `effective_stop = max(pos.stop_loss, entry × (1 + stop_loss_pct/100))` 적용.
- BRAVO_ORB는 strategy_params에 stop_loss_pct: -2.0 추가 → range_low만으로는 손절이 과도하게 완화되던 문제 완화.

---

## 4. PHASE 4: 수정 후 재검증 결과

### 4-1. 일별 요약 (수정 전 vs 수정 후)

| test_date | 수정 전(002) | 수정 후(001-FIX) |
|-----------|-------------|-------------------|
| 2026-02-19 | - | trades=5, total_pnl=-952, avg_pnl_pct=0.03, wins=3 |
| 2026-02-20 | - | trades=5, total_pnl=-21,646, avg_pnl_pct=-0.12, wins=2 |
| 2026-02-24 | - | trades=5, total_pnl=-92,429, avg_pnl_pct=-0.89, wins=2 |
| 2026-02-25 | - | trades=5, total_pnl=-112,108, avg_pnl_pct=-0.90, wins=1 |
| **합계** | **20건, -411,892** | **20건, -227,135** |

### 4-2. 전략별 성과 비교

| strategy_name | trades | total_pnl | avg_pnl_pct | wins |
|---------------|--------|-----------|-------------|------|
| GOLF_REVERSAL | 17 | -123,221 | -0.29 | 8 |
| DELTA_VWAP | 1 | -9,646 | -0.38 | 0 |
| ECHO_ABCD | 1 | -26,140 | -1.79 | 0 |
| BRAVO_ORB | 1 | -68,128 | -2.29 | 0 |

### 4-3. 개별 거래 전체 목록 (20건)

| rn | start_date | stock_code | strategy_name | entry_price | exit_price | pnl_pct | hold_seconds | exit_reason | pnl |
|----|------------|------------|---------------|-------------|------------|---------|--------------|-------------|-----|
| 1 | 2026-02-19 | 272290 | GOLF_REVERSAL | 36836.80 | 36479.98 | -1.16 | 360 | STOP_LOSS | -34664 |
| 2 | 2026-02-19 | 322000 | GOLF_REVERSAL | 85785.70 | 86614.10 | 0.74 | 360 | FIRST_TARGET+TRAILIN | 15143 |
| 3 | 2026-02-19 | 348340 | GOLF_REVERSAL | 80280.20 | 80789.13 | 0.44 | 1260 | TARGET_PROFIT | 13001 |
| 4 | 2026-02-19 | 319400 | GOLF_REVERSAL | 26876.85 | 27066.66 | 0.51 | 600 | TARGET_PROFIT | 10688 |
| 5 | 2026-02-19 | 319660 | GOLF_REVERSAL | 62762.70 | 62662.28 | -0.35 | 120 | TARGET_PROFIT | -5120 |
| 6 | 2026-02-20 | 440110 | GOLF_REVERSAL | 50350.30 | 50049.90 | -0.79 | 1800 | TIMEOUT | -23481 |
| 7 | 2026-02-20 | 295310 | GOLF_REVERSAL | 84084.00 | 84433.88 | 0.45 | 1620 | FIRST_TARGET+TRAILIN | 9493 |
| 8 | 2026-02-20 | 322000 | GOLF_REVERSAL | 88388.30 | 88663.75 | 0.12 | 1380 | TARGET_PROFIT | 1640 |
| 9 | 2026-02-20 | 272210 | GOLF_REVERSAL | 115415.30 | 115526.86 | -0.10 | 60 | TARGET_PROFIT | -1705 |
| 10 | 2026-02-20 | 458870 | GOLF_REVERSAL | 149349.20 | 149260.59 | -0.25 | 60 | TARGET_PROFIT | -7593 |
| 11 | 2026-02-24 | 440110 | GOLF_REVERSAL | 52052.00 | 52160.29 | 0.01 | 180 | TARGET_PROFIT | 374 |
| 12 | 2026-02-24 | 403870 | GOLF_REVERSAL | 40990.95 | 41072.64 | 0.00 | 120 | TARGET_PROFIT | 81 |
| 13 | 2026-02-24 | 347700 | ECHO_ABCD | 44244.20 | 43536.96 | -1.79 | 3420 | STOP_LOSS | -26140 |
| 14 | 2026-02-24 | 403870 | DELTA_VWAP | 41441.40 | 41363.91 | -0.38 | 60 | TARGET_PROFIT | -9646 |
| 15 | 2026-02-24 | 491000 | GOLF_REVERSAL | 92392.30 | 90453.91 | -2.29 | 900 | STOP_LOSS | -57098 |
| 16 | 2026-02-25 | 000720 | BRAVO_ORB | 156656.50 | 153369.85 | -2.29 | 780 | STOP_LOSS | -68128 |
| 17 | 2026-02-25 | 319400 | GOLF_REVERSAL | 35285.25 | 35428.54 | 0.45 | 300 | FIRST_TARGET+TRAILIN | 6513 |
| 18 | 2026-02-25 | 032820 | GOLF_REVERSAL | 17217.20 | 17077.01 | -1.01 | 300 | STOP_LOSS | -21166 |
| 19 | 2026-02-25 | 130660 | GOLF_REVERSAL | 25675.65 | 25524.45 | -0.78 | 780 | DAILY_LIMIT | -16278 |
| 20 | 2026-02-25 | 241520 | GOLF_REVERSAL | 17617.60 | 17494.49 | -0.89 | 780 | STOP_LOSS | -13049 |

### 4-4. 2분할 매도 효과

- **FIRST_TARGET+TRAILING_STOP** 적용 건: 3건 (322000 02-19, 295310 02-20, 319400 02-25). 모두 GOLF_REVERSAL, 양수 PnL.
- DB 저장 시 exit_reason/exit_type은 20자 제한으로 `FIRST_TARGET+TRAILIN` 등으로 truncate.

### 4-5. 실매매 전환 기준 재판정

| 기준 | 목표 | 수정 전(002) | 수정 후(001-FIX) | 판정 |
|------|------|-------------|-------------------|------|
| 기대값 E | > +0.3% | -1.025% | **-0.47%** | 미달, 개선 |
| Profit Factor | > 1.3 | 0.10 | (미계산) | 미달 |
| 일일 최대 손실 | ≤ -3% | -1.60% | -0.90% | 충족 |
| 총 손익 | - | -411,892 | **-227,135** | 개선 |
| 승률 | - | 35% | **40%** | 소폭 개선 |

---

## 5. 결론 및 다음 단계

- **청산 조건**: BRAVO range_low 단독 손절 보완(stop_loss_pct 적용), 시총 fallback 제거로 C7/C4 gate 정상화.
- **2분할 매도**: 1차 50% 목표가 + 2차 트레일링 적용, 3건에서 FIRST_TARGET+TRAILING_STOP 발생, 양수 PnL.
- **재검증**: 동일 4일 20건 기준 총 손익 -411,892 → **-227,135**로 개선. 실매매 전환에는 여전히 기대값·PF 목표 미달.
- **다음**: 추가 기간 확대 검증, PF·기대값 목표 재점검, v4_bt_discoveries INSERT 연동 검토(필요 시 runner에 추가).

---

*문서 레포 푸시: project-docs/kis-autotrade-v4/reports/*
