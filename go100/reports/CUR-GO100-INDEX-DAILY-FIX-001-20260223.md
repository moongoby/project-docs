# CUR-GO100-INDEX-DAILY-FIX-001 — index_daily OHLC=0 수정 및 재수집

**일시:** 2026-02-23 21:30 KST  
**서버:** root@211.188.51.113  
**작업 ID:** CUR-GO100-INDEX-DAILY-FIX-001

---

## 1. 요약

- **문제:** `index_daily` 테이블에 OHLC=0인 행 150건 존재. 원인은 `historical_backfill.py`가 KIS 지수 API 응답에서 주식용 필드(`stck_oprc` 등)만 사용해, 지수용 필드(`bstp_nmix_oprc` 등)를 사용하지 않았기 때문.
- **영향:** GO100 레짐 계산, 차트 API, 백테스트 전부 오염.
- **조치:** `_fetch_index_daily_sync()` 내 output2 파싱에서 지수 전용 필드(`bstp_nmix_*`) 우선 사용, 없으면 `stck_*` 폴백. 코드 반영 후 재수집으로 OHLC 갱신.

---

## 2. 수정 내용

### 2.1 수정 전

- `_fetch_index_daily_sync()` output2 파싱:
  - `open  = float(row.get("stck_oprc") or 0)`
  - `high  = float(row.get("stck_hgpr") or 0)`
  - `low   = float(row.get("stck_lwpr") or 0)`
  - `close = float(row.get("stck_clpr") or 0)`
- 지수 API는 위 주식용 필드를 비우고 `bstp_nmix_*`로 반환 → OHLC가 0으로 저장됨.

### 2.2 수정 후

- 지수 전용 필드 우선, 주식용 폴백:
  - `open  = float(row.get("bstp_nmix_oprc") or row.get("stck_oprc") or 0)`
  - `high  = float(row.get("bstp_nmix_hgpr") or row.get("stck_hgpr") or 0)`
  - `low   = float(row.get("bstp_nmix_lwpr") or row.get("stck_lwpr") or 0)`
  - `close = float(row.get("bstp_nmix_prpr") or row.get("stck_clpr") or 0)`
- 주식 일봉 파싱(`_fetch_daily_ohlcv_sync`)은 **변경 없음** — `stck_*`만 사용 유지.

### 2.3 변경 파일

- **단일 파일:** `scripts/collection/historical_backfill.py`
  - `_fetch_index_daily_sync()` 내 output2 for 루프에서 OHLC 4줄만 위와 같이 수정.

---

## 3. 수정 전 현황 (STEP 2 기록)

| 항목 | 값 |
|------|-----|
| index_daily 총 행 수 | 1,467 |
| OHLC=0 행 수 | 150 |
| OHLC=0 구간 | 20251203 ~ 20260213 |
| index_code별 zero_cnt | 0001: 50, 1001: 50, 2001: 50 |

---

## 4. 백업·재수집·검증

### 4.1 백업

- `pg_dump -t index_daily -F c -f /tmp/backup_INDEX-DAILY-FIX-001_<timestamp>.dump` 실행 완료.

### 4.2 재수집

- **명령:**  
  `PYTHONPATH=/root/kis-autotrade-v4/backend python scripts/collection/historical_backfill.py --index-only --start 20251101 --end 20260223`
- **실행 시점:** KIS 토큰 미설정으로 재수집 미실행. 코드 수정만 반영된 상태.
- **재수집 방법:** KIS 자격증명(legacy/.env 또는 kis_configs) 설정 후 위 명령 재실행 시, ON CONFLICT DO UPDATE로 기존 150건 OHLC가 정상값으로 갱신됨.

### 4.3 검증 (재수집 후 기대)

- `SELECT COUNT(*) FROM index_daily WHERE (open = 0 OR close = 0) AND date >= '20251101';` → **0건**이면 성공.
- 20260210~20260213 구간 샘플: open/high/low/close에 실제 지수값 존재 확인.

---

## 5. DB·스키마·서비스

- **DB 변경:** DDL 없음. `index_daily` UPDATE만 (재수집 시 OHLC 값 갱신).
- **strategy_cards:** 변경 없음.
- **v4_positions:** 변경 없음.
- **kis-v41-* 서비스:** 재시작 없음 (규칙 준수).
- **go100 / go100-frontend:** 재시작 불필요 (배치 스크립트만 수정).

---

## 6. 검수 (STEP 9)

- `git diff HEAD~1 -- scripts/collection/historical_backfill.py` 로 변경 확인.
- 변경 내용은 `_fetch_index_daily_sync` 함수 내 OHLC 파싱 4줄(+ 주석)만 해당. 다른 함수(`_fetch_daily_ohlcv_sync` 등) 무영향.

---

## 7. 참조

- 진단 보고서: [INDEX-DAILY-DIAG-001-20260223](https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/INDEX-DAILY-DIAG-001-20260223.md)
- 지시서: CUR-GO100-INDEX-DAILY-FIX-001 (2026-02-23)
- 코드 repo: `/root/kis-autotrade-v4` (branch: phase-2c-command-center)
