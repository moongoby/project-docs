# 백억이 v3.0 — 천재 트레이더 진화 상세 기획서

**문서 ID**: RPT-GO100-BAEKOGI-V3-GENIUS-TRADER-PLAN-20260226

**작성일**: 2026-02-26

**작성자**: Claude Opus 4.6

---

## PART 1. 현재 시스템 정밀 진단

### 1-1. 실제 운영 데이터 — 우리가 가진 것과 없는 것

현재 DB에서 확인된 실제 데이터는 다음과 같습니다.

**있는 것**: `go100_strategy_cards` 3건(스캘핑, 데일리, 단기스윙 — 모두 user_id=3, 상태 BACKTESTED), `strategy_cards` 62건(V4 레거시), `v4_users` 4명, `ohlcv_daily` 수년치 일봉, `stock_fundamentals`(PER/PBR/EPS/BPS + ROE 2,439건 계산 완료, 단 revenue/operating_profit/dividend_yield 미수집), `v4_market_regime_daily`(레짐 분류 데이터), `v4_investor_daily`(외국인/기관 수급), `index_daily`(코스피/코스닥 지수), `v4_ohlcv_minute_*`(분봉 파티션 — 각 0.75~1.15GB), `accounts` 7건(KIS 증권 계좌 연동 완료), `v4_positions` 5건(V4 실제 보유 포지션).

**없는 것**: `go100_backtest_runs` 0건(Phase 4~10에서 구현했으나 실제 백테스트 실행 이력 없음), `go100_portfolios` 0건, `go100_positions` 0건, `go100_orders` 0건, `go100_trades` 0건, `go100_goals` 테이블은 Phase 5 C-1에서 스키마만 추가(실데이터 없음), 글로벌 시장 데이터(`go100_global_market` — Phase 5 B-3에서 구현했으나 수집 이력 미확인), 경험/학습 데이터 전무.

### 1-2. 핵심 발견 — 구현은 됐지만 "살아있지 않다"

Phase 4~10에서 16건의 모듈을 구현하고 E2E 17/17 PASS를 받았습니다. 하지만 **실제 데이터가 흐르고 있지 않습니다.** 백테스트가 한 번도 돌지 않았고, 목표를 설정한 사용자가 없고, 페이퍼 트레이딩 계좌가 없고, 포트폴리오가 비어 있습니다. 모듈은 배관이 깔린 집인데 수도꼭지를 틀지 않은 상태입니다.

또한 스크린샷에서 확인된 것처럼 "오늘 지수 알려줘"가 stock_info로 잘못 분류되는 문제가 있습니다. 이건 키워드 기반 인텐트 분류의 구조적 한계이며, 새로운 표현이 나올 때마다 키워드를 추가해야 하는 끝없는 패치 작업이 됩니다.

### 1-3. 인프라 제약

서버 1대(Xeon 4코어, 15GB RAM, 99GB SSD), 디스크 89% 사용(84GB/99GB), PostgreSQL 14GB(분봉 파티션이 대부분), 백업 33GB. 크론 일부 미등록(모닝브리핑, 장마감, 페이퍼, 주간, 이벤트 5건). LLM 비용 현재 월 ~$15(100유저 기준).

### 1-4. 사용자 현황

v4_users 4명(시스템 계정 포함). 실사용자는 대표님(user_id=2, [CEO-EMAIL-GM])과 오병용님(user_id=3, [CEO-EMAIL-NV]) 2명. 전략 카드 3건 모두 user_id=3 소유.

---

## PART 2. 버전 정의

| 버전 | 코드명 | 핵심 능력 | 시기 |
|------|--------|-----------|------|
| v1.0 | 정보원 (현재) | 데이터 조회 + 포맷팅 | 완료 |
| v2.0 | 분석가 | LLM 자율 판단 + 시그널 생성 + 경험 축적 시작 | 1~4주 |
| v3.0 | 트레이더 | 전략 자동 진화 + 크로스마켓 예측 + 실매매 검증 | 4~10주 |
| v4.0 | 천재 | 자기 복기 + 포트폴리오 최적화 + 개인화 완성 | 10~16주 |

---

## PART 3. v2.0 "분석가" — 상세 설계 (1~4주)

