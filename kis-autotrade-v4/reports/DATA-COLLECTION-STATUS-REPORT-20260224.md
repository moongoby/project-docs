# 데이터 수집 전체 현황 보고

**확인 일시**: 2026-02-24  
**대상**: 분봉 외 일봉·수급·지수·레짐·호가·유니버스 등 수집 여부 및 최신성

---

## 1. 수집 현황 요약

| 데이터 종류 | 테이블/대상 | 총 행 수 | 최신 일자 | 상태 | 비고 |
|-------------|-------------|----------|-----------|------|------|
| **일봉** | ohlcv_daily | 2,600,387 | 2026-02-23 | ✅ 정상 | cron 18:00 |
| **분봉** | v4_ohlcv_minute | — | 02-19~02-23 | ✅ 수집 중 | systemd + cron 16:00/토 02:00 |
| **종목별 수급** | v4_investor_daily | 166,921 | 2026-02-20 | ⚠️ 지연 | 02-21·02-23·02-24 없음 |
| **시장 수급** | v4_market_investor_daily | 3,612 | 2026-02-23 | ✅ 정상 | cron 18:40 |
| **지수 일봉** | index_daily | 1,467 | 2026-02-13 | ⚠️ 지연 | 약 11일 지연 |
| **시장 레짐** | v4_market_regime_daily | — | 2026-02-13 | ⚠️ 지연 | PRE_MARKET 시 갱신 |
| **섹터 일봉** | v4_sector_daily | 14,725 | 2026-02-23 | ✅ 정상 | 스케줄러 07:50 |
| **순위** | v4_market_ranking | 240 | 2026-02-22 | ⚠️ 1일 지연 | 스케줄러 07:50 |
| **호가 실시간** | v4_orderbook_realtime | 0 | — | ❌ 미수집 | 수집기 inactive |
| **유니버스** | stock_universe (is_active) | 3,844 | — | ✅ 정상 | cron 19:00 |

---

## 2. 데이터별 상세

### 2.1 일봉 (ohlcv_daily)

- **최신**: 2026-02-23
- **수집 경로**: cron 평일 18:00 `backend/scripts/collect_ohlcv_daily.py`
- **상태**: 정상. 당일(02-24)은 장 마감 후 18:00에 수집됨.

### 2.2 분봉 (v4_ohlcv_minute)

- **최근 날짜별**: 02-23 67,695행(181종목), 02-20 72,904(193), 02-19 189,204(500)
- **수집 경로**:  
  - systemd `kis-v41-minute-collector` (collector_minute.py)  
  - cron 평일 16:00·토 02:00 `scripts/minute_batch_cron.sh` (collect_minute_historical.py)
- **상태**: 정상 수집 중. 당일·누락일 보강 및 장 전 순서 변경 적용됨.

### 2.3 종목별 수급 (v4_investor_daily)

- **최신**: 2026-02-20 (02-21, 02-23, 02-24 없음)
- **수집 경로**:  
  - `daily_scheduler` 07:50 장전 수집 (`collect_investor_daily(client, days=5)`)  
  - 수동: `python -m app.services.data_pipeline.run_daily_collection --investor`
- **상태**: ⚠️ 지연. 02-21(토 휴장)·02-23·02-24 미수집.  
  - 07:50 스케줄 미동작/실패 또는 토큰/API 이슈 가능성.  
  - **권장**: 스케줄러 07:50 로그 확인 후, 필요 시 `run_daily_collection --investor` 수동 1회 실행으로 02-23·02-24 보강.

### 2.4 시장 수급 (v4_market_investor_daily)

- **최신**: 2026-02-23
- **수집 경로**: cron 평일 18:40 `scripts/collect_market_investor.py`
- **상태**: 정상.

### 2.5 지수 일봉 (index_daily)

- **최신**: 2026-02-13 (약 11일 지연)
- **수집 경로**: cron 평일 18:30 `scripts/collect_index_daily.sh`
- **상태**: ⚠️ 지연. 02-14~02-23 미수집.  
  - **권장**: 스크립트·토큰·API 확인 후 수동 백필 또는 cron 재등록 확인.

### 2.6 시장 레짐 (v4_market_regime_daily)

