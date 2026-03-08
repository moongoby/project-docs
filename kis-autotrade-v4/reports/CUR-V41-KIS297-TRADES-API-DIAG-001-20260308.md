# KIS-297: trades.html 빈화면 API 진단 보고서

**TASK_ID**: KIS-297
**PROJECT**: KIS-V41
**DATE**: 2026-03-08
**ASSIGNEE**: Cursor AI (서버 211)
**SIZE**: XS | **PRIORITY**: P0-CRITICAL
**타입**: 진단만 (코드 수정 없음)

---

[인계 확인]
직전 완료: v10.72 (AADS-178 좀비 프로세스 근본수정)
현재 단계: Phase 2c (Command Center)
CEO 지시 적용: D-001, D-007
strategy_cards: (진단 미포함)
open_positions: (진단 미포함)

---

## 1. 진단 개요

trades.html 빈화면 원인 규명을 위해 6개 진단 항목 실행. 코드 수정 없음.

---

## 2. 진단 결과 전문

### === 1. 내부 API 테스트 (직접 포트 8003) ===

```
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" http://127.0.0.1:8003/api/chart-data?symbol=005930
{"detail":"Not Found"}
HTTP:404 SIZE:22

curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" http://127.0.0.1:8003/api/stocks/search?q=samsung
{"detail":"Not Found"}
HTTP:404 SIZE:22

curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" http://127.0.0.1:8003/api/trades/unified
{"detail":"Not Found"}
HTTP:404 SIZE:22
```

**결과**: 3개 URL 모두 HTTP 404.
**원인**: 테스트 URL이 `/api/` 접두사를 사용하나, V4.1 API의 실제 경로는 `/api/v4/` 임. 또한 `/api/chart-data` 엔드포인트는 전혀 존재하지 않음.

---

### === 2. 외부 API 테스트 (Nginx 경유 HTTPS) ===

```
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" https://trading41.newtalk.kr/api/chart-data?symbol=005930
{"detail":"Not Found"}
HTTP:404 SIZE:22

curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" https://trading41.newtalk.kr/api/stocks/search?q=samsung
{"detail":"Not Found"}
HTTP:404 SIZE:22

curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" https://trading41.newtalk.kr/api/trades/unified
{"detail":"Not Found"}
HTTP:404 SIZE:22
```

**결과**: 3개 URL 모두 HTTP 404.
**원인**: Nginx는 `/api/` → 포트 8001 (레거시 서버)로 라우팅. 8001에 해당 엔드포인트 없음.
올바른 외부 경로는 `/api/v4/trades/unified`, `/api/v4/stocks/search`.

---

### === 3. Nginx 설정 확인 ===

```nginx
# /etc/nginx/sites-available/kis-autotrade 주요 내용

server {
    listen 80 / 443 ssl;
    server_name trading41.newtalk.kr;
    include /etc/nginx/internal-api-key.conf;
    # → set $internal_api_key "00000000000000000000000000000000";

    # V4 전용 — /api/v4/* 만 8003 (API 키 헤더 주입)
    location /api/v4/ {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header X-Internal-API-Key $internal_api_key;
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }

    # 레거시 API — /api/* (v1 포함) 8001
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_read_timeout 120s;
    }

    # T-281: CEO 통합 거래 뷰어 static serving
    location = /trades.html {
        alias /root/kis-autotrade-v4/frontend/static/trades.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
    location /static/ {
        alias /root/kis-autotrade-v4/frontend/static/;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
```

**결과 분석**:
- `/api/v4/` → 8003 라우팅 + `X-Internal-API-Key` 주입 ✅
- `/api/` → 8001 라우팅 (API 키 없음)
- `internal-api-key.conf` 값: `"00000000000000000000000000000000"` ✅
- `trades.html` 및 `/static/` 서빙 설정 존재 ✅

---

### === 4. 라우터 등록 확인 ===

```
grep -n "v4_trades_unified" backend/app/main.py

131: from backend.app.routers.v4_trades_unified import router as v4_trades_unified_router
439: app.include_router(v4_trades_unified_router)  # T-278: CEO 통합 거래 뷰어
```

```python
# backend/app/routers/v4_trades_unified.py 상단
router = APIRouter(prefix="/api/v4", tags=["V4 Trades Unified"])

@router.get("/trades/unified")    # → /api/v4/trades/unified
@router.get("/stocks/search")     # → /api/v4/stocks/search
```

