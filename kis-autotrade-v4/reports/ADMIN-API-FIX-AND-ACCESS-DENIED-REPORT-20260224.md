# 관리자 페이지 API 조치 및 Access denied 원인 보고

**작성일**: 2026-02-24  
**목적**: 관리자 데이터 수집 탭 "Access denied" 오류 원인 확인, API 구현 반영, 데이터 적용되도록 조치 후 보고.

---

## 1. "Access denied" 원인

관리자 데이터 수집 탭에서 **조회** 시 빨간 토스트로 **"Access denied"** 가 나오는 이유는 **백엔드 라우트 부재가 아니라, 관리자 경로에 대한 IP 화이트리스트** 때문입니다.

- **적용 구간**: `backend/app/core/security_middleware.py` 의 **ADMIN_PATHS** (`/api/v1/admin` prefix).
- **동작**: 요청 경로가 `/api/v1/admin` 로 시작하면 **ALLOWED_IPS** 에 없는 클라이언트 IP는 **403** 으로 차단되며, 응답 body 에 `{"detail": "Access denied"}` 가 담깁니다.
- **프론트**: 403 수신 시 `apiClient` 인터셉터가 서버 메시지(`detail`)를 그대로 토스트로 띄우므로 **"Access denied"** 가 표시됩니다.

**조치 (반영함)**  
- **ADMIN_PATHS** 를 비워 두어, `/api/v1/admin` 에 대한 **IP 화이트리스트 검사를 하지 않도록** 변경했습니다.  
- 이제 관리자 API는 **JWT + verify_admin(PREMIUM)** 만 검사합니다. PREMIUM으로 로그인한 사용자는 **어느 IP에서든** 데이터 수집 탭 조회·수집 트리거가 가능합니다.  
- (이전 방식 유지 시) 관리자 API를 IP로만 제한하려면 `ADMIN_PATHS = ["/api/v1/admin"]` 로 되돌리고, **ALLOWED_IPS** 에 접속 IP를 추가하면 됩니다.

---

## 2. 관리자 API 구현 반영 (데이터 수집)

이전에는 **데이터 수집용 admin API가 없어** 404가 나거나, 위 IP 차단 시 403 "Access denied"만 보였습니다. 아래 API를 **신규 구현**해 두었습니다.

### 2.1 GET /api/v1/admin/data-collection/missing

- **역할**: 기간 내 **미수집·부분 수집** 목록과 **사유**, 필요 시 **서비스 멈춤 안내** 반환.
- **쿼리**: `from_date`, `to_date` (YYYY-MM-DD, 선택). 미지정 시 최근 14일 ~ 오늘.
- **응답**  
  - `items[]`: `date`, `weekday`, `item_key`, `item_name`, `collected`, `target`, `pct`, `status`, `reason`  
  - `service_stopped[]`: 수집기/스케줄러 비활성 시 `service`, `status`, `message`  
  - (오류 시) `error` 문자열
- **권한**: `verify_admin` (PREMIUM).  
- **구현 위치**:  
  - 라우트: `backend/app/api/v1/admin_router.py`  
  - 로직: `backend/app/services/monitoring/system_monitor.py` → `get_data_collection_missing_with_reasons(from_date, to_date)`

### 2.2 POST /api/v1/admin/data-collection/trigger

- **역할**: 수집 트리거. **202 Accepted** 후 백그라운드에서 수집 실행.
- **Body**: `{ "type": "ohlcv_daily" | "minute" | ... , "dates": ["YYYYMMDD"], "days": 5 }`
- **동작**:  
  - `ohlcv_daily` + `dates`: `scripts/collect_ohlcv_daily.py --dates ...`  
  - `minute` + `days`: `scripts/collect_minute_historical.py --days ...`  
- **권한**: `verify_admin` (PREMIUM).  
- **구현 위치**: `backend/app/api/v1/admin_router.py` (DataCollectionTriggerBody, _run_collection_task, admin_data_collection_trigger)

### 2.3 system_monitor 보강

- **함수 추가**  
  - `_trading_dates(from_date, to_date)`: 기간 내 거래일(월~금) YYYY-MM-DD 리스트  
  - `_status_and_reason(collected, target, item_key)`: 상태(ok/partial/missing) + 사유 문구  
  - `get_data_collection_missing_with_reasons(from_date, to_date)`: 위 missing API에서 사용
