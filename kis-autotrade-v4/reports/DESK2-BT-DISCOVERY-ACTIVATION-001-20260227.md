# DESK2-BT-DISCOVERY-ACTIVATION-001 보고서
**작성일:** 2026-02-27  
**목표:** C1~C6 발굴 조건 활성화 → 10일 백테스트 → 전략 다양성 확보 후 성과 분석  
**선행:** DESK2-BT-P0FIX-REVALIDATION-001 (P0 수정 완료, C7만 활성)

---

## 1. Phase A 진단 결과 (C1~C6 비활성 원인)

### 1.1 backtest_runner 발굴 경로
- `DiscoveryManager.scan_all()` 호출: 7개 조건 전부 호출
- 슬롯 필터: `condition_time_slots`로 현재 봉의 `current_slot`이 해당 조건의 활성 슬롯에 있을 때만 `filtered_discoveries`에 포함

### 1.2 조건별 비활성 원인

| 조건 | 원인 |
|------|------|
| **C1 (GAP_UP)** | RVOL_MIN=2.0, MIN_MARKET_CAP=3000억으로 게이트 엄격 |
| **C2 (OPENING_STRONG)** | `_minutes_since_open(indicators)`가 백테스트에서 `datetime.now()` 사용 → 09:00~09:30 구간이 아님 |
| **C3 (VI_EXPLOSION)** | `v4_vi_occurrences` 테이블 없음, feeder에 `vi_triggered`/`pre_rvol`/`daily_vi_count` 미공급 |
| **C4 (INTRADAY_SURGE)** | C2와 동일하게 `_minutes_since_open`이 백테스트 시각 미반영 |
| **C5 (PULLBACK_READY)** | 슬롯/경쟁 제한보다는 조건 자체 통과 빈도 이슈 가능 |
| **C6 (SECTOR_LAG)** | feeder에 `leader_gain_pct`, `follower_change_pct`, `sector_rank`, `follower_volume_trend` 미공급 |
| **C7** | 기존 활성 (P0FIX 기준) |

### 1.3 기타
- **v4_bt_discovery 로그:** runner에서 `write_discovery`/`write_discovery_log` 미호출 → 발굴 이력 DB 미저장

---

## 2. Phase B 수정 내역

### 2.1 C2/C4 — 백테스트 시각 기반 `minutes_since_open`
- **파일:** `historical_price_feeder.py`  
  - `_minutes_since_open_from_ts(timestamp)` 추가: 봉 시각 기준 09:00 KST 이후 경과 분 반환  
  - `get_cumulative_indicators` 반환 dict에 `minutes_since_open` 추가 (빈 봉/전체 공통)
- **파일:** `backtest_runner.py`  
  - `_apply_indicators_to_cache`에서 `minutes_since_open` 등 신규 필드 캐시 반영
- **파일:** `c2_opening_strong.py`, `c4_intraday_surge.py`  
  - `getattr(indicators, "minutes_since_open", None)` 우선 사용, 없을 때만 `_minutes_since_open(indicators)` 호출

### 2.2 C3 — v4_vi_occurrences + feeder 연동
- **마이그레이션:** `scripts/migrations/DESK2_VI_OCCURRENCES_001.sql`  
  - `v4_vi_occurrences` 테이블 생성 (stock_code, vi_time, vi_type, trigger_price 등)
- **데이터:** 2026-02-01~02-25 분봉 기준 5분 내 ±10% 변동 구간을 VI 추정으로 INSERT (319건)
- **feeder:** `_load_vi_occurrences()`, `_vi_triggered_at()`, `_daily_vi_count()` 추가  
  - `get_cumulative_indicators`에 `vi_triggered`, `pre_rvol`, `daily_vi_count` 반영

### 2.3 C1 — 게이트 완화
- **파일:** `c1_gap_discovery.py`  
  - `RVOL_MIN`: 2.0 → **1.5**  
  - `MIN_MARKET_CAP`: 3000억 → **2000억**
- **파일:** `desk2_config.yaml`  
  - `discovery_params.C1`에 `min_rvol: 1.5`, `min_market_cap: 200000000000` 추가

### 2.4 C6 — 섹터 대장주 지표 공급
- **파일:** `historical_price_feeder.py`  
  - `get_cumulative_indicators_all()` 호출 후 `_enrich_sector_leader(indicators_all, timestamp)` 호출  
  - 섹터별 당일 수익률 정렬 후 `leader_gain_pct`, `follower_change_pct`, `sector_rank`, `follower_volume_trend` 부여
- **파일:** `backtest_runner.py`  
  - `_apply_indicators_to_cache`에서 위 4개 필드 캐시 반영

### 2.5 v4_bt_discovery_log 기록
- **파일:** `backtest_runner.py`  
  - 매 봉 `discoveries` 수집 후 `filtered_discoveries` 여부에 따라 `bt_writer.write_discovery_log(..., passed=여부, reject_reason=None 또는 "slot_filter")` 호출

### 2.6 B-검증
- `backtest_runner`, C1~C7 모듈 import 정상 확인

---

## 3. 10일 백테스트 개요

- **대상일:** 2026-02-03, 04, 05, 06, 09, 10, 12, 13, 19, 20 (분봉 존재일)
- **세션명:** `DISC-ACT-{날짜}`  
- **스크립트:** `desk2_live_parity_run.py --date $d --capital 10000000 --session-name "DISC-ACT-$d"`
- **집계 시점:** 10일 전체 실행 완료 후 재집계 권장. 아래는 **4일 완료 시점** 샘플 집계.

