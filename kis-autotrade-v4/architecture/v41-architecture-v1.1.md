# KIS AutoTrade V4.1 — 시스템 아키텍처 문서

```
================================================================
KIS AutoTrade V4.1 자동매매 시스템
시스템 아키텍처 문서
================================================================
문서 버전: 1.1
작성일: 2026-02-21
작성자: Claude Code (자동 생성)
상태: 현행 운영 기준 (phase-2c-command-center 브랜치)
================================================================
```


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 서비스 개요
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

V4.1은 KIS(한국투자증권) API 기반의 한국 주식 자동매매 엔진이다.
4개의 DESK(전략 단위)가 독립적으로 운영되며, 각 DESK는 고유한
투자 스타일(데일리/스윙/중기/장기)에 맞는 전략 카드를 실행한다.

  프로젝트 경로: /root/kis-autotrade-v4
  운영 서버:     [SERVER-IP] (Ubuntu)
  코드 버전:     4.1.0 (backend/app/main.py)
  Git 태그:      v4.1.0-phase6-batch3
  브랜치:        phase-2c-command-center
  DB:            PostgreSQL 16 / kisautotrade


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. 시스템 전체 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────┐
│                   외부 데이터 소스                            │
│  KIS API (실시간 시세, 주문, 계좌)  pykrx (일봉)            │
│  한국거래소 (업종/종목)             기재부 (공휴일 캘린더)    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              데이터 수집 파이프라인 (크론/타이머)              │
│                                                             │
│  [일봉]       ohlcv_daily 수집 (18:00 크론)                 │
│  [분봉]       v4_ohlcv_minute 수집 (kis-v41-minute-col.)    │
│  [투자자]     v4_investor_daily 수집 (MKTINV 크론)          │
│  [업종]       stock_universe + sector 수집 (SECIND 크론)    │
│  [지수]       index_daily / v4_vkospi_daily 수집            │
│  [재무]       stock_fundamentals 수집                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL kisautotrade                     │
│              (100+ 테이블, v4_* + go100_* + 레거시)          │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼────────────────┐
         ▼               ▼                ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ 스케줄러     │  │ 오케스트레이터│  │ 모니터        │
│ (Scheduler) │  │ (V4Pipeline) │  │ (Monitor)    │
│ kis-v41-    │  │ 전략 신호생성 │  │ 포지션 감시   │
│ scheduler   │  │ → 주문 실행   │  │ 리스크 체크  │
└─────────────┘  └──────────────┘  └──────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. DESK 구조 (전략 단위)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────┐
│                    전략 카드 (strategy_cards)              │
│                    Owner: kis_admin / 59건                │
├───────────┬───────────┬───────────┬───────────────────────┤
│  DESK2    │  DESK3    │  DESK4    │  DESK5                │
│ (데일리)  │ (스윙)    │ (중기)    │ (장기)                │
│ 1~5일     │ 5~20일    │ 20~60일   │ 60일+                 │
├───────────┴───────────┴───────────┴───────────────────────┤
│  DESK1 (스캘핑) — 분봉 기반, 구현 예정                    │
└──────────────────────────────────────────────────────────┘

전략 카드 스키마 핵심 필드:
  card_id          — PK (bigint)
  user_id          — v4_users FK
  account_id       — accounts FK (AES-256 암호화 KIS 키 포함)
  strategy_type    — BUILTIN / CUSTOM
  strategy_params  — jsonb (전략별 파라미터)
  entry_rules      — jsonb (진입 조건)
  exit_rules       — jsonb (청산 조건)
  risk_params      — jsonb (리스크 파라미터)
  buy_phases       — jsonb (매수 단계)
  sell_phases      — jsonb (매도 단계)
  promotion_rules  — jsonb (상위 DESK 승격 조건)
  demotion_rules   — jsonb (하위 DESK 강등 조건)
  is_live          — 실행 중 여부
  is_active        — 활성 여부
  desk_id          — DESK 번호 (DESK2~5)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. 매매 실행 흐름
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[일봉 기반 매매]
  V4PipelineOrchestrator
  → 활성 전략 카드 조회 (is_live=true)
  → IndicatorCalculator (SMA, EMA, RSI, MACD, BB, ATR 등)
  → SignalGenerator (entry_rules 해석 → buy/sell 시그널)
  → v4_signals 저장
  → V4OrderExecutor
    → KIS REST API (주문 요청)
    → 체결 확인 → v4_trades 저장
  → PositionManager
    → v4_positions 업데이트
    → 리스크 한도 체크 (max_position, daily_loss_limit)
  → AccountSyncManager
    → v4_account_holdings 동기화

[리스크 관리]
  RiskManager
  → 포지션별 손절 트리거 (stop_loss_pct)
  → 트레일링 스탑 (trailing_stop_pct)
  → 일일 손실 한도 초과 시 긴급 정지
  → DESK별 자금 한도 관리 (v4_desk_fund)

