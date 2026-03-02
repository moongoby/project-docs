# CUR-NASIMG-P2-PIPCACHE-FIX-20260226

**제목:** google-generativeai pip-cache 추가 및 Docker 오프라인 빌드 수정  
**작성일시:** 2026-02-26 (목) 14:10 KST  
**작업 유형:** P2-PIPCACHE-FIX  
**프로젝트:** https://github.com/moongoby/newtalk-image-auto (main)  
**서버:** NAS [NAS-IP]:[NAS-SSH-PORT], 사용자 newtalk

---

## 1. 문제

- Docker 빌드 시 `--no-index` (오프라인) 모드로 `pip install` 수행
- `google-generativeai>=0.8.0` 및 의존성 whl이 `pip-cache/`에 없어 빌드 실패

---

## 2. 해결 조치

### 2.1 STEP 1·4: pip-cache·Dockerfile 확인

- **pip-cache:** 기존에 mediapipe, rembg, opencv 등 whl 존재, **google-generativeai 관련 없음**
- **Dockerfile:** `pip install --no-index --find-links=/tmp/pip-cache/ -r requirements.txt` 사용 확인

### 2.2 STEP 2: google-generativeai + 의존성 whl 다운로드

- **실행 위치:** 로컬 PC (Windows), 워크스페이스 `z:\newtalk-image-auto` (NAS SMB 매핑 동일 저장소)
- **방법:** 작업지시서 STEP 2-B 방법 B — 로컬에서 `pip download` 후 `pip-cache/`에 저장

```powershell
cd z:\newtalk-image-auto
pip download "google-generativeai>=0.8.0" --dest pip-cache --python-version 3.11 --platform manylinux2014_x86_64 --only-binary=:all:
```

- **결과:** 다음 whl이 `pip-cache/`에 추가됨  
  - `google_generativeai-0.8.6-py3-none-any.whl`  
  - `google_ai_generativelanguage-0.6.15-py3-none-any.whl`  
  - `google_api_core-2.30.0-py3-none-any.whl`  
  - `google_api_python_client-2.190.0-py3-none-any.whl`  
  - `google_auth-2.48.0-py3-none-any.whl`  
  - `google_auth_httplib2-0.3.0-py3-none-any.whl`  
  - `googleapis_common_protos-1.72.0-py3-none-any.whl`  
  - `grpcio-1.78.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl`  
  - `grpcio_status-1.71.2-py3-none-any.whl`  
  - `proto_plus-1.27.1-py3-none-any.whl`  
  - `protobuf-5.29.6-cp38-abi3-manylinux2014_x86_64.whl` (google-api-core 의존용)  
  - 기타: certifi, cryptography, httplib2, pyasn1, pyasn1_modules, rsa, uritemplate, pyparsing 등

### 2.3 STEP 3: 병합

- 다운로드 시 `--dest pip-cache`로 직접 저장하여 별도 병합 불필요

### 2.4 requirements.txt 정리

- `# TODO: NAS 오프라인 빌드 시 pip download ...` 주석 제거

---

## 3. NAS 측 후속 작업 (수행자 확인)

- **STEP 5:** DSM 작업 스케줄러에서 `docker-rebuild` 실행  
  - `cd /volume1/뉴톡/newtalk-image-auto`  
  - `docker-compose down` → `docker-compose build --no-cache` → `docker-compose up -d`  
  - 로그: `build_log.txt`, `env_log.txt`

- **STEP 6:** 결과 확인  
  - `build_log.txt`에 ERROR 없음  
  - `env_log.txt`에 GEMINI 환경변수·헬스·/api/sort/status/662 JSON 응답 확인

---

## 4. 완료 조건 체크리스트

| # | 항목 | 상태 |
|---|------|------|
| 1 | pip-cache/에 google-generativeai whl + 의존성 존재 | ✅ 완료 |
| 2 | docker-compose build 성공 (ERROR 없음) | NAS 재빌드 후 확인 |
| 3 | env_log.txt에 GEMINI 환경변수 확인 | NAS 재빌드 후 확인 |
| 4 | /api/sort/status/662 → JSON 응답 | NAS 재빌드 후 확인 |
| 5 | 보고서 커밋 완료 | 진행 예정 |

---

## 5. 참고

- **Private 보고서:** `docs/reports/CUR-NASIMG-P2-PIPCACHE-FIX-20260226.md`
- **Public 보고서:** `project-docs/nas-image/reports/CUR-NASIMG-P2-PIPCACHE-FIX-20260226.md`
- pip-cache whl은 git 포함 가능(오프라인 빌드 필수). `.env` 및 비밀번호 커밋 금지.
- NAS에서 `pip download`가 SSL 등으로 실패할 경우 `--trusted-host pypi.org --trusted-host files.pythonhosted.org` 또는 본 작업처럼 로컬 PC에서 다운로드 후 저장소 반영.
