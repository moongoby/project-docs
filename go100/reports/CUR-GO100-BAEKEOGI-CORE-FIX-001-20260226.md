# CUR-GO100-BAEKEOGI-CORE-FIX-001 — 백억이 핵심 복구 완료 보고

**작성일**: 2026-02-26
**심각도**: CRITICAL
**지시서**: CUR-GO100-BAEKEOGI-CORE-FIX-001
**코드 레포**: `kis-autotrade-v4` (branch: `phase-2c-command-center`)

---

## 1. 작업 요약

| 블록 | 내용 | 상태 |
|------|------|------|
| **A** | C2SC 3단 폴백 (Gemini 1차 → Claude 2차 → 키워드 3차) | DONE |
| **B** | 할루시네이션 프롬프트 모순 해결 (prompts.py 2개) | DONE |
| **C** | stock_info 핸들러 전면 강화 (별명, 쿼리분류, 펀더멘털+수급) | DONE |
| **D** | goal_setup 선택 파싱 강화 ("1번"/"첫번째" 지원) | DONE |
| **E** | 검증 — 8건 curl 테스트 전부 PASS | DONE |
| **F** | 보고서 + 커밋 + 푸시 | DONE |

---

## 2. BLOCK A: C2SC 3단 폴백

### 2.1 문제

- 기존: Anthropic(Claude Haiku) 1차 → 크레딧 소진으로 100% 실패 → 8패턴 키워드 폴백만 작동
- 결과: 대부분 메시지가 `free_chat`(일반대화)로 분류 → stock_info, market_briefing 등 전용 핸들러 미사용

### 2.2 수정 내용

**파일: `backend/app/core/llm_gateway.py`**
- C2SC 라우팅 테이블: `Vendor.GOOGLE / gemini-2.5-flash` (1차), `max_tokens=256`
- FAILOVER_CHAINS: `[("google", "gemini-2.5-flash"), ("anthropic", "claude-haiku-4-5")]`

**파일: `backend/app/routers/go100/ai_router.py`**
- `_C2SC_ENHANCED_PROMPT`: 8개 intent 정의 + 예시 포함한 JSON-only 분류 프롬프트
- `_extract_intent_from_c2sc_response()`: 4단계 파싱
  1. 정규식 `"intent": "xxx"` (markdown fence 전처리 포함)
  2. JSON 파싱 (truncated JSON의 { } 범위 탐색)
  3. 직접 매칭 (intent명만 반환된 경우)
  4. 텍스트 내 intent명 검색 (truncated JSON 대응 — `stock_info` 등 부분 문자열 매칭)
- `_keyword_classify()`: 7개 intent × 60+ 키워드 (기존 8패턴에서 대폭 확장)
- `_classify_intent_c2sc()`: LLMGateway.send() 1회 호출 → 내부 FAILOVER_CHAINS로 Gemini→Claude 자동 폴백 → 실패 시 키워드 3차

### 2.3 결과

| 테스트 메시지 | C2SC 단계 | 분류 결과 |
|--------------|-----------|-----------|
| 삼전 얼마야 | 1차 Gemini | stock_info |
| 상한가 종목 알려줘 | 1차 Gemini | stock_info |
| 오늘 장 어때 | 1차 Gemini | market_briefing |
| 100만원으로 1억 만들고 싶어 | 1차 Gemini | goal_setup |
| 안녕 | 1차 Gemini | help |
| 내 포트폴리오 보여줘 | 1차 Gemini | portfolio_status |
| 거래량 폭발한 종목 | 1차 Gemini | stock_info |
| 005930 | 1차 Gemini | stock_info |

**8/8 Gemini 1차 성공** (max_tokens 256 + truncated JSON 파싱 강화 후)

---

## 3. BLOCK B: 할루시네이션 프롬프트 모순 해결

### 3.1 문제

- `services/go100/ai/prompts.py` 내 두 섹션이 모순:
  - `[절대 규칙]`: "할 수 없습니다"라고 답하라
  - `GOAL_REPLY_SECTION`: "불가능합니다라고 하지 마라"
- LLM이 혼란 → 일관성 없는 답변

### 3.2 수정 내용