### 3-1. Agentic Architecture 전환

**현재 문제**: 키워드 60개 → C2SC LLM → 20개 인텐트 → 하드코딩 핸들러. 키워드에 없으면 오분류. 새 기능 추가할 때마다 인텐트 정의, 키워드 등록, 핸들러 작성, 프롬프트 수정, llm_router 동기화 5곳을 건드려야 합니다.

**전환 설계**:

현재 `function_calling.py`가 stock_info 한 인텐트에만 5개 도구로 실험 중입니다(W3-C, 커밋 ed9c4b84). 이걸 전체 시스템으로 확장합니다.

도구 구성은 `data_queries.py`의 기존 14개+ 함수를 그대로 도구로 등록합니다. 새로 만들 필요 없이 기존 코드를 래핑합니다. 구체적으로 `identify_stock`, `get_stock_ohlcv`, `get_stock_fundamentals`, `get_investor_flow`, `get_market_regime`, `get_index_data`, `get_user_portfolio`, `get_user_goal`, `get_positions_count`, `get_top_stocks`, `get_sector_stats`, `get_trade_history`, `get_backtest_results`, `get_strategy_detail`, `get_portfolio_risk`, `get_cards_for_compare` — 이 함수들이 이미 존재하고 E2E 테스트를 통과했습니다. 여기에 Phase 5~10에서 추가된 `goal_engine`, `portfolio_manager`, `regime_engine`, `paper_trading`, `live_trading`, `proactive_reporter`의 함수들을 도구로 추가합니다.

**멀티 모델 분리** (대표님 보고서 반영):

현재 LLM 구성은 자유대화 Gemini 2.0 Flash, C2SC Gemini 2.5 Flash→Haiku 폴백, 전략검증 Opus입니다. 이걸 다음으로 변경합니다.

대화 처리(Agent Core): **Claude Opus 4.6** — 도구 선택, 결과 종합, 사용자 응답 생성. 가장 복잡한 추론이 필요한 층이므로 최고 모델을 씁니다. 현재 `llm_gateway.py`의 `FAILOVER_CHAINS`에 Opus를 추가하면 됩니다.

배치 분석(시그널 해석, 브리핑 생성): **Claude Sonnet 4** — `daily_reports.py`에서 사용. 현재 `proactive_reporter.py`가 있으므로 여기서 LLM 호출 부분만 Sonnet으로 지정합니다.

전략 가설 생성(주 1회): **Claude Opus 4.6 Temperature 0.9** — 새 모듈 `strategy_ideation.py`에서 사용.

**비용 영향**: Opus 대화 처리로 전환하면 100유저 기준 월 $15 → $40~60 예상. 하지만 Sonnet 배치와 캐싱으로 최적화하면 $35~45 수준으로 제어 가능.

**환각 방지**: Agent Core의 System Prompt에 절대 규칙을 넣습니다. "도구에서 가져온 데이터만 사용하세요. 가격, 수익률, 지표 숫자를 절대 만들어내지 마세요. 도구 결과에 없는 정보는 '해당 데이터가 없습니다'라고 답하세요. 매매 추천을 하지 마세요. 데이터와 분석을 제공하고 판단은 사용자에게 맡기세요." 다만 향후 v3.0에서 경험 DB가 쌓이면 조건부 판단 의견을 제공하는 것으로 진화합니다.

**Fallback**: `GO100_AGENT_MODE` 환경변수로 토글. false이면 기존 키워드+인텐트 시스템 작동.

### 3-2. 크로스마켓 선행 시그널 엔진

**현재 자산**: `go100_global_market` 테이블(Phase 5 B-3에서 생성), `scripts/data_collect/collect_global_market.py`(yfinance 기반), 크론 08:30 등록.

**확장 설계**:

DB 스키마 추가:
```
go100_cross_market_signals
- signal_id SERIAL PRIMARY KEY
- signal_date DATE NOT NULL
- signal_type VARCHAR(30)    -- sox_kr_semi, usd_krw_foreign, us10y_growth, china_open
- signal_value REAL          -- 상관계수 또는 예측 확률
- signal_direction VARCHAR(10) -- bullish, bearish, neutral
- confidence REAL            -- 0~1
- raw_data JSONB             -- 계산에 사용된 원시 데이터
- created_at TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(signal_date, signal_type)
```

