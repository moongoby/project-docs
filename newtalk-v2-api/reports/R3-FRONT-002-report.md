# R3-FRONT-002 작업 보고서

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | R3-FRONT-002 |
| 작업명 | 결제 UI (토스페이먼츠 프론트 연동) |
| 완료일 | 2026-02-25 KST |
| 버전 | v2.4.0 |
| 커밋 SHA | (12단계 푸시 후 git log --oneline -1 결과 7자리로 교체) |
| 상태 | 완료 (토스 테스트 키 설정 후 실결제 플로우 테스트 필요) |

## 페이지
| 경로 | 설명 |
|------|------|
| /retail/payment | 결제 페이지 (order_id 쿼리, 수단 선택, 결제하기) |
| /retail/payment/success | 결제 성공 콜백 (confirmPayment, PaymentResult 성공) |
| /retail/payment/fail | 결제 실패 콜백 (에러 메시지, 다시 시도/주문 내역) |

## 수정 페이지
| 경로 | 변경 내용 |
|------|------------|
| /retail/orders/[id] | getOrderPayment, PaymentDetail, 결제하기 버튼 |
| /retail/order/new | createOrder 성공 시 /retail/payment?order_id={id} 리다이렉트 |
| /wholesale/orders/[id] | getOrderPayment, PaymentStatusBadge + 결제금액 표시 |

## 컴포넌트 (8개)
- PaymentMethodSelector — 결제 수단 선택(카드/가상계좌/계좌이체/간편결제), 카드 할부 개월
- PaymentSummary — 주문 상품 요약, 금액, 결제하기 버튼
- PaymentProcessing — 결제 진행 중 로딩, 30초 후 "결제 확인 중" 메시지
- PaymentResult — 성공(주문번호·금액·영수증·주문 상세 링크) / 실패(에러·다시 시도·주문 내역)
- PaymentStatusBadge — ready=gray, in_progress=yellow, done=green, canceled/aborted=red, partial_canceled=orange, expired=gray
- PaymentDetail — 결제 정보·로그 타임라인, 결제 취소 버튼 → PaymentCancelDialog
- PaymentCancelDialog — 취소 사유(필수), 부분 취소 금액(선택)
- TossPaymentWidget (useTossPaymentRequest) — @tosspayments/tosspayments-sdk 동적 로드, requestPayment

## API 클라이언트
- **payment-api.ts**: preparePayment, confirmPayment, getPayment, cancelPayment, getOrderPayment (5함수)

## 타입
- **payment.ts**: PaymentStatus, OrderPaymentStatus, Payment, PaymentLog, PaymentPrepareRequest/Response, PaymentConfirmRequest, PaymentCancelRequest
- **order.ts**: OrderPaymentStatus 추가, Order에 payment_status?, paid_at? 추가

## 검수
- **TypeScript 컴파일**: 서버에서 `docker compose --env-file .env.docker exec frontend npx tsc --noEmit` → 0 에러 목표
- **페이지 렌더링**: /retail/payment, /retail/payment/success, /retail/payment/fail, /retail/orders 각 200 또는 302
- **V1 헬스**: curl http://114.207.244.86 → 200

## 신규/수정 파일
(서버에서 `git diff --name-only main~1 main` 또는 `git log --name-only -1` 결과로 채움)

- frontend/src/types/payment.ts
- frontend/src/types/order.ts (payment_status, paid_at, OrderPaymentStatus)
- frontend/src/lib/payment-api.ts
- frontend/src/components/payment/PaymentMethodSelector.tsx
- frontend/src/components/payment/PaymentSummary.tsx
- frontend/src/components/payment/PaymentProcessing.tsx
- frontend/src/components/payment/PaymentResult.tsx
- frontend/src/components/payment/PaymentStatusBadge.tsx
- frontend/src/components/payment/PaymentDetail.tsx
- frontend/src/components/payment/PaymentCancelDialog.tsx
- frontend/src/components/payment/TossPaymentWidget.tsx
- frontend/src/components/payment/index.ts
- frontend/src/app/(retail)/retail/payment/page.tsx
- frontend/src/app/(retail)/retail/payment/success/page.tsx
- frontend/src/app/(retail)/retail/payment/fail/page.tsx
- frontend/src/app/(retail)/retail/orders/[id]/page.tsx
- frontend/src/app/(retail)/retail/order/new/page.tsx
- frontend/src/app/(wholesale)/wholesale/orders/[id]/page.tsx
- frontend/package.json (@tosspayments/tosspayments-sdk)
- frontend/.env.local.example (NEXT_PUBLIC_TOSS_CLIENT_KEY 주석)

## 비고
- NEXT_PUBLIC_TOSS_CLIENT_KEY 미설정 시 결제 요청 시 "클라이언트 키가 설정되지 않았습니다" 안내. SDK 로드만 확인 가능.
- 결제 성공 URL에 oid(주문 ID) 쿼리 포함하여 confirm API 호출 시 사용.
