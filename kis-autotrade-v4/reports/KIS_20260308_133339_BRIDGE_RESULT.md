---
project: KIS-V41
task_id: KIS-297
completed_at: 2026-03-08T13:55:00+09:00
---

# KIS-297 RESULT: trades.html 빈화면 API 진단 완료

## 실행한 모든 내용과 결과 (원문)

---

### === 1. 내부 API 테스트 ===

**명령어:**
```
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" http://127.0.0.1:8003/api/chart-data?symbol=005930 | tail -5
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" http://127.0.0.1:8003/api/stocks/search?q=samsung | tail -5
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" http://127.0.0.1:8003/api/trades/unified | tail -5
```

**결과:**
```
{"detail":"Not Found"}
HTTP:404 SIZE:22
---
{"detail":"Not Found"}
HTTP:404 SIZE:22
---
{"detail":"Not Found"}
HTTP:404 SIZE:22
```

---

### === 2. 외부 API 테스트 ===

**명령어:**
```
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" https://trading41.newtalk.kr/api/chart-data?symbol=005930 | tail -5
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" https://trading41.newtalk.kr/api/stocks/search?q=samsung | tail -5
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" https://trading41.newtalk.kr/api/trades/unified | tail -5
```

**결과:**
```
{"detail":"Not Found"}
HTTP:404 SIZE:22
---
{"detail":"Not Found"}
HTTP:404 SIZE:22
---
{"detail":"Not Found"}
HTTP:404 SIZE:22
```

---

### === 3. Nginx 설정 확인 ===

**명령어:**
```
grep -A3 "chart-data|stocks|trades" /etc/nginx/sites-available/kis-autotrade
cat /etc/nginx/sites-available/kis-autotrade
```

**결과 (전체 설정):**
```nginx
# KIS AutoTrade 웹 플랫폼 (211 서버)
# CURSOR-EXEC-FIX-NGINX-ROUTES-20260218: /api/v4/* → 8003, /api/* → 8001
# SVC-RESOLVE 2026-02-21: V4.1 API 8002→8003 (go100이 8002 사용)
# FIX-LIVE-TRADING-20260303: /api/v1/live-trading/ → 8003 (V4.1 mock trades 데이터 연결)
# T-281-20260307: trades.html + /static/ 서빙 추가

server {
    listen 80;
    server_name _ v4.trading.newtalk.kr trading.newtalk.kr trading41.newtalk.kr;
    include /etc/nginx/internal-api-key.conf;

    location /api/v4/ {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Internal-API-Key $internal_api_key;
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    location /manager/ {
        alias /root/kis-autotrade-v4/v41_manager/;
        autoindex off;
        default_type application/json;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Access-Control-Allow-Origin "*";
        try_files $uri =404;
    }

    location = /trades.html {
        alias /root/kis-autotrade-v4/frontend/static/trades.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location /static/ {
        alias /root/kis-autotrade-v4/frontend/static/;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 443 ssl;
    server_name trading41.newtalk.kr;
    include /etc/nginx/internal-api-key.conf;
    ssl_certificate /etc/letsencrypt/live/trading41.newtalk.kr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trading41.newtalk.kr/privkey.pem;
    # ... (동일한 location 블록 반복)
    location /api/v4/ {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header X-Internal-API-Key $internal_api_key;
        ...
    }
    location /api/ { proxy_pass http://127.0.0.1:8001; ... }
    location = /trades.html { alias /root/kis-autotrade-v4/frontend/static/trades.html; }
    location /static/ { alias /root/kis-autotrade-v4/frontend/static/; }
}
```

**내부 API 키 설정:**
```
cat /etc/nginx/internal-api-key.conf
→ set $internal_api_key "00000000000000000000000000000000";
```

---

### === 4. 라우터 등록 확인 ===

**명령어:**
```
grep -rn "chart.data|stocks/search|trades/unified" /root/kis-autotrade-v4/backend/app/routers/
grep -rn "v4_trades_unified" /root/kis-autotrade-v4/backend/app/main.py
grep -r "include_router" /root/kis-autotrade-v4/backend/app/main.py
```

