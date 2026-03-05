---
project: KIS-AutoTrade-V4.1
task_id: T-097
report_id: CUR-V41-CONFIRMATION-ENTRY-001-20260305
date: 2026-03-05
version: v9.6
---

[인계 확인]
직전 완료: T-096 (12가설 백테스트 프레임워크)
현재 단계: Phase 2C — Command Center
CEO 지시 적용: D-001 (단순사고금지), D-002 (수급본질), D-003 (DESK=풀관리)
strategy_cards: 60
open_positions: 14

---

# T-097 보고서: 확인매매 엔진 — 최저점 확인 진입 + H08/H05/H09 승자 적용

## 요약

CEO 7대 원칙 "최저점을 확인하고 진입한다. 손절은 최저점으로 잡는다"를 실행 모듈로 구현.
T-096 12가설 결과에서 확인된 승자 전략(H08/H05/H09/H12)을 param_search_space.yaml에 반영.

---

## 작업 1: ConfirmationEntryEngine 신규 생성

**파일**: `backend/app/services/confirmation_entry_engine.py`

### 구현 내용

```
class ConfirmationEntryEngine:
    def find_recent_low(symbol, lookback_days, conn) → Optional[LowInfo]
    def confirm_bottom(symbol, low_info, bounce_pct, vol_multiplier) → bool
    def calculate_risk_reward(entry, low, desk) → (sl, tp, rr, action)
    def generate_entry_signal(symbol, desk, ...) → EntrySignal
```

### 4메서드 상세

#### find_recent_low
- `ohlcv_daily` 테이블에서 최근 N일 일봉 조회
- 최신봉 제외 historical 중 최저가 탐색
- `investor_daily`에서 외인/기관 순매수 조회 (없으면 0)
- 반환: LowInfo(low_price, low_date, current_price, current_volume, avg_volume, foreign_net, inst_net, is_bullish, prev_close)

#### confirm_bottom (4조건 AND)
| 조건 | 내용 |
|------|------|
| C1 | 현재봉 양봉 (close > open) |
| C2 | 최저점 대비 현재가 반등 ≥ bounce_pct |
| C3 | 현재 거래량 ≥ 평균 거래량 × vol_multiplier (기본 1.5) |
| C4 | 외인 순매수 > 0 OR 기관 순매수 > 0 |

4조건 모두 AND → True, 하나라도 미충족 → False

#### calculate_risk_reward
- `SL = low × 0.99` (최저점 1% 아래)
- `TP = entry × (1 + DESK_TP_RATIO[desk])`
- `RR = (TP - entry) / (entry - SL)`
- RR < min_rr → REJECT
- DESK별 min_rr: DESK5=5.0 / DESK4=2.5 / DESK3=2.0 / DESK2=1.5
- DESK별 TP 비율: DESK5=100% / DESK4=25% / DESK3=20% / DESK2=10%

#### generate_entry_signal
파이프라인:
1. find_recent_low → None이면 WAIT (데이터 부족)
2. confirm_bottom → False이면 WAIT (바닥 확인 미충족)
3. calculate_risk_reward → REJECT이면 REJECT (손익비 불충분)
4. → ENTRY (4조건 충족 + 손익비 통과)

DESK별 기본 파라미터:
| DESK | lookback | bounce | min_rr |
|------|----------|--------|--------|
| DESK5 | 20일 | 3% | 5.0 |
| DESK4 | 10일 | 2% | 2.5 |
| DESK3 | 5일 | 2% | 2.0 |
| DESK2 | 3일 | 1% | 1.5 |

---

## 작업 2: param_search_space.yaml — confirmation_entry 섹션 추가

**파일**: `config/param_search_space.yaml`

```yaml
confirmation_entry:
  desk5:
    lookback: 20
    min_confirm: 4
    min_rr: 5.0
    bounce: 0.03
  desk4:
    lookback: 10
    min_confirm: 3
    min_rr: 2.5
    bounce: 0.02
  desk3:
    lookback: 5
    min_confirm: 3
    min_rr: 2.0
    bounce: 0.02
  desk2:
    lookback: 3
    min_confirm: 2
    min_rr: 1.5
    bounce: 0.01
```

---

## 작업 3: param_search_space.yaml — hypothesis_winners 섹션 추가

