# R2-API-001 보고서: SNS 소셜 엔진 API

**문서번호**: R2-API-001  
**작성일**: 2026-02-23  
**브랜치**: feature/R2-API-001-social-engine  
**참조**: NT-V2-PLAN-002-FINAL, NT-V2-ARCHITECTURE

---

## §1. 생성·수정된 파일 목록

### 마이그레이션 (database/migrations/)
| 구분 | 경로 |
|------|------|
| 신규 | 2026_02_23_120001_create_follows_table.php |
| 신규 | 2026_02_23_120002_create_wishlists_table.php |
| 신규 | 2026_02_23_120003_create_feed_items_table.php |
| 신규 | 2026_02_23_120004_create_feed_likes_table.php |

### 모델 (app/Models/)
| 구분 | 경로 |
|------|------|
| 신규 | Follow.php |
| 신규 | Wishlist.php |
| 신규 | FeedItem.php |
| 신규 | FeedLike.php |
| 신규 | User.php (워크스페이스에 없어 신규 작성; 서버에 기존 파일 있으면 관계만 병합) |

### 컨트롤러 (app/Http/Controllers/Api/)
| 구분 | 경로 |
|------|------|
| 신규 | FeedController.php |
| 신규 | FollowController.php |
| 신규 | WishlistController.php |

### 라우트
| 구분 | 경로 |
|------|------|
| 수정 | routes/api.php (R2-API-001 피드·팔로우·찜 라우트 추가) |

---

## §2. 마이그레이션 결과

서버에서 아래 실행 후 기록.

```bash
cd /srv/newtalk-v2
docker compose --env-file .env.docker exec app php artisan migrate --force
```

| 테이블 | 상태 |
|--------|------|
| follows | (서버 실행 후 기록) |
| wishlists | (서버 실행 후 기록) |
| feed_items | (서버 실행 후 기록) |
| feed_likes | (서버 실행 후 기록) |

확인:
```bash
mysql -u newtalk_v2_user -p -h 127.0.0.1 -P 3307 newtalk_v2 \
  -e "SHOW TABLES LIKE 'follows'; SHOW TABLES LIKE 'wishlists'; SHOW TABLES LIKE 'feed_items'; SHOW TABLES LIKE 'feed_likes';"
```

---

## §3. API 테스트 결과 (HTTP 상태코드)

서버에서 STEP 5 테스트 실행 후 아래 표에 기록.

| # | 엔드포인트 | 방법 | 예상 | 실제 |
|---|------------|------|------|------|
| 1 | /api/auth/login | POST | 200 | |
| 2 | /api/feed (피드 작성, admin) | POST | 201 | |
| 3 | /api/feed (홈 피드) | GET | 200 | |
| 4 | /api/feed/explore (비인증) | GET | 200 | |
| 5 | /api/feed/{id}/like (토글) | POST | 200 | |
| 6 | /api/follows/{userId} (팔로우) | POST | 200 | |
| 7 | /api/wishlists/{productId} (찜 추가) | POST | 201 | |
| 8 | /api/wishlists (찜 목록) | GET | 200 | |
| 9 | /api/feed/search?q=테스트 | GET | 200 | |
| 10 | V1 보호 (http://[SERVER-IP]) | GET | 200 | |

---

## §4. Git / 푸시 결과

| 항목 | 값 |
|------|-----|
| 브랜치 | feature/R2-API-001-social-engine |
| 커밋 SHA (소스) | (서버 푸시 후 기록) |
| 커밋 SHA (문서) | (문서 커밋 후 기록) |
| 원격 푸시 | (성공/실패 기록) |

---

## §5. 엔드포인트 요약

| 도메인 | 메서드 | 경로 | 설명 |
|--------|--------|------|------|
| Feed | GET | /api/feed | 홈 피드 (70% 팔로우 + 30% 인기), cursor |
| Feed | GET | /api/feed/explore | 탐색 (비인증 허용) |
| Feed | GET | /api/feed/search?q= | 피드 검색 |
| Feed | GET | /api/feed/{id} | 피드 상세, view_count +1 |
| Feed | POST | /api/feed | 피드 작성 (wholesale/admin) |
| Feed | POST | /api/feed/{id}/like | 좋아요 토글 |
| Follow | POST | /api/follows/{userId} | 팔로우 |
| Follow | DELETE | /api/follows/{userId} | 언팔로우 |
| Follow | GET | /api/follows/{userId}/followers | 팔로워 목록 |
| Follow | GET | /api/follows/{userId}/following | 팔로잉 목록 |
| Wishlist | GET | /api/wishlists | 내 찜 목록 |
| Wishlist | POST | /api/wishlists/{productId} | 찜 추가 |
| Wishlist | DELETE | /api/wishlists/{productId} | 찜 해제 |

---

## §6. 서버 실행 체크리스트 (STEP 5~9)

다음은 **서버([SERVER-IP])** 에서 실행할 항목입니다.

1. **브랜치 생성**
   - `git checkout develop && git pull origin develop`
   - `git checkout -b feature/R2-API-001-social-engine`
   - (또는 로컬에서 푸시한 브랜치 pull)

2. **마이그레이션**
   - `docker compose --env-file .env.docker exec app php artisan migrate --force`
   - 테이블 4개 확인

3. **User.php**
   - 서버에 `app/Models/User.php` 가 이미 있으면, 이번에 추가한 관계만 병합: `followers()`, `followings()`, `wishlists()`, `feedItems()`, `feedLikes()`.

4. **API 테스트**
   - STEP 5의 (2)~(10) curl 실행 후 §3 표에 HTTP 코드 기록.

5. **Git 커밋·푸시**
   - 민감정보 검사 후 `[R2-API-001] SNS 소셜 엔진 API — 피드, 팔로우, 찜, 검색` 커밋 및 푸시.

6. **보고서·문서**
   - 본 보고서 §2, §3, §4 실제 값으로 갱신.
   - docs/CONTEXT.md, CHANGELOG.md, HANDOVER.md 갱신 후 문서 커밋·푸시.

7. **project-docs 동기화**
   - `bash /data/project-docs/scripts/sync_newtalk_v2_api.sh` 또는 수동 복사 후 project-docs 커밋·푸시.

8. **검수 업로드**
   - FeedController, FollowController, WishlistController를 project-docs/newtalk-v2-api/review/ 에 복사, REVIEW_REQUEST.md 작성 후 푸시.
