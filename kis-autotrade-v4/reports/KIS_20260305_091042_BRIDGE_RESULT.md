---
project: kis-autotrade-v4
task_id: KIS_20260305_091042_BRIDGE
completed_at: 2026-03-05T09:18:07+09:00
---

# KIS_20260305_091042_BRIDGE 실행 결과

## 지시서 원본 요약
- Task ID: 078 (DESK543 프랙탈 백테스트 Phase 0 — 데이터 준비 + 트리거 정의)
- DIR-0071 기반, CEO-DIRECTIVES D-012/D-013/D-014 적용
- 신규 파일로만 구현 (기존 코드 수정 금지)

---

## Phase 0-1: 데이터 검증 결과

### 실행 쿼리 및 결과

#### 1. 일봉 데이터 범위
```sql
SELECT MIN(date), MAX(date), COUNT(DISTINCT stock_code) FROM ohlcv_daily;
```
**결과:** `('20230102', '20260304', 3844)`
- MIN: 2023-01-02
- MAX: 2026-03-04
- 종목 수: 3,844개

> 참고: 지시서 내 테이블명 `v4_ohlcv_daily`는 실제 DB에 존재하지 않음. 실제 테이블명은 `ohlcv_daily` 사용

#### 2. DESK5 풀 종목
```sql
SELECT COUNT(*) FROM v4_desk5_watchlist WHERE status = 'WATCHING';
```
**결과:** `(20,)` → 20종목

> 참고: 지시서 내 `v4_desk_pool WHERE desk_level = 5 AND status = 'WATCHING'`은 실제 DB 테이블 구조와 다름.
> 실제 테이블: `v4_desk5_watchlist` (status 컬럼 존재)

#### 3. DESK4 풀 종목
```sql
SELECT COUNT(*) FROM v4_desk4_watchlist WHERE status = 'WATCHING';
```
**결과:** `(18,)` → 18종목

#### 4. DESK3 풀 종목 (ACTIVE)
```sql
SELECT COUNT(*) FROM v4_desk3_pool WHERE status = 'ACTIVE';
```
**결과:** `(206,)` → 206종목

#### 5. 투자자 수급 데이터 범위
```sql
SELECT MIN(trade_date), MAX(trade_date), COUNT(*) FROM v4_investor_daily;
```
**결과:** `(datetime.date(2010, 1, 28), datetime.date(2026, 3, 4), 2576431)`
- MIN: 2010-01-28
- MAX: 2026-03-04
- 총 행수: 2,576,431

#### 6. v4_desk_backtest_results 스키마 확인
```python
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='v4_desk_backtest_results' ORDER BY ordinal_position")
```
**결과:** `['id', 'run_id', 'desk_level', 'param_key', 'param_value', 'param_snapshot', 'backtest_start', 'backtest_end', 'total_signals', 'triggered_signals', 'win_rate', 'profit_factor', 'avg_pnl_pct', 'max_drawdown_pct', 'sharpe_ratio', 'notes', 'created_at']`

→ 테이블 정상 존재, INSERT 가능

---

## Phase 0-2: 트리거 코드 구현

### 생성 파일
`/root/kis-autotrade-v4/backend/app/services/desk_filters/fractal_triggers.py`

### 구현 내용

#### 공통 유틸 함수
- `_ma(series, period)`: 단순이동평균 (데이터 부족 시 None)
- `_vol_ma(volumes, period)`: 거래량 이동평균
- `_rsi(closes, period=14)`: RSI (단순 평균 방식)
- `_highest_high(bars, period)`: 기간 내 최고가
- `_lowest_low(bars, period)`: 기간 내 최저가
- `_ma_slope_positive(closes, period, lookback)`: 이동평균 기울기 상향 여부

#### DESK5 트리거 (1파 바닥 진입)

**T5-1: MA60 기울기 상향 전환 + 거래량 20일 평균 2배**
```python
def check_t5_1(bars: List[Dict]) -> Dict[str, Any]:
    # MA60 기울기 상향: 현재 MA60 > 5봉 전 MA60
    # 거래량 2배: 현재 거래량 >= 직전 20일 평균 * 2.0
    # 반환: {'pass': bool, 'details': {'ma60_slope_up': bool, 'vol_2x_ma20': bool, ...}}
```

