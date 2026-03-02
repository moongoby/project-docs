# R0-TASK-001-FIX 진단 보고서 — GitHub SSH 키 문제

**문서번호**: NT-V2-R0-TASK-001-FIX  
**작성일**: 2026-02-21  
**대상**: Cursor AI (진단만 수행, 해결은 대표님 확인 후 지시)

---

## 1. 작업 요약

| 항목 | 결과 |
|------|------|
| 목표 | GitHub SSH 푸시 실패(Permission denied publickey) 원인 파악 |
| 진단 범위 | 3-1 ~ 3-8 전 항목 실행 및 결과 수집 |
| 결론 | **원인 파악됨** — Git/SSH 설정 문제(키 선택 오류). 해결 방안 제시 후, 실행은 보류. |

---

## 2. 진단 결과 (3-1 ~ 3-8)

### 3-1. Cursor 규칙 파일 확인

- `/srv/newtalk-v2/.cursorrules` → **파일 없음**
- `/srv/newtalk-v2/.cursor/rules` → **없음**
- `/srv/newtalk-v2/.cursor/` → **디렉터리 없음**
- `/srv/newtalk-v2/.cursorrc` → **없음**

**해석**: 서버 프로젝트 내 Cursor 관련 설정 없음. SSH/Git 문제와 무관.

---

### 3-2. 서버 전역 SSH 키 목록 및 config

**`ls -la ~/.ssh/`**

```
total 2072
drwx------  2 root root    4096 Feb 12 13:10 .
drwx------  27 root root 2068480 Feb 21 16:40 ..
-rw-------  1 root root     431 Feb  9 20:45 authorized_keys
-rw-------  1 root root     206 Feb 21 09:24 config
-rw-------  1 root config.backup_20260212_ssh설정
-rw-------  1 root root     432 Jan 30 08:51 id_ed25519_newtalk
-rw-r--r--  1 root root     113 Jan 30 08:51 id_ed25519_newtalk.pub
-rw-------  1 root root    3389 Jan 28 11:23 id_rsa
-rw-------  1 root root    3381 Jan 27 18:48 id_rsa_116
-rw-r--r--  1 root root     743 Jan 27 18:48 id_rsa_116.pub
-rw-r--r--  1 root root     752 Jan 28 11:23 id_rsa.pub
-rw-r--r--  1 root root    4844 Feb  2 20:26 known_hosts
```

**`~/.ssh/config`**

```
Host server114
  HostName [SERVER-IP]
  Port 7916
  User root
  IdentityFile /root/.ssh/id_ed25519_newtalk
  StrictHostKeyChecking no
  ConnectTimeout 30
  ServerAliveInterval 60
  ServerAliveCountMax 3
```

**해석**: `config`에는 `server114`(이 서버로 들어올 때 사용할 키)만 있고, **github.com**용 Host/IdentityFile 설정이 없음. 따라서 `git@github.com` 접속 시 기본 키 탐색 순서에만 의존함.

---

### 3-3. GitHub 등록 키 확인 (서버 공개키 전체)