**파일: `backend/app/services/go100/ai/prompts.py`**
- 기존 `[절대 규칙] 금융 데이터 할루시네이션 금지` 블록 → 통합 4포인트 규칙:
  1. DB에 없는 숫자 절대 창작 금지 → "현재 해당 데이터가 준비 중입니다" + 대안 안내
  2. 목표가 어렵더라도 "불가능합니다"로 끝내지 말고 대안 제시
  3. DB 데이터 있으면 반드시 인용 (출처 명시)
  4. 장마감 후 "내일 장 열리면 확인하겠습니다" 안내
- `GOAL_REPLY_SECTION` 동일 톤으로 정리

**파일: `backend/app/services/llm/prompts.py`**
- `free-chat` 시스템 프롬프트의 `[절대 규칙]` 동일하게 통합 4포인트 교체

---

## 4. BLOCK C: stock_info 핸들러 전면 강화

### 4.1 문제

- 기존: OHLCV만 반환, 별명 미지원, 쿼리 분류 없음
- "상한가 종목", "거래량 폭발" 등 aggregate 질문 처리 불가

### 4.2 수정 내용 (`ai_router.py`)

| 기능 | 설명 |
|------|------|
| `STOCK_ALIASES` | 35+ 한국어 별명 매핑 (삼전→삼성전자, 하닉→SK하이닉스, 카카→카카오 등) |
| `_identify_stock()` | 4단계 종목 식별: 종목코드 → 별명 → 따옴표 추출 → ILIKE DB 검색 |
| `_detect_stock_query_type()` | 5가지 쿼리 분류: individual / top_gainers / top_losers / top_volume / top_market_cap |
| `_handle_stock_info()` | 쿼리 타입별 분기 처리 |

**개별 종목 응답 데이터**:
- `stock_universe` JOIN: 시장, 섹터, 시총, 시총순위
- `ohlcv_daily`: 최근 5거래일 종가/거래량, 전일대비 등락
- `stock_fundamentals`: PER, PBR, EPS
- `v4_investor_daily`: 최근 3일 외국인/기관 순매수

**Aggregate 쿼리 응답**:
- 상한가(상승률 상위 10), 하한가(하락률 상위 10), 거래량 상위 10, 시총 상위 10

---

## 5. BLOCK D: goal_setup 선택 파싱 강화

### 5.1 수정 내용 (`ai_router.py: _parse_scenario_selection()`)

- 기존: "공격적"/"안전" 텍스트 매칭만 지원
- 추가: "1번"/"첫번째"/"a" → aggressive, "2번"/"두번째" → ultra_aggressive, "3번"/"세번째" → moderate
- Redis TTL 만료 시: "이전 시나리오가 만료되었습니다 (30분 초과). 다시 목표를 말씀해 주세요." 메시지

---

## 6. BLOCK E: 검증 결과

### 6.1 테스트 8건 전부 PASS

| # | 입력 | 기대 agent | 실제 agent | 데이터 검증 |
|---|------|-----------|-----------|-------------|
| 1 | 삼전 얼마야 | STOCK_INFO | STOCK_INFO | 삼성전자 203,500원, PER 30.5, 외국인/기관 수급 포함 |
| 2 | 상한가 종목 알려줘 | STOCK_INFO | STOCK_INFO | 루멘스 +30.30% 등 실제 DB 상위 10 |
| 3 | 오늘 장 어때 | MARKET_BRIEFING | MARKET_BRIEFING | 레짐 횡보, 점수 51, KOSPI 5,846 |
| 4 | 100만원으로 1억 만들고 싶어 | GOAL | GOAL | 목표 입력 안내 정상 |
| 5 | 안녕 | HELP | HELP | 인사 + 기능 안내 |
| 6 | 내 포트폴리오 보여줘 | PORTFOLIO_STATUS | PORTFOLIO_STATUS | 전략 3개, 백테스트 결과 포함 |
| 7 | 거래량 폭발한 종목 | STOCK_INFO | STOCK_INFO | 거래량 상위 10 실제 데이터 |
| 8 | 005930 | STOCK_INFO | STOCK_INFO | 삼성전자 전체 데이터 |

### 6.2 C2SC 로그 (journalctl 확인)

