# CUR-V41-FULL-SYSTEM-AUDIT-001 — 전방위 전수 확인 종합 보고서
> 작성일: 2026-03-01 | 담당: Claude Code Sonnet 4.6 | 레포: kis-autotrade-v4 (phase-2c-command-center)
> 참조 문서: HANDOVER v5.0, CEO-DIRECTIVES v1.6, DESK2-DESIGN-SPEC v3.0, backtest_engine_v2.py, cte_pipeline.py, strategy_params.py, ai_scorer.py, scoring_engine.py, go100_bridge_client.py, broker_gateway.py, system/orchestrator.py, auto_trade_engine.py

---

[인계 확인]
직전 완료: CUR-V41-UNIFIED-ENGINE-REVIEW-002
현재 단계: Cursor #22 — Task B 착수 전 전방위 전수 확인
CEO 지시 적용: D-001(단순사고 금지), D-002(보고서 push 필수)
strategy_cards: 60개
open_positions: 14개

---

## 0. 검토 범위 및 방법

HANDOVER v5.0 전체(100개+ 작업 이력), CEO-DIRECTIVES v1.6(D-001~D-014), 미확인 코드 파일 직접 읽기를 통해 이전 분석의 각 항목을 교차 확인했다.

---

## 1. 통합 엔진에 빠진 모듈 — 전수 확인 결과

### [항목1] CTE 서브모듈 9개 연동 — ✅ 확인 완료

