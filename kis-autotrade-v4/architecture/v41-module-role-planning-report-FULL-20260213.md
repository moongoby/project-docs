# KIS AutoTrade V4.1 — 모듈별 세부 역할 및 기획 보고서 (전문)

**보고일:** 2026-02-13  
**보고자:** Claude (Architecture Lead)  
**수신:** 대표님 (CEO)

---

## 목차

1. 시스템 전체 비유 — "자동매매 회사 조직도"
2. LAYER 0 — System Orchestrator (사장실)
3. LAYER 1-A — Market Regime Detector (거시경제 리서치팀)
4. LAYER 1-B — Market Calendar (일정 관리 비서)
5. LAYER 2-A — Chief Analyst (리서치센터장)
6. LAYER 2-B — Fund Commander (자금운용본부장)
7. LAYER 3 — Market Brain / 5 DESK (5개 트레이딩 데스크)
8. LAYER 4 — Strategy Engine (전략 실행팀)
9. LAYER 5-A — Risk Manager 2계층 (리스크관리본부)
10. LAYER 5-B — Order Executor (주문 집행팀)
11. LAYER 5-C — Fund Pool + Reservation (금고)
12. LAYER 6 — Position Manager (포지션 감시탑)
13. LAYER 7 — Adaptive Engine (학습/진화팀)
14. INFRA-A — Data Provider + Price Poller (정보수집팀)
15. INFRA-B — Data Quality Tracker (품질검사관)
16. INFRA-C — Fault Injection (모의훈련팀)
17. INFRA-D — 운영 지표 + 알림 (관제센터)
18. 모듈 간 데이터 흐름 전체도
19. 모듈별 DB 테이블 매핑
20. 모듈별 구현 우선순위 + Phase 배치

---

## 1. 시스템 전체 비유 — "자동매매 회사 조직도"

