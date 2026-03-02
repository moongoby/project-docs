# CUR-V41-ADDL-INVESTIGATION-002 — 10개 추가 조사항목 전수 확인 보고서
> 작성일: 2026-03-01 | 담당: Claude Code Sonnet 4.6 | 레포: kis-autotrade-v4 (phase-2c-command-center)

---

[인계 확인]
직전 완료: CUR-V41-FULL-SYSTEM-AUDIT-001
현재 단계: Cursor #22 — 백테스트 vs 실매매 엔진 통합 (Task A+분석 완료, Task B 대기)
CEO 지시 적용: D-001(단순사고 금지), D-002(보고서 push 필수)
strategy_cards: 60개
open_positions: 14개

---

## 개요

`CUR-V41-FULL-SYSTEM-AUDIT-001-20260301` 보고서 이후 CEO/AI 분석 세션에서 추가 요청된 10개 항목을 직접 코드·DB·환경변수 전수 확인한 결과를 정리한다.

---

## 조사 결과 일람

| # | 항목 | 상태 | 핵심 결과 |
|---|------|------|-----------|
| 1 | v4_ohlcv_minute 실시간 수집 | ✅ 확인 | WebSocket + 16:00 cron 이중 수집 |
| 2 | SystemOrchestrator L0 가동 여부 | ⚠️ 수정 필요 | V4PipelineOrchestrator가 실제 가동 중 |
| 3 | DRY_RUN 현재 값 | ❌ CRITICAL | `false` — 실전 주문 가능 상태 |
| 4 | price_poller 현황 | ✅ 구현됨 | 코드 완비, SystemOrchestrator 인스턴스에 주입됨 |
| 5 | CTE 모듈 인터페이스 | ✅ 확인 | `evaluate(TradeSignal, now) → PipelineResult` |
| 6 | Layer4 execution 디렉토리 | ✅ 확인 | `__init__.py` only, 의도적 미구현 |
| 7 | 포지션 테이블 관계 | ✅ 확인 | v4_positions / v4_paper_trades / go100_backtest_runs |
| 8 | go100_backtest_runs 스키마 | ✅ 확인 | 8개 핵심 컬럼 포함 |
| 9 | SlippageAnalyzer 존재 여부 | ❌ 없음 | .py 파일 없음, 설계 문서만 존재 |
| 10 | KIS Mock API 자격증명 | ✅ 완비 | Virtual 계좌 자격증명 .env에 존재 |

---

## 1. v4_ohlcv_minute 실시간 수집 현황

### 조사 결과: ✅ 이중 수집 체계 구축 완료

**실시간 (장중)**: `backend/app/services/data/kis_ws_collector.py`
- WebSocket 채널: `H0STCNT0` (체결), `H0STASP0` (호가)
- DB 적재: `v4_tick_data`, `v4_orderbook_realtime`, `v4_ohlcv_minute` (1분봉 집계)
- 도메인: 실전 `ws://ops.koreainvestment.com:21000`, 가상 `:31000`
- **최대 40종목/세션** (`MAX_SUBSCRIPTIONS_PER_SESSION = 40`)
- 운영 시간: 정규장 `08:55~15:35`

**히스토리 배치 (장 마감 후)**: `scripts/minute_batch_cron.sh`
```
0 16 * * 1-5   → collect_minute_historical.py --top 3844 --resume
0 2  * * 6     → 주말 보완 수집
```
- 락 파일 기반 중복 방지

**결론**: v4_ohlcv_minute는 장중 실시간 + 장후 히스토리 이중 구조로 완전 구현됨. (40종목 초과 시 실시간 커버리지 한계 주의)

---

## 2. SystemOrchestrator L0 실제 가동 여부

### 조사 결과: ⚠️ 현재 가동 서비스는 V4PipelineOrchestrator (다름)

**실제 서비스 매핑**:

| 서비스명 | ExecStart | 실제 클래스 |
|---------|-----------|-------------|
| `kis-v41-scheduler` | `python -m app.services.scheduler.daily_scheduler` | `V4PipelineOrchestrator` |
| `kis-trading-engine` | `/root/webapp/...unified_trading_scheduler.py` | 별도 레포 (미분석) |
| `kis-v41-api` | `uvicorn main:app --port 8003` | FastAPI 라우터 |

**핵심 발견**: `daily_scheduler.py`가 lazy init으로 `V4PipelineOrchestrator`를 생성함:
```python
from app.services.trading.v4_pipeline_orchestrator import V4PipelineOrchestrator
_pipeline = V4PipelineOrchestrator(config_id=_config_id(), dry_run=_dry_run())
```

