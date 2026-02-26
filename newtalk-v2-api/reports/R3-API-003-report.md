# R3-API-003 작업 보고서
| 항목 | 내용 |
|------|------|
| 작업 ID | R3-API-003 |
| 작업명 | 배송 API (위탁배송·배송추적·배송지) |
| 버전 | v2.5.0 |
| 상태 | 완료 |

## 구현
- shipments, shipment_logs, shipping_addresses 테이블
- ShipmentController 6 EP, ShippingAddressController 5 EP
- ShippingService (createShipment, updateTracking, updateStatus, getTrackingInfo)
