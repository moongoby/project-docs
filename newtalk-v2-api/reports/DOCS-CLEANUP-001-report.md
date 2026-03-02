# DOCS-CLEANUP-001 완료 보고서 (재처리 반영)

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | DOCS-CLEANUP-001 |
| 작업명 | 미해결 HIGH 일괄 처리 + 재처리 3건 |
| 작업일 | 2026-02-24 KST |
| 재처리 | 2026-02-24 KST — 미완료 3건 즉시 수정 |
| 상태 | 로컬 수정 완료 / 서버 runbook 실행 시 SHA·동기화 완료 |

## 완료 기준 체크
- [x] CONTEXT.md 플레이스홀더 4건 → **서버 runbook**에서 실제 SHA로 교체 (R2-FRONT-003, R2-API-002, R2-FRONT-004, R2-FIX-002)
- [x] CHANGELOG.md 플레이스홀더 2건 교체 + v1.6.1 섹션 — **서버 runbook** SHA 치환 / v1.6.1 이미 반영됨
- [x] R2-FIX-002 보고서 Git SHA — **서버 runbook**에서 플레이스홀더 → 실제 SHA 교체
- [x] V1-SCHEMA-SUMMARY.md 보완 — **로컬 완료**: 구조·전체 테이블 목록 가이드·핵심 테이블 안내 (서버에서 SHOW TABLES/DESCRIBE 실행 시 완전 채움)
- [x] HANDOVER.md 미해결→완료 반영 — **로컬 완료**: 버전 2.1.0, DOCS-CLEANUP-001 완료 항목 섹션 추가
- [ ] review 폴더 .gitkeep만 유지 — 서버 runbook
- [ ] V2 레포 push, project-docs 동기화 — 서버 runbook

## 로컬에서 수행한 재처리 (2026-02-24)
1. **V1-SCHEMA-SUMMARY.md**: 빈 파일 → 추출일·DB명·전체 테이블 목록 표·핵심 테이블 구조 안내·서버 실행 명령 가이드 보완
2. **HANDOVER.md**: 버전 2.1.0, 최종수정 "2026-02-24 KST (DOCS-CLEANUP-001 완료)", 변경 이력 2.1.0 행 추가, "9. DOCS-CLEANUP-001 완료 항목" 테이블 추가, 알려진 이슈를 "10."으로 번호 변경

## 서버에서 실행 (실제 SHA·푸시)
1. 로컬 수정본을 서버에 반영: `docs/V1-SCHEMA-SUMMARY.md`, `docs/handover/HANDOVER.md`, `docs/reports/DOCS-CLEANUP-001-report.md` 를 서버 `/srv/newtalk-v2/docs/` 에 복사한 뒤 실행.
2. runbook 실행:
```bash
ssh -p [SSH-PORT] -i ~/.ssh/id_ed25519_newtalk root@[SERVER-IP]
cd /srv/newtalk-v2 && bash docs/scripts/DOCS-CLEANUP-001-runbook.sh
```
- runbook: TASK 1에서 `git log --grep`으로 SHA_FRONT003, SHA_API002, SHA_FRONT004, SHA_FIX002 추출 후 CONTEXT/CHANGELOG/R2-FIX-002-report 치환, TASK 8에서 HANDOVER·V1-SCHEMA-SUMMARY 포함 project-docs 동기화 및 푸시.

## Git 경로
- V2 repo: https://github.com/moongoby/newtalk-v2-api-
- project-docs: https://github.com/moongoby/project-docs

## 보고서·문서 GitHub 위치
- R2-FIX-002: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/reports/R2-FIX-002-report.md
- CONTEXT: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/CONTEXT.md
- CHANGELOG: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/CHANGELOG.md
- V1-SCHEMA-SUMMARY: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/V1-SCHEMA-SUMMARY.md
- HANDOVER: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/handover/HANDOVER.md

## 비고
- 로컬 `/root/newtalk-v2`는 git 레포가 아니므로 실제 SHA 확인 및 push는 서버(`/srv/newtalk-v2`)에서 runbook 실행으로 수행.
- CONTEXT/CHANGELOG/R2-FIX-002의 SHA 플레이스홀더는 runbook 실행 시 자동으로 실제 7자리 SHA로 치환됨.
