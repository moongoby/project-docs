# OVERLAP-GUARD + REGIME-STRATEGY-CROSS 보고서 (2026-02-23)

**서버:** 211.188.51.113  
**경로:** /root/kis-autotrade-v4  
**성격:** 읽기 전용 분석

---

## 사전 확인

- strategy_cards COUNT: **62** ✓  
- v4_positions OPEN: **5** ✓  
- kis-v41-api / kis-v41-monitor: **active (running)** ✓  
- df /: **53%** ✓  

---

# PART A: OVERLAP-GUARD

## 1. 세션별 중복 종목 수 (상위 10)

| session_id | overlap_stock_count | avg_desk_overlap |
|------------|---------------------|------------------|
| 63 | 2 | 2.00 |
| 61 | 19 | 2.00 |
| 60 | 3 | 2.00 |
| 59 | 1 | 2.00 |
| 58 | 82 | 2.33 |
| 57 | 463 | 2.32 |
| 56 | 268 | 2.27 |
| 55 | 166 | 2.36 |
| 54 | 170 | 2.26 |
| 53 | 2 | 2.00 |

- 세션 61: **19개 종목**이 2개 이상 DESK에서 동시 진입.

---

## 2. 세션 61 중복 종목 상위 20

| stock_code | desk_count | desks | total_trades | avg_pnl |
|------------|------------|-------|--------------|---------|
| 038500 | 2 | {2,3} | 14 | -2.39 |
| 088350 | 2 | {2,3} | 10 | 0.56 |
| 018880 | 2 | {2,3} | 8 | 1.16 |
| 006340 | 2 | {2,3} | 8 | -2.11 |
| 010170 | 2 | {2,3} | 8 | 7.50 |
| 067290 | 2 | {2,3} | 8 | -4.76 |
| 255220 | 2 | {2,3} | 8 | -2.75 |
| 049630 | 2 | {2,3} | 6 | 5.81 |
| 065170 | 2 | {2,3} | 6 | 10.04 |
| 006910 | 2 | {2,3} | 6 | -3.49 |
| 099440 | 2 | {2,3} | 6 | -2.85 |
| 187660 | 2 | {2,3} | 6 | 19.02 |
| 251340 | 2 | {2,3} | 6 | 0.44 |
| 008350 | 2 | {2,3} | 6 | 5.15 |
| 452260 | 2 | {2,3} | 4 | -3.46 |
| 225190 | 2 | {2,3} | 4 | -5.87 |
| 047040 | 2 | {2,3} | 4 | 8.80 |
| 128820 | 2 | {2,3} | 4 | 17.34 |
| 462330 | 2 | {2,3} | 4 | -0.72 |

- 모두 **DESK 2·3** 간 중복. DESK2·DESK3 동일 종목 동시 매수 발생.

---

## 3. 중복 종목의 DESK별 성과 차이 (세션 61)

| desk_id | trades | avg_pnl | total_pnl |
|---------|--------|---------|-----------|
| 2 | 60 | -1.05 | -31.46 |
| 3 | 66 | 4.49 | 148.26 |

- 동일 종목이라도 **DESK3이 DESK2보다 성과 우수** (avg_pnl 4.49 vs -1.05).  
- 중복 허용 시 DESK2 진입이 전체 수익을 깎는 구조 가능성.

---

## 4. 현재 OPEN 포지션 중복

**N** (0 rows)  
- `v4_positions`에서 status='OPEN'인 ticker 기준 동일 종목 2건 이상인 경우 없음.  
- 현재는 **실시간 포지션 상의 DESK 간 동일 종목 중복 없음**.

---

## 5. 기존 중복 방지 로직 존재 여부

- **시그널·주문·포지션 단계**  
  - `strategy_engine.py`: `_deduplicate_signals`, `_check_db_duplicates` (시그널 중복 차단).  
  - `order_executor.py`: `_check_or_create_order_request`로 주문 중복 처리.  
  - `risk_manager.py`: `_check_duplicate_holding` — **이미 보유 종목 재매수 차단** (종목 단위).  
  - `auto_trade_engine.py`: `_is_duplicate_order` (동일 계좌·종목·주문유형 5분 내 중복 주문 방지).  
- **파이프라인 매수 전**  
  - `v4_pipeline_orchestrator.py`: "이미 OPEN 포지션"이면 해당 카드/종목 매수 스킵 (로그: `SKIP ... 이미 OPEN 포지션`).  
- **정리:**  
  - **종목 단위** “이미 보유 시 추가 매수 금지” 로직 있음.  
  - **DESK 단위** “다른 DESK가 이미 같은 종목 보유 시 진입 금지” 로직은 **없음**.  
  - 즉, DESK2가 A종목 보유 중이어도 DESK3이 A종목 매수할 수 있는 구조.

