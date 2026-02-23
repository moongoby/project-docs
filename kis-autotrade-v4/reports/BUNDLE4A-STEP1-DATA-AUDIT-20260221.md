# Modified by: CUR-GO100-BUNDLE4A, 2026-02-21
# V4.1 데이터 전수조사 보고서
**작업 ID**: CUR-GO100-BUNDLE4A | **일시**: 2026-02-21 | **DB 크기**: 4,161 MB

---

## 1. 전체 테이블 목록 (156개, 주요 테이블만 기재)

| 테이블명 | 행수 | 크기 | 비고 |
|----------|------|------|------|
| v4_ohlcv_minute_2026_01 | 3,723,824 | 999 MB | 파티션 (최대) |
| v4_ohlcv_minute_2025_03 | 2,706,452 | 687 MB | 파티션 |
| ohlcv_daily | 2,596,474 | 671 MB | 일봉 |
| v4_ohlcv_minute_2026_02 | 2,068,478 | 539 MB | 파티션 |
| v4_ohlcv_minute_2025_12 | 1,930,426 | 519 MB | 파티션 |
| v4_ohlcv_minute_2025_02 | 986,662 | 253 MB | 파티션 |
| v4_investor_daily | 166,921 | 138 MB | 종목별 투자자 |
| ohlcv_weekly | 357,381 | 50 MB | 주봉 |
| v4_backtest_trades | 136,821 | 19 MB | 백테스트 |
| financial_ratios | 45,870 | 6.7 MB | 재무비율 |
| v4_sector_daily | 14,696 | 8.6 MB | 업종 |
| stock_universe | 3,844 | 1.6 MB | 유니버스 |
| stock_fundamentals | 4,249 | 744 kB | 재무 |
| v4_market_investor_daily | 3,610 | 1.8 MB | 시장 투자자 |
| v4_vkospi_daily | 1,504 | 392 kB | VKOSPI |
| index_daily | 1,467 | 400 kB | 인덱스 |
| v4_market_regime_daily | 2 | 80 kB | 마켓 레짐 |
| v4_market_ranking | 180 | 208 kB | 거래량/등락률 상위 |
| v4_stock_sector | 4,225 | 472 kB | 종목-업종 매핑 |
| v4_signals | 101,274 | 34 MB | 매매 시그널 |

빈 테이블 (0건): v4_theme_* (테마 데이터 전체 미수집), v4_tick_data, v4_broker_trades, v4_program_trades, v4_sector_price 등 약 50개

---

## 2. 핵심 데이터 소스

| 테이블명 | 용도 | 행수 | 기간 | 종목수 | 주요 컬럼 |
|----------|------|------|------|--------|----------|
| ohlcv_daily | 일봉 OHLCV | 2,596,548 | 2023-01-02 ~ 2026-02-20 | 3,844 | stock_code, date(varchar8), open/high/low/close(real), volume(bigint) |
| v4_ohlcv_minute | 분봉 OHLCV | ~11,453,631 | 2025-02-18 ~ 2026-02-19 | 546 | stock_code, trade_date(date), trade_time(time), OHLC(int), volume(bigint) |
| v4_investor_daily | 종목별 투자자 | 166,921 | 2010-01-28 ~ 2026-02-20 | 3,943 | foreign/institution net_qty/amount, consecutive days |
| v4_market_investor_daily | 시장 투자자 | 3,610 | 2018-10-15 ~ 2026-02-20 | 2(KSP/KSQ) | market, index_close, foreign/institution/individual net |
| v4_sector_daily | 업종 지수 | 14,696 | 2018-10-19 ~ 2026-02-20 | 32업종 | sector_code/name, OHLC index, change_rate, 5d/20d change |
| v4_vkospi_daily | 변동성지수 | 1,504 | 2020-01-02 ~ 2026-02-13 | — | date(varchar8), OHLC(real), change_rate |
| index_daily | 시장인덱스 | 1,467 | 2024-02-13 ~ 2026-02-13 | 3(KOSPI/KOSDAQ/KOSPI200) | index_code, OHLCV |
| stock_universe | 종목 마스터 | 3,844 | — | 3,844 | stock_code/name, market, sector/mid/small, per/pbr/eps |
| stock_fundamentals | 재무 스냅샷 | 4,249 | 2026-02-11~12 | 4,225 | per/pbr/eps/bps, market_cap, shares_outstanding |
| financial_ratios | 분기 재무비율 | 45,870 | 2004Q2 ~ 2025Q4 | 2,612 | grs(매출성장), bsop_prfi_inrt(영업이익률), ntin_inrt(순이익률), roe_val, eps, bps, lblt_rate(부채비율) |
| v4_market_regime_daily | 마켓 레짐 | 2 | 2026-02-12~13 | — | regime, regime_score, MA alignment, bull_ratio, vkospi |
| v4_market_ranking | 일별 시장랭킹 | 180 | 2026-02-14~21 | — | VOLUME_TOP / CHANGE_RATE_UP, 각 30종목, 3일분 |

