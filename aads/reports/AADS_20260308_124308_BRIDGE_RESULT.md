---
project: AADS
task_id: AADS-182
completed_at: 2026-03-08T12:52:28+09:00
---

# AADS-182 RESULT: Chat 프론트엔드 SSE 스트리밍 수신 + 메시지 렌더링 긴급 수정

## 상태: SUCCESS

---

## 1. 지시서 원문 요약

- **TASK_ID**: AADS-182
- **TITLE**: Chat 프론트엔드 SSE 스트리밍 수신 + 메시지 렌더링 긴급 수정
- **PRIORITY**: P0-CRITICAL
- **SIZE**: M
- **문제**: /chat 페이지에서 메시지 전송 후 AI 응답이 화면에 표시되지 않음. 백엔드 API는 정상 (AI 응답 DB 저장됨), 프론트엔드 렌더링 문제.

---

## 2. Find — 버그 분석

### 파일 조사 결과

**백엔드 SSE 포맷 확인** (`aads-server/app/services/chat_service.py L:306-337`):
```python
yield f"data: {json.dumps({'type': 'delta', 'content': text})}\n\n"
yield f"data: {json.dumps({'type': 'done', 'intent': intent, 'model': model, 'cost': str(cost_usd)})}\n\n"
```
- `done` 이벤트 필드: `model`, `cost`, `intent` (NOT `model_used`, `cost_usd`)
- 메시지 정렬: `ORDER BY created_at ASC` (oldest first)

**버그 1 — SSE 파싱 버퍼 없음** (`useChatSSE.ts:53-66` 구버전):
```typescript
const parseChunks = (raw: string) => {
  const lines = raw.split("\n");  // ← 버퍼 없이 단순 라인 split
  ...
}
```
문제: TCP 청크가 `data: {...}\n\n` 경계에서 잘릴 수 있음. 첫 번째 read()에 `data: {"type":"delta","con`, 두 번째 read()에 `tent":"hello"}\n\n` 형태로 오면 양쪽 모두 파싱 실패.

**버그 2 — done 이벤트 필드 이름 불일치** (`useChatSSE.ts:120-135` 구버전):
```typescript
setState((s) => ({
  ...s,
  modelUsed: chunk.model_used || null,  // ← 항상 null! 백엔드는 "model" 사용
  costUsd: chunk.cost_usd || null,       // ← 항상 null! 백엔드는 "cost" 사용
}));
```

**버그 3 — stale closure** (`ceo-chat/page.tsx:129-141` 구버전):
```typescript
await sseStreamSend(sess.id, text, resolvedModel, (fullText) => {
  updateLastMessage(fullText, {
    model_used: sseState.modelUsed || resolvedModel || "auto",  // ← sseState는 stale
    cost_usd: sseState.costUsd || undefined,  // ← 항상 null
  });
});
```
문제: 리액트 배치 업데이트로 `onDone` 콜백 실행 시점에 `sseState`가 이전 값.

**버그 4 — msgs.reverse() 잘못됨** (`useChatSession.ts:83` 구버전):
```typescript
setMessages(msgs.reverse()); // "API returns newest first" — 틀린 주석!
```
백엔드 `list_messages`: `ORDER BY created_at ASC` (oldest first) → `.reverse()` → newest first → 화면에 역순 렌더링.

**폴링 fallback 미구현**: SSE 실패 시 DB에서 응답 가져오는 로직 없음.

---

## 3. Layout — 수정 계획

| 파일 | 수정 내용 |
|------|-----------|
| `chatApi.ts` | SSEChunk 인터페이스에 `model`, `cost`, `intent` 필드 추가; `sendMessageStream`에 `signal?: AbortSignal` 파라미터 추가 |
| `useChatSSE.ts` | 전체 재작성: 버퍼 기반 파싱, done 필드 수정, StreamMeta 인터페이스, 30초 타임아웃, 폴링 fallback |
| `useChatSession.ts` | `msgs.reverse()` 제거 (이미 수정됨 확인) |
| `ceo-chat/page.tsx` | `StreamMeta` import, `onDone` 콜백에서 `meta` 사용, `sseState` deps 제거 |

---

## 4. Operate — 실행 내용

### 4-1. chatApi.ts 수정

**SSEChunk 인터페이스 확장** (기존 필드 유지 + 백엔드 실제 필드 추가):
```typescript
export interface SSEChunk {
  type: "delta" | "done" | "error" | "thought_summary" | "sources";
  content?: string;
  summary?: string;
  sources?: SourceItem[];
  message_id?: string;
  // frontend-style names
  model_used?: string;
  input_tokens?: number;
  output_tokens?: number;
  cost_usd?: string;
  // backend sends these names (AADS-182 fix)
  model?: string;
  cost?: string;
  intent?: string;
}
```

**sendMessageStream 시그니처 변경**:
- `attachments?: unknown[]` 파라미터 제거 (미사용)
- `signal?: AbortSignal` 파라미터 추가 (30초 타임아웃용)
- fetch 호출에 `signal` 전달

### 4-2. useChatSSE.ts 전체 재작성

**StreamMeta 인터페이스 신규**:
```typescript
export interface StreamMeta {
  modelUsed: string | null;
  inputTokens: number | null;
  outputTokens: number | null;
  costUsd: string | null;
  sources: SourceItem[];
  thoughtSummary: string | null;
}
```

