# CUR-NASIMG-BUG-FIX-001-20260224

**제목:** QC 프리셋 등록 오류 수정  
**작성일시:** 2026-02-24 KST  
**작업 유형:** BUG-FIX  
**증상:** 등록 버튼 클릭 시 폼만 리셋되고 목록에 미등록

---

## 1. 원인 분석

### 1.1 증상
- 사용자가 톤 프리셋 등록 페이지에서 이미지·이름 등 입력 후 **등록** 클릭
- 폼 필드가 비워짐(리셋된 것처럼 보임)
- 프리셋 목록(`/qc/presets`)에는 새 항목이 나타나지 않음

### 1.2 근본 원인
1. **폼 기본 제출(Native submit)**  
   - `<form>`에 `onsubmit` 방어가 없어, JS 오류·로딩 실패 시 브라우저가 폼을 **현재 URL로 GET 제출**  
   - 그 결과 **같은 페이지(`/qc/presets/register`)가 다시 로드**되어 입력값이 사라짐  
   - `POST /api/preset/register`는 호출되지 않음 → DB에 저장되지 않음

2. **목록 썸네일 미표시(부가)**  
   - `list_presets` API는 `image_path`, `thumbnail_path`(파일 경로)만 반환  
   - 프론트는 `thumbnail_url`/`image_url`만 사용해 썸네일을 그려서, 신규 등록 프리셋도 이미지가 빈 칸으로 보일 수 있음

3. **수정 페이지 컨텍스트 미주입(부가)**  
   - 수정 페이지(`/qc/presets/{id}/edit`)에서 템플릿은 `preset_id`, `is_edit`를 넘기지만, JS 쪽 전역 변수 `presetId`, `isEdit`에 주입되지 않아 수정 모드 분기가 동작하지 않을 수 있음

---

## 2. 수정 내용

### 2.1 폼 기본 제출 방지
**파일:** `app/templates/preset_register.html`

- `method="post"`, `action="#"`, **`onsubmit="return false;"`** 추가  
- JS 실패 시에도 폼이 현재 페이지로 GET 제출되지 않도록 방어

```html
<form class="preset-form" id="preset-register-form" method="post" action="#" onsubmit="return false;">
```

### 2.2 수정 페이지용 JS 변수 주입
**파일:** `app/templates/preset_register.html`

- 등록/수정 공용 템플릿에서 `is_edit`, `preset_id`를 JS 전역으로 주입  
- 등록 페이지에서는 컨텍스트에 없을 수 있으므로 Jinja2 `default` 사용

```html
<script>
  window.isEdit = {{ 'true' if (is_edit|default(false)) else 'false' }};
  window.presetId = {{ (preset_id|default(none))|tojson }};
  presetRegister.init();
</script>
```

### 2.3 목록 썸네일 URL 보강
**파일:** `app/static/js/preset.js`

- API가 `thumbnail_url`/`image_url`을 주지 않을 때 `id`로 `/api/preset/{id}/image` 사용  
- 등록 직후 목록에서도 썸네일이 표시되도록 처리

```javascript
var id = p.id || p.preset_id || "";
var thumb = (p.thumbnail_url || p.image_url || (id ? "/api/preset/" + id + "/image" : "")).replace(/"/g, "&quot;");
```

### 2.4 이미지 분석 실패 시 400 응답 (보강)
**파일:** `app/api/routes.py`

- `analyze_image()` 예외 시 500 대신 **400** + 한글 메시지 반환  
- "이미지 분석 실패. 지원 형식의 이미지인지 확인해 주세요."  
- LAB 추출 실패(손상/비지원 형식) 시에도 `stats_json` INSERT 경로로 진입하지 않음(NOT NULL 안전)

### 2.5 기타
- `preset_register.html`: Jinja2 필터 공백 정리 (`is_edit|default(false)`, `preset_id|default(none)|tojson`)  
- 과거 정리: 하단 불필요 텍스트 제거

---

## 3. 검증

### 3.1 테스트
- QC·프리셋 관련 테스트 실행: **20 passed**
  - `tests/test_qc_ui.py`: 8 passed  
  - `tests/test_tone_matcher.py`: 12 passed (preset CRUD 포함)

