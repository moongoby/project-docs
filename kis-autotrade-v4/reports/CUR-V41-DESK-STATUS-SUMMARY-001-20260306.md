# CUR-V41-DESK-STATUS-SUMMARY-001-20260306

[인계 확인]
직전 완료: T-156 (SELL_FAILED 전건청산+모의매매현황)
현재 단계: Phase 2c (Command Center)
CEO 지시 적용: D-009, D-010, D-011, D-014
strategy_cards: 60
open_positions: 0 (SELL_FAILED=0 확인됨, T-156 기준)

---

**Task ID**: T-164
**제목**: DESK 전체 성과 진단 + DESK5/DESK1 상태 확인 (T-157/T-159 통합 축소)
**작성일**: 2026-03-06
**서버**: 211 (kis-autotrade-v4)
**우선순위**: P1-HIGH
**배경**: T-157/T-159 타임아웃 → 핵심 쿼리 축소 재실행

---

## 1. DESK별 mock trade 성과 (2026-03-02 이후)

> 쿼리: `SELECT strategy_id, COUNT(*), AVG(pnl_pct EXCLUDING -0.47), wins, worst, best FROM v4_mock_trades WHERE created_at >= '2026-03-02' GROUP BY strategy_id`

| strategy_id | 건수 | avg_pnl (비용제외) | 승건 | worst | best | 승률 |
|-------------|------|-------------------|------|-------|------|------|
| D-ORB | 29 | -1.132% | 1 | -3.612% | +0.199% | 3.4% |
| D7 | 29 | -1.583% | 0 | -1.801% | -0.47% | 0% |
| D6 | 29 | -0.374% | 2 | -1.879% | +0.424% | 6.9% |
| D5 | 29 | 0.000% | 0 | 0% | 0% | 0% |
| S1 | 16 | None (전건 -0.47%) | 0 | -0.47% | -0.47% | 0% |
| D2 | 16 | None (전건 -0.47%) | 0 | -0.47% | -0.47% | 0% |
| D4 | 16 | -2.673% | 0 | -2.673% | -0.47% | 0% |
| **합계** | **164** | **-0.967%** | **3** | | | **1.8%** |

### 날짜별 집계

| 날짜 | 건수 | 승건 | avg_pnl |
|------|------|------|---------|
| 2026-03-02 | 7 | 0 | -0.470% |
| 2026-03-03 | 56 | 0 | -0.470% |
| 2026-03-04 | 34 | 0 | -1.039% |
| 2026-03-05 | 56 | 3 | -0.631% |
| 2026-03-06 | 11 | 0 | None (미청산) |

### 핵심 발견
- **전체 승률 1.8% (3승/164건)** — 극히 저조
- D6만 유일하게 플러스 거래 존재 (best=+0.424%) — D6가 가장 성과 우수
- D5: pnl_pct=0 전건 → 청산 미완료 (미청산 포지션이거나 데이터 기록 이슈)
- S1, D2: 전건 -0.47% (거래비용만) → 진입 후 즉시 비용만 기록되고 있음 (실거래 없이 비용만 기록)
- D4: avg=-2.673% → 손절이 실제로 발동되고 있음
- D-ORB: 29건 중 1건 승 (상세 확인 필요, 별도 전략)
- 03-03 56건 모두 -0.47%: 해당일 모든 거래가 비용만 기록 (미체결 or 즉시청산)

---

## 2. strategy_cards 현황

> 쿼리: `SELECT desk_id, COUNT(*), SUM(CASE WHEN is_active THEN 1 ELSE 0 END) FROM strategy_cards GROUP BY desk_id`

| desk_id | total | active | 비고 |
|---------|-------|--------|------|
| 1 (DESK1) | 10 | 10 | cards 등록됨, 실행 인프라 없음 |
| 2 (DESK2) | 16 | **0** | ⚠️ active=0 전체 비활성 |
| 3 (DESK3) | 11 | 11 | 정상 |
| 4 (DESK4) | 9 | 9 | 정상 |
| 5 (DESK5) | 10 | 10 | 정상 |
| None | 4 | 3 | desk 미분류 카드 |
| **합계** | **60** | **43** | |

**핵심 발견**: DESK2 strategy_cards 16개 전체 비활성(is_active=false). T-125/T-128 멀티컨디션 Phase A 구현 완료됐으나 실제 카드 활성화 미수행.

---

## 3. DESK 풀 현황

### DESK5 watchlist
```
count=20, status=WATCHING
```
- 20개 종목 전체 WATCHING 상태
- 전일(T-151) 대비 동일: 20개 유지

### DESK4 watchlist
```
count=18, status=WATCHING
```
- 18개 종목 전체 WATCHING 상태
- 전일(T-151) 대비 동일: 18개 유지

### DESK3 pool
```
count=306, status=ACTIVE
```
- **306개 ACTIVE** — HANDOVER.md 기록(106개)보다 **+200개 급증**
- 원인 추정: node_detector_engine desk3 cron 이 03-06 정상 실행됨 (08:50/16:00 KST)
- 03-06 기준 DESK3 풀 규모 대폭 확대

---

## 4. DESK1 상태 확인

### 4-1. 스캘핑 관련 파일
```python
scalp_files = [f for f in os.listdir('/root/kis-autotrade-v4/backend/app/services/')
               if 'scalp' in f.lower() or 'desk1' in f.lower()]
# 결과: 없음 (빈 리스트)
```
**DESK1 관련 서비스 파일 0개** — 스캘핑 엔진 미구현 확인

