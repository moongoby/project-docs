---
project: KIS
task_id: CUR-V41-DESK2-ACTIVATE-001
completed_at: "2026-03-03 11:15 KST"
commit: 2af6e41e
status: COMPLETED
---

## [CURSOR-KIS] DESK2-ACTIVATE-001 작업 결과

---

## 작업 1 — ohlcv_daily 03-02/03-03 백필 확인

| date | count | 비고 |
|------|-------|------|
| 20260302 | 0 | 삼일절 대체공휴일(휴장) — 정상 |
| 20260303 | 3,839 | ✅ 정상 수집 |

- 03-02(월)는 삼일절(3/1) 대체공휴일 → 휴장 = 데이터 없음 정상
- 백필 시도 후 확인, 불필요 프로세스 종료

---

## 작업 2 — desk2_prescoring 버그 수정 + 실행

### 버그 2개 발견 및 수정

| 버그 | 원인 | 수정 |
|------|------|------|
| ① 날짜형식 불일치 | `d.isoformat()` → `'2026-03-03'` vs ohlcv_daily 저장형식 `'20260303'` | `d.strftime("%Y%m%d")` 사용 |
| ② 공휴일 미스킵 | `_prev_trading_days`가 주말만 스킵, 공휴일(03-02) 포함 → ohlcv없어 0건 | DB 실거래일 조회로 재설계 |

### target_date 기본값 수정
- 기존: `date.today() + 1` (내일) → 08:55 실행 시 D-1이 오늘(미수집)
- 수정: `date.today()` (당일) → 08:55 실행 시 D-1이 어제(수집 완료)

### 실행 결과
```
INFO __main__ desk2_prescoring target_date=2026-03-03 inserted=10 top_n=10 
INSERTED=10
```

### Top 3 후보
| rank | stock_code | stock_name | score | news | vol_ratio |
|------|-----------|------------|-------|------|-----------|
| 1 | 307750 | 국전약품 | 2.0298 | 10 | 4.67 |
| 2 | 027360 | 아주IB투자 | 1.8572 | 28 | 3.63 |
| 3 | 001020 | 페이퍼코리아 | 1.8442 | 10 | 4.50 |

---

## 작업 3 — DESK2 크론 등록

```cron
# 장전 prescoring (D-1 데이터로 당일 후보 선정)
55 8 * * 1-5 source venv/bin/activate && ... python3 scripts/desk2/desk2_prescoring.py

# 장중 realtime signal (5분 간격)
*/5 9-14 * * 1-5 cd /root/kis-autotrade-v4 && ... python3 scripts/desk2/desk2_realtime_signal.py
```

---

## 작업 4 — 전체 파이프라인 검증

| 테이블 | rows | 상태 |
|--------|------|------|
| v4_desk2_candidates | 10 | ✅ 활성화 |
| v4_desk2_signals | 0 | 장중 신호 대기 |
| v4_desk2_trades | 0 | 신호 후 체결 대기 |
| v4_desk2_daily_summary | 0 | 장마감 후 집계 |
| v4_mock_trades(03-03) | 56 | ✅ 기존 매매 정상 |

---

## 수정 파일

- `scripts/desk2/desk2_prescoring.py` → 커밋 `2af6e41e`

---

## DESK2 파이프라인 활성화 여부

**부분 YES**
- candidates 10건 생성 ✅
- prescoring/signal 크론 등록 ✅
- realtime_signal은 장중 크론 대기 (candidates 기반 신호 생성 예정)
- desk2_signals/trades는 장중 realtime_signal 실행 후 생성 예정

security_scan: 0건 | path_check: PASS | commit: 2af6e41e | HTTP: 200