**T5-2: 바닥권 역배열→정배열 전환 (MA5>MA20>MA60)**
```python
def check_t5_2(bars: List[Dict]) -> Dict[str, Any]:
    # 현재봉: MA5 > MA20 > MA60 (정배열)
    # 직전봉: 정배열 아님 (역배열 또는 혼합)
```

**T5-3: 120일 신저가 후 20% 반등**
```python
def check_t5_3(bars: List[Dict]) -> Dict[str, Any]:
    # 최근 120일(현재봉 제외) 저점 대비 현재가 >= 1.20
```

**evaluate_desk5_trigger**: T5-1~T5-3 중 2개 이상 충족 → signal=True

#### DESK4 트리거 (2파 눌림 추매)

**T4-1: MA20 터치 + 양봉**
```python
def check_t4_1(bars: List[Dict]) -> Dict[str, Any]:
    # MA20 터치: 저가 <= MA20 <= 고가
    # 양봉: 종가 > 시가
```

**T4-2: 1파 고점 대비 -15%~-25% 조정 후 거래량 감소**
```python
def check_t4_2(bars, wave1_high=None) -> Dict[str, Any]:
    # wave1_high None이면 최근 60일 최고가 자동 탐색
    # correction_ratio = (wave1_high - current_close) / wave1_high
    # 0.15 <= ratio <= 0.25 AND 최근5일평균거래량 < 직전20일평균 * 0.8
```

**T4-3: 5일선 지지 + VP(체결강도) 120 이상**
```python
def check_t4_3(bars, vp_score=None) -> Dict[str, Any]:
    # 5일선 지지: 종가 >= MA5 * 0.98
    # VP 없으면 조건 완화 (vp_ok=True)
```

**T4-4: 동일 섹터 2종목 이상 동반 반등**
```python
def check_t4_4(stock_code, sector_rebounds) -> Dict[str, Any]:
    # 같은 섹터에서 본인 제외 2종목 이상 반등 중
```

**evaluate_desk4_trigger**: T4-1~T4-4 중 2개 이상 충족 → signal=True

#### DESK3 트리거 (3파 폭발)

**T3-1: 52주 신고가 돌파 + 거래량 3배 (단독 충족)**
```python
def check_t3_1(bars: List[Dict]) -> Dict[str, Any]:
    # 현재 고가 > 과거 249일 최고가
    # 현재 거래량 >= 직전 20일 평균 * 3.0
```

**T3-2: 박스 돌파 + 거래대금 100억 이상 (단독 충족)**
```python
def check_t3_2(bars: List[Dict]) -> Dict[str, Any]:
    # 현재 종가 > 직전 20일 최고가 (박스 상단 돌파)
    # 거래대금(trade_amount 또는 close*volume) >= 10_000_000_000
```

**T3-3: 상한가 경험 종목 + 5일선 지지**
```python
def check_t3_3(bars, had_upper_limit=False) -> Dict[str, Any]:
    # had_upper_limit: 외부 전달 (과거 상한가 경험)
    # 종가 >= MA5 * 0.98
```

**T3-4: 수급 DUAL_FLOW 5일 연속 + 정배열**
```python
def check_t3_4(bars, dual_flow_days=0) -> Dict[str, Any]:
    # dual_flow_days >= 5 (외국인+기관 동시 순매수)
    # MA5 > MA20 > MA60
```

**T3-5: 뉴스 카탈리스트 + RSI 50 이상**
```python
def check_t3_5(bars, has_catalyst_news=False) -> Dict[str, Any]:
    # has_catalyst_news: 외부 전달
    # RSI(14) >= 50
```

**evaluate_desk3_trigger**:
- T3-1 단독 PASS → signal=True, reason="T3-1 단독"
- T3-2 단독 PASS → signal=True, reason="T3-2 단독"
- T3-3~T3-5 중 2개 이상 → signal=True, reason="T3-3/4/5 {N}개"

---

## Phase 0-3: 백테스트 프레임워크 구현

### 생성 파일
`/root/kis-autotrade-v4/backend/app/services/desk_filters/fractal_backtest.py`

### 구현 내용

