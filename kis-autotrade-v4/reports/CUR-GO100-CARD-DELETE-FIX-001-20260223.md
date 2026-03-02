# CUR-GO100-CARD-DELETE-FIX-001 — GO100 전략카드 삭제 실패 수정 보고서

- **일시**: 2026-02-23 19:00 KST
- **서버**: root@[SERVER-IP]
- **DB**: psql -h localhost -U kis_admin -d kisautotrade
- **코드 repo**: /root/kis-autotrade-v4
- **문서 repo**: /root/project-docs (master)
- **절대규칙 준수**: kis-v41-* 재시작 금지, strategy_cards DDL 금지, v4_positions 수정 금지, .env/.bak 커밋 금지

---

## 1. 요약

| 항목 | 결과 |
|------|------|
| **목적** | "내 전략" 탭에서 GO100 전략카드 삭제 시 에러 발생 수정 |
| **원인** | 전략카드 목록 페이지에서 삭제 시 항상 V4.1 API(`/api/v1/strategy-cards/:id`) 호출 → GO100 카드는 `go100_strategy_cards`에만 있어 404/실패 |
| **수정** | CASE C 적용: `source === "go100"`인 카드 삭제 시 GO100 API `DELETE /api/go100/strategy-cards/:id` 호출 |
| **검증** | 프론트 빌드 성공, go100_strategy_cards 6행 유지 (soft delete이므로 행 수 유지) |

---

## 2. 진단 결과

### 2.1 외래키 구조

- `go100_strategy_cards`를 참조하는 자식 테이블 (pg_constraint 기준):
  - `go100_fit_analysis` (go100_card_id)
  - `go100_risk_disclaimers` (strategy_card_id)
  - `go100_portfolios` (go100_card_id)
  - `go100_backtest_runs` (go100_card_id)
- 삭제 방식: 백엔드 `delete_card()`는 **soft delete** (UPDATE is_active=false, card_status='RETIRED')만 수행하므로 FK로 인한 삭제 실패는 아님.

### 2.2 자식 데이터 현황

| 테이블 | 행 수 |
|--------|-------|
| go100_fit_analysis | 40 |
| go100_backtest_runs | 0 |
| go100_orders | 0 |
| go100_positions | 0 |
| go100_trades | 0 |
| go100_portfolios | 0 |
| go100_desk_allocation | 2 |
| go100_risk_disclaimers | 0 |

### 2.3 API 존재 여부

- **백엔드**: `DELETE /api/go100/strategy-cards/{card_id}` 구현됨 (`strategy_router.py`, `card_service.delete_card()`).
- **프론트**: `deleteStrategyCard(cardId)` (go100Api.ts)는 GO100 상세 페이지에서만 사용됨.
- **문제**: 전략카드 **목록** 페이지(`/strategy-cards`)는 카탈로그 API로 GO100 카드를 `source=go100`, `card_id=go100_card_id`로 받으나, 삭제 시 `useDeleteCard()` → V4.1 `deleteCard(id)` 호출 → **잘못된 엔드포인트**로 요청.

---

## 3. 수정 내용 (CASE C)

### 3.1 변경 파일

| 파일 | 변경 |
|------|------|
| `frontend/src/app/(protected)/strategy-cards/page.tsx` | 1) `deleteStrategyCard` import 추가. 2) `handleDeleteConfirm`에서 `deleteTarget.source === "go100"`이면 `deleteStrategyCard(deleteTarget.card_id)` 호출 후 `CATALOG_KEY` 무효화; 그 외는 기존 V4.1 `deleteMutation.mutate(deleteTarget.card_id)` 유지. |

### 3.2 코드 요지

- GO100 카드: `await deleteStrategyCard(deleteTarget.card_id)` → `DELETE /api/go100/strategy-cards/:id` (go100Client).
- V4.1 카드: `deleteMutation.mutate(deleteTarget.card_id)` → `DELETE /api/v1/strategy-cards/:id` (apiClient).

---

## 4. 테스트 결과

- **빌드**: `npm run build` (frontend) 성공.
- **서비스**: go100, go100-frontend만 재시작 (kis-v41-* 미재시작).
- **삭제 동작**: "내 전략" 탭에서 GO100 카드 삭제 시 GO100 API 호출로 정상 처리 예상 (실제 삭제는 soft delete로 카드 비활성화).
- **go100_strategy_cards**: 6행 (삭제 시 행은 유지, is_active=false·card_status='RETIRED'로 변경).

---

## 5. 참고

- GO100 상세 페이지(`StrategyCardDetail.tsx`)는 이미 `deleteStrategyCard(card.go100_card_id)` 사용으로 정상.
- 백엔드 삭제 로직 변경 없음 (기존 soft delete 유지).
