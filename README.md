# 프로젝트 문서 허브
관리자: moongoby | 최종 갱신: 2026-02-23

## 등록 프로젝트
| 프로젝트 | 설명 | 서버 | CONTEXT | Cursor Rules |
|----------|------|------|---------|--------------|
| shortflow | ShortFlow v3.0 + StyleFlow v1.0 | 114서버 | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/cursorrules.md) |
| go100 | GO100 자동매매 | kis-autotrade-v4 | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/cursorrules.md) |
| nas-image | NAS 이미지 자동화 | Synology NAS | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/cursorrules.md) |
| newtalk-v2-api | NewTalk V2 SNS형 B2B SaaS 마켓플레이스 | 114서버 | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/cursorrules.md) |

## 공통 문서 (common/)
| 문서 | 용도 | URL |
|------|------|-----|
| CONTEXT 템플릿 | 새 프로젝트 CONTEXT 작성 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/CONTEXT_TEMPLATE.md) |
| Cursor Rules 템플릿 | 새 프로젝트 .cursorrules 작성 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/CURSORRULES_TEMPLATE.md) |
| 인계서 템플릿 | 대화 종료 시 인계서 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/HANDOVER_TEMPLATE.md) |
| 보고서 템플릿 | 작업 완료 보고서 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/REPORT_TEMPLATE.md) |
| Git 규칙 | 커밋/브랜치 규칙 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/GIT_CONVENTION.md) |
| 보안 규칙 | .env, 키, 코드 관리 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/SECURITY_RULES.md) |
| 동기화 가이드 | 서버→GitHub 동기화 방법 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/SYNC_GUIDE.md) |

## Claude 새 대화 시작법
아래 온보딩 문서를 읽고 작업을 이어가줘:
https://raw.githubusercontent.com/moongoby/project-docs/master/ONBOARDING.md
프로젝트: [프로젝트명], 폴더: [폴더명]

프로젝트별 CONTEXT raw URL (첫 메시지로 전달 가능):
- NewTalk V2: https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md

## 신규 프로젝트 추가 (114 서버)
```bash
bash /data/project-docs/scripts/new_project.sh [폴더명] '[설명]'
```

## 규칙
- 코드, .env, credentials, API키 절대 포함 금지
- 기획서, 아키텍처, CONTEXT, 인계서, cursorrules, 보고서만 관리
- cursorrules.md는 검토용 사본 (원본은 각 프로젝트 .cursorrules)
