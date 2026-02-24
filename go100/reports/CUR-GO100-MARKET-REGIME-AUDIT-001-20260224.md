# CUR-GO100-MARKET-REGIME-AUDIT-001 — 시장 레짐 시스템 현황 조사 보고서

**발행:** 2026-02-24  
**우선순위:** P1  
**목적:** MARKET-REGIME-001 작업 상태 파악 및 미완료 항목 식별  
**작업 유형:** 조사 및 보고서 작성만 (코드 수정 없음)

---

## 1. DB 테이블

### 1.1 레짐 관련 테이블 및 행 수

| table_name                  | row_count |
|-----------------------------|-----------|
| v4_backtest_regime_analysis | 0         |
| v4_market_regime_daily      | 552       |

- **market_regime_history**, **go100_market_regimes** 테이블은 **없음** (지시서 예시 쿼리 대비).
- **v4_regime_strategy_weights** 테이블/뷰 **없음**. 코드(v4_trading.py, v4_ai_trading.py)에서 참조하나 DB에 없어 **DEFAULT_REGIME_MATRIX** 폴백 사용 중.

### 1.2 스키마 요약

**v4_market_regime_daily**  
- id, date, regime, regime_score, kospi_ret_20d, ma5, ma20, ma60, ma_alignment, bull_ratio_20d, vkospi, foreign_flow_20d, previous_regime, transition_note, created_at, updated_at, hysteresis_up_count, hysteresis_down_count, pending_regime, market_type (default 'KOSPI').

**v4_backtest_regime_analysis**  
- id, session_id, card_id, strategy_name, desk_id, market_type (default 'KOSPI'), regime, total_trades, win_count, loss_count, win_rate, profit_factor, total_pnl, avg_pnl, max_pnl, min_pnl, avg_hold_days, avg_mfe_pct, avg_mae_pct, max_drawdown_pct, sharpe_ratio, benchmark_return_pct, strategy_return_pct, alpha_pct, pass_win_rate, pass_pf, pass_alpha, pass_mdd, pass_sharpe, overall_pass, backtest_period_start, backtest_period_end, created_at, regime_mapped.

### 1.3 최근 데이터 샘플 (v4_market_regime_daily)

| date     | regime          | regime_score | market_type |
|----------|-----------------|--------------|-------------|
| 2026-02-23 | SIDEWAYS        | 51.00        | KOSPI       |
| 2026-02-23 | MILD_TREND_DOWN | 49.00        | KOSDAQ      |
| 2026-02-20 | SIDEWAYS        | 41.00        | KOSPI       |
| 2026-02-20 | MILD_TREND_DOWN | 39.00        | KOSDAQ      |
| 2026-02-19 | MILD_TREND_UP   | 41.00        | KOSPI       |

---

## 2. 코드 파일

### 2.1 백엔드 (regime/Regime 포함 파일)

| 구분 | 경로 |
|------|------|
| 라우터 | backend/app/routers/regime.py, v4_dashboard.py, v4_system.py, v4_data_pipeline.py, v4_ai_trading.py, v4_trading.py, brain.py, fund.py |
| 서비스 | backend/app/services/market/regime_detector.py, adaptive/regime_weight.py, adaptive/weekly_scoring.py, strategy/strategy_engine.py, strategy/base_strategy.py, strategy/momentum_breakout.py, mean_reversion.py, box_breakout.py, volatility_breakout.py, dummy_momentum.py, brain/fund_commander.py, execution/fund_pool.py, orchestrator/orchestrator.py, backtest/engine.py, backtest/backtest_engine_v2.py, risk/risk_manager.py, position/signal_processor.py, trading/v4_pipeline_orchestrator.py, v4_risk_manager.py, scheduler/daily_scheduler.py, system/adaptive_bridge.py, system/orchestrator.py, notification/notification_service.py, factory.py, desk1_commander.py, pick_reason_service.py |
| 스키마/모델 | backend/app/schemas/regime.py, schemas/market.py, schemas/adaptive.py, schemas/adaptive_engine.py, models/market.py, models/backtest_analysis.py, models/fund.py, models/position.py, models/trade_analysis.py, core/enums.py (MarketRegime), core/desk_config.py |
| API | backend/app/api/v4_backtest_analysis.py |
| 기타 | backend/app/main.py (regime 라우터 등록) |

### 2.2 GO100 전용 regime 코드

- **backend/app/services/go100/universe/advanced_filters.py**  
  - `get_market_regime(self, db, ref_date=None)`: v4_market_regime_daily 대신 **자체 계산**으로 레짐 산출 (STRONG_BULL/MILD_TREND_UP/SIDEWAYS/MILD_TREND_DOWN/STRONG_BEAR). V4.1 명칭(STRONG_TREND_UP/DOWN)과 불일치.
- **backend/app/services/go100/ai/prompts.py**  
  - 툴 설명 1곳: `get_market_regime | ... | 시장 레짐 판정`.

