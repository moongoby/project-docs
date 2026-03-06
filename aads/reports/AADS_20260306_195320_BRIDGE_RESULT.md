---
project: AADS
task_id: AADS-120
completed_at: 2026-03-06T19:57:56+09:00
---

# AADS-120 실행 결과 — FLOW 문서화 체계 Phase 1-B

[CURSOR-AADS] push 완료 | Task: AADS-120 | 커밋: 0f3d3fe(aads-docs), 3451771(aads-server) | HTTP: 200

---

## work_1: 교훈 8건 작성 — shared/lessons/

### 생성된 파일 목록
1. `/root/aads/aads-docs/shared/lessons/infra/L-001_watchdog-false-positive.md` ✅
2. `/root/aads/aads-docs/shared/lessons/infra/L-002_disk-full-cascade.md` ✅
3. `/root/aads/aads-docs/shared/lessons/infra/L-003_docker-prune-schedule.md` ✅
4. `/root/aads/aads-docs/shared/lessons/api/L-004_token-refresh-pattern.md` ✅
5. `/root/aads/aads-docs/shared/lessons/api/L-005_genspark-no-webhook.md` ✅
6. `/root/aads/aads-docs/shared/lessons/deploy/L-006_verify-before-next-task.md` ✅
7. `/root/aads/aads-docs/shared/lessons/data/L-007_error-hash-dedup.md` ✅
8. `/root/aads/aads-docs/shared/lessons/patterns/L-008_ack-retry-pattern.md` ✅

### 각 파일 내용

#### L-001: Watchdog 서비스명 불일치 오탐 폭주
```
---
# L-001: Watchdog 서비스명 불일치 오탐 폭주

- 출처: AADS-117 (2026-03-06)
- 심각도: critical
- 적용 범위: 모든 watchdog/모니터링 서비스 등록 시

## 상황
monitored_services의 check_target이 실제 Docker 컨테이너명과 불일치

## 결과
30초마다 새 에러 INSERT → 6시간에 903건 → 디스크 94%→100% → API timeout

## 해결
check_target을 docker ps --filter name=xxx 방식으로 변경, error_hash UPSERT

## 예방법
서비스 감시 추가 시 docker ps/systemctl로 실제 이름 확인, 에러 로그는 항상 해시 중복방지
---
```

#### L-002: 디스크 100% 도달 → PostgreSQL write 실패 연쇄
```
---
# L-002: 디스크 100% 도달 → PostgreSQL write 실패 연쇄

- 출처: AADS (2026-03-06)
- 심각도: critical
- 적용 범위: DB 로그 테이블 설계, 디스크 모니터링

## 상황
error_log 테이블 무한 INSERT로 PostgreSQL WAL 급증

## 결과
디스크 100% → PostgreSQL read-only → API 500 → 전체 파이프라인 정지

## 해결
DELETE 오탐 데이터, VACUUM FULL, error_log에 UPSERT + occurrence_count

## 예방법
디스크 75% 경고/90% 긴급 알림, 로그 테이블은 항상 TTL 또는 max_rows 설정
---
```

#### L-003: Docker image 누적 → 주간 prune 필요
```
---
# L-003: Docker image 누적 → 주간 prune 필요

- 출처: AADS (2026-03-06)
- 심각도: normal
- 적용 범위: Docker 운영 서버 전반

## 상황
Docker image/volume 누적으로 디스크 사용률 점진 증가

## 결과
수 주 후 디스크 경고 임계치 도달

## 해결
docker system prune -af --volumes 주간 크론

## 예방법
주간 크론 등록, 프로덕션 서버 모두 동일 적용
---
```

#### L-004: API 토큰 만료 전 자동갱신 필수
```
---
# L-004: API 토큰 만료 전 자동갱신 필수

- 출처: KIS 인증에러 9건 (2026-03-06)
- 심각도: high
- 적용 범위: OAuth 토큰 기반 외부 API 연동 전반

## 상황
OAuth 토큰 만료 시점에 API 호출 실패, 9건 연속 auth_expired

## 결과
새벽 시간대 작업 전량 실패

## 해결
pre_check_account()로 사전 검증, 실패 시 자동 토큰 갱신

## 예방법
토큰 TTL의 80% 시점에 선제 갱신, 만료 전 알림 설정
---
```

