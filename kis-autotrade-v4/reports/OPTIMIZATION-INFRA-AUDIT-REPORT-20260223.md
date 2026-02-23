# OPTIMIZATION-INFRA-AUDIT 보고

**작업명:** OPTIMIZATION-INFRA-AUDIT (최적화 필수 데이터 전방위 점검 + DESK2 개선 분석)  
**서버:** 211.188.51.113  
**경로:** /root/kis-autotrade-v4  
**작성일:** 2026-02-23  
**작업 성격:** 읽기 전용 연구 (DB/파일 수정 없음)

---

## 사전 확인 결과 (기준과 상이 시 보고)

| 항목 | 기준 | 실제 | 비고 |
|------|------|------|------|
| strategy_cards COUNT | 59 | **62** | **기준과 상이 — 보고** |
| v4_positions OPEN | 5 | 5 | 정상 |
| kis-v41-api | active (running) | active (running) | 정상 |
| kis-v41-monitor | active (running) | active (running) | 정상 |
| kis-v41-scheduler | — | (출력 생략) | — |
| df -h / | — | 50% 사용 (48G/99G) | 정상 |

---

## [PART A: 백테스트 데이터 완결성]

### v4_backtest_trades 컬럼 목록

| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | bigint | PK |
| session_id | bigint | FK → v4_backtest_sessions |
| desk_id | integer | 있음 |
| stock_code | varchar(10) | 있음 |
| trade_date | date | 있음 (일자만) |
| trade_type | varchar(10) | BUY/SELL/TRANSFER_IN/OUT |
| quantity | integer | 있음 |
| price | numeric(12,2) | 단일 가격 (진입/청산 구분 없음) |
| amount | numeric(15,0) | 있음 |
| split_phase | integer | 있음 |
| transfer_to | integer | 있음 |
| pnl | numeric(12,0) | 있음 |
| pnl_pct | numeric(8,4) | 있음 |
| reason | varchar(100) | 진입/청산 사유 일부 (BUY_PHASE_1, vwap_cross_above 등) |
| card_id | integer | 있음 |
| exit_reason | varchar(30) | STOP_LOSS, TRAILING_STOP, TIME_EXIT, EOD_FORCE_EXIT 등 (청산 시만) |
| entry_date | date | 있음 |
| exit_date | date | 있음 (청산 시만) |
| hold_days | integer | 있음 |

**참고:** `strategy_name` 컬럼은 없음. 전략명은 session의 desk_configs에서 card_id로 매핑 가능.

### 세션 61 기준 NULL 비율 (요약)

- total: 1006건  
- null_exit_date: 503 (미청산 BUY 또는 미기록)  
- null_pnl / null_pnl_pct: 503  
- null_exit_reason: 503  
- entry_date, price, reason, card_id: 0 (전부 채워짐)

### 최적화에 필수이지만 없는 데이터 (체크리스트 대조)

| # | 데이터 | 필요 이유 | 현재 상태 |
|---|--------|-----------|-----------|
| 1 | **진입 시각 (entry_time/entry_datetime)** | 시간대별 타이밍·분봉 분석 | **없음** — trade_date(일자)만 있음 |
| 2 | **청산 시각 (exit_time/exit_datetime)** | 보유 시간 정밀 분석 | **없음** |
| 3 | **진입가 (entry_price)** | 슬리피지·갭 분석 | **없음** — price는 해당 행의 체결가(매수 시 매수가, 매도 시 매도가)만 저장, 행별로 구분됨. 진입가만 따로 컬럼 없음 |
| 4 | **청산가 (exit_price)** | 실제 수익 검증 | **없음** — SELL 행의 price가 곧 청산가이므로 역산 가능하나 별도 컬럼 없음 |
| 5 | 진입 시 호가 스프레드 | 체결 품질 분석 | **없음** |
| 6 | 진입 시 거래량 | 유동성 검증 | **없음** |
| 7 | 진입 시 시장 레짐 | 시장 상황별 전략 성과 | **없음** |
| 8 | DESK ID | 어떤 DESK에서 매매했는지 | **있음** (desk_id) |
| 9 | 포지션 사이즈 | 자금 운용 분석 | **부분** — quantity·amount로 역산 가능, 전용 컬럼 없음 |
| 10 | 슬리피지 | limit vs 실체결 차이 | **없음** |
| 11 | 수수료 | 순수익 계산 | **없음** — 엔진 내 FEE_RATE 반영은 코드 내부만 |
| 12 | 진입 사유 (entry_reason) | 어떤 시그널로 진입했는지 | **부분** — reason에 진입 시 BUY_PHASE_1, vwap_cross_above 등 저장 |
| 13 | 청산 사유 (exit_reason) | 익절/손절/타임아웃/트레일링 | **있음** (exit_reason) |
| 14 | 최대 유리 가격 (MFE) | MFE 분석 | **없음** |
| 15 | 최대 불리 가격 (MAE) | MAE 분석 | **없음** |
| 16 | 진입 시 기술 지표값 (RSI, MACD, BB 등) | 지표 유효성 검증 | **없음** |
| 17 | 종목 섹터/업종 | 섹터 로테이션 분석 | **없음** |
| 18 | 인계 여부 (promoted_from_desk) | Promotion 분석 | **부분** — transfer_to로 인계 DESK 추론 가능 |