### 2.3 프론트엔드 (regime 관련)

- frontend/src/app/(protected)/backtest/analysis/page.tsx  
- frontend/src/lib/api/backtest-analysis.ts  
- frontend/src/components/backtest-analysis/RegimeTimelineChart.tsx  
- frontend/src/components/backtest-analysis/RegimePerformanceBarChart.tsx  
- frontend/src/components/backtest-analysis/EquityCurveChart.tsx  
- frontend/src/components/backtest-analysis/DeskRadarChart.tsx  
- frontend/src/components/backtest-analysis/StrategyRegimeHeatmap.tsx  

(백테스트 분석 UI에서 레짐 타임라인·성과·히트맵 등 사용.)

### 2.4 regime 관련 함수/클래스 (일부)

- **regime.py (라우터)**: get_regime_current, get_regime_history, get_regime_indicators, post_regime_detect  
- **regime_detector.py**: MarketRegimeDetector, RegimeResult, RegimeIndicators  
- **schemas/regime.py**: RegimeCurrentResponse, RegimeHistoryItem, RegimeHistoryResponse, RegimeIndicatorsResponse, RegimeDetectRequest, RegimeDetectResponse  
- **adaptive/regime_weight.py**: RegimeWeightManager, get_current_regime, get_base_weights, get_regime_transition_adjustment  
- **v4_backtest_analysis.py**: get_regime_analysis, get_regime_matrix, get_regime_timeline, get_regime_comparison  
- **core/enums.py**: MarketRegime (STRONG_TREND_UP, MILD_TREND_UP, SIDEWAYS, MILD_TREND_DOWN, STRONG_TREND_DOWN)  
- **desk_config.py**: get_effective_allocation(regime, total_capital)

---

## 3. API

### 3.1 regime 전용 라우터 (prefix `/api/v4/regime`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET  | /api/v4/regime/current   | 현재 레짐 (Orchestrator 판정값) |
| GET  | /api/v4/regime/history   | 레짐 이력 (limit 1~365) |
| GET  | /api/v4/regime/indicators| 최근 판정 지표 상세 |
| POST | /api/v4/regime/detect    | 수동 레짐 판정 (save=true/false) |

### 3.2 기타 regime 노출 엔드포인트

- **GET /api/v4/system/market/regime** (v4_system.py): v4_market_regime_daily 최신 1건, regime/confidence 반환.  
- **v4_dashboard.py**: 대시보드 응답 내 `regime` (date, regime, score), 브리핑 내 `market_regime`.  
- **v4_data_pipeline.py**: 파이프라인 상태 응답 내 `market_regime` (latest_date, regime, score).  
- **v4_ai_trading.py**: 레짐별 가중치 조회 시 v4_market_regime_daily 사용 (v4_regime_strategy_weights 없으면 DEFAULT_REGIME_MATRIX).  
- **v4_trading.py**: 포지션/트레이드 응답에 regime_at_entry; 레짐 가중치 조회 시 v4_regime_strategy_weights 참조(없으면 null).  
- **brain.py**: get_allocation(regime), post_* body에 regime/regime_score.  
- **fund.py**: regime_config, body.regime, calc.regime 등.

---

## 4. 커밋 히스토리

```
7de9e6b1 feat(regime): CUR-STRATEGY-REGIME-BT-VIZ-001 이원 레짐 백필+분석+보고서
dc87039b chore: CUR-REGIME-BACKFILL-002 백필 스크립트 및 보고서 추가
0482b431 feat: CUR-STRATEGY-REGIME-BT-VIZ-001 레짐별 백테스트 분석 API+차트 구현
556ddb17 BT-ENGINE-UPGRADE: add entry/exit datetime, MFE/MAE, regime, indicators, strategy_name, commission to backtest trades
6ed4ff9e feat: notification service — unified Telegram/FCM/Email with trade/regime/emergency alerts + 11 tests
c0251e1d fix: V4.1 integrated — Cursor rules, rebalance regime-only, bridge datetime/CORS/compat, backtest auth/safe response, email is_verified, compat user_id + emergency log
c9598e37 fix: adaptive engine critical fixes — regime direction, snapshot data, hook dedup, datetime.utcnow, attribute names
9bf76576 feat: Phase 5-W2 — regime-strategy weight matrix with score blending + smooth transition
58a6f0b2 PHASE 2-A: Market Regime Detector - initial implementation
```

---

## 5. 전략카드 레짐 사용 현황

- **go100_strategy_cards**에서 `strategy_params::text LIKE '%regime%'` 조건 조회 결과: **0건**.  
- 즉, **레짐을 strategy_params.regime_type / regime_filter 등으로 사용하는 GO100 전략카드는 현재 없음.**

---

## 6. AI 프롬프트 레짐 참조

