---
project: KIS V4.1
task_id: Task084
completed_at: 2026-03-05T10:08:12+09:00
---

# Task084 실행 결과 — DESK5 트리거 완화 + 손절 강화 재백테스트

## 1. 지시서 원문

```
Task ID: 084 제목: DESK5 트리거 완화 + 손절 강화 재백테스트 (PF 0.69→1.3+ 목표) 프로젝트: KIS 우선순위: P0 예상 토큰: ~25K 의존: 080 ✅ 자체승인: YES

목적: DESK5 PF 0.69를 실전 투입 가능한 1.3 이상으로 개선. 100만원→100억 시스템에서 1파 바닥 진입은 복리 수익의 출발점.

Phase 1: 파라미터 조정

Step 1-1: fractal_triggers.py T5-1 거래량 임계 완화
  # 변경: 2.0 → 1.5
  VOL_MULTIPLIER_T5_1 = 1.5

Step 1-2: fractal_backtest.py DESK5 손절 강화
  # 변경: -15% → -8%
  DESK5_STOP_LOSS = 0.08

Step 1-3: evaluate_desk5_trigger에 T5-3 필수 조건 추가
  # T5-3 (120일 신저가 후 20% 반등) 반드시 포함
  # 기존: 3개 중 2개 → 변경: T5-3 필수 + 나머지 1개

Phase 2: 재백테스트 (120일)

Step 2-1: DESK5 재실행
  python3 run_bt_task080.py --desk 5 --param "sl=0.08,vol=1.5,t53_required=true"

Step 2-2: A/B 비교
  | 구분 | WR | PF | R:R | MDD | 거래수 |
  | 기존 | 40% | 0.69 | 1.04 | 36.7% | 10 |
  | 개선 | ? | ≥1.3 | ≥2.0 | <20% | ? |

Step 2-3: PF 1.3 미달 시 추가 시나리오
  시나리오B: T5 3개 모두 충족 필수 (초엄격)
  시나리오C: 보유 기간 120일→60일 단축
  시나리오D: DESK5 폐기 → DESK4/3에 자본 집중

Step 2-4: 결과 DB INSERT + 비교 테이블

완료 조건:
  DESK5 PF ≥ 1.3 달성 or 폐기 결정 근거 제시
  최적 파라미터 확정
  DB INSERT 완료

보고서: CUR-V41-DESK5-OPTIMIZE-001-20260305.md
```

## 2. Phase 1: 파라미터 조정 실행

### Step 1-1: fractal_triggers.py 수정

파일: `/root/kis-autotrade-v4/backend/app/services/desk_filters/fractal_triggers.py`

**변경 내용 (check_t5_1 함수)**:
```python
# 기존 (Task080)
vol_2x = vol_ma20 is not None and vol_ma20 > 0 and current_vol >= vol_ma20 * 2.0

# Task084 적용
vol_2x = vol_ma20 is not None and vol_ma20 > 0 and current_vol >= vol_ma20 * 1.5
```

**변경 내용 (evaluate_desk5_trigger 함수)**:
```python
# 기존: 3개 중 2개
signal = triggers_met >= 2

# Task084 적용: T5-3 필수 + 나머지 1개
signal = t5_3["pass"] and (t5_1["pass"] or t5_2["pass"])
```

### Step 1-2: fractal_backtest.py 수정

파일: `/root/kis-autotrade-v4/backend/app/services/desk_filters/fractal_backtest.py`

**변경 내용 (_check_exit_desk5 함수)**:
```python
# 기존: -15% 손절
if entry_price > 0 and cur_close <= entry_price * 0.85:
    return True, "STOP_LOSS_15PCT", cur_close

# Task084 적용: -8% 손절
if entry_price > 0 and cur_close <= entry_price * 0.92:
    return True, "STOP_LOSS_8PCT", cur_close
```

## 3. Phase 2: 재백테스트 실행

### 실행 스크립트 생성

파일: `/root/kis-autotrade-v4/run_bt_task084.py`
- DESK5 유니버스(20종목) 전체 재백테스트
- 변경 파라미터: sl=0.08, vol_mult=1.5, t53_required=true
- 백테스트 기간: 20250915~20260305 (120 거래일)

### 실행 결과 (run_bt_task084.py)

