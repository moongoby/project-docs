# [GO100] P1-4: 시드 데이터 생성 및 기존 전략카드 백테스트 실행

**작성일**: 2026-02-27  
**작업 ID**: CUR-GO100-P1-4-SEED-DATA-BACKTEST

## 1. 선행 조건 점검

| 항목 | 결과 |
|------|------|
| DB_SCHEMA.md 참조 | project-docs/go100/DB_SCHEMA.md 기준 |
| go100_strategy_cards | 실제 DB: user_id=2 카드 없음 → 시드 카드 3건 생성(35,36,37) |
| go100_backtest_runs | 실행 전 13건, user_id=2 기준 시드 런 추가 |

## 2. 수행 내용

### 2.1 1단계: DB 현황 확인

```bash
source /root/kis-autotrade-v4/venv/bin/activate
export PYTHONPATH=/root/kis-autotrade-v4/backend
export PGPASSWORD="${DB_PASSWORD:-[DB-PASSWORD]}"

psql -h localhost -U kis_admin -d kisautotrade -c "SELECT go100_card_id, strategy_name, user_id, card_status, is_active FROM go100_strategy_cards WHERE user_id = 2;"
psql -h localhost -U kis_admin -d kisautotrade -c "SELECT COUNT(*) FROM go100_backtest_runs;"
psql -h localhost -U kis_admin -d kisautotrade -c "SELECT COUNT(*) FROM go100_strategy_portfolios WHERE user_id = 2;"
psql -h localhost -U kis_admin -d kisautotrade -c "SELECT COUNT(*) FROM go100_goals WHERE user_id = 2;"
```

### 2.2 2단계: 기본 목표(goal) 생성

- **테이블**: `go100_goals` (스키마: goal_engine 기준 — goal_name, initial_capital, target_capital, target_years, required_cagr, risk_appetite, plan_phases, monte_carlo_result, status 등)
- **처리**: 스크립트 `run_seed_backtest.py` 내 `ensure_goal()`에서 user_id=2에 대해 1건 INSERT (기존 건 있으면 스킵).
- **값**: goal_name='백억이 기본 목표', initial_capital=100,000,000, target_capital=115,000,000(15%), target_years=12, required_cagr=15, risk_appetite='AGGRESSIVE', status='PLANNING'.

### 2.3 3단계: 기본 포트폴리오 생성

- **테이블**: `go100_strategy_portfolios` (029 마이그레이션 — portfolio_name, total_capital, status).
- **처리**: `ensure_strategy_portfolio()`에서 user_id=2에 '백억이 기본 포트폴리오', total_capital=100,000,000, status='ACTIVE' 1건 INSERT (기존 건 있으면 스킵).
- **참고**: `go100_portfolios`(020)는 account_id·go100_card_id 필수이므로, “기본 포트폴리오”는 go100_strategy_portfolios로 생성.

### 2.4 4단계: 전략카드 백테스트 실행

- **스크립트**: `scripts/go100/run_seed_backtest.py` (신규 생성).
- **동작**: user_id=2 활성 카드가 3건 미만이면 시드 카드 3건 생성 후, 카드당 `Go100BacktestService.create_backtest_run` → `execute_backtest` 호출.
- **파라미터**: start_date=2025-01-02, end_date=2026-02-26, initial_capital=10,000,000.
- **실행 예**:
  ```bash
  cd /root/kis-autotrade-v4
  source venv/bin/activate
  export PYTHONPATH=/root/kis-autotrade-v4/backend
  python scripts/go100/run_seed_backtest.py
  ```
- **결과 저장**: `go100_backtest_runs`에 run_id별로 total_return, annualized_return, max_drawdown, status(COMPLETED/FAILED) 등 저장.

### 2.5 5단계: 결과 확인 쿼리

```sql
-- 백테스트 런 (user_id=2 기준 최근)
SELECT id, go100_card_id, strategy_name, total_return, annualized_return, max_drawdown, status
FROM go100_backtest_runs
WHERE user_id = 2
ORDER BY id;

-- 포트폴리오·목표
SELECT * FROM go100_strategy_portfolios WHERE user_id = 2;
SELECT * FROM go100_goals WHERE user_id = 2;
```

### 2.6 6단계: 전략카드 상태 업데이트

- **처리**: `run_seed_backtest.py` 종료 시 자동 실행.
- **로직**: COMPLETED 백테스트가 있는 카드에 대해 `card_status = 'BACKTESTED'`, 최신 COMPLETED run 기준 `total_return > 0` 이고 `max_drawdown > -25` 이면 `is_featured = true`.

## 3. 완료 조건 체크리스트

| 조건 | 상태 |
|------|------|
| go100_goals 1건 이상 (user_id=2) | ✅ (기존 건으로 스킵 또는 1건 INSERT) |
| go100_strategy_portfolios 1건 이상 (user_id=2) | ✅ 1건 INSERT |
| go100_backtest_runs 3건 COMPLETED (user_id=2) | ⏳ 스크립트 실행 중(카드 35 첫 런 RUNNING 후 36, 37 순차 실행) |
| 각 백테스트에 total_return, max_drawdown 값 존재 | ⏳ COMPLETED 건에 한해 저장됨 |

## 4. 산출물

- **스크립트**: `/root/kis-autotrade-v4/scripts/go100/run_seed_backtest.py`
- **보고서**: 본 문서 `project-docs/go100/reports/CUR-GO100-P1-4-SEED-DATA-BACKTEST-20260227.md`

## 5. 참고

- 백테스트 구간이 길면(예: 2025-01-02 ~ 2026-02-26) 카드당 수 분 소요될 수 있음. 3카드 순차 실행이므로 전체 완료까지 시간이 걸릴 수 있음.
- 시드 카드(entry_rules/exit_rules/universe_filter 비어 있음)는 유니버스가 비어 있으면 거래 0건으로 COMPLETED 처리되며, total_return=0, max_drawdown=0 등으로 저장됨.
- 기존에 user_id=2용 전략카드가 이미 3건 이상 있으면 시드 카드는 생성하지 않고 해당 카드들에 대해 백테스트만 실행함.
