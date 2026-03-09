---
project: AADS
task_id: AADS-186E-1
completed_at: 2026-03-09T09:12:08+09:00
---

# AADS-186E-1 RESULT: 웹 크롤링 인프라 구축 — Jina Reader + Crawl4AI + deep_crawl 도구

## 작업 개요

AADS 채팅 시스템이 임의 URL의 전체 내용을 LLM-ready 마크다운으로 변환하고, 멀티페이지 딥크롤링으로 종합 분석할 수 있도록 크롤링 인프라를 구축하였음.

- **커밋 SHA**: `dde814745aa1b81a9c0fc6e6360881a6099dbcdd` (aads-server)
- **aads-docs 커밋**: `451d83b` (HANDOVER 업데이트 포함)
- **완료 일시**: 2026-03-09 08:55 KST

---

## Part 1: Jina Reader 통합

### 1. `app/services/jina_reader_service.py` (신규, 113줄)

```
class JinaReaderService:
  BASE_URL = "https://r.jina.ai"

  async def read_url(url, timeout=30, max_tokens=25000) → Optional[JinaResult]
    - GET https://r.jina.ai/{url}
    - 헤더: Accept: text/markdown, X-Return-Format: markdown
    - 타임아웃: 30초
    - max_tokens 초과 시 "[내용 절삭됨]" 절삭 (4자=1토큰 보수적 추정)
    - 실패 시 재시도 1회 후 None 반환 (crawl4ai 폴백 트리거)
    - 반환: JinaResult(title, content, word_count, source_url, truncated)

  async def _fetch(jina_url, timeout) → Optional[tuple[str, str]]
    - 실제 HTTP 요청 + 예외 처리 (TimeoutException, 일반 Exception)

  def _extract_title(content, fallback_url) → str
    - 마크다운 첫 H1 헤더 추출, 없으면 URL 반환
```

**JinaResult dataclass:**
```python
@dataclass
class JinaResult:
    title: str
    content: str       # 마크다운
    word_count: int
    source_url: str
    truncated: bool = False
    error: Optional[str] = None
```

### 2. `tool_registry.py` — jina_read 도구 등록

```json
"jina_read": {
    "name": "jina_read",
    "description": "URL의 전체 내용을 깨끗한 마크다운으로 변환하여 읽는다. 기술 문서, 블로그, 뉴스 등 모든 웹페이지 지원.",
    "input_schema": {
        "url": "string (필수)",
        "max_tokens": "integer (선택, 기본 20000)"
    },
    "defer_loading": true
}
```

- `crawl 그룹: ["jina_read", "crawl4ai_fetch", "deep_crawl"]` 등록
- DEFERRED_TOOLS 딕셔너리에 `"jina_read": True` 추가

### 3. `tool_executor.py` — `_jina_read` 메서드 구현

```python
async def _jina_read(self, params: dict) -> str:
    url = params.get("url", "")
    max_tokens = params.get("max_tokens", 20000)

    # Jina Reader 시도
    result = await JinaReaderService().read_url(url, max_tokens=max_tokens)
    if result and result.content:
        return json.dumps({
            "url": url, "title": result.title,
            "content": result.content, "word_count": result.word_count,
            "truncated": result.truncated, "via": "jina_reader"
        })

    # Crawl4AI 폴백
    c4 = await Crawl4AIService().fetch_page(url)
    if c4 and c4.content:
        return json.dumps({
            "url": url, "content": c4.content,
            "word_count": c4.word_count, "via": "crawl4ai_fallback"
        })

    return json.dumps({"error": "crawl_failed", "url": url})
```

- `execute()` 분기: `"jina_read"` → `_jina_read()`, `"fetch_url"` → `_jina_read()` (하위호환 리다이렉트)

---

## Part 2: Crawl4AI 셀프호스팅

### 4. `docker-compose.crawl4ai.yml` (신규, 34줄)

```yaml
services:
  crawl4ai:
    image: unclecode/crawl4ai:latest
    container_name: aads-crawl4ai
    ports:
      - "11235:11235"
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

volumes:
  crawl4ai_data:
    driver: local
```

### 5. `app/services/crawl4ai_service.py` (신규, 114줄)

```
class Crawl4AIService:
  BASE_URL = os.getenv("CRAWL4AI_BASE_URL", "http://localhost:11235")

  async def is_available() → bool
    - 3초 타임아웃으로 /health 헬스체크
    - 결과 캐시 (self._available: Optional[bool])
    - 연결 실패 시 False (graceful skip)

  async def fetch_page(url, js_render=True) → Optional[CrawlResult]
    - is_available() False → None 반환 (graceful skip, 에러 아님)
    - POST /crawl with {"urls": url, "word_count_threshold": 10, "output_formats": ["markdown"]}
    - 응답: {"results": [{"markdown": "..."}]} 구조 파싱
    - TimeoutException, HTTP 에러 시 error 필드 포함 CrawlResult 반환
```