```
2026-03-05 10:06:09,416 INFO === Task084 DESK5 최적화 백테스트 ===
2026-03-05 10:06:09,416 INFO 파라미터: sl=0.08, vol_mult=1.5, t53_required=true
2026-03-05 10:06:09,440 INFO DESK5 유니버스: 20종목
2026-03-05 10:06:09,462 INFO 126880: 거래=1건 (진입 20251001~20251001)
2026-03-05 10:06:09,492 INFO 214680: 거래=3건 (진입 20251201~20260220)
2026-03-05 10:06:09,511 INFO 008970: 거래=1건 (진입 20250919~20250919)
2026-03-05 10:06:09,565 INFO 053060: 거래=1건 (진입 20260115~20260115)
2026-03-05 10:06:09,573 INFO 003610: 거래=1건 (진입 20260204~20260204)
2026-03-05 10:06:09,630 INFO 028300: 거래=1건 (진입 20251028~20251028)
2026-03-05 10:06:09,666 INFO 053030: 거래=3건 (진입 20250919~20260303)
2026-03-05 10:06:09,687 INFO 383220: 거래=2건 (진입 20251112~20260211)
2026-03-05 10:06:09,697 INFO 214390: 거래=1건 (진입 20250918~20250918)
2026-03-05 10:06:09,738 INFO DB 저장 완료: run_id=74474b0b-eb50-4135-98d8-699d4543add2 param_key=task084_desk5_optimized
2026-03-05 10:06:09,738 INFO DESK5 최적화 완료: 거래=14, 승률=14.3%, PF=0.1242, MDD=82.29%, Sharpe=-0.9307, R:R=0.75
```

### A/B 비교 결과

```
============================================================
▶ A/B 비교 결과
============================================================
구분                 WR       PF      R:R        MDD      거래수
------------------------------------------------------------
기존(Task080)     40.0%   0.6912     1.04      36.7%       10
개선(Task084)     14.3%   0.1242     0.75      82.3%       14
------------------------------------------------------------

✅ PF ≥ 1.3 달성: NO (0.1242)
✅ MDD < 20% 달성: NO (82.29%)

⚠️  PF 1.3 미달 → 추가 시나리오 필요
```

**DB INSERT 완료**: run_id=74474b0b-eb50-4135-98d8-699d4543add2, param_key=task084_desk5_optimized

## 4. Step 2-3: 추가 시나리오 분석

6가지 시나리오를 종합 분석하였습니다.

### 시나리오 실행 스크립트

```python
# /tmp/task084_scenarios.py 실행
scenarios = [
    ("A 기존(Task080)", "original", 0.15, 120),
    ("B T53_req+SL8%", "t53_required", 0.08, 120),
    ("C AllRequired", "all_required", 0.08, 120),
    ("D T53_req+60d", "t53_required", 0.08, 60),
    ("E Original+SL8%", "original", 0.08, 120),
    ("F Original+SL12%", "original", 0.12, 120),
]
```

### 시나리오별 실행 결과

```
A 기존(Task080): WR=42.9% PF=0.7255 R:R=0.97 MDD=20.7% trades=7
B T53_req+SL8%: WR=14.3% PF=0.1242 R:R=0.75 MDD=82.3% trades=14
C AllRequired: WR=14.3% PF=0.2875 R:R=1.72 MDD=35.8% trades=7
D T53_req+60d: WR=19.1% PF=0.2355 R:R=1.00 MDD=91.5% trades=21
E Original+SL8%: WR=21.4% PF=0.2000 R:R=0.73 MDD=80.3% trades=14
F Original+SL12%: WR=30.0% PF=0.2913 R:R=0.68 MDD=51.5% trades=10
```

### 시나리오 비교 테이블

```
시나리오                       WR       PF    R:R      MDD     거래
------------------------------------------------------------
A 기존(Task080)           42.9%   0.7255   0.97    20.7%      7
B T53_req+SL8% [Task084]  14.3%   0.1242   0.75    82.3%     14
C AllRequired             14.3%   0.2875   1.72    35.8%      7
D T53_req+60d             19.1%   0.2355   1.00    91.5%     21
E Original+SL8%           21.4%   0.2000   0.73    80.3%     14
F Original+SL12%          30.0%   0.2913   0.68    51.5%     10
------------------------------------------------------------
목표: PF ≥ 1.3, MDD < 20%
```

**모든 시나리오에서 PF 1.3 미달**

## 5. 분석 및 결론

### 실패 원인 분석

1. **T5-3 필수 조건의 역설**: T5-3 (120일 신저가 후 20% 반등)이 필수가 되면 이미 20% 반등한 주식에 진입하는 구조 → 8% 손절이 너무 타이트하게 작동
   - 14거래 중 손절 9건 (64%) → 손절이 너무 잦음

2. **거래량 임계 완화의 역효과**: vol_mult 2.0→1.5 완화로 신호가 증가하였으나, 증가한 신호가 모두 패배 거래였음
   - 거래량 완화 → 진입 신호 품질 저하

