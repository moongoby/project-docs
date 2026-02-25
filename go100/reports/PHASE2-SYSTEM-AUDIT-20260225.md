# 백억이 2단계 사전조사 보고서 (v1.1)
> 작성일시: 2026-02-25 KST
> 작성자: Cursor AI
> 브랜치: phase-2c-command-center
> 목적: 2단계 자율형 백억이 구현을 위한 현재 시스템 완전 파악
> 참조: KIWOOM-DATA-COLLECTION-REPORT-20260225.md

---

## 1. 백엔드 구조

### 1-1. GO100 서비스 전체 (55개 .py)
```
backend/app/services/go100/
├── ai/           base_orchestrator.py, intent_router.py, llm_client.py, design_agent.py,
│                 evaluate_agent.py, optimize_agent.py, understand_agent.py, help_flow.py,
│                 help_knowledge.py, prompts.py, schemas.py, __init__.py
├── backtest/     backtest_service.py, data_loader.py, minute_data_loader.py, minute_simulator.py,
│                 partial_exit_simulator.py, signal_evaluator.py, simulator.py, schemas.py, __init__.py
├── live_trading/ live_engine.py, live_service.py, schemas.py, __init__.py
├── notification/ notification_service.py, __init__.py
├── optimizer/    backtest_optimizer.py, fit_engine.py, optimizer_service.py, schemas.py, __init__.py
├── paper_trading/ paper_engine.py, paper_scheduler.py, paper_service.py, schemas.py, __init__.py
├── portfolio/    portfolio_service.py, schemas.py, __init__.py
├── risk/         position_sizing.py, __init__.py
├── scheduler/    go100_scheduler.py, __init__.py
├── strategy/     card_service.py, schemas.py, __init__.py
├── universe/     advanced_filters.py, base_filter.py, data_cache.py, engine.py, expression_parser.py,
│                 fundamental_filter.py, ma_filter.py, market_cap_filter.py, price_filter.py,
│                 rsi_filter.py, scope_filter.py, volume_filter.py, __init__.py
└── user_utils.py
```

### 1-2. GO100 라우터 (12개 .py)
- `ai_router.py`, `backtest_router.py`, `live_trading_router.py`, `notification_router.py`, `optimizer_router.py`, `paper_trading_router.py`, `portfolio_router.py`, `risk_router.py`, `scheduler_router.py`, `strategy_router.py`, `trade_modal_router.py`, `__init__.py`

### 1-3. 코어 모듈 (38개 .py)
- **브로커**: `broker_base.py`, `broker_factory.py`, `broker_kis_adapter.py`, `broker_kiwoom_client.py`
- **인증/보안**: `auth.py`, `auth_v1.py`, `crypto.py`, `security_middleware.py`, `security_headers.py`, `token_manager.py`, `kiwoom_key_manager.py`
- **KIS**: `kis_api_registry.py`, `kis_config.py`, `kis_rate_limiter.py`
- **LLM**: `llm_gateway.py`, `llm_models.py`, `llm_cost_tracker.py`, `llm_rate_limiter.py`, `llm_clients/` (base, anthropic, gemini, openai)
- **인프라**: `config.py`, `database.py`, `deps.py`, `redis.py`, `logging_config.py`, `middleware.py`, `rate_limiter.py`, `error_handler.py`, `exception_handlers.py`
- **기타**: `account_mode.py`, `critical_risk_config.py`, `desk_config.py`, `enums.py`, `strategy_config.py`, `strategy_params.py`, `trade_logger.py`, `social_auth.py`

### 1-4. 전체 백엔드 라우터 (42개 .py)
- GO100 12개 + v4_* 20개 + account_sync, backtest, brain, calendar, execution, fund, metrics, monitoring_router, position, price, regime, report_router, strategy, system, universe, v4_admin, v4_ai_trading, v4_auth, v4_backtest, v4_chart, v4_compat, v4_dashboard, v4_data_pipeline, v4_email, v4_emergency, v4_kis, v4_liquidation, v4_notifications, v4_nxt_test, v4_orders, v4_reports, v4_settings, v4_social_auth, v4_system, v4_trading, v4_websocket

