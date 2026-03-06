---
project: kis-autotrade-v4
task_id: T-152
completed_at: 2026-03-06T09:39:02+09:00
---

# T-152 실행 결과 전문

## 지시서 원문

Task ID: T-152  제목: T-151 CRITICAL 이슈 3건 진단 + 가능 범위 복구  서버: 211 (kis-autotrade-v4)
우선순위: P0-CRITICAL  예상 시간: 15분  의존성: T-151

---

## 실행 내역 및 결과

### 사전 작업: HANDOVER.md / CEO-DIRECTIVES.md 읽기

- /root/project-docs/kis-autotrade-v4/HANDOVER.md 읽기 완료 (v10.11)
  - 직전 완료: T-151 (03-06 장중 전체 시스템 점검)
  - 주요 상태: 4서비스 PASS, 분봉 09:18 수집, DB 40GB, strategy_cards 60, open_positions 0 (SELL_FAILED 10건), 가상매매 03-06 BUY 11건, Redis disconnected WARN, KIS토큰DB만료(실API 정상)
- /root/project-docs/kis-autotrade-v4/CEO-DIRECTIVES.md 읽기 완료 (v1.4)

---

### 작업 1 – SELL_FAILED 10건 진단

#### 실행 쿼리

v4_positions 스키마 확인 (symbol → ticker):
```
COLUMNS: ['id', 'user_id', 'ticker', 'quantity', 'entry_price', 'status', 'desk_id', 'peak_price', 'stop_loss_price', 'trailing_pct', 'target_pct', 'max_hold_days', 'entry_date', 'reservation_id', 'exit_reason', 'exit_price', 'exited_at', 'created_at', 'updated_at', 'current_price', 'pnl_pct', 'price_updated_at', 'account_id', 'card_id', 'split_phase', 'remaining_qty', 'original_desk_id', 'buy_phase', 'signal_id', 'chain_id']
```

#### SELL_FAILED 전체 조회 결과

```python
=== SELL_FAILED 포지션 목록 ===
총 10건
(72, 'A005870', 'SELL_FAILED', 9310, None, Decimal('0.0000'), datetime.datetime(2026, 3, 3, 15, 17, 0, 230261, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 15, 17, 3, 730657, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', 4, None)
(73, 'A027360', 'SELL_FAILED', 5310, None, Decimal('0.0000'), datetime.datetime(2026, 3, 3, 15, 17, 0, 230261, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 15, 17, 3, 759155, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', 4, None)
(74, 'A028670', 'SELL_FAILED', 6269, None, Decimal('0.0000'), datetime.datetime(2026, 3, 3, 15, 17, 0, 230261, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 15, 17, 3, 788242, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', 4, None)
(68, '006340', 'SELL_FAILED', 5510, None, Decimal('9.8004'), datetime.datetime(2026, 2, 25, 21, 26, 9, 321901, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 161520, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', 7, None)
(67, 'A005930', 'SELL_FAILED', 197950, None, Decimal('0.0000'), datetime.datetime(2026, 2, 24, 11, 52, 22, 186169, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 15, 17, 3, 627789, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', 4, None)
(65, '419430', 'SELL_FAILED', 11247, None, Decimal('4.6946'), datetime.datetime(2026, 2, 24, 9, 30, 16, 394386, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 95751, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', 1, None)
(64, '004060', 'SELL_FAILED', 455, None, Decimal('40.2198'), datetime.datetime(2026, 2, 24, 9, 14, 33, 964945, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 79346, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', 7, None)
(61, '360140', 'SELL_FAILED', 12935, None, Decimal('4.2134'), datetime.datetime(2026, 2, 20, 9, 5, 10, 406588, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 61057, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', None, None)
(53, '001290', 'SELL_FAILED', 1175, None, Decimal('10.8936'), datetime.datetime(2026, 2, 20, 9, 1, 15, 830613, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 45402, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', None, None)
(51, '001510', 'SELL_FAILED', 1579, None, Decimal('21.2793'), datetime.datetime(2026, 2, 20, 9, 1, 11, 804353, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), datetime.datetime(2026, 3, 3, 12, 25, 45, 21630, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400))), '가격 불명 보수적 청산', None, None)

=== v4_positions 상태별 건수 ===
('CLOSED', 25)
('SELL_FAILED', 10)
```

#### 계좌 정보 조회 결과

