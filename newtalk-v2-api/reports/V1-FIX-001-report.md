# V1-FIX-001: 이미지 URL 도메인 치환 (DO Spaces → newtalk.kr) 보고서

**작성일:** 2026-02-27  
**커밋 접두사:** `[V1-FIX-001]`  
**목적:** 서빙 URL을 `https://newtalk.nyc3.cdn.digitaloceanspaces.com` → `https://newtalk.kr`로 변경 (도메인+경로 치환)

---

## PART A: 소스 분석 (수정 전 채팅 보고)

### A-1. V1 루트 경로 및 관련 파일

| 구분 | 경로 (워크스페이스 기준) |
|------|-------------------------|
| **V1 루트 (114 서버 추정)** | `server114/`, `tmp_114_app/` (실제 서버는 SSH 접속 후 확인) |
| **Controller (products)** | `server114/products_*.php` (6종), `tmp_114_app/controllers/products.php` |
| **Controller (server-116)** | `server114/server-116/newpigup3/application/controllers/Product.php` |
| **View** | `server114/goods_img_sorting_test1.php`, `server114/server-116/.../views/products/goods_img_sorting_test1.php` |
| **Model** | `server114/server-116/.../application/models/Goods_m.php` — `get_goods_id_update()` |

### A-2. digitaloceanspaces 포함 파일 및 줄

- **tmp_114_app/controllers/products.php:** 11285(DO 호스트 체크), 11304(endpoint), 11331(oceanPath)
- **server114/products_*.php (6개):** 각 11214~11267 부근 — endpoint, oceanPath
- **server114/server-116/.../Product.php:** 3866(endpoint), 3915(oceanPath)
- **server116, go100** 동일 패턴

### A-3. 이미지 URL 조립 로직

- **"이미지 저장":** `goodsDetailOpen()` → shop.newtalk.kr/goods/detail_save (별도 앱)
- **"상세설명 HTML 적용":** 동일 detail_save
- **"디지털 오션 전송":** `digitaloceanApi()` — DO 경로 `$d = "img/".date("Ym")."/"`, `$oceanPath`로 DB 갱신 (`get_goods_id_update`) — **oceanPath를 로컬로 변경 대상**
- **"저장하기":** `goods_img_sorting_save1()` — 순서만 저장

### A-4. config 이미지 경로

- **config:** `user_goodscode_img_dir`, `user_goodscode_img_url` (server-116/newpigup3/application/config/config.php)
- **oceanPath(서빙 URL):** config 없음, `digitaloceanApi()` 내 하드코딩

### A-5. 로컬 이미지 확인

- 서버에서 실행 필요: `find / -path "*/data/files/goods/goodscode/img/bl5890k62" -type d` 등 (결과 채팅 보고)

### A-6. DO → 로컬 매핑

- DO: `/img/{년월}/{파일명}` → 로컬: `/data/files/goods/goodscode/img/{상품코드}/{파일명}`
- 상품코드: 파일명 첫 `-` 앞 (예: `bl5890k62-600_1.jpg` → `bl5890k62`)

---

## 전상품 일괄 치환 — 서버 전수 조사 (STEP 1~4)

### 접속
```bash
ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86
```

### 조사용 파일 (워크스페이스)
- `docs/reports/v1_fix001_survey.sh` — 전수 조사 스크립트 (비밀번호 여러 번 입력)
- `docs/reports/survey_queries.sql` — 1-1, 1-2(goods_detail), 2, 3, 4 한 번에 실행 (비밀번호 1회)

### STEP 1: DO URL 포함 테이블·컬럼 전수 조사

**방법 A — SQL 파일로 실행 (비밀번호 1회)**  
서버에 `survey_queries.sql` 업로드 후:
```bash
mysql -h 127.0.0.1 -P 3306 -u root -p autoda < survey_queries.sql
```

