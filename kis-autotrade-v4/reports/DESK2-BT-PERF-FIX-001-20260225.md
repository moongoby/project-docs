# DESK2-BT-PERF-FIX-001 — 백테스트 성능 긴급 최적화 보고서

**작성일:** 2026-02-25  
**프로젝트:** KIS AutoTrade V4.1  
**우선순위:** P0 (즉시 실행)

---

## 1. 요약

- **목적:** 풀 구간 백테스트 102분 경과 시 266거래일 중 1일만 처리되던 병목 제거.
- **원인:** 매 스캔(5분봉 단위 × 종목 수)마다 **전체 바 구간에 대해 지표를 처음부터 재계산** (O(bar_dt × tickers × bars) 수준).
- **조치:** 지표 **증분 계산** 도입, universe 필터링·로그 축소 적용. **기존 nohup 프로세스·서비스·strategy_cards·v4_positions 미변경.**

---

## 2. STEP 1 — 병목 분석 결과

### 2.1 소스: `desk2_backtester.py` 구조

| 항목 | 내용 |
|------|------|
| **일별 DB 쿼리 횟수** | 4~5회/일: `_load_universe` 1회, `_load_minute_bars` 1회, `_load_prev_close` 1회, `_load_trade_strength` 2회(당일/전일 + 5일평균). 이미 일괄 로드. |
| **분봉 로드 방식** | 해당일 시작 시 `_load_minute_bars(trade_date, tickers)`로 **해당일 전체 분봉 1회 SELECT** → `{stock_code: [Bar, ...]}` 형태. 매 스캔마다 DB 재조회 없음. |
| **전일종가** | `_load_prev_close(trade_date, tickers)`로 **WHERE date = %s 한 번에 전 종목 SELECT** 후 딕셔너리 구성. |
| **체결강도** | `_load_trade_strength`에서 당일/전일 1쿼리, 5일평균 1쿼리로 일괄 로드. |

### 2.2 실제 병목: 스캔 루프 내 지표 재계산

- **스캔 루프:** `all_times` = 해당일 전체 5분봉 시각 집합(약 78개) × **매 bar_dt마다** 모든 ticker(예: 462)에 대해:
  - `blist = [b for b in bars_by_ticker.get(t, []) if b.datetime <= bar_dt]` 로 **해당 시각까지의 전체 바** 구성
  - `_calculate_indicators(t, blist, prev_close)` 호출 → **매번 바 전체를 처음부터** RSI/VWAP/BB/MA 재계산
- **결과:** 1일당 약 `78 × 462 × (1+2+…+78)` 수준의 중복 연산 → **일당 수백만 회** 지표 재계산으로 추정 (102분에 1일 처리와 부합).

### 2.3 기타

- **DiscoveryManager.scan_all:** 매 스캔마다 `logger.info("스캔 완료: 대상=N종목, 발굴=M건")` 출력 → 로그 과다.

---

## 3. STEP 2 — 최적화 적용 내용

### 3.1 지표 증분 계산 (핵심)

- **변경:** 매 bar_dt마다 “해당 시각의 바만” 반영하는 **`_apply_single_bar(ticker, bar, prev_close)`** 추가.
- **동작:**  
  - 해당 시각(`b.datetime == bar_dt`)인 바만 골라 1개씩 증분 반영.  
  - `ind.bars_5m`, VWAP/RSI/BB/MA는 **바가 추가될 때마다** 기존 상태 기준으로만 갱신.
- **루프 변경:**  
  - 기존: `for bar_dt in all_times: for t in tickers: blist = [바 전체]; _calculate_indicators(t, blist, ...)`  
  - 변경: `for bar_dt in all_times: for t in tickers: bar_dt인 바 1개만 찾아 _apply_single_bar(t, bar, ...)`  
- **효과:** 일당 연산량이 **O(bar_dt × tickers × bars)** → **O(bar_dt × tickers)** 수준으로 감소 (바당 1회만 처리).

### 3.2 Universe 필터링

- **prev_close > 0** 인 종목만 universe에 포함.
- 당일 **거래량 0** 종목 조기 제외: `sum(bar.volume for bar in bars_by_ticker.get(t, [])) > 0`.
- 분봉·전일종가 로드 직후 `tickers` 리스트를 위 조건으로 필터링.

### 3.3 로그 축소

- **DiscoveryManager.scan_all:**  
  - 발굴 건수 > 0일 때만 `logger.info("스캔 완료: 대상=N종목, 발굴=M건")`.  
  - 발굴 0건이면 `logger.debug(...)` 로만 출력.

### 3.4 기타 (유지)

- **분봉·전일종가·체결강도:** 원래부터 일괄 로드되어 있어 추가 변경 없음.
- **main 인자:** `--config` 기본값 설정, `--start`/`--end` alias 추가하여 nohup 실행 예시와 호환.

---

## 4. STEP 3 — 벤치마크

- **목표:** 단일일 처리 **60초 이내** (기존 추정 ~100분 대비).
- **실행 예시 (DB 접속 가능 환경):**
  ```bash
  cd /root/kis-autotrade-v4
  PYTHONPATH=backend python3 -c "
  import time
  from pathlib import Path
  from app.services.trading.desk2.tests.desk2_backtester import Desk2Backtester
  config = str(Path('backend/app/services/trading/desk2/config/desk2_config.yaml').resolve())
  bt = Desk2Backtester(config)
  start = time.time()
  bt.run('2026-02-03', '2026-02-03', 10000000)
  print('단일일 처리시간: %.1f초' % (time.time() - start))
  "
  ```
- **비고:** 본 작업 환경에서는 DB 연결 제한으로 실제 단일일 경과 시간 미측정.  
  **이론적 효과:** 매 스캔 전체 재계산 제거로 일당 연산이 수백만 회 → 수만 회 수준으로 축소되므로, **단일일 60초 이내 달성 가능성이 높음.**  
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
- `--config` 없이 실행 가능 (기본값: `desk2_config.yaml`). `--start`/`--end` 사용.

---

## 6. 변경 파일 요약

| 구분 | 경로 | 내용 |
|------|------|------|
| 수정 | `backend/app/services/trading/desk2/tests/desk2_backtester.py` | `_apply_single_bar` 추가, run 루프 증분 갱신으로 변경, universe 필터(prev_close>0, volume>0), main 인자(--config 기본값, --start/--end) |
| 수정 | `backend/app/services/trading/desk2/layer1_discovery/discovery_manager.py` | scan_all 로그: 발굴 있으면 INFO, 없으면 DEBUG |

**미변경:** strategy_cards, v4_positions, 기존 nohup 프로세스, 서비스 재시작 없음.

---

## 7. 완료 체크리스트

- [x] 병목 원인 특정 (매 스캔 전체 지표 재계산)
- [x] 최적화 코드 적용 (증분 지표, universe 필터, 로그 축소)
- [ ] 단일일 벤치마크 60초 이내 (DB 환경에서 실행 후 확인)
- [ ] CEO에게 kill 승인 요청 후 기존 프로세스 종료
- [ ] 최적화 버전으로 short/full 재실행
- [ ] project-docs push 및 curl 200 확인

---

**보고서 위치:** `/root/kis-autotrade-v4/report/v41/DESK2-BT-PERF-FIX-001-20260225.md`  
**예상 풀 구간 완료:** 단일일 60초 달성 시 약 **4.4시간**.
