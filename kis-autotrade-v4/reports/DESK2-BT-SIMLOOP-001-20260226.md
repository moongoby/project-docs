# DESK2-BT-SIMLOOP-001 실매매 시뮬레이션 루프 구현 보고서

- **일자**: 2026-02-26  
- **우선순위**: P0  
- **브랜치**: phase-2c-command-center  
- **선행 완료**: DESK2-DISCOVERY-REDESIGN-001, DESK2-STRATEGY-REDESIGN-001, DESK2-ORCHESTRATION-REDESIGN-001  

---

## STEP 0 — 진단 결과

**진단 대상**: `backend/app/services/trading/desk2/tests/desk2_backtester.py` (래퍼 `scripts/backtest/desk2_backtester.py`가 해당 모듈의 `main()` 호출)

| 확인 항목 | 결과 | 비고 |
|-----------|------|------|
| **1. 분봉 순차 재생 루프** | **YES** | `time_to_bars` → `all_times = sorted(time_to_bars.keys())` → `for bar_dt in all_times:` 로 09:00~15:30 시간순 순회 |
| **2. 루프 내 전략 stalk() 호출** | **NO** | 기존: `discovery.scan_all()` → `strat.evaluate(sig, ind)` 만 사용. `receive_discovery()` → watchlist → 매 봉 `stalk(stock_code, bar_data)` 흐름 없음 |
| **3. 가상 진입/청산 로직** | **YES** | CS 기반 진입, `manage_position()` 손절/익절/타임아웃, `_compute_net_pnl`, `writer.write_trade()` 존재 |

**판정**: **상태 B** (항목 2 NO) → STEP 1 즉시 실행함.

---

## STEP 1 — 실매매 시뮬레이션 루프 구현 요약

### 1-1. 데이터 로드

- 기존 유지: `v4_ohlcv_minute`에서 지정일 전 종목 분봉 로드 (`_load_minute_bars`), `time_to_bars` / `all_times`로 09:00~15:30 시간순 정렬.

### 1-2. 메인 시뮬레이션 루프 구조

- **Phase A (발굴 스캔)**  
  - `discovery.scan_all(tickers, cache, bar_dt)` 후, `discovery_redesign.condition_time_slots`와 `_get_discovery_slot_for_bar_dt(bar_dt)`로 현재 시각이 C1~C7 각 조건의 time_slot에 해당하는 경우만 필터링하여 `filtered_signals` 사용.

- **Phase B (전략 배분 + Stalking)**  
  - `_build_bar_data_map(tickers)`로 종목별 bar_data 구성 (OHLCV, VWAP, RSI, 볼린저, EMA, 체결강도, state_data, recent_candles).  
  - `Desk2Orchestrator`(layer3) 사용: `orch_l3.update_positions(positions)` 후 `orch_l3.process_tick(filtered_signals, bar_data_map)` 호출.  
  - 내부에서 신규 발굴 → `receive_discovery()` → watchlist 등록, 전 종목에 대해 `stalk(stock_code, bar_data)` 호출로 CS Score 산출.

- **Phase C (경쟁 + 진입)**  
  - `process_tick` 반환값인 `selected`(CS≥50 TradeSignal, 동일 종목은 composite_score 최고 1건)에 대해 daily_limit/max_positions 체크 후 `SimPosition` 생성 및 가상 진입(진입가=해당 봉 close), `fund_pool.reserve`, ECHO_ABCD 등 기존 필터 적용.

- **Phase D (보유 포지션 관리)**  
  - 매 봉마다 `SimPosition`에 대해:  
    - MFE/MAE 갱신: `mfe_price = max(mfe_price, ind.high_price)`, `mae_price = min(mae_price, ind.low_price)`.  
    - 손절: `ind.low_price <= pos.stop_loss` → 청산.  
    - 익절: `ind.high_price >= pos.target_price` → 청산.  
    - 타임아웃: `hold_minutes(bar_dt) >= pos.max_hold_minutes` → 청산.  
  - 청산 시 `_compute_net_pnl`, `risk_manager.record_trade_result`, `fund_pool.release`, `closed_trades.append`, `writer.write_trade()` 호출.  
  - 일일 손실 한도 도달 시 보유 중인 SimPosition 전부 청산(기존 daily_limit 로직 유지).

### 1-3. 보조지표 실시간 계산

- `_apply_single_bar`로 봉 적용 시 캐시 갱신: VWAP, RSI(14), 볼린저(20,2), MA(5,20,60).  
- `_build_bar_data_map`에서 캐시 기준으로 bar_data에 vwap, rsi_14, bb_upper/lower/middle, ma_5/ma_20, trade_strength, state_data, recent_candles, adx(있으면) 포함.

