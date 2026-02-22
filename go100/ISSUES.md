# GO100 알려진 이슈
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.0

## 미해결
(없음)

## 해결됨
### ISS-001: 채팅 위젯 브라우저 미표시
- 해결: CUR-GO100-PHASE2-STABILIZE (2026-02-23) — 로딩 중·미인증 시에도 ChatWidget 노출, fixed/z-index 확인

### ISS-002: 백테스트 드롭다운 GO100 표시 미검증
- 해결: CUR-GO100-PHASE2-STABILIZE (2026-02-23) — for-backtest 정렬(featured_order), 안내 문구 보강

### ISS-003: 백억이 전략 저장 E2E 미검증
- 해결: CUR-GO100-PHASE2-STABILIZE (2026-02-23) — get_effective_uid fallback, 필수 필드/에러 로깅, strategy_type

## 이전 해결
### ISS-004: strategy_router.py import 누락
- 해결: 08a3b2ba (get_effective_uid, text)

### ISS-005: 카드15 is_active=false
- 해결: 08a3b2ba

### ISS-006: 전체전략=내전략 동일
- 해결: 09f94b56 (featured 플래그, catalog tab)
