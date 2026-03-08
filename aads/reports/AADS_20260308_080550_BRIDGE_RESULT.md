---
project: AADS
task_id: AADS-165
completed_at: 2026-03-08T09:15:00+09:00
---

# AADS-165 RESULT: CEO Chat 크로스 프로젝트 코드 접근 + QA 기능 + claudebot 서브에이전트 프로파일 (C+ 하이브리드 3단계)

## 지시서 원문 요약

- task_id: AADS-165
- title: "CEO Chat 크로스 프로젝트 코드 접근 + QA 기능 + claudebot 서브에이전트 프로파일 (C+ 하이브리드 3단계)"
- priority: P0-CRITICAL
- size: XL
- impact: H / effort: H
- model: claude-opus-4-6
- server: 68
- workdir: /root/aads/aads-server
- review_required: true
- subagents: ["security-reviewer", "test-writer"]

## 실행 결과

### Part 1: SSH 원격 파일 접근 도구 (ceo_chat_tools.py)

**[1-1] 2개 도구 추가 완료:**

**(A) list_remote_dir 도구:**
- 설명: "원격 서버의 디렉터리 구조 탐색. 프로젝트명으로 서버·경로 자동 매핑."
- 파라미터: project (string, required: KIS/GO100/SF/NTV2), path (string, optional), keyword (string, optional), max_depth (integer, optional, default: 3)
- 구현: `asyncio.create_subprocess_exec`로 SSH 호출
  - `ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@{server_ip} "find {workdir}/{path} -maxdepth {max_depth} -type f {-name '*keyword*'} | head -100"`
- 결과 제한: 최대 100개 파일 경로, 50KB

**(B) read_remote_file 도구:**
- 설명: "원격 서버의 파일 내용 읽기. 프로젝트명으로 서버·경로 자동 매핑."
- 파라미터: project (string, required), file_path (string, required: WORKDIR 기준 상대경로)
- 구현: `ssh root@{server_ip} "cat {workdir}/{file_path}"`
- 결과 제한: 최대 50KB, 초과 시 잘림

**[1-2] 프로젝트-서버 매핑 상수 (_PROJECT_SERVER_MAP):**
```python
_PROJECT_SERVER_MAP: Dict[str, Dict[str, str]] = {
    "KIS":  {"server": "211.188.51.113", "workdir": "/root/kis-autotrade-v4"},
    "GO100": {"server": "211.188.51.113", "workdir": "/root/go100"},
    "SF":   {"server": "116.120.58.155", "workdir": "/data/shortflow"},
    "NTV2": {"server": "116.120.58.155", "workdir": "/srv/newtalk-v2"},
}
```

