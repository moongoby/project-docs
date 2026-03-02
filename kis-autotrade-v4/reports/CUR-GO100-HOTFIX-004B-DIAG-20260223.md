# CUR-GO100-HOTFIX-004B — Too Many Requests + 인프라 진단 보고서

**작업일:** 2026-02-23  
**목적:** "Too Many Requests"(429) 원인 추적 및 백엔드/Nginx rate limit 확인  
**규칙:** go100_* 파일/테이블만 수정, .env/.bak 커밋 금지

---

## 1. 진단 1: 백엔드 rate limit 설정

### 1.1 slowapi/Limiter/RateLimitMiddleware

- **slowapi 미사용.** 백엔드는 **자체 Redis 기반 Rate Limiter** 사용.
- `backend/app/core/rate_limiter.py`: Redis sliding window, 429 + Retry-After 반환.
- `backend/app/core/kis_rate_limiter.py`: KIS API용 Token Bucket (글로벌/계좌별). **HTTP 429를 직접 반환하지 않음** — KIS 호출 제한용.

### 1.2 main.py 미들웨어 (역순 등록)

| 순서 | 미들웨어 |
|------|----------|
| 1 (가장 바깥) | InternalAPIKeyMiddleware |
| 2 | IPWhitelistMiddleware |
| 3 | RequestLoggingMiddleware |
| 4 | **RateLimitMiddleware** ← 429 발생 지점 |
| 5 | SecurityHeadersMiddleware |
| 6 | CORSMiddleware |

### 1.3 main.py 429/rate 관련

- **429 직접 반환:** `main.py`에는 없음. 429는 **`RateLimitMiddleware`** 에서만 반환.
- **rate_limiter_manager:** `kis_rate_limiter.rate_limiter_manager` — startup 시 초기화, KIS/KIWOOM 계좌별 쿼터. 실패 시 graceful degradation(rate limiting 비활성).

### 1.4 rate_limiter.py 요약 (429 발생 로직)

- **파일:** `backend/app/core/rate_limiter.py`
- **제한:**
  - 인증 사용자: **120 req/min** (환경변수 `RATE_LIMIT_AUTHENTICATED`)
  - 비인증: **30 req/min** (`RATE_LIMIT_ANONYMOUS`)
  - `/api/v4/kis/`, `/api/v1/kis/`: **20 req/s** (`KIS_RATE_LIMIT_PER_SECOND`)
- **제외 경로:** `/docs`, `/openapi.json`, `/health`, `/health/ping`, **`/api/go100/ai/chat`** (CUR-GO100-HOTFIX-003)
- **제외되지 않는 경로:** `/api/v1/strategy-cards`, `/api/v1/notifications/*`, `/api/v1/market/*`, `/api/v1/dashboard/*`, `/api/v1/llm/*` 등 → **분당 제한 적용**
- **제한 시:** `JSONResponse(status_code=429, content={"detail": "Too Many Requests", "retry_after": ...}, headers={"Retry-After": ...})`

**결론:** 대시보드/전략카드/LLM 등 **동시 다발 요청**이 60초 슬라이딩 윈도우 안에서 120건을 넘기면 429 발생.

---

## 2. 진단 2: Nginx 상세

### 2.1 설정 파일

- **sites-enabled:** `go100` → `/etc/nginx/sites-available/go100-domain`, `kis-autotrade` → `kis-autotrade`
- **conf.d:** 비어 있음.

### 2.2 go100 Nginx (go100.newtalk.kr)

- **업스트림:** backend 127.0.0.1:8002, frontend 127.0.0.1:3000
- **`/api/`** → go100_backend (8002), `proxy_read_timeout 300s`
- **limit_req / limit_conn / rate= / burst= / limit_req_zone:** **없음** → Nginx 레벨 rate limit 없음.

### 2.3 kis-autotrade Nginx

- `/api/v4/` → 8003, `/api/` → 8001. go100(8002)와 별도.
- Nginx rate limit 설정 없음.

### 2.4 Nginx rate limit 검색 결과

- `grep -rn "limit_req|limit_conn|..." /etc/nginx/` → **매칭 없음.**  
→ **429는 전부 백엔드(8002) RateLimitMiddleware에서 발생.**

### 2.5 Nginx 로그

- **error.log:** `upstream prematurely closed connection` — `/api/v1/notifications/stream` SSE 연결 종료 다수. 429와 직접 무관.
- **access.log 429 (최근):**  
  - **시간대:** 2026-02-23 11:26:50 ~ 11:27:29 (동일 IP [CDN-IP-3])
  - **경로:**  
    - `GET /api/v1/strategy-cards`  
    - `GET /api/v1/notifications/unread-count`  
    - `GET /api/v1/notifications/stream`  
    - `GET /api/v1/market/rankings?type=volume&market=kospi`  
    - `GET /api/v1/market/rankings?type=change_rate&market=kospi`  
    - `GET /api/v1/market/themes`  
    - `GET /api/v1/dashboard/summary`  
    - `GET /api/v1/llm/usage`  
    - `GET /api/v1/llm/sessions`  
  - **응답:** 429, 47바이트 (JSON `{"detail":"Too Many Requests", ...}`)

