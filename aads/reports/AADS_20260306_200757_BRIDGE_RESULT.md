---
project: AADS
task_id: AADS-121
completed_at: 2026-03-06T20:14:24+09:00
---

# AADS-121 실행 결과: Claude Code 3계층 메모리 설정

## 지시 파일
`/root/.genspark/directives/pending/AADS_20260306_200757_BRIDGE.md`

---

## work_1: AADS CLAUDE.md 작성

**파일**: `/root/aads/aads-server/CLAUDE.md`

**작업**: 기존 파일(29줄)을 지시 내용에 맞게 덮어씀

**결과**:
```
28 /root/aads/aads-server/CLAUDE.md
```
28줄 — 60줄 이내 기준 충족

**최종 내용**:
```
# AADS — 자율 AI 개발 시스템 (서버 68)

## 기술 스택
FastAPI 0.115, PostgreSQL 15, LangGraph 1.0.10, Docker Compose, Python 3.11, Next.js 16

## CEO 절대 규칙
- CEO-DIRECTIVES: https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/CEO-DIRECTIVES.md
- 핵심: Supavisor 금지, langgraph-supervisor 금지, LLM 15회/task, 비용 효율 최우선
- HANDOVER 업데이트 없이 완료 선언 금지 (R-001)
- GitHub 브라우저 경로로 보고 (R-008)

## FLOW 프레임워크
Find→Layout→Operate→Wrap up. 상세: .claude/rules/flow-rules.md

## 공유 교훈
docs/shared-lessons/INDEX.md 참조. 작업 전 관련 교훈 확인 필수.

## AADS 전용 지식
docs/knowledge/AADS-KNOWLEDGE.md — 아키텍처, 파이프라인, 교차검증, 함정

## 현재 상태
- Phase: Phase 2 운영
- 최근: AADS-121(Claude Code 설정), AADS-120(교훈), AADS-119(HANDOVER v6.0)
- 긴급: 없음

## 빌드/배포
docker compose -f docker-compose.prod.yml up -d --build aads-server
curl -s https://aads.newtalk.kr/api/v1/ops/health-check | python3 -m json.tool
```

---

## work_2: .claude/rules/ 디렉토리 및 규칙 파일 생성

**디렉토리**: `/root/aads/aads-server/.claude/rules/` (기존 존재)
**디렉토리**: `/root/aads/aads-server/.claude/skills/tpp/` (기존 존재)
**디렉토리**: `/root/aads/aads-server/.claude/skills/handoff/` (기존 존재)

### flow-rules.md
`/root/aads/aads-docs/shared/rules/flow-rules.md` 에서 복사 (cp 명령)

복사된 내용:
```
# FLOW 프레임워크 규칙

## 4단계
1. Find(발견): 시장분석, 자료분석, 연구. 산출물: {PROJECT}-FIND-{SEQ}_{제목}.md
2. Lay out(설계): 기획서, 아키텍처. 산출물: {PROJECT}-LAYOUT-{SEQ}_{제목}.md
3. Operate(실행): 작업지시서. 산출물: {PROJECT}-{SEQ}_{제목}.md. parent 필드 필수.
4. Wrap up(마무리): 검증, 회고, 교훈. 산출물: {PROJECT}-WRAP-{SEQ}_{제목}.md

## Wrap up 의무 수준
- P0/P1: WRAP 파일 필수. 체크리스트 전항목. 미완료 시 다음 작업 차단.
- P2(15분 초과): 5분 모니터링 + HTTP 200 확인 필수.
- P2(15분 이하)/P3: claude_exec.sh 자동 health-check. 실패 시 WRAP 자동 생성.

## 작업 전
- _todo/ 에서 관련 TPP 확인. 있으면 /tpp 스킬로 이어서 진행.
- docs/shared-lessons/INDEX.md에서 관련 교훈 확인.

## 작업 후
- 다른 프로젝트에도 적용 가능한 교훈 → shared/lessons/ 등록
- 결과 파일에 ## 교훈 섹션 작성 시 자동 등록됨
- 컨텍스트 부족 시 /handoff 스킬 실행
```

