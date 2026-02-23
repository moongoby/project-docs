# CUR-GO100-HOTFIX-004A — ChatWidget FAB 전방위 FE 진단 보고서

**작업일:** 2026-02-23  
**목적:** ChatWidget FAB 3차 수정 후에도 브라우저 미노출 — 근본 원인 전방위 추적  
**규칙:** go100_* 파일/테이블만 수정, .env/.bak 커밋 금지

---

## 요약

| 항목 | 결과 |
|------|------|
| **빌드 내 ChatWidget 포함** | ✅ 포함됨 (chat-widget-fab, createPortal, 백억이, layout chunk 내 `et.ChatWidget` 확인) |
| **소스 import 체인** | ✅ 정상 (layout → ChatWidget → api/types/ChatMessage) |
| **클린 빌드** | ❌ 실패 — React Client Manifest/Prerender 오류 다수, Export 단계에서 다수 경로 실패 |
| **Nginx** | ✅ go100.newtalk.kr → 3000 프록시 정상 |
| **서버 HTML 응답 (진단 7)** | ⚠️ `/dashboard` 비인증 시 307 → `/auth/login` 리다이렉트만 반환(29 bytes) — 로그인 후 실제 HTML/JS 로드 필요 |

**결론:** FAB 미노출의 **코드/번들 원인은 아님**. 빌드 산출물에 ChatWidget이 포함되어 있고, layout에서 `!isLlmPage && <ChatWidget />` 로 정상 참조됨. **빌드 실패(prerender 오류)**와 **런타임 환경(인증/캐시/JS 로드 순서)** 쪽 추가 확인 권장.

---

## 진단 1: 빌드 결과 — ChatWidget 포함 여부

- **chat-widget-fab:**  
  `frontend/.next/static/chunks/9376-*.js`, `frontend/.next/server/chunks/1871.js`, webpack cache 등에서 검색됨.
- **ChatWidget:**  
  `frontend/.next/server/app/(protected)/**/page_client-reference-manifest.js` 다수, layout 관련 청크에서 참조됨.
- **createPortal:**  
  `frontend/.next/static/chunks/app/(protected)/layout-*.js`, `6671-*.js`, `fd9d1056-*.js`, `main-*.js` 등.
- **백억이:**  
  `frontend/.next/static/chunks/app/(protected)/go100/chat/page-*.js`, `layout-*.js`, `llm/page-*.js` 등.

→ **ChatWidget/ FAB 관련 문자열이 빌드 산출물에 포함되어 있음.**

---

## 진단 2: layout.tsx 빌드 결과

- **ChatWidget 포함 JS:**  
  `frontend/.next/static/chunks/app/(protected)/layout-9b545e54aa610421.js` (클린 빌드 후 `layout-9b545e54aa610421.js`).
- **isLlmPage:**  
  동일 layout 청크 내 `c="/llm"===(0,r.usePathname())`, `!c&&(0,n.jsx)(et.ChatWidget,{})` 형태로 minify되어 있음.  
  즉, pathname이 `/llm`이 아닐 때만 `ChatWidget` 렌더.
- **동적 import:**  
  layout에서 `et` = 모듈 ID 77044 (ChatWidget 등 go100 클라이언트 컴포넌트) 로 로드됨.

→ **layout 빌드 결과에 ChatWidget 조건부 렌더링이 반영되어 있음.**

---

## 진단 3: 소스 import 체인

| 단계 | 경로/내용 |
|------|-----------|
| layout.tsx | `import { ChatWidget } from "@/go100/components/ChatWidget"`, `pathname === "/llm"` → `!isLlmPage && <ChatWidget />` (로딩/미인증/정상 3분기 모두) |
| ChatWidget.tsx | `import { chatWithAI } from "../api"`, `import type { ChatResponse, RiskTolerance } from "../types"`, `import { ChatMessage } from "./ChatMessage"` |
| go100/api/index.ts | `export * from './go100Api'` |
| go100Api.ts | `export async function chatWithAI(req: ChatRequest): Promise<ChatResponse>` 정의됨 |
| types | `frontend/src/go100/types/index.ts` → `export * from './ai'` 등, `ai.ts`에 `ChatResponse`, `RiskTolerance` 정의 |
| ChatMessage | `frontend/src/go100/components/ChatMessage.tsx` 존재 |

→ **import 체인 및 타입/구성요소 모두 정상.**

---

## 진단 4: 클린 빌드 에러

- **실행:** `rm -rf frontend/.next && npm run build` → 로그: `/tmp/go100-build-004.log`
- **종료:** 빌드 스크립트 기준 **실패 (Export 단계에서 오류)**.  
  로그 끝: `Export encountered errors on following paths:` 후 다수 경로 나열, 정적 생성 실패.
- **에러 유형 요약:**
  - React Client Manifest 관련:  
    `Could not find the module ".../link.js#"`, `layout-router.js#`, `app-router.js#`, `client-page.js#ClientPageRoot` 등 (Next/번들러 측 경고/버그 유사).
  - Server Components render:  
    `An error occurred in the Server Components render. The specific message is omitted in production builds.`
  - Prerender 실패 경로 예:  
    `/_not-found`, `/admin`, `/dashboard`, `/(protected)/go100/chat`, `/(protected)/go100/strategies`, `/(protected)/llm`, 기타 (protected), auth, offline, privacy, terms 등.
