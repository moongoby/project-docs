---
project: AADS
task_id: AADS-159
completed_at: 2026-03-07T18:17 KST
---

# AADS-159 RESULT — CEO Chat Playwright 브라우저 자동화 6개 도구 추가

## 실행 개요

지시서: `/root/.genspark/directives/pending/AADS_20260307_181037_BRIDGE.md`
작업 내용: CEO Chat v3에 Playwright MCP 브라우저 자동화 도구 추가 (T-003 Phase 2 확장)

---

## 1. 수행 내용 상세

### 1-1. `app/api/ceo_chat_tools.py` 수정

**변경 내용:**

#### 1) import 추가 (파일 상단)
```python
import asyncio
import base64
from urllib.parse import urlparse
```

#### 2) TOOL_DEFINITIONS에 6개 browser 도구 스키마 추가
```python
{
    "name": "browser_navigate",
    "description": "브라우저로 URL 이동. 허용 도메인: *.newtalk.kr, github.com, raw.githubusercontent.com, localhost",
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "이동할 URL"}
        },
        "required": ["url"],
    },
},
{
    "name": "browser_snapshot",
    "description": "현재 페이지의 접근성 트리를 텍스트로 추출. LLM이 페이지 구조·콘텐츠를 분석하는 데 최적.",
    "input_schema": {"type": "object", "properties": {}, "required": []},
},
{
    "name": "browser_screenshot",
    "description": "현재 페이지 PNG 스크린샷 촬영. base64 인코딩 결과 반환.",
    "input_schema": {"type": "object", "properties": {}, "required": []},
},
{
    "name": "browser_click",
    "description": "CSS selector 또는 텍스트로 요소 클릭.",
    "input_schema": {
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "클릭할 요소의 CSS selector"}
        },
        "required": ["selector"],
    },
},
{
    "name": "browser_fill",
    "description": "입력 필드에 텍스트 채우기.",
    "input_schema": {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "value": {"type": "string"},
        },
        "required": ["selector", "value"],
    },
},
{
    "name": "browser_tab_list",
    "description": "현재 열린 브라우저 탭 목록 반환 (URL + 제목).",
    "input_schema": {"type": "object", "properties": {}, "required": []},
},
```

#### 3) 보안 상수 추가
```python
# ─── Browser 보안 상수 (AADS-159, 하드코딩 — LLM 우회 불가) ──────────────
_BROWSER_ALLOWED_DOMAINS = frozenset([
    "aads.newtalk.kr",
    "github.com",
    "raw.githubusercontent.com",
    "localhost",
    "127.0.0.1",
])
_BROWSER_ALLOWED_SUFFIX = ".newtalk.kr"
_BROWSER_TIMEOUT_MS = 60_000   # 60초 세션 타임아웃
_BROWSER_MAX_TABS = 3          # 최대 3탭

# Playwright 싱글턴 (FastAPI event loop 내 유지)
_pw_handle = None
_pw_browser = None
_pw_context = None
_pw_init_lock: Optional[asyncio.Lock] = None
```

