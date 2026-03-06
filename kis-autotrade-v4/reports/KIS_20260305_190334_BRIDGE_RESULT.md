---
project: kis-autotrade-v4
task_id: T-127
completed_at: 2026-03-05T19:30:00+09:00 KST
---

# T-127 실행 결과: DESK543 프랙탈 트리거 실전 연결 — D-012/D-013/D-014

## 지시서 읽기
파일: /root/.genspark/directives/running/KIS_20260305_190334_BRIDGE.md
Task ID: T-127
제목: DESK543 프랙탈 트리거 실전 연결 — D-012 Phase 1
서버: 211 (kis-autotrade-v4)

---

## 1. 사전 작업 — .bak 생성

```
cp backend/app/services/desk_filters/pipeline.py \
   backend/app/services/desk_filters/pipeline.py.bak.$(date +%Y%m%d_%H%M)
```
결과: pipeline.py.bak.20260305_1927 생성 완료

---

## 2. config/param_search_space.yaml — fractal_live 섹션 추가

추가 위치: desk2_conditions 섹션 직전
추가 내용:

```yaml
# ────────────────────────────────────────────────────────────
# T-127: DESK543 프랙탈 트리거 실전 연결 파라미터
# CEO D-012/D-013: 트리거 = 매수 신호
# CEO D-014: DESK5 코어 보유 정책 (청산 3조건만)
# FractalLiveConnector에서 사용
# ────────────────────────────────────────────────────────────
fractal_live:
  desk5_triggers:
    min_triggers: 2          # T5-1~T5-3 중 2개 충족 시 매수
    position_size_pct: 5.0   # 총자산 대비 5%
  desk4_triggers:
    min_triggers: 2          # T4-1~T4-4 중 2개
    position_size_pct: 3.0
  desk3_triggers:
    min_triggers: 1          # T3-1/T3-2 단독 또는 T3-3~T3-5 중 2개
    position_size_pct: 2.0
  desk5_exit:                # D-014 코어 보유 정책
    weekly_ma20_break_weeks: 2    # 주봉 MA20 2주 연속 이탈
    force_exit_vol_ratio: 3.0     # 주봉 거래량 20주 평균 3배 + 음봉
    theme_death_days: 30          # 30일 연속 뉴스 0건
    profit_100_recover_principal: true  # +100% 시 원금 회수
    profit_500_trail_weekly_ma10: true  # +500% 시 주봉 MA10 트레일링
```

---

## 3. backend/app/services/fractal_live_connector.py — 신규 생성

파일 크기: 865 lines (fractal_live_connector.py 포함 전체)
경로: /root/kis-autotrade-v4/backend/app/services/fractal_live_connector.py

### 구현 메서드 (6개)
1. `__init__(yaml_path)` — YAML fractal_live 파라미터 로드 + fractal_triggers import (3단계 fallback)
2. `evaluate_desk5_entry(symbol, bars)` → {should_enter, triggers_met, trigger_details}
   - T5-1~T5-3 중 min_triggers(=2)개 이상 충족 시 should_enter=True
3. `evaluate_desk4_entry(symbol, bars, wave1_high, vp_score, sector_rebounds)` → {should_enter, triggers_met, trigger_details}
   - T4-1~T4-4 중 min_triggers(=2)개 이상 충족 시 should_enter=True
4. `evaluate_desk3_entry(symbol, bars, had_upper_limit, dual_flow_days, has_catalyst_news)` → {should_enter, triggers_met, trigger_details, signal_reason}
   - T3-1/T3-2 단독 충족 또는 T3-3~T3-5 중 2개 이상 충족
5. `check_desk5_exit(symbol, position, weekly_bars, news_count_30d)` → {should_exit, reason, exit_type, conditions, pnl_pct, profit_action}
   - D-014 청산 3조건:
     * 조건1: 주봉 MA20 2주 연속 이탈 → exit_type=weekly_ma20
     * 조건2: 주봉 거래량 20주 평균 3배 + 음봉 → exit_type=force_exit
     * 조건3: 30일 뉴스 0건 → exit_type=theme_death
     * D-014 핵심: -30% 손실이어도 3조건 미충족 시 should_exit=False (절대 청산 금지)
   - 수익 실현: +100% → recover_principal, +500% → trail_ma10
