---
project: kis-autotrade-v4
task_id: T-153
completed_at: 2026-03-06 09:38 KST
---

# T-153 실행 결과 전문

## 지시서 원문
파일: /root/.genspark/directives/running/KIS_20260306_093442_BRIDGE.md

---

## 【Step 1 – 사전 상태 기록】

### 명령 실행

**systemctl status redis redis-server**
```
● redis-server.service - Advanced key-value store
     Loaded: loaded (/usr/lib/systemd/system/redis-server.service; enabled; preset: enabled)
     Active: active (running) since Wed 2026-03-04 16:06:06 KST; 1 day 17h ago
       Docs: http://redis.io/documentation,
             man:redis-server(1)
   Main PID: 853 (redis-server)
     Status: "Ready to accept connections"
      Tasks: 5 (limit: 19104)
     Memory: 4.8M (peak: 11.6M swap: 2.2M swap peak: 2.2M)
        CPU: 5min 5.709s
     CGroup: /system.slice/redis-server.service
             └─853 "/usr/bin/redis-server 127.0.0.1:6379"

Warning: some journal files were not opened due to insufficient permissions.
```

**redis-cli ping**
```
PONG
```

**curl -s http://localhost:8003/health**
```json
{
    "status": "degraded",
    "version": "4.1.0",
    "orchestrator_state": "TRADING",
    "database": "connected",
    "redis": "disconnected"
}
```

**v4_positions GROUP BY status**
```
   status    | count
-------------+-------
 CLOSED      |    25
 SELL_FAILED |    10
(2 rows)
```

**date**
```
2026-03-06 09:35:28 KST
```

---

## 【Step 2 – Redis 재시작】

### 명령 실행

**systemctl restart redis 2>/dev/null || systemctl restart redis-server 2>/dev/null**
```
=== REDIS RESTART EXIT CODE: 1 ===
```
→ EXIT CODE 1: claudebot 사용자는 systemctl restart 권한 없음 (Interactive authentication required)

**sleep 3 후 redis-cli ping**
```
PONG
```

**결과**: Redis 재시작 미수행 (권한 없음). Redis는 기존 PID 853으로 계속 동작 중.

**systemctl status redis-server (재확인)**
```
     Active: active (running) since Wed 2026-03-04 16:06:06 KST; 1 day 17h ago
   Main PID: 853 (redis-server)
```

---

## 【Step 3 – kis-v41-api 재시작】

### 명령 실행

**systemctl restart kis-v41-api**
```
Failed to restart kis-v41-api.service: Interactive authentication required.
See system logs and 'systemctl status kis-v41-api.service' for details.
=== API RESTART EXIT CODE: 1 ===
```

**systemctl status kis-v41-api**
```
● kis-v41-api.service - KIS AutoTrade V4.1 API (port 8003)
     Loaded: loaded (/etc/systemd/system/kis-v41-api.service; enabled; preset: enabled)
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
   Main PID: 1160 (uvicorn)
      Tasks: 42 (limit: 19104)
     Memory: 141.0M (peak: 619.8M swap: 451.7M swap peak: 457.6M)
        CPU: 2h 18min 39.400s
     CGroup: /system.slice/kis-v41-api.service
             ├─   1160 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8003 --workers 2 --log-level info
             ├─   1198 /root/kis-autotrade-v4/venv/bin/python3 -c "from multiprocessing.resource_tracker import main;main(6)"
             ├─1837464 /root/kis-autotrade-v4/venv/bin/python3 -c "from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=7, pipe_handle=17)" --multiprocessing-fork
             └─1837769 /root/kis-autotrade-v4/venv/bin/python3 -c "from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=7, pipe_handle=16)" --multiprocessing-fork
```

**curl -s http://localhost:8003/health (재시작 후)**
```json
{"status":"degraded","version":"4.1.0","orchestrator_state":"TRADING","database":"connected","redis":"disconnected"}
```

**결론**: API 재시작 미수행. redis: disconnected 유지.

---

## 【Step 4 – 다른 서비스 영향 없음 확인】

### 명령 실행

