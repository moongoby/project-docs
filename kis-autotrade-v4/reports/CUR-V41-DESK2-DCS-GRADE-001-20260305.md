# T-141: D-010 DCS 일일합산 + 컨디션 등급체계(A/B/C)

[인계 확인]
직전 완료: T-140 (DESK2 5축 운영 마스크 AxisMaskEngine)
현재 단계: Phase 2C — Command Center
CEO 지시 적용: D-010 (DESK2 멀티컨디션 엔진, DCS 생애주기)
strategy_cards: 확인 불가 (DB 직접 조회 권한 없음)
open_positions: 확인 불가 (DB 직접 조회 권한 없음)

---

## 개요
- 작업 ID: T-141
- 서버: 211 (kis-autotrade-v4)
- 브랜치: phase-2c-command-center
- 커밋: 24496f74
- 완료 시각: 2026-03-05 21:57 KST
- 우선순위: P1-HIGH

## 목적
CEO D-010 핵심 — DCS(Daily Condition Score) 일일합산 평가 시스템과 A/B/C 등급 자동 리밸런싱 구현.
DESK2 컨디션(C1/C2/C6 등)에 생애주기 등급을 부여하여 C등급 컨디션의 진입을 자동 차단.

---

## 구현 내용

### 1. YAML 파라미터 추가 (param_search_space.yaml)
```yaml
desk2_dcs:
  evaluation_window: 20  # 거래일
  grade_a: { min_dcs_pct: 2.0, min_positive_ratio: 0.6, allocation: 0.4 }
  grade_b: { min_dcs_pct: 0.5, min_positive_ratio: 0.5, allocation: 0.1 }
  grade_c: { allocation: 0.0 }  # 시뮬만
  rebalance_interval: 20  # 거래일
```

### 2. DcsEvaluator 클래스 신규 (dcs_evaluator.py)

**파일**: `backend/app/services/desk2_conditions/dcs_evaluator.py`

| 메서드 | 기능 |
|--------|------|
| `calculate_daily_dcs(condition_id, date, pnl_rows)` | 컨디션 일일 수익률 합산 → v4_desk2_dcs_history UPSERT |
| `evaluate_grade(condition_id, as_of, history_rows)` | 20일 윈도우 DCS%+양일비율 → A/B/C 등급 판정 |
| `get_allocation(condition_id, as_of, history_rows)` | 등급별 자금 배분율 반환 (A=40%, B=10%, C=0%) |
| `is_blocked(condition_id, as_of, history_rows)` | C등급 여부 판단 (pipeline 연동용) |
| `rebalance_all(condition_ids, as_of)` | 전 컨디션 일괄 재평가 |

**등급 분류 로직**:
- A등급: DCS ≥ +2.0% AND 양일비율 ≥ 60% → 실전 40% 배분
- B등급: DCS ≥ +0.5% AND 양일비율 ≥ 50% → 소규모 10% 배분
- C등급: 그 외 → 시뮬만, 0% 배분 (진입 차단)

**설계 특징**:
- `history_rows` 외부 주입 지원 → DB 없는 단위테스트 가능
- `pnl_rows` 외부 주입 지원 → calculate_daily_dcs 단위테스트 가능
- DB 연결 실패 시 graceful degradation (경고 로그만 출력, 예외 미전파)
- `param_override` 지원 → 백테스트 파라미터 그리드 탐색 가능

### 3. DB 마이그레이션 (066_v4_desk2_dcs_history.sql)

**파일**: `backend/migrations/066_v4_desk2_dcs_history.sql`

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
```
- 인덱스: condition_id+date DESC, grade+date DESC, date DESC
- ALTER 금지 원칙 준수 — 신규 테이블만 생성

### 4. pipeline.py 연동 (C등급 자동 차단)

**위치**: `backend/app/services/desk_filters/pipeline.py` → `run_desk2()` 내부

```python
# T-141: DCS 등급 C → 진입 차단
condition_id = data.get("condition_id")
if condition_id:
    dcs_eval = _get_dcs_evaluator()
    if dcs_eval is not None:
        try:
            if dcs_eval.is_blocked(condition_id):
                return {
                    "stock_code": stock_code,
                    "desk_level": 2,
                    "pass": False,
                    "score": 0.0,
                    "reason": "dcs_grade_c_block",
                    ...
                }
        except Exception as exc:
            logger.warning("[PIPELINE][T-141] DCS 등급 체크 실패 (graceful skip): %s", exc)
