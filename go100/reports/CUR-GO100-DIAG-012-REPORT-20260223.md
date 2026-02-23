# CUR-GO100-DIAG-012 진단 보고서

**일시**: 2026-02-23 22:50 KST (실행: 13:51 KST)  
**목적**: 브라우저에 ChatWidget(FAB)이 안 보이는 근본 원인 특정  
**서버**: root@211.188.51.113  
**수정**: 없음(진단만 수행)

---

## 1. 요약

| 구분 | 결과 |
|------|------|
| 프론트엔드 프로세스 | ✅ 정상 (go100-frontend, next start -p 3000) |
| 빌드 산출물 | ✅ BUILD_ID 일치, layout 청크에 ChatWidget 참조 존재 |
| **layout 청크 내 `chat-widget-fab`** | ❌ **0건** (문자열은 별도 청크 7044-*.js 등에만 존재) |
| 인증(진단용) | ❌ 테스트 계정 401로 토큰 미획득 → C5~C9 미수행 |
| next.config | ✅ next.config.mjs 사용 (스크립트는 .js/.mjs/.ts 순으로 cat 시 D3에서 .js 없음으로 중단) |

---

## 2. 프로세스 실체 (A)

- **systemd**: `WorkingDirectory=/root/kis-autotrade-v4/frontend`, `ExecStart=/usr/bin/npx next start -p 3000`
- **상태**: active (running), Next.js 14.2.35, Ready
- **프로세스 CWD BUILD_ID**: `aQVyue1S2vMvH1hP4xe_X` (디스크 .next와 동일)
- **포트 3000**: next-server (pid=2494555) 리스닝

---

## 3. 빌드 산출물 (B) — 핵심

- **BUILD_ID**: `aQVyue1S2vMvH1hP4xe_X`
- **layout 청크**:
  - `app/(protected)/layout-f7159a8126be50d0.js` (33,806 bytes): **ChatWidget: 1**, **chat-widget-fab: 0**, createPortal: 0
  - `app/(protected)/go100/layout-*.js` (1,027 bytes): ChatWidget / chat-widget-fab / createPortal 모두 0
- **`chat-widget-fab` 포함 파일**:
  - `.next/static/chunks/7044-c2f01c78813332b9.js` (클라이언트 청크)
  - `.next/cache/webpack/...`, `.next/server/chunks/3117.js`

**해석**:  
(protected) layout은 **ChatWidget**을 참조하지만, 실제 FAB 마크업(`data-testid="chat-widget-fab"`)과 **createPortal** 호출은 **ChatWidget 컴포넌트 청크(7044-*.js)** 에만 있음. 즉, FAB은 **클라이언트에서 동적 로드된 뒤** 마운트되는 구조.

---

## 4. HTTP 응답 (C)

- **C1** `/` → HTTP 200, 9,442 bytes
- **C2** `/dashboard` (no auth) → HTTP 200, 11,772 bytes (HTML 정상)
- **C3** 로그인 API: `/api/v1/auth/login` → **401** (나머지 404)
- **C4** 테스트 계정(`moongoby@naver.com` / `test1234`) → **401** "이메일 또는 비밀번호가 올바르습니다."
- **C5~C9** 인증 후 대시보드/청크/전략카드 검사는 **토큰 미획득으로 미수행**

인증 실패는 진단 스크립트의 테스트 계정 정보 한계이며, **ChatWidget 미노출과 직접적인 인과는 아님**.

---

## 5. Next.js 실행 모드 (D)

- **D1** scripts: `start` → `next start` (프로덕션 모드)
- **D2** systemd: `npx next start -p 3000`, NODE_ENV=production
- **D3** 설정 파일: **next.config.mjs** 만 존재 (next.config.js 없음).  
  - 스크립트가 `cat next.config.js` 부터 실행해 **D3에서 종료** (set -e).  
  - 실제 사용 설정: next.config.mjs (API rewrites 등 정상)

---

## 6. 근본 원인 분석 (ChatWidget 미노출)

코드 기준 동작:

1. **ProtectedLayoutClient.tsx**  
   - `pathname === "/llm"` 일 때만 ChatWidget 미렌더. **/dashboard** 에서는 **항상** `<ChatWidget />` 렌더.
2. **ChatWidget**  
   - `dynamic(..., { ssr: false })` → **클라이언트 전용** 로드.
3. FAB은 **createPortal**로 `document.body`에 렌더되며, `data-testid="chat-widget-fab"` 사용.

따라서 **가능한 원인**:

| 우선순위 | 원인 | 확인 방법 |
|----------|------|-----------|
| 1 | **청크 7044-*.js 미로드/로드 실패** | 브라우저 Network에서 `7044-*.js` 요청 여부·상태코드 확인 |
| 2 | **클라이언트 JS 오류**로 ChatWidget 마운트 중단 | 브라우저 Console 오류 확인 |
| 3 | **useAuth(true)** 에서 isLoading 장시간 true 또는 인증 분기로 레이아웃이 로딩/비인증 UI에 머무름 | 동일 경로에서 인증된 사용자로 접속 시 FAB 노출 여부 확인 |
| 4 | **CSS/오버레이**로 FAB 가림 | 개발자 도구로 `[data-testid="chat-widget-fab"]` 존재 여부 및 z-index·visibility 확인 |

**정리**:  
서버·빌드·HTML 배달은 정상. FAB은 **클라이언트에서 동적 청크(7044) 로드 후** 마운트되므로, **브라우저에서 해당 청크 로드 여부·콘솔 오류·인증 상태·DOM/CSS** 를 확인하는 것이 다음 단계입니다.

---

## 7. 스크립트 이슈 (재실행 시 참고)

- **D3**: `next.config.js` 가 없어 `cat` 이 실패하며 **set -e** 로 스크립트 종료.  
  → `next.config.mjs` 만 있는 환경에서는 `cat next.config.mjs` 사용하거나, `cat next.config.js 2>/dev/null || true` 등으로 실패 시 스킵 처리 권장.
- **E** (project-docs 저장/푸시): 디렉터리 없음/권한/네트워크 시 스크립트 중단 방지를 위해 조건 처리 또는 `|| true` 권장.

---

## 8. 권장 후속 조치

1. **브라우저에서** (인증된 계정으로 `/dashboard` 접속):
   - Network: `7044-*.js` (및 `layout-f7159a8126be50d0.js`) 요청·상태코드 확인.
   - Console: 에러 유무 확인.
   - Elements: `[data-testid="chat-widget-fab"]` 존재 여부 및 스타일 확인.
2. **원인에 따라**:
   - 청크 미로드/404 → 빌드·경로·캐시 점검.
   - JS 오류 → 스택 트레이스 기준 ChatWidget/useAuth/동적 import 쪽 수정.
   - 인증/로딩 분기 → ProtectedLayoutClient 분기·타이밍 검토.
3. **수정**은 원인 확정 후 별도 HOTFIX에서 진행 (본 진단은 수정 없음).

---

**진단 로그 전체**: `/tmp/go100-diag-012.txt`  
**스크립트**: `/root/go100-diag-012.sh`
