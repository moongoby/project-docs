# CUR-V41-SESSION-E3-SUPPLY-GATE-VALIDATION-001

> **Session E-3: 수급 게이트 다층 검증 + L3.3 SupplyDemandGate 구현**
> 날짜: 2026-03-02
> 선행: CUR-V41-SESSION-E2B-SUPPLY-DEMAND-001 (CEO 승인 3건 전체)
> 상태: **COMPLETE**

---

## 0. 세션 목표

CEO가 E-2B 보고서의 3가지 권고사항을 전부 승인:
1. **L3.3 SupplyDemandGate 신설** (CLOSE_POSITION_5D > 0.7 + FRGN_CUMUL_5D > 0)
2. **외인 > 기관 가중** (외인 5일 누적 MUST, 기관은 보너스)
3. **소형주 수급 데이터 확대** (Phase 2에서 처리)

본 세션: 권고 ①②를 다층 검증 → Walk-Forward 확정 → 코드 구현 + 통합 테스트

---

## 1. Phase 1: 다층 검증 (Tasks 1–6)

### Task 1: 시장 레짐 교차 검증

| 레짐 | 필터 | N | PF | WR |
|------|------|---:|----:|----:|
| BULL | 무필터 | 786 | 0.689 | 33.6% |
| BULL | CLOSE>0.7 | 531 | **1.591** | 41.1% |
| BULL | CLOSE>0.8 | 396 | **2.505** | 44.7% |
| FLAT | 무필터 | 704 | 0.871 | 35.1% |
| FLAT | CLOSE>0.7 | 487 | **2.017** | 42.5% |
| FLAT | CLOSE>0.8 | 376 | **3.061** | 47.1% |
| BEAR | 무필터 | 439 | 0.992 | 34.2% |
| BEAR | CLOSE>0.7 | 284 | **2.549** | 43.7% |
| BEAR | CLOSE>0.8 | 221 | **3.721** | 47.5% |

**핵심 발견**: BEAR 레짐이 오히려 **가장 높은 PF(2.549)** → 수급 필터가 약세장 노이즈를 가장 효과적으로 제거. 레짐별 임계값 차별화 불필요 (전 레짐 동일 threshold 적용).

레짐 전환 횟수: 45회 (242거래일 기간)

### Task 2: 눌림-반등 시퀀스 분석

수급 궤적(TRAJECTORY)의 4분기별 위상 매칭:

| 위상수 | N | PF | WR |
|-------:|---:|----:|----:|
| 0단계 | 20 | 0.795 | 30.0% |
| 1단계 | 327 | 0.510 | 26.6% |
| 2단계 | 872 | 0.704 | 31.4% |
| 3단계 | 564 | **1.029** | 42.0% |
| 4단계 (완전패턴) | 102 | **1.364** | 42.2% |

**핵심 발견**: 4/4 분기 모두 수급 증가하는 "완전패턴"만 PF>1.3. 3단계부터 PF>1.0 달성.

### Task 3: MFE/MAE 분포 비교

| 필터 | N | MFE5% | MAE중간 | W/L비율 | Top10기여 |
|------|---:|------:|--------:|--------:|----------:|
| 전체 | 1,929 | 13.3% | -0.95% | 1.60 | 81.7% |
| CLOSE>0.7 | 1,302 | **15.8%** | **-0.66%** | **2.73** | 76.6% |
| FRGN>0 | 579 | 12.3% | -0.80% | 1.97 | 73.1% |
| TRAJ≥3 | 368 | 14.4% | -0.80% | 2.19 | 69.8% |

**핵심 발견**: CLOSE>0.7 필터 적용 시:
- W/L 비율 1.60 → **2.73** (+70.6% 개선)
- MAE 중간값 -0.95% → **-0.66%** (손실 30% 감소)
- Top10 기여도 81.7% → 76.6% (수익 분산 개선)

### Task 4: 신고가 + 수급 조합

| 구간 | N | PF | WR |
|------|---:|----:|----:|
| CLOSE >= 1.0 (신고가) | 257 | **13.483** | 54.1% |
| 0.7 ~ 0.99 | 1,046 | 0.707 | 39.2% |
| < 0.7 | 626 | 0.119 | 17.9% |

**극단 발견**: 5일 신고가(CLOSE_POS ≥ 1.0) → PF = **13.483** (257건)
신고가 + 외인매수(FRGN>0) 조합 시 → PF = **27.855** (41건, 추정)

### Task 5: 외국인 장기 추적

외국인 연속매수 4일 이상 종목의 20일 후 수익률:
- 평균: **+9.89%**
- 중간값: +4.99%
- 양수 비율: **70.4%**
- +10% 이상: 38.4%
- +30% 이상: 8.0%

### Task 6: 프랙탈 타임프레임 분석

| 윈도우 | CLOSE_POS AUC | FRGN_CUMUL AUC |
|-------:|-------------:|---------------:|
| **5일** | **0.680** | **0.583** |
| 10일 | 0.666 | 0.575 |
| 20일 | 0.654 | 0.543 |
| 60일 | 0.631 | 0.546 |

