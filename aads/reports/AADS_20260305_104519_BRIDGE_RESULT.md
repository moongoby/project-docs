---
project: AADS
task_id: T-058
completed_at: 2026-03-05T10:51:17+09:00
---

# T-058 실행 결과 전문

## 지시 내용 (원문)

Task ID: T-058 제목: project_dashboard.py 상세API 및 conversation_count 버그 수정 서버: 68 (aads.newtalk.kr) 우선순위: P1-HIGH 예상 시간: 12분 예상 비용: $0 의존성: T-057 완료

배경

T-057에서 /projects/dashboard 목록 API의 project_status override는 성공했으나, 2가지 잔여 버그가 있음:

/projects/dashboard/{project_id} 상세 API에서 progress_percent=0 반환 (override 로직 누락)
목록 API에서 conversation_count가 aads(22)만 반영, 나머지 프로젝트 0

---

## Step 1: 백업

### 실행 명령
```
cp /root/aads/aads-server/app/api/project_dashboard.py /root/aads/aads-server/app/api/project_dashboard.py.bak.T058
```

### 실행 결과
```
Backup OK
```

---

## Step 2: 상세 API override 수정

### 버그 원인
`get_project_detail` 함수에 `go100_user_memory` 테이블의 `project_status` 레코드를 조회하여 `progress_percent`, `total_tasks`, `completed_tasks`, `handover_url`, `key_issues`를 override하는 로직이 누락되어 있었음.

### 수정 내용 (파일: /root/aads/aads-server/app/api/project_dashboard.py)

#### 추가 1: async with conn 블록 내 — status_row 쿼리 추가
```python
            # go100_user_memory project_status 최신 레코드 조회
            status_row = await conn.fetchrow(
                """
                SELECT content FROM go100_user_memory
                WHERE user_id = 2 AND memory_type = 'project_status'
                  AND content->>'project_id' = $1
                ORDER BY created_at DESC LIMIT 1
                """, project_id
            )
```

#### 추가 2: 변수 초기화 (tasks 초기화 블록에 추가)
```python
        total_tasks = 0
        completed_tasks = 0
        handover_url = ""
        key_issues: List[str] = []
```

#### 추가 3: sys_rows 루프 이후 — override 로직
```python
        # project_status override from go100_user_memory
        if status_row:
            s = status_row["content"] if isinstance(status_row["content"], dict) else json.loads(status_row["content"])
            progress_percent = s.get("progress_percent", progress_percent)
            total_tasks = s.get("total_tasks", total_tasks)
            completed_tasks = s.get("completed_tasks", completed_tasks)
            handover_url = s.get("handover_url", handover_url)
            key_issues = s.get("key_issues", key_issues)
            if s.get("status"):
                status = s["status"]
```

#### 추가 4: return 딕셔너리에 필드 추가
```python
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "handover_url": handover_url,
            "key_issues": key_issues,
```

---

## Step 3: conversation_count 매핑 수정

### 버그 원인 (DB 조사 후 발견)

`aads_conversations` 테이블이 해당 서버 DB에 존재하지 않음 (UndefinedTableError). 대화 데이터는 `system_memory`의 `conversation:*` 카테고리로 관리됨.

DB 실제 데이터 확인:
```
conversation:sf: 69
conversation:sales: 58
conversation:kis: 34
conversation:aads: 22
```

`conv_rows` 처리 시 `proj_key = r["category"].replace("conversation:", "")` → "sf", "sales", "kis" 그대로 `conv_stats`에 저장됨. 이후 `conv_stats.get("shortflow", {})` 등으로 조회 시 매칭 실패 → conversation_count=0.

### 수정 내용

#### 변경 전
```python
        conv_stats: Dict[str, Dict] = {}
        total_conversations = 0
        for r in conv_rows:
            # category: conversation:go100 → project_id: go100
            proj_key = r["category"].replace("conversation:", "")
            cnt = r["cnt"]
            total_conversations += cnt
            conv_stats[proj_key] = {
                "count": cnt,
                "last_updated": str(r["last_updated"]),
            }
```

#### 변경 후
```python
        # conversation 통계
        conv_stats: Dict[str, Dict] = {}
        total_conversations = 0
        for r in conv_rows:
            # category: conversation:sf → proj_key: sf → mapped: shortflow (CONV_PROJECT_MAP)
            proj_key = r["category"].replace("conversation:", "")
            proj_key = CONV_PROJECT_MAP.get(proj_key, proj_key)
            cnt = r["cnt"]
            total_conversations += cnt
            if proj_key in conv_stats:
                conv_stats[proj_key]["count"] += cnt
            else:
                conv_stats[proj_key] = {
                    "count": cnt,
                    "last_updated": str(r["last_updated"]),
                }
```

---

## Step 4: 배포

### 컨테이너 확인
```
CONTAINER=08c2cda9300bef14f0a71ff47ea88bc29d85b44ca3ddde5738c3d97cd9804f79  ← DB 컨테이너 (오답)
```

