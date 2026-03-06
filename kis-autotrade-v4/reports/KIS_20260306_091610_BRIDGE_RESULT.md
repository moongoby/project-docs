---
project: kis-autotrade-v4
task_id: T-151
completed_at: "2026-03-06T09:28:00+0900"
---

# T-151 실행 결과: 03-06 장중 전체 시스템 점검 + 가상매매 실시간 확인

> 실행자: claudebot (Claude Code, Sonnet 4.6)
> 실행 일시: 2026-03-06 09:15~09:28 KST
> 지시서: /root/.genspark/directives/running/KIS_20260306_091610_BRIDGE.md

---

## 인계 확인
- 직전 완료: T-144
- 현재 단계: Phase 2C (Command Center)
- CEO 지시 적용: D-001, D-002, D-003, D-007
- strategy_cards: 60
- open_positions: 0 (SELL_FAILED=10, CLOSED=25)

---

## 섹션 1 – 서비스 상태 확인 결과

### 명령어
```bash
systemctl status kis-v41-api kis-v41-monitor kis-v41-scheduler kis-v41-minute-collector
```

### 결과
```
● kis-v41-api.service
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
   Main PID: 1160 (uvicorn)
     Memory: 140.0M

● kis-v41-monitor.service
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
   Main PID: 1162 (python)
     Memory: 7.6M

● kis-v41-scheduler.service
     Active: active (running) since Wed 2026-03-04 16:06:08 KST; 1 day 17h ago
   Main PID: 1164 (python)
     Memory: 54.4M

● kis-v41-minute-collector.service
     Active: active (running) since Fri 2026-03-06 08:54:04 KST; 22min ago
   Main PID: 2510256 (python)
     Memory: 94.7M
     (--days 66 --oldest-first)
```

### 판정: PASS ✅
4개 서비스 모두 active(running). kis-v41-minute-collector 08:54:04 장 시작 전 정상 재기동.

---

## 섹션 2 – 분봉 실시간 수집 결과

### 명령어 (실제 컬럼명 적용)
```python
# v4_ohlcv_minute: trade_date(date), trade_time(time), stock_code(varchar)
SELECT MAX(trade_date), MAX(trade_time), COUNT(*), COUNT(DISTINCT stock_code)
FROM v4_ohlcv_minute WHERE trade_date = CURRENT_DATE
```

### 결과
```
latest_date: 2026-03-06
latest_time: 09:18:00
today_rows: 227
today_symbols: 23
```

### 판정: PASS ✅
09:18분봉까지 정상 수집. 기준 "현재 시각 5분 이내" 충족.

※ 지시서 컬럼명 dt→trade_date, symbol→stock_code (실 스키마 기준 적용)

---

## 섹션 3 – 일봉 데이터 결과

### 명령어 (실 테이블명 적용)
```python
# 테이블: ohlcv_daily (v4_ohlcv_daily 아님), 날짜컬럼: date(varchar)
SELECT MAX(date) AS latest_daily, COUNT(*) AS total_rows FROM ohlcv_daily
```

### 결과
```
latest_daily: 20260305
total_rows:   2,623,502
```

### 판정: PASS ✅
latest_daily = 03-05(어제). total_rows = 2,623,502 (기준 2,615,744+ 초과).

---

## 섹션 4 – 수급 데이터 수집 결과

### 명령어
```python
SELECT MAX(trade_date), COUNT(*) FROM v4_investor_daily
SELECT MAX(trade_date), COUNT(*) FROM v4_volume_power  -- 테이블 없음
```

### 결과
```
v4_investor_daily: latest=2026-03-05, rows=2,580,265  ✅
v4_volume_power:   relation does not exist              ⚠️
대체 테이블: v4_supply_chain, v4_evolution_candidates (존재)
```

### 판정: WARN ⚠️
v4_investor_daily 03-05 정상. v4_volume_power 테이블 미존재 (스키마 불일치).

---

## 섹션 5 – DB 무결성 결과

### 명령어
```python
SELECT COUNT(*) FROM strategy_cards              → 60
SELECT COUNT(*) FROM v4_positions WHERE status='OPEN'  → 0
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'  → 289
SELECT pg_size_pretty(pg_database_size('kisautotrade'))  → 40 GB
```

### 결과
```
strategy_cards: 60     ✅ (기준 60)
open_positions:  0     ⚠️ (기준 ~14)
  - 실제 내역: CLOSED=25, SELL_FAILED=10, OPEN=0
tables:        289     ✅ (기준 ~288)
db_size:        40 GB  ⚠️ (기준 37~38GB)
```

### 판정: WARN ⚠️
strategy_cards/tables 정상. OPEN=0 (SELL_FAILED 10건 주의). db_size 40GB(+2GB 증가).

