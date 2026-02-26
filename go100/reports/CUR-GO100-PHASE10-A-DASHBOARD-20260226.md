# CUR-GO100-PHASE10-A-DASHBOARD (2026-02-26)

## 목표

통합 성과 대시보드 — 한 화면에서 자산, 수익률, 목표, 전략, 레짐을 모두 확인.

## 구현 내용

### 백엔드 (API)

- **파일**: `backend/app/routers/go100/dashboard_router.py`
- **prefix**: `/api/go100/dashboard`
- **엔드포인트 7개**:
  1. `GET /overview` — 종합 현황 (총 자산, 수익률, MDD, 목표 달성률, 레짐, 페이퍼/실매매 상태)
  2. `GET /performance?period=1m|3m|6m|1y|all` — 일별 수익률 시계열 + KOSPI 대비
  3. `GET /positions` — 현재 보유 종목 (페이퍼), 종목별 손익·비중
  4. `GET /strategies` — 전략 카드별 성과 (백테스트 CAGR, 승률, MDD)
  5. `GET /regime-history?days=90` — 레짐 변화 타임라인
  6. `GET /goal-progress` — 목표 대비 진행률, 시뮬레이션 궤적
  7. `GET /activity-log?limit=50` — 최근 활동 (주문 등)

- **사용 모듈**: `data_queries`, `paper_trading`, `portfolio_manager`, `regime_engine`, `goal_engine` 조합
- **신규 쿼리**: `data_queries.get_dashboard_paper_account_id()` 추가
- **main.py**: `go100_dashboard_router` 등록

### 프론트엔드

- **라우트**: `/go100/dashboard` (`app/(protected)/go100/dashboard/page.tsx`)
- **페이지**: `go100/pages/DashboardPage.tsx` — 7개 API 병렬 호출 후 2열 그리드 레이아웃
- **API 클라이언트**: `go100/api/dashboardApi.ts` — 7개 함수 + 타입 정의
- **컴포넌트 7개** (`go100/components/dashboard/`):
  - `OverviewCard` — 총자산·수익률·MDD·레짐
  - `PerformanceChart` — recharts 라인 차트 (기간 1m/3m/6m/1y 전환)
  - `GoalProgressBar` — 목표 진행률 (Radix Progress)
  - `PositionTable` — 보유 종목 테이블
  - `StrategyCards` — 전략별 성과 카드
  - `RegimeTimeline` — 레짐 전환 타임라인
  - `ActivityFeed` — 최근 활동 피드
- **사이드바**: "성과 대시보드" 메뉴 추가 (`/go100/dashboard`)

### 검증

- 프론트엔드: `npm run build` 성공
- 라우트: `/go100/dashboard` 빌드 출력에 포함 확인

## 의존성

- recharts: 기존 `package.json`에 포함 (^3.7.0)
- 백엔드: 기존 go100 서비스 모듈만 사용

## 참고

- 백업: ` /root/backup/app-phase10-dashboard-*`, `frontend-phase10-dashboard-*`
