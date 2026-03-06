---
project: kis-autotrade-v4
task_id: T-161
completed_at: 2026-03-06T10:35:00+09:00
---

# KIS_20260306_101134_BRIDGE_RESULT.md
# T-161: D-010 C7 NEW종목 실시간 탐지 구현 + DESK2 Phase B 완성

## 지시서 원문

Task ID: T-161 제목: D-010 C7 NEW종목 실시간 탐지 구현 + DESK2 Phase B 완성 서버: 211 (kis-autotrade-v4) 우선순위: P0-CRITICAL 예상 시간: 20분 의존성: T-156 (C3/C4/C5 완료)

■ 목적: DESK2 멀티컨디션 7대 조건 중 마지막 C7(NEW 종목 탐지)을 구현하여 D-010 Phase B를 완성한다.

■ 작업 내용

【C7 – NEW 종목 실시간 탐지 (NewStockDetect)】 파일: backend/app/services/desk2_conditions/c7_new_stock_detect.py (신규)

CEO-DIRECTIVES D-009/D-011 기준 4조건:

가격 급등: 현재가 ≥ 당일시가 × 1.05 (5%+) 또는 전일종가 대비 +10%
체결강도: VP ≥ 120 (3분 이상 지속)
이평선 정배열: 1분봉 MA5 > MA10 > MA20
RSI: 30~50 구간 반등 (RSI_14 기준)

추가 조건 (D-006, D-008-KR 반영):

상장 60일 이내 종목 가산점 (IPO 후 첫 눌림 패턴)
거래대금 30억 이상
v4_ohlcv_minute 기반 실시간 계산

출력: score (0~1), is_triggered (bool), details (dict with conditions_met, volume_amount, vp, rsi, ma_aligned)

【통합 작업】

desk2_conditions/init.py에 C7 추가
condition_registry.py에 C7 등록 (총 8개: C1/C2/C3/C4/C5/C6/C7/CS1)
signal_matcher.py에 C7 시그널 매핑 추가 (D-011 기준: TS-B4 거래량폭발양봉, TS-B1 RSI30~50)
desk2_multi_condition_matcher.py CONDITION_BITS에 C7=128 추가

【테스트】 tests/test_c7_new_stock_detect.py (9개 이상):

TC1: 4조건 충족 → triggered=True
TC2: 급등 미달 → triggered=False
TC3: VP 미달 → triggered=False
TC4: 이평선 역배열 → triggered=False
TC5: RSI 범위 밖 → triggered=False
TC6: IPO 60일 이내 가산점
TC7: 거래대금 30억 미만 → score 감점
TC8: 백테스트 모드
TC9: 데이터 없음 처리 전체 DESK2 통합 테스트 ALL PASS 필수

---

## 실행 로그 원문

### Step 1: HANDOVER.md 및 CEO-DIRECTIVES.md 읽기

파일 읽기 성공:
- /root/project-docs/kis-autotrade-v4/HANDOVER.md (v10.12)
- /root/project-docs/kis-autotrade-v4/CEO-DIRECTIVES.md (v1.4)

[인계 확인]
직전 완료: T-156 (SELL_FAILED 전건청산 + 모의매매 현황)
현재 단계: Phase 2c (Command Center)
CEO 지시 적용: D-006, D-008-KR, D-009, D-010, D-011
strategy_cards: 60
open_positions: 0

### Step 2: 기존 코드 분석

기존 desk2_conditions 패키지 파악:
- base_condition.py: BaseCondition ABC
- c1_ul_expected.py: C1 (D6 상따갭)
- c2_prev_ul.py: C2 (D4 전상눌림)
- c3_open_strength.py: C3 (시초가강세)
- c4_intraday_surge.py: C4 (장중급등)
- c5_theme_simultaneous.py: C5 (테마동시급등)
- c6_close_strong.py: C6 (종가배팅갭)
- c_s1_volume_pullback.py: CS1 (S1 눌림)
- condition_registry.py: ConditionRegistry
- signal_matcher.py: SignalMatcher
- desk2_multi_condition_matcher.py: MultiConditionMatcher, CONDITION_BITS

