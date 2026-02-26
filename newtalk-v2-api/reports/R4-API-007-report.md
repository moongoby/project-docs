# R4-API-007 위탁배송 고도화 + 드롭십 API 보고서

**작성일시**: 2026-02-26 KST  
**버전**: v3.10.0  
**커밋 접두사**: [R4-API-007]

---

## 1. 개요

- **위탁배송 고도화**: 검품·포장·CCTV 워크플로우, 풀필먼트 태스크 및 대시보드
- **드롭십 주문**: 소매 → 최종소비자 직배송 (dropship_orders)
- **교환·반품 대행**: return_requests 테이블 및 Return API

---

## 2. 완료 항목

### 2.1 마이그레이션 (3개)

| 테이블 | 파일 | 비고 |
|--------|------|------|
| dropship_orders | 2026_02_26_400001_create_dropship_orders_table.php | order_id, retail/wholesale_user_id, 최종수령인 정보, status, tracking, 가격/수익, 인덱스 3개 |
| return_requests | 2026_02_26_400002_create_return_requests_table.php | order_id, order_item_id(nullable), type/status, reason, 반품송장, 환불/교환, admin_memo, 인덱스 3개 |
| fulfillment_tasks | 2026_02_26_400003_create_fulfillment_tasks_table.php | order_id, shipment_id(nullable), assigned_to(nullable), type/status, notes, cctv_clip_url, 인덱스 2개 |

### 2.2 모델 (3개 + Shipment 1개)

- **DropshipOrder**: 상수(status), fillable, casts, 관계 order / retailUser / wholesaleUser
- **ReturnRequest**: type/status/reason 상수, fillable, casts, 관계 order / orderItem / user / exchangeProduct / exchangeOption
- **FulfillmentTask**: type/status 상수, fillable, casts, 관계 order / shipment / assignee
- **Shipment**: (기존 shipments 테이블용) FulfillmentTask 관계용 모델 추가

### 2.3 서비스 (3개)

| 서비스 | 메서드 수 | 주요 메서드 |
|--------|-----------|-------------|
| DropshipService | 5 | createDropshipOrder, updateStatus, getDropshipOrders, getDetail, calculateProfit |
| ReturnService | 6 | requestReturn, approveReturn, rejectReturn, updateReturnStatus, getReturnRequests, getReturnDetail |
| FulfillmentService | 5 | createTask, assignTask, updateTaskStatus, getTasks, getDashboard |

### 2.4 컨트롤러 + 라우트 (20 EP)

**DropshipController (7 EP)**  
- POST /api/dropship  
- GET /api/dropship  
- GET /api/dropship/by-order/{orderId}  
- GET /api/dropship/{id}  
- PUT /api/dropship/{id}  
- PUT /api/dropship/{id}/status  
- PUT /api/dropship/{id}/tracking  

**ReturnController (7 EP)**  
- POST /api/returns  
- GET /api/returns  
- GET /api/returns/{id}  
- PUT /api/returns/{id}/approve  
- PUT /api/returns/{id}/reject  
- PUT /api/returns/{id}/status  
- PUT /api/returns/{id}/tracking  

**FulfillmentController (6 EP)**  
- POST /api/fulfillment/tasks  
- GET /api/fulfillment/tasks  
- GET /api/fulfillment/tasks/{id}  
- PUT /api/fulfillment/tasks/{id}/assign  
- PUT /api/fulfillment/tasks/{id}/status  
- GET /api/fulfillment/dashboard  

**권한**  
- 드롭십/반품: `role:retail|wholesale|admin`  
- 풀필먼트: `role:admin|purchaser`  

---

## 3. 파일 목록

- database/migrations: 2026_02_26_400001~400003
- app/Models: DropshipOrder, ReturnRequest, FulfillmentTask, Shipment
- app/Services: DropshipService, ReturnService, FulfillmentService
- app/Http/Controllers/Api: DropshipController, ReturnController, FulfillmentController
- routes/api.php: R4-API-007 라우트 그룹 3개 추가

---

## 4. 비고

- 사방넷 연동은 스펙상 스텁으로 두었으며, 추후 실제 API 연동 시 FulfillmentService/외부 서비스 확장 예정.
- 드롭십 상태: pending → confirmed → preparing → shipped → delivered / cancelled / returned.
- 교환·반품 상태: requested → approved → collecting → collected → inspecting → completed / rejected.
