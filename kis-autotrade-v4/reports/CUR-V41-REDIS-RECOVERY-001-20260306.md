# T-153: CEO 승인 Redis 재시작 + API 복구 + SELL_FAILED 진단

[인계 확인]
직전 완료: T-151
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001 (Redis 재시작 승인 2026-03-06 09:30 KST)
strategy_cards: 확인 불요
open_positions: SELL_FAILED=10, CLOSED=25

---

**작업일:** 2026-03-06
**작업자:** claudebot (auto_trigger)
**우선순위:** P0-CRITICAL
**CEO 승인:** 2026-03-06 09:30 KST — Redis 재시작 및 kis-v41-api 재시작 허가

---

## 1. 복구 전 상태 스냅샷

**시각:** 2026-03-06 09:35:28 KST

### Redis 상태
```
● redis-server.service - Advanced key-value store
     Active: active (running) since Wed 2026-03-04 16:06:06 KST; 1 day 17h ago
   Main PID: 853 (redis-server)
   Status: "Ready to accept connections"
redis-cli ping → PONG
```

### API 상태 (복구 전)
```json
{
  "status": "degraded",
  "version": "4.1.0",
  "orchestrator_state": "TRADING",
  "database": "connected",
  "redis": "disconnected"
}
```
- **이상**: redis가 실제로는 살아있는데 API가 "disconnected" 응답

### v4_positions 상태별 카운트
```
   status    | count
-------------+-------
 CLOSED      |    25
 SELL_FAILED |    10
```

---

## 2. Redis 재시작 결과 (Step 2)

```bash
systemctl restart redis
→ EXIT CODE: 1 (Failed — claudebot은 systemctl restart 권한 없음, root 필요)
redis-cli ping → PONG (Redis 기존 PID 853 그대로 동작 중)
```

**결론:** Redis 자체는 정상 동작 중. 실제 restart 미수행 (root 권한 필요).
**Redis PID:** 853 (2026-03-04 16:06:06부터 유지)
**Root 조치 필요:** `systemctl restart redis-server`

---

## 3. API 복구 결과 (Step 3)

```bash
systemctl restart kis-v41-api
→ "Failed to restart kis-v41-api.service: Interactive authentication required."
→ EXIT CODE: 1 (claudebot 권한 없음, root 필요)
```

**결론:** API 재시작 미수행. Redis 연결 복구 실패.
**현재 API 상태:** degraded (redis: disconnected)
**Root 조치 필요:** `systemctl restart kis-v41-api`

---

## 4. 다른 서비스 영향 없음 확인 (Step 4)

재시작 금지 대상 3개 서비스 모두 정상:

| 서비스 | 상태 | 시작 시각 | Main PID |
|--------|------|----------|----------|
| kis-v41-monitor | active (running) | 2026-03-04 16:06:08 KST | 1162 |
| kis-v41-scheduler | active (running) | 2026-03-04 16:06:08 KST | 1164 |
| kis-v41-minute-collector | active (running) | 2026-03-06 08:54:04 KST | 2510256 |

→ **3개 모두 active(running) 유지. 영향 없음.**

---

## 5. SELL_FAILED 10건 전수 진단 (Step 5)

