# CUR-V41-UNIFIED-ENGINE-REVIEW-002 — 통합 엔진 전방위 종합 검토 보고서
> 작성일: 2026-03-01 | 담당: Claude Code Sonnet 4.6 | 레포: kis-autotrade-v4 (phase-2c-command-center)

---

[인계 확인]
직전 완료: CUR-V41-UNIFIED-ENGINE-MOCK-SETUP-001 (Task A)
현재 단계: Cursor #22 — Task B 착수 전 전방위 검토
CEO 지시 적용: D-001(단순사고 금지), D-002(보고서 push 필수)
strategy_cards: 60개
open_positions: 14개

---

## 0. 검토 목적

Task A 보고서(CUR-V41-UNIFIED-ENGINE-MOCK-SETUP-001)에서 16개 항목의 차이점을 분석했다.
본 보고서는 **Task B 구현 착수 전** 다음 3가지를 추가 전방위 검토한다:

1. 통합 엔진 설계에 **빠진 구성요소 및 위험 요인**
2. **GO100 프로젝트 충돌** 여부
3. **AI 매매 검증 로직(AiScorer, ScoringEngine)** 반영 방안

검토 파일: ai_scorer.py(486줄), go100_bridge_client.py(335줄), broker_gateway.py(251줄),
           auto_trade_engine.py(799줄), system/orchestrator.py(664줄),
           v41/modules/scoring_engine.py(153줄), desk2 layer1~4 디렉토리

---

## 1. 통합 엔진 설계에 빠진 항목 — 12가지

### [GAP-01] SystemOrchestrator L0 와 중복 — 가장 위험

`backend/app/services/system/orchestrator.py` (664줄)에 이미 완성도 높은 L0 상태 머신이 존재한다.

```
SystemState: IDLE → PRE_MARKET(07:55) → READY(08:50) → TRADING(09:00)
             → CLOSING(15:20) → POST_MARKET(15:30) → IDLE
```

이 오케스트레이터는 이미:
- `order_executor.execute_buy()` 호출 구조 완비
- `position_manager.check_positions()` / `close_day_positions()` 완비
- `strategy_engine.generate_signals()` 60초 사이클 완비
- `fund_pool`, `reservation_manager`, `risk_manager`, `reentry_guard` 연동 완비
- `price_poller.get_price_safe()` 연동 완비

**→ 통합 엔진 `scripts/run_unified_engine.py`가 이 L0 오케스트레이터와 충돌/중복 발생 위험.**
→ 설계 결정 필수: 통합 엔진이 ① L0 오케스트레이터를 `--mode` 어댑터로 확장하는가,
  아니면 ② L0와 완전히 별개 프로세스로 실행되는가.
→ **권장: L0 오케스트레이터 `order_executor` + `data_source` 어댑터를 교체하는 방식으로 통합.**
  별개 프로세스로 실행 시 `v4_system_heartbeat` 테이블 충돌 + 60초 사이클 이중 실행 위험.

---

### [GAP-02] AI 점수(ScoringEngine) → CTE 파이프라인 연동 미설계

**현황 (ScoringEngine — `v41/modules/scoring_engine.py`)**:
```python
# D6/D7 → cs_ai_gap 사용, 나머지 → cs_ai
score_key = "cs_ai_gap" if strategy_type in ("D6", "D7") else "cs_ai"
final_cs = int(round((1 - w) * rule_cs + w * ai_score))  # w=0.15
```

**현황 (CTE 파이프라인 L3.5)**:
- L3.5: `conviction_score ≥ 50` → CTE 필터 통과
- 현재 `conviction_score`(CS)는 CTE 파이프라인이 직접 계산

**누락**:
- 통합 엔진 설계(`unified_engine/core/`)에 ScoringEngine 호출 위치 미기재
- `rule_cs` stub(`= 50.0`)이 현재 실제 CTE CS 점수로 교체되지 않음
- AI blend 후 최종 CS를 CTE L3.5 임계값(≥50)으로 전달하는 파이프라인 미설계
- **D6/D7 전략에서 `cs_ai_gap`을 써야 함** — 통합 엔진 신호 생성기에서 `strategy_type` 전달 필수

---

### [GAP-03] AutoTradeEngine (구식 엔진) 공존 문제

`backend/app/services/auto_trade_engine.py` (799줄)는 psycopg2 기반 **구식 자동매매 엔진**이다.
현재 V4.1 백엔드(포트 8003/8001)에서 `v4_trade_schedules` 폴링 방식으로 작동 중.

