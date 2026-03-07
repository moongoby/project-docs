---
project: AADS
task_id: AADS-149
completed_at: 2026-03-07T14:35:00+09:00
---

# AADS-149 실행 결과 보고서

## 태스크 개요

- **지시서**: /root/.genspark/directives/pending/AADS_20260307_121538_BRIDGE.md
- **태스크 ID**: AADS-149
- **우선순위**: P1-HIGH
- **크기**: S
- **설명**: 파이프라인 전수조사에서 발견·조치된 버그 5건에 대한 Wrap 보고서 작성 및 교훈 등록 (문서화 전용)

---

## 작업 1: Wrap 보고서 생성

**파일**: `/root/aads/aads-docs/reports/AADS-149-WRAP_pipeline-audit-5bugs.md`

**상태**: ✅ 생성 완료

**내용 요약**:

### BUG-1 (Critical): auto_trigger.sh — SCP 실패 시 seen_tasks 영구 차단
- **원인**: seen_tasks 선등록 후 SCP 실패 시 롤백 로직 없음
- **수정**: `unset seen_tasks["$task_id"]` 롤백 로직 추가 (SCP 실패 직후)
- **적용 서버**: 211, 68, 114

### BUG-2 (High): auto_trigger.sh — RESULT 원격 폴러 타임아웃 25분 < HARD_TIMEOUT 30분
- **원인**: `seq 1 50` (30초×50=25분) < HARD_TIMEOUT 30분
- **수정**: `seq 1 80` (30초×80=40분) — HARD_TIMEOUT + 10분 여유
- **적용 서버**: 211, 68, 114

### BUG-3 (Medium): auto_trigger.sh — aads_lifecycle_queued() 호출 시 _rt/_title 변수 미정의
- **원인**: 변수 추출 코드가 lifecycle 호출 이후에 위치
- **수정**: 변수 추출(`_rt`, `_title`)을 `aads_lifecycle_queued()` 호출 앞으로 이동
- **적용 서버**: 211, 68, 114

### BUG-4 (Critical): claude_exec.sh — Claude가 pending/running 경로 삭제 가능 + /proc grep 금지 없음
- **원인**: CONTEXT_HEADER에 파이프라인 경로 보호 규칙 및 /proc grep 금지 미주입
- **수정**: CONTEXT_HEADER에 아래 규칙 추가
  - `/root/.genspark/directives/pending/ 및 running/ 경로 파일 절대 삭제·이동·수정 금지`
  - `작업 디렉토리(/root/aads) 외부 파일 생성 금지`
  - `/proc, /sys 경로에 grep -r 절대 금지 → pgrep, ps, lsof 사용`
- **적용 서버**: 211, 68, 114

### BUG-5 (High): done_watcher.sh — 114서버 SSH 포트 7916 미지정
- **원인**: SSH 포트 기본값 22 사용 → 서버 114 포트 7916 연결 실패
- **수정**: `get_project_ssh_port()` 함수 추가 (SF/NTV2/NAS → 7916, 나머지 → 22), ssh -p / scp -P 적용
- **적용 서버**: 211 (done_watcher.sh)

---

## 작업 2: 교훈 등록

**파일**: `/root/aads/aads-docs/shared/lessons/infra/L-011_pipeline-audit-critical-patterns.md`

**상태**: ✅ 생성 완료

**교훈 핵심**:
1. 상태 선등록 후 실행 실패 시 반드시 롤백 (BUG-1)
2. 폴러 타임아웃 ≥ HARD_TIMEOUT + 10분 여유 (BUG-2)
3. 변수 정의-사용 순서는 함수 호출 전 검증 (BUG-3)
4. AI 작업자에게 파이프라인 제어 디렉토리 접근 권한 절대 부여 금지 (BUG-4)
5. 멀티서버 SSH 포트는 프로젝트별 매핑 함수로 관리 (BUG-5)

**INDEX.md 업데이트**:
- `/root/aads/aads-docs/shared/lessons/INDEX.md` — 10건 → 11건 (L-011 추가)
- 변경 라인: `- L-011: 파이프라인 감사 5대 패턴 (상태롤백/폴러마진/변수순서/AI격리/멀티포트) [AADS-149] → infra/L-011_pipeline-audit-critical-patterns.md`

---

## 작업 3: HANDOVER 업데이트

**HANDOVER-HISTORY.md**: `/root/aads/aads-docs/HANDOVER-HISTORY.md`
**상태**: ✅ AADS-149 완료 사항 추가 (파일 상단 최신 태스크로 삽입)

**HANDOVER.md**: `/root/aads/aads-docs/HANDOVER.md`
**상태**: ✅ 아래 항목 업데이트
- 버전: v8.4 → v8.5
- 최종 업데이트 메모: "AADS-149 파이프라인 전수조사 버그 5건 수정 Wrap"
- 프로젝트 현황: AADS 최근 태스크 AADS-148 → AADS-149
- AADS-149 주요 변경 섹션 신규 추가

---

## Git 커밋 및 Push

**커밋 SHA**: `0688e5b`
**커밋 메시지**: `docs(AADS-149): 파이프라인 전수조사 버그 5건 Wrap + 교훈 L-011 등록`

**변경 파일**:
- `reports/AADS-149-WRAP_pipeline-audit-5bugs.md` (신규)
- `shared/lessons/infra/L-011_pipeline-audit-critical-patterns.md` (신규)
- `shared/lessons/INDEX.md` (수정)
- `HANDOVER-HISTORY.md` (수정)
- `HANDOVER.md` (수정)

**Push 결과**: ✅ 성공
```
To https://github.com/moongoby-GO100/aads-docs.git
   8075f37..0688e5b  main -> main
```

---

## Success Criteria 검증

| # | 기준 | 결과 |
|---|------|------|
| 1 | reports/AADS-149-WRAP_pipeline-audit-5bugs.md GitHub push | ✅ 완료 (0688e5b) |
| 2 | shared/lessons/infra/L-011 생성 및 INDEX.md 등록 | ✅ 완료 |
| 3 | HANDOVER-HISTORY.md에 AADS-149 기록 추가 | ✅ 완료 |
| 4 | git push HTTP 200 확인 | ✅ 완료 (8075f37..0688e5b) |

---

## 완료 선언

AADS-149 모든 작업 완료. 문서화 3개 작업(Wrap 보고서, 교훈 L-011, HANDOVER 업데이트) 수행 및 GitHub push 검증 완료.
