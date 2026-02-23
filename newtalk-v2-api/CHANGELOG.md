# 뉴톡 V2 변경 이력 (CHANGELOG)

모든 주요 변경 사항을 기록합니다. [Semantic Versioning](https://semver.org/) 준수.

---

## [Unreleased]

## [1.6.0] - 2026-02-24
### Added
- R2-API-002: 브랜드 페이지 API ({SHA})
  - brand_pages 테이블, BrandPage 모델, ProductImage 모델
  - BrandPageController 6 엔드포인트 (목록, 상세, 상품, 피드, 팔로우, 수정)
  - BrandPageSeeder (wholesale@newtalk.kr 테스트 브랜드)
  - Feed API: author.brand_slug, product.wholesale_name (BrandPage/User 관계)
- R2-FRONT-004: 브랜드 페이지 UI ({SHA})
  - 브랜드 상세 /brand/[slug] (커버, 로고, 팔로우, 상품 탭, 피드 탭)
  - 브랜드 탐색 /brands (검색, 그리드, 무한 스크롤)
  - 탐색 페이지 "브랜드" 탭, FeedCard/ProductInfo 작성자·브랜드 → /brand/{slug} 링크
  - brand-api.ts, types/brand.ts

## [1.5.0] - 2026-02-24
### Added (R2-FRONT-003)
- 상품 상세 페이지: `/retail/product/[id]` (app/retail/product/[id]/page.tsx)
- ProductImageCarousel: 이미지 슬라이드, 스와이프, 인디케이터 도트, placeholder
- ProductInfo: 상품명, 도매가·소매가, 브랜드, 찜 토글, 공유(navigator.share / 클립보드)
- ProductOptions: 컬러·사이즈 선택, 재고 0 품절 표시, 가격 차이 반영
- ProductActionBar: 하단 고정 바, 수량 stepper, 찜, 사입하기 버튼
- RelatedProducts: 수평 스크롤 관련상품 카드, `/retail/product/{id}` 링크
- product-api.ts: getProduct, getRelatedProducts, toggleProductWishlist, shareProduct (Mock 지원)
- types/product.ts: ProductDetail, ProductListItem, ProductImage, ProductOption
- retail 레이아웃: app/retail/layout.tsx (RetailLayout)
- globals.css: scrollbar-hide 유틸

## [1.4.1] - 2026-02-24
### Fixed (R2-FIX-001 검수 피드백)
- FeedController::store() — wholesale/admin 역할 체크 추가, 미인증 역할 403
- FeedController::index() — orderByRaw 바인딩 파라미터 사용 (SQL injection 방어)
- index() DocBlock — 팔로잉 70/30 혼합 TODO 주석 추가
- routes/api.php — POST /feed에 role:wholesale|admin 미들웨어, POST /wishlists/{productId}/toggle 추가
- WishlistController::toggle() — 찜 토글 엔드포인트 추가
- feed-api.ts — toggleWishlist를 /wishlists/{id}/toggle 호출로 변경
- feed-card.tsx — 찜 상태 UI(isWishlisted, Bookmark fill), 팔로우 버튼 disabled, 미디어 placeholder
- feed_likes 테이블 — unique(user_id, feed_item_id) 기존 마이그레이션에 존재 확인
- placeholder — public/images/placeholder-feed.svg 추가

## [1.4.0] - 2026-02-23
### Added
- R2-FRONT-002: 홈 피드 UI (푸시 후 SHA 기록)
- FeedCard 컴포넌트 (미디어, 좋아요, 찜, 상품 링크)
- 무한 스크롤 (IntersectionObserver, cursor 페이지네이션)
- 탐색 페이지 (그리드, 탭 필터, 검색바)
- Mock API 레이어 (실 API 전환 대비)
- shadcn/ui 컴포넌트 추가 (card, avatar, badge, tabs, scroll-area, skeleton, separator, button)
- 피드 타입 정의 (feed.ts)
- 유틸리티 (formatRelativeTime, formatPrice)
- useInfiniteScroll 훅
- ExploreCard 컴포넌트

## [1.3.0] - 2026-02-23
### Added
- R2-API-001: SNS 소셜 엔진 API ({SHA})
- follows 테이블 + Follow 모델 + 팔로우/언팔로우/팔로워·팔로잉 목록 API
- wishlists 테이블 + Wishlist 모델 + 찜 추가/해제/목록 API
- feed_items 테이블 + FeedItem 모델 + 홈 피드/탐색/상세/작성/검색 API
- feed_likes 테이블 + FeedLike 모델 + 좋아요 토글 API
- Cursor 기반 페이지네이션 (피드, 팔로우, 찜)

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
