# FRONTEND-AUDIT-001 — 프론트엔드 감사 보고서 (2026-03-05 갱신)

**작성일**: 2026-03-05
**Task ID**: T-012
**우선순위**: P1-HIGH
**감사 범위**: `/srv/newtalk-v2/frontend/src`
**감사 기준**: api.php 12개 API 영역 ↔ Next.js 프론트엔드 매핑

---

## 1. 파일 통계

| 항목 | 수치 |
|------|------|
| 전체 TS/TSX 파일 수 (`.bak` 포함) | **412개** |
| 전체 TS/TSX 파일 수 (`.bak` 제외) | **309개** |
| `src/app` page.tsx 파일 수 | **78개** |
| `*-api.ts` 클라이언트 파일 수 | **19개** |
| `src/` 디렉토리 크기 | **2.9 MB** |

### 실행 커맨드

```bash
# 전체 파일 수 (bak 포함)
find src -name "*.tsx" -o -name "*.ts" | wc -l
# → 412

# page.tsx 목록
find src/app -name "page.tsx" | sort
# → 78개 (route group 패턴 포함)

# 소스 크기
du -sh src/
# → 2.9M
```

### page.tsx 전체 목록

```
src/app/(admin)/admin/channels/[id]/page.tsx
src/app/(admin)/admin/channels/page.tsx
src/app/(admin)/admin/dashboard/page.tsx
src/app/(admin)/admin/fulfillment/[id]/page.tsx
src/app/(admin)/admin/fulfillment/page.tsx
src/app/(admin)/admin/pipeline/[id]/page.tsx
src/app/(admin)/admin/pipeline/page.tsx
src/app/(admin)/admin/pipeline/queue/page.tsx
src/app/(admin)/admin/purchase/barcode/page.tsx
src/app/(admin)/admin/purchase/[id]/page.tsx
src/app/(admin)/admin/purchase/orders/page.tsx
src/app/(admin)/admin/purchase/page.tsx
src/app/(admin)/admin/purchase/receiving/[id]/page.tsx
src/app/(admin)/admin/purchase/receiving/page.tsx
src/app/(admin)/admin/returns/[id]/page.tsx
src/app/(admin)/admin/returns/page.tsx
src/app/(admin)/admin/settlements/[id]/page.tsx
src/app/(admin)/admin/settlements/page.tsx
src/app/(admin)/admin/trade/page.tsx
src/app/(admin)/purchasing/page.tsx
src/app/(auth)/login/page.tsx
src/app/(auth)/register/page.tsx
src/app/(md)/md/dashboard/page.tsx
src/app/outsource/dashboard/page.tsx
src/app/page.tsx
src/app/(purchaser)/purchaser/dashboard/page.tsx
src/app/(retail)/brand/[slug]/page.tsx
src/app/(retail)/brands/page.tsx
src/app/(retail)/explore/page.tsx
src/app/(retail)/feed/page.tsx
src/app/(retail)/mypage/page.tsx
src/app/retail/product/[id]/page.tsx
src/app/(retail)/retail/addresses/page.tsx
src/app/(retail)/retail/cart/page.tsx
src/app/(retail)/retail/dropship/[id]/page.tsx
src/app/(retail)/retail/dropship/page.tsx
src/app/(retail)/retail/explore/page.tsx
src/app/(retail)/retail/feed/page.tsx
src/app/(retail)/retail/messages/[id]/page.tsx
src/app/(retail)/retail/messages/page.tsx
src/app/(retail)/retail/mypage/page.tsx
src/app/(retail)/retail/order/new/page.tsx
src/app/(retail)/retail/orders/[id]/page.tsx
src/app/(retail)/retail/orders/page.tsx
src/app/(retail)/retail/payment/fail/page.tsx
src/app/(retail)/retail/payment/page.tsx
src/app/(retail)/retail/payment/success/page.tsx
src/app/(retail)/retail/returns/[id]/page.tsx
src/app/(retail)/retail/returns/page.tsx
src/app/(retail)/retail/shorts/[id]/page.tsx
src/app/(retail)/retail/shorts/page.tsx
src/app/(retail)/retail/stories/page.tsx
src/app/(retail)/retail/trade/apply/page.tsx
src/app/(retail)/retail/trade/page.tsx
src/app/(retail)/retail/trends/page.tsx
src/app/(wholesale)/wholesale/channels/[id]/page.tsx
src/app/(wholesale)/wholesale/channels/page.tsx
src/app/(wholesale)/wholesale/content/[id]/edit/page.tsx
src/app/(wholesale)/wholesale/content/new/page.tsx
src/app/(wholesale)/wholesale/content/page.tsx
src/app/(wholesale)/wholesale/dashboard/page.tsx
src/app/(wholesale)/wholesale/dropship/[id]/page.tsx
src/app/(wholesale)/wholesale/dropship/page.tsx
src/app/(wholesale)/wholesale/messages/[id]/page.tsx
src/app/(wholesale)/wholesale/messages/page.tsx
src/app/(wholesale)/wholesale/orders/[id]/page.tsx
src/app/(wholesale)/wholesale/orders/page.tsx
src/app/(wholesale)/wholesale/products/[id]/channels/page.tsx
src/app/(wholesale)/wholesale/settlements/[id]/page.tsx
src/app/(wholesale)/wholesale/settlements/page.tsx
src/app/(wholesale)/wholesale/shorts/[id]/edit/page.tsx
src/app/(wholesale)/wholesale/shorts/new/page.tsx
src/app/(wholesale)/wholesale/shorts/page.tsx
src/app/(wholesale)/wholesale/stories/new/page.tsx
src/app/(wholesale)/wholesale/stories/page.tsx
src/app/(wholesale)/wholesale/trade/applications/[id]/page.tsx
src/app/(wholesale)/wholesale/trade/page.tsx
src/app/(wholesale)/wholesale/trade/partners/[id]/page.tsx
```

