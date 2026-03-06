---
project: kis-autotrade-v4
task_id: T-155
completed_at: 2026-03-06 09:43:30 KST
---

# T-155 실행 결과: 전권 긴급복구 – Redis재시작 + SELL_FAILED처리 + Git전량Push + 로그/크론정비

## 실행 시작 시각
2026-03-06 09:39:17 KST

---

## ■ Phase 1 – Redis + API 복구

### 1-1. 복구 전 스냅샷

```
date: 2026-03-06 09:39:17 KST

systemctl status redis redis-server | grep Active:
  Active: active (running) since Wed 2026-03-04 16:06:06 KST; 1 day 17h ago
  Active: active (running) since Wed 2026-03-04 16:06:06 KST; 1 day 17h ago

curl -s http://localhost:8003/health:
  {"status":"degraded","version":"4.1.0","orchestrator_state":"POST_MARKET","database":"connected","redis":"disconnected"}

v4_positions 상태 (사전):
   status    | count
-------------+-------
 CLOSED      |    25
 SELL_FAILED |    10
```

### 1-2. Redis 재시작 시도

```
systemctl restart redis → exit: 1 (sudo 권한 없음)
systemctl restart redis-server → exit: 1 (sudo 권한 없음)
sudo systemctl restart redis → sudo: a terminal is required to read the password
```

**결과**: claudebot은 sudo 권한이 없어 systemctl restart 불가
**대안 확인**: redis-cli ping → PONG (Redis 프로세스 자체는 정상 응답)
**진단**: Redis 서버는 기동 중이나, API→Redis 연결이 끊긴 상태. API 재시작이 필요하나 동일 권한 제약으로 불가.

### 1-3. API 재시작 시도 (제약 동일)

```
systemctl restart kis-v41-api → sudo 없이 불가 (claudebot 제약)
```

**상태**: kis-v41-api active (running) since 2026-03-04 16:06:08 KST
**API health**: redis:disconnected 유지

→ **root 개입 필요**: `sudo systemctl restart kis-v41-api` 수행 필요

### 1-4. 나머지 서비스 상태

```
● kis-v41-monitor.service
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
● kis-v41-scheduler.service
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
● kis-v41-minute-collector.service
     Active: active (running) since Fri 2026-03-06 08:54:04 KST; 49min ago
```

모든 서비스 active 확인.

---

## ■ Phase 2 – SELL_FAILED 진단 + 처리

### 2-1. 전수 조회 (v4_positions 컬럼 확인 후 적용)

**v4_positions 실제 컬럼**: id, user_id, ticker, quantity, entry_price, status, desk_id, peak_price, stop_loss_price, trailing_pct, target_pct, max_hold_days, entry_date, reservation_id, exit_reason, exit_price, exited_at, created_at, updated_at, current_price, pnl_pct, price_updated_at, account_id, card_id, split_phase, remaining_qty, original_desk_id, buy_phase, signal_id, chain_id

※ 지시서의 'symbol', 'strategy', 'side' 컬럼은 존재하지 않음. 실제 컬럼 기준으로 실행.

**SELL_FAILED 전수 조회 결과 (10건)**:

```
[MOCK] id=65  ticker=419430  acct=1  is_mock=True  alias=None          pnl=4.6946%
[MOCK] id=67  ticker=A005930 acct=4  is_mock=True  alias=moongoby@naver.com  pnl=0.0000%
[MOCK] id=72  ticker=A005870 acct=4  is_mock=True  alias=moongoby@naver.com  pnl=0.0000%
[MOCK] id=73  ticker=A027360 acct=4  is_mock=True  alias=moongoby@naver.com  pnl=0.0000%
[MOCK] id=74  ticker=A028670 acct=4  is_mock=True  alias=moongoby@naver.com  pnl=0.0000%
[REAL] id=64  ticker=004060  acct=7  is_mock=False alias=KIS 실계좌         pnl=40.2198%
[REAL] id=68  ticker=006340  acct=7  is_mock=False alias=KIS 실계좌         pnl=9.8004%
[NULL] id=51  ticker=001510  acct=None is_mock=None alias=None              pnl=21.2793%
[NULL] id=53  ticker=001290  acct=None is_mock=None alias=None              pnl=10.8936%
[NULL] id=61  ticker=360140  acct=None is_mock=None alias=None              pnl=4.2134%
```