---

## 3. stock_universe 컬럼별 활용 가능성

| 컬럼명 | 전체 | 데이터 존재 | NULL 비율 | GO100 활용 가능 여부 |
|--------|------|------------|-----------|---------------------|
| stock_code | 3,844 | 3,844 | 0% | **필수** — PK |
| stock_name | 3,844 | 3,844 | 0% | **필수** — 표시용 |
| market | 3,844 | 3,844 (KOSPI 2023, KOSDAQ 1821) | 0% | **가능** — 시장 필터 |
| sector (KSIC) | 3,844 | 2,754 (실제 업종) | 28.3% (1,090건 KOSPI/KOSDAQ 미수집) | **가능** — 업종 필터 (미수집 1,090건 주의) |
| sector_large | 3,844 | 1,514 | 60.6% | **제한적** — 시가총액 규모 구분, 업종 아님 |
| sector_mid | 3,844 | 1,340 | 65.1% | **가능** — KRX 중분류 업종 (미수집 2,504건) |
| sector_small | 3,844 | 1,331 | 65.4% | **가능** — KRX 소분류 업종 |
| market_cap | 3,844 | 0 | **100%** | **불가** — 전부 NULL |
| market_cap_value | 3,844 | 0 | **100%** | **불가** — 전부 NULL |
| rank_market_cap | 3,844 | 0 | **100%** | **불가** — 전부 NULL |
| rank_trade_amount | 3,844 | 0 | **100%** | **불가** — 전부 NULL |
| trade_volume | 3,844 | 0 | **100%** | **불가** — 전부 NULL |
| trade_amount | 3,844 | 0 | **100%** | **불가** — 전부 NULL |
| per | 3,844 | 2,546 (0 제외) | 33.8% | **가능** — 밸류에이션 (avg 26.37) |
| pbr | 3,844 | 2,548 (0 제외) | 33.7% | **가능** — 밸류에이션 (avg 2.42) |
| eps | 3,844 | 2,546 (0 제외) | 33.8% | **가능** — 이익지표 |
| dividend_yield | 3,844 | 0 | **100%** | **불가** — 전부 NULL |
| is_active | 3,844 | 3,844 (전부 true) | 0% | **참고** — 현재 활성종목 표시 |

---

## 4. 투자자 데이터 (v4_investor_daily)

- **행수**: 166,921건
- **기간**: 2010-01-28 ~ 2026-02-20
- **종목수**: 3,943개
- **주요 컬럼**:
  - `foreign_buy_qty / sell_qty / net_qty / net_amount` — 외국인 매수/매도/순매수 수량/금액
  - `institution_buy_qty / sell_qty / net_qty / net_amount` — 기관 매수/매도/순매수 수량/금액
  - `individual_net_qty / net_amount` — 개인 순매수
  - `foreign_hold_qty / hold_ratio` — 외국인 보유수량/비율
  - `program_buy_amount / sell_amount / net_amount` — 프로그램 매매
  - **`consecutive_foreign_buy_days`** — 외국인 연속 순매수 일수
  - **`consecutive_institution_buy_days`** — 기관 연속 순매수 일수
- **GO100 활용**: 외국인/기관 수급 필터, 연속매수일 기반 종목선정 가능

---

## 5. 마켓 레짐 데이터 (v4_market_regime_daily)

- **행수**: **2건** (2026-02-12, 02-13만)
- **레짐 분류**: `MILD_TREND_UP` (75점)
- **주요 컬럼**: regime, regime_score, kospi_ret_20d, ma5/20/60, ma_alignment(BULL_ALIGNED), bull_ratio_20d, vkospi, foreign_flow_20d, hysteresis
- **GO100 활용**: 거의 불가 — 데이터가 2건뿐. 사실상 미운영 상태. 레짐 기반 필터를 쓰려면 별도 계산 또는 수집 보강 필요.

