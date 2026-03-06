---
project: kis-autotrade-v4
task_id: T-125
completed_at: 2026-03-05 19:45 KST
---

# T-125 RESULT: DESK2 멀티컨디션 Phase A — C2(D4)/C1(D6)/C6(D7)

## 실행 요약

지시서: KIS_20260305_190330_BRIDGE.md
완료 상태: 코드 구현 + 테스트 20/20 ALL PASS + 로컬 커밋 완료
SSH 제약: claudebot은 git push 불가 (root 수행 필요)

---

## 1. 사전 작업 (백업)

```
$ cp -r backend/app/services/desk_filters backend/app/services/desk_filters.bak.20260305_1940
$ cp config/param_search_space.yaml config/param_search_space.yaml.bak.20260305_1940
Backups created successfully
```

---

## 2. config/param_search_space.yaml — desk2_conditions 섹션 추가

파일 끝에 아래 내용 추가:

```yaml
# ────────────────────────────────────────────────────────────
# T-125: DESK2 멀티컨디션 Phase A — D4/D6/D7 컨디션 파라미터
# CEO D-010/D-011 DESK2 멀티컨디션 엔진
# C2(D4전상눌림) / C1(D6상따갭) / C6(D7종가배팅갭)
# ────────────────────────────────────────────────────────────
desk2_conditions:
  c2_prev_ul:                    # C2: 전일 상한가 (D4용)
    ul_pct_min: 29.0
    next_day_ma20_1m_break: true
    timeout_minutes: 60
    sl_pct: 2.0
    tp_pct: 3.0
  c1_ul_expected:                # C1: 상한가 예상 (D6용)
    ul_entry_before: "11:00"
    bid_amount_min: 10000000000  # 100억
    sl_pct: 1.0                  # 시간외 -1%
    tp_pct: 0.0                  # 시간외 매도
  c6_close_strong:               # C6: 종가 강세 (D7용)
    entry_after: "14:30"
    close_bet_conditions:
      supply_focus: true          # 수급 집중
      low_rising: true            # 저점 상승
      volume_increase: true       # 거래량 증가
    sl_pct: 1.5
    next_day_open_sell: true
```

결과: desk2_conditions section appended ✅

---

## 3. backend/app/services/desk2_conditions/ 패키지 생성

### 3-1. 디렉토리 생성
```
$ mkdir -p /root/kis-autotrade-v4/backend/app/services/desk2_conditions
Directory created ✅
```

### 3-2. 생성된 파일 목록 (6파일)

```
backend/app/services/desk2_conditions/
├── __init__.py              (패키지 노출)
├── base_condition.py        (BaseCondition ABC + YAML 로더)
├── c2_prev_ul.py            (C2PrevULCondition — 전일 상한가 + MA20 돌파)
├── c1_ul_expected.py        (C1ULExpectedCondition — 상한가 예상 + 매수잔량)
├── c6_close_strong.py       (C6CloseStrongCondition — 종가 강세 3조건 AND)
├── condition_registry.py    (ConditionRegistry — 등록/evaluate_all)
└── signal_matcher.py        (SignalMatcher — D-011 Top5 매칭)
```

### 3-3. 각 파일 구현 내용

**__init__.py**: 6 클래스 노출 (BaseCondition, C2PrevULCondition, C1ULExpectedCondition, C6CloseStrongCondition, ConditionRegistry, SignalMatcher)

**base_condition.py**:
- `_load_yaml_params()`: param_search_space.yaml 캐싱 로더
- `get_condition_param(condition_key, param, default)`: 개별 파라미터 조회
- `class BaseCondition(ABC)`: condition_key / param_override 생성자
  - `p(param, default)`: 파라미터 조회
  - `evaluate(symbol, date, **kwargs) -> dict` [abstract]
  - `backtest_signal(symbol, date, ohlcv_1m) -> dict` [abstract]
  - `get_params() -> dict`: 현재 파라미터 반환

