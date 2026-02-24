# 관리자 데이터 수집 현황 — 추가 기획 (일자별 기간 검색·미수집 수집 버튼)

**작성일**: 2026-02-24  
**관련 문서**: [ADMIN-DATA-COLLECTION-PLAN-20260224.md](./ADMIN-DATA-COLLECTION-PLAN-20260224.md)  
**목적**: 일자별 기간 검색 표 형태 조회, 미수집 현황 체크 및 수집 버튼으로 즉시 수집 기능 추가 기획

---

## 1. 추가 요구사항 요약

| 구분 | 요구 내용 | 기대 효과 |
|------|-----------|-----------|
| **일자별 기간 검색** | 기간(from~to)을 지정하면 **일자별·데이터 종류별** 수집 현황을 **표 형태**로 확인 | 특정 기간(예: 최근 2주) 구간의 수집 누락/지연을 한눈에 점검 |
| **미수집 수집 버튼** | 미수집된 항목을 체크하고 **수집 버튼** 클릭 시 해당 항목만 **바로 수집** 실행 | 스케줄 실패·누락 시 관리자가 수동으로 보강 수집 가능 |

---

## 2. 일자별 기간 검색 표

### 2.1 UI 구성

- **기간 입력**: 시작일(from), 종료일(to) — 날짜 선택기(DatePicker). 기본값 예: 최근 14일(오늘 기준).
- **조회 버튼**: 클릭 시 기간 내 **일자별 수집 현황** API 호출 후 표 갱신.
- **표 형태**:
  - **행**: 기간 내 각 거래일(월~금만 또는 휴장일 제외 옵션).
  - **열**: 데이터 종류별 (일봉, 분봉, 수급, 시장수급, 지수, 섹터, 순위 등 — 1차는 일봉·분봉·수급 위주로 단계 적용 가능).
  - **셀 값**: 해당 일자·해당 데이터의 **건수(또는 종목 수)** 및 **상태 뱃지**(정상/부분/미수집).
- **정렬**: 일자 내림차순(최신이 위) 기본.

### 2.2 API 설계

**엔드포인트 (관리자 전용)**

```
GET /api/v4/admin/data-collection/by-date?from=2026-02-01&to=2026-02-24
```

또는 v1 admin 경로:

```
GET /api/v1/admin/data-collection/by-date?from=2026-02-01&to=2026-02-24
```

**권한**: `get_current_admin_user` 또는 `verify_admin` (PREMIUM).

**쿼리 파라미터**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| from | string (YYYY-MM-DD) | O | 기간 시작일 |
| to | string (YYYY-MM-DD) | O | 기간 종료일 |
| exclude_weekends | bool | X | true 시 토·일 제외 (기본 true 권장) |

**응답 예시**

```json
{
  "from": "2026-02-01",
  "to": "2026-02-24",
  "dates": ["2026-02-24", "2026-02-23", "2026-02-20", "..."],
  "rows": [
    {
      "date": "2026-02-24",
      "weekday": "화",
      "ohlcv_daily": { "count": 0, "status": "missing", "expected_min": 3000 },
      "v4_ohlcv_minute": { "count": 0, "status": "missing", "expected_min": 50000 },
      "v4_investor_daily": { "count": 0, "status": "missing" }
    },
    {
      "date": "2026-02-23",
      "weekday": "월",
      "ohlcv_daily": { "count": 3844, "status": "ok" },
      "v4_ohlcv_minute": { "count": 67695, "status": "partial", "expected_min": 150000 },
      "v4_investor_daily": { "count": 0, "status": "missing" }
    }
  ]
}
```

- **status**: `ok`(정상), `partial`(일부만 수집), `missing`(미수집).  
- **expected_min**: “정상”으로 보기 위한 최소 건수(선택). 테이블별로 기준값을 백엔드에 두고, 그 미만이면 partial/missing 판단.

### 2.3 백엔드 구현 포인트

- **파일**: `backend/app/services/monitoring/system_monitor.py` 또는 전용 서비스 모듈에 함수 추가.  
  - 예: `get_data_collection_by_date_range(from_date: date, to_date: date) -> dict`.
