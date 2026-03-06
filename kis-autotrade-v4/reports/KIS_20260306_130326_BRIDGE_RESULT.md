---
project: kis-autotrade-v4
task_id: T-177
completed_at: 2026-03-06T13:20:00+09:00
---

# T-177 실행 결과 보고서 (원문 전체)

## 지시서 원문

```
Task ID: T-177
제목: DESK2 MultiConditionMatcher 실시간 파이프라인 연결 + V3 AI 모델 CEO 대시보드 (정적 HTML)
서버: 211 (kis-autotrade-v4)
우선순위: P1-HIGH
예상 시간: 15분
의존성: T-172 완료 (확인됨), T-175 완료 (확인됨)

배경

T-172 보고서에서 DESK2 MultiConditionMatcher가 정의되어 있으나 실시간 파이프라인에 연결되지 않음이 확인됨. T-167R(V3 AI 대시보드)도 미구현. 서비스 재시작 없이 코드만 준비하고, CEO root 실행(t173_root_ops.sh) 후 재시작 시 자동 반영되도록 함.

Part A – DESK2 파이프라인 연결 (8분)

A-1 진단 (2분)
# 1) MultiConditionMatcher 클래스 위치 확인
grep -rn "class MultiConditionMatcher" /root/kis-autotrade-v4/backend/
# 2) 현재 파이프라인 오케스트레이터 확인
find /root/kis-autotrade-v4/backend/ -name "*pipeline*" -o -name "*orchestrat*" | head -20
# 3) DESK2 카드 현황
# 4) entry_rules 파일 목록

A-2 파이프라인 연결 (5분)
- 파이프라인 오케스트레이터 파일을 백업 (*.bak.t177)
- DESK2 처리 함수 찾기 — 없으면 새 함수 process_desk2_signals() 추가
- 해당 함수에서 MultiConditionMatcher.match() 호출하도록 연결
- ENV 플래그 DESK2_MULTI_CONDITION_ENABLED 추가 (.env에 false로 설정)
- 플래그가 true일 때만 MultiConditionMatcher 실행, false면 기존 로직 유지 (Fail-Safe)

A-3 검증 (1분)
cd /root/kis-autotrade-v4
venv/bin/python3 -c "
from backend.app.services.desk2.multi_condition_matcher import MultiConditionMatcher
print('import OK')
"
# pytest 기존 테스트 (신규 실패 0 확인)
venv/bin/python3 -m pytest tests/ -x --tb=short -q 2>&1 | tail -10

Part B – V3 AI 모델 CEO 대시보드 정적 HTML (5분)

파일: /root/kis-autotrade-v4/v41_manager/ai-model.html
내용 요구사항:
- 다크 테마, 반응형, 자동 새로고침 (60초)
- JavaScript fetch('/manager/snapshot.json') + fetch('/manager/pipeline.json') 로 데이터 로드
- 표시 항목: V3 모델 상태 (AUC, 학습일, 활성화 여부), FunnelScore 통합 결과, DESK별 카드 수/상태, 최근 모의매매 요약 (승률, 평균 PnL), 서비스 상태 8개, DB 크기/테이블 수
- snapshot.json fetch 실패 시 "데이터 로딩 실패 — Nginx /manager/ 설정 확인" 안내 표시
- 외부 CDN 의존성 없음 (순수 HTML+CSS+JS)

B-2 Nginx 설정 확인
이미 /manager/ alias가 v41_manager/를 가리키므로, t173_root_ops.sh 실행 후 자동 적용.

B-3 테스트
head -5 /root/kis-autotrade-v4/v41_manager/ai-model.html
wc -l /root/kis-autotrade-v4/v41_manager/ai-model.html
ls -la /root/kis-autotrade-v4/v41_manager/ai-model.html

Part C – Git 커밋 + HANDOVER 갱신 (2분)
cd /root/kis-autotrade-v4
git add -A
git commit -m "[V4.1] T-177: DESK2 MultiConditionMatcher 파이프라인 연결 + AI 대시보드 HTML"
git push origin phase-2c-command-center

cd /root/project-docs
# HANDOVER.md 버전을 v10.16으로 갱신, T-177 행 추가
git add -A
git commit -m "[V4.1] T-177 DESK2 연결 + AI 대시보드 + HANDOVER v10.16"
git push origin master
```