### 원시 데이터
```
id=72, ticker=A005870, desk_id=2, entry=9310, exit_price=None, pnl=0.0%, exit_reason='가격 불명 보수적 청산', created=2026-03-03 15:17
id=73, ticker=A027360, desk_id=2, entry=5310, exit_price=None, pnl=0.0%, exit_reason='가격 불명 보수적 청산', created=2026-03-03 15:17
id=74, ticker=A028670, desk_id=2, entry=6269, exit_price=None, pnl=0.0%, exit_reason='가격 불명 보수적 청산', created=2026-03-03 15:17
id=68, ticker=006340,  desk_id=3, entry=5510, exit_price=None, pnl=9.80%, exit_reason='가격 불명 보수적 청산', created=2026-02-25 21:26
id=67, ticker=A005930, desk_id=2, entry=197950, exit_price=None, pnl=0.0%, exit_reason='가격 불명 보수적 청산', created=2026-02-24 11:52
id=65, ticker=419430,  desk_id=4, entry=11247, exit_price=None, pnl=4.69%, exit_reason='가격 불명 보수적 청산', created=2026-02-24 09:30
id=64, ticker=004060,  desk_id=4, entry=455, exit_price=None, pnl=40.22%, exit_reason='가격 불명 보수적 청산', created=2026-02-24 09:14
id=61, ticker=360140,  desk_id=4, entry=12935, exit_price=None, pnl=4.21%, exit_reason='가격 불명 보수적 청산', created=2026-02-20 09:05
id=53, ticker=001290,  desk_id=4, entry=1175, exit_price=None, pnl=10.89%, exit_reason='가격 불명 보수적 청산', created=2026-02-20 09:01
id=51, ticker=001510,  desk_id=4, entry=1579, exit_price=None, pnl=21.28%, exit_reason='가격 불명 보수적 청산', created=2026-02-20 09:01
```

### 분석 요약

| 항목 | 내용 |
|------|------|
| 전체 건수 | 10건 |
| exit_reason | 전건 "가격 불명 보수적 청산" |
| exit_price | 전건 NULL |
| 원인 분류 | 가격 데이터 취득 실패 → 보수적 SELL_FAILED 처리 |
| desk 분포 | desk_id=2: 4건, desk_id=3: 1건, desk_id=4: 5건 |
| 발생 시점 | 2026-02-20, 2026-02-24, 2026-02-25, 2026-03-03 (4개 일자) |
| pnl 범위 | 0.0% ~ 40.22% (미확정, exit_price 없음) |
| 가상/실매매 | 가상매매 추정 (API 토큰 만료 상태에서 발생) |

### 원인 분류
- **분류: 가격 데이터 불명** (API에러/Redis 단절로 current_price 취득 실패)
- exit_price=NULL + exit_reason="가격 불명 보수적 청산" → 매도 시점에 현재가 조회 불가
- 2026-03-03 15:17 집중 발생 3건 (A005870, A027360, A028670): 장 마감 직전 일괄 처리 시도

### CEO 권고 SQL (승인 후 실행)
```sql
-- 상태별 검토 (CEO 승인 전 참고용)
-- 옵션 1: pnl > 0인 6건 → CLOSED로 전환 (수익 확정)
UPDATE v4_positions
SET status='CLOSED', exited_at=NOW()
WHERE status='SELL_FAILED' AND pnl_pct > 0;
-- 대상: id 51,53,61,64,65,68 (6건)

-- 옵션 2: pnl = 0인 4건 → 재매도 시도 또는 수동 처리
-- 대상: id 67,72,73,74 (4건)

-- 실행 전 반드시 CEO 승인 필요. 현재는 진단만 수행.
```

---

## 6. unified_engine.log 0 bytes 원인 확인 (Step 6)

```
-rw-rw-r-- 1 root root    0 Mar  5 00:00 unified_engine.log
-rw-rw-r-- 1 root root 1882 Mar  5 00:00 unified_engine.log-20260305
```

- **원인**: 로그 로테이션(매일 자정)으로 새 파일 생성 → 오늘 아직 unified_engine 미실행
- **unified_engine 크론**: 17:00 (generate_unified_daily_report.py) — 오전에는 0 bytes 정상
- **실행 프로세스**: 없음 (ps aux에 unified_engine 프로세스 없음)
- **결론**: 0 bytes는 비정상 아님. 매일 17:00에 daily report 생성 시 내용 기록됨

---

## 7. 크론 목록 전수 기록 (Step 7)

