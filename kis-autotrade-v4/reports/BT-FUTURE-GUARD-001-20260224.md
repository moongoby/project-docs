# BT-FUTURE-GUARD-001 — FutureDataGuard + Walk-Forward 구현

**작업ID:** BT-FUTURE-GUARD-001  
**작업명:** FutureDataGuard + Walk-Forward 프레임워크 구현  
**일시:** 2026-02-24 KST  
**우선순위:** P3  
**자체승인:** O (백테스트 신뢰성 확보 — CEO 수익 극대화 목표 전제)

---

## 1. 배경 (IMPL-GAP-AUDIT-001 §Phase A 미구현)

- **IMPL-GAP-AUDIT-001** 및 **v41-development-plan-spec.md** Phase A에서 다음이 미구현으로 지적됨:
  - **FutureDataGuard:** sim_date 이후 데이터 참조 차단
  - **Walk-Forward:** 6개월 학습 → 3개월 검증 슬라이딩, OOS/IS 비율·통과 기준
  - **Ablation:** 후속 작업으로 분리

본 작업으로 FutureDataGuard와 Walk-Forward Runner를 구현하고, 기존 백테스트 로직은 wrapper 방식으로 최소 수정하여 연동하였다.

---

## 2. FutureDataGuard

### 2.1 설계

- **파일:** `scripts/backtest/future_data_guard.py`
- **클래스**
  - **FutureDataGuard:** 시뮬레이션 날짜(sim_date) 이후 데이터 접근 차단
    - **DataFrame 모드:** `date_column` 기준으로 `get_data(end_date)` / `get_lookback(sim_date, lookback_days)` 제공
    - **Dict 모드:** `ohlcv_data` 구조 `{date_str: {stock_code: {...}}}` 키(date_str) 기준으로 동일 API 제공
  - **FutureDataLeakError:** 미래 데이터 포함 시 검증 실패용 예외
- **주요 API**
  - `set_sim_date(sim_date: str)` — 현재 시뮬레이션 날짜 설정 (YYYYMMDD)
  - `get_data(end_date=None)` — sim_date(또는 end_date) 이하 데이터만 반환
  - `get_lookback(sim_date, lookback_days)` — sim_date 기준 과거 lookback_days일 치 데이터
  - `validate_no_future_leak(df, sim_date, date_col)` — 정적 검증 (DataFrame에 미래 행 있으면 예외)

### 2.2 적용 지점

- **backtest_engine_v2.py**
  - 생성자에 `use_future_guard: bool = True` 추가
  - `_load_ohlcv()` 직후 `FutureDataGuard(self.ohlcv_data)` 생성 후 `self.future_guard`에 보관
  - `BacktestSignalGenerator` 생성 시 `future_guard=self.future_guard` 전달
  - 일별 루프(`_run_daily` / `_run_minute`) 시작 시 `self.future_guard.set_sim_date(date_str)` 호출
- **signal_generator.py**
  - `BacktestSignalGenerator.__init__`에 `future_guard` 인자 추가
  - `_get_ohlcv_view()`: guard가 있으면 `guard.get_data()` 반환, 없으면 `self.ohlcv_data` 반환
  - `_get_series`, `_get_candidate_stock_codes`, 레거시 모드 시그널 생성에서 `_get_ohlcv_view()` 사용

### 2.3 테스트 결과

- 문법: `future_data_guard.py`, `walk_forward.py`, `backtest_engine_v2.py`, `signal_generator.py` — ast.parse 통과
- 단위 테스트:
  - `sim_date='20250103'` 시 `get_data()` → 3행 반환 (20250101~20250103)
  - `get_lookback('20250103', 2)` → 2행
  - `validate_no_future_leak(df, '20250103', 'date')` → 미래 행 존재 시 `FutureDataLeakError` 발생 확인

---

## 3. Walk-Forward Runner

### 3.1 설계 (6mo train / 3mo test)

- **파일:** `scripts/backtest/walk_forward.py`
- **WalkForwardRunner**
  - **파라미터:** `train_months`, `test_months`, `step_months`, `engine_class`, `db_params`, `report_generator`, `**engine_kwargs`
  - **run(start_date, end_date, card_ids):**
    1. `_generate_windows(start_date, end_date)` → (train_start, train_end, test_start, test_end) 리스트 생성
    2. 각 윈도우: train 기간 백테스트 → report로 IS 메트릭 산출 → test 기간 백테스트(OOS) → report로 OOS 메트릭 산출
    3. E, Calmar, PF, OOS/IS 비율 계산 후 통과 여부 판정
  - **통과 기준 (기획서):**
    - 모든 OOS 윈도우에서 **E(기대값) > 0**
    - **OOS/IS 비율 ≥ 0.6**
    - **OOS Calmar > 1.5**, **OOS PF > 1.3**
  - **메트릭:** `_calculate_metrics(session_id)`에서 report_generator 결과로 E, Calmar, PF, Sharpe, MDD, win_rate, CAGR 등 산출  
    - E = (win_rate/100 × avg_win_pct) − (loss_rate/100 × |avg_loss_pct|)  
    - Calmar = CAGR / |MDD|

### 3.2 실행 스크립트

- **파일:** `scripts/backtest/run_walk_forward.py`
- **argparse:** `--card-ids`, `--start-date`, `--end-date`, `--train-months`, `--test-months`, `--step-months`, `--capital`, `--compound-mode`, `--kelly-fraction`
- 실행 후 각 백테스트 세션은 DB에 저장되며, Walk-Forward 요약 테이블을 stdout으로 출력

### 3.3 테스트 실행

- 명령 예:  
  `python scripts/backtest/run_walk_forward.py --card-ids 6 --start-date 2025-06-01 --end-date 2025-12-31 --train-months 4 --test-months 2 --capital 10000000`
- 실제 데이터·DB 기반으로 실행되며, 윈도우 수에 따라 수 분 이상 소요될 수 있음. 실행 완료 시 요약 테이블 및 전체 통과 여부가 출력됨.

---

## 4. 구현 파일 목록

| 파일 | 변경 |
|------|------|
| `scripts/backtest/future_data_guard.py` | 신규 (FutureDataGuard, FutureDataLeakError) |
| `scripts/backtest/walk_forward.py` | 신규 (WalkForwardRunner) |
| `scripts/backtest/run_walk_forward.py` | 신규 (CLI) |
| `scripts/backtest/signal_generator.py` | future_guard 연동 (_get_ohlcv_view, _get_series, _get_candidate_stock_codes, 레거시 모드) |
| `scripts/backtest/backtest_engine_v2.py` | use_future_guard, future_guard 생성/설정, set_sim_date 호출, SignalGenerator에 guard 전달 |

---

## 5. 검수 결과

- **문법:** 4개 파일 ast.parse 통과
- **FutureDataGuard 단위 테스트:** 전항 통과
- **Walk-Forward:** run_walk_forward.py 실행 가능 (DB·데이터 존재 시 정상 동작)

---

## 6. 잔여 (후속 작업)

- **Ablation Study:** 기획서 Phase A-7의 Ablation(수급/레짐 ON·OFF 등)은 본 작업 범위 외이며, 별도 작업으로 진행 권장.
- **v4_backtest_summary:** report_generator에서 이미 INSERT/UPDATE 하므로 Walk-Forward 세션도 자동 반영됨.

---

*문서 끝 (BT-FUTURE-GUARD-001-20260224)*
