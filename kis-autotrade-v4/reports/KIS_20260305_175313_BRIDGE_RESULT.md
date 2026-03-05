---
project: kis-autotrade-v4
task_id: T-115
completed_at: 2026-03-05T18:10:00+09:00
---

# T-115 실행 결과 보고서 — MKT_SEASON 시장 사계절 가중치 엔진

## 1. 지시 파일

**경로:** `/root/.genspark/directives/running/KIS_20260305_175313_BRIDGE.md`

**내용 원문:**
```
Task ID: T-115 제목: MKT_SEASON 시장 사계절 가중치 엔진 서버: 211 (kis-autotrade-v4) 우선순위: P1-HIGH 예상 시간: 12분 의존성: T-101 (v4_macro_daily 완료)

배경: CEO D-008-KR §3-1. 남석관 사계절론 — Q1=탐색, Q2=공격, Q3=경계, Q4=방어. DESK2 진입 시 분기별 공격도 가중치 적용.

사전 작업:
cd /root/kis-autotrade-v4
cp backend/app/services/feature_engine.py backend/app/services/feature_engine.py.bak.$(date +%Y%m%d_%H%M)
cp config/param_search_space.yaml config/param_search_space.yaml.bak.$(date +%Y%m%d_%H%M)
```

---

## 2. 사전 작업 실행 결과

### 백업 생성
```
$ cp backend/app/services/feature_engine.py backend/app/services/feature_engine.py.bak.$(date +%Y%m%d_%H%M)
$ cp config/param_search_space.yaml config/param_search_space.yaml.bak.$(date +%Y%m%d_%H%M)
백업 완료
```

백업 파일:
- `backend/app/services/feature_engine.py.bak.20260305_18XX`
- `config/param_search_space.yaml.bak.20260305_18XX`

---

## 3. config/param_search_space.yaml — mkt_season 섹션 추가

**추가된 내용 (파일 끝 부분):**
```yaml
# ────────────────────────────────────────────────────────────
# T-115: MKT_SEASON 시장 사계절 가중치 파라미터
# 남석관 사계절론 — Q1=탐색, Q2=공격, Q3=경계, Q4=방어
# MktSeasonEngine에서 사용
# ────────────────────────────────────────────────────────────
mkt_season:
  weights:
    Q1: 0.9    # 1~3월 탐색기 (감산)
    Q2: 1.2    # 4~6월 공격기 (가산)
    Q3: 0.8    # 7~9월 경계기 (감산)
    Q4: 0.7    # 10~12월 방어기 (감산)
  bear_override: 0.5  # 매크로 BEAR 레짐 시 전분기 0.5
  bull_override: 1.3  # 매크로 BULL 레짐 시 전분기 1.3
  source_table: v4_macro_daily
  regime_column: macro_regime
```

**확인:**
```
$ grep -n "mkt_season" /root/kis-autotrade-v4/config/param_search_space.yaml
545:mkt_season:
```

---

## 4. backend/app/services/feature_engine.py — MktSeasonEngine 클래스 추가

### 추가된 함수/클래스

#### `_load_mkt_season_params()`
```python
def _load_mkt_season_params() -> Dict[str, Any]:
    """config/param_search_space.yaml에서 mkt_season 파라미터 로드."""
    try:
        import yaml
        yaml_path = os.path.join(
            os.path.dirname(__file__), "../../../config/param_search_space.yaml"
        )
        yaml_path = os.path.normpath(yaml_path)
        with open(yaml_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("mkt_season", {})
    except Exception as e:
        logger.warning("param_search_space.yaml mkt_season 로드 실패, 기본값 사용: %s", e)
        return {}
```

