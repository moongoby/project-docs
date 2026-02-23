# CUR-DOCS-RULE-UPDATE-001 보고서

## 기본 정보
- 작업일: 2026-02-23 16:50 KST
- 서버: root@211.188.51.113
- 작업 유형: 문서 전용 (코드/DB 변경 없음)

## 작업 내용
CEO 지시에 따라 "보고서 push 필수 절차" 규칙을 아래 2개 파일에 추가:
1. `.cursor/rules/CLAUDE.md` — 공통 규칙에 보고서 push 필수 절차 섹션 추가
2. `.cursor/rules/kis-v41-rules.md` — 작업 절차 8-10단계 추가

## 추가된 규칙 요약
- 모든 작업 보고서는 코드 레포 커밋과 별도로 project-docs에 push 필수
- push 안 되면 태스크 미완료 판정
- 지시서 마지막에 보고서 push 단계 필수 포함
- 코드 커밋 / 보고서 push 각각 독립 체크포인트
- push 실패 시 재시도 후 사용자 보고

## 변경 파일
| 파일 | 변경 내용 |
|------|----------|
| CLAUDE.md | "보고서 push 필수 절차" 섹션 추가 |
| kis-v41-rules.md | "보고서 push 필수 절차" 섹션 + 작업 절차 8-10단계 추가 |

## DB 무결성 (변경 없음 확인)
- strategy_cards: 변경 없음
- v4_positions: 변경 없음

## GitHub URL
- CLAUDE.md: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/rules/CLAUDE.md
- kis-v41-rules.md: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/rules/kis-v41-rules.md
- 본 보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/DOCS-RULE-UPDATE-001-20260223.md
