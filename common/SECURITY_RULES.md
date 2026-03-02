# 보안 규칙
> 모든 프로젝트 공통 적용

## 절대 금지 항목 (Public 저장소)
- .env 파일
- API 키 / Secret Key
- DB 비밀번호
- OAuth credentials (client_secret.json 등)
- SSH 개인키
- 토큰 (GitHub PAT, YouTube OAuth token 등)
- 소스 코드 (Private 저장소에서만 관리)

## .env 관리
- 각 서버의 프로젝트 루트에 .env 파일로 관리
- .gitignore에 반드시 .env 포함
- 예시 파일(.env.example)은 값 없이 키만 기록하여 git 등록 가능

## SSH 키 관리
- moongoby 계정 등록 키 목록:
  - newtalk (114서버)
  - GitHub CLI (114서버)
  - GO100-server (GO100 서버)
- 키 추가/삭제 시 https://github.com/settings/keys 에서 관리

## Public 저장소(project-docs) 등록 전 체크리스트
- [ ] .env, credentials 포함 여부 확인
- [ ] API 키/토큰 하드코딩 여부 확인
- [ ] 소스 코드 포함 여부 확인
- [ ] 개인정보 포함 여부 확인
- [ ] `git diff --cached` 로 커밋 내용 최종 확인

## IP·호스트 마스킹 규칙 (문서 발행 시)
- 내부 IP·호스트는 Public 저장소에 그대로 기재하지 않는다.
- 예: `192.168.x.x` → `[NAS_HOST]`, `2222` → `[NAS_PORT]`, `admin@[NAS-IP]` → `[NAS_USER]@[NAS_HOST]`
- 동기화 가이드·스크립트 샘플에서는 플레이스홀더 사용 후 실제 값은 서버 로컬에서만 관리.
