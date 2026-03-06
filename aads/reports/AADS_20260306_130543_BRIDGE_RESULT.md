---
project: AADS
task_id: AADS-110
completed_at: 2026-03-06T13:19:59+09:00
---

# AADS-110 완료 보고: 대화창 컨텍스트 주입에 서버 환경 스냅샷 자동 포함

## 1. 작업 개요

- **Task ID**: AADS-110
- **제목**: 대화창 컨텍스트 주입에 서버 환경 스냅샷 자동 포함
- **서버**: 68 (aads.newtalk.kr)
- **우선순위**: P1-HIGH
- **의존성**: AADS-108, T-103 (대화창 관리 API)

---

## 2. 수정 파일

### `/root/aads/aads-server/app/api/channels.py`

#### 2-1. import 추가

```python
from datetime import datetime, timezone, timedelta  # timedelta 추가

KST = timezone(timedelta(hours=9))  # KST 상수 추가
```

#### 2-2. 신규 함수: `get_server_environment(server: str) -> dict`

```python
async def get_server_environment(server: str) -> dict:
    """system_memory에서 서버 환경 스냅샷 조회 (category=server_environment, key=env_{server})."""
    conn = await _get_conn()
    try:
        row = await conn.fetchrow(
            "SELECT value FROM system_memory WHERE category = 'server_environment' AND key = $1",
            f"env_{server}",
        )
        if not row:
            return {"collected_at": "스냅샷 없음", "runtimes": {}, "projects": {}, "databases": {}, "services": {}}
        raw = row["value"]
        return json.loads(raw) if isinstance(raw, str) else dict(raw)
    except Exception:
        return {"collected_at": "조회 실패", "runtimes": {}, "projects": {}, "databases": {}, "services": {}}
    finally:
        await conn.close()
```

#### 2-3. 신규 함수: `format_runtimes(runtimes: dict) -> str`

```python
def format_runtimes(runtimes: dict) -> str:
    if not runtimes:
        return "- (데이터 없음)"
    lines = []
    for k, v in runtimes.items():
        lines.append(f"- **{k}**: {v}")
    return "\n".join(lines)
```

#### 2-4. 신규 함수: `format_projects(projects: dict) -> str`

```python
def format_projects(projects: dict) -> str:
    if not projects:
        return "- (데이터 없음)"
    lines = []
    for path, info in projects.items():
        if not isinstance(info, dict):
            lines.append(f"- `{path}`: {info}")
            continue
        exists = info.get("exists", True)
        if not exists:
            lines.append(f"- `{path}`: 디렉터리 없음")
            continue
        branch = info.get("git_branch", "-")
        last3 = info.get("git_last3", "-")
        lines.append(f"- `{path}` (브랜치: {branch})")
        if last3 and last3 != "-":
            for l in last3.splitlines()[:3]:
                lines.append(f"  - {l}")
    return "\n".join(lines) if lines else "- (데이터 없음)"
```

#### 2-5. 신규 함수: `format_databases(databases: dict) -> str`

```python
def format_databases(databases: dict) -> str:
    if not databases:
        return "- (데이터 없음)"
    lines = []
    for db_key, info in databases.items():
        lines.append(f"- **{db_key}**")
        if isinstance(info, dict):
            schema = info.get("schema", "")
            if schema:
                for l in schema.splitlines()[:10]:
                    lines.append(f"  {l}")
    return "\n".join(lines) if lines else "- (데이터 없음)"
```

#### 2-6. 신규 함수: `format_services(services: dict) -> str`

```python
def format_services(services: dict) -> str:
    if not services:
        return "- (데이터 없음)"
    lines = []
    systemd = services.get("systemd_active", "")
    docker = services.get("docker", "")
    if systemd:
        lines.append("**systemd 활성 서비스:**")
        for l in systemd.splitlines()[:15]:
            lines.append(f"  {l}")
    if docker:
        lines.append("**Docker 컨테이너:**")
        for l in docker.splitlines()[:10]:
            lines.append(f"  {l}")
    return "\n".join(lines) if lines else "- (데이터 없음)"
```

#### 2-7. 수정 함수: `get_context_package` (AADS-110 핵심 변경)

주요 변경 내용:
- `server = ch.get("server", "68")` 로 채널 연결 서버 추출
- `env_snapshot = await get_server_environment(server)` 로 환경 스냅샷 조회
- 서버 환경 섹션(런타임/프로젝트 디렉터리/DB 스키마/서비스 상태) 컨텍스트 패키지에 삽입
- 응답 JSON에 `"server"`, `"env_snapshot_at"` 필드 추가
- `datetime.now(timezone.utc)` → `datetime.now(KST)` 로 KST 적용

