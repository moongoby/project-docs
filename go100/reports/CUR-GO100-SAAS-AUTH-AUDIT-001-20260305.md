# CUR-GO100-SAAS-AUTH-AUDIT-001 — SaaS 회원가입·인증 플로우 현황 감사 및 구현 계획 수립

**작성일**: 2026-03-05
**Task ID**: T-013
**우선순위**: P1-HIGH
**작업자**: Claude (claudebot)

---

[인계 확인]
직전 완료: T-122 (KJH_CYCLE)
현재 단계: Phase 2C — Command Center
CEO 지시 적용: D-001 (보고서 push 필수), D-002 (HANDOVER 업데이트)
strategy_cards: 조회 미수행 (인증 감사 태스크)
open_positions: 조회 미수행

---

## 1. 감사 목적

SaaS 체크리스트 #1(회원가입), #5(이용약관), #6(개인정보처리방침)에 대한 **현황 파악** 및 **구현 로드맵 작성**.

---

## 2. 백엔드 인증 코드 스캔 결과

### 2.1 인증 관련 핵심 파일 목록

| 파일 경로 | 크기 | 역할 |
|-----------|------|------|
| `backend/app/routers/v4_auth.py` | 8,623 bytes | V4 인증 라우터 (이메일 로그인/회원가입/갱신) |
| `backend/app/routers/v4_social_auth.py` | 2,868 bytes | 소셜 로그인 라우터 (Kakao/Naver/Google) |
| `backend/app/core/auth_v1.py` | 14,988 bytes | V4.1 JWT 인증 서비스 (AuthService 클래스) |
| `backend/app/core/auth.py` | 3,325 bytes | 레거시 인증 유틸 (create_access_token 등) |
| `backend/app/core/social_auth.py` | ~6KB | 소셜 OAuth2 URL/토큰 교환 처리 |
| `backend/app/services/auth/oauth_service.py` | 7,926 bytes | OAuthService 클래스 (Google/Kakao/Naver) |
| `backend/app/routers/v4_email.py` | 이메일 인증 토큰 라우터 |

### 2.2 이메일 인증(signup) 엔드포인트

**엔드포인트**: `POST /api/v4/auth/signup`
**위치**: `backend/app/routers/v4_auth.py`

구현 상태:
- ✅ 이메일/비밀번호 유효성 검사 (8자 이상)
- ✅ 이메일 중복 확인 (409 CONFLICT)
- ✅ bcrypt 비밀번호 해싱
- ✅ `users` 테이블 INSERT (role='FREE', is_active=true)
- ✅ 가입 즉시 access_token 발급
- ❌ `agreed_terms`, `agreed_privacy` 컬럼 저장 미구현 (DB 컬럼은 존재)
- ❌ 이메일 인증(verify) 후 활성화 플로우 미연결
- ❌ 마케팅 동의(`agreed_marketing`) 저장 미구현

**프론트엔드 signup 요청 코드** (`frontend/src/app/auth/signup/page.tsx`):
```typescript
await apiSignup(email.trim(), password, name.trim(), agreedTerms, agreedTerms);
// agreed_terms, agreed_privacy를 동일 값으로 전달
```
→ `agreedPromo` (마케팅 동의) 값은 전달하지 않음

### 2.3 로그인 엔드포인트

**엔드포인트**: `POST /api/v4/auth/login`
구현 상태:
- ✅ 이메일/비밀번호 검증 (timing attack 방지 포함)
- ✅ 소셜 계정에 비밀번호 없을 때 안내 메시지
- ✅ is_active 비활성 계정 처리
- ✅ access_token + refresh_token 발급
- ✅ refresh_token 갱신 (`POST /api/v4/auth/refresh`)

### 2.4 소셜 로그인 엔드포인트

**라우터**: `backend/app/routers/v4_social_auth.py`

| 엔드포인트 | 설명 |
|------------|------|
| `GET /api/v4/social-auth/providers` | 지원 제공자 목록 (env 설정 여부 기반 enabled) |
| `GET /api/v4/social-auth/{provider}/url` | OAuth 인증 URL 생성 |
| `POST /api/v4/social-auth/{provider}/callback` | OAuth code → JWT 발급 |

지원 제공자: `google`, `kakao`, `naver`

**활성화 여부** (환경변수 기반):
- `GOOGLE_CLIENT_ID`, `KAKAO_CLIENT_ID`, `NAVER_CLIENT_ID` 설정 여부에 따라 enabled
- `OAuthService.handle_callback()`: code → access_token → userinfo → users INSERT/SELECT → JWT 발급

**콜백 URL (redirect_uri)**:
```
Google: https://trading.newtalk.kr/auth/google/callback
Kakao:  https://trading.newtalk.kr/auth/kakao/callback
Naver:  https://trading.newtalk.kr/auth/naver/callback
```

---

## 3. 프론트엔드 인증 페이지 확인 결과