- **최신**: 2026-02-13, regime MILD_TREND_UP
- **수집 경로**: 오케스트레이터 **PRE_MARKET** 단계에서 `regime_detector.detect_regime(save=True)` 호출 시 INSERT/UPDATE
- **상태**: ⚠️ 지연. 02-14 이후 미갱신.  
  - PRE_MARKET 미실행 또는 regime_detector 실패 가능.  
  - **권장**: `kis-v41-scheduler` 동작·PRE_MARKET 로그 확인, 필요 시 `scripts/backfill_regime_history.py`로 백필 검토.

### 2.7 섹터 일봉 (v4_sector_daily)

- **최신**: 2026-02-23
- **수집 경로**: daily_scheduler 07:50 `collect_sector_daily(client, days=5)`
- **상태**: 정상.

### 2.8 순위 (v4_market_ranking)

- **최신**: 2026-02-22 (1일 지연)
- **수집 경로**: daily_scheduler 07:50 `collect_rankings(client)`
- **상태**: ⚠️ 1일 지연. 02-23 미반영 가능.  
  - 07:50 스케줄 또는 API 응답 확인 권장.

### 2.9 호가 실시간 (v4_orderbook_realtime)

- **현재 행 수**: 0
- **수집 경로**: `scripts/collection/orderbook_collector.py` (장중 실시간).  
  - systemd `kis-v41-orderbook-collector` 서비스는 **등록·비가동** 상태로 정책상 월요일 장전 시작 예정.
- **상태**: ❌ 미수집. 의도된 비가동이면 현행 유지, 장중 호가 필요 시 서비스 start.

### 2.10 유니버스 (stock_universe)

- **활성 종목 수**: 3,844
- **수집 경로**: cron 평일 19:00 `backend/scripts/collect_stock_universe.py`
- **상태**: 정상.

---

## 3. 수집 스케줄 요약

| 구분 | 스케줄 | 스크립트/서비스 | 대상 테이블 |
|------|--------|------------------|-------------|
| 일봉 | 18:00 1-5 | collect_ohlcv_daily.py | ohlcv_daily |
| 지수 | 18:30 1-5 | collect_index_daily.sh | index_daily |
| 시장 수급 | 18:40 1-5 | collect_market_investor.py | v4_market_investor_daily |
| 유니버스 | 19:00 1-5 | collect_stock_universe.py | stock_universe |
| 분봉 배치 | 16:00 1-5, 02:00 6 | minute_batch_cron.sh | v4_ohlcv_minute |
| 분봉 상시 | systemd | kis-v41-minute-collector | v4_ohlcv_minute |
| 장전 통합 | 07:50 (scheduler) | daily_scheduler | v4_investor_daily, v4_sector_daily, v4_market_ranking |
| 레짐 | PRE_MARKET (scheduler) | orchestrator + regime_detector | v4_market_regime_daily |
| 호가 | 미가동 | orderbook_collector | v4_orderbook_realtime |

---

## 4. 권장 조치

1. **v4_investor_daily (종목별 수급)**  
   - 07:50 장전 수집 로그 확인.  
   - 필요 시: `python -m app.services.data_pipeline.run_daily_collection --investor`로 02-23·02-24 보강.

2. **index_daily (지수)**  
   - `scripts/collect_index_daily.sh` 실행·에러 로그 확인.  
   - 02-14~02-23 구간 수동 수집 또는 원인 조치 후 cron 재검증.

3. **v4_market_regime_daily (레짐)**  
   - kis-v41-scheduler PRE_MARKET 구간 및 regime_detector 로그 확인.  
   - 필요 시 `scripts/backfill_regime_history.py`로 최근 일자 백필 검토.

4. **v4_market_ranking**  
   - 07:50 collect_rankings 실행 여부 및 당일 반영 여부 확인.

5. **v4_orderbook_realtime**  
   - 호가 수집이 필요하면 `kis-v41-orderbook-collector` start; 불필요하면 현행 유지.

---

이 보고서는 DB 조회·코드·cron/서비스 설정 기준으로 작성되었으며, 실제 수집 실패 원인은 각 스크립트·스케줄러 로그로 추가 확인하는 것을 권장합니다.