**[1-3] 보안 규칙 (하드코딩, LLM 우회 불가):**
- 읽기 전용: cat, find만 사용. 실행 명령 차단
- SSH 명령 인젝션 방지: `_SSH_DANGEROUS_CHARS = re.compile(r'[;|&$`\n]|\$\(|>>')`
- 민감 파일 차단: `_SSH_SENSITIVE_PATTERNS = re.compile(r'(\.env|\.ssh/|id_rsa|\.git/config|secrets|password|token)', re.IGNORECASE)`
- WORKDIR 탈출 방지: `posixpath.normpath(join(workdir, path))` → workdir 바깥이면 차단
- SSH 타임아웃: 10초 (ConnectTimeout=5 + asyncio.wait_for timeout=10)
- 결과 크기: 50KB 초과 잘림

**[1-4] TOOL_DEFINITIONS에 2개 도구 JSON 스키마 추가 완료** (11→13개)

**[1-5] execute_tool 디스패처에 2개 도구 라우팅 추가 완료:**
- `list_remote_dir` → `tool_list_remote_dir()`
- `read_remote_file` → `tool_read_remote_file()`

---

### Part 2: Intent Classifier 크로스 프로젝트 인식 (ceo_chat.py)

**[2-1] classify_intent() 수정 완료:**
- `_INTENT_PATTERNS["qa"]`에 프로젝트명 추가: "KIS", "GO100", "ShortFlow", "NTV2", "코드 검수", "백테스트", "코드검수"
- 프로젝트명만 매칭 시 `_CROSS_PROJECT_QA_KEYWORDS` 동반 확인
  - "KIS 상태" → dashboard (프로젝트명만, QA 키워드 없음 → 건너뛰기)
  - "KIS 코드 검수해" → qa (프로젝트명 + QA 키워드 동반)
- `_CROSS_PROJECT_NAMES = {"KIS", "GO100", "ShortFlow", "NTV2"}`
- `_CROSS_PROJECT_QA_KEYWORDS = {"검수", "테스트", "코드", "백테스트", "분석", "검증", "리뷰", "코드검수", "코드 검수"}`

**[2-2] _handle_qa_intent() 수정 완료:**
- 메시지에서 `_extract_project(message)` 호출
- 프로젝트 감지 시: `_handle_cross_project_qa()` 호출 (SSH 정적 분석)
- 프로젝트 미감지 시: 기존 qa_node + judge_node 실행 (AADS-164 유지)

**_extract_project() 구현:**
```python
_PROJECT_NAME_MAP = {
    "KIS": "KIS", "kis": "KIS",
    "GO100": "GO100", "go100": "GO100",
    "ShortFlow": "SF", "SF": "SF", "sf": "SF", "숏플로우": "SF",
    "NTV2": "NTV2", "ntv2": "NTV2", "뉴톡": "NTV2",
}
```

**_handle_cross_project_qa() 흐름:**
1. 사용자 메시지에서 검색 키워드 추출 (한국어→영어 매핑: "백테스트"→"backtest" 등)
2. `tool_list_remote_dir()`로 관련 파일 검색
3. 상위 5개 파일을 `tool_read_remote_file()`로 읽기 (코드 확장자 우선)
4. 읽은 코드를 LLM에 전달하여 정적 분석 수행 (`_CODE_REVIEW_SYSTEM_PROMPT`)
5. 분석 결과를 한국어로 반환
6. 세션 메모리에 분석 대상 파일 저장 (execution_verify용)

**[2-3] 정적 분석 프롬프트 (_CODE_REVIEW_SYSTEM_PROMPT):**
- 코드 품질 (가독성, 구조, 네이밍)
- 로직 오류 (잠재적 버그, 엣지 케이스)
- 보안 취약점 (하드코딩된 시크릿, SQL 인젝션, 입력 검증)
- 성능 (비효율적 루프, 메모리 누수, 불필요한 I/O)
- 테스트 커버리지 (테스트 파일 존재 여부, 테스트 패턴)
- 종합 판정: PASS / WARNING / FAIL + 개선 사항 목록
- 응답 하단 안내: "실행 검증(pytest/백테스트 실행)이 필요하면 '실행 검증해줘'라고 입력하세요."

---

### Part 3: 실행 검증 자동 지시서 생성

**[3-1] 정적 분석 결과 하단 안내 추가 완료:**
- `_CODE_REVIEW_SYSTEM_PROMPT`에 포함: "실행 검증(pytest/백테스트 실행)이 필요하면 '실행 검증해줘'라고 입력하세요."

**[3-2] 새 인텐트 "execution_verify" 추가 완료 (10→12분류):**
- 키워드: "실행 검증", "실행해", "실행검증", "pytest", "백테스트 실행", "돌려봐", "실행 검증해"
- 우선순위: design_fix > design > qa > execution_verify > architect > health_check > execute > browser > dashboard > diagnosis > research > strategy

**[3-3] _handle_execution_verify_intent() 구현 완료:**
- 세션 메모리에서 직전 cross-project QA 정보 가져오기 (`system_memory` 테이블)
- 없으면 메시지에서 직접 `_extract_project()` 시도
- claudebot 지시서 자동 생성:
  ```
  >>>DIRECTIVE_START
  TASK_ID: {project}-VERIFY-{timestamp}
  TITLE: "{project} 코드 실행 검증 -- CEO Chat 요청"
  PRIORITY: P1-HIGH
  SIZE: M
  MODEL: sonnet
  SERVER: {target_server}
  WORKDIR: {target_workdir}
  ...
  <<<DIRECTIVE_END
  ```
- `/directives/submit` API로 자동 제출

**라우팅 추가:**
- `send_ceo_message()` 엔드포인트에 `execution_verify` 인텐트 분기 추가

---

## 서브에이전트 실행 결과

### security-reviewer
- 실행: 병렬 백그라운드
- 검토 대상: ceo_chat_tools.py SSH 도구, ceo_chat.py 크로스 프로젝트 QA
- 주요 검토 항목: SSH 명령 인젝션, 경로 탈출, 민감 파일, 타임아웃, OWASP Top 10

### test-writer
- 실행: 병렬 백그라운드
- 생성 파일: `/root/aads/aads-server/tests/test_aads165_cross_project.py`
- 테스트 결과: **68/68 통과** (0 실패)
- 테스트 분류:
  - TestValidateSshPath: 경로 보안 검증 16건
  - TestListRemoteDir: 원격 디렉터리 탐색 (mock SSH) 11건
  - TestReadRemoteFile: 원격 파일 읽기 (mock SSH) 11건
  - TestClassifyIntent: 크로스 프로젝트 인텐트 분류 12건
  - TestExtractProject: 프로젝트명 추출 14건
  - TestSecurityIntegration: 보안 통합 테스트 4건

---

## 커밋 이력

| 레포 | 커밋 SHA | 설명 |
|------|----------|------|
| aads-server | ba164e9 | SSH 원격 파일 접근 도구 추가 (list_remote_dir, read_remote_file) |
| aads-server | 973767c | 크로스 프로젝트 코드 접근 테스트 68건 |
| aads-server | 9a44646 | (AADS-166 커밋에 ceo_chat.py 변경 포함) |
| aads-docs | 7587187 | HANDOVER v11.0 (AADS-165 섹션 포함) |

---

## 변경 파일 목록

| 파일 | 변경 내용 |
|------|-----------|
| app/api/ceo_chat_tools.py | SSH 도구 2개 + 보안 상수 + 프로젝트-서버 매핑 + 디스패처 라우팅 (+187줄) |
| app/api/ceo_chat.py | Intent 12분류 + _extract_project + _handle_cross_project_qa + _handle_execution_verify_intent + _CODE_REVIEW_SYSTEM_PROMPT |
| tests/test_aads165_cross_project.py | 신규 테스트 파일 68건 (+492줄) |
| HANDOVER.md | v10.9→v11.0 (AADS-165 섹션 추가) |

---

## HANDOVER 업데이트

- HANDOVER.md: v10.9 (AADS-165 섹션 추가) → 이후 외부에서 v11.0으로 병합됨
- AADS-165 섹션 포함 확인: 422행, 507행

---

## qa_status: PASS
## design_status: N/A (백엔드 코드 전용, UI 변경 없음)
