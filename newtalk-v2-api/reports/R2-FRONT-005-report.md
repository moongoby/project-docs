# R2-FRONT-005 보고서: 관리자 구매 대시보드 상세 페이지

**문서번호**: R2-FRONT-005  
**작업명**: 관리자 구매 대시보드 상세 페이지  
**작성일**: 2026-02-24  
**버전**: v1.7.0  
**커밋 SHA**: 46fccf5

---

## §1. 구현 요약

| 항목 | 내용 |
|------|------|
| 페이지 경로 | `/admin/purchase` (대시보드), `/admin/purchase/orders`, `/admin/purchase/orders/[id]` → `/admin/purchase/[id]`, `/admin/purchase/receiving`, `/admin/purchase/receiving/[id]`, `/admin/purchase/barcode` |
| API 연동 | dashboard/purchasing/summary, recent-orders, purchase-orders(목록/상세/상태), inbound-receipts(목록/상세/complete), barcodes(목록/검색) |
| UI 컴포넌트 | PurchaseStats, PurchaseFilter, PurchaseOrderTable, ReceivingTable, ReceivingDetail, BarcodeScanner, 기존 OrderDetailHeader, OrderItemsTable, InboundStatus, StatusBadge, OrderMemo, OrderStatusChange |
| 타입 | `types/purchase-order.ts`, `types/purchase.ts` |
| 네비게이션 | 관리자 사이드바: 구매 대시보드, 발주관리, 입고관리, 바코드 |

---

## §2. 생성·수정된 파일 목록 (이번 확장)

### 프론트엔드 (frontend/src/)

| 구분 | 경로 |
|------|------|
| 신규 | types/purchase.ts |
| 신규 | lib/purchase-api.ts |
| 신규 | components/purchase/PurchaseStats.tsx |
| 신규 | components/purchase/PurchaseFilter.tsx |
| 신규 | components/purchase/PurchaseOrderTable.tsx |
| 신규 | components/purchase/ReceivingTable.tsx |
| 신규 | components/purchase/ReceivingDetail.tsx |
| 신규 | components/purchase/BarcodeScanner.tsx |
| 신규 | components/purchase/index.ts |
| 신규 | app/(admin)/admin/purchase/page.tsx |
| 신규 | app/(admin)/admin/purchase/orders/page.tsx |
| 신규 | app/(admin)/admin/purchase/receiving/page.tsx |
| 신규 | app/(admin)/admin/purchase/receiving/[id]/page.tsx |
| 신규 | app/(admin)/admin/purchase/barcode/page.tsx |
| 수정 | components/layout/admin-layout.tsx (구매 메뉴 4개 추가) |
| 수정 | components/admin/purchase-detail/OrderDetailHeader.tsx (backHref 기본값 → /admin/purchase/orders) |
| 수정 | app/(admin)/admin/purchase/[id]/page.tsx (목록 링크 → /admin/purchase/orders) |

### 기존 (이전 R2-FRONT-005)
- types/purchase-order.ts, lib/purchase-order-api.ts
- components/admin/purchase-detail/*, app/(admin)/admin/purchase/[id]/page.tsx

---

## §3. 구현 상세

### 3.1 구매 대시보드 메인 (/admin/purchase)
- PurchaseStats: 총 발주 건수, 입고 완료, 승인/입고 대기, 이번 달 발주 금액 (GET dashboard/purchasing/summary)
- 최근 발주 5건 테이블 (GET dashboard/purchasing/recent-orders)
- 빠른 링크: 발주 목록, 입고 관리, 바코드

### 3.2 발주 목록 (/admin/purchase/orders)
- PurchaseFilter: 상태, 날짜 범위, 검색(발주번호) → 적용/초기화
- PurchaseOrderTable: 발주번호, 도매처, 상태(StatusBadge), 금액, 발주일, 상세 링크 → /admin/purchase/[id]
- 페이지네이션 (GET purchase-orders?status&date_from&date_to&search&page)

### 3.3 발주 상세 (/admin/purchase/[id]) — 기존
- OrderDetailHeader, OrderItemsTable, InboundStatus, OrderStatusChange, OrderMemo
- 목록 링크 → /admin/purchase/orders

### 3.4 입고 목록 (/admin/purchase/receiving)
- PurchaseFilter (상태, 날짜), ReceivingTable: 입고번호, 발주번호, 도매처, 상태, 수량, 입고일, 상세 링크
- GET inbound-receipts (페이지네이션)

### 3.5 입고 상세 (/admin/purchase/receiving/[id])
- ReceivingDetail: 입고 기본정보, 입고 상품 테이블(수량/불량), 검수 완료 버튼
- POST inbound-receipts/{id}/complete

### 3.6 바코드 (/admin/purchase/barcode)
- BarcodeScanner: 바코드 입력/조회 (GET barcodes?search=)
- 바코드 목록 테이블 (검색 가능)

### 3.7 API (lib/purchase-api.ts)
- getPurchaseDashboardSummary, getPurchaseOrdersList, getRecentPurchaseOrders
- getInboundReceipts, getInboundReceipt, completeInboundReceipt
- getBarcodesList, scanBarcode

---

## §4. Docker 빌드 및 확인

```bash
cd /srv/newtalk-v2
docker compose --env-file .env.docker up -d --build frontend
```

- 관리자 로그인 후 `/admin/purchase`, `/admin/purchase/orders`, `/admin/purchase/receiving`, `/admin/purchase/barcode` 접속 및 동작 확인.

---

## §5. Git 및 project-docs 동기화

```bash
cd /srv/newtalk-v2
git add -A
git status
git commit -m "[R2-FRONT-005] 관리자 구매 대시보드 상세 페이지 (대시보드·발주·입고·바코드)"
git push origin main
git log --oneline -1  # SHA 기록

# project-docs
cp docs/reports/R2-FRONT-005-report.md /data/project-docs/newtalk-v2-api/reports/
cp docs/CONTEXT.md /data/project-docs/newtalk-v2-api/
cp docs/CHANGELOG.md /data/project-docs/newtalk-v2-api/
cd /data/project-docs && git add -A && git commit -m "docs: R2-FRONT-005 보고서 갱신 (20260224)" && git push origin master
```

---

## §6. 비고

- 백엔드 입고 API 경로: `inbound-receipts` (receivings 아님)
- 바코드 목록: GET barcodes는 paginator 직접 반환 가능 → purchase-api에서 래퍼 처리
- V1 헬스체크: `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` → 200 확인