**결과 분석**:
- v4_trades_unified_router: import ✅ (line 131), include ✅ (line 439)
- 실제 등록 경로: `/api/v4/trades/unified`, `/api/v4/stocks/search`
- prefix는 라우터 내부(`prefix="/api/v4"`)에 설정됨 — include 시 prefix 없음

---

### === 5. JS fetch URL 확인 ===

**kw-chart-data.js**: 해당 파일 존재하지 않음 (directive 언급 오류).
실제 파일 목록: kw-chart-engine.js, kw-trade-list.js, kw-markers-tooltip.js, kw-data-grid.js, kw-indicators.js

```javascript
// frontend/static/js/kw-chart-engine.js (실제 API 호출 파일)
var API_URLS = {
    trades_unified:    '/api/v4/trades/unified',    // ✅ 올바른 경로
    trade_detail:      '/api/v4/trades/{trade_id}/detail',
    chart_minute:      '/api/v4/trades/{trade_id}/chart/minute',
    chart_daily:       '/api/v4/trades/{trade_id}/chart/daily',
    stock_history:     '/api/v4/trades/stock/{stock_code}/history',
    hypothesis_matrix: '/api/v4/trades/hypothesis-matrix',
    stocks_search:     '/api/v4/stocks/search',     // ✅ 올바른 경로
};

function apiFetch(path, opts) {
    var token = localStorage.getItem('access_token') || localStorage.getItem('token') || '';
    var headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    return fetch(path, { headers: headers, ...opts });
}
```

**추가 발견**:
- trades.html은 `trades-viewer.js`를 로드하지 않음 (`kw-*` 파일들만 사용)
- `KWTradeList.setDefaultDates()`가 찾는 DOM ID: `kwFilterDateFrom`/`kwFilterDateTo`
- trades.html의 실제 DOM ID: `filter-date-from`/`filter-date-to`
- **ID 불일치**: 날짜 기본값 미설정 → 날짜 필터 없이 전체 데이터 조회 (기능 문제, 빈화면 원인 아님)

---

### === 6. claude_exec.sh 타이머 확인 ===

```bash
grep -in "size|timer|timeout|1200|2400" /root/.genspark/claude_exec.sh

10: # Usage: claude_exec.sh <directive_file> <project> <workdir> [timeout] [max_turns] [model]
184: # SIZE 기반 차등 타이머 (arg 4 미제공 시 자동 계산)
186:   MAX_TIMEOUT="$4"
188:   _SIZE=$(grep -m1 -oP '(?:^|\s)SIZE\s*:\s*\K\S+' "$DIRECTIVE_FILE" 2>/dev/null)
189:   case "${_SIZE:-}" in
190:     XS|S)  MAX_TIMEOUT=1200 ;;   # 20분
191:     M)     MAX_TIMEOUT=2400 ;;   # 40분
192:     L)     MAX_TIMEOUT=3600 ;;   # 60분
193:     XL)    MAX_TIMEOUT=5400 ;;   # 90분
194:     *)     MAX_TIMEOUT=2400 ;;   # 기본 40분
```

**결과**: KIS-297 (SIZE: XS) → `MAX_TIMEOUT=1200` (20분) 적용

---

## 3. 추가 진단 (진단 정확성 확보)

### 올바른 경로 실제 테스트

```
# Nginx 경유 (브라우저와 동일한 경로)
curl https://trading41.newtalk.kr/api/v4/trades/unified?page=1&per_page=3

HTTP:200 SIZE:20650
{
  "summary": {"total_count": 105526, "win_rate": 46.23, ...},
  "pagination": {"page": 1, "limit": 50, "total": 105526},
  "trades": [{"trade_id": "BT_211438", ...}, ...]
}

curl https://trading41.newtalk.kr/api/v4/stocks/search?q=005930
HTTP:200 → [{"stock_code":"005930","stock_name":"삼성전자","market":"KOSPI"}]

curl https://trading41.newtalk.kr/api/v4/stocks/search?q=samsung
HTTP:200 → [] (영문 검색 결과 없음, 정상)

curl https://trading41.newtalk.kr/api/v4/stocks/search?q=삼성
HTTP:400 → (빈 응답, 한글 URL 인코딩 문제 가능성)
```

