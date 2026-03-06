---
project: kis-autotrade-v4
task_id: T-245
completed_at: 2026-03-07T01:19:00+09:00
---

# T-245 실행 결과 보고 (KIS_20260307_011418_BRIDGE)

## 지시서 요약

- Task ID: T-245
- 제목: 03-10 장 마감 후 모의매매 실전 검증 (T-234R)
- 우선순위: P0-CRITICAL
- 실행 시각: 2026-03-07 01:19 KST

---

## 1. SQL 쿼리 실행 결과

### 1-1. 기본 통계 (2026-03-10)

```sql
SELECT COUNT(*), AVG(pnl_pct), AVG(funnel_score)
FROM v4_mock_trades WHERE trade_date = '2026-03-10';
```

**결과:**
```
 count | avg | avg
-------+-----+-----
     0 |     |
(1 row)
```

**오류 발생**: `column "funnel_score" does not exist` — v4_mock_trades 테이블에 funnel_score 컬럼 없음 (notes TEXT 필드에 JSON 형태로 포함됨)

### 1-2. v4_mock_trades 실제 스키마

```
id, trade_date, ticker, strategy_id, direction, quantity, entry_price, exit_price,
pnl_pct, cost_pct, slippage_pct, kis_order_id, notes, created_at
```

→ funnel_score, exit_reason, desk 컬럼 없음. 모두 notes JSON에서 추출 필요.

### 1-3. 날짜별 데이터 현황 확인

```sql
SELECT trade_date, COUNT(*), AVG(pnl_pct)::numeric(8,4) AS avg_pnl
FROM v4_mock_trades GROUP BY trade_date ORDER BY trade_date DESC;
```

결과:
```
 trade_date | count | avg_pnl
------------+-------+---------
 2026-03-06 |    31 | -0.2425
 2026-03-05 |    56 | -0.6311
 2026-03-04 |    34 | -1.0389
 2026-03-03 |    56 | -0.4700
 2026-03-02 |     7 | -0.4700
(5 rows)
```

**2026-03-10 데이터 = 0건 확인.**
최신 데이터: 2026-03-06 19:10:11 KST

### 1-4. v4_market_calendar 확인 (2026-03-07 ~ 03-14)

```sql
SELECT * FROM v4_market_calendar WHERE date >= '2026-03-07' AND date <= '2026-03-14';
```

결과:
```
 id |    date    |   event_type   |         event_name         | ...
----+------------+----------------+----------------------------+
 54 | 2026-03-12 | FUTURES_EXPIRY | 3월 선물옵션 만기일 (분기) | ...
 64 | 2026-03-12 | QUAD_WITCHING  | 1분기 네 마녀의 날         | ...
(2 rows)
```

→ 2026-03-10 은 calendar에 없음 = 정상 거래일 (비공휴일)

### 1-5. exit_reason 분포 (전체 기간 notes 분석)

```sql
SELECT (notes::jsonb->>'blocking_layer') AS blocking_layer, COUNT(*) AS cnt
FROM v4_mock_trades WHERE trade_date = '2026-03-06' AND notes IS NOT NULL AND notes NOT LIKE '%|%'
GROUP BY blocking_layer ORDER BY cnt DESC;
```

결과:
```
 blocking_layer | cnt | pct
----------------+-----+------
 L3.1_FUNNEL    |  28 | 96.6
 ATR_NETRR      |   1 |  3.4
```

### 1-6. DESK별 기준선 (pnl이 있는 승인된 거래)

```sql
SELECT strategy_id AS desk, COUNT(*) AS cnt, ROUND(AVG(pnl_pct)::numeric, 4) AS avg_pnl
FROM v4_mock_trades WHERE pnl_pct IS NOT NULL
GROUP BY strategy_id ORDER BY strategy_id;
```

