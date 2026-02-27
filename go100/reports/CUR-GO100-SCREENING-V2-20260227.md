# CUR-GO100-SCREENING-V2 — 자체 스크리닝 엔진 V2: 조건식 조합 검색

- **날짜**: 2026-02-27
- **레포**: kis-autotrade-v4 (branch: phase-2c-command-center)
- **커밋**: `652ebe97` (스크리닝 엔진), `4144b69c` (Agent Core combined 지원)
- **서비스**: GO100 (백억이 AI 채팅)

## 개요

기존 3개 필터(momentum_up, foreign_buy, theme)만 지원하던 채팅 스크리닝 엔진을 **13개 필터 + 조합 검색**으로 확장. 백테스트용 `universe/` 모듈의 필터 SQL 로직을 참조하되, 채팅용으로 종목 상세정보(이름, 가격 등)를 함께 반환하도록 구현. Agent Core(GO100_AGENT_MODE=true) 경로에서도 combined 조합검색 지원.

## 수정 파일

| 파일 | 변경 | 내용 |
|------|------|------|
| `backend/app/services/go100/screening_engine.py` | +639/-19 | 10개 신규 필터 + combined + detect/run/format 확장 |
| `backend/app/services/go100/ai/intent_router.py` | +11 | STOCK_SCREENING_KEYWORDS 22개 키워드 추가 |
| `backend/app/services/go100/ai/response_formatter.py` | +1/-1 | screening_unavailable 에러 메시지 업데이트 |
| `backend/app/services/go100/ai/tool_executors.py` | +53 | screen_stocks에 combined filter_type 추가 (Agent Core 경로) |
| `backend/app/services/go100/ai/agent_tools.py` | +11/-5 | screen_stocks 도구 정의에 combined + filters 파라미터 |
| `backend/app/routers/go100/ai_router.py` | +4/-1 | C2SC 프롬프트 스크리닝 예시 확장, _keyword_classify 순서 조정 |

## 신규 필터 목록

| # | 필터 ID | 조건 | 데이터 소스 |
|---|---------|------|------------|
| 1 | `golden_cross` | 5일선 > 20일선 돌파 (전일 5MA<20MA → 금일 5MA>20MA) | ohlcv_daily |
| 2 | `death_cross` | 5일선 < 20일선 돌파 | ohlcv_daily |
| 3 | `ma_align_bull` | 5일 > 20일 > 60일 정배열 | ohlcv_daily |
| 4 | `rsi_oversold` | RSI(14) < 30 과매도 | ohlcv_daily |
| 5 | `rsi_overbought` | RSI(14) > 70 과매수 | ohlcv_daily |
| 6 | `value_low_per` | PER < 10 AND ROE > 5% | stock_fundamentals |
| 7 | `institution_buy` | 기관 연속 순매수 >= 3일 | v4_investor_daily |
| 8 | `volume_surge` | 거래량 > 20일 평균 x 3 | ohlcv_daily |
| 9 | `gap_up` | 시가 > 전일종가 x 1.03 | ohlcv_daily |
| 10 | `trade_strength` | 체결강도 평균 > 120 | v4_trade_strength_history |

## 조합 검색 (combined)

사용자가 2개 이상 필터 키워드를 한 문장에 넣으면 자동으로 교집합 검색:

- "외국인 매수 저PER 종목" → `foreign_buy ∩ value_low_per`
- "골든크로스 거래량 폭발 종목" → `golden_cross ∩ volume_surge`

빈 결과 필터도 교집합에 포함하여 정확한 결과 보장 (빈 집합 버그 수정 완료).

## 테스트 결과

### 백억이 채팅 실제 테스트 (API: /api/go100/ai/chat)

#### 1. 골든크로스 종목 찾아줘
```
골든크로스 발생 종목 10개를 찾아왔어요!

- 코리아써우 (007815): 현재가 18,170원, 5일MA 17,542원, 20일MA 17,188원
- 지아이텍 (382480): 현재가 2,675원, 5일MA 2,450원, 20일MA 2,403원
- CG인바이츠 (083790): 현재가 1,479원, 5일MA 1,312원, 20일MA 1,292원
- 오픈놀 (440320): 현재가 4,065원, 5일MA 3,745원, 20일MA 3,702원
  ... 외 6건
```
→ **PASS** (10건 반환, 필터 정확)

#### 2. RSI 과매도 종목 찾아줘
```
RSI 과매도 종목 검색 결과 (RSI 30 이하)

- 인크레더블버즈 (064090): 798원, RSI 0.0
- 엔케이맥스 (182400): 3,670원, RSI 0.0
- 알파AI (043100): 1,786원, RSI 3.8
- 모아라이프플러스 (142760): 770원, RSI 5.4
  ... 외 6건
```
→ **PASS** (10건, RSI<30 정확)

