# GO100 프로젝트 규칙
# globs: backend/app/routers/go100/**, backend/app/services/go100/**, frontend/src/go100/**, frontend/src/app/(protected)/go100/**, docs/**, .cursorrules

## 필수 참조 문서 (작업 전 반드시 읽기)
- docs/CONTEXT.md (프로젝트 전체 맥락)
- docs/ISSUES.md (미해결 이슈)
- docs/CHANGELOG.md (최근 변경)
- docs/ROADMAP.md (진행 상태)
- docs/DB_SCHEMA.md (테이블 구조)
- docs/API_SPEC.md (API 명세)
- docs/PLANNING.md (기획서)
- docs/ARCHITECTURE.md (아키텍처)
- docs/HANDOVER.md (인수인계)

## GO100 절대 규칙
1. go100_* 파일/테이블만 수정
2. 모든 수정 파일에 헤더 주석: // CUR-GO100-<TASK-ID>, <DATE>
3. DB 스키마 변경은 go100_* 테이블 한정
4. 작업 흐름: 백업→확인→수정→빌드→재시작→검증→커밋→보고서→문서갱신→sync

## GO100 핵심 파일
### 백엔드
- backend/app/routers/go100/strategy_router.py (전략카드 API)
- backend/app/services/go100/strategy/card_service.py (전략카드 CRUD)
- backend/app/services/go100/ai/base_orchestrator.py (AI 대화→전략 생성)
- backend/app/services/go100/user_utils.py (user_id 매핑)

### 프론트엔드
- frontend/src/go100/components/ChatWidget.tsx (백억이 위젯)
- frontend/src/go100/api/go100Api.ts (GO100 API 클라이언트)
- frontend/src/components/chat/StrategyCardSaveButton.tsx (전략 저장 버튼)

## GO100 DB 테이블
- go100_strategy_cards (3행): 전략카드 (PK: go100_card_id)
- go100_backtest_runs: 백테스트 결과
- go100_desk_allocation (2행): 데스크 배분
- go100_fit_analysis (40행): 적합도 분석
- go100_orders, go100_portfolios, go100_positions, go100_trades: 매매 관련

## GO100 API
- POST/GET/PUT/DELETE /api/go100/strategy-cards
- PATCH /api/go100/strategy-cards/{id}/toggle
- POST /api/go100/ai/chat
- POST /api/go100/backtest/run
- GET /api/v1/strategy-cards/catalog?tab=all|my
- GET /api/v1/strategy-cards/for-backtest

## user_id 매핑 (★ 핵심)
- moongoby@naver.com: v4_users.user_id=3, legacy users.id=15
- moongoby@gmail.com: v4_users.user_id=2, legacy users.id=6
- JWT에는 legacy id가 들어있으므로 반드시 get_effective_uid() 사용

## 문서 동기화
- 커밋 후 반드시: bash /root/project-docs/scripts/sync_go100.sh
- 보고서: report/<YYYYMMDD>-<TASK-ID>.md 생성 후 sync

## 문서 저장 규칙 (2026-02-24 추가)
- 보고서 파일명: `CUR-GO100-{TASK}-{SEQ}-{YYYYMMDD}.md`
- 저장 위치: `go100/reports/` (교차 저장 금지)
- 상세: go100/rules/DOCUMENT-RULES.md
- 마스터: https://raw.githubusercontent.com/moongoby/project-docs/master/DOCUMENT-NAMING-CONVENTION.md

## Git 운영 규칙
- 작업 시작: 브랜치 분기 필수 ({type}/CUR-GO100-{TASK-ID})
- 커밋 전: bash scripts/pre-commit-check.sh 실행 필수
- 보호 파일 변경 시: git diff로 의도한 변경만 포함 확인
- GO100 카드 지원 코드 삭제 금지 (trade/page.tsx, ScheduleForm.tsx)