**핵심 발견**: 5일 타임프레임이 DESK2 단기매매에 최적 (AUC = 0.680). 장기 윈도우로 갈수록 AUC 감소.

---

## 2. Phase 2: Walk-Forward 3-Fold 검증 (Task 7)

### 2.1 검증 설계
- 3-Fold 시간순 분할 (80거래일 × 3)
- 16가지 조합: Threshold {0.5, 0.6, 0.7, 0.8} × FRGN {On, Off} × TRAJ {On, Off}
- PASS 기준: 3-Fold 전부 Test PF > 1.0 + OOS Decay < 50%

### 2.2 PASS 조합 (13/16)

| Threshold | FRGN | TRAJ | Fold1 PF | Fold2 PF | Fold3 PF | Avg PF | Min PF |
|----------:|-----:|-----:|---------:|---------:|---------:|-------:|-------:|
| 0.5 | Off | On | 1.339 | 1.472 | 2.519 | 1.777 | 1.339 |
| 0.5 | On | Off | 1.260 | 1.236 | 2.682 | 1.726 | 1.236 |
| 0.5 | On | On | 1.447 | 2.030 | 3.427 | 2.301 | 1.447 |
| 0.6 | Off | On | 1.478 | 1.941 | 2.655 | 2.025 | 1.478 |
| 0.6 | On | Off | 1.404 | 1.520 | 3.058 | 1.994 | 1.404 |
| 0.6 | On | On | 1.555 | 3.110 | 3.848 | 2.838 | 1.555 |
| **0.7** | **Off** | **On** | 1.402 | 2.804 | 2.759 | 2.322 | 1.402 |
| **0.7** | **On** | **Off** | **1.455** | **1.726** | **3.975** | **2.385** | **1.455** |
| **0.7** | **On** | **On** | 1.435 | 3.407 | 4.580 | 3.141 | 1.435 |
| 0.8 | Off | Off | 1.073 | 3.825 | 3.702 | 2.867 | 1.073 |
| 0.8 | Off | On | 1.472 | 3.013 | 5.425 | 3.303 | 1.472 |
| **0.8** | **On** | **Off** | **1.575** | **2.346** | **5.501** | **3.141** | **1.575** |
| 0.8 | On | On | 1.493 | 3.784 | 8.195 | 4.491 | 1.493 |

### 2.3 최종 선정

**Best (최대 min PF)**: Threshold=0.8, FRGN=On, TRAJ=Off → min PF=**1.575**, avg=3.141

**채택 (보수적)**: Threshold=**0.7**, FRGN=**On**, TRAJ=Off → min PF=**1.455**, avg=2.385
- 이유: 0.7은 0.8보다 26% 더 많은 거래 포함 (1,302건 vs 993건)
- 3-Fold 전부 PF > 1.4 (안정적)
- TRAJ는 보너스 가산점으로만 활용 (MUST 조건에서 제외)

---

## 3. Phase 3: L3.3 구현 (Task 8)

### 3.1 supply_demand_gate.py

```
파일: backend/app/services/trading/cte/supply_demand_gate.py
클래스: SupplyDemandGate
설정: SupplyGateConfig (dataclass)
결과: SupplyGateResult (dataclass)
```

**MUST 조건** (모두 충족 필요):
1. `CLOSE_POSITION_5D > 0.7` — 5일 고저 내 종가 위치 (ohlcv_daily 기반)
2. `FRGN_CUMUL_5D > 0` — 외국인 5일 누적 순매수 (v4_investor_daily 기반)

**가산 보너스**:
| 조건 | 점수 | 설명 |
|------|-----:|------|
| CLOSE_POS pass | +3 | 기본 통과 점수 |
| 5일 신고가 (≥1.0) | +2 | E-3 Task 4: PF=13.483 |
| FRGN_CUMUL > 0 | +2 | 외인 순매수 확인 |
| TRAJECTORY ≥ 3 | +2 | 수급 궤적 상승 |
| DUAL_FLOW ≥ 3 | +1 | 기관+외인 동시매수 |
| 외인연속매수 ≥ 1 | +1 | 연속성 보너스 |

**판정 기준**:
| 점수 | 판정 | 동작 |
|-----:|------|------|
| ≥ 5 | ALLOW | 정상 진행 |
| 3–4 | CONDITIONAL | L3.5 CS에 위임 |
| < 3 | BLOCK | 즉시 차단 |

**전략별 오버라이드**:
- D6: FRGN 필수 (PF 1.144 → 5.054)
- D5/D7: TRAJECTORY < 1 시 점수 감점

### 3.2 CTE 파이프라인 통합

```
기존: L3(종목한도) → L3.2(VWAP) → L3.5(CS) → L4 ...
변경: L3(종목한도) → L3.3(수급) → L3.2(VWAP) → L3.5(CS) → L4 ...
```

- `supply_gate_result`를 `TradeSignal` 필드로 추가 (비동기 사전 계산)
- L3.3 BLOCK → `blocking_layer="L3.3_SUPPLY"`, 즉시 차단
- L3.3 CONDITIONAL → 통과, L3.5에서 추가 검증
- L3.3 ALLOW → 정상 진행
- `PipelineResult`에 `supply_gate_label`, `supply_gate_score` 필드 추가

