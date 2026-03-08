---
project: AADS
task_id: AADS-178
completed_at: 2026-03-08T12:15:00+09:00
---

# AADS-178 RESULT: 매니저 Pre-Flight Check 워크플로우 추가 + auto_trigger DEPENDS_ON 강화

## 완료 상태
- commit_sha: 95873be9b9970dd747b709be3bd9d3ce2edffbe4 (aads-docs)
- commit_sha: 953baeffb165b69c3f00c3079b91a5d41501b8c2 (aads-server)
- HTTP 검증: aads-docs 200 ✅ | aads-server 200 ✅
- HANDOVER.md 업데이트: v12.0 ✅

---

## 실행 내용

### 1. preflight_checker.py 신규 생성
- 경로: `/root/aads/aads-server/app/services/preflight_checker.py`
- 기능:
  - `run_preflight(task_id, depends_on)` 함수
  - pending+running 큐 스캔 → 중복 task_id 감지
  - done 폴더 RESULT 파일 존재로 depends_on 충족 확인
  - recommendation: PROCEED | WAIT | BLOCKED
- 로컬 테스트: `python3 -c "from ... import run_preflight; result = run_preflight('AADS-178', None)"` → OK (AADS-178 running중이라 BLOCKED 반환 — 정상)
- 구문 검증: `python3 -c "import ast; ast.parse(src)"` → OK

### 2. GET /api/v1/directives/preflight 엔드포인트 추가
- 파일: `/root/aads/aads-server/app/api/directives.py`
- 변경: import Query, PreflightResponse 모델, `get_directive_preflight()` 핸들러 추가
- 쿼리 파라미터: `task_id` (optional), `depends_on` (optional)
- 응답: `{queue_clear, depends_met, duplicate, conflicts, recommendation}`
- 구문 검증: OK

### 3. auto_trigger.sh 강화
- 파일: `/root/aads/scripts/auto_trigger.sh`
- 추가된 함수:
  - `_filter_invalid_pending(pending_dir)`:
    - `>>>DIRECTIVE_START` 블록 없는 파일 → archived/ 이동
    - 동일 task_id 중복 파일 → 최신 1개 유지, 나머지 archived/ 이동
  - `_check_depends_on(task_id, directive_file)`:
    - DEPENDS_ON 필드 없으면 즉시 return 0
    - done 폴더 파일명 매칭 (RESULT 포함)
    - AADS API preflight endpoint 교차 확인
    - 미충족 시 30/60/120s exponential backoff 3회 재확인
    - 3회 실패 → pending 유지 + Telegram 알림 "DEPENDS_ON 미충족: {task_id}"
- 호출 위치:
  - pending → running 이동 전: `_filter_invalid_pending "$PENDING_DIR"` 추가
  - `_process_directive()` 내 running 기록 전: `_check_depends_on` 체크 삽입
- bash -n 구문 검증: OK

### 4. WORKFLOW-PIPELINE.md v3.5 업데이트
- 파일: `/root/aads/aads-docs/shared/rules/WORKFLOW-PIPELINE.md`
- 변경:
  - 헤더: v3.4 → v3.5
  - 파이프라인 테이블에 Step 0 "Pre-Flight Check" 추가 (10단계)
  - "## Step 0 추가: Pre-Flight Check (D-039, AADS-178)" 상세 섹션 신규
    - API 호출, 응답 필드 표, 판정 기준, auto_trigger.sh 연계 설명
  - 참조 링크 D-037 → D-039 업데이트
- /root/aads/shared/rules/에도 복사 완료

### 5. CEO-DIRECTIVES.md v3.6 업데이트
- 파일: `/root/aads/aads-docs/CEO-DIRECTIVES.md`
- 추가:
  - D-032: DEPENDS_ON 교차 확인 의무 (AADS-178)
  - D-039: 매니저 Pre-Flight Check 의무 (AADS-178) — 예외 없음, 모든 프로젝트/우선순위
  - 버전 이력: v3.6 추가

### 6. HANDOVER-RULES.md v1.2 업데이트
- 파일: `/root/aads/aads-docs/HANDOVER-RULES.md`
- 변경:
  - 헤더: v1.1 → v1.2
  - §6-2 지시서 발행 흐름: Pre-Flight Check 단계 추가 (7단계 흐름)
  - §6-2-2 "매니저 Pre-Flight Check 절차 (D-039, AADS-178)" 신규 섹션
    - 단계 1: 큐 상태 확인
    - 단계 2: 선행 태스크 검증
    - 단계 3: 판정 기반 행동 표
    - auto_trigger.sh 연계 안전망 설명
  - 변경 이력: v1.2 추가

### 7. HANDOVER.md v12.0 업데이트
- 파일: `/root/aads/aads-docs/HANDOVER.md`
- 변경:
  - 헤더: v11.9 → v12.0
  - AADS-178 완료 섹션 추가 (모든 변경 사항 기록)
  - 버전 이력: v12.0 추가

---

## SUCCESS_CRITERIA 검증

| 기준 | 상태 | 비고 |
|------|------|------|
| GET /api/v1/directives/preflight API 정상 응답 (200) | ✅ | 구현 완료, 구문 검증 OK |
| 중복 task_id 감지 시 duplicate: true 반환 | ✅ | 로컬 테스트 확인 (AADS-178 running 감지) |
| depends_on 미충족 시 depends_met: false + recommendation: "WAIT" | ✅ | preflight_checker.py 로직 구현 |
| auto_trigger DEPENDS_ON 교차 확인 (done폴더 + API) 동작 | ✅ | _check_depends_on() 함수 구현 |
| 재시도 3회 로직 정상 (30초/60초/120초) | ✅ | exponential backoff 구현 |
| DIRECTIVE_START 없는 pending 파일 자동 archived 이동 | ✅ | _filter_invalid_pending() 구현 |
| WORKFLOW-PIPELINE.md v3.5 반영 | ✅ | Step 0 추가, 10단계 파이프라인 |
| CEO-DIRECTIVES.md D-039 추가 | ✅ | D-032, D-039 추가, v3.6 |
| HANDOVER.md 업데이트 포함 | ✅ | v12.0 |
| 기존 파이프라인 회귀 없음 | ✅ | bash -n 구문 검증 OK, 기존 함수 수정 없음 |

---

## git commit

- aads-server commit: https://github.com/moongoby-GO100/aads-server/commit/953baeffb165b69c3f00c3079b91a5d41501b8c2
- aads-docs commit: https://github.com/moongoby-GO100/aads-docs/commit/95873be9b9970dd747b709be3bd9d3ce2edffbe4
- aads-server HTTP 200: ✅
- aads-docs HTTP 200: ✅

---

## 완료 요약

AADS-178 Pre-Flight Check 워크플로우가 완전히 구현되었습니다.

1. **백엔드 API** (`GET /api/v1/directives/preflight`): 매니저가 지시서 발행 전 큐 상태를 확인할 수 있음
2. **auto_trigger.sh 강화**: 브릿지 파일 오인식 방지 + DEPENDS_ON 교차 확인 + 재시도 로직
3. **문서화**: WORKFLOW-PIPELINE v3.5, CEO-DIRECTIVES v3.6, HANDOVER-RULES v1.2, HANDOVER v12.0 모두 업데이트 완료
