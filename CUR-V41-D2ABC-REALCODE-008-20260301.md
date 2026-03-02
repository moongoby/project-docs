# CUR-V41-D2ABC-REALCODE-008-20260301

## 제목
D2A/D2B 실코드 적용 + D2C 3분봉/5분봉 VCP OOS 검증

## 날짜
2026-03-01

## 관련 이슈
- CUR-V41-D2ABC-30DAY-TEST-005 (v1.0 OOS-A)
- CUR-V41-D2ABC-V11-TEST-006 (v1.1 OOS-A/B)
- CUR-V41-D2C-V12-TEST-007 (v1.2 3구간)

---

## 1. D2C VCP — 3분봉 vs 5분봉 OOS 검증

### 배경
D2C v1.2 (1분봉 기준)가 3구간 OOS 모두에서 일관된 수익을 보이지 못함
→ 노이즈 감소를 위해 3분봉/5분봉 리샘플링 후 동일 VCP 패턴 재적용

### 파라미터 (D2C v1.2 기준)
```
contraction_min_bars = 4     # 수축 최소 4봉
explosion_vol_ratio  = 1.8   # 거래량 폭발: 직전 4봉 평균 × 1.8배
wave1_proximity_pct  = 0.05  # 1파 고점 ±5% 이내
range_contraction_ratio = 0.40  # 봉 범위 40% 이하로 수축
hold_bars: 3min=40봉(120분), 5min=24봉(120분)
```

### OOS 결과 (3구간)

| OOS | TF | N | WR | AvgPnL | PF | SL/TR/TO |
|---|---|---|---|---|---|---|
| OOS-A (2026-01-14~02-27) | 3min | 1 | 0.0% | -2.99% | 0.000 | 1/0/0 |
| OOS-A | **5min** | **4** | **50.0%** | **+0.57%** | **1.648** | 1/0/3 |
| OOS-B (2025-09-01~10-14) | 3min | 4 | 25.0% | -1.00% | 0.351 | 3/0/1 |
| OOS-B | **5min** | **2** | **50.0%** | **+1.94%** | **2.507** | 0/0/2 |
| OOS-C (2025-11-03~12-12) | 3min | 3 | 33.3% | -0.94% | 0.278 | 1/0/2 |
| OOS-C | 5min | 3 | 33.3% | -0.05% | **0.972** | 2/0/1 |

### 판단

| 항목 | 3분봉 | 5분봉 |
|---|---|---|
| 전체 PF 경향 | 0.278~0.351 (손실) | 0.972~2.507 |
| 3구간 일관성 | ❌ 모두 손실 | ⚠️ OOS-C 손익분기 미달 |
| 신호 건수 | N=1~4 | N=2~4 |

**5분봉이 3분봉 대비 일관적으로 우수하나, OOS-C PF=0.972로 3구간 동시 수익 미달.**

### 결론: D2C 보류
- 1분봉/3분봉/5분봉 모든 시도에서 3구간 OOS 동시 수익 달성 실패
- 건수가 너무 적어(N=1~4) 통계적 유의성 없음
- **D2C는 실코드 적용 보류, 추가 데이터 수집 후 재검토**

---

## 2. D2A/D2B 피보나치 분류 — 실코드 적용

### 수정 파일

#### `backend/app/services/trading/cte/bounce_gate.py`

**CandleData 추가 필드** (이전 세션 완료)
```python
wave1_start: float = 0.0   # 1파 시작가 — Fib 계산용
ma20: float = 0.0          # 눌림 저점 시점의 MA20 — D2B 지지 확인용
```

**BounceConfirmationGate 클래스 상수 추가** (이전 세션 완료)
```python
D2A_FIB_MAX = 0.500           # D2A: 되돌림 < 50%
D2B_FIB_MIN = 0.236           # D2B: 되돌림 23.6~61.8%
D2B_FIB_MAX = 0.618
D2B_MA20_TOLERANCE = 0.005    # MA20 아래 0.5% 초과 이탈 시 지지 실패
```

**check_d2_gate() 피보나치 분류 로직 추가** (이번 세션)

분류 규칙:
```
retrace < 23.6%        → D2A (매우 얕은 눌림)
23.6% ≤ retrace < 50%  → MA20 지지 있으면 D2B, 없으면 D2A (겹침 구간)
50% ≤ retrace < 61.8%  → D2B (MA20 필수); 없으면 REJECT
retrace ≥ 61.8%        → REJECT (너무 깊음)
```

MA20 지지 판정:
```python
ma20_dev = (pullback_low / ma20) - 1.0
ma20_ok = ma20_dev >= -0.005  # MA20 아래로 0.5% 초과 이탈 시 실패
```

GateResult.details["피보나치분류"] 예시:
```json
{"retrace_ratio": 0.40, "sub_strategy": "D2B", "ma20_dev_pct": -0.15}
```

#### `backend/app/services/trading/cte/atr_dynamic_exit.py`

```python
STRATEGY_ATR_PARAMS = {
    "D2":  {"sl_mult": 1.5, "tp_mult": 3.0, "sl_max": 0.020},
    "D2A": {"sl_mult": 1.5, "tp_mult": 3.0, "sl_max": 0.020},  # Fib<50%
    "D2B": {"sl_mult": 1.5, "tp_mult": 3.0, "sl_max": 0.025},  # Fib 23.6~61.8%+MA20
    ...
}
TRAILING_STRATEGIES = {"D2", "D2A", "D2B", "D4", "D5", "S1"}
```

D2B SL 상한을 2.5%로 확장 (D2BParams v1.1 기준, 황금구간 눌림 특성상 약간 더 깊은 SL 허용)

### 동작 검증 (5케이스)

| 케이스 | retrace | MA20 | 결과 | passed |
|---|---|---|---|---|
| T1 D2A | 0.15 (< 23.6%) | 미제공 | D2A | ✅ True |
| T2 D2B | 0.40 (겹침) | 지지(-0.15%) | D2B | ✅ True |
| T3 D2A폴백 | 0.40 (겹침) | 이탈(-2.2%) | D2A | ✅ True |
| T4 REJECT_DEEP | 0.687 (≥ 61.8%) | - | REJECT | ✅ False |
| T5 Fib없음 | wave1_start=0 | - | D2(기본) | ✅ True |

**T3 설명**: retrace 23.6~50% 오버랩 구간에서 MA20 이탈 → D2A로 폴백 (D2A는 MA20 불필요)

---

## 3. 전체 테스트

```
31 passed in 3.19s
```

---

## 4. 배포 상태

| 구분 | 상태 |
|---|---|
| bounce_gate.py D2A/D2B Fib 분류 | ✅ 적용 완료 |
| atr_dynamic_exit.py D2A/D2B ATR | ✅ 적용 완료 |
| strategy_params.py D2AParams/D2BParams/D2CParams | ✅ 적용 완료 (이전 세션) |
| D2C 실코드 | ⏸️ 보류 (3구간 수익 미달) |
| 테스트 31건 | ✅ ALL PASS |

---

## 5. 남은 과제

1. **CTE 파이프라인 연동**: `check_d2_gate()` 반환값에서 `details["피보나치분류"]["sub_strategy"]` 읽어 전략 ID를 D2A/D2B로 분기 → 각각의 ATR 파라미터 적용
2. **wave1_start/ma20 공급**: 실거래 데이터 수집 시 CandleData에 wave1_start, ma20 주입 필요
3. **D2C 재검토**: 더 많은 구간 또는 다른 필터(VWAP 겹침 등) 적용 후 재시도
