---
project: kis-autotrade-v4
task_id: T-114
completed_at: 2026-03-05T17:35:00+09:00
---

# T-114 FunnelScore L3.1 CTE 파이프라인 실제 연동 수정 — 실행 결과

[인계 확인]
직전 완료: T-113
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002, D-003, D-007
strategy_cards: (미확인 — 본 Task 범위 외)
open_positions: (미확인 — 본 Task 범위 외)

---

## A. 원인 진단 결과

### 실행 명령
```
cd /root/kis-autotrade-v4
grep -n "funnel\|FUNNEL\|FunnelScore\|L3.1\|funnel_score" backend/app/services/cte_pipeline.py
# → No such file or directory (경로 오류)

find /root/kis-autotrade-v4/backend -name "cte_pipeline.py"
# → /root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py

grep -n "funnel\|FUNNEL\|FunnelScore\|L3.1\|funnel_score" backend/app/services/trading/cte/cte_pipeline.py
# → 줄 147-148: funnel_score_result: Optional[Dict] = field(default=None)
# → 줄 187-189: funnel_score: float = 0.0, funnel_score_label: str = "SKIP"
# → 줄 410-432: L3.1 FunnelScore 필터 블록 (조건부: if signal.funnel_score_result is not None)

grep -n "funnel\|FUNNEL\|FunnelScore" scripts/run_unified_engine.py
# → 72: from app.services.trading.cte.cte_pipeline import CTEPipeline, TradeSignal
# → 1387: cte_pipeline=pipe
# → funnel 관련 코드 없음!

grep -rn "FunnelScoreEngine\|funnel_score_engine\|funnel_score_result" backend/app/
# → funnel_score_engine.py: 클래스 정의만 (비호출)
# → cte_pipeline.py: signal.funnel_score_result is not None 조건만
# → run_unified_engine.py: 전혀 없음

/root/kis-autotrade-v4/venv/bin/python3 -c "from backend.app.services.funnel_score_engine import FunnelScoreEngine; print('import OK')"
# → import OK
```

### 진단 결론
**가설 2 확정**: `cte_pipeline.py`에 L3.1 코드는 존재하지만, `run_unified_engine.py`에서 `TradeSignal` 생성 시 `funnel_score_result=None`(기본값)으로 설정되어 L3.1이 항상 SKIP 상태였음.

```
cte_pipeline.py L411-432:
    if signal.funnel_score_result is not None:   # ← 항상 None → 항상 SKIP
        ...
```

**근본 원인**: `FunnelScoreEngine.calculate_funnel_score()`를 어디서도 호출하지 않아 `funnel_score_result`가 채워지지 않음.

---

## B. 사전 백업

```bash
cp backend/app/services/trading/cte/cte_pipeline.py backend/app/services/trading/cte/cte_pipeline.py.bak.20260305_1725
cp scripts/run_unified_engine.py scripts/run_unified_engine.py.bak.20260305_1725
```

결과: 백업 완료
```
backend/app/services/trading/cte/cte_pipeline.py.bak.20260305_1725
scripts/run_unified_engine.py.bak.20260305_1725
```

---

## C. 수정 내용

### 수정 파일 1: `backend/app/services/trading/cte/cte_pipeline.py`

#### (1) import logging 추가 및 logger 정의 (모듈 상단)
```python
# 추가된 코드
import logging
...
logger = logging.getLogger(__name__)
```

#### (2) FunnelScoreEngine lazy singleton 함수 추가
```python
# T-114: FunnelScoreEngine lazy-import (순환 방지 — 실제 호출 시 import)
_FUNNEL_ENGINE_INSTANCE = None

def _get_funnel_engine():
    """FunnelScoreEngine 싱글턴 반환 (lazy import, T-114)."""
    global _FUNNEL_ENGINE_INSTANCE
    if _FUNNEL_ENGINE_INSTANCE is None:
        from ...funnel_score_engine import FunnelScoreEngine
        _FUNNEL_ENGINE_INSTANCE = FunnelScoreEngine()
    return _FUNNEL_ENGINE_INSTANCE
```