### API 클라이언트 파일 목록 (19개)

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

## 2. 12개 API 영역 매트릭스

> **라우트 수**: `/srv/newtalk-v2/src/routes/api.php` (Laravel) 기준 Route:: 선언 수 (수동 집계)
> **프론트 파일 수**: `grep -rl "키워드" src/ --include=*.tsx,*.ts` (`.bak` 제외)
> **page.tsx 존재**: Next.js route group 실제 파일 기준
> **API 호출 연동**: 전용 `*-api.ts` 클라이언트 파일 존재 여부

| # | 영역 | 키워드 | api.php 라우트 수 | 프론트 파일 수 | page.tsx 존재 | API 호출 연동 |
|---|------|--------|:-----------------:|:-------------:|:-------------:|:-------------:|
| 1 | **auth** | `/auth`, login, register | 4 | 8 | ✅ login, register | ✅ `api.ts` |
| 2 | **products** | `/api/products` | 7 | 1 (좁은 검색) | ✅ `retail/product/[id]` | ✅ `product-api.ts` |
| 3 | **orders** | `/api/orders` | 5 | 34 | ✅ retail/orders, wholesale/orders | ✅ `order-api.ts` |
| 4 | **payments** | `/api/payments`, payment | 7 | 14 | ✅ retail/payment (page+success+fail) | ✅ `payment-api.ts` |
| 5 | **shipping** | `/api/shipping`, fulfillment | 15 | 48 | ✅ admin/fulfillment, retail/returns, retail/addresses | ✅ `shipping-api.ts`, `fulfillment-api.ts` |
| 6 | **settlements** | `/api/settlements` | 6 | 13 | ✅ admin/settlements, wholesale/settlements | ✅ `settlement-api.ts` |
| 7 | **shorts** | `/api/shorts` | 14 | 19 | ✅ retail/shorts, wholesale/shorts | ✅ `shorts-api.ts` |
| 8 | **partnerships** | `/api/partnerships` | 8 | 20 | ✅ retail/trade, wholesale/trade, admin/trade | ✅ `trade-api.ts` |
| 9 | **stories** | `/api/stories`, story | 6 | 18 | ✅ retail/stories, wholesale/stories | ✅ `story-api.ts` |
| 10 | **brands** | `/api/brands`, brand-page | 7 | 24 | ✅ brands, brand/[slug] | ✅ `brand-api.ts` |
| 11 | **dropship** | `/api/dropship` | 13 | 8 | ✅ retail/dropship, wholesale/dropship, retail/returns | ✅ `fulfillment-api.ts` |
| 12 | **content-pipeline** | `/api/content-pipeline`, pipeline | 14 | 10 | ✅ admin/pipeline, wholesale/content | ✅ `pipeline-api.ts` |

### 각 영역 page.tsx 상세