### 데이터 완결성 등급

**C: 심각 부족**  
- 시간축(진입/청산 시각) 없음 → 분봉·시간대별 최적화 불가.  
- MFE/MAE·진입가/청산가 전용 컬럼·레짐·지표값·스프레드·수수료 등 최적화 필수 항목 다수 미기록.

---

## [PART B: 종목 필터 현황]

### DESK별 종목 선별 방식

| DESK | 선별 방식 | strategy_cards entry_rules.filters/universe/screening |
|------|-----------|------------------------------------------------------|
| DESK1 | Commander 기반 (Desk1Commander.run_premarket_scan) → class_b 픽 | filters/universe/screening 컬럼 **NULL** (entry_rules 내 indicators 등으로 정의) |
| DESK2 | Desk2Commander.run_premarket_scan → class_a 픽 | 동일, **NULL** |
| DESK3 | Desk3Commander + v4_pick_reasons CLASS-D 등 | 동일, **NULL** |
| DESK4·5 | 각 Commander + 전략 카드 | 동일, **NULL** |

- **종목 필터 코드 위치**  
  - 파이프라인: `backend/app/services/trading/v4_pipeline_orchestrator.py` (run_desk1_cycle, run_desk2_cycle 등 → 각 Commander 호출)  
  - DESK1: `Desk1Commander.run_premarket_scan` → class_b  
  - DESK2: `Desk2Commander.run_premarket_scan` → class_a  
  - 시그널/유니버스: `backend/app/services/strategy/strategy_engine.py` (generate_signals), `backend/app/services/brain/chief_analyst.py` (build_today_universe), `backend/app/services/market/universe_service.py`  
  - 필터 관련: `backend/app/services/go100/universe/*.py` (rsi_filter, volume_filter 등), `backend/app/services/strategy/signal_filter.py`

- **현재 필터 수준**  
  - **중간**: DESK별 Commander에서 스캔·클래스별 픽으로 종목 축소. strategy_cards에는 indicators·time_window·min_strength 등으로 진입 규칙은 정의되나, DB 레벨의 filters/universe/screening 필드는 비어 있음.

- **개선 필요사항**  
  - entry_rules 내 indicators와 실제 스크리닝 로직 매핑 명확화.  
  - 유니버스/필터 설정을 DB 또는 설정에서 관리해 DESK별·시간축별 재현 가능하도록 정리.

---

## [PART C: DESK2 심화 분석]

### DESK2 전략(card_id)별 성과 — 세션 61 (일봉, V2_BT-TUNE-DESK2-3M)

| card_id | 전략명(참고) | trades | avg_pnl | pnl_stddev | win_rate | avg_win | avg_loss |
|---------|--------------|--------|---------|------------|----------|---------|----------|
| 7 | DESK2_종가매매_class_c | 14 | 2.38 | 9.11 | 57.1 | 7.85 | -4.91 |
| 22 | DESK2_S05_거래량점화 | 28 | 1.95 | 8.72 | 42.9 | 8.35 | -2.86 |
| 27 | DESK2_M002_AbsoluteZero_종가매매 | 10 | 1.37 | 3.50 | 60.0 | 2.98 | -1.04 |
| 19 | DESK2_거래량스파이크 | 41 | 0.88 | 6.47 | 56.1 | 5.00 | -4.39 |
| 20 | DESK2_변동성확대 | 198 | 0.13 | 6.78 | 44.9 | 5.28 | -4.07 |
| 26 | DESK2_M001_3분봉종합눌림확인 | 1 | -0.46 | — | 0.0 | — | -0.46 |
| 14 | DESK2_장초반레인지돌파 | 63 | -0.51 | 9.42 | 36.5 | 8.55 | -5.72 |
| 21 | DESK2_D01_3분봉_20선눌림목 | 5 | -1.07 | 2.43 | 60.0 | 0.22 | -3.00 |

### DESK2 분봉 성과 — 세션 62 (V2_BT-MIN-DESK2-2M)