**c2_prev_ul.py** — C2PrevULCondition:
- CONDITION_ID = "C2", DESK_TARGET = "D4"
- `evaluate(symbol, date, prev_open, prev_close, ohlcv_1m=[])`
  - prev_close >= prev_open × 1.29 → 상한가 판별
  - `_detect_ma20_break(ohlcv_1m)` → 1분봉 MA20 돌파 감지
  - timeout_minutes=60 이내만 triggered=True
- `_detect_ma20_break(ohlcv_1m)` → (bool, time_str)
  - 버그 수정: `closes[i-1] <= ma20` 방식 (i=20에서 빈 슬라이스 방지)
- `backtest_signal(symbol, date, ohlcv_1m)`: SL/TP/timeout 기반 PnL 계산

**c1_ul_expected.py** — C1ULExpectedCondition:
- CONDITION_ID = "C1", DESK_TARGET = "D6"
- `evaluate(symbol, date, current_time, bid_amount, is_upper_limit=False)`
  - current_time < "11:00" AND bid_amount >= 100억
  - `_is_before(current_time, deadline)` 정적 메서드
- `backtest_signal(symbol, date, ohlcv_1m)`: ul_entry_before 이전 바 진입

**c6_close_strong.py** — C6CloseStrongCondition:
- CONDITION_ID = "C6", DESK_TARGET = "D7"
- `evaluate(symbol, date, current_time, supply_focus, low_rising, volume_increase)`
  - current_time >= "14:30" AND (supply_focus AND low_rising AND volume_increase)
  - close_bet_conditions YAML 설정으로 조건 on/off 가능
  - `_is_after_or_equal(current_time, target)` 정적 메서드
- `backtest_signal(symbol, date, ohlcv_1m)`: entry_after 이후 바 진입

**condition_registry.py** — ConditionRegistry:
- `register(condition_id, condition_instance)`: 인스턴스 등록
- `register_class(condition_id, condition_class, param_override)`: 클래스→인스턴스화 후 등록
- `evaluate_all(symbol, date, **kwargs) -> List[dict]`: 전체 평가, triggered 목록 반환
- `evaluate_single(condition_id, symbol, date, **kwargs) -> dict|None`
- `get_active_conditions() -> List[str]`
- `build_default_registry(param_overrides)`: C2/C1/C6 기본 레지스트리 생성

**signal_matcher.py** — SignalMatcher:
- D-011 기준 컨디션→시그널 매핑:
  - C1 → ["TS-D1", "TS-B1"] (D6 PF13.63 ★최우선)
  - C2 → ["TS-B4", "TS-C3"] (D4 PF2.43)
  - C6 → ["TS-C1"]           (D7 PF2.12)
- 시장 상태별 보너스: bull(TS-D1+0.2, TS-B4+0.1), bear(TS-B1+0.2, TS-C3+0.1), sideways(TS-C1+0.1, TS-B1+0.1)
- `match_signal(condition_id, market_state) -> str`: 최적 시그널 반환
- `match_all(triggered_conditions, market_state) -> dict`
- `get_top5_priority(market_state) -> List[dict]`

---

## 4. tests/unit/test_desk2_conditions.py (20개 테스트)

생성 위치: /root/kis-autotrade-v4/tests/unit/test_desk2_conditions.py

