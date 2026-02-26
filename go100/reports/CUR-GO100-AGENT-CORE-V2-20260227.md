# CUR-GO100-AGENT-CORE-V2-20260227 — v2.0 Agentic Architecture Phase 1

**날짜**: 2026-02-27
**작성 시각**: KST 08:20

---

## 1. 구축 개요

GO100 AI 어시스턴트의 v2.0 Agentic Architecture Phase 1 구현.
기존 인텐트 분류→하드코딩 핸들러 방식에서, LLM이 도구를 자율 선택하는 Agent Loop 방식으로 전환.

| 항목 | 내용 |
|---|---|
| 신규 파일 | `tool_executors.py` (21 실행기), `agent_core.py` (Agent Loop) |
| 기존 파일 | `agent_tools.py` (21 도구 정의, 수정 없음) |
| LLM Provider | Gemini 2.5 Flash (기본) / Anthropic Claude Sonnet (폴백) |
| 토글 | `GO100_AGENT_MODE=false` (테스트 후 true 전환) |

---

## 2. 아키텍처

```
사용자 메시지
    │
    ▼
┌─────────────────────────────────┐
│        agent_core.py            │
│  ┌─────────────────────────┐    │
│  │  Agent Loop (max 5 R)   │    │
│  │  1. LLM에 질문+도구 전달│    │
│  │  2. LLM → function_call │    │
│  │  3. tool_executors 실행  │    │
│  │  4. 결과 → LLM 재전달   │    │
│  │  5. 최종 응답 or 반복    │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
    │                    │
    ▼                    ▼
agent_tools.py    tool_executors.py
(21 도구 정의)    (21 실행 함수)
                       │
                       ▼
                  PostgreSQL
                  (kisautotrade)
```

---

## 3. 도구 목록 (21개)

| 카테고리 | 도구명 | DB 테이블 |
|---|---|---|
| **시장 (3)** | get_market_overview | index_daily, ohlcv_daily |
| | get_market_regime | v4_market_regime_daily |
| | get_global_market | go100_global_market |
| **종목 (4)** | get_stock_price | ohlcv_daily, stock_universe |
| | get_stock_fundamentals | stock_fundamentals, go100_fundamentals_pit |
| | get_investor_flow | v4_investor_daily |
| | get_stock_ohlcv | ohlcv_daily |
| **섹터 (3)** | get_sector_performance | go100_sector_price |
| | get_sector_correlation | go100_sector_correlation |
| | get_top_stocks | ohlcv_daily, stock_universe |
| **포트폴리오 (3)** | get_portfolio_summary | go100_portfolios, go100_positions |
| | get_strategy_cards | go100_strategy_cards |
| | get_backtest_results | go100_backtest_runs |
| **시그널 (3)** | get_cross_market_signals | go100_cross_market_signals |
| | get_overnight_gap | ohlcv_daily (갭 계산) |
| | get_experience_similar | go100_experience_log |
| **매매 (2)** | get_paper_trading_status | go100_paper_positions |
| | get_trade_history | go100_trades |
| **보고서 (1)** | get_latest_report | go100_reports |
| **사용자 (2)** | get_goal_progress | go100_goals |
| | get_user_profile | go100_user_profile |

---

## 4. 테스트 결과

### 4-1. tool_executors 단독 테스트

| 도구 | 결과 | 비고 |
|---|---|---|
| get_market_regime | OK | regime=SIDEWAYS, score=51.0 |
| get_stock_price("삼성전자") | OK | 005930, 218,000원 |
| get_cross_market_signals | OK | 3건 (bullish/neutral 시그널) |
| get_user_profile | OK | aggressive, swing, 반도체/자동차/2차전지/AI |

### 4-2. Agent Core 통합 테스트 (Gemini 2.5 Flash)

| 질문 | 도구 호출 | 라운드 | 지연 | 토큰 |
|---|---|---|---|---|
| "삼성전자 현재가랑 외국인 수급 알려줘" | get_stock_price, get_investor_flow | 2 | 5,281ms | in=5235, out=286 |
| "오늘 시장 어때?" | get_market_overview | 2 | 6,876ms | in=4232, out=229 |
| "반도체 섹터 상황 알려줘" | get_sector_performance | 2 | 2,680ms | in=4037, out=50 |
| "SK하이닉스 PER이랑 외국인 수급 같이 보여줘" | get_stock_fundamentals, get_investor_flow | 2 | 7,000ms | in=5167, out=669 |

**핵심 관측:**
- LLM이 질문에 맞는 도구를 정확히 선택 (멀티 도구 병렬 호출 성공)
- 도구 실행 자체는 20~30ms, 대부분 지연은 LLM 응답 대기
- 종목명 → 종목코드 자동 변환 정상 (줄임말 사전 + stock_universe ILIKE)

---

## 5. 주요 설계 결정

| 결정 | 이유 |
|---|---|
| psycopg2 동기 직접 쿼리 (tool_executors) | Agent Loop가 asyncio.to_thread로 LLM 호출하므로, 도구 실행은 동기로 충분. FastAPI의 AsyncSession 의존 제거 |
| stock_universe 테이블로 종목 해소 | data_queries.py와 동일 패턴, 정확 매칭 우선 + ILIKE 폴백 |
| google.genai SDK 사용 | 기존 function_calling.py와 동일 (google-genai 패키지) |
| Anthropic 폴백 지원 | AGENT_LLM_PROVIDER=anthropic으로 전환 가능 |
| MAX_ROUNDS=5, MAX_TOOLS_PER_ROUND=3 | 무한 루프 방지, 비용 제어 |
| GO100_AGENT_MODE 환경변수 토글 | 기존 인텐트 기반 라우팅과 병행 가능 |

---

## 6. 파일 목록

| 경로 | 크기 | 설명 |
|---|---|---|
| `backend/app/services/go100/ai/agent_tools.py` | 11KB | 21개 도구 스키마 정의 (기존, 수정 없음) |
| `backend/app/services/go100/ai/tool_executors.py` | 30KB | 21개 도구 실행 함수 (신규) |
| `backend/app/services/go100/ai/agent_core.py` | 14KB | Agent Loop 엔진 (신규) |

---

## 7. 다음 단계

| Phase | 내용 | 상태 |
|---|---|---|
| Phase 1 | agent_core + tool_executors 구현 | **완료** |
| Phase 2 | ai_router 연동 (GO100_AGENT_MODE=true) | 다음 |
| Phase 3 | 대화 컨텍스트 유지 (세션 메모리) | 예정 |
| Phase 4 | 경험 DB 축적 + 유사 경험 검색 활성화 | 예정 |
| Phase 5 | 프로덕션 모니터링 + A/B 테스트 | 예정 |

---

*Phase 1 완료. 프로덕션 적용은 GO100_AGENT_MODE=true 전환으로 활성화.*
