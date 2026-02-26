# 차트 개발 반영 — 사용자 페이지 기획 보고서

- **문서 ID**: CHART-USER-PAGE-INTEGRATION-PLAN
- **작성일**: 2026-02-24
- **기준**: `report/CHART-DEVELOPMENT-STATUS-REPORT.md`, 사용자 페이지 구조

---

## 1. 요약

| 구분 | 내용 |
|------|------|
| **목적** | 구현된 차트(StockChart, V4 API)를 사용자 페이지 전반에 어떻게 노출·연동할지 기획 |
| **현재 반영 상태** | **대시보드 한 곳** — 보유 종목 카드에서 종목 클릭 시 `StockDetailModal` → 일봉/분봉 탭에 `StockChart` 표시 |
| **권장 방향** | 진입 경로 확대(여러 위젯/페이지에서 종목 상세·차트 진입) + 필요 시 미니 차트·전용 페이지 추가 |

---

## 2. 차트 접근 경로 (사용자 화면 URL 기준)

아래는 **차트(StockDetailModal / 종목 상세·일봉·분봉)** 에 도달하는 모든 사용자 경로를 **URL + 행동** 기준으로 정리한 표다. 구현 반영 후 기준이다.

| 순번 | URL (페이지) | 차트 진입 행동 | 비고 |
|------|----------------|----------------|------|
| 1 | `/dashboard` | 보유 종목 TOP5에서 **종목명 클릭** | HoldingsCard |
| 2 | `/dashboard` | 시장 순위(거래량/등락률 Top10)에서 **종목 행 클릭** | MarketRankingsWidget |
| 3 | `/dashboard` | 수급 요약(보유 종목)에서 **종목 코드/행 클릭** | InvestorFlowWidget |
| 4 | `/dashboard` | 최근 거래 내역에서 **종목명 클릭** | RecentTradesCard (stock_code 있음 시) |
| 5 | `/portfolio` | 보유 종목 테이블에서 **종목명 또는 코드 클릭** | HoldingsTable |
| 6 | `/go100/paper-trading/[id]` | 포지션 탭에서 **종목 행 클릭** | PositionTable |
| 7 | `/go100/paper-trading/[id]` | 거래내역 탭에서 **종목 행 클릭** | TradeTable |
| 8 | `/go100/live-trading/[id]` | (현재 해당 페이지에 포지션/거래 테이블 없음 — 추후 추가 시 동일하게 종목 행 클릭) | PositionTable/TradeTable 추가 시 연동 |
| 9 | `/backtest` | 백테스트 결과 매매 내역에서 **종목 코드 클릭** | TradeHistoryTable |
| 10 | `/stock/[code]` | **URL 직접 접근** (예: `/stock/005930`) | 종목 전용 페이지에서 차트 표시 |

- **공통**: 위 행동 시 **StockDetailModal**이 열리며, 일봉/분봉 탭에서 **StockChart**(캔들·지표·매매마커·전략시그널·수급) 확인 가능.
- **직접 URL**: `/stock/[code]`는 북마크·공유용으로, 해당 종목 차트만 전용 페이지에 표시.

---

## 3. 현재 사용자 페이지·차트 사용처 (구현 전 참고)

### 3.1 사용자 페이지 목록 (구현 전)

| 페이지(라우트) | 용도 | 차트 관련 컴포넌트 | 차트 진입 경로 |
|----------------|------|--------------------|----------------|
| `/dashboard` | 메인 대시보드 | StockDetailModal(StockChart) | **HoldingsCard** → 종목 클릭 시 모달 |
| `/portfolio` | 포트폴리오 분석 | AssetPieChart, ProfitBarChart, PerformanceChart | 없음(종목 클릭 시 차트 없음) |
| `/go100` | GO100 대시보드 | PortfolioChart(페이퍼 수익 곡선) | 없음 |
| `/go100/paper-trading`, `/go100/live-trading` | 모의/실거래 | PortfolioChart 등 | 보유 종목 클릭 시 차트 없음 |
| `/backtest` | 백테스트 | ExitReasonChart 등 | 거래/종목 클릭 시 차트 없음 |
| `/trade` | 거래 | — | — |
| `/strategy-cards` | 전략 카드 | — | — |

### 3.2 이미 반영된 흐름

