# 백억이(Baekeogi) AI 기술 명세서
> 최종 업데이트: 2026-02-24 | 문서 버전: v1.0
> 위치: go100/docs/BAEKEOGI-TECH-SPEC.md

---

## 1. 개요

### 1-1. 백억이란?
- GO100 서비스의 AI 투자 어시스턴트
- 사용자와 자연어 대화로 주식 투자 전략을 설계·평가·최적화
- 전략카드(go100_strategy_cards) 생성부터 백테스트 최적화까지 자동화

### 1-2. 핵심 능력
- 투자 의도 파악 (이해 에이전트)
- 전략 설계 (설계 에이전트)
- 전략 평가 (평가 에이전트)
- 전략 최적화 (최적화 에이전트 + 백테스트 옵티마이저)

---

## 2. 아키텍처

### 2-1. 전체 흐름도
```
사용자 메시지
    │
    ▼ [ChatWidget.tsx / ChatInterface.tsx]
    │
    ▼ POST /api/go100/ai/chat
    │
    ▼ [ai_router.py]
    │
    ▼ [intent_router.route_intent] ← 의도 분류 (help | optimize_existing | strategy)
    │
    ├─ "help" (사용법/화면 질문) → [help_flow.py] → 도움말 응답
    │
    ├─ "optimize_existing" (이 전략 최적화해줘) → [BacktestOptimizer]
    │       │
    │       │ 백테스트 → LLM(gpt-4o) 분석 → 파라미터 조정 → 새 카드 생성 루프 (최대 5회)
    │       ▼
    │       go100_optimization_runs INSERT/UPDATE
    │
    ├─ "strategy" (새 전략 만들어줘) → [BaseOrchestrator]
    │       │
    │       ┌───────┼───────┐
    │       ▼       ▼       ▼
    │   [Understand] [Design] [Evaluate] (+ BACKTEST → OPTIMIZE 루프 ≤5회)
    │       │       │       │
    │       └───────┼───────┘
    │               ▼
    │       go100_strategy_cards INSERT → BACKTESTED 확정
    │
    └─ 일반 대화 → [BaseOrchestrator] → UNDERSTAND → DESIGN → (DB 없으면 DESIGN만) → call_reply
```

### 2-2. 파일 구조
| 파일 | 라인수 | 역할 |
|------|--------|------|
| base_orchestrator.py | 781 | 메인 오케스트레이터 (UNDERSTAND→DESIGN→BACKTEST→EVALUATE→OPTIMIZE 루프, 카드 저장) |
| prompts.py | 328 | 프롬프트 템플릿 (UNDERSTAND/DESIGN/EVALUATE/OPTIMIZE/REPLY, Universe/AdvancedFilters/분할익절 스펙) |
| llm_client.py | 212 | LLM API 래퍼 (LLMGateway 사용, call_understand/call_design/call_reply) |
| optimize_agent.py | 203 | 전략 최적화 에이전트 (EvaluationResult → 파라미터 조정, 안전 규칙 강제) |
| design_agent.py | 176 | 전략 설계 에이전트 (UserIntent → StrategyDesign, 안전 규칙 적용) |
| evaluate_agent.py | 151 | 전략 평가 에이전트 (백테스트 결과 → EvaluationResult, LLM 해석) |
| understand_agent.py | 140 | 사용자 의도 파악 (자연어 → UserIntent) |
| schemas.py | 132 | Pydantic 스키마 (UserIntent, StrategyDesign, EvaluationResult, OptimizationRecord 등) |
| intent_router.py | 73 | 의도 분류기 (help / optimize_existing / strategy, 키워드+패턴) |
| backtest_optimizer.py | 555 | 백테스트 기반 자동 최적화 루프 (원본 카드→백테스트→LLM 분석→새 카드 생성) |

---

## 3. 에이전트 상세

### 3-1. Intent Router (의도 분류)
- **입력:** 사용자 메시지 텍스트
- **분류 카테고리:** `help` | `optimize_existing` | `strategy`
- **분류 방법:** 키워드 기반 (OPTIMIZE_EXISTING_KEYWORDS, HELP_KEYWORDS, HELP_PATTERN). 애매하면 `strategy` 유지.
- **출력:** intent 문자열 (`route_intent(user_message)`)

