---
project: KIS AutoTrade V4.1
task_id: T-137
completed_at: 2026-03-05T21:22:47 KST
---

# T-137 실행 결과: D-009 P1 확장 변수 4종 구현

## 지시 파일
`/root/.genspark/directives/running/KIS_20260305_205724_BRIDGE.md`

## 실행 단계별 결과

### 사전 작업 (백업)
```
$ cp backend/app/services/feature_engine.py backend/app/services/feature_engine.py.bak.T137
$ cp config/param_search_space.yaml config/param_search_space.yaml.bak.T137
Backups created successfully
```

### Step 1: config/param_search_space.yaml — p1_features 섹션 추가

파일: `/root/kis-autotrade-v4/config/param_search_space.yaml`

추가 내용 (realtime_features ul_flag_extended 섹션 아래 신규 추가):
```yaml
# ────────────────────────────────────────────────────────────
# T-137: D-009 P1 확장 변수 4종
# LEADER_FOLLOWER / CLOSE_BET / RSI_MACD_COMBO / NEWS_CATALYST
# ────────────────────────────────────────────────────────────
p1_features:
  leader_follower_rotation:
    leader_ul_flag: true
    follower_theme_rank_max: 5
    follower_ma20_1m_support: true
    exit_on_leader_ul_release: true
  close_bet_score:
    entry_after: "14:30"
    min_supply_concentration: 0.6
    low_rising_days_min: 3
    vol_increase_ratio: 1.3
    score_weights: {supply: 0.4, low_rise: 0.3, volume: 0.3}
  rsi_macd_combo_1m:
    rsi_period: 14
    rsi_bounce_range: [30, 40]
    vp_min: 120
    macd_params: [12, 26, 9]
    golden_cross_with_volume: true
  news_catalyst_score:
    source_table: "v4_news"
    lookback_hours: 24
    keyword_weights: {contract: 1.5, partnership: 1.3, earnings: 1.2, government: 1.4, ipo: 1.0}
    min_score: 0.5
    ma_convergence_1m_required: true
```

결과: ✅ 성공 — YAML 파일 업데이트 완료

### Step 2: feature_engine.py — 4개 엔진 구현

파일: `/root/kis-autotrade-v4/backend/app/services/feature_engine.py`
위치: 파일 끝(line 2812 이후) 추가

#### 2-1. LeaderFollowerEngine (신규 클래스)

```python
class LeaderFollowerEngine:
    """
    대장주 상한가 → 후발주 MA20 지지 스캔 엔진 (T-137 P1).

    피처:
      leader_ul_flag        : 대장주 당일 상한가 여부 (bool)
      follower_theme_rank   : 동일 테마 내 후발주 순위 (1~N)
      follower_ma20_1m_support : 1분봉 MA20 지지 여부 (bool)
      leader_follower_signal : 종합 진입 신호 (bool)

    로직:
      1) leader_symbol 이 당일 상한가(+29%+) 달성 확인
      2) follower_symbol 이 동일 테마 내 theme_rank ≤ follower_theme_rank_max 확인
      3) follower의 1분봉 현재가 ≥ MA20 확인
      → 3조건 모두 TRUE → leader_follower_signal = True
      4) exit_on_leader_ul_release: 대장 상한가 풀림(종가 < 상한가 -3%) 시 EXIT
    """
    def __init__(self, params=None): ...
    def evaluate(self, leader_change_pct, follower_theme_rank, follower_price_1m, follower_ma20_1m, leader_close=0.0, leader_ul_threshold_pct=29.0) -> Dict: ...
```

출력 피처: `leader_ul_flag`, `follower_theme_rank_ok`, `follower_ma20_1m_support`, `leader_follower_signal`, `exit_signal`

#### 2-2. CloseBetScoreEngine (신규 클래스)

```python
class CloseBetScoreEngine:
    """
    14:30 이후 종가 배팅 점수 엔진 (T-137 P1).
    score = supply*0.4 + low_rise*0.3 + volume*0.3
    진입 조건: time_ok AND score >= 0.6
    """
    def __init__(self, params=None): ...
    def evaluate(self, supply_concentration, low_rising_days, vol_ratio, current_time=None) -> Dict: ...
```

