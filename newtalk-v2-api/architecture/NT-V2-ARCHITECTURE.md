# 뉴톡 V2 — 시스템 아키텍처 문서

> 최종 갱신: 2026-02-25 KST
> 프로젝트 버전: v2.5.0 (R3-API-003 배송 API까지 반영)
> 작성 근거: routes/api.php, frontend 경로, HANDOVER·CONTEXT·CHANGELOG

---

## 1. 시스템 개요

NewTalk V2는 Laravel 12 + Next.js 16 기반의 B2B SaaS 마켓플레이스이다.
V1(CodeIgniter 3 / PHP 5.4)을 전면 재구축하며, 동일 서버에서 V1과 공존한다.

### 1.1 핵심 기능 4가지
1. **SNS 소셜 엔진** — 피드, 스토리, DM, 쇼츠
2. **SaaS 브랜드 인프라** — 도매 브랜드몰 월정액 (44,000 ~ 165,000원)
3. **소매 커머스 허브** — 소매 사입 주문, 장바구니, 결제
4. **소매 회원가입** — 도매몰 내 소매 회원 자동 등록

### 1.2 8-레이어 아키텍처
| 레이어 | 이름 | 설명 | 현재 구현 상태 |
|--------|------|------|---------------|
| L1 | SNS 소셜 엔진 | 피드, 스토리, DM, 쇼츠 | R2-API-001 완료 (피드·팔로우·찜) |
| L2 | SaaS 브랜드 인프라 | 브랜드 페이지, 구독 관리 | R2-API-002 완료 |
| L3 | 소매 커머스 허브 | 장바구니, 주문, 결제, 배송 | R3-API-001/002/003, R3-FRONT-001/002 완료 |
| L4 | 마켓플레이스 거래 엔진 | 거래 수수료 (개설 3-5%, 직접 1-2%) | 설계 완료, 구현 예정 |
| L5 | AI 인텔리전스 | AI 콘텐츠 생성·추천 | R2-API-003 완료 (기본 API) |
| L6 | 확장 (일본·라이브 B2B) | 크로스보더, 라이브 | R4 예정 |
| L7 | 셀러 확장 엔진 | Cafe24·네이버·쿠팡 연동 | R2-API-004 완료 (Cafe24) |
| L8 | 콘텐츠 팩토리 | NAS 연동, 스튜디오, AI 생성 | 별도 진행 중 |

---

## 2. 인프라 구성

### 2.1 서버 정보
- **호스트**: rfree-009 (114.207.244.86)
- **OS**: Ubuntu 20.04 LTS
- **CPU**: AMD EPYC 7262 (8 cores)
- **RAM**: 16 GB
- **Docker**: 28.1.1, Compose v2.35.1

### 2.2 Docker 컨테이너 구성

```
┌─────────────────────────────────────────────────────────────┐
│ rfree-009 서버                                               │
│                                                              │
│ ┌─── V1 (레거시, 수정 금지) ───┐                             │
│ │ Apache + PHP 5.4             │ :80, :443                   │
│ │ MySQL 5.7                    │ :3306                        │
│ │ DB: autoda (read-only)       │                              │
│ └──────────────────────────────┘                             │
│                                                              │
│ ┌─── V2 Docker Stack ──────────────────────────────────────┐ │
│ │ ┌──────────┐ ┌───────────┐ ┌──────────────────┐           │ │
│ │ │ nginx    │ │ app       │ │ frontend         │           │ │
│ │ │ 1.25     │ │ PHP 8.3   │ │ Next.js 16       │           │ │
│ │ │ :8080    │ │ Laravel12 │ │ :3000            │           │ │
│ │ └──────────┘ └───────────┘ └──────────────────┘           │ │
│ │ ┌──────────┐ ┌───────────┐                                 │ │
│ │ │ MySQL8.0 │ │ Redis 7   │                                 │ │
│ │ │ :3307    │ │ :6380     │                                 │ │
│ │ └──────────┘ └───────────┘                                 │ │
│ │ DB: newtalk_v2 (read/write)                                │ │
│ └───────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─── 보호 시스템 (수정 금지) ──┐                              │
│ │ V1 Admin (114.207.244.87)   │                              │
│ │ NAS image-auto (192.168.30.23:8100)                        │
│ │ ShortFlow AI (:3001)        │                              │
│ └─────────────────────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 URL 엔드포인트
| 서비스 | URL | 비고 |
|--------|-----|------|
| V2 API | http://114.207.244.86:8080 | Laravel 12 |
| V2 Frontend | http://114.207.244.86:3000 | Next.js 16 |
| V1 Web | http://114.207.244.86 | 수정 금지 |
| V1 Admin | http://114.207.244.87 | 수정 금지 |

---

## 3. 데이터베이스 스키마

### 3.1 테이블 목록 (HANDOVER·CHANGELOG·보고서 기반)

> 정확한 전체 목록은 서버에서 `SHOW TABLES` 실행 후 `/tmp/db-tables.txt` 참조.

#### 3.1.1 인증·사용자 도메인
- **users** — 사용자 (id, name, email, role, company_name, business_number 등)
- **personal_access_tokens** — Sanctum 토큰

#### 3.1.2 상품 도메인
- **products** — 상품 (id, user_id, brand_id, name, price, wholesale_price 등)
- **product_images** — 상품 이미지
- **product_options** — 상품 옵션

#### 3.1.3 브랜드 도메인
- **brands** — 브랜드 기본 정보
- **brand_pages** — 브랜드 페이지 (user_id, brand_id, template, settings 등)

#### 3.1.4 주문·장바구니 도메인

```
users ──1:N──> carts ──1:N──> cart_items ──N:1──> products
  │                │
  │                │
  └──> orders ──1:N──> order_items ──────────────┘
