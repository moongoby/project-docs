---
project: kis-autotrade-v4
task_id: T-230
completed_at: 2026-03-07T00:54:40+09:00 KST
---

# KIS_20260307_003442_BRIDGE 실행 결과

## 지시서 원문

```
Task ID: T-230 제목: CEO P0 변수 전수 감사 + 파이프라인 연결 확인 서버: 211 (kis-autotrade-v4) 우선순위: P1-HIGH 예상 시간: 30분 의존성: T-237

수행 내용:

9개 P0 변수 감사표:
✅ DUAL_FLOW (T-218/faa85636)
✅ THEME_CYCLE (T-219/7f27b7b4)
✅ SMALL_CAP_QUALITY (T-235/20017658)
✅ SEC_LEADER_FLAG v2 (T-235/20017658)
❓ MKT_SEASON / FORCE_ACC / BJ_SCORE / KJH_CYCLE / D_D1_D2_ENTRY
구현 4개의 cte_pipeline 실연결 확인 (T-237에서 연결 여부)
미구현 5개 우선순위 매트릭스 (데이터 가용/FunnelScore 영향/난이도)
테스트 4건

성공 기준: 감사표 9개 + 연결 확인 + 매트릭스 보고서: CUR-V41-CEO-P0-VARIABLES-AUDIT-001-20260309.md 완료 후: HANDOVER 갱신 + git push
```

---

## 1. 인계 확인 결과

```
직전 완료: T-235 (SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2 구현, 2026-03-09)
현재 단계: Phase 2C (CTE 파이프라인 통합)
CEO 지시 적용: D-008-KR P0~P2
strategy_cards: 60
open_positions: 0
```

파일 확인:
- /root/project-docs/kis-autotrade-v4/HANDOVER.md: 읽기 완료 (v10.40)
- /root/project-docs/kis-autotrade-v4/CEO-DIRECTIVES.md: 읽기 완료 (v1.6)

---

## 2. 9개 P0 변수 전수 감사 결과

### 감사 실행 내역

**읽은 파일:**
- /root/kis-autotrade-v4/backend/app/services/feature_engine.py (grep 탐색)
- /root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py (전체 읽기)
- /root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py (전체 읽기)
- /root/kis-autotrade-v4/config/funnel_score.yaml

**확인 방법:**
```bash
grep -r "MKT_SEASON|FORCE_ACC|BJ_SCORE|KJH_CYCLE|D_D1_D2|..." \
  /root/kis-autotrade-v4/backend/app/services/ --include="*.py"
```

### 감사 결과 테이블

| 변수 | 지시서 상태 | 실제 상태 | 구현 클래스 | 태스크 | 파이프라인 연결 |
|------|------------|---------|------------|--------|----------------|
| DUAL_FLOW | ✅ P0 확인 | ✅ 구현+연결 | DualFlowEngine, compute_dual_flow_5d/20d | T-111/T-218 | L2 주점수 (×0.7) |
| THEME_CYCLE | ✅ P0 확인 | ✅ 구현+연결 | ThemeCycleEngine, compute_theme_cycle_* | T-109/T-219 | L1 +0.2 |
| SMALL_CAP_QUALITY | ✅ P0 확인 | ✅ 구현+연결 | compute_small_cap_quality, SmallCapQualityFilter | T-110/T-235 | L3 +0.2 bonus |
| SEC_LEADER_FLAG v2 | ✅ P0 확인 | ✅ 구현+연결 | SecLeaderV2Engine, flag_sector_leaders_v2 | T-112/T-235 | L1 +0.3 bonus |
| MKT_SEASON | ❓ 미확인 | ✅ 구현+연결 (2026-03-05) | MktSeasonEngine | T-115 | L0 계절 조정 |
| FORCE_ACC | ❓ 미확인 | ✅ 구현+연결 (2026-03-05) | ForceAccEngine | T-116 | L2 +0.15 bonus |
| D_D1_D2_ENTRY | ❓ 미확인 | ✅ 구현+연결 (2026-03-05) | DDayEntryEngine | T-117 | L2.5 CTE 직접 |
| BJ_SCORE | ❓ 미확인 | ✅ 구현+연결 (2026-03-05) | BjScoreEngine | T-121 | L3 +0.10~+0.20 |
| KJH_CYCLE | ❓ 미확인 | ✅ 구현+연결 (2026-03-05) | KjhCycleEngine | T-122 | L3 +0.05~+0.15 |