### 3-2. Understand Agent (이해 에이전트)
- **역할:** 사용자 자연어 → 구조화된 UserIntent (투자 스타일, 위험허용도, 관심 섹터/키워드 등)
- **입력:** user_message, conversation_history (list)
- **처리:** LLM 호출 (FREE_CHAT, UNDERSTAND_SYSTEM_PROMPT) → JSON 추출 → _validate_intent (enum 정규화, 기술용어 시 experience_level 상향). confidence &lt; 0.6 또는 unknown 3개 이상이면 needs_clarification=True
- **출력:** UserIntent (Pydantic)
- **사용 프롬프트:** UNDERSTAND_SYSTEM_PROMPT (prompts.py)

### 3-3. Design Agent (설계 에이전트)
- **역할:** UserIntent → 완전한 StrategyDesign (전략 카드 JSON)
- **입력:** UserIntent, user_message
- **처리:** call_design(intent_dict, user_message) → _apply_safety_rules (stop_loss 보장, max_stocks/max_position_pct 범위, beginner 시 market_cap_rank≤100 강제)
- **출력:** go100_strategy_cards에 저장되는 필드들
  - **strategy_type:** scalping | daily | swing (risk_params.strategy_type 또는 intent/ max_holding_days 유추)
  - **universe_filter:** type "AND"|"OR", conditions (scope, market_cap, ma, rsi 등), AdvancedFilters 스펙 지원
  - **entry_rules:** ma_cross, rsi_threshold, price_breakout, volume_surge 등 리스트
  - **exit_rules:** profit_target, stop_loss, trailing_stop, holding_days 등 리스트 (OR)
  - **risk_params:** max_stocks, max_position_pct, stop_loss_pct, partial_exit(분할익절), strategy_type, bar_interval 등
  - **strategy_params:** (설계 출력에 포함 가능)
- **사용 프롬프트:** DESIGN_SYSTEM_PROMPT (UniverseEngine/AdvancedFilters/분할익절/entry_exit 스펙 포함)

### 3-4. Evaluate Agent (평가 에이전트)
- **역할:** 백테스트 결과(dict) + 위험허용도 → EvaluationResult (4개 메트릭 중 3개 이상 통과 시 passed)
- **입력:** backtest_result (total_return, max_drawdown, win_rate, sharpe_ratio), risk_tolerance
- **처리:** 위험허용도별 임계값(THRESHOLDS) 비교 → 0~100점 계산 → LLM 호출(LLMGateway, EVALUATE_SYSTEM_PROMPT)로 strengths/weaknesses/improvement_suggestions/summary 생성 (실패 시 규칙 기반 폴백)
- **출력:** EvaluationResult (passed, score, metrics, strengths, weaknesses, improvement_suggestions, summary)
- **사용 프롬프트:** EVALUATE_SYSTEM_PROMPT (prompts.py)

### 3-5. Optimize Agent (최적화 에이전트)
- **역할:** EvaluationResult 기반 전략 파라미터 안전 범위 내 최적화 (한 번에 최대 3개 파라미터, stop_loss 제거 불가)
- **입력:** strategy (dict), evaluation (EvaluationResult), risk_tolerance, iteration, previous_records
- **처리:** LLM 호출(OPTIMIZE_SYSTEM_PROMPT) → changes_made/optimized_strategy 파싱 → _enforce_safety (max_stocks 3~10, max_position_pct≤30%, stop_loss 복원)
- **출력:** OptimizationRecord (iteration, changes_made, optimized_strategy, expected_improvement)
- **사용 프롬프트:** OPTIMIZE_SYSTEM_PROMPT (prompts.py)

---

## 4. 오케스트레이터 (base_orchestrator.py)

