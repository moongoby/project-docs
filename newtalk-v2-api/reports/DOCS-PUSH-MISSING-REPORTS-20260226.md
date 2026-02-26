# 문서 레포(project-docs) 미푸시 보고서 반영 — 경로 보고

**작성일시:** 2026-02-26 KST  
**작업:** 문서 레포에 누락된 보고서 확인 후 일괄 푸시

---

## 1. 누락 확인 결과 (푸시 전)

| 원본 위치 | 파일명 | 비고 |
|-----------|--------|------|
| server116/docs/reports/ | 116-DB-ACCESS-REPORT.md | 116 서버 MySQL 접속 정보 |
| newtalk-v2/docs/reports/ | DOCS-ARCH-001-FIX-보고.md | DOCS-ARCH 404 수정 보고 |
| newtalk-v2/docs/reports/ | DOCS-ARCH-001-보완-요약.md | DOCS-ARCH 보완 요약 |
| newtalk-v2/docs/reports/ | DOCS-FIX-007-요약.md | DOCS-FIX-007 요약 |
| newtalk-v2/docs/reports/ | PUSH-VERIFY-001-요약.md | 푸시 검증 요약 |
| newtalk-v2/docs/reports/ | R3-API-005-report.md | R3 Shorts API 보고서 |
| newtalk-v2/docs/reports/ | R3-FRONT-004-report.md | R3 브랜드 페이지 보고서 |

---

## 2. 푸시 완료

- **레포:** project-docs (git@github.com:moongoby/project-docs.git)
- **브랜치:** master
- **커밋:** `744bfe7` — docs: add missing reports (116-DB-ACCESS, DOCS-ARCH-001, DOCS-FIX-007, PUSH-VERIFY-001, R3-API-005, R3-FRONT-004)
- **추가 파일 수:** 7

---

## 3. Public 경로 (project-docs 기준)

아래 경로는 GitHub project-docs **master** 기준입니다.

| 보고서 | Public 경로 |
|--------|------------------|
| 116-DB-ACCESS-REPORT | `newtalk-v2-api/reports/116-DB-ACCESS-REPORT.md` |
| DOCS-ARCH-001-FIX-보고 | `newtalk-v2-api/reports/DOCS-ARCH-001-FIX-보고.md` |
| DOCS-ARCH-001-보완-요약 | `newtalk-v2-api/reports/DOCS-ARCH-001-보완-요약.md` |
| DOCS-FIX-007-요약 | `newtalk-v2-api/reports/DOCS-FIX-007-요약.md` |
| PUSH-VERIFY-001-요약 | `newtalk-v2-api/reports/PUSH-VERIFY-001-요약.md` |
| R3-API-005-report | `newtalk-v2-api/reports/R3-API-005-report.md` |
| R3-FRONT-004-report | `newtalk-v2-api/reports/R3-FRONT-004-report.md` |

**Raw URL 예시:**
- https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/116-DB-ACCESS-REPORT.md
- https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/R3-API-005-report.md
- https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/R3-FRONT-004-report.md

**Blob URL 예시:**
- https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/reports/116-DB-ACCESS-REPORT.md
- https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/reports/R3-API-005-report.md
- https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/reports/R3-FRONT-004-report.md

---

## 4. 로컬 ↔ Public 매핑

| 로컬 (원본) | Public (project-docs) |
|-------------|------------------------|
| server116/docs/reports/116-DB-ACCESS-REPORT.md | newtalk-v2-api/reports/116-DB-ACCESS-REPORT.md |
| newtalk-v2/docs/reports/DOCS-ARCH-001-FIX-보고.md | newtalk-v2-api/reports/DOCS-ARCH-001-FIX-보고.md |
| newtalk-v2/docs/reports/DOCS-ARCH-001-보완-요약.md | newtalk-v2-api/reports/DOCS-ARCH-001-보완-요약.md |
| newtalk-v2/docs/reports/DOCS-FIX-007-요약.md | newtalk-v2-api/reports/DOCS-FIX-007-요약.md |
| newtalk-v2/docs/reports/PUSH-VERIFY-001-요약.md | newtalk-v2-api/reports/PUSH-VERIFY-001-요약.md |
| newtalk-v2/docs/reports/R3-API-005-report.md | newtalk-v2-api/reports/R3-API-005-report.md |
| newtalk-v2/docs/reports/R3-FRONT-004-report.md | newtalk-v2-api/reports/R3-FRONT-004-report.md |

---

이후에도 로컬에만 있는 보고서가 생기면 위와 동일하게  
`project-docs-repo/newtalk-v2-api/reports/` 로 복사 후 add → commit → push 하면 됩니다.
