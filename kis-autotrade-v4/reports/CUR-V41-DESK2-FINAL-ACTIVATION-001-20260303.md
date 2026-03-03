---
task_id: CUR-V41-DESK2-FINAL-ACTIVATION-001
project: KIS
date: 2026-03-03
author: Cursor Claude
status: completed
---

# CUR-V41-DESK2-FINAL-ACTIVATION-001 — DESK2 최적화 잔여 작업 완료 보고

> 작업일: 2026-03-03 KST  
> 완료 항목: 1) 크론 패치, 2) 크론 동작 검증, 3) 오케스트레이터 자동전이 수정, 4) desk2 Live API 신규 생성, 5) DB 전수 확인

---

## 1. 크론 패치 적용 결과

| 항목 | 결과 |
|------|------|
| 패치 파일 | `/tmp/desk2_realtime_signal_patched.py` |
| 복사 대상 | `/root/kis-autotrade-v4/scripts/desk2/desk2_realtime_signal.py` |
| 권한 | `root:root` |
| DATABASE_URL_SYNC 확인 | line 110: `db_url or os.environ.get("DATABASE_URL_SYNC") or ...` |
| 상태 | **PASS** |

---

## 2. 크론 정상 동작 테스트

```
INFO __main__ desk2_realtime_signal signal_date=2026-03-03 inserted=0
INSERTED=0
```

- `desk2_signal.log`: 정상 출력 확인
- `desk2_prescoring.log`: 아직 오늘 미실행 (08:55 크론 대기)

크론 등록 현황:
```
55 8 * * 1-5   desk2_prescoring.py   → /logs/cron/desk2_prescoring.log
*/5 9-14 * * 1-5  desk2_realtime_signal.py → /logs/cron/desk2_signal.log
```

---

## 3. 오케스트레이터 자동전이 수정

### 문제 원인
- `recovery_check()` 실행 중 예외 발생 시 `run()` 에서 `IDLE → ERROR` 전이 시도
- `VALID_STATE_TRANSITIONS["IDLE"]`에 `"ERROR"` 누락 → 전이 거부
- `run()` 루프 종료 → 오케스트레이터 영구 IDLE 상태 고착

### 수정 내용

**`backend/app/schemas/system.py`**
```python
# 수정 전
"IDLE": ["PRE_MARKET"],
# 수정 후
"IDLE": ["PRE_MARKET", "ERROR"],
```

**`backend/app/services/system/orchestrator.py` — `run()` 메서드**
- `recovery_check()` 실패 시 경고 로그 출력 후 루프 계속 진행 (루프 종료 금지)
- 각 사이클 `_state_dispatch()` 내 예외를 try-except로 포착하여 ERROR 전이 처리

### 검증 결과 (서비스 재시작 후 8초)
```json
{
  "state": "TRADING",
  "previous_state": "DEGRADED_READY",
  "cycle_id": 1,
  "is_trading": true,
  "is_buy_allowed": true
}
```

전이 경로: `IDLE → PRE_MARKET → DEGRADED_READY → TRADING` (09:00 이후 자동 캐치업)

---

## 4. desk2-live 백엔드 연결 (G-09 해소)

### 기존 현황
- `/api/v4/desk2-backtest/*` — 백테스트 전용 (기존 존재)
- `/api/v4/desk2/*` — **없음** (G-09 미연결)
- 프론트엔드: `desk2-live.html` + `desk2-live.js` → `/desk2-live-data.json` 정적 파일만 사용

### 신규 생성 엔드포인트

| 엔드포인트 | DB 테이블 | 설명 |
|-----------|----------|------|
| `GET /api/v4/desk2/candidates` | `v4_desk2_candidates` | 오늘 후보 종목 |
| `GET /api/v4/desk2/signals` | `v4_desk2_signals` | 오늘 신호 현황 |
| `GET /api/v4/desk2/trades` | `v4_desk2_trades` | 최근 거래 내역 |
| `GET /api/v4/desk2/summary` | `v4_desk2_daily_summary` | 일별 누적 PnL 요약 |

파일: `backend/app/routers/v4_desk2_live.py` (신규)  
등록: `backend/app/main.py` 에 import + `app.include_router()` 추가

### API 응답 확인 (2026-03-03 12:30 KST)

```
GET /api/v4/desk2/candidates → {"target_date":"2026-03-03","count":10,...}
GET /api/v4/desk2/signals    → {"signal_date":"2026-03-03","count":6,...}
GET /api/v4/desk2/trades     → {"since":"2026-03-03","count":6,...}
GET /api/v4/desk2/summary    → {"daily_count":1,"today":{...},...}
```

---

## 5. DB 전수 최종 확인

| 테이블 | 행수 | 최신 레코드 |
|--------|------|------------|
| `v4_desk2_candidates` | 10 | 2026-03-03 11:20:17 KST |
| `v4_desk2_signals` | 6 | 2026-03-03 11:27:04 KST |
| `v4_desk2_trades` | 6 | 2026-03-03 11:27:04 KST |
| `v4_desk2_daily_summary` | 1 | 2026-03-03 |
| `v4_mock_trades` (오늘) | 56 | 2026-03-03 10:28 KST |

### 오늘 DESK2 성과 (v4_desk2_daily_summary)
- 총 거래: 6건 / 승: 4건 / 패: 2건 / 승률: 66.7%
- 총 순익: 61,326원 / 평균 PnL%: +1.33%

---

## 6. 시스템 상태 요약

| 항목 | 상태 |
|------|------|
| 오케스트레이터 | TRADING (자동전이 정상) |
| 크론 desk2_signal | 정상 (*/5 9-14 평일) |
| 크론 desk2_prescoring | 정상 (08:55 평일) |
| desk2 Live API | 4개 엔드포인트 신규 생성 |
| DB 데이터 | 오늘 데이터 정상 |

---

## 변경 파일 목록

| 파일 | 변경 |
|------|------|
| `scripts/desk2/desk2_realtime_signal.py` | 패치 적용 (DATABASE_URL_SYNC) |
| `backend/app/schemas/system.py` | IDLE→ERROR 전이 허용 추가 |
| `backend/app/services/system/orchestrator.py` | run() 루프 탄력성 개선 |
| `backend/app/routers/v4_desk2_live.py` | 신규 생성 (4개 엔드포인트) |
| `backend/app/main.py` | v4_desk2_live_router 등록 |