### 4-1. 클래스 구조
- **클래스명:** BaseOrchestrator
- **주요 메서드:** process_message (진입점), _run_full_pipeline, _insert_draft_card, _run_backtest, _run_backtest_minute, _run_backtest_daily, _update_card_params, _finalize_card, _auto_strategy_name, _detect_strategy_type, _get_bar_interval
- **상태 관리:** 인스턴스 보유 (UnderstandAgent, DesignAgent, Go100EvaluateAgent, Go100OptimizeAgent, LLMClient). DB/ user_id는 인자로 전달.
- **대화 히스토리:** process_message 인자 conversation_history → UNDERSTAND에만 전달 (list[ConversationMessage])

### 4-2. 대화 → 전략카드 생성 플로우
1. **UNDERSTAND:** understand_agent.analyze(user_message, hist) → UserIntent. needs_clarification이면 call_reply(clarify) 후 반환.
2. **DESIGN:** design_agent.design(intent, user_message) → StrategyDesign. db=None이면 call_reply(present_design) 후 반환 (Phase 5 호환).
3. **DB 저장:** _insert_draft_card → go100_strategy_cards INSERT (DRAFT).
4. **백테스트·평가·최적화 루프 (최대 5+1회):** _run_backtest(캐시 재사용 또는 분봉 우선/일봉 폴백) → evaluate_agent.evaluate → passed면 break, 아니면 optimize_agent.optimize → _update_card_params → 반복.
5. **확정:** best_result/best_evaluation 있으면 _finalize_card (BACKTESTED, last_backtest_* 갱신, 전략명에 [스캘핑]/[데일리]/[단기스윙] 태그).
6. **응답:** call_reply(present_full_result) + "전략카드 '…'이(가) 저장되었습니다." → OrchestrationResult 반환.

### 4-3. 캐시/재사용 로직
- **24시간 백테스트 캐시 (BACKTEST-SAVE-FIX-001):** go100_backtest_runs에서 해당 card_id, status=COMPLETED, completed_at &gt; now()-24h 조건으로 최신 1건 조회 후 재사용. 없으면 분봉(AdvancedFilters+MinuteSimulator) 우선, 종목 부족 시 일봉 폴백.

---

## 5. 백테스트 옵티마이저 (backtest_optimizer.py)

### 5-1. 최적화 루프
1. **원본 카드 조회** (_get_card)
2. **반복 (1~max_iterations):**  
   - 백테스트 실행 (_run_backtest, Go100BacktestService 또는 최근 go100_backtest_runs 폴백)  
   - go100_optimization_runs INSERT (RUNNING)  
   - LLM 분석 (_analyze_with_llm, OpenAI gpt-4o, ANALYSIS_PROMPT, JSON 응답)  
   - 결과가 이전보다 나으면 best_result 갱신  
   - _update_opt_run (COMPLETED, total_return, mdd, sharpe_ratio 등)  
   - should_continue=False 또는 개선폭 미미하면 종료  
   - 새 카드 생성 (_create_optimized_card: version, parent_card_id, optimization_source='AI_BACKTEST') → 다음 반복은 새 카드로
3. **최선 반복 마킹** (_mark_best, is_best=TRUE, status=SELECTED)
4. **알림** (NotificationService, OPTIMIZE_COMPLETED)

### 5-2. API 엔드포인트
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /api/go100/optimizer/backtest-optimize | 백테스트 기반 자동 최적화 시작 (card_id, goal, max_iterations) |
| GET | /api/go100/optimizer/runs/{card_id} | 카드별 최적화 이력 (opt_run_id, iteration, total_return, mdd, status, is_best 등) |
| GET | /api/go100/optimizer/run/{opt_run_id} | 개별 최적화 실행 상세 |
| POST | /api/go100/optimizer/apply/{opt_run_id} | 최적화 결과 적용 (optimized_card_id 활성화, is_best/status 갱신) |

### 5-3. DB 테이블
- **go100_optimization_runs:** opt_run_id, original_card_id, iteration, parameters_before, parameters_after (jsonb), optimization_goal, status (RUNNING/COMPLETED/FAILED/SELECTED), user_id, change_description, llm_analysis, llm_recommendation, total_return, mdd, sharpe_ratio, win_rate, trade_count, optimized_card_id, is_best, created_at, updated_at
- **go100_strategy_cards 추가 컬럼:** version, parent_card_id, optimization_source (예: 'AI_BACKTEST')

