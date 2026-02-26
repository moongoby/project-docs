# CUR-GO100-INTENT-EXPANSION-001

## W3-A: 인텐트 9개 → 15개 확장

**날짜**: 2026-02-26  
**티켓**: CUR-GO100-BAEKOGI-WAVE3-MAIN (W3-A)  
**상태**: 완료

---

## 작업 요약

백억이(GO100 AI) C2SC 인텐트를 9개에서 **15개**로 확장하고, 신규 6개 인텐트에 대한 DB 조회 함수 및 핸들러를 구현함.

## 추가된 인텐트 (6개)

| # | 인텐트명 | 설명 | 우선순위 |
|---|----------|------|----------|
| 1 | sector_analysis | "반도체 업종 어때", "바이오 섹터 동향" → 섹터별 분석 | P1 |
| 2 | trade_history | "최근 거래 내역", "이번 달 수익" → 거래 이력 조회 | P1 |
| 3 | backtest_status | "백테스트 결과 보여줘", "카드 14번 성과" → 백테스트 결과 | P2 |
| 4 | risk_check | "내 포트폴리오 위험도", "최대 손실 얼마" → 리스크 분석 | P2 |
| 5 | strategy_explain | "내 전략 설명해줘", "진입 조건이 뭐야" → 카드 상세 설명 | P2 |
| 6 | compare_strategies | "1번이랑 3번 전략 비교해줘" → 카드 비교 | P3 |

## 변경 파일

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/go100/ai/data_queries.py` | get_sector_stats, get_trade_history, get_backtest_results, get_strategy_detail, get_portfolio_risk, get_cards_for_compare 추가 |
| `backend/app/routers/go100/ai_router.py` | C2SC 15개 인텐트, 키워드 폴백 6종 추가, 핸들러 6개 추가 및 라우팅 |
| `backend/app/api/v1/llm_router.py` | _DATA_BACKED_INTENTS 확장, _try_data_backed_response에 신규 인텐트 분기 추가 |

## C2SC 프롬프트·키워드

- **_C2SC_BASE_PROMPT**: 15개 인텐트 목록 및 설명으로 교체
- **C2SC_VALID_INTENTS**: sector_analysis, trade_history, backtest_status, risk_check, strategy_explain, compare_strategies 추가
- **_keyword_classify**: 섹터/업종, 거래내역, 백테스트, 위험도, 전략설명, 비교 관련 키워드 추가

## data_queries 신규 함수

- **get_sector_stats(db, sector_name=None)**: 섹터별 평균 등락률·대장주 또는 특정 섹터 상위 10종목 (stock_universe + ohlcv_daily)
- **get_trade_history(db, user_id, days=30)**: v4_trade_executions 기반 최근 N일 거래 내역 (accounts → account_id 조회)
- **get_backtest_results(db, card_id=None, user_id=None)**: go100_backtest_runs 조회 (카드별 상세 또는 사용자 전체 요약)
- **get_strategy_detail(db, card_id)**: go100_strategy_cards 1건 (universe_filter, entry_rules, exit_rules, risk_params)
- **get_portfolio_risk(db, user_id)**: 카드별 MDD·stop_loss·배정금액, 위험도 라벨(안전/보통/공격적/매우공격적)
- **get_cards_for_compare(db, card_ids)**: 비교용 카드 2건 + 백테스트 지표

## 검증 포인트

- [ ] 15건 curl 테스트 (기존 9 + 신규 6) PASS
- [ ] llm_router.py 자유대화 탭에서 신규 인텐트 인터셉트 동작
- [ ] sector_analysis "반도체 업종" → 섹터 통계/상위 종목
- [ ] trade_history "최근 거래" → 거래 내역 또는 안내
- [ ] backtest_status → 카드별 백테스트 결과
- [ ] risk_check → 포트폴리오 위험도 분석
- [ ] strategy_explain → 전략 한국어 설명
- [ ] compare_strategies → 카드 비교 테이블

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
