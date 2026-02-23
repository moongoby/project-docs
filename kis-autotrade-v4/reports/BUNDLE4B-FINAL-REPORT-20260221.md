# CUR-GO100-BUNDLE4B 최종 보고서
**일시**: 2026-02-21 | **커밋**: `ab44d85a`, `0c80b5f0` | **브랜치**: `phase-2c-command-center`

---

## 0. 사전 백업
| 항목 | 값 |
|------|-----|
| 백업 파일 | `/tmp/backup_bundle4b_pre_20260221_184436.dump` |
| 백업 크기 | 329MB (정상) |
| CEO user_id | 2 (moongoby@gmail.com, 대표님, PREMIUM) |
| 분봉 보유 종목 수 | 546개 (`/tmp/minute_stock_codes.txt`) |

---

## 1. Advanced Universe Filters (12개)
**파일**: `backend/app/services/go100/universe/advanced_filters.py` (신규)

| # | 필터 | 메서드 | 데이터 소스 |
|---|------|--------|------------|
| 1 | 시가총액 | `filter_market_cap` | stock_fundamentals JOIN stock_universe |
| 2 | 평균거래대금 | `filter_trade_amount` | ohlcv_daily (N일 평균) |
| 3 | 일중변동폭 | `filter_intraday_volatility` | ohlcv_daily (high-low)/close |
| 4 | 외국인/기관 수급 | `filter_institutional_flow` | v4_investor_daily consecutive_*_buy_days |
| 5 | 신저가 회피 | `filter_exclude_new_low` | ohlcv_daily (최근종가 vs N일 최저) |
| 6 | PER 양수 | `filter_per_positive` | stock_fundamentals |
| 7 | 거래정지 제외 | `filter_exclude_suspended` | ohlcv_daily (volume>0 일수) |
| 8 | 섹터 모멘텀 | `filter_sector_momentum` | v4_sector_daily + v4_stock_sector |
| 9 | 분봉 보유 | `filter_has_minute_data` | v4_ohlcv_minute |
| 10 | 갭상승 | `filter_gap_up` | ohlcv_daily (open vs prev_close) |
| 11 | 재무건전성 | `filter_financial_health` | financial_ratios (부채율/ROE/매출성장) |
| 12 | 마켓레짐 | `get_market_regime` | index_daily + v4_vkospi_daily + v4_market_investor_daily |

**build_universe 파이프라인**:
- `scalping`: 분봉보유 → 시가총액 → 거래대금 → 일중변동폭 → 거래정지제외
- `daily`: 시가총액 → 거래대금 → PER양수 → 거래정지제외 → 수급
- `swing`: 시가총액 → 거래대금 → 섹터모멘텀 → 거래정지제외 → 재무건전성 → 수급

---

## 2. 분봉 데이터 로더
**파일**: `backend/app/services/go100/backtest/minute_data_loader.py` (신규)

- `load_minute_data()`: v4_ohlcv_minute에서 단일 종목 분봉 로드
- `load_minute_batch()`: 다종목 배치 로드
- `aggregate_to_nmin(df, n)`: 1분봉 → N분봉 집계 (OHLCV + VWAP)
- `get_daily_with_minute()`: 분봉 + 당일/전일 일봉 병합
- `calc_minute_indicators()`: MA5, MA20, RSI14, VWAP, volume_ratio_20, momentum_10

---

## 3. 분할익절 시뮬레이터
**파일**: `backend/app/services/go100/backtest/partial_exit_simulator.py` (신규)

- `PartialExitConfig`: 다단계 분할익절 설정 (exit_levels, stop_loss, trailing_stop, force_close_time, time_stop_days)
- `ExitLevel`: target_pct, sell_pct, move_stop_to_pct
- `ExitEvent`: 청산 이벤트 (날짜, 시간, 가격, 수량, 사유, 수익률, 수수료, 세금, 순금액)
- 우선순위: stop_loss → force_close → time_stop → partial_exit → trailing_stop
- 수수료 0.015%, 세금 0.18%

---

## 4. 분봉 시뮬레이터
**파일**: `backend/app/services/go100/backtest/minute_simulator.py` (신규)

- 일봉 스크리닝 → 분봉 entry/exit → 분할익절 통합
- `run_backtest()`: 일별 루프 — universe → signal eval → minute position management → equity curve
- `_parse_partial_config()`: risk_params → PartialExitConfig 변환 (기본 2단)
- `_partial_summary()`: 청산 사유별 통계

---

## 5. 백테스트 서비스 확장
**파일**: `backend/app/services/go100/backtest/backtest_service.py` (수정)
**파일**: `backend/app/services/go100/backtest/schemas.py` (수정)

- `Go100BacktestRequest`에 `data_source`, `universe_mode`, `bar_interval` 필드 추가
- `run_backtest()` 분기: daily → BacktestSimulator / minute → Go100MinuteSimulator
- `universe_mode=advanced` → Go100AdvancedFilters.build_universe() 사용

---

## 6. AI 프롬프트 확장
**파일**: `backend/app/services/go100/ai/prompts.py` (수정)

- `ADVANCED_FILTER_SPEC`: 12개 필터 문서화 (파라미터, 파이프라인 기본값)
- `PARTIAL_EXIT_SPEC`: 분할익절 JSON 구조 및 플로우
- `DESIGN_SYSTEM_PROMPT`: partial_exit 출력 포맷, data_source/bar_interval 필드 추가
- `EVALUATE_SYSTEM_PROMPT`: 유니버스 크기, 분할익절 비율, 프로핏 팩터 평가 추가

---

