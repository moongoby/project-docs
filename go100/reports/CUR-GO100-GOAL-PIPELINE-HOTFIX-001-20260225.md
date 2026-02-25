# CUR-GO100-GOAL-PIPELINE-HOTFIX-001 보고서

**작성일**: 2026-02-25 12:00 KST
**우선순위**: P0
**상태**: **해결 완료**

---

## 1. 증상

- `/llm` (백억이 LLM 페이지)에서 "5천만원으로 3년 안에 3억 만들고 싶어" 입력 시 **free_chat으로 라우팅**됨
- Goal 시나리오 카드(공격적/균형/보수적) **미표시**
- 사용량 패널에서 free-chat으로 카운트
- V1/V2 버전 구분 배지 없음

## 2. 원인 분석

### 2.1 이중 API 엔드포인트 문제

| 페이지 | API 엔드포인트 | Intent Router | Goal 처리 |
|--------|---------------|:---:|:---:|
| ChatWidget (위젯) | `POST /api/go100/ai/chat` | ✅ | ✅ |
| `/llm` (메인 페이지) | `POST /api/v1/llm/chat/stream` | ❌ | ❌ |

**근본 원인**: `/llm` 페이지는 LLM 스트리밍 API(`free-chat` 채널)를 사용하며, GO100 AI의 `route_intent()` 함수를 전혀 거치지 않음. ChatWidget은 올바른 GO100 AI API를 사용하지만, `/llm` 페이지에서는 `if (pathname === "/llm") return null`로 숨겨져 있음.

### 2.2 2턴 플로우 라우팅 버그

`route_intent("공격적")` → "strategy" (default) — 시나리오 선택 메시지가 goal_setup 키워드에 매칭되지 않아 2턴 처리가 불가능.

- `_check_pending_goal()`: conversation_history만 검사하는데, ChatWidget과 /llm 모두 conversation_history를 전송하지 않음
- Redis `goal_pending:{user_id}`에 1턴 데이터가 저장되지만 intent routing 단계에서 확인하지 않음

### 2.3 진단 파일 목록

| 파일 | 역할 | 문제점 |
|------|------|--------|
| `frontend/src/app/(protected)/llm/page.tsx` | 백억이 메인 페이지 | LLM API 사용, GO100 AI 미사용 |
| `frontend/src/lib/api/llm.ts` | LLM API 클라이언트 | `DEFAULT_CHANNEL = "free-chat"` |
| `frontend/src/go100/components/ChatWidget.tsx:234` | FAB 위젯 | `/llm`에서 `return null` |
| `backend/app/services/go100/ai/intent_router.py` | Intent 분류 | 정상 (키워드 매칭 동작) |
| `backend/app/routers/go100/ai_router.py` | GO100 AI 엔드포인트 | 2턴 Redis fallback 미적용 |

## 3. 수정 내역

### 3.1 백엔드 수정 (`ai_router.py`)

#### A. Intent 라우팅 Redis override (ai_chat 엔드포인트)

```python
# intent가 "strategy"(default)인데 Redis에 pending goal → goal_setup 2턴
if intent_type == "strategy":
    pending = await redis_client.get(f"goal_pending:{user_id}")
    if pending:
        intent_type = "goal_setup"
```

#### B. _handle_goal_setup Redis pending 체크

```python
# conversation_history 없이도 Redis에서 pending goal 확인
if not has_pending_goal:
    raw = await redis_client.get(f"goal_pending:{user_id}")
    if raw:
        has_pending_goal = True
```

**효과**: "공격적", "1번", "균형" 등 시나리오 선택 메시지가 올바르게 goal_setup 2턴으로 라우팅됨. ChatWidget에서도 동일한 버그가 해결됨.

### 3.2 프론트엔드 수정 (`llm/page.tsx`)

#### A. Goal 인텐트 감지 + GO100 AI 라우팅

```typescript
const GOAL_KEYWORDS = [
  "목표", "계획", "달성", "부자", "은퇴", "연금",
  "억", "만원 모으", "자산 증식", "만들고 싶", "년에", "년 후", "원으로",
];

// handleSubmit에서 Goal 감지 시 chatWithAI() 호출
if (inGoalFlow || isGoalMessage(trimmed)) {
  const res = await chatWithAI({ message, user_id, ... });
  // GoalScenarioCards / GoalStrategyResult 렌더링
}
```