CONDITION_BITS 기존 (T-156):
  C1=1, C2=2, C3=4, C4=8, C5=16, C6=32, CS1=64

### Step 3: c7_new_stock_detect.py 생성

파일 경로: /root/kis-autotrade-v4/backend/app/services/desk2_conditions/c7_new_stock_detect.py
생성 성공 (File created successfully)

구현 내용:
class C7NewStockDetectCondition(BaseCondition):
    CONDITION_ID = "C7"
    DESK_TARGET = "D-010"

    def __init__(self, param_override=None):
        super().__init__("c7_new_stock_detect", param_override)

    def evaluate(self, symbol, date, **kwargs):
        # 조건 1: 가격 급등 (시가×1.05 OR 전일종가×1.10)
        # 조건 2: VP ≥ 120
        # 조건 3: MA5 > MA10 > MA20
        # 조건 4: RSI 30~50
        # 추가: IPO 60일 이내 가산점, 거래대금 30억 감점
        ...

    def backtest_signal(self, symbol, date, ohlcv_1m):
        # 5% 급등봉 감지 → SL/TP
        ...

### Step 4: 통합 파일 업데이트

#### __init__.py 수정
추가:
  from .c7_new_stock_detect import C7NewStockDetectCondition
  "C7NewStockDetectCondition" in __all__

#### condition_registry.py 수정
build_default_registry() 함수에 C7 추가:
  from .c7_new_stock_detect import C7NewStockDetectCondition
  registry.register_class("C7", C7NewStockDetectCondition, overrides.get("C7"))

등록 총 8개: C1/C2/C3/C4/C5/C6/C7/CS1

#### signal_matcher.py 수정
_CONDITION_SIGNAL_MAP에 추가:
  "C7": ["TS-B4", "TS-B1"],  # T-161 NEW종목탐지

#### desk2_multi_condition_matcher.py 수정
CONDITION_BITS에 추가:
  "C7": 0b10000000,  # 128 ← T-161 신규

CONDITION_WEIGHTS에 추가:
  "C7": 1.2,  # IPO 급등 프리미엄

_build_registry()에 추가:
  from .c7_new_stock_detect import C7NewStockDetectCondition
  "C7": C7NewStockDetectCondition(self._overrides.get("C7")),

#### param_search_space.yaml 수정
desk2_conditions.c7_new_stock_detect 섹션 추가:
  c7_new_stock_detect:
    price_surge_open_pct: 5.0
    price_surge_prev_pct: 10.0
    vp_min: 120.0
    rsi_low: 30.0
    rsi_high: 50.0
    volume_amount_min: 3000000000
    ipo_days_bonus: 60
    ipo_score_bonus: 0.1
    sl_pct: 2.0
    tp_pct: 5.0

### Step 5: 테스트 파일 생성

파일 경로: /root/kis-autotrade-v4/tests/test_c7_new_stock_detect.py
12개 TC 생성:
  TC1: 4조건 충족 → triggered=True
  TC2: 가격 급등 미달 → triggered=False
  TC3: VP 미달 → triggered=False
  TC4: 이평선 역배열 → triggered=False
  TC5: RSI 범위 밖 → triggered=False
  TC6: IPO 60일 이내 가산점 → score 상승
  TC7: 거래대금 30억 미만 → score 감점
  TC8: 백테스트 모드 — 5% 급등봉 감지
  TC9: 데이터 없음 → triggered=False, error
  TC10: 전일종가 대비 10% 급등 (시가 기준 미달) → price_ok=True
  TC11: MultiConditionMatcher C7 등록 확인
  TC12: CONDITION_BITS C7=128 비트충돌 없음

### Step 6: 테스트 실행

명령: venv/bin/python3 -m pytest tests/test_c7_new_stock_detect.py -v

출력:
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 12 items

