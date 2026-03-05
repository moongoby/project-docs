---
project: kis-autotrade-v4
task_id: T-092
completed_at: 2026-03-05T11:40:00+09:00
---

# T-092 실행 결과: Node Detector 통합 엔진 — 5 DESK 마디 감지 통합

## 지시 파일
`/root/.genspark/directives/running/KIS_20260305_111840_BRIDGE.md`

---

## Phase 1 — DB 스키마 확인

### 실행
```
PGPASSWORD="KisAuto2026!Secure" psql -h localhost -U kis_admin -d kisautotrade -c "\dt v4_node*"
PGPASSWORD="KisAuto2026!Secure" psql -h localhost -U kis_admin -d kisautotrade -c "\dt v4_capital*"
```

### 결과
```
               List of relations
 Schema |       Name       | Type  |   Owner
--------+------------------+-------+-----------
 public | v4_node_history  | table | kis_admin
 public | v4_node_realtime | table | kis_admin
(2 rows)

              List of relations
 Schema |      Name       | Type  |   Owner
--------+-----------------+-------+-----------
 public | v4_capital_flow | table | kis_admin
(1 row)
```

**판정**: migration 057이 이미 적용되어 3개 테이블 모두 존재함. 별도 마이그레이션 불필요.

---

## Phase 2 — 통합 노드 감지 엔진 생성

### 파일 생성
`/root/kis-autotrade-v4/backend/app/services/node_detector_engine.py` (신규)

### 구조
```python
class NodeDetectorEngine:
    def __init__(self):
        # desk1~desk5 detector 인스턴스화

    def detect_all_nodes(symbols) -> Dict[str, Dict]
    def get_active_nodes(min_confidence=60) -> List[Dict]
    def get_node_history(symbol, desk_level=None) -> List[Dict]
    def predict_next_node(symbol, desk_level) -> Dict
    def detect_desk5_nodes(symbols) -> Dict
    def detect_desk4_nodes(symbols) -> Dict
    def detect_desk3_nodes(symbols) -> Dict
    def detect_desk2_nodes(stock_code, minute_bars, vwap) -> Dict
    def detect_desk1_nodes(stock_code, buy_qty, sell_qty) -> Dict
    def load_history_batch(symbols, desk_levels, max_symbols) -> Dict
    def _backtrack_nodes(stock_code, bars, desk_level) -> List[NodeRecord]
    def daily_summary(symbols) -> Dict
    def get_multi_desk_signal(symbol, bars=None) -> Dict
```

### DESK별 래핑 구조
- DESK5: `Desk5NodeDetector` (node_detector_desk5.py) → detect_desk5_nodes()
- DESK4: `Desk4NodeDetector` (node_detector_desk4.py) → detect_desk4_nodes()
- DESK3: `Desk3NodeDetector` (node_detector_desk3.py) → detect_desk3_nodes()
- DESK2: `Desk2NodeDetector` (node_detector_desk2.py) → detect_desk2_nodes()
- DESK1: `Desk1NodeDetector` (node_detector_desk1.py) → detect_desk1_nodes()

### 신뢰도 계산
```python
if node_count >= 10: confidence = 0.9
elif node_count >= 5: confidence = 0.7
else: confidence = 0.5
```

---

## Phase 3 — 크론 등록

### 실행
```bash
(crontab -l 2>/dev/null; cat <<'CRON'
# [KIS T-092] DESK5/4 노드 감지 — 매일 16:00 KST (07:00 UTC) 평일
0 7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk5 >> /root/kis-autotrade-v4/logs/node_desk5.log 2>&1
# [KIS T-092] DESK4 노드 감지 — 매일 16:00 KST (07:00 UTC) 평일
5 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk4 >> /root/kis-autotrade-v4/logs/node_desk4.log 2>&1
# [KIS T-092] DESK3 노드 감지(프리마켓) — 08:50 KST (23:50 UTC 전날) 평일
50 23 * * 0-4 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk3 >> /root/kis-autotrade-v4/logs/node_desk3.log 2>&1
# [KIS T-092] DESK3 노드 감지(장마감) — 16:00 KST (07:00 UTC) 평일
10 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk3 >> /root/kis-autotrade-v4/logs/node_desk3.log 2>&1
# [KIS T-092] 일간 노드 요약 — 16:30 KST (07:30 UTC) 평일
30 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine daily_summary >> /root/kis-autotrade-v4/logs/node_daily_summary.log 2>&1
CRON
) | crontab -
```

