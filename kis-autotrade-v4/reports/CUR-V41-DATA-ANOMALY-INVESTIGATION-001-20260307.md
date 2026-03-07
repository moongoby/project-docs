# T-262: DESK5 종목코드 이상 + Mock PnL 동일 구간 + 알림 중복 조사 및 수정

[인계 확인]
직전 완료: T-257
현재 단계: Phase 2c
CEO 지시 적용: D-001, D-002, D-007
strategy_cards: 60
open_positions: 0

---

## 1. 작업 개요

| 항목 | 내용 |
|------|------|
| Task ID | T-262 |
| 제목 | v4_desk5_watchlist 종목코드 이상 진단 + v4_mock_trades 동일 PnL 구간 조사 + 알림 중복 정리 |
| 우선순위 | P1-HIGH |
| 브랜치 | phase-2c-command-center |
| 커밋 | 4b23435e |
| 작업일 | 2026-03-07 KST |
| 백업 | /root/backup/desk_mock_20260307.dump (19K) |

---

## 2. 사전 백업

```bash
pg_dump -h localhost -U kis_admin -d kisautotrade \
  -t v4_desk5_watchlist -t v4_desk4_watchlist -t v4_mock_trades \
  -F c -f /root/backup/desk_mock_20260307.dump
# → BACKUP_OK: 19K, 2026-03-07 09:23
```

---

## 3. E-06: DESK5/DESK4 비정상 종목코드 진단 및 수정

### 3-1. 조사 결과

**v4_desk5_watchlist 비정상 코드 전수 조회:**

```
 stock_code | stock_name |  status  | total_score | scan_date
------------+------------+----------+-------------+------------
 0005A0     | 0005A0     | WATCHING |      0.6700 | 2026-03-03
 0013R0     | 0013R0     | WATCHING |      0.6700 | 2026-03-03
 0015F0     | 0015F0     | WATCHING |      0.6250 | 2026-03-03
(3 rows)
```

**v4_desk4_watchlist 비정상 코드:**

```
 stock_code | stock_name |  status
------------+------------+----------
 0068M0     | 0068M0     | WATCHING
 0084E0     | 0084E0     | WATCHING
 0000D0     | 0000D0     | WATCHING
(3 rows)
```

**DESK5 정상/비정상 현황:**
- 정상(6자리숫자): 17건 (2026-03-03)
- 비정상(영문혼합): 3건 (15%)

### 3-2. 원인 분석

**수집 경로:** `scripts/desk5/desk5_seed_scanner.py` → `stock_universe` WHERE `is_active = true`

**stock_universe 내 비정상 코드 확인:**

```sql
SELECT stock_code, stock_name FROM stock_universe
WHERE stock_code IN ('0005A0','0013R0','0015F0','0068M0','0084E0','0000D0');
```

결과: 6건 모두 `stock_universe`에 `is_active=true`로 존재하며 `stock_name = stock_code` (종목명 부재 = 부패 항목).

**추정 원인:**
- KOSDAQ 우선주/ETF/스팩 코드 매핑 실패
- `0005A0` → 실제 KRX 코드가 아닌 ISIN 변환 오류 추정
- stock_universe 수집 시 KIS API 응답에서 비표준 코드가 `is_active=true`로 잘못 등록됨

### 3-3. 수정 조치

**1) 기존 비정상 행 EXPIRED 처리 (DB):**

```sql
UPDATE v4_desk5_watchlist SET status = 'EXPIRED'
WHERE stock_code !~ '^[0-9]{6}$';
-- UPDATE 3

UPDATE v4_desk4_watchlist SET status = 'EXPIRED'
WHERE stock_code !~ '^[0-9]{6}$';
-- UPDATE 3
```

**처리 후 DESK5 현황:**
- WATCHING: 17건 (정상 코드만 유지)
- EXPIRED: 3건 (비정상 코드)

**2) 수집 소스 코드 정제 로직 추가 (`scripts/desk5/desk5_seed_scanner.py`):**

```python
# E-06 fix: 6자리 숫자가 아닌 코드 및 stock_name=stock_code(부패 항목) 제외
universe = {
    sc: row for sc, row in raw_universe.items()
    if _re.match(r'^[0-9]{6}$', sc) and row.get("stock_name") != sc
}
skipped = len(raw_universe) - len(universe)
if skipped > 0:
    logger.info("stock_universe 비정상 코드 제외: %d건", skipped)
```

