---
project: KIS AutoTrade V4.1
task_id: T-141
completed_at: 2026-03-05 21:57 KST
---

# T-141 실행 결과 — D-010 DCS 일일합산 + 컨디션 등급체계(A/B/C)

## 지시서 원문
```
Task ID: T-141 제목: D-010 DCS 일일합산 + 컨디션 등급체계(A/B/C) 서버: 211 (kis-autotrade-v4) 우선순위: P1-HIGH 예상 시간: 25분 의존성: T-140

목적: CEO D-010 핵심 — DCS(Daily Condition Score) 일일합산 평가 시스템과 A/B/C 등급 자동 리밸런싱 구현.

작업 내용:

백업: pipeline.py, param_search_space.yaml
YAML desk2_dcs 섹션 추가:
desk2_dcs:
  evaluation_window: 20  # 거래일
  grade_a: { min_dcs_pct: 2.0, min_positive_ratio: 0.6, allocation: 0.4 }
  grade_b: { min_dcs_pct: 0.5, min_positive_ratio: 0.5, allocation: 0.1 }
  grade_c: { allocation: 0.0 }  # 시뮬만
  rebalance_interval: 20  # 거래일

새 파일 backend/app/services/desk2_conditions/dcs_evaluator.py:
DcsEvaluator 클래스
calculate_daily_dcs(condition_id, date) → 해당 컨디션의 일일 수익률 합산
evaluate_grade(condition_id) → 20일 윈도우 DCS% + 양일비율 → A/B/C 등급
get_allocation(condition_id) → 등급별 자금 배분율
rebalance_all() → 전 컨디션 재평가
DB 테이블: v4_desk2_dcs_history (condition_id, date, dcs_pct, grade, positive_days, total_days)
마이그레이션 파일 생성 (ALTER 금지 준수 — 새 테이블만)
pipeline 연동: 진입 시 grade C 컨디션 자동 차단
테스트 10건 이상 (등급 경계, 리밸런싱, 차단 로직)
git commit [V4.1] T-141: D-010 DCS 등급체계
보고서 + HANDOVER 갱신

완료 기준: DCS 계산 + 등급 자동 분류 + C등급 차단 작동
```

---

## 실행 로그

### Step 1: HANDOVER.md + CEO-DIRECTIVES.md 읽기
- HANDOVER.md: /root/project-docs/kis-autotrade-v4/HANDOVER.md 읽기 완료 (v10.10)
  - 직전 완료: T-138 미커밋 Push
  - 현재 Phase: Phase 2C Command Center
  - CEO 지시: D-001~D-014 전체 확인
- CEO-DIRECTIVES.md: 읽기 완료 (v1.6)
  - D-010 DCS 등급체계 핵심 확인
  - D-012/D-013/D-014 프랙탈 구조 확인

### Step 2: 백업
```
cp /root/kis-autotrade-v4/backend/app/services/desk_filters/pipeline.py \
   /root/kis-autotrade-v4/backend/app/services/desk_filters/pipeline.py.bak_T141
cp /root/kis-autotrade-v4/config/param_search_space.yaml \
   /root/kis-autotrade-v4/config/param_search_space.yaml.bak_T141
→ 백업 완료
```

### Step 3: YAML desk2_dcs 섹션 추가
파일: /root/kis-autotrade-v4/config/param_search_space.yaml

추가 내용:
```yaml
# ────────────────────────────────────────────────────────────
# T-141: D-010 DCS 일일합산 + 컨디션 등급체계(A/B/C)
# CEO D-010 §등급 — 20거래일 윈도우 DCS% + 양일비율 → A/B/C
# DcsEvaluator에서 사용
# ────────────────────────────────────────────────────────────
desk2_dcs:
  evaluation_window: 20  # 거래일
  grade_a: { min_dcs_pct: 2.0, min_positive_ratio: 0.6, allocation: 0.4 }
  grade_b: { min_dcs_pct: 0.5, min_positive_ratio: 0.5, allocation: 0.1 }
  grade_c: { allocation: 0.0 }  # 시뮬만
  rebalance_interval: 20  # 거래일
```
→ 적용 위치: p1_features 섹션 직전

### Step 4: DcsEvaluator 클래스 생성
파일: /root/kis-autotrade-v4/backend/app/services/desk2_conditions/dcs_evaluator.py

구현 메서드:
1. `calculate_daily_dcs(condition_id, target_date, pnl_rows=None)`:
   - pnl_rows가 없으면 DB(v4_strategy_results)에서 조회
   - sum(pnl_pct) → dcs_pct 계산
   - v4_desk2_dcs_history에 UPSERT
   - 반환: {condition_id, date, dcs_pct, trade_count, positive, saved}