| card_id | trades | avg_pnl | win_rate |
|---------|--------|---------|----------|
| 19 | 113 | -0.06 | 40.7 |
| 27 | 36 | -0.10 | 38.9 |
| 22 | 62 | -0.13 | 38.7 |
| 7 | 33 | -0.15 | 39.4 |
| 14 | 179 | -0.17 | 33.0 |
| 26 | 11 | -0.19 | 45.5 |
| 20 | 706 | -0.22 | 32.6 |
| 21 | 31 | -0.35 | 32.3 |

- **일봉 vs 분봉 차이**  
  - 일봉(61)에서는 7, 22, 27, 19, 20이 양의 평균 수익; 분봉(62)에서는 **전 카드 평균 수익이 0 이하**.  
  - 분봉에서 거래 횟수(특히 card 20)는 크게 늘어나나 승률·평균 수익이 하락 → **분봉 진입/청산 타이밍·조건이 일봉 대비 불리하게 작동**하는 것으로 해석 가능.

### DESK2 수익 종목 특성 (세션 61, SELL 기준, pnl_pct>0, 2회 이상)

- 상위 종목 예: 187660(avg_pnl 30.07), 437730(19.25), 038500(17.48), 424870(15.60), 058610(11.36) 등.  
- ohlcv_daily와의 조인으로 거래대금·등락폭 분석 쿼리는 실행했으나, 해당 기간/종목 데이터 이슈로 집계가 비어 있음. **수익 종목 리스트는 확보.**

### DESK2 손실 전략·개선 방향

- **손실 전략**: 일봉 기준 14(장초반레인지돌파), 21(3분봉눌림목), 26(3분봉종합눌림) 등.  
- **개선 방향**  
  - 분봉 백테스트에서 **진입/청산 시각 기록** 후 시간대별·카드별 성과 분석.  
  - 분봉 전용 진입 조건(volume_surge, vwap_cross_above, price_above_open 등)의 **시간대·유동성 필터** 강화.  
  - 일봉에서 수익 난 카드(7, 22, 27, 19)는 유지·가중, 분봉에서만 손실이 큰 카드는 시간창·최소 보유시간·EOD 강제 청산 정책 재검토.

---

## [PART D: DESK별 종목 추천 로직]

- **파이프라인 흐름**  
  - `v4_pipeline_orchestrator`: `run_desk1_cycle` → Desk1Commander.run_premarket_scan → class_b picks → process_signal.  
  - `run_desk2_cycle` → Desk2Commander.run_premarket_scan → class_a picks → 시그널 강도별 분할 매수.  
  - `run_desk3_cycle` → Desk3Commander + _desk3_receive_transfers, phase2 buy pending.  
  - DESK4·5도 각 Commander + transfer 수신·phase 매수.

- **DESK별 차별화**  
  - DESK1: class_b 상한가 후속·스캘핑.  
  - DESK2: class_a 데이트레이딩, 강도 80 이상 전량·60–79 분할.  
  - DESK3: 단기스윙, CLASS-D 등 v4_pick_reasons·시그널 연동.  
  - DESK4·5: 중기·모멘텀, 승격 포지션 처리.

---

## [PART E: 실매매 데이터 기록 현황]

### 기록되는 데이터 (주요 테이블)

| 테이블 | 용도 | 주요 컬럼 |
|--------|------|-----------|
| v4_positions | 포지션 | ticker, quantity, entry_price, status, desk_id, card_id, entry_date, exit_reason, exit_price, exited_at, pnl_pct, signal_id |
| v4_order_requests | 주문 요청 | ticker, side, quantity, price_type, limit_price, signal_id, position_id, status |
| v4_order_executions | 체결 | position_id, stock_code, order_price, order_qty, order_time, exec_price, exec_qty, exec_time, **slippage_pct/amt, market_bid/ask, spread_pct, market_volume_at_order** |
| v4_signals | 시그널 | desk_id, stock_code, signal_date, signal_type, signal_strength, entry_price, target/stop_loss, conditions_met, indicator_data |
| v4_pick_reasons | 픽 사유 | pick_date, desk_id, class_type, stock_code, total_score, score_detail, reason_summary, market_regime |
| v4_trades | 체결 이력 | position_id 등 (v4_positions FK) |

- **실매매에서 기록되지 않는 최적화 필수 데이터**  
  - 포지션·주문 수준: **진입/청산 시각(시간)** (entry_date는 일자만), **진입 시 시장 레짐**, **MFE/MAE**, **진입 시 기술지표 스냅샷**, **종목 섹터/업종**.  
  - v4_order_executions에는 slippage, spread, market_volume_at_order 등이 있어 **체결 품질·유동성 분석은 일부 가능**.

---

## [PART F: 시장 변동 예측 데이터]

