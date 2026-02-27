# DB-TABLE-CATALOG v1.0

**Database**: `kisautotrade` (PostgreSQL)
**Last Updated**: 2026-02-28
**Total Tables**: 225
**Total Size**: ~15.7 GB

---

## 1. 핵심 시장 데이터 (Market Data)

| Table | Rows | Size | Date Range | Owner | Description |
|-------|------|------|------------|-------|-------------|
| `ohlcv_daily` | 2,611,905 | 696 MB | 2023-01-02 ~ 2026-02-26 | V4.1+GO100 | 일봉 OHLCV (stock_code, date[varchar YYYYMMDD], open, high, low, close, volume, trade_amount) |
| `v4_ohlcv_minute` | 0 (parent) | 0 | - | V4.1 | 분봉 파티션 부모 테이블 |
| `v4_ohlcv_minute_2026_02` | 3,132,899 | 807 MB | 2026-02-02 ~ 02-27 | V4.1 | 분봉 (stock_code, trade_date, trade_time, open/high/low/close_price, volume, trade_amount) |
| `v4_ohlcv_minute_2026_01` | 4,344,320 | 1,153 MB | 2026-01-02 ~ 01-30 | V4.1 | 분봉 |
| `v4_ohlcv_minute_2025_12` | 4,157,726 | 1,086 MB | 2025-12 | V4.1 | 분봉 |
| `v4_ohlcv_minute_2025_02~11` | ~35M total | ~9.0 GB | 2025-02 ~ 11 | V4.1 | 분봉 (월별 파티션) |
| `ohlcv_1m_history` | 5,346,069 | 1,122 MB | legacy | V4.1 | 분봉 히스토리 (구버전) |
| `ohlcv_weekly` | 357,381 | 50 MB | - | V4.1 | 주봉 |
| `ohlcv_monthly` | 89,307 | 13 MB | - | V4.1 | 월봉 |
| `market_data_min` | 5,346,472 | 985 MB | legacy | V4.1 | 분봉 (구버전) |
| `index_daily` | 1,488 | 432 kB | - | V4.1 | 주요 지수 일봉 |

## 2. 투자자 수급 데이터 (Investor Flow)

| Table | Rows | Size | Date Range | Owner | Description |
|-------|------|------|------------|-------|-------------|
| `v4_investor_daily` | 261,410 | 187 MB | 2010-01-28 ~ 2026-02-26 | V4.1 | **종목별 외국인/기관/개인 일별 매매** (foreign_buy/sell/net_qty, institution_buy/sell/net_qty, individual_net, foreign_hold_qty/ratio, program_buy/sell/net, consecutive_buy_days) |
| `v4_market_investor_daily` | 3,618 | 1,776 kB | 2018-10-15 ~ 2026-02-26 | V4.1 | **시장별(KOSPI/KOSDAQ) 외국인/기관/개인 일별 순매수** |
| `v4_program_trades` | 287 | 120 kB | 2026-02-25 (1일) | V4.1 | 프로그램매매 (최근 수집 시작, 데이터 극소) |

### 수급 데이터 Coverage 상태
- `v4_investor_daily`: **분석 기간(01-12~02-25) 30일 완전 커버**, 일평균 3,840종목
  - 단, 02-24(623종목), 02-25(148종목) — 최근 2일 수집 미완
- `v4_market_investor_daily`: 분석 기간 완전 커버
- `v4_program_trades`: 2026-02-25 단 1일 — **사실상 사용 불가**

## 3. 호가/틱 데이터 (Orderbook & Tick)

