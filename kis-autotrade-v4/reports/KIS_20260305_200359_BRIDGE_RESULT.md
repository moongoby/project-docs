---
project: KIS-AutoTrade-V4.1
task_id: T-130
completed_at: 2026-03-05T20:46 KST
---

# T-130 실행 결과 보고서
## DESK543 프랙탈 트리거 실전 연결 + DESK5 코어 보유 정책 (D-012/D-014)

---

## 1. 지시서 원문 요약

**파일**: `/root/.genspark/directives/running/KIS_20260305_200359_BRIDGE.md`

- Task ID: T-130
- 제목: DESK543 프랙탈 트리거 실전 연결 + DESK5 코어 보유 정책 (D-012/D-014)
- 서버: 211 (kis-autotrade-v4)
- 우선순위: P1-HIGH
- 의존성: 없음

**배경**: CEO D-012 — 트리거=매수신호. D-014 — DESK5 청산 3조건만 허용, -30% 손실이어도 절대 청산 금지.

---

## 2. 사전 작업

### 2-1. 백업 생성
```
cp backend/app/services/desk_filters/pipeline.py \
   backend/app/services/desk_filters/pipeline.py.bak.20260305_2045
cp config/param_search_space.yaml \
   config/param_search_space.yaml.bak.20260305_2045
```
**결과**: 백업 완료 ✅

---

## 3. 기존 코드 분석

T-127에서 이미 생성된 파일 확인:
- `backend/app/services/fractal_live_connector.py` — 존재 (T-127 구현)
- `tests/unit/test_fractal_live.py` — 존재 (21개 테스트)
- `config/param_search_space.yaml` → `fractal_live` 섹션 존재 (T-127 구현)
- `backend/app/services/desk_filters/pipeline.py` → fractal 통합 이미 완료 (T-127)

**판단**: T-130은 T-127에 추가하는 확장 작업. 신규 필요 요소:
1. YAML `capital_stage` 섹션 추가
2. `check_desk5_profit_action()` 메서드 추가
3. `get_capital_stage()` 메서드 추가
4. 테스트 12개 추가

---

## 4. 변경 내용 상세

### 4-1. config/param_search_space.yaml — capital_stage 추가

**위치**: `fractal_live` 섹션 내 (라인 686 이후)

**추가 내용**:
```yaml
  capital_stage:                       # T-130 자본 단계별 DESK 배분
    stage1_cap: 40000000               # 4천만 미만: DESK2 100%
    stage2_cap: 200000000              # 2억 미만: D2 60%+D3 30%+D4 10%
    stage3_cap: 1000000000             # 10억 이상: 전 DESK (D2 50%+D3 25%+D4 15%+D5 10%)
```

**결과**: 성공 ✅

---

### 4-2. backend/app/services/fractal_live_connector.py — 신규 메서드 추가

#### (A) `__init__` 업데이트
```python
self._capital_stage = self._params.get("capital_stage", {})
```

#### (B) `check_desk5_profit_action(symbol, position)` 신규 추가
```python
def check_desk5_profit_action(
    self,
    symbol: str,
    position: Dict[str, Any],
) -> Dict[str, Any]:
    """
    DESK5 D-014 수익 실현 액션 판단.
    +100% → RECOVER_PRINCIPAL (원금 회수)
    +500% → TRAIL_MA10 (주봉 MA10 트레일링)
    그 외  → HOLD
    Returns: {'action': 'RECOVER_PRINCIPAL' | 'TRAIL_MA10' | 'HOLD', 'pnl_pct': float}
    """
    cfg = self._desk5_exit
    profit_100_recover = cfg.get("profit_100_recover_principal", True)
    profit_500_trail = cfg.get("profit_500_trail_weekly_ma10", True)

    entry_price = float(position.get("entry_price", 0) or 0)
    current_price = float(position.get("current_price", 0) or 0)

    pnl_pct = 0.0
    if entry_price > 0 and current_price > 0:
        pnl_pct = (current_price - entry_price) / entry_price * 100.0

    action = "HOLD"
    if profit_500_trail and pnl_pct >= 500.0:
        action = "TRAIL_MA10"
    elif profit_100_recover and pnl_pct >= 100.0:
        action = "RECOVER_PRINCIPAL"

    return {"action": action, "pnl_pct": round(pnl_pct, 2)}
```

