# CUR-GO100-AUTH-REFRESH-v1 보고서

**작성일:** 2026-02-24
**태스크:** CUR-GO100-AUTH-REFRESH-v1
**범위:** 로그인 세션 유지 개선 — refresh token 자동 갱신 구현

---

## 1. 문제 분석

go100.newtalk.kr에서 로그인이 자주 풀리는 현상 발생.

### 근본 원인
| 항목 | 기존 상태 | 문제 |
|------|-----------|------|
| Access Token 만료 | .env `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15` | 15분마다 만료 |
| 프론트엔드 Refresh 로직 | **없음** | 401 발생 시 즉시 `/auth/login`으로 리다이렉트 |
| 소셜 로그인 | access_token만 발급 | refresh_token 미발급, DB 세션 미저장 |
| 쿠키 max-age | 86400초 (1일) | 쿠키는 남아있으나 JWT 자체는 15분에 만료 |

백엔드에는 이미 `/api/v1/auth/refresh` 엔드포인트와 refresh token rotation 로직이 구현되어 있었으나, 프론트엔드에서 이를 사용하지 않았음.

---

## 2. 수정 내용

### 2.1 프론트엔드 (4파일)

#### `frontend/src/lib/api/auth.ts`
- `login()` 반환 타입에 `refresh_token`, `expires_in` 추가
- `refreshToken(refresh_token)` API 함수 신규 추가 → `POST /api/v1/auth/refresh`
- `logout()`에서 `localStorage.removeItem("refresh_token")` 추가

#### `frontend/src/lib/api/client.ts` — 핵심 변경
- axios response 인터셉터에 **silent refresh** 로직 추가:
  1. 401 응답 수신 시 `localStorage`에서 refresh_token 확인
  2. refresh_token 있으면 `/api/v1/auth/refresh` 호출
  3. 성공 시 새 access_token + refresh_token 저장, 원래 요청 자동 재시도
  4. 실패 시에만 `/auth/login`으로 리다이렉트
- **동시 요청 큐잉**: 여러 API가 동시에 401을 받아도 refresh는 1회만 수행, 나머지는 대기 후 새 토큰으로 재시도

#### `frontend/src/lib/store/auth-store.ts`
- `refreshToken` 상태 필드 추가
- `login()` 시그니처: `login(user, token, refreshToken?)` — refresh_token도 저장
- `updateTokens(token, refreshToken)` 메서드 신규 추가 — silent refresh 후 스토어 동기화
- `hydrateFromClient()`에서 refresh_token도 복원

#### `frontend/src/app/auth/login/page.tsx`
- 로그인 성공 시 `res.refresh_token`을 localStorage에 저장
- `storeLogin(user, access_token, refresh_token)` 호출

#### `frontend/src/app/auth/callback/page.tsx`
- URL searchParams에서 `refresh_token` 파라미터 추출
- localStorage 및 스토어에 저장

### 2.2 백엔드 (1파일)

#### `backend/app/api/v1/social_auth_router.py`
- 소셜 로그인 콜백에서 **refresh_token 발급** 추가
- `auth_service.create_refresh_token(user_id)` 호출
- `auth_service.save_refresh_session(db, ...)` — DB `user_sessions` 테이블에 세션 저장
- 콜백 URL에 `refresh_token` 파라미터 추가: `/auth/callback?token=...&refresh_token=...`

---

## 3. 수정 후 동작 흐름

```
[로그인] → access_token(15분) + refresh_token(7일) 발급 & 저장
  → 15분 경과 → API 호출 시 401 수신
  → axios 인터셉터가 자동으로 POST /api/v1/auth/refresh 호출
  → 새 access_token + refresh_token 발급 (rotation)
  → localStorage + 쿠키 + Zustand 스토어 갱신
  → 원래 실패한 요청 자동 재시도
  → 사용자는 끊김 없이 계속 사용
  → refresh_token 만료(7일) 시에만 재로그인 필요
```

---

## 4. 검증 결과

| 항목 | 결과 |
|------|------|
| `npm run build` | 성공 (빌드 에러 없음) |
| `systemctl restart go100 go100-frontend` | 성공 |
| 백엔드 헬스체크 | `{"status":"ok"}` |
| 프론트엔드 헬스체크 | 307 (미인증 리다이렉트 = 정상) |
| `/api/v1/auth/refresh` 엔드포인트 | 정상 응답 (유효하지 않은 토큰 → 401) |

---

## 5. 백업

| 항목 | 경로 |
|------|------|
| DB 덤프 | `/tmp/backup_GO100-AUTH-FIX_20260224_014012.dump` (740MB) |
| 파일 백업 | 6개 `.bak.20260224_014339` 파일 생성 |

---

## 6. 수정 파일 목록

| 파일 | 변경 유형 |
|------|-----------|
| `frontend/src/lib/api/auth.ts` | 수정 |
| `frontend/src/lib/api/client.ts` | 수정 |
| `frontend/src/lib/store/auth-store.ts` | 수정 |
| `frontend/src/app/auth/login/page.tsx` | 수정 |
| `frontend/src/app/auth/callback/page.tsx` | 수정 |
| `backend/app/api/v1/social_auth_router.py` | 수정 |

---

*CUR-GO100-AUTH-REFRESH-v1 완료*
