# CUR-V41-GROWTH-SCORE-001 — T-098 펀더멘탈 Growth Score 엔진

**날짜**: 2026-03-05
**Task ID**: T-098
**작성자**: Claude Code (Sonnet 4.6)
**서버**: 211 (kis-autotrade-v4)
**우선순위**: P0-CRITICAL
**의존성**: T-097 (확인매매 엔진)

---

[인계 확인]
직전 완료: T-097
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002
strategy_cards: 60
open_positions: 14

---

## 배경

CEO 핵심 질문: "주식은 기업 성장의 거울. 미래 성장(기대가치)인가, 현재 성장(실현가치)인가?"

현재 시스템은 가격·수급·뉴스만 추적하며 재무제표를 보유하지 않음. 이익 성장 데이터가 없으면 "왜 수급이 들어오는가"를 판별할 수 없고, DESK5 대파동 포착(M3=0%)의 근본 해결이 불가.

---

## 작업 1: DB 마이그레이션 061_v4_fundamental_quarterly.sql

### 파일 경로
`backend/migrations/061_v4_fundamental_quarterly.sql`

### 실행 결과
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

### 생성된 테이블 구조
- `v4_fundamental_quarterly`: symbol, fiscal_year, fiscal_quarter, revenue, operating_profit, net_income, eps, bps, roe, per, pbr, operating_margin, revenue_growth_yoy, op_growth_yoy, consensus_eps, earnings_surprise, data_source, collected_at
- 인덱스 3개: idx_fundamental_symbol, idx_fundamental_quarter, idx_fundamental_growth
- UNIQUE 제약: (symbol, fiscal_year, fiscal_quarter)

> **주의**: 기존에 `060_v4_positions_capital_idle_days.sql`이 존재하여 `061`로 번호 조정

---

## 작업 2: FundamentalCollector 신규 생성

### 파일 경로
`backend/app/services/fundamental_collector.py`

### 구현 메서드 (4개)

#### `fetch_financial_ratio(symbol: str) → dict`
- KIS API FHKST66430100 호출
- 최근 8분기 매출·영업이익·순이익·ROE·영업이익률 수집
- rate limit: 1초 슬립

#### `fetch_investment_indicator(symbol: str) → dict`
- KIS API FHKST66430200 호출
- 최근 8분기 EPS·BPS·PER·PBR 수집
- rate limit: 1초 슬립

#### `calculate_growth_metrics(symbol: str) → dict`
- DB에서 최근 8분기 조회
- YoY 성장률 계산 (같은 분기 전년 비교)
- ROE 3분기 추세 계산
- 반환: `{revenue_growth_yoy, op_growth_yoy, eps_growth_yoy, roe_trend}`
- 데이터 없으면 모두 `None` 반환

#### `collect_all_desk_symbols() → int`
- v4_desk5_watchlist + v4_desk4_watchlist + v4_desk3_pool 전 종목 조회
- 각 종목 순차 수집 (rate limit 준수)
- v4_fundamental_quarterly UPSERT
- 반환: 수집 성공 종목 수

---

## 작업 3: GrowthScoreEngine 신규 생성

### 파일 경로
`backend/app/services/growth_score_engine.py`

### CEO 2축 분류

#### 축1 (기대가치 — DESK5 적합)
- 조건 A: 매출 QoQ ≥ +20% AND 영업이익 적자 또는 낮음
- 조건 B: 테마 뉴스 30일 ≥ 5건
- 조건 C: 매출 YoY ≥ +50% (초기 성장 폭발)

#### 축2 (실현가치 — DESK3/4 적합)
- 조건 A: 영업이익 YoY ≥ +15% AND ROE ≥ 10%
- 조건 B: PEG < 1.0 (PER / EPS성장률×100)
- 조건 C: 3분기 연속 영업이익 증가

### 구현 메서드 (3개)

#### `classify_stock(symbol: str) → dict`
- 반환: `{axis, growth_score, recommended_desk, details}`
- axis: `AXIS1_EXPECTATION | AXIS2_REALIZATION | NONE`
- recommended_desk: `DESK5 | DESK4 | DESK3 | NONE`

#### `score_growth(symbol: str) → float`
- 0.0~1.0 범위 성장 점수
- 가중치: revenue×0.25 + op×0.25 + roe_trend×0.20 + surprise×0.15 + peg_inv×0.15

#### `filter_no_growth(symbols: list) → list`
- NONE 축 종목 필터링
- 반환: 제거된 종목 리스트

---

## 작업 4: param_search_space.yaml 추가

### 추가된 섹션 (파일 말미)
```yaml
growth_score:
  axis1_revenue_qoq_min: 0.20
  axis1_revenue_yoy_min: 0.50
  axis1_news_30d_min: 5
  axis2_op_growth_yoy_min: 0.15
  axis2_roe_min: 0.10
  axis2_peg_max: 1.0
  axis2_consecutive_op_quarters: 3
  weight_revenue: 0.25
  weight_op: 0.25
  weight_roe_trend: 0.20
  weight_surprise: 0.15
  weight_peg: 0.15
```

가중치 합계 = 1.0 검증 완료

---

## 작업 5: Node Detector 연동

### node_detector_desk5.py 수정
- `_growth_engine` 모듈 레벨 인스턴스 (ImportError 안전처리)
- `classify_phase(bars, stock_code=None)` 시그니처 변경
- `axis == "AXIS1_EXPECTATION"` → confidence +20
- `axis == "NONE"` → confidence -30

### node_detector_desk3.py 수정
- `_growth_engine` 모듈 레벨 인스턴스 (ImportError 안전처리)
- `classify_phase(bars, layer_score=0.0, stock_code=None)` 시그니처 변경
- `axis == "AXIS2_REALIZATION"` → confidence +15
- `axis == "NONE"` → confidence -20

---

## 작업 6: 단위테스트 10건

### 파일 경로
`tests/test_growth_score.py`

### 실행 결과
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
collected 10 items

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

**10/10 ALL PASS** ✓

---

## 완료 기준 체크

| 항목 | 결과 |
|------|------|
| v4_fundamental_quarterly 테이블 생성 | ✓ (061 마이그레이션, table_exists=1) |
| fundamental_collector.py 4메서드 구현 | ✓ |
| growth_score_engine.py 3메서드 구현 | ✓ |
| node_detector_desk5.py 성장 필터 적용 | ✓ (AXIS1+20/NONE-30) |
| node_detector_desk3.py 성장 필터 적용 | ✓ (AXIS2+15/NONE-20) |
| 10건 단위테스트 ALL PASS | ✓ |
| param_search_space.yaml growth_score 섹션 | ✓ |
| HANDOVER.md v9.7 갱신 | ✓ |

---

## 핵심 발견

1. **CEO 2축 분류 구현 완료**: 기대가치(축1=테마/초기성장) vs 실현가치(축2=이익성장/ROE)
2. **Node Detector 연동**: GrowthScoreEngine이 confidence 점수를 ±보정하여 성장 근거 없는 종목 자동 페널티
3. **DESK5 M3(대파동) 미달 원인**: 재무 데이터 연동으로 테마 폭발형·실적 전환형 구분 가능해짐
4. **migration 번호 061**: 기존 060_v4_positions_capital_idle_days.sql 존재로 061 사용

---

HANDOVER.md 업데이트 완료 (v9.7, project-docs 직접 쓰기 완료)
