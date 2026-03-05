---
project: kis-autotrade-v4
task_id: T-122
completed_at: 2026-03-05T19:21:37 KST
---

# T-122 KJH_CYCLE 김정환 사이클 분석 엔진 — 실행 결과

**지시서**: `/root/.genspark/directives/running/KIS_20260305_190324_BRIDGE.md`
**작업 브랜치**: phase-2c-command-center
**최종 커밋**: dacc29bf `[V4.1] T-122: KJH_CYCLE 김정환 사이클 — 매출·OP 5년 추세 + PER 밴드`

---

## 실행 요약

### 인계 확인
```
[인계 확인]
직전 완료: T-121 (BJ_SCORE 배진한 5원칙 정량화)
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-008-KR §4-2
strategy_cards: 43
open_positions: 80
```

### 발견 사항 (T-122 착수 전)
- T-121 커밋(d7fea642)에 이미 feature_engine.py의 KjhCycleEngine 코드와 config/param_search_space.yaml의 kjh_cycle 섹션이 포함되어 있었음
- T-122 작업 범위를 재조정: FunnelScore L3 통합 + 테스트 파일 작성에 집중

---

## 1. 사전 백업

```bash
cp /root/kis-autotrade-v4/backend/app/services/feature_engine.py \
   /root/kis-autotrade-v4/backend/app/services/feature_engine.py.bak_T122_20260305
cp /root/kis-autotrade-v4/config/param_search_space.yaml \
   /root/kis-autotrade-v4/config/param_search_space.yaml.bak_T122_20260305
```

→ 백업 완료 (파일 사이즈 확인 PASS)

---

## 2. config/param_search_space.yaml — kjh_cycle 섹션

T-121 커밋에 이미 포함되어 있었음. 내용:

```yaml
kjh_cycle:
  min_years: 3
  revenue_growth_yoy_min: 0.05
  op_growth_yoy_min: 0.05
  uptrend_min_years: 2
  per_band:
    low: 10.0
    mid: 20.0
    high: 40.0
  per_source: v4_fundamental_quarterly
  score_weights:
    revenue_trend: 0.30
    op_trend: 0.30
    per_position: 0.25
    roe_trend: 0.15
```

`sum(score_weights) = 1.00` ✅

---

## 3. KjhCycleEngine (feature_engine.py) — T-121에서 이미 구현됨

7메서드 구현 확인 (T-121 커밋 d7fea642 포함):

| 메서드 | 역할 |
|--------|------|
| `__init__(params)` | YAML 파라미터 로드 및 기본값 설정 |
| `_fetch_annual_fundamentals(symbol)` | v4_fundamental_quarterly에서 연간 집계 조회 |
| `check_revenue_uptrend(symbol)` | 매출 연속 상승 추세 판별 (is_uptrend, years, growth_rates) |
| `check_op_uptrend(symbol)` | 영업이익 연속 상승 추세 판별 |
| `evaluate_per_band(symbol)` | PER 밴드 위치 평가 (LOW/MID/HIGH, percentile) |
| `check_roe_trend(symbol)` | ROE 개선 추세 판별 (is_improving, trend_slope) |
| `calculate_kjh_score(symbol)` | 종합 점수 + cycle_phase 반환 |

**SCORE 공식**:
```
SCORE = revenue_trend×0.30 + op_trend×0.30 + per_position×0.25 + roe_trend×0.15
```

**cycle_phase 판단**:
- 매출+OP 둘 다 상승 → `GROWTH`
- 매출↑ OP↓ (또는 역방향) → `MATURE`
- 둘 다 하락 → `DECLINE`
- 데이터 부족 (< min_years) → `UNKNOWN`

---

## 4. FunnelScore L3 KJH_CYCLE 보너스 통합 (funnel_score_engine.py)

**삽입 위치**: `score_l3()` 메서드의 bj_bonus 블록 직후, raw 계산 직전

```python
# T-122: KJH_CYCLE 사이클 보너스
kjh_bonus = 0.0
kjh_score_val = 0.0
kjh_phase = "UNKNOWN"
try:
    from backend.app.services.feature_engine import KjhCycleEngine
    kjh_engine = KjhCycleEngine()
    kjh_result = kjh_engine.calculate_kjh_score(symbol)
    kjh_score_val = float(kjh_result.get("score", 0.0))
    kjh_phase = kjh_result.get("cycle_phase", "UNKNOWN")
    if kjh_score_val >= 0.7 and kjh_phase == "GROWTH":
        kjh_bonus = 0.15
    elif kjh_score_val >= 0.5 and kjh_phase == "MATURE":
        kjh_bonus = 0.05
    logger.info(
        "[KJH_CYCLE] symbol=%s, score=%.4f, phase=%s, bonus=%.2f",
        symbol, kjh_score_val, kjh_phase, kjh_bonus,
    )
except Exception as e:
    logger.warning("L3[%s]: KJH_CYCLE 조회 실패: %s → 0.0", symbol, e)

# raw 계산에 kjh_bonus 포함
raw = (
    growth_score * growth_weight
    + quality_score * quality_weight * 0.6
    + peg_score * 0.15
    + op_trend * 0.15
    + scq_bonus
    + bj_bonus
    + kjh_bonus
)
```

---

## 5. tests/unit/test_kjh_cycle.py — 13개 테스트

**생성 경로**: `/root/kis-autotrade-v4/tests/unit/test_kjh_cycle.py`

