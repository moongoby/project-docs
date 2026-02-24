# DATA-PIPELINE-AUDIT-001 — 전체 데이터 수집 파이프라인 감사 + 미수집 데이터 식별

**작업 ID:** DATA-PIPELINE-AUDIT-001  
**일시:** 2026-02-24 KST  
**작업 유형:** 읽기 전용 조회 (SELECT만, 테이블 생성/변경 없음)  
**프로젝트:** /root/kis-autotrade-v4  

---

## 1. 요약

| 항목 | 결과 |
|------|------|
| public 스키마 테이블 수 | **170개** |
| 스코어링 핵심 테이블 | v4_investor_daily, v4_sector_daily, v4_stock_sector, ohlcv_daily, 분봉 파티션 — 수집 경로 존재. 테마/스캘핑 피처는 미수집 또는 비어 있음 |
| 호가/체결/재무/뉴스 테이블 | orderbook_snapshots, price_tick_snapshots, financial_ratios, stock_fundamentals, v4_orderbook_realtime, v4_tick_data 존재 (일부는 레거시 또는 별도 수집) |
| 데이터 수집 코드 | backend/app/services/data_pipeline/ 10개 파일, scripts/ 내 collect·backfill 관련 다수. 스케줄: daily_scheduler 07:50/15:40 등 |

---

## 2. STEP 1 — DB 전체 테이블 (크기·행 수 상위)

*pg_total_relation_size 기준 내림차순, 상위 40개만 표기.*

| schemaname | tablename | total_size | est_rows |
|------------|-----------|------------|----------|
| public | v4_ohlcv_minute_2026_01 | 1028 MB | 3589928 |
| public | v4_ohlcv_minute_2025_12 | 983 MB | 3731501 |
| public | v4_ohlcv_minute_2025_07 | 945 MB | 3614107 |
| public | v4_ohlcv_minute_2025_09 | 935 MB | 3625874 |
| public | v4_ohlcv_minute_2025_04 | 860 MB | 3180572 |
| public | v4_ohlcv_minute_2025_08 | 824 MB | 3047545 |
| public | v4_ohlcv_minute_2025_03 | 793 MB | 2942183 |
| public | v4_ohlcv_minute_2025_06 | 790 MB | 2910200 |
| public | v4_ohlcv_minute_2025_10 | 789 MB | 2945597 |
| public | v4_ohlcv_minute_2025_05 | 755 MB | 2718477 |
| public | ohlcv_daily | 671 MB | 2578288 |
| public | v4_ohlcv_minute_2026_02 | 653 MB | 2526816 |
| public | v4_ohlcv_minute_2025_11 | 480 MB | 1817114 |
| public | _legacy_ohlcv_1m_history_20260220 | 361 MB | 1434248 |
| public | _legacy_market_data_min_20260220 | 292 MB | 1501288 |
| public | v4_ohlcv_minute_2025_02 | 253 MB | 980364 |
| public | market_data_min | 175 MB | 896323 |
| public | ohlcv_1m_history | 146 MB | 907975 |
| public | v4_investor_daily | 139 MB | 180888 |
| public | ohlcv_weekly | 50 MB | 357381 |
| public | orderbook_snapshots | 42 MB | 35894 |
| public | real_trades | 39 MB | 132506 |
| public | v4_backtest_trades | 37 MB | 184512 |
| public | v4_signals | 34 MB | 101274 |
| … | (이하 146개 테이블) | … | … |

- **v4_ohlcv_minute**: 파티션 뷰(0 bytes)이며 실제 데이터는 `v4_ohlcv_minute_YYYY_MM` 파티션에 있음. 파티션 reltuples 합계 약 **4,331만 행** 수준.
- 전체 170개 테이블 목록은 동일 쿼리로 재실행 시 확인 가능.

---

## 3. STEP 2 — 데이터 수집 코드 전수 파악

### 3.1 backend/app/services/data_pipeline/ (*.py)

```
backend/app/services/data_pipeline/collector_investor.py
backend/app/services/data_pipeline/collector_minute_ohlcv.py
backend/app/services/data_pipeline/collector_minute.py
backend/app/services/data_pipeline/collector_ranking.py
backend/app/services/data_pipeline/collector_theme_sector.py
backend/app/services/data_pipeline/__init__.py
backend/app/services/data_pipeline/kis_api_client.py
backend/app/services/data_pipeline/minute_to_daily.py
backend/app/services/data_pipeline/ohlcv_collector.py
backend/app/services/data_pipeline/run_daily_collection.py
```

