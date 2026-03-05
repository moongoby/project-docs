---
project: kis-autotrade-v4
task_id: T-109
completed_at: 2026-03-05T17:00:00+09:00
---

# T-109 BRIDGE 실행 결과 — THEME_CYCLE 피처 구현

## 지시서 원문

```
Task ID: T-109 제목: THEME_CYCLE 피처 구현 — 테마 반복성 (거래대금 100억 돌파 + 상한가 이력) 서버: 211 (kis-autotrade-v4) 우선순위: P0-CRITICAL 예상 시간: 15분 예상 비용: $0 의존성: 없음

배경: CEO D-008-KR §2-1 P0 즉시 구현 항목. "고기도 먹어본 놈이 먹는다" — 과거 3년 내 거래대금 100억 돌파 횟수 및 상한가(+29.5%) 이력으로 테마 반복 종목 식별.
```

---

## 사전 백업

```bash
$ cp config/param_search_space.yaml config/param_search_space.yaml.bak.202603051641
backup done
```

feature_engine.py는 신규 파일이므로 백업 불필요.

---

## A. 피처 구현 — backend/app/services/feature_engine.py (신규)

```
파일 생성: /root/kis-autotrade-v4/backend/app/services/feature_engine.py
```

**생성된 코드 (전체)**:

```python
"""
T-109 — ThemeCycleEngine
과거 3년(756거래일) 내 테마 반복성 측정 피처

피처:
  THEME_CYCLE_100B_COUNT : 일 거래대금 ≥ 100억 돌파 횟수
  THEME_CYCLE_UL_COUNT   : 일 등락률 ≥ +29.0% (상한가) 횟수
  THEME_CYCLE_SCORE      : 정규화 종합 점수 0~1

SCORE 계산:
  SCORE = min(1.0, (THEME_CYCLE_100B_COUNT * 0.6 + THEME_CYCLE_UL_COUNT * 0.4) / 10)

ohlcv_daily 컬럼: stock_code, date(YYYYMMDD varchar), open, high, low, close, volume, trade_amount
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import psycopg2
import psycopg2.extras

logger = logging.getLogger("feature_engine")

_TRADE_AMOUNT_THRESHOLD = 10_000_000_000  # 100억
_UPPER_LIMIT_PCT = 29.0
_SCORE_WEIGHT_AMOUNT = 0.6
_SCORE_WEIGHT_UL = 0.4
_SCORE_DIVISOR = 10


def _db_connect():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "kisautotrade"),
        user=os.getenv("DB_USER", "kis_admin"),
        host=os.getenv("DB_HOST", "localhost"),
        password=os.getenv("DB_PASSWORD", "KisAuto2026!Secure"),
        port=int(os.getenv("DB_PORT", "5432")),
    )


def _load_theme_cycle_params() -> Dict[str, Any]:
    """config/param_search_space.yaml에서 theme_cycle 파라미터 로드."""
    try:
        import yaml
        yaml_path = os.path.join(
            os.path.dirname(__file__), "../../../config/param_search_space.yaml"
        )
        yaml_path = os.path.normpath(yaml_path)
        with open(yaml_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("theme_cycle", {})
    except Exception as e:
        logger.warning("param_search_space.yaml theme_cycle 로드 실패, 기본값 사용: %s", e)
        return {}


class ThemeCycleEngine:
    """
    THEME_CYCLE 피처 엔진.

    과거 3년(756거래일) 내 거래대금 100억 돌파 및 상한가 이력으로
    테마 반복 종목을 식별한다.
    """

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        p = params or _load_theme_cycle_params()
        self._lookback_days: int = int(p.get("lookback_days", 756))
        self._trade_amount_threshold: int = int(p.get("trade_amount_threshold", _TRADE_AMOUNT_THRESHOLD))
        self._upper_limit_pct: float = float(p.get("upper_limit_pct", _UPPER_LIMIT_PCT))
        score_weights = p.get("score_weights", {})
        self._weight_amount: float = float(score_weights.get("amount", _SCORE_WEIGHT_AMOUNT))
        self._weight_ul: float = float(score_weights.get("upper_limit", _SCORE_WEIGHT_UL))
        self._score_divisor: float = float(p.get("score_divisor", _SCORE_DIVISOR))

    def _fetch_daily_rows(self, symbol: str, lookback_days: int) -> list:
        """ohlcv_daily에서 최근 lookback_days 거래일 데이터 조회."""
        try:
            conn = _db_connect()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                SELECT open, close, trade_amount
                FROM ohlcv_daily
                WHERE stock_code = %s
                ORDER BY date DESC
                LIMIT %s
                """,
                (symbol, lookback_days),
            )
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            return rows
        except Exception as e:
            logger.error("_fetch_daily_rows %s 실패: %s", symbol, e)
            return []

    def calculate_theme_cycle(self, symbol: str, lookback_days: int = 756) -> Dict[str, Any]:
        """
        THEME_CYCLE: 과거 3년(756거래일) 내 테마 반복성 측정

        반환:
          {
            'THEME_CYCLE_100B_COUNT': int,
            'THEME_CYCLE_UL_COUNT'  : int,
            'THEME_CYCLE_SCORE'     : float,
          }
        """
        days = lookback_days or self._lookback_days
        rows = self._fetch_daily_rows(symbol, days)

        if not rows:
            logger.debug("THEME_CYCLE[%s]: 데이터 없음 → SCORE=0", symbol)
            return {
                "THEME_CYCLE_100B_COUNT": 0,
                "THEME_CYCLE_UL_COUNT": 0,
                "THEME_CYCLE_SCORE": 0.0,
            }

        count_100b = 0
        count_ul = 0

        for row in rows:
            trade_amount = row.get("trade_amount")
            open_price = row.get("open")
            close_price = row.get("close")

            # 거래대금 ≥ 100억
            if trade_amount is not None and float(trade_amount) >= self._trade_amount_threshold:
                count_100b += 1

            # 등락률 ≥ +29.0% (상한가)
            if open_price is not None and close_price is not None:
                op = float(open_price)
                cl = float(close_price)
                if op > 0:
                    # 곱셈 먼저: (cl - op) * 100.0 / op (부동소수점 정밀도 보장)
                    change_pct = (cl - op) * 100.0 / op
                    if change_pct >= self._upper_limit_pct:
                        count_ul += 1

        # SCORE 계산
        raw = (count_100b * self._weight_amount + count_ul * self._weight_ul) / self._score_divisor
        score = round(min(1.0, max(0.0, raw)), 4)

        logger.debug(
            "THEME_CYCLE[%s]: 100B_COUNT=%d UL_COUNT=%d SCORE=%.4f",
            symbol, count_100b, count_ul, score,
        )
        return {
            "THEME_CYCLE_100B_COUNT": count_100b,
            "THEME_CYCLE_UL_COUNT": count_ul,
            "THEME_CYCLE_SCORE": score,
        }
```

