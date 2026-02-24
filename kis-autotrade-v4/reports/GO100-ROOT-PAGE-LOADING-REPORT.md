# GO100 루트 페이지 "로딩 중..." 정지 현상 점검 보고서

**일자**: 2026-02-24  
**현상**: `go100.newtalk.kr` 접속 시 "GO100 (고백)" 제목 아래 "로딩 중..."만 계속 표시되고 본문으로 넘어가지 않음.

---

## 1. 현상이 발생하는 위치

| 항목 | 내용 |
|------|------|
| **URL** | `go100.newtalk.kr` (경로 `/`) |
| **화면** | "GO100 (고백)" + "로딩 중..." |
| **코드** | `frontend/src/app/page.tsx` (루트 페이지) |

---

## 2. 동작 방식 (현재 구현)

루트 페이지(`page.tsx`)는 **클라이언트에서만** 리다이렉트를 수행합니다.

```tsx
// frontend/src/app/page.tsx
useEffect(() => {
  const token = localStorage.getItem("token") ||
    document.cookie.split(";").find(c => c.trim().startsWith("token="));

  if (token) {
    router.replace("/dashboard");
  } else {
    router.replace("/auth/login");
  }
}, [router]);

return (
  <div>
    <h1>GO100 (고백)</h1>
    <p>로딩 중...</p>   // ← 이 상태에서 멈춤
  </div>
);
```

- **서버**: `/`는 미들웨어에서 public으로 통과시키며, 별도 리다이렉트 없음.
- **클라이언트**: 마운트 후 `useEffect`에서 `localStorage`/쿠키로 토큰 확인 → `router.replace("/dashboard")` 또는 `router.replace("/auth/login")` 호출.
- 리다이렉트가 일어나기 전까지는 항상 "로딩 중..."만 보입니다.

---

## 3. "계속 로딩 중"으로 보일 수 있는 원인

| 원인 | 설명 |
|------|------|
| **1) JS 미실행** | 스크립트 실패, 차단, 또는 느린 로딩으로 `useEffect`가 실행되지 않음. |
| **2) 리다이렉트 미완료** | `router.replace()` 호출 후 네비게이션이 완료되지 않거나, 목적지에서 에러/추가 로딩으로 사용자가 체감상 같은 화면에 머무름. |
| **3) 토큰 읽기 환경** | `localStorage`/`document.cookie`가 비어 있거나 예외가 나는 환경(서드파티 쿠키 차단, 시크릿/특수 브라우저, iframe 등). |
| **4) 무한/긴 리다이렉트** | `/dashboard` → 미들웨어에서 로그인 페이지로 보냄 → 다시 `/` 등으로 오는 등 루프에 가까운 동작. |
| **5) 타임아웃 없음** | 리다이렉트가 실패하거나 지연되어도 그대로 "로딩 중..."만 유지됨. |

---

## 4. 점검 권장 사항

1. **브라우저 개발자 도구**
   - **Console**: JS 에러, `useEffect` 내 에러 여부 확인.
   - **Network**: HTML/JS 리소스 4xx·5xx, 블로킹 여부 확인.
   - **Application → Cookies / Local Storage**: `token` 존재 여부, 도메인(`go100.newtalk.kr`) 일치 여부 확인.

2. **환경**
   - 시크릿/프라이버시 모드, 광고/스크립트 차단 확장 프로그램 비활성화 후 재현 여부 확인.
   - 다른 브라우저·기기에서도 동일한지 확인.

3. **배포**
   - `go100.newtalk.kr`이 서브경로(예: `/app`)에 붙어 있다면 `basePath` 등 Next 설정과 루트 접근 경로가 일치하는지 확인.

---

## 5. 개선 제안 (요약)

- **타임아웃 + 안내 문구**  
  일정 시간(예: 5~10초) 내에 리다이렉트가 되지 않으면 "로딩 중..." 대신 "페이지를 불러오지 못했습니다. 새로고침하거나 로그인 페이지로 이동해 주세요." + 로그인 링크 노출.
- **쿠키 파싱 견고화**  
  `document.cookie.split(...)` 대신 `token`만 추출하는 유틸(기존 `getTokenFromCookie` 등) 사용해 예외·엣지 케이스 방지.
- **서버 측 리다이렉트 검토**  
  `/` 접속 시 쿠키에 `token`이 있으면 서버(미들웨어 또는 루트 레이아웃)에서 `/dashboard`로, 없으면 `/auth/login`으로 리다이렉트하면 클라이언트 JS 실패 시에도 "로딩 중..." 정지를 줄일 수 있음.

---

## 6. 관련 파일

| 파일 | 역할 |
|------|------|
| `frontend/src/app/page.tsx` | 루트 페이지, "GO100 (고백)" + "로딩 중..." 렌더 및 클라이언트 리다이렉트 |
| `frontend/src/middleware.ts` | `/`는 public, 토큰 검사 없이 통과 |
| `frontend/src/app/(protected)/ProtectedLayoutClient.tsx` | `/dashboard` 등 보호 구역에서 인증 로딩 시 "로딩 중..." 표시 (다른 위치) |

이 보고서는 `go100.newtalk.kr` 루트에서 "로딩 중..."이 계속 보이는 현상을 코드 기준으로 정리한 점검 결과입니다.
