# CUR-GO100-INVEST-AMOUNT-FIX-001 — 사용자 설정값(투자금/비중) 주문 반영

**일시:** 2026-02-23 20:00 KST  
**서버:** root@211.188.51.113  
**작업 ID:** CUR-GO100-INVEST-AMOUNT-FIX-001

---

## 1. 요약

- **문제:** `v4_trade_schedules`의 `invest_amount`, `max_per_stock_pct`가 schedule_runner → `run_strategy()`로 전달되나, 주문 수량은 `sig.target_quantity or 1`로만 결정되어 사용자 설정이 무시됨.
- **원칙:** 사용자 설정값이 항상 최우선(CEO 원칙).
- **조치:** `run_strategy()` 내 주문 수량을 투자금·비중·현재가 기반으로 계산하도록 수정.

---

## 2. 수정 내용

### 2.1 수정 전

- `run_strategy()` 내: `qty = sig.target_quantity or 1`
- 투자금·비중 미반영.

### 2.2 수정 후

- **현재가:** `ohlcv_daily` 최신 종가 조회 함수 `_get_current_price_from_db(stock_code)` 추가. 없으면 `sig.target_price` fallback.
- **수량 공식:**
  - `max_invest_per_stock = invest_amount * (max_per_stock_pct / 100)` (max_per_stock_pct 미설정 시 100% 사용)
  - `calculated_qty = floor(max_invest_per_stock / current_price)`
  - `sig.target_quantity`가 있으면 `final_qty = min(calculated_qty, sig.target_quantity)`, 없으면 `final_qty = calculated_qty`
  - `final_qty <= 0`이면 `final_qty = 1` (fallback)
- **계산 불가 시:** 투자금/현재가 없으면 기존과 동일하게 `qty = sig.target_quantity or 1`, 경고 로그.

### 2.3 변경 파일

- `backend/app/services/auto_trade_engine.py`
  - 상단 `import math` 추가
  - `_get_current_price_from_db(stock_code)` 함수 추가
  - `run_strategy()` 내 buy 신호 루프에서 위 수량 계산 로직 적용, `execute_order(..., schedule_id=schedule.id)` 전달

---

## 3. 테스트 결과

### 3.1 문법

- `python -c "import ast; ast.parse(open('backend/app/services/auto_trade_engine.py').read()); print('✅ 문법 OK')"` → **통과**

### 3.2 수량 계산 단위 테스트 (4케이스)

| 케이스 | 조건 | 기대 | 결과 |
|--------|------|------|------|
| 1 | invest=1천만, pct=100%, price=50,000 | qty=200 | ✅ |
| 2 | invest=5백만, pct=33%, price=100,000 | qty=16 | ✅ |
| 3 | price=0 | fallback qty=1 | ✅ |
| 4 | calculated=200, target_quantity=5 | qty=5 (min) | ✅ |

### 3.3 pytest

- `backend/tests/` 실행: 153 passed, 1 failed (실패 1건은 LLM API 크레딧 관련 `test_design_chat_anthropic`, 본 수정과 무관)

---

## 4. DB·스키마·서비스

- **DB 변경:** 없음
- **strategy_cards:** 변경 없음
- **v4_positions:** 변경 없음
- **서비스:** go100만 재시작 수행. kis-v41-* 재시작 없음(규칙 준수).

---

## 5. 참조

- 지시서: CUR-GO100-INVEST-AMOUNT-FIX-001 (2026-02-23)
- 검증 보고서: [CUR-GO100-TRADE-SETTINGS-VERIFY-001-20260223](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/reports/CUR-GO100-TRADE-SETTINGS-VERIFY-001-20260223.md)
