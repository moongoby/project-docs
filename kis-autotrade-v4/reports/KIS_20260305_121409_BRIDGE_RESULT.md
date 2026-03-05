---
project: kis-autotrade-v4
task_id: T-098
completed_at: 2026-03-05T12:25:00+09:00
---

# T-098 실행 결과 보고서 — 펀더멘탈 데이터 수집 + Growth Score 엔진

## 지시서 원문
파일: /root/.genspark/directives/running/KIS_20260305_121409_BRIDGE.md

---

## 작업 1: DB 마이그레이션 060 — v4_fundamental_quarterly 테이블

### 실행 파일
`backend/migrations/061_v4_fundamental_quarterly.sql`

> 주의: 기존 060_v4_positions_capital_idle_days.sql 존재로 061 번호 사용

### SQL 내용
```sql
CREATE TABLE IF NOT EXISTS v4_fundamental_quarterly (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    fiscal_year INT NOT NULL,
    fiscal_quarter INT NOT NULL,
    revenue BIGINT,
    operating_profit BIGINT,
    net_income BIGINT,
    eps NUMERIC(12,2),
    bps NUMERIC(12,2),
    roe NUMERIC(8,4),
    per NUMERIC(8,2),
    pbr NUMERIC(8,4),
    operating_margin NUMERIC(8,4),
    revenue_growth_yoy NUMERIC(8,4),
    op_growth_yoy NUMERIC(8,4),
    consensus_eps NUMERIC(12,2),
    earnings_surprise NUMERIC(8,4),
    data_source VARCHAR(50) DEFAULT 'KIS_API',
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(symbol, fiscal_year, fiscal_quarter)
);
CREATE INDEX IF NOT EXISTS idx_fundamental_symbol ON v4_fundamental_quarterly(symbol);
CREATE INDEX IF NOT EXISTS idx_fundamental_quarter ON v4_fundamental_quarterly(fiscal_year, fiscal_quarter);
CREATE INDEX IF NOT EXISTS idx_fundamental_growth ON v4_fundamental_quarterly(revenue_growth_yoy);
```

### 실행 결과 (psql 출력 원문)
```
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
 table_exists
--------------
            1
(1 row)
```

### 검증
- `SELECT count(*) FROM information_schema.tables WHERE table_name='v4_fundamental_quarterly'; → 1` ✓

---

## 작업 2: 재무 데이터 수집기 신규 생성

### 파일: backend/app/services/fundamental_collector.py

```python
"""
T-098 — FundamentalCollector
KIS API 재무제표 수집기 (FHKST66430100, FHKST66430200)

rate limit: 1초 1건 (KIS API 제한 준수)
대상: DESK5(20) + DESK4(18) + DESK3(106) 전 종목
"""
```

### 구현된 메서드

#### 1. `fetch_financial_ratio(self, symbol: str) -> dict`
- KIS API FHKST66430100 호출
- 최근 8분기(2년) 매출·영업이익·순이익·ROE·영업이익률 수집
- stac_yymm → fiscal_year, fiscal_quarter 변환 (YYYYMM → year, quarter)
- 백만원 단위 → 원 단위 변환 (×1,000,000)
- rate limit: time.sleep(1.0)
- 반환: `{"symbol", "quarters": [{"year", "quarter", "revenue", "operating_profit", "net_income", "roe", "operating_margin"}]}`

#### 2. `fetch_investment_indicator(self, symbol: str) -> dict`
- KIS API FHKST66430200 호출
- 최근 8분기 EPS·BPS·PER·PBR 수집
- rate limit: time.sleep(1.0)
- 반환: `{"symbol", "quarters": [{"year", "quarter", "eps", "bps", "per", "pbr"}]}`

#### 3. `calculate_growth_metrics(self, symbol: str) -> dict`
- DB v4_fundamental_quarterly에서 최근 8분기 조회
- YoY 성장률: 같은 분기 전년 데이터와 비교
  - revenue_growth_yoy = (rev_latest - rev_prev) / abs(rev_prev)
  - op_growth_yoy = (op_latest - op_prev) / abs(op_prev)
  - eps_growth_yoy = (eps_latest - eps_prev) / abs(eps_prev)
- ROE 추세: 최근 3분기 ROE[0] - ROE[-1] (증가이면 양수)
- 데이터 없으면 `{revenue_growth_yoy: None, op_growth_yoy: None, eps_growth_yoy: None, roe_trend: None}` 반환