#### L-005: 외부 SaaS 웹훅 미지원 시 ACK+재전송
```
---
# L-005: 외부 SaaS 웹훅 미지원 시 ACK+재전송

- 출처: AADS GenSpark 브릿지 (2026-03-06)
- 심각도: normal
- 적용 범위: 외부 SaaS 연동, 메시지 전달 파이프라인

## 상황
GenSpark에서 웹훅(Webhook) 미지원, 실시간 알림 불가

## 결과
폴링 방식으로 대체해야 하며, 메시지 누락 가능성 존재

## 해결
Selenium 폴링 + ACK 마커([BRIDGE-SENT]) + 해시 중복방지

## 예방법
외부 SaaS 연동 시 웹훅 지원 여부 먼저 확인, 미지원 시 ACK+재전송 패턴 적용
---
```

#### L-006: 배포 후 5분 모니터링 의무
```
---
# L-006: 배포 후 5분 모니터링 의무

- 출처: AADS T-038 (2026-03-06)
- 심각도: critical
- 적용 범위: 모든 서비스 배포, Watchdog 배포

## 상황
Watchdog 배포 직후 검증 없이 다음 작업으로 이동

## 결과
서비스명 불일치 오탐을 6시간 동안 미발견, 903건 쓰레기 데이터

## 해결
사후 정리(DELETE + VACUUM)

## 예방법
배포 후 최소 5분 error_log/watchdog 모니터링 필수, FLOW Wrap up 의무화
---
```

#### L-007: 에러 로그 해시 기반 중복 방지
```
---
# L-007: 에러 로그 해시 기반 중복 방지

- 출처: AADS Watchdog (2026-03-06)
- 심각도: high
- 적용 범위: 에러 로그 테이블 설계, 모니터링 데이터 저장

## 상황
동일 에러가 반복 INSERT되어 테이블 폭발

## 결과
디스크 소진 + 쿼리 성능 저하

## 해결
error_message SHA256 해시 컬럼 추가, INSERT → UPSERT(occurrence_count++)

## 예방법
에러/로그 테이블 설계 시 항상 해시 기반 중복 방지 적용
---
```

#### L-008: ACK+Retry 패턴 (외부 메시지 확인)
```
---
# L-008: ACK+Retry 패턴 (외부 메시지 확인)

- 출처: AADS Bridge.py (2026-03-06)
- 심각도: normal
- 적용 범위: 외부 서비스 메시지 전달, 비동기 파이프라인

## 상황
외부 서비스(GenSpark)에 메시지 전송 후 수신 확인 불가

## 결과
중복 전송 또는 누락 발생

## 해결
[BRIDGE-SENT] 마커로 자체 발신 식별, SHA256 해시로 중복 차단, seen_tasks 레지스트리

## 예방법
외부 메시지 전달 시 ACK 마커 + 해시 + 재시도 3세트 패턴 적용
---
```

---

## work_2: INDEX.md 업데이트

파일: `/root/aads/aads-docs/shared/lessons/INDEX.md`

내용:
```
# 공유 교훈 INDEX (최종: 2026-03-06, 8건)

## infra (서버·디스크·Docker·네트워크)
- L-001: Watchdog 서비스명 불일치 오탐 폭주 [AADS-117] → infra/L-001_watchdog-false-positive.md
- L-002: 디스크 100% 도달 → PostgreSQL write 실패 연쇄 [AADS] → infra/L-002_disk-full-cascade.md
- L-003: Docker image 누적 → 주간 prune 필요 [AADS] → infra/L-003_docker-prune-schedule.md

## api (외부 API·토큰·웹훅·타임아웃)
- L-004: API 토큰 만료 전 자동갱신 필수 [KIS 9건] → api/L-004_token-refresh-pattern.md
- L-005: 외부 SaaS 웹훅 미지원 시 ACK+재전송 [GenSpark] → api/L-005_genspark-no-webhook.md

## deploy (배포·검증·롤백)
- L-006: 배포 후 5분 모니터링 의무 [AADS T-038 903건] → deploy/L-006_verify-before-next-task.md

## data (DB·마이그레이션·로깅)
- L-007: 에러 로그 해시 기반 중복 방지 [Watchdog] → data/L-007_error-hash-dedup.md

## patterns (재사용 코드 패턴)
- L-008: ACK+Retry 패턴 (외부 메시지 확인) [Bridge.py] → patterns/L-008_ack-retry-pattern.md
```

---

## work_3: AADS-KNOWLEDGE.md 작성

파일: `/root/aads/aads-server/docs/knowledge/AADS-KNOWLEDGE.md`

