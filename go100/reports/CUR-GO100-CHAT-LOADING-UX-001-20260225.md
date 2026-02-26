# CUR-GO100-CHAT-LOADING-UX-001 보고서

**작성일**: 2026-02-25 18:30 KST
**우선순위**: P0
**상태**: **완료**

---

## 1. 문제

### 1.1 Cloudflare 524 타임아웃 (P0)

- **현상**: Goal 2턴(전략 생성), strategy(전략 설계), optimize_existing(최적화) 처리 시 1~5분 소요 → Cloudflare 100초 타임아웃(524) → 사용자에게 "오류: Request failed with status code 524" 표시
- **실제 로그**: card_25(스캘핑) LLM 설계 3.5분 + 백테스트 37초, card_26(스윙) 설계 30초 + 백테스트 1초 → 총 5.5분
- **백엔드는 정상 완료**하지만 프론트가 응답을 받지 못함

### 1.2 로딩 피드백 부재 (P1)

- **ChatWidget** (위젯 모드): `...` 3점만 표시, 진행 단계 없음
- **ChatInterface** (전체화면): AIProgressIndicator 존재하나 가짜 타이머 기반 (30초 후 "거의 완료됩니다...")
- 사용자 입장에서 1~5분간 아무 피드백 없이 대기

## 2. 해결 전략

**비동기 태스크 + 폴링 방식** 채택.

| 비교 항목 | SSE (Server-Sent Events) | **폴링 (채택)** |
|-----------|--------------------------|----------------|
| Cloudflare 호환 | SSE도 100초 제한 | 각 폴링 50ms 이내 응답 |
| 구현 난이도 | 높음 (연결 관리) | **낮음** |
| 네트워크 안정성 | 끊김에 취약 | **강건** (재시도 자동) |
| 기존 인프라 영향 | notification_router SSE와 충돌 우려 | **없음** |

## 3. 변경 내용

### 3.1 Backend: 비동기 태스크 시스템 (`ai_router.py`)

**JSON 파일 기반** 태스크 트래킹 (멀티 워커 호환):

```
/tmp/go100_tasks/{task_id}.json
```

| 함수 | 역할 |
|------|------|
| `_create_task(user_id)` | 태스크 파일 생성, task_id 반환 |
| `_read_task(task_id)` | 태스크 상태 읽기 |
| `_update_task(task_id, stage, detail)` | 진행 단계 업데이트 |
| `_complete_task(task_id, result)` | 완료 처리 (OrchestrationResult → dict 변환) |
| `_fail_task(task_id, error)` | 에러 처리 |
| `_cleanup_old_tasks()` | 완료 1분/processing 10분 초과 파일 삭제 |

**왜 JSON 파일?**: `--workers 2` 환경에서 인메모리 dict는 워커 간 공유 불가. Redis는 과도, 파일 기반이 최적.

### 3.2 Backend: 비동기 처리 대상

| 인텐트 | 동기/비동기 | 소요 시간 |
|--------|-----------|----------|
| help | 동기 | < 1초 |
| stock_info | 동기 | < 2초 |
| market_briefing | 동기 | < 2초 |
| portfolio_status | 동기 | < 2초 |
| stock_screening | 동기 | < 3초 |
| goal_setup 1턴 | 동기 | < 1초 |
| **goal_setup 2턴** | **비동기** | **1~5분** |
| **strategy** | **비동기** | **10초~3분** |
| **optimize_existing** | **비동기** | **30초~2분** |

### 3.3 Backend: `GET /api/go100/ai/task/{task_id}` 엔드포인트

```
GET /api/go100/ai/task/{task_id}
Authorization: Bearer {token}

# Processing 중:
{"status": "processing", "stage": "designing", "stage_detail": "전략을 설계하고 있습니다..."}

# 완료:
{"status": "completed", "reply_to_user": "...", "strategy_card_id": 27, ...}

# 에러:
{"status": "error", "reply_to_user": "처리 중 오류가 났어요...", "error": "..."}
```

### 3.4 Backend: 진행 단계

