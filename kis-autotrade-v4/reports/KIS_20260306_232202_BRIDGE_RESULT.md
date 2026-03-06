---
project: KIS-autotrade-v4
task_id: T-216
completed_at: 2026-03-07T00:20:00+09:00
---

# T-216 실행 결과 보고서

## 지시서: KIS_20260306_232202_BRIDGE.md

**Task ID:** T-216
**Priority:** P1-HIGH
**커밋 (kis-autotrade-v4):** 8d74d00c
**커밋 (project-docs):** 941eeac

---

## 1. 인계 확인

[인계 확인]
직전 완료: T-215
현재 단계: Phase 2C
CEO 지시 적용: D-001, D-003, D-010
strategy_cards: N/A (변경 없음)
open_positions: N/A (런타임 미확인, 비거래일)

---

## 2. 작업 지시 내용

```
unified_engine.py 또는 signal_generator.py에서 TradeSignal 생성 시 source 필드 설정 코드 확인
grep -rn "source.*VIRTUAL_KIS\|source.*NXT_AM\|source.*NXT_PM" backend/ --include="*.py" | head -20
source 전파 경로 추적: 어디서 signal.source가 설정되는지 확인
미전파 시: signal 생성 지점에 source 할당 코드 추가 (notes에서 추출 또는 ENV/config 기반)
문법 검사 → 테스트 → git commit + push ([V4.1] fix: T-216 ensure source propagation for PRE_SOURCE_FILTER)
03‑07 로그에서 PRE_SOURCE_FILTER BLOCK 로그 발생 여부 확인 계획 기재
성공기준: source 전파 경로 확인 또는 수정 완료
금지: 서비스 재시작, strategy_cards 변경
```

---

## 3. 분석 결과

### 3-1. grep 실행 결과

```bash
$ grep -rn "source.*VIRTUAL_KIS\|source.*NXT_AM\|source.*NXT_PM" backend/ --include="*.py" | head -20
(결과 없음)

$ grep -rn "PRE_SOURCE_FILTER\|source_filter\|VIRTUAL_KIS_MOCK\|NXT_AM\|NXT_PM" backend/ --include="*.py" | head -30
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:163:    # 예: "VIRTUAL_KIS_MOCK", "PM", "" 등
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:164:    # funnel_score.yaml session_strategy_filter 와 매핑
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:165:    source: str = ""
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:427:        # ── 사전 필터 3.5: 소스별 전략 필터 (T-196) ────────────────────────────────────────
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:435:        if _sf_cfg.get("enabled", False) and signal.source:
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:441:                    result.blocking_layer = "PRE_SOURCE_FILTER"
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:447:                        "  PRE_SOURCE_FILTER[%s] source=%s strategy=%s → BLOCK (허용: %s)",
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:452:                    "  PRE_SOURCE_FILTER[%s] source=%s strategy=%s → PASS",
/root/kis-autotrade-v4/backend/app/services/data/kis_ws_collector.py:47:    "NXT_AM": {"start": "08:00", "end": "08:50"},
/root/kis-autotrade-v4/backend/app/services/data/kis_ws_collector.py:48:    "NXT_PM": {"start": "15:40", "end": "20:00"},
/root/kis-autotrade-v4/backend/app/services/unified_engine/config.py:23:    KIS_MOCK = "kis-mock"
```

### 3-2. 근본 원인 분석

**파일:** `backend/app/services/unified_engine/core/signal_generator.py`
**함수:** `SignalGenerator._evaluate_strategy()` 라인 359

```python
# ❌ 수정 전: source 필드 누락
signal = TradeSignal(
    strategy_id=actual_strategy_id,
    trigger="UNIFIED_ENGINE",
    tactic="UNIFIED",
    symbol=ticker,
    price=float(price),
    atr14=atr14,
    spread_pct=spread_pct,
    vp_ratio=vp_ratio,
    surge_pct=0.0,
    bars_since_signal=1,
    vol_ratio=vp_ratio,
    price_position=0.5,
    is_pullback_strategy=strategy_id in ("D2", "D4", "D5", "S1"),
    dcs_grade=dcs_grade,
    tech_rank="MID",
    market_regime=market_regime,
    open_positions_count=open_count,
    portfolio_daily_pnl_pct=portfolio_daily_pnl_pct,
    kosdaq_change_pct=kosdaq_change_pct,
    volume_rank=volume_rank,
    daily_change_pct=daily_change_pct,
    has_lower_low_13_14=has_lower_low,
    d6_positions_today=self._d6_positions_today,
    supply_gate_result=supply_result,
    # ← source 없음 → 기본값 "" → PRE_SOURCE_FILTER 항상 건너뜀
)
```

