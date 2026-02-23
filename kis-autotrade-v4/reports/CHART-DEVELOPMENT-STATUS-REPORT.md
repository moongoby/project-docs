# 차트 개발 현황 보고서

- **문서 ID**: CHART-DEVELOPMENT-STATUS-REPORT
- **작성일**: 2026-02-24
- **기준 문서**: `docs/CHART-FEATURE-PLAN.md` (V4.1 차트 기능 기획)

---

## 1. 요약

| 구분 | 상태 | 비고 |
|------|------|------|
| **백엔드 V4 차트 API** | ✅ 완료 | 9개 엔드포인트 구현·등록 |
| **프론트 → V4 차트 연동** | ⬜ 미진행 | 프론트는 `/api/v1/market/*` 사용 중 |
| **종목 상세 차트(캔들·지표·오버레이)** | ⬜ 미구현 | 기획 3번 |
| **포트폴리오/백테스트 차트** | 🔶 부분 완료 | Recharts·SVG 컴포넌트 있음, V4 API 미연동 |
| **관리자 차트** | ⬜ 미구현 | 기획 5번 |

---

## 2. 백엔드 V4 차트 API (완료)

**파일**: `backend/app/routers/v4_chart.py`  
**prefix**: `/api/v4/chart`  
**메인 앱**: `main.py`에 `v4_chart.router` 등록 완료.

### 구현된 엔드포인트

| 메서드 | 경로 | 설명 | 데이터 소스 |
|--------|------|------|-------------|
| GET | `/chart/stocks` | 차트 검색용 종목 목록 | stock_universe |
| GET | `/chart/daily/{stock_code}` | 일봉 | ohlcv_daily |
| GET | `/chart/weekly/{stock_code}` | 주봉(월요일 시작 집계) | ohlcv_daily |
| GET | `/chart/minute/{stock_code}` | 분봉 (1/3/5/10/15/30/60분) | v4_ohlcv_minute |
| GET | `/chart/index/{index_code}` | 지수 일봉 | index_daily |
| GET | `/chart/investor/{stock_code}` | 투자자 동향 | v4_investor_daily |
| GET | `/chart/indicators/{stock_code}` | 기술적 지표(MA, RSI, Bollinger) | ohlcv_daily 기반 계산 |
| GET | `/chart/positions/overlay/{stock_code}` | 매매 이력 오버레이 | v4_positions, v4_trade_analysis (인증) |
| GET | `/chart/strategy-signals/{stock_code}` | 전략 시그널 | trading_signals(없으면 빈 배열) |

- **응답 형식**: 기획서 5절 데이터 포맷 준수 (일봉 `time`: YYYY-MM-DD, 분봉 `time`: Unix 초, 지표/투자자/매매 오버레이 형식 정의됨).
- **테스트**: `scripts/test_v41_chart.py` — 라우터 임포트·index·empty·인증(positions/overlay 401) 등 검증. DB/이벤트루프 이슈로 일부는 skip, curl 스모크 권장.

---

## 3. 프론트엔드 차트 현황

### 3.1 API 사용 현황

- **종목/시장 데이터**: `frontend/src/lib/api/market.ts` 기준 **V1 마켓 API** 사용.
  - 일봉: `getDailyChart()` → `GET /api/v1/market/chart/{stockCode}`
  - 분봉: `getMinuteBars()` → `GET /api/v1/market/minute-bars/{stockCode}`
  - 수급: `getInvestorFlow()` → `GET /api/v1/market/investor-flow/{stockCode}`
  - 기타: 호가, 재무, 섹터, 순위, 테마, 체결강도, 키움 차트 등 모두 `/api/v1/market/*`.
- **V4 차트 API (`/api/v4/chart/*`) 호출**: 프론트엔드 코드에서 **사용처 없음** (grep 기준).

→ **기획 2번 “기존 kiwoom 차트 페이지 → V4 API 전환” 미완료.**

### 3.2 구현된 차트 컴포넌트

| 컴포넌트 | 경로 | 용도 | 라이브러리/데이터 |
|----------|------|------|-------------------|
| **PortfolioChart** | `go100/components/PortfolioChart.tsx` | GO100 페이퍼 포트폴리오 | Recharts, 스냅샷(일별 자산·수익률) |
| **PerformanceChart** | `portfolio/PerformanceChart.tsx` | 수익률 곡선 | SVG, `PerformanceDataPoint[]` |
| **AssetPieChart** | `portfolio/AssetPieChart.tsx` | 자산 비중 파이 | Recharts |
| **ProfitBarChart** | `portfolio/ProfitBarChart.tsx` | 수익/손실 바 | Recharts |
| **ExitReasonChart** | `backtest/ExitReasonChart.tsx` | 백테스트 청산 사유 | Recharts |
| **StockDetailModal** | `market/StockDetailModal.tsx` | 종목 상세(분봉·수급 등) | v1 market API (분봉·수급·호가·재무 등) |