```
╔══════════════════════════════════════════════════════════════════════════╗
║  이 시스템은 "자동매매 투자회사"입니다.                                  ║
║  각 모듈은 이 회사의 부서이고, 각자 명확한 역할이 있습니다.             ║
║                                                                          ║
║  ┌──────────────────────────────────────────────────────────────┐       ║
║  │                    ★ 사장실 (Orchestrator)                     │       ║
║  │                    "회사 전체를 지휘한다"                      │       ║
║  │                    출근/퇴근 시간 관리, 부서별 업무 순서 통제   │       ║
║  │         ┌──────────────┐    ┌──────────────┐                  │       ║
║  │         │ 거시경제      │    │ 일정관리     │                  │       ║
║  │         │ 리서치팀      │    │ 비서         │                  │       ║
║  │         │ (Regime)      │    │ (Calendar)   │                  │       ║
║  │         └──────┬───────┘    └──────┬───────┘                  │       ║
║  │                ▼                    ▼                          │       ║
║  │  ┌────────────────────────────────────────────┐               │       ║
║  │  │              사령부 (Command Center)         │               │       ║
║  │  │  리서치센터장 (Chief Analyst)                │               │       ║
║  │  │  자금운용본부장 (Fund Commander)             │               │       ║
║  │  └──────────────────┬─────────────────────────┘               │       ║
║  │                      ▼                                         │       ║
║  │  ┌──────────────────────────────────────────┐                 │       ║
║  │  │         5개 트레이딩 데스크                │                 │       ║
║  │  │  DESK 1~5: 초단기·데일리·단기·중기·장기   │                 │       ║
║  │  └──────────────────┬───────────────────────┘                 │       ║
║  │                      ▼                                         │       ║
║  │  ┌──────────────────────────────────────────┐                 │       ║
║  │  │          전략 실행팀 (Strategy Engine)     │                 │       ║
║  │  └──────────────────┬───────────────────────┘                 │       ║
║  │       ┌──────────────┼──────────────┐                         │       ║
║  │       ▼              ▼              ▼                         │       ║
║  │  ┌─────────┐  ┌──────────┐  ┌──────────┐                    │       ║
║  │  │리스크   │  │주문집행  │  │ 금고     │                    │       ║
║  │  │관리본부 │  │팀        │  │ FundPool │                    │       ║
║  │  └─────────┘  └──────────┘  └──────────┘                    │       ║
║  │                      ▼                                         │       ║
║  │  ┌──────────────────────────────────────────┐                 │       ║
║  │  │        포지션 감시탑 (Position Manager)    │                 │       ║
║  │  │        ★ 절대 죽으면 안 되는 핵심 모듈    │                 │       ║
║  │  └──────────────────┬───────────────────────┘                 │       ║
║  │                      ▼                                         │       ║
║  │  ┌──────────────────────────────────────────┐                 │       ║
║  │  │        학습/진화팀 (Adaptive Engine)       │                 │       ║
║  │  └──────────────────────────────────────────┘                 │       ║
║  │  ┌──────────────────────────────────────────┐                 │       ║
║  │  │  인프라: 정보수집·품질검사·관제·모의훈련  │                 │       ║
║  │  └──────────────────────────────────────────┘                 │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 2. LAYER 0 — System Orchestrator (사장실)

**한 줄 요약:** 회사의 출퇴근 시간을 관리하고, 모든 부서의 업무 순서를 통제하며, 비상 상황에서 지휘권을 행사하는 사장실.

**왜 필요한가:** 의도하지 않은 시점에 의도하지 않은 동작이 실행되는 것을 막기 위함. Orchestrator가 없으면 모듈 간 실행 순서가 꼬여 자금 손실로 이어질 수 있음.

### 역할 1: 시간 기반 상태 전이

| 시각    | 상태 전이      | 동작 |
|--------|----------------|------|
| 07:55  | PRE_MARKET 진입 | 출근. 전일 데이터 수집, 레짐·캘린더·유니버스·자금 갱신 |
| 08:50  | READY 전환 시도 | V4.1 불변조건 7개 체크. 실패 시 DEGRADED_READY |
| 09:00  | TRADING 전환   | 장 시작. KIS API 연결 확인 필수 |
| 15:20  | CLOSING 전환   | 신규 진입 차단, order_executor 매수 차단 플래그 |
| 15:30  | POST_MARKET    | 미체결 주문 0건 확인 후 전환 |
| 15:45  | IDLE           | 퇴근. 내일 알람 설정 |

### 역할 2: 60초 사이클 실행 순서

```
[1] cycle_lock 획득 (이전 사이클 완료 확인)
[2] position_manager.check_positions() — 청산 먼저
[3] fund_commander.refresh_available() — 자금 갱신 (V4.1: DB 기반 재계산)
[4] strategy_engine.run_strategies() — 신호 생성
[5] 신호별: 자금확인→리스크→주문→포지션 생성
[6] cycle_lock 해제 + 운영 지표 기록
```

이전 사이클 미완료 시 이번 사이클 skip + 경고. 사이클 60초 초과 시 경고, 연속 3회 초과 시 알림.

### 역할 3: 상태 전이 불변조건 (V4.1)

PRE_MARKET → READY 검증 예시:

```python
class StateTransitionValidator:
    async def validate_pre_to_ready(self) -> TransitionResult:
        checks = [
            ("universe_loaded", self.universe.stock_count > 0),
            ("fund_pool_ready", self.fund_pool.is_rebuilt_from_db),
            ("price_poller_live", self.price_poller.last_heartbeat < 30),
            ("position_manager_healthy", self.position_mgr.is_healthy),
            ("regime_determined", self.regime.score is not None),
            ("calendar_checked", self.calendar.adjustment is not None),
            ("data_quality_ok", self.quality.grade >= GRADE_B),
        ]
        failed = [(name, ok) for name, ok in checks if not ok]
        if failed:
            return TransitionResult(
                allowed=False,
                fallback_state="DEGRADED_READY",
                failed_checks=failed
            )
        return TransitionResult(allowed=True)