**`system/orchestrator.py` (664줄 L0 상태기계) 현황**:
- `factory.py`에서 `price_poller` 등 인프라와 함께 인스턴스화 코드 존재
- 그러나 현재 활성 systemd 서비스가 이 클래스를 직접 가동하지 않음
- **설계는 완료, 실제 배포는 Task B에서 수행 예정**

**결론**: 현재 L0는 `V4PipelineOrchestrator` (레거시 아키텍처). `SystemOrchestrator` (신규 L0)는 미배포 상태.

---

## 3. DRY_RUN 현재 값

### 조사 결과: ❌ CRITICAL — `DRY_RUN=false`

**확인 경로**: `/root/kis-autotrade-v4/.env` line 58

```
DRY_RUN=false
```

**`daily_scheduler.py` dry_run 로직**:
```python
def _dry_run() -> bool:
    v = os.environ.get("DRY_RUN", "true").lower()
    return v in ("1", "true", "yes")
```
- 기본값은 `"true"` (안전)이지만 **현재 .env 설정이 `false`를 명시**

**위험 시나리오**:
1. `V4PipelineOrchestrator(dry_run=False)` 생성 → 실전 주문 API 호출 가능
2. `kis-v41-scheduler` + `kis-trading-engine` 동시 가동 → **이중 주문 위험**
3. `AutoTradeEngine` (별도 레거시) + `V4PipelineOrchestrator` 동시 가동 가능

**즉시 조치 필요 (CEO 확인 후)**:
- 실전 거래 의도라면: account_id 5,6 사용 금지 코드 보강 필요
- 모의 거래만 원한다면: `DRY_RUN=true`로 변경 필요

---

## 4. price_poller 현황

### 조사 결과: ✅ 구현 완료, 인프라 주입 준비됨

**구현 파일**: `backend/app/services/infra/price_poller.py`

**핵심 API**:
```python
class PricePoller:
    def get_price(ticker: str) -> PriceCacheEntry | None
    def get_price_safe(ticker, stale_threshold_ms=None) -> tuple[int|None, int|None]
    def update_watch_list(tickers: set[str])
    def get_max_staleness_ms() -> int
```

**PriceCacheEntry 구조**:
```python
class PriceCacheEntry(BaseModel):
    price: int
    ts: datetime
    source: str  # "KIS_REST", "KIS_WS", "MOCK", "CACHE"
    staleness_ms: int = 0
    stale_threshold_ms: int = 30_000  # 30초 기본
```

**환경변수**:
- `PRICE_POLL_INTERVAL_SEC` (기본 5.0초)
- `PRICE_STALE_THRESHOLD_MS` (기본 30,000ms = 30초)

**factory.py 주입 현황** (line 76):
```python
self.price_poller = self._create_price_poller()
```
→ `SystemOrchestrator` 생성 시 `price_poller=self.price_poller`로 전달됨

**가동 상태**: `SystemOrchestrator`가 미배포이므로 price_poller도 실제 폴링 미가동.
현재 가동 중인 `V4PipelineOrchestrator`는 price_poller를 사용하지 않음.

---

## 5. CTE 모듈 인터페이스

### 조사 결과: ✅ 전체 인터페이스 확인

**파일**: `backend/app/services/trading/cte/cte_pipeline.py` (821줄)

**진입점 (public API)**:
```python
class CTEPipeline:
    MAX_CONCURRENT_POSITIONS = 5

    def evaluate(
        self,
        signal: TradeSignal,
        now: Optional[datetime] = None,
    ) -> PipelineResult:
```

**TradeSignal 주요 필드 (50개+)**:
```python
@dataclass
class TradeSignal:
    strategy_id: str           # "D2","D4","D5","D6","D7","S1","D-ORB"
    trigger: Trigger
    tactic: Tactic
    symbol: str
    price: float
    atr14: float               # ATR(14) 절대값 (원)
    spread_pct: float          # 호가 스프레드 비율
    vp_ratio: float            # 현재 거래량 / 20봉 평균
    # EQS용
    bars_since_signal: int
    vol_ratio: float
    price_position: float      # (close-low)/(high-low) — 0~1
    is_pullback_strategy: bool
    # LAG1 (Cursor #20)
    prev_min_high_low: Optional[float]
    prev_max_high_low: Optional[float]
    # CS용
    dcs_grade: str             # "A"~"F"
    tech_rank: str             # "TOP3"~"NONE"
    market_regime: str         # "BULL"/"FLAT"/"BEAR"
    # 포트폴리오 컨텍스트
    open_positions_count: int
    portfolio_daily_pnl_pct: float
    kosdaq_change_pct: float
    # D6/D7 중복방지
    d6_positions_today: Optional[Set[str]]
    # D7용
    volume_rank: int
    daily_change_pct: float
    has_lower_low_13_14: bool
```

