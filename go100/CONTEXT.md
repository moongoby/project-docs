# GO100 프로젝트 컨텍스트 (Claude PM용)
> 이 파일을 Claude 새 대화 첫 메시지 URL로 전달하면 전체 맥락을 즉시 파악합니다.
> Public URL: https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md
> 최종 갱신: 2026-02-23

## 1. 프로젝트 개요
- GO100: AI 주식 자동매매 SaaS
- V4.1 코드베이스 공유
- 도메인: go100.newtalk.kr, trading41.newtalk.kr
- GitHub: moongoby/go100 (private)
- 진행률: 약 90%

## 2. 서버 환경
- 서버: root@kis-autotrade-v4
- 프로젝트: /root/kis-autotrade-v4
- 브랜치: phase-2c-command-center
- DB: kisautotrade / kis_admin / ****
- 백엔드: FastAPI localhost:8002, systemd go100 (active)
- 프론트: Next.js 14.2.35 localhost:3000, systemd go100-frontend (active)

## 3. 계정
- moongoby@naver.com: v4_users.user_id=3 (GO100 카드 소유)
- moongoby@gmail.com: v4_users.user_id=2
- ★ get_effective_uid() 필수 (legacy users.id ≠ v4_users.user_id)

## 4. 절대 작업 규칙
1. go100_* 파일/테이블만 수정
2. 헤더 코멘트 (작업ID, 날짜)
3. .env/.bak 커밋 금지
4. DB 스키마 go100_* 한정
5. 백업→확인→수정→빌드→재시작→검증→커밋→보고서→문서갱신

## 5. 전략카드 현재 상태
| go100_card_id | strategy_name | user_id | card_status | is_active | is_featured | is_public | featured_order |
|---------------|---------------|---------|-------------|-----------+-------------|-----------+----------------|
| 13 | [스캘핑] 분봉 스캘핑 고변동 대형주 | 3 | BACKTESTED | t | t | t | 1 |
| 14 | [데일리] 대형 우량주 수급 데일리 전략 | 3 | BACKTESTED | t | t | t | 2 |
| 15 | [단기스윙] 섹터모멘텀 외국인수급 스윙 | 3 | BACKTESTED | t | t | t | 3 |

## 6. GO100 테이블 행수
| 테이블 | 행수 |
|--------|------|
| go100_strategy_cards | 3 |
| go100_backtest_runs | 0 |
| go100_desk_allocation | 2 |
| go100_fit_analysis | 40 |
| go100_orders | 0 |
| go100_portfolios | 0 |
| go100_positions | 0 |
| go100_trades | 0 |

## 7. API 구조
### GO100 (/api/go100)
- POST/GET/PUT/DELETE /api/go100/strategy-cards, PATCH /api/go100/strategy-cards/{id}/toggle
- POST /api/go100/ai/chat
- POST /api/go100/backtest/run
- /api/go100/portfolios, store, paper-trading, live-trading, risk, scheduler, optimizer

### Catalog (/api/v1/strategy-cards)
- GET /catalog?tab=all|my|v4, GET /for-backtest

## 8. 최근 커밋 (20건)
- dead44f1 fix: CUR-GO100-PHASE2-STABILIZE (ISS-001/002/003 + cursorrules)
- acca08c0 docs: 문서 체계 구축
- 08a3b2ba fix: CUR-GO100-HOTFIX-IMPORT
- 8da6191b fix: CUR-GO100-HOTFIX-CRITICAL
- 556ddb17 BT-ENGINE-UPGRADE
- d34fb1d5 feat: CUR-GO100-UNIFIED-SAVE-BE
- 66b0038f feat: CUR-GO100-UNIFIED-SAVE-FE
- 67b83d3b fix: CUR-GO100-MY-STRATEGY-FIX
- 1a9c4219 feat: CUR-GO100-CARD-DETAIL-FIX
- 5351de40 fix: CUR-GO100-MY-STRATEGY-FIX
- 51018376 fix: CUR-GO100-CHAT-POSITION-FIX
- af0dbf5f feat: CUR-GO100-CARD-REDESIGN-FE
- 09f94b56 feat: CUR-GO100-CARD-REDESIGN-BE
- d0a09050 DESK-RECOMMEND
- 5a891210 feat: CUR-GO100-CHAT-WIDGET
- 7b75221e DASH-RESTORE
- e6ea2b2e feat: CUR-GO100-FIX-BACKEND
- 1165d00d feat: CUR-GO100-FIX-FRONTEND
- b61e68e1 DASH-FIX
- 4f8fef24 feat: CUR-GO100-STRATEGY-CARD-FIX
- 07c03316 feat: CUR-GO100-STRATEGY-INTEGRATE

## 9. 미해결 이슈
- (없음)

## 10. 로드맵
- Phase 2 (현재): 안정화 5개 항목
- Phase 3: 고도화 5개 항목
- Phase 4: 런칭 4개 항목

## 11. 핵심 파일 경로
### 백엔드
- backend/app/routers/go100/strategy_router.py
- backend/app/services/go100/strategy/card_service.py
- backend/app/services/go100/ai/base_orchestrator.py
- backend/app/services/go100/user_utils.py
- backend/app/services/strategy_card_service.py (catalog)
- backend/app/api/v1/strategy_cards_router.py

### 프론트엔드
- frontend/src/app/(protected)/layout.tsx
- frontend/src/app/(protected)/strategy-cards/page.tsx
- frontend/src/app/(protected)/llm/page.tsx
- frontend/src/app/(protected)/backtest/page.tsx
- frontend/src/go100/components/ChatWidget.tsx
- frontend/src/go100/api/go100Api.ts
- frontend/src/components/chat/StrategyCardSaveButton.tsx (확인 필요)

### 문서
- docs/ (9개: PLANNING, ARCHITECTURE, DB_SCHEMA, API_SPEC, HANDOVER, CHANGELOG, ISSUES, ROADMAP, CONTEXT)
- .cursorrules

## 12. 문서 관리
- 서버: /root/kis-autotrade-v4/docs/ (Cursor용)
- Public: moongoby/project-docs/go100/ (Claude용)
- 동기화: bash /root/project-docs/scripts/sync_go100.sh
- 작업 완료 시 반드시 docs/ 갱신 + sync 실행
