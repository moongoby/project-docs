# 관리자 페이지 데이터 수집 현황 반영 기획 보고

**작성일**: 2026-02-24  
**목적**: 데이터 수집 현황 페이지를 관리자 페이지에 반영하기 위한 기획 및 기술 지침

---

## 1. 현황 정리

### 1.1 관리자 페이지 구조 (현재)

| 구분 | 경로 | 탭 구성 | 비고 |
|------|------|---------|------|
| 관리자 | `/admin` | 사용자, 계좌, **시스템**, LLM 비용, 로그 | PREMIUM 전용, 5탭 |

- **데이터 수집 현황** 전용 탭은 없음.
- 시스템 탭: `SystemTab` → 서버/헬스/Rate Limiter/매수 차단 등.

### 1.2 데이터 수집 현황 제공처 (현재)

| 위치 | API | 표시 항목 |
|------|-----|-----------|
| **모니터링** (`/monitoring`) | `GET /api/v1/monitoring/data-collection` | 오늘 일봉(종목 수), 오늘 분봉(건수), 유니버스 활성 종목, 일봉 최종 수집일, 분봉 최종 수집 시각 |

- 백엔드: `backend/app/services/monitoring/system_monitor.py` → `get_data_collection_status()`
- 반환 필드: `ohlcv_daily_today`, `v4_ohlcv_minute_today`, `stock_universe_active`, `ohlcv_daily_latest_date`, `v4_ohlcv_minute_latest_ts` (및 `error`)

### 1.3 확장 수집 현황 (리포트 기준)

`report/DATA-COLLECTION-STATUS-REPORT-20260224.md` 기준으로 **전체 데이터 수집 현황**에 포함되는 항목:

| 데이터 종류 | 테이블/대상 | 현황 표시 시 필요한 정보 |
|-------------|-------------|---------------------------|
| 일봉 | ohlcv_daily | 오늘 종목 수, 최신 일자 |
| 분봉 | v4_ohlcv_minute | 오늘 건수, 최신 시각 |
| 종목별 수급 | v4_investor_daily | 최신 일자, (선택) 건수 |
| 시장 수급 | v4_market_investor_daily | 최신 일자 |
| 지수 일봉 | index_daily | 최신 일자 |
| 시장 레짐 | v4_market_regime_daily | 최신 일자 |
| 섹터 일봉 | v4_sector_daily | 최신 일자 |
| 순위 | v4_market_ranking | 최신 일자 |
| 호가 실시간 | v4_orderbook_realtime | 행 수 / 최신 시각 |
| 유니버스 | stock_universe | 활성 종목 수 |

관리자 페이지에 반영 시 **위 표와 같은 수준의 “전체 수집 현황”**을 한 화면에서 보는 것이 목표로 두는 것이 적절함.

---

## 2. 기획 방향

### 2.1 목표

- 관리자 페이지에 **데이터 수집 현황**을 하나의 탭으로 추가하여, PREMIUM 사용자가 **사용자/계좌/시스템/LLM/로그**와 함께 **수집 현황**을 바로 확인할 수 있도록 한다.
- 선택적으로: 모니터링 페이지에 있는 “요약 카드”와 동일한 내용을 관리자에서도 보여주거나, 관리자 전용으로 **확장된 수집 현황(위 표 전체)**을 제공한다.

### 2.2 제약·전제

- 기존 **모니터링 API**는 로그인 사용자(`get_current_user`)로 호출 가능. 관리자 전용 API를 새로 두거나, 기존 모니터링 API를 재사용할 수 있음.
- 관리자 페이지는 이미 **PREMIUM 전용**이므로, “데이터 수집” 탭도 동일 권한으로 접근.
- 데이터 수집 현황용 **백엔드**는 읽기 전용·기존 DB만 조회하여 무결점 유지.

---

## 3. 구현 옵션

### 옵션 A: 최소 반영 (기존 API·UI 재사용)

