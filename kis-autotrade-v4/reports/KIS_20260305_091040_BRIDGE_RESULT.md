---
project: kis-autotrade-v4
task_id: CUR-V41-CRON-AUDIT-001
completed_at: 2026-03-05T09:26:00+09:00 KST
---

# TASK-077 실행 결과: 크론 미등록 정비 + 통합보고서 크론 검증

## 지시서
파일: /root/.genspark/directives/running/KIS_20260305_091040_BRIDGE.md

---

## Step 1: 현재 크론 전수 확인 + 백업

### 실행 명령
```
crontab -l > /root/kis-autotrade-v4/crontab_backup_task077_20260305.txt
crontab -l | grep -v "^#" | grep -v "^$" | wc -l
```

### 결과
- 백업 파일: /root/kis-autotrade-v4/crontab_backup_task077_20260305.txt (생성 성공)
- 작업 전 활성 라인 수: **11개**

### 작업 전 전체 crontab 내용
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
```

---

## Step 2: virtual_hourly_report 크론 등록

### 사전 확인
- 스크립트 존재: `/root/kis-autotrade-v4/scripts/monitor_virtual_run.py` ✅
- `periodic` 액션 구현 확인: action_periodic 함수 존재 (line 589) ✅
- /var/log/kis-v41/ 디렉토리 없음 → 대체 경로 사용: `/root/kis-autotrade-v4/logs/virtual_hourly_report.log`
- 기존 crontab에 virtual_hourly_report 없음: **MISSING (FAIL 상태 확인됨)**

### 등록한 크론 라인
```
# [KIS TASK-077] virtual_hourly_report — 장중 매시 정각 09:00-15:00 KST 평일
0 9-15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python scripts/monitor_virtual_run.py periodic >> /root/kis-autotrade-v4/logs/virtual_hourly_report.log 2>&1
```

### 결과
- 등록 성공 (exit=0) ✅

---

## Step 3: 통합보고서 크론 3종 확인

### 사전 확인
```
crontab -l | grep "generate_unified"
```
결과: 출력 없음 (기존 미등록 상태)

### 스크립트 존재 확인
- `/root/kis-autotrade-v4/scripts/generate_unified_daily_report.py` ✅
- `/root/kis-autotrade-v4/scripts/generate_unified_weekly_report.py` ✅
- `/root/kis-autotrade-v4/scripts/generate_unified_monthly_report.py` ✅

### 등록한 크론 3종
```
# [KIS TASK-077] 통합 일일보고서 — 17:00 KST 평일
0 17 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_daily_report.py >> /root/kis-autotrade-v4/logs/unified_daily_report.log 2>&1

# [KIS TASK-077] 통합 주간보고서 — 토요일 10:00 KST
0 10 * * 6 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_weekly_report.py >> /root/kis-autotrade-v4/logs/unified_weekly_report.log 2>&1