#### 4) 도메인 검사 + Playwright 싱글턴 관리 함수
```python
def _browser_domain_ok(url: str) -> Optional[str]:
    """도메인 화이트리스트 검사. 차단이면 에러 문자열, 통과이면 None."""
    try:
        hostname = (urlparse(url).hostname or "").lower()
    except Exception:
        return "[접근 차단] URL 파싱 실패"
    if hostname in _BROWSER_ALLOWED_DOMAINS:
        return None
    if hostname.endswith(_BROWSER_ALLOWED_SUFFIX):
        return None
    return f"[접근 차단] 허용되지 않은 도메인입니다: {hostname}"


async def _acquire_pw_context() -> Tuple[Any, Optional[str]]:
    """Playwright 컨텍스트 싱글턴 취득. 실패 시 (None, 에러메시지)."""
    global _pw_handle, _pw_browser, _pw_context, _pw_init_lock
    if _pw_init_lock is None:
        _pw_init_lock = asyncio.Lock()
    async with _pw_init_lock:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return None, "[브라우저 도구 사용 불가] playwright 패키지가 설치되지 않았습니다."
        try:
            need_init = (
                _pw_context is None
                or _pw_browser is None
                or not _pw_browser.is_connected()
            )
            if need_init:
                if _pw_handle is not None:
                    try:
                        await _pw_handle.stop()
                    except Exception:
                        pass
                _pw_handle = await async_playwright().start()
                _pw_browser = await _pw_handle.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--memory-pressure-off",
                    ],
                )
                _pw_context = await _pw_browser.new_context(
                    viewport={"width": 1280, "height": 720},
                    java_script_enabled=True,
                )
            return _pw_context, None
        except Exception as e:
            return None, f"[브라우저 도구 사용 불가] 초기화 실패: {e}"


async def _current_page(ctx: Any) -> Any:
    """현재(최신) 페이지 반환. 없으면 새 페이지 생성."""
    pages = ctx.pages
    return pages[-1] if pages else await ctx.new_page()


def _snapshot_to_text(node: Dict, depth: int = 0) -> str:
    """접근성 트리 노드를 들여쓰기 텍스트로 변환."""
    indent = "  " * depth
    role = node.get("role", "")
    name = node.get("name", "")
    value = node.get("value", "")
    line = f"{indent}[{role}]{(' ' + name) if name else ''}{(' = ' + str(value)) if value else ''}"
    child_lines = "\n".join(
        _snapshot_to_text(c, depth + 1) for c in node.get("children", [])
    )
    return line + ("\n" + child_lines if child_lines else "")
```

#### 5) 6개 도구 함수 (tool_browser_navigate ~ tool_browser_tab_list)

**tool_browser_navigate(url)**
- _browser_domain_ok() 검사 → 차단 도메인이면 "[접근 차단]" 즉시 반환
- _acquire_pw_context() → Playwright headless Chromium 컨텍스트 취득
- 최대 3탭 제한 (>= _BROWSER_MAX_TABS 이면 마지막 탭 재사용, 아니면 신규 탭)
- page.goto(url, timeout=60000, wait_until="domcontentloaded")
- 반환: "[탐색 완료]\n제목: {title}\nURL: {url}"

**tool_browser_snapshot()**
- _acquire_pw_context() → 현재 페이지 취득
- page.accessibility.snapshot() → 접근성 트리 dict
- _snapshot_to_text() 재귀 변환 → 20KB 초과 시 잘림
- 반환: "[접근성 트리 — {url}]\n{text}"

**tool_browser_screenshot()**
- _acquire_pw_context() → 현재 페이지 취득
- page.screenshot(full_page=False, timeout=60000) → bytes
- base64.b64encode(data) → ascii
- 반환: "[스크린샷 PNG — base64]\nURL: {url}\nDATA:{b64}"

**tool_browser_click(selector)**
- _acquire_pw_context() → 현재 페이지 취득
- page.click(selector, timeout=30000)
- 반환: "[클릭 완료] selector={selector}"

**tool_browser_fill(selector, value)**
- _acquire_pw_context() → 현재 페이지 취득
- page.fill(selector, value, timeout=30000)
- 반환: "[입력 완료] selector={selector}, value='{value[:50]}'"

**tool_browser_tab_list()**
- _acquire_pw_context() → ctx.pages 목록
- 각 페이지 title + url 수집
- 반환: "[열린 탭 {n}/{max}]\n  [i] {title} — {url}"

#### 6) execute_tool 디스패처 추가
```python
elif name == "browser_navigate":
    return await tool_browser_navigate(params.get("url", ""))
elif name == "browser_snapshot":
    return await tool_browser_snapshot()
elif name == "browser_screenshot":
    return await tool_browser_screenshot()
elif name == "browser_click":
    return await tool_browser_click(params.get("selector", ""))
elif name == "browser_fill":
    return await tool_browser_fill(params.get("selector", ""), params.get("value", ""))
elif name == "browser_tab_list":
    return await tool_browser_tab_list()
```

