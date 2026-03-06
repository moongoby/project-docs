---
project: kis-autotrade-v4
task_id: T-164
completed_at: 2026-03-06T10:38:49 KST
---

# T-164 실행 결과 — DESK 전체 성과 진단 + DESK5/DESK1 상태 확인

## 지시서 원문
```
Task ID: T-164 제목: DESK 전체 성과 진단 + DESK5/DESK1 상태 확인 (T-157/T-159 통합 축소) 서버: 211 (kis-autotrade-v4) 우선순위: P1-HIGH 예상 시간: 15분 의존성: 없음

■ 배경: T-157/T-159가 타임아웃. 핵심 쿼리만 축소하여 재실행.

■ 작업 (Python psycopg2 사용)

import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, dbname='kisautotrade', user='kis_admin', password='KisAuto2026!Secure')
cur = conn.cursor()

# 1. DESK별 mock trade 성과
cur.execute("""
SELECT strategy, COUNT(*) as trades,
  ROUND(AVG(CASE WHEN pnl_pct != -0.47 THEN pnl_pct END)::numeric, 3) as avg_pnl_excl_cost,
  SUM(CASE WHEN pnl_pct > 0 THEN 1 ELSE 0 END) as wins,
  MIN(pnl_pct) as worst, MAX(pnl_pct) as best
FROM v4_mock_trades WHERE created_at >= '2026-03-02'
GROUP BY strategy ORDER BY trades DESC
""")

# 2. strategy_cards 현황
cur.execute("SELECT desk_id, COUNT(*), SUM(CASE WHEN is_active THEN 1 ELSE 0 END) FROM strategy_cards GROUP BY desk_id ORDER BY desk_id")

# 3. DESK5 watchlist
cur.execute("SELECT COUNT(*), status FROM v4_desk5_watchlist GROUP BY status")

# 4. DESK4 watchlist
cur.execute("SELECT COUNT(*), status FROM v4_desk4_watchlist GROUP BY status")

# 5. DESK3 pool
cur.execute("SELECT COUNT(*), status FROM v4_desk3_pool GROUP BY status")

# 6. DESK1 스캘핑 관련 파일 존재 확인
import os
scalp_files = [f for f in os.listdir('/root/kis-autotrade-v4/backend/app/services/') if 'scalp' in f.lower() or 'desk1' in f.lower()]

# 7. DESK1 cron 확인
import subprocess
result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
desk1_crons = [l for l in result.stdout.split('\n') if 'desk1' in l.lower() or 'scalp' in l.lower()]

■ 보고서: CUR-V41-DESK-STATUS-SUMMARY-001-20260306.md ■ 완료 후: project-docs push, HANDOVER.md 갱신 ■ 절대 금지: DB 변경, 서비스 재시작
```

---

## 실행 과정

### Step 1: 테이블 구조 확인

v4_mock_trades 컬럼명 확인 (지시서의 `strategy` → 실제 컬럼명은 `strategy_id`):

```
실행 명령: /root/kis-autotrade-v4/venv/bin/python3
DB: kisautotrade @ localhost:5432 (psycopg2)

v4_mock_trades 컬럼:
  id: integer
  trade_date: date
  ticker: character varying
  strategy_id: character varying  ← 실제 컬럼명 (지시서의 strategy != 실제)
  direction: character varying
  quantity: integer
  entry_price: numeric
  exit_price: numeric
  pnl_pct: numeric
  cost_pct: numeric
  slippage_pct: numeric
  kis_order_id: character varying
  notes: text
  created_at: timestamp without time zone
```

오류 내용:
```
psycopg2.errors.UndefinedColumn: column "strategy" does not exist
LINE 2: SELECT strategy, COUNT(*) as trades,
HINT:  Perhaps you meant to reference the column "v4_mock_trades.strategy_id".
```
→ `strategy` → `strategy_id` 로 수정하여 재실행.

### Step 2: 전체 쿼리 실행 결과

```
=== 1. DESK별 mock trade 성과 (2026-03-02 이후) ===
strategy_id      trades   avg_pnl  wins      worst       best
D-ORB                29    -1.132     1     -3.612      0.199
D7                   29    -1.583     0     -1.801      -0.47
D6                   29    -0.374     2     -1.879      0.424
D5                   29     0.000     0          0          0
S1                   16      None     0      -0.47      -0.47
D2                   16      None     0      -0.47      -0.47
D4                   16    -2.673     0     -2.673      -0.47

=== 총계 ===
  total=164, avg_pnl=-0.967, wins=3, losses=41
  승률=1.8%

=== 2. strategy_cards 현황 ===
desk_id        total  active
1                 10      10
2                 16       0
3                 11      11
4                  9       9
5                 10      10
None               4       3
  합계: 60

=== 3. DESK5 watchlist ===
  count=20, status=WATCHING

=== 4. DESK4 watchlist ===
  count=18, status=WATCHING

=== 5. DESK3 pool ===
  count=306, status=ACTIVE

=== 6. DESK1 스캘핑 관련 파일 ===
  발견된 파일: 없음

=== 7. DESK1 cron 확인 ===
  DESK1 관련 cron 수: 0
  (DESK1/scalp 관련 cron 없음)

=== 전체 cron (참고) ===
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

=== 날짜별 mock trade 집계 (2026-03-02 이후) ===
  2026-03-02: 7건, 승0건, avg_pnl=-0.470
  2026-03-03: 56건, 승0건, avg_pnl=-0.470
  2026-03-04: 34건, 승0건, avg_pnl=-1.039
  2026-03-05: 56건, 승3건, avg_pnl=-0.631
  2026-03-06: 11건, 승0건, avg_pnl=None

=== 실행 완료: 2026-03-06 10:37:25 ===
```

---

## 핵심 발견 요약

1. **전체 mock trade 성과 (2026-03-02~)**: 164건, 승3건, 승률1.8%, avg_pnl=-0.967%
2. **DESK별 성과**:
   - D6: 최우수 (avg=-0.374%, 승2건, best=+0.424%)
   - D-ORB: avg=-1.132%, 승1건
   - D7: 전패 (avg=-1.583%)
   - D4: avg=-2.673% (손절 발동 중)
   - D5: pnl=0 전건 (미청산 또는 기록 이슈)
   - S1, D2: 전건 -0.47% (비용만 기록, 실거래 없음)
3. **DESK2 strategy_cards 16개 전체 비활성** (is_active=0)
4. **DESK3 pool 306개** (기존 기록 106개 대비 +200 급증)
5. **DESK1**: 서비스 파일 없음, cron 없음 → 미구현 상태
6. **DESK5**: 20 WATCHING, **DESK4**: 18 WATCHING 유지

---

## 생성된 보고서

- 경로: `/root/kis-autotrade-v4/report/v41/CUR-V41-DESK-STATUS-SUMMARY-001-20260306.md`
- 생성 시각: 2026-03-06 10:38:49 KST

---

## 절대 금지 사항 준수 확인

- [x] DB 변경 없음 (SELECT only)
- [x] 서비스 재시작 없음
- [x] /root/kis-autotrade-v4 내부에서만 파일 생성
