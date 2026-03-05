---
project: kis-autotrade-v4
task_id: T-121
completed_at: 2026-03-05T19:30:00+09:00
---

# T-121: BJ_SCORE 배진한 5원칙 정량화 엔진 — 실행 결과

## 실행 개요

지시 파일: `/root/.genspark/directives/running/KIS_20260305_190322_BRIDGE.md`
실행 시작: 2026-03-05
완료 상태: **코드 구현 완료 / git push SSH 권한 미비 (root 실행 필요)**

---

## 사전 작업 실행 결과

### 파일 백업
```
cp backend/app/services/feature_engine.py backend/app/services/feature_engine.py.bak.20260305_XXXX
cp config/param_search_space.yaml config/param_search_space.yaml.bak.20260305_XXXX
백업 완료
```

---

## 작업 1: config/param_search_space.yaml bj_score 섹션 추가

파일: `/root/kis-autotrade-v4/config/param_search_space.yaml`

```yaml
# ────────────────────────────────────────────────────────────
# T-121: BJ_SCORE 배진한 5원칙 정량화 엔진
# CEO D-008-KR §4-1. 대재수심차 5원칙 100점 만점 정량화
# BjScoreEngine에서 사용 / FunnelScore L3 보너스 통합
# ────────────────────────────────────────────────────────────
bj_score:
  major_shareholder:        # 대주주 (20점)
    min_share_pct: 5.0      # 최소 지분율
    ideal_range: [20.0, 50.0]
    weight: 20
  material_theme:           # 재료/테마 (20점)
    news_30d_min: 5
    theme_cycle_bonus: true
    weight: 20
  financial_numbers:        # 숫자/재무 (20점)
    revenue_growth_min: 0.10
    op_margin_min: 0.05
    roe_min: 0.08
    weight: 20
  sentiment_indicator:      # 심리/보조지표 (20점)
    rsi_range: [30, 70]
    vp_min: 100
    foreign_net_buy_days: 3
    weight: 20
  chart_ma:                 # 차트/이평선 (20점)
    ma_alignment: true      # 정배열 여부
    above_ma60: true
    weight: 20
```

결과: **성공** (d_d1_d2_entry 섹션 이후에 추가됨)

---

## 작업 2: BjScoreEngine 클래스 구현 (feature_engine.py)

파일: `/root/kis-autotrade-v4/backend/app/services/feature_engine.py`
추가 위치: 파일 말미 (DDayEntryEngine 클래스 이후)

### 구현된 메서드 목록

1. `_load_bj_score_params()` — YAML 파라미터 로드 헬퍼
2. `BjScoreEngine.__init__(params)` — YAML 파라미터 로드
3. `BjScoreEngine._fetch_shareholder_pct(symbol)` — stock_universe에서 대주주 지분율 조회
4. `BjScoreEngine._fetch_news_30d_count(symbol)` — v4_news_summary에서 30일 뉴스 건수
5. `BjScoreEngine._fetch_theme_cycle_score(symbol)` — ThemeCycleEngine에서 THEME_CYCLE_SCORE
6. `BjScoreEngine._fetch_financials(symbol)` — v4_fundamental_quarterly에서 재무 데이터
7. `BjScoreEngine._fetch_rsi_and_vp(symbol, date)` — ohlcv_daily에서 RSI(14)/VP 계산
8. `BjScoreEngine._fetch_foreign_net_buy_days(symbol, date)` — v4_investor_daily에서 외인 연속 순매수
9. `BjScoreEngine._fetch_ma_data(symbol, date)` — ohlcv_daily에서 MA5/10/20/60 계산
10. `BjScoreEngine.score_major_shareholder(symbol)` → 0~20
11. `BjScoreEngine.score_material_theme(symbol)` → 0~20
12. `BjScoreEngine.score_financial_numbers(symbol)` → 0~20
13. `BjScoreEngine.score_sentiment_indicator(symbol, date)` → 0~20
14. `BjScoreEngine.score_chart_ma(symbol, date)` → 0~20
15. `BjScoreEngine.calculate_bj_score(symbol, date)` → dict

### calculate_bj_score 반환 형식
```python
{
    'symbol': str,
    'date': str,
    'total': float,      # 0~100
    'grade': str,        # A/B/C/D
    'breakdown': {
        'major_shareholder': float,  # 0~20
        'material_theme': float,     # 0~20
        'financial_numbers': float,  # 0~20
        'sentiment_indicator': float,# 0~20
        'chart_ma': float,           # 0~20
    }
}
```

결과: **성공** (1,397라인 → 1,761라인, +364라인)

---

## 작업 3: FunnelScore L3 BJ_SCORE 보너스 통합 (funnel_score_engine.py)

파일: `/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py`

### 변경 내용

