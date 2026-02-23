# KIS AutoTrade V4.1 — 적응형 자동매매 시스템 아키텍처 기술서

**문서 버전:** V4.1
**작성일:** 2026-02-13
**작성자:** Claude (Architecture Lead)
**승인자:** 대표님 (CEO)
**변경 이력:**
- V4.0 (2026-01) — 최초 설계
- V4.1 (2026-02-13) — GPT 5.2 Pro 외부 리뷰 반영, P0 리스크 보완, 로드맵 재배치

---

## 1. V3.0 → V4.0 → V4.1 진화 핵심

V3.0은 "잘 설계된 정적 시스템"이었습니다. V4.0에서 "시장에 적응하는 살아있는 시스템"으로 진화했고, V4.1에서는 **"실전 장애에서도 자금을 지키는 시스템"**으로 안전성을 강화했습니다.

V4.0 → V4.1 핵심 변경 사항:
- FundPool DB 기반 진실(Source of Truth) 원칙 확립
- 주문 멱등성(idempotency_key) 제도화
- risk_manager 2계층 분리 (CriticalRiskKernel + Full RiskManager)
- position_manager fallback 청산 경로 통제 장치
- 운영 최소 지표 4종 조기 도입 (Phase 3)
- PricePoller staleness/burst 제한 스펙 고정
- 경량 Fault Injection 도입 (Phase 5)

추가된 3대 핵심 엔진은 V4.0과 동일: **Market Regime Detector(시장 레짐 감지)**, **System Orchestrator(시스템 지휘자)**, **Adaptive Engine(적응 엔진)**

---

## 2. V4.1 전체 계층도

