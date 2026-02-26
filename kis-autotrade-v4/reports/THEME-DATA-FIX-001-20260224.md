# THEME-DATA-FIX-001 — 테마/업종 데이터 수집 정상화

**작업 ID:** THEME-DATA-FIX-001  
**일시:** 2026-02-24 KST  
**우선순위:** P2  
**자체승인:** O (CEO "모든 데이터 무조건 수집·저장·활용" 지시)  
**참조:** DATA-PIPELINE-AUDIT-001 §4 미수집 데이터, kis-v41-rules.md  

---

## 1. 배경 (DATA-PIPELINE-AUDIT-001에서 0행 확인)

- **v4_theme_master**, **v4_theme_stock**, **v4_theme_daily**, **v4_theme_activity_daily** 전부 0행으로 확인됨.
- 테마 수집이 스케줄에 포함되어 있더라도 실제 적재가 되지 않았거나 API/설정 이슈 가능성 식별.

---

## 2. 수집 코드 분석 (collector_theme_sector.py)

### 2.1 구조

- **파일:** `backend/app/services/data_pipeline/collector_theme_sector.py`
- **역할:** 테마 리스트 + 업종(섹터) 일별 성과 수집.
- **주요 함수:**
  - `collect_themes(client)` → KIS 테마 리스트 API 호출, **v4_theme_master** 에만 INSERT.
  - `collect_sector_daily(client, days)` → KIS 업종 일봉 API 호출, **v4_sector_daily** INSERT 및 5일/20일 수익률·순위 계산.

### 2.2 KIS API 사용처

| 용도       | 경로                                                                 | tr_id          | 비고                    |
|------------|----------------------------------------------------------------------|----------------|-------------------------|
| 테마 리스트 | `/uapi/domestic-stock/v1/quotations/inquire-theme-list`             | FHPTJ04620000  | **현재 404 반환**       |
| 업종 일봉  | `/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice`   | FHKUP03500100  | 정상 동작 (200 OK)      |

### 2.3 테마 관련 테이블과 코드 매핑

| 테이블                    | INSERT 구현 위치                    | 비고 |
|---------------------------|-------------------------------------|------|
| v4_theme_master           | collector_theme_sector.collect_themes | 테마 API 404로 0건 |
| v4_theme_stock            | **없음**                            | 코드베이스에 INSERT 미구현 |
| v4_theme_daily            | **없음**                            | 코드베이스에 INSERT 미구현 |
| v4_theme_activity_daily   | **없음**                            | 코드베이스에 INSERT 미구현 |

- `run_daily_collection.py --theme` 은 `collect_themes(client)` 만 호출하며, 위 4개 테이블 중 **v4_theme_master** 만 채우는 구조임.
- v4_theme_stock, v4_theme_daily, v4_theme_activity_daily 는 **수집 로직이 없음** (추가 개발 필요).

---

## 3. 수집 실행 결과

### 3.1 테마 수집 (run_daily_collection.py --theme)

- **결과:** **실패** (themes: 0, errors: 1).
- **원인:** KIS API `GET /uapi/domestic-stock/v1/quotations/inquire-theme-list` 호출 시 **HTTP 404 Not Found**.
- **로그:**  
  `API error: rt_cd=-1 msg_cd= msg1=HTTP 404 non-JSON`  
  `Theme list API returned: HTTP 404 non-JSON`
- **USE_KIS_CONFIG=1** 재시도 동일 결과 (404 유지) → 인증 이슈가 아니라 **엔드포인트 비지원/경로 변경** 가능성.

### 3.2 업종 일봉 수집 (run_daily_collection.py --sector)

- **결과:** **성공.**
- **통계:** sectors: 30, rows: 348, errors: 0.
- **테이블:** v4_sector_daily (기존 포함 **14,754행** 유지·갱신).

### 3.3 v4_sector_price 수집 (sector_price_collector.run_sector_price_collect)

- **결과:** **실패** (ok: 0, fail: 3).
- **원인:** `backend/app/services/data/sector_price_collector.py` 는 **KIS_ACCESS_TOKEN, KIS_APP_KEY, KIS_APP_SECRET** 등 **.env 변수**만 사용.  
  일일 수집 파이프라인(run_daily_collection / kis_configs·token_manager)과 **토큰 소스 불일치**.  
  .env에 KIS_ACCESS_TOKEN 미설정 시 호출 실패.
- **테이블:** v4_sector_price **0행** 유지.

---

## 4. 디버깅 내역

- 테마: 404 → KIS 개발자 포털/문서에서 **테마 API 경로·tr_id** 재확인 필요 (예: FHPST01710000, FHPST01720000 등 대체 API 여부).
- v4_sector_price: token_manager/kis_configs 기반 토큰을 사용하도록 `sector_price_collector` 수정 또는 .env에 실전 토큰 설정 후 스케줄에서 호출 필요.

---

## 5. 스케줄 등록 상태

- **daily_scheduler (07:50 전일 수집):**  
  `collect_rankings`, `collect_sector_daily`, `collect_investor_daily` 만 호출.  
  **collect_themes 미호출** → 테마 수집이 일일 스케줄에 **미포함**.
- **장후 수집 (15:40):** `collect_sector_daily`, `collect_investor_daily` 만 호출. 테마 미포함.
- **phase2_data_scheduler:** `run_sector_price_collect` 호출 (v4_sector_price). 토큰 미설정 시 실패.
- **phase3_data_scheduler:** 17:00 전후 `theme_detail_collector` 호출 (v4_theme_detail). v4_theme_master가 비어 있으면 테마 코드 없어 효과 없음.

---

## 6. 잔여 작업 (권장)

1. **테마 API**
   - KIS OpenAPI 문서/포털에서 **테마 리스트·테마별 종목** 실제 제공 경로·tr_id 확인.
   - 404 해소 후 `collect_themes` 재실행으로 **v4_theme_master** 적재.
   - 필요 시 **v4_theme_stock**, **v4_theme_daily**, **v4_theme_activity_daily** 수집 로직 신규 구현 (FHPST01710000 등 활용 검토).

2. **일일 스케줄**
   - 테마 API 복구 후 **daily_scheduler** 07:50(또는 장후)에 `collect_themes` 호출 추가 권장.

3. **v4_sector_price**
   - **옵션 A:** sector_price_collector를 token_manager/kis_configs 기반으로 변경.  
   - **옵션 B:** .env에 KIS_ACCESS_TOKEN(실전) 설정 후 phase2 스케줄 유지.  
   - 수집 성공 시 v4_sector_price 행 수·일자 확인 및 모니터링.

4. **히스토리 백필**
   - 테마 API 정상화 후 v4_theme_master 등 **과거 구간 백필** 필요 시 별도 스크립트/옵션 검토.

---

## 7. 최종 테이블 현황 (2026-02-24 수집 후)

| 테이블                   | 행 수   | 비고 |
|--------------------------|--------|------|
| v4_theme_master         | 0      | 테마 API 404 |
| v4_theme_stock          | 0      | INSERT 미구현 |
| v4_theme_daily          | 0      | INSERT 미구현 |
| v4_theme_activity_daily | 0      | INSERT 미구현 |
| v4_sector_daily         | 14,754 | 정상 수집 |
| v4_sector_price         | 0      | 토큰 미설정으로 수집 실패 |

---

**보고서 작성:** 2026-02-24  
**다음 단계:** KIS 테마 API 문서 확인, 테마 스케줄 추가, v4_sector_price 토큰 연동 또는 .env 설정.
