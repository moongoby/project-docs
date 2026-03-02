# R2-FRONT-006 작업 보고서

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | R2-FRONT-006 |
| 작업명 | 도매 콘텐츠 업로드 UI |
| 작업일 | 2026-02-24 KST |
| 버전 | v1.8.0 |
| 커밋 SHA | 520353b |
| 상태 | 완료 |

## 구현 기능
### 페이지
1. `/wholesale/content` — 콘텐츠 관리 목록 (그리드/리스트 뷰, 타입·상태 필터, 페이지네이션)
2. `/wholesale/content/new` — 새 콘텐츠 작성
3. `/wholesale/content/[id]/edit` — 콘텐츠 수정

### 컴포넌트
- **MediaUploader**: 드래그앤드롭, 다중 파일(최대 10장), 미리보기 그리드, 개별 삭제, 이미지 10MB/영상 100MB 제한, jpg/png/webp/mp4/mov
- **ContentEditor**: 타입 선택(이미지/영상/룩북/코디), 제목/본문(2000자), 미디어, 상품 태그, 공개/비공개 스위치
- **ProductTagSelector**: 상품 검색(debounce 300ms), 태그 추가/제거(최대 10개)
- **ContentList**: 그리드/리스트 뷰 토글, 필터(타입·상태), 페이지네이션, 삭제(AlertDialog 확인)
- **ContentCard**: 썸네일 카드(그리드/리스트), 타입 배지, 좋아요/조회수
- **ContentPreview**: 발행 전 미리보기(FeedCard 스타일)

### API (lib/content-api.ts)
- getMyContents, getContent, createContent, updateContent, deleteContent
- uploadMedia(진행률 지원, 백엔드 API 구현 시 연동)
- searchMyProducts

### UI 컴포넌트 (shadcn 스타일)
- input, label, textarea, progress, switch, alert-dialog

### 네비게이션
- wholesale 레이아웃 사이드바에 콘텐츠 메뉴 이미 존재 (`/wholesale/content`)

## 신규/수정 파일
- `frontend/src/types/content.ts` (신규)
- `frontend/src/lib/content-api.ts` (신규)
- `frontend/src/lib/api.ts` (FormData 시 Content-Type 미설정)
- `frontend/src/components/ui/input.tsx`, `label.tsx`, `textarea.tsx`, `progress.tsx`, `switch.tsx`, `alert-dialog.tsx` (신규)
- `frontend/src/components/content/MediaUploader.tsx`, `ProductTagSelector.tsx`, `ContentEditor.tsx`, `ContentList.tsx`, `ContentCard.tsx`, `ContentPreview.tsx`, `index.ts` (신규)
- `frontend/src/app/(wholesale)/wholesale/content/page.tsx`, `content/new/page.tsx`, `content/[id]/edit/page.tsx` (신규)

## 검수 결과
- **TypeScript 컴파일**: 서버 `/srv/newtalk-v2`에서 `docker compose --env-file .env.docker exec frontend npx tsc --noEmit` 실행 후 결과 확인. (로컬에 Docker/env 없으면 해당 서버에서 실행)
- **페이지 렌더링**: 서버에서 `docker compose --env-file .env.docker up -d --build frontend` 후 `curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]:3000/wholesale/content` → 200, `curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]:3000/wholesale/content/new` → 200 확인.
- **V1 헬스**: **200** (curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP])

## 비고
- 파일 업로드 백엔드 API는 R2-API-003에서 구현 예정. 현재는 프론트만 구현, API 연동 시 `contents`, `contents/mine`, `contents/{id}`, `media/upload`, `products/mine` 엔드포인트 필요.
- Mock 또는 기존 POST /api/feed 활용 가능 until R2-API-003 완료.

## 서버 측 마무리 (필수)
- `/srv/newtalk-v2`에서 코드 커밋·푸시 후 위 "커밋 SHA"에 실제 7자리 SHA 기록. (본 문서는 520353b 반영됨)
- CONTEXT.md, CHANGELOG.md, HANDOVER.md 내 R2-FRONT-006·R2-API-003 관련 플레이스홀더를 동일 SHA(520353b)로 교체 후 재커밋·푸시.
- project-docs 동기화 후 push (보고서 규칙 §16).
