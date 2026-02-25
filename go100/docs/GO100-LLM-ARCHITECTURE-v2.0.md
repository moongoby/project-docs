# GO100 백억이 LLM 아키텍처 기술서 v2.0

**문서 ID**: GO100-LLM-ARCHITECTURE-v2.0  
**작성일**: 2026-02-25  
**작성자**: Claude Opus 4.6 (CEO 지시)  
**상태**: CONFIRMED  
**저장 경로**: `/root/project-docs/go100/docs/GO100-LLM-ARCHITECTURE-v2.0.md`  
**참조 문서**: OPUS-LLM-AI-v1-FULL-SPEC.md, BAEKEOGI-TECH-SPEC.md, HANDOVER-20260225-V4.md

---

## 1. 개요

GO100 백억이(Baekeogi)는 3-Tier 멀티-LLM 지능형 라우팅 아키텍처를 채택하고 있습니다. 단일 모델에 의존하지 않고, 작업의 성격에 따라 최적의 LLM을 자동 배분하는 구조로, 2026년 2월 기준 업계 최선 사례(Multi-LLM Orchestration)에 정확히 부합합니다.

핵심 설계 철학은 "비용은 낮추고, 품질은 올리고, 장애에 강하게"입니다.

---

## 2. 3-Tier LLM 아키텍처

### Tier 1 — 자연어 대응 (Gemini 2.5 Flash)

Tier 1은 전체 호출량의 약 70~80%를 처리하는 기본 엔진입니다. Google Gemini 2.5 Flash를 사용하며, 입력 $0.30/MTok, 출력 $2.50/MTok으로 현존 주요 모델 중 최저가 수준입니다. 1M 토큰 컨텍스트 윈도우를 지원하고, 응답 속도가 빠릅니다.

담당 업무는 일상 대화(free_chat), 인사·환영 메시지, 종목 스크리닝 키워드 분류, 일일 시장 브리핑(Proactive Report, 크론 08:30 KST), CS 대응(Phase 2), 간단한 질문 응답입니다.

LLMGateway 설정은 request_type이 "free_chat"일 때 vendor는 "google", model은 env("LLM_FREE_CHAT_MODEL", "gemini-2.5-flash"), max_tokens는 2048, temperature는 0.7, timeout_s는 10, cache_enabled는 False입니다.

선정 근거는 세 가지입니다. 첫째, LMArena Elo에서 Gemini 계열이 인간 선호도 최상위권(2.5 Pro Elo 1452)을 기록하고 있어 대화 품질이 우수합니다. 둘째, $0.30/$2.50 가격으로 대량 호출을 감당할 수 있습니다. 셋째, 한국어 자연어 처리 품질이 검증되어 있습니다.

### Tier 2 — 전략 수립 (Claude Sonnet 4.6)

Tier 2는 전체 호출량의 약 15~25%를 담당하는 전략 엔진입니다. Anthropic Claude Sonnet 4.6을 사용하며, 입력 $3.00/MTok, 출력 $15.00/MTok입니다. SWE-bench Verified 70.6%로 코딩·구조화 출력 분야 세계 1위 모델입니다.

담당 업무는 전략 설계(design_chat) — UnderstandAgent → DesignAgent 파이프라인, Goal Pipeline(goal_setup) — 목표 분석 → 시나리오 3개 생성 → 전략 자동 설계, 전략 평가(EvaluateAgent) — 백테스트 결과 해석, 전략 최적화(OptimizeAgent) — 파라미터 조정, C2SC 파싱 보조(폴백 시)입니다.

LLMGateway 설정은 request_type이 "design_chat"일 때 vendor는 "anthropic", model은 env("LLM_DESIGN_CHAT_MODEL", "claude-sonnet-4-6"), max_tokens는 4096, temperature는 0.3, timeout_s는 30, cache_enabled는 True입니다.

