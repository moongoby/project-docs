# R4-FRONT-001 거래처 제도 UI — 완료 보고서

**작업 ID**: R4-FRONT-001  
**버전**: v3.6.0  
**완료 시각**: 2026-02-26 KST  
**선행**: R4-API-001 (trade API) — 본 서버에는 trade 라우트 미배포 상태, 프론트만 구현 완료

---

## 1. 요약

소매의 거래처 신청, 도매의 거래처 관리(승인/거절/전용가), 관리자 거래처 현황 UI를 구현했습니다.

---

## 2. 구현 목록

### 2.1 타입 (frontend/src/types/trade.ts)
- `ApplicationStatus`: pending | approved | rejected | suspended | terminated
- `PartnershipTier`: basic | silver | gold | vip
- `TradeApplication`, `TradePartnership`, `TradePrice`, `TradeApplyRequest` 인터페이스

### 2.2 API 클라이언트 (frontend/src/lib/trade-api.ts) — 9함수
| 함수 | 메서드/경로 | 비고 |
|------|-------------|------|
| applyTrade | POST trade/apply | 거래처 신청 |
| getApplications | GET trade/applications | 신청 목록 (status, page, per_page) |
| getApplicationDetail | GET trade/applications/{id} | 신청 상세 |
| approveApplication | PUT trade/applications/{id}/approve | 승인 |
| rejectApplication | PUT trade/applications/{id}/reject | 거절 |
| getPartners | GET trade/partners | 거래처 목록 |
| getPartnerDetail | GET trade/partners/{id} | 거래처 상세 |
| setTradePrice | POST trade/partners/{id}/prices | 전용가 설정 |
| getTradePrice | GET trade/price/{productId} | 상품별 전용가 조회 |

### 2.3 컴포넌트 10개 (frontend/src/components/trade/)
| 컴포넌트 | 역할 |
|----------|------|
| TradeApplicationForm | 소매: 거래처 신청 폼 (상호명, 사업자번호, 업종, 소개, 연락처) |
| TradeApplicationList | 신청 목록 (상태 필터, 검색, 페이지네이션) |
| TradeApplicationDetail | 신청 상세 (소매 정보, 승인/거절 버튼) |
| TradeApplicationStatusBadge | 상태 배지 (pending=노랑, approved=초록, rejected=빨강, suspended=회색, terminated=검정) |
| TradePartnerList | 거래처 목록 (등급, 누적거래액, 활성 상태) |
| TradePartnerDetail | 거래처 상세 (등급, 거래 통계, 전용가 목록, 메모) |
| TradePriceTable | 전용가 목록·설정 (상품 ID, 가격 입력, 추가) |
| TradeTierBadge | 등급 배지 (basic=회색, silver=은, gold=금, vip=보라) |
| TradeApplyDialog | 브랜드 페이지용 "거래처 신청" 다이얼로그 |
| index | barrel export |

### 2.4 페이지·라우트 6개
| 경로 | 역할 |
|------|------|
| /retail/trade/apply | 소매: 거래처 신청 (wholesale_user_id 쿼리 또는 브랜드에서 진입) |
| /retail/trade | 소매: 내 거래처 목록 + 신청 현황 (탭) |
| /wholesale/trade | 도매: 받은 신청 + 거래처 목록 (탭) |
| /wholesale/trade/applications/[id] | 도매: 신청 상세 (승인/거절) |
| /wholesale/trade/partners/[id] | 도매: 거래처 상세 (전용가·메모) |
| /admin/trade | 관리자: 전체 거래처 현황 (탭) |

### 2.5 레이아웃 메뉴
- **retail-layout.tsx**: 하단 네비 "거래처" → /retail/trade (Handshake 아이콘)
- **wholesale-layout.tsx**: 사이드 "거래처 관리" → /wholesale/trade (기존 /wholesale/partners에서 변경)
- **admin-layout.tsx**: 사이드 "거래처" → /admin/trade (Handshake 아이콘)

### 2.6 브랜드 페이지 연동
- **brand-header.tsx**: "거래처 신청" 버튼 추가 → TradeApplyDialog(brand.user_id) 연결

---

## 3. 검증

### 3.1 STEP 0 (사전 확인)
- Docker: 5/5 Up (app, nginx, db, redis, frontend)
- trade 라우트: **미등록** (R4-API-001 미배포). 프론트는 동일 경로로 호출 준비 완료.

### 3.2 TypeScript
- 로컬/컨테이너 tsc 실행 환경 이슈로 IDE Lint 기준으로 확인. 수정한 파일들 린트 0건.

### 3.3 문서 갱신
- CHANGELOG.md: [3.6.0] R4-FRONT-001 섹션 추가
- CONTEXT.md: 완료 항목에 R4-FRONT-001 추가
- HANDOVER.md: 버전 2.7.0, 변경이력 2.7.0 행 추가
- NT-V2-ARCHITECTURE.md: Frontend 라우트에 retail/wholesale/admin trade 경로 추가

---

## 4. 파일 목록 (신규·수정)

**신규**
- frontend/src/types/trade.ts
- frontend/src/lib/trade-api.ts
- frontend/src/components/trade/TradeApplicationForm.tsx
- frontend/src/components/trade/TradeApplicationList.tsx
- frontend/src/components/trade/TradeApplicationDetail.tsx
- frontend/src/components/trade/TradeApplicationStatusBadge.tsx
- frontend/src/components/trade/TradePartnerList.tsx
- frontend/src/components/trade/TradePartnerDetail.tsx
- frontend/src/components/trade/TradePriceTable.tsx
- frontend/src/components/trade/TradeTierBadge.tsx
- frontend/src/components/trade/TradeApplyDialog.tsx
- frontend/src/components/trade/index.ts
- frontend/src/app/(retail)/retail/trade/page.tsx
- frontend/src/app/(retail)/retail/trade/apply/page.tsx
- frontend/src/app/(wholesale)/wholesale/trade/page.tsx
- frontend/src/app/(wholesale)/wholesale/trade/applications/[id]/page.tsx
- frontend/src/app/(wholesale)/wholesale/trade/partners/[id]/page.tsx
- frontend/src/app/(admin)/admin/trade/page.tsx

**수정**
- frontend/src/components/layout/retail-layout.tsx (거래처 메뉴)
- frontend/src/components/layout/wholesale-layout.tsx (거래처 관리 링크)
- frontend/src/components/layout/admin-layout.tsx (거래처 메뉴)
- frontend/src/components/brand/brand-header.tsx (거래처 신청 버튼)
- docs/CHANGELOG.md
- docs/CONTEXT.md
- docs/handover/HANDOVER.md
- docs/architecture/NT-V2-ARCHITECTURE.md

---

## 5. 비고

- R4-API-001 배포 후 동일 엔드포인트로 연동하면 됩니다.
- 소매 거래처 신청 시 `/retail/trade/apply?wholesale_user_id={id}` 또는 브랜드 페이지 "거래처 신청"으로 진입합니다.