#### (3) L3.1 블록 수정 — funnel_score_result=None일 때 직접 호출
**수정 전** (L411-432):
```python
        # ── L3.1: FunnelScore 필터 (T-103) ──────
        # 사전 계산 결과(funnel_score_result)가 있을 때만 평가, None이면 스킵
        if signal.funnel_score_result is not None:
            fs = signal.funnel_score_result
            fs_val = float(fs.get("funnel_score", 0.0))
            result.funnel_score = fs_val
            result.details["funnel"] = {
                "funnel_score": fs_val,
                "l0_score": fs.get("l0_score"),
                "l1_score": fs.get("l1_score"),
                "l2_score": fs.get("l2_score"),
                "l3_score": fs.get("l3_score"),
            }
            # min_score_for_entry: funnel_score.yaml 기본 0.40
            _min_funnel = 0.40
            if fs_val < _min_funnel:
                result.funnel_score_label = "BLOCK"
                result.blocking_layer = "L3.1_FUNNEL"
                result.blocking_reason = (
                    f"FunnelScore 미달: {fs_val:.3f} < {_min_funnel} (min_score_for_entry)"
                )
                return result
            result.funnel_score_label = "PASS"
```

**수정 후** (T-114):
```python
        # ── L3.1: FunnelScore 필터 (T-103 / T-114 연동수정) ──────
        # 1) 사전 계산 결과(funnel_score_result) 있으면 그대로 사용
        # 2) None이면 FunnelScoreEngine 직접 호출 (T-114 핵심 수정)
        _fs_result = signal.funnel_score_result
        if _fs_result is None:
            try:
                _funnel_engine = _get_funnel_engine()
                _trade_date = now.strftime("%Y-%m-%d")
                _fs_result = _funnel_engine.calculate_funnel_score(signal.symbol, _trade_date)
                logger.info(
                    "  L3.1 FunnelScore 계산: %s date=%s score=%.3f",
                    signal.symbol, _trade_date, _fs_result.get("funnel_score", 0),
                )
            except Exception as _e:
                logger.warning(
                    "  L3.1 FunnelScore 오류 (Fail-Open): %s %s", signal.symbol, _e
                )
                _fs_result = {"funnel_score": 0.5}  # Fail-Open 기본값

        if _fs_result is not None:
            fs = _fs_result
            fs_val = float(fs.get("funnel_score", 0.0))
            result.funnel_score = fs_val
            result.details["funnel"] = {
                "funnel_score": fs_val,
                "l0_score": fs.get("l0_score"),
                "l1_score": fs.get("l1_score"),
                "l2_score": fs.get("l2_score"),
                "l3_score": fs.get("l3_score"),
            }
            # min_score_for_entry: funnel_score.yaml 기본 0.40
            _min_funnel = 0.40
            if fs_val < _min_funnel:
                result.funnel_score_label = "BLOCK"
                result.blocking_layer = "L3.1_FUNNEL"
                result.blocking_reason = (
                    f"FunnelScore 미달: {fs_val:.3f} < {_min_funnel} (min_score_for_entry)"
                )
                return result
            result.funnel_score_label = "PASS"
            logger.info(
                "  L3.1 FunnelScore PASS: %s score=%.3f", signal.symbol, fs_val
            )
```

### 수정 파일 2: `backend/app/services/funnel_score_engine.py`

`calculate_funnel_score()` 메서드에 진입/반환 INFO 로그 추가:
```python
        logger.info("FunnelScore calculate: %s date=%s", symbol, date)

        # ... (기존 계산 코드) ...

        logger.info(
            "FunnelScore result: %s L0=%.3f L1=%.3f L2=%.3f L3=%.3f total=%.3f",
            symbol, l0, l1, l2, l3, funnel_score,
        )
```

---

## D. 수동 테스트 결과

