---
project: AADS
task_id: AADS-186E-1
completed_at: 2026-03-09T09:35:00+09:00
---

# AADS-186E-1 실행 결과 보고서

## 지시서 정보
- TASK_ID: AADS-186E-1
- TITLE: 검색·크롤링 완전 해방 — Jina Reader + Crawl4AI + deep_crawl 도구
- PRIORITY: P1-HIGH
- SIZE: M

---

## 실행 내역 (원문 그대로)

### 1. 파일 탐색 및 상태 확인

```
find /root/.genspark -name "*BRIDGE*" → running/AADS_20260309_084851_BRIDGE.md 발견
```

지시서 경로: `/root/.genspark/directives/running/AADS_20260309_084851_BRIDGE.md`

기존 파일 확인 결과:
- `app/services/jina_reader_service.py` → **이미 존재** (이전 작업에서 생성됨)
- `app/services/crawl4ai_service.py` → **이미 존재** (이전 작업에서 생성됨)
- `app/services/deep_crawl_service.py` → **미존재** — 신규 생성 필요
- `docker-compose.crawl4ai.yml` → **미존재** — 신규 생성 필요
- `tests/test_crawl_tools.py` → **미존재** — 신규 생성 필요
- `tool_registry.py` 에 crawl 도구 → **이미 추가됨** (tool_registry 확인 시 이미 3개 도구 존재)
- `tool_executor.py` 에 실행기 → **미존재** — 추가 필요
- `intent_router.py` 에 url_read/deep_crawl → **미존재** — 추가 필요

`httpx>=0.28.0` — pyproject.toml에 이미 존재, 별도 추가 불필요

---

### 2. deep_crawl_service.py 신규 생성

파일 경로: `/root/aads/aads-server/app/services/deep_crawl_service.py`

구현 내용:
- `DeepCrawlService` 클래스
- `research_crawl(query, max_pages=5, summarize=True)` — 5단계 파이프라인
  - Step 1: `_search()` — Brave API → URL 목록 최대 max_pages개
  - Step 2: `_crawl_all()` — asyncio.gather 병렬 크롤링 (Jina → Crawl4AI 폴백)
  - Step 3: `_summarize_pages()` — Gemini Flash로 각 페이지 5000토큰 요약
  - Step 4: `_synthesize()` — Claude Sonnet으로 전체 종합 분석
  - Step 5: 인용 생성 (url, title, excerpt 300자)
- 총 결과 최대 15000 토큰
- `_llm_call()` — LiteLLM 경유 통일 호출
- `@dataclass CrawledPage` / `DeepCrawlResult`

```bash
cat > /root/aads/aads-server/app/services/deep_crawl_service.py << 'PYEOF'
...
EXIT:0
```

---

### 3. tool_registry.py — crawl 그룹 도구 3개 (이미 존재 확인)

확인 결과 tool_registry.py에 이미 다음이 추가되어 있었음:

```python
# ── crawl 그룹 (AADS-186E-1) ──────────────────────────────────────────────
"jina_read": {
    "name": "jina_read",
    "description": "URL의 전체 내용을 깨끗한 마크다운으로 변환하여 읽는다...",
    "input_schema": { "type": "object", "properties": {"url": ..., "max_tokens": ...} },
    "defer_loading": True,
},
"crawl4ai_fetch": {
    "name": "crawl4ai_fetch",
    "description": "JavaScript 렌더링이 필요한 SPA 페이지를 크롤링한다...",
    "defer_loading": True,
},
"deep_crawl": {
    "name": "deep_crawl",
    "description": "주제에 대해 검색 후 상위 페이지를 자동 크롤링하고 내용을 종합 분석한다...",
    "defer_loading": True,
},
```

그리고 `_GROUPS`에도:
```python
"crawl": ["jina_read", "crawl4ai_fetch", "deep_crawl"],
```

---

### 4. tool_executor.py — 실행기 3개 + fetch_url 리다이렉트 추가

**dispatch 테이블에 추가:**

