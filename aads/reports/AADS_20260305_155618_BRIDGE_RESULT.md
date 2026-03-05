---
project: AADS
task_id: T-072
completed_at: 2026-03-05T16:07:02+09:00
---

# T-072 실행 결과 보고서

## 보고 형식 (지시서 요구)

- Task: T-072
- Status: completed
- React Error #31: 해결 (error_type safeRender + StatusBadge 객체 처리 + backend error 키 숫자화)
- API endpoints:
  - /api/v1/dashboard/directives: HTTP 200
  - /api/v1/dashboard/reports: HTTP 200
  - /api/v1/dashboard/task-history: HTTP 200
  - /tasks: HTTP 200 (307 redirect → 200)
- Build: 성공 (0 에러)
- Git commits:
  - aads-server: ee3df33
  - aads-dashboard: ca2c27c
  - aads-docs: e6cd12a
- 검증 URL: https://aads.newtalk.kr/tasks

---

## 상세 실행 내역

### 사전 준비 — 백업

```
cp /root/aads/aads-dashboard/src/app/tasks/page.tsx /root/aads/aads-dashboard/src/app/tasks/page.tsx.bak.T072
cp /root/aads/aads-dashboard/src/lib/api.ts /root/aads/aads-dashboard/src/lib/api.ts.bak.T072
cp /root/aads/aads-server/app/api/project_dashboard.py /root/aads/aads-server/app/api/project_dashboard.py.bak.T072
```
→ 완료

---

### Part A — React Error #31 수정

**원인 분석:**
- `/api/v1/dashboard/directives` 응답에서 `"error"` 키가 dict 객체 `{"total": 20, "auth_expired": 0, ...}` 로 반환
- Frontend `DirectiveSummary.error: number` 타입임에도 실제로 객체가 오면 `{data.error}` JSX 렌더링 시 React Error #31 발생

**수정 내역 (page.tsx):**

1. `safeRender()` 헬퍼 함수 추가:
```typescript
function safeRender(value: unknown): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}
```

2. `StatusBadge` 컴포넌트: `status: unknown` 타입 처리
```typescript
function StatusBadge({ status }: { status: unknown }) {
  const statusStr = typeof status === 'object' && status !== null
    ? (status as Record<string, string>).label || (status as Record<string, string>).value || '확인중'
    : String(status || '');
  const s = statusStr.toLowerCase();
  ...
  return <span ...>{statusStr}</span>;
}
```

3. `error_type` 렌더링: `safeRender(d.error_type)` 사용
4. `task_id`, `title` 렌더링: `safeRender()` 사용으로 안전 처리

---

### Part B — Backend API 정리

**수정 파일:** `/root/aads/aads-server/app/api/project_dashboard.py`

#### 1. `_classify_project()` 함수 강화 (키워드 매핑 방식으로 변경)

**변경 전:**
```python
def _classify_project(content: str) -> str:
    if re.search(r"kis-autotrade|KIS|kis_autotrade|한국투자", content):
        return "KIS"
    if re.search(r"shortflow|ShortFlow|숏폼|쇼츠|템빨", content):
        return "ShortFlow"
    if re.search(r"newtalk|뉴톡|NewTalk|newtalk-v2", content):
        return "NewTalk"
    if re.search(r"nas-image|nasync|NAS|nas(?!\w)", content):
        return "NAS"
    if re.search(r"go100|GO100", content):
        return "GO100"
    return "AADS"
```

**변경 후:**
```python
def _classify_project(content: str) -> str:
    """보고서/지시서 내용에서 프로젝트 자동 분류 (T-072: 키워드 매핑 강화)"""
    mappings = [
        (['kis-autotrade', 'KIS', 'kis_autotrade', '주식', 'autotrade'], 'KIS'),
        (['shortflow', 'ShortFlow', '쇼츠', 'shorts', '템빨'], 'ShortFlow'),
        (['newtalk', 'NewTalk', '뉴톡'], 'NewTalk'),
        (['nas', 'NAS', 'nasync'], 'NAS'),
        (['go100', 'GO100', 'go_100'], 'GO100'),
    ]
    content_lower = content.lower()
    for keywords, project in mappings:
        if any(kw.lower() in content_lower for kw in keywords):
            return project
    return 'AADS'
```

