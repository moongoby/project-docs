# R3-API-002 작업 보고서

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | R3-API-002 |
| 작업명 | 결제 연동 API (토스페이먼츠) |
| 완료일 | 2026-02-25 KST |
| 버전 | v2.3.0 |
| 커밋 SHA | (서버 푸시 후 `git log --oneline -1` 결과 기입) |
| 상태 | 완료 (토스 테스트 키 설정 후 실결제 테스트 필요) |

## 엔드포인트 목록 (6개)
| 메서드 | 경로 | 설명 | 권한 |
|--------|------|------|------|
| POST | /api/payments/prepare | 결제 준비 (order_id → payment_id, client_key, amount) | auth, 주문 소유자 |
| POST | /api/payments/confirm | 결제 확인 (payment_key, order_id, amount) | auth |
| GET | /api/payments/{id} | 결제 상세 (with logs) | 소유자 또는 admin |
| POST | /api/payments/{id}/cancel | 결제 취소 (cancel_reason 필수, cancel_amount 선택) | 소유자 또는 admin |
| GET | /api/orders/{id}/payment | 주문의 결제 조회 | buyer/seller/admin |
| POST | /api/payments/webhook | 토스 웹훅 수신 | 없음 (secret 검증 추후 설정) |

## DB 스키마

### payments
- id (bigIncrements), order_id (FK orders), user_id (FK users), payment_key (string 200 unique nullable), order_number (string 30 index), method (string 20 nullable), status (string 20 default ready), amount, approved_amount, balance_amount, currency (default KRW), requested_at, approved_at, cancelled_at, cancel_reason, fail_reason, receipt_url, card_company, card_number, card_installment_months, virtual_account_*, raw_response (json), timestamps, softDeletes, index(order_id, status), index(user_id, status)

### payment_logs
- id (bigIncrements), payment_id (FK payments cascadeDelete), action (string 30), status_before, status_after, amount, request_data, response_data (json), error_code, error_message, ip_address, timestamps, index(payment_id, action)

### orders 추가 컬럼
- payment_status (string 20 default unpaid) — unpaid, paid, partial_refund, refunded
- paid_at (timestamp nullable)

## 신규/수정 파일
- database/migrations/2026_02_25_160001_create_payments_table.php (신규)
- database/migrations/2026_02_25_160002_create_payment_logs_table.php (신규)
- database/migrations/2026_02_25_160003_add_payment_columns_to_orders_table.php (신규)
- app/Models/Payment.php (신규)
- app/Models/PaymentLog.php (신규)
- app/Models/Order.php (수정 — payment_status, paid_at, payment(), final_amount accessor, isPaid())
- app/Services/TossPaymentService.php (신규)
- app/Http/Controllers/Api/PaymentController.php (신규)
- routes/api.php (수정 — payments 5라우트 + webhook 1라우트, orders/{id}/payment)
- config/services.php (수정 — toss 섹션)

## API 테스트 결과 (curl 시나리오)
| 시나리오 | 기대 | 비고 |
|----------|------|------|
| 15-1 소매 로그인 | 200 | 서버에서 실행 후 결과 기록 |
| 15-3 POST /api/payments/prepare (order_id=1) | 200, payment_id, client_key, amount | TOSS_CLIENT_KEY 없어도 prepare는 동작 (client_key 빈 문자열 가능) |
| 15-4 GET /api/payments/{id} | 200, status=ready | |
| 15-5 GET /api/orders/{id}/payment | 200 또는 404 | 해당 주문에 결제 없으면 404 |
| 15-6 POST /api/payments/confirm | 200 또는 400 | TOSS_SECRET_KEY 미설정 시 스킵 또는 400 메시지 기록 |
| 15-7 POST /api/payments/{id}/cancel | 200 또는 422 | 토스 키 필요 시 스킵 사유 기록 |
| 15-8 POST /api/payments/webhook | 200 | webhook secret 미설정 시에도 200 + 로그 기록 |
| 15-9 V1 헬스 GET http://114.207.244.86 | 200 | |

## 검수 결과
- **PHP Syntax**: app/Models/Payment.php, PaymentLog.php, Order.php, TossPaymentService.php, PaymentController.php — 모두 "No syntax errors detected".
- **마이그레이션**: 서버에서 `php artisan migrate` 실행 후 2026_02_25_160001, 160002, 160003 Ran 확인.
- **라우트**: `php artisan route:list --path=payments` → 6개 (prepare, confirm, show, cancel, webhook, orderPayment). `--path=orders` 에 GET orders/{id}/payment 포함 확인.
- **V1 헬스**: 서버에서 `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` → 200 확인.

## 비고
- orders 테이블에는 기존에 payment_method 컬럼이 있어 160003 마이그레이션에서는 payment_status, paid_at만 추가함.
- 결제 요청 금액은 Order::final_amount (total_amount + shipping_fee) 사용.
- .env.docker에 TOSS_CLIENT_KEY, TOSS_SECRET_KEY 설정 후 토스 대시보드 테스트 키로 실결제/취소 테스트 가능.