- **내용**: 관리자에 **“데이터 수집”** 탭 1개 추가. 해당 탭에서는 **기존** `GET /api/v1/monitoring/data-collection` 호출 후, 모니터링 페이지와 동일한 형태의 테이블(오늘 일봉/분봉, 유니버스, 일봉·분봉 최종 수집일·시각)만 표시.
- **프론트**
  - `admin/page.tsx`: 탭 목록에 **“데이터 수집”** 추가, `TabsList`를 5→6 탭으로 변경.
  - `DataCollectionTab.tsx` 신규: `getDataCollectionStatus()` 호출 후 `DataCollectionTable`과 동일한 테이블 렌더링.  
    - 공통화: 모니터링의 `DataCollectionTable`을 `@/components/admin/DataCollectionTable.tsx` 등으로 분리해 모니터링·관리자 둘 다에서 import 하거나, 관리자 전용으로 같은 API를 쓰는 작은 컴포넌트를 만든다.
- **백엔드**: 변경 없음.
- **장점**: 구현 빠름, 기존 API/로직 재사용.  
- **단점**: 관리자에서 보는 항목은 현재 5개 수준으로 제한됨.

### 옵션 B: 확장 반영 (전체 수집 현황 테이블)

- **내용**: “데이터 수집 현황”을 **리포트에 나온 전체 데이터 종류**까지 확장하여, 관리자 탭에서 **테이블별 최신 일자/건수·상태(정상·지연·미수집)** 를 한 화면에 표시.
- **백엔드**
  - `get_data_collection_status()` 확장 또는 `get_data_collection_status_full()` 같은 새 함수 추가.
  - 조회 대상:  
    `ohlcv_daily`, `v4_ohlcv_minute`, `v4_investor_daily`, `v4_market_investor_daily`, `index_daily`, `v4_market_regime_daily`, `v4_sector_daily`, `v4_market_ranking`, `v4_orderbook_realtime`, `stock_universe`  
  - 각 테이블에 대해 (존재 시) `COUNT(*)` 또는 적절한 집계, `MAX(date)`/`MAX(ts)` 등으로 “최신 일자/시각” 반환.  
  - 응답 스키마에 `items: [{ name, table, row_count, latest_date, status }]` 형태로 정리하면 프론트에서 테이블로 쓰기 좋음.  
  - **상태 판단**: “오늘/어제” 기준으로 정상, N일 지연이면 지연, 데이터 없으면 미수집 등 간단 규칙을 백엔드 또는 프론트에서 적용.
- **API**
  - 기존: `GET /api/v1/monitoring/data-collection` → 확장된 JSON 반환하도록 변경하거나,
  - 관리자 전용: `GET /api/v4/admin/data-collection-status` (또는 `GET /api/v1/admin/data-collection`) 를 추가하고, 여기서만 확장 응답을 내려주고 모니터링은 기존 필드만 유지.
- **프론트**
  - 관리자 **“데이터 수집”** 탭: 확장 API 호출 후, 테이블 형태로 “데이터 종류, 테이블명, 행 수, 최신 일자, 상태” 컬럼을 표시.  
  - 상태는 뱃지(정상/지연/미수집)로 표시.
- **장점**: 관리자가 한 화면에서 전체 파이프라인 상태를 점검 가능.  
- **단점**: 백엔드 확장 + 테이블/날짜 형식 통일 등 작업량 증가.

### 옵션 C: 혼합 (1단계 + 2단계)

- **1단계**: 옵션 A 적용 — 관리자에 “데이터 수집” 탭 추가, 기존 모니터링 API·동일 UI로 “요약”만 노출.
- **2단계**: 옵션 B 적용 — 백엔드 확장 + 관리자 전용/확장 API 추가 후, 같은 탭을 “전체 수집 현황” 테이블로 교체 또는 탭 내 상단 요약 + 하단 상세 테이블로 구성.

---

## 4. 권장안

- **단기**: **옵션 A**로 관리자 페이지에 “데이터 수집” 탭을 빠르게 반영하고, 기존 모니터링 데이터 수집 카드와 동일한 내용을 노출.
- **중기**: **옵션 B**를 적용해 “전체 수집 현황” API·UI를 추가하고, 관리자 “데이터 수집” 탭을 확장 뷰로 전환(또는 요약 + 상세 구성).

---

## 5. 기술 지침 (옵션 A 기준, 무결점 유지)

### 5.1 프론트엔드

