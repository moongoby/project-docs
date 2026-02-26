# CUR-GO100-BAEKEOGI-COMPREHENSIVE-TEST-001 보고서

**작성일**: 2026-02-25 18:00 KST
**우선순위**: P0
**상태**: **완료**

---

## 1. 목표

백억이(GO100 AI 채팅) 전체 인텐트 라우팅 + 응답 품질 55개 시나리오 종합 테스트.

## 2. 테스트 결과 요약

| 카테고리 | 시나리오 수 | 통과 | 실패 | 비고 |
|----------|-----------|------|------|------|
| HELP | 5 | 5 | 0 | |
| GOAL_SETUP | 5 | 5 | 0 | 수정 후 통과 |
| STOCK_SCREENING | 10 | 10 | 0 | |
| STOCK_INFO | 5 | 5 | 0 | |
| MARKET_BRIEFING | 5 | 5 | 0 | 수정 후 통과 |
| PORTFOLIO_STATUS | 5 | 5 | 0 | 수정 후 통과 |
| OPTIMIZE_EXISTING | 3 | 3 | 0 | |
| STRATEGY (기본값) | 5 | 5 | 0 | |
| Edge/Crossover | 7 | 7 | 0 | |
| 응답 품질 | 5 | 5 | 0 | |
| **합계** | **55** | **55** | **0** | **100% 통과** |

## 3. 상세 테스트 결과

### 3.1 HELP (5/5)

| # | 입력 메시지 | 기대 Agent | 결과 |
|---|-----------|-----------|------|
| 1 | GO100 어떻게 사용하나요? | HELP | ✅ |
| 2 | 뭐부터 해야하나요? | HELP | ✅ |
| 3 | 전략카드가 뭐예요? | HELP | ✅ |
| 4 | 백테스트 어디서 해요? | HELP | ✅ |
| 5 | 계좌 연결은 어떻게 하나요? | HELP | ✅ |

### 3.2 GOAL_SETUP (5/5)

| # | 입력 메시지 | 기대 Agent | 결과 | 비고 |
|---|-----------|-----------|------|------|
| 6 | 5천만원으로 3년 안에 3억 만들고 싶어 | GOAL | ✅ | |
| 7 | 1억으로 10년 후 10억 달성하고 싶어 | GOAL | ✅ | |
| 8 | 은퇴 자금 목표 설정해줘 | GOAL | ✅ | **수정 후 통과** — help+goal overlap |
| 9 | CAGR 30% 수익률 목표 | GOAL | ✅ | |
| 10 | 100만원으로 1억 만들기 | GOAL | ✅ | |

### 3.3 STOCK_SCREENING (10/10)

| # | 입력 메시지 | 기대 Agent | 결과 |
|---|-----------|-----------|------|
| 11 | 모멘텀 상승 종목 찾아줘 | STOCK_SCREENING | ✅ |
| 12 | 거래량 급증 종목 보여줘 | STOCK_SCREENING | ✅ |
| 13 | 외국인 순매수 종목 알려줘 | STOCK_SCREENING | ✅ |
| 14 | 기관 순매수 종목 찾아줘 | STOCK_SCREENING | ✅ |
| 15 | 오늘 상승 테마 알려줘 | STOCK_SCREENING | ✅ |
| 16 | 반도체 섹터 종목 추천해줘 | STOCK_SCREENING | ✅ |
| 17 | 수급 좋은 종목 스크리닝해줘 | STOCK_SCREENING | ✅ |
| 18 | 급등 종목 찾아줘 | STOCK_SCREENING | ✅ |
| 19 | 상한가 종목 알려줘 | STOCK_SCREENING | ✅ |
| 20 | 바이오 테마주 보여줘 | STOCK_SCREENING | ✅ |

### 3.4 STOCK_INFO (5/5)