선정 근거는 세 가지입니다. 첫째, JSON 구조화 출력의 정확도가 최상급이라 전략카드 JSON 생성에 최적입니다. 둘째, Anthropic 프롬프트 캐싱(cache_control)을 적용하여 시스템 프롬프트(약 2,500토큰) 비용을 90% 절감합니다. 셋째, 1M 토큰 컨텍스트로 복잡한 대화 히스토리를 유지할 수 있습니다.

### Tier 3 — 검증 (Claude Opus 4.6)

Tier 3는 전체 호출량의 약 3~5%만 처리하는 최종 검증 엔진입니다. Anthropic Claude Opus 4.6을 사용하며, 입력 $5.00/MTok, 출력 $25.00/MTok으로 비용이 높지만 최고 수준의 추론 능력을 제공합니다.

담당 업무는 전략 검증(strategy_review) — 전략카드 논리 완결성·위험 요소 심층 분석, 매매 실행 전 최종 안전 검증(Phase 3~4), 레짐 전환 판단 검증, 포트폴리오 리밸런싱 최종 승인입니다.

LLMGateway 설정은 request_type이 "strategy_review"일 때 vendor는 "anthropic", model은 env("LLM_STRATEGY_REVIEW_MODEL", "claude-opus-4-6"), max_tokens는 8192, temperature는 0.2, timeout_s는 60, cache_enabled는 True입니다.

선정 근거는 세 가지입니다. 첫째, Constitutional AI 기반 안전성이 최고 수준이라 투자 규제 준수(투자 권유 금지)에 가장 적합합니다. 둘째, Anthropic 배치 API 적용 시 비용 50% 절감이 가능합니다(배치 처리 1~2분 허용). 셋째, 오류 비용이 큰 작업(실제 매매 검증)에만 사용하여 비용 효율을 극대화합니다.

### 보조 — C2SC 파싱 (GPT-4.1 mini)

전략 대화를 전략카드 JSON으로 변환하는 C2SC(Conversation-to-Strategy-Card) 파싱에 OpenAI GPT-4.1 mini를 사용합니다. 입력 $0.40/MTok, 출력 $1.60/MTok이며, temperature 0.0으로 결정론적 출력을 보장합니다.

---

## 3. 전체 요청 흐름도

사용자 메시지가 ChatWidget.tsx를 통해 POST /api/go100/ai/chat으로 전달됩니다. ai_router.py에서 intent_router.route_intent()를 호출하여 의도를 분류합니다(help, optimize_existing, strategy, goal_setup, stock_info, stock_screening, market_briefing, portfolio_status, free_chat 등). 분류된 의도에 따라 해당 request_type이 LLMGateway.send()로 전달되고, Gateway 내부의 라우팅 엔진이 ROUTING_TABLE을 참조하여 적절한 벤더/모델을 선택합니다.

free_chat, greeting, stock_screening(단순), market_briefing은 Tier 1(Gemini 2.5 Flash)로 라우팅됩니다. goal_setup, strategy_create, design_chat, evaluate, optimize는 Tier 2(Claude Sonnet 4.6)로 라우팅됩니다. strategy_review, trade_execute_verify는 Tier 3(Claude Opus 4.6)로 라우팅됩니다. c2sc는 GPT-4.1 mini로 라우팅됩니다.

---

## 4. 페일오버 체인

장애 시 자동으로 대체 모델로 전환되는 폴백 구조입니다. free_chat의 1차는 Gemini 2.5 Flash, 2차는 Claude Haiku 4.5입니다. design_chat의 1차는 Claude Sonnet 4.6, 2차는 Claude Sonnet 4.5입니다. c2sc의 1차는 GPT-4.1 mini, 2차는 Claude Sonnet 4.6입니다. strategy_review의 1차는 Claude Opus 4.6, 2차는 Claude Sonnet 4.6입니다.

서킷 브레이커는 벤더 단위로 관리되며, 5분 윈도우 내 3회 실패 시 OPEN → 300초 쿨다운 → HALF_OPEN(1회 테스트) → CLOSED 순서로 복구됩니다.

---

## 5. 비용 최적화 전략

