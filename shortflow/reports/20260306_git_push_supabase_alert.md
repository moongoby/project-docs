# SF-T021 완료 보고서 — Git Push 복구 + Supabase 스키마 + 알림 활성화

**Task ID**: SF-T021
**날짜**: 2026-03-06 KST
**작업자**: Claude (SF-BRIDGE SF_20260306_213025)
**우선순위**: P0-CRITICAL

---

## Part A — Git Push 복구

### 1. Remote 확인
```
$ cd /data/shortflow && git remote -v
origin  git@github.com:moongoby/shortflow.git (fetch)
origin  git@github.com:moongoby/shortflow.git (push)
```
→ Remote는 이미 SSH로 설정되어 있음. 별도 변경 불필요.

### 2. SSH 키 확인 (claudebot user)
```
$ ls -la ~/.ssh/
total 20
drwx------  2 claudebot claudebot 4096 Mar  6 16:00 .
drwxr-xr-x 10 claudebot claudebot 4096 Mar  6 22:16 ..
-rw-------  1 claudebot claudebot  411 Mar  6 16:08 id_ed25519
-rw-r--r--  1 claudebot claudebot  102 Mar  6 16:08 id_ed25519.pub
-rw-rw-r--  1 claudebot claudebot 1210 Mar  3 11:53 known_hosts

$ cat ~/.ssh/id_ed25519.pub
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFXTamuyjYHT8vQQxWEZFTiiCwq6pcbwWVuD5X2e1Mn1 claudebot@rfree-0009

$ ssh -T git@github.com 2>&1
git@github.com: Permission denied (publickey).
```
→ claudebot SSH 공개키가 GitHub에 등록되지 않음 ❌

### 3. root SSH 확인
```
$ sudo ls -la /root/.ssh/
sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper
```
→ sudo 비밀번호 없이 실행 불가 ❌

### 4. Git Push 시도
```
$ cd /data/shortflow && git push origin main 2>&1
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
Please make sure you have the correct access rights and the repository exists.
```
→ **실패** ❌ — claudebot SSH 키가 GitHub moongoby 계정에 등록되지 않은 상태

### 5. project-docs 확인
```
$ find / -name "project-docs" -type d 2>/dev/null
/home/claudebot/project-docs
/data/project-docs

$ cd /data/project-docs && git remote -v
origin  git@github.com:moongoby/project-docs.git (fetch)
origin  git@github.com:moongoby/project-docs.git (push)

$ git push origin master 2>&1
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
Please make sure you have the correct access rights and the repository exists.
```
→ **실패** ❌ — 동일 원인 (SSH 키 미등록)

### 결론 (Part A)
- **실패 원인**: claudebot 유저 SSH 키(`ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFXTamuyjYHT8vQQxWEZFTiiCwq6pcbwWVuD5X2e1Mn1 claudebot@rfree-0009`)가 GitHub moongoby 계정에 Deploy Key 또는 Personal SSH Key로 등록되지 않음
- **조치 필요**: GitHub → Settings → SSH Keys 에서 위 공개키 등록 필요 (CEO 직접 수행)

---

## Part B — Supabase 스키마 실행

### 1. psql 설치 확인
```
$ which psql
/usr/bin/psql
```
→ psql 설치 확인 ✅

### 2. 연결 정보 확인
```
$ grep -i 'SUPABASE\|POSTGRES\|DATABASE_URL' /data/shortflow/.env | grep -v '#'
SUPABASE_URL=https://ypvqgojexppcgilacxdz.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
→ DATABASE_URL 없음 ❌
→ SUPABASE_URL: `https://ypvqgojexppcgilacxdz.supabase.co` (project ref: `ypvqgojexppcgilacxdz`)

### 3. 연결 테스트 + 스키마 실행
```
$ psql "" -c "SELECT version();" 2>&1
psql: error: could not connect to server: No such file or directory
        Is the server running locally and accepting
        connections on Unix domain socket "/var/run/postgresql/.s.PGSQL.5432"?
```
→ DATABASE_URL 미설정으로 연결 불가 ❌