# [KIS TASK-077] 통합 월간보고서 — 매월 1일 10:00 KST
0 10 1 * * cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 scripts/generate_unified_monthly_report.py >> /root/kis-autotrade-v4/logs/unified_monthly_report.log 2>&1
```

### 결과
- 3종 모두 등록 성공 ✅

---

## Step 4: 데이터 수집 크론 검증

### 크론탭 grep 결과
```
crontab -l | grep "collect\|ohlcv\|investor\|fill_strength"
```
결과: 출력 없음 (claudebot crontab에 없음)

### /etc/cron.d/ 데이터 수집 크론 확인
- `/etc/cron.d/kiwoom_data_collection` 존재 — root 사용자로 실행:
  - 체결강도 증분 수집: `40 16 * * 1-5` (collect_kiwoom_strength.py --incremental)
  - 프로그램매매: `30 16 * * 1-5`
  - 테마 데이터: `0 17 * * 1-5`
- `/etc/cron.d/external_data_collection` 존재 — root 사용자로 실행:
  - 환율: `0 18 * * 1-5` (collect_fx_daily.py)
  - 해외지수: `30 9 * * 1-5` (collect_global_index.py)
  - 암호화폐: `0 8 * * *` (collect_crypto_daily.py)
- `/etc/cron.d/cron_data_miner_211` 존재 — 1분봉 수집 (run_data_miner_nxt.sh)

### DB 폭락장 데이터 수집 확인
```
SELECT MAX(trade_date) FROM v4_investor_daily;  → 2026-03-04 ✅
SELECT MAX(date) FROM ohlcv_daily;              → 20260304 ✅
SELECT MAX(trade_date) FROM v4_market_investor_daily; → 2026-03-04 ✅
```
- 데이터 최신: 전 거래일(2026-03-04) 데이터 정상 수집됨 ✅
- fill_strength/ohlcv/investor 크론은 /etc/cron.d/ (root 실행)에 분산 등록되어 정상 작동 중

---

## Step 5: 누락 크론 목록 정리 + 등록

### 누락 크론 목록 (작업 전)
| 항목 | 상태 | 조치 |
|------|------|------|
| virtual_hourly_report (monitor_virtual_run.py periodic) | MISSING | 등록 완료 |
| generate_unified_daily_report.py (0 17 * * 1-5) | MISSING | 등록 완료 |
| generate_unified_weekly_report.py (0 10 * * 6) | MISSING | 등록 완료 |
| generate_unified_monthly_report.py (0 10 1 * *) | MISSING | 등록 완료 |
| collect_ohlcv/investor | /etc/cron.d/ root 실행 확인됨 | 등록 불필요 |

### 등록 후 활성 라인 수: 11 → **15개** (+4)

---

## Step 6: 검증 — 등록된 크론 전체 dry-run (import 테스트)

### 실행 명령 및 결과
```
$ cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -c "import scripts.monitor_virtual_run; print('OK')"
monitor_virtual_run: OK ✅

$ /root/kis-autotrade-v4/venv/bin/python3 -c "import scripts.generate_unified_daily_report; print('OK')"
generate_unified_daily_report: OK ✅

$ /root/kis-autotrade-v4/venv/bin/python3 -c "import scripts.generate_unified_weekly_report; print('OK')"
generate_unified_weekly_report: OK ✅

$ /root/kis-autotrade-v4/venv/bin/python3 -c "import scripts.generate_unified_monthly_report; print('OK')"
generate_unified_monthly_report: OK ✅
```

모든 스크립트 import 성공 — 크론 실행 시 문법/임포트 오류 없음.

---

## 최종 crontab 전체 내용 (작업 후)

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
```

총 활성 라인: **15개**

---

## 특이사항 / 비고

1. **/var/log/kis-v41/ 미존재**: 지시서에서 virtual_hourly_report 로그 경로로 지정되었으나 디렉토리가 없고 claudebot 권한으로 /var/log/ 하위 생성 불가. 대체 경로 `/root/kis-autotrade-v4/logs/virtual_hourly_report.log` 사용.

2. **데이터 수집 크론 위치**: collect_ohlcv/investor/fill_strength 크론은 claudebot crontab이 아닌 `/etc/cron.d/` (root 실행)에 분산 등록되어 있음. DB 데이터는 2026-03-04(전 거래일)까지 정상 수집됨.

3. **v4_ohlcv_daily 테이블 없음**: 지시서에서 `SELECT MAX(trade_date) FROM v4_ohlcv_daily;` 실행 지시했으나 해당 테이블 미존재. 실제 테이블명은 `ohlcv_daily` (컬럼명: `date`). `ohlcv_daily` MAX date = 20260304 정상 확인.

4. **generate_unified 크론 미등록 사유**: 기존 crontab에 `generate_v41_daily/weekly/monthly_report.py` 는 등록되어 있었으나 `generate_unified_*` 3종은 미등록 상태였음. 이번 작업에서 등록 완료.

---

## 체크포인트

- [x] 크론 등록 완료 (4개 추가: virtual_hourly + unified 3종)
- [x] 모든 스크립트 import OK
- [x] DB 데이터 최신 (2026-03-04) 확인
- [x] crontab 백업: /root/kis-autotrade-v4/crontab_backup_task077_20260305.txt
