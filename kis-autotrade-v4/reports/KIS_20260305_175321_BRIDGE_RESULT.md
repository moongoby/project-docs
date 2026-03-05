---
project: kis-autotrade-v4
task_id: T-119
completed_at: 2026-03-05T18:10:02 KST
---

# T-119 실행 결과: DESK5 GrowthScore ALL NONE 해결

## 지시서 원문
```
Task ID: T-119 제목: DESK5 GrowthScore 20종목 ALL NONE 개선 서버: 211 (kis-autotrade-v4) 우선순위: P1-HIGH 예상 시간: 12분 의존성: T-098 (GrowthScoreEngine 완료)
```

---

## 1. 사전 작업 (백업)

```bash
cp /root/kis-autotrade-v4/backend/app/services/growth_score_engine.py /root/kis-autotrade-v4/backend/app/services/growth_score_engine.py.bak.20260305_1809
cp /root/kis-autotrade-v4/config/param_search_space.yaml /root/kis-autotrade-v4/config/param_search_space.yaml.bak.20260305_1809
```
결과: 백업 완료

---

## 2. 데이터 진단

### v4_fundamental_quarterly 현황
```sql
SELECT symbol, COUNT(*) as quarters FROM v4_fundamental_quarterly GROUP BY symbol ORDER BY quarters DESC LIMIT 20;
```
결과: 기존 종목들은 최대 7분기까지 데이터 있음. 단, 이들은 DESK5 종목이 아님.

### DESK5 watchlist 현황
```python
# v4_desk5_watchlist 컬럼 확인
columns: ['id', 'stock_code', 'stock_name', 'scan_date', 'status', ..., 'theme_news_count_30d', ...]
```

DESK5 20종목:
```
['383220', '0005A0', '0013R0', '008730', '028300', '041190', '053030', '053060',
 '214390', '300720', '438100', '006880', '126880', '214680', '0015F0', '003230',
 '003300', '003610', '006040', '008970']
```

**근본 원인 1**: DESK5 20종목 전부 `v4_fundamental_quarterly`에 데이터 없음 (T-098 수집 누락)
```
Has fundamental data: []
NO fundamental data: 20/20 종목 전부
```

**근본 원인 2**: `v4_news_feed` 테이블 자체 없음 → `_fetch_news_count_30d()` 항상 0 반환

**근본 원인 3**: `classify_stock()` 로직 — rows 빈 배열이면 뉴스 체크 없이 즉시 NONE 반환

```python
# 기존 코드 (문제)
if not rows:
    return {"axis": "NONE", "growth_score": 0.0, ...}  # 뉴스 체크도 안 함
```

---

## 3. 수정 내용

### 3-A. growth_score_engine.py 수정

**파일**: `/root/kis-autotrade-v4/backend/app/services/growth_score_engine.py`

#### _DEFAULT_PARAMS 임계값 완화
```python
# 변경 전
"axis1_revenue_yoy_min": 0.50,
"axis2_op_growth_yoy_min": 0.15,

# 변경 후 (T-119)
"axis1_revenue_yoy_min": 0.30,     # 0.50→0.30 완화
"axis2_op_growth_yoy_min": 0.05,   # 0.15→0.05 완화
"min_quarters": 4,                  # 신규: 8→4
"min_revenue_growth": 0.05,         # 신규
"default_axis1_score": 0.3,         # 신규: fallback 점수
```

#### _fetch_fundamental() — min_quarters 파라미터화
```python
def _fetch_fundamental(self, symbol: str) -> List[Dict[str, Any]]:
    """DB에서 최근 min_quarters 분기 재무 데이터 조회."""
    limit = self.params.get("min_quarters", 4)
    # ... LIMIT %s 사용
```

#### _fetch_news_from_watchlist() 신규 메서드
```python
def _fetch_news_from_watchlist(self, symbol: str) -> int:
    """v4_desk5_watchlist.theme_news_count_30d fallback (v4_news_feed 없을 때)."""
    cur.execute(
        "SELECT theme_news_count_30d FROM v4_desk5_watchlist "
        "WHERE stock_code = %s ORDER BY updated_at DESC LIMIT 1",
        (symbol,),
    )
```

