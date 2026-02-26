# INDEX-DAILY-REFILL-001 — index_daily 결측 구간 OHLC 재수집 보고서

**작업ID:** INDEX-DAILY-REFILL-001  
**작업명:** index_daily 결측 구간(2025-12-03~2026-02-13) OHLC 재수집  
**실행일:** 2026-02-24 KST  
**CEO 승인:** O (데이터 수집 무조건 수행)

---

## 1. 요약

- **목적:** `index_daily` 테이블에서 `close = 0` 또는 `close IS NULL`인 구간(2025-12-03 ~ 2026-02-13)에 대해 3지수(0001 KOSPI, 1001 KOSDAQ, 2001 KOSPI200) OHLC를 재수집하여 **UPDATE만** 수행.
- **결과:** 재수집 150건 반영, 결측 0건으로 정리. DELETE 미사용, 서비스 재시작 없음.

---

## 2. 사전 준비

- **규칙 참조:** `kis-v41-rules.md` (kis-v41-api / monitor / scheduler 재시작 금지, index_daily DELETE 금지 준수)
- **DB 백업:**  
  `pg_dump -h localhost -U kis_admin -d kisautotrade -F c -f /tmp/backup_INDEX-REFILL-001_20260224.dump`  
  완료. 파일: `/tmp/backup_INDEX-REFILL-001_20260224.dump` (약 238MB)

---

## 3. STEP 1 — 결측 구간 재확인

```sql
SELECT index_code, COUNT(*) as zero_rows, MIN(date) as gap_start, MAX(date) as gap_end
FROM index_daily WHERE (close = 0 OR close IS NULL) GROUP BY index_code;
```

| index_code | zero_rows | gap_start | gap_end  |
|------------|-----------|-----------|----------|
| 0001       | 50        | 20251203  | 20260213 |
| 1001       | 50        | 20251203  | 20260213 |
| 2001       | 50        | 20251203  | 20260213 |

---

## 4. STEP 2 — 기존 수집 스크립트

- **스크립트:** `scripts/collect_index_daily.sh` → 내부에서 `scripts/collection/historical_backfill.py` 호출
- **수집 로직:** `backend` 참조 없음. `scripts/collection/historical_backfill.py`  
  - KIS API: FHKUP03500100 (지수 일봉)  
  - 저장: `index_daily` INSERT + **ON CONFLICT (index_code, date) DO UPDATE** (DELETE 없음)

---

## 5. STEP 3 — 재수집 실행

- **방식:** `historical_backfill.py --index-only --start 20251203 --end 20260213`
- **인증:** 최초 실행 시 legacy `.env` 기준 KIS 토큰 실패. **USE_KIS_CONFIG=1** 로 DB `kis_configs`에서 실계좌 키/토큰 로드 후 성공.
- **실행 명령 예시:**
  ```bash
  cd /root/kis-autotrade-v4 && source venv/bin/activate
  set -a && source .env && set +a
  export USE_KIS_CONFIG=1
  PYTHONPATH=/root/kis-autotrade-v4:/root/kis-autotrade-v4/backend \
    python scripts/collection/historical_backfill.py --index-only --start 20251203 --end 20260213
  ```
- **로그:** `Backfill done: ohlcv_rows=0 index_rows=150 errors=0`

---

## 6. STEP 4 — 검증

```sql
SELECT index_code, COUNT(*) as zero_rows
FROM index_daily WHERE (close = 0 OR close IS NULL) GROUP BY index_code;
```

**결과:** 0 rows (결측 없음)

**구간 양끝 샘플 (20251203, 20260213):**

| index_code | date     | open    | high    | low     | close   |
|------------|----------|---------|---------|---------|---------|
| 0001       | 20251203 | 4010.26 | 4052.83 | 3987.76 | 4036.30 |
| 0001       | 20260213 | 5513.71 | 5583.74 | 5480.92 | 5507.01 |
| 1001       | 20251203 | 931.49  | 932.98  | 926.08  | 932.01  |
| 1001       | 20260213 | 1113.53 | 1117.91 | 1099.62 | 1106.08 |
| 2001       | 20251203 | 567.89  | 573.84  | 564.19  | 570.79  |
| 2001       | 20260213 | 815.97  | 827.14  | 811.16  | 814.59  |

---

## 7. 준수 사항

- kis-v41-api / kis-v41-monitor / kis-v41-scheduler **재시작하지 않음**
- index_daily **DELETE 미실행** (ON CONFLICT DO UPDATE만 사용)

---

## 8. 권장 사항

- **정기 수집:** `scripts/collect_index_daily.sh` 크론 시, 수집 서버에서 KIS 인증이 필요하면 `USE_KIS_CONFIG=1` 및 루트 `.env`(또는 legacy `.env`)의 DB/SECRET_KEY 설정 유지 권장.
- **재수집 필요 시:** 동일 명령으로 구간 `--start`/`--end` 지정하여 재실행 가능.

---

*작성: 2026-02-24 (INDEX-DAILY-REFILL-001)*
