---
project: V4.1
task_id: CUR-V41-VIRTUAL-RUN-HEALTH-CHECK-002
completed_at: 2026-03-04T14:14:23+09:00
---

# CUR-V41-VIRTUAL-RUN-HEALTH-CHECK-002 — 가상매매 헬스체크 보완 + MONITOR 에러 수정 결과

**실행일시**: 2026-03-04 14:14 KST
**작업자**: Claude (claudebot)
**기반 지시서**: /root/.genspark/directives/running/KIS_20260304_140955_BRIDGE.md
**인계 확인**: HANDOVER.md v8.8 확인 (최신: CUR-V41-ATR-COMMANDER-ACTIVATE-001)

---

[인계 확인]
직전 완료: CUR-V41-VIRTUAL-RUN-HEALTH-CHECK-001
현재 단계: Phase 2 (가상매매 운영)
CEO 지시 적용: D-001, D-002, D-007
strategy_cards: 확인 불요 (헬스체크 작업)
open_positions: 3건 (917803/D2, 888604/S1, 104733/D7 — 현재가 없음 지속)

---

## 완료 조건 달성 여부

| 완료 조건 | 상태 | 비고 |
|----------|------|------|
| 6개 항목 ALL PASS/FAIL 완전한 표 | ✅ 완료 | 아래 재조회 결과 참조 |
| float(None) 에러 재현 불가 확인 (테스트) | ✅ 완료 | 12/12 ALL PASS |
| synthetic 649645 확인 | ✅ 완료 | synthetic 확인, 정상 차단 |
| 보고서 작성 | ✅ 완료 | 본 파일 |

---

## 보완 항목 1: HEALTH-CHECK-001 항목 2~6 현재 상태 재조회 (14:14 KST 기준)

### 항목 2. 오늘(03-04) 거래 실적 — 재확인

#### v4_mock_trades (2026-03-04)

```sql
SELECT count(*), strategy_id FROM v4_mock_trades
WHERE trade_date='2026-03-04' GROUP BY strategy_id ORDER BY strategy_id;
```

결과:
```
 count | strategy_id
-------+-------------
     2 | D-ORB
     2 | D2
     2 | D4
     2 | D5
     2 | D6
     2 | D7
     2 | S1
(7 rows, 합계 14건)
```

#### v4_virtual_trades_full (2026-03-04)
```
count: 9건 (HEALTH-CHECK-001과 동일)
```

#### v4_virtual_monitor_snapshots (2026-03-04)
```
count: 77건 (14:14 기준 — 이후 계속 증가 중)
```

**판정**: ✅ PASS (HEALTH-CHECK-001 동일 유지)

---

### 항목 3. L3.3 수급 게이트 작동 — 재확인

```bash
grep "2026-03-04" /var/log/unified_engine.log | grep "synthetic_BLOCK"
```
결과:
```
2026-03-04 08:50:02,059 [INFO] [SIGNAL] D6 649645 차단 L3.3_SUPPLY: 수급 차단: synthetic_BLOCK
2026-03-04 08:50:02,064 [INFO] [SIGNAL] D5 403930 차단 L3.3_SUPPLY: 수급 차단: synthetic_BLOCK
2026-03-04 08:50:02,066 [INFO] [SIGNAL] D4 756835 차단 L3.3_SUPPLY: 수급 차단: synthetic_BLOCK
2026-03-04 08:50:02,074 [INFO] [SIGNAL] D-ORB 892224 차단 L3.3_SUPPLY: 수급 차단: synthetic_BLOCK
```

```bash
grep "2026-03-04" /var/log/unified_engine.log | grep -c "Fail-Open\|supply gate error"
```
결과: 0건

**판정**: ✅ PASS (HEALTH-CHECK-001 동일)

---

### 항목 4. 청산 로직 작동 — 재확인

```bash
cat /root/kis-autotrade-v4/reports/daily/2026-03-04/exit_events.jsonl
wc -l /root/kis-autotrade-v4/reports/daily/2026-03-04/exit_events.jsonl
```
결과:
```json
{"ts": "2026-03-04T09:17:50.856581", "trade_id": 77, "ticker": "000180", "strategy": "D-ORB", "entry": 1623.0, "exit": 1572.0, "pnl_pct": -3.612, "reason": "SL(2.5%)", "hold_min": 0}
{"ts": "2026-03-04T10:18:01.433296", "trade_id": 71, "ticker": "000087", "strategy": "D6", "entry": 14190.0, "exit": 13990.0, "pnl_pct": -1.879, "reason": "TIMEOUT(60min)", "hold_min": 60}
2건
```

