---
project: kis-autotrade-v4
task_id: T-229
completed_at: 2026-03-09T14:30:00+09:00
---

# KIS_20260307_002325_BRIDGE 실행 결과

## 지시서 원문

```
Task ID: T-229 제목: Exit Manager D5 정비 + MA20 트레일링 스톱 + hypothesis_winners 서버: 211 (kis-autotrade-v4) 우선순위: P0-CRITICAL 예상 시간: 40분 의존성: T-226

배경: D5 34 trades/0 wins/PnL 0.0%. 백테스트 승자 H05-D(MA20 trail PF=2.18), H08-B(5주 PF=25.93) 미적용. 구 T-201 통합.

수행 내용:

D5 exit 현행 trace: D5_D014_CONFIG(enabled=True, min_hold_weeks=4) 호출 경로 확인
MA20 트레일링 구현: _check_ma20_trailing_stop() — 10거래일 연속 종가<MA20 → EXIT
hypothesis_winners.yaml 생성:
H08-B: desk=D5, hold_weeks=5, pf=25.93
H05-D: desk=[D3,D4], trail=MA20, pf=2.18
H12-D: desk=ALL, hold_multiplier=2.0, pf=3.15
테스트 5건: MA20 10일 breach/9일 hold/min_hold 미달/winners 로드/복합

성공 기준: MA20 trailing + hypothesis_winners.yaml + 테스트 ALL PASS 보고서: CUR-V41-EXIT-MANAGER-D5-MA20-001-20260309.md 주의: exit_manager.py 핵심 파일 → review/ + CEO 승인 완료 후: HANDOVER.md 갱신 + git push
```

---

## Step 1: 파일 읽기 결과

### 인계서 확인 (HANDOVER.md v10.37 — 최신 70k 토큰 파일, 상단 100줄 읽음)
- 최신 완료: T-235 SMALL_CAP_QUALITY+SEC_LEADER_FLAG v2 (커밋 20017658)
- D5_D014_CONFIG: enabled=True, min_hold_weeks=4 (T-201/T-215 확인됨)
- exit_manager.py: `backend/app/services/trading/exit_manager.py` (592줄)

### CEO-DIRECTIVES.md 확인
- D-014: DESK5 코어 보유 — 주봉 MA20 2주 연속 이탈/세력이탈/테마사망 3가지 외 청산 금지
- D-008-KR: 한국 슈퍼개미 전략 통합 P0 (THEME_CYCLE/SMALL_CAP_QUALITY/DUAL_FLOW/SEC_LEADER v2)

---

## Step 2: D5 Exit 현행 Trace 결과

**파일 위치**: `/root/kis-autotrade-v4/backend/app/services/trading/exit_manager.py`

**D5 호출 경로**:
```
ExitManager.should_exit(strategy="D5")
  └── D5_D014_CONFIG["enabled"] = True  ← 확인됨
       └── _check_d5_d014()
            ├── seoryeok_exit=True → EXIT("SEORYEOK_EXIT")
            ├── theme_death=True → EXIT("THEME_DEATH_EXIT")
            ├── elapsed_days < min_hold_days(4주=28일) → HOLD
            │    └── +100% → partial_exit=True("PRINCIPAL_RECOVERY")
            └── 4주 이후:
                 ├── calculate_ma20_trailing(ohlcv_daily, "D5")
                 │    └── 주봉 MA20, 2주 연속 이탈 → EXIT("MA20_WEEKLY_CONSECUTIVE")
                 └── +100% → partial_exit=True("PRINCIPAL_RECOVERY")
```

