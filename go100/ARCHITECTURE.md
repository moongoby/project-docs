# GO100 시스템 아키텍처
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.0

## 1. 시스템 개요
```
사용자 → Nginx → Next.js(:3000) → FastAPI(:8002) → PostgreSQL
                                              → Redis
                                              → KIS API
                                              → LLM API
```

## 2. 인프라
- **서버**: Linux kis-autotrade-v4 6.8.0-84-generic #84-Ubuntu SMP PREEMPT_DYNAMIC x86_64 GNU/Linux
- **디스크**: /dev/vda2 99G 51G 45G 54% /
- **메모리**: total 15Gi, used 4.3Gi, available 11Gi
- **Python**: 3.12.3
- **Node**: v18.19.1
- **npm**: 9.2.0

## 3. 백엔드
- **프레임워크**: FastAPI 0.128.8
- **ASGI**: uvicorn 0.40.0
- **서비스**: systemd go100 (localhost:8002), active
- **경로**: /root/kis-autotrade-v4/backend
- **실행**: /root/kis-autotrade-v4/venv/bin/python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002 --workers 2
- **주요 패키지**: asyncpg 0.31.0, fastapi 0.128.8, openai 2.21.0, psycopg2-binary 2.9.11, pydantic 2.12.5, redis 7.1.1, SQLAlchemy 2.0.46, uvicorn 0.40.0

### 3.1 라우터 구조 (main.py include_router)
- system_router, v4_signal_api_router, v4_position_api_router, v4_alert_api_router, v4_backtest_api_router
- fund_router, execution_router, position_router, regime_router, calendar_router, universe_router, price_router, brain_router, metrics_router, strategy_router
- v4_system, v4_trading, v4_backtest, v4_auth, v4_email, v4_ai_trading, v4_orders (prefix /api/v4)
- dashboard_v1_router (/api/v1/dashboard), portfolio_v1_router, market_v1_router, trade_router (/api/v1/trade), notification_router, settings_router (/api/v1/settings)
- health_router, monitoring_router, v4_compat (/api/v1), auth_v1_router, social_auth_v1_router, accounts_v1_router, account_sync_router, user_settings_v1_router
- strategy_cards_v1_router (/api/v1), backtest_router (/api/v1), report_router (/api/v1), admin_v1_router, llm_v1_router (/api/v1)
- v4_websocket, v4_reports, v4_admin, v4_kis, v4_settings, v4_emergency, v4_liquidation, v4_notifications, v4_social_auth, v4_data_pipeline, v4_dashboard, v4_desk_recommend_router, v4_chart (/api/v4)
- **GO100**: go100_portfolio_router, go100_strategy_router, go100_store_router, go100_backtest_router, go100_ai_router, go100_paper_trading_router, go100_risk_router, go100_live_trading_router, go100_scheduler_router, go100_optimizer_router
- app.mount: /static/v4-dashboard

### 3.2 GO100 전용 파일 (backend)
- **라우터**: backend/app/routers/go100/ai_router.py, backtest_router.py, live_trading_router.py, optimizer_router.py, paper_trading_router.py, portfolio_router.py, risk_router.py, scheduler_router.py, strategy_router.py
- **서비스**: backend/app/services/go100/ai/ (base_orchestrator, design_agent, evaluate_agent, llm_client, optimize_agent, prompts, schemas, understand_agent)
- backend/app/services/go100/backtest/ (backtest_service, data_loader, minute_data_loader, minute_simulator, partial_exit_simulator, schemas, signal_evaluator, simulator)
- backend/app/services/go100/live_trading/, optimizer/, paper_trading/, portfolio/, risk/, scheduler/, strategy/ (card_service, schemas), universe/ (advanced_filters, base_filter, data_cache, engine, expression_parser, fundamental_filter, ma_filter, market_cap_filter, price_filter, rsi_filter, scope_filter, volume_filter)
- backend/app/services/go100/user_utils.py

### 3.3 핵심 서비스
- card_service.py: 전략카드 CRUD
- base_orchestrator.py: AI 대화 → 전략 생성
- user_utils.py: legacy ↔ v4 user_id 변환
- strategy_card_service.py (api/v1): catalog API (V4+GO100 병합)

## 4. 프론트엔드
- **Next.js**: 14.2.35, name: frontend, version: 0.1.0
- **서비스**: systemd go100-frontend (localhost:3000), active
- **경로**: /root/kis-autotrade-v4/frontend
- **실행**: npx next start -p 3000, NODE_ENV=production, NEXT_PUBLIC_API_URL=http://localhost:8002

### 4.1 페이지 라우트 (page.tsx)
- auth: callback, forgot-password, login, signup
- app: page, offline, privacy, terms
- (protected): accounts, admin, backtest, dashboard, llm, monitoring, notifications, portfolio, reports, settings, strategy-cards, trade
- (protected)/go100: page, chat, live-trading, live-trading/[id], paper-trading, paper-trading/[id], settings, store, strategies, strategies/[id]

### 4.2 GO100 전용 파일 (frontend)
- app/(protected)/go100/*.tsx (chat, error, layout, live-trading, paper-trading, settings, store, strategies)
- go100/api (go100Api.ts, index.ts)
- go100/components (AIProgressIndicator, ChatInterface, ChatMessage, ChatWidget, ConfirmModal, DashboardContent, DisclaimerModal, Go100Layout, Go100Sidebar, StrategyCard, StrategyCardDetail, strategy/*, LiveTradingDetailContent, PaperTradingDetailContent, PortfolioChart, PositionTable, RiskConfigForm, SettingsRiskSection, StatusBadge, Toast, TradeTable 등)
- go100/hooks, go100/types

## 5. 데이터베이스
- PostgreSQL, DB: kisautotrade, User: kis_admin, Host: localhost:5432
- **공개 테이블 수**: 100개 이상 (pg_stat_user_tables 기준)

### 5.1 주요 테이블 + 행수 (일부)
| table_name | row_count |
|------------|-----------|
| go100_strategy_cards | 3 |
| go100_backtest_runs | 0 |
| go100_desk_allocation | 2 |
| go100_fit_analysis | 40 |
| strategy_cards | 62 |
| v4_users | 4 |
| v4_positions | 24 |
| accounts | 7 |
| users | 12 |

(전체 목록은 DB_SCHEMA.md 참조)

## 6. 외부 연동
- KIS API (한국투자증권)
- Redis (세션/캐시)
- LLM API (OpenAI, Anthropic, Google AI 등)

## 7. 환경변수 (.env 키 목록, 값 마스킹)
ALLOWED_IPS=****, ANTHROPIC_API_KEY=****, APP_DEBUG=****, APP_ENV=****, APP_HOST=****, APP_NAME=****, APP_PORT=****, DATABASE_URL=****, DATABASE_URL_SYNC=****, DATA_GO_KR_API_KEY=****, DB_HOST=****, DB_NAME=****, DB_PASSWORD=****, DB_PORT=****, DB_USER=****, DRY_RUN=****, ENCRYPTION_KEY=****, GEMINI_API_KEY=****, GOOGLE_AI_API_KEY=****, INTERNAL_API_KEY=****, JWT_ACCESS_TOKEN_EXPIRE_MINUTES=****, JWT_ALGORITHM=****, JWT_SECRET_KEY=****, KIS_* (계좌/API 관련), LLM_* (채팅/일한도 등), LOG_*, REDIS_*, SECRET_KEY=****, SMTP_*, TOTAL_KIS_RPS=****, TRUSTED_PROXY_IPS=****, TZ=****
