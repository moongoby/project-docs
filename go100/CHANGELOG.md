# GO100 변경 이력
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.0

## 2026-02-23
### [acca08c0] docs: 문서 체계 구축
- CONTEXT.md + architecture/handover/plan 디렉토리 정리

### [08a3b2ba] fix: CUR-GO100-HOTFIX-IMPORT
- strategy_router.py import 누락 수정 (get_effective_uid, text)
- 카드15 is_active 복구

### [8da6191b] fix: CUR-GO100-HOTFIX-CRITICAL
- 전략저장 fallback, 에러로깅, 상세모달, 토글API, 채팅 z-index

### [556ddb17] BT-ENGINE-UPGRADE
- add entry/exit datetime, MFE/MAE, regime, indicators, strategy_name, commission to backtest trades

### [d34fb1d5] feat: CUR-GO100-UNIFIED-SAVE-BE
- 전략저장 go100 통일, 백테스트 연동, AI 자동전략명, user_utils

### [66b0038f] feat: CUR-GO100-UNIFIED-SAVE-FE
- 채팅링크 /llm, 리다이렉트, 저장GO100, 상세/토글/검색

## 2026-02-22
### [67b83d3b] fix: CUR-GO100-MY-STRATEGY-FIX
- 내전략 user_id 매핑, 채팅위치, 핀치줌, 세션연장

### [1a9c4219] feat: CUR-GO100-CARD-DETAIL-FIX
- 상세창 수정, 활성토글, 검색

### [5351de40] fix: CUR-GO100-MY-STRATEGY-FIX
- 내전략 user_id 매핑, Go100StrategyCardUpdate is_active

### [51018376] fix: CUR-GO100-CHAT-POSITION-FIX
- 채팅 위젯 우하단 위치 수정

### [af0dbf5f] feat: CUR-GO100-CARD-REDESIGN-FE
- GO100 메뉴 삭제, 탭 tab=all/my

### [09f94b56] feat: CUR-GO100-CARD-REDESIGN-BE
- featured 플래그, catalog tab 파라미터

### [5a891210] feat: CUR-GO100-CHAT-WIDGET
- 백억이 플로팅 위젯

### [7b75221e] DASH-RESTORE
- revert /dashboard mount to legacy UI, disable new frontend

### [e6ea2b2e] feat: CUR-GO100-FIX-BACKEND
- DB 정리, Catalog GO100 병합 확정

### [1165d00d] feat: CUR-GO100-FIX-FRONTEND
- 전략카드 GO100 표시 및 뱃지

### [4f8fef24] feat: CUR-GO100-STRATEGY-CARD-FIX
- GO100 전략카드 화면 노출 수정

### [07c03316] feat: CUR-GO100-STRATEGY-INTEGRATE
- V4.1 전략카드 페이지에 GO100 카드 통합 표시

## 이전
- DESK-RECOMMEND, DASH-FIX, DESK1-DATA, CUR-GO100-BUNDLE4D/4C/4B, STRAT-TUNE, CUR-BT-TRADE-DETAIL, docs/CLAUDE.md 등 (git log 참조)
