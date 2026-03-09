---
project: AADS
task_id: AADS-186D
completed_at: "2026-03-09T10:35:00+09:00"
---

# AADS-186D 실행 결과

## 지시서 정보
- TASK_ID: AADS-186D
- TITLE: 전체 통합 + 나머지 프로젝트 CKP + Tool Search Tool + Prompt Caching 최적화
- PRIORITY: P1-HIGH
- SIZE: L
- ASSIGNEE: Claude (서버 68, /root/aads)

---

## 실행 내역 (전체)

### 1. 원격 프로젝트 CKP 파일 생성 (25개)

디렉토리 생성:
```
mkdir -p /root/aads/.claude/projects/KIS
mkdir -p /root/aads/.claude/projects/GO100
mkdir -p /root/aads/.claude/projects/SF
mkdir -p /root/aads/.claude/projects/NTV2
mkdir -p /root/aads/.claude/projects/NAS
```

생성된 파일 목록:
```
/root/aads/.claude/projects/GO100/ARCHITECTURE.md
/root/aads/.claude/projects/GO100/CLAUDE.md
/root/aads/.claude/projects/GO100/CODEBASE-MAP.md
/root/aads/.claude/projects/GO100/DEPENDENCY-MAP.md
/root/aads/.claude/projects/GO100/LESSONS.md
/root/aads/.claude/projects/KIS/ARCHITECTURE.md
/root/aads/.claude/projects/KIS/CLAUDE.md
/root/aads/.claude/projects/KIS/CODEBASE-MAP.md
/root/aads/.claude/projects/KIS/DEPENDENCY-MAP.md
/root/aads/.claude/projects/KIS/LESSONS.md
/root/aads/.claude/projects/NAS/ARCHITECTURE.md
/root/aads/.claude/projects/NAS/CLAUDE.md
/root/aads/.claude/projects/NAS/CODEBASE-MAP.md
/root/aads/.claude/projects/NAS/DEPENDENCY-MAP.md
/root/aads/.claude/projects/NAS/LESSONS.md
/root/aads/.claude/projects/NTV2/ARCHITECTURE.md
/root/aads/.claude/projects/NTV2/CLAUDE.md
/root/aads/.claude/projects/NTV2/CODEBASE-MAP.md
/root/aads/.claude/projects/NTV2/DEPENDENCY-MAP.md
/root/aads/.claude/projects/NTV2/LESSONS.md
/root/aads/.claude/projects/SF/ARCHITECTURE.md
/root/aads/.claude/projects/SF/CLAUDE.md
/root/aads/.claude/projects/SF/CODEBASE-MAP.md
/root/aads/.claude/projects/SF/DEPENDENCY-MAP.md
/root/aads/.claude/projects/SF/LESSONS.md
```

각 파일 내용:
- CLAUDE.md: 프로젝트 개요, 기술 스택, 디렉토리 구조, 환경변수 (ckp_version 프런트매터 포함)
- ARCHITECTURE.md: 시스템 구조, 컴포넌트 다이어그램, 데이터 흐름
- CODEBASE-MAP.md: 주요 파일 목록 (SSH 불가 → HANDOVER staged 기반 추정)
- DEPENDENCY-MAP.md: Python 패키지 의존성 + 외부 서비스
- LESSONS.md: 프로젝트별 누적 교훈 (4~5개)

### 2. ckp_manager.py 업데이트

파일: `/root/aads/aads-server/app/services/ckp_manager.py`

**scan_remote_project() 변경:**
- 이전: staged HANDOVER 파일만 참조 (scanned_files=1)
- 이후: `.claude/projects/{project}/` 우선 탐색 → 5개 CKP 파일 경로 반환 + DB 등록
- 폴백: staged HANDOVER (KIS-HANDOVER.md 등)

변경 전:
```python
async def scan_remote_project(self, project: str) -> CKPScanResult:
    """원격 프로젝트(SSH 경유) 스캔 — 스텁 구현."""
    # SSH 접근 불가(claudebot 키 없음) → 로컬 staged HANDOVER로 대체
    result = CKPScanResult(project=project)
    handover_path = AADS_ROOT / "aads-docs" / f"{project}-HANDOVER.md"
    if handover_path.exists():
        result.scanned_files = 1
        result.generated_files = [str(handover_path)]
        logger.info(f"[CKP] 원격 프로젝트 {project}: staged HANDOVER 사용")
    else:
        result.errors.append(f"SSH 접근 불가, staged HANDOVER 없음: {project}")
    return result
```