- **collector_investor**: v4_investor_daily (수급)
- **collector_theme_sector**: v4_theme_master, v4_sector_daily (테마 리스트, 업종 일봉)
- **collector_ranking**: v4_market_ranking
- **collector_minute / collector_minute_ohlcv**: 분봉 수집
- **minute_to_daily**: 분봉→일봉 집계
- **ohlcv_collector**: 일봉(ohlcv_daily) 수집
- **run_daily_collection**: 일일 통합 실행 (--all, --investor, --theme, --sector, --ranking, --test)

### 3.2 scripts/ — collect·fetch·crawl·backfill 관련 (일부만 열거)

| 구분 | 경로 |
|------|------|
| 수집 | scripts/collect_minute_historical.py, scripts/collect_ohlcv_daily.py, scripts/collect_ohlcv_daily_history.py, scripts/collect_historical_daily.py |
| 수집 | scripts/collect_index_daily.sh, scripts/collection/historical_backfill.py, scripts/collection/collect_investor_data.py, scripts/collection/orderbook_collector.py, scripts/collection/fundamental_collector.py |
| 수집 | scripts/collect_market_investor.py, scripts/collect_market_investor_history.py, scripts/collect_vkospi.py, scripts/collect_vkospi_alt.py, scripts/collect_sector_history.py, scripts/collect_stock_industry.py |
| 백필 | scripts/backfill_regime_history.py, scripts/analysis/backfill_regime_data.py, scripts/analysis/generate_regime_data.py, scripts/backfill_signals.py |
| 스케줄/크론 | scripts/minute_batch_cron.sh, scripts/collection/legacy/collection_scheduler.sh, scripts/collection/legacy/run_top100_collector.sh |

### 3.3 schedule / cron / interval 참조 (backend/app, *.py)

- **daily_scheduler.py**: 07:50 전일 수급·순위·섹터 수집 + 분봉→일봉 집계; 15:40 장후 데이터 수집; 15:45 ohlcv_daily 일봉 수집
- **phase2_data_scheduler.py**, **phase3_data_scheduler.py**, **schedule_runner.py**, **account_sync_scheduler.py**
- **main.py**, **monitoring_router.py**, **health_router.py**, **v4_position_api.py** 등에서 스케줄/주기 참조

### 3.4 KIS OpenAPI 사용 (koreainvestment / openapi.*kis)

- backend/app/services/data_pipeline/kis_api_client.py, collector_minute.py
- backend/app/core/kis_config.py, kis_api_registry.py
- backend/app/services/trading/kis_order_service.py, account_sync_manager.py, position_monitor.py
- backend/app/services/data/sector_price_collector.py, credit_balance_collector.py, broker_trades_collector.py
- backend/app/services/sync/balance_sync_service.py, account_service.py

---

## 4. STEP 3 — 스코어링 필요 데이터 품질 점검

기획서 5대 스코어링에 필요한 테이블 기준.

| tbl | rows | min_dt | max_dt | 비고 |
|-----|------|--------|--------|------|
| v4_investor_daily | 170,760 | 2010-01-28 | 2026-02-23 | 정상 수집 |
| v4_sector_daily | 14,754 | 2018-10-19 | 2026-02-24 | 정상 수집 |
| v4_stock_sector | 4,225 | — | — | 정상 |
| ohlcv_daily | 2,600,387 | 20230102 | 20260223 | 정상 (날짜 형식 varchar) |
| scalping_features_daily | 45 | — | — | 행 적음, 수집 코드 미확인 |
| v4_ohlcv_minute (파티션 합계) | ~43,312,709 | — | — | 파티션별 존재 |

**테마·스코어링 관련 (실제 테이블명 기준)**

| tbl | rows | min_dt | max_dt | 비고 |
|-----|------|--------|--------|------|
| v4_theme_activity_daily | 0 | — | — | **미수집** (기획서 v4_theme_activity에 대응 가능한 테이블) |
| v4_theme_stock | 0 | — | — | **미수집** (기획서 v4_theme_stocks에 대응) |
| v4_theme_master | 0 | — | — | **미수집** (collector_theme_sector는 v4_theme_master INSERT 구현 있으나 현재 0건) |
| v4_theme_daily | 0 | — | — | **미수집** |