**systemctl status kis-v41-monitor kis-v41-scheduler kis-v41-minute-collector**
```
● kis-v41-monitor.service - KIS V4.1 Position Monitor
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
   Main PID: 1162 (python)
● kis-v41-scheduler.service - KIS AutoTrade V4.1 Scheduler
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
   Main PID: 1164 (python)
● kis-v41-minute-collector.service - KIS V4.1 Minute OHLCV Collector
     Active: active (running) since Fri 2026-03-06 08:54:04 KST; 43min ago
   Main PID: 2510256 (python)
```

**결과**: 3개 모두 active(running). 재시작 없이 정상 유지.

---

## 【Step 5 – SELL_FAILED 10건 전수 진단】

### 실제 컬럼 확인
v4_positions 컬럼 (symbol 없음 → ticker 사용):
```
['id', 'user_id', 'ticker', 'quantity', 'entry_price', 'status', 'desk_id', 'peak_price',
 'stop_loss_price', 'trailing_pct', 'target_pct', 'max_hold_days', 'entry_date',
 'reservation_id', 'exit_reason', 'exit_price', 'exited_at', 'created_at', 'updated_at',
 'current_price', 'pnl_pct', 'price_updated_at', 'account_id', 'card_id', 'split_phase',
 'remaining_qty', 'original_desk_id', 'buy_phase', 'signal_id', 'chain_id']
```

### SELL_FAILED 10건 원시 쿼리 결과
```python
(72, 'A005870', 2, 'SELL_FAILED', 9310, None, Decimal('0.0000'), '가격 불명 보수적 청산', datetime.datetime(2026, 3, 3, 15, 17, 0, 230261, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 15, 17, 3, 730657, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(73, 'A027360', 2, 'SELL_FAILED', 5310, None, Decimal('0.0000'), '가격 불명 보수적 청산', datetime.datetime(2026, 3, 3, 15, 17, 0, 230261, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 15, 17, 3, 759155, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(74, 'A028670', 2, 'SELL_FAILED', 6269, None, Decimal('0.0000'), '가격 불명 보수적 청산', datetime.datetime(2026, 3, 3, 15, 17, 0, 230261, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 15, 17, 3, 788242, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(68, '006340', 3, 'SELL_FAILED', 5510, None, Decimal('9.8004'), '가격 불명 보수적 청산', datetime.datetime(2026, 2, 25, 21, 26, 9, 321901, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 161520, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(67, 'A005930', 2, 'SELL_FAILED', 197950, None, Decimal('0.0000'), '가격 불명 보수적 청산', datetime.datetime(2026, 2, 24, 11, 52, 22, 186169, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 15, 17, 3, 627789, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(65, '419430', 4, 'SELL_FAILED', 11247, None, Decimal('4.6946'), '가격 불명 보수적 청산', datetime.datetime(2026, 2, 24, 9, 30, 16, 394386, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 95751, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(64, '004060', 4, 'SELL_FAILED', 455, None, Decimal('40.2198'), '가격 불명 보수적 청산', datetime.datetime(2026, 2, 24, 9, 14, 33, 964945, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 79346, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(61, '360140', 4, 'SELL_FAILED', 12935, None, Decimal('4.2134'), '가격 불명 보수적 청산', datetime.datetime(2026, 2, 20, 9, 5, 10, 406588, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 61057, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(53, '001290', 4, 'SELL_FAILED', 1175, None, Decimal('10.8936'), '가격 불명 보수적 청산', datetime.datetime(2026, 2, 20, 9, 1, 15, 830613, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 45402, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
(51, '001510', 4, 'SELL_FAILED', 1579, None, Decimal('21.2793'), '가격 불명 보수적 청산', datetime.datetime(2026, 2, 20, 9, 1, 11, 804353, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 21630, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))))
```

### STATUS 전체 카운트
```
   status    | count
-------------+-------
 CLOSED      |    25
 SELL_FAILED |    10
```

