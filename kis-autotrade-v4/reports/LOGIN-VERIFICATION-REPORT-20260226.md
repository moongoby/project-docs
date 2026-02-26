# 로그인 직접 확인 결과 보고

**일시**: 2026-02-26  
**방법**: 브라우저로 trading41.newtalk.kr 실제 접속 후 URL·화면 확인

---

## 1. 직접 확인 결과

| 확인 항목 | 결과 |
|-----------|------|
| **https://trading41.newtalk.kr/admin/login.html** | 랜딩 페이지만 노출됨. 로그인 폼 없음. **리다이렉트 없음.** |
| **상단/본문 "로그인" 링크 클릭** | `login.html`(상대경로) → 같은 `/admin/login.html` 페이지로만 이동. 로그인 폼 없음. |
| **https://trading41.newtalk.kr/auth/login** | **동일한 랜딩 페이지만 노출됨.** 로그인 폼 없음. |

**결론**: trading41.newtalk.kr 에서는 **어떤 경로로 접속해도 로그인 폼(Next.js 로그인 페이지)이 나오지 않음.**

---

## 2. 원인 분석

- **trading41.newtalk.kr** 은 현재 **정적 랜딩 페이지만** 서빙하고 있음.
- **Next.js 앱(실제 로그인 페이지)은 이 도메인에 배포되어 있지 않음.**  
  → 따라서 이번에 반영한 **Next.js 미들웨어 리다이렉트는 trading41에서는 실행되지 않음.**
- 배포 스크립트·헬스체크는 **go100.newtalk.kr** 기준으로만 동작하는 것으로 확인됨.

---

## 3. 필요한 조치 (운영 측)

trading41에서 로그인까지 연결하려면 **서버(리버스 프록시) 설정** 이 필요함.

### 방법 A: 리다이렉트 설정 (권장)

trading41을 서빙하는 **nginx(또는 리버스 프록시)** 에서 아래 경로를 **실제 로그인 서비스(예: go100.newtalk.kr)** 로 리다이렉트.

```nginx
# trading41.newtalk.kr 서버 블록 내부에 추가
location = /admin/login.html { return 302 https://go100.newtalk.kr/auth/login?from=%2Fadmin; }
location = /admin/login      { return 302 https://go100.newtalk.kr/auth/login?from=%2Fadmin; }
location = /auth/login       { return 302 https://go100.newtalk.kr/auth/login; }
```

- 적용 후: `trading41.newtalk.kr/admin/login.html` 접속 시 → `go100.newtalk.kr/auth/login` 으로 이동하여 로그인 가능.

### 방법 B: 정적 랜딩의 링크 수정

랜딩 페이지 소스(다른 저장소/빌드 결과일 수 있음)에서  
**로그인** 링크를 `login.html` → **`https://go100.newtalk.kr/auth/login`** 로 변경.

- 그러면 사용자가 "로그인" 클릭 시 바로 실제 로그인 페이지로 이동.

### 방법 C: trading41에 Next.js 앱 배포

trading41 도메인에도 이 리포지토리의 Next.js 앱을 배포하고,  
`/admin/login`, `/admin/login.html`, `/auth/login` 등이 **Next.js로** 오도록 프록시 설정.  
(이 경우 이미 반영한 미들웨어 리다이렉트가 동작함.)

---

## 4. 코드베이스 측에서 이미 반영된 내용

- **frontend/src/middleware.ts**  
  `/admin/login`, `/admin/login.html` 접속 시 `/auth/login?from=/admin` 으로 리다이렉트하도록 설정됨.  
  → **Next.js 앱이 해당 요청을 처리할 때만** 적용됨.
- **frontend/src/app/auth/login/page.tsx**  
  로그인 직후 사용자 표시명(username) 보강 처리됨.

위 변경은 **go100.newtalk.kr** 또는 Next.js가 서빙되는 다른 도메인에서는 유효함.  
**trading41에는 Next 앱이 없으므로, 반영했다고 해도 trading41 화면이 “안 바뀐” 상태로 보이는 것이 맞음.**

---

## 5. 요약

| 항목 | 내용 |
|------|------|
| **직접 확인** | trading41.newtalk.kr/admin/login.html, /auth/login 모두 랜딩만 표시, 로그인 폼 없음. |
| **이유** | trading41은 정적 랜딩만 서빙, Next.js 미들웨어가 실행되지 않음. |
| **조치** | trading41 서버에서 **nginx 등으로 /admin/login.html, /auth/login → go100.newtalk.kr/auth/login 리다이렉트** 적용 필요. (또는 랜딩의 로그인 링크를 go100 로 변경.) |

위 서버/링크 조치가 적용된 뒤 다시 접속하면 로그인까지 정상 동작하는지 확인할 수 있음.