#### 4. `collect_all_desk_symbols(self) -> int`
- v4_desk5_watchlist (status='ACTIVE'), v4_desk4_watchlist (ACTIVE), v4_desk3_pool (ACTIVE) 조회
- 중복 제거 후 순차 수집
- 각 종목: fetch_financial_ratio + fetch_investment_indicator + calculate_growth_metrics → UPSERT
- 반환: 수집 성공 종목 수

---

## 작업 3: Growth Score 엔진 신규 생성

### 파일: backend/app/services/growth_score_engine.py

```python
"""
T-098 — GrowthScoreEngine
CEO 2축 분류: 축1(기대가치) vs 축2(실현가치)
"""
```

### 구현된 메서드

#### 1. `classify_stock(self, symbol: str) -> dict`

**축1 (기대가치 — DESK5 적합) 판별 조건:**
- 조건 A: revenue_qoq ≥ axis1_revenue_qoq_min(0.20) AND (영업이익 <= 0 OR operating_margin < 5%)
- 조건 B: news_30d >= axis1_news_30d_min(5)
- 조건 C: revenue_yoy >= axis1_revenue_yoy_min(0.50)

**축2 (실현가치 — DESK3/4 적합) 판별 조건:**
- 조건 A: op_yoy >= axis2_op_growth_yoy_min(0.15) AND roe >= axis2_roe_min(0.10)
- 조건 B: PEG = per / (eps_growth × 100) < axis2_peg_max(1.0)
- 조건 C: 최근 3분기 연속 영업이익 증가 (op[i] > op[i+1] for i in range(2))

**결정 로직:**
- 축1만: `AXIS1_EXPECTATION`, `recommended_desk: DESK5`
- 축2만: `AXIS2_REALIZATION`, `recommended_desk: DESK3`
- 둘 다: growth_score >= 0.6 → AXIS2/DESK4, else AXIS1/DESK5
- 없음: `NONE`, `recommended_desk: NONE`

**반환 형식:**
```json
{
  "axis": "AXIS1_EXPECTATION | AXIS2_REALIZATION | NONE",
  "growth_score": 0.0~1.0,
  "recommended_desk": "DESK5 | DESK4 | DESK3 | NONE",
  "details": {
    "symbol": "...",
    "quarters_loaded": N,
    "revenue_qoq": ...,
    "revenue_yoy": ...,
    "op_yoy": ...,
    "roe": ...,
    "news_30d": N,
    "axis1_reasons": [...],
    "axis2_reasons": [...],
    "peg": ...
  }
}
```

#### 2. `score_growth(self, symbol: str) -> float`

**가중치 공식:**
```
score = s_revenue × 0.25
      + s_op       × 0.25
      + s_roe      × 0.20
      + s_surprise × 0.15
      + s_peg      × 0.15
```

**각 점수 계산:**
- s_revenue: min(1.0, max(0.0, revenue_yoy / 0.5))
- s_op: min(1.0, max(0.0, op_yoy / 0.3))
- s_roe: min(1.0, max(0.0, (roe[0]-roe[-1]) / 0.05 + 0.5)) — 3분기 추세
- s_surprise: min(1.0, max(0.0, surprise / 0.20 + 0.5))
- s_peg: peg < peg_max → 1 - peg/peg_max, else max(0, 1 - peg/(peg_max×3))

**반환**: 0.0~1.0 (round 4자리)

#### 3. `filter_no_growth(self, symbols: list) -> list`
- 각 종목 classify_stock() 호출
- axis == "NONE"인 종목 removed 리스트에 추가
- 반환: 제거된 종목 리스트

---

## 작업 4: param_search_space.yaml 추가

### 추가 위치
`config/param_search_space.yaml` 말미 (hypothesis_winners 섹션 다음)

### 추가된 내용 원문
```yaml
# ────────────────────────────────────────────────────────────
# T-098: Growth Score 엔진 파라미터
# CEO 2축 분류: 축1(기대가치) vs 축2(실현가치)
# GrowthScoreEngine에서 사용
# ────────────────────────────────────────────────────────────
growth_score:
  axis1_revenue_qoq_min: 0.20        # 축1 매출 QoQ 최소 성장률
  axis1_revenue_yoy_min: 0.50        # 축1 매출 YoY 최소 성장률
  axis1_news_30d_min: 5              # 축1 테마 뉴스 최소 건수
  axis2_op_growth_yoy_min: 0.15      # 축2 영업이익 YoY 최소 성장률
  axis2_roe_min: 0.10                # 축2 ROE 최소
  axis2_peg_max: 1.0                 # 축2 PEG 최대
  axis2_consecutive_op_quarters: 3   # 축2 연속 영업이익 증가 분기수
  weight_revenue: 0.25
  weight_op: 0.25
  weight_roe_trend: 0.20
  weight_surprise: 0.15
  weight_peg: 0.15
```

