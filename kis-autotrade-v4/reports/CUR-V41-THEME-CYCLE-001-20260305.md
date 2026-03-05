# T-109 THEME_CYCLE 피처 구현 결과

[인계 확인]
직전 완료: T-108
현재 단계: Phase 2C
CEO 지시 적용: D-008-KR §2-1

---

## 개요
- Task ID: T-109
- 제목: THEME_CYCLE 피처 구현 — 테마 반복성 (거래대금 100억 돌파 + 상한가 이력)
- 일시: 2026-03-05 KST
- 서버: 211 (kis-autotrade-v4)
- 브랜치: phase-2c-command-center

---

## 구현 완료 항목

### A. 피처 구현
**파일**: `backend/app/services/feature_engine.py` (신규 생성)

```python
class ThemeCycleEngine:
    def calculate_theme_cycle(self, symbol: str, lookback_days: int = 756) -> dict:
        """
        THEME_CYCLE: 과거 3년(756거래일) 내 테마 반복성 측정
        - THEME_CYCLE_100B_COUNT: 일 거래대금 ≥ 100억 돌파 횟수
        - THEME_CYCLE_UL_COUNT: 일 등락률 ≥ +29.0% (상한가) 횟수
        - THEME_CYCLE_SCORE: 정규화 종합 점수 0~1
        """
```

- ohlcv_daily 테이블에서 756거래일치 조회
- `trade_amount >= 10,000,000,000` → THEME_CYCLE_100B_COUNT
- `(close - open) * 100.0 / open >= 29.0` → THEME_CYCLE_UL_COUNT (부동소수점 안정성 위해 곱셈 우선)
- `SCORE = min(1.0, (100B_COUNT * 0.6 + UL_COUNT * 0.4) / 10)`

### B. YAML 파라미터
**파일**: `config/param_search_space.yaml`

```yaml
theme_cycle:
  lookback_days: 756
  trade_amount_threshold: 10000000000  # 100억
  upper_limit_pct: 29.0
  score_weights: { amount: 0.6, upper_limit: 0.4 }
  score_divisor: 10
```

### C. FunnelScore L1 연동
**파일**: `backend/app/services/funnel_score_engine.py`

`score_l1()` 내부에 THEME_CYCLE_SCORE 가산 로직 추가:
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
```

### D. 단위 테스트
**파일**: `tests/unit/test_theme_cycle.py`

---

## 테스트 결과

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
collected 6 items

tests/unit/test_theme_cycle.py::TestThemeCycle::test_high_trade_amount_count PASSED [ 16%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_upper_limit_count PASSED [ 33%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_score_calculation PASSED [ 50%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_no_history PASSED   [ 66%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_score_capped_at_1 PASSED [ 83%]
tests/unit/test_theme_cycle.py::TestThemeCycle::test_yaml_params_loaded PASSED [100%]

============================== 6 passed in 0.12s ===============================
```

**결과: 6/6 ALL PASS**

---

## 수정 파일 목록

| 파일 | 변경 유형 | 내용 |
|------|----------|------|
| `backend/app/services/feature_engine.py` | 신규 생성 | ThemeCycleEngine 클래스 구현 (155줄) |
| `backend/app/services/funnel_score_engine.py` | 수정 | score_l1()에 THEME_CYCLE_SCORE 가산 (+16줄) |
| `config/param_search_space.yaml` | 수정 | theme_cycle 파라미터 섹션 추가 (+11줄) |
| `tests/unit/test_theme_cycle.py` | 신규 생성 | 6개 단위 테스트 (129줄) |

---

## Git 커밋

```
commit 2dda4ac52bce3ab4b4ce2279b03de6d847353634
Author: claudebot <claudebot@autotrade>
Date:   Thu Mar 5 16:45:55 2026 +0900

    [V4.1] T-109: THEME_CYCLE 피처 구현 — 거래대금100억+상한가 반복성

 backend/app/services/feature_engine.py      | 155 ++++++++++++++++++++++++
 backend/app/services/funnel_score_engine.py |  16 ++-
 config/param_search_space.yaml              |  11 ++
 tests/unit/test_theme_cycle.py              | 129 +++++++++++++++++++++++
 4 files changed, 308 insertions(+), 3 deletions(-)
```

**브랜치**: phase-2c-command-center
**push**: SSH 키 미설정(claudebot)으로 인해 로컬 커밋 완료, root에서 push 필요

---

## 완료 체크포인트

- [x] feature_engine.py에 calculate_theme_cycle 메서드 구현
- [x] YAML 파라미터(theme_cycle 섹션) 추가
- [x] FunnelScore L1 연동 (+theme_cycle_score * 0.2)
- [x] 6/6 테스트 통과
- [x] 코드 커밋 (로컬, SHA: 2dda4ac5)
- [ ] 코드 push (SSH 키 필요, root에서 수행)
- [x] 보고서 작성 완료

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-THEME-CYCLE-001-20260305.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-THEME-CYCLE-001-20260305.md
- 코드 커밋: 2dda4ac52bce3ab4b4ce2279b03de6d847353634
- 보고서 push: 아래 결과 참조
