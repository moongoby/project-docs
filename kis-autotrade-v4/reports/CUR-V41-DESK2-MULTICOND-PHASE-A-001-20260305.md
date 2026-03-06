# CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305

[인계 확인]
직전 완료: T-124 (03-06 사전점검 9/9 PASS)
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-010 (DESK2 멀티컨디션 엔진), D-011 (PF 우선순위 기준)
strategy_cards: 60
open_positions: 14

---

## T-125: DESK2 멀티컨디션 Phase A — C2(D4전상눌림) / C1(D6상따갭) / C6(D7종가배팅갭)

**작성일**: 2026-03-05 19:40 KST
**커밋**: bca18a1e
**브랜치**: phase-2c-command-center
**테스트**: 20/20 ALL PASS

---

## 1. 배경 및 목적

CEO D-010 지시에 따라 DESK2 멀티컨디션 엔진을 구축한다.
VE-003 Phase A 대상: D4(전상눌림), D6(상따→갭), D7(종가배팅→갭).
D-011 기준 우선순위: D6(PF13.63) > D4(PF2.43) > D7(PF2.12).

---

## 2. 구현 내용

### 2-1. config/param_search_space.yaml — desk2_conditions 섹션 추가

```yaml
desk2_conditions:
  c2_prev_ul:                    # C2: 전일 상한가 (D4용)
    ul_pct_min: 29.0
    next_day_ma20_1m_break: true
    timeout_minutes: 60
    sl_pct: 2.0
    tp_pct: 3.0
  c1_ul_expected:                # C1: 상한가 예상 (D6용)
    ul_entry_before: "11:00"
    bid_amount_min: 10000000000  # 100억
    sl_pct: 1.0
    tp_pct: 0.0                  # 시간외 매도
  c6_close_strong:               # C6: 종가 강세 (D7용)
    entry_after: "14:30"
    close_bet_conditions:
      supply_focus: true
      low_rising: true
      volume_increase: true
    sl_pct: 1.5
    next_day_open_sell: true
```

### 2-2. backend/app/services/desk2_conditions/ 패키지 (6파일)

| 파일 | 역할 |
|------|------|
| `__init__.py` | 패키지 노출 (6 클래스) |
| `base_condition.py` | BaseCondition ABC — evaluate/backtest_signal/get_params + YAML 로더 |
| `c2_prev_ul.py` | C2PrevULCondition — 전일 상한가 판별 + 1분봉 MA20 돌파 감지 |
| `c1_ul_expected.py` | C1ULExpectedCondition — 상한가 예상(시간대 + 매수잔량 100억+) |
| `c6_close_strong.py` | C6CloseStrongCondition — 종가 강세 3조건 AND (수급/저점/거래량) |
| `condition_registry.py` | ConditionRegistry — 등록/evaluate_all/evaluate_single/get_active_conditions |
| `signal_matcher.py` | SignalMatcher — D-011 기준 Top5 매칭 (match_signal/match_all/get_top5_priority) |

### 2-3. 컨디션 상세 구현

**C2PrevULCondition (D4 전상눌림)**
- `evaluate(symbol, date, prev_open, prev_close, ohlcv_1m)` → triggered/confidence/details
- 로직: `prev_close >= prev_open × 1.29` → 상한가 판별
- 1분봉 20MA 돌파 감지: `close[i] > MA20 AND close[i-1] <= MA20`
- timeout_minutes=60 이내 돌파 시만 triggered=True

**C1ULExpectedCondition (D6 상따갭)**
- `evaluate(symbol, date, current_time, bid_amount)` → triggered/confidence/bid_amount
- 로직: `current_time < 11:00` AND `bid_amount >= 100억`
- 시간 파싱 실패 → False (안전 fallback)

**C6CloseStrongCondition (D7 종가배팅갭)**
- `evaluate(symbol, date, current_time, supply_focus, low_rising, volume_increase)`
- 로직: `current_time >= 14:30` AND (수급집중 AND 저점상승 AND 거래량증가)
- close_bet_conditions YAML 설정으로 각 조건 on/off 가능

### 2-4. SignalMatcher D-011 기준

| 컨디션 | 1순위 시그널 | 2순위 시그널 | PF (D-011) |
|--------|------------|------------|-----------|
| C1 (D6) | TS-D1 (미니갭) | TS-B1 (RSI30~50) | 13.63 ★ |
| C2 (D4) | TS-B4 (거래량폭발양봉) | TS-C3 (20봉신고가) | 2.43 |
| C6 (D7) | TS-C1 (5봉거래집중) | — | 2.12 |

---

## 3. 테스트 결과

