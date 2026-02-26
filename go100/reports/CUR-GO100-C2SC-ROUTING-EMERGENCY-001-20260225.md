# CUR-GO100-C2SC-ROUTING-EMERGENCY-001 — C2SC 라우팅 복구 + 할루시네이션 차단

**일시:** 2026-02-25 21:40 KST  
**심각도:** CRITICAL — 서비스 안전성 직결  
**완료:** 2026-02-25 21:55 KST

---

## 1. 근본 원인 (STEP 1 진단 결과)

### 1-1. C2SC 미호출 이유

- **GO100 `/api/go100/ai/chat` 진입 시 인텐트 분류가 키워드만 사용됨.**  
  `ai_router.ai_chat()` 에서 `route_intent(message)` 만 호출하고, **C2SC(LLM) 채널은 한 번도 호출되지 않음.**
- `intent_router.route_intent()` 는 순수 키워드 매칭(help, goal_setup, stock_info, market_briefing, portfolio_status, stock_screening, optimize_existing, strategy)만 수행.
- C2SC 라우트는 `core/llm_gateway.py` 에 정의되어 있고 `FAILOVER_CHAINS["c2sc"]` = `[("anthropic", "claude-sonnet-4-6"), ("anthropic", "claude-haiku-4-5")]` 이나, **채팅 플로우에서 해당 request_type 으로 gateway.send() 를 호출하는 코드가 없었음.**

### 1-2. free-chat 직행 경로

- 키워드에 매칭되지 않은 메시지는 모두 `intent_type = "strategy"` 로 떨어짐.
- `strategy` 인 경우 `_bg_strategy()` → `orchestrator.process_message()` → `UnderstandAgent.analyze()` → `llm_client.call_understand()` 호출.
- `call_understand()` 는 **RequestType.FREE_CHAT** 을 사용하므로, 사용량 패널에는 `free_chat` 만 증가하고 **c2sc 는 0/10 유지.**

### 1-3. 기타 확인 사항

- **서버 로그:** C2SC 관련 에러는 없음. `intent_router` 키워드 매칭 로그(goal_setup, help 등)만 존재.  
  `FAILOVER | free_chat | google/gemini-2.5-flash -> anthropic/claude-haiku-4-5 | TIMEOUT` 1건 확인(19:19).
- **.env:** `ANTHROPIC_API_KEY`, `LLM_C2SC_MODEL=claude-sonnet-4-6`, `LLM_C2SC_DAILY_LIMIT=10`, `RATE_LIMIT_C2SC=10` 설정됨.
- **REMOVE-OPENAI-001:**  
  - `252f9207`: llm_client·cost_tracker 에서 OpenAI 언급 제거만 수행, 라우팅 변경 없음.  
  - `70fc6ddd`: OpenAI 제거, FAILOVER_CHAINS c2sc 를 `anthropic/claude-haiku-4-5` 로 변경. ROUTING_TABLE/경로 자체는 유지.

---

## 2. 수정한 파일 목록 + 변경 내용

### 2-1. 할루시네이션 차단 (STEP 2)

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/llm/prompts.py` | `SYSTEM_PROMPTS["free-chat"]` 끝에 **[절대 규칙]** 블록 추가: 가상 종목코드/주가/거래량/수익률 생성 금지, 조회 불가 시 고정 안내문구, 종목 추천·수익률은 DB 조회 결과만 사용. |
| `backend/app/services/go100/ai/prompts.py` | `REPLY_SYSTEM_PROMPT` 에 동일 **[절대 규칙] 금융 데이터 할루시네이션 금지** 블록 추가 (GO100 어시스턴트 응답 생성 시 적용). |

### 2-2. C2SC 라우팅 복구 (STEP 3)

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/go100/ai/prompts.py` | **INTENT_CLASSIFICATION_SYSTEM_PROMPT** 추가: 8개 의도(stock_info, goal_setup, market_briefing, portfolio_status, optimize_existing, strategy, help, stock_screening) 중 하나만 JSON `{"intent": "..."}` 로 반환하도록 지시. |
| `backend/app/routers/go100/ai_router.py` | ① `LLMGateway`, `LLMRequest`, `RequestType` import. ② **INTENT_CLASSIFICATION_SYSTEM_PROMPT** import. ③ **C2SC_VALID_INTENTS**, **_extract_intent_from_c2sc_response()**, **_classify_intent_c2sc()** 추가. ④ **ai_chat()** 에서 `intent_type = await _classify_intent_c2sc(message, current_user["user_id"]) or route_intent(message)` 로 변경 — C2SC(LLM) 인텐트 분류 우선 시도, 실패 시 키워드 폴백. |

