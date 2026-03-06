# SF-T008 멀티플랫폼 동시 업로드 엔진 구현 보고서

**날짜**: 2026-03-06
**Task ID**: SF-T008
**우선순위**: P2-NORMAL
**의존성**: SF-T006, SF-T013

---

## 1. 개요

YouTube 알고리즘 가산점 확보 및 채널 노출 극대화를 위해
YouTube + TikTok + Instagram + X(Twitter) **동시 업로드 엔진**을 구현하였다.

---

## 2. 산출물

| 파일 | 설명 |
|------|------|
| `engine/multi_platform_uploader.py` | 멀티플랫폼 업로드 엔진 (신규) |
| `scripts/run_v4_pipeline.py` | v4 파이프라인 — SF-T008 멀티플랫폼 호출 블록 추가 |
| `docs/reports/20260306_multi_upload.md` | 본 보고서 |

---

## 3. 구현 내용

### 3.1 `engine/multi_platform_uploader.py`

#### 구조

```
upload_all_platforms()          ← 메인 진입점
├─ _upload_youtube()            ← 기존 YouTube Data API v3 래핑
├─ _upload_tiktok()             ← TikTok Content Posting API
├─ _upload_instagram()          ← Instagram Content Publishing API (FB Graph API)
└─ _upload_x()                  ← X Media Upload → Tweet Create
```

#### 플랫폼별 동작

| 플랫폼 | OAuth 토큰 파일 | 미연결 시 동작 | API |
|--------|----------------|---------------|-----|
| YouTube | `config/youtube_token_{channel}.json` | graceful skip | YouTube Data API v3 |
| TikTok | `config/tiktok_token_{channel}.json` | graceful skip | TikTok Content Posting API v2 |
| Instagram | `config/instagram_token_{channel}.json` | graceful skip | Facebook Graph API v19.0 |
| X | `config/x_token_{channel}.json` | graceful skip | Twitter API v2 + Media Upload v1.1 |

#### 플랫폼별 메타데이터 조정

| 플랫폼 | 제목 최대 | 설명 최대 | 해시태그 형식 |
|--------|----------|----------|--------------|
| YouTube | 100자 | 5,000자 | `#태그 #태그` |
| TikTok | 150자 | 2,200자 | `#태그 #태그` |
| Instagram | (캡션에 통합) | 2,200자 | `#태그 #태그` |
| X | (트윗에 통합) | 280자 | `#태그 #태그` |

#### 장애 격리

- 각 플랫폼 업로드는 **독립 try/except** — 하나 실패해도 나머지 진행
- `PlatformResult.status`: `"success"` | `"skipped"` | `"failed"`
- YouTube 실패해도 TikTok/Instagram/X 업로드 계속 시도

### 3.2 `scripts/run_v4_pipeline.py` 수정

- `upload_with_privacy()` (YouTube) 성공 후 `upload_all_platforms()` 호출
- TikTok/Instagram/X 결과는 로그 출력 후 무시 (YouTube 업로드 성공 시 파이프라인 완료 처리)
- `_mp_err` 예외 발생 시 "무시, YouTube 업로드는 성공" 메시지 출력 후 계속

---

## 4. 완료 기준 확인

| 항목 | 상태 |
|------|------|
| YouTube 업로드 기존대로 정상 동작 | ✅ `upload_with_privacy()` 유지, `upload_all_platforms()` 가 후속 실행 |
| TikTok OAuth 미연결 시 graceful skip | ✅ `tiktok_token_{channel}.json` 없으면 SKIP 메시지 출력 |
| Instagram OAuth 미연결 시 graceful skip | ✅ `instagram_token_{channel}.json` 없으면 SKIP |
| X OAuth 미연결 시 graceful skip | ✅ `x_token_{channel}.json` 없으면 SKIP |
| 로그에 플랫폼별 업로드 상태 기록 | ✅ `[SF-T008] {platform} 업로드 완료/SKIP/실패` 로그 |
| HANDOVER.md §2 SF-T008 추가 | ✅ (이 보고서 작성 후 업데이트) |

---

## 5. OAuth 연결 방법 (향후)

### TikTok
1. TikTok for Developers → 앱 생성 → `video.publish` 스코프
2. OAuth 2.0 코드 교환 후 `access_token` 취득
3. `config/tiktok_token_{channel}.json` 에 `{"access_token": "..."}` 저장

### Instagram
1. Meta for Developers → Instagram Graph API → `instagram_basic`, `instagram_content_publish` 권한
2. `config/instagram_token_{channel}.json` 에 `{"access_token": "...", "ig_user_id": "...", "video_cdn_url": "..."}` 저장
   - **주의**: Instagram Reels 업로드는 공개 CDN URL 필요 (로컬 파일 직접 전송 불가)

### X(Twitter)
1. Twitter Developer Portal → 앱 생성 → OAuth 1.0a User Context
2. `config/x_token_{channel}.json` 에 4개 키 저장:
   ```json
   {
     "consumer_key": "...",
     "consumer_secret": "...",
     "access_token": "...",
     "access_token_secret": "..."
   }
   ```
3. `pip install requests-oauthlib` 필요

---

## 6. 추가 의존성

```
# requirements.txt 에 추가 (X 업로드 시)
requests-oauthlib>=1.3.1
```

---

## 7. 로그 예시

```
[2026-03-06 19:00:01] 멀티플랫폼 업로드 시작 (TikTok / Instagram / X) ...
[2026-03-06 19:00:01] [SF-T008] tiktok SKIP: TikTok OAuth 토큰 없음: /data/shortflow/config/tiktok_token_economy.json
[2026-03-06 19:00:01] [SF-T008] instagram SKIP: Instagram 토큰 없음: /data/shortflow/config/instagram_token_economy.json
[2026-03-06 19:00:01] [SF-T008] x SKIP: X(Twitter) OAuth 토큰 없음: /data/shortflow/config/x_token_economy.json
[2026-03-06 19:00:01] === v4 파이프라인 완료: economy | 영상ID=abc123 | QA=88/100 | public ===
```

---

*ShortFlow SF-T008 완료 — 2026-03-06*
