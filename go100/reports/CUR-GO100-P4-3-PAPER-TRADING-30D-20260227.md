# CUR-GO100-P4-3: 30일 모의투자 시뮬레이션 시스템 구현

**작성일**: 2026-02-27  
**태스크**: P4-3 30일 모의투자(페이퍼 트레이딩) 엔진 구축  
**상태**: 완료

---

## 1. 개요

백테스트(과거 OHLCV 일괄 검증)와 구분되는 **실시간 시장 기반 30일 가상 매매** 시뮬레이션 시스템을 구현하였다.

| 구분 | 백테스트 | 30일 모의투자 |
|------|----------|----------------|
| 데이터 | 과거 OHLCV 일괄 | 매일 장중 실시간(또는 당일 종가) |
| 실행 | 수초 내 결과 | 30일 경과 후 성과 확정 |
| 반영 요소 | 단순 종가 체결 가정 | 슬리피지(10bps), 스프레드, 수수료/세금 |

---

## 2. 구현 내역

### 2.1 DB 마이그레이션 (`backend/migrations/041_go100_paper_trading_30d.sql`)

- **go100_paper_trading_sessions**  
  - `session_id`, `user_id`, `strategy_card_id`, `initial_capital`, `current_capital`  
  - `start_date`, `end_date` (start_date + 30일)  
  - `status`: ACTIVE / COMPLETED / STOPPED  
  - `total_return`, `max_drawdown`, `win_rate`, `total_trades`, `sharpe_ratio`, `result_summary` (JSONB)

- **go100_paper_trades**  
  - `session_id`, `ticker`, `trade_type` (BUY/SELL), `quantity`, `price`  
  - `slippage_bps`, `commission`, `executed_at`  
  - `signal_source`: entry_rule, exit_rule, stop_loss, take_profit, stop_session  
  - `pnl`, `notes`

- 인덱스: `idx_pt30_session_user`, `idx_pt30_session_status`, `idx_pt30_session_dates`, `idx_pt30_trades_session`, `idx_pt30_trades_executed`

### 2.2 엔진 (`backend/app/services/go100/paper_trading_engine_30d.py`)

- **start_session(user_id, strategy_card_id, initial_capital=10_000_000, start_date=None)**  
  - 세션 생성, `end_date = start_date + 30`

- **run_daily_check(session_id)**  
  - 전략 카드 `entry_rules`로 유니버스 스크리닝 → 조건 충족 종목 가상 매수  
  - 보유 종목에 `exit_rules` + `stop_loss` + `take_profit` 적용 → 조건 충족 시 가상 매도  
  - 슬리피지 10bps 적용, `go100_paper_trades`에 기록

- **evaluate_session(session_id)**  
  - `total_return`, `max_drawdown`, `win_rate`, `total_trades`, `sharpe_ratio` 계산  
  - `result_summary`에 일별 equity curve 저장  
  - 30일 도달 시 `status = COMPLETED` 처리

- **stop_session(session_id)**  
  - 조기 중단: 보유 종목 전량 시장가 매도, `status = STOPPED`

- 내부 헬퍼: `_apply_slippage(price, side, bps=10)`, `_get_positions(session_id)`(trades 집계), `_load_card`, `_load_ohlcv`, `_get_close` 등

### 2.3 Cron 스케줄

- **09:10 (매수 시그널)**  
  - `scripts/go100/run_paper_trading_daily.sh`  
  - ACTIVE 세션 중 `end_date >= today`인 세션에 대해 `run_daily_check` 실행

- **15:20 (매도 시그널 + 일일 평가)**  
  - `scripts/go100/run_paper_trading_evaluate.sh`  
  - 모든 ACTIVE 세션에 `run_daily_check` 후, `end_date <= today` 세션에 `evaluate_session` 호출

- 로그: `>> /var/log/go100/paper_trading.log 2>&1`

### 2.4 Agent Tools

- **start_paper_trading(strategy_card_id, capital)**  
  - 30일 모의투자 세션 시작 (context `user_id` 사용, 없으면 2)

- **get_paper_trading_status(session_id=None)**  
  - `session_id` 지정 시: 해당 30일 세션 현황(보유종목, 수익률, 경과일수 등)  
  - 미지정 시: 기존 페이퍼 포지션 현황(go100_paper_positions)

- **stop_paper_trading(session_id)**  
  - 해당 세션 조기 중단

- `agent_tools.py`에 도구 정의 추가, `tool_executors.py`에 실행체 및 `TOOL_EXECUTORS` 등록 완료.

---

## 3. 테스트 및 검증

- 마이그레이션 적용: `sudo -u postgres psql -d kisautotrade -f backend/migrations/041_go100_paper_trading_30d.sql` → 성공
- 세션 생성: 카드 35번, 1천만원으로 `start_session(2, 35, 10_000_000)` → `session_id=1` 생성 확인
- `run_daily_check(1)` 1회 실행 → 매수/매도 발생 여부는 전략·유니버스·당일 데이터에 따라 0건일 수 있음 (정상)
- `evaluate_session(1)` → `total_return`, `max_drawdown`, `win_rate`, `total_trades`, `sharpe_ratio` 산출 및 `result_summary` 저장 확인
- Agent 도구: `get_paper_trading_status(session_id=1)`, `start_paper_trading(35, 10000000)` 호출 정상 동작
- DB 조회: `go100_paper_trading_sessions`, `go100_paper_trades` 데이터 존재 확인

---

## 4. 파일 목록

| 경로 | 설명 |
|------|------|
| `backend/migrations/041_go100_paper_trading_30d.sql` | 세션·체결 테이블 및 인덱스 |
| `backend/app/services/go100/paper_trading_engine_30d.py` | 30일 모의투자 엔진 |
| `scripts/go100/run_paper_trading_daily.sh` | 09:10 매수 시그널 크론 |
| `scripts/go100/run_paper_trading_evaluate.sh` | 15:20 매도·평가 크론 |
| `backend/app/services/go100/ai/agent_tools.py` | start/stop/get_paper_trading_status 도구 정의 추가 |
| `backend/app/services/go100/ai/tool_executors.py` | 실행체 및 30d 세션 조회 로직 |

---

## 5. 크론 등록 예시

```cron
# 09:10 - 매수 시그널 체크 (장 시작 10분 후)
10 9 * * 1-5 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_daily.sh >> /var/log/go100/paper_trading.log 2>&1
# 15:20 - 매도 시그널 체크 + 일일 평가 (장 마감 10분 전)
20 15 * * 1-5 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_evaluate.sh >> /var/log/go100/paper_trading.log 2>&1
```

---

## 6. 체크리스트

- [x] 코드 레포(kis-autotrade-v4) 반영 완료
- [ ] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)
