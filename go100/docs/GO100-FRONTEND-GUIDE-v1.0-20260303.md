# GO100 프론트엔드 개발 가이드 v1.0

| 항목 | 내용 |
|------|------|
| **최종 업데이트** | 2026-03-03 |
| **도메인** | go100.newtalk.kr |
| **기술 스택** | Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui |
| **백엔드** | FastAPI port 8002 (`go100` 서비스) |
| **코드 경로** | `/root/kis-autotrade-v4/frontend/` |

---

## 1. 전체 구조

```
frontend/src/
  app/                          ← Next.js App Router
    (protected)/                ← 인증 필요 경로 그룹
      layout.tsx                ← 인증 체크 + ChatWidget FAB
      ProtectedLayoutClient.tsx ← 레이아웃 실체 (hooks 최상단 필수!)
      dashboard/page.tsx        ← /dashboard (공용 메인 홈)
      portfolio/page.tsx        ← /portfolio
      accounts/page.tsx         ← /accounts (운영자)
      trade/page.tsx            ← /trade (운영자)
      backtest/page.tsx         ← /backtest (운영자)
      llm/page.tsx              ← /llm (백억이 AI 대화)
      monitoring/page.tsx       ← /monitoring (운영자)
      notifications/page.tsx    ← /notifications
      reports/page.tsx          ← /reports (운영자)
      settings/page.tsx         ← /settings
      strategy-cards/page.tsx   ← /strategy-cards (운영자)
      admin/page.tsx            ← /admin (ADMIN only)
      go100/                    ← GO100 전용 영역
        layout.tsx              ← Go100Layout 래핑
        page.tsx                ← /go100 → redirect /dashboard
        dashboard/page.tsx      ← /go100/dashboard
        chat/page.tsx           ← /go100/chat → redirect /llm
        portfolio/page.tsx      ← /go100/portfolio → redirect /go100/dashboard
        strategies/page.tsx     ← /go100/strategies
        strategies/[id]/page.tsx
        store/page.tsx          ← /go100/store
        paper-trading/page.tsx  ← /go100/paper-trading
        paper-trading/[id]/page.tsx
        live-trading/page.tsx   ← /go100/live-trading
        live-trading/[id]/page.tsx
        notifications/page.tsx  ← /go100/notifications
        settings/page.tsx       ← /go100/settings
    auth/
      login/page.tsx
      signup/page.tsx
      forgot-password/page.tsx
    page.tsx                    ← 루트: 로그인 여부 확인 후 /dashboard로
  go100/                        ← GO100 전용 컴포넌트/API
    api/
      go100Api.ts               ← GO100 CRUD API (/api/go100/*)
      dashboardApi.ts           ← GO100 대시보드 API
      index.ts
    components/
      Go100Layout.tsx           ← GO100 전용 레이아웃 (Go100Sidebar 포함)
      Go100Sidebar.tsx          ← GO100 사이드바
      DashboardContent.tsx      ← /go100 메인 대시보드 컴포넌트
      dashboard/                ← /go100/dashboard 컴포넌트들
        OverviewCard, PerformanceChart, GoalProgressBar,
        PositionTable, StrategyCards, RegimeTimeline, ActivityFeed
    hooks/
      useDashboard.ts
      useChatHistoryStore.ts
      useStrategies.ts
    pages/
      DashboardPage.tsx         ← /go100/dashboard 실체
    types/
      strategy.ts, backtest.ts, paper-trading.ts,
      live-trading.ts, portfolio.ts, risk.ts, ai.ts
  components/
    layout/
      Sidebar.tsx               ← V4.1 사이드바 (공용+운영자 조건부)
      BottomNav.tsx             ← 모바일 하단 네비
      Header.tsx                ← 모바일 헤더
    dashboard/                  ← /dashboard 전용 위젯들
      BaekogiWelcomeBanner, MetricCards, AccountsCard,
      HoldingsCard, RecentTradesCard, MarketRankingsWidget,
      InvestorFlowWidget, SyncStatusWidget, ThemesSectorsWidget,
      ActiveStrategiesCard, SystemStatusCard, LLMUsageCard
  lib/
    api/                        ← V4.1 API 클라이언트
      client.ts                 ← axios 기반 (baseURL: go100.newtalk.kr)
      dashboard.ts              ← /api/v1/dashboard/*
      accounts.ts, portfolio.ts, trade.ts, llm.ts,
      notifications.ts, reports.ts, settings.ts, monitoring.ts
    store/
      auth-store.ts             ← Zustand (user, token, tier, role)
    hooks/
      useAuth.ts                ← 인증 훅 (hydrateFromClient 호출)
```