### 검증
- 가중치 합계: 0.25 + 0.25 + 0.20 + 0.15 + 0.15 = 1.00 ✓

---

## 작업 5: Node Detector 연동 — 성장 필터 추가

### 파일 1: backend/app/services/desk_filters/node_detector_desk5.py

**추가된 import 섹션 (모듈 레벨):**
```python
# T-098: GrowthScoreEngine 연동 (성장 필터)
try:
    from backend.app.services.growth_score_engine import GrowthScoreEngine as _GrowthScoreEngine
    _growth_engine = _GrowthScoreEngine()
except Exception:
    _growth_engine = None  # type: ignore
```

**classify_phase 시그니처 변경:**
```python
def classify_phase(
    self, bars: List[Dict], stock_code: Optional[str] = None
) -> Tuple[str, int]:
```

**추가된 성장 필터 로직 (메서드 말미):**
```python
# T-098: GrowthScoreEngine 성장 필터 적용
if stock_code and _growth_engine is not None:
    try:
        result = _growth_engine.classify_stock(stock_code)
        axis = result.get("axis", "")
        if axis == "NONE":
            confidence = max(0, confidence - 30)
            logger.debug("DESK5 %s: 성장 근거 없음 → confidence -30 = %d", stock_code, confidence)
        elif axis == "AXIS1_EXPECTATION":
            confidence = min(100, confidence + 20)
            logger.debug("DESK5 %s: AXIS1 → confidence +20 = %d", stock_code, confidence)
    except Exception as ge:
        logger.warning("DESK5 growth filter 오류 %s: %s", stock_code, ge)
```

### 파일 2: backend/app/services/desk_filters/node_detector_desk3.py

**추가된 import 섹션 (모듈 레벨):**
```python
# T-098: GrowthScoreEngine 연동 (성장 필터)
try:
    from backend.app.services.growth_score_engine import GrowthScoreEngine as _GrowthScoreEngine
    _growth_engine = _GrowthScoreEngine()
except Exception:
    _growth_engine = None  # type: ignore
```

**classify_phase 시그니처 변경:**
```python
def classify_phase(
    self,
    bars: List[Dict],
    layer_score: float = 0.0,
    stock_code: Optional[str] = None,
) -> Tuple[str, int]:
```

**추가된 성장 필터 로직 (메서드 말미):**
```python
# T-098: GrowthScoreEngine 성장 필터 적용
if stock_code and _growth_engine is not None:
    try:
        result = _growth_engine.classify_stock(stock_code)
        axis = result.get("axis", "")
        if axis == "AXIS2_REALIZATION":
            confidence = min(100, confidence + 15)
            logger.debug("DESK3 %s: AXIS2 → confidence +15 = %d", stock_code, confidence)
        elif axis == "NONE":
            confidence = max(0, confidence - 20)
            logger.debug("DESK3 %s: 성장 근거 없음 → confidence -20 = %d", stock_code, confidence)
    except Exception as ge:
        logger.warning("DESK3 growth filter 오류 %s: %s", stock_code, ge)
```

---

## 작업 6: 단위테스트 10건

### 파일: tests/test_growth_score.py

### pytest 실행 결과 원문
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 10 items

tests/test_growth_score.py::test_01_table_exists PASSED                  [ 10%]
tests/test_growth_score.py::test_02_fundamental_collector_instantiation PASSED [ 20%]
tests/test_growth_score.py::test_03_calculate_growth_metrics_empty PASSED [ 30%]
tests/test_growth_score.py::test_04_growth_score_engine_instantiation PASSED [ 40%]
tests/test_growth_score.py::test_05_classify_axis1 PASSED                [ 50%]
tests/test_growth_score.py::test_06_classify_axis2 PASSED                [ 60%]
tests/test_growth_score.py::test_07_classify_none PASSED                 [ 70%]
tests/test_growth_score.py::test_08_score_growth_range PASSED            [ 80%]
tests/test_growth_score.py::test_09_filter_no_growth PASSED              [ 90%]
tests/test_growth_score.py::test_10_yaml_growth_score_params PASSED      [100%]

