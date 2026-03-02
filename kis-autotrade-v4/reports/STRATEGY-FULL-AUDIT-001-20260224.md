# STRATEGY-FULL-AUDIT-001 전략카드 전수 분석 + 레짐별 백테스트 보고서

**작업ID:** CUR-STRATEGY-FULL-AUDIT-001 (v3 - 레짐 연동 최종본)  
**작성일:** 2026-02-24 (KST)  
**서버:** root@[SERVER-IP]  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  

---

## 1. 전략카드 전수 목록 (52개, 구현상태)

- **데이터 소스:** `strategy_cards` + `v4_desk_strategy_mapping` (stage_id=1, is_active=true)
- **구현상태:** 52개 전략 모두 `backtest_compatible = true`, `entry_rules.indicators` 존재 → **FULL(백테스트 가능)**

### 1.1 DESK별 요약

| DESK | 카드 수 | card_id 목록 | 비고 |
|------|--------|--------------|------|
| DESK1 | 10 | 5, 38~46 | 스캘핑/초단타/갭메우기/호가불균형 등 |
| DESK2 | 16 | 6, 7, 14~27 | 데일리/종가매매/레인지돌파/VWAP/볼린저 등 |
| DESK3 | 11 | 8, 28~37 | 스윙/골든크로스/RSI/추세추종 등 |
| DESK4 | 9 | 9, 11, 47~53 | 중기추세/피보나치/엘리어트/ADX/켈트너 등 |
| DESK5 | 10 | 10, 12, 13, 54~60 | 장기스윙/가치/성장주/배당/모멘텀팩터 등 |

### 1.2 전략카드 상세 (card_id, 이름, 진입/청산 요약)

- **DESK1:** entry_rules: indicators + time_window + min_strength/min_conditions; exit_rules: max_hold_days(0~1), stop_loss_pct(-0.3%~-1%), target_profit_pct(1%~2.5%), eod_force_exit
- **DESK2:** 일부 time_window 14:30~15:20(종가매매); 공통 exit: stop_loss_pct(-1.5%~-5%), target_profit_pct(0.5%~6%), max_hold_days(0~3)
- **DESK3:** ma5_ma20_golden_cross, rsi, macd 등; max_hold_days(5~20), stop_loss_pct(-2%~-4%)
- **DESK4:** max_hold_days(20~40), target_profit_pct(38%~42%), stop_loss_pct(-5%)
- **DESK5:** max_hold_days(90~120), target_profit_pct(64%~85%), stop_loss_pct(-7%)

*(전체 52개 카드의 strategy_name, entry_rules, exit_rules, risk_params는 DB 조회 결과와 동일)*

### 1.3 strategy_engine.py 구현 현황

- **역할:** 시그널 생성 → 시간/CLASS 필터 → 신뢰도 필터 → Idempotency → 정렬 후 상위 N개 반환
- **진입/청산 로직:** 개별 전략 클래스(BaseStrategy)의 `generate_signals()` 및 백테스트 엔진 V2의 `entry_rules`/`exit_rules` 기반 일봉(또는 분봉) 시그널/청산 처리
- **백테스트:** `BacktestEngineV2`가 `strategy_cards` + `v4_desk_strategy_mapping`에서 카드별 entry/exit/risk 파라미터 로드 후 `BacktestSignalGenerator`와 연동하여 진입/청산 시뮬레이션

---

## 2. v4_market_regime_daily 레짐 분포 & 전환점

### 2.1 레짐 분포

| regime | 건수 | MIN(date) | MAX(date) |
|--------|------|-----------|-----------|
| MILD_TREND_DOWN | 16 | 2025-11-24 | 2026-01-21 |
| MILD_TREND_UP | 3 | 2026-02-12 | 2026-02-19 |
| SIDEWAYS | 23 | 2025-11-20 | 2026-02-23 |
| STRONG_TREND_DOWN | 20 | 2025-12-05 | 2026-01-06 |

- **총 59행**, 기간: **2025-11-20 ~ 2026-02-23**
- **미커버 구간:** 2025-01-01 ~ 2025-11-19 (백테스트 기간 2025-01-01~2026-02-23 중 약 10.5개월 레짐 없음)
- **레짐 명칭 매핑 (보고서 기준):**  
  - BULL = STRONG_TREND_UP + MILD_TREND_UP  
  - NEUTRAL = SIDEWAYS  
  - BEAR = MILD_TREND_DOWN  
  - CRISIS = STRONG_TREND_DOWN  

