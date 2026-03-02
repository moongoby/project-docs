# CUR-V41-SESSION-E2A-ANTIPATTERN-APPLY-001

**태스크 ID**: CUR-V41-SESSION-E2A-ANTIPATTERN-APPLY-001
**날짜**: 2026-03-02
**작성자**: Claude (Sonnet 4.6)
**분류**: 고도화 / 안티패턴 제거 / 리플레이 재검증

---

## [인계 확인]

```
직전 완료: CUR-V41-HISTORICAL-DATA-COMPLETE-001 (v4_market_regime_daily 843→1,116행 완성)
현재 단계: Phase E — 분봉 패턴 분석 & Anti-Pattern 제거
CEO 지시 적용: D-001(repo push), D-004(session naming)
strategy_cards: 조회 없음 (replay 전용 세션)
open_positions: 조회 없음 (replay 전용 세션)
```

---

## 1. 목적

Session E-1(CUR-V41-SESSION-E1-MINUTE-PATTERN-001)에서 발견한 **3개 Anti-Pattern** 즉시 차단 + CEO 승인 3건 파라미터 변경 + D7 PREV_DAY_CLOSE_RANK 필터를 코드에 적용하고, 동일 242거래일(2025-03-01 ~ 2026-02-27)로 리플레이 재검증.

---

## 2. 적용된 변경 사항 (6개 항목)

### 2-1. exit_simulator.py — CEO 승인 파라미터 변경

| 전략 | 파라미터 | 변경 전 | 변경 후 | 근거 |
|------|----------|---------|---------|------|
| D2 | trail_start | 0.020 | **0.100** | CEO: trail 활성화를 +10%로 상향 (조기 청산 방지) |
| D4 | sl_pct | 0.025 | **0.010** | CEO: 눌림확인 SL -1% |
| D4 | tp_pct | (없음) | **0.050** | CEO: TP +5% 신규 추가 |

**추가 구현**: D4 전용 HARD_TP 청산 모드 (`exit_reason="HARD_TP"`) — unrealized >= +5% 도달 시 전량 청산.

### 2-2. entry_detector.py — Anti-Pattern 3건 차단

**Anti-Pattern A (절대 금지): 장후반+거래량급감**
```python
@staticmethod
def _is_absolute_forbidden(minutes_from_open, volumes) -> bool:
    """장후반(>240분) + 거래량급감(<50%) 절대 금지.
    E-1 결과: 29건 PF=0.062."""
    if minutes_from_open <= 240: return False
    avg5 = sum(volumes[-5:]) / 5
    avg20 = sum(volumes[-20:]) / 20
    vol_ratio = avg5 / avg20 if avg20 > 0 else 1.0
    return vol_ratio < 0.5
```

**Anti-Pattern B (금지): 역배열+VWAP하회+거래량감소**
```python
@staticmethod
def _is_anti_pattern(closes, volumes, cum_vol_price, cum_vol, current_price) -> bool:
    """역배열(ma5<ma10<ma20) + VWAP하회 + 거래량감소 3조건 동시 충족.
    E-1 결과: 446건 PF=0.647."""
    ma5 = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10
    ma20 = sum(closes[-20:]) / 20
    reversed_ma = (ma5 < ma10) and (ma10 < ma20)
    vwap = cum_vol_price / cum_vol
    below_vwap = current_price < vwap
    avg5 = sum(volumes[-5:]) / 5
    avg20 = sum(volumes[-20:]) / 20
    vol_decreasing = avg5 < avg20 * 0.8 if avg20 > 0 else False
    return reversed_ma and below_vwap and vol_decreasing
```

**Anti-Pattern C (D5 장후반 금지)**:
- D5 진입 시간 상한: `time(15, 0)` → `time(13, 0)` (240분 초과 진입 차단)
- E-1 결과: 230건 PF=0.266 → 즉시 차단

**D4 진입 창 변경 (CEO 승인)**:
- 시작: `time(9, 15)` → `time(9, 25)` (갭 안정화 대기)
- 종료: `time(10, 0)` 이후 진입 차단 추가 (눌림 이후 초기 구간만)

### 2-3. candidate_scanner.py

| 전략 | 변경 내용 | 근거 |
|------|----------|------|
| D7 | `close_position >= 0.30` 추가 (하위 30% 제외) | E-1 PREV_DAY_CLOSE_RANK AUC=0.66, LOW구간 WR=21.1% |
| S1 | `change_pct >= 3.0` → `change_pct >= 5.0` | CEO 승인: 갭 필터 상향 |

### 2-4. strategy_params.py (CTE 파이프라인)

- S1 SignalPreset: `SIG1_VP_TURN` 제거 → `SIG8_BULLFLAG_BREAK` 추가
  - 기존: `[SIG1_VP_TURN, SIG3_YANGBONG, SIG6_VWAP_SUPPORT]`
  - 변경: `[SIG3_YANGBONG, SIG6_VWAP_SUPPORT, SIG8_BULLFLAG_BREAK]`
