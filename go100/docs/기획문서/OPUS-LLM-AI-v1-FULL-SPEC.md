# OPUS-LLM-AI-v1 | LLM/AI 레이어 기획문서 (통합본)

**문서 ID:** OPUS-LLM-AI-v1-FULL-SPEC
**버전:** v2.1.1
**작성일:** 2026-02-19
**최종 수정:** 2026-02-23
**상태:** OPUS-MAIN-v1 승인 대기

---

## 목차

```
1. 문서 개요
2. 프로젝트 컨텍스트
3. LLM 멀티벤더 전략 (확정)
4. LLM Gateway 아키텍처 상세 설계
   4-A. 설계 판단 (미들웨어 vs 서비스 모듈)
   4-B. 전체 요청 흐름
   4-C. 클래스 다이어그램
   4-D. 데이터 모델 (Pydantic)
   4-E. 라우팅 엔진
   4-F. 페일오버 & 서킷 브레이커
   4-G. 프롬프트 캐싱 통합
   4-H. 배치 API 통합
   4-I. Rate Limiter
   4-J. 비용 추적 시스템
   4-K. 에러 핸들링 전략
5. 시퀀스 다이어그램
   5-A. 정상 흐름
   5-B. 페일오버 흐름
   5-C. 배치 흐름
6. DB 스키마 (DDL)
7. 환경 변수 (.env)
8. 코드베이스 배치 (파일 구조)
9. 시스템 프롬프트 가드레일
   9-A. 자유대화 프롬프트
   9-B. 설계대화 프롬프트
   9-C. C2SC 파싱 프롬프트
   9-D. CS 프롬프트 (Phase 2)
10. 비용 시뮬레이션 (100명 기준)
11. 미결 사항 & Phase 2 로드맵
12. Cursor 구현 지시서 초안
13. 변경 이력
```

---

## 1. 문서 개요

이 문서는 MyTrader AI 플랫폼의 LLM/AI 레이어 전체 설계를 통합한 기획문서다. OPUS-LLM-AI-v1 대화창에서 산출한 v2 보고서, v2.1 수정, v2.1.1 마이크로 수정을 모두 반영한 최종 통합본이며, OPUS-MAIN-v1의 Cursor 지시서 발행 전 최종 레퍼런스로 사용된다.

이 문서는 코드를 포함하지 않는다. 설계서와 Cursor 구현 지시서만 산출한다.

---

## 2. 프로젝트 컨텍스트

### 2-1. MyTrader AI란

MyTrader AI는 AI 교육형 자동매매 플랫폼이다. 자연어 대화를 통해 투자 교육을 받고, 전략을 설계하며, 백테스트와 모의투자를 거쳐 실전 매매까지 이어지는 흐름을 제공한다. 핵심 포지셔닝은 "투자 판단을 대신하지 않는 소프트웨어 도구 제공자"이며, 모든 투자 의사결정은 사용자 본인이 한다.

### 2-2. 기술 스택

백엔드는 FastAPI + PostgreSQL 16으로 구성되며, Naver Cloud Linux 서버에서 운영 중이다. 현재 V4.1이 운영 중이고, 동일 코드베이스에 V2.3 SaaS 기능을 확장하는 방식이다. 프론트엔드는 Flutter로 개발 예정이며, API 통신은 REST + WebSocket(실시간 알림용)을 사용한다.

### 2-3. 규제 환경

한국 인공지능기본법에 따라 AI 생성 답변에 대한 고지 의무가 있다. 모든 AI 응답에 "AI가 생성한 답변입니다" 표시를 포함한다. 자본시장법상 투자 자문 행위에 해당하지 않도록 종목 추천, 매매 시점 제안, 가격 예측을 엄격히 금지한다.

### 2-4. 도메인 분리 원칙

자유대화, 설계대화, CS는 완전히 분리된 도메인이다. 각 도메인은 별도의 시스템 프롬프트, 별도의 LLM 모델, 별도의 API 엔드포인트를 사용한다. 도메인 간 대화 히스토리의 교차 전달은 금지된다. 전환은 UI 버튼("전략 설계 시작하기") 클릭으로만 발생하며, 전환 시점에 user_id, session_id, timestamp를 DB에 기록한다.

---

## 3. LLM 멀티벤더 전략 (확정)

### 3-1. 용도별 모델 배치

| 용도 | 모델 | 벤더 | $/MTok In | $/MTok Out | 비고 |
|------|------|------|-----------|------------|------|
| 자유대화 | Gemini 2.0 Flash | Google | $0.10 | $0.40 | 최저 비용, 고속 |
| 설계대화 | Sonnet 4.6 | Anthropic | $3.00 | $15.00 | 프롬프트 캐싱 적용 |
| C2SC 파싱 | GPT-4.1 mini | OpenAI | $0.40 | $1.60 | temp=0.0 결정론적 |
| 전략 검증 | Opus 4.6 | Anthropic | $5.00 | $25.00 | 배치 API 50% 할인 |
| CS (Phase 2) | Gemini 2.0 Flash | Google | $0.10 | $0.40 | Phase 2 |

### 3-2. 페일오버 체인

| 도메인 | 1차 (기본) | 2차 (폴백) | 폴백 근거 |
|--------|-----------|-----------|-----------|
| free_chat | google/gemini-2.0-flash | anthropic/claude-haiku-4-5 | 저비용 유지 ($1/$5) |
| design_chat | anthropic/claude-sonnet-4-6 | anthropic/claude-sonnet-4-5 | 동일 벤더, 캐싱 구조 호환 |
| c2sc | openai/gpt-4.1-mini | anthropic/claude-sonnet-4-6 | JSON 파싱 정확도 |
| strategy_review | anthropic/claude-opus-4-6 | anthropic/claude-sonnet-4-6 | 경량 검증 |
| cs | google/gemini-2.0-flash | anthropic/claude-haiku-4-5 | 저비용 유지 |

설계대화 폴백을 GPT-4.1이 아닌 Sonnet 4.5로 선택한 근거는 다음과 같다. 설계대화 시스템 프롬프트가 Anthropic API 형식(cache_control 블록 포함)에 최적화되어 있으므로, 동일 벤더 내 폴백이 프롬프트 호환성과 캐싱 구조를 유지할 수 있다. GPT-4.1로 폴백하려면 프롬프트 구조 변환이 필요해 지연이 발생한다.

### 3-3. 비용 최적화 전략

Anthropic 프롬프트 캐싱을 설계대화와 전략 검증에 적용하여 시스템 프롬프트 입력 비용을 90% 절감한다. 캐시 생성 시 25% 할증이 있으나, 이후 5분 TTL 내 히트 시 10%만 과금된다. Anthropic 배치 API를 전략 검증(Opus 4.6)에 적용하여 전체 비용을 50% 절감한다. 배치 처리는 비동기로 1~2분 내 완료되며, 사용자에게 "검증 중" 상태를 표시한다. 사용자당 월 LLM 비용 목표는 ₩900 이하이며, 실제 시뮬레이션 결과 ₩216으로 목표의 24% 수준이다.

---

## 4. LLM Gateway 아키텍처 상세 설계

### 4-A. 설계 판단: 미들웨어 vs 서비스 모듈

**결정: 독립 서비스 모듈로 구현한다.**

FastAPI 미들웨어 방식은 모든 HTTP 요청을 가로채므로, LLM과 무관한 요청(헬스체크, 정적 파일, 인증 API 등)에도 불필요한 오버헤드가 발생한다. LLM Gateway는 Chat Router에서 명시적으로 호출되는 서비스 레이어 모듈이 적합하다. FastAPI의 lifespan 이벤트에서 싱글톤으로 초기화하고, Dependency Injection으로 라우터에 주입하는 구조를 채택한다.

### 4-B. 전체 요청 흐름

