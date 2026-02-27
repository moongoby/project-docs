# 뉴톡 V2 프로젝트 인수인계서

**버전**: 3.0.0
**최종수정**: 2026-02-26 KST (R4-FRONT-006 콘텐츠 파이프라인 UI)
**목적**: 신규 개발자·AI 에이전트가 프로젝트를 즉시 이해하고 작업할 수 있도록 하는 종합 인계 문서

---

## 변경 이력
| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2026-02-23 | R1 완료 + R2 착수 상태 기준 초판 |
| 2.x | 2026-02-24~26 | R2/R3 완료, R4-API-001·002, R4-FRONT-001 |
| 3.0.0 | 2026-02-26 | DOCS-FIX-008: 완료 항목 정합성 복구; R4-FRONT-006 콘텐츠 파이프라인 UI 완료 반영 |

---

## 1. 프로젝트 개요

뉴톡 V2는 V1(CodeIgniter 2.x/PHP 5.4)을 Laravel 12 + Next.js 16으로 재구축하는 프로젝트.
SNS형 B2B SaaS 마켓플레이스로 진화 중.

**핵심 이해관계자**: CEO (moongoby@gmail.com) – 사입 시스템 유일 의사결정자.

---

## 2. 접속 정보

### 서버 (rfree-009)
```
SSH: ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86
OS: Ubuntu 20.04
CPU: AMD EPYC 7262 8-Core
RAM: 16 GB
Disk: 875 GB
IP: 114.207.244.86 (V2), 114.207.244.87 (V1 어드민)
Docker: 28.1.1, Compose v2.35.1
```

### V2 Docker 스택 (/srv/newtalk-v2/)
```
app:      PHP 8.3-FPM (Laravel 12)
nginx:    1.25-alpine → :8080
db:       MySQL 8.0 → :3307
redis:    Redis 7 → :6380
frontend: Next.js 16 → :3000 (R2 추가)
```

### DB 접속
```
V1 (읽기 전용): mysql -u pigupuser -p -h 127.0.0.1 -P 3306 autoda
  비밀번호: /home/danharoo/www/application/config/database.php 참조
V2 (읽기/쓰기): mysql -u newtalk_v2_user -p -h 127.0.0.1 -P 3307 newtalk_v2
  비밀번호: /srv/newtalk-v2/.env.docker 참조
```

### NAS
```
Synology DS1821+, IP 192.168.30.23
image-auto 컨테이너: :8100
```

### Git
```
레포: git@github.com:moongoby/newtalk-v2-api-.git (끝 하이픈 주의)
웹: https://github.com/moongoby/newtalk-v2-api-
```

### URL
```
V2 API: http://114.207.244.86:8080
V2 Frontend: http://114.207.244.86:3000
V1: http://114.207.244.86
```

### 테스트 계정 (비밀번호: .env 또는 시더 참조, 인계서에 평문 기록 금지)
```
admin@newtalk.kr (관리자)
md@newtalk.kr (MD)
purchaser@newtalk.kr (사입자)
wholesale@newtalk.kr (도매)
retail@newtalk.kr (소매)
outsource@newtalk.kr (외주)
```

---

## 3. 작업 규칙 (필독)

### 3.1 절대 금지
- V1 소스 코드 수정 금지
- V1 DB 쓰기 금지 (읽기만 허용)
- .env.docker, 비밀번호 등 민감정보 Git 커밋 금지

### 3.2 백업
- 파일 수정 전 반드시: .bak.{YYYYMMDD_HHMMSS}

### 3.3 Git 규칙
- 커밋 접두사: [R{라운드}-{TASK번호}] 또는 [DOCS]
- 예: [R1-003] 발주 API, [R2-FRONT-001] Next.js 셋업, [DOCS] 기획서 수정
- 빈 테이블 커밋 금지

### 3.4 Docker 명령
```
docker compose --env-file .env.docker exec app php artisan {command}
docker compose --env-file .env.docker exec app composer {command}
```

### 3.5 보고서
- 위치: /srv/newtalk-v2/docs/reports/{TASK-ID}-report.md
- 필수 항목: 파일 목록, 실행 결과, 테스트 결과, Git SHA

---

## 4. 완료된 작업

