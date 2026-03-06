# CUR-V41-0310-TRADING-MONITOR-001-20260310

> Task ID: T-234R
> 작성일: 2026-03-07 (03-10 장 마감 후 검증 예정 → 현재 사전 검증 보고서)
> 작성자: claudebot (AI 세션)
> 의존성: T-237 FunnelScore 재교정 (pass율 88%, avg 0.44) 첫 실전 효과 검증

---

## [인계 확인]
직전 완료: T-239 (DESK4 v4_node_realtime cron 생성)
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002, D-003, D-008-KR, D-010, D-011
strategy_cards: 조회 불필요 (금지 항목)
open_positions: 모의매매 실시간 (03-10 장 미개장 상태)

---

## 1. 작업 개요

T-234R는 **T-237 FunnelScore Fail-Open + 재가중 첫 실전 효과 검증**을 목적으로 한다.
본 보고서는 **2026-03-07(토요일) 사전 실행** 시점으로, 03-10 데이터는 없으나:

1. 현재 DB (184건, 2026-03-02~03-06) 기반 사전 베이스라인 확인
2. T-237 적용 상태 검증 (funnel_score.yaml 신규 가중치 확인)
3. 03-10 실행 후 재확인 체크리스트 수립
4. T-237 이전(T-234 기준선) vs 이후 기대 효과 비교표 작성

---

## 2. 실행 환경 확인

```sql
-- 2026-03-10 데이터 조회 결과
SELECT count(*) FROM v4_mock_trades WHERE trade_date='2026-03-10';
-- → 0 rows (03-07 현재 데이터 없음, 03-10 장 미개장)

-- 현재 데이터 범위
SELECT trade_date, COUNT(*) FROM v4_mock_trades GROUP BY trade_date ORDER BY trade_date DESC;
```

| trade_date | 건수 |
|------------|------|
| 2026-03-06 |   31 |
| 2026-03-05 |   56 |
| 2026-03-04 |   34 |
| 2026-03-03 |   56 |
| 2026-03-02 |    7 |
| **합계**   | **184** |

**판정**: 03-10 데이터 부재 → 사전 베이스라인 기반 예비 검증 수행 (PENDING)

---

## 3. T-237 적용 상태 확인

### 3.1 funnel_score.yaml 신규 가중치 확인

```yaml
# /root/kis-autotrade-v4/config/funnel_score.yaml (T-237 적용 완료)
funnel_score:
  null_fallback_score: 0.5    # 신규: 레이어 NULL 시 Fail-Open (구: 차단)
  weights:
    l0_macro: 0.40            # 변경: 0.15→0.40 (매크로 비중 강화)
    l1_sector: 0.10           # 변경: 0.25→0.10 (섹터 데이터 불완전 반영)
    l2_supply: 0.20           # 변경: 0.30→0.20 (수급 데이터 불완전 반영)
    l3_fundamental: 0.30      # 유지
  thresholds:
    min_score_for_entry: 0.35 # T-163 적용값 유지
```

**T-237 커밋**: `91051978` — phase-2c-command-center
**설정 파일**: `/root/kis-autotrade-v4/config/funnel_score.yaml` 갱신 확인 ✅
**단위 테스트**: 8T ALL PASS (test_funnel_score_t237.py) ✅

### 3.2 T-237 예상 효과 vs 구 시스템 비교

| 항목 | T-234 기준선 (구 시스템) | T-237 이후 예상 | 비고 |
|------|------------------------|----------------|------|
| Null 레이어 처리 | Fail-Close (0 반환) | Fail-Open (0.5 반환) | 핵심 변경 |
| L0 가중치 | 0.15 | 0.40 | +0.25 (매크로 신뢰도 높음) |
| L1 가중치 | 0.25 | 0.10 | -0.15 (섹터 데이터 불완전) |
| L2 가중치 | 0.30 | 0.20 | -0.10 (수급 데이터 불완전) |
| L3 가중치 | 0.30 | 0.30 | 유지 |
| 전레이어 Null 시 score | 0.00 | 0.50 | ≥ 0.35 → 통과 |
| 시뮬 pass율 (184건) | 0% (0/184) | 88% (161/184) | +88%p |
| 시뮬 avg score | 0.191~0.261 | 0.44 | +0.18↑ |

---

