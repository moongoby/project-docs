# DESK2-BT-LIVE-PARITY-001 통합 지시서

- **일자**: 2026-02-26  
- **우선순위**: P0  
- **목표**: DESK2 7조건 7전략을 실거래 동일 환경에서 백테스트 → 검증 → 실매매 반영  

---

## 전제: 이미 완료된 작업

| Stage | 작업 | 상태 |
|-------|------|------|
| Stage 1 | C1~C7 발굴 재설계 (DESK2-DISCOVERY-REDESIGN-001) | 완료 |
| Stage 2 | 7전략 재설계 — watchlist + stalking + CS Score (DESK2-STRATEGY-REDESIGN-001) | 완료 |
| Stage 3 | 오케스트레이터 — 다:다 경쟁 + composite score (DESK2-ORCHESTRATION-REDESIGN-001) | 완료 |

이 3개 Stage의 코드가 **실거래에도 백테스트에도 동일하게** 사용된다.

---

## PHASE 1 — 실거래 동일 백테스트 엔진 구축

### 1-1. 신규 디렉토리 및 파일

`backend/app/services/trading/desk2/backtest/` 아래 4개 파일:

| 파일 | 역할 |
|------|------|
| **historical_price_feeder.py** | 실거래 PricePoller 대체. v4_ohlcv_minute 지정일 분봉 09:00~15:30 시간순 1봉씩 공급, 누적 보조지표(VWAP, RSI, BB, EMA, ADX), 체결강도 추정, state_data 구성 |
| **sim_order_executor.py** | 실거래 OrderExecutor 대체. 슬리피지 ±0.1%, 수수료 0.015%, 세금 0.18%(매도), 손절/익절 시 갭 대응 exit_price |
| **sim_fund_pool.py** | 실거래 FundPool 대체. 초기 자본금 기반 available/reserved, position_size_pct 기반 수량, reserve/release with P&L, daily_loss_pct() |
| **backtest_runner.py** | 메인 실행기. layer1_discovery / layer2_strategy / layer3_orchestration / risk_manager 실거래 코드 그대로 import, Feeder/Executor/FundPool만 교체 |

### 1-2. 메인 시뮬레이션 루프 요약

- **PRE_MARKET**: regime = regime_detector.detect(trade_date), fund_pool 초기화  
- **매 봉(09:00→15:30)**  
  - **Phase A** 발굴: discovery_manager.scan_all(tickers, cache, bar_dt), DESK Score ≥ 60, time_slot 필터  
  - **Phase B** 전략: orchestrator.process_tick(filtered_discoveries, bar_data_map) → TradeSignal, composite score  
  - **Phase C** 리스크 + 진입: risk_manager.check_entry, fund_pool.get_position_size, sim_executor.execute_buy, reserve  
  - **Phase D** 포지션 관리: 진입 봉 스킵(hold_bars≥1), MFE/MAE 갱신, 손절(갭 하락 시 exit_price=open), 익절(갭 상승 시 exit_price=open), 타임아웃  
  - **Phase E** 일일 손실 한도: daily_loss_pct ≤ -3% 시 전량 청산 후 break  
- **POST_MARKET**: 15:30 잔여 포지션 전량 청산, writer.update_session_result  

### 1-3. 7조건 × 7전략 매칭

desk2_config.yaml `discovery_redesign.eligible_strategies_matrix` 및 `condition_time_slots`에서 로드.  
C1 갭→ALPHA_GAP, C2→BRAVO_ORB, C3→CHARLIE_VI, C4→DELTA_VWAP, C5→ECHO_ABCD, C6→FOXTROT_SECTOR, C7→GOLF_REVERSAL.

### 1-4. 전략별 매매 파라미터

desk2_config.yaml `strategy_params`, `risk`, `orchestration_v2`에서 로드.  
stop_loss / target / max_hold 는 전략별 설정값 사용.

---

## PHASE 2 — 검증

### 2-1. 1일 테스트 (2026-02-20)

```bash
cd /root/kis-autotrade-v4
PYTHONPATH=/root/kis-autotrade-v4:/root/kis-autotrade-v4/backend \
python3 scripts/backtest/desk2_live_parity_run.py \
  --date 2026-02-20 --capital 10000000 --verbose \
  --session-name "DESK2-LIVE-PARITY-V1" \
  --output-json /tmp/live_parity_v1.json
```

### 2-1. 1일 테스트 (2026-02-20)

```bash
cd /root/kis-autotrade-v4
PYTHONPATH=/root/kis-autotrade-v4:/root/kis-autotrade-v4/backend \
python3 scripts/backtest/desk2_live_parity_run.py \
  --date 2026-02-20 --capital 10000000 --verbose \
  --session-name "DESK2-LIVE-PARITY-V1" \
  --output-json /tmp/live_parity_v1.json
```

