---
project: KIS + GO100
task_id: 079-2
completed_at: 2026-03-05T09:46:00 KST
---

# Task 079-2 실행 결과: 폭락장 장중 모니터링 2차 + GO100 매도 결과 확인

## 실행 일시
2026-03-05 09:46:00 KST

---

## Phase 1: READ-ONLY 서비스 상태

### Step 1-1: 서비스 확인

```
실행 명령: systemctl status kis-v41-api kis-v41-monitor kis-v41-scheduler

● kis-v41-api.service - KIS AutoTrade V4.1 API (port 8003)
     Loaded: loaded (/etc/systemd/system/kis-v41-api.service; enabled; preset: enabled)
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 17h ago
   Main PID: 1160 (uvicorn)
      Tasks: 42 (limit: 19104)
     Memory: 586.4M (peak: 619.8M swap: 20.5M swap peak: 447.9M)
        CPU: 29min 7.575s
     CGroup: /system.slice/kis-v41-api.service
             ├─   1160 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8003 --workers 2 --log-level info
             ├─   1198 /root/kis-autotrade-v4/venv/bin/python3 -c "from multiprocessing.resource_tracker import main;main(6)"
             ├─1837464 /root/kis-autotrade-v4/venv/bin/python3 -c "from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=7, pipe_handle=17)" --multiprocessing-fork
             └─1837769 /root/kis-autotrade-v4/venv/bin/python3 -c "from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=7, pipe_handle=16)" --multiprocessing-fork

Warning: some journal files were not opened due to insufficient permissions.

● kis-v41-monitor.service - KIS V4.1 Position Monitor
     Loaded: loaded (/etc/systemd/system/kis-v41-monitor.service; enabled; preset: enabled)
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 17h ago
   Main PID: 1162 (python)
      Tasks: 1 (limit: 19104)
     Memory: 8.4M (peak: 16.9M swap: 9.0M swap peak: 9.0M)
        CPU: 434ms
     CGroup: /system.slice/kis-v41-monitor.service
             └─1162 /root/kis-autotrade-v4/venv/bin/python /root/kis-autotrade-v4/backend/app/services/trading/v4_position_monitor.py

Warning: some journal files were not opened due to insufficient permissions.

● kis-v41-scheduler.service - KIS AutoTrade V4.1 Scheduler
     Loaded: loaded (/etc/systemd/system/kis-v41-scheduler.service; enabled; preset: enabled)
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 17h ago
   Main PID: 1164 (python)
      Tasks: 5 (limit: 19104)
     Memory: 106.5M (peak: 107.0M swap: 12.1M swap peak: 12.6M)
        CPU: 19.864s
     CGroup: /system.slice/kis-v41-scheduler.service
             └─1164 /root/kis-autotrade-v4/venv/bin/python -m app.services.scheduler.daily_scheduler

Warning: some journal files were not opened due to insufficient permissions.
```

**결과: 서비스 3/3 모두 active (running) ✅**
- kis-v41-api: ACTIVE (17h 가동)
- kis-v41-monitor: ACTIVE (17h 가동)
- kis-v41-scheduler: ACTIVE (17h 가동)

---

### Step 1-2: 오늘 가상매매 현황 (2026-03-05)

```sql
SELECT strategy_id, COUNT(*) as cnt,
  COUNT(*) FILTER (WHERE notes LIKE '%"approved": true%') as approved,
  COUNT(*) FILTER (WHERE notes LIKE '%"approved": false%') as blocked,
  COUNT(*) FILTER (WHERE exit_price IS NOT NULL) as exited,
  ROUND(AVG(pnl_pct)::numeric, 4) as avg_pnl
FROM v4_mock_trades
WHERE created_at::date = '2026-03-05'
GROUP BY strategy_id ORDER BY strategy_id;
```

결과:
```
 strategy_id | cnt | approved | blocked | exited | avg_pnl
-------------+-----+----------+---------+--------+---------
 D2          |   1 |        0 |       1 |      0 |
 D4          |   1 |        0 |       1 |      0 |
 D5          |   2 |        1 |       1 |      0 |
 D6          |   2 |        1 |       1 |      0 |
 D7          |   2 |        0 |       2 |      0 |
 D-ORB       |   2 |        1 |       1 |      0 |
 S1          |   1 |        0 |       1 |      0 |
(7 rows)
```

**분석:**
- 총 11건 신호 발생 (7개 전략)
- approved: D5(1), D6(1), D-ORB(1) = 3건
- blocked: 8건 (폭락장 필터 정상 작동 추정)
- exited: 0건 (모두 오픈 포지션)
- avg_pnl: NULL (아직 미청산)

---

### Step 1-3: TP 발동 여부 (075 핵심 검증)