#### (C) `get_capital_stage(total_capital)` 신규 추가
```python
def get_capital_stage(self, total_capital: float) -> Dict[str, Any]:
    """
    자본 규모에 따른 DESK 배분 단계 반환.
    Stage 1 (< 4천만):  DESK2 100%
    Stage 2 (4천만~2억): D2 60% + D3 30% + D4 10%
    Stage 3 (2억+):      D2 50% + D3 25% + D4 15% + D5 10%
    Returns: {'stage': int, 'allocation': {...}, 'total_capital': float}
    """
    cfg = self._capital_stage
    stage1_cap = float(cfg.get("stage1_cap", 40_000_000))
    stage2_cap = float(cfg.get("stage2_cap", 200_000_000))

    if total_capital < stage1_cap:
        stage = 1
        allocation = {"desk2": 1.0, "desk3": 0.0, "desk4": 0.0, "desk5": 0.0}
    elif total_capital < stage2_cap:
        stage = 2
        allocation = {"desk2": 0.6, "desk3": 0.3, "desk4": 0.1, "desk5": 0.0}
    else:
        stage = 3
        allocation = {"desk2": 0.5, "desk3": 0.25, "desk4": 0.15, "desk5": 0.10}

    return {"stage": stage, "allocation": allocation, "total_capital": total_capital}
```

**결과**: 성공 ✅ (파일 라인 수: 361 → 452)

---

### 4-3. tests/unit/test_fractal_live.py — T-130 테스트 추가

**추가 테스트 (12개)**:

#### TC-08: check_desk5_profit_action (6개)
| 테스트 | 입력 | 기대 |
|--------|------|------|
| test_profit_action_hold | +50% | HOLD |
| test_profit_action_recover_principal | +102% | RECOVER_PRINCIPAL |
| test_profit_action_trail_ma10 | +505% | TRAIL_MA10 |
| test_profit_action_exactly_500pct | +500% | TRAIL_MA10 |
| test_profit_action_exactly_100pct | +100% | RECOVER_PRINCIPAL |
| test_profit_action_response_structure | any | 구조 검증 |

#### TC-09: get_capital_stage (5개)
| 테스트 | 입력 | 기대 |
|--------|------|------|
| test_capital_stage_1_desk2_only | 3천만 | stage=1, desk2=100% |
| test_capital_stage_2_mixed | 1억 | stage=2, D2=60%/D3=30%/D4=10% |
| test_capital_stage_3_full_desk | 5억 | stage=3, 합계=100% |
| test_capital_stage_boundary_stage1_cap | 4천만 | stage=2 |
| test_capital_stage_response_structure | any | 구조 검증 |

#### TC-10: Pipeline 통합 (1개)
| 테스트 | 흐름 |
|--------|------|
| test_pipeline_integration_fractal_and_capital | 자본단계→진입평가→포지션크기→수익액션→청산체크 전체 흐름 |

**결과**: 성공 ✅

---

## 5. pytest 실행 결과

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
collected 33 items