Anthropic 프롬프트 캐싱이 설계대화(Sonnet 4.6)와 전략 검증(Opus 4.6)에 적용되어 있습니다. 시스템 프롬프트에 cache_control: {"type": "ephemeral"}을 설정하여, 첫 호출에서 25% 할증이 발생하지만 이후 5분 TTL 내 히트 시 입력 비용이 90% 절감됩니다. 동일 시스템 프롬프트를 사용하는 다수 사용자가 호출하면 캐시가 공유됩니다.

Anthropic 배치 API는 전략 검증(Opus 4.6) 전용으로 적용되어 전체 비용 50%가 절감됩니다. 1~2분 지연이 허용되는 심층 분석에만 사용하며, 사용자에게 "AI가 전략을 심층 검증 중입니다" 프로그레스를 표시합니다.

---

## 6. 비용 시뮬레이션 (유저 1인 월간)

Tier 1(Gemini 2.5 Flash)은 일 15회 대화, 대화당 2,000토큰 기준으로 월 입력 900K 토큰, 출력 450K 토큰이 발생하여 약 $1.40입니다. Tier 2(Claude Sonnet 4.6)는 일 3회 전략 대화, 대화당 4,000토큰 기준으로 월 입력 360K, 출력 180K로 약 $3.78입니다(캐싱 적용 시 약 $2.50). Tier 3(Claude Opus 4.6)는 월 5회 검증, 대화당 6,000토큰 기준으로 약 $0.53입니다(배치 적용 시 약 $0.27). 보조(GPT-4.1 mini)는 월 약 $0.18입니다.

합계는 약 $4.35~$5.89/월, 원화 기준 약 ₩6,000~₩8,100입니다. OPUS-LLM-AI-v1-FULL-SPEC의 100명 시뮬레이션에서는 유저당 ₩216/월(교육 위주 가벼운 사용)로 산출된 바 있으며, 실제 전략 활용이 많아지면 위 범위로 상승합니다. SaaS 구독 요금(Basic ₩9,900, Pro ₩29,900) 대비 충분한 마진이 확보됩니다.

---

## 7. 2026년 2월 기준 모델 시장 위치

Gemini 2.5 Flash는 LMArena 인간 선호도 최상위권, $0.30/$2.50 초저가, 1M 컨텍스트로 Tier 1에 최적입니다. Claude Sonnet 4.6은 SWE-bench 70.6% 세계 1위, 프롬프트 캐싱 90% 절감, 1M 컨텍스트로 Tier 2에 최적입니다. Claude Opus 4.6은 2026-02-05 출시 최신 모델로, Constitutional AI 최고 안전성, Extended Thinking 모드를 지원하여 Tier 3에 최적입니다. GPT-4.1 mini는 $0.40/$1.60 저가에 temp=0.0 결정론적 JSON 출력이 안정적이라 C2SC 파싱에 최적입니다.

---

## 8. 코드 레벨 미결 사항 및 개선 권장

첫째, BacktestOptimizer(backtest_optimizer.py)에서 OpenAI gpt-4o가 하드코딩되어 있어 LLMGateway 라우팅으로 통합 전환이 필요합니다. 둘째, OPUS-LLM-AI-v1-FULL-SPEC의 모델 표기가 "Gemini 2.0 Flash"로 되어 있어 실제 코드의 "gemini-2.5-flash"에 맞게 문서 업데이트가 필요합니다. 셋째, Gemini Context Caching(Phase 2 검토 예정)이 Tier 1에 적용되면 반복 시스템 프롬프트 비용을 추가 절감할 수 있습니다.

---

## 9. 결론

GO100 백억이는 자연어 대응에 Gemini 2.5 Flash(Tier 1), 전략 수립에 Claude Sonnet 4.6(Tier 2), 검증에 Claude Opus 4.6(Tier 3)이라는 3-Tier 아키텍처로 구성되어 있으며, 이는 2026년 2월 현재 각 분야의 세계 최상위 모델을 정확히 배치한 최적 구성입니다. 프롬프트 캐싱, 배치 API, 서킷 브레이커 페일오버까지 갖춘 엔터프라이즈급 LLM 인프라입니다.
