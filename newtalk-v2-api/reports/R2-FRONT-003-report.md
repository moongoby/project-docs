# R2-FRONT-003 보고서 — 상품 상세·찜·공유 UI

- **작업일**: 2026-02-24
- **브랜치**: feature/R2-FRONT-003-product-detail
- **Git SHA**: (커밋 후 `git log --oneline -1` 결과로 갱신)
- **GitHub**: https://github.com/moongoby/newtalk-v2-api-
- **목표 버전**: v1.5.0

---

## §1. 추가·수정된 파일

### 타입·API
| 구분 | 경로 |
|------|------|
| 신규 | frontend/src/types/product.ts |
| 신규 | frontend/src/lib/product-api.ts |

### 컴포넌트
| 구분 | 경로 |
|------|------|
| 신규 | frontend/src/components/product/product-image-carousel.tsx |
| 신규 | frontend/src/components/product/product-info.tsx |
| 신규 | frontend/src/components/product/product-options.tsx |
| 신규 | frontend/src/components/product/product-action-bar.tsx |
| 신규 | frontend/src/components/product/related-products.tsx |

### 페이지·라우트
| 구분 | 경로 |
|------|------|
| 신규 | frontend/src/app/retail/layout.tsx |
| 신규 | frontend/src/app/retail/product/[id]/page.tsx |

### 기타
| 구분 | 경로 |
|------|------|
| 수정 | frontend/src/app/globals.css (scrollbar-hide 유틸 추가) |

### 문서
| 구분 | 경로 |
|------|------|
| 신규 | docs/reports/R2-FRONT-003-report.md |

---

## §2. 구현 요약

- **ProductImageCarousel**: 이미지 슬라이드, 스와이프·인디케이터 도트, 이미지 없을 때 placeholder.
- **ProductInfo**: 상품명, 도매가·소매가, 브랜드 아바타·이름, 찜(하트 토글·카운트), 공유(navigator.share / 클립보드).
- **ProductOptions**: 컬러·사이즈 버튼 그룹, 재고 0 시 disabled·품절 표시, 선택 시 가격 차이 반영.
- **ProductActionBar**: 하단 고정 바, 수량 stepper(±), 찜 아이콘, "사입하기" primary 버튼.
- **RelatedProducts**: 수평 스크롤 카드, 클릭 시 `/retail/product/{id}`.
- **상품 상세 페이지**: 캐러셀 → Info → Options → 설명(접기/펼치기) → 관련상품 → ActionBar, 404·로딩·스켈레톤 처리.

---

## §3. 테스트 결과

(서버에서 아래 명령 실행 후 기재)

- **빌드**: `docker compose --env-file .env.docker up -d --build frontend` → 에러 없음
- **로그**: `docker compose --env-file .env.docker logs frontend --tail 30` → 정상
- **접속**: `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86:3000/retail/product/1` → 200 또는 307
- **V1 헬스**: `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` → 200

---

## §4. 비고

- feed-card.tsx는 이미 "사입하기" 링크가 `/retail/product/{id}`로 연결되어 있어 수정 없음(STEP 6 skip).
- 상품 API는 Mock 사용(USE_MOCK). 실 API 연동 시 product-api.ts에서 USE_MOCK = false로 변경.
- UI 라이브러리: 캐러셀은 커스텀 구현(snap scroll + 터치). shadcn carousel 추가 시 교체 가능.