---

## 2. 레이아웃 구조 (핵심!)

### 2.1 경로별 레이아웃

```
/dashboard, /portfolio, /accounts 등 V4.1 경로
  └── ProtectedLayoutClient
        ├── Sidebar (데스크톱)
        ├── Header (모바일)
        ├── main > {children}
        └── BottomNav (모바일)

/go100/* 경로
  └── ProtectedLayoutClient → pathname 체크 → children만 반환
        └── Go100Layout (자체 shell)
              ├── Go100Sidebar (데스크톱)
              ├── MobileMenuButton + 드로어 (모바일)
              └── main > {children}
```

### 2.2 ProtectedLayoutClient 주의사항 ⚠️

**React Hooks 규칙**: hooks는 반드시 컴포넌트 최상단에 위치해야 함.
`usePathname()`, `useAuth()`, `useQuery()` 등 모든 hooks는 조건문 이전에 선언.

```tsx
// ✅ 올바른 구조
export default function ProtectedLayoutClient() {
  const { isAuthenticated, isLoading } = useAuth(true);  // 최상단
  const pathname = usePathname();                         // 최상단
  const { data } = useQuery({ ... });                     // 최상단

  if (isLoading) return <Loading />;
  if (!isAuthenticated) return <Unauthenticated />;
  if (pathname?.startsWith("/go100")) return <>{children}</>;
  return <V4Layout>{children}</V4Layout>;
}

// ❌ 잘못된 구조 (hooks 규칙 위반)
export default function ProtectedLayoutClient() {
  const { isAuthenticated, isLoading } = useAuth(true);
  if (isLoading) return <Loading />;
  if (!isAuthenticated) return <Unauthenticated />;
  const pathname = usePathname();  // ← 조건문 이후 선언 금지!
}
```

---

## 3. 경로 구조 (Path Consolidation v1.0)

### 3.1 공용 경로 (모든 사용자)

| URL | 파일 | 내용 |
|-----|------|------|
| `/dashboard` | `dashboard/page.tsx` | 메인 홈. 실시간 시세·계좌·시장·수급 위젯 |
| `/go100/dashboard` | `go100/dashboard/page.tsx` | GO100 성과. 성과차트·목표·포지션·레짐 |
| `/portfolio` | `portfolio/page.tsx` | V4 전체 자산 분석 |
| `/go100/strategies` | `go100/strategies/page.tsx` | 전략 카드 생성·관리 |
| `/go100/strategies/[id]` | `go100/strategies/[id]/page.tsx` | 전략 상세·백테스트·자동매매 |
| `/go100/store` | `go100/store/page.tsx` | 전략 마켓플레이스 |
| `/go100/paper-trading` | `go100/paper-trading/page.tsx` | 모의거래 목록 |
| `/go100/paper-trading/[id]` | `go100/paper-trading/[id]/page.tsx` | 모의거래 상세 |
| `/go100/live-trading` | `go100/live-trading/page.tsx` | 실거래 목록 |
| `/go100/live-trading/[id]` | `go100/live-trading/[id]/page.tsx` | 실거래 상세 |
| `/llm` | `llm/page.tsx` | 백억이 AI 대화 (채널·세션·전략생성) |
| `/notifications` | `notifications/page.tsx` | V4 알림 |
| `/go100/notifications` | `go100/notifications/page.tsx` | GO100 알림 |
| `/settings` | `settings/page.tsx` | 공통 설정 |
| `/go100/settings` | `go100/settings/page.tsx` | GO100 리스크·면책 설정 |
| `/reports` | `reports/page.tsx` | 성과 리포트 |

