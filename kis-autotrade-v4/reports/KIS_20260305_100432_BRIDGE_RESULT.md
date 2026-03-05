---
project: KIS V4.1
task_id: "086"
completed_at: "2026-03-05T10:16:27 KST"
---

# KIS_20260305_100432_BRIDGE_RESULT
## Task 086: 100만원→100억 복리 시뮬레이션 + Stage 자동 전환 설계 — 실행 결과

---

## 1. 지시서 파일 확인

```
파일: /root/.genspark/directives/running/KIS_20260305_100432_BRIDGE.md
내용 요약:
  - Task ID: 086
  - 제목: 100만원→100억 복리 시뮬레이션 + Stage 자동 전환 설계
  - 목적: 현재 백테스트 결과 기반으로 100만원에서 100억까지 도달하는
          복리 경로를 수학적으로 설계. Stage 자동 전환 트리거 정의.
  - 보고서: CUR-V41-COMPOUND-GROWTH-SIM-001-20260305.md
```

---

## 2. Phase 1: 복리 시뮬레이션 모델

### Step 1-1: 시뮬레이션 스크립트 생성

**파일 생성: `/root/kis-autotrade-v4/scripts/compound_growth_simulator.py`**

```
생성 결과: 성공
파일 크기: 약 8.5KB
실행 권한: Python 3.12.3 (venv)
```

스크립트 주요 구성 요소:

- `STAGES` 딕셔너리: Stage 1~4 자본 범위 및 DESK 배분
- `STAGE_TRANSITIONS`: 업그레이드 트리거
- `STAGE_DOWNGRADES`: 역전환 안전장치
- `DESK_PARAMS`: 각 DESK 파라미터 (avg_pnl, holding_days, win_rate, 등)
- `get_desk_expected_daily()`: μ = avg_pnl / holding_days 계산
- `get_desk_daily_return()`: 확률적 일일 수익률 생성 (win/loss 혼합 가우시안)
- `run_single_simulation()`: 단일 시뮬레이션 실행
- `run_monte_carlo()`: 1,000회 반복
- `build_summary_table()`: 5/50/95 백분위수 테이블

### Step 1-2: DESK별 일일 기대수익률

```
DESK3: avgPnL 9.33% / 보유 ~15일 = 일 0.622%
DESK4: avgPnL 4.20% / 보유 ~20일 = 일 0.210%
DESK5: avgPnL 3.50% / 보유 ~12일 = 일 0.292%
DESK2: avgPnL 2.80% / 보유 ~8일  = 일 0.350%
GO100: avgPnL 5.00% / 보유 ~30일 = 일 0.167%
BOND:  연 7.5%  / 250일          = 일 0.030%
```

수식: μ = avg_pnl_pct / holding_days

### Step 1-3: 몬테카를로 시뮬레이션 실행 로그 (1,000회)

```
=================================================================
Task 086: 100만원→100억 복리 시뮬레이션 (몬테카를로)
  초기자본:       1,000,000원
  목표자본:  10,000,000,000원
  시뮬레이션: 1,000회  / 최대기간: 10년
=================================================================

[Stage별 가중 일일 기대수익률]
  Stage1: 일 0.4984%  / 연 246.57%
  Stage2: 일 0.4382%  / 연 198.33%
  Stage3: 일 0.4088%  / 연 177.3%
  Stage4: 일 0.3543%  / 연 142.08%
[Monte Carlo] 1,000회 시뮬레이션 시작...
  진행:    0/1000 (0%)
  진행:  200/1000 (20%)
  진행:  400/1000 (40%)
  진행:  600/1000 (60%)
  진행:  800/1000 (80%)
  완료: 1,000회

[도달 기간 테이블]
                                Stage2 (4천만)       Stage3 (2억)      Stage4 (10억)     Target (100억)
  보수적(5%ile)                            3.3년              4.9년              6.5년              9.2년
  중간(50%ile)                            3.0년              4.5년              6.1년              8.7년
  낙관적(95%ile)                           2.7년              4.1년              5.7년              8.2년

  목표 도달률      : 100.0%
  평균 최대 낙폭   : 4.28%

[Stage 업그레이드 트리거]
  1→2: capital >= 40M AND trailing_30d_pf >= 1.5
  2→3: capital >= 200M AND trailing_60d_pf >= 1.3 AND max_dd_30d <= 15%
  3→4: capital >= 1B AND trailing_90d_pf >= 1.2 AND max_dd_60d <= 20%

[Stage 다운그레이드(안전장치) 트리거]
  2→1: capital < 30M OR trailing_30d_pf < 1.0
  3→2: capital < 150M OR max_dd_30d > 25%

  JSON export → /root/kis-autotrade-v4/report/v41/task086_simulation_result.json

[완료] compound_growth_simulator.py 실행 완료
```

---

## 3. Phase 2: Stage 자동 전환 트리거

