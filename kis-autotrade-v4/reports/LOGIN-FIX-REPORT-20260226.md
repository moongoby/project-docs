# 로그인 불가 현상 확인·조치 보고

**일시**: 2026-02-26  
**대상**: trading41.newtalk.kr/admin/login.html 접속 시 로그인 불가

---

## 1. 원인 분석

| 항목 | 내용 |
|------|------|
| **증상** | `trading41.newtalk.kr/admin/login.html` 접속 시 로그인 폼이 아닌 **랜딩 페이지**만 노출됨 |
| **원인** | 앱의 실제 로그인 경로는 `/auth/login`인데, 사용자가 접속한 경로는 `/admin/login.html`로 서로 불일치 |
| **추가** | 로그인 응답의 `user`에 `username`이 없을 경우 스토어/대시보드에서 표시명이 비어 있을 수 있음 |

---

## 2. 적용한 조치

### 2-1. 미들웨어 리다이렉트 (frontend/src/middleware.ts)

- **경로**: `/admin/login`, `/admin/login.html`
- **동작**: 위 경로 접속 시 즉시 **`/auth/login?from=/admin`** 으로 302 리다이렉트
- **효과**: `trading41.newtalk.kr/admin/login.html` 접속 시 실제 로그인 페이지(`/auth/login`)로 자동 이동

### 2-2. 로그인 후 사용자 객체 정규화 (frontend/src/app/auth/login/page.tsx)

- **내용**: 로그인 API 응답 `user`에 `username`이 없을 수 있으므로, `nickname` 또는 `email`을 사용해 `username`을 채워 `User` 타입과 맞춤
- **효과**: 로그인 직후 대시보드/사이드바 등에서 표시명이 정상 노출

---

## 3. 확인 방법

1. 브라우저에서 **https://trading41.newtalk.kr/admin/login.html** 접속
2. **자동으로** `https://trading41.newtalk.kr/auth/login?from=/admin` 로 이동하는지 확인
3. 이메일·비밀번호 입력 후 로그인 → 대시보드 진입 및 상단 표시명 확인

---

## 4. 참고

- 실제 로그인 URL: **https://trading41.newtalk.kr/auth/login** (또는 동일 도메인의 `/auth/login`)
- 관리자 계정이 없다면 `scripts/ensure_admin_user.py`를 운영 DB 기준으로 실행 후 동일 계정으로 로그인 테스트 (자세한 내용은 `report/ADMIN-LOGIN-ACCESS-REPORT-20260224.md` 참고)