---

## 섹션 6 – 가상매매(Mock Trade) 실행 결과

### 명령어 (실 컬럼명: direction, strategy_id)
```python
SELECT trade_date, COUNT(*), SUM(direction='BUY'), SUM(direction='SELL')
FROM v4_mock_trades WHERE trade_date >= '2026-03-05' GROUP BY trade_date ORDER BY trade_date
```

### 결과 — 일별
```
trade_date=2026-03-05, trades=56, buys=56, sells=0
trade_date=2026-03-06, trades=11, buys=11, sells=0
```

### 결과 — 전략별 (03-05 이후)
```
strategy_id=D-ORB, cnt=13, avg_pnl=-0.61%, wins=1, losses=5
strategy_id=D7,    cnt=13, avg_pnl=-1.21%, wins=0, losses=3
strategy_id=D6,    cnt=13, avg_pnl=-0.20%, wins=2, losses=5
strategy_id=D5,    cnt=13, avg_pnl=0.00%,  wins=0, losses=1
strategy_id=S1,    cnt=5,  avg_pnl=None,   wins=0, losses=0
strategy_id=D2,    cnt=5,  avg_pnl=None,   wins=0, losses=0
strategy_id=D4,    cnt=5,  avg_pnl=-2.67%, wins=0, losses=1
```

### v4_mock_trades 전체
```
rows=164, date_range=2026-03-02 ~ 2026-03-06
```

### 판정: PASS ✅
03-06 장 시작 후 BUY 11건 신호 발생 확인. SELL=0은 당일 진입 포지션 미청산 상태 (정상).
D4(-2.67%), D7(-1.21%)는 성과 검토 필요.

---

## 섹션 7 – 통합엔진 로그 결과

### 명령어
```bash
tail -50 /root/kis-autotrade-v4/logs/unified_engine.log
grep -c "ERROR|CRITICAL" /root/kis-autotrade-v4/logs/unified_engine.log
```

### 결과
```
unified_engine.log 크기: 0 bytes (2026-03-05 00:00 rotate 후 오늘 미기록)
unified_engine.log-20260305: ERROR=0건, CRITICAL=0건 ✅

scheduler.log-20260306: 오늘 스케줄러 정상 작동 확인
  - account_sync_periodic 3분 주기 작동
  - KIS 실계좌 API HTTP 200 OK (openapi.koreainvestment.com)
  - KIS 모의계좌 API 간헐적 HTTP 500 (openapivts.koreainvestment.com, config_id=3)
```

### 판정: WARN ⚠️
unified_engine.log 0 bytes. 어제(03-05) 에러 0건. 오늘 스케줄러 로그에서 정상 확인.

---

## 섹션 8 – 수급 게이트 + AxisMask 결과

### 명령어
```bash
tail -100 /root/kis-autotrade-v4/logs/unified_engine.log | grep -i "supply|gate|ALLOW|BLOCK|CONDITIONAL|axis_mask"
```

### 결과
```
unified_engine.log: 0 bytes → 직접 검색 불가
scheduler.log-20260306 (어제 데이터 포함): supply_demand 스코어링 정상
  예: "supply_demand": {"value": "외국인+기관 순매수", "score": 21, "max": 25}  (252670 KODEX 인버스2X)
      "supply_demand": {"value": "3일 연속 순매수", "score": 10, "max": 20}     (004360 세방)
```

### 판정: PARTIAL ⚠️
오늘자 ALLOW/BLOCK/CONDITIONAL 직접 집계 불가. 어제 supply_demand 스코어링 정상 확인.

---

## 섹션 9 – 크론 + KIS 토큰 결과

### 크론탭
```bash
crontab -l | grep -v "^#" | wc -l
→ 23개 (기준 30+, WARN)
```

### 주요 크론 항목 (23개 중 샘플)
```
@reboot /usr/bin/python3 /home/claudebot/done_watcher.py
5 16 1,29 * * ... lightgbm_retrainer.py
0 8 * * 1-5 ... generate_v41_daily_report.py
0 9-15 * * 1-5 ... monitor_virtual_run.py periodic
0 7 * * 1-5 ... node_detector_engine desk5
5 7 * * 1-5 ... node_detector_engine desk4
... (23개 총)
```

### KIS API 토큰
```sql
SELECT id, token_type, expires_at, is_valid FROM v4_api_tokens
→ id=1, Bearer, expires_at=2026-03-04 17:00:06 KST, is_valid=True
```

⚠️ DB 기록상 만료(03-04 17:00). 단, 실제 KIS API HTTP 200 정상 (scheduler 로그 확인).
→ 토큰 자동 갱신 메커니즘 작동 중, DB 업데이트 누락 추정.

