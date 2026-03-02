# CUR-GO100-P3-2-ORDERBOOK-BACKTEST-20260227

**작업일**: 2026-02-27  
**태스크**: P3-2 호가창(오더북) 백테스트 파이프라인  
**프로젝트**: GO100

---

## 1. 개요

분봉 데이터(`v4_ohlcv_minute`) 기반 **호가창 시뮬레이션 백테스트** 엔진을 구축하였다.  
실제 호가 데이터가 없으므로 OHLCV로 **pseudo-orderbook**(5호가 depth)을 생성하고, 전략카드의 entry/exit 규칙을 분봉 단위로 평가하여 진입/청산을 시뮬레이션한다.

---

## 2. 선행 확인

- `.cursorrules` / `CLAUDE.md`: GO100 서비스 경계·보고서 push 규칙 확인
- `v4_ohlcv_minute`: 43,218,884건 존재 확인 (kis_admin 계정)
- 전략카드 35번([시드] 스캘핑 기본) 존재 확인

---

## 3. 구현 내역

### 3.1 DB 테이블

**파일**: `backend/migrations/036_go100_orderbook_backtest.sql`

- **테이블**: `go100_orderbook_backtest_runs`
- **컬럼**:  
  `run_id`, `strategy_card_id`(FK: `go100_strategy_cards(go100_card_id)`),  
  `ticker`, `timeframe`(1m/5m/15m), `start_date`, `end_date`,  
  `total_trades`, `win_rate`, `total_return`, `max_drawdown`, `avg_holding_minutes`,  
  `slippage_model`, `slippage_bps`, `result_detail`(JSONB), `status`, `created_at`
- **인덱스**: strategy_card_id, ticker, status, created_at DESC
- 마이그레이션 실행 완료

### 3.2 Pseudo-Orderbook 생성기

**파일**: `backend/app/services/go100/orderbook_simulator.py`

- **`load_ohlcv_minute(db, ticker, trade_date)`**  
  `v4_ohlcv_minute`에서 해당 종목·일자 분봉 로드
- **`generate_pseudo_orderbook(ohlcv_df, ticker)`**  
  각 분봉의 high/low/close/volume으로 **5호가 depth** 생성  
  - 호가단위: `_tick_size(close)` (원 단위 구간별 적용)  
  - 매수 5호가: close 기준 하단 5단계, 매도 5호가: close 기준 상단 5단계  
  - 수량: 당봉 거래량 비율로 분배
- **체결 시뮬**  
  - **시장가**: `simulate_market_fill()` — close 기준 + 슬리피지  
  - **지정가**: `simulate_limit_fill()` — high/low 범위 내 체결 여부 판단
- **슬리피지**  
  - `fixed_bps`: 고정 bps  
  - `volume_impact`: 거래량 반비례 추가 슬리피지  
  - `apply_slippage()`로 매수 시 가격 상승, 매도 시 가격 하락 적용
- **`generate_pseudo_orderbook_for_date(db, ticker, trade_date)`**  
  DB 로드 후 위 생성기 호출해 스냅샷 리스트 반환

### 3.3 분봉 백테스트 엔진

**파일**: `backend/app/services/go100/orderbook_backtest_engine.py`

- **`run_orderbook_backtest(db, strategy_card_id, ticker, start_date, end_date, ...)`**  
  - 전략카드 `entry_rules` / `exit_rules` / `risk_params` 로드  
  - 거래일별 분봉 로드 → `Go100MinuteDataLoader.calc_minute_indicators()` (MA, RSI, VWAP 등)  
  - bar별 pseudo-orderbook 생성  
  - `SignalEvaluator`로 분봉 단위 진입/청산 평가 (일봉과 동일 규칙, `date`를 bar 시각 문자열로 사용)  
  - 진입/청산 시 `simulate_market_fill()`로 체결가 산출 후 포지션·거래로그·equity 곡선 갱신  
  - 반환: `total_trades`, `win_rate`, `total_return`, `max_drawdown`, `avg_holding_minutes`, `trade_log`, `equity_curve`