---

## 6. 프롬프트 체계 (prompts.py)

### 6-1. 프롬프트 목록
| 프롬프트명 | 용도 | 대략적 토큰수 |
|-----------|------|-------------|
| UNDERSTAND_SYSTEM_PROMPT | 투자 의도 추출 (JSON) | ~600 |
| DESIGN_SYSTEM_PROMPT | 전략 카드 설계 (Universe/AdvancedFilters/분할익절/entry_exit 스펙 포함) | ~2500 |
| EVALUATE_SYSTEM_PROMPT | 백테스트 결과 평가 (strengths/weaknesses/suggestions/summary) | ~400 |
| OPTIMIZE_SYSTEM_PROMPT | 파라미터 최적화 (changes_made, optimized_strategy JSON) | ~350 |
| REPLY_SYSTEM_PROMPT | 사용자 응답 생성 (친근한 한국어) | ~200 |

### 6-2. 프롬프트 구조
- 공통: 시스템 메시지(system_prompt) + 사용자 메시지(JSON/컨텍스트). 응답은 JSON 블록(```json ... ```) 또는 단일 `{...}` 추출(_extract_json).
- DESIGN: UNIVERSE_FILTER_SPEC, ADVANCED_FILTER_SPEC, PARTIAL_EXIT_SPEC, ENTRY_EXIT_RULES_SPEC 삽입.

### 6-3. 시장 레짐 참조
- ADVANCED_FILTER_SPEC에 `get_market_regime` 필터 설명 포함 (index_daily, vkospi, market_investor 기반 레짐 판정). 프롬프트에서 레짐을 직접 요구하지는 않음.

---

## 7. LLM 클라이언트 (llm_client.py)

### 7-1. 지원 모델
- **llm_client.py:** LLMGateway 사용. 모델은 Gateway 라우팅에 따름.
- **실제 라우팅 (core):** FREE_CHAT → LLM_FREE_CHAT_MODEL (예: gemini-2.5-flash), DESIGN_CHAT → LLM_DESIGN_CHAT_MODEL (예: claude-sonnet-4-6). Evaluate/Optimize 단독 호출 시 LLMGateway + RequestType.FREE_CHAT 또는 DESIGN_CHAT 사용.
- **BacktestOptimizer:** OpenAI AsyncOpenAI, model="gpt-4o", response_format={"type": "json_object"}.

### 7-2. 호출 설정
- **Temperature:** UNDERSTAND/DESIGN 0.3, REPLY 0.5. Evaluate 0.3, Optimize 0.4. BacktestOptimizer 0.3.
- **Max tokens:** UNDERSTAND/DESIGN 4096, REPLY 1024. Evaluate 2048, Optimize 4096.
- **Timeout:** llm_client.py TIMEOUT_S=30 (Gateway 내부 사용).
- **재시도:** MAX_RETRIES=2, 429/500/503 시 재시도.

### 7-3. 비용 관리
- **일일 한도:** LLM_FREE_CHAT_DAILY_LIMIT=50, LLM_DESIGN_CHAT_DAILY_LIMIT=20 등 (.env).
- **.env 설정:** GOOGLE_AI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, LLM_GLOBAL_ENABLED, LLM_*_MODEL, LLM_MONTHLY_BUDGET_USD, LLM_USER_MONTHLY_WARN_USD, LLM_CIRCUIT_* 등 (키 값은 마스킹 권장).

---

## 8. 프론트엔드 연동

### 8-1. 채팅 컴포넌트
- **ChatWidget.tsx:** 플로팅 FAB + 패널 (createPortal로 body에 렌더). mode=fullscreen이면 전체화면 채팅 레이아웃. /llm 경로에서는 FAB 숨김. chatWithAI 호출, reply_to_user 또는 message로 응답 표시.
- **ChatInterface.tsx:** 위험 허용도 선택, 대화 히스토리 로컬 저장, 메시지 송수신, lastResponse에 strategy_card_id 있으면 StrategyResultCard 표시.
- **AIProgressIndicator.tsx:** UNDERSTAND→DESIGN→BACKTEST→EVALUATE→OPTIMIZE 단계별 시간 기반 진행 표시 (0/3/8/15/20/30초). done=true 시 전체 완료 체크 표시.

