# [병렬2/4] Python 3.10+ 업그레이드 + Gemini SDK 정상화

**작성일시:** 2026-02-26 20:10 KST  
**서버:** ssh root@[SERVER-IP]  
**작업 디렉터리:** /data/shortflow  
**관련:** `venv`, `venv_test`, `pyenv`, `requirements*.txt`, `.env`

---

## 1. 개요

- **목적:** Python 3.10+ 환경 구축 및 `google-generativeai`(Gemini) SDK 정상 동작 확인. 기존 venv/크론/서비스는 유지한 채 신규 venv로만 테스트.
- **결과 요약:**
  - 시스템 Python: **3.8.10** 유지.
  - **pyenv**로 **Python 3.11.14** 설치 완료.
  - **venv_test**(Python 3.11) 생성 및 의존성 설치 성공.
  - **Gemini SDK** (`google-generativeai` 0.8.6) **정상 동작** 확인. API 호출 시 403은 **API 키 유출 신고**로 인한 차단(키 교체 필요).
  - **실제 venv 교체는 수행하지 않음.** 아래 교체 계획만 수립. 대표님 승인 후 진행.

---

## 2. 백업

| 항목 | 경로 |
|------|------|
| 백업 디렉터리 | `/data/shortflow/backups/20260226_201016_python_upgrade` |
| 백업된 파일 | `.env`, `requirements_old.txt`(pip freeze), `vendor.txt` |

복원 시: `cp backups/20260226_201016_python_upgrade/.env .env` 등으로 복구 가능.

---

## 3. 현재 Python 버전 (작업 전)

| 구분 | 버전/경로 |
|------|-----------|
| 시스템 `python3` | Python 3.8.10 (`/usr/bin/python3` → `python3.8`) |
| 기존 venv | Python 3.8.10 |
| `/usr/bin/python3*` | `python3`, `python3.8` 만 존재 |

---

## 4. Python 3.10+ 설치 가능 여부

- **apt (Ubuntu 20.04 focal):**
  - 기본 저장소: `python3.10`, `python3.11` 패키지 없음.
  - **deadsnakes PPA** 추가: `add-apt-repository -y ppa:deadsnakes/ppa` 실행 완료.
  - **이슈:** PPA 추가 후 `apt update` 시 `ppa.launchpad.net_deadsnakes_ppa_ubuntu_dists_focal_InRelease` 만 존재하고, `main/binary-amd64/Packages` 등 패키지 인덱스가 내려받아지지 않음.  
    → `apt install python3.11` 시 **Unable to locate package python3.11** 발생.
- **대안 채택:** **pyenv**로 소스 빌드 설치.

---

## 5. pyenv 설치 및 Python 3.11.14 빌드

- **pyenv 설치:** `curl -sL https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash`  
  - 설치 경로: `~/.pyenv` (root 기준 `/root/.pyenv`)
- **빌드 의존성:** `build-essential`, `libssl-dev`, `zlib1g-dev`, `libbz2-dev`, `libreadline-dev`, `libsqlite3-dev`, `libncursesw5-dev`, `xz-utils`, `tk-dev`, `libffi-dev`, `liblzma-dev` 설치함.  
  - `libxml2-dev`, `libxmlsec1-dev` 는 기존 패키지 충돌로 제외.
- **Python 설치:** `pyenv install -v 3.11.14`  
  - 설치 경로: `/root/.pyenv/versions/3.11.14/bin/python`  
  - 소스 빌드로 약 65초 소요.

---

## 6. 신규 venv 테스트 (venv_test)

- **생성:** `/root/.pyenv/versions/3.11.14/bin/python -m venv venv_test`  
  → `venv_test/bin/python` → Python 3.11.14
- **pip 업그레이드:** 24.0 → 26.0.1
- **의존성 설치:** `backups/20260226_201016_python_upgrade/requirements_old.txt` 기준 설치 시:
  - **제거한 항목:**  
    - `pkg_resources==0.0.0` (PyPI에 해당 버전 없음, setuptools 내장 사용).  
    - `cffi==1.17.1` (고정 시 `cryptography 46.0.5` 의 `cffi>=2.0.0` 와 충돌).
  - 수정된 리스트로 `pip install -r` 실행 → **설치 성공**.
