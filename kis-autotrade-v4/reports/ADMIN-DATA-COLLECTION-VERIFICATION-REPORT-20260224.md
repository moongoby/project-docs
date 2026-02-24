# 관리자 데이터 수집 탭 노출 위치 및 구현 반영 확인 보고

**확인 일시**: 2026-02-24  
**목적**: 관리자 어드민용 데이터 수집 페이지(재수집 버튼 등) 노출 위치 안내 및 요약된 구현 내용의 실제 반영 여부 확인.

---

## 1. 관리자·데이터 수집 탭 노출 위치

### 1.1 관리자 페이지 진입 경로

| 경로 | 설명 |
|------|------|
| **URL 직접** | `https://go100.newtalk.kr/admin` (또는 로컬 `http://localhost:3000/admin`) |
| **사이드바** | 좌측 네비게이션 **「관리자」** (Shield 아이콘) 클릭 → `/admin` |
| **하단 네비** | `BottomNav` / `MobileTabBar` 에서 **「관리자」** 클릭 → `/admin` |
| **헤더** | 경로가 `/admin` 일 때 제목 "관리자" 표시 |

**전제**: **PREMIUM** 등급 사용자만 접근 가능. 등급이 없으면 "접근 권한 없음 / 현재 등급: 없음" 안내만 표시됨.

### 1.2 데이터 수집 탭 위치

관리자 페이지(`/admin`)에 진입한 뒤:

- **탭 순서**: 사용자 → 계좌 → 시스템 → **데이터 수집** → LLM 비용 → 로그  
- **4번째 탭**이 **「데이터 수집」** 이며, 여기에서 다음이 노출됨:
  - 기간 조회 (시작일·종료일 입력 + [조회] 버튼)
  - 미수집·부분 수집 목록 테이블 (일자, 요일, 항목, 수집/목표, 상태, 미수집 사유, **조치**)
  - **조치 컬럼**: 행마다 **[수집]** 버튼 (재수집 트리거)
  - 서비스 멈춤 시 상단 알림 + "아래 미수집 건에 대해 [수집] 버튼을 누르면 재수집이 시작됩니다." 안내

즉, **재수집 버튼**은 **관리자 → 데이터 수집 탭** 안의 테이블 **「조치」** 열에 행 단위로 노출됩니다.

---

## 2. 요약된 구현 내용 vs 실제 반영 여부

### 2.1 프론트엔드 — 반영됨

| 항목 | 상태 | 위치 |
|------|------|------|
| 관리자 페이지에 "데이터 수집" 탭 | ✅ 반영 | `frontend/src/app/(protected)/admin/page.tsx` (6탭 중 4번째) |
| DataCollectionTab (기간 조회, 미수집 목록, 사유, 수집 버튼) | ✅ 반영 | `frontend/src/components/admin/DataCollectionTab.tsx` |
| getDataCollectionMissing, triggerDataCollection API 호출 | ✅ 반영 | `frontend/src/lib/api/admin.ts` (GET missing, POST trigger) |
| service_stopped 안내, 행별 [수집] 버튼, 토스트 메시지 | ✅ 반영 | `DataCollectionTab.tsx` 내 |

### 2.2 백엔드 API — 미반영

| API | 요약 문서 | 실제 admin_router.py |
|-----|-----------|----------------------|
| GET `/api/v1/admin/data-collection/by-date?from=&to=` | 명시됨 | ❌ **없음** |
| GET `/api/v1/admin/data-collection/missing?from_date=&to_date=` | 명시됨 | ❌ **없음** |
| POST `/api/v1/admin/data-collection/trigger` (body: type, dates?, days?) | 명시됨 | ❌ **없음** |

`admin_router.py` 에는 위 data-collection 관련 라우트가 전혀 정의되어 있지 않음.  
→ 프론트에서 **조회** 시 404 등으로 실패하고, **[수집]** 클릭 시에도 **트리거 API가 없어** 재수집이 동작하지 않음.

### 2.3 백엔드 서비스 로직 — 미반영

| 항목 | 요약 문서 | 실제 system_monitor.py |
|------|-----------|------------------------|
| `_status_and_reason(collected, target, item_key)` (ok/partial/missing + reason) | 명시됨 | ❌ **없음** |
| `get_data_collection_missing_with_reasons(from_date, to_date)` | 명시됨 | ❌ **없음** |
| `get_data_collection_by_date_range(from_date, to_date)` | 명시됨 | ❌ **없음** |
| service_stopped[] (수집기 중단 안내) | 명시됨 | ❌ **없음** (get_service_status()는 있으나 missing 응답과 결합 로직 없음) |

`system_monitor.py` 에는 **get_data_collection_status()** (모니터링용 오늘 건수/최종 수집일) 만 있고,  
기간별 미수집·사유·서비스 멈춤 안내를 위한 함수는 없음.

---

## 3. 결론 및 조치 제안

- **노출 위치**:  
  - **관리자** 페이지는 **사이드바/하단 네비 「관리자」** 또는 **URL `/admin`** 으로 진입.  
  - **재수집 버튼** 등은 그 안의 **「데이터 수집」** 탭(4번째 탭) → 기간 조회 후 나오는 테이블의 **「조치」** 열에 행별 **[수집]** 버튼으로 노출됨.

- **구현 상태**:  
  - **프론트**: 관리자 탭, DataCollectionTab, 기간 조회·미수집 사유·재수집 버튼·API 호출 코드까지 **요약된 대로 반영**되어 있음.  
  - **백엔드**:  
    - **GET by-date, GET missing, POST trigger** 및  
    - **system_monitor 쪽 _status_and_reason, get_data_collection_missing_with_reasons, get_data_collection_by_date_range, service_stopped 연동**  
    은 **아직 반영되지 않음.**

- **조치**:  
  - 관리자 데이터 수집 탭에서 **실제로 조회·재수집**이 동작하려면,  
    요약 문서에 적힌 대로 **admin_router.py** 에 위 3개 엔드포인트를 추가하고,  
    **system_monitor.py** 에 기간별 미수집·사유·서비스 멈춤 로직을 구현해 연동해야 함.

---

## 4. 참고 파일

| 구분 | 파일 |
|------|------|
| 관리자 페이지·탭 | `frontend/src/app/(protected)/admin/page.tsx` |
| 데이터 수집 탭 UI | `frontend/src/components/admin/DataCollectionTab.tsx` |
| 프론트 API | `frontend/src/lib/api/admin.ts` |
| 백엔드 라우터 | `backend/app/api/v1/admin_router.py` (data-collection 라우트 없음) |
| 백엔드 모니터링 서비스 | `backend/app/services/monitoring/system_monitor.py` (missing/by-date/trigger 용 로직 없음) |