컨테이너 목록 전체 확인:
```
CONTAINER                                                           IMAGE    RUNTIME
08c2cda9300bef14f0a71ff47ea88bc29d85b44ca3ddde5738c3d97cd9804f79    -        io.containerd.runc.v2
66a2d415ab32ae1b47fccaa414457c9f276577355181534a47a5c8e741798fb9    -        io.containerd.runc.v2
dc6c14b59bf3349cb4579b6792ddf54e30adcbcac1f8eb5c9545997a9abde2d9    -        io.containerd.runc.v2
e48383aa0587ef010416a1d7d61074b3470ab0025986d2cda7b66edece7b201e    -        io.containerd.runc.v2
```

실제 Python API 컨테이너: `e48383aa0587ef010416a1d7d61074b3470ab0025986d2cda7b66edece7b201e`
(`/app` 내에 Dockerfile, app/, supervisord.conf 등 존재 확인)

### 1차 배포 (Step 2 반영 후)

```
INJECT_OK
aads-api: stopped
aads-api: started
RESTART_OK
```

1차 검증 결과 (conversation_count 아직 0):
```
go100: progress=97, conv=0
kis_v41: progress=85, conv=0
shortflow: progress=80, conv=0
nas: progress=65, conv=0
newtalk_v2: progress=60, conv=0
aads: progress=75, conv=22
```
→ progress=97 수정 확인. conversation_count 문제 추가 조사 필요.

### 2차 배포 (Step 3 수정 후)

```
INJECT_OK
aads-api: stopped
aads-api: started
RESTART_OK
```

---

## Step 5: 검증

### 목록 API 결과: GET /projects/dashboard
```
go100: progress=97, conv=0
kis_v41: progress=85, conv=34
shortflow: progress=80, conv=69
nas: progress=65, conv=0
newtalk_v2: progress=60, conv=58
aads: progress=75, conv=22
```

### 상세 API 결과: GET /projects/dashboard/go100
```
progress=97
```

### 완료 기준 대조

| 기준 | 기대값 | 실제값 | 결과 |
|------|--------|--------|------|
| GET /projects/dashboard/go100 → progress_percent | 97 | 97 | ✓ PASS |
| GET /projects/dashboard → shortflow conversation_count | ≥50 | 69 | ✓ PASS |
| GET /projects/dashboard → kis_v41 conversation_count | ≥30 | 34 | ✓ PASS |

---

## Step 6: Git push

### aads-server
```
cd /root/aads/aads-server
git add app/api/project_dashboard.py
git commit -m "[AADS] fix: T-058 detail API progress override + conversation_count mapping"
```

커밋 결과:
```
[main 7824f3d] [AADS] fix: T-058 detail API progress override + conversation_count mapping
 1 file changed, 38 insertions(+), 5 deletions(-))
```

push 결과:
```
To https://github.com/moongoby-GO100/aads-server.git
   9ab699c..7824f3d  main -> main
error: update_ref failed for ref 'refs/remotes/origin/main': cannot update the ref 'refs/remotes/origin/main': unable to append to '.git/logs/refs/remotes/origin/main': Permission denied
```
(원격 push 성공. 로컬 ref 갱신 권한 오류는 비치명적)

### aads-docs
```
cd /root/aads/aads-docs
git add reports/T-058_RESULT.md
git commit -m "[AADS] report: T-058 결과 보고서"
git push origin main
```

커밋 결과:
```
[main 930df3e] [AADS] report: T-058 결과 보고서
 1 file changed, 163 insertions(+)
 create mode 100644 reports/T-058_RESULT.md
To https://github.com/moongoby-GO100/aads-docs.git
   f74c370..930df3e  main -> main
error: update_ref failed for ref 'refs/remotes/origin/main': cannot update the ref 'refs/remotes/origin/main': unable to append to '.git/logs/refs/remotes/origin/main': Permission denied
```
(원격 push 성공. 로컬 ref 갱신 권한 오류는 비치명적)

---

## Step 7: 보고서

파일 생성: `/root/aads/aads-docs/reports/T-058_RESULT.md`
aads-docs push: 완료 (커밋 930df3e)

---

## 최종 요약

T-058의 두 가지 버그를 모두 수정하고 완료 기준을 충족함:

1. **상세 API (get_project_detail) progress_percent override 수정**: `go100_user_memory`의 `project_status` 레코드를 조회하여 progress_percent, total_tasks, completed_tasks, handover_url, key_issues를 override하는 로직 추가. GET /projects/dashboard/go100 → progress_percent=97 확인.

2. **conversation_count 매핑 수정**: `system_memory`의 `conversation:sf`, `conversation:sales`, `conversation:kis` 카테고리를 `conv_stats`에 저장할 때 `CONV_PROJECT_MAP`을 적용하여 "shortflow"(69), "newtalk_v2"(58), "kis_v41"(34), "aads"(22)로 올바르게 매핑.

Git push: aads-server(7824f3d), aads-docs(930df3e) 모두 완료.
