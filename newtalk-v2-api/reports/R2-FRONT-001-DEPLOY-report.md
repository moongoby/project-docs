# R2-FRONT-001-DEPLOY 실행 보고서

**문서번호**: R2-FRONT-001-DEPLOY  
**작성일**: 2026-02-23  
**브랜치**: feature/R2-FRONT-001-setup  
**Git SHA**: 870c007a07ea7bc87d8442038476674e28c61712

---

## §1. 수행 내용 요약

| TASK | 내용 | 결과 |
|------|------|------|
| TASK 1 | AuthController Rate Limiting (throttle:5,1, Sanctum 7일, Redis 포트 수정) | 완료 |
| TASK 2 | middleware 역할별 경로 보호 (ROLE_PATHS, ROLE_HOME, newtalk_role Cookie) | 완료 |
| TASK 3 | api.ts 401 자동 로그아웃 (Cookie/Store 클리어, /login 리다이렉트) | 완료 |
| TASK 4 | frontend Docker 빌드·실행, .env.local, 방화벽 3000, 접속 테스트 | 완료 |
| TASK 5 | Git 커밋·푸시, 보고서, CONTEXT/CHANGELOG 갱신 | 완료 |

---

## §2. 파일 변경 목록

### 백엔드 (서버 반영)
- **routes/api.php** (호스트): login 라우트에 `throttle:5,1` 추가
- **src/routes/api.php**: login 라우트에 `throttle:5,1` 추가 (컨테이너 마운트)
- **src/config/sanctum.php** (컨테이너 내): `expiration` => 60*24*7 (7일)
- **docker-compose.yml**: app 서비스에 `REDIS_PORT=6379` 추가, frontend 서비스 추가
- **app/Http/Controllers/Api/AuthController.php**: 백업 생성 (수정 없음)

### 프론트엔드
- **frontend/src/lib/api.ts**: 로그인 시 `newtalk_role` Cookie 저장, 로그아웃 시 삭제, fetchApi에서 401 시 클리어·리다이렉트
- **frontend/src/middleware.ts**: ROLE_PATHS, ROLE_HOME, 역할별 경로 보호 로직 추가
- **frontend/tailwind.config.ts**: theme.extend.colors에 background, foreground 추가
- **frontend/Dockerfile**: `npm ci` → `npm install` (package-lock.json 없음 대응)
- **frontend/src/app**: (admin)/dashboard → (admin)/admin/dashboard, (md)/md/dashboard 등 역할별 경로로 이동 (Next.js 라우트 충돌 해소)
- **frontend/.env.local**: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_NAME (서버에만 존재, 미커밋)

---

## §3. 빌드 결과

- **frontend**: `docker compose --env-file .env.docker up -d --build frontend` 성공
- Next.js 15.5.12, 정적 페이지 15개 생성, Middleware 34.4 kB
- 컨테이너: newtalk-v2-frontend, 포트 3000:3000

---

## §4. 접속 테스트 결과

| URL | 기대 | 실제 |
|-----|------|------|
| http://127.0.0.1:3000 | 200 또는 리다이렉트 | 307 (→ /login 등) |
| http://[SERVER-IP]:3000 | 200 | 307 |
| http://[SERVER-IP]:3000/login | 200 | **200** |
| http://[SERVER-IP] (V1) | 200 | **200** |
| http://[SERVER-IP]:8080 (API) | 200 | **200** |

- 로그인 rate limit: 1~5회 422, 6회째부터 **429** (throttle 동작 확인)
- V1(80), API(8080) 영향 없음

---

## §5. Git

- **커밋**: `[R2-FRONT-001] Rate Limiting + 역할별 라우트 보호 + 401 자동 로그아웃 + DEPLOY`
- **SHA**: 870c007a07ea7bc87d8442038476674e28c61712
- **푸시**: origin feature/R2-FRONT-001-setup 완료

---

## §6. 비고

- review/ 파일은 유지 (Claude 최종 확인 후 삭제 지시 예정)
- project-docs 동기화: 스크립트 내 `git diff --cached | grep -iE '(password|secret|key|token)'` 검사가 코드 내 `token` 문자열(TOKEN_KEY 등)에 걸려 중단됨. 필요 시 스크립트에서 패턴 조정 후 재실행 권장.
