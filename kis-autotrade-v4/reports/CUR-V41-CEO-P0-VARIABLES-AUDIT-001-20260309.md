# CUR-V41-CEO-P0-VARIABLES-AUDIT-001-20260309

**Task ID**: T-230
**제목**: CEO P0 변수 전수 감사 + 파이프라인 연결 확인
**서버**: 211 (kis-autotrade-v4)
**우선순위**: P1-HIGH
**작업일**: 2026-03-09 (KST)
**작업자**: claudebot (Claude Sonnet 4.6)

---

## [인계 확인]

```
직전 완료: T-235 (SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2 구현, 2026-03-09)
현재 단계: Phase 2C (CTE 파이프라인 통합)
CEO 지시 적용: D-008-KR P0~P2 (한국 슈퍼개미 7인 전략 통합)
strategy_cards: 60
open_positions: 0
```

---

## 1. 감사 목적

CEO D-008-KR 지시서에 따라 정의된 **한국 시장 고유 변수 9개** (P0~P2)의 구현 완료 여부 및 CTE 파이프라인 연결 상태를 전수 감사한다.

- **P0 즉시 구현 4개**: THEME_CYCLE, SMALL_CAP_QUALITY, DUAL_FLOW, SEC_LEADER_FLAG v2
- **P1 1주 내 구현 3개**: MKT_SEASON, FORCE_ACC, D_D1_D2_ENTRY
- **P2 2주 내 구현 2개**: BJ_SCORE, KJH_CYCLE

---

## 2. 9개 P0 변수 전수 감사표

### 2-1. 구현 완료 4개 (P0 즉시 — ✅ 확인됨)

| 변수 | 클래스/함수 | 구현 파일 | 태스크 | 커밋 |
|------|------------|---------|--------|------|
| **DUAL_FLOW** | `DualFlowEngine`, `compute_dual_flow_5d/20d` | feature_engine.py | T-111/T-218 | faa85636 (2026-03-07) |
| **THEME_CYCLE** | `ThemeCycleEngine`, `compute_theme_cycle_100b_count/ul_count` | feature_engine.py | T-109/T-219 | 7f27b7b4 (2026-03-07) |
| **SMALL_CAP_QUALITY** | `compute_small_cap_quality`, `SmallCapQualityFilter` | feature_engine.py, universe_builder.py | T-110/T-235 | 20017658 (2026-03-09) |
| **SEC_LEADER_FLAG v2** | `SecLeaderV2Engine`, `flag_sector_leaders_v2` | feature_engine.py, universe_builder.py | T-112/T-235 | 20017658 (2026-03-09) |

### 2-2. 미지정 5개 — 감사 결과: **전원 구현 완료** ✅

| 변수 | 지시서 분류 | 실제 상태 | 클래스 | 태스크 | 커밋 |
|------|------------|---------|--------|--------|------|
| **MKT_SEASON** | P1 | ✅ 구현+연결 완료 | `MktSeasonEngine` | T-115 | 5f4d590c (2026-03-05) |
| **FORCE_ACC** | P1 | ✅ 구현+연결 완료 | `ForceAccEngine` | T-116 | 7d213031 (2026-03-05) |
| **D_D1_D2_ENTRY** | P1 | ✅ 구현+연결 완료 | `DDayEntryEngine` | T-117 | 474039d7 (2026-03-05) |
| **BJ_SCORE** | P2 | ✅ 구현+연결 완료 | `BjScoreEngine` | T-121 | d7fea642 (2026-03-05) |
| **KJH_CYCLE** | P2 | ✅ 구현+연결 완료 | `KjhCycleEngine` | T-122 | dacc29bf (2026-03-05) |

**결론**: CEO D-008-KR에서 P1/P2로 분류된 5개 변수는 T-115~T-122 (2026-03-05) 작업을 통해 모두 구현 완료 및 FunnelScoreEngine에 연결됨. 지시서 작성 시점 기준 "❓"로 표시된 변수들이 이미 구현 완료 상태임.

