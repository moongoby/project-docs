# 116서버 모델촬영폴더생성 PHP 코드 확인 보고서

**작성일시:** 2026-02-24 KST  
**목적:** 폴더 자동생성 자동화를 위한 기존 로직 파악  
**대상:** 116서버 코드 (워크스페이스 내 `/root/server116` 기준)

---

## 1. 사전 준수사항 확인

- `docs/CONTEXT.md`, `.cursorrules` 읽기 완료.
- 116서버 PHP 코드는 로컬 워크스페이스 `server116` 폴더에 있음 (114서버 SSH 규칙은 .cursorrules 기준).

---

## 2. 폴더생성 관련 위치 요약

| 구분 | 경로 |
|------|------|
| 컨트롤러 | `server116/application/controllers/Content.php` |
| 뷰(버튼) | `server116/views/content/shooting_register.php` |
| 모델(DB) | `server116/application/models/Common_m.php` |
| URL | `POST /content/createModelShootingFolder` |

---

## 3. 폴더생성 PHP 함수 전체 코드

**컨트롤러 메서드:** `Content::createModelShootingFolder()`

```php
// 모델촬영폴더생성
public function createModelShootingFolder()
{
    $selectedProducts = $this->input->post('selected_codies');
    $shooting_id = $this->input->post('shooting_id');
    
    $contentsData = $this->common_m->fetchShootingDate($shooting_id);
    
    $zipFileName = $contentsData['ShootingDate'] . '_' . $contentsData['model_name'] . '_' . $contentsData['place_name'] . '.zip';
    $zipFilePath = '/home/newpigup3/www/data/' . $zipFileName;

    $zip = new ZipArchive();

    if ($zip->open($zipFilePath, ZipArchive::CREATE) === TRUE) {
        foreach ($selectedProducts as $codyID) {
            $codyData = $this->common_m->fetchCodyData($codyID);

            $codyNumber = $codyData[0]['codyNumber'];
            $Model_shooting_complete_date = $codyData[0]['Model_shooting_complete_date'];
            $model_name = $codyData[0]['model_name'];
            $place_name = $codyData[0]['place_name'];

            $codyFolder = $codyNumber.'번코디 - '. $codyData[0]['codyCode'];
            $codyProductData = $this->common_m->fetchCodyProductData($codyID);
        
            $codyProductFolder = '';
            foreach ($codyProductData as $codyProduct) {
                $codyProductFolder .= $codyProduct['codyProdCode'] .  '_' . $codyProduct['GoodsEtc6'] .'_' . $codyProduct['codyProdName'] . '_' . $codyProduct['codyProdColor'] . '_' . $codyProduct['codyProdSize'] .'+';
            }
            $codyProductFolder = rtrim($codyProductFolder, ' + ');

            $fullFolderPath = $codyFolder . '_' . $codyProductFolder;

            if (!is_dir($fullFolderPath)) {
                @mkdir($fullFolderPath, 0777, true);
            }

            $zip->addEmptyDir($fullFolderPath);
        }

        $zip->close();

        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="' . $zipFileName . '"');
        header('Content-Length: ' . filesize($zipFilePath));
        readfile($zipFilePath);

        unlink($zipFilePath);
        $this->removeEmptyDirectories('/home/newpigup3/www/data/');
    }
}

private function removeEmptyDirectories($path)
{
    if (is_dir($path)) {
        $files = scandir($path);
        foreach ($files as $file) {
            if ($file != '.' && $file != '..') {
                $fullPath = $path . '/' . $file;
                if (is_dir($fullPath)) {
                    $this->removeEmptyDirectories($fullPath);
                    if (count(glob($fullPath . '/*')) === 0) {
                        rmdir($fullPath);
                    }
                }
            }
        }
    }
}
```

- **입력:** `selected_codies` (코디 코드 배열), `shooting_id`.
- **동작:** ZIP 파일을 `/home/newpigup3/www/data/`에 생성한 뒤 다운로드 응답으로 내려보내고, 응답 후 해당 zip 파일 삭제 및 data 폴더 내 빈 디렉터리 정리.

---

## 4. 다운로드되는 ZIP 구조

- **ZIP 파일명:** `{ShootingDate}_{model_name}_{place_name}.zip`  
  - 예: `2026-02-20_홍길동_스튜디오A.zip`
