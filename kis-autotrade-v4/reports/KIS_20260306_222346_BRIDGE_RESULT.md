---
project: KIS AutoTrade V4.1
task_id: T-204
completed_at: 2026-03-06 23:35 KST
---

# KIS_20260306_222346_BRIDGE RESULT — T-204 실행 보고

## 지시서 원문

Task ID: T-204 제목: 03-07 모의매매 실시간 모니터링 + T-187 SL/TP 효과 검증 우선순위: P1-HIGH 예상 소요: 25분 (장 마감 후 16:00~) 선행: T-200, T-201

배경: T-187에서 D-ORB SL 1.8%/TP 1%/TIMEOUT 90min, D4 SL 1.5%, D6 TP 1%/TIMEOUT 90min으로 변경하고, T-189에서 BEAR FunnelScore를 0.28로 완화했다. 03-07이 변경 후 첫 거래일이므로 효과를 실시간 추적해야 한다.

수행 내용: 장 마감(15:30) 후 v4_mock_trades 03-07 데이터 전수 조회 / T-187 변경 전후 비교 분석 / T-189 BEAR threshold 효과 / 종합 판단.

---

## 실행 단계별 결과

### STEP 1. HANDOVER.md / CEO-DIRECTIVES.md 확인

```
cat /root/project-docs/kis-autotrade-v4/HANDOVER.md | head -120
cat /root/project-docs/kis-autotrade-v4/CEO-DIRECTIVES.md | head -60
```

결과: 정상 확인
- 최종 버전: v10.24
- 직전 완료: T-189 BEAR 레짐 FunnelScore 방안C 적용
- strategy_cards: 60건 (관련 없음, 분석 전용)
- open_positions: 0 (장 외)

---

### STEP 2. 현재 날짜 및 DB 상태 확인

```sql
SELECT CURRENT_DATE, CURRENT_TIMESTAMP;
```

```
 current_date |       current_timestamp
--------------+-------------------------------
 2026-03-06   | 2026-03-06 23:13:28.896326+09
(1 row)
```

**핵심 발견**: 현재 날짜는 2026-03-06 (금요일). 03-07은 토요일(비거래일).

---

### STEP 3. v4_mock_trades 날짜별 현황

```sql
SELECT created_at::date as trade_date, COUNT(*) as cnt
FROM v4_mock_trades GROUP BY 1 ORDER BY 1 DESC LIMIT 10;
```

```
 trade_date | cnt
------------+-----
 2026-03-06 |  31
 2026-03-05 |  56
 2026-03-04 |  34
 2026-03-03 |  56
 2026-03-02 |   7
(5 rows)
```

---

### STEP 4. 03-07 전수 조회 (지시서 원문 쿼리)

```sql
SELECT * FROM v4_mock_trades WHERE created_at::date = '2026-03-07' ORDER BY created_at;
```

```
 id | trade_date | ticker | strategy_id | direction | quantity | entry_price | exit_price | pnl_pct | cost_pct | slippage_pct | kis_order_id | notes | created_at
----+------------+--------+-------------+-----------+----------+-------------+------------+---------+----------+--------------+--------------+-------+------------
(0 rows)
```

**결과: 0건** — 03-07 토요일 비거래일. 정상.

---

### STEP 5. T-187 커밋 타임스탬프 확인

```
git log --oneline --format="%H %ai %s" -10
```

```
8674cd71e867a4cfed205bbf7ac2088e481f8d23 2026-03-06 23:08:01 +0900 [V4.1] feat: KIS_MOCK 세션 D6 전용화 (T-196)
bd8d4620fa43faef8d409c9e95abe78b5c9961e0 2026-03-06 22:31:40 +0900 [KIS] feat: T-193 D5 4주 보유기간 테스트 + T-195 14:00 진입차단 게이트
7df7dc8122dac48401d4a99a92402ee61fc839f7 2026-03-06 22:12:11 +0900 [V4.1] feat: L0 BEAR 레짐 FunnelScore 개선 (T-189)
854466b82b773ca92b8f3a6634854dccbdb94663 2026-03-06 20:54:16 +0900 [V4.1] fix: T-187 진단 기반 SL/TP/timeout 조정 적용 (exit_manager.py)
b93b43f5c98dd50808294ac531cde2984a27163c 2026-03-06 20:52:56 +0900 [V4.1] fix: FunnelScore 0.4 하드코딩 잔존 제거 (T-188)
```