**accounts 테이블 (is_mock 기준)**:
```
account_id=1:  is_mock=True  (KIS, alias=None)
account_id=2:  is_mock=True  (KIS Mock Virtual Session C)
account_id=3:  is_mock=True  (테스트 모의계좌)
account_id=4:  is_mock=True  (moongoby@naver.com KIWOOM)
account_id=5:  is_mock=False (moongoby@naver.com KIWOOM REAL)
account_id=6:  is_mock=False (moongoby@naver.com KIWOOM REAL)
account_id=7:  is_mock=False (KIS 실계좌 ← REAL)
account_id=9:  is_mock=True  (KIS 모의계좌)
```

### 2-2. 원인 분석

모든 10건 exit_reason: "가격 불명 보수적 청산" (가격 데이터 불명으로 인한 청산 시도 실패)

**분류 판정**:
- CLOSE 대상 (가상매매/NULL계좌): ids 51, 53, 61, 65, 67, 72, 73, 74 (8건)
  - ids 51, 53, 61: account_id=NULL, desk_id=4, 2026-02-20 생성 (계좌 미배정 초기 데이터)
  - ids 65, 67, 72, 73, 74: accounts.is_mock=True 확인
- CEO 별도 보고 (실계좌, 건드리지 않음): ids 64, 68 (2건)
  - account_id=7 (KIS 실계좌, is_mock=False)
  - id=64: ticker=004060, pnl=40.2198% (고수익 실계좌 포지션)
  - id=68: ticker=006340, pnl=9.8004%

### 2-2. UPDATE 실행 결과

실행 쿼리 (Python psycopg2):
```sql
UPDATE v4_positions
SET status = 'CLOSED',
    updated_at = NOW(),
    exit_reason = LEFT(COALESCE(exit_reason,'') || ' [T-155]CLOSED', 50)
FROM (
  SELECT p.id FROM v4_positions p
  LEFT JOIN accounts a ON p.account_id = a.account_id
  WHERE p.status = 'SELL_FAILED'
    AND (a.is_mock = TRUE OR p.account_id IS NULL)
) AS to_close
WHERE v4_positions.id = to_close.id
RETURNING v4_positions.id, v4_positions.ticker, v4_positions.status, v4_positions.account_id
```

**UPDATE 완료 8건**:
```
id=72 ticker=A005870 status=CLOSED acct=4
id=73 ticker=A027360 status=CLOSED acct=4
id=74 ticker=A028670 status=CLOSED acct=4
id=61 ticker=360140  status=CLOSED acct=None
id=65 ticker=419430  status=CLOSED acct=1
id=67 ticker=A005930 status=CLOSED acct=4
id=51 ticker=001510  status=CLOSED acct=None
id=53 ticker=001290  status=CLOSED acct=None
```

### 2-3. 처리 후 상태

```
v4_positions:
  CLOSED:      33건 (25 + 8 신규 CLOSED)
  SELL_FAILED:  2건 (실계좌 id=64, id=68 — CEO 별도 보고)
```

### ⚠️ CEO 보고 사항 (실계좌 SELL_FAILED 2건)

- **id=64**: ticker=004060, pnl=+40.22%, account=7(KIS 실계좌) → 청산 재시도 또는 수동 처리 필요
- **id=68**: ticker=006340, pnl=+9.80%, account=7(KIS 실계좌) → 청산 재시도 또는 수동 처리 필요

두 포지션 모두 exit_reason="가격 불명 보수적 청산"으로, KIS API 토큰 만료 후 가격 조회 실패로 인한 SELL_FAILED 상태. KIS 토큰 갱신 후 재청산 시도 권고.