**결과:**
```
/root/kis-autotrade-v4/backend/app/routers/v4_trades_unified.py:3:GET /api/v4/trades/unified
/root/kis-autotrade-v4/backend/app/routers/v4_trades_unified.py:9:GET /api/v4/stocks/search
/root/kis-autotrade-v4/backend/app/routers/v4_trades_unified.py:64:@router.get("/trades/unified")
/root/kis-autotrade-v4/backend/app/routers/v4_trades_unified.py:843:@router.get("/stocks/search")

main.py:
131: from backend.app.routers.v4_trades_unified import router as v4_trades_unified_router  # T-278
439: app.include_router(v4_trades_unified_router)  # T-278: CEO 통합 거래 뷰어

# v4_trades_unified.py 라우터 정의:
router = APIRouter(prefix="/api/v4", tags=["V4 Trades Unified"])

# include_router 전체 목록 (발췌):
app.include_router(v4_system.router, prefix="/api/v4")
app.include_router(v4_trading.router, prefix="/api/v4")
app.include_router(v4_backtest.router, prefix="/api/v4")
app.include_router(v4_auth.router, prefix="/api/v4")
app.include_router(v4_email.router, prefix="/api/v4")
app.include_router(v4_ai_trading.router, prefix="/api/v4")
app.include_router(v4_orders.router, prefix="/api/v4")
app.include_router(v4_trades_unified_router)  # ← prefix 없음 (라우터 내부에 있음)
```

---

### === 5. JS fetch URL 확인 ===

**명령어:**
```
ls /root/kis-autotrade-v4/frontend/static/js/
grep -rn "fetch|api/" /root/kis-autotrade-v4/frontend/static/js/kw-chart-data.js | head -20
```

**결과:**
```
# 파일 목록:
backtest-dashboard.js
dashboard.js
data-collection.js
desk2-backtest.js
desk2-live.js
kw-chart-engine.js
kw-data-grid.js
kw-indicators.js
kw-markers-tooltip.js
kw-trade-list.js
trades-viewer.js

# kw-chart-data.js: 존재하지 않음
```

**kw-chart-engine.js (실제 API 호출 파일) 내용:**
```javascript
// frontend/static/js/kw-chart-engine.js:10-17
var API_URLS = {
    trades_unified:    '/api/v4/trades/unified',
    trade_detail:      '/api/v4/trades/{trade_id}/detail',
    chart_minute:      '/api/v4/trades/{trade_id}/chart/minute',
    chart_daily:       '/api/v4/trades/{trade_id}/chart/daily',
    stock_history:     '/api/v4/trades/stock/{stock_code}/history',
    hypothesis_matrix: '/api/v4/trades/hypothesis-matrix',
    stocks_search:     '/api/v4/stocks/search',
};

// kw-chart-engine.js:44-48
function apiFetch(path, opts) {
    opts = opts || {};
    var token = getToken();  // localStorage.getItem('access_token') || ...
    var headers = Object.assign({ 'Content-Type': 'application/json' },
      token ? { 'Authorization': 'Bearer ' + token } : {});
    return fetch(path, Object.assign({ headers: headers }, opts));
}
```

**trades.html 스크립트 로딩:**
```html
<script src="/static/js/kw-indicators.js"></script>
<script src="/static/js/kw-chart-engine.js"></script>
<script src="/static/js/kw-trade-list.js"></script>
<script src="/static/js/kw-markers-tooltip.js"></script>
<script src="/static/js/kw-data-grid.js"></script>
<!-- trades-viewer.js는 로드하지 않음 -->
```

---

### === 6. claude_exec.sh 타이머 확인 ===

**명령어:**
```
grep -i "size|timer|timeout|1200|2400" /root/.genspark/claude_exec.sh | head -10
```

**결과:**
```
10:# Usage: claude_exec.sh <directive_file> <project> <workdir> [timeout] [max_turns] [model]
184:# SIZE 기반 차등 타이머 (arg 4 미제공 시 자동 계산)
186:  MAX_TIMEOUT="$4"
188:  _SIZE=$(grep -m1 -oP '(?:^|\s)SIZE\s*:\s*\K\S+' "$DIRECTIVE_FILE" 2>/dev/null | tr '[:lower:]' '[:upper:]' | head -1)
189:  case "${_SIZE:-}" in
190:    XS|S)  MAX_TIMEOUT=1200 ;;
191:    M)     MAX_TIMEOUT=2400 ;;
192:    L)     MAX_TIMEOUT=3600 ;;
193:    XL)    MAX_TIMEOUT=5400 ;;
194:    *)     MAX_TIMEOUT=2400 ;;
```

→ KIS-297 (SIZE: XS) 타이머: 1200초 (20분)

---

### === 추가 진단 (진단 정확성 확보) ===

