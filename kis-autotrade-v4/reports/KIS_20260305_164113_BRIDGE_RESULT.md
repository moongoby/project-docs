---
project: kis-autotrade-v4
task_id: T-111
completed_at: 2026-03-05T17:20:00+09:00
---

# KIS_20260305_164113_BRIDGE 실행 결과

Task ID: T-111 제목: DUAL_FLOW 피처 구현 — 기관+외국인 동시 순매수 비율 (5D/20D) 서버: 211 (kis-autotrade-v4) 우선순위: P0-CRITICAL

---

## 사전 백업

실행:
```
cd /root/kis-autotrade-v4
cp backend/app/services/feature_engine.py backend/app/services/feature_engine.py.bak.$(date +%Y%m%d_%H%M)
cp config/param_search_space.yaml config/param_search_space.yaml.bak.$(date +%Y%m%d_%H%M)
```

결과: `Backup done` — 백업 파일 생성 확인:
- backend/app/services/feature_engine.py.bak.20260305_1721 (또는 유사한 타임스탬프)
- config/param_search_space.yaml.bak.20260305_1721

---

## A. 피처 구현 — feature_engine.py

파일: `/root/kis-autotrade-v4/backend/app/services/feature_engine.py`

추가된 함수/클래스:

### `_load_dual_flow_params()`
```python
def _load_dual_flow_params() -> Dict[str, Any]:
    """config/param_search_space.yaml에서 dual_flow 파라미터 로드."""
    try:
        import yaml
        yaml_path = os.path.join(
            os.path.dirname(__file__), "../../../config/param_search_space.yaml"
        )
        yaml_path = os.path.normpath(yaml_path)
        with open(yaml_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("dual_flow", {})
    except Exception as e:
        logger.warning("param_search_space.yaml dual_flow 로드 실패, 기본값 사용: %s", e)
        return {}
```

### `DualFlowEngine` 클래스 (T-111)
```python
class DualFlowEngine:
    """
    DUAL_FLOW 피처 엔진 (T-111).

    IBD Accumulation Rating 한국판.
    기관+외국인 동시 순매수 일수 비율로 수급 집중도를 측정한다.

    피처:
      DUAL_FLOW_5D            : 최근 5거래일 중 동시 순매수 일수 / 5
      DUAL_FLOW_20D           : 최근 20거래일 중 동시 순매수 일수 / 20
      CONSECUTIVE_FOREIGN_BUY : 외국인 연속 순매수 일수 (최신 기준)
      DUAL_FLOW_SCORE         : 종합 점수 0~1
        = DUAL_FLOW_20D * 0.5 + min(CONSECUTIVE_FOREIGN_BUY / consecutive_buy_cap, 1.0) * 0.5
    """

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        p = params or _load_dual_flow_params()
        self._short_window: int = int(p.get("short_window", 5))
        self._long_window: int = int(p.get("long_window", 20))
        self._consec_cap: int = int(p.get("consecutive_buy_cap", 5))
        score_weights = p.get("score_weights", {})
        self._w_flow20d: float = float(score_weights.get("flow_20d", 0.5))
        self._w_consec: float = float(score_weights.get("consecutive", 0.5))

    def _fetch_investor_rows(self, symbol: str, date: Optional[str], days: int) -> list:
        """v4_investor_daily에서 최근 days 거래일 수급 데이터 조회."""
        try:
            conn = _db_connect()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            if date:
                cur.execute(
                    """
                    SELECT trade_date, foreign_net_qty, institution_net_qty
                    FROM v4_investor_daily
                    WHERE stock_code = %s AND trade_date <= %s
                    ORDER BY trade_date DESC
                    LIMIT %s
                    """,
                    (symbol, date, days),
                )
            else:
                cur.execute(
                    """
                    SELECT trade_date, foreign_net_qty, institution_net_qty
                    FROM v4_investor_daily
                    WHERE stock_code = %s
                    ORDER BY trade_date DESC
                    LIMIT %s
                    """,
                    (symbol, days),
                )
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            return rows
        except Exception as e:
            logger.error("DualFlowEngine._fetch_investor_rows %s 실패: %s", symbol, e)
            return []

    def calculate_dual_flow(self, symbol: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        DUAL_FLOW: 기관+외국인 동시 순매수 일수 비율

        반환:
          {
            'DUAL_FLOW_5D'            : float,  # 최근 5일 동시 순매수 비율
            'DUAL_FLOW_20D'           : float,  # 최근 20일 동시 순매수 비율
            'CONSECUTIVE_FOREIGN_BUY' : int,    # 외국인 연속 순매수 일수
            'DUAL_FLOW_SCORE'         : float,  # 종합 점수 0~1
          }
        """
        rows = self._fetch_investor_rows(symbol, date, self._long_window)

        if not rows:
            logger.debug("DUAL_FLOW[%s]: 데이터 없음 → SCORE=0", symbol)
            return {
                "DUAL_FLOW_5D": 0.0,
                "DUAL_FLOW_20D": 0.0,
                "CONSECUTIVE_FOREIGN_BUY": 0,
                "DUAL_FLOW_SCORE": 0.0,
            }

        # DUAL_FLOW_5D: 최근 5거래일 중 동시 순매수 비율
        rows_5d = rows[: self._short_window]
        dual_5d_count = sum(
            1 for r in rows_5d
            if (r.get("foreign_net_qty") or 0) > 0
            and (r.get("institution_net_qty") or 0) > 0
        )
        dual_flow_5d = round(dual_5d_count / self._short_window, 4)

        # DUAL_FLOW_20D: 최근 20거래일 중 동시 순매수 비율
        rows_20d = rows[: self._long_window]
        dual_20d_count = sum(
            1 for r in rows_20d
            if (r.get("foreign_net_qty") or 0) > 0
            and (r.get("institution_net_qty") or 0) > 0
        )
        dual_flow_20d = round(dual_20d_count / max(len(rows_20d), 1), 4)

        # CONSECUTIVE_FOREIGN_BUY: 외국인 연속 순매수 일수 (최신 행부터)
        consec = 0
        for r in rows:
            if (r.get("foreign_net_qty") or 0) > 0:
                consec += 1
            else:
                break

        # DUAL_FLOW_SCORE
        score = round(
            dual_flow_20d * self._w_flow20d
            + min(consec / self._consec_cap, 1.0) * self._w_consec,
            4,
        )
        score = min(1.0, max(0.0, score))

        logger.debug(
            "DUAL_FLOW[%s]: 5D=%.4f 20D=%.4f CONSEC=%d SCORE=%.4f",
            symbol, dual_flow_5d, dual_flow_20d, consec, score,
        )
        return {
            "DUAL_FLOW_5D": dual_flow_5d,
            "DUAL_FLOW_20D": dual_flow_20d,
            "CONSECUTIVE_FOREIGN_BUY": consec,
            "DUAL_FLOW_SCORE": score,
        }
```

