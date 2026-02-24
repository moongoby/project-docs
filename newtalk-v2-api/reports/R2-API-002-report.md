# R2-API-002 보고서: 브랜드 페이지 API

**문서번호**: R2-API-002  
**작성일**: 2026-02-24  
**브랜치**: feature/R2-API-002-brand-page  
**목표 버전**: v1.6.0

---

## §1. 생성·수정된 파일 목록

### 백엔드
| 구분 | 경로 |
|------|------|
| 신규 | database/migrations/2026_02_24_090000_create_brand_pages_table.php |
| 신규 | app/Models/BrandPage.php |
| 신규 | app/Models/ProductImage.php |
| 신규 | app/Http/Controllers/Api/BrandPageController.php |
| 신규 | database/seeders/BrandPageSeeder.php |
| 수정 | app/Models/User.php (hasOne BrandPage) |
| 수정 | app/Models/Product.php (images 관계, ProductImage) |
| 수정 | routes/api.php (brands 공개 4 EP, 인증 2 EP) |
| 수정 | database/seeders/DatabaseSeeder.php (BrandPageSeeder 호출) |
| 수정 | app/Http/Controllers/Api/FeedController.php (author.brand_slug, product.wholesale_name, author.brandPage·product.user 관계 로드) |

---

## §2. API 엔드포인트

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | /api/brands | 브랜드 목록 (페이지네이션, ?q= 검색) | 공개 |
| GET | /api/brands/{slug} | 브랜드 상세 (products 20, feed_items 10 포함) | 공개 |
| GET | /api/brands/{slug}/products | 브랜드 상품 목록 (cursor, ?category=, ?min_price=, ?max_price=) | 공개 |
| GET | /api/brands/{slug}/feed | 브랜드 피드 (cursor) | 공개 |
| POST | /api/brands/{slug}/follow | 팔로우 토글 | auth:sanctum |
| PUT | /api/brands/me | 내 브랜드 수정/생성 (wholesale만) | auth:sanctum |

---

## §3. DB 스키마 (brand_pages)

- id (bigIncrements), user_id (unique FK → users), brand_name, slug (unique), logo_url, cover_url, description, business_info (json), sns_links (json), is_active, follower_count, product_count, timestamps, softDeletes

---

## §4. 시드·실행

- BrandPageSeeder: wholesale@newtalk.kr 계정으로 brand_page 1건 (slug: test-wholesale, brand_name: 테스트 도매 브랜드)
- 마이그레이션: `docker compose --env-file .env.docker exec app php artisan migrate --force`
- 시드: `docker compose --env-file .env.docker exec app php artisan db:seed --class=BrandPageSeeder`

---

## §5. HTTP 테스트 결과 (예시)

서버에서 아래 순서로 실행 후 결과 기록.

```bash
# 토큰
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"wholesale@newtalk.kr","password":"[.env.docker 참조]"}' | jq -r '.token')

# 브랜드 목록
curl -s http://127.0.0.1:8080/api/brands
# 기대: { "data": [...], "current_page": 1, "last_page": 1, ... }

# 브랜드 상세
curl -s http://127.0.0.1:8080/api/brands/test-wholesale
# 기대: { "data": { "id", "slug", "brand_name", "products", "feed_items", ... } }

# 브랜드 상품
curl -s "http://127.0.0.1:8080/api/brands/test-wholesale/products"

# 팔로우
curl -s -X POST http://127.0.0.1:8080/api/brands/test-wholesale/follow \
  -H "Authorization: Bearer $TOKEN"

# 내 브랜드 수정
curl -s -X PUT http://127.0.0.1:8080/api/brands/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"brand_name":"수정 테스트","description":"수정된 설명"}'
```

---

## §6. Git SHA

- (서버 푸시 후 기록)  
- 브랜치: feature/R2-API-002-brand-page