시그널 4종:

**SOX→한국반도체**: 전날 SOX 지수 변화율 → `v4_sector_stock_mapping`에서 반도체 섹터 종목 추출 → 과거 60일 롤링 상관계수 계산 → SOX가 ±2% 이상 변동 시 시그널 발생. 기존 `v4_sector_price`, `v4_sector_stock_mapping` 테이블(DESK2에서 생성)을 그대로 활용합니다.

**USD/KRW→외국인 매매**: 전날 환율 변화 → `v4_investor_daily`의 외국인 순매수 → 과거 60일 롤링 상관. 환율 약세(원화 강세) → 외국인 매수 경향.

**US10Y→성장주**: 미국 10년물 금리 변화 → KOSDAQ 대비 KOSPI 상대 강도. 금리 급등 → 성장주(코스닥) 약세 경향.

**중국 CSI300 개장 30분**: 한국 시장보다 1시간 먼저 여는 중국 시장 초반 방향. 이건 장중 데이터가 필요하므로 v2.0 후반에 추가.

**수집 스크립트**: `scripts/go100/collect_cross_market_signals.py` — 매일 새벽 07:00 실행. yfinance로 전날 미국 데이터 수집 → 상관계수 계산 → 시그널 INSERT → 모닝 브리핑에 포함.

**모닝 브리핑 연동**: `proactive_reporter.py`의 `generate_morning_briefing()`에 크로스마켓 시그널 섹션 추가. "🌍 글로벌 시그널: 전날 SOX +2.3% → 오늘 국내 반도체 섹터 갭업 확률 72% (최근 60일 기준)"

### 3-3. 경험 DB 축적 시작

**현재 자산**: `go100_usage_logs`(Phase 10-B에서 생성, 사용 로그), `go100_paper_snapshots`(페이퍼 일일 스냅샷), `go100_live_orders`(실매매 주문 로그), `go100_live_daily_summary`(일일 매매 집계).

**신규 테이블**:
```
go100_experience_log
- exp_id SERIAL PRIMARY KEY
- user_id INTEGER NOT NULL
- event_type VARCHAR(30)     -- signal_generated, order_placed, order_filled, 
                             -- position_closed, regime_changed, strategy_evolved
- context JSONB              -- 이벤트 시점의 시장 상태
  {
    "regime": "sideways",
    "regime_score": 45,
    "vkospi": 18.5,
    "kospi_change_pct": -0.3,
    "kosdaq_change_pct": 0.8,
    "usd_krw": 1385.2,
    "cross_signals": ["sox_bullish_0.72"],
    "sector_momentum": {"반도체": 0.85, "자동차": -0.3}
  }
- action JSONB               -- 취한 행동
  {
    "stock_code": "005930",
    "stock_name": "삼성전자",
    "direction": "BUY",
    "strategy_name": "섹터모멘텀 외국인수급 스윙",
    "entry_reason": "외국인 3일 연속 순매수 + SOX 시그널 bullish",
    "quantity": 10,
    "price": 85000
  }
- outcome JSONB              -- 결과 (position_closed 시 채움)
  {
    "exit_price": 92000,
    "holding_days": 7,
    "return_pct": 8.2,
    "pnl_amount": 70000,
    "exit_reason": "목표가 도달"
  }
- created_at TIMESTAMPTZ DEFAULT NOW()

CREATE INDEX idx_go100_exp_context ON go100_experience_log 
  USING GIN (context jsonb_path_ops);
CREATE INDEX idx_go100_exp_user_date ON go100_experience_log(user_id, created_at DESC);
```

**핵심**: 이 테이블은 지금부터 모든 행동을 기록합니다. 페이퍼 트레이딩이 시작되는 순간부터 데이터가 쌓이기 시작하고, 경험이 축적됩니다. v3.0에서 이 데이터를 활용해 "과거에 비슷한 상황에서 어떤 결과가 나왔는지"를 판단 시점에 참조합니다.

**기록 시점**: `paper_trading.py`의 `fill_orders()`, `run_daily_signals()`, `take_snapshot()`에서 자동 기록. `live_trading.py`의 `submit_order()`, `check_filled_orders()`에서 자동 기록. `regime_engine.py`의 `detect_regime_change()`에서 레짐 변화 시 기록.