- **로직 요약**:
  1. from~to 사이의 **거래일 목록** 생성 (토·일 제외 옵션 적용).
  2. 테이블별로 **일자 컬럼**에 대해 집계:
     - `ohlcv_daily`: `date` (또는 to_char 일치) → `GROUP BY date`, `COUNT(DISTINCT stock_code)`.
     - `v4_ohlcv_minute`: `trade_date` → `GROUP BY trade_date`, `COUNT(*)`.
     - `v4_investor_daily`: 일자 컬럼(스키마 확인) → `GROUP BY date`, `COUNT(*)` 또는 종목 수.
  3. 거래일 목록과 집계 결과를 매칭하여, 날짜별·테이블별 `count`, `status` 계산 후 반환.
- **성능**: 기간이 길면(예: 60일) 쿼리 부담이 있을 수 있으므로, **최대 90일** 등 상한 두고, 필요 시 페이지네이션(또는 “최근 N일” 고정) 권장.

### 2.4 프론트엔드

- **데이터 수집 탭** 내 상단 또는 별도 섹션에 “일자별 현황” 블록 추가.
- 기간 선택 + [조회] → `GET .../by-date?from=&to=` 호출 후 테이블 컴포넌트에 `rows` 바인딩.
- 테이블: `date` | `ohlcv_daily`(건수/상태) | `v4_ohlcv_minute`(건수/상태) | … 컬럼 구성.
- **일자별·항목별 수집률(전체 대상 대비)** 및 화면 구성 상세: [ADMIN-DATA-COLLECTION-SCREEN-BY-DATE-20260224.md](./ADMIN-DATA-COLLECTION-SCREEN-BY-DATE-20260224.md) 참고.

---

## 3. 미수집 현황 체크 및 수집 버튼

### 3.1 “미수집” 정의

- **일자별 기간 조회 결과** 또는 **최근 N일 요약**에서:
  - `status === "missing"` 또는 `status === "partial"` 인 (데이터 종류, 일자) 조합을 “미수집(또는 보강 대상)”으로 간주.
- 관리자 화면에서는 이들을 **목록**으로 보여주고, 항목별(또는 그룹별) **수집 버튼**을 제공.

### 3.2 UI 구성

- **미수집 목록**:
  - “일자별 현황” 조회 결과에서 status가 missing/partial인 셀을 모아,  
    예: `[일봉 2026-02-23] [수집]`, `[분봉 2026-02-20] [수집]`, `[수급 2026-02-23] [수집]` 형태로 표시.
  - 또는 표에서 행/열 단위로 “이 일자 수집” 버튼을 두는 방식 가능.
- **수집 버튼 동작**:
  - 클릭 시 해당 **데이터 종류 + 일자(또는 기간)**에 대해 **수집 트리거 API** 호출.
  - 수집은 **비동기(백그라운드)** 실행 권장 → API는 즉시 202 Accepted + job_id 등 반환, 클라이언트는 “수집 중” 표시 후 일정 시간 뒤 “일자별 현황” 재조회로 결과 확인.

### 3.3 수집 트리거 API 설계

**엔드포인트 (관리자 전용)**

```
POST /api/v4/admin/data-collection/trigger
```

**권한**: `get_current_admin_user` 또는 `verify_admin`.

**요청 Body 예시**

```json
{
  "type": "ohlcv_daily",
  "dates": ["20260223", "20260224"]
}
```

또는

```json
{
  "type": "minute",
  "days": 5
}
```

```json
{
  "type": "investor",
  "days": 3
}
```

**type 값과 실행 방식 정리**