최신 로그 (14:14 기준):
```
2026-03-04 14:13:01 [INFO]   id=67 917803 [D2] 현재가 없음 — 스킵
2026-03-04 14:13:01 [INFO]   id=68 888604 [S1] 현재가 없음 — 스킵
2026-03-04 14:13:01 [INFO]   id=69 104733 [D7] 현재가 없음 — 스킵
```

**판정**: ⚠️ PARTIAL (HEALTH-CHECK-001 동일)
- SL 1건, TIMEOUT 1건 정상 청산 확인
- 오픈 3건 현재가 없음 14:14까지 지속 (약 5시간)
- 본 작업에서 fallback 로직 추가로 향후 개선 예정

---

### 항목 5. 데이터 수집 정상성 — 재확인

```sql
SELECT MAX(created_at AT TIME ZONE 'Asia/Seoul'), COUNT(*) FROM v4_tick_data
WHERE DATE(created_at AT TIME ZONE 'Asia/Seoul')=CURRENT_DATE;
```
결과: `2026-03-04 14:10:57+09, 39,636건`

```sql
SELECT MAX(captured_at), COUNT(*) FROM v4_orderbook_realtime
WHERE DATE(captured_at)=CURRENT_DATE;
```
결과: `2026-03-04 14:10:57, 124,407건`

```sql
SELECT count(*), MAX(trade_date) FROM v4_ohlcv_minute
WHERE DATE(trade_date)='2026-03-04';
```
결과: `4,111건, 2026-03-04`

| 테이블 | HEALTH-CHECK-001 건수 | 현재(14:14) 건수 | 증가분 | 상태 |
|--------|---------------------|----------------|--------|------|
| v4_tick_data | 39,104 | 39,636 | +532 | ✅ |
| v4_orderbook_realtime | 121,946 | 124,407 | +2,461 | ✅ |
| v4_ohlcv_minute | 4,008 | 4,111 | +103 | ✅ |

**판정**: ✅ PASS (정상 증가 중)

---

### 항목 6. 텔레그램 보고 정상성 — 재확인

```bash
find /root/kis-autotrade-v4/scripts -name "*hourly*report*"
# → /root/kis-autotrade-v4/scripts/virtual_hourly_report.py (존재)
ls -la /var/log/virtual_hourly_report.log
# → ls: cannot access '/var/log/virtual_hourly_report.log': No such file or directory
grep -r "virtual_hourly_report" /etc/cron.d/
# → (결과 없음)
```

**판정**: ❌ FAIL (HEALTH-CHECK-001 동일, cron 미등록)

---

### 항목 2~6 최종 표

| # | 항목 | HEALTH-CHECK-001 | HEALTH-CHECK-002 재조회 | 변화 |
|---|------|-----------------|------------------------|------|
| 2 | 거래 실적 | ✅ PASS (14건/9건/77건) | ✅ PASS (14건/9건/77건+) | 동일 |
| 3 | L3.3 수급 게이트 | ✅ PASS (BLOCK 4/9건, Fail-Open 0) | ✅ PASS (동일) | 동일 |
| 4 | 청산 로직 | ⚠️ PARTIAL (SL+TIMEOUT 2건, 오픈3건 현재가없음) | ⚠️ PARTIAL (동일) | 동일 |
| 5 | 데이터 수집 | ✅ PASS (39K/121K/4K건) | ✅ PASS (39.6K/124K/4.1K건, 정상증가) | 개선 |
| 6 | 텔레그램 보고 | ❌ FAIL (cron 미등록) | ❌ FAIL (cron 미등록 유지) | 동일 |

**전체**: 항목 1~6 중 4 PASS, 1 PARTIAL, 1 FAIL — HEALTH-CHECK-001과 동일

---

## 보완 항목 2: float(None) 에러 근본 수정

### 에러 상황

