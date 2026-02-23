# GO100 알려진 이슈
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.2

## 미해결
(없음)

## 해결됨
### ISS-010: 전략카드 저장 500 재발 (브라우저 E2E)
- 원인: get_effective_uid 예외 전파 또는 JSON 직렬화 실패
- 해결: CUR-GO100-HOTFIX-002 (2026-02-23, 6c69a23a) — user_utils try/except, card_service _safe_json
- 검증: 백억이 화면 "전략카드로 저장" 재시도 후 201 확인

### ISS-009: ChatWidget FAB 대시보드 미노출
- 원인: 부모 overflow/stacking context로 FAB 가림
- 해결: CUR-GO100-HOTFIX-002 (2026-02-23, 6c69a23a) — FAB를 createPortal로 document.body 렌더링
- 검증: Ctrl+Shift+R 후 /dashboard 등에서 FAB(data-testid=chat-widget-fab) 노출 확인

### ISS-008: ChatWidget 전체 페이지 미노출
- 원인: layout.tsx 조건부 렌더링 오류 또는 빌드 미반영
- 해결: CUR-GO100-FINAL-FIX-001 + CUR-GO100-HOTFIX-002 — usePathname 분기 + FAB Portal
- 검증: /go100, /strategy-cards 등에서 FAB 노출 확인

### ISS-007: 전략 저장 500 에러 (strategy_type CHECK)
- 원인: DB CHECK 제약조건에 'GO100_AI' 미포함
- 해결: CUR-GO100-FINAL-FIX-001 (2026-02-23) — CHECK에 GO100_AI 추가 (8529b500 선행 반영)
- 검증: 인증 후 POST /api/go100/strategy-cards strategy_type=GO100_AI 성공

### ISS-001: 채팅 위젯 브라우저 미표시
- 해결: CUR-GO100-PHASE2-STABILIZE (2026-02-23) → ISS-008로 재추적

### ISS-002: 백테스트 드롭다운 GO100 표시 미검증
- 해결: CUR-GO100-PHASE2-STABILIZE (2026-02-23) — for-backtest 정렬, 안내 문구

### ISS-003: 백억이 전략 저장 E2E 미검증
- 해결: CUR-GO100-PHASE2-STABILIZE (2026-02-23) → ISS-007로 재추적

### ISS-004: strategy_router.py import 누락
- 해결: 08a3b2ba

### ISS-005: 카드15 is_active=false
- 해결: 08a3b2ba

### ISS-006: 전체전략=내전략 동일
- 해결: 09f94b56