출력 피처: `time_ok`, `supply_concentration_ok`, `low_rising_ok`, `volume_increase_ok`, `close_bet_score`, `close_bet_valid`

#### 2-3. RsiMacdCombo1mEngine (신규 클래스)

```python
class RsiMacdCombo1mEngine:
    """
    1분봉 RSI 30~40 반등 + MACD 골든크로스 + 거래량 콤보 엔진 (T-137 P1).
    combo_signal = rsi_ok AND vp_ok AND macd_cross
    """
    def __init__(self, params=None): ...
    def evaluate(self, rsi_14, vp, macd_value, macd_signal_value) -> Dict: ...
```

출력 피처: `rsi_bounce_ok`, `vp_ok`, `macd_golden_cross`, `combo_signal`

#### 2-4. NewsCatalystEngine (신규 클래스)

```python
class NewsCatalystEngine:
    """
    24h 뉴스 키워드 가중 합산 + MA 수렴 확인 엔진 (T-137 P1).
    한국어 키워드 매핑: 계약/MOU, 정부/국책, 실적/흑자전환 등
    catalyst_valid = normalized_score >= 0.5 AND ma_convergence_ok
    """
    _KR_KEYWORD_MAP = {
        "contract": ["계약", "수주", "공급계약", "MOU"],
        "partnership": ["파트너십", "협력", "합작", "전략적"],
        "earnings": ["실적", "영업이익", "매출", "흑자전환"],
        "government": ["정부", "정책", "지원", "규제완화", "국책"],
        "ipo": ["IPO", "상장", "공모", "기업공개"],
    }
    def __init__(self, params=None): ...
    def evaluate(self, headlines, ma_convergence_ok, max_raw_score=5.0) -> Dict: ...
```

출력 피처: `news_keyword_score`, `news_score_normalized`, `ma_convergence_ok`, `catalyst_valid`

결과: ✅ 성공 — feature_engine.py에 4개 엔진 추가 (약 300 lines)

### Step 3: tests/unit/test_p1_features.py — 12개 테스트

파일: `/root/kis-autotrade-v4/tests/unit/test_p1_features.py` (신규 생성)

테스트 목록:
```
TestYamlParamLoad::test_leader_follower_yaml_params   — YAML follower_theme_rank_max=5 등 확인
TestYamlParamLoad::test_close_bet_yaml_params         — YAML entry_after="14:30" 등 확인
TestYamlParamLoad::test_rsi_macd_yaml_params          — YAML rsi_period=14, vp_min=120 등 확인
TestYamlParamLoad::test_news_catalyst_yaml_params     — YAML keyword_weights 확인
TestLeaderFollowerEngine::test_leader_follower_signal_true        — 대장+30% 순위3 MA지지 → signal=True
TestLeaderFollowerEngine::test_leader_follower_signal_false_rank_exceed — 순위6(>5) → signal=False
TestCloseBetScoreEngine::test_close_bet_high_score   — 수급0.75+저점4일+거래량1.6 → score=1.0, valid=True
TestCloseBetScoreEngine::test_close_bet_low_score    — 수급0.3+저점1일+거래량1.0 → score<0.6, valid=False
TestRsiMacdCombo1mEngine::test_rsi_macd_combo_true   — RSI35+VP150+MACD골든 → combo=True
TestRsiMacdCombo1mEngine::test_rsi_macd_combo_false_rsi_out — RSI55(범위밖) → combo=False
TestNewsCatalystEngine::test_news_catalyst_high_score — 계약+정부+실적 뉴스+MA수렴 → catalyst=True
TestNewsCatalystEngine::test_news_catalyst_low_score  — 관련없는뉴스+MA미수렴 → catalyst=False
```

### pytest 실행 결과

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.1.2, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False
collecting ... collected 12 items