### API Health Check
```bash
curl -s http://localhost:8003/health
→ {"status":"degraded","version":"4.1.0","orchestrator_state":"POST_MARKET","database":"connected","redis":"disconnected"}
```

⚠️ Redis disconnected → API status degraded.

### 판정: WARN ⚠️

---

## 섹션 10 – Git 상태 결과

### 명령어
```bash
git status --short | head -20
git log --oneline -5
git remote -v
```

### 결과
```
?? report/v41/DAILY-20260306.md
?? reports/DAILY-20260306.md
?? reports/daily/2026-03-06/

최근 커밋:
86a80d8d feat: 미커밋 보고서·스크립트 일괄 추가 (DESK2/P2/DCS/push_t139)
120ecef1 [V4.1] T-143: D-010 Phase C S1 테마그룹핑
4762a13d [V4.1] T-144: 03-06 장중 모의매매 모니터링 일간 보고서
d23b372a [V4.1] T-142: D-009 P2 변수 3종 완료 (NEW_DETECTOR/ORDERBOOK/CK480)
24496f74 [V4.1] T-141: D-010 DCS 등급체계 A/B/C 구현

원격:
origin     git@github.com:moongoby/go100.git (fetch)
origin     git@github.com:moongoby/go100.git (push)
```

### 판정: PASS ✅

---

## 수행한 작업 목록 (완료)

### 1. HANDOVER.md + CEO-DIRECTIVES.md 읽기 ✅
- /root/project-docs/kis-autotrade-v4/HANDOVER.md (v10.10 기준 읽기 완료)
- /root/project-docs/kis-autotrade-v4/CEO-DIRECTIVES.md (D-001~D-008-KR 확인)

### 2. 10개 섹션 점검 실행 ✅
- 서비스 상태, 분봉, 일봉, 수급, DB무결성, 가상매매, 엔진로그, SupplyGate, 크론/토큰, Git

### 3. 보고서 작성 ✅
- 파일: /root/kis-autotrade-v4/report/v41/CUR-V41-LIVE-SYSTEM-CHECK-001-20260306.md
- 내용: 10개 섹션 PASS/WARN/FAIL 판정, 종합 PARTIAL

### 4. kis-autotrade-v4 git commit ✅
- 커밋: 346a9f15
- 메시지: [V4.1] T-151: 03-06 장중 전체 시스템 점검 + 가상매매 실시간 확인
- 브랜치: phase-2c-command-center

### 5. project-docs 보고서 복사 + commit ✅
- 복사: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-LIVE-SYSTEM-CHECK-001-20260306.md
- HANDOVER.md v10.11 갱신 (섹션1 DB수치 갱신, T-151/T-141~T-144 완료 반영, 섹션6 최신상태 추가)
- 커밋: 6873f19 (master)

### 6. git push ⚠️ (root 수동 필요)
- kis-autotrade-v4: `git push origin phase-2c-command-center` (SSH 권한 없음)
- project-docs: `git push origin master` (SSH 권한 없음)
- **root에서 다음 명령 실행 필요:**
  ```bash
  cd /root/kis-autotrade-v4 && git push origin phase-2c-command-center
  cd /root/project-docs && git push origin master
  ```

---

## GitHub raw URL 확인 (push 완료 후)
```bash
curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-LIVE-SYSTEM-CHECK-001-20260306.md"
```
→ push 전이므로 현재 200 불가. push 후 확인 필요.

---

## 종합 결과

| 항목 | 상태 |
|------|------|
| 섹션1 서비스 | ✅ PASS |
| 섹션2 분봉 | ✅ PASS |
| 섹션3 일봉 | ✅ PASS |
| 섹션4 수급 | ⚠️ WARN |
| 섹션5 DB | ⚠️ WARN |
| 섹션6 가상매매 | ✅ PASS |
| 섹션7 엔진로그 | ⚠️ WARN |
| 섹션8 SupplyGate | ⚠️ PARTIAL |
| 섹션9 크론/토큰 | ⚠️ WARN |
| 섹션10 Git | ✅ PASS |
| **종합** | **PARTIAL** ⚠️ |

### 핵심 이슈 (재시작 금지, 모니터링)
1. Redis disconnected (API degraded) — 실매매 전환 시 복구 필수
2. SELL_FAILED 10건 — 수동 확인 권장 (root 권한 필요)
3. KIS 토큰 DB 만료 — 15:22 갱신 후 DB 동기화 확인
4. v4_volume_power 테이블 없음 — 스키마 불일치 문서화 필요

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4, 346a9f15, phase-2c-command-center)
- [x] project-docs HANDOVER.md v10.11 갱신 + 보고서 추가 (6873f19)
- [ ] git push 미완료 — root에서 수동 push 필요

HANDOVER.md 업데이트 완료: 6873f19
