# Python 3.11 업그레이드 + Gemini 정상화

**일시:** 2026-02-27 KST  
**작업:** 병렬3/4

## 설치 과정
- **현재 환경**: Python 3.8.10 (시스템·venv 동일). 백업 완료: `backups/20260227_*_python_upgrade/` (requirements_old.txt 62패키지, .env).
- **Python 3.11 설치**: `apt install python3.11`, `venv_new` 생성·패키지 설치·Gemini/LLM/YouTube 검수·venv 교체는 **서버(ssh root@114.207.244.86)에서 실행 필요**. 로컬/다른 호스트에서는 apt·venv 교체 생략.

## 패키지 호환성
- requirements_old.txt 기준 62개 패키지. google-generativeai, google-auth, google-api-python-client 등 호환 시 venv_new에 설치 후 검수 진행.

## Gemini 직접 호출 결과
- (서버에서 venv_new 생성 후 `venv_new/bin/python -c "import google.generativeai as genai; ..."` 실행하여 기록)

## LLM 검수 / YouTube 검수 / 교체 결과
- (서버에서 5,6,7 단계 성공 시 venv → venv_old, venv_new → venv 교체 후 기록)

**※ 병렬3 완료를 위해 서버 접속 후 스크립트 블록(apt, venv_new, 검수, 교체) 실행 권장.**