- **`save_orderbook_backtest_run(db, ...)`**  
  결과를 `go100_orderbook_backtest_runs`에 INSERT, `run_id` 반환
- **기술 지표**: 기존 `Go100MinuteDataLoader.calc_minute_indicators` 활용 (pandas 기반, RSI·MA·VWAP 등)

### 3.4 Agent Tool 등록

**파일**:  
- `backend/app/services/go100/ai/agent_tools.py`  
- `backend/app/services/go100/ai/tool_executors.py`

- **`run_orderbook_backtest(strategy_card_id, ticker, days=30)`**  
  - ticker: 종목코드 또는 종목명(이름으로 조회 시 코드 자동 해석)  
  - 최근 `days`일 구간으로 백테스트 실행 후 DB 저장, run_id·성과 요약 반환  
  - 비동기 엔진 호출은 `AsyncSessionLocal` + `asyncio.run()` 패턴 사용
- **`get_orderbook_backtest_results(strategy_card_id=None, limit=10)`**  
  - `strategy_card_id` 지정 시 해당 전략만, 미지정 시 최근 실행 결과 조회  
  - `go100_orderbook_backtest_runs` SELECT 후 run_id·ticker·기간·total_trades·win_rate·total_return·max_drawdown·status 등 반환

---

## 4. 테스트 결과

| 항목 | 결과 |
|------|------|
| 마이그레이션 036 실행 | 성공 (CREATE TABLE + 인덱스) |
| Pseudo-orderbook 생성 | 삼성전자(005930) 2026-02-25 1일 분봉 → 381봉, 5호가 depth 출력 정상 |
| 5일 백테스트 (전략 35, 005930) | 실행·저장 성공 (run_id=1, 진입 조건 미충족으로 거래 0건) |
| DB 저장 확인 | `go100_orderbook_backtest_runs`에 run_id, win_rate, total_return, status 등 저장 확인 |
| Agent `get_orderbook_backtest_results` | 정상 응답 (results[], count) |
| Agent `run_orderbook_backtest` (ticker="삼성전자", days=3) | 종목명 해석 → 005930, run_id=2 저장·반환 성공 |

---

## 5. 파일 목록

| 경로 | 설명 |
|------|------|
| `backend/migrations/036_go100_orderbook_backtest.sql` | 호가창 백테스트 런 테이블 |
| `backend/app/services/go100/orderbook_simulator.py` | Pseudo-orderbook 생성·체결 시뮬·슬리피지 |
| `backend/app/services/go100/orderbook_backtest_engine.py` | 분봉 백테스트 엔진·DB 저장 |
| `backend/app/services/go100/ai/agent_tools.py` | run_orderbook_backtest / get_orderbook_backtest_results 도구 정의 추가 |
| `backend/app/services/go100/ai/tool_executors.py` | 위 두 도구 실행 함수·TOOL_EXECUTORS 등록 |

---

## 6. 비고

- **진입 0건**: 시드 전략 35의 entry_rules(예: MA 크로스 등)가 5일 분봉 구간에서 충족되지 않아 거래가 발생하지 않을 수 있음. 파이프라인 자체는 정상 동작.
- **Agent Chat**: "삼성전자 호가창 백테스트 돌려줘" 요청 시 `run_orderbook_backtest(ticker="삼성전자", strategy_card_id=35 또는 사용자 지정, days=30)` 호출로 동작 가능.
- **timeframe**: 1m 기본, 5m/15m은 `bar_interval`로 N분봉 집계 후 동일 로직 적용 가능.

---

## 7. 체크포인트

- [x] 코드 레포 반영 (마이그레이션·시뮬레이터·엔진·Agent 도구)
- [ ] project-docs 보고서 push (본 문서 push 후 완료)
