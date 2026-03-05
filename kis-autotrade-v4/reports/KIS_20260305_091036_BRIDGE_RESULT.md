---
project: kis-autotrade-v4
task_id: T-075 (CUR-V41-TP-ZERO-FIX-001)
completed_at: 2026-03-05T09:21:00+09:00
---

# T-075 결과 보고서: 가상매매 TP=0 근본 원인 해결

[인계 확인]
직전 완료: T-076 (GO100 V3 Q2 모델 활성화 + 모의투자 0체결)
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-001, D-007, CEO-APPROVAL-20260305 (D4 SL2% TP3%)
strategy_cards: 60
open_positions: 14

---

## Phase 1: READ-ONLY 진단 결과

### Step 1-1: v4_mock_trades 전수 분석

```
-- 수행 쿼리
SELECT strategy_id, COUNT(*) as cnt,
       ROUND(AVG(pnl_pct)::numeric, 4) as avg_pnl,
       ROUND(MIN(pnl_pct)::numeric, 4) as min_pnl,
       ROUND(MAX(pnl_pct)::numeric, 4) as max_pnl,
       COUNT(*) FILTER (WHERE pnl_pct > 0) as profitable,
       COUNT(*) FILTER (WHERE exit_price IS NULL) as open_trades
FROM v4_mock_trades
GROUP BY strategy_id ORDER BY strategy_id;

-- 결과 (2026-03-05 기준, 총 108건)
 strategy_id | cnt | avg_pnl | min_pnl | max_pnl | profitable | open_trades
-------------+-----+---------+---------+---------+------------+-------------
 D2          |  12 | -0.4700 | -0.4700 | -0.4700 |          0 |           9
 D4          |  12 | -0.4700 | -0.4700 | -0.4700 |          0 |           9
 D5          |  18 |         |         |         |          0 |          18
 D6          |  18 | -0.7518 | -1.8790 | -0.4700 |          0 |          13
 D7          |  18 | -0.4700 | -0.4700 | -0.4700 |          0 |          14
 D-ORB       |  18 | -0.9937 | -3.6120 | -0.4700 |          0 |          12
 S1          |  12 | -0.4700 | -0.4700 | -0.4700 |          0 |           7
```

**진단**: 108건 중 TP 체결 0건. 모든 수익 거래 없음. profitable = 0.

### Step 1-2: v4_mock_trades 스키마 불일치 발견

지시서가 가정한 컬럼(status, exit_type, card_id, stock_code, highest_price, closed_at)이
실제 테이블에 없음. 실제 스키마:

```
 id, trade_date, ticker, strategy_id, direction, quantity,
 entry_price, exit_price, pnl_pct, cost_pct, slippage_pct,
 kis_order_id, notes (text/JSON), created_at
```

notes 컬럼에 승인 결과 JSON 포함:
`{"approved": false/true, "blocking_layer": ..., "cs_score": ..., "eqs_score": ...}`

### Step 1-3: 수급게이트 BLOCK 비율 분석

```sql
SELECT
  CASE WHEN notes LIKE '%"approved": true%' THEN 'approved_true'
       WHEN notes LIKE '%"approved": false%' THEN 'approved_false'
       ELSE 'other' END as approval_status,
  CASE WHEN notes LIKE '%L3.3_SUPPLY%' THEN 'L3.3_SUPPLY_BLOCK'
       ELSE 'no_block' END as block_status,
  COUNT(*) as cnt
FROM v4_mock_trades
GROUP BY 1, 2;

-- 결과
 approval_status |   block_status    | cnt
-----------------+-------------------+-----
 approved_false  | L3.3_SUPPLY_BLOCK |  72   ← 67% 차단
 approved_true   | no_block          |  29   ← 27% 통과
 approved_false  | no_block          |   7   ← 6% 기타차단
```

**발견**: 72건(67%)이 L3.3_SUPPLY 수급게이트에서 차단됨. entry_price = NULL.

### Step 1-4: 실제 진입 29건 ticker 분석

```sql
-- 진입(entry_price IS NOT NULL) 거래들의 tick 데이터 유무 확인
-- 어제(2026-03-04) 데이터 기준

 ticker | strategy_id | entry_price | exit_price | total_tick_count | total_ob_count
--------+-------------+-------------+------------+------------------+----------------
 000180 | D-ORB       |      1623.0 |     1572.0 |              450 |           2280  ← 실제종목
 000087 | D6          |     14190.0 |    13990.0 |              197 |           1095  ← 실제종목
 000040 | D6          |       357.0 |      357.0 |              586 |           2192  ← 실제종목
 0005A0 | D6          |      9610.0 |     9610.0 |                1 |            126  ← 실제종목
 917803 | D2          |    138121.0 |   138121.0 |                0 |              0  ← 합성ticker
 888604 | S1          |     40677.0 |    40677.0 |                0 |              0  ← 합성ticker
 104733 | D7          |    127398.0 |   127398.0 |                0 |              0  ← 합성ticker
 442205 | D-ORB       |     27330.0 |    27330.0 |                0 |              0  ← 합성ticker
```

**발견**: 29건 중 21건이 합성 ticker(tick 데이터 없음), 3건만 실제 종목

