# R2-FRONT-004 보고서: 브랜드 페이지 UI

**문서번호**: R2-FRONT-004  
**작성일**: 2026-02-24  
**브랜치**: feature/R2-API-002-brand-page  
**목표 버전**: v1.6.0

---

## §1. 생성·수정된 파일 목록

### 타입·API
| 구분 | 경로 |
|------|------|
| 신규 | frontend/src/types/brand.ts (BrandPage, BrandListItem, BrandProductListItem, 응답 타입) |
| 신규 | frontend/src/lib/brand-api.ts (getBrands, getBrand, getBrandProducts, getBrandFeed, toggleBrandFollow) |

### 컴포넌트
| 구분 | 경로 |
|------|------|
| 신규 | frontend/src/components/brand/brand-header.tsx (커버·로고·설명·팔로우·SNS) |
| 신규 | frontend/src/components/brand/brand-card.tsx (목록용 카드, /brand/{slug}) |
| 신규 | frontend/src/components/brand/brand-product-grid.tsx (2/3열 그리드, 무한 스크롤) |
| 신규 | frontend/src/components/brand/brand-feed-section.tsx (FeedCard 재활용, 무한 스크롤) |

### 페이지
| 구분 | 경로 |
|------|------|
| 신규 | frontend/src/app/(retail)/brand/[slug]/page.tsx (상세: 헤더 + 탭 상품/피드) |
| 신규 | frontend/src/app/(retail)/brands/page.tsx (브랜드 탐색, 검색, 그리드) |

### 수정
| 구분 | 경로 |
|------|------|
| 수정 | frontend/src/app/(retail)/explore/page.tsx (탭 "브랜드" 추가, BrandCard 그리드) |
| 수정 | frontend/src/components/feed/feed-card.tsx (작성자 이름 → /brand/{slug} 링크, author.brand_slug) |
| 수정 | frontend/src/types/feed.ts (FeedAuthor.brand_slug) |
| 수정 | frontend/src/types/product.ts (author.brand_slug) |
| 수정 | frontend/src/components/product/product-info.tsx (브랜드명 → /brand/{slug} 링크) |

---

## §2. URL

- `/brand/{slug}` — 브랜드 상세 (헤더, 탭: 상품 | 피드)
- `/brands` — 브랜드 탐색 (검색, BrandCard 그리드, 무한 스크롤)
- 탐색 페이지 탭 "브랜드" 선택 시 동일 그리드 표시

---

## §3. 네비게이션 연결

- 피드 카드 작성자 이름 클릭 → `/brand/{slug}` (author.brand_slug 있을 때)
- 상품 상세 브랜드(작성자) 클릭 → `/brand/{slug}` (author.brand_slug 있을 때)
- 탐색 페이지 "브랜드" 탭 → 브랜드 목록 그리드

---

## §4. HTTP 테스트 (프론트)

```bash
curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86:3000/brand/test-wholesale
# 기대: 200

curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86:3000/brands
# 기대: 200
```

---

## §5. Git SHA

- (서버 푸시 후 기록)  
- 브랜치: feature/R2-API-002-brand-page