### 직접 접근 (Nginx 없이) 500 오류

```
curl http://127.0.0.1:8003/api/v4/stocks/search?q=samsung
HTTP:500 → {"detail":"Internal Server Error"}

# 서버 로그:
'/api/v4/stocks/search', 500, '403: Invalid or missing X-Internal-API-Key'
fastapi.exceptions.HTTPException: 403: Invalid or missing X-Internal-API-Key
```

**분석**: `BaseHTTPMiddleware.dispatch()`에서 `HTTPException(403)`을 raise하면
FastAPI의 Exception Handler가 개입하지 못하고 500으로 변환됨.
(FastAPI 알려진 이슈: HTTPException in middleware → 500)
Nginx 경유 시에는 API 키가 정상 주입되어 이 문제 미발생.

### 서비스 포트 상태

```
ss -tlnp | grep -E "8001|8002|8003"
LISTEN  127.0.0.1:8002  (go100)
LISTEN  127.0.0.1:8003  (kis-v41-api) ✅ 정상 실행 중
LISTEN  127.0.0.1:8001  (레거시)
```

### INTERNAL_API_KEY 일치 확인

```
.env:                         INTERNAL_API_KEY=00000000000000000000000000000000
/etc/nginx/internal-api-key.conf:  set $internal_api_key "00000000000000000000000000000000";
```

**결과**: 양쪽 값 일치 ✅ — 브라우저 → Nginx → FastAPI 경로 정상 작동해야 함

---

## 4. 진단 종합

### 4.1 빈화면 원인 분석

| 항목 | 상태 | 비고 |
|------|------|------|
| API 서버 (8003) | ✅ 정상 실행 | kis-v41-api systemd 서비스 |
| Nginx → 8003 라우팅 | ✅ 정상 | /api/v4/ → 8003 |
| X-Internal-API-Key | ✅ 일치 | Nginx 주입 + .env 일치 |
| 라우터 등록 | ✅ 정상 | import + include 모두 존재 |
| /api/v4/trades/unified | ✅ HTTP 200 | 브라우저 경로 정상 |
| JS API 경로 | ✅ 올바름 | kw-chart-engine.js /api/v4/ 사용 |
| `kw-chart-data.js` | ❌ 파일 없음 | 지시서 항목 5 오류 (실제: kw-chart-engine.js) |
| KWTradeList 날짜 DOM ID | ⚠️ 불일치 | kwFilterDateFrom ≠ filter-date-from |
| 한글 stocks/search | ⚠️ HTTP 400 | URL 인코딩 문제 가능성 |
| 직접 8003 접근 (API 키 없이) | ❌ 500 | 브라우저 미해당 (Nginx 경유) |

### 4.2 핵심 발견: 빈화면은 이미 해결됨

- KIS-295 (bad34b3f) 커밋에서 API 경로 수정 완료
- `/api/v4/trades/unified` → HTTP 200, 105,526건 반환 확인
- Nginx X-Internal-API-Key 주입 정상
- **현재 브라우저 접근 시 데이터 정상 로드 예상**

### 4.3 잔여 이슈 (빈화면 직접 원인 아님)

1. **날짜 필터 기본값 미설정**: `KWTradeList.setDefaultDates()`의 DOM ID 불일치
   - 탐색: `kwFilterDateFrom` → 실제: `filter-date-from`
   - 결과: 날짜 기본값 없이 전체 조회 (105,526건 부하)

2. **한글 종목명 검색 400**: `stocks/search?q=삼성` → HTTP 400 (URL 인코딩 이슈)

3. **stock_name 미표시**: trades.html 내 일부 종목명이 stock_code와 동일 표시됨 (DB join 미완)

4. **HTTPException in middleware 500 변환**: 직접 접근 시만 해당, 브라우저 미영향

---

## 5. 결론

**진단 명령어 실행 결과**: 6개 항목 전부 완료
**빈화면 주요 원인**: KIS-295에서 이미 수정됨 (`/api/v4/` 경로 + 모듈 API 사용)
**현재 상태**: Nginx 경유 정상 작동 (HTTP 200, 105,526건)
**잔여 이슈**: 날짜 기본값 DOM ID 불일치, 한글 검색 400, stock_name null

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (진단 전용, 코드 수정 없음 — 커밋 불필요)
- [ ] project-docs 보고서 push 완료 (진행 예정)
