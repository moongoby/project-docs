# GO100 프론트엔드 경로 통합 기획서 v1.0

| 항목 | 내용 |
|------|------|
| **문서 ID** | GO100-FRONTEND-PATH-CONSOLIDATION-v1.0 |
| **작성일** | 2026-03-03 |
| **상태** | 승인 대기 → 구현 예정 |
| **도메인** | go100.newtalk.kr |
| **기술 스택** | Next.js (App Router), FastAPI 8002 |

---

## 1. 현재 문제점

### 1.1 이중 레이아웃 중첩
`/go100/*` 접속 시 두 레이아웃이 겹쳐 표시됨:

```
ProtectedLayout (V4.1 Sidebar — 운영자 메뉴 12개)
  └── Go100Layout (GO100 Sidebar — 사용자 메뉴 10개)
       └── 실제 콘텐츠
```

→ 고객이 내부 운영자 메뉴(계좌관리, 자동매매, 모니터링 등) 전부 노출됨

### 1.2 기능 중복
| 중복 쌍 | 결정 |
|---------|------|
| `/go100` vs `/dashboard` | `/dashboard`가 더 풍부 → `/dashboard` 통합 |
| `/go100/chat` vs `/llm` | `/llm`이 더 완성도 높음 → `/llm` 통합 |
| `/go100/portfolio` vs `/portfolio` + `/go100/dashboard` | 역할 분리 후 유지 |

### 1.3 로그인 후 진입점
현재: 모든 사용자 → `/dashboard` (운영자 화면)
목표: 역할별 자동 분기

---

## 2. 기본 원칙

> **운영자 화면이 더 풍부한 페이지는 공용 사용, GO100 전용 기능만 사용자 화면으로 분리**

---

## 3. 최종 경로 구조

### 3.1 공용 경로 (운영자 + 일반 사용자 모두 접근)

| URL | 내용 | 비고 |
|-----|------|------|
| `/dashboard` | 메인 홈 — 실시간 시세·계좌·시장·수급 | 가장 기능 풍부 |
| `/go100/dashboard` | GO100 성과 — 성과차트·목표·레짐·활동로그 | GO100 전용 성과 |
| `/portfolio` | V4 자산 분석 — 전체 보유종목·수익률 | 계좌 통합 뷰 |
| `/accounts` | 계좌 관리 — 추가·잔액동기화·API 발급 | |
| `/notifications` | V4 알림 — 매매·시스템·리스크 이벤트 | 데이터 다름 |
| `/go100/notifications` | GO100 알림 — 체결·손절·시스템 | 데이터 다름 |
| `/settings` | 공통 설정 — 프로필·API키·보안·테마 | |
| `/go100/settings` | GO100 설정 — 리스크·면책·알림 | GO100 전용 설정 |
| `/reports` | 성과 리포트 — 일간/주간 생성·재발송 | |
| `/llm` | 백억이 채팅 — 채널선택·세션·전략생성 | `/go100/chat` 대체 |

### 3.2 GO100 사용자 전용 경로

| URL | 내용 |
|-----|------|
| `/go100/strategies` | 전략 카드 생성·관리 |
| `/go100/strategies/[id]` | 전략 상세·백테스트·자동매매 시작 |
| `/go100/store` | 전략 마켓플레이스 |
| `/go100/paper-trading` | 모의거래 목록 |
| `/go100/paper-trading/[id]` | 모의거래 상세 |
| `/go100/live-trading` | 실거래 목록 |
| `/go100/live-trading/[id]` | 실거래 상세 |

### 3.3 운영자 전용 경로 (PREMIUM / ADMIN만)

| URL | 내용 |
|-----|------|
| `/trade` | V4.1 자동매매 스케줄 관리 |
| `/backtest` | V4.1 백테스트 실행 |
| `/backtest/analysis` | 백테스트 분석 |
| `/strategy-cards` | V4.1 전략카드 카탈로그 |
| `/monitoring` | 시스템 실시간 모니터링 |
| `/monitoring/data-collection` | 데이터 수집 상태 |
| `/admin` | 사용자·계좌·시스템·LLM비용·로그 |
| `/admin/backtest/*` | 어드민 백테스트 상세 |

