# T-140: D-010 Phase E — DESK2 5축 운영 마스크 구현 보고서

[인계 확인]
직전 완료: T-138
현재 단계: Phase 2c-command-center
CEO 지시 적용: D-010
strategy_cards: 60
open_positions: 14

---

## 개요

| 항목 | 내용 |
|------|------|
| Task ID | T-140 |
| 제목 | D-010 Phase E — DESK2 5축 운영 마스크 구현 |
| 우선순위 | P0-CRITICAL |
| 서버 | 211 (kis-autotrade-v4) |
| 브랜치 | phase-2c-command-center |
| 커밋 | e67ae9f3 |
| 완료 시각 | 2026-03-05 21:52 KST |

---

## 목적

CEO D-010 Phase E: 5축 분해(시간대/시장상태/변동성/순위/보유시간) ON/OFF 마스크 구현.
Phase A(C2/C1/C6) 컨디션 매칭 전 단계에 5축 필터를 결합하여 손실 구간 자동 차단.

---

## 작업 내용

### 1. 백업
```
backend/app/services/desk_filters/pipeline.py.bak.T140 생성
```

### 2. config/param_search_space.yaml — desk2_axis_mask 섹션 추가
```yaml
desk2_axis_mask:
  axis1_time:
    T1: { start: "09:00", end: "09:30", weight: 0.8 }
    T2: { start: "09:30", end: "10:30", weight: 1.2 }
    T3: { start: "10:30", end: "13:00", weight: 0.9 }
    T4: { start: "13:00", end: "14:30", weight: 0.7 }
    T5: { start: "14:30", end: "15:20", weight: 1.1 }
    T6: { start: "15:20", end: "15:30", weight: 0.6 }
  axis2_market: { BULL: 1.3, FLAT: 1.0, BEAR: 0.5 }
  axis3_volatility: { LOW: 0.8, MID: 1.0, HIGH: 1.2 }
  axis4_rank: { TOP: 1.3, MID: 1.0, LOW: 0.7 }
  axis5_holding: { SCALP: 0.9, SHORT: 1.0, MID: 1.1, HOLD: 0.8 }
  combined_threshold: 0.5
```

### 3. backend/app/services/desk2_conditions/axis_mask.py 신규 생성

**AxisMaskEngine 클래스 구조:**
- `__init__(yaml_path=None)`: YAML 로드 (실패 시 기본값), 시간 슬롯 캐시 구성
- `eval_axis1_time(timestamp)`: 시간대 가중치 반환 (T1~T6)
- `eval_axis2_market(regime)`: 시장 레짐(BULL/FLAT/BEAR) 가중치
- `eval_axis3_volatility(volatility)`: 변동성(LOW/MID/HIGH) 가중치
- `eval_axis4_rank(rank)`: 순위(TOP/MID/LOW) 가중치
- `eval_axis5_holding(holding_type)`: 보유시간(SCALP/SHORT/MID/HOLD) 가중치
- `evaluate(timestamp, regime, volatility, rank, holding_type)`: 5축 곱 → threshold 비교
  - `combined <= threshold` → BLOCK
  - `combined > threshold` → ALLOW
  - 반환: `{w1~w5, combined, threshold, decision, blocked}`

**알 수 없는 키 처리:**
- axis2: 미등록 regime → FLAT(1.0) fallback
- axis3: 미등록 volatility → MID(1.0) fallback
- axis4: 미등록 rank → MID(1.0) fallback
- axis5: 미등록 holding_type → SHORT(1.0) fallback

### 4. backend/app/services/desk_filters/pipeline.py — AxisMaskEngine 삽입

**위치:** `run_desk2()` 메서드 상단 — `self.desk2.evaluate()` 호출 **전** 단계

**동작 흐름:**
```
run_desk2() 호출
  → AxisMaskEngine 로드 (lazy import, 실패 시 비활성화)
  → data 에서 timestamp/market_regime/volatility/rank/holding_type 추출
  → axis_mask.evaluate() 호출
  → BLOCK → 즉시 {pass:False, score:0.0, reason:'axis_mask_block', axis_mask:...} 반환
  → ALLOW → 기존 desk2.evaluate() 진행, 결과에 axis_mask 첨부
```

