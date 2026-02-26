# R4-API-006 SNS 자동 게시 API — 완료 보고서

**작성일시**: 2026-02-26 KST  
**버전**: v3.9.0  
**커밋 접두사**: `[R4-API-006]`

---

## 요약

| 항목 | 내용 |
|------|------|
| 테이블 | 3개 (`sns_connections`, `sns_posts`, `sns_post_analytics`) |
| 모델 | 3개 (`SnsConnection`, `SnsPost`, `SnsPostAnalytics`) |
| 서비스 | `SnsPostService` (14 메서드) + `SnsDriverInterface` |
| 드라이버 | Instagram, Tiktok, Facebook, Youtube (모두 스텁) |
| 엔드포인트 | 12개 |
| 스케줄러 | 2개 (예약 게시 매분, 성과 수집 매일) |

---

## STEP 1: 마이그레이션

- `database/migrations/2026_02_26_340001_create_sns_connections_table.php`
  - **sns_connections**: user_id, platform(instagram/tiktok/facebook/youtube), platform_user_id, platform_username, access_token, refresh_token, token_expires_at, scopes, is_active, status, last_error  
  - unique(user_id, platform, platform_user_id)

- `database/migrations/2026_02_26_340002_create_sns_posts_table.php`
  - **sns_posts**: user_id, sns_connection_id, content_id(nullable), platform, platform_post_id, post_type(image/video/reel/story/shorts), caption, media_urls(json), hashtags(json), status(draft/scheduled/posting/posted/failed/deleted), scheduled_at, posted_at, error_message, engagement(json)  
  - index(user_id, status), index(scheduled_at, status), index(sns_connection_id)

- `database/migrations/2026_02_26_340003_create_sns_post_analytics_table.php`
  - **sns_post_analytics**: sns_post_id, snapshot_date, views, likes, comments, shares, saves, reach, impressions, engagement_rate  
  - unique(sns_post_id, snapshot_date)

---

## STEP 2: 모델

- **SnsConnection**  
  관계: `user`, `snsPosts`  
  fillable, casts, hidden(access_token, refresh_token)  
  scopes: `byUser`, `active`, `byPlatform`  
  상수: PLATFORM_*, STATUS_*

- **SnsPost**  
  관계: `user`, `snsConnection`, `content`, `analytics`  
  fillable, casts  
  scopes: `byUser`, `byStatus`, `scheduledDue`  
  상수: POST_TYPE_*, STATUS_*

- **SnsPostAnalytics**  
  관계: `snsPost`  
  fillable, casts (timestamps 없음)

---

## STEP 3: 서비스 레이어

### SnsDriverInterface

- `publish(connection, post): array` — 게시 → platform_post_id 반환
- `delete(connection, platformPostId): bool`
- `getAnalytics(connection, platformPostId): array`
- `refreshToken(connection): SnsConnection`

### 드라이버 (모두 스텁)

| 드라이버 | 파일 |
|---------|------|
| Instagram | `App\Services\Sns\InstagramDriver` |
| Tiktok | `App\Services\Sns\TiktokDriver` |
| Facebook | `App\Services\Sns\FacebookDriver` |
| Youtube | `App\Services\Sns\YoutubeDriver` |

### SnsPostService (14 메서드)

1. `connect(userId, platform, authData)` — SNS 연결
2. `disconnect(connectionId)` — 연결 해제
3. `getConnections(userId)` — 내 SNS 목록
4. `createPost(userId, data)` — 게시물 생성 (즉시 또는 예약)
5. `schedulePost(postId, scheduledAt)` — 예약 시간 설정
6. `publishPost(post)` — 실제 게시 (플랫폼 API 호출 → 스텁)
7. `deletePost(postId)` — 삭제
8. `getMyPosts(userId, filters)` — 내 게시 이력
9. `getPostAnalytics(postId)` — 성과 조회
10. `processScheduledPosts()` — 예약 게시 실행 (스케줄러)
11. `fetchAnalytics(post)` — 성과 데이터 수집 (스텁)
12. `bulkPost(userId, connectionIds[], contentData)` — 다채널 일괄 게시
13. `generateHashtags(contentId)` — AI 해시태그 추천 (스텁)
14. `getOptimalPostTime(connectionId)` — 최적 게시 시간 추천 (스텁)

---

## STEP 4: 컨트롤러·라우트

**파일**: `app/Http/Controllers/Api/SnsController.php`

| Method | URI | 메서드 |
|--------|-----|--------|
| POST | /api/sns/connect | connect |
| DELETE | /api/sns/{id} | disconnect |
| GET | /api/sns/connections | connections |
| POST | /api/sns/posts | storePost |
| GET | /api/sns/posts | indexPosts |
| GET | /api/sns/posts/{id} | showPost |
| PUT | /api/sns/posts/{id}/schedule | schedulePost |
| DELETE | /api/sns/posts/{id} | destroyPost |
| POST | /api/sns/posts/bulk | bulkPost |
| GET | /api/sns/posts/{id}/analytics | postAnalytics |
| POST | /api/sns/posts/{id}/hashtags | generateHashtags |
| GET | /api/sns/optimal-time/{connectionId} | optimalTime |

미들웨어: `auth:sanctum`, `role:wholesale|admin`.

---

## STEP 5: 스케줄러

**파일**: `routes/console.php`

| 커맨드 | 주기 | 설명 |
|--------|------|------|
| `sns:process-scheduled` | everyMinute | 예약 시간이 된 SNS 게시물 게시 |
| `sns:fetch-analytics` | daily | 게시된 게시물 성과 수집 |

크론 미사용 시 수동 실행 예:
- `php artisan sns:process-scheduled`
- `php artisan sns:fetch-analytics`

---

## 검증

- SNS 연결/해제/목록: 본인 `user_id` 기준.
- 게시물 CRUD·예약·일괄·성과·해시태그·최적시간: 해당 사용자 소유만 조회·수정.
- 마이그레이션: `php artisan migrate` 실행.

---

## 신규·변경 파일 목록

- `database/migrations/2026_02_26_340001_create_sns_connections_table.php`
- `database/migrations/2026_02_26_340002_create_sns_posts_table.php`
- `database/migrations/2026_02_26_340003_create_sns_post_analytics_table.php`
- `app/Models/SnsConnection.php`
- `app/Models/SnsPost.php`
- `app/Models/SnsPostAnalytics.php`
- `app/Services/Sns/SnsDriverInterface.php`
- `app/Services/Sns/InstagramDriver.php`
- `app/Services/Sns/TiktokDriver.php`
- `app/Services/Sns/FacebookDriver.php`
- `app/Services/Sns/YoutubeDriver.php`
- `app/Services/SnsPostService.php`
- `app/Http/Controllers/Api/SnsController.php`
- `app/Console/Commands/ProcessScheduledSnsPostsCommand.php`
- `app/Console/Commands/FetchSnsPostAnalyticsCommand.php`
- `routes/api.php` (SNS 라우트 그룹)
- `routes/console.php` (SNS 스케줄 2개)

---

## R4-API-006 완료

- 테이블 3개, 모델 3개  
- 서비스: SnsPostService (14 메서드) + SnsDriverInterface  
- 드라이버: Instagram, Tiktok, Facebook, Youtube (스텁 4개)  
- 엔드포인트 12개  
- 스케줄러 2개 (예약 게시 매분, 성과 수집 매일)