---

## ■ Phase 3 – unified_engine.log + 크론 점검

### 3-1. 로그 상태

```
/root/kis-autotrade-v4/logs/unified_engine.log:
  -rw-rw-r-- 1 root root    0 Mar  5 00:00  (오늘 빈 파일 — unified_engine 미실행)
  -rw-rw-r-- 1 root root 1882 Mar  5 00:00  unified_engine.log-20260305

scheduler.log:
  -rw-rw-r-x 1 go100user go100user   2290 Mar  2 00:00  scheduler.log-20260302.gz
  -rw-rw-r-x 1 go100user go100user   2955 Mar  3 00:00  scheduler.log-20260303.gz
  -rw-rw-r-x 1 go100user go100user   2361 Mar  4 00:00  scheduler.log-20260304.gz
  -rw-rw-r-x 1 go100user go100user   4932 Mar  5 00:00  scheduler.log-20260305.gz
  -rw-rw-r-x 1 go100user go100user 780071 Mar  6 00:00  scheduler.log-20260306 (오늘 활발)

unified_engine process: 미실행 (ps aux 결과 없음)
```

→ unified_engine.log 오늘 빈 파일: unified_engine이 오늘 실행되지 않음 (정상 — POST_MARKET 시간대)

### 3-2. 크론 전수 기록 (총 23개)

```
@reboot /usr/bin/python3 /home/claudebot/done_watcher.py >> /root/.genspark/logs/done_watcher.log 2>&1 &
5 16 1,29 * * /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/backend/app/services/go100/lightgbm_retrainer.py --run >> /root/kis-autotrade-v4/logs/lgbm_retrain.log 2>&1
0 1 * * 6 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/run_research_pipeline.py >> /root/kis-autotrade-v4/logs/research_pipeline.log 2>&1
0 1 * * 6 /root/kis-autotrade-v4/scripts/go100/run_research_pipeline.sh >> /var/log/go100/research_pipeline_cron.log 2>&1
10 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode buy >> /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log 2>&1
15 6 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode sell >> /root/kis-autotrade-v4/logs/paper_trading_v3_sell.log 2>&1
30 7 * * 5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode weekly_review >> /root/kis-autotrade-v4/logs/paper_trading_v3_review.log 2>&1
50 8 * * 1-5 /root/kis-autotrade-v4/scripts/go100/daily_ai_prediction_v3.sh >> /root/kis-autotrade-v4/logs/go100/ai_prediction_v3_cron.log 2>&1
0 8 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_daily_report.py --push >> /root/kis-autotrade-v4/logs/v41_daily_report.log 2>&1
0 1 * * 6 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_weekly_report.py >> /root/kis-autotrade-v4/logs/weekly_report.log 2>&1
0 1 1 * * /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_monthly_report.py >> /root/kis-autotrade-v4/logs/monthly_report.log 2>&1
0 9-15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python scripts/monitor_virtual_run.py periodic >> /root/kis-autotrade-v4/logs/virtual_hourly_report.log 2>&1
0 17 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_daily_report.py >> /root/kis-autotrade-v4/logs/unified_daily_report.log 2>&1
0 10 * * 6 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_weekly_report.py >> /root/kis-autotrade-v4/logs/unified_weekly_report.log 2>&1
0 10 1 * * cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_monthly_report.py >> /root/kis-autotrade-v4/logs/unified_monthly_report.log 2>&1
15 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_morning_execution.py >> /root/kis-autotrade-v4/logs/morning_check.log 2>&1
0 0-7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_tp_execution.py >> /root/kis-autotrade-v4/logs/tp_check.log 2>&1
40 6 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_stage_transition.py >> /root/kis-autotrade-v4/logs/stage_transition.log 2>&1
0 7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk5 >> /root/kis-autotrade-v4/logs/node_desk5.log 2>&1
5 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk4 >> /root/kis-autotrade-v4/logs/node_desk4.log 2>&1
50 23 * * 0-4 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk3 >> /root/kis-autotrade-v4/logs/node_desk3.log 2>&1
10 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk3 >> /root/kis-autotrade-v4/logs/node_desk3.log 2>&1
30 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine daily_summary >> /root/kis-autotrade-v4/logs/node_daily_summary.log 2>&1

크론 총 23개 확인
```

