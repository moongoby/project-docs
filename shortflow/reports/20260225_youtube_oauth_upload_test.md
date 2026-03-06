# YouTube OAuth 토큰 발급 + 업로드 테스트 보고서

**일시**: 2026-02-25 KST  
**서버**: ssh root@114.207.244.86  
**작업 디렉터리**: /data/shortflow  

---

## 1. 요약

| 항목 | 결과 |
|------|------|
| .env OAuth 키 | **키 존재, 값 비어 있음** → 대표님 조치 필요 |
| OAuth 토큰 발급 (economy/health) | **미실행** (키 없음 + 서버 Python/OpenSSL 이슈) |
| 업로드 테스트 | **미실행** (토큰 없음) |
| 스크립트/설정 | ✅ `scripts/youtube_oauth_setup.py`, `scripts/youtube_upload_test.py` 생성 완료, `.gitignore`에 `config/youtube_token_*.json` 추가 |

---

## 2. .env OAuth 키 확인

```bash
grep -E "YOUTUBE_CLIENT" .env
```

**결과:**
```
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_CLIENT_SECRET_PATH=/data/shortflow/credentials/client_secret.json
```

- `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` **변수는 있으나 값이 비어 있음**.
- 토큰 발급 및 업로드 테스트를 진행하려면 **대표님이 Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성한 뒤 .env에 값을 채워 넣어야 합니다.**

---

## 3. 대표님 조치 필요 (Google Cloud Console)

아래 순서로 진행 후 `.env`에 반영해 주세요.

1. **https://console.cloud.google.com** 접속 → 기존 ShortFlow 사용 프로젝트 선택  
2. **API 및 서비스** → **사용자 인증 정보** → **OAuth 2.0 클라이언트 ID 만들기**  
3. **애플리케이션 유형**: "데스크톱 앱"  
4. **이름**: "ShortFlow YouTube Uploader" (또는 원하는 이름)  
5. 생성 후 **클라이언트 ID**와 **클라이언트 보안 비밀** 복사  
6. 서버 `/data/shortflow/.env` 수정:
   ```bash
   YOUTUBE_CLIENT_ID=복사한_클라이언트_ID
   YOUTUBE_CLIENT_SECRET=복사한_클라이언트_보안_비밀
   ```

이후 서버에서 아래 순서로 다시 실행하면 됩니다.

```bash
cd /data/shortflow
python3 scripts/youtube_oauth_setup.py economy   # 콘솔에 나온 URL로 대표님이 브라우저 인증
python3 scripts/youtube_oauth_setup.py health
python3 scripts/youtube_upload_test.py economy   # 비공개 1건 업로드 테스트
```

---

## 4. 서버 Python/OpenSSL 환경 이슈 (참고)

현재 서버에서 `pip` / `python3` 실행 시 **시스템 OpenSSL(pyOpenSSL) 호환 문제**로 다음 오류가 발생합니다.

```
AttributeError: module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'
```

- **영향**: `google-auth`, `google-auth-oauthlib`, `requests` 등이 시스템 `requests`/`urllib3`/`OpenSSL`을 쓰면서 import 단계에서 실패합니다.  
- **결과**: OAuth 키를 .env에 채워 넣어도, 해당 환경에서는 `youtube_oauth_setup.py` 실행이 같은 오류로 막힐 수 있습니다.

**권장 대응:**

1. **가상환경(venv) 사용**  
   - `python3 -m venv /data/shortflow/venv` 후 `venv/bin/pip install google-auth google-auth-oauthlib google-api-python-client python-dotenv`  
   - 이후 `venv/bin/python scripts/youtube_oauth_setup.py economy` 등으로 실행  
2. 또는 **시스템 pyOpenSSL/OpenSSL 업데이트**  
   - 배포/보안 정책에 맞게 libssl / pyopenssl 버전 정리 후 pip 재설치  

OAuth 키 설정까지 완료된 뒤에도 위 오류가 나오면, 위와 같이 venv 또는 OpenSSL 정리를 먼저 진행한 뒤 동일 스크립트를 다시 실행하면 됩니다.

---

## 5. 수행한 작업 내역

- [x] 백업: `/data/shortflow/backups/20260225_153108_oauth` 생성, `config/` 복사  
- [x] `scripts/youtube_oauth_setup.py` 생성 (2채널: economy=3분경제, health=건강한입)  
- [x] `scripts/youtube_upload_test.py` 생성 (private 업로드 1건 테스트)  
- [x] `.gitignore`에 `config/youtube_token_*.json` 추가 확인 (토큰 파일 커밋 방지)  
- [ ] 의존성 설치: 시스템 pip/pyOpenSSL 오류로 `pip install` 실패 → venv 또는 환경 수정 후 재시도 필요  
- [ ] OAuth 토큰 발급: .env 키 값 없음 + 위 환경 이슈로 미실행  
- [ ] 업로드 테스트: 토큰 없음으로 미실행  

---

## 6. 실패 시 에러 메시지 (기록용)

### 6.1 .env 키 없을 때 스크립트 기대 동작

- `youtube_oauth_setup.py` 실행 시 `get_client_config()`에서  
  `❌ .env에 YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET 없음` 출력 후 `sys.exit(1)`.

### 6.2 현재 서버에서 실제 발생한 오류 (import 단계)

```
File "scripts/youtube_oauth_setup.py", line 13, in <module>
    from google_auth_oauthlib.flow import InstalledAppFlow
  ...
  File "/usr/lib/python3/dist-packages/OpenSSL/crypto.py", line 1571, in X509StoreFlags
    NOTIFY_POLICY = _lib.X509_V_FLAG_NOTIFY_POLICY
AttributeError: module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'
```

---

## 7. 다음 단계 (체크리스트)

1. **대표님**: Google Cloud Console에서 OAuth 2.0 데스크톱 앱 클라이언트 생성 후 `.env`에 `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` 설정  
2. **서버**: (필요 시) venv 생성 및 의존성 설치, 또는 OpenSSL/pyOpenSSL 정리  
3. **서버**: `python3 scripts/youtube_oauth_setup.py economy` → 출력된 URL로 브라우저 인증 (3분경제 계정)  
4. **서버**: `python3 scripts/youtube_oauth_setup.py health` → 동일 방식으로 건강한입 계정 인증  
5. **서버**: `ls -la config/youtube_token_*.json`으로 토큰 파일 생성 확인  
6. **서버**: `python3 scripts/youtube_upload_test.py economy` 로 비공개 업로드 1건 테스트  
7. 테스트 완료 후 필요 시 본 보고서에 **업로드 결과(Video ID, URL, 상태)** 보완  

---

**보고서 작성**: 2026-02-25  
**채널 정보**: 3분경제 UC1qhhty2MDsF4worImq6-dQ (oby240610@gmail.com), 건강한입 UCKRf4X2fOwhTGcKSVO8rLYQ (moongo76@gmail.com)
