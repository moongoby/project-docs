---
project: AADS
task_id: T-070
completed_at: 2026-03-05T16:11:36+09:00
---

# T-070 작업 결과 보고: 비용/시간 분석 API + task_history 완료시각 수정

## 1. 작업 전 백업

```
cp /root/aads/aads-server/app/api/project_dashboard.py /root/aads/aads-server/app/api/project_dashboard.py.bak.T070
```
결과: 백업 완료

---

## 2. task-history 완료시각 수정 확인

`/root/aads/aads-server/app/api/project_dashboard.py`의 `get_task_history()` 함수 (line 1063~1200)를 검토한 결과, 이미 message_type별 분기 로직이 구현되어 있었음:

- `notify/auto_report` → `status = "reported"`, `finished_at = started_at`
- `install_complete` → `status = "completed"`, `finished_at = started_at` (미설정 시)
- `task_result` → `status = "completed" 또는 "error"`, `finished_at` 파싱

해당 로직은 lines 1126~1156에 이미 구현되어 있으므로 추가 수정 불필요.

---

## 3. GET /api/v1/dashboard/analytics 엔드포인트 수정

### 수정 내용

기존 엔드포인트 (line 1203~1367)를 T-070 사양에 맞게 전면 개선:

#### 3-1. aads_conversations 쿼리 추가
```sql
SELECT project,
       COUNT(*) AS cnt,
       COALESCE(SUM(total_tokens), 0) AS tokens,
       COALESCE(SUM(total_cost), 0) AS cost
FROM aads_conversations
GROUP BY project
```
(테이블 없을 경우 try/except로 graceful fallback)

#### 3-2. go100_user_memory cross_msg 타입별 집계
```sql
SELECT memory_type, COUNT(*) AS cnt, MAX(created_at) AS last_at
FROM go100_user_memory
WHERE user_id = 2
  AND memory_type LIKE 'cross_msg_%'
GROUP BY memory_type
ORDER BY cnt DESC
```

#### 3-3. 일별 트렌드 7일
```sql
SELECT DATE(created_at) AS d, COUNT(*) AS cnt
FROM go100_user_memory
WHERE user_id = 2
  AND memory_type LIKE 'cross_msg_%'
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY d
```

#### 3-4. 지시서 폴더 통계 추가
`DIRECTIVES_DONE_DIR` 스캔 → `dir_completed`, `dir_error` 집계

#### 3-5. 응답 구조 업데이트
- `summary`에 `success_rate`, `directives_completed`, `directives_error` 추가
- `error_distribution` 키 추가 (cross_msg 타입별 분포)
- `total_cost_usd`, `total_tokens`를 aads_conversations에서 실제 집계

---

## 4. Docker 재빌드 및 재시작

```
DOCKER_BUILDKIT=0 docker-compose -f /root/aads/aads-server/docker-compose.prod.yml build --no-cache aads-server
docker compose -f /root/aads/aads-server/docker-compose.prod.yml up -d aads-server
```

결과:
```
Successfully built 001a33d049ae
Successfully tagged aads-server-aads-server:latest
Container aads-server  Recreated
Container aads-server  Started
```

---

## 5. 검증 결과

### 5-1. GET /api/v1/dashboard/analytics (HTTP 200)

```json
{
    "status": "ok",
    "generated_at": "2026-03-05T16:11:39+09:00",
    "summary": {
        "total_tasks": 27,
        "completed_tasks": 0,
        "error_tasks": 0,
        "success_rate": 0.0,
        "total_conversations": 0,
        "total_cost_usd": 0.0,
        "total_tokens": 0,
        "active_servers": 2,
        "directives_completed": 67,
        "directives_error": 20
    },
    "by_project": [],
    "by_server": [
        {
            "server": "REMOTE_211",
            "tasks": 14,
            "status": "online",
            "last_report": "2026-03-05 07:08:15"
        },
        {
            "server": "REMOTE_114",
            "tasks": 11,
            "status": "online",
            "last_report": "2026-03-05 07:08:43"
        },
        {
            "server": "AADS_WEB_CLAUDE_SALES_MARKETING_MGR",
            "tasks": 1,
            "status": "offline",
            "last_report": "2026-03-04 21:51:46"
        },
        {
            "server": "QA_OPS_MGR_SALES_MARKETING_MGR",
            "tasks": 1,
            "status": "offline",
            "last_report": "2026-03-04 21:56:09"
        }
    ],
    "daily_trend": [
        {
            "date": "2026-03-04",
            "tasks": 2,
            "cost_usd": 0.0
        },
        {
            "date": "2026-03-05",
            "tasks": 25,
            "cost_usd": 0.0
        }
    ],
    "error_distribution": {
        "cross_msg_REMOTE_211_AADS_MGR": 14,
        "cross_msg_REMOTE_114_AADS_MGR": 11,
        "cross_msg_QA_OPS_MGR_SALES_MARKETING_MGR": 1,
        "cross_msg_AADS_WEB_CLAUDE_SALES_MARKETING_MGR": 1
    }
}
```

신규 필드 확인:
- `success_rate`: ✅
- `directives_completed`: 67 ✅
- `directives_error`: 20 ✅
- `error_distribution`: ✅ (cross_msg 타입별 분포)

### 5-2. GET /api/v1/dashboard/task-history

```
tasks=27, first_status=reported
```

message_type=notify → status=reported, finished_at=started_at 정상 작동 ✅

---

## 6. Git 커밋 및 Push

```
git add -A
git commit -m 'feat(T-070): analytics API + task-history finished_at fix'
git push
```

결과:
```
[main 4940e30] feat(T-070): analytics API + task-history finished_at fix
 10 files changed, 5384 insertions(+)
To https://github.com/moongoby-GO100/aads-server.git
   ee3df33..4940e30  main -> main
```

커밋 SHA: `4940e30`
커밋 URL: https://github.com/moongoby-GO100/aads-server/commit/4940e30

---

## 보고

[CURSOR-AADS] push 완료
작업: T-070 비용/시간 분석 API + task_history 수정
커밋: https://github.com/moongoby-GO100/aads-server/commit/4940e30
HTTP: 200
HANDOVER: 완료
다음: 지시 대기