```
╔══════════════════════════════════════════════════════════════════════╗
║                    V4.1 SYSTEM HIERARCHY                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌────────────────────────────────────────────────────────────┐     ║
║  │                                                              │     ║
║  │              LAYER 0 — SYSTEM ORCHESTRATOR                   │     ║
║  │              (system_orchestrator)                            │     ║
║  │                                                              │     ║
║  │  시스템 전체 상태 관리, 모듈 간 실행 순서 보장               │     ║
║  │  상태 머신: IDLE → PRE_MARKET → READY → TRADING             │     ║
║  │            → CLOSING → POST_MARKET → IDLE                   │     ║
║  │  장애 감지, 복구, heartbeat 관리                             │     ║
║  │  ★ V4.1: 상태 전이 불변조건(Invariants) 코드 레벨 강제     │     ║
║  │                                                              │     ║
║  └──────┬───────────────────────────────────────┬───────────────┘     ║
║         │                                       │                     ║
║         ▼                                       ▼                     ║
║  ┌──────────────────┐                ┌──────────────────────┐        ║
║  │  LAYER 1-A        │                │  LAYER 1-B            │        ║
║  │  MARKET REGIME    │                │  MARKET CALENDAR      │        ║
║  │  DETECTOR         │                │                       │        ║
║  │                   │                │  FOMC, 만기일, IPO    │        ║
║  │  "지금 어떤       │                │  MSCI, 배당락, 락업   │        ║
║  │   장세인가"       │                │  특수일 관리          │        ║
║  │                   │                │                       │        ║
║  │  regime + mood    │                │  trading_restriction  │        ║
║  └────────┬──────────┘                └──────────┬────────────┘        ║
║           │                                      │                     ║
║           └──────────────┬───────────────────────┘                     ║
║                          ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │              LAYER 2 — COMMAND CENTER                        │       ║
║  │                                                              │       ║
║  │  ┌─────────────────┐  ┌─────────────────┐                  │       ║
║  │  │  chief_analyst   │  │  fund_commander  │                  │       ║
║  │  │  어디서 싸울지   │  │  얼마를 걸지    │                  │       ║
║  │  │  regime 반영     │  │  regime 반영    │                  │       ║
║  │  │  ★ V4.1:        │  │  ★ V4.1:        │                  │       ║
║  │  │  universe 버전화 │  │  DB=SoT 재구성  │                  │       ║
║  │  └────────┬─────────┘  └────────┬─────────┘                  │       ║
║  │           │                      │                           │       ║
║  └───────────┼──────────────────────┼───────────────────────────┘       ║
║              │                      │                                   ║
║              ▼                      ▼                                   ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 3 — MARKET BRAIN (5 DESK)                            │       ║
║  │                                                              │       ║
║  │  DESK1    DESK2    DESK3    DESK4    DESK5                  │       ║
║  │  초단기   데일리   단기SW   중기SW   장기SW                 │       ║
║  │                                                              │       ║
║  │  → today_universe (CLASS + confidence + regime_context)     │       ║
║  └────────────────────────┬─────────────────────────────────────┘       ║
║                            │                                             ║
║                            ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 4 — STRATEGY ENGINE                                   │       ║
║  │  today_universe 안에서만 신호 생성                           │       ║
║  │  signal_aggregator → sorted_signals                         │       ║
║  │  ★ V4.1: idempotency_key로 중복 신호 실행 차단             │       ║
║  └────────────────────────┬─────────────────────────────────────┘       ║
║                            │                                             ║
║                            ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 5 — EXECUTION CORE                                    │       ║
║  │  fund_commander   risk_manager   order_executor              │       ║
║  │  (가변베팅)       (안전장치)     (KIS실행+체결관리)         │       ║
║  │  ★ V4.1: fund_pool DB=SoT (메모리는 캐시)                 │       ║
║  │  ★ V4.1: ReservationState 상태 머신                        │       ║
║  │  ★ V4.1: idempotency_key UNIQUE 제약                       │       ║
║  │  ★ V4.1: risk_manager 2계층 분리                           │       ║
║  │  ★ fund_pool (자금 풀) 중앙 관리                           │       ║
║  │  ★ reservation 시스템 (예약금 DB + 자동만료)               │       ║
║  └────────────────────────┬─────────────────────────────────────┘       ║
║                            │                                             ║
║                            ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 6 — POSITION LIFECYCLE                                │       ║
║  │  position_manager: 감시 + 청산 + 승격/이관                  │       ║
║  │  재매수 방지 규칙 적용                                       │       ║
║  │  청산 실패 재시도 + SELL_FAILED 처리                        │       ║
║  │  ★ V4.1: fallback 청산 경로 (긴급 모드 전용)              │       ║
║  │  ★ V4.1: SELL_FAILED 재시도 전략                           │       ║
║  └────────────────────────┬─────────────────────────────────────┘       ║
║                            │                                             ║
║                            ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 7 — ADAPTIVE ENGINE                                    │       ║
║  │  스코어링 가중치 자동 보정                                   │       ║
║  │  전략 파라미터 롤링 최적화                                   │       ║
║  │  데스크 성과 기반 배분 조정                                  │       ║
║  │  매매 결과 상세 분석 + 피드백 루프                           │       ║
║  │  ★ V4.1: 레짐 조건부 가중치 분리                           │       ║
║  │  ★ V4.1: 지수감쇠 창 (4주 가중 + 12주 약가중)             │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
║                                                                          ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  INFRA — DATA PIPELINE                                       │       ║
║  │  data_provider (추상화 인터페이스)                           │       ║
║  │  price_poller (중앙 시세 수집기)                             │       ║
║  │  ★ V4.1: (price, ts, source, staleness_ms) 캐시 구조      │       ║
║  │  ★ V4.1: burst 제한 레이트리미터                           │       ║
║  │  data_quality_tracker (데이터 품질 추적)                    │       ║
║  │  ★ V4.1: 경량 Fault Injection (개발/모의 전용)            │       ║
║  │  ★ V4.1: 운영 최소 지표 4종 조기 도입                     │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 3. LAYER 0 — SYSTEM ORCHESTRATOR

```
╔══════════════════════════════════════════════════════════════════════╗
║  SYSTEM ORCHESTRATOR — 시스템 지휘자                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ■ 상태 머신 (State Machine)                                        ║
║                                                                      ║
║    ┌───────┐   07:55    ┌────────────┐   08:50   ┌───────────┐     ║
║    │ IDLE  │ ────────→ │ PRE_MARKET │ ───────→ │  READY    │     ║
║    └───┬───┘            └────────────┘           └─────┬─────┘     ║
║        ↑                                                │           ║
║        │                                          09:00 │           ║
║        │                                                ▼           ║
║    ┌───┴────────┐  15:35  ┌──────────┐  15:20  ┌───────────┐     ║
║    │POST_MARKET│ ←────── │ CLOSING  │ ←───── │ TRADING   │     ║
║    └────────────┘         └──────────┘         └───────────┘     ║
║                                                                      ║
║  ═══════════════════════════════════════════════════════════         ║
║                                                                      ║
║  ■ 각 상태에서 허용되는 동작                                        ║
║                                                                      ║
║    IDLE:                                                             ║
║      - 아무 모듈도 실행하지 않음                                    ║
║      - heartbeat만 기록                                              ║
║      - 다음 거래일 알람 설정                                        ║
║                                                                      ║
║    PRE_MARKET (07:55~08:50):                                        ║
║      - recovery_check 실행 (장애 복구)                              ║
║      - ★ V4.1: FundPool DB 기반 메모리 재구성                      ║
║      - data_provider: 전일 데이터 수집                              ║
║      - market_regime_detector: 레짐 판정                            ║
║      - market_calendar: 특수일 확인                                  ║
║      - market_analyst 5 DESK: 장 전 분석                            ║
║      - chief_analyst: universe 확정                                  ║
║      - fund_commander: 자금 상태 갱신 + 배분 계산                  ║
║      - ★ 매매 불가, 분석만                                         ║
║                                                                      ║
║    READY (08:50~09:00):                                              ║
║      - 모든 분석 완료 확인                                          ║
║      - today_universe 정상 로드 확인                                ║
║      - fund_allocation 정상 확인                                     ║
║      - KIS API 연결 상태 확인                                       ║
║      - 하나라도 실패 → DEGRADED_READY (축소 운영)                  ║
║      - ★ 매매 불가, 준비 확인만                                    ║
║                                                                      ║
║    TRADING (09:00~15:20):                                            ║
║      - strategy_engine: 매매 신호 생성                               ║
║      - fund_commander: bet_size 계산                                 ║
║      - risk_manager: pre_trade_check                                 ║
║      - order_executor: 주문 실행                                     ║
║      - position_manager: 포지션 감시 + 청산                         ║
║      - market_analyst: realtime_monitor (5분 주기)                  ║
║      - ★ 전체 기능 가동                                            ║
║                                                                      ║
║    CLOSING (15:20~15:30):                                            ║
║      - 신규 진입 차단                                                ║
║      - 당일 청산 대상 강제 청산 실행                                ║
║      - CLASS-C 오버나잇 포지션 확인                                 ║
║      - ★ 청산만 가능, 신규 매수 불가                               ║
║                                                                      ║
║    POST_MARKET (15:30~15:45):                                        ║
║      - market_analyst: 성과 기록                                    ║
║      - adaptive_engine: 스코어링 검증 데이터 기록                  ║
║      - 일일 리포트 생성                                              ║
║      - daily_capital_state 저장                                      ║
║      - ★ 매매 불가, 정산 및 분석만                                 ║
║                                                                      ║
║  ═══════════════════════════════════════════════════════════         ║
║                                                                      ║
║  ■ ★ V4.1 추가: 상태 전이 불변조건 (Invariants)                    ║
║                                                                      ║
║    PRE_MARKET → READY 전이 조건:                                     ║
║      ✓ today_universe loaded (종목 수 > 0)                           ║
║      ✓ fund_pool ready (DB 기반 재구성 완료)                        ║
║      ✓ price_poller live (heartbeat 최근 30초 이내)                 ║
║      ✓ position_manager healthy (heartbeat 정상)                    ║
║      ✓ regime 판정 완료 (regime_score is not None)                  ║
║      ✓ calendar 조회 완료 (adjustment 객체 존재)                    ║
║      ✓ data_quality >= GRADE_B                                      ║
║      하나라도 실패 → DEGRADED_READY로 전환                          ║
║                                                                      ║
║    READY → TRADING 전이 조건:                                        ║
║      ✓ KIS API 연결 확인 (ping 또는 잔고 조회 성공)                ║
║      ✓ 현재 시각 >= 09:00                                           ║
║      ✓ CriticalRiskKernel 정상 (heartbeat 최근 30초)               ║
║                                                                      ║
║    TRADING → CLOSING 전이 조건:                                       ║
║      ✓ 현재 시각 >= 15:20                                           ║
║      ★ CLOSING 진입 시 즉시 order_executor에 "신규 매수 차단" 플래그 ║
║                                                                      ║
║    CLOSING → POST_MARKET 전이 조건:                                   ║
║      ✓ 현재 시각 >= 15:30                                           ║
║      ✓ 미체결 주문 0건 (또는 전부 취소 완료)                       ║
║                                                                      ║
║  ═══════════════════════════════════════════════════════════         ║
║                                                                      ║
║  ■ TRADING 상태 — 60초 사이클 내부 순서:                           ║
║                                                                      ║
║    [1] cycle_lock 획득 → 이전 사이클 완료 확인                      ║
║    [2] position_manager.check_positions() ★ 매수보다 청산이 먼저   ║
║    [3] fund_commander.refresh_available() ★ V4.1: DB에서 재계산   ║
║    [4] strategy_engine.run_strategies()                              ║
║    [5] for signal: idempotency_key 중복 확인 → bet_size →          ║
║        risk_manager.pre_trade_check() → order_executor.execute_buy() ║
║    [6] cycle_lock 해제, 운영 지표 기록                               ║
║                                                                      ║
║  ═══════════════════════════════════════════════════════════         ║
║                                                                      ║
║  ■ recovery_check (시스템 시작 시 필수 실행):                        ║
║                                                                      ║
║    async def recovery_check():                                       ║
║      # 0. ★ V4.1: FundPool DB 기반 메모리 재구성                   ║
║      await fund_pool.rebuild_from_db()                               ║
║      #   reservation(RESERVED/ORDER_SUBMITTED) SUM                   ║
║      #   + position(OPEN) invested SUM                               ║
║      #   → 메모리 available/reserved/invested 재계산                 ║
║      # 1. KIS 실잔고 vs DB 포지션 대조                              ║
║      kis_holdings = await kis_api.get_holdings()                     ║
║      db_positions = await get_open_positions()                       ║
║      # KIS에 있는데 DB에 없는 것 (장애 중 체결) → create_orphan    ║
║      # DB에 있는데 KIS에 없는 것 (장애 중 청산) → close_orphan      ║
║      # 2. 만료 예약금 정리 cleanup_expired_reservations()           ║
║      # 3. 손절가 이탈 즉시 체크 → emergency_sell(position)          ║
║      # 4. 미체결 주문 30분 초과 시 취소                             ║
║                                                                      ║
║  ■ 축소 운영 모드 (DEGRADED)                                         ║
║  ┌──────────────────┬──────────────────────────────┐               ║
║  │ 장애 모듈         │ 축소 운영 행동                │               ║
║  ├──────────────────┼──────────────────────────────┤               ║
║  │ market_analyst    │ 신규 진입 중단, 기존 포지션만 │               ║
║  │ strategy_engine   │ 신규 진입 중단, 기존 포지션만 │               ║
║  │ fund_commander    │ 고정 bet_size(20%)로 전환     │               ║
║  │ risk_manager(Full)│ 신규 진입 차단, CRK만 가동   │               ║
║  │ CriticalRiskKernel│ ★ 절대 죽으면 안 됨, 내장   │               ║
║  │ order_executor    │ fallback 청산 경로 + 알림    │               ║
║  │ data_provider     │ 캐시 전환, bet ×0.5          │               ║
║  │ position_manager  │ ★ 절대 불멸, CRK+fallback   │               ║
║  └──────────────────┴──────────────────────────────┘               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 4. LAYER 1-A — MARKET REGIME DETECTOR

