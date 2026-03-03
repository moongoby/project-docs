---
project: KIS
task_id: CUR-V41-DESK2-SIGNAL-RUN-001
completed_at: 2026-03-03T11:35:00+09:00
status: SUCCESS
---

# RESULT: CUR-V41-DESK2-SIGNAL-RUN-001

## 1. realtime_signal 수동 실행 결과

```
INSERTED=0
INFO __main__ desk2_realtime_signal signal_date=2026-03-03 inserted=0
```

- 실행 경로: `PYTHONPATH=/root/kis-autotrade-v4/backend python3 scripts/desk2/desk2_realtime_signal.py`
- INSERTED=0: 신호 6건이 이미 11:27:04에 삽입되어 있어 중복 방지 로직(`_already_signaled()`)으로 재삽입 없음
- **실행 성공** (exit 0)

### DB URL 이슈 (수동 실행 시 주의)
- `.env`의 `DATABASE_URL`은 `postgresql+asyncpg://` 형식 → psycopg2 파싱 불가
- 해결: `DATABASE_URL_SYNC`의 `postgresql+psycopg2://` → `postgresql://` 변환하여 실행

## 2. 크론 로그 확인

| 로그 파일 | 상태 | 내용 |
|-----------|------|------|
| `logs/cron/desk2_signal.log` | ❌ 4회 실패 | `psycopg2.ProgrammingError: invalid dsn` (asyncpg URL 파싱 오류) |
| `logs/cron/desk2_prescoring.log` | NO_LOG_YET | 크론 미실행 |

**크론 버그**: 크론 환경에서 `DATABASE_URL=postgresql+asyncpg://...`로 실행 → psycopg2 파싱 실패
→ 크론 스크립트에서 `DATABASE_URL_SYNC` 사용 또는 URL 변환 패치 필요

## 3. DB 전수 확인

| 테이블 | 건수 | 비고 |
|--------|------|------|
| v4_desk2_candidates | 10 | 2026-03-03 당일 10건 |
| v4_desk2_signals | 6 | 당일 6건 FILLED |
| v4_desk2_trades | 6 | 당일 6건 |
| v4_desk2_daily_summary | 1 | 2026-03-03 요약 1건 |
| v4_mock_trades (오늘) | 56 | 당일 모의매매 56건 |

## 4. v4_desk2_signals 상세 (2026-03-03)

| id | stock_code | stock_type | signal | signal_time | price | dip_pct | status | created_at |
|----|------------|------------|--------|-------------|-------|---------|--------|------------|
| 1 | 307750 | TREND | T5 | 09:35 | 3,721 | 0.3% | FILLED | 11:27:04 |
| 2 | 027360 | TREND | T5 | 09:42 | 5,938 | 0.5% | FILLED | 11:27:04 |
| 3 | 001020 | TREND | T5 | 09:49 | 737 | 0.8% | FILLED | 11:27:04 |
| 4 | 054620 | REVERSAL | S1 | 09:56 | 4,870 | 2.5% | FILLED | 11:27:04 |
| 5 | 322000 | REVERSAL | S1 | 10:03 | 100,880 | 3.0% | FILLED | 11:27:04 |
| 6 | 105330 | BORDER | S1 | 10:10 | 4,816 | 1.2% | FILLED | 11:27:04 |

## 5. v4_desk2_daily_summary (2026-03-03)

| 항목 | 값 |
|------|-----|
| total_trades | 6 |
| win_count | 4 |
| loss_count | 2 |
| win_rate | 66.667% |
| gross_pnl | 79,019원 |
| net_pnl | 61,326원 |
| avg_pnl_pct | 1.3333% |
| max_loss_pct | -2.1% |
| TREND/REVERSAL/BORDER | 3/2/1 |
| market_regime | NORMAL |

## 6. 조치 필요 사항

1. **크론 DB URL 버그**: `scripts/desk2/desk2_realtime_signal.py` line 110
   `os.environ.get("DATABASE_URL", ...)` → psycopg2 호환 URL로 변환하는 로직 추가 필요
   예: `db_url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg2://", "postgresql://")`

2. **desk2_prescoring 크론**: 로그 없음 → crontab 등록 여부 확인 필요

## 결론

- 당일 신호 6건 DB 정상 적재 확인 ✅
- daily_summary 정상 (승률 66.7%, net_pnl 61,326원) ✅
- 크론 자동 실행은 DB URL 이슈로 실패 중 ❌ → 패치 필요
- 수동 실행 시 INSERTED=0 (중복 방지 정상 동작) ✅
