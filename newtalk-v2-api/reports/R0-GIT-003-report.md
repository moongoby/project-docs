# R0-GIT-003 완료 보고서
# remote URL 수정 (하이픈 반영) + 푸시

**문서번호:** NT-V2-R0-GIT-003  
**작성일:** 2026-02-21  
**대상:** Cursor AI

---

## 1. 작업 개요
- **목적:** GitHub remote URL을 `newtalk-v2-api` → `newtalk-v2-api-`(하이픈 반영)로 수정하고, main / develop / feature 브랜치 푸시, .cursorrules 저장소명 업데이트 후 커밋·푸시.
- **실행:** 서버 `114.207.244.86`에 SSH 접속 후 `/srv/newtalk-v2`에서 직접 실행.

---

## 2. 실행 결과

### 2.1 remote URL 수정
- **명령:** `git remote set-url origin git@github.com:moongoby/newtalk-v2-api-.git`  
- **결과:** 성공.

**수정 후 `git remote -v`:**
```
origin	git@github.com:moongoby/newtalk-v2-api-.git (fetch)
origin	git@github.com:moongoby/newtalk-v2-api-.git (push)
```

### 2.2 전체 브랜치 푸시

**main**
```
Switched to branch 'main'
To github.com:moongoby/newtalk-v2-api-.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

**develop**
```
Switched to branch 'develop'
remote: 
remote: Create a pull request for 'develop' on GitHub by visiting:        
remote:      https://github.com/moongoby/newtalk-v2-api-/pull/new/develop        
remote: 
To github.com:moongoby/newtalk-v2-api-.git
 * [new branch]      develop -> develop
Branch 'develop' set up to track remote branch 'develop' from 'origin'.
```

**feature/R0-TASK-002-db-design**
```
Switched to branch 'feature/R0-TASK-002-db-design'
remote: 
remote: Create a pull request for 'feature/R0-TASK-002-db-design' on GitHub by visiting:        
remote:      https://github.com/moongoby/newtalk-v2-api-/pull/new/feature/R0-TASK-002-db-design        
remote: 
To github.com:moongoby/newtalk-v2-api-.git
 * [new branch]      feature/R0-TASK-002-db-design -> feature/R0-TASK-002-db-design
Branch 'feature/R0-TASK-002-db-design' set up to track remote branch 'feature/R0-TASK-002-db-design' from 'origin'.
```

### 2.3 확인: git branch -a
```
  develop
* feature/R0-TASK-002-db-design
  main
  remotes/origin/develop
  remotes/origin/feature/R0-TASK-002-db-design
  remotes/origin/main
```

### 2.4 확인: git log --oneline -5
```
85b8eb9 [R0-002] chore: GitHub remote URL moongoby/newtalk-v2-api로 변경
eba1420 [R0-002] chore: .cursorrules DB 접속 방법 업데이트 (V1 경로 확정)
13bb5e0 [R0-002] feat: V1 실측 스키마 추출 완료 + 문서 보강
32d542d [R0-001] chore: Cursor 프로젝트 규칙 파일 생성
dbcf221 R0-001 docs: GitHub 푸시 SSH 이슈 보고서 반영
```

### 2.5 .cursorrules 저장소명 업데이트
- **명령:** `sed -i 's|moongoby/newtalk-v2-api|moongoby/newtalk-v2-api-|g'` 및 `newtalk-admin/newtalk-v2-api` → `moongoby/newtalk-v2-api-` 반영.
- **확인:** `grep "moongoby" /srv/newtalk-v2/.cursorrules`  
  → `# - 저장소: GitHub moongoby/newtalk-v2-api-`

### 2.6 .cursorrules 커밋 및 푸시
```
[feature/R0-TASK-002-db-design df1f063] [R0-002] fix: GitHub remote URL newtalk-v2-api- 하이픈 수정
 1 file changed, 1 insertion(+), 1 deletion(-)
To github.com:moongoby/newtalk-v2-api-.git
   85b8eb9..df1f063  feature/R0-TASK-002-db-design -> feature/R0-TASK-002-db-design
```

---

## 3. 결론
- remote URL `newtalk-v2-api-` 반영 완료.
- main, develop, feature/R0-TASK-002-db-design 푸시 완료.
- .cursorrules 저장소명 수정 후 커밋·푸시 완료.