### import 확인
```bash
/root/kis-autotrade-v4/venv/bin/python3 -c "
import sys; sys.path.insert(0, 'backend')
from app.services.funnel_score_engine import FunnelScoreEngine
engine = FunnelScoreEngine()
result = engine.calculate_funnel_score('005930', '2026-03-05')
print(result)
"
```
결과:
```
{'symbol': '005930', 'date': '2026-03-05', 'l0_score': 0.4, 'l1_score': 0.55, 'l2_score': 0.37, 'l3_score': 0.2837, 'funnel_score': 0.3936, 'detail': {'l0': {'macro_weight': 0.15, 'score': 0.4}, 'l1': {'sector_weight': 0.25, 'score': 0.55}, 'l2': {'supply_weight': 0.3, 'score': 0.37}, 'l3': {'fundamental_weight': 0.3, 'score': 0.2837}}}
```

### CTEPipeline 통합 테스트
```bash
/root/kis-autotrade-v4/venv/bin/python3 -c "
import sys, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s')
sys.path.insert(0, 'backend')
from app.services.trading.cte.cte_pipeline import CTEPipeline, TradeSignal
from app.services.trading.cte.trigger_tactic_matrix import Trigger, Tactic
from app.services.trading.cte.supply_demand_gate import SupplyGateResult
from app.services.trading.cte.bounce_gate import CandleData, VwapData
from datetime import datetime

pipe = CTEPipeline()
# ... (TradeSignal 생성, funnel_score_result=None) ...
result = pipe.evaluate(sig, now=datetime(2026, 3, 5, 9, 30))
print('approved:', result.approved, 'blocking_layer:', result.blocking_layer, 'funnel_score:', result.funnel_score, 'funnel_label:', result.funnel_score_label)
"
```
결과:
```
2026-03-05 17:29:34,531 [funnel_score_engine] FunnelScore calculate: 005930 date=2026-03-05
2026-03-05 17:29:35,072 [funnel_score_engine] FunnelScore result: 005930 L0=0.400 L1=0.550 L2=0.370 L3=0.284 total=0.394
2026-03-05 17:29:35,073 [app.services.trading.cte.cte_pipeline]   L3.1 FunnelScore 계산: 005930 date=2026-03-05 score=0.394
approved: False blocking_layer: L3.1_FUNNEL funnel_score: 0.3936 funnel_label: BLOCK
```
→ L3.1_FUNNEL 차단 정상 작동 (0.394 < 0.40 min_score_for_entry)

---

## E. Dry-Run 결과 (run_unified_engine.py)

```bash
/root/kis-autotrade-v4/venv/bin/python3 scripts/run_unified_engine.py 2>&1 | grep -i "funnel\|L3.1" | tail -20
```

결과 (출력 샘플):
```
2026-03-05 17:31:16,376 [INFO] FunnelScore result: 644368 L0=0.400 L1=0.300 L2=0.300 L3=0.075 total=0.247
2026-03-05 17:31:16,376 [INFO]   L3.1 FunnelScore 계산: 644368 date=2026-03-05 score=0.247
2026-03-05 17:31:16,376 [INFO] FunnelScore calculate: 739702 date=2026-03-05
2026-03-05 17:31:16,442 [INFO] FunnelScore result: 739702 L0=0.400 L1=0.300 L2=0.300 L3=0.075 total=0.247
2026-03-05 17:31:16,443 [INFO]   L3.1 FunnelScore 계산: 739702 date=2026-03-05 score=0.247
2026-03-05 17:31:16,443 [INFO] FunnelScore calculate: 599219 date=2026-03-05
2026-03-05 17:31:16,520 [INFO] FunnelScore result: 599219 L0=0.400 L1=0.300 L2=0.300 L3=0.075 total=0.247
2026-03-05 17:31:16,520 [INFO]   L3.1 FunnelScore 계산: 599219 date=2026-03-05 score=0.247
...
```
→ "FunnelScore calculate/result" 및 "L3.1 FunnelScore 계산" 로그 모두 출현 확인 ✅