```
=== 전체 계좌 목록 ===
(1, '50160711', None, True, 'KIS', True)       ← KIS Mock
(2, '50160697', 'KIS Mock Virtual (Session C)', True, 'KIS', True)
(3, '50000000-02', '테스트 모의계좌', True, 'KIS', True)
(4, '81201280', 'moongoby@naver.com', True, 'KIWOOM', True)   ← KIWOOM Mock
(5, '52568156', 'moongoby@naver.com', False, 'KIWOOM', True)
(6, '63109343', 'moongoby@naver.com', False, 'KIWOOM', True)
(7, '74032243', 'KIS 실계좌', False, 'KIS', True)             ← KIS 실계좌
(9, '50160697', 'KIS 모의계좌', True, 'KIS', True)
```

#### 분석 결론

- 모든 10건 exit_reason = '가격 불명 보수적 청산' (동일 원인)
- exit_price = None → 실제 매도 주문 미발송
- account_id=4 (KIWOOM Mock): 4건 — 가상
- account_id=7 (KIS 실계좌): 2건 (id=64 004060, id=68 006340) — **실계좌! CEO 확인 필요**
- account_id=1 (KIS Mock): 1건 — 가상
- account_id=None (레거시): 3건 — 구형 데이터

---

### 작업 2 – Redis 상태 진단

#### 실행 명령 및 결과

```
$ redis-cli ping
PONG
REDIS_PING_EXIT:0
```

```
$ redis-cli info server
# Server
redis_version:7.0.15
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:62c7a5d52c72f4cd
redis_mode:standalone
os:Linux 6.8.0-84-generic x86_64
arch_bits:64
monotonic_clock:POSIX clock_gettime
multiplexing_api:epoll
atomicvar_api:c11-builtin
gcc_version:13.3.0
process_id:853
process_supervised:systemd
run_id:992120340c125d9c0aae0df06b89124f21a928da
tcp_port:6379
server_time_usec:1772757269291907
uptime_in_seconds:149303
uptime_in_days:1
hz:10
configured_hz:10
lru_clock:11149589
executable:/usr/bin/redis-server
config_file:/etc/redis/redis.conf
io_threads_active:0

$ redis-cli info keyspace
# Keyspace
db0:keys=8,expires=8,avg_ttl=92090975
```

```
$ ps aux | grep redis
redis  853  0.2  0.0  74524 10616 ?  Ssl  Mar04  5:05 /usr/bin/redis-server 127.0.0.1:6379
```

```
$ curl -s http://localhost:8002/health
{
    "status": "ok",
    "version": "4.1.0",
    "orchestrator_state": "TRADING",
    "database": "connected",
    "redis": "connected"
}
```

#### 결론

Redis 정상 동작 (PONG, PID 853, uptime 1.7일, 8키). T-151 WARN은 일시적 transient disconnect, 자동 복구됨.

---

### 작업 3 – unified_engine.log 0 bytes 원인

#### 파일 확인

```
$ ls -la /root/kis-autotrade-v4/logs/ | grep unified_engine
-rw-rw-r-- 1 root root     0 Mar  5 00:00 unified_engine.log
-rw-rw-r-- 1 root root  1882 Mar  5 00:00 unified_engine.log-20260305
```

#### logrotate 설정 확인

```
$ cat /etc/logrotate.d/kis-autotrade
/root/kis-autotrade-v4/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    dateext
    dateformat -%Y%m%d
}
```

#### unified_engine.py 로그 설정 확인

```
$ grep -n "LOG_FILE\|logging" /root/kis-autotrade-v4/scripts/run_unified_engine.py
38:import logging
62:logging.basicConfig(
63:    level=logging.INFO,
65:    handlers=[logging.StreamHandler()],   ← stdout만, 파일 핸들러 없음
67:logger = logging.getLogger("unified_engine")
```

#### cron 등록 여부

```
$ crontab -l | grep unified
(결과 없음)

$ crontab -u root -l | grep unified
NO_ROOT_CRON_UNIFIED
```

#### rotated 로그 마지막 내용

```
2026-03-03 09:32:48,377 [INFO] CTE 모듈 로드 성공
2026-03-03 09:32:48,397 [INFO] 통합 엔진 시작: mode=virtual action=monitor data-source=db
2026-03-03 09:32:48,397 [INFO] [MONITOR] 09:32:48 — 포지션 모니터링
2026-03-03 09:32:48,419 [INFO] [MONITOR] 오픈 포지션 20건
...
```