```python
# AADS-186E-1 크롤링 도구
"jina_read":              self._jina_read,
"crawl4ai_fetch":         self._crawl4ai_fetch,
"deep_crawl":             self._deep_crawl,
# 하위호환: fetch_url → jina_read 내부 리다이렉트
"fetch_url":              self._jina_read,
```

**_jina_read() 메서드:**
- `JinaReaderService.read_url()` 호출
- 실패 시 `Crawl4AIService.fetch_page()` 폴백
- `{"via": "crawl4ai_fallback"}` 필드로 폴백 여부 표시

**_crawl4ai_fetch() 메서드:**
- `Crawl4AIService.fetch_page()` 직접 호출
- None 반환 시 "crawl4ai 서버 미가용" 에러 반환

**_deep_crawl() 메서드:**
- `DeepCrawlService.research_crawl()` 호출
- query, synthesis, citations, pages_crawled, pages_failed 반환

**_INTENT_TOOL_MAP 업데이트:**
```python
"url_analyze": ["jina_read"],      # 기존 read_github_file → jina_read로 변경
"url_read":    ["jina_read"],      # 신규
"deep_crawl":  ["deep_crawl"],     # 신규
```

---

### 5. intent_router.py — url_read / deep_crawl 인텐트 추가

**INTENT_MAP 추가:**
```python
# AADS-186E-1 크롤링 인텐트
"url_read":   {"model": "claude-sonnet", "tools": True, "group": "crawl"},
"deep_crawl": {"model": "claude-sonnet", "tools": True, "group": "crawl"},
```

**분류 프롬프트 인텐트 목록 추가:**
```
service_inspection, all_service_status,
url_read, deep_crawl
```

**분류 규칙 추가:**
```
- 이 URL 읽어, 이 문서 분석, 이 페이지 내용, http로 시작하는 URL → url_read
- 조사해서 정리, 여러 소스 비교, 크롤링해서 분석, 리서치, 딥 크롤 → deep_crawl
```

**키워드 폴백 추가:**
```python
if any(w in msg for w in ("이 url 읽어", "이 문서 분석", "이 페이지 내용", "http://", "https://", "url 열어", "링크 내용")):
    return _make_result("url_read")
if any(w in msg for w in ("조사해서 정리", "여러 소스 비교", "크롤링해서 분석", "리서치", "딥 크롤", "deep crawl")):
    return _make_result("deep_crawl")
```

---

### 6. docker-compose.crawl4ai.yml 신규 생성

파일 경로: `/root/aads/aads-server/docker-compose.crawl4ai.yml`

```yaml
services:
  crawl4ai:
    image: unclecode/crawl4ai:latest
    container_name: aads-crawl4ai
    ports: ["11235:11235"]
    restart: unless-stopped
    environment:
      - CRAWL4AI_API_TOKEN=${CRAWL4AI_API_TOKEN:-}
    volumes:
      - crawl4ai_data:/data
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11235/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

---

### 7. tests/test_crawl_tools.py 신규 생성 + 실행

파일 경로: `/root/aads/aads-server/tests/test_crawl_tools.py`

테스트 케이스 8개:
1. `TestJinaReaderService::test_read_url_success` — URL → 마크다운 반환 확인
2. `TestJinaReaderService::test_read_url_truncation` — max_tokens 초과 시 "[내용 절삭됨]" 확인
3. `TestJinaReaderService::test_read_url_failure_returns_none` — HTTP 5xx → None 반환
4. `TestCrawl4AIService::test_fetch_page_unavailable` — 미설치 시 None 반환 (graceful skip)
5. `TestCrawl4AIService::test_fetch_page_success` — 정상 크롤링 결과 확인
6. `TestJinaReadFallback::test_jina_read_falls_back_to_crawl4ai` — Jina 실패 시 crawl4ai 폴백
7. `TestDeepCrawlService::test_research_crawl_with_citations` — 인용 포함 종합 결과 확인
8. `TestDeepCrawlService::test_research_crawl_no_results` — 검색 결과 없음 에러 처리

**실행 결과:**
```
============================= test session starts ==============================
platform linux -- Python 3.11.9, pytest-9.0.2