내용:
```
# AADS-KNOWLEDGE: AADS 시스템 전용 지식

## 아키텍처
- 8-agent LangGraph 체인: Supervisor→PM→Architect→Developer→QA→Judge→DevOps→Researcher
- 5계층 메모리: Working→Project→Experience(pgvector)→System→Procedural
- MCP 상시 4개(Filesystem, Git, Memory, PostgreSQL) + 온디맨드 3개(GitHub, Brave, Fetch)
- Backend: FastAPI 0.115 + Uvicorn, PostgreSQL 15, Upstash Redis, Docker Compose
- Frontend: Next.js 16 + React 19 + Tailwind CSS 4

## 지시서 자동화 파이프라인 (TECH-002)
8단계: CEO지시 → Bridge감지 → 사전검증 → 우선순위전송 → Claude실행 → 결과보고 → DB기록 → 교차검증
교차검증 9종: pending정체, running초과, DB-파일정합, 커밋완전성, 비용$0, 디스크75%, 에이전트무활동, seen_tasks차단, 미감지복원
자동복구 12건: pipeline_monitor, watchdog, cross_validator, approval_queue 등

## Bridge.py 동작 원리
- GenSpark 채팅 → Selenium 폴링 → 분류(7카테고리) → 의사결정 추출 → 지시서 .md 생성 → pending/
- 중복 방지: SKIP_PATTERNS 10개, [BRIDGE-SENT] 마커, SHA256 해시, seen_tasks.json
- 결과 보고: done/ 감시 → Telegram 발송 → archived/ 이동

## Watchdog 주의사항 (L-001, L-006 참조)
- 서비스명은 반드시 docker ps --filter name=xxx 확인 후 등록
- error_log INSERT는 error_hash UPSERT (occurrence_count 증가)
- 배포 직후 5분 error_log 증가 추이 모니터링 필수

## 세션 관리 (AADS-117)
- 글로벌 ≤4세션 (3서버 합산), 서버별 동적 1~3슬롯
- 211=Hub(SSH 집계, 캐시 생성 TTL 40s), 68/114=Client(캐시 읽기)
- 계정 2개(gmail/naver) MAX-200, 전환 쿨다운 5분

## 함정 (과거 실패)
- Supavisor 경유 → AsyncPipeline 충돌 → 직접 연결만 사용 (R-011)
- langgraph-supervisor MCP 루프 버그 #249 → 프로덕션 금지 (R-010)
- HANDOVER 22k토큰 → 컨텍스트 낭비 → v6.0에서 50줄로 축소 완료
- seen_tasks에 실패 작업 잔류 → 영구 차단 → 체크 8로 자동 해제
```

---

## work_4: AADS Claude Code 설정 — .claude/ 디렉토리

### 4-1. `/root/aads/aads-server/CLAUDE.md` (28줄)
```
# AADS — 자율 AI 개발 시스템 (서버 68)

## 기술 스택
FastAPI 0.115, PostgreSQL 15+pgvector, LangGraph 1.0.10, Docker, Python 3.11, Next.js 16

## CEO 절대 규칙
핵심: HANDOVER 필수 업데이트, push+HTTP200, 시크릿 커밋 금지, 직접DB편집 금지
비용 효율 최우선, max 15 LLM/task, no Supavisor, no langgraph-supervisor
상세: https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/CEO-DIRECTIVES.md

## 공유 교훈
docs/shared-lessons/INDEX.md 또는 https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/shared/lessons/INDEX.md

## AADS 전용 지식
docs/knowledge/AADS-KNOWLEDGE.md

## FLOW 규칙
.claude/rules/flow-rules.md
모든 작업: Find→Layout→Operate→Wrap up. Wrap up 미완료 시 다음 작업 차단(P0/P1).

## 현재 상태
- Phase: Phase 2 운영, FLOW 문서화 체계 도입중
- 최근: AADS-120(FLOW Phase 1-B), AADS-119(HANDOVER v6.0), AADS-118(교차검증 9종)
- 긴급: 없음

## 빌드/배포
docker compose -f docker-compose.prod.yml up -d --build aads-server
curl -s https://aads.newtalk.kr/api/v1/ops/health-check | python3 -m json.tool
```

### 4-2. `/root/aads/aads-server/.claude/rules/flow-rules.md`
flow-rules.md 원본 내용 복사 완료 (shared/rules/flow-rules.md 동일 내용)

### 4-3. `/root/aads/aads-server/.claude/rules/watchdog.md`
```
# Watchdog 규칙
- 서비스 등록 전 docker ps --filter name=xxx로 실제 이름 확인 (L-001)
- error_log INSERT는 반드시 error_hash UPSERT (L-007)
- 배포 후 5분 error_log 모니터링 필수 (L-006)
- 오탐 발생 시 DELETE + VACUUM, 근본 원인(서비스명 불일치) 해결
```