### 결과
```
크론 등록 완료
# [KIS T-092] DESK5/4 노드 감지 — 매일 16:00 KST (07:00 UTC) 평일
# [KIS T-092] DESK4 노드 감지 — 매일 16:00 KST (07:00 UTC) 평일
# [KIS T-092] DESK3 노드 감지(프리마켓) — 08:50 KST (23:50 UTC 전날) 평일
# [KIS T-092] DESK3 노드 감지(장마감) — 16:00 KST (07:00 UTC) 평일
# [KIS T-092] 일간 노드 요약 — 16:30 KST (07:30 UTC) 평일
```

**5건 등록 완료**

---

## Phase 4 — v4_node_history 히스토리 배치 적재

### 파일 생성
`/root/kis-autotrade-v4/scripts/run_node_history_batch.py` (신규)

### 실행
```bash
/root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/run_node_history_batch.py --max 500 --desk 5,4,3
```

### 출력 (tail -20)
```
2026-03-05 11:34:59,485 INFO DESK4 완료: 9905건
2026-03-05 11:34:59,485 INFO DESK3 역추적 시작...
2026-03-05 11:35:02,971 INFO   DESK3: 50/500 처리, 2041건 적재
2026-03-05 11:35:06,095 INFO   DESK3: 100/500 처리, 4003건 적재
2026-03-05 11:35:08,839 INFO   DESK3: 150/500 처리, 5980건 적재
2026-03-05 11:35:11,579 INFO   DESK3: 200/500 처리, 7975건 적재
2026-03-05 11:35:14,516 INFO   DESK3: 250/500 처리, 9984건 적재
2026-03-05 11:35:17,638 INFO   DESK3: 300/500 처리, 11936건 적재
2026-03-05 11:35:20,697 INFO   DESK3: 350/500 처리, 13924건 적재
2026-03-05 11:35:23,940 INFO   DESK3: 400/500 처리, 15915건 적재
2026-03-05 11:35:27,074 INFO   DESK3: 450/500 처리, 17911건 적재
2026-03-05 11:35:30,117 INFO   DESK3: 500/500 처리, 19857건 적재
2026-03-05 11:35:30,117 INFO DESK3 완료: 19857건
2026-03-05 11:35:30,117 INFO === 배치 완료: 총 33100건, 소요 87.9초 ===
2026-03-05 11:35:30,148 INFO v4_node_history 총 33100행
2026-03-05 11:35:30,148 INFO   DESK3: 19857행
2026-03-05 11:35:30,148 INFO   DESK4: 9905행
2026-03-05 11:35:30,148 INFO   DESK5: 3338행
배치 완료: 총 33100행 (이번 적재 33100건)
DESK별: {3: 19857, 4: 9905, 5: 3338}
```

### DB 검증
```sql
SELECT desk_level, COUNT(*) as nodes, AVG(node_pnl_pct) as avg_pnl, AVG(pullback_depth_pct) as avg_pullback
FROM v4_node_history GROUP BY desk_level ORDER BY desk_level;
```

```
 desk_level | nodes |         avg_pnl         |    avg_pullback
------------+-------+-------------------------+---------------------
          3 | 19857 |  0.33848592939517550486 |  4.5945070906984942
          4 |  9905 |  0.37942055527511357900 |  6.9349220292781424
          5 |  3338 | -0.99728220491312162972 | 12.5849081186339125
(3 rows)
```

```sql
SELECT node_size_category, COUNT(*) FROM v4_node_history GROUP BY node_size_category ORDER BY COUNT(*) DESC;
```

```
 node_size_category | count
--------------------+-------
 SMALL              | 30444
 MEDIUM             |  1861
 LARGE              |   702
 EXPLOSIVE          |    93
(4 rows)
```