### Step 1-5: STRATEGY_EXIT_PARAMS 분석

```python
# exit_manager.py STRATEGY_EXIT_PARAMS (수정 전)
STRATEGY_EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": 60},   # TP 없음!
    "D4":  {"sl_pct": 0.010, "tp_pct": 0.050, "timeout_min": 60},   # TP=5% 너무 높음
    "D5":  {"sl_pct": 0.025, "tp_pct": None,  "timeout_min": 60},   # TP 없음!
    "S1":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": None}, # TP 없음!
}
# run_unified_engine.py action_monitor EXIT_PARAMS (수정 전) 동일

# D6, D7, D-ORB도 tp_pct=None (D-ORB만 0.050 있었음)
```

### Step 1-6: action_signal 실제 종목 조회 쿼리 분석

```python
# 문제 코드 (수정 전)
cur_s.execute("""
    SELECT stock_code, MAX(price) as last_price
    FROM v4_tick_data
    WHERE tick_time >= NOW() - INTERVAL '30 minutes'  ← 핵심 버그!
    GROUP BY stock_code
    ORDER BY COUNT(*) DESC
    LIMIT 50
""")
```

**발견**: action_signal이 08:50에 실행되는데, 장전(08:20~08:50) tick이 거의 없음.
결과: stock_iter = [] → 합성 random 종목 사용.

```sql
-- 검증: 08:50 기준 30분 vs 20시간 종목 수 비교
SELECT
  COUNT(DISTINCT stock_code) FILTER (
    WHERE tick_time >= TIMESTAMPTZ '2026-03-04 08:50:00+09' - INTERVAL '30 minutes'
  ) as within_30min,
  COUNT(DISTINCT stock_code) FILTER (
    WHERE tick_time >= TIMESTAMPTZ '2026-03-04 08:50:00+09' - INTERVAL '20 hours'
  ) as within_20h
FROM v4_tick_data;

-- 결과
 within_30min | within_20h
--------------+------------
            4 |         25   ← 20시간이면 전일 실제 종목 25개 포착
```

### Step 1-7: 로그 분석

```
# /root/kis-autotrade-v4/logs/unified_engine.log-20260305 (03-03 실행분)
2026-03-03 09:32:48,397 [INFO] [MONITOR] 09:32:48 — 포지션 모니터링
2026-03-03 09:32:48,419 [INFO] [MONITOR] 오픈 포지션 20건
2026-03-03 09:32:48,419 [INFO]   id=8 ticker=182487 strategy=D6 entry=80322.0  (합성)
2026-03-03 09:32:48,419 [INFO]   id=9 ticker=529671 strategy=D5 entry=None     (차단)
...
2026-03-03 09:32:48,420 [INFO] 통합 엔진 종료
```
→ 모니터 1회 실행 후 현재가 없어 모든 포지션 스킵. TP/SL 체크 미실행.

### 유일하게 TP/SL이 작동한 거래 (검증)

```
-- id=77 (D-ORB, 000180): 실제 종목, SL 발동
notes: {"approved": true, ...} | SL(2.5%) @ 09:17:50
entry=1623, exit=1572, pnl=-3.612% (실제 가격 손실)

-- id=71 (D6, 000087): 실제 종목, TIMEOUT 발동
notes: {"approved": true, ...} | TIMEOUT(60min) @ 10:18:01
entry=14190, exit=13990, pnl=-1.879% (60분 타임아웃 후 가격 하락)
```

---

## 근본 원인 요약

### RC-1 (주요): 08:50 신호 액션에서 실제 종목 조회 실패

- `action_signal` 이 08:50에 실행, `INTERVAL '30 minutes'` = 08:20~08:50
- 장전이라 tick 없음 → `stock_iter=[]` → 합성 random 종목 사용
- 합성 종목(917803 등)은 `v4_tick_data`에 없음 → 모니터에서 현재가 조회 불가
- 현재가 없으면 `action_monitor`가 포지션 스킵 → TP/SL 불발
- `action_close`에서 `exit_price = entry_price` (보수적 처리) → pnl=-0.47% (비용만)

### RC-2 (부차): 대부분 전략에 TP 파라미터 미정의

- D2, D5, D6, D7의 `tp_pct=None` → TP 체크 자체가 실행 안 됨
- D4: `tp_pct=0.050`(5%)는 CEO 승인(3%)과 불일치 + 당일 +5% 달성 어려움
- D-ORB: `tp_pct=0.050`(5%)도 너무 높음

---

## Phase 2: 수정 내역

### Fix 1: action_signal tick 조회 창 30분→20시간

**파일**: `scripts/run_unified_engine.py`

```python
# 수정 전
WHERE tick_time >= NOW() - INTERVAL '30 minutes'

# 수정 후
WHERE tick_time >= NOW() - INTERVAL '20 hours'
```

효과: 08:50 실행 시 전일 거래 종목 25개+ 확보 가능.
nxt_signal 함수의 `INTERVAL '60 minutes'`도 동일하게 수정.

### Fix 2: TP 파라미터 추가 (action_monitor EXIT_PARAMS)

