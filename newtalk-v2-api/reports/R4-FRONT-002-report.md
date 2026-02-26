# R4-FRONT-002 스토리 UI — 완료 보고서

**작업 ID**: R4-FRONT-002  
**버전**: v3.7.0  
**완료 시각**: 2026-02-26 KST  
**선행**: R4-API-002 (스토리 API) — 프론트 구현 완료, API 연동 준비

---

## 1. 요약

인스타그램 스타일 스토리 UX: 피드 상단 스토리 바, 풀스크린 뷰어, 도매 업로드/관리, 소매 시청·리액션, 브랜드 하이라이트 연동.

---

## 2. 구현 목록

### 2.1 타입 (frontend/src/types/story.ts)
- `Story`: id, user_id, media_url, media_type, caption, link_url, link_type, duration_seconds, view_count, expires_at, is_highlight 등
- `StoryView`: 조회자·리액션·viewed_at
- `StoryGroup`: 사용자별 묶음 (user_id, user_name, user_avatar, stories, has_unread)
- `StoryFeedResponse`: data: StoryGroup[]

### 2.2 API 클라이언트 (frontend/src/lib/story-api.ts) — 8함수
| 함수 | 메서드/경로 | 비고 |
|------|-------------|------|
| getStoryFeed | GET stories/feed | 피드용 그룹 목록 |
| getUserStories | GET stories/user/{id} | 특정 사용자 스토리 목록 |
| getMyStories | GET stories/me | 내 스토리 목록 |
| createStory | POST stories | 업로드 |
| deleteStory | DELETE stories/{id} | 삭제 |
| recordView | POST stories/{id}/view | 조회 기록 |
| react | POST stories/{id}/react | 리액션 (like, fire, clap, wow, sad) |
| toggleHighlight | POST stories/{id}/highlight | 하이라이트 토글 |

### 2.3 컴포넌트 10개 (frontend/src/components/story/)
| 컴포넌트 | 역할 |
|----------|------|
| StoryBar | 피드 상단 가로 스크롤 스토리 바 (아바타 링, unread=gradient/read=회색) |
| StoryAvatar | 개별 아바타 + 이름, unread 상태 |
| StoryViewer | 풀스크린 뷰어 (좌/우 탭, 프로그레스 바, 5초 자동 넘김) |
| StoryMediaDisplay | 이미지/영상 표시, 캡션 오버레이 |
| StoryReactionBar | 하단 리액션 (like, fire, clap, wow, sad) + 메시지 버튼 |
| StoryUploadPage | 업로드 폼 (미디어 URL, 캡션, 링크 연결 상품/브랜드/외부) |
| StoryViewersList | 조회자 목록 (누가 봤는지 + 리액션) |
| MyStoriesPage | 내 스토리 관리 (활성/만료, 하이라이트 토글, 삭제) |
| StoryHighlights | 브랜드 페이지 하이라이트 원형 캐러셀 |
| index | barrel export |

### 2.4 페이지·라우트 3개
| 경로 | 역할 |
|------|------|
| /wholesale/stories/new | 도매: 스토리 업로드 |
| /wholesale/stories | 도매: 내 스토리 관리 |
| /retail/stories | 소매: 스토리 피드 (전용 페이지, ?user= 로 뷰어 진입) |

### 2.5 기존 페이지 연동
- **/retail/feed**: 상단에 StoryBar 삽입
- **/brand/[slug]**: StoryHighlights 삽입 (brandUserId, slug 전달)
- **wholesale-layout**: "스토리" 메뉴 → /wholesale/stories (CircleDot 아이콘)

---

## 3. 검증

- 문서: CHANGELOG, CONTEXT, HANDOVER, NT-V2-ARCHITECTURE 갱신
- Lint: 수정 구역 기준 0건

---

## 4. 파일 목록 (신규·수정)

**신규**
- frontend/src/types/story.ts
- frontend/src/lib/story-api.ts
- frontend/src/components/story/StoryBar.tsx
- frontend/src/components/story/StoryAvatar.tsx
- frontend/src/components/story/StoryViewer.tsx
- frontend/src/components/story/StoryMediaDisplay.tsx
- frontend/src/components/story/StoryReactionBar.tsx
- frontend/src/components/story/StoryUploadPage.tsx
- frontend/src/components/story/StoryViewersList.tsx
- frontend/src/components/story/MyStoriesPage.tsx
- frontend/src/components/story/StoryHighlights.tsx
- frontend/src/components/story/index.ts
- frontend/src/app/(wholesale)/wholesale/stories/page.tsx
- frontend/src/app/(wholesale)/wholesale/stories/new/page.tsx
- frontend/src/app/(retail)/retail/stories/page.tsx

**수정**
- frontend/src/app/(retail)/retail/feed/page.tsx (StoryBar 추가)
- frontend/src/app/(retail)/brand/[slug]/page.tsx (StoryHighlights 추가)
- frontend/src/components/layout/wholesale-layout.tsx (스토리 메뉴)
- docs/CHANGELOG.md, docs/CONTEXT.md, docs/handover/HANDOVER.md, docs/architecture/NT-V2-ARCHITECTURE.md
