# R2-FIX-002 검수 피드백 반영 보고서

**작업일**: 2026-02-24  
**브랜치**: feature/R2-FIX-002-review-feedback  
**Git SHA**: (서버 푸시 후 기록)  
**버전**: v1.6.1  

---

## 수정 내역

### BrandPageController.php (HIGH 2, MEDIUM 3, LOW 1)
- updateMine() — Rule import 불필요(블록 제거로 미사용), slug 재생성 블록 전체 삭제
- updateMine() — array_filter 키 기반 필터: nullableFields `['description','business_info','sns_links']`, ARRAY_FILTER_USE_BOTH
- toggleFollow() — follower_count 음수 방지: `BrandPage::where('id',$brand->id)->where('follower_count','>',0)->decrement('follower_count')`
- products() — 파라미터 `category` → `keyword`, `name` like 검색
- products() — 가격 필터 `COALESCE(retail_price, wholesale_price)` 기준 min/max
- show() — `withCount([])` 제거

### product-api.ts (MEDIUM 1, LOW 1)
- USE_MOCK → `process.env.NEXT_PUBLIC_USE_MOCK === 'true'`
- shareProduct — clipboard fallback에 try/catch 추가

### brand-api.ts (MEDIUM 3)
- getBrands(q?, page?) — 시그니처 cursor→page, `params.set("page", String(page ?? 1))`
- getBrand() — `fetchApi<{ data: BrandPage }>` 후 `return body.data`
- getBrandFeed() — 응답을 BrandFeedPayload로 한 번만 추출 후 반환

### 호출부
- brands/page.tsx, explore/page.tsx — getBrands 두 번째 인자 cursor 문자열 → page 숫자로 변환하여 전달

### cursorrules
- 섹션 16 "project-docs 보고서 push 필수 마감" 추가 (보고서 존재 확인, 문서 복사, 민감정보 검사, push, 원격 검증, {SHA} 금지)

### SHA 교체 (서버 실행 시)
- CONTEXT.md, CHANGELOG.md, 보고서 4건의 {SHA}/(커밋 후 기록)/(서버 푸시 후 기록) 플레이스홀더를 `git log --oneline --all --grep=...` 결과로 교체

---

## API 변경 (문서 갱신)

| 엔드포인트 | 변경 |
|------------|------|
| GET /api/brands/{slug}/products | 쿼리 파라미터 `category` → `keyword` (상품명 검색) |

---

## 동기화 체크 (서버·project-docs 실행 후)

- CONTEXT {SHA} 0건
- CHANGELOG {SHA} 0건
- cursorrules 섹션 16 존재
- R2-FIX-002 보고서 푸시
- review 비움(해당 시)
- V1 헬스 200
