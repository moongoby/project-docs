# MINUTE-COLLECTOR-FIX 수정 보고서
> 날짜: 2026-02-23  
> 작업: CUR-MINUTE-COLLECTOR-FIX (boolean=integer 타입 수정)  
> 브랜치: phase-2c-command-center

## 1. 에러 원인
- **현상**: kis-v41-minute-collector가 activating 상태로 재시작 루프 (Main process exited, status=1/FAILURE)
- **예외**: `asyncpg.exceptions.UndefinedFunctionError: operator does not exist: boolean = integer`  
  HINT: No operator matches the given name and argument types. You might need to add explicit type casts.
- **위치**: `backend/app/services/data_pipeline/collector_minute.py`  
  `_get_target_stocks()` 내부, `conn.fetch()` 호출 시점 (라인 427 근처)
- **원인**: SQL에서 `stock_universe.is_active`(boolean)와 정수 리터럴 `1` 비교  
  PostgreSQL은 boolean과 integer 간 비교 연산자를 제공하지 않음.

## 2. 수정 내용

### AS-IS
```sql
WHERE su.is_active = 1
```
- docstring: `stock_universe.is_active=1`

### TO-BE
```sql
WHERE su.is_active = true
```
- docstring: `stock_universe.is_active=true`
- 파일 상단 헤더 주석 추가: `# CUR-MINUTE-COLLECTOR-FIX, 2026-02-23`

### 수정 범위
- 타입 비교값 변경만 적용. 로직 변경 없음.
- 수정 라인: 425(주석), 445(SQL), 상단 2행(헤더 주석)

## 3. 검증 결과
| 항목 | 결과 |
|------|------|
| 문법 검사 | `python -c "import ast; ast.parse(...)"` → SYNTAX OK |
| 임포트 검증 | `PYTHONPATH=... from backend.app...collector_minute import *` → IMPORT OK |
| 수정 SQL 실행 | psql에서 동일 쿼리 실행 → **500건** (TARGET_STOCK_COUNT=500) |

## 4. DB 무결성
| 항목 | 기준값 | 확인 |
|------|--------|------|
| strategy_cards | 62건 | 62 |
| v4_positions OPEN | 5건 | 5 |

- strategy_cards ALTER/DROP/DELETE 없음.
- v4_positions 직접 수정 없음.

## 5. 백업
- `backend/app/services/data_pipeline/collector_minute.py.bak.20260223_125950` 생성
- `.gitignore`에 `*.bak`, `*.bak.*` 포함으로 커밋 대상 아님

## 6. 서비스 재시작 (CEO 승인 완료)
- **승인 시각**: 2026-02-23 13:01 KST (장중 긴급)
- **재시작**: `systemctl restart kis-v41-minute-collector` 실행
- **결과**: active (running) since Mon 2026-02-23 13:00:14 KST
- **로그**: 에러 없이 분봉 API 호출 정상 (inquire-time-dailychartprice 200 OK)

## 7. 분봉 수집 재개 및 누락
- **수집 재개**: 13:00:14 이후 수집 시작. 최신 DB 기준 `v4_ohlcv_minute` MAX: trade_date=2026-02-20, trade_time=16:00 (수집기는 최근 거래일 우선으로 20260220 수집 진행 중).
- **2026-02-23 당일**: `SELECT COUNT(*) FROM v4_ohlcv_minute WHERE trade_date='2026-02-23'` → 0건 (13:xx 시점 기준). 09:00~13:0x 구간 누락. 장후 배치 수집 또는 별도 보충 예정.
- 실시간 수집 정상화로 13:0x 이후 데이터는 수집기 진행에 따라 적재됨.

## 8. 커밋
- **SHA**: a9df255ebfcfcb3e2fd85a50138fd531a8f95d32
- 메시지: `fix: CUR-MINUTE-COLLECTOR-FIX — boolean=integer 타입 캐스트 수정 (장중 긴급, CEO 승인)`
- 브랜치: phase-2c-command-center
- 푸시 완료 (원격 반영)

## 9. 절대 규칙 준수
- kis-v41-api, kis-v41-monitor, kis-v41-scheduler 재시작 없음
- strategy_cards / v4_positions 스키마·데이터 직접 수정 없음
- .env/.bak 파일 커밋 없음

---

## 10. Phase A 추가 — 배치 수집 경로 진단 (2026-02-23)

### 10.1 배치 스크립트 vs collector_minute
- **minute_batch_cron.sh** 호출 대상: `scripts/collect_minute_historical.py` (NOT `collector_minute.py`).
- 배치 경로는 **collector_minute.py를 사용하지 않음** → Phase C 수정(collector_minute.py)은 **배치와 무관**. 동일 SQL 미사용.

### 10.2 배치 전용 SQL (boolean 이슈 여부)
- `collect_minute_historical.py`의 `get_top_stocks()`: **ohlcv_daily만 사용**, `stock_universe` / `is_active` 미사용.
- **결론**: 배치 스크립트에는 `boolean = integer` 오류 **없음**. 별도 수정 불필요.

### 10.3 Cron 등록
- 평일 16:00: `0 16 * * 1-5 /root/kis-autotrade-v4/scripts/minute_batch_cron.sh`
- 토요일 02:00: `0 2 * * 6 /root/kis-autotrade-v4/scripts/minute_batch_cron.sh`

### 10.4 최근 배치 로그
| 로그 파일 | 크기 | 비고 |
|-----------|------|------|
| minute_hist_20260220.log-20260223 | 41MB | 목 16:00~ 일 07:00 수집 시도. INSERT 에러 다수 (trade_date str→date 타입) |
| minute_hist_20260221.log-20260223 | 79B | 토 02:00 "이미 실행 중 (PID 1383866). 건너뜀." 만 기록 |

### 10.5 금요일(02-21) 16:00 배치 및 DB 현황
- **v4_ohlcv_minute** (trade_date ≥ 2026-02-19):
  - 2026-02-19: **189,204건**
  - 2026-02-20: **12,183건**
  - 2026-02-21: **0건** (금요일 데이터 없음)
- 02-21 16:00 배치: 해당 일자 로그가 동일 파일(minute_hist_20260221.log)에 남지 않음. 토 02:00만 "이미 실행 중"으로 건너뜀 → **금 16:00 배치 미실행 또는 로그 유실 가능성**.
- 02-20 배치 로그: API는 정상 호출되었으나 **INSERT 에러** 반복 — `'str' object has no attribute 'toordinal'` (executemany 시 trade_date 인자 타입). 수집 행 0으로 종료. → **배치 경로는 별도 버그(날짜 타입)** 보유.

### 10.6 Phase C와 배치 관계 요약
- **같은 파일 아님**: 장중 수집 = `backend/.../collector_minute.py`, 배치 = `scripts/collect_minute_historical.py`.
- **1회 수정으로 양쪽 해결 여부**: 아니오. Phase C 수정은 **collector_minute.py 전용**. 배치 스크립트는 동일 SQL을 쓰지 않으며, boolean 오류는 없고 **INSERT 시 trade_date 타입 오류**만 존재.