1. `score_l3` 시그니처 변경:
   ```python
   # 변경 전
   def score_l3(self, symbol: str) -> float:
   # 변경 후
   def score_l3(self, symbol: str, date: Optional[str] = None) -> float:
   ```

2. BJ_SCORE 보너스 블록 추가 (raw = ... 계산 전):
   ```python
   # T-121: BJ_SCORE(배진한 5원칙) 보너스
   bj_bonus = 0.0
   bj_total = 0
   bj_grade = "N/A"
   if date is not None:
       try:
           from backend.app.services.feature_engine import BjScoreEngine
           bj_engine = BjScoreEngine()
           bj_result = bj_engine.calculate_bj_score(symbol, date)
           bj_total = bj_result.get("total", 0)
           bj_grade = bj_result.get("grade", "D")
           if bj_total >= 80:
               bj_bonus = 0.20
           elif bj_total >= 60:
               bj_bonus = 0.10
           logger.info(
               "[BJ_SCORE] symbol=%s, total=%s, grade=%s, bonus=%.2f",
               symbol, bj_total, bj_grade, bj_bonus,
           )
       except Exception as e:
           logger.warning("L3[%s]: BjScoreEngine 조회 실패: %s", symbol, e)
   ```

3. raw 계산에 bj_bonus 추가:
   ```python
   raw = (
       growth_score * growth_weight
       + quality_score * quality_weight * 0.6
       + peg_score * 0.15
       + op_trend * 0.15
       + scq_bonus
       + bj_bonus  # T-121 추가
   )
   ```

4. `calculate_funnel_score`에서 `l3 = self.score_l3(symbol, date)` 로 date 전달

결과: **성공**

---

## 작업 4: tests/unit/test_bj_score.py 작성

파일: `/root/kis-autotrade-v4/tests/unit/test_bj_score.py`

### 테스트 목록 (27개)

| 클래스 | 테스트명 |
|--------|---------|
| TestMajorShareholder | test_ideal_range_returns_full_score |
| TestMajorShareholder | test_below_min_returns_zero |
| TestMajorShareholder | test_no_data_returns_zero |
| TestMajorShareholder | test_score_in_range |
| TestMaterialTheme | test_enough_news_returns_positive_score |
| TestMaterialTheme | test_no_news_returns_zero |
| TestMaterialTheme | test_theme_cycle_bonus_adds_to_score |
| TestFinancialNumbers | test_strong_financials_return_high_score |
| TestFinancialNumbers | test_no_data_returns_zero |
| TestFinancialNumbers | test_score_in_range |
| TestBjScoreTotal | test_perfect_score_is_100 |
| TestBjScoreTotal | test_zero_score_is_0 |
| TestBjScoreTotal | test_total_is_clamped_to_100 |
| TestBjGrade | test_grade_boundary[80.0-A] |
| TestBjGrade | test_grade_boundary[85.0-A] |
| TestBjGrade | test_grade_boundary[100.0-A] |
| TestBjGrade | test_grade_boundary[79.9-B] |
| TestBjGrade | test_grade_boundary[60.0-B] |
| TestBjGrade | test_grade_boundary[59.9-C] |
| TestBjGrade | test_grade_boundary[40.0-C] |
| TestBjGrade | test_grade_boundary[39.9-D] |
| TestBjGrade | test_grade_boundary[0.0-D] |
| TestBjScoreStructure | test_return_structure |
| TestYamlLoad | test_bj_score_yaml_section_exists |
| TestYamlLoad | test_yaml_weights_sum_to_100 |
| TestFunnelL3BjBonus | test_bj_score_80_gives_020_bonus |
| TestFunnelL3BjBonus | test_bj_score_60_gives_010_bonus |

결과: **성공**

---

## 작업 5: pytest 실행 결과