- **backend/app/services/go100/ai/prompts.py**  
  - 한 곳만 참조: `| get_market_regime | index_daily + vkospi + market_investor | 자체계산 | 시장 레짐 판정 |` (툴 설명 테이블).

---

## 7. 기존 보고서

- **CUR-GO100-REGIME-SOURCE-AUDIT-001-20260223.md**: GO100 vs V4.1 레짐 소스·명칭 불일치 정리, 통일 vs 독립 결정 필요성 기술.  
- **CUR-GO100-REGIME-STRATEGY-RESEARCH-001-20260223.md**: GO100 레짐 활용 현황, V4.1 전략/adaptive/risk_manager 레짐 사용, 레짐별 백테스트·방어 모드 연구.  
- **STRATEGY-FULL-AUDIT-001** 형식의 보고서는 **없음**. 레짐별 백테스트 결과는 REGIME-STRATEGY-RESEARCH-001 및 레짐별 백테스트 분석 API/차트(CUR-STRATEGY-REGIME-BT-VIZ-001)에서 다룸.

---

## 8. 판정

### 8.1 현재 상태: **진행 중 (부분 완료)**

- Phase 2-A 레짐 감지·DB·API·대시/파이프라인 노출은 구현·가동 중.  
- GO100은 유니버스/필터·AI 툴 설명에서만 레짐 사용하며, V4.1 테이블과 **미통합** 및 **명칭 불일치** 유지.  
- v4_regime_strategy_weights 미존재, v4_backtest_regime_analysis 0건 등 **미완료/미활용** 항목 있음.

### 8.2 완료된 항목

- v4_market_regime_daily 테이블 및 552건 데이터 (KOSPI/KOSDAQ, 히스테리시스·pending_regime 포함).  
- MarketRegimeDetector, RegimeResult, 히스테리시스(상승 3일/하락 2일) 로직.  
- /api/v4/regime/* (current, history, indicators, detect) 및 /api/v4/system/market/regime.  
- 대시보드·데이터 파이프라인·AI 트레이딩·브레인·펀드 등에서 레짐 조회/노출.  
- 레짐별 백테스트 분석 API·차트(RegimeTimelineChart, RegimePerformanceBarChart, StrategyRegimeHeatmap 등).  
- adaptive regime_weight, risk_manager 레짐 차단/수정, strategy_engine regime 인자 전달.  
- GO100 advanced_filters 자체 레짐 계산 및 prompts 툴 설명 반영.

### 8.3 미완료·주의 항목

- **v4_regime_strategy_weights** 테이블/뷰 없음 → 코드는 DEFAULT_REGIME_MATRIX 폴백 사용.  
- **v4_backtest_regime_analysis** 0건 → 레짐별 백테스트 결과 적재 미사용 또는 미실행.  
- **GO100 vs V4.1 레짐 통일 미결정**: 소스(자체 계산 vs v4_market_regime_daily), 명칭(STRONG_BULL/STRONG_BEAR vs STRONG_TREND_UP/DOWN) — REGIME-SOURCE-AUDIT-001 결론 대기.  
- **GO100 전략카드**에 regime_type/regime_filter 등 레짐 파라미터 사용 카드 없음.  
- **POST /api/v4/regime/detect** 인증/관리자 권한 미적용 (TODO Phase 5).

### 8.4 다음 조치 필요 사항

1. **v4_regime_strategy_weights** 도입 여부 결정 후, 필요 시 마이그레이션 및 코드 연동.  
2. **v4_backtest_regime_analysis** 적재 파이프라인/스크립트 실행 여부 확인 및 필요 시 레짐별 백테스트 결과 적재.  
3. **GO100 레짐 소스 통일** (REGIME-SOURCE-AUDIT-001): v4_market_regime_daily + V4.1 명칭으로 통일할지, GO100 독립 유지할지 결정 후 반영.  
4. GO100 전략카드에 레짐 필터/가중치를 쓸 계획이 있다면 스키마·카드 생성 플로우 설계.  
5. /api/v4/regime/detect 관리자 권한 및 감사 로그 검토.

---

## 9. 참고

- **STRATEGY-FULL-AUDIT-001** 형식의 별도 보고서는 없음. 레짐별 백테스트는 **CUR-GO100-REGIME-STRATEGY-RESEARCH-001** 및 **CUR-STRATEGY-REGIME-BT-VIZ-001** 관련 API/차트로 다뤄짐.  
- **인계서 Phase 2와의 관계**: Phase 2-A에서 Market Regime Detector 초기 구현(58a6f0b2)이 이루어졌고, 현재 일일 레짐 판정·v4_market_regime_daily 적재·레짐 API·대시/파이프라인 노출까지 반영된 상태. Phase 5-W2에서 레짐–전략 가중치 매트릭스(9bf76576)가 도입되었으나 DB 테이블(v4_regime_strategy_weights)은 미생성으로 폴백 사용 중.
