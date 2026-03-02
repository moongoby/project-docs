# CUR-GO100-TRADE-SETTINGS-VERIFY-001 보고서

## 기본 정보
- 작업일: 2026-02-23 17:40 KST
- 서버: root@[SERVER-IP]
- 작업 유형: 읽기 전용 확인 (코드/DB 변경 없음)
- CEO 지시: 자동매매 설정값에 사용자 설정이 실제 반영되어 있는지 확인

---

## 1. 스케줄 DB 테이블 구조

- **실제 사용 테이블**: `v4_trade_schedules` (스크립트에서 가정한 `go100_trade_schedules`는 존재하지 않음)
- 스케줄 관련 테이블 목록(일부): `v4_trade_schedules`, `auto_trade_positions`, `autotrade_positions`, `go100_trades`, `real_trades`, `v4_trade_executions` 등

### v4_trade_schedules 컬럼 구조

| column_name      | data_type                   | is_nullable |
|------------------|-----------------------------|-------------|
| id               | integer                     | NO         |
| user_id          | bigint                      | YES        |
| strategy_id      | integer                     | NO         |
| account_id       | bigint                      | YES        |
| is_active        | boolean                     | YES        |
| run_interval     | character varying           | YES        |
| market_open_only | boolean                     | YES        |
| invest_amount    | numeric                     | YES        |
| max_stocks       | integer                     | YES        |
| max_per_stock_pct| numeric                     | YES        |
| stop_loss_pct    | numeric                     | YES        |
| take_profit_pct  | numeric                     | YES        |
| last_run_at      | timestamp without time zone | YES        |
| next_run_at      | timestamp without time zone | YES        |
| created_at       | timestamp without time zone | YES        |
| updated_at       | timestamp without time zone | YES        |

---

## 2. 활성 스케줄 현황 (스크린샷 vs DB 대조)

### 스크린샷 기준값

| 전략 | 투자금 | 최대종목 | 손절 | 익절 | 비중 | 주기 | 장중만 |
|------|--------|---------|------|------|------|------|--------|
| 전략 #3 | 10,000,000 | 2 | -3% | 50% | 100% | 실시간 | ON |
| [데일리] 대형 우량주 | 5,000,000 | 3 | -5% | +15% | 33% | 1일 | ON |
| (3번째) | 10,000,000 | ? | ? | ? | ? | ? | ? |

### DB 실제 저장값 (v4_trade_schedules, 2026-02-23 조회)

| id | strategy_id | invest_amount | max_stocks | max_per_stock_pct | stop_loss_pct | take_profit_pct | run_interval | market_open_only |
|----|-------------|---------------|------------|-------------------|---------------|-----------------|--------------|------------------|
| 1  | 3  | 10,000,000 | 2 | 100.00 | -3.00 | 50.00 | realtime | t |
| 2  | 14 |  5,000,000 | 3 |  31.00 | -5.00 | 15.00 | daily    | t |
| 3  | 15 | 10,000,000 | 3 | 100.00 | -3.00 | 50.00 | daily    | t |

### 일치 여부