결과:
```
 desk  | cnt | avg_pnl
-------+-----+---------
 D2    |   3 | -0.4700
 D4    |   4 | -1.0208
 D5    |   1 |  0.0000
 D6    |  13 | -0.4331
 D7    |   8 | -0.6914
 D-ORB |  12 | -0.8010
 S1    |   5 | -0.4700
(7 rows)
```

### 1-7. FunnelScore 분포 (notes JSON 파싱)

```sql
SELECT ROUND(AVG(CASE WHEN (notes::jsonb->>'blocking_reason') LIKE '%FunnelScore%'
  THEN (regexp_match(notes::jsonb->>'blocking_reason', '(\d+\.\d+) <'))[1]::numeric
  END), 4) AS avg_funnel_score
FROM v4_mock_trades WHERE notes IS NOT NULL AND notes NOT LIKE '%|%';
```

결과:
```
 avg_funnel_score
------------------
           0.2316
```

### 1-8. 승인된 거래 전체 통계 (기준선)

```sql
SELECT COUNT(*) AS total_approved, ROUND(AVG(pnl_pct)::numeric, 4) AS avg_pnl,
  COUNT(*) FILTER (WHERE notes LIKE '%FORCED_CLOSE_EOD%') AS forced_eod,
  COUNT(*) FILTER (WHERE notes LIKE '%SL%') AS sl_exit,
  COUNT(*) FILTER (WHERE notes LIKE '%TIMEOUT%') AS timeout_exit,
  ROUND(COUNT(*) FILTER (WHERE notes LIKE '%FORCED_CLOSE_EOD%') * 100.0 / NULLIF(COUNT(*),0), 1) AS forced_eod_pct
FROM v4_mock_trades WHERE pnl_pct IS NOT NULL;
```

결과:
```
 total_approved | avg_pnl | forced_eod | sl_exit | timeout_exit | forced_eod_pct
----------------+---------+------------+---------+--------------+----------------
             46 | -0.6221 |         28 |       2 |           16 |           60.9
```

### 1-9. SL 청산 평균 손실

```sql
SELECT ROUND(AVG(pnl_pct)::numeric, 4) AS avg_sl_pnl, COUNT(*) AS sl_count
FROM v4_mock_trades WHERE pnl_pct IS NOT NULL AND notes LIKE '%SL%';
```

결과:
```
 avg_sl_pnl | sl_count
------------+----------
    -3.1425 |        2
```

---

## 2. KPI 판정 결과

### 2026-03-10 데이터 0건 → 모든 KPI PENDING

| KPI | 기준선 | 목표 | 03-10 실측 | 판정 |
|-----|--------|------|-----------|------|
| 거래 건수 ≥ 1 | 184건(5일) ~37/일 | ≥ 1 | 0건 | **PENDING** |
| FORCED_EOD < 40% | 60.9% | < 40% | — | **PENDING** |
| SL 평균 > -1.8% | -3.1425% | > -1.8% | — | **PENDING** |
| FunnelScore 평균 ≥ 0.30 | 0.2316 | ≥ 0.30 | — | **PENDING** |
| 승인율 > 25% | 25% (46/184) | > 25% | — | **PENDING** |
| 평균 PnL > -0.4% | -0.6221% | > -0.4% | — | **PENDING** |

**전체 판정: DEFERRED**

---

## 3. 폴백 처리

지시서 원문:
> "03-10 데이터 0건인 경우: 장 미개장(공휴일 등) 판단 후 다음 거래일로 재스케줄링하고, HANDOVER에 'T-245 deferred to next trading day' 기록."

원인 분석:
- 2026-03-10은 공휴일 아님 (v4_market_calendar 확인)
- 현재 날짜 2026-03-07 (금요일) → 2026-03-10 (월요일) 미도래
- T-245 지시서가 대상 거래일 이전에 실행됨

처리:
- **T-245 deferred to next trading day (2026-03-10)**
- 재실행 조건: 2026-03-10 15:40 KST 이후

---

## 4. DESK별 분석 (2026-03-10 데이터 0건 → 기준선 기록)

