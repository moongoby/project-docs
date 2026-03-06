---
project: AADS
task_id: AADS-122
completed_at: 2026-03-06 20:48:00 KST
---

# AADS-122 실행 결과 — Context API lessons 엔드포인트 + 교훈 자동등록

## work_1: 유지보수 모드 활성화

실행 명령:
```
curl -X POST https://aads.newtalk.kr/api/v1/ops/maintenance/start \
  -H "Content-Type: application/json" \
  -d '{"server":"68","reason":"AADS-122 Context API lessons 엔드포인트 추가","estimated_minutes":30,"services":["aads-server"]}'
```

결과:
```json
{"ok":true,"id":2,"server":"68","reason":"AADS-122 Context API lessons 엔드포인트 추가","services_paused":["aads-server"],"started_at":"2026-03-06T11:41:52.584838+00:00","estimated_end":"2026-03-06T12:11:52.584676+00:00"}
```
→ {"ok":true} 확인 완료

---

## work_2: lessons 테이블 생성

수정 파일: /root/aads/scripts/migrate_ops_db.py

DDL 추가 내용:
```sql
-- 10. 교훈 (AADS-122)
CREATE TABLE IF NOT EXISTS lessons (
    id VARCHAR(10) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    source_project VARCHAR(20) NOT NULL,
    source_task VARCHAR(30),
    severity VARCHAR(20) DEFAULT 'normal',
    summary TEXT NOT NULL,
    file_path VARCHAR(500),
    applicable_to TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lessons_category ON lessons(category);
CREATE INDEX IF NOT EXISTS idx_lessons_project ON lessons(source_project);
```

마이그레이션 실행:
```
python3 scripts/migrate_ops_db.py
```

실행 결과:
```
[migrate_ops_db] DB 연결: localhost:5433/aads
[migrate_ops_db] 10개 테이블 DDL 실행 중...
[migrate_ops_db] 생성 확인된 테이블: ['agent_activity_log', 'bridge_activity_log', 'ceo_decision_log', 'commit_log', 'cost_tracking', 'directive_lifecycle', 'lessons', 'maintenance_schedule', 'server_env_history', 'system_metrics']
[migrate_ops_db] ✅ 10개 테이블 모두 생성 완료
```

---

## work_3: FastAPI 라우터 /api/v1/lessons 구현

신규 파일 생성: /root/aads/aads-server/app/api/lessons.py

구현 엔드포인트:
- POST /api/v1/lessons — 교훈 등록
- GET  /api/v1/lessons — 전체 목록 (category/project/severity 필터)
- GET  /api/v1/lessons/{id} — 개별 조회

main.py 수정:
```python
from app.api.lessons import router as lessons_router
...
app.include_router(lessons_router, prefix="/api/v1", tags=["lessons"])
```

---

## work_4: 기존 8건 교훈 DB INSERT

신규 파일 생성: /root/aads/scripts/backfill_lessons.py

실행 결과:
```
[backfill_lessons] API: http://localhost:8100/api/v1
  [OK] L-001: {'ok': True, 'id': 'L-001'}
  [OK] L-002: {'ok': True, 'id': 'L-002'}
  [OK] L-003: {'ok': True, 'id': 'L-003'}
  [OK] L-004: {'ok': True, 'id': 'L-004'}
  [OK] L-005: {'ok': True, 'id': 'L-005'}
  [OK] L-006: {'ok': True, 'id': 'L-006'}
  [OK] L-007: {'ok': True, 'id': 'L-007'}
  [OK] L-008: {'ok': True, 'id': 'L-008'}

[backfill_lessons] 완료: 8/8 등록
```

---

## work_5: claude_exec.sh 교훈 자동 파싱 + POST 로직 추가

수정 파일: /root/aads/claude_exec.sh