#### 2. `_classify_error()` 함수 강화 (Optional[str] 반환, 패턴 추가)

**변경 전:**
```python
def _classify_error(content: str) -> str:
    if re.search(r"OAuth|401|Failed to authenticate", content):
        return "auth_expired"
    if re.search(r"Permission denied", content):
        return "permission_denied"
    if re.search(r"command not found", content):
        return "env_error"
    if re.search(r"timeout|Watchdog|1200초|Session terminated", content, re.IGNORECASE):
        return "timeout"
    return "task_failure"
```

**변경 후:**
```python
def _classify_error(content: str) -> Optional[str]:
    """에러 내용에서 에러 유형 분류 (T-072: 패턴 강화)"""
    if any(x in content for x in ['401', 'OAuth', 'token expired', 'Unauthorized']):
        return 'auth_expired'
    if any(x in content for x in ['Permission denied', 'EACCES', 'permission']):
        return 'permission_denied'
    if any(x in content for x in ['env', 'environment', 'variable not set']):
        return 'env_error'
    if any(x in content for x in ['timeout', 'watchdog', 'TIMEOUT']):
        return 'timeout'
    if any(x in content for x in ['error', 'failed', 'failure', 'ERROR']):
        return 'task_failure'
    return None
```

#### 3. `_parse_directive_file()` — error_type 필드 추가

반환 dict에 `error_type` 추가:
```python
error_type = _classify_error(raw[:2000]) if status == "error" else None

return {
    "task_id": task_id,
    "title": title,
    "status": status,
    "project": project,
    "error_type": error_type or "",
    "created_at": created_at,
    "file_path": str(filepath),
}
```

#### 4. `get_directives()` 응답 구조 수정 (T-072 핵심 수정)

**변경 전 (버그):**
```python
"error": error_breakdown,  # dict 객체 → React Error #31 원인!
```

**변경 후 (수정):**
```python
"error": f_error,                        # T-072: 숫자로만 (React Error #31 방지)
"error_breakdown": error_breakdown,      # T-072: 별도 키로 분리
"summary": {
    "completed": f_completed,
    "error": f_error,
    "running": f_running,
    "timeout": error_breakdown.get("timeout", 0),
    "pending": 0,
},
"project_breakdown": by_project,
"by_project": by_project,
"items": unique_directives,              # T-072: items 키 추가 (별칭)
"directives": unique_directives,
```

#### 5. `get_reports()` 동일하게 정리

```python
"error": len(error_reports),             # T-072: 숫자로만 (React Error #31 방지)
"error_breakdown": error_breakdown,      # T-072: 별도 키로 분리
```

#### 6. `get_task_history()` 확인

- `remote_servers`: REMOTE_211, REMOTE_114 정상 (REMOTE_116 없음, 이미 올바름)
- `finished_at`: 이미 포함 (auto_report는 started_at과 동일, task_result는 실제 완료시각)

---

### Part C — Frontend 4탭 구조 확인 및 보강

**수정 파일:** `/root/aads/aads-dashboard/src/app/tasks/page.tsx`

4탭 구조 이미 구현됨 (지시서/보고서/원격작업/분석). 추가 보강:

1. `Directive` 인터페이스에 `started_at?`, `completed_at?`, `duration_seconds?` 추가
2. `DirectiveSummary` 인터페이스에 `error_breakdown?`, `by_project?` 추가
3. 에러 KPI 카드: `data.error_breakdown` API 필드 우선 사용

**테이블 컬럼 구조:**
- Task ID | 제목 | 프로젝트(뱃지) | 상태(뱃지) | 에러유형 | 시작 | 완료

**프로젝트 뱃지 색상:**
- AADS=blue, KIS=purple, ShortFlow=orange, NewTalk=green, GO100=yellow, NAS=pink

---

### Part D — 빌드 및 배포

#### npm run build 결과

```
> aads-dashboard@0.1.0 build
> next build

▲ Next.js 16.1.6 (Turbopack)

✓ Compiled successfully in 20.8s
✓ Generating static pages using 7 workers (12/12) in 824.4ms

Route (app)
┌ ○ /
├ ○ /_not-found
├ ○ /conversations
├ ○ /decisions
├ ○ /login
├ ○ /managers
├ ○ /project-status
├ ƒ /project-status/[id]
├ ○ /projects
├ ƒ /projects/[id]
├ ƒ /projects/[id]/costs
├ ƒ /projects/[id]/stream
├ ○ /settings
└ ○ /tasks

빌드 성공, 에러 수: 0
```