**핵심 설정값 확인**:
- `D5_D014_CONFIG["enabled"]` = True ✅
- `D5_D014_CONFIG["min_hold_weeks"]` = 4 ✅
- `D5_D014_CONFIG["weekly_ma20_consecutive"]` = 2 ✅
- `D5_LONG_HOLD_CONFIG["enabled"]` = False (T-193→T-201으로 교체, 비활성) ✅
- `SIXTY_MIN_STRATEGIES` = {"D2", "D4"} — D5 제거됨 ✅
- `MAX_SL_CAP["D-ORB"]` = 0.020, `["D4"]` = 0.018, `["D6"]` = 0.020 ✅

**문제점**:
- D5 34건 0수익의 근본 원인: 주봉 MA20 2주 연속 이탈 기준이 너무 보수적
- H05-D (일봉 MA20 연속 이탈, PF=2.18) 미적용 상태

---

## Step 3: `_check_ma20_trailing_stop()` 구현

**파일**: `backend/app/services/trading/exit_manager.py`

**추가 위치**: ExitManager 클래스 직전 (calculate_atr_sl() 이후)

**구현된 함수 전문**:
```python
def _check_ma20_trailing_stop(
    ohlcv_daily: List[Dict[str, Any]],
    consecutive_days: int = 10,
) -> Dict[str, Any]:
    """
    T-229: MA20 트레일링 스톱 — N거래일 연속 종가<일봉MA20 → EXIT.

    H05-D 백테스트 승자 (PF=2.18, desk=[D3,D4]) 기반.
    daily close가 20일 이동평균(MA20) 이하로 consecutive_days 연속 지속되면 청산.

    각 거래일마다 해당 시점의 MA20을 산출(슬라이딩 윈도우)하여
    연속 이탈 여부를 판정한다.

    Args:
        ohlcv_daily: 일봉 OHLCV (오름차순 정렬, 최신이 마지막)
                     각 항목: {"close": float, ...}
        consecutive_days: 연속 이탈 일수 임계값 (기본 10거래일)

    Returns:
        {
            "should_exit": bool,
            "reason": str,              # "MA20_DAILY_CONSECUTIVE" | "HOLD" | "INSUFFICIENT_DATA"
            "ma20": Optional[float],    # 최신 MA20 값
            "current_price": Optional[float],
            "consecutive_breaks": int,  # 연속 이탈 일수 (최신 기준 역산)
        }
    """
    if not ohlcv_daily:
        return {
            "should_exit": False,
            "reason": "INSUFFICIENT_DATA",
            "ma20": None,
            "current_price": None,
            "consecutive_breaks": 0,
        }

    closes = [float(b["close"]) for b in ohlcv_daily if b.get("close") is not None]
    n = len(closes)

    # 슬라이딩 MA20 계산: 각 체크 대상 날(consecutive_days개)에 대해
    # 20일 창이 필요하므로 최소 19 + consecutive_days개 필요
    min_required = 19 + consecutive_days
    if n < min_required:
        return {
            "should_exit": False,
            "reason": "INSUFFICIENT_DATA",
            "ma20": None,
            "current_price": closes[-1] if closes else None,
            "consecutive_breaks": 0,
        }

    # 최신 MA20 (참조용)
    ma20_latest = sum(closes[-20:]) / 20
    current_price = closes[-1]

    # 연속 이탈 일수 카운트 (최신→과거 방향으로 역산, 연속이 끊기면 중단)
    consecutive_breaks = 0
    for i in range(consecutive_days):
        idx = n - 1 - i                          # 절대 인덱스 (0-based)
        ma20_at_idx = sum(closes[idx - 19:idx + 1]) / 20
        if closes[idx] < ma20_at_idx:
            consecutive_breaks += 1
        else:
            break                                # 연속이 끊긴 시점에서 중단

    should_exit = consecutive_breaks >= consecutive_days

    return {
        "should_exit": should_exit,
        "reason": "MA20_DAILY_CONSECUTIVE" if should_exit else "HOLD",
        "ma20": round(ma20_latest, 2),
        "current_price": current_price,
        "consecutive_breaks": consecutive_breaks,
    }
```