#### _fetch_news_count_30d() fallback 추가
```python
def _fetch_news_count_30d(self, symbol: str) -> int:
    try:
        # v4_news_feed 시도
        ...
    except Exception:
        # v4_news_feed 테이블 없음 → v4_desk5_watchlist fallback
        return self._fetch_news_from_watchlist(symbol)
```

#### classify_stock() — 빈 rows 처리 로직 수정
```python
if not rows:
    # 재무 데이터 없음 → 뉴스 기반 fallback (T-119)
    news_30d = self._fetch_news_count_30d(symbol)
    news_min = p.get("axis1_news_30d_min", 5)
    if news_30d >= news_min:
        default_score = p.get("default_axis1_score", 0.3)
        logger.warning(
            "[GROWTH_SCORE] %s classified AXIS1_EXPECTATION (fallback): "
            "no fundamental data, news_30d=%d >= threshold=%d, score=%.2f",
            symbol, news_30d, news_min, default_score,
        )
        details["fallback"] = "no_fundamental_news_based"
        return {
            "axis": "AXIS1_EXPECTATION",
            "growth_score": default_score,
            "recommended_desk": "DESK5",
            "details": details,
        }
    logger.warning(
        "[GROWTH_SCORE] %s classified NONE: no fundamental data, "
        "news_30d=%d < threshold=%d",
        symbol, news_30d, news_min,
    )
    return {"axis": "NONE", "growth_score": 0.0, ...}
```

#### NONE 분류 시 warning 로깅 강화
```python
else:
    logger.warning(
        "[GROWTH_SCORE] %s classified NONE: axis1=%s, axis2=%s, ...",
        symbol, axis1_reasons, axis2_reasons, ...
    )
```

### 3-B. param_search_space.yaml 수정

**파일**: `/root/kis-autotrade-v4/config/param_search_space.yaml`

```yaml
growth_score:
  axis1_revenue_yoy_min: 0.30        # T-119: 0.50→0.30 완화
  axis2_op_growth_yoy_min: 0.05      # T-119: 0.15→0.05 완화
  min_quarters: 4                    # T-119: 재무 조회 최소 분기 수 (8→4)
  min_revenue_growth: 0.05           # T-119: 신규 일반 최소 매출 성장률 임계값
  default_axis1_score: 0.3           # T-119: 재무 데이터 없을 때 뉴스 기반 fallback 점수
```

---

## 4. 단위 테스트

**파일**: `/root/kis-autotrade-v4/tests/unit/test_growth_score_fix.py`

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
collected 6 items

tests/unit/test_growth_score_fix.py::test_desk5_not_all_none PASSED      [ 16%]
tests/unit/test_growth_score_fix.py::test_insufficient_data_fallback PASSED [ 33%]
tests/unit/test_growth_score_fix.py::test_threshold_relaxation PASSED    [ 50%]
tests/unit/test_growth_score_fix.py::test_score_range PASSED             [ 66%]
tests/unit/test_growth_score_fix.py::test_yaml_update PASSED             [ 83%]
tests/unit/test_growth_score_fix.py::test_none_default_score PASSED      [100%]

============================== 6 passed in 0.17s ===============================
```

**결과: 6/6 ALL PASS**

---

## 5. 실제 DB 검증

```python
/root/kis-autotrade-v4/venv/bin/python3 -c "
from backend.app.services.growth_score_engine import GrowthScoreEngine
engine = GrowthScoreEngine()
desk5_symbols = ['383220','0005A0','0013R0','008730','028300','041190','053030','053060',
                 '214390','300720','438100','006880','126880','214680','0015F0','003230',
                 '003300','003610','006040','008970']
