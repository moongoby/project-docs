---
project: KIS-V41
task_id: KIS-302
completed_at: 2026-03-09T10:35:00+09:00
---

# KIS-302 BRIDGE RESULT — 03-10 장전 최종 시스템 헬스체크 전수점검

## 지시서 원문

TASK_ID: KIS-302 PROJECT: KIS-V41 TITLE: 03-10 장전 최종 시스템 헬스체크 — 서비스+DB+FunnelScore+Redis+크론 전수점검 PRIORITY: P0-CRITICAL SIZE: S IMPACT: H EFFORT: L

## 1. 작업 전 백업

```
cp /root/kis-autotrade-v4/config/funnel_score.yaml /root/kis-autotrade-v4/config/funnel_score.yaml.bak.20260309_102400
백업 완료
```

## 2. 인계 확인

HANDOVER.md (v11.5 기준) 및 CEO-DIRECTIVES.md (v2.0) 읽기 완료.

```
[인계 확인]
직전 완료: T-054 (Admin War Room 구현 검증)
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002, D-003
strategy_cards: 60
open_positions: 0
```

## 3. 헬스체크 10개 항목 실행 결과

### ① bridge.py PID 기록

명령:
```
ps aux | grep bridge
```

실행 결과:
```
root     2405236  1.6  0.9 257508 151088 ?       Ssl  Mar08  21:37 /root/.genspark/venv/bin/python /root/.genspark/genspark_bridge.py
claudeb+ 3875199  0.0  0.0   7340  3584 ?        Ss   10:23   0:00 /bin/bash -c source /home/claudebot/.claude/shell-snapshots/snapshot-bash-1773019419168-cz0xpk.sh && shopt -u extglob 2>/dev/null || true && eval 'ps aux < /dev/null | grep bridge 2>/dev/null' && pwd -P >| /tmp/claude-8e9b-cwd
claudeb+ 3875220  0.0  0.0   6544  2304 ?        S    10:23   0:00 grep bridge
```

판정: ✅ PASS — bridge.py PID 2405236 (root, Mar08 시작, 21h37min 가동)

---

### ② funnel_score.yaml null_fallback 확인

명령:
```
cat /root/kis-autotrade-v4/config/funnel_score.yaml | grep null_fallback
```

실행 결과:
```
null_fallback_score: 0.5  # T-237: 레이어 데이터 없음/NULL/0 시 Fail-Open 기본값
```

판정: ✅ PASS — null_fallback_score = 0.5

---

### ③ 서비스 5개 active 확인

명령:
```
sudo systemctl is-active kis-v41-api
sudo systemctl is-active kis-v41-monitor
sudo systemctl is-active kis-v41-scheduler
sudo systemctl is-active postgresql
sudo systemctl is-active redis-server

systemctl status kis-v41-api (상세)
```

실행 결과:
```
active   ← kis-v41-api
active   ← kis-v41-monitor
active   ← kis-v41-scheduler
active   ← postgresql
active   ← redis-server

● kis-v41-api.service - KIS AutoTrade V4.1 API (port 8003)
     Active: active (running) since Sun 2026-03-08 14:23:25 KST; 20h ago
```

판정: ✅ PASS — 5개 서비스 모두 active

---

### ④ DB 쿼리 — strategy_cards / open_positions

명령:
```sql
sudo /usr/bin/psql -h localhost -U kis_admin -d kisautotrade -c "SELECT COUNT(*) as strategy_cards_count FROM strategy_cards;"
sudo /usr/bin/psql -h localhost -U kis_admin -d kisautotrade -c "SELECT COUNT(*) as open_positions_count FROM v4_positions WHERE status='OPEN';"
```

실행 결과:
```
 strategy_cards_count
----------------------
                   60
(1 row)

 open_positions_count
----------------------
                    0
(1 row)
```

판정: ✅ PASS — strategy_cards=60, open_positions=0

---

### ⑤ Redis ping

명령:
```
redis-cli ping
```

실행 결과:
```
PONG
```

판정: ✅ PASS

---

### ⑥ crontab 건수

명령:
```
crontab -l | wc -l
```

실행 결과:
```
44
```

