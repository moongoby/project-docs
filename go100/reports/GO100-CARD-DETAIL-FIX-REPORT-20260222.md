# CUR-GO100-CARD-DETAIL-FIX 보고서
작업일: 2026-02-22

## 상세창 오류
- **원인**: GET /api/go100/strategy-cards/:id 상세 API가 `user_id = current_user` 조건만 사용해, "전체 전략" 탭에서 노출되는 **다른 사용자 소유의 featured 카드**를 조회할 때 404 발생.
- **수정**: `go100_strategy_cards` 조회 조건을 `(user_id = :user_id OR is_featured = true) AND is_active = true` 로 변경. 본인 카드 또는 featured 카드 모두 상세 조회 가능하도록 함.

## 활성/비활성 토글
- **API**: 기존 PUT /api/go100/strategy-cards/:id 사용. `Go100StrategyCardUpdate` 스키마에 `is_active: Optional[bool]` 추가, `update_card` 서비스에서 `is_active` 변경 처리. 타인 카드 토글 시 `OwnershipException` (400) 반환.
- **프론트**: 카드 헤더 우측에 스위치 토글 추가. 활성=녹색, 비활성=회색. GO100 카드에만 표시, 클릭 시 `updateStrategyCard(cardId, { is_active })` 호출 후 카탈로그 무효화로 목록 갱신.

## 검색 기능
- **방식**: 클라이언트 사이드 필터링.
- **검색 대상**: `name`, `strategy_params.ticker_name`, `type` (전략명/종목명/타입).
- **UI**: 필터 바 왼쪽에 "전략 검색..." placeholder 입력창. 검색 결과 0건 시 "검색 결과가 없습니다." 표시.

## 수정 파일
- backend/app/routers/go100/strategy_router.py (헤더 주석)
- backend/app/services/go100/strategy/card_service.py (get_card 조건, update_card is_active)
- backend/app/services/go100/strategy/schemas.py (Go100StrategyCardUpdate.is_active)
- frontend/src/app/(protected)/strategy-cards/page.tsx (검색 상태/필터, GO100 토글 mutation)
- frontend/src/app/(protected)/go100/strategies/[id]/page.tsx (헤더 주석)
- frontend/src/components/strategy/StrategyCard.tsx (GO100 토글 스위치, onToggleGo100Active)
- frontend/src/lib/hooks/useStrategyCards.ts (CATALOG_KEY export)

## 빌드/테스트
- tsc: 성공
- build: 성공 (Next.js 14.2.35)
- pytest: 184 passed, 8 failed (LLM e2e/Universe 기존 이슈, 본 작업과 무관)

## 컴플라이언스
- [x] go100_strategy_cards 3건 유지
- [x] v4_positions OPEN 5건 유지
- [x] V4.1 핵심 파일 수정 최소화 (go100_* 위주)
- [x] .env/.bak 커밋 없음
- [x] 파일 헤더 주석 포함 (CUR-GO100-CARD-DETAIL-FIX, 2026-02-22)

## 커밋
- 메시지: feat: CUR-GO100-CARD-DETAIL-FIX - 상세창 수정 + 활성토글 + 검색
- 해시: 1a9c4219