### R0: 인프라 구축
- Laravel 12 + Docker 환경
- V1 스키마 추출 (226 테이블)
- 38 테이블 마이그레이션
- Spatie RBAC (6 roles, 36 permissions)
- GitHub 레포 + .cursorrules (129줄)

### R1-TASK-001: 인증 + RBAC
- Sanctum 인증 API
- 커밋: 37ad7e4
- 브랜치: feature/R1-TASK-001-auth

### R1-TASK-002: 상품 CRUD API
- 모델, 이미지, 옵션, 카테고리, 역할별 접근
- 커밋: 876f4b3
- 브랜치: feature/R1-TASK-002-products

### R1-TASK-003: 발주·입고·바코드 API
- 7단계 발주 상태 전이, 입고→수량 자동 갱신, 바코드 일괄 생성
- 커밋: 555ee03 (구현 완성)
- 브랜치: feature/R1-TASK-003-purchasing

### R1-TASK-004: 사입 대시보드 API
- admin 전용 6개 엔드포인트 (summary, suppliers, trend, recent-orders, recent-inbounds, alerts)
- 커밋: 67f0a64
- 브랜치: feature/R1-TASK-004-dashboard

### R1-TASK-005: 기본 대시보드 + V1 마이그레이션
- 역할별 overview + admin stats 엔드포인트
- V1→V2 마이그레이션 커맨드 3개 (users, products, wholesale)
  - users: 79,459건 dry-run 확인
  - products: 77,111건 dry-run 확인 (active 12,585)
  - wholesale: 1,818건 dry-run 확인
- 커밋: be662c7
- 브랜치: feature/R1-TASK-005-migration

### R2-FRONT-001: Next.js 프로젝트 셋업
- Next.js 16 프로젝트 구조, 인증(로그인/회원가입), 역할별 라우팅
- 관리자 대시보드 + 사입 대시보드 화면
- 소매/도매/MD/사입자 레이아웃
- 커밋: ce541c5
- 브랜치: feature/R2-FRONT-001-setup

### R2-FRONT-001-DEPLOY: 프론트엔드 배포
- Rate Limiting + 역할 라우트 + 401 로그아웃 + Docker 기동
- 커밋: 870c007
- 브랜치: feature/R2-FRONT-001-setup
- 접속: http://114.207.244.86:3000

### R2-API-001: SNS 소셜 엔진 API
- 피드(홈/탐색/상세/작성/검색/좋아요), 팔로우(팔로우/언팔로우/팔로워·팔로잉), 찜(목록/추가/해제)
- follows, wishlists, feed_items, feed_likes 테이블 + 4 모델 + 3 컨트롤러 (13 엔드포인트)
- 커밋: 520353b
- 브랜치: feature/R2-API-001-social-engine

### R2-FIX-001: 검수 피드백 반영 (v1.4.1)
- store() 역할 체크(wholesale|admin), index() orderByRaw 바인딩, feed_likes unique 확인
- WishlistController::toggle, POST /wishlists/{productId}/toggle
- 프론트: toggleWishlist 엔드포인트 변경, 찜 UI 상태, 팔로우 disabled, placeholder 이미지
- 브랜치: feature/R2-FIX-001-review-feedback

### R2-FRONT-003: 상품 상세·찜·공유 UI (v1.5.0)
- 상품 상세 페이지 `/retail/product/[id]`, 이미지 캐러셀, 옵션(컬러·사이즈), 찜·공유, 액션바, 관련상품
- product-api.ts (getProduct, getRelatedProducts, toggleProductWishlist, shareProduct)
- 브랜치: feature/R2-FRONT-003-product-detail
- Git SHA: 520353b

### R2-API-002: 브랜드 페이지 API (v1.6.0)
- brand_pages 테이블, BrandPage·ProductImage 모델, BrandPageController 6 EP
- GET /brands, /brands/{slug}, /brands/{slug}/products, /brands/{slug}/feed, POST follow, PUT /brands/me
- BrandPageSeeder (wholesale@newtalk.kr), Feed API author.brand_slug·product.wholesale_name
- 브랜치: feature/R2-API-002-brand-page
- Git SHA: 520353b