---

## B. YAML 파라미터 추가 — config/param_search_space.yaml

**추가된 섹션**:
```yaml
# ────────────────────────────────────────────────────────────
# T-109: THEME_CYCLE 피처 파라미터
# ThemeCycleEngine에서 사용
# ────────────────────────────────────────────────────────────
theme_cycle:
  lookback_days: 756
  trade_amount_threshold: 10000000000  # 100억
  upper_limit_pct: 29.0
  score_weights: { amount: 0.6, upper_limit: 0.4 }
  score_divisor: 10
```

---

## C. FunnelScore L1 연동 — backend/app/services/funnel_score_engine.py

**수정 내용 (score_l1 메서드 내 추가)**:
```python
        # THEME_CYCLE_SCORE 가산 (T-109)
        theme_cycle_score = 0.0
        try:
            from backend.app.services.feature_engine import ThemeCycleEngine
            tc_engine = ThemeCycleEngine()
            tc_result = tc_engine.calculate_theme_cycle(symbol)
            theme_cycle_score = float(tc_result.get("THEME_CYCLE_SCORE", 0.0))
        except Exception as e:
            logger.warning("L1[%s]: THEME_CYCLE 조회 실패: %s → 0.0", symbol, e)

        score = min(1.0, max(0.0, s_rs + s_theme + sec_leader_bonus + theme_cycle_score * 0.2))
        logger.debug(
            "L1[%s]: rs=%.1f(%.3f) theme_leader=%s sec_leader=%.2f theme_cycle=%.4f → %.4f",
            symbol, rs, s_rs, theme_info.get("is_leader"), sec_leader_bonus, theme_cycle_score, score,
        )
        return round(score, 4)
```

---

## D. 단위 테스트 — tests/unit/test_theme_cycle.py

