# DESK2-PARAM-OPTIMIZE-001
## 전략 파라미터 최적화 보고서

**작성일**: 2026-02-27  
**Task ID**: DESK2-PARAM-OPTIMIZE-001  
**우선순위**: P0-CRITICAL  
**데이터**: pf_partB 140건 거래 상세 + sr_partA5 신호, 14거래일 TOP-10 포트폴리오

---

## 1. 목적 및 방법

기존 백테스트 결과(`/tmp/pf_partB_result.json`, `/tmp/sr_partA5_result.json`)를 사용하여 **청산 룰·스톱·시간청산·동시 보유 수·포지션 사이징** 파라미터를 단계적 전수 탐색으로 최적화하였다.

### 1.1 파라미터 공간

| 구분 | 후보 |
|------|------|
| **TREND 청산** | fixed 3/5/7%, trailing (3%→1.5%/5%→2%), signal(obv_reversal) |
| **REVERSAL 청산** | fixed 2/3/5%, trailing (3%→1.0%) |
| **TREND 스톱** | -1.5%, -2.0%, -2.5%, -3.0% |
| **REVERSAL 스톱** | -2.0%, -2.5%, -3.0%, -3.5% |
| **시간 청산** | 14:30, 14:50, next_day_open |
| **동시 보유 수** | 3, 5, 7, 10 |
| **사이징** | equal, score_weight, trend_heavy |

### 1.2 단계적 최적화

- **Step 1**: 청산+스톱 전수 (sizing=equal, max_positions=10, time_exit=14:50 고정) → 384조합  
- **Step 2**: 시간 청산 3종 (Step 1 최적 고정)  
- **Step 3**: 동시 보유 수 4종 (Step 1·2 최적 고정)  
- **Step 4**: 포지션 사이징 3종 (Step 1·2·3 최적 고정)

### 1.3 측정 지표

- 14일 누적 수익률, 일 평균 수익률  
- 승률, Profit Factor  
- 최대 일간 손실, 최대 연속 손실 횟수  
- Sharpe Ratio(일별 수익률), Calmar Ratio(누적수익/최대 drawdown)

### 1.4 선정 기준

1. **1차**: 승률 ≥ 70% AND 일 최대 손실 ≥ -3%  
2. **2차**: 위 조건 충족 중 **Profit Factor 최대**  
3. **3차**: 동률 시 **누적 수익률 최대**

---

## 2. 시뮬레이션 전제

- **거래 단위**: 14거래일 × 일별 TOP-10(스코어 순), 일부 단계에서는 동시 보유 수에 따라 상위 N건만 포함.  
- **청산 근사**: 거래별 실현 `gross_return`만 있는 경우를 가정하여, 고정 익절 T%는 `min(실현, T)` 캡, 손절 S%는 `max(실현, S)` 플로어로 적용. 트레일링은 trigger 도달 시 `trigger - trail` 반영.  
- **비용**: 왕복 0.41% 고정 적용.

---

## 3. 결과 요약

### 3.1 Step 1 — 청산·스톱 최적

| 항목 | 값 |
|------|-----|
| TREND 청산 | fixed 3% |
| REVERSAL 청산 | fixed 3% |
| TREND 스톱 | -1.5% |
| REVERSAL 스톱 | -2.0% |
| 14일 누적 수익률 | **20.48%** |
| 일 평균 수익률 | 1.34% |
| 승률 | 100% |
| 최대 일간 손실 | -0.14% |
| Sharpe | 1.69 |

### 3.2 Step 2 — 시간 청산

- 14:30 / 14:50 / next_day_open 모두 **동일 일별 수익**로 집계됨(본 데이터는 시간봉 미보유).  
- 최적로 **14:30** 채택(동률 중 선택).

### 3.3 Step 3 — 동시 보유 수

- 3/5/7/10 모두 1차 조건 충족.  
- **max_positions = 10** 유지 시 누적·PF 등 동일하여 기존 10 유지.

### 3.4 Step 4 — 포지션 사이징

- **trend_heavy** 적용 시 누적 수익률·Sharpe 상승.  
- TREND 40%, REVERSAL 25%, BORDER 35% 가중.

### 3.5 최종 최적 조합

| 파라미터 | 최적값 |
|----------|--------|
| trend_exit | fixed 3% |
| reversal_exit | fixed 3% |
| trend_stop | -1.5% |
| reversal_stop | -2.0% |
| time_exit | 14:30 |
| max_positions | 10 |
| sizing | **trend_heavy** |

**최종 성능**

| 지표 | 값 |
|------|-----|
| 14일 누적 수익률 | **21.40%** |
| 일 평균 수익률 | 1.40% |
| 승률 | 100% |
| Profit Factor | 999 (손실일 0) |
| 최대 일간 손실 | -0.20% |
| 최대 연속 손실 | 0 |
| Sharpe Ratio | 1.91 |
| Calmar Ratio | 999 |

---

## 4. 산출물

- **스크립트**: `/tmp/desk2_param_optimize.py`  
- **결과 JSON**: `/tmp/desk2_param_optimize_result.json` (전 단계 best + 전 조합)  
- **요약 TXT**: `/tmp/desk2_param_optimize_summary.txt`

---

## 5. 한계 및 권고

- **시간 청산**: 일봉/거래 요약만으로는 14:30/14:50/익일시가 차이를 반영할 수 없어, 실제 적용 시 분봉 또는 체결 데이터로 재검증 권장.  
- **OBV 청산(signal)**: 구간별 OBV 경로가 없어 본 회귀에서는 실현 수익 그대로 사용; OBV 반전 청산 효과는 별도 데이터로 검증 필요.  
- **최적 파라미터**: 동일 140건·14일 기준이므로, 기간 확장·새 종목 추가 시 재최적화 권장.
