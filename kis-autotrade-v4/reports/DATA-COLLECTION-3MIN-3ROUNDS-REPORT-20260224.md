# 실시간 제외 데이터 수집 조치 및 3분 단위 3회 결과 보고

**작업 일시**: 2026-02-24  
**범위**: 실시간 데이터 수집(호가 등) 제외, 일봉·분봉·수급·지수·레짐·순위·섹터·유니버스 등 전부 확인 후 수집되도록 조치

---

## 1. Baseline (조치 전)

| 데이터 | 테이블 | 최신 일자 | 비고 |
|--------|--------|-----------|------|
| 일봉 | ohlcv_daily | 20260223 | 정상 |
| 분봉 | v4_ohlcv_minute | 02-19~02-23 | 정상 수집 중 |
| 종목별 수급 | v4_investor_daily | 2026-02-20 | ⚠️ 02-21·02-23·02-24 없음 |
| 지수 일봉 | index_daily | 20260213 | ⚠️ 약 11일 지연 |
| 시장 레짐 | v4_market_regime_daily | 2026-02-13 | ⚠️ 지연 |
| 섹터 | v4_sector_daily | 2026-02-23 | 정상 |
| 순위 | v4_market_ranking | 2026-02-22 | ⚠️ 1일 지연 |
| 시장 수급 | v4_market_investor_daily | 2026-02-23 | 정상 |

---

## 2. 조치 내용

### 2.1 수급 수집기 오류 수정

- **원인**: `collector_investor.py`의 `_get_target_stocks()`에서 `is_active = 1` 사용. PostgreSQL에서 `is_active`는 boolean이라 `boolean = integer` 오류 발생.
- **수정**: `is_active = 1` → `is_active = true`.
- **파일**: `backend/app/services/data_pipeline/collector_investor.py`

### 2.2 수급·순위 수집 실행

- **명령**: `python -m app.services.data_pipeline.run_daily_collection --investor --ranking --days 10`
- **결과**: 수급 수집 정상 진행(3844종목×10일). 순위는 별도 1회 실행으로 02-24 반영.

### 2.3 지수 일봉 수집

- **원인**: `scripts/collection/historical_backfill.py --index-only`가 `legacy/.env`의 KIS 키만 사용해 토큰 실패.
- **조치**: `USE_KIS_CONFIG=1`로 실행해 kis_configs(DB) 토큰 사용.
- **실행**: `USE_KIS_CONFIG=1 PYTHONPATH=... python scripts/collection/historical_backfill.py --index-only --start 20260214 --end 20260224`
- **결과**: index_rows=9, index_daily 최신일 20260223으로 갱신.
- **크론 반영**: `scripts/collect_index_daily.sh`에 `USE_KIS_CONFIG=1` 추가해 향후 크론에서도 kis_configs 사용하도록 수정.

### 2.4 레짐 백필

- **1차**: index_daily가 02-13까지라 `backfill_regime_history.py --from 20260214 --to 20260224` → 처리 0일.
- **2차**: 지수 수집으로 index_daily 02-23 갱신 후 동일 명령 재실행 → 처리 3일, 새로 삽입 3건. v4_market_regime_daily 최신일 2026-02-23.

### 2.5 순위 수집

- **실행**: `run_daily_collection --ranking`
- **결과**: VOLUME_TOP·CHANGE_RATE_UP 2종 수집 성공, 일부 API(404 등) 실패. v4_market_ranking 최신일 2026-02-24.

---

## 3. 3분 단위 3회 결과

### 1차 (조치 시작 후 3분)

| 데이터 | 최신 일자 |
|--------|-----------|
| ohlcv_daily | 20260223 |
| v4_investor_daily | **2026-02-23** (갱신됨) |
| index_daily | 20260213 |
| v4_market_regime_daily | 2026-02-13 |
| v4_sector_daily | 2026-02-23 |
| v4_market_ranking | 2026-02-22 |

### 2차 (6분 후)

- v4_investor_daily 02-23 유지. 나머지 동일.

### 3차 (9분 후)

- 동일. (이후 지수·레짐·순위 추가 조치 수행)

---

## 4. 추가 조치 후 최종 현황

| 데이터 | 테이블 | 최신 일자 | 상태 |
|--------|--------|-----------|------|
| 일봉 | ohlcv_daily | 20260223 | ✅ |
| 종목별 수급 | v4_investor_daily | 2026-02-23 | ✅ 조치 반영 |
| 지수 일봉 | index_daily | 20260223 | ✅ USE_KIS_CONFIG=1 조치 |
| 시장 레짐 | v4_market_regime_daily | 2026-02-23 | ✅ 백필 3일 추가 |
| 섹터 | v4_sector_daily | 2026-02-23 | ✅ |
| 순위 | v4_market_ranking | 2026-02-24 | ✅ 순위 수집 1회 실행 |
| 시장 수급 | v4_market_investor_daily | 2026-02-23 | ✅ |
| 분봉 | v4_ohlcv_minute | 02-19~02-23 | ✅ (기존 수집기 유지) |

---

## 5. 요약

- **수정한 코드**: `collector_investor.py` (is_active = true), `collect_index_daily.sh` (USE_KIS_CONFIG=1).
- **실행한 수집**: 수급(10일)·순위·지수(02-14~02-24)·레짐 백필(02-14~02-24).
- **3분×3회**: 1차에서 v4_investor_daily 02-23 갱신 확인. 2·3차 유지. 이후 지수·레짐·순위 조치로 전 항목 최신일 확보.
- **실시간 수집**(v4_orderbook_realtime 등)은 제외했으며, 호가 수집기는 정책상 비가동 유지.

이제 실시간을 제외한 모든 배치 수집이 최신일까지 반영된 상태입니다.