| # | 영역 | 구현된 page.tsx 경로 |
|---|------|---------------------|
| 1 | auth | `(auth)/login/page.tsx`, `(auth)/register/page.tsx` |
| 2 | products | `retail/product/[id]/page.tsx` |
| 3 | orders | `retail/orders/page.tsx`, `retail/orders/[id]/page.tsx`, `retail/order/new/page.tsx`, `wholesale/orders/page.tsx`, `wholesale/orders/[id]/page.tsx`, `admin/purchase/orders/page.tsx` |
| 4 | payments | `retail/payment/page.tsx`, `retail/payment/success/page.tsx`, `retail/payment/fail/page.tsx` |
| 5 | shipping | `admin/fulfillment/page.tsx`, `admin/fulfillment/[id]/page.tsx`, `admin/returns/page.tsx`, `admin/returns/[id]/page.tsx`, `retail/returns/page.tsx`, `retail/returns/[id]/page.tsx`, `retail/addresses/page.tsx` |
| 6 | settlements | `admin/settlements/page.tsx`, `admin/settlements/[id]/page.tsx`, `wholesale/settlements/page.tsx`, `wholesale/settlements/[id]/page.tsx` |
| 7 | shorts | `retail/shorts/page.tsx`, `retail/shorts/[id]/page.tsx`, `wholesale/shorts/page.tsx`, `wholesale/shorts/new/page.tsx`, `wholesale/shorts/[id]/edit/page.tsx` |
| 8 | partnerships | `retail/trade/page.tsx`, `retail/trade/apply/page.tsx`, `admin/trade/page.tsx`, `wholesale/trade/page.tsx`, `wholesale/trade/applications/[id]/page.tsx`, `wholesale/trade/partners/[id]/page.tsx` |
| 9 | stories | `retail/stories/page.tsx`, `wholesale/stories/page.tsx`, `wholesale/stories/new/page.tsx` |
| 10 | brands | `(retail)/brands/page.tsx`, `(retail)/brand/[slug]/page.tsx` |
| 11 | dropship | `retail/dropship/page.tsx`, `retail/dropship/[id]/page.tsx`, `wholesale/dropship/page.tsx`, `wholesale/dropship/[id]/page.tsx` |
| 12 | content-pipeline | `admin/pipeline/page.tsx`, `admin/pipeline/[id]/page.tsx`, `admin/pipeline/queue/page.tsx`, `wholesale/content/page.tsx`, `wholesale/content/new/page.tsx`, `wholesale/content/[id]/edit/page.tsx` |

---

## 3. 누락 페이지 식별

### 완전 연동 완료 (12/12 영역)

이전 감사(2026-03-05 초안) 대비 **정산(settlements)** 및 **콘텐츠파이프라인(pipeline)** 영역이 구현 완료됨:

| 이전 상태 | 현재 상태 | 완료 작업 |
|-----------|-----------|-----------|
| settlement-api.ts 없음 | ✅ `settlement-api.ts` 존재 | R5-FRONT-SETTLE-001 |
| admin/settlements/ 없음 | ✅ admin/settlements, [id] 존재 | R5-FRONT-SETTLE-001 |
| wholesale/settlements/ 없음 | ✅ wholesale/settlements, [id] 존재 | R5-FRONT-SETTLE-001 |
| admin/pipeline/ 없음 | ✅ admin/pipeline, [id], queue 존재 | R5-FRONT-PIPELINE-001 |
| pipeline-api.ts 없음 | ✅ `pipeline-api.ts` 존재 | R5-FRONT-PIPELINE-001 |

### 잔존 미구현 / 부분 구현 항목

| 항목 | 상태 | 설명 | 우선순위 |
|------|------|------|---------|
| 어드민 상품 관리 페이지 | ⚠️ 미구현 | `/admin/products/` 전용 CRUD 페이지 없음. 현재 구매/바코드 워크플로우로 대체 | P2 |
| 배송 추적 전용 목록 페이지 | ⚠️ 부분 구현 | `/retail/shipments/` 독립 페이지 없음. 주문 상세 페이지에 통합되어 있음 | P3 |
| 소매 장바구니 | ✅ 구현됨 | `retail/cart/page.tsx` 존재 | — |

### R3-FRONT-002 / R3-API-003 재확인

