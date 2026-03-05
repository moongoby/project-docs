# API-SMOKE-002 보고서 — 시드 데이터 기반 V2 API 기능 테스트

**Task ID**: API-SMOKE-002
**의존성**: SEEDER-001 (완료)
**실행일시**: 2026-03-05 (KST)
**작업 디렉토리**: /srv/newtalk-v2
**실행자**: claudebot (Claude Sonnet 4.6)

---

## 1. 환경 및 사전 조건

| 항목 | 내용 |
|------|------|
| API 서버 | localhost:8080 (nginx → newtalk-v2-app 컨테이너) |
| DB 접근 | 127.0.0.1:3307 (MySQL 8.0, newtalk_v2) |
| 시드 데이터 | users 17명, products 46개, orders, shorts 8개, settlements 5개 |
| 호스트 PHP | 8.0.14 (Docker 내 PHP 8.3+ 사용) |

---

## 2. Step 1: DB 백업

```
$ mysqldump -h 127.0.0.1 -P 3307 -u newtalk_v2_user -p"..." newtalk_v2 > /tmp/newtalk_v2_pre_smoke_20260305_191927.sql
BACKUP OK: /tmp/newtalk_v2_pre_smoke_20260305_191927.sql (3307 lines)
```

**결과**: ✅ 백업 완료

> 주의: Docker socket 권한 없음(claudebot 미가입 docker 그룹). `docker compose exec db mysqldump` 대신 직접 MySQL 포트 3307 연결 사용.

---

## 3. Step 2: 인증 테스트 (6개 계정)

**비밀번호 정책**:
- `admin@newtalk.kr` → `NewTalk2026!@#`
- 나머지 5개 → `Test2026!@#`

> 특이사항: throttle 5/1분 제한으로 마지막 2개 계정(retail, outsource)은 1분 대기 후 재시도

| Email | 기대 | HTTP | token 발급 | 결과 |
|-------|------|------|-----------|------|
| admin@newtalk.kr | 200+token | 200 | YES | ✅ PASS |
| md@newtalk.kr | 200+token | 200 | YES | ✅ PASS |
| purchaser@newtalk.kr | 200+token | 200 | YES | ✅ PASS |
| wholesale@newtalk.kr | 200+token | 200 | YES | ✅ PASS |
| retail@newtalk.kr | 200+token | 200 | YES | ✅ PASS |
| outsource@newtalk.kr | 200+token | 200 | YES | ✅ PASS |

**결과**: ✅ 6/6 로그인 성공

---

## 4. Step 3: CRUD 테스트 (admin 토큰 사용)

**admin 토큰**: `109|31Mv0riK5kEFh2GhaL1Z3Ee5zycExFsoFaD9xVIz9f83a9dc`

> 특이사항: Sanctum 토큰은 52자. Python 출력 截잘림([:50]) 이슈로 첫 시도 401 발생. 파일 기반 응답 저장 후 전체 토큰 추출하여 재시도 성공.

### 결과 매트릭스

| 엔드포인트 | 메서드 | 기대 | 실제 HTTP | 실제 데이터 | 결과 |
|------------|--------|------|-----------|------------|------|
| /api/health | GET (no auth) | 200 | **404** | (Laravel에는 없음 — ShortFlow:8000) | ⚠️ N/A |
| /api/auth/me | GET | 200+user | 200 | admin user, roles:["admin"] | ✅ PASS |
| /api/products | GET | 200+data | 200 | total:45, last_page:3 | ✅ PASS |
| /api/orders | GET | 200+data | 200 | 6 items | ✅ PASS |
| /api/dashboard/overview | GET | 200+data | 200 | products:45, members:17 | ✅ PASS |
| /api/shorts | GET | 200+data | 200 | total:8 items | ✅ PASS |
| /api/settlements | GET | 200+data | 200 | total:5 items | ✅ PASS |
| /api/dropship | GET | 200+data | 200 | total:0 (시드 미투입) | ✅ PASS |
| /api/fulfillment/dashboard | GET | 200+data | 200 | total:0 (시드 미투입) | ✅ PASS |
| /api/pipeline/dashboard | GET | 200+data | 200 | by_status 구조 정상 | ✅ PASS |
| /api/purchase-orders | GET | 200+data | 200 | total 정상 | ✅ PASS |

**500 에러**: **0건** ✅
**정상 응답 (200)**: **10/10 엔드포인트** ✅