---

## 3. CTE 파이프라인 연결 확인 (T-237 이후 상태)

### 3-1. 연결 구조도

```
CTE 파이프라인 평가 흐름
├── L0 (매크로, 가중치 40%)
│   ├── macro_regime (BULL/NEUTRAL/BEAR)
│   ├── VIX 점수
│   ├── KOSPI MA60/MA120 위치
│   └── ★ MKT_SEASON 사계절 가중치 조정 (T-115: Q2×1.2, Q4×0.7)
│
├── L1 (섹터/테마, 가중치 10%)
│   ├── 업종 RS 기반 점수 (0.0~0.7)
│   ├── ★ THEME_CYCLE_SCORE × 0.2 (T-109: 과거 3년 100억+상한가 횟수)
│   └── ★ SEC_LEADER_FLAG v2 bonus +0.3 (T-112: RS>80, 거래대금1위, 폭락후돌파)
│
├── L2 (수급 흐름, 가중치 20%)
│   ├── ★ DUAL_FLOW_SCORE × 0.7 (T-111: 기관+외인 동시 순매수 비율)
│   ├── CLOSE_POSITION_5D bonus +0.3
│   └── ★ FORCE_ACC bonus × 0.15 (T-116: 120일선 수렴+급등봉+갭상승)
│
├── L3 (펀더멘탈, 가중치 30%)
│   ├── GrowthScore (T-098)
│   ├── ★ SMALL_CAP_QUALITY 판정 +0.2 bonus (T-110/T-235: ROE>0/흑자≥75%/부채<200%)
│   ├── PEG inverse 점수
│   ├── 영업이익 YoY 추세
│   ├── ★ BJ_SCORE bonus (T-121: ≥80→+0.20, ≥60→+0.10)
│   └── ★ KJH_CYCLE bonus (T-122: GROWTH≥0.7→+0.15, MATURE≥0.5→+0.05)
│
└── L2.5 CTE 파이프라인 직접 연결
    └── ★ D_D1_D2_ENTRY (T-117: DDayEntryEngine, is_dday_candidate, dday_signal_result)
```

### 3-2. 레이어별 상세 연결 상태

#### L0: MKT_SEASON (funnel_score_engine.py:194-206)
```python
from backend.app.services.feature_engine import MktSeasonEngine
season_engine = MktSeasonEngine()
score = season_engine.adjust_score(score, date, macro_regime=regime)
# Q1=0.9, Q2=1.2, Q3=0.8, Q4=0.7 / BEAR×0.5, BULL×1.3
```
- **연결 레이어**: L0 최종 점수 조정
- **데이터 의존성**: 없음 (날짜 기반 계산)
- **T-237 Fail-Open**: L0 데이터 없음 → null_fallback_score=0.5

#### L1: SEC_LEADER_FLAG v2 (funnel_score_engine.py:322-332)
```python
from backend.app.services.feature_engine import SecLeaderV2Engine
_sl_engine = SecLeaderV2Engine()
_sl_result = _sl_engine.calculate_sec_leader_v2(symbol, date)
if _sl_result.get("is_leader_v2"):
    sec_leader_bonus = leader_bonus  # +0.3
```
- **연결 레이어**: L1 섹터/테마 점수 보너스
- **데이터 의존성**: v4_investor_daily, v4_sector_mapping, v4_sector_index_daily

#### L1: THEME_CYCLE (funnel_score_engine.py:334-343)
```python
from backend.app.services.feature_engine import ThemeCycleEngine
tc_engine = ThemeCycleEngine()
tc_result = tc_engine.calculate_theme_cycle(symbol)
theme_cycle_score = float(tc_result.get("THEME_CYCLE_SCORE", 0.0))
score = min(1.0, max(0.0, s_rs + s_theme + sec_leader_bonus + theme_cycle_score * 0.2))
```
- **연결 레이어**: L1 최종 점수의 +20% 가산
- **데이터 의존성**: ohlcv_daily (trade_amount, pct_change)