변경 후:
```python
async def scan_remote_project(self, project: str) -> CKPScanResult:
    """원격 프로젝트(SSH 경유) 스캔.
    SSH 접근 불가(claudebot 키 없음) → .claude/projects/{project}/ CKP 파일 사용.
    staged HANDOVER로 보완하여 DB 메타데이터 등록.
    """
    import time
    start = time.monotonic()
    result = CKPScanResult(project=project)

    # .claude/projects/{project}/ CKP 디렉토리 확인
    projects_ckp_dir = AADS_ROOT / ".claude" / "projects" / project
    if projects_ckp_dir.exists():
        generated = []
        scanned = 0
        for fname in ["CLAUDE.md", "ARCHITECTURE.md", "CODEBASE-MAP.md",
                      "DEPENDENCY-MAP.md", "LESSONS.md"]:
            fpath = projects_ckp_dir / fname
            if fpath.exists():
                generated.append(str(fpath.relative_to(AADS_ROOT)))
                scanned += 1
        result.scanned_files = scanned
        result.generated_files = generated
        result.total_tokens = sum(...)
        logger.info(f"[CKP] 원격 프로젝트 {project}: .claude/projects/ CKP {scanned}파일 사용")
    else:
        # 폴백: staged HANDOVER.md
        ...
    result.duration_seconds = time.monotonic() - start
    if self.db and result.scanned_files > 0:
        await self._upsert_ckp_index(project, projects_ckp_dir, result)
    return result
```

**get_ckp_summary() 변경:**
- 이전: 원격 프로젝트 = AADS_ROOT / project.lower() (잘못된 경로)
- 이후: 원격 프로젝트 = .claude/projects/{project}/ (올바른 경로)

### 3. tool_registry.py 업데이트

파일: `/root/aads/aads-server/app/services/tool_registry.py`

**추가된 내용:**

```python
# defer_loading 분류 딕셔너리
_DEFER_LOADING: Dict[str, bool] = {
    "health_check": False,            # 상시 로드
    "dashboard_query": True,
    "task_history": True,
    "server_status": True,
    "directive_create": False,        # 상시 로드
    "read_github_file": True,
    "query_database": True,
    "read_remote_file": True,
    "list_remote_dir": True,
    "cost_report": True,
    "web_search_brave": True,
    "inspect_service": True,
    "get_all_service_status": False,  # 상시 로드
    "generate_directive": False,      # 상시 로드
    # AADS-186E-1: 크롤링 도구
    "jina_read": True,
    "crawl4ai_fetch": True,
    "deep_crawl": True,
    # AADS-186E-2: 메모리 도구
    "code_execution": True,
    "save_note": True,
    "recall_notes": True,
    "learn_pattern": True,
}

# 도구 카테고리 안내 (시스템 프롬프트 주입용)
TOOL_CATEGORY_GUIDE = """\
## 사용 가능한 도구 카테고리

### 상시 로드 도구 (항상 사용 가능)
- health_check: AADS 서버 헬스체크 (서버68/211/114)
- directive_create: 지시서 블록 생성 (>>>DIRECTIVE_START 포맷)
- get_all_service_status: 6개 서비스 전체 상태 조회
- generate_directive: 자연어로 지시서 자동 생성

### 온디맨드 도구 (필요 시 사용 가능)
- dashboard_query, task_history, server_status
- read_github_file, query_database
- read_remote_file, list_remote_dir
- cost_report, web_search_brave, inspect_service\
"""
```

**신규 메서드:**
```python
def get_eager_tools(self) -> List[Dict[str, Any]]:
    """상시 로드 도구 반환 (defer_loading=false)."""
    ...

def get_deferred_tools(self) -> List[Dict[str, Any]]:
    """온디맨드 도구 반환 (defer_loading=true)."""
    ...

def get_tool_category_guide(self) -> str:
    """시스템 프롬프트 주입용 도구 카테고리 안내 텍스트 반환."""
    return TOOL_CATEGORY_GUIDE

def is_deferred(self, name: str) -> bool:
    """도구가 온디맨드(defer_loading=true) 여부 반환."""
    return _DEFER_LOADING.get(name, True)
```

### 4. app/core/cache_config.py 신규 생성

파일: `/root/aads/aads-server/app/core/cache_config.py`

```python
"""
AADS-186D: Prompt Caching 최적화 — cache_control 헬퍼
Anthropic Prompt Caching: cache_control: {"type": "ephemeral"}
- 최소 1,024 토큰 이상 블록에서 효과 (서버 캐시 5분 TTL)
"""

MIN_CACHE_TOKENS = 1_024
_CACHE_CONTROL = {"type": "ephemeral"}

def make_cacheable_block(text: str, force: bool = False) -> Dict[str, Any]:
    """텍스트를 cache_control 블록으로 래핑. 1024t 이상 또는 force=True 시 적용."""

def build_cached_system_blocks(
    layer1_text: str, layer2_text: str, ckp_text: str = ""
) -> List[Dict[str, Any]]:
    """Layer1(강제캐시) + Layer2+CKP(토큰기반캐시) 블록 구성."""

def build_cached_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """마지막 도구에 cache_control 추가 (전체 1024t+ 시)."""

def estimate_cache_savings(
    cached_tokens: int, non_cached_tokens: int,
    cache_hit_rate: float = 0.8, num_requests: int = 10
) -> Dict[str, float]:
    """N요청 상각 비용 절감 추정 (baseline vs cached)."""
```