- **ZIP 내용:** **폴더만 포함, 파일은 없음** (`addEmptyDir`만 사용).
- **폴더명 규칙 (각 선택 코디당 1개):**
  - `{codyNumber}번코디 - {codyCode}_{codyProdCode}_{GoodsEtc6}_{codyProdName}_{codyProdColor}_{codyProdSize}[+ ...]`
  - 동일 코디에 상품이 여러 개면 `+`로 이어 붙임 (마지막 ` + `는 제거).

**예시 구조:**

```
2026-02-20_홍길동_스튜디오A.zip
├── 1번코디 - CD001_CP01_도매처A_상품명_블랙_M+
├── 2번코디 - CD002_CP02_도매처B_상품명2_화이트_L
└── ...
```

---

## 5. DB 테이블/필드 (폴더명 결정에 사용)

### 5.1 촬영 일정 정보 — ZIP 파일명

**함수:** `Common_m::fetchShootingDate($shooting_id)`

| 테이블 | 용도 |
|--------|------|
| `contents_msg` | 촬영 일정 (id = shooting_id) |
| `user_model` | 모델명 (contents_msg.ModelName = user_model.id) |
| `user_place` | 장소명 (contents_msg.PlaceName = user_place.id) |

**ZIP 파일명에 쓰이는 필드:**

- `contents_msg.ShootingDate` → 촬영일
- `user_model.name` → model_name
- `user_place.Name` → place_name

### 5.2 코디 정보 — 폴더명 앞부분

**함수:** `Common_m::fetchCodyData($codyCode)`  
(codyCode = 화면에서 선택한 `selected_codies[]` 값)

| 테이블 | 용도 |
|--------|------|
| `cody_msg` | 코디 마스터 (codyCode로 조회) |
| `contents_msg` | shooting_id 연동 |
| `user_model` | model_name |
| `user_place` | place_name |
| `cody_product_msg` | 코디별 상품 (left join) |

**폴더명에 사용하는 필드:**

- `cody_msg.codyNumber` → N번코디
- `cody_msg.codyCode` → 코디 코드

### 5.3 코디별 상품 — 폴더명 뒷부분

**함수:** `Common_m::fetchCodyProductData($codyCode)`  
조건: `cody_product_msg.codyCode = $codyCode` AND `useCody = 0`

| 테이블 | 필드 (폴더명 조합) |
|--------|---------------------|
| `cody_product_msg` | codyProdCode, GoodsEtc6, codyProdName, codyProdColor, codyProdSize |

---

## 6. 프론트엔드 호출 (모델촬영폴더생성 버튼)

- **화면:** `pick.newtalk.kr/content/shooting_register` (촬영 등록 단계)
- **버튼:** `id="createModelShootingFolder"` — "모델촬영폴더생성"
- **동작:**  
  - `name="selected_codies[]"` 체크된 체크박스 값 수집  
  - `shooting_id` (페이지 내 변수) 수집  
  - `method="POST"`, `action="/content/createModelShootingFolder"` 인 폼을 동적 생성 후 submit  
  - 서버가 ZIP으로 응답 → 브라우저에서 파일 다운로드

---

## 7. 참고 사항 (버그/개선 가능점)

1. **`mkdir($fullFolderPath)`:**  
   `$fullFolderPath`는 상대 경로 문자열(예: `1번코디 - CD001_...`)이라, 현재 작업 디렉터리 아래에 폴더가 생성됨. ZIP에는 `addEmptyDir`로만 넣으므로 실제로는 **ZIP 안에만 빈 폴더 구조가 들어가고**, 디스크의 mkdir은 다운로드와 무관하며, `removeEmptyDirectories('/home/newpigup3/www/data/')`로는 이렇게 생성된 디렉터리는 정리되지 않음.
2. **ZIP 내용:** 현재는 **빈 폴더만** 생성. 실제 이미지/파일을 넣는 로직은 없음.
3. **116서버 실제 경로:** 코드 상 ZIP 저장 경로는 `/home/newpigup3/www/data/` (116서버 실제 호스트 경로는 배포 환경에 따라 확인 필요).

---

## 8. 요약

| 항목 | 내용 |
|------|------|
| API | `POST /content/createModelShootingFolder` |
| 파라미터 | `selected_codies[]`, `shooting_id` |
| ZIP 파일명 | `{ShootingDate}_{model_name}_{place_name}.zip` |
| ZIP 내용 | 선택 코디별 빈 폴더 1개씩, 폴더명 = `N번코디 - {codyCode}_{상품정보}+...` |
| DB | contents_msg, user_model, user_place, cody_msg, cody_product_msg |

이 문서를 기준으로 폴더 자동생성 자동화 시 동일 테이블/필드 및 네이밍 규칙을 맞추면 됨.