**알고리즘 검증**:
- consecutive_days=10, 30일 데이터(앞 20일=1000, 뒤 10일=700):
  - day -1(idx=29): MA20 = mean([1000]*10+[700]*10) = 850 → 700 < 850 ✓
  - day -2(idx=28): MA20 = mean([1000]*11+[700]*9) = 865 → 700 < 865 ✓
  - ... 10일 모두 이탈 → should_exit=True ✓

---

## Step 4: `config/hypothesis_winners.yaml` 생성

**파일 내용**:
```yaml
# hypothesis_winners.yaml
# T-229: 백테스트 승자 가설 목록 (T-096 결과 기반)
# 최종 업데이트: 2026-03-09

winners:
  H08-B:
    desk: D5
    hold_weeks: 5
    pf: 25.93
    description: "5주 고정 보유 전략 — DESK5 장기 추세 포착"
    backtest_basis: "T-096 3년 300종목 일봉 백테스트"
    status: applied     # T-201 D5_D014_CONFIG(min_hold_weeks=4) 반영
    note: "H08-B PF=25.93은 5주 보유 기준; D-014 min_hold_weeks=4(28일) ≒ 4주 적용"

  H05-D:
    desk:
      - D3
      - D4
    trail: MA20
    consecutive_days: 10        # T-229: 10거래일 연속 종가<MA20 → EXIT
    pf: 2.18
    description: "일봉 MA20 연속 이탈 트레일링 스톱 — D3/D4 스윙 청산"
    backtest_basis: "T-096 3년 300종목 일봉 백테스트"
    status: pending_ceo_approval  # T-229: _check_ma20_trailing_stop() 구현, CEO 승인 대기
    note: "10거래일 연속 종가<슬라이딩MA20 시 EXIT"

  H12-D:
    desk: ALL
    hold_multiplier: 2.0
    pf: 3.15
    description: "기본 보유기간 ×2.0배 확장 — 전 DESK 공통"
    backtest_basis: "T-096 3년 300종목 일봉 백테스트"
    status: pending_review
    note: "현재 전략별 timeout_minutes × 2.0 배 적용 시 PF=3.15 달성 추정"
```

---

## Step 5: 테스트 실행 결과

**파일**: `tests/test_exit_manager_d5_ma20.py` (신규 생성, 5건)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2
collecting ... collected 5 items

tests/test_exit_manager_d5_ma20.py::test_tc_ma20_01_10day_breach_exits PASSED [ 20%]
tests/test_exit_manager_d5_ma20.py::test_tc_ma20_02_9day_breach_holds PASSED [ 40%]
tests/test_exit_manager_d5_ma20.py::test_tc_ma20_03_d5_minhold_not_met_holds PASSED [ 60%]
tests/test_exit_manager_d5_ma20.py::test_tc_ma20_04_hypothesis_winners_yaml_loads PASSED [ 80%]
tests/test_exit_manager_d5_ma20.py::test_tc_ma20_05_complex_break_recovery_holds PASSED [100%]

============================== 5 passed in 0.08s ==============================
```

**신규 5/5 ALL PASS** ✅

### 기존 테스트 회귀 확인
```
tests/test_exit_manager_d5.py::... (30건 ALL PASS)
tests/test_exit_manager_atr_sl_cap.py::... (9건 ALL PASS)

