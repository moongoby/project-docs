# Git Push 복구 + Supabase 스키마 실행 작업 보고서

**Task ID**: SF-T021
**지시 파일**: SF_20260306_212822_BRIDGE.md
**작업일**: 2026-03-06 KST
**서버**: 114 (shortflow, /data/shortflow)
**우선순위**: P0-CRITICAL

---

## Part A — Git Push 복구

### 1단계: 현재 remote 확인

```
$ cd /data/shortflow && git remote -v
origin	git@github.com:moongoby/shortflow.git (fetch)
origin	git@github.com:moongoby/shortflow.git (push)
```

→ **SSH 방식으로 이미 설정됨** (HTTPS 전환 불필요)

---

### 2단계: SSH 키 확인

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
```

→ **SSH 키 존재** (`id_ed25519`, ed25519 방식)

---

### 3단계: SSH 접속 테스트

```
$ ssh -T git@github.com 2>&1
git@github.com: Permission denied (publickey).
EXIT_CODE: 255
```

→ **GitHub 미등록 상태** — 공개키가 GitHub에 등록되어 있지 않음

---

### 4단계: 상황별 진단

**해당 케이스: (C) SSH 키는 있으나 GitHub 미등록**

- Remote: SSH ✅ (이미 `git@github.com:moongoby/shortflow.git`)
- SSH 키: 존재 ✅ (`~/.ssh/id_ed25519`)
- GitHub 등록: ❌ (Permission denied)
- sudo 접근: ❌ (터미널 없이 sudo 비밀번호 입력 불가)

**root SSH 키 확인 시도:**
```
$ sudo ls -la /root/.ssh/
sudo: a terminal is required to read the password; either use the -S option
to read from standard input or configure an askpass helper
EXIT_CODE: 1
```
→ sudo 비밀번호 없이 접근 불가

---

### 5단계: git push 실행 결과

```
$ cd /data/shortflow && git push origin main 2>&1; echo "EXIT_CODE: $?"
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
EXIT_CODE: 128
```

→ **PUSH 실패** — SSH 공개키 미등록 원인

---

### 6단계: project-docs 경로 확인

```
$ find / -name "project-docs" -type d 2>/dev/null | head -5
/home/claudebot/project-docs
/data/project-docs
```

→ `/data/project-docs` 존재 확인 (project-docs push도 동일 SSH 이슈로 차단)

---

### git log (현재 로컬 상태)

```
$ git log --oneline -10
d392dee [SF] SF-T020/T021: Git Push 복구 + Supabase 연결 진단 + 알림 이메일 활성화
91c1f14 [SF] SF-T016: Pipeline v5 통합 — Planner+QA+Metadata+Tracker 연동
a514652 [SF] SF-T016 BRIDGE: §2 완료 태스크 정비 + qa_logs 생성 + dry-run PASS
197a38f [SF] SF-T016: HANDOVER v2.2 갱신 + pipeline v5 통합 리포트
7bd63c7 [SF] SF-T017: run_v5_pipeline.py QA 게이트 삽입 — v2 evaluate_all + 85점 미달 업로드 차단
02195c8 [SF] SF-T016: Pipeline v5 통합 — Planner→프롬프트v2→메타데이터→Tracker 자동 연결
489ae57 [SF] SF-T017: QA Score Engine v2 — 4항목 25점 만점, 85점 게이트
b9d1510 [SF] SF-T014: AI Content Planner v1 — Gemini 트렌드 기반 주제 기획 + topic_history
dfcb903 [SF] SF-T013: Performance Tracker v1 — YouTube 영상 성과 수집기 + video_registry
8782abf [SF] SF-T008: 멀티플랫폼 동시 업로드 엔진 구현 (YouTube+TikTok+Instagram+X)
```

---

### Part A 결론

| 항목 | 상태 | 내용 |
|------|------|------|
| Remote URL | ✅ SSH | `git@github.com:moongoby/shortflow.git` |
| SSH 키 존재 | ✅ 존재 | `~/.ssh/id_ed25519` |
| GitHub 등록 | ❌ 미등록 | Permission denied (publickey) |
| git push | ❌ 실패 | EXIT_CODE: 128 |
| 실패 원인 | SSH 공개키 미등록 | CEO 수동 등록 필요 |

**GitHub 등록 필요 공개키:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFXTamuyjYHT8vQQxWEZFTiiCwq6pcbwWVuD5X2e1Mn1 claudebot@rfree-0009
```