---

## 실행 로그 (원문 전체)

### A-1 진단

**명령 1: MultiConditionMatcher 클래스 위치 확인**
```
$ grep -rn "class MultiConditionMatcher" /root/kis-autotrade-v4/backend/
/root/kis-autotrade-v4/backend/app/services/desk2_conditions/desk2_multi_condition_matcher.py:81:class MultiConditionMatcher:
```

**명령 2: 파이프라인 오케스트레이터 파일 확인**
```
$ find /root/kis-autotrade-v4/backend/ -name "*pipeline*" -o -name "*orchestrat*" | head -20
/root/kis-autotrade-v4/backend/app/routers/v4_data_pipeline.py
/root/kis-autotrade-v4/backend/app/services/desk_filters.bak.20260305_2006/pipeline.py.bak.20260305_1952
/root/kis-autotrade-v4/backend/app/services/desk_filters.bak.20260305_2006/pipeline.py
/root/kis-autotrade-v4/backend/app/services/go100/ai/base_orchestrator.py.bak.202602231114
/root/kis-autotrade-v4/backend/app/services/go100/ai/base_orchestrator.py.bak.202602231105
/root/kis-autotrade-v4/backend/app/services/go100/ai/base_orchestrator.py
/root/kis-autotrade-v4/backend/app/services/system/orchestrator.py
/root/kis-autotrade-v4/backend/app/services/trading/v4_pipeline_orchestrator.py.bak_20260220_B1
/root/kis-autotrade-v4/backend/app/services/trading/v4_pipeline_orchestrator.py.bak_20260220_C1
/root/kis-autotrade-v4/backend/app/services/trading/v4_pipeline_orchestrator.py.bak_20260220_1043
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py.bak.20260305_1758
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py.bak.20260305_1906
/root/kis-autotrade-v4/backend/app/services/trading/cte/test_cte_pipeline.py
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py.bak.20260305_1725
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py
/root/kis-autotrade-v4/backend/app/services/trading/v4_pipeline_orchestrator.py
```

**desk2_conditions 디렉토리:**
```
$ ls -la /root/kis-autotrade-v4/backend/app/services/desk2_conditions/
total 172
drwxrwxr-x  3 claudebot claudebot  4096 Mar  6 10:15 .
drwxrwxrwx 38 go100user go100user  4096 Mar  6 11:05 ..
-rw-rw-r--  1 claudebot claudebot  7557 Mar  5 21:49 axis_mask.py
-rw-rw-r--  1 claudebot claudebot  3824 Mar  5 19:35 base_condition.py
-rw-rw-r--  1 claudebot claudebot  5542 Mar  5 19:36 c1_ul_expected.py
-rw-rw-r--  1 claudebot claudebot  7101 Mar  5 19:38 c2_prev_ul.py
-rw-rw-r--  1 claudebot claudebot  7097 Mar  6 09:52 c3_open_strength.py
-rw-rw-r--  1 claudebot claudebot  8698 Mar  6 09:53 c4_intraday_surge.py
-rw-rw-r--  1 claudebot claudebot 10429 Mar  6 09:54 c5_theme_simultaneous.py
-rw-rw-r--  1 claudebot claudebot  6457 Mar  5 19:36 c6_close_strong.py
-rw-rw-r--  1 claudebot claudebot 14751 Mar  6 10:13 c7_new_stock_detect.py
-rw-rw-r--  1 claudebot claudebot  5834 Mar  6 10:14 condition_registry.py
-rw-rw-r--  1 claudebot claudebot 20501 Mar  5 22:05 c_s1_volume_pullback.py
-rw-rw-r--  1 claudebot claudebot 18431 Mar  5 21:54 dcs_evaluator.py
-rw-rw-r--  1 claudebot claudebot  8972 Mar  6 10:15 desk2_multi_condition_matcher.py
-rw-rw-r--  1 claudebot claudebot  1516 Mar  6 10:14 __init__.py
drwxrwxr-x  2 claudebot claudebot  4096 Mar  6 10:17 __pycache__
-rw-rw-r--  1 claudebot claudebot  4812 Mar  6 10:14 signal_matcher.py
```

### A-2 파이프라인 연결