```
2026-03-04 09:40:02,039 [ERROR] [MONITOR] 처리 실패: float() argument must be a string or a real number, not 'NoneType'
2026-03-04 09:41:01,407 [ERROR] [MONITOR] 처리 실패: float() argument must be a string or a real number, not 'NoneType'
... (총 8건, 09:40~10:05)
```

### 근본 원인 분석

`scripts/run_unified_engine.py` action_monitor의 가격 조회 로직 (수정 전):

```python
# 수정 전 — float(None) 에러 발생 가능
cur.execute("""SELECT price FROM v4_tick_data WHERE stock_code = %s
              AND tick_time >= NOW() - INTERVAL '5 minutes'
              ORDER BY tick_time DESC LIMIT 1""", (ticker,))
tick_row = cur.fetchone()

if tick_row is None:
    cur.execute("""SELECT last_price FROM v4_orderbook_realtime WHERE stock_code = %s
                  AND captured_at >= NOW() - INTERVAL '5 minutes'
                  ORDER BY captured_at DESC LIMIT 1""", (ticker,))
    ob_row = cur.fetchone()
    current_price = float(ob_row[0]) if ob_row else None  # ← ob_row[0]=NULL이면 에러!
else:
    current_price = float(tick_row[0])  # ← tick_row[0]=NULL이면 에러!
```

**에러 원인**:
1. `ob_row` is not None이지만 `ob_row[0]` (last_price 컬럼)이 NULL인 경우 → `float(None)` TypeError
2. `tick_row` is not None이지만 `tick_row[0]` (price 컬럼)이 NULL인 경우 → `float(None)` TypeError
3. 09:40~10:05 장초반에 해당 종목들의 가격 데이터가 NULL로 반환된 것으로 추정

### 수정 내용 (`scripts/run_unified_engine.py` 라인 938~982)

```python
# 수정 후 — None 가드 + 3차 fallback 추가
# 1차: v4_tick_data 5분 이내
cur.execute("""SELECT price FROM v4_tick_data WHERE stock_code = %s
              AND tick_time >= NOW() - INTERVAL '5 minutes'
              ORDER BY tick_time DESC LIMIT 1""", (ticker,))
tick_row = cur.fetchone()
tick_price = float(tick_row[0]) if tick_row and tick_row[0] is not None else None

current_price = tick_price
ob_row = None
tick_fallback_row = None

if current_price is None:
    # 2차 fallback: v4_orderbook_realtime 5분 이내
    cur.execute("""SELECT last_price FROM v4_orderbook_realtime WHERE stock_code = %s
                  AND captured_at >= NOW() - INTERVAL '5 minutes'
                  ORDER BY captured_at DESC LIMIT 1""", (ticker,))
    ob_row = cur.fetchone()
    current_price = float(ob_row[0]) if ob_row and ob_row[0] is not None else None

if current_price is None:
    # 3차 fallback: v4_tick_data 30분 이내 (장초반 데이터 지연 대응)
    cur.execute("""SELECT price FROM v4_tick_data WHERE stock_code = %s
                  AND tick_time >= NOW() - INTERVAL '30 minutes'
                  ORDER BY tick_time DESC LIMIT 1""", (ticker,))
    tick_fallback_row = cur.fetchone()
    current_price = float(tick_fallback_row[0]) if tick_fallback_row and tick_fallback_row[0] is not None else None
    if current_price is not None:
        logger.info(f"  id={trade_id} {ticker} [{strategy_id}] tick 5분 없음 → 30분 fallback: {current_price:,.0f}")

price_source = "missing"
if tick_price is not None:
    price_source = "tick"
elif ob_row and ob_row[0] is not None:
    price_source = "orderbook"
elif tick_fallback_row and tick_fallback_row[0] is not None:
    price_source = "tick_fallback_30m"
```

**수정 파일**: `/root/kis-autotrade-v4/scripts/run_unified_engine.py` (라인 938~982)

---

## 보완 항목 3: 단위 테스트 추가

**파일**: `/root/kis-autotrade-v4/tests/unit/test_monitor_price_fallback.py`

### 테스트 실행 결과

