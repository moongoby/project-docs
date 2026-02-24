# REGIME-DATA-STATUS-001 — v4_market_regime_daily 현재 상태 점검 보고서

**작업 ID:** REGIME-DATA-STATUS-001  
**일시:** 2026-02-24 KST  
**작업 유형:** 읽기 전용 조회 + 보고서 작성 (INSERT/UPDATE/DELETE 미수행)  
**프로젝트:** /root/kis-autotrade-v4  

---

## 1. 요약

| 항목 | 결과 |
|------|------|
| 전체 행 수 | **552행** |
| KOSPI | 276행, 2025-01-02 ~ 2026-02-23 |
| KOSDAQ | 276행, 2025-01-02 ~ 2026-02-23 |
| 누락 구간 | **없음** (인계서 기준 KOSDAQ 121일만 있던 이슈는 백필 완료 상태) |
| CUR-REGIME-BACKFILL-002 원격 파일 | **404** (URL 기준 해당 파일명 없음) |
| 로컬 관련 보고서 | report/v41/REGIME-BACKFILL-002-20260224.md 존재 |

---

## 2. 테이블 구조 (v4_market_regime_daily)

| column_name | data_type |
|-------------|-----------|
| id | bigint |
| date | date |
| regime | character varying |
| regime_score | numeric |
| kospi_ret_20d | numeric |
| ma5 | numeric |
| ma20 | numeric |
| ma60 | numeric |
| ma_alignment | character varying |
| bull_ratio_20d | numeric |
| vkospi | numeric |
| foreign_flow_20d | bigint |
| previous_regime | character varying |
| transition_note | text |
| created_at | timestamp with time zone |
| updated_at | timestamp with time zone |
| hysteresis_up_count | integer |
| hysteresis_down_count | integer |
| pending_regime | character varying |
| **market_type** | character varying |

- **market_type** 컬럼 존재 확인됨 (UNIQUE(date, market_type) 제약은 REGIME-BACKFILL-002 보고서 참고).

---

## 3. market_type별 요약 (조회 시점: 2026-02-24)

| market_type | cnt | min_date | max_date |
|-------------|-----|----------|----------|
| KOSDAQ | 276 | 2025-01-02 | 2026-02-23 |
| KOSPI | 276 | 2025-01-02 | 2026-02-23 |

---

## 4. 레짐 분포 (market_type × regime)

| market_type | regime | cnt |
|-------------|--------|-----|
| KOSDAQ | MILD_TREND_DOWN | 46 |
| KOSDAQ | MILD_TREND_UP | 100 |
| KOSDAQ | SIDEWAYS | 93 |
| KOSDAQ | STRONG_TREND_DOWN | 31 |
| KOSDAQ | STRONG_TREND_UP | 6 |
| KOSPI | MILD_TREND_DOWN | 34 |
| KOSPI | MILD_TREND_UP | 121 |
| KOSPI | SIDEWAYS | 98 |
| KOSPI | STRONG_TREND_DOWN | 20 |
| KOSPI | STRONG_TREND_UP | 3 |

---

## 5. 누락 구간

- **KOSPI:** 276행, 2025-01-02 ~ 2026-02-23 → **정상** (인계서 기준과 일치).
- **KOSDAQ:** 276행, 2025-01-02 ~ 2026-02-23 → **현재 DB 기준 누락 없음.**  
  - 인계서에는 "KOSDAQ 121일만 있음, 2025-07-04 이후 누락 (CEO 승인 대기)"로 되어 있었으나,  
    REGIME-BACKFILL-002 백필 작업으로 동일 기간 보정된 상태로 확인됨.
- **AUDIT 보고서 59행 이슈:** kis-v41-rules.md의 DB 무결성 기준값에는 `v4_market_regime_daily: 59행`으로 기재되어 있음.  
  - 현재는 market_type별 이중화로 **552행**(KOSPI 276 + KOSDAQ 276)이므로, 59행은 **과거 단일 시장(KOSPI 등) 기준 또는 시점 차이**로 해석 가능.  
  - 규칙 문서의 기준값 갱신은 별도 문서/승인 후 반영 권장.

---

## 6. 기존 보고서 존재 여부

| 위치/URL | 파일명 | 결과 |
|----------|--------|------|
| 로컬 report/v41/ | REGIME-BACKFILL-002-20260224.md | 존재 |
| 로컬 report/v41/ | FULLBT-REGIME-003-20260224.md, REGIME-BT-EXEC-005-20260224.md 등 | 존재 |
| project-docs/reports/ | REGIME-BACKFILL-002-20260224.md | 존재 (동기화됨) |
| GitHub raw | CUR-REGIME-BACKFILL-002-20260224.md | **HTTP 404** (해당 파일명 없음) |

- **CUR-REGIME-BACKFILL-002-20260224.md** 는 지정 URL 기준으로는 존재하지 않음.  
  실무 참고용 백필 보고서는 **REGIME-BACKFILL-002-20260224.md** 로 로컬/ project-docs에 있음.

---

## 7. CEO 승인 필요 사항

- **KOSDAQ 전체 기간 백필:** 현재 DB에는 2025-01-02 ~ 2026-02-23 구간 276일 모두 존재하므로 **추가 백필 불필요**로 판단됨.
- 향후 레짐 필터·전환 방어 등 정책 적용 시, **레짐 데이터 기간/품질 재검증**이 필요하면 본 보고서와 REGIME-BACKFILL-002를 기준으로 진행 권장.

---

## 8. 결론

- **v4_market_regime_daily** 는 KOSPI·KOSDAQ 각 276행, 동일 기간(2025-01-02 ~ 2026-02-23)으로 **정상**이며, 인계서에 있던 KOSDAQ 누락 구간은 이미 보정된 상태임.
- 본 점검은 **SELECT만 수행**하였으며, kis-v41-api / monitor / scheduler 재시작 및 DB 변경 없음.
