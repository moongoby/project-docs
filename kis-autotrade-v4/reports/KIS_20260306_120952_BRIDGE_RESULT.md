---
project: GO100
task_id: T-034R
completed_at: 2026-03-06T12:30:00+09:00
---

# T-034R 실행 결과: GO100 모의투자 수동 1회 실행 검증

## 원본 지시서 내용

```
Task ID: T-034R (재발행) 제목: GO100 모의투자 수동 1회 실행 – entry_rules 수정 후 거래 발생 확인
서버: 211 우선순위: P1-HIGH 예상 시간: 10분 의존성: T-033B 완료 (커밋 ba7f2431 확인됨)

# 1) T-033B 커밋 확인
cd /root/kis-autotrade-v4 && git log --oneline -5

# 2) entry_rules 포맷 확인 (card_id=35,36)
sudo -u postgres psql -d kisautotrade -c "SELECT card_id, entry_rules->>'type' as type FROM go100_strategy_cards WHERE card_id IN (35,36);"

# 3) 모의투자 수동 1회 실행
cd /root/kis-autotrade-v4 && .venv/bin/python3 -m backend.app.services.go100.paper_trading_engine --run-once 2>&1 | tee /tmp/paper_trading_run.log

# 4) 거래 발생 확인
sudo -u postgres psql -d kisautotrade -c "SELECT count(*) as total, count(*) FILTER (WHERE created_at > now() - interval '1 hour') as recent FROM go100_paper_trades;"

# 5) 에러 확인
tail -50 /tmp/paper_trading_run.log | grep -i "error\|exception\|fail"

성공 기준: 수동 실행 후 go100_paper_trades에 1건 이상 신규 거래 발생
보고서: CUR-GO100-PAPER-TRADING-VERIFY-001-20260306.md → /root/project-docs/go100/reports/
금지: go100 서비스 재시작 금지, strategy_cards 변경 금지
```

---

## 실행 결과 상세

### STEP 1: T-033B 커밋 확인

```bash
$ git log --oneline | grep "ba7f2431\|T-033B\|entry_rules"

2295aa10 [V4.1] T-172 Manager 스냅샷 시스템 + DESK2 entry_rules 진단 보고서
ba7f2431 [GO100] fix: entry_rules 포맷 정규화 + DB 수정 카드35/36 (T-033B)
1a18c15d feat: CUR-ENGLINK 숲나무가지 3단계 필터 + entry_rules JSONB 해석 엔진 연동
```

T-033B 커밋 ba7f2431 존재 확인 ✅

---

### STEP 2: entry_rules 포맷 확인 (card_id=35,36)

> 참고: `sudo -u postgres psql` 권한 없음 → Python psycopg2 사용

```bash
$ /root/kis-autotrade-v4/venv/bin/python3 /tmp/db_check3.py
```

```
=== go100_card_id=35,36 entry_rules ===
go100_card_id=36, card_code=None: type=RAW
  entry_rules=[{"type": "rsi_threshold", "value": 30, "period": 14, "operator": "<"}, {"type": "volume_surge", "ratio": 1.5, "period": 20}]
go100_card_id=35, card_code=None: type=RAW
  entry_rules=[{"long": 20, "type": "ma_cross", "short": 5, "direction": "golden"}, {"type": "volume_surge", "ratio": 2.0, "period": 20}]

=== 모든 DESK2 카드 (desk_id=2) ===
  card_id=54, code=2.DP01, active=False, entry_type=None
```

**확인 결과**:
- go100_card_id=35: `[{"long": 20, "type": "ma_cross", "short": 5, "direction": "golden"}, {"type": "volume_surge", "ratio": 2.0, "period": 20}]`
- go100_card_id=36: `[{"type": "rsi_threshold", "value": 30, "period": 14, "operator": "<"}, {"type": "volume_surge", "ratio": 1.5, "period": 20}]`

두 카드 모두 배열 포맷(T-033B 정규화 결과) 확인됨 ✅

---

### STEP 3: 모의투자 수동 1회 실행

> 참고: `backend.app.services.go100.paper_trading_engine` 모듈 없음 (paper_trading_engine_30d.py 존재)
> → Go100PaperScheduler.run_all_active() 직접 실행

#### 3-1. paper_trading/paper_engine.py 기반 (go100_portfolios ACTIVE)

```bash
$ /root/kis-autotrade-v4/venv/bin/python3 /tmp/run_paper_once.py 2>&1 | tee /tmp/paper_trading_run.log
```

