# R1-TASK-001 보고서: 인증(Sanctum) + RBAC 실제 구현

**문서번호:** NT-V2-R1-TASK-001  
**작성일:** 2026-02-21  
**대상:** 뉴톡 V2 — R1-TASK-001 완료 보고

---

## 1. Sanctum 설치 결과

- **composer require laravel/sanctum**  
  - `laravel/sanctum` v4.3.1 설치 완료.  
  - 설치 시 기존 `spatie/laravel-permission`이 제거되어, 이후 `composer require spatie/laravel-permission`으로 재설치함.
- **vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider"**  
  - `config/sanctum.php` 퍼블리시 완료.  
  - `database/migrations/2026_02_21_100019_create_personal_access_tokens_table.php` 퍼블리시 완료.

---

## 2. 마이그레이션 결과

```text
INFO  Running migrations.
2026_02_21_100019_create_personal_access_tokens_table ......... 21.20ms DONE
```

- `personal_access_tokens` 테이블 생성 완료.

---

## 3. 시더 실행 결과 (계정 목록, 역할)

**실행 명령:** `php artisan db:seed --class=AdminUserSeeder`

**tinker 확인 결과:**

```text
Users: 6
admin@newtalk.kr => admin
md@newtalk.kr => md
purchaser@newtalk.kr => purchaser
wholesale@newtalk.kr => wholesale
retail@newtalk.kr => retail
outsource@newtalk.kr => outsource
```

- 관리자 1명 + 역할별 테스트 계정 5명, 역할 부여 정상.

---

## 4. route:list 출력 (api)

```text
GET|HEAD   api/admin/dashboard ............................................. 
POST       api/auth/login ......................... Api\AuthController@login
POST       api/auth/logout ....................... Api\AuthController@logout
GET|HEAD   api/auth/me ............................... Api\AuthController@me
POST       api/auth/register ................... Api\AuthController@register
GET|HEAD   api/md/dashboard ................................................ 
GET|HEAD   api/purchaser/dashboard ......................................... 
GET|HEAD   api/retail/dashboard ............................................ 
GET|HEAD   api/wholesale/dashboard ......................................... 

Showing [9] routes
```

---

## 5. curl 테스트 결과 (HTTP 코드 + body)

- 테스트 환경: 서버 내부 `http://localhost:8080` (V2 Nginx 포트).

### 6-2. 회원가입 (POST /api/auth/register)

- **HTTP 코드:** 201  
- **body (요약):**  
  - `message`: "회원가입 완료"  
  - `user`: id, name, email, phone  
  - `roles`: ["retail"]  
  - `token`: 발급됨 (1|4xY7...)

### 6-3. 로그인 – 관리자 (POST /api/auth/login)

- **HTTP 코드:** 200  
- **body (요약):**  
  - `message`: "로그인 성공"  
  - `user`: id, name, email, phone, company_name  
  - `roles`: ["admin"]  
  - `permissions`: 배열 (products.view, orders.view, … 등)  
  - `token`: 발급됨 (2|6plMqg...)

### 6-4. 내 정보 조회 (GET /api/auth/me, Bearer 관리자 토큰)

- **HTTP 코드:** 200  
- **body (요약):**  
  - `user`: id, name, email, phone, company_name, business_number, created_at  
  - `roles`: ["admin"]  
  - `permissions`: 전체 권한 목록

### 6-5. 관리자 대시보드 (GET /api/admin/dashboard, Bearer 관리자 토큰)

- **HTTP 코드:** 200  
- **body:** `{"message":"admin dashboard"}`

### 6-6. 소매 토큰으로 관리자 대시보드 접근 (역할 차단)

- **HTTP 코드:** 403  
- **body:**  
  - `message`: "User does not have the right roles."  
  - `exception`: `Spatie\Permission\Exceptions\UnauthorizedException`  
- RBAC 역할 차단 정상 동작.

### 6-7. 로그아웃 (POST /api/auth/logout, Bearer 관리자 토큰)

- **HTTP 코드:** 200  
- **body:** `{"message":"로그아웃 완료"}`

### 6-7 계속. 로그아웃 후 동일 토큰으로 /api/auth/me

- **HTTP 코드:** 401  
- **body:** `{"message":"Unauthenticated."}`  
- 토큰 무효화 확인됨.

---

## 6. V1 영향 없음 확인

- **명령:** `curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]`  
- **결과:** **200**  
- V1 사이트 응답 정상.

---

## 7. Git 커밋·푸시 결과

- **브랜치:** `feature/R1-TASK-001-auth`  
- **커밋:**  
  - 해시: `37ad7e4`  
  - 메시지: `[R1-001] feat: Sanctum 인증 + RBAC 미들웨어 + 관리자 시더`  
  - 변경: 9 files changed, 556 insertions(+), 4 deletions(-)  
- **푸시:** `git push -u origin feature/R1-TASK-001-auth`  
  - 원격 브랜치 생성 및 푸시 완료.  
  - PR 링크: https://github.com/moongoby/newtalk-v2-api-/pull/new/feature/R1-TASK-001-auth

---

## 8. 기타 적용 사항

- **User 모델:**  
  - `HasApiTokens`, `HasRoles` 사용.  
  - `fillable`에 phone, company_name, business_number, v1_idx, v1_auth_code 추가.
- **config/sanctum.php:**  
  - `stateful` 도메인에 `[SERVER-IP]:8080` 포함.
- **bootstrap/app.php:**  
  - `api` 라우트 파일 등록 (`routes/api.php`).  
  - Spatie 미들웨어 alias 등록: `role`, `permission`, `role_or_permission`.
- **인증 불필요:** `/api/auth/register`, `/api/auth/login`.  
- **인증 필요:** `/api/auth/logout`, `/api/auth/me`, 역할별 `/api/*/dashboard`.

---

**완료 기준:** STEP 5 curl 테스트 6-2 ~ 6-7 전 항목 통과.  
**보고서 작성:** 실제 실행 결과만 기재함.