#### L2: DUAL_FLOW (funnel_score_engine.py:422-434)
```python
from backend.app.services.feature_engine import DualFlowEngine
df_engine = DualFlowEngine()
df_result = df_engine.calculate_dual_flow(symbol, date)
dual_flow_score = float(df_result.get("DUAL_FLOW_SCORE", 0.0))
# SCORE = DUAL_FLOW_20D * 0.5 + min(CONSEC_FOREIGN_BUY/5, 1.0) * 0.5
raw = dual_flow_score * 0.7 + s_close
```
- **연결 레이어**: L2 주요 점수 (가중치 70%)
- **데이터 의존성**: v4_investor_daily (foreign_net_qty, institution_net_qty)

#### L2: FORCE_ACC (funnel_score_engine.py:449-457)
```python
from backend.app.services.feature_engine import ForceAccEngine
fa_engine = ForceAccEngine()
fa_result = fa_engine.calculate_force_acc(symbol, date)
force_acc_bonus = float(fa_result.get("force_acc_score", 0.0)) * 0.15
```
- **연결 레이어**: L2 보너스 점수 (+최대 0.15)
- **데이터 의존성**: ohlcv_daily (120일 이동평균 수렴도, 급등봉, 갭)

#### L3: SMALL_CAP_QUALITY (funnel_score_engine.py:581-597)
```python
from backend.app.services.feature_engine import compute_small_cap_quality
_scq_v2 = compute_small_cap_quality(rows)
quality_score_v2 = float(_scq_v2.get("quality_score", 0.0))
# CEO 3대조건: ROE>0, 영업이익흑자≥75%, 부채비율<200%
# T-110 SmallCapQualityFilter 전체 통과 시 scq_bonus = +0.2
```
- **연결 레이어**: L3 quality_score + scq_bonus +0.2
- **데이터 의존성**: v4_fundamental_quarterly (roe, op_profit, debt_ratio)

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
- **연결 레이어**: L3 보너스 (+0.10 or +0.20)
- **데이터 의존성**: v4_fundamental_quarterly, 뉴스 데이터 (대재수심차 5원칙)

#### L3: KJH_CYCLE (funnel_score_engine.py:638-657)
```python
from backend.app.services.feature_engine import KjhCycleEngine
kjh_engine = KjhCycleEngine()
kjh_result = kjh_engine.calculate_kjh_score(symbol)
if kjh_score_val >= 0.7 and kjh_phase == "GROWTH":
    kjh_bonus = 0.15
elif kjh_score_val >= 0.5 and kjh_phase == "MATURE":
    kjh_bonus = 0.05
```
- **연결 레이어**: L3 보너스 (+0.05 or +0.15)
- **데이터 의존성**: v4_fundamental_quarterly (5년 재무 데이터 필요)

#### L2.5 CTE 직접: D_D1_D2_ENTRY (cte_pipeline.py:474-481)
```python
if signal.is_dday_candidate and signal.dday_signal_result is not None:
    _dday = signal.dday_signal_result
    result.is_dday_candidate = True
    result.dday_action   = _dday.get("action", "SKIP")  # ENTRY/WAIT/REJECT
    result.dday_day_type = _dday.get("day_type", "")    # D/D+1/D+2
    result.details["dday"] = {...}
```
- **연결 레이어**: L2.5 CTE 파이프라인 직접 (FunnelScore 우회)
- **데이터 의존성**: ohlcv_daily (장대양봉 ≥7%, 거래량 2.5배)
- **주의**: REJECT 액션이어도 파이프라인 차단 안 함 (우선순위 가산만)

---

## 4. 미구현 5개 우선순위 매트릭스

> **감사 결과 수정**: 지시서에서 "미구현"으로 분류된 5개는 실제로 모두 구현 완료됨.
> 아래 매트릭스는 **실질적 데이터 기여도 및 개선 우선순위** 기준으로 재작성.