## 4. T-234 기준선 KPI (03-02~03-06, 184건)

### 4.1 전체 KPI 요약

| 항목 | T-234 기준선 값 | T-237 이후 목표 |
|------|----------------|----------------|
| 총 거래 건수 | **184건** | 재측정 필요 |
| 승인 건수 | **46건** | 기대: ~161건 (+250%) |
| 승인율 | **25.0%** | 기대: ~88% |
| avg PnL (승인건) | **-0.622%** | 개선 기대 |
| FunnelScore 범위 | **0.191~0.261** | 기대: 0.35~0.70 |
| FunnelScore 통과 | **0건** | 기대: 161건 |
| 승리 건수 (pnl>0) | **3건 (1.6%)** | 기대: 개선 |

### 4.2 날짜별 KPI 추이

| trade_date | 총건수 | 승인 | 승인율 | avg PnL(승인) | 승리 |
|------------|--------|------|--------|--------------|------|
| 2026-03-02 |      7 |    4 | 57.1%  | -0.4700%     |    0 |
| 2026-03-03 |     56 |   14 | 25.0%  | -0.4700%     |    0 |
| 2026-03-04 |     34 |    8 | 23.5%  | -1.0389%     |    0 |
| 2026-03-05 |     56 |   18 | 32.1%  | -0.6311%     |    3 |
| 2026-03-06 |     31 |    2 |  6.5%  | -0.2425%     |    0 |
| **합계**   |**184** | **46** | **25.0%** | **-0.622%** | **3** |

> 주: 03-06 승인율 6.5%로 최저 — T-237 미적용 상태(구 가중치)로 인해 FunnelScore 전원 미달

---

## 5. DESK별 분석 (03-02~03-06 전체, 기준선)

### 5.1 전략별 건수 + PnL

```sql
SELECT strategy_id, count(*), avg(pnl_pct), count(CASE WHEN pnl_pct > 0 THEN 1 END) as wins
FROM v4_mock_trades
WHERE trade_date BETWEEN '2026-03-02' AND '2026-03-06'
GROUP BY 1 ORDER BY 1;
-- 결과: D2=16건/-0.470%/0승, D4=16건/-1.021%/0승, D5=34건/0.000%/0승,
--       D6=34건/-0.433%/2승, D7=34건/-0.913%/0승, D-ORB=34건/-0.801%/1승, S1=16건/-0.470%/0승
```

| strategy_id | 건수 | avg PnL | 승리 | 분석 |
|-------------|------|---------|------|------|
| D2          |   16 | -0.470% |    0 | FORCED_EOD 100% |
| D4          |   16 | -1.021% |    0 | SL HIT 포함 (-2.673%) |
| D5          |   34 |  0.000% |    0 | 청산 미발동 (T-229 완료) |
| D6          |   34 | -0.433% |    2 | 최우수 전략 |
| D7          |   34 | -0.913% |    0 | FORCED_EOD 75% |
| D-ORB       |   34 | -0.801% |    1 | SL HIT (-3.612% 갭슬리피지) |
| S1          |   16 | -0.470% |    0 | FORCED_EOD 100% |

### 5.2 최근 03-05~06 구간 (T-237 직전)

| strategy_id | 건수 | avg PnL | 승리 |
|-------------|------|---------|------|
| D2          |    5 |  NULL   |    0 |
| D4          |    5 | -2.673% |    0 |
| D5          |   18 |  0.000% |    0 |
| D6          |   18 | -0.234% |    2 |
| D7          |   18 | -0.913% |    0 |
| D-ORB       |   18 | -0.608% |    1 |
| S1          |    5 |  NULL   |    0 |

---

## 6. FunnelScore 분포 분석 (T-237 이전)

### 6.1 03-06 FunnelScore 실측 (notes 컬럼 기준)

| FunnelScore | 소스 | 판정 | 건수 |
|-------------|------|------|------|
| 0.191 | VIRTUAL_KIS_MOCK | L3.1_FUNNEL BLOCK (< 0.40) | 1 |
| 0.226 | VIRTUAL_NXT_NIGHT/PM | L3.1_FUNNEL BLOCK (< 0.35) | 9 |
| 0.241 | VIRTUAL_NXT_AM | L3.1_FUNNEL BLOCK (< 0.40) | 4 |
| 0.245 | VIRTUAL_NXT_NIGHT/PM | L3.1_FUNNEL BLOCK (< 0.35) | 4 |
| 0.247 | VIRTUAL_NXT_PM | L3.1_FUNNEL BLOCK (< 0.35) | 4 |
| 0.257 | VIRTUAL_KIS_MOCK | L3.1_FUNNEL BLOCK (< 0.40) | 2 |
| **최대** | - | - | **0.261** |