#### `class MktSeasonEngine`
```python
class MktSeasonEngine:
    """
    MKT_SEASON 시장 사계절 가중치 엔진 (T-115).

    남석관 사계절론:
      Q1 (1~3월): 탐색기  — 기본 가중치 0.9
      Q2 (4~6월): 공격기  — 기본 가중치 1.2
      Q3 (7~9월): 경계기  — 기본 가중치 0.8
      Q4 (10~12월): 방어기 — 기본 가중치 0.7

    매크로 레짐 오버라이드:
      BEAR → 전분기 bear_override (기본 0.5)
      BULL → 전분기 bull_override (기본 1.3)
    """

    _QUARTER_MAP = {1: "Q1", 2: "Q1", 3: "Q1",
                    4: "Q2", 5: "Q2", 6: "Q2",
                    7: "Q3", 8: "Q3", 9: "Q3",
                    10: "Q4", 11: "Q4", 12: "Q4"}

    _DEFAULT_WEIGHTS = {"Q1": 0.9, "Q2": 1.2, "Q3": 0.8, "Q4": 0.7}

    def __init__(self, params: Optional[Dict[str, Any]] = None): ...
    def get_current_season(self, date) -> str: ...      # Q1/Q2/Q3/Q4
    def get_season_weight(self, date, macro_regime=None) -> float: ...   # bear/bull override 포함
    def adjust_score(self, base_score, date, macro_regime=None) -> float: ...  # base_score × weight
```

---

## 5. backend/app/services/funnel_score_engine.py — score_l0() MktSeasonEngine 통합

**변경된 코드 (score_l0 메서드 내):**
```python
        # ── 가중평균 ──
        raw = s_regime * 0.5 + s_vix * 0.3 + ma_bonus * 0.5
        score = min(1.0, max(0.0, raw))

        # ── T-115: MKT_SEASON 사계절 가중치 적용 ──
        try:
            from backend.app.services.feature_engine import MktSeasonEngine
            season_engine = MktSeasonEngine()
            score = season_engine.adjust_score(score, date, macro_regime=regime)
            season = season_engine.get_current_season(date)
            weight = season_engine.get_season_weight(date, macro_regime=regime)
            logger.info(
                "[MKT_SEASON] date=%s, season=%s, weight=%.2f, regime=%s",
                date, season, weight, regime,
            )
        except Exception as e:
            logger.warning("L0[%s]: MktSeasonEngine 적용 실패: %s → 원본 점수 유지", date, e)

        logger.debug(
            "L0[%s]: regime=%s(%.2f) vix=%s(%.2f) ma_bonus=%.2f → %.4f",
            date, regime, s_regime, vix if vix is not None else "N/A", s_vix, ma_bonus, score,
        )
        return round(score, 4)
```

**로깅 확인:** `[MKT_SEASON] date={date}, season={season}, weight={weight}, regime={regime}` 형식으로 logger.info 출력

---

## 6. 단위 테스트 — tests/unit/test_mkt_season.py

**파일 생성:** `/root/kis-autotrade-v4/tests/unit/test_mkt_season.py`

**8개 테스트 목록:**
1. `test_q1_weight` — 1~3월 → Q1 가중치 0.9
2. `test_q2_weight` — 4~6월 → Q2 가중치 1.2
3. `test_q3_weight` — 7~9월 → Q3 가중치 0.8
4. `test_q4_weight` — 10~12월 → Q4 가중치 0.7
5. `test_bear_override` — BEAR 레짐 → bear_override 0.5 (전분기 적용)
6. `test_bull_override` — BULL 레짐 → bull_override 1.3 (전분기 적용)
7. `test_score_adjustment` — adjust_score 기본 동작 (곱셈, 클램프 0~1)
8. `test_yaml_load` — YAML mkt_season 섹션 정상 로드 및 값 검증

---

## 7. pytest 실행 결과

```
$ /root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/test_mkt_season.py -v

============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 8 items

tests/unit/test_mkt_season.py::test_q1_weight PASSED                     [ 12%]
tests/unit/test_mkt_season.py::test_q2_weight PASSED                     [ 25%]
tests/unit/test_mkt_season.py::test_q3_weight PASSED                     [ 37%]
tests/unit/test_mkt_season.py::test_q4_weight PASSED                     [ 50%]
tests/unit/test_mkt_season.py::test_bear_override PASSED                 [ 62%]
tests/unit/test_mkt_season.py::test_bull_override PASSED                 [ 75%]
tests/unit/test_mkt_season.py::test_score_adjustment PASSED              [ 87%]
tests/unit/test_mkt_season.py::test_yaml_load PASSED                     [100%]

============================== 8 passed in 0.18s ===============================
```

