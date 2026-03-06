# CUR-V41-CAPITAL-ROUTER-001 — Capital Router 자본 순환 라우팅 엔진

**Task ID**: T-093
**날짜**: 2026-03-05
**우선순위**: P0-CRITICAL
**의존성**: T-092 (NodeDetectorEngine) 완료 기반

---

[인계 확인]
직전 완료: T-092 (NodeDetectorEngine 5 DESK 마디 감지 통합 엔진)
현재 단계: Phase 2C — Command Center
CEO 지시 적용: D-001, D-002, D-003, D-007
strategy_cards: 60
open_positions: 14

---

## 1. 작업 개요

FNCCS(Fractal Node Capital Circulation System) v1.0의 핵심 엔진인 Capital Router를 구현.
"자본은 분할되지 않고 순환한다" — 한 마디에서 수확한 자본이 즉시 다음 최고 기대수익 마디로 이동.

**CEO 원칙 반영**:
- "모든 시간대의 파동을 감시하고, 최적 타이밍에 자본을 이동"
- "자본이 쉬면 복리가 멈춘다"
- Priority = (기대수익/소요시간) × 신뢰도 × 파이프라인보너스 × (1-유휴율패널티)

---

## 2. 구현 내용

### Phase 1 — Capital Router 핵심 엔진

**파일**: `backend/app/services/capital_router.py` (기존 파일, 버그 수정 포함)

#### 구현 클래스 및 메서드

| 메서드 | 역할 |
|--------|------|
| `calculate_priority_score()` | Priority Score 계산: (수익/기간) × 확신도 × 파이프라인보너스 × (1-유휴패널티) |
| `get_routing_candidates()` | v4_node_realtime에서 STARTING/BOTTOM 종목 조회 → Priority Score 정렬 |
| `get_routing_decision()` | 가용 자본 배분 결정 (단일종목 ≤30%, DESK5 ≤10%) |
| `execute_routing()` | v4_capital_flow에 라우팅 기록 |
| `get_available_capital()` | accounts 테이블에서 현금성 자산 조회 |
| `get_capital_idle_rate()` | CIR(Capital Idle Rate) 계산 |
| `run_morning()` | 장전 08:50 라우팅 (DESK3/4/5 대상) |
| `run_intraday()` | 장중 10분 간격 DESK2 분봉 라우팅 |
| `run_closing()` | 장후 15:40 수확금 집계 + 익일 계획 |

#### Priority Score 공식

```
Priority = (est_return_pct / est_days) × (confidence/100) × pipeline_bonus × (1 - idle_penalty)

pipeline_bonus = {DESK1: 1.0, DESK2: 1.2, DESK3: 1.1, DESK4: 1.05, DESK5: 0.9}
idle_penalty = max(0, capital_utilization_ratio - 0.8) × 2.0
재진입 부스트: × 1.3 (최근 7일 내 청산 이력)
```

#### 라우팅 계층 (우선순위 순)

| 순위 | 구분 | 조건 |
|------|------|------|
| 1 | DESK2_MINUTE | DESK2 + 확신도 ≥ 80 |
| 2 | DESK3_ACCEL | DESK3 + 확신도 ≥ 70 |
| 3 | DESK4_BOTTOM | DESK4 전체 |
| 4 | DESK3_NORMAL | DESK3 + 확신도 < 70 |
| 5 | DESK5_SEED | DESK5 (최대 10%) |
| 6 | MMF_PARKING | 대기 (최대 2일) |

#### 자본 분배 규칙

- 단일 종목 최대 **30%**
- 단일 섹터 최대 **40%**
- DESK5 누적 최대 **10%** ← 버그 수정 (TC-08: 개별 배분도 한도 내로 클램핑)

#### 버그 수정 내역

기존 코드에서 DESK5 한도 체크 순서가 잘못되어 첫 DESK5 종목이 30%(MAX_SINGLE_STOCK_RATIO) 전액을 배분받는 문제 수정:

```python
# 수정 전 (버그)
if candidate.desk_level == 5:
    desk5_limit = int(available_capital * DESK5_MAX_RATIO)
    if desk5_allocated >= desk5_limit:
        continue
max_per_stock = int(available_capital * MAX_SINGLE_STOCK_RATIO)
alloc = min(remaining, max_per_stock)

# 수정 후
max_per_stock = int(available_capital * MAX_SINGLE_STOCK_RATIO)
alloc = min(remaining, max_per_stock)
if candidate.desk_level == 5:
    desk5_limit = int(available_capital * DESK5_MAX_RATIO)
    if desk5_allocated >= desk5_limit:
        continue
    alloc = min(alloc, desk5_limit - desk5_allocated)  # ← 추가
```

