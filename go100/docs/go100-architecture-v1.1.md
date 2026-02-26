# GO100 AI 전략 플랫폼 — 시스템 아키텍처 문서

```
================================================================
GO100 AI 전략 플랫폼 (백억이)
시스템 아키텍처 문서
================================================================
문서 버전: 1.1
작성일: 2026-02-21
작성자: Claude Code (자동 생성)
상태: Phase 5 완료 기준 (phase-2c-command-center 브랜치)
================================================================
```


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 서비스 개요
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GO100은 AI 채팅 기반 전략 설계 → 백테스트 검증 → 실매매 실행을
하나의 플랫폼에서 제공하는 한국 주식 자동매매 SaaS 시스템이다.
사용자는 "백억이" AI와 자연어 대화로 투자 전략을 설계하고,
백테스트 결과를 확인한 뒤 실매매에 투입한다.

  서비스명:      GO100 (백억이 AI)
  도메인:        https://go100.newtalk.kr
  프로젝트 경로: /root/kis-autotrade-v4
  운영 서버:     211.188.51.113 (Ubuntu)
  브랜치:        phase-2c-command-center
  현재 Phase:    5 완료 (UNDERSTAND+DESIGN 에이전트)
  다음 Phase:    6 (EVALUATE+OPTIMIZE 루프)

V4.1 자동매매 시스템과 동일 코드베이스에 공존하며,
V4.1 인프라(DB, KIS API, LLM Gateway)를 읽기 전용으로 참조하고,
go100_* 전용 테이블에서 독립적으로 운영된다.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. 시스템 전체 아키텍처
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────────┐
│                   사용자 (브라우저/모바일)                     │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTPS
                          ▼