주요 크론 목록 (crontab -l 전체):
```
@reboot /usr/bin/python3 /home/claudebot/done_watcher.py >> /root/.genspark/logs/done_watcher.log 2>&1 &
# [GO100 DIR-009] LightGBM 재학습 — 20거래일 ≈ 28일 주기 (매월 1일/29일 16:05 KST)
5 16 1,29 * * /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/backend/app/services/go100/lightgbm_retrainer.py --run >> /root/kis-autotrade-v4/logs/lgbm_retrain.log 2>&1
# [GO100 CUR-RESEARCH-PIPELINE-LIVE-001] 주간 연구 파이프라인 — 토요일 10:00 KST (01:00 UTC)
0 1 * * 6 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/run_research_pipeline.py >> /root/kis-autotrade-v4/logs/research_pipeline.log 2>&1
# [GO100 연구소] 주간 연구 파이프라인 — 토요일 10:00 KST (01:00 UTC)
0 1 * * 6 /root/kis-autotrade-v4/scripts/go100/run_research_pipeline.sh >> /var/log/go100/research_pipeline_cron.log 2>&1
# [GO100 DIR-PT-V3] 30일 모의투자 V3 Brain 매수 — 09:10 KST (00:10 UTC) 평일
10 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode buy >> /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log 2>&1
# [GO100 DIR-PT-V3] 30일 모의투자 V3 Brain 매도 — 15:15 KST (06:15 UTC) 평일
15 6 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode sell >> /root/kis-autotrade-v4/logs/paper_trading_v3_sell.log 2>&1
# [GO100 DIR-PT-V3] 30일 모의투자 V3 Brain 주간 자기리뷰 — 금 16:30 KST (07:30 UTC)
30 7 * * 5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode weekly_review >> /root/kis-autotrade-v4/logs/paper_trading_v3_review.log 2>&1
50 8 * * 1-5 /root/kis-autotrade-v4/scripts/go100/daily_ai_prediction_v3.sh >> /root/kis-autotrade-v4/logs/go100/ai_prediction_v3_cron.log 2>&1
# [KIS DIR-0066] V4.1 일일 매매 보고서 — 17:00 KST (08:00 UTC) 평일
0 8 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_daily_report.py --push >> /root/kis-autotrade-v4/logs/v41_daily_report.log 2>&1
# [V4.1 DIR-0067] 주간 보고서 — 토요일 10:00 KST (01:00 UTC)
0 1 * * 6 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_weekly_report.py >> /root/kis-autotrade-v4/logs/weekly_report.log 2>&1
# [V4.1 DIR-0067] 월간 보고서 — 매월 1일 10:00 KST (01:00 UTC)
0 1 1 * * /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/generate_v41_monthly_report.py >> /root/kis-autotrade-v4/logs/monthly_report.log 2>&1
# [KIS TASK-077] virtual_hourly_report — 장중 매시 정각 09:00-15:00 KST 평일
0 9-15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python scripts/monitor_virtual_run.py periodic >> /root/kis-autotrade-v4/logs/virtual_hourly_report.log 2>&1
# [KIS TASK-077] 통합 일일보고서 — 17:00 KST 평일
0 17 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_daily_report.py >> /root/kis-autotrade-v4/logs/unified_daily_report.log 2>&1
# [KIS TASK-077] 통합 주간보고서 — 토요일 10:00 KST
0 10 * * 6 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_weekly_report.py >> /root/kis-autotrade-v4/logs/unified_weekly_report.log 2>&1
# [KIS TASK-077] 통합 월간보고서 — 매월 1일 10:00 KST
0 10 1 * * cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_monthly_report.py >> /root/kis-autotrade-v4/logs/unified_monthly_report.log 2>&1
# [KIS TASK-087] 모닝 매수 체결 확인 — 09:15 KST (00:15 UTC) 평일
15 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_morning_execution.py >> /root/kis-autotrade-v4/logs/morning_check.log 2>&1
# [KIS TASK-087] TP 발동 감지 — 매시 정각 09:00-16:00 KST (00:00-07:00 UTC) 평일
0 0-7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_tp_execution.py >> /root/kis-autotrade-v4/logs/tp_check.log 2>&1
# [KIS TASK-090] Stage 전환 체크 — 15:40 KST (06:40 UTC) 평일
40 6 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_stage_transition.py >> /root/kis-autotrade-v4/logs/stage_transition.log 2>&1
# [KIS T-092] DESK5/4 노드 감지 — 매일 16:00 KST (07:00 UTC) 평일
0 7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk5 >> /root/kis-autotrade-v4/logs/node_desk5.log 2>&1
# [KIS T-092] DESK4 노드 감지 — 매일 16:00 KST (07:00 UTC) 평일
5 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk4 >> /root/kis-autotrade-v4/logs/node_desk4.log 2>&1
# [KIS T-092] DESK3 노드 감지(프리마켓) — 08:50 KST (23:50 UTC 전날) 평일
50 23 * * 0-4 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk3 >> /root/kis-autotrade-v4/logs/node_desk3.log 2>&1
# [KIS T-092] DESK3 노드 감지(장마감) — 16:00 KST (07:00 UTC) 평일
10 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk3 >> /root/kis-autotrade-v4/logs/node_desk3.log 2>&1
# [KIS T-092] 일간 노드 요약 — 16:30 KST (07:30 UTC) 평일
30 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine daily_summary >> /root/kis-autotrade-v4/logs/node_daily_summary.log 2>&1
```

판정: ✅ PASS — 44줄, 20잡+ 등록 (5건+ 기준 충족)

---

### ⑦ backtest/progress API 200 OK 확인

명령:
```
curl -s https://trading41.newtalk.kr/api/v4/backtest/progress | head -c 200
```

실행 결과:
```json
{"total_sessions":3,"completed":3,"running":0,"failed":0,"pending":0,"completion_pct":100.0,"latest_session":{"session_id":3,"hypothesis_id":null,"phase":"seed","status":"CONVERGED","started_at":"2026...
```

