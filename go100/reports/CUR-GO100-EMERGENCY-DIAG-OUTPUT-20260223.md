# CUR-GO100-EMERGENCY-DIAG — 진단 출력 보고서
**작성일:** 2026-02-23  
**지시서:** CUR-GO100-EMERGENCY-DIAG (진단 전용, 코드 수정 없음)

---

## PART A: 사라진 전략카드 확인 (DB)

### go100_strategy_cards 전체 (3건)
| go100_card_id | strategy_name | user_id | card_status | is_active | is_featured | is_public | featured_order | created_at |
|---------------|---------------|---------|-------------|-----------+-------------|-----------+----------------|------------|
| 13 | [스캘핑] 분봉 스캘핑 고변동 대형주 | 3 | BACKTESTED | t | t | t | 1 | 2026-02-21 21:39:20+09 |
| 14 | [데일리] 대형 우량주 수급 데일리 전략 | 3 | BACKTESTED | t | t | t | 2 | 2026-02-21 21:47:10+09 |
| 15 | [단기스윙] 섹터모멘텀 외국인수급 스윙 | 3 | BACKTESTED | **f** | t | t | 3 | 2026-02-21 21:48:21+09 |

### is_active=false 인 카드 (1건)
- **go100_card_id 15**: "[단기스윙] 섹터모멘텀 외국인수급 스윙" — `is_active=false`, `is_featured=true`

### strategy_cards (user_id 2,3,6,15) 최근 20건
| card_id | strategy_name | user_id | strategy_type | created_at |
|---------|---------------|---------|---------------|------------|
| 64 | ㅊㅊㅊ | 3 | CUSTOM | 2026-02-22 22:21:20+09 |
| 63 | 제시해주신 조건들을 바탕으로... | 3 | CUSTOM | 2026-02-22 10:59:34+09 |
| 62 | 제시해주신 조건들을 바탕으로... | 3 | CUSTOM | 2026-02-22 10:59:03+09 |
| 61 | 시초가매매 | 2 | CUSTOM | 2026-02-21 06:39:39+09 |
| 3 | # 🚀 GO100 추세 상승 극대화 전략... | 3 | CUSTOM | 2026-02-20 11:29:25+09 |
| 1 | 볼린저 밴드 돌파 | 2 | BUILTIN | 2026-02-20 00:16:59+09 |

**요약:** `go100_strategy_cards`에는 3건만 존재. 카드 15는 `is_active=false`라 목록에서 제외될 수 있음. `strategy_cards`는 레거시/다른 플로우용으로 GO100과 별도.

---

## PART B: 백억이 전략저장 500 에러 원인

### B-1. 최근 go100 서비스 에러 로그 (핵심)

**원인:** `NameError: name 'get_effective_uid' is not defined`

- **발생 위치:** `backend/app/routers/go100/strategy_router.py` **line 127**, `toggle_card_active`
- **호출:** `effective_uid = await get_effective_uid(db, current_user["user_id"])`
- **상황:** `strategy_router.py`에서 `get_effective_uid`를 사용하지만 **import 하지 않음**.  
  `card_service.py`에는 `from backend.app.services.go100.user_utils import get_effective_uid` 있음.

추가로 **`text`** 도 사용(라인 128 `db.execute(text("""...`))하지만 `from sqlalchemy import text` 없음.

### B-2. 로그 요약
- `POST /api/go100/strategy-cards` → **500** (05:39:19)
- `PATCH /api/go100/strategy-cards/13/toggle` → **500** (05:40:32~35, 여러 번) — 위 NameError와 동일 스택
- `GET /api/v1/strategy-cards/catalog` → 200
- `GET /api/v1/strategy-cards/for-backtest` → 200

**POST 500:** create_card는 라우터에서 `go100_strategy_card_service.create_card()`만 호출하며, `card_service`는 `get_effective_uid`를 import하고 있어서, POST 500이 동일 원인인지는 로그만으로 불명. **toggle 500은 `get_effective_uid`(및 `text`) 미 import로 확실.**

### B-3. uvicorn 최근 로그
- 정상 요청(200) 및 SQL 로그 다수. 에러 구간은 위 Traceback과 일치.

---

## PART C: 프론트 전략 저장 호출

### C-1. StrategyCardSaveButton
- **파일:** `frontend/src/components/chat/StrategyCardSaveButton.tsx`
- **저장 API:** `createStrategyCard(body)` → `@/go100/api/go100Api`의 `createStrategyCard`
- **실제 요청:** `POST ${BASE}/strategy-cards` (BASE = `/api/go100` 또는 `NEXT_PUBLIC_GO100_API_URL/api/go100`)
- **결과:** **POST /api/go100/strategy-cards** 로 전략카드 생성 요청.

### C-2. /llm 페이지
- **파일:** `frontend/src/app/(protected)/llm/page.tsx`
- `ChatMessage`에 `accounts={accounts}` 전달. 전략 저장 버튼은 `ChatMessage` 내부에서 `StrategyCardSaveButton` 사용으로 추정 (채널/설계 응답 연동).

### C-3. go100Api.ts
- `createStrategyCard`: `go100Client.post(\`${BASE}/strategy-cards\`, data)` → **POST /api/go100/strategy-cards**
- `toggleStrategyCardActive`: `go100Client.patch(\`${BASE}/strategy-cards/${cardId}/toggle\`)` → **PATCH /api/go100/strategy-cards/:id/toggle**

### C-4. strategy-cards.ts (v1 API)
- `getCatalog(tab)`: `GET /api/v1/strategy-cards/catalog?tab=...`
- `createCard`: `POST /api/v1/strategy-cards` (레거시/일반 카드용. GO100 저장은 go100Api 사용)