### 3.2 운영자 전용 경로 (PREMIUM tier / ADMIN role)

| URL | 내용 |
|-----|------|
| `/accounts` | 계좌 관리 |
| `/trade` | V4.1 자동매매 스케줄 |
| `/backtest`, `/backtest/analysis` | V4.1 백테스트 |
| `/strategy-cards` | V4.1 전략카드 카탈로그 |
| `/monitoring`, `/monitoring/data-collection` | 시스템 모니터링 |
| `/admin`, `/admin/backtest/*` | 어드민 |

### 3.3 리다이렉트 경로

| 경로 | 리다이렉트 | 이유 |
|------|----------|------|
| `/go100` | `/dashboard` | 운영자 화면이 더 풍부 |
| `/go100/chat` | `/llm` | 채널·세션 기능 통합 |
| `/go100/portfolio` | `/go100/dashboard` | 기능 중복 |

---

## 4. 사이드바 메뉴 구조

### 4.1 데스크톱 Sidebar (V4.1 경로에만 표시)

```
공용 메뉴 (navCommon)           운영자 메뉴 (navAdmin, showAdmin만)
  ├── /dashboard                   ├── /accounts
  ├── /go100/dashboard             ├── /trade
  ├── /portfolio                   ├── /backtest
  ├── /go100/strategies            ├── /backtest/analysis
  ├── /go100/store                 ├── /strategy-cards
  ├── /go100/paper-trading         ├── /monitoring
  ├── /go100/live-trading          └── /reports
  ├── /llm
  ├── /notifications
  └── /settings
```

`showAdmin` 조건: `role === "ADMIN" || role === "SUPER_ADMIN" || tier === "PREMIUM"`

### 4.2 Go100Sidebar (GO100 경로에만 표시)

```
  ├── /dashboard          (대시보드)
  ├── /go100/dashboard    (GO100 성과)
  ├── /go100/strategies   (내 전략)
  ├── /go100/store        (마켓플레이스)
  ├── /go100/paper-trading(모의거래)
  ├── /go100/live-trading (실거래)
  ├── /llm                (AI 대화)
  ├── /go100/notifications(알림)
  └── /go100/settings     (설정)
```

### 4.3 모바일 BottomNav (mainTabs + 더보기 시트)

```
mainTabs:  /dashboard | /llm | /notifications | 더보기

더보기 시트:
  GO100: /go100/strategies, /go100/store, /go100/paper-trading, /go100/live-trading
  공통:  /portfolio, /settings
  운영자: /accounts, /backtest, /monitoring, /reports, /admin (showAdmin만)
```

---

## 5. API 연결 구조

### 5.1 GO100 API (`src/go100/api/`)

**Base URL**: `NEXT_PUBLIC_GO100_API_URL/api/go100` 또는 `/api/go100`

```
go100Api.ts:
  전략카드: GET/POST/PATCH/DELETE /strategy-cards/*
  백테스트: POST/GET /backtest/*
  포트폴리오: GET /portfolio (paper/live 포함)
  AI 채팅: POST /ai/chat
  스토어: GET/POST /store/*
  알림: GET/POST /notification/*
  리스크: GET/PATCH /risk/*
  기타: /me, /disclaimer, /trade/*

dashboardApi.ts:
  GET /api/go100/dashboard/overview
  GET /api/go100/dashboard/performance
  GET /api/go100/dashboard/positions
  GET /api/go100/dashboard/strategies
  GET /api/go100/dashboard/regime-history
  GET /api/go100/dashboard/goal-progress
  GET /api/go100/dashboard/activity-log
```

### 5.2 V4.1 API (`src/lib/api/`)

**Base URL**: `NEXT_PUBLIC_API_URL` (= go100.newtalk.kr → port 8002)

```
dashboard.ts:  GET /api/v1/dashboard/summary
accounts.ts:   GET/POST/PATCH/DELETE /api/v1/accounts/*
portfolio.ts:  GET /api/v1/portfolio/*
trade.ts:      GET/POST/PATCH/DELETE /api/v1/trade/*
llm.ts:        POST /api/v1/llm/chat, /api/go100/ai/chat
notifications: GET/POST /api/v1/notifications/*
monitoring.ts: GET /api/v4/monitoring/*
backtest.ts:   GET/POST /api/v4/backtest/*
```

