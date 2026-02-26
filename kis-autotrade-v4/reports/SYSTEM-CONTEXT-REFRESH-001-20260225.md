# SYSTEM-CONTEXT-REFRESH-001 시스템 컨텍스트 갱신 보고서
**작성일:** 2026-02-25

## 1. DB 현황 스냅샷

### 1-1. 핵심 테이블 행 수
| tbl | count |
|-----|-------|
| strategy_cards | 60 |
| v4_positions_OPEN | 11 |
| v4_ohlcv_minute_total | 42,351,682 |
| ohlcv_daily | 2,608,066 |
| v4_market_regime_daily | 819 |
| v4_scalping_universe | 708 |
| v4_theme_master | 125 |
| v4_theme_stock | 781 |
| v4_trade_strength_history | 223,814 |
| v4_investor_daily | 171,261 |
| v4_sector_price | 0 |
| v4_tick_data | 0 |
| scalping_features_daily | 45 |

### 1-2. DB 크기
13 GB

### 1-3. 서비스 상태
- kis-v41-api: active
- kis-v41-monitor: active
- kis-v41-scheduler: active

### 1-4. 분봉 파티션별 현황
| relname | n_live_tup | size |
|---------|------------|------|
| v4_ohlcv_minute | 0 | 0 bytes |
| v4_ohlcv_minute_2025_01 ~ 2026_03 | (합계 42,351,682) | 파티션별 253MB~1153MB |

## 2. 레짐 분석 적재

- **post_regime_bt_exec_005.sh 실행:** 미실행 (오늘(2026-02-25) REGIME-BT 세션 없음)
- **v4_backtest_regime_analysis 행 수:** 230행 (기존 적재분 유지)
- **레짐별 통과 현황:**

| regime | cards | passed |
|--------|-------|--------|
| MILD_TREND_DOWN | 56 | 7 |
| MILD_TREND_UP | 57 | 0 |
| SIDEWAYS | 57 | 8 |
| STRONG_TREND_DOWN | 42 | 5 |
| STRONG_TREND_UP | 18 | 0 |

## 3. CONTEXT.md 갱신 항목

- 최종 갱신일: 2026-02-23 → **2026-02-25**
- 사전확인: strategy_cards 62→**60**, v4_positions OPEN 5→**11**
- DB 무결성 기준: strategy_cards 62→**60건**, OPEN 5→**11건**, DB 크기 6,152 MB→**13 GB**, v4_ohlcv_minute 19,468,781→**42,351,682행**
- 신규 반영: v4_theme_master **125건**, v4_theme_stock **781건**, v4_trade_strength_history **223,814건**
- 작업 큐: P0~P5 → **DESK2-BT-RESULT-HARVEST-001, BT-DASHBOARD-DATA-SYNC-001, MINUTE-BAR-VERIFY-AND-CHART-001, DESK2-BT-LIVE-PARITY 잔여, DESK2 모의매매 투입**
- DESK2 상태: "분봉 진입 최적화 필요" → **"7개 발굴 조건 + 7개 전략 재설계 완료, LIVE-PARITY 백테스트 진행 중"**
- 최신 인계서: HANDOVER-KIS-V41-005 유지

## 완료 체크리스트

| # | 항목 | 확인 |
|---|------|------|
| 1 | DB 현황 스냅샷 수집 | ✓ |
| 2 | post_regime_bt_exec_005.sh 안전성 점검 | ✓ (DROP/DELETE/ALTER 없음, 서비스 재시작 없음) |
| 3 | post_regime 실행 완료 | — (오늘 세션 없음, 기존 230행 유지) |
| 4 | v4_backtest_regime_analysis > 0행 | ✓ (230행) |
| 5 | CONTEXT.md 갱신 (날짜, 행수, 작업큐) | ✓ |
| 6 | .bak 파일 삭제 확인 | ✓ |
| 7 | push + URL 200 | (아래 4-2에서 확인) |
| 8 | 실거래 파일 변경 0건 | ✓ (project-docs만 변경) |