**PRE_SOURCE_FILTER 조건 (cte_pipeline.py:435):**
```python
if _sf_cfg.get("enabled", False) and signal.source:
    # signal.source == "" → 조건 False → 필터 항상 건너뜀 (Fail-Open)
```

**결론:**
- `signal.source = ""` (기본값) → `and signal.source` = `and ""` = `False` → PRE_SOURCE_FILTER 건너뜀
- KIS_MOCK 세션에서도 D4/D5/D7/D2/S1 전략이 필터 없이 통과
- T-196에서 설계된 D6 전용화가 실질적으로 작동하지 않는 상태

---

## 4. 수정 내용

### 4-1. signal_generator.py 수정

**파일:** `backend/app/services/unified_engine/core/signal_generator.py`

**수정 1: `__init__` 파라미터 추가**

```python
# 수정 전
def __init__(
    self,
    cte_pipeline: Any,
    scoring_engine: Any = None,
    bridge_client: Any = None,
    pool: Any = None,
) -> None:
    self._cte = cte_pipeline
    self._scoring = scoring_engine
    self._bridge = bridge_client
    self._dcs_calc = DCSCalculator()
    self._d6_positions_today: Set[str] = set()
    self._supply_gate = SupplyDemandGate(pool=pool) if pool else None

# 수정 후
def __init__(
    self,
    cte_pipeline: Any,
    scoring_engine: Any = None,
    bridge_client: Any = None,
    pool: Any = None,
    session_source: str = "",
) -> None:
    self._cte = cte_pipeline
    self._scoring = scoring_engine
    self._bridge = bridge_client
    self._dcs_calc = DCSCalculator()
    self._d6_positions_today: Set[str] = set()
    self._supply_gate = SupplyDemandGate(pool=pool) if pool else None
    # T-216: 소스(세션) 식별자 — PRE_SOURCE_FILTER 전파용
    # 예: "VIRTUAL_KIS_MOCK" (KIS 모의투자), "" (일반)
    self._session_source: str = session_source
```

**수정 2: TradeSignal 생성 시 source 전파**

```python
signal = TradeSignal(
    ...
    supply_gate_result=supply_result,
    source=self._session_source,  # T-216: 소스 전파 (PRE_SOURCE_FILTER 활성화)
)
```

### 4-2. engine.py 수정

**파일:** `backend/app/services/unified_engine/engine.py`

**수정: DataSourceType import 추가 + session_source 계산 후 전달**

```python
# import에 DataSourceType 추가
from .config import (
    ActionType,
    CONCURRENT_LIMIT,
    DataSourceType,  # T-216 추가
    EngineMode,
    SHADOW_STRATEGIES,
    UnifiedEngineConfig,
)

# SignalGenerator 초기화 시 session_source 전달
# T-216: KIS_MOCK 세션 source 식별자 — PRE_SOURCE_FILTER 전파
_session_source = (
    "VIRTUAL_KIS_MOCK"
    if config.data_source == DataSourceType.KIS_MOCK
    else ""
)
self.signal_gen = SignalGenerator(
    cte_pipeline=cte_pipeline,
    scoring_engine=scoring_engine,
    bridge_client=bridge_client,
    pool=pool,
    session_source=_session_source,
)
```

**매핑:**
| config.data_source | session_source | PRE_SOURCE_FILTER |
|---|---|---|
| DataSourceType.KIS_MOCK | "VIRTUAL_KIS_MOCK" | 활성화 (D6만 허용) |
| DataSourceType.DB | "" | Fail-Open (필터 건너뜀) |

---

## 5. 문법 검사 결과