### 3-4. 시스템 살리기 — 데이터 흐름 시작

현재 go100_backtest_runs 0건, go100_goals 0건입니다. 모듈이 있어도 데이터가 없으면 무의미합니다.

**자동 시드 데이터 생성**: 서비스 시작 시 또는 별도 스크립트로, 기존 전략 카드 3건(card_id 13, 14, 15)에 대해 자동 백테스트를 실행합니다. `go100_backtest_runs`에 결과가 쌓이면 대시보드와 전략 비교 기능이 실제로 작동합니다.

**대표님 계정 자동 설정**: user_id=2(대표님)에 대해 기본 목표(예: 1억→3억, 5년)를 `go100_goals`에 INSERT하고, 기본 포트폴리오를 `go100_strategy_portfolios`에 생성하고, 기존 전략 카드 3건을 연결합니다. 이렇게 하면 "내 포트폴리오"라고 물었을 때 빈 응답이 아니라 실제 데이터가 나옵니다.

**크론 전체 등록**: 미등록 5건(모닝 08:50, 장마감 15:40, 페이퍼 16:10, 주간 토 09:00, 이벤트 */5 장중) + 크로스마켓 시그널 07:00 + 헬스모니터 */5.

---

## PART 4. v3.0 "트레이더" — 상세 설계 (4~10주)

### 4-1. Strategy Evolution Engine

**현재 자산**: 전략 카드 스키마(`entry_rules`, `exit_rules`, `risk_params`가 JSONB), 백테스트 인프라(`go100_backtest_runs`), V4 레거시 전략 62건(`strategy_cards`).

**설계**:

매주 월요일 새벽 04:00에 자동 실행되는 `scripts/go100/strategy_evolution.py`:

1단계 — **현재 전략 성과 평가**: `go100_backtest_runs`와 `go100_paper_snapshots`에서 각 전략의 최근 성과를 조회. 샤프비율, MDD, 승률 기준 순위 매김.

2단계 — **파라미터 변이**: 상위 50% 전략의 `entry_rules`, `exit_rules`, `risk_params`를 복제 후 파라미터를 ±10~30% 범위에서 랜덤 변이. 예: 이동평균 기간 20일→18일 또는 22일, 손절선 -5%→-4% 또는 -6%.

3단계 — **LLM 창의적 전략 생성** (대표님 보고서 반영): Claude Opus Temperature 0.9로, 최근 시장 데이터(레짐 히스토리, 섹터 로테이션, 크로스마켓 시그널)를 컨텍스트로 주고 "이 시장 환경에 맞는 새로운 전략 구조를 3개 제안해주세요. entry_rules, exit_rules, risk_params를 GO100 JSONB 형식으로 작성해주세요."라고 요청. 기존 전략 62건(V4 레거시)의 구조를 참고 예시로 제공.

4단계 — **자동 백테스트**: 변이 전략 + LLM 생성 전략을 모두 백테스트. 기존 `go100_backtest_runs` 인프라 사용.

5단계 — **선별**: 기존 전략 대비 샤프비율이 높고 MDD가 낮은 전략만 `go100_strategy_cards`에 `card_status='CANDIDATE'`로 저장. 사용자에게 "새로운 전략 후보가 생겼습니다" 알림.

6단계 — **퇴출**: 3주 연속 하위 20% 성과인 전략은 `card_status='RETIRED'`로 변경.

**생존 편향 제거** (교차 검토 보고서 반영): 백테스트 시 `stock_universe`에서 `is_active=false`(상장폐지) 종목도 해당 기간에는 포함. `stock_fundamentals`의 재무 데이터는 발표일 기준으로만 사용(point-in-time).

### 4-2. 이벤트 드리븐 엔진

**현재 자산**: `v4_investor_daily`(수급), `stock_fundamentals`(재무), 뉴스/공시 수집 없음.

**단계적 구현**:

1차(4~6주) — **DART 공시 수집**: OpenDart API로 주요 공시(실적발표, 대규모 수주, 유상증자, 자사주 매입) 수집. `go100_dart_disclosures` 테이블에 저장. 장중 1분 간격 폴링.

