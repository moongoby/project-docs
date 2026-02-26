# R4-API-003 완료 보고서 — AI 맞춤 피드 + 추천 엔진

**작성일시**: 2026-02-26 KST  
**버전**: v3.3.0  
**커밋 접두사**: `[R4-API-003]`

---

## 요약

| 항목 | 내용 |
|------|------|
| 테이블 | 3개 (`user_interests`, `product_scores`, `trend_snapshots`) |
| 모델 | 3개 (`UserInterest`, `ProductScore`, `TrendSnapshot`) + `Category` (추가) |
| 서비스 | `RecommendationService`, `TrendService` |
| 엔드포인트 | 7개 (추천 3 + 트렌드 4) |
| FeedController | 개편 — 로그인 시 팔로잉 70% + AI 추천 30% 혼합 |
| 스케줄러 | 3개 (매시 점수, 매일 03:00 스냅샷, 매주 관심도 감쇠) |

---

## STEP 1: 마이그레이션 (3개)

| 파일 | 테이블 | 비고 |
|------|--------|------|
| `database/migrations/2026_02_26_320001_create_user_interests_table.php` | `user_interests` | user_id, interest_type, interest_value, score, interaction_count, last_interacted_at |
| `database/migrations/2026_02_26_320002_create_product_scores_table.php` | `product_scores` | product_id(unique), popularity_score, trend_score, *_count_7d, calculated_at |
| `database/migrations/2026_02_26_320003_create_trend_snapshots_table.php` | `trend_snapshots` | snapshot_date, type(category/keyword/brand/product), key, rank, score, metadata |

---

## STEP 2: 모델 (3+1)

- **UserInterest**: fillable, casts, `user()`, `scopeOfType`, `scopeTopScored`
- **ProductScore**: fillable, casts, `product()`, `scopeOrderByPopularity`, `scopeOrderByTrend`
- **TrendSnapshot**: fillable, casts, `scopeOfType`, `scopeOnDate`, `scopeTopRanks`
- **Category** (신규): `products()` 관계 — 트렌드/추천용
- **Product**: `productScore()`, `categories()` 관계 추가
- **User**: `userInterests()` 관계 추가

---

## STEP 3: 서비스

### RecommendationService (`app/Services/RecommendationService.php`)

| 메서드 | 설명 |
|--------|------|
| `getPersonalizedFeed(userId, cursor?, perPage=20)` | 팔로잉 70% + AI 추천 30% 혼합, 인터리브·중복 제거 |
| `getRecommendedProducts(userId, limit=20)` | 관심사 기반 카테고리/브랜드 + popularity_score, 찜·주문 제외 |
| `getSimilarProducts(productId, limit=10)` | 동일 카테고리 + 가격 ±30% + product_scores 상위 |
| `updateUserInterests(userId, interactionType, data)` | view_product +0.1, wishlist +0.5, order +2.0, follow +1.0, feed_like +0.3 |
| `decayAllInterests()` | 7일 지난 관심도 × 0.9 (스케줄 주간) |

### TrendService (`app/Services/TrendService.php`)

| 메서드 | 설명 |
|--------|------|
| `calculateProductScores()` | 전체 상품 popularity/trend 재계산 (views×0.1 + wishlists×0.5 + orders×2.0 + likes×0.3) |
| `generateTrendSnapshot()` | 일일 스냅샷: 카테고리 TOP 20, 키워드 TOP 50, 브랜드 TOP 20, 상품 TOP 100 |
| `getTrending(type, limit, days=7)` | 트렌드 목록 조회 |
| `getKeywordTrends(limit=30)` | 인기 검색어(키워드) |
| `getCategoryTrends(limit=20)` | 인기 카테고리 |
| `getTrendingProducts(limit=100)` | 인기 상품 |

---

## STEP 4: FeedController 개편

- **index()**: 로그인 사용자 → `RecommendationService::getPersonalizedFeed()` 호출, 70/30 혼합 피드 반환
- **show()**: 상품 조회 시 `updateUserInterests($userId, 'view_product', ['product_id' => $productId])` 호출
- **toggleLike()**: 좋아요 시 `updateUserInterests($userId, 'feed_like', ['brand' => $brandSlug])` 호출

**이벤트 기반 관심사 갱신 연동**
- **WishlistController** (store, toggle): 찜 추가 시 `updateUserInterests(..., 'wishlist', ['product_id'])`
- **BrandPageController** (toggleFollow): 브랜드 팔로우 시 `updateUserInterests(..., 'follow', ['brand' => slug])`
- **OrderController** (store): 주문 생성 시 주문 항목별 `updateUserInterests(..., 'order', ['product_id'])`

---

## STEP 5·6: 컨트롤러·라우트

### RecommendationController (`app/Http/Controllers/Api/RecommendationController.php`)

| 메서드 | 엔드포인트 | 인증 |
|--------|------------|------|
| `products` | GET /api/recommendations/products | auth:sanctum |
| `similar` | GET /api/recommendations/similar/{productId} | auth:sanctum |
| `interests` | GET /api/recommendations/interests | auth:sanctum |
| `trends` | GET /api/trends?type=&limit=&days= | 공개 |
| `keywords` | GET /api/trends/keywords | 공개 |
| `categories` | GET /api/trends/categories | 공개 |
| `trendingProducts` | GET /api/trends/products | 공개 |

라우트는 `routes/api.php`에 반영됨 (recommendations는 auth:sanctum 그룹 내, trends는 공개 그룹).

---

## STEP 7: 스케줄러 (`routes/console.php`)

| 이름 | 주기 | 내용 |
|------|------|------|
| r4:calculate-product-scores | 매시 | `TrendService::calculateProductScores()` |
| r4:generate-trend-snapshot | 매일 03:00 | `TrendService::generateTrendSnapshot()` |
| r4:decay-interests | 매주 | `RecommendationService::decayAllInterests()` |

---

## 검증

- PHP 문법 검사 통과 (RecommendationService, TrendService, RecommendationController, UserInterest)
- 린트 에러 없음
- 마이그레이션 파일 3개 생성 완료 (실서버 적용 시 `php artisan migrate` 실행)

---

## 커밋 메시지 (권장)

```
[R4-API-003] AI 맞춤 피드 + 추천 엔진 — user_interests/product_scores/trend_snapshots, RecommendationService, TrendService, 7 EP (v3.3.0)
```

---

**R4-API-003 완료**  
테이블 3개, 모델 3개, 서비스 2개, 엔드포인트 7개, FeedController 개편(70/30 혼합), 스케줄러 3개.