### R2-FRONT-004: 브랜드 페이지 UI (v1.6.0)
- /brand/[slug] 상세 (헤더, 탭 상품/피드), /brands 탐색, 탐색 탭 "브랜드", FeedCard·ProductInfo 브랜드 링크
- brand-api.ts, BrandHeader, BrandCard, BrandProductGrid, BrandFeedSection
- 브랜치: feature/R2-API-002-brand-page
- Git SHA: 520353b

### R2-FRONT-005: 관리자 구매 대시보드 상세 (v1.7.0)
- 구매 대시보드 메인 /admin/purchase, 발주 목록 /admin/purchase/orders, 발주 상세 /admin/purchase/[id]
- 입고 목록 /admin/purchase/receiving, 입고 상세 /admin/purchase/receiving/[id], 바코드 /admin/purchase/barcode
- PurchaseStats, PurchaseFilter, PurchaseOrderTable, ReceivingTable, ReceivingDetail, BarcodeScanner
- API: dashboard/purchasing/summary·recent-orders, purchase-orders(목록), inbound-receipts(목록/상세/complete), barcodes
- 보고서: docs/reports/R2-FRONT-005-report.md
- Git SHA: 520353b

### R2-FRONT-006: 도매 콘텐츠 업로드 UI (v1.8.0)
- /wholesale/content 목록(그리드/리스트, 필터, 페이지네이션), /wholesale/content/new 작성, /wholesale/content/[id]/edit 수정
- MediaUploader, ContentEditor, ProductTagSelector, ContentList, ContentCard, ContentPreview
- content-api.ts, types/content.ts, UI: input, label, textarea, progress, switch, alert-dialog
- Git SHA: 520353b

### R2-API-003: AI 콘텐츠 처리 API (v1.9.0)
- contents, contents_media, contents_product_tags 테이블 및 Content, ContentFile, ContentProductTagLink 모델
- ContentController: store, mine, show, update, destroy
- MediaController: upload (id, file_path, file_name, url), type=image|video
- GET /api/contents/{id} 인증만(visibility=private은 본인만)
- Git SHA: 520353b

### R2-API-004: 카페24 API 연동 (v2.0.0)
- cafe24_connections, cafe24_product_mappings 테이블 및 Cafe24Connection, Cafe24ProductMapping 모델
- Cafe24ApiService (OAuth URL, token 교환/갱신, 상품 push/update/delete/list)
- Cafe24Controller: connect, callback, status, pushProducts, updateProduct, deleteProduct, listProducts
- POST/GET /api/cafe24/connect, callback, GET status, POST products/push, PUT/DELETE/GET products
- Git SHA: 520353b

### R3-API-001: 사입 주문 API (v2.1.0)
- carts (status, note, softDeletes, unique user_id+status), cart_items, orders R3 컬럼, order_items 스냅샷
- CartController: index, addItem, updateItem, removeItem, clear (장바구니 5개 엔드포인트)
- OrderController: store(cart_id/item_ids), index, show, updateStatus, cancel (주문 5개 엔드포인트)
- 주문번호 NT-YYYYMMDD-XXXXX, 도매처별 주문 분리, 소매 취소/도매 확인·배송/관리자 refund
- Git SHA: 87cb07b

### R3-API-002: 결제 연동 API (v2.3.0)
- payments, payment_logs 테이블 및 orders 결제 컬럼 (payment_status, paid_at)
- Payment, PaymentLog 모델. TossPaymentService (prepare, confirm, cancel, webhook)
- PaymentController: prepare, confirm, show, cancel, orderPayment, webhook (6 엔드포인트)
- Git SHA: b798049

### R3-FRONT-001: 사입 주문·장바구니 프론트 UI (v2.2.0)
- /retail/cart 장바구니 (조회, 수량 변경, 삭제, 비우기, 주문하기)
- /retail/order/new 주문 생성 (배송정보, item_ids/cart 연동)
- /retail/orders, /retail/orders/[id] 주문 목록·상세 (필터, 페이지네이션, 취소)
- /wholesale/orders, /wholesale/orders/[id] 도매 주문 관리 (상태 변경, 송장)
- CartItemCard, CartSummary, CartEmpty, ShippingForm, OrderItemList, OrderSummaryCard, OrderStatusBadge, OrderCard, OrderDetail, OrderCancelDialog
- cart-api.ts (5함수), order-api.ts (5함수), types/cart.ts, types/order.ts
- retail 레이아웃: 주문내역 링크. 상품 상세: 장바구니 담기 버튼
- Git SHA: b798049