---

### Phase 2 — 재진입 스케줄러

**파일**: `backend/app/services/reentry_scheduler.py` (신규)

#### 구현 클래스 및 메서드

| 메서드 | 역할 |
|--------|------|
| `get_pullback_predictions()` | v4_node_realtime PULLBACK 종목 → 눌림 완료 시점 예측 |
| `get_offset_opportunities()` | 보유 외 STARTING/BOTTOM 종목 → 시간 오프셋 기회 탐색 |
| `check_idle_capital()` | capital_idle_days ≥ 5 종목 WARN/CRITICAL 경고 |
| `increment_idle_days()` | 장 마감: 미청산 포지션 idle_days +1 |
| `reset_idle_days()` | 청산 시 해당 종목 idle_days 0으로 리셋 |
| `calculate_cir()` | CIR = avg(idle_days) / 50 (단순화) |
| `build_reentry_plan()` | 전체 재진입 계획 생성 (후보 + 경고 + CIR) |
| `run_daily_close()` | 장 마감 15:40 통합 실행 |

#### 유휴 자본 경고 기준

| idle_days | 경고 수준 |
|-----------|-----------|
| ≥ 5일 | WARN |
| ≥ 10일 | CRITICAL |

#### 종목 간 시간 오프셋 전략

```
A종목 PULLBACK 중 (눌림 대기)
     ↓
B종목 STARTING/BOTTOM 활성 (즉시 진입 가능)
     ↓
B 진입 → A 재진입 예약 (눌림 완료 시점)
```

---

### Phase 3 — DB 마이그레이션

**파일**: `backend/migrations/060_v4_positions_capital_idle_days.sql` (신규)

```sql
ALTER TABLE v4_positions
    ADD COLUMN IF NOT EXISTS capital_idle_days INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_v4_positions_idle_days
    ON v4_positions (capital_idle_days DESC)
    WHERE status = 'OPEN';
```

> 참고: 지시서는 migration 054로 명시했으나 054는 기존 `054_go100_ai_predictions.sql`로 사용 중.
> 060번으로 할당 (최신 미사용 번호).

---

### Phase 4 — KPI 지표

| KPI | 설명 | 목표 |
|-----|------|------|
| CVR | Capital Velocity Ratio — 연간 자본 회전 횟수 | ≥ 6 |
| CIR | Capital Idle Rate — 유휴 자본 비율 | ≤ 10% |
| CGR | Compound Growth Rate per Rotation | ≥ 2.5% |
| PCR | Pipeline Conversion Rate — 파이프라인 전환율 | ≥ 10% |

KPI 저장 테이블: `v4_compound_growth_daily` (migration 059, TASK 095에서 상세 정의)

---

### Phase 5 — 백테스트 시뮬레이션 설계

| 시나리오 | 설명 |
|----------|------|
| A | Capital Router 없음 (기존 독립 DESK 운영) |
| B | Capital Router 적용 (자본 순환) |
| C | Capital Router + 파이프라인 보너스 |

검증 지표: 총 수익률, PF, MDD, CVR, CIR

> 120일 실제 DB 백테스트는 T-095 (Compound Growth Tracker)에서 수행 예정.

---

### Phase 6 — 단위 테스트

**파일**: `tests/test_capital_router.py` (신규, 21건)

#### 테스트 결과