**레짐이란:** market_mood는 "오늘의 기분", market_regime은 "지금 시장의 성격"(최근 2~4주). 같은 BULL 기분이라도 강한 추세장은 모멘텀 대박, 횡보장은 가짜 돌파 실패 가능.

**5대 레짐:**

| 레짐 | 판정 요약 | 시스템 대응 |
|------|-----------|-------------|
| **STRONG_TREND_UP** | 코스피 20일 수익률 > +5%, 정배열, 양봉일 > 65%, 외국인 순매수 | DESK1·2 공격적, bet ×1.15, 손절 넓게·목표 높게 |
| **MILD_TREND_UP** | 20일 수익률 +1%~+5%, 단기 정배열 | 기본 배분, bet ×1.0 |
| **SIDEWAYS** | 20일 수익률 -1%~+1%, 고저 범위 < 3%, 5MA·20MA 수렴 | DESK1 비활성, DESK3 박스돌파 주력, bet ×0.8 |
| **MILD_TREND_DOWN** | 20일 수익률 -5%~-1%, 역배열, 음봉일 > 11일 | DESK2 CLASS-C만, bet ×0.5, 현금 50% |
| **STRONG_TREND_DOWN** | 20일 수익률 < -5%, 역배열, VIX/VKOSPI > 25, 외국인 순매도 | DESK1·2·3 전면 비활성, 신규 진입 중단, bet ×0.0 |

