# 뉴톡 V2 변경 이력 (CHANGELOG)

모든 주요 변경 사항을 기록합니다. [Semantic Versioning](https://semver.org/) 준수.

---

## [Unreleased]

## [3.15.0] - 2026-02-27
### Fixed (DOCS-FIX-009 R4 최종 문서 정합성 복구)
- CONTEXT.md v3.15.0: R4-FRONT-004·007 완료 반영, 다음 작업 정리, 완료 45건
- CHANGELOG.md v3.15.0: 누락 엔트리 복원
- HANDOVER.md v3.0.1: R4-FRONT-004·005·007 완료 상세 추가, 다음 작업 큐 정리

### Added (R4-FRONT-007 위탁배송·드롭십 UI)
- **타입**: frontend/src/types/fulfillment.ts — DropshipStatus, ReturnType/Status/Reason, FulfillmentTaskType/Status, DropshipOrder, ReturnRequest, FulfillmentTask, FulfillmentDashboard
- **API 클라이언트**: frontend/src/lib/fulfillment-api.ts — 20함수 (드롭십 7 + 반품 7 + 풀필먼트 6)
- **컴포넌트 14개** (frontend/src/components/fulfillment/): DropshipStatusBadge, DropshipOrderCard, DropshipOrderList, DropshipOrderDetail, DropshipCreateDialog, ReturnStatusBadge, ReturnRequestList, ReturnRequestDetail, ReturnCreateDialog, FulfillmentTaskStatusBadge, FulfillmentTaskCard, FulfillmentTaskList, FulfillmentTaskDetail, FulfillmentDashboardWidget, index
- **페이지**: /retail/dropship, /retail/dropship/[id], /retail/returns, /retail/returns/[id], /wholesale/dropship, /wholesale/dropship/[id], /admin/fulfillment, /admin/fulfillment/[id], /admin/returns, /admin/returns/[id]
- **레이아웃**: retail 드롭십·반품, wholesale 드롭십 관리, admin 풀필먼트·반품 메뉴 추가

## [3.14.0] - 2026-02-26
### Added (R4-FRONT-006 콘텐츠 파이프라인 UI)
- **타입**: frontend/src/types/pipeline.ts — PipelineStatus(12단계), PipelinePriority, PipelineGrade, PipelineContentType, PipelineMediaStage, ContentPipelineJob, PipelineLog, PipelineMedia, PipelineDashboard, PipelineCreateRequest, PipelineListResponse, PipelineStatistics
- **API 클라이언트**: frontend/src/lib/pipeline-api.ts — createPipelineJob, getPipelineJobs, getPipelineJob, updatePipelineJob, updatePipelineStatus, assignMD, assignPhotographer, assignEditor, uploadPipelineMedia, linkContent, rejectQA, bulkCreateJobs, getPipelineDashboard, getPipelineStatistics (14함수)
- **컴포넌트 12개** (frontend/src/components/pipeline/): PipelineKanbanBoard, PipelineJobCard, PipelineJobList, PipelineJobDetail, PipelineStatusBadge, PipelinePriorityBadge, PipelineAssignDialog, PipelineMediaGallery, PipelineCreateDialog, PipelineDashboardPage, PipelineTimeline, index
- **페이지**: /admin/pipeline (칸반 보드 + 리스트 뷰 토글, 작업 생성), /admin/pipeline/[id] (작업 상세), /admin/pipeline/dashboard (대시보드), /admin/pipeline/new (단일·일괄 작업 생성)
- **레이아웃**: admin-layout "콘텐츠 파이프라인" → /admin/pipeline (Workflow 아이콘)
- 12단계 워크플로우(입고→분류→촬영대기→촬영→촬영완료→편집→편집완료→QA대기→QA승인/반려→퍼블리싱→취소), 칸반 드래그 시 상태 변경 API, 상태별·담당자별·기간 필터, 미디어 갤러리(raw/edited/final), 로그 타임라인

## [3.13.0] - 2026-02-26
### Added (R4-FRONT-005 SNS 자동 게시 UI)
- **타입**: frontend/src/types/sns.ts — SnsPlatform, SnsPostStatus, SnsPostType, SnsConnection, SnsPost, SnsPostAnalytics, SnsCreatePostRequest, SnsBulkPostRequest
- **API 클라이언트**: frontend/src/lib/sns-api.ts — connectSns, disconnectSns, getSnsConnections, createSnsPost, getSnsPostList, getSnsPost, scheduleSnsPost, deleteSnsPost, bulkPost, getPostAnalytics, generateHashtags, getOptimalTime (12함수)
- **컴포넌트 12개** (frontend/src/components/sns/): SnsConnectionList, SnsConnectDialog, SnsPostList, SnsPostCard, SnsPostCreatePage, SnsPostDetail, SnsPostDetailPage, SnsPostStatusBadge, SnsAnalyticsDashboard, SnsHashtagSuggestion, SnsOptimalTimeWidget, SnsBulkPostDialog, index
- **페이지**: /wholesale/sns (계정 목록 + 게시물 목록 탭), /wholesale/sns/new (게시물 작성), /wholesale/sns/[id] (게시물 상세 + 성과), /wholesale/sns/analytics (SNS 성과 대시보드)
- **레이아웃**: wholesale-layout "SNS 관리" → /wholesale/sns (Share2 아이콘)
- 인스타그램·틱톡·페이스북·유튜브 연결·해제, 즉시/예약/다채널 일괄 게시, AI 해시태그 추천, 최적 게시 시간 위젯

## [3.12.0] - 2026-02-26
### Added (R4-FRONT-004 셀러 채널 관리 UI)
- **타입**: frontend/src/types/channel.ts — ChannelPlatform, ChannelStatus, SyncStatus, ChannelConnection, ChannelProductMapping
- **API 클라이언트**: frontend/src/lib/channel-api.ts — 13함수 (getChannels, connectChannel, getAuthUrl, getChannelDetail, disconnectChannel, updateChannelSettings, pushProduct, pushBulk, deleteChannelProduct, syncChannel, getMappings, refreshToken, getProductChannels)
- **컴포넌트 10개** (frontend/src/components/channel/): ChannelList, ChannelCard, ChannelConnectDialog, ChannelDetail, ChannelStatusBadge, ChannelMappingTable, ChannelPushDialog, ChannelSettingsForm, ProductChannelBadges, index
- **페이지**: /wholesale/channels, /wholesale/channels/[id], /admin/channels, /admin/channels/[id], /wholesale/products/[id]/channels
- **레이아웃**: wholesale "채널 관리", admin "채널" 메뉴 추가

## [3.11.0] - 2026-02-26
### Fixed (DOCS-FIX-008 4대 핵심 문서 정합성 복구)
- CONTEXT.md v3.11.0 전면 재작성: 완료 항목 42건 정합성 복구
- CHANGELOG.md v1.7.0~v2.12.0 누락 구간 14개 버전 복원
- ARCHITECTURE.md v3.0.0 전면 재작성: R3 마켓플레이스+R4 거래처/스토리/AI/채널/콘텐츠/SNS/드롭십 반영
- HANDOVER.md v3.0.0 완료 항목 전체 정합성 복구

## [3.10.0] - 2026-02-26
### Added (R4-API-007 위탁배송 고도화 + 드롭십 API)
- 위탁배송·드롭십 주문·반품·이행 테이블·API

## [3.9.0] - 2026-02-26
### Added (R4-API-006 SNS 자동 게시 API)
- sns_connections, sns_posts, sns_post_analytics, SNS 4채널 스텁 연동

## [3.8.0] - 2026-02-26
### Added (R4-FRONT-003 AI 추천 피드 UI + 소매 마이페이지)
- AI 맞춤 피드 UI, 소매 마이페이지

## [3.7.0] - 2026-02-26
### Added (R4-FRONT-002 스토리 UI)
- 스토리 피드·뷰어·하이라이트 UI

## [3.6.0] - 2026-02-26
### Added (R4-FRONT-001 거래처 제도 UI)
- **타입**: frontend/src/types/trade.ts — ApplicationStatus, PartnershipTier, TradeApplication, TradePartnership, TradePrice, TradeApplyRequest
- **API 클라이언트**: frontend/src/lib/trade-api.ts — applyTrade, getApplications, getApplicationDetail, approveApplication, rejectApplication, getPartners, getPartnerDetail, setTradePrice, getTradePrice, bulkSetTradePrices, removeTradePrice (11함수)
- **컴포넌트 10개** (frontend/src/components/trade/): TradeApplicationForm, TradeApplicationList, TradeApplicationDetail, TradeApplicationStatusBadge, TradePartnerList, TradePartnerDetail, TradePriceTable, TradeTierBadge, TradeApplyDialog, index
- **페이지**: /retail/trade (내 거래처·신청 현황), /retail/trade/apply (거래처 신청), /retail/trade/applications/[id], /retail/trade/partners/[id], /wholesale/trade (받은 신청·거래처 목록), /wholesale/trade/applications/[id], /wholesale/trade/partners/[id], /admin/trade (전체 거래처 현황), /admin/trade/applications/[id], /admin/trade/partners/[id]
- **레이아웃**: retail-layout "거래처" → /retail/trade, wholesale-layout "거래처 관리" → /wholesale/trade, admin-layout "거래처" → /admin/trade
- **브랜드 페이지**: /brand/[slug] "거래처 신청" 버튼 → TradeApplyDialog (wholesale_user_id 연동)

## [3.5.0] - 2026-02-26
### Added (R4-API-005 콘텐츠 파이프라인 API)
- content_pipeline_jobs, pipeline_logs, pipeline_media, 콘텐츠 파이프라인 API

## [3.4.0] - 2026-02-26
### Added (R4-API-004 셀러 채널 관리 API)
- channel_connections, channel_product_mappings, 셀러 채널 관리 API

## [3.3.0] - 2026-02-26
### Added (R4-API-003 AI 맞춤 피드 + 추천 엔진)
- user_interests, product_scores, trend_snapshots, AI 추천 엔진 API

## [3.1.0] - 2026-02-26
### Added (R4-API-001 거래처 제도 API)
- **trade_applications** 테이블: 소매→도매 거래처 신청 (status: pending/approved/rejected/suspended/terminated), business_name/number/type, introduction, phone, reject_reason, approved_at/rejected_at
- **trade_partnerships** 테이블: 승인된 거래 관계, tier(basic/silver/gold/vip), discount_rate, commission_rate(경로 B 1~2%), total_orders/total_amount, wholesale_memo/retail_memo
- **trade_prices** 테이블: 거래처 전용가 (partnership_id, product_id, product_option_id, trade_price, original_price)
- **orders**: trade_partnership_id, commission_rate 컬럼 추가
- TradeApplication, TradePartnership, TradePrice 모델 (상태 전이, 할인가, 누적 통계, 자동 등급 업그레이드)
- TradeService 14 메서드: apply, approve, reject, suspend, terminate, getApplications, getPartners, getPartnerDetail, setTradePrice, removeTradePrice, bulkSetTradePrices, getTradePrice, updatePartnershipTier, updateCommissionRate
- TradeController 14 엔드포인트: 소매(신청/적용가), 도매(승인/거절/전용가/일시중지/종료), 공용(신청·거래처 목록/상세), 관리자(수수료율)
- 주문 생성 시 거래처 적용가·수수료 반영, 배송 완료 시 거래처 누적 통계·등급 갱신

## [3.2.0] - 2026-02-26
### Added (R4-API-002 스토리 API)
- **stories** 테이블: user_id, media_type(image|video), media_url, thumbnail_url, caption, link_url, link_type(product|brand|external|none), link_id, view_count, reply_count, is_highlight, expires_at(생성+24h), softDeletes
- **story_views** 테이블: story_id, user_id, viewed_at, reaction(none|like|fire|clap|wow|sad), unique(story_id, user_id)
- Story, StoryView 모델 (scopeActive, scopeExpired, isExpired, isViewedBy)
- StoryService 11 메서드: create, getFeed, getUserStories, getMyStories, view, react, getViewers, delete, getHighlights, toggleHighlight, cleanupExpired
- StoryController 10 엔드포인트: store, feed, userStories, mine, show, destroy, recordView, react, viewers, toggleHighlight
- 라우트: auth:sanctum 내 /api/stories (feed, mine, user/{userId}, CRUD, view, react, viewers, highlight)
- 스케줄러: 매시 만료 스토리 소프트삭제 (routes/console.php), Artisan story:cleanup-expired

## [2.12.0] - 2026-02-26
### Added (R3-FRONT-006 정산 UI)
- /admin/settlements 관리자 정산 목록 (필터, 검색, 생성)
- /admin/settlements/[id] 관리자 정산 상세 (상태변경, 항목관리, 재계산)
- /wholesale/settlements 도매 정산 목록
- /wholesale/settlements/[id] 도매 정산 상세 (은행정보, 메모)
- 컴포넌트 10개: SettlementList, SettlementDetail, SettlementStatusBadge, SettlementSummaryCard, SettlementItemTable, SettlementTimeline, SettlementCreateDialog, SettlementStatusChangeDialog, BankInfoForm, index
- settlement-api.ts 9함수, types/settlement.ts
- admin/wholesale 레이아웃 정산 메뉴 추가

## [2.11.0] - 2026-02-26
### Added (R3-API-006 정산 API)
- **settlements** 테이블: seller_id, settlement_number(ST-YYYYMMDD-XXXXX), status(pending/confirmed/processing/completed/cancelled), period_type(weekly/biweekly/monthly), period_start/end, order_count, total_sales, total_shipping_fee, platform_fee, platform_fee_rate, deductions, net_amount, bank_name/account/holder, confirmed_at, paid_at, admin_memo, seller_memo, softDeletes
- **settlement_items** 테이블: settlement_id, order_id, payment_id, order_number(스냅샷), order_amount, shipping_fee, commission, commission_rate, deduction, net_amount, status(included/excluded/refunded), note
- **settlement_logs** 테이블: settlement_id, user_id, action(created/confirmed/processing/completed/cancelled/memo/recalculated), from_status, to_status, description, metadata
- Settlement, SettlementItem, SettlementLog 모델
- SettlementService: create, updateStatus, list, getDetail, recalculate, updateItemStatus, preview, updateBankInfo
- SettlementController 9 엔드포인트: preview, store, index, show, updateStatus, recalculate, updateBankInfo, updateItemStatus, addMemo
- Order::settlementItems() 관계 추가
- 정산번호 자동생성, 상태 전이 규칙, 금액 자동 재계산

## [2.10.0] - 2026-02-26
### Added (R3-FRONT-005 Shorts UI)
- 쇼츠 피드 (세로 스와이프, 자동재생, 무한스크롤)
- /retail/shorts 소매 쇼츠 피드, /retail/shorts/[id] 쇼츠 상세
- /wholesale/shorts 내 쇼츠 관리, /wholesale/shorts/new 업로드, /wholesale/shorts/[id]/edit 수정
- 컴포넌트 12개: ShortsFeed, ShortCard, ShortVideoPlayer, ShortActions, ShortCommentSheet, CommentItem, ProductTagOverlay, ProductTagCard, ShortUploadPage, ShortEditPage, MyShortsPage, index
- shorts-api.ts 11함수, types/shorts.ts
- 댓글 시트, 상품태그 오버레이, 좋아요 애니메이션
- retail/wholesale 레이아웃 쇼츠 메뉴 추가

## [2.9.0] - 2026-02-26
### Added (R3-API-005 Shorts API)
- **shorts** 테이블: user_id, title, description, video_url, thumbnail_url, duration, status(draft/processing/published/hidden/rejected), visibility(public/private/followers), view_count, like_count, comment_count, share_count, metadata, published_at, softDeletes, index(user_id,status), index(status,published_at), index(view_count)
- **short_product_tags** 테이블: short_id, product_id, position_x/y, unique(short_id, product_id)
- **short_likes** 테이블: short_id, user_id, unique(short_id, user_id)
- **short_comments** 테이블: short_id, user_id, parent_id(대댓글), body, is_deleted, like_count
- **short_views** 테이블: short_id, user_id(nullable), ip_address, watched_seconds, watched_percent
- Short, ShortProductTag, ShortLike, ShortComment, ShortView 모델
- ShortsService: getFeed, getShort, create, update, delete, toggleLike, getComments, addComment, deleteComment, recordView, getMine
- ShortController 11 엔드포인트: feed, show, store, update, destroy, toggleLike, recordView, comments, addComment, deleteComment, mine
- 라우트: GET/POST shorts(공개·인증·도매), GET shorts/{id}, GET shorts/{id}/comments, POST shorts/{id}/view, POST shorts/{id}/like, POST shorts/{id}/comments, DELETE shorts/comments/{id}
- 쇼츠 피드: published+public, cursor 페이지네이션, 로그인 시 is_liked
- 조회: 24시간 내 동일 user+short 중복 시 view_count 미증가

## [2.8.0] - 2026-02-26
### Added (R3-FRONT-004 DM UI)
- /retail/messages 대화 목록 (ConversationList, ConversationItem, UnreadBadge)
- /retail/messages/[id] 대화방 (ChatRoom, MessageBubble, MessageInput)
- /wholesale/messages, /wholesale/messages/[id] 도매 DM
- 컴포넌트 10개: ConversationList, ConversationItem, ChatRoom, MessageBubble, MessageInput, ProductShareDialog, NewConversationDialog, ChatMenu, UnreadBadge, index
- dm-api.ts 10함수, types/dm.ts
- 상품 상세 "문의하기" 버튼, 브랜드 페이지 "메시지 보내기" 버튼
- 실시간 polling (2초 간격), 읽음 처리 자동 호출
- retail/wholesale 레이아웃 "메시지" 메뉴 추가

## [2.7.0] - 2026-02-26
### Added (R3-API-004 DM API)
- **conversations** 테이블: type(direct/group), title, last_message_id, last_message_at, metadata, softDeletes, index(type), index(last_message_at)
- **conversation_participants** 테이블: conversation_id, user_id, role(owner/member), nickname, is_muted, is_pinned, last_read_at, joined_at, left_at, unique(conversation_id, user_id), index(user_id, left_at)
- **messages** 테이블: conversation_id, sender_id, type(text/image/product/order/system), body, metadata, is_deleted, index(conversation_id, created_at), index(sender_id)
- **message_reads** 테이블: message_id, user_id, read_at, unique(message_id, user_id), index(user_id, read_at)
- Conversation, ConversationParticipant, Message, MessageRead 모델
- ConversationService: getOrCreateDirect, getConversations (unread_count 포함), getConversation, leave (시스템 메시지)
- MessageService: sendMessage, getMessages (cursor 페이지네이션), markAsRead (일괄), deleteMessage (soft)
- ConversationController: store, index, show, toggleMute, togglePin, leave (6 EP)
- MessageController: index, store, markAsRead, destroy (4 EP)
- 라우트: auth:sanctum 내 /conversations 6개, /conversations/{id}/messages 3개, /messages/{id} 1개 = 10 엔드포인트
- 메시지 타입: text(일반), image(이미지), product(상품 공유), order(주문 알림), system(시스템)
- 읽음 처리: participant.last_read_at + message_reads 이중 추적

## [2.6.0] - 2026-02-25
### Added (R3-FRONT-003 배송 UI)
- /retail/addresses 배송지 관리 (목록, 추가, 수정, 삭제, 기본설정)
- 주문 상세 배송 정보 (ShipmentCard, ShipmentTimeline, ShipmentStatusBadge)
- 도매 주문 상세 송장 입력 (TrackingInput, updateTracking), 배송 접수·배송 완료 처리
- 주문 생성 배송지 연동 (AddressSelectDialog, 기본배송지 자동 채움)
- shipping-api.ts (배송 6함수 + 배송지 5함수 = 11함수), types/shipping.ts
- 컴포넌트: ShipmentTimeline, ShipmentStatusBadge, ShipmentDetail, TrackingInput, ShipmentCard, AddressCard, AddressForm, AddressSelectDialog, AddressList
- retail-layout 하단 메뉴 "배송지" 링크 추가

## [2.5.0] - 2026-02-25
### Added (R3-API-003 배송 API)
- **shipments** 테이블 (alter): seller_id, buyer_id, type(direct/consignment), tracking_company, tracking_url, sender_*, receiver_*, returned_at, estimated_delivery, weight, note, softDeletes, index(order_id, status), index(tracking_company, tracking_number). 기존 carrier → tracking_company 이전 후 제거.
- **shipment_logs** 테이블: shipment_id(cascadeDelete), status, location, description, logged_at, index(shipment_id, logged_at).
- **shipping_addresses** 테이블: user_id, label, name, phone, postal_code, address, address_detail, is_default, softDeletes, index(user_id, is_default).
- Shipment, ShipmentLog, ShippingAddress 모델. Shipment::SHIPPING_COMPANIES, TRACKING_URL_TEMPLATES, generateTrackingUrl(), updateStatus().
- ShippingService: createShipment, updateTracking, updateStatus, getTrackingInfo.
- ShipmentController: store, orderShipment, show, updateTracking, updateStatus, trackingInfo (6 EP).
- ShippingAddressController: index, store, update, destroy, setDefault (5 EP).
- Order::shipment(), Order::shipping_status accessor.

## [2.4.0] - 2026-02-25
### Added (R3-FRONT-002 결제 UI)
- /retail/payment 결제 페이지 (토스 SDK, 수단 선택, 금액 확인, 결제하기)
- /retail/payment/success, /retail/payment/fail 콜백 페이지 (confirmPayment, PaymentResult)
- 주문 상세 결제 정보·취소 (PaymentDetail, PaymentCancelDialog), 주문 생성→결제 리다이렉트 (/retail/order/new → /retail/payment?order_id=)
- 도매 주문 상세 결제 상태 표시 (PaymentStatusBadge, 결제금액)
- 컴포넌트 8개: PaymentMethodSelector, PaymentSummary, PaymentProcessing, PaymentResult, PaymentStatusBadge, PaymentDetail, PaymentCancelDialog, useTossPaymentRequest (TossPaymentWidget)
- payment-api.ts 5함수: preparePayment, confirmPayment, getPayment, cancelPayment, getOrderPayment
- types/payment.ts (PaymentStatus, OrderPaymentStatus, Payment, PaymentLog, Request/Response 타입)
- types/order.ts: OrderPaymentStatus, payment_status?, paid_at?

## [2.3.0] - 2026-02-25
### Added (R3-API-002 결제 연동 API)
- **payments** 테이블: 토스 결제 정보 (payment_key, order_number, method, status, amount, approved_amount, balance_amount, 카드/가상계좌 필드, raw_response), softDeletes.
- **payment_logs** 테이블: 결제 이벤트 로그 (action: request, confirm, cancel, webhook, fail).
- **orders** 테이블: payment_status (unpaid/paid/partial_refund/refunded), paid_at 컬럼 추가.
- Payment, PaymentLog 모델. Order::payment(), Order::final_amount, Order::isPaid().
- TossPaymentService: preparePayment, confirmPayment, cancelPayment, getPaymentByKey, handleWebhook.
- PaymentController: prepare, confirm, show, cancel, orderPayment, webhook (6 엔드포인트).
- config/services.php toss 섹션 (TOSS_CLIENT_KEY, TOSS_SECRET_KEY, TOSS_WEBHOOK_SECRET, base_url).

## [2.2.0] - 2026-02-25
### Added (R3-FRONT-001 사입 주문·장바구니 프론트 UI)
- 장바구니 페이지 /retail/cart (조회, 수량 변경, 삭제, 비우기)
- 주문 생성 /retail/order/new (배송정보, 확인, API 연동)
- 주문 목록 /retail/orders (필터, 페이지네이션)
- 주문 상세 /retail/orders/[id] (타임라인, 취소)
- 도매 주문관리 /wholesale/orders, /wholesale/orders/[id] (상태 변경, tracking)
- 컴포넌트 10개 (CartItemCard, CartSummary, CartEmpty, ShippingForm, OrderItemList, OrderSummaryCard, OrderStatusBadge, OrderCard, OrderDetail, OrderCancelDialog)
- API 클라이언트: cart-api.ts (5함수), order-api.ts (5함수)
- 타입: cart.ts, order.ts
- retail 레이아웃: 주문내역 링크 추가
- 상품 상세: 장바구니 담기 버튼 (addCartItem)

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
  - 서버: 116 ([SERVER-IP])
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
