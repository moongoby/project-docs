# CUR-GO100-DOCS-NAMING-RULE-001 보고서

**작업일시**: 2026-02-24 KST
**서버**: root@211.188.51.113
**작업자**: Cursor (Claude PM 지시)

## 1. 작업 내용
문서 명명규칙 수립 및 문서화, 각 프로젝트 rules 폴더에 배치

## 2. 생성된 파일

| 파일 | 경로 | 역할 |
|------|------|------|
| DOCUMENT-NAMING-CONVENTION.md | repo 루트 | 마스터 규칙 |
| DOCUMENT-RULES.md | go100/rules/ | GO100용 요약 |
| DOCUMENT-RULES.md | kis-autotrade-v4/rules/ | V4.1용 요약 |
| CURSORRULES.md | go100/ | 커서 규칙 포인터 (갱신) |

## 3. 수정된 파일

| 파일 | 변경 내용 |
|------|-----------|
| go100/rules/go100-rules.md | 문서 저장 규칙 섹션 추가 |

## 4. 핵심 규칙 요약
- 보고서 형식: CUR-{GO100|V41}-{TASK}-{SEQ}-{YYYYMMDD}.md
- GO100 보고서 → go100/reports/
- V4.1 보고서 → kis-autotrade-v4/reports/
- 교차 저장 금지
- 커서 지시 시 저장 경로·파일명 반드시 명시

## 5. 코드/DB 변경
없음

## 6. 확인 URL
- https://raw.githubusercontent.com/moongoby/project-docs/master/DOCUMENT-NAMING-CONVENTION.md → 200
- https://raw.githubusercontent.com/moongoby/project-docs/master/go100/rules/DOCUMENT-RULES.md → 200
- https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/DOCUMENT-RULES.md → 200