**방법 B — 1-2 전수(모든 텍스트 컬럼) 쿼리 생성**  
1-1 결과로 컬럼 목록을 확인한 뒤, 아래 쿼리로 DO 건수용 UNION 쿼리 생성:
```sql
SELECT CONCAT(
  'SELECT ''', TABLE_NAME, ''' AS tbl, ''', COLUMN_NAME, ''' AS col, COUNT(*) AS cnt FROM `', TABLE_NAME, '` WHERE `', COLUMN_NAME, '` LIKE ''%digitaloceanspaces.com%'' HAVING cnt > 0 UNION ALL'
)
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'autoda'
AND DATA_TYPE IN ('varchar','text','mediumtext','longtext','char')
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```
→ 출력 마지막 줄의 `UNION ALL`을 `;`로 바꾼 뒤 실행.

**방법 C — 스크립트 실행**
```bash
bash v1_fix001_survey.sh
```

### STEP 2: 상품코드 하이픈 포함 여부
```sql
SELECT GoodsCode FROM goods WHERE GoodsCode LIKE '%-%' LIMIT 20;
```
→ 하이픈 있으면 SUBSTRING_INDEX(파일명, '-', 1) 사용 불가, JOIN 방식 필수.

### STEP 3: 샘플 데이터 (경로 패턴 확인)
```sql
SELECT GoodsEtc60, GoodsEtc73 FROM goods_detail WHERE GoodsEtc60 LIKE '%digitaloceanspaces.com%' LIMIT 5;
```

### STEP 4: 상세설명 HTML 필드 DO URL 건수
```sql
SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'autoda' AND TABLE_NAME IN ('goods', 'goods_detail')
AND DATA_TYPE IN ('text','mediumtext','longtext');
```
→ 위 컬럼마다 `SELECT COUNT(*) FROM 테이블 WHERE 컬럼 LIKE '%digitaloceanspaces.com%';` 실행.

### 보고 형식 (채팅 보고 후 UPDATE 승인 대기)
| 테이블 | 컬럼 | DO URL 포함 건수 |
|--------|------|------------------|
| ... | ... | ... |
**총 영향 행 수:** ___건  
**goods_detail 외 테이블:** 있음/없음

---

## V1-FIX-001 서버 직접 실행 결과 (2026-02-27)

### 접속 가능 확인 (실행 완료)

| 대상 | 결과 | 비고 |
|------|------|------|
| **SSH** | 가능 | `ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86` |
| **MySQL root** | 비밀번호 필요 | 비대화형에서 사용 불가 |
| **MySQL pigupuser** | 가능 | V1 `application/config/database.php` 계정으로 접속·조회·덤프 가능 |

→ **pigupuser**로 전수 조사 및 영향 테이블 백업 실행 완료.

---

### STEP 0: 백업 (실행 완료)

| 항목 | 상태 | 비고 |
|------|------|------|
| 백업 디렉터리 | 완료 | `/root/backup/v1-fix-001-20260227/` |
| V1 소스(controllers) | 완료 | `v1_controllers_20260227.tar.gz` **443KB** |
| goods_detail 테이블 | 완료 | `goods_detail_before_20260227.sql` **1.1GB** (pigupuser 덤프) |
| DB 전체 덤프 | 미실행 | root 권한 필요 시 서버에서 직접 실행 |

---

### STEP 1: DB 전수 조사 결과 (실행 완료)

| 테이블 | 컬럼 | DO URL 포함 건수 |
|--------|------|------------------|
| goods_detail | GoodsEtc60 | 155 |
| goods_detail | GoodsEtc61 | 155 |
| goods_detail | GoodsEtc62 | 155 |
| goods_detail | GoodsEtc63 | 155 |
| goods_detail | GoodsEtc64 | 155 |
| goods_detail | GoodsEtc65 | 155 |
| goods_detail | GoodsEtc66 | 155 |
| goods_detail | GoodsEtc67 | 155 |
| goods_detail | GoodsEtc68 | 155 |
| goods_detail | GoodsEtc69 | 155 |
| goods_detail | GoodsEtc70 | 155 |
| goods_detail | GoodsEtc71 | 155 |
| goods_detail | GoodsEtc72 | 155 |
| goods_detail | GoodsEtc73 | 155 |
| goods_detail | GoodsEtc74 | 155 |
| goods_detail | DanharooDescription | 155 |

