# DOCS-FIX-005 요약

**작성일**: 2026-02-25 KST  
**목적**: 보고서 project-docs 404 해결 + CONTEXT/HANDOVER SHA 플레이스홀더 교체

## 해결 대상 (4건)

| # | 항목 | 조치 |
|---|------|------|
| 1 | R3-FRONT-002-report.md project-docs 404 | 서버 runbook 7단계에서 `newtalk-v2-api/reports/`로 복사 후 project-docs 푸시 |
| 2 | R3-API-003-report.md project-docs 404 | 동일 |
| 3 | CONTEXT.md SHA 플레이스홀더 2건 | 서버 runbook 4단계에서 `(푸시 후 SHA 기입)` → 실제 SHA 치환 |
| 4 | HANDOVER.md SHA 플레이스홀더 2건 | 서버 runbook 4단계에서 `(12단계 푸시 후 기입)`, `(서버 main 푸시 후 기입)` → 실제 SHA 치환 |

## 로컬에서 한 작업

- **runbook 스크립트 추가**: `docs/scripts/DOCS-FIX-005-runbook.sh`
  - 서버에서 실행: `ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86` 후 `/srv/newtalk-v2`에서 `bash docs/scripts/DOCS-FIX-005-runbook.sh`
  - 4단계에서 CONTEXT.md, HANDOVER.md, R3-FRONT-002-report.md, R3-API-003-report.md 내 SHA 플레이스홀더를 `git log --oneline -1` 결과로 일괄 치환
  - 5단계 검사는 본 작업에서 치환한 문구만 검사 (다른 보고서의 "푸시 후 기록" 등은 제외)
- **문서 수정 없음**: CONTEXT.md, HANDOVER.md는 runbook이 기대하는 문자열 그대로 유지 (서버에서 치환).

## 서버에서 실행 순서

1. SSH 접속 후 `cd /srv/newtalk-v2`
2. (선택) `git pull` 로 runbook 스크립트 반영
3. `bash docs/scripts/DOCS-FIX-005-runbook.sh`
4. 8단계 원격 검증까지 완료 후, 완료 보고 문구 확인

## 검증

- V2 커밋 메시지: `[DOCS] DOCS-FIX-005 SHA 플레이스홀더 교체 (R3-FRONT-002, R3-API-003)`
- project-docs 커밋: `[DOCS] DOCS-FIX-005 R3-FRONT-002·R3-API-003 보고서 동기화, SHA 교체`
- 원격 200 확인:
  - `https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/R3-FRONT-002-report.md`
  - `https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/R3-API-003-report.md`
  - `https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md`
  - `https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/handover/HANDOVER.md`
