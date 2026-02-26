# YouTube OAuth 키 등록 (newtalk) + venv + 토큰 발급

**작성일시:** 2026-02-25 KST  
**작업 유형:** OAuth 키 등록(newtalk) / venv 구성 / 토큰 발급  
**상태:** 설정 완료, 토큰 발급은 대표님 인증 코드 입력 대기  
**서버:** 114.207.244.86 (ssh root@114.207.244.86)  
**작업 디렉터리:** /data/shortflow  
**OAuth 프로젝트:** newtalk (moongoby@gmail.com)

---

## 1. 작업 요약

| 단계 | 내용 | 결과 |
|------|------|------|
| STEP 1 | .env 백업 | ✅ 완료 |
| STEP 2 | .env에 newtalk OAuth 키 등록 | ✅ 완료 |
| STEP 3 | venv + 패키지 설치 | ✅ 완료 |
| STEP 4 | OAuth 동의 화면 테스트 사용자 | ⚠️ 대표님 확인 필요 |
| STEP 5–6 | 토큰 발급 시도 (economy / health) | 🔶 인증 URL 출력 완료, 코드 입력 대기 |
| STEP 7 | 결과 확인 | ✅ 완료 |
| STEP 8 | 업로드 테스트 | ⏸️ 토큰 발급 후 실행 (현재 토큰 없음으로 스킵) |

---

## 2. .env 키 등록 결과

- **결과:** 성공  
- **프로젝트:** newtalk (Client ID `651195163214-...`)  
- **확인:** `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` 값 설정됨  
- **주의:** `.env` 절대 git 커밋 금지 (`.gitignore` 포함)

---

## 3. venv + 패키지 설치 결과

- **결과:** 성공  
- **경로:** `/data/shortflow/venv`  
- **패키지:** google-auth, google-auth-oauthlib, google-api-python-client, python-dotenv  
- **검증:** `InstalledAppFlow`, `build` import OK  
- **주의:** `venv/` 절대 git 커밋 금지

---

## 4. OAuth 동의 화면 테스트 사용자

- **위치:** Google Cloud Console (newtalk 프로젝트) → OAuth 동의 화면  
- **필요:** 테스트 사용자에 아래 계정 등록  
  - `oby240610@gmail.com` (3분경제)  
  - `moongo76@gmail.com` (건강한입)  
- **상태:** 서버에서 확인 불가 → **대표님 조치 필요** (미등록 시 인증 불가)

---

## 5. 토큰 발급 결과 및 인증 URL

### 5.1 economy (3분경제 / oby240610@gmail.com)

- **명령:** `venv/bin/python scripts/youtube_oauth_setup.py economy`  
- **결과:** 인증 URL 출력 성공. 토큰 발급은 **인증 코드 입력 후** 완료.

**인증 URL (실제 인증 시에는 서버에서 스크립트 재실행해 나온 URL 사용, state는 매번 변경됨):**

```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=651195163214-mjupn2kn5ere0a77m4sn7qj15z69nidv.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.upload+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube&state=VJgphuWkagasmugZcbxCmCrGKvwsr5&access_type=offline&prompt=consent
```

### 5.2 health (건강한입 / moongo76@gmail.com)

- **명령:** `venv/bin/python scripts/youtube_oauth_setup.py health`  
- **결과:** 인증 URL 출력 성공. 토큰 발급은 **인증 코드 입력 후** 완료.

**인증 URL (실제 인증 시 서버에서 스크립트 재실행 후 출력 URL 사용):**

```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=651195163214-mjupn2kn5ere0a77m4sn7qj15z69nidv.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.upload+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube&state=SYnemeDwWkabt8ScqMKVDTtOopBCRB&access_type=offline&prompt=consent
```

### 5.3 대표님 토큰 발급 절차

1. SSH: `ssh root@114.207.244.86`  
2. economy: `cd /data/shortflow && venv/bin/python scripts/youtube_oauth_setup.py economy`  
   - 출력된 URL을 브라우저에서 열기 → oby240610@gmail.com 로그인 → **3분경제** 채널 선택 → 승인 → 인증 코드 복사 → 서버 터미널에 붙여넣기  
3. health: `venv/bin/python scripts/youtube_oauth_setup.py health`  
   - 출력된 URL 열기 → moongo76@gmail.com 로그인 → **건강한입** 채널 선택 → 승인 → 인증 코드 입력  

---

## 6. STEP 7 결과 확인

- **.env OAuth 키:** 등록 확인  
- **venv 패키지:** google-auth, google-auth-oauthlib, google-api-python-client 등 설치 확인  
- **토큰 파일:** 없음 (인증 코드 미입력으로 미발급)  
- **.gitignore:** `config/youtube_token_*.json`, `venv/` 포함 확인  

---

## 7. STEP 8 업로드 테스트 (토큰 발급 성공 시)

- **현재:** 토큰 없음 → `venv/bin/python scripts/youtube_upload_test.py economy` 실행 시  
  `❌ 3분경제 토큰 없음. 먼저 youtube_oauth_setup.py 실행` 출력  
- **토큰 발급 후:**  
  `venv/bin/python scripts/youtube_upload_test.py economy`  
  - economy 채널에 비공개(private) 1건 업로드  
  - 성공 시 Video ID, URL을 본 보고서 또는 별도 보고에 기록  

---

## 8. 백업 경로

- **경로:** `/data/shortflow/backups/20260225_164025_oauth_newtalk/`  
- **내용:** 작업 전 `.env` 복사본  

---

## 9. 대표님 추가 조치 항목

| 항목 | 조치 |
|------|------|
| OAuth 동의 화면 | 테스트 사용자에 oby240610@gmail.com, moongo76@gmail.com 추가 |
| economy 토큰 | 서버에서 스크립트 실행 → URL 접속(oby240610) → 인증 코드 입력 |
| health 토큰 | 서버에서 스크립트 실행 → URL 접속(moongo76) → 인증 코드 입력 |
| 업로드 테스트 | 토큰 발급 후 `venv/bin/python scripts/youtube_upload_test.py economy` 실행 |

---

## 10. 주의사항

- `config/youtube_token_*.json`, `.env`, `venv/` **절대 git 커밋 금지**  
- 업로드 테스트는 반드시 **private(비공개)** 로 수행  

---

## 11. 푸시 및 동기화 결과

| 항목 | 결과 |
|------|------|
| shortflow 푸시 | ✅ 완료 (main, 1174cac) |
| project-docs 동기화 | ✅ `sync_shortflow.sh` 실행 후 `git pull --rebase` + `git push origin master` 완료 |
| raw URL HTTP 200 | ⚠️ 저장소가 비공개일 경우 raw URL은 인증 없이 404. 브라우저 로그인 후 `https://github.com/moongoby/shortflow/blob/main/docs/reports/20260225_youtube_oauth_newtalk_토큰발급.md` 에서 확인 가능. |
