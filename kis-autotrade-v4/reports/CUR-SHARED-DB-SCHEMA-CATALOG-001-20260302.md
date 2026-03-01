# CUR-SHARED-DB-SCHEMA-CATALOG-001 — Session G 전체 조치 + DB 스키마 카탈로그 통합

> 작성: 2026-03-02 | 세션: G-3 | 실행: Claude Code (claude-opus-4-6)
> 레포: project-docs | 커밋: 이 보고서와 함께 push
> HANDOVER 업데이트: V4.1 v6.0 + GO100 v10.4

---

## 1. 완료된 조치 (G-2 잔여)

| # | 항목 | Before | After | 비고 |
|---|------|--------|-------|------|
| 1 | 3중 수집기 정리 | 3개 PID | 1개 (PID 876043) | CEO 직접 조치 완료 |
| 2 | Swap 사용량 | 6.0G/8.0G (75%) | 5.9G/8.0G (74%) | 커널 특성상 점진 감소, 03-03 Virtual 엔진 가동에 문제 없음 |
| 3 | global_market 테이블명 | HANDOVER에 `global_market` 오기 | `go100_global_market`으로 정정 | 접두어 go100_ 누락이었음 |
| 4 | scalping_universe 테이블명 | HANDOVER에 `scalping_universe` 축약 | `v4_scalping_universe`로 정정 | 관련 테이블 3개: v4_scalping_universe, v4_scalping_signals, scalping_features_daily |
| 5 | 테이블 수 | HANDOVER "254 테이블" (모호) | "246 테이블 + 8 뷰 = 254 DB 객체" 명시 | 정확한 구분 추가 |
| 6 | CTE BT 스크립트 3개 | HANDOVER에 "신규" 기재 | 서버 미존재 주석 추가 | Session D replay 엔진으로 대체 |
| 7 | 22개 test collection error | 미기록 | HANDOVER에 기록 | 시스템 Python pip 미설치, 서비스 무관 |

---

## 2. DB 스키마 카탈로그

### 총괄

| 항목 | 값 |
|------|-----|
| 총 테이블 | 246 |
| 총 뷰 | 8 |
| 총 DB 객체 | 254 |
| 카탈로그 크기 | 7,646줄 |
| 생성 시각 | 2026-03-02 08:20 KST |

### 프로젝트별 분포

| 프로젝트 | 테이블 수 | 비율 |
|---------|----------|------|
| V4.1 (v4_*) | 124 | 50.4% |
| GO100 (go100_*) | 65 | 26.4% |
| 공통 | 57 | 23.2% |

### 카테고리별 분포

| 카테고리 | 테이블 수 | 주요 테이블 |
|---------|----------|-----------|
| MARKET | 28 | ohlcv_daily(2.6M), v4_ohlcv_minute(84M+), index_daily |
| INVESTOR | 4 | v4_investor_daily(261K), v4_market_investor_daily |
| STRATEGY | 19 | strategy_cards, v4_strategies, go100_strategy_cards |
| POSITION | 47 | v4_positions, v4_paper_trades, go100_live_orders |
| RISK | 6 | v4_market_regime_daily, go100_risk_rules/events |
| NEWS | 1 | go100_news_items(2.1M) |
| AI | 24 | v4_bt_discovery_log(776K), go100_gap_calibrator(108K) |
| INFRA | 49 | accounts, users, v4_notifications, go100_user_preferences |
| GLOBAL | 1 | go100_global_market |
| UNIVERSE | 25 | stock_universe, v4_scalping_universe, v4_theme_master |
| ETC | 42 | go100_episodic_memory, v4_daily_portfolio, go100_goals |

### 뷰 (8개)

| 뷰 | 소유 |
|-----|------|
| go100_investor_flow | GO100 |
| go100_minute_bars | GO100 |
| go100_orderbook_snapshot | GO100 |
| go100_strategy_store | GO100 |
| go100_tick_data | GO100 |
| vw_fund_ledger | 공통 |
| vw_llm_daily_total | 공통 |
| vw_llm_user_monthly | 공통 |

### 대형 테이블 Top 5

