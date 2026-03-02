# CUR-V41-SESSION-L-GAP-RESOLVE-001 — 아키텍처 잔여 GAP 해소 (G-5, G-6, 단위 통일)
> 작성: 2026-03-02 | Model: Claude Code (claude-opus-4-6)
> 코드 커밋: kis-autotrade-v4 (이 커밋) | 문서 커밋: project-docs (이 커밋)

---

## 1. 목적

Session H에서 식별된 아키텍처 GAP 3건을 03-03 Virtual Run 이전에 해소:

| GAP | 설명 | 긴급도 | 상태 |
|-----|------|--------|------|
| G-5 | Anti-Pattern 필터가 entry_detector에만 존재, signal_generator에 미적용 | P0 | **해소** |
| G-6 | timeout_min이 exit_simulator에만 존재, exit_manager에 미적용 | P0 | **해소** |
| 단위 | exit_manager 퍼센트(3.0=3%), exit_simulator 비율(0.030=3%) 불일치 | P0 | **해소** |

---

## 2. G-5: Anti-Pattern 필터 동기화

### 변경 파일: `backend/app/services/unified_engine/core/signal_generator.py`

### 구현 방식: Method A (signal_generator 직접 구현)
- CTE L4.5(EQS Gate)는 실행 품질 평가이므로 anti-pattern과 관련 없음
- signal_generator에 이미 minute_df가 있어 별도 데이터 조회 불필요

### 추가된 구성요소

| 구성 | 설명 |
|------|------|
| `_ANTI_PATTERN_STRATEGIES` | `{"D2", "D2A", "D2B", "D4", "D5", "S1"}` |
| `_ABSOLUTE_FORBIDDEN_STRATEGIES` | `{"D2", "D2A", "D2B", "D5", "S1"}` |
| `_is_anti_pattern(minute_df)` | 3조건 AND: 역배열(MA5<MA10<MA20) + VWAP 하회 + 거래량 감소 |
| `_is_absolute_forbidden(now, minute_df)` | 2조건 AND: 장후반(13시+) + 거래량 급감(avg5/avg20 < 0.5) |

### 호출 위치
`_evaluate_strategy()` 내 L3.3 수급 필터 이후, TradeSignal 생성/CTE 호출 이전:
```
L3.3 Supply Gate → Anti-Pattern Check → Absolute Forbidden Check → TradeSignal → CTE
```

### entry_detector와의 동기화 확인
| 항목 | entry_detector | signal_generator | 일치 |
|------|---------------|-----------------|------|
| MA 역배열 조건 | MA5 < MA10 < MA20 | 동일 | O |
| VWAP 하회 | close < VWAP | 동일 | O |
| 거래량 감소 | avg5 < avg20 × 0.8 | 동일 | O |
| 절대 차단 시간 | 240분(13시+) | 동일 | O |
| 절대 차단 볼륨 | avg5/avg20 < 0.5 | 동일 | O |
| Fail-Open (데이터 부족) | 통과 | 동일 | O |

---

## 3. G-6: Timeout 추가

### 변경 파일: `backend/app/services/unified_engine/core/exit_manager.py`

### 추가된 구성요소

| 구성 | 설명 |
|------|------|
| `ExitMode.TIMEOUT` | 신규 Enum 값 (`"TIMEOUT"`, MODE_6) |
| `timeout_min` in STRATEGY_EXIT_PARAMS | D2=60, D2A=30, D2B=60, D4=60, D5=60, S1=None |
| MODE_6 체크 | `_check_exit()` 내 elapsed_min >= timeout_min 시 청산 |

### 청산 우선순위 (6모드)
```
MODE_5 (DD L4 강제이탈) > MODE_1 (하드스톱) > HARD_TP (D4 전용) > MODE_6 (타임아웃)
> MODE_3 (15:30 시간청산) > MODE_4 (부분익절) > MODE_2 (ATR 트레일링)
```

### exit_simulator와의 동기화 확인
| 전략 | exit_simulator timeout_min | exit_manager timeout_min | 일치 |
|------|---------------------------|-------------------------|------|
| D2 | 60 | 60 | O |
| D2A | 30 | 30 | O |
| D2B | 60 | 60 | O |
| D4 | 60 | 60 | O |
| D5 | 60 | 60 | O |
| S1 | None | None | O |

---

## 4. 단위 통일

### 변경 파일: `backend/app/services/unified_engine/core/exit_manager.py`

### Before (퍼센트 단위)
```python
STRATEGY_EXIT_PARAMS = {
    "D2":  {"sl_pct": 3.0, "trail_start": 3.0, ...},
    ...
}
PARTIAL_TP_TRIGGER_PCT = 3.0
```

### After (비율 단위 — exit_simulator와 동일)
```python
STRATEGY_EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "trail_start": 0.030, ...},
    ...
}
PARTIAL_TP_TRIGGER = 0.03
```

### 안전 장치: `_pnl_as_ratio()`
- 포지션의 미실현 PnL을 항상 비율로 반환
- 직접 계산 우선: `(current_price - entry_price) / entry_price`
- Fallback: `unrealized_pnl_pct` 속성 (abs > 1.0이면 퍼센트로 간주, /100 변환)

---

## 5. 테스트 결과

### 신규: test_architecture_sync.py (38 tests)

| 클래스 | 테스트 수 | 검증 내용 |
|--------|----------|----------|
| TestExitParamSync | 21 | sl_pct/trail_start/trail_retrace/tp_pct 양쪽 동기화 (6전략 × 3파라미터 + keys + tp_pct) |
| TestTimeoutSync | 8 | timeout_min 존재/값동기화(5전략)/S1=None/TIMEOUT enum |
| TestUnitConsistency | 3 | 모든 파라미터 < 1.0 (비율 단위)/D2 trail_start=0.030 |
| TestAntiPatternSync | 6 | 3조건 차단/상승추세 통과/데이터 부족 Fail-Open/절대차단/전략 집합 |

### 전체 CTE 테스트
```
132 passed, 1 warning in 0.72s  (기존 94 + 신규 38)
```

---

## 6. 수정 파일 목록

| 파일 | 변경 유형 | 핵심 변경 |
|------|----------|----------|
| `backend/app/services/unified_engine/core/signal_generator.py` | 수정 | G-5 Anti-Pattern 2메서드 + 전략 집합 + _evaluate_strategy 호출 |
| `backend/app/services/unified_engine/core/exit_manager.py` | 수정 | G-6 Timeout + 단위 비율 통일 + _pnl_as_ratio() + ExitMode.TIMEOUT |
| `backend/app/services/trading/cte/test_architecture_sync.py` | 신규 | 38 테스트 (파라미터/타임아웃/단위/안티패턴 동기화 검증) |

---

## 7. 03-03 Virtual Run 준비 완료 체크리스트

| # | 항목 | 상태 |
|---|------|------|
| 1 | L3.3 수급 필터 (Session H/E-3) | DONE |
| 2 | Anti-Pattern 필터 동기화 (G-5) | DONE |
| 3 | Timeout 동기화 (G-6) | DONE |
| 4 | 단위 통일 (비율) | DONE |
| 5 | 모니터링 자동 수집 (Session K) | DONE |
| 6 | 아키텍처 동기화 테스트 132 ALL PASS | DONE |
| 7 | 서비스 미재시작 (cron → venv/bin/python 직접 실행) | DONE |
