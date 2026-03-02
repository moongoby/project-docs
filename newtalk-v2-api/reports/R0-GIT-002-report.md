# R0-GIT-002 완료 보고서
# remote URL 변경 + 전체 푸시

**문서번호:** NT-V2-R0-GIT-002  
**작성일:** 2026-02-21  
**대상:** Cursor AI

---

## 1. 작업 개요
- **목적:** GitHub remote URL을 `newtalk-admin/newtalk-v2-api` → `moongoby/newtalk-v2-api`로 변경하고, main / develop / feature 브랜치 푸시.
- **실행:** 서버 `[SERVER-IP]`에 SSH 접속 후 `/srv/newtalk-v2`에서 직접 실행.

---

## 2. 실행 결과

### 2.1 remote URL 변경
- **명령:** `git remote set-url origin git@github.com:moongoby/newtalk-v2-api.git`  
- **결과:** 성공.

**변경 전 `git remote -v`:**
```
origin	git@github.com:newtalk-admin/newtalk-v2-api.git (fetch)
origin	git@github.com:newtalk-admin/newtalk-v2-api.git (push)
```

**변경 후 `git remote -v`:**
```
origin	git@github.com:moongoby/newtalk-v2-api.git (fetch)
origin	git@github.com:moongoby/newtalk-v2-api.git (push)
```

### 2.2 전체 브랜치 푸시
- **명령:** `git checkout main` → `git push -u origin main` (동일하게 develop, feature/R0-TASK-002-db-design)
- **결과:** **실패** — 세 브랜치 모두 동일 오류.

**오류 메시지:**
```
ERROR: Repository not found.
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

**사유:**  
- `git@github.com:moongoby/newtalk-v2-api` 저장소가 아직 없거나,  
- 서버 SSH 키(`~/.ssh/id_ed25519_newtalk`)가 해당 저장소에 등록되지 않았을 가능성.

**조치 권장:**  
1. GitHub에 `moongoby/newtalk-v2-api` 저장소 생성 후 푸시 재실행.  
2. 또는 기존 저장소가 있다면 해당 계정/조직에 서버 SSH 공개키를 Deploy key 또는 계정 SSH key로 등록 후 재푸시.

### 2.3 확인 명령
**`git branch -a`:**
```
  develop
* feature/R0-TASK-002-db-design
  main
```

**`git log --oneline -5`:**
```
eba1420 [R0-002] chore: .cursorrules DB 접속 방법 업데이트 (V1 경로 확정)
13bb5e0 [R0-002] feat: V1 실측 스키마 추출 완료 + 문서 보강
32d542d [R0-001] chore: Cursor 프로젝트 규칙 파일 생성
dbcf221 R0-001 docs: GitHub 푸시 SSH 이슈 보고서 반영
2975c0f R0-001 docs: 작업 완료 보고서 및 gitignore 보완
```

### 2.4 .cursorrules 저장소명 업데이트
- **명령:** `sed -i 's|newtalk-admin/newtalk-v2-api|moongoby/newtalk-v2-api|g' /srv/newtalk-v2/.cursorrules`
- **결과:** 성공. 섹션 7 저장소명이 `moongoby/newtalk-v2-api`로 변경됨.

**확인:** `grep "moongoby" /srv/newtalk-v2/.cursorrules`  
→ `85:# - 저장소: GitHub moongoby/newtalk-v2-api`

### 2.5 .cursorrules 커밋 (서버)
- **명령:** `git add .cursorrules` 후 `env -i HOME="$HOME" PATH="/usr/bin:/bin" git commit -m "[R0-002] chore: GitHub remote URL moongoby/newtalk-v2-api로 변경"`
- **결과:** 커밋 성공. `1 file changed, 1 insertion(+), 1 deletion(-)` — 커밋 해시 `85b8eb9`.
- **푸시:** 원격 저장소 미존재/권한 이슈로 `git push origin feature/R0-TASK-002-db-design` 실행 불가. 저장소 생성·권한 해결 후 동일 명령으로 푸시 필요.

---

## 3. 요약
| 항목 | 결과 |
|------|------|
| remote URL 변경 | ✅ 완료 (moongoby/newtalk-v2-api) |
| main 푸시 | ❌ Repository not found |
| develop 푸시 | ❌ Repository not found |
| feature/R0-TASK-002-db-design 푸시 | ❌ Repository not found |
| .cursorrules 업데이트 | ✅ 완료 |
| .cursorrules 커밋 | ✅ 완료 (85b8eb9) |

---

## 4. 결론
- remote URL 변경 및 .cursorrules 반영·커밋까지 서버에서 정상 수행됨.
- 푸시는 `moongoby/newtalk-v2-api` 저장소 생성 및 서버 SSH 키 권한 확보 후, 아래 명령으로 재실행 필요.

```bash
cd /srv/newtalk-v2
git checkout main && git push -u origin main
git checkout develop && git push -u origin develop
git checkout feature/R0-TASK-002-db-design && git push -u origin feature/R0-TASK-002-db-design
```