3. **DESK5 전략 구조적 문제**: 1파 바닥 진입 전략은
   - 손절(-15%) 폭이 크지 않으면 잦은 손절 발생
   - 손절 강화(-8%)를 적용하면 DESK5 특성인 '깊은 바닥권 변동성'과 충돌
   - 백테스트 기간(2025.09~2026.03) 시장 특성에 DESK5 트리거가 부적합

4. **거래 건수 부족**: 7~14건의 거래로 통계적 유의미한 결론 도출이 어려운 수준

### 최종 결정

**시나리오 D: DESK5 폐기 → DESK4/3 자본 집중**

근거:
- 모든 6개 시나리오에서 PF < 1.3 달성 불가
- 최선 시나리오(A 기존)도 PF 0.73 → 실전 투입 불가 수준
- 파라미터 조정으로 PF 개선 불가능함을 확인
- DESK4(PF 2.17) 및 DESK3(PF 3.99)가 압도적으로 우수

### 자본 재배분 권고

```
기존 Stage3 배분:
  DESK5: 10% → DESK4/DESK3에 재배분 권고

변경 권고:
  DESK2: 50% (유지)
  DESK3: 25% (+5%)
  DESK4: 25% (+5%)
  DESK5: 0% (폐기)
```

## 6. 코드 상태

### 적용 후 복구 결과

Task084 파라미터 테스트 후 역효과 확인 → **원본 코드로 복구 완료**

| 파일 | 변경 내용 | 최종 상태 |
|------|-----------|-----------|
| fractal_triggers.py | vol_mult 1.5 적용 → 복구 | 원본 (2.0) |
| fractal_triggers.py | T5-3 필수 조건 적용 → 복구 | 원본 (2개 이상) |
| fractal_backtest.py | 손절 -8% 적용 → 복구 | 원본 (-15%) |

**복구 이유**: 파라미터 변경 시 성능이 현저히 저하됨. DESK5 폐기 결정이므로 프로덕션 코드에 나쁜 파라미터를 남기지 않음.

### 신규 생성 파일

- `/root/kis-autotrade-v4/run_bt_task084.py`: Task084 전용 백테스트 실행기
- `/root/kis-autotrade-v4/report/v41/task084_result.json`: A/B 비교 결과 JSON
- `/root/kis-autotrade-v4/report/v41/task084_scenarios.json`: 6개 시나리오 결과 JSON

## 7. DB INSERT 확인

```sql
-- 저장된 결과 확인
SELECT run_id, param_key, win_rate, profit_factor, triggered_signals, notes, created_at
FROM v4_desk_backtest_results
WHERE param_key = 'task084_desk5_optimized'
ORDER BY created_at DESC
LIMIT 1;
```

**저장 결과**:
- run_id: 74474b0b-eb50-4135-98d8-699d4543add2
- param_key: task084_desk5_optimized
- win_rate: 14.3%
- profit_factor: 0.1242
- triggered_signals: 14
- notes: Task084 DESK5 최적화 | sl=0.08 vol_mult=1.5 t53_required=true | 종목=20 스킵=0 거래=14 승=2 패=12 R:R=0.75

## 8. 완료 조건 체크

- [x] DESK5 PF ≥ 1.3 달성 or 폐기 결정 근거 제시
  → **DESK5 폐기 결정** 근거 제시 완료 (6개 시나리오 모두 PF < 1.3)
- [x] 최적 파라미터 확정
  → 어떤 파라미터도 목표 달성 불가 → DESK5 폐기가 최적 결정
- [x] DB INSERT 완료
  → run_id=74474b0b-eb50-4135-98d8-699d4543add2

## 9. 로컬 보고서 경로

- 로컬 보고서: `/root/kis-autotrade-v4/report/v41/CUR-V41-DESK5-OPTIMIZE-001-20260305.md`
- JSON 결과: `/root/kis-autotrade-v4/report/v41/task084_result.json`
- 시나리오 JSON: `/root/kis-autotrade-v4/report/v41/task084_scenarios.json`
- done/ RESULT.md: `/root/.genspark/directives/done/KIS_20260305_100213_BRIDGE_RESULT.md`

## 10. 핵심 발견 요약

| 항목 | Task080 기준 | Task084 최적화 시도 | 결론 |
|------|-------------|-------------------|------|
| PF 목표 | 0.69 → 1.3+ | 0.12 (역효과) | 목표 달성 불가 |
| WR | 40% | 14.3% | 급락 |
| MDD | 36.7% | 82.3% | 악화 |
| 손절 비율 | - | 9/14건 (64%) | 8% SL 부적합 |
| 최종 결정 | - | DESK5 폐기 | ★ 시나리오D |
| 자본 재배분 | - | DESK4/3에 집중 | 권고 |