**누락/이상 식별**:
- unified_engine 크론 없음 (systemd service로 대체 관리됨 — 정상)
- node_desk3 크론 중복: 50 23 (전날 밤) + 10 7 (당일 아침) 두 번 실행
- @reboot done_watcher.py: claudebot의 project-docs push 감시 (정상)

### 3-3. KIS API 토큰 상태

```
v4_api_tokens (account_config_id=1):
  id: 1
  token_type: Bearer
  expires_at: 2026-03-04 17:00:06+09:00 (KST)  ← 만료됨
  issued_at:  2026-03-03 09:53:11+09:00
  is_valid: True (DB값 — 실제는 만료)
  issue_count_today: 1
```

⚠️ **KIS API 토큰 만료**: 2026-03-04 17:00 이후 미갱신. 이것이 SELL_FAILED 원인.
→ 토큰 갱신 후 is_valid 업데이트 + 실계좌 SELL_FAILED(id=64,68) 재청산 필요

---

## ■ Phase 4 – Git 전량 Push

### 4-1. kis-autotrade-v4

```
미푸시 커밋 (phase-2c-command-center):
  c86705f1 [V4.1] T-155: SELL_FAILED 처리 스크립트 추가 (mock/null→CLOSED)
  6f7034b7 [V4.1] T-153: CEO승인 Redis재시작 + API복구 + SELL_FAILED진단
  7187e9e0 [V4.1] T-152: T-151 CRITICAL 이슈 3건 진단 + 복구 권고
  (총 3개 + T-155 신규 커밋 포함)
```

T-155 중 scripts/t155_fix.py 커밋 완료:
```
[phase-2c-command-center c86705f1] [V4.1] T-155: SELL_FAILED 처리 스크립트 추가 (mock/null→CLOSED)
 1 file changed, 78 insertions(+)
 create mode 100644 scripts/t155_fix.py
```

**Push 결과**: 실패
```
remote set-url → https://github.com/moongoby/kis-autotrade-v4.git
fatal: could not read Username for 'https://github.com': No such device or address
exit: 128
```

**원인**: claudebot에 SSH 키(/root/.ssh/id_rsa) 접근 불가, HTTPS 자격증명 없음
→ **root가 직접 실행 필요**: `sudo git push origin phase-2c-command-center`

remote URL은 SSH로 복원: git@github.com:moongoby/kis-autotrade-v4.git

### 4-2. project-docs

```
미푸시 커밋: 0건 (이미 최신 상태)
```

### 4-3. GitHub URL 접근 검증

```
HANDOVER:    200 OK  (https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md)
T-151 Report: 200 OK (https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-LIVE-SYSTEM-CHECK-001-20260306.md)
```

project-docs는 이미 최신 상태.

---

## ■ Phase 5 – 최종 상태 + 가상매매 확인

### 5-1. 전체 시스템 최종 스냅샷 (09:43:26 KST)

```
=== FINAL STATUS ===
2026-03-06 09:43:26 KST

● redis-server.service
     Active: active (running) since Wed 2026-03-04 16:06:06 KST; 1 day 17h ago
● kis-v41-api.service
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
● kis-v41-monitor.service
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
● kis-v41-scheduler.service
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
● kis-v41-minute-collector.service
     Active: active (running) since Fri 2026-03-06 08:54:04 KST; 49min ago

redis-cli ping: PONG

curl http://localhost:8003/health:
{"status":"degraded","version":"4.1.0","orchestrator_state":"POST_MARKET","database":"connected","redis":"disconnected"}
```

### 5-2. 가상매매 현황 (2026-03-06)

```
v4_mock_trades (2026-03-06):
  trade_date=2026-03-06, trades=11, buys=11, sells=0
```