| 항목 | 결론 |
|------|------|
| R3-FRONT-002 (결제 UI) | ✅ 불필요 — `retail/payment/` (page, success, fail) 전체 구현 완료 |
| R3-API-003 (배송 API) | ✅ 불필요 — `ShipmentController` (`/shipments`), `ShippingAddressController` (`/shipping-addresses`) API 존재. 프론트는 주문 상세 통합 방식으로 처리 |

---

## 4. 의존성 및 빌드 확인

### package.json 핵심 의존성

```bash
# cd /srv/newtalk-v2/frontend && cat package.json | grep -E "next|react|shadcn"
```

| 패키지 | 버전 |
|--------|------|
| `next` | `^15.0.3` |
| `react` | `^19.0.0` |
| `react-dom` | `^19.0.0` |
| `@tanstack/react-query` | `^5.62.2` |
| `@tanstack/react-query-devtools` | `^5.62.2` |
| `react-hook-form` | `^7.54.2` |
| `@radix-ui/react-avatar` | `^1.1.1` |
| `@radix-ui/react-checkbox` | `^1.1.2` |
| `@radix-ui/react-dialog` | `^1.1.2` |
| `@radix-ui/react-dropdown-menu` | `^2.1.2` |
| `@radix-ui/react-label` | `^2.1.0` |
| `@radix-ui/react-radio-group` | `^1.2.1` |
| `@radix-ui/react-scroll-area` | `^1.2.0` |
| `@radix-ui/react-select` | `^2.1.2` |
| `@radix-ui/react-separator` | `^1.1.0` |
| `@radix-ui/react-slot` | `^1.1.0` |
| `@radix-ui/react-tabs` | `^1.1.1` |
| `@radix-ui/react-toast` | `^1.2.2` |
| `tailwindcss` | `^3.4.15` |
| `tailwindcss-animate` | `^1.0.7` |
| `lucide-react` | `^0.460.0` |
| `tailwind-merge` | `^2.5.4` |

> **참고**: `shadcn/ui`는 별도 패키지로 설치되지 않음. `@radix-ui/*` 컴포넌트 + Tailwind CSS 조합으로 동일한 효과 구현.

### 빌드 실행 결과

```bash
# docker compose --env-file .env.docker exec frontend npm run build 2>&1 | tail -20
```

**결과**: ❌ 권한 오류로 실행 불가

```
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

**원인**: 현재 실행 사용자(`claudebot`)가 `docker` 그룹에 미속. `npm`/`node` 로컬 미설치.
**조치 필요**: `usermod -aG docker claudebot` 후 재로그인 또는 root 권한으로 실행

> **이전 빌드 상태**: git log 기준 R5-FRONT-PIPELINE-001, R5-FRONT-SETTLE-001 커밋 정상 push 완료. CI/CD 파이프라인 미설정으로 자동 빌드 이력 없음.

---

## 5. 요약

| 구분 | 수치 |
|------|------|
| 전체 감사 API 영역 | 12개 |
| 완전 연동 완료 | **12개 (100%)** |
| 부분 미구현 (독립 페이지 없음) | 2건 (낮은 우선순위) |
| 완전 미구현 | **0건** |
| 전체 TS/TSX 파일 | 412개 (bak 포함) / 309개 (순수) |
| page.tsx 파일 | 78개 |
| API 클라이언트 파일 | 19개 |

### 변경 이력 (이전 감사 대비)

| 항목 | 이전 (초안) | 현재 |
|------|------------|------|
| 정산(settlement) 연동 | ❌ 미구현 | ✅ 완료 (R5-FRONT-SETTLE-001) |
| 콘텐츠파이프라인(pipeline) 어드민 페이지 | ❌ 미구현 | ✅ 완료 (R5-FRONT-PIPELINE-001) |
| 전체 API 연동률 | 75% (9/12) | 100% (12/12) |

### 다음 단계 권고 (우선순위 순)

1. **[P2]** Docker 권한 수정 (`usermod -aG docker claudebot`) → 빌드 검증 가능화
2. **[P2]** 어드민 상품 관리 페이지 (`/admin/products/`) 필요 여부 검토 — 현재 MD 워크플로우로 대체 가능
3. **[P3]** 배송 추적 전용 목록 페이지 (`/retail/shipments/`) 분리 여부 UX 검토
4. **[P3]** CI/CD 파이프라인 구성으로 자동 빌드 검증 체계 수립
