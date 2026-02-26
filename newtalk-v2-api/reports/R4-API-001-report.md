# R4-API-001 작업 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | R4-API-001 |
| 작업명 | 거래처 제도 API (소매→도매 신청/승인/전용가, 경로 B 1~2%) |
| 완료일 | 2026-02-26 KST |
| 버전 | v3.1.0 |
| 커밋 SHA | 푸시 후 `git log -1 --pretty=%h` 로 확인하여 기입 |
| 상태 | 완료 |

## 테이블 (3개 + orders 컬럼 추가)
- **trade_applications**: retail_user_id, wholesale_user_id, status(pending/approved/rejected/suspended/terminated), business_name, business_number, business_type, introduction, phone, reject_reason, approved_at, rejected_at, UNIQUE(retail_user_id, wholesale_user_id), INDEX(wholesale_user_id, status), INDEX(retail_user_id, status), softDeletes
- **trade_partnerships**: retail_user_id, wholesale_user_id, application_id, tier(basic/silver/gold/vip), discount_rate, commission_rate(기본 1.5%), is_active, total_orders, total_amount, wholesale_memo, retail_memo, UNIQUE(retail_user_id, wholesale_user_id), INDEX(wholesale_user_id, is_active), INDEX(tier), softDeletes
- **trade_prices**: partnership_id, product_id, product_option_id(nullable), trade_price, original_price, is_active, UNIQUE(partnership_id, product_id, product_option_id), INDEX(product_id, is_active)
- **orders**: trade_partnership_id(nullable), commission_rate(nullable) 컬럼 추가

## 모델 (3개 + Order 수정)
- TradeApplication (STATUS_TRANSITIONS, canTransitionTo, scopePending, scopeByWholesale, scopeByRetail, retailUser, wholesaleUser, partnership)
- TradePartnership (TIER_THRESHOLDS, getDiscountedPrice, incrementOrderStats, autoUpgradeTier, retailUser, wholesaleUser, application, prices)
- TradePrice (partnership, product, productOption)
- Order: trade_partnership_id, commission_rate fillable/casts, tradePartnership() 관계 추가

## 서비스
- **TradeService** (14 메서드): apply, approve, reject, suspend, terminate, getApplications, getPartners, getPartnerDetail, setTradePrice, removeTradePrice, bulkSetTradePrices, getTradePrice, updatePartnershipTier, updateCommissionRate

## 엔드포인트 (14개)
| Method | URI | 설명 | 권한 |
|--------|-----|------|------|
| POST | /api/trade/apply | 거래처 신청 | auth + role:retail |
| GET | /api/trade/price/{productId} | 내 적용가 조회 | auth + role:retail |
| GET | /api/trade/applications | 신청 목록 (도매: 받은 신청, 소매: 내 신청) | auth + role:retail\|wholesale\|admin |
| GET | /api/trade/applications/{application} | 신청 상세 | auth + role:retail\|wholesale\|admin |
| PUT | /api/trade/applications/{application}/approve | 승인 | auth + role:wholesale |
| PUT | /api/trade/applications/{application}/reject | 거절 | auth + role:wholesale |
| GET | /api/trade/partners | 거래처 목록 | auth + role:retail\|wholesale\|admin |
| GET | /api/trade/partners/{partnership} | 거래처 상세 | auth + role:retail\|wholesale\|admin |
| PUT | /api/trade/partners/{partnership}/suspend | 일시 중지 | auth + role:wholesale |
| PUT | /api/trade/partners/{partnership}/terminate | 종료 | auth + role:wholesale |
| POST | /api/trade/partners/{partnership}/prices | 전용가 설정 | auth + role:wholesale |
| POST | /api/trade/partners/{partnership}/prices/bulk | 일괄 전용가 | auth + role:wholesale |
| DELETE | /api/trade/prices/{tradePrice} | 전용가 삭제 | auth + role:wholesale |
| PUT | /api/trade/partners/{partnership}/commission | 수수료율 변경 | auth + role:admin |

## Order 연동
- 주문 생성 시: TradeService::getTradePrice()로 품목별 적용가 조회, 거래처 관계 있으면 commission_rate(경로 B 1~2%)·trade_partnership_id 저장
- 주문 배송 완료 시: TradePartnership::incrementOrderStats(), autoUpgradeTier() 호출 (결제 완료된 경우)

## 파일 목록
- database/migrations/2026_02_26_300001_create_trade_applications_table.php
- database/migrations/2026_02_26_300002_create_trade_partnerships_table.php
- database/migrations/2026_02_26_300003_create_trade_prices_table.php
- database/migrations/2026_02_26_300004_add_trade_partnership_id_to_orders_table.php
- app/Models/TradeApplication.php
- app/Models/TradePartnership.php
- app/Models/TradePrice.php
- app/Services/TradeService.php
- app/Http/Controllers/Api/TradeController.php
- app/Models/Order.php (trade_partnership_id, commission_rate, tradePartnership 관계)
- app/Http/Controllers/Api/OrderController.php (TradeService 주입, 주문 시 적용가/거래처 반영, 배송 완료 시 통계 갱신)
- routes/api.php (trade prefix 14 라우트)

## 실행 결과 (서버에서 실행 후 기입)
- 마이그레이션: `docker compose --env-file .env.docker exec app php artisan migrate --force` → 4개 Ran
- 라우트: `php artisan route:list --path=trade` → 14개 확인
- API 테스트: 지시서 STEP 7 curl 실행 후 결과 기입
- V1 헬스: `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` → 200

## 비고
- 거래처 신청 상태 전이: pending→approved/rejected, approved→suspended/terminated, rejected→pending(재신청), suspended→approved/terminated.
- 등급 임계: basic 0원, silver 500만, gold 2천만, vip 5천만 (누적 거래액 기준).
- 경로 B: 직거래 수수료 1~2%, 관리자만 수수료율 변경 가능.
