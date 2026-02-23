# 뉴톡 V2 변경 이력 (CHANGELOG)

모든 주요 변경 사항을 기록합니다. [Semantic Versioning](https://semver.org/) 준수.

---

## [Unreleased]

## [1.4.1] - 2026-02-23
### Fixed
- FeedController store() 역할 체크 추가 (wholesale|admin만 피드 작성)
- FeedController index() orderByRaw SQL 바인딩 파라미터 적용
- feed_likes 테이블 unique(user_id, feed_item_id) 인덱스 추가
- WishlistController toggle 엔드포인트 추가 (POST /api/wishlists/{id}/toggle)
- feed-card.tsx 찜 상태 UI 반영 (Bookmark 아이콘 색상 토글)
- feed-card.tsx 팔로우 버튼 disabled 처리
- feed-api.ts toggleWishlist → toggle 엔드포인트로 변경
- feed-api.ts 타입 캐스팅 개선 (as unknown → 제네릭)

## [1.4.0] - 2026-02-23
### Added
- R2-FRONT-002: 홈 피드 + 탐색 UI (ed3177b)
- 피드카드, 무한스크롤, 탐색 그리드, feed-api 연동 (USE_MOCK=false)
- shadcn card, avatar, tabs, skeleton, button

## [1.3.0] - 2026-02-23
### Added
- R2-API-001: SNS 소셜 엔진 API (c40faba)
- follows, wishlists, feed_items, feed_likes 테이블
- FeedController, FollowController, WishlistController
- GET/POST feed, feed/explore, feed/search, feed/{id}, feed/{id}/like
- POST/DELETE follows/{userId}, GET followers/following
- GET/POST/DELETE wishlists


## [1.2.0] - 2026-02-23
### Added
- R2-FRONT-001-DEPLOY: 프론트엔드 Docker 빌드·실행 (870c007)
- Rate Limiting: 로그인 API throttle:5,1 (1분 5회 제한)
- 역할별 라우트 보호: middleware.ts ROLE_PATHS/ROLE_HOME 매핑
- 401 자동 로그아웃: fetchApi에서 401 감지 → 쿠키·스토어 클리어 → /login 리다이렉트
- Sanctum 토큰 만료: 7일 (config/sanctum.php)
- 방화벽 3000 포트 개방 (ufw)
### Fixed
- Redis 연결: REDIS_PORT=6379 → app 서비스 환경변수 추가
- Tailwind 배경·전경색 수정

## [1.1.0] - 2026-02-23
### Added
- R2-FRONT-001: Next.js 16 프로젝트 셋업 (ce541c5)
- 로그인/회원가입 화면
- 역할별 레이아웃 (소매/도매/관리자/MD/사입자)
- 관리자 대시보드 + 사입 대시보드 (R1 API 연동)
- AuthController (POST login/logout, GET me)
- Docker Compose frontend 서비스 구성

### Documentation
- NT-V2-PLAN-002-FINAL.md: 통합 기획서 v1.0.0
- NT-V2-ARCHITECTURE.md: 시스템 아키텍처 v1.0.0
- HANDOVER.md: 인수인계서 v1.0.0
- docs/ 디렉터리 구조 표준화

## [1.0.0] - 2026-02-22
### R1 완료
- R1-001: Sanctum 인증 + RBAC (37ad7e4)
- R1-002: 상품 CRUD API (876f4b3)
- R1-003: 발주·입고·바코드 API (555ee03)
- R1-004: 사입 대시보드 API (67f0a64)
- R1-005: 기본 대시보드 + V1 마이그레이션 (be662c7)

## [0.1.0] - 2026-02-21
### R0 완료
- Laravel 12 + Docker 환경 구축
- V1 스키마 추출 (226 테이블)
- 38 테이블 마이그레이션
- Spatie RBAC 시더 (6 roles, 36 permissions)
- GitHub 레포 생성, .cursorrules 작성