### 4-4. `/root/aads/aads-server/.claude/rules/bridge.md`
```
# Bridge 규칙
- 중복 방지 3중: SKIP_PATTERNS + [BRIDGE-SENT] + SHA256 해시
- 외부 서비스 연동 시 ACK+Retry 패턴 적용 (L-005, L-008)
- seen_tasks.json에 실패 작업 잔류 주의 → 교차검증 체크 8이 자동 해제
- 컨텍스트 압축 감지 시 session_restore_prompt 자동 재주입 (AADS-115)
```

### 4-5. `/root/aads/aads-server/.claude/rules/context-api.md`
```
# Context API 규칙
- directive_lifecycle: queued→running→completed/failed 전이 자동 기록
- cost_tracking: 토큰/비용 자동 기록
- commit_log: SHA 자동 추출
- lessons: POST /api/v1/lessons 로 교훈 등록 (Phase 3에서 구현)
- 유지보수 모드: POST /ops/maintenance/start 후 배포, 완료 후 /end
```

### 4-6. `/root/aads/aads-server/.claude/skills/tpp/SKILL.md`
```
name: tpp
description: 진행중인 TPP를 이어서 작업합니다.
argument-hint: [path-to-tpp]
allowed-tools: Bash, Read, Glob, Grep, Edit, Write

## 필수 읽기
- CLAUDE.md
- docs/knowledge/AADS-KNOWLEDGE.md
- docs/shared-lessons/INDEX.md

## 절차
1. _todo/ 에서 지정된 TPP 읽기
2. 현재 Phase 확인
3. 해당 Phase 작업 수행
4. TPP 업데이트: 완료 항목 체크, 발견사항·함정 기록
5. 400줄 초과 시 분할
```

### 4-7. `/root/aads/aads-server/.claude/skills/handoff/SKILL.md`
```
name: handoff
description: 컨텍스트 부족 시 현재 상태를 TPP에 저장합니다.
allowed-tools: Read, Edit, Write, Glob

## 절차
1. 현재 TPP 다시 읽기
2. 완료 항목 체크, Phase 업데이트
3. 발견사항·함정·실패한 접근법 기록
4. 다음 세션이 알아야 할 것 명시
5. HANDOVER.md "최근 태스크" 항목 업데이트
6. 400줄 이내 유지
```

---

## work_5: 공유 교훈을 aads-server에도 복사

```
mkdir -p /root/aads/aads-server/docs/shared-lessons
cp -r /root/aads/aads-docs/shared/lessons/* /root/aads/aads-server/docs/shared-lessons/
```

결과:
```
api  data  deploy  INDEX.md  infra  patterns
```

17개 파일 복사 완료 (INDEX.md + 8개 교훈 파일 + 디렉토리 구조)

---

## work_6: Git commit + push — aads-docs

```
[main c256fa8] [AADS] feat(AADS-120): FLOW Phase 1-B — 교훈 8건 등록 + INDEX.md
 9 files changed, 165 insertions(+), 2 deletions(-)
 create mode 100644 shared/lessons/api/L-004_token-refresh-pattern.md
 create mode 100644 shared/lessons/api/L-005_genspark-no-webhook.md
 create mode 100644 shared/lessons/data/L-007_error-hash-dedup.md
 create mode 100644 shared/lessons/deploy/L-006_verify-before-next-task.md
 create mode 100644 shared/lessons/infra/L-001_watchdog-false-positive.md
 create mode 100644 shared/lessons/infra/L-002_disk-full-cascade.md
 create mode 100644 shared/lessons/infra/L-003_docker-prune-schedule.md
 create mode 100644 shared/lessons/patterns/L-008_ack-retry-pattern.md
To https://github.com/moongoby-GO100/aads-docs.git
   72ae5cf..c256fa8  main -> main
```

HANDOVER.md 업데이트 커밋:
```
[main 0f3d3fe] [AADS] docs(AADS-120): HANDOVER 최근 태스크 AADS-120으로 업데이트
 1 file changed, 1 insertion(+), 1 deletion(-)
To https://github.com/moongoby-GO100/aads-docs.git
   c256fa8..0f3d3fe  main -> main
```

---

## work_7: Git commit + push — aads-server

