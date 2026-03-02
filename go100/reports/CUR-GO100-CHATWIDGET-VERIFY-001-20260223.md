# CUR-GO100-CHATWIDGET-VERIFY-001 보고서

**일시**: 2026-02-23 (월) 15:25 KST  
**서버**: root@[SERVER-IP] (SSH)  
**목적**: 토큰 발급 성공 확인 후 인증·JS 청크 분석 → ChatWidget FAB 원인 특정 및 수정  
**선행**: E2E-VERIFY-001 (토큰 발급 성공, HTML에 chat-widget 0건, JS 청크 빌드 존재)

---

## STEP 1. 토큰 발급 + 인증 후 HTML/JS 분석

| 항목 | 결과 |
|------|------|
| 토큰 발급 | 성공 (`POST /api/v1/auth/login` → `access_token` 수신) |
| 프론트 인증 방식 | 미들웨어: `request.cookies.get("token")` · auth-store: `localStorage` + `document.cookie` (로그인 시 동기화) |
| 쿠키명 | **`token`** (미들웨어·auth-store 일치) |
| 쿠키 `token`으로 `/dashboard` | **HTTP 200** |
| 쿠키 `access_token` / `session` / `next-auth.session-token` | HTTP 307 (리다이렉트) |
| 인증 후 HTML | ChatWidget 문자열 0건 (정상: 클라이언트 동적 렌더) |
| JS 참조 수 | 25개 (layout·dashboard·공용 청크 등 포함) |
| Bearer 헤더만 사용 시 | 200 가능하나, 미들웨어는 쿠키·Authorization 둘 다 지원 |

**결론**: 인증은 쿠키 `token` 기준으로 200 정상. HTML에 ChatWidget 미포함은 기대 동작(SSR 없음, dynamic `ssr: false`).

---

## STEP 2. layout JS 청크 내 ChatWidget 코드 확인

| 항목 | 결과 |
|------|------|
| (protected) layout 청크 | `app/(protected)/layout-f7159a8126be50d0.js` |
| layout 청크 내 ChatWidget 관련 | **1건** — `dynamic(..., 77044).then(e=>({default:e.ChatWidget})), { ssr: false }` |
| 7044 청크 | `7044-c2f01c78813332b9.js` (webpack id 77044 ↔ 파일 7044) |
| 7044 청크 내 FAB | **1건** — `data-testid="chat-widget-fab"`, `bottom-6 right-6 z-[9999]` 등 |
| `/dashboard` HTML에 7044 직접 참조 | **0건** — 7044는 layout 실행 후 **동적 import**로 로드됨 |

**결론**: ChatWidget 코드는 layout → 7044 청크 체인에 존재하며, 빌드·매니페스트 정상. FAB은 클라이언트에서 7044 로드 및 ChatWidget 마운트 후에만 표시됨.

---

## STEP 3. 소스 검수 (ProtectedLayoutClient, ChatWidget, layout)

- **layout.tsx**: `force-dynamic`, `ProtectedLayoutClient` 래핑만 수행.
- **ProtectedLayoutClient.tsx**: `useAuth(true)` 사용, `isLoading`/`!isAuthenticated` 시에도 `{!isLlmPage && <ChatWidget />}` 렌더.  
  ChatWidget은 **dynamic import**, `ssr: false`.
- **ChatWidget.tsx**: `mounted` 전 또는 `document` 없으면 `return null`, 이후 `createPortal(fab, document.body)` 등으로 FAB·패널 렌더.
- **useAuth**: `isAuthenticated = token ?? localStorage.getItem("token")` — **쿠키는 참조하지 않음**.

**결론**: 인증 판단이 **Zustand + localStorage**만 사용하고, **쿠키는 사용하지 않음**. 미들웨어는 쿠키로 통과시키므로, 쿠키만 있고 localStorage가 비어 있는 경우(새 탭/새로고침 직후 등) 클라이언트에서 `isAuthenticated === false` → 로그인 페이지로 replace → (protected) 레이아웃이 유지되지 않아 **ChatWidget(7044) 로드 기회 상실** 가능성 있음.

