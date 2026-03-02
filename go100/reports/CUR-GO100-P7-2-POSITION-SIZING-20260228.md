# CUR-GO100-P7-2-POSITION-SIZING-20260228

**제목:** P7-2 동적 포지션 사이징 엔진 + CEO 지시 1번 구현  
**작성일:** 2026-02-28  
**상태:** 완료

---

## [인계 확인]

```
직전 완료: P7-1-QA-V2, P6-EXTRA-VERIFY-V2
현재 단계: P7-2 포지션 사이징 (CEO 지시 1번)
CEO 지시 적용: 동적 포지션 사이징, MFE 기반, +3% 50% 익절, D2/D4 60/40
```

---

## 1. 개요

- **목적:** CEO 지시 1번 — 동적 포지션 사이징(MFE 기반, +3% 시 50% 익절, 전략 배분 D2 60% / D4 40%) 구현.
- **구성:** DB 마이그레이션 048, position_sizing_engine, Agent 도구 2개, KIS execute_buy 연동, 테스트 스크립트.

---

## 2. DB Migration 048

**파일:** `backend/migrations/048_go100_position_sizing.sql`

- **테이블:** `go100_position_sizing`
  - id, user_id, strategy_id(FK go100_strategy_cards), sizing_method(FIXED/MFE_BASED/KELLY/ATR_BASED)
  - base_allocation_pct, max_allocation_pct, take_profit_pct, take_profit_ratio, stop_loss_pct
  - strategy_weight (JSONB), mfe_lookback_days, is_active, created_at, updated_at
- **인덱스:** idx_go100_position_sizing_user, idx_go100_position_sizing_strategy

적용: `sudo -u postgres psql -d kisautotrade -f backend/migrations/048_go100_position_sizing.sql`

---

## 3. 포지션 사이징 엔진

**파일:** `backend/app/services/go100/position_sizing_engine.py`

| 함수 | 설명 |
|------|------|
| **calculate_position_size(conn, user_id, strategy_id, ticker, current_price, account_balance)** | MFE 기반 적정 수량. go100_position_sizing 설정 조회, ohlcv_daily에서 mfe_lookback_days MFE 평균, base_allocation_pct × 잔고로 수량 산출. 반환: quantity, method, allocation_pct, mfe_pct, message. |
| **apply_take_profit(conn, user_id, position_id, current_price, entry_price, take_profit_pct, take_profit_ratio)** | 현재가가 매수가 대비 +take_profit_pct 이상이면 take_profit_ratio% 분할 매도 정보 반환 (order_side, ratio_pct, message). |
| **get_strategy_allocation(conn, user_id)** | strategy_weight JSONB 기반 전략별 배분 (예: D2 60%, D4 40%). |
| **setup_default_sizing(conn, user_id)** | CEO 기본: MFE_BASED, base 10%, max 25%, take_profit_pct 3%, take_profit_ratio 50%, stop_loss 5%, strategy_weight {"D2":0.6,"D4":0.4}, mfe_lookback_days 60. |

---

## 4. Agent 도구

- **get_position_sizing:** 현재 포지션 사이징 설정 조회 (strategy_id 선택).
- **set_position_sizing:** sizing_method, base_allocation_pct, max_allocation_pct, take_profit_pct, take_profit_ratio, stop_loss_pct, strategy_weight, mfe_lookback_days 변경.

**등록:** `agent_tools.py` (AGENT_TOOLS), `tool_executors.py` (함수 + TOOL_EXECUTORS). 도구 수 48 → 50.

---

## 5. KIS 게이트웨이 연동

- **위치:** `tool_executors.execute_buy`
- **동작:** quantity가 0 또는 미제공 시 `position_sizing_engine.calculate_position_size(conn, user_id, strategy_id, ticker, current_price, account_balance)` 호출로 동적 수량 산출 후 `kis_order_gateway.execute_buy(db, user_id, ticker, quantity, ...)` 호출.
- **순서:** risk_engine.check_pre_trade → (quantity 0이면) position_sizing → KIS order.

---

## 6. 테스트

**스크립트:** `scripts/go100/test_position_sizing.py`

| 단계 | 내용 | 결과 |
|------|------|------|
| 1 | setup_default_sizing(2) → DB 확인 | MFE_BASED, take_profit_pct 3.0, strategy_weight D2/D4 OK |
| 2 | calculate_position_size(삼성전자, 5.5만원, 1억) | quantity 246, allocation_pct 13.6% 등 산출 OK |
| 3 | get_strategy_allocation(2) | D2:0.6, D4:0.4 OK |
| 4 | apply_take_profit(+3% 도달) | order_side SELL, ratio_pct 50% OK |
| 5 | Agent get_position_sizing / set_position_sizing | 호출 정상 |

실행: `cd /root/kis-autotrade-v4 && .venv/bin/python scripts/go100/test_position_sizing.py`

---

## 7. 파일 목록

| 경로 | 변경 |
|------|------|
| backend/migrations/048_go100_position_sizing.sql | 신규 |
| backend/app/services/go100/position_sizing_engine.py | 신규 |
| backend/app/services/go100/ai/agent_tools.py | get_position_sizing, set_position_sizing 추가 |
| backend/app/services/go100/ai/tool_executors.py | 위 2개 실행 함수, execute_buy 동적 수량 분기, TOOL_EXECUTORS 등록 |
| scripts/go100/test_position_sizing.py | 신규 |

---

## 8. Git

- **보고서 push:**  
  `cd /root/project-docs && git add go100/reports/CUR-GO100-P7-2-POSITION-SIZING-20260228.md && git commit -m "[GO100] P7-2: 동적 포지션 사이징 엔진 + CEO 지시 1번 구현 (20260228)" && git push origin master`
- **코드 레포:**  
  `cd /root/kis-autotrade-v4 && git add backend/migrations/048_go100_position_sizing.sql backend/app/services/go100/position_sizing_engine.py backend/app/services/go100/ai/agent_tools.py backend/app/services/go100/ai/tool_executors.py scripts/go100/test_position_sizing.py && git commit -m "[GO100] P7-2: 동적 포지션 사이징 엔진 + Agent 도구 + execute_buy 연동"`
