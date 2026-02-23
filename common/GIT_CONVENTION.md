# Git 커밋/브랜치 규칙
> 모든 프로젝트 공통 적용

## 커밋 메시지 형식
[type] 간결한 설명 (한글 가능)


## type 목록
- **feat**: 새 기능
- **fix**: 버그 수정
- **docs**: 문서 변경
- **config**: 설정 변경 (.env, .cursorrules, docker 등)
- **refactor**: 리팩토링 (기능 변경 없음)
- **test**: 테스트 추가/수정
- **report**: 작업 보고서
- **sync**: 문서 동기화
- **context**: CONTEXT.md 갱신
- **handover**: 인계서 작성

## 브랜치 전략
- main/master: 운영 브랜치 (직접 push)
- feature/기능명: 대규모 기능 개발 시에만 분기

## 필수 .gitignore 항목
.env credentials/ pycache/ *.pyc node_modules/ .next/cache/ *.pack backups/ *.log


## push 규칙
- 모든 작업 완료 후 반드시 push
- 커밋 없이 퇴근/대화 종료 금지