**총 영향 행 수:** 155건 (동일 상품 다수 컬럼 포함).  
**상품코드 하이픈 포함:** 있음 (예: `NS30-RT`) → 경로 치환 시 **goods JOIN으로 GoodsCode 사용 권장**, 파일명만으로 추출 시 오류 가능.  
**goods_detail 외 테이블:** 없음 (goods 텍스트 컬럼은 0건).

**샘플 URL:**  
- `https://newtalk.nyc3.cdn.digitaloceanspaces.com/img/202602/bl5861c5c-600_1.jpg`  
- GoodsEtc73: `https://newtalk.nyc3.cdn.digitaloceanspaces.com/img/202602/`

---

### STEP 2 보고 및 UPDATE 대기

- 전수 조사까지 완료. **UPDATE는 채팅에서 승인 후 실행.**
- pigupuser는 읽기 전용일 수 있으므로, **UPDATE 실행 시에는 root 등 쓰기 권한 계정** 사용 필요.

---

## PART A (이전): 이미지 정렬 페이지 소스 분석 및 수정

### A-3 분석 보고 (수정 전)

#### 1) V1 루트 경로
- **로컬 워크스페이스 기준:**  
  - 114 서버용 추정: `tmp_114_app`, `server114/` (products_*.php, server-116/newpigup3)  
  - 116 서버용: `server116/`  
  - 기타 복사본: `go100/server-116/newpigup3`  
- **실제 114 서버 경로:** SSH 접속 후 확인 필요  
  - 예: `/var/www/newtalk`, `/home/danharoo/www` 등

#### 2) goods_img_sorting_test1 관련 파일
| 구분 | 경로 |
|------|------|
| Controller | `tmp_114_app/controllers/products.php` — `goods_img_sorting_test1()`, `digitaloceanApi()` |
| View | `tmp_114_views/goods_img_sorting_test1.php` (동일 구조: server114/server-116/newpigup3/views/products/goods_img_sorting_test1.php, server116/views/products/goods_img_sorting_test1.php) |
| Model | `server116/application/models/Goods_m.php` — `get_goods_id_update()`, `get_goods_ocean_last_date()`, `get_goods_info()` |

#### 3) digitaloceanspaces 문자열이 포함된 파일 및 해당 줄
| 파일 | 줄 | 용도 |
|------|-----|------|
| tmp_114_app/controllers/products.php | 11285 | URL 파싱 시 호스트가 digitaloceanspaces인지 체크 (path 추출) |
| tmp_114_app/controllers/products.php | 11304 | S3 업로드 **endpoint** (유지) |
| tmp_114_app/controllers/products.php | 11331 | **서빙 URL** `$oceanPath` → **치환 완료** |
| server114/products_*.php (6개) | 각 11216~11267 부근 | 동일 패턴 — **치환 완료** |
| server114/server-116/.../Product.php | 3866, 3915 | endpoint 유지, oceanPath **치환 완료** |
| server116/application/controllers/Product.php | 3998, 4047 | **치환 완료** |
| go100/.../Product.php | 3748, 3797 | **치환 완료** |

#### 4) 이미지 저장 로직 요약
- **URL 조립 위치:** 각 Controller의 `digitaloceanApi()` 함수 내  
  - **실제 서빙 경로:** `https://newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/{filename}` (로컬/Cloudflare 서빙)  
  - `$oceanPath = "https://newtalk.kr/data/files/goods/goodscode/img/".$goodsCode."/";` 로 변경 완료  
  - (기존 DO: `https://newtalk.nyc3.cdn.digitaloceanspaces.com/img/YYYYMM/` → `/img/...` 경로는 404 확인됨)
- **DB 반영:** `Goods_m::get_goods_id_update($goodsCode, $oceanPath, $i, $j, $fileName)`  
  - `goods_detail` 테이블의 `GoodsEtc60`~`GoodsEtc74` 컬럼 값을 `$oceanPath.basename($value)` 형태로 갱신  
  - `GoodsEtc73`에는 `$oceanPath`만 저장

