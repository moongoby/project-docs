# 뉴톡 V2 변경 이력 (CHANGELOG)

모든 주요 변경 사항을 기록합니다. [Semantic Versioning](https://semver.org/) 준수.

---

## [Unreleased]

## [2.1.0] - 2026-02-25
### Added (R3-API-001 사입 주문 API)
- **carts** 테이블: status(active/merged/ordered/abandoned), note, softDeletes, unique(user_id, status). Cart::getOrCreate(userId), scopeActive.
- **cart_items**: 기존 유지, CartItem::getTotalPriceAttribute.
- **orders** (기존+R3): buyer_id, seller_id, shipping_*, cancelled_at/reason, confirmed_at, shipped_at, delivered_at, tracking_number, tracking_company. order_number 형식 NT-YYYYMMDD-XXXXX(5자리). Order::canCancel().
- **order_items**: product_name, option_name, subtotal (기존 R3 컬럼).
- CartController: GET/POST/PUT/DELETE cart, DELETE cart/items/{id}, DELETE /cart(clear). addItem(product_option_id, quantity 1~9999), updateItem(quantity 0이면 삭제).
- OrderController: store(cart_id 또는 item_ids, shipping_* 필수), index(status, date_from, date_to), show, updateStatus(소매 cancel만/도매 confirmed·preparing·shipped/관리자 전체+refunded, shipped 시 tracking_* 필수), cancel(cancel_reason 필수).
- 라우트: auth:sanctum 내 role:retail → cart 5개, orders 5개(store, index, show, updateStatus, cancel). 엔드포인트 9개.

## [2.0.0] - 2026-02-25
### Added (R2-API-004 카페24 API 연동)
- **cafe24_connections** 테이블: user_id, mall_id(unique per user), client_id, client_secret, access_token, refresh_token, token_expires_at, scopes, is_active
- **cafe24_product_mappings** 테이블: user_id, product_id, cafe24_product_no, cafe24_mall_id, sync_status(pending,synced,failed,deleted), last_synced_at, error_message, unique(user_id, product_id, cafe24_mall_id)
- Cafe24Connection, Cafe24ProductMapping 모델
- Cafe24ApiService: getAuthUrl, exchangeToken, refreshToken, pushProduct, updateProduct, deleteProduct, getProducts (Base: https://{mall_id}.cafe24api.com/api/v2)
- Cafe24Controller: connect, callback, status, pushProducts, updateProduct, deleteProduct, listProducts
- 라우트: POST/GET /api/cafe24/connect, callback, GET status, POST products/push, PUT/DELETE/GET products (auth:sanctum, role:retail|wholesale|admin)
- config/services.php cafe24 섹션 (CAFE24_CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes). .env.docker에 값 설정 후 실제 연동 가능.

## [1.9.0] - 2026-02-25
### Added (R2-API-003 AI 콘텐츠 처리 API)
- **contents** 테이블: type(image,video,lookbook,codi), status(draft,published,scheduled,hidden), visibility(public,private), soft delete
- **contents_media** 테이블: content_id(nullable), file_path, file_name, file_size, mime_type, sort_order
- **contents_product_tags** 테이블: content_id, product_id, unique
- Content, ContentFile, ContentProductTagLink 모델
- ContentController: store, mine, show, update, destroy (본인 검증, visibility 적용)
- MediaController: upload (storage/app/public/contents/{user_id}/{YYYYMMDD}/), 응답 id, file_path, file_name, url
- ProductController::mine (기존): 내 상품 목록 검색
- 라우트: POST/GET/PUT/DELETE contents, GET contents/mine, GET contents/{id}(인증만), POST media/upload, GET products/mine
- 유효성: title required|max:200, body nullable|max:2000, type/status/visibility enum, media_ids max 10, product_ids max 10, scheduled_at (status=scheduled 시 required)

## [1.8.0] - 2026-02-24
### Added (R2-FRONT-006 도매 콘텐츠 업로드)
- `/wholesale/content`: 콘텐츠 관리 목록 (그리드/리스트, 필터 타입·상태, 페이지네이션)
- `/wholesale/content/new`: 새 콘텐츠 작성
- `/wholesale/content/[id]/edit`: 콘텐츠 수정
- MediaUploader: 드래그앤드롭, 다중파일(10장), 미리보기, 순서·삭제, 진행률, 이미지 10MB/영상 100MB
- ContentEditor: 타입(이미지/영상/룩북/코디), 제목/본문(2000자), 공개/비공개, 예약발행
- ProductTagSelector: 내 상품 검색·태그(10개)
- ContentList, ContentCard, ContentPreview
- content-api.ts, types/content.ts
- UI: input, label, textarea, progress, switch, alert-dialog
- api.ts: FormData 요청 시 Content-Type 미설정

## [1.7.0] - 2026-02-24
### Added (R2-FRONT-005 관리자 구매 대시보드 상세)
- **구매 대시보드 메인** `/admin/purchase`: 통계 카드(PurchaseStats), 최근 발주 5건, 빠른 링크
- **발주 목록** `/admin/purchase/orders`: 필터(상태/날짜/검색), 테이블, 페이지네이션, 상세 링크
- **발주 상세** `/admin/purchase/[id]`: OrderDetailHeader, OrderItemsTable, InboundStatus, OrderStatusChange, OrderMemo (목록 → /admin/purchase/orders)
- **입고 목록** `/admin/purchase/receiving`: ReceivingTable, 필터, 페이지네이션
- **입고 상세** `/admin/purchase/receiving/[id]`: ReceivingDetail, 검수 완료 (POST inbound-receipts/{id}/complete)
- **바코드** `/admin/purchase/barcode`: BarcodeScanner, 바코드 목록 검색
- 타입: types/purchase.ts (입고·바코드·필터), lib/purchase-api.ts (대시보드·발주 목록·입고·바코드)
- 컴포넌트: PurchaseStats, PurchaseFilter, PurchaseOrderTable, ReceivingTable, ReceivingDetail, BarcodeScanner
- 관리자 사이드바: 구매 대시보드, 발주관리, 입고관리, 바코드 메뉴 추가
- API: dashboard/purchasing/summary·recent-orders, purchase-orders(목록), inbound-receipts(목록/상세/complete), barcodes(목록/검색)

## [1.6.1] - 2026-02-24
### Fixed (R2-FIX-002 코드 검수 피드백)
- BrandPageController.php: Rule import, slug 수정, array_filter 키기반, follower_count 음수 방어, 카테고리 keyword, 가격 COALESCE
- product-api.ts: USE_MOCK 환경변수 전환, clipboard fallback
- brand-api.ts: 함수 시그니처 명확화, cursor-page 변환, 이중추출 제거

### Fixed (V1-CODI-FIX-001)
- V1 코디등록 버그 수정 (products.php)
  - 버그1: 코디삭제 시 `$code` → `$goodsCode` 변수명 수정 (3039줄, 5034줄)
  - 버그2: 코디등록 시 중복체크 로직 추가 (2645줄, 3045줄)
  - 서버: 116 (114.207.244.86)
  - 백업: products.php.bak.20260224
  - 검수 통과, PHP syntax OK, HTTP 200 확인

## [1.6.0] - 2026-02-24
### Added
- R2-API-002: 브랜드 페이지 API (520353b)
  - brand_pages 테이블, BrandPage 모델, ProductImage 모델
  - BrandPageController 6 엔드포인트 (목록, 상세, 상품, 피드, 팔로우, 수정)
  - BrandPageSeeder (wholesale@newtalk.kr 테스트 브랜드)
  - Feed API: author.brand_slug, product.wholesale_name (BrandPage/User 관계)
- R2-FRONT-004: 브랜드 페이지 UI (520353b)
  - 브랜드 상세 /brand/[slug] (커버, 로고, 팔로우, 상품 탭, 피드 탭)
  - 브랜드 탐색 /brands (검색, 그리드, 무한 스크롤)
  - 탐색 페이지 "브랜드" 탭, FeedCard/ProductInfo 작성자·브랜드 → /brand/{slug} 링크
  - brand-api.ts, types/brand.ts

## [1.5.0] - 2026-02-24
### Added (R2-FRONT-003 520353b)
- 상품 상세 페이지: `/retail/product/[id]` (app/retail/product/[id]/page.tsx)
- ProductImageCarousel: 이미지 슬라이드, 스와이프, 인디케이터 도트, placeholder
- ProductInfo: 상품명, 도매가·소매가, 브랜드, 찜 토글, 공유(navigator.share / 클립보드)
- ProductOptions: 컬러·사이즈 선택, 재고 0 품절 표시, 가격 차이 반영
- ProductActionBar: 하단 고정 바, 수량 stepper, 찜, 사입하기 버튼
- RelatedProducts: 수평 스크롤 관련상품 카드, `/retail/product/{id}` 링크
- product-api.ts: getProduct, getRelatedProducts, toggleProductWishlist, shareProduct (Mock 지원)
- types/product.ts: ProductDetail, ProductListItem, ProductImage, ProductOption
- retail 레이아웃: app/retail/layout.tsx (RetailLayout)
- globals.css: scrollbar-hide 유틸

## [1.4.1] - 2026-02-24
### Fixed (R2-FIX-001 검수 피드백)
- FeedController::store() — wholesale/admin 역할 체크 추가, 미인증 역할 403
- FeedController::index() — orderByRaw 바인딩 파라미터 사용 (SQL injection 방어)
- index() DocBlock — 팔로잉 70/30 혼합 TODO 주석 추가
- routes/api.php — POST /feed에 role:wholesale|admin 미들웨어, POST /wishlists/{productId}/toggle 추가
- WishlistController::toggle() — 찜 토글 엔드포인트 추가
- feed-api.ts — toggleWishlist를 /wishlists/{id}/toggle 호출로 변경
- feed-card.tsx — 찜 상태 UI(isWishlisted, Bookmark fill), 팔로우 버튼 disabled, 미디어 placeholder
- feed_likes 테이블 — unique(user_id, feed_item_id) 기존 마이그레이션에 존재 확인
- placeholder — public/images/placeholder-feed.svg 추가

## [1.4.0] - 2026-02-23
### Added
- R2-FRONT-002: 홈 피드 UI (520353b)
- FeedCard 컴포넌트 (미디어, 좋아요, 찜, 상품 링크)
- 무한 스크롤 (IntersectionObserver, cursor 페이지네이션)
- 탐색 페이지 (그리드, 탭 필터, 검색바)
- Mock API 레이어 (실 API 전환 대비)
- shadcn/ui 컴포넌트 추가 (card, avatar, badge, tabs, scroll-area, skeleton, separator, button)
- 피드 타입 정의 (feed.ts)
- 유틸리티 (formatRelativeTime, formatPrice)
- useInfiniteScroll 훅
- ExploreCard 컴포넌트

## [1.3.0] - 2026-02-23
### Added
- R2-API-001: SNS 소셜 엔진 API (520353b)
- follows 테이블 + Follow 모델 + 팔로우/언팔로우/팔로워·팔로잉 목록 API
- wishlists 테이블 + Wishlist 모델 + 찜 추가/해제/목록 API
- feed_items 테이블 + FeedItem 모델 + 홈 피드/탐색/상세/작성/검색 API
- feed_likes 테이블 + FeedLike 모델 + 좋아요 토글 API
- Cursor 기반 페이지네이션 (피드, 팔로우, 찜)

## [1.2.0] - 2026-02-23
### Added
- R2-FRONT-001-DEPLOY: 프론트엔드 Docker 빌드·실행 (870c007)
- Rate Limiting: 로그인 API throttle:5,1 (1분 5회 제한)
- 역할별 라우트 보호: middleware.ts ROLE_PATHS/ROLE_HOME 매핑
- 401 자동 로그아웃: fetchApi에서 401 감지 → 쿠키·스토어 클리어 → /login 리다이렉트
- Sanctum 토큰 만료: 7일 (config/sanctum.php)
- 방화벽 3000 포트 개방 (ufw)
### Fixed
- Redis 연결: REDIS_PORT=6379 → app 서비스 환경변수 추가
- Tailwind 배경·전경색 수정

## [1.1.0] - 2026-02-23
### Added
- R2-FRONT-001: Next.js 16 프로젝트 셋업 (ce541c5)
- 로그인/회원가입 화면
- 역할별 레이아웃 (소매/도매/관리자/MD/사입자)
- 관리자 대시보드 + 사입 대시보드 (R1 API 연동)
- AuthController (POST login/logout, GET me)
- Docker Compose frontend 서비스 구성

### Documentation
- NT-V2-PLAN-002-FINAL.md: 통합 기획서 v1.0.0
- NT-V2-ARCHITECTURE.md: 시스템 아키텍처 v1.0.0
- HANDOVER.md: 인수인계서 v1.0.0
- docs/ 디렉터리 구조 표준화

## [1.0.0] - 2026-02-22
### R1 완료
- R1-001: Sanctum 인증 + RBAC (37ad7e4)
- R1-002: 상품 CRUD API (876f4b3)
- R1-003: 발주·입고·바코드 API (555ee03)
- R1-004: 사입 대시보드 API (67f0a64)
- R1-005: 기본 대시보드 + V1 마이그레이션 (be662c7)

## [0.1.0] - 2026-02-21
### R0 완료
- Laravel 12 + Docker 환경 구축
- V1 스키마 추출 (226 테이블)
- 38 테이블 마이그레이션
- Spatie RBAC 시더 (6 roles, 36 permissions)
- GitHub 레포 생성, .cursorrules 작성