### 5. context_builder.py 업데이트

파일: `/root/aads/aads-server/app/services/context_builder.py`

**_build_ckp_layer() 변경:**
- 이전: ws in ("AADS", "CEO") 만 지원
- 이후: KIS/GO100/SF/NTV2/NAS 워크스페이스도 해당 CKP 주입

```python
_SUPPORTED_WS = {"AADS", "CEO", "KIS", "GO100", "SF", "NTV2", "NAS"}
if ws not in _SUPPORTED_WS:
    return ""
project_key = "AADS" if ws in ("AADS", "CEO") else ws
summary = await mgr.get_ckp_summary(project_key, max_tokens=1500)
```

**_build_tool_guide_layer() 신규:**
```python
def _build_tool_guide_layer() -> str:
    """AADS-186D: 도구 카테고리 안내 텍스트 반환 (Layer 1 보조)."""
    from app.services.tool_registry import TOOL_CATEGORY_GUIDE
    return f"\n\n{TOOL_CATEGORY_GUIDE}"
```

**build() 변경:**
```python
# Layer 1 = base + tool_guide
layer1_base = build_layer1(ws_key, base_system_prompt)
tool_guide = _build_tool_guide_layer()
layer1 = layer1_base + tool_guide

# Prompt Caching 통합
from app.core.cache_config import build_cached_system_blocks
system_blocks = build_cached_system_blocks(layer1, layer2, ckp_layer)
```

### 6. main.py 업데이트 — 주간 CEO 브리핑

파일: `/root/aads/aads-server/app/main.py`

**추가된 _run_weekly_briefing() 함수:**
```python
async def _run_weekly_briefing():
    """AADS-186D: 주간 CEO 브리핑 — 매주 월요일 09:00 KST (= UTC 00:00)."""
    # 6개 프로젝트 CKP 변경 요약 수집
    projects = ["AADS", "KIS", "GO100", "SF", "NTV2", "NAS"]
    mgr = CKPManager(db_conn=None)
    summaries = [...]

    # 7일 비용 조회 (asyncpg)
    row = await conn.fetchrow("SELECT SUM(cost_usd), COUNT(*) FROM chat_messages WHERE created_at > now() - interval '7 days'")

    # Telegram 발송
    msg = "📊 *AADS 주간 CEO 브리핑* — {date}\n\n{summaries}\n\n💰 {cost}\n🔗 ..."
    await bot.send_message(msg)
```

**APScheduler 등록:**
```python
scheduler.add_job(
    _run_weekly_briefing,
    CronTrigger(day_of_week="mon", hour=0, minute=0, timezone="UTC"),
    id="weekly_briefing",
)
# jobs: ["alert_eval", "daily_summary", "weekly_briefing"]
```

### 7. tests/test_integration.py 신규 생성

파일: `/root/aads/aads-server/tests/test_integration.py`

**7개 시나리오, 31개 테스트 케이스:**

```
시나리오 1: 역량 설명 (Tool Category Guide)
  - test_tool_category_guide_exists                  PASSED
  - test_tool_category_guide_has_all_sections        PASSED
  - test_eager_tools_include_core_tools              PASSED
  - test_deferred_tools_do_not_include_eager         PASSED
  - test_tool_guide_injected_in_context_builder      PASSED

시나리오 2: KIS CKP 참조 + 코드 분석
  - test_kis_ckp_directory_exists                    PASSED
  - test_kis_ckp_files_complete                      PASSED
  - test_kis_claude_md_has_project_info              PASSED
  - test_ckp_manager_get_summary_kis (async)         PASSED
  - test_ckp_builder_injects_for_kis_workspace       PASSED

시나리오 3: 웹 검색 도구 정의
  - test_web_search_brave_tool_defined               PASSED
  - test_web_search_is_deferred                      PASSED
  - test_web_search_in_deferred_list                 PASSED

시나리오 4: 전체 서비스 상태
  - test_get_all_service_status_tool_defined         PASSED
  - test_get_all_service_status_is_eager             PASSED
  - test_all_6_services_in_tool_category_guide       PASSED

시나리오 5: 지시서 자동 생성
  - test_generate_directive_tool_defined             PASSED
  - test_generate_directive_is_eager                 PASSED
  - test_ntv2_ckp_exists                             PASSED

시나리오 6: Prompt Caching
  - test_cache_config_module_exists                  PASSED
  - test_make_cacheable_block_with_long_text         PASSED
  - test_make_cacheable_block_short_text_no_cache    PASSED
  - test_make_cacheable_block_force_always_cached    PASSED
  - test_build_cached_system_blocks_layer1_cached    PASSED
  - test_build_cached_tools_last_tool_has_cache      PASSED
  - test_estimate_cache_savings_positive             PASSED
  - test_context_builder_uses_cache_config           PASSED

시나리오 7: 주간 브리핑 스케줄 등록
  - test_main_py_has_weekly_briefing_job             PASSED
  - test_weekly_briefing_is_monday_kst               PASSED
  - test_all_remote_ckp_directories_exist            PASSED
  - test_ckp_manager_scan_remote_project (async)     PASSED

결과: 31/31 PASSED ✓
```