6. `get_position_size(desk_level, total_capital)` → float (투자금액)
   - DESK5: 5%, DESK4: 3%, DESK3: 2%

로깅 형식: `[FRACTAL_LIVE] desk={} symbol={} action={} triggers={}`

---

## 4. backend/app/services/desk_filters/pipeline.py — 수정

### 추가 내용
1. `_fractal_connector` 전역 변수 + `_get_fractal_connector()` lazy loader
2. `run_all()` 메서드에 `fractal_bars: Optional[List] = None` 파라미터 추가
3. fractal_bars 제공 시 `_evaluate_fractal_triggers()` 호출
4. `_evaluate_fractal_triggers()` 신규 메서드:
   - DESK5 → DESK4 → DESK3 순서로 프랙탈 트리거 평가
   - triggered=True 시 results["any_pass"] = True 설정 (CTE 파이프라인 주입)

```
[PIPELINE] fractal_trigger activated: symbol=TEST desk=5
```

---

## 5. tests/unit/test_fractal_live.py — 21개 테스트 생성

| TC | 테스트명 | 결과 |
|----|---------|------|
| TC-01a | test_yaml_load_fractal_live | PASS |
| TC-01b | test_yaml_desk5_min_triggers | PASS |
| TC-01c | test_yaml_desk5_exit_params | PASS |
| TC-02a | test_desk5_entry_insufficient_triggers | PASS |
| TC-02b | test_desk5_entry_true_two_triggers | PASS |
| TC-03a | test_desk4_entry_two_triggers_pass | PASS |
| TC-03b | test_desk4_entry_one_trigger_fail | PASS |
| TC-04a | test_desk3_entry_solo_t3_1 (T3-1 단독) | PASS |
| TC-04b | test_desk3_entry_catalyst_rsi_pass | PASS |
| TC-05a | test_desk5_exit_weekly_ma20_break | PASS |
| TC-05b | test_desk5_exit_force_exit_volume_spike | PASS |
| TC-05c | test_desk5_exit_theme_death | PASS |
| TC-05d | **test_desk5_exit_loss_30pct_no_conditions** (D-014 핵심!) | **PASS** |
| TC-05e | test_desk5_exit_profit_100_recover_principal | PASS |
| TC-05f | test_desk5_exit_profit_500_trail_ma10 | PASS |
| TC-06a | test_get_position_size_desk5 | PASS |
| TC-06b | test_get_position_size_desk4 | PASS |
| TC-06c | test_get_position_size_desk3 | PASS |
| TC-07a | test_evaluate_desk5_response_structure | PASS |
| TC-07b | test_check_desk5_exit_response_structure | PASS |
| TC-07c | test_exit_without_weekly_bars | PASS |

---

## 6. pytest 실행 결과

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function
collecting ... collected 21 items