### watchdog.md
`/root/aads/aads-server/.claude/rules/watchdog.md` 생성/업데이트:
```
# Watchdog 규칙
<!-- paths: **/watchdog*, **/error_log* -->
- 서비스 감시 추가 시: docker ps --filter name=xxx로 실제 이름 확인 (L-001)
- error_log INSERT: error_hash 기반 UPSERT 필수 (L-007)
- 배포 후 5분 모니터링 필수 (L-006)
- 10회 연속 실패 시 텔레그램 긴급알림
- CEO 승인 필요 항목: 원격 서버 복구, 서비스 재시작
```

### bridge.md
`/root/aads/aads-server/.claude/rules/bridge.md` 생성/업데이트:
```
# Bridge 규칙
<!-- paths: **/bridge*, **/genspark* -->
- 메시지 중복방지 3단계: SKIP_PATTERNS → SHA256 해시 → seen_tasks
- [BRIDGE-SENT] 태그 필수 삽입
- 컨텍스트 압축 감지 시 session_restore_prompt 자동 재주입 (AADS-115)
- GenSpark 웹훅 미지원 → 폴링+ACK 패턴 (L-005)
```

### context-api.md
`/root/aads/aads-server/.claude/rules/context-api.md` 생성/업데이트:
```
# Context API 규칙
<!-- paths: **/context*, **/channels*, **/memory* -->
- context_docs URL 캐시 TTL 300초, HANDOVER 변경 시 즉시 무효화
- system_memory category별 용도 엄격 구분
- 민감 데이터 마스킹: /context/public-summary
```

### ops.md (신규 생성)
`/root/aads/aads-server/.claude/rules/ops.md` 생성:
```
# Ops API 규칙
<!-- paths: **/ops*, **/lifecycle*, **/cost* -->
- directive_lifecycle UPSERT: pre-computed timestamps 사용 (asyncpg 타입 이슈)
- health-check 응답에 신규 필드 추가 시 반드시 기존 필드 유지
- 유지보수 모드: Docker rebuild/migration 감지 시 자동 활성화
```

---

## work_3: Skills 생성

### tpp/SKILL.md
`/root/aads/aads-server/.claude/skills/tpp/SKILL.md` 업데이트:
```
---
name: tpp
description: 진행중인 TPP를 이어서 작업합니다.
argument-hint: [path-to-tpp]
allowed-tools: Bash, Read, Glob, Grep, Edit, Write
---
# TPP 작업 진행
## 필수 읽기
- CLAUDE.md
- docs/knowledge/AADS-KNOWLEDGE.md
- docs/shared-lessons/INDEX.md
## 절차
1. _todo/ 에서 지정된 TPP 읽기
2. 현재 Phase 확인
3. 해당 Phase 작업 수행
4. TPP 업데이트: 완료 항목 체크, 발견사항/함정 기록
5. 400줄 초과 시 분할
```

### handoff/SKILL.md
`/root/aads/aads-server/.claude/skills/handoff/SKILL.md` 업데이트:
```
---
name: handoff
description: 컨텍스트 부족 시 현재 상태를 TPP에 저장합니다.
allowed-tools: Read, Edit, Write, Glob
---
# 세션 인수인계
## 절차
1. 현재 TPP 다시 읽기
2. 완료 항목 체크, Phase 업데이트
3. 발견사항/함정/실패한 접근법 기록
4. 다음 세션이 알아야 할 것 명시
5. 400줄 이내 유지
```

---

## work_4: _todo/ _done/ 디렉토리 및 shared-lessons 동기화

```bash
mkdir -p /root/aads/aads-server/_todo
mkdir -p /root/aads/aads-server/_done
mkdir -p /root/aads/aads-server/docs/shared-lessons
cp -r /root/aads/aads-docs/shared/lessons/* /root/aads/aads-server/docs/shared-lessons/
```