- **id=1 (전략 #3)**: 투자금 1천만, 최대종목 2, 손절 -3%, 익절 50%, 비중 100%, 실시간, 장중만 ON → **스크린샷과 일치**
- **id=2 (대형 우량주 등)**: 투자금 5백만, 최대종목 3, 손절 -5%, 익절 15%, 비중 31%(≈33%), 1일, 장중만 ON → **스크린샷과 일치**
- **id=3**: 투자금 1천만, 최대종목 3, 손절 -3%, 익절 50%, 비중 100%, 1일, 장중만 ON → DB에 정상 저장

---

## 3. 설정값 코드 흐름

### 프론트 → API → DB 저장 경로

1. **프론트**: `frontend/src/components/trade/ScheduleForm.tsx`
   - 필드: `invest_amount`, `max_stocks`, `max_per_stock_pct`, `stop_loss_pct`, `take_profit_pct`, `run_interval`, `market_open_only`
   - 제출 시 `ScheduleCreateRequest` / `ScheduleUpdateRequest`로 전달
2. **API 클라이언트**: `frontend/src/lib/api/trade.ts` → `createSchedule(body)`, `updateSchedule(id, body)`
3. **백엔드**: `backend/app/api/v1/trade_router.py`
   - `POST /api/v1/trade/schedules` → INSERT INTO `v4_trade_schedules` (invest_amount, max_stocks, max_per_stock_pct, stop_loss_pct, take_profit_pct, run_interval, market_open_only 등)
   - `PUT /api/v1/trade/schedules/{id}` → UPDATE `v4_trade_schedules` (동일 컬럼들)

### DB → 실행 로직 적용 경로

1. **스케줄 폴링**: `backend/app/services/schedule_runner.py`
   - `v4_trade_schedules` WHERE is_active = true 조회
   - 행별로 `TradeSchedule` dataclass 생성 (invest_amount, max_stocks, max_per_stock_pct, stop_loss_pct, take_profit_pct, run_interval, market_open_only 포함)
   - `auto_trade_engine.run_strategy(schedule)` 호출
2. **실행 엔진**: `backend/app/services/auto_trade_engine.py`
   - `run_strategy(schedule)`:
     - `schedule.market_open_only` → 장중이 아니면 스킵
     - `schedule.max_stocks` → `params["max_stocks"]`로 전달 → `strategy_signal_generator.generate()`에서 **신호 개수(종목 수) 상한**으로만 사용
     - **주문 수량**: `qty = sig.target_quantity or 1` → **schedule.invest_amount, schedule.max_per_stock_pct 미사용**
   - `check_stop_loss(schedule)` / `check_take_profit(schedule)`:
     - `schedule.stop_loss_pct`, `schedule.take_profit_pct` 사용 → **적용됨**
   - `_update_schedule_run(schedule_id, run_interval)`:
     - `schedule.run_interval`에 따라 next_run_at 계산 → **적용됨**

---

## 4. V4.1 Fund Commander와의 관계

- **GO100 스케줄(v4_trade_schedules)과 Fund Commander**: `backend/app/services/go100/` 내에서 `fund_commander`, `FundCommander`, `fund.*alloc`, `desk.*weight` 검색 결과 **없음**
- **Fund 관련 서비스**: `backend/app/services/fund/`(또는 adaptive/fund_rebalancer)에서 `go100`, `schedule`, `v4_trade_schedules` 참조 **없음**
- **결론**: 트레이드 페이지의 스케줄(v4_trade_schedules)과 V4.1 Fund Commander는 **독립 운영**. GO100 비중 설정이 Fund Commander로 전달되는 경로는 없음.
- 참고: `Go100DailyScheduler`(go100_scheduler.py)는 **go100_portfolios** 기반 실거래/페이퍼 실행이며, **v4_trade_schedules**와는 별도 플로우.

---

## 5. 설정값 항목별 적용 상태

| 설정 항목 | DB 저장 | 실행 시 적용 | 적용 파일:라인 | 비고 |
|----------|---------|-------------|----------------|------|
| 투자금(invest_amount) | Y | **N** | schedule_runner.py:162 전달만, auto_trade_engine.run_strategy에서 미사용 | 주문 수량 계산에 반영 안 됨 |
| 최대 종목 수(max_stocks) | Y | Y | auto_trade_engine.py:551 → strategy_signal params | 신호 종목 수 상한으로만 사용 |
| 종목별 최대 비중(max_per_stock_pct) | Y | **N** | schedule_runner.py:164 전달만, run_strategy에서 미사용 | 주문 수량/비중 계산에 미반영 |
| 손절 라인(stop_loss_pct) | Y | Y | auto_trade_engine.py:629-656 check_stop_loss | 적용됨 |
| 익절 라인(take_profit_pct) | Y | Y | auto_trade_engine.py:658-685 check_take_profit | 적용됨 |
| 신호 주기(run_interval) | Y | Y | auto_trade_engine.py:575-598 _update_schedule_run | next_run_at 계산에 사용 |
| 장중만 실행(market_open_only) | Y | Y | auto_trade_engine.py:536-538 run_strategy | 장외 시 스킵 |

---

## 6. 발견된 이슈 (있을 경우)

1. **투자금(invest_amount)**: DB 및 API·프론트엔드에서 저장·표시되나, **실제 주문 수량 계산에 사용되지 않음**. `run_strategy`는 `sig.target_quantity or 1`만 사용.
2. **종목별 최대 비중(max_per_stock_pct)**: DB 저장 및 스케줄 객체로 전달되나, **run_strategy 및 주문 수량 로직에서 미사용**. (GO100 risk/position_sizing.py의 invest_amount 기반 수량 계산은 go100_portfolios 플로우용이며, v4_trade_schedules 플로우와 연결되어 있지 않음.)
3. **테이블명**: 실제 스케줄 테이블은 **v4_trade_schedules**이며, **go100_trade_schedules**는 존재하지 않음. 문서/스크립트에서 테이블명 정정 필요.

---

## DB 무결성 (변경 없음)

- strategy_cards: 변경 없음
- v4_positions: 변경 없음
- v4_trade_schedules: SELECT만 수행, DML 없음

---

## GitHub URL

- 보고서: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-TRADE-SETTINGS-VERIFY-001-20260223.md