| type | 설명 | 백엔드 실행 방식 | 비고 |
|------|------|-------------------|------|
| ohlcv_daily | 일봉 | subprocess: `scripts/collect_ohlcv_daily.py --dates 20260223,20260224` (또는 backend 스크립트 동일 CLI) | 기존 스크립트와 동일 인자 |
| minute | 분봉 | subprocess: `python -m backend.app.services.data_pipeline.collector_minute --days N` | 장시간 실행 → 반드시 백그라운드 |
| investor | 수급 | in-process 호출 또는 subprocess: `python -m backend.app.services.data_pipeline.run_daily_collection --investor --days N` | KIS 토큰 필요 |
| sector | 섹터 | run_daily_collection --sector --days N | 동일 |
| ranking | 순위 | run_daily_collection --ranking | 일자 개념 없을 수 있음 |

- **일봉**: 기존처럼 `--dates` 쉼표 구분 일자 전달.
- **분봉**: `--days N`으로 최근 N거래일 이어하기(resume) 실행.
- **수급/섹터/순위**: `run_daily_collection`의 `--days`로 보강 일수 지정.

### 3.4 백엔드 구현 포인트

- **새 라우터/엔드포인트**:  
  - `backend/app/routers/v4_admin.py` 또는 `backend/app/api/v1/admin_router.py`에  
    `POST /api/v4/admin/data-collection/trigger` (또는 v1 경로) 추가.
- **검증**:
  - `type` 화이트리스트 허용: `ohlcv_daily`, `minute`, `investor`, `sector`, `ranking` 등.
  - `dates`는 YYYYMMDD 리스트, 최대 개수 제한(예: 31일).
  - `days`는 1~30 등 상한.
- **실행 방식**:
  - **비동기 실행**: FastAPI `BackgroundTasks`에 수집 작업 넣기.  
    - 응답은 즉시 `202 Accepted` + `{ "job_id": "...", "message": "수집이 백그라운드에서 시작되었습니다." }`.
  - 실제 실행: `asyncio.create_subprocess_exec`로 위 표의 스크립트/모듈 호출.  
    - 작업 디렉터리·환경변수(PYTHONPATH, DB_*)는 기존 크론/스케줄러와 동일하게 설정.
- **안전장치**:
  - 동일 type에 대해 **중복 실행 방지**: 이미 해당 type으로 수집이 진행 중이면 409 Conflict 또는 “이미 수집 중” 메시지 반환.
  - (선택) **Rate limit**: type당 5분에 1회 등 제한.
  - (선택) **dry_run**: body에 `"dry_run": true`면 실제 subprocess 없이 허용될 인자만 검증 후 반환.

### 3.5 프론트엔드

- **미수집 목록**:
  - 일자별 현황 API 응답에서 `status !== "ok"` 인 항목을 리스트로 만들어, 각 항목에 [수집] 버튼 부여.
- **수집 버튼 클릭**:
  - `POST .../trigger` 호출 시 body에 `{ type, dates }` 또는 `{ type, days }` 전달.
  - 202 수신 시 토스트/배너로 “수집이 시작되었습니다. 완료 후 현황을 다시 조회해 주세요.” 표시.
  - (선택) job_id로 주기적 폴링하여 “수집 완료” 상태 표시.
- **재조회**: “일자별 현황” [조회] 버튼 또는 일정 간격 자동 재조회로 수집 결과 반영.

---

## 4. 데이터 종류별 일자 컬럼·실행 스크립트 정리 (분봉·섹터·순위 포함)

**확장 범위**: 일자별 표와 수집 트리거 모두 **분봉·섹터·순위**를 1차 스코프에 포함한다. 실시간 현황·전체 개선안은 [DATA-LIFECYCLE-IMPROVEMENT-PLAN-20260224.md](./DATA-LIFECYCLE-IMPROVEMENT-PLAN-20260224.md) 참고.

| 데이터 종류 | 테이블 | 일자 컬럼 | 일자별 집계 쿼리 | 수집 트리거 (실제 호출) |
|-------------|--------|-----------|------------------|--------------------------|
| 일봉 | ohlcv_daily | date | GROUP BY date, COUNT(DISTINCT stock_code) | scripts/collect_ohlcv_daily.py --dates YYYYMMDD,... |
| 분봉 | v4_ohlcv_minute | trade_date | GROUP BY trade_date, COUNT(*) | collector_minute --days N |
| 수급 | v4_investor_daily | (스키마 확인) | GROUP BY 해당 date 컬럼 | run_daily_collection --investor --days N |
| 시장 수급 | v4_market_investor_daily | date | GROUP BY date | collect_market_investor.py (스크립트 확인) |
| 섹터 | v4_sector_daily | date | GROUP BY date | run_daily_collection --sector --days N |
| 순위 | v4_market_ranking | (스키마 확인) | 최신 1건 또는 date | run_daily_collection --ranking |

