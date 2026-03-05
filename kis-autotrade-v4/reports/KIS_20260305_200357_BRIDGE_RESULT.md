---
project: kis-autotrade-v4
task_id: T-129
completed_at: 2026-03-05T20:10:14+0900
---

# T-129 실행 결과 보고서
## 기술적 시그널 Top5 매칭 엔진 + 60분 청산 전환 (D-011)

---

## 1. 사전 작업 (bak 파일 생성)

```
cp backend/app/services/trading/exit_manager.py backend/app/services/trading/exit_manager.py.bak.202603052007
cp config/param_search_space.yaml config/param_search_space.yaml.bak.202603052007
→ bak files created (정상)
```

- signal_generator.py: 해당 파일 없음 → bak 스킵

---

## 2. config/param_search_space.yaml 수정

### 기존 exit_rules 섹션 (T-126 시점)
```yaml
exit_rules:
  intraday_timeout_minutes: 60
  ma20_exit: false
  strategies_60min: ["D2", "D4", "D5"]
  strategies_ma20: ["S1"]
```

### 추가 내용 (T-129)
```yaml
exit_rules:
  intraday_timeout_minutes: 60
  ma20_exit: false
  strategies_60min: ["D2", "D4", "D5"]
  strategies_ma20: ["S1"]
  deprecated: ["D1", "D3", "S2"]         # CEO D-011 폐기 확정 전략 (D1:PF0.89, D3:PF1.17, S2:PF0.88~1.27)
```

- technical_signals 섹션 (ts_b4_volume_explosion, ts_d1_mini_gap, ts_c1_5bar_volume, ts_b1_rsi_bounce, ts_c3_20bar_high): T-126에서 이미 존재 → 유지
- exit_rules.deprecated 필드: T-129에서 신규 추가

**참고**: T-128 커밋(d6fc488b)에 param_search_space.yaml의 T-129 변경사항이 포함됨

---

## 3. backend/app/services/trading/technical_signal_engine.py

T-126에서 이미 완전 구현됨. T-129에서 신규 생성 불필요.

파일 내용 확인:
- `class TechnicalSignalEngine` 존재
- `evaluate_ts_b4()`, `evaluate_ts_d1()`, `evaluate_ts_c1()`, `evaluate_ts_b1()`, `evaluate_ts_c3()` 5개 평가 메서드
- `evaluate_all()`: 5개 시그널 전체 평가 → List 반환
- `get_best_signal()`: PF 우선 정렬 후 최고 시그널 반환

---

## 4. backend/app/services/trading/exit_manager.py 수정

### 추가 내용

```python
# 기존 (T-126)
SIXTY_MIN_STRATEGIES = {"D2", "D4", "D5"}
MA20_STRATEGIES = {"S1"}

# T-129 추가
DEPRECATED_STRATEGIES = {"D1", "D3", "S2"}  # CEO D-011 폐기 확정
```

```python
# should_exit() 메서드 내 T-129 추가 로직
# 폐기 전략 거부 (D1/D3/S2 — CEO D-011 확정)
if strategy in DEPRECATED_STRATEGIES:
    logger.warning(
        "[EXIT_DEPRECATED] symbol=%s, strategy=%s → DEPRECATED_STRATEGY (CEO D-011)",
        symbol, strategy,
    )
    return {"exit": False, "reason": "DEPRECATED_STRATEGY", "elapsed_minutes": elapsed}
```

로깅 포맷: `[EXIT_DEPRECATED] symbol={}, strategy={} → DEPRECATED_STRATEGY (CEO D-011)`

**참고**: T-128 커밋(d6fc488b)에 exit_manager.py의 T-129 변경사항이 포함됨

---

## 5. D1/D3/S2 비활성화 상태 DB 확인

```sql
SELECT card_id, strategy_name, is_active FROM strategy_cards WHERE strategy_name IN ('D1','D3','S2');
```

### 결과
```
card_id | strategy_name | is_active
--------+---------------+----------
총 0행
→ D1/D3/S2 전략카드 없음 (미생성 또는 다른 명명 규칙)
```

