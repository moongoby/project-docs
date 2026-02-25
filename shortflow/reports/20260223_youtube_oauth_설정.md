# Phase 2-2 YouTube OAuth2.0 설정 + 채널 소유 확인 + 토큰 발급 테스트

**작성일시:** 2026-02-23
**작업 유형:** 신규 개발 / 설정 변경
**상태:** 완료
**관련 파일:**  
`scripts/youtube_auth.py`, `scripts/youtube_channel_check.py`, `scripts/youtube_upload_test.py`,  
`docs/guides/youtube_oauth_setup_guide.md`, `.env`, `.env.example`, `.gitignore`

---

## 1. 작업 개요

- Phase 2-1(.env 보안 강화) 완료 후, YouTube Shorts 자동 업로드를 위한 OAuth2.0 인증 체계 구축.
- 자체 채널 **템빨신상맨**, YouTube Data API v3 일일 10,000 units, 업로드 1회 1,600 units, 일일 최대 약 6건 권장.
- 서버: rfree-0009.cafe24.com, 프로젝트 경로 `/data/shortflow`, credentials `/data/shortflow/credentials/`.

---

## 2. 변경 사항

### 2.1 사전 확인(Step 0) 결과

- **.env:** YouTube OAuth용 키(YOUTUBE_CLIENT_ID 등) 없음 → Step 5에서 추가.
- **credentials:** `client_secret.json` 존재(프로젝트 ID 확인됨), `token.pickle` 존재(만료 상태, youtube.upload 스코프만 → 재인증 시 youtube.readonly 포함 권장).
- **YouTube 업로드 관련 기존 .py:** 없음.
- **DB 접속:** 성공, goods 77,111건.

### 2.2 Step 1 – Google Cloud / OAuth 가이드

- **파일:** `docs/guides/youtube_oauth_setup_guide.md`
- 내용: Console 접속, 프로젝트 선택/생성, YouTube Data API v3 활성화, OAuth 2.0 데스크톱 클라이언트 ID 생성, `client_secret.json` 다운로드·배치, OAuth 동의 화면·테스트 사용자, .env YouTube 변수 목록, 할당량(10,000 units / 1,600 per upload), 다음 단계(토큰 발급·채널 확인·업로드 테스트), 보안 유의사항.
- `client_secret.json`이 이미 있으면 프로젝트 ID만 확인해 재활용하도록 명시.

### 2.3 Step 2 – 토큰 발급 스크립트

- **파일:** `scripts/youtube_auth.py`
- 기능: `client_secret.json` 기반 OAuth2.0, `--noauth_local_webserver` 시 URL 출력 후 인증 코드 입력, 인증 후 `token.pickle` 저장, 기존 토큰 유효 시 스킵·만료 시 갱신 시도.
- 스코프: `youtube.upload`, `youtube.readonly`.
- 실행: `python3 /data/shortflow/scripts/youtube_auth.py` (서버에서는 `--noauth_local_webserver` 권장).

### 2.4 Step 3 – 채널 소유 확인 스크립트

- **파일:** `scripts/youtube_channel_check.py`
- 기능: `token.pickle` 로드, `channels.list(mine=True)` 호출, 채널 ID·채널명·구독자·영상 수·조회수 출력, .env `YOUTUBE_CHANNEL_ID`와 일치 여부, API 1 unit 안내.
- 실행: `python3 /data/shortflow/scripts/youtube_channel_check.py`.

### 2.5 Step 4 – 업로드 테스트 스크립트

- **파일:** `scripts/youtube_upload_test.py`
- 기능: `token.pickle` 로드, 테스트 mp4 자동 탐색 또는 FFmpeg 5초 테스트 영상 생성, `videos.insert` 비공개(privacyStatus: private), Video ID·URL 출력, 1,600 units 안내, `--delete` 시 업로드 후 즉시 삭제.
- 실행: `python3 /data/shortflow/scripts/youtube_upload_test.py --delete` (OAuth 인증 완료 후).

### 2.6 Step 5 – .env / .env.example

- .env에 추가(값은 비공개 유지):  
  `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_CHANNEL_ID`,  
  `YOUTUBE_API_SCOPES`, `YOUTUBE_TOKEN_PATH`, `YOUTUBE_CLIENT_SECRET_PATH`,  
  `YOUTUBE_DAILY_QUOTA`, `YOUTUBE_UPLOAD_COST`, `YOUTUBE_MAX_DAILY_UPLOADS`.
- `.env.example`에 동일 키 목록 반영(값 비움).
- `.env.example`에 .env 기타 키 동기화 스크립트 실행 완료.

### 2.7 .gitignore

- `token*.pickle` 명시 추가(credentials/ 로도 제외되며, 이중 확인용).
- `client_secret*.json`, `credentials/` 기존 유지.

### 2.8 백업

- 작업 전: `/data/shortflow/backups/20260223_phase22_pre/`에 .env, credentials/ 복사 완료.

---

## 3. 테스트 결과

- **스크립트 존재:** `youtube_auth.py`, `youtube_channel_check.py`, `youtube_upload_test.py` 정상 생성.
- **가이드:** `docs/guides/youtube_oauth_setup_guide.md` 상단 30줄 이상 확인.
- **.env YouTube 키 이름:** YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_CHANNEL_ID, YOUTUBE_API_SCOPES, YOUTUBE_TOKEN_PATH, YOUTUBE_CLIENT_SECRET_PATH, YOUTUBE_DAILY_QUOTA, YOUTUBE_UPLOAD_COST, YOUTUBE_MAX_DAILY_UPLOADS 확인.
- **credentials:** client_secret.json, token.pickle 등 존재 확인.
- **DB:** 접속 성공, goods 77,111건.
- **의존성:** 서버 시스템 pip3 오류(OpenSSL 등)로 `pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client` 미실행. venv 또는 정상 pip 환경에서 설치 필요.
- **Git 커밋:** 스테이징까지 완료. 커밋 시 환경에서 `git commit --trailer ...` 사용으로 Git 2.25.1 미지원 옵션으로 실패. 사용자가 직접 `git commit` 및 `git push` 실행 필요.

---

## 4. 주의사항 / 후속 작업

- **보안:** .env 실제 값, client_secret 내용, token.pickle은 보고서·가이드에 **절대 노출 금지**. client_secret.json·token.pickle은 Git 미포함(.gitignore 확인됨).
- **OAuth 최초 인증:** 대표님이 브라우저에서 URL 열어 인증 후 코드 붙여넣기 필요(서버에서 `youtube_auth.py --noauth_local_webserver` 실행 시).
- **업로드 테스트:** 반드시 비공개(privacyStatus: private), 테스트 후 `--delete` 권장.
- **할당량:** 업로드 1회 1,600 units, 일일 10,000 units → 최대 약 6건/일 권장.
- **의존성 설치:**  
  `pip3 install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`  
  (venv 또는 pip 정상 동작 환경에서 실행.)
- **수동 커밋/푸시:**  
  `cd /data/shortflow`  
  `git add scripts/youtube_auth.py scripts/youtube_channel_check.py scripts/youtube_upload_test.py docs/guides/youtube_oauth_setup_guide.md .env.example .gitignore`  
  `git commit -m "[feat] YouTube OAuth2.0 auth, channel check, upload test scripts and setup guide"`  
  `git push origin main`
- **project-docs 발행:**  
  `bash /data/project-docs/scripts/sync_shortflow.sh` (해당 스크립트 존재 시).