#### 5) 버튼별 처리 흐름
| 버튼 | 동작 |
|------|------|
| **이미지 저장** | `goodsDetailOpen()` → `http://shop.newtalk.kr/goods/detail_save?goodsId=...&de_skin=...` 새 창 오픈 (별도 서비스에서 HTML 생성 후 저장) |
| **상세설명 html 적용** | 동일 `detail_save` URL에 `&check=1` 추가하여 오픈 |
| **디지털 오션 전송** | `/products/digitaloceanApi` POST — 로컬 파일을 DO Spaces에 업로드한 뒤 `get_goods_id_update()`로 **서빙 URL(oceanPath)** 을 DB에 반영 → **이 oceanPath를 newtalk.kr로 변경함** |
| **저장하기** | `/products/goods_img_sorting_save1` — 이미지 순서(GoodsSortImg1~3)만 저장, URL 도메인과 무관 |

---

### A-4 백업
- **로컬 워크스페이스:** 아래 모든 파일에 대해 `*.bak.20260227_184358` 생성 완료.

### A-5 소스 수정 요약
- **변경 내용:** 서빙 URL을 **실제 로컬/Cloudflare 서빙 경로**로 통일. 업로드용 `endpoint`(`https://nyc3.digitaloceanspaces.com`)는 변경하지 않음.
- **실제 이미지 주소:** `https://newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/{filename}` (검증 완료: bl5890k62, cd3288k48, ns916k36)
- **Before:** `$oceanPath = "https://newtalk.nyc3.cdn.digitaloceanspaces.com/".$d;` (또는 `https://newtalk.kr/".$d`)  
- **After:** `$oceanPath = "https://newtalk.kr/data/files/goods/goodscode/img/".$goodsCode."/";`

#### 변경 파일 목록 (경로, 변경 전/후)
| 파일 | 변경 후 (서빙 base URL) |
|------|-------------------------|
| tmp_114_app/controllers/products.php | `https://newtalk.kr/data/files/goods/goodscode/img/".$goodsCode."/` |
| server114/products_complete.php | 동일 |
| server114/products_current.php | 동일 |
| server114/products_error.php | 동일 |
| server114/products_final.php | 동일 |
| server114/products_original.php | 동일 |
| server114/products_modified.php | 동일 |
| server114/server-116/newpigup3/application/controllers/Product.php | 동일 |
| server116/application/controllers/Product.php | 동일 |
| go100/server-116/newpigup3/application/controllers/Product.php | 동일 |

---

## PART B: DB 기존 데이터 일괄 치환

### B-1 V1 DB 접속
```bash
mysql -h 127.0.0.1 -P 3306 -u root -p autoda
```

### B-2 영향 범위 조사 (SELECT만 실행)

**1) 텍스트 계열 컬럼 목록 (참고용)**
```sql
SELECT TABLE_NAME, COLUMN_NAME
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'autoda'
AND DATA_TYPE IN ('varchar','text','mediumtext','longtext');
```

**2) goods_detail — DO URL 포함 건수 (GoodsEtc60~74)**
```sql
SELECT COUNT(*) AS cnt FROM goods_detail
WHERE CONCAT(IFNULL(GoodsEtc60,''), IFNULL(GoodsEtc61,''), IFNULL(GoodsEtc62,''), IFNULL(GoodsEtc63,''), IFNULL(GoodsEtc64,''), IFNULL(GoodsEtc65,''), IFNULL(GoodsEtc66,''), IFNULL(GoodsEtc67,''), IFNULL(GoodsEtc68,''), IFNULL(GoodsEtc69,''), IFNULL(GoodsEtc70,''), IFNULL(GoodsEtc71,''), IFNULL(GoodsEtc72,''), IFNULL(GoodsEtc73,''), IFNULL(GoodsEtc74,'')) LIKE '%digitaloceanspaces.com%';
```

