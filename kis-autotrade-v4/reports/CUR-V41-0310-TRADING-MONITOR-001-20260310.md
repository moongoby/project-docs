# T-245: 03-10 장 마감 후 모의매매 실전 검증 (T-234R)

[인계 확인]
직전 완료: T-239
현재 단계: Phase 2c
CEO 지시 적용: D-001, D-002, D-008, D-009
strategy_cards: 60
open_positions: 0

---

## 메타 정보

| 항목 | 내용 |
|------|------|
| Task ID | T-245 |
| 보고서 ID | CUR-V41-0310-TRADING-MONITOR-001-20260310 |
| 작성일 | 2026-03-07 (KST) |
| 검증 대상 | 2026-03-10 장 마감 후 모의매매 데이터 |
| 의존성 | T-237 (FunnelScore Fail-Open v10.40 적용) |

---

## 1. 실행 결과 요약

### 1-1. 2026-03-10 데이터 조회 결과

```sql
SELECT COUNT(*), AVG(pnl_pct), AVG(funnel_score)
FROM v4_mock_trades WHERE trade_date = '2026-03-10';
```

**결과: 0건 (데이터 없음)**

### 1-2. 원인 분석

| 원인 | 판정 |
|------|------|
| 공휴일 여부 | v4_market_calendar 확인 → 2026-03-10 해당 없음 (정상 거래일) |
| **미래 날짜** | **현재 날짜: 2026-03-07 (금요일)** → 2026-03-10 (월요일)은 아직 미도래 |
| 데이터베이스 최신 | v4_mock_trades MAX(created_at) = 2026-03-06 19:10 KST |

**결론: T-245는 2026-03-07에 조기 실행됨. 대상 날짜(2026-03-10)가 아직 미도래.**

---

## 2. 지시서 폴백 처리

> 지시서 원문: "03-10 데이터 0건인 경우: 장 미개장(공휴일 등) 판단 후 다음 거래일로 재스케줄링하고, HANDOVER에 'T-245 deferred to next trading day' 기록."

### 판정: **T-245 DEFERRED → 2026-03-10 장 마감(15:40 KST) 이후 재실행**

---

## 3. 기준선 데이터 확인 (T-234 인수인계 검증)

### 3-1. 전체 기간 집계 (2026-03-02 ~ 2026-03-06)

```sql
SELECT COUNT(*), COUNT(*) FILTER (WHERE pnl_pct IS NOT NULL) AS approved,
       AVG(pnl_pct), ... FROM v4_mock_trades;
```

| 지표 | 실측값 | T-234 기준선 | 일치 여부 |
|------|--------|------------|----------|
| 총 거래 건수 | 184건 | 184건 | ✅ MATCH |
| 승인(실행)된 거래 | 46건 (25%) | 46건 (25%) | ✅ MATCH |
| 평균 PnL (승인 거래) | -0.6221% | -0.622% | ✅ MATCH |
| FORCED_EOD 비율 | 60.9% (28/46) | 60.9% | ✅ MATCH |
| SL 청산 평균 손실 | -3.1425% | -3.14% | ✅ MATCH |
| SL 건수 | 2건 | 2건 | ✅ MATCH |
| TIMEOUT 청산 | 16건 | 16건 | ✅ MATCH |

### 3-2. FunnelScore 기준선 확인

```
v4_mock_trades.notes (JSON) blocking_reason에서 추출:
```

| 날짜 | 평균 FunnelScore (차단된 건) |
|------|--------------------------|
| 2026-03-05 | 0.2140 |
| 2026-03-06 | 0.2391 |
| 전체 평균 | 0.2316 |

→ T-237 적용 전 기준선: FunnelScore 0.191 ~ 0.261 범위 **확인됨**

### 3-3. Blocking Layer 분포 (2026-03-06 기준)

| Layer | 건수 | 비율 |
|-------|------|------|
| L3.1_FUNNEL | 28 | 96.6% |
| ATR_NETRR | 1 | 3.4% |

### 3-4. DESK별 기준선

| DESK | 건수(승인) | 평균 PnL |
|------|-----------|---------|
| D2 | 3건 | -0.4700% |
| D4 | 4건 | -1.0208% |
| D5 | 1건 | 0.0000% |
| D6 | 13건 | -0.4331% |
| D7 | 8건 | -0.6914% |
| D-ORB | 12건 | -0.8010% |
| S1 | 5건 | -0.4700% |

---

## 4. T-237 FunnelScore Fail-Open 효과 예측

T-237 적용 (v10.40, 커밋 91051978):
- null_fallback_score = 0.5
- 가중치 재조정 (l0: 0.40 / l1: 0.10 / l2: 0.20 / l3: 0.30)
- Mock Replay 결과: pass율 88% / avg_score 0.44

**예상 변화 (2026-03-10 검증 포인트):**