tests/unit/test_fractal_live.py::test_yaml_load_fractal_live PASSED      [  4%]
tests/unit/test_fractal_live.py::test_yaml_desk5_min_triggers PASSED     [  9%]
tests/unit/test_fractal_live.py::test_yaml_desk5_exit_params PASSED      [ 14%]
tests/unit/test_fractal_live.py::test_desk5_entry_insufficient_triggers PASSED [ 19%]
tests/unit/test_fractal_live.py::test_desk5_entry_true_two_triggers PASSED [ 23%]
tests/unit/test_fractal_live.py::test_desk4_entry_two_triggers_pass PASSED [ 28%]
tests/unit/test_fractal_live.py::test_desk4_entry_one_trigger_fail PASSED [ 33%]
tests/unit/test_fractal_live.py::test_desk3_entry_solo_t3_1 PASSED       [ 38%]
tests/unit/test_fractal_live.py::test_desk3_entry_catalyst_rsi_pass PASSED [ 42%]
tests/unit/test_fractal_live.py::test_desk5_exit_weekly_ma20_break PASSED [ 47%]
tests/unit/test_fractal_live.py::test_desk5_exit_force_exit_volume_spike PASSED [ 52%]
tests/unit/test_fractal_live.py::test_desk5_exit_theme_death PASSED      [ 57%]
tests/unit/test_fractal_live.py::test_desk5_exit_loss_30pct_no_conditions PASSED [ 61%]
tests/unit/test_fractal_live.py::test_desk5_exit_profit_100_recover_principal PASSED [ 66%]
tests/unit/test_fractal_live.py::test_desk5_exit_profit_500_trail_ma10 PASSED [ 71%]
tests/unit/test_fractal_live.py::test_get_position_size_desk5 PASSED     [ 76%]
tests/unit/test_fractal_live.py::test_get_position_size_desk4 PASSED     [ 80%]
tests/unit/test_fractal_live.py::test_get_position_size_desk3 PASSED     [ 85%]
tests/unit/test_fractal_live.py::test_evaluate_desk5_response_structure PASSED [ 90%]
tests/unit/test_fractal_live.py::test_check_desk5_exit_response_structure PASSED [ 95%]
tests/unit/test_fractal_live.py::test_exit_without_weekly_bars PASSED    [100%]

============================== 21 passed in 0.35s ==============================
```

**결과: 21/21 ALL PASS**

---

## 7. git commit

```
커밋 해시: f8bd2bee
브랜치: phase-2c-command-center
메시지: [V4.1] T-127: DESK543 프랙탈 트리거 실전 연결 — D-012/D-013/D-014

변경 파일:
  M backend/app/services/desk_filters/pipeline.py
  A backend/app/services/fractal_live_connector.py
  M config/param_search_space.yaml
  A tests/unit/test_fractal_live.py

4 files changed, 865 insertions(+), 1 deletion(-)
```

git push: SSH 권한 오류 (Permission denied publickey) — root 실행 필요
→ done_watcher.sh 또는 root에서 `git push origin phase-2c-command-center` 실행 필요

---

## 8. 완료 조건 체크

| 항목 | 결과 |
|------|------|
| fractal_live YAML 섹션 생성 | ✅ |
| FractalLiveConnector 6메서드 구현 | ✅ |
| D-014 DESK5 청산 3조건 + 원금회수/트레일링 구현 | ✅ |
| pipeline.py 통합 | ✅ |
| 10+ 테스트 ALL PASS (21개) | ✅ |
| git commit | ✅ (f8bd2bee) |
| git push | ⚠️ SSH 권한 필요 (root 실행) |
| .bak 커밋 제외 | ✅ |
| 서비스 재시작 금지 | ✅ |

---

## 9. 핵심 구현 사항 (D-014)

```
D-014 DESK5 코어 보유 정책:
  청산 허용 조건 (3가지만):
    1. 주봉 MA20 2주 연속 이탈
    2. 주봉 거래량 20주 평균 3배 + 음봉 (세력 이탈)
    3. 30일 연속 뉴스 0건 (테마 사망)

  절대 청산 금지:
    - -30% 손실 (3조건 미충족 시 should_exit=False)
    - 단순 시간 경과
    - 기타 기술적 지표

  수익 실현 (청산과 무관, 병행):
    - +100% 도달 → 원금 회수 (profit_action=recover_principal)
    - +500% 도달 → 주봉 MA10 트레일링 (profit_action=trail_ma10)
```

---

## 10. project-docs 보고서 push

보고서 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-FRACTAL-LIVE-001-20260305.md
→ root 권한 필요 (done_watcher.sh 자동 처리 예정)

HANDOVER.md 업데이트: root 권한 필요

---

## 로컬 보고서

/root/kis-autotrade-v4/report/v41/ 에 보고서 생성 필요
(done_watcher.sh가 본 RESULT.md 감지하여 project-docs push 자동 수행)