**결과: 8/8 ALL PASS ✅**

---

## 8. Git 커밋 결과

```
$ git add backend/app/services/feature_engine.py config/param_search_space.yaml backend/app/services/funnel_score_engine.py tests/unit/test_mkt_season.py

$ git commit -m "[V4.1] T-115: MKT_SEASON 시장 사계절 가중치 — 남석관 사계절론 L0 통합"
[phase-2c-command-center 5f4d590c] [V4.1] T-115: MKT_SEASON 시장 사계절 가중치 — 남석관 사계절론 L0 통합
 4 files changed, 292 insertions(+)
 create mode 100644 tests/unit/test_mkt_season.py
```

**커밋 해시:** `5f4d590c`

### Git Push 결과 (❌ SSH 권한 문제)
```
$ git push origin phase-2c-command-center

git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
Please make sure you have the correct access rights and the repository exists.
```

**원인:** claudebot 계정에 SSH key 미설정 → push 불가
**상태:** 로컬 커밋 완료, 원격 push 미완료
**조치 필요:** root 계정에서 `git push origin phase-2c-command-center` 실행 필요

---

## 9. 완료 기준 체크

| 기준 | 상태 |
|------|------|
| YAML mkt_season 섹션 생성 (Q1/Q2/Q3/Q4, bear/bull override) | ✅ 완료 |
| `_load_mkt_season_params()` 함수 구현 | ✅ 완료 |
| `MktSeasonEngine` 클래스 구현 (get_current_season, get_season_weight, adjust_score) | ✅ 완료 |
| FunnelScore `score_l0()` L0 MktSeasonEngine 통합 | ✅ 완료 |
| 로깅: `[MKT_SEASON] date=, season=, weight=, regime=` | ✅ 완료 |
| 단위 테스트 8개 작성 | ✅ 완료 |
| 8/8 테스트 PASS | ✅ 완료 |
| 로컬 git 커밋 | ✅ 완료 (5f4d590c) |
| git push | ❌ SSH 권한 오류 — root에서 재시도 필요 |
| .bak 파일 커밋 제외 | ✅ 미커밋 |
| 서비스 재시작 (금지) | ✅ 미실행 |

---

## 10. 구현 상세 — MktSeasonEngine 설계 노트

### 분기 매핑
- Q1: 1월, 2월, 3월 (탐색기) → 0.9
- Q2: 4월, 5월, 6월 (공격기) → 1.2
- Q3: 7월, 8월, 9월 (경계기) → 0.8
- Q4: 10월, 11월, 12월 (방어기) → 0.7

### 오버라이드 우선순위
1. BEAR 레짐 → 무조건 0.5 (가장 보수적)
2. BULL 레짐 → 무조건 1.3 (가장 공격적)
3. NEUTRAL → 해당 분기 가중치

### adjust_score 클램프
- `base_score × weight` 결과를 `[0.0, 1.0]` 범위로 클램프
- 예: base=0.9, BULL(1.3) → 1.17 → 클램프 → 1.0

### FunnelScore L0 통합 방식
- 기존 score_l0() 계산 후 → MktSeasonEngine.adjust_score() 적용
- 실패 시 원본 score 유지 (graceful fallback)

---

## 11. 파일 변경 목록

| 파일 | 변경 종류 | 내용 |
|------|-----------|------|
| `config/param_search_space.yaml` | 수정 | mkt_season 섹션 추가 |
| `backend/app/services/feature_engine.py` | 수정 | `_load_mkt_season_params`, `MktSeasonEngine` 추가 |
| `backend/app/services/funnel_score_engine.py` | 수정 | `score_l0()` MktSeasonEngine 통합 |
| `tests/unit/test_mkt_season.py` | 신규 생성 | 8개 단위 테스트 |
