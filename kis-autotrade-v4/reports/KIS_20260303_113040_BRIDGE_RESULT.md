---
project: KIS
task_id: CUR-V41-DESK2-SIGNAL-RUN-001
completed_at: "2026-03-03T11:35:31 KST"
status: DONE
---

# CUR-V41-DESK2-SIGNAL-RUN-001 실행 결과

[인계 확인]
직전 완료: CUR-V41-DIRECTIVE-AUTOMATION-002
현재 단계: Phase 2C (Virtual Run)
CEO 지시 적용: D-001, D-002, D-003
strategy_cards: 60
open_positions: 14

---

## Step 1: realtime_signal 수동 실행

```
PYTHONPATH=/root/kis-autotrade-v4/backend python3 scripts/desk2/desk2_realtime_signal.py
→ INFO __main__ desk2_realtime_signal signal_date=2026-03-03 inserted=0
→ INSERTED=0
```

- **성공** (DATABASE_URL asyncpg 포맷 버그 → postgresql:// URL로 오버라이드하여 실행)
- inserted=0: 당일 시그널(6건)이 이미 11:27에 입력되어 있어 중복 방지됨

---

## Step 2: 크론 로그 확인

```
-rw-r--r-- 1 root root 3824 Mar  3 11:30 /root/kis-autotrade-v4/logs/cron/desk2_signal.log
```

- 로그 파일 존재, 크론 **4회 연속 실패**
- 원인: `.env`의 `DATABASE_URL=postgresql+asyncpg://...` 포맷을 psycopg2가 파싱 불가
- **버그**: `desk2_realtime_signal.py:110` — `DATABASE_URL_SYNC` 대신 `DATABASE_URL` 우선 사용
- 수동 실행은 `DATABASE_URL` 직접 오버라이드(`postgresql://`)로 성공

---

## Step 3: DB 전수 확인

| 테이블 | 건수 | 비고 |
|--------|------|------|
| `v4_desk2_candidates` | 10 | 오늘(03-03), 11:20 생성 |
| `v4_desk2_signals` | 6 | 오늘(03-03), 11:27 생성, 전부 FILLED |
| `v4_desk2_trades` | 6 | 오늘 |
| `v4_desk2_daily_summary` | 1 | 오늘, WR=66.67%, 순PnL=+61,326원 |
| `v4_mock_trades` (오늘) | 56 | Virtual Run 정상 기록 중 |

---

## Step 4: v4_desk2_signals 상세 (최근 10건)

| signal_date | stock_code | stock_type | signal_name | signal_time | signal_price | status |
|-------------|------------|------------|-------------|-------------|-------------|--------|
| 2026-03-03 | 105330 | BORDER | S1 | 10:10 | 4,816 | FILLED |
| 2026-03-03 | 322000 | REVERSAL | S1 | 10:03 | 100,880 | FILLED |
| 2026-03-03 | 054620 | REVERSAL | S1 | 09:56 | 4,870 | FILLED |
| 2026-03-03 | 001020 | TREND | T5 | 09:49 | 737 | FILLED |
| 2026-03-03 | 027360 | TREND | T5 | 09:42 | 5,938 | FILLED |
| 2026-03-03 | 307750 | TREND | T5 | 09:35 | 3,721 | FILLED |

**전 6건 FILLED** — TREND(T5) 3건 + REVERSAL(S1) 2건 + BORDER(S1) 1건

---

## Daily Summary (2026-03-03)

| 항목 | 값 |
|------|----|
| 총 거래 | 6건 |
| 승 / 패 | 4 / 2 |
| 승률 | 66.67% |
| Gross PnL | +79,019원 |
| Net PnL | +61,326원 |
| 평균 PnL% | +1.33% |
| 최대 손실% | -2.10% |
| 레짐 | NORMAL |

---

## 핵심 발견 및 버그 보고

### [BUG] desk2_realtime_signal.py DB 연결 버그

- **위치**: `scripts/desk2/desk2_realtime_signal.py:110`
- **원인**: `.env`의 `DATABASE_URL`이 `postgresql+asyncpg://` 포맷(SQLAlchemy async)이나, 스크립트는 psycopg2로 직접 연결 시도
- **결과**: 크론 실행 시 매번 실패 (4회 연속)
- **임시 해결**: 수동 실행 시 `DATABASE_URL=postgresql://...` 오버라이드
- **영구 수정 필요**: `DATABASE_URL_SYNC` 우선 사용 또는 dialect prefix 제거 로직 추가 (root 권한 필요)

### 시그널 정상 반영 확인

- 6개 시그널 모두 FILLED, DB 반영 정상
- candidates 10건(score rank 1~10) → signals 6건(상위 6종목 채택)
- daily_summary 자동 생성 확인

---

## echo

```
DONE
```