T-096 결과 기반 승자 전략:

| 가설 | 승자 | 결과 | 적용값 |
|------|------|------|--------|
| H08 (급등후 보유기간) | B (5주) | PF=25.93, WR=87.6% | h08_desk5_min_hold_weeks: 5 |
| H05 (3파 청산) | D (MA20 트레일링) | PF=2.18 | h05_desk3_exit_method: "ma20_trailing" |
| H09 (거래량급감 후 청산) | C (2일 후) | PF=2.35 | h09_exit_delay_days: 2 |
| H12 (파이프라인 보유배율) | D (2.0배) | PF=3.15 | h12_desk5_hold_multiplier: 2.0 |

```yaml
hypothesis_winners:
  h08_desk5_min_hold_weeks: 5
  h05_desk3_exit_method: "ma20_trailing"
  h09_exit_delay_days: 2
  h12_desk5_hold_multiplier: 2.0
```

---

## 작업 4: 단위테스트 9건 ALL PASS

**파일**: `tests/test_confirmation_entry.py`

```
tests/test_confirmation_entry.py::test_find_recent_low_returns_low_info         PASSED
tests/test_confirmation_entry.py::test_confirm_bottom_all_conditions_met         PASSED
tests/test_confirmation_entry.py::test_confirm_bottom_fails_when_not_bullish     PASSED
tests/test_confirmation_entry.py::test_confirm_bottom_fails_when_volume_low      PASSED
tests/test_confirmation_entry.py::test_calculate_risk_reward_below_min_rr_rejected PASSED
tests/test_confirmation_entry.py::test_calculate_risk_reward_desk5_passes        PASSED
tests/test_confirmation_entry.py::test_generate_entry_signal_returns_entry       PASSED
tests/test_confirmation_entry.py::test_generate_entry_signal_returns_reject_on_low_rr PASSED
tests/test_confirmation_entry.py::test_yaml_confirmation_entry_params_loaded     PASSED

9 passed in 0.13s
```

**커버리지**:
- find_recent_low: DB mock 정상 반환 검증
- confirm_bottom 충족: 4조건 모두 True → True
- confirm_bottom 미충족: 음봉(C1 실패) → False
- confirm_bottom 미충족: 거래량 부족(C3 실패) → False
- calculate_risk_reward RR<min: DESK2 RR=1.04 < 1.5 → REJECT
- calculate_risk_reward DESK5 통과: RR=50.5 ≥ 5.0 → OK
- generate_entry_signal ENTRY: DESK5 4조건+RR≥5.0 → ENTRY
- generate_entry_signal REJECT: DESK2 RR<1.5 → REJECT
- YAML 로드: confirmation_entry + hypothesis_winners 섹션 존재 확인

---

## 작업 5: HANDOVER.md v9.6 갱신

HANDOVER.md 업데이트 내용:
- 헤더 v9.5 → v9.6 + T-097 요약 추가
- 섹션 2 "완료된 작업" 테이블 T-097 행 추가
- 섹션 6 "최신 상태" v9.6 추가 (T-097 완료 현황)
- 버전 이력 v9.6 행 추가

**주의**: claudebot 권한 제약으로 git commit 직접 실행 불가 → done_watcher.sh가 처리

---

## 완료 기준 체크

| 기준 | 상태 |
|------|------|
| confirmation_entry_engine.py 생성, 4메서드 구현 | ✅ DONE |
| param_search_space.yaml confirmation_entry 섹션 추가 | ✅ DONE |
| param_search_space.yaml hypothesis_winners 섹션 추가 | ✅ DONE |
| 9건 테스트 ALL PASS | ✅ 9/9 PASS (0.13s) |
| HANDOVER.md v9.6 갱신 | ✅ 파일 수정 완료 (git push → done_watcher 처리) |
| 보고서 CUR-V41-CONFIRMATION-ENTRY-001-20260305.md | ✅ 작성 완료 |

---

## 코드 레포 커밋 대상 파일

```
?? backend/app/services/confirmation_entry_engine.py    (신규)
?? tests/test_confirmation_entry.py                     (신규)
M  config/param_search_space.yaml                       (수정: confirmation_entry + hypothesis_winners 섹션 추가)
```

HANDOVER.md 업데이트 완료: (done_watcher.sh 처리 예정)