테스트 목록:
- TC-01: test_c2_upper_limit_true — 전일 상한가 판별 True
- TC-02: test_c2_upper_limit_false — 전일 상한가 판별 False (10% 상승)
- TC-03: test_c2_ma20_break_detected — 1분봉 MA20 돌파 감지 (버그 수정 후 PASS)
- TC-04: test_c2_missing_data_fallback — 데이터 없을 때 graceful fallback
- TC-05: test_c1_upper_limit_with_bid_true — 11:00 이전 + 150억 → True
- TC-06: test_c1_time_filter_after_11 — 11:30 → False
- TC-07: test_c1_insufficient_bid_amount — 50억 → False
- TC-08: test_c6_close_strong_all_conditions_true — 14:45 + 3조건 모두 True
- TC-09: test_c6_time_filter_before_1430 — 13:00 → False
- TC-10: test_c6_partial_conditions_false — volume_increase=False → False
- TC-11: test_condition_registry_register_and_evaluate — Registry C1/C2/C6 등록/evaluate_all
- TC-12: test_signal_matcher_basic — C1→TS-D1, C2→TS-B4, C6→TS-C1
- TC-13: test_condition_params_yaml_load — YAML 파라미터 로드 (ul_pct_min=29.0, bid_min=100억, entry_after="14:30")
- TC-14: test_five_axis_time_mask_structure — 5축 마스크 T1~T6 시간대 검증
- TC-15: test_dcs_daily_sum_structure — DCS 일일합산 (confidence 합산 ≥ 0.0)
- TC-16: test_signal_matcher_top5_and_match_all — Top5 내림차순 + match_all
- TC-17: test_c2_get_params_structure — get_params 딕셔너리 구조 확인
- TC-18: test_registry_evaluate_single_missing — 미등록 컨디션 None 반환
- TC-19: test_c1_backtest_signal_basic — 빈 bars → triggered=False
- TC-20: test_c6_backtest_signal_basic — 14:30 이후 바 포함 → triggered=True

---

## 5. pytest 실행 결과

### 1차 실행 (TC-03 실패)
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
asyncio: mode=Mode.AUTO

FAILED tests/unit/test_desk2_conditions.py::test_c2_ma20_break_detected
 - AssertionError: assert False is True
  (원인: i=20에서 closes[-1:19] 빈 슬라이스 → prev_ma20=0.0 → 10000<=0.0 False)

1 failed, 19 passed
```

### 버그 수정
파일: backend/app/services/desk2_conditions/c2_prev_ul.py
변경:
```python
# 변경 전
if bar["close"] > ma20 and ohlcv_1m[i - 1]["close"] <= (
    sum(closes[i - 21:i - 1]) / 20
):
# 변경 후
if bar["close"] > ma20 and closes[i - 1] <= ma20:
```

### 2차 실행 (ALL PASS)
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 20 items

tests/unit/test_desk2_conditions.py::test_c2_upper_limit_true PASSED     [  5%]
tests/unit/test_desk2_conditions.py::test_c2_upper_limit_false PASSED    [ 10%]
tests/unit/test_desk2_conditions.py::test_c2_ma20_break_detected PASSED  [ 15%]
tests/unit/test_desk2_conditions.py::test_c2_missing_data_fallback PASSED [ 20%]
tests/unit/test_desk2_conditions.py::test_c1_upper_limit_with_bid_true PASSED [ 25%]
tests/unit/test_desk2_conditions.py::test_c1_time_filter_after_11 PASSED [ 30%]
tests/unit/test_desk2_conditions.py::test_c1_insufficient_bid_amount PASSED [ 35%]
tests/unit/test_desk2_conditions.py::test_c6_close_strong_all_conditions_true PASSED [ 40%]
tests/unit/test_desk2_conditions.py::test_c6_time_filter_before_1430 PASSED [ 45%]
tests/unit/test_desk2_conditions.py::test_c6_partial_conditions_false PASSED [ 50%]
tests/unit/test_desk2_conditions.py::test_condition_registry_register_and_evaluate PASSED [ 55%]
tests/unit/test_desk2_conditions.py::test_signal_matcher_basic PASSED    [ 60%]
tests/unit/test_desk2_conditions.py::test_condition_params_yaml_load PASSED [ 65%]
tests/unit/test_desk2_conditions.py::test_five_axis_time_mask_structure PASSED [ 70%]
tests/unit/test_desk2_conditions.py::test_dcs_daily_sum_structure PASSED [ 75%]
tests/unit/test_desk2_conditions.py::test_signal_matcher_top5_and_match_all PASSED [ 80%]
tests/unit/test_desk2_conditions.py::test_c2_get_params_structure PASSED [ 85%]
tests/unit/test_desk2_conditions.py::test_registry_evaluate_single_missing PASSED [ 90%]
tests/unit/test_desk2_conditions.py::test_c1_backtest_signal_basic PASSED [ 95%]
tests/unit/test_desk2_conditions.py::test_c6_backtest_signal_basic PASSED [100%]

============================== 20 passed in 0.14s ==============================
```