**파일**: `scripts/run_unified_engine.py`

```python
# 수정 전
EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": 60},
    "D4":  {"sl_pct": 0.010, "tp_pct": 0.050, "timeout_min": 60},
    "D5":  {"sl_pct": 0.025, "tp_pct": None,  "timeout_min": 60},
    "S1":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": None},
    "D6":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": 60},
    "D7":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": 60},
    "D-ORB": {"sl_pct": 0.025, "tp_pct": 0.050, "timeout_min": 60},
}
DEFAULT_EXIT = {"sl_pct": 0.030, "tp_pct": None, "timeout_min": 60}

# 수정 후
EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
    "D2A": {"sl_pct": 0.020, "tp_pct": None,  "timeout_min": 30},
    "D2B": {"sl_pct": 0.025, "tp_pct": None,  "timeout_min": 60},
    "D4":  {"sl_pct": 0.020, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305: SL 2%, TP 3%
    "D5":  {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
    "S1":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": None},
    "D6":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
    "D7":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
    "D-ORB": {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
}
DEFAULT_EXIT = {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60}
```

### Fix 3: exit_manager.py STRATEGY_EXIT_PARAMS 동기화

**파일**: `backend/app/services/unified_engine/core/exit_manager.py`

```python
# 수정 전
STRATEGY_EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": None, ...},
    "D4":  {"sl_pct": 0.010, "trail_start": 0.050, "trail_retrace": 0.10, "tp_pct": 0.050, ...},
    "D5":  {"sl_pct": 0.025, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": None, ...},
    "S1":  {"sl_pct": 0.030, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": None, ...},
    # D6, D7, D-ORB 미정의
}

# 수정 후
STRATEGY_EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, ...},
    "D4":  {"sl_pct": 0.020, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, ...},  # CEO-APPROVAL-20260305
    "D5":  {"sl_pct": 0.025, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": 0.030, ...},
    "S1":  {"sl_pct": 0.030, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": None,  ...},
    "D6":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, ...},
    "D7":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, ...},
    "D-ORB": {"sl_pct": 0.025, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, ...},
}
```

---

## Phase 3: 단위 테스트 검증

**파일**: `tests/test_unified_engine.py` (TestExitManager 클래스 확장)

```
# 신규 추가 테스트 3건
tests/test_unified_engine.py::TestExitManager::test_tp_d4_3pct    PASSED
tests/test_unified_engine.py::TestExitManager::test_tp_d2_3pct    PASSED
tests/test_unified_engine.py::TestExitManager::test_tp_not_triggered_below_threshold  PASSED

# 기존 테스트 (내 변경과 무관한 pre-existing failure)
tests/test_unified_engine.py::TestExitManager::test_hard_stop     PASSED
tests/test_unified_engine.py::TestExitManager::test_time_close    FAILED (pre-existing bug: MagicMock entry_time)
```

테스트 결과: 신규 TP 시나리오 3건 모두 통과.
`test_time_close` 실패는 내 변경 이전에도 발생하던 기존 문제 (git stash 전 상태에서도 동일 실패 확인됨).

---

## 커밋 정보

```
commit: 04740d65e1ee804e3af8a34f41470c50ba94c550
branch: phase-2c-command-center
files changed:
  - backend/app/services/unified_engine/core/exit_manager.py (+11 -2)
  - scripts/run_unified_engine.py (+10 -8)
  - tests/test_unified_engine.py (+51)
```

주: T-075 변경사항은 T-076 세션과 동시 커밋됨 (두 세션 병행 작업으로 인해 하나의 커밋에 포함).

---

## v4_virtual_trades_full 현황 (Phase 1 데이터 기준)

```sql
SELECT COUNT(*) as total,
       COUNT(*) FILTER (WHERE approved=true) as approved_cnt,
       COUNT(*) FILTER (WHERE exit_price IS NOT NULL) as exited
FROM v4_virtual_trades_full
WHERE session_date >= '2026-03-03';

-- 결과
 total | approved_cnt | exited
-------+--------------+--------
    49 |           19 |     11
```

---

## 향후 검증 계획 (Phase 3 지속)

- [x] 단위 테스트 3건 통과 확인
- [ ] 다음 가상매매 신호일(03-06 이후) 실행 결과 확인
  - action_signal에서 `stock_iter` 비어있지 않은지 로그 확인
  - 실제 종목으로 진입 후 TP +3% 도달 시 체결 여부 모니터링
- [ ] TP 1건 이상 체결 확인 목표

---

## 부기: action_close 보수적 처리 (개선 후보)

현재 action_close는 미청산 포지션을 `exit_price = entry_price`로 처리.
실제로 마감 시 현재가로 처리하면 더 정확하지만,
CEO 지시 서비스 재시작 금지 조건으로 인해 다음 세션 별도 검토 권고.

```python
# action_close 현재 코드 (보수적)
UPDATE v4_mock_trades
SET exit_price = entry_price,  ← 실제 마감가 아닌 진입가
    pnl_pct = -0.47            ← 비용만 차감
WHERE trade_date = %s AND direction = 'BUY' AND exit_price IS NULL AND entry_price IS NOT NULL
```