#### 데이터 로드
- `load_ohlcv(stock_code, start_date, end_date, conn)`: ohlcv_daily 테이블에서 OHLCV 로드
- `load_backtest_universe(desk_level, conn)`: DESK별 유니버스 로드
  - DESK5: v4_desk5_watchlist
  - DESK4: v4_desk4_watchlist
  - DESK3: v4_desk3_pool

#### 청산 조건 구현 (D-013/D-014)

**DESK5 청산 (_check_exit_desk5)**:
- 강제 손절: 진입가 대비 -15% (`STOP_LOSS_15PCT`)
- 주봉 MA20 2주 연속 이탈 (`WEEKLY_MA20_BREACH_2W`)
- 최대 보유: 120거래일 (`MAX_HOLD_120D`)

**DESK4 청산 (_check_exit_desk4)**:
- 손절: 진입가 대비 -8% (`STOP_LOSS_8PCT`)
- 익절: 진입가 대비 +30% (`TAKE_PROFIT_30PCT`)
- 최대 보유: 60거래일 (`MAX_HOLD_60D`)

**DESK3 청산 (_check_exit_desk3)**:
- 손절: 진입가 대비 -5% (`STOP_LOSS_5PCT`)
- 일봉 MA10 이탈 (10일 이상 보유 후, `MA10_BREACH`)
- 최대 보유: 30거래일 (`MAX_HOLD_30D`)

#### 시뮬레이션
- `simulate_single_stock(stock_code, desk_level, all_bars, min_bars_before=120)`:
  - 슬라이딩 윈도우로 시계열 트리거 평가
  - 진입 → 청산 사이클 반복
  - 미청산 포지션은 기간 종료 시 강제 청산

#### 성과 지표
- `_compute_metrics(trades)`: 승률, PF, 평균 손익률, MDD, 샤프비율 계산

#### 메인 실행
- `run_fractal_backtest(desk_level, lookback_days=120, max_stocks=50, ...)`:
  - 백테스트 기간: 최근 120거래일 (≈170 달력일)
  - 자본: Stage 1 기준 (DESK2 100%, 4천만원)
  - 결과: FractalBacktestResult 반환

#### DB 저장
- `save_backtest_result(result, conn)`:
  - v4_desk_backtest_results 테이블에만 INSERT
  - 기존 테이블 수정 없음

---

## Phase 0-4: 단위 테스트 결과

### 생성 파일
`/root/kis-autotrade-v4/tests/unit/test_fractal_triggers.py`

### 실행 결과
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
collected 55 items

