# BT-CHART-VISUALIZER-001 구현 보고서

**작성일시**: 2026-02-25 17:30 KST  
**브랜치**: phase-2c-command-center  
**우선순위**: P0 (백테스트 검증 핵심 기능)

---

## 1. 목표

백테스트 거래를 멀티 타임프레임 차트 위에 시각화하여, CEO가 각 진입/청산이 차트상 합리적인지 육안 검증할 수 있는 기능 구현.

---

## 2. 구현 요약

### 2-1. 기존 자산 활용

- **프론트엔드**: `StockChart` (lightweight-charts 기반) — 캔들, 거래량, 지표(MA/RSI/볼린저), 매매 마커 지원
- **API 클라이언트**: `lib/api/chart.ts` (V4 차트) 참고하여 백테스트 전용 `lib/api/backtest-chart.ts` 추가
- **백엔드**: `v4_chart` 라우터의 분봉/일봉/지표 로직 참고, 백테스트 전용 `bt_chart` 라우터 신규 추가

### 2-2. 백엔드 API (5개 엔드포인트)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/backtest/chart/candles` | OHLCV 캔들 (stock_code, date, timeframe) |
| GET | `/api/v1/backtest/chart/indicators` | 지표 시계열 (rsi, vwap, bb, ma20, ma60, ma120) |
| GET | `/api/v1/backtest/chart/trade-overlay` | 진입/청산 마커, 전략 참조 타임프레임 (trade_id) |
| GET | `/api/v1/backtest/chart/multi-timeframe` | trade_id 기준 멀티 TF 캔들+지표 통합 |
| GET | `/api/v1/backtest/chart/strategy-config` | 전략별 참조 타임프레임·지표 (strategy_name) |

- **파일**: `backend/app/routers/bt_chart.py`
- **등록**: `main.py` — `app.include_router(bt_chart_router, prefix="/api/v1/backtest/chart")`

### 2-3. 리샘플링·지표 유틸

- **파일**: `backend/app/services/trading/desk2/utils/candle_resampler.py`
- **클래스**: `CandleResampler`
  - `resample(minute_bars, target_minutes)`: 1분봉 → N분봉 (open=첫봉, high=max, low=min, close=마지막봉, volume=sum)
  - `calc_rsi(closes, period=14)`
  - `calc_vwap(highs, lows, closes, volumes)`
  - `calc_bollinger(closes, period=20, std_dev=2)`
  - `calc_ma(closes, period)`

### 2-4. 지원 타임프레임·지표

- **타임프레임**: 1m, 3m, 5m, 10m, 30m, 60m, 1d
- **지표**: RSI(14), VWAP, 볼린저(20,2), MA20, MA60, MA120
- **전략별 기본 TF**: ALPHA_GAP(5m,1d), BRAVO_ORB(5m,1d), DELTA_VWAP(5m,10m), ECHO_ABCD(5m,30m,1d), GOLF_REVERSAL(5m,60m,1d)

### 2-5. 프론트엔드 컴포넌트

| 컴포넌트 | 경로 | 설명 |
|----------|------|------|
| BacktestTradeChart | `components/admin/backtest/BacktestTradeChart.tsx` | 멀티 TF 탭 + 기존 StockChart 재사용 |
| 거래 차트 페이지 | `app/(protected)/admin/backtest/trades/[tradeId]/page.tsx` | 거래 상세 + BacktestTradeChart |
| TradeTimeline | `components/admin/backtest/TradeTimeline.tsx` | "차트 보기" 버튼 추가 → `/admin/backtest/trades/{tradeId}` |

- **API 훅**: `getBacktestMultiTimeframe`, `getBacktestTradeOverlay` 등 — `lib/api/backtest-chart.ts` + react-query `useQuery` 사용
- **StockChart 수정**: 지표 시간 포맷을 `timeFormat`(daily/minute)에 맞춰 사용하도록 변경

### 2-6. 데이터 소스

- **분봉**: `v4_ohlcv_minute` (trade_date, trade_time, open_price, high_price, low_price, close_price, volume)
- **일봉**: `ohlcv_daily` (date, open, high, low, close, volume)
- **거래**: `v4_bt_trades` (entry_date, entry_time, exit_date, exit_time, entry_price, exit_price, pnl_pct 등)
- **스키마 확장**: v4_bt_trades에 진입/청산 시각 필드가 이미 존재하여 별도 마이그레이션 없음

---

## 3. 검증

- 백엔드: `PYTHONPATH=backend .venv/bin/python -c "from app.routers.bt_chart import router; from app.services.trading.desk2.utils.candle_resampler import CandleResampler"` — 정상 로드, 라우트 5개
- 프론트엔드: `npm run build` — 타입/린트 수정 후 0 에러 목표
- API: 서비스 기동 후 `GET /api/v1/backtest/chart/candles?stock_code=005930&date=20260203&timeframe=5m`, `GET /api/v1/backtest/chart/multi-timeframe?trade_id=...` 호출로 검증 권장

---

## 4. 완료 체크리스트

- [x] CandleResampler 구현 (1/3/5/10/30/60m, 1d)
- [x] bt_chart.py 5개 API 엔드포인트
- [x] main.py 라우터 등록
- [x] 기존 StockChart 활용 (lightweight-charts)
- [x] BacktestTradeChart (멀티 TF 탭)
- [x] TradeMarker (진입/청산) — StockChart trades 오버레이
- [x] IndicatorOverlay (RSI/VWAP/BB/MA) — StockChart indicators
- [x] TimeframeSelector — 탭(5m/30m/1d)
- [x] v4_bt_trades 기존 컬럼 사용 (entry_time, exit_time 등)
- [ ] npm run build 0 에러 (타입 수정 후 최종 확인)
- [ ] API 실제 응답 검증 (서비스 환경)
- [ ] 보고서 push (소스/문서 repo)

---

## 5. 참고

- 리샘플링: 5분봉 → 30분봉 시 6개 봉 그룹핑 (open=그룹 첫 봉 open, close=마지막 봉 close, high/low=구간 max/min, volume=sum)
- SQL injection 방지: `_safe_alphanumeric`로 파라미터 검증
- 한국시간(KST): 로그/보고서는 KST 기준, 서버 내부는 `datetime.now(timezone.utc)` 사용