2차(6~8주) — **과거 유사 이벤트 통계**: 실적 서프라이즈 데이터(실적 발표 vs 컨센서스)를 축적. "실적 서프라이즈 20% 이상일 때 발표 후 5일 평균 수익률"을 자동 계산. 이 통계를 경험 DB에 저장.

3차(8~10주) — **실시간 알림**: DART 공시 수집 → LLM(Sonnet)이 임팩트 판단 → 유의미하면 `go100_reports`에 urgent 알림 저장 → 프론트엔드 미읽은 뱃지.

### 4-3. 크로스마켓 예측 모델 고도화

v2.0에서 시작한 상관계수 기반 시그널을 **롤링 윈도우 + 상관 붕괴 감지**로 업그레이드합니다.

상관계수를 20일/60일/120일 세 윈도우로 계산하고, 20일과 120일의 차이가 급격히 벌어지면(예: 20일 상관 0.3, 120일 상관 0.8) "상관관계 구조 변화" 시그널을 발생시킵니다. 이건 시장 구조가 바뀌고 있다는 조기 경보입니다.

---

## PART 5. v4.0 "천재" — 상세 설계 (10~16주)

### 5-1. 경험 기반 판단 시스템

v2.0에서 축적 시작한 `go100_experience_log`가 10주 차에는 수백~수천 건이 됩니다. 이 데이터로 **유사 상황 검색**을 합니다.

매매 신호가 발생했을 때, 현재 context(레짐, VKOSPI, 섹터 모멘텀, 크로스마켓 시그널)와 유사한 과거 경험을 JSONB GIN 인덱스로 검색합니다. "현재 레짐=sideways, VKOSPI>20, 반도체 섹터 모멘텀 양수인 상황에서 과거 모멘텀 전략 진입 결과: 12건 중 4건 수익(승률 33%), 평균 수익률 -2.1%"라는 통계가 나오면, 백억이는 "모멘텀 전략이 매수 신호를 내고 있지만, 과거 유사 상황에서 성과가 좋지 않았습니다(승률 33%)"를 사용자에게 알려줍니다.

이게 대표님이 말한 "경험 기억이 판단 시점에 개입"하는 것입니다.

### 5-2. 포트폴리오 레벨 최적화

**현재 자산**: `portfolio_manager.py`(Phase 5 C-2), `go100_strategy_portfolios`, `go100_portfolio_allocations`.

**추가 구현**:

**상관관계 매트릭스**: 보유 종목 간 일별 수익률 상관계수를 `ohlcv_daily` 기반으로 계산. `v4_sector_correlation`(DESK2에서 이미 생성)도 활용.

**꼬리 리스크(CVaR)**: 정상 시장 VaR(95%)뿐 아니라 스트레스 시나리오(과거 폭락 구간)에서의 포트폴리오 손실을 계산. "최악의 경우 포트폴리오가 -23% 빠질 수 있습니다" 경고.

**신규 종목 추가 시뮬레이션**: "하이닉스 추가하면 포트폴리오 전체 변동성이 12%→18%로 증가합니다. 반도체 섹터 비중이 15%→40%로 편중됩니다" — 매수 전에 알려줌.

### 5-3. 대표님 개인화 프로파일

```
go100_user_profile
- user_id INTEGER PRIMARY KEY
- risk_tolerance VARCHAR(20)     -- conservative, moderate, aggressive
- preferred_style VARCHAR(20)    -- scalping, swing, position
- preferred_sectors JSONB        -- ["반도체", "자동차"]
- avoided_sectors JSONB          -- ["바이오"]
- max_drawdown_tolerance REAL    -- 최대 허용 MDD (%)
- trading_frequency VARCHAR(20)  -- daily, weekly, monthly
- market_hours_active BOOLEAN    -- 장중 알림 원하는지
- notes TEXT                     -- 자유 메모
- learned_preferences JSONB      -- 대화에서 자동 학습된 선호 (v4.0)
- created_at TIMESTAMPTZ DEFAULT NOW()
- updated_at TIMESTAMPTZ DEFAULT NOW()
```