**3) 테이블·컬럼별 DO URL 포함 건수 (예시 — 테이블명/컬럼명은 실제 스키마에 맞게 수정)**
```sql
-- goods_detail 각 컬럼별 (필요 시)
SELECT 'goods_detail' AS tbl, 'GoodsEtc60' AS col, COUNT(*) AS cnt FROM goods_detail WHERE GoodsEtc60 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc61', COUNT(*) FROM goods_detail WHERE GoodsEtc61 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc62', COUNT(*) FROM goods_detail WHERE GoodsEtc62 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc63', COUNT(*) FROM goods_detail WHERE GoodsEtc63 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc64', COUNT(*) FROM goods_detail WHERE GoodsEtc64 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc65', COUNT(*) FROM goods_detail WHERE GoodsEtc65 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc66', COUNT(*) FROM goods_detail WHERE GoodsEtc66 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc67', COUNT(*) FROM goods_detail WHERE GoodsEtc67 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc68', COUNT(*) FROM goods_detail WHERE GoodsEtc68 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc69', COUNT(*) FROM goods_detail WHERE GoodsEtc69 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc70', COUNT(*) FROM goods_detail WHERE GoodsEtc70 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc71', COUNT(*) FROM goods_detail WHERE GoodsEtc71 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc72', COUNT(*) FROM goods_detail WHERE GoodsEtc72 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc73', COUNT(*) FROM goods_detail WHERE GoodsEtc73 LIKE '%digitaloceanspaces.com%'
UNION ALL SELECT 'goods_detail','GoodsEtc74', COUNT(*) FROM goods_detail WHERE GoodsEtc74 LIKE '%digitaloceanspaces.com%';
```

**4) goods 테이블에 대표이미지/상세설명 컬럼이 있는 경우**
```sql
-- 컬럼명은 실제 스키마에 맞게 변경 (예: GoodsImage, GoodsDetail 등)
-- SELECT COUNT(*) FROM goods WHERE GoodsImage LIKE '%digitaloceanspaces.com%';
-- SELECT COUNT(*) FROM goods_detail WHERE GoodsDetail LIKE '%digitaloceanspaces.com%';
```

### B-3 채팅 보고 형식
조사 후 아래 형식으로 채팅 공유:
| 테이블 | 컬럼 | DO URL 포함 건수 |
|--------|------|------------------|
| goods_detail | GoodsEtc60 | ... |
| ... | ... | ... |
**총 영향 행 수:** ___건

### B-4 승인 후 백업 + UPDATE 실행
**DB 백업 (영향 테이블 dump)**
```bash
mysqldump -h 127.0.0.1 -P 3306 -u root -p autoda goods_detail > /root/backup/v1_imageURL_before_20260227.sql
```

**URL 형식 설명**
- **기존 DO URL:** `https://newtalk.nyc3.cdn.digitaloceanspaces.com/img/YYYYMM/filename` (예: `.../img/202602/bl5890k62-600_1.jpg`)
- **변환 후:** `https://newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/filename` (예: `.../img/bl5890k62/bl5890k62-600_1.jpg`)
- 파일명에서 상품코드 추출: `filename`의 첫 번째 `-` 앞 부분 (예: `bl5890k62-600_1.jpg` → `bl5890k62`)

