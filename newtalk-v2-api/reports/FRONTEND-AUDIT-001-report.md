# FRONTEND-AUDIT-001 — Next.js 프론트엔드 B2/B3 API 연동 감사 보고서

**Task ID**: FRONTEND-AUDIT-001
**서버**: 114 (newtalk-v2-api)
**작성일**: 2026-03-06
**작성자**: Claude (자동 감사)
**우선순위**: P1-HIGH

---

## 1. 파일 통계 (Step 1)

```
전체 TS/TSX 파일 수: 630
app/ 라우트 디렉토리 수: 153
API 라이브러리 파일 수 (src/lib/*-api.ts): 21개 (활성)
```

### 활성 API 라이브러리 파일 목록
```
src/lib/admin-product-api.ts
src/lib/admin-user-api.ts
src/lib/brand-api.ts
src/lib/cart-api.ts
src/lib/channel-api.ts
src/lib/content-api.ts
src/lib/dm-api.ts
src/lib/dropship-api.ts
src/lib/feed-api.ts
src/lib/fulfillment-api.ts
src/lib/messenger-api.ts
src/lib/order-api.ts
src/lib/payment-api.ts
src/lib/pipeline-api.ts
src/lib/product-api.ts
src/lib/purchase-api.ts
src/lib/purchase-order-api.ts
src/lib/recommendation-api.ts
src/lib/settlement-api.ts
src/lib/shipping-api.ts
src/lib/shorts-api.ts
src/lib/story-api.ts
src/lib/trade-api.ts
```

---

## 2. B-2 API 키워드 매핑 결과 (Step 2)

### 2-1. 결제 (payment / toss / 결제)
```
src/app/(retail)/retail/order/new/page.tsx
src/app/(retail)/retail/orders/[id]/page.tsx
src/app/(retail)/retail/orders/page.tsx
src/app/(retail)/retail/payment/fail/page.tsx
src/app/(retail)/retail/payment/page.tsx
src/app/(retail)/retail/payment/success/page.tsx
src/app/(wholesale)/wholesale/orders/[id]/page.tsx
src/app/(wholesale)/wholesale/orders/page.tsx
src/components/order/OrderStatusBadge.tsx
src/components/order/OrderSummaryCard.tsx
src/components/payment/PaymentCancelDialog.tsx
src/components/payment/PaymentDetail.tsx
src/components/payment/PaymentMethodSelector.tsx
src/components/payment/PaymentProcessing.tsx
src/components/payment/PaymentResult.tsx
src/components/payment/PaymentStatusBadge.tsx
src/components/payment/PaymentSummary.tsx
src/components/payment/TossPaymentWidget.tsx
src/lib/payment-api.ts
src/types/order.ts
src/types/payment.ts
```

### 2-2. 배송 (shipping / shipment / 배송 / 송장)
```
src/app/(retail)/retail/addresses/page.tsx
src/app/(retail)/retail/order/new/page.tsx
src/app/(retail)/retail/orders/[id]/page.tsx
src/app/(retail)/retail/orders/page.tsx
src/app/(retail)/retail/payment/page.tsx
src/app/(wholesale)/wholesale/dropship/[id]/page.tsx
src/app/(wholesale)/wholesale/dropship/page.tsx
src/app/(wholesale)/wholesale/orders/[id]/page.tsx
src/app/(wholesale)/wholesale/orders/page.tsx
src/components/address/AddressCard.tsx
src/components/address/AddressForm.tsx
src/components/address/AddressList.tsx
src/components/address/AddressSelectDialog.tsx
src/components/cart/CartSummary.tsx
src/components/dropship/DropshipOrderTable.tsx
src/components/dropship/DropshipStatusBadge.tsx
src/components/fulfillment/DropshipOrderCard.tsx
src/components/fulfillment/DropshipOrderDetail.tsx
src/components/fulfillment/DropshipOrderList.tsx
src/components/fulfillment/DropshipStatusBadge.tsx
src/components/fulfillment/ReturnCreateDialog.tsx
src/components/fulfillment/ReturnRequestDetail.tsx
src/components/order/OrderDetail.tsx
src/components/order/OrderStatusBadge.tsx
src/components/order/OrderSummaryCard.tsx
src/components/order/ShippingForm.tsx
src/components/payment/PaymentSummary.tsx
src/components/shipping/ShipmentCard.tsx
src/components/shipping/ShipmentDetail.tsx
src/components/shipping/ShipmentStatusBadge.tsx
src/components/shipping/ShipmentTimeline.tsx
src/components/shipping/TrackingInput.tsx
src/lib/fulfillment-api.ts
src/lib/shipping-api.ts
src/types/fulfillment.ts
src/types/order.ts
src/types/shipping.ts
```

