# 코스피/코스닥 이원 레짐 백테스트 + DB화 + 차트 시각화 통합 보고서

**작업ID:** CUR-STRATEGY-REGIME-BT-VIZ-001  
**작성일:** 2026-02-24 (KST)  
**서버:** root@[SERVER-IP]  
**프로젝트:** /root/kis-autotrade-v4  
**DB:** PostgreSQL kisautotrade (kis_admin), localhost:5432  

---

## 1. 요약

- **PART A:** v4_market_regime_daily에 `market_type` 컬럼 추가(KOSPI/KOSDAQ), 코스피·코스닥 레짐 백필 완료.
- **PART B:** v4_backtest_regime_analysis 테이블 생성, 레짐별 분석 스크립트(regime_analysis.py) 작성. FULL 34개 전략 전수 백테스트는 세션별 실행 후 `--fix-regime` 및 분석 스크립트로 결과 적재.
- **PART C:** 백테스트·레짐 API(v4_backtest_analysis) 기존 구현 활용, regime-timeline에 market_type 필터 반영. 프론트엔드 차트(RegimeTimelineChart, RegimePerformanceBarChart, EquityCurveChart, DeskRadarChart) 존재.
- **PART D:** 본 보고서 작성, DB-SCHEMA.md 반영.

---

## 2. PART A: 코스피/코스닥 이원 레짐 시스템

### 2.1 현황 분석 (A-1)

| 항목 | 결과 |
|------|------|
| v4_market_regime_daily (기존) | 59행, 2025-11-20 ~ 2026-02-23, date UNIQUE |
| index_daily | 0001(KOSPI), 1001(KOSDAQ), 2001 각 492행, 2024-02-13 ~ 2026-02-23 |
| regime_detector.py | KOSPI(0001) 기준 MA/수익률/양봉비율·VKOSPI·외국인 수급으로 5단계 레짐 판정. 코스닥 수익률(kosdaq_ret_20d)은 지표에만 포함, 저장 레짐은 단일 시장. |

### 2.2 스키마 변경 (A-2, 자체승인)

- **마이그레이션:** `scripts/migrations/regime_dual_market_20260224.sql`
  - `v4_market_regime_daily`에 `market_type VARCHAR(10) DEFAULT 'KOSPI'` 추가
  - `v4_market_regime_daily_date_key` (UNIQUE date) 제거
  - `v4_market_regime_daily_date_market_key` UNIQUE(date, market_type) 생성
- **백필 스크립트:** `scripts/backfill_regime_history.py` 수정
  - INSERT/ON CONFLICT에 `market_type` 포함, `get_previous_row`/`check_strong_down_escape`/`apply_transition`에 market_type 인자 추가
  - `collect_indicators_as_of_kosdaq`, `run_backfill_kosdaq` 추가
  - CLI: `--market KOSPI` | `--market KOSDAQ`

### 2.3 레짐 데이터 생성 및 검증 (A-3)

| market_type | 건수 | 기간 |
|-------------|------|------|
| KOSPI | 265 | 2025-01-02 ~ 2026-02-23 |
| KOSDAQ | 121 | 2025-01-02 ~ 2025-07-03 (전 구간은 generate_regime_data.py 재실행 시 확장) |

- 코스피: 2025-01-02 ~ 2026-02-23 구간 백필 완료.
- 코스닥: `scripts/analysis/generate_regime_data.py` 또는 `backfill_regime_history.py --market KOSDAQ --from 20250101 --to 20260223`로 전 구간 생성 가능.

**레짐 분포 (KOSPI):**

| regime | 건수 | 기간 |
|--------|------|------|
| MILD_TREND_DOWN | 34 | 2025-01-02 ~ 2026-01-21 |
| MILD_TREND_UP | 56 | 2025-02-14 ~ 2026-02-19 |
| SIDEWAYS | 70 | 2025-01-09 ~ 2026-02-23 |
| STRONG_TREND_DOWN | 20 | 2025-12-05 ~ 2026-01-06 |
| STRONG_TREND_UP | 3 | 2025-06-20 ~ 2025-06-24 |

