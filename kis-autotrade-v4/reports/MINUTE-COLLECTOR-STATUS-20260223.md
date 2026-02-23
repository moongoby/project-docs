# MINUTE-COLLECTOR-STATUS 보고서
- 날짜: 2026-02-23
- 작업자: Cursor
- 우선순위: P0

## 사전 확인
- strategy_cards: **62** (기대 62 ✓)
- v4_positions OPEN: **5** (기대 5 ✓)
- 서비스 kis-v41-api / kis-v41-monitor / kis-v41-scheduler: **전부 active** ✓

## 분봉 수집기 상태
- systemd 상태: **activating (auto-restart)** — 프로세스가 exit-code 1로 반복 실패 후 60초마다 재시작 (restart counter 517+)
- enabled 여부: **enabled**
- 서비스 파일 경로: `/etc/systemd/system/kis-v41-minute-collector.service`
- 실행 명령: `ExecStart=/root/kis-autotrade-v4/venv/bin/python -m backend.app.services.data_pipeline.collector_minute`
- **실패 원인**: `_get_target_stocks()` 내 SQL — `asyncpg.exceptions.UndefinedFunctionError: operator does not exist: boolean = integer`  
  - `stock_universe.is_active` 컬럼은 **boolean**인데, 쿼리에서 `WHERE su.is_active = 1` (integer) 사용 → PostgreSQL에서 boolean = integer 비교 불가.  
  - 수정 시: `su.is_active = true` 또는 `su.is_active IS TRUE` 로 변경 필요 (본 점검에서는 코드 수정 금지 규칙으로 미수행).

## 호가 수집기 상태
- systemd 상태: **inactive (dead)**
- enabled 여부: **disabled**
- 비고: 서비스는 등록됨 (`/etc/systemd/system/kis-v41-orderbook-collector.service`), 현재 미가동.

## crontab
- minute-collector 관련 크론: **있음** (과거 분봉 배치만, 실시간 분봉 수집 아님)
  - `0 16 * * 1-5` → `/root/kis-autotrade-v4/scripts/minute_batch_cron.sh` (장후 16:00 평일)
  - `0 2 * * 6` → 동일 스크립트 (토요일 02:00)
- 실시간 분봉 수집: **systemd 서비스**로 동작 예정 (스케줄러 08:55 start, 15:35 stop). crontab에서 직접 minute-collector 서비스 기동 없음.

## 분봉 데이터 현황 (v4_ohlcv_minute)
- 총 행수: **35,029,032** (기준 19,468,781 대비 충분)
- 종목 수: **547** (기준 499+ 충족)
- 최초 수집일: **2025-02-18**
- 최근 수집일: **2026-02-19**
- 거래일 수: **225**
- 최근 10일 수집 현황:

| dt         | rows   | stocks |
|-----------|--------|--------|
| 2026-02-19 | 189,204 | 500 |
| 2026-02-13 | 189,302 | 500 |
| 2026-02-12 | 188,736 | 500 |
| 2026-02-11 | 188,171 | 501 |
| 2026-02-10 | 187,812 | 500 |
| 2026-02-09 | 187,638 | 500 |
| 2026-02-06 | 187,453 | 500 |
| 2026-02-05 | 187,343 | 499 |
| 2026-02-04 | 186,990 | 499 |
| 2026-02-03 | 186,884 | 498 |

- **데이터 갭**: 2026-02-20(금) 분봉 미수집 (DB 최신일 2026-02-19). 2026-02-21~23은 주말/휴장으로 미수집 정상.

## 스캘핑 유니버스
- 총 종목: **708** (unique_stocks 708) — 기준 708 ✓

## 월요일 활성화 절차
- 활성화 방법: **스케줄러(kis-v41-scheduler)에서 systemd 제어**  
  - `daily_scheduler.py`: `minute_collector_start` 08:55, `minute_collector_stop` 15:35  
  - 08:55에 `systemctl start kis-v41-minute-collector` 실행, 15:35에 `systemctl stop kis-v41-minute-collector` 실행.
- systemd timer: **없음** (`systemctl list-timers` 내 minute/collector 항목 없음).
- 활성화 시간: **장전 08:55 KST** (스케줄러에 의해 start 호출).
- 현재 상태: 서비스가 **실패로 인해 정상 기동되지 않음** — 스케줄러가 start 해도 프로세스가 곧바로 exit-code 1로 종료.

### 필요 조치 (코드 수정 별도 작업)
1. `collector_minute.py` 내 `_get_target_stocks()` SQL에서 `WHERE su.is_active = 1` → `WHERE su.is_active = true` (또는 `IS TRUE`) 로 변경.
2. 변경 후 서비스 재시작은 **CEO 승인 후** 수행 (본 작업 규칙상 재시작 금지).

## CEO 보고 사항
1. **분봉 수집기 정상 여부**: **비정상** — SQL 타입 오류(boolean = integer)로 기동 즉시 실패, 60초마다 auto-restart 반복.
2. **월요일 활성화 준비 완료 여부**: **미완료** — 위 SQL 수정 및 (승인 후) 서비스 재시작 전까지 월요일 08:55 자동 기동 시에도 동일 실패 예상.
3. **데이터 갭 존재 여부**: **있음** — 2026-02-20(금) 분봉 미수집. 2026-02-21~23은 휴장/주말으로 정상.
4. **권장 조치**:  
   - P0: `collector_minute.py` 427행 근처 `su.is_active = 1` → `su.is_active = true` 수정 후, CEO 승인 하에 `systemctl restart kis-v41-minute-collector` 1회 실행.  
   - 2026-02-20 갭은 과거 분봉 배치(`minute_batch_cron.sh`) 또는 별도 배치로 보강 검토.

## 영향
- DB: 없음 (조회만)
- 코드: 없음 (수정 금지 준수)
- 서비스: 없음 (재시작/활성·비활성 변경 없음)

## 컴플라이언스
- [x] .env/.bak 커밋: 없음
- [x] strategy_cards: 62건 유지
- [x] v4_positions OPEN: 5건 유지
- [x] 서비스 재시작: 없음
- [x] 수집기 활성화/비활성화: 없음
- [x] crontab 수정: 없음