### 2-3. 정산 (settlement / 정산)
```
src/app/(admin)/admin/settlements/[id]/page.tsx
src/app/(admin)/admin/settlements/page.tsx
src/app/(wholesale)/wholesale/dropship/[id]/page.tsx
src/app/(wholesale)/wholesale/settlements/[id]/page.tsx
src/app/(wholesale)/wholesale/settlements/page.tsx
src/components/layout/admin-layout.tsx
src/components/layout/wholesale-layout.tsx
src/components/settlement/SettlementCard.tsx
src/components/settlement/SettlementDetail.tsx
src/components/settlement/SettlementList.tsx
src/components/settlement/SettlementStatusBadge.tsx
src/components/settlement/SettlementSummaryWidget.tsx
src/lib/settlement-api.ts
src/types/settlement.ts
```

### 2-4. 쇼츠 (short / shorts / 쇼츠)
```
src/app/(retail)/explore/page.tsx
src/app/(retail)/retail/shorts/[id]/page.tsx
src/app/(retail)/retail/shorts/page.tsx
src/app/(wholesale)/wholesale/shorts/[id]/edit/page.tsx
src/app/(wholesale)/wholesale/shorts/new/page.tsx
src/app/(wholesale)/wholesale/shorts/page.tsx
src/components/shorts/CommentItem.tsx
src/components/shorts/MyShortsPage.tsx
src/components/shorts/ProductTagCard.tsx
src/components/shorts/ProductTagOverlay.tsx
src/components/shorts/ShortActions.tsx
src/components/shorts/ShortCard.tsx
src/components/shorts/ShortCommentSheet.tsx
src/components/shorts/ShortEditPage.tsx
src/components/shorts/ShortsFeed.tsx
src/components/shorts/ShortUploadPage.tsx
src/lib/mock-feed.ts
src/lib/shorts-api.ts
src/types/feed.ts
src/types/shorts.ts
```

---

## 3. B-3 API 키워드 매핑 결과 (Step 3)

### 3-1. 거래처 (partnership / trade / 거래처)
```
src/app/(admin)/admin/trade/page.tsx
src/app/(retail)/retail/trade/apply/page.tsx
src/app/(retail)/retail/trade/page.tsx
src/app/(wholesale)/wholesale/trade/applications/[id]/page.tsx
src/app/(wholesale)/wholesale/trade/page.tsx
src/app/(wholesale)/wholesale/trade/partners/[id]/page.tsx
src/components/brand/brand-header.tsx
src/components/layout/admin-layout.tsx
src/components/layout/retail-layout.tsx
src/components/layout/wholesale-layout.tsx
src/components/trade/TradeApplicationDetail.tsx
src/components/trade/TradeApplicationForm.tsx
src/components/trade/TradeApplicationList.tsx
src/components/trade/TradeApplicationStatusBadge.tsx
src/components/trade/TradeApplyDialog.tsx
src/components/trade/TradePartnerDetail.tsx
src/components/trade/TradePartnerList.tsx
src/components/trade/TradePriceTable.tsx
src/components/trade/TradeTierBadge.tsx
src/lib/trade-api.ts
src/types/trade.ts
```

### 3-2. 스토리 (story / stories / 스토리)
```
src/app/(retail)/brand/[slug]/page.tsx
src/app/(retail)/retail/feed/page.tsx
src/app/(retail)/retail/stories/page.tsx
src/app/(wholesale)/wholesale/stories/new/page.tsx
src/app/(wholesale)/wholesale/stories/page.tsx
src/components/layout/wholesale-layout.tsx
src/components/story/MyStoriesPage.tsx
src/components/story/StoryAvatar.tsx
src/components/story/StoryBar.tsx
src/components/story/StoryHighlights.tsx
src/components/story/StoryMediaDisplay.tsx
src/components/story/StoryReactionBar.tsx
src/components/story/StoryUploadPage.tsx
src/components/story/StoryViewersList.tsx
src/components/story/StoryViewer.tsx
src/lib/story-api.ts
src/types/feed.ts
src/types/story.ts
```