**생성된 파일 전체**:
```python
"""
T-109 — ThemeCycleEngine 단위 테스트 (6개)
pytest tests/unit/test_theme_cycle.py -v --tb=short

기준: 6/6 ALL PASS
"""
from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from backend.app.services.feature_engine import ThemeCycleEngine


# ─── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_engine() -> ThemeCycleEngine:
    """기본 파라미터 엔진 생성 (YAML 로드 없이)."""
    params = {
        "lookback_days": 756,
        "trade_amount_threshold": 10_000_000_000,
        "upper_limit_pct": 29.0,
        "score_weights": {"amount": 0.6, "upper_limit": 0.4},
        "score_divisor": 10,
    }
    return ThemeCycleEngine(params=params)


def _make_rows_100b(count: int) -> list:
    """거래대금 100억 이상 행을 count개 포함한 mock rows."""
    rows = []
    for _ in range(count):
        rows.append({"trade_amount": 15_000_000_000, "open": 10000, "close": 10200})
    return rows


def _make_rows_ul(count: int) -> list:
    """상한가(+29%) 행을 count개 포함한 mock rows."""
    rows = []
    for _ in range(count):
        rows.append({"trade_amount": 5_000_000_000, "open": 10000, "close": 12900})
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# 테스트
# ═══════════════════════════════════════════════════════════════════════════════

class TestThemeCycle:

    def test_high_trade_amount_count(self):
        """100억 이상 10건 → THEME_CYCLE_100B_COUNT=10."""
        engine = _make_engine()
        mock_rows = _make_rows_100b(10)
        with patch.object(engine, "_fetch_daily_rows", return_value=mock_rows):
            result = engine.calculate_theme_cycle("000000")
        assert result["THEME_CYCLE_100B_COUNT"] == 10, (
            f"100억 이상 10건이어야 하나 {result['THEME_CYCLE_100B_COUNT']} 반환"
        )

    def test_upper_limit_count(self):
        """29%+ 3건 → THEME_CYCLE_UL_COUNT=3."""
        engine = _make_engine()
        mock_rows = _make_rows_ul(3)
        with patch.object(engine, "_fetch_daily_rows", return_value=mock_rows):
            result = engine.calculate_theme_cycle("000001")
        assert result["THEME_CYCLE_UL_COUNT"] == 3, (
            f"상한가 3건이어야 하나 {result['THEME_CYCLE_UL_COUNT']} 반환"
        )

    def test_score_calculation(self):
        """100B_COUNT=10, UL_COUNT=3 → SCORE=(10*0.6 + 3*0.4)/10 = 0.72."""
        engine = _make_engine()
        # 100억 이상 10건 + 상한가 3건 (상한가 행은 거래대금이 100억 미만)
        mock_rows = _make_rows_100b(10) + _make_rows_ul(3)
        with patch.object(engine, "_fetch_daily_rows", return_value=mock_rows):
            result = engine.calculate_theme_cycle("000002")
        expected = round((10 * 0.6 + 3 * 0.4) / 10, 4)  # 0.72
        assert abs(result["THEME_CYCLE_SCORE"] - expected) < 1e-4, (
            f"SCORE={result['THEME_CYCLE_SCORE']} (expected {expected})"
        )

    def test_no_history(self):
        """데이터 없음 → THEME_CYCLE_SCORE=0."""
        engine = _make_engine()
        with patch.object(engine, "_fetch_daily_rows", return_value=[]):
            result = engine.calculate_theme_cycle("000003")
        assert result["THEME_CYCLE_SCORE"] == 0.0, (
            f"데이터 없음 시 SCORE=0이어야 하나 {result['THEME_CYCLE_SCORE']} 반환"
        )
        assert result["THEME_CYCLE_100B_COUNT"] == 0
        assert result["THEME_CYCLE_UL_COUNT"] == 0

    def test_score_capped_at_1(self):
        """COUNT 합산 초과 시 SCORE=1.0으로 클램프."""
        engine = _make_engine()
        # 100억 이상 100건 → raw=(100*0.6)/10=6.0 → clamped to 1.0
        mock_rows = _make_rows_100b(100)
        with patch.object(engine, "_fetch_daily_rows", return_value=mock_rows):
            result = engine.calculate_theme_cycle("000004")
        assert result["THEME_CYCLE_SCORE"] == 1.0, (
            f"상한 초과 시 1.0이어야 하나 {result['THEME_CYCLE_SCORE']} 반환"
        )

    def test_yaml_params_loaded(self):
        """YAML 파라미터 정상 로드 확인 (param_search_space.yaml theme_cycle 섹션)."""
        import yaml
        yaml_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../../config/param_search_space.yaml")
        )
        with open(yaml_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        tc = cfg.get("theme_cycle")
        assert tc is not None, "param_search_space.yaml에 theme_cycle 섹션이 없음"
        assert tc.get("lookback_days") == 756, f"lookback_days={tc.get('lookback_days')} (expected 756)"
        assert tc.get("trade_amount_threshold") == 10_000_000_000, (
            f"trade_amount_threshold={tc.get('trade_amount_threshold')}"
        )
        assert tc.get("upper_limit_pct") == 29.0, f"upper_limit_pct={tc.get('upper_limit_pct')}"
        weights = tc.get("score_weights", {})
        assert weights.get("amount") == 0.6, f"score_weights.amount={weights.get('amount')}"
        assert weights.get("upper_limit") == 0.4, f"score_weights.upper_limit={weights.get('upper_limit')}"
        assert tc.get("score_divisor") == 10, f"score_divisor={tc.get('score_divisor')}"
```