**★ V4.1 레짐 전환 히스테리시스:** 상향 전환 = 새 레짐 점수 3거래일 연속 상위 경계 초과. 하향 전환 = 2거래일 연속 하위 경계 미달. STRONG_TREND_DOWN 진입은 2일 연속, 탈출은 3일 연속 개선(데드캣 바운스 방지).

**레짐 판정 지표 (Phase 2-A 기준):** KOSPI 20일 수익률, 5MA/20MA/60MA 정렬, 20일 양봉 비율, 거래대금 추이, 외국인 순매수 20일, VKOSPI (index_daily, daily_investor, v4_vkospi_daily).

**레짐 → 데스크/파라미터:** DESK1~5 배분 비율·현금 비중·bet modifier·손절·목표·진입 score는 레짐별로 상이 (표 생략). ROCKET MODE(100만원)에서는 DESK4·5 비활성 시 해당 배분을 DESK2·3으로 재분배.

---

## 5. LAYER 1-B — MARKET CALENDAR

**특수일 유형 및 대응:**

| 유형 | 대응 |
|------|------|
| FOMC 금리 결정일 | 당일 bet_size × 0.3, DESK1 비활성 |
| 한은 금리 결정일(BOK_RATE) | 당일 bet × 0.5, DESK1 비활성 |
| 선물/옵션 만기일 | 당일 bet × 0.5, DESK1·CLASS-V 비활성 |
| 네 마녀의 날 | 당일 bet × 0.3, DESK1·2 비활성 |
| 대형 IPO | 해당 섹터 bet × 0.7 |
| 실적 시즌 | 해당 종목 실적 당일 진입 금지, 익일 확인 후 진입 |
| MSCI/FTSE 리밸런싱 | 당일 bet × 0.5 |
| 지수 정기변경(INDEX_REBALANCE) | 당일 bet × 0.7 |
| 대형 락업해제(LOCKUP_EXPIRY) | 해제일 해당 종목 진입 금지, 전후 3일 bet × 0.7 |
| 배당락(EX_DIVIDEND) | 배당락일 해당 종목 진입 금지 |
| 연휴 전후(HOLIDAY_ADJACENT) | 연휴 전일 bet × 0.7, CLASS-C 오버나잇 차단; 연휴 후 첫날 bet × 0.8 |
| 사용자 지정(USER_CUSTOM) | 대표님 수동 등록 가능 |