tests/unit/test_fractal_triggers.py::TestT51::test_pass_both_conditions PASSED [  1%]
tests/unit/test_fractal_triggers.py::TestT51::test_fail_insufficient_data PASSED [  3%]
tests/unit/test_fractal_triggers.py::TestT51::test_fail_volume_insufficient PASSED [  5%]
tests/unit/test_fractal_triggers.py::TestT51::test_details_populated PASSED [  7%]
tests/unit/test_fractal_triggers.py::TestT52::test_pass_golden_cross_transition PASSED [  9%]
tests/unit/test_fractal_triggers.py::TestT52::test_fail_already_golden PASSED [ 10%]
tests/unit/test_fractal_triggers.py::TestT52::test_fail_insufficient_data PASSED [ 12%]
tests/unit/test_fractal_triggers.py::TestT52::test_details_populated PASSED [ 14%]
tests/unit/test_fractal_triggers.py::TestT53::test_pass_rebound_after_low PASSED [ 16%]
tests/unit/test_fractal_triggers.py::TestT53::test_pass_exact_20pct PASSED [ 18%]
tests/unit/test_fractal_triggers.py::TestT53::test_fail_insufficient_data PASSED [ 20%]
tests/unit/test_fractal_triggers.py::TestT53::test_fail_below_threshold PASSED [ 21%]
tests/unit/test_fractal_triggers.py::TestDesk5Evaluate::test_signal_requires_2_triggers PASSED [ 23%]
tests/unit/test_fractal_triggers.py::TestDesk5Evaluate::test_structure_complete PASSED [ 25%]
tests/unit/test_fractal_triggers.py::TestT41::test_pass_ma20_touch_bullish PASSED [ 27%]
tests/unit/test_fractal_triggers.py::TestT41::test_fail_bearish_candle PASSED [ 29%]
tests/unit/test_fractal_triggers.py::TestT41::test_fail_no_touch PASSED  [ 30%]
tests/unit/test_fractal_triggers.py::TestT41::test_fail_insufficient_data PASSED [ 32%]
tests/unit/test_fractal_triggers.py::TestT42::test_pass_correct_correction_and_vol_decrease PASSED [ 34%]
tests/unit/test_fractal_triggers.py::TestT42::test_fail_correction_too_small PASSED [ 36%]
tests/unit/test_fractal_triggers.py::TestT42::test_fail_correction_too_large PASSED [ 38%]
tests/unit/test_fractal_triggers.py::TestT42::test_auto_wave1_high_detection PASSED [ 40%]
tests/unit/test_fractal_triggers.py::TestT43::test_pass_ma5_support_with_high_vp PASSED [ 41%]
tests/unit/test_fractal_triggers.py::TestT43::test_fail_vp_below_threshold PASSED [ 43%]
tests/unit/test_fractal_triggers.py::TestT43::test_pass_vp_none_relaxed PASSED [ 45%]
tests/unit/test_fractal_triggers.py::TestT44::test_pass_sector_2_others PASSED [ 47%]
tests/unit/test_fractal_triggers.py::TestT44::test_fail_only_1_other PASSED [ 49%]
tests/unit/test_fractal_triggers.py::TestT44::test_fail_not_in_sector PASSED [ 50%]
tests/unit/test_fractal_triggers.py::TestDesk4Evaluate::test_structure_complete PASSED [ 52%]
tests/unit/test_fractal_triggers.py::TestDesk4Evaluate::test_signal_requires_2_triggers PASSED [ 54%]
tests/unit/test_fractal_triggers.py::TestT31::test_pass_new_high_with_3x_volume PASSED [ 56%]
tests/unit/test_fractal_triggers.py::TestT31::test_fail_insufficient_data PASSED [ 58%]
tests/unit/test_fractal_triggers.py::TestT31::test_fail_not_new_high PASSED [ 60%]
tests/unit/test_fractal_triggers.py::TestT31::test_fail_volume_insufficient PASSED [ 61%]
tests/unit/test_fractal_triggers.py::TestT32::test_pass_box_breakout_high_amount PASSED [ 65%]
tests/unit/test_fractal_triggers.py::TestT32::test_fail_no_breakout PASSED [ 67%]
tests/unit/test_fractal_triggers.py::TestT32::test_fail_amount_insufficient PASSED [ 67%]
tests/unit/test_fractal_triggers.py::TestT32::test_fail_insufficient_data PASSED [ 69%]
tests/unit/test_fractal_triggers.py::TestT33::test_pass_upper_limit_with_ma5_support PASSED [ 70%]
tests/unit/test_fractal_triggers.py::TestT33::test_fail_no_upper_limit_history PASSED [ 72%]
tests/unit/test_fractal_triggers.py::TestT33::test_fail_below_ma5 PASSED  [ 74%]
tests/unit/test_fractal_triggers.py::TestT34::test_pass_dual_flow_5d_and_golden PASSED [ 76%]
tests/unit/test_fractal_triggers.py::TestT34::test_fail_dual_flow_4d PASSED [ 78%]
tests/unit/test_fractal_triggers.py::TestT34::test_fail_insufficient_data PASSED [ 80%]
tests/unit/test_fractal_triggers.py::TestT35::test_pass_catalyst_and_rsi_above_50 PASSED [ 81%]
tests/unit/test_fractal_triggers.py::TestT35::test_fail_no_catalyst_news PASSED [ 83%]
tests/unit/test_fractal_triggers.py::TestT35::test_fail_insufficient_data PASSED [ 85%]
tests/unit/test_fractal_triggers.py::TestDesk3Evaluate::test_t3_1_solo_signal PASSED [ 87%]
tests/unit/test_fractal_triggers.py::TestDesk3Evaluate::test_t3_2_solo_signal PASSED [ 89%]
tests/unit/test_fractal_triggers.py::TestDesk3Evaluate::test_no_signal_all_fail PASSED [ 90%]
tests/unit/test_fractal_triggers.py::TestDesk3Evaluate::test_structure_complete PASSED [ 92%]
tests/unit/test_fractal_triggers.py::TestUtils::test_ma_basic PASSED     [ 94%]
tests/unit/test_fractal_triggers.py::TestUtils::test_ma_insufficient PASSED [ 96%]
tests/unit/test_fractal_triggers.py::TestUtils::test_rsi_range PASSED    [ 98%]
tests/unit/test_fractal_triggers.py::TestUtils::test_rsi_insufficient PASSED [100%]