### 4-2. DESK1 관련 cron
```
desk1_crons = []  # DESK1/scalp 관련 cron 없음
```
**DESK1 cron 등록 없음** — 자동 실행 체계 없음

### DESK1 종합 판단
| 항목 | 상태 |
|------|------|
| strategy_cards | 10개 등록 (all active) |
| 서비스 파일 | 없음 |
| cron 등록 | 없음 |
| 실행 여부 | **미실행** |

→ **DESK1은 strategy_cards만 등록된 상태, 실제 스캘핑 엔진 미구현**

---

## 5. 전체 cron 현황 (DESK 관련)

총 등록 cron: 약 20+개

| 태그 | 시간 | 대상 |
|------|------|------|
| KIS T-092 | 07:00 UTC (16:00 KST) 평일 | DESK5 노드감지 |
| KIS T-092 | 07:05 UTC (16:05 KST) 평일 | DESK4 노드감지 |
| KIS T-092 | 23:50 UTC (08:50 KST 다음날) | DESK3 노드감지 (프리마켓) |
| KIS T-092 | 07:10 UTC (16:10 KST) 평일 | DESK3 노드감지 (장마감) |
| KIS T-092 | 07:30 UTC (16:30 KST) 평일 | daily_summary |
| KIS TASK-077 | 09:00-15:00 KST 평일 | virtual_hourly_report |

**DESK1/DESK2 전용 cron: 없음**

---

## 6. 종합 진단

### 전략별 상태 요약

| DESK | cards(active) | 풀 상태 | mock성과 | cron | 판정 |
|------|--------------|---------|---------|------|------|
| DESK1 | 10/10 | 없음 | -/ | 없음 | ❌ 미구현 |
| DESK2 | 16/0 | 없음 | -0.47% (비용만) | 없음 | ⚠️ 비활성 |
| DESK3 | 11/11 | 306 ACTIVE | -/ | 있음 | ✅ 정상 |
| DESK4 | 9/9 | 18 WATCHING | -2.673% | 있음 | ⚠️ 손실 중 |
| DESK5 | 10/10 | 20 WATCHING | 0% | 있음 | ⚠️ 미체결 |
| D6 | - | DESK2 내 | -0.374% (승2건) | - | ✅ 최우수 |
| D7 | - | DESK2 내 | -1.583% (승0건) | - | ❌ 전패 |

### 주요 이슈

1. **전체 승률 1.8%** — 정상적인 매매 미수행 의심
   - 03-02~03-03 전건 -0.47% (비용만): 체결 후 즉시 시스템 청산 또는 mock 기록 방식 이슈
   - D5 전건 pnl=0: 청산 미완료 가능성

2. **DESK2 전체 비활성** (is_active=0/16)
   - T-125/T-128 멀티컨디션 구현 완료했으나 카드 활성화 안 됨
   - D6/D7 mock trade는 발생 → strategy_id 기반 매매는 동작 중

3. **DESK1 미구현**
   - strategy_cards 10개 등록됐으나 실행 엔진/cron 없음
   - 스캘핑 전략 개발 필요

4. **DESK3 풀 306개** (기존 기록 106개 대비 +200)
   - 긍정적: 풀 확대
   - 확인 필요: 과다 종목이 품질 저하 위험

5. **D4 avg=-2.673%**: 손절이 실제 발동 중이나 전패
   - E2A 파라미터(SL2%/TP3%) 적용 후에도 성과 부진

---

## 7. 권고사항

1. **DESK2 활성화 검토**: strategy_cards is_active=true 전환 (CEO 승인 필요)
2. **D5 pnl=0 원인 조사**: 청산 로직 또는 exit_manager 점검
3. **DESK1 구현 일정 확정**: 스캘핑 엔진 개발 필요
4. **D6 집중 관찰**: 유일하게 플러스 거래 발생, 파라미터 최적화 우선
5. **DESK3 풀 품질 점검**: 306개가 적정 수준인지 확인

---

## 8. DB 조회 원시 데이터

### v4_mock_trades (2026-03-02~)
```
strategy_id  trades   avg_pnl   wins     worst       best
D-ORB           29    -1.132      1    -3.612      0.199
D7              29    -1.583      0    -1.801      -0.47
D6              29    -0.374      2    -1.879      0.424
D5              29     0.000      0         0          0
S1              16      None      0     -0.47      -0.47
D2              16      None      0     -0.47      -0.47
D4              16    -2.673      0    -2.673      -0.47
총계           164    -0.967      3
```

### strategy_cards
```
desk_id  total  active
1           10      10
2           16       0
3           11      11
4            9       9
5           10      10
None         4       3
합계        60      43
```

### 풀 테이블
```
v4_desk5_watchlist: 20 WATCHING
v4_desk4_watchlist: 18 WATCHING
v4_desk3_pool:     306 ACTIVE
```

### DESK1 파일/cron
```
scalp_files: []  (없음)
desk1_crons: []  (없음)
```

---

**실행 시각**: 2026-03-06 10:37:25 KST
**쿼리 실행**: Python psycopg2 (venv)
**DB**: kisautotrade @ localhost:5432
**절대 금지 사항 준수**: DB 변경 없음, 서비스 재시작 없음