#### 결론

unified_engine.log 0 bytes 원인:
1. logrotate daily가 매일 00:00 새 빈 파일 생성 (copytruncate)
2. unified_engine.py는 StreamHandler(stdout) 전용, 파일 핸들러 없음
3. 크론 등록 없음 → 자동 실행 없음 (수동 실행만)
4. 정상 설계. 단, monitor_virtual_run.py의 로그 경로 불일치 버그 존재 (/var/log/unified_engine.log vs 실제 경로)

---

### 작업 4 – 크론 23개 vs 30+ 차이 분석

#### claudebot crontab 전체 (23개)

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

#### /etc/cron.d/ 카운트

```
cron_data_miner_211: 6
external_data_collection: 6
go100_closing_report: 3
go100_morning_briefing: 4
go100_paper_trading: 4
kiwoom_data_collection: 6
certbot: 3
e2scrub_all: 2
sysstat: 3
합계: 37
```

#### 결론

- claudebot crontab: 23개
- /etc/cron.d/ (root 실행): 37개
- 전체: 60개
- T-124 "30+"는 user+일부 system cron 합산. T-151 23 WARN은 user crontab만 카운트하는 로직 문제.

---

### 작업 5 – KIS 토큰 실제 상태 확인

#### v4_api_tokens 스키마

```
v4_api_tokens cols: ['id', 'account_config_id', 'access_token', 'token_type', 'expires_at', 'issued_at', 'is_valid', 'issue_count_today', 'created_at']
```

#### 토큰 조회 결과

```
=== KIS 토큰 현황 ===
id=1 cfg=1 type=Bearer prefix=eyJ0eXAiOiJKV1QiLCJh valid=True 만료됨 (1 day, 16:34:53.155180전) cnt=1
```

#### API 헬스

```json
{
    "status": "ok",
    "version": "4.1.0",
    "orchestrator_state": "TRADING",
    "database": "connected",
    "redis": "connected"
}
```

#### 결론

- v4_api_tokens: 1건, is_valid=True이나 expires_at 1.7일 전 만료 → DB 레코드 스테일
- FastAPI 서비스 및 가상매매는 정상 동작 → 실 토큰은 accounts.enc_token 또는 메모리 캐시 사용
- T-151 "모의계좌 HTTP 500 간헐 에러": v4_api_tokens 만료 레코드를 일부 API가 참조 시 500 발생 추정
- 장 종료 후 v4_api_tokens 갱신 및 자동화 로직 추가 필요

---

## 보고서 생성

경로: /root/kis-autotrade-v4/report/v41/CUR-V41-CRITICAL-ISSUE-DIAGNOSIS-001-20260306.md
생성 완료: ✅

---

## 커밋 결과

```
커밋 해시: 7187e9e0
메시지: [V4.1] T-152: T-151 CRITICAL 이슈 3건 진단 + 복구 권고
브랜치: phase-2c-command-center
변경: 1 file changed, 335 insertions(+)
```

git push: ❌ HTTPS 인증 불가 (claudebot 권한 없음) → root SSH push 필요
```
fatal: could not read Username for 'https://github.com': No such device or address
```

---

## 종합 결과 요약

| 이슈 | 심각도 | 진단 결과 | 조치 |
|------|--------|---------|------|
| SELL_FAILED 10건 | CRITICAL | 가격 불명 보수적 청산, exit_price=None, 실계좌 2건 포함 | 장 종료 후 CEO 승인 후 처리 |
| Redis 단절 WARN | WARN | 현재 정상(PONG, uptime 1.7일) - 일시적 transient | 없음 (자동 복구) |
| unified_engine.log 0 bytes | INFO | logrotate daily + 파일핸들러 없음 - 설계대로 | 모니터링 경로 수정 |
| 크론 23 vs 30+ | WARN | 총 60개(23+37) 정상 - 점검 로직 문제 | 점검 스크립트 수정 |
| KIS 토큰 DB 만료 | WARN | DB 스테일, 실 API 정상 | 장 종료 후 갱신 |

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (7187e9e0, phase-2c-command-center)
- [ ] project-docs 보고서 push 완료 (root push 필요 / done_watcher.sh 자동 처리 예정)