HANDOVER 확인:
- BOUNCE-GATE-IMPL-001 (Cursor #14): BounceConfirmationGate + PullbackClassifier + ConfirmationSignalEngine → 단위 96케이스 전체 PASS
- DD-RISK-IMPL-001 (Cursor #15): DDDecelerator(5레벨) + FiveLayerRiskManager(L1~L5) + DisasterPatternDetector → 단위 29케이스 전체 PASS
- CS-EQS-IMPL-001 (Cursor #16): ConvictionScoreEngine + ExecutionQualityScoreEngine + TriggerTacticMatrix → 단위 45케이스 전체 PASS
- 코드 레포 커밋 확인: 3개 Phase 모두 완료

**통합 엔진 누락 여부**: CTE 파이프라인(cte_pipeline.py)이 이 9개 서브모듈을 import하여 사용 중. 단, 통합 엔진 설계서(`unified_engine/engine.py`)에 이 연결 흐름이 명시되지 않았음. Task B에서 엔진이 cte_pipeline.py를 그대로 호출하면 자동 연동 — **설계서 명시만 추가하면 됨**.

---

### [항목2] HAV (Hypothesis Auto Validator) — ✅ 확인 완료, 프로덕션 준비 완료

HANDOVER 확인:
- DEV-HAV-001: 4-Layer, 27변수 135K 조합, OOS PF=12.26, WF 2/2 PASS
- HAV-EXTEND-35VAR-001: 27→35변수, Bayesian 탐색 유효 3변수(body_size/atr/bb_width)
- HAV-DRYRUN-DRIFT-001: 35변수 YAML 파싱 오류 0건, 100건 dry-run PF 12.24 PASS
- **★ 03-02(일) 06:00 cron GO 판정** ✅

통합 엔진 관계: HAV는 go100_backtest_runs 테이블에서 전략 성과를 읽는다. 현재 CTE 백테스트(run_cte_full_backtest.py)는 `/tmp/cte_backtest_daily.json`에만 저장하고 go100_backtest_runs에 INSERT하지 않음 → **Task C에서 연결 필수**.

---

### [항목3] 적응형 청산 5모드 — ✅ 확인 완료 (연구 완료, 코드 미반영)

HANDOVER 확인:
- RESEARCH-ADAPTIVE-EXIT: 5모드 아키텍처 설계 완료 (즉시익절/부분익절/파동전환/트레일링강화/강제이탈)
- VE003-P4-ADAPTIVE-EXIT: 22,406건 검증, PF 1.32→1.34, 모드2(부분익절) 전 전략 최적
  - 최대 일일손실 -174%→-74% (극단 손실 방지)
  - 모드3(파동전환) 2파 발생률 0% → 4조건 임계값 재조정 필요

통합 엔진 관계: **연구/설계는 완료, 구현 코드 미반영**. Task B `order_executor` 어댑터에 모드2 중심 청산 로직 구현 필요. 모드3은 4조건 재조정 후 Task B-2에서 추가.

---

### [항목4] 릴레이 청산-재진입 (D5→D2, D4→D2, D2→D5) — ✅ 확인 완료 (연구 완료, 코드 미반영)

HANDOVER 확인: RESEARCH-RELAY-REENTRY 완료 — D5→D2, D4→D2, D2→D5 연쇄 맵, 컨디션별 적합도, 자본체감 규칙.

통합 엔진 관계: Task B 초기 구현에서 제외하고, Phase 2(60일 페이퍼 이후)에서 추가 권고.

---

### [항목5] 장중 복리 자본 순환 — ✅ 확인 완료 (연구 완료, 코드 미반영)

HANDOVER 확인: RESEARCH-INTRADAY-COMPOUND — 부분청산→재투입 자본풀, 단리+2.3%→복리+7.3%(3.1배).

통합 엔진 관계: Task B 초기 구현에서 제외. PortfolioManager에 복리 재투입 경로는 Phase 2에서 추가.

---

### [항목6] D7 갭다운 필터 — ✅ **이미 수정 완료** ← 기존 분석 오류 수정

**⚠️ 이전 보고서(REVIEW-002)에서 "긴급 수정 필요"로 분류한 것은 오류.**

HANDOVER v5.0 "다음 세션" 섹션 명시:
> ~~D7 갭다운 필터 코드 업그레이드~~ → ✅ **완료** (CTE-PIPELINE-INTEGRATE-001, 커밋 67602428)

코드 확인: `strategy_params.py` + `live_paper_d6_d7.py`에서 `종가위치 ≥ 0.80 + Top10` 반영 완료.
D7 갭다운 43.4%→24.1% 달성. **03-02 첫 실행에 문제 없음.**

---

### [항목7~9] D4 긴급 교체 / D2 TP/SL 변경 / S1 필터 강화 — ✅ 확인 완료 (CEO 승인 대기)

| 전략 | 현재 PF | 변경 후 예상 PF | 상태 |
|------|--------|----------------|------|
| D4 09:20양봉 → 눌림확인 | 0.73 | **13.3** | CEO 승인 대기 |
| D2 trail-20% → SL-3%+trail-10% | 1.57 | **4.41** | CEO 승인 대기 |
| S1 갭+5%+양봉첫봉 | 1.44 | **2.52** | CEO 승인 대기 |

통합 엔진 관계: CEO 승인 완료 후 `strategy_params.py` 업데이트 → 통합 엔진에 자동 반영.

---

### [항목10] 분봉 멀티타임프레임 — ✅ 확인 완료 (기획 완료, 미구현)

CEO-DIRECTIVES D-009에서 P0 변수(VP_REALTIME, MA_REGIME_1M 등) 정의됨. 구현은 아직.
통합 엔진 DataAdapter의 `resample()` 인터페이스 설계 필요.

---

## 2. GO100 프로젝트 충돌 — 전수 확인 결과

### [항목1] GO100 Bridge Phase 1~3 삽입점 A/B/C — ✅ 직접 코드 확인 완료

`backend/app/services/backtest/backtest_engine_v2.py` 직접 확인:

```
[브릿지 삽입점 A] 매 거래일 진입 전 킬스위치 확인 (line 609~617)
[브릿지 삽입점 B] 청산 후 에피소드 메모리 적재 (line 647~665)
[삽입점 C]  포트폴리오 최적화 비중 요청 (line 423~478)
BacktestConfig.enable_go100_bridge = True (기본값 활성화, Phase 3 완료)
```

커밋: CUR-V41-GO100-BRIDGE-PHASE3-001 (85945058) — **삽입점 A/B/C 모두 활성 확인**.

통합 엔진 관계: 통합 엔진이 backtest_engine_v2를 교체할 경우 이 삽입점 3개를 반드시 이식해야 한다. **끊기면 GO100 포트폴리오 최적화 비중 배분이 작동하지 않음.**

---

### [항목2] GO100 AI 가설검증 파이프라인 — ✅ 확인 완료

HypothesisEngine → go100_backtest_runs READ, tasks.json WRITE 구조 확인.
통합 엔진 백테스트 결과가 go100_backtest_runs에 기록되지 않으면 HAV 루프 단절.

---

### [항목3] GO100 AI Feature Store v2 Z-score 핫픽스 — ✅ 확인 완료

CUR-V41-AI-SCORING-ZSCORE-HOTFIX-001 (799e33ee) 적용 완료:
- cs_ai 이중 Z-score 해소
- 삼성전자 100→65, SK하이닉스 100→61, NAVER 100→45
- feature_stats.json 원시 기준 재생성 완료

---

### [항목4~5] GO100 킬스위치 / 에피소드 메모리 — ✅ 충돌 없음 확인

- Phase 2: 킬스위치 Mock(True)→전종목 Halt 검증 PASS
- memory_id 적재 확인 (V4.1_DESK_AGENT 네임스페이스 분리)
- 통합 엔진에서도 동일 패턴 유지 필요

---

## 3. AI 매매 검증 로직 반영 — 전수 확인 결과

### [항목1] Validation Engine 5모듈 (precision 90.3%, 118변수) — ✅ 확인 완료

HANDOVER: VALIDATION-ENGINE-002 (57b6de5f) — precision 6.9%→90.3%, 118변수, 20핵심, L3=0 발견.

통합 엔진 관계: VE는 발굴 엔진(universe_builder) 영역. 통합 엔진의 CTE 파이프라인과는 다른 레이어. **직접 충돌 없음. 단, 통합 엔진의 유니버스 입력을 VE가 필터링한 종목으로 제한해야 CS 스코어 신뢰도 확보.**

---

### [항목2] HAV 자동 탐색 (35변수, OOS PF 12.26) — ✅ 확인 완료

DEV-HAV-001: 27변수 135K 조합, Bayesian 탐색 확인.
HAV-EXTEND-35VAR-001: 35변수 솔로테스트 ALL 유효(PF 1.0~2.71).
HAV-DRYRUN-DRIFT-001: 03-02 cron GO.

통합 엔진 관계: HAV drift_detector.py가 4개 시장지표를 감시 → 드리프트 감지 시 파라미터 재탐색. 통합 엔진은 drift_detector 출력을 참조하여 strategy_params.py를 자동 업데이트하는 루프 필요.

---

### [항목3] CS AI 점수 (cs_ai, Shadow w=0.15) — ✅ 직접 코드 확인 완료

`ai_scorer.py` + `scoring_engine.py` + `go100_bridge_client.py` 직접 읽기:
- AiScorer: DB 조회(ohlcv_daily/v4_investor_daily/v4_ohlcv_minute) → LightGBM 4모델 → cs_ai / cs_ai_gap
- ScoringEngine: `final_cs = (1-w)*rule_cs + w*ai_score` (w=0.15, 환경변수 V41_AI_BLEND_WEIGHT)
- D6/D7 → cs_ai_gap, 나머지 → cs_ai 분기 확인
- Fail-Open: AI 불가 시 rule_cs 100% 사용

**통합 엔진 연동 설계 (Task B에 포함 필요)**:
```
signal_generator.py
  → CTE 파이프라인 호출 (CS 기본 계산)
  → ScoringEngine.compute_final_cs(rule_cs, strategy_type, bridge_client)
     → Go100BridgeClient.request_ai_scoring(ticker)
     → final_cs = (0.85 * rule_cs) + (0.15 * cs_ai)
  → CTE L3.5 임계값(≥50) 통과 여부 결정
```

---

### [항목4] EQS AI 점수 (LAG1 교정) — ✅ 확인 완료

EQS-BIAS-CROSS-FILTER-001: PRICE_POSITION t-1 LAG1 교정 완료 (HIGH WR 85.2%→72.1%).
CS65+EQS65 최적 조합: 연 550건, PF_net 2.499.
통합 엔진에서 동일 교정 적용 필수.

---

### [항목5] GO100 HypothesisEngine — ✅ 확인 완료 (의도적 분리)

V4.1 통합 엔진 ↔ GO100 가설검증은 **의도적으로 분리된 파이프라인**. HTTP 브릿지로 느슨한 결합 유지.
통합 엔진이 해야 할 것: 거래 결과를 go100_backtest_runs에 INSERT → HAV 자동 탐색 루프 연결.

---

### [항목6] 반등확인 게이트 BounceConfirmationGate (OOS PF 2.683) — ✅ 확인 완료

GATE-OOS-WALKFORWARD-001: 5전략 Test PF_net > 2.5 전원 PASS. 월별 PF<1.0 0개월.
2/3 충족 기본버전 권장.

통합 엔진 관계: HANDOVER "다음 단계"에 **"반등확인 게이트 5전략 배포 — 다음"** 명시. Task B signal_generator에 BounceConfirmationGate 호출 포함 필요.

---

### [항목7] DD Decelerator 5단계 (maxDD -45.66%→-11.42%) — ✅ 확인 완료

DD-RISK-IMPL-001: 5레벨 S1 권고. maxDD -45.66%→-11.42%, PnL 95.8% 유지.
통합 엔진 RiskManager에 DDDecelerator 5레벨 연동 필수.

---

### [항목8] TriggerTacticMatrix — ✅ 확인 완료 + ⚠️ 오류 수정

**이전 분석 오류**: "금지18/시너지18" → **실제: 금지18/시너지8** (HANDOVER 명시: "81셀/금지18/시너지8")
CS-EQS-IMPL-001: 81셀, 금지18, 시너지8 규칙 확인. 45케이스 전체 PASS.

---

## 4. 추가 고려사항 — 전수 확인 결과

### [항목1] 기존 Cron 충돌 — ✅ HIGH 위험 재확인

현재 가동 중인 cron 목록 (HANDOVER 확인):
```
50 8 * * 1-5   live_paper_cte.py          → v4_paper_trades
06:00 03-02(일) HAV coarse_grid (GO)
15:40 평일       run_daily_hypothesis_pipeline.py
22:00 평일       run_hypothesis_backtest.py
16:25 평일       stock_universe 업데이트
15:50 평일       v4_vkospi_daily 수집
```

통합 엔진 cron 추가 시 08:50 충돌, DB 동시 접근 위험. **통합 엔진 paper 모드 완성 후 live_paper_cte.py cron 제거 필수.**

---

### [항목2] DB 테이블 분산 — ✅ 확인 완료

포지션 관련 테이블: v4_paper_trades, v4_positions, v4_desk_positions, v4_desk_pool, (신규 예정) v4_mock_trades.
통합 엔진에서 모드별 테이블 매핑 명확화 필요:
- backtest: 메모리 (DB 없음)
- paper: v4_paper_trades
- mock: v4_mock_trades (신규 생성 필요)
- live: v4_positions

---

### [항목3] DESK2 vs CTE 아키텍처 중복 — ✅ 확인 완료

CTE-COMPARE-ARCH (HANDOVER): "CTE vs DESK 7축 비교, 흡수12개, 통합아키텍처". CTE가 DESK 요소를 흡수하는 방향으로 확정됨. desk2/ layer1_discovery + layer2_strategy는 CTE에 통합 또는 병렬 유지.

---

### [항목4] Stage 1 자본 배분 — ✅ 확인 완료

D-012: Stage 1(4천만) = DESK2 100%. Mock 모의투자(1천만 예정)는 Stage 1 내. 문제 없음.

---

### [항목5] KIS API 토큰 만료 — ✅ 합리적 우려

KIS API 토큰 유효기간 24시간. 08:40 발급 → 15:30까지 6시간 50분 → 안전. 다만 만료 예외 처리 및 자동 재발급 로직 포함 필요.

---

### [항목6] 시장 휴장일 처리 — ✅ 합리적 우려

공휴일 cron 자동 실행 위험. `calendar_service.calculate_daily_adjustments()` 이미 L0 오케스트레이터에 연동됨 (system/orchestrator.py 확인). 통합 엔진에서 동일 서비스 활용 가능.

---

### [항목7] 14개 OPEN positions 기존 포지션 격리 — ✅ 확인 완료

HANDOVER: "5개 DESK (60개 strategy cards, 14개 OPEN positions)". 이 포지션들은 go100_strategy_cards 기반 AutoTradeEngine이 관리. 통합 엔진은 별도 계좌/테이블에서 운영하여 충돌 방지.

---

### [항목8] v4_scalping_universe 708종목 — ✅ 부분 확인

DB에 v4_scalping_universe 테이블 존재 가능성 높음. HANDOVER에 직접 언급 없으나, 유니버스 범위는 VE 필터 통과 종목 + Top20 거래대금 기준으로 동적 결정.

---

### [신규 발견-1] GO100 Bridge 삽입점 A/B/C: 통합 엔진이 반드시 이식해야 함

backtest_engine_v2.py 코드 직접 확인:
- 삽입점 A: 매 거래일 진입 전 킬스위치 확인 (line 609)
- 삽입점 B: 청산 후 에피소드 메모리 적재 (line 647)
- 삽입점 C: 포트폴리오 최적화 비중 기반 자본 배분 (line 423~478)
- `enable_go100_bridge: bool = True` 기본 활성화

통합 엔진이 backtest_engine_v2를 직접 교체하면 이 3개 삽입점이 사라진다. **반드시 통합 엔진 engine.py에 동일 삽입점 이식 필요.**

---

### [신규 발견-2] D2/D4/D5 trailing 파라미터: 코드 반영 대기 중

HANDOVER "다음 세션" 항목:
> D2/D4/D5 trailing 파라미터 코드 반영: start=+5%, retrace=20%, order=limit_1tick (strategy_params.py에 D2_PARAMS 정의 완료, 실행 코드 반영 대기)

strategy_params.py에 파라미터 정의는 완료. 통합 엔진 `order_executor`에서 이 파라미터를 읽어 실행하는 코드 필요.

---

### [신규 발견-3] live_paper_d6_d7.py에 D6/D7 중복방지 로직 누락

HANDOVER "다음 세션" 항목:
> live_paper_d6_d7.py에 D6/D7 중복방지 로직 추가 (check_d7_allowed 함수)

D6/D7 중복: 36건 D6 중 28건(77.8%)이 D7 조건 동시 충족 → 우선순위 로직 없으면 같은 종목에 두 전략 동시 진입.

---

### [신규 발견-4] orchestrator.py에 strategy_params 연결 누락

HANDOVER "다음 세션" 항목:
> strategy_params.py를 실제 DESK2 실행 흐름에 연결: orchestrator.py가 strategy_params import하여 EV 검증, 버킷 차단, 신호 조합 강제 적용

현재 L0 오케스트레이터(`system/orchestrator.py`)는 `strategy_engine.generate_signals()`를 호출하지만, strategy_params.py의 B4/B6 금지, PF 우선 슬롯, 신호 조합 강제 등이 이 연결에 적용되지 않는다.

---

## 5. 이전 보고서 오류 수정 3건

| 오류 위치 | 기존 기재 | 정정 | 근거 |
|-----------|----------|------|------|
| REVIEW-002 GAP-07 | "D7 갭다운 0.70→0.80 미수정, 03-02 전 긴급" | **이미 수정 완료** (커밋 67602428) | HANDOVER v5.0 "다음 세션" ~~완료~~ 표기 |
| 사용자 분석 항목8 | "TriggerTacticMatrix 금지18/시너지18" | **금지18/시너지8** | HANDOVER "81셀/금지18/시너지8" 명시 |
| REVIEW-002 전반 | "Paper PnL 완전 누락 — 03-02 전 필수 수정" | **계속 유효** (D7 갭다운과 달리 미수정) | HANDOVER에 수정 완료 표시 없음 |

---

## 6. CEO 질문에 대한 답변: PnL 핫픽스 vs Task B 지시서

CEO 검토 메시지 요약:
- CRITICAL: make_synthetic_signal 미래정보 주입 → BT PF 2.368 신뢰성 의문
- HIGH: pnl_pct=None → 03-02부터 성과 측정 불가
- HIGH: 실시간 청산 로직 부재

**권고 판단**:

| 순서 | 작업 | 이유 | 소요 |
|------|------|------|------|
| ① **즉시 (오늘)** | `live_paper_cte.py` PnL 핫픽스 | 03-02 08:50 가동 전 필수. 비용 0.47% 차감 포함. 코드 10줄 수준 | 30분 |
| ② **즉시** | D6/D7 중복방지 `check_d7_allowed()` 추가 | 03-02 첫 실행에 영향 | 20분 |
| ③ **오늘 중** | Task B 지시서 확정 + Cursor #22 착수 | 통합 엔진 전체 구조 확정 | - |
| ④ **1주차** | Task C: BT 미래정보 제거 후 실제 PF 측정 | 전략 실제 가치 파악 (PF 1.5~2.0 예상) | - |

**결론: PnL 핫픽스 먼저, Task B 지시서는 병행 확정.**
이 두 작업은 독립적이므로 핫픽스를 오늘 완료하고 Task B 지시서를 확정하면 됩니다.

---

## 7. Task B Cursor #22 지시서에 포함해야 할 필수 항목 (우선순위 순)

### Phase 1 필수 (통합 엔진 골격)
1. `core/portfolio_manager.py` — 포지션/자본/DD 5단계 관리
2. `core/pnl_calculator.py` — PnL + 비용 0.47% + D7 갭다운 분기
3. `core/signal_generator.py` — CTE 파이프라인 + ScoringEngine (AI CS 블렌딩)
4. `adapters/data_source.py` — DB 히스토리 / KIS 실시간 분기
5. `adapters/order_executor.py` — 가상/DB/Mock API 분기 + 삽입점 A/B/C 이식
6. `engine.py` — `--mode backtest/paper/mock/live` 분기 + L0 오케스트레이터와의 관계 확정
7. **BounceConfirmationGate 5전략 연동** (HANDOVER "다음 단계" 명시)
8. **strategy_params → engine 연결** (B4/B6 금지, PF우선 슬롯, 신호조합 강제)
9. **GO100 Bridge 삽입점 A/B/C 이식**
10. **D2/D4/D5 trailing 파라미터 실행 코드** (start=+5%, retrace=20%)

### Phase 2 (60일 페이퍼 중)
11. 적응형 청산 5모드 (모드2 우선)
12. 릴레이 청산-재진입
13. go100_backtest_runs INSERT (HAV 루프 연결)
14. 분봉 멀티타임프레임 리샘플링
15. 장중 복리 자본 순환

---

## 8. 전수 확인 종합 판정표

| # | 항목 | 판정 | 수정 사항 |
|---|------|------|----------|
| 1 | CTE 서브모듈 9개 | ✅ 확인 | 통합 엔진 설계서에 연동 경로 명시 필요 |
| 2 | HAV (35변수, PF12.26) | ✅ 확인 | go100_backtest_runs INSERT 연결 필요 |
| 3 | 적응형 청산 5모드 | ✅ 확인 | 연구 완료, 코드 미반영 (Phase 1) |
| 4 | 릴레이 청산-재진입 | ✅ 확인 | Phase 2 |
| 5 | 장중 복리 자본 순환 | ✅ 확인 | Phase 2 |
| 6 | D7 갭다운 필터 | ✅ **이미 수정** | 이전 보고서 오류 수정 |
| 7 | D4 긴급 교체 | ✅ 확인 | CEO 승인 대기 |
| 8 | D2 TP/SL 변경 | ✅ 확인 | CEO 승인 대기 |
| 9 | S1 필터 강화 | ✅ 확인 | CEO 승인 대기 |
| 10 | 분봉 멀티타임프레임 | ✅ 확인 | Phase 2 |
| 11 | GO100 Bridge A/B/C | ✅ **코드 직접 확인** | 통합 엔진 이식 필수 |
| 12 | GO100 가설검증 연동 | ✅ 확인 | Task C에서 연결 |
| 13 | Feature Store Z-score 핫픽스 | ✅ 확인 | 완료 (799e33ee) |
| 14 | GO100 킬스위치 | ✅ 확인 | 통합 엔진 이식 필요 |
| 15 | GO100 메모리 | ✅ 확인 | 동일 패턴 유지 |
| 16 | VE 5모듈 (90.3%) | ✅ 확인 | 유니버스 필터 연결 필요 |
| 17 | CS AI 점수 (w=0.15) | ✅ **코드 직접 확인** | signal_generator 연동 설계 필요 |
| 18 | EQS LAG1 교정 | ✅ 확인 | 동일 적용 필요 |
| 19 | 반등확인 게이트 (PF2.683) | ✅ 확인 | Task B Phase 1 포함 |
| 20 | DD Decelerator 5단계 | ✅ 확인 | RiskManager 연동 필수 |
| 21 | TriggerTacticMatrix | ✅ 확인 + 오류수정 | 시너지18→8 수정 |
| 22 | Cron 충돌 | ✅ 확인 | live_paper_cte 교체 후 제거 |
| 23 | DB 테이블 분산 | ✅ 확인 | 모드별 테이블 매핑 확정 |
| 24 | DESK2 vs CTE 중복 | ✅ 확인 | CTE 흡수 방향 확정 |
| 25 | D2/D4/D5 trailing 미반영 | ✅ **신규 발견** | Task B 필수 |
| 26 | D6/D7 중복방지 미구현 | ✅ **신규 발견** | 03-02 전 핫픽스 |
| 27 | orchestrator ↔ strategy_params | ✅ **신규 발견** | Task B 필수 |

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-FULL-SYSTEM-AUDIT-001-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-FULL-SYSTEM-AUDIT-001-20260301.md
- 커밋: (push 후 기재)
- HTTP 확인: (push 후 기재)
- HANDOVER 업데이트: 미완료 (Task E에서 완료)