### Step 2-1: 전환 조건 정의

```python
STAGE_TRANSITIONS = {
    "1→2": {
        "condition":         "capital >= 40M AND trailing_30d_pf >= 1.5",
        "capital_threshold":  40_000_000,
        "pf_threshold":       1.5,
        "pf_window":          30,
    },
    "2→3": {
        "condition":         "capital >= 200M AND trailing_60d_pf >= 1.3 AND max_dd_30d <= 15%",
        "capital_threshold":  200_000_000,
        "pf_threshold":       1.3,
        "pf_window":          60,
        "max_dd_threshold":   0.15,
    },
    "3→4": {
        "condition":         "capital >= 1B AND trailing_90d_pf >= 1.2 AND max_dd_60d <= 20%",
        "capital_threshold":  1_000_000_000,
        "pf_threshold":       1.2,
        "pf_window":          90,
        "max_dd_threshold":   0.20,
    },
}
```

### Step 2-2: 역전환(안전장치) 조건

```python
STAGE_DOWNGRADES = {
    "2→1": {
        "condition":         "capital < 30M OR trailing_30d_pf < 1.0",
        "capital_threshold":  30_000_000,
        "pf_threshold":       1.0,
        "pf_window":          30,
    },
    "3→2": {
        "condition":         "capital < 150M OR max_dd_30d > 25%",
        "capital_threshold":  150_000_000,
        "max_dd_threshold":   0.25,
        "pf_window":          30,
    },
}
```

시뮬레이션 내 다운그레이드 로직 (자본 기준):
```python
# Stage 다운그레이드 (자본 기준)
if stage == 2 and capital < 30_000_000:
    stage = 1
elif stage == 3 and capital < 150_000_000:
    stage = 2
```

---

## 4. Phase 3: 결과 시각화 데이터

### Step 3-1: 도달 예상 기간 테이블 (완성)

| 시나리오 | 100만→4천만 | →2억 | →10억 | →100억 | 총 기간 |
|---------|-----------|------|-------|--------|--------|
| 보수적(5%ile) | **3.3년** | **4.9년** | **6.5년** | **9.2년** | 9.2년 |
| 중간(50%ile) | **3.0년** | **4.5년** | **6.1년** | **8.7년** | 8.7년 |
| 낙관적(95%ile) | **2.7년** | **4.1년** | **5.7년** | **8.2년** | 8.2년 |

### Step 3-2: JSON export 완료

```
파일: /root/kis-autotrade-v4/report/v41/task086_simulation_result.json
내용:
  - task_id: "086"
  - generated_at: 2026-03-05T...
  - initial_capital: 1000000
  - target_capital: 10000000000
  - n_simulations: 1000
  - stages: {1~4 정의}
  - stage_transitions, stage_downgrades
  - desk_params (DESK2~5, GO100, BOND)
  - stage_summary (Stage별 일/연 기대수익)
  - simulation_table (보수적/중간/낙관적 × 4마일스톤)
  - meta: {target_reach_rate_pct: 100.0, avg_max_drawdown_pct: 4.28}
```

---

## 5. 완료 조건 검증

| 조건 | 결과 |
|------|------|
| ✅ 복리 시뮬레이션 1,000회 실행 | **완료** — 1,000/1,000회 성공 |
| ✅ Stage 전환 트리거 코드 구현 | **완료** — STAGE_TRANSITIONS (3개) |
| ✅ 도달 기간 테이블 생성 | **완료** — 5%/50%/95% 백분위수 × 4 마일스톤 |
| ✅ 역전환 안전장치 포함 | **완료** — STAGE_DOWNGRADES (2개) |

---

## 6. 생성된 파일 목록

```
신규 생성:
  /root/kis-autotrade-v4/scripts/compound_growth_simulator.py
  /root/kis-autotrade-v4/report/v41/task086_simulation_result.json
  /root/kis-autotrade-v4/report/v41/CUR-V41-COMPOUND-GROWTH-SIM-001-20260305.md
  /root/.genspark/directives/done/KIS_20260305_100432_BRIDGE_RESULT.md (본 파일)
```

---

## 7. 주요 발견사항

1. **10년 이내 100억 도달 가능성 100%**: 백테스트 수익률 유지 시 모든 시뮬레이션에서 목표 도달
2. **낙폭 안전**: 평균 최대 낙폭 4.28%로 매우 낮음 (안전한 복리 경로)
3. **Stage1이 병목**: 초기 100만→4천만 구간이 전체 기간의 약 34% 차지 (3.0년/8.7년)
4. **Stage 배분 원칙**: 자본 규모 증가 시 위험 다각화 확대 (DESK 수 증가, BOND 추가)
5. **연 수익률 의도적 감소**: Stage1(246%) → Stage4(142%) — 자본 보호 중심 전환

---

_작업 완료: 2026-03-05T10:16:27 KST_
_Task: 086 / KIS V4.1_
