# KIS AutoTrade V4.1 — 모듈별 세부 역할 및 기획 보고서

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

이 시스템은 "자동매매 투자회사"입니다.  
각 모듈은 이 회사의 부서이고, 각자 명확한 역할이 있습니다.

- **사장실 (Orchestrator):** 회사 전체를 지휘, 출퇴근 시간 관리, 부서별 업무 순서 통제, 비상 상황 시 지휘
- **거시경제 리서치팀 / 일정관리 비서:** 레짐·캘린더
- **사령부 (Command Center):** Chief Analyst(어디서 싸울지), Fund Commander(얼마를 걸지)
- **5개 트레이딩 데스크:** DESK 1~5 (초단기·데일리·단기·중기·장기 스윙)
- **전략 실행팀:** 지금 사라/팔라 신호 생성
- **리스크관리본부 / 주문집행팀 / 금고(FundPool)**
- **포지션 감시탑:** 손절·익절·트레일링·승격 — 절대 죽으면 안 되는 핵심 모듈
- **학습/진화팀 (Adaptive Engine)**
- **인프라:** 정보수집팀, 품질검사관, 관제센터, 모의훈련팀

---

## 2. LAYER 0 — System Orchestrator (사장실)

**한 줄 요약:** 회사의 출퇴근 시간을 관리하고, 모든 부서의 업무 순서를 통제하며, 비상 상황에서 지휘권을 행사하는 사장실.

**왜 필요한가:** 의도하지 않은 시점에 의도하지 않은 동작이 실행되는 것을 막기 위함. Orchestrator가 없으면 모듈 간 실행 순서가 꼬여 자금 손실로 이어질 수 있음.

**세부 역할 7가지:**

1. **시간 기반 상태 전이:** 07:55 PRE_MARKET → 08:50 READY(불변조건 7개) → 09:00 TRADING → 15:20 CLOSING → 15:30 POST_MARKET → 15:45 IDLE
2. **60초 사이클 실행 순서 보장:** [청산 → 자금갱신 → 전략 → 주문] 순서 엄격 통제
3. **상태 전이 불변조건 (V4.1):** `StateTransitionValidator` — universe_loaded, fund_pool_ready, price_poller_live, position_manager_healthy, regime_determined, calendar_checked, data_quality_ok
4. **heartbeat 관리:** 30초마다 v4_system_heartbeat 기록 (current_state, module_status, last_cycle_duration_ms, order_success/fail_count, max_price_staleness_ms)
5. **장애 복구 (recovery_check):** FundPool DB 재구성, KIS 실잔고 vs DB 포지션 대조, 만료 예약금 정리, 손절가 이탈 즉시 체크, 미체결 주문 정리
6. **축소 운영 모드 (DEGRADED):** degraded_modules 관리, 장애 시 신규 진입만 막고 기존 포지션 관리
7. **상태 이력 기록:** v4_system_state_log (from_state, to_state, transition_time, trigger_reason, validation_result)

**DB 테이블:** v4_system_state_log, v4_system_heartbeat  
**구현 Phase:** Phase 1 완료, V4.1 불변조건 강화는 Phase 2-C

---

## 3. LAYER 1-A — Market Regime Detector (거시경제 리서치팀)

**한 줄 요약:** 지금 시장이 어떤 성격인가(추세/횡보/하락)를 판단하여 시스템 전체의 공격/방어 수위를 결정하는 거시 분석팀.

**세부 역할:**  
- 6개 지표로 regime_score 계산 (코스피 20일 수익률, 이동평균 정렬, 양봉 비율, 거래대금 추이, 외국인 순매수, VKOSPI)  
- regime_score → 5대 레짐 라벨 (STRONG_TREND_UP ~ STRONG_TREND_DOWN)  
- V4.1 레짐 전환 히스테리시스 (RegimeTransitionManager: 상향 전환 신중, 하락 진입/하락 탈출 비대칭)  
- v4_market_regime_daily 기록, get_current_regime() → RegimeContext 제공  