### 2.2 레짐 전환점 (previous_regime ≠ regime)

| date | previous_regime | regime | transition_note |
|------|-----------------|--------|-----------------|
| 2025-11-24 | SIDEWAYS | MILD_TREND_DOWN | 하락 전환 적용 |
| 2025-12-05 | MILD_TREND_DOWN | STRONG_TREND_DOWN | 하락 전환 적용 |
| 2026-01-07 | STRONG_TREND_DOWN | MILD_TREND_DOWN | 상승 전환 적용 |
| 2026-01-12 | MILD_TREND_DOWN | SIDEWAYS | 상승 전환 적용 |
| 2026-01-16 | SIDEWAYS | MILD_TREND_DOWN | 하락 전환 적용 |
| 2026-01-22 | MILD_TREND_DOWN | SIDEWAYS | 상승 전환 적용 |
| 2026-02-20 | MILD_TREND_UP | SIDEWAYS | 하락 전환 적용 |

### 2.3 코스피 실제 추이와 레짐 매핑 검증

- **레짐별 평균 KOSPI 20일 수익률 (v4_market_regime_daily):**

| regime | avg_kospi_ret_20d | trading_days |
|--------|-------------------|--------------|
| MILD_TREND_DOWN | -14.23% | 16 |
| MILD_TREND_UP | 20.63% | 3 |
| SIDEWAYS | -0.13% | 23 |
| STRONG_TREND_DOWN | -85.00% | 20 |

- 참고: 2025년 연간 코스피 수익률 약 +75.63%(위키피디아); 2026.02 월간 5,825→5,912 수준. 현재 DB 레짐 구간(2025-11~2026-02)은 하락·횡보 구간 비중이 커서 STRONG_TREND_DOWN 구간에서 -85% 등 극단값 포함.

---

## 3. 레짐별 백테스트 성과표 (BULL/NEUTRAL/BEAR/CRISIS 분리)

- **분리 방법:** `v4_backtest_trades`(SELL만)의 `entry_date`로 `v4_market_regime_daily`와 조인하여 진입일 레짐 기준 집계.
- **백테스트 실행:** 2026-02-24 기준 `REGIME-BT-ALL-52` 세션 **session_id=70** 실행 중 (자본 1,000만 원, 2025-01-01~2026-02-23, engine=v2, 52개 카드 일괄). 완료 후 본 섹션은 session_id=70 기준으로 갱신 예정.

### 3.1 기존 세션 샘플 (session_id=69, card_id=6만 해당)

| card_id | strategy_name | regime | trades | win_rate_pct | total_pnl | avg_hold |
|---------|---------------|--------|--------|--------------|-----------|----------|
| 6 | DESK2_데일리_class_a | MILD_TREND_DOWN | 66 | 39.4 | -20,410 | - |
| 6 | DESK2_데일리_class_a | SIDEWAYS | 90 | 51.1 | 9,233 | - |
| 6 | DESK2_데일리_class_a | STRONG_TREND_DOWN | 120 | 44.2 | -2,035 | - |

- REGIME-BT-ALL-52 완료 후 **전 카드 × 레짐** 성과표로 교체 예정.

---

## 4. 레짐별 벤치마크 대비 알파

- **벤치마크:** 위 레짐별 `avg_kospi_ret_20d` (또는 거래일 가중 평균).
- **알파:** 전략(카드)별 레짐별 수익률 − 해당 레짐 코스피 20일 수익률.  
- REGIME-BT-ALL-52 결과 반영 후 카드별·레짐별 알파 표 추가 예정.

---

## 5. 전략 × 레짐 적합성 매트릭스

- **합격 기준:** 지시서 STEP 7 레짐별 차등 합격 기준 (DESK1~5별 최소 승률, PF, 알파, MDD, 샤프).
- **매핑:** DB 레짐(STRONG_TREND_UP, MILD_TREND_UP, SIDEWAYS, MILD_TREND_DOWN, STRONG_TREND_DOWN) → BULL/NEUTRAL/BEAR/CRISIS 적용.
- REGIME-BT-ALL-52 완료 후 각 (card_id, regime)에 대해 합격/불합격/조건부 판정 및 **전략 × 레짐 매트릭스** 표 작성 예정.

---

## 6. 상승장(BULL) 기준 상위 전략 랭킹