---

## 6. 중복 방지 구현 필요도

**높음**  
- 백테스트상 세션 61만 해도 19종목이 2 DESK 중복, DESK2 쪽 평균 손실.  
- 리스크 매니저는 “같은 계좌/포지션” 기준이라, **전체 포지션(전 DESK) 기준 동일 종목 1포지션만 허용**하도록 확장하는 것이 안전.

---

## 7. 권장 방안

1. **매수 전 검사**  
   - `v4_positions`에서 `status='OPEN'`이고 **다른 desk_id**로 동일 `ticker`가 이미 있으면, 해당 신호는 매수하지 않도록 체크 (파이프라인 or risk_manager).  
2. **정책 선택**  
   - “종목당 전 시스템 1포지션” vs “DESK당 1포지션” 중 하나로 정책 고정 후, 그에 맞춰 쿼리 및 로그 메시지 통일.  
3. **백테스트 반영**  
   - 백테스트에서 “이미 다른 DESK가 해당 종목 보유 시 진입 불가” 규칙을 시뮬레이션에 넣어 성과 재측정 검토.

---

# PART B: REGIME-STRATEGY-CROSS

## 1. 레짐 분포 (일수)

| regime | days | from_date | to_date |
|--------|------|-----------|---------|
| SIDEWAYS | 21 | 2025-11-20 | 2026-02-11 |
| STRONG_TREND_DOWN | 20 | 2025-12-05 | 2026-01-06 |
| MILD_TREND_DOWN | 16 | 2025-11-24 | 2026-01-21 |
| MILD_TREND_UP | 2 | 2026-02-12 | 2026-02-13 |

---

## 2. 레짐별 전체 성과 (세션 61)

| regime | trade_count | avg_pnl | total_pnl | wins | losses |
|--------|-------------|---------|-----------|------|--------|
| MILD_TREND_UP | 16 | 3.86 | 61.70 | 7 | 9 |
| MILD_TREND_DOWN | 128 | 2.39 | 305.83 | 55 | 73 |
| STRONG_TREND_DOWN | 186 | 0.20 | 37.18 | 72 | 114 |
| SIDEWAYS | 159 | 0.08 | 13.12 | 69 | 90 |

- **MILD_TREND_UP**이 평균 수익률·총 수익 모두 가장 좋음 (거래 수는 적음).  
- **SIDEWAYS**, **STRONG_TREND_DOWN**은 avg_pnl이 거의 0에 가깝고, 승률은 낮음.

---

## 3. DESK × 레짐 성과 매트릭스

| desk_id | regime | trades | avg_pnl | total_pnl | wins |
|---------|--------|--------|---------|-----------|------|
| 2 | MILD_TREND_UP | 12 | 4.28 | 51.42 | 6 |
| 2 | MILD_TREND_DOWN | 96 | 1.76 | 168.55 | 45 |
| 2 | SIDEWAYS | 126 | -0.42 | -53.06 | 57 |
| 2 | STRONG_TREND_DOWN | 120 | -0.50 | -59.44 | 53 |
| 3 | MILD_TREND_DOWN | 32 | 4.29 | 137.28 | 10 |
| 3 | MILD_TREND_UP | 4 | 2.57 | 10.29 | 1 |
| 3 | SIDEWAYS | 33 | 2.01 | 66.18 | 12 |
| 3 | STRONG_TREND_DOWN | 66 | 1.46 | 96.62 | 19 |

- **DESK2:** SIDEWAYS·STRONG_TREND_DOWN에서 평균 마이너스.  
- **DESK3:** 모든 레짐에서 avg_pnl 양수.  
- 레짐별로 DESK 가중치(또는 진입 강도) 조정 시, DESK2는 상승/완만 하락 구간에, DESK3은 전 레짐에 비중 유지하는 방안 검토 가능.

---

## 4. 레짐별 최고 전략 TOP 5 (요약)

- **MILD_TREND_DOWN:** DESK2_종가매매_class_c (6.50), DESK3_단기스윙_class_d (4.29), DESK2_장초반레인지돌파 (3.28) 등.  
- **MILD_TREND_UP:** (거래 수 적음) DESK2 쪽 4.28 수준.  
- **SIDEWAYS:** DESK3_단기스윙_class_d (2.01), DESK2_M002_AbsoluteZero_종가매매 (0.65).  
- **STRONG_TREND_DOWN:** DESK2_거래량스파이크 (2.58), DESK3_단기스윙_class_d (1.46), DESK2_S05_거래량점화 (1.71).

