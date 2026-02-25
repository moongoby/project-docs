# 뉴톡 상세페이지/배너/편집 이미지 구조 파악 보고서

**작성일시:** 2026-02-24 KST  
**프로젝트:** newtalk-image-auto (nas-image)  
**목적:** 자동화 파이프라인 문서화를 위한 편집물 구조 파악

---

## 사전 준수사항 확인

- [x] `docs/CONTEXT.md` 읽음
- [x] `.cursorrules` 읽음 (116/114 서버, V1 보호, 보고서 규칙 등)
- [x] 모든 시간 KST 기준

---

## 1. 114서버 — 상품 이미지 폴더 구조

### 1.1 실행 결과 (STEP 1·2)

**상태:** **미실행** — 현재 환경에서 114 서버 SSH 접속 불가  
- 원인: `~/.ssh/id_ed25519` 키 없음 (Permission denied)  
- 명령: `ssh -p 7916 -i ~/.ssh/id_ed25519 nasync@114.207.244.86`

### 1.2 코드/설정 기반 추정 구조

116 서버 PHP 설정 및 코드에서 사용하는 **이미지 경로**는 아래와 같다.

| 구분 | 116 서버 설정 (config) | 114 서버 경로 (지시서 기준) |
|------|------------------------|-----------------------------|
| 상품코드별 이미지 디렉터리 | `user_goodscode_img_dir` = `/home/danharoo/www/data/files/goods/goodscode/img/` | `/home/danharoo/www/data/files/goods/goodscode/img/` |
| URL 경로 | `user_goodscode_img_url` = `/data/files/goods/goodscode/img/` | — |
| 업로드 서버 도메인 | `upload_serve_domain` = `https://www.newtalk.kr` | — |
| 114 업로드 경로 참조 | `upload_serve_path_114` = `114.207.244.86/` | — |

- **상품 하나당 폴더:** `.../goodscode/img/{GoodsCode}/`  
  - 예: `.../goodscode/img/ns916k36/`
- **썸네일:** 동일 폴더 내 `thumbnail/` 서브디렉터리 사용  
  - `Upload_handler.php` 등에서 `thumbnail` 버전 생성 후 업로드

### 1.3 파일명 패턴 (코드 기준)

`Common_m.php` 등에서 사용하는 **기본 이미지 파일명** 규칙:

| 용도 | 파일명 패턴 | 비고 |
|------|-------------|------|
| 대표/종합몰 JPG | `{GoodsCode}-600_1.jpg`, `-600_2.jpg` … `-600_6.jpg` | 소문자 GoodsCode |
| 리스트/부가 | `-270.gif`, `-list2.jpg`, `-220.jpg` | 부가이미지 11·12·15·20·22 등 |
| 상세 정렬용 | 폴더 내 원본 파일명 그대로 | DB에 `GoodsSortImg1`~`4`에 `\|\|` 구분 저장 |

- **배너/인트로/부가설명** 전용 **파일명 접미사**는 코드에 없음.  
- “인트로/모델/제품” 구분은 **DB 정렬 필드**로만 관리됨 (아래 3절).

---

## 2. 배너/인트로/부가설명 이미지 파일명 규칙

### 2.1 상품 상세용 (goodscode/img)

- **파일명 규칙:**  
  - 공통 접두: 상품코드(소문자) + `-` + 해상도/용도 접미사.  
  - 예: `ns916k36-600_1.jpg`, `ns916k36-270.gif`, `ns916k36-list2.jpg`.  
- **배너/인트로/부가설명** 구분:  
  - **파일명에 `banner`, `intro`, `detail`, `desc` 등 고정 접미사 없음.**  
  - `find ... *banner* *intro* *detail*` 같은 패턴 검색은 114에서 직접 실행 시 확인 필요.

### 2.2 상세페이지 “인트로/모델/제품” 구분 (116 DB)

- **인트로 정렬(1)** = `goods_detail.GoodsSortImg1`  
- **모델사진 정렬** = `GoodsSortImg2`  
- **제품사진 정렬** = `GoodsSortImg3`  
- **MO(모바일) 정렬** = `GoodsSortImg4`  

각 필드는 **파일명을 `||`로 이어 붙인 문자열** (예: `파일1.jpg||파일2.jpg`).  
즉, “인트로/배너/부가설명”은 **같은 폴더의 같은 파일명**을 쓰고, **정렬 그룹만 DB로 나눔**.

### 2.3 도매 배너 (메인/앱 배너)

- **파일명 규칙:** 코드에서 고정 패턴 없음. 업로드 시 저장된 파일명 그대로.  
- **저장 경로 (116 config):**  
  - PC: `banner_upload_dir` = `/home/newpigup3/www/data/files/notice/banner/`  
  - 모바일: `banner_mobile_upload_dir` = `.../notice/m_banner/`  