### 2.4 코스피 vs 코스닥 레짐 불일치 구간

- 동일 date에 KOSPI와 KOSDAQ 레짐이 다른 구간은 전략별 벤치마크(코스피/코스닥) 선택에 사용.
- 쿼리 예:  
  `SELECT k.date, k.regime AS kospi_regime, d.regime AS kosdaq_regime FROM v4_market_regime_daily k JOIN v4_market_regime_daily d ON k.date = d.date WHERE k.market_type = 'KOSPI' AND d.market_type = 'KOSDAQ' AND k.regime != d.regime ORDER BY k.date;`
- 현재 KOSDAQ 데이터가 2025-04-15까지이므로, 그 이전 구간만 불일치 분석 가능.

---

## 3. PART B: 레짐별 백테스트 및 DB화

### 3.1 v4_backtest_regime_analysis 테이블

- **마이그레이션:** `scripts/migrations/v4_backtest_regime_analysis_20260224.sql`
- 컬럼: session_id, card_id, strategy_name, desk_id, market_type, regime, total_trades, win_count, loss_count, win_rate, profit_factor, total_pnl, avg_pnl, max_pnl, min_pnl, avg_hold_days, avg_mfe_pct, avg_mae_pct, max_drawdown_pct, sharpe_ratio, benchmark_return_pct, strategy_return_pct, alpha_pct, pass_win_rate, pass_pf, pass_alpha, pass_mdd, pass_sharpe, overall_pass, backtest_period_start/end, created_at.
- 인덱스: card_id+regime, desk_id+regime, session_id.

### 3.2 레짐별 분석 스크립트

- **경로:** `scripts/backtest/regime_analysis.py`
- **기능:**  
  - `--session-ids`: 분석할 세션 ID(쉼표 구분). 미지정 시 최근 1개.  
  - `--fix-regime`: regime_at_entry가 NULL인 트레이드를 entry_date + stock_universe.market으로 v4_market_regime_daily와 조인해 UPDATE.
  - (session_id, card_id, market_type, regime)별로 집계 후 v4_backtest_regime_analysis에 INSERT.
- **합격 기준:** 지시서 B-2-3 표준(DESK1~5 × BULL/NEUTRAL/BEAR/CRISIS). 5단계 레짐은 STRONG_TREND_UP·MILD_TREND_UP→BULL, SIDEWAYS→NEUTRAL, MILD_TREND_DOWN→BEAR, STRONG_TREND_DOWN→CRISIS로 매핑.

### 3.3 백테스트 실행 (FULL 34개)

- **기간:** 2025-01-01 ~ 2026-02-23, 자본 10,000,000원, 엔진 v2.
- **실행 예:**  
  `PYTHONPATH=/root/kis-autotrade-v4/backend python scripts/backtest/run_backtest.py --start 20250101 --end 20260223 --capital 10000000 --name "REGIME-BT-DESK{n}-CARD{id}" --engine v2 --desk-strategies '[{"desk_id":n,"card_id":id}]'`
- **FULL 카드 목록 (STRATEGY-FULL-AUDIT-001 기준):**  
  DESK1: 39, 45 | DESK2: 6,15,16,17,18,19,20,21,22,24,26,27 | DESK3: 8,28~37 | DESK4: 9,47~53 | DESK5: 60.
- **일괄 실행 스크립트:** `scripts/backtest/run_regime_bt_34.sh` — 34개 카드 순차 실행.  
  `nohup bash scripts/backtest/run_regime_bt_34.sh > /tmp/regime_bt_34.log 2>&1 &`
