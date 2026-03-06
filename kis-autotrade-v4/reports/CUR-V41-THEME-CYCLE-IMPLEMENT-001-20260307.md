# T-219 보고서: THEME_CYCLE feature variable 구현 (D-008-KR P0)

**Task ID:** T-219
**Date:** 2026-03-07
**Branch:** phase-2c-command-center
**커밋:** 7f27b7b4

---

[인계 확인]
직전 완료: T-218 (DUAL_FLOW_5D/20D feature variable)
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-008-KR P0 (THEME_CYCLE 한국 슈퍼개미 전략 변수)
strategy_cards: (변경 없음)
open_positions: (변경 없음)

---

## 1. 작업 목적

CEO 지시 D-008-KR P0: 한국 시장 고유 변수 `THEME_CYCLE` 구현.
"고기도 먹어본 놈이 먹는다" (시간여행TV) / "상한가도 가본 놈이 간다" (홍인기) 원리 적용.
T-218 DUAL_FLOW 패턴을 따라 DB 의존 없는 standalone 계산 함수를 추가하여
DESK3/4/5 풀 스캔 시 pre-fetched rows로 직접 feature 전달 가능하도록 구현.

---

## 2. 구현 내용

### 2-1. feature_engine.py 수정

**파일:** `backend/app/services/feature_engine.py`
**위치:** ThemeCycleEngine 클래스(기존) 직후, DualFlowEngine 섹션 이전
**태그:** T-219 주석 블록 추가 (line ~170~231)

#### 추가 함수 1: `compute_theme_cycle_100b_count`

```python
def compute_theme_cycle_100b_count(
    rows: list,
    threshold: int = _TRADE_AMOUNT_THRESHOLD,  # 10,000,000,000 (100억)
) -> int:
```

- **입력:** list of dicts with key `trade_amount` (ohlcv_daily 조회 결과)
- **반환:** 거래대금 ≥ 100억 충족 일수 (int)
- **데이터 없음:** 0 반환
- **DB 의존:** 없음 (pure function)

#### 추가 함수 2: `compute_theme_cycle_ul_count`

```python
def compute_theme_cycle_ul_count(
    rows: list,
    upper_limit_pct: float = _UPPER_LIMIT_PCT,  # 29.0%
) -> int:
```

- **입력:** list of dicts with keys `open`, `close` (ohlcv_daily 조회 결과)
- **반환:** 등락률 ≥ +29.0% (상한가) 충족 일수 (int)
- **계산식:** `(close - open) * 100.0 / open >= 29.0`
- **DB 의존:** 없음 (pure function)

### 2-2. 단위 테스트 추가

**파일:** `tests/unit/test_T219_theme_cycle_feature.py` (신규 생성)

| 케이스 | 설명 | 결과 |
|--------|------|------|
| TC-1 (TestTC1AllMatch) | 전체 행 조건 충족 → count = n | PASS |
| TC-2 (TestTC2NoneMatch) | 조건 미달 (50억, 28%) → count = 0 | PASS |
| TC-3 (TestTC3NoData) | 빈 rows → count = 0 | PASS |

**총 테스트:** 6 tests (각 케이스 2개 sub-test)
**결과:** 6/6 ALL PASS

---

## 3. 기존 코드와의 관계

- `ThemeCycleEngine.calculate_theme_cycle()` (기존 T-109): DB 직접 조회, 단독 symbol 조회
- `compute_theme_cycle_100b_count()` / `compute_theme_cycle_ul_count()` (T-219): pre-fetched rows 기반, DESK3/4/5 pool scan용 standalone 함수
- 패턴: T-218에서 추가한 `compute_dual_flow_5d()` / `compute_dual_flow_20d()` 와 동일한 설계

---

## 4. 테스트 실행 결과

```
$ /root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/test_T219_theme_cycle_feature.py -v

tests/unit/test_T219_theme_cycle_feature.py::TestTC1AllMatch::test_100b_count_all_match PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC1AllMatch::test_ul_count_all_match PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC2NoneMatch::test_100b_count_below_threshold PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC2NoneMatch::test_ul_count_below_threshold PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC3NoData::test_100b_count_no_data PASSED
tests/unit/test_T219_theme_cycle_feature.py::TestTC3NoData::test_ul_count_no_data PASSED

6 passed in 0.10s
```

전체 테스트: 798 passed (16 failed - 기존 pre-existing 실패, T-219 무관)

---

## 5. 커밋 정보

- **커밋 해시:** 7f27b7b4
- **메시지:** `[V4.1] feat: T-219 THEME_CYCLE feature variable (D-008-KR P0)`
- **브랜치:** phase-2c-command-center
- **변경 파일:**
  - `backend/app/services/feature_engine.py` (+61 lines)
  - `tests/unit/test_T219_theme_cycle_feature.py` (+91 lines, new)

---

## 6. 성공 기준 체크

- [x] `compute_theme_cycle_100b_count()` 함수 구현 완료
- [x] `compute_theme_cycle_ul_count()` 함수 구현 완료
- [x] 단위 테스트 3케이스 (6 sub-tests) ALL PASS
- [x] `git push` 성공 (7f27b7b4)
- [ ] project-docs 보고서 push (다음 단계)
- [ ] HANDOVER.md 업데이트 (다음 단계)

---

## 7. 금지사항 준수 확인

- [x] 서비스 재시작 없음
- [x] strategy_cards 변경 없음
- [x] .env/.bak 커밋 없음

---

HANDOVER.md 업데이트 완료: (업데이트 후 기재)