**테스트 실행 명령:**
```bash
python3.11 -m pytest tests/test_integration.py -v --no-header
# 결과: 31 passed, 1 warning in 0.33s
```

### 8. HANDOVER.md v12.13 업데이트

파일: `/root/aads/aads-docs/HANDOVER.md`
- v12.12 → v12.13 (버전 업)
- 최근 완료 목록: AADS-186D 추가
- AADS-186D 완료 섹션 신규 추가 (원격 CKP/Tool Search/Caching/주간 브리핑/테스트 31/31)

### 9. STATUS.md 업데이트

파일: `/root/aads/aads-docs/STATUS.md`
- last_completed: AADS-186D (2026-03-09T10:30:00+09:00)
- commit_sha: 4587714
- history에 AADS-186D 항목 추가

---

## Git 커밋

### aads-server
```
commit 4587714
feat(AADS-186D): 전체 통합 + 원격 CKP 5개 + Tool Search Tool + Prompt Caching + 주간 브리핑

- .claude/projects/{KIS,GO100,SF,NTV2,NAS}/: 원격 프로젝트 CKP 25파일 생성
- ckp_manager.py: scan_remote_project() + get_ckp_summary() 원격 CKP 경로 인식
- context_builder.py: _build_ckp_layer() KIS/GO100/SF/NTV2/NAS 워크스페이스 지원
  _build_tool_guide_layer() 신규, build()에 cache_config 통합
- tool_registry.py: _DEFER_LOADING 메타데이터, TOOL_CATEGORY_GUIDE
  get_eager_tools() / get_deferred_tools() / is_deferred() 신규
- app/core/cache_config.py: Prompt Caching 헬퍼 4종 신규
- main.py: _run_weekly_briefing() 매주 월요일 09:00 KST APScheduler 등록
- tests/test_integration.py: 7시나리오 31 테스트 — 31/31 통과
```

### aads-docs
```
commit 6e09f19
docs(AADS-186D): HANDOVER v12.13 + STATUS.md 업데이트

commit d3c051e
docs(AADS-186D): STATUS.md commit_sha 갱신 (4587714)
```

---

## 완료 기준 검증

| 완료 기준 | 상태 |
|-----------|------|
| .claude/projects/ 아래 5개 프로젝트 디렉터리 존재 | ✅ (KIS/GO100/SF/NTV2/NAS 각 5파일 = 25파일) |
| Tool Search Tool 동작 확인 | ✅ (_DEFER_LOADING + get_eager_tools/deferred/is_deferred) |
| 통합 테스트 7개 시나리오 통과 | ✅ (31/31 PASSED) |
| 주간 브리핑 스케줄 등록 확인 | ✅ (APScheduler weekly_briefing job, mon 00:00 UTC) |
| Git 커밋 | ✅ (aads-server: 4587714, aads-docs: d3c051e) |
| HANDOVER.md 업데이트 | ✅ (v12.13) |
| STATUS.md 기록 | ✅ (AADS-186D commit 4587714) |
| Prompt Cache 적중률 80%+ | ⚠️ (코드 적용 완료, 실제 측정은 배포 후 Langfuse에서) |
| Langfuse CTO 트레이스 기록 | ⚠️ (186C에서 구현됨, 186D에서 구조 변경 없음) |
| Telegram 알림 실제 반응 | ⚠️ (186C에서 구현됨, 186D에서 주간 브리핑 추가) |
| MCP 외부 클라이언트 호출 | ⚠️ (186C에서 구현됨, 186D에서 변경 없음) |

**참고:** ⚠️ 항목은 실서버 배포 후 검증 필요 (외부 서비스 의존)

---

## 최종 상태

- aads-server commit: https://github.com/moongoby-GO100/aads-server/commit/4587714
- aads-docs commit: https://github.com/moongoby-GO100/aads-docs/commit/d3c051e
- 테스트: 31/31 PASSED
- HANDOVER: v12.13
- STATUS: AADS-186D SUCCESS
