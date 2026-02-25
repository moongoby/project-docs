# 116서버 PHP 수정 - NAS 폴더생성 DB 폴링 연동 완료 보고서

**작성일시:** 2026-02-25 KST  
**프로젝트:** server116 (뉴톡 어드민)  
**연관:** newtalk-image-auto (NAS Docker)

---

## 1. 수정된 파일 목록

| 파일 | 변경 내용 |
|------|-----------|
| `server116/application/controllers/Content.php` | `createModelShootingFolder()` 내 NAS 폴더 요청 INSERT 로직 추가 (ZIP 생성 전 실행, 기존 ZIP 다운로드 유지) |
| `server116/application/models/Common_m.php` | `insertNasFolderRequest()`, `getNasFolderRequestStatus()` 함수 추가 |
| `server116/views/content/shooting_register.php` | "모델촬영폴더생성" 버튼 옆 상태 스팬 추가, 버튼 클릭 시 "NAS 폴더 생성 요청됨" 표시 |

---

## 2. SQL 파일 위치

- **경로:** `server116/sql/create_nas_folder_request.sql`
- **용도:** `nas_folder_request` 테이블 생성 (NAS 폴더 생성 요청 큐)

---

## 3. DB 테이블 생성 (STEP 5)

배포 후 116서버 또는 DB 호스트에서 아래 중 한 가지 방법으로 실행 필요.

**방법 A) mysql CLI**
```bash
mysql -u pigupuser -p autoda < server116/sql/create_nas_folder_request.sql
```

**방법 B) 직접 실행**
```bash
mysql -u pigupuser -p autoda -e "
CREATE TABLE IF NOT EXISTS nas_folder_request (
  id INT AUTO_INCREMENT PRIMARY KEY,
  shooting_id INT NOT NULL,
  shooting_date VARCHAR(20) DEFAULT NULL,
  model_name VARCHAR(100) DEFAULT NULL,
  place_name VARCHAR(100) DEFAULT NULL,
  cody_data TEXT NOT NULL,
  status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
  error_message TEXT DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  processed_at DATETIME DEFAULT NULL,
  INDEX idx_status (status),
  INDEX idx_shooting_id (shooting_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"
```

**생성 확인**
```bash
mysql -u pigupuser -p autoda -e "DESCRIBE nas_folder_request;"
```

---

## 4. 테스트 (STEP 6)

테이블 생성 후 아래 순서로 검증 권장.

1. **테이블 존재 확인**
   ```bash
   mysql -u pigupuser -p autoda -e "SELECT COUNT(*) FROM nas_folder_request;"
   ```

2. **수동 INSERT 테스트**
   ```bash
   mysql -u pigupuser -p autoda -e "
   INSERT INTO nas_folder_request (shooting_id, shooting_date, model_name, place_name, cody_data, status)
   VALUES (1, '2026-02-25', '테스트모델', '스튜디오A',
           '[{\"codyNumber\":\"1\",\"codyCode\":\"TEST001\",\"products\":[{\"code\":\"P001\",\"name\":\"테스트상품\",\"color\":\"블랙\",\"size\":\"F\",\"etc6\":\"기타\"}]}]',
           'pending');
   "
   ```

3. **조회 확인**
   ```bash
   mysql -u pigupuser -p autoda -e "SELECT * FROM nas_folder_request ORDER BY id DESC LIMIT 5;"
   ```

4. **테스트 데이터 삭제**
   ```bash
   mysql -u pigupuser -p autoda -e "DELETE FROM nas_folder_request WHERE model_name='테스트모델';"
   ```

---

## 5. 기존 ZIP 다운로드 기능

- **유지 여부:** 유지됨. `createModelShootingFolder()` 내 NAS 요청 로직은 ZIP 생성 로직 **앞단**에만 추가되었으며, 기존 ZIP 생성·다운로드·파일 삭제 로직은 변경 없음.
- **동작 순서:** NAS 요청 INSERT → (기존) `fetchShootingDate` → ZIP 생성 → 다운로드 → 정리.

---

## 6. Git 커밋 및 푸시

**완료 (2026-02-25)**  
- **커밋:** `9c6cd7b` — `feat: NAS folder auto-create DB polling - nas_folder_request table and PHP INSERT`
- **원격:** `git@github.com:moongoby/server116.git` (origin) — **main 브랜치 푸시 완료**

**포함된 파일**
- `sql/create_nas_folder_request.sql`
- `application/controllers/Content.php`
- `application/models/Common_m.php`
- `views/content/shooting_register.php`
- `docs/reports/116-NAS-FOLDER-DB-POLLING-REPORT.md`

(.env, database.php 비밀번호 등 민감정보는 미포함.)

---

## 7. 참고 사항

- **Common_m.php:** `fetchShootingDate` 반환값 키는 `ShootingDate`, `model_name`, `place_name` 사용. `insertNasFolderRequest`에서 동일 키로 매핑함.
- **fetchCodyData / fetchCodyProductData:** 각각 `result_array()` 반환. 코디 정보는 첫 행 `$codyInfo[0]` 사용.
- **로그:** 요청 등록 성공/실패/예외는 `log_message('info'|'error', ...)` 로 기록됨.

---

**보고서 끝**
