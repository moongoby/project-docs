# R3-API-003 작업 보고서

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | R3-API-003 |
| 작업명 | 배송 API (위탁배송 + 배송추적 + 배송지관리) |
| 완료일 | 2026-02-25 KST |
| 버전 | v2.5.0 |
| 커밋 SHA | (서버 main 푸시 후 `git log --oneline -1` 결과 7자리 기입) |
| 상태 | 완료 |

## 엔드포인트 목록 (11개)

### 배송 (6개)
| 메서드 | 경로 | 설명 | 권한 |
|--------|------|------|------|
| POST | /api/orders/{orderId}/shipment | 배송 생성 | seller, admin |
| GET | /api/orders/{orderId}/shipment | 주문의 배송 조회 | buyer, seller, admin |
| GET | /api/shipments/{id} | 배송 상세 (with logs, order) | buyer, seller, admin |
| PUT | /api/shipments/{id}/tracking | 송장 등록/수정 | seller, admin |
| PUT | /api/shipments/{id}/status | 배송 상태 변경 | seller, admin |
| GET | /api/shipments/{id}/tracking | 배송 추적 (tracking_url + logs) | buyer, seller, admin |

### 배송지 (5개)
| 메서드 | 경로 | 설명 | 권한 |
|--------|------|------|------|
| GET | /api/shipping-addresses | 내 배송지 목록 | auth |
| POST | /api/shipping-addresses | 배송지 추가 | auth |
| PUT | /api/shipping-addresses/{id} | 배송지 수정 | 소유자 |
| DELETE | /api/shipping-addresses/{id} | 배송지 삭제 | 소유자 |
| PUT | /api/shipping-addresses/{id}/default | 기본 배송지 설정 | 소유자 |

## DB 스키마 (3개 테이블)

### shipments (기존 테이블 alter)
- R3-API-003에서 추가: seller_id, buyer_id, type(direct/consignment), tracking_company, tracking_url, sender_*, receiver_*, returned_at, estimated_delivery, weight, note, softDeletes, index(order_id, status), index(tracking_company, tracking_number)
- 기존 carrier → tracking_company 이전 후 carrier 제거

### shipment_logs (신규)
- id, shipment_id (FK cascadeDelete), status, location, description, logged_at, timestamps, index(shipment_id, logged_at)

### shipping_addresses (신규)
- id, user_id (FK), label, name, phone, postal_code, address, address_detail, is_default, timestamps, softDeletes, index(user_id, is_default)

## 신규/수정 파일
- database/migrations/2026_02_25_170001_alter_shipments_table_for_r3_api_003.php (신규)
- database/migrations/2026_02_25_170002_create_shipment_logs_table.php (신규)
- database/migrations/2026_02_25_170003_create_shipping_addresses_table.php (신규)
- app/Models/Shipment.php (신규)
- app/Models/ShipmentLog.php (신규)
- app/Models/ShippingAddress.php (신규)
- app/Models/Order.php (수정 — shipment(), shipping_status accessor)
- app/Services/ShippingService.php (신규)
- app/Http/Controllers/Api/ShipmentController.php (신규)
- app/Http/Controllers/Api/ShippingAddressController.php (신규)
- routes/api.php (수정 — 배송 6라우트, 배송지 5라우트)

## API 테스트 결과 (curl 시나리오)
| 시나리오 | 기대 HTTP | 비고 |
|----------|-----------|------|
| 14-1 소매 로그인 | 200 | RETAIL_TOKEN 획득 |
| 14-2 도매 로그인 | 200 | WHOLESALE_TOKEN 획득 |
| 14-3 관리자 로그인 | 200 | ADMIN_TOKEN 획득 |
| 14-4 POST /api/shipping-addresses | 201 | name, phone, address, is_default |
| 14-5 GET /api/shipping-addresses | 200 | addresses 배열 |
| 14-6 PUT /api/shipping-addresses/{id}/default | 200 | |
| 14-7 POST /api/orders/{id}/shipment | 201 | 주문 confirmed/preparing, 도매/관리자 토큰 |
| 14-8 PUT /api/shipments/{id}/tracking | 200 | tracking_company, tracking_number |
| 14-9 GET /api/shipments/{id}/tracking | 200 | tracking_url, logs |
| 14-10 PUT /api/shipments/{id}/status | 200 | status=delivered 등 |
| 14-11 GET /api/orders/{id}/shipment | 200 | |
| 14-12 V1 헬스 GET http://114.207.244.86 | 200 | |

(서버에서 14-1~14-12 curl 실행 후 위와 일치하는지 확인. 불일치 시 원인 파악 후 수정·재테스트.)

## 검수 결과
- **PHP Syntax**: app/Models/Shipment.php, ShipmentLog.php, ShippingAddress.php, Order.php, ShippingService.php, ShipmentController.php, ShippingAddressController.php — 7개 파일 `php -l` 통과 (No syntax errors detected).
- **마이그레이션**: 서버에서 `php artisan migrate` 실행 후 2026_02_25_170001, 170002, 170003 Ran 확인.
- **라우트**: `php artisan route:list --path=shipment` → 6개, `php artisan route:list --path=shipping-address` → 5개 확인.
- **V1 헬스**: `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` → 200.

## 비고
- 배송 생성은 주문 상태가 confirmed 또는 preparing(결제 완료 후)일 때만 가능.
- 송장 등록 시 Shipment.status=in_transit, Order.status=shipped, Order.tracking_* 동기화.
- 배송 상태 delivered 시 Order.delivered_at·status=delivered, returned 시 Order.status=cancelled 반영.
- 택배사: CJ대한통운, 로젠택배, 한진택배, 롯데택배, 우체국택배, 경동택배 (Shipment::SHIPPING_COMPANIES).