```
[main 3451771] [AADS] feat(AADS-120): Claude Code 메모리 설정 + AADS-KNOWLEDGE + .claude rules/skills
 17 files changed, 297 insertions(+)
 create mode 100644 .claude/rules/bridge.md
 create mode 100644 .claude/rules/context-api.md
 create mode 100644 .claude/rules/flow-rules.md
 create mode 100644 .claude/rules/watchdog.md
 create mode 100644 .claude/skills/handoff/SKILL.md
 create mode 100644 .claude/skills/tpp/SKILL.md
 create mode 100644 CLAUDE.md
 create mode 100644 docs/knowledge/AADS-KNOWLEDGE.md
 create mode 100644 docs/shared-lessons/INDEX.md
 create mode 100644 docs/shared-lessons/api/L-004_token-refresh-pattern.md
 create mode 100644 docs/shared-lessons/api/L-005_genspark-no-webhook.md
 create mode 100644 docs/shared-lessons/data/L-007_error-hash-dedup.md
 create mode 100644 docs/shared-lessons/deploy/L-006_verify-before-next-task.md
 create mode 100644 docs/shared-lessons/infra/L-001_watchdog-false-positive.md
 create mode 100644 docs/shared-lessons/infra/L-002_disk-full-cascade.md
 create mode 100644 docs/shared-lessons/infra/L-003_docker-prune-schedule.md
 create mode 100644 docs/shared-lessons/patterns/L-008_ack-retry-pattern.md
To https://github.com/moongoby-GO100/aads-server.git
   c0abf3c..3451771  main -> main
```

---

## work_8: 검증 결과

### CHECK 1: 교훈 파일 수
```
ls /root/aads/aads-docs/shared/lessons/*/L-*.md | wc -l → 8
```
결과: **8건** ✅

### CHECK 2: INDEX.md L- 줄 수
```
grep "L-" /root/aads/aads-docs/shared/lessons/INDEX.md | wc -l → 8
```
결과: **8줄** ✅

### CHECK 3: 원격 INDEX.md head -5
```
# 공유 교훈 INDEX (최종: 2026-03-06, 8건)

## infra (서버·디스크·Docker·네트워크)
- L-001: Watchdog 서비스명 불일치 오탐 폭주 [AADS-117] → infra/L-001_watchdog-false-positive.md
- L-002: 디스크 100% 도달 → PostgreSQL write 실패 연쇄 [AADS] → infra/L-002_disk-full-cascade.md
```
결과: **GitHub 원격 반영 확인** ✅

### CHECK 4: CLAUDE.md 줄 수
```
wc -l /root/aads/aads-server/CLAUDE.md → 28
```
결과: **28줄 (60줄 이내)** ✅

### CHECK 5: .claude/rules/ 파일 목록
```
ls /root/aads/aads-server/.claude/rules/
→ bridge.md  context-api.md  flow-rules.md  watchdog.md
```
결과: **4개 파일** ✅

### CHECK 6: .claude/skills/ 디렉토리 목록
```
ls /root/aads/aads-server/.claude/skills/
→ handoff  tpp
```
결과: **2개 디렉토리** ✅

### CHECK 7: AADS-KNOWLEDGE.md head -3
```
# AADS-KNOWLEDGE: AADS 시스템 전용 지식

## 아키텍처
```
결과: **내용 정상** ✅

### CHECK 8: health-check
```json
{
    "pipeline_healthy": true,
    "stalled_count": 0,
    "stalled_queue": 0,
    "stalled_running": 0,
    "active_count": 2,
    "recent_completed_30m": 5,
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
결과: **pipeline_healthy: true** ✅

### CHECK 9: _todo/ 존재 확인
```
ls /root/aads/aads-server/_todo/ → (빈 디렉토리, 존재함)
```
결과: **디렉토리 존재** ✅

### CHECK 10: shared-lessons/INDEX.md 존재 확인
```
ls /root/aads/aads-server/docs/shared-lessons/INDEX.md
→ /root/aads/aads-server/docs/shared-lessons/INDEX.md
```
결과: **파일 존재** ✅

---

## success_criteria 달성 현황

1. ✅ 교훈 8건 파일 모두 존재, INDEX.md에 8건 기록
2. ✅ AADS-KNOWLEDGE.md 생성 완료 (/root/aads/aads-server/docs/knowledge/AADS-KNOWLEDGE.md)
3. ✅ CLAUDE.md 28줄(60줄 이내), .claude/rules/ 4개 파일, .claude/skills/ 2개 디렉토리
4. ✅ aads-docs (0f3d3fe), aads-server (3451771) 양쪽 모두 git push 완료
5. ✅ health-check pipeline_healthy=true
6. ✅ shared-lessons/ 서버 로컬 복사 완료 (/root/aads/aads-server/docs/shared-lessons/)

---

## HANDOVER.md 업데이트

AADS 프로젝트 최근 태스크를 AADS-120으로 업데이트 완료:
- 변경 전: `AADS-119 FLOW 체계 도입`
- 변경 후: `AADS-120 FLOW Phase 1-B 완료`

커밋: 0f3d3fe → aads-docs main에 push 완료