### 3-3. AI 추천 (recommend / trend / score / 추천)
```
src/app/(admin)/admin/dashboard/page.tsx
src/app/(retail)/explore/page.tsx
src/app/retail/product/[id]/page.tsx
src/app/(retail)/retail/feed/page.tsx
src/app/(retail)/retail/trends/page.tsx
src/components/feed/feed-card.tsx
src/components/layout/retail-layout.tsx
src/components/mypage/RetailMyPage.tsx
src/components/recommendation/AIFeedBadge.tsx
src/components/recommendation/InterestTags.tsx
src/components/recommendation/RecommendedProductsSection.tsx
src/components/recommendation/SimilarProductsSection.tsx
src/components/recommendation/TrendingCategories.tsx
src/components/recommendation/TrendingKeywords.tsx
src/components/recommendation/TrendingProducts.tsx
src/lib/recommendation-api.ts
src/types/feed.ts
src/types/recommendation.ts
```

### 3-4. 셀러채널 (channel / cafe24 / 채널)
```
src/app/(admin)/admin/channels/[id]/page.tsx
src/app/(admin)/admin/channels/page.tsx
src/app/(admin)/admin/dashboard/page.tsx
src/app/retail/product/[id]/page.tsx
src/app/(wholesale)/wholesale/channels/[id]/page.tsx
src/app/(wholesale)/wholesale/channels/page.tsx
src/app/(wholesale)/wholesale/products/[id]/channels/page.tsx
src/components/channel/ChannelCard.tsx
src/components/channel/ChannelConnectDialog.tsx
src/components/channel/ChannelDetail.tsx
src/components/channel/ChannelList.tsx
src/components/channel/ChannelMappingTable.tsx
src/components/channel/ChannelPushDialog.tsx
src/components/channel/ChannelSettingsForm.tsx
src/components/channel/ChannelStatusBadge.tsx
src/components/channel/ProductChannelBadges.tsx
src/components/layout/admin-layout.tsx
src/components/layout/wholesale-layout.tsx
src/lib/channel-api.ts
src/lib/echo.ts
src/types/admin-product.ts
src/types/channel.ts
```

### 3-5. 드롭십/위탁 (dropship / fulfillment / 위탁)
```
src/app/(admin)/admin/fulfillment/[id]/page.tsx
src/app/(admin)/admin/fulfillment/page.tsx
src/app/(admin)/admin/returns/[id]/page.tsx
src/app/(admin)/admin/returns/page.tsx
src/app/(retail)/retail/dropship/[id]/page.tsx
src/app/(retail)/retail/dropship/page.tsx
src/app/(retail)/retail/returns/[id]/page.tsx
src/app/(retail)/retail/returns/page.tsx
src/app/(wholesale)/wholesale/dropship/[id]/page.tsx
src/app/(wholesale)/wholesale/dropship/page.tsx
src/components/dropship/DropshipOrderTable.tsx
src/components/dropship/DropshipProductCard.tsx
src/components/dropship/DropshipStatusBadge.tsx
src/components/fulfillment/DropshipCreateDialog.tsx
src/components/fulfillment/DropshipOrderCard.tsx
src/components/fulfillment/DropshipOrderDetail.tsx
src/components/fulfillment/DropshipOrderList.tsx
src/components/fulfillment/DropshipStatusBadge.tsx
src/components/fulfillment/FulfillmentDashboardWidget.tsx
src/components/fulfillment/FulfillmentTaskCard.tsx
src/components/fulfillment/FulfillmentTaskDetail.tsx
src/components/fulfillment/FulfillmentTaskList.tsx
src/components/fulfillment/FulfillmentTaskStatusBadge.tsx
src/components/fulfillment/ReturnCreateDialog.tsx
src/components/fulfillment/ReturnRequestDetail.tsx
src/components/fulfillment/ReturnRequestList.tsx
src/components/fulfillment/ReturnStatusBadge.tsx
src/components/layout/admin-layout.tsx
src/components/layout/retail-layout.tsx
src/components/layout/wholesale-layout.tsx
src/lib/dropship-api.ts
src/lib/fulfillment-api.ts
```

