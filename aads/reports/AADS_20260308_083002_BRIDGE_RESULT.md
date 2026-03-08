---
project: AADS
task_id: AADS-166
completed_at: 2026-03-08T08:58:38+09:00
---

# AADS-166 파이프라인 전체 헬스체크 시스템 + 실시간 SSE 스트리밍 (8파트)

## 실행 결과 요약

**전체 상태: 완료**

8파트 모두 구현, 배포, 검증 완료.

---

## Part 1: 디렉티브 폴더 실시간 조회 API

### 구현 내용
- `GET /api/v1/directives/{status}` (status: pending|running|done|archived)
- 서버 68의 `/root/.genspark/directives/{status}/` 폴더 스캔
- 각 .md 파일의 파일명, 크기, 수정시각, 내용 첫 5줄 반환
- 폴더 없으면 빈 배열 + `folder_exists: false`

### 파일
- `app/services/health_checker.py` — `scan_directive_folder()` 함수
- `app/api/ops.py` — `@router.get("/directives/{status}")` 엔드포인트

### 검증
```
curl -s https://aads.newtalk.kr/api/v1/directives/pending | python3 -m json.tool
→ {"status": "pending", "folder_exists": true, "count": 2, "directives": [...]}
```

---

## Part 2: 파이프라인 프로세스 liveness API

### 구현 내용
- `GET /api/v1/ops/pipeline-status`
- 로컬(서버68): pgrep으로 bridge.py, auto_trigger, session_watchdog, claude_exec 확인
- 원격(서버211): SSH 경유 pgrep (ConnectTimeout=5)
- overall: HEALTHY / DEGRADED 판정

### 파일
- `app/services/health_checker.py` — `check_pipeline_status()`, `_run_local_cmd()`, `_run_ssh_cmd()`
- `app/api/ops.py` — `@router.get("/ops/pipeline-status")`

### 검증
```
curl -s https://aads.newtalk.kr/api/v1/ops/pipeline-status | python3 -m json.tool
→ {"server_211": {"reachable": false, ...}, "server_68": {...}, "overall": "DEGRADED"}
```
(Docker 컨테이너 내부에서 SSH 미설정으로 서버211 unreachable — graceful degradation 동작 확인)

---

## Part 3: 인프라 점검 API

### 구현 내용
- `GET /api/v1/ops/infra-check`
- 병렬 실행 (asyncio.gather): DB ping, GitHub PAT, SSH 211/114, 디스크 68/211/114, 메모리 68, CPU 68
- 임계값: 디스크 >80% warning, >90% critical
- overall: HEALTHY / DEGRADED / CRITICAL

### 파일
- `app/services/health_checker.py` — `check_infra()`, `_check_db()`, `_check_github_pat()`, `_check_ssh()`, `_check_disk()`, `_check_memory()`, `_check_cpu()`
- `app/api/ops.py` — `@router.get("/ops/infra-check")`

### 검증
```
curl -s https://aads.newtalk.kr/api/v1/ops/infra-check | python3 -m json.tool
→ {"db": {"ok": true, "latency_ms": 336}, "github_pat": {"ok": false, "error": "PAT not configured"}, "disk_68": {"ok": true, "usage_pct": 47}, ...}
```

---

## Part 4: 정합성 검증 API

### 구현 내용
- `GET /api/v1/ops/consistency-check`
- STATUS.md ↔ DB: last_completed 일치 검증
- pending 폴더 ↔ DB queued: 건수 비교 (허용 오차 2건)
- commit SHA 검증: DB commit_log 최신 ↔ STATUS.md
- HANDOVER 동기화 확인

### 파일
- `app/services/health_checker.py` — `check_consistency()`
- `app/api/ops.py` — `@router.get("/ops/consistency-check")`

### 검증
```
curl -s https://aads.newtalk.kr/api/v1/ops/consistency-check | python3 -m json.tool
→ {"status_md_sync": {"ok": true, "db_last": "AADS-161"}, "pending_sync": {"ok": false, "folder_count": 2, "db_queued": 32, "mismatch": 30}, ...}
```

---

## Part 5: 통합 헬스 엔드포인트

### 구현 내용
- `GET /api/v1/ops/full-health`
- Part 1~4 + 기존 health-check 병렬 실행
- 전체 상태: HEALTHY / DEGRADED / CRITICAL
- 한국어 요약 (summary_kr)
- 응답 시간: ~530ms (SSH 포함)

### 파일
- `app/services/health_checker.py` — `full_health_check()`
- `app/api/ops.py` — `@router.get("/ops/full-health")`

### 검증
```
curl -s https://aads.newtalk.kr/api/v1/ops/full-health
→ {"status": "CRITICAL", "checked_at": "2026-03-08T08:55:49.859751+09:00", "duration_ms": 530, "sections": {"directives": {"pending": {"count": 2, ...}}, "pipeline": {...}, "infra": {...}, "consistency": {...}}, "issues": [...], "summary_kr": "파이프라인: DEGRADED, 인프라: CRITICAL, 정합성: DEGRADED, 이슈 8건"}
```

---

## Part 6: CEO Chat health-check 인텐트

### 구현 내용
- `_INTENT_PATTERNS`에 `health_check` 추가: "헬스체크", "건강", "시스템 상태", "인프라", "health", "전체 점검" 등
- `classify_intent()` 우선순위: design_fix > design > qa > execution_verify > architect > **health_check** > execute > ...
- `_handle_health_check_intent()`: /api/v1/ops/full-health 호출 → 한국어 요약 (파이프라인/인프라/정합성/디렉티브/이슈)

### 파일
- `app/api/ceo_chat.py` — `_INTENT_PATTERNS["health_check"]`, `_handle_health_check_intent()`, intent dispatch