```
$ /root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/test_monitor_price_fallback.py -v

============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini

tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_tick_row_none_does_not_raise PASSED [  8%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_tick_row_value_none_does_not_raise PASSED [ 16%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_ob_row_value_none_does_not_raise PASSED [ 25%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_tick_5min_available PASSED [ 33%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_tick_missing_ob_fallback PASSED [ 41%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_tick_and_ob_missing_tick30_fallback PASSED [ 50%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_all_missing_returns_none PASSED [ 58%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_tick_takes_priority_over_ob PASSED [ 66%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_ob_takes_priority_over_fallback PASSED [ 75%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_ob_row_none_tuple_vs_none_value PASSED [ 83%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_integer_price_converted_to_float PASSED [ 91%]
tests/unit/test_monitor_price_fallback.py::TestResolvePrice::test_string_price_raises PASSED [100%]

============================== 12 passed in 0.05s ==============================
```

**결과**: 12/12 ALL PASS ✅

### 테스트 케이스 요약

| 테스트 | 시나리오 | 결과 |
|--------|---------|------|
| test_tick_row_none_does_not_raise | tick_row=None | PASS |
| test_tick_row_value_none_does_not_raise | tick_row=(None,) — **핵심 버그 재현** | PASS |
| test_ob_row_value_none_does_not_raise | ob_row=(None,) — **핵심 버그 재현** | PASS |
| test_tick_5min_available | tick 정상 → price=50000 | PASS |
| test_tick_missing_ob_fallback | tick 없음 → ob fallback | PASS |
| test_tick_and_ob_missing_tick30_fallback | tick+ob 없음 → 30분 fallback | PASS |
| test_all_missing_returns_none | 모두 없음 → None | PASS |
| test_tick_takes_priority_over_ob | tick 우선순위 | PASS |
| test_ob_takes_priority_over_fallback | ob 우선순위 | PASS |
| test_ob_row_none_tuple_vs_none_value | None 튜플 vs None 동일 처리 | PASS |
| test_integer_price_converted_to_float | 정수→float 변환 | PASS |
| test_string_price_raises | 문자열 → 에러 (정상) | PASS |

**float(None) 에러 재현 불가 확인**: test_tick_row_value_none_does_not_raise, test_ob_row_value_none_does_not_raise 모두 PASS — 수정 후 동일 조건에서 에러 발생 없음.

---

## 보완 항목 4: 649645 synthetic_BLOCK 잔존 여부 확인

### 조사 결과

**DB 5개 테이블 조회**:
```sql
SELECT 'ohlcv_daily' AS src, COUNT(*) FROM ohlcv_daily WHERE stock_code='649645'
UNION ALL
SELECT 'v4_stock_master', COUNT(*) FROM v4_stock_master WHERE stock_code='649645'
UNION ALL
SELECT 'stock_universe', COUNT(*) FROM stock_universe WHERE stock_code='649645'
UNION ALL
SELECT 'v4_tick_data (전체)', COUNT(*) FROM v4_tick_data WHERE stock_code='649645'
UNION ALL
SELECT 'v4_signals', COUNT(*) FROM v4_signals WHERE stock_code='649645';
```

결과:
```
         src         | count
---------------------+-------
 ohlcv_daily         |     0
 v4_stock_master     |     0
 stock_universe      |     0
 v4_tick_data (전체) |     0
 v4_signals          |     0
(5 rows)
```

**v4_mock_trades에서 649645 조회**:
```sql
SELECT * FROM v4_mock_trades WHERE ticker='649645';
```

결과:
```
 id | trade_date |  ticker | strategy_id | direction | entry_price |
    blocking_reason                              |
----+------------+---------+-------------+-----------+-------------+
 64 | 2026-03-04 | 649645  | D6          | BUY       | (NULL)      |
    | 수급 차단: synthetic_BLOCK                 |
```

### 판정

| 확인 항목 | 결과 |
|----------|------|
| 649645가 ohlcv_daily에 존재하는가? | ❌ 없음 (실제 종목 아님) |
| 649645가 v4_stock_master에 존재하는가? | ❌ 없음 |
| 649645가 stock_universe에 존재하는가? | ❌ 없음 |
| 649645가 v4_tick_data에 존재하는가? | ❌ 없음 (실시간 수신 이력 없음) |
| 649645 생성 방식 | `rng.randint(100_000, 999_999)` → 649645 in [100000, 999999] = True |
| mock_trades에서 처리 결과 | entry_price=NULL, blocking_reason="수급 차단: synthetic_BLOCK" |
| L3.3 게이트 처리 | approved=false → 진입 차단 완료 |