### 1-5. 데이터 수집 서비스 (15개 .py)
- `backtest_provider.py`, `base_provider.py`, `broker_trades_collector.py`, `condition_search_collector.py`, `credit_balance_collector.py`, `investor_collector.py`, `kis_api_interface.py`, **`kiwoom_credentials.py`**, `live_provider.py`, `program_trades_collector.py`, `sector_price_collector.py`, `theme_detail_collector.py`, `tick_data_collector.py`, `trade_strength_history_collector.py`, `__init__.py`

### 1-6. 스크립트 폴더 (161개 .py)
- `scripts/backtest/` 20개, `scripts/analysis/` 7개, `scripts/collection/` 11개, `scripts/docs/` 1개, `scripts/ops/` 1개
- 키움 수집: `collect_kiwoom_strength.py` (210줄), `collect_kiwoom_theme.py` (344줄)
- 기타: collect_*, run_*, test_*, nxt_*, verify_*, migrate_*, seed_* 등

### 1-7. 설정 (config.py 요약)
- 앱: app_name=KIS_AutoTrade_V4, app_env, app_host=0.0.0.0, app_port=8000
- DB: db_host/port/name/user/password, database_url, database_url_sync
- Redis: redis_host/port/db, redis_url
- KIS: kis_app_key, kis_app_secret, kis_account_no, kis_is_virtual
- 공공: data_go_kr_api_key
- 로깅: log_level, log_dir
- tz: Asia/Seoul
- SMTP: smtp_host/port/user/password/from (Optional)

---

## 2. DB 스키마 현황

### 2-1. 전체 테이블 수
- **174개** (public 스키마)

### 2-2. GO100 전용 테이블 (16개)
| 테이블명 | 용도 |
|----------|------|
| go100_account_reconciliation | 계좌 정합성 |
| go100_backtest_runs | 백테스트 실행 이력 |
| go100_desk_allocation | 데스크 자금 배분 |
| go100_fit_analysis | 전략-종목 적합도 |
| go100_notification_settings | 알림 설정 |
| go100_notifications | 알림 이력 |
| go100_optimization_runs | 최적화 실행 |
| go100_orders | 주문 |
| go100_portfolio_snapshots | 포트폴리오 스냅샷 |
| go100_portfolios | 포트폴리오 |
| go100_positions | 포지션 |
| go100_push_subscriptions | 푸시 구독 |
| go100_risk_disclaimers | 리스크 동의 |
| go100_strategy_cards | 전략 카드 |
| go100_strategy_store | 전략 스토어 |
| go100_trades | 체결/거래 |

GO100 테이블 컬럼: 270개 컬럼 (테이블별 상세는 조사 2-2 결과 참조).

### 2-3. 키움 신규 테이블 데이터 현황
| 테이블 | 행 수 |
|--------|------:|
| v4_theme_master | 100 |
| v4_theme_stock | 569 |
| v4_theme_detail | 100 |
| v4_trade_strength_history | 219,892 |
| v4_program_trades | 0 |

### 2-4. V4 공유·신규 테이블 (103개 목록)
- v4_* 99개 + index_daily, ohlcv_daily, stock_fundamentals, stock_universe

### 2-5. accounts 테이블 구조 (키 값 제외)
| column_name | data_type | is_nullable |
|-------------|-----------|-------------|
| account_id | bigint | NO |
| user_id | bigint | NO |
| broker_type | character varying | NO |
| account_number | character varying | NO |
| account_alias | character varying | YES |
| is_mock | boolean | NO |
| enc_app_key | text | NO |
| enc_app_secret | text | NO |
| enc_token | text | YES |
| token_expires_at | timestamp with time zone | YES |
| kis_config_id | integer | YES |
| daily_order_limit | numeric | NO |
| buy_blocked | boolean | NO |
| buy_blocked_at | timestamp with time zone | YES |
| buy_block_reason | character varying | YES |
| is_active | boolean | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |
| total_deposit | numeric | YES |
| total_evaluation | numeric | YES |

### 2-6. 브로커 계좌 현황
| account_id | broker_type | is_mock | is_active | account_number |
|------------|-------------|---------|-----------|----------------|
| 1 | KIS | t | t | 50160711 |
| 2 | KIS | t | t | 50160697 |
| 3 | KIS | t | t | 50000000-02 |
| 4 | KIWOOM | t | t | **81201280** (모의) |
| 5 | KIWOOM | f | t | 52568156 |
| 6 | KIWOOM | f | t | 63109343 |
| 7 | KIS | f | t | 74032243 |