```
Client (Flutter App)
  │
  │ POST /api/v1/chat
  │ Body: { message, domain_type, session_id }
  │
  ▼
┌─────────────────────────────────────────┐
│  api/v1/chat.py (FastAPI 엔드포인트)      │
│  - JWT 인증 → user_id 추출               │
│  - 사용자별 Rate Limit 체크 (RPM, Daily) │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  services/ai/chat_router.py             │
│  - domain_type → request_type 매핑      │
│  - 시스템 프롬프트 로드                    │
│  - 대화 히스토리 조합                     │
│  - LLMGateway.send() 호출               │
│  - 응답 후처리 (전환 카드, AI 고지 삽입)   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  core/llm_gateway.py (LLMGateway 싱글톤) │
│  - _resolve_route(request_type)         │
│  - RateLimiter.try_acquire(vendor)      │
│  - CircuitBreaker.check(vendor)         │
│  - VendorClient.send()                  │
│  - (실패 시) _execute_with_failover()   │
│  - CostTracker.record()                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  core/llm_clients/                      │
│  - gemini_client.py → Google Gemini API │
│  - anthropic_client.py → Anthropic API  │
│  - openai_client.py → OpenAI API        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  core/llm_cost_tracker.py               │
│  - 비용 계산 (캐시 할인, 배치 할인 반영)  │
│  - DB INSERT (llm_requests)             │
│  - 예산 알림 체크                        │
└─────────────────────────────────────────┘
                 │
                 ▼
            JSON Response → Client
```

### 4-C. 클래스 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Lifespan                           │
│         (startup → LLMGateway.init(), shutdown → cleanup)    │
└─────────────────────────┬───────────────────────────────────┘
                          │ DI inject
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  LLMGateway (Singleton)                       │
│  파일: core/llm_gateway.py                                    │
│─────────────────────────────────────────────────────────────│
│ 속성:                                                        │
│ - _instance: ClassVar[LLMGateway | None]                     │
│ - _clients: dict[str, BaseLLMClient]                         │
│   → {"google": GeminiClient,                                 │
│      "anthropic": AnthropicClient,                           │
│      "openai": OpenAIClient}                                 │
│ - _routing_table: dict[str, RouteConfig]                     │
│   → {"free_chat": RouteConfig(...), ...}                     │
│ - _failover_chains: dict[str, list[RouteConfig]]             │
│ - _circuit_breakers: dict[str, CircuitBreaker]               │
│   → {"google": CB, "anthropic": CB, "openai": CB}           │
│ - _rate_limiters: dict[str, RateLimiter]                     │
│   → {"google": RL, "anthropic": RL, "openai": RL}           │
│ - _cost_tracker: LLMCostTracker                              │
│ - _batch_queue: BatchQueue                                   │
│─────────────────────────────────────────────────────────────│
│ 메서드:                                                       │
│ + get_instance() → LLMGateway          [클래스메서드]          │
│ + send(req: LLMRequest) → LLMResponse  [주요 진입점]          │
│ + send_batch(req: LLMRequest) → BatchJob [배치 진입점]        │
│ - _resolve_route(request_type: str) → RouteConfig             │
│ - _execute_with_failover(                                     │
│     route: RouteConfig,                                       │
│     messages: list,                                           │
│     system_prompt: str                                        │
│   ) → LLMResponse                                            │
│ - _handle_error(vendor: str, error: Exception) → None         │
│ - _build_failover_route(                                      │
│     request_type: str,                                        │
│     failed_index: int                                         │
│   ) → RouteConfig | None                                      │
└──────────┬──────────────┬───────────────┬───────────────────┘
           │              │               │
           │ owns         │ owns          │ owns
           ▼              ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ GeminiClient │  │Anthropic     │  │ OpenAIClient │
│              │  │  Client      │  │              │
│ SDK:         │  │ SDK:         │  │ SDK:         │
│ google-genai │  │ anthropic    │  │ openai       │
│              │  │              │  │              │
│ 특화:        │  │ 특화:        │  │ 특화:        │
│ - 표준 호출  │  │ - cache_     │  │ - temp=0.0   │
│              │  │   control    │  │   결정론적   │
│              │  │ - 배치 API   │  │              │
│              │  │ - 캐시 토큰  │  │              │
│              │  │   추출       │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
       ▲                ▲                 ▲
       └────────────────┼─────────────────┘
                        │ implements
            ┌───────────▼───────────┐
            │  BaseLLMClient (ABC)  │
            │───────────────────────│
            │ + send(               │
            │     messages: list,   │
            │     system_prompt:str,│
            │     params: dict      │
            │   ) → RawResponse     │
            │ + parse_response(     │
            │     raw: RawResponse  │
            │   ) → StandardResp.   │
            │ + count_tokens(       │
            │     raw: RawResponse  │
            │   ) → TokenUsage      │
            └───────────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐
│  CircuitBreaker   │  │   RateLimiter    │  │  BatchQueue    │
│──────────────────│  │──────────────────│  │────────────────│
│ 속성:             │  │ 속성:            │  │ 속성:          │
│ - vendor: str     │  │ - vendor: str    │  │ - _pending:    │
│ - state: CBState  │  │ - rpm_bucket:    │  │    list[Req]   │
│   (CLOSED/OPEN/   │  │    TokenBucket   │  │ - _poll_task:  │
│    HALF_OPEN)     │  │ - tpm_bucket:    │  │    asyncio.Task│
│ - opened_at:      │  │    TokenBucket   │  │ - poll_interval│
│    datetime|None  │  │──────────────────│  │    : 15s       │
│ - failure_count:  │  │ 메서드:          │  │ - max_wait:    │
│    int            │  │ + try_acquire(   │  │    300s        │
│ - cooldown: 300s  │  │    est_tokens:int│  │────────────────│
│ - threshold: 3    │  │   ) → bool       │  │ 메서드:        │
│──────────────────│  │ + wait_or_fail() │  │ + enqueue(req) │
│ 메서드:           │  │    → bool        │  │    → job_id    │
│ + trip() → None   │  │ + _refill()      │  │ + submit()     │
│ + check() → bool  │  │    (매초 리필)   │  │    → batch_id  │
│ + reset() → None  │  └──────────────────┘  │ + poll()       │
│ + is_available()  │                         │    → results   │
│    → bool         │                         │ + on_done(     │
└──────────────────┘                          │    callback)   │
                                              └────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   LLMCostTracker                             │
│  파일: core/llm_cost_tracker.py                              │
│─────────────────────────────────────────────────────────────│
│ 속성:                                                        │
│ - _db: AsyncSession                                          │
│ - _price_map: dict[tuple[str,str], PriceTier]                │
│   → {("anthropic","claude-sonnet-4-6"): PriceTier(...), ...} │
│ - _monthly_budget_usd: float (from .env)                     │
│ - _user_warn_usd: float (from .env)                          │
│─────────────────────────────────────────────────────────────│
│ 메서드:                                                       │
│ + record(log: UsageLog) → None                               │
│   → 비용 계산 + DB INSERT (llm_requests)                      │
│ + calc_cost(vendor, model, tokens, cache, batch) → float    │
│ + get_user_monthly(user_id: int) → CostSummary               │
│ + get_total_daily() → CostSummary                            │
│ + check_budget() → BudgetAlert | None                        │
│ + aggregate_daily() → None  (크론: 매일 00:05 KST)           │
│   → llm_requests → llm_cost_daily 집계                       │
└─────────────────────────────────────────────────────────────┘
```

### 4-D. 데이터 모델 (Pydantic)

```
┌─────────────────────────┐
│       LLMRequest         │
│─────────────────────────│
│ request_type: str        │  "free_chat" | "design_chat" | "c2sc"
│                          │  | "strategy_review" | "cs"
│ messages: list[Message]  │  [{"role":"user","content":"..."}]
│ system_prompt: str       │  도메인별 시스템 프롬프트
│ user_id: int             │  BIGINT, v4_users.user_id FK
│ session_id: str          │  대화 세션 식별자
│ metadata: dict           │  추가 컨텍스트 (선택)
│ max_tokens: int | None   │  RouteConfig 기본값 오버라이드
│ temperature: float | None│  RouteConfig 기본값 오버라이드
└─────────────────────────┘