온보딩 시 기본 질문으로 채우고, 이후 대화에서 자동 업데이트합니다. "바이오는 잘 모르겠어"라고 하면 `avoided_sectors`에 추가. "난 MDD 10% 넘으면 못 견딘다"라면 `max_drawdown_tolerance=10`. 이 프로파일이 Agent Core의 System Prompt에 반영되어, 백억이가 대표님에게 맞춤 분석을 제공합니다.

### 5-4. 자기 복기 시스템 고도화

주간 자동 복기 보고서에 경험 DB 통계를 포함합니다. "이번 주 모멘텀 전략 3건 중 1건만 수익. 공통 실패 패턴: 레짐 전환 구간(sideways→bear)에서 진입. 권고: 레짐 전환 감지 시 모멘텀 전략 진입 보류." 이 권고가 다음 주 `regime_engine.py`의 조정 제안에 자동 반영됩니다.

---

## PART 6. 인프라 로드맵

### 6-1. 디스크 (즉시)

현재 89%(84GB/99GB). **Cafe24 250GB 확장(₩10,000/월)을 즉시 신청해야 합니다.** 분봉 파티션만 4~5GB이고, 경험 DB + 이벤트 데이터 + 글로벌 데이터가 추가되면 100GB는 금방 찹니다. 99GB로는 v2.0도 위험합니다.

### 6-2. 크론 정비 (즉시)

미등록 5건 즉시 등록 + 신규 크론 추가:

| 크론 | 스케줄 | 용도 | 상태 |
|------|--------|------|------|
| 07:00 월~금 | collect_cross_market_signals.py | 크로스마켓 시그널 | 신규 |
| 08:30 월~금 | collect_global_market.py | 글로벌 데이터 | 등록됨 |
| 08:50 월~금 | daily_reports.py --type morning | 모닝 브리핑 | **미등록** |
| 15:40 월~금 | daily_reports.py --type closing | 장마감 리포트 | **미등록** |
| 16:10 월~금 | paper_trading_daily.py | 페이퍼 트레이딩 | **미등록** |
| 19:30 월~금 | collect_financials.py | 재무제표 수집 | 등록됨 |
| 토 09:00 | daily_reports.py --type weekly | 주간 보고 | **미등록** |
| */5 장중 | daily_reports.py --type event | 이벤트 알림 | **미등록** |
| */5 매일 | health_monitor.py | 헬스 모니터 | 신규 |
| 월 04:00 | strategy_evolution.py | 전략 진화 (v3.0) | 신규 |
| 04:00 매일 | 백업 삭제 7일 초과 | 디스크 관리 | 등록됨 |

### 6-3. LLM 비용 관리

| 용도 | 모델 | 호출 빈도 | 월 비용 추정 |
|------|------|-----------|-------------|
| 대화 (Agent Core) | Opus 4.6 | 사용자당 일 10회 | $25 |
| 배치 (브리핑, 복기) | Sonnet 4 | 일 4회 | $3 |
| 전략 생성 | Opus 4.6 T=0.9 | 주 1회 | $2 |
| C2SC 폴백 (기존) | Gemini Flash | 점진 감소 | $5 |
| **합계 (100유저)** | | | **~$35/월** |

### 6-4. 장애 대응 (v3.0 실매매 전)

별도 watchdog 프로세스: `scripts/go100/watchdog.py` — go100 서비스 상태 모니터링, 다운 시 자동 재시작, 실매매 포지션 열린 상태에서 서비스 장애 시 KIS API로 직접 전량 시장가 청산 또는 사전 설정된 Stop-loss 주문 확인.

---

## PART 7. 구현 순서 — 커서 지시서 단위

### Week 1 (즉시)

| 커서 | 작업 | 의존성 |
|------|------|--------|
| #A | 크론 5건 등록 + 디스크 정리 + 로그 로테이션 | 없음 |
| #B | 인텐트 분류 핫픽스(지수 등) + response_formatter 적용 확인 | 없음 |
| #C | 시드 데이터 생성(백테스트 3건, 대표님 목표/포트폴리오) | 없음 |
| #D | 경험 DB 테이블 생성 + 기록 로직 연동 | 없음 |

### Week 2