```
============================= test session starts ==============================
collected 21 items

tests/test_capital_router.py::TestPriorityScore::test_tc01_basic_score_positive PASSED
tests/test_capital_router.py::TestPriorityScore::test_tc02_zero_days_clamped_to_one PASSED
tests/test_capital_router.py::TestPriorityScore::test_tc03_zero_confidence_gives_zero_score PASSED
tests/test_capital_router.py::TestPriorityScore::test_tc04_reentry_boost_applied PASSED
tests/test_capital_router.py::TestPriorityScore::test_tc05_desk_level_pipeline_bonus_ordering PASSED
tests/test_capital_router.py::TestRoutingDecision::test_tc06_allocation_does_not_exceed_available PASSED
tests/test_capital_router.py::TestRoutingDecision::test_tc07_single_stock_max_30pct PASSED
tests/test_capital_router.py::TestRoutingDecision::test_tc08_desk5_max_10pct PASSED
tests/test_capital_router.py::TestRoutingDecision::test_tc09_idle_rate_zero_when_fully_allocated PASSED
tests/test_capital_router.py::TestRoutingDecision::test_tc10_empty_candidates_gives_zero_allocated PASSED
tests/test_capital_router.py::TestRoutingDecision::test_tc11_routing_decision_has_datetime PASSED
tests/test_capital_router.py::TestRoutingTypeClassification::test_tc12_desk2_high_confidence_classified_as_minute PASSED
tests/test_capital_router.py::TestRoutingTypeClassification::test_tc13_desk3_low_confidence_classified_normal PASSED
tests/test_capital_router.py::TestReentryScheduler::test_tc14_idle_alert_level_warn PASSED
tests/test_capital_router.py::TestReentryScheduler::test_tc15_idle_alert_level_critical PASSED
tests/test_capital_router.py::TestReentryScheduler::test_tc16_cir_calculation_within_target PASSED
tests/test_capital_router.py::TestReentryScheduler::test_tc17_reset_idle_days_false_on_db_error PASSED
tests/test_capital_router.py::TestReentryScheduler::test_tc18_increment_idle_days_zero_on_db_error PASSED
tests/test_capital_router.py::TestReentryScheduler::test_tc19_cir_zero_on_db_error PASSED
tests/test_capital_router.py::TestIntegrationScenario::test_tc20_run_morning_structure PASSED
tests/test_capital_router.py::TestIntegrationScenario::test_tc21_run_closing_structure PASSED

============================== 21 passed in 0.08s ==============================
```

**21/21 ALL PASS** ✅ (목표 ≥15 달성)

---

## 3. 파일 생성/수정 목록

| 구분 | 파일 | 내용 |
|------|------|------|
| 수정 | `backend/app/services/capital_router.py` | DESK5 한도 버그 수정 (alloc 클램핑 추가) |
| 신규 | `backend/app/services/reentry_scheduler.py` | 재진입 스케줄러 전체 구현 |
| 신규 | `backend/migrations/060_v4_positions_capital_idle_days.sql` | v4_positions capital_idle_days 컬럼 추가 |
| 신규 | `tests/test_capital_router.py` | 단위 테스트 21건 ALL PASS |
| 신규 | `report/v41/CUR-V41-CAPITAL-ROUTER-001-20260305.md` | 본 보고서 |

---

## 4. 크론 스케줄 (등록 필요 — root 실행)

```cron
# Capital Router 크론 3건
50 8 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -c "from backend.app.services.capital_router import CapitalRouter; r=CapitalRouter(); r.run_morning()" >> /root/kis-autotrade-v4/logs/capital_router.log 2>&1
*/10 9-15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -c "from backend.app.services.capital_router import CapitalRouter; r=CapitalRouter(); r.run_intraday()" >> /root/kis-autotrade-v4/logs/capital_router.log 2>&1
40 15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -c "from backend.app.services.reentry_scheduler import ReentryScheduler; s=ReentryScheduler(); s.run_daily_close()" >> /root/kis-autotrade-v4/logs/capital_router.log 2>&1
```

> root 권한 없이 crontab 등록 불가. root에서 `crontab -e` 실행 필요.

---

## 5. 완료 기준 체크

| 기준 | 결과 |
|------|------|
| Capital Router 핵심 엔진 구현 | ✅ capital_router.py |
| 재진입 스케줄러 구현 | ✅ reentry_scheduler.py |
| v4_positions capital_idle_days 마이그레이션 | ✅ migration 060 |
| 단위 테스트 ≥15건 ALL PASS | ✅ 21/21 PASS |
| DESK5 한도 버그 수정 | ✅ alloc 클램핑 추가 |

---

## 6. 잔여 작업 (T-095 이후)

- 120일 백테스트 시뮬레이션 (시나리오 A/B/C 비교)
- CVR ≥ 6 실증 검증
- v4_compound_growth_daily KPI 실제 적재
- 크론 root 등록 (root 권한 필요)
- migration 060 실제 DB 적용 (root 실행 필요)

---

HANDOVER.md 업데이트 완료: (done_watcher.sh 자동 처리 예정)