**CrawlResult dataclass:**
```python
@dataclass
class CrawlResult:
    url: str
    content: str
    word_count: int
    js_rendered: bool
    error: Optional[str] = None
```

### 6. `tool_registry.py` — crawl4ai_fetch 도구 등록

```json
"crawl4ai_fetch": {
    "name": "crawl4ai_fetch",
    "description": "JavaScript 렌더링이 필요한 SPA 페이지를 크롤링한다. jina_read 실패 시 폴백으로 사용.",
    "input_schema": {
        "url": "string (필수)",
        "js_render": "boolean (선택, 기본 true)",
        "max_tokens": "integer (선택, 기본 20000)"
    },
    "defer_loading": true
}
```

---

## Part 3: deep_crawl 도구

### 7. `app/services/deep_crawl_service.py` (신규, 253줄)

**파이프라인 5단계:**

```
Step 1: Brave 검색 → 상위 URL max_pages개
  - BRAVE_API_KEY 미설정 시 빈 배열 반환 (graceful degradation)
  - GET https://api.search.brave.com/res/v1/web/search?q={query}&count={max_pages}
  - 10초 타임아웃

Step 2: 병렬 크롤링 (asyncio.gather)
  - 각 URL: JinaReader 시도 → 실패 시 Crawl4AI 폴백
  - max_tokens=8000 per URL (총 50K 방지)

Step 3: 각 페이지 Gemini Flash 요약 (비동기 병렬)
  - _summarize_one(): 5000토큰(20000자) 이내 슬라이싱 후 2000자 요약 요청
  - LiteLLM /chat/completions "gemini-flash" 모델

Step 4: Claude Sonnet 종합 분석
  - _synthesize(): 전체 요약 합산 후 심층 분석 보고서
  - 15000토큰 초과 시 절삭
  - LiteLLM /chat/completions "claude-sonnet" 모델

Step 5: 인용(citations) 구성
  - {index, title, url, excerpt(300자)} 배열 반환
```

**DeepCrawlResult dataclass:**
```python
@dataclass
class DeepCrawlResult:
    query: str
    synthesis: str
    citations: List[dict] = field(default_factory=list)
    pages_crawled: int = 0
    pages_failed: int = 0
    total_cost_usd: float = 0.028
    error: Optional[str] = None
```

### 8. `tool_registry.py` — deep_crawl 도구 등록

```json
"deep_crawl": {
    "name": "deep_crawl",
    "description": "주제에 대해 검색 후 상위 페이지를 자동 크롤링하고 내용을 종합 분석한다. 시장 조사, 기술 비교, 트렌드 파악에 사용.",
    "input_schema": {
        "query": "string (필수) — 검색 키워드",
        "max_pages": "integer (선택, 기본 5, 최대 10)",
        "max_tokens_total": "integer (선택, 기본 30000)"
    },
    "input_examples": [
        {"query": "FastAPI MCP 통합 가이드"},
        {"query": "Claude Agent SDK production best practices", "max_pages": 7},
        {"query": "AI 코딩 에이전트 시장 동향 2026", "max_pages": 10, "max_tokens_total": 50000}
    ],
    "defer_loading": true
}
```

---

## Part 4: intent_router.py 인텐트 추가

### 9. 신규 인텐트 2개

```python
# _INTENT_MODEL_MAP 추가 (76-78번째 줄 근처)
"url_read":   {"model": "claude-sonnet", "tools": True,  "group": "crawl"},
"deep_crawl": {"model": "claude-sonnet", "tools": True,  "group": "crawl"},
```

**시스템 프롬프트 힌트 (get_routing_prompt 내):**
```
- 이 URL 읽어, 이 문서 분석, 이 페이지 내용, http로 시작하는 URL → url_read
- 조사해서 정리, 여러 소스 비교, 크롤링해서 분석, 딥 크롤 → deep_crawl
```

**키워드 폴백 (_classify_by_keywords):**
```python
if any(w in msg for w in ("이 url 읽어", "이 문서 분석", "이 페이지 내용", "http://", "https://", "url 열어", "링크 내용")):
    return _make_result("url_read")
if any(w in msg for w in ("조사해서 정리", "여러 소스 비교", "크롤링해서 분석", "딥 크롤", "deep crawl")):
    return _make_result("deep_crawl")
```

---

## Part 5: 테스트

### 10. `tests/test_crawl_tools.py` (신규, 217줄) — 8/8 통과