**판단**: strategy_cards 테이블에 D1/D3/S2 명칭의 전략카드가 존재하지 않음.
- strategy_cards 컬럼 구조: card_id, user_id, account_id, strategy_name, strategy_type, ...
- 현 시점 활성 전략카드에 D1/D3/S2 없음 → 별도 CEO 승인 불필요 (이미 미생성 상태)

---

## 6. tests/unit/test_technical_signals.py 수정

### 기존 (T-126): 22개 테스트 (TC-01 ~ TC-22)
### T-129 추가: 5개 테스트 (TC-23 ~ TC-27)

```
TC-23: test_exit_manager_d1_deprecated
  D1 폐기 전략 → exit=False, reason=DEPRECATED_STRATEGY

TC-24: test_exit_manager_d3_deprecated
  D3 폐기 전략 → exit=False, reason=DEPRECATED_STRATEGY

TC-25: test_exit_manager_s2_deprecated
  S2 폐기 전략 (ma20 제공해도) → exit=False, reason=DEPRECATED_STRATEGY

TC-26: test_deprecated_strategies_set
  DEPRECATED_STRATEGIES 집합에 D1/D3/S2 모두 포함

TC-27: test_yaml_exit_rules_deprecated
  YAML exit_rules.deprecated=['D1','D3','S2'] 검증
```

### import 변경
```python
# 기존
from backend.app.services.trading.exit_manager import ExitManager, STRATEGY_EXIT_PARAMS
# T-129 추가
from backend.app.services.trading.exit_manager import ExitManager, STRATEGY_EXIT_PARAMS, DEPRECATED_STRATEGIES
```

---

## 7. pytest 실행 결과

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
asyncio: mode=Mode.AUTO

collected 27 items

tests/unit/test_technical_signals.py::test_ts_b4_triggered PASSED        [  3%]
tests/unit/test_technical_signals.py::test_ts_b4_not_triggered_bearish PASSED [  7%]
tests/unit/test_technical_signals.py::test_ts_d1_triggered PASSED        [ 11%]
tests/unit/test_technical_signals.py::test_ts_d1_not_triggered_gap_too_large PASSED [ 14%]
tests/unit/test_technical_signals.py::test_ts_c1_triggered PASSED        [ 18%]
tests/unit/test_technical_signals.py::test_ts_c1_not_triggered PASSED    [ 22%]
tests/unit/test_technical_signals.py::test_ts_b1_triggered PASSED        [ 25%]
tests/unit/test_technical_signals.py::test_ts_b1_not_triggered_rsi_out_of_range PASSED [ 29%]
tests/unit/test_technical_signals.py::test_ts_c3_triggered PASSED        [ 33%]
tests/unit/test_technical_signals.py::test_ts_c3_not_triggered_no_new_high PASSED [ 37%]
tests/unit/test_technical_signals.py::test_evaluate_all_returns_five_signals PASSED [ 40%]
tests/unit/test_technical_signals.py::test_get_best_signal_pf_priority PASSED [ 44%]
tests/unit/test_technical_signals.py::test_get_best_signal_none_when_no_trigger PASSED [ 48%]
tests/unit/test_technical_signals.py::test_graceful_fallback_empty_bar_data PASSED [ 51%]
tests/unit/test_technical_signals.py::test_yaml_load_technical_signals PASSED [ 55%]
tests/unit/test_technical_signals.py::test_yaml_load_exit_rules PASSED   [ 59%]
tests/unit/test_technical_signals.py::test_exit_manager_d2_60min_timeout PASSED [ 62%]
tests/unit/test_technical_signals.py::test_exit_manager_d4_hold_before_60min PASSED [ 66%]
tests/unit/test_technical_signals.py::test_exit_manager_d5_60min_exit PASSED [ 70%]
tests/unit/test_technical_signals.py::test_exit_manager_s1_ma20_break_exit PASSED [ 74%]
tests/unit/test_technical_signals.py::test_exit_manager_s1_ma20_hold PASSED [ 77%]
tests/unit/test_technical_signals.py::test_strategy_exit_params_structure PASSED [ 81%]
tests/unit/test_technical_signals.py::test_exit_manager_d1_deprecated PASSED [ 85%]
tests/unit/test_technical_signals.py::test_exit_manager_d3_deprecated PASSED [ 88%]
tests/unit/test_technical_signals.py::test_exit_manager_s2_deprecated PASSED [ 92%]
tests/unit/test_technical_signals.py::test_deprecated_strategies_set PASSED [ 96%]
tests/unit/test_technical_signals.py::test_yaml_exit_rules_deprecated PASSED [100%]

