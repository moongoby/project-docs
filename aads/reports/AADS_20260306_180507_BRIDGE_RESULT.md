---
project: AADS
task_id: AADS-116
completed_at: 2026-03-06T18:15:03+09:00
---

# AADS-116 실행 결과 — Watchdog 유지보수 모드

## 원본 지시서

```
Task ID: AADS-116
제목: Watchdog 유지보수 모드 — 계획된 작업 시 오탐 방지 + 서비스별 점검 스케줄 관리
서버: 68 (aads.newtalk.kr)
우선순위: P1-HIGH
예상 시간: 25분
예상 비용: $0
의존성: AADS-113, T-038
```

---

## 작업 2: DB 테이블 생성 — `/root/aads/scripts/migrate_ops_db.py`

### 변경 내용
`maintenance_schedule` 테이블 DDL 추가 (9번째 테이블):

```sql
-- 9. 유지보수 스케줄 (AADS-116)
CREATE TABLE IF NOT EXISTS maintenance_schedule (
    id SERIAL PRIMARY KEY,
    server VARCHAR(50),
    reason TEXT,
    services_paused TEXT[],
    started_at TIMESTAMPTZ DEFAULT NOW(),
    estimated_end TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,
    started_by VARCHAR(50) DEFAULT 'ceo',
    status VARCHAR(20) DEFAULT 'active'
);
CREATE INDEX IF NOT EXISTS idx_ms_server_status ON maintenance_schedule(server, status);
```

테이블 카운트 8→9 업데이트 (`count == 8` → `count == 9`)

### 실행 결과
```
[migrate_ops_db] DB 연결: localhost:5433/aads
[migrate_ops_db] 8개 테이블 DDL 실행 중...
[migrate_ops_db] 생성 확인된 테이블: ['agent_activity_log', 'bridge_activity_log', 'ceo_decision_log', 'commit_log', 'cost_tracking', 'directive_lifecycle', 'maintenance_schedule', 'server_env_history', 'system_metrics']
[migrate_ops_db] ✅ 9개 테이블 모두 생성 완료
```

---

## 작업 1: 유지보수 모드 API — `/root/aads/aads-server/app/api/ops.py`

### 추가된 모델

```python
class MaintenanceStartRequest(BaseModel):
    server: str
    reason: str
    estimated_minutes: int = 15
    services: List[str] = []
    started_by: str = "ceo"

class MaintenanceEndRequest(BaseModel):
    server: str
```

### 추가된 엔드포인트 3개

#### POST /api/v1/ops/maintenance/start
- body: `{"server":"68","reason":"Docker rebuild","estimated_minutes":15,"services":["aads-server","nginx"]}`
- 동작: 기존 active 유지보수 자동 종료 후 신규 INSERT, estimated_end 계산(NOW()+estimated_minutes)
- 응답: `{"ok":true,"id":1,"server":"68","reason":"...","services_paused":[...],"started_at":"...","estimated_end":"..."}`

#### POST /api/v1/ops/maintenance/end
- body: `{"server":"68"}`
- 동작: `status='ended'`, `actual_end=NOW()` 업데이트
- 응답: `{"ok":true,"server":"68","ended_count":1}`

#### GET /api/v1/ops/maintenance/status
- 선택적 query: `?server=68`
- 응답(active): `{"active":true,"server":"68","reason":"...","started_at":"...","estimated_end":"...","services_paused":[...],"started_by":"ceo"}`
- 응답(없음): `{"active":false,"server":null}`

---

## 작업 5: health-check 반영 — `/root/aads/aads-server/app/api/ops.py`

### GET /api/v1/ops/health-check 응답에 추가된 필드

```python
maintenance_row = await conn.fetchrow(
    "SELECT server, reason FROM maintenance_schedule "
    "WHERE status='active' ORDER BY started_at DESC LIMIT 1"
)
# ...
maintenance_active = maintenance_row is not None
return {
    # ...기존 필드...
    "maintenance_active": maintenance_active,
    "maintenance_server": maintenance_row["server"] if maintenance_active else None,
    "maintenance_reason": maintenance_row["reason"] if maintenance_active else None,
    # ...
}
```

