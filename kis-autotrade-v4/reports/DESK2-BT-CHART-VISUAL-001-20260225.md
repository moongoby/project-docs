# DESK2-BT-CHART-VISUAL-001 백테스트 차트 시각화 보고서
**작성일:** 2026-02-25  
**브랜치:** phase-2c-command-center  
**우선순위:** P0 (CEO 직접 지시)

## 1. 개요
백테스트 결과를 숫자가 아닌 차트 위에서 검증한다. 거래 클릭 시 해당 종목의 분봉·일봉 차트에 진입/청산 화살표, 보유 구간, 보조지표가 그려지며, 발굴 시점부터 장 마감까지의 생애주기를 차트로 확인할 수 있다.

## 2. 재사용 자산
- **StockChart.tsx** (`frontend/src/components/market/StockChart.tsx`) — lightweight-charts 기반 캔들·거래량·기존 지표(ma5, ma20, bollinger, rsi)·trades/signals 마커 유지
- **StockDetailModal.tsx** — 기존 동작 유지, 미수정
- **V4 차트 API** (`/api/v4/chart/*`) — 일봉/분봉/지표/포지션 오버레이 등 9개 엔드포인트 그대로 활용
- **lightweight-charts** `^5.1.0` — 기존 설치 버전 사용

## 3. 추가된 StockChart optional props
- **markers** (`TradeMarker[]`) — 전달 시 `candleSeries.setMarkers(markers)` 호출. 미전달 시 기존처럼 `trades`/`signals`로 마커 생성.
- **highlightRanges** (`HighlightRange[]`) — 보유 구간 등 영역 표시. 각 구간에 대해 AreaSeries로 minLow~maxHigh 채움.
- **indicatorLines** (`IndicatorLine[]`) — 지표별 `chart.addSeries(LineSeries)` 추가 (이름·데이터·색상).

타입: `TradeMarker.time`·`HighlightRange.startTime/endTime`·`IndicatorLine.data[].time` 은 `string | number` 지원.

## 4. 신규 컴포넌트
- **TimeframeSelector** (`frontend/src/components/admin/backtest/TimeframeSelector.tsx`) — 선택 타임프레임 탭 (1m~1d).
- **TradeInfoPanel** (`frontend/src/components/admin/backtest/TradeInfoPanel.tsx`) — 거래 상세(전략, 진입/청산, 수익률, 수수료/세금, 복합점수 등).

## 5. 신규 백엔드 API (prefix: `/api/v1/backtest/chart`)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/trade/{trade_id}` | 단일 거래 차트: 캔들 + 진입/청산 마커 + 보유 구간 하이라이트 + VWAP/BB/MA20 |
| GET | `/trade/{trade_id}/timeframe/{tf}` | 동일 거래를 지정 tf(1m|3m|5m|10m|30m|60m|1d)로 리샘플한 캔들·마커·지표 |
| GET | `/discovery/{discovery_id}` | 발굴 생애주기: 발굴 시각~장 마감 5분봉 + 발굴 마커 + VWAP, lifecycle(이론 최대/실제 포착 수익) |
| GET | `/daily-summary/{session_id}/{date}` | 해당일 레짐·일일 손익·KOSPI 분봉 + 거래 마커, trades/discoveries 목록 |
| GET | `/strategy-compare/{session_id}/{stock_code}/{date}` | 동일 종목·날짜 전략별 진입/청산 시점 색상 구분 |

기존 쿼리 기반 엔드포인트(`/candles`, `/indicators`, `/trade-overlay`, `/multi-timeframe`, `/strategy-config`) 유지.

## 6. 리샘플링
- **CandleResampler** (`backend/app/services/trading/desk2/utils/candle_resampler.py`): 기존 `resample(minute_bars, target_minutes: int)` 사용.
- **resample_tf(minute_bars, target_tf: str)** 클래스 메서드 추가 — `'1m'`~`'60m'` 매핑 후 `resample` 호출, `'1d'`는 빈 리스트(일봉은 별도 ohlcv_daily 경로).

## 7. 프론트엔드 페이지
- **거래 차트 상세** — `(protected)/admin/backtest/trades/[tradeId]/page.tsx`: 상단 요약, TimeframeSelector + StockChart(markers, highlightRanges, indicatorLines), 우측 TradeInfoPanel.
- **발굴 생애주기** — `(protected)/admin/backtest/discovery/[discoveryId]/page.tsx`: 발굴 요약, StockChart(발굴 마커 + 지표), 하단 lifecycle 카드.
- **일일 타임라인** — `(protected)/admin/backtest/daily/[sessionId]/[date]/page.tsx`: 세션·날짜 요약, KOSPI 분봉 + 거래 마커, 당일 거래 목록.
- **백테스트 차트 진입** — `(protected)/admin/backtest/charts/page.tsx`: 거래 차트 / 발굴 추적 / 일일 타임라인 카드 링크.

## 8. 기존 목록 연동
- **거래 목록** — `TradeTimeline.tsx`: 기존 "차트 보기" 버튼 유지 → `/admin/backtest/trades/[tradeId]`.
- **발굴 목록** — `DiscoveryPanel.tsx`: 발굴 기록 테이블에 "차트" 열 추가. `d.id`가 있을 때만 `/admin/backtest/discovery/[id]` 링크 표시(API에서 id 반환 시 연동).

## 9. API 훅
- **backtestChartApi.ts** (`frontend/src/lib/api/backtestChartApi.ts`): `getTradeChart`, `getTradeChartTimeframe`, `getDiscoveryChart`, `getDailySummaryChart`, `getStrategyCompareChart` 및 관련 타입 정의.

## 10. 사이드바
- 관리자 메뉴에 **"백테스트 차트"** 링크 추가 → `/admin/backtest/charts`.

## 11. 빌드·검증
- **프론트엔드:** `npm run build` 오류 0건 완료.
- **기존 차트 영향:** StockChart에서 `markers`/`highlightRanges`/`indicatorLines` 미전달 시 기존과 동일 동작(기존 props만 사용).

## 12. 규칙 준수
- kis-v41-api / monitor / scheduler 재시작 없음.
- strategy_cards ALTER/DROP/DELETE 없음.
- v4_positions 직접 수정 없음.
- `datetime.now(timezone.utc)` 사용.
- f-string 로깅 미사용.
- `typing.Any` 제거(bt_chart.py에서 `List[object]` 등으로 대체).
- 기존 StockChart/StockDetailModal 기능 훼손 없음(optional props 추가만).

## 13. 완료 체크리스트
| # | 항목 | 확인 |
|---|------|------|
| 1 | StockChart.tsx에 markers/highlightRanges/indicatorLines props 추가 | ✅ |
| 2 | 기존 props만 사용 시 동작 변화 없음 | ✅ |
| 3 | TimeframeSelector, TradeInfoPanel 생성 | ✅ |
| 4 | bt_chart.py 경로 기반 5개 엔드포인트 구현 | ✅ |
| 5 | main.py에 bt_chart 라우터 등록(기존 유지) | ✅ |
| 6 | CandleResampler.resample_tf 추가 | ✅ |
| 7 | 거래 차트 상세 페이지 구현 | ✅ |
| 8 | 발굴 생애주기 차트 페이지 구현 | ✅ |
| 9 | 일일 타임라인 페이지 구현 | ✅ |
| 10 | 거래/발굴 목록에 차트 보기 연동 | ✅ |
| 11 | backtestChartApi.ts 훅 5개 구현 | ✅ |
| 12 | npm run build 오류 0건 | ✅ |
| 13 | 보고서 작성 | ✅ |