## 7. 테스트 결과
| 테스트 파일 | 테스트 수 | 상태 |
|------------|----------|------|
| test_go100_advanced_filters.py (신규) | 15 | PASSED |
| test_go100_minute_backtest.py (신규) | 16 | PASSED |
| test_go100_strategy_card_service.py | 10 | PASSED |
| test_go100_portfolio_service.py | 8 | PASSED |
| test_go100_paper_trading.py | 12 | PASSED |
| test_go100_position_sizing.py | 11 | PASSED |
| test_go100_ai_agents.py | 12 | PASSED |
| test_go100_live_trading.py | 10 | PASSED |
| test_go100_backtest_service.py | 15 | PASSED |
| test_universe_engine_unit.py | 10 | PASSED |
| test_go100_scheduler.py | 10 | PASSED |
| **합계** | **129** | **ALL PASSED** |

---

## 8. CEO 전략 3건 (AI Chat 생성)

| Card ID | 전략명 | 유형 | source_type | card_status |
|---------|--------|------|-------------|-------------|
| 4 | 3분봉 골든크로스 스캘핑 | scalping | LLM | PAPER_LIVE |
| 5 | 데일리 수급 반등 전략 | daily | LLM | PAPER_LIVE |
| 6 | 단기 스윙 눌림목 전략 | swing | LLM | PAPER_LIVE |

---

## 9. Paper Trading 현황

| Portfolio ID | Card ID | 전략명 | is_paper | status | initial_capital |
|-------------|---------|--------|----------|--------|-----------------|
| 3 | 4 | 3분봉 골든크로스 스캘핑 | true | ACTIVE | 10,000,000 |
| 4 | 5 | 데일리 수급 반등 전략 | true | ACTIVE | 10,000,000 |
| 5 | 6 | 단기 스윙 눌림목 전략 | true | ACTIVE | 10,000,000 |

---

## 10. 서비스 상태

| 서비스 | 상태 | 비고 |
|--------|------|------|
| go100 | active | 8002 정상 응답 |
| kis-v41-api | active | 8003 |
| kis-v41-scheduler | active | — |
| kis-v41-monitor | active | — |
| kis-v41-minute-collector | inactive | 16:00 평일만 가동 (정상) |
| go100 health | OK | `{"status":"ok","version":"4.1.0","database":"connected","redis":"connected"}` |

---

## 11. 신규/수정 파일 목록

### 신규 파일 (Backend)
1. `backend/app/services/go100/universe/advanced_filters.py`
2. `backend/app/services/go100/backtest/minute_data_loader.py`
3. `backend/app/services/go100/backtest/partial_exit_simulator.py`
4. `backend/app/services/go100/backtest/minute_simulator.py`
5. `backend/tests/test_go100_advanced_filters.py`
6. `backend/tests/test_go100_minute_backtest.py`

### 수정 파일 (Backend)
7. `backend/app/services/go100/backtest/backtest_service.py`
8. `backend/app/services/go100/backtest/schemas.py`
9. `backend/app/services/go100/ai/prompts.py`

### 신규/수정 파일 (Frontend)
10. `frontend/src/go100/components/DashboardContent.tsx` (신규)
11. `frontend/src/go100/components/LiveTradingDetailContent.tsx` (신규)
12. `frontend/src/go100/components/MobileMenuButton.tsx` (신규)
13. `frontend/src/go100/components/PaperTradingDetailContent.tsx` (신규)
14. `frontend/src/go100/components/SettingsRiskSection.tsx` (신규)
15. `frontend/src/go100/components/Toast.tsx` (신규)
16. `frontend/src/go100/hooks/*.ts` (신규 6개)
17. `frontend/src/go100/components/*.tsx` (수정 — Layout, Sidebar, PortfolioChart, RiskConfigForm, index)
18. `frontend/src/go100/api/go100Api.ts` (수정)
19. `frontend/src/app/(protected)/go100/**/*.tsx` (수정 4개)
20. `frontend/package.json`, `frontend/package-lock.json` (수정)

### 보고서
21. `report/BUNDLE4A-STEP1-DATA-AUDIT-20260221.md`
22. `report/BUNDLE4B-FINAL-REPORT-20260221.md`

---

## 12. 컴플라이언스 체크리스트

| 항목 | 결과 |
|------|------|
| `.env/.bak` 커밋 여부 | **미포함** (git diff --cached 확인) |
| `strategy_cards` 59건 | **59건 유지** |
| `v4_positions` OPEN 수 | **5건 유지** |
| 파일 헤더 | `# Modified by: CUR-GO100-BUNDLE4B, 2026-02-21` |
| DB 스키마 변경 | **없음** (go100_ 테이블 기존 구조 활용) |
| 서비스 재시작 | go100 수동 재시작 완료 |
| V4.1 파일 수정 여부 | **없음** (go100/ 범위만 수정) |

---

## 13. 주요 발견 사항 (BUNDLE4A 데이터 감사)

1. **stock_universe.market_cap = ALL NULL** → 모든 시가총액 필터는 `stock_fundamentals` JOIN 필수
2. **v4_market_regime_daily 2건만 존재** → market_regime 자체 계산 로직 구현
3. **financial_ratios 45,870건** (2004~2025) — 재무건전성 필터에 활용
4. **v4_investor_daily** consecutive_*_buy_days 컬럼 존재 — 수급 필터 직접 활용 가능
5. 전체 DB: 156 테이블, 4,161MB

---

**작성**: Claude Code (CUR-GO100-BUNDLE4B) | **커밋**: `ab44d85a` + `0c80b5f0`
