# R4-FRONT-003 AI 추천 피드 UI + 소매 마이페이지 — 완료 보고서

**작업 ID**: R4-FRONT-003  
**버전**: v3.8.0  
**완료 시각**: 2026-02-26 KST  
**선행**: R4-API-003 (v3.3.0) — 프론트 구현 완료, API 연동 준비

---

## 1. 요약

1. 홈 피드 개편: 팔로잉 + AI 추천 혼합(피드 중간 추천 상품 섹션, AI 추천 아이템 배지)  
2. 추천 상품 섹션: 피드·탐색·상품 상세 삽입  
3. 트렌드 페이지: 인기 검색어, 인기 카테고리, 인기 상품  
4. 소매 마이페이지: 프로필, 주문/찜/팔로우/쿠폰 통계, 관심사, 최근 본 상품

---

## 2. 구현 목록

### 2.1 타입 (frontend/src/types/recommendation.ts)
- RecommendedProduct, TrendItem, UserInterest, TrendKeyword, TrendCategory

### 2.2 API 클라이언트 (frontend/src/lib/recommendation-api.ts) — 7함수
- getRecommendedProducts, getSimilarProducts, getMyInterests  
- getTrends, getTrendKeywords, getTrendCategories, getTrendingProducts

### 2.3 컴포넌트 12개
| 구분 | 컴포넌트 | 역할 |
|------|----------|------|
| recommendation/ | RecommendedProductsSection | 추천 상품 가로 스크롤 (피드 중간 삽입) |
| | SimilarProductsSection | 유사 상품 (상품 상세 하단) |
| | TrendingKeywords | 인기 검색어 (탐색 상단) |
| | TrendingCategories | 인기 카테고리 카드 그리드 |
| | TrendingProducts | 인기 상품 랭킹 리스트 |
| | AIFeedBadge | AI 추천 피드 아이템 "추천" 배지 |
| | InterestTags | 내 관심사 태그 (마이페이지) |
| mypage/ | RetailMyPage | 소매 마이페이지 통합 |
| | ProfileCard | 프로필 카드 (아바타, 이름, 이메일, 역할) |
| | StatsGrid | 통계 그리드 (주문/찜/팔로우/쿠폰) |
| | RecentViewedProducts | 최근 본 상품 (로컬 스토리지) |

### 2.4 페이지·라우트 3개 + 기존 수정
- /retail/mypage — 소매 마이페이지 (RetailMyPage)
- /retail/trends — 트렌드 (인기 검색어, 카테고리, 상품)
- /retail/explore — 탐색 개편 (TrendingKeywords 상단, 트렌드 탭 → /retail/trends)
- /retail/feed — AIFeedBadge, RecommendedProductsSection (4건마다 삽입)
- /retail/product/[id] — SimilarProductsSection 하단, addRecentProduct 연동
- retail-layout — "트렌드" 메뉴 → /retail/trends

### 2.5 FeedItem 확장
- is_recommended?: boolean (API에서 70/30 혼합 시 추천 아이템 표시용)

---

## 3. 파일 목록 (신규·수정)

**신규**  
- frontend/src/types/recommendation.ts  
- frontend/src/lib/recommendation-api.ts  
- frontend/src/components/recommendation/*.tsx, index.ts  
- frontend/src/components/mypage/*.tsx, index.ts  
- frontend/src/app/(retail)/retail/trends/page.tsx  

**수정**  
- frontend/src/types/feed.ts (is_recommended)  
- frontend/src/components/feed/feed-card.tsx (AIFeedBadge)  
- frontend/src/app/(retail)/retail/feed/page.tsx (RecommendedProductsSection)  
- frontend/src/app/(retail)/explore/page.tsx (TrendingKeywords, 트렌드 탭)  
- frontend/src/app/(retail)/mypage/page.tsx (RetailMyPage)  
- frontend/src/app/retail/product/[id]/page.tsx (SimilarProductsSection, addRecentProduct)  
- frontend/src/components/layout/retail-layout.tsx (트렌드 메뉴)  
- docs/CHANGELOG.md, CONTEXT.md, handover/HANDOVER.md, architecture/NT-V2-ARCHITECTURE.md  

---

## 4. 비고

- 피드 70/30 혼합은 백엔드에서 is_recommended 플래그로 내려주면 FeedCard에서 AIFeedBadge 표시.
- 최근 본 상품은 로컬 스토리지 키 `newtalk_recent_products`, 최대 12건.
