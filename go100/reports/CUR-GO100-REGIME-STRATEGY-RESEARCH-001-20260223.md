# CUR-GO100-REGIME-STRATEGY-RESEARCH-001
# GO100 레짐 활용 현황 + 하락장 방어 모드 심층 연구

## 기본 정보
- 작업일: 2026-02-23 17:30 KST
- 서버: root@211.188.51.113
- 작업 유형: 읽기 전용 조사 + 연구 보고서
- CEO 지시: GO100의 레짐 운영전략 반영 여부 확인 + 방어 모드 심층 연구

---

## PART A: GO100에서 레짐 데이터 활용 현황

### 현재 상태 (A-1~A-4 결과)

- **A-1 GO100 코드 내 regime 참조**
  - `backend/app/services/go100/universe/advanced_filters.py`: `get_market_regime()` 메서드 존재. **v4_market_regime_daily가 2건뿐이므로** DB 대신 **자체 계산**으로 레짐 산출 (index_daily KOSPI + v4_vkospi_daily + v4_market_investor_daily 활용).
  - 5단계 분류: `STRONG_BULL`(80+), `MILD_TREND_UP`(60+), `SIDEWAYS`(40+), `MILD_TREND_DOWN`(20+), `STRONG_BEAR`(그 미만). V4.1 regime_detector와 **네이밍/임계값이 상이** (GO100은 STRONG_BULL/STRONG_BEAR, V4.1은 STRONG_TREND_UP/STRONG_TREND_DOWN).
  - `backend/app/services/go100/ai/prompts.py`: `get_market_regime` 툴 설명에 "시장 레짐 판정" 기재.
- **A-2 GO100 전략카드 생성/실행**
  - `backend/app/services/go100/strategy/` 내 **regime 키워드 검색 결과 없음**. 전략카드 생성·실행 로직에서 레짐을 직접 참조하는 코드는 없음.
- **A-3 GO100 API**
  - `backend/app/api/` 내 go100 관련 라우터에서 **regime 검색 결과 없음**. 레짐 전용 엔드포인트는 없음.
- **A-4 GO100 프론트엔드**
  - `frontend/src`에서 "regime", "레짐", "시장 상태", "market state" + "go100" 조건 검색 시 **GO100 전용 레짐 표시 UI 없음**. 대시보드 등 일반 시장 상태 위젯만 존재.

**요약**: GO100은 **유니버스/필터 단계**에서만 레짐을 사용하며, **V4.1 공용 테이블(v4_market_regime_daily)을 쓰지 않고** advanced_filters 내 자체 계산으로 regime/regime_score를 구해 AI 프롬프트 등에 활용한다. 전략카드 생성·API·프론트엔드에는 레짐 전용 노출이 없음.

### 레짐 판정 모듈 (V4.1 regime_detector.py) — A-5~A-7

- **파일**: `backend/app/services/market/regime_detector.py`
- **5단계 레짐**: `STRONG_TREND_UP`, `MILD_TREND_UP`, `SIDEWAYS`, `MILD_TREND_DOWN`, `STRONG_TREND_DOWN`
- **판정 소스**: KOSPI/KOSDAQ 20일 수익률, MA 5/20/60 배열(BULL_ALIGNED/BEAR_ALIGNED/MIXED), 20일 양봉 비율, 거래대금 추이, 외국인 20일 순매수, 상한가/하한가 비율, VKOSPI(선택).
- **점수→레짐 매핑** (`_map_score_to_regime`):  
  - 81 이상 → STRONG_TREND_UP  
  - 61 이상 → MILD_TREND_UP  
  - 41 이상 → SIDEWAYS  
  - 21 이상 → MILD_TREND_DOWN  
  - 그 미만 → STRONG_TREND_DOWN  
- **히스테리시스 (Phase 2-C)**: 상승 전환 3일 연속, 하락 전환 2일 연속 시 전환 허용; 2단계 이상 점프 시 1단계만 이동; STRONG_TREND_DOWN 탈출 시 3일 연속 score 개선 추가 확인.
- **출력**: `RegimeResult` (regime, regime_score, indicators, previous_regime, transition_applied, transition_note). PRE_MARKET에서 Orchestrator가 호출하며 `v4_market_regime_daily`에 저장.