- 포트폴리오/백테스트 차트는 **대시보드·백테스트 결과 데이터**와 연동되어 있으나, **V4 chart API와는 직접 연동되지 않음**.

### 3.3 종목 상세 차트(캔들·지표·오버레이)

- **기획 3번** “종목 상세 차트 페이지 확장 (캔들 + MA/RSI/볼린저 + 매매 마커 + 전략 시그널 + 거래량 + 투자자 동향)”:
  - **전용 페이지/뷰**: `/stock/{stock_code}` 또는 kiwoom 스타일 차트 전용 페이지는 코드베이스에 없음.
  - **StockDetailModal**: 종목 상세 정보·분봉·수급 등 표시하나, **TradingView Lightweight Charts 캔들 + 지표 + 매매 오버레이** 구성은 없음.
- **라이브러리**: 기획서상 TradingView Lightweight Charts v4.2.0 (CDN) 단일 사용 예정이나, 현재 프론트엔드에서 해당 캔들 차트 컴포넌트 구현 여부는 **미확인** (캔들 전용 컴포넌트 검색 시 별도 파일 없음).

---

## 4. 기획 대비 우선순위별 정리

| 순위 | 항목 (CHART-FEATURE-PLAN §6) | 현재 상태 |
|------|------------------------------|-----------|
| 1 | V4.1 차트 API 7개 엔드포인트 | ✅ **완료** (실제로 9개: stocks, daily, weekly, minute, index, investor, indicators, positions/overlay, strategy-signals) |
| 2 | 기존 kiwoom 차트 페이지 → V4 API 전환 | ⬜ **미진행** — 프론트는 v1 market API 사용 |
| 3 | 종목 상세 차트 페이지 확장(지표·오버레이) | ⬜ **미구현** — 캔들+지표+매매마커+전략시그널 UI 없음 |
| 4 | 포트폴리오/백테스트 차트 | 🔶 **부분** — GO100·포트폴리오·백테스트용 차트 컴포넌트 있음, V4 chart API 미연동 |
| 5 | 관리자 데이터 품질·종목 분석 차트 | ⬜ **미구현** |

---

## 5. 권장 다음 단계

1. **프론트 V4 차트 연동**
   - `market.ts`에 `/api/v4/chart/daily`, `/api/v4/chart/minute`, `/api/v4/chart/indicators`, `/api/v4/chart/investor`, `/api/v4/chart/positions/overlay` 등 클라이언트 함수 추가.
   - 종목 상세(또는 키움 스타일 차트)에서 기존 v1 호출을 v4 chart API로 전환하거나, v1 compat 레이어가 v4를 바라보도록 백엔드에서 라우팅.

2. **종목 상세 차트 페이지/모달 확장**
   - TradingView Lightweight Charts 사용하는 **캔들 + 거래량** 컴포넌트 구현.
   - V4 `/chart/indicators`, `/chart/positions/overlay`, `/chart/strategy-signals`, `/chart/investor` 연동해 MA/RSI/볼린저·매매 마커·전략 시그널·투자자 동향 표시.

3. **포트폴리오/백테스트**
   - 필요 시 V4 `/chart/positions/overlay`, `/chart/daily` 등으로 “매매 오버레이 캔들” 등 기획 4번 항목 연동.

4. **관리자**
   - 기획 5번(데이터 품질 모니터링, 종목 분석 차트)은 별도 스프린트로 설계 후 구현.

---

## 6. 어떻게 해야 하나 — 실행 로드맵

차트 미구현 항목을 **효과 순서**대로 나누면 아래와 같다. 한 번에 다 하지 말고 **Phase 1 → 2 → 3** 순으로 진행하는 것을 권장한다.

### Phase 1: V4 API 연동만 먼저 (1~2일, 백엔드 수정 최소)

**목표**: 프론트가 V4 차트 API를 쓰도록만 바꾼다. UI는 기존 그대로 두고 **데이터 소스만** V4로 전환.

| 순서 | 작업 | 파일 | 설명 |
|------|------|------|------|
| 1-1 | V4 chart API 클라이언트 추가 | `frontend/src/lib/api/market.ts` 또는 `frontend/src/lib/api/chart.ts` | `getChartDaily()`, `getChartMinute()`, `getChartIndicators()`, `getChartInvestor()`, `getChartPositionsOverlay()` 등 → `/api/v4/chart/*` 호출 |
| 1-2 | (선택) V1 compat에서 chart 요청을 V4로 라우팅 | 백엔드 `v4_compat` 또는 market 라우터 | `/api/v1/market/chart/*`, `minute-bars/*`, `investor-flow/*` 요청을 내부적으로 V4 chart API 호출로 대체. 프론트 수정 없이 백엔드만 바꿀 수 있음. |
| 1-3 | 종목 상세에서 V4 사용하도록 전환 | `StockDetailModal.tsx` 등 | `getMinuteBars` → V4 `getChartMinute`, `getInvestorFlow` → V4 `getChartInvestor` 등으로 교체 후 응답 필드명만 매핑 (time/date, volume 등). |