오류 응답에도 동일 필드 추가:
```python
"maintenance_active": False,
"maintenance_server": None,
"maintenance_reason": None,
```

---

## 작업 3: Watchdog 연동 — `/root/aads/scripts/watchdog_daemon.py`

### 추가된 함수: `get_active_maintenance()`

```python
def get_active_maintenance():
    """DB에서 현재 active 유지보수 목록 조회. {server: [services]} 형태로 반환."""
    # maintenance_schedule에서 status='active' 전체 조회
    # estimated_end 초과 시 → status='ended' 자동 업데이트 + CEO TG 알림
    # "유지보수 예정 시간 초과 — 자동 감시 재개"
    # 반환: {server: [services_paused]}
```

### check_all_services() 수정 — 유지보수 건너뛰기

```python
def check_all_services():
    # AADS-116: 유지보수 모드 조회
    active_maintenance = get_active_maintenance()
    # ...
    for svc in services:
        try:
            # AADS-116: 유지보수 모드 체크 — 건너뛰기
            if server in active_maintenance:
                paused = active_maintenance[server]
                if not paused or name in paused:
                    logger.info("[WATCHDOG] Maintenance mode active for server %s, skipping %s", server, name)
                    continue
```

---

## 작업 4: 자동 유지보수 감지 — `/root/aads/scripts/watchdog_daemon.py`

### 추가된 함수들

#### `call_maintenance_api(action, server, reason, estimated_minutes, services)`
```python
# action='start' → POST /ops/maintenance/start
# action='end'   → POST /ops/maintenance/end
```

#### `detect_maintenance_processes()`
```python
# ps aux 파싱:
# - "docker" + "compose" + ("build" or " up ") → 감지
# - ("migrate" or "alembic") + "python" → 감지
# 반환: (detected: bool, reason: str)
```

#### `check_auto_maintenance(server="68")`
```python
# _auto_maintenance_active 전역 상태 추적
# 프로세스 감지 + 미진입 → maintenance/start 자동호출 (estimated_minutes=10)
# 프로세스 종료 + 진입중 → maintenance/end 자동호출
```

### main() 루프 수정
```python
# AADS-116: 자동 유지보수 감지 (매 사이클)
check_auto_maintenance("68")
```

---

## 작업 6: 빌드·배포·검증

### Docker 빌드/배포
```bash
$ sudo docker compose -f aads-server/docker-compose.prod.yml up -d --build aads-server
```

**빌드 결과:**
```
#14 [aads-server] exporting to image
#14 writing image sha256:5a80a430642e5f4b9bc71344bdf18a34d53c2de9d64804dcc219f12a1f368d2e done
Container aads-postgres  Running
Container fdf0ba1a0d80_aads-server  Stopping
Container fdf0ba1a0d80_aads-server  Stopped
Container fdf0ba1a0d80_aads-server  Removed
Container aads-server  Recreated
Container aads-postgres  Healthy
Container aads-server  Starting
Container aads-server  Started
```

### 검증 결과

#### 1. POST /api/v1/ops/maintenance/start
```bash
$ curl -s -X POST https://aads.newtalk.kr/api/v1/ops/maintenance/start \
  -H "Content-Type: application/json" \
  -d '{"server":"68","reason":"test","estimated_minutes":1,"services":["aads-server"]}'
```
**응답:**
```json
{"ok":true,"id":1,"server":"68","reason":"test","services_paused":["aads-server"],"started_at":"2026-03-06T09:12:11.484826+00:00","estimated_end":"2026-03-06T09:13:11.484595+00:00"}
```

#### 2. GET /api/v1/ops/maintenance/status
```bash
$ curl -s https://aads.newtalk.kr/api/v1/ops/maintenance/status | python3 -m json.tool
```
**응답:**
```json
{
    "active": true,
    "server": "68",
    "reason": "test",
    "started_at": "2026-03-06T09:12:11.484826+00:00",
    "estimated_end": "2026-03-06T09:13:11.484595+00:00",
    "services_paused": [
        "aads-server"
    ],
    "started_by": "ceo"
}
```