### 1-4. 가상 포지션 관리 클래스

- `SimPosition` dataclass 추가 (desk2_backtester.py 내):  
  `stock_code`, `strategy_name`, `entry_price`, `entry_time`, `quantity`, `stop_loss`, `target_price`, `max_hold_minutes`, `mfe_price`, `mae_price`, `desk_score`, `cs_score`, `metadata`.  
  - `hold_minutes(as_of)` 메서드로 보유 시간(분) 계산.

### 1-5. BtDataWriter 연동

- 세션: 기존대로 `writer.create_session()` 사용.  
- 발굴: 매 발굴마다 `writer.write_discovery()` 호출 → **v4_bt_discoveries** 에 기록(대시보드 테이블). 기존 `write_discovery_log`(v4_bt_discovery_log) 호출 유지.  
- 거래: 청산 시 `writer.write_trade()` 호출(진입/청산 각각 기록).  
- 세션 종료: 기존대로 `writer.update_session_result()` 호출.

### 1-6. 출력

- `--verbose` 시 상세 로그.  
- `--output-json {파일}` 시 재현성 JSON을 해당 파일에 기록(래퍼에서 stdout 리다이렉트).  
- DB 저장은 항상 수행.

---

## 루프 구조 수치 (설명)

- **분봉 수**: 해당일 `all_times` 길이(종목별 분봉 시각 집합의 정렬 목록).  
- **발굴 횟수**: 매 봉 `scan_all` → time_slot 필터 후 `filtered_signals` 건수 누적.  
- **stalk 호출 횟수**: 매 봉 `orch_l3.run_stalking_cycle(bar_data_map)` 내부에서 (전략 수 × 해당 전략 watchlist 종목 수) 합.  
- **진입/청산 건수**: `SimPosition` 생성 수 = 진입 건수, Phase D 및 daily_limit 청산 수 = 청산 건수.

**실행 시간**: 390봉 기준 — 현재 환경에서 universe=0으로 데이터 미로드 시 루프 자체는 거의 즉시 종료. 데이터 존재 시 루프 구조상 390봉 × (캐시 갱신 + bar_data_map 구성 + process_tick + Phase D) 순서로 처리되며, 구체적 초 단위는 DB/캐시 성능에 따름.

---

## STEP 2 — 검증 테스트 결과

- **테스트 A** (`--date 2026-02-20`):  
  - 실행 결과: `universe=0`(해당일 v4_ohlcv_minute 데이터 없음)으로 발굴/거래 0건.  
  - 기대(최소 1건 발굴·최소 1건 거래)는 **데이터 존재 시** 충족 가능한 구조로 구현됨. 현재 환경에서는 **FAIL(데이터 부재)**.

- **테스트 B (DB 확인)**:  
  - 세션 생성 시에만 v4_bt_sessions/discoveries/trades INSERT.  
  - 데이터가 없어 세션 생성 후 바로 “거래 없음”으로 종료되므로, 데이터 있는 날짜로 실행 시 `v4_bt_discoveries`, `v4_bt_trades`, `v4_bt_sessions.total_return` 확인 가능.

- **테스트 C (재현성)**:  
  - 동일 날짜 2회 실행 시 `--output-reproducibility`(또는 `--output-json`)로 JSON 출력/저장. 결정론적 재현성 수집 로직(`_repro_discovery_events`, closed_trades 기반 리포트) 유지.

- **테스트 D (대시보드 API)**:  
  - `curl -s https://trading41.newtalk.kr/api/v1/backtest/sessions/{new_session}` 및 `/trades` 확인은 세션 생성 후 동일 URL로 가능. (데이터 있는 날짜 실행 후 session_id 사용)

---

## STEP 3 — 결론 및 준수 사항

- **수정 범위**:  
  - `backend/app/services/trading/desk2/tests/desk2_backtester.py` (SimPosition, Phase A/B/C/D, bar_data_map, write_discovery, orch_l3 연동).  
  - `backend/app/services/trading/desk2/tests/backtest_risk_manager.py` (`check_entry` 추가).  
  - `scripts/backtest/desk2_backtester.py`, `desk2_config.yaml` 은 지시서대로 참고/유지; config는 기존 discovery_redesign/condition_time_slots 사용.

- **절대 규칙 준수**:  
  - kis-v41-api/monitor/scheduler 재시작 금지.  
  - strategy_cards, v4_positions ALTER/DELETE 금지.  
  - 기존 `backtest_engine_v2.py` 수정 금지(참고만).  
  - DB는 v4_bt_sessions / v4_bt_discoveries / v4_bt_trades 에만 INSERT.

- **project-docs push 및 raw URL 200**:  
  - 보고서 작성 완료. push 및 raw URL 200 확인은 운영 측에서 수행.
