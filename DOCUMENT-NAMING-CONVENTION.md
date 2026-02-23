# project-docs 문서 명명 규칙
> 최종 갱신: 2026-02-24

## 1. 폴더 구조

```
project-docs/
├── go100/                         ← GO100 전용
│   ├── CONTEXT.md
│   ├── CURSORRULES.md
│   ├── docs/
│   ├── rules/
│   │   └── go100-rules.md
│   ├── reports/                   ← GO100 보고서만
│   └── review/
├── kis-autotrade-v4/              ← V4.1 전용
│   ├── CONTEXT.md
│   ├── docs/
│   ├── rules/
│   │   ├── kis-v41-rules.md
│   │   ├── CLAUDE.md              ← 공통
│   │   └── MARKET-HOURS-KR.md
│   ├── reports/                   ← V4.1 보고서만
│   └── review/
└── DOCUMENT-NAMING-CONVENTION.md  ← 이 파일
```

## 2. 보고서 파일명 규칙

**형식**: `CUR-{PROJECT}-{TASK_TYPE}-{SEQ}-{YYYYMMDD}.md`

| 항목 | 값 | 설명 |
|------|------|------|
| CUR | 고정 | Cursor 작업 식별자 |
| PROJECT | GO100 또는 V41 | 프로젝트 구분 |
| TASK_TYPE | FIX, HOTFIX, DIAG, VERIFY, AUDIT, RESEARCH, E2E, MIGRATE, DOC 등 | 작업 유형 |
| SEQ | 001~999 | 동일 작업의 일련번호 |
| YYYYMMDD | 20260223 | 작업일 (KST) |

**예시**:
- `CUR-GO100-CHATWIDGET-FIX-004-20260223.md` → `go100/reports/`
- `CUR-V41-ARCHITECTURE-SCAN-001-20260223.md` → `kis-autotrade-v4/reports/`

## 3. 저장 규칙

| 보고서 프로젝트 | 저장 위치 |
|----------------|-----------|
| CUR-GO100-* | `go100/reports/` |
| CUR-V41-* | `kis-autotrade-v4/reports/` |

**교차 저장 금지**: GO100 보고서를 V4.1 폴더에 저장하거나 그 반대를 하지 않는다.

## 4. 인계서 규칙

| 문서 | 파일명 | 위치 |
|------|--------|------|
| GO100 인계서 | HANDOVER-YYYYMMDD.md | go100/ |
| V4.1 인계서 | HANDOVER-YYYYMMDD.md | kis-autotrade-v4/ |

## 5. 커서 지시 시 필수 포함 사항

모든 커서 지시서에 아래를 반드시 명시:
1. 보고서 저장 경로 (절대 경로)
2. 보고서 파일명 (명명 규칙 준수)
3. GitHub push 후 URL 확인 명령
