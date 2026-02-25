# DESK2-BT-PERF-FIX-001 — 백테스트 성능 긴급 최적화 보고서

**작성일:** 2026-02-25  
**프로젝트:** KIS AutoTrade V4.1  
**우선순위:** P0 (즉시 실행)

---

## 1. 요약

- **목적:** 풀 구간 백테스트 102분 경과 시 266거래일 중 1일만 처리되던 병목 제거.
- **원인:** 매 bar_dt(5분봉 시각)마다 **전체 종목×전체 바 리스트 선형 스캔**으로 해당 시각 바 탐색(O(tickers×bars) × 78회) 및 매 스캔마다 INFO 로그 과다 출력.
- **조치:** 시각별 바 인덱스(`time_to_bars`) 도입, 전일종가 선로드 후 분봉 로드 대상 축소, 로그 10분봉/DEBUG 축소. **기존 nohup 프로세스·서비스·strategy_cards·v4_positions 미변경.**

---

## 2. STEP 1 — 병목 분석 결과

### 2.1 소스: `desk2_backtester.py` 구조

| 항목 | 내용 |
|------|------|
| **일별 DB 쿼리 횟수** | 5회/일: `_load_universe` 1회, `_load_prev_close` 1회, `_load_minute_bars` 1회, `_load_trade_strength` 2회(당일/전일 + 5일평균). 이미 일괄 로드. |
| **분봉 로드 방식** | 해당일 `_load_minute_bars(trade_date, tickers)`로 **해당일 전체 분봉 1회 SELECT** → `{stock_code: [Bar, ...]}`. 매 스캔마다 DB 재조회 없음. |
| **전일종가** | `_load_prev_close(trade_date, tickers)`로 **WHERE date = %s 한 번에 전 종목 SELECT** 후 딕셔너리 구성. |
| **체결강도** | `_load_trade_strength`에서 당일/전일 1쿼리, 5일평균 1쿼리로 일괄 로드. |

### 2.2 실제 병목: 스캔 루프 내 바 탐색

- **스캔 루프:** `all_times` = 해당일 5분봉 시각 약 78개. **매 bar_dt마다**:
  - `for t in tickers: for b in bars_by_ticker.get(t, []): if b.datetime == bar_dt` 로 **해당 시각의 바 1개** 탐색 → 462종목 × 평균 78바 = **약 3.6만 회 비교/일당 bar_dt 1개**, 일당 총 **약 78 × 3.6만 ≈ 280만 회** 선형 스캔.
- **지표:** 이미 `_apply_single_bar`로 증분 갱신 중. 매 스캔 전체 재계산 없음.
- **DiscoveryManager.scan_all:** 매 스캔(78회)마다 발굴 건수 > 0이면 `logger.info` → 로그 과다. base_condition/base_strategy에서도 발굴·매매 시마다 INFO.

### 2.3 스캔 루프 구조

- 5분봉 시각 단위로 `all_times` 순회 → 매 시각마다 462종목 바 증분 반영 후 `scan_all(tickers, cache)` 호출.
- 1일 ≈ 78 시각 × (바 적용 + discovery 5개 조건 × 462종목).

---

## 3. STEP 2 — 최적화 적용 내용

### 3.1 시각별 바 인덱스 (핵심)

- **변경:** 분봉 로드 후 `time_to_bars: Dict[datetime, List[Tuple[str, Bar]]]` 구성. `bar_dt`당 해당 시각의 `(ticker, bar)` 리스트만 보관.
- **루프:** `for bar_dt in all_times: for t, b in time_to_bars.get(bar_dt, []): _apply_single_bar(t, b, ...)` — **해당 시각에 실제 존재하는 종목만** 순회, 선형 스캔 제거.
- **효과:** O(tickers × bars) × 78 → O(실제 바 개수) 수준으로 감소.

### 3.2 로드 순서 및 universe 필터링

- **순서:** `_load_universe` → `_load_prev_close(universe)` → **prev_close > 0 필터** → `_load_minute_bars(필터된 tickers)` → `_load_trade_strength` → **거래량 > 0 필터**.
- **효과:** 전일 종가 없는 종목은 분봉 로드 대상에서 제외되어 쿼리·메모리 감소.

### 3.3 로그 축소

- **DiscoveryManager.scan_all:** `bar_dt` 인자 추가. 발굴 건수 > 0일 때 **bar_dt.minute % 10 == 0** 인 시각(10분봉 단위)에서만 `logger.info`, 그 외는 `logger.debug`. 발굴 0건은 계속 `logger.debug`.
- **base_condition._build_signal:** 발굴 로그 `logger.info` → `logger.debug`.
- **base_strategy (evaluate / manage_position / _check_target_exit):** 시그널 만료·매매신호·손절·타임아웃·목표도달 로그 `logger.info` → `logger.debug`.
- **desk2_backtester:** 일별 1회만 `logger.info("DESK2-BT [날짜] universe=N bars=M")`.