- **전체 계좌 수**: 7
- **브로커별**: KIS 4 (모의 3, 실전 1), KIWOOM 3 (모의 1, 실전 2)

### 2-7. LLM 관련 테이블
- llm_cost_daily, llm_requests

---

## 3. 핵심 소스 분석

### 3-1. BaseOrchestrator
- **파일**: `backend/app/services/go100/ai/base_orchestrator.py` (**781줄**)
- **역할**: UNDERSTAND → DESIGN → BACKTEST → EVALUATE → (OPTIMIZE ≤5회) → PRESENT + DB 저장. 분봉 백테스트 우선, 일봉 폴백. AdvancedFilters 연동.
- **주요 클래스**: `BaseOrchestrator`, `_to_dict`
- **의존**: UnderstandAgent, DesignAgent, Go100EvaluateAgent, Go100OptimizeAgent, LLMClient, Go100MinuteSimulator, Go100AdvancedFilters

### 3-2. IntentRouter
- **파일**: `backend/app/services/go100/ai/intent_router.py` (76줄)
- **역할**: 채팅 메시지를 "strategy" | "help" | "optimize_existing" 로 분류 (규칙 기반 키워드/패턴).
- **함수**: `route_intent(user_message: str) -> str`

### 3-3. LLM Gateway
- **파일**: `backend/app/core/llm_gateway.py` (**400줄**)
- **LLM 관련 경로**: core/llm_*.py, core/llm_clients/, api/v1/llm_router.py, services/llm/, services/go100/ai/llm_client.py, schemas/llm_schemas.py

### 3-4. AI Router
- **파일**: `backend/app/routers/go100/ai_router.py` (302줄)
- **엔드포인트**: POST /api/go100/ai/chat, /evaluate, /optimize, /understand, /design
- **흐름**: route_intent → help면 HelpFlow, optimize_existing면 BacktestOptimizer, 아니면 BaseOrchestrator.process_message

### 3-5. KIS API 연동
- **파일**: broker_kis_adapter.py, kis_api_registry.py, kis_config.py, kis_rate_limiter.py, v4_kis.py, kis_api_interface.py, data_pipeline/kis_api_client.py, trading/kis_order_service.py (pyc 제외)

### 3-6. 키움 자격증명 모듈 (kiwoom_credentials.py, 89줄)
- **역할**: 환경변수(KIWOOM_APP_KEY/SECRET) 우선 → DB accounts (KIWOOM, is_active) 복호화 폴백. KiwoomBrokerClient 반환.
- **함수**: `get_kiwoom_client()`, `_load_from_db()` (psycopg2 + crypto_service.decrypt)

### 3-7. 키움 컬렉터 (총 866줄)
| 파일 | 줄 수 |
|------|------:|
| kiwoom_credentials.py | 89 |
| theme_detail_collector.py | 111 |
| trade_strength_history_collector.py | 126 |
| program_trades_collector.py | 151 |
| condition_search_collector.py | 191 |
| tick_data_collector.py | 198 |

### 3-8. 키움 수집 스크립트
- collect_kiwoom_strength.py 210줄, collect_kiwoom_theme.py 344줄 (총 554줄)

### 3-9. BacktestOptimizer
- **파일**: `backend/app/services/go100/optimizer/backtest_optimizer.py` (**555줄**)
- **기타**: optimizer_router.py, param_optimizer.py, optimize_agent.py, optimizer_service.py

### 3-10. CryptoService (암호화)
- **파일**: `backend/app/core/crypto.py` (accounts enc_app_key/enc_app_secret 복호화에 사용)

### 3-11. KiwoomBrokerClient
- **정의**: `backend/app/core/broker_kiwoom_client.py` (class KiwoomBrokerClient(BaseBrokerClient))
- **사용처**: broker_factory.py, kiwoom_credentials.py, account_service.py, balance_sync_service.py

---

## 4. 프론트엔드 구조

### 4-1. GO100 전용
- **앱 라우트**: (protected)/go100/chat, error, layout, live-trading, notifications, page, paper-trading, settings, store, strategies
- **API/훅/타입**: go100/api/go100Api.ts, hooks (useDashboard, useLiveTrading, useNotifications, usePaperTrading, useRisk, useStrategies 등), types (ai, backtest, live-trading, paper-trading, portfolio, position, risk, strategy)
- **컴포넌트**: ChatInterface, ChatMessage, ChatWidget, DashboardContent, StrategyCard, StrategyDetailModal, LiveTradingDetailContent, PaperTradingDetailContent, Go100Sidebar, AutoTradeModal, RiskConfigForm 등 (go100/components/, strategy 하위 포함)