```
$ /root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/test_bj_score.py -v --tb=short

============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
...
collected 27 items

tests/unit/test_bj_score.py::TestMajorShareholder::test_ideal_range_returns_full_score PASSED [  3%]
tests/unit/test_bj_score.py::TestMajorShareholder::test_below_min_returns_zero PASSED [  7%]
tests/unit/test_bj_score.py::TestMajorShareholder::test_no_data_returns_zero PASSED [ 11%]
tests/unit/test_bj_score.py::TestMajorShareholder::test_score_in_range PASSED [ 14%]
tests/unit/test_bj_score.py::TestMaterialTheme::test_enough_news_returns_positive_score PASSED [ 18%]
tests/unit/test_bj_score.py::TestMaterialTheme::test_no_news_returns_zero PASSED [ 22%]
tests/unit/test_bj_score.py::TestMaterialTheme::test_theme_cycle_bonus_adds_to_score PASSED [ 25%]
tests/unit/test_bj_score.py::TestFinancialNumbers::test_strong_financials_return_high_score PASSED [ 29%]
tests/unit/test_bj_score.py::TestFinancialNumbers::test_no_data_returns_zero PASSED [ 33%]
tests/unit/test_bj_score.py::TestFinancialNumbers::test_score_in_range PASSED [ 37%]
tests/unit/test_bj_score.py::TestBjScoreTotal::test_perfect_score_is_100 PASSED [ 40%]
tests/unit/test_bj_score.py::TestBjScoreTotal::test_zero_score_is_0 PASSED [ 44%]
tests/unit/test_bj_score.py::TestBjScoreTotal::test_total_is_clamped_to_100 PASSED [ 48%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[80.0-A] PASSED [ 51%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[85.0-A] PASSED [ 55%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[100.0-A] PASSED [ 59%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[79.9-B] PASSED [ 62%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[60.0-B] PASSED [ 66%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[59.9-C] PASSED [ 70%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[40.0-C] PASSED [ 74%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[39.9-D] PASSED [ 77%]
tests/unit/test_bj_score.py::TestBjGrade::test_grade_boundary[0.0-D] PASSED [ 81%]
tests/unit/test_bj_score.py::TestBjScoreStructure::test_return_structure PASSED [ 85%]
tests/unit/test_bj_score.py::TestYamlLoad::test_bj_score_yaml_section_exists PASSED [ 88%]
tests/unit/test_bj_score.py::TestYamlLoad::test_yaml_weights_sum_to_100 PASSED [ 92%]
tests/unit/test_bj_score.py::TestFunnelL3BjBonus::test_bj_score_80_gives_020_bonus PASSED [ 96%]
tests/unit/test_bj_score.py::TestFunnelL3BjBonus::test_bj_score_60_gives_010_bonus PASSED [100%]

============================== 27 passed in 0.58s ==============================
```

**전체 unit test:**
```
1 failed (pre-existing: test_funnel_score_engine.py::TestScoreL2::test_score_l2_dual_flow_high),
254 passed, 1 warning in 7.55s
```

- 기존 실패 테스트는 T-121 이전부터 동일하게 실패 (이번 작업과 무관, git stash로 확인)
- T-121 신규 27개 ALL PASS ✅

---

## 작업 6: git commit

```
$ git add backend/app/services/feature_engine.py backend/app/services/funnel_score_engine.py \
    config/param_search_space.yaml tests/unit/test_bj_score.py

$ git commit -m "[V4.1] T-121: BJ_SCORE 배진한 5원칙 정량화 — L3 보너스 통합"

[phase-2c-command-center d7fea642] [V4.1] T-121: BJ_SCORE 배진한 5원칙 정량화 — L3 보너스 통합
 4 files changed, 1377 insertions(+), 5 deletions(-)
 create mode 100644 tests/unit/test_bj_score.py
```

**커밋 해시**: `d7fea642`
**브랜치**: `phase-2c-command-center`

---

## 작업 7: git push

```
$ git push origin phase-2c-command-center

git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**상태**: SSH 키 미설정 (claudebot 계정) → **root에서 수동 push 필요**

```bash
# root에서 실행:
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center
```

---

## 완료 조건 체크

- [x] bj_score YAML 섹션 생성
- [x] BjScoreEngine 6메서드 구현 (실제 DB 헬퍼 포함 15메서드)
- [x] FunnelScore L3 보너스 통합 (+0.10/+0.20)
- [x] 27개 테스트 ALL PASS (10개 이상 완료)
- [x] git commit `d7fea642`
- [ ] git push (SSH 권한 미비 — root 수동 필요)
- [ ] 보고서 project-docs push (done_watcher.sh 자동 처리 예정)
- [ ] HANDOVER.md 업데이트 (done_watcher.sh 자동 처리 예정)

---

## 필수 후속 조치 (root에서 실행)

```bash
# 1. 코드 push
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center

# 2. 보고서 project-docs 동기화
cp /root/kis-autotrade-v4/report/v41/CUR-V41-BJ-SCORE-001-20260305.md \
   /root/project-docs/kis-autotrade-v4/reports/CUR-V41-BJ-SCORE-001-20260305.md
cd /root/project-docs
git add kis-autotrade-v4/reports/CUR-V41-BJ-SCORE-001-20260305.md
git commit -m "[DOCS] T-121 BJ_SCORE 보고서"
git push origin master

# 3. HANDOVER.md 업데이트: T-121 항목 추가
# 섹션 2 완료된 작업 테이블에 T-121 행 추가
# 섹션 6 웹Claude 인수인계 갱신
```

---

## 로컬 보고서 경로

```
PATH-001: /root/kis-autotrade-v4/report/v41/CUR-V41-BJ-SCORE-001-20260305.md
REPORT-001: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-BJ-SCORE-001-20260305.md (push 필요)
```