- **ChatWidget 직접 에러:**  
  빌드 로그에서 `ChatWidget`/`chatWithAI`/`go100` 로 검색 시, prerender 실패 경로 목록에 go100/chat, go100/strategies 등이 포함되어 있으나, **ChatWidget 자체의 “Module not found”/컴파일 에러는 없음.**

→ **ChatWidget 미포치가 아니라, 전반적인 React Client Manifest/Prerender 이슈로 빌드가 실패한 상태.**  
  (Next 14 App Router + RSC 환경에서 알려진 유사 이슈와 유사.)

---

## 진단 5: 빌드 후 ChatWidget 포함 재확인

- 클린 빌드 산출물 기준:
  - **chat-widget-fab:**  
    `frontend/.next/static/chunks/9376-430c657dfe5197fa.js`, server chunks, webpack cache 등.
  - **백억이:**  
    `frontend/.next/static/chunks/app/(protected)/layout-9b545e54aa610421.js`, go100/chat, go100/page, settings, strategy-cards 등.

→ **빌드 실패 이후 생성된 .next 기준으로도 ChatWidget/ FAB 관련 코드는 번들에 포함되어 있음.**

---

## 진단 6: Nginx 설정

- **관련 설정:**  
  `go100.newtalk.kr` → `upstream go100_frontend (127.0.0.1:3000)`, `location /` → `proxy_pass http://go100_frontend`, WebSocket HMR용 `/_next/webpack-hmr` 프록시 있음.
- **API:**  
  `location /api/` → `go100_backend` (8002).

→ **Nginx 자체는 프론트 3000으로 정상 프록시됨. FAB 미노출의 직접 원인으로 보기 어렵음.**

---

## 진단 7: 서버 HTML 응답

- **요청:** `curl -s http://localhost:3000/dashboard`
- **결과:**
  - **HTTP 307 Temporary Redirect** → `location: /auth/login?from=%2Fdashboard`
  - **본문:** 리다이렉트 URL 문자열만 포함, **29 bytes** (실제 HTML/JS 없음).
- **이유:** (protected) 라우트는 비인증 시 로그인으로 리다이렉트하므로, **인증 없이 dashboard를 호출하면 HTML이 아닌 리다이렉트만 반환되는 것이 정상**임.
- **추가:** 로그인 후 동일 URL로 접근하면 전체 HTML과 `_next/static/chunks/` 스크립트가 내려와야 하며, 그 중 `app/(protected)/layout-*.js` 등에 ChatWidget이 포함됨.

→ **현재 진단 7만으로는 “HTML에 ChatWidget이 없다”고 단정할 수 없음. 로그인 세션을 붙인 뒤 HTML/JS 응답을 다시 확인하는 것이 필요.**

---

## 권장 후속 조치

1. **브라우저 측 확인 (우선)**  
   - 로그인한 상태에서 `https://go100.newtalk.kr/dashboard` 접속 후:  
     - 개발자 도구 → Network에서 `layout-*.js` 및 ChatWidget이 들어간 chunk 로드 여부 확인.  
     - Console에 “hydration”/“createPortal”/“ChatWidget” 관련 에러 여부 확인.  
   - 시크릿/다른 브라우저 또는 캐시 비우고 재접속하여 캐시 영향 여부 확인.

2. **런타임 노출 조건**  
   - `ChatWidget`은 `mounted` 후 `createPortal`로 `document.body`에 렌더되므로,  
     - `document.body`가 준비되기 전 스크립트 실행,  
     - 전역 CSS/overflow로 인한 가리기(z-index 등),  
     - 다른 요소에 가려짐  
     여부를 Elements 탭에서 확인.

3. **빌드 안정화 (별도 이슈)**  
   - React Client Manifest / Prerender 오류는 Next 14 + RSC 환경 이슈 가능성이 있음.  
   - `next.config`에서 해당 경로들 `dynamic = 'force-dynamic'` 또는 `export const dynamic = 'force-dynamic'` 적용 검토, 또는 Next/React 버전 및 의존성 정리 후 재빌드.

4. **서버 HTML 재검증**  
   - 로그인 쿠키/토큰을 붙여 `curl` 또는 E2E로 `/dashboard` HTML을 받은 뒤,  
     `ChatWidget`/`chat-widget-fab`/`백억이`/관련 chunk `src`가 포함되는지 확인.

---

## 파일/경로 참조

- Layout: `frontend/src/app/(protected)/layout.tsx`
- ChatWidget: `frontend/src/go100/components/ChatWidget.tsx`
- API: `frontend/src/go100/api/index.ts`, `go100Api.ts` (`chatWithAI`)
- Types: `frontend/src/go100/types/index.ts`, `ai.ts`
- 빌드 로그: `/tmp/go100-build-004.log`
- Nginx: `go100.newtalk.kr` (sites-enabled/conf.d 내 go100 관련 설정)

---

*CUR-GO100-HOTFIX-004A ChatWidget FAB 전방위 FE 진단 — 2026-02-23*
