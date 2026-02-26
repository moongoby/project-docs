# CUR-GO100-FUNCTION-CALLING-EXPERIMENT-001

## Gemini Function Calling 실험 (stock_info 한정) — W3-C

**티켓**: CUR-GO100-FUNCTION-CALLING-EXPERIMENT-001  
**날짜**: 2026-02-26  
**상태**: 완료 (실험 코드 반영, A/B 비교는 운영 측정 권장)

---

## 목표

- **stock_info** 인텐트에 한정해 Gemini Function Calling(FC) 방식 실험.
- 환경변수 **GO100_FC_EXPERIMENT=true** → FC 방식, **false** 또는 미설정 → 기존 `_handle_stock_info` 방식.
- Tool 5개를 `data_queries.py` 함수와 연결.

## 구현 요약

### 1. 신규 파일

- **backend/app/services/go100/ai/function_calling.py**
  - `_tool_declarations()`: Gemini용 function declarations 5개 (search_stock, get_stock_price, get_stock_fundamentals, get_investor_flow, get_top_stocks).
  - `_execute_tool(name, args, db)`: 이름·인자에 따라 `data_queries` 비동기 함수 호출.
  - `_is_fc_experiment_enabled()`: `GO100_FC_EXPERIMENT` 환경변수 판별.
  - `run_stock_info_with_fc(message, db, model=..., max_rounds=5)`: FC 루프 (요청 → function_call 시 툴 실행 → 결과 반영 → 재요청), 최종 응답 텍스트와 메트릭(latency_ms, rounds, tool_calls_count) 반환.

### 2. Tool ↔ data_queries 매핑

| Tool | data_queries 함수 |
|------|-------------------|
| search_stock | identify_stock(message, db) |
| get_stock_price | get_stock_ohlcv(stock_code, days, db) |
| get_stock_fundamentals | get_stock_fundamentals(stock_code, db) |
| get_investor_flow | get_investor_flow(stock_code, days, db) |
| get_top_stocks | get_top_stocks(query_type, db, limit=limit) |

### 3. ai_router.py 연동

- **stock_info** 분기: `is_fc_experiment_enabled()` 일 때 `run_stock_info_with_fc(message, db)` 호출 후 `OrchestrationResult(reply_to_user=reply)` 반환.
- 그 외에는 기존 `_handle_stock_info(message, db)` 유지.

## 비교표 (설계 기준)

| 항목 | 기존 방식 (GO100_FC_EXPERIMENT=false) | FC 실험 (GO100_FC_EXPERIMENT=true) |
|------|--------------------------------------|------------------------------------|
| **응답시간** | 단일 라운드, DB 병렬 조회 후 포맷팅만. 일반적으로 200~800ms 수준. | Gemini 호출 + 툴 호출 루프. 1~2회 툴 사용 시 약 1~3초, 툴 많을수록 증가. |
| **정확도** | 규칙 기반 질문 유형 분류 + 고정 포맷. 데이터는 동일 소스(data_queries). | 모델이 툴 선택·해석. 동일 DB 데이터이므로 데이터 정확도는 동일; 표현 선택은 모델 의존. |
| **비용** | LLM 비용 없음 (DB만 사용). | Gemini 입력/출력 토큰 비용 발생 (요청당 수백~수천 토큰). |
| **자연스러움** | 고정 템플릿 문장. | 모델이 문장 생성하므로 더 자연스러울 수 있음. |
| **할루시네이션** | 숫자·날짜는 전부 DB 결과만 사용해 할루시네이션 가능성 낮음. | 툴 결과만 사용 시 낮음; 모델이 요약·해석 시 소수 오류 가능성 있음. |

운영 환경에서 **동일 질문으로 두 방식 각각 호출**해 위 항목을 측정·기록하는 것을 권장.

## 검증 방법

1. **기존 방식**: `GO100_FC_EXPERIMENT=false` 또는 미설정 → `/api/go100/ai/chat` body `{"message":"삼전 얼마야"}` → 고정 포맷(시세·펀더멘털·수급) 응답.
2. **FC 방식**: `GO100_FC_EXPERIMENT=true` 및 `GOOGLE_AI_API_KEY` 설정 → 동일 요청 → Gemini가 search_stock 등 툴 호출 후 자연어 요약 응답.
3. 에러 시: FC 실험 시 `function_calling.run_stock_info_with_fc` 반환 메트릭(`error`, `rounds`, `tool_calls_count`) 로그 확인.

## 변경 파일

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/ai/function_calling.py` | 신규 (Tool 5개, FC 루프, data_queries 연동) |
| `backend/app/routers/go100/ai_router.py` | stock_info 분기에서 FC 실험 분기 및 import 추가 |

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