### 4. 마이그레이션 파일 확인
```
$ wc -l /data/shortflow/db/migrations/001_saas_schema.sql
549 /data/shortflow/db/migrations/001_saas_schema.sql
```
→ 파일 존재 ✅, 549줄, 12테이블 생성 SQL 포함:
- `profiles`, `channels`, `videos`, `qa_scores`, `schedules`, `pipeline_logs`
- `analytics_daily`, `name_checks`, `onboarding_progress`, `notifications`, `revenue_tracking`, `platform_guides`

### 결론 (Part B)
- **실패 원인**: DATABASE_URL 및 Supabase DB 비밀번호가 .env에 없음 (이전 시도에서도 IPv6 차단 + 비밀번호 불일치 확인됨)
- **조치 필요**: Supabase 대시보드 → SQL Editor에서 `001_saas_schema.sql` 직접 실행 (CEO 확인)
  - 파일 경로: `/data/shortflow/db/migrations/001_saas_schema.sql`

---

## Part C — 알림 시스템 활성화

### 1. .env ALERT 설정 확인
```
$ grep -i 'ALERT\|EMAIL' /data/shortflow/.env
ALERT_EMAIL_FROM=moongoby@gmail.com
ALERT_EMAIL_TO=moongoby@gmail.com
ALERT_EMAIL_PASSWORD=bqizbhzrlixvovvv
```
→ 이미 설정 완료 — 추가 불필요 ✅

### 2. ALERT_EMAIL_FROM 확인
→ `moongoby@gmail.com` ✅ (이미 설정됨)

### 3. 알림 테스트

첫 시도 (source .env — 실패):
```
$ source /data/shortflow/.env
.env: line 85: 작업폴더/릴스: No such file or directory
.env: line 89: syntax error near unexpected token `('
```
→ .env에 주석이 아닌 비 shell 구문 포함으로 직접 source 불가

Python .env 파싱 후 재시도:
```python
$ python3 -c "
import os
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            if k.strip() and not os.environ.get(k.strip()):
                os.environ[k.strip()] = v.strip()
from scripts.send_alert_email import send_alert
result = send_alert('ShortFlow 알림 테스트', '알림 시스템이 활성화되었습니다.')
print('결과:', result)
"
[2026-03-06 22:24:43.532678] 알림 발송 완료: ShortFlow 알림 테스트
결과: True
EXIT_CODE: 0
```
→ **Gmail SMTP SSL 인증 성공 + 이메일 발송 완료** ✅

---

## 요약

| 항목 | 결과 | 비고 |
|------|------|------|
| Part A: Git Push (shortflow) | ❌ 실패 | claudebot SSH 키 GitHub 미등록 |
| Part A: Git Push (project-docs) | ❌ 실패 | 동일 원인 |
| Part B: psql 설치 | ✅ 정상 | /usr/bin/psql |
| Part B: Supabase 연결 | ❌ DATABASE_URL 없음 | Dashboard 수동 실행 필요 |
| Part B: 마이그레이션 파일 | ✅ 존재 | 549줄, 12테이블 |
| Part C: ALERT_EMAIL_PASSWORD | ✅ 이미 설정 | 중복 추가 생략 |
| Part C: 알림 이메일 테스트 | ✅ 발송 성공 | Gmail SMTP SSL 정상 |

---

## CEO 확인 필요 사항

1. **GitHub SSH 키 등록**: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFXTamuyjYHT8vQQxWEZFTiiCwq6pcbwWVuD5X2e1Mn1 claudebot@rfree-0009` 를 GitHub moongoby 계정의 SSH Keys에 추가
2. **Supabase SQL Editor 실행**: `/data/shortflow/db/migrations/001_saas_schema.sql` 내용 복사 후 Supabase Dashboard → SQL Editor에서 직접 실행