```bash
python -m pytest tests/test_qc_ui.py tests/test_tone_matcher.py -v --tb=short
# 20 passed
```

### 3.2 수동 확인 권장 (NAS 배포 후)
1. `http://192.168.30.23:8100/qc/presets/register` 접속  
2. 대표 이미지 선택, 이름·설명 등 입력 후 **등록** 클릭  
3. "등록되었습니다." 메시지 후 약 1.5초 뒤 `/qc/presets`로 이동하는지 확인  
4. 목록에 방금 등록한 프리셋이 보이고, 썸네일이 로드되는지 확인  
5. (선택) 브라우저 개발자 도구에서 `POST /api/preset/register` → 200 응답 확인  

### 3.3 API 직접 확인 (curl)
```bash
# 등록 (이미지 파일 필요)
curl -s -X POST -F "image=@/path/to/test.jpg" -F "name=테스트" \
  http://192.168.30.23:8100/api/preset/register

# 목록
curl -s http://192.168.30.23:8100/api/preset/list
```

---

## 4. 변경 파일 요약

| 파일 | 변경 내용 |
|------|-----------|
| `app/templates/preset_register.html` | 폼 `onsubmit` 방어, `isEdit`/`presetId` 주입, Jinja2 필터 공백 정리 |
| `app/static/js/preset.js` | 목록 썸네일용 fallback URL (`/api/preset/{id}/image`) |
| `app/api/routes.py` | `analyze_image()` 예외 시 400 + 한글 메시지 반환 |

---

## 5. 배포 시 참고

- NAS에서 코드 반영 후: `docker restart newtalk-image-auto`  
- DB·API 경로는 기존과 동일: `POST /api/preset/register`, `GET /api/preset/list`  
- 작업지시서의 STEP 1~4(컨테이너 로그, API 테스트, DB 확인, 프론트 확인)는 원인 파악용으로 수행 가능하며, 본 수정으로 동일 증상은 해소되는 것이 기대됨

---

## 6. 작업 완료 보고

- **보고서:** docs/reports/CUR-NASIMG-BUG-FIX-001-20260224.md  
- **GitHub Private:** https://github.com/moongoby/newtalk-image-auto (main)  
- **GitHub Public docs:** https://github.com/moongoby/project-docs (master), nas-image/reports/  
- **확인:** `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/reports/CUR-NASIMG-BUG-FIX-001-20260224.md` → 200 필수  
- **동기화:** Private 커밋·푸시 후 Public project-docs 동기화 필수 (DOC_RULES.md 절차)  
- **KST:** 2026-02-24

---

## 7. 프리셋 등록 실패 2차 추적 (curl 등록 후에도 목록 미표시·썸네일 깨짐)

### 7.1 디버그 스크립트 실행

NAS SSH 접속 후 아래 중 한 가지로 실행한 뒤, **출력 전체**를 복사하여 보고한다.

```bash
# 방법 A: 로컬에서 원격 실행
ssh -p 2222 newtalk@192.168.30.23 "cd /volume1/뉴톡/newtalk-image-auto && bash scripts/nas_preset_debug_report.sh"

# 방법 B: NAS에 접속한 뒤
cd /volume1/뉴톡/newtalk-image-auto && bash scripts/nas_preset_debug_report.sh
```

### 7.2 결과 해석 가이드

