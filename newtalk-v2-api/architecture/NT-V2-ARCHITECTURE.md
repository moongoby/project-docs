# 뉴톡 V2 시스템 아키텍처

**버전**: 2.0.0  
**최종수정**: 2026-02-26 KST

## 변경 이력
| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2026-02-23 | 초판 (8레이어, Docker, DB, Frontend 구조) |
| 2.0.0 | 2026-02-26 | R3 완료 반영 — DM, Shorts, 결제, 배송, 주문 도메인 추가, 전체 API/DB/프론트 갱신 |

---

## 1. 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        클라이언트 레이어                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ 소매 웹/앱    │  │ 도매 웹/앱    │  │ 관리자/MD/사입 웹     │   │
│  │ (Next.js 16) │  │ (Next.js 16) │  │ (Next.js 16)        │   │
│  │ 피드·쇼츠·DM  │  │ 주문·DM·쇼츠  │  │ 사입·발주·입고·바코드 │   │
│  │ 장바구니·결제  │  │ 콘텐츠·배송   │  │ 대시보드             │   │
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
│  Cart·Order·Payment·Shipment  Brand·Content  Cafe24              │
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

## 3. 데이터베이스 스키마 (60+ 테이블)

### R1 테이블 (47+)
- **인증·역할**: users, roles, permissions, model_has_roles, model_has_permissions, role_has_permissions, personal_access_tokens
- **상품**: products, product_options, product_images, product_categories, categories
- **도매**: wholesale_profiles
- **사입**: purchase_orders, purchase_order_items, inbound_receipts, inbound_receipt_items, barcodes

### R2 추가 테이블
- **SNS**: follows, wishlists, feed_items, feed_likes
- **브랜드·콘텐츠**: brand_pages, contents, contents_media, contents_product_tags
- **연동**: cafe24_connections, cafe24_product_mappings

### R3 추가 테이블
- **주문·장바구니**: carts (status, note, unique user_id+status), cart_items
- **주문**: orders (buyer_id, seller_id, order_number NT-YYYYMMDD-XXXXX, payment_status, paid_at), order_items (스냅샷)
- **결제**: payments (payment_key, method, status, amount), payment_logs
- **배송**: shipments (seller_id, buyer_id, type, tracking_company, tracking_number), shipment_logs, shipping_addresses
- **DM**: conversations (type, last_message_id/at), conversation_participants, messages (type text/image/product/order/system), message_reads
- **쇼츠**: shorts (video_url, status, visibility, view_count), short_product_tags, short_likes, short_comments, short_views

주요 관계: users ↔ carts ↔ cart_items ↔ products; orders ↔ order_items; orders ↔ payments ↔ payment_logs; orders ↔ shipments ↔ shipment_logs; conversations ↔ conversation_participants ↔ messages ↔ message_reads; shorts ↔ short_product_tags, short_likes, short_comments, short_views.

---

## 4. 인증 & RBAC

- **Laravel Sanctum** + **Spatie Permission**
- **6 역할**: admin, md, purchaser, wholesale, retail, outsource
- **로그인**: POST /api/auth/login → Bearer token 발급
- API 요청: Authorization: Bearer {token}, 역할별 미들웨어 적용

---

## 5. API 엔드포인트 전체 목록

(routes/api.php 기준, prefix /api)

### R1
- **인증**: 3 — POST auth/login, POST auth/logout, GET auth/me
- **상품**: (Brand/Product 경유) 6 — GET brands, brands/{slug}, brands/{slug}/products, brands/{slug}/feed, POST follow, PUT brands/me
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

**총 엔드포인트 수**: 100개 이상 (공개·인증·역할별 그룹 포함).

---

## 6. Frontend 라우트 맵

(Next.js App Router 그룹별)

### 공개·인증
- /, /login, /register, /feed, /explore, /brands, /brand/[slug], /retail/product/[id]

### 소매 (retail)
- /, /feed, /retail/product/[id], /brand/[slug], /brands, /retail/cart, /retail/order/new, /retail/orders, /retail/orders/[id], /retail/payment, /retail/payment/success, /retail/payment/fail, /retail/addresses, /retail/messages, /retail/messages/[id], /retail/shorts, /retail/shorts/[id]

### 도매 (wholesale)
- /wholesale/dashboard, /wholesale/content, /wholesale/content/new, /wholesale/content/[id]/edit, /wholesale/orders, /wholesale/orders/[id], /wholesale/messages, /wholesale/messages/[id], /wholesale/shorts, /wholesale/shorts/new, /wholesale/shorts/[id]/edit

### 관리자 (admin)
- /admin/dashboard, /admin/purchase, /admin/purchase/orders, /admin/purchase/[id], /admin/purchase/receiving, /admin/purchase/receiving/[id], /admin/purchase/barcode

### MD / 사입자 (purchaser)
- /(md)/dashboard, /(purchaser)/dashboard

---

## 7. 비즈니스 모델

(인계서·기획서 수익모델 반영)

| 구분 | 내용 |
|------|------|
| SaaS 월정액 | 44,000 ~ 165,000원 (브랜드몰 구독) |
| 거래 수수료 | 오픈 3~5%, 직거래 1~2% |
| 콘텐츠 | 건당 2,000원 등 |
| 배송 | 위탁배송 수수료 |
| 스튜디오 | 베이직(무료/10만) → 프로(44만) → 프리미엄(110~165만) |
| 기타 | 셀러 도구 초과 건당, 스폰서드 카드, 데이터 서비스 (R4 예정) |

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
| Meta / TikTok / YouTube | SNS·쇼핑 | 향후 |
| ShortFlow AI | 쇼츠 | 별도 진행 |
| Photoroom | 이미지 | 향후 |

---

## 10. 로드맵

- **R2**: 완료 (피드, 브랜드, 콘텐츠, 카페24)
- **R3**: 진행 중 — 사입 주문·결제·배송·DM·Shorts API 완료, Shorts UI·정산 미착수
- **R4**: 계획 (AI 추천, 스토리, 라이브, 일본 확대, 유튜브/틱톡 연동)

---

## 부록 A — 버전 히스토리

| 버전 | 날짜 | 태스크 | Git SHA |
|------|------|--------|---------|
| v0.1.0 | 2026-02-21 | R0 인프라 | — |
| v1.0.0 | 2026-02-22 | R1 API | 37ad7e4, 876f4b3, 555ee03, 67f0a64, be662c7 |
| v1.1.0 ~ v1.9.0 | 2026-02-23~25 | R2 프론트·API | 520353b, 870c007, ce541c5 등 |
| v2.0.0 | 2026-02-25 | R2-API-004 Cafe24 | 520353b |
| v2.1.0 | 2026-02-25 | R3-API-001 사입 주문 | 87cb07b |
| v2.2.0 | 2026-02-25 | R3-FRONT-001 장바구니·주문 UI | b798049 |
| v2.3.0 | 2026-02-25 | R3-API-002 결제 연동 | b798049 |
| v2.4.0 | 2026-02-25 | R3-FRONT-002 결제 UI | 0000000 |
| v2.5.0 | 2026-02-25 | R3-API-003 배송 API | 0000000 |
| v2.6.0 | 2026-02-25 | R3-FRONT-003 배송 UI | 0000000 |
| v2.7.0 | 2026-02-26 | R3-API-004 DM API | 0000000 |
| v2.8.0 | 2026-02-26 | R3-FRONT-004 DM UI | — |
| v2.9.0 | 2026-02-26 | R3-API-005 Shorts API | — |

> 서버 푸시 후 `git log -1 --pretty=%h` 로 0000000 을 실제 7자리 SHA로 교체 권장.