**DB:** v4_market_regime_daily  
**Phase:** Phase 2-A 완료

---

## 4. LAYER 1-B — Market Calendar (일정 관리 비서)

**한 줄 요약:** 오늘 특수한 이벤트가 있는지 확인하고, 매매 강도를 자동 조절하는 일정 관리 비서.

**세부 역할:**  
- 특수일 이벤트 등록 (SYSTEM: FOMC, BOK_RATE, FUTURES_EXPIRY, QUAD_WITCHING, YEAR_END/START, MSCI/FTSE/INDEX_REBALANCE, HOLIDAY_ADJACENT; USER: LARGE_IPO, LOCKUP_EXPIRY, EX_DIVIDEND, EARNINGS)  
- get_today_adjustment() → CalendarAdj (bet_modifier, desk_active, class_restrictions, events)  
- 종목 단위 이벤트 (target_ticker), check_stock_restriction(ticker, date)  
- 연초 일괄 생성 스크립트 (generate_calendar --year)  

**DB:** v4_market_calendar  
**Phase:** Phase 2-B 진행 중

---

## 5. LAYER 2-A — Chief Analyst (리서치센터장)

**한 줄 요약:** 5개 데스크의 분석 결과를 취합하고, 레짐/캘린더를 반영하여 오늘 매매할 종목 목록(today_universe)을 확정.

**세부 역할:**  
- 5 DESK 추천 취합 (desk_recommendations)  
- 레짐 기반 필터링 (비활성 데스크 제외, min_entry_score, CLASS 제한)  
- 캘린더 기반 필터링 (desk_active, class_restrictions, 종목 restriction)  
- today_universe 확정 + V4.1 버전화 (universe_id, v4_universe_version, inputs_hash로 재생성 skip)  
- 장중 5분 주기 갱신 (status, universe_score만; 레짐·캘린더는 고정)  

**Phase:** Phase 2-C

---

## 6. LAYER 2-B — Fund Commander (자금운용본부장)

**한 줄 요약:** 각 매매에 얼마를 걸 것인가(bet_size)를 레짐·무드·캘린더·데이터 품질·신호 신뢰도를 반영해 계산.

**세부 역할:**  
- 가변 bet_size: base_pct(25%) × regime_modifier × mood_modifier × calendar_modifier × confidence_modifier × data_quality_modifier, 상하한 10%~40%  
- 데스크별 자금 배분(desk_limits), V4.1 DB 기반 available 재계산 (rebuild_from_db)  
- 경합 해소(score 순 배분), v4_bet_history 기록  

**DB:** v4_bet_history, v4_fund_pool_snapshot, v4_reservations  
**Phase:** Phase 2-C

---

## 7. LAYER 3 — Market Brain / 5 DESK (5개 트레이딩 데스크)

**한 줄 요약:** 시장을 5가지 시간축으로 분석해 각 시간축에 맞는 매매 후보 종목을 발굴·분류(CLASS)하는 5개 전문 데스크.

- **DESK 1:** 초단기(수분~수시간), CLASS-B, 5분봉·갭 상승, 손절 -1%~-2%, 상승장에서만 활성  
- **DESK 2:** 데일리(당일~익일), CLASS-A/B/C, 5대 스코어링(supply 35%, sector 20%, theme 15%, volume 15%, tech 15%), ROCKET 주력  
- **DESK 3:** 단기 스윙(2~5일), CLASS-K/V, 박스·변동성 돌파, ROCKET 활성  
- **DESK 4/5:** 중기/장기 스윙, ROCKET 비활성(자금 확대 시 활성화)  

**포지션 승격:** D2→D3(+3%), D3→D4(+5%), D4→D5(+10%) 조건 및 손절/목표/보유기간 변경.

**Phase:** Phase 2-D (DESK 2,3) → Phase 3

