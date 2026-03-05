# CUR-GO100-ERROR-MONITORING-001 보고서

**Task ID:** T-031
**제목:** 에러 모니터링 설정 (자체 에러 로깅 + Telegram 알림)
**날짜:** 2026-03-05
**담당:** claudebot (Claude Sonnet 4.6)
**브랜치:** phase-2c-command-center
**커밋:** 758dc8c7

---

## [인계 확인]
직전 완료: T-029 (sitemap.xml 동적 생성)
현재 단계: Phase GO100 SaaS 체크리스트
CEO 지시 적용: CLAUDE.md 공통 절대 규칙
strategy_cards: N/A
open_positions: N/A

---

## 1. 배경 및 목적

SaaS 체크리스트 #10 "에러 모니터링" 항목 미구현 상태.
Sentry DSN 없음 → 자체 에러 모니터링 미들웨어 + Telegram 알림으로 구현.

---

## 2. 사전 조건 확인

| 항목 | 결과 |
|------|------|
| SENTRY DSN 존재 여부 | **없음** (NO_SENTRY_DSN) |
| GO100_TELEGRAM_BOT_TOKEN | 설정됨 (8327167593:...) |
| GO100_TELEGRAM_CHAT_ID | 설정됨 (6817948795) |
| FastAPI 서비스 상태 | 정상 (HTTP 200) |
| main.py 백업 | backend/app/main.py.bak.T031 |

---

## 3. 구현 내용

### 3.1 파일 생성

#### `backend/app/middleware/__init__.py`
미들웨어 패키지 초기화 파일.

#### `backend/app/middleware/error_monitor.py`
FastAPI `BaseHTTPMiddleware` 기반 에러 모니터링 미들웨어.

**주요 기능:**
- `dispatch()`: 모든 요청을 감싸서 500 에러 캐치
- `_handle_error()`: 에러 정보 수집 (endpoint, method, traceback, request body)
- `_save_to_db()`: `go100_error_log` 테이블에 비동기 저장
- `_send_telegram()`: `GO100_TELEGRAM_BOT_TOKEN`/`GO100_TELEGRAM_CHAT_ID`로 즉시 알림

**DB 저장 SQL:**
```sql
INSERT INTO go100_error_log
    (endpoint, status_code, error_message, traceback, request_body)
VALUES
    (:endpoint, :status_code, :error_message, :traceback, CAST(:request_body AS jsonb))
```
(asyncpg 호환: `::jsonb` 대신 `CAST(... AS jsonb)` 사용)

**Telegram 메시지 형식:**
```
🚨 [GO100 500 에러]
Endpoint: {METHOD} {path}
Status: 500
Error: {error_message}
Traceback: {last 800 chars}
```

#### `backend/migrations/065_add_error_log_table.sql`
```sql
CREATE TABLE IF NOT EXISTS go100_error_log (
    id           SERIAL PRIMARY KEY,
    endpoint     TEXT,
    status_code  INT,
    error_message TEXT,
    traceback    TEXT,
    request_body JSONB,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ... ON go100_error_log (created_at DESC);
CREATE INDEX ... ON go100_error_log (status_code);
```

### 3.2 main.py 수정

```python
# import 추가
from backend.app.middleware.error_monitor import ErrorMonitorMiddleware

# 미들웨어 등록 (InternalAPIKeyMiddleware 다음)
app.add_middleware(InternalAPIKeyMiddleware)
app.add_middleware(IPWhitelistMiddleware)
app.add_middleware(ErrorMonitorMiddleware)  # T-031
app.add_middleware(RequestLoggingMiddleware)
...
```

---

## 4. DB 마이그레이션 실행 결과

```
PGPASSWORD=... psql ... -f 065_add_error_log_table.sql
→ CREATE TABLE
→ CREATE INDEX
→ CREATE INDEX
```

테이블 구조 확인:
```
                     Table "public.go100_error_log"
    Column     |           Type           | Default
---------------+--------------------------+------------------------------------------
 id            | integer                  | nextval('go100_error_log_id_seq')
 endpoint      | text                     |
 status_code   | integer                  |
 error_message | text                     |
 traceback     | text                     |
 request_body  | jsonb                    |
 created_at    | timestamptz              | now()
Indexes:
    "go100_error_log_pkey" PRIMARY KEY
    "idx_go100_error_log_created_at" btree (created_at DESC)
    "idx_go100_error_log_status_code" btree (status_code)
```

---

## 5. 테스트 결과

### 5.1 DB 저장 테스트
```
asyncio.run(test_db())
→ (1, '/test/intentional-500', 500, datetime(2026, 3, 5, 11, 58, 0, ...))
```
**결과: PASS** ✅

### 5.2 Telegram 알림 테스트
```
Telegram 응답: 200 {"ok":true,"result":{"message_id":8525,"from":{"id":8327167593,"is_bot":true,"first_name":"Go100억",...}}}
```
**결과: PASS** ✅ — Telegram 메시지 message_id=8525 발송 확인

---

## 6. 커밋

```
[phase-2c-command-center 758dc8c7] [GO100] feat: 에러 모니터링 미들웨어 + Telegram 알림 (T-031)
 4 files changed, 170 insertions(+)
 create mode 100644 backend/app/middleware/__init__.py
 create mode 100644 backend/app/middleware/error_monitor.py
 create mode 100644 backend/migrations/065_add_error_log_table.sql
```

---

## 7. 체크포인트

- [x] 코드 레포 커밋 완료 (758dc8c7)
- [ ] project-docs 보고서 push 완료

---

## 8. 특이사항

- 마이그레이션 번호: 지시서에서 `050_`을 지정했으나 `050_*`가 이미 3개 존재하므로 충돌 방지를 위해 `065_`로 생성
- asyncpg 호환 이슈: `::jsonb` 캐스트는 asyncpg 파라미터 처리와 충돌 → `CAST(:field AS jsonb)` 패턴으로 해결
- 미들웨어 순서: `InternalAPIKeyMiddleware` 다음, `RequestLoggingMiddleware` 앞에 배치 (에러를 가능한 넓게 캐치)
