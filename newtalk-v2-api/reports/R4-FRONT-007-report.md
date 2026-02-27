# R4-FRONT-007 위탁배송·드롭십 UI — 완료 보고서

**작업 ID**: R4-FRONT-007  
**버전**: v3.15.0  
**완료일**: 2026-02-26  
**선행**: R4-API-007 (DropshipService / ReturnService / FulfillmentService, 20 EP)

---

## 1. 개요

소매의 드롭십 주문(최종소비자 직배송), 교환·반품 대행 신청, 관리자/사입자의 풀필먼트 태스크(검품·포장·CCTV) 관리 UI를 구현했습니다.

---

## 2. 구현 요약

| 구분 | 내용 |
|------|------|
| 타입 | `frontend/src/types/fulfillment.ts` — DropshipStatus, ReturnType, ReturnStatus, ReturnReason, FulfillmentTaskType, FulfillmentTaskStatus, DropshipOrder, ReturnRequest, FulfillmentTask, FulfillmentDashboard |
| API 클라이언트 | `frontend/src/lib/fulfillment-api.ts` — 20함수 (드롭십 7 + 반품 7 + 풀필먼트 6) |
| 컴포넌트 | `frontend/src/components/fulfillment/` — 14개 + index.ts |
| 페이지 | 6개 경로 (retail/dropship, retail/dropship/[id], retail/returns, wholesale/dropship, admin/fulfillment, admin/returns) + 상세 페이지 4개 |
| 레이아웃 | retail: 드롭십(Truck), 반품·교환(RotateCcw) / wholesale: 드롭십 관리(Truck) / admin: 풀필먼트(Package), 반품·교환(RotateCcw) |

---

## 3. 파일 목록

### 타입
- `frontend/src/types/fulfillment.ts`

### API
- `frontend/src/lib/fulfillment-api.ts`

### 컴포넌트 (fulfillment/)
- `DropshipStatusBadge.tsx`
- `DropshipOrderCard.tsx`
- `DropshipOrderList.tsx`
- `DropshipOrderDetail.tsx`
- `DropshipCreateDialog.tsx`
- `ReturnStatusBadge.tsx`
- `ReturnRequestList.tsx`
- `ReturnRequestDetail.tsx`
- `ReturnCreateDialog.tsx`
- `FulfillmentTaskStatusBadge.tsx`
- `FulfillmentTaskCard.tsx`
- `FulfillmentTaskList.tsx`
- `FulfillmentTaskDetail.tsx`
- `FulfillmentDashboardWidget.tsx`
- `index.ts`

### 페이지
- `frontend/src/app/(retail)/retail/dropship/page.tsx`
- `frontend/src/app/(retail)/retail/dropship/[id]/page.tsx`
- `frontend/src/app/(retail)/retail/returns/page.tsx`
- `frontend/src/app/(retail)/retail/returns/[id]/page.tsx`
- `frontend/src/app/(wholesale)/wholesale/dropship/page.tsx`
- `frontend/src/app/(wholesale)/wholesale/dropship/[id]/page.tsx`
- `frontend/src/app/(admin)/admin/fulfillment/page.tsx`
- `frontend/src/app/(admin)/admin/fulfillment/[id]/page.tsx`
- `frontend/src/app/(admin)/admin/returns/page.tsx`
- `frontend/src/app/(admin)/admin/returns/[id]/page.tsx`

### 레이아웃
- `frontend/src/components/layout/retail-layout.tsx` — 드롭십, 반품·교환 메뉴 추가
- `frontend/src/components/layout/wholesale-layout.tsx` — 드롭십 관리 메뉴 추가
- `frontend/src/components/layout/admin-layout.tsx` — 풀필먼트, 반품·교환 메뉴 추가

### 문서
- `docs/CONTEXT.md` — 완료 항목, 다음 작업 갱신
- `docs/CHANGELOG.md` — [3.15.0] R4-FRONT-007 추가
- `docs/architecture/NT-V2-ARCHITECTURE.md` — Frontend 라우트 추가
- `docs/handover/HANDOVER.md` — 변경이력, 다음 작업 큐 갱신

---

## 4. API 함수 (20개)

| # | 함수 | 메서드 | 경로 |
|---|------|--------|------|
| 1 | createDropship | POST | /dropship |
| 2 | getDropshipList | GET | /dropship |
| 3 | getDropshipByOrder | GET | /dropship/by-order/{orderId} |
| 4 | getDropshipDetail | GET | /dropship/{id} |
| 5 | updateDropship | PUT | /dropship/{id} |
| 6 | updateDropshipStatus | PUT | /dropship/{id}/status |
| 7 | updateDropshipTracking | PUT | /dropship/{id}/tracking |
| 8 | createReturn | POST | /returns |
| 9 | getReturnList | GET | /returns |
| 10 | getReturnDetail | GET | /returns/{id} |
| 11 | approveReturn | PUT | /returns/{id}/approve |
| 12 | rejectReturn | PUT | /returns/{id}/reject |
| 13 | updateReturnStatus | PUT | /returns/{id}/status |
| 14 | updateReturnTracking | PUT | /returns/{id}/tracking |
| 15 | createFulfillmentTask | POST | /fulfillment/tasks |
| 16 | getFulfillmentTasks | GET | /fulfillment/tasks |
| 17 | getFulfillmentTask | GET | /fulfillment/tasks/{id} |
| 18 | assignFulfillmentTask | PUT | /fulfillment/tasks/{id}/assign |
| 19 | updateFulfillmentStatus | PUT | /fulfillment/tasks/{id}/status |
| 20 | getFulfillmentDashboard | GET | /fulfillment/dashboard |

---

## 5. 테스트

- Docker 5/5 Up 확인
- 백엔드 라우트: `routes/api.php` 에 dropship 7 + returns 7 + fulfillment 6 = 20 EP 등록 확인
- TypeScript: 린트 0 errors (프로젝트 기준)
- 문서: CONTEXT, CHANGELOG, HANDOVER, ARCHITECTURE 갱신 완료

---

## 6. 결론

R4-FRONT-007 위탁배송·드롭십 UI를 완료했습니다.  
컴포넌트 14개, API 함수 20개, 페이지 6개 경로(+ 상세 4개), 레이아웃 메뉴 반영 및 문서를 갱신했습니다.  
R4 라운드 프론트 작업을 마쳤으며, 다음은 R5 기획 확정 대기(일본 크로스보더, 라이브 B2B)입니다.