┌─────────────────────────┐
│       LLMResponse        │
│─────────────────────────│
│ content: str             │  LLM 응답 텍스트
│ token_usage: TokenUsage  │  토큰 사용량 상세
│ cost_usd: float          │  이 호출의 비용 (USD)
│ latency_ms: int          │  응답 시간
│ is_failover: bool        │  페일오버 발생 여부
│ model_used: str          │  실제 사용된 모델
│ vendor_used: str         │  실제 사용된 벤더
│ batch_job_id: str | None │  배치 요청 시 job ID
└─────────────────────────┘

┌─────────────────────────┐
│       TokenUsage         │
│─────────────────────────│
│ input_tokens: int        │  일반 입력 토큰
│ output_tokens: int       │  출력 토큰
│ cache_creation_tokens:int│  캐시 생성 토큰 (Anthropic)
│ cache_read_tokens: int   │  캐시 히트 토큰 (Anthropic)
└─────────────────────────┘

┌─────────────────────────┐
│       RouteConfig        │
│─────────────────────────│
│ vendor: str              │  "google" | "anthropic" | "openai"
│ model: str               │  모델 식별자
│ max_tokens: int          │  최대 출력 토큰
│ temperature: float       │  생성 온도
│ timeout_s: int           │  타임아웃 (초)
│ cache_enabled: bool      │  프롬프트 캐싱 적용 여부
└─────────────────────────┘

┌─────────────────────────┐
│       PriceTier          │
│─────────────────────────│
│ input_per_mtok: float    │  입력 $/MTok
│ output_per_mtok: float   │  출력 $/MTok
│ cache_create_per_mtok:   │  캐시 생성 $/MTok (nullable)
│   float | None           │
│ cache_read_per_mtok:     │  캐시 히트 $/MTok (nullable)
│   float | None           │
└─────────────────────────┘

┌─────────────────────────┐
│       UsageLog           │
│─────────────────────────│
│ user_id: int             │
│ session_id: str          │
│ request_type: str        │
│ vendor: str              │
│ model: str               │
│ token_usage: TokenUsage  │
│ cost_usd: float          │
│ is_cache_hit: bool       │
│ is_failover: bool        │
│ is_batch: bool           │
│ latency_ms: int          │
│ error_code: str | None   │
│ failover_from_vendor:    │
│   str | None             │
│ failover_from_model:     │
│   str | None             │
└─────────────────────────┘

┌─────────────────────────┐
│       BatchJob           │
│─────────────────────────│
│ job_id: str              │  내부 관리 ID
│ batch_id: str | None     │  Anthropic batch ID
│ status: str              │  "queued"|"submitted"|"ended"|"failed"
│ request: LLMRequest      │  원본 요청
│ result: LLMResponse|None │  완료 시 결과
│ created_at: datetime     │
│ completed_at: datetime|  │
│   None                   │
└─────────────────────────┘

┌─────────────────────────┐
│     CostSummary          │
│─────────────────────────│
│ total_cost_usd: float    │
│ total_calls: int         │
│ total_input_tokens: int  │
│ total_output_tokens: int │
│ avg_latency_ms: int      │
│ cache_hit_rate: float    │
│ failover_count: int      │
│ period: str              │  "daily" | "monthly"
└─────────────────────────┘

┌─────────────────────────┐
│     BudgetAlert          │
│─────────────────────────│
│ level: str               │  "WARNING" | "CRITICAL"
│ current_usd: float       │
│ budget_usd: float        │
│ usage_pct: float         │
│ message: str             │
└─────────────────────────┘
```

### 4-E. 라우팅 엔진

**저장 방식: 코드 상수 + .env 오버라이드**

100명 규모 MVP에서 DB 관리는 오버엔지니어링이다. 코드 상수로 기본 매핑을 정의하되, .env의 LLM_*_MODEL 변수로 런타임 오버라이드를 지원한다. 모델 전환(예: Sonnet 4.5 → Sonnet 4.6)이 .env 변경 + 서비스 재시작으로 완료된다. Phase 2에서 관리자 UI가 필요해지면 그때 DB 테이블(llm_routing_config)로 승격한다.

**라우팅 매핑 테이블:**

```python
ROUTING_TABLE = {
    "free_chat": RouteConfig(
        vendor="google",
        model=env("LLM_FREE_CHAT_MODEL", "gemini-2.0-flash"),
        max_tokens=2048,
        temperature=0.7,
        timeout_s=10,
        cache_enabled=False,
    ),
    "design_chat": RouteConfig(
        vendor="anthropic",
        model=env("LLM_DESIGN_CHAT_MODEL", "claude-sonnet-4-6"),
        max_tokens=4096,
        temperature=0.3,
        timeout_s=30,
        cache_enabled=True,
    ),
    "c2sc": RouteConfig(
        vendor="openai",
        model=env("LLM_C2SC_MODEL", "gpt-4.1-mini"),
        max_tokens=2048,
        temperature=0.0,
        timeout_s=10,
        cache_enabled=False,
    ),
    "strategy_review": RouteConfig(
        vendor="anthropic",
        model=env("LLM_STRATEGY_REVIEW_MODEL", "claude-opus-4-6"),
        max_tokens=8192,
        temperature=0.2,
        timeout_s=60,
        cache_enabled=True,
    ),
    "cs": RouteConfig(
        vendor="google",
        model=env("LLM_CS_MODEL", "gemini-2.0-flash"),
        max_tokens=1024,
        temperature=0.5,
        timeout_s=10,
        cache_enabled=False,
    ),
}
```

**페일오버 체인:**

```python
FAILOVER_CHAINS = {
    "free_chat":       ["google/gemini-2.0-flash",    "anthropic/claude-haiku-4-5"],
    "design_chat":     ["anthropic/claude-sonnet-4-6", "anthropic/claude-sonnet-4-5"],
    "c2sc":            ["openai/gpt-4.1-mini",         "anthropic/claude-sonnet-4-6"],
    "strategy_review": ["anthropic/claude-opus-4-6",   "anthropic/claude-sonnet-4-6"],
    "cs":              ["google/gemini-2.0-flash",     "anthropic/claude-haiku-4-5"],
}
```

**라우팅 해석 흐름:**

LLMGateway.send() 호출 시, request_type으로 ROUTING_TABLE을 조회하여 RouteConfig를 얻는다. LLMRequest에 max_tokens나 temperature가 명시되어 있으면 RouteConfig 기본값을 오버라이드한다. RouteConfig의 vendor 필드로 _clients 딕셔너리에서 해당 벤더 클라이언트를 가져온다. 이후 Rate Limiter와 Circuit Breaker를 통과한 뒤 실제 API 호출이 진행된다.

### 4-F. 페일오버 & 서킷 브레이커

**페일오버 트리거 조건 (OR):**

HTTP 5xx 응답, 벤더별 timeout_s 초과, HTTP 429(Rate Limit Exceeded)에서 3회 재시도 후에도 실패, ConnectionError 또는 DNS 실패가 발생하면 페일오버가 트리거된다.

**페일오버 실행 흐름:**

1차 모델 호출 실패 시, 로그에 "FAILOVER | {request_type} | {1차 모델} → {2차 모델} | reason={실패 사유}"를 기록한다. FAILOVER_CHAINS에서 다음 인덱스의 모델을 조회하여 해당 벤더 클라이언트로 재시도한다. 2차 모델도 실패하면 클라이언트에 "일시적으로 서비스가 원활하지 않습니다. 잠시 후 다시 시도해 주세요." 에러를 반환한다. 페일오버 발생 시 CostTracker에 is_failover=true, failover_from_vendor, failover_from_model을 기록한다.

**서킷 브레이커 상태 머신:**

```
CLOSED ──(5분 윈도우 내 실패 3회)──→ OPEN
  │                                    │
  │                                (300초 대기)
  │                                    │
  │                                    ▼
  │                                HALF_OPEN
  │                                    │
  │                         ┌──────────┼──────────┐
  │                         ▼                     ▼
  │                  (테스트 1회 성공)       (테스트 실패)
  │                         │                     │
  │                         ▼                     ▼
  └───(정상 유지)────── CLOSED               OPEN (300초 재시작)