```python
class AutoTradeEngine:
    def __init__(self, dry_run=None):
        self.dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"
```

**충돌 위험**:
- AutoTradeEngine과 통합 엔진이 **동시에 주문**을 낼 수 있음
- `v4_trade_executions` 테이블에 중복 기록 가능
- DRY_RUN=true 확인 필수. 실계좌(account_id 5,6) 주문 이중 실행 최악 케이스

**→ Task B 착수 전 AutoTradeEngine의 현재 실행 상태 확인 및 명시적 비활성화 계획 수립 필요.**

---

### [GAP-04] BrokerGateway account_id 실계좌 보호 미비

`backend/app/core/broker_gateway.py`의 `_place_order_impl()`은:
```python
if account and not account["is_mock"]:
    logger.warning("BrokerGateway place_order REAL account: ...")
```
**WARNING 로그만 남길 뿐 실계좌(account_id 5,6) 주문을 차단하지 않는다.**

**→ 통합 엔진의 `order_executor` 어댑터에서 account_id 5,6 진입 시 `assert False` 또는 예외 발생 필수.**
→ Mock 모드에서는 반드시 `is_mock=True` 계좌만 허용하는 단단한 가드 필요.

---

### [GAP-05] DCS(Desk Conviction Score) 계산 미설계

통합 엔진 설계에 `signal_generator.py`가 있지만, 실제 **DCS 계산** 방법이 미기재.
현재:
- BT: `make_synthetic_signal()` — 랜덤 dcs_grade="A"/"B"/"C"
- Paper: `make_synthetic_signal()` — 고정 dcs_grade="B"
- 실제 DCS: VWAP, ATR, RSI, 투자자 동향 등 실시간 지표 기반 계산이어야 함

**→ 1분봉 데이터 기반 실시간 DCS 계산 로직 설계가 Task B의 핵심 난이도.**
→ `v4_ohlcv_minute` 테이블에서 당일 분봉 데이터를 읽어 VWAP/ATR 계산해야 함.
→ ai_scorer.py는 이미 `compute_track_b_from_minute()`을 통해 분봉 기반 VWAP 계산 구현됨 — 재사용 가능.

---

### [GAP-06] 실시간 청산 로직 완전 미구현 — 양쪽 모두

Task A에서 지적된 사항 재강조:
| 청산 유형 | BT | Paper | Mock(예정) | Live(예정) |
|----------|-----|-------|-----------|-----------|
| 하드스톱 -3% | 통계 반영 | 미구현 | 미구현 | 미구현 |
| ATR 트레일링 | 파라미터만 계산 | 파라미터만 계산 | 미구현 | 미구현 |
| 15:30 시간청산 | 미구현 | 미구현 | 미구현 | 미구현 |

SystemOrchestrator에서 `_handle_closing()` → `close_day_positions()` 구조는 있지만,
실제 포지션 청산 가격 결정 로직(현재가 조회 → KIS API 매도)이 없음.

**→ Task B의 `order_executor` 어댑터에서 실시간 청산 구현이 필수 포함 항목.**
→ `price_poller`는 L0 오케스트레이터에 이미 슬롯 존재 → 활용 가능.

---

### [GAP-07] D7 갭다운 필터 0.70 → 0.80 미반영 (3일 후 PAPER_LIVE 첫 실행)

`monitor_paper_d6d7.py`에서 명시:
```python
# 현행 코드 0.70 vs 확정 기준 0.80 — 코드 미반영 상태 (2026-03-01)
```

**03-02 첫 실행** 시 D7 갭다운 필터가 잘못된 값(0.70)으로 실행된다.
통합 엔진 구현 전에 이 값을 먼저 수정해야 한다.

---

### [GAP-08] cron 충돌 — live_paper_cte.py 08:50 vs 통합 엔진 예정 스케줄

현재 등록된 cron:
```
50 8 * * 1-5  → /root/kis-autotrade-v4/scripts/live_paper_cte.py
40 15 * * 1-5 → run_daily_hypothesis_pipeline.py
0 22 * * 1-5  → run_hypothesis_backtest.py
```

통합 엔진 예정 cron(Task D):
```
?? 7:55 premarket
?? 8:50 signal (READY 진입)
?? 9:00 monitor (TRADING 시작)
?? 15:30 close
```