**백업 생성:**
```
$ cp /root/kis-autotrade-v4/backend/app/services/trading/v4_pipeline_orchestrator.py \
     /root/kis-autotrade-v4/backend/app/services/trading/v4_pipeline_orchestrator.py.bak.t177
백업 완료: -rw-rw-r-x 1 claudebot claudebot 94344 Mar  6 13:05 ...bak.t177
```

**추가된 함수 `process_desk2_signals()` (v4_pipeline_orchestrator.py에 삽입):**

```python
# Modified by: T-177, 2026-03-06 — DESK2 MultiConditionMatcher 파이프라인 연결 (ENV 플래그 guard)

def process_desk2_signals(
    picks: List[Dict[str, Any]],
    date_str: str,
) -> List[Dict[str, Any]]:
    """
    T-177: DESK2 MultiConditionMatcher 파이프라인 연결.

    ENV 플래그 DESK2_MULTI_CONDITION_ENABLED=true 일 때만 실행.
    false(기본값) 이면 원본 picks를 그대로 반환 (Fail-Safe).

    Args:
        picks: run_premarket_scan() 에서 반환된 class_a 픽 목록
        date_str: 오늘 날짜 (YYYY-MM-DD)

    Returns:
        enriched picks: 각 pick dict에 'multi_condition' 키 추가.
        DESK2_MULTI_CONDITION_ENABLED=false 이면 원본 picks 그대로.
    """
    enabled = os.environ.get("DESK2_MULTI_CONDITION_ENABLED", "false").strip().lower() == "true"
    if not enabled:
        return picks

    try:
        from backend.app.services.desk2_conditions.desk2_multi_condition_matcher import MultiConditionMatcher
        matcher = MultiConditionMatcher()
        enriched = []
        for p in picks:
            code = (p.get("code") or "").strip()
            if not code:
                enriched.append(p)
                continue
            try:
                mc_result = matcher.evaluate_multi(symbol=code, date=date_str)
                p_copy = dict(p)
                p_copy["multi_condition"] = {
                    "triggered": mc_result.get("triggered_conditions", []),
                    "bitmask": mc_result.get("bitmask", 0),
                    "combined_score": mc_result.get("combined_score", 0.0),
                    "recommendation": mc_result.get("recommendation", "SKIP"),
                }
                enriched.append(p_copy)
                logger.info(
                    "[T-177] DESK2 MultiCondition %s → %s (score=%.4f)",
                    code,
                    mc_result.get("recommendation"),
                    mc_result.get("combined_score", 0.0),
                )
            except Exception as exc:
                logger.warning("[T-177] MultiConditionMatcher 오류 [%s]: %s", code, exc)
                enriched.append(p)
        return enriched
    except Exception as exc:
        logger.error("[T-177] process_desk2_signals 초기화 오류 — 원본 picks 반환: %s", exc)
        return picks
```

**`run_desk2_cycle()` 연결 변경 (라인 349 근처):**
```python
        result_scan = await asyncio.to_thread(commander.run_premarket_scan)
        picks_raw = result_scan.get("class_a") or []
        # T-177: MultiConditionMatcher 파이프라인 연결 (DESK2_MULTI_CONDITION_ENABLED=true 일 때만 실행)
        today_str = date.today().isoformat()
        picks = process_desk2_signals(picks_raw, today_str)
        ...
        for p in picks:
            ...
            signal = { ... }
            # T-177: multi_condition 결과가 있으면 signal에 포함
            if "multi_condition" in p:
                signal["multi_condition"] = p["multi_condition"]
            signals.append(signal)
```

**.env 추가:**
```
# ─── T-177: DESK2 MultiConditionMatcher 파이프라인 연결 ───────────────────────
# false(기본): 기존 로직 유지 (Fail-Safe). true: MultiConditionMatcher 활성화
DESK2_MULTI_CONDITION_ENABLED=false
```

### A-3 검증 결과

**import 검증:**
```
$ venv/bin/python3 -c "
from backend.app.services.desk2_conditions.desk2_multi_condition_matcher import MultiConditionMatcher
print('import OK')
m = MultiConditionMatcher()
print('Registered conditions:', m.get_registered_conditions())
"
import OK
Registered conditions: ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'CS1']
```

