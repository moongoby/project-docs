# 116 NAS 폴더 INSERT 미작동 조사 보고서

**작성일시:** 2026-02-25  
**프로젝트:** server116 (git@github.com:moongoby/server116.git, main)  
**문제:** "모델촬영폴더생성" 버튼 클릭 시 `nas_folder_request` 테이블에 INSERT 되지 않음 (테이블은 존재하나 비어 있음)

---

## 1. 확인 결과 요약

| 확인 항목 | 결과 |
|-----------|------|
| `Content.php` — `createModelShootingFolder()` | INSERT 호출부 존재, 조건문 `if ($shootingId && !empty($selectedCodies))` 내부에서만 실행 |
| `Common_m.php` — `insertNasFolderRequest()` | 메서드 존재, `nas_folder_request` INSERT 정상 구현 |
| DB 설정 | `application/config/database.php` — `database => 'autoda'` 사용 (정상) |
| **원인** | **뷰에서 `shooting_id` 값을 잘못된 jQuery 선택자로 읽어 값이 비어 있음 → PHP에서 `$shootingId`가 빈 값이라 조건 불만족 → INSERT 미실행** |

---

## 2. 원인 상세

### 2.1 파일: `views/content/shooting_register.php`

**위치:** `#createModelShootingFolder` 클릭 핸들러 내 (약 3652행)

**기존 코드 (오류):**
```javascript
var shooting_id = $('input[name="shooting_id').val();
```

**문제점:**  
- 속성 선택자 `[name="shooting_id"` 에 **닫는 따옴표와 괄호 `"]"` 가 누락**됨.  
- 올바른 선택자는 `$('input[name="shooting_id"]')` 또는 `$('#shooting_id')` 여야 함.  
- 잘못된 선택자로 인해 요소를 찾지 못하고 `shooting_id` 가 `undefined` 가 됨.  
- 폼 제출 시 `shooting_id` hidden 값이 비어 있어, PHP `$this->input->post('shooting_id')` 가 빈 값.  
- `createModelShootingFolder()` 내 조건 `if ($shootingId && !empty($selectedCodies))` 에서 `$shootingId` 가 falsy 이므로 **INSERT 블록 전체가 실행되지 않음**.

### 2.2 컨트롤러/모델

- **Content.php:** `insertNasFolderRequest` 호출부는 조건문 안에만 있으며, 로직상 정상.  
- **Common_m.php:** `insertNasFolderRequest()`, `fetchShootingDate()`, `fetchCodyData()`, `fetchCodyProductData()` 모두 존재하며, DB는 기본(autoda) 연결 사용.

---

## 3. 수정 내용

**파일:** `server116/views/content/shooting_register.php`

**변경:**  
- `var shooting_id = $('input[name="shooting_id').val();`  
- → `var shooting_id = $('#shooting_id').val();`  
- 페이지 내 hidden input 이 `id="shooting_id"` 를 갖고 있으므로 `#shooting_id` 로 확실히 참조.

---

## 4. 배포 후 확인 권장 (116 서버)

배포 후 실제 서버에서 아래로 검증 권장.

```bash
# 배포된 파일에 insertNasFolderRequest / nas_folder_request 포함 여부
grep -n "insertNasFolderRequest\|nas_folder_request" /home/newpigup3/application/controllers/Content.php
grep -n "insertNasFolderRequest\|nas_folder_request" /home/newpigup3/application/models/Common_m.php

# PHP 에러 로그 (해당일)
grep -i "nas_folder\|insertNas\|error" /home/newpigup3/application/logs/log-2026-02-25.php | tail -30
```

버튼 클릭 후:

```bash
mysql -u pigupuser -p autoda -e "SELECT * FROM nas_folder_request ORDER BY id DESC LIMIT 5;"
```

으로 새 행 INSERT 여부 확인.

---

## 5. 결론

- **근본 원인:** `shooting_register.php` 의 jQuery 선택자 오타로 `shooting_id` 가 전달되지 않아, NAS 폴더 요청 INSERT 조건이 만족되지 않음.  
- **조치:** `shooting_id` 를 `$('#shooting_id').val()` 로 읽도록 수정 완료.  
- **배포:** 수정 반영 후 커밋 및 푸시 완료.

---

## 6. 해결 확인

**해결 일시:** 2026-02-25 18:55 KST  

**해결 방법:**  
- `shooting_id` 선택자 오타 수정 (`$('input[name="shooting_id')` → `$('#shooting_id').val()`) 후 116 서버 배포.

**검증 결과:**  
- DB `nas_folder_request` INSERT 성공 (id=1, shooting_id=662, model_name=임지영 등).  
- NAS 폴더 생성 정상 (pending → completed, 약 17초).  
- 상세 검증 내역: [116-NAS-DEPLOY-VERIFY-20260225.md](./116-NAS-DEPLOY-VERIFY-20260225.md) 참고.

---

**보고서 끝**