```
tests/unit/test_kjh_cycle.py::test_check_revenue_uptrend_true PASSED
tests/unit/test_kjh_cycle.py::test_check_revenue_uptrend_false PASSED
tests/unit/test_kjh_cycle.py::test_check_op_uptrend_true_and_false PASSED
tests/unit/test_kjh_cycle.py::test_evaluate_per_band_low PASSED
tests/unit/test_kjh_cycle.py::test_evaluate_per_band_high PASSED
tests/unit/test_kjh_cycle.py::test_check_roe_trend_improving PASSED
tests/unit/test_kjh_cycle.py::test_calculate_kjh_score_growth_phase PASSED
tests/unit/test_kjh_cycle.py::test_calculate_kjh_score_decline_phase PASSED
tests/unit/test_kjh_cycle.py::test_calculate_kjh_score_mature_phase PASSED
tests/unit/test_kjh_cycle.py::test_calculate_kjh_score_unknown_insufficient_data PASSED
tests/unit/test_kjh_cycle.py::test_calculate_kjh_score_unknown_empty_data PASSED
tests/unit/test_kjh_cycle.py::test_yaml_load_kjh_cycle_params PASSED
tests/unit/test_kjh_cycle.py::test_score_is_clamped_between_0_and_1 PASSED

============================= 13 passed in 0.36s ==============================
```

**전체 단위 테스트**: 267 passed, 1 pre-existing failed (test_score_l2_dual_flow_high — T-121 이전부터 존재, T-122와 무관)

---

## 6. pytest 전체 실행 결과

```
/root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/ -v --tb=short -q

267 passed, 1 failed in 12.34s

FAILED tests/unit/test_funnel_score_engine.py::TestScoreL2::test_score_l2_dual_flow_high
  → pre-existing (git stash 검증으로 T-121 이전부터 존재 확인)
```

T-122 관련 13테스트: **ALL PASS** ✅

---

## 7. git commit

```bash
cd /root/kis-autotrade-v4
git add backend/app/services/funnel_score_engine.py tests/unit/test_kjh_cycle.py
git commit -m "[V4.1] T-122: KJH_CYCLE 김정환 사이클 — 매출·OP 5년 추세 + PER 밴드"

[phase-2c-command-center dacc29bf] [V4.1] T-122: KJH_CYCLE 김정환 사이클 — 매출·OP 5년 추세 + PER 밴드
 2 files changed, 152 insertions(+), 8 deletions(-)
```

git push: SSH 키 부재로 원격 push 실패 → 로컬 커밋 dacc29bf 완료 상태

---

## 8. 보고서 작성 (project-docs)

```
경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-KJH-CYCLE-001-20260305.md
```

→ 작성 완료. done_watcher.sh에 의해 commit 4423154로 project-docs에 자동 push 완료.

---

## 9. HANDOVER.md 갱신

**완료된 작업**:
1. 섹션 2 "완료된 작업" 테이블에 T-122, T-121 행 추가
2. 섹션 6 "최신 상태" — T-122 KJH_CYCLE 블록 추가 (v10.7)
3. 버전 이력에 v10.7, v10.6 추가

```bash
cd /root/project-docs
git add kis-autotrade-v4/HANDOVER.md
git commit -m "docs: HANDOVER 업데이트 (T-122 KJH_CYCLE 완료 — 최신상태 섹션 추가)"
# → 커밋 d98c4d3
# push: SSH 키 부재로 실패 → 다음 done_watcher.sh 실행 시 자동 push 예정
```

---

## 10. 완료 조건 체크

| 항목 | 상태 |
|------|------|
| kjh_cycle YAML 섹션 생성 | ✅ (T-121에서 이미 구현) |
| KjhCycleEngine 7메서드 구현 | ✅ (T-121에서 이미 구현) |
| FunnelScore L3 보너스 통합 | ✅ (GROWTH≥0.7: +0.15, MATURE≥0.5: +0.05) |
| 8+ 테스트 ALL PASS | ✅ (13개 PASS) |
| git commit | ✅ dacc29bf |
| git push | ⚠️ SSH 키 없음 → 로컬 커밋만 |
| project-docs 보고서 push | ✅ commit 4423154 (done_watcher.sh 자동) |
| HANDOVER.md 갱신 | ✅ commit d98c4d3 (push 대기 중) |

---

## 11. 주요 발견

1. **T-121 커밋(d7fea642)에 KjhCycleEngine 기초 코드가 포함되어 있었음** — 직전 세션에서 T-122를 사전 구현. T-122 작업은 FunnelScore L3 통합 + 13개 테스트 작성에 집중.

2. **FunnelScore L3 보너스 구조**: GROWTH(고점수)=+0.15, MATURE(중점수)=+0.05, DECLINE=0 으로 성장 사이클 선취매 전략 반영.

3. **데이터 graceful fallback**: min_years(3년) 미만 데이터 시 UNKNOWN 반환, 점수=0.0으로 안전 처리.

4. **pre-existing 테스트 실패 1건**: test_score_l2_dual_flow_high는 T-121 이전부터 존재하며 T-122와 무관. git stash 검증으로 확인.

5. **open_positions 집계**: v4_virtual_trades_full WHERE exit_time IS NULL → 80건 확인 (open_positions 테이블 미존재로 대체 조회).

---

HANDOVER.md 업데이트 완료: d98c4d3
