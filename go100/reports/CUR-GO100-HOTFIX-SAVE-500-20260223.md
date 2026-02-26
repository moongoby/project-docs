# CUR-GO100-HOTFIX-SAVE-500 보고서
작성일: 2026-02-23
커밋: 8529b500

## 근본 원인
go100_strategy_cards.strategy_type CHECK 제약조건에 'GO100_AI' 미포함 → INSERT 시 500

## 수정 내용
1. DB: ALTER TABLE - CHECK에 'GO100_AI' 추가
2. FE: layout.tsx - /llm 페이지에서 ChatWidget 중복 렌더 제거 (usePathname)

## 검수 결과
- DB CHECK: GO100_AI 포함 확인
- API: 401 (이전 500 해소)
- layout.tsx: isLlmPage 조건 3곳 적용 확인
- 에러 로그: strategy_type/constraint 에러 없음