**복수 이벤트 겹침:** bet_modifier = min(이벤트별 modifier). desk_active = 하나라도 비활성이면 비활성. class_restrictions = DISABLED > RESTRICTED > NORMAL.

**DB:** v4_market_calendar (date, event_type, event_name, bet_modifier, desk1~5_active, class_restrictions, note, source, UNIQUE(date, event_type)).

---

## 6. LAYER 5 — EXECUTION CORE (V4.1 강화)

**★ V4.1: FundPool DB = Source of Truth (SoT)**  
DB가 진실, 메모리는 캐시. reservation 테이블이 예약금 SoT, position 테이블이 투자금 SoT. `async def rebuild_from_db()`: RESERVED/ORDER_SUBMITTED 합계 + OPEN 포지션 (entry_price×quantity) 합계 → reserved, invested, available 재계산. invariant: total_capital = available + reserved + invested.

**ReservationState 상태 머신:**  
RESERVED → (주문제출) → ORDER_SUBMITTED → (체결 결과) → FILLED / PARTIAL / CANCELLED / FAILED. RESERVED → (만료/취소) → EXPIRED / RELEASED. 자금 반환: EXPIRED/RELEASED/CANCELLED/FAILED 시 예약금 전액 available; FILLED 시 invested 전환; PARTIAL 시 체결분 invested, 잔여 available.

**★ 주문 멱등성 (Idempotency):**  
idempotency_key = `"{trade_date}_{cycle_id}_{ticker}_{action}"` (예: 2026-02-13_42_005930_BUY). v4_order_requests 테이블에 idempotency_key UNIQUE. INSERT 성공 시에만 KIS API 호출, UNIQUE 위반 시 "이미 처리된 주문" 처리.

**FundPool 연성 배분:** total_capital, available, reserved, invested; desk_limits / desk_used. can_allocate(desk_id, amount), allocate(), release(). ★ V4.1: allocate 시 DB 트랜잭션과 함께 실행. resolve_contention(requests)로 복수 데스크 경합 해소(score 순).

**★ risk_manager 2계층:**  
(1) **CriticalRiskKernel** — position_manager 내장, 절대 불멸. 손절가 이탈·일일 손실 한도·최대 손실 초과 → 강제 청산. 가격 조회 실패 시 보수적 청산. critical_risk_config만 참조.  
(2) **Full RiskManager** — 정상 시 pre_trade_check, 동시 포지션 수·1종목1포지션·재매수 규칙·예약금 관리·데이터 품질·레짐 연동. 장애 시 비활성(CRK만 잔존).