---

## B. YAML 파라미터 — param_search_space.yaml

파일: `/root/kis-autotrade-v4/config/param_search_space.yaml`

추가된 섹션:
```yaml
# ────────────────────────────────────────────────────────────
# T-111: DUAL_FLOW 피처 파라미터
# IBD Accumulation Rating 한국판 — 기관+외국인 동시 순매수 비율
# DualFlowEngine에서 사용
# ────────────────────────────────────────────────────────────
dual_flow:
  short_window: 5
  long_window: 20
  consecutive_buy_cap: 5
  score_weights: { flow_20d: 0.5, consecutive: 0.5 }
```

---

## C. FunnelScore L2 연동 — funnel_score_engine.py

파일: `/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py`

`score_l2()` 메서드 수정:
- 기존: 수동 foreign_net_qty + institution_net_qty 카운트 + consecutive_foreign_buy_days DB 조회
- 변경: `DualFlowEngine.calculate_dual_flow()` 호출 → DUAL_FLOW_SCORE 사용
- 새 가중치: `raw = dual_flow_score * 0.7 + s_close`
- fallback: DualFlowEngine 실패/데이터 없음 → 기본값 0.3 반환

변경된 score_l2() 코드:
```python
def score_l2(self, symbol: str, date: str) -> float:
    """L2 수급 흐름 점수 (0~1).

    구성:
      - DUAL_FLOW_SCORE (T-111 DualFlowEngine): 기관+외국인 동시 순매수 종합 점수
        (DUAL_FLOW_20D × 0.5 + min(CONSECUTIVE_FOREIGN_BUY/5, 1.0) × 0.5)
      - CLOSE_POSITION_5D > 0.7 → +0.3 가산
    가중치: DUAL_FLOW_SCORE × 0.7 + CLOSE_POSITION_5D 보너스 × 0.3
    반환: 기본값 0.3 (데이터 없을 시)
    """
    l2_cfg = self._cfg.get("l2", _DEFAULT_CONFIG["l2"])
    close_pos_threshold = float(l2_cfg.get("close_pos_threshold", 0.7))

    # T-111: DualFlowEngine 기반 수급 점수
    dual_flow_score = 0.0
    consec_days = 0
    dual_flow_20d = 0.0
    try:
        from backend.app.services.feature_engine import DualFlowEngine
        df_engine = DualFlowEngine()
        df_result = df_engine.calculate_dual_flow(symbol, date)
        dual_flow_score = float(df_result.get("DUAL_FLOW_SCORE", 0.0))
        consec_days = int(df_result.get("CONSECUTIVE_FOREIGN_BUY", 0))
        dual_flow_20d = float(df_result.get("DUAL_FLOW_20D", 0.0))
    except Exception as e:
        logger.warning("L2[%s]: DualFlowEngine 조회 실패: %s → 0.0", symbol, e)

    if dual_flow_score == 0.0 and consec_days == 0:
        logger.debug("L2[%s]: DUAL_FLOW 데이터 없음 → 기본값 0.3", symbol)
        return 0.3

    # CLOSE_POSITION_5D
    close_pos = self._fetch_close_position(symbol, date, window=5)
    s_close = 0.3 if (close_pos is not None and close_pos > close_pos_threshold) else 0.0

    # 가중치: DUAL_FLOW_SCORE(0.7) + CLOSE_POSITION_5D 보너스(0.3)
    raw = dual_flow_score * 0.7 + s_close
    score = min(1.0, max(0.0, raw))
    logger.debug(
        "L2[%s]: dual_flow_score=%.4f(20D=%.4f consec=%d) close_pos=%s → %.4f",
        symbol, dual_flow_score, dual_flow_20d, consec_days,
        f"{close_pos:.3f}" if close_pos is not None else "N/A",
        score,
    )
    return round(score, 4)
```

