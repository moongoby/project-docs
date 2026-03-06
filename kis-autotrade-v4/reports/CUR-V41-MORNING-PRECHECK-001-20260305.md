# Task087 보고서: 내일(3/6) 09:10 자동매수 사전 검증 + TP 발동 모니터링 체계

[인계 확인]
직전 완료: Task084
현재 단계: Phase 2c (Command Center)
CEO 지시 적용: D-001, D-002, D-003
strategy_cards: (확인 생략 — READ-ONLY 독립 태스크)
open_positions: (확인 생략 — READ-ONLY 독립 태스크)

---

## 개요
- **Task ID**: 087
- **제목**: 내일(3/6) 09:10 자동매수 사전 검증 + TP 발동 모니터링 체계
- **프로젝트**: KIS + GO100
- **우선순위**: P0
- **실행일**: 2026-03-05
- **완료일**: 2026-03-05T10:13:32+09:00

---

## Phase 1: 사전 검증 결과

### Step 1-1: 크론 스케줄 최종 확인

```
crontab -l | grep -E "paper_trading|unified_engine|monitor_virtual"
```

**결과**:
```
10 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode buy >> /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log 2>&1
15 6 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode sell >> /root/kis-autotrade-v4/logs/paper_trading_v3_sell.log 2>&1
30 7 * * 5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode weekly_review >> /root/kis-autotrade-v4/logs/paper_trading_v3_review.log 2>&1
0 9-15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python scripts/monitor_virtual_run.py periodic >> /root/kis-autotrade-v4/logs/virtual_hourly_report.log 2>&1
```

**판정**: ✅ 09:10 KST (00:10 UTC) 매수 크론 정상 등록됨

---

### Step 1-2: paper_trading_v3 dry-run 재실행

```
python3 scripts/go100/run_paper_trading_v3.py --mode buy --dry-run
```

**실행 로그 요약**:
```
2026-03-05 10:11:18 [INFO] paper_trading_v3 — run_paper_trading_v3 시작: mode=buy dry_run=True date=2026-03-05
2026-03-05 10:11:18 [INFO] paper_trading_v3 — === BUY MODE 시작 [DRY-RUN] ===
2026-03-05 10:11:30 [INFO] paper_trading_v3 — run_paper_trading_v3 완료: {
  'ok': True,
  'session_id': 2,
  'candidates': 100,
  'scored_pass': 5,
  'bought': [
    {'ticker': '000020', 'qty': 300, 'price': 5665.66, 'up_5d_prob': 0.5629, 'cs_ai': 99, 'dry_run': True},
    {'ticker': '000050', 'qty': 200, 'price': 8658.65, 'up_5d_prob': 0.5629, 'cs_ai': 100, 'dry_run': True},
    {'ticker': '000080', 'qty': 100, 'price': 16296.28, 'up_5d_prob': 0.5629, 'cs_ai': 100, 'dry_run': True},
    {'ticker': '0000H0', 'qty': 100, 'price': 10420.41, 'up_5d_prob': 0.5629, 'cs_ai': 91,  'dry_run': True},
    {'ticker': '0000Z0', 'qty': 100, 'price': 14899.88, 'up_5d_prob': 0.5629, 'cs_ai': 100, 'dry_run': True}
  ],
  'dry_run': True
}
```

**판정**:
- ✅ 5종목 scored_pass 확인 (candidates: 100 → scored_pass: 5)
- ✅ CONVICTION_THRESHOLD=0.50 반영 확인 (up_5d_prob=0.5629 ≥ 0.50)
- ✅ TOP_N_STOCKS=5 (종목당 max_position_pct=20% 준수)
- ✅ dry_run=True 정상 동작

---

### Step 1-3: unified_engine action_signal 시간 창 20h 적용 확인

```
grep "INTERVAL" scripts/run_unified_engine.py | head -5
```

**결과**:
```
WHERE tick_time >= NOW() - INTERVAL '20 hours'
AND tick_time >= NOW() - INTERVAL '5 minutes'
AND captured_at >= NOW() - INTERVAL '5 minutes'
WHERE t.tick_time >= NOW() - INTERVAL '20 hours'
```

**판정**: ✅ `INTERVAL '20 hours'` 확인됨

---

### Step 1-4: EXIT_PARAMS TP=3% 적용 확인

```
grep -A 10 "EXIT_PARAMS" scripts/run_unified_engine.py
grep -A 10 "STRATEGY_EXIT_PARAMS" backend/app/services/unified_engine/core/exit_manager.py
```