- E2A 상수 블록 추가: `E2A_D2_TRAIL_START_PCT`, `E2A_D4_*`, `E2A_S1_*`

---

## 3. 테스트 결과

### 3-1. CTE 파이프라인 테스트
```
26 passed (test_go100_minute_backtest.py + test_go100_backtest.py)
167 passed (전체 유닛/통합 테스트, DB 미연결 테스트 기준)
```

### 3-2. Anti-Pattern 필터 단위 테스트 (인라인)

| 케이스 | 입력 | 기대값 | 결과 |
|--------|------|--------|------|
| 역배열+VWAP하회+거래량감소 | ma5<ma10<ma20, price<vwap, avg5<avg20*0.8 | True | ✅ |
| 정상 상승추세 | ma5>ma10>ma20, price>vwap | False | ✅ |
| 장후반(241분)+거래량급감 | min=241, vol_ratio=0.33 | True | ✅ |
| 240분(미충족) | min=240 | False | ✅ |
| 장후반+거래량정상 | min=241, vol_ratio=1.0 | False | ✅ |
| D5 13:00 이전 | time(12,59) | 진입허용 | ✅ |
| D5 13:00 이후 | time(13,00) | 진입차단 | ✅ |

### 3-3. HARD_TP 검증
- D4 params: `sl_pct=0.010, trail_start=0.050, tp_pct=0.050`
- 시뮬레이션: 진입가 10,000 → bar idx=5에서 10,500 도달 → `exit_reason=HARD_TP` ✅

---

## 4. 리플레이 백테스트 결과 (242거래일)

**기간**: 2025-03-01 ~ 2026-02-27 | **초기자본**: 40,000,000원 | **비용**: 편도 0.47% (왕복)

### 4-1. 전략별 성과 (E-2A Full Apply)

| 전략 | N | WR% | PF | AvgW% | AvgL% | Sharpe | MDD% | 불안정 | 판정 |
|------|---|-----|----|-------|-------|--------|------|--------|------|
| D6 | 250 | 50.4 | **1.142** | 14.12 | 12.56 | 1.02 | -374.04 | 42% | FAIL |
| D5 | 696 | 33.2 | 0.573 | 2.21 | 1.92 | -5.16 | -380.54 | 100% | FAIL |
| D4 | 190 | 23.2 | 0.695 | 4.45 | 1.93 | -3.09 | -89.09 | 75% | FAIL |
| D7 | 387 | 32.0 | 0.734 | 1.83 | 1.17 | -2.30 | -94.39 | 75% | FAIL |
| D2 | 383 | 30.5 | 0.400 | 1.14 | 1.25 | -8.46 | -207.08 | 92% | FAIL |
| S1 | 129 | 31.8 | 0.380 | 1.23 | 1.51 | -8.28 | -82.53 | 100% | FAIL |
| **TOTAL** | **2,035** | **33.6** | **0.826** | 4.24 | 2.59 | -2.00 | -822.02 | 67% | FAIL |

**총 누적 수익률**: -610.89%

### 4-2. E-1 Baseline vs E-2A 비교

| 구분 | N | PF | 변화 |
|------|---|----|------|
| E-1 Baseline (Session D) | 1,929 | 0.834 | — |
| E-2A Full Apply | 2,035 | 0.826 | **-0.8pp (소폭 악화)** |

**기대 효과 미달 원인 분석**:

1. **D2 trail_start 2%→10% 역효과**: trail 활성화 조건이 +10%로 높아져 거의 활성화되지 않음. D2 청산: HARD_STOP 52건 + **TIMEOUT 331건** (총 383건 중 86%). 기존 trail_start=2%는 소폭 상승 구간도 보호했으나, 10%는 사실상 trail 기능 무력화.

2. **D5 구조적 부진 지속**: 13:00 차단 후에도 D5 696건, PF=0.573. 70% 이상이 TIMEOUT 청산. D5 자체의 진입 기준(뉴스 급등 +3~+20%)이 현재 시장에서 과도하게 많은 거래 발생.

3. **S1 PF 0.380**: 갭 5% 필터 적용 후에도 구조적 부진. TIMEOUT 117건(91%).

### 4-3. 청산 사유 분포

| 전략 | EOD | HARD_STOP | HARD_TP | NEXT_OPEN | TIMEOUT | TIME_CLOSE |
|------|-----|-----------|---------|-----------|---------|------------|
| D6 | 0 | 0 | 0 | 250 | 0 | 0 |
| D5 | 1 | 167 | 0 | 0 | 526 | 2 |
| D4 | 0 | 139 | **32** | 0 | 19 | 0 |
| D7 | 0 | 0 | 0 | 387 | 0 | 0 |
| D2 | 0 | 52 | 0 | 0 | 331 | 0 |
| S1 | 0 | 12 | 0 | 0 | 117 | 0 |

