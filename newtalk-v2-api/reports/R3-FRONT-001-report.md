# R3-FRONT-001 작업 보고서

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | R3-FRONT-001 |
| 작업명 | 사입 주문·장바구니 프론트 UI |
| 완료일 | 2026-02-25 KST 2026-02-25 15:01:01 KST |
| 버전 | v2.2.0 |
| 커밋 SHA | b798049 |
| 상태 | 완료 |

## 페이지 목록
| 경로 | 설명 |
|------|------|
| /retail/cart | 장바구니 (조회, 수량 변경, 삭제, 비우기, 주문하기) |
| /retail/order/new | 주문 생성 (배송정보, 상품 목록, 주문 확정) |
| /retail/orders | 주문 목록 (필터, 페이지네이션) |
| /retail/orders/[id] | 주문 상세 (타임라인, 취소) |
| /wholesale/orders | 도매 주문 관리 목록 |
| /wholesale/orders/[id] | 도매 주문 상세 (상태 변경, 송장 입력) |

## 컴포넌트 목록
- **장바구니**: CartItemCard, CartSummary, CartEmpty
- **주문**: ShippingForm, OrderItemList, OrderSummaryCard, OrderStatusBadge, OrderCard, OrderDetail, OrderCancelDialog

## API 클라이언트
- **cart-api.ts**: getCart, addCartItem, updateCartItem, removeCartItem, clearCart (5함수)
- **order-api.ts**: createOrder, getOrders, getOrder, updateOrderStatus, cancelOrder (5함수)

## 타입
- **cart.ts**: Cart, CartItem, GetCartResponse, CartItemRequest, CartItemUpdateRequest
- **order.ts**: Order, OrderItem, OrderStatus, OrderCreateRequest, OrderStatusUpdateRequest, OrderCancelRequest, OrderListParams, OrderListResponse

## 검수 결과
- **TypeScript 컴파일**: `docker compose --env-file .env.docker exec frontend npx tsc --noEmit` → 0 에러
- **페이지 렌더링**: /retail/cart, /retail/order/new, /retail/orders, /wholesale/orders → 각 200 (또는 302 로그인 리다이렉트)
- **V1 헬스**: `curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]` → 200
- **보고서 빈칸**: 0 (푸시 후 SHA·완료일을 실제 값으로 교체 후 재커밋)

## 신규/수정 파일
(서버에서 `git diff --name-only main~1 main` 또는 `git log --name-only -1` 결과로 채움)

- frontend/src/types/cart.ts
- frontend/src/types/order.ts
- frontend/src/lib/cart-api.ts
- frontend/src/lib/order-api.ts
- frontend/src/components/cart/CartItemCard.tsx
- frontend/src/components/cart/CartSummary.tsx
- frontend/src/components/cart/CartEmpty.tsx
- frontend/src/components/cart/index.ts
- frontend/src/components/order/ShippingForm.tsx
- frontend/src/components/order/OrderItemList.tsx
- frontend/src/components/order/OrderSummaryCard.tsx
- frontend/src/components/order/OrderStatusBadge.tsx
- frontend/src/components/order/OrderCard.tsx
- frontend/src/components/order/OrderDetail.tsx
- frontend/src/components/order/OrderCancelDialog.tsx
- frontend/src/components/order/index.ts
- frontend/src/app/(retail)/retail/cart/page.tsx
- frontend/src/app/(retail)/retail/order/new/page.tsx
- frontend/src/app/(retail)/retail/orders/page.tsx
- frontend/src/app/(retail)/retail/orders/[id]/page.tsx
- frontend/src/app/(wholesale)/wholesale/orders/page.tsx
- frontend/src/app/(wholesale)/wholesale/orders/[id]/page.tsx
- frontend/src/components/layout/retail-layout.tsx (주문내역 링크 추가)
- frontend/src/components/product/product-action-bar.tsx (장바구니 담기 버튼 추가)

## 비고
- shadcn 컴포넌트(table, dialog, sheet, toast, select, radio-group)는 지시서대로 Docker 내부에서 `npx shadcn@latest add table dialog sheet toast select radio-group` 실행 후 필요 시 사용 가능.
- 장바구니 담기 시 product_option_id는 상품 상세에서 선택 옵션 연동 시 추가 가능.