`live_paper_cte.py` 08:50과 통합 엔진 08:50 signal이 동시에 실행되면:
- `v4_paper_trades` 테이블에 중복 INSERT
- CTE 파이프라인 동시 호출로 DB 부하
**→ 통합 엔진 `paper` 모드 완성 후 `live_paper_cte.py` cron을 반드시 제거해야 함.**
→ Task D에서 cron 교체를 명시적 단계로 포함 필요.

---

### [GAP-09] PF 우선순위 슬롯 배분 페이퍼 미구현

Task A에서 확인: BT에만 `PRIORITY_ORDER = ["D6","D5","D4","D2","S1","D7","D-ORB"]` 존재.
`strategy_params.py`의 `STRATEGY_PRIORITY_ORDER = [D6, D5, D4, D7, D2, S1]`와 순서 불일치:
- BT: D6→D5→D4→D2→S1→D7→D-ORB
- strategy_params.py: D6→D5→D4→D7→D2→S1

**→ 통합 엔진에서 `strategy_params.py` 정의를 공식 기준으로 사용하고, BT의 PRIORITY_ORDER 제거 필요.**

---

### [GAP-10] D2A/D2B/D2C 서브타입 분기 미설계

`strategy_params.py`에 D2A/D2B/D2C 서브타입이 정의되어 있으나,
통합 엔진 `signal_generator.py` 설계에서 이 서브타입 분기가 누락됨.
각 서브타입별로 `cs_threshold`, `eqs_threshold`, `capital_pct`가 다르다.

**→ `TradeSignal` 생성 시 D2의 서브타입(A/B/C)을 명시적으로 전달하도록 설계 필요.**

---

### [GAP-11] 자본금 계산 — Mock 계좌 잔고 실조회 방법 미정

통합 엔진은 `--mode mock` 시 KIS Mock API에서 실제 잔고를 조회해야 한다.
BrokerGateway.get_balance() → `AccountBalance.deposit`으로 가용 자금 계산 가능하나,
Mock 계좌(account_id?)가 아직 DB에 등록되지 않았다.

**→ Task D에서 Mock 전용 계좌 생성(accounts 테이블 INSERT, is_mock=True) 및 account_id 확정 필요.**
→ KIS Mock API 토큰 발급(`https://openapivts.koreainvestment.com:29443`) 및 저장 필요.

---

### [GAP-12] desk2 Layer1~4 기존 구현 활용 여부 미검토

`backend/app/services/trading/desk2/`에는 완성된 4레이어 아키텍처가 존재:
- `layer1_discovery/`: 7개 조건 파일 (c1_gap~c7_oversold)
- `layer2_strategy/`: alpha_gap, bravo_orb, charlie_vi, delta_vwap, echo_abcd, foxtrot_sector, golf_reversal
- `layer3_orchestration/orchestrator.py` (222줄)
- `layer4_execution/` (비어 있음 — 실행 미구현)

통합 엔진 `signal_generator.py`가 desk2 Layer1 discovery + Layer2 strategy와 중복될 수 있음.
**→ 통합 엔진은 desk2 Layer1/2를 재사용하거나, 별도 CTE 전용 신호 생성으로 완전히 대체하는지 결정 필요.**

---

## 2. GO100 프로젝트 충돌 분석

### [GO100-01] bridge.py 라우터 — 정상, 충돌 없음

V4.1 → GO100 연동은 HTTP REST(`http://127.0.0.1:8002/api/go100/bridge`)만 사용.
직접 임포트 없음. **Go100BridgeClient 방식 = 안전.**

### [GO100-02] hypothesis_engine.py ← go100_backtest_runs 테이블

GO100 AI 가설검증 파이프라인(L1~L3)은 `go100_backtest_runs` 테이블에서 전략 성과를 읽는다.
통합 엔진 백테스트 결과가 `go100_backtest_runs`에 쌓이는지 확인 필요:
- 현재 BT는 `/tmp/cte_backtest_daily.json` + CSV만 저장
- `go100_backtest_runs`에 통합 엔진 BT 결과가 INSERT되지 않으면 AI 가설검증 대상에서 누락

**→ 통합 엔진 backtest 모드 완료 후 `go100_backtest_runs` INSERT 로직 추가 필요 (Task C).**

### [GO100-03] ai_scorer.py 싱글톤 — V4.1에서 직접 임포트 금지

