# CUR-V41-VWAP-ATR-ENGINE-001

**프로젝트**: KIS AutoTrade V4.1
**작성일**: 2026-03-01 (KST)
**작성자**: Claude Sonnet 4.6 (Cursor #18)
**선행 커밋**: `67602428` (CTE 파이프라인 통합, Cursor #17)
**관련 문서**:
- CUR-V41-DD-VWAP-GATE-DESIGN-001-20260301.md
- CUR-V41-VWAP-RECONCILE-001-20260301.md
- CUR-V41-EXIT-SLIPPAGE-INTEGRATE-001-20260301.md
- CUR-V41-CTE-PIPELINE-INTEGRATE-001-20260301.md

---

## Executive Summary

Cursor #18 Phase B-2 완료. VWAP 엔진(5변수)과 ATR 동적청산 모듈을 구현하고 CTE 파이프라인에 삽입하였다.

| 항목 | 결과 |
|------|------|
| 신규 파일 | `vwap_engine.py` (개선), `atr_dynamic_exit.py` (개선), `test_vwap_atr.py` (신규) |
| 수정 파일 | `cte_pipeline.py` (L3.2 + ATR 실행 레이어 추가) |
| 통합 테스트 | **25/25 PASS** |
| 기존 파이프라인 테스트 | **33/33 PASS** (비파괴 확인) |

---

## 1. VWAP 5변수 구현 (`vwap_engine.py`)

### 1.1 5변수 정의

| # | 변수명 | 공식 | 구현 |
|---|--------|------|------|
| V1 | `VWAP_PRICE` | Σ(TP×V)/Σ(V), TP=(H+L+C)/3 | `calc_vwap_from_bars()` |
| V2 | `VWAP_DISTANCE` | (price-vwap)/vwap×100 (%) | `vwap_distance` 필드 |
| V3 | `VWAP_SUPPORT_FLAG` | price ≥ vwap×0.997 | `vwap_support_flag` bool |
| V4 | `VWAP_SUPPORT_COUNT` | 장중 터치 후 반등 횟수 (≥2 임계점) | `vwap_support_count` int |
| V5 | `VWAP_TREND` | 최근 10분 선형회귀 기울기 (%/분) | `vwap_trend` float |

### 1.2 VWAP_TREND 구현

10개 봉 VWAP 히스토리를 `collections.deque(maxlen=10)`으로 관리하고 단순 선형회귀 OLS로 기울기를 산출.

```python
slope = Σ(xi - x̄)(yi - ȳ) / Σ(xi - x̄)²
# x: 시간 인덱스 (0..9), y: VWAP 값
# 결과: 원/분 → 첫 VWAP 기준 %/분으로 정규화
```

### 1.3 VWAP_SUPPORT_FLAG 정의

VWAP-RECONCILE 통일 정의(±0.3% 이내) 기반:
```
VWAP_SUPPORT_FLAG = True  if  price >= vwap × 0.997
```

경계값 검증:
- 9970 / 10000 = 0.997 → True ✓
- 9969 / 10000 < 0.997 → False ✓

### 1.4 보조 변수 (legacy 호환)

기존 파이프라인과의 호환을 위해 `cross_up`, `cross_down`, `price_position`(ABOVE/TOUCH/BELOW)도 유지.

---

## 2. ATR 동적 TP/SL 구현 (`atr_dynamic_exit.py`)

### 2.1 비용 상수 업데이트

| 항목 | 이전 | 개선 | 근거 |
|------|------|------|------|
| `COST_ROUNDTRIP` | 0.00071 (0.071%) | **0.0047 (0.47%)** | DD-VWAP-GATE §5: 수수료0.03%+세금0.18%+슬리피지0.26% |
| `COST_HALF` | N/A | **0.00235 (0.235%)** | NetR:R 계산용 half-cost |

### 2.2 전략별 ATR 멀티플라이어 (DD-VWAP-GATE §5.2 확정)

| 전략 | sl_mult | tp_mult | SL_MAX | SL_MIN |
|------|---------|---------|--------|--------|
| D2 | 1.5 | 3.0 | 2.0% | 0.3% |
| D4 | 1.5 | 3.5 | 2.5% | 0.3% |
| D5 | 2.0 | 4.0 | 2.5% | 0.3% |
| S1 | 1.5 | 3.0 | 2.0% | 0.3% |
| D6/D7 | — | — | — | EOD 전략 |

### 2.3 NetR:R ≥ 2.0 강제 공식

```python
net_sl = sl_pct + half_cost            # 비용 포함 실질 손실
min_tp = net_sl × 2.0 + half_cost     # NetR:R = 2.0 보장 TP
tp_pct = max(raw_tp_pct, min_tp)      # ATR 기반 vs 최소 TP
```

검증: 모든 전략(D2/D4/D5/S1)에서 NetR:R ≥ 2.0 보장 ✓

### 2.4 전략별 청산 방식 (EXIT-SLIPPAGE 확정)

| 전략 | ExitMode | 청산 상세 |
|------|----------|---------|
| D2 | `TRAILING` | start+5%, retrace20%, hard_stop-3%, timeout 60분 |
| D4 | `TRAILING` | start+5%, retrace20%, hard_stop-3%, timeout 60분 |
| D5 | `TRAILING` | start+5%, retrace20%, hard_stop-3%, timeout 60분 |
| D6 | `FIXED_EOD` | D+1 시초가 시장가 매도 (현행 유지) |
| D7 | `FIXED_EOD` | D+1 시초가 시장가 매도 (현행 유지) |
| S1 | `TRAILING_MA5` | 트레일링 + close < MA5 시 전량 청산 |

### 2.5 트레일링 하드 손절 상한

```python
hard_stop_price = entry_price × (1 - 0.03)  # -3%
# 트레일링 활성화 전후 관계없이 항상 적용
```

---

## 3. CTE 파이프라인 삽입 (`cte_pipeline.py`)

### 3.1 파이프라인 흐름 (수정 후)

```
[사전] FORBIDDEN / 우선순위 / 동시보유 한도
L1   ATR SL 계산
L2   전략 쿨다운
L3   종목 한도
L3.2 VWAP 지지 체크 ← 신규 (#18)
     VWAP_SUPPORT_COUNT < 2 → 포지션 50% 축소 (D2/D4/D5)
     VWAP_SUPPORT_FLAG = False → BounceGate 강화
L3.5 CS 게이트 (≥50 통과)
L4   포트폴리오 킬스위치
L4.5 EQS 게이트 (≥35 통과)
L5   시장(KOSDAQ) 게이트
[실행] ATR 동적 TP/SL + NetR:R 검증 ← 신규 (#18)
      NetR:R < 2.0 → blocking_layer="ATR_NETRR"
[사후] final = DD × min(CS, EQS, Market) × VWAP_mult
```

### 3.2 신규 상태 필드 (PipelineResult)

| 필드 | 타입 | 설명 |
|------|------|------|
| `vwap_support_count` | int | L3.2 VWAP 지지 횟수 |
| `vwap_support_flag` | bool | L3.2 VWAP_SUPPORT_FLAG |
| `vwap_multiplier` | float | 포지션 배수 (0.5 or 1.0) |
| `atr_exit_params` | ATRExitParams | ATR 기반 TP/SL 파라미터 |
| `atr_net_rr` | float | ATR NetR:R 값 |
| `atr_net_rr_ok` | bool | NetR:R ≥ 2.0 여부 |

### 3.3 최종 배수 계산

```
final_multiplier = DD_mult × min(CS_mult, EQS_mult, Market_mult) × VWAP_mult
```

VWAP_mult: 1.0 (지지 ≥2회) 또는 0.5 (지지 <2회, D2/D4/D5 한정)

---

## 4. 통합 테스트 결과 (25/25 PASS)

| 클래스 | 케이스 | 결과 |
|--------|--------|------|
| TestVWAPCalculation | 5 | ✅ 5/5 |
| TestVWAPSupport | 4 | ✅ 4/4 |
| TestATRCalculation | 3 | ✅ 3/3 |
| TestATREntryBlock | 3 | ✅ 3/3 |
| TestExitStrategy | 6 | ✅ 6/6 |
| TestPipelineIntegration | 4 | ✅ 4/4 |
| **합계** | **25** | ✅ **25/25** |

기존 파이프라인 테스트: 33/33 PASS (비파괴 확인)

### 주요 테스트 검증 항목

- **V1**: VWAP_PRICE = Σ(TP×V)/Σ(V) 정확도 ✓
- **V2**: VWAP_DISTANCE % 계산 ✓
- **V3**: VWAP_SUPPORT_FLAG 경계값 9970/9969 구분 ✓
- **V4**: SUPPORT_COUNT ≥2 → 1.0배, <2 → 0.5배 ✓
- **V5**: VWAP_TREND 상승 시리즈 양수 기울기 ✓
- **ATR**: COST_ROUNDTRIP=0.0047, NetR:R≥2.0 강제 ✓
- **전략 청산**: D2/D4/D5=TRAILING, D6/D7=FIXED_EOD, S1=TRAILING_MA5 ✓
- **파이프라인**: L3.2 결과 포함, VWAP_COUNT<2→0.5배 적용 ✓

---

## 5. PASS 기준 대비 점검

| 기준 | 조건 | 결과 |
|------|------|------|
| 통합 테스트 | 25/25 PASS | ✅ |
| VWAP 5변수 계산 | 단위테스트 정확도 검증 | ✅ |
| ATR NetR:R | ≥2.0 미달 시 진입차단 동작 확인 | ✅ |
| 전략별 청산 매핑 | D2/D4/D5 트레일링, D6/D7 시초가, S1 MA5이탈 | ✅ |
| 파이프라인 순서 | L3→VWAP(L3.2)→L3.5(CS)→L4→L4.5(EQS)→L5→ATR | ✅ |
| 기존 테스트 유지 | 33/33 비파괴 PASS | ✅ |

---

## 6. 설계 결정사항 (변경 이유)

### COST_ROUNDTRIP 0.071% → 0.47%

DD-VWAP-GATE 설계문서가 0.47% 왕복비용(수수료+세금+슬리피지)을 기준으로 NetR:R을 계산하므로 이에 맞춤. 기존 0.071%는 슬리피지만 반영한 불완전한 값이었음.

### TRAILING_HARD_STOP -3%

EXIT-SLIPPAGE 확정표에서 D2/D4/D5 트레일링의 SL을 -3%로 명시. ATR 기반 초기 SL(0.3~2.5%)이 더 타이트하므로, -3%는 최악의 경우 상한으로 작동.

### S1: ExitMode.TRAILING_MA5 신규 추가

인스트럭션 Task 2에서 S1을 "트레일링(지정가-1틱) + MA5 이탈"로 명시. `check_ma5_exit()` 정적 메서드를 통해 close < MA5 시 전량 청산 신호 제공.

---

## 저장 정보

- 서버 경로: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-VWAP-ATR-ENGINE-001-20260301.md`
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-VWAP-ATR-ENGINE-001-20260301.md
- 코드 커밋: `e84ac1b9` (phase-2c-command-center, moongoby/go100)
- 문서 커밋: `48f3bf9` (master, moongoby/project-docs)
- HTTP 확인: 200 ✓
- HANDOVER 업데이트: v4.6 (본 보고서에서 완료)
