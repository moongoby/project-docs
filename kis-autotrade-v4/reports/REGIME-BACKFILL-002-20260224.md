# CUR-REGIME-BACKFILL-002 레짐 보정 + 코스닥 백필 보고서

**작업 ID:** CUR-REGIME-BACKFILL-002  
**일시:** 2026-02-24 KST  
**서버:** root@[SERVER-IP]  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  

---

## 1. 요약

- **STEP 0:** KST 2026-02-24 12:13 확인, kis-v41-api/monitor/scheduler active, DB 백업 완료 (`/tmp/backup_REGIME_BACKFILL_20260224_121358.dump`).
- **STEP 1:** `v4_market_regime_daily`에 `market_type` 컬럼 및 UNIQUE(date, market_type) 제약 이미 반영됨. idempotent ALTER/UPDATE 수행.
- **STEP 2:** `regime_detector.py` 산식·히스테리시스 분석 완료. index_daily 0001/1001/2001 각 492건 (2024-02-13 ~ 2026-02-23).
- **STEP 3:** `scripts/analysis/backfill_regime_data.py` 작성·실행. 코스피 2025-01-01~2025-11-19, 코스닥 2025-01-01~2026-02-23 구간 ON CONFLICT DO NOTHING 처리.
- **STEP 4:** 레짐 분포·최근 판정·판정 이슈(코스피 5,900대 SIDEWAYS) 문서화.
- **STEP 5:** DB-SCHEMA.md 변경이력 추가.
- **STEP 6:** 본 보고서 작성 및 project-docs push.

---

## 2. 스키마 변경 내역

| 항목 | 내용 |
|------|------|
| 테이블 | v4_market_regime_daily |
| 추가 컬럼 | market_type VARCHAR(10) DEFAULT 'KOSPI' |
| 제약 | UNIQUE(date, market_type) — 기존 제약명: v4_market_regime_daily_date_market_key |
| 기존 행 | market_type = 'KOSPI'로 일괄 업데이트 |

---

## 3. 코스피/코스닥 레짐 분포

### 3.1 시장별 건수·기간 (검증 시점: 2026-02-24)

| market_type | COUNT | MIN(date) | MAX(date) |
|-------------|-------|-----------|-----------|
| KOSPI       | 276   | 2025-01-02 | 2026-02-23 |
| KOSDAQ      | 276   | 2025-01-02 | 2026-02-23 |

### 3.2 시장·레짐별 분포

| market_type | regime            | count |
|-------------|-------------------|-------|
| KOSDAQ      | MILD_TREND_DOWN   | 46    |
| KOSDAQ      | MILD_TREND_UP     | 100   |
| KOSDAQ      | SIDEWAYS          | 93    |
| KOSDAQ      | STRONG_TREND_DOWN | 31    |
| KOSDAQ      | STRONG_TREND_UP   | 6     |
| KOSPI       | MILD_TREND_DOWN   | 34    |
| KOSPI       | MILD_TREND_UP     | 121   |
| KOSPI       | SIDEWAYS          | 98    |
| KOSPI       | STRONG_TREND_DOWN | 20    |
| KOSPI       | STRONG_TREND_UP   | 3     |

### 3.3 2025년 코스피 레짐 분포 (first_date ~ last_date)

| regime            | count | first_date | last_date   |
|-------------------|-------|------------|-------------|
| MILD_TREND_UP     | 121   | 2025-02-14 | 2026-02-19  |
| SIDEWAYS          | 98    | 2025-01-09 | 2026-02-23  |
| MILD_TREND_DOWN   | 34    | 2025-01-02 | 2026-01-21  |
| STRONG_TREND_DOWN | 20    | 2025-12-05 | 2026-01-06  |
| STRONG_TREND_UP   | 3     | 2025-06-20 | 2025-06-24  |

### 3.4 전환점 요약

- **코스피:** 최근 10거래일 2026-02-23 기준 SIDEWAYS 다수, 2026-02-19·02-12~13 MILD_TREND_UP.
- **코스닥:** 동일 기간 index_daily 1001 기준 레짐 백필 완료, MILD_TREND_UP·SIDEWAYS 비중이 큼.

---

## 4. 레짐 판정 기준 검증 (코스피 5,900 = SIDEWAYS 이슈)

### 4.1 최근 코스피 판정 (상위 10일)