`ai_scorer = AiScorer()` (global singleton)은 **GO100 서버(포트 8002)에서만 실행**.
V4.1 코드에서 직접 임포트 시 joblib 모델 4개를 메모리에 중복 적재 + 두 프로세스 간 캐시 불일치 위험.

**→ V4.1 통합 엔진은 반드시 `Go100BridgeClient.request_ai_scoring()`으로만 호출.**
→ `ScoringEngine.compute_final_cs(bridge=bridge_client)` 패턴 유지.

### [GO100-04] go100_episodic_memory 테이블 혼입 방지

`Go100BridgeClient.log_episodic_memory()`는 `agent_id=V4.1_DESK_AGENT`로 기록.
GO100 봇 데이터(`agent_id=GO100_BAEKEOUK`)와 분리됨. **충돌 없음.**

Shadow 로그(`ScoringEngine._log_shadow`) → `event_type="ai_score_shadow"` 로 GO100 메모리에 기록.
통합 엔진에서도 이 패턴 유지 필요.

### [GO100-05] go100_backtest_runs 테이블 — write 충돌 위험

HypothesisEngine(L3)이 야간 배치에서 `go100_backtest_runs`를 READ.
통합 엔진 BACKTEST 모드가 같은 테이블에 WRITE 시 동시 접근 가능.
→ **cron 시간 분리 필요**: 통합 엔진 BT는 주간/수동, 가설 배치는 22:00 — 충돌 최소화.

---

## 3. AI 매매 검증 로직 통합 방안

### 3.1 현재 AiScorer 처리 흐름

```
AiScorer.score(ticker, db)
  ├── compute_realtime_features()
  │     ├── ohlcv_daily (최근 65일) — Track A
  │     ├── v4_investor_daily (최근 20일) — Track A
  │     ├── v4_market_regime_daily — 레짐
  │     ├── v4_ohlcv_minute (당일) — Track B
  │     └── go100_news_items (5일) — News
  ├── _apply_zscore()
  ├── _predict_all() → up_5d_prob, mfe_60min, mfe_3d, gap_d1
  └── _compute_scores()
        ├── cs_ai     = round(0.6*norm_mfe60 + 0.4*norm_mfe3d)  ← 일반 전략
        └── cs_ai_gap = round(norm_gap)                          ← D6/D7 갭전략
```

### 3.2 ScoringEngine → CTE 통합 방법

```python
# 통합 엔진 signal_generator.py에서 (설계 제안)
for strategy_type, ticker in candidates:
    rule_cs = cte_pipeline.compute_cs(ticker, ...)   # 실제 CTE CS 계산
    final_cs = await scoring_engine.compute_final_cs(
        ticker=ticker,
        rule_cs=rule_cs,
        strategy_type=strategy_type,     # D6/D7 → cs_ai_gap
        bridge=bridge_client,
    )
    if final_cs < 50:
        continue  # L3.5 블로킹
```

### 3.3 통합 시 주의사항

| 항목 | 현황 | 통합 엔진 조치 |
|------|------|----------------|
| blend_weight | 0.15 (Phase 1 Shadow) | 환경변수 V41_AI_BLEND_WEIGHT 유지 |
| Fail-Open | AI 불가 시 rule_cs 100% | 유지 필수 — 실매매 차단 금지 |
| 모델 파일 | data/go100/models/go100_brain_v2_*.joblib | GO100 서버에서만 로드 |
| TTLCache | ticker:날짜 키, TTL=300초 | 공유 불가 (프로세스 분리) |
| Track B 분봉 | v4_ohlcv_minute (당일 분봉) | 장중 실시간 적재 여부 확인 필요 |
| D6/D7 cs_ai_gap | gap_d1_raw 기반 | 통합 엔진 strategy_type 전달 필수 |

### 3.4 v4_ohlcv_minute 당일 적재 확인 필요

AiScorer.Track B는 `v4_ohlcv_minute WHERE trade_date = today`를 조회.
**장중에 이 테이블이 실시간으로 채워지는가?** 현재 스크립트를 확인해야 함.
적재되지 않으면 AiScorer Track B가 fallback(VWAP 근사)으로 작동 → AI 점수 정확도 저하.

---

## 4. 기타 전방위 위험 요인

### [RISK-01] 03-02 첫 페이퍼 실행 전 필수 수정사항

