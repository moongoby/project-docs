# GO100 프로젝트 컨텍스트 (Claude PM용)
> Public URL: https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md
> 최종 갱신: 2026-02-24

## 1. 프로젝트 개요
- GO100: AI 대화 기반 전략카드 생성·백테스트·자동매매 서비스
- 도메인: go100.newtalk.kr
- GitHub: moongoby/kis-autotrade-v4 (코드), moongoby/project-docs (문서)
- 문서 경로: project-docs/go100/

## 2. 서버 환경
- 서버: root@211.188.51.113
- 프로젝트: /root/kis-autotrade-v4
- 브랜치: phase-2c-command-center
- DB: PostgreSQL 16, kisautotrade / kis_admin / localhost:5432
- GO100 백엔드: localhost:8002 (uvicorn, systemd: go100)
- GO100 프론트엔드: localhost:3000 (Next.js 14, systemd: go100-frontend)
- Python 3.12, FastAPI, Redis 7.x

## 3. GO100 절대 규칙
1. go100_* 파일/테이블만 수정
2. kis-v41-* 서비스 재시작 금지
3. strategy_cards ALTER/DROP/DELETE 금지 (GO100은 go100_strategy_cards만 사용)
4. v4_positions 직접 수정 금지
5. .env/.bak 커밋 금지
6. GO100 보고서는 반드시 go100/reports/ 에 저장
7. 파일명 규칙: CUR-GO100-{TASK}-{SEQ}-{YYYYMMDD}.md

## 4. GO100 DB 테이블
| 테이블 | 행수 | 설명 |
|--------|------|------|
| go100_strategy_cards | 6 | 전략카드 (PK: go100_card_id) |
| go100_fit_analysis | 40 | 적합도 분석 |
| go100_desk_allocation | 2 | 데스크 배분 |
| go100_backtest_runs | 0 | 백테스트 |
| go100_orders | 0 | 주문 |
| go100_positions | 0 | 포지션 |
| go100_trades | 0 | 체결 |
| go100_portfolios | 0 | 포트폴리오 |

## 5. GO100 API
- POST/GET/PUT/DELETE /api/go100/strategy-cards
- PATCH /api/go100/strategy-cards/{id}/toggle
- POST /api/go100/ai/chat
- POST /api/go100/backtest/run
- GET /api/v1/strategy-cards/catalog?tab=all|my

## 6. 핵심 파일
### 백엔드
- backend/app/routers/go100/strategy_router.py
- backend/app/services/go100/strategy/card_service.py
- backend/app/services/go100/ai/base_orchestrator.py
- backend/app/services/go100/universe/advanced_filters.py
- backend/app/services/auto_trade_engine.py

### 프론트엔드
- frontend/src/go100/components/ChatWidget.tsx
- frontend/src/go100/api/go100Api.ts
- frontend/src/app/(protected)/strategy-cards/page.tsx
- frontend/src/app/(protected)/layout.tsx

## 7. 공유 테이블 (V4.1과 공유, 읽기 전용)
- strategy_cards (60행) — V4.1 관리
- v4_trade_schedules (3 active)
- v4_market_regime_daily (59행)
- index_daily (1,467행, 150행 OHLC=0)
- ohlcv_daily, market_data_min

## 8. 서비스 현황
| 서비스 | 포트 | 상태 |
|--------|------|------|
| go100 (백엔드) | 8002 | active |
| go100-frontend | 3000 | active |
| nginx | 80/443 | active (go100.newtalk.kr) |

## 9. user_id 매핑 (중요)
- moongoby@naver.com: v4_users.user_id=3, legacy users.id=15
- moongoby@gmail.com: v4_users.user_id=2, legacy users.id=6
- JWT에는 legacy id → get_effective_uid() 사용 필수

## 10. 문서 체계
- 컨텍스트: go100/CONTEXT.md (이 파일)
- 규칙: go100/rules/go100-rules.md
- 보고서: go100/reports/CUR-GO100-{TASK}-{SEQ}-{YYYYMMDD}.md
- 인계서: go100/HANDOVER-{YYYYMMDD}.md
- 아키텍처: go100/ARCHITECTURE.md
- DB 스키마: go100/DB_SCHEMA.md, go100/docs/DB-SCHEMA-GO100.md
- API 명세: go100/API_SPEC.md

## 11. AI 세션 시작 시 필수 읽기
1. https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md (이 파일)
2. https://raw.githubusercontent.com/moongoby/project-docs/master/go100/rules/go100-rules.md
3. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/CLAUDE.md

## 12. 현재 작업 상태 (2026-02-24 기준)
### 완료
- CHATWIDGET-FIX-004: tailwind content 경로 추가
- CARD-DELETE-FIX-001: GO100 삭제 API 분기
- INVEST-AMOUNT-FIX-001: invest_amount 주문수량 반영
- INDEX-DAILY-FIX-001: OHLC 필드명 수정 (재수집 대기)
- REGIME-SOURCE-AUDIT-001: 레짐 소스 비교 분석
- E2E-TRADE-VERIFY-001: 자동매매 수량 계산 검증

### 대기
- P0-remnant: index_daily 재수집 (KIS 토큰 필요)
- P1: GO100 레짐 소스 통일 (CEO 결정: A 통일 vs B 독립)
- P2: 2/24 장중 invest_amount 로그 모니터링
- P3: 레짐 방어 모드 Layer 1+4 구현