| Table | Rows | Size | Date Range | Owner | Description |
|-------|------|------|------------|-------|-------------|
| `v4_orderbook_realtime` | 1,270,746 | 432 MB | **2026-02-27 (오늘만)** | V4.1 | 실시간 호가 10단계 (ask/bid price/qty 1~10, total_ask/bid_qty, spread_pct) — 20종목 |
| `v4_tick_data` | 814,605 | 116 MB | **2026-02-27 (오늘만)** | V4.1 | 체결 틱 (price, volume, buy_sell, strength) — 21종목 |
| `orderbook_snapshots` | 35,894 | 42 MB | legacy | V4.1 | 호가 스냅샷 (구버전) |
| `price_tick_snapshots` | 35,865 | 4.6 MB | legacy | V4.1 | 가격 틱 스냅샷 (구버전) |

### 호가/틱 데이터 Assessment
- **v4_orderbook_realtime, v4_tick_data**: 오늘(02-27) 데이터만 존재 → **과거 분석 불가**
- 분석 기간(01-12~02-25) 호가/틱 데이터 없음 → PART B의 X13, X14 변수 계산 불가

## 4. 뉴스/이벤트 데이터

| Table | Rows | Size | Date Range | Owner | Description |
|-------|------|------|------------|-------|-------------|
| `go100_news_items` | 2,140,477 | 1,898 MB | 2025-02-27 ~ 2026-02-26 | GO100 | 뉴스 (data_date, data_time, title, stock_code1~3, category_code, is_disclosure) |
| `v4_vi_occurrences` | 319 | 96 kB | 2026-02-02 ~ 02-25 | V4.1 | VI 발동 기록 |

### 뉴스 시간대 분포 (2026-01-12 이후)
- 장전 (<09:00): 15,304건 — **장전 뉴스 존재**
- 장중 (09:00~15:30): 153,526건
- 장후 (>15:30): 102,843건

## 5. 시장 레짐/변동성

| Table | Rows | Size | Date Range | Owner | Description |
|-------|------|------|------------|-------|-------------|
| `v4_market_regime_daily` | 822 | 416 kB | 2022-09-07 ~ 2026-02-25 | V4.1 | 시장 레짐 (date, regime, regime_score, market_type[KOSPI/KOSDAQ], ma5/20/60, vkospi, foreign_flow_20d) |
| `v4_vkospi_daily` | 1,511 | 400 kB | 2020-01-02 ~ 2026-02-27 | V4.1 | VKOSPI 일별 (date[varchar], open, high, low, close, change_rate) |
| `data_global_index_daily` | 2,738 | 680 kB | 2025-02-25 ~ 2026-02-27 | GO100 | 글로벌 지수 일별 |

### 레짐 데이터 상태
- `v4_market_regime_daily`: **market_type별(KOSPI/KOSDAQ) 2행/일** — 분석 기간 완전 커버
- Phase 2에서 `v4_market_regime`(밑줄 없는 이름)로 조회해서 "없음" 보고 → 실제 이름은 `v4_market_regime_daily`

## 6. 체결강도/매매동향

| Table | Rows | Size | Date Range | Owner | Description |
|-------|------|------|------------|-------|-------------|
| `v4_trade_strength_history` | 231,307 | 30 MB | 2025-11-26 ~ 2026-02-27 | V4.1 | 종목별 체결강도 히스토리 (stock_code, recorded_at, strength, buy/sell_count, buy/sell_amount) |
| `market_turnover_daily` | 26,148 | 3.3 MB | 2025-02-05 ~ 2026-02-05 | V4.1 | 시장 거래대금 상위 |

## 7. 섹터/테마

| Table | Rows | Size | Date Range | Owner | Description |
|-------|------|------|------------|-------|-------------|
| `v4_sector_daily` | 15,057 | 9.4 MB | 2018-10-19 ~ 2026-02-27 | V4.1 | 섹터 일별 데이터 |
| `v4_stock_sector` | 4,225 | 472 kB | - | V4.1 | 종목-섹터 매핑 |
| `v4_sector_stock_mapping` | 2,770 | 616 kB | - | V4.1 | 섹터-종목 매핑 (역방향) |
| `v4_theme_master` | 141 | 112 kB | - | V4.1 | 테마 마스터 |
| `v4_theme_stock` | 1,493 | 384 kB | - | V4.1 | 테마-종목 매핑 |
| `v4_theme_detail` | 141 | 160 kB | - | V4.1 | 테마 상세 |
| `go100_sector_price` | 7,047 | 1.2 MB | - | GO100 | 섹터별 가격 |
| `go100_sector_correlation` | 1,624 | 536 kB | - | GO100 | 섹터 상관관계 |

