# FRONTEND-AUDIT-001 — Next.js 프론트엔드 B2/B3 API 연동 감사 보고서

**작성일**: 2026-03-05
**Task ID**: 8
**우선순위**: P1-HIGH
**감사 범위**: `/srv/newtalk-v2/frontend/src`

---

## 1. 파일 통계 (Step 1)

| 항목 | 수치 |
|------|------|
| 전체 TS/TSX 파일 수 | **287개** |
| `src/app` 디렉토리 수 | **93개** |
| `*-api.ts` 파일 수 | **17개** |

### 발견된 API 클라이언트 파일 목록

```
src/lib/brand-api.ts
src/lib/cart-api.ts
src/lib/channel-api.ts
src/lib/content-api.ts
src/lib/dm-api.ts
src/lib/feed-api.ts
src/lib/fulfillment-api.ts
src/lib/order-api.ts
src/lib/payment-api.ts
src/lib/product-api.ts
src/lib/purchase-api.ts
src/lib/purchase-order-api.ts
src/lib/recommendation-api.ts
src/lib/shipping-api.ts
src/lib/shorts-api.ts
src/lib/story-api.ts
src/lib/trade-api.ts
```

---

## 2. B-2 API 키워드 매핑 (Step 2)

### B-2 결제 (payment / toss / 결제)

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

### B-2 배송 (shipping / shipment / 배송 / 송장)

```
src/app/(retail)/retail/addresses/page.tsx
src/app/(retail)/retail/order/new/page.tsx
src/app/(retail)/retail/orders/[id]/page.tsx
src/app/(retail)/retail/orders/page.tsx
src/app/(retail)/retail/payment/page.tsx
src/app/(wholesale)/wholesale/orders/[id]/page.tsx
src/app/(wholesale)/wholesale/orders/page.tsx
src/components/address/AddressCard.tsx
src/components/address/AddressForm.tsx
src/components/address/AddressList.tsx
src/components/address/AddressSelectDialog.tsx
src/components/cart/CartSummary.tsx
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

### B-2 정산 (settlement / 정산)

```
src/components/layout/admin-layout.tsx  ← 내비게이션 링크만 존재
```

### B-2 쇼츠 (short / shorts / 쇼츠)

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
src/components/shorts/ShortsFeed.tsx
src/components/shorts/ShortUploadPage.tsx
src/lib/mock-feed.ts
src/lib/shorts-api.ts
src/types/feed.ts
src/types/shorts.ts
```

---

## 3. B-3 API 키워드 매핑 (Step 3)

### B-3 거래처 (partnership / trade / 거래처)

```
src/app/(admin)/admin/trade/page.tsx
src/app/(retail)/retail/trade/apply/page.tsx
src/app/(retail)/retail/trade/page.tsx
src/app/(wholesale)/wholesale/trade/applications/[id]/page.tsx
src/app/(wholesale)/wholesale/trade/page.tsx
src/app/(wholesale)/wholesale/trade/partners/[id]/page.tsx
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

### B-3 스토리 (story / stories / 스토리)

```
src/app/(retail)/brand/[slug]/page.tsx
src/app/(retail)/retail/feed/page.tsx
src/app/(retail)/retail/stories/page.tsx
src/app/(wholesale)/wholesale/stories/new/page.tsx
src/app/(wholesale)/wholesale/stories/page.tsx
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

### B-3 AI 추천 (recommend / trend / score / 추천)

```
src/app/(admin)/admin/dashboard/page.tsx
src/app/(retail)/explore/page.tsx
src/app/retail/product/[id]/page.tsx
src/app/(retail)/retail/feed/page.tsx
src/app/(retail)/retail/trends/page.tsx
src/components/feed/feed-card.tsx
src/components/mypage/RetailMyPage.tsx
src/components/recommendation/AIFeedBadge.tsx
src/components/recommendation/InterestTags.tsx
src/components/recommendation/RecommendedProductsSection.tsx
src/components/recommendation/SimilarProductsSection.tsx
src/components/recommendation/TrendingCategories.tsx
src/components/recommendation/TrendingKeywords.tsx
src/components/recommendation/TrendingProducts.tsx
src/lib/recommendation-api.ts
src/types/recommendation.ts
```

### B-3 셀러채널 (channel / cafe24 / 채널)

```
src/app/(admin)/admin/channels/[id]/page.tsx
src/app/(admin)/admin/channels/page.tsx
src/app/(admin)/admin/dashboard/page.tsx
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
src/lib/channel-api.ts
src/types/channel.ts
```