```sql
SELECT id, strategy_id, ticker, entry_price, exit_price, pnl_pct, notes
FROM v4_mock_trades
WHERE created_at::date = '2026-03-05' AND pnl_pct > 0;
```

결과:
```
 id | strategy_id | ticker | entry_price | exit_price | pnl_pct | notes
----+-------------+--------+-------------+------------+---------+-------
(0 rows)
```

**결과: TP 발동 없음 — 오늘 장중 수익 실현 없음 (폭락장 영향)**

---

### Step 1-4: 079-1차 오픈 포지션 PnL 추적

```sql
SELECT id, strategy_id, ticker, entry_price,
  (SELECT close FROM ohlcv_daily WHERE stock_code = v.ticker ORDER BY date DESC LIMIT 1) as latest_close,
  pnl_pct
FROM v4_mock_trades v
WHERE created_at::date = '2026-03-05' AND notes LIKE '%"approved": true%' AND exit_price IS NULL;
```

결과:
```
 id  | strategy_id | ticker | entry_price | latest_close | pnl_pct
-----+-------------+--------+-------------+--------------+---------
  98 | D6          | 108196 |    113883.0 |              |
 100 | D-ORB       | 195359 |     83479.0 |              |
 101 | D5          | 328284 |    140667.0 |              |
(3 rows)
```

**분석:**
- ID 98 (D6, 108196): entry 113,883원, latest_close N/A (ohlcv_daily 미매칭)
- ID 100 (D-ORB, 195359): entry 83,479원, latest_close N/A
- ID 101 (D5, 328284): entry 140,667원, latest_close N/A
- latest_close가 NULL인 이유: ohlcv_daily의 stock_code 형식과 v4_mock_trades.ticker 형식 불일치 가능성 (ETF 코드 포함)
- pnl_pct도 NULL — 장중 실시간 체결가 미업데이트 상태

---

## Phase 2: GO100 매도 결과 확인

### Step 2-1: GO100 매도 체결

**참고: go100_live_orders 테이블 컬럼 확인 후 수정 실행**
- 원본 쿼리의 `id` 컬럼이 존재하지 않음 → 실제 PK는 `order_id`, ticker는 `stock_code`

```sql
SELECT order_id, stock_code, order_type, quantity, filled_price, status, created_at
FROM go100_live_orders
WHERE created_at::date = '2026-03-05' ORDER BY created_at;
```

결과:
```
 order_id | stock_code | order_type | quantity | filled_price | status |          created_at
----------+------------+------------+----------+--------------+--------+-------------------------------
       33 | 027360     | SELL       |      406 |         4889 | FILLED | 2026-03-05 09:10:04.357816+09
       34 | 028670     | SELL       |      421 |         5043 | FILLED | 2026-03-05 09:10:04.357816+09
       35 | 0080G0     | SELL       |      144 |        13544 | FILLED | 2026-03-05 09:10:04.357816+09
(3 rows)
```

**결과: GO100 SELL 3건 전부 FILLED ✅**
- 027360: 406주 × 4,889원 = 약 1,984,934원
- 028670: 421주 × 5,043원 = 약 2,123,103원
- 0080G0: 144주 × 13,544원 = 약 1,950,336원
- 체결 시각: 09:10:04 KST (장 개시 직후 일괄 매도)

---

### Step 2-2: GO100 Commander 의사결정

```sql
SELECT id, decision_type, ticker, reasoning, created_at
FROM go100_commander_decisions
WHERE created_at::date = '2026-03-05' ORDER BY created_at;
```

결과:
```
ERROR: column "id" does not exist
```

테이블 존재 확인:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name = 'go100_commander_decisions';
-- (0 rows)
```

**결과: go100_commander_decisions 테이블 미존재 → Commander decision 로깅 미구현 확인**
→ 지시서 명시대로: Task 082에서 보완 예정

---

### Step 2-3: GO100 모의투자 세션

```sql
SELECT session_id, status, total_trades, current_capital, total_return
FROM go100_paper_trading_sessions WHERE status = 'ACTIVE';
```

결과:
```
 session_id | status | total_trades | current_capital | total_return
------------+--------+--------------+-----------------+--------------
          2 | ACTIVE |            0 |     10000000.00 |
