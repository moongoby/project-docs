# SF-T005: SaaS 플랫폼 DB 스키마 구축 보고서

**작업일**: 2026-03-06 KST
**Task ID**: SF-T005
**서버**: 114 (shortflow)
**우선순위**: P1-HIGH
**상태**: ✅ 완료

---

## 1. 개요

Shortflow SaaS 플랫폼의 데이터 기반을 구축하기 위해 Supabase(PostgreSQL)에 12개 테이블 DDL과 RLS(Row Level Security) 정책을 작성하였다. 기존 `profiles` 테이블과의 호환성을 유지하면서 신규 테이블을 추가하는 방향으로 설계되었다.

---

## 2. 생성 파일

| 파일 | 설명 |
|------|------|
| `db/migrations/001_saas_schema.sql` | 12테이블 DDL + RLS 정책 + 인덱스 |
| `db/verify_schema.py` | Python 검증 스크립트 |
| `docs/reports/20260306_saas_db_schema.md` | 본 보고서 |

---

## 3. 테이블 목록 (12개)

### 3.1 profiles

```sql
CREATE TABLE IF NOT EXISTS public.profiles (
  id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  user_id       UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name  TEXT,
  plan          TEXT DEFAULT 'free' CHECK (plan IN ('free', 'basic', 'pro', 'enterprise')),
  email         TEXT UNIQUE,
  avatar_url    TEXT,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: Supabase Auth 사용자 프로필 확장
- **RLS**: `auth.uid() = id` (본인만 SELECT/UPDATE/INSERT)
- **기존 데이터 보존**: `IF NOT EXISTS` 사용, 기존 행 무손상

### 3.2 channels

```sql
CREATE TABLE IF NOT EXISTS public.channels (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  platform              TEXT NOT NULL CHECK (platform IN ('youtube', 'tiktok', 'instagram', 'other')),
  channel_name          TEXT NOT NULL,
  channel_id            TEXT,
  oauth_token_encrypted TEXT,
  status                TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'pending')),
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 사용자별 플랫폼 채널 관리
- **RLS**: `user_id = auth.uid()` (SELECT/INSERT/UPDATE/DELETE)
- **보안**: `oauth_token_encrypted` 필드는 암호화된 토큰만 저장

### 3.3 videos

```sql
CREATE TABLE IF NOT EXISTS public.videos (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id       UUID NOT NULL REFERENCES public.channels(id) ON DELETE CASCADE,
  title            TEXT NOT NULL,
  description      TEXT,
  file_path        TEXT,
  youtube_video_id TEXT,
  status           TEXT DEFAULT 'pending',
  qa_score         NUMERIC(5,2),
  published_at     TIMESTAMPTZ,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 생성 영상 메타데이터 + 업로드 상태 추적
- **RLS**: channels → user_id 조인 기반 소유자 확인
- **status 값**: `pending | processing | ready | uploading | published | failed | deleted`

### 3.4 qa_scores

```sql
CREATE TABLE IF NOT EXISTS public.qa_scores (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id         UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
  visual_score     NUMERIC(5,2),
  audio_score      NUMERIC(5,2),
  script_score     NUMERIC(5,2),
  engagement_score NUMERIC(5,2),
  total_score      NUMERIC(5,2),
  created_at       TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 영상 QA 점수 기록 (SF-T002 QA 엔진 연동)
- **RLS**: videos → channels → user_id 체인 조인

### 3.5 schedules

```sql
CREATE TABLE IF NOT EXISTS public.schedules (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id            UUID NOT NULL REFERENCES public.channels(id) ON DELETE CASCADE,
  cron_expression       TEXT NOT NULL,
  upload_count_per_day  INT DEFAULT 1 CHECK (upload_count_per_day BETWEEN 1 AND 20),
  is_active             BOOLEAN DEFAULT true,
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 채널별 업로드 스케줄 정의
- **RLS**: channels → user_id 기반

### 3.6 pipeline_logs

```sql
CREATE TABLE IF NOT EXISTS public.pipeline_logs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id      UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
  step          TEXT NOT NULL,
  status        TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'success', 'failed', 'skipped')),
  error_message TEXT,
  started_at    TIMESTAMPTZ,
  completed_at  TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 파이프라인 각 단계 실행 로그
- **RLS**: videos → channels → user_id 체인

### 3.7 analytics_daily

```sql
CREATE TABLE IF NOT EXISTS public.analytics_daily (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id             UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
  date                 DATE NOT NULL,
  views                BIGINT DEFAULT 0,
  watch_time_sec       BIGINT DEFAULT 0,
  avg_view_duration    NUMERIC(10,2),
  retention_rate       NUMERIC(5,2),
  likes                INT DEFAULT 0,
  comments             INT DEFAULT 0,
  shares               INT DEFAULT 0,
  subscribers_gained   INT DEFAULT 0,
  created_at           TIMESTAMPTZ DEFAULT now(),
  UNIQUE (video_id, date)
);
```

