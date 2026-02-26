# 뉴톡 V2 시스템 아키텍처

**버전**: 1.0.0
**최종수정**: 2026-02-23

---

## 변경 이력
| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2026-02-23 | 초판 (8레이어, Docker, DB, Frontend 구조) |

---

## 1. 전체 구조

```
클라이언트 (Next.js 16)
  ├── 소매 웹/앱 (모바일 퍼스트)
  ├── 도매 웹/앱 (데스크톱+모바일)
  └── 관리자/MD/사입 웹 (데스크톱)
       │
       ▼
API Gateway (Nginx :8080)
       │
       ▼
Laravel 12 API (PHP 8.3-FPM)
  ├── Auth (Sanctum+Spatie RBAC)
  ├── Product CRUD
  ├── Purchase Order / Receipt / Barcode
  ├── Dashboard
  ├── Social Engine (피드/팔로우/찜/DM)
  ├── Marketplace (주문/결제/정산)
  ├── Brand Page
  ├── Content Factory
  ├── Seller Expansion (다채널/SNS/마케팅)
  ├── AI Intelligence (추천/트렌드)
  └── V1 Migration Commands
       │
   ┌───┼───────────┐
   ▼   ▼           ▼
MySQL  Redis      NAS (Synology)
:3307  :6380      192.168.30.23:8100
                   │
                   ▼
              외부 서비스
              ├── 카페24 API
              ├── 사방넷 API
              ├── Meta Graph API
              ├── TikTok API
              ├── YouTube Data API
              ├── ShortFlow AI
              └── Photoroom API
```

## 2. Docker Compose

### 현재 (R1+R2)
| 서비스 | 이미지 | 포트 | 역할 |
|--------|--------|------|------|
| app | PHP 8.3-FPM | - | Laravel API |
| nginx | 1.25-alpine | 8080 | Reverse proxy |
| db | MySQL 8.0 | 3307 | 데이터베이스 |
| redis | Redis 7 | 6380 | 캐시/세션 |
| frontend | Node 20-alpine | 3000 | Next.js (R2 추가) |

### V1 연동 (읽기 전용)
| 대상 | 포트 | 용도 |
|------|------|------|
| V1 MySQL | 3306 | 마이그레이션 소스 |
| V1 웹 | 80 | 보호 확인용 |

## 3. 데이터베이스

### R1 완료 (47+ 테이블)
users, roles, permissions, products, product_options, product_images,
product_categories, categories, wholesale_profiles,
purchase_orders, purchase_order_items,
inbound_receipts, inbound_receipt_items,
barcodes, personal_access_tokens 등

### R2 추가 예정
follows, wishlists, brand_pages, feed_items, stories,
direct_messages, channel_connections, sns_posts

### R3 추가 예정
retail_orders, retail_order_items, cart_items, payments,
settlements, trade_applications, dropship_orders, content_pipeline_jobs

## 4. 인증
POST /api/auth/login → Sanctum 토큰 → Authorization: Bearer {token}
→ Spatie 역할: admin | md | purchaser | wholesale | retail | outsource

## 5. Frontend 구조
Next.js 16 App Router, Route Groups:
(auth)/ (retail)/ (wholesale)/ (admin)/ (md)/ (purchaser)/

### 주요 라우트 (R4-FRONT-001 포함)
- **소매**: /retail/feed, /retail/explore, /retail/cart, /retail/trade, /retail/trade/apply, /retail/stories, /retail/mypage, /retail/orders, /retail/messages, /retail/shorts, /brand/[slug]
- **도매**: /wholesale/dashboard, /wholesale/orders, /wholesale/trade, /wholesale/trade/applications/[id], /wholesale/trade/partners/[id], /wholesale/stories, /wholesale/stories/new, /wholesale/content, /wholesale/messages, /wholesale/shorts
- **관리자**: /admin/dashboard, /admin/trade, /admin/purchase, /admin/settlement, /admin/settings

## 6. API 엔드포인트

### R1 완료
/api/auth/, /api/products/, /api/purchase-orders/,
/api/inbound-receipts/, /api/barcodes/, /api/dashboard/

### R2 신규
/api/feed/, /api/follows/, /api/wishlists/,
/api/brands/, /api/content/, /api/cafe24/

### R3 신규
/api/retail-orders/, /api/cart/, /api/payments/,
/api/settlements/, /api/trade-applications/,
/api/channels/, /api/sns-posts/, /api/dropship/
