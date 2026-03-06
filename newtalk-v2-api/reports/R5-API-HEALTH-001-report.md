# R5-API-HEALTH-001 — Health Check 엔드포인트 추가

**Task ID:** T-019
**작성일:** 2026-03-05
**작성자:** Claude (Sonnet 4.6)
**우선순위:** P2-NORMAL

---

## 배경

API-SMOKE-002 스모크 테스트에서 `GET /api/health → 404` 확인.
서비스 모니터링을 위한 헬스체크 엔드포인트가 부재하여 추가 구현함.

---

## 구현 내용

### Step 1: routes/api.php 백업

```
routes/api.php.bak.20260305_201828
```

### Step 2: HealthController 생성

**파일:** `app/Http/Controllers/Api/HealthController.php`

- `index()` 메서드: 인증 불필요
- DB 연결 확인: `DB::connection()->getPdo()` + `SELECT 1`
- Redis 연결 확인: `Redis::ping()`
- 디스크 여유 공간: `disk_free_space('/')`
- 응답 형식:
  ```json
  {
    "status": "ok",
    "timestamp": "2026-03-05T11:19:04+00:00",
    "services": {
      "database": "ok",
      "redis": "ok",
      "disk_free_gb": 188.9
    }
  }
  ```
- HTTP 200 (정상) / 503 (장애)

### Step 3: 라우트 등록

**파일:** `routes/api.php`

```php
// R5-API-HEALTH-001: 헬스체크 (인증 불필요)
Route::get('health', [HealthController::class, 'index']);
```

최상단 인증 미들웨어 밖에 등록 완료.

### Step 4: 테스트

```bash
$ curl -s -w "\nHTTP_STATUS:%{http_code}" http://localhost:8080/api/health
{"status":"ok","timestamp":"2026-03-05T11:19:04+00:00","services":{"database":"ok","redis":"ok","disk_free_gb":188.9}}
HTTP_STATUS:200
```

**결과:** ✅ HTTP 200, status: ok, DB/Redis 정상

### Step 5: 프론트엔드 대시보드 뱃지 (선택 구현)

**파일:** `frontend/src/app/(admin)/admin/dashboard/page.tsx`

- `useQuery`로 `GET /api/health` 폴링 (60초 간격)
- 상태에 따른 색상 뱃지 렌더링:
  - `ok` → 초록 뱃지 "서버 정상"
  - `degraded` → 노란 뱃지 "서버 장애"
- 툴팁: DB·Redis·디스크 상세 표시

---

## 완료 기준 확인

| 항목 | 결과 |
|------|------|
| `GET /api/health → 200 + status:ok` | ✅ 확인 |
| DB/Redis 상태 포함 | ✅ database:ok, redis:ok |
| 보고서 작성 | ✅ 본 문서 |

---

## 변경 파일 목록

| 파일 | 변경 유형 |
|------|----------|
| `src/app/Http/Controllers/Api/HealthController.php` | 신규 생성 |
| `src/routes/api.php` | 라우트 추가 |
| `frontend/src/app/(admin)/admin/dashboard/page.tsx` | 헬스 뱃지 추가 |
| `docs/reports/R5-API-HEALTH-001-report.md` | 신규 생성 (본 문서) |