```

**서킷 브레이커 파라미터:**

cooldown은 300초(5분)이며, 이 시간 동안 해당 벤더로의 모든 요청이 차단되고 자동으로 페일오버 체인이 사용된다. failure_threshold는 3회(5분 윈도우 내)로, 이를 초과하면 서킷이 OPEN된다. half_open_max_calls는 1회로, HALF_OPEN 상태에서 테스트 호출 1회를 시도한다. 서킷 브레이커는 벤더 단위로 관리하며, 모델 단위가 아니다. Google 서킷이 열리면 gemini-2.0-flash 전체가 차단된다.

**TRIP하지 않는 조건:**

HTTP 429(Rate Limit)는 일시적 제한이므로 서킷 브레이커를 trip하지 않고, 재시도 로직에서 처리한다. HTTP 4xx(클라이언트 오류)도 요청 자체의 문제이므로 trip하지 않는다.

### 4-G. 프롬프트 캐싱 통합

**적용 대상:**

설계대화(Sonnet 4.6)와 전략 검증(Opus 4.6)에 Anthropic 프롬프트 캐싱을 적용한다. 자유대화(Gemini)와 C2SC(OpenAI)에는 적용하지 않는다. Gemini의 Context Caching은 별도 API이며 Phase 2에서 검토한다.

**구조: 정적 부분 / 동적 부분 분리**

Anthropic API에서 system 필드의 텍스트 블록에 cache_control: {"type": "ephemeral"}을 추가하면, 해당 블록이 캐시 대상이 된다. 시스템 프롬프트(약 950~1,000 토큰)는 모든 사용자에게 동일하므로 정적 부분으로 캐시하고, 사용자 메시지는 동적 부분으로 캐시하지 않는다.

```
Anthropic API 요청 구조:

{
  "model": "claude-sonnet-4-6",
  "max_tokens": 4096,
  "system": [
    {
      "type": "text",
      "text": "[ 시스템 프롬프트 전체 텍스트 ~950 토큰 ]",
      "cache_control": {"type": "ephemeral"}     ← 캐시 마커
    }
  ],
  "messages": [
    {"role": "user", "content": "동적 사용자 메시지"}
  ]
}
```

**캐시 비용 구조 (2026-02-19 확인):**

| 상황 | Sonnet 4.6 단가 | 시스템 프롬프트 950 토큰 비용 |
|------|----------------|-------------------------------|
| 캐시 없음 (기본) | $3.00 / MTok | $0.00285 |
| 캐시 생성 (첫 호출) | $3.75 / MTok (25% 할증) | $0.00356 |
| 캐시 히트 (이후) | $0.30 / MTok (90% 절감) | $0.000285 |

**캐시 TTL:**

기본 5분이며, 동일 prefix로 호출할 때마다 TTL이 갱신된다. 1시간 옵션도 추가 비용으로 가능하나, 5분 TTL로 충분하다(활성 사용자가 있는 한 계속 갱신). 동일 시스템 프롬프트를 사용하는 다수 사용자가 호출하면 캐시가 공유된다.

**캐시 히트율 모니터링:**

AnthropicClient.parse_response() 시 응답의 usage 필드에서 cache_creation_input_tokens와 cache_read_input_tokens를 추출한다. llm_requests 테이블의 cache_creation_tokens, cache_read_tokens 필드에 기록한다. 히트율은 SUM(CASE WHEN cache_read_tokens > 0 THEN 1 ELSE 0 END) / COUNT(*) FILTER (WHERE vendor = 'anthropic')로 산출한다. 히트율 80% 미만 시 WARNING 로그 + 관리자 알림이 발생하며, 프롬프트 변경 빈도가 높아 캐시가 무효화되고 있는지 점검해야 한다.

### 4-H. 배치 API 통합

**대상:** 전략 검증(strategy_review) 전용. 나머지 도메인은 모두 실시간 처리.

**배치 처리를 전략 검증에만 적용하는 근거:** 전략 검증은 심층 분석이므로 1~2분 지연이 허용된다. Opus 4.6의 높은 비용($5/$25)에서 배치 50% 할인 효과가 크다(월 $8.5 절감). 자유대화와 설계대화는 실시간 응답이 필수이므로 배치 부적합. C2SC는 비용이 낮아($0.176/월) 배치 효과 미미.

**배치 처리 흐름:**

1단계로 ChatRouter가 strategy_review 요청을 LLMGateway.send_batch()로 전달한다. 2단계에서 BatchQueue.enqueue()가 요청을 내부 큐에 축적하고 job_id를 반환한다. 3단계에서 클라이언트에 즉시 응답으로 {"status": "queued", "batch_job_id": "batch_001"}을 전달한다. 4단계에서 프론트엔드가 "AI가 전략을 심층 검증 중입니다 (약 1~2분)" + 프로그레스 인디케이터를 표시한다. 5단계에서 Background Worker가 큐에서 꺼내어 Anthropic Batch API(create_message_batch)로 제출한다. 6단계에서 15초 간격으로 폴링(retrieve_message_batch)하여 완료를 확인한다. 7단계에서 완료 시 결과를 파싱하고, CostTracker에 50% 할인 비용을 기록하며, WebSocket/SSE로 클라이언트에 push한다.

**큐 구현 (MVP):** Redis나 Celery 대신 asyncio.Queue + BackgroundTask로 구현한다. 100명 규모에서 전략 검증은 동시 2~3건 이하로 예상되므로 충분하다. Scale-out이 필요해지면 Phase 2에서 Redis Queue로 전환한다.

**타임아웃:** 배치 최대 대기 300초(5분). 초과 시 사용자에게 "검증 시간이 초과되었습니다. 다시 시도해 주세요." 안내와 함께 job을 실패 처리한다.

### 4-I. Rate Limiter

**벤더별 Rate Limit 설정 (보수적: 실제 한도의 70~80%):**

| 벤더 | RPM (분당 요청) | TPM (분당 토큰) | 근거 |
|------|----------------|----------------|------|
| Google | 800 | 4,000,000 | Gemini Paid Tier |
| Anthropic | 800 | 160,000 | Tier 1 기준 |
| OpenAI | 800 | 2,000,000 | Tier 1 기준 |

**사용자별 Rate Limit (ChatRouter 레벨, Gateway 진입 전):**

| 제한 | 값 | 초과 시 |
|------|-----|---------|
| 분당 요청 | 10 RPM | HTTP 429 + "잠시 후 다시 시도해 주세요" |
| 일일 요청 | 500/일 | HTTP 429 + "오늘의 이용 한도에 도달했습니다" |

사용자별 제한은 ChatRouter에서 체크하여 LLMGateway까지 도달하지 않게 한다. 이를 통해 벤더 Rate Limit 소진을 방지한다.

**Token Bucket 알고리즘:**

버킷 용량은 RPM (또는 TPM)과 동일하다. 매 초마다 (limit / 60) 만큼 리필한다. 요청 시 try_acquire(estimated_tokens)를 호출하여, RPM 체크에는 1, TPM 체크에는 예상 토큰 수를 사용한다. 버킷 잔량이 부족하면 100ms 백오프 후 재시도하며 최대 3회까지 시도한다. 3회 실패 시 페일오버 체인으로 전환한다.

### 4-J. 비용 추적 시스템

**가격 테이블 (코드 상수, LLMCostTracker 내장):**

```python
PRICE_TABLE = {
    ("google",    "gemini-2.0-flash"):     PriceTier(0.10, 0.40,  None, None),
    ("anthropic", "claude-sonnet-4-5"):    PriceTier(3.00, 15.00, 3.75, 0.30),
    ("anthropic", "claude-sonnet-4-6"):    PriceTier(3.00, 15.00, 3.75, 0.30),
    ("anthropic", "claude-opus-4-6"):      PriceTier(5.00, 25.00, 6.25, 0.50),
    ("anthropic", "claude-haiku-4-5"):     PriceTier(1.00, 5.00,  1.25, 0.10),
    ("openai",    "gpt-4.1-mini"):         PriceTier(0.40, 1.60,  None, 0.10),
}
```

**비용 계산 공식:**

```
base_input_cost =
    (input_tokens - cache_read_tokens) × input_per_mtok / 1,000,000

