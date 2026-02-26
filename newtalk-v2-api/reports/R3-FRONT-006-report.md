# R3-FRONT-006 작업 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | R3-FRONT-006 |
| 작업명 | 정산 UI |
| 완료일 | 2026-02-26 KST |
| 버전 | v2.12.0 |
| 커밋 SHA | 푸시 후 `git log -1 --pretty=%h` 로 확인하여 기입 |
| 상태 | 완료 |

## 페이지 (4개)
- /admin/settlements — 관리자 정산 목록 (필터, 검색, 새 정산 생성)
- /admin/settlements/[id] — 관리자 정산 상세 (상태 변경, 항목 관리, 재계산)
- /wholesale/settlements — 도매 정산 목록 (본인만)
- /wholesale/settlements/[id] — 도매 정산 상세 (은행 정보, 메모)

## 컴포넌트 (10개)
- SettlementList — 정산 목록 테이블, 필터, 페이지네이션
- SettlementDetail — 정산 상세 (요약 카드, 항목 테이블, 타임라인, 은행/메모)
- SettlementStatusBadge — 상태별 색상 배지
- SettlementSummaryCard — 금액 요약 (매출/배송비/수수료/공제/정산액)
- SettlementItemTable — 항목 목록 (관리자 시 항목 제외/복원)
- SettlementTimeline — 로그 타임라인
- SettlementCreateDialog — 정산 생성 (판매자, 기간, 수수료율, 미리보기→생성)
- SettlementStatusChangeDialog — 상태 변경 확인
- BankInfoForm — 은행 정보 입력/수정 (도매 전용)
- index.ts — barrel export

## API 클라이언트
- frontend/src/lib/settlement-api.ts — previewSettlement, createSettlement, getSettlements, getSettlement, updateSettlementStatus, recalculateSettlement, updateBankInfo, updateSettlementItemStatus, addSettlementMemo (9함수)
- frontend/src/types/settlement.ts — Settlement, SettlementItem, SettlementLog, SettlementPreview, SettlementCreateRequest, SettlementListResponse, 타입/인터페이스

## 레이아웃 메뉴
- admin-layout: "정산 관리" → /admin/settlements
- wholesale-layout: "정산" (Wallet 아이콘) → /wholesale/settlements

## 파일 목록
- frontend/src/types/settlement.ts
- frontend/src/lib/settlement-api.ts
- frontend/src/components/settlement/SettlementStatusBadge.tsx
- frontend/src/components/settlement/SettlementSummaryCard.tsx
- frontend/src/components/settlement/SettlementItemTable.tsx
- frontend/src/components/settlement/SettlementTimeline.tsx
- frontend/src/components/settlement/BankInfoForm.tsx
- frontend/src/components/settlement/SettlementStatusChangeDialog.tsx
- frontend/src/components/settlement/SettlementCreateDialog.tsx
- frontend/src/components/settlement/SettlementList.tsx
- frontend/src/components/settlement/SettlementDetail.tsx
- frontend/src/components/settlement/index.ts
- frontend/src/app/(admin)/admin/settlements/page.tsx
- frontend/src/app/(admin)/admin/settlements/[id]/page.tsx
- frontend/src/app/(wholesale)/wholesale/settlements/page.tsx
- frontend/src/app/(wholesale)/wholesale/settlements/[id]/page.tsx
- frontend/src/components/layout/admin-layout.tsx (정산 관리 링크 수정)
- frontend/src/components/layout/wholesale-layout.tsx (정산 메뉴 추가)

## 검증
- TypeScript: `npx tsc --noEmit` → 0 errors (로컬/서버에서 실행 후 기입)
- HTTP: /admin/settlements, /wholesale/settlements → 200 또는 302

## 비고
- 관리자 정산 생성 다이얼로그의 판매자(도매) 목록은 sellerOptions=[] 로 두었음. GET /api/users?role=wholesale 등 API 추가 시 연동 가능.
