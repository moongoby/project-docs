# CUR-GO100-CHART-FULLCHECK-001 — 차트 전체 페이지 확인 + 대시보드 팝업 수정

**발행:** 2026-02-24  
**우선순위:** P0

---

## 1. 차트 보고서 내용 요약

| 문서 | 위치 | 요약 |
|------|------|------|
| **CHART-DEVELOPMENT-STATUS-REPORT** | `report/CHART-DEVELOPMENT-STATUS-REPORT.md` | 백엔드 V4 차트 API 9개 엔드포인트 완료. 프론트는 V4 chart 연동 완료(StockDetailModal에서 getChartDaily 등 사용). 종목 상세 차트(캔들·지표·오버레이)는 StockChart로 구현됨. |
| **CHART-ALL-ROUTES-EXTERNAL-URL** | `report/CHART-ALL-ROUTES-EXTERNAL-URL.md` | 차트 진입 경로: /dashboard(보유·시장순위·수급·최근거래), /portfolio, /backtest, /stock/[code] 등. |
| **CHART-USER-PAGE-INTEGRATION-PLAN** | `report/CHART-USER-PAGE-INTEGRATION-PLAN.md` | 대시보드 HoldingsCard에서만 종목 클릭 → StockDetailModal 반영됨. 시장 순위·수급·최근 거래에서 진입은 **미구현**으로 명시됨. |
| **CHART-HEALTH-CHECK-001** | `report/v41/CHART-HEALTH-CHECK-001-20260224.md` | 백테스트 분석 차트 페이지 접속·API 정상. regime-timeline 등 동작. |

---

## 2. 대시보드 팝업 미작동 원인 및 수정

### 원인
- **보유 종목 TOP5(HoldingsCard)**  
  - 이미 `onStockClick` → `setDetailStock` → `StockDetailModal` 연결되어 있음. **코드상 정상**.
- **시장 순위·수급 요약·최근 거래**  
  - `MarketRankingsWidget`, `InvestorFlowWidget`, `RecentTradesCard`에는 **종목 클릭 시 모달을 여는 콜백이 없었음** (CHART-USER-PAGE-INTEGRATION-PLAN의 “진입 경로 확대” 미반영).

### 수정 내용 (CUR-GO100-CHART-FULLCHECK-001)

1. **MarketRankingsWidget**  
   - `onStockClick?: (stockCode, stockName?) => void` prop 추가.  
   - 거래량/등락률 Top10 테이블 **행 클릭** 시 `onStockClick(r.stock_code, r.stock_name)` 호출.  
   - 대시보드에서 `onStockClick={(code, name) => setDetailStock({ code, name })}` 전달.

2. **InvestorFlowWidget**  
   - `onStockClick?: (stockCode, stockName?) => void` prop 추가.  
   - 수급 요약 **종목 행 클릭** 시 `onStockClick(r.stock_code)` 호출.  
   - 대시보드에서 동일하게 `setDetailStock` 연동.

3. **RecentTradesCard**  
   - `onStockClick?: (stockCode, stockName?) => void` prop 추가.  
   - 최근 거래 **행에 stock_code 있을 때만** 클릭 가능, 클릭 시 `onStockClick(code, t.stock_name)` 호출.  
   - 대시보드에서 동일하게 `setDetailStock` 연동.

4. **백엔드 recent_trades**  
   - `dashboard_router.py`: v4_trade_executions, legacy trades, v4_trades 경로 모두 응답에 **stock_code** 필드 추가.  
   - 프론트 `DashboardSummary.recent_trades` 타입에 `stock_code?: string` 추가.  
   - 최근 거래 행 클릭 시 종목 코드로 모달 오픈 가능.

5. **대시보드 페이지**  
   - `MarketRankingsWidget`, `InvestorFlowWidget`, `RecentTradesCard`에 `onStockClick={(code, name) => setDetailStock({ code, name })}` 전달.

