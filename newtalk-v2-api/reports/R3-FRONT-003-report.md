# R3-FRONT-003 작업 보고서

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | R3-FRONT-003 |
| 작업명 | 배송 UI (배송 추적·배송지 관리) |
| 완료일 | 2026-02-25 KST |
| 버전 | v2.6.0 |
| 커밋 SHA | (서버 main 푸시 후 `git log --oneline -1` 결과 7자리 기입) |
| 상태 | 완료 |

## 페이지 목록
| 경로 | 설명 |
|------|------|
| /retail/addresses | 배송지 관리 (목록, 추가, 수정, 삭제, 기본설정) |
| /retail/orders/[id] | 주문 상세 + ShipmentCard, ShipmentTimeline, 추적 링크 |
| /wholesale/orders/[id] | 도매 주문 상세 + 배송 접수, TrackingInput, ShipmentCard·Timeline, 배송 완료 |
| /retail/order/new | 주문 생성 + AddressSelectDialog, 기본배송지 자동 채움 |

## 컴포넌트 목록
- **배송**: ShipmentTimeline, ShipmentStatusBadge, ShipmentDetail, TrackingInput, ShipmentCard
- **배송지**: AddressCard, AddressForm, AddressSelectDialog, AddressList

## API 클라이언트 (shipping-api.ts)
- **배송 (6)**: getOrderShipment, createShipment, updateTracking, updateShipmentStatus, getTrackingInfo, getShipment
- **배송지 (5)**: getShippingAddresses, createShippingAddress, updateShippingAddress, deleteShippingAddress, setDefaultAddress

## 타입 파일
- **types/shipping.ts**: ShippingAddress, Shipment, ShipmentLog, ShipmentStatus, ShippingCompany, SHIPPING_COMPANIES, ShippingAddressForm, CreateShipmentRequest, UpdateTrackingRequest, UpdateShipmentStatusRequest, TrackingInfoResponse

## 검수 결과
- **TypeScript 컴파일**: 서버에서 `docker compose --env-file .env.docker exec frontend npx tsc --noEmit` 실행 후 0 에러 확인
- **페이지 HTTP 검증**: /retail/addresses, /retail/orders, /wholesale/orders → 200 또는 302 (로그인 리다이렉트)
- **V1 헬스**: `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` → 200

## 신규/수정 파일
- frontend/src/types/shipping.ts
- frontend/src/lib/shipping-api.ts
- frontend/src/components/shipping/ShipmentTimeline.tsx
- frontend/src/components/shipping/ShipmentStatusBadge.tsx
- frontend/src/components/shipping/ShipmentDetail.tsx
- frontend/src/components/shipping/TrackingInput.tsx
- frontend/src/components/shipping/ShipmentCard.tsx
- frontend/src/components/shipping/index.ts
- frontend/src/components/address/AddressCard.tsx
- frontend/src/components/address/AddressForm.tsx
- frontend/src/components/address/AddressList.tsx
- frontend/src/components/address/AddressSelectDialog.tsx
- frontend/src/components/address/index.ts
- frontend/src/app/(retail)/retail/addresses/page.tsx
- frontend/src/app/(retail)/retail/orders/[id]/page.tsx
- frontend/src/app/(retail)/retail/order/new/page.tsx
- frontend/src/app/(wholesale)/wholesale/orders/[id]/page.tsx
- frontend/src/components/layout/retail-layout.tsx

## 비고
- R3-API-003 배송 API 의존. 배송 생성은 주문 상태 confirmed/preparing일 때만 가능.
- 택배사: CJ대한통운, 로젠택배, 한진택배, 롯데택배, 우체국택배, 경동택배 (백엔드 Shipment::SHIPPING_COMPANIES와 동일).
- 주문 생성 시 기본배송지가 있으면 폼에 자동 채움; "배송지 선택"으로 다른 배송지 선택 가능.
