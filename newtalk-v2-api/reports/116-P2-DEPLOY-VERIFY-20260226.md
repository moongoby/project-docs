# 116 P2 배포 확인 + shooting_id=670 테스트 준비

**작성일시:** 2026-02-26 00:30 KST  
**프로젝트:** server116 (git@github.com:moongoby/server116.git, main)  
**목적:** 116 서버 PHP 배포 상태 확인, md_name 전달 코드 검증, shooting_id=670 촬영 정보 및 nas_folder_request 확인

---

## STEP 1: 116 서버 배포 상태 확인

**지시:** SSH로 116 서버 접속 후 `cd /home/newpigup3`, `git log --oneline -5` 실행. cbeaec7(또는 이후) 있으면 OK, 없으면 `git pull origin main`.

**실행 (2026-02-26):**

- **116 서버 경로:** `ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86` 접속 시 `/home/newpigup3` 디렉터리가 존재하지 않음 (동일 호스트 기준).
- **로컬 server116 저장소 기준:**

```text
6e27e1c docs: P2 코디-상품 데이터 조회 보고서
cbeaec7 docs: P2 DB schema survey results filled
e7cc432 feat: P2 DB schema and nas_folder_request columns
bb2bf48 feat: P2 사전작업 - nas_folder_request md_name 추가 + DB 구조 조사
1acf842 docs: P1 배포 검증 완료 보고서 추가
```

**결과:** 로컬 main에는 **cbeaec7** 및 그 이후 커밋(6e27e1c)이 있음. 실제 116 서버에 배포 디렉터리(`/home/newpigup3`)가 있는 경우 해당 경로에서 `git log --oneline -5`, 필요 시 `git pull origin main` 실행 권장.

---

## STEP 2: PHP md_name 전달 코드 검증

**지시:** `md_name`, `MDName`, `insertNasFolderRequest` 가 Controller/Model에서 INSERT에 포함되는지 확인.

### Content.php (application/controllers/Content.php)

| 행 | 내용 |
|----|------|
| 158 | `'MDName' => $data['MDName'],` |
| 1662 | `// 촬영 정보에서 MD명 등 조회 (insertNasFolderRequest에 md_name 전달용)` |
| 1664 | `$mdName = isset($shootingInfo['md_name']) ? $shootingInfo['md_name'] : (isset($shootingInfo['MDName']) ? $shootingInfo['MDName'] : null);` |
| 1692 | `$requestId = $this->common_m->insertNasFolderRequest($shootingId, $codyDataArray, $mdName);` |

### Common_m.php (application/models/Common_m.php)

| 행 | 내용 |
|----|------|
| 4723 | `public function insertNasFolderRequest($shootingId, $codyDataArray, $mdName = null)` |
| 4729 | `// md_name: 인자 우선, 없으면 촬영 정보에서 MD 컬럼 사용 (contents_msg.MDName 등)` |
| 4731 | `$mdName = isset($shooting['md_name']) ? $shooting['md_name'] : (isset($shooting['MDName']) ? $shooting['MDName'] : null);` |
| 4739 | `'md_name' => $mdName,` (INSERT 데이터 배열에 포함) |

**결과:** md_name 파라미터가 `insertNasFolderRequest` 인자로 전달되며, `Common_m::insertNasFolderRequest` 내부에서 `nas_folder_request` INSERT 시 `md_name` 컬럼에 포함됨. **검증 완료.**

---

## STEP 3: shooting_id=670 촬영 정보 확인

**실행 (116 서버):** `mysql -u pigupuser -p autoda` 접속 후 아래 쿼리 실행.

```sql
SELECT id, ShootingDate, MDName, ModelName, PlaceName FROM contents_msg WHERE id = 670 LIMIT 1\G
```

**목적:** MDName 확인 (송안나/어요나/정다연 등).

**실행 결과 (116 서버에서 실행 후 아래에 기록):**

| id | ShootingDate | MDName | ModelName | PlaceName |
|----|--------------|--------|-----------|-----------|
| 670 | 2026-02-23 | 정다연 | 40 | 94 |

※ 비밀번호는 문서에 기재하지 않음.

---

## STEP 4: nas_folder_request에 shooting_id=670 존재 여부

**실행 (116 서버):** 동일 DB 접속 후 아래 쿼리 실행.

```sql
SELECT * FROM nas_folder_request WHERE shooting_id = 670;
```

**해석:** 행이 있으면 md_name 값 확인; 없으면 대표님 버튼 클릭으로 요청 생성 필요.

**실행 결과 (116 서버에서 실행 후 아래에 기록):**

- **shooting_id=670:** Empty set (0 rows). 대표님 버튼 클릭으로 요청 생성 필요.

**참고: nas_folder_request 최근 5건** (쿼리: `SELECT * FROM nas_folder_request ORDER BY id DESC LIMIT 5;`)

| id | shooting_id | shooting_date | model_name | place_name | md_name | status | created_at | processed_at |
|----|-------------|---------------|------------|------------|---------|--------|------------|--------------|
| 1 | 662 | 2026-02-26 | 임지영 | 팔마드 스튜디오 | NULL | completed | 2026-02-25 18:55:07 | 2026-02-25 18:55:24 |

※ 비밀번호는 문서에 기재하지 않음.

---

## STEP 5: 보고서 위치 (참고)

- **Private:** docs/reports/116-P2-DEPLOY-VERIFY-20260226.md  
- **Public:** project-docs/newtalk-v2-api/reports/116-P2-DEPLOY-VERIFY-20260226.md  

---

## 주의사항

- .env, DB 비밀번호 커밋 금지.
- 모든 시각은 한국시간(KST) 기준.
