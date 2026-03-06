---
project: kis-autotrade-v4
task_id: T-163B
completed_at: 2026-03-06T10:45:00+09:00 KST
---

# KIS_20260306_104123_BRIDGE_RESULT — T-163B 실행 결과

## 지시서 원문
```
Task ID: T-163B 제목: SL 완화 (D-ORB 4%/D4 3%/D7 3%) 서버: 211 (kis-autotrade-v4) 우선순위: P0-CRITICAL 예상 시간: 5분 의존성: 없음

작업:

# 1) 현재 SL 값 확인
grep -n "stop_loss\|SL\|sl_pct" /root/kis-autotrade-v4/config/param_search_space.yaml

# 2) D-ORB 2.5→4.0, D4 2.0→3.0, D7에 3.0 추가 (vi 또는 sed)
# 원래값 주석 보존: # was 2.5 T-163B

# 3) 변경 확인
grep -A2 -B2 "stop_loss" /root/kis-autotrade-v4/config/param_search_space.yaml

# 4) git commit
cd /root/kis-autotrade-v4 && git add -A && git commit -m "[V4.1] T-163B SL loosen D-ORB/D4/D7"


보고서: CUR-V41-T163B-SL-FIX-20260306.md 금지: 서비스 재시작, 다른 전략 SL 변경.
```

---

## Step 1: 현재 SL 값 확인

### grep config/param_search_space.yaml 결과
```
129:  stop_loss_threshold: 0.93           # 손절 임계값 (진입가의 93% = -7%)
269:  desk4.stop_loss_threshold:
331:    entry_sl_pct: 0.08                # 손절 8%
361:      exit_stop_loss_pct: 0.06        # SL 축소 → 생존율 UP ✓
571:  sl_pct: 2.0             # 손절: -2%
697:    sl_pct: 2.0
703:    sl_pct: 1.0                  # 시간외 -1%
710:    sl_pct: 1.5
721:    sl_pct: 2.0
849:    sl_pct: 2.0                  # 손절 -2%
```

### grep scripts/run_unified_engine.py 결과 (D-ORB 포함)
```
887:        "D2":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
888:        "D2A": {"sl_pct": 0.020, "tp_pct": None,  "timeout_min": 30},
889:        "D2B": {"sl_pct": 0.025, "tp_pct": None,  "timeout_min": 60},
890:        "D4":  {"sl_pct": 0.020, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305: SL 2%, TP 3%
891:        "D5":  {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
892:        "S1":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": None},
893:        "D6":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
894:        "D7":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
895:        "D-ORB": {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
```

---

## Step 2: 파일 수정 (T-163B)

### 수정 파일 1: scripts/run_unified_engine.py (line 890, 895)

**변경 전:**
```python
"D4":  {"sl_pct": 0.020, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305: SL 2%, TP 3%
"D-ORB": {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
```

**변경 후:**
```python
"D4":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305: SL 2%, TP 3% | T-163B: SL 2.0→3.0 (was 2.0 T-163B)
"D-ORB": {"sl_pct": 0.040, "tp_pct": 0.030, "timeout_min": 60},  # T-163B: SL 2.5→4.0 (was 2.5 T-163B)
```

### 수정 파일 2: config/param_search_space.yaml (desk2_conditions)

**c2_prev_ul (D4) 변경 전:**
```yaml
  c2_prev_ul:                    # C2: 전일 상한가 → D4
    ul_pct_min: 29.0             # 상한가 기준 (29%+)
    next_day_ma20_1m_break: true # 당일 1분봉 MA20 돌파
    timeout_minutes: 60          # D-011: 60분 보유
    sl_pct: 2.0
    tp_pct: 3.0
```

**c2_prev_ul (D4) 변경 후:**
```yaml
  c2_prev_ul:                    # C2: 전일 상한가 → D4
    ul_pct_min: 29.0             # 상한가 기준 (29%+)
    next_day_ma20_1m_break: true # 당일 1분봉 MA20 돌파
    timeout_minutes: 60          # D-011: 60분 보유
    sl_pct: 3.0                  # T-163B: SL 완화 2.0→3.0 (was 2.0 T-163B)
    tp_pct: 3.0
```

**c6_close_strong (D7) 변경 전:**
```yaml
  c6_close_strong:               # C6: 종가 강세 → D7
    entry_after: "14:30"         # 14:30 이후만
    supply_focus: true           # 수급 집중
    low_rising: true             # 저점 상승
    volume_increase: true        # 거래량 증가
    sl_pct: 1.5
    next_day_open_sell: true
```

**c6_close_strong (D7) 변경 후:**
```yaml
  c6_close_strong:               # C6: 종가 강세 → D7
    entry_after: "14:30"         # 14:30 이후만
    supply_focus: true           # 수급 집중
    low_rising: true             # 저점 상승
    volume_increase: true        # 거래량 증가
    sl_pct: 3.0                  # T-163B: SL 완화 1.5→3.0 추가 (was 1.5 T-163B)
    next_day_open_sell: true
```

---

## Step 3: 변경 확인

### run_unified_engine.py 최종 SL 상태
```
890: "D4":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305: SL 2%, TP 3% | T-163B: SL 2.0→3.0 (was 2.0 T-163B)
891: "D5":  {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
892: "S1":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": None},
893: "D6":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
894: "D7":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
895: "D-ORB": {"sl_pct": 0.040, "tp_pct": 0.030, "timeout_min": 60},  # T-163B: SL 2.5→4.0 (was 2.5 T-163B)
```

### param_search_space.yaml 최종 SL 상태
```
697:    sl_pct: 3.0                  # T-163B: SL 완화 2.0→3.0 (was 2.0 T-163B)
710:    sl_pct: 3.0                  # T-163B: SL 완화 1.5→3.0 추가 (was 1.5 T-163B)
```

---

## Step 4: git commit

```
git add config/param_search_space.yaml scripts/run_unified_engine.py
git commit -m "[V4.1] T-163B SL loosen D-ORB/D4/D7
...
"
```

### 결과:
```
[phase-2c-command-center 34e762b0] [V4.1] T-163B SL loosen D-ORB/D4/D7
 2 files changed, 4 insertions(+), 4 deletions(-)
```

---

## 최종 SL 요약

| 전략   | 변경 전 SL | 변경 후 SL | 변경 파일                                      |
|--------|-----------|-----------|------------------------------------------------|
| D-ORB  | 2.5%      | 4.0%      | scripts/run_unified_engine.py                 |
| D4     | 2.0%      | 3.0%      | scripts/run_unified_engine.py + config/param_search_space.yaml |
| D7     | 1.5%      | 3.0%      | config/param_search_space.yaml                |

## 금지 항목 준수
- ✅ 서비스 재시작 없음
- ✅ D2/D5/D6/S1 SL 변경 없음

## 보고서
- 로컬: /root/kis-autotrade-v4/report/v41/CUR-V41-T163B-SL-FIX-20260306.md