| 확인 항목 | 정상일 때 | 이상 시 의심 원인 |
|-----------|-----------|-------------------|
| **STEP 1 로그** | `error`/`traceback`/`500` 없음 | 이미지 분석 실패(400), 디스크/권한 오류(500), 또는 preset register 예외 |
| **STEP 2 HTTP_CODE** | `200` | `400` → 이미지 분석 실패(형식/손상). `500` → 서버 예외(로그와 함께 확인) |
| **STEP 2 응답 body** | `{"id": 숫자, "stats": {...}, "preset": {...}}` | `{"detail": "..."}` → 에러 메시지로 원인 확인 |
| **STEP 3 DB** | `tone_presets`에 행 존재, `ip_len`/`tp_len` > 0 | 등록 후에도 행 없음 → API가 실패했거나 DB 경로 불일치. `ip_len`=0 → 이미지 저장/update_preset 실패 |
| **STEP 3 image_path** | `/data/processed/_preset_assets/{id}/image.jpg` 형태 | 호스트 경로(`/volume1/...`)로 저장돼 있으면 컨테이너 내부에서 `Path(path).exists()` 실패 → 썸네일 404 |
| **STEP 4 _preset_assets** | 호스트 `_processed/_preset_assets/{id}/` 및 컨테이너 내 동일 경로에 `image.jpg`, `thumbnail.jpg` 존재 | 디렉터리 없음 → 마운트 또는 쓰기 권한 문제. 파일 없음 → 썸네일 생성 또는 copy 실패 |
| **STEP 5 preset.js** | 등록 시 `POST /api/preset/register` 호출 (FormData) | URL 오타 또는 다른 엔드포인트 호출 시 등록 안 됨 |
| **STEP 6 list 응답** | `{"presets": [{ "id", "name", "image_path", ... }]}` | `presets` 빈 배열이면 DB에 없음. 항목은 있는데 썸네일만 깨지면 `/api/preset/{id}/image` 404 → image_path 경로/파일 존재 여부 확인 |

### 7.3 썸네일 전체 깨짐 시 체크리스트

1. **DB의 image_path가 컨테이너 기준인가?**  
   - 저장 시 `_preset_assets_dir()` = `processed_root / "_preset_assets"` → 기본값 `/data/processed/_preset_assets/{id}/image.jpg`.  
   - 컨테이너 내부에서 해당 Path가 마운트된 볼륨과 일치해야 하며, `api_preset_image`는 `Path(path).exists()`로 검사하므로 **호스트 전용 경로**(예: `/volume1/...`)가 들어가면 404.

2. **실제 파일 존재**  
   - 호스트: `ls /volume1/★제품사진/_processed/_preset_assets/`  
   - 컨테이너: `docker exec newtalk-image-auto ls -la /data/processed/_preset_assets/`

3. **목록에 미표시**  
   - API 목록(`/api/preset/list`)에 항목이 있는지 먼저 확인.  
   - 없으면 등록 API 실패 또는 DB가 다른 경로에 있음(컨테이너와 호스트 DB 디렉터리 불일치).

---

## 8. 프리셋 등록 정상 테스트 + 썸네일 문제 수정 (2026-02-24)

### 8.1 작업 요약

- **STEP 1:** 정상 JPG로 등록 테스트 — 서버에서 `find` 시 `@eaDir` 제외 후 `curl` 등록, DB·목록 API 확인.
- **STEP 2:** 기본 프리셋 썸네일 문제 수정 — 목록/QC에서 썸네일이 없을 때 플레이스홀더 표시.
- **STEP 3:** `@eaDir` 제외 보강 — Python 상수·헬퍼 추가, shell `find` 시 `-not -path "*@eaDir*"` 사용 권장.
- **STEP 4:** Docker 재시작 후 헬스체크.
- **STEP 5:** 보고서 갱신, Private commit/push, Public 동기화 후 `curl 200` 확인.

### 8.2 STEP 2: 썸네일 수정 내용

**파일:** `app/static/js/preset.js`

- **플레이스홀더 상수:** 썸네일/이미지 URL이 없을 때 사용할 SVG 데이터 URI (`"이미지 없음"` 문구 포함) 추가.
- **목록 카드:** `thumbnail_url`/`image_url`이 없으면 `/api/preset/{id}/image` 사용, 그것도 없으면 플레이스홀더 표시.  
  `onerror` 시에도 플레이스홀더로 대체해 빈 칸/깨짐 방지.
- **QC 상세 프리셋 선택:** 동일하게 `thumbnail_url`/`image_url` 없을 때 `/api/preset/{id}/image` → 없으면 플레이스홀더, `onerror` 시 플레이스홀더로 대체.

### 8.3 STEP 3: @eaDir 제외 처리

**파일:** `app/parsers/folder_parser.py`

- **상수:** `SYNC_SKIP_DIR_NAMES = ("@eaDir",)` — Synology NAS 썸네일/메타데이터용 시스템 폴더.
- **헬퍼:**  
  - `should_skip_folder_name(name)` — 폴더명이 `@eaDir` 등이면 True.  
  - `path_contains_skip_dir(path)` — 경로 중 어느 부분이 제외 대상이면 True.