### 4-1. 실효성 매트릭스

| 변수 | 데이터 가용성 | FunnelScore 영향도 | 실제 기여도 | 개선 필요 사항 | 우선순위 |
|------|-------------|-------------------|-----------|--------------|---------|
| **MKT_SEASON** | ★★★ HIGH | ★★ MEDIUM (+/-30%) | ★★★ HIGH | 계절별 실증 데이터 부재 → 백테스트 검증 필요 | P1 |
| **D_D1_D2_ENTRY** | ★★★ HIGH | ★★ INDIRECT (CTE 직접) | ★★★ HIGH | leader_only=True 조건 → 현실 적용 종목 수 추적 필요 | P1 |
| **FORCE_ACC** | ★★★ HIGH | ★★ MEDIUM (+max 0.15) | ★★ MEDIUM | 실제 force_acc_score 분포 실측 필요 (매집 감지율) | P2 |
| **BJ_SCORE** | ★★ MEDIUM | ★★★ HIGH (+0.10/+0.20) | ★★ MEDIUM | 뉴스 214만건 연결 강화 → 실증 필요 (현재 재무 커버 7.1%) | P2 |
| **KJH_CYCLE** | ★ LOW | ★★ MEDIUM (+0.05/+0.15) | ★ LOW | 5년 재무데이터 커버리지 7.1%→50%+ 확대 필요 | P3 |

### 4-2. 데이터 커버리지 현황

| 변수 | 의존 테이블 | 커버리지 | 가용 여부 |
|------|------------|---------|---------|
| MKT_SEASON | 없음 (날짜 계산) | 100% | ✅ 즉시 활용 |
| D_D1_D2_ENTRY | ohlcv_daily (2,623,502행) | ~100% | ✅ 즉시 활용 |
| FORCE_ACC | ohlcv_daily (120일선) | ~100% | ✅ 즉시 활용 |
| BJ_SCORE | v4_fundamental_quarterly (787행/3,844종목) | **7.1%** | ⚠️ 데이터 확대 필요 |
| KJH_CYCLE | v4_fundamental_quarterly (5년 필요) | **<7.1%** | ❌ 데이터 심각 부족 |

### 4-3. 권장 개선 로드맵

| 단계 | 변수 | 조치 | 기대 효과 |
|-----|-----|------|---------|
| **즉시** | MKT_SEASON | Q2/Q4 실측 효과 검증 (backtest 기반) | 계절 조정 신뢰도 ↑ |
| **즉시** | D_D1_D2_ENTRY | is_dday_candidate 일별 발생 건수 모니터링 | 장대양봉 포착율 추적 |
| **1주** | FORCE_ACC | force_acc_score > 0.3 종목 비율 실측 | 매집 포착 실효성 확인 |
| **1주** | BJ_SCORE | v4_fundamental_quarterly 수집 확대 (3,844→2,000+종목) | BJ_SCORE 기여 구간 확대 |
| **2주** | KJH_CYCLE | 5년치 재무 KIS API 수집 (현재 787행 → 목표 10,000행+) | KJH_CYCLE 기여 구간 확대 |

---

## 5. 테스트 4건 실행 결과

```
실행 명령: /root/kis-autotrade-v4/venv/bin/python3 -m pytest \
  tests/unit/test_T218_dual_flow_feature.py \
  tests/unit/test_T219_theme_cycle_feature.py \
  tests/test_small_cap_sec_leader_v2.py \
  tests/test_funnel_score_t237.py -v

실행 시각: 2026-03-09 KST
```