```bash
$ /root/kis-autotrade-v4/venv/bin/python3 -c "
from backend.app.services.unified_engine.core.signal_generator import SignalGenerator
from backend.app.services.unified_engine.engine import UnifiedEngine
print('Import OK')
sg = SignalGenerator(cte_pipeline=None, session_source='VIRTUAL_KIS_MOCK')
print(f'SignalGenerator._session_source = {repr(sg._session_source)}')
"
Import OK
SignalGenerator._session_source = 'VIRTUAL_KIS_MOCK'
```

---

## 6. 테스트 실행 결과

### 신규 테스트 (TC-30~TC-35) — 6건 ALL PASS

```
tests/test_unified_engine.py::TestSourcePropagation::test_signal_generator_kis_mock_session_source PASSED
tests/test_unified_engine.py::TestSourcePropagation::test_signal_generator_db_session_source_empty PASSED
tests/test_unified_engine.py::TestSourcePropagation::test_engine_sets_session_source_for_kis_mock PASSED
tests/test_unified_engine.py::TestSourcePropagation::test_engine_sets_session_source_empty_for_db PASSED
tests/test_unified_engine.py::TestSourcePropagation::test_pre_source_filter_bypass_when_source_empty PASSED
tests/test_unified_engine.py::TestSourcePropagation::test_pre_source_filter_active_when_source_set PASSED
```

### 기존 테스트 회귀 검증

```
tests/test_unified_engine.py: 27 passed, 1 pre-existing failed
tests/unit/test_technical_signals.py: 29/29 PASS

총계: 61 passed, 1 pre-existing failed (test_time_close MagicMock issue, T-216 무관)
```

---

## 7. git commit + push 결과

```bash
$ sudo /usr/bin/git -C /root/kis-autotrade-v4 commit -m "[V4.1] fix: T-216 ensure source propagation for PRE_SOURCE_FILTER"
[phase-2c-command-center 8d74d00c] [V4.1] fix: T-216 ensure source propagation for PRE_SOURCE_FILTER
 3 files changed, 94 insertions(+)

$ sudo /usr/bin/git -C /root/kis-autotrade-v4 push origin phase-2c-command-center
To github.com:moongoby/go100.git
   e55aff96..8d74d00c  phase-2c-command-center -> phase-2c-command-center
```

---

## 8. 03-07 로그 확인 계획

PRE_SOURCE_FILTER 동작 확인 (03-09 첫 거래일 이후):

```bash
# PRE_SOURCE_FILTER BLOCK 로그 확인
grep "PRE_SOURCE_FILTER" /var/log/go100.log | tail -20

# 기대 동작
# D4/D5/D7/D2/S1 신호:
# "PRE_SOURCE_FILTER[{ticker}] source=VIRTUAL_KIS_MOCK strategy=D4 → BLOCK (허용: ['D6'])"
# D6 신호:
# "PRE_SOURCE_FILTER[{ticker}] source=VIRTUAL_KIS_MOCK strategy=D6 → PASS"
```

---

## 9. 성공 기준 달성

- [x] source 전파 경로 확인 완료
- [x] 미전파 지점 발견: `signal_generator.py` `_evaluate_strategy()` → TradeSignal 생성 시 source 필드 없음
- [x] 수정 완료: session_source 파라미터 → TradeSignal.source 전파
- [x] 문법 검사: 정상 import 확인
- [x] 테스트: TC-30~TC-35 6/6 PASS, 61/62 전체 PASS
- [x] git commit: 8d74d00c
- [x] git push: phase-2c-command-center 성공
- [x] 03-07 로그 확인 계획 기재

---

## 10. 보고서 정보

- 로컬 보고서: `/root/kis-autotrade-v4/report/v41/CUR-V41-SOURCE-PROPAGATION-VERIFY-001-20260307.md`
- project-docs 경로: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-SOURCE-PROPAGATION-VERIFY-001-20260307.md`
- GitHub 보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-SOURCE-PROPAGATION-VERIFY-001-20260307.md
- GitHub 커밋: https://github.com/moongoby/project-docs/commit/941eeac
- HANDOVER: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md
- HTTP 확인: 200

---

## 체크포인트

- [x] 코드 레포 커밋 완료: kis-autotrade-v4 커밋 8d74d00c
- [x] project-docs 보고서 push 완료: 941eeac, HTTP 200 확인
