# 코드 검수 요청서
> 작성일: 2026-02-23
> 작업ID: R2-FRONT-003 + R2-API-002 + R2-FRONT-004

## 검수 대상 파일
| 파일 | 검수 포인트 |
|------|------------|
| R2-API-002_BrandPageController.php | slug 조회, 팔로우 토글, N+1, 권한 |
| R2-FRONT-004_brand-api.ts | API 연동, 에러 처리 |
| R2-FRONT-003_product-api.ts | 상품 API, wishlist toggle |

## 민감정보 확인
- [x] 비밀번호 제거
- [x] API 키/토큰 제거
- [x] .env 하드코딩 없음
