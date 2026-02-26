# 뉴톡 V2 시스템 아키텍처

**버전**: 3.0.0  
**최종수정**: 2026-02-26 KST

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2026-02-23 | 초판 (8레이어, Docker, DB, Frontend 구조) |
| 2.0.0 | 2026-02-26 | R3 완료 반영 — DM, Shorts, 결제, 배송, 주문, 정산 도메인 추가 |
| 3.0.0 | 2026-02-26 | R4 반영 — 거래처, 스토리, AI 추천, 셀러 채널, 콘텐츠 파이프라인, SNS 자동게시, 위탁배송·드롭십 |

---

## 1. 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        클라이언트 레이어                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ 소매 웹/앱    │  │ 도매 웹/앱    │  │ 관리자/MD/사입 웹     │   │
│  │ (Next.js 16) │  │ (Next.js 16) │  │ (Next.js 16)        │   │
│  │ 피드·쇼츠·DM  │  │ 주문·DM·쇼츠  │  │ 사입·발주·입고·바코드 │   │
│  │ 장바구니·결제  │  │ 콘텐츠·배송   │  │ 정산·거래처·대시보드   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
└─────────┼──────────────────┼────────────────────┼───────────────┘
          │                  │                    │
          ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway (Nginx 1.25)                      │
│                     114.207.244.86:8080                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   Laravel 12 API (PHP 8.3-FPM)                   │
│  Auth(Sanctum)  Product  Purchase  Dashboard  Social(피드·DM·쇼츠) │
│  Cart·Order·Payment·Shipment  Brand·Content  Cafe24  Trade·Story  │
│  Settlement  AI추천  Channel  ContentPipeline  SNS·Dropship       │
└──────┬───────────────┬───────────────┬──────────────────────────┘
       │               │               │
       ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────────────┐
│ MySQL 8.0  │  │ Redis 7    │  │ NAS (image-auto)   │
│ :3307      │  │ :6380      │  │ 192.168.30.23:8100 │
│ newtalk_v2 │  │ 캐시/세션   │  └────────────────────┘
└────────────┘  └────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 외부: 카페24, 토스페이먼츠, (향후) 사방넷, Meta, TikTok, YouTube,  │
│       ShortFlow AI, Photoroom                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Docker Compose (5 서비스)

| 서비스 | 이미지/스택 | 포트 | 비고 |
|--------|-------------|------|------|
| app | PHP 8.3-FPM (Laravel 12) | — | 웹루트 /var/www/html |
| nginx | 1.25-alpine | :8080 | API 역방향 프록시 |
| db | MySQL 8.0 | :3307 | newtalk_v2 |
| redis | Redis 7 | :6380 | 캐시·세션 |
| frontend | Node 20-alpine (Next.js 16) | :3000 | SPA |

---

## 3. 데이터베이스 스키마 (90+ 테이블)

### R1 (47+ 테이블)
- **인증·역할**: users, roles, permissions, model_has_roles, model_has_permissions, role_has_permissions, personal_access_tokens
- **상품**: products, product_options, product_images, product_categories, categories
- **도매**: wholesale_profiles
- **사입**: purchase_orders, purchase_order_items, inbound_receipts, inbound_receipt_items, barcodes

### R2 추가
- **SNS**: follows, wishlists, feed_items, feed_likes
- **브랜드·콘텐츠**: brand_pages, contents, contents_media, contents_product_tags
- **연동**: cafe24_connections, cafe24_product_mappings

### R3 추가
- **주문·장바구니**: carts, cart_items
- **주문**: orders(확장), order_items
- **결제**: payments, payment_logs
- **배송**: shipments, shipment_logs, shipping_addresses
- **DM**: dm_conversations(conversations), dm_participants(conversation_participants), dm_messages(messages), message_reads
- **쇼츠**: shorts, short_product_tags, short_likes, short_comments, short_views
- **정산**: settlements, settlement_items, settlement_logs

### R4 추가
- **거래처**: trade_applications, trade_partnerships, trade_prices
- **스토리**: stories, story_views
- **AI 추천**: user_interests, product_scores, trend_snapshots
- **셀러 채널**: channel_connections, channel_product_mappings
- **콘텐츠 파이프라인**: content_pipeline_jobs, pipeline_logs, pipeline_media
- **SNS 자동게시**: sns_connections, sns_posts, sns_post_analytics
- **위탁배송·드롭십**: dropship_orders, return_requests, fulfillment_tasks

주요 관계: users ↔ carts ↔ cart_items ↔ products; orders ↔ order_items ↔ payments; orders ↔ shipments; conversations ↔ participants ↔ messages; shorts ↔ short_product_tags, short_likes, short_comments; trade_partnerships ↔ trade_prices; stories ↔ story_views; content_pipeline_jobs ↔ pipeline_logs, pipeline_media.

