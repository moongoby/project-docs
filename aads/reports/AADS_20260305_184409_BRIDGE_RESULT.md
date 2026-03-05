---
project: AADS
task_id: T-082
completed_at: 2026-03-05T18:55:33+09:00
---

# T-082 실행 결과 — classify_project 전면 재작성

## 지시서 원문

Task ID: T-082
제목: classify_project 전면 재작성 — 파일명 접두사 + AADS 인프라 1순위 + 한글 오분류 제거
프로젝트: AADS
서버: 68 (aads.newtalk.kr)
우선순위: P0-CRITICAL
예상 시간: 20분
예상 비용: $0
의존성: T-081 완료 후
병렬: T-083, T-084와 동시 진행 불가 (같은 파일 project_dashboard.py 수정)

---

## 실행 내역

### 1. 파일 읽기

지시서 파일: `/root/.genspark/directives/pending/AADS_20260305_184409_BRIDGE.md` 읽기 완료

대상 파일: `/root/aads/aads-server/app/api/project_dashboard.py` 읽기 완료 (65.9KB)

기존 `_classify_project()` 함수 위치: line 685 (파일 읽기 시점 기준)
실제 작업 시점 line: 710 (다른 세션에서 이미 일부 수정된 상태)

---

### 2. 백업 및 태그

```bash
cd /root/aads/aads-server
cp app/api/project_dashboard.py app/api/project_dashboard.py.bak.T082
git tag pre-T082
```

**결과**: 백업 완료 (Backup done)

---

### 3. classify_project() 전면 재작성

#### 변경 전 (T-081 버전)
```python
def _classify_project(filename: str, content: str) -> str:
    """파일명 프리픽스 + 보고서 본문 키워드로 프로젝트 자동 분류 (T-081 개선)

    1단계: AADS 인프라 확정 키워드 (최우선) → AADS
    2단계: 프로젝트 고유 키워드 (좁은 범위)
    3단계: 기본값 AADS
    ...
    """
    # 1단계: AADS 인프라 확정 키워드 — 하나라도 있으면 무조건 AADS
    aads_definitive = [...]
    content_check = content
    content_lower = content.lower()
    for kw in aads_definitive:
        if kw.lower() in content_lower:
            return "AADS"

    # 파일명 프리픽스 (1단계 통과 후)
    fname = filename.upper()
    if fname.startswith("KIS_"): return "KIS"
    if fname.startswith("GO100_"): return "GO100"
    if fname.startswith("SF_"): return "ShortFlow"
    if fname.startswith("NT_"): return "NewTalk"
    # (SALES_, NAS_ 없음)

    # 2단계: 프로젝트 고유 키워드 (좁은 범위)
    kis_keywords = ['kis-autotrade', 'KIS-V41', 'DESK1', ...]
    go100_keywords = ['go100 프로젝트', 'GO100 목표', '100일 목표', ...]
    sf_keywords = ['shortflow 영상', 'shortflow 파이프라인', ...]
    nt_keywords = ['newtalk v2 서비스', 'ntv2 배포', ...]
    nas_keywords = ['nasync', 'nas동기화', ...]
    # 3단계: 기본값 AADS
    return "AADS"
```

#### 변경 후 (T-082 버전)
`VALID_PROJECT_NAMES`, `validate_project_name()`, `_classify_project()` 3개 추가/변경:

```python
VALID_PROJECT_NAMES = frozenset({
    "AADS", "KIS", "GO100", "ShortFlow", "NewTalk", "NAS", "SALES",
    "aads-server", "aads-dashboard",
})


def validate_project_name(project: str) -> str:
    """프로젝트명 유효성 검사 — 한글 문장 등 비정상 값은 AADS로 대체 (T-082)

    허용값: AADS, KIS, GO100, ShortFlow, NewTalk, NAS, SALES, aads-server, aads-dashboard
    """
    if not project or len(project) > 30:
        return "AADS"
    if project in VALID_PROJECT_NAMES:
        return project
    project_lower = project.lower()
    for valid in VALID_PROJECT_NAMES:
        if project_lower == valid.lower():
            return valid
    return "AADS"


def _classify_project(filename: str, content: str) -> str:
    """파일명 접두사 + 본문 키워드로 프로젝트 자동 분류 (T-082 전면 재작성)

    1단계: 파일명 접두사 매칭 (최우선) → 해당 프로젝트
    2단계: AADS 인프라 키워드 리스트 매칭 → AADS
    3단계: 프로젝트 고유 키워드 매칭
    4단계: 기본값 AADS
    """
    content_lower = content.lower()

    # 1단계: 파일명 접두사 매칭 (최우선)
    fname = filename.upper()
    if fname.startswith("KIS_"): return "KIS"
    if fname.startswith("GO100_"): return "GO100"
    if fname.startswith("SF_"): return "ShortFlow"
    if fname.startswith("NT_"): return "NewTalk"
    if fname.startswith("SALES_"): return "SALES"
    if fname.startswith("NAS_"): return "NAS"

    # 2단계: AADS 인프라 키워드 → AADS
    aads_keywords = [
        'dashboard', 'bridge', 'handover', 'ceo_chat', 'context', 'memory',
        'supervisor', 'agent', 'pipeline', 'docker', 'nginx', 'remote_agent',
        'classify_project', 'saferender', 'parse_engine', 'visual_qa', 'mobile_qa',
        'mcp', 'langgraph', 'sandbox', 'directives', 'deploy',
        'typescript', 'npm build', 'git push', 'aads-server', 'aads-dashboard', 'aads-docs',
        'project_dashboard', 'bridge.py', 'genspark_bridge', 'auto_trigger', 'claude_exec',
        'docker-compose', 'aads_remote', 'cross-message', 'cross_msg',
        'system_memory', 'context.py', 'task id:', 'directive',
        'error_breakdown', 'frontend', 'npm run build',
        '대시보드', 'ceo chat', '원격 에이전트', 'remote agent', '프론트엔드',
    ]
    for kw in aads_keywords:
        if kw in content_lower:
            return "AADS"

    # 3단계: 프로젝트 고유 키워드 매칭
    kis_keywords = ['kis', 'autotrade', '자동매매', '피라미딩', 'desk', '한국투자',
                    'fractal trend', 'pyramiding']
    if any(kw.lower() in content_lower for kw in kis_keywords):
        return "KIS"

    go100_keywords = ['go100', '지오백', '100세']
    if any(kw.lower() in content_lower for kw in go100_keywords):
        return "GO100"

    sf_keywords = ['shortflow', 'sf', '숏폼', '영상', 'economy', 'finance', 'tech',
                   'ffmpeg', 'shortform video', 'run_v4_pipeline']
    if any(kw.lower() in content_lower for kw in sf_keywords):
        return "ShortFlow"

    nt_keywords = ['newtalk', '뉴톡', 'v1fix', 'v2', '이미지', 'goods']
    if any(kw.lower() in content_lower for kw in nt_keywords):
        return "NewTalk"

    nas_keywords = ['nas', 'nasync', 'n2']
    if any(kw.lower() in content_lower for kw in nas_keywords):
        return "NAS"

    sales_keywords = ['sales', 'marketing', '마케팅', '영업']
    if any(kw.lower() in content_lower for kw in sales_keywords):
        return "SALES"

    # 4단계: 기본값 AADS
    return "AADS"
```

---

### 4. 한글 오분류 버그 수정

#### 4-1. title 파싱: 50자 초과 시 파일명 사용

`_parse_directive_file()` 내 title 파싱 수정:

```python
# 변경 전
if title_match:
    title = title_match.group(1).strip()

# 변경 후 (T-082)
if title_match:
    _t = title_match.group(1).strip()
    title = _t if len(_t) <= 50 else filename
```

동일 패턴을 YAML 프런트매터 분기와 일반 텍스트 분기 양쪽에 적용.

#### 4-2. validate_project_name() 적용

YAML 프런트매터 `project:` 필드:
```python
# 변경 전
project = _normalize_project(line.split(":", 1)[1].strip())

# 변경 후
project = validate_project_name(_normalize_project(line.split(":", 1)[1].strip()))
```

일반 텍스트 `프로젝트:` 필드 (이미 50자 제한 있음):
```python
# 변경 전
project = _normalize_project(m_proj.group(1).strip())

# 변경 후
project = validate_project_name(_normalize_project(m_proj.group(1).strip()))
```

`_parse_report_file()` 의 YAML `project:` 필드에도 동일 적용.

---

### 5. analytics API by_project 통합