| date     | regime        | market_type |
|----------|---------------|-------------|
| 2026-02-23 | SIDEWAYS      | KOSPI       |
| 2026-02-20 | SIDEWAYS      | KOSPI       |
| 2026-02-19 | MILD_TREND_UP | KOSPI       |
| 2026-02-13 | MILD_TREND_UP | KOSPI       |
| 2026-02-12 | MILD_TREND_UP | KOSPI       |
| 2026-02-11 | SIDEWAYS      | KOSPI       |
| 2026-02-10 | SIDEWAYS      | KOSPI       |
| 2026-02-09 | SIDEWAYS      | KOSPI       |
| 2026-02-06 | SIDEWAYS      | KOSPI       |
| 2026-02-05 | SIDEWAYS      | KOSPI       |

### 4.2 regime_detector.py 임계값 요약

- **점수 → 레짐:**  
  - 81 이상: STRONG_TREND_UP  
  - 61 이상: MILD_TREND_UP  
  - 41 이상: SIDEWAYS  
  - 21 이상: MILD_TREND_DOWN  
  - 미만: STRONG_TREND_DOWN  

- **점수 구성 (총 100점, VKOSPI 없으면 90점 기준 스케일):**
  - KOSPI 20일 수익률: 25점 (5%↑ 25, 3%↑ 20, 1%↑ 15, -1~1% 12.5, -3% 8, -5% 4, 그 이하 0)
  - MA 배열: 20점 (BULL_ALIGNED 20, MIXED 10, BEAR_ALIGNED 0)
  - 양봉 비율 20일: 15점 (0.65↑ 15, 0.55↑ 11, 0.45↑ 7.5, 0.35↑ 4, 그 이하 0)
  - 거래대금 추이: 10점
  - 외국인 20일 순매수: 15점 (양수 11, ±1e9 7.5, 그 이하 4)
  - 상한가/하한가: 5점
  - VKOSPI: 10점 (없으면 90점 합계를 100으로 스케일)

- **히스테리시스:** 상승 전환 3일 연속, 하락 전환 2일 연속. STRONG_TREND_DOWN 탈출 시 3일 연속 score 개선 추가 확인.

### 4.3 현재 시장이 STRONG_BULL로 보이는데 SIDEWAYS로 나오는 원인

- 지수 수준(예: 코스피 5,900)만으로는 레짐이 정해지지 않으며, **20일 수익률·MA·양봉비율·외국인·VKOSPI 등 복합 점수**로 판정된다.
- SIDEWAYS는 **regime_score 41~60** 구간이다. 즉:
  - 20일 수익률이 -1%~+1% 근처(12.5점)이거나
  - MA가 MIXED(10점)이거나
  - 양봉 비율이 0.45~0.55대(7.5~11점)이면
  상대적으로 점수가 61 미만으로 나와 MILD_TREND_UP이 아닌 SIDEWAYS로 나올 수 있다.
- 히스테리시스 때문에 “상승 전환”은 3일 연속 조건을 만족해야 하므로, 단기 강세만으로는 MILD_TREND_UP/STRONG_TREND_UP으로 바로 전환되지 않을 수 있다.

**결론:** 코스피 5,900대에서 SIDEWAYS로 판정되는 것은 현재 산식(20일 수익률·MA·양봉비율·외국인·VKOSPI 등)과 점수 구간(41~60→SIDEWAYS)의 결과이며, 임계값·가중치 변경은 CEO 승인 후 `regime_detector.py` 등 핵심 파일 수정으로 진행하는 것이 적절하다.

---

## 5. 수행 항목 체크리스트

- [x] market_type 컬럼 추가 완료
- [x] 코스피 과거 레짐 (2025-01-01~2025-11-19) INSERT 완료 (기존 백필·신규 스크립트로 구간 반영)
- [x] 코스닥 전체 레짐 (2025-01-01~2026-02-23) INSERT 완료
- [x] 레짐 분포 검증 (양 시장)
- [x] 레짐 판정 이슈 문서화
- [x] DB-SCHEMA.md 업데이트
- [ ] 코드 레포 커밋 완료
- [ ] project-docs 보고서 push 완료 (GitHub raw URL 200)

---

## 6. 참고

- 백필 스크립트: `scripts/analysis/backfill_regime_data.py` (기존 `scripts/backfill_regime_history.py` 호출)
- index_daily: 코스피 0001, 코스닥 1001 사용 (regime_detector 및 백필과 동일)
- DB 백업: `/tmp/backup_REGIME_BACKFILL_20260224_121358.dump`