→ T-187: 2026-03-06 20:54 (장 마감 후), T-189: 2026-03-06 22:12 (장 마감 후)
→ 03-06 데이터는 T-187/T-189 적용 전 데이터

---

### STEP 6. T-187 변경 내용 확인 (커밋 854466b8)

```
git show 854466b8 -- backend/app/services/unified_engine/core/exit_manager.py
```

```diff
-        "D4":  {"sl_pct": 0.030, ...},  # T-163: SL 2%→3%
+        "D4":  {"sl_pct": 0.015, ...},  # T-187: SL 3%→1.5% (ATR기반)
-        "D6":  {"sl_pct": 0.030, ..., "tp_pct": 0.030, "timeout_min": 60},
+        "D6":  {"sl_pct": 0.030, ..., "tp_pct": 0.010, "timeout_min": 90},  # T-187: TP 3%→1%, TIMEOUT 60→90min
-        "D-ORB": {"sl_pct": 0.040, ..., "tp_pct": 0.030, "timeout_min": 60},  # T-163: SL 2.5%→4.0%
+        "D-ORB": {"sl_pct": 0.018, ..., "tp_pct": 0.010, "timeout_min": 90},  # T-187: SL 4%→1.8%(ATR기반), TP 3%→1%, TIMEOUT 60→90min
```

---

### STEP 7. T-189 변경 내용 확인 (커밋 7df7dc81)

```
git show 7df7dc81
```

핵심 변경:
- config/funnel_score.yaml: bear_min_score_for_entry=0.28
- funnel_score_engine.py: _last_macro_regime 저장, macro_regime 반환값 포함
- cte_pipeline.py: BEAR 레짐 감지 시 min_score_for_entry=0.35→0.28 동적 적용
- 시뮬 통과율: BEAR 구간 50%→75% (+25%p)

---

### STEP 8. 베이스라인 날짜별 통계

```sql
SELECT
  created_at::date as trade_date,
  COUNT(*) as total_records,
  COUNT(CASE WHEN notes::text LIKE '%"approved": true%' THEN 1 END) as approved,
  COUNT(CASE WHEN notes::text LIKE '%"approved": false%' THEN 1 END) as blocked,
  ROUND(100.0*..., 1) as block_rate_pct,
  ...
FROM v4_mock_trades
WHERE created_at::date >= '2026-03-02'
GROUP BY 1 ORDER BY 1;
```

```
 trade_date | total_records | approved | blocked | block_rate_pct | funnel_blocked | atr_blocked | supply_blocked | gate_blocked | priority_blocked
------------+---------------+----------+---------+----------------+----------------+-------------+----------------+--------------+------------------
 2026-03-02 |             7 |        4 |       3 |           42.9 |              0 |           0 |              0 |            1 |                0
 2026-03-03 |            56 |       14 |      42 |           75.0 |              0 |           0 |             39 |            2 |                0
 2026-03-04 |            34 |        8 |      26 |           76.5 |              0 |           0 |             25 |            1 |                0
 2026-03-05 |            56 |       18 |      38 |           67.9 |             12 |           0 |              8 |            5 |                4
 2026-03-06 |            31 |        2 |      29 |           93.5 |             28 |           1 |              0 |            0 |                0
(5 rows)
```

---

### STEP 9. Exit reason 날짜별 분석