| stage | stage_detail | AIProgressIndicator 매핑 |
|-------|-------------|-------------------------|
| `analyzing` | 요청을 분석하고 있습니다... | UNDERSTAND |
| `designing` | 전략을 설계하고 있습니다... | DESIGN |
| `backtesting` | 백테스트를 실행하고 있습니다... | BACKTEST |
| `evaluating` | 성과를 평가하고 있습니다... | EVALUATE |
| `completing` | 결과를 정리하고 있습니다... | OPTIMIZE |

Goal 2턴에서는 `전략 {i+1}/{total} 설계 중...`, `전략 {i+1}/{total} 백테스트 중...` 등 상세 표시.

### 3.5 Backend: Background Task 패턴

```python
task_id = _create_task(user_id)

async def _bg_strategy():
    from backend.app.core.database import AsyncSessionLocal
    try:
        _update_task(task_id, "designing", "전략을 설계하고 있습니다...")
        async with AsyncSessionLocal() as bg_db:
            resp = await orch.process_message(...)
            _complete_task(task_id, resp)  # model_dump() → JSON
    except Exception as e:
        _fail_task(task_id, str(e))

asyncio.create_task(_bg_strategy())
return OrchestrationResult(status="processing", data={"task_id": task_id})
```

**DB 세션 주의**: `asyncio.create_task`로 분리 시 기존 `db` 세션이 request scope에 묶여 있으므로, 백그라운드 태스크 내부에서 `AsyncSessionLocal()`로 새 세션 생성.

### 3.6 Frontend: 타입 (`types/ai.ts`)

```typescript
export interface GoalChatData {
  // ... 기존 필드 ...
  task_id?: string;  // 비동기 태스크 ID
}

export interface TaskStatusResponse {
  status: "processing" | "completed" | "error";
  stage?: string;
  stage_detail?: string;
  [key: string]: unknown;
}
```

### 3.7 Frontend: API (`go100Api.ts`)

```typescript
export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const { data } = await go100Client.get<TaskStatusResponse>(`${BASE}/ai/task/${taskId}`);
  return data;
}
```

### 3.8 Frontend: AIProgressIndicator (`AIProgressIndicator.tsx`)

- `stage` prop 추가: 서버에서 보고한 진행 단계 반영
- `stageDetail` prop 추가: 서버 상세 설명 표시
- `stage` 있으면 서버 단계 기반, 없으면 기존 타이머 기반 (폴백)
- `STAGE_TO_INDEX` 매핑: `analyzing→0, designing→1, backtesting→2, evaluating→3, completing→4`

### 3.9 Frontend: ChatWidget + ChatInterface 폴링

```typescript
const pollTaskUntilDone = async (taskId: string): Promise<ChatResponse> => {
  for (let i = 0; i < 180; i++) {  // 최대 6분
    await new Promise(r => setTimeout(r, 2000));  // 2초 간격
    const status = await getTaskStatus(taskId);
    if (status.status !== "processing") return status;  // 완료
    setPollStage(status.stage);  // AIProgressIndicator 업데이트
  }
};
```

- `res.status === "processing" && res.data?.task_id` 감지 → 폴링 시작
- 폴링 중 `AIProgressIndicator` 표시 (서버 stage 기반)
- 완료 시 마지막 "처리 중" 메시지를 결과로 교체

## 4. 발견 이슈 및 해결

### 4.1 멀티 워커 인메모리 딕셔너리 공유 불가

- **문제**: `--workers 2` 환경에서 `dict` 기반 태스크 트래킹 → POST 워커 A, GET 워커 B → 404
- **해결**: JSON 파일 기반 (`/tmp/go100_tasks/`) — 파일시스템은 워커 간 공유

### 4.2 OrchestrationResult Pickle 직렬화 실패

- **문제**: Pydantic 모델 pickle 직렬화 → 파일 소실/데이터 손상
- **해결**: `pickle` → `json` 전환, `_complete_task`에서 `model_dump()` 호출하여 dict 변환 후 JSON 저장

