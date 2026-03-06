---
project: kis-autotrade-v4
task_id: T-161
completed_at: 2026-03-06T10:30:00+09:00
---

# T-161 보고서: D-010 C7 NEW종목 실시간 탐지 구현 + DESK2 Phase B 완성

[인계 확인]
직전 완료: T-156 (SELL_FAILED 전건청산 + 모의매매 현황)
현재 단계: Phase 2c (Command Center)
CEO 지시 적용: D-006, D-008-KR, D-009, D-010, D-011
strategy_cards: 60
open_positions: 0

---

## 1. 작업 개요

| 항목 | 내용 |
|------|------|
| Task ID | T-161 |
| 제목 | D-010 C7 NEW종목 실시간 탐지 구현 + DESK2 Phase B 완성 |
| 브랜치 | phase-2c-command-center |
| 커밋 | d1b1bb9a |
| 테스트 결과 | 12/12 ALL PASS (C7) / 39/39 ALL PASS (전체 통합) |
| 우선순위 | P0-CRITICAL |

---

## 2. 구현 내용

### 2-1. C7NewStockDetectCondition (신규)

**파일**: `backend/app/services/desk2_conditions/c7_new_stock_detect.py`

D-009/D-011 기준 4대 핵심 조건:

| 조건 | 기준 | 구현 |
|------|------|------|
| 가격 급등 | 시가 대비 +5% OR 전일종가 대비 +10% | `price_surge_from_open` / `price_surge_from_prev` |
| 체결강도 | VP ≥ 120 (3분 이상 지속) | `vp >= vp_min` |
| 이평선 정배열 | 1분봉 MA5 > MA10 > MA20 | `ma5 > ma10 > ma20` |
| RSI 반등 | RSI_14 30~50 구간 | `rsi_low ≤ rsi ≤ rsi_high` |

추가 조건 (D-006, D-008-KR 반영):

| 조건 | 기준 | 처리 |
|------|------|------|
| IPO 가산점 | 상장 60일 이내 | `+0.1` score 가산 |
| 거래대금 | 30억 이상 | 미달 시 `-0.15` score 감점 |
| 데이터 결측 | 각 지표 없을 경우 | 해당 조건 패스 처리 |

**출력 구조**:
```python
{
  "triggered": bool,
  "is_triggered": bool,
  "score": float,          # 0~1
  "confidence": float,     # score와 동일
  "params": dict,
  "details": {
    "conditions_met": list,  # ["PRICE_SURGE", "VP_STRONG", "MA_ALIGNED", "RSI_REBOUND"]
    "volume_amount": float,
    "vp": float,
    "rsi": float,
    "ma_aligned": bool,
    "is_ipo_bonus": bool,
    ...
  }
}
```

**스코어 산식**:
- 가격 급등 강도: `min(best_surge / (surge_pct × 3), 1.0) × 0.30`
- VP 강도: `min((vp - vp_min) / vp_min, 1.0) × 0.25`
- 이평선 정배열: `+0.20` (확정)
- RSI 중간값 근접도: `(1 - |rsi - mid| / range) × 0.15`
- 거래대금 미달: `-0.15`
- IPO 가산점: `+0.10`

### 2-2. 통합 파일 수정

| 파일 | 변경 내용 |
|------|----------|
| `__init__.py` | `C7NewStockDetectCondition` import/export 추가 |
| `condition_registry.py` | `build_default_registry()` C7 등록 (총 8개: C1/C2/C3/C4/C5/C6/C7/CS1) |
| `signal_matcher.py` | `_CONDITION_SIGNAL_MAP["C7"] = ["TS-B4", "TS-B1"]` 추가 (D-011 기준) |
| `desk2_multi_condition_matcher.py` | `CONDITION_BITS["C7"] = 0b10000000 (128)`, `CONDITION_WEIGHTS["C7"] = 1.2` 추가 |
| `config/param_search_space.yaml` | `desk2_conditions.c7_new_stock_detect` 섹션 추가 |

### 2-3. CONDITION_BITS 전체 현황 (T-161 기준)