┌──────────────────────────────────────────────────────────────┐
│          Nginx Reverse Proxy / go100.newtalk.kr              │
│          SSL Termination (Let's Encrypt)                     │
└──────────┬───────────────────────────┬───────────────────────┘
           │ :3000                     │ :8002
           ▼                           ▼
┌────────────────────┐   ┌─────────────────────────────────────┐
│  Frontend           │   │      Backend (FastAPI / uvicorn)     │
│  Next.js 14         │   │      Python 3.11+ / Port 8002       │
│  TypeScript         │   │      go100.service (systemd)        │
│  pnpm / Port 3000   │   │                                     │
│  go100-frontend     │   │  ┌───────────────────────────────┐  │
│  .service (systemd) │   │  │ API Layer                     │  │
│                     │   │  │ /api/go100/* (GO100 전용)     │  │
│  /src/app/          │   │  │ /api/v1/*   (공통 서비스)     │  │
│  /src/go100/        │   │  │ /api/v4/*   (V4.1 호환)      │  │
│  (GO100 전용 모듈)  │   │  └───────────────────────────────┘  │
└────────────────────┘   │  ┌───────────────────────────────┐  │
                         │  │ GO100 Service Layer           │  │
                         │  │ ─ AI 에이전트 (UNDERSTAND,   │  │
                         │  │   DESIGN)                    │  │
                         │  │ ─ UniverseEngine (7 필터)    │  │
                         │  │ ─ BacktestService            │  │
                         │  │ ─ StrategyCardService        │  │
                         │  │ ─ PortfolioService           │  │
                         │  └───────────────────────────────┘  │
                         │  ┌───────────────────────────────┐  │
                         │  │ V4.1 공유 인프라 (읽기 전용)  │  │
                         │  │ ─ LLMGateway (Singleton)     │  │
                         │  │ ─ KIS API 브로커             │  │
                         │  │ ─ stock_universe (시장 데이터)│  │
                         │  │ ─ ohlcv_daily / v4_ohlcv_min │  │
                         │  └───────────────────────────────┘  │
                         └──────────┬──────────────────────────┘
                                    │
                    ┌───────────────┼──────────────┐
                    ▼               ▼              ▼
             ┌──────────┐   ┌──────────┐   ┌────────────┐
             │PostgreSQL │   │  Redis   │   │External API│
             │go100_*    │   │ 캐시/세션 │   │Gemini      │
             │7 테이블   │   │          │   │Anthropic   │
             └──────────┘   └──────────┘   │OpenAI      │
                                           └────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. 사용자 여정 (User Journey)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[A] 가입 → 계좌 연결
    이메일/소셜 가입 → v4_users 생성 (tier: FREE/PRO/PREMIUM)
    → 증권 계좌 등록 (KIS API 키 AES-256 암호화 저장)
    → Rate Quota 자동 할당

[B] AI 채팅 전략 설계 (백억이)
    자유 대화 (Gemini Flash)
    → 투자 개념 교육, 질문 응답
    → 사용자 의향 감지 시 전략 설계 모드 전환

    UNDERSTAND 에이전트 ✅ Phase 5 완료
    → 자연어에서 투자 의향(UserIntent) 12개 필드 추출
    → confidence < 0.6 → 추가 질문 요청

    DESIGN 에이전트 ✅ Phase 5 완료
    → UserIntent → 전략 카드(StrategyDesign) 설계
    → universe_filter + entry_rules + exit_rules + risk_params
    → 안전성 규칙 강제 (stop_loss 필수, max_stocks 3~10 등)

    EVALUATE 에이전트 ❌ Phase 6 예정
    → 백테스트 결과 AI 성과 평가

    OPTIMIZE 에이전트 ❌ Phase 6 예정
    → 자율 개선 루프 (최대 5회 반복)

[C] 백테스트 검증 ✅ Phase 4 완료
    UniverseEngine → 조건 충족 종목 필터링
    → BacktestSimulator → 전략 시뮬레이션
    → 수익률, MDD, 샤프 지수, 승률 계산
    → go100_backtest_runs 저장
    → go100_strategy_cards.last_backtest_* 업데이트

[D] Paper Trading ❌ Phase 7 예정
    card_status: BACKTESTED → PAPER_LIVE
    → 모의 실행 (실제 주문 없음)

[E] 실매매 ❌ Phase 8 예정
    card_status: PAPER_LIVE → LIVE
    → KIS API 실제 주문 실행

[F] 전략 진화 ❌ Phase 10 예정
    주간 자동 재평가 → 사용자 승인 → 파라미터 갱신


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. AI 에이전트 상세 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[LLM 클라이언트 (llm_client.py)]
  기존 LLMGateway Singleton 래핑
  UNDERSTAND → RequestType.FREE_CHAT  → Gemini 2.0 Flash
  DESIGN     → RequestType.DESIGN_CHAT → Claude Sonnet 4.6
  REPLY      → RequestType.FREE_CHAT  → Gemini 2.0 Flash

[UnderstandAgent (understand_agent.py)]
  입력: user_message + conversation_history
  출력: UserIntent (12개 필드)
    investment_style    — scalping/day_trading/swing/position/long_term_value/dividend
    risk_tolerance      — very_low/low/moderate/high/very_high
    target_sectors      — 목표 섹터 목록
    target_keywords     — 키워드 (예: "골든크로스", "존버")
    target_return       — 목표 수익률 (%)
    holding_period      — 보유 기간 (일)
    capital_hint        — 예상 투자금
    dividend_preference — 배당 선호 여부
    specific_conditions — 특수 조건 (골든크로스 등)
    exclude_conditions  — 제외 조건
    experience_level    — beginner/intermediate/advanced
    confidence          — 신뢰도 0.0~1.0
    needs_clarification — 추가 질문 필요 여부
    clarification_questions — 질문 목록

  검증 로직:
    confidence < 0.6 → needs_clarification = True
    unknown 필드 3개+ → needs_clarification = True

[DesignAgent (design_agent.py)]
  입력: UserIntent + user_message
  출력: StrategyDesign
    universe_filter — UniverseEngine 필터 표현식 (jsonb)
    entry_rules     — 진입 조건 목록
    exit_rules      — 청산 조건 (stop_loss 필수)
    risk_params     — 리스크 파라미터
    strategy_params — 전략 파라미터

  안전성 규칙 (_apply_safety_rules):
    stop_loss 없으면 강제 추가 (스타일별 기본값)
    max_stocks < 1 → 3, > 10 → 10
    max_position_pct > 30 → 30
    experience_level == beginner → market_cap rank 100 이하 강제

  스타일별 기본값 (_get_defaults_by_style):
    scalping:         stop_loss 2%, max_stocks 5, holding 1일
    day_trading:      stop_loss 3%, max_stocks 5, holding 1일
    swing:            stop_loss 5%, max_stocks 5, holding 20일
    position:         stop_loss 8%, max_stocks 5, holding 60일
    long_term_value:  stop_loss 10%, max_stocks 5, holding 180일
    dividend:         stop_loss 10%, max_stocks 10, 배당 우선

[BaseOrchestrator (base_orchestrator.py)]
  흐름:
    1. UnderstandAgent.analyze() → UserIntent
    2. needs_clarification → REPLY (추가 질문)
    3. DesignAgent.design() → StrategyDesign
    4. REPLY (전략 카드 설명)
    5. go100_strategy_cards DB 저장 (Phase 6에서 활성화 예정)
    6. BaseAgentResponse 반환

[API 엔드포인트 (ai_router.py)]
  POST /api/go100/ai/chat        — 백억이 대화 (JWT 필수)
  POST /api/go100/ai/understand  — UNDERSTAND 단독 테스트
  POST /api/go100/ai/design      — DESIGN 단독 테스트


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. UniverseEngine 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[현재 구현: 7개 필터 + AND/OR/NOT 논리 표현식] ✅ Phase 2 완료

┌─────────────────────────────────────────────────────────┐
│                  UniverseEngine                          │
│           engine.py + expression_parser.py              │
├─────────────────────────────────────────────────────────┤
│  논리 연산자                                              │
│    AND  — type:"AND", conditions:[...]                   │
│    OR   — type:"OR",  conditions:[...]                   │
│    NOT  — type:"NOT", condition:{...}                    │
├─────────────────────────────────────────────────────────┤
│  리프 필터 (7개)                                         │
│    scope       — market(KOSPI/KOSDAQ), sectors,          │
│                  exclude_etf, exclude_codes              │
│    price       — min/max 가격 범위                       │
│    volume      — min/max 거래량                          │
│    market_cap  — min/max 시가총액, rank (rank_market_cap)│
│    ma          — SMA/EMA 기간, 조건(above/below/cross)  │
│    rsi         — 기간, min/max 범위                      │
│    fundamental — per_max, pbr_max, roe_min, debt_max    │
└─────────────────────────────────────────────────────────┘

[v2.1 기획 확장 예정: +14개 필터] ❌ Phase 9
  bollinger, macd, stochastic, cci, dmi, obv,
  ichimoku, pivot, sar, williams,
  candle_pattern, gap, trend, investor_flow

[데이터 캐시 (data_cache.py)]
  DataCache — 동일 실행 내 쿼리 중복 방지
  stock_universe, ohlcv_daily, stock_fundamentals 참조

[입력 형식 예시]
  {
    "type": "AND",
    "conditions": [
      {"type": "scope",      "params": {"market": "KOSPI"}},
      {"type": "price",      "params": {"min": 5000, "max": 100000}},
      {"type": "market_cap", "params": {"min": 300000000000}},
      {"type": "ma",         "params": {"period": 20, "condition": "above"}},
      {"type": "rsi",        "params": {"period": 14, "min": 30, "max": 70}}
    ]
  }


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. 전략 카드 라이프사이클
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌───────┐    ┌───────┐    ┌────────────┐    ┌────────────┐
│ IDEA  │───▶│ DRAFT │───▶│ BACKTESTED │───▶│ PAPER_LIVE │
└───────┘    └───────┘    └────────────┘    └────────────┘
                                                   │
                              ┌────────────┐       │
                              │   PAUSED   │◀──────▼──────▶┌──────┐
                              └────────────┘               │ LIVE │
                                    │                      └──────┘
                                    ▼                          │
                              ┌──────────┐                     │
                              │ RETIRED  │◀────────────────────┘
                              └──────────┘

상태 전환 규칙 (go100_strategy_cards.card_status):
  IDEA        — AI 대화 중, 전략 미확정
  DRAFT       — 전략 설계 완료, 백테스트 미실행
  BACKTESTED  — 백테스트 완료 (last_backtest_* 필드 업데이트)
  PAPER_LIVE  — 모의 실행 중 (Phase 7 구현 예정)
  LIVE        — 실매매 실행 중 (Phase 8 구현 예정)
  PAUSED      — 일시 정지
  RETIRED     — 폐기

카드 출처 (source_type):
  CUSTOM        — 사용자 직접 생성
  LLM           — 백억이 AI 생성
  SYSTEM        — 시스템 제공 기본 전략
  SHARED        — 스토어에서 복사


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. 데이터베이스 (GO100 전용 테이블)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DB: PostgreSQL kisautotrade / public 스키마
Owner: postgres (V4.1 kis_admin 과 명확히 구분)
Migration: backend/migrations/020_go100_tables.sql

[7개 전용 테이블]

■ go100_strategy_cards (핵심)
    go100_card_id       — PK (bigint, sequences)
    user_id             — v4_users FK
    account_id          — accounts FK (nullable)
    strategy_name       — varchar(200)
    strategy_type       — CUSTOM/BUILTIN/LLM_GENERATED/SUBSCRIBED
    universe_filter     — jsonb (UniverseEngine 필터 표현식)
    entry_rules         — jsonb 배열
    exit_rules          — jsonb 배열
    risk_params         — jsonb
    strategy_params     — jsonb
    card_status         — IDEA/DRAFT/BACKTESTED/PAPER_LIVE/LIVE/PAUSED/RETIRED
    source_type         — SYSTEM/CUSTOM/LLM/SHARED
    llm_session_id      — AI 대화 세션 ID
    last_backtest_id    — go100_backtest_runs FK
    last_backtest_return / mdd / sharpe — 최근 백테스트 요약
    paper_total_return / paper_start_date / paper_days — 페이퍼 성과
    dedicated_account   — 전용 계좌 여부
    disclaimer_agreed   — 투자 위험 동의

■ go100_backtest_runs
    go100_card_id FK, 실행 일시, 기간, 수익률, MDD, 샤프, 거래 수

■ go100_portfolios
    go100_card_id FK, 배분 금액, 상태, 실적

■ go100_positions
    포지션 (종목코드, 보유수량, 평균단가, 평가손익)

■ go100_orders
    주문 이력 (종목코드, 수량, 가격, 상태)

■ go100_trades
    체결 내역 (종목코드, 체결수량, 체결가격, 수익률)

■ go100_account_reconciliation
    계좌 정산 이력

[V4.1 공유 테이블 (읽기 전용)]
  stock_universe        — 종목 마스터 (sector_large/mid/small 포함)
  ohlcv_daily           — 일봉 백테스트용
  v4_ohlcv_minute       — 분봉 백테스트용
  stock_fundamentals    — PER/PBR/ROE/부채비율
  v4_investor_daily     — 투자자 수급 (Sector Rotation 예정)
  v4_market_regime_daily — 시장 레짐 (Market Regime 예정)

[분리 현황 확인 — 2026-02-21]
  ✅ V4.1 strategy_cards (59건, kis_admin) ↔ go100_strategy_cards 완전 분리
  ✅ 크로스 FK 없음 (v4_users를 공통 FK로만 사용)
  ✅ 서비스 레이어 독립 (card_service.py는 go100_strategy_cards만 접근)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. 백엔드 서비스 모듈 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

backend/app/services/go100/
├── ai/
│   ├── schemas.py           # UserIntent, StrategyDesign, BaseAgentResponse
│   ├── prompts.py           # UNDERSTAND/DESIGN/REPLY 프롬프트 + UNIVERSE_FILTER_SPEC
│   ├── llm_client.py        # LLMGateway 래퍼 (UNDERSTAND/DESIGN/REPLY 라우팅)
│   ├── understand_agent.py  # UNDERSTAND 에이전트 (12-field 의향 추출)
│   ├── design_agent.py      # DESIGN 에이전트 (전략 설계 + 안전성 규칙)
│   └── base_orchestrator.py # UNDERSTAND→DESIGN 파이프라인
│
├── universe/
│   ├── engine.py            # UniverseEngine 진입점
│   ├── expression_parser.py # AND/OR/NOT 논리 표현식 파서
│   ├── base_filter.py       # BaseFilter 추상 클래스
│   ├── data_cache.py        # 쿼리 캐시 (실행 단위)
│   ├── scope_filter.py      # 시장/섹터/ETF 제외
│   ├── price_filter.py      # 가격 범위
│   ├── volume_filter.py     # 거래량 범위
│   ├── market_cap_filter.py # 시가총액/순위
│   ├── ma_filter.py         # 이동평균 (SMA/EMA)
│   ├── rsi_filter.py        # RSI
│   └── fundamental_filter.py # PER/PBR/ROE/부채비율
│
├── backtest/
│   ├── schemas.py           # BacktestRequest, BacktestResult
│   ├── data_loader.py       # ohlcv_daily + v4_ohlcv_minute 로드
│   ├── signal_evaluator.py  # entry_rules 시그널 평가
│   ├── simulator.py         # 전략 시뮬레이션 (UniverseEngine 연동)
│   └── backtest_service.py  # 백테스트 실행 오케스트레이터
│
├── strategy/
│   ├── schemas.py           # StrategyCard 스키마
│   └── card_service.py      # go100_strategy_cards CRUD (raw SQL)
│
└── portfolio/
    ├── schemas.py           # Portfolio 스키마
    └── portfolio_service.py # go100_portfolios CRUD + 포지션 조회

backend/app/routers/go100/
├── ai_router.py             # /api/go100/ai/chat, /understand, /design
├── backtest_router.py       # /api/go100/backtest/*
├── strategy_router.py       # /api/go100/strategies/*
└── portfolio_router.py      # /api/go100/portfolios/*


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. 프론트엔드 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

frontend/src/
├── app/
│   ├── auth/                — 로그인/회원가입/소셜/비밀번호
│   ├── (protected)/
│   │   ├── dashboard/       — 대시보드 (포트폴리오 요약 위젯)
│   │   ├── portfolio/       — 포트폴리오 (보유/성과)
│   │   ├── accounts/        — 계좌 관리 (CRUD)
│   │   ├── trade/           — 자동매매 (실행/스케줄)
│   │   ├── backtest/        — 백테스트 (실행/결과)
│   │   ├── strategy-cards/  — 전략카드 (카탈로그/생성/활성화)
│   │   ├── llm/             — 백억이 AI 채팅
│   │   ├── reports/         — 리포트
│   │   ├── monitoring/      — 시스템 모니터링
│   │   ├── notifications/   — 알림
│   │   ├── settings/        — 설정
│   │   └── admin/           — 관리자
│   ├── terms/ privacy/ offline/
│   └── providers.tsx        — React Query + Auth Provider
│
├── go100/                   — GO100 전용 프론트엔드 모듈
│   (전략 설계 UI, 백억이 채팅, 유니버스 필터 빌더 등)
│
├── lib/api/                 — API 클라이언트 (16 모듈)
│   ├── client.ts            — 공통 HTTP 클라이언트 (JWT 자동 갱신)
│   ├── auth.ts              — 인증 API
│   ├── accounts.ts          — 계좌 API
│   ├── strategy-cards.ts    — 전략카드 API
│   ├── backtest.ts          — 백테스트 API
│   ├── llm.ts               — LLM 채팅 API (스트리밍)
│   ├── dashboard.ts         — 대시보드 API
│   ├── portfolio.ts         — 포트폴리오 API
│   ├── trade.ts             — 자동매매 API
│   ├── market.ts            — 시세 API
│   ├── monitoring.ts        — 모니터링 API
│   ├── reports.ts           — 리포트 API
│   ├── notifications.ts     — 알림 API
│   ├── settings.ts          — 설정 API
│   ├── admin.ts             — 관리자 API
│   └── accountSync.ts       — 계좌 동기화 API
│
└── components/              — UI 컴포넌트 (shadcn 기반)
    ├── chat/                — 백억이 채팅 UI
    ├── strategy/            — 전략카드 컴포넌트
    ├── backtest/            — 백테스트 결과/차트
    ├── dashboard/           — 위젯
    └── ui/                  — 공통 UI (Button, Modal, Table 등)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10. API 엔드포인트 전체 맵 (GO100)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

■ GO100 전용 (/api/go100/*)
  POST /api/go100/ai/chat        — 백억이 전략 대화 (JWT 필수)
  POST /api/go100/ai/understand  — UNDERSTAND 단독 (테스트)
  POST /api/go100/ai/design      — DESIGN 단독 (테스트)
  GET  /api/go100/strategies     — 내 전략 카드 목록
  POST /api/go100/strategies     — 전략 카드 생성
  GET  /api/go100/strategies/{id} — 전략 카드 상세
  PUT  /api/go100/strategies/{id} — 전략 카드 수정
  DELETE /api/go100/strategies/{id} — 전략 카드 삭제
  POST /api/go100/backtest/run   — 백테스트 실행
  GET  /api/go100/backtest/{id}  — 백테스트 결과 조회
  GET  /api/go100/portfolios     — 포트폴리오 목록
  POST /api/go100/portfolios     — 포트폴리오 생성
  GET  /api/go100/portfolios/{id}/positions — 포지션 조회

■ 공통 서비스 (/api/v1/*) — GO100도 사용
  /auth     — 로그인/회원가입/JWT/소셜
  /accounts — 증권 계좌 CRUD
  /market   — 시세/차트/업종/테마
  /llm      — 백억이 채팅 (V4.1 LLM Gateway)
  /dashboard — 대시보드 요약


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
11. LLM Gateway 라우팅 (GO100 관점)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌────────────────────────────────────────────────┐
│            LLMGateway (Singleton, V4.1 공유)    │
├────────────────────────────────────────────────┤
│ GO100 사용 라우팅:                              │
│   FREE_CHAT   → Gemini 2.0 Flash               │
│               (UNDERSTAND, REPLY)              │
│   DESIGN_CHAT → Claude Sonnet 4.6             │
│               (DESIGN)                        │
├────────────────────────────────────────────────┤
│ V4.1 사용 라우팅 (GO100 미사용):               │
│   C2SC          → GPT-4.1 mini                 │
│   STRATEGY_REVIEW → Claude Opus 4.6 (Batch)   │
├────────────────────────────────────────────────┤
│ 공통 인프라:                                    │
│   CircuitBreaker (벤더별, 5분 cooldown)         │
│   RateLimiter (Token Bucket)                    │
│   LLMCostTracker (llm_cost_daily)              │
│   프롬프트 캐싱 (Anthropic, 90% 절감)           │
└────────────────────────────────────────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12. 구현 완성도 현황 (2026-02-21 기준)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Phase | 내용                               | 상태      | 커밋      |
|-------|------------------------------------|-----------|-----------|
| 1     | DDL (7개 go100_* 테이블)            | ✅ 완료   | 84bb6c6a  |
| 2     | UniverseEngine 7필터 + AND/OR/NOT  | ✅ 완료   | bac814b6  |
| 3     | Card Service + Store API           | ✅ 완료   | —         |
| 3C    | Portfolio Service                  | ✅ 완료   | f37dc984  |
| 4     | Backtest Engine + Universe 연동    | ✅ 완료   | 6adb11d0  |
| 5     | UNDERSTAND + DESIGN 에이전트       | ✅ 완료   | d7206f1b  |
| 6     | EVALUATE + OPTIMIZE 루프           | ❌ 예정   | —         |
| 7     | Paper Trading 엔진                 | ❌ 예정   | —         |
| 8     | Live Trading 엔진                  | ❌ 예정   | —         |
| 9     | 고급 지표 필터 확장 (Bollinger 등)  | ❌ 예정   | —         |
| 10    | Strategy Evolution (주간 재평가)   | ❌ 예정   | —         |
| 11    | 정산 / 랭킹 / 네트워크 효과        | ❌ 예정   | —         |

테스트: 51 unit tests 통과 (Phase 2~5 합산)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
13. 알려진 이슈 및 기술 부채
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[P0 해결됨]
  ✅ 서비스 포트 충돌 (kis-v41-api vs go100) — kis-v41-api 중지로 해결
  ✅ 백테스트 거래 0건 — source_type SYSTEM/CUSTOM 통일로 해결
  ✅ DB 인증 — mock 단위 테스트 분리로 해결

[P1 현재]
  ⚠ BaseOrchestrator DB 저장 주석 처리 — Phase 6 활성화 대기
  ⚠ rank_market_cap ALL NULL — market_cap 필터 폴백 작동 중
  ⚠ sector_large 품질 혼재 (시가총액규모 vs 업종명)

[P2 대기]
  - EVALUATE/OPTIMIZE 에이전트 미구현 (Phase 6 핵심)
  - Paper Trading 엔진 미구현 (Phase 7)
  - Live Trading 엔진 미구현 (Phase 8)
  - 고급 지표 필터 14종 미구현 (Bollinger, MACD 등)
  - Market Regime 연동 (v4_market_regime_daily)
  - Sector Rotation 연동 (v4_investor_daily)
  - ATR 기반 동적 손절 미구현
  - 부분 익절 로직 미구현

[P3 향후]
  - 전략 성과 랭킹 / 네트워크 효과 학습
  - 주간 자동 재평가 스케줄러
  - 구독 과금 연동


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
14. 문서 변경 이력
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 버전 | 날짜       | 변경 내용                                                          |
|------|------------|---------------------------------------------------------------------|
| 1.0  | 2026-02-20 | 초판 작성 (go100-architecture-v1.0.md, V4.1과 혼합 형태)            |
| 1.1  | 2026-02-21 | GO100 전용 문서로 분리. Phase 5 완료 반영 (UNDERSTAND+DESIGN 에이전트)|
|      |            | DB 분리 완료 확인 (go100_strategy_cards 독립). 서비스 상태 갱신.    |
|      |            | 구현 완성도 표 (Phase 1~11) 추가. 기술 부채 현행화.                  |

================================================================
문서 끝 (go100-architecture-v1.1.md)
================================================================