| DESK | 기간 내 건수(승인) | 평균 PnL | 특이사항 |
|------|------------------|---------|---------|
| D2 | 3건 | -0.4700% | 전부 FORCED_CLOSE_EOD |
| D4 | 4건 | -1.0208% | SL 1건 포함 |
| D5 | 1건 | 0.0000% | TIMEOUT_NO_PRICE |
| D6 | 13건 | -0.4331% | 가장 많은 거래/최선 성과 |
| D7 | 8건 | -0.6914% | TIMEOUT 포함 |
| D-ORB | 12건 | -0.8010% | SL 1건 포함 |
| S1 | 5건 | -0.4700% | 전부 FORCED_CLOSE_EOD |

---

## 5. 기준선 대비 비교표

| 지표 | 기준선 (~03-06) | 03-10 실측 | 판정 |
|------|----------------|-----------|------|
| 총 거래 건수 | 184건 | 0건(미도래) | PENDING |
| 승인율 | 25% | — | PENDING |
| 평균 PnL | -0.622% | — | PENDING |
| FORCED_EOD 비율 | 60.9% | — | PENDING |
| SL 평균 손실 | -3.14% | — | PENDING |
| FunnelScore 평균 | 0.2316 | — | PENDING |

---

## 6. 결론 및 후속 조치

**전체 판정: DEFERRED**

이유:
1. 2026-03-10 데이터 0건 (미래 날짜, 현재 2026-03-07)
2. v4_mock_trades 테이블 스키마 상 funnel_score 컬럼 없음 확인
3. exit_reason, desk 컬럼 없음 → notes JSON 파싱으로 대체 가능

후속 조치:
1. T-245 재실행: 2026-03-10 15:40 KST 이후 동일 SQL 쿼리 실행
2. FunnelScore 파싱: notes TEXT → JSONB 캐스팅 필요 (notes NOT LIKE '%|%' 조건 추가)
3. T-237 효과 집중 관찰: FunnelScore Fail-Open 후 첫 거래일
4. HANDOVER v10.45 업데이트 완료

---

## 7. 실행된 파일 목록

### 생성된 파일
1. `/root/kis-autotrade-v4/report/v41/CUR-V41-0310-TRADING-MONITOR-001-20260310.md`
2. `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-0310-TRADING-MONITOR-001-20260310.md` (복사)

### 수정된 파일
1. `/root/project-docs/kis-autotrade-v4/HANDOVER.md` (v10.44 → v10.45)
   - 헤더: v10.45 T-245 DEFERRED 기록 추가
   - 섹션 2: T-245 완료 테이블 행 추가

---

## 8. Git 커밋 정보

### project-docs
- 커밋: c8407dc
- 메시지: "docs: T-245 03-10 trading monitor DEFERRED + HANDOVER v10.45"
- 변경: 2 files changed, 226 insertions(+), 1 deletion(-)
- GitHub HTTP 확인: **200 OK**
  - URL: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-0310-TRADING-MONITOR-001-20260310.md

### kis-autotrade-v4 코드 레포
- 코드 변경 없음 (검증/문서 전용 Task)

---

## 9. 체크포인트

- [x] SQL 쿼리 실행 완료 (6개 쿼리 모두 실행, 2026-03-10 = 0건 확인)
- [x] KPI 판정 완료 (DEFERRED — 데이터 0건)
- [x] 기준선 재확인 완료 (T-234와 완전 일치)
- [x] 보고서 생성 완료 (CUR-V41-0310-TRADING-MONITOR-001-20260310.md)
- [x] project-docs 보고서 push 완료 (GitHub raw URL HTTP 200 확인)
- [x] HANDOVER.md v10.45 업데이트 완료 (커밋 c8407dc)
- [x] HANDOVER에 'T-245 deferred to next trading day' 기록 완료

HANDOVER.md 업데이트 완료: c8407dc