| 테이블 | 행 수 | 크기 |
|--------|------|------|
| v4_ohlcv_minute | 84M+ (파티션 15개) | 수 GB |
| ohlcv_daily | 2,615,744 | ~600 MB |
| go100_news_items | 2,140,000+ | ~1 GB |
| v4_bt_discovery_log | 776,636 | 518 MB |
| v4_investor_daily | 261,000+ | ~100 MB |

---

## 3. 자동 최신화 체계

| 항목 | 내용 |
|------|------|
| 생성 스크립트 | `/root/kis-autotrade-v4/scripts/generate_db_catalog.py` |
| 쉘 래퍼 | `/root/kis-autotrade-v4/scripts/update_db_catalog.sh` |
| 출력 파일 | `/root/project-docs/shared/DB-SCHEMA-CATALOG.md` |
| 변경 이력 | `/root/project-docs/shared/DB-SCHEMA-CHANGELOG.md` |
| cron | `0 6 * * *` (매일 06:00) |
| 동작 방식 | asyncpg로 DB 조회 -> MD 생성 -> MD5 비교 -> 변경 시 git push |
| DB 접속 | kis_admin@localhost:5432/kisautotrade |

---

## 4. HANDOVER 정정 내역

### V4.1 HANDOVER (v5.11 -> v6.0)

| # | 위치 | Before | After |
|---|------|--------|-------|
| 1 | 버전 헤더 | v5.11 | v6.0 — Session G 전체 조치 + DB 스키마 카탈로그 통합 |
| 2 | 프로젝트 개요 | "254 테이블" | "246 테이블 + 8 뷰 = 254 DB 객체" |
| 3 | CUR-V41-HISTORICAL-DATA-COMPLETE-001 | global_market/scalping_universe | go100_global_market/v4_scalping_universe |
| 4 | CUR-V41-DATA-COLLECTION-STATUS-001 | global_market/scalping_universe | go100_global_market/v4_scalping_universe |
| 5 | CUR-V41-CTE-FULL-BACKTEST-001 | 스크립트 3개 "신규" | 서버 미존재 주석 추가 |
| 6 | 완료된 작업 테이블 | - | CUR-SHARED-DB-SCHEMA-CATALOG-001 행 신규 추가 |
| 7 | 버전 이력 | v5.8 마지막 | v6.0 추가 |

### GO100 HANDOVER (v10.3 -> v10.4)

| # | 위치 | 변경 |
|---|------|------|
| 1 | 완료 작업 테이블 | CUR-SHARED-DB-SCHEMA-CATALOG-001 행 신규 추가 |
| 2 | 버전 이력 | v10.4 추가 |

---

## 5. 검증

| 항목 | 결과 |
|------|------|
| generate_db_catalog.py 실행 | OK (246 테이블 + 8 뷰 = 254) |
| DB-SCHEMA-CATALOG.md 생성 | OK (7,646줄) |
| cron 등록 | OK (0 6 * * *) |
| V4.1 HANDOVER 정정 | OK (7개 항목) |
| GO100 HANDOVER 정정 | OK (2개 항목) |
| 서비스 영향 | 없음 (SELECT 조회 + 문서 작업만) |

---

## 6. 참조 경로

| 산출물 | 경로 |
|--------|------|
| DB 스키마 카탈로그 | shared/DB-SCHEMA-CATALOG.md |
| DB 스키마 변경 이력 | shared/DB-SCHEMA-CHANGELOG.md |
| 카탈로그 생성기 | kis-autotrade-v4/scripts/generate_db_catalog.py |
| 자동 갱신 래퍼 | kis-autotrade-v4/scripts/update_db_catalog.sh |
| 이 보고서 | kis-autotrade-v4/reports/CUR-SHARED-DB-SCHEMA-CATALOG-001-20260302.md |
| V4.1 HANDOVER | kis-autotrade-v4/HANDOVER.md (v6.0) |
| GO100 HANDOVER | go100/HANDOVER.md (v10.4) |

---

HANDOVER 업데이트: V4.1 v6.0, GO100 v10.4 (이 커밋에 포함)