### 3-6. 콘텐츠파이프라인 (pipeline / 파이프라인)
```
src/app/(admin)/admin/pipeline/[id]/page.tsx
src/app/(admin)/admin/pipeline/page.tsx
src/app/(admin)/admin/pipeline/queue/page.tsx
src/components/layout/admin-layout.tsx
src/components/pipeline/PipelineDashboardWidget.tsx
src/components/pipeline/PipelineKanbanBoard.tsx
src/components/pipeline/PipelineRejectDialog.tsx
src/components/pipeline/PipelineStatusBadge.tsx
src/components/pipeline/PipelineTaskCard.tsx
src/lib/pipeline-api.ts
```

---

## 4. 페이지 존재 확인 (Step 4)

> **참고**: Next.js App Router 라우트 그룹 `(retail)`, `(wholesale)`, `(admin)` 구조로 인해
> 평탄 경로(`src/app/retail/shorts/`)는 실제로 `src/app/(retail)/retail/shorts/` 아래 존재함.
> 아래 표는 실제 경로 기준으로 확인.

| 확인 경로 | 실제 경로 | 존재 여부 |
|---|---|---|
| retail/payments | `(retail)/retail/payment` | ✅ 존재 (singular) |
| retail/shorts | `(retail)/retail/shorts` | ✅ 존재 |
| wholesale/settlements | `(wholesale)/wholesale/settlements` | ✅ 존재 |
| wholesale/partnerships | 없음 (`wholesale/trade/partners/[id]`로 통합) | ⚠️ 전용 페이지 없음 |
| wholesale/stories | `(wholesale)/wholesale/stories` | ✅ 존재 |
| admin/settlements | `(admin)/admin/settlements` | ✅ 존재 |
| admin/partnerships | 없음 (`admin/trade`로 통합) | ⚠️ 전용 페이지 없음 |

### 실제 B-2/B-3 관련 앱 라우트 디렉토리 전체 목록
```
(admin)/admin/channels
(admin)/admin/channels/[id]
(admin)/admin/fulfillment
(admin)/admin/fulfillment/[id]
(admin)/admin/pipeline
(admin)/admin/pipeline/[id]
(admin)/admin/pipeline/queue
(admin)/admin/purchase
(admin)/admin/purchase/[id]
(admin)/admin/purchase/barcode
(admin)/admin/purchase/orders
(admin)/admin/purchase/receiving
(admin)/admin/purchase/receiving/[id]
(admin)/admin/returns
(admin)/admin/returns/[id]
(admin)/admin/settlements
(admin)/admin/settlements/[id]
(admin)/admin/trade
(retail)/retail/dropship
(retail)/retail/dropship/[id]
(retail)/retail/payment
(retail)/retail/payment/fail
(retail)/retail/payment/success
(retail)/retail/returns
(retail)/retail/returns/[id]
(retail)/retail/shorts
(retail)/retail/shorts/[id]
(retail)/retail/stories
(retail)/retail/trade
(retail)/retail/trade/apply
(retail)/retail/trends
(wholesale)/wholesale/channels
(wholesale)/wholesale/channels/[id]
(wholesale)/wholesale/dropship
(wholesale)/wholesale/dropship/[id]
(wholesale)/wholesale/products/[id]/channels
(wholesale)/wholesale/settlements
(wholesale)/wholesale/settlements/[id]
(wholesale)/wholesale/shorts
(wholesale)/wholesale/shorts/[id]
(wholesale)/wholesale/shorts/[id]/edit
(wholesale)/wholesale/shorts/new
(wholesale)/wholesale/stories
(wholesale)/wholesale/stories/new
(wholesale)/wholesale/trade
(wholesale)/wholesale/trade/applications/[id]
(wholesale)/wholesale/trade/partners/[id]
```