| 파일 | 변경 내용 |
|------|-----------|
| `frontend/src/app/(protected)/admin/page.tsx` | 탭 6개로 확장. `TabsList`에 "데이터 수집" 탭 추가, `TabsContent`에 `DataCollectionTab` 렌더링. |
| `frontend/src/components/admin/DataCollectionTab.tsx` (신규) | `getDataCollectionStatus()` 호출(`@/lib/api/monitoring`), 로딩/에러 처리, 기존 모니터링과 동일한 5항목 테이블 표시. 30초 등 refetch 간격 선택 적용. |
| (선택) `frontend/src/components/monitoring/DataCollectionTable.tsx` | 모니터링 페이지의 `DataCollectionTable`을 별도 파일로 분리해 `DataCollectionTab`에서 재사용하면 중복 제거. |

- **권한**: 관리자 페이지 자체가 이미 `useAdminGuard()`로 PREMIUM만 진입하므로 별도 API 권한 체크는 기존 모니터링 API 의존으로 충분. 필요 시 나중에 `GET /api/v4/admin/data-collection-status`로 옮기면 관리자 전용으로 제한 가능.

### 5.2 백엔드

- **옵션 A**: 변경 없음. 기존 `GET /api/v1/monitoring/data-collection` 재사용.
- **옵션 B 적용 시**:  
  - `backend/app/services/monitoring/system_monitor.py`에 확장 함수 추가 시, 테이블/컬럼 존재 여부 확인 후 `COUNT`/`MAX`만 수행하여 읽기 전용 유지.  
  - 새 엔드포인트는 `get_current_admin_user` 또는 `verify_admin`로 관리자만 호출 가능하게 구성.

### 5.3 테스트

- 관리자(PREMIUM)로 로그인 후 `/admin` → “데이터 수집” 탭 선택 시, 5항목이 기존 모니터링과 동일하게 표시되는지 확인.
- 비관리자 계정으로는 `/admin` 진입 자체가 차단되므로 데이터 수집 탭 노출 여부는 관리자 플로우에서만 검증.

---

## 6. 작업 체크리스트 (옵션 A)

- [ ] `DataCollectionTab.tsx` 생성: monitoring API 호출 + 테이블 UI (또는 공통 `DataCollectionTable` 사용)
- [ ] `admin/page.tsx`: 탭 리스트 6개로 변경, "데이터 수집" 탭 및 `DataCollectionTab` 연결
- [ ] (선택) 모니터링 쪽 `DataCollectionTable` 컴포넌트 분리 후 재사용
- [ ] PREMIUM 계정으로 "데이터 수집" 탭 표시 및 데이터 로딩 확인

---

## 7. 참고

- **모니터링 데이터 수집 카드**: `frontend/src/app/(protected)/monitoring/page.tsx` — `DataCollectionTable`, `getDataCollectionStatus`.
- **데이터 수집 현황 API**: `backend/app/services/monitoring/system_monitor.py` — `get_data_collection_status()`.
- **전체 수집 현황 정의**: `report/DATA-COLLECTION-STATUS-REPORT-20260224.md`, `report/MINUTE-COLLECTION-FIX-20260224.md`.

이 기획에 따라 1차는 옵션 A로 관리자 페이지에 데이터 수집 현황 탭을 반영하고, 이후 옵션 B로 “전체 수집 현황”을 확장하는 순서를 권장한다.

---

## 8. 추가 기획 (일자별 검색·미수집 수집 버튼)

**일자별 기간 검색 표** 및 **미수집 현황 체크 후 수집 버튼으로 바로 수집** 기능은 별도 문서에서 상세 기획함.

- **문서**: [ADMIN-DATA-COLLECTION-PLAN-ADDENDUM-20260224.md](./ADMIN-DATA-COLLECTION-PLAN-ADDENDUM-20260224.md)
- **요약**:
  - **일자별 기간 검색**: `GET /api/v4/admin/data-collection/by-date?from=&to=` 로 기간 내 거래일별·데이터 종류별 건수/상태 조회 → 표 형태 UI.
  - **미수집 수집 버튼**: 미수집(missing/partial) 항목 목록에 [수집] 버튼 → `POST /api/v4/admin/data-collection/trigger` 로 해당 type·일자(또는 days) 수집 트리거. 수집은 백그라운드 실행(202 Accepted), 중복 실행 방지·rate limit 권장.
  - **실시간 현황·전체 항목·분봉/섹터/순위 확장·데이터 확인·수집·관리 종합 개선안**: [DATA-LIFECYCLE-IMPROVEMENT-PLAN-20260224.md](./DATA-LIFECYCLE-IMPROVEMENT-PLAN-20260224.md) 참고.
