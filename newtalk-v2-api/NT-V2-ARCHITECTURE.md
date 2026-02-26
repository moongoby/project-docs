# 뉴톡 V2 시스템 아키텍처

**버전**: 2.0  
**작성일**: 2026-02-22  
**최종갱신**: 2026-02-26 (R3 DM·결제·배송·쇼츠 반영)

## 1. 전체 구조도 (텍스트)

```
┌─────────────────────────────────────────────────────────────────┐
│                        클라이언트 레이어                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ 소매 웹/앱    │  │ 도매 웹/앱    │  │ 관리자/MD/사입 웹     │   │
│  │ (Next.js 16) │  │ (Next.js 16) │  │ (Next.js 16)        │   │
│  │ 모바일 퍼스트  │  │ 데스크톱+모바일│  │ 데스크톱 퍼스트       │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
└─────────┼──────────────────┼────────────────────┼───────────────┘
          │                  │                    │
          ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway (Nginx)                          │
│                     114.207.244.86:8080                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   Laravel 12 API 서버 (PHP 8.3-FPM)              │
│                                                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ │
│  │ Auth    │ │ Product │ │Purchase │ │Dashboard│ │ Social   │ │
│  │(Sanctum)│ │ CRUD    │ │Order/   │ │ API    │ │ Engine   │ │
│  │+ RBAC  │ │ API     │ │Receipt  │ │        │ │(피드/팔로│ │
│  │(Spatie)│ │         │ │/Barcode │ │        │ │우/찜/DM/쇼츠) │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └──────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────────────┐ │
│  │Marketplace│ │Brand   │ │Content │ │ Seller Expansion     │ │
│  │(주문/결제│ │Page    │ │Factory │ │ (다채널/SNS/자동마케팅)│ │
│  │/배송/정산)│ │API     │ │API     │ │                      │ │
│  └─────────┘ └─────────┘ └─────────┘ └──────────────────────┘ │
│  ┌─────────────────────┐ ┌─────────────────────────────────┐   │
│  │ V1 Migration        │ │ AI Intelligence                 │   │
│  │ Commands            │ │ (추천/트렌드/사입예측)            │   │
│  └─────────────────────┘ └─────────────────────────────────┘   │
└──────┬───────────────┬───────────────┬──────────────────────────┘
       │               │               │
       ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────────────┐
│ MySQL 8.0  │  │ Redis 7    │  │ NAS (Synology)     │
│ :3307      │  │ :6380      │  │ 192.168.30.23:8100 │
│ newtalk_v2 │  │ 캐시/세션   │  │ image-auto 컨테이너 │
└────────────┘  └────────────┘  │ 이미지 처리 파이프라인│
                                └────────────────────┘
                                         │
                                         ▼
                                ┌────────────────────┐
                                │ 외부 서비스 연동     │
                                │ - 카페24 API        │
                                │ - 사방넷 API        │
                                │ - Meta Graph API    │
                                │ - TikTok API        │
                                │ - YouTube Data API  │
                                │ - ShortFlow AI      │
                                │ - Photoroom API     │
                                └────────────────────┘
```

## 2. Docker Compose 구성

### 현재 (R1 완료)
```yaml
services:
  app:     # PHP 8.3-FPM + Laravel 12
  nginx:   # 1.25-alpine, :8080
  db:      # MySQL 8.0, :3307
  redis:   # Redis 7, :6380
```

### R2 추가 예정
```yaml
services:
  # ... 기존 유지
  frontend:  # Next.js 16, :3000
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://nginx:8080/api
    depends_on: [nginx]
```

## 3. 데이터베이스 구조

### R1 완료 테이블 (47+)
- users, roles, permissions, model_has_roles, model_has_permissions, role_has_permissions
- products, product_options, product_images, product_categories, categories
- wholesale_profiles
- purchase_orders, purchase_order_items
- inbound_receipts, inbound_receipt_items
- barcodes
- personal_access_tokens
- 기타 38개 마이그레이션 테이블

### R2 완료 테이블
- follows, wishlists, feed_items, feed_likes
- brand_pages, product_images (BrandPage)
- contents, contents_media, contents_product_tags
- cafe24_connections, cafe24_product_mappings

### R3 완료 테이블
- **사입·주문**: carts, cart_items, orders, order_items
- **결제**: payments, payment_logs (orders.payment_status, paid_at)
- **배송**: shipments, shipment_logs, shipping_addresses
- **DM**: conversations, conversation_participants, messages, message_reads
- **쇼츠**: shorts, short_product_tags, short_likes, short_comments, short_views

### R3 추가 예정 테이블 (미구현)
- settlements, trade_applications, dropship_orders, content_pipeline_jobs

