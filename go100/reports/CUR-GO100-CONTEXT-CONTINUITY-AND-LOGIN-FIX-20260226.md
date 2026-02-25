# CUR-GO100-CONTEXT-CONTINUITY-001 + LOGIN-FIX-AND-NEXTJS-DEPLOY-001

**날짜**: 2026-02-26
**커밋**: `87eca856` (branch: `feat/CUR-GO100-BAEKOGI-WAVE3`)
**레포**: kis-autotrade-v4

---

## 1. 대화 맥락 연속성 (CUR-GO100-CONTEXT-CONTINUITY-001)

### 문제
- 사용자가 "삼성전자 얼마야" → "더 보여줘" 또는 "다른 종목은?" 같은 **후속 질문**을 했을 때, C2SC가 맥락 없이 새 intent로 분류하여 엉뚱한 응답 발생
- 짧은 후속 메시지("더", "그거", "자세히")가 기본값 `strategy`로 폴백

### 해결

#### 1-1. follow_up intent 추가
- C2SC 분류를 8개 → **9개 intent**로 확장
- `follow_up`: "더 보여줘", "10종목 알려줘", "그중에서", "다른 종목은?" 등

#### 1-2. Redis 기반 대화 맥락 저장
- `go100:chat:ctx:{user_id}` 키에 직전 intent + 메시지 저장 (TTL 10분)
- `_save_chat_context()`: 핸들러 성공 시 호출
- `_get_chat_context()`: C2SC 분류 시 이전 맥락 조회

#### 1-3. follow_up → 이전 intent 라우팅
- LLM이 `follow_up`으로 분류 → Redis에서 직전 intent 조회 → 해당 핸들러로 라우팅
- 키워드 폴백(3차)에서도 짧은 메시지 + 힌트 단어 → `_resolve_follow_up()` 적용

#### 1-4. 맥락 포함 프롬프트
- `_build_c2sc_prompt()`: 기존 프롬프트 + [이전 대화 맥락] + [최근 대화] 섹션 동적 추가
- 대화 히스토리 최근 2턴(4메시지)까지 포함

### 수정 파일
| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/routers/go100/ai_router.py` | follow_up intent, Redis 컨텍스트, _build_c2sc_prompt, _resolve_follow_up, 핸들러별 _save_chat_context |
| `backend/app/api/v1/llm_router.py` | 자유대화(LLM 스트리밍)에서도 히스토리 전달 + 맥락 저장 |

---

## 2. 로그인/배포 수정 (LOGIN-FIX-AND-NEXTJS-DEPLOY-001)

### 2-1. trading41.newtalk.kr API 호출 수정
- **문제**: 외부 도메인(trading41.newtalk.kr)에서 접속 시 API 호출이 localhost:8002로 되어 CORS/접속 실패
- **해결**: `getApiBaseURL()` 함수로 변경 → `trading41.newtalk.kr` 오리진이면 빈 baseURL(same-origin) 사용
- refresh_token 갱신 시에도 동일 로직 적용

### 2-2. /admin/login → /auth/login 리다이렉트
- **문제**: `/admin/login` 또는 `/admin/login.html` 접속 시 404
- **해결**: Next.js middleware에서 `/auth/login?from=/admin`으로 307 리다이렉트

### 2-3. User 타입 호환
- **문제**: 로그인 응답의 user 객체에 `username` 필드 없이 `nickname`만 있는 경우 타입 에러
- **해결**: `nickname → username` 매핑 폴백 추가

### 수정 파일
| 파일 | 변경 내용 |
|------|-----------|
| `frontend/src/lib/api/client.ts` | getApiBaseURL() + same-origin 처리 |
| `frontend/src/app/auth/login/page.tsx` | username 매핑 폴백 |
| `frontend/src/middleware.ts` | /admin/login 리다이렉트 |

---

## 3. collect_kiwoom_strength.py 리팩토링

- Kiwoom ka10047 체결강도 수집 스크립트 코드 정리

---

## 배포 확인

| 항목 | 결과 |
|------|------|
| 백엔드 (go100) | active, 에러 없음 |
| 프론트엔드 (go100-frontend) | active, 빌드 성공 |
| /admin/login 리다이렉트 | 307 → /auth/login |
| API health | 정상 |
