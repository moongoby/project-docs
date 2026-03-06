# CUR-V41-SOURCE-PROPAGATION-VERIFY-001-20260307

**Task ID:** T-216
**작성일:** 2026-03-07
**작성자:** claude-sonnet-4-6 (claudebot)
**Phase:** Phase 2C Command Center
**커밋:** 8d74d00c

---

[인계 확인]
직전 완료: T-215
현재 단계: Phase 2C
CEO 지시 적용: D-001, D-003, D-010
strategy_cards: N/A (변경 없음)
open_positions: N/A (런타임 미확인, 비거래일)

---

## 1. 작업 개요

**목표:** T-196에서 도입된 `PRE_SOURCE_FILTER`(KIS_MOCK 세션 D6 전용화)의 `source` 필드 전파 경로 확인 및 수정.

**배경:**
- T-196 (커밋 8674cd71): `funnel_score.yaml`에 `session_strategy_filter` 추가, `cte_pipeline.py`에 `PRE_SOURCE_FILTER` 구현
- T-196 보고서 주의사항: "signal.source가 VIRTUAL_KIS_MOCK으로 올바르게 전파되는지 런타임 확인 필요"
- **문제:** `signal.source`가 빈 문자열이면 Fail-Open으로 필터 무력화 → D6 외 전략이 KIS_MOCK 세션에서도 통과

---

## 2. 분석 결과

### 2-1. PRE_SOURCE_FILTER 로직 (cte_pipeline.py:435)

```python
if _sf_cfg.get("enabled", False) and signal.source:
```

`signal.source`가 빈 문자열(`""`)이면 조건이 `False` → 필터 건너뜀 (Fail-Open).

### 2-2. source 미전파 지점 발견

**파일:** `backend/app/services/unified_engine/core/signal_generator.py`
**함수:** `SignalGenerator._evaluate_strategy()` (line 359)

```python
signal = TradeSignal(
    strategy_id=actual_strategy_id,
    trigger="UNIFIED_ENGINE",
    ...
    # ❌ source 필드 없음 → 기본값 "" → PRE_SOURCE_FILTER 항상 건너뜀
)
```

**근본 원인:** `SignalGenerator`가 session 정보를 받지 않았으므로, 생성하는 모든 `TradeSignal`의 `source`가 기본값 `""`.

### 2-3. 필터 설정 확인 (funnel_score.yaml)

```yaml
session_strategy_filter:
  enabled: true
  rules:
    VIRTUAL_KIS_MOCK:
      allowed:
        - D6
      block_reason: "KIS_MOCK 세션 D6 전용화 (T-196)"
```

설정은 올바르게 되어 있으나, `signal.source`가 전파되지 않아 필터가 작동하지 않는 상태였음.

---

## 3. 수정 내용

### 3-1. signal_generator.py — session_source 파라미터 추가

```python
# 수정 전
def __init__(self, cte_pipeline, scoring_engine=None, bridge_client=None, pool=None):
    ...

# 수정 후
def __init__(self, cte_pipeline, scoring_engine=None, bridge_client=None,
             pool=None, session_source: str = ""):
    ...
    self._session_source: str = session_source  # T-216: PRE_SOURCE_FILTER 전파용
```

TradeSignal 생성 시 `source` 필드 추가:
```python
signal = TradeSignal(
    ...
    source=self._session_source,  # T-216: 소스 전파 (PRE_SOURCE_FILTER 활성화)
)
```

### 3-2. engine.py — DataSourceType 기반 session_source 결정

```python
# T-216: KIS_MOCK 세션 source 식별자 — PRE_SOURCE_FILTER 전파
_session_source = (
    "VIRTUAL_KIS_MOCK"
    if config.data_source == DataSourceType.KIS_MOCK
    else ""
)
self.signal_gen = SignalGenerator(
    cte_pipeline=cte_pipeline,
    ...
    session_source=_session_source,
)
```

**매핑:**
| `config.data_source` | `session_source` | PRE_SOURCE_FILTER |
|---|---|---|
| `DataSourceType.KIS_MOCK` | `"VIRTUAL_KIS_MOCK"` | 활성화 (D6만 허용) |
| `DataSourceType.DB` | `""` | Fail-Open (필터 건너뜀) |

---

## 4. 테스트 결과

### 4-1. 신규 테스트 (TC-30~TC-35) — 6건 추가

| TC# | 테스트명 | 결과 |
|---|---|---|
| TC-30 | `test_signal_generator_kis_mock_session_source` | PASS |
| TC-31 | `test_signal_generator_db_session_source_empty` | PASS |
| TC-32 | `test_engine_sets_session_source_for_kis_mock` | PASS |
| TC-33 | `test_engine_sets_session_source_empty_for_db` | PASS |
| TC-34 | `test_pre_source_filter_bypass_when_source_empty` | PASS |
| TC-35 | `test_pre_source_filter_active_when_source_set` | PASS |

### 4-2. 기존 테스트 (회귀 검증)

| 파일 | 결과 |
|---|---|
| `tests/test_unified_engine.py` | 27 passed, 1 pre-existing failed (test_time_close MagicMock 이슈, 본 태스크와 무관) |
| `tests/unit/test_technical_signals.py` | 29/29 passed |

**총계: 61 passed, 1 pre-existing failed**

---

## 5. 03-07 로그 확인 계획

PRE_SOURCE_FILTER 동작 확인:

```bash
# 로그에서 PRE_SOURCE_FILTER BLOCK 발생 여부 확인
grep "PRE_SOURCE_FILTER" /var/log/go100.log | tail -20

# KIS_MOCK 세션 실행 시 source 전파 확인
grep "source=VIRTUAL_KIS_MOCK" /var/log/go100.log | tail -10
```

**기대 동작 (03-09 첫 거래일 이후):**
- KIS_MOCK 세션에서 D6 외 전략(D4/D5/D7/D2/S1) 신호 생성 시 `PRE_SOURCE_FILTER[{ticker}] source=VIRTUAL_KIS_MOCK strategy=D4 → BLOCK (허용: ['D6'])` 로그 발생
- D6 전략만 `PRE_SOURCE_FILTER[{ticker}] source=VIRTUAL_KIS_MOCK strategy=D6 → PASS` 통과

---

## 6. 변경 파일 목록

| 파일 | 변경 유형 | 내용 |
|---|---|---|
| `backend/app/services/unified_engine/core/signal_generator.py` | FIX | `session_source` 파라미터 추가, `TradeSignal.source` 전파 |
| `backend/app/services/unified_engine/engine.py` | FIX | `DataSourceType.KIS_MOCK` 감지 → `session_source="VIRTUAL_KIS_MOCK"` 전달 |
| `tests/test_unified_engine.py` | TEST | `TestSourcePropagation` 6건 추가 (TC-30~TC-35) |

---

## 7. 성공 기준 달성

- [x] source 전파 경로 확인 완료: `SignalGenerator._evaluate_strategy()` → `TradeSignal.source`
- [x] 수정 완료: `session_source` 파라미터 → `TradeSignal.source` 전파
- [x] 문법 검사: 정상 import 확인
- [x] 테스트: 6/6 신규 TC PASS, 61/62 전체 PASS (1건 pre-existing)
- [x] git commit: 8d74d00c
- [x] git push: phase-2c-command-center 성공

---

## 저장 정보

- 서버 경로: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-SOURCE-PROPAGATION-VERIFY-001-20260307.md`
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-SOURCE-PROPAGATION-VERIFY-001-20260307.md
- 커밋: (project-docs 커밋 후 기재)
- HTTP 확인: (push 후 확인)
- HANDOVER 업데이트: (완료 후 기재)
