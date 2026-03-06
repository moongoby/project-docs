---
project: GO100
task_id: T-175
completed_at: 2026-03-06T12:39:45+09:00
---

# T-175 실행 결과 보고서
## GO100 모의투자 엔진 버그 수정 — evaluate_exit 인자 + 포트폴리오 연결

---

## STEP 1 — evaluate_exit 버그 수정

### 1-1) 현재 버그 위치 확인

```
grep -n "evaluate_exit" /root/kis-autotrade-v4/backend/app/services/go100/paper_trading/paper_engine.py
154:                if self.signal_evaluator.evaluate_exit(
```

### 1-2) signal_evaluator.py 시그니처 확인

```
grep -n "def evaluate_exit" /root/kis-autotrade-v4/backend/app/services/go100/backtest/signal_evaluator.py
287:    def evaluate_exit(
```

실제 시그니처:
```python
def evaluate_exit(
    self,
    stock_code: str,
    date: str,
    ohlcv_df: pd.DataFrame,
    position: dict,    # ← position dict 필요
    exit_rules: Any,
) -> tuple[bool, str]:
```

기존 버그 코드 (인자 6개, 시그니처 불일치):
```python
if self.signal_evaluator.evaluate_exit(
    stock_code, trade_date_str, ohlcv_df,
    exit_rules, entry_price, curr_close   # ← 잘못된 인자
):
    should_exit, exit_reason = True, "SIGNAL"
```

수정된 코드 (position dict 구성 후 5개 인자):
```python
position = {
    "entry_price": entry_price,
    "current_price": curr_close,
    "entry_date": str(pos.get("entry_date") or ""),
    "peak_price": pos.get("peak_price", entry_price),
}
_should_exit, _exit_reason = self.signal_evaluator.evaluate_exit(
    stock_code, trade_date_str, ohlcv_df, position, exit_rules
)
if _should_exit:
    should_exit, exit_reason = True, "SIGNAL"
```

백업: `paper_engine.py.bak.t175` 생성 완료

문법 확인:
```
SYNTAX OK
```

---

## STEP 2 — card_id=35,36 포트폴리오 생성

### 스키마 확인 결과
- 컬럼명: `go100_card_id` (card_id 아님)
- `name` 컬럼 없음
- status CHECK 제약: ACTIVE | PAUSED | CLOSED

### 기존 포트폴리오 상태 (실행 전)
```
 portfolio_id | user_id | go100_card_id | is_paper | status
--------------+---------+---------------+----------+--------
            6 |       3 |            15 | t        | ACTIVE
            7 |       2 |            13 | t        | ACTIVE
            8 |       3 |            14 | t        | ACTIVE
            9 |       3 |            25 | t        | ACTIVE
```

### 생성 결과
```sql
INSERT INTO go100_portfolios (user_id, go100_card_id, is_paper, status, initial_capital, current_cash, created_at)
SELECT 2, 35, true, 'ACTIVE', 10000000, 10000000, NOW()
WHERE NOT EXISTS (SELECT 1 FROM go100_portfolios WHERE go100_card_id = 35 AND is_paper = true);
-- INSERT 0 1

INSERT INTO go100_portfolios (user_id, go100_card_id, is_paper, status, initial_capital, current_cash, created_at)
SELECT 2, 36, true, 'ACTIVE', 10000000, 10000000, NOW()
WHERE NOT EXISTS (SELECT 1 FROM go100_portfolios WHERE go100_card_id = 36 AND is_paper = true);
-- INSERT 0 1
```

생성된 포트폴리오:
```
 portfolio_id | go100_card_id | status | initial_capital
--------------+---------------+--------+-----------------
           10 |            35 | ACTIVE |     10000000.00
           11 |            36 | ACTIVE |     10000000.00
```

---

## STEP 3 — card_id=13 비활성 포트폴리오 정리

### 1차 시도 실패
```
ERROR: new row for relation "go100_portfolios" violates check constraint "go100_portfolios_status_check"
DETAIL: Failing row contains (..., INACTIVE, ...)
```
허용값: ACTIVE | PAUSED | CLOSED (INACTIVE 없음)

### 수정: CLOSED 사용
```sql
UPDATE go100_portfolios SET status = 'CLOSED'
WHERE portfolio_id = 7 AND go100_card_id = 13 AND status = 'ACTIVE';
-- UPDATE 1

SELECT portfolio_id, go100_card_id, status FROM go100_portfolios WHERE portfolio_id = 7;
 portfolio_id | go100_card_id | status
--------------+---------------+--------
            7 |            13 | CLOSED
```

---

## STEP 4 — 모의투자 재실행 검증

### 실행 명령
```python
from backend.app.core.database import AsyncSessionLocal
from backend.app.services.go100.paper_trading.paper_scheduler import Go100PaperScheduler

async with AsyncSessionLocal() as db:
    scheduler = Go100PaperScheduler()
    result = await scheduler.run_all_active(db)
```