**UPDATE — 경로 변환 (컬럼별 실행)**  
아래는 DO URL을 실제 서빙 경로로 변환. `SUBSTRING_INDEX(컬럼, '/', -1)` = filename, `SUBSTRING_INDEX(filename, '-', 1)` = GoodsCode.
```sql
UPDATE goods_detail SET GoodsEtc60 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc60, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc60, '/', -1)) WHERE GoodsEtc60 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc61 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc61, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc61, '/', -1)) WHERE GoodsEtc61 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc62 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc62, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc62, '/', -1)) WHERE GoodsEtc62 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc63 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc63, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc63, '/', -1)) WHERE GoodsEtc63 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc64 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc64, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc64, '/', -1)) WHERE GoodsEtc64 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc65 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc65, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc65, '/', -1)) WHERE GoodsEtc65 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc66 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc66, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc66, '/', -1)) WHERE GoodsEtc66 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc67 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc67, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc67, '/', -1)) WHERE GoodsEtc67 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc68 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc68, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc68, '/', -1)) WHERE GoodsEtc68 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc69 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc69, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc69, '/', -1)) WHERE GoodsEtc69 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc70 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc70, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc70, '/', -1)) WHERE GoodsEtc70 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc71 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc71, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc71, '/', -1)) WHERE GoodsEtc71 LIKE '%digitaloceanspaces.com%';
UPDATE goods_detail SET GoodsEtc72 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc72, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc72, '/', -1)) WHERE GoodsEtc72 LIKE '%digitaloceanspaces.com%';
-- GoodsEtc73: base path만 저장된 경우. goods 테이블과 조인하여 GoodsCode로 새 base 설정
UPDATE goods_detail gd
INNER JOIN goods g ON gd.goods_id = g.id
SET gd.GoodsEtc73 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', LOWER(g.GoodsCode), '/')
WHERE gd.GoodsEtc73 LIKE '%digitaloceanspaces.com%' AND gd.GoodsEtc73 != '';
UPDATE goods_detail SET GoodsEtc74 = CONCAT('https://newtalk.kr/data/files/goods/goodscode/img/', SUBSTRING_INDEX(SUBSTRING_INDEX(GoodsEtc74, '/', -1), '-', 1), '/', SUBSTRING_INDEX(GoodsEtc74, '/', -1)) WHERE GoodsEtc74 LIKE '%digitaloceanspaces.com%';
```
각 실행 후 `affected rows` 기록.

---

## PART C: 검증

### C-1 DB 검증
```sql
SELECT COUNT(*) FROM goods_detail WHERE CONCAT(IFNULL(GoodsEtc60,''), IFNULL(GoodsEtc61,''), ... , IFNULL(GoodsEtc74,'')) LIKE '%digitaloceanspaces.com%';
```
→ 기대값: 0

### C-2 페이지 검증
- 이미지 정렬 페이지에서 테스트 상품으로:
  1. **이미지 저장** 버튼 클릭 → DB 저장 URL이 newtalk.kr인지 확인
  2. **상세설명 HTML 적용** 버튼 클릭 → HTML 내 IMG src가 newtalk.kr인지 확인
  3. 상품 수정 페이지에서 이미지 정상 표시 여부 확인

### C-3 이미지 실제 로딩
```bash
# 실제 서빙 경로 (검증 완료)
curl -I "https://newtalk.kr/data/files/goods/goodscode/img/bl5890k62/bl5890k62-600_1.jpg"
curl -I "https://newtalk.kr/data/files/goods/goodscode/img/cd3288k48/cd3288k48-600_1.jpg"
```
→ 기대: HTTP 200.  
※ `https://newtalk.kr/img/202602/...` 경로는 404이므로 사용하지 않음.

---

## PART D: 보고서 요약

### 소스 백업 경로 (로컬)
- `{각 파일 경로}.bak.20260227_184358`  
  예: `/root/tmp_114_app/controllers/products.php.bak.20260227_184358`

### DB 백업 경로
- 서버에서 실행 시: `/root/backup/v1_imageURL_before_20260227.sql` (실제 테이블 dump 후 경로 기입)

### DB UPDATE 결과 (테이블별 affected rows)
- (B-4 실행 후 채팅/보고서에 기입)

### 검증 결과
- (C-1~C-3 실행 후 채팅/보고서에 기입)

---

## 실행 순서 요약
1. **A-1~A-3** 탐색·분석·보고 → 채팅 공유 ✅  
2. **A-4~A-5** 백업·소스 수정 ✅ (로컬 완료; 114 서버 반영은 배포 시 적용)  
3. **B-1~B-3** DB 조사·보고 → 채팅 공유 (114 서버 SSH 접속 후 실행)  
4. **B-4** DB 백업·UPDATE (승인 후 실행)  
5. **C-1~C-3** 검증  
6. **D** 보고서 최종 갱신