### 3.4 제거/리다이렉트 경로

| 현재 경로 | 처리 | 대체 경로 |
|----------|------|---------|
| `/go100` (메인 홈) | 리다이렉트 | `/dashboard` |
| `/go100/chat` | 리다이렉트 | `/llm` |
| `/go100/portfolio` | 리다이렉트 | `/go100/dashboard` |

---

## 4. 통합 사이드바 메뉴 구조

```
공용 메뉴 (모든 사용자에게 표시)
  ├── 대시보드              /dashboard
  ├── GO100 성과            /go100/dashboard
  ├── 포트폴리오             /portfolio
  ├── 내 전략               /go100/strategies
  ├── 마켓플레이스            /go100/store
  ├── 모의거래               /go100/paper-trading
  ├── 실거래                /go100/live-trading
  ├── 백억이 대화            /llm
  ├── 알림                  /notifications  (+ /go100/notifications)
  └── 설정                  /settings  (+ /go100/settings)

운영자 추가 메뉴 (PREMIUM / ADMIN만 표시)
  ├── 계좌관리               /accounts
  ├── 자동매매               /trade
  ├── 백테스트               /backtest
  ├── 백테스트 분석           /backtest/analysis
  ├── 전략카드(V4)            /strategy-cards
  ├── 모니터링               /monitoring
  ├── 리포트                 /reports
  └── 관리자                 /admin
```

---

## 5. 구현 작업 목록

### Step 1 — 이중 사이드바 제거 (핵심, 1시간)

**파일**: `frontend/src/app/(protected)/ProtectedLayoutClient.tsx`
- `usePathname()` 추가
- `/go100` 경로에서 V4.1 Sidebar/Header/BottomNav 렌더 안 함

### Step 2 — 사이드바 메뉴 통합 (2시간)

**파일**: `frontend/src/components/layout/Sidebar.tsx`
- 공용 메뉴에 GO100 전용 항목 추가
- 운영자 전용 메뉴는 `tier === "PREMIUM" || role === "ADMIN"` 조건부 표시

**파일**: `frontend/src/components/layout/BottomNav.tsx`
- 모바일 BottomNav도 동일하게 정리

### Step 3 — 리다이렉트 처리 (30분)

- `/go100` → `/dashboard` 리다이렉트
- `/go100/chat` → `/llm` 리다이렉트
- `/go100/portfolio` → `/go100/dashboard` 리다이렉트

### Step 4 — 로그인 후 진입점 분기 (1시간)

**파일**: `frontend/src/lib/store/auth-store.ts`
- `login()` 시 `localStorage.setItem("go100_tier", user.tier ?? "")` 추가
- `hydrateFromClient()` 시 tier 복원

**파일**: `frontend/src/app/page.tsx`
- tier/role 기반 리다이렉트 분기
  - PREMIUM / ADMIN → `/dashboard`
  - 일반 사용자 → `/dashboard` (메뉴만 다르게 표시)

### Step 5 — 빌드 및 배포 (30분)

```bash
cd /root/kis-autotrade-v4/frontend
npm run build
systemctl restart go100-frontend
```

**총 예상 시간: 약 4~5시간**

---

## 6. 영향 범위

| 항목 | 영향 |
|------|------|
| 기존 URL 접근 | `/go100`, `/go100/chat`, `/go100/portfolio` 리다이렉트 |
| API 연결 | 변경 없음 |
| 백엔드 | 변경 없음 |
| 기존 기능 | 변경 없음 (레이아웃만 조정) |
| 모바일 | BottomNav 메뉴 조정 필요 |

---

## 7. 주의사항

1. `kis-v41-*`, `kis-v41-frontend` 서비스 재시작 금지
2. `go100_` 접두사 파일/테이블만 수정
3. Next.js 빌드 실패 시 `rm -rf .next && npm run build`
4. 빌드 후 반드시 `systemctl restart go100-frontend`

---

## 8. 버전 이력

| 버전 | 일자 | 내용 |
|------|------|------|
| v1.0 | 2026-03-03 | 최초 작성. 공용/사용자전용/운영자전용 경로 분류, 이중 사이드바 해결방안, 통합 메뉴 구조 |