#### 5-1. directives 엔드포인트 by_project 집계
```python
# 변경 전
proj = d["project"]

# 변경 후
proj = validate_project_name(d["project"])
```

#### 5-2. reports 엔드포인트 by_project 집계
```python
# 변경 전
proj = r["project"]

# 변경 후
proj = validate_project_name(r["project"])
```

#### 5-3. analytics 엔드포인트 by_project_dir 집계
```python
# 변경 전
proj = d["project"]

# 변경 후 (T-082: validate_project_name 적용)
proj = validate_project_name(d["project"])
```

#### 5-4. analytics 엔드포인트 by_project_conv (aads_conversations DB)
```python
# 변경 전
proj = CONV_PROJECT_MAP.get(r["project"] or "", r["project"] or "unknown")

# 변경 후
proj = validate_project_name(CONV_PROJECT_MAP.get(r["project"] or "", r["project"] or "AADS"))
```

---

### 6. 빌드/배포

```bash
DOCKER_BUILDKIT=0 docker compose -f docker-compose.prod.yml up -d --build
```

**결과**:
```
NAME             STATUS
aads-dashboard   Up 34 seconds (healthy)
aads-postgres    Up 36 minutes (healthy)
aads-redis       Up 36 minutes (healthy)
aads-server      Up 36 seconds (healthy)
```

---

### 7. 검증

#### health check
```bash
curl -s -o /dev/null -w "%{http_code}" https://aads.newtalk.kr/api/v1/health
```
**결과**: `200`

#### directives AADS 카운트
```bash
curl -s https://aads.newtalk.kr/api/v1/dashboard/directives | python3 -m json.tool | grep -c '"project": "AADS"'
```
**결과**: `172`

#### analytics by_project (한글 문장 0건)
```bash
curl -s https://aads.newtalk.kr/api/v1/dashboard/analytics | python3 -c "import sys,json; d=json.load(sys.stdin); [print(p['project'],p['total']) for p in d['by_project']]"
```
**결과**:
```
AADS 97
KIS 2
```
→ 한글 문장 프로젝트명 0건 확인 ✅

---

### 8. Git 커밋 및 푸시

#### aads-server
```bash
git add app/api/project_dashboard.py
git commit -m "fix(T-082): classify_project 전면 재작성 — 3단계 분류 + 한글 오분류 제거"
git push origin main
```

**결과**:
```
[main 2179ff9] fix(T-082): classify_project 전면 재작성 — 3단계 분류 + 한글 오분류 제거
 1 file changed, 186 insertions(+), 55 deletions(-)
To https://github.com/moongoby-GO100/aads-server.git
   ad86f8c..2179ff9  main -> main
```

GitHub 원문 확인:
```bash
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby-GO100/aads-server/main/app/api/project_dashboard.py
```
**결과**: `200`

---

### 9. 보고서 작성 및 HANDOVER 업데이트

#### 보고서
```bash
# /root/aads/aads-docs/reports/T-082-RESULT.md 작성 완료
cd /root/aads/aads-docs
git add reports/T-082-RESULT.md
git commit -m "[AADS] report: T-082 classify_project 재작성 결과"
git push origin main
```

**결과**:
```
[main cf011c6] [AADS] report: T-082 classify_project 재작성 결과
 1 file changed, 73 insertions(+)
To https://github.com/moongoby-GO100/aads-docs.git
   f04e611..cf011c6  main -> main
```

#### HANDOVER.md 업데이트
```bash
git add HANDOVER.md
git commit -m "[AADS] docs: HANDOVER T-082 추가"
git push origin main
```

**결과**:
```
[main acd29b9] [AADS] docs: HANDOVER T-082 추가
 1 file changed, 2 insertions(+), 1 deletion(-)
To https://github.com/moongoby-GO100/aads-docs.git
   cf011c6..acd29b9  main -> main
```

---

## 최종 보고

[CURSOR-AADS] push 완료
작업: T-082 classify_project 3단계 분류 + 한글 오분류 제거
보고서: https://github.com/moongoby-GO100/aads-docs/blob/main/reports/T-082-RESULT.md
커밋: https://github.com/moongoby-GO100/aads-server/commit/2179ff9
HTTP: 200
HANDOVER: 업데이트 완료 (v5.18)
다음: T-083 착수 또는 지시 대기
