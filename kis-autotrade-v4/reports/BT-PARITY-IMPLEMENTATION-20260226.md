# 백테스트-실매매 패리티 보완 구현 보고서

- **일자**: 2026-02-26
- **커밋**: `91a08d61` (phase-2c-command-center)
- **기반 분석**: BT-LIVE-PARITY-GAP-ANALYSIS-20260226.md

---

## 1. 구현 완료 항목

### Phase 1 — P0 치명 (코드 변경)

| # | 작업 | 파일 | 상태 |
|---|------|------|------|
| 1 | **ATR(14) + ADX(14) 계산** | indicator_cache.py, desk2_backtester.py | **완료** |
| 2 | **외인/기관 순매수 로드** | desk2_backtester.py (`_load_investor_data`) | **완료** |
| 3 | **시가총액 실데이터 로드** | desk2_backtester.py (`_load_market_cap`) | **완료** |

#### 상세 변경

**indicator_cache.py** (+10행):
- `adx: float = 0.0` 필드 추가
- `foreign_net_buy: float = 0.0`, `inst_net_buy: float = 0.0` 필드 추가
- `_high_history`, `_low_history`, `_dx_history` 내부 상태 추가
- `reset_daily()`에 새 필드 초기화 추가

**desk2_backtester.py** (+478행, -100행):

1. `_update_atr_adx(ind, bar)` — True Range → ATR(14), +DM/-DM → DX → ADX(14) 증분 계산
2. `_load_investor_data(trade_date, tickers)` — v4_investor_daily에서 외인/기관 순매수금액 로드 (당일 없으면 직전 5영업일)
3. `_load_market_cap(tickers)` — stock_fundamentals에서 실제 시가총액 로드
4. `_load_news_flags(trade_date, tickers)` — go100_news_items에서 종목별 뉴스/악재공시 판별
5. `_load_sector_map(tickers)` — v4_stock_sector에서 섹터코드 매핑
6. `_load_sector_returns(trade_date)` — v4_sector_daily에서 섹터 수익률 로드
7. `run()` 일별 루프: 모든 데이터를 로드하여 indicator_cache에 반영
8. `_build_bar_data_map()`: 새 필드(adx, atr_14, foreign_net_buy, inst_net_buy, market_cap 등) bar_data에 포함

### Phase 2 — P1 높음 (코드 변경)

| # | 작업 | 구현 방식 | 상태 |
|---|------|----------|------|
| 4 | **뉴스 → has_news** | go100_news_items.stock_code1 매칭 | **완료** |
| 5 | **공시 악재 → has_bad_news** | 18개 악재 키워드 regex 매칭 | **완료** |
| 6 | **market_is_down** | regime → BEAR/CRISIS = down, BULL/RISK_ON = bullish | **완료** |

악재 키워드: 상장폐지, 관리종목, 감사의견거절/한정, 횡령, 배임, 부도, 회생절차, 자본잠식, 영업정지, 거래정지, 불성실공시, 투자주의, 조회공시, 소송, 벌금, 과징금, 유상감자

### Phase 3 — P2 보통 (코드 변경 + 자동화)

| # | 작업 | 상태 |
|---|------|------|
| 7 | **sector_code 매핑** | **완료** — v4_stock_sector JOIN |
| 8 | **섹터 수익률 연동** | **완료** — v4_sector_daily 로드 |
| 9 | **수집 자동화** | **완료** — 뉴스 cron 17:10, 외인/기관 기존 유지 |

### Phase 4 — P3 데이터 축적

| # | 작업 | 상태 |
|---|------|------|
| 10 | **뉴스 1년 과거 수집** | **진행 중** — `collect_kis_news.py --days 365` 실행 중 |
| 11 | **테마 자동화** | **기존 cron 동작** — Kiwoom 토큰 갱신 필요 |
| 12 | **프로그램매매 자동화** | **기존 cron 동작** |

---

## 2. DESK 점수 개선 예상

| 항목 | 이전 (하드코딩) | 이후 (실데이터) | 점수 회복 |
|------|----------------|----------------|----------|
| ADX | 항상 0 → 3점 | 실제 계산 0~100 | **+7~10점** |
| 외인/기관 | 항상 0 → 5점 | 순매수금액 반영 | **+10점** |
| 뉴스 has_news | 항상 False | DB 매칭 | **+15점** (뉴스 있는 종목) |
| 악재 has_bad_news | 항상 False | 공시 키워드 | **과대탐지 제거** |
| 시가총액 | 5000억 고정 | 실제 시총 | **왜곡 제거** |
| market_is_down | 항상 False | regime 기반 | **하락장 필터 활성** |
| 섹터 | 항상 "" | 실제 코드 | **C6 활성화** |
| **합계** | | | **+25~35점 정상화** |

---

## 3. 데이터 수집 현황

| 데이터 | 수집 전 | 수집 후 | 비고 |
|--------|--------|--------|------|
| 뉴스/공시 | 7일, 43,552건 | **1년 수집 중** (진행) | ~2M건 예상 |
| 외인/기관 | 171,261건 (불균일) | 동일 (cron 유지) | 2010~2026 |
| 시가총액 | 8,093건 | 동일 | stock_fundamentals |
| 섹터 매핑 | 4,225건 | 동일 | v4_stock_sector |
| 섹터 일별 | 1,806일분 | 동일 | v4_sector_daily |

---

## 4. crontab 수집 일정 (평일)

| 시각 | 대상 | 스크립트 |
|------|------|---------|
| 16:00 | 분봉 배치 | minute_batch_cron.sh |
| 16:30 | 프로그램매매 | collect_program_trades.sh |
| 16:35 | 체결강도(일말) | collect_strength_daily.sh |
| 16:45 | 신용잔고 | collect_credit_balance.sh |
| 16:50 | 투자자(종목별) | collect_investor_daily.sh |
| 17:00 | 테마 | collect_theme.sh |
| **17:10** | **뉴스/공시** | **collect_news_daily.sh (신규)** |
| 18:00 | OHLCV 일봉 | collect_ohlcv_daily.py |
| 18:30 | VKOSPI | collect_vkospi_alt.py |
| 18:30 | 섹터 지수 | collect_index_daily.sh |
| 18:40 | 투자자(시장) | collect_market_investor.py |
| 19:00 | 종목 마스터 | collect_stock_universe.py |

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