### 3.4 기타

- **지표:** 기존처럼 `_apply_single_bar`로 증분 갱신 유지. RSI/BB/VWAP/MA 매 스캔 전체 재계산 없음.
- **분봉·전일종가·체결강도:** 원래부터 일괄 로드, 변경 없음.

---

## 4. STEP 3 — 벤치마크

- **목표:** 단일일 처리 **60초 이내** (기존 추정 ~100분 대비).
- **실행 예시 (DB 접속 가능 환경):**
  ```bash
  cd /root/kis-autotrade-v4
  PYTHONPATH=backend python3 -c "
  import time
  from app.services.trading.desk2.tests.desk2_backtester import Desk2Backtester
  config = '/root/kis-autotrade-v4/backend/app/services/trading/desk2/config/desk2_config.yaml'
  bt = Desk2Backtester(config)
  start = time.time()
  result = bt.run('2026-02-03', '2026-02-03', 10000000)
  elapsed = time.time() - start
  print('단일일 처리시간: %.1f초' % elapsed)
  print('total_trades:', result.get('total_trades'), 'pass:', result.get('pass'))
  "
  ```
- **비고:** 본 작업 환경에서는 DB/데이터 미제공으로 실제 단일일 경과 시간 미측정.  
  **이론적 효과:** 시각별 바 인덱스로 일당 수백만 회 선형 스캔 제거 + 로그 축소로 I/O 부담 감소 → **단일일 60초 이내 달성 가능성 높음.**  
  **풀 구간 예상:** 266일 × 60초 ≈ **약 4.4시간** (기존 19일 예상 대비 대폭 단축).

---

## 5. STEP 4 — 기존 프로세스 종료 및 재실행 (CEO 승인 후)

- **규칙:** 기존 nohup 프로세스 kill은 **CEO가 직접 수행**할 때까지 대기. 서비스 재시작 금지.
- **승인 후 예시:**
  ```bash
  kill 3518833 3518925
  ```
- **재실행 (short 구간):**
  ```bash
  cd /root/kis-autotrade-v4
  nohup bash -c 'PYTHONPATH=backend python3 \
    backend/app/services/trading/desk2/tests/desk2_backtester.py \
    --start 2026-02-01 --end 2026-02-14 --capital 10000000 \
    --strategy ALL' \
    > report/v41/desk2-bt/short_bt_result_v2.txt 2>&1 &
  ```
- **재실행 (풀 구간):**
  ```bash
  nohup bash -c 'PYTHONPATH=backend python3 \
    backend/app/services/trading/desk2/tests/desk2_backtester.py \
    --start 2025-06-01 --end 2026-02-21 --capital 10000000 \
    --strategy ALL' \
    > report/v41/desk2-bt/full_bt_result_v2.txt 2>&1 &
  ```
- `--config` 없이 실행 가능 (기본값: desk2_config.yaml). `--start`/`--end` 사용.

---

## 6. 변경 파일 요약

| 구분 | 경로 | 내용 |
|------|------|------|
| 수정 | `backend/app/services/trading/desk2/tests/desk2_backtester.py` | `defaultdict` 사용, 로드 순서(prev_close 선로드→필터→분봉), `time_to_bars` 인덱스 구성 및 루프에서 시각별 바만 적용, `scan_all(..., bar_dt=bar_dt)`, 일별 INFO 1회 |
| 수정 | `backend/app/services/trading/desk2/layer1_discovery/discovery_manager.py` | `scan_all(..., bar_dt=None)` 추가, 10분봉 단위에서만 INFO 로그 |
| 수정 | `backend/app/services/trading/desk2/layer1_discovery/base_condition.py` | 발굴 로그 `logger.info` → `logger.debug` |
| 수정 | `backend/app/services/trading/desk2/layer2_strategy/base_strategy.py` | 시그널 만료·매매신호·손절·타임아웃·목표도달 로그 `logger.info` → `logger.debug` |

**미변경:** strategy_cards, v4_positions, 기존 nohup 프로세스, 서비스 재시작 없음.

---

## 7. 완료 체크리스트

- [x] 병목 원인 특정 (시각별 바 선형 스캔, 로그 과다)
- [x] 최적화 코드 적용 (time_to_bars 인덱스, 로드 순서, 로그 축소)
- [ ] 단일일 벤치마크 60초 이내 (DB 환경에서 실행 후 확인)
- [ ] CEO에게 kill 승인 요청 후 기존 프로세스 종료
- [ ] 최적화 버전으로 short/full 재실행
- [ ] project-docs push 및 curl 200 확인