- **google-generativeai:**  
  - 기존 요구사항: `google-generativeai==0.1.0rc1` (구 API, `GenerativeModel` 없음).  
  - **업그레이드:** `pip install --upgrade 'google-generativeai>=0.8.0'` → **0.8.6** 설치.  
  - `import google.generativeai as genai` 및 `genai.GenerativeModel`, `model.generate_content()` **정상 동작**.

---

## 7. Gemini 호출 테스트 결과

- **테스트 코드 (venv_test):**
  - `genai.configure(api_key="[.env:GEMINI_API_KEY]")`
  - `model = genai.GenerativeModel('gemini-2.0-flash')`
  - `resp = model.generate_content('한국 경제 뉴스 3줄 요약')`
- **결과:**
  - **SDK 동작:** 요청이 API까지 전달됨.
  - **HTTP/API:** `403 Your API key was reported as leaked. Please use another API key.`  
    → **API 키가 유출로 신고되어 차단된 상태.** SDK/코드 문제 아님. **새 API 키 발급·교체 후** 동일 코드로 재테스트 필요.
- **참고:** `google.generativeai` 패키지는 deprecated 경고가 있으며, 장기적으로 `google.genai` 로 이전이 권장됨. 당장 venv 교체 시에는 기존 `google-generativeai` 0.8.x 로도 동작 가능.

---

## 8. venv 교체 계획 (실행 보류)

실제 교체는 **이번 작업에서 하지 않음.** 대표님 승인 후 아래 순서로 진행 권장.

| 단계 | 작업 | 비고 |
|------|------|------|
| 1 | 기존 `venv` → `venv_old` 로 리네임 | `mv venv venv_old` |
| 2 | `venv_test` → `venv` 로 리네임 | `mv venv_test venv` |
| 3 | 크론/시스템드 등에서 `venv/bin/python`, `venv/bin/pip` 경로 사용 여부 확인 | 절대 경로 사용 시 변경 불필요 |
| 4 | 대표 스크립트로 동작 검증 (예: `venv/bin/python scripts/generate_content_script.py --channel economy --dry-run`) | LLM 호출은 API 키 교체 후 테스트 |
| 5 | 실패 시 롤백 | `mv venv venv_test; mv venv_old venv` |

**주의:**  
- **pyenv**에 의존하지 않도록 하려면, 교체 후 `venv` 가 **절대 경로의 Python 바이너리**를 참조하는지 확인.  
  현재 `venv_test` 는 `/root/.pyenv/versions/3.11.14/bin/python` 를 가리키므로, pyenv 제거 시 venv가 깨질 수 있음.  
  → 서버에서 Python 3.11을 계속 쓸 경우 **pyenv 유지** 또는 나중에 **apt로 python3.11 설치 가능해지면** 해당 경로로 venv 재생성 검토.

---

## 9. 리스크 및 정리

| 리스크 | 내용 | 대응 |
|--------|------|------|
| API 키 403 | 현재 GEMINI_API_KEY 가 유출 신고로 차단됨 | Google Cloud Console에서 새 키 발급 후 `.env` 교체 |
| requirements 변경 | `pkg_resources` 제거, `cffi` 버전 고정 완화 | 필요 시 `requirements.txt` 에 반영 후 다른 환경과 동기화 |
| pyenv 의존 | venv가 pyenv 설치 경로의 Python을 참조 | pyenv 삭제하지 않거나, 추후 apt/python 공식 빌드로 venv 재구성 |
| deprecated SDK | `google.generativeai` → `google.genai` 이전 권장 | 당분간 0.8.x 유지 가능, 추후 마이그레이션 검토 |

---

## 10. 다음 액션

1. **대표님 승인** 후 위 **venv 교체 계획**대로 `venv` ↔ `venv_test` 교체 진행.
2. **GEMINI_API_KEY** 새로 발급 후 `.env` 에 반영, `venv/bin/python` 으로 Gemini 호출 재테스트.
3. (선택) `requirements.txt` 에서 `pkg_resources`, `cffi` 고정 제거 반영 후 저장소에 커밋.

---

*문서 레포 raw URL: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/20260226_병렬2_Python업그레이드_Gemini정상화.md*