```

### 역할 4: heartbeat 관리

매 30초마다 `v4_system_heartbeat` INSERT: timestamp, current_state, module_status, last_cycle_duration_ms, order_success_count, order_fail_count, max_price_staleness_ms. 외부 watchdog: 3분 부재 시 알림, 10분 부재 시 자동 재시작 시도.

### 역할 5: 장애 복구 (recovery_check)

PRE_MARKET 진입 시 필수 실행:

- **[0] V4.1 FundPool DB 재구성** — `fund_pool.rebuild_from_db()`
- **[1] KIS 실잔고 vs DB 포지션 대조** — 고아 포지션 생성 / 누락 청산 + 알림
- **[2] 만료 예약금 정리** — state=RESERVED 이면서 expires_at 지남 → EXPIRED, 자금 반환
- **[3] 손절가 이탈 즉시 체크** — 긴급 매도 + 알림
- **[4] 미체결 주문 정리** — 30분 이상 된 미체결 주문 자동 취소 + 알림

### 역할 6: 축소 운영 (DEGRADED)

원칙: "보유 포지션이 있는데 시스템이 죽으면 손절도 못 한다. 신규 진입만 막고 기존 포지션은 관리하자."  
Orchestrator가 degraded_modules를 관리하고, 장애 모듈 발견 시 해당 축소 정책 적용 + 알림.

### 역할 7: 상태 이력 기록

`v4_system_state_log`: from_state, to_state, transition_time, trigger_reason, validation_result. 사후 분석용.

**DB:** v4_system_state_log, v4_system_heartbeat  
**Phase:** Phase 1 완료, V4.1 불변조건 강화는 Phase 2-C

---

## 3. LAYER 1-A — Market Regime Detector (거시경제 리서치팀)

**한 줄 요약:** 지금 시장이 어떤 성격인가(추세/횡보/하락)를 판단하여 시스템 전체의 공격/방어 수위를 결정하는 거시 분석팀.

### 역할 1: 레짐 판정 (regime_score)

실행: PRE_MARKET, 하루 1회. 입력 6개 지표:

| 지표 | 계산 | 점수화 |
|------|------|--------|
| 코스피 20일 수익률 | (오늘 종가/20거래일 전 종가)-1 | +5% 이상→100점, -5% 미만→0점 등 |
| 이동평균 정렬 | 5MA·20MA·60MA 순서 | 정배열→100, 역배열→0 |
| 양봉 비율 | 20일 중 close>open 비율 | 비율×100 |
| 거래대금 추이 | 최근 5일/20일 평균 | 1.3 이상→100, 0.7 미만→0 |
| 외국인 순매수 20일 | daily_investor 합계 | 대규모 순매수→100, 순매도→0 |
| VKOSPI | v4_vkospi_daily | 15 미만→100, 25 초과→0 (없으면 5개 지표로만) |

최종 regime_score = 가중 평균 0~100.

### 역할 2: 레짐 라벨 매핑

- 80~100: STRONG_TREND_UP  
- 60~79: MILD_TREND_UP  
- 40~59: SIDEWAYS  
- 20~39: MILD_TREND_DOWN  
- 0~19: STRONG_TREND_DOWN  

각 레짐이 데스크 배분·bet_size modifier·손절/익절·진입 score 하한·현금 비중에 반영.

### 역할 3: V4.1 레짐 전환 히스테리시스

```python
class RegimeTransitionManager:
    def __init__(self):
        self.current_regime = "SIDEWAYS"
        self.pending_regime = None
        self.pending_days = 0

    def update(self, raw_regime: str) -> str:
        if raw_regime == self.current_regime:
            self.pending_regime = None
            self.pending_days = 0
            return self.current_regime
        if raw_regime == self.pending_regime:
            self.pending_days += 1
        else:
            self.pending_regime = raw_regime
            self.pending_days = 1
        required_days = self._get_required_days(self.current_regime, raw_regime)
        if self.pending_days >= required_days:
            self.current_regime = raw_regime
            self.pending_regime = None
            self.pending_days = 0
        return self.current_regime

    def _get_required_days(self, current, new):
        # STRONG_TREND_DOWN 진입 2일, 탈출 3일; 상승 전환 3일, 하향 전환 2일
        ...
