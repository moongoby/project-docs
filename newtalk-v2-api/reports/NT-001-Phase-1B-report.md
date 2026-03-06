# NT-001 Phase 1-B 완료 보고서 — 메신저 프론트엔드 채팅 UI

**Task ID**: NT-001-1B
**완료일**: 2026-03-06 KST
**의존성**: NT-001 Phase 1-A (커밋 2fd517e)
**우선순위**: P1-HIGH

---

## 1. 작업 요약

Phase 1-A에서 완성된 백엔드 메신저 API 8개 엔드포인트 + WebSocket 이벤트 3개를 기반으로,
프론트엔드 채팅 UI 전체를 구현하였다.

---

## 2. 백업

```
/srv/newtalk-v2/frontend/src/app.bak.20260306_153057/
```

---

## 3. 생성된 파일

### 3-1. 타입 정의 (`frontend/src/types/messenger.ts`)

| 타입 | 필드 |
|------|------|
| `MessageType` | text\|image\|file\|product_card\|order_update\|system |
| `ConversationType` | direct\|group\|support\|order\|product_inquiry |
| `ParticipantRole` | owner\|admin\|member\|observer |
| `MessageAttachment` | id, type, url, filename, size, mime_type |
| `MessageSender` | id, name, avatar |
| `Message` | id, conversation_id, sender_id, type, content, attachments, reply_to, reply_message, is_edited, sender, created_at |
| `ConversationParticipant` | id, user_id, role, unread_count, user |
| `LastMessage` | id, type, content, sender_name, created_at |
| `Conversation` | id, type, title, last_message, participants, unread_count |
| `MessageRead` | id, message_id, user_id, read_at |
| `TypingEvent` | conversation_id, user_id, user_name, is_typing |
| `MessagesResponse` | data, next_cursor, has_more |
| `ConversationsResponse` | data, meta |

### 3-2. API 클라이언트 (`frontend/src/lib/messenger-api.ts`)

| 함수 | HTTP | 엔드포인트 |
|------|------|-----------|
| `getConversations(page?, type?)` | GET | /api/messenger/conversations |
| `createConversation(participantIds, type?, title?)` | POST | /api/messenger/conversations |
| `getMessages(conversationId, cursor?)` | GET | /api/messenger/conversations/{id}/messages |
| `sendMessage(conversationId, content, type?, replyTo?, attachments?)` | POST | /api/messenger/conversations/{id}/messages |
| `markAsRead(conversationId)` | POST | /api/messenger/conversations/{id}/read |
| `sendTyping(conversationId)` | POST | /api/messenger/conversations/{id}/typing |
| `deleteMessage(conversationId, messageId)` | DELETE | /api/messenger/conversations/{id}/messages/{messageId} |
| `uploadFile(conversationId, file)` | POST | /api/messenger/conversations/{id}/files |

### 3-3. Echo 준비 파일 (`frontend/src/lib/echo.ts`)

- Reverb WebSocket 연결 설정 준비 (NEXT_PUBLIC_REVERB_HOST, NEXT_PUBLIC_REVERB_PORT, NEXT_PUBLIC_REVERB_KEY)
- `ECHO_ENABLED = false` — laravel-echo/pusher-js 미설치 상태
- 현재 polling fallback 사용 (2초 간격)
- Reverb 컨테이너 기동 후 활성화 방법 주석 포함
- `getEcho()`, `subscribeToConversation()`, `subscribeToUserChannel()` 함수 준비

### 3-4. 공통 컴포넌트 (`frontend/src/components/messenger/`)

| 파일 | 역할 |
|------|------|
| `MessengerLayout.tsx` | 좌측 대화목록 + 우측 메시지 영역, 반응형 (모바일: 대화목록/메시지 토글) |
| `ConversationList.tsx` | 대화 목록 (검색, 타입 필터 6종, 읽지않은 카운트 뱃지) |
| `ConversationItem.tsx` | 대화 항목 (아바타, 제목, 최근 메시지, 시간, 읽지않은 수) |
| `MessageView.tsx` | 메시지 영역 (스크롤, 날짜 구분선, 2초 polling, 무한스크롤 위로) |
| `MessageBubble.tsx` | 메시지 버블 (내 메시지/상대방, 답장 표시, 편집됨 표시, type별 렌더링) |
| `MessageInput.tsx` | 입력창 (텍스트, 이미지/파일 첨부, 전송, 답장 미리보기, 타이핑 이벤트) |
| `TypingIndicator.tsx` | 타이핑 표시 (점 3개 bounce 애니메이션) |
| `index.ts` | barrel export |

**MessageBubble type별 렌더링:**
- `text`: 일반 텍스트 (whitespace-pre-wrap)
- `image`: 첨부파일 이미지 (클릭 → 새탭)
- `file`: 파일 다운로드 링크 (파일명 + 크기)
- `product_card`: 상품 카드 UI
- `order_update`: 주문 업데이트 UI
- `system`: 중앙 정렬 이탤릭 뱃지

### 3-5. 페이지 (`src/app/*/messenger/page.tsx`)

| 파일 | 경로 |
|------|------|
| `(admin)/admin/messenger/page.tsx` | `/admin/messenger` |
| `(wholesale)/wholesale/messenger/page.tsx` | `/wholesale/messenger` |
| `(retail)/retail/messenger/page.tsx` | `/retail/messenger` |

모두 `<MessengerLayout />`을 렌더링.

### 3-6. 레이아웃 메뉴 추가

| 파일 | 변경 내용 |
|------|----------|
| `admin-layout.tsx` | `MessageSquare` import 추가, `{ href: "/admin/messenger", label: "메신저", icon: MessageSquare }` 항목 추가 |
| `wholesale-layout.tsx` | `MessageSquare` import 추가, `{ href: "/wholesale/messenger", label: "메신저", icon: MessageSquare }` 항목 추가 |
| `retail-layout.tsx` | `MessageSquare` import 추가, 하단 네비게이션에 `{ href: "/retail/messenger", label: "메신저" }` 항목 추가 |

---

## 4. 검증

### 4-1. import 경로 확인

```
grep -rn "from.*messenger" frontend/src/app/ frontend/src/components/messenger/ | head -30
```

결과 13개 모두 `@/components/messenger`, `@/lib/messenger-api`, `@/types/messenger` 경로로 일관성 확인.

### 4-2. npm run build

```
결과: Node.js 호스트 미설치 (docker exec 권한 없음) → 실행 불가
```

호스트에 Node.js / npm이 PATH에 없으며, Docker exec 권한이 없어 컨테이너 내 실행도 불가.
빌드 검증은 **Docker 컨테이너 재기동 후 `npm run build`** 를 실행하여 확인한다.

---

## 5. 아키텍처 메모

- **실시간 통신**: 현재 2초 polling (POLL_INTERVAL_MS = 2000)
- **Echo/Reverb**: `src/lib/echo.ts` 준비 완료. `laravel-echo` + `pusher-js` 설치 후 `ECHO_ENABLED = true`로 변경하면 활성화
- **메신저 vs DM**: 기존 `/api/conversations/` (dm-api.ts, components/dm/)는 그대로 유지. 신규 `/api/messenger/` (messenger-api.ts, components/messenger/)는 별도 모듈
- **반응형**: md 이상에서는 좌우 분할, md 미만에서는 리스트/채팅 토글

---

## 6. 다음 단계

- Reverb 컨테이너 기동 → `npm install laravel-echo pusher-js` → `echo.ts` ECHO_ENABLED=true
- Docker 컨테이너 내 `npm run build` 검증
- Phase 2, 3: 별도 지시서 (NT-002, NT-003)
