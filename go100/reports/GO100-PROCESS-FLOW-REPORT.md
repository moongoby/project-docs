# 백억이(GO100) 프로세스 흐름 보고서

**작성일:** 2026-02-24  
**범위:** 사용자 대화 입력 → AI 파이프라인 → 전략카드 저장 → 백테스트/평가/최적화 → 응답 반환

---

## 1. 전체 흐름 개요

```
[사용자] → [프론트 채팅] → POST /api/go100/ai/chat → [BaseOrchestrator]
    → UNDERSTAND → (추가질문?) → DESIGN → [DB 연결 시] 전체 파이프라인
    → DRAFT 카드 INSERT → BACKTEST → EVALUATE → (OPTIMIZE 루프 ≤5회)
    → 카드 BACKTESTED 확정 → REPLY 생성 → [사용자]
```

| 단계 | 설명 | 담당 모듈 |
|------|------|-----------|
| 진입 | 사용자가 채팅 메시지 전송 | ChatWidget / ChatInterface |
| API | `POST /api/go100/ai/chat` (JWT 필수) | ai_router.py |
| 오케스트레이션 | 메시지당 1회 `process_message()` | BaseOrchestrator |
| UNDERSTAND | 자연어 → UserIntent (12개 필드) | UnderstandAgent |
| DESIGN | UserIntent → StrategyDesign (진입/청산/리스크 등) | DesignAgent |
| DB 없음 | DESIGN까지만 반환 (Phase 5 호환) | BaseOrchestrator |
| DB 있음 | DRAFT 카드 저장 → 백테스트 → 평가 → 최적화 루프 → BACKTESTED 확정 | BaseOrchestrator |

---

## 2. 프론트엔드 → 백엔드 진입

### 2.1 채팅 진입점

| 위치 | 용도 |
|------|------|
| `frontend/src/go100/components/ChatWidget.tsx` | 우측 하단 FAB → 패널 (백억이 위젯) |
| `frontend/src/app/(protected)/.../llm` (전체화면) | ChatInterface 기반 전체화면 채팅 |

### 2.2 API 호출

- **함수:** `chatWithAI(req)` (`frontend/src/go100/api/go100Api.ts`)
- **URL:** `POST ${BASE}/ai/chat` → `/api/go100/ai/chat` (브라우저) 또는 `http://localhost:8002/api/go100/ai/chat` (SSR)
- **Body:** `{ message, user_id?, risk_tolerance?, conversation_history?, session_id? }`
- **인증:** `Authorization: Bearer <token>` (go100Client 인터셉터)

### 2.3 라우터 수신

- **파일:** `backend/app/routers/go100/ai_router.py`
- **엔드포인트:** `POST /api/go100/ai/chat`
- **동작:** `get_current_user`로 JWT 검증 → `get_orchestrator().process_message(user_id, message, conversation_history, db, risk_tolerance)` 호출

---

## 3. 오케스트레이터 단일 메시지 처리 (process_message)

**파일:** `backend/app/services/go100/ai/base_orchestrator.py`

### 3.1 단계 1: UNDERSTAND

```
conversation_history + user_message → UnderstandAgent.analyze()
→ UserIntent (investment_style, risk_tolerance, target_sectors, target_keywords,
   target_return_pct, holding_period, capital_hint, dividend_preference,
   specific_conditions, exclude_conditions, experience_level,
   confidence, needs_clarification, clarification_questions)
```

- **LLM:** `LLMClient.call_understand()` → **RequestType.FREE_CHAT** → 기본 `gemini-2.5-flash` (Google)
- **검증:** `confidence < 0.6` 또는 unknown 필드 3개 이상 → `needs_clarification = True`

### 3.2 단계 2: 추가 정보 필요 시 (needs_clarification)

```
LLMClient.call_reply({ action: "clarify", intent, questions })
→ OrchestrationResult(agent_name="UNDERSTAND", reply_to_user=..., needs_more_info=True, status="needs_clarification")
→ 즉시 반환 (DESIGN 미실행)
```

### 3.3 단계 3: DESIGN

```
UserIntent + user_message → DesignAgent.design()
→ StrategyDesign (universe_filter, entry_rules, exit_rules, risk_params, strategy_params, strategy_name 등)
```

- **안전 규칙:** stop_loss 없으면 스타일별 기본값 추가, max_stocks 3~10, max_position_pct ≤ 30%, beginner 시 시총 상위 100 제한 등
- **LLM:** `LLMClient.call_design()` → **RequestType.DESIGN_CHAT** → 기본 `claude-sonnet-4-6` (Anthropic)

### 3.4 단계 4: DB 없을 때 (Phase 5 호환)

```
db is None:
  → call_reply({ action: "present_design", intent, design })
  → BaseAgentResponse(agent_name="DESIGN", reply_to_user=..., strategy_design=design, needs_more_info=False)
  → 반환 (카드 저장·백테스트 없음)
```