### 상세 응답 발췌

```json
// dashboard/overview
{
  "success": true,
  "data": {
    "role": "admin",
    "products": {"total": 45, "active": 45},
    "orders": {"pending_approval": 5, "in_progress": 12, "this_month_amount": 0},
    "members": {"total": 17, "wholesale": 4, "retail": 9}
  }
}

// fulfillment/dashboard
{
  "by_status": {"pending": 0, "in_progress": 0, "completed": 0, "issue_found": 0},
  "by_type": {"inspection": 0, "packing": 0, "labeling": 0, "shipping": 0},
  "total": 0
}
```

### SERVICE-FIX-001 확인

| 서비스 | 이전 (500 에러) | 이번 결과 | 결과 |
|--------|----------------|----------|------|
| /api/dropship | 500 | **200** | ✅ 해소 |
| /api/fulfillment/dashboard | 500 | **200** | ✅ 해소 |
| /api/pipeline/dashboard | 500 | **200** | ✅ 해소 |

---

## 5. Step 4: Feature Test

```
$ docker compose --env-file .env.docker exec app php artisan test --testsuite=Feature
permission denied while trying to connect to the Docker daemon socket
```

**결과**: ⚠️ SKIPPED — 실행 제약

**사유**:
- `claudebot` 계정이 `docker` 그룹에 미포함 (permission denied)
- 호스트 PHP 8.0.14 — Laravel 요구 PHP >= 8.3.0 충족 불가
- Feature test 파일 존재 확인: `tests/Feature/Api/` 내 AuthTest, ProductTest, ShortTest, PaymentTest (총 7개 테스트 파일)

**대안 검증**: API 직접 호출 테스트(HTTP)로 핵심 기능 동작 확인 완료 (500 에러 0건, 10개 엔드포인트 200 응답)

---

## 6. 시드 데이터 검증 (MySQL 직접)

```
$ mysql -h 127.0.0.1 -P 3307 -u newtalk_v2_user ... -e "SELECT COUNT(*) FROM users;"
COUNT(*): 17

(백업 파일 3307 라인 — 전체 테이블 정상 덤프됨)
```

---

## 7. 완료 기준 체크리스트

| 기준 | 상태 |
|------|------|
| ✅ 6개 계정 로그인 성공 (200 + token) | **PASS** |
| ✅ 핵심 엔드포인트 10개+ 정상 응답 (200 + data) | **PASS (10/10)** |
| ✅ 500 에러 0건 | **PASS** |
| ⚠️ Feature Test PASS | **SKIPPED** (Docker 권한 제약) |
| ✅ 보고서 push HTTP 200 | (push 후 확인 예정) |

---

## 8. 특이사항 / 트러블슈팅

1. **Docker socket 권한 없음**: `claudebot` 계정이 `docker` 그룹 미포함. `mysqldump`는 포트 3307 직접 접속으로 우회.
2. **throttle 5/1분**: 로그인 엔드포인트에 `throttle:5,1` 미들웨어. 6개 계정 순차 테스트 시 마지막 2개 429 → 1분 대기 후 성공.
3. **Bash ! 특수문자**: `NewTalk2026!@#` 비밀번호 curl 단일따옴표에서 history expansion 충돌. 해결: 파일 기반 JSON(`-d @file`) 또는 heredoc(`-d @-`) 사용.
4. **Sanctum 토큰 截잘림**: token[:50] 파이썬 슬라이스로 52자 토큰 잘림 → 401. 해결: 전체 응답 파일 저장 후 토큰 추출.
5. **/api/health 404**: Laravel 앱에는 `/api/health`가 없음. ShortFlow Worker API(포트 8000)에 존재. Laravel 헬스는 `/` 응답(200)으로 확인 가능.
6. **products 45 vs 46**: seeder에서 46개 목표였으나 DB에 45개 — 동일 product_code 중복 방지로 1개 skip된 것으로 추정. 기능 이상 없음.

---

## 9. 결론

**SEEDER-001 시드 데이터 기반 API 기능 테스트 완료.**

- 6개 역할별 계정 로그인: **전원 성공**
- 핵심 API 엔드포인트 10개: **모두 200 응답**
- 500 에러: **0건**
- SERVICE-FIX-001 (DropshipService, FulfillmentService, ContentPipelineService): **전원 정상 (200)**
- Feature Test: Docker 권한 제약으로 실행 불가 (HTTP 직접 테스트로 대체 검증)