**결론**: 649645는 `make_neutral_signal()`에서 `rng.randint(100_000, 999_999).zfill(6)`으로 생성된 **순수 synthetic 종목코드**. 실제 KOSPI/KOSDAQ 시장에 존재하지 않음. L3.3 수급 게이트에서 `synthetic_BLOCK`으로 정상 차단되었으며, `entry_price=NULL`로 진입 없이 차단 기록만 남음. **잔존 이슈 없음.**

### signal 로직 재점검

08:50 첫 배치에서 synthetic 종목이 신호를 생성하는 것은 `run_unified_engine.py`의 설계상 정상 동작:
- 실제 종목 조회 실패 시 `make_neutral_signal()`으로 fallback (라인 789: `logger.warning("[SIGNAL] 실제 종목 조회 실패, synthetic 사용")`)
- L3.3 게이트에서 synthetic_BLOCK 처리 → 진입 불가 → 차단 기록만 남음
- 문제 없음. synthetic signal은 L3.3 이후 절대 진입 불가 구조.

---

## 전체 작업 요약

### 1. HEALTH-CHECK-001 재조회 결과

| 항목 | 14:00 HEALTH-CHECK-001 | 14:14 HEALTH-CHECK-002 재조회 | 변화 |
|------|----------------------|------------------------------|------|
| 1. 엔진 가동 | ✅ PASS | (재조회 불필요) | — |
| 2. 거래 실적 | ✅ PASS | ✅ PASS (동일) | 동일 |
| 3. L3.3 게이트 | ✅ PASS | ✅ PASS (동일) | 동일 |
| 4. 청산 로직 | ⚠️ PARTIAL | ⚠️ PARTIAL (동일) | 동일 |
| 5. 데이터 수집 | ✅ PASS | ✅ PASS (정상 증가) | 개선 |
| 6. 텔레그램 | ❌ FAIL | ❌ FAIL (cron 미등록) | 동일 |

### 2. float(None) 에러 수정

- **파일**: `scripts/run_unified_engine.py` 라인 938~982
- **수정**: None 가드 추가 (`tick_row[0] is not None`, `ob_row[0] is not None`) + 3차 fallback (30분 tick)
- **테스트**: 12/12 ALL PASS (`tests/unit/test_monitor_price_fallback.py`)
- **에러 재현**: 불가 확인

### 3. 649645 synthetic 확인

- **결론**: synthetic (rng.randint 생성) — 실제 종목 아님
- **처리**: L3.3에서 정상 차단 (approved=false, entry_price=NULL)
- **잔존 이슈**: 없음

---

## 명령어 전체 실행 로그

### 항목 2~6 재조회

```bash
# 항목 2: 거래 실적
PGPASSWORD="KisAuto2026!Secure" psql -h localhost -U kis_admin -d kisautotrade -t -c "
SELECT count(*), strategy_id FROM v4_mock_trades WHERE trade_date='2026-03-04' GROUP BY strategy_id ORDER BY strategy_id;"
# → D-ORB:2, D2:2, D4:2, D5:2, D6:2, D7:2, S1:2 (합계 14건)

PGPASSWORD="KisAuto2026!Secure" psql -h localhost -U kis_admin -d kisautotrade -t -c "
SELECT count(*) FROM v4_virtual_trades_full WHERE DATE(created_at)='2026-03-04';"
# → 9건

PGPASSWORD="KisAuto2026!Secure" psql -h localhost -U kis_admin -d kisautotrade -t -c "
SELECT count(*) FROM v4_virtual_monitor_snapshots WHERE DATE(snapshot_time)='2026-03-04';"
# → 77건

# 항목 3: L3.3 게이트
grep "2026-03-04" /var/log/unified_engine.log | grep -i "synthetic_BLOCK\|synthetic_ALLOW\|L3.3" | head -20
# → 4건 synthetic_BLOCK, 0건 Fail-Open

# 항목 4: 청산
cat /root/kis-autotrade-v4/reports/daily/2026-03-04/exit_events.jsonl
# → 2건 (SL, TIMEOUT)

# 항목 5: 데이터 수집
PGPASSWORD="..." psql ... "SELECT MAX(created_at AT TIME ZONE 'Asia/Seoul'), COUNT(*) FROM v4_tick_data WHERE DATE(...)=CURRENT_DATE;"
# → 14:10:57+09, 39,636건
PGPASSWORD="..." psql ... "SELECT MAX(captured_at), COUNT(*) FROM v4_orderbook_realtime WHERE DATE(...)=CURRENT_DATE;"
# → 14:10:57, 124,407건
PGPASSWORD="..." psql ... "SELECT count(*), MAX(trade_date) FROM v4_ohlcv_minute WHERE DATE(trade_date)='2026-03-04';"
# → 4,111건

# 항목 6: 텔레그램
find /root/kis-autotrade-v4/scripts -name "*hourly*report*"
# → /root/kis-autotrade-v4/scripts/virtual_hourly_report.py (존재)
ls -la /var/log/virtual_hourly_report.log
# → 파일 없음
grep -r "virtual_hourly_report" /etc/cron.d/
# → (결과 없음)
```

