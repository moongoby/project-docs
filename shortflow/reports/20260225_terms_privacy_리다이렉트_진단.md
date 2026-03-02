# /terms·/privacy 리다이렉트 원인 진단

**일시**: 2026-02-25 KST  
**서버**: ssh root@[SERVER-IP]  
**프로젝트**: /data/shortflow  

---

## 1. 진단 요약

| 항목 | 결과 |
|------|------|
| middleware.ts 위치 | `saas-dashboard/middleware.ts` |
| /terms, /privacy 공개 허용 | ✅ `isPublic`에 포함됨 (51–52행) |
| terms/page.tsx, privacy/page.tsx | ✅ 존재 |
| next.config.js 리다이렉트 | 없음 |
| basePath | 없음 |

**결론**: 코드 상으로는 `/terms`, `/privacy`가 로그인 없이 접근 가능하도록 되어 있음. 리다이렉트가 발생한다면 **(1) 배포된 이미지가 예전 빌드**이거나 **(2) 같은 포트(3000)를 쓰는 다른 앱**이 응답하고 있을 가능성이 큼.

### 1.1 실행 환경 참고 (진단 스크립트 실행 호스트)

- **포트 3000 사용**: `newtalk-v2-frontend` (Next.js). ShortFlow saas-dashboard가 아님.
- **localhost:3000/terms, /privacy**: **307 Temporary Redirect → /login** (위 앱의 미들웨어).
- **shortflow-saas-dashboard**: 현재 컨테이너 목록에 없음 (미기동 또는 다른 호스트에서 기동).

실제 서버([SERVER-IP])에서 3000을 ShortFlow가 쓰는데 리다이렉트된다면 → 예전 빌드로 재빌드·재배포 필요.

---

## 2. 미들웨어 동작 (현재 코드)

```44:56:saas-dashboard/middleware.ts
  const pathname = request.nextUrl.pathname;
  const isPublic =
    pathname === "/" ||
    pathname.startsWith("/login") ||
    pathname.startsWith("/register") ||
    pathname.startsWith("/signup") ||
    pathname.startsWith("/terms") ||
    pathname.startsWith("/privacy");

  if (!user && !isPublic) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }
```

- `isPublic`이 true면 `!user && !isPublic`은 false → **리다이렉트하지 않음**.
- 따라서 현재 소스 기준으로는 `/terms`, `/privacy`는 로그인 페이지로 리다이렉트되지 않아야 함.

---

## 3. 리다이렉트가 날 수 있는 원인

1. **이전 빌드로 실행 중인 컨테이너**  
   - 과거에 `/terms`, `/privacy`가 `isPublic`에 없던 시점의 이미지로 실행 중이면, 그 미들웨어가 적용되어 `/login`으로 리다이렉트함.
   - **조치**: 최신 코드로 이미지 재빌드 후 컨테이너 재기동.

2. **Supabase `getUser()` 예외**  
   - `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` 미설정 등으로 `getUser()`에서 예외가 나면, 미들웨어가 에러를 반환하거나 기본 동작으로 리다이렉트가 이뤄질 수 있음 (환경에 따라 다름).
   - **조치**: 컨테이너/런타임 환경 변수 확인.

3. **캐시**  
   - CDN/프록시/브라우저에서 예전 302 응답이 캐시돼 있을 수 있음.
   - **조치**: 재배포 후 해당 URL을 캐시 무시하고 재요청해 확인.

---

## 4. 권장 조치

### 4.1 포트 확인 (같은 서버에 다른 앱이 3000 사용 시)

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
ss -tlnp | grep 3000
```

- 3000이 **newtalk-v2-frontend** 등 다른 컨테이너가 쓰고 있으면, ShortFlow saas-dashboard는 **다른 포트**(예: 3001)로 띄우고 nginx/리버스프록시에서 `shotflow.newtalk.kr`만 3001로 연결하도록 설정해야 함.
- 3000이 비어 있으면 아래 재빌드 후 `shortflow-saas-dashboard`가 3000을 사용하면 됨.

### 4.2 재빌드·재배포

```bash
cd /data/shortflow
# 사용 중인 배포 스크립트가 있으면 실행 (예: scripts/redeploy_saas_dashboard.sh)
docker compose build saas-dashboard --no-cache
docker compose up -d saas-dashboard
```

### 4.3 배포 후 검증 (서버에서)

```bash
# 302 + Location: /login 이면 여전히 리다이렉트되는 것
curl -sI http://localhost:3000/terms
curl -sI http://localhost:3000/privacy
# 200 OK 가 나와야 함
```

### 4.4 컨테이너 내부에서 미들웨어 확인 (선택)

```bash
CONTAINER=$(docker ps --format "{{.Names}}" | grep -i saas | head -1)
docker exec "$CONTAINER" cat /app/middleware.ts 2>/dev/null | head -60
# isPublic에 /terms, /privacy 가 포함돼 있는지 확인
```

---

## 5. 서버에서 한 번에 돌릴 진단 스크립트

아래 스크립트를 서버에서 실행한 뒤, 출력을 보관하면 재발 시 비교하기 좋음.

- 스크립트 경로: `scripts/diagnose_terms_privacy_redirect.sh`
- 실행: `bash /data/shortflow/scripts/diagnose_terms_privacy_redirect.sh`

(스크립트는 별도 파일로 두었음.)

---

**작성**: 2026-02-25  
**다음 확인**: 재배포 후 외부 URL(예: `https://도메인/terms`, `/privacy`)로 직접 접속해 200 응답 및 약관/개인정보처리방침 본문 노출 여부 확인.
