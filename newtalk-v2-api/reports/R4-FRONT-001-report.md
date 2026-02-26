# R4-FRONT-001 거래처 제도 UI — 완료 보고서

**작성일시**: 2026-02-26 KST  
**버전**: v3.6.0  
**선행**: R4-API-001 (v3.1.0) 완료 필수

---

## 1. 개요

소매의 거래처 신청, 도매의 거래처 관리(승인/거절/전용가), 관리자 거래처 현황 UI를 구현했습니다.

---

## 2. 구현 파일 목록

### 타입
- `frontend/src/types/trade.ts` — ApplicationStatus, PartnershipTier, TradeApplication, TradePartnership, TradePrice, TradeApplyRequest

### API 클라이언트
- `frontend/src/lib/trade-api.ts` — 11함수 (applyTrade, getApplications, getApplicationDetail, approveApplication, rejectApplication, getPartners, getPartnerDetail, setTradePrice, getTradePrice, bulkSetTradePrices, removeTradePrice)

### 컴포넌트 (10개)
- `frontend/src/components/trade/TradeApplicationForm.tsx` — 소매: 거래처 신청 폼
- `frontend/src/components/trade/TradeApplicationList.tsx` — 신청 목록 (상태 필터, 검색)
- `frontend/src/components/trade/TradeApplicationDetail.tsx` — 신청 상세 (승인/거절 버튼)
- `frontend/src/components/trade/TradeApplicationStatusBadge.tsx` — 상태 배지 (pending/approved/rejected/suspended/terminated)
- `frontend/src/components/trade/TradePartnerList.tsx` — 거래처 목록 (등급, 누적거래액, 활성 상태)
- `frontend/src/components/trade/TradePartnerDetail.tsx` — 거래처 상세 (전용가 목록, 메모)
- `frontend/src/components/trade/TradePriceTable.tsx` — 전용가 목록·설정 (단일 추가, 일괄 설정, 삭제)
- `frontend/src/components/trade/TradeTierBadge.tsx` — 등급 배지 (basic/silver/gold/vip)
- `frontend/src/components/trade/TradeApplyDialog.tsx` — 브랜드 페이지용 거래처 신청 다이얼로그
- `frontend/src/components/trade/index.ts` — barrel

### 페이지·라우트
- `frontend/src/app/(retail)/retail/trade/page.tsx` — /retail/trade (내 거래처·신청 현황)
- `frontend/src/app/(retail)/retail/trade/apply/page.tsx` — /retail/trade/apply (거래처 신청, 쿼리 wholesale_user_id)
- `frontend/src/app/(retail)/retail/trade/applications/[id]/page.tsx` — /retail/trade/applications/[id]
- `frontend/src/app/(retail)/retail/trade/partners/[id]/page.tsx` — /retail/trade/partners/[id]
- `frontend/src/app/(wholesale)/wholesale/trade/page.tsx` — /wholesale/trade
- `frontend/src/app/(wholesale)/wholesale/trade/applications/[id]/page.tsx` — /wholesale/trade/applications/[id]
- `frontend/src/app/(wholesale)/wholesale/trade/partners/[id]/page.tsx` — /wholesale/trade/partners/[id]
- `frontend/src/app/(admin)/admin/trade/page.tsx` — /admin/trade
- `frontend/src/app/(admin)/admin/trade/applications/[id]/page.tsx` — /admin/trade/applications/[id]
- `frontend/src/app/(admin)/admin/trade/partners/[id]/page.tsx` — /admin/trade/partners/[id]

### 레이아웃·브랜드
- `frontend/src/components/layout/retail-layout.tsx` — "거래처" 메뉴 → /retail/trade
- `frontend/src/components/layout/wholesale-layout.tsx` — "거래처 관리" → /wholesale/trade
- `frontend/src/components/layout/admin-layout.tsx` — "거래처" → /admin/trade (Handshake 아이콘)
- `frontend/src/app/(retail)/brand/[slug]/page.tsx` — "거래처 신청" 버튼 + TradeApplyDialog 연동

### 문서
- `docs/CHANGELOG.md` — [3.6.0] R4-FRONT-001 섹션
- `docs/CONTEXT.md` — 완료 항목 추가
- `docs/handover/HANDOVER.md` — 변경이력 + 완료작업
- `docs/NT-V2-ARCHITECTURE.md` — Frontend 라우트·API trade 반영
- `docs/reports/R4-FRONT-001-report.md` — 본 보고서

---

## 3. 검증

### TypeScript
- 로컬에서 `npx tsc --noEmit` 미실행(환경 제한). 린트 에러 없음 확인.
- 서버 배포 후: `docker compose --env-file .env.docker exec frontend npx tsc --noEmit` → 0 errors 목표.

### 페이지 HTTP 확인 (서버에서 실행)
```bash
curl -s -o /dev/null -w "retail trade: %{http_code}\n" http://localhost:3000/retail/trade
curl -s -o /dev/null -w "wholesale trade: %{http_code}\n" http://localhost:3000/wholesale/trade
curl -s -o /dev/null -w "admin trade: %{http_code}\n" http://localhost:3000/admin/trade
```
- 200 응답 확인 목표.

---

## 4. 요약

| 항목 | 내용 |
|------|------|
| 컴포넌트 | 10개 |
| API 함수 | 11개 (지시서 9개 + bulkSetTradePrices, removeTradePrice) |
| 페이지 | retail 4, wholesale 3, admin 3 (상세 포함) |
| 타입 | types/trade.ts |
| 브랜드 페이지 | "거래처 신청" 버튼 → TradeApplyDialog (wholesale_user_id 연동) |
| 문서 | CHANGELOG, CONTEXT, HANDOVER, ARCHITECTURE 갱신 |

---

## 5. Git / 배포

- 커밋 접두사: `[R4-FRONT-001]`
- Push Step A (V2 메인 레포), Step B (project-docs 동기화), Step C (검증)는 서버(`/srv/newtalk-v2`)에서 지시서대로 실행 필요.
- **⚠️ PUSH 실행하지 않으면 작업 미완료 처리.**

---

**보고서 끝**