```

- **carts** — 장바구니 (user_id, status[active/ordered/abandoned], note, unique(user_id,status))
- **cart_items** — 장바구니 아이템 (cart_id, product_id, product_option_id, quantity, unit_price)
- **orders** — 주문 (buyer_id, seller_id, order_number[NT-YYYYMMDD-XXXXX], status, shipping 필드, payment_status, paid_at, tracking)
- **order_items** — 주문 아이템 (order_id, product_id, 스냅샷 필드)

#### 3.1.5 결제 도메인

```
orders ──1:1──> payments ──1:N──> payment_logs
```

- **payments** — 결제 (order_id, user_id, payment_key, method, status, amount, card/vbank 필드, raw_response)
- **payment_logs** — 결제 로그 (payment_id, action, status_before/after, request/response data, ip)

#### 3.1.6 배송 도메인 (R3-API-003)
- **shipments** — 배송 (order_id, seller_id, buyer_id, type, tracking_company, tracking_number 등)
- **shipment_logs** — 배송 로그
- **shipping_addresses** — 배송지 (user_id, label, name, phone, postal_code, address, is_default)

#### 3.1.7 AI 콘텐츠 도메인
- **contents** — 콘텐츠 (user_id, type, status, visibility, title, body, scheduled_at)
- **contents_media** — 미디어 (content_id, type, url, order)
- **contents_product_tags** — 상품 태그 (content_id, product_id)

#### 3.1.8 Cafe24 연동 도메인
- **cafe24_connections** — Cafe24 연결 (user_id, mall_id, access/refresh tokens, scopes)
- **cafe24_product_mappings** — 상품 매핑 (product_id, cafe24_product_id, sync_status, last_synced_at)

#### 3.1.9 SNS·피드 도메인
- **follows** — 팔로우
- **wishlists** — 찜
- **feed_items** — 피드 아이템
- **feed_likes** — 피드 좋아요

#### 3.1.10 R1 사입·입고·바코드
- **purchase_orders**, **purchase_order_items**
- **inbound_receipts**, **inbound_receipt_items**
- **barcodes**

---

## 4. API 엔드포인트 전체 목록

> `routes/api.php` 기반. prefix `/api` 적용.

### 4.1 인증 (Auth)
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| POST | /api/auth/login | AuthController@login | - |
| POST | /api/auth/logout | AuthController@logout | auth:sanctum |
| GET | /api/auth/me | AuthController@me | auth:sanctum |

### 4.2 브랜드 (Brands) — 공개 + 인증
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| GET | /api/brands | BrandPageController@index | 공개 |
| GET | /api/brands/{slug} | BrandPageController@show | 공개 |
| GET | /api/brands/{slug}/products | BrandPageController@products | 공개 |
| GET | /api/brands/{slug}/feed | BrandPageController@feed | 공개 |
| POST | /api/brands/{slug}/follow | BrandPageController@toggleFollow | auth:sanctum |
| PUT | /api/brands/me | BrandPageController@updateMine | auth:sanctum |

### 4.3 발주 (Purchase Orders)
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| GET | /api/purchase-orders | PurchaseOrderController@index | role:admin\|purchaser |
| GET | /api/purchase-orders/{id} | PurchaseOrderController@show | role:admin\|purchaser |
| POST | /api/purchase-orders | PurchaseOrderController@store | role:admin\|purchaser |
| PUT | /api/purchase-orders/{id} | PurchaseOrderController@update | role:admin\|purchaser |
| POST | /api/purchase-orders/{id}/cancel | PurchaseOrderController@cancel | role:admin\|purchaser |
| POST | /api/purchase-orders/{id}/status | PurchaseOrderController@updateStatus | role:admin\|purchaser |
| DELETE | /api/purchase-orders/{id} | PurchaseOrderController@destroy | role:admin |
| POST | /api/purchase-orders/{id}/approve | PurchaseOrderController@approve | role:admin |

### 4.4 입고 (Inbound Receipts)
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| GET | /api/inbound-receipts | InboundReceiptController@index | role:admin\|purchaser |
| GET | /api/inbound-receipts/{id} | InboundReceiptController@show | role:admin\|purchaser |
| POST | /api/inbound-receipts | InboundReceiptController@store | role:admin\|purchaser |
| PUT | /api/inbound-receipts/{id} | InboundReceiptController@update | role:admin\|purchaser |
| POST | /api/inbound-receipts/{id}/complete | InboundReceiptController@complete | role:admin\|purchaser |
| POST | /api/inbound-receipts/{id}/reject | InboundReceiptController@reject | role:admin |

### 4.5 바코드 (Barcodes)
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| GET | /api/barcodes | BarcodeController@index | role:admin\|purchaser |
| POST | /api/barcodes/generate | BarcodeController@generate | role:admin\|purchaser |
| POST | /api/barcodes/print-batch | BarcodeController@printBatch | role:admin\|purchaser |
| GET | /api/barcodes/{id} | BarcodeController@show | role:admin\|purchaser |
| PUT | /api/barcodes/{id}/status | BarcodeController@updateStatus | role:admin\|purchaser |

### 4.6 대시보드
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| GET | /api/dashboard/overview | DashboardController@overview | auth:sanctum |
| GET | /api/dashboard/stats | DashboardController@stats | role:admin |
| GET | /api/dashboard/purchasing/summary | PurchasingDashboardController@summary | role:admin |
| GET | /api/dashboard/purchasing/suppliers | PurchasingDashboardController@suppliers | role:admin |
| GET | /api/dashboard/purchasing/trend | PurchasingDashboardController@trend | role:admin |
| GET | /api/dashboard/purchasing/recent-orders | PurchasingDashboardController@recentOrders | role:admin |
| GET | /api/dashboard/purchasing/recent-inbounds | PurchasingDashboardController@recentInbounds | role:admin |
| GET | /api/dashboard/purchasing/alerts | PurchasingDashboardController@alerts | role:admin |

### 4.7 피드·팔로우·찜 (SNS)
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| GET | /api/feed | FeedController@index | auth:sanctum |
| GET | /api/feed/search | FeedController@search | auth:sanctum |
| GET | /api/feed/{id} | FeedController@show | auth:sanctum |
| POST | /api/feed | FeedController@store | auth:sanctum, role:wholesale\|admin |
| POST | /api/feed/{id}/like | FeedController@toggleLike | auth:sanctum |
| POST | /api/follows/{userId} | FollowController@follow | auth:sanctum |
| DELETE | /api/follows/{userId} | FollowController@unfollow | auth:sanctum |
| GET | /api/follows/{userId}/followers | FollowController@followers | auth:sanctum |
| GET | /api/follows/{userId}/following | FollowController@following | auth:sanctum |
| GET | /api/wishlists | WishlistController@index | auth:sanctum |
| POST | /api/wishlists/{productId} | WishlistController@store | auth:sanctum |
| POST | /api/wishlists/{productId}/toggle | WishlistController@toggle | auth:sanctum |
| DELETE | /api/wishlists/{productId} | WishlistController@destroy | auth:sanctum |

### 4.8 콘텐츠·미디어
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| POST | /api/contents | ContentController@store | role:wholesale\|admin |
| GET | /api/contents/mine | ContentController@mine | role:wholesale\|admin |
| GET | /api/contents/{id} | ContentController@show | auth:sanctum |
| PUT | /api/contents/{id} | ContentController@update | role:wholesale\|admin |
| DELETE | /api/contents/{id} | ContentController@destroy | role:wholesale\|admin |
| POST | /api/media/upload | MediaController@upload | role:wholesale\|admin |
| GET | /api/products/mine | ProductController@mine | role:wholesale\|admin |

### 4.9 Cafe24 연동
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| POST | /api/cafe24/connect | Cafe24Controller@connect | role:retail\|wholesale\|admin |
| GET | /api/cafe24/callback | Cafe24Controller@callback | - |
| GET | /api/cafe24/status | Cafe24Controller@status | role:retail\|wholesale\|admin |
| POST | /api/cafe24/products/push | Cafe24Controller@pushProducts | role:retail\|wholesale\|admin |
| PUT | /api/cafe24/products/{id} | Cafe24Controller@updateProduct | role:retail\|wholesale\|admin |
| DELETE | /api/cafe24/products/{id} | Cafe24Controller@deleteProduct | role:retail\|wholesale\|admin |
| GET | /api/cafe24/products | Cafe24Controller@listProducts | role:retail\|wholesale\|admin |

### 4.10 장바구니 (Cart) — 5 라우트
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| GET | /api/cart | CartController@index | auth:sanctum, role:retail |
| POST | /api/cart/items | CartController@addItem | auth:sanctum, role:retail |
| PUT | /api/cart/items/{id} | CartController@updateItem | auth:sanctum, role:retail |
| DELETE | /api/cart/items/{id} | CartController@removeItem | auth:sanctum, role:retail |
| DELETE | /api/cart | CartController@clear | auth:sanctum, role:retail |

### 4.11 주문 (Orders)
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| POST | /api/orders | OrderController@store | auth:sanctum, role:retail |
| GET | /api/orders | OrderController@index | auth:sanctum |
| GET | /api/orders/{id} | OrderController@show | auth:sanctum |
| GET | /api/orders/{id}/payment | PaymentController@orderPayment | auth:sanctum |
| PUT | /api/orders/{id}/status | OrderController@updateStatus | auth:sanctum |
| POST | /api/orders/{id}/cancel | OrderController@cancel | auth:sanctum |

### 4.12 배송 (Shipments) — R3-API-003
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| POST | /api/orders/{orderId}/shipment | ShipmentController@store | auth:sanctum |
| GET | /api/orders/{orderId}/shipment | ShipmentController@orderShipment | auth:sanctum |
| GET | /api/shipments/{id} | ShipmentController@show | auth:sanctum |
| PUT | /api/shipments/{id}/tracking | ShipmentController@updateTracking | auth:sanctum |
| PUT | /api/shipments/{id}/status | ShipmentController@updateStatus | auth:sanctum |
| GET | /api/shipments/{id}/tracking | ShipmentController@trackingInfo | auth:sanctum |

### 4.13 배송지 (Shipping Addresses)
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| GET | /api/shipping-addresses | ShippingAddressController@index | auth:sanctum |
| POST | /api/shipping-addresses | ShippingAddressController@store | auth:sanctum |
| PUT | /api/shipping-addresses/{id} | ShippingAddressController@update | auth:sanctum |
| DELETE | /api/shipping-addresses/{id} | ShippingAddressController@destroy | auth:sanctum |
| PUT | /api/shipping-addresses/{id}/default | ShippingAddressController@setDefault | auth:sanctum |

### 4.14 결제 (Payments)
| Method | URI | Controller | 비고 |
|--------|-----|------------|------|
| POST | /api/payments/prepare | PaymentController@prepare | auth:sanctum |
| POST | /api/payments/confirm | PaymentController@confirm | auth:sanctum |
| GET | /api/payments/{id} | PaymentController@show | auth:sanctum |
| POST | /api/payments/{id}/cancel | PaymentController@cancel | auth:sanctum |
| POST | /api/payments/webhook | PaymentController@webhook | 공개 (secret 검증) |

---

## 5. 프론트엔드 라우트 맵

> `find frontend/src/app -name "page.tsx"` 결과 기반.

### 5.1 공개·인증
| 경로 | 설명 |
|------|------|
| / | 홈 (피드) |
| /login | 로그인 |
| /register | 회원가입 |
| /feed | 피드 |
| /explore | 탐색 |
| /brands | 브랜드 목록 |
| /brand/[slug] | 브랜드 상세 |
| /retail/product/[id] | 상품 상세 |

### 5.2 소매 (Retail)
| 경로 | 설명 | 구현 버전 |
|------|------|----------|
| /retail/cart | 장바구니 | v2.2.0 |
| /retail/order/new | 주문 생성 | v2.2.0 |
| /retail/orders | 주문 목록 | v2.2.0 |
| /retail/orders/[id] | 주문 상세 | v2.2.0 |
| /retail/payment | 결제 (토스) | v2.4.0 |
| /retail/payment/success | 결제 성공 | v2.4.0 |
| /retail/payment/fail | 결제 실패 | v2.4.0 |
| /retail/mypage | 마이페이지 | - |

### 5.3 도매 (Wholesale)
| 경로 | 설명 | 구현 버전 |
|------|------|----------|
| /wholesale/dashboard | 도매 대시보드 | - |
| /wholesale/content | 콘텐츠 목록 | v1.8.0 |
| /wholesale/content/new | 콘텐츠 작성 | v1.8.0 |
| /wholesale/content/[id]/edit | 콘텐츠 수정 | v1.8.0 |
| /wholesale/orders | 주문 관리 | v2.2.0 |
| /wholesale/orders/[id] | 주문 상세 | v2.2.0 |

### 5.4 관리자 (Admin)
| 경로 | 설명 | 구현 버전 |
|------|------|----------|
| /admin/dashboard | 관리자 대시보드 | - |
| /admin/purchase | 사입 대시보드 | v1.7.0 |
| /admin/purchase/orders | 발주 목록 | v1.7.0 |
| /admin/purchase/[id] | 발주 상세 | v1.7.0 |
| /admin/purchase/receiving | 입고 목록 | v1.7.0 |
| /admin/purchase/receiving/[id] | 입고 상세 | v1.7.0 |
| /admin/purchase/barcode | 바코드 | v1.7.0 |
| /admin/purchasing | 사입 (별도) | - |

### 5.5 기타 역할
| 경로 | 설명 |
|------|------|
| /(md)/dashboard | MD 대시보드 |
| /(purchaser)/dashboard | 사입자 대시보드 |
| /outsource/dashboard | 외주 대시보드 |

---

## 6. 인증 & RBAC

### 6.1 인증 방식
- **Laravel Sanctum** (SPA + API 토큰)
- 로그인 → `POST /api/auth/login` → Bearer Token 발급
- 프론트엔드는 쿠키 기반 SPA 인증 또는 토큰 헤더

### 6.2 역할 (Roles)
| Role | 설명 | 주요 권한 |
|------|------|----------|
| admin | 시스템 관리자 | 전체 접근, 주문 상태 변경, 사용자 관리 |
| md | 상품 기획 (MD) | 상품 관리, 사입 관리 |
| purchaser | 사입 담당 | 사입 주문, 입고 |
| wholesale | 도매 업체 | 상품 등록, 콘텐츠, Cafe24 연동, 자기 주문 조회 |
| retail | 소매 업체 | 장바구니, 주문, 결제, 피드 |
| outsource | 외주 업체 | 제한적 접근 |

### 6.3 테스트 계정
| 이메일 | 역할 |
|--------|------|
| admin@newtalk.kr | admin |
| md@newtalk.kr | md |
| purchaser@newtalk.kr | purchaser |
| wholesale@newtalk.kr | wholesale |
| retail@newtalk.kr | retail |
| outsource@newtalk.kr | outsource |

> 비밀번호는 `.env.docker` 또는 시더 참조 (문서에 기록 금지).

---

## 7. 수익 모델 & 비즈니스 로직

| 수익원 | 금액/비율 | 구현 상태 |
|--------|----------|----------|
| SaaS 월정액 | 44,000 ~ 165,000원 | 설계 완료, 구현 예정 |
| 거래 수수료 (오픈) | 3 ~ 5% | 설계 완료 |
| 거래 수수료 (직접) | 1 ~ 2% | 설계 완료 |
| 콘텐츠 이용료 | 2,000원/건 | 설계 완료 |
| 배송 대행료 | 별도 | R3-API-003 완료 (배송 API) |
| 셀러 자동화 도구 | 별도 | R4 예정 |
| 스폰서드 카드 | 별도 | R4 예정 |
| 데이터 서비스 | 별도 | R4 예정 |

---

## 8. 배포 & 운영

### 8.1 배포 절차
1. `feature/*` 브랜치에서 개발
2. `develop` 으로 PR/merge
3. `main` 으로 merge → 버전 태그
4. SSH 접속 → `git pull` → `docker compose --env-file .env.docker up -d --build`
5. `docker compose exec app php artisan migrate` (필요 시)
6. V1 헬스 체크 (`curl http://114.207.244.86` → 200)

### 8.2 백업 규칙
- 파일 변경 전: `.bak.{YYYYMMDD_HHMMSS}` 복사
- DB 변경 전: `mysqldump` → `/srv/newtalk-v2/backups/`
- 마이그레이션 전: `php artisan migrate:status` 스냅샷

### 8.3 보호 시스템 (절대 수정 금지)
1. V1 소스 (/home/autoda/, /home/danharoo/)
2. V1 DB (autoda, 3306) — 읽기만 가능
3. V1 포트 (80, 443, 3306)
4. V1 Admin (114.207.244.87)
5. NAS image-auto (192.168.30.23:8100)
6. ShortFlow AI (:3001)

---

## 9. Git & 문서 동기화

### 9.1 리포지토리
| 리포 | URL | 용도 |
|------|-----|------|
| V2 소스 | git@github.com:moongoby/newtalk-v2-api-.git | Laravel + Next.js |
| project-docs | git@github.com:moongoby/project-docs.git | 공개 문서 동기화 |

### 9.2 브랜치 전략
main ← develop ← feature/

### 9.3 커밋 메시지 규칙
`[R{라운드}-{태스크}] 설명 (v{버전})` / `[DOCS] 문서 관련`

### 9.4 문서 동기화 흐름
1. 작업 완료 → 보고서 작성 (`docs/reports/`)
2. CONTEXT.md, CHANGELOG.md, HANDOVER.md 갱신
3. sync 스크립트 실행 또는 수동 복사 (architecture/, planning/ 포함)
4. project-docs 커밋·푸시
5. 민감 정보 grep 확인 (비밀번호 → [REDACTED])
6. 원격 HTTP 200 검증

---

## 10. 로드맵

### R2 (주 0-8) — ✅ 완료
프론트엔드 셋업, 인증 UI, 피드, 상품 상세, 브랜드 페이지, SNS API, AI 콘텐츠 API, Cafe24 연동

### R3 (주 8-16) — 🔄 진행 중
| 태스크 | 설명 | 상태 |
|--------|------|------|
| R3-API-001 | 사입 주문 API | ✅ v2.1.0 |
| R3-API-002 | 결제 연동 (Toss) | ✅ v2.3.0 |
| R3-FRONT-001 | 장바구니·주문 UI | ✅ v2.2.0 |
| R3-FRONT-002 | 결제 UI | ✅ v2.4.0 |
| R3-API-003 | 배송 API | ✅ v2.5.0 |
| R3-FRONT-003 | 배송 UI | ⬜ 대기 |
| R3-API-004 | DM API | ⬜ 대기 |
| R3-API-005 | Shorts API | ⬜ 대기 |
| R3-API-006 | 정산 API | ⬜ 대기 |

### R4 (주 16-24) — ⬜ 예정
AI 추천, 스토리, 라이브, 일본 크로스보더, YouTube 쇼핑, TikTok, 자동 마케팅

---

## 부록 A. 버전 히스토리 요약

| 버전 | 날짜 | 태스크 | Git SHA |
|------|------|--------|---------|
| 0.1.0 | 2026-02-21 | R0 인프라 | CONTEXT.md 참조 |
| 1.0.0 | 2026-02-22 | R1 API | 37ad7e4, 876f4b3, 555ee03, 67f0a64, be662c7 |
| 1.1.0 ~ 1.9.0 | 2026-02-23~25 | R2 프론트·API | 520353b, 870c007, ce541c5 등 |
| 2.0.0 | 2026-02-25 | R2-API-004 Cafe24 | 520353b |
| 2.1.0 | 2026-02-25 | R3-API-001 사입 주문 | 87cb07b |
| 2.2.0 | 2026-02-25 | R3-FRONT-001 장바구니·주문 UI | b798049 |
| 2.3.0 | 2026-02-25 | R3-API-002 결제 연동 | b798049 |
| 2.4.0 | 2026-02-25 | R3-FRONT-002 결제 UI | 서버 git log 참조 |
| 2.5.0 | 2026-02-25 | R3-API-003 배송 API | 서버 git log 참조 |

> 전체 버전 히스토리는 CHANGELOG.md 참조.
