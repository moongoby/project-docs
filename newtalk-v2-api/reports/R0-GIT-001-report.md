# R0-GIT-001 보고서: GitHub 저장소 생성 + 전체 푸시

**문서번호:** NT-V2-R0-GIT-001  
**작성일:** 2026-02-21  
**대상:** 뉴톡 V2 (newtalk-admin/newtalk-v2-api)

---

## 1. 작업 요약

- **목표:** gh CLI 인증 → private 저장소 생성 → main/develop/feature/R0-TASK-002-db-design 푸시
- **결과:** gh 미인증·저장소 미생성 상태로, 푸시까지 에이전트에서 완료하지 못함. 아래는 실제 실행 결과와 미실행 사유.

---

## 2. 실제 실행 결과

### 2-1. gh auth status (서버에서 실행)

```
You are not logged into any GitHub hosts. To log in, run: gh auth login
```

→ 서버에서 gh CLI 로그인 상태 아님.

### 2-2. gh auth login

- **시도:** 서버에서 `BROWSER=false timeout 25 gh auth login -p ssh -h github.com --skip-ssh-key` 실행.
- **결과:** 디바이스 코드 출력 후 타임아웃으로 종료. 코드 예: `D45B-3FBA`, URL: https://github.com/login/device  
- **미완료 사유:** 디바이스 코드 방식은 사용자가 브라우저에서 코드 입력 후 승인해야 하며, 그 전에 프로세스가 종료되어 서버에 로그인 상태가 저장되지 않음.  
- **결론:** **서버 터미널에서 직접** 아래 중 하나 필요:
  - `gh auth login -p ssh -h github.com` (대화형, SSH 선택)
  - 또는 `BROWSER=false gh auth login -p ssh -h github.com --skip-ssh-key` 실행 후 출력된 코드로 https://github.com/login/device 에서 인증

### 2-3. gh repo create

- **미실행.**  
- **사유:** gh 로그인 선행 필요. 로그인 후 아래 명령으로 생성 가능.

```bash
gh repo create newtalk-admin/newtalk-v2-api \
  --private \
  --description "뉴톡 V2 백엔드 API (Laravel 12)"
```

### 2-4. 저장소 접근 확인 (git ls-remote)

서버 `/srv/newtalk-v2`에서 origin 접근 시도:

```
ERROR: Repository not found.
fatal: Could not read from remote repository.
```

→ 저장소가 아직 없거나 해당 계정/키로 접근 불가. **gh repo create 선행 필요.**

### 2-5. git push

- **미실행.**  
- **사유:** origin 저장소 미생성.  
- **서버 Git 상태:** remote `origin` = `git@github.com:newtalk-admin/newtalk-v2-api.git`, 브랜치 `main`, `develop`, `feature/R0-TASK-002-db-design` 존재.

### 2-6. git branch -a (서버 /srv/newtalk-v2)

```
  develop
* feature/R0-TASK-002-db-design
  main
```

(remote 추적 브랜치 없음 — origin 푸시 전)

### 2-7. 서버 환경 확인

- **gh:** `/usr/bin/gh`, version 2.87.2
- **SSH 키:** `/root/.ssh/id_ed25519_newtalk` 존재 (GitHub 푸시용으로 사용 가능한지 계정 설정에 따름)

---

## 3. 인증 완료 후 서버에서 실행할 명령

서버에 SSH 접속한 뒤, **gh 로그인을 완료한 같은 셸**에서 아래를 순서대로 실행.

```bash
# 1) 저장소 생성
gh repo create newtalk-admin/newtalk-v2-api \
  --private \
  --description "뉴톡 V2 백엔드 API (Laravel 12)"

# 2) 생성 확인
gh repo view newtalk-admin/newtalk-v2-api

# 3) 푸시
cd /srv/newtalk-v2
git push -u origin main
git push -u origin develop
git push -u origin feature/R0-TASK-002-db-design

# 4) 푸시 확인
git branch -a
git log --oneline -5
```

실행 후 `gh auth status`, `gh repo view`, `git branch -a`, `git log --oneline -5` 출력을 이 보고서에 추가하면 완료 검증이 가능함.

---

## 4. 오류·특이 사항

- 디바이스 코드 로그인은 사용자 브라우저 입력이 필요해, 비대화형 SSH 단일 명령으로는 “로그인 완료”까지 불가.
- `.cursorrules` 준수: 서버에서 직접 명령 실행 시도함. 실행 불가 항목은 사유만 명시함.

---

**끝.**