---

## 6. 분봉 데이터 (v4_ohlcv_minute)

- **총 행수**: ~11,453,631건 (volume>0 기준)
- **기간**: 2025-02-18 ~ 2026-02-19 (약 1년)
- **종목수**: 546개
- **시간 분포**:
  | 시간대 | 건수 |
  |--------|------|
  | 09시 | 1,806,782 |
  | 10시 | 1,809,421 |
  | 11시 | 1,783,781 |
  | 12시 | 1,776,255 |
  | 13시 | 1,797,485 |
  | 14시 | 1,830,868 |
  | 15시 | 653,183 |
  | 16시 | 1 |
- **파티션**: 15개 월별 (2025-01 ~ 2026-03), 실데이터 4개월(2025-02/03/11/12, 2026-01/02)
- **GO100 활용**: 분봉 백테스트, 장중 entry/exit 타이밍 (546종목 한정)

---

## 7. 인덱스 구성종목 정보: **없음**

- `stock_universe`에 KOSPI200/KOSDAQ150 구성종목 여부 컬럼 없음
- `index_daily`에는 지수 OHLCV만 존재 (KOSPI, KOSDAQ, KOSPI200 3종)
- GO100에서 인덱스 구성종목 기반 필터가 필요하면 별도 수집 필요

---

## 8. 관리종목/거래정지 정보: **없음**

- `stock_universe`에 관리종목/거래정지/투자경고 관련 컬럼 없음
- 위험종목 필터링이 필요하면 별도 수집 또는 ohlcv_daily volume=0 기반 우회 필요

---

## 9. 재무 데이터

| 소스 | 내용 | 비고 |
|------|------|------|
| stock_universe.per/pbr/eps | 2,546건 유효 (66.2%) | 최신 스냅샷, 수집일 기준 |
| stock_fundamentals | 4,249건, 2026-02-11~12 | market_cap(3,862건), shares_outstanding(3,864건) 보유 |
| financial_ratios | 45,870건, 2004~2025Q4, 2,612종목 | ROE(37,008건), 매출성장(40,093건), 부채비율(42,945건) |

- **stock_fundamentals가 유일한 market_cap 소스** (stock_universe.market_cap은 전부 NULL)
- **financial_ratios가 과거 재무비율의 유일한 소스** (ROE, 매출성장률, 영업이익률, 부채비율)
- dividend_yield: 전체 NULL (미수집)

---

## 10. 스케줄러 수집 주기

| 시간 | 수단 | 대상 |
|------|------|------|
| 매일 07:49 | kis-v41-scheduler (추정) | v4_market_ranking (VOLUME_TOP, CHANGE_RATE_UP 각 30) |
| 매일 09:10 (평일) | kis-v41-scheduler | v4_signals (매매 시그널) |
| 15:40 (평일) | kis-v41-scheduler | v4_investor_daily (종목별 투자자) |
| 16:00 (평일) | minute-collector (systemd) | v4_ohlcv_minute |
| 18:00 (평일) | collect_ohlcv_daily.py (cron) | ohlcv_daily |
| 18:30 (평일) | collect_index_daily.sh (cron) | index_daily |
| 18:40 (평일) | collect_market_investor.py (cron) | v4_market_investor_daily |
| 19:00 (평일) | collect_stock_universe.py (cron) | stock_universe |
| 토 02:00 | minute_batch_cron | v4_ohlcv_minute (주말 보충) |
| 토 03:00 | collect_stock_industry.py | stock_universe 업종 |
| 20:00 | kis-autotrade-top100-211.timer | top100 리포트 |
| go100 timers | live/paper/reconcile/report | go100_* 테이블 |

---

## 컴플라이언스 체크리스트
| 항목 | 결과 |
|------|------|
| .env/.bak 커밋여부 | N/A (읽기 전용) |
| strategy_cards | **59건** 유지 |
| v4_positions OPEN수 | **5건** 유지 |
| 파일헤더 | N/A (DB 조사만) |
| DB 스키마 변경 | **없음** |
| 서비스 재시작 | **없음** |
| V4.1 파일 수정여부 | **없음** |