### GO100 레짐 반영 여부 판단

- **결론: 부분 반영**
  - **반영되는 부분**: GO100 유니버스/advanced_filters에서 `get_market_regime()`으로 **자체 계산 레짐**을 사용해 시장 상태를 판정하고, AI 프롬프트 툴 설명에 포함됨. 즉 "레짐 개념"은 GO100 파이프라인에 들어가 있음.
  - **미반영/불일치**: (1) V4.1 공식 테이블 `v4_market_regime_daily` 및 `regime_detector.py`와 **동기화되지 않음** (데이터 2건이라는 전제로 자체 계산 사용). (2) 전략카드 생성·실행, API, 프론트엔드에는 레짐 기반 분기 또는 노출이 없음. (3) GO100 레짐 명칭(STRONG_BULL/STRONG_BEAR)과 V4.1(STRONG_TREND_UP/DOWN) 불일치.

---

## PART B: V4.1 전략별 레짐 활용 현황

### strategy_engine (B-1)

- **파일**: `backend/app/services/strategy/strategy_engine.py`
- `generate_signals(..., regime: Optional[str] = None, ...)` 로 **현재 레짐을 인자로 받아** 각 활성 전략의 `strategy.generate_signals(..., regime=regime)`에 전달. 전략별로 레짐에 따른 시그널 필터/가중치 적용 가능.

### risk_manager (B-2)

- **파일**: `backend/app/services/risk/risk_manager.py`
- `pre_trade_check(..., regime: str | None = None, ...)`:
  - `regime == "STRONG_TREND_DOWN"` 이면 **매매 불가** (approved=False, checks_failed=["REGIME"]).
  - 그 외 레짐은 `RiskConfig.REGIME_RISK_MODIFIERS`로 금액 조정:  
    STRONG_TREND_UP 1.15, MILD_TREND_UP 1.0, SIDEWAYS 0.8, MILD_TREND_DOWN 0.5, STRONG_TREND_DOWN 0.0(위에서 이미 차단).

### adaptive_engine (B-3)

- **regime_weight.py**: `v4_market_regime_daily`에서 최신 레짐 조회. 레짐별 기본 전략 가중치 매트릭스(DEFAULT_REGIME_MATRIX) 및 전환 시 조정(`get_regime_transition_adjustment`).
- **fund_rebalancer.py**: `regime` 인자로 리밸런스 여부/가중치 결정, `should_rebalance(new_regime=regime)`.
- **engine.py**: `get_current_regime()` → `get_adjusted_weights(regime=..., period_days=7)`, `_is_emergency_transition(prev_regime, curr_regime)`(2단계 이상 하락 또는 STRONG_DOWN 진입 시 긴급 전환), 일간/주간 사이클 결과에 `regime` 포함.

### pipeline_orchestrator (B-4)

- `run_desk1_cycle()` 등 반환값에 `"market_regime": result_scan.get("market_regime")` 포함. 스캔 결과에서 레짐을 상위로 전달.

### strategy_cards 레짐 컬럼 (B-5)

- `information_schema.columns` 조회 결과 **regime 관련 컬럼 없음**. strategy_cards에는 레짐 컬럼이 정의되어 있지 않음.

### 레짐별 백테스트 수익률 (B-6, C-2)

- **v4_backtest_trades**: 총 176,896건. **regime_at_entry는 미사용**(NULL만 존재, 0건 채움).
- **trade_date × v4_market_regime_daily 조인** 기준 레짐별 집계:

| regime            | trade_count | avg_pnl | win_rate |
|-------------------|------------|---------|----------|
| MILD_TREND_DOWN   | 14,086     | 491,279 | 0.24     |
| MILD_TREND_UP     | 2,649      | 116,553 | 0.22     |
| SIDEWAYS          | 24,624     | 320,429 | 0.23     |
| STRONG_TREND_DOWN | 17,824     | 519,128 | 0.23     |

- 승률은 레짐별로 비슷(0.22~0.24). 평균 PnL은 STRONG_TREND_DOWN에서 오히려 높게 나옴(표본·기간 의존적). **regime_at_entry를 채우면** 진입 시점 레짐 기준 분석이 가능해짐.

---

