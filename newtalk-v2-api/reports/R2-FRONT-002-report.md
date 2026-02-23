# R2-FRONT-002 보고서 — 홈 피드 + 탐색 UI

- **작업일**: 2026-02-23
- **브랜치**: feature/R2-FRONT-002-feed-ui
- **Git SHA**: ed3177b8ecc33b4aa119b5f817f4e2c27bd44436
- **GitHub**: https://github.com/moongoby/newtalk-v2-api-

## 요약
피드카드, 무한스크롤, 탐색 그리드, API 연동 (USE_MOCK=false)

## 추가/수정 파일
- frontend/src/types/feed.ts
- frontend/src/lib/feed-api.ts, mock-feed.ts, date-utils.ts
- frontend/src/hooks/use-infinite-scroll.ts
- frontend/src/components/feed/feed-card.tsx, feed-card-skeleton.tsx, explore-card.tsx
- frontend/src/components/ui/card.tsx, avatar.tsx, button.tsx, skeleton.tsx, tabs.tsx
- frontend/src/app/(retail)/feed/page.tsx, explore/page.tsx

## 테스트
- /feed: 307 (리다이렉트), /explore: 307, V1: 200