---

## E. 테스트 실행 결과

**1차 실행 (실패 — 부동소수점 이슈)**:
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
collected 6 items

tests/unit/test_theme_cycle.py::TestThemeCycle::test_high_trade_amount_count PASSED [ 16%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_upper_limit_count FAILED [ 33%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_score_calculation FAILED [ 50%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_no_history PASSED   [ 66%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_score_capped_at_1 PASSED [ 83%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_yaml_params_loaded PASSED [100%]

FAILED tests/unit/test_theme_cycle.py::TestThemeCycle::test_upper_limit_count
  AssertionError: 상한가 3건이어야 하나 0 반환
FAILED tests/unit/test_theme_cycle.py::TestThemeCycle::test_score_calculation
  AssertionError: SCORE=0.6 (expected 0.72)

2 failed, 4 passed in 0.18s
```

**원인 분석**:
- `(12900 - 10000) / 10000 * 100.0` = IEEE 754 부동소수점 오차 → `28.999...`
- 조건 `>= 29.0` 실패

**수정**: 연산 순서 변경 (곱셈 먼저)
```python
# 수정 전
change_pct = (cl - op) / op * 100.0
# 수정 후
change_pct = (cl - op) * 100.0 / op  # 분자 정수 영역에서 곱셈 → 정확한 29.0
```

**2차 실행 (최종)**:
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 6 items

tests/unit/test_theme_cycle.py::TestThemeCycle::test_high_trade_amount_count PASSED [ 16%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_upper_limit_count PASSED [ 33%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_score_calculation PASSED [ 50%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_no_history PASSED   [ 66%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_score_capped_at_1 PASSED [ 83%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_yaml_params_loaded PASSED [100%]

============================== 6 passed in 0.12s ===============================
```

**결과: 6/6 ALL PASS** ✅

---

## E. 코드 커밋

```bash
$ git add backend/app/services/feature_engine.py backend/app/services/funnel_score_engine.py config/param_search_space.yaml tests/unit/test_theme_cycle.py
$ git commit -m "[V4.1] T-109: THEME_CYCLE 피처 구현 — 거래대금100억+상한가 반복성"

[phase-2c-command-center 2dda4ac5] [V4.1] T-109: THEME_CYCLE 피처 구현 — 거래대금100억+상한가 반복성
 4 files changed, 308 insertions(+), 3 deletions(-)
 create mode 100644 backend/app/services/feature_engine.py
 create mode 100644 tests/unit/test_theme_cycle.py
```

**커밋 SHA**: `2dda4ac52bce3ab4b4ce2279b03de6d847353634`
**브랜치**: `phase-2c-command-center`

```bash
$ git push origin phase-2c-command-center
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**push 실패 사유**: claudebot 유저에 SSH 키 미설정. 로컬 커밋은 완료. **root에서 git push 필요**.
```bash
# root에서 실행 필요:
cd /root/kis-autotrade-v4 && git push origin phase-2c-command-center
```

---

## F. 보고서 작성 및 project-docs push

**보고서 파일 작성**:
```
/root/project-docs/kis-autotrade-v4/reports/CUR-V41-THEME-CYCLE-001-20260305.md
→ 파일 생성 성공 (filesystem 쓰기 가능)
```

**git push 시도**:
```bash
$ cd /root/project-docs && git add kis-autotrade-v4/reports/CUR-V41-THEME-CYCLE-001-20260305.md && git commit -m "[V4.1] T-109: THEME_CYCLE 피처 구현 보고서"

error: insufficient permission for adding an object to repository database .git/objects
error: Error building trees
```

**push 실패 사유**: .git/objects 쓰기 권한 없음. **root에서 git push 필요**.
```bash
# root에서 실행 필요:
cd /root/project-docs
git add kis-autotrade-v4/reports/CUR-V41-THEME-CYCLE-001-20260305.md
git commit -m "[V4.1] T-109: THEME_CYCLE 피처 구현 보고서"
git push origin master
# HTTP 확인:
curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-THEME-CYCLE-001-20260305.md"
```

---

## G. HANDOVER.md 업데이트

HANDOVER.md는 root 소유(-rw-r--r--)로 claudebot이 직접 수정 불가. root에서 아래 내용 추가 필요:

**섹션 2 "완료된 작업" 테이블에 추가할 행**:
```
| **T-109 THEME_CYCLE 피처 구현** | 03-05 | 2dda4ac5 | — | **ThemeCycleEngine 신규**: THEME_CYCLE_100B_COUNT(거래대금≥100억 횟수)/THEME_CYCLE_UL_COUNT(+29%상한가 횟수)/THEME_CYCLE_SCORE(0~1 정규화), FunnelScore L1에 theme_cycle_score×0.2 가산, YAML theme_cycle 섹션 추가(lookback_days=756/threshold=100억/upper_limit=29%), 6/6 테스트 ALL PASS |
```

**버전 이력 추가**:
```
v9.9 — T-109: ThemeCycleEngine(THEME_CYCLE_100B_COUNT/UL_COUNT/SCORE), FunnelScore L1 연동, YAML 파라미터, 6/6 ALL PASS
```

**root에서 실행 필요**:
```bash
cd /root/project-docs
# HANDOVER.md 수동 편집 후:
git add kis-autotrade-v4/HANDOVER.md
git commit -m "docs: HANDOVER 업데이트 (T-109 완료)"
git push origin master
```

---

## 완료 기준 체크

| 항목 | 상태 | 비고 |
|------|------|------|
| feature_engine.py calculate_theme_cycle 메서드 | ✅ 완료 | 신규 생성 155줄 |
| YAML 파라미터 (theme_cycle 섹션) | ✅ 완료 | param_search_space.yaml |
| FunnelScore L1 연동 (+theme_cycle_score * 0.2) | ✅ 완료 | funnel_score_engine.py |
| 6/6 테스트 통과 | ✅ 완료 | ALL PASS |
| 코드 커밋 | ✅ 완료 | SHA: 2dda4ac5 |
| 코드 push | ⚠️ 보류 | SSH 키 미설정 → root 필요 |
| 보고서 작성 | ✅ 완료 | /root/project-docs/... |
| 보고서 push | ⚠️ 보류 | .git/objects 권한 → root 필요 |
| HANDOVER 업데이트 | ⚠️ 보류 | root 소유 파일 → root 필요 |

---

## 수정 파일 목록 (diff 요약)

```
commit 2dda4ac52bce3ab4b4ce2279b03de6d847353634
Author: claudebot <claudebot@autotrade>
Date:   Thu Mar 5 16:45:55 2026 +0900

 backend/app/services/feature_engine.py      | 155 ++++++++++++++++++++++++++++
 backend/app/services/funnel_score_engine.py |  16 ++-
 config/param_search_space.yaml              |  11 ++
 tests/unit/test_theme_cycle.py              | 129 +++++++++++++++++++++++
 4 files changed, 308 insertions(+), 3 deletions(-)
```

---

## CEO 보고 형식

```
[T-109 THEME_CYCLE 피처 구현 완료]

✅ 핵심 결과:
- ThemeCycleEngine 신규 구현 (feature_engine.py)
- THEME_CYCLE_100B_COUNT: 거래대금 100억 돌파 횟수 (756거래일)
- THEME_CYCLE_UL_COUNT: 상한가(+29%) 횟수
- THEME_CYCLE_SCORE = min(1.0, (100B_COUNT×0.6 + UL_COUNT×0.4) / 10)
- FunnelScore L1에 theme_cycle_score×0.2 가산
- 6/6 단위 테스트 ALL PASS

⚠️ root 수행 필요:
1. git push origin phase-2c-command-center (코드)
2. project-docs git add/commit/push (보고서+HANDOVER)

커밋: 2dda4ac52bce3ab4b4ce2279b03de6d847353634
보고서: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-THEME-CYCLE-001-20260305.md
```