results = [engine.classify_stock(sym) for sym in desk5_symbols]
"
```

실행 로그:
```
[GROWTH_SCORE] 383220 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=29 >= threshold=5, score=0.30
[GROWTH_SCORE] 0005A0 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=5 >= threshold=5, score=0.30
[GROWTH_SCORE] 0013R0 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=5 >= threshold=5, score=0.30
[GROWTH_SCORE] 008730 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=13 >= threshold=5, score=0.30
[GROWTH_SCORE] 028300 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=94 >= threshold=5, score=0.30
[GROWTH_SCORE] 041190 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=9 >= threshold=5, score=0.30
[GROWTH_SCORE] 053030 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=10 >= threshold=5, score=0.30
[GROWTH_SCORE] 053060 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=9 >= threshold=5, score=0.30
[GROWTH_SCORE] 214390 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=14 >= threshold=5, score=0.30
[GROWTH_SCORE] 300720 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=12 >= threshold=5, score=0.30
[GROWTH_SCORE] 438100 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=11 >= threshold=5, score=0.30
[GROWTH_SCORE] 006880 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=12 >= threshold=5, score=0.30
[GROWTH_SCORE] 126880 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=6 >= threshold=5, score=0.30
[GROWTH_SCORE] 214680 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=13 >= threshold=5, score=0.30
[GROWTH_SCORE] 0015F0 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=5 >= threshold=5, score=0.30
[GROWTH_SCORE] 003230 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=122 >= threshold=5, score=0.30
[GROWTH_SCORE] 003300 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=9 >= threshold=5, score=0.30
[GROWTH_SCORE] 003610 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=17 >= threshold=5, score=0.30
[GROWTH_SCORE] 006040 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=56 >= threshold=5, score=0.30
[GROWTH_SCORE] 008970 classified AXIS1_EXPECTATION (fallback): no fundamental data, news_30d=10 >= threshold=5, score=0.30

--- 결과 요약 ---
전체: 20, NONE: 0, 분류성공: 20
NONE < 50% 기준: PASS
```

---

## 6. git commit

```bash
git add backend/app/services/growth_score_engine.py config/param_search_space.yaml tests/unit/test_growth_score_fix.py
git commit -m "[V4.1] T-119: DESK5 GrowthScore ALL NONE 해결 — 임계값 완화 + fallback 추가"
```

결과:
```
[phase-2c-command-center 060786f2] [V4.1] T-119: DESK5 GrowthScore ALL NONE 해결 — 임계값 완화 + fallback 추가
 3 files changed, 318 insertions(+), 9 deletions(-)
 create mode 100644 tests/unit/test_growth_score_fix.py
```

git push: **claudebot SSH 키 미설정으로 불가 (로컬 커밋 완료, root에서 push 필요)**

---

## 7. 완료 기준 체크

| 기준 | 결과 |
|------|------|
| DESK5 20종목 중 NONE < 50% (10종목 이상 분류 성공) | ✅ NONE=0%, 분류성공=20/20 (100%) |
| fallback 작동 (재무 없음 → 뉴스 기반 AXIS1) | ✅ 전 종목 fallback 정상 작동 |
| 6/6 테스트 PASS | ✅ 6/6 ALL PASS (0.17s) |
| 코드 레포 커밋 | ✅ 060786f2 |
| git push | ⚠️ 로컬 커밋 완료, claudebot SSH 키 미설정으로 push 미완료 |
| HANDOVER 갱신 | ⚠️ root 권한 필요, done_watcher.sh가 처리 예정 |

---

## 8. 추가 발견 사항

- `v4_desk5_watchlist.theme_news_count_30d`는 이미 최신 값으로 유지됨 (watchlist 업데이트 시 자동 갱신)
- DESK5 뉴스 건수 범위: 5~122건 (모든 종목 threshold=5 충족)
- `v4_news_feed` 테이블은 현재 없음 → watchlist fallback이 주 경로로 동작
- T-098 완료 후 DESK5 종목 fundamental 수집 시 자동으로 정상 경로(재무 기반)로 전환됨
