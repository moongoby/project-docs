---
project: kis-autotrade-v4
task_id: T-116
completed_at: 2026-03-05T17:58:10+09:00
---

# T-116 FORCE_ACC 세력 매집 패턴 탐지 엔진 — 실행 결과 보고서

## 1. 사전 작업 (백업)

```
$ cp backend/app/services/feature_engine.py backend/app/services/feature_engine.py.bak.20260305_1754
$ cp config/param_search_space.yaml config/param_search_space.yaml.bak.20260305_1754

백업 완료
-rw-rw-r-- 1 claudebot claudebot  5546 Mar  5 16:52 backend/app/services/feature_engine.py.bak.20260305_1652
-rw-rw-r-- 1 claudebot claudebot 12196 Mar  5 16:56 backend/app/services/feature_engine.py.bak.20260305_1656
-rw-rw-r-- 1 claudebot claudebot 23526 Mar  5 17:53 backend/app/services/feature_engine.py.bak.20260305_1753
-rw-rw-r-- 1 claudebot claudebot 23526 Mar  5 17:54 backend/app/services/feature_engine.py.bak.20260305_1754
-rw-r--r-- 1 claudebot claudebot 22894 Mar  5 16:42 config/param_search_space.yaml.bak.20260305_1642
-rw-r--r-- 1 claudebot claudebot 23511 Mar  5 16:45 config/param_search_space.yaml.bak.20260305_1645
-rw-r--r-- 1 claudebot claudebot 24453 Mar  5 16:52 config/param_search_space.yaml.bak.20260305_1652
-rw-r--r-- 1 claudebot claudebot 25095 Mar  5 16:56 config/param_search_space.yaml.bak.20260305_1656
-rw-r--r-- 1 claudebot claudebot 25815 Mar  5 17:53 config/param_search_space.yaml.bak.20260305_1753
-rw-r--r-- 1 claudebot claudebot 25815 Mar  5 17:54 config/param_search_space.yaml.bak.20260305_1754
```

## 2. config/param_search_space.yaml — force_acc 섹션 추가

파일: `/root/kis-autotrade-v4/config/param_search_space.yaml`

추가된 섹션 (line 519~543):

```yaml
# ────────────────────────────────────────────────────────────
# T-116: FORCE_ACC 세력 매집 패턴 탐지 엔진 파라미터
# CEO D-008-KR §3-2. VCP + Wyckoff Spring 한국 변형
# ForceAccEngine에서 사용
# ────────────────────────────────────────────────────────────
force_acc:
  ma_convergence:
    period: 120          # 120일선 기준
    std_threshold: 0.03  # MA5/10/20/60/120 표준편차 ≤ 3%
    lookback_days: 60    # 수렴 구간 검색 윈도우
  surge_in_range:
    pct_threshold: 20.0  # 수렴 구간 내 20%+ 급등봉
    min_count: 1         # 최소 1회
  gap_breakout:
    gap_pct: 3.0         # 시초가 갭 ≥ 3%
    volume_ratio: 2.0    # 전일 대비 거래량 2배
  score_weights:
    convergence: 0.40
    surge: 0.30
    gap: 0.30
```

확인:
```
$ grep -n "force_acc" config/param_search_space.yaml | head -5
194:  l5_weight_force_acc: 0.25           # FORCE_ACC 가중치
198:  l5_force_acc_vol_multiplier: 2.0    # FORCE_ACC 거래량 배수
524:force_acc:
```

## 3. backend/app/services/feature_engine.py — ForceAccEngine 구현

파일: `/root/kis-autotrade-v4/backend/app/services/feature_engine.py`

추가 내용:

### 3.1 `_load_force_acc_params()`
config/param_search_space.yaml에서 `force_acc` 섹션 로드.
실패 시 빈 dict 반환 (기본값 사용).

### 3.2 `class ForceAccEngine`