### 검증
- "헬스체크" 입력 시 health_check 인텐트 분류 → full-health 호출 → 한국어 요약 응답

---

## Part 7: SSE 실시간 스트리밍

### 구현 내용
- `GET /api/v1/ops/stream` (SSE endpoint)
- Content-Type: text/event-stream
- 5초 주기 3가지 이벤트:
  1. `event: health` — quick_health() 경량 헬스체크
  2. `event: directive` — directive_changes_since() 최신 변경
  3. `event: pipeline` — pipeline_quick_status() 브릿지/세션
- 최대 5개 동시 연결 제한
- 클라이언트 연결 해제 시 자동 정리

### 파일
- `app/services/health_checker.py` — `quick_health()`, `directive_changes_since()`, `pipeline_quick_status()`
- `app/api/ops.py` — `@router.get("/ops/stream")`, `event_generator()`

### 검증
```
timeout 15 curl -s --no-buffer https://aads.newtalk.kr/api/v1/ops/stream &
sleep 10
→ event: health
  data: {"status": "DEGRADED", "stalled": 3, "running": 6, "completed_today": 22, ...}
→ event: pipeline
  data: {"bridge_running": false, "active_sessions": 0, ...}
(5초 주기 반복 확인)
```

---

## Part 8: 대시보드 Pipeline Health 탭 + SSE 연결

### [8-1] 새 탭 "Pipeline" 추가
- 기존 5탭 → 6탭: directives | reports | **pipeline** | remote | analytics | docs
- `TabType` 타입에 "pipeline" 추가
- `PipelineTab` 컴포넌트 → `PipelineHealthTab` 렌더링

### [8-2] PipelineHealthCard 컴포넌트
- SSE 연결: `useSSE()` 훅으로 EventSource 관리
- 4개 상태 카드:
  1. **Directives**: pending/running/done/archived 건수
  2. **Pipeline**: bridge/auto_trigger/watchdog 프로세스 상태 (green/red dot)
  3. **Infrastructure**: DB/SSH/디스크/메모리 상태 (green/yellow/red)
  4. **Consistency**: STATUS↔DB, HANDOVER↔태스크, pending↔큐 동기화
- 통합 상태 배너: HEALTHY(green) / DEGRADED(yellow) / CRITICAL(red)
- Issues 리스트: severity별 정렬
- SSE 이벤트 수신 시 즉시 업데이트 + fallback 30초 폴링

### [8-3] 기존 Directives 탭 개선
- 정체 태스크 강조: `status === "running"` && `started_at > 1h ago` → 빨간 배경 + 경고 아이콘

### [8-4] 헤더에 미니 상태 표시
- Header 컴포넌트에 SSE 연결
- 파이프라인 상태 dot: HEALTHY=green, DEGRADED=yellow, CRITICAL=red(점멸)
- fallback: SSE 실패 시 15초 폴링

### 파일
- `src/hooks/useSSE.ts` — **신규**: SSE 연결 관리 훅
- `src/components/PipelineHealthCard.tsx` — **신규**: Pipeline 탭 전체 UI
- `src/app/tasks/page.tsx` — Pipeline 탭 추가, 정체 강조
- `src/components/Header.tsx` — SSE 상태 dot 추가
- `src/lib/api.ts` — 5개 엔드포인트 추가

### 검증
- TypeScript: `npx tsc --noEmit` 에러 0건
- Next.js: `npm run build` 성공
- PM2: `pm2 start aads-dashboard` 정상 구동

---

## Git 커밋

| 리포 | 커밋 SHA | 메시지 |
|------|----------|--------|
| aads-server | 9a44646 | [AADS] feat: AADS-166 파이프라인 전체 헬스체크 + 실시간 SSE 스트리밍 |
| aads-dashboard | 16c67bc | [AADS] feat: AADS-166 Pipeline Health 탭 + SSE 실시간 갱신 + Header 상태 dot |
| aads-docs | 7587187 | [AADS] docs: HANDOVER v11.0 |

## 기존 기능 회귀 없음

- `GET /api/v1/ops/health-check` — 기존 응답 형식 완전 유지 (pipeline_healthy, stalled_count, checks 등)
- CEO Chat 기존 10개 인텐트 정상 동작 (health_check 11번째로 추가)
- 대시보드 기존 5탭 정상 동작 (pipeline 6번째로 추가)

## success_criteria 달성 현황

| # | 기준 | 달성 |
|---|------|------|
| 1 | GET /api/v1/directives/{4상태} — 200 + JSON | O |
| 2 | GET /api/v1/ops/pipeline-status — bridge/watchdog 상태, SSH graceful | O |
| 3 | GET /api/v1/ops/infra-check — DB/GitHub/SSH/디스크/메모리 포함, 5초 이내 | O |
| 4 | GET /api/v1/ops/consistency-check — STATUS↔DB, pending↔큐 교차검증 | O |
| 5 | GET /api/v1/ops/full-health — 병렬, ≤5초, HEALTHY/DEGRADED/CRITICAL | O (530ms) |
| 6 | CEO Chat "헬스체크" → 한국어 요약 반환 | O |
| 7 | GET /api/v1/ops/stream — SSE 5초 주기 health/directive/pipeline | O |
| 8 | 대시보드 Pipeline 탭 — 4카드 렌더링, SSE 즉시 갱신, fallback 폴링 | O |
| 9 | 대시보드 헤더 — 상태 dot (green/yellow/red) | O |
| 10 | 정체 태스크 시각적 강조 (stalled > 1h → 빨간 배경) | O |
| 11 | 기존 API + 인텐트 + 대시보드 정상 유지 (회귀 없음) | O |
| 12 | git push HTTP 200, HANDOVER.md 업데이트, STATUS.md 업데이트 | O |
| 13 | 커밋 메시지 형식 준수 | O |