### 4-2. 대시보드
- (protected)/dashboard/page.tsx, components/dashboard/ (AccountsCard, AccountSummaryCard, ActiveStrategiesCard, AssetAllocationCard, BaekogiWelcomeBanner, EmergencyStopWidget, HoldingsCard, InvestorFlowWidget, LLMUsageCard, MarketRankingsWidget, MetricCards, RecentTradesCard, SyncStatusWidget, SystemStatusCard, ThemesSectorsWidget, TodayBriefingCard 등), lib/api/dashboard.ts

### 4-3. 채팅
- go100/chat/page.tsx, go100/components/ChatInterface, ChatMessage, ChatWidget, components/chat/ (ChannelSelector, ChatInput, ChatMessage, LegalNotice, SessionList, StrategyCardSaveButton, StrategyPreviewModal, WelcomeScreen), components/llm/ (ChatMessageBubble, ChatWindow), lib/store/chat-store.ts

---

## 5. 서비스 운영 현황

### 5-1. 서비스 상태
- **go100.service**: active (running), 127.0.0.1:8002, uvicorn workers 2
- **go100-frontend.service**: active (running), Next.js 14.2.35, port 3000

### 5-2. Git
- **현재 브랜치**: phase-2c-command-center (up to date with origin)
- **최근 커밋**: 30ab98e1 feat: 키움증권 REST API 데이터 수집 인프라 구축 및 테마·체결강도 수집 완료
- **상태**: Changes not staged — 주로 .venv 내 numpy 등 (프로젝트 소스 변경 없음)

### 5-3. 환경변수 (API키 제외)
- KAKAO/NAVER/GOOGLE 소셜 클라이언트 ID, REDIRECT_URI, SOCIAL_REDIRECT_BASE_URL

### 5-4. Redis
- PONG 정상. `token:kiwoom:kiwoom:default`, `token:kis:kis:4` 존재.