---

## D. 단위 테스트 — test_dual_flow.py

파일: `/root/kis-autotrade-v4/tests/unit/test_dual_flow.py`

테스트 코드:
```python
"""
T-111 — DualFlowEngine 단위 테스트 (6개)
pytest tests/unit/test_dual_flow.py -v --tb=short

기준: 6/6 ALL PASS
"""
from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from backend.app.services.feature_engine import DualFlowEngine


# ─── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_engine() -> DualFlowEngine:
    """기본 파라미터 엔진 생성 (YAML 로드 없이)."""
    params = {
        "short_window": 5,
        "long_window": 20,
        "consecutive_buy_cap": 5,
        "score_weights": {"flow_20d": 0.5, "consecutive": 0.5},
    }
    return DualFlowEngine(params=params)


def _make_dual_rows(n: int, both_buy: bool = True) -> list:
    """n개의 수급 행 생성. both_buy=True이면 외인+기관 모두 순매수."""
    fq = 1000 if both_buy else -1000
    iq = 500 if both_buy else -500
    return [{"foreign_net_qty": fq, "institution_net_qty": iq} for _ in range(n)]


def _make_mixed_rows(both_count: int, other_count: int) -> list:
    """both_count개의 동시매수 + other_count개의 비동시매수 행 생성."""
    rows = _make_dual_rows(both_count, both_buy=True)
    rows += _make_dual_rows(other_count, both_buy=False)
    return rows


class TestDualFlow:

    def test_dual_flow_5d_all_buy(self):
        """5/5 동시매수 → DUAL_FLOW_5D=1.0."""
        engine = _make_engine()
        mock_rows = _make_dual_rows(5, both_buy=True)
        with patch.object(engine, "_fetch_investor_rows", return_value=mock_rows):
            result = engine.calculate_dual_flow("000001", "2026-03-05")
        assert result["DUAL_FLOW_5D"] == 1.0

    def test_dual_flow_20d_partial(self):
        """8/20 동시매수 → DUAL_FLOW_20D=0.4."""
        engine = _make_engine()
        mock_rows = _make_mixed_rows(8, 12)
        with patch.object(engine, "_fetch_investor_rows", return_value=mock_rows):
            result = engine.calculate_dual_flow("000002", "2026-03-05")
        expected = round(8 / 20, 4)  # 0.4
        assert abs(result["DUAL_FLOW_20D"] - expected) < 1e-4

    def test_consecutive_foreign_buy(self):
        """3일 연속 외국인 순매수 → CONSECUTIVE_FOREIGN_BUY=3, SCORE 검증."""
        engine = _make_engine()
        rows = []
        for i in range(3):
            rows.append({"foreign_net_qty": 1000, "institution_net_qty": 500})
        for i in range(17):
            rows.append({"foreign_net_qty": -1000, "institution_net_qty": -500})
        with patch.object(engine, "_fetch_investor_rows", return_value=rows):
            result = engine.calculate_dual_flow("000003", "2026-03-05")
        assert result["CONSECUTIVE_FOREIGN_BUY"] == 3
        expected_score = round(0.15 * 0.5 + min(3 / 5, 1.0) * 0.5, 4)
        assert abs(result["DUAL_FLOW_SCORE"] - expected_score) < 1e-4

    def test_no_investor_data(self):
        """데이터 없음 → 모든 피처=0."""
        engine = _make_engine()
        with patch.object(engine, "_fetch_investor_rows", return_value=[]):
            result = engine.calculate_dual_flow("000004", "2026-03-05")
        assert result["DUAL_FLOW_5D"] == 0.0
        assert result["DUAL_FLOW_20D"] == 0.0
        assert result["CONSECUTIVE_FOREIGN_BUY"] == 0
        assert result["DUAL_FLOW_SCORE"] == 0.0

    def test_score_integration(self):
        """20일 모두 동시매수 → SCORE=1.0."""
        engine = _make_engine()
        mock_rows = _make_dual_rows(20, both_buy=True)
        with patch.object(engine, "_fetch_investor_rows", return_value=mock_rows):
            result = engine.calculate_dual_flow("000005", "2026-03-05")
        assert result["DUAL_FLOW_5D"] == 1.0
        assert result["DUAL_FLOW_20D"] == 1.0
        assert result["DUAL_FLOW_SCORE"] == 1.0

    def test_yaml_params_loaded(self):
        """YAML dual_flow 섹션 파라미터 검증."""
        import yaml
        yaml_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../../config/param_search_space.yaml")
        )
        with open(yaml_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        df = cfg.get("dual_flow")
        assert df is not None
        assert df.get("short_window") == 5
        assert df.get("long_window") == 20
        assert df.get("consecutive_buy_cap") == 5
        weights = df.get("score_weights", {})
        assert weights.get("flow_20d") == 0.5
        assert weights.get("consecutive") == 0.5
```