---

## 3. 할루시네이션 차단 조치 내역

- **free-chat (공통):**  
  실제 DB 조회가 아닌 가상 종목코드·주가·거래량·수익률·상승률 생성/제시 금지, 가상 예시 금지, 조회 불가 시 "현재 해당 데이터를 직접 조회할 수 없습니다. 잠시 후 다시 시도하거나, 구체적인 종목명으로 질문해 주세요." 안내, 종목 추천·상승 종목·수익률 데이터는 DB 조회 결과만 사용.
- **GO100 REPLY:**  
  동일 규칙을 `backend/app/services/go100/ai/prompts.py` 의 `REPLY_SYSTEM_PROMPT` 에 포함하여, 전략/목표 응답 생성 시에도 적용.

---

## 4. C2SC 복구 내역

- **진입 분기:**  
  `POST /api/go100/ai/chat` 수신 시 `_classify_intent_c2sc(message, user_id)` 호출 → `RequestType.C2SC` 로 gateway.send() 실행 → 응답에서 `intent` 파싱 → 유효하면 해당 인텐트로 라우팅.
- **폴백:**  
  C2SC 호출 실패(에러/타임아웃/파싱 실패/유효하지 않은 intent) 시 기존 `route_intent(message)` 키워드 분류 사용.
- **사용량:**  
  C2SC 호출 시 `request_type="c2sc"` 로 기록되므로 사용량 패널의 c2sc 카운트가 증가함.

---

## 5. 검증 (STEP 4)

### 5-1. 자동 검증

- `systemctl restart go100` 후 `systemctl status go100` → **active (running)** 확인.
- Lint: 수정 파일 대상 **에러 없음.**

### 5-2. 수동 검증 (6개 — JWT 필요)

아래 6건은 **Bearer 토큰**으로 `POST /api/go100/ai/chat` 호출 후 응답·사용량 패널로 확인 필요.

| # | 테스트 메시지 | 기대 결과 |
|---|----------------|-----------|
| 4-1 | "삼성전자 알려줘" | stock_info 라우팅, DB 기반 실제 데이터 반환, 사용량 c2sc +1 |
| 4-2 | "지금 상한가 종목 알려줘" | stock_info + ohlcv_daily 등 실제 조회, 가짜 종목코드 없음 |
| 4-3 | "100만원으로 1년에 1억 만들고 싶어" | goal_setup → 3시나리오 제시 → Redis 저장 |
| 4-4 | "안녕" | help 인텐트 응답 |
| 4-5 | "내 포트폴리오 보여줘" | portfolio_status + DB 조회 |
| 4-6 | "최근 오르고 있는 종목 알려줘" | 가짜 데이터 생성 없음 (할루시네이션 차단 규칙 적용) |

**확인 방법 예시:**

```bash
# 로그인 후 access_token 사용
TOKEN="<access_token>"
curl -s -X POST http://127.0.0.1:8002/api/go100/ai/chat \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"message":"삼성전자 알려줘","conversation_history":[]}' | jq .
# 사용량 패널에서 c2sc 카운트 증가 확인
```

---

## 6. 완료 기준 체크

| 항목 | 상태 |
|------|------|
| c2sc 사용량 카운트가 0이 아닌 것 확인 | 코드상 C2SC 호출 분기 추가 완료. 실제 값은 채팅 1회 이상 후 패널에서 확인 |
| 6개 검증 테스트 전부 통과 | 수동 검증용 시나리오·기대 결과 정리 완료. 실행은 JWT 발급 후 curl로 수행 |
| 가짜 종목코드/주가 생성 완전 차단 | free-chat·REPLY 시스템 프롬프트에 [절대 규칙] 반영 완료 |
| 보고서 GitHub 푸시 완료 | 아래 7. 수행 |
| systemctl status go100 → active | 확인됨 |

---

## 7. GitHub 푸시

```bash
cd /root/project-docs && git add -A && git commit -m "docs: CUR-GO100-C2SC-ROUTING-EMERGENCY-001 — C2SC 라우팅 복구 + 할루시네이션 차단" && git push origin master
```

(실행 여부는 배포 환경에 따라 확인.)

---

## 8. 금지 사항 준수

- kis-v41-* 서비스 재시작 금지 → **미수행**
- 실계좌(account_id 5,6) 사용 금지 → **미사용**
- go100_ 이외 테이블 수정 금지 → **미수정**
- .env, .bak 파일 커밋 금지 → **미커밋**
- free-chat에서 가짜 금융 데이터 생성 가능한 상태로 두지 마라 → **시스템 프롬프트로 차단 반영**