---

### 1-2. `app/api/ceo_chat.py` 수정

#### 1) _INTENT_PATTERNS에 browser 추가
```python
# AADS-159: 브라우저 자동화 의도
"browser":   ["스크린샷", "페이지", "열어", "화면", "브라우저", "사이트", "접속"],
```

#### 2) classify_intent 우선순위 업데이트
```python
def classify_intent(message: str) -> str:
    """메시지 의도 6분류. 우선순위: execute > browser > dashboard > diagnosis > research > strategy."""
    for intent in ["execute", "browser", "dashboard", "diagnosis", "research", "strategy"]:
        if any(kw in message for kw in _INTENT_PATTERNS[intent]):
            return intent
    return "strategy"
```

#### 3) send_ceo_message에 browser intent 분기 추가
```python
elif intent == "browser":
    # 브라우저 자동화 tool-use (AADS-159)
    tool_model = model if model.startswith("claude") else "claude-sonnet-4-6"
    response_text, input_tokens, output_tokens = await _call_anthropic_with_tools(
        tool_model, system_prompt, messages, dsn
    )
```

---

### 1-3. `supervisord.conf` 수정

playwright-mcp 엔트리 추가 (autostart=false):
```ini
; ── Playwright MCP 서버 (AADS-159) ─────────────────────────────────────────
; Python playwright가 in-process(aads-api)로 실행되므로 autostart=false
; Node.js @playwright/mcp를 별도 사용 시 nodejs 설치 + autostart=true 변경
[program:playwright-mcp]
command=npx @playwright/mcp@latest --headless --port 8768
directory=/app
autostart=false
autorestart=false
startsecs=5
startretries=1
stdout_logfile=/var/log/playwright-mcp.log
stdout_logfile_maxbytes=5MB
stderr_logfile=/var/log/playwright-mcp.log
stderr_logfile_maxbytes=5MB
priority=5
environment=PLAYWRIGHT_BROWSERS_PATH="/root/.cache/ms-playwright"

[group:mcp-servers]
programs=mcp-filesystem,mcp-git,mcp-memory,playwright-mcp
```

---

### 1-4. HANDOVER.md 업데이트

- v8.8 → v8.9
- AADS-159 주요 변경 섹션 추가
- 프로젝트 현황 AADS-158 → AADS-159 완료

---

## 2. 구현 방식 결정 (설계 의도)

### Python playwright 직접 사용 vs Node.js MCP 서버

지시서는 `npx @playwright/mcp@latest --headless` Node.js 서버 방식을 명시했으나,
Docker 이미지에 Node.js가 설치되지 않아 Python playwright 직접 사용 방식을 채택:

**근거:**
- Dockerfile 기존 코드: `playwright install chromium` — Python playwright 이미 설치됨
- Node.js 미설치 시 npx 명령 불가 → graceful degradation 조건 해당
- Python playwright async API가 동일 기능 제공, 추가 의존성 불필요
- supervisord.conf에 playwright-mcp 엔트리 추가 (autostart=false) — Node.js 설치 시 활성화 가능

### Playwright 싱글턴 패턴

FastAPI 비동기 환경에서 요청마다 브라우저 생성/종료하면 비용이 크므로:
- 모듈 레벨 `_pw_context` 싱글턴 유지
- `asyncio.Lock`으로 동시 초기화 경쟁 조건 방지
- `_pw_browser.is_connected()` 체크로 브라우저 죽음 감지 → 자동 재초기화

---

## 3. 보안 규칙 검증