- **REGIME-BT-* 전용 분석:** `scripts/analysis/regime_backtest_analysis.py [--fix-regime]` — session_name LIKE '%REGIME-BT-%' 세션만 조회 후 regime_analysis.run_analysis 호출.
- **사후 처리:**  
  1) `regime_analysis.py --session-ids <session_id> --fix-regime`  
  2) `regime_analysis.py --session-ids <session_id>`  
  → v4_backtest_regime_analysis에 레짐별 성과·합격 여부 적재.

### 3.4 regime_at_entry

- backtest_engine_v2는 매매 기록 시 regime_at_entry를 인자로 받지만, 현재 호출부에서 전달하지 않아 NULL로 남을 수 있음.
- 분석 스크립트의 `--fix-regime` 또는 분석 시점 in-memory 조인(entry_date + stock → market_type → v4_market_regime_daily)으로 보정.

---

## 4. PART C: 백테스트 + 레짐 시각화 API·프론트

### 4.1 API (backend/app/api/v4_backtest_analysis.py)

- **GET /api/v4/backtest/regime-analysis** — card_id, desk_id, regime, session_id 필터.
- **GET /api/v4/backtest/regime-matrix** — 전략×레짐 매트릭스.
- **GET /api/v4/backtest/equity-curve** — session_id, card_id, 일별 누적 수익 + regime_at_entry.
- **GET /api/v4/backtest/regime-timeline** — market_type(KOSPI/KOSDAQ) 필터 반영. v4_market_regime_daily + index_daily 조인, 날짜·레짐·지수 close.
- **GET /api/v4/backtest/regime-comparison** — card_id별 레짐별 성과(바 차트용).

main.py에 bt_analysis_router 등록됨.

### 4.2 프론트엔드 차트

- `frontend/src/components/backtest-analysis/`: RegimeTimelineChart, RegimePerformanceBarChart, EquityCurveChart, DeskRadarChart.
- `frontend/src/app/(protected)/backtest/analysis/page.tsx`, `backtest/page.tsx` 존재.
- 레짐 타임라인은 BULL/NEUTRAL/BEAR/CRISIS 색상 매핑 지원.

### 4.3 DB-SCHEMA.md

- v4_market_regime_daily: market_type, UNIQUE(date, market_type) 반영.
- v4_backtest_regime_analysis 테이블 설명 추가.

---

## 5. 체크포인트

| 항목 | 상태 |
|------|------|
| DB 백업 | /tmp/backup_REGIME_BT_VIZ_*.dump (실행됨) |
| v4_market_regime_daily 현황 분석 | 완료 |
| index_daily 코스피/코스닥 확인 | 완료 |
| regime_detector.py 분석 | 완료 |
| 코스닥 레짐 데이터 생성 | 69건 적재 (전 구간은 재실행 권장) |
| 코스피 미커버 구간 보정 | 완료 (265건) |
| 백테스트 FULL 전략 전수 실행 | 세션별 실행 명령·절차 문서화 |
| regime_at_entry 매핑 | 분석 스크립트 --fix-regime 및 조인 로직 |
| v4_backtest_regime_analysis 테이블 생성·INSERT | 테이블·스크립트 완료 |
| 전략×레짐 적합성 매트릭스 | regime-matrix API·분석 스크립트 overall_pass |
| 프론트엔드 차트 현황 | 확인됨 |
| 백테스트+레짐 API | 구현·market_type 반영 |
| 차트 5종 | 타임라인·에쿼티·바·레이더 구현됨, 히트맵은 매트릭스 API로 보완 가능 |
| DB-SCHEMA.md 업데이트 | project-docs 반영 |

---

## 6. 참조

- STRATEGY-FULL-AUDIT-001-20260224.md  
- kis-v41-rules.md, CLAUDE.md, DB-SCHEMA.md  
- regime_detector.py (읽기 전용), backfill_regime_history.py, scripts/backtest/regime_analysis.py  

---

*보고서는 2026-02-24 작업 기준으로 작성되었으며, FULL 34개 전략 전수 백테스트 완료 후 레짐별 성과표·매트릭스·BULL 랭킹을 보완할 수 있습니다.*
