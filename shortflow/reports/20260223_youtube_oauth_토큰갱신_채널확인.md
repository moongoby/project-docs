# YouTube OAuth 토큰 갱신 및 채널 확인 (Phase 2-2)

**작성일시:** 2026-02-23
**작업 유형:** 설정 변경 / 검증
**상태:** 부분 완료 (토큰 갱신·업로드 성공, 채널 확인·삭제는 스코프 재인증 후 가능)
**관련 파일:** `credentials/token.pickle`, `scripts/youtube_auth.py`, `scripts/youtube_channel_check.py`, `scripts/youtube_upload_test.py`

---

## 1. 작업 개요

Phase 2-2: OAuth 토큰 갱신, 채널 소유 확인, 업로드 테스트를 수행하여 YouTube 자동 업로드 인증 체계를 검증하였다. 토큰은 refresh로 갱신되었으나, 기존 토큰이 **youtube.upload** 스코프만 보유하여 채널 API·영상 삭제는 실패하였다. 업로드 자체는 정상 동작 확인.

---

## 2. 변경 사항 및 실행 결과

### 백업

- **경로:** `/data/shortflow/backups/20260223_000000/`
- **내용:** `credentials/` 전체 복사
- 작업 전 생성 완료.

### Step 1 – 토큰 자동 갱신

- **명령:** `python3 scripts/youtube_auth.py` (venv 활성화)
- **결과:** 성공
- **출력:** `토큰 갱신 완료.` / `토큰 저장 완료: .../credentials/token.pickle`
- **비고:** refresh_token으로 access token 갱신만 수행. 기존 토큰의 스코프는 그대로 유지됨.

### Step 2 – 채널 소유 확인

- **명령:** `python3 scripts/youtube_channel_check.py`
- **결과:** 실패 (스코프 부족)
- **에러:** `HttpError 403 ... "Request had insufficient authentication scopes."` (Insufficient Permission)
- **원인:** 현재 token.pickle의 스코프가 `youtube.upload`만 있음. `channels.list(mine=True)`에는 `youtube.readonly` 필요.
- **.env YOUTUBE_CHANNEL_ID 일치 여부:** 채널 확인 미실행으로 비교 불가. 재인증 후 Step 2 재실행 시 일치/불일치만 보고서에 기록할 것.

#### 재인증 시 (대표님 브라우저 인증 필요)

- 아래 URL을 브라우저에서 연 뒤, 로그인 후 표시되는 **인증 코드**를 복사한다.
- 서버에서:  
  `python3 scripts/youtube_auth.py --noauth_local_webserver`  
  실행 후 프롬프트에 인증 코드 붙여넣기.
- 또는 기존 토큰을 버리고 전체 재발급:  
  `python3 scripts/youtube_auth.py --force --noauth_local_webserver`  
  → 동일하게 URL 출력 후 코드 입력.

**인증 URL (재인증 시 브라우저에서 열기):**

```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=651195163214-mjupn2kn5ere0a77m4sn7oj15269nidv.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.upload+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.readonly&state=xIY2A4oQ5i0dzNpxvBlTs3HFB1qVe9&prompt=consent&access_type=offline
```

- **주의:** state 값은 실행 시마다 바뀌므로, 재인증 시에는 당일 실행 시 출력되는 URL을 사용할 것.

### Step 3 – 업로드 테스트 (비공개 + 삭제)

- **명령:** `python3 scripts/youtube_upload_test.py --delete`
- **업로드:** 성공
  - **privacyStatus:** private
  - **Video ID:** yMnvHuZXjXY
  - **URL:** https://www.youtube.com/watch?v=yMnvHuZXjXY
  - **소모 units:** 1600
- **삭제:** 실패 (스코프 부족)
  - **에러:** `HttpError 403 ... "Request had insufficient authentication scopes."` (Insufficient Permission)
  - **원인:** 영상 삭제에는 upload 외 추가 스코프(예: youtube.force-ssl 등) 필요. 현재 토큰은 youtube.upload만 보유.
- **조치:** 테스트 영상은 YouTube 스튜디오에서 수동 삭제 가능. Video ID: **yMnvHuZXjXY**.

### Step 4 – 검증

- **토큰 상태 (credentials/token.pickle):**
  - `valid`: True
  - `expired`: False
  - `scopes`: `['https://www.googleapis.com/auth/youtube.upload']`
- **.env YouTube 관련 키 (키 이름만):**  
  YOUTUBE_CHANNELS_JSON, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_CHANNEL_ID, YOUTUBE_API_SCOPES, YOUTUBE_TOKEN_PATH, YOUTUBE_CLIENT_SECRET_PATH, YOUTUBE_DAILY_QUOTA, YOUTUBE_UPLOAD_COST, YOUTUBE_MAX_DAILY_UPLOADS
- **최근 커밋 (git log --oneline -3):**
  - c4a69e0 feat: YouTube OAuth2.0 auth channel check upload test scripts and setup guide
  - 747480a config env security
  - 9c4865b [config] 작업 보고서 자동 발행 규칙 추가

---

## 3. 테스트 결과 요약

| 항목           | 결과     | 비고                          |
|----------------|----------|-------------------------------|
| 토큰 갱신      | 성공     | refresh로 갱신 완료           |
| 채널 확인      | 실패     | 스코프 부족, 재인증 후 재실행 |
| 비공개 업로드  | 성공     | Video ID·URL 출력 확인        |
| 업로드 후 삭제 | 실패     | 스코프 부족, 수동 삭제 권장   |
| 토큰 valid     | True     | expired: False                |

---

## 4. 주의사항 / 후속 작업

- **재인증:** 채널 확인 및 API 삭제를 쓰려면 `youtube.readonly`(및 필요 시 삭제용 스코프)가 포함된 토큰이 필요함. `youtube_auth.py --force --noauth_local_webserver`로 위 인증 URL을 새로 받아 브라우저 인증 후 코드 입력하여 토큰 재발급 권장.
- **테스트 영상:** yMnvHuZXjXY 는 비공개로 업로드됨. 할당량 절약을 위해 YouTube 스튜디오에서 수동 삭제 권장.
- **보안:** .env 실제 값, client_secret 내용, token 내용은 보고서에 노출하지 않음.
- **venv:** 모든 YouTube 스크립트 실행 시 `source /data/shortflow/venv/bin/activate` 필수.
- **project-docs 동기화:** `bash /data/project-docs/scripts/sync_shortflow.sh` 실행함. shortflow → project-docs 복사 및 로컬 커밋 완료. push는 원격에 새 커밋이 있어 거절됨(`fetch first`). 필요 시 project-docs에서 `git pull --rebase` 후 `git push` 수행.
