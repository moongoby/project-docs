# DESK2-ENGINE-IMPL-001: 스코어링 엔진 + 신호 감지 코드 구현

**Task ID**: DESK2-ENGINE-IMPL-001  
**Priority**: P0-CRITICAL  
**작성일**: 2026-02-27  

---

## 1. 개요

커서 1(파라미터 최적화), 커서 3(인프라) 결과와 무관하게, **현재 확보된 파라미터**로 스코어링 엔진과 신호 감지·자동 매매 코드를 먼저 구현하였다.  
최적화 결과가 나오면 **`desk2_config.yaml`만 수정**하면 되도록 모든 파라미터를 config에서 읽는 구조로 설계했다.

---

## 2. 구현 요약

| 구분 | 파일 | 역할 |
|------|------|------|
| 설정 | `scripts/desk2/desk2_config.yaml` | scoring / signal / exit / position / risk 초기값 |
| 사전 스코어링 | `scripts/desk2/desk2_prescoring.py` | D-5~D-1 일봉·뉴스 수·스코어·2차 필터 → `v4_desk2_candidates` INSERT |
| 실시간 신호 | `scripts/desk2/desk2_realtime_signal.py` | 당일 후보·분봉·유형(dip%)·T5/S1 감지 → `v4_desk2_signals` INSERT |
| 자동 매매 | `scripts/desk2/desk2_auto_trader.py` | NEW 신호 매수, 목표/스톱/시간 청산 모니터링·실행 → `v4_desk2_trades` INSERT |

---

## 3. 설정 파일: `scripts/desk2/desk2_config.yaml`

- **scoring**: 가중치(f3_vol_ratio, f2_vol_change, f1_news_count, f4_close_pos), filter(min_news_count, min_close_pos), top_n
- **signal**: trend(T5, threshold_pct, delay_minutes), reversal(S1, strength_low/high, lookback_minutes, delay_minutes), classification(trend_dip_max, reversal_dip_min)
- **exit**: trend/reversal별 type, target_pct, stop_pct, time_exit, next_day_exit
- **position**: max_positions, sizing, capital_per_trade_pct, cash_reserve_pct
- **risk**: daily_max_loss_pct, consecutive_loss_halt, market_crash_threshold, same_stock_reentry

최적화 후에는 이 파일만 갱신하면 된다.

---

## 4. desk2_prescoring.py

- **데이터 소스**: `ohlcv_daily`(D-5~D-1), `go100_news_items`(D-1 뉴스 건수)
- **피처**: f3_vol_ratio(D-1 거래량/5일 평균), f2_vol_change(5일 대비 변화), f1_news_count, f4_close_pos(D-1 봉 종가 위치)
- **정규화**: 유니버스 내 min-max 0~1 후 가중 합으로 스코어 계산
- **2차 필터**: min_news_count 이상, min_close_pos 이상
- **결과**: 상위 top_n 건 `v4_desk2_candidates` INSERT, 기존 해당 target_date 건 삭제 후 삽입
- **실행**: `python3 scripts/desk2/desk2_prescoring.py [target_date_YYYY-MM-DD]`

---

## 5. desk2_realtime_signal.py

- **데이터 소스**: `v4_desk2_candidates`(당일 후보), `v4_ohlcv_minute`(당일 분봉)
- **유형 분류**: dip_pct(시가 대비 당일 최저가 하락률) 기준  
  - dip &lt; trend_dip_max → TREND  
  - dip ≥ reversal_dip_min → REVERSAL  
  - 그 외 → BORDER
- **T5(TREND)**: 시가 대비 +threshold_pct% 이상, delay_minutes 봉 만족 시 신호 INSERT
- **S1(REVERSAL)**: dip ≥ reversal_dip_min, lookback 분봉 내 종가위치(strength)가 strength_low~strength_high 구간일 때 신호 INSERT
- **결과**: `v4_desk2_signals` INSERT(status=NEW)
- **실행**: `python3 scripts/desk2/desk2_realtime_signal.py [signal_date] [as_of_time_HH:MM]`

---

## 6. desk2_auto_trader.py

- **order_executor / position_manager**: 기존 `backend.app.services.execution.order_executor`, `backend.app.services.position.position_manager`를 **import하여 wrapper로만 호출**. 해당 파일들은 수정하지 않음.
- **process_new_signals(db_session_factory, create_reservation, order_executor, config)**  
  - `v4_desk2_signals`에서 status=NEW 조회  
  - 예약(create_reservation) → order_executor.execute_buy  
  - 체결 시 신호 FILLED 갱신, `v4_desk2_trades`에 진입 행 INSERT(exit_time NULL)
- **monitor_exits(db_session_factory, get_current_price, order_executor, config)**  
  - exit_time IS NULL인 `v4_desk2_trades` 조회  
  - 목표/스톱/시간(time_exit) 조건 만족 시 order_executor.execute_sell 호출 후 해당 trade 행 UPDATE(exit_time, exit_price, exit_reason, gross_pnl 등)
- **실행**: 백엔드 컨텍스트에서 의존성 주입 후 호출. CLI는 import 검증만 수행.  
  `PYTHONPATH=backend python3 scripts/desk2/desk2_auto_trader.py`

---

## 7. import 및 실행 테스트 결과

- **desk2_prescoring.py**: venv 기준 실행 성공. (데이터 없음 시 INSERTED=0 정상)
- **desk2_realtime_signal.py**: venv 기준 실행 성공. (당일 후보 없음 시 INSERTED=0 정상)
- **desk2_auto_trader.py**: venv + PYTHONPATH=backend 실행 시 정상 종료.  
  백엔드 컨텍스트 없을 때는 “Backend imports skipped” 로그 후 안내 메시지 출력.

---

## 8. DB 테이블 (기존 마이그레이션 활용)

- `v4_desk2_candidates`: target_date, stock_code, score, score_rank, f1~f4, stock_name, market_cap, sector 등
- `v4_desk2_signals`: signal_date, stock_code, stock_type, signal_name, signal_time, signal_price, dip_pct, entry_price, status(NEW/FILLED 등)
- `v4_desk2_trades`: trade_date, stock_code, entry_time, entry_price, quantity, exit_time, exit_price, exit_reason, gross_pnl, gross_pnl_pct 등 (진입 시 INSERT, 청산 시 UPDATE)

---

## 9. 결론

- 스코어링 엔진(desk2_prescoring), 신호 감지(desk2_realtime_signal), 자동 매매(desk2_auto_trader) 구현 완료.
- 모든 파라미터는 `scripts/desk2/desk2_config.yaml`에서 로드되며, 최적화 후에는 이 파일만 갱신하면 됨.
- order_executor / position_manager는 기존 모듈을 import해 wrapper로만 사용하며, 해당 파일은 수정하지 않음.
- import 및 스크립트 실행 테스트 통과.