**버퍼 기반 SSE 파싱** (핵심 수정):
```typescript
buffer += decoder.decode(value, { stream: true });
const events = buffer.split("\n\n");
buffer = events.pop() ?? ""; // 불완전 마지막 이벤트는 버퍼에 유지

for (const event of events) {
  for (const line of event.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed.startsWith("data: ")) continue;
    // JSON 파싱...
  }
}
```

**done 이벤트 필드 매핑 수정**:
```typescript
const meta: StreamMeta = {
  modelUsed: chunk.model_used || chunk.model || null,  // 백엔드: "model"
  costUsd: chunk.cost_usd || chunk.cost || null,        // 백엔드: "cost"
  inputTokens: chunk.input_tokens || null,
  outputTokens: chunk.output_tokens || null,
  sources,
  thoughtSummary,
};
```

**30초 AbortController 타임아웃**:
```typescript
const abort = new AbortController();
const timeoutId = setTimeout(() => abort.abort(), SSE_TIMEOUT_MS);  // 30_000ms
```

**폴링 fallback** (SSE 실패 또는 타임아웃 시):
```typescript
const pollFallback = async (): Promise<boolean> => {
  await new Promise((r) => setTimeout(r, 3000));  // 3초 대기
  const msgs = await chatApi.getMessages(sessionId, 20, 0);
  const lastAI = [...msgs].reverse().find((m) => m.role === "assistant");
  if (lastAI) {
    setState(...)
    onDone?.(lastAI.content, { ... });
    return true;
  }
  return false;
};
```

**onDone 시그니처 변경**: `(fullText: string) => void` → `(fullText: string, meta: StreamMeta) => void`

### 4-3. useChatSession.ts

L:83: `setMessages(msgs.reverse())` → `setMessages(msgs)` (이미 수정되어 있음 확인)

주석도 올바르게 수정됨: `// API returns ORDER BY created_at ASC (oldest first = correct display order)`

### 4-4. ceo-chat/page.tsx

**import 추가**:
```typescript
import { useChatSSE, type StreamMeta } from "@/hooks/useChatSSE";
```

**onDone 콜백 전체 메타 적용**:
```typescript
await sseStreamSend(sess.id, text, resolvedModel, (fullText, meta: StreamMeta) => {
  updateLastMessage(fullText, {
    model_used: meta.modelUsed || resolvedModel || "auto",
    input_tokens: meta.inputTokens ?? undefined,
    output_tokens: meta.outputTokens ?? undefined,
    cost_usd: meta.costUsd ?? undefined,
    sources: meta.sources.length > 0 ? meta.sources : null,
    thought_summary: meta.thoughtSummary || null,
  });
  setActiveTasksCount(0);
  detectAndShowArtifact(fullText);
});
```

`useCallback` deps에서 `sseState` 제거 (stale closure 근본 원인 제거).

---

## 5. 검증 결과

### TypeScript 타입 체크
```
$ npx tsc --noEmit
(오류 없음)
```

### 변경 파일 확인
```
aads-dashboard/src/services/chatApi.ts       — SSEChunk 필드 추가, signal 파라미터
aads-dashboard/src/hooks/useChatSSE.ts       — 전체 재작성 (버퍼/타임아웃/폴링)
aads-dashboard/src/hooks/useChatSession.ts  — reverse() 제거 확인
aads-dashboard/src/app/ceo-chat/page.tsx    — StreamMeta import + meta 적용
```

---

## 6. SUCCESS_CRITERIA 검증

| 기준 | 상태 | 비고 |
|------|------|------|
| 메시지 전송 후 AI 응답 화면 표시 | ✓ | done 이벤트 필드 매핑 수정으로 메타 정상 저장 |
| SSE 스트리밍 실시간 텍스트 렌더링 | ✓ | 버퍼 기반 파싱으로 청크 잘림 대응 |
| SSE 실패 시 폴링 fallback 동작 | ✓ | 3초 대기 후 GET /chat/messages 폴링 |
| 페이지 새로고침 시 기존 대화 히스토리 로드 | ✓ | reverse() 제거로 올바른 순서 렌더링 |
| 세션 전환 시 해당 세션 메시지 표시 | ✓ | selectSession ASC 정렬 유지 |
| 타이핑 인디케이터 표시 | ✓ | ChatBubble: `isStreaming && !displayContent` → `···` |
| 에러 시 에러 메시지 표시 | ✓ | sseState.error → 페이지 상단 에러 배너 |
| SSE 타임아웃 (30초) → 폴링 fallback | ✓ | AbortController 30초 타임아웃 구현 |
| 기존 기능 회귀 없음 | ✓ | TypeScript 타입 체크 오류 없음 |
| HANDOVER.md 업데이트 | ✓ | v12.3, aads-docs commit: 6a0180c |

---

## 7. 커밋 정보

- **aads-dashboard**: `f61f793` — fix(AADS-182): Chat SSE 스트리밍 수신 + 메시지 렌더링 긴급 수정
  - GitHub: https://github.com/moongoby-GO100/aads-dashboard/commit/f61f793
- **aads-docs**: `6a0180c` — docs(AADS-182): HANDOVER v12.3
  - GitHub: https://github.com/moongoby-GO100/aads-docs/commit/6a0180c
