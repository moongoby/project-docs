# GO100 변경 이력
> 최종 업데이트: 2026-02-24 | 문서 버전: v1.1

## 2026-02-24
### [CUR-GO100-DETAIL-PAGE] feat: 전략 상세 페이지 모바일 최적화 구현 (5bf98a68)
- FE: /go100/strategies/[id] 리다이렉트 → 전용 상세 페이지로 전면 재작성
- 모바일 퍼스트: 히어로 카드, 핵심 지표 2x2, 3탭(요약/매매규칙/위험관리)
- 기능: 백테스트 실행/polling, 활성 토글, 삭제, 상태별 액션 버튼
- FE: portfolio/page.tsx React Hook 순서 버그 수정
- FE: stock/[code]/page.tsx params null 체크 수정
- 보고서: report/GO100-DETAIL-PAGE-DEV-REPORT-20260224.md
- 프로세스 개선안: report/GO100-STRATEGY-PROCESS-IMPROVEMENT-REPORT-20260224.md

## 2026-02-23
### [CUR-GO100-HOTFIX-002] fix: ChatWidget FAB 미노출 + 전략카드 저장 500 (6c69a23a)
- FE: ChatWidget FAB를 createPortal로 document.body에 렌더링(ISS-008/009)
- BE: get_effective_uid 예외 시 JWT fallback, card_service _safe_json으로 직렬화 방어(ISS-010)
- 보고서: docs/reports/20260223-HOTFIX-002.md

### [CUR-GO100-FINAL-FIX-001] fix: 전략저장 500 해결 + ChatWidget 조건부 렌더링
- DB: strategy_type CHECK에 GO100_AI 추가 (ALTER TABLE, 진단 시 이미 반영 확인)
- FE: layout.tsx usePathname으로 /llm 페이지 ChatWidget 제외 유지, FINAL-FIX-001 주석
- 검증: 비인증 401, 백엔드/프론트 200 확인

### [CUR-GO100-PHASE2-STABILIZE] fix: ISS-001/002/003 + .cursorrules 보완
- ISS-001: ChatWidget 로딩 중 노출, fixed/z-[9999] 확인
- ISS-002: for-backtest GO100 정렬(featured_order), universe_filter 안내 문구
- ISS-003: 전략 저장 get_effective_uid fallback, INSERT 전 로깅, logger.exception, FE strategy_type/에러 로깅
- .cursorrules: 빌드 검증 규칙, 커밋 후 sync, 보고서 규칙, 필수 참조 문서

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