```
[C2SC-1차-Gemini] 성공 (google/gemini-2.5-flash): '삼전 얼마야' → stock_info
[C2SC-1차-Gemini] 성공 (google/gemini-2.5-flash): '상한가 종목 알려줘' → stock_info
[C2SC-1차-Gemini] 성공 (google/gemini-2.5-flash): '오늘 장 어때' → market_briefing
[C2SC-1차-Gemini] 성공 (google/gemini-2.5-flash): '100만원으로 1억 만들고 싶어' → goal_setup
[C2SC-1차-Gemini] 성공 (google/gemini-2.5-flash): '안녕' → help
[C2SC-1차-Gemini] 성공 (google/gemini-2.5-flash): '내 포트폴리오 보여줘' → portfolio_status
[C2SC-1차-Gemini] 성공 (google/gemini-2.5-flash): '거래량 폭발한 종목' → stock_info
[C2SC-1차-Gemini] 성공 (google/gemini-2.5-flash): '005930' → stock_info
```

### 6.3 체크리스트

- [x] C2SC Gemini 1차 성공 ≥ 1건 (실제: 8/8)
- [x] stock_info: 삼전 → PER, 종가, 수급 포함
- [x] 상한가 → 실제 DB 상위 10 반환
- [x] market_briefing → regime 점수 + KOSPI 지수
- [x] goal_setup → 시나리오 안내
- [x] help → 인사 + 기능 안내
- [x] portfolio_status → 카드 목록 + 백테스트 결과
- [x] 거래량 → 실제 DB 상위 10
- [x] 숫자 할루시네이션 없음 (모든 데이터 DB 조회)
- [x] prompts.py 모순 제거

---

## 7. 변경 파일 목록

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/core/llm_gateway.py` | C2SC route → Gemini 1차, max_tokens 256, FAILOVER_CHAINS 수정 |
| `backend/app/routers/go100/ai_router.py` | C2SC 3단 폴백 전면 교체, stock_info 5종 쿼리 핸들러, goal_setup 파싱 강화 |
| `backend/app/services/go100/ai/prompts.py` | 할루시네이션 규칙 통합 4포인트 |
| `backend/app/services/llm/prompts.py` | free-chat 할루시네이션 규칙 동일 교체 |

**백업**: `/root/backup/baekeogi-core-fix-20260225-234253/`

---

## 8. 추가 개선사항 (지시서 외)

1. **Truncated JSON 파싱 강화**: Gemini가 간헐적으로 response를 30자에서 truncate하는 현상 → `_extract_intent_from_c2sc_response()` 방법4에서 부분 문자열 매칭 추가하여 `"stock_info` (closing quote 없는) 패턴도 정상 파싱
2. **max_tokens 256**: C2SC RouteConfig + LLMRequest 모두 128→256으로 증가하여 truncation 빈도 감소
3. **`_SKIP_WORDS` 필터**: "알려줘", "어떻게" 등 비종목 단어가 종목으로 오인되는 것 방지

---

*작성: Claude Code (CUR-GO100-BAEKEOGI-CORE-FIX-001)*

---

## 9. 추가 긴급 수정 (2026-02-26 00:50)

### 문제 발견
프론트엔드 "자유대화" 탭이 `/api/v1/llm/chat/stream` 엔드포인트를 호출하고 있었으며, 이 엔드포인트에는 C2SC 인텐트 분류가 없어서 모든 질문이 범용 LLM 스트리밍으로 직행 → 데이터 없이 "조회할 수 없습니다" 응답.

### 수정

| 파일 | 변경 |
|------|------|
| `backend/app/api/v1/llm_router.py` | C2SC 인터셉터 추가 — stock_info/market_briefing/portfolio_status/stock_screening 인텐트 감지 시 go100 핸들러 직접 호출 |
| `frontend/src/components/chat/StrategyCardSaveButton.tsx` | 매수/매도/손절 섹션 최소 1개 있어야 "전략카드로 저장" 버튼 표시 |

### 검증
- "오늘 삼성전자 가격알려줘" → stock_info 인터셉트 → 203,500원 실데이터
- "오늘장 어때" → market_briefing 인터셉트 → 레짐/KOSPI 실데이터
- "안녕" → help (data-backed 아님) → 일반 LLM 스트리밍 정상

### 커밋
- `phase-2c-command-center` → `6adb7162`