**결과**: 기존 화면 그대로 두고도 V4 데이터로 동작. “V4 전환” 체감 가능.

---

### Phase 2: 종목 상세 차트 확장 (1~2주)

**목표**: 기획 3번 — 캔들 + 지표 + 매매 마커 + 전략 시그널 + 투자자 동향 한 화면에 구성.

| 순서 | 작업 | 설명 |
|------|------|------|
| 2-1 | Lightweight Charts 패키지 추가 | `pnpm add lightweight-charts` (또는 기획서대로 CDN). |
| 2-2 | 캔들+거래량 컴포넌트 1개 구현 | `StockChart.tsx` 같은 단일 컴포넌트. V4 `daily` 또는 `minute` 데이터 받아서 캔들 + 볼륨 바 렌더링. |
| 2-3 | 지표 오버레이 | V4 `indicators` (ma20, ma60, rsi, bollinger) 연동. 라인 시리즈·별도 RSI 패널 등. |
| 2-4 | 매매 마커 / 전략 시그널 | V4 `positions/overlay`, `strategy-signals`로 마커(▲매수 ▼매도, ◆BUY ◇SELL) 표시. |
| 2-5 | 투자자 동향 블록 | V4 `investor` 데이터로 외국인/기관 순매매 차트(작은 바/라인)를 차트 아래 또는 옆에 배치. |
| 2-6 | 종목 상세 페이지/모달에 배치 | `/stock/[code]` 페이지 또는 `StockDetailModal` 안에 `StockChart` 넣고, 일봉/분봉 탭 등으로 전환. |

**결과**: 사용자용 “종목 상세 차트” 기획 3번 완료.

---

### Phase 3: 포트폴리오·백테스트·관리자 (필요 시 순차)

| 구분 | 작업 | 우선순위 |
|------|------|----------|
| **포트폴리오** | 이미 있는 `PortfolioChart` 등은 데이터 소스만 유지해도 됨. “매매 오버레이 캔들”이 필요하면 V4 `chart/daily` + `positions/overlay` 연동한 작은 캔들 뷰 추가. | 중 |
| **백테스트** | 자본 곡선·드로우다운·월별 히트맵은 기존대로. “결과 상세에서 해당 종목 캔들+매매 포인트”만 V4 chart로 넣을지 결정 후 구현. | 중 |
| **관리자** | 데이터 품질(갭·커버리지)·종목 분석 차트는 별도 스프린트. 기획 5번 문서 보고 요구사항 정리 후 진행. | 낮 |

---

### 체크리스트 (Phase 1) — 2026-02-24 진행분

- [x] `frontend`: `/api/v4/chart`용 API 함수 추가 → `frontend/src/lib/api/chart.ts` (getChartStocks, getChartDaily, getChartWeekly, getChartMinute, getChartIndex, getChartInvestor, getChartIndicators, getChartPositionsOverlay, getChartStrategySignals)
- [x] `frontend`: `StockDetailModal`에서 분봉·수급을 V4로 전환 — `getChartMinute`, `getChartInvestor` 사용, 응답 필드 매핑 (time/inst_net→institution_net)
- [ ] (선택) `backend`: V1 market chart/minute-bars/investor-flow를 V4 chart 호출로 compat
- [ ] 브라우저에서 종목 상세 열어서 분봉·수급 등이 V4 데이터로 나오는지 확인

---

## 7. Phase 2 완료 내역 (2026-02-24)

- [x] **2-1** lightweight-charts v5.1.0 패키지 추가
- [x] **2-2** `StockChart.tsx` — 캔들 + 거래량 (CandlestickSeries, HistogramSeries), 클라이언트 전용 동적 import
- [x] **2-3** 지표 오버레이: MA(5/20/60/120), 볼린저, RSI(별도 pane) — V4 `indicators` 연동
- [x] **2-4** 매매 마커·전략 시그널: `createSeriesMarkers`로 매수/매도·◆◇ 표시 — V4 `positions/overlay`, `strategy-signals` 연동
- [x] **2-5** 투자자 동향: Phase 1에서 이미 V4 `investor` 사용 중 (FlowBars 유지)
- [x] **2-6** `StockDetailModal`: 일봉/분봉 탭 추가, 일봉 탭에 `StockChart`(daily + indicators + trades + signals), 분봉 탭에 `StockChart`(minute + volume)

---

## 8. 참고 파일

- 기획: `docs/CHART-FEATURE-PLAN.md`
- 백엔드 차트 라우터: `backend/app/routers/v4_chart.py`
- 차트 API 테스트: `scripts/test_v41_chart.py`
- 프론트 시장 API: `frontend/src/lib/api/market.ts`
- GO100 포트폴리오 차트: `frontend/src/go100/components/PortfolioChart.tsx`
- API 매핑: `docs/FRONTEND-API-MAPPING.md` (차트 전용 Stage는 없음)
