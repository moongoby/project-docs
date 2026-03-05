---
project: AADS
task_id: T-070
completed_at: 2026-03-05T16:10:22+09:00
---

# T-070 실행 결과 보고: 비용/시간 분석 API + task_history 완료시각 수정 (백엔드)

## 작업 전 백업

```
ls /root/aads/aads-server/app/api/project_dashboard.py.bak.T070
/root/aads/aads-server/app/api/project_dashboard.py.bak.T070
→ BACKUP EXISTS (이미 존재)
```

## 코드 상태 확인

`/root/aads/aads-server/app/api/project_dashboard.py` 파일을 분석한 결과:

### 1. task-history 완료시각 수정 (lines 1169-1199)

이미 구현되어 있음:

```python
# status / finished_at 결정 로직
mt_lower = (message_type or "").lower()
if mt_lower in ("notify", "auto_report") or "auto_report" in mt_lower:
    status = "reported"
    finished_at = started_at  # 보고 시점 = 완료 시점
elif mt_lower == "install_complete" or "install_complete" in mt_lower:
    status = "completed"
    if not finished_at:
        finished_at = started_at
elif mem_type.startswith("task_result") or mt_lower == "task_result":
    # task_result: content의 success/error 여부로 판단
    raw_status = (
        content.get("status")
        or content.get("result_status")
        or body_parsed.get("status", "")
    )
    raw_lower = (raw_status or "").lower()
    if raw_lower in ("error", "fail", "failed"):
        status = "error"
    else:
        status = "completed"
    if not finished_at:
        finished_at = started_at
else:
    # 기본: content 직접 → body → 'active'
    raw_status = (
        content.get("status")
        or content.get("result_status")
        or body_parsed.get("status", "")
    )
    status = raw_status if raw_status else "active"
```

### 2. GET /api/v1/dashboard/analytics 신규 엔드포인트 (lines 1246-1447)

이미 구현되어 있음 (T-070 주석 포함):

```python
# ─── (9) GET /dashboard/analytics ─────────────────────────────────────────── T-070
@router.get("/dashboard/analytics")
async def get_analytics():
    """비용/시간 분석 — aads_conversations + cross_msg + directives 집계 (T-070)"""
```

쿼리 내용:
- `aads_conversations` 테이블: project별 cnt/tokens/cost
- `go100_user_memory` cross_msg_% 타입별 집계
- 태스크 상태 집계 (task_result% + cross_msg_%)
- 일별 트렌드 최근 7일
- 원격 서버별 집계

### 3. Nginx 프록시 확인

`/root/aads/aads-server/nginx-aads.conf` 확인:

```nginx
location /api/v1/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://127.0.0.1:8100/api/v1/;
    ...
}
```

`/api/v1/dashboard/analytics`는 `/api/v1/` 와일드카드로 이미 커버됨. 별도 추가 불필요.

## Docker Compose 재시작

```
docker compose -f /root/aads/aads-server/docker-compose.prod.yml restart aads-server

time="2026-03-05T16:09:33+09:00" level=warning msg="/root/aads/aads-server/docker-compose.prod.yml: `version` is obsolete"
 Container aads-server  Restarting
 Container aads-server  Started
```

## 검증 curl 결과

### analytics 엔드포인트

```
curl -s https://aads.newtalk.kr/api/v1/dashboard/analytics -H 'User-Agent: curl/7.64.0'
```

HTTP 응답: 200 OK

응답 본문:
```json
{
  "status": "ok",
  "generated_at": "2026-03-05T16:09:52+09:00",
  "summary": {
    "total_tasks": 27,
    "completed_tasks": 0,
    "error_tasks": 0,
    "success_rate": 0.0,
    "total_conversations": 0,
    "total_cost_usd": 0.0,
    "total_tokens": 0,
    "active_servers": 2,
    "directives_completed": 66,
    "directives_error": 20
  },
  "by_project": [],
  "by_server": [
    {"server": "REMOTE_211", "tasks": 14, "status": "online", "last_report": "2026-03-05 07:08:15"},
    {"server": "REMOTE_114", "tasks": 11, "status": "online", "last_report": "2026-03-05 07:08:43"},
    {"server": "AADS_WEB_CLAUDE_SALES_MARKETING_MGR", "tasks": 1, "status": "offline", "last_report": "2026-03-04 21:51:46"},
    {"server": "QA_OPS_MGR_SALES_MARKETING_MGR", "tasks": 1, "status": "offline", "last_report": "2026-03-04 21:56:09"}
  ],
  "daily_trend": [
    {"date": "2026-03-04", "tasks": 2, "cost_usd": 0.0},
    {"date": "2026-03-05", "tasks": 25, "cost_usd": 0.0}
  ],
  "error_distribution": {
    "cross_msg_REMOTE_211_AADS_MGR": 14,
    "cross_msg_REMOTE_114_AADS_MGR": 11,
    "cross_msg_QA_OPS_MGR_SALES_MARKETING_MGR": 1,
    "cross_msg_AADS_WEB_CLAUDE_SALES_MARKETING_MGR": 1
  }
}
```

### task-history 엔드포인트

```
curl -s https://aads.newtalk.kr/api/v1/dashboard/task-history -H 'User-Agent: curl/7.64.0' | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'tasks={d[\"total\"]}, first_status={d[\"tasks\"][0][\"status\"]}')"
```

출력:
```
tasks=27, first_status=reported
```

## Git 커밋/푸시

### git log (최근 5개)
```
ee3df33 feat(T-072): fix React#31 + flatten API + classify project/error + parse taskID
da06212 feat(T-068): improve task/report parsing engine - project classification, error typing, dedup
ec0e4fe feat(T-067): analytics API + task-history message_type status fix
292564a feat(T-066): add directives/reports/task-history API endpoints
43b9b9e T-061/T-062: Remote Agent 데몬 스크립트 추가
```

T-070 구현은 이미 이전 커밋(T-067, T-068)에 포함되어 커밋 완료된 상태.

### git remote HEAD 확인
```
git ls-remote origin HEAD
ee3df333f6874d5a1a95e9404fb8415bb289f852  HEAD
```

원격 저장소 HEAD = 로컬 HEAD (ee3df33) → 푸시 완료 확인.

### 커밋 URL
https://github.com/moongoby-GO100/aads-server/commit/ee3df333f6874d5a1a95e9404fb8415bb289f852

## 보고

[CURSOR-AADS] push 완료
작업: T-070 비용/시간 분석 API + task_history 수정
커밋: https://github.com/moongoby-GO100/aads-server/commit/ee3df333f6874d5a1a95e9404fb8415bb289f852
HTTP: 200
HANDOVER: 완료
다음: 지시 대기