### 3.1 인증 관련 페이지 목록

| 경로 | 파일 | 상태 |
|------|------|------|
| `/auth/login` | `frontend/src/app/auth/login/page.tsx` | ✅ 구현 완료 |
| `/auth/signup` | `frontend/src/app/auth/signup/page.tsx` | ✅ 구현 완료 |
| `/terms` | `frontend/src/app/terms/page.tsx` | ✅ 구현 완료 |
| `/privacy` | `frontend/src/app/privacy/page.tsx` | ✅ 구현 완료 |

### 3.2 로그인 페이지 (`/auth/login`)

- ✅ 이메일/비밀번호 폼
- ✅ 카카오/네이버/구글 소셜 버튼 (API URL 동적 생성)
- ✅ refresh_token localStorage 저장
- ✅ `?from=` 파라미터로 리다이렉트
- ✅ 모바일 최적화 레이아웃

수정 이력:
- CUR-V1-LOGIN-PAGE-v1, CUR-AL-DESIGN-v1 (2026-02-19)
- CUR-AR-KAKAO-AUTH-v1 + CUR-AS-NAVER-AUTH-v1 (2026-02-19)
- CUR-SIGNUP-SNS-v1 (2026-02-19): 구글 버튼 추가
- CUR-GO100-AUTH-REFRESH-v1 (2026-02-24): refresh_token 저장

### 3.3 회원가입 페이지 (`/auth/signup`)

- ✅ 이름, 이메일, 비밀번호, 비밀번호 확인 필드
- ✅ 비밀번호 강도 검증 (8자, 영문+숫자+특수문자)
- ✅ 이용약관 동의 체크박스 (필수)
- ✅ 마케팅 동의 체크박스 (선택, 기본값 true)
- ✅ 카카오/네이버/구글 소셜 간편가입 버튼
- ✅ `/terms`, `/privacy` 링크

**미구현**:
- ❌ 이메일 인증 발송 후 "인증 메일을 확인하세요" 안내 없음
- ❌ 가입 즉시 대시보드 진입 (이메일 검증 없이)

### 3.4 이용약관 페이지 (`/terms`)

- ✅ 구현 완료 (CUR-LEGAL-PAGES-v1, 2026-02-20)
- 시행일: 2026-02-20
- 소프트웨어 제공업 한정, 3회 검토 완료
- 주요 조항: 서비스 성격 고지, 면책 조항 포함

### 3.5 개인정보처리방침 페이지 (`/privacy`)

- ✅ 구현 완료 (CUR-LEGAL-PAGES-v1, 2026-02-20)
- 시행일: 2026-02-20

---

## 4. DB 사용자 테이블 확인 결과

### 4.1 `users` 테이블 스키마

```
=== users table columns ===
id              : integer
email           : character varying
name            : character varying
phone           : character varying
hashed_password : character varying
role            : character varying
plan_type       : character varying
is_active       : boolean
is_verified     : boolean
agreed_terms    : boolean
agreed_privacy  : boolean
agreed_marketing: boolean
subscription_end: timestamp without time zone
created_at      : timestamp without time zone
updated_at      : timestamp without time zone
last_login      : timestamp without time zone

Total users: 12
```

### 4.2 컬럼 분석

| 컬럼 | 현황 |
|------|------|
| `is_verified` | DB 컬럼 존재, 가입 시 false 기본값 추정 — 이메일 인증 플로우 미연결 |
| `agreed_terms` | DB 컬럼 존재, 가입 API에서 저장 미구현 |
| `agreed_privacy` | DB 컬럼 존재, 가입 API에서 저장 미구현 |
| `agreed_marketing` | DB 컬럼 존재, 가입 API에서 저장 미구현 |
| `plan_type` | DB 컬럼 존재, 가입 시 저장 미구현 |
| `phone` | DB 컬럼 존재, 가입 폼에 없음 |

---

## 5. OAuth/소셜 로그인 라이브러리 확인 결과

### 5.1 백엔드 (`backend/requirements.txt`)

```
passlib[bcrypt]>=1.7.4   # 비밀번호 해싱
PyJWT>=2.8.0             # JWT 생성/검증
bcrypt>=4.1.0            # bcrypt
```

**미포함 라이브러리**:
- `authlib` — 없음 (자체 httpx 기반 OAuth 구현)
- `python-social-auth` — 없음
- `fastapi-users` — 없음

→ **순수 httpx 기반 커스텀 OAuth2 구현** (`social_auth.py`, `services/auth/oauth_service.py`)

### 5.2 프론트엔드 (`frontend/package.json`)

- `next-auth` — **없음**
- OAuth 처리는 백엔드 redirect URL로 위임

---

## 6. 현황 종합 평가

### 6.1 SaaS 체크리스트 달성 현황