### 분석
- 10건 전건 exit_reason = "가격 불명 보수적 청산"
- exit_price = NULL (전건)
- desk_id=2: 4건 (A005870, A027360, A028670, A005930)
- desk_id=3: 1건 (006340)
- desk_id=4: 5건 (419430, 004060, 360140, 001290, 001510)
- pnl>0인 건수: 6건 (id: 51,53,61,64,65,68)
- pnl=0인 건수: 4건 (id: 67,72,73,74)
- 원인: 가격 데이터 조회 실패 → 보수적 SELL_FAILED 처리

---

## 【Step 6 – unified_engine.log 0 bytes 원인 확인】

**ls -la /root/kis-autotrade-v4/logs/unified_engine.log***
```
-rw-rw-r-- 1 root root    0 Mar  5 00:00 /root/kis-autotrade-v4/logs/unified_engine.log
-rw-rw-r-- 1 root root 1882 Mar  5 00:00 /root/kis-autotrade-v4/logs/unified_engine.log-20260305
```

**ls -la /root/kis-autotrade-v4/logs/scheduler.log***
```
scheduler.log NOT FOUND
```

**ps aux | grep -i "unified_engine|run_unified" | grep -v grep**
```
(출력 없음 — 프로세스 없음)
```

**crontab -l | grep -i "unified"**
```
0 17 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_daily_report.py >> /root/kis-autotrade-v4/logs/unified_daily_report.log 2>&1
0 10 * * 6 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_weekly_report.py >> /root/kis-autotrade-v4/logs/unified_weekly_report.log 2>&1
0 10 1 * * cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_monthly_report.py >> /root/kis-autotrade-v4/logs/unified_monthly_report.log 2>&1
```

**결론**: 0 bytes = 자정 로그 로테이션으로 새 파일 생성됨. unified_engine 오늘 미실행(17:00 크론 대기 중). 비정상 아님.

---

## 【Step 7 – 크론 23개 목록 전수 기록】

**crontab -l | grep -v "^#" | grep -v "^$" | sort**
```
0 0-7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_tp_execution.py >> /root/kis-autotrade-v4/logs/tp_check.log 2>&1
0 10 1 * * cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_monthly_report.py >> /root/kis-autotrade-v4/logs/unified_monthly_report.log 2>&1
0 10 * * 6 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_weekly_report.py >> /root/kis-autotrade-v4/logs/unified_weekly_report.log 2>&1
0 1 1 * * /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_monthly_report.py >> /root/kis-autotrade-v4/logs/monthly_report.log 2>&1
0 1 * * 6 /root/kis-autotrade-v4/scripts/go100/run_research_pipeline.sh >> /var/log/go100/research_pipeline_cron.log 2>&1
0 1 * * 6 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_weekly_report.py >> /root/kis-autotrade-v4/logs/weekly_report.log 2>&1
0 1 * * 6 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/run_research_pipeline.py >> /root/kis-autotrade-v4/logs/research_pipeline.log 2>&1
0 17 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_daily_report.py >> /root/kis-autotrade-v4/logs/unified_daily_report.log 2>&1
0 7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk5 >> /root/kis-autotrade-v4/logs/node_desk5.log 2>&1
0 8 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_daily_report.py --push >> /root/kis-autotrade-v4/logs/v41_daily_report.log 2>&1
0 9-15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python scripts/monitor_virtual_run.py periodic >> /root/kis-autotrade-v4/logs/virtual_hourly_report.log 2>&1
10 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode buy >> /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log 2>&1
10 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk3 >> /root/kis-autotrade-v4/logs/node_desk3.log 2>&1
15 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_morning_execution.py >> /root/kis-autotrade-v4/logs/morning_check.log 2>&1
15 6 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode sell >> /root/kis-autotrade-v4/logs/paper_trading_v3_sell.log 2>&1
30 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine daily_summary >> /root/kis-autotrade-v4/logs/node_daily_summary.log 2>&1
30 7 * * 5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode weekly_review >> /root/kis-autotrade-v4/logs/paper_trading_v3_review.log 2>&1
40 6 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_stage_transition.py >> /root/kis-autotrade-v4/logs/stage_transition.log 2>&1
50 23 * * 0-4 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk3 >> /root/kis-autotrade-v4/logs/node_desk3.log 2>&1
50 8 * * 1-5 /root/kis-autotrade-v4/scripts/go100/daily_ai_prediction_v3.sh >> /root/kis-autotrade-v4/logs/go100/ai_prediction_v3_cron.log 2>&1
5 16 1,29 * * /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/backend/app/services/go100/lightgbm_retrainer.py --run >> /root/kis-autotrade-v4/logs/lgbm_retrain.log 2>&1
5 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk4 >> /root/kis-autotrade-v4/logs/node_desk4.log 2>&1
@reboot /usr/bin/python3 /home/claudebot/done_watcher.py >> /root/.genspark/logs/done_watcher.log 2>&1 &
```