### R3-FRONT-002: 결제 UI (v2.4.0)
- /retail/payment 결제 페이지 (preparePayment, 수단 선택, TossPaymentWidget/useTossPaymentRequest)
- /retail/payment/success, /retail/payment/fail 콜백 (confirmPayment, PaymentResult)
- 주문 상세: getOrderPayment, PaymentDetail, 결제하기 버튼 (unpaid·pending 또는 ready/expired)
- 주문 생성 성공 시 /retail/payment?order_id={id} 리다이렉트
- 도매 주문 상세: 결제 상태 PaymentStatusBadge, 결제금액 표시
- 컴포넌트 8개: PaymentMethodSelector, PaymentSummary, PaymentProcessing, PaymentResult, PaymentStatusBadge, PaymentDetail, PaymentCancelDialog, useTossPaymentRequest
- payment-api.ts (5함수), types/payment.ts
- Git SHA: b798049

### R3-API-003: 배송 API (v2.5.0)
- shipments 테이블 alter: seller_id, buyer_id, type(direct/consignment), tracking_company, tracking_url, sender_*, receiver_*, returned_at, estimated_delivery, weight, note, softDeletes
- shipment_logs 테이블 (배송 이벤트 타임라인)
- shipping_addresses 테이블 (기본배송지, 소프트삭제)
- Shipment, ShipmentLog, ShippingAddress 모델. ShippingService (createShipment, updateTracking, updateStatus, getTrackingInfo)
- ShipmentController: POST/GET orders/{orderId}/shipment, GET/PUT shipments/{id}, PUT tracking, PUT status, GET tracking (6 EP)
- ShippingAddressController: GET/POST/PUT/DELETE shipping-addresses, PUT default (5 EP)
- Order::shipment(), Order::shipping_status accessor
- Git SHA: b798049

### R3-FRONT-003: 배송 UI (v2.6.0)
- /retail/addresses 배송지 관리 (목록, 추가, 수정, 삭제, 기본설정)
- 주문 상세 /retail/orders/[id]: getOrderShipment, ShipmentCard, ShipmentTimeline, 추적 링크
- 도매 주문 상세 /wholesale/orders/[id]: 배송 접수(createShipment), TrackingInput(updateTracking), 배송 완료(updateShipmentStatus), ShipmentCard·ShipmentTimeline
- 주문 생성 /retail/order/new: AddressSelectDialog, 기본배송지 자동 채움(getShippingAddresses)
- retail-layout: 하단 메뉴 "배송지" 링크 (/retail/addresses)
- 컴포넌트: ShipmentTimeline, ShipmentStatusBadge, ShipmentDetail, TrackingInput, ShipmentCard, AddressCard, AddressForm, AddressSelectDialog, AddressList
- shipping-api.ts 11함수, types/shipping.ts
- Git SHA: b798049

### R3-API-004: DM API (v2.7.0)
- conversations, conversation_participants, messages, message_reads 테이블
- Conversation, ConversationParticipant, Message, MessageRead 모델
- ConversationService: getOrCreateDirect, getConversations, getConversation, leave (시스템 메시지)
- MessageService: sendMessage, getMessages (cursor), markAsRead, deleteMessage (soft)
- ConversationController: store, index, show, toggleMute, togglePin, leave (6 EP)
- MessageController: index, store, markAsRead, destroy (4 EP)
- 라우트: GET/POST /conversations, GET/PUT/DELETE /conversations/{id}, mute, pin, messages, read, DELETE /messages/{id}
- Git SHA: b798049

### R3-FRONT-004: DM UI (v2.8.0)
- /retail/messages 대화 목록, /retail/messages/[id] 대화방
- /wholesale/messages, /wholesale/messages/[id] 도매 DM
- 컴포넌트 10개: ConversationList, ConversationItem, ChatRoom, MessageBubble, MessageInput, ProductShareDialog, NewConversationDialog, ChatMenu, UnreadBadge, index
- dm-api.ts 10함수, types/dm.ts
- 상품 상세 문의하기, 브랜드 페이지 메시지 보내기, 실시간 polling 2초, 읽음 처리, retail/wholesale 레이아웃 메시지 메뉴