```

### 역할 4: 레짐 이력 및 제공

`v4_market_regime_daily`: date, regime_score, regime_label, raw_regime, confirmed_regime, individual_scores, pending_transition.  
API: `get_current_regime()` → RegimeContext (regime_label, regime_score, desk_allocation, bet_modifier, sl_adjustment, tp_adjustment, min_entry_score, cash_target_pct).

**DB:** v4_market_regime_daily  
**Phase:** Phase 2-A 완료

---

## 4. LAYER 1-B — Market Calendar (일정 관리 비서)

**한 줄 요약:** 오늘 특수한 이벤트가 있는지 확인하고, 매매 강도를 자동 조절하는 일정 관리 비서.

**SYSTEM 자동 등록:** FOMC, BOK_RATE, FUTURES_EXPIRY(매월 둘째 목), QUAD_WITCHING, YEAR_END, YEAR_START, MSCI_REBALANCE, FTSE_REBALANCE, INDEX_REBALANCE, HOLIDAY_ADJACENT.  
**USER 수동:** LARGE_IPO, LOCKUP_EXPIRY, EX_DIVIDEND, EARNINGS, USER_CUSTOM.

**당일 조회:** `get_today_adjustment(date)` → CalendarAdj(bet_modifier, desk_active, class_restrictions, events). 복수 이벤트 시 bet_modifier=min(각 modifier), desk_active=모두 True여야 활성.  
**종목 제한:** target_ticker 있으면 해당 종목만; `check_stock_restriction(ticker, date)`.

**연초 생성:** `python manage.py generate_calendar --year 2026` — 선물 만기·네 마녀·연말연초·공휴 전후일.

**DB:** v4_market_calendar  
**Phase:** Phase 2-B 진행 중

---

## 5. LAYER 2-A — Chief Analyst (리서치센터장)

**한 줄 요약:** 5개 데스크의 분석 결과를 취합하고, 레짐/캘린더를 반영하여 today_universe를 확정.

- 5 DESK 추천 취합 → desk_recommendations (ticker, stock_class, universe_score, confidence, desk_id, individual_scores)
- 레짐 기반 필터링: 비활성 데스크 제외, min_entry_score 미달 제외, CLASS 제한
- 캘린더 기반 필터링: desk_active, class_restrictions, 종목 restriction
- today_universe 확정 + V4.1 버전화: universe_id, v4_universe_version (generated_at, regime, calendar_adj, data_quality, inputs_hash, stock_count, version_seq). inputs_hash 동일 시 재생성 skip
- 장중 5분 주기: 개별 종목 status·universe_score만 갱신; 레짐·캘린더·데스크 활성은 고정

**Phase:** Phase 2-C

---

## 6. LAYER 2-B — Fund Commander (자금운용본부장)

**한 줄 요약:** 각 매매에 얼마를 걸 것인가(bet_size)를 레짐·무드·캘린더·데이터 품질·신뢰도를 반영해 계산.

**bet_size 공식 (ROCKET 100만원 기준):**

```
base_pct = 25%
adjusted = base_pct × regime_modifier × mood_modifier × calendar_modifier
           × confidence_modifier × data_quality_modifier
