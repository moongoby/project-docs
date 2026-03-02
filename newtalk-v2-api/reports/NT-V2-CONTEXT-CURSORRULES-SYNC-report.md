# CONTEXT·cursorrules 보강 및 동기화 보고서

| 항목 | 내용 |
|------|------|
| 작업일 | 2026-02-23 |
| 대상 | .cursorrules, docs/CONTEXT.md, project-docs 동기화 |

## 1. 수행 내용

### 1.1 .cursorrules 수정 (완료)

- **7번 Git 커밋 규칙**
  - `저장소: GitHub newtalk-admin/newtalk-v2-api`  
  - → `저장소: GitHub moongoby/newtalk-v2-api-` (끝 하이픈 유지)
- **12~15번 섹션 추가** (기존 11번 뒤에 추가)
  - 12. 작업 완료 후 문서 동기화 (필수)
  - 13. project-docs 보안 (Public 저장소)
  - 14. Frontend 빌드 규칙
  - 15. 대화 인계 규칙

### 1.2 CONTEXT.md 보강 (완료)

- 워크스페이스에는 기존 `docs/CONTEXT.md`가 없어 **새 파일 생성**
- 아래 섹션 포함:
  - V2 핵심 기능 4가지
  - 8레이어 아키텍처
  - 수익 모델
  - 완료 항목 / 진행 중 / 다음 작업
  - 로드맵 (R2~R4)

**참고:** 서버(`/srv/newtalk-v2/docs/CONTEXT.md`)에 이미 프로젝트 개요·서버 정보·기술스택 등이 있는 경우, 해당 파일 **끝**에 이번에 추가한 섹션(V2 핵심 기능 4가지 ~ 로드맵)만 이어 붙이면 됩니다.

## 2. 서버에서 실행할 동기화 (수동)

아래는 **서버([SERVER-IP], 작업 디렉토리 `/srv/newtalk-v2`)** 에서 실행해야 합니다.

### 2.1 private 저장소 반영

```bash
cd /srv/newtalk-v2
git add .cursorrules docs/CONTEXT.md docs/reports/NT-V2-CONTEXT-CURSORRULES-SYNC-report.md
git status   # 확인 후
git commit -m "[DOCS] cursorrules 12~15번 추가·7번 저장소명 수정, CONTEXT.md 기획 맥락 보강"
git push origin main   # 또는 develop 등 사용 브랜치
```

### 2.2 project-docs 동기화 (cursorrules)

```bash
cp /srv/newtalk-v2/.cursorrules /data/project-docs/newtalk-v2-api/cursorrules.md
cd /data/project-docs && git add -A && git commit -m "[sync] newtalk-v2-api cursorrules 업데이트" && GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin master
```

### 2.3 project-docs 전체 동기화 (스크립트 사용 시)

```bash
bash /data/project-docs/scripts/sync_newtalk_v2_api.sh
```

- CONTEXT.md, cursorrules.md, reports 등이 한 번에 복사·커밋·푸시됩니다.
- 스크립트 없거나 실패 시: 2.2에서 한 것처럼 `cp`로 `CONTEXT.md`, `cursorrules.md`, `reports/*.md`를 `/data/project-docs/newtalk-v2-api/`로 수동 복사 후 `git add` → `commit` → `push`.

## 3. 요약

| 항목 | 상태 |
|------|------|
| .cursorrules 7번 저장소명 수정 | 완료 (moongoby/newtalk-v2-api-) |
| .cursorrules 12~15번 추가 | 완료 |
| docs/CONTEXT.md 기획 맥락 보강 | 완료 (신규 생성) |
| project-docs 동기화 | 서버에서 위 2.2 또는 2.3 실행 필요 |

새 대화 시작 시:  
`https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md` 전달 시 프로젝트 전체 맥락 파악 가능합니다.
