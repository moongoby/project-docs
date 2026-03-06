# SF-T020: Supabase SQL 스키마 실행 보고서

**작성일**: 2026-03-06 KST
**Task ID**: SF-T020
**서버**: 114 (shortflow, /data/shortflow)
**상태**: ❌ BLOCKED — CONNECTION_INFO_MISSING + PSQL_INSTALL_FAILED

---

## §1. 실행 단계별 결과

### Step 1: psql 설치 확인

```bash
$ which psql
psql not found
```

**결과**: psql 미설치 확인됨.

### Step 2: psql 설치 시도

```bash
$ sudo apt-get install -y postgresql-client
sudo: a terminal is required to read the password; either use the -S option...

$ apt-get install -y postgresql-client
E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)
E: Unable to acquire the dpkg frontend lock, are you root?
```

**결과**: **PSQL_INSTALL_FAILED**
- 실행 사용자: `claudebot` (uid=1009, gid=1010) — root 아님
- sudo 권한 없음, apt-get 설치 불가

### Step 3: .env Supabase/PostgreSQL 연결 정보 확인

```bash
$ grep -i 'SUPABASE\|POSTGRES\|DATABASE_URL' /data/shortflow/.env | grep -v '#'
SUPABASE_URL=https://ypvqgojexppcgilacxdz.supabase.co
SUPABASE_KEY=eyJhbGci... (anon JWT)
SUPABASE_SERVICE_KEY=eyJhbGci... (service_role JWT)
```

**확인된 정보**:
| 항목 | 값 | 상태 |
|------|-----|------|
| SUPABASE_URL | https://ypvqgojexppcgilacxdz.supabase.co | ✅ 존재 |
| SUPABASE_KEY | anon JWT token | ✅ 존재 (REST API용) |
| SUPABASE_SERVICE_KEY | service_role JWT token | ✅ 존재 (REST API용) |
| DATABASE_URL | — | ❌ **CONNECTION_INFO_MISSING** |
| DB_PASSWORD | — | ❌ **CONNECTION_INFO_MISSING** |
| PGHOST / PGPORT | — | ❌ **CONNECTION_INFO_MISSING** |

**결론**: `.env`에 psql 직접 연결에 필요한 DB 비밀번호(DATABASE_URL) 없음.
SUPABASE_KEY / SUPABASE_SERVICE_KEY는 JWT 토큰 (PostgREST REST API용)이며, psql 직접 연결 패스워드가 아님.

### Step 4: Supabase REST API 연결 테스트 (대안)

psql 연결이 불가하여 REST API 연결 테스트 수행.

```bash
$ curl -s "https://ypvqgojexppcgilacxdz.supabase.co/rest/v1/" \
  -H "apikey: [SUPABASE_SERVICE_KEY]" \
  -H "Authorization: Bearer [SUPABASE_SERVICE_KEY]"
→ 200 OK (OpenAPI swagger 응답)
```

**결과**: Supabase 프로젝트 REST API 연결 **성공**.
프로젝트 ref: `ypvqgojexppcgilacxdz`

### Step 5: 현재 Supabase public 스키마 테이블 확인 (REST API via swagger)

```
현재 존재하는 테이블 (13개):
/analytics
/daily_picks
/feedback_insights
/jobs
/optimization_logs
/product_blacklist
/profiles
/prompt_templates
/raw_videos
/scripts
/trends
/video_analytics
/videos
```

### Step 6: 마이그레이션 SQL 파일 확인

```bash
$ ls /data/shortflow/db/migrations/
001_saas_schema.sql  ✅ 존재
```

파일 내용: 12개 SaaS 테이블 DDL 포함 (550줄).

### Step 7: SQL 실행 — BLOCKED

psql 미설치 + DB 패스워드 없음으로 실행 불가.
PostgREST REST API는 임의 DDL 실행 불가 (보안상 제한).
Python psycopg2: 미설치, pip 설치도 OpenSSL 오류로 실패.