```sql
SELECT
  created_at::date as trade_date,
  COUNT(CASE WHEN notes::text LIKE '%"approved": true%' THEN 1 END) as approved_total,
  COUNT(CASE WHEN notes::text LIKE '%FORCED_CLOSE_EOD%' THEN 1 END) as forced_eod,
  COUNT(CASE WHEN notes::text LIKE '%SL(%' THEN 1 END) as sl_hit,
  COUNT(CASE WHEN notes::text LIKE '%TP(%' THEN 1 END) as tp_hit,
  COUNT(CASE WHEN notes::text LIKE '%TIMEOUT(%' THEN 1 END) as timeout_hit,
  COUNT(CASE WHEN notes::text LIKE '%TIMEOUT_NO_PRICE%' THEN 1 END) as timeout_no_price,
  ROUND(AVG(...)::numeric, 4) as avg_pnl,
  ...
FROM v4_mock_trades
WHERE created_at::date >= '2026-03-02'
GROUP BY 1 ORDER BY 1;
```

```
 trade_date | approved_total | forced_eod | sl_hit | tp_hit | timeout_hit | timeout_no_price | avg_pnl | worst_pnl | best_pnl
------------+----------------+------------+--------+--------+-------------+------------------+---------+-----------+----------
 2026-03-02 |              4 |          4 |      0 |      0 |           0 |                0 | -0.4700 |   -0.4700 |  -0.4700
 2026-03-03 |             14 |         14 |      0 |      0 |           0 |                0 | -0.4700 |   -0.4700 |  -0.4700
 2026-03-04 |              8 |          6 |      1 |      0 |           1 |                0 | -1.0389 |   -3.6120 |  -0.4700
 2026-03-05 |             18 |          3 |      1 |      0 |          11 |                3 | -0.6311 |   -2.6730 |   0.4240
 2026-03-06 |              2 |          1 |      0 |      0 |           1 |                0 | -0.2425 |   -0.4700 |  -0.0150
(5 rows)
```

---

### STEP 10. 전체 종합 통계 (T-187 이전 베이스라인)

```sql
SELECT
  COUNT(*) as total_records,
  COUNT(CASE WHEN notes::text LIKE '%"approved": true%' THEN 1 END) as total_approved,
  COUNT(CASE WHEN notes::text LIKE '%"approved": false%' THEN 1 END) as total_blocked,
  ROUND(100.0*... /COUNT(*),1) as block_rate_pct,
  COUNT(CASE WHEN notes::text LIKE '%FORCED_CLOSE_EOD%' THEN 1 END) as total_forced_eod,
  ROUND(100.0*... /NULLIF(... ,0),1) as forced_eod_pct,
  COUNT(CASE WHEN notes::text LIKE '%SL(%' THEN 1 END) as total_sl,
  COUNT(CASE WHEN notes::text LIKE '%TP(%' THEN 1 END) as total_tp,
  COUNT(CASE WHEN notes::text LIKE '%TIMEOUT(%' THEN 1 END) as total_timeout,
  ROUND(AVG(CASE WHEN pnl_pct IS NOT NULL THEN pnl_pct END)::numeric, 4) as overall_avg_pnl,
  COUNT(CASE WHEN pnl_pct > 0 THEN 1 END) as profit_trades,
  COUNT(CASE WHEN pnl_pct < 0 THEN 1 END) as loss_trades,
  ROUND(100.0*COUNT(CASE WHEN pnl_pct > 0 THEN 1 END)/NULLIF(COUNT(CASE WHEN pnl_pct IS NOT NULL THEN 1 END),0),1) as win_rate_pct
FROM v4_mock_trades
WHERE created_at::date BETWEEN '2026-03-02' AND '2026-03-06';
```

```
 total_records | total_approved | total_blocked | block_rate_pct | total_forced_eod | forced_eod_pct | total_sl | total_tp | total_timeout | overall_avg_pnl | profit_trades | loss_trades | win_rate_pct
---------------+----------------+---------------+----------------+------------------+----------------+----------+----------+---------------+-----------------+---------------+-------------+--------------
           184 |             46 |           138 |           75.0 |               28 |           60.9 |        2 |        0 |            13 |         -0.6221 |             3 |          40 |          6.5
(1 row)
```

---

### STEP 11. SL 발동 건 상세

