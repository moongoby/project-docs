# 코드 검수 요청서
> 작성일: 2026-02-23
> 작업ID: R2-API-001 + R2-FRONT-002

## 검수 대상 파일
| 파일 | 검수 포인트 |
|------|------------|
| R2-API-001_FeedController.php | 피드 혼합 70/30, cursor, 좋아요 race condition, N+1 |
| R2-API-001_FollowController.php | 자기 팔로우 방지, 중복, 페이지네이션 |
| R2-API-001_WishlistController.php | 중복 찜, eager loading |
| R2-FRONT-002_feed-card.tsx | 모바일 퍼스트, optimistic update |
| R2-FRONT-002_feed-api.ts | API 연동, 에러 처리 |

## 민감정보 확인
- [x] 비밀번호 제거
- [x] API 키/토큰 제거
- [x] .env 하드코딩 없음
