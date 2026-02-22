# GO100 알려진 이슈
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.0

## 미해결
### ISS-001: 채팅 위젯 브라우저 미표시
- **심각도**: 중간
- 코드/import/layout 정상, 브라우저에서 안 보임
- 원인: 런타임 JS에러 또는 CSS, 브라우저 콘솔 확인 필요

### ISS-002: 백테스트 드롭다운 GO100 표시 미검증
- **심각도**: 중간
- API는 GO100 포함 반환, 프론트 실제 확인 필요

### ISS-003: 백억이 전략 저장 E2E 미검증
- **심각도**: 높음
- import 수정 완료, 실제 로그인 후 저장 성공 미확인

## 해결됨
### ISS-004: strategy_router.py import 누락
- 해결: 08a3b2ba (get_effective_uid, text)

### ISS-005: 카드15 is_active=false
- 해결: 08a3b2ba

### ISS-006: 전체전략=내전략 동일
- 해결: 09f94b56 (featured 플래그, catalog tab)
