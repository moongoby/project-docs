# 새 대화창 / 신규 프로젝트 온보딩

> 이 문서를 Claude 새 대화 첫 메시지에 URL로 전달하면 전체 맥락이 복원됩니다.

## GitHub 문서 허브
- Public 저장소: https://github.com/moongoby/project-docs
- 관리자: moongoby

## 등록된 프로젝트

| 프로젝트 | 서버 | 폴더 | CONTEXT | Cursor Rules |
|----------|------|------|---------|--------------|
| ShortFlow/StyleFlow | 114서버 rfree-0009 | shortflow/ | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/cursorrules.md) |
| GO100 자동매매 | kis-autotrade-v4 | go100/ | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/cursorrules.md) |
| KIS AutoTrade V4.1 | 211서버 | kis-autotrade-v4 | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md) |
| KIS AutoTrade V4.1 | 211서버 | kis-autotrade-v4 | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md) |
| NAS 이미지 자동화 | Synology NAS | nas-image/ | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/cursorrules.md) |

## 사용법

### 기존 프로젝트 대화 시작
아래 온보딩 문서를 읽고 작업을 이어가줘: https://raw.githubusercontent.com/moongoby/project-docs/master/ONBOARDING.md 프로젝트: [프로젝트명], 폴더: [폴더명]


### 신규 프로젝트 등록
아래 온보딩 문서를 읽고 신규 프로젝트를 등록해줘: https://raw.githubusercontent.com/moongoby/project-docs/master/ONBOARDING.md 프로젝트명: [이름], 서버: [서버정보], 폴더명: [영문폴더명]


### Claude에게 문서 검토 요청
아래 확인하고 피드백해줘: https://raw.githubusercontent.com/moongoby/project-docs/master/[폴더명]/CONTEXT.md


## 공통 템플릿 (common/)
- [CONTEXT 템플릿](https://raw.githubusercontent.com/moongoby/project-docs/master/common/CONTEXT_TEMPLATE.md)
- [Cursor Rules 템플릿](https://raw.githubusercontent.com/moongoby/project-docs/master/common/CURSORRULES_TEMPLATE.md)
- [인계서 템플릿](https://raw.githubusercontent.com/moongoby/project-docs/master/common/HANDOVER_TEMPLATE.md)
- [보고서 템플릿](https://raw.githubusercontent.com/moongoby/project-docs/master/common/REPORT_TEMPLATE.md)
- [Git 규칙](https://raw.githubusercontent.com/moongoby/project-docs/master/common/GIT_CONVENTION.md)
- [보안 규칙](https://raw.githubusercontent.com/moongoby/project-docs/master/common/SECURITY_RULES.md)
- [동기화 가이드](https://raw.githubusercontent.com/moongoby/project-docs/master/common/SYNC_GUIDE.md)

## 운영 규칙
- 작업 완료 → CONTEXT.md 갱신
- 대화 종료 → 인계서 작성
- 보고서 → project-docs/[폴더]/reports/에 발행
- .env, credentials, API키, 코드 → Public 저장소 포함 절대 금지