```

**차단 흐름**:
1. AxisMaskEngine 5축 마스크 체크 (T-140)
2. DcsEvaluator C등급 체크 (T-141) ← **신규**
3. Desk2Filter 컨디션 평가
- `condition_id`가 data에 없으면 차단 스킵 (하위 호환)
- DcsEvaluator 로드 실패 시 비활성화 (graceful degradation)

---

## 테스트 결과

**파일**: `tests/test_dcs_evaluator.py`

| TC | 검증 항목 | 결과 |
|----|-----------|------|
| TC-01 | 빈 히스토리 → C등급 | PASS |
| TC-02 | A등급 경계 정확 충족 (DCS=2.0, 양일비율=0.6) | PASS |
| TC-03 | A등급 미충족 — 양일비율 부족 → B등급 | PASS |
| TC-04 | A등급 미충족 — DCS 부족 → B등급 | PASS |
| TC-05 | B등급 경계 정확 충족 (DCS=0.5, 양일비율=0.5) | PASS |
| TC-06 | B등급 미충족 → C등급 | PASS |
| TC-07 | C등급 → is_blocked() True | PASS |
| TC-08 | A등급 → is_blocked() False | PASS |
| TC-09 | B등급 → is_blocked() False | PASS |
| TC-10 | get_allocation A등급 → 0.4 | PASS |
| TC-11 | get_allocation B등급 → 0.1 | PASS |
| TC-12 | get_allocation C등급 → 0.0 | PASS |
| TC-13 | calculate_daily_dcs 양일 | PASS |
| TC-14 | calculate_daily_dcs 음일 | PASS |
| TC-15 | calculate_daily_dcs 합산 정확성 (3거래) | PASS |
| TC-16 | rebalance_all 여러 컨디션 일괄 반환 | PASS |
| TC-17 | param_override grade_a 임계값 변경 | PASS |
| TC-18 | 음수 DCS → C등급 | PASS |
| TC-19 | DCS = 0.5 정확히 (B 하한 경계) | PASS |
| TC-20 | DCS = 2.0 정확히 (A 하한 경계) | PASS |

**최종: 20/20 ALL PASS**

---

## 변경 파일 목록

| 파일 | 변경 종류 |
|------|-----------|
| `backend/app/services/desk2_conditions/dcs_evaluator.py` | 신규 |
| `backend/migrations/066_v4_desk2_dcs_history.sql` | 신규 |
| `tests/test_dcs_evaluator.py` | 신규 |
| `config/param_search_space.yaml` | desk2_dcs 섹션 추가 |
| `backend/app/services/desk_filters/pipeline.py` | DCS C등급 차단 추가 |

---

## 완료 기준 달성 확인

- [x] DCS 일일합산 계산: `calculate_daily_dcs()` 구현
- [x] 등급 자동 분류: `evaluate_grade()` A/B/C 판정
- [x] C등급 차단: `is_blocked()` + `pipeline.run_desk2()` 통합
- [x] DB 테이블: `v4_desk2_dcs_history` (066 마이그레이션)
- [x] 리밸런싱: `rebalance_all()` 전 컨디션 재평가
- [x] 테스트 20건 ALL PASS
- [x] git commit: 24496f74

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK2-DCS-GRADE-001-20260305.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DESK2-DCS-GRADE-001-20260305.md
- 커밋: (project-docs push는 done_watcher.sh가 처리)
- HTTP 확인: (push 후 확인)
- HANDOVER 업데이트: (done_watcher.sh 처리)