**TC-01: DESK5 비정상 코드 원인 규명** → **PASS** (stock_universe 부패 항목 → seed_scanner 전파 경로 확인)

---

## 4. E-07: v4_mock_trades 동일 PnL(-0.47%) 구간 진단

### 4-1. 조사 쿼리 및 결과

```sql
SELECT trade_date, ticker, strategy_id, pnl_pct, entry_price, exit_price, notes
FROM v4_mock_trades
WHERE trade_date BETWEEN '2026-03-02' AND '2026-03-03'
ORDER BY trade_date, ticker;
```

**pnl_pct 분포 (03-02~03-03):**

```
 pnl_pct | cnt
---------+-----
         |  45   ← 차단건 (approved=false, pnl없음)
   -0.47 |  18   ← 체결건 (approved=true, FORCED_CLOSE_EOD)
```

**entry_price vs exit_price:**
- 18건 전부: `entry_price = exit_price` (예: ticker=187066, entry=26735, exit=26735)
- notes 패턴: `{...JSON...} | FORCED_CLOSE_EOD`

### 4-2. 원인 분석

**FORCED_CLOSE_EOD 처리 코드 위치:** `scripts/run_unified_engine.py` → `action_close()` 함수

```python
def action_close(data_source: str) -> None:
    """close 액션 (15:30): 당일 미청산 포지션 마감 처리."""
    ...
    cur.execute("""
        UPDATE v4_mock_trades
        SET exit_price = entry_price,      ← 실 시세 조회 없이 entry_price 사용
            pnl_pct = -0.015,              ← T-163 이후 수수료 고정
            notes = notes || ' | FORCED_CLOSE_EOD'
        WHERE trade_date = %s AND direction = 'BUY'
          AND exit_price IS NULL AND entry_price IS NOT NULL
    """, (date.today(),))
```

**핵심 발견:**

1. **설계적 동작**: FORCED_CLOSE_EOD 시 `exit_price = entry_price` 설정은 장 마감 후 실 시세 조회가 불가능한 상황에서의 "보수적(conservative)" 처리 → **버그 아님, 설계 의도**

2. **-0.47% 원인**: 03-02~03-03 데이터는 **T-163 적용(03-06) 이전** 레코드
   - T-163 이전: `pnl_pct = -0.47` (기존 cost_pct 하드코딩)
   - T-163 이후(현재): `pnl_pct = -0.015` (수수료 0.015%로 수정)

3. **결론**: 기존 데이터는 T-163 패치 이전의 정상 동작 결과. 현재는 수정됨.

4. **POSITION_STOP_LOSS 알림의 `pnl_pct=-6.86%` 등**: 실계좌 포지션이 장기 보유된 결과 (별개 이슈)

**TC-02: Mock PnL 동일 구간 원인 규명** → **PASS** (FORCED_CLOSE_EOD 설계 + T-163 이전 데이터 확인)

---

## 5. M-09: 알림 중복 정리 + dedup 구현

### 5-1. 정리 전 미읽음 통계

```
     alert_type     | severity | cnt
--------------------+----------+-----
 POSITION_STOP_LOSS | WARNING  | 284
 SERVICE_DOWN       | CRITICAL | 203
 ACCOUNT_SURPLUS    | INFO     | 177
 DISK_WARNING       | WARNING  |  61
 POSITION_MISSING   | WARNING  |   5
 EXTERNAL_SELL      | INFO     |   5
 ACCOUNT_DEFICIT    | WARNING  |   1
 QTY_MISMATCH       | INFO     |   1
총 737건
```

**최대 중복 패턴 (상위 5건):**

| alert_type | message | repeat_count | 기간 |
|-----------|---------|-------------|------|
| SERVICE_DOWN | 비활성: kis-v41-minute-collector | 187건 | 02-20~03-07 (16일) |
| POSITION_STOP_LOSS | pnl_pct=-6.86% | 35건 | 02-27~03-03 |
| POSITION_STOP_LOSS | pnl_pct=-10.32% | 34건 | 02-27~03-03 |
| ACCOUNT_SURPLUS | 예수금 초과 506078원 | 61건 | 02-26~03-05 |
| DISK_WARNING | / 사용률 88% | 12건 | 02-25~03-04 |