---

## 4. 인증 & RBAC

- **Laravel Sanctum** + **Spatie Permission**
- **6 역할**: admin, md, purchaser, wholesale, retail, outsource
- **로그인**: POST /api/auth/login → Bearer token 발급
- API 요청: Authorization: Bearer {token}, 역할별 미들웨어 적용

---

## 5. API 엔드포인트 전체 목록 (130+ EP)

(routes/api.php 기준, prefix /api)

### R1
- **인증**: 3 — POST auth/login, POST auth/logout, GET auth/me
- **상품/브랜드**: 6 — GET brands, brands/{slug}, brands/{slug}/products, brands/{slug}/feed, POST follow, PUT brands/me
- **발주**: 8 — GET/POST/PUT purchase-orders, GET/PUT purchase-orders/{id}, cancel, status, DELETE, approve
- **입고**: 6 — GET/POST/PUT inbound-receipts, GET/PUT inbound-receipts/{id}, complete, reject
- **바코드**: 5 — GET barcodes, POST generate, POST print-batch, GET/PUT barcodes/{id}
- **대시보드**: 8 — GET dashboard/overview, stats, purchasing/summary, suppliers, trend, recent-orders, recent-inbounds, alerts

### R2
- **피드**: 7 — GET feed, feed/search, feed/{id}, POST feed, POST feed/{id}/like + follows/wishlists
- **팔로우**: 4 — POST/DELETE follows/{userId}, GET followers, GET following
- **찜**: 3 — GET wishlists, POST wishlists/{productId}, POST toggle, DELETE
- **브랜드**: 6 — (공개 4 + 인증 follow/me)
- **콘텐츠**: 6 — POST/GET contents, GET mine, GET/PUT/DELETE contents/{id}
- **미디어**: 1 — POST media/upload
- **카페24**: 7 — connect, callback, status, products/push, PUT/DELETE/GET products

### R3
- **장바구니**: 5 — GET cart, POST cart/items, PUT/DELETE cart/items/{id}, DELETE cart
- **주문**: 5 — POST orders, GET orders, GET orders/{id}, GET orders/{id}/payment, PUT status, POST cancel
- **결제**: 6 — POST prepare, POST confirm, GET payments/{id}, POST cancel, GET orderPayment, POST webhook(공개)
- **배송**: 6 — POST/GET orders/{orderId}/shipment, GET/PUT shipments/{id}, PUT tracking, PUT status, GET tracking
- **배송지**: 5 — GET/POST/PUT/DELETE shipping-addresses, PUT default
- **DM 대화**: 6 — GET/POST conversations, GET/PUT/DELETE conversations/{id}, mute, pin, leave
- **DM 메시지**: 4 — GET/POST conversations/{id}/messages, POST read, DELETE messages/{id}
- **쇼츠**: 11 — GET shorts(피드), GET shorts/{id}, GET shorts/mine, POST shorts, PUT/DELETE shorts/{id}, POST like, POST view, GET comments, POST addComment, DELETE comments/{id}
- **정산**: 9 — preview, store, index, show, updateStatus, recalculate, updateBankInfo, updateItemStatus, addMemo

### R4
- **거래처**: 14 — apply, getApplications, getApplicationDetail, approve, reject, getPartners, getPartnerDetail, setTradePrice, getTradePrice, bulkSetTradePrices, removeTradePrice, suspend, terminate, updateCommissionRate
- **스토리**: 10 — store, feed, userStories, mine, show, destroy, recordView, react, viewers, toggleHighlight
- **AI 추천**: 피드·추천 엔진 엔드포인트
- **셀러 채널**: channel_connections, channel_product_mappings CRUD
- **콘텐츠 파이프라인**: pipeline jobs·logs·media API
- **SNS 자동게시**: sns_connections, sns_posts 연동 (스텁)
- **위탁배송·드롭십**: dropship_orders, return_requests, fulfillment_tasks API

**총 엔드포인트**: 130개 이상 (공개·인증·역할별 그룹 포함).

상세 라우트는 `routes/api.php` 및 각 컨트롤러 참조. 역할별 미들웨어로 retail/wholesale/admin 등 접근 제어.

---

## 6. Frontend 라우트 맵

### 공개·인증
- /, /login, /register, /feed, /explore, /brands, /brand/[slug], /retail/product/[id]