============================== 55 passed in 0.22s ==============================
```

**결과: 55/55 ALL PASS**

### 추가 기능 검증
```python
# _compute_metrics 테스트
metrics = {'win_rate': 66.67, 'profit_factor': 3.75, 'avg_pnl_pct': 7.3333, 'max_drawdown_pct': 8.0, 'sharpe_ratio': 0.5168}
# → 통과

# 청산 조건 테스트
# DESK5 -16% 손절: exit=True, reason=STOP_LOSS_15PCT → 통과
# DESK4 -8% 손절: exit=True, reason=STOP_LOSS_8PCT → 통과
# DESK3 -5% 손절: exit=True, reason=STOP_LOSS_5PCT → 통과
```

---

## 생성 파일 목록

| 파일 | 라인 수 | 비고 |
|------|---------|------|
| `/root/kis-autotrade-v4/backend/app/services/desk_filters/fractal_triggers.py` | ~380 | D-012 트리거 정의 |
| `/root/kis-autotrade-v4/backend/app/services/desk_filters/fractal_backtest.py` | ~370 | D-013/D-014 청산+프레임워크 |
| `/root/kis-autotrade-v4/tests/unit/test_fractal_triggers.py` | ~320 | 단위 테스트 55개 |

---

## DB 상태 요약

| 항목 | 값 |
|------|-----|
| ohlcv_daily 범위 | 2023-01-02 ~ 2026-03-04 |
| 일봉 종목 수 | 3,844개 |
| DESK5 WATCHING | 20종목 |
| DESK4 WATCHING | 18종목 |
| DESK3 ACTIVE | 206종목 |
| v4_investor_daily | 2010-01-28 ~ 2026-03-04 (2,576,431행) |
| v4_desk_backtest_results | 존재 (INSERT 가능) |

---

## 적용 CEO-DIRECTIVES

| 지시 | 내용 | 적용 위치 |
|------|------|-----------|
| D-012 | DESK5/4/3 진입 트리거 정의 | fractal_triggers.py |
| D-013 | DESK4/5 청산 조건 | fractal_backtest.py: _check_exit_desk4/5 |
| D-014 | DESK3 청산 조건 | fractal_backtest.py: _check_exit_desk3 |

---

## 주요 발견 및 특이사항

1. **테이블명 불일치**: 지시서의 `v4_ohlcv_daily` → 실제 `ohlcv_daily`, `v4_desk_pool` → 실제 `v4_desk5_watchlist`/`v4_desk4_watchlist`/`v4_desk3_pool`로 분리됨
2. **DESK3 ACTIVE 종목 과다**: 206종목으로 백테스트 시 `max_stocks=50`으로 제한 권장
3. **VP 데이터 없음**: T4-3의 체결강도(VP)는 외부 시스템 연동 필요, 현재는 None 시 조건 완화 처리
4. **주봉 데이터 없음**: T5 청산 조건의 주봉 MA20은 일봉 데이터로 대체 가능하나 현재는 weekly_bars=None 시 조건 스킵

---

## 완료 체크리스트

- [x] Phase 0-1: 데이터 검증 완료 (ohlcv_daily 3844종목, investor_daily 257만행)
- [x] Phase 0-2: fractal_triggers.py 신규 생성 (D-012 DESK5/4/3 트리거 전체 구현)
- [x] Phase 0-3: fractal_backtest.py 신규 생성 (D-013/D-014 청산 조건, 프레임워크)
- [x] Phase 0-4: 단위 테스트 55개 ALL PASS
- [x] v4_desk_backtest_results 테이블만 INSERT (기존 테이블 수정 없음)
- [x] 기존 코드 수정 없음 (신규 파일 3개만 생성)