## PART C: 하락장 방어 모드 심층 연구

### 1. 문제 정의

레짐 전환 시점(특히 상승→하락)에 전략 신호가 급변해 손실 위험이 커진다. 단순 "48h 50% 축소"의 한계:

- 모든 레짐 전환에 동일 대응 (상승→횡보 vs 상승→하락 구분 없음).
- 고정 50%는 시장 변동성(ATR/VIX 등)을 반영하지 못함.
- 전환 후 복귀(whipsaw) 시 기회비용 과다.

### 2. 과거 레짐 전환 분석

**전환 이력 (C-1)**  
v4_market_regime_daily 기준 전환일:

| date       | prev_regime     | new_regime       |
|-----------|------------------|-------------------|
| 2025-11-20 | (null)          | SIDEWAYS          |
| 2025-11-24 | SIDEWAYS        | MILD_TREND_DOWN   |
| 2025-12-05 | MILD_TREND_DOWN | STRONG_TREND_DOWN |
| 2026-01-07 | STRONG_TREND_DOWN | MILD_TREND_DOWN |
| 2026-01-12 | MILD_TREND_DOWN | SIDEWAYS          |
| 2026-01-16 | SIDEWAYS        | MILD_TREND_DOWN   |
| 2026-01-22 | MILD_TREND_DOWN | SIDEWAYS          |
| 2026-02-12 | SIDEWAYS        | MILD_TREND_UP     |

**전환 직후 48h(전환일~+2일) 거래 수·평균 PnL (C-3)**

| change_date | old_regime     | new_regime       | trades_48h | avg_pnl_48h |
|-------------|----------------|------------------|------------|-------------|
| 2025-11-20 | (null)         | SIDEWAYS         | 1,634      | 365,413     |
| 2025-11-24 | SIDEWAYS       | MILD_TREND_DOWN  | 2,530      | 244,337     |
| 2025-12-05 | MILD_TREND_DOWN| STRONG_TREND_DOWN| 834        | 166,932     |
| 2026-01-07 | STRONG_TREND_DOWN | MILD_TREND_DOWN | 2,732    | 665,566     |
| 2026-01-12 | MILD_TREND_DOWN | SIDEWAYS        | 2,854      | 346,343     |
| 2026-01-16 | SIDEWAYS       | MILD_TREND_DOWN  | 984        | 594,011     |
| 2026-01-22 | MILD_TREND_DOWN | SIDEWAYS        | 2,431      | 311,544     |
| 2026-02-12 | SIDEWAYS       | MILD_TREND_UP    | 2,649      | 116,553     |

- **상승→하락** 전환(예: SIDEWAYS→MILD_TREND_DOWN, MILD_TREND_DOWN→STRONG_TREND_DOWN) 직후 48h 평균 PnL이 상대적으로 낮거나 거래 수가 줄어드는 구간 존재. 반대로 **하락→상승/횡보** 전환(STRONG_TREND_DOWN→MILD_TREND_DOWN, MILD_TREND_DOWN→SIDEWAYS) 직후는 평균 PnL이 더 크게 나옴.
- 데이터는 백테스트 집계이며, 진입 시점 레짐(regime_at_entry)이 비어 있어 "전환 직후 진입한 거래만" 필터한 분석은 미실시. 추후 regime_at_entry 채우면 전환 직후 진입 거래만 분리 분석 가능.

### 3. 제안: 다층적 방어 전략 (Multi-Layer Defense)

#### Layer 1 — 전환 강도 분류

- **상승→하락**(MILD_TREND_UP/SIDEWAYS → MILD_TREND_DOWN/STRONG_TREND_DOWN): 위험도 높음 → 포지션/신규 진입 축소·지연 강하게 적용.
- **상승→횡보**, **횡보→하락**: 중간 위험 → 중간 축소.
- **하락→횡보**, **횡보→상승**: 방어 완화 또는 정상 배분으로 점진 복귀.
- 구현: `regime_detector`의 `previous_regime`과 현재 `regime`으로 전환 유형(up_to_down, down_to_up, to_sideways 등)을 분류하고, 유형별로 다른 "방어 계수" 또는 "쿨다운 시간" 적용.

#### Layer 2 — 변동성 연동 포지션 축소

