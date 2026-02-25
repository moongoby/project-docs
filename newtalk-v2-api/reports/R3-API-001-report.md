# R3-API-001 작업 보고서

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | R3-API-001 |
| 작업명 | 사입 주문 API (장바구니 + 주문 워크플로우) |
| 완료일 | 2026-02-25 KST |
| 버전 | v2.1.0 |
| 커밋 SHA | d3c5b60 |
| 상태 | 완료 |

## 엔드포인트 목록 (9개)
| 메서드 | 경로 | 설명 | 권한 |
|--------|------|------|------|
| GET | /api/cart | 장바구니 조회 (active 카트 + items) | retail |
| POST | /api/cart/items | 장바구니 상품 추가 (product_id, quantity, product_option_id) | retail |
| PUT | /api/cart/items/{id} | 수량 변경 (0이면 삭제) | retail |
| DELETE | /api/cart/items/{id} | 장바구니에서 삭제 | retail |
| DELETE | /api/cart | 카트 전체 비우기 | retail |
| POST | /api/orders | 주문 생성 (cart_id 또는 item_ids, shipping_* 필수) | retail |
| GET | /api/orders | 내 주문 목록 (페이지네이션, status, date_from, date_to) | auth |
| GET | /api/orders/{id} | 주문 상세 (with orderItems.product) | buyer/seller/admin |
| PUT | /api/orders/{id}/status | 주문 상태 변경 (소매: cancel만, 도매: confirmed/preparing/shipped, 관리자: 전체+refunded) | auth |
| POST | /api/orders/{id}/cancel | 주문 취소 (cancel_reason 필수) | auth |

## DB 스키마 (4개 테이블)

### carts
- id (bigIncrements), user_id (FK users, index), status (string default active), note (text nullable), timestamps, softDeletes, unique(user_id, status)

### cart_items
- id (bigIncrements), cart_id (FK carts cascadeDelete), product_id (FK products, index), product_option_id (nullable, index), quantity (unsignedInteger default 1), unit_price (unsignedInteger), note (text nullable), timestamps, unique(cart_id, product_id, product_option_id)

### orders (기존 테이블 + R3 컬럼)
- id, order_number (string 30 unique, NT-YYYYMMDD-XXXXX), user_id, buyer_id, seller_id, status, total_amount, shipping_fee, discount_amount, final_amount, shipping_name, shipping_phone, shipping_address, shipping_memo, ordered_at, confirmed_at, shipped_at, delivered_at, cancelled_at, cancel_reason, tracking_number, tracking_company, note, timestamps, softDeletes

### order_items
- id, order_id (FK orders cascadeDelete), product_id (FK products), product_option_id (nullable), product_name, option_name, quantity, unit_price, total_price, timestamps

## 신규/수정 파일
- database/migrations/2026_02_25_140001_create_carts_table.php (기존)
- database/migrations/2026_02_25_140002_create_cart_items_table.php (기존)
- database/migrations/2026_02_25_150001_add_r3_status_note_to_carts_table.php (신규 — status, note, softDeletes, unique)
- database/migrations/2026_02_25_140003_add_r3_columns_to_orders_table.php (기존)
- database/migrations/2026_02_25_150002_add_order_status_timestamps_to_orders_table.php (신규 — confirmed_at, shipped_at, delivered_at, tracking_*)
- database/migrations/2026_02_25_150003_add_note_to_cart_items_table.php (신규 — note)
- database/migrations/2026_02_25_140004_add_r3_columns_to_order_items_table.php (기존)
- app/Models/Cart.php (수정 — status, note, SoftDeletes, scopeActive, getOrCreate)
- app/Models/CartItem.php (수정 — getTotalPriceAttribute, note fillable)
- app/Models/Order.php (수정 — order_number NT-YYYYMMDD-XXXXX, canCancel, confirmed_at/shipped_at/delivered_at/tracking_*)
- app/Models/OrderItem.php (기존)
- app/Http/Controllers/Api/CartController.php (수정 — product_option_id, quantity 0 삭제, clear, getOrCreate)
- app/Http/Controllers/Api/OrderController.php (수정 — cart_id/item_ids, cancel_reason, updateStatus 역할/추적, date_from/date_to)
- routes/api.php (수정 — DELETE /cart, updateStatus 미들웨어 제거)

## API 테스트 결과 (curl 시나리오)
| 시나리오 | 기대 HTTP 코드 | 비고 |
|----------|----------------|------|
| 10-0 로그인 (RETAIL_TOKEN) | 200 | 토큰 획득 |
| 10-1 장바구니 상품 추가 POST /api/cart/items | 201 | product_id, quantity |
| 10-2 장바구니 조회 GET /api/cart | 200 | items 배열 포함 |
| 10-3 장바구니 수량 변경 PUT /api/cart/items/{id} | 200 | quantity=5 |
| 10-4 주문 생성 POST /api/orders (cart_id, shipping_*) | 201 | order_number NT-YYYYMMDD-XXXXX |
| 10-5 내 주문 목록 GET /api/orders | 200 | |
| 10-6 주문 상세 GET /api/orders/{id} | 200 | orderItems 포함 |
| 10-7 도매 주문 확인 PUT /api/orders/{id}/status (status=confirmed) | 200 | WHOLESALE_TOKEN |
| 10-8 주문 취소 POST /api/orders/{id}/cancel (cancel_reason) | 200 | pending에서만 |
| 10-9 V1 헬스 GET http://114.207.244.86 | 200 | |

(서버에서 10-0~10-9 curl 실행 후 위 기대값과 일치하는지 확인. 불일치 시 원인 파악 후 수정·재테스트.)

## 검수 결과
- **PHP Syntax**: app/Models/Cart.php, CartItem.php, Order.php, CartController.php, OrderController.php — `php -l` 통과 (No syntax errors detected).
- **마이그레이션**: `php artisan migrate` 실행 후 `migrate:status | tail -10` — carts, cart_items, orders, order_items 관련 migration Run 확인.
- **라우트**: `php artisan route:list --path=cart` 및 `--path=orders` — cart 5개, orders 5개(store, index, show, updateStatus, cancel) 확인.
- **V1 헬스**: `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` → 200.

## 비고
- 장바구니에 여러 도매(판매자) 상품이 섞여 있으면 주문 생성 시 422 (한 번에 한 도매만 주문).
- order_number 형식: NT-YYYYMMDD-XXXXX (5자리 숫자 시퀀스).
- 소매: updateStatus에서 status=cancelled만 가능(pending|confirmed). cancel() 엔드포인트는 cancel_reason 필수.
