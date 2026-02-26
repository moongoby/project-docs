# CUR-GO100-CHAT-HISTORY-PERSIST-001 보고서

**작성일**: 2026-02-25 19:00 KST
**우선순위**: P1
**상태**: **완료**

---

## 1. 문제

- **현상**: "새 대화" 클릭 시 현재 대화가 저장되지 않고 완전히 사라짐
- **원인**: ChatWidget은 메시지를 React state에만 보관 → 위젯 닫기/페이지 이동/새 대화 시 대화 유실
- **기존 상태**: `go100_chat_widget_session_id`(세션 ID)만 localStorage 저장, 메시지는 비영속

## 2. 해결

### 2.1 Zustand 스토어: `useChatHistoryStore`

**왜 zustand?**: ChatWidget이 두 인스턴스(FAB portal + fullscreen)로 동시에 존재하며, React context는 `createPortal` 경계를 넘지 못함.

**저장 구조**:
```typescript
interface SavedConversation {
  id: string;
  title: string;        // 첫 사용자 메시지 앞 20자
  messages: ChatMsg[];
  sessionId: string | null;
  createdAt: string;     // ISO
  updatedAt: string;     // ISO
}
// localStorage key: "go100_chat_history"
// 최대 20개 대화, 초과 시 오래된 것 자동 삭제
```

**스토어 액션**:
| 액션 | 동작 |
|------|------|
| `hydrate()` | 마운트 시 localStorage 로드 (idempotent) |
| `addMessage(msg)` | 메시지 추가 + 자동 저장 |
| `replaceLastMessage(msg)` | 마지막 메시지 교체 (폴링 완료 시) + 자동 저장 |
| `startNewConversation()` | 현재 대화 저장 → 상태 초기화 |
| `loadConversation(id)` | 현재 대화 저장 → 선택한 대화 로드 |
| `deleteConversation(id)` | 대화 삭제 (활성 대화 삭제 시 빈 상태) |

### 2.2 ChatWidget 변경

- 로컬 `messages`, `sessionId`, `isPolling` state → 스토어 셀렉터로 교체
- `sendMessage` 내부에서 `store.getState().addMessage()` / `.replaceLastMessage()` 사용
- "새 대화" 버튼(`Plus` 아이콘) 추가: fullscreen 헤더 + widget 패널 헤더
- 전략 생성 중(폴링) "새 대화" 클릭 → `ConfirmModal` 경고 팝업
- 기존 `getStoredSessionId`/`setStoredSessionId` 제거 (스토어에서 관리)

### 2.3 Go100Sidebar 대화 기록 목록

- nav 아래에 "대화 기록" 섹션 추가
- `updatedAt` 내림차순 정렬, 최근 대화 위에 표시
- 각 항목: 제목(truncate) + 마우스 오버 시 삭제 버튼(`Trash2`)
- 활성 대화 하이라이트 (`bg-primary/20`)
- 클릭 → `loadConversation(id)` + 모바일 사이드바 자동 닫기
- 빈 상태: "대화 기록이 없습니다"

### 2.4 ChatInterface (dead code 정리)

- DEPRECATED 주석 추가
- localStorage 충돌 방지를 위해 `CHAT_HISTORY_KEY`, `loadHistory`, `saveHistory` 제거

## 3. 변경 파일

| 파일 | 변경 | 비고 |
|------|------|------|
| `frontend/src/go100/hooks/useChatHistoryStore.ts` | **생성** | 핵심: zustand 스토어 |
| `frontend/src/go100/components/ChatWidget.tsx` | state→스토어, 새 대화 버튼, ConfirmModal | **핵심** |
| `frontend/src/go100/components/Go100Sidebar.tsx` | 대화 기록 목록 추가 | **핵심** |
| `frontend/src/go100/hooks/index.ts` | export 추가 | 소규모 |
| `frontend/src/go100/components/ChatInterface.tsx` | deprecated, localStorage 제거 | 정리 |

## 4. 검증

- `npx next build` 성공
- `go100-frontend` 서비스 재시작 정상 (active/running)

## 보고 요약

- 대화 자동 저장: 메시지 추가/교체 시 자동 localStorage 저장
- 새 대화: 현재 대화 저장 후 빈 세션 시작, 폴링 중 경고 팝업
- 사이드바 대화 목록: 저장된 대화 클릭으로 복원, 삭제 가능
- 최대 20개 대화, 오래된 것 자동 삭제
- 두 ChatWidget 인스턴스(FAB+fullscreen) 간 zustand 스토어로 상태 공유