**결론**: 9개 전원 구현 완료 + 파이프라인 연결 완료. "❓ 5개 미구현"은 T-115~T-122 (2026-03-05) 작업으로 이미 모두 해소됨.

---

## 3. CTE 파이프라인 연결 확인 (T-237 이후)

### 연결 구조 확인 (코드 직접 확인)

#### L0: MKT_SEASON (funnel_score_engine.py:194-206)
```python
from backend.app.services.feature_engine import MktSeasonEngine
season_engine = MktSeasonEngine()
score = season_engine.adjust_score(score, date, macro_regime=regime)
season = season_engine.get_current_season(date)
weight = season_engine.get_season_weight(date, macro_regime=regime)
# Q1=0.9, Q2=1.2, Q3=0.8, Q4=0.7
# BEAR×0.5, BULL×1.3
```
→ **연결 확인** ✅

#### L1: SEC_LEADER_FLAG v2 (funnel_score_engine.py:322-332)
```python
from backend.app.services.feature_engine import SecLeaderV2Engine
_sl_engine = SecLeaderV2Engine()
_sl_result = _sl_engine.calculate_sec_leader_v2(symbol, date)
if _sl_result.get("is_leader_v2"):
    sec_leader_bonus = leader_bonus  # +0.3
```
→ **연결 확인** ✅

#### L1: THEME_CYCLE (funnel_score_engine.py:334-343)
```python
from backend.app.services.feature_engine import ThemeCycleEngine
tc_engine = ThemeCycleEngine()
tc_result = tc_engine.calculate_theme_cycle(symbol)
theme_cycle_score = float(tc_result.get("THEME_CYCLE_SCORE", 0.0))
score = min(1.0, max(0.0, s_rs + s_theme + sec_leader_bonus + theme_cycle_score * 0.2))
```
→ **연결 확인** ✅

#### L2: DUAL_FLOW (funnel_score_engine.py:422-434)
```python
from backend.app.services.feature_engine import DualFlowEngine
df_engine = DualFlowEngine()
df_result = df_engine.calculate_dual_flow(symbol, date)
dual_flow_score = float(df_result.get("DUAL_FLOW_SCORE", 0.0))
raw = dual_flow_score * 0.7 + s_close
```
→ **연결 확인** ✅

#### L2: FORCE_ACC (funnel_score_engine.py:449-457)
```python
from backend.app.services.feature_engine import ForceAccEngine
fa_engine = ForceAccEngine()
fa_result = fa_engine.calculate_force_acc(symbol, date)
force_acc_bonus = float(fa_result.get("force_acc_score", 0.0)) * 0.15
score = min(1.0, max(0.0, raw + force_acc_bonus))
```
→ **연결 확인** ✅

#### L3: SMALL_CAP_QUALITY (funnel_score_engine.py:581-597)
```python
from backend.app.services.feature_engine import compute_small_cap_quality
_scq_v2 = compute_small_cap_quality(rows)
quality_score_v2 = float(_scq_v2.get("quality_score", 0.0))
# T-110: SmallCapQualityFilter 전체 통과 시 scq_bonus = +0.2
```
→ **연결 확인** ✅

#### L3: BJ_SCORE (funnel_score_engine.py:616-636)
```python
from backend.app.services.feature_engine import BjScoreEngine
bj_engine = BjScoreEngine()
bj_result = bj_engine.calculate_bj_score(symbol, date)
bj_total = bj_result.get("total", 0)
if bj_total >= 80:
    bj_bonus = 0.20
elif bj_total >= 60:
    bj_bonus = 0.10
```
→ **연결 확인** ✅

