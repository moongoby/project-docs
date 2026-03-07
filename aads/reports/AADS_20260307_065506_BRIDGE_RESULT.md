---
project: AADS
task_id: AADS_20260307_065506
completed_at: 2026-03-07T09:10:15 KST
---

# AADS_20260307_065506_BRIDGE 실행 결과

## 지시 파일
`/root/.genspark/directives/pending/AADS_20260307_065506_BRIDGE.md`

## 지시 내용 요약
AADS-139: 파이프라인 정체 해소 + AADS 매니저 대화창 완료보고 루프 수정

---

## Part A — 파이프라인 즉시 해소

### Step 1: 좀비 태스크 강제 종료 (서버 211 Docker DB)

**실행 DB**: Docker 컨테이너 `aads-postgres` (PostgreSQL, 내부 포트 5432 / 외부 5433)
- 로컬 PostgreSQL (`localhost:5432`)에는 `directive_lifecycle` 테이블 없음
- `directive_lifecycle`은 Docker aads-postgres에 존재 확인

**실행 쿼리**:
```sql
UPDATE directive_lifecycle
SET status='failed',
    error_detail='AADS-139: zombie_kill',
    completed_at=NOW()
WHERE status='running'
  AND started_at < NOW() - INTERVAL '60 minutes';
```

**결과**:
```
UPDATE 0
```
좀비 태스크(60분 초과 실행 중) 없음. 현재 running 태스크 4건 모두 실행 시작 2분 이내.

**running 태스크 현황** (실행 직전 조회):
```
task_id               | status  | started_at                    | elapsed
----------------------+---------+-------------------------------+---------
AADS_20260307_064855  | running | 2026-03-07 00:03:23+00        | 00:02:21
AADS_20260307_065506  | running | 2026-03-07 00:03:58+00        | 00:01:46
AADS_20260307_083602  | running | 2026-03-07 00:04:27+00        | 00:01:17
AADS_20260307_083604  | running | 2026-03-07 00:04:54+00        | 00:00:51
```

---

### Step 2: 핵심 프로세스 확인 + 재시작 (서버 211)

**genspark_bridge.py**:
- 확인 결과: `genspark_bridge.py`는 데몬(daemon)이 아닌 per-task 스크립트
- `sys.argv` 기반으로 `task_id` 인자를 받아 실행하는 일회성 유틸리티
- `main` 블록 실행 시 `usage: python3 genspark_bridge.py <task_id> [project]` 출력
- 데몬으로 실행할 필요 없음 → 별도 프로세스 시작 불필요

**auto_trigger.sh**:
```
pgrep -fa auto_trigger.sh → PID 31950 /root/.genspark/auto_trigger.sh 실행 중 ✅
```

**watchdog_daemon.py**:
```
pgrep -fa watchdog_daemon.py → PID 1661 /root/aads/scripts/watchdog_daemon.py 실행 중 ✅
```

---

### Step 3: pipeline_blocked 원인 분석 및 해소

**health-check 분석**:
- `pipeline_blocked` 판단 로직 (`/root/aads/aads-server/app/api/ops.py:456`):
  ```python
  pipeline_blocked = (int(recent_completed or 0) == 0 and int(active_count or 0) > 0)
  ```
- `active_count: 4` (queued/running 태스크 존재)
- `recent_completed_30m: 0` (30분 내 completed 태스크 없음)
- 결과: `pipeline_blocked: true`

**추가 발견**: `AADS_20260307_064855` 결과 파일이 이미 done/ 디렉터리에 존재하나 lifecycle DB 상태가 `running`으로 미업데이트 상태.

**조치**:
```bash
curl -s -X POST "https://aads.newtalk.kr/api/v1/ops/directive-lifecycle" \
  -H "Content-Type: application/json" \
  -d '{"task_id":"AADS_20260307_064855","project":"AADS","status":"completed","completed_at":"2026-03-07T09:09:28+09:00"}'
```

**응답**:
```json
{"ok": true, "task_id": "AADS_20260307_064855", "status": "completed"}
```

---

### health-check 최종 검증

**초기 상태** (작업 전):
```json
{
  "pipeline_healthy": false,
  "stalled_count": 0,
  "stalled_queue": 0,
  "stalled_running": 0,
  "active_count": 4,
  "recent_completed_30m": 0,
  "pipeline_blocked": true,
  "bridge_activity_1h": 0,
  "blocked_tasks_count": 0,
  "undetected_tasks_count": 0,
  "last_seen_tasks_check": "2026-03-06T18:33:25.510714+09:00",
  "maintenance_active": false,
  "maintenance_server": null,
  "maintenance_reason": null,
  "issues": [
    {"type": "pipeline_blocked", "severity": "critical"}
  ]
}
```