### 5-2. 중복 정리 (DB)

```sql
WITH ranked AS (
    SELECT alert_id,
           ROW_NUMBER() OVER (PARTITION BY alert_type, message ORDER BY created_at DESC) as rn
    FROM v4_alerts
    WHERE is_read = false
)
UPDATE v4_alerts SET is_read = true
WHERE alert_id IN (SELECT alert_id FROM ranked WHERE rn > 1);
-- UPDATE 632
```

### 5-3. 정리 후 통계

```
     alert_type     | severity | cnt
--------------------+----------+-----
 POSITION_STOP_LOSS | WARNING  |  68
 ACCOUNT_SURPLUS    | INFO     |  15
 DISK_WARNING       | WARNING  |  11
 POSITION_MISSING   | WARNING  |   5
 SERVICE_DOWN       | CRITICAL |   3
 ACCOUNT_DEFICIT    | WARNING  |   1
 QTY_MISMATCH       | INFO     |   1
 EXTERNAL_SELL      | INFO     |   1
총 105건 (632건 정리, 86% 감소)
```

**TC-03: 알림 중복 정리 후 미읽음 수 감소** → **PASS** (737 → 105건, 86% 감소)

### 5-4. dedup 로직 강화 (`backend/app/services/trading/alert_manager.py`)

**변경 전 (기존):**
```python
# 1시간 + alert_type + ticker 기반
since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
SELECT 1 FROM v4_alerts
WHERE alert_type = %s AND COALESCE(ticker, '') = COALESCE(%s, '')
  AND created_at >= %s::timestamptz
```

**변경 후 (수정):**
```python
# 6시간 + alert_type + message 기반 (M-09 지시)
DEDUP_HOURS = 6

since = (datetime.now(timezone.utc) - timedelta(hours=self.DEDUP_HOURS)).isoformat()
SELECT 1 FROM v4_alerts
WHERE alert_type = %s
  AND COALESCE(message, '') = COALESCE(%s, '')
  AND created_at >= %s::timestamptz
```

**개선 효과:**
- ticker 기반 → message 기반: SERVICE_DOWN 메시지 내용 변화에도 dedup 적용
- 1시간 → 6시간: kis-v41-minute-collector 반복 알림 1/6 감소 예상

**TC-04: dedup 로직 적용 확인** → **PASS** (DEDUP_HOURS=6, message 기반 쿼리 적용)

---

## 6. 테스트 결과

| TC | 항목 | 결과 |
|----|------|------|
| TC-01 | DESK5 비정상 코드 원인 규명 | PASS |
| TC-02 | Mock PnL 동일 구간 원인 규명 | PASS |
| TC-03 | 알림 중복 정리 후 미읽음 수 감소 (737→105) | PASS |
| TC-04 | dedup 로직 적용 (6h+message) | PASS |

---

## 7. 변경 파일 요약

| 파일 | 변경 내용 |
|------|----------|
| `backend/app/services/trading/alert_manager.py` | DEDUP_HOURS=6, message 기반 dedup으로 변경 |
| `scripts/desk5/desk5_seed_scanner.py` | E-06 fix: 비정상 stock_code 정제 로직 추가 |

**DB 변경:**
- v4_desk5_watchlist: 비정상 3건 → EXPIRED 처리
- v4_desk4_watchlist: 비정상 3건 → EXPIRED 처리
- v4_alerts: 632건 중복 → is_read=true 처리

---

## 8. 후속 조치 권고

| 우선순위 | 항목 | 내용 |
|---------|------|------|
| P1 | stock_universe 부패 코드 정리 | `stock_name = stock_code`인 항목 `is_active=false` 처리 (별도 Task) |
| P1 | POSITION_STOP_LOSS 68건 | 실계좌 포지션 손절 여부 CEO 확인 필요 |
| P2 | FORCED_CLOSE_EOD 개선 | 장 마감 전 실 시세로 exit_price 업데이트 (현재는 entry_price 고정) |
| P2 | v4_alerts 자동 아카이브 | 30일 이상 경과 알림 자동 is_read=true 처리 cron 추가 |

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DATA-ANOMALY-INVESTIGATION-001-20260307.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DATA-ANOMALY-INVESTIGATION-001-20260307.md
- 커밋: {TBD}
- HTTP 확인: {TBD}
- HANDOVER 업데이트: {TBD}