| 파일 | 내용 |
|------|------|
| `id_rsa.pub` | `ssh-rsa AAAAB3NzaC1yc2E... root@[SERVER-HOSTNAME]` |
| `id_ed25519.pub` | **(없음)** — 서버에 id_ed25519 키 쌍 없음 |
| `id_ed25519_newtalk.pub` | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEIeydSrq946EEiWrGqgW7ciVZKi2Pi1GUm6om0e6OOU newtalk-go100-infra@genspark.ai` |
| `id_rsa_116.pub` | `ssh-rsa AAAAB3NzaC1yc2E... [SERVER-ID]_to_116` |

**해석**: 뉴톡 V2 / GitHub용으로 추정되는 키는 **id_ed25519_newtalk** (newtalk-go100-infra@genspark.ai). 대표님 확인으로 GitHub에는 이 키가 등록되어 있다고 가정.

---

### 3-4. GitHub SSH 연결 테스트

```text
git@github.com: Permission denied (publickey).
```

**해석**: 서버에서 `ssh -T git@github.com` 시 **공개키 인증 실패** 확인.

---

### 3-5. 어떤 키로 시도하는지 (ssh -vT)

```text
debug1: identity file /root/.ssh/id_rsa type 0
debug1: identity file /root/.ssh/id_ed25519 type -1
...
debug1: Offering public key: /root/.ssh/id_rsa RSA SHA256:PxMWi+cpWrfUpUKwsEfg9jqlCT7WEwwKX0HWk3InKqM
debug1: Authentications that can continue: publickey
debug1: Trying private key: /root/.ssh/id_dsa
debug1: Trying private key: /root/.ssh/id_ecdsa
debug1: Trying private key: /root/.ssh/id_ed25519
...
```

**해석 (원인)**  
- SSH 기본 순서대로 **id_rsa**만 먼저 제시(Offering)하고, GitHub이 이를 거부함.  
- 그 다음 **id_ed25519**를 시도하지만, 서버에는 `id_ed25519` 키 쌍이 없음(type -1).  
- **id_ed25519_newtalk**는 기본 탐색 목록에 없어서 **한 번도 시도되지 않음**.  
→ **GitHub에 등록된 키(id_ed25519_newtalk)를 쓰도록 하려면, github.com 전용으로 IdentityFile을 지정해야 함.**

---

### 3-6. Git remote 설정

```text
origin  git@github.com:newtalk-admin/newtalk-v2-api.git (fetch)
origin  git@github.com:newtalk-admin/newtalk-v2-api.git (push)
```

**해석**: origin이 `git@github.com:newtalk-admin/newtalk-v2-api.git`로 정상 설정됨.

---

### 3-7. Git 전역/로컬 설정

**전역 (`git config --global --list`)**

- credential.helper=store  
- user.name=moongoby-GO100  
- user.email=genspark_dev@genspark.ai  
- safe.directory=/home/danharoo/www (중복 2건)

**로컬 (`/srv/newtalk-v2`, `git config --local --list`)**

- core.repositoryformatversion=0, filemode=true, bare=false, logallrefupdates=true  
- remote.origin.url=git@github.com:newtalk-admin/newtalk-v2-api.git  
- remote.origin.fetch=+refs/heads/*:refs/remotes/origin/*  

**해석**: SSH 키 선택과 직접 관련된 Git 설정 없음. SSH 쪽 config에서 키 지정이 필요함.

---

### 3-8. R0-TASK-001 보고서 언급 Git 훅/alias

**`~/.gitconfig`**

```ini
[credential]
	helper = store
[user]
	name = moongoby-GO100
	email = genspark_dev@genspark.ai
[safe]
	directory = /home/danharoo/www
	directory = /home/danharoo/www
	directory = /home/danharoo/www
```

**`/srv/newtalk-v2/.git/hooks/`**  
- 샘플 훅만 존재(applypatch-msg.sample, commit-msg.sample 등). 활성 훅(확장자 없는 실행 훅) 없음.

**`/srv/newtalk-v2/.git/config`**

```ini
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[remote "origin"]
	url = git@github.com:newtalk-admin/newtalk-v2-api.git
	fetch = +refs/heads/*:refs/remotes/origin/*
```

**해석**: commit 시 "unknown option trailer" 등 훅/alias 문제와는 무관. 현재 푸시 실패 원인은 SSH 키 선택 문제로 한정 가능.

---

## 3. 원인 정리

| 구분 | 내용 |
|------|------|
| 직접 원인 | `git push` 시 `ssh git@github.com`이 **id_rsa**만 제시하고, GitHub에 등록된 **id_ed25519_newtalk**는 시도하지 않음. |
| 구조적 원인 | `~/.ssh/config`에 **github.com**용 Host가 없어, SSH가 기본 키 탐색 순서(id_rsa → id_ed25519 등)만 사용함. 서버에는 id_ed25519가 없고, id_ed25519_newtalk는 목록에 없음. |

---

## 4. 해결 방안 (실행 보류)

**방안**: 서버 `~/.ssh/config`에 **github.com** 전용 블록 추가.

1. 변경 전 백업  
   - `cp ~/.ssh/config ~/.ssh/config.bak.20260221_HHMMSS`

2. 다음 블록을 **기존 config 맨 앞 또는 Host server114 블록 위**에 추가  
   (기존 `Host server114` 블록은 그대로 유지)

```text
Host github.com
  HostName github.com
  User git
  IdentityFile /root/.ssh/id_ed25519_newtalk
  IdentitiesOnly yes
```

3. 확인  
   - `ssh -T git@github.com` → "Hi <username>!" 출력 확인  
   - `cd /srv/newtalk-v2 && git push origin <branch>` 로 푸시 재시도  

**실행**: 위 조치는 **대표님 확인 후 지시**에 따라 진행할 것. 본 문서는 진단 및 방안 제시까지만 수행함.

---

## 5. 참고

- 진단 실행 일시: 2026-02-21  
- 진단 실행 위치: 서버 [SERVER-IP] (port 7916, root, id_ed25519_newtalk로 접속)  
- 보고서 경로(로컬): `newtalk-v2/docs/reports/R0-TASK-001-FIX-report.md`  
- 서버 동일 보고서 경로: `/srv/newtalk-v2/docs/reports/R0-TASK-001-FIX-report.md` (배포 시 동일 내용 반영 권장)

---

**끝.**
