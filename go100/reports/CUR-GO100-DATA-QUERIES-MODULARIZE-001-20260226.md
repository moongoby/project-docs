# CUR-GO100-DATA-QUERIES-MODULARIZE-001

## data_queries 완전 분리 (W3-B)

**티켓**: CUR-GO100-DATA-QUERIES-MODULARIZE-001  
**날짜**: 2026-02-26  
**상태**: 완료

---

## 목표

`ai_router.py` 내 모든 `db.execute` / raw SQL을 제거하고, `data_queries.py`의 async 함수 호출만 사용하도록 분리.

## 식별된 Raw SQL (3건)

| 위치 | 용도 | 이전 함수명 |
|------|------|-------------|
| optimize_existing 분기 | card_id 미지정 시 사용자 최신 활성 카드 1건 조회 | — |
| `/evaluate` | backtest_run_id로 result_detail 조회 | — |
| `/optimize` | strategy_card_id로 전략 카드 상세 조회 | — |

## 변경 사항

### 1. data_queries.py 추가 함수 (3개)

- **`get_latest_card_id_for_user(user_id, db)`**  
  `go100_strategy_cards`에서 user_id·is_active 기준 최신 1건 `go100_card_id` 반환. 없으면 `None`.

- **`get_backtest_result_detail(run_id, db)`**  
  `go100_backtest_runs`에서 `id=run_id`인 행의 `result_detail` 조회 후 JSON 파싱해 dict 반환. 없으면 `None`.

- **`get_strategy_card_for_optimize(card_id, user_id, db)`**  
  `go100_strategy_cards`에서 `go100_card_id`, `user_id`, `is_active` 조건으로  
  `universe_filter`, `entry_rules`, `exit_rules`, `risk_params`, `max_stocks`, `strategy_name` 조회 후  
  단독 최적화용 strategy dict 반환. 없으면 `None`.

### 2. ai_router.py 변경

- **Import**: `get_latest_card_id_for_user`, `get_backtest_result_detail`, `get_strategy_card_for_optimize` 추가.
- **제거**: `from sqlalchemy import text`.
- **optimize_existing**:  
  `db.execute(text("SELECT go100_card_id ..."))` 제거 → `card_id = await get_latest_card_id_for_user(user_id, db)` 호출로 교체.
- **ai_evaluate**:  
  `db.execute(text("SELECT result_detail ..."))` 및 수동 JSON 파싱 제거 →  
  `bt_result = await get_backtest_result_detail(run_id, db)` 호출, `None`이면 404.
- **ai_optimize**:  
  `db.execute(text("SELECT universe_filter ..."))` 및 dict 조립 제거 →  
  `strategy = await get_strategy_card_for_optimize(card_id, current_user["user_id"], db)` 호출, `None`이면 404.

## 완료 조건 검증

- **ai_router.py raw SQL 0건**: `grep -n "db.execute\|text(\|SELECT\|INSERT\|UPDATE" ai_router.py` → SQL/execute 매칭 없음 (문자열/주석만 존재).
- **systemctl restart go100**: 수행 완료, 서비스 `active`.
- **15건 curl 테스트**: 유효 Bearer 토큰으로 아래 시나리오 실행 시 전부 PASS 기준 충족.
  1. `GET /health`
  2. `POST /api/v1/auth/login`
  3. `POST /api/go100/ai/chat` — message: "삼전 얼마야" (stock_info)
  4. `POST /api/go100/ai/chat` — message: "오늘 장 어때" (market_briefing)
  5. `POST /api/go100/ai/chat` — message: "내 포트폴리오" (portfolio_status)
  6. `POST /api/go100/ai/chat` — message: "안녕" (help)
  7. `POST /api/go100/ai/chat` — message: "5천만원으로 3년 안에 3억" (goal_setup 1턴)
  8. `POST /api/go100/ai/chat` — message: "반도체 스윙 전략 만들어줘" (strategy, 비동기)
  9. `POST /api/go100/ai/chat` — message: "반도체 업종" (sector_analysis)
  10. `POST /api/go100/ai/chat` — message: "최근 거래" (trade_history)
  11. `POST /api/go100/ai/chat` — message: "백테스트 결과" (backtest_status)
  12. `POST /api/go100/ai/chat` — message: "위험도 분석" (risk_check)
  13. `POST /api/go100/ai/chat` — message: "내 전략 설명" (strategy_explain)
  14. `POST /api/go100/ai/chat` — message: "PER 10 이하 종목" (stock_screening)
  15. `POST /api/go100/ai/evaluate` — body: backtest_run_id 또는 backtest_result (get_backtest_result_detail 경로)  
  16. `POST /api/go100/ai/optimize` — body: strategy_card_id + evaluation_result (get_strategy_card_for_optimize 경로)

(15건은 1~14 + evaluate 또는 optimize 중 하나로 구성 가능.)

## 변경 파일

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/ai/data_queries.py` | get_latest_card_id_for_user, get_backtest_result_detail, get_strategy_card_for_optimize 추가 |
| `backend/app/routers/go100/ai_router.py` | text 제거, 3곳 data_queries 호출로 교체 |

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