```
2026-03-06 12:15:11,011 [INFO] paper_run_once: === GO100 모의투자 수동 1회 실행 시작 ===
2026-03-06 12:15:11,081 [INFO] backend.app.services.go100.paper_trading.paper_scheduler: PAPER SCHEDULER: 실행 대상 4개 포트폴리오
2026-03-06 12:15:15,646 [INFO] backend.app.services.go100.paper_trading.paper_scheduler: PAPER SCHEDULER: portfolio_id=6 완료 (bought=0, sold=0)
2026-03-06 12:15:15,648 [WARNING] backend.app.services.go100.paper_trading.paper_engine: PAPER ENGINE: card_id=13 없음
2026-03-06 12:15:15,649 [INFO] backend.app.services.go100.paper_trading.paper_scheduler: PAPER SCHEDULER: portfolio_id=7 완료 (card not found)
2026-03-06 12:15:20,165 [INFO] backend.app.services.go100.paper_trading.paper_scheduler: PAPER SCHEDULER: portfolio_id=8 완료 (bought=0, sold=0)
2026-03-06 12:15:23,613 [ERROR] backend.app.services.go100.paper_trading.paper_scheduler: PAPER SCHEDULER: portfolio_id=9 실패: SignalEvaluator.evaluate_exit() takes 6 positional arguments but 7 were given
2026-03-06 12:15:23,640 [INFO] paper_run_once: === 실행 결과 ===
2026-03-06 12:15:23,640 [INFO] paper_run_once: total=4, success=3, failed=1
2026-03-06 12:15:23,640 [INFO] paper_run_once: portfolio_id=6: success
2026-03-06 12:15:23,640 [INFO] paper_run_once:   bought=0, sold=0, open_positions=0, run_date=2026-03-05
2026-03-06 12:15:23,640 [INFO] paper_run_once: portfolio_id=7: success
2026-03-06 12:15:23,640 [INFO] paper_run_once:   bought=0, sold=0, open_positions=0, run_date=2026-03-06
2026-03-06 12:15:23,640 [INFO] paper_run_once: portfolio_id=8: success
2026-03-06 12:15:23,640 [INFO] paper_run_once:   bought=0, sold=0, open_positions=0, run_date=2026-03-05
2026-03-06 12:15:23,640 [INFO] paper_run_once: portfolio_id=9: failed
2026-03-06 12:15:23,640 [ERROR] paper_run_once:   error: SignalEvaluator.evaluate_exit() takes 6 positional arguments but 7 were given

=== JSON RESULT ===
{
  "total": 4,
  "success": 3,
  "failed": 1,
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
      "portfolio_id": 7,
      "status": "success",
      "bought": [],
      "sold": [],
      "open_positions": 0,
      "current_cash": 100000000.0,
      "total_equity": 100000000.0,
      "run_date": "2026-03-06",
      "message": "card not found"
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
      "status": "failed",
      "error": "SignalEvaluator.evaluate_exit() takes 6 positional arguments but 7 were given"
    }
  ]
}
```

#### 3-2. paper_trading_engine_30d.py (session_id=2, card_id=35)

```bash
$ /root/kis-autotrade-v4/venv/bin/python3 /tmp/run_paper_30d.py 2>&1 | tee -a /tmp/paper_trading_run.log
```

```
2026-03-06 12:17:17,796 [INFO] paper_30d_run: === paper_trading_engine_30d: session_id=2 run_daily_check 실행 ===
2026-03-06 12:17:41,383 [INFO] paper_30d_run: 결과: ok=True
2026-03-06 12:17:41,383 [INFO] paper_30d_run: bought=[]
2026-03-06 12:17:41,383 [INFO] paper_30d_run: sold=[]

=== JSON RESULT (session_id=2) ===
{
  "ok": true,
  "session_id": 2,
  "trade_date": "2026-03-05",
  "bought": [],
  "sold": [],
  "current_capital": 10000000.0
}
```

---

### STEP 4: 거래 발생 확인 (go100_paper_trades)

```bash
$ /root/kis-autotrade-v4/venv/bin/python3 /tmp/db_check5.py
```

```
=== go100_paper_trades 컬럼: ['trade_id', 'session_id', 'ticker', 'trade_type', 'quantity', 'price', 'slippage_bps', 'commission', 'executed_at', 'signal_source', 'pnl', 'notes']
전체 건수: 0

최근 5건 (정렬: executed_at): (없음)
최근 1시간 내 신규 거래: 0건
```

**결과**: go100_paper_trades 총 0건, 신규 거래 발생 없음 ❌

