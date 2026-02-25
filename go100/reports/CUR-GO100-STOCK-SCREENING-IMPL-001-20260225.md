# CUR-GO100-STOCK-SCREENING-IMPL-001 보고서

**작성일**: 2026-02-25 15:30 KST
**우선순위**: P2
**상태**: **완료**

---

## 1. 목표

백억이 채팅에서 종목 스크리닝 기능 구현: 모멘텀 상승, 외국인 연속 순매수, 테마/섹터별 종목 탐색.

## 2. 변경 내역

### 2.1 Backend

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/ai/intent_router.py` | `stock_screening` 인텐트 추가, help/stock_info 오버랩 시 screening 우선 처리 |
| `backend/app/services/go100/screening_engine.py` | **신규** — 3종 스크리닝 엔진 (momentum_up, foreign_buy, theme) |
| `backend/app/routers/go100/ai_router.py` | `_handle_stock_screening()` 핸들러 추가, ai_chat에 stock_screening 분기 추가 |

### 2.2 스크리닝 타입

| 타입 | 조건 | 데이터 소스 |
|------|------|-------------|
| `momentum_up` | 종가 > 5일 MA & 거래량 > 20일 평균 ×1.5 | ohlcv_daily + stock_universe |
| `foreign_buy` | 외국인 연속 순매수 3일 이상 | v4_investor_daily + stock_universe |
| `theme` | 업종별 평균 수익률 상위 3개 / 키워드 검색 | stock_universe + ohlcv_daily |

## 3. Intent Router 우선순위

```
1. optimize_existing
2. help (단, screening/stock_info/market_briefing 키워드 겹침 시 해당 인텐트 우선)
3. goal_setup
4. stock_screening ← 신규
5. stock_info
6. market_briefing
7. portfolio_status
8. strategy (기본값)
```

## 4. 검증 결과

| 테스트 | 입력 메시지 | Agent | 결과 |
|--------|------------|-------|------|
| 모멘텀 | "모멘텀 상승 종목 찾아줘" | STOCK_SCREENING | ✅ 거래량 폭발 종목 10개 표시 |
| 외국인 | "외국인 순매수 종목 알려줘" | STOCK_SCREENING | ✅ 연속 매수 종목 표시 (농심 18일 등) |
| 테마 자동 | "오늘 상승 테마 알려줘" | STOCK_SCREENING | ✅ 상위 3개 섹터 + 관련 종목 |
| 반도체 테마 | "반도체 섹터 종목 추천해줘" | STOCK_SCREENING | ✅ 반도체 제조업 종목 리스트 |
| 종목 정보 | "삼성전자 주가 알려줘" | STOCK_INFO | ✅ 기존 stock_info 정상 동작 |
| 도움말 | "GO100 어떻게 사용하나요?" | HELP | ✅ 기존 help 정상 동작 |

## 보고 요약

- **구현 범위**: intent_router + screening_engine + ai_router 핸들러
- **3종 스크리닝**: momentum_up, foreign_buy, theme
- **인텐트 우선순위**: help와의 키워드 오버랩 해결 (screening 우선)
- **기존 기능 영향**: 없음 (stock_info, help, goal_setup 모두 정상)
