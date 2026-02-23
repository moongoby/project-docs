"""
KIS AutoTrade V4.0 — FastAPI 메인 앱
Orchestrator 통합 버전
"""
# Modified by CUR-DASHBOARD-v1, 2026-02-19 — dashboard_router 등록
# Modified by CUR-J-CRUD-v1, 2026-02-19, R4 Accounts/StrategyCards API 라우터 등록
# Modified by CUR-K-INTEGRATE-v1, 2026-02-19, R5 Admin/LLM 라우터, rate_limiter 초기화, session cleanup
# Modified by CUR-R-RATE-INIT-POLICY-v1, 2026-02-19
# Modified by CUR-S-ERROR-HANDLER-v1, 2026-02-19
# Modified by CUR-AR-KAKAO-AUTH-v1 + CUR-AS-NAVER-AUTH-v1, 2026-02-19
# Modified by CUR-SOCIAL-ENV-COPY-v1, 2026-02-20 — backend/.env 소셜 키 로드
# Modified by CUR-AUTO-TRADE-v1, 2026-02-20 — trade_router 등록
# Modified by CUR-USER-SETTINGS-v1, 2026-02-20 — user_settings_router 등록
# Modified by CUR-PORTFOLIO-DETAIL-v1, 2026-02-20 — portfolio_router 등록
# Modified by CUR-REALTIME-PRICE-v1, 2026-02-20 — market_router 등록
# Modified by CUR-MONITORING-HEALTH-v1, 2026-02-20 — health_router 등록
# Modified by CUR-SCHEDULED-RUNNER-v1, 2026-02-20 — ScheduleRunner startup/shutdown
# Modified by CUR-LLM-GATEWAY-CORE-v1, 2026-02-20 — LLMGateway 초기화
# Modified by #2026-0220-M, 2026-02-20 — v4_signal_api, v4_position_api (시그널/포지션 시각화)
# Modified by #2026-0220-O, 2026-02-20 — v4_alert_api (알림 시스템)
# Modified by CUR-LOG-SYSTEM-v1, 2026-02-20 — setup_logging() 연결
# Modified by CUR-ACCOUNT-SYNC-MANAGER-v1, 2026-02-20 — account_sync_router 등록
# Modified by CUR-DATA-COLLECTOR-PHASE2-v1, 2026-02-20 — Phase2 데이터 스케줄러 등록
# Modified by CUR-DATA-COLLECTOR-PHASE3-v1, 2026-02-20 — Phase3 데이터 스케줄러 등록
# Modified by CUR-MONITORING-DASHBOARD-v1, 2026-02-20 — monitoring_router 등록
# Modified by CUR-AUTO-REPORT-v1, 2026-02-20 — report_router 등록

import asyncio
from pathlib import Path

# backend/.env를 os.environ에 로드 (소셜 로그인 등 os.getenv 사용처용)
try:
    from dotenv import load_dotenv
    _backend_env = Path(__file__).resolve().parents[1] / ".env"
    if _backend_env.exists():
        load_dotenv(_backend_env)