(1 row)
```

**결과:**
- ACTIVE 세션 1개 (session_id=2)
- total_trades: 0 (모의투자 미체결)
- current_capital: 10,000,000원 (초기자본 그대로)
- total_return: NULL (거래 없음)
- **주의**: 076 Task에서 모의투자 0체결 해결 작업이 있었으나, 모의투자는 여전히 미거래 상태

---

## Phase 3: 에러 로그 스캔

### unified_engine.log
```
grep -i "error\|exception\|traceback" /root/kis-autotrade-v4/logs/unified_engine.log | tail -20
```
결과: 파일 없음 (unified_engine.log 미존재)

### paper_trading_v3_buy.log
```
grep -i "error" /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log | tail -10
```
결과: 파일 없음 (paper_trading_v3_buy.log 미존재)

### 대체 로그 확인
```
ls /root/kis-autotrade-v4/logs/ | grep 2026-03-05
→ app_2026-03-05.log (67,555줄)
→ error_2026-03-05.log (0줄)
→ trading_2026-03-05.log
```

### error_2026-03-05.log
```
grep -i "error\|exception\|traceback" /root/kis-autotrade-v4/logs/error_2026-03-05.log
결과: 0줄 (에러 없음)
```

### app_2026-03-05.log (마지막 5줄)
```
2026-03-05 09:44:59 | INFO     | backend.app.services.system.orchestrator:_run_trading_cycle:392 | [CYCLE %s] position check: %s
2026-03-05 09:44:59 | WARNING  | backend.app.services.execution.fund_pool:rebuild_from_db:518 | [FundPool] positions lacks desk_id column; desk_used rebuilt from v4_reservations only. TODO: Phase 3 migration.
2026-03-05 09:44:59 | INFO     | backend.app.services.execution.fund_pool:rebuild_from_db:569 | rebuild_from_db 완료: total=2098369 available=0 reserved=0 invested=2098369 desk_used={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
2026-03-05 09:44:59 | INFO     | backend.app.services.system.orchestrator:_run_trading_cycle:415 | [CYCLE %s] signals generated: %s
2026-03-05 09:44:59 | INFO     | backend.app.services.system.orchestrator:_run_trading_cycle:443 | [CYCLE %s] done: %sms, signals=%s, buy_ok=%s, buy_fail=%s
```

**결과:**
- ERROR 레벨 로그 없음 ✅
- WARNING 1건: FundPool desk_id 컬럼 미존재 (Phase 3 마이그레이션 예정 사항, 기존 인지 이슈)
- 오케스트레이터 정상 사이클 동작 확인
- total=2,098,369원 전액 invested 상태 (available=0, 추가 매수 불가)

---

## Phase 4: 시스템 리소스

```
free -h | head -3
```
결과:
```
               total        used        free      shared  buff/cache   available
Mem:            15Gi       7.1Gi       1.7Gi       155Mi       7.4Gi       8.6Gi
Swap:          8.0Gi       393Mi       7.6Gi
```

```
df -h / | tail -1
```
결과:
```
/dev/vda2        99G   63G   32G  67% /
```

**결과:**
- RAM: 15Gi 중 7.1Gi 사용 (47%), available 8.6Gi — 정상 ✅
- Swap: 8Gi 중 393Mi 사용 (5%) — 정상 ✅
- 디스크: 99G 중 63G 사용 (67%) — 정상 ✅

---

## 완료 조건 체크

| 항목 | 결과 | 상태 |
|------|------|------|
| 서비스 3/3 ACTIVE 확인 | kis-v41-api, monitor, scheduler 모두 active | ✅ |
| 오늘 거래 현황 집계 | 11건 신호, approved 3건, blocked 8건 | ✅ |
| TP 발동 여부 확인 (075 검증) | TP 발동 없음 (폭락장 영향) | ✅ |
| GO100 SELL 3건 결과 확인 | 3건 전부 FILLED (09:10:04 KST) | ✅ |
| 에러 로그 이상 없음 | error.log 0줄, WARNING 1건 (기존 인지 이슈) | ✅ |

---

## 종합 요약

### KIS V4.1 상태
- **서비스**: 정상 가동 (3/3 ACTIVE, 17h+)
- **장중 신호**: 11건 발생, 8건 차단 (폭락장 필터 정상 동작 추정), 3건 승인
- **오픈 포지션 3건**: D6(108196), D-ORB(195359), D5(328284) — 아직 미청산
- **TP**: 발동 없음 (폭락장으로 수익 실현 불가)
- **자금 상태**: 2,098,369원 전액 투자 중, available=0

### GO100 상태
- **실전 매도**: 3건 전부 FILLED ✅ (09:10:04 장 개시 직후)
  - 027360: 406주 × 4,889원 FILLED
  - 028670: 421주 × 5,043원 FILLED
  - 0080G0: 144주 × 13,544원 FILLED
- **Commander Decision 로깅**: 미구현 (go100_commander_decisions 테이블 없음) → Task 082 보완
- **모의투자 세션**: ACTIVE이나 total_trades=0 (미체결 지속)

### 후속 조치 필요
1. GO100 Commander Decision 로깅 테이블 생성 (Task 082)
2. v4_mock_trades의 latest_close 조회 미매칭 원인 파악 (stock_code 형식 차이)
3. 폭락장 종료 후 오픈 포지션 3건 청산 결과 확인 (Task 079-3)
4. FundPool desk_id 컬럼 Phase 3 마이그레이션 일정 확인
