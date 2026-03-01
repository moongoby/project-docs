# CUR-V41-CTE-PIPELINE-INTEGRATE-001

> **Cursor #17 CTE 파이프라인 통합 + D7 갭다운 핫픽스**
> 작성일: 2026-03-01 | 작성자: Claude Opus 4.6

---

[인계 확인]
직전 완료: CUR-V41-PAPER-D6D7-WEEK1-001, CUR-V41-CTE-FULLBACKTEST-CEO-REPORT-001
현재 단계: Phase B — CTE 파이프라인 통합 + 파라미터 교정
CEO 지시 적용: D-001, D-002, D-003, D-010, D-011
strategy_cards: 36
open_positions: 14

---

## 1. 작업 요약

### 1-1. D7 갭다운 핫픽스 (Task 1)

**파일**: `/root/kis-autotrade-v4/scripts/live_paper_d6_d7.py`

| 항목 | 변경 전 | 변경 후 | 근거 |
|------|---------|---------|------|
| 종가위치 임계값 | `close_pos < 0.70` | `close_pos < 0.80` | EXIT-SLIPPAGE-INTEGRATE-001 확정 |
| 거래대금 필터 | Top15 (`all_ranks[:15]`) | Top10 (`all_ranks[:10]`) | EXIT-SLIPPAGE-INTEGRATE-001 확정 |
| DB 카드 #43 | `≥0.70 + Top15` | `≥0.80 + Top10` | 갭다운 43.4%→24.1% |

**검증 결과**:
- `python -c "import scripts.live_paper_d6_d7"` — 구문 오류 없음 ✅
- DB `go100_strategy_cards` #43 entry_condition 갱신 확인 ✅
- 03-02(월) 08:50 KST 전 완료 ✅

### 1-2. CTE 파이프라인 통합 (Task 2)

#### 생성 파일

| 파일 | 크기 | 설명 |
|------|------|------|
| `backend/app/services/trading/cte/strategy_params.py` | 신규 | 전략별 교정 파라미터, 신호 프리셋, 버킷 규칙 |
| `backend/app/services/trading/cte/test_cte_pipeline.py` | 신규 | 통합 테스트 33케이스 |

#### 기존 파일 (이미 #17~#19에서 완성)

| 파일 | 상태 | 설명 |
|------|------|------|
| `cte_pipeline.py` | 유지 | 6-Layer 파이프라인 (CS L3.5 + EQS L4.5) |
| 그 외 9개 CTE 모듈 | 유지 | bounce_gate, pullback_classifier, confirmation_signals, dd_decelerator, risk_layer_manager, disaster_detector, trigger_tactic_matrix, conviction_score, execution_quality_score |

---

## 2. #25 Sharpe 분석 교정 반영

### 2-1. D2 avg_win 교정

| 항목 | 이전(오류) | 교정(실측) | 출처 |
|------|-----------|-----------|------|
| avg_win | 1.2% | **3.36%** | VE-003-PHASE-B 1,038건 |
| avg_loss | 1.41% | 1.41% (동일) | |
| win_rate | 39.79% | 39.79% (동일) | |
| EV/거래 | **-0.43%** | **+0.49%** | 교정 핵심 |

```
교정 EV = 0.3979 × 3.36% − 0.6021 × 1.41% = +0.488% ≈ +0.49%
```

### 2-2. 동시보유 한도 교정

| 항목 | 이전 | 교정 | 조건 |
|------|------|------|------|
| concurrent | 3 | **5** | D2 EV > 0 전제 |
| 용량 활용 | 49.9% | ~83% | CROSS-RELAY-PRESIM-001 |

### 2-3. 최적 신호 조합 (비용 차감 후)

| 전략 | 신호 | min | PF_net | 연간 거래 |
|------|------|-----|--------|----------|
| D2 | SIG3+SIG6+SIG7 | 2/3 | **8.92** | ~820 |
| D4 | SIG5+SIG6 | 2/2 | **6.80** | ~2,070 |
| D5 | SIG3+SIG6+SIG8 | 2/3 | **14.60** | ~133 |
| D6 | (EOD) | — | 9.96 | ~36 |
| D7 | (EOD) | — | 2.10 | ~380 |
| S1 | SIG1+SIG3+SIG6 | 2/3 | 5.81 | ~400 |