---

## 5. 12개 API 영역 매트릭스 (Step 5)

### 백엔드 엔드포인트 수 집계

| # | API 영역 | 백엔드 라우트 | 백엔드 EP 수 |
|---|---|---|---|
| 1 | 결제 | `/api/payments` (6) + callback (1) | **7 EP** |
| 2 | 배송+배송지 | `/api/shipments` (4) + `/api/shipping-addresses` (5) | **9 EP** |
| 3 | 정산 | `/api/settlements` | **6 EP** |
| 4 | 쇼츠 | `/api/shorts` | **14 EP** |
| 5 | 거래처 | `/api/trade-applications` (4) + `/api/partnerships` (4) | **8 EP** |
| 6 | 스토리 | `/api/stories` | **6 EP** |
| 7 | AI 추천 | `/api/recommendations` + `/api/trends` + `/api/user-interests` | **4 EP** |
| 8 | 셀러채널 | `/api/channels` (7) + `/api/cafe24` (7) | **14 EP** |
| 9 | 드롭십+반품 | `/api/dropship` (7) + `/api/returns` (7) | **14 EP** |
| 10 | 풀필먼트 | `/api/fulfillment` | **6 EP** |
| 11 | 콘텐츠파이프라인 | `/api/pipeline` | **14 EP** |
| 12 | 구매발주 | `/api/purchase-orders` (8) + `/api/inbound-receipts` (5) + `/api/barcodes` (5) | **18 EP** |

**총 백엔드 EP 합계: 120 EP**

---

### 12개 API 영역 연동 매트릭스

