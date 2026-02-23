# 프로젝트 문서 허브
> 관리자: moongoby
> 최종 갱신: 2026-02-23

| 프로젝트 | 설명 | 서버 | CONTEXT | Cursor Rules |
|-----------|------|------|---------|--------------|
| [shortflow](./shortflow/) | ShortFlow v3.0 + StyleFlow v1.0 | 114서버 | [CONTEXT.md](./shortflow/CONTEXT.md) | [cursorrules.md](./shortflow/cursorrules.md) |
| [go100](./go100/) | GO100 자동매매 | kis-autotrade-v4 | [CONTEXT.md](./go100/CONTEXT.md) | [cursorrules.md](./go100/cursorrules.md) |

## Claude 새 대화 시작법
해당 프로젝트 CONTEXT.md raw URL을 첫 메시지로 전달:
- ShortFlow: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/CONTEXT.md
- GO100: https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md

## Claude에게 보고서 확인 요청
```
아래 보고서 확인하고 피드백해줘:
https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/파일명.md
```

## Claude에게 Cursor Rules 검토 요청
```
아래 cursorrules 검토하고 수정사항 알려줘:
https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/cursorrules.md
```

## 규칙
- 코드, .env, credentials, API키 절대 포함 금지
- 기획서, 아키텍처, CONTEXT, 인계서, cursorrules, 보고서만 관리
- cursorrules.md는 검토용 사본 (원본은 각 프로젝트 .cursorrules)