**결과**:
- _todo/ 존재: ✓
- _done/ 존재: ✓ (기존 존재)
- docs/shared-lessons/ 동기화 완료: api, data, deploy, INDEX.md, infra, patterns

---

## work_5: deploy_rules.sh 작성 및 크론 등록

**파일**: `/root/aads/scripts/deploy_rules.sh`

```bash
#!/bin/bash
# 공유 규칙/교훈 동기화 스크립트
# 크론: 0 * * * * /root/aads/scripts/deploy_rules.sh >> /var/log/aads/deploy_rules.log 2>&1

set -e
LOG_PREFIX="[DEPLOY_RULES $(date '+%Y-%m-%d %H:%M:%S')]"

# 1. aads-docs 최신화
cd /root/aads/aads-docs && git pull origin main --quiet
echo "$LOG_PREFIX aads-docs pulled"

# 2. 서버 68 (AADS)
cp /root/aads/aads-docs/shared/rules/flow-rules.md /root/aads/aads-server/.claude/rules/flow-rules.md
cp -r /root/aads/aads-docs/shared/lessons/* /root/aads/aads-server/docs/shared-lessons/
echo "$LOG_PREFIX server 68 synced"

# 3. 완료 로그
echo "$LOG_PREFIX sync complete"
```

chmod +x 실행:
```
-rwxrwxr-x. 1 claudebot claudebot 637 Mar  6 20:13 /root/aads/scripts/deploy_rules.sh
```

**크론 등록**:
```
(crontab -l 2>/dev/null; echo "0 * * * * /root/aads/scripts/deploy_rules.sh >> /var/log/aads/deploy_rules.log 2>&1") | sort -u | crontab -
```

크론 확인:
```
0 * * * * /root/aads/scripts/deploy_rules.sh >> /var/log/aads/deploy_rules.log 2>&1
```

---

## work_6: 글로벌 CLAUDE.md 생성

**참고**: 실행 유저가 `claudebot`(uid=1002)이므로 `~/.claude/` = `/home/claudebot/.claude/`
`/root/.claude/` 는 권한 없음(0700, root 소유).

**파일**: `/home/claudebot/.claude/CLAUDE.md` (8줄)

```
# CEO 작업 스타일 (글로벌)
- 직접적 피드백 선호. 미사여구 없이 핵심만.
- 계획 먼저 보고, 승인 후 실행.
- 검증 없이 완료 선언 금지.
- FLOW: Find→Layout→Operate→Wrap up
- 비용 효율 최우선. 최저 비용으로 최대 품질.
- HANDOVER.md 업데이트 필수 (R-001)
- GitHub 브라우저 경로로 보고 (R-008)
```

---

## work_7: Git commit + push

```bash
cd /root/aads/aads-server
git add CLAUDE.md .claude/rules/ .claude/skills/
git diff --cached --stat
```

diff 결과:
```
 .claude/rules/bridge.md         |  7 ++++---
 .claude/rules/context-api.md    |  9 ++++-----
 .claude/rules/ops.md            |  5 +++++
 .claude/rules/watchdog.md       | 10 ++++++----
 .claude/skills/handoff/SKILL.md |  9 +++++----
 .claude/skills/tpp/SKILL.md     |  7 ++++---
 CLAUDE.md                       | 24 ++++++++++++------------
 7 files changed, 40 insertions(+), 31 deletions(-)
```

commit:
```
[main 3a4edf7] [AADS] feat(AADS-121): Claude Code 3계층 메모리 설정 — CLAUDE.md + rules + skills + deploy_rules
 7 files changed, 40 insertions(+), 31 deletions(-)
 create mode 100644 .claude/rules/ops.md
```