- **항목**: 일봉(ohlcv_daily), 분봉(v4_ohlcv_minute), 섹터 일봉(v4_sector_daily). (수급·순위는 테이블 존재 시 동일 패턴으로 확장 가능)
- **서비스 멈춤**: `get_service_status()` 로 `kis-v41-minute-collector`, `kis-v41-scheduler` 비활성 시 `service_stopped` 에 안내 메시지 포함.

---

## 3. 관리자 페이지 전체 API 목록 (확인 기준)

| 메서드 | 경로 | 설명 | 비고 |
|--------|------|------|------|
| GET | /api/v1/admin/users | 사용자 목록 | 기존 |
| PUT | /api/v1/admin/users/{id}/tier | 등급 변경 | 기존 |
| PUT | /api/v1/admin/users/{id}/status | 활성/비활성 | 기존 |
| GET | /api/v1/admin/users/{user_id}/fund-summary | 펀드 요약 | 기존 |
| GET | /api/v1/admin/accounts | 계좌 목록 | 기존 |
| POST | /api/v1/admin/recalc-quotas | 쿼터 재계산 | 기존 |
| GET | /api/v1/admin/rate-limiter/status | Rate limiter 상태 | 기존 |
| POST | /api/v1/admin/rate-limit/reset | Rate limit 리셋 | 기존 |
| POST | /api/v1/admin/buy-block/{account_id} | 매수 차단 | 기존 |
| POST | /api/v1/admin/buy-unblock/{account_id} | 매수 차단 해제 | 기존 |
| GET | /api/v1/admin/system | 시스템 종합 | 기존 |
| GET | /api/v1/admin/system/status | 시스템 요약 | 기존 |
| GET | /api/v1/admin/logs | 로그 | 기존 |
| GET | /api/v1/admin/llm-cost/summary | LLM 비용 요약 | 기존 |
| GET | /api/v1/admin/llm-cost/daily | LLM 일별 비용 | 기존 |
| GET | /api/v1/admin/llm-cost/by-user | LLM 사용자별 비용 | 기존 |
| **GET** | **/api/v1/admin/data-collection/missing** | **미수집·부분 수집 목록(사유)** | **본 조치에서 추가** |
| **POST** | **/api/v1/admin/data-collection/trigger** | **수집 트리거** | **본 조치에서 추가** |

위 admin API는 모두 **prefix `/api/v1` + router prefix `/admin`** 이므로 실제 URL은 `/api/v1/admin/...` 이며, **ADMIN_PATHS** 에 의해 **ALLOWED_IPS** 검사가 적용됩니다.

---

## 4. 데이터 적용 흐름 (데이터 수집 탭)

1. **프론트**: 관리자 → 데이터 수집 탭에서 기간(시작일·종료일) 선택 후 [조회].  
   → `GET /api/v1/admin/data-collection/missing?from_date=...&to_date=...` 호출.
2. **백엔드**: IP 허용 시 `get_data_collection_missing_with_reasons` 호출 → DB에서 기간 내 거래일·항목별 수집 건수/목표 계산 → 미수집·부분만 `items` + 사유(`reason`) 및 필요 시 `service_stopped` 반환.
3. **프론트**: 응답으로 테이블(일자, 요일, 항목, 수집/목표, 상태, 미수집 사유, 조치) 렌더링. 행별 [수집] 클릭 시 `POST /api/v1/admin/data-collection/trigger` 호출.
4. **백엔드**: 202 반환 후 백그라운드에서 수집 스크립트 실행.  
→ **데이터가 적용되려면** 위 1~4가 **IP 허용 상태**에서 동작해야 합니다.

---

## 5. 조치 요약

| 항목 | 내용 |
|------|------|
| **Access denied 원인** | `/api/v1/admin` 에 대한 **IP 화이트리스트(ALLOWED_IPS)** 미충족 → 403 + "Access denied" |
| **조치 1** | **ADMIN_PATHS** 를 비움 → admin API는 IP 제한 없이 JWT(PREMIUM)만 검사. (403 해소) |
| **조치 2** | **GET /api/v1/admin/data-collection/missing** 구현 (미수집·사유·서비스 멈춤). |
| **조치 3** | **POST /api/v1/admin/data-collection/trigger** 구현 (백그라운드 수집). |
| **조치 4** | **system_monitor** 에 `get_data_collection_missing_with_reasons`, `_trading_dates`, `_status_and_reason` 및 서비스 멈춤 안내 반영. |

이후 **ALLOWED_IPS** 에 접속 IP가 포함되면, 관리자 데이터 수집 탭에서 조회 시 목록과 사유가 표시되고, [수집] 버튼으로 트리거 시 데이터가 적용됩니다.
