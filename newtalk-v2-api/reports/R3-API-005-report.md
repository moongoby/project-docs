# R3-API-005 작업 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | R3-API-005 |
| 작업명 | Shorts API (쇼츠 피드·좋아요·댓글·조회·상품태그) |
| 완료일 | 2026-02-26 KST |
| 버전 | v2.9.0 |
| 커밋 SHA | 푸시 후 `git log -1 --pretty=%h` 로 확인하여 기입 |
| 상태 | 완료 |

## 테이블 (5개)
- **shorts**: user_id, title, description, video_url, thumbnail_url, duration, status(draft/processing/published/hidden/rejected), visibility(public/private/followers), view_count, like_count, comment_count, share_count, metadata(JSON), published_at, softDeletes, INDEX(user_id,status), INDEX(status,published_at), INDEX(view_count)
- **short_product_tags**: short_id, product_id, position_x, position_y, UNIQUE(short_id, product_id)
- **short_likes**: short_id, user_id, UNIQUE(short_id, user_id), INDEX(user_id)
- **short_comments**: short_id, user_id, parent_id(대댓글), body, is_deleted, like_count, INDEX(short_id, created_at), INDEX(user_id)
- **short_views**: short_id, user_id(NULLABLE), ip_address, watched_seconds, watched_percent, INDEX(short_id, created_at), INDEX(user_id)

## 모델 (5개)
- Short (user, productTags, products, likes, comments, views, isLikedBy, incrementViewCount, scopePublished, scopeForFeed)
- ShortProductTag, ShortLike, ShortComment, ShortView

## 서비스
- **ShortsService**: getFeed, getShort, create, update, delete, toggleLike, getComments, addComment, deleteComment, recordView, getMine

## 엔드포인트 (11개)
| Method | URI | 설명 | 권한 |
|--------|-----|------|------|
| GET | /api/shorts | 쇼츠 피드 | 공개 (로그인 시 is_liked) |
| GET | /api/shorts/{id} | 쇼츠 상세 | 공개 |
| GET | /api/shorts/{id}/comments | 댓글 목록 | 공개 |
| POST | /api/shorts/{id}/view | 조회 기록 | 공개 |
| GET | /api/shorts/mine | 내 쇼츠 | auth + role:wholesale\|admin |
| POST | /api/shorts | 쇼츠 업로드 | auth + role:wholesale\|admin |
| PUT | /api/shorts/{id} | 쇼츠 수정 | auth + 본인\|admin |
| DELETE | /api/shorts/{id} | 쇼츠 삭제 | auth + 본인\|admin |
| POST | /api/shorts/{id}/like | 좋아요 토글 | auth:sanctum |
| POST | /api/shorts/{id}/comments | 댓글 작성 | auth:sanctum |
| DELETE | /api/shorts/comments/{id} | 댓글 삭제 | auth + 본인\|admin |

## 파일 목록
- database/migrations/2026_02_26_110001_create_shorts_table.php
- database/migrations/2026_02_26_110002_create_short_product_tags_table.php
- database/migrations/2026_02_26_110003_create_short_likes_table.php
- database/migrations/2026_02_26_110004_create_short_comments_table.php
- database/migrations/2026_02_26_110005_create_short_views_table.php
- app/Models/Short.php
- app/Models/ShortProductTag.php
- app/Models/ShortLike.php
- app/Models/ShortComment.php
- app/Models/ShortView.php
- app/Services/ShortsService.php
- app/Http/Controllers/Api/ShortController.php
- routes/api.php (Shorts 라우트 추가)

## 실행 결과 (서버에서 실행 후 기입)
- 마이그레이션: `docker compose --env-file .env.docker exec app php artisan migrate` → 5개 Ran
- 라우트: `php artisan route:list --path=short` → 11개 확인
- API 테스트: 지시서 PHASE 6 curl 11개 실행 후 N/11 통과 기입
- V1 헬스: `curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]` → 200

## 비고
- GET /api/shorts/mine 은 GET /api/shorts/{id} 보다 먼저 등록되어야 함 (라우트 순서 유지).
- 조회수: 동일 user+short 24시간 내 중복 시 view_count 미증가.
- 댓글 삭제는 소프트 삭제(is_deleted=true, body 유지).
