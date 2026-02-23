# R2-API-001 보고서 — SNS 소셜 엔진 API

- **작업일**: 2026-02-23
- **브랜치**: feature/R2-API-001-social-engine
- **Git SHA**: c40fabaad19c709ae26c3e7993c9740619b15e03
- **GitHub**: https://github.com/moongoby/newtalk-v2-api-

## 요약
피드·팔로우·찜·검색 API (4테이블, 4모델, 3컨트롤러, 13엔드포인트)

## 추가/수정 파일
- src/database/migrations/2026_02_23_100040_create_follows_table.php
- src/database/migrations/2026_02_23_100041_create_wishlists_table.php
- src/database/migrations/2026_02_23_100042_create_feed_items_table.php
- src/database/migrations/2026_02_23_100043_create_feed_likes_table.php
- src/app/Models/Follow.php, Wishlist.php, FeedItem.php, FeedLike.php
- src/app/Models/User.php (관계 추가)
- src/app/Http/Controllers/Api/FeedController.php, FollowController.php, WishlistController.php
- src/routes/api.php (feed/explore 비인증, feed·follows·wishlists 인증 라우트)

## API 테스트 HTTP 코드
- 피드작성: 201, 홈피드: 200, 탐색: 200, 좋아요: 200, 팔로우: 200/409, 찜목록: 200, 검색: 200, V1: 200
