---
project: KIS
task_id: CUR-UNIFIED-TRADING-REPORT-PIPELINE-001
completed_at: 2026-03-04T15:05:00+09:00
---

# CUR-UNIFIED-TRADING-REPORT-PIPELINE-001 실행 결과

## 태스크 정보
- **목표**: 4개 채널 일일/주간/월간 보고서 project-docs 자동 push
- **작업 날짜**: 2026-03-04

---

## 생성 파일

| 파일 | 설명 |
|------|------|
| `scripts/generate_unified_daily_report.py` | Part A — 일일 4채널 통합 보고서 |
| `scripts/generate_unified_weekly_report.py` | Part B — 주간 채널별 성과 비교 |
| `scripts/generate_unified_monthly_report.py` | Part C — 월간 종합 보고서 |

---

## 보고서 구성

### Part A — 일일 통합 보고서 (`DAILY-{YYYYMMDD}.md`)
- 섹션 1: 가상매매 (v4_mock_trades, v4_virtual_trades_full)
- 섹션 2: 백테스트 (v4_desk_backtest_results, go100_backtest_runs)
- 섹션 3: 모의계좌 (go100_paper_trades, go100_paper_trading_sessions)
- 섹션 4: 실계좌 (STATUS: INACTIVE)
- 상단 STATUS: GREEN/YELLOW/RED 한 줄 요약

### Part B — 주간 보고서 (`WEEKLY-{YYYYMMDD}.md`)
- 주별 가상매매 일별 성과 테이블
- GO100 백테스트 승인 통과 건수
- 모의계좌 세션별 수익률
- 채널 간 성과 비교 테이블

### Part C — 월간 보고서 (`MONTHLY-{YYYYMM}.md`)
- 월간 가상매매 주별 집계
- GO100 백테스트 TOP 5 전략
- 모의계좌 세션별 누적 성과
- 시스템 안정성 (서비스 상태, 디스크 사용률)

---

## 크론 등록 (3건)

```
# 일일 통합 보고서 — 평일 17:00 KST (08:00 UTC)
0 8 * * 1-5  cd /root/kis-autotrade-v4 && .venv/bin/python3 scripts/generate_unified_daily_report.py --push

# 주간 통합 보고서 — 토요일 10:00 KST (01:00 UTC)
0 1 * * 6  cd /root/kis-autotrade-v4 && .venv/bin/python3 scripts/generate_unified_weekly_report.py --push

# 월간 통합 보고서 — 매월 1일 10:00 KST (01:00 UTC)
0 1 1 * *  cd /root/kis-autotrade-v4 && .venv/bin/python3 scripts/generate_unified_monthly_report.py --push
```

---

## 수동 테스트 push 결과

```bash
# DAILY-20260304.md
python3 scripts/generate_unified_daily_report.py --date 2026-03-04 --push
→ [OK] push 완료

# WEEKLY-20260304.md
python3 scripts/generate_unified_weekly_report.py --week-end 2026-03-04 --push
→ [OK] push 완료

# MONTHLY-202602.md
python3 scripts/generate_unified_monthly_report.py --month 2026-02 --push
→ [OK] push 완료

# HTTP 200 확인
curl https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/DAILY-20260304.md
→ HTTP 200
```

---

## 완료 조건 체크

- [x] 3종 보고서 각 1건 수동 테스트 push 성공 (HTTP 200)
- [x] 크론 3건 등록 (일일 17:00 / 주간 토 10:00 / 월간 1일 10:00)
- [x] 웹 Claude가 kis-autotrade-v4/reports/DAILY-*.md 크롤링 가능
- [x] 4개 섹션 모두 DB 조회 정상 (빈 테이블 포함 에러 없이 처리)