```
============================= test session info ==============================
파일: tests/unit/test_desk2_conditions.py
수행: /root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/test_desk2_conditions.py -v

tests/unit/test_desk2_conditions.py::test_c2_upper_limit_true            PASSED
tests/unit/test_desk2_conditions.py::test_c2_upper_limit_false           PASSED
tests/unit/test_desk2_conditions.py::test_c2_ma20_break_detected         PASSED
tests/unit/test_desk2_conditions.py::test_c2_missing_data_fallback       PASSED
tests/unit/test_desk2_conditions.py::test_c1_upper_limit_with_bid_true   PASSED
tests/unit/test_desk2_conditions.py::test_c1_time_filter_after_11        PASSED
tests/unit/test_desk2_conditions.py::test_c1_insufficient_bid_amount     PASSED
tests/unit/test_desk2_conditions.py::test_c6_close_strong_all_conditions_true PASSED
tests/unit/test_desk2_conditions.py::test_c6_time_filter_before_1430     PASSED
tests/unit/test_desk2_conditions.py::test_c6_partial_conditions_false    PASSED
tests/unit/test_desk2_conditions.py::test_condition_registry_register_and_evaluate PASSED
tests/unit/test_desk2_conditions.py::test_signal_matcher_basic           PASSED
tests/unit/test_desk2_conditions.py::test_condition_params_yaml_load     PASSED
tests/unit/test_desk2_conditions.py::test_five_axis_time_mask_structure  PASSED
tests/unit/test_desk2_conditions.py::test_dcs_daily_sum_structure        PASSED
tests/unit/test_desk2_conditions.py::test_signal_matcher_top5_and_match_all PASSED
tests/unit/test_desk2_conditions.py::test_c2_get_params_structure        PASSED
tests/unit/test_desk2_conditions.py::test_registry_evaluate_single_missing PASSED
tests/unit/test_desk2_conditions.py::test_c1_backtest_signal_basic       PASSED
tests/unit/test_desk2_conditions.py::test_c6_backtest_signal_basic       PASSED

============================== 20 passed in 0.14s ==============================
```

중간 실패 수정: TC-03 `test_c2_ma20_break_detected` — `_detect_ma20_break`에서 `i=20`일 때 `closes[-1:19]`가 빈 배열이 되는 버그.
수정: `ohlcv_1m[i-1]["close"] <= (sum(closes[i-21:i-1])/20)` → `closes[i-1] <= ma20` (단순 크로스오버 조건으로 변경).

---

## 4. 버그 수정 이력

| 위치 | 원인 | 수정 내용 |
|------|------|---------|
| c2_prev_ul.py `_detect_ma20_break()` | i=20에서 `closes[-1:19]` 빈 슬라이스 → prev_ma20=0.0 | `closes[i-1] <= ma20` 단순화 |

---

## 5. 완료 조건 체크

- [x] desk2_conditions 패키지 6파일 생성
- [x] C2/C1/C6 컨디션 3개 구현 (evaluate + backtest_signal + get_params)
- [x] ConditionRegistry 구현 (register/evaluate_all/get_active_conditions)
- [x] SignalMatcher 구현 (match_signal/match_all/get_top5_priority)
- [x] 20개 테스트 ALL PASS (요구: 12+)
- [x] git commit bca18a1e
- [ ] git push origin phase-2c-command-center (SSH 권한 — root 수행 필요)
- [ ] project-docs 보고서 push (root 수행 필요)
- [ ] HANDOVER.md 갱신 (root 수행 필요)

---

## 6. Root 수행 필요 작업

```bash
# 1. 코드 push
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center

# 2. project-docs 보고서 복사 + push
cp /root/kis-autotrade-v4/report/v41/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md \
   /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md
cd /root/project-docs
git add -A
git commit -m "[DOCS] T-125 DESK2 멀티컨디션 Phase A 보고서"
git push origin master

# 3. HTTP 200 확인
curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-DESK2-MULTICOND-PHASE-A-001-20260305.md"
```

---

## 7. 핵심 발견

1. **D-011 C1 최우선**: C1(D6 상따갭, PF13.63)이 3개 컨디션 중 압도적 우선순위.
   TS-D1(미니갭) + bull 시장 조합이 최고 점수(0.85+0.2=1.05).
2. **C2 MA20 돌파 감지**: `closes[i-1] <= ma20` 방식이 종가 기반 크로스오버로 충분.
   첫 번째 가능 인덱스(i=20)에서도 정확 동작 확인.
3. **ConditionRegistry 설계**: evaluate_all에서 각 컨디션 오류를 catch하여 전체 평가 중단 방지.
   graceful fallback 패턴이 운영 환경에 필수.
4. **5축 마스크 T6(14:30~15:30)**: C6는 T6 시간대에서만 활성화됨을 TC-14로 검증.
5. **DCS 일일합산**: triggered 컨디션의 confidence 합산으로 일일 강도 측정 가능.

---

## 8. 다음 단계 (Phase B)

- D4/D6/D7 실 데이터 백테스트 (1분봉 vs DB)
- ConditionRegistry → CTE Pipeline 연동 (L2.5 또는 L3 레벨)
- C2 `backtest_signal` 실 1분봉 데이터 검증
- D-011 PF 재검증 (Phase A 컨디션 기반)