- **미수집/공백 요약**: v4_theme_master, v4_theme_stock, v4_theme_daily, v4_theme_activity_daily 전부 0행. 테마 수집이 스케줄에 포함되어 있더라도 실제 적재가 안 되었거나 API/설정 이슈 가능성 있음.
- **scalping_features_daily**: 45행만 존재하며, 코드베이스에서 해당 테이블에 INSERT하는 코드는 발견되지 않음 (레거시 또는 수동/별도 job 가능성).

---

## 5. STEP 4 — 호가/체결/재무/뉴스 테이블 존재 여부

| tablename | 비고 |
|-----------|------|
| financial_ratios | 존재 (약 45,870행). GO100 advanced filter에서 사용. INSERT 경로는 본 감사에서 미확인 |
| orderbook_snapshots | 존재 (약 35,894행). scripts/collection/orderbook_collector.py 로 수집 |
| price_tick_snapshots | 존재 (약 35,865행). 체결/틱 스냅샷 |
| stock_fundamentals | 존재 (약 4,249행). GO100 시총/PER 등에서 사용. backend 재무 수집은 stock_universe 업데이트 위주, 본 테이블 직접 INSERT 코드 미확인 |
| v4_orderbook_realtime | 존재 (est_rows -1, 빈 테이블 가능) |
| v4_tick_data | 존재 (0행) |

- **news / disclosure** 패턴 테이블: **없음**.

---

## 6. 미수집·보완 필요 데이터 정리

| 데이터 | 테이블 | 상태 | 권장 |
|--------|--------|------|------|
| 테마 마스터/종목/일별 | v4_theme_master, v4_theme_stock, v4_theme_daily, v4_theme_activity_daily | 전부 0행 | run_daily_collection --theme 실행 및 KIS 테마 API 응답·에러 로그 확인; 필요 시 백필 |
| 스코어링용 테마 활동 | v4_theme_activity_daily | 0행 | 기획서 “v4_theme_activity”와 매핑 여부 확인 후 수집 설계 |
| 스캘핑 피처 | scalping_features_daily | 45행, 수집 경로 불명 | 수집 스크립트/스케줄 유무 확인 및 필요 시 일일 수집 추가 |
| 재무 비율 | financial_ratios | 데이터 있음, INSERT 경로 미확인 | 레거시/외부 job 문서화 또는 V4.1 파이프라인에 통합 |
| 종목 재무(시총 등) | stock_fundamentals | 데이터 있음, INSERT 경로 미확인 | 동일 |
| 뉴스/공시 | — | 해당 테이블 없음 | 기획 필요 시 별도 설계 |
| index_daily | index_daily | 1,476행, 20240213~20260223 | 레짐/백필용으로 사용 중. 구간 확장 필요 시 historical_backfill 등 활용 |

---

## 7. 참고 — 실행 제한 사항

- 본 작업은 **SELECT만** 수행. 테이블 생성/변경/삭제 없음.
- kis-v41-api / kis-v41-monitor / kis-v41-scheduler **재시작 금지** (자체승인 읽기 전용).

---

## 8. 첨부 — 스코어링 쿼리 (참고용)

```sql
-- v4_investor_daily / v4_sector_daily / ohlcv_daily 등은 trade_date 또는 date 컬럼 사용.
-- v4_theme_activity, v4_theme_stocks 는 실제 스키마에선 v4_theme_activity_daily, v4_theme_stock 이며 현재 0행.
SELECT 'v4_investor_daily' AS tbl, COUNT(*) AS rows, MIN(trade_date)::text AS min_dt, MAX(trade_date)::text AS max_dt FROM v4_investor_daily
UNION ALL SELECT 'v4_sector_daily', COUNT(*), MIN(trade_date)::text, MAX(trade_date)::text FROM v4_sector_daily
UNION ALL SELECT 'v4_stock_sector', COUNT(*), NULL::text, NULL::text FROM v4_stock_sector
UNION ALL SELECT 'ohlcv_daily', COUNT(*), MIN(date)::text, MAX(date)::text FROM ohlcv_daily
UNION ALL SELECT 'scalping_features_daily', COUNT(*), NULL::text, NULL::text FROM scalping_features_daily;
```

---

**보고서 작성:** 2026-02-24  
**다음 단계:** 테마/스캘핑 피처 수집 경로 확정 및 재무 테이블 INSERT 경로 문서화 권장.
