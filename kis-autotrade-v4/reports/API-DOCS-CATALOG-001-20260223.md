# CUR-API-DOCS-CATALOG-001 보고서

## 기본 정보
- 작업일: 2026-02-23 17:00 KST
- 서버: root@[SERVER-IP]
- 작업 유형: 문서 전용 (코드/DB 변경 없음)

## 작업 내용
1. /root/kis-autotrade-v4/docs/api/ 폴더의 KIS 엑셀 8건, 키움 PDF 1건 현황 파악
2. 각 엑셀 시트명·내용 요약 확인 (openpyxl로 API 목록·TR_ID 등 추출)
3. project-docs에 API-DOCS-CATALOG.md 카탈로그 작성
4. 코드에서 실제 사용 중인 API tr_id/api-id 매핑 확인 (grep 기반)
5. CONTEXT.md에 카탈로그 링크 추가
6. docs/api/README.md 갱신 (kis-autotrade-v4 로컬)

## 산출물
| 파일 | 위치 |
|------|------|
| API-DOCS-CATALOG.md | /root/project-docs/kis-autotrade-v4/docs/API-DOCS-CATALOG.md |
| README.md | /root/kis-autotrade-v4/docs/api/README.md |
| CONTEXT.md (수정) | /root/project-docs/kis-autotrade-v4/CONTEXT.md |
| 본 보고서 | /root/project-docs/kis-autotrade-v4/reports/API-DOCS-CATALOG-001-20260223.md |

## GitHub URL
- 카탈로그: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/docs/API-DOCS-CATALOG.md
- 보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/API-DOCS-CATALOG-001-20260223.md

## DB 무결성 (변경 없음)
- strategy_cards: 변경 없음
- v4_positions: 변경 없음