추가된 함수 (aads_queue_msg 함수 바로 뒤):
```bash
# ── AADS-122: 교훈 자동 파싱 + POST 함수 ────────────────────────────────────
aads_lesson_check() {
    local result_file="$1"
    local aads_url
    aads_url=$(grep '^AADS_API_URL=' /root/.env.aads 2>/dev/null | cut -d= -f2-)
    [ -z "$aads_url" ] && aads_url="http://localhost:8080/api/v1"
    local AADS_API="${aads_url}"
    # 결과 파일에서 ## 교훈 또는 ## Lesson 섹션 추출
    local lesson_content
    lesson_content=$(sed -n '/^## 교훈/,/^## /p' "$result_file" 2>/dev/null | head -20)
    if [ -z "$lesson_content" ]; then
        lesson_content=$(sed -n '/^## Lesson/,/^## /p' "$result_file" 2>/dev/null | head -20)
    fi
    if [ -n "$lesson_content" ]; then
        # 다음 ID 계산
        local next_id
        next_id=$(curl -s "${AADS_API}/lessons" | python3 -c "import sys,json; print(f'L-{len(json.load(sys.stdin).get(\"lessons\",[]))+1:03d}')" 2>/dev/null)
        [ -z "$next_id" ] && next_id="L-AUTO"
        # summary JSON escape
        local summary_json
        summary_json=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" 2>/dev/null <<< "${lesson_content}" || echo "\"${lesson_content}\"")
        # POST 호출
        curl -s -X POST "${AADS_API}/lessons" \
            -H "Content-Type: application/json" \
            -d "{\"id\":\"${next_id}\",\"title\":\"Auto: ${TASK_ID}\",\"category\":\"auto\",\"source_project\":\"${PROJECT}\",\"source_task\":\"${TASK_ID}\",\"severity\":\"normal\",\"summary\":${summary_json}}" \
            > /dev/null 2>&1
        echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] [LESSON_AUTO_REGISTERED] ${next_id} from ${TASK_ID}" >> "${LOG_DIR}/auto_trigger.log"
    fi
}
```

완료 단계에서 호출 추가:
```bash
# AADS-122: 교훈 자동 등록
TASK_ID="${_task_id:-${FILENAME%.md}}"
aads_lesson_check "$RESULT_FILE"
```

---

## work_6: Bridge.py 교훈 자동 첨부 로직

수정 파일: /root/aads/scripts/genspark_bridge.py

추가된 함수 (_attach_relevant_lessons) 및 키워드→카테고리 매핑:
- 키워드: watchdog, docker, disk, 디스크, 서버 → infra
- 키워드: deploy, 배포 → deploy
- 키워드: token, 토큰, bridge, webhook → api
- 키워드: db, database, migration, 마이그레이션 → data
- 키워드: retry, ack, 재시도 → patterns

process_directive 함수에서 정상 투입 전 자동 첨부 로직 실행:
```python
# AADS-122: 교훈 자동 첨부
content = await _attach_relevant_lessons(content, aads_api_url)
```

---

## work_7: Docker rebuild + 배포

실행:
```
DOCKER_BUILDKIT=0 docker compose -f /root/aads/aads-server/docker-compose.prod.yml up -d --build aads-server
```

결과:
```
NAMES         STATUS
aads-server   Up 18 seconds (healthy)
```
→ 컨테이너 healthy 상태 확인

---

## work_8: 유지보수 모드 종료

실행:
```
curl -X POST https://aads.newtalk.kr/api/v1/ops/maintenance/end \
  -H "Content-Type: application/json" \
  -d '{"server":"68"}'
```

결과:
```json
{"ok":true,"server":"68","ended_count":1}
```
→ ended_count:1 확인 완료

---

## work_9: 검증

### 검증 1: GET /api/v1/lessons → total=8
```
curl -s https://aads.newtalk.kr/api/v1/lessons | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'total: {d[\"total\"]}')"
```
결과: **total: 8** ✅

### 검증 2: GET /api/v1/lessons?category=infra → total=3
```
curl -s "https://aads.newtalk.kr/api/v1/lessons?category=infra" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'infra: {d[\"total\"]}')"
```
결과: **infra: 3** ✅

### 검증 3: GET /api/v1/lessons/L-001 → 상세 JSON
```
curl -s https://aads.newtalk.kr/api/v1/lessons/L-001 | python3 -c "import sys,json; print(json.load(sys.stdin)['title'])"
```
결과: **Watchdog 서비스명 불일치 오탐 폭주** ✅