tests/unit/test_fractal_live.py::test_yaml_load_fractal_live PASSED      [  3%]
tests/unit/test_fractal_live.py::test_yaml_desk5_min_triggers PASSED     [  6%]
tests/unit/test_fractal_live.py::test_yaml_desk5_exit_params PASSED      [  9%]
tests/unit/test_fractal_live.py::test_desk5_entry_insufficient_triggers PASSED [ 12%]
tests/unit/test_fractal_live.py::test_desk5_entry_true_two_triggers PASSED [ 15%]
tests/unit/test_fractal_live.py::test_desk4_entry_two_triggers_pass PASSED [ 18%]
tests/unit/test_fractal_live.py::test_desk4_entry_one_trigger_fail PASSED [ 21%]
tests/unit/test_fractal_live.py::test_desk3_entry_solo_t3_1 PASSED       [ 24%]
tests/unit/test_fractal_live.py::test_desk3_entry_catalyst_rsi_pass PASSED [ 27%]
tests/unit/test_fractal_live.py::test_desk5_exit_weekly_ma20_break PASSED [ 30%]
tests/unit/test_fractal_live.py::test_desk5_exit_force_exit_volume_spike PASSED [ 33%]
tests/unit/test_fractal_live.py::test_desk5_exit_theme_death PASSED      [ 36%]
tests/unit/test_fractal_live.py::test_desk5_exit_loss_30pct_no_conditions PASSED [ 39%]
tests/unit/test_fractal_live.py::test_desk5_exit_profit_100_recover_principal PASSED [ 42%]
tests/unit/test_fractal_live.py::test_desk5_exit_profit_500_trail_ma10 PASSED [ 45%]
tests/unit/test_fractal_live.py::test_get_position_size_desk5 PASSED     [ 48%]
tests/unit/test_fractal_live.py::test_get_position_size_desk4 PASSED     [ 51%]
tests/unit/test_fractal_live.py::test_get_position_size_desk3 PASSED     [ 54%]
tests/unit/test_fractal_live.py::test_evaluate_desk5_response_structure PASSED [ 57%]
tests/unit/test_fractal_live.py::test_check_desk5_exit_response_structure PASSED [ 60%]
tests/unit/test_fractal_live.py::test_exit_without_weekly_bars PASSED    [ 63%]
tests/unit/test_fractal_live.py::test_profit_action_hold PASSED          [ 66%]
tests/unit/test_fractal_live.py::test_profit_action_recover_principal PASSED [ 69%]
tests/unit/test_fractal_live.py::test_profit_action_trail_ma10 PASSED    [ 72%]
tests/unit/test_fractal_live.py::test_profit_action_exactly_500pct PASSED [ 75%]
tests/unit/test_fractal_live.py::test_profit_action_exactly_100pct PASSED [ 78%]
tests/unit/test_fractal_live.py::test_profit_action_response_structure PASSED [ 81%]
tests/unit/test_fractal_live.py::test_capital_stage_1_desk2_only PASSED  [ 84%]
tests/unit/test_fractal_live.py::test_capital_stage_2_mixed PASSED       [ 87%]
tests/unit/test_fractal_live.py::test_capital_stage_3_full_desk PASSED   [ 90%]
tests/unit/test_fractal_live.py::test_capital_stage_boundary_stage1_cap PASSED [ 93%]
tests/unit/test_fractal_live.py::test_capital_stage_response_structure PASSED [ 96%]
tests/unit/test_fractal_live.py::test_pipeline_integration_fractal_and_capital PASSED [100%]

============================== 33 passed in 0.24s ==============================
```

**결과**: 33/33 ALL PASS ✅ (기존 21개 + 신규 12개)

---

## 6. Git 커밋

```
커밋 해시: a3d8fd50
브랜치: phase-2c-command-center
메시지: [V4.1] T-130: DESK543 프랙탈 실전 연결 + DESK5 코어 보유 — D-012/D-014
변경 파일: 3개 (254 insertions)
```

**Push 결과**: `git push origin phase-2c-command-center`
→ SSH 권한 오류 (claudebot은 SSH 키 없음, root에서 push 필요)
→ 커밋 자체는 로컬에 완료됨. root에서 push 실행 필요.

---

## 7. 파이프라인 변경 없음 (확인)

`backend/app/services/desk_filters/pipeline.py` — T-127에서 이미 fractal 통합 완료.
T-130에서 pipeline.py 변경 불필요 (기존 `_evaluate_fractal_triggers` 유지).

---

## 8. CEO 원칙 준수 확인

| 원칙 | 항목 | 상태 |
|------|------|------|
| D-012 | 트리거=매수신호 | ✅ (T-127 기반 유지) |
| D-013 | DESK5/4/3 트리거 실전 적용 | ✅ |
| D-014 | DESK5 청산 3조건만 / -30% 보유 유지 | ✅ `test_desk5_exit_loss_30pct_no_conditions` PASS |
| D-014 | +100% 원금 회수 | ✅ `RECOVER_PRINCIPAL` 구현 + 테스트 PASS |
| D-014 | +500% 주봉 MA10 트레일링 | ✅ `TRAIL_MA10` 구현 + 테스트 PASS |

---

## 9. 완료 기준 체크

- [x] config/param_search_space.yaml capital_stage 섹션 추가
- [x] fractal_live_connector.py check_desk5_profit_action() 추가
- [x] fractal_live_connector.py get_capital_stage() 추가
- [x] tests/unit/test_fractal_live.py 12개 추가 (33/33 ALL PASS)
- [x] git commit a3d8fd50 완료
- [ ] git push (SSH 권한 → root에서 수행 필요)
- [ ] project-docs 보고서 push (root에서 done_watcher.sh 또는 수동 수행 필요)