**결론**: 구 가중치 기준 최대 0.261 → 임계값 0.35 미달로 전원 차단

### 6.2 T-237 신규 가중치 기대값

모든 레이어 NULL → Fail-Open(0.5) 시:
```
score = 0.40×0.5 + 0.10×0.5 + 0.20×0.5 + 0.30×0.5 = 0.50 ≥ 0.35 → 통과
```

| 시나리오 | 구 점수 | T-237 신규 점수 | 통과 여부 |
|----------|---------|----------------|----------|
| 전레이어 NULL | 0.00 | 0.50 | ✅ 통과 |
| L0=0.5 + 나머지 NULL | ~0.08 | 0.50 | ✅ 통과 |
| L0=0.36 (실측 KOSPI) | 0.261 | 0.47 | ✅ 통과 |
| 전레이어 실측 평균 | 0.226 | 0.44 | ✅ 통과 |

---

## 7. T-237 효과 판정 (03-07 현재 사전 평가)

### 7.1 KPI 비교표 (기준선 vs 기대치)

| KPI | T-234 기준선 | T-237 목표 | 03-07 현재 | 판정 |
|-----|-------------|-----------|-----------|------|
| 거래 승인율 | 25.0% | ≥ 88% | N/A (03-10 데이터 없음) | ⏳ PENDING |
| avg FunnelScore | 0.191~0.261 | 0.44 | N/A | ⏳ PENDING |
| avg PnL | -0.622% | 개선 | N/A | ⏳ PENDING |
| FunnelScore 통과 건수 | 0건 | 161건 | N/A | ⏳ PENDING |
| T-237 config 적용 | ❌ 미적용 | ✅ 적용 완료 | ✅ 확인 | ✅ CONFIRMED |
| T-237 단위 테스트 | N/A | 8T ALL PASS | 8/8 PASS | ✅ CONFIRMED |

### 7.2 판정

> **PENDING** — 03-10 장 마감 후 실제 데이터 수집 후 재평가 필요
> T-237 설정 적용은 확인되었으나 실전 효과 검증은 03-10 데이터 필수

---

## 8. 03-10 장 마감 후 재확인 체크리스트

```sql
-- 8.1 거래 건수 확인
SELECT count(*) FROM v4_mock_trades WHERE trade_date='2026-03-10';

-- 8.2 전략별 KPI
SELECT strategy_id, count(*), avg(pnl_pct),
  count(CASE WHEN pnl_pct > 0 THEN 1 END) as wins
FROM v4_mock_trades WHERE trade_date='2026-03-10' GROUP BY 1 ORDER BY 1;

-- 8.3 FunnelScore 분포
SELECT strategy_id, count(*), avg(pnl_pct) FROM v4_mock_trades
WHERE trade_date='2026-03-10' GROUP BY 1;

-- 8.4 승인율
SELECT
  count(*) as total,
  sum(CASE WHEN notes LIKE '%"approved": true%' THEN 1 ELSE 0 END) as approved,
  round(100.0 * sum(CASE WHEN notes LIKE '%"approved": true%' THEN 1 ELSE 0 END) / count(*), 1) as approval_rate
FROM v4_mock_trades WHERE trade_date='2026-03-10';

-- 8.5 avg PnL 승인건
SELECT round(avg(pnl_pct)::numeric, 4) as avg_pnl
FROM v4_mock_trades WHERE trade_date='2026-03-10' AND notes LIKE '%"approved": true%';
```

### 재확인 판정 기준

| 항목 | PASS 기준 | PARTIAL 기준 | FAIL 기준 |
|------|-----------|-------------|---------|
| 승인율 | ≥ 70% | 30~70% | < 30% |
| avg FunnelScore | ≥ 0.40 | 0.35~0.40 | < 0.35 |
| avg PnL | > -0.4% | -0.4%~-0.7% | < -0.7% |
| FunnelScore 통과 건수 | 구 대비 개선 | 소폭 개선 | 미개선 |

