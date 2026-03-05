---
project: kis-autotrade-v4
task_id: T-117
completed_at: 2026-03-05T18:02:28 KST
---

# T-117: D_D1_D2_ENTRY 장대양봉 D+1 전략 카드 구현 — 실행 결과

## 1. 사전 작업 — 백업

```
cp backend/app/services/feature_engine.py backend/app/services/feature_engine.py.bak.$(date +%Y%m%d_%H%M)
cp config/param_search_space.yaml config/param_search_space.yaml.bak.$(date +%Y%m%d_%H%M)
cp backend/app/services/trading/cte/cte_pipeline.py backend/app/services/trading/cte/cte_pipeline.py.bak.$(date +%Y%m%d_%H%M)
```
결과: 백업 완료

---

## 2. config/param_search_space.yaml — d_d1_d2_entry 섹션 추가

파일: `/root/kis-autotrade-v4/config/param_search_space.yaml` 맨 끝에 추가됨.

추가된 내용:
```yaml
# ────────────────────────────────────────────────────────────
# T-117: D_D1_D2_ENTRY 장대양봉 D+1/D+2 전략 진입 파라미터
# CEO D-008-KR §3-3. 홍인기 전략 — 장대양봉 당일(D)/D+1/D+2 진입 패턴
# DDayEntryEngine에서 사용
# ────────────────────────────────────────────────────────────
d_d1_d2_entry:
  big_yang_pct: 7.0       # 장대양봉 기준: 종가/시가 ≥ 7%
  volume_ratio: 2.5       # 전일 대비 거래량 2.5배
  d1_pullback_max: -5.0   # D+1 최대 하락 -5% (넘으면 진입 불가)
  d1_support_ma: 5        # D+1 5일선 지지 확인
  d2_pullback_max: -3.0   # D+2 최대 하락 -3%
  d2_support_ma: 10       # D+2 10일선 지지
  sl_pct: 2.0             # 손절: -2%
  tp_pct: 5.0             # 익절: +5%
  timeout_minutes: 120    # 보유 제한: 120분
  leader_only: true       # SEC_LEADER_FLAG v2 종목만 대상
  min_trade_amount: 5000000000  # 최소 거래대금 50억
```

---

## 3. backend/app/services/feature_engine.py — DDayEntryEngine 클래스 추가

파일 끝에 추가됨.

### 추가된 함수/클래스

#### `_load_d_d1_d2_params() → Dict`
YAML에서 `d_d1_d2_entry` 섹션 로드. 실패 시 빈 dict 반환.

#### `class DDayEntryEngine`
생성자 파라미터: `big_yang_pct, volume_ratio, d1_pullback_max, d1_support_ma, d2_pullback_max, d2_support_ma, sl_pct, tp_pct, timeout_minutes, leader_only, min_trade_amount`

메서드:
- `_fetch_ohlcv_rows(symbol, date, limit)` — DB 조회 (테스트 mock 가능)
- `_calc_ma(closes, period)` — 단순이동평균 계산
- `detect_big_yang(symbol, date)` → `{is_big_yang, pct_change, volume_ratio, trade_amount}`
  - 조건: (close-open)/open×100 ≥ 7% AND vol_today/vol_prev ≥ 2.5배 AND trade_amount ≥ 50억
- `evaluate_d1_entry(symbol, date)` → `{is_valid, pullback_pct, ma5_support, entry_price}`
  - 조건: pullback ≥ -5% AND close ≥ MA5
- `evaluate_d2_entry(symbol, date)` → `{is_valid, pullback_pct, ma10_support, entry_price}`
  - 조건: pullback ≥ -3% AND close ≥ MA10
- `generate_dday_signal(symbol, date, day_offset=0|1|2, is_leader=True)` → `{action, day_type, sl, tp, timeout, reason}`
  - day_offset=0: 장대양봉 감지 후 WAIT 반환 (D+1/D+2 대기)
  - day_offset=1: D+1 조건 충족 시 ENTRY (sl=entry_price×0.98, tp=entry_price×1.05)
  - day_offset=2: D+2 조건 충족 시 ENTRY (sl=entry_price×0.98, tp=entry_price×1.05)
  - leader_only=True AND is_leader=False → REJECT

---

## 4. backend/app/services/trading/cte/cte_pipeline.py — L2.5 삽입

### TradeSignal 필드 추가
```python
# ── L2.5 D-Day 장대양봉 후보 (T-117) ─────────
is_dday_candidate: bool = False
dday_signal_result: Optional[Dict] = field(default=None)
```

### PipelineResult 필드 추가
```python
# ── L2.5 D-Day 장대양봉 (T-117) ──────────
is_dday_candidate: bool = False
dday_action: str = "SKIP"
dday_day_type: str = ""
```