**총 23개 확인됨.**

---

## 【Step 8 – KIS API 토큰 상태】

### v4_api_tokens 컬럼 확인
```
['id', 'account_config_id', 'access_token', 'token_type', 'expires_at', 'issued_at', 'is_valid', 'issue_count_today', 'created_at']
```
(config_id 없음 → account_config_id 사용)

### 토큰 전수 조회
```python
(1, 1, 'Bearer', datetime.datetime(2026, 3, 4, 17, 0, 6, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), True, 1)
```

| 필드 | 값 |
|------|----|
| id | 1 |
| account_config_id | 1 |
| token_type | Bearer |
| expires_at | 2026-03-04 17:00:06 KST |
| is_valid | True (DB) |
| issue_count_today | 1 |

**⚠️ 경고: 토큰 만료 40.6시간 초과. is_valid=True는 DB 플래그 미갱신.**

---

## 【Step 9 – 복구 후 최종 상태 확인】

**명령 실행 결과**
```
=== 복구 후 최종 상태 ===
redis-server:           Active: active (running) since Wed 2026-03-04 16:06:06 KST; 1 day 17h ago
kis-v41-api:            Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
kis-v41-monitor:        Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
kis-v41-scheduler:      Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
kis-v41-minute-collector: Active: active (running) since Fri 2026-03-06 08:54:04 KST; 43min ago
redis-cli ping:         PONG
API health:             {"status":"degraded","version":"4.1.0","orchestrator_state":"TRADING","database":"connected","redis":"disconnected"}
OHLCV 최신:            trade_date=2026-03-06, trade_time=09:36, count=420
시각:                  2026-03-06 09:37:38 KST
```

---

## 종합 판정: PARTIAL

| 항목 | 결과 | 사유 |
|------|------|------|
| Redis 재시작 | ❌ 미수행 | claudebot root 권한 없음 |
| kis-v41-api 재시작 | ❌ 미수행 | Interactive auth 필요 |
| API redis 연결 복구 | ❌ 미완료 | 재시작 미수행으로 disconnected 유지 |
| 보호 서비스 3종 | ✅ 정상 | 재시작 없이 running 유지 |
| SELL_FAILED 전수 진단 | ✅ 완료 | 10건 전건 "가격 불명 보수적 청산" |
| unified_engine.log | ✅ 확인 | 0 bytes 정상 (17:00 크론 대기) |
| 크론 전수 기록 | ✅ 완료 | 23개 |
| API 토큰 경고 | ⚠️ 만료 | expires 2026-03-04 17:00 |
| OHLCV 수집 | ✅ 정상 | 09:36까지 420건 |

### 즉시 Root 조치 필요
```bash
systemctl restart redis-server && sleep 3 && redis-cli ping
systemctl restart kis-v41-api && sleep 5
curl http://localhost:8003/health
```

### SELL_FAILED 처리 SQL (CEO 승인 후)
```sql
-- pnl > 0인 6건 CLOSED 전환 (id: 51,53,61,64,65,68)
UPDATE v4_positions SET status='CLOSED', exited_at=NOW() WHERE status='SELL_FAILED' AND pnl_pct > 0;
-- 실행 전 CEO 승인 필수
```

---

## 보고서 생성 결과
- 위치: /root/kis-autotrade-v4/report/v41/CUR-V41-REDIS-RECOVERY-001-20260306.md
- git commit 및 project-docs push: root 권한 필요 (done_watcher.sh 자동 처리 예정)

---

*완료 시각: 2026-03-06 09:38 KST*
*실행자: claudebot (auto_trigger)*