## 8. 종목 마스터/유니버스

| Table | Rows | Size | Active | Owner | Description |
|-------|------|------|--------|-------|-------------|
| `stock_universe` | 3,844 | 1.7 MB | 3,844 | V4.1+GO100 | 종목 유니버스 (stock_code, name, sector, market, is_active) |
| `stock_fundamentals` | 33,831 | 5.2 MB | - | V4.1 | 종목 재무정보 |
| `financial_ratios` | 45,870 | 6.7 MB | - | V4.1 | 재무비율 |
| `go100_fundamentals` | 2,720 | 1.9 MB | - | GO100 | 펀더멘탈 |
| `go100_fundamentals_pit` | 30,463 | 5.9 MB | - | GO100 | PIT 펀더멘탈 |
| `go100_delisted_stocks` | 100 | 72 kB | - | GO100 | 상장폐지 종목 |
| `go100_delisted_ohlcv` | 24,127 | 4.3 MB | - | GO100 | 상장폐지 종목 OHLCV |

## 9. 트레이딩 시스템

| Table | Rows | Size | Owner | Description |
|-------|------|------|-------|-------------|
| `strategy_cards` | 60 | 312 kB | V4.1 | 전략 카드 |
| `v4_positions` | 31 | 208 kB | V4.1 | 포지션 (OPEN 14건) |
| `v4_trades` | 33 | 136 kB | V4.1 | 실매매 기록 |
| `v4_signals` | 101,274 | 34 MB | V4.1 | 시그널 |
| `v4_backtest_trades` | 211,008 | 38 MB | V4.1 | 백테스트 매매 |
| `v4_desk_fund` | 5 | 120 kB | V4.1 | 데스크 자금 |
| `v4_desk_strategy_mapping` | 56 | 104 kB | V4.1 | 데스크-전략 매핑 |
| `v4_bt_discovery_log` | 776,636 | 518 MB | V4.1 | 발굴 로그 |
| `v4_bt_discoveries` | 6,931 | 2.9 MB | V4.1 | 발굴 결과 |
| `v4_pick_reasons` | 84 | 168 kB | V4.1 | 종목 선정 사유 |

## 10. GO100 전용

| Table | Rows | Size | Description |
|-------|------|------|-------------|
| `go100_strategy_cards` | 26 | 288 kB | GO100 전략 카드 |
| `go100_data_integrity_log` | 5,549 | 1.5 MB | 데이터 무결성 로그 |
| `go100_reports` | 247 | 136 kB | 보고서 |
| `go100_notifications` | 20 | 160 kB | 알림 |
| `go100_global_market` | 294 | 216 kB | 글로벌 시장 |
| `go100_fit_analysis` | 40 | 88 kB | 적합성 분석 |
| `go100_calibration_params` | 12 | 48 kB | 보정 파라미터 |

## 11. 빈 테이블 (0행, 미사용/미수집)