- **목적**: 영상별 일별 분석 데이터
- **RLS**: videos → channels → user_id 체인
- **유니크**: `(video_id, date)` - 날짜 중복 방지

### 3.8 name_checks

```sql
CREATE TABLE IF NOT EXISTS public.name_checks (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  platform          TEXT NOT NULL,
  desired_name      TEXT NOT NULL,
  is_available      BOOLEAN,
  alternatives_json JSONB,
  checked_at        TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 채널명 가용성 체크 이력
- **RLS**: `user_id = auth.uid()`

### 3.9 onboarding_progress

```sql
CREATE TABLE IF NOT EXISTS public.onboarding_progress (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                 UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  step_current            INT DEFAULT 1,
  steps_total             INT DEFAULT 5,
  platform_statuses_json  JSONB DEFAULT '{}',
  completed_at            TIMESTAMPTZ,
  created_at              TIMESTAMPTZ DEFAULT now(),
  updated_at              TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 사용자 온보딩 진행 상태
- **RLS**: `user_id = auth.uid()`

### 3.10 notifications

```sql
CREATE TABLE IF NOT EXISTS public.notifications (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  type       TEXT NOT NULL CHECK (type IN ('info', 'success', 'warning', 'error', 'upload', 'qa', 'billing')),
  title      TEXT NOT NULL,
  message    TEXT,
  is_read    BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 사용자 인앱 알림
- **RLS**: `user_id = auth.uid()`

### 3.11 revenue_tracking

```sql
CREATE TABLE IF NOT EXISTS public.revenue_tracking (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id     UUID NOT NULL REFERENCES public.channels(id) ON DELETE CASCADE,
  date           DATE NOT NULL,
  platform       TEXT NOT NULL,
  revenue_amount NUMERIC(12,4) DEFAULT 0,
  currency       TEXT DEFAULT 'USD',
  source         TEXT,
  created_at     TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 채널별 수익 트래킹
- **RLS**: channels → user_id 기반

### 3.12 platform_guides

```sql
CREATE TABLE IF NOT EXISTS public.platform_guides (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform       TEXT NOT NULL,
  step_number    INT NOT NULL,
  title          TEXT NOT NULL,
  description    TEXT,
  screenshot_url TEXT,
  created_at     TIMESTAMPTZ DEFAULT now()
);
```

- **목적**: 플랫폼별 온보딩 가이드 콘텐츠
- **RLS**: SELECT는 전체 공개(`USING (true)`), INSERT는 enterprise 플랜 제한

---

## 4. RLS 정책 요약

| 테이블 | SELECT | INSERT | UPDATE | DELETE | 기준 |
|--------|--------|--------|--------|--------|------|
| profiles | ✅ | ✅ | ✅ | - | `auth.uid() = id` |
| channels | ✅ | ✅ | ✅ | ✅ | `user_id = auth.uid()` |
| videos | ✅ | ✅ | ✅ | ✅ | channels join |
| qa_scores | ✅ | ✅ | - | - | videos → channels join |
| schedules | ✅ | ✅ | ✅ | ✅ | channels join |
| pipeline_logs | ✅ | ✅ | - | - | videos → channels join |
| analytics_daily | ✅ | ✅ | - | - | videos → channels join |
| name_checks | ✅ | ✅ | - | - | `user_id = auth.uid()` |
| onboarding_progress | ✅ | ✅ | ✅ | - | `user_id = auth.uid()` |
| notifications | ✅ | ✅ | ✅ | ✅ | `user_id = auth.uid()` |
| revenue_tracking | ✅ | ✅ | - | - | channels join |
| platform_guides | 공개 | enterprise only | - | - | - |

---

## 5. 마이그레이션 실행 방법

### Supabase SQL Editor (권장)

1. [Supabase Dashboard] → SQL Editor 접속
2. `db/migrations/001_saas_schema.sql` 전체 내용 붙여넣기
3. Run (Ctrl+Enter)

### Supabase CLI

```bash
supabase db push
# 또는
supabase db diff --use-migra | supabase db push
```

---

## 6. 검증

```bash
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="eyJ..."
python3 db/verify_schema.py
```

기대 출력:
```
✅ OK  profiles
✅ OK  channels
...
결과: ✅ 모든 12개 테이블 존재 확인 완료
```

---

## 7. 보안 준수 (D-005)

- `.env`, OAuth 토큰 파일 Git 커밋 금지
- `oauth_token_encrypted`: 암호화된 값만 저장
- RLS: 모든 테이블에 적용 완료

---

## 8. 후속 작업

- SF-T006: 채널 연동 API 엔드포인트 구현
- SF-T007: analytics_daily 자동 수집 크론 연동
- SF-T008: revenue_tracking API 연동 (YouTube Analytics API)
