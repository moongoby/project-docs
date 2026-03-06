# CUR-V41-0309-TRADING-MONITOR-001-20260309

> Task ID: T-234
> 작성일: 2026-03-07 (03-09 장 마감 후 검증 예정 → 현재 사전 검증 보고서)
> 작성자: claudebot (AI 세션)
> 의존성: T-226, T-187, T-189, T-195, T-196, T-207, T-227

---

## [인계 확인]
직전 완료: T-235 (SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2)
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002, D-003, D-008-KR, D-010, D-011
strategy_cards: 조회 불필요 (금지 항목)
open_positions: 모의매매 실시간 (03-09 장 미개장 상태)

---

## 1. 작업 개요

T-234는 **2026-03-09(월요일) 장 마감 후** 전체 효과 검증을 목적으로 한다.
본 보고서는 **2026-03-07(토요일) 사전 실행** 시점으로, 03-09 데이터는 없으나:

1. 현재 DB (184건, 2026-03-02~03-06) 기반 사전 검증 완료
2. 각 태스크 구현 상태 확인 (T-187/T-189/T-195/T-196/T-207/T-227)
3. 03-09 실행 후 재확인 체크리스트 수립

---

## 2. 실행 환경 확인

```sql
-- 2026-03-09 데이터 조회 결과
SELECT * FROM v4_mock_trades WHERE trade_date='2026-03-09';
-- → 0 rows (03-07 현재 데이터 없음, 03-09 장 미개장)

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

**판정**: 03-09 데이터 부재 → 현재 184건(기준선) 기반 사전 검증 수행

---

## 3. T-187 효과 검증 — FORCED_EOD / SL / TP / avg PnL

### 검증 기준
| 항목 | 기준 | 현재 값 | 판정 |
|------|------|---------|------|
| FORCED_EOD 비율 | < 40% | **60.9%** (28/46건) | ❌ FAIL |
| SL 손실 D-ORB | < 1.8% | **-3.612%** (SL(2.5%) 트리거 + 갭슬리피지) | ❌ FAIL |
| SL 손실 D4 | < 1.5% | **-2.673%** (SL(2.0%) 트리거 + 슬리피지) | ❌ FAIL |
| TP ≥ 1건 | ≥ 1 | **3건** (+0.424%, +0.372%, +0.199%) | ✅ PASS |
| avg PnL (approved exits) | > -0.4% | **-0.622%** | ❌ FAIL |

### 전략별 상세

```sql
-- 전략별 FORCED_EOD/SL/TP 분포 (approved, exit_price IS NOT NULL)
```

| strategy_id | total | SL | FORCED_EOD | FORCED_EOD_% | TP | avg_pnl |
|-------------|-------|----|------------|--------------|----|---------|
| D2          |     3 |  0 |          3 | 100.0%       |  0 | -0.4700 |
| D4          |     4 |  1 |          3 |  75.0%       |  0 | -1.0208 |
| D5          |     1 |  0 |          0 |   0.0%       |  0 |  0.0000 |
| D6          |    13 |  0 |          5 |  38.5%       |  2 | -0.4331 |
| D7          |     8 |  0 |          6 |  75.0%       |  0 | -0.6914 |
| D-ORB       |    12 |  1 |          6 |  50.0%       |  1 | -0.8010 |
| S1          |     5 |  0 |          5 | 100.0%       |  0 | -0.4700 |

### 분석
- **D6만이** FORCED_EOD 38.5%로 유일하게 40% 기준 충족
- D2, S1은 100% FORCED_EOD → T-195 PRE_TIME_GATE가 실시간 매매에서 이를 차단해야 함
- SL 트리거 D-ORB: `SL(2.5%) @ 09:17:50` 기록되나 실제 손실 -3.612% → 갭하락 슬리피지로 추정
- SL 트리거 D4: `SL(2.0%) @ 16:14:01` 기록되나 실제 손실 -2.673% → 장 마감 직전 급락 추정
- T-207 ATR SL Cap이 SL 트리거를 정상 기록하나, 갭/슬리피지 손실은 별도 관리 필요

---

## 4. T-189 효과 검증 — FunnelScore 0.28~0.35 구간 통과 건수

### 검증 기준
| 항목 | 현재 값 | 판정 |
|------|---------|------|
| 0.28~0.35 구간 통과 건수 | **0건** | 📊 데이터 없음 |

### FunnelScore 실측 분포 (L3.1_FUNNEL 차단 40건)

| FunnelScore | 차단 건수 |
|-------------|---------|
| 0.191       |       6 |
| 0.197       |       3 |
| 0.226       |       9 |
| 0.241       |       4 |
| 0.245       |       4 |
| 0.247       |       4 |
| 0.250       |       1 |
| 0.254       |       4 |
| 0.257       |       2 |
| 0.260       |       2 |
| 0.261       |       1 |
| **최대**    | **0.261** |

### 분석
- **최대 FunnelScore = 0.261**: 임계값 0.35 미달로 전원 차단
- 0.28~0.35 구간 통과 건수 = **0건** (해당 점수 구간 자체에 도달하지 못함)
- T-227 FunnelScore 재교정안 (A: Fail-Open / B: 재가중 / C: 임계값 0.20) 미적용 상태
- **구조적 결론**: L0(KOSPI오염+VIX NULL), L1(섹터미등록), L2(수급데이터없음)로 인해 FunnelScore 최대 0.2415 → CEO 승인 후 T-227 재교정 적용 필요

---

## 5. T-195 효과 검증 — PRE_TIME_GATE 차단 건수 (14:00 이후)

### 구현 상태
- **코드**: `/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py` line 395
- **로직**: `_current_hour >= 14` → `blocking_layer = "PRE_TIME_GATE"` → BLOCK

### DB 기록 현황
| 항목 | 값 |
|------|-----|
| PRE_TIME_GATE 차단 기록 | **0건** |
| 이유 | Mock trade 시뮬레이터가 CTE pipeline을 직접 통과하지 않음 |

### Mock trade blocking_layer 분포 (blocked 138건)
| blocking_layer | 건수 |
|----------------|------|
| L3.3_SUPPLY    |   72 |
| L3.1_FUNNEL    |   40 |
| SIGNAL_COMBO   |   12 |
| GATE           |    9 |
| PRE_PRIORITY   |    4 |
| ATR_NETRR      |    1 |
| PRE_TIME_GATE  |    0 |
| PRE_SOURCE_FILTER | 0 |

### 분석
- PRE_TIME_GATE 코드 구현 완료, 하지만 **Mock 시뮬레이터는 CTE pipeline 사전 필터를 우회**
- 실시간 KIS API 매매 시에는 정상 작동 예상
- 03-09 실시간 매매 로그에서 PRE_TIME_GATE 기록 확인 필요
- FORCED_EOD 60.9% (28건) 중 14:00 이후 진입 건수가 얼마인지 별도 추적 필요

---

## 6. T-196 효과 검증 — PRE_SOURCE_FILTER 차단 건수 (KIS_MOCK 비D6)

### 구현 상태
- **코드**: cte_pipeline.py line 441
- **Config** (`config/funnel_score.yaml`):
  ```yaml
  session_strategy_filter:
    enabled: true
    rules:
      VIRTUAL_KIS_MOCK:
        allowed:
          - D6
        block_reason: "KIS_MOCK 세션 D6 전용화 (T-196): D6 외 전략 차단"
  ```

### DB 기록 현황
| 항목 | 값 |
|------|-----|
| PRE_SOURCE_FILTER 차단 기록 | **0건** |
| KIS_MOCK approved 비D6 건수 | **33건** (D2:3, D4:4, D7:7, D-ORB:8, S1:5 등) |

### KIS_MOCK approved 비D6 현황

| strategy_id | KIS_MOCK approved 건수 |
|-------------|----------------------|
| D2          |                    3 |
| D4          |                    4 |
| D7          |                    7 |
| D-ORB       |                    8 |
| S1          |                    5 |
| **소계**    |                   27 |

### 분석
- **설정 파일**: `session_strategy_filter.enabled: true` → 필터 활성화 상태
- **DB 기록**: PRE_SOURCE_FILTER = 0건, KIS_MOCK 비D6 approved 27건 존재
- **결론**: Mock trade 시뮬레이터가 CTE pipeline의 PRE_SOURCE_FILTER를 우회
- 이는 Mock 시뮬레이터가 `cte_pipeline.py` 경로가 아닌 별도 경로로 mock trade를 생성하기 때문으로 판단
- **03-09 실시간 매매**에서는 CTE pipeline을 통과하므로 PRE_SOURCE_FILTER 정상 작동 예상
- Mock 시뮬레이터에 필터 적용 여부는 별도 태스크로 검토 필요

---

## 7. T-227 FunnelScore 재교정 — 점수 분포 변화

### 현재 상태
| 항목 | 값 |
|------|-----|
| T-227 재교정안 | A/B/C 3건 도출, CEO 승인 대기 |
| 현재 임계값 | 0.35 (일부 0.40) |
| 최대 실측 FunnelScore | 0.261 |
| L3.1_FUNNEL 차단 | 40건 / 184건 = 21.7% |

### T-227 재교정안별 예상 효과 (기준: 184건 시뮬)

| 안 | 방식 | 예상 통과 | 비율 |
|----|------|----------|------|
| A | Fail-Open (0.20 미만만 차단) | 164/184 | 89% |
| B | 재가중 (L0 가중치 조정) | 53/184 | 29% |
| C | 임계값 0.20으로 하향 | 166/184 | 90% |

### 분석
- 현재 재교정 미적용 상태: 184건 중 0건 통과 (FunnelScore < 임계값)
- T-227 재교정안 C (임계값 0.20) 적용 시 166/184 통과 예상
- **CEO 승인 후 즉시 적용 시** 03-09 거래 건수 대폭 증가 예상
- 재교정 없이는 avg PnL 개선 불가능 (구조적 차단 지속)

---

## 8. 기준선 비교 요약

| 항목 | 기준선 | 03-07 현재 | 판정 |
|------|--------|-----------|------|
| 총 거래 건수 | 184건 | 184건 | = 동일 |
| 승률 (TP/total) | 1.6% | 1.6% (3/184) | = 동일 |
| avg PnL | -0.622% | -0.622% | = 동일 |
| FORCED_EOD 비율 | 기준 미정 | 60.9% (28/46) | ❌ 미개선 |
| FunnelScore 최대 | 기준 미정 | 0.261 | ❌ 미개선 |

**결론**: 03-09 장 전 상태에서는 기준선 대비 변화 없음. T-195/T-196/T-207/T-227 구현은 완료되었으나 실시간 매매 효과는 03-09 장중/마감 후 확인 필요.

---

## 9. 미개선 항목 → 후속 지시 도출

| # | 항목 | 원인 | 후속 태스크 |
|---|------|------|-------------|
| 1 | FORCED_EOD 60.9% | Mock 시뮬레이터에서 T-195 PRE_TIME_GATE 우회 | Mock 시뮬레이터 T-195 필터 통합 (T-240 후보) |
| 2 | FunnelScore 최대 0.261 | L0/L1/L2 데이터 결함 (KOSPI오염/섹터미등록/수급없음) | T-227 재교정안 CEO 승인 → 즉시 적용 (T-241 후보) |
| 3 | PRE_SOURCE_FILTER 0건 | Mock 시뮬레이터 CTE pipeline 우회 | Mock 시뮬레이터 source filter 적용 또는 별도 검증 (T-242 후보) |
| 4 | D-ORB SL -3.612% | 갭하락 슬리피지 (SL캡 적용 후에도 초과 손실) | ATR SL + 갭보호 로직 개선 (T-243 후보) |
| 5 | avg PnL -0.622% | FunnelScore 구조 문제 + FORCED_EOD 과다 | T-227 재교정 + T-195 실시간 적용 → 재측정 |

---

## 10. 03-09 장 마감 후 재확인 체크리스트

### 실시간 매매 로그 확인 (16:00 이후 실행)
- [ ] `SELECT COUNT(*) FROM v4_mock_trades WHERE trade_date='2026-03-09'` → N건 확인
- [ ] PRE_TIME_GATE 차단 기록: `WHERE notes LIKE '%PRE_TIME_GATE%'`
- [ ] PRE_SOURCE_FILTER 차단 기록: `WHERE notes LIKE '%PRE_SOURCE_FILTER%'`
- [ ] FORCED_EOD 비율: N/M건 → 40% 미만 여부
- [ ] SL 발생 건수 및 전략별 손실 폭
- [ ] TP 발생 건수 (pnl_pct > 0)
- [ ] avg PnL → -0.4% 초과 여부
- [ ] FunnelScore 분포 변화 (T-227 적용 시)

---

## 11. 성공 기준 판정 (03-07 사전 평가)

| 검증 항목 | 기준 | 현재 | 판정 |
|-----------|------|------|------|
| T-187: FORCED_EOD < 40% | < 40% | 60.9% | ❌ FAIL |
| T-187: SL D-ORB < 1.8% | < 1.8% | -3.612% (실손) | ❌ FAIL |
| T-187: SL D4 < 1.5% | < 1.5% | -2.673% (실손) | ❌ FAIL |
| T-187: TP ≥ 1건 | ≥ 1건 | 3건 | ✅ PASS |
| T-187: avg PnL > -0.4% | > -0.4% | -0.622% | ❌ FAIL |
| T-189: 0.28~0.35 통과 건수 | > 0건 | 0건 | ❌ FAIL |
| T-195: PRE_TIME_GATE 차단 확인 | 코드 존재 | 구현 완료 / DB 0건 | ⚠️ PARTIAL |
| T-196: PRE_SOURCE_FILTER 차단 확인 | 코드 존재 | 구현 완료 / DB 0건 | ⚠️ PARTIAL |
| T-227: FunnelScore 분포 변화 | CEO 승인 후 | 미적용 | ⚠️ PENDING |

**전체 판정: FAIL (03-09 장 전 기준) — 03-09 실시간 매매 데이터 확인 후 재평가 필요**

---

## 12. 개선 방향 요약

1. **즉시 필요**: T-227 FunnelScore 재교정안 CEO 승인 및 적용 (임계값 0.20 또는 B안 재가중)
2. **03-09 우선 관찰**: PRE_TIME_GATE/PRE_SOURCE_FILTER 실시간 매매에서 정상 작동 여부
3. **중기 과제**: Mock 시뮬레이터 CTE pipeline 통합 (T-195/T-196 효과를 시뮬에서도 측정 가능하게)
4. **검토 필요**: ATR SL cap 이후에도 발생하는 갭/슬리피지 손실 관리 방안

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-0309-TRADING-MONITOR-001-20260309.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-0309-TRADING-MONITOR-001-20260309.md
- 커밋: (push 후 기재)
- HTTP 확인: (push 후 기재)
- HANDOVER 업데이트: (완료 후 기재)

---

**체크포인트**
- [ ] 코드 레포 커밋 완료 (코드 변경 없음, 보고서만)
- [ ] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)