---

## 8. DESK2-BT-PERF-DEBUG-002 — 디버그 실행 결과 (2026-02-25)

### 8.1 문제

- **최적화 전:** 2026-02-03 단일일에서 498종목, 186,884 bars, ALPHA_GAP 거래 발생 확인됨.
- **최적화 후:** 같은 날짜에서 `total_trades=0`, 처리시간 0.000초 → 증분 계산 전환 과정에서 로직 파손 의심.

### 8.2 STEP 1 — 디버그 로그 삽입

`desk2_backtester.run()` 내 다음 위치에 **logger.debug** 로그 추가 (DEBUG 레벨에서만 출력):

| 위치 | 로그 내용 |
|------|-----------|
| 거래일 루프 진입 직후 | `DAY=%s` |
| _load_universe 직후 | `universe=%d` |
| _load_prev_close 직후 | `prev_close=%d종목` |
| _load_minute_bars 직후 | `bars=%d종목, total=%d건` |
| all_times 생성 직후 | `all_times=%d개` |
| 스캔 루프 첫 bar_dt | `first_scan: bar_dt=... tickers=%d` |
| _apply_single_bar 직후 (첫 ticker) | `indicator sample: rsi=... vwap=...` |
| discovery_manager.scan_all 직후 | `discoveries=%d` |
| 전략 매칭 후 | `signals=%d` |

**실행 예시 (디버그 출력 보려면 DEBUG 레벨):**
```bash
cd /root/kis-autotrade-v4
PYTHONPATH=backend python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from pathlib import Path
from app.services.trading.desk2.tests.desk2_backtester import Desk2Backtester
config = str(Path('backend/app/services/trading/desk2/config/desk2_config.yaml').resolve())
bt = Desk2Backtester(config)
result = bt.run('2026-02-03', '2026-02-03', 10000000)
print('RESULT:', result)
" 2>&1 | tee report/v41/desk2-bt/debug_v2_result.txt
```

### 8.3 STEP 2 — 원인 분석 (0이 되는 첫 지점)

| 첫 0 지점 | 원인 | 대응 |
|-----------|------|------|
| **universe=0** | _load_universe 쿼리 결과 없음. 해당일 `v4_ohlcv_minute` 데이터 없거나 DB 미연결. | DB에 해당일 분봉 데이터 존재 여부 확인. 데이터 존재 환경에서 동일 명령 재실행 시 다음 단계 확인. |
| bars=0 | _load_minute_bars 날짜 포맷 또는 tickers 비어 있음. | prev_close 필터 후 tickers 비어 있지 않은지 확인. |
| prev_close=0 | ohlcv_daily 날짜(YYYYMMDD)·컬럼(close AS close_price) 확인. | DESK2-BT-DEBUG-001 반영 여부 확인. |
| all_times=0 | bars에서 시간 추출 실패. | time_to_bars 구성 로직 확인. |
| discoveries=0 | _apply_single_bar가 지표를 갱신하지 못함. | bar_dt/datetime 타입 일치, bars_5m append 확인. |
| signals=0 | 발굴은 되나 전략 매칭 실패. | 전략 evaluate 조건·지표 초기값 확인. |

**본 환경 실행 결과:** `universe=0` → 해당 환경 DB에 2026-02-03 분봉 데이터 없음. 데이터 있는 환경에서 실행 시 universe=498 등으로 나오며, 그때는 위 표의 후속 단계에서 첫 0 위치 확인 가능.

### 8.4 STEP 3 — 적용한 수정

1. **Volume 필터 폴백**  
   거래량 > 0 필터 후 `tickers`가 비었지만 `bars_by_ticker`에 키가 있으면, 해당 키를 tickers로 복원하여 해당일 스캔이 누락되지 않도록 함.
2. **디버그 로그**  
   print 제거, `logger.debug`로 변경하여 기본 실행에는 영향 없고, 원인 추적 시 `logging.basicConfig(level=logging.DEBUG)`로 재현 가능.

### 8.5 완료 조건 (데이터 환경에서 확인)

- 2026-02-03 단일일에서 `total_trades > 0`
- 처리시간 60초 이내
- 최적화 전과 동일한 발굴/거래 패턴 확인

---

**보고서 위치:** `/root/kis-autotrade-v4/report/v41/DESK2-BT-PERF-FIX-001-20260225.md`  
**예상 풀 구간 완료:** 단일일 60초 달성 시 약 **4.4시간**.
