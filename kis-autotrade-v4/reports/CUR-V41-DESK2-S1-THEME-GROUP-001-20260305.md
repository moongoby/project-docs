# CUR-V41-DESK2-S1-THEME-GROUP-001

[인계 확인]
직전 완료: T-142
현재 단계: Phase C (D-010 VE-003)
CEO 지시 적용: D-010, D-011
strategy_cards: 60
open_positions: 14

---

## 태스크 정보
- **Task ID**: T-143
- **제목**: D-010 Phase C — 테마/섹터 그룹핑 + S1 연계
- **날짜**: 2026-03-05
- **우선순위**: P1-HIGH
- **의존성**: 없음

---

## 작업 목적
CEO D-010 VE-003 Phase C — D3(폐기 확정)/S1(조건부 채택 PF 1.44)/S2(폐기) 중
S1 거래대금 폭발 후 눌림 전략의 테마/섹터 그룹핑 엔진 구현.

---

## 구현 내용

### 1. YAML desk2_theme_group 섹션 추가
파일: `config/param_search_space.yaml`

```yaml
desk2_theme_group:
  s1_volume_explosion:
    lookback_days: 10            # 거래대금 폭발 탐지 기간 (10일)
    min_trade_amount: 50000000000  # 최소 거래대금 500억
    min_price_surge: 10.0        # 최소 급등 기준 +10%
    theme_alive_min_days: 5      # 테마 유효 최소 기간
    pullback_ma20_support: true  # MA20 지지 확인 필수
    sl_pct: 2.0                  # 손절 -2%
    tp_pct: 4.0                  # 익절 +4%
    timeout_minutes: 60          # 보유 타임아웃 60분
  sector_grouping:
    min_sector_stocks: 2         # 동일섹터 최소 종목수
    comovement_correlation: 0.6  # 동행 상관계수 기준
    leader_follower_lag: 3       # 대장 후 3일 내 후발 진입
    sector_table: v4_sector_mapping
    theme_table: v4_theme_mapping
```

### 2. 신규 파일: c_s1_volume_pullback.py
경로: `backend/app/services/desk2_conditions/c_s1_volume_pullback.py`

#### 클래스: CS1VolumePullbackCondition
- `CONDITION_ID = "CS1"`, `DESK_TARGET = "S1"`
- `evaluate()`: 4단계 판정
  1. 거래대금 폭발 감지 (`_detect_volume_explosion`)
  2. 눌림 구간 확인 (`_check_pullback`, 3~25% 범위)
  3. MA20 지지 확인 (`_check_ma20_support`, 0~+5% 범위)
  4. 테마/섹터 그룹핑 (`evaluate_sector_grouping`)
- `evaluate_sector_grouping()`: v4_sector_mapping, v4_theme_mapping 연동
  - 대장-후발 lag 3일 내 → sector_leader_follower
  - 섹터만 → sector
  - 테마만 → theme
- `get_x9_signal_point()`: CTE 파이프라인 X9 연계 표준 형식 반환
  - `sector_boost`: 0.15 (leader_follower) / 0.10 (sector) / 0.08 (sector_only)
  - `theme_boost`: 0.05
- `backtest_signal()`: 1분봉 백테스트 (SL 2% / TP 4% / timeout 60분)

#### 신뢰도 계산 (0~1.0)
| 요소 | 가중치 |
|------|--------|
| 거래대금 배수 (500억 기준, 최대 3배) | 0.4 |
| 급등 강도 (10% 기준, 최대 3배) | 0.3 |
| MA20 밀착도 (거리 최소) | 0.2 |
| 그룹 보너스 | 0.1 |

### 3. condition_registry.py 업데이트
- `build_default_registry()`에 CS1 추가
- 등록 컨디션: C2, C1, C6, CS1 (4개)

### 4. __init__.py 업데이트
- `CS1VolumePullbackCondition` 노출 추가
- T-143 Phase C 설명 추가

### 5. pipeline.py X9 연계 포인트
경로: `backend/app/services/desk_filters/pipeline.py`

`run_desk2()` 내부에 T-143 연계 블록 추가:
- `data['condition_id'] == 'CS1'` && `data['ohlcv_daily']` 있을 때 CS1 평가
- `result['cs1_evaluate']` = 평가 결과
- `result['x9_signal_point']` = X9 연계 포인트
- `result['score']` += `sector_boost + theme_boost`
- graceful degradation (예외 시 스킵)

---

## 테스트 결과

```
tests/desk2_conditions/test_cs1_volume_pullback.py::test_cs1_instantiation PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_detect_volume_explosion_found PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_detect_volume_explosion_not_found PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_check_ma20_support_ok PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_check_ma20_support_fail PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_check_pullback_in_range PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_evaluate_triggered_true PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_evaluate_no_ohlcv PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_sector_grouping_leader_follower PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_sector_grouping_lag_exceeded PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_get_x9_signal_point_format PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_registry_includes_cs1 PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_backtest_signal_basic PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_backtest_signal_empty PASSED
tests/desk2_conditions/test_cs1_volume_pullback.py::test_sector_grouping_theme_only PASSED

15 passed in 0.16s
```

**15/15 ALL PASS**

---

## 변경 파일 목록
| 파일 | 변경 유형 |
|------|---------|
| `config/param_search_space.yaml` | 수정 (desk2_theme_group 섹션 추가) |
| `backend/app/services/desk2_conditions/c_s1_volume_pullback.py` | 신규 |
| `backend/app/services/desk2_conditions/condition_registry.py` | 수정 (CS1 등록 추가) |
| `backend/app/services/desk2_conditions/__init__.py` | 수정 (CS1 노출 추가) |
| `backend/app/services/desk_filters/pipeline.py` | 수정 (T-143 X9 연계 포인트) |
| `tests/desk2_conditions/test_cs1_volume_pullback.py` | 신규 (15개 테스트) |

---

## 완료 기준 달성 확인
- [x] S1 컨디션 구현 (CS1VolumePullbackCondition)
- [x] 테마/섹터 그룹핑 작동 (evaluate_sector_grouping)
- [x] pipeline 연동 (run_desk2 T-143 X9 연계)
- [x] 15/15 테스트 ALL PASS

---

## 체크포인트
- [x] 코드 레포 커밋 완료 (kis-autotrade-v4)
- [ ] project-docs 보고서 push 완료 (done_watcher.sh 자동 처리)