### float(None) 에러 원인 파악

```bash
grep -n "action_monitor\|현재가\|current_price\|float\|tick_data" /root/kis-autotrade-v4/scripts/run_unified_engine.py | head -30
# → 938~982라인에서 가격 조회 로직 확인
```

```
수정 전 라인 956:
    current_price = float(ob_row[0]) if ob_row else None
    # ← ob_row=(None,)이면 ob_row는 True이지만 ob_row[0]=None → float(None) TypeError

수정 전 라인 958:
    current_price = float(tick_row[0])
    # ← tick_row[0]=None이면 → float(None) TypeError
```

### 코드 수정

```bash
# Edit 도구로 scripts/run_unified_engine.py 라인 938~982 수정
# None 가드 추가 + 3차 fallback (30분 tick) 추가
```

### 단위 테스트 작성 및 실행

```bash
# tests/unit/test_monitor_price_fallback.py 작성
/root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/test_monitor_price_fallback.py -v
# → 12/12 ALL PASS in 0.05s
```

### 649645 synthetic 확인

```bash
echo "649645 in range 100000..999999: $(python3 -c 'print(100000 <= 649645 <= 999999)')"
# → True (synthetic 범위 내)

PGPASSWORD="..." psql ... <<'SQL'
SELECT 'ohlcv_daily' AS src, COUNT(*) FROM ohlcv_daily WHERE stock_code='649645'
UNION ALL
SELECT 'v4_stock_master', COUNT(*) FROM v4_stock_master WHERE stock_code='649645'
UNION ALL
SELECT 'stock_universe', COUNT(*) FROM stock_universe WHERE stock_code='649645'
UNION ALL
SELECT 'v4_tick_data (전체)', COUNT(*) FROM v4_tick_data WHERE stock_code='649645'
UNION ALL
SELECT 'v4_signals', COUNT(*) FROM v4_signals WHERE stock_code='649645';
SQL
# → 모두 0건 (실제 종목 아님 확인)

PGPASSWORD="..." psql ... <<'SQL'
SELECT * FROM v4_mock_trades WHERE ticker='649645' LIMIT 5;
SQL
# → 1건, blocking_reason="수급 차단: synthetic_BLOCK", entry_price=NULL (정상 차단)
```

---

## 잔존 이슈 정리

| 이슈 | 수준 | 상태 | 비고 |
|------|------|------|------|
| 오픈 포지션 3건 현재가 없음 지속 (09:16~14:14) | ⚠️ 높음 | 미해결 | 30분 fallback 추가됨. 실제 tick 수신 여부는 KIS API 설정 문제 |
| 텔레그램 hourly 보고 cron 미등록 | ⚠️ 중간 | 미해결 (root 권한 필요) | /etc/cron.d/kis_virtual_hourly 생성 필요 |
| float(None) 에러 | ✅ 해결 | 코드 수정 + 테스트 12/12 PASS | |
| 649645 synthetic_BLOCK | ✅ 확인 | 정상 동작 확인 | 잔존 이슈 없음 |

*보고 작성: Claude (claudebot) @ 2026-03-04 14:14 KST*
