# NewTalk V2 — R1~R4 코드 검수 보고서

**문서번호**: CODE-REVIEW-001
**검수일**: 2026-02-27
**검수환경**: 114.207.244.86 (서버 114)
**상태**: 검수 완료 (코드 수정 없음)

---

## 1. 인프라 검증 (PHASE 1)

### 1-1. Docker 컨테이너 상태

| 컨테이너 | 상태 | 비고 |
|---|---|---|
| newtalk-v2-app | Up 4일 | PHP 8.3-FPM |
| newtalk-v2-db | Up 5일 (healthy) | MySQL |
| newtalk-v2-nginx | Up 5일 | Reverse Proxy |
| newtalk-v2-redis | Up 5일 | Cache |
| newtalk-v2-frontend | Up 19시간 | Next.js |

**결과**: 5/5 컨테이너 정상 가동 ✅

### 1-2. Git 상태

| 항목 | 값 |
|---|---|
| Branch | main |
| 최신 SHA | 770ae91 |
| Origin 동기화 | 비동기 (로컬 4커밋 ahead, 원격 2커밋 behind) |

**주의**: `git push` 필요. 로컬과 원격이 diverged 상태.

### 1-3. 프레임워크 버전

| 항목 | 버전 |
|---|---|
| PHP | 8.3.30 |
| Laravel | 12.52.0 |
| Next.js | 15.x |
| Node (frontend) | 20.x |
| TypeScript | 5.9.3 |

### 1-4. 마이그레이션

| 항목 | 값 |
|---|---|
| 총 마이그레이션 | 71개 |
| 실행 완료 | 71개 |
| 미실행 (pending) | 0개 |
| migrate --pretend | OK (오류 없음) |

**결과**: 마이그레이션 정상 ✅

### 1-5. 데이터베이스

| 항목 | 값 | 예상 | 판정 |
|---|---|---|---|
| 테이블 수 | 66 | 90+ | ⚠️ 부족 |

**주의**: R3/R4 관련 테이블이 일부 누락 가능성 있음.

### 1-6. 라우트

| 항목 | 값 | 예상 | 판정 |
|---|---|---|---|
| API 라우트 수 | 71 | 130+ | ⚠️ 부족 |

**주의**: R4 확장 기능(배송/정산/결제 등) 라우트 미구현.

---

## 2. 헬스체크 (PHASE 2)

| 대상 | URL | HTTP | 판정 |
|---|---|---|---|
| V1 | https://newtalk.kr | 200 | ✅ |
| V2 API | http://114.207.244.86:8080 | 200 | ⚠️ HTML 반환 (JSON 아님) |
| V2 Frontend | http://114.207.244.86:3000 | 307→/login | ✅ (인증 리다이렉트 정상) |

---

## 3. API 스모크 테스트 (PHASE 3)

### 3-0. 인증 (Auth)

| 테스트 | HTTP | 결과 |
|---|---|---|
| POST /api/auth/login (JSON body) | 200 | ⚠️ tinker로 토큰 생성 (시더 비밀번호 불명) |
| GET /api/auth/me | 200 | ✅ admin 역할, 33개 퍼미션 |
| Sanctum 토큰 인증 | - | ✅ 정상 동작 |

**데이터 확인**:
- 사용자 수: 17명
- admin 계정: admin@newtalk.kr (id:1)
- 역할: admin, md, purchaser, wholesale, retail 시스템 구현 완료

### 3-1. R1: 상품/재고/사입 API

| 엔드포인트 | HTTP | 결과 | 비고 |
|---|---|---|---|
| GET /api/products?per_page=3 | 200 | ✅ | 15개 상품, 페이지네이션 정상 |
| GET /api/purchase-orders | **500** | ❌ | `Builder::byDateRange()` 미정의 |
| GET /api/inbound-receipts | 200 | ✅ | 빈 목록 (데이터 없음) |
| GET /api/barcodes | 200 | ✅ | 빈 목록 (데이터 없음) |
| GET /api/dashboard/overview | **500** | ❌ | `PurchaseOrder::STATUS_PENDING` 미정의 |
| GET /api/dashboard/stats | 200 | ✅ | 시스템 통계 정상 |
| GET /api/dashboard/purchasing/summary | **500** | ❌ | `PurchaseOrder::STATUS_CANCELLED` 미정의 |

**R1 크리티컬 버그**:

> **BUG-001: R1 모델 파일 비어있음 (심각도: CRITICAL)**
>
> `PurchaseOrder.php`, `InboundReceipt.php`, `Barcode.php` 3개 모델이 빈 스텁(empty stub)입니다.
>
> ```php
> // 현재 (PurchaseOrder.php)
> class PurchaseOrder extends Model
> {
>     //
> }
> ```
>
> - 백업 파일 존재: `*.php.bak.20260221_230235`
> - 백업에는 `STATUS_PENDING`, `STATUS_CANCELLED`, `scopeByDateRange()` 등 전체 구현이 있음
> - **원인 추정**: 2026-02-21 작업 중 모델이 빈 상태로 덮어씌워짐
> - **영향**: 발주 목록, 대시보드 개요, 사입 대시보드 전면 장애 (HTTP 500)

### 3-2. R2: SNS 소셜 엔진 API

| 엔드포인트 | HTTP | 결과 | 비고 |
|---|---|---|---|
| GET /api/feed/explore (비인증) | 200 | ✅ | 3개 피드, 커서 기반 |
| GET /api/feed | 200 | ✅ | 팔로우 기반 피드 |
| GET /api/feed/search?q=test | 200 | ✅ | 검색 동작 (결과 0) |
| GET /api/feed/1 | 200 | ✅ | 상세 조회, view_count 증가 |
| POST /api/feed/1/like | 200 | ✅ | 좋아요 토글 동작 |
| GET /api/wishlists | 200 | ✅ | 빈 목록 |
| GET /api/follows/1/followers | 200 | ✅ | 빈 목록 |
| GET /api/follows/1/following | 200 | ✅ | 1명 팔로잉 |

**R2 판정**: 전체 정상 ✅

### 3-3. R3: DM (Direct Message) API

| 엔드포인트 | HTTP | 결과 | 비고 |
|---|---|---|---|
| GET /api/conversations | **500** | ❌ | ParseError (구문 오류) |
| POST /api/conversations | **500** | ❌ | ParseError (구문 오류) |

**R3 크리티컬 버그**:

> **BUG-002: ConversationService.php 구문 오류 (심각도: CRITICAL)**
>
> 파일: `app/Services/ConversationService.php:63`
> 에러: `syntax error, unexpected token "public", expecting ")"`
>
> **원인**: `getOrCreateDirect()` 메서드의 `DB::transaction()` 클로저에 닫는 `});` 가 누락됨.
>
> ```php
> // 라인 60-63 (현재 — 버그)
>         return $conversation->fresh(['participants']);
>     }    // ← DB::transaction 클로저 닫는 }); 가 없음
>
>     /**
>      * 대화 나가기 ...
>      */
>     public function leave(...)  // ← "public" 에서 파싱 에러
> ```
>
> **영향**: R3 DM 전체 기능 사용 불가

### 3-4. R4: 역할별 대시보드

| 엔드포인트 | HTTP | 결과 |
|---|---|---|
| GET /api/admin/dashboard | 200 | ✅ |
| GET /api/md/dashboard | 200 | ✅ |
| GET /api/purchaser/dashboard | 200 | ✅ |
| GET /api/wholesale/dashboard | 200 | ✅ |
| GET /api/retail/dashboard | 200 | ✅ |

**R4 판정**: 역할별 라우팅 정상 ✅ (단, 실제 비즈니스 로직은 placeholder 수준)

### 3-5. 보안 테스트

| 테스트 | HTTP | 결과 |
|---|---|---|
| 토큰 없이 GET /api/products | 401 | ✅ 차단 |
| 토큰 없이 GET /api/admin/dashboard | 401 | ✅ 차단 |
| 잘못된 토큰으로 GET /api/auth/me | 401 | ✅ 차단 |

**보안 판정**: Sanctum 인증 + Spatie Role 미들웨어 정상 ✅

---

## 4. 프론트엔드 렌더링 (PHASE 4)

### 4-1. 페이지 접근 테스트

| 페이지 | HTTP | 결과 | 비고 |
|---|---|---|---|
| / (홈) | 307 | ✅ | /login 리다이렉트 (미인증) |
| /login | 200 | ✅ | 한국어 UI 정상 렌더링 |
| /products | 307 | ✅ | /login 리다이렉트 |
| /dashboard | 307 | ✅ | /login 리다이렉트 |
| /feed | 307 | ✅ | /login 리다이렉트 |

**렌더링 판정**: SSR 정상, 인증 가드 동작 ✅

### 4-2. 프론트엔드 로그 (컨테이너)

> **BUG-003: Server Action 에러 (심각도: HIGH)**
>
> ```
> [Error: Failed to find Server Action "x". This request might be from an older or newer deployment.]
> [Error: aborted] { code: 'ECONNRESET' }
> ```
>
> - 로그인 form 등에서 Server Action 호출 시 지속적 에러 발생
> - **원인 추정**: Next.js 빌드 후 Server Action ID 불일치 (deployment 미스매치)
> - **영향**: 로그인 등 Server Action 기반 기능 동작 불가

---