| API 영역 | 백엔드 EP 수 | 프론트 lib 함수 수 | 프론트 컴포넌트 수 | 페이지 존재 | API 호출 연동 | 상태 |
|---|---|---|---|---|---|---|
| **결제** | 7 EP | 5 (`payment-api.ts`) | 8개 (`components/payment/`) | ✅ retail/payment, success, fail | ✅ preparePayment, confirmPayment, getPayment, cancelPayment, getOrderPayment | ✅ **연동** |
| **배송+배송지** | 9 EP | 11 (`shipping-api.ts`) | 9개 (`components/shipping/`, `components/address/`) | ✅ retail/addresses, retail/orders/[id] | ✅ getShipment, getTrackingInfo, createShipment, updateTracking, updateShipmentStatus, getShippingAddresses, createShippingAddress, updateShippingAddress, deleteShippingAddress, setDefaultAddress, getOrderShipment | ✅ **연동** |
| **정산** | 6 EP | 6 (`settlement-api.ts`) | 5개 (`components/settlement/`) | ✅ wholesale/settlements, admin/settlements | ✅ getSettlements, getSettlement, createSettlement, confirmSettlement, getSettlementItems, getSettlementLogs | ✅ **연동** |
| **쇼츠** | 14 EP | 11 (`shorts-api.ts`) | 9개 (`components/shorts/`) | ✅ retail/shorts, wholesale/shorts (업로드/편집 포함) | ✅ 11/14 EP 연동 (getShortsFeed, getShort, getMyShorts, createShort, updateShort, deleteShort, toggleShortLike, recordShortView, getShortComments, addShortComment, deleteShortComment) | ⚠️ **부분연동** (viewStats, addTag, removeTag 3EP 미연동) |
| **거래처** | 8 EP | 9 (`trade-api.ts`) | 9개 (`components/trade/`) | ✅ retail/trade, wholesale/trade, wholesale/trade/partners/[id], admin/trade | ✅ applyTrade, getApplications, getApplicationDetail, approveApplication, rejectApplication, getPartners, getPartnerDetail, setTradePrice, getTradePrice | ✅ **연동** (partnerships 전용 페이지 없으나 admin/trade+wholesale/trade/partners 로 통합 처리) |
| **스토리** | 6 EP | 8 (`story-api.ts`) | 10개 (`components/story/`) | ✅ retail/stories, wholesale/stories (업로드 포함) | ✅ 6/8 함수 연동 (getStoryFeed, getUserStories, getMyStories, createStory, deleteStory, recordView) | ⚠️ **부분연동** (frontend `react()`, `toggleHighlight()` 함수 있으나 백엔드 EP 미구현) |
| **AI 추천** | 4 EP | 7 (`recommendation-api.ts`) | 7개 (`components/recommendation/`) | ✅ retail/trends, explore | ✅ 4/7 함수 연동 (getRecommendedProducts→/recommendations, getTrends→/trends, getMyInterests→/user-interests, updateInterest) | ⚠️ **부분연동** (getSimilarProducts, getTrendKeywords, getTrendCategories, getTrendingProducts — 백엔드 EP 미구현) |
| **셀러채널** | 14 EP | 13 (`channel-api.ts`) | 9개 (`components/channel/`) | ✅ wholesale/channels, admin/channels, wholesale/products/[id]/channels | ✅ getChannels, connectChannel, getAuthUrl, getChannelDetail, disconnectChannel, updateChannelSettings, pushProduct, pushBulk, deleteChannelProduct, syncChannel, getMappings, refreshToken, getProductChannels | ✅ **연동** |
| **드롭십+반품** | 14 EP | 6 (`dropship-api.ts`) + 20 (`fulfillment-api.ts`) | 13개 (`components/dropship/`, `components/fulfillment/`) | ✅ retail/dropship, wholesale/dropship, retail/returns, admin/returns | ✅ 전 EP 연동 (dropship CRUD, returns CRUD, 상태관리, 송장추적) | ✅ **연동** |
| **풀필먼트** | 6 EP | 포함 `fulfillment-api.ts` | 7개 (`components/fulfillment/FulfillmentTask*`) | ✅ admin/fulfillment, admin/fulfillment/[id] | ✅ getFulfillmentDashboard, createFulfillmentTask, getFulfillmentTasks, getFulfillmentTask, assignFulfillmentTask, updateFulfillmentStatus | ✅ **연동** |
| **콘텐츠파이프라인** | 14 EP | 10 (`pipeline-api.ts`) | 5개 (`components/pipeline/`) | ✅ admin/pipeline, admin/pipeline/[id], admin/pipeline/queue | ✅ getPipelineDashboard, getPipelineQueue, assignPipelineTask, updatePipelineStatus, rejectPipelineItem, approvePipelineItem, publishPipelineItem, getPipelineStats, getPipelineByProduct, bulkAssignPipeline | ✅ **연동** |
| **구매발주** | 18 EP | 2 (`purchase-order-api.ts`) + `purchase-api.ts` 별도 | 8개 (`components/purchase/`, `components/admin/purchase-detail/`) | ✅ admin/purchase, admin/purchase/orders, admin/purchase/[id], admin/purchase/receiving, admin/purchase/barcode | ⚠️ purchase-order-api.ts에 2함수만 (getPurchaseOrder, updatePurchaseOrderStatus), purchase-api.ts가 보완하나 18EP 대비 커버리지 부족 | ⚠️ **부분연동** |

---

## 6. 누락 페이지 목록 (Missing Pages)

### 독립 페이지 미존재 (기능은 다른 페이지로 통합)

| 누락 경로 | 통합된 실제 경로 | 영향 |
|---|---|---|
| `wholesale/partnerships` | `wholesale/trade/partners/[id]` | 낮음 — 파트너 상세는 trade 경로로 접근 가능 |
| `admin/partnerships` | `admin/trade` | 낮음 — admin/trade에서 모든 거래처 관리 |

### 프론트엔드 함수 있으나 백엔드 EP 미구현

| 프론트 함수 | 해당 lib 파일 | 백엔드 EP | 우선순위 |
|---|---|---|---|
| `getSimilarProducts()` | `recommendation-api.ts` | 유사상품 추천 EP 없음 | **P1** (상품상세 핵심 기능) |
| `getTrendingProducts()` | `recommendation-api.ts` | 트렌딩 상품 EP 없음 | P2 |
| `getTrendKeywords()` | `recommendation-api.ts` | 트렌드 키워드 EP 없음 | P2 |
| `getTrendCategories()` | `recommendation-api.ts` | 트렌드 카테고리 EP 없음 | P2 |
| `react()` — 리액션 | `story-api.ts` | 스토리 리액션 EP 없음 | P3 |
| `toggleHighlight()` — 하이라이트 | `story-api.ts` | 스토리 하이라이트 EP 없음 | P3 |