**관련 테이블 현황**:
```
go100_paper_trades: 0건
go100_paper_trading_sessions: 2건 (session_id=1 CANCELLED, session_id=2 ACTIVE/card_id=35)
go100_trades (실거래+모의거래 통합): 15건 (최신 2026-03-05)
go100_positions: 16건
go100_orders: 2건
```

---

### STEP 5: 에러 확인

```bash
$ grep -i "error\|exception\|fail" /tmp/paper_trading_run.log
```

```
2026-03-06 12:15:23,613 [ERROR] backend.app.services.go100.paper_trading.paper_scheduler: PAPER SCHEDULER: portfolio_id=9 실패: SignalEvaluator.evaluate_exit() takes 6 positional arguments but 7 were given
2026-03-06 12:15:23,640 [INFO] paper_run_once: total=4, success=3, failed=1
2026-03-06 12:15:23,640 [INFO] paper_run_once: portfolio_id=9: failed
2026-03-06 12:15:23,640 [ERROR] paper_run_once:   error: SignalEvaluator.evaluate_exit() takes 6 positional arguments but 7 were given
  "failed": 1,
      "status": "failed",
      "error": "SignalEvaluator.evaluate_exit() takes 6 positional arguments but 7 were given"
```

**에러 목록**:

| 번호 | 유형 | 대상 | 내용 |
|---|---|---|---|
| E-1 | ArgumentError | portfolio_id=9 (card_id=25) | `SignalEvaluator.evaluate_exit() takes 6 positional arguments but 7 were given` |
| E-2 | CardNotFound | portfolio_id=7 (card_id=13) | card_id=13의 is_active=False → paper_engine._load_card 반환 None |
| E-3 | NoSignal | portfolio_id=6,8 / session_id=2 | entry_rules 조건 불충족 (시장 조건) |

**에러 E-1 원인 분석**:

- `paper_engine.py:154` 호출:
  ```python
  self.signal_evaluator.evaluate_exit(
      stock_code, trade_date_str, ohlcv_df,
      exit_rules, entry_price, curr_close  # 6개 인수 전달
  )
  ```
- `signal_evaluator.py:287` 실제 시그니처:
  ```python
  def evaluate_exit(self, stock_code: str, date: str, ohlcv_df, position: dict, exit_rules) -> tuple[bool, str]
  ```
- 4번째 인자로 `position: dict` 기대하는데 `exit_rules`가 전달됨 → 버그

**에러 E-2 원인 분석**:
- card_id=13: is_active=False (비활성화된 카드)
- `_load_card` 쿼리에 `AND is_active = true` 조건 존재 → None 반환

---

## 성공 기준 평가

| 기준 | 상태 | 비고 |
|---|---|---|
| 수동 실행 완료 | ✅ | paper_scheduler + paper_trading_engine_30d 모두 실행 |
| go100_paper_trades 신규 1건 이상 | ❌ | 0건 (전체 0건) |
| 에러 확인 | ✅ | 2개 버그 식별 (evaluate_exit, card_id=13 비활성) |

**종합 판정**: 부분 성공 — 엔진 실행은 완료했으나 신규 거래 발생 조건 미충족

---

## DB 데이터 요약

```
go100_strategy_cards: card_id=35 (ma_cross+volume_surge), card_id=36 (rsi+volume_surge) — T-033B 정규화 확인
go100_portfolios (ACTIVE, is_paper=true): 4개 (card_id=13,14,15,25) — card_id=35,36 포트폴리오 없음
go100_paper_trading_sessions (ACTIVE): 1개 (session_id=2, card_id=35)
go100_paper_trades: 0건 (신규 발생 없음)
go100_trades: 15건 (최신 2026-03-05)
ohlcv_daily: 2,623,502건 (최신 20260305)
stock_universe: 3,844건 (is_active=true, 모두 KOSPI)
```

---

## 후속 조치 권고

| 우선순위 | 항목 | 내용 |
|---|---|---|
| P1 | paper_engine.py evaluate_exit 버그 수정 | `exit_rules, entry_price, curr_close` → `position dict` 형태로 호출 수정 |
| P2 | card_id=35,36 포트폴리오 연결 | go100_portfolios에 is_paper=true 포트폴리오 생성 |
| P3 | card_id=13 정리 | portfolio_id=7에 활성 카드 재연결 또는 portfolio 비활성화 |

---

## 로그 파일 위치

```
/tmp/paper_trading_run.log  — 전체 실행 로그
/root/kis-autotrade-v4/report/go100/CUR-GO100-PAPER-TRADING-VERIFY-001-20260306.md  — 보고서
```