- **URL:** `/www/data/files/notice/banner/`, `/www/data/files/notice/m_banner/`  
- 이 경로는 **상품 goodscode 이미지와 별도**이며, `goodscode/img` 아래가 아님.

---

## 3. 116서버 — 상세페이지 생성/저장 PHP 코드

### 3.1 컨트롤러·라우트

| 기능 | 컨트롤러 | 메서드 | 비고 |
|------|----------|--------|------|
| 상품 상세 페이지 | `Product` | `detail()` | 뷰: `product/detail` |
| 상세페이지 “생성” 진입 (이미지 정렬 1) | `Product` | `goods_img_sorting_test1()` | 뷰: `products/goods_img_sorting_test1` |
| 상세페이지 “생성” 진입 (이미지 정렬 2) | `Product` | `goods_img_sorting_test2()` | 뷰: `products/goods_img_sorting_test2` |
| 인트로/모델/제품 정렬 저장 | `Product` | `goods_img_sorting_save1()` | POST, `goods_detail` 업데이트 |
| MO 정렬 저장 | `Product` | `goods_img_sorting_save2()` | POST, `GoodsSortImg4` |
| 이미지 등록 화면 | `Product` | `goods_img_upload()` | `Upload_handler` 사용 |
| 이미지 압축 | `Product` | `goods_code_image_compress()` | `Products_handler` |
| 상품 등록/수정 | `Product` | `regist_update()` 등 | 상품 마스터 + `goods_detail` |

### 3.2 상세페이지 생성 흐름 (이미지 정렬)

1. **진입 URL**  
   - `https://www.newtalk.kr/products/goods_img_sorting_test1/{GoodsCode}`  
   - `https://www.newtalk.kr/products/goods_img_sorting_test2/{GoodsCode}`  
2. **이미지 소스**  
   - 디렉터리: `user_goodscode_img_dir` + `{GoodsCode}/`  
   - 썸네일 URL: `upload_serve_domain` + `user_goodscode_img_url` + `{GoodsCode}/thumbnail/`  
3. **DB 조회**  
   - `goods` + `goods_detail` JOIN, `GoodsSortImg1`~`GoodsSortImg4` 읽어서 `sortable2`~`sortable4` 등으로 뷰에 전달.  
4. **저장**  
   - `goods_img_sorting_save1`: `GoodsSortImg1`(인트로), `GoodsSortImg2`(모델), `GoodsSortImg3`(제품).  
   - `goods_img_sorting_save2`: `GoodsSortImg4`(MO).

### 3.3 DB 필드 (상세/이미지)

- **goods_detail**  
  - `GoodsSortImg1` = 인트로 순서 (`||` 구분)  
  - `GoodsSortImg2` = 모델사진 순서  
  - `GoodsSortImg3` = 제품사진 순서  
  - `GoodsSortImg4` = MO 순서  
  - `GoodsEtc60` = 대표이미지 URL  
  - `GoodsEtc61` = 종합몰 JPG  
  - `GoodsEtc62`~`GoodsEtc74` = 부가이미지 URL 등 (Common_m.php 기본값 참고)

### 3.4 이미지 업로드/처리 라이브러리

| 라이브러리 | 경로 | 역할 |
|------------|------|------|
| `Upload_handler` | `application/libraries/Upload_handler.php` | 상품코드별 업로드, FTP 연동, 썸네일 생성 |
| `Products_handler` | `application/libraries/Products_handler.php` | 이미지 압축, 상품 이미지 확인 |
| `product_hander` / `Pro_handler` | `application/libraries/` | 상품 등록 시 이미지 처리·압축 |

- 업로드 디렉터리: `Upload_handler`에 전달되는 `upload_dir` = `user_goodscode_img_dir` + `{GoodsCode}/` (실제 값은 config의 `user_goodscode_img_dir`).

---

## 4. 웹디자이너 편집물 업로드 경로

### 4.1 상품 상세용 (제품컷·모델컷·인트로·부가 등)

- **업로드 화면:**  
  - `https://www.newtalk.kr/products/goods_img/{GoodsCode}`  
- **실제 저장 경로 (116 설정 기준):**  
  - `/home/danharoo/www/data/files/goods/goodscode/img/{GoodsCode}/`  
- **114 동기화 경로 (지시서 기준):**  
  - `/home/danharoo/www/data/files/goods/goodscode/img/`  
- 웹디자이너는 위 URL에서 해당 상품코드 폴더로 이미지를 올리고,  
  이후 **상세페이지 생성1/2** 화면에서 “인트로/모델/제품/MO”로 드래그하여 순서만 지정함.