---

## 6. 인증 구조

### 6.1 auth-store (Zustand)

```typescript
// 저장 필드
user: User | null       // { user_id, username, email, tier, role }
token: string | null
refreshToken: string | null
isAuthenticated: boolean

// localStorage에 저장되는 키
"token"          → JWT access token
"refresh_token"  → refresh token
"go100_tier"     → user.tier (예: "PREMIUM")
"go100_role"     → user.role (예: "ADMIN")

// 주요 메서드
login(user, token, refreshToken)  → localStorage + 스토어 갱신
logout()                          → localStorage 전체 삭제
hydrateFromClient()               → 새로고침 시 localStorage → 스토어 복원
```

### 6.2 역할 판단

```typescript
function isAdminUser(user): boolean {
  const r = (user.role ?? "").toUpperCase();
  return r === "ADMIN" || r === "SUPER_ADMIN" || user.tier === "PREMIUM";
}
```

`PREMIUM` tier는 운영자와 동일한 메뉴 접근 권한.

---

## 7. 컴포넌트 수정 규칙

### 7.1 새 페이지 추가 시

1. `app/(protected)/[경로]/page.tsx` 생성
2. **공용 페이지**: `Sidebar.tsx`의 `navCommon`에 추가
3. **GO100 전용**: `Go100Sidebar.tsx`의 `navItems`에 추가
4. **운영자 전용**: `Sidebar.tsx`의 `navAdmin`에 추가 (showAdmin 조건부)
5. `BottomNav.tsx` 더보기 시트에도 추가

### 7.2 GO100 경로에서 레이아웃 수정

- `/go100/*` 경로는 `Go100Layout`이 shell 담당
- `ProtectedLayoutClient`의 `/go100` 조건 절대 건드리지 않기
- Go100Sidebar 링크 변경 시 반드시 리다이렉트 경로 확인

### 7.3 API 추가 시

- GO100 전용 → `src/go100/api/go100Api.ts` 또는 `dashboardApi.ts`
- V4.1 공용 → `src/lib/api/` 해당 파일

### 7.4 절대 금지

```
❌ hooks를 조건문/반복문 안에서 사용
❌ ProtectedLayoutClient에서 hooks를 early return 이후에 선언
❌ 같은 아이콘을 다른 이름으로 두 번 import (TrendingUp as X)
❌ 리다이렉트 경로를 사이드바 링크로 사용
```

---

## 8. 빌드 및 배포

```bash
# 빌드
cd /root/kis-autotrade-v4/frontend
npm run build

# 빌드 에러 시
rm -rf .next && npm run build

# 배포
systemctl restart go100-frontend

# 상태 확인
systemctl is-active go100-frontend
curl -s -o /dev/null -w "%{http_code}" https://go100.newtalk.kr/
```

---

## 9. 주요 수정 이력

| 날짜 | 커밋 | 내용 |
|------|------|------|
| 2026-03-03 | 2a831b8b | 종목명(코드) 표기 통일, stock_universe JOIN |
| 2026-03-03 | 8554e14b | **경로 통합** — 관리자/사용자 분리, 이중 사이드바 제거 |
| 2026-03-03 | 1841546f | Hooks 규칙 위반 수정, Go100Sidebar 링크 업데이트, BottomNav GO100 메뉴 추가 |

---

## 10. 주요 파일 체크리스트 (수정 전 반드시 확인)

수정 가능성 높은 파일들:

| 파일 | 수정 시 영향 범위 |
|------|----------------|
| `ProtectedLayoutClient.tsx` | 모든 보호 경로의 레이아웃 |
| `Sidebar.tsx` | 데스크톱 사이드바 메뉴 |
| `BottomNav.tsx` | 모바일 하단 네비 |
| `Go100Sidebar.tsx` | GO100 전용 사이드바 |
| `auth-store.ts` | 인증 상태 전체 |
| `go100Api.ts` | GO100 API 전체 |
| `app/page.tsx` | 로그인 후 진입점 |