============================== 10 passed in 0.45s ==============================
```

**결과: 10/10 ALL PASS** ✓

### 테스트 목록
1. `test_01_table_exists`: v4_fundamental_quarterly 테이블 DB 존재 확인
2. `test_02_fundamental_collector_instantiation`: FundamentalCollector 인스턴스 + 4메서드 존재
3. `test_03_calculate_growth_metrics_empty`: 존재하지 않는 종목 → 모두 None 반환
4. `test_04_growth_score_engine_instantiation`: GrowthScoreEngine 인스턴스 + 3메서드 존재
5. `test_05_classify_axis1`: 매출YoY=60% → AXIS1_EXPECTATION, recommended_desk=DESK5
6. `test_06_classify_axis2`: 영업이익YoY=20% + ROE=15% → AXIS2_REALIZATION
7. `test_07_classify_none`: 매출YoY=2%, 영업이익YoY=3% → NONE
8. `test_08_score_growth_range`: 빈 데이터=0.0, 고성장=0~1, 저성장=0~1 모두 범위 내
9. `test_09_filter_no_growth`: NONE 종목 2개 제거, AXIS1/AXIS2 종목 보존
10. `test_10_yaml_growth_score_params`: growth_score 섹션 존재, 11개 키, 가중치합=1.0

---

## 작업 7: HANDOVER.md v9.7 갱신

### 갱신 내용
- 헤더 v9.6 → v9.7 (T-098 설명 추가)
- 완료된 작업 테이블에 T-098 행 추가
- 버전 이력에 v9.7 행 추가

### 갱신 파일
`/root/project-docs/kis-autotrade-v4/HANDOVER.md`

**git 상태:**
- HANDOVER.md: staged (modified)
- CUR-V41-GROWTH-SCORE-001-20260305.md: untracked (신규)

> 주의: git commit은 root 권한 필요. done_watcher.sh가 자동 처리 예정.

---

## 완료 기준 최종 체크

| 완료 기준 | 결과 |
|-----------|------|
| v4_fundamental_quarterly 테이블 생성 확인 | ✓ (table_exists=1) |
| fundamental_collector.py 4메서드 구현 | ✓ |
| growth_score_engine.py 3메서드 구현 (classify_stock, score_growth, filter_no_growth) | ✓ |
| node_detector_desk5.py, node_detector_desk3.py에 성장 필터 적용 | ✓ |
| 10건 단위테스트 ALL PASS | ✓ (10/10) |
| param_search_space.yaml growth_score 섹션 추가 | ✓ |
| HANDOVER.md v9.7 갱신 | ✓ |
| 보고서 작성 | ✓ /root/project-docs/kis-autotrade-v4/reports/CUR-V41-GROWTH-SCORE-001-20260305.md |

---

## 생성/수정된 파일 목록

| 파일 | 상태 | 설명 |
|------|------|------|
| `backend/migrations/061_v4_fundamental_quarterly.sql` | 신규 | DB 마이그레이션 |
| `backend/app/services/fundamental_collector.py` | 신규 | KIS API 재무 수집기 |
| `backend/app/services/growth_score_engine.py` | 신규 | CEO 2축 Growth Score 분류 엔진 |
| `config/param_search_space.yaml` | 수정 | growth_score 섹션 추가 |
| `backend/app/services/desk_filters/node_detector_desk5.py` | 수정 | AXIS1/NONE confidence 조정 |
| `backend/app/services/desk_filters/node_detector_desk3.py` | 수정 | AXIS2/NONE confidence 조정 |
| `tests/test_growth_score.py` | 신규 | 단위테스트 10건 |
| `/root/project-docs/kis-autotrade-v4/HANDOVER.md` | 수정 | v9.7 갱신 |
| `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-GROWTH-SCORE-001-20260305.md` | 신규 | 보고서 |

---

## 체크포인트

- [x] 코드 레포 작업 완료 (kis-autotrade-v4 — 파일 생성/수정)
- [x] project-docs 보고서 작성 완료 (HANDOVER.md v9.7 + 보고서 파일)
- [ ] GitHub raw URL 200 확인 (done_watcher.sh 자동 push 대기)

HANDOVER.md 업데이트 완료: (done_watcher.sh push 대기 중)
