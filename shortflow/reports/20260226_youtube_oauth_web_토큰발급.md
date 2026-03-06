# YouTube OAuth 웹 클라이언트 키 교체 + 토큰 발급

**작성일시:** 2026-02-26 10:45 KST  
**서버:** ssh root@114.207.244.86  
**작업 디렉터리:** /data/shortflow  
**관련 파일:** `.env`, `scripts/youtube_oauth_setup.py`, `config/youtube_token_*.json`

---

## 1. 개요

- **목적:** 웹 애플리케이션용 Google OAuth 클라이언트로 전환하고, 리다이렉트 URI를 `http://shotflow.newtalk.kr:8090`으로 고정하여 토큰 발급·갱신을 안정화.
- **변경 요약:**  
  - `.env`: `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` → 웹 앱 클라이언트 값으로 교체  
  - `youtube_oauth_setup.py`: `InstalledAppFlow` + localhost/IP → `Flow`(웹) + `REDIRECT_URI = "http://shotflow.newtalk.kr:8090"`, 포트 8090에서 콜백 수신

---

## 2. STEP 1: 백업

| 항목 | 경로 |
|------|------|
| 백업 디렉터리 | `/data/shortflow/backups/20260226_104911_oauth_web` |
| 백업된 파일 | `.env`, `scripts/youtube_oauth_setup.py` |

복원 시: `cp backups/20260226_104911_oauth_web/.env .env` 등으로 복구 가능.

---

## 3. STEP 2: .env 키 교체 (웹 애플리케이션 클라이언트)

- **적용 내용:**
  - `YOUTUBE_CLIENT_ID` → `(.env 에서 관리, 문서에 기재하지 않음)`
  - `YOUTUBE_CLIENT_SECRET` → `(.env 에서 관리, 문서에 기재하지 않음)`
- **확인:** `grep -E "YOUTUBE_CLIENT" .env` 로 위 값이 반영되었는지 확인 완료.

---

## 4. STEP 3: 스크립트 수정 (웹 애플리케이션 + shotflow.newtalk.kr redirect)

| 구분 | 기존 (InstalledApp) | 변경 후 (Web) |
|------|---------------------|----------------|
| 클라이언트 타입 | `installed` + `InstalledAppFlow` | `web` + `Flow.from_client_config()` |
| redirect_uri | `http://localhost:8090`, `http://114.207.244.86:8090` | `http://shotflow.newtalk.kr:8090` |
| 콜백 수신 | `flow.run_local_server(...)` | `HTTPServer(("0.0.0.0", PORT), OAuthHandler)` → `flow.fetch_token(code=auth_code)` |

- **동작:** 스크립트 실행 시 포트 8090에서 콜백 대기 → 사용자가 출력된 인증 URL을 브라우저에서 열고 로그인·승인 → `http://shotflow.newtalk.kr:8090?...&code=...` 로 리다이렉트되면 스크립트가 `code`를 받아 토큰 발급·저장.
- **Google Cloud Console:** OAuth 2.0 클라이언트(웹 애플리케이션)에 **승인된 리디렉션 URI** 로 `http://shotflow.newtalk.kr:8090` 이 등록되어 있어야 함.

---

## 5. STEP 4: 포트 8090 및 방화벽

서버에서 실행:

```bash
ss -tlnp | grep 8090 || echo "✅ 포트 8090 사용 가능"
iptables -L INPUT -n | grep 8090 || iptables -I INPUT -p tcp --dport 8090 -j ACCEPT
```

- 8090이 이미 사용 중이면 해당 프로세스 확인 후 정리.
- 방화벽에 8090 허용 규칙이 없으면 위 `iptables -I` 로 추가.

---

## 6. STEP 5–6: 토큰 발급 실행

**economy (3분경제):**

```bash
cd /data/shortflow
venv/bin/python scripts/youtube_oauth_setup.py economy
```

- 출력된 URL을 브라우저에서 열기 → **oby240610@gmail.com** 로그인 → **3분경제** 채널 선택 → 승인.
- 서버가 인증 코드를 자동 수신 후 `config/youtube_token_economy.json` 저장.

**health (건강한입):** economy 완료 후

```bash
venv/bin/python scripts/youtube_oauth_setup.py health
```

- **moongo76@gmail.com** 로그인 → **건강한입** 채널 선택 → 승인.
- `config/youtube_token_health.json` 저장.

---

## 7. STEP 7: 결과 확인

```bash
echo "=== 토큰 파일 ==="
ls -la config/youtube_token_*.json

echo "=== .gitignore ==="
grep -E "youtube_token|venv" .gitignore
```

- `config/youtube_token_*.json`, `venv/`, `.env` 는 **절대 git 커밋 금지** (.gitignore에 포함됨).

---

## 8. STEP 8: 업로드 테스트 (토큰 발급 성공 시)

```bash
venv/bin/python scripts/youtube_upload_test.py economy
```

- 정상 시 economy 채널에 테스트 업로드 또는 채널 정보 조회가 동작하는지 확인.

---

## 9. 정리 및 주의사항

- **shortflow 푸시:** 이 보고서 및 `scripts/youtube_oauth_setup.py` 변경만 커밋·푸시. `config/youtube_token_*.json`, `.env`, `venv/` 는 커밋하지 않음.
- **project-docs 동기화:** 필요 시 shortflow 푸시 후 raw URL 등 문서 위치 확인.
- **보안:** 클라이언트 시크릿·토큰 파일이 저장소나 외부에 노출되지 않도록 유지.