### 4.3 `needs_clarification` 상태 미처리

- **문제**: 프론트 폴링에서 `completed`/`error`만 종료 조건 → `needs_clarification` 시 무한 폴링
- **해결**: `status !== "processing"` 이면 모두 종료 (모든 비-processing 상태 = 완료)

### 4.4 GET 엔드포인트 파일 즉시 삭제 → 재시도 불가

- **문제**: 완료 결과 반환 시 파일 즉시 삭제 → 네트워크 오류 시 재폴링 불가
- **해결**: 파일 삭제를 `_cleanup_old_tasks`에 위임 (완료 1분, processing 10분 후 자동 삭제)

## 5. Pre-existing 빌드 오류 수정

| 파일 | 문제 | 수정 |
|------|------|------|
| `GoalTracking.tsx` | recharts Tooltip formatter 타입 불일치 | `...args: unknown[]` 패턴으로 변경 |
| `StockChart.tsx` | `lineWidth: 0` → `DeepPartial<LineWidth>` 타입 오류 | `lineWidth: 1`, cast 추가 |
| `bt_chart.py` | 괄호 누락 문법 오류 (line 616) | 닫는 괄호 추가 |
| `backtest-chart.ts` | `BtChartCandle.time: string | number` → `ChartOhlcvBar.time: string` 불일치 | `string`으로 통일 |

## 6. 변경 파일

| 파일 | 변경 | 비고 |
|------|------|------|
| `backend/app/routers/go100/ai_router.py` | 비동기 태스크 시스템 + GET /task + 3개 인텐트 비동기화 | **핵심** |
| `frontend/src/go100/types/ai.ts` | `TaskStatusResponse`, `task_id` 필드 | 소규모 |
| `frontend/src/go100/api/go100Api.ts` | `getTaskStatus()` + import | 소규모 |
| `frontend/src/go100/components/AIProgressIndicator.tsx` | `stage`/`stageDetail` prop, 서버 단계 매핑 | 중간 |
| `frontend/src/go100/components/ChatWidget.tsx` | 폴링 로직 + AIProgressIndicator 적용 | **핵심** |
| `frontend/src/go100/components/ChatInterface.tsx` | 동일 폴링 로직 | **핵심** |
| `frontend/src/components/admin/backtest/GoalTracking.tsx` | 빌드 오류 수정 | 부수 |
| `frontend/src/components/market/StockChart.tsx` | 빌드 오류 수정 | 부수 |
| `backend/app/routers/bt_chart.py` | 문법 오류 수정 | 부수 |
| `frontend/src/lib/api/backtest-chart.ts` | 타입 통일 | 부수 |

## 7. 검증

### 7.1 동기 인텐트 (help)

```
POST /chat → status: "completed", task_id: 없음
Reply: "안녕하세요! 백억이입니다. GO100 사용법이 궁금하시군요..."
```

### 7.2 비동기 인텐트 (strategy)

```
POST /chat → status: "processing", task_id: "6e3e1f96"
[0s]  GET /task → processing, stage=designing
[2s]  GET /task → processing, stage=designing
...
[10s] GET /task → status=needs_clarification, reply="볼린저밴드를 활용한..."
```

### 7.3 백엔드 태스크 라이프사이클 로그

```
bg_strategy task=6e3e1f96 started
bg_strategy task=6e3e1f96 calling orchestrator
Task 6e3e1f96 completed, result stored
bg_strategy task=6e3e1f96 completed successfully
```

## 보고 요약

- **Cloudflare 524 타임아웃 해결**: 장시간 작업을 백그라운드 asyncio Task로 실행, 즉시 task_id 반환
- **실시간 진행 표시**: 2초 간격 폴링으로 서버 단계 → AIProgressIndicator 반영
- **3개 인텐트 비동기화**: strategy, goal_setup 2턴, optimize_existing
- **멀티 워커 호환**: JSON 파일 기반 태스크 트래킹 (`/tmp/go100_tasks/`)
- **E2E 검증**: 동기(help) + 비동기(strategy) 모두 정상 동작 확인