| 항목 | 체크리스트 | 상태 | 비고 |
|------|------------|------|------|
| #1 회원가입 | 이메일/비밀번호 가입 | ✅ 완료 | DB에 is_verified 미반영 |
| #1 회원가입 | 소셜(카카오/네이버/구글) 간편가입 | ⚠️ 부분 | API 구조 완성, env 키 설정 필요 |
| #1 회원가입 | 이메일 인증 발송 | ❌ 미연결 | v4_email.py 존재하나 signup 시 미호출 |
| #5 이용약관 | /terms 페이지 | ✅ 완료 | 2026-02-20 검토 완료 |
| #5 이용약관 | 가입 시 동의 체크박스 | ✅ 완료 | 프론트엔드 구현됨 |
| #5 이용약관 | DB agreed_terms 저장 | ❌ 미구현 | signup API에서 누락 |
| #6 개인정보처리방침 | /privacy 페이지 | ✅ 완료 | 2026-02-20 검토 완료 |
| #6 개인정보처리방침 | DB agreed_privacy 저장 | ❌ 미구현 | signup API에서 누락 |

---

## 7. SaaS 인증 구현 로드맵

### Phase A: 즉시 수정 필요 (P1)

#### A-1: signup API에 agreed_terms/agreed_privacy/agreed_marketing 저장

**파일**: `backend/app/routers/v4_auth.py`
**변경**: INSERT 쿼리에 컬럼 추가

```sql
INSERT INTO users (email, name, hashed_password, role, is_active,
                   agreed_terms, agreed_privacy, agreed_marketing)
VALUES (:email, :name, :hashed_password, 'FREE', true,
        :agreed_terms, :agreed_privacy, :agreed_marketing)
```

**프론트엔드**: `SignupRequest` 스키마에 agreed_terms/agreed_privacy/agreed_marketing 추가

#### A-2: is_verified 플래그 신뢰성 확보

현재 가입 시 `is_verified=false`가 기본값이나, 로그인 시 is_verified 체크 없음.
→ 이메일 인증 의무화 여부를 결정 후 적용

### Phase B: 이메일 인증 플로우 연결 (P2)

`backend/app/routers/v4_email.py`가 이미 존재함:
- `POST /api/v4/email/send-verify` — 인증 이메일 발송
- `POST /api/v4/email/verify` — 토큰 검증 → `is_verified = true`

**변경 사항**:
1. `signup` 완료 후 `send-verify` 자동 호출
2. 프론트: "인증 메일을 확인해 주세요" 안내 페이지 추가
3. 로그인 시 `is_verified = false` 계정에 경고 표시 (강제 차단은 선택)

### Phase C: 소셜 로그인 활성화 (P2)

**현재 상태**: 코드 완성, env 키 미설정

필요 작업:
1. `.env`에 OAuth 앱 키 설정:
   ```
   KAKAO_CLIENT_ID=...
   KAKAO_CLIENT_SECRET=...
   NAVER_CLIENT_ID=...
   NAVER_CLIENT_SECRET=...
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   ```
2. 각 플랫폼 OAuth 앱에 redirect_uri 등록:
   - `https://trading.newtalk.kr/auth/{provider}/callback`
3. 프론트엔드: 소셜 로그인 콜백 페이지 구현
   - `/auth/kakao/callback`, `/auth/naver/callback`, `/auth/google/callback`
   - query param `code`를 백엔드 `/api/v4/social-auth/{provider}/callback`으로 전달

### Phase D: 추가 SaaS 기능 (P3)

- 비밀번호 찾기/재설정 (forgot-password, reset-password)
- 계정 탈퇴 (GDPR/개인정보보호법 대응)
- 이용약관 버전 관리 (업데이트 시 재동의 요청)
- 멀티팩터 인증 (MFA) — 장기 로드맵

---

## 8. 핵심 발견 사항

1. **agreed_terms/agreed_privacy DB 컬럼 존재하나 signup API에서 미저장** — 법적 리스크
2. **이메일 인증 인프라 (v4_email.py) 이미 완성** — signup과 연결만 하면 됨
3. **소셜 로그인 코드 완성** — env 키와 프론트 콜백 페이지만 추가하면 즉시 활성화 가능
4. **약관/개인정보 페이지 정식 완성** (2026-02-20) — 법적 고지 요건 충족
5. **next-auth 미사용** — 순수 커스텀 JWT 구현, 유연하나 유지보수 부담 존재

---

## 9. 저장 정보

```
보고서 로컬 경로: /root/project-docs/go100/reports/CUR-GO100-SAAS-AUTH-AUDIT-001-20260305.md
보고서 GitHub URL: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-SAAS-AUTH-AUDIT-001-20260305.md
작성 시각: 2026-03-05T19:xx KST
Task ID: T-013
```

- [x] 코드 레포 커밋 완료 (해당 없음 — 코드 변경 없는 감사 태스크)
- [ ] project-docs 보고서 push 완료