---

## 8. LAYER 4 — Strategy Engine (전략 실행팀)

**한 줄 요약:** today_universe 안의 종목에 대해 "지금 사야 하는가"를 판단하고 매수/매도 신호를 생성.

**세부 역할:**  
- CLASS별 전략 실행 (CLASS-A 수급 반전+기술 돌파, CLASS-B 갭+확인봉, CLASS-C 종가 베팅, CLASS-K 박스 돌파, CLASS-V 변동성 돌파)  
- Signal Aggregator: 신호 집계·정렬·종목별 중복 제거  
- V4.1 멱등성(idempotency_key) 체크  
- 시간대별 전략 활성화 (NOISE/INITIAL/DEVELOPING/RELIABLE/CLOSING)  
- ReentryGuard: 당일 손절 재매수 금지, 3회 이상 매매 금지, 당일 익절 재매수 시 confidence 하향  

**Phase:** Phase 2-D → Phase 3

---

## 9. LAYER 5-A — Risk Manager 2계층 (리스크관리본부)

**한 줄 요약:** 이 매매를 실행해도 안전한지 검사. 2계층 분리로 Full이 죽어도 핵심 손절 기능은 유지.

- **계층 1 CriticalRiskKernel (position_manager 내장):** 손절가 이탈, 최대 손실 초과, 일일 손실 한도, 가격 불명 시 보수적 청산. strategy/data_provider/fund_commander 비의존.  
- **계층 2 Full RiskManager:** pre_trade_check(최대 포지션, 1종목 1포지션, ReentryGuard, 자금 가용성, 데스크 한도, 데이터 품질, 캘린더 제한), 예약금 관리, 레짐/무드 연동 파라미터.  

**Phase:** Full Phase 3, CRK Phase 5

---

## 10. LAYER 5-B — Order Executor (주문 집행팀)

**한 줄 요약:** 리스크 통과 신호를 KIS API로 실제 주문·체결 확인·시스템 반영.

**세부 역할:** execute_buy(수량 계산, 예약금 ORDER_SUBMITTED, KIS API 호출, wait_for_fill, v4_order_requests 기록), 매도 실행·체결 기록, CLOSING 시 매수 차단(CLASS-C 예외), KIS 토큰 관리. Phase 4에서 WebSocket 체결 연동 계획.

**DB:** v4_order_requests, v4_reservations  
**Phase:** Phase 3 → Phase 4(WebSocket)

---

## 11. LAYER 5-C — Fund Pool + Reservation (금고)

**한 줄 요약:** total_capital = available + reserved + invested 불변식, DB 기반 자금 관리.

**세부 역할:**  
- V4.1 rebuild_from_db (reservations + positions에서 reserved/invested 재계산)  
- Reservation 상태 머신: RESERVED → ORDER_SUBMITTED → FILLED/FAILED/PARTIAL/EXPIRED  
- 데스크별 사용량·desk_limits, can_allocate(), 만료 예약금 cleanup_expired_reservations  

**DB:** v4_reservations, v4_fund_pool_snapshot  
**Phase:** Phase 2-C(DB=SoT) → Phase 3(상태 머신)

---

## 12. LAYER 6 — Position Manager (포지션 감시탑)

**한 줄 요약:** 보유 포지션 실시간 감시, 손절/익절/트레일링/승격/강제청산 실행. CriticalRiskKernel 내장. **절대 죽으면 안 되는 모듈.**

**세부 역할:**  
- check_positions: CRK 검사 → 트레일링 스톱 → 목표 수익 → 최대 보유 기간 → 승격 조건  
- sell → order_executor 또는 fallback_sell(매도 전용, RateLimiter 공유, v4_order_requests source=EMERGENCY_FALLBACK)  
- V4.1 SELL_FAILED 단계적 재시도: 지정가 → IOC → 시장가 → 수동 알림  
- 포지션 승격/이관, close_position(DB 갱신, fund_pool 반환, trade_analyzer 기록), CLOSING 시 당일 청산 대상 강제 청산  