| 항목 | 현재 | 필요 조치 | 마감 |
|------|------|----------|------|
| D7 갭다운 필터 | 0.70 | 0.80으로 수정 | 03-02 전 |
| Paper PnL 계산 | None | 진입가/청산가/수익률 추가 | 03-02 전 |
| Paper 비용 차감 | 미처리 | 0.47% 차감 로직 | 03-02 전 |
| Paper 시장 컨텍스트 | 하드코딩 FLAT | 실제 KOSDAQ 레짐 조회 | 낮은 우선순위 |

**03-02 08:50 첫 실행까지 약 2일. Task B보다 페이퍼 버그픽스가 먼저.**

### [RISK-02] 실계좌 보호 다중 계층 요구

통합 엔진에서 `--mode live` 실행 시 반드시 3중 안전장치:
1. `assert account_id not in (5, 6)` — 코드 레벨
2. `if not account["is_mock"]: raise` — Mock 모드에서
3. KIS 실전 API 도메인 `openapi.koreainvestment.com` 사용 시 별도 확인 다이얼로그 (스크립트 실행 시 --confirm-live 플래그 요구)

### [RISK-03] v4_ohlcv_minute 실시간 수집 미확인

AI 점수 Track B, DCS 계산, ATR/VWAP 계산 모두 분봉 데이터 필요.
현재 `v4_ohlcv_minute`가 장중 실시간으로 수집되는지 확인 필요.
수집이 없으면 통합 엔진 전체가 일봉 기반으로 강등.

### [RISK-04] 백테스트 PF 2.368 과적합 미해결 (CRITICAL 지속)

`make_synthetic_signal(is_winner=True/False)` 미래정보 주입은 Task C에서 해결.
통합 엔진 BT가 실제 분봉 신호로 교체되면 PF가 크게 하락할 수 있음 — **CEO에게 사전 고지 필요**.
재현 목표를 PF ≥ 1.5 (현실적 기대치)로 재설정하는 것이 바람직.

### [RISK-05] HAV 큐 통합

HypothesisEngine L3 → `data/go100/hav_queue/tasks.json` 등록.
통합 엔진 BT 완료 후 `go100_backtest_runs` 결과가 AI 판정 → HAV로 자동 연결되어야 함.
**현재 연결 고리가 끊어져 있음 → Task C~D에서 연결 필요.**

---

## 5. 통합 우선순위 재정렬 (CEO 확인 요청)

Task A 결과를 반영하여 Task B~E의 실행 순서를 재제안한다:

| 우선순위 | 작업 | 이유 |
|--------|------|------|
| **즉시 (03-01~02)** | D7 갭다운 0.80 수정 | 첫 실행 03-02 |
| **즉시** | Paper PnL 계산 + 비용 0.47% | 첫 실행 03-02 |
| **Task B-1** | AutoTradeEngine 현황 파악 + 비활성화 계획 | 중복 주문 방지 |
| **Task B-2** | 통합 엔진 `paper` 모드 (live_paper_cte 대체) | CEO 최우선 |
| **Task B-3** | ScoringEngine → CTE CS 연동 (rule_cs stub 교체) | AI 점수 실적용 |
| **Task C** | BT 미래정보 제거 → PF 재측정 | 과적합 해소 |
| **Task D** | Mock 계좌 생성 + KIS Mock API + v4_mock_trades | 모의실매매 |
| **Task E** | HANDOVER + REPORT push | 인계 |

---

## 6. 체크포인트

- [x] Task A 보고서 push 완료 (commit 5a5c52c)
- [x] ai_scorer.py (486줄) 전체 분석
- [x] go100_bridge_client.py (335줄) 전체 분석
- [x] broker_gateway.py (251줄) 전체 분석
- [x] scoring_engine.py (153줄) 전체 분석
- [x] system/orchestrator.py (664줄) 전체 분석
- [x] auto_trade_engine.py (799줄) 분석
- [x] desk2 layer1~4 디렉토리 구조 확인
- [x] 통합 엔진 누락 12개 항목 식별
- [x] GO100 충돌 5개 항목 분석 (충돌 없음 확인)
- [x] AI 매매 검증 로직 통합 방안 설계
- [x] 기타 5개 위험 요인 정리
- [ ] CEO 검토 후 Task B 착수 승인
- [ ] 03-02 전 버그픽스(D7 필터, Paper PnL) 적용
- [ ] Task B: 통합 엔진 paper 모드 구현

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-UNIFIED-ENGINE-REVIEW-002-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-UNIFIED-ENGINE-REVIEW-002-20260301.md
- 커밋: (push 후 기재)
- HTTP 확인: (push 후 기재)