판정: ✅ PASS — 200 OK, 3세션 CONVERGED(100%)

---

### ⑧ trades/unified 10만건+ 확인

명령:
```
curl -s https://trading41.newtalk.kr/api/v4/trades/unified
python3 -c "import sys,json; d=json.load(sys.stdin); print(type(d)); print(str(d)[:300])"
```

실행 결과:
```
<class 'dict'>
{'summary': {'total_count': 105526, 'win_rate': 46.23, 'profit_factor': 2.1033, 'avg_pnl_pct': 1.7141, 'cum_pct': 180499.0963, 'mdd_pct': 100.0, 'max_win_pct': 103.6515, 'max_loss_pct': -38.1955}, 'pagination': {'page': 1, 'limit': 50, 'total': 105526, 'pages': 2111}, 'trades': [{'trade_id': 'BT_211...
```

- total_count: **105,526건** (10만건+ ✅)
- win_rate: 46.23%
- profit_factor: 2.1033
- avg_pnl_pct: 1.7141%
- cum_pct: 180,499.09%

판정: ✅ PASS — 105,526건 (10만건+ 충족)

참고: `len(response_dict)` = 3 (dict keys: summary/pagination/trades). 실제 거래 건수는 summary.total_count로 확인.

---

### ⑨ GO100 모의투자 세션 ACTIVE 확인

명령:
```sql
sudo /usr/bin/psql -h localhost -U kis_admin -d kisautotrade -c "SELECT session_id, strategy_card_id, status FROM go100_paper_trading_sessions WHERE status='ACTIVE';"
```

실행 결과:
```
 session_id | strategy_card_id | status
------------+------------------+--------
          2 |               35 | ACTIVE
          3 |               55 | ACTIVE
          4 |               56 | ACTIVE
          5 |               57 | ACTIVE
          6 |               58 | ACTIVE
          7 |               59 | ACTIVE
(6 rows)
```

판정: ✅ PASS — 6개 ACTIVE (session_id 2-7, card_id 35/55-59)

---

### ⑩ go100 서비스 상태

명령:
```
systemctl status go100
```

실행 결과:
```
● go100.service - GO100 V4.1 AutoTrade API
     Active: active (running) since Mon 2026-03-09 09:07:33 KST; 1h 16min ago
```

판정: ✅ PASS — active (running) 09:07 KST

---

## 4. 최종 결과 요약

| # | 항목 | 예상값 | 실제값 | 판정 |
|---|------|--------|--------|------|
| ① | bridge.py PID | 존재 | PID 2405236 (21h+) | ✅ PASS |
| ② | null_fallback | 0.5 | 0.5 | ✅ PASS |
| ③ | 서비스 5개 | 모두 active | 5/5 active | ✅ PASS |
| ④ | strategy_cards / open | 60 / 0 | 60 / 0 | ✅ PASS |
| ⑤ | redis ping | PONG | PONG | ✅ PASS |
| ⑥ | crontab | 5건+ | 44줄 (20잡+) | ✅ PASS |
| ⑦ | backtest/progress | 200 OK | 200, CONVERGED 100% | ✅ PASS |
| ⑧ | trades/unified | 10만건+ | 105,526건 | ✅ PASS |
| ⑨ | GO100 ACTIVE 세션 | 6개 | 6개 (session 2-7) | ✅ PASS |
| ⑩ | go100 서비스 | active | active (09:07 KST) | ✅ PASS |

**✅ 10/10 ALL PASS — 03-10 장전 시스템 이상 없음**

---

## 5. 보고서 push 결과

보고서 파일:
```
/root/project-docs/kis-autotrade-v4/reports/CUR-V41-KIS302-PREMARKET-HEALTHCHECK-001-20260309.md
```

git push:
```
[master 5ba135f] [V4.1] KIS-302 03-10 장전 최종 헬스체크 보고서
 1 file changed, 277 insertions(+)
 create mode 100644 kis-autotrade-v4/reports/CUR-V41-KIS302-PREMARKET-HEALTHCHECK-001-20260309.md
To github.com:moongoby/project-docs.git
   6434034..5ba135f  master -> master
```

GitHub HTTP 200 확인:
```
curl result: 200
URL: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-KIS302-PREMARKET-HEALTHCHECK-001-20260309.md
```

---

## 6. HANDOVER.md 업데이트

KIS-302 항목 추가 완료.

git push:
```
[master a1f38eb] docs: HANDOVER 업데이트 (KIS-302 완료)
 1 file changed, 18 insertions(+)
To github.com:moongoby/project-docs.git
   06895d5..a1f38eb  master -> master
```

HANDOVER.md HTTP 200:
```
curl result: 200
URL: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md
```

HANDOVER.md 업데이트 완료: a1f38eb

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (이 태스크는 코드 변경 없음, 헬스체크만)
- [x] project-docs 보고서 push 완료 (GitHub raw URL 200 ✅, 커밋 5ba135f)