[긴급 청산]
  /api/v4/emergency — stop-all, close-all
  LiquidationService → 전체 포지션 즉시 청산


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. 데이터베이스 (V4.1 전용 테이블)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[시장 데이터]
  stock_universe (3,844건)
    — 종목 마스터 (code, name, market, sector)
    — sector_large / sector_mid / sector_small (SECIND-V2 추가, 2026-02-21)
  ohlcv_daily                    — 일봉 (varchar YYYYMMDD, 전종목)
  v4_ohlcv_minute (파티션 테이블) — 분봉 (월별 파티션)
    v4_ohlcv_minute_2025_01 ~ 2026_03 (368만 건)
  v4_investor_daily (16만건)      — 투자자별 매매동향 (외인/기관/개인)
  v4_stock_sector (4,225건)       — 종목-업종 매핑
  v4_vkospi_daily (489건)         — VKOSPI 변동성 지수
  index_daily                     — 코스피/코스닥 일봉

[사용자/계좌]
  v4_users (4건)                  — 사용자 마스터 (tier: FREE/PRO/PREMIUM)
  accounts                        — 증권 계좌 (KIS/키움, 실전/모의, AES-256 암호화)
  account_rate_quotas             — 계좌별 API Rate Limit 할당
  user_sessions                   — JWT refresh token
  v4_account_holdings (1,351건)   — 계좌 보유종목 스냅샷
  v4_account_sync_log             — 계좌 동기화 이력
  v4_account_config               — 계좌 설정

[전략/트레이딩]
  strategy_cards (59건)           — V4.1 전략 카드 (Owner: kis_admin)
  v4_desk_strategy_mapping        — DESK-전략 매핑
  v4_positions                    — 실시간 포지션
  v4_trades                       — 체결 내역
  v4_desk_fund                    — DESK별 자금 배분
  v4_signals                      — 매매 시그널 이력
  v4_orders                       — 주문 이력

[백테스트]
  v4_backtest_runs                — 백테스트 실행 (strategy_card_id FK)
  v4_backtest_sessions            — 세션 기반 백테스트 (V4.1 방식)
  v4_backtest_daily               — 일별 백테스트 결과
  v4_backtest_trades              — 백테스트 가상 거래 내역

[시스템]
  v4_alerts                       — 알림
  v4_notifications                — 알림 상세
  v4_reports                      — 자동 리포트
  v4_api_error_log                — API 오류 로그
  v4_api_tokens                   — KIS API 토큰 캐시
  v4_market_regime_daily          — 시장 레짐 (bull/bear/sideways)
  v4_market_calendar              — 개장일 캘린더
  llm_requests / llm_cost_daily   — LLM 사용량/비용

[레거시 (DROP 예정)]
  _legacy_daily_investor_stats_20260220
  _legacy_market_data_min_20260220   (1.5GB)
  _legacy_ohlcv_1m_history_20260220  (1.75GB)
  ohlcv_1m                           (v4_ohlcv_minute로 통일)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. 백테스트 엔진 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[경로1] 기존 방식 (entry_rules 없는 카드)
  backtest_router.py → run_backtest()
  → backtest_engine.py
  → strategy_simulator.run_single_stock_simulation()
  → strategy_type + strategy_params 기반
  → 일봉 (ohlcv_daily) 사용

[경로2] 카드 규칙 방식 (entry_rules 있는 카드)
  backtest_router.py → CardRuleSimulator
  → EntryConditionEvaluator (SMA, EMA, RSI, MACD, BB 등)
  → entry_rules.indicators + min_conditions 해석
  → exit_rules (stop_loss, trailing_stop, max_hold_days)
  → risk_params (max_positions, daily_loss_limit)
  → 일봉 (ohlcv_daily) 사용

[경로3] V4.1 확장 엔진
  v4_backtest_api.py → BacktestEngineV2
  → sessions 기반, 멀티데스크 지원
  → 분봉 지원 (v4_ohlcv_minute, use_minute_data=True)

[데이터 소스]
  일봉: ohlcv_daily (varchar YYYYMMDD, 3,844종목, 20240213~현재)
  분봉: v4_ohlcv_minute (파티션, date+time 타입, backtest_provider 참조)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. systemd 서비스
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 서비스                       | 상태       | 역할                          |
|------------------------------|------------|-------------------------------|
| kis-v41-scheduler            | active     | 매매 스케줄 실행               |
| kis-v41-monitor              | active     | 포지션 모니터링                |
| kis-v41-position-monitor     | active     | 포지션 리스크 모니터링         |
| kis-v41-minute-collector     | active     | 분봉 OHLCV 실시간 수집         |
| kis-v41-api                  | inactive   | V4.1 독립 API (포트 충돌로 중단)|
| kis-v41-webapp               | inactive   — 미사용               |