- **Market Regime Detector 상태**  
  - 코드: `backend/app/services/market/regime_detector.py`.  
  - 5단계 레짐: STRONG_TREND_UP, MILD_TREND_UP, SIDEWAYS, MILD_TREND_DOWN, STRONG_TREND_DOWN.  
  - 입력: KOSPI 20일 수익률, MA5/20/60, 양봉 비율 20일, 거래대금 추이, **외국인 20일 순매수**(v4_investor_daily), 상한/하한가 비율, **VKOSPI**(v4_vkospi_daily).

- **v4_market_regime_daily**  
  - 스키마: date, regime, regime_score, kospi_ret_20d, ma5/20/60, ma_alignment, bull_ratio_20d, vkospi, foreign_flow_20d, previous_regime, transition_note 등.  
  - **현재 건수**: regime별 COUNT 2건 (MILD_TREND_UP만 존재). **과거 일자 적재 부족.**

- **사용 가능한 외부·보조 데이터**  
  - index_daily: 0001(KOSPI), 1001(KOSDAQ), 2001 (2024-02-13 ~ 2026-02-13).  
  - v4_investor_daily (외국인 순매수 등).  
  - v4_vkospi_daily (VKOSPI).  
  - v4_market_investor_daily.

- **부족한 데이터**  
  - **레짐 일별 히스토리** 충분 적재 없음 → 시장 구간별 백테스트·전략 가중 적용 불가.  
  - 금리·환율·VIX·put/call 등 외부 지표 테이블 없음 (레짐 판정은 현재 지표로만 동작).

---

## [PART G: 백테스트 엔진 데이터 기록]

- **현재 기록 항목** (backtest_engine_v2.py `_record_trade` INSERT)  
  - session_id, desk_id, stock_code, trade_date, trade_type, quantity, price, amount, split_phase, transfer_to, pnl, pnl_pct, reason, card_id, exit_reason, entry_date, exit_date, hold_days.

- **추가 필요 항목 (우선순위)**  
  1. **진입/청산 시각** (entry_time, exit_time 또는 entry_datetime, exit_datetime) — 분봉·시간대 최적화 필수.  
  2. **진입가/청산가** (entry_price, exit_price) — 행별로 매수/매도 구분되어 있으나 전용 컬럼 있으면 집계·검증 용이.  
  3. **진입 시 시장 레짐** (regime_at_entry).  
  4. **MFE/MAE** (max_favorable_price, max_adverse_price 또는 pct).  
  5. **진입 시 기술 지표 스냅샷** (JSON 또는 별도 테이블).  
  6. **슬리피지/수수료** (실제 적용값 기록).  
  7. **종목 섹터/업종** (또는 sector_id).

- **분봉 백테스트 시간 데이터**  
  - `_run_minute`에서 `trade_date`, `minute_time`(datetime)으로 루프하나, **DB INSERT 시에는 trade_date(일자)만 저장**. 분봉 시각은 기록되지 않음.

---

## [종합 — 최적화 불가/부족 데이터 전체 목록]

| # | 데이터 | 영향 범위 | 현재 상태 | 개선 우선순위 |
|---|--------|-----------|-----------|----------------|
| 1 | 진입/청산 시각 (entry_time, exit_time) | 분봉·시간대별 최적화, 보유시간 분석 | 없음 | **최우선** |
| 2 | 진입가/청산가 전용 컬럼 | 슬리피지·갭·수익 검증 | 없음(역산 가능하나 불편) | 높음 |
| 3 | MFE/MAE | 전략·청산 규칙 최적화 | 없음 | 높음 |
| 4 | 진입 시 시장 레짐 | 레짐별 전략 가중·비활성화 | 없음 | 높음 |
| 5 | 진입 시 기술 지표 스냅샷 | 지표 유효성·임계값 튜닝 | 없음 | 중간 |
| 6 | 슬리피지·수수료 기록 | 순수익·체결 품질 | 없음(코드 내 상수만) | 중간 |
| 7 | 종목 섹터/업종 | 섹터 로테이션 | 없음 | 중간 |
| 8 | 호가 스프레드·진입 시 거래량 | 체결 품질·유동성 | 없음 | 낮음 |
| 9 | v4_market_regime_daily 과거 적재 | 시장 구간별 백테스트 | 2건 수준, 부족 | 높음 |
| 10 | strategy_name 컬럼 | 집계·리포트 가독성 | 없음(card_id만) | 낮음 |

---

## 확인 수치

- **strategy_cards COUNT:** 62 (기준 59와 상이 — 보고함)  
- **v4_positions OPEN:** 5 (기준과 동일)

---

**— 보고 끝 —**

*(이 작업은 읽기 전용 연구이다. DB/파일 수정·backtest_engine_v2.py 수정 없음.)*