### 테스트 1: T-218 DUAL_FLOW 피처 (8케이스)
```
tests/unit/test_T218_dual_flow_feature.py::TestTC1AllBuy::test_dual_flow_5d_all_buy PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC1AllBuy::test_dual_flow_20d_all_buy PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC2ZeroBuy::test_dual_flow_5d_zero PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC2ZeroBuy::test_dual_flow_20d_zero PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC3Partial::test_dual_flow_5d_partial PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC3Partial::test_dual_flow_20d_partial PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC4NoData::test_dual_flow_5d_no_data PASSED
tests/unit/test_T218_dual_flow_feature.py::TestTC4NoData::test_dual_flow_20d_no_data PASSED
결과: 8/8 PASS ✅
```

### 테스트 2: T-219 THEME_CYCLE 피처 (6케이스)
```
tests/unit/test_T219_theme_cycle_feature.py::TestTC1AllMatch::test_100b_count_all_match PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC1AllMatch::test_ul_count_all_match PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC2NoneMatch::test_100b_count_below_threshold PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC2NoneMatch::test_ul_count_below_threshold PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC3NoData::test_100b_count_no_data PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC3NoData::test_ul_count_no_data PASSED
결과: 6/6 PASS ✅
```

### 테스트 3: T-235 SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2 (8케이스)
```
tests/test_small_cap_sec_leader_v2.py::TestSmallCapQuality::test_tc01_a_grade_all_conditions_met PASSED
tests/test_small_cap_sec_leader_v2.py::TestSmallCapQuality::test_tc02_b_grade_two_conditions_met PASSED
tests/test_small_cap_sec_leader_v2.py::TestSmallCapQuality::test_tc03_reject_no_data PASSED
tests/test_small_cap_sec_leader_v2.py::TestSmallCapQuality::test_tc04_c_grade_only_roe_positive PASSED
tests/test_small_cap_sec_leader_v2.py::TestFlagSectorLeadersV2::test_tc05_leader_supply_top_and_momentum_top PASSED
tests/test_small_cap_sec_leader_v2.py::TestFlagSectorLeadersV2::test_tc06_non_leader_low_rank PASSED
tests/test_small_cap_sec_leader_v2.py::TestFlagSectorLeadersV2::test_tc07_data_insufficient_no_investor_rows PASSED
tests/test_small_cap_sec_leader_v2.py::TestFlagSectorLeadersV2::test_tc08_boundary_exactly_at_cutoff PASSED
결과: 8/8 PASS ✅
```

### 테스트 4: T-237 FunnelScore Fail-Open + 가중치 (8케이스)
```
tests/test_funnel_score_t237.py::TestL0NullFallback::test_l0_returns_fallback_when_no_macro_data PASSED
tests/test_funnel_score_t237.py::TestL1NullFallback::test_l1_returns_fallback_when_no_sector_info PASSED
tests/test_funnel_score_t237.py::TestL2NullFallback::test_l2_returns_fallback_when_no_dual_flow PASSED
tests/test_funnel_score_t237.py::TestL3NullFallback::test_l3_returns_fallback_when_all_data_missing PASSED
tests/test_funnel_score_t237.py::TestNewWeightsCombination::test_new_weights_produce_passing_score PASSED
tests/test_funnel_score_t237.py::TestNewWeightsCombination::test_weight_sum_equals_one PASSED
tests/test_funnel_score_t237.py::TestMockReplay184::test_pass_rate_above_25pct PASSED
tests/test_funnel_score_t237.py::TestMockReplay184::test_avg_score_above_030 PASSED
결과: 8/8 PASS ✅
```

### 전체 테스트 결과
```
======================== 30 passed, 4 warnings in 2.89s ========================
4개 테스트 파일 × 총 30 케이스: ALL PASS ✅
```

---

## 6. 감사 결론 및 주요 발견

### 6-1. 핵심 발견

1. **9개 P0 변수 전원 구현 완료**: CEO D-008-KR의 P0/P1/P2 변수 9개 전부 `feature_engine.py`에 클래스/함수로 구현 완료. 지시서의 "❓ 5개 미구현"은 T-115~T-122 (2026-03-05) 작업으로 이미 해소됨.