**실행 결과 (2026-02-26 검증)**  
- BT 세션 생성·DB 기록 정상. JSON 출력 정상.  
- 해당일(2026-02-20) 레짐=MILD_TREND_DOWN, 발굴 0건 → 거래 0건. (발굴 발생일은 데이터/게이트에 따라 상이할 수 있음.)

**PASS 기준**

| 항목 | 기준 |
|------|------|
| 발굴 | C1~C7 중 최소 2개 조건에서 발굴 발생 |
| 거래 | ≥ 2건 (진입+청산) 또는 1일 유효 실행 |
| hold_seconds | 모든 거래 > 0 |
| entry_quantity | 자금 비례 (1주 아님) |
| stop_loss 작동 | exit_price = stop_loss 가격 (봉의 low 아님) |
| 수수료/세금 | 적용됨 (gross_pnl ≠ net_pnl 반영) |
| DB 저장 | v4_bt_sessions, v4_bt_discoveries, v4_bt_trades 모두 기록 |
| 대시보드 | API 조회 가능 |

### 2-2. 재현성 검증

동일 날짜 2회 실행 → JSON diff 0건.

```bash
bash scripts/backtest/desk2_live_parity_verify.sh 2026-02-20
```

### 2-3. 5일 연속 테스트

2026-02-19, 20, 23, 24, 25 각각 실행하여:

- 전체 C1~C7 최소 1회씩 발굴 발생 확인  
- 7전략 중 최소 3개 이상 진입 발생 확인  
- 일별 거래 2~5건 범위 확인  
- 일일 손실 -3% 한도 작동 확인  

---

## PHASE 3 — 성과 분석 및 파라미터 튜닝 (이후 별도 지시)

- 조건별 발굴 성공률  
- 전략별 승률, 평균 수익, 평균 손실  
- composite score와 실제 수익의 상관관계  
- gate 조건 완화/강화, stop_loss/target/max_hold 최적값  

---

## PHASE 4 — 실매매 반영 (CEO 승인 후)

백테스트에서 아래 기준 충족 시 실매매 전환:

| 기준 | 목표 |
|------|------|
| E(기대값) | > +0.3% |
| Calmar | > 1.5 |
| PF(수익비율) | > 1.3 |
| 일일 손실 | ≤ -3% |
| 일일 거래 | 2~5회 |
| OOS/IS 비율 | ≥ 0.6 |

충족 시: CEO 승인 → strategy_cards DESK2 신규 카드 등록 → desk2_config 실거래 파라미터 반영 → 모의투자 1주일 → 실매매 전환.

---

## 절대 규칙

- **kis-v41-*** 서비스 재시작 금지  
- **strategy_cards**, **v4_positions** ALTER/DELETE 금지  
- **실거래 코드** (layer1_discovery, layer2_strategy, layer3_orchestration, risk_manager, position_manager) **수정 금지** — 어댑터로 감쌈  
- 신규 파일만 생성: backtest/ 디렉토리 4개 파일 + CLI wrapper  
- DB는 **v4_bt_sessions / v4_bt_discoveries / v4_bt_trades** 에만 INSERT  
- 기존 **desk2_backtester.py** 는 보존 (신규 backtest_runner.py 가 실거래 동일 경로 백테스트용)  

---

## 구현 요약 (2026-02-26)

- **historical_price_feeder.py**: v4_ohlcv_minute 로드, 누적 VWAP/RSI/BB/EMA/ADX, 체결강도(close>open→110 else 90), state_data 호환 dict  
- **sim_order_executor.py**: execute_buy(slippage +0.1%, 수수료), execute_sell(slippage -0.1%, 수수료+세금), P&L 반영  
- **sim_fund_pool.py**: reserve/release, get_position_size(position_size_pct), daily_loss_pct()  
- **backtest_runner.py**: 7전략(ALPHA_GAP~GOLF_REVERSAL+CHARLIE_VI, FOXTROT_SECTOR), 진입 봉 청산 스킵, 갭 하락/상승 시 exit_price=open, 일일 -3% 한도, POST_MARKET 15:30 잔여 청산, BtDataWriter 연동  
- **CLI**: scripts/backtest/desk2_live_parity_run.py — --date, --capital, --session-name DESK2-LIVE-PARITY-V1, --output-json  

---

## 문서 레포 푸시 후 경로

- 본 지시서 경로: **`report/v41/DESK2-BT-LIVE-PARITY-001-20260226.md`** (메인 레포 `kis-autotrade-v4` 내).  
- 별도 문서 레포에 푸시 시 해당 레포 경로를 운영 측에서 보고할 것.