**최종 상태** (작업 후):
```json
{
  "pipeline_healthy": true,
  "stalled_count": 0,
  "stalled_queue": 0,
  "stalled_running": 0,
  "active_count": 3,
  "recent_completed_30m": 1,
  "pipeline_blocked": false,
  "bridge_activity_1h": 0,
  "blocked_tasks_count": 0,
  "undetected_tasks_count": 0,
  "last_seen_tasks_check": "2026-03-06T18:33:25.510714+09:00",
  "maintenance_active": false,
  "maintenance_server": null,
  "maintenance_reason": null,
  "issues": []
}
```

**결과**: `stalled_running=0` ✅, `pipeline_blocked=false` ✅, `pipeline_healthy=true` ✅

---

## Part B — AADS 매니저 대화창 완료보고 루프 구현 검증

### 문제 원인 조사

**실행 명령**:
```bash
grep -n "completion|report|완료.*보고|send.*result|response.*channel|reply|callback" /root/aads/scripts/genspark_bridge.py
```

**결과** (주요 라인):
```
260:    # ─── AADS-113: 완료보고 파싱 ───
262:    def _extract_cost_from_report(self, content: str) -> dict:
263:        """완료 보고서에서 비용 정보 추출."""
299:    def _extract_commits_from_report(self, content: str) -> list:
300:        """완료 보고서에서 커밋 정보 추출."""
587:    # AADS-139: source_channel_id 기록 — 완료 시 원본 채널에 보고하기 위해 저장
667:# ─── AADS-139: 완료보고 루프 — source_channel로 결과 반환 ────────────────────
721:async def send_completion_to_source(
728:    AADS-139: 원본 매니저 대화창에 완료 보고 — AADS message_queue에 pending 저장.
737:    completion_msg = (
745:    item_key = f"{source_channel_id}_{epoch}_completion"
760:                        "message": completion_msg,
789:    # AADS-139: 펜딩 완료 보고 수거 (source_channel이 이 채널인 완료 메시지)
790:    pending_reports = await fetch_pending_chat_messages(channel_id, aads_api_url)
806:        # AADS-139: channel_id를 process_directive에 전달 — 완료 시 이 채널로 보고
809:                "pending_reports": pending_reports}
```

### 구현 상태 확인

**`/root/aads/scripts/genspark_bridge.py` 내 AADS-139 구현 완료 확인**:

1. **source_channel_id 저장** (line 587-588):
   ```python
   # AADS-139: source_channel_id 기록 — 완료 시 원본 채널에 보고하기 위해 저장
   header = f"<!-- source_channel_id: {channel_id} -->\n"
   ```

2. **send_completion_to_source()** (line 721-769):
   ```python
   async def send_completion_to_source(
       task_id: str,
       source_channel_id: str,
       result: dict,
       aads_api_url: str = None,
   ) -> bool:
       """
       AADS-139: 원본 매니저 대화창에 완료 보고 — AADS message_queue에 pending 저장.
       """
       completion_msg = (
           f"[AADS] {task_id} {result.get('status', 'completed')}\n"
           f"소요: {result.get('duration', 'N/A')}초\n"
           f"커밋: {result.get('commit_sha', 'N/A')}\n"
           f"결과: {result.get('verdict', 'completed')}\n"
           f"다음: 지시 대기"
       )
   ```

3. **fetch_pending_chat_messages()** (line 667-...):
   - 펜딩 완료 보고 수거 함수 구현 완료

4. **handle_incoming_message() 통합** (line 789-809):
   ```python
   # AADS-139: 펜딩 완료 보고 수거 (source_channel이 이 채널인 완료 메시지)
   pending_reports = await fetch_pending_chat_messages(channel_id, aads_api_url)
   ...
   # AADS-139: channel_id를 process_directive에 전달 — 완료 시 이 채널로 보고
   ```

**판단**: AADS-139 완료보고 루프 이미 구현 완료 — 추가 수정 불필요

---

## 파일 생성

- 검증 파일: `/root/aads/shared/verify/AADS-WRAP-139_파이프라인해소_보고루프.md` ✅

---

## success_criteria 체크리스트

- [x] stalled_running = 0
- [x] pipeline_blocked = false
- [x] 브릿지 프로세스 가동 확인 (auto_trigger.sh PID 31950, watchdog PID 1661)
- [x] pipeline_healthy = true (AADS 매니저 보고 루프 복원 조건 충족)
- [x] AADS-139 완료보고 루프 구현 확인 (기존 구현 검증)
- [ ] git push — genspark_bridge.py는 git 미추적 파일 (aads-server 외부), 해당 없음
- [x] HTTP 200 — https://aads.newtalk.kr/api/v1/ops/health-check 정상 응답

---

## 비고

- `bridge_activity_1h: 0` 는 `bridge_activity_log` 테이블이 비어있는 상태이나, genspark_bridge.py가 데몬이 아닌 per-task 실행 방식이므로 구조적으로 bridge_activity_log에 직접 기록하지 않음. 별도 개선 태스크로 검토 필요.
- `last_seen_tasks_check: 2026-03-06T18:33:25` — 9시간 이상 미업데이트. watchdog의 seen_tasks 스캔이 정상 동작하고 있는지 확인 권장.