```
대시보드 → 보유 종목 TOP5 (HoldingsCard) → [종목명 클릭] → StockDetailModal
  → 탭: 일봉 | 분봉 | 호가/재무/기타
  → 일봉: StockChart (캔들+거래량+MA/RSI/볼린저+매매마커+전략시그널)
  → 분봉: StockChart (분봉+거래량)
  → 수급: V4 investor
```

즉, **차트는 이미 “사용자 페이지”에 반영되어 있으나, 진입 경로가 “대시보드 보유 종목 클릭” 한 가지로 제한**되어 있음.

---

## 4. 사용자 페이지별 반영 방안

### 4.1 대시보드 (`/dashboard`)

| 방안 | 설명 | 우선순위 | 비고 |
|------|------|----------|------|
| **현행 유지** | HoldingsCard에서 종목 클릭 → StockDetailModal(차트) | — | 이미 구현됨 |
| **시장 순위 위젯에서 진입** | MarketRankingsWidget 종목 행 클릭 시 동일 StockDetailModal 오픈 | **높음** | 순위 테이블만 있고 차트 진입 없음 |
| **수급 위젯에서 진입** | InvestorFlowWidget에서 종목 클릭 시 StockDetailModal 오픈 | **높음** | 수급 보고 → 해당 종목 차트로 자연스러움 |
| **최근 거래에서 진입** | RecentTradesCard 거래 행의 종목 클릭 시 StockDetailModal 오픈 | **중** | “방금 거래한 종목” 차트 확인 |
| **미니 차트 위젯** | 보유 종목 또는 관심 종목 1~3개에 대해 작은 스파크라인(미니 캔들/라인) 표시 | 낮음 | Phase 2 이후 고려 |

**구현 포인트**

- 대시보드 페이지에 이미 `detailStock` / `setDetailStock` / `StockDetailModal` 있음.
- **MarketRankingsWidget**, **InvestorFlowWidget**, **RecentTradesCard**에 `onStockClick?(code, name)` prop 추가 후, 대시보드에서 `setDetailStock({ code, name })` 전달하면 동일 모달로 차트 진입 가능.
- 위젯 내부는 “종목명/코드 클릭 시 onStockClick 호출”만 추가하면 됨.

---

### 4.2 포트폴리오 (`/portfolio`)

| 방안 | 설명 | 우선순위 | 비고 |
|------|------|----------|------|
| **보유 종목 테이블에서 진입** | HoldingsTable 행 클릭(또는 종목명 클릭) 시 StockDetailModal 오픈 | **높음** | 포트폴리오 분석 후 해당 종목 차트 확인 |
| **공통 모달 재사용** | StockDetailModal을 포트폴리오 페이지에서도 사용(상태로 열 종목 관리) | **높음** | 대시보드와 동일 패턴 |

**구현 포인트**

- `portfolio/page.tsx`에 `useState<{ code: string; name?: string } \| null>(null)` 및 `StockDetailModal` 추가.
- `HoldingsTable`에 `onStockClick?: (code: string, name?: string) => void` prop 추가 후, 종목명/코드 클릭 시 호출.

---

### 4.3 GO100 (`/go100`, 페이퍼/라이브 트레이딩)

| 방안 | 설명 | 우선순위 | 비고 |
|------|------|----------|------|
| **페이퍼·라이브 보유 종목에서 진입** | 포트폴리오 상세(보유 종목)에서 종목 클릭 시 StockDetailModal 오픈 | **중** | GO100 레이아웃에 모달 하나 두고 재사용 |
| **PortfolioChart 유지** | 자산 곡선·수익률 차트는 기존 그대로 유지 | — | 이미 반영됨 |

**구현 포인트**

- GO100 레이아웃 또는 paper-trading/[id], live-trading/[id] 페이지에 `StockDetailModal` + `detailStock` 상태 추가.
- 보유 종목을 그리는 컴포넌트에 `onStockClick` 전달 후, 클릭 시 해당 종목으로 모달 오픈.

---

### 4.4 백테스트 (`/backtest`)

| 방안 | 설명 | 우선순위 | 비고 |
|------|------|----------|------|
| **거래/종목 클릭 시 차트** | 결과 상세의 거래 이력(TradeHistoryTable) 또는 종목명 클릭 시 StockDetailModal 오픈 | **중** | “이 종목에서 언제 매매했는지” 캔들+매매 마커로 확인 |
| **기존 ExitReasonChart 등 유지** | 청산 사유 등 기존 차트는 유지 | — | — |

**구현 포인트**