총 47개 테이블이 0행 — 생성만 되고 데이터 미수집:
`v4_desk2_candidates`, `v4_desk2_trades`, `v4_desk2_signals`, `v4_desk2_daily_summary`,
`v4_condition_search`, `v4_sector_price`, `v4_theme_daily`, `v4_theme_activity_daily`,
`v4_theme_stock_mapping`, `v4_vi_history`, `v4_stock_master`, `v4_trade_analysis`,
`v4_bet_history`, `v4_order_executions`, `v4_llm_usage`, `v4_api_error_log`,
`v4_scalping_signals`, `v4_backtest_results`, `v4_position_transfers`,
`v4_user_strategies`, `v4_reports`, `v4_broker_trades`, `v4_system_state_log`,
`v4_notification_channel_config`, `v4_backtest_profile`,
`go100_paper_accounts`, `go100_paper_positions`, `go100_paper_orders`, `go100_paper_snapshots`,
`go100_portfolio_allocations`, `go100_optimization_runs`, `go100_orderbook_daily_stats`,
`go100_live_daily_summary`, `go100_live_trading_config`, `go100_gap_analysis`,
`go100_events`, `go100_signal_performance`, `go100_account_reconciliation`,
`go100_live_orders`, `go100_user_profiles`, `go100_tick_daily_stats`,
`go100_strategy_portfolio_snapshots`, `go100_experience_log`,
`liquidation_orders`, `liquidation_logs`, `liquidation_sessions`,
`strategy_performance`, `daily_trading_summary`, `payments`

---

## 12. 결측 데이터 식별 + 조치

### 존재하지만 분석기간 미커버
| 데이터 | 상태 | 조치 |
|--------|------|------|
| `v4_orderbook_realtime` | 오늘(02-27)만 | 과거 호가 데이터 없음 — 실시간 수집만 진행 중 |
| `v4_tick_data` | 오늘(02-27)만 | 과거 틱 데이터 없음 — 실시간 수집만 진행 중 |
| `v4_program_trades` | 02-25 1일만 | Kiwoom ka90004로 수집 시작했으나 과거 백필 안됨 |
| `v4_investor_daily` | 02-24(623), 02-25(148) | 최근 2일 수집 미완 — 백필 필요 |

### 필요하지만 없는 데이터
| 데이터 | 현재 상태 | 수집 가능성 |
|--------|----------|-------------|
| 종목별 외국인/기관 일별 순매수 | **v4_investor_daily에 존재!** | 이미 있음, 즉시 사용 가능 |
| 시장 레짐 | **v4_market_regime_daily에 존재** (KOSPI/KOSDAQ별) | 이미 있음 |
| 장전 뉴스 (08:00~09:00) | **go100_news_items에 15,304건 존재** | 이미 있음 |
| 과거 호가/틱 데이터 | 없음 | KIS API 과거 호가 제공 안함 — 향후 실시간 축적만 가능 |
| 과거 프로그램매매 | 1일만 | Kiwoom ka90004 백필 가능 (수집 스크립트 존재) |

### 핵심 발견
Phase 2에서 "없다"고 보고된 데이터 3건 모두 **실제로는 존재**:
1. **외국인/기관 순매수** → `v4_investor_daily` (261K행, 2010~현재)
2. **시장 레짐** → `v4_market_regime_daily` (822행, KOSPI/KOSDAQ별)
3. **장전 뉴스** → `go100_news_items` (data_time < 09:00, 15K건)

---

## 13. 테이블 분류

### V4.1 전용 (접두사 v4_)
- 시장: `v4_ohlcv_minute_*`, `v4_investor_daily`, `v4_market_regime_daily`, `v4_vkospi_daily`, `v4_sector_daily`
- 트레이딩: `v4_positions`, `v4_trades`, `v4_signals`, `v4_desk_*`, `strategy_cards`
- 백테스트: `v4_backtest_*`, `v4_bt_*`
- 호가/틱: `v4_orderbook_realtime`, `v4_tick_data`

### GO100 전용 (접두사 go100_)
- 뉴스: `go100_news_items`
- 전략: `go100_strategy_cards`, `go100_fundamentals*`
- 운영: `go100_reports`, `go100_notifications`, `go100_alerts`

### 공용
- `ohlcv_daily`, `stock_universe`, `accounts`, `users`

---

*Document Version*: 1.0
*Author*: Claude Opus 4.6
*Next Update*: 테이블 추가/변경 시 즉시 업데이트