2. **파이프라인 연결 완료**: 9개 변수 전부 FunnelScoreEngine (L0~L3) 또는 CTE 파이프라인 (L2.5)에 연결됨. T-237 이후 null_fallback_score=0.5로 Fail-Open 강화됨.

3. **실질적 기여 제약**: BJ_SCORE (T-121), KJH_CYCLE (T-122)는 `v4_fundamental_quarterly` 커버리지 7.1% (787행/3,844종목) 한계로 실질 기여 제한. 연결은 완료됐으나 데이터 수집 확대 필요.

4. **T-237 Fail-Open 효과**: L0~L3 각 레이어 데이터 없음 시 null_fallback_score=0.5 반환으로 구조적 차단 해소. 실측 통과율 상승 기대.

### 6-2. 변수별 최종 상태

| 변수 | CEO 분류 | 구현 | 파이프라인 연결 | 데이터 가용 | 실효성 |
|------|---------|------|--------------|-----------|-------|
| DUAL_FLOW | P0 | ✅ T-111/T-218 | ✅ L2 주점수 | ✅ HIGH | ★★★ |
| THEME_CYCLE | P0 | ✅ T-109/T-219 | ✅ L1 +0.2 | ✅ HIGH | ★★★ |
| SMALL_CAP_QUALITY | P0 | ✅ T-110/T-235 | ✅ L3 +0.2 | ✅ HIGH | ★★★ |
| SEC_LEADER_FLAG v2 | P0 | ✅ T-112/T-235 | ✅ L1 +0.3 | ✅ HIGH | ★★★ |
| MKT_SEASON | P1 | ✅ T-115 | ✅ L0 조정 | ✅ HIGH | ★★★ |
| FORCE_ACC | P1 | ✅ T-116 | ✅ L2 +0.15 | ✅ HIGH | ★★ |
| D_D1_D2_ENTRY | P1 | ✅ T-117 | ✅ L2.5 CTE | ✅ HIGH | ★★★ |
| BJ_SCORE | P2 | ✅ T-121 | ✅ L3 +0.10/+0.20 | ⚠️ 7.1% | ★★ |
| KJH_CYCLE | P2 | ✅ T-122 | ✅ L3 +0.05/+0.15 | ❌ <7.1% | ★ |

### 6-3. 권장 후속 조치

| 우선순위 | 항목 | 내용 | 예상 효과 |
|---------|------|------|---------|
| **P0** | v4_fundamental_quarterly 수집 확대 | 787행 → 2,000행+ (BJ_SCORE/KJH_CYCLE 기여 구간 확대) | BJ/KJH 실효성 ↑ |
| **P1** | D_D1_D2_ENTRY 발동 건수 모니터링 | is_dday_candidate 일별 통계 수집 | 장대양봉 포착율 실측 |
| **P1** | MKT_SEASON 계절 효과 검증 | Q2/Q4 구간 통과율 비교 | 계절 조정 신뢰도 ↑ |
| **P2** | FORCE_ACC 실측 분포 확인 | force_acc_score > 0.3 종목 비율 | 매집 감지 실효성 확인 |

---

## 7. 성공 기준 달성 여부

| 기준 | 상태 |
|-----|-----|
| 감사표 9개 완성 | ✅ |
| CTE 파이프라인 연결 확인 | ✅ (9/9 전원 연결) |
| 우선순위 매트릭스 작성 | ✅ (데이터 가용성/FunnelScore 영향/실효성) |
| 테스트 4건 ALL PASS | ✅ (30/30 케이스 PASS) |
| 보고서 작성 | ✅ |

---

## 저장 정보

- 서버 경로: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-CEO-P0-VARIABLES-AUDIT-001-20260309.md`
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-CEO-P0-VARIABLES-AUDIT-001-20260309.md
- 커밋: 0137655
- HTTP 확인: 200 ✅
- HANDOVER 업데이트: v10.41 완료 (커밋 0137655)