- **Python:** 현재 `iterdir()` 사용처는 `is_file()`만 취하므로 디렉터리(`@eaDir`)는 이미 제외됨.  
  향후 `walk`/`rglob` 등 재귀 스캔 시 `path_contains_skip_dir`로 필터 권장.
- **Shell:** NAS에서 `find` 사용 시 `-not -path "*@eaDir*"` 옵션 사용 권장.  
  예: `find /volume1/★제품사진/ -name "*.jpg" -not -path "*@eaDir*" -not -path "*_processed*"`

### 8.4 변경 파일 요약 (본 절 추가분)

| 파일 | 변경 내용 |
|------|-----------|
| `app/static/js/preset.js` | 빈 썸네일 시 플레이스홀더 SVG 표시, 목록·QC 프리셋 썸네일 onerror 시 플레이스홀더 대체 |
| `app/parsers/folder_parser.py` | `SYNC_SKIP_DIR_NAMES`, `should_skip_folder_name()`, `path_contains_skip_dir()` 추가 |

### 8.5 서버 측 확인 (STEP 1, 4, 5)

- STEP 1: `TESTIMG=$(find ... -not -path "*@eaDir*" ...); curl -X POST -F "image=@${TESTIMG}" ...` → HTTP 200, DB·목록 API 확인.
- STEP 4: `docker restart newtalk-image-auto` 후 `curl -s http://localhost:8100/api/health`.
- STEP 5: 보고서 갱신 후 Private commit/push, Public 동기화,  
  `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/reports/CUR-NASIMG-BUG-FIX-001-20260224.md` → **200** 확인 필수.

---

## 9. 3차 추적 — Docker 반영 확인 (2026-02-24)

### 9.1 목적
코드 수정(preset_register.html `onsubmit`, preset.js 등)이 **Docker 컨테이너에 실제 반영됐는지** 확인.

### 9.2 로컬 프로젝트 기준 결론 (사전 판단)

| 항목 | 내용 |
|------|------|
| **Dockerfile** | `COPY . .`(22행) — **앱 코드 전체가 이미지 빌드 시 복사됨** |
| **docker-compose volumes** | `./data/db`, `./data/logs`, 사진/처리 경로, SSH 키만 마운트. **app/ 또는 templates 마운트 없음** |
| **반영 방식** | 코드는 **이미지에 고정**. 호스트에서 파일만 수정하고 `docker restart`만 하면 **변경 반영 안 됨** |

**따라서:** 프리셋 수정 사항을 NAS에서 쓰려면 **이미지 재빌드 후 컨테이너 재기동**이 필요함.

### 9.3 서버에서 실행할 검증 스크립트
프로젝트 루트에 `scripts/nas_docker_code_verify.sh` 추가됨. NAS 접속 후:

```bash
ssh -p 2222 newtalk@192.168.30.23
cd /volume1/뉴톡/newtalk-image-auto
bash scripts/nas_docker_code_verify.sh
```

**스크립트가 확인하는 것:**
- 호스트 vs 컨테이너 `preset_register.html`의 `onsubmit` 존재 여부
- `docker inspect` 마운트 목록
- `docker-compose.yml` volumes
- Dockerfile의 COPY/ADD/WORKDIR
- 컨테이너 내부 health API, DB 경로, `tone_presets` 조회

### 9.4 재빌드로 반영하기 (권장)
NAS에서 코드 반영 절차:

```bash
cd /volume1/뉴톡/newtalk-image-auto
# 최신 코드가 이미 올라와 있다고 가정 (git pull 또는 동기화 후)
docker-compose build --no-cache
docker-compose up -d
```

빌드 후 `scripts/nas_docker_code_verify.sh`를 다시 실행해 컨테이너 내부 `grep "onsubmit"` 결과에 `onsubmit="return false;"`가 나오면 반영된 것.

### 9.5 결과 보고 시 확인할 것
- Dockerfile COPY 내용: `COPY . .` 여부
- docker-compose 마운트: app/ 경로 마운트 있는지 여부
- 호스트 vs 컨테이너 코드 차이: onsubmit 한 줄 비교
- DB 조회 결과: tone_presets 최신 행

---