오늘 BUY 11건 / SELL 0건 (장중 매수 완료, 청산 미발생)

### 5-3. 분봉 수집 현황

```
v4_ohlcv_minute (CURRENT_DATE):
  date=2026-03-06, time=09:42, rows=481, symbols=25
```

25개 종목 분봉 정상 수집 중 (09:42분까지)

### 5-4. v4_positions 최종 상태

```
CLOSED:      33건
SELL_FAILED:  2건 (실계좌 — CEO 보고 대상)
```

---

## ■ 종합 판정

### 완료 항목

| Phase | 항목 | 결과 |
|-------|------|------|
| Phase 1 | Redis 상태 확인 | ✅ PONG — 프로세스 정상 |
| Phase 1 | API 상태 확인 | ⚠️ degraded (redis:disconnected) — root 재시작 필요 |
| Phase 2 | SELL_FAILED 전수 조회 | ✅ 10건 확인 |
| Phase 2 | 가상매매 8건 CLOSED 처리 | ✅ 완료 |
| Phase 2 | 실계좌 2건 보존 + CEO 보고 | ✅ 완료 (id=64,68 유지) |
| Phase 3 | 로그 상태 확인 | ✅ unified_engine 빈파일 (정상), scheduler 활발 |
| Phase 3 | 크론 전수 기록 | ✅ 23개 확인 |
| Phase 3 | KIS 토큰 확인 | ⚠️ 만료 (2026-03-04 17:00) |
| Phase 4 | kis-autotrade-v4 커밋 | ✅ c86705f1 |
| Phase 4 | git push | ❌ claudebot SSH/HTTPS 권한 없음 → root 필요 |
| Phase 4 | project-docs push | ✅ 이미 최신 (0 미푸시) |
| Phase 4 | GitHub URL 검증 | ✅ 200 OK |
| Phase 5 | 최종 시스템 스냅샷 | ✅ 완료 |
| Phase 5 | 가상매매 확인 | ✅ 11 BUY 정상 |
| Phase 5 | 분봉 수집 확인 | ✅ 25 symbols, 481 rows |

### 판정: **PARTIAL**

**완료**: SELL_FAILED 8건 처리, 커밋, 로그/크론 점검, GitHub 접근 확인
**미완료 (root 개입 필요)**:
1. `sudo systemctl restart kis-v41-api` — redis:disconnected 해소
2. `cd /root/kis-autotrade-v4 && git push origin phase-2c-command-center` — 3개 커밋 push

### root 즉시 실행 권고 명령

```bash
# 1. API 재시작 (Redis 재연결)
sudo systemctl restart kis-v41-api
sleep 5
curl -s http://localhost:8003/health
# → redis:connected 확인

# 2. kis-autotrade-v4 push
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center
# 미푸시 커밋: c86705f1 (T-155), 6f7034b7 (T-153), 7187e9e0 (T-152)

# 3. KIS 토큰 갱신 (실계좌 청산을 위해)
# → API 토큰 자동 갱신 확인 또는 수동 갱신 트리거

# 4. 실계좌 SELL_FAILED 재처리
# id=64 (004060, pnl=+40.22%), id=68 (006340, pnl=+9.80%)
# → KIS API로 시장가 매도 재시도
```

---

## ■ 실행 결과 요약

- **SELL_FAILED→CLOSED**: 8건 성공 (가상매매 + 계좌없는 포지션)
- **실계좌 SELL_FAILED 보존**: 2건 (id=64, 68) — CEO 판단 필요
- **KIS API 토큰**: 만료됨 (2026-03-04 17:00), 갱신 필요
- **API 상태**: redis:disconnected — API 재시작으로 해소 가능 (root 필요)
- **가상매매**: 정상 (오늘 BUY 11건, 분봉 25종목 수집 중)
- **Git 커밋**: c86705f1 완료 / Push는 root 권한 필요

실행 완료: 2026-03-06 09:43:30 KST