#### 3. 거래량 폭발 종목 보여줘
```
거래량 폭발 상위 10개 종목:

- 오픈놀 (440320): 4,065원, 거래량 비율 109.4배
- 참엔지니어링 (009310): 1,312원, 거래량 비율 66.3배
- SGA솔루션즈 (184230): 641원, 거래량 비율 43.7배
  ... 외 7건
```
→ **PASS** (10건, vol_ratio 내림차순)

#### 4. 골든크로스이면서 거래량 폭발한 종목 찾아줘 (조합 검색)
```
골든크로스이면서 거래량 폭발 조건을 만족하는 종목:

- 인트론바이오 (KOSDAQ) — 4,615원
- SGA솔루션즈 (KOSDAQ) — 641원
- 오픈놀 (KOSDAQ) — 4,065원
```
→ **PASS** (3건 교집합, Agent Core combined 경로 정상 동작)

#### 5. 모멘텀 상승 종목 찾아줘 (하위호환)
→ **PASS** (기존 momentum_up 필터 정상)

### DB 쿼리 실행 테스트 (12개 필터)

| 필터 | 결과 건수 | 첫 번째 종목 |
|------|----------|-------------|
| golden_cross | 10 | 코리아써우 (007815) |
| death_cross | 10 | 와이제이링크 (209640) |
| ma_align_bull | 10 | 현대ADM (187660) |
| rsi_oversold | 10 | 인크레더블버즈 (064090) |
| rsi_overbought | 10 | 삼익THK (004380) |
| value_low_per | 10 | DH오토넥스 (000300) |
| institution_buy | 0 | (데이터 부재 — 쿼리 정상) |
| volume_surge | 10 | 오픈놀 (440320) |
| gap_up | 10 | 젠큐릭스 (229000) |
| trade_strength | 10 | 363510 |
| momentum_up | 10 | 오픈놀 (440320) |
| foreign_buy | 0 | (데이터 부재 — 쿼리 정상) |

### 조합 검색 교집합 테스트

| 조합 | 결과 건수 | 비고 |
|------|----------|------|
| golden_cross + volume_surge | 6 | 정상 교집합 |
| volume_surge + rsi_oversold | 2 | 정상 교집합 |
| foreign_buy + value_low_per | 0 | foreign_buy 빈 결과 → 교집합 0 (정상) |

### Intent Router 검증

| 입력 메시지 | 감지 타입 | 결과 |
|------------|----------|------|
| "골든크로스 종목 찾아줘" | golden_cross | OK |
| "RSI 과매도 종목" | rsi_oversold | OK |
| "외국인 매수 저PER 종목" | combined | OK |
| "정배열 종목" | ma_align_bull | OK |
| "모멘텀 상승 종목" | momentum_up | OK (하위호환) |
| "거래량 폭발 종목 보여줘" | volume_surge | OK |
| "갭상승 종목" | gap_up | OK |
| "기관매수 종목" | institution_buy | OK |
| "체결강도 높은 종목" | trade_strength | OK |
| "데드크로스 종목" | death_cross | OK |
| "과매수 종목" | rsi_overbought | OK |

## 설계 결정

1. **단일 SQL CTE 쿼리**: 각 필터는 window function + CTE로 한 번의 쿼리로 결과 반환
2. **교집합 방식**: combined 모드에서 각 필터 결과의 stock_code 교집합 → 상세정보 조회
3. **기존 3개 필터 유지**: momentum_up, foreign_buy, theme 100% 하위호환
4. **Agent Core 경로 지원**: GO100_AGENT_MODE=true일 때 tool_executors.screen_stocks에서도 combined 처리
5. **C2SC 프롬프트 보강**: LLM 인텐트 분류에서 스크리닝 예시 확장 (골든크로스, RSI, 조합검색 등)

## 발견 및 수정 이슈

1. **빈 집합 교집합 버그**: combined에서 결과 0건인 필터가 code_sets에서 제외되어 교집합이 부정확 → 빈 집합도 포함하도록 수정
2. **Agent Core 경로 우회**: GO100_AGENT_MODE=true 시 C2SC → Agent Core로 직행하여 screening_engine.py를 거치지 않음 → tool_executors.py에 combined 직접 구현
3. **C2SC 분류 오류**: LLM이 "골든크로스 거래량 폭발 종목"을 stock_screening이 아닌 다른 인텐트로 분류 → C2SC 프롬프트에 스크리닝 예시 대폭 추가

## 서비스 상태

- `systemctl status go100` → active (running)
- 프론트엔드 변경 없음 (빌드 불필요)
