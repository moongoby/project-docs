# R3-FRONT-004 작업 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | R3-FRONT-004 |
| 작업명 | DM UI (대화 목록·대화방·상품공유·읽음처리) |
| 버전 | v2.8.0 |
| 상태 | 완료 |
| 일자 | 2026-02-26 |

## 목표

1:1 DM 채팅 프론트엔드 UI 구현.

- 대화 목록, 대화방(메시지 주고받기), 새 대화 시작
- 읽음 처리, 상품/주문 공유 메시지 렌더링
- 실시간은 polling 방식 (2초 간격), 향후 WebSocket 전환 대비 구조

## 구현 파일 목록

### 타입·API

- `frontend/src/types/dm.ts` — MessageType, ConversationParticipant, MessageData, Conversation, ConversationDetail, MessagesResponse, SendMessageRequest
- `frontend/src/lib/dm-api.ts` — getConversations, createConversation, getConversation, toggleMute, togglePin, leaveConversation, getMessages, sendMessage, markAsRead, deleteMessage (10함수)

### 컴포넌트 (10개)

- `frontend/src/components/dm/ConversationList.tsx` — 대화 목록, 빈 상태, 새 대화 FAB
- `frontend/src/components/dm/ConversationItem.tsx` — 개별 대화 카드, 아바타·상대방·미리보기·unread 뱃지
- `frontend/src/components/dm/ChatRoom.tsx` — 대화방 상단(이름·뒤로·메뉴), 메시지 영역, polling 2초, 이전 메시지 cursor 로드, markAsRead 진입 시
- `frontend/src/components/dm/MessageBubble.tsx` — text/image/product/order/system 타입별 렌더링, is_mine 좌/우, 삭제 옵션
- `frontend/src/components/dm/MessageInput.tsx` — textarea(Enter 전송·Shift+Enter 줄바꿈), 이미지 첨부, 상품 공유(ProductShareDialog)
- `frontend/src/components/dm/ProductShareDialog.tsx` — 찜 목록 조회·검색·선택 시 sendMessage(type: product)
- `frontend/src/components/dm/NewConversationDialog.tsx` — 팔로잉 목록 검색·선택 시 createConversation → 대화방 이동
- `frontend/src/components/dm/ChatMenu.tsx` — 음소거·고정·나가기(확인 다이얼로그)
- `frontend/src/components/dm/UnreadBadge.tsx` — 읽지 않은 수 뱃지
- `frontend/src/components/dm/index.ts` — barrel export

### 페이지·라우트

- `frontend/src/app/(retail)/retail/messages/page.tsx` — 소매 대화 목록
- `frontend/src/app/(retail)/retail/messages/[id]/page.tsx` — 소매 대화방
- `frontend/src/app/(wholesale)/wholesale/messages/page.tsx` — 도매 대화 목록
- `frontend/src/app/(wholesale)/wholesale/messages/[id]/page.tsx` — 도매 대화방

### 레이아웃·연동

- `frontend/src/components/layout/retail-layout.tsx` — 하단 메뉴 "메시지" + UnreadBadge, 헤더 메시지 아이콘 + UnreadBadge
- `frontend/src/components/layout/wholesale-layout.tsx` — 사이드바 "메시지" 메뉴 추가
- `frontend/src/hooks/use-unread-count.ts` — 전체 대화 unread 합산 (getConversations 1페이지)
- `frontend/src/components/product/product-action-bar.tsx` — "문의하기" 버튼 (createConversation(seller_id) → /retail/messages/[id])
- `frontend/src/components/brand/brand-header.tsx` — "메시지 보내기" 버튼 (createConversation(brand.user_id) → /retail/messages/[id])

## 검증

- TypeScript: 서버에서 `docker compose --env-file .env.docker exec frontend npx tsc --noEmit` → 0 에러 확인 권장
- 페이지: /retail/messages, /retail/messages/[id], /wholesale/messages, /wholesale/messages/[id] → 200 또는 302
- V1 헬스: `curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]` → 200

## Git

- 커밋 메시지: `[R3-FRONT-004] DM UI — 대화 목록, 대화방, 상품공유, polling, 10 컴포넌트 (v2.8.0)`

## 다음 작업

- R3-FRONT-005: Shorts UI (R3-API-005 완료 후)
