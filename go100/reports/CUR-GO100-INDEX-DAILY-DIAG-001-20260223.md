# CUR-INDEX-DAILY-DIAG-001 — index_daily OHLC=0 진단 보고서

## 기본 정보
- 작업일: 2026-02-23
- 서버: root@[SERVER-IP]
- 작업 유형: 읽기 전용 진단 (코드/DB 변경 없음)

## 1. index_daily 테이블 현황
- **전체 행 수:** 1,467
- **OHLC=0 행 수:** 150
- **테이블 구조:**
  - 컬럼: id, index_code, index_name, date(varchar 8), open, high, low, close, volume, trade_amount, created_at
  - PK: id, UNIQUE: (index_code, date), 인덱스: idx_index_daily_code_date

OHLC=0 샘플(최근): 0001(KOSPI), 1001(KOSDAQ), 2001(KOSPI200)의 20260210~20260213 일자에서 open/high/low/close=0, volume·trade_amount는 정상 값.
정상 샘플: 20251201~20251202 일자에 open/high/low/close 모두 유효 값.

## 2. 용도 (어디에 쓰이는지)
| 파일 | 용도 |
|------|------|
| backend/app/services/go100/universe/advanced_filters.py | index_daily(KOSPI) + v4_vkospi_daily 등으로 시장 레짐/필터 (date, close 조회) |
| backend/app/services/go100/ai/prompts.py | get_market_regime 설명: index_daily + vkospi + market_investor |
| backend/app/services/data/live_provider.py | 지수 일봉 조회 (index_name, date, close, open, high, low, volume) |
| backend/app/services/data/backtest_provider.py | sim_date 기준 index_daily 조회 |
| backend/app/routers/v4_chart.py | get_index_daily: 지수 일봉 차트 API |
| backend/app/services/strategy/desk1_commander.py | KOSPI 20일 수익률 등 (close 조회) |
| backend/app/services/market/regime_detector.py | KOSPI/KOSDAQ 20일 수익률, MA, 양봉 비율, 거래대금 (index_daily 전면 사용) |
| scripts/collection/historical_backfill.py | **유일한 INSERT 주체**: fetch_index_daily + save_index_daily |
| scripts/backfill_regime_history.py | index_daily 날짜/데이터 기반 레짐 이력 백필 |
| scripts/test_v41_chart.py | test_index_daily |

## 3. 수집 주체
- **V4.1에서 수집:** 아니오. V4.1 스케줄러(daily_scheduler)는 `v4_sector_daily`(업종)만 수집하며, **index_daily**를 INSERT하는 스케줄/크론 없음.
- **GO100에서 수집:** 아니오. GO100은 index_daily **참조만** 함 (advanced_filters, prompts).
- **실제 수집:** `scripts/collection/historical_backfill.py` — 수동/배치 실행 시 `--index-only` 또는 기본 `include_index=True`로 지수 일봉 수집. KIS API FHKUP03500100 호출 후 `save_index_daily`로 INSERT.

## 4. OHLC=0 원인
- **근본 원인:** KIS API **FHKUP03500100**(국내주식업종기간별시세)의 **output2**는 업종 지수용 필드명을 사용함.
  - 문서상 output2 필드: `bstp_nmix_oprc`, `bstp_nmix_hgpr`, `bstp_nmix_lwpr`, `bstp_nmix_prpr`(현재가=close), `stck_bsop_date`, `acml_vol`, `acml_tr_pbmn`
  - `historical_backfill.py`의 `_fetch_index_daily_sync`는 **주식용** 필드명 `stck_oprc`, `stck_hgpr`, `stck_lwpr`, `stck_clpr`만 참조하고, 없으면 `float(row.get("stck_oprc") or 0)` 등으로 **0**을 넣음.
  - 따라서 API가 정상 응답해도 OHLC는 항상 0으로 파싱되고, volume/trade_amount는 `acml_vol`/`acml_tr_pbmn`로 정상 수집됨.
- **영향 구간:** 위와 같이 파싱된 0이 그대로 INSERT된 모든 구간(약 150건, 주로 20260210~20260213 및 20260211 등).

## 5. 재수집 필요 여부 및 방법
- **재수집 필요:** 예. OHLC=0인 150건은 차트/레짐/백테스트에 사용 시 잘못된 결과를 낳음.
- **방법:**
  1. **코드 수정(필수):** `scripts/collection/historical_backfill.py`의 `_fetch_index_daily_sync`에서 output2 파싱 시 **업종 지수 필드** 사용.
     - open: `row.get("bstp_nmix_oprc") or row.get("stck_oprc")`
     - high: `row.get("bstp_nmix_hgpr") or row.get("stck_hgpr")`
     - low:  `row.get("bstp_nmix_lwpr") or row.get("stck_lwpr")`
     - close: `row.get("bstp_nmix_prpr") or row.get("stck_clpr")`
     (하위 호환을 위해 stck_* 폴백 유지 권장)
  2. **재수집 실행:** 코드 반영 후 동일 구간(예: 20260201~20260223)에 대해 `python -m scripts.collection.historical_backfill --index-only --start 20260201 --end 20260223` 실행. ON CONFLICT DO UPDATE로 기존 행의 OHLC가 정상 값으로 갱신됨.
  3. **검증:** `SELECT * FROM index_daily WHERE date >= '20260201' AND (open = 0 OR close = 0);` → 0건 확인.

진단 완료.