### 3.5 단계 5: 전체 파이프라인 (db 있음) — _run_full_pipeline

1. **5-a. DRAFT 카드 INSERT**
   - `_insert_draft_card(user_id, design_dict, db)`
   - `get_effective_uid(db, user_id)` 로 레거시 user_id → v4_users.user_id 변환
   - `go100_strategy_cards` INSERT: strategy_name, universe_filter, entry_rules, exit_rules, risk_params, max_stocks, card_status='DRAFT', source_type='LLM'
   - 실패 시 DESIGN만 반환하고 종료

2. **5-b. BACKTEST → EVALUATE → OPTIMIZE 루프 (최대 5회 + 1)**

   - **백테스트:** `_run_backtest(card_id, current_strategy, db, user_id, intent)`
     - 전략 유형 판별: scalping / daily / swing
     - `AdvancedFilters.build_universe()` → 분봉 보유 종목 필터 → **분봉 백테스트 우선** (Go100MinuteSimulator), 종목 부족 시 **일봉 폴백** (UniverseEngine + 시그널 평가 + 시뮬레이션)
     - 결과: total_return, max_drawdown, sharpe_ratio, total_trades 등
   - **평가:** `Go100EvaluateAgent.evaluate(bt_result, risk_tolerance)` → passed, score 등
   - **최선 결과 유지:** score가 기존보다 높으면 best_result / best_evaluation 갱신
   - **passed면 루프 종료**
   - **미통과 시:** `Go100OptimizeAgent.optimize(strategy, evaluation, ...)` → optimized_strategy → `_update_card_params(card_id, current_strategy, db)` 로 카드 파라미터 갱신 후 다음 루프

3. **5-c. 카드 BACKTESTED 확정**
   - `_finalize_card(card_id, best_result, best_evaluation, db, strategy_type)`
   - `go100_strategy_cards` UPDATE: card_status='BACKTESTED', last_backtest_id, last_backtest_return, last_backtest_mdd, last_backtest_sharpe, last_backtest_at, strategy_name 앞에 [스캘핑]/[데일리]/[단기스윙] 태그 부여

4. **5-d. 사용자 응답 생성**
   - `call_reply({ action: "present_full_result", intent, design, passed, score, optimization_loops, warning })`
   - 메시지 끝에 "전략카드 'xxx'이(가) 저장되었습니다. 내 전략 탭에서 확인하세요." 추가
   - `OrchestrationResult(agent_name="ORCHESTRATOR", reply_to_user=..., strategy_card_id=card_id, go100_card_id=card_id, backtest_result, evaluation, optimization_history)` 반환

---

## 4. 전략 카드 라이프사이클 (card_status)

```
IDEA → DRAFT → BACKTESTED → PAPER_LIVE → LIVE
                ↑              ↓    ↓
                └────────────── PAUSED → RETIRED
```

| 상태 | 의미 |
|------|------|
| IDEA | AI 대화 중, 전략 미확정 |
| DRAFT | 전략 설계 완료, 백테스트 미실행(또는 실패) |
| BACKTESTED | 백테스트 완료, last_backtest_* 갱신됨 |
| PAPER_LIVE | 모의 실행 중 (Phase 7 예정) |
| LIVE | 실매매 실행 중 (Phase 8 예정) |
| PAUSED | 일시 정지 |
| RETIRED | 폐기 |

백억이 파이프라인에서는 **DRAFT 생성 → (백테스트/평가/최적화) → BACKTESTED** 까지만 수행된다.

---

## 5. AI 에이전트 및 LLM 사용처

| 에이전트 | 입력 | 출력 | RequestType | 기본 모델 |
|----------|------|------|-------------|-----------|
| UnderstandAgent | user_message, conversation_history | UserIntent | FREE_CHAT | gemini-2.5-flash (Google) |
| DesignAgent | UserIntent, user_message | StrategyDesign | DESIGN_CHAT | claude-sonnet-4-6 (Anthropic) |
| LLMClient.call_reply | clarify / present_design / present_full_result | 자연어 문장 | FREE_CHAT | gemini-2.5-flash (Google) |
| Go100EvaluateAgent | backtest_result, risk_tolerance | EvaluationResult (strengths/weaknesses/summary 등) | FREE_CHAT | gemini-2.5-flash (Google) |
| Go100OptimizeAgent | strategy, evaluation, ... | OptimizationRecord (optimized_strategy) | DESIGN_CHAT | claude-sonnet-4-6 (Anthropic) |

---

## 6. 흐름별 LLM 사용 모델 (자연어 대화 → 전략 생성 → 백테스트 → 최적화)

백억이 대화 흐름에서 **자연어 대화 · 전략 생성 · 백테스트 · 최적화** 각 단계별로 사용하는 LLM 모델을 정리한다.  
라우팅은 `backend/app/core/llm_gateway.py`의 `RequestType` → `RouteConfig` 및 환경 변수로 결정된다.

### 6.1 요약 표