### R3-API-005: Shorts API (v2.9.0)
- shorts, short_product_tags, short_likes, short_comments, short_views 테이블
- Short, ShortProductTag, ShortLike, ShortComment, ShortView 모델
- ShortsService: getFeed, getShort, create, update, delete, toggleLike, getComments, addComment, deleteComment, recordView, getMine
- ShortController: feed, show, store, update, destroy, toggleLike, recordView, comments, addComment, deleteComment, mine (11 EP)
- 라우트: GET /shorts(피드), GET /shorts/{id}(상세), GET /shorts/mine(도매), POST /shorts, PUT/DELETE /shorts/{id}, POST /shorts/{id}/like, POST /shorts/{id}/view, GET /shorts/{id}/comments, POST /shorts/{id}/comments, DELETE /shorts/comments/{id}
- 쇼츠 피드·상세·업로드·수정·삭제·좋아요·댓글·조회 기록·상품 태그

### R3-FRONT-005: Shorts UI (v2.10.0)
- /retail/shorts 쇼츠 피드 (ShortsFeed, 세로 스와이프, 자동재생, 3초 이상 시청 시 recordShortView)
- /retail/shorts/[id] 쇼츠 상세 (ShortCard, 댓글 시트, 상품태그 오버레이)
- /wholesale/shorts 내 쇼츠 관리 (MyShortsPage, 그리드, 수정/삭제)
- /wholesale/shorts/new 쇼츠 업로드 (ShortUploadPage, 영상 100MB, 제목·설명·상품태그·공개범위)
- /wholesale/shorts/[id]/edit 쇼츠 수정 (ShortEditPage, 삭제 확인 다이얼로그)
- 컴포넌트 12개: ShortsFeed, ShortCard, ShortVideoPlayer, ShortActions, ShortCommentSheet, CommentItem, ProductTagOverlay, ProductTagCard, ShortUploadPage, ShortEditPage, MyShortsPage, index
- shorts-api.ts 11함수, types/shorts.ts
- retail 하단 메뉴 "쇼츠", wholesale 사이드바 "쇼츠 관리" 추가

### R4-API-002: 스토리 API (v3.2.0)
- stories, story_views 테이블 (24시간 만료, 조회·리액션)
- Story, StoryView 모델 (scopeActive, scopeExpired, isViewedBy)
- StoryService: create, getFeed, getUserStories, getMyStories, view, react, getViewers, delete, getHighlights, toggleHighlight, cleanupExpired (11 메서드)
- StoryController 10 엔드포인트: store, feed, userStories, mine, show, destroy, recordView, react, viewers, toggleHighlight
- 라우트: GET stories/feed, GET stories/mine, GET stories/user/{userId}, POST stories, GET/DELETE stories/{id}, POST view, POST react, GET viewers, PUT highlight
- 스케줄러: 매시 만료 스토리 소프트삭제 (routes/console.php), Artisan story:cleanup-expired
- 보고서: docs/reports/R4-API-002-report.md

### R4-FRONT-001: 거래처 제도 UI (v3.6.0)
- 타입: types/trade.ts (ApplicationStatus, PartnershipTier, TradeApplication, TradePartnership, TradePrice, TradeApplyRequest)
- API: trade-api.ts — applyTrade, getApplications, getApplicationDetail, approveApplication, rejectApplication, getPartners, getPartnerDetail, setTradePrice, getTradePrice, bulkSetTradePrices, removeTradePrice (11함수)
- 컴포넌트 10개: TradeApplicationForm, TradeApplicationList, TradeApplicationDetail, TradeApplicationStatusBadge, TradePartnerList, TradePartnerDetail, TradePriceTable, TradeTierBadge, TradeApplyDialog, index
- 페이지: /retail/trade, /retail/trade/apply, /retail/trade/applications/[id], /retail/trade/partners/[id], /wholesale/trade, /wholesale/trade/applications/[id], /wholesale/trade/partners/[id], /admin/trade, /admin/trade/applications/[id], /admin/trade/partners/[id]
- 레이아웃: retail "거래처", wholesale "거래처 관리", admin "거래처" 메뉴 추가
- 브랜드 페이지 /brand/[slug] "거래처 신청" 버튼 → TradeApplyDialog
- 보고서: docs/reports/R4-FRONT-001-report.md