**`__init__(self, params=None)`**
- `_ma_period`: 120 (120일선 기준)
- `_std_threshold`: 0.03 (MA 표준편차 ≤ 3%)
- `_lookback_days`: 60 (수렴 구간 검색 윈도우)
- `_surge_pct`: 20.0 (급등봉 기준 %)
- `_surge_min_count`: 1 (최소 1회)
- `_gap_pct`: 3.0 (갭상승 기준 %)
- `_vol_ratio`: 2.0 (거래량 2배)
- `_w_convergence`: 0.40, `_w_surge`: 0.30, `_w_gap`: 0.30

**`_fetch_ohlcv(symbol, date, limit)`**
- ohlcv_daily에서 최근 N 거래일 데이터 조회 (날짜 내림차순)
- date 지정 시 해당일 이전 데이터 조회

**`_calc_ma_convergence(symbol, date) → (bool, float)`**
- MA5/10/20/60/120 종가 기준 이평선 계산
- 이평선들의 평균 대비 상대 표준편차(rel_std) 계산
- is_converging: rel_std ≤ std_threshold (0.03)
- std_score: max(0.0, 1.0 - rel_std / std_threshold)

**`_count_surge_in_range(symbol, date) → int`**
- lookback_days 구간 내 (close-open)/open×100 ≥ 20.0% 봉 수 카운트

**`_check_gap_breakout(symbol, date) → (bool, float)`**
- 최신일 시초가 vs 전일 종가: 갭 ≥ 3.0%
- 최신일 거래량 / 전일 거래량 ≥ 2.0배
- 두 조건 모두 충족 시 has_gap=True

**`calculate_force_acc(symbol, date) → dict`**
```python
{
    'is_accumulating': bool,   # is_converging AND surge_count >= min_count
    'convergence_score': float,
    'surge_count': int,
    'gap_breakout': bool,
    'force_acc_score': float,
}
# SCORE = convergence×0.4 + min(surge_count/3, 1)×0.3 + gap×0.3
```
로그: `logger.info("[FORCE_ACC] symbol=%s, converging=%s, surge=%d, score=%.4f", ...)`

## 4. backend/app/services/funnel_score_engine.py — score_l2() ForceAccEngine 통합

파일: `/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py`

`score_l2()` 메서드에 다음 코드 추가 (line 441~457):

```python
# T-116: FORCE_ACC 매집 보너스 (+force_acc_score × 0.15)
force_acc_bonus = 0.0
try:
    from backend.app.services.feature_engine import ForceAccEngine
    fa_engine = ForceAccEngine()
    fa_result = fa_engine.calculate_force_acc(symbol, date)
    force_acc_bonus = float(fa_result.get("force_acc_score", 0.0)) * 0.15
except Exception as e:
    logger.warning("L2[%s]: ForceAccEngine 조회 실패: %s → 0.0", symbol, e)

score = min(1.0, max(0.0, raw + force_acc_bonus))
logger.debug(
    "L2[%s]: dual_flow_score=%.4f(20D=%.4f consec=%d) close_pos=%s force_acc_bonus=%.4f → %.4f",
    symbol, dual_flow_score, dual_flow_20d, consec_days,
    f"{close_pos:.3f}" if close_pos is not None else "N/A",
    force_acc_bonus, score,
)
```

L2 최종 공식: `score = min(1.0, DUAL_FLOW_SCORE×0.7 + CLOSE_POS_BONUS + force_acc_score×0.15)`

## 5. tests/unit/test_force_acc.py — 단위 테스트 8개

파일: `/root/kis-autotrade-v4/tests/unit/test_force_acc.py`

| # | 테스트명 | 검증 내용 |
|---|----------|-----------|
| 1 | test_ma_convergence_true | 동일 종가 → is_converging=True, std_score>0 |
| 2 | test_ma_convergence_false | 강한 트렌드 → is_converging=False |
| 3 | test_surge_count | 급등봉 3개 정확히 카운트 |
| 4 | test_gap_breakout | 갭 5%+거래량 3배 → has_gap=True |
| 5 | test_score_calculation | SCORE 공식 검증 (최대 1.0) |
| 6 | test_no_data_graceful | 데이터 없음 → 기본값 0.0 반환 |
| 7 | test_yaml_load | force_acc YAML 섹션 파싱 + 가중치 합계 1.0 검증 |
| 8 | test_funnel_integration | FunnelScoreEngine.score_l2() FORCE_ACC 보너스 가산 확인 |