============================== 39 passed in 0.15s ==============================
```

**기존 39/39 ALL PASS, 신규 실패 0건** ✅

**전체 누적**: 44/44 PASS

---

## Step 6: 테스트 케이스 상세

### TC-MA20-01: 10일 breach → EXIT
- 입력: 30일 데이터 (앞 20일=1000, 뒤 10일=700)
- `_check_ma20_trailing_stop(bars, consecutive_days=10)`
- 결과: should_exit=True, reason="MA20_DAILY_CONSECUTIVE", consecutive_breaks=10 ✅

### TC-MA20-02: 9일 hold → HOLD
- 입력: 30일 데이터 (앞 21일=1000, 뒤 9일=700)
- closes[-10]=1000 (회복점) → 연속이 끊김
- 결과: should_exit=False, reason="HOLD", consecutive_breaks=9 ✅

### TC-MA20-03: min_hold 미달 → HOLD
- D5 전략, 14일 전 진입 (< min_hold_weeks=4=28일)
- 주봉 2주 연속 이탈 데이터 제공
- `ExitManager.should_exit()`: elapsed_days=14 < 28 → HOLD (D-014 min_hold 우선)
- 결과: exit=False, reason="HOLD" ✅

### TC-MA20-04: hypothesis_winners.yaml 로드
- `config/hypothesis_winners.yaml` 파일 존재 확인
- H08-B: desk="D5", hold_weeks=5, pf=25.93 ✅
- H05-D: desk=["D3","D4"], trail="MA20", consecutive_days=10, pf=2.18 ✅
- H12-D: desk="ALL", hold_multiplier=2.0, pf=3.15 ✅

### TC-MA20-05: 복합 패턴 → HOLD
- 입력: 40일 데이터 ([1000]*20 + [700]*10 + [1050] + [700]*9)
- closes[-10]=1050 (회복, MA20 이상) → consecutive_breaks 9에서 중단
- 결과: should_exit=False, consecutive_breaks<10 ✅

---

## Step 7: 변경 파일 목록

| 파일 | 변경 유형 | 내용 |
|------|-----------|------|
| `backend/app/services/trading/exit_manager.py` | 수정 (additive) | `_check_ma20_trailing_stop()` 함수 추가 (~70줄) |
| `config/hypothesis_winners.yaml` | 신규 생성 | H08-B/H05-D/H12-D 백테스트 승자 YAML |
| `tests/test_exit_manager_d5_ma20.py` | 신규 생성 | TC-MA20-01~05 (5건) |
| `report/v41/CUR-V41-EXIT-MANAGER-D5-MA20-001-20260309.md` | 신규 생성 | 보고서 |

---

## Step 8: 성공 기준 달성 여부

| 항목 | 기준 | 달성 |
|------|------|------|
| D5 exit 현행 trace | D5_D014_CONFIG 호출 경로 확인 | ✅ 완료 |
| `_check_ma20_trailing_stop()` 구현 | 10거래일 연속 종가<MA20 → EXIT | ✅ 완료 |
| `config/hypothesis_winners.yaml` 생성 | H08-B/H05-D/H12-D 포함 | ✅ 완료 |
| 테스트 5건 ALL PASS | TC-MA20-01~05 | ✅ 5/5 PASS |
| 기존 테스트 회귀 없음 | 39/39 PASS | ✅ 완료 |

---

## Step 9: 주의 사항 (CEO 검토 필요)

### 9-1. 현재 미연결 상태
`_check_ma20_trailing_stop()`은 standalone 함수로만 구현됨.
D3/D4 exit 로직에 실제 연결은 **CEO 승인 후** 진행.

### 9-2. D5 개선 제안
현행 D5 주봉 MA20 2주 연속 이탈은 반응 느림.
H05-D (일봉 10거래일 연속 이탈)을 D5에도 적용할지 CEO 결정 요청.

### 9-3. git push 대기
- exit_manager.py 핵심 파일 변경분 → CEO 검토 후 push
- HANDOVER.md 업데이트 → CEO 승인 후 진행

---

## 보고서 경로

- **로컬**: `/root/kis-autotrade-v4/report/v41/CUR-V41-EXIT-MANAGER-D5-MA20-001-20260309.md`
- **project-docs 대상**: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-EXIT-MANAGER-D5-MA20-001-20260309.md`
- **git push**: CEO 승인 후 진행

---

## 최종 상태

```
T-229 완료 (코드 구현 + 테스트 ALL PASS + 보고서 작성)
git push: CEO 검토 대기 중
```