tests/test_c7_new_stock_detect.py::test_tc1_all_conditions_triggered PASSED [  8%]
tests/test_c7_new_stock_detect.py::test_tc2_price_surge_insufficient PASSED [ 16%]
tests/test_c7_new_stock_detect.py::test_tc3_vp_insufficient PASSED       [ 25%]
tests/test_c7_new_stock_detect.py::test_tc4_ma_reverse_alignment PASSED  [ 33%]
tests/test_c7_new_stock_detect.py::test_tc5_rsi_out_of_range PASSED      [ 41%]
tests/test_c7_new_stock_detect.py::test_tc6_ipo_bonus PASSED             [ 50%]
tests/test_c7_new_stock_detect.py::test_tc7_low_volume_amount_penalty PASSED [ 58%]
tests/test_c7_new_stock_detect.py::test_tc8_backtest_mode_triggered PASSED [ 66%]
tests/test_c7_new_stock_detect.py::test_tc9_missing_required_data PASSED [ 75%]
tests/test_c7_new_stock_detect.py::test_tc10_surge_from_prev_close PASSED [ 83%]
tests/test_c7_new_stock_detect.py::test_tc11_multi_condition_matcher_c7_registered PASSED [ 91%]
tests/test_c7_new_stock_detect.py::test_tc12_condition_bits_c7_is_128 PASSED [100%]

============================== 12 passed in 0.16s ==============================

### Step 7: 전체 DESK2 통합 테스트

명령: venv/bin/python3 -m pytest tests/test_c3_open_strength.py tests/test_c4_intraday_surge.py tests/test_c5_theme_simultaneous.py tests/test_c7_new_stock_detect.py -v

출력:
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 39 items

tests/test_c3_open_strength.py::test_tc1_gap_and_volume_triggered PASSED [  2%]
tests/test_c3_open_strength.py::test_tc2_insufficient_gap PASSED         [  5%]
tests/test_c3_open_strength.py::test_tc3_gap_ok_volume_insufficient PASSED [  7%]
tests/test_c3_open_strength.py::test_tc4_missing_data PASSED             [ 10%]
tests/test_c3_open_strength.py::test_tc5_exact_boundary PASSED           [ 12%]
tests/test_c3_open_strength.py::test_tc6_large_gap_high_score PASSED     [ 15%]
tests/test_c3_open_strength.py::test_tc7_backtest_signal_triggered PASSED [ 17%]
tests/test_c3_open_strength.py::test_tc8_backtest_empty_data PASSED      [ 20%]
tests/test_c3_open_strength.py::test_tc9_invalid_prev_close PASSED       [ 23%]
tests/test_c4_intraday_surge.py::test_tc1_surge_and_strength_triggered PASSED [ 25%]
tests/test_c4_intraday_surge.py::test_tc2_insufficient_surge PASSED      [ 28%]
tests/test_c4_intraday_surge.py::test_tc3_surge_volume_spike_no_strength PASSED [ 30%]
tests/test_c4_intraday_surge.py::test_tc4_surge_but_momentum_insufficient PASSED [ 33%]
tests/test_c4_intraday_surge.py::test_tc5_missing_data PASSED            [ 35%]
tests/test_c4_intraday_surge.py::test_tc6_exact_boundary PASSED          [ 38%]
tests/test_c4_intraday_surge.py::test_tc7_invalid_today_open PASSED      [ 41%]
tests/test_c4_intraday_surge.py::test_tc8_backtest_surge_detected PASSED [ 43%]
tests/test_c4_intraday_surge.py::test_tc9_backtest_empty PASSED          [ 46%]
tests/test_c5_theme_simultaneous.py::test_tc1_three_stocks_triggered PASSED [ 48%]
tests/test_c5_theme_simultaneous.py::test_tc2_only_two_triggered PASSED  [ 51%]
tests/test_c5_theme_simultaneous.py::test_tc3_mixed_stocks_not_triggered PASSED [ 53%]
tests/test_c5_theme_simultaneous.py::test_tc4_no_theme_stocks PASSED     [ 56%]
tests/test_c5_theme_simultaneous.py::test_tc5_exact_boundary_three_stocks PASSED [ 58%]
tests/test_c5_theme_simultaneous.py::test_tc6_five_stocks_high_score PASSED [ 61%]
tests/test_c5_theme_simultaneous.py::test_tc7_theme_name_detected PASSED [ 64%]
tests/test_c5_theme_simultaneous.py::test_tc8_backtest_signal_triggered PASSED [ 66%]
tests/test_c5_theme_simultaneous.py::test_tc9_backtest_empty PASSED      [ 69%]
tests/test_c7_new_stock_detect.py::test_tc1_all_conditions_triggered PASSED [ 71%]
tests/test_c7_new_stock_detect.py::test_tc2_price_surge_insufficient PASSED [ 74%]
tests/test_c7_new_stock_detect.py::test_tc3_vp_insufficient PASSED       [ 76%]
tests/test_c7_new_stock_detect.py::test_tc4_ma_reverse_alignment PASSED  [ 79%]
tests/test_c7_new_stock_detect.py::test_tc5_rsi_out_of_range PASSED      [ 82%]
tests/test_c7_new_stock_detect.py::test_tc6_ipo_bonus PASSED             [ 84%]
tests/test_c7_new_stock_detect.py::test_tc7_low_volume_amount_penalty PASSED [ 87%]
tests/test_c7_new_stock_detect.py::test_tc8_backtest_mode_triggered PASSED [ 89%]
tests/test_c7_new_stock_detect.py::test_tc9_missing_required_data PASSED [ 92%]
tests/test_c7_new_stock_detect.py::test_tc10_surge_from_prev_close PASSED [ 94%]
tests/test_c7_new_stock_detect.py::test_tc11_multi_condition_matcher_c7_registered PASSED [ 97%]
tests/test_c7_new_stock_detect.py::test_tc12_condition_bits_c7_is_128 PASSED [100%]