#### L3: KJH_CYCLE (funnel_score_engine.py:638-657)
```python
from backend.app.services.feature_engine import KjhCycleEngine
kjh_engine = KjhCycleEngine()
kjh_result = kjh_engine.calculate_kjh_score(symbol)
kjh_score_val = float(kjh_result.get("score", 0.0))
kjh_phase = kjh_result.get("cycle_phase", "UNKNOWN")
if kjh_score_val >= 0.7 and kjh_phase == "GROWTH":
    kjh_bonus = 0.15
elif kjh_score_val >= 0.5 and kjh_phase == "MATURE":
    kjh_bonus = 0.05
```
→ **연결 확인** ✅

#### L2.5 CTE 직접: D_D1_D2_ENTRY (cte_pipeline.py:474-481)
```python
if signal.is_dday_candidate and signal.dday_signal_result is not None:
    _dday = signal.dday_signal_result
    result.is_dday_candidate = True
    result.dday_action   = _dday.get("action", "SKIP")  # ENTRY/WAIT/REJECT
    result.dday_day_type = _dday.get("day_type", "")    # D/D+1/D+2
    result.details["dday"] = {...}
```
→ **연결 확인** ✅

---

## 4. 미구현 5개 우선순위 매트릭스

> 실제 감사 결과: 5개 전부 구현 완료. 아래는 **실질적 데이터 기여도 및 개선 우선순위** 매트릭스.

### 데이터 가용성 / FunnelScore 영향 / 실효성 매트릭스

| 변수 | 데이터 가용성 | FunnelScore 영향도 | 실효성 | 개선 우선순위 |
|------|-------------|-------------------|---------|-----------:|
| MKT_SEASON | ★★★ HIGH (날짜 기반) | ★★ MEDIUM (±30%) | ★★★ HIGH | **P1** |
| D_D1_D2_ENTRY | ★★★ HIGH (ohlcv_daily) | ★★ INDIRECT (CTE 직접) | ★★★ HIGH | **P1** |
| FORCE_ACC | ★★★ HIGH (ohlcv_daily 120일) | ★★ MEDIUM (×0.15) | ★★ MEDIUM | **P2** |
| BJ_SCORE | ★★ MEDIUM (재무 7.1% 커버) | ★★★ HIGH (+0.10/+0.20) | ★★ MEDIUM | **P2** |
| KJH_CYCLE | ★ LOW (5년 재무 필요, 7.1%) | ★★ MEDIUM (+0.05/+0.15) | ★ LOW | **P3** |

### 데이터 커버리지 현황
| 변수 | 의존 테이블 | 행수 | 종목수 | 커버리지 |
|------|------------|-----|--------|---------|
| MKT_SEASON | 없음 | — | — | 100% |
| D_D1_D2_ENTRY | ohlcv_daily | 2,623,502 | ~3,844 | ~100% |
| FORCE_ACC | ohlcv_daily | 2,623,502 | ~3,844 | ~100% |
| BJ_SCORE | v4_fundamental_quarterly | 787 | 149/3,844 | **7.1%** |
| KJH_CYCLE | v4_fundamental_quarterly (5년) | <787 | <149 | **<7.1%** |

### 권장 후속 조치
| 우선순위 | 조치 |
|---------|------|
| P0 즉시 | v4_fundamental_quarterly 수집 확대 (787→2,000행+) |
| P1 | D_D1_D2_ENTRY 발동 건수 일별 모니터링 시작 |
| P1 | MKT_SEASON Q2/Q4 구간 통과율 실측 |
| P2 | FORCE_ACC 실측 분포 확인 (score > 0.3 종목 비율) |

---

## 5. 테스트 4건 실행

