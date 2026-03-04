# CUR-GO100-RESEARCH-CORE-BUILD-001 — 연구소 코어 모듈 구축 (Part 1+2+3)
> 날짜: 2026-03-04 | 담당: claudebot | 프로젝트: GO100

---

[인계 확인]
직전 완료: CUR-V41-VIRTUAL-RUN-HEALTH-CHECK-001
현재 단계: Phase 9 준비 (연구소 코어 강화)
CEO 지시 적용: D-001, D-002, D-003, D-007
strategy_cards: N/A (코어 모듈 구축)
open_positions: N/A

---

## 1. 작업 요약

연구소 코어 3개 모듈(BacktesterAgent, StockProfiler, AnalystAgent)의 존재 및 기능을 검증하고, 단위 테스트 11건을 작성하여 ALL PASS를 달성하였다.

---

## 2. 사전 확인

- 3개 파일 모두 이미 존재 확인:
  - `backend/app/services/go100/agents/agent_backtester.py` ✅
  - `backend/app/services/go100/agents/stock_profiler.py` ✅
  - `backend/app/services/go100/agents/agent_analyst.py` ✅
- import 테스트: `ALL IMPORTS OK` ✅

---

## 3. Part 1 — BacktesterAgent 리플레이 브릿지

**파일**: `backend/app/services/go100/agents/agent_backtester.py`

### 주요 기능 확인
- `tool_generate_strategy_code(context)`: 가설 dict → Python 전략 코드 자동 생성 (entry_signal/exit_signal 함수 포함)
- `tool_run_replay_backtest(context)`: `replay/backtest_runner.py` 호출, JSON I/O, 1800s timeout 지원
- `tool_validate_robustness(context)`: Walk-Forward 3-Fold 검증 + 과적합 위험도 판단 (LOW/MID/HIGH)
- `BacktesterAgent.run_full_backtest(hypothesis)`: 코드 생성 → 리플레이 → 강건성 검증 → 결과 반환

### 단위 테스트 (3건)
| ID | 테스트명 | 결과 |
|----|---------|------|
| BT-01 | import 정상 + BacktesterAgent 인스턴스 생성 | PASS |
| BT-02 | tool_generate_strategy_code — 가설 → Python 코드 생성 | PASS |
| BT-03 | tool_validate_robustness — WF 3-fold, 과적합 HIGH/정상/WF 불통과 케이스 | PASS |

---

## 4. Part 2 — StockProfiler 종목 유형 분류기

**파일**: `backend/app/services/go100/agents/stock_profiler.py`

### 주요 기능 확인
- `_classify_stock_type()`: TYPE-A(대형 5,000억+), TYPE-B(중형 1,000~5,000억), TYPE-C(소형 1,000억-), TYPE-D(52주 신고가 돌파) 분류
  - TYPE-D 우선 적용 (52주 신고가 95%+ 근접 + 거래량 2배+)
- `StockProfiler.profile(backtest_results)`: 종목별 프로파일 생성 및 집계
  - `discovery_accuracy` (desk_accuracy): DESK별 발굴 정확도
  - `desk_path_analysis` (_get_desk_path): DESK5→DESK4→DESK3 경로 추적
- `_aggregate()`: type_summary, winner_chars, loser_chars, desk_accuracy 집계

### 단위 테스트 (5건)
| ID | 테스트명 | 결과 |
|----|---------|------|
| SP-01 | import 정상 + 상수값 검증 | PASS |
| SP-02 | _classify_stock_type TYPE-A (6,000억 대형주) | PASS |
| SP-03 | _classify_stock_type TYPE-D 우선 (신고가 98% + 거래량 2.5배) | PASS |
| SP-04 | _classify_stock_type TYPE-B (2,000억) / TYPE-C (300억) | PASS |
| SP-05 | StockProfiler.profile() — DB 없는 환경, 10건 trades 주입, 집계 검증 | PASS |

---