============================== 39 passed in 0.19s ==============================

### Step 8: git commit

명령:
git add backend/app/services/desk2_conditions/c7_new_stock_detect.py \
        backend/app/services/desk2_conditions/__init__.py \
        backend/app/services/desk2_conditions/condition_registry.py \
        backend/app/services/desk2_conditions/signal_matcher.py \
        backend/app/services/desk2_conditions/desk2_multi_condition_matcher.py \
        config/param_search_space.yaml \
        tests/test_c7_new_stock_detect.py

출력:
On branch phase-2c-command-center
Changes to be committed:
  modified:   backend/app/services/desk2_conditions/__init__.py
  new file:   backend/app/services/desk2_conditions/c7_new_stock_detect.py
  modified:   backend/app/services/desk2_conditions/condition_registry.py
  modified:   backend/app/services/desk2_conditions/desk2_multi_condition_matcher.py
  modified:   backend/app/services/desk2_conditions/signal_matcher.py
  modified:   config/param_search_space.yaml
  new file:   tests/test_c7_new_stock_detect.py

커밋 메시지:
[V4.1] T-161: D-010 C7 NEW종목 실시간 탐지 + DESK2 Phase B 완성

커밋 결과:
[phase-2c-command-center d1b1bb9a] [V4.1] T-161: D-010 C7 NEW종목 실시간 탐지 + DESK2 Phase B 완성
 7 files changed, 693 insertions(+), 8 deletions(-)
 create mode 100644 backend/app/services/desk2_conditions/c7_new_stock_detect.py
 create mode 100644 tests/test_c7_new_stock_detect.py

### Step 9: 보고서 생성

파일 경로: /root/kis-autotrade-v4/report/v41/CUR-V41-DESK2-C7-NEW-DETECT-001-20260306.md
생성 성공

---

## 완료 요약

| 항목 | 결과 |
|------|------|
| C7 구현 | ✅ 완료 (c7_new_stock_detect.py) |
| 통합 등록 | ✅ 완료 (8개 컨디션: C1/C2/C3/C4/C5/C6/C7/CS1) |
| CONDITION_BITS C7=128 | ✅ 완료 |
| 시그널 매핑 C7→TS-B4/TS-B1 | ✅ 완료 |
| YAML 파라미터 | ✅ 완료 |
| 테스트 12/12 ALL PASS | ✅ 완료 |
| 통합 테스트 39/39 ALL PASS | ✅ 완료 |
| git commit | ✅ d1b1bb9a |
| 보고서 작성 | ✅ 완료 |
| D-010 Phase B 완성 | ✅ 8개 컨디션 모두 구현 |

## 체크포인트

- [x] 코드 레포 커밋 완료 (d1b1bb9a, phase-2c-command-center)
- [ ] project-docs 보고서 push 완료 (done_watcher.sh 자동 처리 예정)