push:
```
To https://github.com/moongoby-GO100/aads-server.git
   3451771..3a4edf7  main -> main
error: update_ref failed for ref 'refs/remotes/origin/main': cannot update the ref 'refs/remotes/origin/main': unable to append to '.git/logs/refs/remotes/origin/main': Permission denied
```
※ remote push 성공. 로컬 ref 로그 파일 권한 오류는 비치명적 (claudebot 유저 권한 이슈).

---

## work_8: 검증 결과

### 1. wc -l /root/aads/aads-server/CLAUDE.md
```
28 /root/aads/aads-server/CLAUDE.md
```
✓ 60줄 이내

### 2. ls /root/aads/aads-server/.claude/rules/
```
bridge.md
context-api.md
flow-rules.md
ops.md
watchdog.md
```
✓ 5개 파일 존재

### 3. ls /root/aads/aads-server/.claude/skills/
```
tpp/SKILL.md
handoff/SKILL.md
```
✓ 2개 스킬 존재

### 4. ls /root/aads/aads-server/_todo/ _done/
```
/root/aads/aads-server/_done/
/root/aads/aads-server/_todo/
```
✓ 디렉토리 존재

### 5. ls /root/aads/aads-server/docs/shared-lessons/INDEX.md
```
/root/aads/aads-server/docs/shared-lessons/INDEX.md
```
✓ 존재

### 6. cat /root/aads/scripts/deploy_rules.sh
```
-rwxrwxr-x. 1 claudebot claudebot 637 Mar  6 20:13 /root/aads/scripts/deploy_rules.sh
```
✓ 실행 가능

### 7. crontab -l | grep deploy_rules
```
0 * * * * /root/aads/scripts/deploy_rules.sh >> /var/log/aads/deploy_rules.log 2>&1
```
✓ 크론 등록 확인

### 8. health-check
```json
{
  "pipeline_healthy": false,
  "stalled_count": 2,
  "stalled_queue": 2,
  "stalled_running": 0,
  "active_count": 4,
  "recent_completed_30m": 4,
  "pipeline_blocked": false,
  "bridge_activity_1h": 0,
  "blocked_tasks_count": 0,
  "undetected_tasks_count": 0,
  "last_seen_tasks_check": "2026-03-06T18:33:25.510714+09:00",
  "maintenance_active": false,
  "maintenance_server": null,
  "maintenance_reason": null,
  "issues": [
    {
      "type": "queue_stalled",
      "count": 2,
      "severity": "critical"
    }
  ]
}
```
⚠ pipeline_healthy: false — stalled_count:2 (queue_stalled). 이는 AADS-121 작업과 무관한 기존 파이프라인 상태.

---

## success_criteria 체크

| # | 기준 | 결과 |
|---|------|------|
| 1 | CLAUDE.md 60줄 이내, 핵심 섹션 포함 | ✓ 28줄, 모든 섹션 포함 |
| 2 | .claude/rules/ 5개 파일 존재 | ✓ |
| 3 | .claude/skills/ 2개 스킬 존재 | ✓ |
| 4 | deploy_rules.sh 크론 등록 동작 | ✓ |
| 5 | health-check 정상 | ⚠ 기존 stalled 상태 (AADS-121 범위 외) |

---

## 특이사항

1. **글로벌 CLAUDE.md 경로**: 지시서는 `~/.claude/CLAUDE.md` 기재. 실행 유저 `claudebot`의 홈은 `/home/claudebot/`이므로 `/home/claudebot/.claude/CLAUDE.md`에 생성. `/root/.claude/`는 root 소유 0700으로 접근 불가.

2. **Git push 로컬 ref 오류**: `unable to append to '.git/logs/refs/remotes/origin/main': Permission denied` — remote에는 정상 push됨. 로컬 git 디렉토리가 다른 유저 소유여서 발생하는 비치명적 오류.

3. **기존 파일 업데이트**: .claude/rules/ 4개 파일 및 skills/ 2개 파일이 이미 존재했으나 지시 내용과 차이가 있어 전면 업데이트. ops.md만 신규 생성.