```sql
SELECT trade_date, ticker, strategy_id, pnl_pct,
  regexp_match(notes, 'SL\(([0-9.]+)%\)') as sl_pct_match,
  notes
FROM v4_mock_trades
WHERE notes::text LIKE '%SL(%'
ORDER BY created_at;
```

```
 trade_date | ticker | strategy_id | pnl_pct | sl_pct_match | notes
------------+--------+-------------+---------+--------------+------
 2026-03-04 | 000180 | D-ORB       |  -3.612 | {2.5}        | ... | SL(2.5%) @ 09:17:50
 2026-03-05 | 001275 | D4          |  -2.673 | {2.0}        | ... | SL(2.0%) @ 16:14:01
(2 rows)
```

---

### STEP 12. FunnelScore 분포 (T-189 BEAR threshold 효과 예측)

```sql
SELECT
  (regexp_match(notes, 'FunnelScore 미달: ([0-9.]+)'))[1]::numeric as funnel_score,
  (regexp_match(notes, '< ([0-9.]+) \(min_score'))[1]::numeric as current_threshold,
  CASE
    WHEN ... >= 0.28 THEN 'WOULD_PASS_WITH_BEAR_028'
    ELSE 'STILL_BLOCKED_028'
  END as bear_effect
FROM v4_mock_trades
WHERE notes::text LIKE '%FunnelScore 미달%'
  AND created_at::date >= '2026-03-05'
ORDER BY 1;
```

```
 funnel_score | current_threshold |    bear_effect
--------------+-------------------+-------------------
        0.191 |               0.4 | STILL_BLOCKED_028
        0.191 |               0.4 | STILL_BLOCKED_028
        0.191 |               0.4 | STILL_BLOCKED_028
        0.191 |               0.4 | STILL_BLOCKED_028
        0.191 |               0.4 | STILL_BLOCKED_028
        0.191 |               0.4 | STILL_BLOCKED_028
        0.197 |               0.4 | STILL_BLOCKED_028
        0.197 |               0.4 | STILL_BLOCKED_028
        0.197 |               0.4 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.226 |              0.35 | STILL_BLOCKED_028
        0.241 |               0.4 | STILL_BLOCKED_028
        0.241 |               0.4 | STILL_BLOCKED_028
        0.241 |               0.4 | STILL_BLOCKED_028
        0.241 |               0.4 | STILL_BLOCKED_028
        0.245 |              0.35 | STILL_BLOCKED_028
        0.245 |              0.35 | STILL_BLOCKED_028
        0.245 |              0.35 | STILL_BLOCKED_028
        0.245 |              0.35 | STILL_BLOCKED_028
        0.247 |              0.35 | STILL_BLOCKED_028
        0.247 |              0.35 | STILL_BLOCKED_028
        0.247 |              0.35 | STILL_BLOCKED_028
        0.247 |              0.35 | STILL_BLOCKED_028
        0.250 |               0.4 | STILL_BLOCKED_028
        0.254 |               0.4 | STILL_BLOCKED_028
        0.254 |               0.4 | STILL_BLOCKED_028
        0.254 |               0.4 | STILL_BLOCKED_028
        0.254 |               0.4 | STILL_BLOCKED_028
        0.257 |               0.4 | STILL_BLOCKED_028
        0.257 |               0.4 | STILL_BLOCKED_028
        0.260 |               0.4 | STILL_BLOCKED_028
        0.260 |               0.4 | STILL_BLOCKED_028
        0.261 |              0.35 | STILL_BLOCKED_028
(40 rows)
```

**결론**: 03-05~06 FunnelScore 전체가 0.261 이하 → BEAR threshold 0.28에도 모두 해당 없음.

---

### STEP 13. 보고서 생성

```
파일: /root/kis-autotrade-v4/report/v41/CUR-V41-0307-TRADING-MONITOR-001-20260307.md
생성: 성공 (246줄)
```

---

### STEP 14. project-docs 보고서 push