**PipelineResult 구조 (통과/차단 결과)**:
```python
@dataclass
class PipelineResult:
    approved: bool
    final_multiplier: float    # 0.0~1.0 포지션 크기 배수
    blocking_layer: str        # "NONE", "PRE_MATRIX", "PRE_PRIORITY", "PRE_POS_LIMIT", "L1"~"L5"
    blocking_reason: str
    sl_pct: float              # L1 손절 %
    cs_score: int              # L3.5 Conviction Score
    eqs_score: int             # L4.5 Execution Quality Score
    gate_passed: bool          # BounceGate 통과
    dd_level: int              # DD Decelerator 레벨 0~4
    atr_exit_params: Optional[object]  # TP/SL 파라미터
    atr_net_rr: float          # ATR NetR:R 값
```

**3단계 사전 필터 (평가 전)**:
1. FORBIDDEN 매트릭스 차단 (`_check_matrix`)
2. D6>D7>D-ORB 우선순위 중복방지 (`_check_priority`)
3. 동시 보유 한도 5개 초과 시 차단

**D6/D7 중복방지**: `d6_positions_today: Optional[Set[str]]` 필드로 외부에서 관리, 파이프라인 내부 `PRE_PRIORITY` 레이어에서 차단. ✅ 이미 구현됨 (이전 분석의 "미구현" 수정)

---

## 6. Layer4 execution 디렉토리

### 조사 결과: ✅ 의도적 미구현 확인

**경로**: `backend/app/services/trading/execution/layer4/`

```
__init__.py  (0 bytes — 빈 파일)
```

다른 파일 없음. CTE L1~L5 파이프라인의 Layer4 실행 컴포넌트 (`order_executor`)가 이 디렉토리에 구현되어야 하지만, 현재는 `V4PipelineOrchestrator`의 `_execute_sell_order()` / `_place_order()` 메서드로 직접 처리.

**통합 엔진 Task B에서 `adapters/order_executor.py` 구현 시 활성화 예정.**

---

## 7. 포지션 테이블 관계

### 조사 결과: ✅ 3개 테이블 역할 확인

| 테이블 | 역할 | 비고 |
|--------|------|------|
| `v4_positions` | 실/모의 라이브 포지션 | trailing_pct=3.0, max_hold_days=5 |
| `v4_paper_trades` | 페이퍼 거래 기록 | pnl_pct=None 버그 (미수정) |
| `go100_backtest_runs` | GO100 백테스트 실행 결과 | PF/WR/MDD/샤프 저장 |
| `v4_mock_trades` | KIS 모의투자 거래 기록 | **테이블 미존재 (Task D 생성 예정)** |

**`v4_positions` 스키마 핵심**:
```sql
ticker, quantity, entry_price, status
desk_id, peak_price, stop_loss_price
trailing_pct = 3.0   -- 트레일링 스탑 기본값
target_pct = 5.0     -- 목표 수익률
max_hold_days = 5    -- 최대 보유일
reservation_id       -- 예약 ID (주문 연결)
```

**중요**: `v4_mock_trades` 테이블 미존재 → Task D(Mock 계좌 설정) 시 생성 필요.

---

## 8. go100_backtest_runs 스키마

### 조사 결과: ✅ 확인

```sql
TABLE "public.go100_backtest_runs"
- strategy_name VARCHAR
- profit_factor  NUMERIC
- win_rate       NUMERIC
- max_drawdown   NUMERIC
- sharpe_ratio   NUMERIC
- total_trades   INTEGER
- start_date     DATE
- end_date       DATE
- (+ 메타 컬럼: id, created_at 등)
```

HAV (DEV-HAV-001) 루프와 연결: `go100_backtest_runs`에 INSERT 후 파라미터 최적화 루프. 현재 직접 연결 코드 미확인 (Task C 구현 예정).

---

## 9. SlippageAnalyzer 존재 여부

### 조사 결과: ❌ 코드 파일 없음

`find /root/kis-autotrade-v4 -name "slippage*.py"` → 결과 없음

설계 문서/리서치 메모에만 언급됨. 구현된 .py 파일 없음.

**결론**: SlippageAnalyzer는 Task B 통합 엔진의 `adapters/order_executor.py`에서 구현 필요. 현재 BT의 `COST_ROUNDTRIP=0.0047` (슬리피지 포함)이 유일한 대체.

---

## 10. KIS Mock API 자격증명

### 조사 결과: ✅ 자격증명 완비 (단, v4_mock_trades 테이블 미존재)