- 백테스트 결과 페이지에 `StockDetailModal` + `detailStock` 상태 추가.
- `TradeHistoryTable` 등에 `onStockClick?(code, name)` prop 추가 후, 종목 클릭 시 모달 오픈.

---

### 4.5 거래 페이지 (`/trade`)

| 방안 | 설명 | 우선순위 | 비고 |
|------|------|----------|------|
| **주문 전/후 차트 확인** | 주문 대상 종목에 대해 “차트 보기” 버튼 또는 종목명 클릭 시 StockDetailModal 오픈 | 낮음 | 주문 UX 보강용, 필요 시 도입 |

---

### 4.6 종목 전용 페이지 (선택)

| 방안 | 설명 | 우선순위 | 비고 |
|------|------|----------|------|
| **`/stock/[code]` 전용 페이지** | URL로 종목 차트 직접 접근, 공유/북마크 가능 | 낮음 | 모달만으로 충분하면 생략 가능 |
| **모달과 병행** | 목록/위젯에서는 모달, 직접 URL 접근 시 전용 페이지 | 낮음 | 나중 단계에서 검토 |

---

## 5. 진입 경로 정리(권장 순서)

1. **Phase A — 대시보드 진입 확대 (즉시)**  
   - MarketRankingsWidget, InvestorFlowWidget, RecentTradesCard에 종목 클릭 → `StockDetailModal`(동일 차트) 연동.

2. **Phase B — 포트폴리오**  
   - HoldingsTable 종목 클릭 → StockDetailModal (포트폴리오 페이지에 모달+상태 추가).

3. **Phase C — GO100 / 백테스트**  
   - GO100 보유 종목, 백테스트 거래 이력에서 종목 클릭 → StockDetailModal.

4. **Phase D — 선택**  
   - 미니 차트 위젯, `/stock/[code]` 전용 페이지, 거래 페이지 “차트 보기”.

---

## 6. UI/UX 권장 사항

- **일관된 진입**: “종목명/코드 클릭 = 종목 상세(차트 포함) 모달”로 통일하면 학습 비용이 적음.
- **모달 재사용**: `StockDetailModal`은 이미 일봉/분봉·지표·매매마커·시그널·수급을 지원하므로, 새 페이지마다 동일 모달만 열어주면 됨.
- **성능**: 모달은 `open && stockCode`일 때만 V4 차트 API 호출하므로, 클릭 전에는 부하 없음.
- **모바일**: 모달이 전체 화면에 가깝게 보이도록 반응형 유지(기존 StockDetailModal 구조 활용).

---

## 7. 체크리스트 (반영 완료)

- [x] `MarketRankingsWidget`: 종목 행 클릭 시 `onStockClick?.(stock_code, stock_name)` 호출.
- [x] `InvestorFlowWidget`: 종목 행 클릭 시 `onStockClick?.(code, name)` 호출.
- [x] `RecentTradesCard`: 거래 행 종목 클릭 시 `onStockClick?.(stock_code, stock_name)` 호출 (stock_code 있음 시).
- [x] `dashboard/page.tsx`: 위 세 위젯에 `onStockClick` 전달.
- [x] `HoldingsTable`: 종목명/코드 클릭 시 `onStockClick` 호출.
- [x] `portfolio/page.tsx`: StockDetailModal + detailStock 상태 추가.
- [x] GO100 PositionTable/TradeTable: onStockClick 추가, 페이퍼/라이브 상세 페이지에 StockDetailModal 추가.
- [x] `TradeHistoryTable`: 종목 코드 클릭 시 onStockClick 호출.
- [x] `backtest/page.tsx`: StockDetailModal + detailStock 상태 추가.
- [x] `/stock/[code]` 전용 페이지 추가.

---

## 8. 참고 파일

- 차트 현황: `report/CHART-DEVELOPMENT-STATUS-REPORT.md`
- 차트 컴포넌트: `frontend/src/components/market/StockChart.tsx`, `StockDetailModal.tsx`
- V4 차트 API 클라이언트: `frontend/src/lib/api/chart.ts`
- 대시보드: `frontend/src/app/(protected)/dashboard/page.tsx`
- 위젯: `MarketRankingsWidget.tsx`, `InvestorFlowWidget.tsx`, `RecentTradesCard.tsx`
- 포트폴리오: `frontend/src/app/(protected)/portfolio/page.tsx`, `HoldingsTable.tsx`
