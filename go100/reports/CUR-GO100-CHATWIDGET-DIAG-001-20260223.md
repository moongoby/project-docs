# CUR-GO100-CHATWIDGET-DIAG-001 — ChatWidget FAB 미노출 진단 보고서

## 기본 정보
- 작업일: 2026-02-23 17:10 KST
- 서버: root@211.188.51.113
- 목적: ChatWidget FAB가 5회 수정 후에도 미노출되는 근본 원인 진단
- 작업 유형: 진단 전용 (코드 수정 없음)

## 진단 결과

### 1. 빌드 산출물 (.next/static/chunks)
- **ChatWidget 문자열 포함 청크:** `9376-d04bd66a54ca4385.js` 1개 존재.
- **FAB 관련 CSS 클래스:** 동일 청크 내에 chat/fab/fixed/bottom 등 문자열 포함 (minified).
- **layout 서버 파일에서 ChatWidget 참조:** (protected) 레이아웃은 RSC; dynamic import된 ChatWidget은 서버 청크에 직접 문자열로 없고, 클라이언트에서 `9376-*.js` 청크로 로드됨.

### 2. 소스 코드 현재 상태
- **layout.tsx에서 ChatWidget 배치 위치:** `(protected)/layout.tsx`에서 `next/dynamic`으로 `@/go100/components/ChatWidget` 로드(ssr: false), `ProtectedLayoutClient` 다음에 `<ChatWidget />` 렌더.
- **ChatWidget.tsx 렌더 조건:**  
  - `pathname === "/llm"` → `return null`.  
  - `!mounted || !portalReady || typeof document === "undefined"` → `return null`.  
  - FAB은 `fixed bottom-6 right-6 z-[9999]`, `createPortal(fab, document.body)`로 body에 포탈.
- **ProtectedLayoutClient에서 ChatWidget 참조 여부:** 없음 (FIX-003에서 layout으로 이전됨).

### 3. HTML 응답 분석
- **/dashboard HTML에서 chat 관련 요소:** 비인증 시 29 bytes 응답(리다이렉트/최소 HTML). 로그인 API(localhost:8002) 토큰 획득 실패로 인증 HTML 미확보.
- **HTML 크기:** 29 bytes (비인증 기준).
- **chat 언급 횟수:** 0.

### 4. Dynamic Import 청크
- **ChatWidget 전용 청크 존재 여부:** 있음. `9376-d04bd66a54ca4385.js`에 `portalReady`, `handleFabClick`, `data-testid="chat-widget-fab"` 등 포함.
- **BUILD_ID:** `zzvOjINi7lWCJHAZuxog2` (빌드 시각 2026-02-23 16:29).

### 5. CSS 숨김 가능성
- **hidden/invisible/opacity-0:** ChatWidget.tsx에는 해당 클래스 없음. `overflow-hidden`만 사용(패널용).
- **globals.css chat 스타일:** 없음.
- **tailwind content 경로:** `./src/pages/**`, `./src/components/**`, `./src/app/**` 만 포함. **`./src/go100/**` 미포함.**

### 6. 인프라
- **go100-frontend 상태:** active (running), next start -p 3000, 16:30:07 기동.
- **nginx 프록시:** go100_backend 127.0.0.1:8002, go100_frontend 127.0.0.1:3000, server_name go100.newtalk.kr.

---

## 근본 원인 판단

**Tailwind `content`에 `./src/go100/**`가 없어, ChatWidget이 사용하는 유틸리티 클래스가 purge 대상이 됨.**

- ChatWidget 경로: `src/go100/components/ChatWidget.tsx`.
- `tailwind.config.ts`의 `content`에는 `./src/pages/**`, `./src/components/**`, `./src/app/**`만 있어 **`go100` 디렉터리가 스캔되지 않음.**
- 그 결과 FAB에 쓰인 `fixed`, `bottom-6`, `right-6`, `z-[9999]`, `flex`, `h-14`, `w-14`, `rounded-full`, `bg-blue-600` 등이 빌드 시 제거될 수 있음.
- 클래스가 제거되면 FAB 노드는 존재하나 위치·크기·색이 적용되지 않아 화면 밖에 있거나, 크기 0이거나, 다른 요소에 가려져 “미노출”로 보일 수 있음.

동적 청크는 정상 존재하고, layout 배치·렌더 조건·인프라도 정상이므로, **스타일 purge가 FAB 미노출의 근본 원인으로 판단됨.**

---

## 수정 제안

(코드 수정은 이 보고서 확인 후 별도 지시서로 진행)

- **최소 변경:** `frontend/tailwind.config.ts`의 `content` 배열에 `./src/go100/**/*.{js,ts,jsx,tsx,mdx}` 추가.
- 추가 후 `npm run build` 재실행 및 go100-frontend 재시작(또는 배포 절차에 따라 반영)하여 FAB 노출 여부 확인.

---

## GitHub URL
- 보고서: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-CHATWIDGET-DIAG-001-20260223.md