### 백엔드 EP 있으나 프론트 커버리지 부족

| 백엔드 EP | 영역 | 현황 |
|---|---|---|
| `GET /api/shorts/{id}/views` | 쇼츠 | `shorts-api.ts` 미연동 |
| `POST /api/shorts/{id}/tags` | 쇼츠 | `shorts-api.ts` 미연동 |
| `DELETE /api/shorts/{id}/tags/{pid}` | 쇼츠 | `shorts-api.ts` 미연동 |
| `GET /api/purchase-orders` (목록) | 구매발주 | `purchase-order-api.ts`에 없음 |
| `POST /api/purchase-orders` (생성) | 구매발주 | `purchase-order-api.ts`에 없음 |
| `PUT /api/purchase-orders/{id}` (수정) | 구매발주 | `purchase-order-api.ts`에 없음 |
| `POST /api/purchase-orders/{id}/cancel` | 구매발주 | `purchase-order-api.ts`에 없음 |
| `POST /api/purchase-orders/{id}/approve` | 구매발주 | `purchase-order-api.ts`에 없음 |

---

## 7. 종합 평가

### 연동 상태 요약

| 상태 | 영역 수 | 영역 목록 |
|---|---|---|
| ✅ 완전 연동 | 8 | 결제, 배송+배송지, 정산, 거래처, 셀러채널, 드롭십+반품, 풀필먼트, 콘텐츠파이프라인 |
| ⚠️ 부분 연동 | 4 | 쇼츠 (3EP 미연동), 스토리 (2함수 백엔드 미구현), AI추천 (4함수 백엔드 미구현), 구매발주 (purchase-order-api.ts 커버리지 부족) |
| ❌ 미구현 | 0 | 없음 |

### 핵심 발견

1. **전반적 연동 수준 우수**: 12개 영역 중 8개(67%)가 백엔드 EP와 프론트엔드 페이지/API 함수가 모두 완비된 상태.

2. **AI 추천 백엔드 부족**: `recommendation-api.ts`의 7개 함수 중 4개(`getSimilarProducts`, `getTrendKeywords`, `getTrendCategories`, `getTrendingProducts`)에 대응하는 백엔드 EP 미구현. `retail/product/[id]`에서 유사상품 추천은 고객 경험에 직결되므로 **P1 대응 권장**.

3. **구매발주 API 파일 이원화**: `purchase-api.ts`와 `purchase-order-api.ts`가 분리되어 있어 커버리지 파악이 어려움. 통합 또는 명확한 역할 분리 필요.

4. **스토리 리액션/하이라이트**: 프론트엔드 UI 컴포넌트(`StoryReactionBar.tsx`, `StoryHighlights.tsx`)는 구현되어 있으나 백엔드 API 없음. 프론트 dead code 가능성.

5. **쇼츠 태그/조회통계**: 백엔드에 `addTag`, `removeTag`, `viewStats` EP가 존재하나 프론트 API 함수 미연동.

6. **파트너십 전용 페이지**: `admin/partnerships`, `wholesale/partnerships` 독립 경로 없음. 현재 trade 경로로 통합 처리 중 — 기능 누락은 없으나 직관적 네비게이션 개선 고려 가능.

---

## 8. 권장 후속 작업

| 우선순위 | 작업 | 영역 |
|---|---|---|
| P1 | `getSimilarProducts` 백엔드 EP 구현 (`GET /api/products/{id}/similar`) | AI 추천 |
| P2 | `getTrendKeywords`, `getTrendCategories`, `getTrendingProducts` 백엔드 EP 구현 | AI 추천 |
| P2 | 쇼츠 태그 EP 프론트 연동 (`addTag`, `removeTag`, `viewStats`) | 쇼츠 |
| P3 | 스토리 리액션 백엔드 EP 구현 또는 프론트 dead code 제거 | 스토리 |
| P3 | `purchase-order-api.ts` 커버리지 확장 (CRUD 전체) | 구매발주 |

---

*보고서 생성: 2026-03-06 | FRONTEND-AUDIT-001 | newtalk-v2*