| KPI | 기준선 | 목표 | 검증 방법 |
|-----|--------|------|---------|
| 거래 건수 (총) | 184 (5일) / ~37/일 | ≥ 1건 | v4_mock_trades COUNT |
| FORCED_EOD 비율 | 60.9% | < 40% | notes LIKE '%FORCED_CLOSE_EOD%' |
| SL 평균 손실 | -3.14% | > -1.8% | T-207 ATR SL Cap 적용 효과 |
| FunnelScore 평균 | 0.191~0.261 | ≥ 0.30 | notes JSON blocking_reason 파싱 |
| 승인율 | 25% (46/184) | > 25% | approved / total |
| 평균 PnL | -0.622% | > -0.4% | AVG(pnl_pct) |

---

## 5. 2026-03-10 실행 SQL (재실행 시 사용)

```sql
-- 1. 기본 통계
SELECT COUNT(*) AS total,
       COUNT(*) FILTER (WHERE pnl_pct IS NOT NULL) AS approved,
       ROUND(AVG(pnl_pct)::numeric, 4) AS avg_pnl,
       ROUND(AVG(CASE WHEN notes LIKE '%FunnelScore%'
         THEN (regexp_match(notes, '(\d+\.\d+) <'))[1]::numeric
         END), 4) AS avg_funnel_score
FROM v4_mock_trades
WHERE trade_date = '2026-03-10';

-- 2. exit_reason 분포 (notes 필드에서)
SELECT
  CASE
    WHEN notes LIKE '%FORCED_CLOSE_EOD%' THEN 'FORCED_EOD'
    WHEN notes LIKE '%SL(%' THEN 'SL_HIT'
    WHEN notes LIKE '%TIMEOUT%' THEN 'TIMEOUT'
    ELSE 'OTHER'
  END AS exit_reason,
  COUNT(*) AS cnt
FROM v4_mock_trades
WHERE trade_date = '2026-03-10' AND pnl_pct IS NOT NULL
GROUP BY 1 ORDER BY 2 DESC;

-- 3. DESK별 분석
SELECT
  strategy_id AS desk,
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE (notes::jsonb->>'approved') = 'true') AS approved,
  ROUND(AVG(pnl_pct)::numeric, 4) AS avg_pnl
FROM v4_mock_trades
WHERE trade_date = '2026-03-10'
GROUP BY strategy_id
ORDER BY strategy_id;

-- 4. FunnelScore 분포 (차단된 거래에서)
SELECT
  ROUND((regexp_match(notes::jsonb->>'blocking_reason', '(\d+\.\d+) <'))[1]::numeric, 1) AS bucket,
  COUNT(*) AS cnt
FROM v4_mock_trades
WHERE trade_date = '2026-03-10' AND notes LIKE '%FunnelScore%'
GROUP BY bucket ORDER BY bucket;
```

---

## 6. KPI 판정

**2026-03-10 데이터 부재로 KPI 판정 불가 → DEFERRED**

| KPI | 기준선 | 목표 | 03-10 실측 | 판정 |
|-----|--------|------|-----------|------|
| 거래 건수 ≥ 1 | 184건(5일) | ≥ 1 | — | PENDING |
| FORCED_EOD < 40% | 60.9% | < 40% | — | PENDING |
| SL 평균 > -1.8% | -3.14% | > -1.8% | — | PENDING |
| FunnelScore ≥ 0.30 | 0.191~0.261 | ≥ 0.30 | — | PENDING |
| 승인율 > 25% | 25% | > 25% | — | PENDING |
| 평균 PnL > -0.4% | -0.622% | > -0.4% | — | PENDING |

**전체 판정: DEFERRED**
**이유: 대상 거래일(2026-03-10) 미도래 (보고서 작성 시점 2026-03-07)**

---

## 7. 후속 조치

1. **T-245 재실행**: 2026-03-10 15:40 KST 이후 동일 SQL 쿼리로 재실행
2. **v4_mock_trades 컬럼 주의**: `funnel_score` 컬럼 없음 → `notes` JSON 파싱 필요
3. **T-237 효과 모니터링**: FunnelScore Fail-Open 후 첫 거래일이므로 승인율 변화 집중 관찰
4. **HANDOVER**: T-245 deferred to 2026-03-10 기록

---

## 8. 시스템 상태 (2026-03-07 기준)

| 항목 | 상태 |
|------|------|
| v4_mock_trades 최신 | 2026-03-06 19:10 KST |
| T-237 커밋 | 91051978 (적용됨) |
| FunnelScore null_fallback | 0.5 (Fail-Open) |
| ATR SL Cap | D-ORB 2.0% / D4 1.8% / D6 2.0% (T-232) |
| v4_market_calendar | 2026-03-10 특이일정 없음 |

---

## 체크포인트

- [x] 코드 레포 확인 완료 (kis-autotrade-v4)
- [x] 2026-03-10 데이터 0건 확인 및 원인 분석 (미래 날짜)
- [x] 기준선 데이터 재확인 (T-234와 완전 일치)
- [ ] project-docs 보고서 push (DEFERRED 보고서)
- [ ] HANDOVER.md v10.45 업데이트

HANDOVER.md 업데이트 완료: (커밋 예정)
