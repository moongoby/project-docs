# R1-TASK-002 완료 보고서 — 상품 CRUD API

**문서번호:** NT-V2-R1-TASK-002  
**작성일:** 2026-02-21  
**대상:** 뉴톡 V2 (Cursor AI 실행 결과)

---

## 1. 작업 요약

- 상품 관련 Model 6종 + WholesaleProfile 생성
- 상품 CRUD API (목록/상세/등록/수정/소프트삭제) 구현
- 채널·옵션·카테고리·상세 연동 생성/수정
- 상품 이미지 업로드·삭제 API
- CategorySeeder 7개 기본 카테고리
- 역할 기반 접근: 등록/수정 admin|md, 삭제 admin, 조회 인증 사용자

---

## 2. Model 생성 결과

| 모델 | 파일 | 비고 |
|------|------|------|
| Product | `src/app/Models/Product.php` | SoftDeletes, fillable/casts/관계 정의 |
| ProductChannel | `src/app/Models/ProductChannel.php` | channel_data json, synced_at datetime |
| ProductImage | `src/app/Models/ProductImage.php` | is_primary, file_size, sort_order |
| ProductOption | `src/app/Models/ProductOption.php` | stock, additional_price integer |
| ProductDetail | `src/app/Models/ProductDetail.php` | html_content, version |
| Category | `src/app/Models/Category.php` | code/slug, parent_id, sort_order, is_active |
| WholesaleProfile | `src/app/Models/WholesaleProfile.php` | products FK용 |

마이그레이션: wholesale_profiles, categories, products, product_channels, product_images, product_options, product_details, product_categories — 서버에서 이미 적용됨(Batch 2).

---

## 3. route:list (api/products 관련)

```
GET|HEAD   api/products ............................ products.index › Api\ProductController@index
POST       api/products ............................ products.store › Api\ProductController@store
GET|HEAD   api/products/{product} .................. products.show › Api\ProductController@show
PUT|PATCH  api/products/{product} ................. products.update › Api\ProductController@update
DELETE     api/products/{product} ................ products.destroy › Api\ProductController@destroy
POST       api/products/{product}/images .......... Api\ProductImageController@store
DELETE     api/products/{product}/images/{image} .. Api\ProductImageController@destroy
```
총 7개 라우트 등록됨.

---

## 4. CategorySeeder 실행 결과

```bash
docker compose --env-file .env.docker exec app php artisan db:seed --class=CategorySeeder --force
```
- **결과:** `INFO  Seeding database.` 정상 완료
- **내용:** 아우터, 상의, 하의, 원피스, 스커트, 셋업, 악세서리 (code=slug 형식, sort_order 1~7, is_active true)
- **비고:** 기존 DB의 categories 테이블이 `code` 컬럼을 사용해 시더를 code 기준 updateOrCreate로 수정하여 실행함.

---

## 5. API 테스트 결과 (curl)

### 5-1. 관리자 로그인 → 토큰 획득
- **요청:** `POST /api/auth/login` (admin@newtalk.kr / [REDACTED])
- **결과:** 200, `message: 로그인 성공`, `token` 수신

### 5-2. 8-1 상품 등록
- **요청:** `POST /api/products` (Bearer ADMIN_TOKEN), name/product_code/options/channels/html_content 등
- **응답:** **HTTP 201**
- **body 요약:** `message: 상품 등록 완료`, product (id:1, options 2개, channels 2개, detail 1개)

### 5-3. 8-2 상품 목록 조회
- **요청:** `GET /api/products?page=1&per_page=10` (Bearer ADMIN_TOKEN)
- **응답:** **HTTP 200**
- **body 요약:** pagination (current_page, data[], per_page, total 등), data에 상품 + wholesale_profile, channels, images

### 5-4. 8-3 상품 상세 조회
- **요청:** `GET /api/products/1` (Bearer ADMIN_TOKEN)
- **응답:** **HTTP 200**
- **body 요약:** product + user, wholesale_profile, channels, images, options, detail, categories

### 5-5. 8-4 상품 수정
- **요청:** `PUT /api/products/1` (name 수정, retail_price 42000, options 3개로 변경)
- **응답:** **HTTP 200**
- **body 요약:** `message: 상품 수정 완료`, product (name 수정됨, options 3개 반영)

### 5-6. 8-5 이미지 업로드
- **요청:** `POST /api/products/1/images` (multipart: image=test.jpg, type=product_cut, is_primary=1)
- **응답:** **HTTP 201**
- **body 요약:** `message: 이미지 업로드 완료`, image (path, filename, is_primary: true 등)

### 5-7. 8-6 소매 계정 상품 등록 시도 (차단)
- **요청:** `POST /api/products` (Bearer RETAIL_TOKEN), 최소 필드만
- **응답:** **HTTP 403**
- **body 요약:** `This action is unauthorized.` (AccessDeniedHttpException)

### 5-8. 8-7 소매 계정 목록 조회 (허용)
- **요청:** `GET /api/products` (Bearer RETAIL_TOKEN)
- **응답:** **HTTP 200**
- **body 요약:** 목록 정상 반환

### 5-9. 8-8 상품 삭제 (관리자)
- **요청:** `DELETE /api/products/1` (Bearer ADMIN_TOKEN)
- **응답:** **HTTP 200**
- **body 요약:** `message: 상품 삭제 완료`

### 5-10. 삭제 후 상세 조회 (소프트삭제 확인)
- **요청:** `GET /api/products/1` (Bearer ADMIN_TOKEN)
- **응답:** **HTTP 404**
- **body 요약:** `No query results for model [App\Models\Product] 1` (NotFoundHttpException) — 소프트삭제로 조회 불가 확인

---

## 6. V1 영향

- **확인:** `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86`
- **결과:** **200** — V1 서비스 정상, 영향 없음.

---

## 7. Git 커밋·푸시 결과

- **브랜치:** `feature/R1-TASK-002-products` (develop 기준 생성)
- **커밋:** `876f4b3` — 메시지: `[R1-002] feat: 상품 CRUD API + 이미지 업로드 + 채널/옵션 관리` (21 files changed, 821 insertions)
- **푸시:** `git push -u origin feature/R1-TASK-002-products` 성공
- **원격:** `github.com:moongoby/newtalk-v2-api-.git` 에 브랜치 푸시 완료

---

## 8. 비고

- 상품 삭제 후 동일 ID로 재등록 가능 (product_code는 unique 유지).
- 이미지 업로드 시 `storage/app/public` 사용, public 디스크 링크 필요 시 `php artisan storage:link` 확인.
- categories 테이블이 기존 스키마(code, is_active)를 사용 중이어서 Category 모델 fillable에 code, is_active 포함, CategorySeeder는 code 기준으로 시딩하도록 반영함.

---

**보고서 끝.**