※ go100.service(포트 8002)가 운영 중이므로 kis-v41-api는 중지 유지


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. 크론 / 타이머 스케줄
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[데이터 수집]
  18:00   — ohlcv_daily 수집 (전종목 일봉)
  16:00   — 분봉 배치 수집
  토 02:00 — 주간 분봉 보완 수집
  17:30   — stock_universe 종목 마스터 갱신
  주 1회   — sector 업종 수집 (collect_stock_industry.py)
  MKTINV  — v4_investor_daily 투자자 동향 수집
  18:30   — VKOSPI 수집

[운영]
  03:00   — DB 백업
  6h      — 디스크 사용량 모니터링
  5min    — 장중 알림 체크
  30min   — 장외 알림 체크
  14:30   — KIS API 토큰 갱신

[정리]
  일요일 04:00 — 레거시 테이블 DROP (예정)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. API 엔드포인트 (V4.1 전용)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

■ /api/v4/* (V4.1 네이티브, prefix="/api/v4")
  /system        — status, health, market-regime, calendar
  /trading       — positions, fund-pool, strategies, desk-cycles
  /backtest      — sessions, compare, run, progress, config-options
  /dashboard     — system, trading, overview, desks, signals
  /chart         — stocks, daily/weekly/minute/index/investor/indicators
  /orders        — create, cancel, pending
  /emergency     — stop-all, stop-user, resume, close-all
  /liquidation   — execute, status, release-buy-block
  /ai-trading    — status, start, stop, recommendations
  /admin         — users, stats, maintenance, trades
  /auth          — login, refresh, me, verify, signup
  /kis           — accounts, token-status, token-refresh, config
  /settings      — trading, notification, strategy
  /data-pipeline — pipeline/ohlcv/investor/collection status
  /reports       — daily/weekly/monthly, trade-history
  /notifications — test, stats, channels
  /social-auth   — providers, url, callback
  /ws/live-trade — WebSocket 실시간 매매
  /ws/ticks      — WebSocket 시세


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10. 핵심 서비스 모듈 (backend/app/services/)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

services/
├── backtest/
│   ├── backtest_engine.py         # 경로1: 기본 엔진
│   ├── backtest_engine_v2.py      # 확장 엔진 (분봉/멀티데스크) ← 수정 금지
│   ├── card_rule_simulator.py     # 경로2: 카드 규칙 기반
│   ├── strategy_simulator.py      # 전략 시뮬레이터
│   ├── performance_calculator.py  # 성과 지표 (수익률, MDD, 샤프)
│   └── virtual_executor.py        # 가상 주문 실행
├── trading/                       # 실매매 엔진
├── execution/                     # 주문 실행 (V4OrderExecutor)
├── orchestrator/                  # V4PipelineOrchestrator ← 수정 금지
├── strategy/                      # 전략 관리, 시그널 생성
│   └── strategies/                # DESK별 전략 구현체
├── position/                      # 포지션 관리
├── risk/                          # 리스크 관리
├── data_pipeline/                 # 데이터 수집 파이프라인
├── collectors/                    # 종목 수집기
├── indicators/                    # 기술 지표 계산 (INDICATOR_MAP 50종+)
├── adaptive/                      # 적응형 리밸런싱, 파라미터 최적화
├── monitoring/                    # 시스템 모니터링
├── notification/                  # Telegram/Slack/Email 알림
├── report/                        # 리포트 생성
├── market/                        # 시세/업종/테마
├── market_brain/                  # 시장 분석 브레인
├── brain/                         # 전략 브레인
├── sync/                          # 계좌 동기화
├── system/                        # 시스템 상태
├── auth/                          # OAuth 서비스
├── llm/                           # LLM Gateway 서비스
│   └── llm_gateway.py             # Singleton ← 수정 금지
├── data/                          # 데이터 제공 (backtest_provider)
└── strategy_card_service.py       # 전략카드 CRUD ← 수정 금지


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
11. 인프라 / 배포
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

서버: [SERVER-IP] (Ubuntu, 99GB 디스크 / 51GB 사용)
Nginx: 리버스 프록시
  /api/v4/* → 8002 (go100.service)
  /api/*    → 8001 (레거시 webapp)
  /ws/*     → 8002 (WebSocket)
  SSL: trading41.newtalk.kr (Let's Encrypt)
       trading.newtalk.kr (미발급, Cloudflare 프록시 경유)

PostgreSQL: 16, kisautotrade DB
Redis:      db 0 (토큰/세션/캐시)
venv:       /root/kis-autotrade-v4/venv (go100.service 사용)
            /root/kis-autotrade-v4/.venv (개발용)

외부 API:
  KIS API    — 실시간 시세, 주문, 계좌 조회
  pykrx      — 일봉 OHLCV 보완
  Gemini     — LLM (FREE_CHAT, REPLY)
  Anthropic  — LLM (DESIGN_CHAT)
  OpenAI     — LLM (C2SC 변환)
  SMTP       — 이메일 알림


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12. 멀티유저 / 계좌 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

v4_users (4건, tier: FREE/PRO/PREMIUM)
  │
  ├── accounts (1:N, KIS/키움, 실전/모의)
  │     — API 키 AES-256 암호화 (pgcrypto)
  │     │
  │     ├── strategy_cards (1:N, 59건)
  │     │     ├── v4_positions
  │     │     ├── v4_trades
  │     │     └── v4_desk_fund
  │     │
  │     └── account_rate_quotas (Fair-share Rate Limit)
  │           — KIS 20rps / 활성 계좌 수로 분배
  │
  └── user_sessions (JWT refresh token, 7일)

인증 흐름:
  JWT Access Token (15분) + Refresh Token (7일, DB 저장)
  소셜 로그인: Google/Kakao OAuth

티어별 제한 (Phase 2 구현 예정):
  FREE    — 1계좌, 1전략, 모의만
  PRO     — 3계좌, 5전략, 실전 가능
  PREMIUM — 무제한


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
13. 환경변수 카테고리 (.env)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[앱]       APP_NAME, APP_ENV, APP_DEBUG, APP_HOST, APP_PORT, TZ
[DB]       DATABASE_URL, DATABASE_URL_SYNC, DB_HOST/NAME/USER/PASSWORD/PORT
[Redis]    REDIS_URL, REDIS_HOST, REDIS_PORT, REDIS_DB
[JWT]      JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS/REFRESH_EXPIRE
[암호화]   ENCRYPTION_KEY, SECRET_KEY
[KIS]      KIS_APP_KEY/SECRET, KIS_REAL_*/VIRTUAL_*, KIS_ACCOUNT_*, KIS_BASE_URL
[키움]     KIWOOM_APP_KEY/SECRET_KEY, KIWOOM_IS_PRODUCTION
[Rate]     RATE_LIMIT_*, TOTAL_KIS_RPS, TOTAL_KIWOOM_RPS, MIN_ACCOUNT_RPS
[LLM]      GOOGLE_AI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY
           LLM_FREE_CHAT/DESIGN_CHAT/CS/STRATEGY_REVIEW_MODEL
           LLM_MONTHLY_BUDGET_USD, LLM_GLOBAL_ENABLED