except Exception:
    pass
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.core.database import async_engine, AsyncSessionLocal
from backend.app.core.redis import redis_client
from backend.app.core.logging import get_logger
from backend.app.core.logging_config import setup_logging
from backend.app.core.error_handler import register_exception_handlers
from backend.app.core.exception_handlers import (
    register_exception_handlers as register_domain_exception_handlers,
)
from backend.app.core.middleware import RequestLoggingMiddleware
from backend.app.core.security_headers import SecurityHeadersMiddleware
from backend.app.core.rate_limiter import RateLimitMiddleware
from backend.app.core.security_middleware import (
    IPWhitelistMiddleware,
    InternalAPIKeyMiddleware,
)
from backend.app.api.v1.auth_router import router as auth_v1_router
from backend.app.api.v1.social_auth_router import router as social_auth_v1_router
from backend.app.api.v1.accounts_router import router as accounts_v1_router
from backend.app.api.v1.user_settings_router import router as user_settings_v1_router
from backend.app.api.v1.strategy_cards_router import router as strategy_cards_v1_router
from backend.app.api.v1.admin_router import router as admin_v1_router
from backend.app.api.v1.llm_router import router as llm_v1_router
from backend.app.api.v1.dashboard_router import router as dashboard_v1_router
from backend.app.api.v1.portfolio_router import router as portfolio_v1_router
from backend.app.api.v1.market_router import router as market_v1_router
from backend.app.api.v1.trade_router import router as trade_router
from backend.app.api.v1.notification_router import router as notification_router
from backend.app.api.v1.settings_router import router as settings_router
from backend.app.api.v1.health_router import router as health_router
from backend.app.api.v4_signal_api import router as v4_signal_api_router
from backend.app.api.v4_position_api import router as v4_position_api_router
from backend.app.api.v4_alert_api import router as v4_alert_api_router
from backend.app.api.v4_backtest_api import router as v4_backtest_api_router
from backend.app.api.v4_desk_recommend import router as v4_desk_recommend_router
from backend.app.core.kis_rate_limiter import rate_limiter_manager
from backend.app.services.system.orchestrator import SystemOrchestrator  # Phase 3-A 신규
from backend.app.routers.system import router as system_router, set_orchestrator
from backend.app.routers import fund as fund_router
from backend.app.routers import execution as execution_router
from backend.app.routers import position as position_router
from backend.app.routers import regime as regime_router
from backend.app.routers import calendar as calendar_router
from backend.app.routers.universe import router as universe_router
from backend.app.routers.price import router as price_router
from backend.app.routers.brain import router as brain_router
from backend.app.routers.metrics import router as metrics_router
from backend.app.routers.strategy import router as strategy_router
from backend.app.routers.account_sync_router import router as account_sync_router
from backend.app.routers.monitoring_router import router as monitoring_router
from backend.app.routers.backtest_router import router as backtest_router
from backend.app.routers.report_router import router as report_router
from backend.app.routers.go100.portfolio_router import router as go100_portfolio_router  # Added by CUR-GO100-PHASE3C-PORTFOLIO-SERVICE
from backend.app.routers.go100.backtest_router import router as go100_backtest_router  # Added by CUR-GO100-PHASE4-BACKTEST
from backend.app.routers.go100.ai_router import router as go100_ai_router  # Added by CUR-GO100-PHASE5-BASE-UNDERSTAND-DESIGN
from backend.app.routers.go100.paper_trading_router import router as go100_paper_trading_router  # Added by CUR-GO100-BUNDLE2
from backend.app.routers.go100.risk_router import router as go100_risk_router  # Added by CUR-GO100-BUNDLE3
from backend.app.routers.go100.live_trading_router import router as go100_live_trading_router  # Added by CUR-GO100-BUNDLE3
from backend.app.routers.go100.scheduler_router import router as go100_scheduler_router  # Added by CUR-GO100-BUNDLE3
from backend.app.routers.go100.optimizer_router import router as go100_optimizer_router  # Added by CUR-GO100-BUNDLE4D
from backend.app.routers.go100.strategy_router import router as go100_strategy_router, store_router as go100_store_router  # CUR-GO100-FRONTEND-FIX2, 2026-02-21
from backend.app.routers import (
    v4_system,
    v4_trading,
    v4_backtest,
    v4_auth,
    v4_email,
    v4_ai_trading,
    v4_orders,
    v4_compat,
    v4_reports,
    v4_admin,
    v4_kis,
    v4_settings,
    v4_emergency,
    v4_liquidation,
    v4_notifications,
    v4_social_auth,
    v4_data_pipeline,
    v4_dashboard,
    v4_websocket,
    v4_chart,
)

logger = get_logger("main")