| # | 입력 메시지 | 기대 Agent | 결과 |
|---|-----------|-----------|------|
| 21 | 삼성전자 주가 알려줘 | STOCK_INFO | ✅ |
| 22 | 카카오 종목 정보 보여줘 | STOCK_INFO | ✅ |
| 23 | NAVER PER 얼마야? | STOCK_INFO | ✅ |
| 24 | SK하이닉스 재무 현황 | STOCK_INFO | ✅ |
| 25 | 현대차 실적 어때? | STOCK_INFO | ✅ |

### 3.5 MARKET_BRIEFING (5/5)

| # | 입력 메시지 | 기대 Agent | 결과 | 비고 |
|---|-----------|-----------|------|------|
| 26 | 오늘 시장 어때? | MARKET_BRIEFING | ✅ | **수정 후 통과** — stock_info+market overlap |
| 27 | 코스피 시황 알려줘 | MARKET_BRIEFING | ✅ | **수정 후 통과** — help+market overlap |
| 28 | 오늘 장 마감 요약해줘 | MARKET_BRIEFING | ✅ | |
| 29 | 시장 브리핑 보여줘 | MARKET_BRIEFING | ✅ | |
| 30 | 환율 동향 알려줘 | MARKET_BRIEFING | ✅ | **수정 후 통과** — help+market overlap |

### 3.6 PORTFOLIO_STATUS (5/5)

| # | 입력 메시지 | 기대 Agent | 결과 | 비고 |
|---|-----------|-----------|------|------|
| 31 | 내 포트폴리오 현황 보여줘 | PORTFOLIO_STATUS | ✅ | **수정 후 통과** — help+portfolio overlap |
| 32 | 내 자산 얼마야? | PORTFOLIO_STATUS | ✅ | |
| 33 | 보유 종목 잔고 알려줘 | PORTFOLIO_STATUS | ✅ | **수정 후 통과** — help+stock+portfolio overlap |
| 34 | 내 수익률 어때? | PORTFOLIO_STATUS | ✅ | **수정 후 통과** — stock_info+portfolio overlap |
| 35 | 계좌 성과 요약해줘 | PORTFOLIO_STATUS | ✅ | **수정 후 통과** — market+portfolio overlap |

### 3.7 OPTIMIZE_EXISTING (3/3)

| # | 입력 메시지 | 기대 Agent | 결과 |
|---|-----------|-----------|------|
| 36 | 이 전략 최적화해줘 | OPTIMIZER | ✅ |
| 37 | 수익률 올려줘 | OPTIMIZER | ✅ |
| 38 | MDD 줄여서 개선해줘 | OPTIMIZER | ✅ |

### 3.8 STRATEGY / 기본값 (5/5)

| # | 입력 메시지 | 기대 Agent | 결과 |
|---|-----------|-----------|------|
| 39 | 볼린저밴드 전략 만들어줘 | UNDERSTAND | ✅ |
| 40 | RSI 기반 매매 전략 설계해줘 | UNDERSTAND | ✅ |
| 41 | 이동평균 골든크로스 전략 | UNDERSTAND | ✅ |
| 42 | 안녕하세요 | UNDERSTAND | ✅ |
| 43 | 단기 스캘핑 전략 하나 짜줘 | UNDERSTAND | ✅ |

### 3.9 Edge Cases / Crossover (7/7)

| # | 입력 메시지 | 기대 Agent | 결과 | 테스트 목적 |
|---|-----------|-----------|------|-----------|
| 44 | 상승 테마 종목 알려줘 | STOCK_SCREENING | ✅ | help+screening overlap |
| 45 | 코스닥 시황 설명해줘 | MARKET_BRIEFING | ✅ | help+market overlap |
| 46 | 삼성전자 PER 설명해줘 | STOCK_INFO | ✅ | help+stock_info overlap |
| 47 | 코스피 종목 주가 동향 | MARKET_BRIEFING | ✅ | stock_info+market overlap |
| 48 | ? | UNDERSTAND | ✅ | 1글자 입력 |
| 49 | ㅎ | UNDERSTAND | ✅ | 최소 입력 |
| 50 | 은퇴 자금 목표 설정해줘 | GOAL | ✅ | help+goal overlap |