tests/test_crawl_tools.py::TestJinaReaderService::test_read_url_success PASSED [ 12%]
tests/test_crawl_tools.py::TestJinaReaderService::test_read_url_truncation PASSED [ 25%]
tests/test_crawl_tools.py::TestJinaReaderService::test_read_url_failure_returns_none PASSED [ 37%]
tests/test_crawl_tools.py::TestCrawl4AIService::test_fetch_page_unavailable PASSED [ 50%]
tests/test_crawl_tools.py::TestCrawl4AIService::test_fetch_page_success PASSED [ 62%]
tests/test_crawl_tools.py::TestJinaReadFallback::test_jina_read_falls_back_to_crawl4ai PASSED [ 75%]
tests/test_crawl_tools.py::TestDeepCrawlService::test_research_crawl_with_citations PASSED [ 87%]
tests/test_crawl_tools.py::TestDeepCrawlService::test_research_crawl_no_results PASSED [100%]

========================= 8 passed, 1 warning in 0.19s =========================
```

**결과: 8/8 통과 (warning은 pytest_cache 권한 문제, 테스트 무관)**

---

### 8. Git 커밋

**aads-server:**
```
commit dde8147
feat(AADS-186E-1): Jina Reader + Crawl4AI + deep_crawl 크롤링 도구 통합

8 files changed, 1169 insertions(+), 9 deletions(-)
 create mode 100644 app/services/crawl4ai_service.py
 create mode 100644 app/services/deep_crawl_service.py
 create mode 100644 app/services/jina_reader_service.py
 create mode 100644 docker-compose.crawl4ai.yml
 create mode 100644 tests/test_crawl_tools.py
```

**aads-docs:**
```
commit 451d83b
docs(AADS-186E-1): HANDOVER v12.12 + STATUS 업데이트

2 files changed, 13 insertions(+), 3 deletions(-)
```

---

## 완료 기준(ACCEPTANCE_CRITERIA) 충족 여부

| # | 기준 | 결과 |
|---|------|------|
| 1 | jina_reader_service.py — JinaReaderService.read_url(), 25K토큰 제한, None 반환 | ✅ PASS |
| 2 | crawl4ai_service.py — Crawl4AIService.fetch_page(), graceful 비활성화 | ✅ PASS |
| 3 | deep_crawl_service.py — DeepCrawlService.research_crawl() 5단계 파이프라인 | ✅ PASS |
| 4 | tool_registry.py — jina_read/crawl4ai_fetch/deep_crawl 도구 3개 + crawl 그룹 | ✅ PASS |
| 5 | tool_executor.py — _jina_read/_crawl4ai_fetch/_deep_crawl 실행기 | ✅ PASS |
| 6 | intent_router.py — url_read/deep_crawl 인텐트 추가, 키워드 폴백 | ✅ PASS |
| 7 | docker-compose.crawl4ai.yml — 선택적 배포, 1G 메모리 제한 | ✅ PASS |
| 8 | requirements.txt — httpx 이미 존재(pyproject.toml>=0.28.0) | ✅ PASS |
| 9 | tests/test_crawl_tools.py — 8/8 통과 | ✅ PASS |

## CONSTRAINTS 충족 여부

| 제약 | 결과 |
|------|------|
| Jina Reader 네트워크 타임아웃 30초, 재시도 1회 | ✅ 구현됨 |
| Crawl4AI Optional dependency — 미설치 시 graceful skip | ✅ is_available() 캐시 체크 |
| deep_crawl 중간 결과 서비스 내부 요약 | ✅ _summarize_pages() 내부 처리 |
| 도구 응답 최대 25,000 토큰 | ✅ _MAX_RESULT_CHARS = 25000 |
| fetch_url 기존 도구 제거 금지 — jina_read 리다이렉트 | ✅ dispatch에 "fetch_url": self._jina_read |

## GitHub 커밋 링크 (R-008)
- aads-server: https://github.com/moongoby-GO100/aads-server/commit/dde8147
- aads-docs: https://github.com/moongoby-GO100/aads-docs/commit/451d83b

## 상태
- qa_status: PASS (8/8)
- HANDOVER: v12.12 업데이트 완료
- STATUS.md: AADS-186E-1 SUCCESS 기록
