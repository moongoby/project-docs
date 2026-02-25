# CUR-GO100-STOCK-INFO-ENRICHMENT-001

## Wave 2: 백억이 데이터 연결 + 후처리 필터

**날짜**: 2026-02-26
**브랜치**: `feat/CUR-GO100-STOCK-INFO-ENRICHMENT-001` (from `phase-2c-command-center`)
**상태**: 완료

---

## 작업 요약

Wave 1 이후 백억이(GO100 AI) 챗봇의 `stock_info` / `market_briefing` / `portfolio_status` 핸들러에 실제 재무+수급 데이터를 연결하고, LLM 할루시네이션 후처리 필터를 추가.

## 변경 파일

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/ai/data_queries.py` | **신규** — DB 조회 함수 모듈 |
| `backend/app/services/go100/ai/response_filter.py` | **신규** — 할루시네이션 후처리 필터 |
| `backend/app/routers/go100/ai_router.py` | stock_info/market_briefing/portfolio_status 리팩토링+확장, data_queries 활용, response_filter 연동 |

## DB 스키마 변경

```sql
ALTER TABLE stock_fundamentals
  ADD COLUMN IF NOT EXISTS roe REAL,
  ADD COLUMN IF NOT EXISTS dividend_yield REAL,
  ADD COLUMN IF NOT EXISTS revenue BIGINT,
  ADD COLUMN IF NOT EXISTS operating_profit BIGINT;
```

- ROE: eps/bps 기반 계산 (2,439건 업데이트)
- dividend_yield: stock_universe 마이그레이션 시도 (데이터 0건)
- revenue/operating_profit: 향후 KIS API 수집 대비 NULL 허용

## Step별 구현 내용

### W2-A: data_queries.py (신규)
- `identify_stock()`: STOCK_ALIASES + 코드/줄임말/ILIKE 4단 검색
- `get_stock_ohlcv()`: ohlcv_daily N일 조회
- `get_stock_fundamentals()`: stock_fundamentals 우선 → stock_universe 폴백
- `get_investor_flow()`: v4_investor_daily 수급 데이터
- `get_market_regime()`: v4_market_regime_daily KOSPI
- `get_index_data()`: index_daily KOSPI/KOSDAQ
- `get_user_portfolio()`: go100_strategy_cards
- `get_user_goal()`: go100_goals (ACTIVE/PLANNING)
- `get_positions_count()`: go100_positions OPEN/전체
- `get_top_stocks()`: 상승률/하락률/거래량/시총 상위

### W2-A: stock_info 리팩토링
- `_identify_stock` + `STOCK_ALIASES` → `data_queries.identify_stock` 활용
- `_detect_stock_query_type()` 추가 (개별/상승/하락/거래량/시총)
- 개별 종목: `asyncio.gather(ohlcv, fundamentals, investor_flow)` 병렬 조회
- `_format_stock_report()` 분리 — 3개 섹션(시세+펀더멘털+수급) 포맷
- 펀더멘털: PER/PBR/EPS/BPS/ROE/배당/대출잔고 표시
- 수급: 연속매수일, 지분율, 3일 상세 표시

### W2-B: market_briefing 확장
- 1일 → 5일 추이 표시 (레짐 점수 + 지수)
- VKOSPI 라벨 (안정/주의/경고)
- 외국인 20일 흐름 이모지 (순매수/순매도)
- 레짐 변화 이력 (transitions 5일 내)

### W2-C: portfolio_status 확장
- go100_goals 목표 조회 (진행률, 성향 표시)
- go100_positions 보유 포지션 카운트
- 기존 전략 카드 표시 유지

### W2-D: response_filter.py (신규)
3가지 필터:
1. 가짜 종목코드 감지 (stock_universe에 없는 6자리)
2. 비현실적 수익률 감지 (+-100% 초과)
3. 미래 날짜 데이터 감지

적용 대상: strategy, optimize LLM 생성 응답만.
DB 직접 조회 핸들러는 미적용.

## 검증 결과 (8건 curl 테스트)

| # | 테스트 | 결과 |
|---|--------|------|
| 1 | Health check | PASS |
| 2 | stock_info: 삼성전자 (시세+펀더멘털+수급) | PASS |
| 3 | stock_info: 삼전(줄임말) | PASS |
| 4 | stock_info: 005930(코드) | PASS |
| 5 | stock_info: 상승률 상위 | PASS |
| 6 | market_briefing: VKOSPI+외국인+5일추이 | PASS |
| 7 | portfolio_status: 목표+카드+포지션 | PASS |
| 8 | stock_info: 거래량 상위 | PASS |

## 응답 예시 (삼성전자)

```
📊 **삼성전자** (005930)
시장: KOSPI | 섹터: 통신 및 방송 장비 제조업
시가총액: 11839276억원 | 시총순위: -위

💰 최근 종가: 203,500원 (20260225)
전일대비: 🔺 +3,500원 (+1.75%)
거래량: 26,061,306주

📈 펀더멘털: PER: 30.5 | PBR: 3.13 | EPS: 6,564원 | BPS: 63,997원 | ROE: 10.3% | 대출잔고: 0.3%

👥 수급 (최근 3일)
  기관 연속매수: 6일째
  2026-02-24: 외국인 -2,294,251주 | 기관 +3,776,093주
  2026-02-23: 외국인 -5,936,436주 | 기관 +754,361주
  2026-02-20: 외국인 -10,839,769주 | 기관 +3,427,880주
```