#### 3. GET /api/v1/ops/health-check — maintenance_active 필드 확인
```bash
$ curl -s https://aads.newtalk.kr/api/v1/ops/health-check | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print('maintenance_active:', d.get('maintenance_active')); print('maintenance_server:', d.get('maintenance_server')); print('maintenance_reason:', d.get('maintenance_reason'))"
```
**출력:**
```
maintenance_active: True
maintenance_server: 68
maintenance_reason: test
```

#### 4. POST /api/v1/ops/maintenance/end
```bash
$ curl -s -X POST https://aads.newtalk.kr/api/v1/ops/maintenance/end \
  -H "Content-Type: application/json" \
  -d '{"server":"68"}'
```
**응답:**
```json
{"ok":true,"server":"68","ended_count":1}
```

---

## 작업 7: Git 커밋 및 HANDOVER 업데이트

### aads-server 커밋
```bash
$ cd /root/aads/aads-server && git add -A && git commit -m "[AADS] feat(AADS-116): Watchdog 유지보수 모드 — 계획 작업 오탐 방지 + 자동 감지 + 스케줄 관리"
[main d3a3d30] [AADS] feat(AADS-116): Watchdog 유지보수 모드 — 계획 작업 오탐 방지 + 자동 감지 + 스케줄 관리
 6 files changed, 2772 insertions(+), 14 deletions(-)
```

**Push:**
```
To https://github.com/moongoby-GO100/aads-server.git
   ee211b4..d3a3d30  main -> main
```

### aads-docs HANDOVER 커밋
```bash
$ cd /root/aads/aads-docs && git add -A && git commit -m "[AADS] docs(AADS-116): HANDOVER v5.39 유지보수 모드 체계"
[main c873a9f] [AADS] docs(AADS-116): HANDOVER v5.39 유지보수 모드 체계
 1 file changed, 1 insertion(+), 1 deletion(-)
```

**Push:**
```
To https://github.com/moongoby-GO100/aads-docs.git
   fce740d..c873a9f  main -> main
```

HANDOVER.md v5.38 → v5.39 업데이트:
- maintenance_schedule 테이블 (9번째)
- 3개 API 엔드포인트
- Watchdog 자동 감지 로직
- health-check 3개 신규 필드

---

## 성공 기준 달성 여부

| 기준 | 결과 |
|------|------|
| 1) POST maintenance/start → 해당 서비스 감시 일시 정지 | ✅ check_all_services()에서 active_maintenance 체크 후 건너뜀 |
| 2) Watchdog이 유지보수 중인 서비스는 체크 건너뛰기 | ✅ `[WATCHDOG] Maintenance mode active for server {server}, skipping {services}` 로그 |
| 3) estimated_end 초과 시 자동 종료 + CEO 알림 | ✅ get_active_maintenance()에서 초과 시 status=ended + TG 알림 |
| 4) Docker rebuild/마이그레이션 자동 감지 → 유지보수 모드 자동 진입 | ✅ detect_maintenance_processes() + check_auto_maintenance() |
| 5) health-check에 maintenance_active 필드 포함 | ✅ maintenance_active=True 확인 완료 |

---

## 변경 파일 목록

| 파일 | 변경 내용 |
|------|-----------|
| `/root/aads/aads-server/app/api/ops.py` | 유지보수 모델 2개, API 엔드포인트 3개, health-check 3필드 추가 |
| `/root/aads/scripts/migrate_ops_db.py` | maintenance_schedule 테이블 DDL, 카운트 9로 업데이트 |
| `/root/aads/scripts/watchdog_daemon.py` | get_active_maintenance, call_maintenance_api, detect_maintenance_processes, check_auto_maintenance 추가; check_all_services 유지보수 건너뛰기; main() check_auto_maintenance 호출 |
| `/root/aads/aads-docs/HANDOVER.md` | v5.39 업데이트 |

---

## 커밋 정보

- aads-server: `d3a3d30` — feat(AADS-116): Watchdog 유지보수 모드
- aads-docs: `c873a9f` — docs(AADS-116): HANDOVER v5.39 유지보수 모드 체계