**DB:** positions, v4_position_extended, v4_order_requests  
**Phase:** Phase 3 → Phase 5(CRK+fallback)

---

## 13. LAYER 7 — Adaptive Engine (학습/진화팀)

**한 줄 요약:** 과거 매매 결과로 스코어링 가중치·전략 파라미터·데스크 배분을 자동 보정.

**세부 역할:**  
- 매주: 스코어링 가중치 보정(지수감쇠 4/8/12주, 레짐 조건부 가중치), 전략 파라미터 롤링 최적화(손절/익절/보유기간)  
- 매월: 데스크 성과 기반 배분(Calmar Ratio)  
- Trade Analyzer: 매매 상세·사후 24h 추적, universe_id 연결  
- 과적합 방지: 변경폭 상한, 최소 50건, 교차 검증, 원점 회귀 감지, 수동 오버라이드  

**DB:** v4_trade_analysis, v4_scoring_weights  
**Phase:** Phase 5

---

## 14. INFRA-A — Data Provider + Price Poller (정보수집팀)

**한 줄 요약:** 시세·수급·섹터·지수 데이터 수집·제공, 실시간/백테스트 동일 인터페이스.

- DataProvider: get_current_price, get_daily_ohlcv, get_minute_candles, get_supply_demand, get_sector_momentum, get_market_index  
- LiveDataProvider(PricePoller 캐시 + KIS), BacktestDataProvider(sim_time, 미래 참조 차단, 슬리피지 시뮬레이션)  
- V4.1 PricePoller: price/ts/source/staleness_ms 캐시, 병렬 수집 + Semaphore(5), 수집 주기·우선순위(EMERGENCY>ORDER>NORMAL)  
- KIS Rate Limiter: 초당 20회, 동시 5개 제한  

**Phase:** Phase 1 → Phase 4(병렬+staleness+WebSocket)

---

## 15. INFRA-B — Data Quality Tracker (품질검사관)

**한 줄 요약:** 데이터 신뢰도 실시간 추적, 품질 저하 시 매매 강도 자동 축소.

- 소스별 상태(LIVE/STALE/FALLBACK/DEAD), 전체 등급 GRADE_A/B/C/D  
- GRADE_D(핵심 소스 DEAD) 시 DEGRADED, 신규 진입 중단  
- 3단계 폴백, v4_system_heartbeat에 data_quality_grade 기록  

**Phase:** Phase 4

---

## 16. INFRA-C — Fault Injection (모의훈련팀)

**한 줄 요약:** 개발/모의 환경에서만 장애 주입으로 장애 대응 검증. 실거래에서는 절대 활성화 금지.

- FAULT_KIS_TIMEOUT, FAULT_DB_DELAY, FAULT_PRICE_STALE, FAULT_ORDER_REJECT  
- @fault_injectable 데코레이터, 실거래·실계좌 키와 동시 사용 차단  

**Phase:** Phase 5

---

## 17. INFRA-D — 운영 지표 + 알림 (관제센터)

**한 줄 요약:** 정상 동작 모니터링, 이상 시 즉시 알림.

- V4.1 최소 지표 4종: order_success/fail_count, fill_latency_ms, price_staleness_ms, cycle_duration_ms  
- 알림 등급: INFO(로그만), WARNING(일일 리포트), CRITICAL(즉시 직통), 쿨다운(동일 유형 5분, CRITICAL 제외)  
- 일일 리포트: 요약·매매 내역·보유 포지션·시장 환경·시스템 건강·자금 현황  

**Phase:** Phase 3(알림) → Phase 5(대시보드)

---

## 18. 모듈 간 데이터 흐름 전체도