| 흐름 단계 | 용도 | RequestType | 기본 모델 (env 미설정 시) | 벤더 | 비고 |
|-----------|------|-------------|---------------------------|------|------|
| **자연어 대화** | 사용자 의도 추출 (UNDERSTAND) | FREE_CHAT | gemini-2.5-flash | Google | 대화 히스토리 + 현재 메시지 → UserIntent JSON |
| **자연어 대화** | 추가 질문 요청 (clarify) | FREE_CHAT | gemini-2.5-flash | Google | needs_clarification 시 사용자용 문장 생성 |
| **전략 생성** | 전략 설계 (DESIGN) | DESIGN_CHAT | claude-sonnet-4-6 | Anthropic | UserIntent → StrategyDesign JSON |
| **자연어 대화** | 설계/결과 안내 (present_design, present_full_result) | FREE_CHAT | gemini-2.5-flash | Google | 사용자에게 보여줄 친근한 한국어 응답 |
| **백테스트** | 시뮬레이션 자체 | — | **LLM 미사용** | — | UniverseEngine + MinuteSimulator/일봉 시뮬레이터 (규칙/수치 연산) |
| **백테스트 후** | 결과 해석 (EVALUATE) | FREE_CHAT | gemini-2.5-flash | Google | 통과 여부는 규칙 기반; LLM은 strengths/weaknesses/summary/improvement_suggestions 생성 |
| **최적화** | 파라미터 최적화 (OPTIMIZE) | DESIGN_CHAT | claude-sonnet-4-6 | Anthropic | 평가 결과 기반 전략 JSON 수정 제안 (안전 규칙으로 후처리) |

### 6.2 RequestType별 라우팅 (llm_gateway.py 기준)

| RequestType | 환경 변수 | 기본값 | 페일오버 체인 |
|-------------|-----------|--------|----------------|
| FREE_CHAT | LLM_FREE_CHAT_MODEL | gemini-2.5-flash | (google, gemini-2.5-flash) → (anthropic, claude-haiku-4-5) |
| DESIGN_CHAT | LLM_DESIGN_CHAT_MODEL | claude-sonnet-4-6 | (anthropic, claude-sonnet-4-6) → (anthropic, claude-sonnet-4-5) |

### 6.3 단계별 코드 위치

| 단계 | 호출 위치 | RequestType |
|------|-----------|-------------|
| UNDERSTAND | `llm_client.py` → `call_understand()` | FREE_CHAT |
| DESIGN | `llm_client.py` → `call_design()` | DESIGN_CHAT |
| REPLY (clarify / present_design / present_full_result) | `llm_client.py` → `call_reply()` | FREE_CHAT |
| EVALUATE (LLM 해석) | `evaluate_agent.py` → `_call_llm()` | FREE_CHAT |
| OPTIMIZE | `optimize_agent.py` → `_call_llm()` | DESIGN_CHAT |

### 6.4 백테스트에 LLM이 쓰이지 않는 이유

백테스트는 **UniverseEngine**(종목 필터) + **Go100MinuteSimulator** 또는 일봉 시뮬레이터로 **과거 OHLCV 데이터와 규칙(진입/청산)**만으로 실행된다.  
수익률·MDD·샤프·승률 등은 전부 수치 연산이므로 이 단계에서는 **LLM을 호출하지 않는다.**  
LLM은 그 **결과를 해석**하는 EVALUATE 단계에서만 사용된다.

---

## 7. 백테스트 데이터 흐름

1. **유니버스:** AdvancedFilters.build_universe(strategy_type, ref_date) → 종목 리스트  
2. **분봉:** 분봉 데이터 보유 종목만 필터 → Go100MinuteSimulator.run_backtest(universe_codes, strategy_config, start/end, bar_interval)  
3. **일봉 폴백:** UniverseEngine + ohlcv_daily → SignalEvaluator + 수수료/세금 계산 → 성과 지표  
4. **결과:** total_return, max_drawdown, sharpe_ratio, total_trades 등 dict → EVALUATE → (미통과 시) OPTIMIZE → 카드 파라미터 갱신 후 재백테스트

---

## 8. 참조 파일 요약

| 구분 | 파일 |
|------|------|
| API 진입 | `backend/app/routers/go100/ai_router.py` |
| 오케스트레이션 | `backend/app/services/go100/ai/base_orchestrator.py` |
| UNDERSTAND | `backend/app/services/go100/ai/understand_agent.py` |
| DESIGN | `backend/app/services/go100/ai/design_agent.py` |
| LLM 래퍼 | `backend/app/services/go100/ai/llm_client.py` |
| 프론트 채팅 | `frontend/src/go100/components/ChatWidget.tsx`, `ChatInterface.tsx` |
| 프론트 API | `frontend/src/go100/api/go100Api.ts` (chatWithAI) |
| 아키텍처 문서 | `docs/go100-architecture-v1.1.md` |

---

*이 보고서는 코드 기준으로 백억이(GO100)의 프로세스 흐름을 기술한 것입니다.*