### 소매 (retail)
- /, /feed, /retail/product/[id], /brand/[slug], /brands, /retail/cart, /retail/order/new, /retail/orders, /retail/orders/[id], /retail/payment, /retail/payment/success, /retail/payment/fail, /retail/addresses, /retail/messages, /retail/messages/[id], /retail/shorts, /retail/shorts/[id], /retail/trade, /retail/trade/apply, /retail/trade/applications/[id], /retail/trade/partners/[id]

### 도매 (wholesale)
- /wholesale/dashboard, /wholesale/content, /wholesale/content/new, /wholesale/content/[id]/edit, /wholesale/orders, /wholesale/orders/[id], /wholesale/messages, /wholesale/messages/[id], /wholesale/shorts, /wholesale/shorts/new, /wholesale/shorts/[id]/edit, /wholesale/trade, /wholesale/trade/applications/[id], /wholesale/trade/partners/[id], /wholesale/settlements, /wholesale/settlements/[id]

### 관리자 (admin)
- /admin/dashboard, /admin/purchase, /admin/purchase/orders, /admin/purchase/[id], /admin/purchase/receiving, /admin/purchase/receiving/[id], /admin/purchase/barcode, /admin/trade, /admin/trade/applications/[id], /admin/trade/partners/[id], /admin/settlements, /admin/settlements/[id]

### MD / 사입자 (purchaser)
- /(md)/dashboard, /(purchaser)/dashboard

---

## 7. 비즈니스 모델

| 구분 | 내용 |
|------|------|
| SaaS 월정액 | 44,000 ~ 165,000원 (브랜드몰 구독) |
| 거래 수수료 | 오픈 3~5%, 직거래 1~2% |
| 콘텐츠 | 건당 2,000원 등 |
| 배송 | 위탁배송 수수료 |
| 스튜디오 | 베이직(무료/10만) → 프로(44만) → 프리미엄(110~165만) |
| 기타 | 셀러 도구 초과 건당, 스폰서드 카드, 데이터 서비스 |

---

## 8. 배포 프로세스

1. feature 브랜치 개발 → main(또는 develop) 머지
2. 태그 생성 (필요 시)
3. 서버 SSH 접속 → cd /srv/newtalk-v2 → git pull origin main
4. docker compose --env-file .env.docker up -d --build
5. php artisan migrate (필요 시)
6. V1 헬스 확인: curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86 → 200

---

## 9. 외부 서비스 연동

| 서비스 | 용도 | 상태 |
|--------|------|------|
| 카페24 | 쇼핑몰 상품 연동 | R2-API-004 연동 완료 |
| 토스페이먼츠 | 결제 | R3-API-002 연동 완료 |
| 사방넷 | 배송 | 향후 |
| Meta / TikTok / YouTube | SNS·쇼핑 | R4 스텁·향후 |
| ShortFlow AI | 쇼츠 | 별도 진행 |
| Photoroom | 이미지 | 향후 |
| NAS | 이미지 스토리지 | image-auto :8100 |

---

## 10. 로드맵 현황

- **R0~R1**: 완료 (인프라, 47+ 테이블, Sanctum, RBAC, 사입 API)
- **R2**: 완료 (피드, 브랜드, 콘텐츠, 카페24)
- **R3**: 완료 (사입 주문, 결제, 배송, DM, 쇼츠, 정산)
- **R4**: 진행 중 (거래처, 스토리, AI 추천, 셀러 채널, 콘텐츠 파이프라인, SNS 자동게시, 위탁배송·드롭십)
- **R5**: 대기 (일본 크로스보더, 라이브 B2B)

---

## 부록 A — 버전 히스토리

| 버전 | 날짜 | 태스크 |
|------|------|--------|
| v0.1.0 | 2026-02-21 | R0 인프라 |
| v1.0.0 | 2026-02-22 | R1 API |
| v1.1.0 ~ v1.9.0 | 2026-02-23~25 | R2 프론트·API |
| v2.0.0 | 2026-02-25 | R2-API-004 Cafe24 |
| v2.1.0 | 2026-02-25 | R3-API-001 사입 주문 |
| v2.2.0 ~ v2.12.0 | 2026-02-25~26 | R3 주문·결제·배송·DM·쇼츠·정산 |
| v3.1.0 | 2026-02-26 | R4-API-001 거래처 |
| v3.2.0 | 2026-02-26 | R4-API-002 스토리 |
| v3.3.0 ~ v3.10.0 | 2026-02-26 | R4 AI·채널·콘텐츠·SNS·드롭십 |
| v3.11.0 | 2026-02-26 | DOCS-FIX-008 4대 문서 정합성 복구 |

(서버 푸시 후 `git log -1 --pretty=%h` 로 필요 시 SHA 갱신. 비밀번호·평문 인증정보 문서 포함 금지.)