async def _session_cleanup_loop():
    """매시간 만료된 세션 정리 (CUR-K-INTEGRATE-v1)."""
    while True:
        try:
            await asyncio.sleep(3600)  # 1시간
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    text("DELETE FROM user_sessions WHERE expires_at < NOW()")
                )
                await db.commit()
                deleted = result.rowcount if hasattr(result, "rowcount") else 0
                if deleted and deleted > 0:
                    logger.info("Session cleanup: %d expired sessions removed", deleted)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("Session cleanup error: %s", e)
            await asyncio.sleep(60)  # 에러 시 1분 후 재시도


try:
    from backend.app.services.factory import ServiceFactory

    _factory = ServiceFactory(db_session_factory=AsyncSessionLocal)
    orchestrator = _factory.orchestrator
    logger.info("ServiceFactory 초기화 성공")
except Exception as e:
    logger.error("ServiceFactory 초기화 실패, 레거시 모드: %s", e)
    orchestrator = SystemOrchestrator(
        db_session_factory=AsyncSessionLocal,
        fund_pool=None,
        reservation_manager=None,
        regime_detector=None,
        calendar_service=None,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 리소스 관리"""
    setup_logging()
    logger.info(f"KIS AutoTrade V4.0 시작 (env={settings.app_env})")

    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL 연결 성공")
    except Exception as e:
        logger.error(f"PostgreSQL 연결 실패: {e}")

    try:
        await redis_client.ping()
        logger.info("Redis 연결 성공")
    except Exception as e:
        logger.error(f"Redis 연결 실패: {e}")

    set_orchestrator(orchestrator)
    regime_router.set_orchestrator(orchestrator)

    # Phase 4: Rate Limiter Manager 초기화 (CUR-R-RATE-INIT-POLICY-v1: graceful degradation)
    try:
        await rate_limiter_manager.initialize()
        await rate_limiter_manager.recalc_quotas("KIS")
        await rate_limiter_manager.recalc_quotas("KIWOOM")
        logger.info("✅ Rate Limiter Manager initialized")
    except Exception as e:
        logger.error("⚠️ Rate Limiter init failed: %s", e)
        logger.warning("Service continues WITHOUT per-account rate limiting")
        # graceful degradation: 서비스는 시작하되 rate limiting 비활성

    # Phase 4: Session cleanup 백그라운드 태스크
    cleanup_task = asyncio.create_task(_session_cleanup_loop())

    # ── Schedule Runner 시작 (CUR-SCHEDULED-RUNNER-v1) ──
    from backend.app.services.schedule_runner import create_schedule_runner
    runner = create_schedule_runner(session_factory=AsyncSessionLocal, redis_client=redis_client)
    await runner.start()
    app.state.schedule_runner = runner
    logger.info("ScheduleRunner started")

    # ── 계좌잔고 동기화 스케줄러 (CUR-ACCOUNT-SYNC-MANAGER-v1) ──
    from backend.app.services.account_sync_scheduler import start_account_sync_scheduler
    account_sync_task = start_account_sync_scheduler()
    app.state.account_sync_task = account_sync_task
    logger.info("AccountSyncScheduler started")

    # ── Phase 2 데이터 수집 스케줄러 (CUR-DATA-COLLECTOR-PHASE2-v1) ──
    from backend.app.services.phase2_data_scheduler import start_phase2_scheduler
    phase2_task = start_phase2_scheduler()
    app.state.phase2_data_task = phase2_task
    logger.info("Phase2DataScheduler started")

    # ── LLM Gateway (CUR-LLM-GATEWAY-CORE-v1) ──
    try:
        from backend.app.core.llm_gateway import LLMGateway
        gateway = LLMGateway.initialize(session_factory=AsyncSessionLocal)
        app.state.llm_gateway = gateway
        logger.info("LLMGateway 초기화 완료")
    except Exception as e:
        logger.warning("LLMGateway 초기화 실패 (graceful): %s", e)
        app.state.llm_gateway = None

    orch_task = None
    if settings.app_env != "development":
        orch_task = asyncio.create_task(orchestrator.start())
        logger.info("Orchestrator 백그라운드 시작")
    else:
        logger.info("개발 모드: Orchestrator 자동 시작 안 함 (/api/v4/system/status로 확인)")

    yield

    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
    acc_sync_task = getattr(app.state, "account_sync_task", None)
    if acc_sync_task:
        acc_sync_task.cancel()
        try:
            await acc_sync_task
        except asyncio.CancelledError:
            pass
    phase2_task = getattr(app.state, "phase2_data_task", None)
    if phase2_task:
        phase2_task.cancel()
        try:
            await phase2_task
        except asyncio.CancelledError:
            pass
    phase3_task = getattr(app.state, "phase3_data_task", None)
    if phase3_task:
        phase3_task.cancel()
        try:
            await phase3_task
        except asyncio.CancelledError:
            pass
    if orch_task:
        orchestrator.stop()
        orch_task.cancel()
        try:
            await orch_task
        except asyncio.CancelledError:
            pass
    # ── Schedule Runner 중지 (CUR-SCHEDULED-RUNNER-v1) ──
    if hasattr(app.state, "schedule_runner") and app.state.schedule_runner:
        await app.state.schedule_runner.stop()
        logger.info("ScheduleRunner stopped")
    logger.info("KIS AutoTrade V4.0 종료")
    await async_engine.dispose()
    await redis_client.close()


app = FastAPI(
    title="GO100 (고백) V4.1 API",
    description="KIS AutoTrade Multi-User/Multi-Account Trading Platform",
    version="4.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Auth", "description": "인증 및 토큰 관리"},
        {"name": "Accounts", "description": "계좌 CRUD 및 매수차단"},
        {"name": "Strategy Cards", "description": "전략 카드 CRUD 및 라이브 토글"},
        {"name": "Fund", "description": "자금 관리 및 DRY_RUN"},
        {"name": "Admin", "description": "관리자 전용 (PREMIUM)"},
        {"name": "LLM", "description": "AI 채팅 및 모델 관리"},
        {"name": "System", "description": "헬스체크 및 시스템 상태"},
    ],
    lifespan=lifespan,
)

# 순서: SecurityHeaders → RateLimit → RequestLogging → (앱 로직) → ErrorHandler
# (add_middleware는 역순 등록: 마지막이 가장 바깥에서 먼저 실행)
# V4.1 Multi-User Security: IP 화이트리스트 → Internal API Key (CUR-G-AUTH-v1)
app.add_middleware(InternalAPIKeyMiddleware)
app.add_middleware(IPWhitelistMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

register_exception_handlers(app)
register_domain_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://trading.newtalk.kr",
        "https://trading41.newtalk.kr",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
app.include_router(v4_signal_api_router)
app.include_router(v4_position_api_router)
app.include_router(v4_alert_api_router)
app.include_router(v4_backtest_api_router)
app.include_router(fund_router.router)
app.include_router(execution_router.router)
app.include_router(position_router.router)
app.include_router(regime_router.router)
app.include_router(calendar_router.router)
app.include_router(universe_router)
app.include_router(price_router)
app.include_router(brain_router)
app.include_router(metrics_router)
app.include_router(strategy_router)
app.include_router(v4_system.router, prefix="/api/v4")
app.include_router(v4_trading.router, prefix="/api/v4")
app.include_router(v4_backtest.router, prefix="/api/v4")
app.include_router(v4_auth.router, prefix="/api/v4")
app.include_router(v4_email.router, prefix="/api/v4")
app.include_router(v4_ai_trading.router, prefix="/api/v4")
app.include_router(v4_orders.router, prefix="/api/v4")
app.include_router(dashboard_v1_router, prefix="/api/v1/dashboard")
app.include_router(portfolio_v1_router, prefix="/api/v1")
app.include_router(market_v1_router, prefix="/api/v1")
app.include_router(trade_router, prefix="/api/v1/trade")
app.include_router(notification_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1/settings")
app.include_router(health_router)
app.include_router(monitoring_router)
app.include_router(v4_compat.router, prefix="/api/v1", tags=["legacy-compat"])
app.include_router(auth_v1_router, prefix="/api/v1")
app.include_router(social_auth_v1_router, prefix="/api/v1")
app.include_router(accounts_v1_router, prefix="/api/v1")
app.include_router(account_sync_router, prefix="/api/v1")
app.include_router(user_settings_v1_router, prefix="/api/v1")
app.include_router(strategy_cards_v1_router, prefix="/api/v1")
app.include_router(backtest_router, prefix="/api/v1")
app.include_router(report_router, prefix="/api/v1")
# Phase 4 Admin + LLM (CUR-K-INTEGRATE-v1)
app.include_router(admin_v1_router, prefix="/api/v1")
app.include_router(llm_v1_router, prefix="/api/v1")
app.include_router(v4_websocket.router)
app.include_router(v4_reports.router)
app.include_router(v4_admin.router)
app.include_router(v4_kis.router)
app.include_router(v4_settings.router)
app.include_router(v4_emergency.router)
app.include_router(v4_liquidation.router)
app.include_router(v4_notifications.router)
app.include_router(v4_social_auth.router)
app.include_router(v4_data_pipeline.router)
app.include_router(v4_dashboard.router)
app.include_router(v4_desk_recommend_router)
app.include_router(v4_chart.router, prefix="/api/v4")
# Added by CUR-GO100-PHASE3C-PORTFOLIO-SERVICE
app.include_router(go100_portfolio_router)
# CUR-GO100-FRONTEND-FIX2, 2026-02-21 — 대시보드/전략카드 404 해결
app.include_router(go100_strategy_router)
app.include_router(go100_store_router)
# Added by CUR-GO100-PHASE4-BACKTEST
app.include_router(go100_backtest_router)
# Added by CUR-GO100-PHASE5-BASE-UNDERSTAND-DESIGN
app.include_router(go100_ai_router)
# Added by CUR-GO100-BUNDLE2
app.include_router(go100_paper_trading_router)
# Added by CUR-GO100-BUNDLE3
app.include_router(go100_risk_router)
app.include_router(go100_live_trading_router)
app.include_router(go100_scheduler_router)
# Added by CUR-GO100-BUNDLE4D
app.include_router(go100_optimizer_router)

# V4 대시보드 정적 페이지 (CURSOR-EXEC-FRONTEND-V4-DASHBOARD-20260218)
_static_dir = Path(__file__).resolve().parent.parent / "static"
if _static_dir.is_dir():
    app.mount("/static/v4-dashboard", StaticFiles(directory=_static_dir / "v4-dashboard", html=True), name="v4-dashboard")

# [DASH-RESTORE 2026-02-22] 레거시 대시보드 복구를 위해 비활성화
# _dashboard_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dashboard"
# if _dashboard_dir.is_dir():
#     app.mount("/dashboard", StaticFiles(directory=str(_dashboard_dir), html=True), name="dashboard")


@app.get("/health", tags=["System"])
async def health_check():
    """시스템 상태 확인"""
    health = {
        "status": "ok",
        "version": "4.1.0",
        "orchestrator_state": orchestrator.state.value,
    }

    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health["database"] = "connected"
    except Exception:
        health["database"] = "disconnected"
        health["status"] = "degraded"

    try:
        await redis_client.ping()
        health["redis"] = "connected"
    except Exception:
        health["redis"] = "disconnected"
        health["status"] = "degraded"

    return health


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "KIS AutoTrade V4.0",
        "docs": "/docs",
        "health": "/health",
        "system_status": "/api/v4/system/status",
    }