---

## PART D: 백엔드 전략 저장 코드

### D-1. strategy_router.py
- **prefix:** `/api/go100/strategy-cards`
- **POST ""** → `create_card` → `go100_strategy_card_service.create_card(current_user["user_id"], data, db)`
- **PATCH "/{card_id}/toggle"** → `toggle_card_active` → **`get_effective_uid` 호출하나 import 없음**, `text()` 사용하나 `sqlalchemy.text` import 없음.

### D-2. card_service.py
- `create_card`: `get_effective_uid(db, user_id)` 사용, **user_utils에서 import 함.** INSERT 후 `_row_to_response` 반환.

### D-3. schemas.py
- `Go100StrategyCardCreate`, `Go100StrategyCardUpdate`, `Go100StrategyCardResponse` 등 정의. `entry_rules`/`exit_rules` 등 list|dict 허용.

### D-4. base_orchestrator.py
- `_insert_draft_card`에서 `get_effective_uid(db, user_id)` 사용, **user_utils import 있음.**  
  DESIGN → DRAFT INSERT → 백테스트 → BACKTESTED 정리 플로우.

### D-5. ai/schemas.py
- `OrchestrationResult`에 `strategy_card_id`, `go100_card_id` 포함.

---

## PART E: 채팅 위젯이 안 보이는 이유

### E-1. ChatWidget.tsx
- **위치:** `frontend/src/go100/components/ChatWidget.tsx`
- FAB: `fixed bottom-6 right-6 z-[9999]`, 패널: `z-[9998]`, 정상 정의.

### E-2. layout.tsx
- **import:** `import { ChatWidget } from "@/go100/components/ChatWidget";`
- **렌더:** `<> ... <ChatWidget /> </>` (flex 컨테이너 밖, 최상위에서 고정)

### E-3. go100/components/index.ts
- `export { ChatWidget } from "./ChatWidget";` 존재.

### E-4. ChatWidget 참조
- `frontend/src/app/(protected)/layout.tsx` 에서만 import 및 사용.  
**결론:** 레이아웃에 포함되어 있으므로, “안 보임”은 빌드/런타임 에러, CSS 겹침, 또는 인증 후에만 렌더되는 구조(예: `!isAuthenticated` 시 null 반환) 가능성 확인 필요. 코드상 누락은 없음.

---

## PART F: 토글 API

### F-1. strategy_router.py
- **PATCH "/{card_id}/toggle"** 존재 (라인 120–141).
- `is_active = NOT is_active` 로 토글, `get_effective_uid`/`text` 미 import 로 500 발생.

### F-2. 프론트
- `strategy-cards/page.tsx`: `toggleStrategyCardActive`(go100Api) import, `toggleGo100Mutation`으로 `PATCH .../toggle` 호출.
- `go100Api.ts`: `toggleStrategyCardActive(cardId)` → `patch(\`${BASE}/strategy-cards/${cardId}/toggle\`)`.

---

## PART G: 전략카드 목록 API 실제 응답

- **GET /api/v1/strategy-cards/catalog?tab=all** → `401 Not authenticated`
- **GET /api/go100/strategy-cards** → `401 Not authenticated`
- **GET /api/v1/strategy-cards/for-backtest** → `401 Not authenticated`

(인증 헤더 없이 호출하여 401. 엔드포인트는 존재.)

---

## PART H: 라우트 등록

### main.py
- `from backend.app.routers.go100.strategy_router import router as go100_strategy_router, store_router as go100_store_router`
- `app.include_router(go100_strategy_router)` (라인 386)
- `app.include_router(go100_store_router)` (라인 387)
- prefix는 라우터 자체에 `prefix="/api/go100/strategy-cards"` 로 정의됨.

### strategy_router.py
- `router = APIRouter(prefix="/api/go100/strategy-cards", tags=["GO100 Strategy Cards"])`

---

## PART I: user_utils.py

- **get_effective_uid(db, jwt_user_id):**  
  JWT의 user_id가 v4_users.user_id면 그대로, legacy users.id면 email로 v4_users.user_id 조회해 반환.
- **get_user_email(db, user_id):** v4_users/legacy users에서 email 조회.

---

## ★ 종합 결론 (수정 권고 사항, 진단만 기술)

1. **500 원인 (toggle 및 가능하면 POST):**  
   `backend/app/routers/go100/strategy_router.py`에서  
   - `get_effective_uid` 사용 but **미 import**  
   - `text()` 사용 but **`from sqlalchemy import text` 미 import**  
   → **추가 권고:**  
   - `from backend.app.services.go100.user_utils import get_effective_uid`  
   - `from sqlalchemy import text`  
   (실제 코드 변경은 지시서에 따라 수행하지 않았음.)

2. **전략카드 “사라짐”:**  
   - `go100_strategy_cards` 3건 유지.  
   - 카드 15는 `is_active=false` → `is_active = true` 필터 사용 시 목록에서 제외됨.

3. **채팅 위젯:**  
   - layout에 ChatWidget 포함·export 정상.  
   - 안 보일 경우 빌드/콘솔 에러, z-index/레이아웃, 인증 조건 확인 필요.

4. **토글 API:**  
   - 엔드포인트·프론트 호출 일치.  
   - 백엔드에서 `get_effective_uid`/`text` import 추가 시 500 해소 예상.

---

*이 문서는 진단 전용 출력을 정리한 것이며, 코드 수정은 수행하지 않았습니다.*