## 4. 인증 흐름

```
소매/도매 앱 → POST /api/auth/login → Sanctum 토큰 발급
→ 모든 API 요청 시 Authorization: Bearer {token}
→ Spatie 미들웨어로 역할 검증 (admin|md|purchaser|wholesale|retail|outsource)
```

## 5. 프론트엔드 구조

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/             # 로그인/회원가입 (공통)
│   │   ├── login/
│   │   └── register/
│   ├── (retail)/           # 소매 셀러 영역
│   │   ├── feed/           # SN-001 홈 피드
│   │   ├── explore/        # SN-002 탐색
│   │   ├── shorts/         # SN-003 쇼츠
│   │   ├── brand/[slug]/   # SN-004 브랜드 페이지
│   │   ├── product/[id]/   # SN-005 상품 상세
│   │   ├── cart/           # SN-006 장바구니
│   │   ├── orders/         # SN-007 주문 내역
│   │   ├── messages/       # SN-008 DM
│   │   ├── mypage/         # SN-009 마이페이지
│   │   ├── bulk-register/  # SN-010 대량 등록
│   │   ├── channels/       # SN-011 채널 관리
│   │   ├── auto-post/      # SN-012 자동 게시
│   │   ├── analytics/      # SN-013 마케팅 성과
│   │   └── bulk-channel/   # SN-014 대량 채널 등록
│   ├── (wholesale)/        # 도매 영역
│   │   ├── dashboard/      # WH-001
│   │   ├── brand-page/     # WH-002
│   │   ├── products/       # WH-003
│   │   ├── orders/         # WH-004
│   │   ├── partners/       # WH-005
│   │   ├── analytics/      # WH-006
│   │   ├── content/        # WH-007, WH-010, WH-011
│   │   └── plan/           # WH-012
│   ├── (admin)/            # 관리자 영역
│   │   ├── dashboard/      # ADM-001
│   │   ├── products/       # ADM-002, 003
│   │   ├── purchasing/     # ADM-004~008, 015
│   │   ├── members/        # ADM-010
│   │   ├── marketplace/   # ADM-021
│   │   ├── content/        # ADM-022
│   │   ├── feed/           # ADM-020
│   │   ├── settlement/     # ADM-024
│   │   └── settings/       # ADM-018
│   ├── (md)/               # MD 영역
│   └── (purchaser)/        # 사입자 영역
├── components/
│   ├── ui/                 # shadcn/ui 컴포넌트
│   ├── layout/             # 레이아웃 (사이드바, 헤더, 탭바)
│   ├── feed/               # 피드 카드, 스토리 등
│   ├── product/            # 상품 관련
│   └── common/             # 공통 (모달, 토스트 등)
├── lib/
│   ├── api.ts              # API 클라이언트 (fetch + Sanctum 토큰)
│   ├── auth.ts             # 인증 유틸
│   └── utils.ts            # 공통 유틸
├── stores/
│   ├── auth-store.ts       # Zustand 인증 상태
│   ├── cart-store.ts       # 장바구니
│   └── feed-store.ts       # 피드 상태
├── hooks/
│   ├── use-auth.ts         # TanStack Query 인증
│   ├── use-products.ts     # 상품 쿼리
│   └── use-feed.ts         # 피드 쿼리
├── types/
│   ├── api.ts              # API 응답 타입
│   ├── product.ts          # 상품 타입
│   └── user.ts             # 사용자 타입
├── tailwind.config.ts
├── next.config.ts
├── package.json
├── tsconfig.json
└── Dockerfile
```

## 6. API 엔드포인트 구조

### R1 완료
```
/api/auth/          - 인증
/api/products/      - 상품 CRUD
/api/purchase-orders/ - 발주
/api/inbound-receipts/ - 입고
/api/barcodes/      - 바코드
/api/dashboard/     - 대시보드
```

### R2 완료
```
/api/feed/          - 피드 조회
/api/follows/       - 팔로우/언팔로우
/api/wishlists/     - 찜
/api/brands/        - 브랜드 페이지
/api/contents/      - 콘텐츠 CRUD
/api/cafe24/        - 카페24 연동
```

### R3 완료
```
/api/cart/          - 장바구니 (CRUD, 비우기)
/api/orders/        - 주문 (생성/목록/상세/상태변경/취소)
/api/payments/      - 결제 (토스페이먼츠 prepare/confirm/cancel/webhook)
/api/orders/{id}/shipment, /api/shipments/, /api/shipping-addresses/ - 배송·배송지
/api/conversations/ - DM (대화 목록/생성/상세/메시지/읽음)
/api/shorts/        - 쇼츠 (피드/상세/업로드/좋아요/댓글/조회)
```