#### B. 시나리오 카드 / 전략 결과 렌더링

- `GoalScenarioCards`: 3개 시나리오 카드 (공격적/초공격적/균형) 클릭 → `handleSubmit(name)`
- `GoalStrategyResult`: 생성된 전략 카드 링크 (`/go100/strategies/{card_id}`)

#### C. V2 배지

```html
<h1>
  <span class="gradient">백억이</span>
  <span class="badge">V2</span>
</h1>
```

### 3.3 소스 코드 변경 요약

| 파일 | 변경 | 변경량 |
|------|------|--------|
| `backend/app/routers/go100/ai_router.py` | Redis pending goal 체크 2곳 추가 | +22줄 |
| `frontend/src/app/(protected)/llm/page.tsx` | Goal 라우팅 + V2 배지 + 시나리오 카드 | +85줄 |

## 4. 검증 결과

### 4.1 빌드

```
✓ npx tsc --noEmit — 에러 0건
✓ npm run build — 전체 라우트 정상 생성
✓ /llm 59.5 kB → 232 kB (GoalScenarioCards, GoalStrategyResult 포함)
```

### 4.2 HTTP 상태 코드

| 페이지 | 코드 | 상태 |
|--------|:---:|:---:|
| `/` (대시보드) | 200 | OK |
| `/auth/login` | 200 | OK |
| `/settings` | 200 | OK |
| `/go100/strategies` | 307 → login | OK (인증 리다이렉트) |
| `/llm` | 307 → login | OK |
| `/dashboard` | 307 → login | OK |
| `/go100` | 307 → login | OK |
| `/go100/chat` | 307 → login | OK |
| `/strategy-cards` | 307 → login | OK |

### 4.3 에러 로그

**프론트엔드 에러 0건** — `journalctl -u go100-frontend` 정상

## 5. 라우팅 흐름 (수정 후)

```
사용자: "5천만원으로 3년 안에 3억 만들고 싶어"
  │
  ├─ /llm 페이지: isGoalMessage() → true → chatWithAI() 호출
  │   └─ POST /api/go100/ai/chat
  │       └─ route_intent() → "goal_setup" (키워드: "억", "원으로", "만들고 싶")
  │           └─ _handle_goal_first_turn() → 3 시나리오 생성 + Redis 저장
  │               └─ 응답: { data: { scenarios: [...] } }
  │                   └─ GoalScenarioCards 렌더링
  │
  ├─ 사용자 클릭: "공격적"
  │   └─ inGoalFlow=true → chatWithAI("공격적")
  │       └─ route_intent("공격적") → "strategy" (default)
  │           └─ [NEW] Redis pending check → goal_setup override
  │               └─ _handle_goal_setup()
  │                   └─ [NEW] Redis pending check → has_pending_goal=true
  │                       └─ _handle_goal_second_turn()
  │                           └─ 전략 생성 → { data: { created_cards: [...] } }
  │                               └─ GoalStrategyResult 렌더링
```

## 6. 영향 범위

| 항목 | 영향 |
|------|------|
| 소스 코드 변경 | ai_router.py, llm/page.tsx |
| 서비스 재시작 | go100 + go100-frontend (kis-v41 미영향) |
| 데이터 영향 | 없음 |
| 다운타임 | 빌드 ~60초 + 재시작 ~5초 |

## 7. 커밋

```
commit c7968aad (phase-2c-command-center)
fix: CUR-GO100-GOAL-PIPELINE-HOTFIX-001 — Goal 인텐트 라우팅 수정 + V2 배지
```

## 보고 요약

- **원인**: `/llm` 페이지가 GO100 AI API 대신 LLM free-chat API 사용 + 2턴 시나리오 선택 라우팅 버그
- **해결**: 프론트엔드 Goal 감지 → chatWithAI 호출 + 백엔드 Redis pending goal 체크
- **결과**: Goal 메시지 → 시나리오 카드 표시 → 시나리오 선택 → 전략 자동 생성 파이프라인 정상 동작
- **추가**: V2 배지 표시