- 단순 50% 고정 대신, **ATR(일간/주간)** 또는 **VKOSPI** 구간별로 축소 비율을 다르게 설정.
  - 예: VKOSPI &gt; 25 → 40% 수준, 20~25 → 50%, &lt;20 → 60% 등.
- risk_manager의 `REGIME_RISK_MODIFIERS`를 레짐×변동성 2차원으로 확장하거나, 별도 "transition_cool_down_modifier"에서 변동성 구간을 참조.

#### Layer 3 — DESK별 차등 대응

- **DESK2(단타)**: 레짐 하락 전환 직후 48h 신규 진입 차단 또는 최소 비중만 허용.
- **DESK3(스윙)**: 신규 진입만 제한(기존 포지션 유지), 손절선만 타이트하게 옵션 적용.
- **DESK4(중기)**: 신규 진입 제한 + 손절만 타이트(트레일링 스탑 비율 축소 등).
- pipeline_orchestrator/desk별 commander에서 "transition_cool_down" 플래그와 DESK ID를 함께 보고, desk_id별로 다른 규칙 적용.

#### Layer 4 — 점진적 복귀 (Gradual Recovery)

- 48h 후 일시에 100% 복귀하지 않고, **25% → 50% → 75% → 100%** 처럼 N일(또는 N사이클)에 걸쳐 배분 복구.
- 구현: 전환일(transition_date)과 현재일 차이로 "복귀 단계"를 계산하고, 단계별 modifier를 곱해 최종 허용 비중 결정.

#### Layer 5 — 레짐 확신도 기반 판단

- `regime_detector`는 이미 `regime_score`, `transition_applied`, `transition_note`를 제공. **확신도가 낮은 경우**(예: score가 41 근처로 SIDEWAYS 경계, 또는 "상승 1/3일" 등 미확정 전환) 방어를 더 강하게 적용.
- 예: transition_applied=True 이면서 transition_note가 "하락 1/2일"이면 48h 쿨다운 + 50% 축소; "하락 전환 적용" 확정 후에는 48h 40% 등으로 강화.

### 4. 구현 우선순위 제안

1. **1순위 — Layer 1(전환 강도 분류) + Layer 4(점진적 복귀)**  
   - 기존 48h 50%를 "전환 유형별 계수 + 전환일 기준 단계적 복귀"로 대체. 구현 규모가 상대적으로 작고, whipsaw 완화와 기회비용 균형에 직결.
2. **2순위 — Layer 3(DESK별 차등)**  
   - DESK2부터 적용 후 DESK3/4 확대. 단타가 레짐 전환에 가장 취약하다는 가정에 부합.
3. **3순위 — Layer 2(변동성 연동)**  
   - VKOSPI/ATR 데이터가 이미 있으므로, 레짐 전환 시 modifier에 변동성 구간 반영.
4. **4순위 — Layer 5(확신도)**  
   - regime_detector 출력 확장(확신도 플래그 또는 구간) 후, risk_manager/adaptive에서 참조.

### 5. GO100 적용 방안

- **단기**: GO100은 현재 유니버스 단계에서만 자체 레짐을 사용하므로, **V4.1과 동일한 레짐 정의를 쓰지 않음**. GO100 전략카드 생성·실행에 "레짐 전환 직후 48h 신규 진입 축소"를 넣으려면 (1) 레짐 소스를 V4.1 `v4_market_regime_daily`로 통일할지, (2) 계속 자체 계산을 쓰되 "전환일" 개념을 GO100 내부에서 도입할지 정책 결정이 필요.
- **중기**: V4.1에서 Layer 1~4가 안정화되면, GO100에도 "레짐 전환 강도"와 "점진적 복귀"를 옵션으로 노출(예: 전략카드 메타 또는 실행 파라미터)해, GO100 전용 전략만 선택적으로 방어 모드를 켤 수 있게 함.
- **데이터 정합성**: `regime_at_entry`를 백테스트/실거래 기록 시 채우면, 이후 "전환 직후 진입" 거래만 추려서 GO100·V4.1 공통으로 효과 검증 가능.

---

## GitHub URL

- 보고서: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-REGIME-STRATEGY-RESEARCH-001-20260223.md