**ReentryGuard:** 당일 손절 종목 재매수 금지; 당일 동일 종목 3회 매매 금지; 당일 익절 종목 재매수 시 confidence 한 단계 하향.

---

## 7. LAYER 6 — POSITION LIFECYCLE (V4.1 강화)

**★ fallback 청산 경로:**  
order_executor 장애 시 position_manager가 직접 KIS 시장가 매도 호출.  
(1) 청산 전용 + 긴급 모드 플래그(is_emergency_mode=True 일 때만).  
(2) 동일 KIS API 레이트리미터 공유(긴급 청산 > 폴링 우선).  
(3) fallback 주문도 v4_order_requests에 기록, idempotency_key 적용, source='EMERGENCY_FALLBACK'.  
흐름: 청산 요청 → order_executor 실패 → is_emergency_mode=True → fallback_sell() → 기록·알림 → 자금 반환 → 복구.

**★ SELL_FAILED 재시도 전략:**  
시도1 지정가(매수1호가) → 30초 대기 미체결 시; 시도2 IOC(매수1호가-1틱); 시도3 시장가; 시도4 알림+수동 청산 가이드. 최대 재시도 시간 3분. 모든 시도 v4_order_requests 기록.

**포지션 승격 시 손익 기준:**  
손절가 = max(매입가 기준, 현재가 기준)으로 new_sl_pct 적용. 트레일링 고점(peak_price) 리셋 안 함. TransferParams: stop_loss_price, trailing_peak, trailing_stop_pct, target_profit_pct, max_hold_days.

---

## 8. LAYER 7 — ADAPTIVE ENGINE (V4.1 강화)

**미션:** "매주 조금씩 더 똑똑해지는 시스템" — 스코어링·전략 파라미터·데스크 배분 자동 보정.

**모듈 1 — 스코어링 가중치 자동 보정:**  
실행 주기 매주 일요일. ★ V4.1: 지수감쇠 — 최근 4주 가중 1.0, 5~8주 0.5, 9~12주 0.25, 12주 이전 제외. ★ V4.1: 레짐 조건부 가중치 — scoring_weights 테이블에 regime(ALL, STRONG_UP, MILD_UP, SIDEWAYS, MILD_DOWN)별 supply/sector/theme/volume/tech. 해당 레짐 매매 50건 미만이면 해당 레짐 가중치 보정 안 함(ALL 사용). 처리: 요소별 수익률 상관→가중치 변환, 급변 방지 ±5%, 최소 5% 보장.

**모듈 2 — 전략 파라미터 롤링 최적화:** 손절/익절/보유기간 주당 최적화, 변경폭 ±1% 또는 ±1일.

**모듈 3 — 데스크 성과 기반 배분:** 매월 1일, calmar = monthly_return / max_drawdown. calmar > 2.0 배분 +2%, 0.5~1.0 -2%, < 0.5 -3%. 월 ±3% 제한, 대폭 변경 시 승인.

**모듈 4 — Trade Analyzer:** 매 청산 시 trade_analysis 기록(진입 시 universe_score·regime·bet_confidence·desk_id·entry_time·data_quality·universe_id; 보유 중 max_profit_pct·hold_days; 청산 exit_reason·realized_pnl·order_request_id; 사후 price_after_1h/1d·early_exit).

**모듈 5 — 과적합 방지:** 변경폭 상한(가중치 ±5%, 파라미터 ±1%, 배분 ±3%). 최소 50건(레짐별 50건). ★ V4.1: 12주 중 9주 최적화·3주 검증, 검증 성과 30% 이상 나쁘면 보정 미적용. 원점 회귀 감지 시 초기 리셋. 수동 오버라이드 가능.

---

## 9. INFRA — DATA PIPELINE V4.1

**데이터 제공자 추상화:** DataProvider(ABC) — get_current_price, get_daily_ohlcv, get_minute_candles, get_supply_demand, get_sector_momentum, get_market_index. LiveDataProvider(KIS+KRX+캐시), BacktestDataProvider(sim_datetime, 미래 참조 차단).