### 4.2 도매 배너 (메인/앱 배너)

- **업로드 경로:**  
  - PC: `banner_upload_dir` → `/home/newpigup3/www/data/files/notice/banner/`  
  - 모바일: `banner_mobile_upload_dir` → `.../notice/m_banner/`  
- **관리 화면:**  
  - `/root/banner_manage` (배너 등록/수정/삭제)  
  - 컨트롤러: `Root::banner_make()`, `banner_modify()`  
  - 업로드: `file_img_upload($_FILES['image'], ...)`, `file_img_upload($_FILES['m_image'], ...)`  
- 이 경로는 **상품 goodscode 이미지와 무관**하며, **편집물 자동화 파이프라인**에서는 상품 폴더(`goodscode/img`)만 대상으로 하면 됨.

---

## 5. CDN/이미지 URL 패턴

### 5.1 도메인·경로 정리

| 용도 | URL 패턴 | 근거 |
|------|----------|------|
| 상품 이미지 (기본) | `http://newtalk.kr/data/files/goods/img/{GoodsCode}/{파일명}` | Common_m.php 기본값 (대표/부가이미지) |
| 상품 이미지 (실제 서빙) | `https://www.newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/...` | config `upload_serve_domain` + `user_goodscode_img_url` |
| 상품 이미지 (CDN) | `https://cdn.newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/{파일명}` | STEP6_v3_0h_canary_switch.php |
| 썸네일 | `.../goodscode/img/{GoodsCode}/thumbnail/{파일명}` | Product.php, 뷰 등 |
| 회원별 상품 이미지 | `https://www.newtalk.kr/data/files/goods/{user_id}/...` | product_sample_mng_detail 등 |

### 5.2 코드 인용

- **Common_m.php (기본 이미지 URL):**  
  `http://newtalk.kr/data/files/goods/img/`.strtolower($data['GoodsCode']).`-600_1.jpg` 등  
- **상세 적용 시:**  
  `str_replace("{GoodsImgPath}", "http://newtalk.kr/data/files/goods/img/".$data['GoodsCode']."/", ...)`  
- **CDN 전환 스크립트:**  
  `$baseUrl = 'https://cdn.newtalk.kr/data/files/goods/goodscode/img/';`

### 5.3 뷰에서의 이미지 경로

- **product_mng.php:**  
  - 예시: `/data/files/goods/goodscode/img/ns916k36/thumbnail/ns916k36-600_1.jpg`  
- **product_sample_mng_detail.php:**  
  - `https://www.newtalk.kr/data/files/goods/{$goods->user_id}/$imgValue`  
  - 입력값: `newtalk.kr/data/files/goods/img/`+imgCode+`/`+imgCode+txtArr[i]

---

## 6. 요약 및 자동화 시 참고사항

| 항목 | 내용 |
|------|------|
| 114 상품 폴더 | `/home/danharoo/www/data/files/goods/goodscode/img/` 아래에 `{GoodsCode}/` 단위, 썸네일은 `thumbnail/` |
| 파일명 규칙 | `{goodscode}-600_1.jpg` 등; 인트로/배너/부가는 **파일명이 아니라 DB 정렬 필드**로 구분 |
| 상세 생성/저장 | `Product::goods_img_sorting_test1/2`, `goods_img_sorting_save1/2`, `goods_detail.GoodsSortImg1`~`4` |
| 웹디자이너 업로드 | 상품: `products/goods_img/{GoodsCode}` → goodscode/img; 배너: `/root/banner_manage` → notice/banner, m_banner |
| CDN URL | `https://cdn.newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/{파일명}` |

**114 서버 STEP 1·2 (실제 디렉터리 목록·파일명 패턴·배너/인트로 검색):**  
현재 환경에서 SSH 키 미비로 미실행. 114에 SSH 접속 가능한 환경에서 아래를 직접 실행해 보완 권장.

```bash
ssh -p 7916 -i ~/.ssh/id_ed25519 nasync@114.207.244.86
ls -lt /home/danharoo/www/data/files/goods/goodscode/img/ | head -20
# 샘플 폴더 하나 선택 후
SAMPLE_DIR=$(ls -t /home/danharoo/www/data/files/goods/goodscode/img/ | head -1)
ls -la /home/danharoo/www/data/files/goods/goodscode/img/$SAMPLE_DIR/
find /home/danharoo/www/data/files/goods/goodscode/img/$SAMPLE_DIR/ -type f | sort
find /home/danharoo/www/data/files/goods/goodscode/img/ -name "*banner*" -o -name "*intro*" -o -name "*detail*" 2>/dev/null | head -20
```

---

*보고서 끝*