## 10. 프리셋 썸네일 전부 깨짐 수정 (2026-02-24)

### 10.1 증상
- 프리셋 등록은 성공하나 **목록에서 썸네일 전부 깨짐** (이미지 없음/404).

### 10.2 원인
1. **경로 불일치:** DB에 저장된 `image_path`/`thumbnail_path`가 비어 있거나, 호스트 경로(`/volume1/...`)로 저장된 경우 컨테이너 내부에서 `Path(path).exists()`가 False → `/api/preset/{id}/image`가 404 반환.
2. **목록 API:** `list_presets`는 `image_path`, `thumbnail_path`(파일 경로)만 반환하고 `thumbnail_url`/`image_url`은 반환하지 않음. 프론트는 fallback으로 `/api/preset/{id}/image`를 쓰지만, 위 404로 썸네일이 깨짐.

### 10.3 수정 내용

**파일:** `app/api/routes.py`

1. **경로 해석 fallback (`_resolve_preset_image_path`)**
   - DB 경로가 없거나 해당 경로에 파일이 없으면 **정규 경로**로 재시도:  
     `processed_root / "_preset_assets" / str(preset_id) / filename`  
   - NAS 등에서 DB에 호스트 경로가 들어가 있어도 컨테이너 내 마운트 경로(`/data/processed/_preset_assets/...`)로 서빙 가능.

2. **`GET /api/preset/{preset_id}/image`**
   - `preset.get("image_path")`만 보지 않고 `_resolve_preset_image_path(preset_id, path_from_db, "image.jpg")` 사용.  
   - 정규 경로에 파일이 있으면 해당 파일 반환.

3. **`GET /api/preset/{preset_id}/thumbnail` 신규**
   - 썸네일 전용 엔드포인트. `thumbnail_path` → 정규 경로 `thumbnail.jpg` fallback.  
   - 썸네일 파일 없으면 원본 `image.jpg`로 fallback 후 404.

4. **`GET /api/preset/list`**
   - 각 프리셋 항목에 `thumbnail_url`, `image_url` 추가:  
     `"/api/preset/{id}/thumbnail"`, `"/api/preset/{id}/image"`  
   - 프론트는 기존대로 `thumbnail_url` 우선 사용 → 목록에서 썸네일 URL이 명시적으로 채워짐.

### 10.4 검증 절차 (NAS 배포 후)

```bash
# STEP 1: DB 저장 경로 확인
sqlite3 /volume1/뉴톡/newtalk-image-auto/data/db/jobs.db \
  "SELECT id, name, image_path, thumbnail_path FROM tone_presets ORDER BY id DESC LIMIT 5;"

# STEP 2: 정규 경로에 파일 존재 확인 (호스트)
ls -la /volume1/★제품사진/_processed/_preset_assets/
# 또는 컨테이너
sudo docker exec newtalk-image-auto ls -la /data/processed/_preset_assets/

# STEP 3: 이미지/썸네일 API 응답 확인
curl -s -w "\nHTTP_CODE: %{http_code}\n" http://localhost:8100/api/preset/1/image
curl -s -w "\nHTTP_CODE: %{http_code}\n" http://localhost:8100/api/preset/1/thumbnail

# STEP 4: 목록 API에 thumbnail_url/image_url 포함 여부
curl -s http://localhost:8100/api/preset/list | head -c 500
```

**기대 결과:**  
- STEP 3: HTTP_CODE 200, 바이너리 이미지 body.  
- STEP 4: `"presets": [{ "id", "thumbnail_url": "/api/preset/1/thumbnail", "image_url": "/api/preset/1/image", ... }]`

### 10.5 변경 파일 요약 (본 절)

| 파일 | 변경 내용 |
|------|-----------|
| `app/api/routes.py` | `_resolve_preset_image_path()` 도입, `api_preset_image`/`api_preset_thumbnail` 경로 fallback, `api_preset_list`에 `thumbnail_url`/`image_url` 추가 |

### 10.6 배포 시 참고
- **코드 수정이므로** NAS에서 반영 시 이미지 재빌드 필요:  
  `docker-compose build --no-cache && docker-compose up -d`  
- 재빌드 후 브라우저에서 `/qc/presets` 목록 썸네일이 모두 표시되는지 확인.