---

## 6. git commit

```
$ git add \
  config/param_search_space.yaml \
  backend/app/services/desk2_conditions/__init__.py \
  backend/app/services/desk2_conditions/base_condition.py \
  backend/app/services/desk2_conditions/c2_prev_ul.py \
  backend/app/services/desk2_conditions/c1_ul_expected.py \
  backend/app/services/desk2_conditions/c6_close_strong.py \
  backend/app/services/desk2_conditions/condition_registry.py \
  backend/app/services/desk2_conditions/signal_matcher.py \
  tests/unit/test_desk2_conditions.py

$ git commit -m "[V4.1] T-125: DESK2 멀티컨디션 Phase A — C2(D4)/C1(D6)/C6(D7)
..."

[phase-2c-command-center bca18a1e] [V4.1] T-125: DESK2 멀티컨디션 Phase A — C2(D4)/C1(D6)/C6(D7)
 9 files changed, 1389 insertions(+)
 create mode 100644 backend/app/services/desk2_conditions/__init__.py
 create mode 100644 backend/app/services/desk2_conditions/base_condition.py
 create mode 100644 backend/app/services/desk2_conditions/c1_ul_expected.py
 create mode 100644 backend/app/services/desk2_conditions/c2_prev_ul.py
 create mode 100644 backend/app/services/desk2_conditions/c6_close_strong.py
 create mode 100644 backend/app/services/desk2_conditions/condition_registry.py
 create mode 100644 backend/app/services/desk2_conditions/signal_matcher.py
 create mode 100644 tests/unit/test_desk2_conditions.py
```

커밋 해시: **bca18a1e**

---

## 7. git push (SSH 권한 제약 — root 수행 필요)

```
$ git push origin phase-2c-command-center
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

claudebot은 SSH 키 접근 불가. root에서 수행 필요:

```bash
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center
```

---

## 8. 보고서 생성

로컬 보고서 경로: `/root/kis-autotrade-v4/report/v41/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md`
생성 완료 ✅

project-docs 보고서 경로: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md`
→ root 수행 필요:

```bash
cp /root/kis-autotrade-v4/report/v41/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md \
   /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md
cd /root/project-docs
git add -A
git commit -m "[DOCS] T-125 DESK2 멀티컨디션 Phase A 보고서"
git push origin master
curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md"
```

---

## 9. HANDOVER.md 업데이트 (root 수행 필요)

/root/project-docs/kis-autotrade-v4/HANDOVER.md에 아래 내용 추가:

### 섹션 2 "완료된 작업" 테이블에 추가할 행:
```
| **T-125 DESK2 멀티컨디션 Phase A** | 03-05 | bca18a1e | — | desk2_conditions 패키지 6파일(base_condition/c2_prev_ul/c1_ul_expected/c6_close_strong/condition_registry/signal_matcher), C2(D4전상눌림)/C1(D6상따갭)/C6(D7종가배팅갭) 3컨디션, ConditionRegistry(등록/evaluate_all), SignalMatcher(D-011 Top5 매칭), YAML desk2_conditions 섹션, 20테스트 ALL PASS |
```

