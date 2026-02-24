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