### 2-4. B4/B6 진입금지

| 버킷 | PF_net_ac | 판정 |
|------|-----------|------|
| B1 (0-1%) | 6.758 | Core ✅ |
| B2 (1-2%) | 3.485 | Core ✅ |
| B3 (2-3%) | 1.825 | Conditional ⚠️ |
| B4 (3-5%) | **0.986** | **FORBIDDEN** ❌ |
| B6 (5%+) | **0.527** | **FORBIDDEN** ❌ |

---

## 3. strategy_params.py 상세

### 핵심 데이터 클래스

```python
# StrategyStats: 전략별 실측 통계 + EV 자동 계산
d2 = STRATEGY_STATS["D2"]
d2.ev_per_trade   # +0.49% (교정 후)
d2.is_positive_ev # True

# SignalPreset: 전략별 최적 신호 조합
SIGNAL_PRESETS["D2"].pf_net  # 8.92

# 진입 금지 버킷
FORBIDDEN_BUCKETS  # {B4, B6}

# 동시보유 한도
CONCURRENT_LIMIT  # 5

# PF우선 슬롯 배정
STRATEGY_PRIORITY_ORDER  # D6 > D5 > D4 > D7 > D2 > S1
```

### D2 v2.0 교정 파라미터

```python
D2_PARAMS = D2Params(
    rsi_range=(30, 50),
    entry_priority=(B2, B1, B3),  # B4/B6 제외
    signals=(SIG3, SIG6, SIG7),
    trailing_start_pct=5.0,
    trailing_retrace_pct=20.0,
    stop_loss_pct=-3.0,
    timeout_min=60,
    order_type="limit_-1tick",
)
```

---

## 4. 통합 테스트 결과

```
33 passed in 0.13s
```

| 테스트 클래스 | 케이스 | 검증 내용 |
|--------------|--------|----------|
| TestD2EVCorrection | 4 | avg_win 3.36%, EV +0.49%, 이전 음수 확인, 전략 등록 |
| TestForbiddenMatrix | 3 | 금지 18셀+, FORBIDDEN 차단, OPTIMAL 비차단 |
| TestConcurrentLimit | 4 | 한도=5, 5개시 차단, 6+차단, 4이하 통과 |
| TestCSGate | 2 | CS<50 BLOCKED, CS≥65 FULL |
| TestEQSGate | 3 | LAG1=62, 저점수 REJECT, 고점수 PROCEED |
| TestBucketForbidden | 6 | B4/B6 금지, B1/B2/B3 허용, 2개 정확 |
| TestPriorityDedup | 2 | D6 후 D7 차단, 우선순위 1>2>3 |
| TestSignalCombo | 4 | D2/D5 신호 확인, EOD 불필요, 프리셋 정의 |
| TestD2SmokePositiveEV | 2 | 100건 EV>0, 비용후 viable |
| TestPipelineEndToEnd | 3 | 승인→양수배수, 차단→0배수, 시장정지 |
| **합계** | **33** | **전체 PASS** |

---

## 5. PASS 기준 충족 확인

| 기준 | 결과 | 상태 |
|------|------|------|
| 통합 테스트 전체 PASS | 33/33 PASS | ✅ |
| D2 100건 스모크 EV>0 | EV = +0.49%/거래 | ✅ |
| 금지 18셀 진입 0건 | FORBIDDEN → PRE_MATRIX 차단 | ✅ |
| D7 종가위치 ≥0.80 | 코드 + DB #43 갱신 | ✅ |
| D7 거래대금 Top10 | 코드 갱신 | ✅ |

---

## 6. 수정 파일 목록

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `scripts/live_paper_d6_d7.py` | 수정 | D7 종가위치 0.80, Top10 |
| `backend/app/services/trading/cte/strategy_params.py` | **신규** | 전략별 교정 파라미터 |
| `backend/app/services/trading/cte/test_cte_pipeline.py` | **신규** | 통합 테스트 33케이스 |
| DB `go100_strategy_cards` #43 | 갱신 | entry_condition 0.80+Top10 |

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-CTE-PIPELINE-INTEGRATE-001-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-CTE-PIPELINE-INTEGRATE-001-20260301.md
- 커밋: {SHA}
- HTTP 확인: {확인예정}
- HANDOVER 업데이트: {완료예정}