### 5-5. cron
- **crontab**: 없음 (root 사용자)
- **/etc/cron.d/**: KIS AutoTrade V4.1 Data Collection 등 (vkospi_alt, data_miner 토큰 갱신, disk_monitor, db_backup, alert_cron, minute_batch_cron, stock_universe, ohlcv_daily, legacy drop, index_daily, market_investor, stock_industry). **키움 테마/체결강도/프로그램매매 전용 cron 항목은 없음.**

---

## 6. 문서 현황

### 6-1. 로컬
- **docs**: 599개 .md (architecture, api, go100, kis-api-portal, reports, plan 등)
- **report**: 185개 .md (KIWOOM-DATA-COLLECTION-REPORT-20260225.md, BAEKOGI-AI-TECH-DOCS-REPORT-20260225.md, v41/, go100/, ADMIN-*, GO100-* 등)

### 6-2. project-docs
- **위치**: /root/project-docs (존재)
- **구성**: common/, go100/, kis-autotrade-v4/, scripts 등. go100/docs (BAEKEOGI-TECH-SPEC, DB-SCHEMA-GO100, go100-architecture-v1.1), go100/reports (BAEKOGI-AI-TECH-DOCS-REPORT-20260225.md 등)

---

## 7. 브로커 연동 아키텍처 분석

### 7-1. 브로커/클라이언트/어댑터 클래스
| 클래스 | 파일 | 역할 |
|--------|------|------|
| BaseBrokerClient | broker_base.py | ABC: authenticate, buy, sell, modify_order, cancel_order, get_balance, get_quote |
| BrokerType | broker_base.py | KIS, KIWOOM enum |
| KISBrokerAdapter | broker_kis_adapter.py | KIS 래퍼 (kis_client, kis_order_service) |
| KiwoomBrokerClient | broker_kiwoom_client.py | 키움 REST API 클라이언트 (app_key, secret_key, is_production, key_manager) |
| BrokerFactory | broker_factory.py | broker_type별 KIS/KIWOOM 인스턴스 생성. 키움 시 kiwoom_key_manager 연동. |
| LegacyCompatAdapter | legacy_adapter.py | 레거시 호환 |
| KISAPIClient | data_pipeline/kis_api_client.py | KIS API 호출 |

### 7-2. 주문 관련 코드 (일부)
- v4_order_executor.py, v4_trade_bridge.py, kis_order_service.py, broker_kis_adapter.py, broker_kiwoom_client.py, order_fulfillment.py, v4_orders.py, schemas/order.py, execution/order_executor.py

### 7-3. 실매매/트레이딩 엔진
- live_trading/live_engine.py, live_service.py | paper_trading/paper_engine.py, paper_service.py | trading/v4_trade_bridge.py, v4_order_executor.py, kis_order_service.py | execution/order_executor.py | auto_trade_engine.py

### 7-4. 스케줄러/잡
- go100_scheduler.py, paper_scheduler.py, scheduler_router.py | account_sync_scheduler.py, phase2_data_scheduler.py, phase3_data_scheduler.py | scheduler/daily_scheduler.py

### 7-5. accounts 테이블 사용처 (일부)
- account_service.py, balance_sync_service.py, broker_factory.py, broker_kiwoom_client.py, kiwoom_credentials.py, card_service.py, portfolio_service.py, live_engine.py, paper_engine.py, v4_order_executor.py, v4_trade_bridge.py, v4_pipeline_orchestrator.py, kis_order_service.py, token_manager.py, account_schemas.py, v4_kis.py, admin_router.py, accounts_router.py 등

---

## 8. 2단계 구현 영향도 분석

### 8-1. 기존 파일 중 수정 필요 목록 (최소화)
- **accounts 사용처**: 2단계에서 계좌 선택/브로커 라우팅 추가 시, account_service, balance_sync_service, broker_factory, token_manager 등에서 **account_id/ broker_type** 기준 분기만 확장하면 됨. 기존 KIS/키움 로직 교체 최소화.
- **GO100**: live_engine, paper_engine, paper_scheduler — **키움 모의(81201280) Paper Trading** 연동 시 계좌 소스(accounts) 및 BrokerFactory 경로만 명시. 기존 KIS 실전/모의 플로우 유지.
- **라우터**: v4_orders, v4_trading, go100/trade_modal_router — BrokerGateway 경유 시 Depends/팩토리만 주입하면 되므로 **신규 계층 추가**로 기존 라우터 시그니처는 유지 가능.

### 8-2. 새로 생성할 파일 목록
- **BrokerGateway** (또는 broker_gateway.py): account_id → BrokerFactory.create(broker_type) + 토큰/잔고 캐시. 기존 broker_factory 확장 또는 상위 퍼사드.
- **2단계 전용 설정/스키마**: go100_broker_accounts 사용 시 스키마 1개, 마이그레이션 1개.
- **키움 Paper 전용 훅** (선택): paper_engine에서 계좌 81201280 고정 또는 설정 테이블에서 읽기.

### 8-3. DB 마이그레이션 필요 사항
- **accounts 테이블 확장 vs go100_broker_accounts**: 현재 accounts에 이미 broker_type, is_mock, account_number, enc_* 등이 있으므로 **2단계 1차는 accounts 확장 없이 기존 테이블만 사용** 가능. GO100 전용 “선택 계좌/데스크” 매핑이 필요하면 go100_desk_allocation 또는 go100_strategy_cards의 account_id로 충족. **go100_broker_accounts 신규 생성은 “GO100 전용 브로커 설정/할당”이 명확히 필요할 때만 권장.**

### 8-4. accounts 확장 vs go100_broker_accounts 신규 생성 판단
- **판단**: 우선 **accounts만 사용**. 이미 KIWOOM/KIS, is_mock, account_number, enc_app_key/enc_app_secret 존재. 2단계에서 “여러 계좌 중 어떤 계좌로 주문/잔고를 쓸지”는 기존 go100_strategy_cards.account_id, go100_portfolios 등으로 해결 가능. **go100_broker_accounts**는 “GO100 전용 브로커 프로파일(이름, 기본 주문 한도, 사용 여부)” 등이 필요해질 때 도입 검토.

### 8-5. 기존 서비스 영향도 평가
- **목표**: 0 영향. 신규 BrokerGateway/계좌 라우팅은 기존 호출 경로를 대체하지 않고, **새 엔드포인트 또는 기존 엔드포인트에 선택적 주입**으로 구현 가능. go100, v4_orders, v4_trading은 기존대로 동작하고, 2단계 플래그/계좌가 있을 때만 Gateway 경유.

### 8-6. 키움 모의계좌(81201280) Paper Trading 활용 방안
- accounts에 이미 account_id=4, KIWOOM, is_mock=true, 81201280 등록. **Paper Trading 엔진(paper_engine/paper_scheduler)**에서 “모의 계좌 전용” 모드 추가 시, account_id=4를 소스로 하여 KiwoomBrokerClient(app_key, secret, is_production=False)로 주문/잔고 호출. 기존 KIS 모의와 동일하게 “실제 주문은 하되 모의 환경”으로 처리 가능. Redis token:kiwoom:* 은 모의/실전 구분 키 사용(현재 kiwoom:default 등).

### 8-7. 기존 키움 컬렉터와 2단계 데이터 파이프라인 통합 방안
- **컬렉터**: 테마/체결강도/프로그램매매는 **데이터 수집 전용**이며, kiwoom_credentials → KiwoomBrokerClient로 인증만 공유. 2단계 “트레이딩” 파이프라인(주문/잔고)은 동일 KiwoomBrokerClient를 **BrokerGateway 경유**로 사용하면 됨. 수집 스크립트(collect_kiwoom_theme, collect_kiwoom_strength)와 장중 프로그램매매 수집은 **기존 cron/스케줄에 추가**만 하면 되며, 2단계와 코드 공유는 kiwoom_credentials + BrokerFactory/KiwoomBrokerClient에 한정. **통합**: 동일 자격증명·동일 클라이언트; “수집” vs “주문”은 사용처만 구분.

---

## 9. 2단계 구현 우선순위 TOP 5

1. **BrokerGateway 도입 (account_id → broker_type → BaseBrokerClient)**  
   - broker_factory와 token/잔고 캐시를 묶은 퍼사드. 기존 v4_order_executor, live_engine, paper_engine에서 account_id만 넘기면 올바른 브로커 인스턴스 반환. 기존 서비스 변경 최소화.

2. **키움 모의(81201280) Paper Trading 연동**  
   - paper_engine/paper_scheduler에서 account_id=4 또는 “키움 모의” 계좌 선택 시 KiwoomBrokerClient(is_production=False)로 주문/잔고 호출. Redis 토큰 키 모의/실전 구분 정리.

3. **키움 데이터 수집 cron 정리**  
   - KIWOOM-DATA-COLLECTION-REPORT 대로 테마 일 1회(17:00), 체결강도 증분, 프로그램매매 장중(16:30) cron 등록. 기존 컬렉터·스크립트 재사용.

4. **2단계 계좌 선택/할당 정책 고정**  
   - “GO100 전용 계좌”를 accounts + go100_strategy_cards.account_id로만 쓸지, go100_broker_accounts 신규 테이블이 필요한지 결정. 1차는 accounts만 사용 권장.

5. **영향도 0 유지 검증**  
   - BrokerGateway 추가 후 기존 KIS 실전/모의, 기존 키움 수집·인증 동작 회귀 테스트. v4_orders, v4_trading, go100 라우터 단위 테스트로 기존 동작 보존 확인.

---

## 요약 수치 (작업 완료 보고용)

| 항목 | 값 |
|------|-----|
| 전체 테이블 수 | 174 |
| GO100 테이블 수 | 16 |
| 키움 관련 v4 테이블 (테마/체결강도/프로그램) | 5 (v4_theme_master, v4_theme_stock, v4_theme_detail, v4_trade_strength_history, v4_program_trades) |
| 백엔드 .py 파일 수 | 461 |
| 스크립트 .py 파일 수 | 161 |
| **전체 Python 파일 수 (백엔드+스크립트)** | **622** |
| accounts 계좌 수 | 7 (KIS 4, KIWOOM 3) |
| 기존 자동매매/스케줄러 | 있음. go100_scheduler, paper_scheduler, daily_scheduler, account_sync_scheduler, phase2/3_data_scheduler 등 |
| 2단계 최우선 이슈 TOP 3 | ① BrokerGateway 도입 ② 키움 모의 Paper 연동 ③ 키움 수집 cron 정리 |
| 기존 시스템 영향도 | **없음** (신규 계층·선택적 주입으로 0 영향 목표 가능) |
