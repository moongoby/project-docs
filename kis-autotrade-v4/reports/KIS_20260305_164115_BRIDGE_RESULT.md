---
project: kis-autotrade-v4
task_id: T-112
completed_at: 2026-03-05T17:05:00+09:00
---

# T-112 SEC_LEADER_FLAG v2 구현 결과 보고서

## 인계 확인
- 직전 완료: T-111 (DUAL_FLOW 기관+외국인 동시 순매수 피처)
- 현재 단계: Phase 2C Command Center
- CEO 지시 적용: D-008-KR §2-4
- 작업 전 상태: branch=phase-2c-command-center

---

## A. 백업 완료

```
backend/app/services/feature_engine.py.bak.20260305_1656
backend/app/services/funnel_score_engine.py.bak.20260305_1656
config/param_search_space.yaml.bak.20260305_1656
```

---

## B. SecLeaderV2Engine 구현

**파일**: `backend/app/services/feature_engine.py` (끝에 추가)

### 추가된 함수/클래스

#### `_load_sec_leader_v2_params()`
- `param_search_space.yaml`의 `sec_leader_v2` 섹션 로드
- 실패 시 빈 dict 반환 (기본값 사용)

#### `class SecLeaderV2Engine`

**`__init__(params=None)`**
- `_rs_threshold`: 80 (RS 기준선)
- `_rs_period_days`: 60 (RS 계산 기간)
- `_crash_lookback_days`: 20 (폭락 탐지 기간)
- `_crash_recovery_pct`: 5.0 (KOSPI 회복 기준 %)
- `_w_rs`: 0.4, `_w_trade_rank`: 0.3, `_w_first_breakout`: 0.3

**`_fetch_sector_code(symbol) → Optional[str]`**
- `v4_sector_mapping`에서 `krx_sector_code` 조회
- None 반환 시 기본값 반환

**`_fetch_trade_amount_rank(symbol, sector_code, date_str) → int`**
- 섹터 피어 목록 → `ohlcv_daily`에서 당일 거래대금 순위
- 1 = 최고, 0 = 데이터 없음

**`_calc_rs_score(symbol, date_str, sector_code) → float`**
- 섹터 피어 내 60일 수익률 백분위 (0~100)
- 기본값 50.0

**`_check_first_breakout_after_crash(symbol, date_str) → bool`**
- `v4_macro_daily`에서 KOSPI 20일 최저 대비 +5% 회복 확인
- `ohlcv_daily`에서 52주 신고가(현재가 >= 252일 최고가) 확인

**`calculate_sec_leader_v2(symbol, date=None) → dict`**
```python
# leader_score 계산
rs_component    = w_rs        if rs_score > 80    else 0.0  # 0.4
rank_component  = w_trade_rank if trade_rank == 1 else 0.0  # 0.3
break_component = w_first_breakout if first_breakout else 0.0  # 0.3

leader_score = rs_component + rank_component + break_component  # 0.0 ~ 1.0
is_leader_v2 = leader_score >= 0.3  # 최소 1가지 조건 충족

return {
    'is_leader_v2': bool,
    'rs_score': float,
    'trade_amount_rank': int,
    'is_first_breakout': bool,
    'leader_score': float 0~1
}
```

---

## C. YAML 파라미터 추가

**파일**: `config/param_search_space.yaml` (끝에 추가)

```yaml
sec_leader_v2:
  rs_threshold: 80
  rs_period_days: 60
  crash_lookback_days: 20
  crash_recovery_pct: 5.0
  score_weights: { rs: 0.4, trade_rank: 0.3, first_breakout: 0.3 }
```

---

## D. FunnelScore L1 연동

**파일**: `backend/app/services/funnel_score_engine.py`

**변경 위치**: `score_l1()` 메서드 내 SEC_LEADER 로직

