# R2-FIX-001 검수 피드백 반영 — 실행 보고서

**작업 ID**: R2-FIX-001  
**버전**: v1.4.1  
**기준일**: 2026-02-23  
**목적**: 검수 피드백 반영 — store 역할 체크, SQL 바인딩, wishlist toggle, 찜 UI, feed_likes unique

---

## 1. 수정 파일 목록

### 백엔드 (Laravel)
- `app/Http/Controllers/Api/FeedController.php` — store() 역할 체크(wholesale|admin), index() orderByRaw 바인딩
- `app/Http/Controllers/Api/WishlistController.php` — toggle() 엔드포인트 추가
- `routes/api.php` — POST /feed role:wholesale|admin, POST /wishlists/{productId}/toggle
- `database/migrations/*_feed_likes_table.php` — unique(user_id, feed_item_id) 확인/추가

### 프론트엔드 (Next.js)
- `frontend/src/components/feed/feed-card.tsx` — 찜 상태 UI(Bookmark fill), 팔로우 disabled, placeholder
- `frontend/src/lib/api/feed-api.ts` — toggleWishlist → /wishlists/{id}/toggle, 타입 캐스팅 개선
- `frontend/public/images/placeholder-feed.svg` — placeholder 이미지 (없을 경우)

---

## 2. 변경 내용 요약

| 구분 | 내용 |
|------|------|
| FeedController::store() | wholesale 또는 admin 역할만 피드 작성 허용, 미인증 역할 403 |
| FeedController::index() | orderByRaw SQL 바인딩 파라미터 적용 (SQL injection 방지) |
| WishlistController | toggle() — POST /api/wishlists/{id}/toggle 찜 토글 |
| feed_likes | unique(user_id, feed_item_id) 인덱스 확인/추가 |
| feed-card.tsx | isWishlisted 반영(Bookmark 아이콘 색상), 팔로우 버튼 disabled, 미디어 placeholder |
| feed-api.ts | toggleWishlist → toggle 엔드포인트 호출, as unknown → 제네릭 타입 개선 |

---

## 3. 테스트 결과

- Feed 작성: wholesale/admin 계정으로만 POST /feed 성공, 소매 계정 403 확인
- 피드 목록: orderByRaw 바인딩 적용 후 정상 조회
- 찜 토글: POST /api/wishlists/{productId}/toggle 정상 동작
- feed_likes: 동일 사용자 중복 좋아요 방지(unique) 확인
- 프론트: 찜 아이콘 상태 반영, 팔로우 비활성화 표시

---

## 4. Git SHA

- DOCS 커밋: 89fde04
- 소스 브랜치: feature/R2-FIX-001-review-feedback