이제 대시보드에서 **보유 종목 TOP5, 시장 순위, 수급 요약, 최근 거래** 네 곳 모두에서 종목 클릭 시 **StockDetailModal(차트 포함)** 이 열리도록 수정됨.

---

## 3. 차트 반영 전체 페이지 현황

| 페이지 | StockDetailModal | StockChart | 동작 여부 |
|--------|------------------|------------|----------|
| /dashboard | 있음 (보유·시장순위·수급·최근거래 클릭) | 모달 내 일봉/분봉 탭 | 수정 반영 완료 |
| /go100 | 없음 | — | GO100 전용 대시에는 종목 모달 없음 (현행 유지) |
| /portfolio | 있음 (보유 종목 테이블 클릭) | 모달 내 | 기존 동작 |
| /strategy-cards | 없음 | — | 차트 진입 경로 없음 |
| /go100/strategies/[id] | 없음 | — | 차트 진입 경로 없음 |
| /backtest | 있음 (매매 내역 종목 코드 클릭) | 모달 내 | 기존 동작 |
| /stock/[code] | 있음 (전용 페이지) | 모달 내 | 기존 동작 |

---

## 4. 차트 API

- **엔드포인트:** `/api/v4/chart/*` (backend `v4_chart.router`, prefix `/api/v4`).  
  - 일봉: `GET /api/v4/chart/daily/{stock_code}`, 분봉·지표·투자자·오버레이·전략시그널 등 구현됨.
- **프론트:** `frontend/src/lib/api/chart.ts`에서 `apiClient`(baseURL 8002)로 호출.  
  - `StockDetailModal`에서 `getChartDaily`, `getChartMinute`, `getChartIndicators`, `getChartPositionsOverlay`, `getChartStrategySignals`, `getChartInvestor` 사용.
- **직접 호출 테스트:** 로그인 API 실패(계정/서버 환경)로 인해 본 작업에서는 생략. 서버에서 `curl` + 유효 JWT로 `/api/v4/chart/daily/005930` 호출 시 `stock_code`, `data`, `count` 형식 응답 확인 권장.

---

## 5. 빌드/배포

- **npm build:** 컴파일·타입·린트 성공.  
  - 최종 단계에서 `.next/server/pages/_app.js.nft.json` 관련 ENOENT 발생(Next trace 이슈, 코드 변경과 무관).
- **서비스:** 지시서에 따라 **kis-v41-* 재시작 금지**.  
  - 배포 시: `systemctl restart go100-frontend` 만 수행.

---

## 6. 대표님 확인 필요

- **브라우저 동작 확인 요청**  
  - `/dashboard` 접속 후  
    1) 보유 종목 TOP5 종목명 클릭,  
    2) 시장 순위(거래량/등락률) 행 클릭,  
    3) 수급 요약 종목 행 클릭,  
    4) 최근 거래 내역 종목 행 클릭  
  - 위 네 곳 모두에서 **StockDetailModal(일봉/분봉 차트)** 가 정상 열리는지 확인 부탁드립니다.
- **브라우저 콘솔(F12)**  
  - 모달이 안 열리거나 차트가 비어 있으면 콘솔 에러 메시지 공유 부탁드립니다.

---

## 7. 수정 파일 목록 (참고)

- `frontend/src/app/(protected)/dashboard/page.tsx` — 위젯에 onStockClick 전달
- `frontend/src/components/dashboard/MarketRankingsWidget.tsx` — onStockClick + 행 클릭
- `frontend/src/components/dashboard/InvestorFlowWidget.tsx` — onStockClick + 행 클릭
- `frontend/src/components/dashboard/RecentTradesCard.tsx` — onStockClick + stock_code 반영, 행 클릭
- `frontend/src/types/index.ts` — recent_trades에 stock_code?
- `backend/app/api/v1/dashboard_router.py` — recent_trades 응답에 stock_code 추가 (v4/legacy/v4_trades 모두)