```bash
cp /root/kis-autotrade-v4/report/v41/CUR-V41-0307-TRADING-MONITOR-001-20260307.md \
   /root/project-docs/kis-autotrade-v4/reports/CUR-V41-0307-TRADING-MONITOR-001-20260307.md

sudo git -C /root/project-docs add kis-autotrade-v4/reports/CUR-V41-0307-TRADING-MONITOR-001-20260307.md
sudo git -C /root/project-docs commit -m "docs: T-204 보고서 push — 03-07 모의매매 모니터링 + T-187/T-189 베이스라인 분석 (20260307)"
sudo git -C /root/project-docs push origin master
```

```
[master cfa16bb] docs: T-204 보고서 push — 03-07 모의매매 모니터링 + T-187/T-189 베이스라인 분석 (20260307)
 1 file changed, 246 insertions(+)
 create mode 100644 kis-autotrade-v4/reports/CUR-V41-0307-TRADING-MONITOR-001-20260307.md
To github.com:moongoby/project-docs.git
   684e02c..cfa16bb  master -> master
```

GitHub HTTP 확인:
```
curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-0307-TRADING-MONITOR-001-20260307.md"
```
→ **200**

---

### STEP 15. HANDOVER.md 업데이트

```
HANDOVER.md v10.24 → v10.25
추가 내용: T-204 완료 — 03-07 토요일(비거래일)/첫검증일=03-09(월)/베이스라인 184건 승인46(25%)차단138(75%)/FORCED_EOD60.9%/SL2건avg-3.14%/TP0건/avg_pnl-0.622%/FunnelScore0.191~0.261구간→T-189 BEAR 0.28도 현재구간이하(0건추가통과)/보고서 push cfa16bb
```

```
sudo git -C /root/project-docs add kis-autotrade-v4/HANDOVER.md
sudo git -C /root/project-docs commit -m "docs: HANDOVER 업데이트 (T-204 완료 — v10.25)"
sudo git -C /root/project-docs push origin master
```

```
[master 36660ef] docs: HANDOVER 업데이트 (T-204 완료 — v10.25)
 1 file changed, 1 insertion(+), 1 deletion(-)
To github.com:moongoby/project-docs.git
   cfa16bb..36660ef  master -> master
```

HANDOVER HTTP 확인: **200**

---

## 최종 결과 요약

### T-204 수행 결론

| 항목 | 결과 |
|------|------|
| 03-07 데이터 | **0건** (토요일 비거래일) |
| 첫 효과 확인일 | **03-09 (월요일)** |
| 베이스라인 총 거래 | 184건 (03-02~03-06) |
| 승인율 | 25.0% (46/184) |
| FORCED_CLOSE_EOD | 60.9% (28/46) |
| SL 발동 avg 손실 | -3.14% (2건: -3.612%, -2.673%) |
| TP 달성 | 0건 |
| 전체 avg PnL | -0.622% |
| 승률 | 6.5% |
| T-189 BEAR 0.28 즉각 효과 | 없음 (현 종목 모두 0.261 이하) |

### T-187 기대 효과 (03-09 검증 필요)

- D-ORB SL 4%→1.8%: 최악 손실 -3.61% → -1.8% 이내 기대
- D4 SL 3%→1.5%: 최악 손실 -2.67% → -1.5% 이내 기대
- D-ORB/D6 TP 3%→1%: TP 달성 0건 → ≥1건 기대
- D-ORB/D6 TIMEOUT 60→90min: FORCED_EOD 60.9% → <40% 기대

### T-189 기대 효과 (조건부)

- BEAR 레짐 감지 시 threshold 0.35→0.28
- 현재 점수 분포(0.191~0.261)에서는 추가 통과 없음
- macro_regime BEAR 판정 시 0.28~0.35 구간 종목이 있어야 효과 발현

---

## 체크포인트

- [x] 코드 레포 커밋 완료: T-187(854466b8), T-189(7df7dc81)
- [x] project-docs 보고서 push 완료
  - 보고서 커밋: cfa16bb
  - GitHub URL HTTP 200: ✅ https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-0307-TRADING-MONITOR-001-20260307.md
  - HANDOVER.md 커밋: 36660ef
  - HANDOVER URL HTTP 200: ✅ https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md

HANDOVER.md 업데이트 완료: 36660ef
