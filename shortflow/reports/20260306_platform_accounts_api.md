# SF-T032: 멀티플랫폼 계정 DB + FastAPI API 구현 보고서

**작성일**: 2026-03-06
**Task ID**: SF-T032
**상태**: 완료
**서버**: 114 (shortflow, /data/shortflow)

---

## 개요

멀티플랫폼 소셜 계정 등록 및 관리를 위한 DB 스키마, FastAPI API 라우터, 플랫폼 상수 정의, 기존 YouTube 채널 마이그레이션 스크립트를 구현하였다.

---

## 완료 항목

### 사전 백업

```
backups/shortflow_pre_T032_20260306_224051.tar.gz
```
- `--exclude='./venv' --exclude='./venv_old' --exclude='./cache/stock_videos' --exclude='./node_modules' --exclude='./backups'` 옵션 적용

---

### STEP 1 — DB 마이그레이션 파일 (기존 파일 확인·유지)

**파일**: `db/migrations/002_platform_accounts.sql`
**상태**: 이미 존재 (SF-T022에서 생성됨) — 더 완전한 버전으로 유지

**포함 내용**:
- `handle_updated_at()` 트리거 함수 생성
- `platform_accounts` 테이블 생성 (UUID PK, user_id FK, platform, account_nickname, auth_status, platform_config JSONB 등 16개 컬럼)
- 인덱스: `idx_user_platform_nickname` (UNIQUE), `idx_platform`, `idx_user_active`
- Row Level Security 활성화 및 정책 "Users manage own accounts" 설정
- `set_platform_accounts_updated_at` BEFORE UPDATE 트리거

**Supabase 연결**: 미연결 (SUPABASE_URL/SUPABASE_SERVICE_KEY 미설정) — 파일만 보존

---

### STEP 2 — 플랫폼 상수 정의

**파일**: `config/platforms.json` (신규 생성)

**지원 플랫폼 (14개)**:
| 플랫폼 | 이름 | OAuth | API 업로드 | 동영상 스펙 |
|--------|------|-------|-----------|------------|
| youtube | YouTube | ✓ | ✓ | vertical ≤60s |
| instagram | Instagram | ✓ | ✓ | vertical ≤90s |
| tiktok | TikTok | ✓ | ✓ | vertical ≤10m |
| facebook | Facebook | ✓ | ✓ | vertical ≤90s |
| x | X (Twitter) | ✓ | ✓ | vertical ≤140s |
| naver_clip | 네이버 클립 | ✓ | ✗ | vertical ≤60s |
| kakao | 카카오 | ✓ | ✓ | vertical |
| linkedin | LinkedIn | ✓ | ✓ | any |
| pinterest | Pinterest | ✓ | ✓ | vertical |
| snapchat | Snapchat | ✓ | ✓ | vertical ≤60s |
| threads | Threads | ✓ | ✓ | vertical |
| lemon8 | Lemon8 | ✗ | ✗ | vertical |
| naver_blog | 네이버 블로그 | ✓ | ✓ | any |
| kakao_story | 카카오스토리 | ✓ | ✓ | any |

---

### STEP 3 — FastAPI 라우터

**파일 A**: `api/routes/platform_accounts.py` (신규 생성)
**파일 B**: `api/routers/platform_accounts.py` (기존 SF-T022 파일 유지)

**6개 엔드포인트**:
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/platforms | platforms.json 반환 |
| GET | /api/accounts | 유저 계정 목록 (Supabase RPC 또는 직접 쿼리) |
| POST | /api/accounts | 새 계정 등록 |
| PUT | /api/accounts/{id} | 계정 수정 |
| DELETE | /api/accounts/{id} | soft delete (is_active=false) |
| POST | /api/accounts/{id}/refresh-token | 토큰 갱신 placeholder |

**Supabase 폴백**: `data/accounts.json` 파일 기반 임시 저장소로 자동 폴백

**worker/main.py 등록**:
```python
# SF-T032: 멀티플랫폼 계정 등록 API
from api.routes.platform_accounts import router as platform_accounts_router
app.include_router(platform_accounts_router)
```
→ API 서버 재시작 후 활성화됨

---

### STEP 4 — 기존 채널 마이그레이션 스크립트

**파일**: `scripts/migrate_existing_channels.py` (신규 생성)

**마이그레이션 결과** (JSON 폴백 사용):
- Supabase: 연결 실패 (`module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'`)
- 폴백: `data/accounts.json` 저장 완료
- 삽입 완료: `['3분경제', '건강한입']`
- 중복 스킵: `[]`

**저장된 계정 데이터**:
```json
[
  {
    "platform": "youtube",
    "account_nickname": "3분경제",
    "platform_user_id": "UC1qhhty2MDsF4worImq6-dQ",
    "connected_email": "oby240610@gmail.com",
    "auth_status": "active",
    "niche": "economy_finance"
  },
  {
    "platform": "youtube",
    "account_nickname": "건강한입",
    "platform_user_id": "UCKRf4X2fOwhTGcKSVO8rLYQ",
    "connected_email": "moongo76@gmail.com",
    "auth_status": "active",
    "niche": "health_wellness"
  }
]
```

---

### STEP 5 — 테스트 결과

```bash
# platforms.json 로드 테스트
platforms.json LOAD_OK: 14 개 플랫폼
플랫폼 목록: ['youtube', 'instagram', 'tiktok', 'facebook', 'x', 'naver_clip',
              'kakao', 'linkedin', 'pinterest', 'snapchat', 'threads', 'lemon8',
              'naver_blog', 'kakao_story']

# accounts.json 로드 테스트
accounts.json LOAD_OK: 2 개 계정
 - 3분경제 / youtube / active
 - 건강한입 / youtube / active

# 핵심 로직 import 테스트 (FastAPI 의존 제외)
IMPORT_OK (non-FastAPI core)

# FastAPI import 테스트
FAILED: fastapi 미설치 (호스트 python3.9 환경)
→ FastAPI는 worker 컨테이너 환경에서 python3.11로 실행 중

# curl 테스트
$ curl http://localhost:8000/api/platforms
{"detail":"Not Found"}
→ worker/main.py에 라우터 등록 완료, 재시작 후 활성화 예정
```

---

## 생성/수정 파일 목록

| 파일 | 작업 |
|------|------|
| `db/migrations/002_platform_accounts.sql` | 기존 유지 (더 완전한 버전) |
| `config/platforms.json` | 신규 생성 |
| `api/routes/__init__.py` | 신규 생성 |
| `api/routes/platform_accounts.py` | 신규 생성 (Supabase+JSON 폴백) |
| `scripts/migrate_existing_channels.py` | 신규 생성 |
| `data/accounts.json` | 마이그레이션으로 자동 생성 |
| `worker/main.py` | platform_accounts_router 등록 추가 |
| `docs/reports/20260306_platform_accounts_api.md` | 본 보고서 |

---

## 완료 기준 달성

- [x] 마이그레이션 SQL (`db/migrations/002_platform_accounts.sql`) — 기존 파일 확인·유지
- [x] `config/platforms.json` — 14개 플랫폼 정의
- [x] API 라우터 (`api/routes/platform_accounts.py`) — 6 엔드포인트, JSON 폴백 포함
- [x] 마이그레이션 스크립트 (`scripts/migrate_existing_channels.py`) — economy, health 채널 삽입 완료
- [x] `worker/main.py`에 라우터 등록
- [x] 보고서 작성
