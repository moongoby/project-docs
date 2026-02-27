# Python 업그레이드 + Gemini 정상화

**일시:** 2026-02-27 10:00 KST  
**서버:** ssh root@114.207.244.86  
**작업 디렉터리:** /data/shortflow

---

## 1. 개요

- **목적:** 시스템 Python 3.8 → 상위 버전 venv 전환, Gemini·YouTube 동작 검수 후 venv 교체.
- **결과:** Python 3.11은 Focal(20.04)에서 미제공 → **Python 3.9**로 venv 재구성 후 교체 완료.

---

## 2. Python 3.11 불가 사유

- **deadsnakes PPA:** 2026년 기준 Noble·Jammy만 패키지 제공. Focal(20.04)에서는 `python3.11` 검색 시 패키지 없음.
- **조치:** 시스템 기본 제공 `python3.9` 설치 후 `python3.9 -m venv venv_new` 로 진행.

```bash
apt install -y python3.9 python3.9-venv python3.9-dev
```

---

## 3. 설치·패키지 과정

| 단계 | 내용 |
|------|------|
| 백업 | `venv/bin/pip freeze > /tmp/requirements_old.txt` (62패키지) |
| venv_new | `python3.9 -m venv venv_new`, `pip install --upgrade pip` |
| 핵심 패키지 | google-generativeai, google-auth, google-auth-oauthlib, google-api-python-client, python-dotenv, requests, edge-tts, aiohttp |
| 전체 패키지 | `requirements_old.txt` 고정 버전 시 cffi/cryptography 충돌 → 패키지 이름만 추출 후 `pip install -r` (호환 버전으로 설치) |

---

## 4. 검수 결과

### 4.1 Gemini

- **모델:** 스크립트의 `gemini-2.0-flash`는 "no longer available to new users" 로 404. 사용 가능 모델 목록 조회 후 **gemini-2.5-flash** 로 검수.
- **결과:** ✅ 정상 응답 (한국 경제 뉴스 3줄 요약).

```bash
venv/bin/python -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')
resp = model.generate_content('한국 경제 뉴스 3줄 요약해줘')
print(resp.text[:200])
"
```

- **참고:** 코드에서 `gemini-2.0-flash` 를 쓰는 부분이 있으면 `gemini-2.5-flash` 등 사용 가능 모델로 변경 필요.

### 4.2 YouTube (economy)

- **결과:** ✅ `config/youtube_token_economy.json` 기준 채널 조회 성공 (채널명: 3분경제).

---

## 5. venv 교체 및 정리

- `mv venv venv_old` → `mv venv_new venv`
- **교체 후:** `venv/bin/python --version` → **Python 3.9.5**
- `rm -rf venv_test` 실행으로 venv_test 정리 완료.

---

## 6. 정리

- **현재 venv:** Python 3.9.5, 기존 62개 패키지 호환 설치 완료.
- **Gemini:** gemini-2.5-flash 기준 검수 통과. 구 모델명 사용 구간은 필요 시 모델명 업데이트 권장.
- **YouTube:** economy 토큰·채널 조회 정상.
- **Python 3.11** 사용이 필수이면 Ubuntu 업그레이드(Noble/Jammy) 또는 pyenv/소스 빌드 검토.