**★ PricePoller (중앙 시세 수집기):** 독립 운영, 모든 모듈은 이 캐시에서만 가격 읽음. V4.1 캐시: price:{ticker} → { price, ts, source, staleness_ms }. 소비 측에서 staleness > 30초 시 경고; CriticalRiskKernel은 stale에서도 보수적 청산 판단. V4.1 병렬 수집(asyncio.gather) + KISRateLimiter(max_per_second=20, max_concurrent=5). 우선순위: EMERGENCY > ORDER > NORMAL.

**data_quality_tracker:** data_sources별 status(LIVE/STALE/FALLBACK/DEAD), last_success, fail_count. 전체 품질 등급: GRADE_A(모두 LIVE), GRADE_B(1~2개 STALE), GRADE_C(1개 이상 FALLBACK), GRADE_D(핵심 DEAD). chief_analyst 전달; GRADE_C 시 bet ×0.7, GRADE_D 시 DEGRADED. 3단계 폴백: 실시간 → 캐시(전일, 스코어×0.8) → 해당 요소 제외 재분배.

**★ 운영 최소 지표 4종 (Phase 3):** (1) order_submit 성공/실패/거부 카운트(heartbeat). (2) fill_latency_ms(v4_order_requests). (3) price_staleness_ms(heartbeat). (4) cycle_duration_ms(last_cycle_duration_ms). v4_system_heartbeat에 order_success_count, order_fail_count, max_price_staleness_ms 추가.

**★ 경량 Fault Injection (Phase 5, 개발/모의 전용):** FAULT_INJECTION=false(기본). FAULT_KIS_TIMEOUT, FAULT_DB_DELAY, FAULT_PRICE_STALE, FAULT_ORDER_REJECT 등 환경 변수로 주입. @fault_injectable 데코레이터, false 시 no-op.

---

## 10. 장 시작 노이즈 구간 처리

**시간대별 신뢰도:** 09:00~09:05 NOISE(관찰만, 진입 불가). 09:05~09:15 INITIAL(CLASS-B만, 첫 5분봉+확인봉). 09:15~09:30 DEVELOPING(CLASS-A·B, bet ×0.9). 09:30~14:30 RELIABLE(전 CLASS, 표준 bet). 14:30~15:20 CLOSING(CLASS-C 전용, 신규 진입 금지).

**CLASS-B 확인봉:** 09:05 첫 5분봉 양봉 → 09:10 확인봉(저점 상승·거래량 유지) 후 진입.

---

## 11. 테마 분석 현실적 구현

뉴스 NLP 대신 시장 데이터 기반. (1) v4_theme_stock_mapping 테마-종목 매핑(수동 관리). (2) theme_activity_score = (테마 종목 평균 거래량/20일평균)×0.4 + (등락률 백분위)×0.3 + (수급 양호 비율)×0.3. >70 ACTIVE, 50~70 WARM, <50 COLD. Phase 2에서 뉴스 키워드→테마 보조 신호 추가 가능.

---

## 12. mood 연속값 체계

mood_score 0~100 계산(선물 등락·미국장·환율·VIX/VKOSPI·장중 지수). 라벨: 85~100 STRONG_BULL, 65~84 BULL, 45~64 NEUTRAL, 25~44 BEAR, 0~24 STRONG_BEAR. mood_modifier = mood_score/65(cap 1.2). 장중 mood 10점 이상 하락 시 trailing_stop 1% 강화; 20점 이상 하락 시 수익 0% 이하 포지션 즉시 청산 검토.

---

## 13. 사용자 개입 관리 모드

**AUTO_LOCKED:** 완전 자동, 비상 정지·전체 청산·모니터링만 가능. **AUTO_ADVISORY:** 자동+개입 허용, 수동 행동 별도 기록. **MANUAL_ASSIST:** 신호 제안만, 실행은 사용자. 권장: 모의 AUTO_ADVISORY, 실전 초기 1개월 MANUAL_ASSIST, 안정화 후 AUTO_LOCKED. 파라미터 변경은 POST_MARKET 또는 PRE_MARKET에서만.

---

## 14. today_universe 버전화 (V4.1)

universe_version 메타데이터: universe_id(예 UV-20260213-001), generated_at, regime_state_id, regime, regime_score, calendar_adjustment_id, data_quality_grade, inputs_hash(입력 동일 시 동일 해시), stock_count, version_seq(장중 재생성 시 증가). v4_universe_version 테이블. trade_analysis.universe_id로 "어떤 입력 조건의 universe에서 나온 신호인지" 완전 추적.

---

## 15. V4.1 DB 스키마 전체