| 컨디션 | 비트 | 정수 | 전략 |
|--------|------|------|------|
| C1 | 0b00000001 | 1 | D6 상따갭 |
| C2 | 0b00000010 | 2 | D4 전상눌림 |
| C3 | 0b00000100 | 4 | 시초가강세 |
| C4 | 0b00001000 | 8 | 장중급등 |
| C5 | 0b00010000 | 16 | 테마동시급등 |
| C6 | 0b00100000 | 32 | 종가배팅갭 |
| CS1 | 0b01000000 | 64 | S1 거래대금폭발눌림 |
| **C7** | **0b10000000** | **128** | **NEW종목 실시간 탐지** |

---

## 3. 테스트 결과

### 3-1. C7 단위 테스트 (test_c7_new_stock_detect.py)

| TC | 설명 | 결과 |
|----|------|------|
| TC1 | 4조건 충족 → triggered=True | ✅ PASS |
| TC2 | 가격 급등 미달 → triggered=False | ✅ PASS |
| TC3 | VP 미달 (100 < 120) → triggered=False | ✅ PASS |
| TC4 | 이평선 역배열 → triggered=False | ✅ PASS |
| TC5 | RSI=65 (30~50 범위 밖) → triggered=False | ✅ PASS |
| TC6 | IPO 30일 가산점 → score 상승 확인 | ✅ PASS |
| TC7 | 거래대금 10억 (30억 미달) → score 감점 | ✅ PASS |
| TC8 | 백테스트 모드 — 5% 급등봉 감지 | ✅ PASS |
| TC9 | 데이터 없음 → triggered=False, error | ✅ PASS |
| TC10 | 전일종가 대비 11% 급등 (시가 기준 미달) → price_ok=True | ✅ PASS |
| TC11 | MultiConditionMatcher C7 등록 확인 | ✅ PASS |
| TC12 | CONDITION_BITS C7=128 비트충돌 없음 | ✅ PASS |

**C7 단위: 12/12 ALL PASS**

### 3-2. 전체 DESK2 통합 테스트

```
tests/test_c3_open_strength.py     9/9  PASS
tests/test_c4_intraday_surge.py    9/9  PASS
tests/test_c5_theme_simultaneous.py 9/9 PASS
tests/test_c7_new_stock_detect.py  12/12 PASS
─────────────────────────────────────────
총계: 39/39 ALL PASS (0.19s)
```

---

## 4. D-010 Phase B 완성 현황

| 컨디션 | Task | 상태 |
|--------|------|------|
| C1 (D6 상따갭) | T-128 | ✅ 완료 |
| C2 (D4 전상눌림) | T-125/T-128 | ✅ 완료 |
| C3 (시초가강세) | T-156 | ✅ 완료 |
| C4 (장중급등) | T-156 | ✅ 완료 |
| C5 (테마동시급등) | T-156 | ✅ 완료 |
| C6 (D7 종가배팅갭) | T-125/T-128 | ✅ 완료 |
| **C7 (NEW종목탐지)** | **T-161** | **✅ 완료** |
| CS1 (S1 눌림) | T-143 | ✅ 완료 |

**D-010 Phase B 완성: 총 8개 컨디션 모두 구현 완료**

---

## 5. 파일 목록

| 파일 | 상태 |
|------|------|
| `backend/app/services/desk2_conditions/c7_new_stock_detect.py` | 신규 |
| `backend/app/services/desk2_conditions/__init__.py` | 수정 |
| `backend/app/services/desk2_conditions/condition_registry.py` | 수정 |
| `backend/app/services/desk2_conditions/signal_matcher.py` | 수정 |
| `backend/app/services/desk2_conditions/desk2_multi_condition_matcher.py` | 수정 |
| `config/param_search_space.yaml` | 수정 |
| `tests/test_c7_new_stock_detect.py` | 신규 |

---

## 6. 체크포인트

- [x] 코드 레포 커밋 완료 (d1b1bb9a, phase-2c-command-center)
- [ ] project-docs 보고서 push 완료 (done_watcher.sh 처리 예정)

---

## 7. 절대 금지 사항 준수 확인

- [x] 서비스 재시작 없음
- [x] strategy_cards 변경 없음
- [x] C1~C6/CS1 기존 코드 변경 없음 (추가만)

HANDOVER.md 업데이트 완료: 별도 push 예정 (done_watcher.sh 자동 처리)