### 실행 명령
```bash
/root/kis-autotrade-v4/venv/bin/python3 -m pytest \
  tests/unit/test_T218_dual_flow_feature.py \
  tests/unit/test_T219_theme_cycle_feature.py \
  tests/test_small_cap_sec_leader_v2.py \
  tests/test_funnel_score_t237.py -v
```

### 실행 결과 (전체 출력)
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 30 items

tests/unit/test_T218_dual_flow_feature.py::TestTC1AllBuy::test_dual_flow_5d_all_buy PASSED [  3%]
tests/unit/test_T218_dual_flow_feature.py::TestTC1AllBuy::test_dual_flow_20d_all_buy PASSED [  6%]
tests/unit/test_T218_dual_flow_feature.py::TestTC2ZeroBuy::test_dual_flow_5d_zero PASSED [ 10%]
tests/unit/test_T218_dual_flow_feature.py::TestTC2ZeroBuy::test_dual_flow_20d_zero PASSED [ 13%]
tests/unit/test_T218_dual_flow_feature.py::TestTC3Partial::test_dual_flow_5d_partial PASSED [ 16%]
tests/unit/test_T218_dual_flow_feature.py::TestTC3Partial::test_dual_flow_20d_partial PASSED [ 20%]
tests/unit/test_T218_dual_flow_feature.py::TestTC4NoData::test_dual_flow_5d_no_data PASSED [ 23%]
tests/unit/test_T218_dual_flow_feature.py::TestTC4NoData::test_dual_flow_20d_no_data PASSED [ 26%]
tests/unit/test_T219_theme_cycle_feature.py::TestTC1AllMatch::test_100b_count_all_match PASSED [ 30%]
tests/unit/test_T219_theme_cycle_feature.py::TestTC1AllMatch::test_ul_count_all_match PASSED [ 33%]
tests/unit/test_T219_theme_cycle_feature.py::TestTC2NoneMatch::test_100b_count_below_threshold PASSED [ 36%]
tests/unit/test_T219_theme_cycle_feature.py::TestTC2NoneMatch::test_ul_count_below_threshold PASSED [ 40%]
tests/unit/test_T219_theme_cycle_feature.py::TestTC3NoData::test_100b_count_no_data PASSED [ 43%]
tests/unit/test_T219_theme_cycle_feature.py::TestTC3NoData::test_ul_count_no_data PASSED [ 46%]
tests/test_small_cap_sec_leader_v2.py::TestSmallCapQuality::test_tc01_a_grade_all_conditions_met PASSED [ 50%]
tests/test_small_cap_sec_leader_v2.py::TestSmallCapQuality::test_tc02_b_grade_two_conditions_met PASSED [ 53%]
tests/test_small_cap_sec_leader_v2.py::TestSmallCapQuality::test_tc03_reject_no_data PASSED [ 56%]
tests/test_small_cap_sec_leader_v2.py::TestSmallCapQuality::test_tc04_c_grade_only_roe_positive PASSED [ 60%]
tests/test_small_cap_sec_leader_v2.py::TestFlagSectorLeadersV2::test_tc05_leader_supply_top_and_momentum_top PASSED [ 63%]
tests/test_small_cap_sec_leader_v2.py::TestFlagSectorLeadersV2::test_tc06_non_leader_low_rank PASSED [ 66%]
tests/test_small_cap_sec_leader_v2.py::TestFlagSectorLeadersV2::test_tc07_data_insufficient_no_investor_rows PASSED [ 70%]
tests/test_small_cap_sec_leader_v2.py::TestFlagSectorLeadersV2::test_tc08_boundary_exactly_at_cutoff PASSED [ 73%]
tests/test_funnel_score_t237.py::TestL0NullFallback::test_l0_returns_fallback_when_no_macro_data PASSED [ 76%]
tests/test_funnel_score_t237.py::TestL1NullFallback::test_l1_returns_fallback_when_no_sector_info PASSED [ 80%]
tests/test_funnel_score_t237.py::TestL2NullFallback::test_l2_returns_fallback_when_no_dual_flow PASSED [ 83%]
tests/test_funnel_score_t237.py::TestL3NullFallback::test_l3_returns_fallback_when_all_data_missing PASSED [ 86%]
tests/test_funnel_score_t237.py::TestNewWeightsCombination::test_new_weights_produce_passing_score PASSED [ 90%]
tests/test_funnel_score_t237.py::TestNewWeightsCombination::test_weight_sum_equals_one PASSED [ 93%]
tests/test_funnel_score_t237.py::TestMockReplay184::test_pass_rate_above_25pct PASSED [ 96%]
tests/test_funnel_score_t237.py::TestMockReplay184::test_avg_score_above_030 PASSED [100%]