- **PRE_MARKET:** recovery_check → DataProvider → Regime → Calendar → 5 DESK → Chief Analyst(today_universe) → Fund Commander(desk_limits)  
- **TRADING(60초 사이클):** cycle_lock → Position Manager(청산) → Fund Commander(rebuild_from_db) → Strategy Engine(signals) → 신호별: idempotency → Fund Commander(bet) → Risk(pre_trade, 예약금) → Order Executor → Position Manager(포지션 생성) → 운영 지표 기록 → cycle_lock 해제  
- **POST_MARKET:** Trade Analyzer, Adaptive 데이터 축적, 일일 리포트, daily_capital_state, 알림  
- **주간/월간:** Adaptive 가중치·파라미터·데스크 배분 보정  

---

## 19. 모듈별 DB 테이블 매핑

| 모듈 | 사용 테이블 | 비고 |
|------|-------------|------|
| Orchestrator | v4_system_state_log, v4_system_heartbeat | 쓰기 |
| Regime Detector | index_daily, daily_investor, v4_vkospi_daily, v4_market_regime_daily | |
| Market Calendar | v4_market_calendar | |
| Chief Analyst | v4_universe_version | |
| Fund Commander | v4_reservations, positions, v4_fund_pool_snapshot, v4_bet_history | |
| 5 DESK | daily_stock, daily_investor, sector_daily, v4_theme_* | |
| Strategy Engine | v4_order_requests | |
| Risk Manager | v4_reservations, positions, v4_market_calendar | |
| Order Executor | v4_order_requests, v4_reservations | |
| FundPool | v4_reservations, positions, v4_fund_pool_snapshot | |
| Position Manager | positions, v4_position_extended, v4_order_requests | |
| Adaptive Engine | v4_trade_analysis, v4_scoring_weights | |

레거시 테이블은 읽기 전용. V4 테이블만 쓰기 허용.

---

## 20. 모듈별 구현 우선순위 + Phase 배치

- **Phase 0:** Modernization 완료  
- **Phase 1:** Core Skeleton 완료 (Orchestrator, heartbeat, DataProvider, PricePoller, FundPool 기본)  
- **Phase 2-A:** Regime Detector 완료  
- **Phase 2-B:** Market Calendar 진행 중(10%)  
- **Phase 2-C:** Command Center — Chief Analyst, Fund Commander, FundPool DB=SoT, ReservationState, idempotency_key, 레짐 히스테리시스  
- **Phase 2-D:** DESK 2/3, 5대 스코어링, 테마 활성도  
- **Phase 3:** Strategy Engine, Risk(Full), ReentryGuard, Order Executor, Position Manager 기본, SELL_FAILED 재시도, 운영 지표 4종, 알림, 일일 리포트  
- **Phase 4:** Live/Backtest DataProvider, PricePoller 강화, Quality Tracker, WebSocket, mood 연속값  
- **Phase 5:** CriticalRiskKernel, fallback 청산, PrioritySemaphore, Adaptive 모듈 1·2·3, Trade Analyzer, Fault Injection, Observability, DB 보관 정책  
- **Phase 6:** 모의 계좌 → 실계좌 MANUAL_ASSIST → AUTO_LOCKED  

잔여 약 14주(병렬 시 12~13주), 예상 완료 2026년 5월 중순.

---

## 보고 요약

- **가장 중요한 모듈 3개(절대 불멸):** Position Manager, CriticalRiskKernel, FundPool. 이들이 살아있으면 보유 포지션 손절은 실행 가능.  
- **가치 창출 핵심 3개:** 5 DESK 스코어링, Strategy Engine, Adaptive Engine.  
- **다음 마일스톤:** Phase 2-B Market Calendar 완료 후 Phase 2-C에서 DB=SoT, ReservationState, idempotency_key, universe 버전화, 레짐 히스테리시스 구현.

---

*문서 버전: V4.1 | 보고일: 2026-02-13 | project-docs/kis-autotrade-v4/architecture*
