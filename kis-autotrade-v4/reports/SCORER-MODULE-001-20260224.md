# SCORER-MODULE-001 — ChiefAnalyst 5대 스코어러 모듈화 + 백테스트 연동 설계

**작업ID:** SCORER-MODULE-001  
**작업명:** ChiefAnalyst 5대 스코어러 모듈화 + 백테스트 연동 설계  
**일시:** 2026-02-24 KST  
**우선순위:** P4  
**성격:** 코드 분석 + 모듈 설계·구현, 기존 commander/provider 로직 변경 없음  

---

## 1. 배경 (IMPL-GAP-AUDIT-001 §LAYER 2-A)

- **LAYER 2-A:** Chief Analyst (today_universe, 버전화, **5대 스코어러**) — 부분구현.
- 기획서 기준 5개 독립 스코어러 파일(`scoring/supply_demand.py`, `sector.py`, `theme.py`, `volume.py`, `technical.py`, `composite_scorer.py`)이 없고, 수급/업종/테마/거래량/기술적 점수가 **desk1/2/3_commander** 및 **data provider**(`get_supply_demand` 등)에 분산되어 있음.
- v4_scoring_weights(supply_demand_w, sector_momentum_w, theme_w, volume_w, technical_w) 컬럼은 존재.

본 작업으로 5대 스코어러를 **신규 모듈**로 구현하고, 백테스트에서 CompositeScorer 기반 후보 선정 **옵션**을 설계·연동했다.

---

## 2. 현재 스코어링 분산 현황 분석

| 위치 | 내용 |
|------|------|
| **chief_analyst.py** | today_universe 생성, candidate_stocks를 DESK별 min_entry_score·allowed_classes로 필터. 스코어 산출 자체는 하지 않음. |
| **desk2_commander.py** | CLASS-A: `_check_supply`, `_check_technical_a`, 거래량 순위·등락률로 score 조합(0.3·0.3·0.2·0.2). v4_investor_daily, ohlcv_daily 직접 조회. |
| **data_provider** | `get_supply_demand(ticker, days)` — v4_investor_daily 기반. backtest_provider는 sim_date 기준. |
| **signal_generator.py** | 후보 선정: D-1 거래대금 상위 500종목(`_get_candidate_stock_codes`). 수급은 StockFlowFilter로 가중만. |
| **v4_scoring_weights** | supply_demand_w, sector_momentum_w, theme_w, volume_w, technical_w. 주간 전략 스코어링(weekly_scoring)은 현재 유니버스용 컬럼과 매핑 없이 기본값 사용. |

**결론:** 스코어링 로직이 commander·provider·signal_generator에 분산되어 있어, ChiefAnalyst·DESK·백테스트에서 **일원화된 스코어 모듈**이 필요함.

---

## 3. 5대 스코어러 설계

### 3.1 공통 인터페이스 (BaseScorer)

- **경로:** `backend/app/services/scoring/base_scorer.py`
- **역할:** `db_session`(AsyncSession), `sim_date`(백테스트용, YYYYMMDD 또는 YYYY-MM-DD).
- **메서드:**
  - `score(ticker, date) -> float` (0.0~1.0)
  - `score_batch(tickers, date) -> Dict[str, float]`

### 3.2 SupplyDemandScorer (수급)

- **데이터:** v4_investor_daily (foreign_net_qty, institution_net_qty, consecutive_foreign_buy_days, consecutive_institution_buy_days).
- **로직:** N일(기본 20일) 합산·연속매수일 반영. 순매수 > 0 → 0.5 + 연속매수 가점(최대 0.5); 순매수 ≤ 0 → 0.0~0.3.
- **입출력:** ticker, date → 0.0~1.0.

### 3.3 SectorScorer (업종 강도)

- **데이터:** v4_sector_daily, v4_stock_sector.
- **로직:** 종목의 sector_code 해당일 change_rate 순위. 상위 30% → 0.7~1.0, 그 외 보다 낮은 점수.
- **입출력:** ticker, date → 0.0~1.0.

### 3.4 ThemeScorer (테마 활성도)

- **데이터:** v4_theme_stock (및 추후 v4_theme_daily 등).
- **로직:** 테마 소속 여부만 사용. 소속 시 0.7, **데이터 없으면 0.5 반환** (graceful degradation). 테마 0행 이슈 대응.
- **입출력:** ticker, date → 0.0~1.0.

### 3.5 VolumeScorer (거래량 이상 탐지)

- **데이터:** ohlcv_daily (close, volume).
- **로직:** 당일 거래대금 / 20일 평균 거래대금. 1.5배 이상 → 0.7~1.0.
- **입출력:** ticker, date → 0.0~1.0.

### 3.6 TechnicalScorer (기술적 지표 복합)

- **데이터:** ohlcv_daily (open, high, low, close, volume).
- **로직:**  
  - MA5 > MA20 > MA60 정배열 → +0.3  
  - RSI 30~70 → +0.2  
  - MACD 히스토그램 양전환 → +0.3  
  - Bollinger Band 하단 근처 반등 → +0.2  
  (기본 0.2 부여 후 상한 1.0)
- **입출력:** ticker, date → 0.0~1.0.

### 3.7 CompositeScorer (가중 합산)

