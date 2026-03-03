---
project: KIS V4.1 AutoTrade
task_id: CUR-V41-EMERGENCY-DIAG-001
completed_at: 2026-03-03 08:59 KST
---

# CUR-V41-EMERGENCY-DIAG-001 긴급 진단 결과

## 핵심 결론: 엔진 정상 — 로그 경로 오인이 원인

CEO가 확인한 경로 `/root/kis-autotrade-v4/logs/unified_engine.log`는 존재하지 않음.
**실제 로그 경로: `/var/log/unified_engine.log`** (366KB, 최신 08:50 업데이트 확인)

---

## STEP_1 진단 결과

### 로그 파일 위치
| 확인 경로 | 존재 여부 |
|-----------|-----------|
| `/root/kis-autotrade-v4/logs/unified_engine.log` | ❌ 없음 (CEO가 확인한 경로) |
| `/var/log/unified_engine.log` | ✅ 존재 (366,253 bytes, root 소유) |

### scripts 파일 존재 확인
- `/root/kis-autotrade-v4/scripts/monitor_virtual_run.py` — ✅ 존재
- `/root/kis-autotrade-v4/scripts/run_unified_engine.py` — ✅ 존재 (root 위치 아님)

### 오늘(2026-03-03) 엔진 실행 이력
```
07:55:01 [PREMARKET] 완료 — DB 연결 PASS, Mock API 확인
08:50:02 [SIGNAL]    완료 — 통과 3개, 차단 4개
```

### cron 등록 상태
- `/etc/cron.d/` 에 unified_engine 관련 cron 없음
- claudebot crontab: done_watcher.py만 등록
- root crontab: claudebot 읽기 불가 (권한)
- 엔진이 어떻게 07:55, 08:50에 실행됐는지는 root crontab 확인 필요

### 실행 중인 관련 프로세스
```
PID 3029739: /root/kis-autotrade-v4/venv/bin/python -m app.services.scheduler.daily_scheduler
PID 3029738: position_monitor.py
PID 3029747: v4_position_monitor.py
PID 246683: unified_trading_scheduler.py (/root/webapp/)
```

---

## STEP_2 결과

```
mkdir /root/kis-autotrade-v4/logs/shadow → Permission denied
```
- `/root/kis-autotrade-v4/logs/` 는 go100user 소유 (755)
- claudebot 쓰기 불가 → **root 권한으로 별도 생성 필요**
- 명령: `sudo mkdir -p /root/kis-autotrade-v4/logs/shadow`

---

## STEP_3 premarket 수동 실행 결과

07:55:01 이미 자동 실행 완료 상태였으나, 08:59:17 수동 재실행 성공:

```
2026-03-03 08:59:17 [INFO] CTE 모듈 로드 성공
2026-03-03 08:59:17 [INFO] 통합 엔진 시작: mode=virtual action=premarket data-source=db
2026-03-03 08:59:17 [INFO] [PREMARKET] 08:59:17 — 장 전 준비 시작
2026-03-03 08:59:17 [INFO]   KIS Mock URL: https://openapivts.koreainvestment.com:29443
2026-03-03 08:59:17 [INFO]   VIRTUAL_ACCOUNT: 50160697
2026-03-03 08:59:17 [INFO]   DB 연결 PASS
2026-03-03 08:59:17 [INFO] [PREMARKET] 완료
2026-03-03 08:59:17 [INFO] 통합 엔진 종료
```

실행 명령: `venv/bin/python3 scripts/run_unified_engine.py --mode virtual --action premarket`

---

## STEP_4 DB 상태 (v4_mock_trades 오늘 7행)

| ticker | strategy | direction | entry_price | result |
|--------|----------|-----------|-------------|--------|
| 182487 | D6 | BUY | 80,322 | ✅ 통과 (CS:86, EQS:54) |
| 529671 | D5 | BUY | - | ❌ GATE차단: 반등확인 미통과 |
| 702721 | D4 | BUY | - | ❌ L3.3_SUPPLY: synthetic_BLOCK |
| 884760 | D2 | BUY | 67,721 | ✅ 통과 (CS:74, EQS:62) |
| 196979 | S1 | BUY | - | ❌ L3.3_SUPPLY: synthetic_BLOCK |
| 956527 | D7 | BUY | - | ❌ L3.3_SUPPLY: synthetic_BLOCK |
| 645820 | D-ORB | BUY | 147,818 | ✅ 통과 (CS:59, EQS:68) |

**통과: 3건, 차단: 4건**

---

## 부가 발견: unified_trading_scheduler 에러

`/var/log/kis-autotrade/unified_trading_scheduler.log` 최신 에러:
```
❌ 에러: operator does not exist: boolean = integer
SQL: WHERE user_id = 6 AND is_active = 1
```
→ user_strategies 테이블 is_active 컬럼 타입 불일치 (boolean vs integer)
→ 별도 수정 태스크 권고

---

## 최종 상태 요약

| 항목 | 상태 |
|------|------|
| unified_engine.log 존재 | ✅ /var/log/unified_engine.log |
| PREMARKET 실행 | ✅ 07:55 자동 + 08:59 수동 성공 |
| SIGNAL 실행 | ✅ 08:50 완료 (통과 3/7) |
| DB 기록 | ✅ 7행 저장 완료 |
| logs/shadow 생성 | ❌ root 권한 필요 |
| 장 시작 대응 | ✅ 이상 없음 |
