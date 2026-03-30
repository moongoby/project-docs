# GO100 프로젝트 규칙
# globs: backend/app/routers/go100/**, backend/app/services/go100/**, frontend/src/go100/**, frontend/src/app/(protected)/go100/**, docs/**, .cursorrules

## 필수 참조 문서 (3계층 체계, 작업 전 반드시 읽기)

| 계층 | 파일 | 역할 | 읽기 시점 |
|------|------|------|-----------|
| Core | CONTEXT.md | 프로젝트 현황, 서버, DB, Agent, 규칙, 작업큐 | 매 세션 필수 |
| Directives | CEO-DIRECTIVES.md | CEO 투자철학, 전략 지시, 절대규칙 | 매 세션 필수 |
| Rules | go100-rules.md (본 파일) | 서비스 경계, 파일 목록, API, 문서 규칙 | 온보딩/규칙확인 |
| History L1 | /root/project-docs/go100/handover/HANDOVER.md | 현재 상태 요약, 즉시 체크리스트, 다음 작업 | 매 세션 필수 |
| History L2 | /root/project-docs/go100/handover/HANDOVER-DETAIL.md | 완료 작업 테이블, 아키텍처, DB, 파일 경로 | 이전 작업 참조 시 |
| Archive L3 | /root/project-docs/go100/handover/HANDOVER-ARCHIVE.md | 과거 전체 이력 + 핵심 발견 보관 | 장기 참조 시 |

### 기타 참조
- docs/ISSUES.md (미해결 이슈)
- docs/CHANGELOG.md (최근 변경)
- docs/ROADMAP.md (진행 상태)
- docs/DB_SCHEMA.md (테이블 구조)
- docs/API_SPEC.md (API 명세)
- docs/PLANNING.md (기획서)
- docs/ARCHITECTURE.md (아키텍처)

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

## API 키 보안 절대 규칙 (R-KEY)
- 절대 API 키를 소스코드/config 파일에 하드코딩하지 않는다
- 모든 시크릿은 `.env` 파일에만 저장
- 커밋 전 pre-commit hook이 API 키 패턴 자동 감지 → 차단
- 위반 시: 제공사가 키를 leaked 처리하여 영구 비활성화됨
