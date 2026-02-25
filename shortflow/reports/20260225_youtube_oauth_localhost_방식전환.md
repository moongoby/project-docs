# YouTube OAuth: OOB 방식 폐기 → localhost redirect 방식 전환

**작성일시:** 2026-02-25 KST  
**서버:** ssh root@114.207.244.86  
**작업 디렉터리:** /data/shortflow  
**관련 파일:** `scripts/youtube_oauth_setup.py`, `scripts/youtube_oauth_setup.py.bak`

---

## 1. 전환 사유 (OOB 폐기 → localhost redirect)

- **OOB(Out-of-Band) 방식 폐기:** Google이 `urn:ietf:wg:oauth:2.0:oob` 및 “localhost” 리디렉션 없이 표시되는 인증 코드 방식을 단계적으로 폐기·제한하고 있음. 장기적으로는 리디렉션 URI 기반 방식만 지원 예정.
- **localhost redirect 방식 채택:** 서버에서 `run_local_server(host="0.0.0.0", port=8090)`로 임시 콜백 서버를 띄우고, 브라우저에서 `http://114.207.244.86:8090`으로 접속해 리다이렉트를 받으면 코드 복사·붙여넣기 없이 토큰 발급이 완료됨.
- **효과:** 대표님이 URL만 열고 로그인·승인하면 곧바로 토큰 발급 완료. 인증 코드를 수동으로 복사해 서버에 붙여넣는 단계 제거.

---

## 2. 스크립트 수정 내용

| 구분 | 기존 (OOB) | 변경 후 (localhost redirect) |
|------|------------|------------------------------|
| `redirect_uris` | `["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]` | `["http://localhost:8090", "http://114.207.244.86:8090"]` |
| 인증 흐름 | `flow.authorization_url()` → URL 출력 → `input("인증 코드 입력")` → `flow.fetch_token(code=...)` | `flow.run_local_server(host="0.0.0.0", port=8090, open_browser=False)` |
| 사용자 조작 | URL 열기 → 코드 복사 → 터미널에 붙여넣기 | URL 열기 → 로그인·승인 → 자동 리다이렉트로 완료 |

- **백업:** `scripts/youtube_oauth_setup.py.bak` 에 기존 스크립트 보관.
- **동작 요약:**  
  - 서버에서 스크립트 실행 시 포트 8090에서 임시 웹 서버 대기.  
  - 브라우저에서 출력된 URL 또는 `http://114.207.244.86:8090` 접속 → Google 로그인·채널 승인 → `http://114.207.244.86:8090?...` 로 리다이렉트되며 스크립트가 인증 코드를 받아 토큰 발급·저장.

---

## 3. 포트 8090 확인 결과

- **확인 명령:** `ss -tlnp | grep 8090`
- **결과:** 8090 포트 선점 프로세스 없음 → **포트 8090 사용 가능** 확인.

---

## 4. 방화벽

- **조치:** `iptables -I INPUT -p tcp --dport 8090 -j ACCEPT` 실행하여 8090 허용 규칙 추가.
- **참고:** 재부팅 시 iptables 규칙이 사라질 수 있음. 영구 반영이 필요하면 배포/방화벽 정책에 8090 허용을 추가할 것.

---

## 5. 대표님 조치 필요 (Google Cloud Console 리디렉션 URI)

**스크립트 실행 전에 반드시 아래 URI를 등록해야 합니다.**

1. **Google Cloud Console** 접속 → **newtalk** 프로젝트 선택.
2. **APIs 및 서비스** → **사용자 인증 정보** → **ShortFlow** OAuth 2.0 클라이언트 ID 클릭.
3. **승인된 리디렉션 URI**에 아래 두 개를 **추가** 후 **저장**.
   - `http://localhost:8090`
   - `http://114.207.244.86:8090`

리디렉션 URI 저장 후에만 서버에서 스크립트를 실행해 토큰 발급을 진행할 수 있습니다.

---

## 6. 토큰 발급 실행 절차 (리디렉션 URI 추가 후)

1. **서버 접속**
   ```bash
   ssh root@114.207.244.86
   cd /data/shortflow
   ```

2. **3분경제 채널 토큰 발급**
   ```bash
   venv/bin/python scripts/youtube_oauth_setup.py economy
   ```
   - 터미널에 출력되는 URL을 브라우저에서 연다.
   - **oby240610@gmail.com** 로그인 → **3분경제** 채널 선택 → 승인.
   - 자동으로 `http://114.207.244.86:8090` 으로 리다이렉트되며 토큰 발급 완료.

3. **건강한입 채널 토큰 발급**
   ```bash
   venv/bin/python scripts/youtube_oauth_setup.py health
   ```
   - **moongo76@gmail.com** 로그인 → **건강한입** 채널 선택 → 승인.
   - 동일하게 리다이렉트로 토큰 발급 완료.

4. **두 채널 한 번에**
   ```bash
   venv/bin/python scripts/youtube_oauth_setup.py
   ```
   - economy → health 순으로 위와 동일한 흐름 진행.

---

## 7. 요약

| 항목 | 내용 |
|------|------|
| OOB 방식 | 폐기, 스크립트에서 제거 |
| 인증 방식 | localhost redirect (포트 8090) |
| 포트 8090 | 사용 가능 확인, 방화벽 허용 완료 |
| 대표님 조치 | Google Console에 `http://localhost:8090`, `http://114.207.244.86:8090` 리디렉션 URI 추가 |
| 실행 | 리디렉션 URI 추가 후 `venv/bin/python scripts/youtube_oauth_setup.py economy` 또는 `health` |

---

*작성: 2026-02-25 | 서버: 114.207.244.86*