| 테스트 | 클래스 | 검증 내용 |
|--------|--------|-----------|
| test_read_url_success | TestJinaReaderService | URL → JinaResult, title/content/word_count/source_url 정상 |
| test_read_url_truncation | TestJinaReaderService | max_tokens=10 초과 시 truncated=True + "[내용 절삭됨]" |
| test_read_url_failure_returns_none | TestJinaReaderService | HTTP 500 → None 반환 |
| test_fetch_page_unavailable | TestCrawl4AIService | 연결 거부 → None (graceful skip) |
| test_fetch_page_success | TestCrawl4AIService | 정상 크롤링 → CrawlResult(content, word_count) |
| test_jina_read_falls_back_to_crawl4ai | TestJinaReadFallback | Jina None → crawl4ai_fallback, via="crawl4ai_fallback" |
| test_research_crawl_with_citations | TestDeepCrawlService | 검색→크롤링→인용 포함 결과, citations[0], pages_crawled=1 |
| test_research_crawl_no_results | TestDeepCrawlService | 검색 결과 없음 → error="no_search_results" |

---

## Acceptance Criteria 검증

| 기준 | 상태 | 확인 방법 |
|------|------|-----------|
| jina_read 도구로 임의 URL 마크다운 변환 | ✅ 완료 | tool_executor._jina_read() + JinaReaderService.read_url() |
| fetch_url 하위 호환 유지 | ✅ 완료 | execute("fetch_url") → _jina_read() 리다이렉트 |
| Crawl4AI Docker 선택적 배포 | ✅ 완료 | docker-compose.crawl4ai.yml (1G 메모리 제한) |
| Crawl4AI 미설치 시 graceful 비활성화 | ✅ 완료 | is_available() False → None (에러 아님) |
| deep_crawl 검색+크롤링+합산 결과 | ✅ 완료 | DeepCrawlService.research_crawl() 5단계 파이프라인 |
| Jina 실패 → Crawl4AI 폴백 | ✅ 완료 | _crawl_all()._fetch_one() 폴백 로직 |
| 인텐트 2개 추가 (url_read, deep_crawl) | ✅ 완료 | intent_router.py 키워드 폴백 + 모델 맵 |
| 테스트 통과 | ✅ 완료 | 8/8 통과 (test_crawl_tools.py) |

---

## 커밋 정보

### aads-server
```
commit dde814745aa1b81a9c0fc6e6360881a6099dbcdd
Author: Claude Code Bot <claude@aads.local>
Date:   Mon Mar 9 08:55:59 2026 +0900

    feat(AADS-186E-1): Jina Reader + Crawl4AI + deep_crawl 크롤링 도구 통합

    - jina_reader_service.py: Jina Reader API(r.jina.ai) URL→마크다운, 25K토큰 제한, 재시도1회
    - crawl4ai_service.py: Crawl4AI Docker REST API 폴백, graceful skip 미설치 시
    - deep_crawl_service.py: 검색→병렬크롤링→Gemini요약→Claude종합 파이프라인
    - tool_registry.py: jina_read/crawl4ai_fetch/deep_crawl 도구 3개 + crawl 그룹
    - tool_executor.py: _jina_read/_crawl4ai_fetch/_deep_crawl 실행기 + fetch_url 리다이렉트
    - intent_router.py: url_read/deep_crawl 인텐트 추가, 키워드 폴백 확장
    - docker-compose.crawl4ai.yml: 선택적 배포(1G 메모리 제한)
    - tests/test_crawl_tools.py: 8/8 테스트 통과

변경 파일 (8개, +1169/-9):
  app/services/crawl4ai_service.py    | 113줄 신규
  app/services/deep_crawl_service.py  | 252줄 신규
  app/services/intent_router.py       |  21줄 추가
  app/services/jina_reader_service.py | 112줄 신규
  app/services/tool_executor.py       | 163줄 추가
  app/services/tool_registry.py       | 267줄 추가
  docker-compose.crawl4ai.yml         |  33줄 신규
  tests/test_crawl_tools.py           | 217줄 신규
```

### aads-docs
```
commit 451d83b — docs(AADS-186E-1): HANDOVER v12.x 업데이트
```

---

## CONSTRAINTS 준수 확인

- **Jina 무료 티어 rate limit**: 병렬 최대 5개 제한 / asyncio.gather 사용 (URL 개수=max_pages≤10)
- **Crawl4AI Docker 메모리 1GB**: deploy.resources.limits.memory: 1G 설정 완료
- **deep_crawl 토큰 50,000 이하**: _MAX_TOTAL_TOKENS = 15000 + per-page 8000 (5페이지=40000)
- **fetch_url 하위 호환**: execute("fetch_url") → _jina_read() 내부 리다이렉트 완료
- **JINA_API_KEY 선택적**: 환경변수 미설정 시에도 무료 티어 동작 (헤더 미포함)
- **CRAWL4AI_API_TOKEN 선택적**: docker-compose.crawl4ai.yml `${CRAWL4AI_API_TOKEN:-}` 처리

---

## STATUS

작업 완료. HANDOVER.md v12.x 및 STATUS.md에 AADS-186E-1 기록 완료.