tests/unit/test_p1_features.py::TestYamlParamLoad::test_leader_follower_yaml_params PASSED [  8%]
tests/unit/test_p1_features.py::TestYamlParamLoad::test_close_bet_yaml_params PASSED [ 16%]
tests/unit/test_p1_features.py::TestYamlParamLoad::test_rsi_macd_yaml_params PASSED [ 25%]
tests/unit/test_p1_features.py::TestYamlParamLoad::test_news_catalyst_yaml_params PASSED [ 33%]
tests/unit/test_p1_features.py::TestLeaderFollowerEngine::test_leader_follower_signal_true PASSED [ 41%]
tests/unit/test_p1_features.py::TestLeaderFollowerEngine::test_leader_follower_signal_false_rank_exceed PASSED [ 50%]
tests/unit/test_p1_features.py::TestCloseBetScoreEngine::test_close_bet_high_score PASSED [ 58%]
tests/unit/test_p1_features.py::TestCloseBetScoreEngine::test_close_bet_low_score PASSED [ 66%]
tests/unit/test_p1_features.py::TestRsiMacdCombo1mEngine::test_rsi_macd_combo_true PASSED [ 75%]
tests/unit/test_p1_features.py::TestRsiMacdCombo1mEngine::test_rsi_macd_combo_false_rsi_out PASSED [ 83%]
tests/unit/test_p1_features.py::TestNewsCatalystEngine::test_news_catalyst_high_score PASSED [ 91%]
tests/unit/test_p1_features.py::TestNewsCatalystEngine::test_news_catalyst_low_score [100%]

============================== 12 passed in 0.38s ==============================
```

**결과: 12/12 ALL PASS ✅**

### Step 4: git commit

```
$ git add backend/app/services/feature_engine.py config/param_search_space.yaml \
         tests/unit/test_p1_features.py report/v41/CUR-V41-P1-FEATURES-001-20260306.md

$ git commit -m "[V4.1] T-137: D-009 P1 확장 변수 4종 구현 ..."
[phase-2c-command-center 93036bd1] [V4.1] T-137: D-009 P1 확장 변수 4종 구현
 4 files changed, 821 insertions(+)
 create mode 100644 report/v41/CUR-V41-P1-FEATURES-001-20260306.md
 create mode 100644 tests/unit/test_p1_features.py
```

**커밋 해시: 93036bd1**

### Step 5: git push

```
$ git push origin phase-2c-command-center
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**결과: ❌ SSH 권한 없음 (claudebot 제약 — root에서 수동 push 필요)**
- 로컬 커밋은 완료: `93036bd1`
- `git push`는 root 계정에서 수행 필요

### Step 6: 보고서 작성

파일: `/root/kis-autotrade-v4/report/v41/CUR-V41-P1-FEATURES-001-20260306.md`
결과: ✅ 생성 완료

---

## 완료 체크리스트

- [x] 백업 생성 (feature_engine.py.bak.T137, param_search_space.yaml.bak.T137)
- [x] YAML p1_features 섹션 추가 (4개 엔진 파라미터)
- [x] LeaderFollowerEngine 구현 (대장 상한가 → 후발 MA20 지지)
- [x] CloseBetScoreEngine 구현 (14:30 수급+저점상승+거래량 점수)
- [x] RsiMacdCombo1mEngine 구현 (RSI 30~40 + MACD 골든크로스 + VP)
- [x] NewsCatalystEngine 구현 (24h 뉴스 키워드 + MA수렴)
- [x] 12개 테스트 ALL PASS (12/12)
- [x] git commit 93036bd1
- [ ] git push (root에서 수동 수행 필요)
- [ ] project-docs 보고서 push (done_watcher.sh 자동 처리 예정)
- [ ] HANDOVER.md T-137 반영 (root에서 수동 수행 필요)

---

## 잔여 작업 (root 권한 필요)

```bash
# 1. git push
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center

# 2. project-docs 보고서 sync
bash /root/project-docs/scripts/sync_kis.sh

# 3. HANDOVER.md 업데이트
# T-137 완료 항목 추가 필요
```
