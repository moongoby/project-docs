# GO100 AI 주식자동매매 시스템 기술 문서

**문서 유형**: 시스템 정밀 분석 보고서
**작성일**: 2026-02-22
**대상 시스템**: GO100 (고백) V4.1 AI 전략 플랫폼
**서버**: 211.188.51.113 (211서버)
**도메인**: https://go100.newtalk.kr

---

## 목차

1. [시스템 개요](#1-시스템-개요)
2. [아키텍처 총괄](#2-아키텍처-총괄)
3. [백엔드 서비스 구조](#3-백엔드-서비스-구조)
4. [AI/LLM 파이프라인](#4-aillm-파이프라인)
5. [백테스트 엔진](#5-백테스트-엔진)
6. [종목 유니버스 엔진](#6-종목-유니버스-엔진)
7. [리스크 관리](#7-리스크-관리)
8. [모의매매 / 실매매](#8-모의매매--실매매)
9. [최적화 엔진](#9-최적화-엔진)
10. [API 엔드포인트 전수](#10-api-엔드포인트-전수)
11. [데이터베이스 스키마](#11-데이터베이스-스키마)
12. [데이터 파이프라인](#12-데이터-파이프라인)
13. [프론트엔드 아키텍처](#13-프론트엔드-아키텍처)
14. [인프라 및 배포](#14-인프라-및-배포)
15. [보안 아키텍처](#15-보안-아키텍처)
16. [운영 현황](#16-운영-현황)

---

## 1. 시스템 개요

### 1.1 플랫폼 정의

GO100은 **AI 기반 주식 자동매매 전략 플랫폼**으로, 사용자가 자연어로 투자 전략을 설명하면 AI가 전략을 설계하고, 백테스트로 검증한 후, 모의매매와 실매매까지 자동 실행하는 풀스택 시스템이다.

### 1.2 핵심 수치

| 항목 | 값 |
|------|-----|
| 백엔드 GO100 코드 | **15,631 LOC** (Python) |
| 프론트엔드 GO100 코드 | **3,965 LOC** (TypeScript/React) |
| 서비스 모듈 | **10개** |
| API 엔드포인트 | **34+개** (10 라우터) |
| 단위 테스트 | **141건** (100% PASSED) |
| GO100 전용 DB 테이블 | **10개** |
| 참조 V4.1 데이터 테이블 | **11개** |
| GO100 전략 카드 | 15개 (LLM 14, CUSTOM 1) |
| 일봉 OHLCV 데이터 | 2,596,548행 (3,844종목) |
| 분봉 OHLCV 데이터 | 18,395,750행 (499종목) |

### 1.3 전략 카드 생애주기

```
IDEA → DRAFT → BACKTESTED → PAPER_LIVE → LIVE → PAUSED → RETIRED
 💡      📝       📊           🧪         🟢      ⏸️       🔴
```

| 상태 | 현재 카드수 | 설명 |
|------|-----------|------|
| DRAFT | 5 | 초안 (백테스트 전) |
| BACKTESTED | 6 | 백테스트 완료 |
| PAPER_LIVE | 3 | 모의매매 중 |
| LIVE | 1 | 실매매 중 |

---

## 2. 아키텍처 총괄

### 2.1 전체 시스템 구성도

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                              │
│           https://go100.newtalk.kr                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS (SSL/TLS)
┌──────────────────────▼──────────────────────────────────────────┐
│                    NGINX REVERSE PROXY                           │
│  /api/*     → 127.0.0.1:8002  (GO100 FastAPI)                  │
│  /          → 127.0.0.1:3000  (Next.js 14 Frontend)            │
│  /_next/hmr → 127.0.0.1:3000  (WebSocket HMR)                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌───────────────────┐      ┌───────────────────┐
│ GO100 API (8002)  │      │ Next.js FE (3000) │
│ FastAPI + uvicorn │      │ React 18 + SSR    │
│ 2 workers         │      │ App Router        │
│ 10 routers        │      │ go100Api.ts       │
│ 10 services       │      │ 9 hooks           │
│ 141 tests         │      │ 20+ components    │
└───────┬───────────┘      └───────────────────┘
        │
        ├── V4.1 인프라 재사용 (읽기전용)
        │   ├── LLMGateway (Claude/Gemini/GPT-4)
        │   ├── V4OrderExecutor (KIS API)
        │   ├── BrokerFactory
        │   └── AccountSyncManager
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                    PostgreSQL 16 (kisautotrade)                   │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ GO100 테이블    │  │ V4.1 핵심     │  │ 시장 데이터      │  │
│  │ 10 tables       │  │ strategy_cards │  │ ohlcv_daily      │  │
│  │ (824 KB)        │  │ v4_positions   │  │ v4_ohlcv_minute  │  │
│  │                 │  │ v4_signals     │  │ stock_universe   │  │
│  └─────────────────┘  └────────────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                    외부 API 연동                                  │
│  KIS OpenAPI (주문/잔고)  │  Claude/Gemini/GPT-4 (전략설계)     │
│  Virtual: openapivts...   │  Anthropic SDK + Google AI SDK      │
│  Real: openapi...         │  Circuit Breaker + Failover Chain   │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 서비스 상태

| 서비스 | 포트 | systemd | 상태 |
|--------|------|---------|------|
| GO100 API | 8002 | go100.service | **active** |
| GO100 Frontend | 3000 | go100-frontend.service | **active** |
| V4.1 API | 8003 | kis-v41-api.service | **active** |
| V4.1 Scheduler | — | kis-v41-scheduler.service | **active** |
| V4.1 Monitor | — | kis-v41-monitor.service | **active** |
| V4.1 Minute Collector | — | kis-v41-minute-collector | **inactive** (타이머 기반) |

---

## 3. 백엔드 서비스 구조

### 3.1 디렉토리 레이아웃

```
backend/app/services/go100/
├── ai/                 # AI/LLM 에이전트 파이프라인
│   ├── base_orchestrator.py   (716 LOC)  # 전체 파이프라인 오케스트레이터
│   ├── understand_agent.py               # 의도 분석 에이전트
│   ├── design_agent.py                   # 전략 설계 에이전트
│   ├── evaluate_agent.py                 # 평가 에이전트
│   ├── optimize_agent.py                 # 최적화 에이전트
│   ├── llm_client.py                     # LLM API 클라이언트
│   └── schemas.py                        # Pydantic 모델
│
├── backtest/           # 백테스트 시뮬레이션 엔진
│   ├── simulator.py           (374 LOC)  # 일봉 시뮬레이터
│   ├── minute_simulator.py    (396 LOC)  # 분봉 시뮬레이터 + 분할익절
│   ├── signal_evaluator.py    (213 LOC)  # entry/exit 시그널 평가
│   ├── data_loader.py                    # OHLCV 데이터 로더
│   ├── partial_exit_simulator.py (253 LOC) # 분할익절 시뮬레이터
│   └── backtest_service.py               # 백테스트 서비스 퍼사드
│
├── universe/           # 종목 선정 엔진
│   ├── engine.py              (75 LOC)   # 7개 기본 필터 유니버스
│   ├── advanced_filters.py    (710 LOC)  # 12개 고급 필터
│   └── data_cache.py                     # 데이터 캐싱
│
├── strategy/           # 전략 카드 관리
│   └── card_service.py        (434 LOC)  # CRUD + 상태전이 + 마켓플레이스
│
├── portfolio/          # 포트폴리오 관리
│   └── portfolio_service.py   (403 LOC)  # CRUD + 포지션 조회
│
├── paper_trading/      # 모의매매
│   ├── paper_service.py       (431 LOC)  # 서비스 퍼사드
│   ├── paper_engine.py        (657 LOC)  # 일일 시뮬레이션 엔진
│   └── paper_scheduler.py                # 자동 실행 스케줄러
│
├── live_trading/       # 실매매
│   ├── live_service.py        (278 LOC)  # 서비스 퍼사드
│   └── live_engine.py         (650 LOC)  # KIS 주문 실행 엔진
│
├── risk/               # 리스크 관리
│   └── position_sizing.py     (315 LOC)  # 포지션 사이징 + 면책동의
│
├── scheduler/          # 스케줄러
│   └── go100_scheduler.py     (221 LOC)  # Paper/Live 일괄 실행
│
└── optimizer/          # 최적화 엔진 (BUNDLE4D)
    ├── fit_engine.py          (370 LOC)  # 종목×전략 적합도
    ├── optimizer_service.py   (310 LOC)  # 서비스 퍼사드
    └── schemas.py             (93 LOC)   # Pydantic 모델
```

### 3.2 핵심 클래스 요약

| 클래스 | 모듈 | 핵심 책임 |
|--------|------|----------|
| `BaseOrchestrator` | ai/ | UNDERSTAND→DESIGN→BACKTEST→EVALUATE→OPTIMIZE 전체 루프 |
| `BacktestSimulator` | backtest/ | 일봉 인메모리 백테스트 (유니버스 리프레시, 포지션 관리) |
| `Go100MinuteSimulator` | backtest/ | 분봉 백테스트 + N분봉 집계 + 분할익절 |
| `SignalEvaluator` | backtest/ | 4종류 entry + 5종류 exit 시그널 판정 |
| `Go100AdvancedFilters` | universe/ | 12개 고급 필터 + 전략유형별 파이프라인 |
| `Go100StrategyCardService` | strategy/ | 카드 CRUD + 6단계 상태전이 검증 |
| `Go100PaperTradingEngine` | paper_trading/ | 일일 모의매매 (entry/exit + 수수료/세금) |
| `Go100LiveTradingEngine` | live_trading/ | KIS 실매매 + 계좌 잔고 조회 |
| `Go100PositionSizingManager` | risk/ | 3-tier 포지션 사이징 + 면책동의 |
| `StockStrategyFitEngine` | optimizer/ | 종목별 백테스트 → fit_score 산출 |
| `Go100OptimizerService` | optimizer/ | 청산 그리드서치 + 멀티데스크 배분 |

---

## 4. AI/LLM 파이프라인

### 4.1 오케스트레이션 흐름

```
사용자 자연어 입력
        │
┌───────▼───────────────────────────────────────────┐
│ 1. UNDERSTAND Agent                                │
│    입력: user_message + conversation_history       │
│    출력: UserIntent {                              │
│      investment_style: SCALPING|DAY_TRADING|SWING  │
│      risk_tolerance: very_low~very_high           │
│      target_sectors: [string]                      │
│      experience_level: string                      │
│      confidence: float (0~1)                       │
│    }                                               │
│    판단: confidence < 0.6 → 추가 질문 요청         │
└───────┬───────────────────────────────────────────┘
        │ (confidence ≥ 0.6)
┌───────▼───────────────────────────────────────────┐
│ 2. DESIGN Agent                                    │
│    입력: UserIntent + user_message                 │
│    출력: StrategyDesign {                          │
│      strategy_name, universe_filter,               │
│      entry_rules[], exit_rules[], risk_params{},   │
│      max_stocks                                    │
│    }                                               │
│    안전장치: stop_loss 필수, max_stocks 3~10 제한  │
└───────┬───────────────────────────────────────────┘
        │
┌───────▼───────────────────────────────────────────┐
│ 3. BACKTEST LOOP (최대 6회)                        │
│    ┌─────────────────────────────────┐             │
│    │ A. 분봉 우선 백테스트            │             │
│    │    AdvancedFilters → 분봉교집합  │             │
│    │    ≥5종목 → MinuteSimulator     │             │
│    │    <5종목 → 일봉 폴백           │             │
│    └──────────┬──────────────────────┘             │
│    ┌──────────▼──────────────────────┐             │
│    │ B. EVALUATE Agent               │             │
│    │    4 메트릭 vs 리스크 허용범위   │             │
│    │    3/4 통과 → passed=true        │             │
│    │    점수 = 25pt × 통과 메트릭     │             │
│    └──────────┬──────────────────────┘             │
│    ┌──────────▼──────────────────────┐             │
│    │ C. OPTIMIZE Agent (미통과 시)    │             │
│    │    LLM 파라미터 조정 제안        │             │
│    │    반복당 최대 3개 파라미터 변경  │             │
│    │    stop_loss 제거 불가           │             │
│    └─────────────────────────────────┘             │
└───────┬───────────────────────────────────────────┘
        │
┌───────▼───────────────────────────────────────────┐
│ 4. FINALIZE → BACKTESTED 상태 확정                 │
│    전략 유형 태그: [스캘핑] / [데일리] / [단기스윙] │
│    백테스트 결과 캐시 저장                          │
└───────────────────────────────────────────────────┘
```

### 4.2 LLM Gateway 라우팅

| 요청 유형 | 1차 모델 | Failover | 최대 토큰 | 타임아웃 |
|-----------|---------|----------|----------|---------|
| free_chat | Gemini 2.5 Flash | Claude Haiku | 4,096 | 30s |
| design_chat | Claude Sonnet 4.6 | Claude Sonnet 4.5 | 4,096 | 60s |
| strategy_review | Claude Opus 4.6 | Claude Sonnet 4.6 | 8,192 | 60s |

- **Circuit Breaker**: 벤더당 3회 실패/300초 → OPEN → 쿨다운 후 HALF_OPEN
- **비용 추적**: 월 $100 예산, 사용자당 $2.0 경고 임계값

### 4.3 전략 유형 판별 (3단계 폴백)

```python
1순위: risk_params.strategy_type (LLM 명시)
2순위: UserIntent.investment_style 매핑
3순위: max_holding_days (≤1=scalping, ≤5=daily, >5=swing)
기본값: "daily"
```

---

## 5. 백테스트 엔진

### 5.1 일봉 시뮬레이터 (`BacktestSimulator`)

- **데이터 소스**: ohlcv_daily (varchar(8) YYYYMMDD)
- **MA 계산 여유**: 시작일 -120일 데이터 로드
- **유니버스 갱신**: weekly/monthly 단위
- **수수료**: 0.015% (매수/매도 양방향)
- **세금**: 0.18% (매도 시)
- **포지션 관리**: max_stocks 제한, max_position_pct 비중 제한

```
매 거래일:
  1. 유니버스 갱신 (주간/월간)
  2. 보유 종목 exit 평가 (stop_loss, take_profit, trailing_stop, signal, holding_days)
  3. 신규 진입 평가 (ma_cross, rsi_threshold, price_breakout, volume_surge)
  4. 일일 equity 기록
  5. 마지막 날 미청산 포지션 강제 청산
```

### 5.2 분봉 시뮬레이터 (`Go100MinuteSimulator`)

- **데이터 소스**: v4_ohlcv_minute (월별 파티션)
- **N분봉 집계**: 3분/5분 bar 자동 생성
- **분할익절**: PartialExitSimulator (3단계: 20%/30%/50% 물량 매도)
- **우선순위**: 분봉 종목 ≥5개 → 분봉 백테스트, <5개 → 일봉 폴백
- **bar_interval 기본값**: scalping=3분, daily=3분, swing=5분

### 5.3 시그널 평가기 (`SignalEvaluator`)

**진입 조건 (4종류)**:

| 타입 | 파라미터 | 판정 기준 |
|------|---------|----------|
| `ma_cross` | short, long, direction | 최근 3일 내 골든/데드 크로스 |
| `rsi_threshold` | period, operator, value | RSI </>/<=/>=  값 |
| `price_breakout` | period, direction | N일 고가/저가 돌파 + 방향 확인 |
| `volume_surge` | ratio, period | 당일 거래량 ≥ N일 평균 × ratio |

**청산 조건 (5종류)**:

| 타입 | 판정 기준 |
|------|----------|
| `stop_loss` | (현재가/매수가 - 1) × 100 ≤ -pct% |
| `profit_target` | (현재가/매수가 - 1) × 100 ≥ pct% |
| `trailing_stop` | (현재가/최고가 - 1) × 100 ≤ -pct% |
| `holding_days` | (현재일 - 매수일).days ≥ max |
| `ma_cross` | 데드크로스 (구현 보류) |

### 5.4 성과 지표 계산

| 지표 | 산출 방식 |
|------|----------|
| Total Return | (최종 equity / 초기 자본 - 1) × 100 |
| Annual Return | 복리 연율화: (final/initial)^(365/days) - 1 |
| Max Drawdown | peak-to-trough 최대 하락 % (음수) |
| Sharpe Ratio | 일간수익률 평균 / 표준편차 × √252 |
| Win Rate | 수익 거래 / 전체 거래 × 100 |
| Profit Factor | 총 수익 / |총 손실| |
| Avg Holding Days | 거래별 보유일수 평균 |

---

## 6. 종목 유니버스 엔진

### 6.1 기본 필터 (`UniverseEngine`, 7종)

| 필터 | 데이터 소스 | 기준 |
|------|------------|------|
| ScopeFilter | stock_universe | KOSPI/KOSDAQ 시장, 섹터, ETF 제외 |
| PriceFilter | ohlcv_daily | 가격 범위 (min/max) |
| VolumeFilter | ohlcv_daily | 일 거래량 하한 |
| MarketCapFilter | **stock_fundamentals** | 시가총액 (stock_universe는 NULL) |
| MovingAverageFilter | ohlcv_daily | MA 크로스오버 |
| RSIFilter | ohlcv_daily | RSI 과매수/과매도 |
| FundamentalFilter | stock_universe | PER, PBR, 배당수익률 |

### 6.2 고급 필터 (`Go100AdvancedFilters`, 12종)

| # | 필터 | 데이터 소스 | 전략유형 |
|---|------|------------|---------|
| 1 | 시가총액 | stock_fundamentals | 스캘핑/데일리/스윙 |
| 2 | 거래대금 | ohlcv_daily (close×volume) | 스캘핑/데일리 |
| 3 | 일중 변동성 | ohlcv_daily (H-L)/C% | 스캘핑 |
| 4 | 외인/기관 수급 | v4_investor_daily | 데일리/스윙 |
| 5 | 가격 모멘텀 | ohlcv_daily | 스윙 |
| 6 | RSI 과매도 | ohlcv_daily | 데일리 |
| 7 | 섹터 로테이션 | v4_sector_daily | 스윙 |
| 8 | 분봉 데이터 보유 | v4_ohlcv_minute | 스캘핑/데일리 |
| 9 | 신저가 제외 | ohlcv_daily | 스캘핑 |
| 10 | PER 양수 | stock_fundamentals | 데일리 |
| 11 | 거래정지 제외 | ohlcv_daily | 전체 |
| 12 | 재무건전성 | financial_ratios | 스윙 |

### 6.3 전략유형별 파이프라인

| 유형 | 필터 조합 (AND 교집합) |
|------|----------------------|
| **스캘핑** | 분봉보유 ∩ 시가총액(5000억+) ∩ 변동성(2%+) ∩ 거래정지제외 |
| **데일리** | 시가총액 ∩ 거래대금 ∩ PER양수 ∩ 수급 |
| **스윙** | 시가총액 ∩ 섹터모멘텀 ∩ 재무건전성 |

---

## 7. 리스크 관리

### 7.1 포지션 사이징 (`Go100PositionSizingManager`)

**3-Tier 우선순위**:
```
시스템 기본값 (DEFAULT_RISK_PROFILES)
    ↓ override
카드 risk_params (전략 정의)
    ↓ override
사용자 직접 설정
```

### 7.2 리스크 허용 수준 프로파일

| 수준 | max_position_pct | max_stocks | max_invested | stop_loss | slippage |
|------|-----------------|-----------|-------------|-----------|----------|
| very_low | 15% | 10 | 70% | -5% | 10 bps |
| low | 20% | 7 | 80% | -7% | 10 bps |
| **medium** | **30%** | **5** | **90%** | **-10%** | **10 bps** |
| high | 50% | 3 | 95% | -15% | 15 bps |
| very_high | 70% | 2 | 100% | -20% | 20 bps |

### 7.3 안전 가드레일

- **stop_loss 필수**: None/0/양수 불가 → 자동 복원
- **max_stocks**: 1~100 범위 강제
- **max_position_pct**: ≤100% 강제
- **면책동의**: 프로파일 기본값 초과 설정 시 사용자 동의 필수
- **동시 보유 한도**: max_concurrent_positions (기본 10)
- **일일 진입 한도**: max_daily_entries (기본 20)
- **자본 사용률 상한**: max_capital_usage_pct (기본 80%)
- **단일 포지션 비중**: max_single_position_pct (기본 10%)

---

## 8. 모의매매 / 실매매

### 8.1 모의매매 (`Go100PaperTradingEngine`)

```
┌─────────────────────────────────────────────────────┐
│  start() → Portfolio 생성 (is_paper=true)            │
│          → Card PAPER_LIVE 전이                      │
└───────┬─────────────────────────────────────────────┘
        │ (매일 자동 또는 수동 run-now)
┌───────▼─────────────────────────────────────────────┐
│  run_one_day():                                      │
│    1. entry/exit rules 로드                          │
│    2. 보유 포지션 exit 평가                          │
│    3. 신규 진입 평가                                 │
│    4. 시뮬레이션 주문 (수수료 0.015%, 세금 0.18%)    │
│    5. go100_positions/trades/snapshots 업데이트       │
│    6. equity curve 기록                              │
└─────────────────────────────────────────────────────┘
```

### 8.2 실매매 (`Go100LiveTradingEngine`)

```
┌─────────────────────────────────────────────────────┐
│  start() → Portfolio 생성 (is_live=true)             │
│          → disclaimer_agreed 확인                    │
│          → Card LIVE 전이                            │
└───────┬─────────────────────────────────────────────┘
        │ (매일 자동 또는 수동 run-now)
┌───────▼─────────────────────────────────────────────┐
│  run_one_day():                                      │
│    1. KIS 계좌 잔고 조회 (get_balance)               │
│    2. entry/exit rules + risk_params 로드            │
│    3. 보유 포지션 exit 평가 → V4OrderExecutor.sell   │
│    4. 신규 진입 평가 → V4OrderExecutor.buy           │
│    5. 주문 확인 + 체결 대기                          │
│    6. go100_positions/trades 업데이트                 │
│    7. 잔고 재확인                                    │
└─────────────────────────────────────────────────────┘
```

### 8.3 계좌 조정 (Reconciliation)

- 시스템 포지션 vs KIS 브로커 실제 잔고 비교
- 불일치 감지: 외부 매수/매도, 수량 차이, 현금 차이
- 상태: OK / DETECTED / USER_CONFIRMED / AUTO_ADJUSTED
- go100_account_reconciliation 테이블에 기록

### 8.4 KIS 브로커 연동

| 구분 | Virtual (모의) | Real (실전) |
|------|---------------|------------|
| Base URL | openapivts.koreainvestment.com:29443 | openapi.koreainvestment.com:9443 |
| TR_ID 접두사 | VTTC | TTTC |
| config_id | 3 | 4 |
| is_production | false | true |

---

## 9. 최적화 엔진

### 9.1 종목×전략 적합도 (`StockStrategyFitEngine`)

1. 카드 로드 → strategy_type 판별
2. AdvancedFilters.build_universe → 종목 후보 (최대 200)
3. OHLCV bulk SELECT 1회 → stock_code별 dict 인덱싱
4. 종목당 인메모리 백테스트 (SignalEvaluator 재사용)
5. fit_score 6지표 가중합 산출

**fit_score 공식**:
```
return(0~30%) × 0.25
+ win_rate(30~70%) × 0.15
+ profit_factor(0.5~3.0) × 0.20
+ mdd(-30~0%) × 0.15
+ sharpe(0~2.0) × 0.15
+ trades(0~20) × 0.10
```

### 9.2 청산 파라미터 그리드 서치

| 전략 유형 | SL 그리드 | TP 그리드 | TS 그리드 | 조합수 |
|-----------|----------|----------|----------|--------|
| scalping | [1, 1.5, 2, 3] | [1.5, 2, 3, 5] | [1, 1.5, 2] | **96** |
| daily | [2, 3, 5] | [5, 8, 10, 15] | [2, 3, 5] | **108** |
| swing | [3, 5, 7] | [10, 15, 20, 30] | [3, 5, 7] | **108** |

**랭킹**: `sharpe × 0.4 + profit_factor × 0.3 + return/100 × 0.3`

### 9.3 멀티 데스크 자금 배분

- 양수 Sharpe 비율 가중 배분 (음수 Sharpe → 0% 배분)
- 종목 중복 해소: fit_score 최고 카드에 할당
- go100_desk_allocation 테이블에 결과 저장

---

## 10. API 엔드포인트 전수

### 10.1 전략 카드 (`/api/go100/strategy-cards`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/` | 전략 카드 생성 |
| GET | `/` | 카드 목록 (page, page_size, status, source_type) |
| GET | `/{card_id}` | 카드 상세 조회 |
| PUT | `/{card_id}` | 카드 수정 (LIVE 시 제한) |
| DELETE | `/{card_id}` | 카드 비활성화 |
| POST | `/{card_id}/transition` | 상태 전이 |

### 10.2 마켓플레이스 (`/api/go100/store`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 시스템 전략 목록 |
| POST | `/subscribe` | 시스템 전략 복제 구독 |

### 10.3 포트폴리오 (`/api/go100/portfolios`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/` | 포트폴리오 생성 |
| GET | `/` | 목록 (portfolio_type=PAPER/LIVE) |
| GET | `/{id}` | 상세 조회 |
| PUT | `/{id}` | 수정 |
| DELETE | `/{id}` | 비활성화 |
| GET | `/{id}/positions` | 포지션 목록 (status=OPEN/CLOSED) |
| GET | `/{id}/summary` | 성과 요약 |

### 10.4 백테스트 (`/api/go100/backtest`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/run` | 백테스트 실행 (동기, 300s 타임아웃) |
| GET | `/` | 실행 이력 목록 |
| GET | `/{run_id}` | 결과 조회 |

### 10.5 AI Chat (`/api/go100/ai`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/chat` | 전체 파이프라인 (UNDERSTAND→PRESENT) |
| POST | `/understand` | 의도 분석 단독 |
| POST | `/design` | 전략 설계 단독 |
| POST | `/evaluate` | 평가 단독 |
| POST | `/optimize` | 최적화 단독 |

### 10.6 모의매매 (`/api/go100/paper-trading`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/start` | 모의매매 시작 |
| GET | `/` | 모의 포트폴리오 목록 |
| GET | `/{id}` | 상태 조회 |
| POST | `/{id}/pause` | 일시 중지 |
| POST | `/{id}/resume` | 재개 |
| POST | `/{id}/stop` | 중단 (전 포지션 청산) |
| POST | `/{id}/run-now` | 수동 실행 |
| GET | `/{id}/positions` | 보유 종목 |
| GET | `/{id}/trades` | 거래 내역 |
| GET | `/{id}/snapshots` | 일별 스냅샷 |

### 10.7 실매매 (`/api/go100/live-trading`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/start` | 실매매 시작 |
| GET | `/` | 실매매 포트폴리오 목록 |
| GET | `/{id}` | 상태 조회 |
| POST | `/{id}/pause` | 일시 중지 |
| POST | `/{id}/resume` | 재개 |
| POST | `/{id}/stop` | 중단 |
| POST | `/{id}/run-now` | 수동 실행 (dry_run 파라미터) |
| POST | `/{id}/reconcile` | 계좌 조정 |

### 10.8 리스크 (`/api/go100/risk`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/defaults/{level}` | 리스크 수준별 기본값 |
| GET | `/effective` | 유효 설정 미리보기 (3-tier 병합) |
| POST | `/disclaimer` | 면책 동의 기록 |
| GET | `/disclaimers` | 면책 이력 조회 |

### 10.9 스케줄러 (`/api/go100/scheduler`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/run-live` | 전체 실매매 일괄 실행 |
| POST | `/run-paper` | 전체 모의매매 일괄 실행 |
| POST | `/reconcile` | 전체 계좌 조정 |
| GET | `/status` | 스케줄러 상태 |

### 10.10 최적화 (`/api/go100/optimizer`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/fit-analysis` | 종목×전략 적합도 분석 |
| GET | `/fit-analysis/{card_id}` | 저장된 결과 조회 |
| POST | `/exit-optimize` | 청산 파라미터 그리드 서치 |
| POST | `/desk-allocation` | 멀티 데스크 자금 배분 |
| GET | `/desk-allocation/{id}` | 저장된 배분 조회 |

**전체 인증**: JWT Bearer Token (`get_current_user` 의존성 주입)

---

## 11. 데이터베이스 스키마

### 11.1 GO100 전용 테이블 (10개, 824 KB)

#### go100_strategy_cards (전략 카드)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| go100_card_id | BIGSERIAL PK | 카드 고유 ID |
| user_id | INTEGER FK | 소유자 |
| account_id | INTEGER FK | 연결 계좌 |
| strategy_name | VARCHAR(200) | 전략명 |
| strategy_type | VARCHAR(20) | CUSTOM/BUILTIN/LLM_GENERATED/SUBSCRIBED |
| universe_filter | JSONB | 종목 선정 필터 |
| entry_rules | JSONB | 진입 조건 배열 |
| exit_rules | JSONB | 청산 조건 배열 |
| risk_params | JSONB | 리스크 파라미터 |
| max_stocks | INTEGER | 최대 동시 보유 |
| card_status | VARCHAR(20) | IDEA/DRAFT/BACKTESTED/PAPER_LIVE/LIVE/PAUSED/RETIRED |
| source_type | VARCHAR(20) | SYSTEM/CUSTOM/LLM/SHARED |
| last_backtest_return | NUMERIC(10,4) | 최근 백테스트 수익률 캐시 |
| last_backtest_mdd | NUMERIC(10,4) | 최근 백테스트 MDD 캐시 |
| last_backtest_sharpe | NUMERIC(10,4) | 최근 백테스트 Sharpe 캐시 |
| disclaimer_agreed | BOOLEAN | 면책 동의 여부 |
| created_at / updated_at | TIMESTAMPTZ | 생성/수정 시점 |

#### go100_portfolios (포트폴리오)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| portfolio_id | BIGSERIAL PK | |
| user_id, account_id, go100_card_id | FK | 소유자/계좌/전략 |
| initial_capital | NUMERIC(20,2) | 초기 자본 |
| current_cash | NUMERIC(20,2) | 현재 현금 |
| total_invested / total_eval | NUMERIC(20,2) | 투자금 / 평가금 |
| is_paper / is_live | BOOLEAN | 모의/실 구분 |
| status | VARCHAR(20) | ACTIVE/PAUSED/CLOSED |
| risk_tolerance | VARCHAR(20) | 리스크 수준 |

#### go100_positions (포지션)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGSERIAL PK | |
| portfolio_id | FK | 포트폴리오 |
| stock_code, stock_name | VARCHAR | 종목 |
| quantity, remaining_qty | INTEGER | 수량 |
| entry_price, current_price | NUMERIC | 가격 |
| status | VARCHAR(20) | OPEN/CLOSED/PARTIAL/FORCE_CLOSED |
| stop_loss_price, take_profit_price | NUMERIC | 청산 기준가 |
| trailing_pct, peak_price | NUMERIC | 트레일링 |
| pnl_amount, pnl_pct | NUMERIC | 손익 |

#### go100_orders (주문)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGSERIAL PK | |
| side | VARCHAR(10) | BUY/SELL |
| order_type | VARCHAR(20) | MARKET/LIMIT |
| status | VARCHAR(20) | PENDING/SUBMITTED/FILLED/PARTIAL/CANCELLED/REJECTED/SIMULATED |
| broker_order_no | VARCHAR(50) | KIS 주문번호 |
| is_paper | BOOLEAN | 모의/실 구분 |

#### go100_trades (체결 기록)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGSERIAL PK | |
| side | VARCHAR(10) | BUY/SELL |
| price, quantity, amount | NUMERIC | 체결 정보 |
| pnl_amount, pnl_pct | NUMERIC | 실현 손익 (SELL만) |

#### go100_backtest_runs (백테스트 이력)

| 주요 컬럼 | 설명 |
|-----------|------|
| start_date, end_date | 테스트 기간 |
| total_return, max_drawdown, sharpe_ratio | 성과 지표 |
| result_detail | JSONB (equity curve, trade log) |
| optimization_round, parent_run_id | 최적화 루프 추적 |

#### go100_fit_analysis (종목 적합도, BUNDLE4D)

| 주요 컬럼 | 설명 |
|-----------|------|
| go100_card_id, stock_code | 전략-종목 조합 |
| total_return, win_rate, profit_factor | 개별 백테스트 성과 |
| fit_score | 복합 적합도 점수 (0~100) |
| entry_timing | JSONB (요일별 승률/수익) |

#### go100_desk_allocation (데스크 배분, BUNDLE4D)

| 주요 컬럼 | 설명 |
|-----------|------|
| total_capital | 총 자본 |
| card_allocations | JSONB (카드별 비중/금액) |
| overlap_resolved | JSONB (중복 종목 해소 기록) |

#### go100_risk_disclaimers (면책 동의)
#### go100_account_reconciliation (계좌 조정)

### 11.2 V4.1 참조 테이블 (읽기전용)

| 테이블 | 행수 | GO100 사용처 |
|--------|------|-------------|
| ohlcv_daily | **2,596,548** | 일봉 백테스트, 유니버스 필터 |
| v4_ohlcv_minute | **18,395,750** | 분봉 백테스트 (499종목, 월별 파티션) |
| stock_universe | **3,844** | 종목 마스터, 섹터, 시장 구분 |
| stock_fundamentals | **4,249** | 시가총액 (유일한 유효 소스), PER/PBR |
| v4_investor_daily | **166,921** | 외인/기관 수급 필터 |
| v4_sector_daily | **14,696** | 섹터 로테이션 (32업종) |
| v4_vkospi_daily | **1,504** | 변동성 지수 (리짐 판단) |
| index_daily | **1,467** | 벤치마크 지수 |
| v4_signals | **101,274** | CARD-BUY 브릿지 |
| v4_positions | **5 (OPEN)** | 실매매 포지션 모니터링 |
| strategy_cards | **59** | V4.1 레거시 전략 |

### 11.3 데이터 특이사항

| 항목 | 주의 |
|------|------|
| ohlcv_daily.date | **VARCHAR(8)** YYYYMMDD (DATE 타입 아님!) |
| stock_universe.market_cap | **전부 NULL** → stock_fundamentals.market_cap 사용 |
| stock_universe.rank_market_cap | **전부 NULL** |
| v4_ohlcv_minute | 월별 파티션, 499/3,844종목만 보유 |

---

## 12. 데이터 파이프라인

### 12.1 자동 수집 스케줄

| 시간 | 요일 | 스크립트 | 대상 테이블 |
|------|------|---------|------------|
| 16:00 | 평일 | kis-v41-minute-collector (systemd) | v4_ohlcv_minute |
| 18:00 | 평일 | collect_ohlcv_daily.py | ohlcv_daily |
| 18:30 | 평일 | collect_index_daily.sh | index_daily |
| 18:40 | 평일 | collect_market_investor.py | v4_market_investor_daily |
| 19:00 | 평일 | collect_stock_universe.py | stock_universe |
| 토 02:00 | 토 | minute_batch_cron | v4_ohlcv_minute (보충) |
| 토 03:00 | 토 | collect_stock_industry.py | stock_universe 업종 |
| 수동 | — | fundamental_collector.py | stock_fundamentals |

### 12.2 데이터 흐름

```
KIS API (주식시세)
    │
    ▼
collect_*.py (수집 스크립트)
    │
    ▼
PostgreSQL (ohlcv_daily, v4_ohlcv_minute, ...)
    │
    ├─→ BacktestDataLoader     → BacktestSimulator
    ├─→ Go100AdvancedFilters   → 유니버스 선정
    ├─→ Go100MinuteDataLoader  → 분봉 시뮬레이터
    └─→ DataCache              → SignalEvaluator
```

---

## 13. 프론트엔드 아키텍처

### 13.1 기술 스택

| 항목 | 기술 |
|------|------|
| 프레임워크 | **Next.js 14** (App Router) |
| 렌더링 | SSR + CSR 혼합 |
| UI | React 18, TypeScript |
| HTTP | Axios (go100Client, JWT 자동 첨부) |
| 인증 | localStorage JWT → 401시 /auth/login 리다이렉트 |
| 라우팅 | `(protected)/go100/` 레이아웃 보호 |

### 13.2 디렉토리 구조

```
frontend/src/go100/
├── api/go100Api.ts          (53개 API 함수)
├── types/                   (8개 타입 파일: strategy, portfolio, position, ...)
├── hooks/                   (useDashboard, useStrategies, usePaperTrading, ...)
└── components/              (20+ 컴포넌트)
    ├── DashboardContent.tsx  (대시보드)
    ├── ChatInterface.tsx     (AI 채팅)
    ├── StrategyCard.tsx      (카드 표시)
    ├── PositionTable.tsx     (포지션 테이블)
    ├── PortfolioChart.tsx    (수익 차트)
    └── strategy/             (전략 상세 서브컴포넌트)
```

### 13.3 페이지 라우트

| 경로 | 페이지 |
|------|--------|
| `/go100` | 대시보드 (활성 전략, 포트폴리오, 최근 활동) |
| `/go100/chat` | AI 채팅 (백억이) |
| `/go100/strategies` | 전략 목록 |
| `/go100/strategies/[id]` | 전략 상세 (편집/백테스트/상태전이) |
| `/go100/store` | 마켓플레이스 |
| `/go100/paper-trading` | 모의매매 목록 |
| `/go100/paper-trading/[id]` | 모의매매 상세 |
| `/go100/live-trading` | 실매매 목록 |
| `/go100/live-trading/[id]` | 실매매 상세 |
| `/go100/settings` | 설정 |

### 13.4 Axios 인터셉터

```typescript
// Request: JWT 자동 첨부
config.headers.Authorization = `Bearer ${localStorage.getItem("token")}`;

// Response: 401 → 자동 로그아웃
if (err.response?.status === 401) {
  localStorage.removeItem("token");
  window.location.href = "/auth/login";
}
```

---

## 14. 인프라 및 배포

### 14.1 Nginx 라우팅

```nginx
# go100.newtalk.kr (HTTPS)
server {
    listen 443 ssl;
    server_name go100.newtalk.kr;

    location /api/   → proxy_pass http://127.0.0.1:8002  # GO100 API
    location /docs   → proxy_pass http://127.0.0.1:8002  # Swagger
    location /health → proxy_pass http://127.0.0.1:8002  # 헬스체크
    location /       → proxy_pass http://127.0.0.1:3000  # Frontend
}
```

### 14.2 systemd 서비스

**GO100 API** (`go100.service`):
```ini
ExecStart=/root/kis-autotrade-v4/venv/bin/python3 -m uvicorn \
    backend.app.main:app --host 127.0.0.1 --port 8002 --workers 2
Restart=on-failure
RestartSec=10
```

**GO100 스케줄러 타이머** (`go100-scheduler@{live|paper|reconcile|report}.timer`):
```ini
ExecStart=/root/kis-autotrade-v4/venv/bin/python3 \
    backend/app/services/go100/scheduler/go100_scheduler.py %i
```

### 14.3 DB 연결 풀

```python
async_engine = create_async_engine(
    "postgresql+asyncpg://kis_admin:***@localhost/kisautotrade",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

---

## 15. 보안 아키텍처

### 15.1 미들웨어 스택 (실행 순서)

```
Request →
  1. IPWhitelistMiddleware (공개 경로 제외)
  2. InternalAPIKeyMiddleware (/api/v4/* 전용)
  3. CORSMiddleware (go100.newtalk.kr, localhost:3000)
  4. RateLimitMiddleware
  5. RequestLoggingMiddleware
  6. SecurityHeadersMiddleware (HSTS, CSP, X-Frame-Options)
  7. FastAPI 라우터 → get_current_user (JWT 검증)
→ Response
```

### 15.2 JWT 인증 흐름

1. 로그인 → `auth_service.create_access_token(user_id, tier)`
2. 클라이언트 → `Authorization: Bearer <JWT>` 헤더 첨부
3. 서버 → `verify_access_token()` → payload에서 `sub`(user_id), `tier` 추출
4. DB 조회 → `v4_users` 테이블에서 email, tier, is_active 확인
5. `current_user = {"user_id": int, "email": str, "tier": str, "is_active": bool}`

### 15.3 Tier 기반 접근 제어

| Tier | 수준 | 접근 가능 기능 |
|------|------|---------------|
| FREE | 0 | 전략 생성, 백테스트, 모의매매 |
| PRO | 1 | + 실매매 |
| PREMIUM | 2 | + 관리자 기능, 스케줄러 제어 |

---

## 16. 운영 현황

### 16.1 현재 GO100 데이터 현황

| 테이블 | 건수 |
|--------|------|
| 전략 카드 | 15 (LLM 14 + CUSTOM 1) |
| 포트폴리오 | 5 (PAPER 3 + LIVE 1 + CLOSED 1) |
| 포지션 | 6 |
| 주문 | 3 |
| 거래 | 3 |
| 적합도 분석 | 40 |
| 데스크 배분 | 2 |
| 면책 동의 | 1 |
| 계좌 조정 | 0 |
| 백테스트 실행 | 0 (인메모리 실행, DB 저장 없음) |

### 16.2 CEO 3전략 분석 결과 (BUNDLE4D)

| Card | 전략 | 유형 | TOP 종목 | fit_score | Sharpe | 배분비중 |
|------|------|------|---------|-----------|--------|---------|
| 13 | 분봉 스캘핑 고변동 대형주 | 스캘핑 | 자화전자 | 78.73 | 3.52 | 49.1% |
| 14 | 대형 우량주 수급 데일리 | 데일리 | ISC | 78.90 | 3.65 | 50.9% |
| 15 | 섹터모멘텀 외인수급 스윙 | 스윙 | (유니버스 실패) | — | 0 | 0% |

### 16.3 알려진 이슈 및 제한

| 이슈 | 상태 | 영향 |
|------|------|------|
| stock_universe.market_cap = ALL NULL | 인지 | stock_fundamentals 대체 사용 |
| Card 15 스윙 유니버스 실패 | 인지 | v4_stock_sector 데이터 부족 |
| 분봉 데이터 499/3,844종목 | 수집중 | 분봉 백테스트 대상 제한 |
| LLM 비용 월 $100 제한 | 운영중 | 초과 시 무료 모델 폴백 |

### 16.4 구현 이력 (최근 주요)

| ID | 내용 | 테스트 |
|----|------|--------|
| BUNDLE4D | 종목×전략 적합도+청산 최적화+멀티 데스크 배분 | 141 |
| BUNDLE4C | 오케스트레이터 분봉 우선+일봉 폴백+분할익절 | 129 |
| BUNDLE4B-FIX | 오케스트레이터 전체 루프 복구 | 129 |
| BUNDLE3 | 포지션사이징+면책동의+실거래엔진+스케줄러 | 98 |
| PHASE7 | Paper Trading 엔진/스케줄러/서비스/라우터 | 74 |
| PHASE6 | EVALUATE+OPTIMIZE 에이전트+전체 오케스트레이션 | 61 |
| PHASE5 | UNDERSTAND+DESIGN AI 에이전트 | 12 |
| PHASE4 | 백테스트 시뮬레이터+시그널 평가기 | 10 |
| PHASE3 | 포트폴리오 서비스+포지션 관리 | 8 |

---

**보고서 끝**

| 메트릭 | 값 |
|--------|-----|
| 분석 대상 파일 수 | ~110개 |
| 분석 범위 | 백엔드 서비스, DB 스키마, API, 프론트엔드, 인프라 전체 |
| 보고서 위치 | `report/GO100-SYSTEM-TECHNICAL-REPORT-20260222.md` |