### 3.3 단위 테스트

```
파일: backend/app/services/trading/cte/test_supply_demand_gate.py
테스트: 24건 ALL PASS
```

| 테스트 클래스 | 건수 | 검증 항목 |
|-------------|-----:|----------|
| TestSupplyDemandGateAllow | 3 | 기본 ALLOW, 전 레짐 ALLOW, 신고가 보너스 |
| TestSupplyDemandGateBlock | 5 | 데이터 부재, 저종가위치, 음수 FRGN, 제로 FRGN, D6 FRGN |
| TestSupplyDemandGateConditional | 1 | Fail-Open CONDITIONAL |
| TestSupplyDemandGateBoundary | 5 | threshold 정확값, 직상, 점수 cap(10), 최소양수, high==low |
| TestSupplyDemandGateStrategyOverride | 4 | D5/D7 궤적 패널티, D2 무패널티, D6 오버라이드 해제 |
| TestSupplyDemandGateNoPool | 1 | pool=None BLOCK |
| TestSupplyDemandGateConfig | 3 | 커스텀 threshold, FRGN 비활성화, 기본값 확인 |
| TestSupplyGateResult | 2 | 필드 생성, 기본값 |

기존 CTE 파이프라인 테스트: **33건 ALL PASS** (비파괴 확인)

---

## 4. Phase 4: 통합 리플레이 검증 (Task 9)

1,929건 Session D 거래에 대해 5가지 시나리오 비교:

| 시나리오 | N | PF | WR | MFE중간 | MAE중간 | Top10기여 |
|----------|---:|----:|----:|--------:|--------:|----------:|
| A. Baseline | 1,929 | 0.834 | 34.3% | 0.97% | -0.95% | 81.7% |
| B. E1 Anti-Pattern | 1,824 | 0.826 | 34.5% | 1.01% | -1.03% | 81.5% |
| C. L3.3 Supply Only | 352 | **2.778** | **50.3%** | 1.13% | -0.58% | 69.9% |
| **D. Full (L3.3+E1)** | **331** | **2.727** | **51.1%** | **1.18%** | **-0.61%** | **70.1%** |
| E. Full+Regime | 246 | 2.494 | 52.0% | 1.16% | -0.60% | 69.2% |

### 핵심 결과

1. **Baseline PF=0.834 → D_Full PF=2.727** (+227% 개선)
2. **승률 34.3% → 51.1%** (+16.8%p)
3. **거래 수 1,929 → 331건** (82.8% 필터링) — 품질 거래만 선별
4. **MAE 중간값 -0.95% → -0.61%** (손실 36% 감소)
5. E_Full+Regime은 추가 필터링(246건) 대비 성능 개선 미미 → 레짐 필터 불필요 확인

---

## 5. CEO D-002 "본질은 수급이다" 최종 검증

| 검증 항목 | 결과 | 수치 |
|----------|------|------|
| 단일 최강 변수 | CLOSE_POSITION_5D | AUC=0.682 (33변수 중 #1) |
| 외인 유의성 | p=0.014 (통계적 유의) | FDR 보정 후 유지 |
| 레짐 독립성 | 3레짐 모두 PF>1.5 | BEAR 오히려 최고(2.549) |
| Walk-Forward | 3-Fold ALL PASS | min PF=1.455 |
| 통합 리플레이 | PF +227% 개선 | 0.834 → 2.727 |

**결론**: CEO D-002 가설 **실증 완료**. 수급은 분봉 패턴(avg AUC=0.516)을 압도하는 근본 요인(avg AUC=0.556, 최강 0.682).

---

## 6. 산출물

### 코드
| 파일 | 설명 |
|------|------|
| `backend/app/services/trading/cte/supply_demand_gate.py` | L3.3 SupplyDemandGate (신규) |
| `backend/app/services/trading/cte/test_supply_demand_gate.py` | 단위 테스트 24건 (신규) |
| `backend/app/services/trading/cte/cte_pipeline.py` | L3.3 삽입 (수정) |

### 분석 스크립트
| 파일 | 설명 |
|------|------|
| `scripts/e3_supply_gate_validation.py` | Phase 1+2+4 전체 분석 |

### 데이터
| 파일 | 설명 |
|------|------|
| `/tmp/e3_results/e3_results.json` | 전체 분석 결과 JSON |
| `/tmp/e3_results/e3_features.csv` | 1,929건 피처 CSV |

---

## 7. 후속 작업

| 우선순위 | 항목 | 설명 |
|---------|------|------|
| P0 | Virtual Run 적용 | 03-03 Virtual Run에서 L3.3 활성화 |
| P1 | Signal Generator 연동 | signal_generator.py에서 SupplyDemandGate.evaluate() 호출 |
| P2 | 소형주 데이터 확대 | CEO 승인 ③: v4_investor_daily 커버리지 확대 |
| P3 | D2 trail_start 재검토 | E-2A에서 발견된 D2 trail 10% 역효과 해결 |
