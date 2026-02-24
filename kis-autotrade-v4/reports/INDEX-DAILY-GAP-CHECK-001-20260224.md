# INDEX-DAILY-GAP-CHECK-001 — index_daily 테이블 결측(close=0) 구간 조사

**작업ID:** INDEX-DAILY-GAP-CHECK-001  
**작업명:** index_daily 테이블 결측(close=0) 구간 조사  
**일시:** 2026-02-24 KST  
**자체승인:** O (읽기 전용, SELECT만 수행)

---

## 1. 사전 필수 읽기

| 파일 | 결과 |
|------|------|
| `/root/kis-autotrade-v4/.cursor/rules/kis-v41-rules.md` | ✅ 읽음 |

---

## 2. index_daily 테이블 구조

| column_name | data_type |
|-------------|-----------|
| id | integer |
| index_code | character varying |
| index_name | character varying |
| date | character varying |
| open | real |
| high | real |
| low | real |
| close | real |
| volume | bigint |
| trade_amount | real |
| created_at | timestamp without time zone |

- **전체 행 수:** 1,476행

---

## 3. 결측(close=0 또는 NULL) 구간

### 3.1 기간별 요약

| index_code | gap_start | gap_end | gap_days |
|------------|-----------|---------|----------|
| 0001 | 20251203 | 20260213 | 50 |
| 1001 | 20251203 | 20260213 | 50 |
| 2001 | 20251203 | 20260213 | 50 |

- **결측 기간:** 2025-12-03 ~ 2026-02-13 (영업일 50일)
- **대상 지수:** 3종(0001, 1001, 2001) 동일 구간
- **특징:** 해당 구간은 open/high/low/close 모두 0, volume만 존재

### 3.2 정상 데이터 범위 (지수별)

| index_code | min_date | max_date | total_rows | valid_rows | zero_rows |
|------------|----------|----------|------------|------------|-----------|
| 0001 | 20240213 | 20260223 | 492 | 442 | 50 |
| 1001 | 20240213 | 20260223 | 492 | 442 | 50 |
| 2001 | 20240213 | 20260223 | 492 | 442 | 50 |

- **정상 OHLC:** 2024-02-13 ~ 2025-12-02, 2026-02-14 ~ 2026-02-23
- **결측:** 2025-12-03 ~ 2026-02-13 (50일)

---

## 4. 차트 시각화 영향 범위

- **CHART-HEALTH-CHECK-001**에서 확인된 구간: **2025-12-03 ~ 2026-02-13**에서 `index_close: 0` 노출.
- **index_daily** 결측 구간과 **완전히 일치**함.
- **영향:** regime-timeline API의 해당 구간 `index_close`가 0으로 내려가 차트에서 지수 라인이 끊기거나 0으로 표시될 수 있음.

---

## 5. 재수집 필요 여부 및 CEO 승인 사항

| 항목 | 내용 |
|------|------|
| **재수집 필요 여부** | **필요.** 2025-12-03 ~ 2026-02-13 구간 3지수(0001, 1001, 2001) OHLC 재수집 시 차트·레짐 연계 데이터 정상화 가능. |
| **실행 전 필수** | **CEO 승인 후에만** 재수집 스크립트/배치 실행. (kis-v41-rules: "index_daily OHLC=0 재수집" CEO 결정 대기) |
| **본 작업 범위** | SELECT만 수행. INSERT/UPDATE/DELETE 미실행. API/monitor/scheduler 재시작 없음. |

---

## 6. 결론

- **index_daily** 테이블: 1,476행, 3지수(0001, 1001, 2001), 2024-02-13 ~ 2026-02-23 기간 보유.
- **결측 구간:** 2025-12-03 ~ 2026-02-13, 50일, 3지수 동일. close=0이며 open/high/low도 0, volume만 존재.
- **차트 영향:** CHART-HEALTH-CHECK-001의 regime-timeline `index_close: 0` 구간과 동일. 재수집 시 해당 구간 시각화 정상화 가능.
- **다음 단계:** 재수집 실행은 **CEO 승인 후** 진행.

---

*보고서 작성: 2026-02-24 KST*