**Nginx 경유 올바른 경로 테스트:**
```
curl -s -w "\nHTTP:%{http_code} SIZE:%{size_download}" "https://trading41.newtalk.kr/api/v4/trades/unified?page=1&per_page=3"

결과: HTTP:200 SIZE:20650
{
  "summary": {"total_count": 105526, "win_rate": 46.23, "profit_factor": 2.1033, ...},
  "pagination": {"page": 1, "limit": 50, "total": 105526, "pages": 2111},
  "trades": [{"trade_id":"BT_211438","channel":"BT","desk_id":2,...}, ...]
}

curl "https://trading41.newtalk.kr/api/v4/stocks/search?q=005930"
HTTP:200 → [{"stock_code":"005930","stock_name":"삼성전자","market":"KOSPI"}]

curl "https://trading41.newtalk.kr/api/v4/stocks/search?q=samsung"
HTTP:200 → [] (영문 검색 결과 없음)

curl "https://trading41.newtalk.kr/api/v4/stocks/search?q=삼성"
HTTP:400 → (빈 응답 — 한글 URL 인코딩 이슈 가능성)
```

**직접 접근 500 오류 (Nginx 없이):**
```
curl http://127.0.0.1:8003/api/v4/stocks/search?q=samsung
HTTP:500 → {"detail":"Internal Server Error"}

# 서버 로그 원문:
'/api/v4/stocks/search', 500, '403: Invalid or missing X-Internal-API-Key',
'fastapi.exceptions.HTTPException: 403: Invalid or missing X-Internal-API-Key'
```

**원인**: BaseHTTPMiddleware에서 HTTPException raise → FastAPI ExceptionHandler 미개입 → 500 반환
(브라우저는 Nginx 경유이므로 미해당)

**INTERNAL_API_KEY 일치 확인:**
```
.env:                          INTERNAL_API_KEY=00000000000000000000000000000000
/etc/nginx/internal-api-key.conf:  set $internal_api_key "00000000000000000000000000000000";
→ 완전 일치 ✅
```

**서비스 포트 상태:**
```
ss -tlnp | grep -E "8001|8002|8003"
LISTEN  127.0.0.1:8002  (go100)
LISTEN  127.0.0.1:8003  (kis-v41-api) ✅
LISTEN  127.0.0.1:8001  (레거시)
```

**KWTradeList.setDefaultDates() DOM ID 불일치:**
```javascript
// kw-trade-list.js:182-195
function setDefaultDates() {
    var elFrom = document.getElementById('kwFilterDateFrom');  // 찾는 ID
    var elTo   = document.getElementById('kwFilterDateTo');    // 찾는 ID
    ...
}

// trades.html의 실제 DOM ID:
<input type="date" id="filter-date-from">   // ← 불일치
<input type="date" id="filter-date-to">     // ← 불일치
```
→ 날짜 기본값 미설정 (함수가 null 체크 후 조용히 실패), 빈화면 직접 원인 아님

---

## 최종 판단

| 항목 | 결과 |
|------|------|
| 지시서 테스트 URL 1~6 | 모두 404 (경로 오류: /api/ vs /api/v4/) |
| /api/chart-data 엔드포인트 | 존재하지 않음 |
| 올바른 /api/v4/trades/unified | HTTP 200, 105,526건 정상 |
| Nginx 라우팅 | 정상 (/api/v4/ → 8003 + API 키 주입) |
| 라우터 등록 | 정상 (import + include 모두 존재) |
| INTERNAL_API_KEY | 일치 (nginx = fastapi) |
| JS API 경로 | 정상 (kw-chart-engine.js /api/v4/ 사용) |
| kw-chart-data.js | 존재하지 않음 |
| 빈화면 결론 | KIS-295에서 이미 수정됨, 현재 정상 |
| 잔여 이슈 | 날짜 ID 불일치 / 한글검색 400 / stock_name null |

---

## 생성 파일

- 로컬 보고서: /root/kis-autotrade-v4/report/v41/CUR-V41-KIS297-TRADES-API-DIAG-001-20260308.md
- project-docs push: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-KIS297-TRADES-API-DIAG-001-20260308.md
- HTTP 200 확인: ✅
- HANDOVER.md 업데이트: v10.73 (커밋 86d9f15)
- HANDOVER.md HTTP 200 확인: ✅

## 체크포인트
- [x] 코드 레포 커밋 완료 (진단 전용 — 코드 수정 없으므로 별도 커밋 불필요)
- [x] project-docs 보고서 push 완료 (GitHub raw URL HTTP 200 확인)

HANDOVER.md 업데이트 완료: 86d9f15