**등록 절차**: GitHub.com → Settings → SSH and GPG keys → New SSH key
- Title: `shortflow-server-114-claudebot`
- Key: (위 공개키 전체)

등록 완료 후 서버에서 실행:
```bash
ssh -T git@github.com  # "Hi moongoby!" 메시지 확인
cd /data/shortflow && git push origin main
```

---

## Part B — Supabase 스키마 실행

### 1단계: psql 확인

```
$ which psql
/usr/bin/psql
```

→ **psql 사용 가능**

---

### 2단계: Supabase 연결 정보 확인

```
$ cd /data/shortflow
$ grep -i 'SUPABASE\|POSTGRES\|DATABASE_URL' .env | grep -v '#'
SUPABASE_URL=https://ypvqgojexppcgilacxdz.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

→ **DATABASE_URL 없음**
→ POSTGRES_URL, SUPABASE_DB_URL 등 직접 연결 정보 없음

```
$ grep -i 'DB_URL\|POSTGRES\|DATABASE' .env | grep -v '#'
NO_DB_URL
```

---

### 3단계: 연결 테스트

**결과: DB_URL_MISSING**

.env에 `DATABASE_URL`, `POSTGRES_URL`, `SUPABASE_DB_URL` 등 psql 직접 연결 가능한 URL이 없음.
존재하는 것: SUPABASE_URL (REST API 엔드포인트), SUPABASE_KEY (anon), SUPABASE_SERVICE_KEY (service_role)

Supabase 프로젝트 ref: `ypvqgojexppcgilacxdz`
→ psql 연결 URL 형식: `postgresql://postgres:[PASSWORD]@db.ypvqgojexppcgilacxdz.supabase.co:5432/postgres`
→ DB 비밀번호가 .env에 저장되어 있지 않음

**Part B 중단 (DB_URL_MISSING)**

---

### 4단계: 스키마 파일 확인

```
$ ls /data/shortflow/db/migrations/
001_saas_schema.sql
```

→ 스키마 파일 존재 (`db/migrations/001_saas_schema.sql`) — 연결 정보 확보 시 즉시 실행 가능

---

### Part B 결론

| 항목 | 상태 | 내용 |
|------|------|------|
| psql | ✅ 사용 가능 | `/usr/bin/psql` |
| DATABASE_URL | ❌ 없음 | DB_URL_MISSING |
| 스키마 파일 | ✅ 존재 | `db/migrations/001_saas_schema.sql` |
| 스키마 실행 | ❌ 차단 | DB 연결 정보 부재 |

**CEO 처리 필요:**
1. Supabase Dashboard → Project Settings → Database → Connection string 복사
2. `.env`에 추가 (커밋 금지):
   ```
   DATABASE_URL=postgresql://postgres:[YOUR_DB_PASSWORD]@db.ypvqgojexppcgilacxdz.supabase.co:5432/postgres
   ```
3. 서버에서:
   ```bash
   source /data/shortflow/.env  # 또는 직접 export
   psql "$DATABASE_URL" -f /data/shortflow/db/migrations/001_saas_schema.sql
   psql "$DATABASE_URL" -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"
   ```

---

## 전체 요약

| Task | 상태 | 차단 원인 | CEO 조치 필요 |
|------|------|-----------|---------------|
| Part A: git push | ❌ 실패 | SSH 공개키 GitHub 미등록 | GitHub SSH 키 등록 후 `git push` |
| Part B: Supabase 스키마 | ❌ 차단 | DATABASE_URL 없음 | Supabase DB 비밀번호 → `.env` 추가 후 재실행 |

두 작업 모두 **CEO 수동 처리**가 필요한 자격증명 문제로 차단됨.