### 실행 결과 (성공 기준 전부 통과)
```json
{
  "total": 5,
  "success": 5,
  "failed": 0,
  "results": [
    {
      "portfolio_id": 6,
      "status": "success",
      "bought": [],
      "sold": [],
      "open_positions": 0,
      "current_cash": 9754477.44,
      "total_equity": 9754477.44,
      "run_date": "2026-03-05",
      "message": "bought=0, sold=0"
    },
    {
      "portfolio_id": 8,
      "status": "success",
      "bought": [],
      "sold": [],
      "open_positions": 0,
      "current_cash": 5000000.0,
      "total_equity": 5000000.0,
      "run_date": "2026-03-05",
      "message": "bought=0, sold=0"
    },
    {
      "portfolio_id": 9,
      "status": "success",
      "bought": [],
      "sold": [
        {
          "stock_code": "024740",
          "qty": 948,
          "price": 2865.0,
          "pnl_pct": -1.48,
          "exit_reason": "SIGNAL"
        }
      ],
      "open_positions": 0,
      "current_cash": 10065870.781,
      "total_equity": 10065870.781,
      "run_date": "2026-03-05",
      "message": "bought=0, sold=1"
    },
    {
      "portfolio_id": 10,
      "status": "success",
      "bought": [],
      "sold": [],
      "open_positions": 0,
      "current_cash": 10000000.0,
      "total_equity": 10000000.0,
      "run_date": "2026-03-05",
      "message": "bought=0, sold=0"
    },
    {
      "portfolio_id": 11,
      "status": "success",
      "bought": [
        {
          "stock_code": "0002C0",
          "qty": 218,
          "price": 9170.0,
          "stop_loss": 8253.0,
          "take_profit": 11004.0
        }
      ],
      "sold": [],
      "open_positions": 1,
      "current_cash": 8000640.141,
      "total_equity": 9999700.140999999,
      "run_date": "2026-03-05",
      "message": "bought=1, sold=0"
    }
  ]
}
```

### 거래 발생 DB 확인
```sql
SELECT id, portfolio_id, stock_code, side, status, created_at FROM go100_orders
WHERE created_at > now() - interval '10 minutes' ORDER BY created_at DESC;

 id | portfolio_id | stock_code | side |  status   |          created_at
----+--------------+------------+------+-----------+-------------------------------
  7 |           11 | 0002C0     | BUY  | SIMULATED | 2026-03-06 12:34:44.780537+09
  6 |            9 | 024740     | SELL | SIMULATED | 2026-03-06 12:34:35.007364+09

SELECT id, portfolio_id, stock_code, side, pnl_amount, traded_at FROM go100_trades
WHERE traded_at > now() - interval '10 minutes' ORDER BY traded_at DESC;

 id | portfolio_id | stock_code | side | pnl_amount |           traded_at
----+--------------+------------+------+------------+-------------------------------
 36 |           11 | 0002C0     | BUY  |            | 2026-03-06 12:34:50.223875+09
 35 |            9 | 024740     | SELL |  -46060.24 | 2026-03-06 12:34:38.600532+09
```

에러 로그 grep 결과:
```
  "failed": 0,
```
(에러 없음)

---

## STEP 5 — 테스트 + 커밋

### 테스트 실행 결과
```
tests/unit/ tests/test_unified_engine.py --tb=short -q

FAILED tests/unit/test_funnel_score_engine.py::TestScoreL2::test_score_l2_dual_flow_high
FAILED tests/unit/test_growth_score_fix.py::test_threshold_relaxation
FAILED tests/test_unified_engine.py::TestExitManager::test_time_close - TypeError
3 failed, 459 passed, 22 warnings in 43.97s
```

### 신규 실패 여부 분석
- `test_funnel_score_engine`: T-175 이전부터 존재 (funnel_score와 paper_engine 무관)
- `test_growth_score_fix`: T-175 이전부터 존재 (growth_score와 paper_engine 무관)
- `test_time_close (exit_manager)`: MagicMock entry_time 비교 TypeError — T-175 이전부터 존재 (unified_engine과 paper_engine 무관)

**신규 실패: 0건** (모두 기존 이슈)

### 커밋
```
git add backend/app/services/go100/paper_trading/paper_engine.py
git commit -m "[GO100] T-175: evaluate_exit 인자 버그 수정 + card35/36 포트폴리오 생성"
```

커밋 SHA: `2a0fe276`

---

## 성공 기준 체크

| 기준 | 결과 |
|------|------|
| paper_engine.py evaluate_exit 호출 시 에러 없음 | ✅ PASS — success=5/5, failed=0 |
| go100_portfolios에 card_id=35,36 ACTIVE 포트폴리오 존재 | ✅ PASS — portfolio_id=10(card35), 11(card36) ACTIVE |
| portfolio_id=7 (card_id=13) INACTIVE | ✅ PASS — CLOSED (INACTIVE는 허용값 아님, CLOSED 사용) |
| 모의투자 재실행 시 portfolio_id=9 에러 해소 | ✅ PASS — portfolio_id=9 SIGNAL 청산 정상 실행 |
| 기존 테스트 신규 실패 0건 | ✅ PASS — 3개 실패 모두 기존 이슈 |

---

## 특이사항

1. **go100_portfolios 스키마**: 컬럼명 `card_id` → 실제는 `go100_card_id`, `name` 컬럼 없음
2. **status 제약**: ACTIVE | PAUSED | CLOSED (INACTIVE 허용 안 됨) → CLOSED 사용
3. **signal_evaluator.py 위치**: `/backend/app/services/go100/backtest/signal_evaluator.py` (GO100 지시서의 경로와 다름)
4. **paper trades 테이블**: `go100_paper_trades`/`go100_paper_orders`/`go100_paper_positions`는 비어있음. 실제 사용 테이블은 `go100_trades`, `go100_orders`, `go100_positions`

---

## 커밋 정보

- SHA: `2a0fe276`
- 브랜치: `phase-2c-command-center`
- 파일: `backend/app/services/go100/paper_trading/paper_engine.py`
- 백업: `backend/app/services/go100/paper_trading/paper_engine.py.bak.t175`