============================== 27 passed in 0.36s ==============================
```

**결과: 27/27 ALL PASS**

---

## 8. git 커밋 상태

### 로컬 브랜치 상태
- branch: phase-2c-command-center
- HEAD: d6fc488b [V4.1] T-128: DESK2 멀티컨디션 Phase A — C2(D4)/C1(D6)/C6(D7) + SignalMatcher

### T-129 변경사항 커밋 상황
T-129의 모든 변경사항(exit_manager.py, param_search_space.yaml, test_technical_signals.py)이
T-128 커밋(d6fc488b, 2026-03-05 20:08:12 KST)에 이미 포함됨.

```
commit d6fc488b...
 backend/app/services/trading/exit_manager.py    |  9 ++++
 config/param_search_space.yaml                  | 39 ++++++++++-------
 tests/unit/test_technical_signals.py            | 63 ++++++++++++++++++++++++++
 3 files changed, 94 insertions(+), 17 deletions(-)
```

T-129 별도 커밋: 변경사항이 이미 HEAD에 존재하므로 별도 커밋 불가 (nothing to commit)

### git push 상태
```
git push origin phase-2c-command-center
→ git@github.com: Permission denied (publickey).
→ SSH 키 권한은 root에서만 가능 (claudebot 권한 제약)
→ root에서 git push 필요
```

**미완료 항목**: git push origin phase-2c-command-center (root SSH 키 필요)

---

## 9. 완료 요약

| 항목 | 상태 |
|------|------|
| bak 파일 생성 | ✅ 완료 |
| YAML technical_signals 섹션 | ✅ T-126에서 구현 완료 |
| YAML exit_rules.deprecated 추가 | ✅ 완료 |
| technical_signal_engine.py | ✅ T-126에서 구현 완료 |
| exit_manager.py DEPRECATED_STRATEGIES | ✅ 완료 |
| D1/D3/S2 DB 상태 확인 | ✅ 0행 (미생성 상태 확인) |
| 테스트 TC-23~27 추가 | ✅ 완료 |
| pytest 27/27 ALL PASS | ✅ 완료 |
| git commit (로컬) | ✅ d6fc488b (T-128에 포함) |
| git push | ❌ root SSH 키 필요 |
| project-docs push | ❌ root 권한 필요 |

---

## 10. 후속 조치 필요 (root에서 실행)

```bash
# 1) git push
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center

# 2) project-docs 보고서 push
cp /root/kis-autotrade-v4/report/v41/CUR-V41-TECH-SIGNAL-EXIT-001-20260306.md \
   /root/project-docs/kis-autotrade-v4/reports/
cd /root/project-docs
git add kis-autotrade-v4/reports/CUR-V41-TECH-SIGNAL-EXIT-001-20260306.md
git commit -m "[DOCS] T-129 기술적 시그널+청산"
git push origin master

# 3) HANDOVER.md 갱신 후 push
```

---

## 11. D1/D3/S2 폐기 전략 처리 설계 결정

**ExitManager.should_exit() 동작**:
- D1/D3/S2 입력 시: `exit=False, reason="DEPRECATED_STRATEGY"` 반환
- 로그: `[EXIT_DEPRECATED] symbol=..., strategy=... → DEPRECATED_STRATEGY (CEO D-011)`
- 이유: 즉시 exit=True를 반환하면 관련 포지션이 강제 청산될 수 있음. DEPRECATED_STRATEGY reason을 반환하면 상위 로직에서 별도 처리 가능.

**CEO D-011 폐기 배경**:
- D1 (PF 0.89): 손실 전략
- D3 (PF 1.17): 수익률 부족
- S2 (PF 0.88~1.27): 불안정