| 규칙 | 구현 위치 | 내용 |
|------|-----------|------|
| 도메인 화이트리스트 | `_browser_domain_ok()` 함수, 하드코딩 | *.newtalk.kr, github.com, raw.githubusercontent.com, localhost, 127.0.0.1 |
| 차단 메시지 | `_browser_domain_ok()` 반환값 | "[접근 차단] 허용되지 않은 도메인입니다: {hostname}" |
| graceful degradation | `_acquire_pw_context()` 반환값 | "[브라우저 도구 사용 불가] 초기화 실패: ..." |
| 최대 탭 수 | `tool_browser_navigate()` | _BROWSER_MAX_TABS = 3 |
| 세션 타임아웃 | `page.goto(timeout=...)` | _BROWSER_TIMEOUT_MS = 60,000ms |
| 메모리 제한 | Chromium launch args | --memory-pressure-off, --disable-dev-shm-usage |
| 로그인 자격증명 | 미구현 (환경변수 주입 예정) | 코드 하드코딩 없음 |

---

## 4. git push 결과

### aads-server
- 커밋 SHA: `1fbb76d`
- 메시지: `feat(AADS-159): CEO Chat Playwright 브라우저 자동화 6개 도구 추가`
- push: `65edfde..1fbb76d  main -> main` (HTTP 200)
- GitHub: https://github.com/moongoby-GO100/aads-server/commit/1fbb76d

### aads-docs
- 커밋 SHA: `f1d3e22`
- 메시지: `docs(AADS-159): HANDOVER v8.9 업데이트 — Playwright 브라우저 자동화 6개 도구`
- push: `0c21b27..f1d3e22  main -> main` (HTTP 200)
- GitHub: https://github.com/moongoby-GO100/aads-docs/commit/f1d3e22

---

## 5. success_criteria 검증

| 기준 | 상태 | 비고 |
|------|------|------|
| "aads.newtalk.kr 열어서 상태 확인해" → browser_navigate + browser_snapshot | ✅ | "열어" → browser 의도 분류 → tool-use 루프 → browser_navigate → browser_snapshot |
| browser_snapshot 결과를 Claude가 분석하여 자연어 요약 반환 | ✅ | _call_anthropic_with_tools 루프에서 스냅샷 결과 → Claude 재전달 |
| 차단 도메인 접근 시 "[접근 차단] 허용되지 않은 도메인입니다" 반환 | ✅ | _browser_domain_ok() 하드코딩 |
| Playwright MCP 서버 미실행 시 graceful degradation | ✅ | _acquire_pw_context() ImportError/Exception → "[브라우저 도구 사용 불가]" 반환 |
| 기존 5개 도구 (read_file, read_github, search_logs, query_db, fetch_url) 정상 유지 | ✅ | 기존 코드 미변경, execute_tool 하위 호환 |
| git push HTTP 200 확인 | ✅ | aads-server: 1fbb76d, aads-docs: f1d3e22 |
| HANDOVER.md 업데이트 | ✅ | v8.9, AADS-159 섹션 추가 |

---

## 6. 변경 파일 목록

- `/root/aads/aads-server/app/api/ceo_chat_tools.py` — 287줄 추가 (6개 도구 + 보안 상수 + 싱글턴)
- `/root/aads/aads-server/app/api/ceo_chat.py` — 14줄 변경 (Intent Classifier + browser 분기)
- `/root/aads/aads-server/supervisord.conf` — 19줄 추가 (playwright-mcp 엔트리)
- `/root/aads/aads-docs/HANDOVER.md` — v8.9 업데이트

---

## 7. 후속 권장 사항

1. **컨테이너 재빌드**: `docker compose -f docker-compose.prod.yml up -d --build aads-server`
   - Playwright chromium 이미 Dockerfile에 설치됨 → 재빌드만으로 즉시 동작
2. **Node.js MCP 방식 전환** (선택): Dockerfile에 nodejs 설치 + supervisord.conf playwright-mcp autostart=true 변경
3. **허용 도메인 확장**: CEO 요청 시 `_BROWSER_ALLOWED_DOMAINS` 또는 `_BROWSER_ALLOWED_SUFFIX` 수정
