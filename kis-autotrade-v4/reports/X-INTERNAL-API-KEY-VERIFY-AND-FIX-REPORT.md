# X-Internal-API-Key 확인·조치·보고

- **문서 ID**: X-INTERNAL-API-KEY-VERIFY-AND-FIX-REPORT
- **작성일**: 2026-02-24
- **관련 오류**: 사용자 화면 하단 "Invalid or missing X-Internal-API-Key", 차트·재무·수급 미로드

---

## 1. 확인 (원인)

### 1.1 현상
- 대시보드에서 종목 클릭 시 **종목 상세 모달**에서 차트·재무·체결강도·수급이 비어 있거나 "데이터 로딩 중".
- 브라우저 하단/토스트에 **"Invalid or missing X-Internal-API-Key"** 표시.

### 1.2 원인
- 백엔드 `InternalAPIKeyMiddleware`(`backend/app/core/security_middleware.py`)는 **모든 `/api/v4/*` 요청**에 대해 `X-Internal-API-Key` 헤더를 검증함.
- 프론트엔드(Next.js)는 `apiClient`로 `/api/v4/chart/*`, `/api/v1/*` 등을 호출할 때 **해당 헤더를 붙이지 않음** (보안상 브라우저에 키를 두지 않음).
- Next.js `next.config.mjs`에서 **rewrites**로 `/api/:path*` → 백엔드(apiBase)로 프록시함. 이때 **프록시 요청에 X-Internal-API-Key가 포함되지 않음**.
- 따라서 브라우저 → Next 서버 → 백엔드로 가는 `/api/v4/*` 요청이 백엔드에서 403으로 차단됨.

### 1.3 확인한 코드
| 위치 | 내용 |
|------|------|
| `backend/app/core/security_middleware.py` | `/api/v4/*` 경로에서 `X-Internal-API-Key` 검증, 불일치 시 403 + "Invalid or missing X-Internal-API-Key" |
| `frontend/src/lib/api/client.ts` | `apiClient`에 Authorization(Bearer)만 설정, X-Internal-API-Key 없음 |
| `frontend/next.config.mjs` | `rewrites`: `/api/:path*` → `apiBase/api/:path*` (헤더 추가 없음) |
| `frontend/src/middleware.ts` | 기존: `/api` 경로는 EXCLUDED_PREFIXES로 인해 인증만 스킵, **V4용 헤더 주입 없음** |

---

## 2. 조치 내용

### 2.1 Next.js 미들웨어에서 `/api/v4/*` 요청에 헤더 주입
- **파일**: `frontend/src/middleware.ts`
- **내용**: `pathname.startsWith("/api/v4/")`인 요청에 대해 `process.env.INTERNAL_API_KEY` 값을 `X-Internal-API-Key` 헤더로 설정 후 `NextResponse.next({ request: { headers } })` 반환.
- Next.js rewrite로 백엔드에 전달되는 요청에 위 헤더가 포함되어 백엔드 검증 통과.

### 2.2 403 사용자 안내 문구 보강
- **파일**: `frontend/src/lib/api/client.ts`
- **내용**: 403 응답 시 `detail`이 "Invalid or missing X-Internal-API-Key" 등이면 "서버 설정이 필요합니다. 관리자에게 문의하세요. (API 키)"로 토스트 메시지 표시.

### 2.3 환경 변수 안내
- **파일**: `.env.example`
- **내용**: `INTERNAL_API_KEY`에 “Next.js가 /api 리라이트 시 프록시 요청에 주입하므로 **프론트 배포 시에도 동일 값 설정 필요**” 주석 추가.

### 2.4 배포 측 필요 사항
- **프론트(Next.js) 배포 환경**에 백엔드와 **동일한** `INTERNAL_API_KEY` 값 설정 필요.
- 예: Vercel/Node 서버 등에서 `INTERNAL_API_KEY=...` 환경 변수 설정 후 재배포.

---

## 3. 검증 방법

### 3.1 로컬
1. 백엔드 `.env`에 `INTERNAL_API_KEY=테스트값` 설정.
2. 프론트 `.env.local`(또는 동일 방식)에 `INTERNAL_API_KEY=테스트값`, `NEXT_PUBLIC_API_URL=http://localhost:8002` 설정.
3. 백엔드·프론트 실행 후 대시보드에서 종목 클릭 → 종목 상세 모달에서 차트·재무·수급 로드 확인.
4. 브라우저 Network 탭에서 `/api/v4/chart/*` 요청이 **200**으로 응답하는지 확인.

### 3.2 운영(go100.newtalk.kr 등)
1. 해당 서버의 Next.js 실행 환경(PM2/node 등)에 `INTERNAL_API_KEY`가 백엔드와 동일하게 설정되어 있는지 확인.
2. 설정 후 Next 재시작(또는 재배포) 후, 대시보드 → 종목 클릭 → 차트·재무·수급 정상 로드 및 "Invalid or missing X-Internal-API-Key" 미표시 확인.

### 3.3 nginx만 사용하는 구축
- 기존처럼 **nginx**가 `/api/v4/`를 백엔드로 프록시하는 구성이면, nginx에서 `proxy_set_header X-Internal-API-Key $internal_api_key;` 및 `include internal-api-key.conf` 유지.
- 이번 조치는 **Next.js가 직접 백엔드로 rewrite하는 구성**을 전제로 함. nginx가 Next만 바라보고 Next가 백엔드로 프록시하는 경우, 위 미들웨어 조치로 해결.

---

## 4. 요약

| 항목 | 내용 |
|------|------|
| **원인** | Next.js rewrite로 전달되는 `/api/v4/*` 요청에 X-Internal-API-Key 미포함 → 백엔드 403 |
| **조치** | Next.js 미들웨어에서 `/api/v4/*` 요청에 `INTERNAL_API_KEY`를 헤더로 주입 |
| **배포** | 프론트 배포 환경에 `INTERNAL_API_KEY` 설정 후 재배포 필요 |
| **검증** | 종목 상세 모달에서 차트·재무·수급 로드 및 403 미발생 확인 |