final_pct = max(10%, min(40%, adjusted))
bet_amount = total_capital × final_pct / 100
```

레짐: STRONG_UP×1.15, MILD_UP×1.0, SIDEWAYS×0.8, MILD_DOWN×0.5, STRONG_DOWN×0.0.  
mood_modifier = mood_score/65 (cap 0.5~1.2). confidence: HIGH×1.0, MEDIUM×0.7, LOW×0.5. data_quality: A×1.0, B×0.9, C×0.7, D×0.0.

**데스크별 배분:** regime → desk_allocation_pct → desk_limits. can_allocate(desk_id, amount)로 한도 체크.  
**V4.1 DB 기반:** 매 사이클 `fund_pool.rebuild_from_db()`; available = total_capital - reserved - invested. 불변식 위반 시 경고 + 매매 중단.  
**경합 해소:** score 순 배분. **기록:** v4_bet_history.

**DB:** v4_bet_history, v4_fund_pool_snapshot, v4_reservations  
**Phase:** Phase 2-C

---

## 7. LAYER 3 — Market Brain / 5 DESK (5개 트레이딩 데스크)

**한 줄 요약:** 시장을 5가지 시간축으로 분석해 각 시간축에 맞는 매매 후보를 발굴·분류(CLASS)하는 5개 전문 데스크.

| 데스크 | 시간축 | 주요 CLASS | 비고 |
|--------|--------|------------|------|
| DESK 1 | 수분~수시간 | CLASS-B | 갭 상승+5분봉, 손절 -1%~-2%, 상승장에서만 활성 |
| DESK 2 | 당일~익일 | CLASS-A,B,C | 5대 스코어링, ROCKET 주력 |
| DESK 3 | 2~5일 | CLASS-K,V | 박스·변동성 돌파, ROCKET 활성 |
| DESK 4 | 1~3주 | - | ROCKET 비활성 |
| DESK 5 | 1~3개월 | - | ROCKET 비활성 |

**5대 스코어링:** supply 35%, sector 20%, theme 15%, volume 15%, tech 15%. universe_score = Σ(개별×가중치).  
**승격:** D2→D3(+3%), D3→D4(+5%), D4→D5(+10%) 조건 시 손절/목표/보유기간 변경.

**Phase:** Phase 2-D → Phase 3

---

## 8. LAYER 4 — Strategy Engine (전략 실행팀)

**한 줄 요약:** today_universe 안의 종목에 대해 "지금 사야 하는가"를 판단하고 매수/매도 신호를 생성.

- **CLASS별 전략:** CLASS-A(수급 반전+기술 돌파), CLASS-B(갭+확인봉), CLASS-C(종가 베팅), CLASS-K(박스 돌파), CLASS-V(변동성 돌파). 각 진입 조건·신호 강도 정의.
- **Signal Aggregator:** raw_signals 수집 → priority_score 기준 정렬 → ticker 기준 중복 제거.
- **V4.1 멱등성:** idempotency_key = `{today}_{cycle_id}_{ticker}_{action}`. v4_order_requests에 UNIQUE; 존재 시 skip.
- **시간대:** NOISE(09:00~09:05) 비활성, INITIAL(09:05~09:15) CLASS-B만, DEVELOPING(09:15~09:30) A·B, RELIABLE(09:30~14:30) 전 CLASS, CLOSING(14:30~15:20) CLASS-C만.
- **ReentryGuard:** 당일 손절 재매수 금지; 당일 3회 이상 매매 금지; 당일 익절 재매수 시 confidence 하향.

**Phase:** Phase 2-D → Phase 3

---

## 9. LAYER 5-A — Risk Manager 2계층 (리스크관리본부)

**한 줄 요약:** 이 매매를 실행해도 안전한지 검사. 2계층 분리로 Full이 죽어도 핵심 손절은 유지.

**계층 1 — CriticalRiskKernel (position_manager 내장):**

- 손절가 이탈 → FORCE_SELL IMMEDIATE  
- 최대 손실 초과(기본 -5%) → FORCE_SELL  
- 일일 손실 한도(기본 -3%) → CLOSE_ALL  
- 가격 불명 60초 초과 → CONSERVATIVE_SELL  
의존성 최소화(critical_risk_config만). strategy/data_provider/fund_commander 비의존.

**계층 2 — Full RiskManager:**

- pre_trade_check: 최대 포지션 수, 1종목 1포지션, ReentryGuard, 자금 가용성, 데스크 한도, 데이터 품질, 캘린더 제한. 통과 시 예약금 생성.
- 예약금 상태: RESERVED → ORDER_SUBMITTED → FILLED/FAILED/PARTIAL/EXPIRED.
- 레짐/무드에 따라 max_positions 등 조정.

**Phase:** Full Phase 3, CRK Phase 5

---

## 10. LAYER 5-B — Order Executor (주문 집행팀)

**한 줄 요약:** 리스크 통과 신호를 KIS API로 실제 주문·체결 확인·시스템 반영.

**execute_buy 흐름:** (1) 수량 = bet_amount // current_price; 0이면 예약금 RELEASED 반환. (2) 예약금 state → ORDER_SUBMITTED. (3) KIS API 호출(rate_limiter, 시장가). (4) 주문번호·v4_order_requests 기록. (5) wait_for_fill(타임아웃 30초), 체결 시 fill_price·fill_qty·slippage 기록; 타임아웃 시 취소·CANCELLED.  
**매도:** 예약금 없음; 체결 시 fund_pool 반환, 포지션 CLOSED.  
**매수 차단:** CLOSING 시 set_buy_blocked(True). CLASS-C는 15:20 전까지 예외.  
**KIS 토큰:** PRE_MARKET 갱신, 만료 감지 시 자동 갱신, 실패 시 DEGRADED+알림.

**DB:** v4_order_requests, v4_reservations  
**Phase:** Phase 3 → Phase 4(WebSocket)

---

## 11. LAYER 5-C — Fund Pool + Reservation (금고)

**한 줄 요약:** total_capital = available + reserved + invested 불변식, DB 기반 자금 관리.

**V4.1 rebuild_from_db:**

```python
async def rebuild_from_db(self):
    self.reserved = await db.scalar(
        "SELECT COALESCE(SUM(amount), 0) FROM v4_reservations "
        "WHERE state IN ('RESERVED', 'ORDER_SUBMITTED') AND user_id = :uid", ...
    )
    self.invested = await db.scalar(
        "SELECT COALESCE(SUM(entry_price*quantity), 0) FROM positions "
        "WHERE status = 'OPEN' AND user_id = :uid", ...
    )
    self.available = self.total_capital - self.reserved - self.invested
    assert self.available >= 0
    assert self.available + self.reserved + self.invested == self.total_capital
    self.is_rebuilt_from_db = True
