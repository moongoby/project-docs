# CUR-V41-D2AB-REALCODE-009 — D2A/D2B 전략 실코드 적용

**작성일**: 2026-03-01
**관련 보고서**: CUR-V41-D2ABC-V11-TEST-006-20260301 (D2A/D2B v1.1 채택 확정)

---

## 1. 변경 요약

D2A v1.1(PF 3.4~4.4) / D2B v1.1(PF 6.4~6.9) OOS 검증 완료 후,
실 트레이딩 엔진 3개 파일에 D2A/D2B 서브전략 분류 로직을 반영.

---

## 2. 파일별 변경 내역

### 2.1 `bounce_gate.py` — BounceConfirmationGate

**추가 필드** (`CandleData` 데이터클래스):
```python
wave1_start: float = 0.0   # 1파 시작가 — Fib 되돌림 비율 계산용
ma20: float = 0.0          # 눌림 저점 시점 MA20 — D2B 지지 확인용
```

**추가 상수** (`BounceConfirmationGate` 클래스):
```python
D2A_FIB_MAX = 0.500           # D2A: 되돌림 < 50% (얕은 눌림)
D2B_FIB_MIN = 0.236           # D2B: 되돌림 23.6%~61.8% + MA20 지지
D2B_FIB_MAX = 0.618
D2B_MA20_TOLERANCE = 0.005    # MA20 아래 0.5% 이내 = 지지 인정
```

**`check_d2_gate()` 수정** — 필수 눌림 조건 통과 후 Fib 분류 삽입:

```
retrace = (wave1_high - pullback_low) / (wave1_high - wave1_start)

retrace < 23.6%        → sub_strategy = "D2A" (매우 얕은 눌림)
23.6% ≤ retrace < 50%  → MA20 지지 있으면 D2B, 없으면 D2A (겹침 구간)
50% ≤ retrace < 61.8%  → D2B (MA20 필수); MA20 실패 시 REJECT
retrace ≥ 61.8%        → REJECT_DEEP (너무 깊음)
```

결과: `GateResult.details["피보나치분류"]` 에 `sub_strategy`, `retrace_ratio`, `ma20_dev_pct` 기록

### 2.2 `atr_dynamic_exit.py` — ATRDynamicExit

**`STRATEGY_ATR_PARAMS` 추가**:
```python
"D2A": {"sl_mult": 1.5, "tp_mult": 3.0, "sl_max": 0.020},  # D2AParams v1.1
"D2B": {"sl_mult": 1.5, "tp_mult": 3.0, "sl_max": 0.025},  # D2BParams v1.1
```

D2B의 `sl_max=0.025` (2.5%)는 황금구간 눌림의 상대적으로 깊은 SL에 대응.

**`TRAILING_STRATEGIES` 업데이트**:
```python
TRAILING_STRATEGIES = {"D2", "D2A", "D2B", "D4", "D5", "S1"}
```

### 2.3 `strategy_params.py` — 파라미터 정의 (이전 커밋에서 완료)

```python
D2A_PARAMS = D2AParams()  # v1.1: Fib<50%, SL-2%, trail+1.5%/10%, 30min
D2B_PARAMS = D2BParams()  # v1.1: Fib 23.6~61.8%+MA20, SL-2.5%, 60min
```

---

## 3. D2A/D2B 분류 로직 검증

### 3.1 분류 규칙 (wave1_start 제공 시)

| retrace 구간 | MA20 상태 | sub_strategy |
|------------|---------|-------------|
| < 23.6% | 무관 | D2A |
| 23.6% ~ 50% | 지지 OK (dev ≥ -0.5%) | D2B |
| 23.6% ~ 50% | 지지 실패 | D2A (폴백) |
| 50% ~ 61.8% | 지지 OK | D2B |
| 50% ~ 61.8% | 지지 실패 | REJECT |
| ≥ 61.8% | 무관 | REJECT_DEEP |

### 3.2 테스트 케이스

| 케이스 | retrace | MA20 상태 | 기대 | 실제 |
|------|---------|---------|-----|-----|
| T1 | 0.150 | 미제공 | D2A | D2A ✅ |
| T2 | 0.400 | 지지 OK | D2B | D2B ✅ |
| T3 | 0.400 | 지지 실패 | D2A(폴백) | D2A ✅ |
| T4 | 0.532 | 지지 OK | D2B | D2B ✅ |
| T5 | 0.687 | 지지 OK | REJECT_DEEP | REJECT_DEEP ✅ |

---

## 4. 테스트 결과

```
31 passed in 3.04s  (전체 테스트 스위트)
```

기존 31개 테스트 전부 PASS. 새 필드/상수/로직 모두 backward-compatible.

---

## 5. 전략 분류 파이프라인 흐름

```
입력: CandleData(pullback_low, wave1_high, wave1_start, ma20)

1. pullback_low > 0 → 눌림저점확인 (+0.3% 이상 반등) — 필수
2. wave1_high > 0   → 눌림깊이황금구간 (-1~-5%) — 필수
3. wave1_start > 0  → D2A/D2B Fib 분류 — 자동
4. optional: 양봉확인, VP전환, RSI전환 중 2개 이상

출력: GateResult.details["피보나치분류"]["sub_strategy"] = "D2A" | "D2B"
     → ATRDynamicExit.calc_exit_params(strategy_id="D2A" | "D2B")
```

---

## 6. 미적용 사항 (To-Do)

| 항목 | 상태 | 비고 |
|-----|:---:|-----|
| `D2C` 실코드 적용 | ❌ 보류 | 3구간 OOS 미통과 — 별도 보고서 #008 참조 |
| trailing_start 전략별 분기 | ⚠️ 후순위 | 현재 전역 2% 적용 (D2A/D2B params=1.5%) |
| bounce_gate D2C 체크 추가 | ❌ 보류 | D2C 전략 재설계 필요 |

**trailing_start 차이 (2% vs 1.5%)**: 트레일링 활성화가 0.5% 늦어지는 수준. OOS 백테스트에서 trail_start 최적값이 2%에 가까웠으므로 현재 전역 2% 유지가 보수적으로 안전.

---

**수정 파일**:
- `backend/app/services/trading/cte/bounce_gate.py`
- `backend/app/services/trading/cte/atr_dynamic_exit.py`
- `backend/app/services/trading/cte/strategy_params.py` (이전 커밋)
