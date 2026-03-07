---
project: AADS
task_id: AADS-163
completed_at: 2026-03-08 17:41 KST
commit_sha_aads_docs: a685325
commit_sha_aads_server: cf0373e
commit_sha_aads_dashboard: 18cb7a6
qa_status: PASS
design_status: PASS
---

# AADS-163 실행 결과: QA+디자인 3단계 품질 게이트 통합

## 실행 요약

개발→QA→디자인 3단계 품질 게이트를 claude_exec.sh에 통합하고, auto_trigger.sh 후처리, 대시보드 /ops 페이지, 문서(CEO-DIRECTIVES, RULE-MATRIX, WORKFLOW-PIPELINE, HANDOVER) 전체를 업데이트하였다.

---

## 1. claude_exec.sh 3단계 품질 게이트

### 추가 함수: `_run_qa_gate()`
- **위치**: `/root/aads/claude_exec.sh` (사용량 DB 기록 섹션 앞)
- **동작**: Claude 코드 수정 완료 후 test-writer 에이전트를 실행
- **재시도**: QA FAIL 시 자동 재작업 최대 2회 (각 재작업 후 재QA)
- **FAIL 처리**: 2회 초과 시 RESULT_FILE에 `qa_status: FAIL` 기록 + 서킷브레이커 카운트+1 신호
- **PASS 처리**: RESULT_FILE에 `qa_status: PASS` 기록 → 디자인 게이트 진행

### 추가 함수: `_run_design_gate()`
- **위치**: `/root/aads/claude_exec.sh` (_run_qa_gate 바로 아래)
- **동작**: QA PASS 후 doc-writer 에이전트 실행, UI/UX 변경 여부 판단
- **PASS**: RESULT_FILE에 `design_status: PASS` 기록
- **REVIEW_NEEDED**: `aads_queue_msg` CEO Chat 보고 + Telegram 알림 → 60초 대기 → `design_status: PASS_TIMEOUT`
- **RESULT_FILE 최종 필드**: `qa_status: PASS | FAIL`, `design_status: PASS | PASS_TIMEOUT | REVIEW_NEEDED`

### 실행 흐름 수정
```
Claude 코드 수정 완료
     ↓
_run_qa_gate (test-writer, 최대 2회 재시도)
     ├── PASS → _run_design_gate (doc-writer)
     │           ├── PASS → RESULT_FILE 생성
     │           └── REVIEW_NEEDED → CEO 보고 → 60초 → PASS_TIMEOUT
     └── FAIL (2회 초과) → qa_status=FAIL + 서킷브레이커 트리거
              ↓
aads_lesson_check, commit SHA 기록, etc. (기존 흐름 유지)
```

---

## 2. auto_trigger.sh 후처리 수정

### 추가 블록: RESULT_FILE에서 qa_status / design_status 읽기
- **위치**: `/root/aads/scripts/auto_trigger.sh` — `_process_directive()` 함수 내 exec_exit 판단 직전
- **동작**:
  - `qa_status=FAIL` 감지 시: `/ops/circuit-breaker/increment` API 호출 + Telegram 알림 + `exec_exit=1`
  - Telegram 알림 형식: `✅ [project] task_id 완료\nQA: {qa_status} | 디자인: {design_status}\n커밋: {sha}`

### aads-server/scripts/auto_trigger.sh 동일 적용
- **위치**: `/root/aads/aads-server/scripts/auto_trigger.sh`
- 동일한 QA/디자인 상태 읽기 + 서킷브레이커 연동 + Telegram 판정 포함 로직 추가

---

## 3. 대시보드 /ops 페이지 확장

### ops/page.tsx 추가 섹션
- **파일**: `/root/aads/aads-dashboard/src/app/ops/page.tsx`
- **섹션 6 (신규): QA Results (최근 20건)**
  - 테이블: Task ID, 프로젝트, 판정(PASS/FAIL 뱃지), 재시도 횟수, 상세, 시각
  - FAIL 행 강조 표시 (빨간 배경)
  - 접기/펼치기 토글
- **섹션 7 (신규): Design Reviews (최근 10건)**
  - 카드 형태: 스크린샷 썸네일(56×40px) + Task ID + 프로젝트 + 판정 뱃지 + 시각
  - 판정: PASS(초록) / PASS_TIMEOUT(타임아웃 표시) / REVIEW_NEEDED(빨강)
  - 클릭 시 상세 내용 토글 표시

### api.ts 추가 메서드
- **파일**: `/root/aads/aads-dashboard/src/lib/api.ts`
- `getOpsQaResults(limit = 20)` → `GET /ops/qa-results?limit={limit}`
- `getOpsDesignReviews(limit = 10)` → `GET /ops/design-reviews?limit={limit}`

---

## 4. 문서 업데이트

### CEO-DIRECTIVES.md v3.5
- **파일**: `/root/aads/aads-docs/CEO-DIRECTIVES.md`
- **D-030**: QA 에이전트 의무화 — test-writer 서브에이전트, 최대 2회 재시도, RESULT_FILE qa_status 기록 의무
- **D-031**: 디자인 검증 의무화 — doc-writer 서브에이전트, REVIEW_NEEDED 시 CEO 보고+60초 타임아웃, RESULT_FILE design_status 기록 의무
- **버전 이력**: v3.5 행 추가