---

## 5. 레짐별 최악 전략 BOTTOM 5

- **STRONG_TREND_DOWN:** DESK2_장초반레인지돌파 avg_pnl -2.57, total -71.88.  
- **SIDEWAYS:** DESK2_장초반레인지돌파 -2.08, DESK2_거래량스파이크 -0.54, DESK2_S05_거래량점화 -0.43 등.  
- **MILD_TREND_UP:** DESK2_변동성확대 -1.55.  
- **MILD_TREND_DOWN:** (하위는 상대적으로 덜 나쁨) 변동성확대 1.41 등.

---

## 6. 레짐 전환 시점 성과

| change_date | prev_regime | new_regime | trades_on_change | avg_pnl_on_change |
|-------------|-------------|------------|------------------|--------------------|
| 2025-11-24 | SIDEWAYS | MILD_TREND_DOWN | 9 | -2.68 |
| 2025-12-05 | MILD_TREND_DOWN | STRONG_TREND_DOWN | 11 | 0.68 |
| 2026-01-07 | STRONG_TREND_DOWN | MILD_TREND_DOWN | 6 | -1.19 |
| 2026-01-12 | MILD_TREND_DOWN | SIDEWAYS | 8 | 1.96 |
| 2026-01-16 | SIDEWAYS | MILD_TREND_DOWN | 8 | 5.52 |
| 2026-01-22 | MILD_TREND_DOWN | SIDEWAYS | 8 | -6.32 |
| 2026-02-12 | SIDEWAYS | MILD_TREND_UP | 7 | 7.28 |

- **SIDEWAYS → MILD_TREND_UP** 전환일(2026-02-12)에 avg_pnl 7.28로 가장 좋음.  
- **MILD_TREND_DOWN → SIDEWAYS** (2026-01-22)는 -6.32로 전환일 손실 큼.

---

## 7. 현재 레짐

- **v4_market_regime_daily** 최신: **2026-02-13** — **MILD_TREND_UP** (regime_score 75, BULL_ALIGNED).  
- 2026-02-12도 MILD_TREND_UP.  
- 2026-02-11까지 SIDEWAYS.  
- **2026-02-23 레짐**은 DB에 당일 행이 없어, 전날(2/13) 기준 MILD_TREND_UP으로 해석 가능.  
- 장 전 PRE_MARKET에서 regime_detector가 오늘 레짐을 갱신하면 그때 현재 레짐 확정.

---

## 8. regime_detector 자동 업데이트 여부

- **orchestrator (system)**  
  - PRE_MARKET 단계에서 `regime_detector.detect_regime(save=True)` 호출.  
  - 결과를 `v4_market_regime_daily`에 저장하고, 레짐 변경 시 `register_regime_change_hook` 콜백 실행.  
- **adaptive_bridge**  
  - `on_regime_change`로 레짐 전환 시 비상 사이클 등 대응.  
- **정리:**  
  - 스케줄러/오케스트레이터가 장 전 PRE_MARKET을 돌리면 **자동 업데이트됨**.  
  - 당일(2/23) 레짐 행이 아직 없는 것은 PRE_MARKET 미실행이거나, 아직 오늘 날짜로 저장되지 않았을 가능성.

---

## 9. 레짐 기반 전략 가중치 조정 권장안

1. **SIDEWAYS / STRONG_TREND_DOWN**  
   - DESK2_장초반레인지돌파, DESK2_변동성확대 비중 축소 또는 진입 조건 강화.  
2. **MILD_TREND_UP / MILD_TREND_DOWN**  
   - DESK2_종가매매_class_c, DESK3_단기스윙_class_d, DESK2_장초반레인지돌파 등 유지·강화 검토.  
3. **레짐 전환일**  
   - SIDEWAYS→MILD_TREND_UP 전환 시점은 성과 좋음; 전환일 전후로 진입 허용 완화 검토.  
   - MILD_TREND_DOWN→SIDEWAYS 전환일(1/22)처럼 손실 큰 구간은 진입 제한 또는 포지션 축소 검토.  
4. **DESK 비중**  
   - 레짐이 SIDEWAYS/STRONG_TREND_DOWN일 때 DESK2 비중 감소, DESK3 비중 유지 방안 검토.

---

# 공통

- **strategy_cards COUNT:** 62  
- **v4_positions OPEN:** 5  
- **이슈:**  
  - OVERLAP: DESK 간 동일 종목 중복 매수 방지 로직 추가 권장.  
  - REGIME: 현재 DB상 최신 레짐 2026-02-13 MILD_TREND_UP; 당일 레짐은 PRE_MARKET 실행 후 확인.

---

**보고 완료.**