### 3.10 응답 품질 검증 (5/5)

| # | 테스트 | 결과 | 상세 |
|---|--------|------|------|
| 51 | 외국인 순매수 스크리닝 데이터 | ✅ | 611자, 10개 종목 |
| 52 | 일일 브리핑 데이터 | ✅ | 2026-02-25, gainers 5, losers 5, AI 코멘터리 |
| 53 | 목표 설정 E2E | ✅ | agent=GOAL, status=awaiting_selection |
| 54 | HELP 응답 내용 | ✅ | 627자, GO100 서비스 설명 |
| 55 | STOCK_INFO 응답 | ✅ | 441자, 주가/시총/거래량 표시 |

## 4. 발견 이슈 및 수정

### 4.1 ISS-014: help+goal overlap ("설정" 키워드)

- **문제**: "은퇴 자금 목표 설정해줘" → HELP ("설정" in HELP_KEYWORDS)
- **수정**: help overlap 체크 시 goal_setup 키워드도 감지 → goal_setup 우선 반환
- **파일**: `intent_router.py`

### 4.2 ISS-015: help+market / stock_info+market overlap

- **문제**: "코스피 시황 알려줘" → STOCK_INFO ("알려줘" help → stock_info overlap)
- **문제**: "오늘 시장 어때?" → STOCK_INFO ("어때" in STOCK_INFO)
- **수정**:
  1. help overlap 내 market_briefing 체크를 stock_info 체크보다 앞으로 이동
  2. stock_info main chain에서 market_briefing 키워드 동시 매칭 시 market_briefing 우선
- **파일**: `intent_router.py`

### 4.3 ISS-016: portfolio_status 키워드 오버랩 (4건)

- **문제**: "포트폴리오"→HELP, "알려줘"→STOCK_INFO, "어때"→STOCK_INFO, "요약"→MARKET_BRIEFING
- **수정**: 3개 체크포인트에 portfolio_status overlap 감지 추가
  1. help overlap 내 portfolio_status 체크 (stock_info보다 먼저)
  2. stock_info main chain에서 portfolio_status 동시 매칭 체크
  3. market_briefing main chain에서 portfolio_status 동시 매칭 체크
- **파일**: `intent_router.py`

## 5. 수정 후 인텐트 라우터 우선순위 (최종)

```
1. optimize_existing (키워드 매칭)
2. help (키워드 매칭) → overlap 감지:
   → screening 키워드 ✓ → stock_screening
   → goal 키워드 ✓ → goal_setup
   → market 키워드 ✓ → market_briefing
   → portfolio 키워드 ✓ → portfolio_status
   → stock_info 키워드 ✓ → stock_info
   → (그 외) → help
3. goal_setup (키워드 매칭)
4. stock_screening (키워드 매칭)
5. stock_info (키워드 매칭) → overlap 감지:
   → market 키워드 ✓ → market_briefing
   → portfolio 키워드 ✓ → portfolio_status
   → (그 외) → stock_info
6. market_briefing (키워드 매칭) → overlap 감지:
   → portfolio 키워드 ✓ → portfolio_status
   → (그 외) → market_briefing
7. portfolio_status (키워드 매칭)
8. strategy (기본값)
```

## 6. 변경 파일

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/ai/intent_router.py` | ISS-014/015/016 — 6개 overlap 감지 로직 추가 |

## 보고 요약

- **55개 시나리오 전수 통과** (100%)
- **8개 인텐트 카테고리** 모두 정상 동작
- **7개 오버랩 케이스** 발견 → intent_router.py 수정으로 해결
- **응답 품질**: 스크리닝/브리핑/목표/도움/종목정보 모두 실데이터 반환 확인
- **기존 기능 영향**: 회귀 테스트 통과 (수정 전 통과했던 시나리오 전부 재확인)