cache_create_cost =
    cache_creation_tokens × cache_create_per_mtok / 1,000,000

cache_read_cost =
    cache_read_tokens × cache_read_per_mtok / 1,000,000

output_cost =
    output_tokens × output_per_mtok / 1,000,000

subtotal = base_input_cost + cache_create_cost + cache_read_cost + output_cost

if is_batch:
    cost_usd = subtotal × 0.5
else:
    cost_usd = subtotal
```

**예산 한도:**

| 레벨 | 한도 | 도달 시 동작 |
|------|------|-------------|
| 사용자별 | $2.00/월 (≈₩2,900) | WARNING 로그 + "이번 달 AI 사용량이 많습니다" 안내. 차단하지 않음 (MVP). |
| 서비스 전체 80% | $80/월 | WARNING 로그 + 관리자 알림 |
| 서비스 전체 100% | $100/월 (≈₩145,000) | CRITICAL 로그 + 관리자 긴급 알림. 차단은 수동 판단. |

**일별 집계 크론:**

매일 00:05 KST에 크론 작업이 실행되어, llm_requests의 전일 데이터를 llm_cost_daily 테이블로 집계한다. user_id + request_type + vendor + model 조합별로 GROUP BY하여 INSERT한다. UNIQUE 제약조건(date, user_id, request_type, vendor, model)으로 멱등성을 보장한다.

### 4-K. 에러 핸들링 전략

**벤더별 타임아웃:**

| 도메인 | 타임아웃 | 근거 |
|--------|---------|------|
| free_chat | 10초 | 실시간 대화, 사용자 인내 한계 |
| design_chat | 30초 | 전략 파라미터 구조화에 시간 소요 |
| c2sc | 10초 | JSON 파싱, 빠른 응답 기대 |
| strategy_review | 60초 | 심층 검증 (배치는 별도 관리) |
| cs | 10초 | CS는 즉시 응답 기대 |

**Rate Limit (HTTP 429) 처리 흐름:**

429 수신 시 Retry-After 헤더를 확인한다. 헤더가 없으면 exponential backoff(1초, 2초, 4초)를 적용한다. 최대 3회 재시도하며, 3회 모두 실패하면 페일오버 체인으로 전환한다. 서킷 브레이커는 429에서 trip하지 않는다(일시적 제한이므로 5분 차단은 과도).

**에러 분류 및 대응:**

| 에러 유형 | 대응 | 서킷 trip | 사용자 메시지 |
|----------|------|----------|-------------|
| HTTP 5xx | 즉시 페일오버 | 3회 누적 시 | (투명 처리, 사용자 인지 없음) |
| Timeout | 즉시 페일오버 | 3회 누적 시 | (투명 처리) |
| HTTP 429 | 재시도 3회 → 페일오버 | 안 함 | (투명 처리) |
| Connection Error | 즉시 페일오버 | 3회 누적 시 | (투명 처리) |
| HTTP 4xx (인증 등) | 재시도 안 함, 로그 | 안 함 | "일시적 오류가 발생했습니다" |
| 2차 모델도 실패 | 에러 반환 | — | "서비스가 원활하지 않습니다. 잠시 후 다시 시도해 주세요." |

---

## 5. 시퀀스 다이어그램

### 5-A. 정상 흐름 (자유대화 예시)

```
┌──────┐    ┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
│Client│    │ chat.py  │    │ChatRouter │    │LLMGateway │    │GeminiCli.│
└──┬───┘    └────┬─────┘    └─────┬─────┘    └─────┬─────┘    └────┬─────┘
   │             │               │                 │                │
   │ POST /chat  │               │                 │                │
   │ {msg,       │               │                 │                │
   │  domain:    │               │                 │                │
   │  FREE_CHAT} │               │                 │                │
   │────────────>│               │                 │                │
   │             │ JWT 인증       │                 │                │
   │             │ user_id 추출   │                 │                │
   │             │ 사용자 RPM 체크│                 │                │
   │             │───┐           │                 │                │
   │             │<──┘ OK        │                 │                │
   │             │ route(msg,    │                 │                │
   │             │  FREE_CHAT,   │                 │                │
   │             │  user_id,     │                 │                │
   │             │  session_id)  │                 │                │
   │             │──────────────>│                 │                │
   │             │               │ 시스템 프롬프트   │                │
   │             │               │ 로드 (free_chat │                │
   │             │               │ .txt)           │                 │
   │             │               │ send(LLMReq)    │                 │
   │             │               │────────────────>│                │
   │             │               │                 │ _resolve_route  │
   │             │               │                 │ RateLimit OK    │
   │             │               │                 │ Circuit OK      │
   │             │               │                 │ send() ────────>│
   │             │               │                 │ RawResponse    │
   │             │               │                 │<────────────────│
   │             │               │                 │ CostTracker    │
   │             │               │  LLMResponse     │ .record()       │
   │             │               │<────────────────│                │
   │             │  응답 후처리:   │                 │                │
   │             │  AI 고지 삽입  │                 │                │
   │  JSON Resp  │<──────────────│                 │                │
```

### 5-B. 페일오버 흐름 (자유대화, Gemini 타임아웃)

```
┌──────┐    ┌───────────┐    ┌──────────┐    ┌──────────────┐
│Client│    │LLMGateway │    │GeminiCli.│    │AnthropicCli. │
   │              │ send(req)   │               │                  │
   │              │ _resolve_route → google/gemini-flash            │
   │              │ send(msgs) ───────────────>│                  │
   │              │               │ TIMEOUT ❌    │                  │
   │              │ TimeoutError <──────────────│                  │
   │              │ _handle_error │ Circuit failure_count += 1       │
   │              │ LOG: FAILOVER free_chat | google → anthropic   │
   │              │ _build_failover_route → anthropic/haiku-4-5     │
   │              │ send(msgs, haiku-4-5) ─────────────────────────>│
   │              │ RawResponse  <─────────────────────────────────│
   │              │ CostTracker .record(is_failover=true)          │
   │  LLMResponse │<─────────────│                                  │
