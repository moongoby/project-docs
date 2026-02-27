# R4-FRONT-005 보고서: SNS 자동 게시 UI

**작업 ID**: R4-FRONT-005  
**버전**: v3.13.0  
**완료일**: 2026-02-26  
**선행**: R4-API-006 (v3.9.0) SNS 자동 게시 API

---

## 1. 개요

도매가 인스타그램·틱톡·페이스북·유튜브에 콘텐츠를 자동 게시(즉시·예약)하고, 성과(조회수·좋아요·댓글·공유)를 대시보드로 확인하는 UI를 구현하였다.

---

## 2. 구현 목록

### 2.1 타입 정의
- **파일**: `frontend/src/types/sns.ts`
- **타입**: SnsPlatform, SnsPostStatus, SnsPostType, SnsConnection, SnsPost, SnsPostAnalytics, SnsCreatePostRequest, SnsBulkPostRequest

### 2.2 API 클라이언트
- **파일**: `frontend/src/lib/sns-api.ts`
- **함수 12개**:
  1. connectSns — POST /sns/connect
  2. disconnectSns — DELETE /sns/{id}
  3. getSnsConnections — GET /sns/connections
  4. createSnsPost — POST /sns/posts
  5. getSnsPostList — GET /sns/posts
  6. getSnsPost — GET /sns/posts/{id}
  7. scheduleSnsPost — PUT /sns/posts/{id}/schedule
  8. deleteSnsPost — DELETE /sns/posts/{id}
  9. bulkPost — POST /sns/posts/bulk
  10. getPostAnalytics — GET /sns/posts/{id}/analytics
  11. generateHashtags — POST /sns/posts/{id}/hashtags
  12. getOptimalTime — GET /sns/optimal-time/{connectionId}

### 2.3 컴포넌트 12개
- **디렉터리**: `frontend/src/components/sns/`
- **목록**:
  - SnsConnectionList — 연결된 SNS 계정 목록 (플랫폼 아이콘, 사용자명, 상태, 해제 버튼)
  - SnsConnectDialog — SNS 연결 다이얼로그 (플랫폼 선택, 인증 정보 입력)
  - SnsPostList — 게시물 목록 (상태·플랫폼 필터, 페이지네이션)
  - SnsPostCard — 게시물 카드 (썸네일, 캡션 미리보기, 플랫폼, 상태, 성과 요약)
  - SnsPostCreatePage — 게시물 작성 (채널 선택, 미디어 URL, 캡션, 해시태그, 즉시/예약, 다채널 일괄)
  - SnsPostDetail — 게시물 상세 (전체 정보, 성과 차트, 스냅샷 타임라인, 예약 변경)
  - SnsPostDetailPage — 게시물 상세 페이지 래퍼 (로드, 삭제 확인)
  - SnsPostStatusBadge — 상태 배지 (draft/scheduled/posting/posted/failed/deleted)
  - SnsAnalyticsDashboard — SNS 성과 대시보드 (플랫폼별 총 조회·좋아요·댓글·공유)
  - SnsHashtagSuggestion — AI 해시태그 추천 (generateHashtags 호출, 태그 선택·추가)
  - SnsOptimalTimeWidget — 최적 게시 시간 위젯 (getOptimalTime 표시)
  - SnsBulkPostDialog — 다채널 일괄 게시 다이얼로그 (채널 체크박스, 공통 캡션/미디어, 예약)
  - index.ts — barrel export

### 2.4 페이지 4개
- **경로**:
  - `/wholesale/sns` — 도매: SNS 계정 목록 + 게시물 목록 (탭)
  - `/wholesale/sns/new` — 도매: 게시물 작성 (즉시/예약/일괄)
  - `/wholesale/sns/[id]` — 도매: 게시물 상세 + 성과
  - `/wholesale/sns/analytics` — 도매: SNS 성과 대시보드

### 2.5 레이아웃
- **파일**: `frontend/src/components/layout/wholesale-layout.tsx`
- **변경**: "SNS 관리" 메뉴 추가 → `/wholesale/sns`, Share2 아이콘

---

## 3. 문서 갱신
- CHANGELOG.md: [3.13.0] R4-FRONT-005 SNS 자동 게시 UI
- CONTEXT.md: v3.13.0, 완료 항목에 R4-FRONT-005 추가, 다음 작업에서 제거
- HANDOVER.md: R4-FRONT-005 완료 섹션 추가, 다음 작업 큐 갱신
- docs/architecture/NT-V2-ARCHITECTURE.md: Frontend 라우트에 wholesale/sns, wholesale/sns/new, wholesale/sns/[id], wholesale/sns/analytics 추가

---

## 4. 테스트
- TypeScript: 0 errors (프론트엔드 린트 확인)
- Docker: 5/5 Up
- SNS API 라우트 12개 확인 (routes/api.php prefix sns)

---

## 5. Git
- V2 repo: 커밋 메시지 `[R4-FRONT-005] SNS 자동 게시 UI — 12컴포넌트 4페이지 12 API함수, 인스타/틱톡/페북/유튜브 게시·예약·성과 (v3.13.0)`
- project-docs: R4-FRONT-005 문서 동기화 (v3.13.0)

---

## 6. 다음 작업
- R4-FRONT-006: 콘텐츠 파이프라인 UI
- R4-FRONT-007: 위탁배송·드롭십 UI