2. `evaluate_grade(condition_id, as_of=None, history_rows=None)`:
   - history_rows가 없으면 DB(v4_desk2_dcs_history)에서 최근 20거래일 조회
   - dcs_total, positive_ratio 계산
   - _classify_grade() 호출: A/B/C 판정
   - DB 등급 갱신 (실패 시 경고 로그)
   - 반환: {condition_id, grade, dcs_pct_total, positive_ratio, positive_days, total_days, allocation, as_of}

3. `get_allocation(condition_id, as_of=None, history_rows=None)`:
   - evaluate_grade() 호출 후 allocation 반환
   - A=0.4, B=0.1, C=0.0

4. `is_blocked(condition_id, as_of=None, history_rows=None)`:
   - evaluate_grade() 호출 후 grade=="C" 여부 반환
   - pipeline.py에서 진입 차단용

5. `rebalance_all(condition_ids=None, as_of=None)`:
   - condition_ids가 None이면 DB에서 활성 컨디션 목록 조회
   - 각 컨디션 evaluate_grade() 호출
   - 반환: {as_of, total, grade_a, grade_b, grade_c, results}

설계 특징:
- history_rows/pnl_rows 외부 주입 → DB 없는 단위테스트 가능
- DB 연결 실패 시 graceful degradation
- param_override 지원 → 백테스트 파라미터 탐색 가능
- lazy import _get_db_conn() → DB 연결 비용 최소화

### Step 5: DB 마이그레이션 파일 생성
파일: /root/kis-autotrade-v4/backend/migrations/066_v4_desk2_dcs_history.sql

DDL:
```sql
CREATE TABLE IF NOT EXISTS v4_desk2_dcs_history (
    id              BIGSERIAL       PRIMARY KEY,
    condition_id    VARCHAR(10)     NOT NULL,
    date            DATE            NOT NULL,
    dcs_pct         NUMERIC(10, 4)  NOT NULL DEFAULT 0.0,
    positive        BOOLEAN         NOT NULL DEFAULT FALSE,
    trade_count     INTEGER         NOT NULL DEFAULT 0,
    grade           VARCHAR(10)     NOT NULL DEFAULT 'PENDING',
    positive_days   INTEGER         NOT NULL DEFAULT 0,
    total_days      INTEGER         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_desk2_dcs_cond_date UNIQUE (condition_id, date)
);

CREATE INDEX IF NOT EXISTS idx_desk2_dcs_condition_date ON v4_desk2_dcs_history (condition_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_desk2_dcs_grade ON v4_desk2_dcs_history (grade, date DESC);
CREATE INDEX IF NOT EXISTS idx_desk2_dcs_date ON v4_desk2_dcs_history (date DESC);
```
→ ALTER 금지 원칙 준수. 신규 테이블만.

### Step 6: pipeline.py 연동
파일: /root/kis-autotrade-v4/backend/app/services/desk_filters/pipeline.py

수정 1 — docstring 업데이트:
```
T-141: D-010 DCS 등급체계 (A/B/C) 연동
  - DcsEvaluator: 컨디션 진입 전 C등급 자동 차단
  - condition_id 데이터 없으면 차단 스킵 (graceful degradation)
```

수정 2 — lazy import 추가:
```python
# T-141: DcsEvaluator lazy import
_dcs_evaluator = None

def _get_dcs_evaluator():
    global _dcs_evaluator
    if _dcs_evaluator is None:
        try:
            from backend.app.services.desk2_conditions.dcs_evaluator import DcsEvaluator
            _dcs_evaluator = DcsEvaluator()
        except Exception as e:
            logger.warning("DcsEvaluator 로드 실패 (dcs_grade_block 비활성화): %s", e)
    return _dcs_evaluator
```

수정 3 — run_desk2() 내 C등급 차단:
```python
# ── T-141: DCS 등급 C → 진입 차단 ──
condition_id = data.get("condition_id")
if condition_id:
    dcs_eval = _get_dcs_evaluator()
    if dcs_eval is not None:
        try:
            if dcs_eval.is_blocked(condition_id):
                logger.info("[PIPELINE][T-141] DESK2 BLOCK (dcs_grade_c): stock=%s condition=%s", stock_code, condition_id)
                return {
                    "stock_code": stock_code, "desk_level": 2,
                    "pass": False, "score": 0.0,
                    "reason": "dcs_grade_c_block",
                    "condition_id": condition_id,
                    "axis_mask": axis_mask_result,
                }
        except Exception as exc:
            logger.warning("[PIPELINE][T-141] DCS 등급 체크 실패 (graceful skip): %s", exc)
```

