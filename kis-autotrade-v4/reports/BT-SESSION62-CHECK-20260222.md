# BT-SESSION62-CHECK 결과 (2026-02-22)

## 사전 확인 결과 (기준 충족)

| 항목 | 기준 | 결과 |
|------|------|------|
| strategy_cards COUNT | 59 | **59** ✓ |
| v4_positions OPEN | 5 | **5** ✓ |
| kis-v41-api | active (running) | **running** ✓ |
| kis-v41-monitor | active (running) | **running** ✓ |
| df -h / | 여유 확인 | **41% 사용, 56G 가용** ✓ |

---

## BT-SESSION62-CHECK 결과

| 항목 | 내용 |
|------|------|
| **세션 62 DB 상태** | RUNNING |
| **세션 62 시작 시간** | 2026-02-21 22:42:16 KST |
| **세션 62 경과 시간** | 약 2시간 29분 (02:29:15) |
| **관련 프로세스 생존** | **Y** (PID 2014474, `run_backtest.py --name BT-MIN-DESK2-2M` 실행 중, CPU 96.9%, Rl 상태) |
| **세션 62 거래 기록 수** | 1,094건 |
| **세션 62 거래 범위** | 2025-12-15 ~ 2026-01-13 |
| **판정** | **실행중** (프로세스 생존 + DB RUNNING + 거래 기록 증가 구간 진행 중) |
| **다른 RUNNING 세션** | 없음 (session_id 62만 RUNNING) |
| **세션 60 ROI** | (summary 없음) |
| **세션 60 승률** | - |
| **세션 60 MDD** | - |
| **세션 61 ROI** | 7.48% |
| **세션 61 승률** | 41.55% |
| **세션 61 MDD** | 7.38% |
| **strategy_cards COUNT** | 59 ✓ |
| **v4_positions OPEN** | 5 ✓ |
| **권장 조치** | **대기** (세션 62 정상 실행 중, 완료까지 모니터링 유지) |

---

## 상세 참고

- **세션 62**: `[DB] V2_BT-MIN-DESK2-2M`, created_at 2026-02-21 22:42:16, completed_at NULL.
- **프로세스**: `python scripts/backtest/run_backtest.py --start 20251215 --end 20260219 --capital 1000000 --name BT-MIN-DESK2-2M --engine v2 --timeframe minute ...` (PID 2014474) 정상 동작 중.
- **v4_backtest_sessions** 컬럼: `session_id`, `session_name`, `status`, `created_at`, `completed_at`, `stage_config`, `desk_configs` (작업지시의 id/name/started_at은 실제 스키마와 상이하여 위 컬럼으로 조회함).
- 본 작업은 **읽기 전용**이며, 세션 상태 UPDATE 및 backtest 관련 코드 수정 없음.

--- 보고 끝 ---