---

## STEP 4. 원인 특정 + 수정

### 원인 (특정)

- **D) 인증 불일치**: 미들웨어는 **쿠키 `token`**으로 200을 주지만, 클라이언트 **useAuth**는 **Zustand·localStorage**만 보고 쿠키를 보지 않음.
- 그 결과, 쿠키만 있고 store/localStorage가 비어 있는 경우 `isAuthenticated === false` → `router.replace("/auth/login")` → protected 레이아웃이 내려가며 **7044 청크 로드 전에 이탈** → FAB 미노출로 이어질 수 있음.

### 수정 내용

- **파일**: `frontend/src/lib/hooks/useAuth.ts`
- **변경**: 미들웨어와 동기화하기 위해 **쿠키의 `token`**도 인증 소스로 사용.
  - `getTokenFromCookie()` 추가: `document.cookie`에서 `token=...` 파싱.
  - `hasToken` 및 `isAuthenticated` 계산 시 `getTokenFromCookie()` fallback 추가.
- **백업**: `useAuth.ts.bak` (동일 디렉터리).
- **빌드**: `npm run build` 성공.
- **재시작**: `go100-frontend`, `go100` 만 재시작 (kis-v41-* 재시작 없음).

### 검증 (curl 시뮬레이션)

- 토큰 발급 후 `cookie: token=<access_token>` 로 `/dashboard` 요청 → **HTTP 200**.
- 응답 HTML에 `app/(protected)/layout-...js` 청크 **1건** 포함 확인.
- 7044 청크는 HTML에 직접 없음(동적 로드로 정상).

---

## STEP 5. 브라우저 검증 권장

- 브라우저에서 로그인 → `/dashboard` 이동 후 **우하단 FAB(백억이 채팅)** 노출 여부 확인.
- 새로고침 후에도 쿠키만으로 인증 유지되는지, FAB이 계속 노출되는지 확인 권장.

---

## STEP 6. 커밋·push 가이드

**코드 저장소 (go100 / kis-autotrade-v4)**  
- 브랜치: `phase-2c-command-center`  
- 변경: `frontend/src/lib/hooks/useAuth.ts` (쿠키 기반 token 인정)

```bash
cd /root/kis-autotrade-v4
git add frontend/src/lib/hooks/useAuth.ts
git status
git commit -m 'fix: CUR-GO100-CHATWIDGET-VERIFY-001 - useAuth 쿠키 token 인정, ChatWidget FAB 노출 안정화 (20260223_1525)'
git push
```

**문서 저장소 (project-docs)**  
- 브랜치: `master`  
- 추가: `go100/reports/CUR-GO100-CHATWIDGET-VERIFY-001-20260223.md`

```bash
cd /root/project-docs
git add go100/reports/CUR-GO100-CHATWIDGET-VERIFY-001-20260223.md
git status
git commit -m 'docs: CUR-GO100-CHATWIDGET-VERIFY-001 ChatWidget FAB 최종 진단 (20260223_1525)'
git push
```

---

## 동기화 체크리스트

- [x] STEP 1 토큰 발급 + 인증 HTML 확인
- [x] STEP 2 JS 청크 내 ChatWidget 존재 확인
- [x] STEP 3 소스 검수 (ProtectedLayoutClient, ChatWidget, layout)
- [x] STEP 4 원인 특정 + 수정 + 빌드 + 재시작(go100-frontend, go100) + 검증
- [x] 보고서 작성 → project-docs 커밋·push 대기
- [ ] 코드 변경 시 go100 repo 커밋·push (위 명령 실행)

---

**Git 경로**  
- 코드: https://github.com/moongoby/go100 (phase-2c-command-center)  
- 문서: https://github.com/moongoby/project-docs (master)