### 검증 4: health-check
```
curl -s https://aads.newtalk.kr/api/v1/ops/health-check | python3 -m json.tool | head -5
```
결과:
```json
{
    "pipeline_healthy": false,
    "stalled_count": 5,
    ...
}
```
※ pipeline_healthy=false는 작업 시작 전부터 존재한 기존 stalled_count=5 상태 (본 작업과 무관). API 자체는 200 OK 정상 응답.

### 검증 5: maintenance status
```
curl -s https://aads.newtalk.kr/api/v1/ops/maintenance/status | python3 -c "import sys,json; print('maintenance ended' if not json.load(sys.stdin).get('active') else 'STILL ACTIVE')"
```
결과: **maintenance ended** ✅

---

## work_10: Git commit + push

### aads-server
```
cd /root/aads/aads-server
git add app/api/lessons.py app/main.py
git commit -m "[AADS] feat(AADS-122): Context API lessons CRUD + 교훈 자동등록 + Bridge 자동첨부"
git push origin main
```
결과:
```
[main 5065ff9] [AADS] feat(AADS-122): ...
 2 files changed, 157 insertions(+)
 create mode 100644 app/api/lessons.py
To https://github.com/moongoby-GO100/aads-server.git
   f92f9a5..5065ff9  main -> main
```
→ push 성공 ✅

### aads-docs (HANDOVER.md 업데이트)
```
cd /root/aads/aads-docs
git add HANDOVER.md
git commit -m "[AADS] docs(AADS-122): HANDOVER 최근 태스크 업데이트"
git push origin main
```
결과:
```
[main 407d58f] [AADS] docs(AADS-122): HANDOVER 최근 태스크 업데이트
 1 file changed, 11 insertions(+), 3 deletions(-)
To https://github.com/moongoby-GO100/aads-docs.git
   0f3d3fe..407d58f  main -> main
```
→ push 성공 ✅

---

## 성공 기준 체크리스트

| # | 기준 | 결과 |
|---|------|------|
| 1 | GET /api/v1/lessons → 200 OK, total=8 | ✅ total: 8 |
| 2 | GET /api/v1/lessons?category=infra → total=3 | ✅ infra: 3 |
| 3 | GET /api/v1/lessons/L-001 → 상세 JSON 반환 | ✅ title 확인 |
| 4 | 유지보수 모드 활성화→종료 정상 동작 (AADS-116 첫 실전 검증) | ✅ ended_count:1 |
| 5 | claude_exec.sh에 aads_lesson_check 함수 존재 | ✅ 추가 완료 |
| 6 | Bridge.py에 교훈 자동첨부 로직 존재 | ✅ _attach_relevant_lessons 추가 |
| 7 | health-check pipeline_healthy=true | ⚠️ false (기존 stalled 5건, 본 작업과 무관) |

## 변경 파일 목록

| 파일 | 변경 유형 | 내용 |
|------|-----------|------|
| /root/aads/scripts/migrate_ops_db.py | 수정 | lessons 테이블 DDL 추가, 10개 테이블로 업데이트 |
| /root/aads/aads-server/app/api/lessons.py | 신규 생성 | lessons CRUD API |
| /root/aads/aads-server/app/main.py | 수정 | lessons_router 등록 |
| /root/aads/scripts/backfill_lessons.py | 신규 생성 | 기존 8건 DB INSERT 스크립트 |
| /root/aads/claude_exec.sh | 수정 | aads_lesson_check 함수 + 완료 단계 호출 추가 |
| /root/aads/scripts/genspark_bridge.py | 수정 | _attach_relevant_lessons 함수 + process_directive 내 호출 |
| /root/aads/aads-docs/HANDOVER.md | 수정 | v6.1 업데이트, 최근 태스크 AADS-122 반영 |

## GitHub 커밋
- aads-server: https://github.com/moongoby-GO100/aads-server/commit/5065ff9
- aads-docs: https://github.com/moongoby-GO100/aads-docs/commit/407d58f