차단 흐름 (run_desk2 내):
1. AxisMaskEngine 5축 마스크 체크 (T-140)
2. DcsEvaluator C등급 체크 (T-141) ← 신규
3. Desk2Filter 컨디션 평가

### Step 7: 테스트 작성 및 실행
파일: /root/kis-autotrade-v4/tests/test_dcs_evaluator.py
테스트 20건 작성

테스트 실행 결과:
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
collected 20 items

tests/test_dcs_evaluator.py::test_tc01_empty_history_grade_c PASSED      [  5%]
tests/test_dcs_evaluator.py::test_tc02_grade_a_exact_boundary PASSED     [ 10%]
tests/test_dcs_evaluator.py::test_tc03_a_miss_positive_ratio PASSED      [ 15%]
tests/test_dcs_evaluator.py::test_tc04_a_miss_dcs PASSED                 [ 20%]
tests/test_dcs_evaluator.py::test_tc05_grade_b_exact_boundary PASSED     [ 25%]
tests/test_dcs_evaluator.py::test_tc06_grade_c PASSED                    [ 30%]
tests/test_dcs_evaluator.py::test_tc07_c_grade_is_blocked PASSED         [ 35%]
tests/test_dcs_evaluator.py::test_tc08_a_grade_not_blocked PASSED        [ 40%]
tests/test_dcs_evaluator.py::test_tc09_b_grade_not_blocked PASSED        [ 45%]
tests/test_dcs_evaluator.py::test_tc10_allocation_grade_a PASSED         [ 50%]
tests/test_dcs_evaluator.py::test_tc11_allocation_grade_b PASSED         [ 55%]
tests/test_dcs_evaluator.py::test_tc12_allocation_grade_c PASSED         [ 60%]
tests/test_dcs_evaluator.py::test_tc13_daily_dcs_positive PASSED         [ 65%]
tests/test_dcs_evaluator.py::test_tc14_daily_dcs_negative PASSED         [ 70%]
tests/test_dcs_evaluator.py::test_tc15_daily_dcs_multi_trades PASSED     [ 75%]
tests/test_dcs_evaluator.py::test_tc16_rebalance_all_no_db PASSED        [ 80%]
tests/test_dcs_evaluator.py::test_tc17_param_override_grade_a_threshold PASSED [ 85%]
tests/test_dcs_evaluator.py::test_tc18_negative_dcs_grade_c PASSED       [ 90%]
tests/test_dcs_evaluator.py::test_tc19_dcs_exactly_b_lower_boundary PASSED [ 95%]
tests/test_dcs_evaluator.py::test_tc20_dcs_exactly_a_lower_boundary PASSED [100%]

============================== 20 passed in 0.61s ==============================
```
→ 20/20 ALL PASS

### Step 8: Git Commit
```
git add backend/app/services/desk2_conditions/dcs_evaluator.py
        backend/app/services/desk_filters/pipeline.py
        config/param_search_space.yaml
        backend/migrations/066_v4_desk2_dcs_history.sql
        tests/test_dcs_evaluator.py
git commit -m "[V4.1] T-141: D-010 DCS 등급체계 A/B/C 구현"

[phase-2c-command-center 24496f74] [V4.1] T-141: D-010 DCS 등급체계 A/B/C 구현
 5 files changed, 895 insertions(+)
 create mode 100644 backend/app/services/desk2_conditions/dcs_evaluator.py
 create mode 100644 backend/migrations/066_v4_desk2_dcs_history.sql
 create mode 100644 tests/test_dcs_evaluator.py
```

### Step 9: 보고서 생성
파일: /root/kis-autotrade-v4/report/v41/CUR-V41-DESK2-DCS-GRADE-001-20260305.md
→ 생성 완료

---

## 최종 결과 요약

| 항목 | 결과 |
|------|------|
| YAML desk2_dcs 섹션 | ✅ 추가 완료 |
| DcsEvaluator 클래스 (4메서드) | ✅ 신규 생성 |
| DB 마이그레이션 066 | ✅ 신규 생성 |
| pipeline.py C등급 차단 | ✅ 연동 완료 |
| 테스트 20건 | ✅ 20/20 ALL PASS |
| git commit | ✅ 24496f74 |
| 보고서 | ✅ 생성 완료 |

## 완료 기준 달성 확인
- [x] DCS 계산: calculate_daily_dcs() 작동
- [x] 등급 자동 분류: A/B/C 판정 정확
- [x] C등급 차단: pipeline.run_desk2() 통합 완료
- [x] 코드 레포 커밋 완료 (24496f74, phase-2c-command-center)
- [ ] project-docs 보고서 push (done_watcher.sh 자동 처리 예정)