```python
# 변경 전 (v1):
sec_leader_bonus = leader_bonus if rs > rs_threshold else 0.0

# 변경 후 (v2):
sec_leader_bonus = 0.0
try:
    from backend.app.services.feature_engine import SecLeaderV2Engine
    _sl_engine = SecLeaderV2Engine()
    _sl_result = _sl_engine.calculate_sec_leader_v2(symbol, date)
    if _sl_result.get("is_leader_v2"):
        sec_leader_bonus = leader_bonus  # +0.3
except Exception as e:
    logger.warning("L1[%s]: SEC_LEADER_V2 조회 실패: %s → RS fallback", symbol, e)
    sec_leader_bonus = leader_bonus if rs > rs_threshold else 0.0  # fallback
```

- SEC_LEADER v2 통과(is_leader_v2=True) 시 `leader_bonus` 0.3 가산
- 조회 실패 시 v1 RS 기반 fallback

---

## E. 단위 테스트 결과

**파일**: `tests/unit/test_sec_leader_v2.py`

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
collecting ... collected 7 items

tests/unit/test_sec_leader_v2.py::TestSecLeaderV2::test_trade_amount_rank_1       PASSED [ 14%]
tests/unit/test_sec_leader_v2.py::TestSecLeaderV2::test_rs_above_80               PASSED [ 28%]
tests/unit/test_sec_leader_v2.py::TestSecLeaderV2::test_rs_below_80               PASSED [ 42%]
tests/unit/test_sec_leader_v2.py::TestSecLeaderV2::test_first_breakout_after_crash PASSED [ 57%]
tests/unit/test_sec_leader_v2.py::TestSecLeaderV2::test_no_crash_no_breakout      PASSED [ 71%]
tests/unit/test_sec_leader_v2.py::TestSecLeaderV2::test_leader_score_integration  PASSED [ 85%]
tests/unit/test_sec_leader_v2.py::TestSecLeaderV2::test_no_sector_mapping         PASSED [100%]

============================== 7 passed in 0.09s ===============================
```

**결과: 7/7 ALL PASS** ✅

---

## F. git 커밋

**커밋 해시**: `b81c5817`
**브랜치**: `phase-2c-command-center`
**커밋 메시지**:
```
[V4.1] T-112: SEC_LEADER_FLAG v2 대장주 판별 강화

- SecLeaderV2Engine: 거래대금1위(홍인기) + 폭락후돌파(남석관) + RS>80(미너비니) 3조건
- leader_score = (rs>80)*0.4 + (rank==1)*0.3 + (first_breakout)*0.3
- FunnelScore L1 score_l1() 연동: is_leader_v2=True 시 leader_bonus 0.3 가산
- param_search_space.yaml: sec_leader_v2 섹션 추가
- tests: 7/7 ALL PASS
```

**git push 상태**: claudebot SSH 키 없음 → `git push origin phase-2c-command-center` 실패
- 로컬 커밋은 완료 (b81c5817)
- root 계정에서 수동 push 필요: `cd /root/kis-autotrade-v4 && git push origin phase-2c-command-center`

---

## G. 완료 기준 체크리스트

| 항목 | 상태 | 비고 |
|------|------|------|
| ① `calculate_sec_leader_v2()` 구현 | ✅ | feature_engine.py SecLeaderV2Engine |
| ② YAML 파라미터 추가 | ✅ | sec_leader_v2 섹션 |
| ③ FunnelScore L1 연동 | ✅ | score_l1() leader_bonus 0.3 가산 |
| ④ 단위 테스트 7/7 PASS | ✅ | 0.09s |
| ⑤ 코드 커밋 | ✅ | b81c5817 |
| ⑥ git push | ⚠️ | SSH 키 없음 - root 수동 push 필요 |
| ⑦ 서비스 재시작 | 🚫 | 지시서 명시: 재시작 금지 |
| ⑧ .bak 파일 커밋 금지 | ✅ | 스테이징에서 제외됨 |

---

## 비고

- 변경 파일 목록:
  - `backend/app/services/feature_engine.py` (+200행)
  - `backend/app/services/funnel_score_engine.py` (+10행, -2행)
  - `config/param_search_space.yaml` (+10행)
  - `tests/unit/test_sec_leader_v2.py` (신규, +130행)
- `.bak` 파일 3개 생성 (커밋 미포함)
- 서비스 재시작 금지 준수