### RULE-MATRIX.md
- **파일**: `/root/aads/aads-docs/shared/rules/RULE-MATRIX.md`
- D-030, D-031 행 추가 (5단계:✅, 6단계:✅, 7단계:✅/⚠️, 8단계:✅)
- 5단계 핵심 규칙 요약: D-030, D-031 포함
- 6단계 핵심 규칙 요약: RESULT_FILE 기록 규칙 포함
- 8단계 핵심 규칙 요약: qa_status/design_status 확인 포함
- 규칙 목록: D-030, D-031 행 추가

### WORKFLOW-PIPELINE.md
- **파일**: `/root/aads/aads-docs/shared/rules/WORKFLOW-PIPELINE.md` (v3.3→v3.4)
- 6단계를 "Claude 실행 + QA + 디자인 검증"으로 확장
- D-030/D-031 세부 흐름 섹션 추가 (실행 순서, 소요시간 추정)
- 참조 업데이트: RULE-MATRIX v1.2, CEO-DIRECTIVES D-016~D-031

### HANDOVER.md v10.8
- **파일**: `/root/aads/aads-docs/HANDOVER.md`
- AADS 현황: AADS-163 완료 반영
- QA/디자인 에이전트 현황 섹션 신규 추가 (에이전트 파일 경로, 판정 기준, 대시보드 API)
- CEO-DIRECTIVES 전문 요약: D-030, D-031 항목 추가

### STATUS.md
- **파일**: `/root/aads/aads-docs/STATUS.md`
- `last_completed: AADS-163`
- `commit_sha: 74d2401`
- history에 AADS-163 추가

---

## 5. git push + HTTP 200 검증

| 리포 | 커밋 SHA | HTTP 200 |
|------|----------|----------|
| aads-docs | a685325 (최종, STATUS.md SHA 확정) | ✅ 200 |
| aads-server | cf0373e | ✅ 200 |
| aads-dashboard | 18cb7a6 | ✅ 200 |

---

## 6. success_criteria 검증

| 기준 | 결과 |
|------|------|
| claude_exec.sh에 개발→QA→디자인 3단계 순차 흐름 구현 | ✅ _run_qa_gate() + _run_design_gate() 구현 |
| QA FAIL 시 자동 재작업 루프 + 서킷브레이커 연동 | ✅ 최대 2회 재작업 + /ops/circuit-breaker/increment 호출 |
| DESIGN_REVIEW_NEEDED 시 CEO Chat 보고 전송 | ✅ aads_queue_msg + Telegram + 60초 타임아웃 |
| /ops 페이지에 QA Results + Design Reviews 섹션 표시 | ✅ 섹션 6/7 추가, 테이블+카드+썸네일 |
| CEO-DIRECTIVES.md v3.5에 D-030, D-031 존재 | ✅ |
| RULE-MATRIX.md에 D-030, D-031 행 추가 | ✅ |
| WORKFLOW-PIPELINE.md v3.4에 QA/디자인 단계 반영 | ✅ |
| STATUS.md last_completed=AADS-163 갱신 | ✅ commit_sha=74d2401 |
| git push HTTP 200 확인 (3개 리포) | ✅ aads-docs/aads-server/aads-dashboard |
| 커밋 메시지: [AADS-163] feat: QA+디자인 3단계 품질 게이트 통합 | ✅ |

---

## 7. 주요 파일 변경 목록

| 파일 | 변경 내용 |
|------|-----------|
| `/root/aads/claude_exec.sh` | _run_qa_gate(), _run_design_gate() 함수 추가 + 성공 경로에 게이트 호출 |
| `/root/aads/scripts/auto_trigger.sh` | qa_status=FAIL 서킷브레이커 연동 + Telegram 판정 포함 |
| `/root/aads/aads-server/scripts/claude_exec.sh` | 동일 QA/디자인 게이트 추가 |
| `/root/aads/aads-server/scripts/auto_trigger.sh` | 동일 후처리 추가 |
| `/root/aads/aads-dashboard/src/app/ops/page.tsx` | QA Results + Design Reviews 섹션 신규 |
| `/root/aads/aads-dashboard/src/lib/api.ts` | getOpsQaResults, getOpsDesignReviews 추가 |
| `/root/aads/aads-docs/CEO-DIRECTIVES.md` | v3.5: D-030, D-031 추가 |
| `/root/aads/aads-docs/shared/rules/RULE-MATRIX.md` | D-030, D-031 행 추가 |
| `/root/aads/aads-docs/shared/rules/WORKFLOW-PIPELINE.md` | v3.4: 6단계 QA+디자인 확장 |
| `/root/aads/aads-docs/HANDOVER.md` | v10.8: QA/디자인 에이전트 현황 + AADS-163 반영 |
| `/root/aads/aads-docs/STATUS.md` | last_completed=AADS-163, commit_sha=74d2401 |