## 5. TypeScript 빌드 검증 (PHASE 5)

### 5-1. tsc --noEmit 결과

| 항목 | 값 |
|---|---|
| 총 TS 에러 | **43개** |
| 에러 파일 수 | 11개 |

### 5-2. 에러 파일별 분포

| 파일 | 에러 수 | 주요 원인 |
|---|---|---|
| lib/shorts-api.ts | 18 | ApiResponse\<T\> → T 타입 변환 오류 |
| lib/shipping-api.ts | 10 | ApiResponse\<T\> → T 타입 변환 오류 |
| lib/dm-api.ts | 6 | ApiResponse\<T\> 래핑 타입 불일치 |
| components/fulfillment/*.tsx | 4 | 타입 정의 불일치 |
| components/story/StoryReactionBar.tsx | 1 | 타입 오류 |
| components/channel/*.tsx | 2 | 타입 정의 불일치 |

**공통 원인**: `ApiResponse<T>` 래퍼 타입에서 내부 `T` 데이터를 직접 반환하는 패턴에서 타입 불일치. `api.ts`의 공통 fetch 함수가 `ApiResponse<T>`를 반환하지만, 개별 API 함수들이 `T`를 직접 반환하는 것으로 선언됨.

### 5-3. Laravel 테스트

| 항목 | 값 |
|---|---|
| 테스트 수 | 2개 (Example 테스트만) |
| 결과 | 2 passed ✅ |

**주의**: R1~R4 기능별 테스트가 없음. 예제 테스트만 존재.

---

## 6. 종합 판정

### 6-1. 라운드별 판정

| 라운드 | 상태 | 판정 | 비고 |
|---|---|---|---|
| **R1** (상품/재고/사입) | ⚠️ 부분 장애 | **FAIL** | 모델 빈 스텁 → 발주/대시보드 500 에러 |
| **R2** (SNS 소셜) | ✅ 정상 | **PASS** | 전 엔드포인트 200 |
| **R3** (DM) | ❌ 전면 장애 | **FAIL** | ConversationService 구문 오류 |
| **R4** (역할 대시보드) | ✅ 정상 | **PASS** | 5개 역할 라우팅 정상 (placeholder) |

### 6-2. 크리티컬 버그 요약

| ID | 심각도 | 모듈 | 설명 | 영향 |
|---|---|---|---|---|
| BUG-001 | **CRITICAL** | R1 | PurchaseOrder/InboundReceipt/Barcode 모델 빈 스텁 | 발주목록, 대시보드 개요, 사입대시보드 500 에러 |
| BUG-002 | **CRITICAL** | R3 | ConversationService.php:63 구문 오류 (닫는 중괄호 누락) | DM 전체 기능 사용 불가 |
| BUG-003 | **HIGH** | Frontend | Server Action ID 불일치 (continuous error) | 로그인 등 SA 기반 기능 동작 불가 |

### 6-3. 경고 사항

| ID | 심각도 | 설명 |
|---|---|---|
| WARN-001 | MEDIUM | TypeScript 43개 에러 (shorts-api, shipping-api, dm-api) |
| WARN-002 | MEDIUM | DB 테이블 66개 (예상 90+ 대비 부족) |
| WARN-003 | MEDIUM | API 라우트 71개 (예상 130+ 대비 부족) |
| WARN-004 | LOW | R1~R4 기능별 유닛/통합 테스트 없음 (Example만 2개) |
| WARN-005 | LOW | Git origin과 diverged 상태 (push 필요) |
| WARN-006 | LOW | V2 API 루트(/) HTML 반환 (JSON welcome 권장) |
| WARN-007 | LOW | R4 역할별 대시보드 placeholder 수준 (실제 비즈니스 로직 미구현) |

### 6-4. 즉시 조치 필요 항목

1. **[BUG-001]** `.bak.20260221_230235` 백업 파일에서 R1 모델 3개 복원
2. **[BUG-002]** ConversationService.php `getOrCreateDirect()` 메서드 닫는 `});` 추가
3. **[BUG-003]** Frontend 컨테이너 재빌드 (`next build` → `next start`)

### 6-5. 권장 후속 작업

1. R1~R4 기능별 Feature 테스트 작성
2. TypeScript 43개 에러 수정 (ApiResponse\<T\> 래퍼 패턴 통일)
3. 누락 테이블/라우트 점검 및 구현 완료
4. Git origin 동기화 (push/rebase)
5. R4 역할별 대시보드 실제 비즈니스 로직 구현

---

**검수자**: Claude Code (자동 검수)
**검수 방법**: Docker 내부 curl + tsc --noEmit + Laravel artisan
**참고**: 본 검수는 코드 수정 없이 읽기 전용으로 수행됨.