**판정**: 33,100행 ≥ 10,000 기준 ✅

---

## Phase 5 — 단위테스트

### 파일 생성
`/root/kis-autotrade-v4/tests/unit/test_node_detector_engine.py` (신규, 40건)

### 실행
```bash
/root/kis-autotrade-v4/venv/bin/python3 -m pytest tests/unit/test_node_detector_engine.py -v --tb=short
```

### 출력 전문
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False
collecting ... collected 40 items

tests/unit/test_node_detector_engine.py::TestHelpers::test_T01_ma_returns_correct_mean PASSED [  2%]
tests/unit/test_node_detector_engine.py::TestHelpers::test_T02_ma_returns_none_if_insufficient PASSED [  5%]
tests/unit/test_node_detector_engine.py::TestHelpers::test_T03_vol_ma_returns_correct_mean PASSED [  7%]
tests/unit/test_node_detector_engine.py::TestHelpers::test_T04_vol_ma_returns_none_if_insufficient PASSED [ 10%]
tests/unit/test_node_detector_engine.py::TestHelpers::test_T05_ma_exact_length PASSED [ 12%]
tests/unit/test_node_detector_engine.py::TestDesk5Detector::test_T06_classify_phase_insufficient_bars_returns_pullback PASSED [ 15%]
tests/unit/test_node_detector_engine.py::TestDesk5Detector::test_T07_classify_phase_rising_returns_rising PASSED [ 17%]
tests/unit/test_node_detector_engine.py::TestDesk5Detector::test_T08_detect_node_history_empty_on_insufficient_bars PASSED [ 20%]
tests/unit/test_node_detector_engine.py::TestDesk5Detector::test_T09_detect_node_history_returns_records PASSED [ 22%]
tests/unit/test_node_detector_engine.py::TestDesk5Detector::test_T10_predict_next_node_empty_history PASSED [ 25%]
tests/unit/test_node_detector_engine.py::TestDesk5Detector::test_T11_predict_next_node_with_history PASSED [ 27%]
tests/unit/test_node_detector_engine.py::TestDesk5Detector::test_T12_node_record_defaults PASSED [ 30%]
tests/unit/test_node_detector_engine.py::TestDesk4Detector::test_T13_classify_phase_insufficient PASSED [ 32%]
tests/unit/test_node_detector_engine.py::TestDesk4Detector::test_T14_classify_phase_returns_valid_phase PASSED [ 35%]
tests/unit/test_node_detector_engine.py::TestDesk4Detector::test_T15_detect_desk3_promote_insufficient_bars PASSED [ 37%]
tests/unit/test_node_detector_engine.py::TestDesk4Detector::test_T16_detect_node_reentry_insufficient_bars PASSED [ 40%]
tests/unit/test_node_detector_engine.py::TestDesk4Detector::test_T17_detect_desk3_promote_vol_3x PASSED [ 42%]
tests/unit/test_node_detector_engine.py::TestDesk3Detector::test_T18_classify_phase_insufficient PASSED [ 45%]
tests/unit/test_node_detector_engine.py::TestDesk3Detector::test_T19_classify_phase_rising PASSED [ 47%]
tests/unit/test_node_detector_engine.py::TestDesk3Detector::test_T20_get_node_bonus_insufficient_bars PASSED [ 50%]
tests/unit/test_node_detector_engine.py::TestDesk2Detector::test_T21_classify_phase_with_vwap_above PASSED [ 52%]
tests/unit/test_node_detector_engine.py::TestDesk2Detector::test_T22_classify_phase_with_vwap_below PASSED [ 55%]
tests/unit/test_node_detector_engine.py::TestDesk2Detector::test_T23_detect_reentry_signal_not_starting PASSED [ 57%]
tests/unit/test_node_detector_engine.py::TestDesk1Detector::test_T24_classify_rising_when_buy_dominant PASSED [ 60%]
tests/unit/test_node_detector_engine.py::TestDesk1Detector::test_T25_classify_pullback_when_sell_dominant PASSED [ 62%]
tests/unit/test_node_detector_engine.py::TestDesk1Detector::test_T26_classify_rising_when_sell_zero PASSED [ 65%]
tests/unit/test_node_detector_engine.py::TestDesk1Detector::test_T27_get_optimal_entry_starting PASSED [ 67%]
tests/unit/test_node_detector_engine.py::TestDesk1Detector::test_T28_get_optimal_entry_pullback PASSED [ 70%]
tests/unit/test_node_detector_engine.py::TestDesk1Detector::test_T29_simulate_execution_improvement_empty PASSED [ 72%]
tests/unit/test_node_detector_engine.py::TestDesk1Detector::test_T30_run_on_order_returns_dict PASSED [ 75%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T31_engine_has_all_detectors PASSED [ 77%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T32_detect_desk1_nodes_returns_dict PASSED [ 80%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T33_detect_desk2_nodes_returns_dict PASSED [ 82%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T34_get_active_nodes_handles_db_error PASSED [ 85%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T35_get_node_history_handles_db_error PASSED [ 87%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T36_predict_next_node_no_history PASSED [ 90%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T37_predict_next_node_with_mock_history PASSED [ 92%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T38_get_multi_desk_signal_returns_all_desks PASSED [ 95%]
tests/unit/test_node_detector_engine.py::TestNodeDetectorEngine::test_T39_confidence_high_for_10_plus_nodes PASSED [ 97%]
tests/unit/test_node_detector_engine.py::TestIntegrationLive::test_T40_desk5_classify_live_symbol PASSED [100%]

=============================== warnings summary ===============================
tests/unit/test_node_detector_engine.py:357
  PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 40 passed, 1 warning in 0.38s =========================
```

**판정**: 40/40 ALL PASS ✅

---

## git 커밋

### 실행
```bash
git add backend/app/services/node_detector_engine.py \
        tests/unit/test_node_detector_engine.py \
        scripts/run_node_history_batch.py \
        report/v41/CUR-V41-NODE-DETECTOR-001-20260305.md

git commit -m "feat: T-092 NodeDetectorEngine 5 DESK 마디 감지 통합 엔진
..."
```

### 결과
```
[phase-2c-command-center 5ceb5f11] feat: T-092 NodeDetectorEngine 5 DESK 마디 감지 통합 엔진
 4 files changed, 1304 insertions(+)
 create mode 100644 backend/app/services/node_detector_engine.py
 create mode 100644 report/v41/CUR-V41-NODE-DETECTOR-001-20260305.md
 create mode 100644 scripts/run_node_history_batch.py
 create mode 100644 tests/unit/test_node_detector_engine.py
```

커밋 해시: `5ceb5f11`

---

## 완료 기준 최종 체크

| 기준 | 결과 |
|------|------|
| 3개 테이블 마이그레이션 성공 | ✅ v4_node_history, v4_node_realtime, v4_capital_flow 모두 존재 |
| 과거 3년 마디 데이터 적재 (≥10,000행) | ✅ **33,100행** (DESK3: 19,857 / DESK4: 9,905 / DESK5: 3,338) |
| 단위테스트 ≥25건 ALL PASS | ✅ **40/40 PASS** |
| 크론 등록 | ✅ 5건 등록 (DESK5/4/3 + 프리마켓 DESK3 + 일간 요약) |
| 코드 레포 커밋 | ✅ `5ceb5f11` |

---

## 생성된 파일 목록

| 경로 | 설명 |
|------|------|
| `backend/app/services/node_detector_engine.py` | 5 DESK 통합 엔진 (NodeDetectorEngine 클래스) |
| `scripts/run_node_history_batch.py` | 3년 히스토리 배치 적재 스크립트 |
| `tests/unit/test_node_detector_engine.py` | 단위테스트 40건 |
| `report/v41/CUR-V41-NODE-DETECTOR-001-20260305.md` | 상세 보고서 |

---

*실행 완료: 2026-03-05 11:40 KST*
*브랜치: phase-2c-command-center*
*커밋: 5ceb5f11*
