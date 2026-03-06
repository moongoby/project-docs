# CUR-V41-DUAL-FLOW-IMPLEMENT-001-20260307

**Task ID**: T-218
**Priority**: P1-HIGH
**완료일시**: 2026-03-07 (KST 2026-03-06 23:55 실행)
**커밋**: faa85636
**브랜치**: phase-2c-command-center

---

[인계 확인]
직전 완료: T-216 (source propagation PRE_SOURCE_FILTER fix)
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-008-KR (P0 즉시 구현 변수 — DUAL_FLOW)
strategy_cards: 조회 불필요 (feature_engine 레벨 작업)
open_positions: 조회 불필요

---

## 1. 작업 개요

CEO 지시 D-008-KR P0: 한국 수급 변수 DUAL_FLOW (기관+외국인 동시 순매수 비율)를
feature_engine.py에 정식 변수화.

**배경**:
- supply_demand_gate.py L3.3에 DUAL_FLOW 개념이 있으나 raw SQL 기반 int count 반환
- feature_engine.py에 DualFlowEngine 클래스(T-111)가 존재하나 DB 호출 필요
- T-218: 순수 계산 함수(no DB 의존)로 feature 정식 변수화하여 CTE 파이프라인에서 활용 가능하게

---

## 2. 사전 조사

### feature_engine.py 현황
- `DualFlowEngine` 클래스 (T-111 구현): `calculate_dual_flow(symbol, date)` 메서드
  - DB에서 v4_investor_daily 조회 → DUAL_FLOW_5D/20D 계산
  - 기존 테스트 6/6 ALL PASS (`tests/unit/test_dual_flow.py`)
- 문제: DB 의존으로 인해 backtest/pipeline에서 직접 활용 어려움

### supply_demand_gate.py L3.3
- `_get_dual_flow(ticker, date, window=5)` → int count (0~5) 반환
- DualFlowEngine 미사용, 독자 raw SQL 구현
- `DUAL_FLOW_5D >= 3 (+1점)` 가산 점수로 활용

### CTE 파이프라인 연결
- cte_pipeline.py → supply_demand_gate.py (L3.3) → `_get_dual_flow()` 사용
- feature_engine.DualFlowEngine은 CTE 파이프라인과 미연결 상태

---

## 3. 구현 내용

### 3-1. 백업
```bash
cp backend/app/services/feature_engine.py \
   backend/app/services/feature_engine.py.bak.20260307
```

### 3-2. feature_engine.py 추가 내용

`backend/app/services/feature_engine.py` 의 DualFlowEngine 클래스 직후 (행 317 이후)에
**T-218 섹션** 으로 두 개의 순수 계산 함수 추가:

#### `compute_dual_flow_5d(rows, window=5) -> float`
```python
def compute_dual_flow_5d(rows: list, window: int = 5) -> float:
    """
    DUAL_FLOW_5D: 최근 5거래일 중 기관+외국인 동시 순매수 일수 / 5
    입력: rows (foreign_net_qty, institution_net_qty) — DB 의존 없음
    산출: ratio [0.0, 1.0]
    """
    if not rows:
        return 0.0
    target = rows[:window]
    if not target:
        return 0.0
    dual_count = sum(
        1 for r in target
        if (r.get("foreign_net_qty") or 0) > 0
        and (r.get("institution_net_qty") or 0) > 0
    )
    return round(dual_count / window, 4)
```

#### `compute_dual_flow_20d(rows, window=20) -> float`
```python
def compute_dual_flow_20d(rows: list, window: int = 20) -> float:
    """
    DUAL_FLOW_20D: 최근 20거래일 중 기관+외국인 동시 순매수 일수 / 실제 행 수
    입력: rows (foreign_net_qty, institution_net_qty) — DB 의존 없음
    산출: ratio [0.0, 1.0]
    """
    if not rows:
        return 0.0
    target = rows[:window]
    if not target:
        return 0.0
    dual_count = sum(
        1 for r in target
        if (r.get("foreign_net_qty") or 0) > 0
        and (r.get("institution_net_qty") or 0) > 0
    )
    return round(dual_count / max(len(target), 1), 4)
```

**설계 포인트**:
- DB 의존 없음 → backtest/replay/CTE 어디서든 사용 가능
- DualFlowEngine.calculate_dual_flow()와 동일 로직 (ratio 계산)
- supply_demand_gate._get_dual_flow()의 int count와 차별화 (ratio 반환)

### 3-3. CTE 파이프라인 L3.3 연결 확인
- supply_demand_gate.py `_get_dual_flow()` → int count 방식 유지 (하위호환)
- feature_engine의 compute_dual_flow_5d/20d는 ratio 방식으로 backtest/AI 파이프라인 활용
- L3.3: cte_pipeline.py → supply_demand_gate (기존 방식 유지, 서비스 재시작 금지 원칙)

---

## 4. 테스트 결과

### 신규 테스트 (`tests/unit/test_T218_dual_flow_feature.py`)

```
tests/unit/test_T218_dual_flow_feature.py::TestTC1AllBuy::test_dual_flow_5d_all_buy PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC1AllBuy::test_dual_flow_20d_all_buy PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC2ZeroBuy::test_dual_flow_5d_zero PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC2ZeroBuy::test_dual_flow_20d_zero PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC3Partial::test_dual_flow_5d_partial PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC3Partial::test_dual_flow_20d_partial PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC4NoData::test_dual_flow_5d_no_data PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC4NoData::test_dual_flow_20d_no_data PASSED
============================= 8 passed in 0.12s ================================
```

| TC | 케이스 | 결과 |
|----|--------|------|
| TC-1 | 5일 전체 동시매수 → DUAL_FLOW_5D=1.0 | PASS |
| TC-2 | 0일 동시매수 (데이터 있음) → 0.0 | PASS |
| TC-3 | 부분 (2/5=0.4, 8/20=0.4) | PASS |
| TC-4 | 데이터 부재 → 0.0 | PASS |

### 기존 테스트 회귀 확인

```
tests/unit/test_dual_flow.py: 6/6 ALL PASS (DualFlowEngine 기존 구현 이상 없음)
```

---

## 5. 커밋 정보

| 항목 | 내용 |
|------|------|
| 커밋 해시 | faa85636 |
| 브랜치 | phase-2c-command-center |
| 커밋 메시지 | [V4.1] feat: T-218 DUAL_FLOW_5D/20D feature variable (D-008-KR P0) |
| 변경 파일 | backend/app/services/feature_engine.py (+57줄) |
| 신규 파일 | tests/unit/test_T218_dual_flow_feature.py (+126줄) |
| push | origin/phase-2c-command-center |

---

## 6. 성공 기준 점검

| 기준 | 결과 |
|------|------|
| compute_dual_flow_5d/20d 함수 구현 | ✅ 완료 |
| 4케이스 테스트 ALL PASS | ✅ 8/8 PASS (케이스당 2개 서브테스트) |
| git commit + push | ✅ faa85636 push 완료 |
| 서비스 재시작 금지 준수 | ✅ (순수 코드 변경만) |
| strategy_cards 변경 금지 준수 | ✅ |

---

## 7. 금지 사항 준수

- ❌ 서비스 재시작: 없음
- ❌ strategy_cards 변경: 없음
- ❌ .env/.bak 파일 커밋: 없음

---

## 8. 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4, faa85636)
- [ ] project-docs 보고서 push (진행 예정)

---

HANDOVER.md 업데이트 완료: (project-docs push 후 기재)
