# MINUTE-COLLECTOR-STATUS 보고서 (2026-02-23)

**서버:** 211.188.51.113  
**경로:** /root/kis-autotrade-v4  
**성격:** 읽기 전용 확인

---

## 사전 확인 결과

| 항목 | 기대값 | 실제 | 결과 |
|------|--------|------|------|
| strategy_cards COUNT | 62 | 62 | ✓ |
| v4_positions OPEN | 5 | 5 | ✓ |
| kis-v41-api | active | active (running) | ✓ |
| kis-v41-monitor | active | active (running) | ✓ |
| kis-v41-scheduler | active | active (running) | ✓ |
| 디스크 / | - | 53% (50G/99G) | ✓ |

---

## 1. minute-collector 서비스 상태

**inactive (dead)**  
- Exit: status=1/FAILURE  
- 마지막 중지: 2026-02-22 15:34:01 KST (약 13시간 전)  
- Process: ExecStart=.../collector_minute (code=exited, status=1/FAILURE)

---

## 2. orderbook-collector 서비스 상태

**inactive (dead)**  
- Loaded, **disabled**  
- 유닛 주석: "등록만 하고 enable/start는 하지 않음 (월요일 장전에 시작)"

---

## 3. 프로세스 실행 여부

**N** (PID 없음)  
- `ps aux | grep -E "collector_minute|orderbook_collector"` 결과 없음

---

## 4. v4_ohlcv_minute

| 항목 | 값 |
|------|-----|
| **총 행수** | 35,029,032 |
| **최초 데이터** | 2025-02-18 09:00:00 |
| **최신 데이터** | 2026-02-19 16:00:00 |
| **최근 7일 일별 행수** | 2026-02-19: 189,204 (그 외 일자 없음) |
| **2/20 이후 일별 종목수·행수** | 0건 (2/20 이후 데이터 없음) |

- 테이블 컬럼: `trade_date`, `trade_time` (datetime 아님). 최신 거래일은 **2026-02-19**까지이며, 2/20·2/22·2/23 분봉 미수집.

---

## 5. v4_orderbook_realtime

| 항목 | 값 |
|------|-----|
| **총 행수** | 0 |
| **최초 ~ 최신** | (데이터 없음) |
| **최근 7일 일별 행수** | (없음) |

- 호가 수집기는 미가동 설계(월요일 장전 시작 예정). 실데이터 없음.

---

## 6. v4_scalping_universe

| 항목 | 값 |
|------|-----|
| **총 행수** | 708 |
| **최신 날짜** | 2026-02-21 (earliest/latest 동일일) |

---

## 7. 수집 주기/간격

- **minute-collector**  
  - `API_INTERVAL = 0.15` (150ms)  
  - `sleep(2)` 초기 대기, `sleep(wait_sec)` 토큰 갱신 대기, `sleep(API_INTERVAL)` 요청 간격, `sleep(300)` 장 종료 후 대기  
- **orderbook-collector**  
  - `COLLECT_INTERVAL_SEC = 3` (3초), `sleep(60)` 에러 시 대기

---

## 8. API 토큰 키 존재 여부

**Y**  
- .env에 존재: `KIS_APP_KEY=***`, `KIS_APP_SECRET=***`  
- (값 출력 금지 준수)

---

## 9. 2026-02-23 장 운영일 여부

**v4_market_calendar에 2026-02-23 행 없음** (0 rows)  
- 컬럼: `date`, `event_type`, `desk1_active` 등.  
- 해당 일자가 캘린더에 등록되지 않았거나, 월요일 장일이어도 아직 행이 없는 상태로 해석 가능.

---

## 10. 최근 로그 요약 (에러/경고)

### minute-collector (2026-02-22)

- 실전계좌 감지·토큰 검증 성공, "분봉 수집 시작" 직후 **실패**.
- **에러:**  
  `asyncpg.exceptions.UndefinedFunctionError: operator does not exist: boolean = integer`  
  **HINT:** No operator matches the given name and argument types. You might need to add explicit type casts.
- **발생 위치:**  
  `collector_minute.py` → `_get_target_stocks()` → SQL 실행 시.  
  **원인:** `stock_universe.is_active`는 boolean인데 쿼리에서 `su.is_active = 1`(integer)로 비교함.  
  **수정 제안:** `WHERE su.is_active = 1` → `WHERE su.is_active = true` (또는 `IS TRUE`).  
  **규칙:** 본 작업은 읽기 전용이므로 코드 수정은 하지 않음. 활성화 지시서에서 반영 권장.

### orderbook-collector

- 2026-02-22 이후 journal 로그 없음 (No entries). 미가동 상태와 일치.

---

## 11. strategy_cards COUNT

**62**

---

## 12. v4_positions OPEN

**5**

---

## 13. 이슈

1. **분봉 수집기 비가동**  
   - 서비스 inactive(dead), 실패 후 재시작해도 동일 SQL 오류로 재실패할 가능성 높음.  
   - **조치:** `collector_minute.py` 445행 `su.is_active = 1` → `su.is_active = true` 수정 후 서비스 재시작 필요.  
   - 월요일 장 전 분봉 수집을 위해 **수집기 활성화 지시서** 별도 작성 권장.

2. **분봉 데이터 공백**  
   - 최신 분봉이 2026-02-19까지. 2/20, 2/22, 2/23 분봉 없음.  
   - 수집기 수정·가동 후 당일(2/23) 분봉 수집 및 필요 시 2/22 백필 여부 검토.

3. **호가 수집기**  
   - 설계상 월요일 장전 시작 예정. 현재 inactive·데이터 없음은 의도와 일치.

4. **시스템 유닛 경고**  
   - minute/orderbook-collector 등 유닛 파일 변경 후 `systemctl daemon-reload` 미실행 경고 있음.  
   - 재시작/활성화 전에 `sudo systemctl daemon-reload` 실행 권장.

---

**보고 완료.**  
다음: Tab 1 결과에 따라 월요일 장 전 수집기 활성화 지시서 작성 및 DESK2 분봉 재BT 투입 여부 결정.