---

## 4. 일별 요약 (4일 완료 시점 샘플)

| test_date  | trades | wins | win_rate | total_pnl | return_pct |
|------------|--------|------|----------|-----------+------------|
| 2026-02-03 | 4 | 2 | 50.0 | 14,209 | 0.14 |
| 2026-02-04 | 5 | 0 | 0.0 | -119,817 | -1.20 |
| 2026-02-09 | 5 | 1 | 20.0 | -91,968 | -0.92 |
| 2026-02-10 | 2 | 0 | 0.0 | -40,610 | -0.41 |

---

## 5. C1~C7 발굴 분포 (v4_bt_discovery_log, 4일 샘플)

| discovery_type | total | passed | rejected | pass_rate |
|----------------|-------|--------|----------|-----------|
| C6 | 1,859 | 1,494 | 365 | 80.4 |

- **해석:** 현재 집계 시점에는 C6(SECTOR_FOLLOW)만 로그에 기록됨. C1~C5·C7은 해당 기간 슬롯/게이트에서 발굴이 없거나, 10일 완료 후 재집계 시 추가될 수 있음.

---

## 6. 전략별 성과 (4일 샘플)

| strategy   | trades | wins | avg_pnl | total_pnl | pf   | avg_hold |
|------------|--------|------|---------|-----------+------|----------|
| DELTA_VWAP | 16     | 2    | -15,889 | -254,227  | 0.22 | 2,708    |
| BRAVO_ORB  | 1      | 1    | 4,280   | 4,280     | —    | 300      |

- DELTA_VWAP이 대부분 거래, BRAVO_ORB 1건. C6→FOXTROT_SECTOR/DELTA_VWAP/BRAVO_ORB 분배 후 경쟁에서 DELTA_VWAP 진입 비중이 큼.

---

## 7. 조건→전략 매핑 (4일 샘플)

| discovery_type | strategy   | trades | win_rate | total_pnl |
|----------------|------------|--------|----------|-----------|
| C6             | DELTA_VWAP | 17     | 11.8     | -265,967  |
| C6             | BRAVO_ORB  | 1      | 100.0    | 4,280     |

- C6 발굴이 DELTA_VWAP·BRAVO_ORB로 전략 매칭되어 실행된 구조 확인.

---

## 8. 전체 거래 상세 (PnL ±3% 하이라이트)

- 4일 샘플 기준 **PnL ±3% 이상** 구간 없음 (최대 손실 -1.79%, 최대 수익 +1.71%).
- 상세 리스트는 D-4 SQL로 `s.start_date, t.stock_code, t.strategy_name, t.entry_price, t.exit_price, t.pnl, t.pnl_pct, t.hold_seconds, t.exit_reason` 조회.

---

## 9. 실매매 전환 기준 평가 (4일 샘플)

| 항목 | 값 | 비고 |
|------|-----|------|
| avg_daily_return_pct | -0.63 | 기대 수익률 미달 |
| overall_pf | 0.26 | 1 미만 |
| max_daily_loss_pct | -1.20 | 일 최대 손실 |
| avg_daily_trades | 4.3 | 일 평균 거래 수 |

- **판정:** 4일 샘플 기준 실매매 전환 4대 기준 **PASS 불가**. 10일 완료 후 재집계 및 기준 재검토 권장.

---

## 10. P0FIX 7일 vs DISC-ACT 10일 비교

- P0FIX 7일 결과와 DISC-ACT 10일 최종 결과는 10일 백테스트 완료 후 동일 조건으로 재집계하여 비교표 작성 권장.
- 현재는 DISC-ACT 4일 샘플만 확보된 상태.

---

## 11. 문제점 및 다음 단계

1. **C1·C2·C3·C4·C5·C7 발굴 로그 부재**  
   - 4일 구간에서 discovery_log에는 C6만 존재. 슬롯/게이트·유니버스로 인해 다른 조건이 스캔에서 걸리지 않았을 가능성 있음. 10일 전체 로그 재확인 및 필요 시 C1/C2/C3 게이트·시간대 재점검.

2. **전략 편중**  
   - DELTA_VWAP 비중이 과대. 슬롯별 한도(slot_trade_limits) 미적용 등으로 인한 편중 가능성 검토.

3. **실매매 전환**  
   - 4일 샘플 기준 PF·일평균수익 미달. 10일 완료 후 재평가 및 손절/타겟/보유시간 튜닝 검토.

4. **다음 권장 작업**  
   - 10일 백테스트 완료 후 D-1~D-6 재실행하여 본 보고서 수치 갱신.  
   - `desk2_export_json.py --session-prefix "DISC-ACT"` 로 대시보드 JSON 재생성.  
   - P0FIX 7일과 DISC-ACT 10일 비교표 작성 후 CEO 보고.

---

*본 문서는 DESK2-BT-DISCOVERY-ACTIVATION-001 작업 기준으로 작성되었으며, Absolute Rules(kis-v41-api/monitor/scheduler 미재기동, strategy_cards 변경 없음, v4_positions 직접 수정 없음, go100_* SELECT 전용, v4_bt_* INSERT만 사용, backtest_engine_v2.py 미수정)를 준수함.*