```

### 5-C. 배치 흐름 (전략 검증)

```
┌──────┐    ┌───────────┐    ┌──────────┐    ┌──────────────┐
│Client│    │LLMGateway │    │BatchQueue│    │Anthropic API │
   │ send_batch(strategy_review) │               │                  │
   │─────────────>│ enqueue(req) │               │                  │
   │              │──────────────>│ job_id       │                  │
   │  즉시 응답:   │<──────────────│               │                  │
   │  {status:queued, job_id}    │               │                  │
   │  [Flutter] "AI가 전략을 심층 검증 중입니다 (약 1~2분)"           │
   │    ════ Background Worker (15초 간격) ════   │                  │
   │              │               │ submit_batch() → create_message_batch
   │              │               │─────────────────>│ batch_id      │
   │              │               │ poll → retrieve_message_batch   │
   │              │               │ status: ended, results         │
   │              │ CostTracker .record(is_batch=T, cost×0.5)       │
   │  WebSocket/SSE push: "전략 검증 완료" + 검증 결과 카드          │
   │<─────────────│               │                  │
```

---

## 6. DB 스키마 (DDL)

### 6-1. llm_requests (API 호출 개별 로그)

```sql
CREATE TABLE IF NOT EXISTS llm_requests (
    id                          BIGSERIAL       PRIMARY KEY,
    user_id                     BIGINT          NOT NULL
                                REFERENCES v4_users(user_id),
    session_id                  VARCHAR(64)     NOT NULL,
    request_type                VARCHAR(32)     NOT NULL
                                CHECK (request_type IN (
                                    'free_chat','design_chat','c2sc',
                                    'strategy_review','cs'
                                )),
    vendor                      VARCHAR(16)     NOT NULL
                                CHECK (vendor IN ('google','anthropic','openai')),
    model                       VARCHAR(64)     NOT NULL,

    input_tokens                INTEGER         NOT NULL DEFAULT 0,
    output_tokens               INTEGER         NOT NULL DEFAULT 0,
    cache_creation_tokens       INTEGER         NOT NULL DEFAULT 0,
    cache_read_tokens           INTEGER         NOT NULL DEFAULT 0,

    cost_usd                    NUMERIC(10,6)   NOT NULL DEFAULT 0,

    is_cache_hit                BOOLEAN         NOT NULL DEFAULT FALSE,
    is_failover                 BOOLEAN         NOT NULL DEFAULT FALSE,
    is_batch                    BOOLEAN         NOT NULL DEFAULT FALSE,
    latency_ms                  INTEGER         NOT NULL DEFAULT 0,
    error_code                  VARCHAR(32)     NULL,
    failover_from_vendor        VARCHAR(16)     NULL,
    failover_from_model         VARCHAR(64)     NULL,

    created_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_llm_req_user_created
    ON llm_requests (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_req_type_created
    ON llm_requests (request_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_req_vendor_created
    ON llm_requests (vendor, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_req_monthly_cost
    ON llm_requests (user_id, created_at)
    WHERE error_code IS NULL;
```

### 6-2. llm_cost_daily (일별 집계)

```sql
CREATE TABLE IF NOT EXISTS llm_cost_daily (
    id                  SERIAL          PRIMARY KEY,
    date                DATE            NOT NULL,
    user_id             BIGINT          NOT NULL
                        REFERENCES v4_users(user_id),
    request_type        VARCHAR(32)     NOT NULL,
    vendor              VARCHAR(16)     NOT NULL,
    model               VARCHAR(64)     NOT NULL,

    total_calls         INTEGER         NOT NULL DEFAULT 0,
    total_input_tokens  BIGINT          NOT NULL DEFAULT 0,
    total_output_tokens BIGINT          NOT NULL DEFAULT 0,
    total_cost_usd      NUMERIC(10,4)   NOT NULL DEFAULT 0,

    cache_hit_count     INTEGER         NOT NULL DEFAULT 0,
    failover_count      INTEGER         NOT NULL DEFAULT 0,
    avg_latency_ms      INTEGER         NOT NULL DEFAULT 0,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE (date, user_id, request_type, vendor, model)
);

CREATE INDEX IF NOT EXISTS idx_llm_cost_daily_date
    ON llm_cost_daily (date DESC);
CREATE INDEX IF NOT EXISTS idx_llm_cost_daily_user
    ON llm_cost_daily (user_id, date DESC);
```

### 6-3. 집계 뷰 (2종)

```sql
CREATE OR REPLACE VIEW vw_llm_user_monthly AS
SELECT
    user_id,
    DATE_TRUNC('month', created_at)         AS month,
    COUNT(*)                                 AS total_calls,
    SUM(cost_usd)                            AS total_cost_usd,
    SUM(input_tokens)                        AS total_input_tokens,
    SUM(output_tokens)                       AS total_output_tokens,
    AVG(latency_ms)::INTEGER                 AS avg_latency_ms,
    ROUND(
        SUM(CASE WHEN is_cache_hit THEN 1 ELSE 0 END)::NUMERIC
        / NULLIF(COUNT(*) FILTER (WHERE vendor = 'anthropic'), 0),
        3
    )                                        AS anthropic_cache_hit_rate,
    SUM(CASE WHEN is_failover THEN 1 ELSE 0 END) AS failover_count
FROM llm_requests
WHERE error_code IS NULL
GROUP BY user_id, DATE_TRUNC('month', created_at);

CREATE OR REPLACE VIEW vw_llm_daily_total AS
SELECT
    DATE_TRUNC('day', created_at)   AS day,
    vendor,
    model,
    COUNT(*)                         AS total_calls,
    SUM(cost_usd)                    AS total_cost_usd,
    AVG(latency_ms)::INTEGER         AS avg_latency_ms,
    SUM(CASE WHEN is_failover THEN 1 ELSE 0 END) AS failover_count
FROM llm_requests
WHERE error_code IS NULL
GROUP BY DATE_TRUNC('day', created_at), vendor, model;
```

---

## 7. 환경 변수 (.env)

```bash
# ================================================================
# LLM Gateway 환경 변수
# ================================================================

GOOGLE_AI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

LLM_FREE_CHAT_MODEL=gemini-2.0-flash
LLM_DESIGN_CHAT_MODEL=claude-sonnet-4-6
LLM_C2SC_MODEL=gpt-4.1-mini
LLM_STRATEGY_REVIEW_MODEL=claude-opus-4-6
LLM_CS_MODEL=gemini-2.0-flash

LLM_TIMEOUT_FREE_CHAT=10
LLM_TIMEOUT_DESIGN_CHAT=30
LLM_TIMEOUT_C2SC=10
LLM_TIMEOUT_STRATEGY_REVIEW=60
LLM_TIMEOUT_CS=10

LLM_CIRCUIT_COOLDOWN_SEC=300
LLM_CIRCUIT_FAILURE_THRESHOLD=3

LLM_USER_RPM=10
LLM_USER_DAILY_LIMIT=500

LLM_MONTHLY_BUDGET_USD=100.0
LLM_BUDGET_ALERT_PCT=80
LLM_USER_MONTHLY_WARN_USD=2.0

LLM_BATCH_POLL_INTERVAL_SEC=15
LLM_BATCH_MAX_WAIT_SEC=300

LLM_CACHE_HIT_ALERT_THRESHOLD=0.80
```

---

## 8. 코드베이스 배치 (파일 구조)

```
/root/kis-autotrade-v4/backend/app/
├── core/
│   ├── llm_gateway.py              ← LLMGateway 싱글톤, BaseLLMClient, RouteConfig,
│   │                                  ROUTING_TABLE, FAILOVER_CHAINS, CircuitBreaker,
│   │                                  RateLimiter, BatchQueue
│   ├── llm_cost_tracker.py         ← LLMCostTracker, PriceTier, PRICE_TABLE
│   ├── llm_clients/
│   │   ├── __init__.py
│   │   ├── gemini_client.py        ← GeminiClient (google-genai)
│   │   ├── anthropic_client.py     ← AnthropicClient (cache_control, 배치 API, 캐시 토큰)
│   │   └── openai_client.py        ← OpenAIClient (temp=0.0)
│   └── llm_models.py               ← Pydantic: LLMRequest, LLMResponse, TokenUsage,
│                                      UsageLog, BatchJob, CostSummary, BudgetAlert
├── services/ai/
│   ├── chat_router.py              ← ChatRouter, domain_type→request_type, 사용자 Rate Limit
│   ├── c2sc_engine.py              ← C2SC Engine
│   ├── cs_agent.py                 ← CS Agent (Phase 2)
│   └── prompt_templates/
│       ├── free_chat.txt
│       ├── design_chat.txt
│       ├── c2sc.txt
│       ├── strategy_review.txt
│       └── cs.txt
└── api/v1/
    └── chat.py                     ← POST /api/v1/chat, JWT, ChatRouter
```

---

## 9. 시스템 프롬프트 가드레일

### 9-A. 자유대화 프롬프트 (Gemini 2.0 Flash용)

**파일:** `prompt_templates/free_chat.txt`  
**토큰 추정:** ~850 토큰  
**캐싱:** 미적용 (Gemini, Phase 2에서 Context Caching 검토)

- 역할: MyTrader AI 투자 교육 도우미 "마이트". 투자·금융 교육, 개념 설명.
- 허용: 투자 개념 설명, 전략 유형 교육, 시장 구조, 리스크 관리 원칙, 용어 해설, 서비스 사용법·일상 대화.
- 절대 금지: 종목 추천, 시점 판단, 가격 예측, 설계 모드 전환 권유, 다른 AI인 척.
- 금지 요청 시: "해당 내용은 안내드리기 어렵습니다. 대신 [관련 교육 주제]에 대해 설명드릴 수 있습니다."
- 전환 카드: 키워드("전략 만들", "전략 설계", "백테스트", "모의투자 해보" 등) 포함 시에만 제시. JSON: `{"type":"mode_switch_card","message":"...","button":{"label":"전략 설계 시작하기","action":"switch_to_design_chat"}}`
- 응답 스타일: 한국어, 친근하지만 전문적. 핵심 먼저. 불확실 시 "일반적으로" 한정. 과도한 이모지 금지.
- 법적 고지: 모든 응답 마지막에 "ℹ️ AI가 생성한 답변이며, 투자 조언이 아닙니다."

**테스트 시나리오 (7건):** RSI 설명, 종목/시점 질문 거부, 모멘텀 교육, "전략 만들어보고 싶다"→전환 카드, 프롬프트/규칙 무시 거부, "자동매매가 뭐야?"→전환 카드 미제시, "전략이 뭔지 궁금해"→전환 카드 미제시.

### 9-B. 설계대화 프롬프트 (Sonnet 4.6용)

**파일:** `prompt_templates/design_chat.txt`  
**토큰 추정:** ~950 토큰  
**캐싱:** Anthropic cache_control: {"type": "ephemeral"} 적용

- 역할: 전략 설계 어시스턴트. 파라미터 설정 보조, 의사결정 대신 안 함.
- 허용: 파라미터 의미·범위 안내, 값 되풀이 확인, 누락 필수 입력 요청, 백테스트 결과 객관적 해석.
- 절대 금지: 파라미터 값 추천, 성과 예측, 누락 값 임의 채움, 종목 추천, 전략 좋다/나쁘다 판단.
- 필수 파라미터(저장 조건): Stop-Loss(%), Position Limit(%), Daily Loss Cap(%). 누락 시 "전략을 저장하려면 [누락 항목]을 설정해 주세요."
- 대화 흐름: 전략 의도 파악 → 필수 3개 수집 → 확인 → 전략 카드 JSON 생성 → 최종 확인 요청. confirmed_by_user는 **항상 false** (true는 프론트 [전략 확정] 버튼에서만).
- 전략 카드 JSON: strategy_card with name, type, parameters(indicator, entry_condition, exit_condition, stop_loss_pct, position_limit_pct, daily_loss_cap_pct, additional_params), target_market, confirmed_by_user: false.
- 법적 고지: "ℹ️ AI가 설계를 보조했으며, 모든 투자 판단과 책임은 사용자에게 있습니다."

**테스트 시나리오 (5건):** RSI 모멘텀 요청→범위 안내만, "Stop-Loss 몇 %?"→범위 안내, 2개 입력 후 Daily Loss Cap 요청, "수익률 얼마나 나와?"→예측 거부, 3개 완료 시 카드+confirmed_by_user: false.

### 9-C. C2SC 파싱 프롬프트 (GPT-4.1 mini용)

**파일:** `prompt_templates/c2sc.txt`  
**토큰 추정:** ~700 토큰  
**캐싱:** OpenAI 자동 캐싱 (동일 prefix 시 50% 할인)

- 역할: 전략 코드 변환기. 설계대화 전략 카드 JSON → V4.1 Strategy Engine 호환 설정 JSON.
- 처리 조건: confirmed_by_user: true만 처리. false면 UNCONFIRMED 에러 반환.
- 출력: strategy_config (strategy_id, name, version, engine_type, rules.entry/exit, risk_management, target_market, status: "inactive", created_at) 또는 c2sc_error (code, message, field, suggestion).
- 파싱 규칙: 수치만 변환, 1:1 매핑, 누락 필드 금지, status 항상 "inactive", 필수 리스크 3종 검증.
- 에러 코드: PARSE_FAILED, MISSING_FIELD, AMBIGUOUS_VALUE, UNCONFIRMED. 지원 지표: RSI, MA_CROSS, BOLLINGER, MACD, VOLUME_SPIKE, PRICE_BREAKOUT.

**테스트 시나리오 (5건):** 정상 카드→strategy_config, confirmed false→UNCONFIRMED, stop_loss 누락→MISSING_FIELD, "적당한 타이밍"→AMBIGUOUS_VALUE, 미지원 지표→PARSE_FAILED.

### 9-D. CS 프롬프트 (Phase 2, Gemini 2.0 Flash용)

**파일:** `prompt_templates/cs.txt`  
**토큰 추정:** ~750 토큰  
**상태:** Phase 2 참조용 초안

- 역할: 고객 지원 어시스턴트. 이용 문의, 문제 해결. 투자 질문은 자유대화 안내.
- Tier 1: 계정 설정, 요금·결제, 전략/백테스트/모의 사용법, API 연동, FAQ.
- Tier 2: 결제 오류·환불, 주문 오류, 계좌 연동 실패, 데이터 오류 → 정보 수집 후 에스컬레이션.
- Tier 3: 보안, 법적 문의, 대규모 자금 → 즉시 에스컬레이션. 에스컬레이션 JSON 형식 정의.
- 금지: 투자 조언, 개인정보 조회, 규칙 해제, 보상/환불 직접 약속.
- 법적 고지: "ℹ️ AI 어시스턴트가 응답했습니다. 추가 도움이 필요하시면 고객센터(support@mytrader.ai)로 문의해 주세요."

---

## 10. 비용 시뮬레이션 (100명 기준)

### 10-1. 사용 패턴 가정

| 항목 | 가정값 | 근거 |
|------|-------|------|
| 총 사용자 수 | 100명 | MVP 목표 |
| DAU | 30명 (30%) | 핀테크 앱 평균 |
| 사용자당 일간 자유대화 | 5회 | 교육적 대화 평균 |
| 설계대화 활성 | DAU 30% = 9명 | 전략 설계 수요 |
| 사용자당 일간 설계대화 | 1회 | 설계는 집중 작업 |
| 사용자당 월간 C2SC | 2회 | 전략 생성 시에만 |
| 사용자당 월간 전략 검증 | 2회 | 전략 확정 전 검증 |

**대화당 평균 토큰:** 자유대화 500 in / 600 out, 설계대화 800 / 1,000, C2SC 600 / 400, 전략 검증 2,000 / 3,000.

### 10-2. 월간 호출 수

| 도메인 | 산식 | 월간 호출 |
|--------|------|----------|
| 자유대화 | 30×5×30 | 4,500 |
| 설계대화 | 9×1×30 | 270 |
| C2SC | 100×2 | 200 |
| 전략 검증 | 100×2 | 200 |
| **합계** | | **5,170** |

### 10-3. 도메인별 월간 비용 (USD)

- **자유대화 (Gemini):** Input $0.225 + Output $1.080 = **$1.305**
- **설계대화 (Sonnet 4.6+캐싱):** 캐시 생성/히트 + 사용자 Input/Output = **$4.939** (캐싱 미적용 시 $5.468, 약 9.7% 절감)
- **C2SC (GPT-4.1 mini):** **$0.176**
- **전략 검증 (Opus 4.6 배치 50%):** **$8.500** (배치 미적용 시 $17.000)

### 10-4. 월간 총합

| 도메인 | 모델 | USD | KRW (₩1,450/$) | 비중 |
|--------|------|-----|-----------------|------|
| 자유대화 | Gemini 2.0 Flash | $1.31 | ₩1,900 | 8.8% |
| 설계대화 | Sonnet 4.6 | $4.94 | ₩7,163 | 33.1% |
| C2SC | GPT-4.1 mini | $0.18 | ₩261 | 1.2% |
| 전략 검증 | Opus 4.6 (배치) | $8.50 | ₩12,325 | 56.9% |
| **합계** | | **$14.93** | **₩21,649** | **100%** |

### 10-5. 핵심 지표

| 지표 | 값 |
|------|-----|
| 사용자당 월 비용 | $0.149 (≈₩216) |
| 100명 기준 월 총비용 | $14.93 (≈₩21,649) |
| 확정 목표 대비 | 목표 ₩90,000 → 실제 ₩21,649 **(목표의 24%)** |
| 최대 수용 규모 (₩9만 한도) | ~416명 (현재 가정 기준) |

### 10-6. 민감도 분석

전략 검증 빈도 2×/3×, 배치 미적용, 캐싱 미적용 등 시나리오별 월 비용·사용자당 비용 산출. 최악 시나리오에서도 ₩58,700으로 목표 ₩90,000의 65%.

---

## 11. 미결 사항 & Phase 2 로드맵

### 11-1. 미결 사항 (MVP 전 해결 필요)

| # | 항목 | 상태 | 해결 방안 |
|---|------|------|----------|
| 1 | Sonnet 4.6 안정성 | 2~3주 관찰 중 | .env에서 claude-sonnet-4-5로 즉시 폴백 가능 |
| 2 | GPT-4.1 mini 한국어 C2SC 정확도 | 테스트 미실시 | 50건 한국어 전략 카드 테스트, 95% 미만 시 Sonnet 4.6 대체 |
| 3 | Gemini 2.0 Flash 한국어 품질 | 테스트 미실시 | 50건 A/B (Gemini vs Haiku 4.5), 미달 시 Haiku 전환 |
| 4 | strategy_review 프롬프트 | 초안 미작성 | 전략 엔진 설계 확정 후 작성 |

### 11-2. Phase 2 로드맵

| # | 항목 | 내용 | 예상 효과 |
|---|------|------|-----------|
| 1 | 멀티턴 대화 히스토리 캐싱 | Anthropic cache_control 대화 prefix 적용 | 설계대화 20~30% 추가 절감 |
| 2 | Gemini Context Caching | 자유대화 시스템 프롬프트 캐시 | 자유대화 입력 90% 절감 |
| 3 | CS 도메인 가동 | cs_agent.py + cs.txt 활성화 | 고객 문의 자동 응대 |
| 4 | 라우팅 설정 DB화 | llm_routing_config 테이블, 관리자 UI | 재시작 없이 모델 전환 |
| 5 | A/B 테스트 프레임워크 | 비율 기반 이중 모델 분배 | 품질·비용 비교 데이터 |
| 6 | Redis Queue 전환 | BatchQueue → Redis | 다중 워커, 장애 복구 |

---

## 12. Cursor 구현 지시서 초안

> **⚠️ OPUS-MAIN-v1 최종 검토 후 발행**

```
================================================================
CURSOR 지시서: LLM Gateway + Cost Tracker 구현
================================================================

■ 메타 정보
- 지시서 ID: CUR-LLM-GATEWAY-v1
- 우선순위: P0 (MVP 핵심)
- 선행 조건: DB 마이그레이션 (llm_requests, llm_cost_daily)
- 참조 문서: OPUS-LLM-AI-v1-FULL-SPEC v2.1.1
- 대상 디렉토리: /root/kis-autotrade-v4/backend/app/

■ 절대 규칙
- 레거시 48개 테이블 SELECT-only (변경 금지)
- 파일 변경 시 .bak_YYYYMMDD_HHMMSS 백업 + MD5 기록
- 단계별 보고 (각 STEP 완료 시)
- git commit: [V4.1] feat/fix: 설명 - YYYYMMDD
- 서비스 상태 확인: systemctl status kis-v41-api

================================================================

【STEP 1】 DB 마이그레이션
Alembic 마이그레이션. llm_requests + 인덱스 4개, llm_cost_daily + 인덱스 2개,
vw_llm_user_monthly, vw_llm_daily_total 뷰. 실행 전 SQL 전문 보고 → 리뷰 승인 후 실행.

【STEP 2】 Pydantic 모델 (core/llm_models.py)
LLMRequest, LLMResponse, TokenUsage, RouteConfig, PriceTier, UsageLog,
BatchJob, CostSummary, BudgetAlert. 설계서 4-D 필드 그대로. user_id: int (BIGINT).

【STEP 3】 BaseLLMClient (core/llm_gateway.py)
ABC. send(), parse_response(), count_tokens(). 모든 메서드 async.

【STEP 4】 GeminiClient (core/llm_clients/gemini_client.py)
google-genai SDK. send() 형식 변환, parse_response(), count_tokens() usage_metadata.

【STEP 5】 AnthropicClient (core/llm_clients/anthropic_client.py)
anthropic SDK async. cache_control 조건부 적용 (cache_enabled=True 시).
system에 cache_control: {"type": "ephemeral"}. 응답에서 cache_creation_input_tokens,
cache_read_input_tokens → TokenUsage. 배치 API create_message_batch, retrieve_message_batch.

【STEP 6】 OpenAIClient (core/llm_clients/openai_client.py)
openai SDK async. temperature=0.0. response_format 미지정.

【STEP 7】 RateLimiter
Token Bucket, asyncio. 벤더별 인스턴스. try_acquire(vendor, estimated_tokens). 실패 시 100ms×3회.

【STEP 8】 CircuitBreaker
CLOSED/OPEN/HALF_OPEN. failure_count 5분 윈도우, threshold 3, cooldown 300s. trip(), check(), reset(), is_available().

【STEP 9】 LLMGateway 싱글톤
lifespan 초기화. send(): route → rate limit → circuit → client.send() → (실패 시 failover) → cost record.
send_batch(): BatchQueue enqueue → 즉시 응답. _execute_with_failover() 폴백 체인 순회.

【STEP 10】 LLMCostTracker (core/llm_cost_tracker.py)
record(): 비용 계산 + DB INSERT (llm_requests). calc_cost(): 4-J 공식. 캐시 히트 90% 절감, 배치 50% 할인.
check_budget(): 월간 합계 → 알림. aggregate_daily(): 크론 일별 집계.

（이하 STEP 11 이후 OPUS-MAIN-v1 지시서에서 계속）
```

---

## 13. 변경 이력

| 버전 | 일자 | 변경 내용 |
|------|------|----------|
| v2.0 | 2026-02-19 | v2 보고서 통합 |
| v2.1 | 2026-02-2x | 수정 반영 |
| v2.1.1 | 2026-02-23 | 마이크로 수정, 최종 통합본 |