### R3-API-006: 정산 API (v2.11.0)
- settlements, settlement_items, settlement_logs 테이블, SettlementService 8메서드, 9 엔드포인트

### R3-FRONT-006: 정산 UI (v2.12.0)
- 컴포넌트 10개, 페이지 4개 (/admin/settlements, /wholesale/settlements), settlement-api.ts 9함수, types/settlement.ts

### R4-API-003: AI 맞춤 피드 + 추천 엔진 (v3.3.0)
- user_interests, product_scores, trend_snapshots, AI 추천 엔진 API

### R4-API-004: 셀러 채널 관리 API (v3.4.0)
- channel_connections, channel_product_mappings, 셀러 채널 관리 API

### R4-API-005: 콘텐츠 파이프라인 API (v3.5.0)
- content_pipeline_jobs, pipeline_logs, pipeline_media, 콘텐츠 파이프라인 API

### R4-FRONT-002: 스토리 UI (v3.7.0)
- 스토리 피드·뷰어·하이라이트 UI

### R4-FRONT-003: AI 추천 피드 UI + 소매 마이페이지 (v3.8.0)
- AI 맞춤 피드 UI, 소매 마이페이지

### R4-API-006: SNS 자동 게시 API (v3.9.0)
- sns_connections, sns_posts, sns_post_analytics, SNS 4채널 스텁 연동

### R4-API-007: 위탁배송 고도화 + 드롭십 API (v3.10.0)
- dropship_orders, return_requests, fulfillment_tasks, 위탁배송·드롭십 API

### R4-FRONT-006: 콘텐츠 파이프라인 UI (v3.14.0)
- 타입: types/pipeline.ts (PipelineStatus 12단계, ContentPipelineJob, PipelineLog, PipelineMedia, PipelineDashboard, PipelineCreateRequest 등)
- API: pipeline-api.ts — createPipelineJob, getPipelineJobs, getPipelineJob, updatePipelineJob, updatePipelineStatus, assignMD, assignPhotographer, assignEditor, uploadPipelineMedia, linkContent, rejectQA, bulkCreateJobs, getPipelineDashboard, getPipelineStatistics (14함수)
- 컴포넌트 12개: PipelineKanbanBoard, PipelineJobCard, PipelineJobList, PipelineJobDetail, PipelineStatusBadge, PipelinePriorityBadge, PipelineAssignDialog, PipelineMediaGallery, PipelineCreateDialog, PipelineDashboardPage, PipelineTimeline, index
- 페이지: /admin/pipeline (칸반+리스트), /admin/pipeline/[id], /admin/pipeline/dashboard, /admin/pipeline/new
- admin-layout "콘텐츠 파이프라인" → /admin/pipeline (Workflow 아이콘)
- 보고서: docs/reports/R4-FRONT-006-report.md

### R4-FRONT-005: SNS 자동 게시 UI (v3.13.0)
- 타입: types/sns.ts (SnsPlatform, SnsPostStatus, SnsPostType, SnsConnection, SnsPost, SnsPostAnalytics, SnsCreatePostRequest, SnsBulkPostRequest)
- API: sns-api.ts — connectSns, disconnectSns, getSnsConnections, createSnsPost, getSnsPostList, getSnsPost, scheduleSnsPost, deleteSnsPost, bulkPost, getPostAnalytics, generateHashtags, getOptimalTime (12함수)
- 컴포넌트 12개: SnsConnectionList, SnsConnectDialog, SnsPostList, SnsPostCard, SnsPostCreatePage, SnsPostDetail, SnsPostDetailPage, SnsPostStatusBadge, SnsAnalyticsDashboard, SnsHashtagSuggestion, SnsOptimalTimeWidget, SnsBulkPostDialog
- 페이지: /wholesale/sns (계정+게시물 탭), /wholesale/sns/new, /wholesale/sns/[id], /wholesale/sns/analytics
- wholesale-layout "SNS 관리" → /wholesale/sns (Share2 아이콘)