### 8-2. API 호출
- **chatWithAI(req):** POST `${BASE}/ai/chat`, req: message, user_id, risk_tolerance, session_id 등 → ChatResponse (reply_to_user, strategy_card_id, status 등).
- **aiUnderstand(body):** POST `${BASE}/ai/understand` (디버그).
- **aiDesign(body):** POST `${BASE}/ai/design` (디버그).
- **aiEvaluate(body):** POST `${BASE}/ai/evaluate`.
- **aiOptimize(body):** POST `${BASE}/ai/optimize`.
- **startBacktestOptimization(req):** POST `${BASE}/optimizer/backtest-optimize` (card_id, goal, max_iterations).
- **getOptimizationRuns(cardId):** GET `${BASE}/optimizer/runs/${cardId}`.
- **getOptimizationRunDetail(optRunId):** GET `${BASE}/optimizer/run/${optRunId}`.
- **applyOptimizationResult(optRunId, { activate }):** POST `${BASE}/optimizer/apply/${optRunId}`.

### 8-3. 채팅 → 전략카드 연결
- ai_router /chat 응답에 strategy_card_id(go100_card_id) 포함. ChatInterface는 lastResponse.strategy_card_id가 있으면 StrategyResultCard로 "내 전략" 확인 유도. 카드 생성 후 목록 갱신은 페이지/탭 전환 또는 "내 전략" 탭 재조회 시 반영.

---

## 9. 데이터 스키마

### 9-1. go100_optimization_runs
- **컬럼 (코드 기준):** opt_run_id, original_card_id, iteration, parameters_before (jsonb), parameters_after (jsonb), optimization_goal, status, user_id, change_description, llm_analysis, llm_recommendation, total_return, mdd, sharpe_ratio, win_rate, trade_count, optimized_card_id, is_best, created_at, updated_at.
- **상태:** RUNNING → COMPLETED/FAILED, 최선 선택 시 SELECTED, is_best=TRUE.

### 9-2. go100_strategy_cards AI 관련 컬럼
- **version:** 카드 버전 (최적화 시 v2, v3… 생성 시 증가).
- **parent_card_id:** 원본 카드 ID (최적화로 생성된 카드).
- **optimization_source:** 최적화 출처 (예: 'AI_BACKTEST').

---

## 10. 알려진 이슈 / 제한사항
- DB 직접 접속 없이 코드 기준으로 스키마 기술. 실제 DB는 서버([SERVER-IP])에서 PGPASSWORD 등으로 접속 필요.
- ChatInterface의 DEFAULT_USER_ID=1 하드코딩은 ISS-012 등에서 제거 권장(실제 auth-store user_id 사용).
- BacktestOptimizer는 OpenAI gpt-4o 고정; 다른 모델/LLMGateway 통합은 미적용.
- 24시간 백테스트 캐시 사용 시 동일 카드 파라미터 변경 후에도 캐시가 우선 사용됨.
- Phase 2 백테스트 기반 자동 최적화는 구현 완료, E2E/실서비스 검증은 추가 권장.

---

## 11. 향후 계획
- Phase 2: 백테스트 기반 자동 최적화 (구현 완료, E2E 미검증)
- Phase 3: 모의매매 결과 기반 실전 최적화
- Phase 4: 실계좌 최적화
- 5개 시간축 체계 연동 (DataGate → 최적화 전 데이터 충족 검증)

---

## 참고
- AI-BACKTEST-OPT-001 보고서: go100/reports/CUR-GO100-AI-BACKTEST-OPT-001-20260224.md
- 인계서: go100/HANDOVER-20260224-V2.md
- API 명세: go100/API_SPEC.md
- 키움증권 데이터 수집 (2026-02-25): [KIWOOM-DATA-COLLECTION-REPORT-20260225](https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/KIWOOM-DATA-COLLECTION-REPORT-20260225.md) — v4_theme_*, v4_trade_strength_history 등 신규 수집; DataGate/백테스트 반영 시 참고.
