# R2-FRONT-002 보고서: 소매 홈 피드 + 탐색 UI

**문서번호**: R2-FRONT-002  
**작성일**: 2026-02-23  
**브랜치**: feature/R2-FRONT-002-feed-ui  
**참조**: NT-V2-PLAN-002-FINAL (레이어 1: SNS 소셜 엔진), SN-001(홈 피드), SN-002(탐색)

---

## §1. 생성·수정된 파일 목록

### 프론트엔드 (frontend/)

#### UI 컴포넌트 (shadcn/ui 스타일)
| 구분 | 경로 |
|------|------|
| 신규 | frontend/src/components/ui/card.tsx |
| 신규 | frontend/src/components/ui/avatar.tsx |
| 신규 | frontend/src/components/ui/badge.tsx |
| 신규 | frontend/src/components/ui/tabs.tsx |
| 신규 | frontend/src/components/ui/scroll-area.tsx |
| 신규 | frontend/src/components/ui/skeleton.tsx |
| 신규 | frontend/src/components/ui/separator.tsx |
| 신규 | frontend/src/components/ui/button.tsx |

#### 피드·탐색
| 구분 | 경로 |
|------|------|
| 신규 | frontend/src/types/feed.ts |
| 신규 | frontend/src/lib/mock-feed.ts |
| 신규 | frontend/src/lib/feed-api.ts |
| 신규 | frontend/src/lib/date-utils.ts |
| 신규 | frontend/src/hooks/use-infinite-scroll.ts |
| 신규 | frontend/src/components/feed/feed-card.tsx |
| 신규 | frontend/src/components/feed/feed-card-skeleton.tsx |
| 신규 | frontend/src/components/feed/explore-card.tsx |
| 수정 | frontend/src/app/(retail)/feed/page.tsx |
| 수정 | frontend/src/app/(retail)/explore/page.tsx |
| 수정 | frontend/src/components/layout/retail-layout.tsx |

#### 기타
| 구분 | 경로 |
|------|------|
| 수정 | frontend/package.json (@radix-ui/react-scroll-area 추가) |

---

## §2. 구현 요약

- **홈 피드 (SN-001)**: 상단 헤더(뉴톡·검색·DM), FeedCard 세로 나열, 무한 스크롤(IntersectionObserver + cursor), 로딩 시 FeedCardSkeleton 3개, 빈 상태 문구, 좋아요 optimistic 업데이트.
- **탐색 (SN-002)**: 검색바, 탭(전체|상품|콘텐츠|쇼츠), 2/3/4열 그리드, ExploreCard(썸네일·호버 시 좋아요/댓글 수·브랜드명), 탭 전환 시 type 파라미터로 getExplore(type) 호출, 무한 스크롤.
- **Mock API**: getMockFeed / getMockExplore 20건 규모, USE_MOCK=true. API 완성 후 feed-api.ts에서 USE_MOCK=false로 전환만 하면 됨.

---

## §3. 빌드·접속 테스트

| 항목 | 예상/명령 | 비고 |
|------|-----------|------|
| 프론트 빌드 | `docker compose --env-file .env.docker up -d --build frontend` | 서버 /srv/newtalk-v2 에서 실행 |
| 빌드 성공 확인 | `docker compose --env-file .env.docker logs frontend --tail 20` | "Ready" 또는 "started server" 메시지 |
| /feed 접속 | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/retail/feed` | 200 기대 |
| /explore 접속 | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/retail/explore` | 200 기대 |
| V1 보호 | `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` | 200 유지 |

실제 HTTP 상태 코드 및 Git SHA는 서버에서 빌드·푸시 후 기록.

---

## §4. 스크린샷 설명 (텍스트)

- **홈 피드**: 모바일 퍼스트, 카드마다 도매 프로필(아바타·이름·팔로우)·미디어(4:5)·좋아요/댓글/공유/찜 액션·좋아요 수·제목·설명(2줄·더보기)·상품 카드(있을 때 사입하기)·상대 시간(예: 5분 전).
- **탐색**: 상단 검색바·탭 4개·그리드 카드(정사각 썸네일·호버 시 좋아요/댓글·하단 브랜드명).

---

## §5. Git·푸시 결과

| 항목 | 내용 |
|------|------|
| 브랜치 | feature/R2-FRONT-002-feed-ui |
| 커밋 메시지 | [R2-FRONT-002] 홈 피드 + 탐색 UI — 피드카드, 무한스크롤, 탐색그리드, Mock API |
| SHA | (커밋·푸시 후 기록) |
| 푸시 | `GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin feature/R2-FRONT-002-feed-ui` |

---

## §6. 완료 기준 체크리스트

- [x] shadcn/ui 컴포넌트 7종 + button
- [x] 피드 타입 정의 (feed.ts)
- [x] Mock API 레이어 (mock-feed.ts, feed-api.ts)
- [x] FeedCard + FeedCardSkeleton
- [x] ExploreCard
- [x] 홈 피드 페이지 — 무한 스크롤, 좋아요 토글
- [x] 탐색 페이지 — 탭 필터, 그리드, 무한 스크롤
- [x] useInfiniteScroll 훅
- [x] 유틸리티 (formatRelativeTime, formatPrice)
- [ ] 프론트 빌드 성공 + /retail/feed, /retail/explore 200 (서버에서 확인)
- [ ] V1 200 확인 (서버에서 확인)
- [ ] Git 커밋·푸시 (서버에서 실행)
- [x] 보고서·CONTEXT·CHANGELOG·HANDOVER 갱신
- [ ] project-docs 동기화 (서버 /data/project-docs 에서 실행)

**참고**: STEP 1(review 폴더 정리)은 `/data/project-docs/newtalk-v2-api/review/` 경로에서 서버 측 실행 대상이며, 로컬 워크스페이스에는 해당 경로가 없어 생략함.