- **데이터:** v4_scoring_weights (effective_from, supply_demand_w, sector_momentum_w, theme_w, volume_w, technical_w).
- **로직:** `total = Σ(weight_i × score_i) / Σ(weight_i)`. 가중치 미존재 시 DEFAULT_WEIGHTS(0.35, 0.20, 0.15, 0.15, 0.15).
- **DESK별 가중치:** 설계상 `desk_id` 인자 확장 가능(현재 미사용).

---

## 4. 구현 파일 목록 (7개)

| 파일 | 설명 |
|------|------|
| `backend/app/services/scoring/__init__.py` | 패키지 노출 (BaseScorer, 5개 스코어러, CompositeScorer). |
| `backend/app/services/scoring/base_scorer.py` | BaseScorer 추상 클래스, _norm_date. |
| `backend/app/services/scoring/supply_demand_scorer.py` | SupplyDemandScorer. |
| `backend/app/services/scoring/sector_scorer.py` | SectorScorer. |
| `backend/app/services/scoring/theme_scorer.py` | ThemeScorer (graceful degradation 0.5). |
| `backend/app/services/scoring/volume_scorer.py` | VolumeScorer. |
| `backend/app/services/scoring/technical_scorer.py` | TechnicalScorer. |
| `backend/app/services/scoring/composite_scorer.py` | CompositeScorer (가중치 DB 로드, 5개 스코어 병합). |

**규칙 준수:** 기존 commander/provider 코드는 수정하지 않았고, 스코어러는 **신규 모듈로만** 추가함.

---

## 5. 백테스트 연동 인터페이스

### 5.1 signal_generator 옵션

- **기본 동작 (scorer_mode="none"):** `_get_candidate_stock_codes(date, 500)` — D-1 거래대금 상위 500종목.
- **스코어링 모드 (옵션):** 후보를 CompositeScorer로 선정하려면, 호출 측에서 **스코어 상위 500 종목 리스트**를 넘기면 됨.

### 5.2 추가된 파라미터

- `generate_signals(..., get_candidate_tickers: Optional[Callable[[str], List[str]]] = None)`  
- `_generate_signals_card_entries(..., get_candidate_tickers: Optional[Callable[[str], List[str]]] = None)`  

**동작:**  
- `get_candidate_tickers`가 제공되면: `candidate_stocks = get_candidate_tickers(date)` 사용.  
- 미제공 시: 기존처럼 `_get_candidate_stock_codes(date)` 사용.

### 5.3 백테스트 엔진 연동 (설계)

- **scoring 모드** 사용 시 백테스트 엔진에서:
  1. 해당 일자 기준 ohlcv_daily에 존재하는 종목 목록 확보.
  2. (AsyncSession 등으로) CompositeScorer 생성, `sim_date=date` 설정.
  3. `score_batch(전체_종목, date)` 호출 후 스코어 내림차순 정렬, 상위 500개를 해당 일자 후보로 사용.
  4. `get_candidate_tickers = lambda d: precomputed_top500_by_date.get(d, [])` 형태로 전달하거나, 일자별로 동일 로직 호출하여 `BacktestSignalGenerator.generate_signals(..., get_candidate_tickers=...)`에 넘김.
- entry_rules 필터는 기존과 동일 적용.

(실제 backtest_engine_v2.py에 scorer_mode·async 세션 주입은 추후 작업으로 두었음.)

---

## 6. 데이터 의존성

| 스코어러 | 테이블/소스 | 비고 |
|----------|-------------|------|
| SupplyDemandScorer | v4_investor_daily | 170,760행 수급 데이터 사용 가능. |
| SectorScorer | v4_sector_daily, v4_stock_sector | v4_sector_daily 14,754행, v4_stock_sector 4,225행. |
| ThemeScorer | v4_theme_stock | 테마 0행 시 0.5 반환 (graceful degradation). |
| VolumeScorer | ohlcv_daily | 일봉 거래대금. |
| TechnicalScorer | ohlcv_daily | MA/RSI/MACD/BB. |
| CompositeScorer | v4_scoring_weights | 1행 이상 권장, 없으면 DEFAULT_WEIGHTS. |

---

## 7. 검수 결과

- **문법:** `backend/app/services/scoring/*.py` 8개 파일 `ast.parse` 통과.
- **import:** `PYTHONPATH=backend` 기준 `from app.services.scoring.base_scorer import BaseScorer`, `from app.services.scoring.composite_scorer import CompositeScorer` 정상.
- **기존 코드:** commander·provider·chief_analyst 수정 없음. signal_generator는 옵션 인자만 추가.

---

## 8. 잔여 (추후 작업)

- **ChiefAnalyst 연동:** build_today_universe 전에 CompositeScorer 또는 개별 스코어러로 후보 스코어 산출 후 candidate_stocks에 반영.
- **DESK별 가중치:** v4_scoring_weights에 regime/desk_id 차등 확장 시 CompositeScorer에서 해당 컬럼 사용.
- **백테스트 엔진:** scorer_mode="scoring" 시 AsyncSession 생성 및 CompositeScorer.score_batch → 상위 500 도출 후 `get_candidate_tickers` 주입.

---

*문서 끝 (SCORER-MODULE-001-20260224)*
