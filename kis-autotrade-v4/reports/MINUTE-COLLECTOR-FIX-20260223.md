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