### evaluate() 메서드 L2.5 삽입 (L2 쿨다운 후, L3 종목한도 전)
```python
# ── L2.5: D-Day 장대양봉 후보 체크 (T-117) ──
if signal.is_dday_candidate and signal.dday_signal_result is not None:
    _dday = signal.dday_signal_result
    result.is_dday_candidate = True
    result.dday_action   = _dday.get("action", "SKIP")
    result.dday_day_type = _dday.get("day_type", "")
    result.details["dday"] = {
        "action":    _dday.get("action"),
        "day_type":  _dday.get("day_type"),
        "sl":        _dday.get("sl", 0.0),
        "tp":        _dday.get("tp", 0.0),
        "timeout":   _dday.get("timeout", 120),
        "reason":    _dday.get("reason", ""),
    }
    logger.info(...)
```
REJECT 액션이어도 파이프라인을 차단하지 않음 (기록만). is_dday_candidate=True이면 우선순위 부여.

---

## 5. tests/unit/test_dday_entry.py — 단위 테스트 10개 작성 및 실행

### 테스트 목록
1. `test_big_yang_detect` — 장대양봉 조건 충족 시 is_big_yang=True
2. `test_big_yang_below_threshold` — 상승률 7% 미만 시 is_big_yang=False
3. `test_d1_entry_valid` — D+1 눌림 -2.73% + MA5 지지 → is_valid=True
4. `test_d1_entry_too_deep` — D+1 눌림 -6% → is_valid=False
5. `test_d2_entry_valid` — D+2 눌림 -2% + MA10 지지 → is_valid=True
6. `test_d2_entry_ma_break` — D+2 close < MA10 → is_valid=False
7. `test_leader_only_filter` — is_leader=False → action=REJECT
8. `test_timeout_setting` — timeout=120 확인
9. `test_yaml_load` — _load_d_d1_d2_params() dict 반환 확인
10. `test_signal_generation` — D+1 ENTRY + sl/tp 계산 정확성

### 실행 결과
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 10 items

tests/unit/test_dday_entry.py::test_big_yang_detect PASSED               [ 10%]
tests/unit/test_dday_entry.py::test_big_yang_below_threshold PASSED      [ 20%]
tests/unit/test_dday_entry.py::test_d1_entry_valid PASSED                [ 30%]
tests/unit/test_dday_entry.py::test_d1_entry_too_deep PASSED             [ 40%]
tests/unit/test_dday_entry.py::test_d2_entry_valid PASSED                [ 50%]
tests/unit/test_dday_entry.py::test_d2_entry_ma_break PASSED             [ 60%]
tests/unit/test_dday_entry.py::test_leader_only_filter PASSED            [ 70%]
tests/unit/test_dday_entry.py::test_timeout_setting PASSED               [ 80%]
tests/unit/test_dday_entry.py::test_yaml_load PASSED                     [ 90%]
tests/unit/test_dday_entry.py::test_signal_generation PASSED             [100%]

============================== 10 passed in 0.18s ==============================
```

**10/10 ALL PASS ✅**

---

## 6. git commit

```
git add backend/app/services/feature_engine.py config/param_search_space.yaml backend/app/services/trading/cte/cte_pipeline.py tests/unit/test_dday_entry.py
git commit -m "[V4.1] T-117: D_D1_D2_ENTRY 장대양봉 D+1 전략 카드 — 홍인기 대장주 진입"
```

결과:
```
[phase-2c-command-center 474039d7] [V4.1] T-117: D_D1_D2_ENTRY 장대양봉 D+1 전략 카드 — 홍인기 대장주 진입
 4 files changed, 729 insertions(+)
 create mode 100644 tests/unit/test_dday_entry.py
```

커밋 해시: `474039d7`

## 7. git push

```
git push origin phase-2c-command-center
```

결과:
```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**SSH 키 권한 문제로 push 실패** (서버 claudebot 환경 제약).
- 로컬 커밋은 완료 (474039d7)
- root 권한으로 별도 push 필요: `git push origin phase-2c-command-center`

---

## 완료 기준 체크

| 항목 | 상태 |
|------|------|
| YAML d_d1_d2_entry 섹션 생성 | ✅ 완료 |
| DDayEntryEngine 4메서드 구현 | ✅ 완료 |
| CTE L2.5 삽입 | ✅ 완료 |
| 10/10 테스트 PASS | ✅ 완료 |
| git commit | ✅ 완료 (474039d7) |
| git push | ❌ SSH 권한 문제 (root 별도 push 필요) |
| .bak 파일 미커밋 | ✅ 확인 |
| 서비스 재시작 금지 | ✅ 준수 |