```
→ STATUS: SQL 실행 불가 / BLOCKED
```

---

## §2. SaaS 12테이블 현황

| # | 테이블명 | 필요 | 현재 존재 | 비고 |
|---|---------|------|-----------|------|
| 1 | profiles | ✅ | ⚠️ 이미 존재 (다른 스키마) | 기존 profiles 테이블 존재, SaaS 스키마 적용 여부 불명 |
| 2 | channels | ✅ | ❌ 없음 | 생성 필요 |
| 3 | videos | ✅ | ⚠️ 이미 존재 (다른 스키마) | 기존 videos 테이블 존재, SaaS 스키마 적용 여부 불명 |
| 4 | qa_scores | ✅ | ❌ 없음 | 생성 필요 |
| 5 | schedules | ✅ | ❌ 없음 | 생성 필요 |
| 6 | pipeline_logs | ✅ | ❌ 없음 | 생성 필요 |
| 7 | analytics_daily | ✅ | ❌ 없음 | 생성 필요 |
| 8 | name_checks | ✅ | ❌ 없음 | 생성 필요 |
| 9 | onboarding_progress | ✅ | ❌ 없음 | 생성 필요 |
| 10 | notifications | ✅ | ❌ 없음 | 생성 필요 |
| 11 | revenue_tracking | ✅ | ❌ 없음 | 생성 필요 |
| 12 | platform_guides | ✅ | ❌ 없음 | 생성 필요 |

**결론**: 10개 테이블 미생성. 스키마 실행 필요.

---

## §3. 블로커 요약

| 블로커 | 상세 | 해결 방법 |
|--------|------|-----------|
| PSQL_INSTALL_FAILED | claudebot 사용자 권한 없음 (apt-get 불가) | root/sudo 권한자가 postgresql-client 설치 필요 |
| CONNECTION_INFO_MISSING | .env에 DATABASE_URL / DB_PASSWORD 없음 | Supabase 대시보드 → Project Settings → Database → Connection String 확인 후 .env에 DATABASE_URL 추가 |

---

## §4. 수동 실행 가이드 (CEO/운영자용)

### Option A: Supabase SQL Editor (가장 빠름)
1. https://supabase.com/dashboard/project/ypvqgojexppcgilacxdz 접속
2. SQL Editor 메뉴 클릭
3. `/data/shortflow/db/migrations/001_saas_schema.sql` 내용 붙여넣기
4. "Run" 클릭
5. `\dt` 또는 Table Editor에서 12테이블 확인

### Option B: psql 직접 실행 (root 사용자)
1. `sudo apt-get install -y postgresql-client`
2. Supabase 대시보드 → Project Settings → Database → Connection string (Direct) 복사
3. `psql "postgresql://postgres.[PROJECT_REF]:[DB_PASSWORD]@db.ypvqgojexppcgilacxdz.supabase.co:5432/postgres" -f /data/shortflow/db/migrations/001_saas_schema.sql`
4. `psql "..." -c "\dt"` 로 12테이블 확인
5. `.env`에 `DATABASE_URL=postgresql://...` 추가

### Option C: .env에 DATABASE_URL 추가 후 재실행
1. Supabase 대시보드에서 DB 비밀번호 확인
2. `.env`에 `DATABASE_URL=postgresql://postgres.[ref]:[pass]@db.ypvqgojexppcgilacxdz.supabase.co:5432/postgres` 추가
3. 이 Task (SF-T020) 재실행

---

## §5. 검증 스크립트 위치

```
/data/shortflow/db/verify_schema.py
```

실행 후 12테이블 존재 여부 자동 확인.

---

## §6. 완료 기준 (미달성)

- [ ] 12테이블 생성 확인 — ❌ BLOCKED
- [ ] `\dt` 결과 캡처 — ❌ BLOCKED
- [ ] 보고서 작성 — ✅ 완료 (이 문서)
- [ ] 로컬 커밋 — 진행 중

---

*보고서 작성: SF-T020 자동 실행, 2026-03-06 KST*