**주목**: D4 HARD_TP 32건 확인 — TP+5% 기능 정상 작동.

---

## 5. Walk-Forward 3-Fold 검증

**방법**: 242거래일을 3등분하여 각 구간의 PF 일관성 확인

| Fold | 기간 | 거래일 | N | PF | cumPnL% |
|------|------|--------|---|----|---------|
| Fold 1 | 2025-03-01 ~ 2025-07-25 | ~80일 | 801 | 0.730 | -497.38 |
| Fold 2 | 2025-07-28 ~ 2025-11-14 | ~80일 | 646 | 0.664 | -210.08 |
| Fold 3 | 2025-11-17 ~ 2026-02-27 | ~82일 | 577 | **1.096** | +99.13 |

**Fold별 전략 성과**:

| 전략 | Fold1 PF | Fold2 PF | Fold3 PF | 해석 |
|------|----------|----------|----------|------|
| D6 | 0.892 | **1.478** | **1.707** | 후반으로 갈수록 개선 |
| D5 | 0.435 | 0.630 | 0.725 | 일관되게 부진, 개선 추세는 있음 |
| D4 | 0.703 | **1.383** | 0.499 | Fold2 양호, Fold3 급락 |
| D7 | 0.660 | 0.717 | 0.825 | 점진적 개선 |
| D2 | 0.315 | 0.475 | 0.407 | 일관되게 부진 |
| S1 | 0.593 | 0.324 | 0.285 | 악화 추세 |

**Walk-Forward 결론**:
- **비정상성(Non-Stationarity) 확인**: Fold 1-2 부진 → Fold 3 반등, 시장환경 의존도 높음
- **D6만 일관된 상승 추세**: 오버나이트 전략으로 구조적 강점
- **D2/S1 구조적 약점**: 3개 Fold 모두 PF<0.6, 근본적 재검토 필요

---

## 6. 핵심 발견

### F-1: D2 trail_start=10% 역효과 (즉시 주목)
- CEO 승인 변경이었으나 역효과 확인
- D2 TIMEOUT 비율 331/383 = 86%로 급증
- **권고**: D2 trail_start를 2~5% 범위로 재실험 필요
- 다음 세션에서 반드시 검토

### F-2: D5 구조적 부진 지속
- 13:00 차단 적용 후에도 696건, PF=0.573
- D5 진입 기준(뉴스+등락률 3~20%)이 과도하게 많은 거래 생성
- TIMEOUT이 75%(526/696)로 진입 타이밍 문제
- **권고**: D5 등락률 하한 상향(5%→8%) 또는 volume surge 추가 조건

### F-3: D6 일관성 확인
- Fold1=0.892, Fold2=1.478, Fold3=1.707 (지속 개선)
- 오버나이트 NEXT_OPEN 청산 100% — 갭 상승 구조 활용
- **권고**: D6에 리소스 집중, 포지션 한도 확대 검토

### F-4: D4 HARD_TP 효과 확인
- 32건 HARD_TP 발생 → CEO 승인 TP+5% 정상 작동
- Fold2 PF=1.383으로 일부 기간 유효
- SL-1% 조합이 좁은 구간에서만 유효함 확인

---

## 7. 코드 변경 파일 목록

| 파일 | 변경 내용 |
|------|----------|
| `backend/app/services/unified_engine/replay/exit_simulator.py` | D2 trail_start 0.020→0.100, D4 sl_pct 0.025→0.010 + tp_pct=0.050, HARD_TP 청산 모드 추가 |
| `backend/app/services/unified_engine/replay/entry_detector.py` | D5 13:00 차단, D4 09:25-10:00 창, `_is_anti_pattern()`, `_is_absolute_forbidden()` 추가 |
| `backend/app/services/unified_engine/replay/candidate_scanner.py` | D7 close_position>=0.30, S1 change_pct>=5.0 |
| `backend/app/services/trading/cte/strategy_params.py` | S1 SIG8 추가, E2A 상수 블록 |

---

## 8. 다음 세션 (E-3) 작업 항목

| 우선순위 | 항목 | 내용 |
|----------|------|------|
| P0 | D2 trail_start 재검토 | 현재 0.100 역효과 확인. 0.030~0.050 범위 실험 |
| P0 | D5 진입 기준 강화 | change_pct 하한 5%→8%, VWAP 지지 조건 추가 |
| P1 | D6 집중화 | D6 포지션 한도 OVERNIGHT_LIMIT 4→6 실험 |
| P1 | S1 전면 재검토 | 3개 Fold 모두 PF<0.6, 신호 체계 재설계 |
| P2 | D7 추가 필터 | close_position 0.30→0.50 상향 실험 |

---

## 9. 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4, 4개 파일)
- [x] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)
