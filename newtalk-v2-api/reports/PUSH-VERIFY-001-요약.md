# PUSH-VERIFY-001 요약

| 항목 | 내용 |
|------|------|
| 지시서 ID | PUSH-VERIFY-001 |
| 목표 | 서버 로컬 작업물 확인 → V2 레포 + project-docs 레포 push → 경로 보고 |
| 실행 위치 | **서버** `ssh -p [SSH-PORT] -i ~/.ssh/id_ed25519_newtalk root@[SERVER-IP]` → `cd /srv/newtalk-v2` |

## 로컬(워크스페이스) 검증 결과 (STEP 1 대체)

- **V2 Git**: 현재 워크스페이스 `/root/newtalk-v2` 에는 `.git` 없음 → **push는 서버 `/srv/newtalk-v2` 에서만 가능**
- **R3-FRONT-004 (DM UI)**: **구현완료**
  - `frontend/src/lib/dm-api.ts`, `frontend/src/types/dm.ts` 존재
  - 메시지 페이지: `frontend/src/app/(retail)/retail/messages/page.tsx` (App Router 경로)
  - 보고서: `docs/reports/R3-FRONT-004-report.md` 존재
- **R3-API-005 (Shorts API)**: **구현완료**
  - 컨트롤러: `app/Http/Controllers/Api/ShortController.php` (지시서는 ShortsController라고 했으나 실제는 ShortController)
  - `app/Services/ShortsService.php`, `app/Models/Short.php` 존재
  - 보고서: `docs/reports/R3-API-005-report.md` 존재
- **CHANGELOG**: v2.8.0 (DM UI), v2.9.0 (Shorts API) 반영됨
- **플레이스홀더**: CONTEXT.md 4건, HANDOVER.md 4건, ARCHITECTURE.md 4건, R3-API-004-report.md 1건, R3-API-005-report.md 1건 → **서버 runbook에서 푸시 후 REPLACE_SHA 치환**

## 서버에서 실행할 Runbook

```bash
ssh -p [SSH-PORT] -i ~/.ssh/id_ed25519_newtalk root@[SERVER-IP]
cd /srv/newtalk-v2
chmod +x docs/scripts/PUSH-VERIFY-001-runbook.sh
bash docs/scripts/PUSH-VERIFY-001-runbook.sh
```

Runbook이 수행하는 작업:

1. **STEP 1**: Docker ps, git log, DM/Shorts 파일 존재 확인, 보고서·CHANGELOG 확인, git status
2. **STEP 2**: `git add -A`, 필요 시 커밋, `git push origin main`, V2_SHA 기록
3. **REPLACE_SHA 치환**: CONTEXT, HANDOVER, ARCHITECTURE, R3-API-004-report, R3-API-005-report → 푸시 후 실제 7자리 SHA로 치환, 필요 시 재커밋·푸시
4. **STEP 3**: project-docs 위치 확인/클론, pull, 문서 복사, 민감정보 검사, commit, push, PDOCS_SHA 기록
5. **STEP 6**: 헬스체크 (V1, V2 API, Frontend), Docker ps
6. **최종 보고**: 지시서 형식에 맞춰 채팅에 붙여넣을 문자열 출력

## 최종 보고 형식 (서버 runbook 실행 후 채움)

```
PUSH-VERIFY-001 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━
완료 시각: {KST}
V2 repo SHA: {7자리}
project-docs SHA: {7자리}

R3-FRONT-004 (DM UI): 구현완료 — 컴포넌트 10개, API함수 10개
R3-API-005 (Shorts API): 구현완료 — 테이블 5개, EP 11개

GitHub 경로:
- CONTEXT.md: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/CONTEXT.md
- CHANGELOG.md: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/CHANGELOG.md
- HANDOVER.md: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/handover/HANDOVER.md
- ARCHITECTURE.md: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/architecture/NT-V2-ARCHITECTURE.md
- R3-FRONT-004: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/reports/R3-FRONT-004-report.md
- R3-API-005: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/reports/R3-API-005-report.md

헬스: V1 {code}, V2 API {code}, Frontend {code}
Docker: {N}/5 Up
플레이스홀더 잔여: {N}건
HANDOVER 다음작업큐: R3-FRONT-005 (Shorts UI), (선택) 카페24 실제 연동 테스트

다음 작업: R3-FRONT-005 (Shorts UI)
```

## 참고

- **STEP 4 (누락 작업)** 불필요 — R3-FRONT-004, R3-API-005 모두 구현되어 있음.
- **project-docs** 레포는 서버에서 `project-docs-repo` 또는 `/data/project-docs` 에 있을 수 있음. runbook이 순서대로 찾아서 사용함.
- `.cursorrules` 규칙: 작업은 서버에서 직접 실행. 플레이스홀더 남긴 보고서로 push 금지 → runbook에서 푸시 후 SHA 치환 후 재커밋 반영.