### B-3 드롭십 (dropship / fulfillment / 위탁)

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
src/lib/fulfillment-api.ts
```

### B-3 콘텐츠파이프라인 (pipeline / 파이프라인)

직접 "pipeline" 키워드 검색 결과 없음. "content" 키워드로 확장 검색:

```
src/app/(wholesale)/wholesale/content/[id]/edit/page.tsx
src/app/(wholesale)/wholesale/content/new/page.tsx
src/app/(wholesale)/wholesale/content/page.tsx
src/components/content/ContentCard.tsx
src/components/content/ContentEditor.tsx
src/components/content/ContentList.tsx
src/components/content/ContentPreview.tsx
src/components/content/MediaUploader.tsx
src/components/content/ProductTagSelector.tsx
src/lib/content-api.ts
```

---

## 4. 페이지 존재 확인 (Step 4)

### 지시서 체크 목록

| 경로 (절대 경로 기준) | 존재 여부 | 비고 |
|-----------------------|-----------|------|
| `src/app/retail/payments/` | **MISSING** | `src/app/(retail)/retail/payment/` (단수)로 대체 존재 |
| `src/app/retail/shorts/` | **MISSING** | `src/app/(retail)/retail/shorts/` (route group 내)로 존재 |
| `src/app/wholesale/settlements/` | **MISSING** | 프론트 미구현 |
| `src/app/wholesale/partnerships/` | **MISSING** | `src/app/(wholesale)/wholesale/trade/`로 대체 존재 |
| `src/app/wholesale/stories/` | **MISSING** | `src/app/(wholesale)/wholesale/stories/`로 존재 |
| `src/app/admin/settlements/` | **MISSING** | 프론트 미구현 |
| `src/app/admin/partnerships/` | **MISSING** | `src/app/(admin)/admin/trade/`로 대체 존재 |

> **주의**: Next.js route group `(retail)`, `(wholesale)`, `(admin)` 패턴 사용으로 직접 경로 ls 시 MISSING으로 표시되나, 실제 route group 내에 존재하는 경우가 있음.

### 실제 라우트 그룹 기준 페이지 존재 현황

| 영역 | 실제 경로 | 존재 여부 |
|------|-----------|-----------|
| 결제 (retail) | `src/app/(retail)/retail/payment/` | ✅ 존재 (page, success, fail) |
| 쇼츠 (retail) | `src/app/(retail)/retail/shorts/` | ✅ 존재 |
| 쇼츠 (wholesale) | `src/app/(wholesale)/wholesale/shorts/` | ✅ 존재 |
| 정산 (wholesale) | `src/app/(wholesale)/wholesale/settlements/` | **❌ 미구현** |
| 정산 (admin) | `src/app/(admin)/admin/settlements/` | **❌ 미구현** |
| 거래처 (retail) | `src/app/(retail)/retail/trade/` | ✅ 존재 |
| 거래처 (wholesale) | `src/app/(wholesale)/wholesale/trade/` | ✅ 존재 |
| 거래처 (admin) | `src/app/(admin)/admin/trade/` | ✅ 존재 |
| 스토리 (retail) | `src/app/(retail)/retail/stories/` | ✅ 존재 |
| 스토리 (wholesale) | `src/app/(wholesale)/wholesale/stories/` | ✅ 존재 |
| AI 추천 (retail) | `src/app/(retail)/retail/trends/` | ✅ 존재 |
| 셀러채널 (wholesale) | `src/app/(wholesale)/wholesale/channels/` | ✅ 존재 |
| 셀러채널 (admin) | `src/app/(admin)/admin/channels/` | ✅ 존재 |
| 드롭십 (retail) | `src/app/(retail)/retail/dropship/` | ✅ 존재 |
| 드롭십 (wholesale) | `src/app/(wholesale)/wholesale/dropship/` | ✅ 존재 |
| 풀필먼트 (admin) | `src/app/(admin)/admin/fulfillment/` | ✅ 존재 |
| 반품 (retail) | `src/app/(retail)/retail/returns/` | ✅ 존재 |
| 반품 (admin) | `src/app/(admin)/admin/returns/` | ✅ 존재 |
| 콘텐츠 (wholesale) | `src/app/(wholesale)/wholesale/content/` | ✅ 존재 |
| 파이프라인 (admin) | `src/app/(admin)/admin/pipeline/` | **❌ 미구현** |
| 배송 전용 목록 | `src/app/(retail)/retail/shipments/` | **❌ 미구현** (주문 상세에 통합) |

---

## 5. 12개 API 영역 연동 매트릭스 (Step 5)

> **라우트 수**: `src/routes/api.php` (Laravel) 기준 `Route::` 선언 수
> **프론트 파일 수**: `src/lib/*-api.ts` export 함수 수
> **페이지 존재**: Next.js route group 기준
> **API 호출 연동**: 전용 `*-api.ts` 클라이언트 파일 존재 여부 + 페이지에서 임포트 여부

| # | API 영역 | 백엔드 EP 수 | 프론트 API 파일 | 함수 수 | 페이지 존재 | API 호출 연동 | 상태 |
|---|----------|-------------|----------------|---------|------------|--------------|------|
| 1 | **결제** (Payment) | 7 EP | `payment-api.ts` | 5 | ✅ `retail/payment/` | ✅ 연동 | **연동 완료** |
| 2 | **배송** (Shipping/Shipment) | 9 EP (ShipmentCtrl 4 + AddrCtrl 5) | `shipping-api.ts` | 11 | ⚠️ 전용 페이지 없음 (주문상세 통합) | ✅ 연동 | **페이지 미분리** |
| 3 | **정산** (Settlement) | 6 EP | **없음** | 0 | ❌ 페이지 없음 | ❌ 미연동 | **❌ 미구현** |
| 4 | **쇼츠** (Shorts) | 14 EP | `shorts-api.ts` | 11 | ✅ `retail/shorts/`, `wholesale/shorts/` | ✅ 연동 | **연동 완료** |
| 5 | **거래처** (Trade) | 8 EP | `trade-api.ts` | 9 | ✅ `retail/trade/`, `wholesale/trade/`, `admin/trade/` | ✅ 연동 | **연동 완료** |
| 6 | **스토리** (Story) | 6 EP | `story-api.ts` | 8 | ✅ `retail/stories/`, `wholesale/stories/` | ✅ 연동 | **연동 완료** |
| 7 | **AI 추천** (Recommendation) | 4 EP | `recommendation-api.ts` | 7 | ✅ `retail/trends/` | ✅ 연동 | **연동 완료** |
| 8 | **셀러채널** (Channel) | 7 EP | `channel-api.ts` | 13 | ✅ `wholesale/channels/`, `admin/channels/` | ✅ 연동 | **연동 완료** |
| 9 | **드롭십** (Dropship) | 7 EP | `fulfillment-api.ts` (공용) | 20 | ✅ `retail/dropship/`, `wholesale/dropship/` | ✅ 연동 | **연동 완료** |
| 10 | **풀필먼트** (Fulfillment) | 6 EP | `fulfillment-api.ts` (공용) | — | ✅ `admin/fulfillment/` | ✅ 연동 | **연동 완료** |
| 11 | **반품** (Return) | 7 EP | `fulfillment-api.ts` (공용) | — | ✅ `retail/returns/`, `admin/returns/` | ✅ 연동 | **연동 완료** |
| 12 | **콘텐츠파이프라인** (Content Pipeline) | 10 EP | `content-api.ts` | 7 | ⚠️ `wholesale/content/` 존재, admin pipeline 페이지 없음 | ⚠️ 부분 연동 | **⚠️ 부분 미구현** |

---

## 6. 누락 페이지 및 미구현 목록

### 🔴 완전 미구현 (백엔드 API 있으나 프론트 없음)

| 영역 | 백엔드 EP | 누락 항목 | 우선순위 |
|------|-----------|-----------|---------|
| **정산** | 6 EP (SettlementController) | `settlement-api.ts` 없음, `wholesale/settlements/` 없음, `admin/settlements/` 없음 | P0 |

### 🟡 부분 미구현 (일부 연동 누락)

| 영역 | 백엔드 EP | 누락 항목 | 우선순위 |
|------|-----------|-----------|---------|
| **콘텐츠파이프라인** | 10 EP (ContentPipelineController) | `admin/pipeline/` 페이지 없음, content-api.ts에 pipeline 전용 함수 없음 | P1 |
| **배송** | 9 EP | 배송 전용 목록 페이지 없음 (주문 상세에 통합) | P2 |

### 🟢 정상 연동 (9/12 영역)

결제, 쇼츠, 거래처, 스토리, AI 추천, 셀러채널, 드롭십, 풀필먼트, 반품

---

## 7. 요약

| 구분 | 수치 |
|------|------|
| 전체 감사 영역 | 12개 |
| 완전 연동 완료 | **9개** (75%) |
| 부분 미구현 | **2개** (17%) |
| 완전 미구현 | **1개** (8%) |

**핵심 액션 아이템**:
1. `settlement-api.ts` 생성 및 `wholesale/settlements/`, `admin/settlements/` 페이지 구현 (P0)
2. `admin/pipeline/` 페이지 및 `content-api.ts`에 ContentPipeline 함수 추가 (P1)
3. 배송 전용 목록 페이지 필요 여부 검토 (P2, 선택적)
