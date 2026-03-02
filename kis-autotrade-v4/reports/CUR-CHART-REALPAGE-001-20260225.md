# CUR-CHART-REALPAGE-001 — 실사용 페이지 차트 반영 보고서

> 작성일시: 2026-02-25 KST
> 커밋: `9d1c995e` (feat/CUR-GO100-DATA-ENGINE-INTEGRATION)
> 서버: [SERVER-IP] | 프론트엔드 포트: 3000

---

## 1. 배경

이전 차트 작업(커밋 `4cee5e72`)이 미사용 `/go100/*` 페이지에 반영되어 실제 사용자가 접근하는 메인 사이드바 페이지(`/dashboard`, `/portfolio`, `/strategy-cards`)에는 차트가 없는 상태였음.

### 문제 요약

| 구분 | 이전 작업 대상 (미사용) | 실사용 페이지 |
|------|----------------------|-------------|
| 대시보드 | `/go100` (DashboardContent.tsx) | **`/dashboard`** (dashboard/page.tsx) |
| 포트폴리오 | `/go100/portfolio` (PortfolioChart) | **`/portfolio`** (CSS 커스텀 차트) |
| 전략 상세 | `/go100/strategies/[id]` | **`/strategy-cards`** (StrategyDetailModal) |

### 실사용 페이지 차트 현황 (작업 전)

- `/dashboard` — 차트 없음 (KPI 메트릭, 위젯 카드만)
- `/portfolio` — CSS conic-gradient 파이, CSS div 바, 텍스트 리스트 (라이브러리 미사용)
- `/strategy-cards` — StrategyDetailModal에 숫자 지표만 (차트 없음)

---

## 2. 구현 내용

### [P1] /dashboard — PortfolioTrendChart 신규 추가

**파일**: `frontend/src/components/dashboard/PortfolioTrendChart.tsx` (신규)
**삽입 위치**: 핵심 지표 4칸 아래, 내 계좌 섹션 위

- recharts `AreaChart`로 자산 추이 시각화 (최근 30일)
- API: `GET /api/v1/portfolio/performance?account_id={id}&period=30d`
- X축: 날짜 (MM-DD), Y축: 금액 (만/억 단위 자동 포맷)
- 파란색 그라데이션 채우기 + 툴팁 (원화 포맷)
- 데이터 2개 미만이면 컴포넌트 자체 비표시
- `useQuery` 60초 자동 갱신

### [P2] /portfolio — CSS 차트 → recharts 전환 (3개 컴포넌트)

#### AssetPieChart (자산 비중)
**파일**: `frontend/src/components/portfolio/AssetPieChart.tsx`

- CSS `conic-gradient` 원형 → recharts `PieChart` 도넛형 전환
- `innerRadius=50, outerRadius=80, paddingAngle=2`
- 하단 Legend 자동 표시
- 빈 데이터 시 "보유 종목이 없습니다" 표시 유지

#### ProfitBarChart (종목별 수익률)
**파일**: `frontend/src/components/portfolio/ProfitBarChart.tsx`

- CSS `div` 가로 바 → recharts `BarChart` (layout=vertical) 전환
- 수익 = 초록(#22c55e), 손실 = 빨강(#ef4444) Cell 색상
- `ReferenceLine x=0` 기준선 추가
- 종목명 Y축 라벨 (72px), 수익률 X축 (%포맷)

#### DailyPnLCard (일별 손익)
**파일**: `frontend/src/components/portfolio/DailyPnLCard.tsx`

- 텍스트 리스트 → recharts `BarChart` (수직) 전환
- 최근 7일, 날짜순 정렬
- 양수 = 초록, 음수 = 빨강 Cell 색상
- `ReferenceLine y=0` 기준선
- Y축 만원 단위 자동 포맷

### [P3] /strategy-cards — StrategyDetailModal 차트 추가

**파일**: `frontend/src/go100/components/StrategyDetailModal.tsx`

- 핵심 지표 2×2 그리드 아래에 차트 블록 삽입
- **Equity Curve** (AreaChart): `lastRun.equity_curve` 데이터 파싱
  - `[{date, equity}]` 형식 → amber 그라데이션 AreaChart
  - 날짜 X축 + 원화 Y축 + 툴팁
- **승/패 분포** (PieChart): `profit_trades` / `loss_trades` 데이터
  - 초록(수익) / 빨강(손실) 도넛 차트
  - 중앙에 총 매매 횟수 + 승률 표시
- 데이터 없으면 차트 블록 자체 비표시 (조건부 렌더링)

---

## 3. 변경 파일 목록

| # | 파일 | 변경 | 줄수 |
|---|------|------|------|
| 1 | `frontend/src/components/dashboard/PortfolioTrendChart.tsx` | **신규** | +97 |
| 2 | `frontend/src/app/(protected)/dashboard/page.tsx` | 수정 | +4 |
| 3 | `frontend/src/components/portfolio/AssetPieChart.tsx` | 전면 재작성 | +73 -83 |
| 4 | `frontend/src/components/portfolio/ProfitBarChart.tsx` | 전면 재작성 | +76 -75 |
| 5 | `frontend/src/components/portfolio/DailyPnLCard.tsx` | 전면 재작성 | +74 -57 |
| 6 | `frontend/src/go100/components/StrategyDetailModal.tsx` | 차트 블록 추가 | +68 |
| **합계** | | | **+320 -130** |

---

## 4. 차트 라이브러리 현황 (실사용 페이지 기준)

| 페이지 | 차트 | 라이브러리 | 비고 |
|--------|------|-----------|------|
| `/dashboard` | PortfolioTrendChart (AreaChart) | recharts | 신규 |
| `/portfolio` | AssetPieChart (PieChart) | recharts | CSS→recharts 전환 |
| `/portfolio` | ProfitBarChart (BarChart) | recharts | CSS→recharts 전환 |
| `/portfolio` | DailyPnLCard (BarChart) | recharts | 텍스트→recharts 전환 |
| `/strategy-cards` | Equity Curve (AreaChart) | recharts | 모달 내 신규 |
| `/strategy-cards` | 승/패 PieChart | recharts | 모달 내 신규 |
| `/backtest/analysis` | 4종 (Line, Bar, Radar, Timeline) | recharts | 기존 유지 |
| StockDetailModal | 캔들스틱 (일봉/분봉) | lightweight-charts | 기존 유지 |

---

## 5. 검증

- [x] `npx next build` — 성공
- [x] `systemctl restart go100-frontend` — active
- [x] Git 커밋: `9d1c995e`
- [x] Git 푸시: `feat/CUR-GO100-DATA-ENGINE-INTEGRATION`
- [x] project-docs 커밋 + 푸시

---

## 6. 미반영 사항 (P4 이하)

| 항목 | 이유 | 필요한 작업 |
|------|------|-----------|
| `/dashboard` 자산추이 — 계좌 미연결 시 | performance API가 account_id 필요 | 계좌 없는 사용자용 fallback UI |
| `/backtest` Equity Curve recharts 전환 | 이미 recharts AreaChart 적용됨 (커밋 4cee5e72) | 확인 완료 |
| 누적수익률 KOSPI 벤치마크 | 벤치마크 데이터 미연동 | KOSPI 지수 수집 + 비교 로직 |
