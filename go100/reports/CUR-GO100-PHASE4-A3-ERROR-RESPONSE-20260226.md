# CUR-GO100-PHASE4-A3-ERROR-RESPONSE 보고서 (2026-02-26)

## 개요
에러 발생 시 무미건조한 "오류가 발생했습니다" 대신 **사용자 친화적 메시지 + 다음 액션 제안**으로 전면 개선.

## 구현 요약

### 1. 에러 유형별 응답 표준 (response_formatter.py)
- **ERROR_RESPONSES** 13종 추가: `stock_not_found`, `no_portfolio`, `no_goal`, `no_trades`, `no_backtest`, `no_strategy_cards`, `card_not_found`, `db_error`, `llm_error`, `market_closed`, `screening_unavailable`, `sector_not_found`, `compare_need_two`
- **format_error(error_type, **kwargs)** 함수: 템플릿 포맷 및 KeyError 방어

### 2. ai_router.py 핸들러 적용
| 핸들러 | 적용 내용 |
|--------|-----------|
| _handle_stock_info | identify_stock 실패 → format_error("stock_not_found", query=message); 상위 종목 없음 → db_error |
| _handle_portfolio_status | 카드 0건 → no_strategy_cards; 목표 없음 → no_goal |
| _handle_trade_history | 거래 0건 → no_trades(days=30) |
| _handle_backtest_status | 카드 지정 시 결과 없음 → card_not_found(card_id); 사용자 결과 없음 → no_backtest |
| _handle_risk_check | 카드 없음 → no_strategy_cards |
| _handle_strategy_explain | 카드 없음 → no_strategy_cards; 카드 못찾음 → card_not_found(card_id) |
| _handle_compare_strategies | 카드 2개 미만 → compare_need_two; 지정 카드 못찾음 → card_not_found |
| _handle_sector_analysis | data.error → sector_not_found(sector=message) |
| _handle_stock_screening | 조건 미지원/요청≠실행 → screening_unavailable(condition=requested_label) |

### 3. 글로벌 try-except 개선
- 인텐트별 except 전부 **format_error("db_error")** 사용 (help, optimizer, goal_setup 1턴, stock_info, market_briefing, portfolio_status, stock_screening, sector_analysis, trade_history, backtest_status, risk_check, strategy_explain, compare_strategies)
- **GET /task/{task_id}** error 시 reply_to_user → format_error("db_error")
- 최적화 실패 시 reply → format_error("db_error"); 카드 없음 → no_strategy_cards

### 4. llm_router.py C2SC 인터셉터
- **_try_data_backed_response** except 시 **return format_error("llm_error")** (기존 None → LLM 폴백 대신 사용자에게 안내 메시지 반환)

### 5. data_queries.py 에러 처리 강화
- **logger** 추가 및 전 함수 **try-except** 적용, 실패 시 None/빈 리스트/빈 dict 반환 + **logger.error(..., exc_info=True)** 또는 **logger.error(...)**
- 대상: identify_stock, get_stock_ohlcv, get_stock_fundamentals, get_investor_flow, get_market_regime, get_index_data, get_user_portfolio, get_user_goal, get_positions_count, get_top_stocks, get_sector_stats, get_trade_history(기존 except에 logger 추가), get_backtest_results, get_strategy_detail, get_portfolio_risk, get_cards_for_compare, get_latest_card_id_for_user, get_backtest_result_detail, get_strategy_card_for_optimize

## 검증
- `systemctl restart go100` 후 에러 시나리오 테스트는 배포 환경에서 Bearer 토큰으로 진행 권장.
- 예상 결과:
  1. 존재하지 않는 종목 "가나다라 얼마야" → "🔍 '가나다라' 종목을 찾지 못했어요..."
  2. 백테스트 결과 없는 사용자 "백테스트 결과 보여줘" → "📊 아직 백테스트 결과가 없어요..."
  3. 전략 비교 카드 번호 누락 "전략 비교해줘" → "⚖️ 전략 비교를 위해 2개 카드 번호가 필요해요..."

## 변경 파일
- backend/app/services/go100/ai/response_formatter.py
- backend/app/routers/go100/ai_router.py
- backend/app/api/v1/llm_router.py
- backend/app/services/go100/ai/data_queries.py

## 백업
- /root/backup/go100-routers-phase4-a3-*
- /root/backup/go100-ai-services-phase4-a3-*