### 섹션 6 "웹 Claude 인수인계 사항" 업데이트:
최신 상태 헤더를:
```
### 최신 상태 (2026-03-05, T-125 DESK2 멀티컨디션 Phase A — v10.8)
```
으로 변경하고 아래 내용 추가:
```
#### ★ T-125 완료: DESK2 멀티컨디션 Phase A

**[T-125 CUR-V41-DESK2-MULTICOND-PHASE-A-001] desk2_conditions 패키지 구현**
- **패키지**: `backend/app/services/desk2_conditions/` (6파일)
- **C2PrevULCondition** (D4 전상눌림): 전일 종가 ≥ 시가×1.29 + 1분봉 MA20 돌파
- **C1ULExpectedCondition** (D6 상따갭): 오전 < 11:00 + 매수잔량 ≥ 100억
- **C6CloseStrongCondition** (D7 종가배팅갭): 14:30 이후 + 수급집중/저점상승/거래량증가 AND
- **ConditionRegistry**: register/evaluate_all/evaluate_single/get_active_conditions/build_default_registry
- **SignalMatcher**: D-011 기준 C1→TS-D1, C2→TS-B4, C6→TS-C1 매칭
- **YAML**: `config/param_search_space.yaml` desk2_conditions 섹션 (C2/C1/C6 파라미터)
- **테스트**: 20건 ALL PASS (`tests/unit/test_desk2_conditions.py`)
- **커밋**: bca18a1e (phase-2c-command-center), push 미완료 (root SSH 필요)
```

### 버전 이력에 추가:
```
| v10.8 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-125 DESK2 멀티컨디션 Phase A**: desk2_conditions 패키지 6파일(BaseCondition ABC/C2PrevULCondition/C1ULExpectedCondition/C6CloseStrongCondition/ConditionRegistry/SignalMatcher), D-011 기준 C1(D6 PF13.63)>C2(D4 PF2.43)>C6(D7 PF2.12) 우선순위, YAML desk2_conditions 섹션, 20테스트 ALL PASS, 커밋 bca18a1e |
```

HANDOVER.md 업데이트 후 push:
```bash
cd /root/project-docs
git add kis-autotrade-v4/HANDOVER.md
git commit -m "docs: HANDOVER 업데이트 (T-125 완료)"
git push origin master
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md
```

---

## 10. 완료 조건 체크

- [x] desk2_conditions 패키지 6파일 생성
- [x] C2/C1/C6 컨디션 3개 구현 (evaluate + backtest_signal + get_params)
- [x] ConditionRegistry 구현 (register/evaluate_all/get_active_conditions)
- [x] SignalMatcher 구현 (match_signal/match_all/get_top5_priority)
- [x] 20개 테스트 ALL PASS (요구: 12+)
- [x] git commit bca18a1e
- [ ] git push origin phase-2c-command-center → root 수행 필요
- [ ] project-docs 보고서 push → root 수행 필요
- [ ] HANDOVER.md 갱신 + push → root 수행 필요

---

## 11. 핵심 발견

1. D-011 C1(D6 PF13.63) 최우선: TS-D1(미니갭) + bull 시장 조합 최고 점수(1.05)
2. C2 MA20 돌파 감지 버그: `closes[i-21:i-1]` 슬라이스가 `i=20`에서 빈 배열 → `closes[i-1] <= ma20` 단순화로 해결
3. ConditionRegistry graceful fallback: 각 컨디션 오류를 try/except로 잡아 전체 평가 중단 방지
4. 5축 마스크 T6(14:30~15:30): C6(D7)는 T6 시간대에서만 활성화
5. DCS 일일합산: triggered 컨디션 confidence의 합산이 일일 강도 측정 지표

---

## 12. 생성/수정된 파일 전체 목록

```
수정:
- config/param_search_space.yaml (desk2_conditions 섹션 추가)

신규 생성:
- backend/app/services/desk2_conditions/__init__.py
- backend/app/services/desk2_conditions/base_condition.py
- backend/app/services/desk2_conditions/c2_prev_ul.py
- backend/app/services/desk2_conditions/c1_ul_expected.py
- backend/app/services/desk2_conditions/c6_close_strong.py
- backend/app/services/desk2_conditions/condition_registry.py
- backend/app/services/desk2_conditions/signal_matcher.py
- tests/unit/test_desk2_conditions.py
- report/v41/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md

백업 (.bak, 커밋 제외):
- backend/app/services/desk_filters.bak.20260305_1940/
- config/param_search_space.yaml.bak.20260305_1940
```

---

RESULT 파일 저장 완료: 2026-03-05 19:45 KST
커밋: bca18a1e
브랜치: phase-2c-command-center