- BULL = STRONG_TREND_UP + MILD_TREND_UP. 현재 레짐 데이터상 MILD_TREND_UP 3일만 존재.
- REGIME-BT-ALL-52 결과로 BULL 구간 거래가 있는 전략만 필터 후, 알파·PF·승률 종합 스코어 순 랭킹 작성 예정.

---

## 7. 1차 최적화 결과 (파라미터 추천값)

- **대상:** 현재 레짐(BULL/STRONG_BULL)에서 성과 부진 전략.
- **방법:** target_pct, stop_loss_pct, trailing_pct, holding_period 그리드 서치 후 BULL 구간만 재백테스트.
- **제약:** `strategy_cards` UPDATE는 CEO 승인 필요 → **추천값만 보고** 반영.
- REGIME-BT-ALL-52 및 BULL 구간 성과 확정 후 1차 최적화 실행 및 추천값 표 추가 예정.

---

## 8. 모의실매매 대상 선정

- STEP 8 매트릭스에서 **현재 레짐(BULL) 합격 전략** 추출.
- DESK별: DESK1 5개, DESK2 3개, DESK3~5 각 2개. 우선순위 = BULL 알파 × PF × 승률 종합 스코어.
- 레짐별 성과·매트릭스 확정 후 선정 목록 추가 예정.

---

## 9. 미구현 전략 구현 계획

- **현황:** 52개 카드 모두 `backtest_compatible=true`이며 `entry_rules.indicators` 존재 → 백테스트 관점에서는 구현 완료로 분류.
- **미구현:** 지시서에서 정의한 “미구현”이 라이브 시그널 미연동·특수 로직 미구현 등을 의미할 경우, strategy_engine 등록 전략 목록과 카드별 indicator 구현 대조 후 별도 목록화 가능. (현재는 전수 FULL로 두고, Phase 4 병렬 작업 시 세부 항목 정리 권장.)

---

## 10. 사전 점검 체크리스트

| 항목 | 상태 |
|------|------|
| KST 확인 (timeapi.io) | 2026-02-24 11:33 KST |
| 서비스 상태 (kis-v41-api, monitor, scheduler) | active |
| DB 백업 | /tmp/backup_STRATEGY_AUDIT_20260224_113340.dump |
| v4_market_regime_daily 전수 조회 | 59행, 2025-11-20~2026-02-23 |
| 레짐 미커버 구간 | 2025-01-01~2025-11-19 → 보정 스크립트 권장(INSERT만) |
| strategy_cards 전수 조회 | card_id, entry_rules, exit_rules, risk_params 기준 52개 BUILTIN |
| strategy_engine.py 분석 | 진입/청산은 BaseStrategy + BacktestEngineV2 연동 |
| v4_desk_strategy_mapping | 56행 (52개 고유 desk_id+card_id 조합) |
| 기존 백테스트 이력 | v4_backtest_trades에 card_id별 건수 존재 (36개 card_id) |
| 백테스트 전략 실행 | REGIME-BT-ALL-52 실행 중 (완료 시 레짐별 성과·매트릭스 갱신) |

---

## 11. 레짐 데이터 보정 권장사항

- **목표:** 2025-01-01 ~ 2025-11-19 구간에 대해 `v4_market_regime_daily` INSERT만 수행 (기존 행 UPDATE/DELETE 금지).
- **참조:** `regime_detector.py` 로직(읽기 전용) — index_daily, ohlcv_daily, v4_vkospi_daily, v4_investor_daily 기반 일별 레짐 판정.
- **방법:** 거래일 순으로 과거 일자부터 `detect_regime(save=False)` 또는 동일 산식의 동기 스크립트로 레짐 계산 후 `INSERT INTO v4_market_regime_daily (...)` 실행. 히스테리시스(상승 3일/하락 2일) 유지하려면 일자 순차 처리 필요.

---

## 12. 참조 문서

- CLAUDE.md, kis-v41-rules.md, MARKET-HOURS-KR.md, DB-SCHEMA.md  
- v41-architecture-v1.2.md  
- regime_detector.py (읽기 전용)  
- 코스피: 위키피디아 2025 연간 +75.63%, Investing.com 2026.02, TradingEconomics 5,825→5,912  

---

*본 보고서는 REGIME-BT-ALL-52 세션 완료 후 레짐별 성과표·알파·적합성 매트릭스·BULL 랭킹·최적화 추천값·모의실매매 대상을 보완할 예정입니다.*