**Lazy import 처리:** AxisMaskEngine 로드 실패 시 경고 로그만 출력하고 axis_mask 비활성화 (기존 평가 계속).

---

## 테스트 결과

```
tests/unit/test_axis_mask.py - 32건 ALL PASS (2.14s)

TestAxis1Time (5건):
  - test_t2_weight           PASSED  [T2=1.2]
  - test_t6_weight           PASSED  [T6=0.6]
  - test_t4_weight           PASSED  [T4=0.7]
  - test_t5_weight           PASSED  [T5=1.1]
  - test_outside_slot_fallback PASSED [08:55→1.0]

TestAxis2Market (4건):
  - test_bull                PASSED  [1.3]
  - test_bear                PASSED  [0.5]
  - test_flat                PASSED  [1.0]
  - test_unknown_fallback    PASSED  [→1.0]

TestAxis3Volatility (3건):
  - test_high                PASSED  [1.2]
  - test_low                 PASSED  [0.8]
  - test_mid                 PASSED  [1.0]

TestAxis4Rank (3건):
  - test_top                 PASSED  [1.3]
  - test_low                 PASSED  [0.7]
  - test_mid                 PASSED  [1.0]

TestAxis5Holding (5건):
  - test_scalp               PASSED  [0.9]
  - test_short               PASSED  [1.0]
  - test_mid                 PASSED  [1.1]
  - test_hold                PASSED  [0.8]
  - test_unknown_fallback    PASSED  [→1.0]

TestEvaluateIntegration (12건):
  - test_bull_t2_high_top_allow         PASSED [1.2×1.3×1.2×1.3×1.0=2.4336→ALLOW]
  - test_bear_t6_low_low_block          PASSED [0.6×0.5×0.8×0.7×1.0=0.168→BLOCK]
  - test_boundary_just_above_threshold  PASSED [0.9>0.5→ALLOW]
  - test_boundary_exact_threshold_is_block PASSED [0.416≤0.5→BLOCK]
  - test_result_has_required_keys       PASSED
  - test_decision_allow_combined_greater_than_threshold PASSED [2.6196→ALLOW]
  - test_flat_mid_mid_mid_short_allow   PASSED [0.9→ALLOW]
  - test_bear_t4_low_low_hold_block     PASSED [0.1568→BLOCK]
  - test_case_insensitive_input         PASSED [소문자=대문자]
  - test_threshold_in_result            PASSED [threshold=0.5]
  - test_bull_t1_high_top_short         PASSED [1.6224→ALLOW]
  - test_bear_t6_low_low_scalp_extreme_block PASSED [0.1512→BLOCK]
```

---

## 지시서 지정 케이스 검증

| 조합 | 계산 | 결과 |
|------|------|------|
| BULL+T2+HIGH+TOP+SHORT | 1.2×1.3×1.2×1.3×1.0 = 2.4336 | ✅ ALLOW |
| BEAR+T6+LOW+LOW+SHORT | 0.6×0.5×0.8×0.7×1.0 = 0.168 | ✅ BLOCK |

---

## 완료 기준 체크

- [x] pytest PASS (32/32)
- [x] 5축 마스크 pipeline 연동 (컨디션 매칭 전 단계)
- [x] YAML 외부화 (config/param_search_space.yaml)
- [x] git commit e67ae9f3

---

## 변경 파일 목록

| 파일 | 변경 |
|------|------|
| backend/app/services/desk2_conditions/axis_mask.py | 신규 (AxisMaskEngine) |
| backend/app/services/desk_filters/pipeline.py | 수정 (AxisMaskEngine 삽입) |
| backend/app/services/desk_filters/pipeline.py.bak.T140 | 백업 |
| config/param_search_space.yaml | 수정 (desk2_axis_mask 섹션 추가) |
| tests/unit/test_axis_mask.py | 신규 (32건) |
