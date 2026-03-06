# INFRA-PERM-001 실행 보고서

**Task ID**: T-014
**제목**: claudebot SSH키·Docker 권한 부여 및 미push 커밋 일괄 동기화
**서버**: 114 (newtalk-v2-api)
**실행일시**: 2026-03-05 KST
**실행자**: Claude Bot (claudebot 계정)
**우선순위**: P0-CRITICAL

---

## 요약

claudebot 계정은 /root/.ssh/id_ed25519_newtalk SSH 키에 접근 불가 (Permission denied) 상태이며 docker 그룹 미포함으로, root 권한이 필요한 Steps 1–3은 실행 불가. project-docs 보고서 복사(Step 4 Part 2)만 로컬 커밋 완료. **git push는 SSH 키 접근 불가로 실패.**

---

## Step 1 — SSH 키 백업

**명령어**:
```bash
cp /root/.ssh/id_ed25519_newtalk /root/.ssh/id_ed25519_newtalk.bak.$(date +%Y%m%d_%H%M%S)
```

**결과**:
```
cp: failed to access '/root/.ssh/id_ed25519_newtalk.bak.20260305_193712': Permission denied
```

**원인**: claudebot 계정은 /root/.ssh/ 디렉토리 접근 권한 없음 (root 소유)

---

## Step 2 — claudebot SSH 키 읽기 권한 부여

**명령어**:
```bash
chown root:claudebot /root/.ssh/id_ed25519_newtalk
chmod 640 /root/.ssh/id_ed25519_newtalk
```

**결과**: **미실행** — root 권한 필요. claudebot 계정으로는 실행 불가.

**현재 상태 (실행 전)**:
```
ls: cannot access '/root/.ssh/id_ed25519_newtalk': Permission denied
```
claudebot이 /root/.ssh/ 디렉토리 자체를 조회할 수 없어 변경 전 파일 권한 확인 불가.

---

## Step 3 — claudebot docker 그룹 추가

**명령어**:
```bash
usermod -aG docker claudebot
```

**결과**: **미실행** — root 권한 필요.

**현재 claudebot groups**:
```
claudebot : claudebot
```
(docker 그룹 미포함 확인)

---

## Step 4 — 미push 커밋 일괄 동기화

### newtalk-v2 repo (6 commits ahead)

**밀린 커밋 목록**:
```
b13ae13 [NTV2] API-SMOKE-002 — 시드 데이터 기반 API 기능 테스트 완료
88c6861 [NTV2] DOCS-SYNC-003 — HANDOVER v5.0 + CEO-DIRECTIVES v1.1 정합성 복구
012bc9c [NTV2] FRONTEND-AUDIT-001 — 프론트엔드 B2/B3 API 연동 감사
da42612 [NTV2] SEEDER-001 완료 — 시더 14개, HANDOVER v4.9.0
4a51a2f [NTV2] SEEDER-001 완료 — 시더 8개, HANDOVER v4.9.0
d89640e [NTV2] SEEDER-001-A — 핵심 시더 Part 1 (users+products+orders)
```

**git push 시도**:
```
GIT_SSH_COMMAND="ssh -i /root/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin main
```

**결과**:
```
Warning: Identity file /root/.ssh/id_ed25519_newtalk not accessible: Permission denied.
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**상태**: **실패** — SSH 키 접근 불가

### project-docs repo

**git pull**:
```
error: cannot open .git/FETCH_HEAD: Permission denied
```
(pull 실패, 로컬 브랜치에서 직접 진행)

**보고서 복사**:
```
cp /srv/newtalk-v2/docs/reports/FRONTEND-AUDIT-001-report.md newtalk-v2-api/reports/
→ 결과: 0 (성공, 이미 존재하는 파일 덮어쓰기)

cp /srv/newtalk-v2/docs/reports/API-SMOKE-002-report.md newtalk-v2-api/reports/
→ 결과: 0 (성공, 신규 파일 추가)
```

**git add & diff**:
```
 newtalk-v2-api/reports/API-SMOKE-002-report.md | 173 +++++++++++++++++++++++++
 1 file changed, 173 insertions(+)
```

**로컬 커밋 (성공)**:
```
[master ec14551] [NTV2] INFRA-PERM-001 — 누락 보고서 일괄 동기화 (FRONTEND-AUDIT-001, API-SMOKE-002)
 1 file changed, 173 insertions(+)
 create mode 100644 newtalk-v2-api/reports/API-SMOKE-002-report.md
```

**git push (project-docs)**:
```
Warning: Identity file /root/.ssh/id_ed25519_newtalk not accessible: Permission denied.
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**상태**: 로컬 커밋 완료, **push 실패** (SSH 키 접근 불가 동일)

---

## Step 5 — 검증

### curl HTTP 상태 확인

```
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/API-SMOKE-002-report.md
→ 404  (push 미완료로 GitHub에 미반영)

curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/FRONTEND-AUDIT-001-report.md
→ 404  (push 미완료로 GitHub에 미반영)
```

**기대값**: 200 / **실제**: 404 — **실패**

### claudebot SSH 접근 검증

```bash
sudo -u claudebot GIT_SSH_COMMAND="ssh -i /root/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git -C /srv/newtalk-v2 ls-remote origin HEAD
```

**결과**: 실행 불가 (sudo requires password, terminal required)

---

## 변경 전/후 파일 권한 (ls -la)

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| /root/.ssh/id_ed25519_newtalk | 조회 불가 (Permission denied) | 변경 없음 (root 작업 미실행) |

---

## claudebot groups 출력

```
claudebot : claudebot
```

docker 그룹 미포함 — 변경 없음 (root 작업 미실행)

---

## 미완료 원인 및 필요 조치

**근본 원인**: Claude Bot은 claudebot 계정으로 실행 중이며 sudo 권한 없음.

**필요 조치** (root로 서버 접속 후 수동 실행):
```bash
# Step 1: 백업
cp /root/.ssh/id_ed25519_newtalk /root/.ssh/id_ed25519_newtalk.bak.$(date +%Y%m%d_%H%M%S)

# Step 2: claudebot SSH 키 읽기 권한
chown root:claudebot /root/.ssh/id_ed25519_newtalk
chmod 640 /root/.ssh/id_ed25519_newtalk

# Step 3: docker 그룹 추가
usermod -aG docker claudebot

# Step 4: push
cd /srv/newtalk-v2
GIT_SSH_COMMAND="ssh -i /root/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin main

cd /root/project-docs
GIT_SSH_COMMAND="ssh -i /root/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin master
```

---

## 완료 항목 요약

| Step | 내용 | 결과 |
|------|------|------|
| 1 | SSH 키 백업 | **실패** (Permission denied) |
| 2 | claudebot SSH 키 읽기 권한 부여 | **미실행** (root 권한 필요) |
| 3 | claudebot docker 그룹 추가 | **미실행** (root 권한 필요) |
| 4a | newtalk-v2 git push (6 commits) | **실패** (SSH 키 접근 불가) |
| 4b | project-docs 보고서 복사 + 로컬 커밋 | **성공** (push 실패) |
| 5 | HTTP 200 검증 | **실패** (404, push 미완료) |
| 6 | 보고서 작성 | **완료** |
| 7 | HANDOVER.md 갱신 | **완료** |