## 6. 테스트 실행 결과 (8/8 ALL PASS)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 8 items

tests/unit/test_force_acc.py::TestForceAccEngine::test_ma_convergence_true PASSED [ 12%]
tests/unit/test_force_acc.py::TestForceAccEngine::test_ma_convergence_false PASSED [ 25%]
tests/unit/test_force_acc.py::TestForceAccEngine::test_surge_count PASSED [ 37%]
tests/unit/test_force_acc.py::TestForceAccEngine::test_gap_breakout PASSED [ 50%]
tests/unit/test_force_acc.py::TestForceAccEngine::test_score_calculation PASSED [ 62%]
tests/unit/test_force_acc.py::TestForceAccEngine::test_no_data_graceful PASSED [ 75%]
tests/unit/test_force_acc.py::TestForceAccEngine::test_yaml_load PASSED  [ 87%]
tests/unit/test_force_acc.py::TestForceAccEngine::test_funnel_integration PASSED [100%]

============================== 8 passed in 0.19s ===============================
```

## 7. Git 커밋 내역

```
$ git add backend/app/services/feature_engine.py config/param_search_space.yaml backend/app/services/funnel_score_engine.py tests/unit/test_force_acc.py

$ git commit -m "[V4.1] T-116: FORCE_ACC 세력 매집 패턴 탐지 — VCP+Wyckoff Spring 한국판"
[phase-2c-command-center 7d213031] [V4.1] T-116: FORCE_ACC 세력 매집 패턴 탐지 — VCP+Wyckoff Spring 한국판
 3 files changed, 486 insertions(+), 3 deletions(-)
 create mode 100644 tests/unit/test_force_acc.py
```

커밋 해시: `7d213031`

## 8. Git Push 상태

```
$ git push origin phase-2c-command-center
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**⚠️ Push 실패**: claudebot 계정에 GitHub SSH 키 없음.
root 계정에서 수동 push 필요:
```bash
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center
```

## 9. 완료 기준 체크

| 항목 | 상태 |
|------|------|
| YAML force_acc 섹션 추가 | ✅ 완료 |
| `_load_force_acc_params()` 구현 | ✅ 완료 |
| `ForceAccEngine._calc_ma_convergence()` | ✅ 완료 |
| `ForceAccEngine._count_surge_in_range()` | ✅ 완료 |
| `ForceAccEngine._check_gap_breakout()` | ✅ 완료 |
| `ForceAccEngine.calculate_force_acc()` | ✅ 완료 |
| FunnelScore L2 통합 (×0.15 보너스) | ✅ 완료 |
| SCORE 공식 검증 (convergence×0.4+surge×0.3+gap×0.3) | ✅ 완료 |
| [FORCE_ACC] 로그 출력 | ✅ 완료 |
| 8/8 단위 테스트 PASS | ✅ 완료 |
| .bak 파일 미커밋 | ✅ 확인 |
| 서비스 재시작 없음 | ✅ 확인 |
| 코드 레포 커밋 | ✅ 7d213031 |
| 코드 레포 push | ⚠️ SSH 키 없음 — root 수동 push 필요 |

## 10. 알고리즘 설계 요약

### FORCE_ACC Score 공식
```
SCORE = convergence_score × 0.40
      + min(surge_count / 3, 1.0) × 0.30
      + (has_gap ? 1.0 : 0.0) × 0.30
```

### 매집 판단 조건 (is_accumulating)
```
is_accumulating = is_converging AND surge_count >= 1
  where is_converging = rel_std(MA5,10,20,60,120) <= 0.03
```

### FunnelScore L2 최종 공식
```
L2 = min(1.0, DUAL_FLOW_SCORE×0.7 + CLOSE_POS_BONUS + FORCE_ACC×0.15)
```