---

## 3. NTV2_MGR 채널 서버 확인

```json
GET https://aads.newtalk.kr/api/v1/channels/NTV2_MGR

{
    "channel": {
        "id": "NTV2_MGR",
        "name": "NewTalk V2 매니저",
        "description": "NewTalk V2 채팅 서비스",
        "url": "https://www.genspark.ai",
        "status": "active",
        "project": "NewTalk",
        "server": "114",
        "context_docs": [
            {
                "url": "https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md",
                "role": "CONTEXT"
            }
        ],
        "system_prompt": "너는 NewTalk V2 프로젝트 매니저다.",
        "created_at": "2026-03-06T03:05:00+00:00",
        "updated_at": "2026-03-06T03:36:20.154221+00:00"
    }
}
```

NTV2_MGR `"server": "114"` 확인 완료 ✅

---

## 4. Git 커밋

- **aads-server**: `82a5b79` — `[AADS] feat(AADS-110): context-package에 서버 환경 스냅샷 자동 포함`
  - push 200 ✅
  - 변경: `app/api/channels.py` (+110 -5)
- **aads-docs**: `738e318` — `[AADS] docs(AADS-110): HANDOVER v5.32 — context-package 서버 환경 스냅샷 자동 포함 완료 기록`
  - push 200 ✅

---

## 5. Docker 재배포

```
DOCKER_BUILDKIT=0 docker-compose -f docker-compose.prod.yml build aads-server
→ Successfully built 591c1e260cdb
→ Successfully tagged aads-server-aads-server:latest

DOCKER_BUILDKIT=0 docker-compose -f docker-compose.prod.yml up -d aads-server
→ Container aads-server Recreated
→ Container aads-server Started
```

---

## 6. 검증 결과

### Health Check
```
GET https://aads.newtalk.kr/api/v1/health
→ {"status":"ok","graph_ready":true,"version":"0.1.0",...}
HTTP: 200 ✅
```

### NTV2_MGR context-package 응답

```json
GET https://aads.newtalk.kr/api/v1/channels/NTV2_MGR/context-package

{
    "channel_id": "NTV2_MGR",
    "channel_name": "NewTalk V2 매니저",
    "generated_at": "2026-03-06 13:19 KST",
    "server": "114",
    "env_snapshot_at": "스냅샷 없음",
    "context_package": "# NewTalk V2 매니저 컨텍스트 패키지\n> 자동 생성: 2026-03-06 13:19 KST\n> 프로젝트: NewTalk | 서버: 114\n\n## 시스템 프롬프트\n너는 NewTalk V2 프로젝트 매니저다.\n\n## 서버 114 실시간 환경 (스냅샷: 스냅샷 없음)\n\n### 런타임\n- (데이터 없음)\n\n### 프로젝트 디렉터리\n- (데이터 없음)\n\n### DB 스키마\n- (데이터 없음)\n\n### 서비스 상태\n- (데이터 없음)\n\n---\n## CONTEXT\n...(이하 CONTEXT.md 내용)...",
    "doc_count": 1
}
HTTP: 200 ✅
```

**비고**: `env_snapshot_at: "스냅샷 없음"` — 114서버에서 collect_env_snapshot.py가 실행되면 자동으로 스냅샷 데이터가 채워짐. 엔드포인트 구조 정상 동작 확인.

---

## 7. HANDOVER 갱신

- **버전**: v5.32
- **내용**: AADS-110 완료 기록, AADS Task ID 카운터 AADS-110 → AADS-111 갱신
- **파일**: `/root/aads/aads-docs/HANDOVER.md`
- **커밋**: `738e318`, push 200 ✅

---

## 8. 완료 요약

| 항목 | 결과 |
|------|------|
| channels.py get_context_package 서버 환경 섹션 추가 | ✅ |
| get_server_environment() 함수 구현 | ✅ |
| format_runtimes/projects/databases/services 포맷터 구현 | ✅ |
| NTV2_MGR server=114 확인 | ✅ |
| aads-server commit 82a5b79 push | ✅ 200 |
| Docker rebuild + 재배포 | ✅ |
| API health check | ✅ HTTP 200 |
| context-package endpoint 검증 | ✅ HTTP 200 |
| HANDOVER v5.32 갱신 | ✅ |
| aads-docs commit 738e318 push | ✅ 200 |

---

[CURSOR-AADS] push 완료
작업: AADS-110 대화창 컨텍스트에 환경 스냅샷 포함
커밋: 82a5b79
HTTP: 200
검증: NTV2_MGR context-package에 서버 114 환경 섹션 포함 ✅
HANDOVER: v5.32 업데이트 완료
다음: 지시 대기