[이메일]   SMTP_*
[트레이딩] DRY_RUN, TRADING_CONFIG_ID, MOCK_CONFIG_ID, KIS_ACCOUNT_MODE
[보안]     ALLOWED_IPS, TRUSTED_PROXY_IPS, INTERNAL_API_KEY


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
14. 알려진 이슈 및 기술 부채
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[P0 해결됨]
  ✅ 백테스트 500 에러 — asyncpg date 바인딩 + YYYYMMDD 수정
  ✅ KIS API 토큰 선제 갱신 — 만료 전 자동 재발급

[P1 현재]
  ⚠ sector_large 품질 — KIS API가 업종명 대신 시가총액규모 반환 혼재
  ⚠ rank_market_cap — stock_universe 전체 NULL (폴백 로직 작동 중)
  ⚠ trading.newtalk.kr SSL 미발급 — Cloudflare 프록시로 우회 중

[P2 대기]
  - 분봉 백테스트 미구현 (DESK1 스캘핑 카드 대기)
  - 레거시 테이블 3.2GB DROP 예정 (일요일 크론 미등록)
  - users vs v4_users 이중 구조 통합 필요
  - v1 backtest_router + v4 backtest_api 이중 구조 병존
  - venv vs .venv 이중 가상환경 (go100.service는 venv 사용)
  - 리포트 자동생성 크론 미등록 (코드 준비 완료)

[P3 향후]
  - 68서버 → 211서버 통폐합 (trading.newtalk.kr 이전, 보류 중)
  - 모바일 PWA 최적화
  - 구독 과금 시스템 (티어별 제한 스키마만 준비)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
15. 문서 변경 이력
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 버전 | 날짜       | 변경 내용                                                        |
|------|------------|------------------------------------------------------------------|
| 1.0  | 2026-02-20 | 초판 작성 (architecture-v1.0.md에 통합 형태로 포함)              |
| 1.1  | 2026-02-21 | V4.1 전용 문서로 분리. SECIND-V2 업종 3단계 컬럼 추가 반영.      |
|      |            | strategy_cards 59건 확인. DB 분리 완료 확인. 서비스 상태 갱신.   |

================================================================
문서 끝 (v41-architecture-v1.1.md)
================================================================