**3개 이상 PASS → PASS / 1~2개 → PARTIAL / 0개 → FAIL**

---

## 9. 후속 조치 목록

| # | 항목 | 원인 | 후속 태스크 | 상태 |
|---|------|------|------------|------|
| 1 | FORCED_EOD 60.9% | Mock 시뮬레이터 PRE_TIME_GATE 우회 | T-240 후보 | PENDING |
| 2 | D-ORB SL -3.612% | 갭하락 슬리피지 | T-232 ATR SL Cap | 완료 |
| 3 | D4 SL -2.673% | 장 마감 직전 급락 | T-232 ATR SL Cap | 완료 |
| 4 | avg PnL -0.622% | FunnelScore 구조 + FORCED_EOD | T-237 재교정 | 완료 |
| 5 | D5 청산 미발동 | exit_manager D5 청산 로직 미작동 | T-229 Exit Manager D5 | 완료 |

---

## 10. 성공 기준 달성 현황

| 검증 항목 | 기준 | 현재 상태 | 판정 |
|-----------|------|----------|------|
| T-237 설정 적용 | config 갱신 | funnel_score.yaml T-237 가중치 확인 | ✅ CONFIRMED |
| T-237 단위 테스트 | 8T ALL PASS | 8/8 PASS | ✅ CONFIRMED |
| 03-10 데이터 기반 KPI | 03-10 장 마감 후 | 03-10 데이터 미생성 | ⏳ PENDING |
| 기준선 비교 | T-234 baseline 대비 | 기준선 확인 완료, 실전 비교 대기 | ⏳ PENDING |
| T-237 pass율 변화 | 0% → ≥88% | 03-10 실전 데이터 필요 | ⏳ PENDING |
| avg PnL 개선 | -0.622% → 개선 | 03-10 실전 데이터 필요 | ⏳ PENDING |
| HANDOVER 갱신 | v10.45 | 진행 중 | 🔄 |

**종합 판정: PENDING — 03-10 장 마감 후 재실행 시 PASS/PARTIAL/FAIL 확정 가능**

---

## 11. 저장 정보
- 서버 경로: /root/kis-autotrade-v4/report/v41/CUR-V41-0310-TRADING-MONITOR-001-20260310.md
- project-docs 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-0310-TRADING-MONITOR-001-20260310.md
- HANDOVER 업데이트: v10.45

---

**체크포인트**
- [ ] 코드 레포 커밋 완료 (코드 변경 없음, 보고서만)
- [ ] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)

---

## [T-245R 재실행 기록] 2026-03-07 01:24 KST

**Task ID**: T-245R
**재실행 시각**: 2026-03-07 01:24 KST
**재실행 사유**: T-245가 03-07 새벽 조기 실행으로 DEFERRED, 03-10 장 마감 후 재실행 지시

### 실행 결과

```sql
SELECT COUNT(*) FROM v4_mock_trades WHERE trade_date = '2026-03-10';
-- 결과: 0건
```

| 항목 | 결과 |
|------|------|
| 조회 일자 | 2026-03-10 |
| 데이터 건수 | **0건** |
| 현재 서버 시각 | 2026-03-07 01:24 KST |
| 판정 | **DEFERRED — 03-10 미도래 날짜 (현재 03-07)** |

### 판정 근거

현재 서버 시각이 **2026-03-07 01:24 KST**로 2026-03-10 장 마감(15:40 KST) 이전. 03-10 데이터 미수집은 미개장 또는 날짜 미도래로 인한 정상 상태.

### 최신 데이터 현황

```
trade_date | count
-----------+-------
2026-03-06 |    31
2026-03-05 |    56
2026-03-04 |    34
2026-03-03 |    56
2026-03-02 |     7
합계       |   184건
```

### T-245R 후속 조치

- **재스케줄**: 2026-03-11(화) 장 마감 후 재실행
- **HANDOVER**: "T-245R deferred → 2026-03-11 재실행" 기록
- **다음 거래일**: 2026-03-11 (월요일이 공휴일인 경우 확인 필요)

### T-245R 종합 판정

> **DEFERRED** — 2026-03-10 데이터 미수집 (현재 2026-03-07). 다음 거래일(2026-03-11) 재실행 예정.