## 5. Part 3 — AnalystAgent 실패 분석기

**파일**: `backend/app/services/go100/agents/agent_analyst.py`

### 주요 기능 확인
- `tool_analyze_failure(context)`: PF/MDD/WF/승률/유형별 집중손실 5가지 구조적 실패 원인 분석
  - `need_external_research` 판단 (findings >= 2 또는 PF < 1.1이면 외부 탐색)
- `tool_web_search_evidence(context)`: DuckDuckGo HTML 파싱, 최대 3개 검색 주제 자동 생성
- `tool_generate_hypothesis_revision(context)`: 유형별 파라미터 조정 (stop_pct, trailing_pct, timeout_min) + 진입/청산 조건 변경 + DESK 피드백
- `AnalystAgent._llm_enhance()`: Gemini 2.5 Flash 호출 (GEMINI_API_KEY 있을 때)

### 단위 테스트 (3건)
| ID | 테스트명 | 결과 |
|----|---------|------|
| AN-01 | import 정상 + AnalystAgent 인스턴스 생성 | PASS |
| AN-02 | tool_analyze_failure — 5가지 실패 패턴 감지, worst_type=TYPE-C, need_external=True | PASS |
| AN-03 | tool_generate_hypothesis_revision — 유형별 4종 파라미터 + discovery_feedback 3 DESK | PASS |

---

## 6. 전체 테스트 결과

```
tests/test_research_core_build_001.py::TestBacktesterAgent::test_bt01_import PASSED
tests/test_research_core_build_001.py::TestBacktesterAgent::test_bt02_generate_strategy_code PASSED
tests/test_research_core_build_001.py::TestBacktesterAgent::test_bt03_validate_robustness PASSED
tests/test_research_core_build_001.py::TestStockProfiler::test_sp01_import PASSED
tests/test_research_core_build_001.py::TestStockProfiler::test_sp02_classify_type_a PASSED
tests/test_research_core_build_001.py::TestStockProfiler::test_sp03_classify_type_d PASSED
tests/test_research_core_build_001.py::TestStockProfiler::test_sp04_classify_type_b_c PASSED
tests/test_research_core_build_001.py::TestStockProfiler::test_sp05_profile_no_db PASSED
tests/test_research_core_build_001.py::TestAnalystAgent::test_an01_import PASSED
tests/test_research_core_build_001.py::TestAnalystAgent::test_an02_analyze_failure PASSED
tests/test_research_core_build_001.py::TestAnalystAgent::test_an03_generate_hypothesis_revision PASSED

11 passed, 1 warning in 0.12s
```

**11/11 ALL PASS** ✅

기존 테스트 비파괴 확인: 237 passed (17 pre-existing failures, 모두 본 작업과 무관)

---

## 7. 생성/수정 파일

| 파일 | 상태 | 비고 |
|------|------|------|
| `backend/app/services/go100/agents/agent_backtester.py` | 기존 존재, 검증 완료 | 수정 없음 |
| `backend/app/services/go100/agents/stock_profiler.py` | 기존 존재, 검증 완료 | 수정 없음 |
| `backend/app/services/go100/agents/agent_analyst.py` | 기존 존재, 검증 완료 | 수정 없음 |
| `backend/tests/test_research_core_build_001.py` | **신규 생성** | 11건 단위 테스트 |

---

## 8. 완료 체크포인트

- [x] Part 1 BacktesterAgent import PASS + 단위 테스트 3건 PASS
- [x] Part 2 StockProfiler import PASS + 단위 테스트 5건 PASS
- [x] Part 3 AnalystAgent import PASS + 단위 테스트 3건 PASS
- [x] 전체 단위 테스트 11건 ALL PASS
- [x] 기존 테스트 비파괴 확인 (237 passed)
- [ ] 코드 레포 커밋 (kis-autotrade-v4)
- [ ] project-docs 보고서 push

---

완료 시각: 2026-03-04 14:22 KST