| 커서 | 작업 | 의존성 |
|------|------|--------|
| #E | Agentic Architecture — agent_tools.py + agent_core.py | #B 완료 |
| #F | 크로스마켓 시그널 수집 스크립트 + DB + 크론 | #A 완료 |
| #G | 멀티 모델 분리(Opus 대화, Sonnet 배치) | #E 완료 |

### Week 3~4

| 커서 | 작업 | 의존성 |
|------|------|--------|
| #H | Agent Core 검증 + 기존 시스템 비교 테스트 | #E, #G 완료 |
| #I | 모닝 브리핑에 크로스마켓 시그널 연동 | #F 완료 |
| #J | 사용자 프로파일 테이블 + 온보딩 연동 | #C 완료 |

### Week 5~8

| 커서 | 작업 | 의존성 |
|------|------|--------|
| #K | Strategy Evolution Engine | 경험 DB 데이터 축적 |
| #L | DART 공시 수집 + 이벤트 알림 | 없음 |
| #M | 크로스마켓 예측 모델 고도화 (롤링 윈도우) | #F, #I 완료 |

### Week 9~12

| 커서 | 작업 | 의존성 |
|------|------|--------|
| #N | 경험 기반 판단 시스템 | 경험 DB 수백 건 축적 |
| #O | 포트폴리오 CVaR + 상관관계 매트릭스 | 포트폴리오 데이터 축적 |
| #P | 자기 복기 고도화 + 전략 자동 조정 연동 | #K, #N 완료 |

### Week 13~16

| 커서 | 작업 | 의존성 |
|------|------|--------|
| #Q | watchdog + 장애 대응 | 실매매 전 필수 |
| #R | 실매매 본격 운영 + 모니터링 | 모든 이전 단계 |
| #S | 전체 시스템 안정화 + v4.0 완성 보고 | 모든 이전 단계 |

---

## PART 8. 성공 지표

| 지표 | v1.0 (현재) | v2.0 목표 | v3.0 목표 | v4.0 목표 |
|------|-------------|-----------|-----------|-----------|
| 인텐트 정확도 | 17/17 (키워드 한정) | 자유 질문 90%+ | 95%+ | 98%+ |
| 응답 시간 | 200~800ms | 1~3초 (Agent) | 1~3초 | 1~3초 |
| 크로스마켓 시그널 | 없음 | 4종 일일 생성 | 롤링 윈도우 | 상관 붕괴 감지 |
| 경험 DB | 0건 | 축적 시작 | 수백 건 | 수천 건 |
| 전략 자동 진화 | 없음 | 없음 | 주간 자동 | 주간+복기 반영 |
| 페이퍼 수익률 | 미운영 | 운영 시작 | KOSPI 대비 측정 | KOSPI+5% 목표 |
| 사용자 체감 | 데이터 조회 | 똑똑한 분석가 | 매매 파트너 | 전담 트레이더 |

---

## PART 9. 리스크와 대응

**리스크 1: Agentic 모드의 레이턴시가 사용자 이탈을 유발** — 대응: 간단한 질문(인사, 도움말)은 키워드로 즉시 응답하고, 분석 질문만 Agent로 라우팅하는 하이브리드. "분석 중입니다..." 스트리밍 응답으로 체감 대기시간 감소.

**리스크 2: LLM 환각으로 잘못된 투자 정보 제공** — 대응: 도구 결과만 사용하라는 절대 규칙 + response_filter.py의 기존 3종 필터(가짜 종목코드, 비현실적 수익률, 미래 날짜) 유지 + 모든 수치 응답에 데이터 출처 태그 부착.

**리스크 3: 전략 자동 진화가 과적합(Overfitting) 전략을 생산** — 대응: 백테스트 기간을 in-sample/out-of-sample으로 분리. 최소 3년 데이터로 백테스트하되 최근 6개월은 검증 구간으로 사용. 샤프비율이 3 이상이면 과적합 의심으로 자동 플래그.

**리스크 4: 디스크 100% 도달로 DB PANIC** — 대응: 250GB 확장 즉시 신청. 확장 전까지 분봉 데이터 3개월 이전 아카이빙.

**리스크 5: 실매매 중 시스템 장애** — 대응: watchdog 프로세스 + KIS API Stop-loss 사전 설정 + circuit breaker(일일 손실 3%). 서비스 장애 시 자동 전량 청산.

---