---

## 5. 현재 진행 중인 작업

### 별도 진행 중 (다른 Cursor 대화)
- NAS 이미지 연동

---

## 6. 다음 작업 큐

| 순서 | Task ID | 설명 |
|------|---------|------|
| 1 | R4-FRONT-004 | 셀러 채널 관리 UI |
| 2 | R4-FRONT-007 | 위탁배송·드롭십 UI |
| 3 | R5 | 기획 확정 대기 (일본 크로스보더, 라이브 B2B) |

---

## 7. 주요 문서 위치

```
/srv/newtalk-v2/
├── docs/
│   ├── planning/
│   │   └── NT-V2-PLAN-002-FINAL.md      ← 기획서 (8레이어, 66화면)
│   ├── architecture/
│   │   └── NT-V2-ARCHITECTURE.md         ← 시스템 아키텍처
│   ├── handover/
│   │   └── HANDOVER.md                   ← 이 문서 (인수인계서)
│   ├── reports/
│   │   ├── R1-TASK-001-report.md
│   │   ├── R1-TASK-002-report.md
│   │   ├── R1-TASK-003-report.md
│   │   ├── R1-TASK-004-report.md
│   │   ├── R1-TASK-005-report.md
│   │   ├── R2-FRONT-001-report.md
│   │   ├── R2-API-001-report.md
│   │   ├── R2-API-002-report.md
│   │   ├── R2-FRONT-004-report.md
│   │   └── R4-API-001-report.md
│   ├── v1-analysis/
│   │   └── v1-purchasing-analysis.md
│   ├── scripts/
│   │   └── (런북 스크립트들)
│   ├── CHANGELOG.md                      ← 전체 변경 이력
│   └── README.md                         ← docs 디렉터리 안내
├── .cursorrules                          ← Cursor 작업 규칙 (129줄)
├── frontend/                             ← Next.js 16 (R2)
├── src/ 또는 루트                         ← Laravel 12
├── docker-compose.yml
└── .env.docker                           ← DB/Redis 비밀번호 (커밋 금지)
```

---

## 8. 기존 시스템 보호 (System A~D)

| ID | 설명 | 규칙 |
|---|---|---|
| A | V1 웹 (114.207.244.86:80) | 수정 금지 |
| B | V1 어드민 (114.207.244.87) | 수정 금지 |
| C | NAS image-auto (192.168.30.23:8100) | 별도 진행 |
| D | ShortFlow AI 쇼츠 | 별도 진행 |

---

## 9. DOCS-CLEANUP-001 완료 항목 (2026-02-24)

| 항목 | 우선순위 | 비고 |
|------|----------|------|
| CONTEXT.md SHA 교체 | ~~HIGH~~ 완료 | R2-FRONT-003, R2-API-002, R2-FRONT-004, R2-FIX-002 실제 SHA 교체 (서버 runbook 실행) |
| CHANGELOG.md SHA + v1.6.1 | ~~HIGH~~ 완료 | SHA 2건 교체 + v1.6.1 섹션 추가 완료 |
| R2-FIX-002 보고서 | ~~HIGH~~ 완료 | 보고서 작성 + Git SHA 기록 (서버 runbook에서 치환) |
| HANDOVER.md 플레이스홀더 | ~~MEDIUM~~ 완료 | SHA 교체 완료 시 반영 |
| V1-SCHEMA-SUMMARY.md | ~~MEDIUM~~ 완료 | 테이블 목록·핵심 구조 보완 (서버에서 SHOW TABLES/DESCRIBE 실행 시 완전 채움) |
| review 폴더 | ~~LOW~~ 완료 | .gitkeep만 유지 |

---

## 10. 알려진 이슈

1. **auth_code 90 사용자 65,580명**: V1에서 역할 미분류. 분석 후 소매/도매 분류 필요.
2. **V1 products 마이그레이션**: 컬럼명 차이(g_idx, GoodsName 등) 해결 완료 (be662c7).
3. **R1 브랜치 미병합**: develop에 R1 브랜치들 아직 미병합. R2 전에 정리 필요.
4. **Docker src/ vs 루트**: app 서비스의 마운트가 ./src:/var/www/html인지 확인 필요.