- 일자별 표 1차 단계에서는 **일봉·분봉·수급** 위주로 구현하고, 이후 시장 수급·섹터·순위를 열로 확장하는 단계 적용을 권장.

---

## 5. 구현 단계 제안

| 단계 | 내용 | 산출물 |
|------|------|--------|
| 1 | 일자별 기간 조회 API (일봉·분봉·수급) | GET .../by-date, 서비스 함수, 응답 스키마 |
| 2 | 데이터 수집 탭에 “일자별 현황” 블록 (기간 선택 + 표) | DataCollectionByDateTable 컴포넌트, API 연동 |
| 3 | 미수집 항목 목록 표시 (일자별 결과에서 도출) | 미수집 목록 UI |
| 4 | 수집 트리거 API (ohlcv_daily, investor 우선) | POST .../trigger, BackgroundTasks, subprocess 호출 |
| 5 | 수집 버튼 + 202 처리 + 재조회 유도 | [수집] 버튼, 토스트, 재조회 |
| 6 | **분봉·섹터·순위** 트리거 및 일자별 표 열 확장 | type에 minute/sector/ranking 포함, by-date 응답에 v4_sector_daily, v4_market_ranking 등 컬럼 추가 (필수) |

---

## 6. 위험·주의사항

- **분봉 수집**은 수십 분 이상 걸릴 수 있으므로 반드시 **백그라운드** 실행. 타임아웃이 있는 HTTP에서 동기 실행 금지.
- **KIS API 한도·토큰**: 수집 트리거가 동시에 다수 호출되면 API 한도 초과 가능. “동일 type 중복 실행 방지”와 type별 rate limit으로 완화.
- **실행 환경**: subprocess는 **백엔드 프로세스가 기동 중인 서버 환경**과 동일한 PYTHONPATH·DB·.env를 사용해야 함. 배포 경로(`/root/kis-autotrade-v4` 등)는 설정값으로 두고 코드에 하드코딩 최소화.
- **보안**: 트리거 API는 **관리자 전용**. 엔드포인트에 `get_current_admin_user`(또는 verify_admin) 필수 적용.

---

## 7. 참고 코드 위치

- 일봉 수집 (스크립트): `scripts/collect_ohlcv_daily.py` (--dates), `backend/scripts/collect_ohlcv_daily.py`
- 분봉 수집: `backend/app/services/data_pipeline/collector_minute.py` (--days)
- 수급/섹터/순위: `backend/app/services/data_pipeline/run_daily_collection.py` (--investor, --sector, --ranking, --days)
- 스케줄러에서 subprocess 예: `backend/app/services/scheduler/daily_scheduler.py` (`_collect_ohlcv_daily`, minute collector start/stop)
- 백엔드 관리자 라우터: `backend/app/routers/v4_admin.py`, `backend/app/api/v1/admin_router.py`

이 추가 기획에 따라 기존 [ADMIN-DATA-COLLECTION-PLAN-20260224.md](./ADMIN-DATA-COLLECTION-PLAN-20260224.md)의 “데이터 수집” 탭을 **일자별 기간 검색 표** + **미수집 현황 및 수집 버튼**까지 포함하도록 확장할 수 있다.

- **실시간 수집 현황**(전체 항목·당일 숫자 변동)·**분봉·섹터·순위 확장**·**데이터 확인·수집·관리 종합 개선안**은 [DATA-LIFECYCLE-IMPROVEMENT-PLAN-20260224.md](./DATA-LIFECYCLE-IMPROVEMENT-PLAN-20260224.md) 에 정리되어 있다.