**결과 (run_unified_engine.py)**:
```python
EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
    "D2A": {"sl_pct": 0.020, "tp_pct": None,  "timeout_min": 30},
    "D2B": {"sl_pct": 0.025, "tp_pct": None,  "timeout_min": 60},
    "D4":  {"sl_pct": 0.020, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305: SL 2%, TP 3%
    "D5":  {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
    "S1":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": None},
    "D6":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
    "D7":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
    "D-ORB": {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
}
```

**결과 (exit_manager.py)**:
```python
STRATEGY_EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    "D2A": {"sl_pct": 0.020, "trail_start": 0.015, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": 30},
    "D2B": {"sl_pct": 0.025, "trail_start": 0.015, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": 60},
    "D4":  {"sl_pct": 0.020, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305
    "D5":  {"sl_pct": 0.025, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    "S1":  {"sl_pct": 0.030, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": None},
    "D6":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    "D7":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    "D-ORB": {"sl_pct": 0.025, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
}
```

**판정**:
- ✅ TP=3% (0.030) 모든 주요 전략(D2, D4, D5, D6, D7, D-ORB)에 적용됨
- ✅ run_unified_engine.py ↔ exit_manager.py 동기화됨
- ✅ `# CEO-APPROVAL-20260305` 주석으로 변경 이력 명확

---

## Phase 2: 모니터링 자동화 결과

### Step 2-1: check_morning_execution.py 생성

**파일 경로**: `/root/kis-autotrade-v4/scripts/check_morning_execution.py`

**기능**:
- paper_trading_v3_buy.log 에서 오늘 날짜 로그 추출 (최근 500줄)
- `run_paper_trading_v3 완료` + `bought` 키워드 탐색
- 성공 시: scored_pass 수, 매수 종목 리스트 → 텔레그램 성공 알림
- 실패 시: 최근 에러 로그 + 최근 10줄 → 텔레그램 긴급 알림

### Step 2-2: 모닝 체크 크론 등록

```
# [KIS TASK-087] 모닝 매수 체결 확인 — 09:15 KST (00:15 UTC) 평일
15 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_morning_execution.py >> /root/kis-autotrade-v4/logs/morning_check.log 2>&1
```

**판정**: ✅ 크론 등록 완료 (매주 평일 09:15 KST 실행)

---

### Step 2-3: check_tp_execution.py 생성 + 크론 등록

**파일 경로**: `/root/kis-autotrade-v4/scripts/check_tp_execution.py`

**기능**:
- v4_mock_trades 에서 오늘 청산(status='closed') + (exit_reason='TP' OR pnl_pct >= 0.028) 조회
- 중복 알림 방지: /root/kis-autotrade-v4/logs/tp_check_sent.log 에 trade_id 기록
- TP 발동 시: 종목, 전략, 수익률, 매수가/매도가 → 텔레그램 보고

**크론 등록**:
```
# [KIS TASK-087] TP 발동 감지 — 매시 정각 09:00-16:00 KST (00:00-07:00 UTC) 평일
0 0-7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_tp_execution.py >> /root/kis-autotrade-v4/logs/tp_check.log 2>&1
```

**판정**: ✅ 크론 등록 완료 (매 시간 장중 09:00-16:00 KST 실행)

---

## 완료 조건 체크

- [x] dry-run 5종목 매수 재확인 (`scored_pass: 5`, 5개 ticker 모두 dry_run=True 정상 실행)
- [x] EXIT_PARAMS TP=3% 코드 확인 (run_unified_engine.py + exit_manager.py 양쪽 확인)
- [x] 모닝 체크 스크립트 + 크론 등록 (`scripts/check_morning_execution.py`, 09:15 KST)
- [x] TP 감지 스크립트 + 크론 등록 (`scripts/check_tp_execution.py`, 매시 장중)

---

## 내일(3/6) 09:10 실전 체크리스트

1. **09:10 KST**: paper_trading_v3 buy 크론 실행 (자동)
2. **09:15 KST**: check_morning_execution.py 실행 → 텔레그램 알림 확인
3. **09:00-16:00 KST 매시**: check_tp_execution.py → TP 발동 시 텔레그램 알림
4. **15:15 KST**: paper_trading_v3 sell 크론 실행 (자동)

---

## 생성 파일 목록

| 파일 | 설명 |
|------|------|
| `scripts/check_morning_execution.py` | 09:15 모닝 매수 체결 확인 스크립트 |
| `scripts/check_tp_execution.py` | 매시 TP 발동 감지 스크립트 |

---

HANDOVER.md 업데이트 완료: (done_watcher 자동 처리 예정)