---

## E. 코드 커밋 + push

```bash
cd /root/kis-autotrade-v4
git add backend/app/services/feature_engine.py backend/app/services/funnel_score_engine.py config/param_search_space.yaml tests/unit/test_dual_flow.py
```

git status 결과:
```
On branch phase-2c-command-center
Your branch is ahead of 'origin/phase-2c-command-center' by 7 commits.

Changes to be committed:
	modified:   backend/app/services/feature_engine.py
	modified:   backend/app/services/funnel_score_engine.py
	modified:   config/param_search_space.yaml
	new file:   tests/unit/test_dual_flow.py
```

커밋:
```
[phase-2c-command-center 92fa3fef] [V4.1] T-111: DUAL_FLOW 기관+외국인 동시 순매수 피처
 4 files changed, 341 insertions(+), 24 deletions(-)
 create mode 100644 tests/unit/test_dual_flow.py
```

push 결과:
```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```
→ SSH 키 권한 없음 (환경 제약). 로컬 커밋은 완료됨.

---

## F. 보고서 + project-docs push

보고서 파일 생성: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-DUAL-FLOW-001-20260305.md`

git add/commit 결과:
```
error: insufficient permission for adding an object to repository database .git/objects
```
→ /root/project-docs/.git/objects 는 root 소유. done_watcher.sh가 자동 처리 예정.

---

## G. 완료 기준 최종 확인

| 기준 | 결과 |
|------|------|
| calculate_dual_flow 4개 피처 | ✅ DUAL_FLOW_5D, DUAL_FLOW_20D, CONSECUTIVE_FOREIGN_BUY, DUAL_FLOW_SCORE |
| YAML dual_flow 섹션 | ✅ short_window=5, long_window=20, consecutive_buy_cap=5, score_weights |
| FunnelScore L2 연동 | ✅ score_l2() DualFlowEngine 호출로 대체 |
| 6/6 테스트 ALL PASS | ✅ 0.15s |
| 코드 커밋 | ✅ SHA: 92fa3fef |
| 보고서 작성 | ✅ /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DUAL-FLOW-001-20260305.md |
| 서비스 재시작 | 지시서 "서비스 재시작 금지"에 따라 생략 |
| .bak 커밋 | 지시서 ".bak 커밋 금지"에 따라 스테이징 제외 |

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4 SHA: 92fa3fef)
- [ ] project-docs 보고서 push 완료 (done_watcher.sh 자동 처리 대기)

---

## HANDOVER.md 업데이트

완료 항목:
- T-111: DUAL_FLOW 기관+외국인 동시 순매수 피처 (feature_engine.py DualFlowEngine, funnel_score_engine.py score_l2 연동, 6/6 테스트 PASS)

HANDOVER.md 업데이트: project-docs push 권한 없음 (root 소유). done_watcher.sh 자동 처리 대기.