**신규 테이블:** v4_order_requests(idempotency_key UNIQUE, user_id, trade_date, cycle_id, ticker, action, reservation_id, order_amount, order_qty, kis_order_no, status, fill_*, fill_latency_ms, source, reject_reason). v4_reservations(user_id, desk_id, ticker, amount, state, order_request_id, expires_at). v4_universe_version(universe_id UNIQUE, trade_date, version_seq, generated_at, regime*, calendar_adj_id, final_bet_modifier, data_quality_grade, inputs_hash, stock_count).

**기존 ALTER:** v4_system_heartbeat + order_success_count, order_fail_count, max_price_staleness_ms. v4_scoring_weights + regime, UNIQUE(effective_from, regime). v4_trade_analysis + universe_id, order_request_id.

**인덱스:** v4_order_requests(trade_date, user_id). v4_reservations(state), (expires_at) WHERE state='RESERVED'. **보관:** heartbeat 90일 raw 후 일별 집계, trade_analysis 12개월 후 월별, order_requests 6개월 후 아카이브.

---

## 16. V3.0 → V4.0 → V4.1 변경 요약

| 항목 | V3.0 | V4.0 | V4.1 |
|------|------|------|------|
| 시스템 상태 | 없음 | 상태 머신 | + 불변조건 강제 |
| 시장 레짐 | 없음 | 5대 레짐+수치 | + 히스테리시스 |
| 자금 정합성 | - | 메모리 lock | + DB=SoT, 재구성 |
| 예약금 | - | 타이머 | + 상태 머신 |
| 주문 멱등성 | 없음 | 없음 | + idempotency_key |
| risk_manager | 단일 | 단일 | 2계층(CRK+Full) |
| 청산 fallback | - | - | + 긴급 모드 3통제 |
| SELL_FAILED | 단순 재시도 | 단순 재시도 | 단계적 전환 전략 |
| today_universe 추적 | - | - | + 버전화 |
| DB 테이블 수 | 48 | 60 | 63 |

---

## 17. V4.1 단계별 구현 로드맵

Phase 0 Modernization 100%. Phase 1 Core Skeleton 100%. Phase 2 Market Brain(2-A Regime 100%, 2-B Calendar 진행, 2-C Command Center·2-D Strategies 대기). Phase 3 Strategy+Betting(운영 지표 4종, SELL_FAILED 재시도). Phase 4 Data Pipeline(PricePoller 병렬·staleness, burst, WebSocket). Phase 5 Adaptive+Stabilize(CRK, fallback, 레짐 가중치·지수감쇠, Fault Injection). Phase 6 Live Rollout. V4.1 반영 항목은 2-C( FundPool DB=SoT, ReservationState, idempotency, universe 버전화), 3·4·5에 명시.

---

## 18. V4.1 설계 원칙 (불변)

1. FundPool invariant: total_capital = available + reserved + invested. ★ V4.1: DB=SoT, 메모리 캐시.  
2. Lock 기반 동시성.  
3. 레거시 48개 테이블 ALTER/DROP 금지.  
4. Graceful degradation. ★ V4.1: CriticalRiskKernel 모든 장애에서 생존.  
5. Soft allocation per desk.  
6. ★ V4.1: 멱등성 — 모든 주문 idempotency_key.  
7. ★ V4.1: 추적 가능성 — universe→signal→order→fill→position→analysis ID 체인.  
8. ★ V4.1: 비대칭 방어 — 하락 빠르게(2일), 상승 확인 후(3일); 가격 불명=위험; 긴급일수록 기록 중요.

---

## 19. 문서 변경 이력

**V4.0 (2026-01):** 최초 설계, 8계층·5대 레짐·Adaptive·FundPool·DataProvider.

**V4.1 (2026-02-13):** GPT 5.2 Pro 리뷰 반영. P0: FundPool DB=SoT, ReservationState, idempotency_key·v4_order_requests·v4_reservations, risk_manager 2계층, fallback 청산·3통제, SELL_FAILED 재시도. P1: Orchestrator Invariants, 레짐 히스테리시스, Calendar 확장, universe 버전화, Adaptive 레짐 조건부·지수감쇠, 과적합 레짐별 50건. P2: PricePoller 병렬·burst, 캐시 구조, 운영 지표 4종, 보관 정책, Fault Injection. 설계 원칙 6·7·8 추가. DB 신규 3개·ALTER·인덱스.

---

*본 문서는 KIS AutoTrade V4.1 적응형 자동매매 시스템 아키텍처 기술서 19절 전문입니다.*
