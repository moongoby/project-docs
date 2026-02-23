# CUR-GO100-CHATWIDGET-FIX-002 보고서

**일시**: 2026-02-23 16:00 KST  
**서버**: root@211.188.51.113  
**목적**: ChatWidget FAB 브라우저 미노출 원인 특정 및 수정  
**코드**: /root/kis-autotrade-v4 (branch: phase-2c-command-center)  
**절대규칙**: kis-v41-* 재시작 금지, strategy_cards ALTER/DROP/DELETE 금지

---

## 1. 진단 요약 (STEP 1~9)

| 항목 | 결과 |
|------|------|
| useAuth.ts | 쿠키 `getTokenFromCookie()` 사용 중, 스토어와 동기화 없음 |
| ChatWidget.tsx | `mounted` 후 `createPortal(fab, document.body)`, SSR 방지 `return null` |
| ProtectedLayoutClient | `useAuth(true)`, isLoading/!isAuthenticated 시에도 `<ChatWidget />` 렌더 |
| layout.tsx | `force-dynamic`, `ProtectedLayoutClient` 래핑 |
| middleware.ts | PROTECTED_PREFIXES에 `/go100` 없음 → 보호 경로 불일치 |
| auth-store | 새로고침 시 token null, 쿠키/로컬스토리지에서 수화 로직 없음 |
| 토큰 발급 | 성공 (TOKEN length 185), 쿠키 인증 200 가능 |

**원인 정리**

- **Case A (보강)**: 새로고침 시 Zustand 스토어가 쿠키/로컬스토리지를 읽지 않아, 일부 구간에서 `isAuthenticated`가 지연되거나 레이아웃이 로그인 화면으로 바뀌며 ChatWidget 마운트 기회가 줄어듦. 쿠키는 useAuth에서 읽지만 스토어와 동기화가 없음.
- **Case B (보강)**: `createPortal`이 마운트 직후 한 프레임에서만 실행될 때, 일부 환경에서 body 준비/페인트 타이밍으로 FAB이 누락될 수 있음.
- **미들웨어**: `/go100`이 보호 경로에 없어 미들웨어·클라이언트 인증 정책 불일치.

---

## 2. 수정 내용

### 2.1 auth-store.ts

- **백업**: `auth-store.ts.bak.20260223_1600`
- **변경**:
  - `getTokenFromCookie()` 헬퍼 추가 (미들웨어·useAuth와 동일한 `token` 쿠키 파싱).
  - `hydrateFromClient(): void` 추가: 클라이언트에서만 실행, 스토어 `token`이 비어 있을 때 `localStorage.getItem("token")` 및 `getTokenFromCookie()`로 채움 → `token`, `isAuthenticated` 동기화.

### 2.2 useAuth.ts

- **백업**: `useAuth.ts.bak.20260223_1600`
- **변경**:
  - `mounted` 후 `hydrateFromClient()` 호출하는 `useEffect` 추가.
  - 클라이언트 초기 로드 시 스토어 수화로 `isAuthenticated`가 즉시 true가 되도록 해, 로그인 화면으로의 불필요한 replace 및 ChatWidget 미마운트 가능성 감소.

### 2.3 ChatWidget.tsx

- **백업**: `ChatWidget.tsx.bak.20260223_1600`
- **변경**:
  - `portalReady` state 추가.
  - `mounted` 후 `requestAnimationFrame` 2회 지연 후 `setPortalReady(true)`.
  - FAB/패널 렌더 조건을 `mounted && portalReady && typeof document !== "undefined"`로 통일.
  - createPortal 실행을 2 rAF 지연해, body 준비 및 페인트 후 FAB이 안정적으로 노출되도록 함.

### 2.4 middleware.ts

- **변경**: `PROTECTED_PREFIXES`에 `"/go100"` 추가 → 미들웨어·클라이언트 보호 경로 일치.

---

## 3. 빌드·재시작·검증

| 단계 | 결과 |
|------|------|
| 백업 | auth-store, useAuth, ChatWidget 각 `.bak.20260223_1600` 생성 |
| `npm run build` | 성공 (Next.js 14.2.35) |
| 재시작 | `go100-frontend`, `go100` 만 재시작 (kis-v41-* 미재시작) |
| BUILD_ID | `Lgu7Xfozk6TCBSx1Joe-P` |

---

## 4. 검증 권장

- 브라우저에서 로그인 후 `/go100` 또는 `/dashboard` 이동.
- 우하단 **FAB(백억이 채팅)** 노출 여부 확인.
- 새로고침 후에도 FAB 노출 유지 확인.
- `/go100` 미인증 접근 시 로그인 페이지로 리다이렉트되는지 확인.

---

## 5. Git

- **문서**: project-docs, master — `go100/reports/CUR-GO100-CHATWIDGET-FIX-002-20260223.md` 추가 후 push.
- **코드**: kis-autotrade-v4, phase-2c-command-center — auth-store, useAuth, ChatWidget, middleware 수정 후 push.

---

## 6. 참고

- 선행: CUR-GO100-CHATWIDGET-VERIFY-001 (쿠키 인정 후에도 FAB 미노출 이슈 지속 → 본 수정).
- 규칙: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/CLAUDE.md