---

## 3. 진단 3: 직접 API 429 테스트

### 3.1 /health 연속 10회

```
health 1: 200 … health 10: 200
```

- `/health`는 **EXEMPT_PATHS**에 있어 rate limit 적용 안 됨 → 429 없음.

### 3.2 LLM(go100 AI) rate limit

- `backend/app/services/go100/ai/llm_client.py`: `RETRYABLE_STATUS = (429, 500, 503)` — 외부 LLM API 429 시 재시도.
- go100 AI 서비스 내부에서 **429를 클라이언트에게 반환하는 코드는 없음.**  
→ 사용자에게 보이는 429는 **전역 RateLimitMiddleware** 때문.

### 3.3 journalctl (go100, 최근 1시간)

- `grep -i "429|too.many|rate"` → **429/Too Many/rate 문자열 로그 없음.**  
- 미들웨어는 429 응답만 반환하고 별도 로그를 남기지 않는 것으로 보임.

---

## 4. 진단 4: 프론트엔드 "Too Many Requests" 표시

### 4.1 429/Too Many/rate 검색

- **위치:** `frontend/src/lib/api/client.ts`
  - 주석: `401/403/429/500/네트워크/타임아웃 + 토스트`
  - **67~73행:** `status === 429` 시  
    `showToast(serverMsg || "요청이 너무 많습니다. 잠시 후 다시 시도해주세요", undefined, "destructive")`

### 4.2 toast/notification

- 429 전용 토스트는 **client.ts 인터셉터** 한 곳에서만 처리.

### 4.3 API interceptor 429

- **client.ts:** `apiClient.interceptors.response.use` → 429 시 토스트 후 `Promise.reject(err)`.
- **go100Api.ts:** `go100Client`는 **401만** 처리하고 **429는 처리하지 않음.**  
  → `/api/go100/*` 호출이 같은 호스트(8002)의 다른 라우트로 가면, 실제 요청은 `apiClient`가 아닌 `go100Client`로 나갈 수 있음.  
  → **dashboard/strategy-cards** 등은 `apiClient`(baseURL 8002) 사용 시 429 시 client.ts에서 토스트 표시.

---

## 5. 종합 결론 및 권장 사항

### 5.1 429 원인

| 구분 | 내용 |
|------|------|
| **발생 위치** | 백엔드(8002) **RateLimitMiddleware** (`backend/app/core/rate_limiter.py`) |
| **Nginx** | rate limit 없음. 429는 백엔드만 반환. |
| **트리거** | 대시보드/전략카드/LLM 페이지 진입 시 **동시 다수 요청** (strategy-cards, notifications, market, dashboard/summary, llm/sessions 등)이 **60초 슬라이딩 윈도우 120건**을 초과 |

### 5.2 FE 표시

- **표시 위치:** `frontend/src/lib/api/client.ts` 429 분기 → 토스트 "요청이 너무 많습니다. 잠시 후 다시 시도해주세요".

### 5.3 권장 조치 (go100_* 범위 내)

1. **백엔드 (rate_limiter.py)**  
   - go100 대시/전략카드용 **읽기 전용·고빈도 경로**를 제외 목록에 추가 검토:  
     예: `/api/v1/strategy-cards`(GET), `/api/v1/notifications/unread-count`, `/api/v1/market/rankings`, `/api/v1/market/themes`, `/api/v1/dashboard/summary`, `/api/v1/llm/usage`, `/api/v1/llm/sessions`  
     → **제외 시** 429 감소하나, 악의적 폭주 시 무제한 요청 가능하므로 **일부만 제외** 또는 **상한 완화(예: 120→240)** 중 선택.
2. **제한 완화**  
   - `RATE_LIMIT_AUTHENTICATED` 120 → 240 등으로 상향 (환경변수 또는 기본값 수정).
3. **FE**  
   - 429 수신 시 **Retry-After** 있으면 해당 초 후 재시도 또는 안내 문구에 "N초 후 재시도" 표시 (선택).
4. **Nginx**  
   - 현재 429 원인 아님. 필요 시 악성 트래픽 방지용으로만 `limit_req_zone` 등 추가 검토.

---

## 6. 진단 명령 요약

```bash
# 백엔드 rate limit
grep -rn "slowapi|Limiter|RateLimit|rate_limit|throttle" backend/app/ --include="*.py"
# → kis_rate_limiter.py, rate_limiter.py

# main.py 미들웨어
grep -n "middleware|add_middleware|RateLimit" backend/app/main.py

# Nginx
ls -la /etc/nginx/sites-enabled/ /etc/nginx/conf.d/
grep -rn "limit_req|limit_conn|rate=" /etc/nginx/  # 없음

# 429 접근 로그
grep " 429 " /var/log/nginx/access.log | tail -20

# FE 429 표시
grep -rn "429|Too Many" frontend/src --include="*.ts" --include="*.tsx"
# → frontend/src/lib/api/client.ts
```

---

**보고서 끝.**