=============================== warnings summary ===============================
tests/test_funnel_score_t237.py::TestL3NullFallback::test_l3_returns_fallback_when_all_data_missing
  /root/kis-autotrade-v4/venv/lib/python3.12/site-packages/sklearn/utils/validation.py:2691: UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with feature names
    warnings.warn(

tests/test_funnel_score_t237.py::TestL3NullFallback::test_l3_returns_fallback_when_all_data_missing
tests/test_funnel_score_t237.py::TestL3NullFallback::test_l3_returns_fallback_when_all_data_missing
tests/test_funnel_score_t237.py::TestL3NullFallback::test_l3_returns_fallback_when_all_data_missing
  /root/kis-autotrade-v4/venv/lib/python3.12/site-packages/sklearn/utils/validation.py:2691: UserWarning: X does not have valid feature names, but LGBMRegressor was fitted with feature names
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 30 passed, 4 warnings in 2.89s ========================
```

**결과: 30/30 ALL PASS** ✅

---

## 6. 보고서 작성 및 push

### 작성된 보고서
- 로컬: /root/kis-autotrade-v4/report/v41/CUR-V41-CEO-P0-VARIABLES-AUDIT-001-20260309.md
- project-docs: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-CEO-P0-VARIABLES-AUDIT-001-20260309.md

### git push 결과
```
[master 0137655] docs: T-230 CEO P0 변수 전수 감사 보고서 + HANDOVER v10.41 갱신 (20260309)
 2 files changed, 367 insertions(+), 1 deletion(-)
 create mode 100644 kis-autotrade-v4/reports/CUR-V41-CEO-P0-VARIABLES-AUDIT-001-20260309.md
To github.com:moongoby/project-docs.git
   41df1ec..0137655  master -> master
```

### HTTP 200 확인
```
HTTP: 200 ✅
```

---

## 7. HANDOVER.md 갱신

- 버전: v10.41
- 변경 내용: T-230 CEO P0 변수 전수 감사 완료 행 추가 (섹션 2 완료된 작업)
- 버전 이력: v10.40→v10.41 갱신
- 커밋: 0137655

---

## 8. 성공 기준 달성 여부

| 기준 | 상태 |
|-----|-----|
| 감사표 9개 완성 | ✅ |
| CTE 파이프라인 연결 확인 | ✅ 9/9 전원 연결 |
| 우선순위 매트릭스 작성 | ✅ (데이터 가용성/FunnelScore 영향/실효성) |
| 테스트 4건 ALL PASS | ✅ 30/30 케이스 PASS |
| 보고서 작성 | ✅ |
| HANDOVER 갱신 + git push | ✅ (커밋 0137655, HTTP 200) |

---

## 최종 체크포인트

- [x] 코드 레포 커밋 완료 — 코드 변경 없음 (감사전용 Task), feature_engine.py 기존 구현 확인
- [x] project-docs 보고서 push 완료 — GitHub raw URL HTTP 200 확인
  - https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-CEO-P0-VARIABLES-AUDIT-001-20260309.md

두 체크 모두 통과 → **T-230 완료 판정** ✅

HANDOVER.md 업데이트 완료: 0137655