#### Docker compose 결과

```
DOCKER_BUILDKIT=0 BUILDX_NO_DEFAULT_LOAD=1 docker compose -f /root/aads/aads-server/docker-compose.prod.yml up -d --build

Successfully built 8e8b19450b12
Successfully tagged aads-server-aads-dashboard:latest
 Container aads-redis  Running
 Container aads-dashboard  Recreated
 Container aads-postgres  Running
 Container aads-server  Recreated
 Container aads-dashboard  Started
 Container aads-server  Started
```

#### curl 검증 결과

```
curl -s https://aads.newtalk.kr/api/v1/dashboard/directives
→ HTTP 200
→ {"status":"ok","total":85,"unique_tasks":75,"running":0,"completed":54,"error":20,
   "error_breakdown":{"auth_expired":3,"permission_denied":12,"env_error":0,"timeout":0,"task_failure":5},
   "summary":{"completed":54,"error":20,"running":0,"timeout":0,"pending":0},
   ...}
→ error 키 타입: int ✅

curl -s https://aads.newtalk.kr/api/v1/dashboard/reports
→ HTTP 200
→ total: 75, error type: int, error val: 20
→ error_breakdown keys: ['total', 'auth_expired', 'permission_denied', 'env_error', 'timeout', 'task_failure'] ✅

curl -s https://aads.newtalk.kr/api/v1/dashboard/task-history
→ HTTP 200
→ total: 25, remote_servers: ['REMOTE_211', 'REMOTE_114']
→ first task keys: ['task_id', 'server', 'status', 'message_type', 'started_at', 'finished_at', 'from_agent', 'memory_type'] ✅

curl -sL https://aads.newtalk.kr/tasks
→ HTTP 200 (307 redirect → 200) ✅
```

---

### Part E — Git Push

#### aads-server

```
cd /root/aads/aads-server
git add app/api/project_dashboard.py
git commit -m 'feat(T-072): fix React#31 + flatten API + classify project/error + parse taskID'
git push

→ [main ee3df33] feat(T-072): fix React#31 + flatten API + classify project/error + parse taskID
→ 1 file changed, 170 insertions(+), 89 deletions(-)
→ To https://github.com/moongoby-GO100/aads-server.git
→    da06212..ee3df33  main -> main
→ SHA: ee3df33
```

#### aads-dashboard

```
cd /root/aads/aads-dashboard
git add src/app/tasks/page.tsx src/lib/api.ts
git commit -m 'feat(T-072): 4-tab Tasks page + KPI + filters + safe rendering'
git push

→ [main ca2c27c] feat(T-072): 4-tab Tasks page + KPI + filters + safe rendering
→ 2 files changed, 51 insertions(+), 26 deletions(-)
→ To https://github.com/moongoby-GO100/aads-dashboard.git
→    b8e3b3d..ca2c27c  main -> main
→ SHA: ca2c27c
```

#### aads-docs

```
cd /root/aads/aads-docs
git add handover/handover-v5.13.md
git commit -m 'docs(T-072): HANDOVER v5.13 Tasks page rebuild'
git push

→ [main e6cd12a] docs(T-072): HANDOVER v5.13 Tasks page rebuild
→ 1 file changed, 63 insertions(+)
→ create mode 100644 handover/handover-v5.13.md
→ To https://github.com/moongoby-GO100/aads-docs.git
→    ad41674..e6cd12a  main -> main
→ SHA: e6cd12a
```

---

## 최종 검증 요약

| 항목 | 결과 |
|------|------|
| React Error #31 | 해결 (error_type safeRender + status 객체 처리 + backend error 키 숫자화) |
| /api/v1/dashboard/directives | HTTP 200 ✅ |
| /api/v1/dashboard/reports | HTTP 200 ✅ |
| /api/v1/dashboard/task-history | HTTP 200 ✅ |
| /tasks | HTTP 200 ✅ |
| Build | 성공 (0 에러) ✅ |
| Docker deploy | 성공 ✅ |
| aads-server commit | ee3df33 ✅ |
| aads-dashboard commit | ca2c27c ✅ |
| aads-docs commit | e6cd12a ✅ |
