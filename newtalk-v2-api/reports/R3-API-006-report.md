# R3-API-006 작업 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | R3-API-006 |
| 작업명 | 정산 API |
| 완료일 | 2026-02-26 KST |
| 버전 | v2.11.0 |
| 커밋 SHA | 푸시 후 `git log -1 --pretty=%h` 로 확인하여 기입 |
| 상태 | 완료 |

## 테이블 (3개)
- **settlements**: seller_id, settlement_number(ST-YYYYMMDD-XXXXX), status(pending/confirmed/processing/completed/cancelled), period_type(weekly/biweekly/monthly), period_start/end, order_count, total_sales, total_shipping_fee, platform_fee, platform_fee_rate, deductions, net_amount, bank_name/account/holder, confirmed_at, paid_at, admin_memo, seller_memo, softDeletes, INDEX(seller_id,status), INDEX(status,period_end), INDEX(settlement_number)
- **settlement_items**: settlement_id, order_id, payment_id, order_number(스냅샷), order_amount, shipping_fee, commission, commission_rate, deduction, net_amount, status(included/excluded/refunded), note, INDEX(settlement_id,order_id), INDEX(order_id)
- **settlement_logs**: settlement_id, user_id, action(created/confirmed/processing/completed/cancelled/memo/recalculated), from_status, to_status, description, metadata(JSON), INDEX(settlement_id,created_at)

## 모델 (3개)
- Settlement (seller, items, logs, generateNumber, canTransitionTo, recalculate)
- SettlementItem (settlement, order, payment)
- SettlementLog (settlement, user)

## 서비스
- **SettlementService**: create, updateStatus, list, getDetail, recalculate, updateItemStatus, preview, updateBankInfo

## 엔드포인트 (9개)
| Method | URI | 설명 | 권한 |
|--------|-----|------|------|
| POST | /api/settlements/preview | 정산 미리보기 | admin |
| POST | /api/settlements | 정산 생성 | admin |
| GET | /api/settlements | 정산 목록 | admin \| wholesale |
| GET | /api/settlements/{id} | 정산 상세 | admin \| wholesale (본인) |
| PUT | /api/settlements/{id}/status | 상태 변경 | admin |
| POST | /api/settlements/{id}/recalculate | 재계산 | admin |
| PUT | /api/settlements/{id}/bank-info | 은행 정보 | wholesale (본인) |
| PUT | /api/settlement-items/{id}/status | 항목 상태 | admin |
| POST | /api/settlements/{id}/memo | 메모 | admin \| wholesale |

## 파일 목록
- database/migrations/2026_02_26_200001_create_settlements_table.php
- database/migrations/2026_02_26_200002_create_settlement_items_table.php
- database/migrations/2026_02_26_200003_create_settlement_logs_table.php
- app/Models/Settlement.php
- app/Models/SettlementItem.php
- app/Models/SettlementLog.php
- app/Models/Order.php (settlementItems 관계 추가)
- app/Services/SettlementService.php
- app/Http/Controllers/Api/SettlementController.php
- routes/api.php (정산 라우트 추가)

## 실행 결과 (서버에서 실행 후 기입)
- 마이그레이션: `docker compose --env-file .env.docker exec app php artisan migrate --force` → 3개 Ran
- 라우트: `php artisan route:list --path=settlement` → 9개 확인
- tinker: `Schema::hasTable('settlements')` 등 → 111 출력 확인
- V1 헬스: `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` → 200

## 비고
- 정산 생성 시 기간 내 delivered/completed + payment_status=paid + delivered_at 기준, 이미 정산에 포함된 주문 제외(whereDoesntHave('settlementItems')).
- 상태 전이: pending→confirmed/cancelled, confirmed→processing/cancelled, processing→completed/cancelled, completed/cancelled 종료. cancelled→pending 재처리 가능.