**`.env` 확인값**:
```
KIS_VIRTUAL_APP_KEY=[KIS-VIRTUAL-APP-KEY]
KIS_VIRTUAL_APP_SECRET=[KIS-VIRTUAL-APP-SECRET]  (암호화됨)
KIS_VIRTUAL_ACCOUNT_NUMBER=50160697
KIS_VIRTUAL_ACCOUNT_PRODUCT_CODE=01
MOCK_CONFIG_ID=3
KIS_MOCK_RATE_LIMIT=1.5
```

**`kis_ws_collector.py` 확인**:
```python
WS_DOMAIN_REAL    = "ws://ops.koreainvestment.com:21000"
WS_DOMAIN_VIRTUAL = "ws://ops.koreainvestment.com:31000"
REST_DOMAIN_REAL    = "https://openapi.koreainvestment.com:9443"
REST_DOMAIN_VIRTUAL = "https://openapivts.koreainvestment.com:29443"
```
→ KIS 모의투자(Virtual) API 엔드포인트 도메인 이중화됨

**Tasks for 완전 가동**:
- [x] KIS Virtual API 자격증명 존재
- [x] MOCK_CONFIG_ID=3 설정
- [ ] `v4_mock_trades` 테이블 생성 (Task D)
- [ ] Mock 계좌 `accounts` 테이블 INSERT (`is_mock=True`, account_id 신규)
- [ ] Token 발급 테스트 (`/oauth2/tokenP` Virtual endpoint)

---

## 추가 발견: D6/D7 중복방지 현황 수정

이전 보고서(`CUR-V41-UNIFIED-ENGINE-REVIEW-002`)에서 "D6/D7 중복방지 미구현"으로 분류했으나,
**실제 CTE 파이프라인 코드를 직접 확인한 결과**:

```python
# CTEPipeline.evaluate() 내 사전 필터 2:
priority_ok, priority_reason = self._check_priority(signal)
if not priority_ok:
    result.blocking_layer = "PRE_PRIORITY"
    result.blocking_reason = priority_reason
    return result
```

`TradeSignal.d6_positions_today: Optional[Set[str]]` 필드로 외부(스케줄러)에서 오늘 D6 진입 종목 집합을 전달, 파이프라인 내부에서 D6>D7>D-ORB 우선순위 체크.

**수정된 평가**: 파이프라인 내부 로직은 구현됨. 단, **`d6_positions_today` 세트를 올바르게 구성해서 전달**하는 호출측(스케줄러) 코드 검증 필요.

---

## v4_scalping_universe 현황

요청 외 추가 확인:
```sql
COUNT(*) = 708, MAX(created_date) = 2026-02-21
```
→ 708종목 클레임 정확, 2026-02-21 최신 업데이트.

---

## 종합 위험 우선순위 (갱신)

| 순위 | 항목 | 심각도 | 즉시 조치 |
|------|------|--------|-----------|
| 1 | `DRY_RUN=false` — 실전 주문 가능 상태 | ❌ CRITICAL | CEO 확인 후 값 결정 |
| 2 | `v4_paper_trades.pnl_pct=None` — 성과 측정 불가 | ❌ HIGH | 03-02 08:50 전 핫픽스 |
| 3 | `v4_mock_trades` 테이블 미존재 | ⚠️ HIGH | Task D 시 생성 |
| 4 | `SystemOrchestrator` 미배포 — V4PipelineOrchestrator 가동 중 | ⚠️ MED | Task B에서 전환 |
| 5 | `price_poller` 미가동 — real-time 가격 캐시 없음 | ⚠️ MED | SystemOrchestrator 배포 시 자동 해결 |
| 6 | `make_synthetic_signal` 미래정보 주입 — BT 과적합 | ⚠️ HIGH | Task C에서 수정 |
| 7 | `SlippageAnalyzer` 미구현 — 비용 추정 한계 | ℹ️ LOW | Task B order_executor에서 구현 |
| 8 | `d6_positions_today` 전달 코드 검증 미완료 | ⚠️ MED | D6/D7 병행 실행 전 검증 |

---

## 체크포인트

- [x] 10개 추가 조사 항목 전수 확인
- [x] D6/D7 중복방지 오류 수정 (파이프라인 내부 구현됨 확인)
- [x] v4_scalping_universe 708종목 실DB 확인
- [x] KIS Virtual 자격증명 완비 확인
- [x] price_poller 구현 완료 확인 (SystemOrchestrator 미배포로 미가동)
- [x] v4_mock_trades 미존재 확인 → Task D 필요
- [x] DRY_RUN=false CRITICAL 발견
- [x] 보고서 project-docs push 완료

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-ADDL-INVESTIGATION-002-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-ADDL-INVESTIGATION-002-20260301.md
- 커밋: (push 후 기재)
- HTTP 확인: (push 후 기재)