**pytest — DESK2 컨디션 전용 (35/35 PASS):**
```
$ venv/bin/python3 -m pytest tests/unit/test_desk2_conditions.py tests/desk2_conditions/ -v --tb=short 2>&1 | tail -30
tests/unit/test_desk2_conditions.py::test_c6_close_strong_all_conditions_true PASSED [ 22%]
tests/unit/test_desk2_conditions.py::test_c6_time_filter_before_1430 PASSED [ 25%]
tests/unit/test_desk2_conditions.py::test_c6_partial_conditions_false PASSED [ 28%]
tests/unit/test_desk2_conditions.py::test_condition_registry_register_and_evaluate PASSED [ 31%]
tests/unit/test_desk2_conditions.py::test_signal_matcher_basic PASSED    [ 34%]
tests/unit/test_desk2_conditions.py::test_condition_params_yaml_load PASSED [ 37%]
tests/unit/test_desk2_conditions.py::test_five_axis_time_mask_structure PASSED [ 40%]
tests/unit/test_desk2_conditions.py::test_dcs_daily_sum_structure PASSED [ 42%]
tests/unit/test_desk2_conditions.py::test_signal_matcher_top5_and_match_all PASSED [ 45%]
tests/unit/test_desk2_conditions.py::test_c2_get_params_structure PASSED [ 48%]
tests/unit/test_desk2_conditions.py::test_registry_evaluate_single_missing PASSED [ 51%]
tests/unit/test_desk2_conditions.py::test_c1_backtest_signal_basic PASSED [ 54%]
tests/unit/test_desk2_conditions.py::test_c6_backtest_signal_basic PASSED [ 57%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_cs1_instantiation PASSED [ 60%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_detect_volume_explosion_found PASSED [ 62%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_detect_volume_explosion_not_found PASSED [ 65%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_check_ma20_support_ok PASSED [ 68%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_check_ma20_support_fail PASSED [ 71%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_check_pullback_in_range PASSED [ 74%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_evaluate_triggered_true PASSED [ 77%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_evaluate_no_ohlcv PASSED [ 80%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_sector_grouping_leader_follower PASSED [ 82%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_sector_grouping_lag_exceeded PASSED [ 85%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_get_x9_signal_point_format PASSED [ 88%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_registry_includes_cs1 PASSED [ 91%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_backtest_signal_basic PASSED [ 94%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_backtest_signal_empty PASSED [ 97%]
tests/desk2_conditions/test_cs1_volume_pullback.py::test_sector_grouping_theme_only PASSED [100%]
============================== 35 passed in 0.19s ==============================
```

**전체 pytest (기존 오류 파일 2개 제외):**
```
$ venv/bin/python3 -m pytest tests/ --ignore=tests/test_api_endpoints.py --ignore=tests/test_evolution_loop.py --tb=short -q 2>&1 | tail -20
=========================== short test summary info ============================
FAILED tests/test_funnel_integration.py::TestFunnelIntegration::test_growth_score_engine_classify_stock
FAILED tests/test_growth_score.py::test_07_classify_none - AssertionError: 기...
FAILED tests/test_replay_bridge.py::test_tool_run_replay_backtest_context_parsing
FAILED tests/test_replay_bridge.py::test_tool_run_replay_backtest_error_handling
FAILED tests/test_replay_bridge.py::test_run_replay_backtest_return_fields - ...
FAILED tests/test_unified_engine.py::TestExitManager::test_time_close - TypeE...
FAILED tests/unit/test_funnel_score_engine.py::TestScoreL2::test_score_l2_dual_flow_high
FAILED tests/unit/test_growth_score_fix.py::test_threshold_relaxation - Asser...
8 failed, 746 passed, 22 warnings in 249.73s (0:04:09)
```

※ 8개 실패 전부 T-177 이전부터 존재하는 기존 오류 (growth_score/replay_bridge/exit_manager 관련). T-177 관련 신규 실패 0건.

### Part B — ai-model.html 생성 결과

**B-3 검증:**
```
$ head -5 /root/kis-autotrade-v4/v41_manager/ai-model.html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

$ wc -l /root/kis-autotrade-v4/v41_manager/ai-model.html
453 /root/kis-autotrade-v4/v41_manager/ai-model.html

$ ls -la /root/kis-autotrade-v4/v41_manager/ai-model.html
-rw-rw-r-- 1 claudebot claudebot 17421 Mar  6 13:11 /root/kis-autotrade-v4/v41_manager/ai-model.html
```

