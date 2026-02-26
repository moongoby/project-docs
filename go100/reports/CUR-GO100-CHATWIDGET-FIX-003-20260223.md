# CUR-GO100-CHATWIDGET-FIX-003 보고서

**일시**: 2026-02-23 16:20 KST  
**서버**: root@211.188.51.113  
**목적**: ChatWidget FAB 근본 수정 — 인증 상태 의존 제거, 페이지 로드 시 무조건 FAB 렌더  
**코드**: /root/kis-autotrade-v4 (branch: phase-2c-command-center)  
**문서**: /root/project-docs (branch: master)  
**절대규칙**: kis-v41-* 재시작 금지, strategy_cards ALTER/DROP/DELETE 금지

---

## 1. 방침 변경 요약

| 구분 | 기존 (FIX-002 등 4회 수정) | FIX-003 |
|------|----------------------------|---------|
| FAB 노출 | useAuth/isAuthenticated·쿠키 수화·hydration·rAF 등에 의존 | **인증 체크 없이 항상 렌더** |
| 인증 확인 시점 | 레이아웃/ProtectedLayoutClient 단계에서 판단 | **FAB 클릭 시에만** 확인 → 미인증이면 로그인 유도 |
| ChatWidget 위치 | ProtectedLayoutClient 내부 (로딩/미인증/인증 3분기 모두에서 렌더 시도) | **(protected) layout.tsx에서 ProtectedLayoutClient 밖**에 배치 |

**핵심**: ChatWidget이 인증 상태와 무관하게 DOM에 마운트되도록, 레이아웃에서 **인증 조건 밖**으로 이동.

---

## 2. 원인 정리 (4회 수정 실패 배경)

- createPortal, useAuth 쿠키, hydration, rAF 2프레임 지연 등으로 FAB 미노출이 계속 보고됨.
- ProtectedLayoutClient에서 `isLoading` / `!isAuthenticated` 시에도 `<ChatWidget />`를 넣었으나, **해당 컴포넌트가 실행(마운트)되기 전에** 리다이렉트·로딩 UI로 인해 마운트 기회가 줄어들거나, 클라이언트 수화 순서에 따라 FAB이 안 그려질 수 있음.
- 인증 상태에 의존하지 않고, **페이지가 로드되면 무조건 FAB을 렌더**하는 구조로 전환 필요.

---

## 3. 수정 내용

### 3.1 (protected)/layout.tsx

- **백업**: `layout.tsx.bak.20260223_1620`
- **변경**:
  - `next/dynamic` import (이름 충돌 방지로 `nextDynamic` 별칭 사용).
  - `export const dynamic = "force-dynamic"` 유지.
  - `<ProtectedLayoutClient>{children}</ProtectedLayoutClient>` **밖**에 `<ChatWidget />` 배치.
  - ChatWidget은 `dynamic(..., { ssr: false })`로 로드.

```tsx
return (
  <>
    <ProtectedLayoutClient>{children}</ProtectedLayoutClient>
    <ChatWidget />
  </>
);
```

### 3.2 ProtectedLayoutClient.tsx

- **백업**: `ProtectedLayoutClient.tsx.bak.20260223_1620`
- **변경**:
  - ChatWidget 관련 `dynamic` import 및 `usePathname` 제거.
  - 로딩/미인증/인증 3분기 모두에서 `<ChatWidget />` 제거.
  - 레이아웃은 **로딩 UI / 리다이렉트 / 메인 콘텐츠**만 담당.

### 3.3 ChatWidget.tsx

- **백업**: `ChatWidget.tsx.bak.20260223_1620`
- **변경**:
  - **인증 훅 제거**: `useAuth` / `isAuthenticated` 미사용. FAB은 항상 표시.
  - **경로 제어**: `usePathname()` 추가, `pathname === "/llm"`이면 `return null` (전체화면 채팅과 중복 방지).
  - **FAB 클릭 시 인증 확인**: `hasToken()` 헬퍼 추가 (쿠키·localStorage만 사용, 스토어/훅 없음).  
    패널을 **열 때만** `hasToken()` 확인 → 미인증이면 `router.push("/auth/login")` 후 패널 미오픈.
  - `handleFabClick`은 훅 규칙 준수를 위해 early return 이전에 `useCallback`으로 정의.

---

## 4. 검증

| 항목 | 결과 |
|------|------|
| 빌드 | `npm run build` 성공 (Next.js 14.2.35) |
| go100-frontend | 재시작 후 active |
| go100 (백엔드) | 재시작 후 active |
| Backend health | `curl localhost:8002/health` → `{"status":"ok",...}` |
| /go100 | `curl -s -o /dev/null -w "%{http_code}" localhost:3000/go100` → 307 (리다이렉트 정상) |

---

## 5. 요약

- **ChatWidget**은 이제 **(protected) layout**에서 **ProtectedLayoutClient와 동등한 레벨**에 배치되어, 인증 여부와 관계없이 **항상 마운트**됨.
- FAB은 **mounted + portalReady** 조건만으로 렌더되며, **/llm**에서는 숨김.
- **인증은 FAB 클릭 시에만** 쿠키·localStorage로 확인하고, 미인증 시 로그인 페이지로 유도.

---

**보고서 작성**: 2026-02-23  
**코드 반영**: kis-autotrade-v4 phase-2c-command-center  
**문서 반영**: project-docs master
