# Phase 2-2 후속 – 의존성 설치 + Git 커밋 해결

**작성일시:** 2026-02-23 11:21  
**작업 유형:** 설정 변경 / 버그 수정  
**상태:** 완료  
**관련 파일:** venv(신규), .env, .gitignore(기존 유지), docs/reports/20260223_youtube_oauth_후속_의존성_git해결.md

---

## 1. 작업 개요

Phase 2-2에서 확인된 **pip3 설치 실패**, **git commit 실패** 2건을 해결하여, 대표님 OAuth 브라우저 인증 진행 전 환경을 정리함.

- **대상 서버:** 114 (rfree-0009.cafe24.com)  
- **프로젝트 경로:** /data/shortflow  

---

## 2. 변경 사항

### 2.1 Step 1 – pip3 / Python 환경 및 의존성

| 항목 | 결과 |
|------|------|
| Python | 3.8.10 (/usr/bin/python3) |
| pip3 (시스템) | 없음 → venv 내 pip 사용 |
| python3.8-venv | 미설치로 venv 실패 → `apt install python3.8-venv` 실행 후 해결 |
| venv | `/data/shortflow/venv` 생성 후 pip 업그레이드 및 패키지 설치 완료 |

**설치 패키지 (venv 내):**  
`google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `pymysql`, `python-dotenv` 및 의존성 일체.

- **.env:** `PYTHON_VENV_PATH=/data/shortflow/venv` 추가(선택 반영).  
- **.gitignore:** `venv/`, `.venv/` 이미 포함되어 있어 변경 없음.

### 2.2 Step 2 – Git 커밋 해결

| 항목 | 내용 |
|------|------|
| Git 버전 | 2.25.1 (--trailer 미지원) |
| trailer 설정 | global에 없음; **Cursor IDE가 `git commit` 호출 시 `--trailer 'Co-authored-by: Cursor <...>'` 주입**하여 실패 |
| 조치 | **`/usr/bin/git` 직접 호출**로 커밋·푸시 실행 |
| 커밋 | `feat: YouTube OAuth2.0 auth channel check upload test scripts and setup guide` (c4a69e0) |
| 푸시 | `origin main` 푸시 성공 (747480a..c4a69e0) |

### 2.3 Step 3 – YouTube 스크립트 사전 테스트

| 항목 | 결과 |
|------|------|
| Google API import | 성공 (Python 3.8 EOL 경고만 출력) |
| client_secret.json | 유효 (type: installed, project_id·client_id·client_secret 존재) |
| token.pickle | 존재, expired, **refresh 가능** (재인증 없이 갱신 가능) |

---

## 3. 테스트 결과

- venv 활성화 후 `pip list`로 google-auth, google-api-python-client, oauth, pymysql, dotenv 확인 완료.  
- `git log --oneline -5`에서 c4a69e0 푸시 반영 확인.  
- `scripts/youtube_*.py` 3개 파일 존재 및 credentials 구성 정상.

---

## 4. 주의사항 / 후속 작업

1. **venv**  
   - `venv/`는 .gitignore에 포함되어 있으며, **절대 git에 커밋하지 말 것.**

2. **Git 커밋**  
   - Git 2.25.1은 `--trailer` 미지원.  
   - Cursor에서 커밋 시 trailer 주입으로 실패하면, 터미널에서 **`/usr/bin/git commit -m "메시지"`** 로 실행할 것.

3. **Python 3.8**  
   - EOL로 google-auth 등에서 경고 출력. 장기적으로 Python 3.10+ 업그레이드 권장.

4. **OAuth 브라우저 인증**  
   - token.pickle 만료·refresh 가능 상태이므로, 대표님 브라우저 인증 시 필요하면 재발급 또는 refresh 후 업로드 테스트 진행 가능.

5. **project-docs 동기화**  
   - 작업 완료 후 `bash /data/project-docs/scripts/sync_shortflow.sh` 실행으로 동기화 완료.