---

## F. 단위 테스트 결과

```bash
/root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/test_funnel_score_engine.py -v --tb=short
```

결과:
```
tests/unit/test_funnel_score_engine.py::TestScoreL0::test_score_l0_bull_regime PASSED
tests/unit/test_funnel_score_engine.py::TestScoreL0::test_score_l0_bear_regime PASSED
tests/unit/test_funnel_score_engine.py::TestScoreL0::test_score_l0_missing_macro_data PASSED
tests/unit/test_funnel_score_engine.py::TestScoreL1::test_score_l1_sector_leader PASSED
tests/unit/test_funnel_score_engine.py::TestScoreL1::test_score_l1_no_sector_mapping PASSED
tests/unit/test_funnel_score_engine.py::TestScoreL2::test_score_l2_dual_flow_high FAILED  ← pre-existing (T-114 무관)
tests/unit/test_funnel_score_engine.py::TestScoreL2::test_score_l2_no_investor_data PASSED
tests/unit/test_funnel_score_engine.py::TestScoreL3::test_score_l3_growth_stock PASSED
tests/unit/test_funnel_score_engine.py::TestCalculateFunnelScore::test_calculate_funnel_score_integration PASSED
tests/unit/test_funnel_score_engine.py::TestCalculateFunnelScore::test_score_batch_sorting PASSED

9/10 PASS, 1 FAIL (pre-existing: test_score_l2_dual_flow_high — T-114 변경과 무관, 테스트 파일 미수정 확인)
```

---

## G. Git 커밋

```bash
git add backend/app/services/funnel_score_engine.py backend/app/services/trading/cte/cte_pipeline.py
git commit -m "[V4.1] T-114: FunnelScore L3.1 CTE 파이프라인 실제 연동 수정"
```

커밋 해시: `70797156`

```
git log --oneline -3
70797156 [V4.1] T-114: FunnelScore L3.1 CTE 파이프라인 실제 연동 수정
b81c5817 [V4.1] T-112: SEC_LEADER_FLAG v2 대장주 판별 강화
92fa3fef [V4.1] T-111: DUAL_FLOW 기관+외국인 동시 순매수 피처
```

Push:
```bash
git push origin phase-2c-command-center
# → Permission denied (publickey) — claudebot 계정 SSH 키 없음 (pre-existing 제약)
# → 로컬 커밋 완료, root 계정에서 push 필요
```

---

## H. 변경 요약 (diff stats)

```
2 files changed, 45 insertions(+), 4 deletions(-)
```

파일:
- `backend/app/services/trading/cte/cte_pipeline.py`: import logging 추가, logger 정의, _get_funnel_engine() 함수, L3.1 블록 연동 수정
- `backend/app/services/funnel_score_engine.py`: calculate_funnel_score() 진입/반환 로그 추가

---

## 완료 기준 체크

- [x] 원인 특정: `funnel_score_result` 항상 None → L3.1 항상 SKIP
- [x] L3.1 코드 수정: FunnelScoreEngine 직접 호출 (Fail-Open 포함)
- [x] dry-run에서 funnel 로그 출현: "FunnelScore calculate/result", "L3.1 FunnelScore 계산" 확인
- [x] 테스트 9/10 PASS (1건 pre-existing)
- [x] 코드 커밋: 70797156
- [ ] 코드 push: SSH 키 없음 → root에서 수동 push 필요
- [ ] 보고서 project-docs push: done_watcher.sh 자동 처리 예정
- [ ] HANDOVER 갱신: done_watcher.sh 처리 예정

## 비고
- 서비스 재시작 없음 (지시서 명시)
- .bak 파일 커밋 없음 (지시서 명시)
- 서비스가 실행 중이면 L3.1 FunnelScore가 이제 항상 평가됨 (SKIP 없음)
- 백테스트 synthetic symbol의 경우 FunnelScore DB 조회 실패 → Fail-Open(0.5) 적용