```

**Reservation 상태:** RESERVED → ORDER_SUBMITTED → FILLED / FAILED / PARTIAL / EXPIRED. FILLED 시 reserved→invested; FAILED/EXPIRED 시 reserved→available.  
**데스크:** desk_used, desk_limits, can_allocate(desk_id, amount).  
**만료 정리:** cleanup_expired_reservations() — RESERVED & expires_at < NOW() → EXPIRED, 자금 반환.

**DB:** v4_reservations, v4_fund_pool_snapshot  
**Phase:** Phase 2-C → Phase 3

---

## 12. LAYER 6 — Position Manager (포지션 감시탑)

**한 줄 요약:** 보유 포지션 실시간 감시, 손절/익절/트레일링/승격/강제청산. CriticalRiskKernel 내장. **절대 죽으면 안 되는 모듈.**

**check_positions (60초 사이클 1순위):**

1. CriticalRiskKernel 검사 → critical 시 execute_critical_action (FORCE_SELL/CLOSE_ALL/CONSERVATIVE_SELL)
2. peak_price 갱신 후 트레일링 스톱 체크 → 청산
3. 목표 수익 도달 → 청산
4. 최대 보유 기간 초과 → 청산
5. 승격 조건 → transfer_desk

**sell:** order_executor.execute_sell 호출. 실패 시 handle_sell_failed → 지정가→IOC→시장가 단계적 재시도(최대 3분), 모두 실패 시 수동 알림.

**fallback_sell:** order_executor 장애 시 position_manager가 직접 KIS 시장가 매도. (1) 매도 전용 (2) 동일 RateLimiter 공유 (3) v4_order_requests에 source='EMERGENCY_FALLBACK' 기록 + 알림.

**close_position:** DB status=CLOSED, exit_price·exit_reason·realized_pnl, fund_pool.release, trade_analyzer.record.  
**CLOSING 시:** 당일 청산 대상 강제 청산, CLASS-C 오버나잇만 유지.

**DB:** positions, v4_position_extended, v4_order_requests  
**Phase:** Phase 3 → Phase 5(CRK+fallback)

---

## 13. LAYER 7 — Adaptive Engine (학습/진화팀)

**한 줄 요약:** 과거 매매 결과로 스코어링 가중치·전략 파라미터·데스크 배분을 자동 보정.

- **모듈 1 (매주):** 스코어링 가중치. V4.1 지수감쇠(4주 1.0, 5~8주 0.5, 9~12주 0.25). V4.1 레짐 조건부 가중치. 50건 미만이면 보정 안 함. 변경폭 ±5%, 최소 5%.
- **모듈 2 (매주):** 손절/익절/보유기간 롤링 최적화. 주당 ±1% 또는 ±1일.
- **모듈 3 (매월):** 데스크 배분. Calmar Ratio 기반. 월 ±3%, 대폭 변경 시 승인.
- **모듈 4:** Trade Analyzer — 진입·보유·청산·사후 24h 상세 기록, universe_id·order_request_id 연결.
- **모듈 5:** 과적합 방지 — 변경폭 상한, 최소 50건, 9주 학습+3주 검증, 원점 회귀 감지, 수동 오버라이드.

**DB:** v4_trade_analysis, v4_scoring_weights  
**Phase:** Phase 5

---

## 14. INFRA-A — Data Provider + Price Poller (정보수집팀)

**한 줄 요약:** 시세·수급·섹터·지수 수집·제공, 실시간/백테스트 동일 인터페이스.

**DataProvider:** get_current_price, get_daily_ohlcv, get_minute_candles, get_supply_demand, get_sector_momentum, get_market_index.  
**LiveDataProvider:** PricePoller 캐시 + KIS. **BacktestDataProvider:** sim_time 기준, date <= sim_date로 미래 참조 차단, 슬리피지 시뮬레이션.

**V4.1 PricePoller:** 캐시 `{ price, ts, source, staleness_ms }`. 병렬 수집 + Semaphore(5). 보유 포지션 5초, universe 10초. 우선순위 EMERGENCY > ORDER > NORMAL.  
**KIS Rate Limiter:** 초당 20회, 동시 5개. Order Executor·fallback과 동일 인스턴스 공유.

**Phase:** Phase 1 → Phase 4

---

## 15. INFRA-B — Data Quality Tracker (품질검사관)

소스별 status(LIVE/STALE/FALLBACK/DEAD), last_success, fail_count.  
등급: GRADE_A(전부 LIVE), B(1~2 STALE → bet×0.9), C(1+ FALLBACK → bet×0.7, 알림), D(핵심 DEAD → DEGRADED, 신규 진입 중단).  
3단계 폴백: 실시간 → 캐시(×0.8) → 해당 요소 제외 재분배.  
heartbeat에 data_quality_grade 기록.

**Phase:** Phase 4

---

## 16. INFRA-C — Fault Injection (모의훈련팀)

FAULT_INJECTION=false(기본). true 시에만 동작.  
FAULT_KIS_TIMEOUT, FAULT_DB_DELAY, FAULT_PRICE_STALE, FAULT_ORDER_REJECT. @fault_injectable 데코레이터. 실거래·실계좌 키와 동시 사용 차단.

**Phase:** Phase 5

---

## 17. INFRA-D — 운영 지표 + 알림 (관제센터)

**V4.1 최소 지표 4종:** order_success_count, order_fail_count; fill_latency_ms; price_staleness_ms; cycle_duration_ms.  
**알림:** INFO(로그), WARNING(일일 리포트), CRITICAL(즉시). 동일 유형 5분 쿨다운(CRITICAL 제외).  
**일일 리포트:** 요약·매매 내역·보유 포지션·시장 환경·시스템 건강·자금 현황.

**Phase:** Phase 3 → Phase 5

---

## 18. 모듈 간 데이터 흐름 전체도

**PRE_MARKET:** recovery_check → DataProvider → Regime → Calendar → 5 DESK → Chief Analyst(today_universe) → Fund Commander(desk_limits).

**TRADING (60초):** cycle_lock → Position Manager(청산) → Fund Commander(rebuild_from_db) → Strategy Engine(signals) → 신호별 idempotency → Fund Commander(bet) → Risk(pre_trade, 예약금) → Order Executor → Position Manager(포지션 생성) → 운영 지표 → cycle_lock 해제.

**POST_MARKET:** Trade Analyzer, Adaptive 데이터 축적, 일일 리포트, daily_capital_state, 알림.

**주간/월간:** Adaptive 가중치·파라미터·데스크 배분 보정.

---

## 19. 모듈별 DB 테이블 매핑

| 모듈 | 사용 테이블 | 읽기/쓰기 |
|------|-------------|-----------|
| Orchestrator | v4_system_state_log, v4_system_heartbeat | 쓰기 |
| Regime Detector | index_daily, daily_investor, v4_vkospi_daily, v4_market_regime_daily | 읽기+쓰기 |
| Market Calendar | v4_market_calendar | 읽기+쓰기 |
| Chief Analyst | v4_universe_version | 쓰기 |
| Fund Commander | v4_reservations, positions, v4_fund_pool_snapshot, v4_bet_history | 읽기/쓰기 |
| 5 DESK | daily_stock, daily_investor, sector_daily, v4_theme_* | 읽기 |
| Strategy Engine | v4_order_requests | 읽기+쓰기 |
| Risk Manager | v4_reservations, positions, v4_market_calendar | 읽기+쓰기 |
| Order Executor | v4_order_requests, v4_reservations | 읽기+쓰기 |
| FundPool | v4_reservations, positions, v4_fund_pool_snapshot | 읽기/쓰기 |
| Position Manager | positions, v4_position_extended, v4_order_requests | 읽기+쓰기 |
| Adaptive Engine | v4_trade_analysis, v4_scoring_weights | 읽기+쓰기 |

레거시 테이블 읽기 전용. V4 테이블만 쓰기 허용.

---

## 20. 모듈별 구현 우선순위 + Phase 배치

| Phase | 내용 |
|-------|------|
| 0 | Modernization 완료 |
| 1 | Core Skeleton 완료 |
| 2-A | Regime Detector 완료 |
| 2-B | Market Calendar 진행 중(10%) |
| 2-C | Command Center — Chief Analyst, Fund Commander, FundPool DB=SoT, ReservationState, idempotency_key, 레짐 히스테리시스 |
| 2-D | DESK 2/3, 5대 스코어링, 테마 활성도 |
| 3 | Strategy Engine, Risk(Full), ReentryGuard, Order Executor, Position Manager 기본, SELL_FAILED 재시도, 운영 지표 4종, 알림, 일일 리포트 |
| 4 | Live/Backtest DataProvider, PricePoller 강화, Quality Tracker, WebSocket, mood 연속값 |
| 5 | CriticalRiskKernel, fallback 청산, PrioritySemaphore, Adaptive 모듈 1·2·3, Trade Analyzer, Fault Injection, Observability, DB 보관 정책 |
| 6 | 모의 계좌 → 실계좌 MANUAL_ASSIST → AUTO_LOCKED |

잔여 약 14주(병렬 시 12~13주). 예상 완료 2026년 5월 중순.

---

## 보고 요약

- **가장 중요한 모듈 3개(절대 불멸):** Position Manager, CriticalRiskKernel, FundPool. 이들이 살아있으면 보유 포지션 손절은 실행 가능.
- **가치 창출 핵심 3개:** 5 DESK 스코어링, Strategy Engine, Adaptive Engine.
- **다음 마일스톤:** Phase 2-B Market Calendar 완료 후 Phase 2-C에서 DB=SoT, ReservationState, idempotency_key, universe 버전화, 레짐 히스테리시스 구현.

---

*문서 버전: V4.1 | 보고일: 2026-02-13 | 전문 (FULL) | project-docs/kis-autotrade-v4/architecture*