```
총 23개 (crontab -l 기준)

0 0-7 * * 1-5   check_tp_execution.py
0 10 1 * *      generate_unified_monthly_report.py
0 10 * * 6      generate_unified_weekly_report.py
0 1 1 * *       generate_v41_monthly_report.py
0 1 * * 6       run_research_pipeline.sh (go100)
0 1 * * 6       generate_v41_weekly_report.py
0 1 * * 6       run_research_pipeline.py
0 17 * * 1-5    generate_unified_daily_report.py
0 7 * * 1-5     node_detector_engine desk5
0 8 * * 1-5     generate_v41_daily_report.py --push
0 9-15 * * 1-5  monitor_virtual_run.py periodic
10 0 * * 1-5    run_paper_trading_v3.py --mode buy
10 7 * * 1-5    node_detector_engine desk3
15 0 * * 1-5    check_morning_execution.py
15 6 * * 1-5    run_paper_trading_v3.py --mode sell
30 7 * * 1-5    node_detector_engine daily_summary
30 7 * * 5      run_paper_trading_v3.py --mode weekly_review
40 6 * * 1-5    check_stage_transition.py
50 23 * * 0-4   node_detector_engine desk3
50 8 * * 1-5    daily_ai_prediction_v3.sh
5 16 1,29 * *   lightgbm_retrainer.py --run
5 7 * * 1-5     node_detector_engine desk4
@reboot         done_watcher.py
```

**T-124(30+) 대비**: 7개 누락 가능성. T-124 크론 원본 대비 비교 필요.

---

## 8. KIS API 토큰 상태 (Step 8)

```
id=1, account_config_id=1, token_type='Bearer'
expires_at: 2026-03-04 17:00:06 KST
is_valid: True (DB 플래그)
issue_count_today: 1
```

**⚠️ 경고: 토큰 만료 (2일 경과)**
- expires_at = 2026-03-04 17:00:06 → 현재(03-06 09:37)보다 40.6시간 초과
- DB의 is_valid=True는 자동 갱신 미반영 (잘못된 플래그 가능성)
- **영향**: SELL_FAILED 발생에 기여했을 가능성 높음
- **조치 필요**: API 재시작 후 토큰 자동 갱신 확인 (또는 수동 갱신)

---

## 9. 복구 후 최종 상태 확인 (Step 9)

**시각:** 2026-03-06 09:37:38 KST

```
Redis:                active (running) — PID 853 유지
kis-v41-api:          active (running) — redis: disconnected (재시작 미수행)
kis-v41-monitor:      active (running) — 정상
kis-v41-scheduler:    active (running) — 정상
kis-v41-minute-collector: active (running) — 정상
redis-cli ping:       PONG
API health:           degraded (redis: disconnected)
OHLCV 수집:           최신 09:36, 오늘 420건
```

---

## 종합 판정

**판정: PARTIAL**

| 항목 | 결과 | 비고 |
|------|------|------|
| Redis 재시작 | ❌ 미수행 | claudebot root 권한 없음 |
| kis-v41-api 재시작 | ❌ 미수행 | Interactive auth 필요 |
| API redis 연결 복구 | ❌ 미완료 | 재시작 후 확인 필요 |
| 다른 서비스 보호 | ✅ 유지 | 3개 모두 running |
| SELL_FAILED 진단 | ✅ 완료 | 전건 "가격 불명 보수적 청산" |
| 크론 목록 기록 | ✅ 완료 | 23개 전수 |
| API 토큰 경고 | ⚠️ 만료 | 40.6시간 초과 |
| OHLCV 수집 | ✅ 정상 | 420건 수집 중 |

### Root가 즉시 수행해야 할 조치

```bash
# 1. Redis 재시작 (CEO 승인)
systemctl restart redis-server
sleep 3
redis-cli ping

# 2. kis-v41-api 재시작 (CEO 승인)
systemctl restart kis-v41-api
sleep 5
curl http://localhost:8003/health

# 3. API 토큰 갱신 확인
# API 재시작 후 자동 갱신 여부 확인
```

### SELL_FAILED 처리 (CEO 승인 후)
- 10건 전건: exit_reason = "가격 불명 보수적 청산"
- pnl > 0인 6건(id: 51,53,61,64,65,68): CLOSED로 전환 권고
- pnl = 0인 4건(id: 67,72,73,74): 개별 검토 후 결정

---

*보고서 작성: 2026-03-06 09:37 KST by claudebot*