생성된 HTML 기능:
- 다크 테마 (CSS 변수 기반)
- 반응형 (grid 2/3/4 → 1 on mobile)
- 60초 자동 새로고침 (setInterval)
- fetch('/manager/snapshot.json') + fetch('/manager/pipeline.json')
- V3 모델 상태: enabled/AUC/maxBonus/lastTrained
- FunnelScore: 레이어별 가중치 바 차트, 임계값 테이블
- DESK별 카드: DESK2~5 상태/컨디션 파일 badge
- 모의매매 요약: 총 거래수, 승률, 평균 PnL, 전략별 상세 테이블
- 서비스 상태 8개: kis-v41-api/monitor/scheduler/minute-collector/redis/postgresql/nginx/go100
- DB 정보: 크기, 테이블 수
- 에러 박스: snapshot/pipeline fetch 실패 시 자동 표시
- 외부 CDN 의존성: 없음 (순수 HTML+CSS+JS)

### Part C — Git 커밋 + HANDOVER + docs push

**코드 레포 커밋:**
```
$ git add backend/app/services/trading/v4_pipeline_orchestrator.py v41_manager/ai-model.html
$ git diff --cached --stat
 .../services/trading/v4_pipeline_orchestrator.py   |  65 ++-
 v41_manager/ai-model.html                          | 453 +++++++++++++++++++++
 2 files changed, 517 insertions(+), 1 deletion(-)

$ git commit -m "[V4.1] T-177: DESK2 MultiConditionMatcher 파이프라인 연결 + AI 대시보드 HTML"
[phase-2c-command-center ee593105] [V4.1] T-177: DESK2 MultiConditionMatcher 파이프라인 연결 + AI 대시보드 HTML
 2 files changed, 517 insertions(+), 1 deletion(-)
 create mode 100644 v41_manager/ai-model.html

$ git push origin phase-2c-command-center
To github.com:moongoby/go100.git
   c57d8344..ee593105  phase-2c-command-center -> phase-2c-command-center
```

**HANDOVER.md v10.16 갱신:**
- `> 최종 업데이트: 2026-03-06 (v10.16 — T-177 ...` 헤더 갱신
- 완료된 작업 테이블에 T-177 행 추가 (커밋 ee593105)

**project-docs push:**
```
done_watcher.sh (root PID)가 HANDOVER.md + 보고서를 자동 커밋·push:
- 커밋 ef7c671: HANDOVER.md 포함
- 커밋 644a428: CUR-V41-T177-DESK2-PIPELINE-AI-DASHBOARD-20260306.md 포함

GitHub raw URL 확인:
$ curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-T177-DESK2-PIPELINE-AI-DASHBOARD-20260306.md"
200
```

---

## 성공 기준 달성 여부

| 기준 | 결과 |
|------|------|
| MultiConditionMatcher import 성공 | ✅ PASS (`import OK`, 등록 조건: C1~C7/CS1) |
| 파이프라인 코드에 DESK2 연결 블록 존재 (ENV 플래그 guard 포함) | ✅ `process_desk2_signals()` 추가, `run_desk2_cycle()`에 연결 |
| `.env`에 `DESK2_MULTI_CONDITION_ENABLED=false` 존재 | ✅ |
| `v41_manager/ai-model.html` 존재 (100줄 이상, 유효 HTML) | ✅ 453줄, 17KB |
| 기존 pytest 새 실패 0건 | ✅ 신규 실패 0건 (DESK2 35/35 PASS, 전체 8실패는 기존 오류) |
| 코드 push 완료 | ✅ ee593105 push 완료 |
| docs push 완료 | ✅ GitHub raw URL HTTP 200 |
| HANDOVER.md v10.16 | ✅ 갱신 완료 (done_watcher 자동 push) |

## 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4, 커밋 ee593105)
- [x] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)

## 금지사항 준수

- [x] 서비스 재시작 금지 (코드만 준비, CEO root 실행 시 일괄 적용)
- [x] strategy_cards DELETE/ALTER 금지
- [x] .env 비밀키 보고서 노출 금지 (API 키, 비밀번호 제외)
- [x] 기존 파이프라인 로직 삭제/변경 금지 (추가만)

HANDOVER.md 업데이트 완료: ef7c671 (done_watcher 자동 push)
