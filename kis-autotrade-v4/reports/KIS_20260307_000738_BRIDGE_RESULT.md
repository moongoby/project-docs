---
project: kis-autotrade-v4
task_id: T-234
completed_at: 2026-03-07T00:40:39+0900
---

# KIS_20260307_000738_BRIDGE_RESULT

## 지시서 원문
```
Task ID: T-234 제목: 03-09 모의매매 실시간 모니터링 + 전체 효과 검증 서버: 211 (kis-autotrade-v4) 우선순위: P1-HIGH 예상 시간: 25분 의존성: T-226 + 장 마감 (16:00 이후 실행)

작업 내용:

SELECT * FROM v4_mock_trades WHERE trade_date='2026-03-09' ORDER BY id;
효과 검증 체크리스트:
T-187: FORCED_EOD < 40% / SL < 1.8%(D-ORB) < 1.5%(D4) / TP ≥1건 / avg PnL > -0.4%
T-189: 0.28~0.35 구간 통과 건수
T-195: PRE_TIME_GATE 차단 건수 (14:00 이후)
T-196: PRE_SOURCE_FILTER 차단 건수 (KIS_MOCK 비D6)
T-227 적용 시: FunnelScore 점수 분포 변화
기준선 비교: 184건/1.6%/-0.622% 대비 개선 여부
미개선 항목 → 후속 지시 도출

성공 기준: 검증 항목별 PASS/FAIL, 개선 방향 도출 보고서: CUR-V41-0309-TRADING-MONITOR-001-20260309.md 금지: strategy_cards 변경, 서비스 재시작 HANDOVER 업데이트 필수 → git push → GitHub URL + 커밋 SHA + HTTP 200 보고
```

---

## 1. HANDOVER/CEO-DIRECTIVES 인계 확인

**실행**: `cat /root/project-docs/kis-autotrade-v4/HANDOVER.md` 및 `cat /root/project-docs/kis-autotrade-v4/CEO-DIRECTIVES.md` 완료

**인계 확인**:
- 직전 완료: T-235 (SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2), T-232 (ATR SL Cap 강화)
- 현재 단계: Phase 2C (Command Center)
- CEO 지시 적용: D-001, D-002, D-003, D-008-KR, D-010, D-011
- HANDOVER 버전: v10.37 → v10.38 (본 작업 완료 후 갱신)

---

## 2. SQL 실행 결과

### 2026-03-09 데이터 조회
```sql
SELECT * FROM v4_mock_trades WHERE trade_date='2026-03-09' ORDER BY id;
-- 결과: 0 rows
```

**결론**: 오늘(2026-03-07 KST)은 토요일로 2026-03-09(월) 장이 미개장 상태. 03-09 데이터 없음.
현재 데이터 범위: 2026-03-02 ~ 2026-03-06 (총 184건)

### 현재 데이터 현황 쿼리
```sql
SELECT trade_date, COUNT(*) as cnt FROM v4_mock_trades GROUP BY trade_date ORDER BY trade_date DESC;
```
```
 trade_date | cnt
------------+-----
 2026-03-06 |  31
 2026-03-05 |  56
 2026-03-04 |  34
 2026-03-03 |  56
 2026-03-02 |   7
```

### 전체 통계
```sql
SELECT COUNT(*), ROUND(AVG(pnl_pct)::numeric,4) as avg_pnl, MIN(pnl_pct), MAX(pnl_pct) FROM v4_mock_trades;
```
```
 count | avg_pnl | min_pnl | max_pnl
-------+---------+---------+---------
   184 | -0.6221 | -3.6120 |  0.4240
```

---

## 3. T-187 효과 검증

### 전략별 FORCED_EOD/SL/TP 분석 쿼리
```sql
SELECT strategy_id, COUNT(*) as total, COUNT(CASE WHEN notes LIKE '%SL%' THEN 1 END) as sl_cnt,
  COUNT(CASE WHEN notes LIKE '%FORCED_CLOSE_EOD%' THEN 1 END) as forced_eod_cnt,
  ROUND(COUNT(CASE WHEN notes LIKE '%FORCED_CLOSE_EOD%' THEN 1 END)*100.0/COUNT(*),1) as forced_eod_pct,
  COUNT(CASE WHEN pnl_pct > 0 THEN 1 END) as tp_cnt,
  ROUND(AVG(pnl_pct)::numeric,4) as avg_pnl
FROM v4_mock_trades
WHERE notes LIKE '%"approved": true%' AND exit_price IS NOT NULL
GROUP BY strategy_id ORDER BY strategy_id;
```
```
 strategy_id | total | sl_cnt | forced_eod_cnt | forced_eod_pct | tp_cnt | avg_pnl
-------------+-------+--------+----------------+----------------+--------+---------
 D2          |     3 |      0 |              3 |          100.0 |      0 | -0.4700
 D4          |     4 |      1 |              3 |           75.0 |      0 | -1.0208
 D5          |     1 |      0 |              0 |            0.0 |      0 |  0.0000
 D6          |    13 |      0 |              5 |           38.5 |      2 | -0.4331
 D7          |     8 |      0 |              6 |           75.0 |      0 | -0.6914
 D-ORB       |    12 |      1 |              6 |           50.0 |      1 | -0.8010
 S1          |     5 |      0 |              5 |          100.0 |      0 | -0.4700
```

### 전체 approved exits 통계
```sql
SELECT COUNT(*) as total_approved_exits,
  COUNT(CASE WHEN notes LIKE '%FORCED_CLOSE_EOD%' THEN 1 END) as forced_eod_cnt,
  ROUND(COUNT(CASE WHEN notes LIKE '%FORCED_CLOSE_EOD%' THEN 1 END) * 100.0 / COUNT(*), 1) as forced_eod_pct,
  COUNT(CASE WHEN notes LIKE '%SL%' THEN 1 END) as sl_cnt,
  COUNT(CASE WHEN pnl_pct > 0 THEN 1 END) as tp_cnt,
  ROUND(AVG(pnl_pct)::numeric, 4) as avg_pnl
FROM v4_mock_trades
WHERE notes LIKE '%"approved": true%' AND exit_price IS NOT NULL;
```
```
 total_approved_exits | forced_eod_cnt | forced_eod_pct | sl_cnt | tp_cnt | avg_pnl
----------------------+----------------+----------------+--------+--------+---------
                   46 |             28 |           60.9 |      2 |      3 | -0.6221
```

### T-187 검증 결과
| 항목 | 기준 | 현재 | PASS/FAIL |
|------|------|------|-----------|
| FORCED_EOD 비율 | < 40% | 60.9% | ❌ FAIL |
| SL D-ORB | < 1.8% | -3.612% (실손) | ❌ FAIL |
| SL D4 | < 1.5% | -2.673% (실손) | ❌ FAIL |
| TP ≥ 1건 | ≥ 1건 | 3건 | ✅ PASS |
| avg PnL | > -0.4% | -0.622% | ❌ FAIL |

---

## 4. T-189 효과 검증 — FunnelScore 0.28~0.35 구간

### FunnelScore 분포 쿼리
```sql
SELECT SUBSTRING(notes FROM 'FunnelScore 미달: ([0-9.]+)') as funnel_score, COUNT(*)
FROM v4_mock_trades WHERE notes LIKE '%FunnelScore 미달%'
GROUP BY 1 ORDER BY 1::numeric;
```
```
 funnel_score | count
--------------+-------
 0.191        |     6
 0.197        |     3
 0.226        |     9
 0.241        |     4
 0.245        |     4
 0.247        |     4
 0.250        |     1
 0.254        |     4
 0.257        |     2
 0.260        |     2
 0.261        |     1
```

**T-189 결과**: 0.28~0.35 구간 통과 건수 = **0건** (최대 FunnelScore = 0.261 < 임계값 0.35)

---

## 5. T-195 / T-196 효과 검증

### blocking_layer 분포 쿼리
```sql
SELECT blocking_layer_desc, COUNT(*)
FROM (
  SELECT CASE
    WHEN notes LIKE '%PRE_TIME_GATE%' THEN 'PRE_TIME_GATE'
    WHEN notes LIKE '%PRE_SOURCE_FILTER%' THEN 'PRE_SOURCE_FILTER'
    WHEN notes LIKE '%PRE_PRIORITY%' THEN 'PRE_PRIORITY'
    WHEN notes LIKE '%L3.3_SUPPLY%' THEN 'L3.3_SUPPLY'
    WHEN notes LIKE '%L3.1_FUNNEL%' THEN 'L3.1_FUNNEL'
    WHEN notes LIKE '%GATE%' THEN 'GATE'
    ELSE 'OTHER'
  END as blocking_layer_desc
  FROM v4_mock_trades WHERE notes LIKE '%"approved": false%'
) t GROUP BY 1 ORDER BY count DESC;
```
```
 blocking_layer_desc | count
---------------------+-------
 L3.3_SUPPLY         |    72
 L3.1_FUNNEL         |    40
 OTHER               |    13
 GATE                |     9
 PRE_PRIORITY        |     4
```

### 전체 blocking_layer 분포 (approved 포함)
```sql
-- 결과:
APPROVED/PASS: 46건
BLOCKED/L3.3_SUPPLY: 72건
BLOCKED/L3.1_FUNNEL: 40건
BLOCKED/SIGNAL_COMBO: 12건
BLOCKED/GATE: 9건
BLOCKED/PRE_PRIORITY: 4건
BLOCKED/ATR_NETRR: 1건
BLOCKED/PRE_TIME_GATE: 0건
BLOCKED/PRE_SOURCE_FILTER: 0건
```

### funnel_score.yaml 확인 결과
```yaml
session_strategy_filter:
  enabled: true
  rules:
    VIRTUAL_KIS_MOCK:
      allowed:
        - D6
      block_reason: "KIS_MOCK 세션 D6 전용화 (T-196): D6 외 전략 차단 (승률 0% 손실 제거)"
```

### KIS_MOCK approved 비D6 현황 (T-196 우회 확인)
```sql
SELECT strategy_id, COUNT(*), notes LIKE '%VIRTUAL_KIS_MOCK%' as is_kis_mock
FROM v4_mock_trades WHERE notes LIKE '%"approved": true%' AND notes LIKE '%VIRTUAL_KIS_MOCK%'
GROUP BY strategy_id, is_kis_mock ORDER BY strategy_id;
```
```
 strategy_id | count | is_kis_mock
-------------+-------+-------------
 D2          |     3 | t
 D4          |     4 | t
 D6          |     6 | t
 D7          |     7 | t
 D-ORB       |     8 | t
 S1          |     5 | t
```

**T-195 결과**: PRE_TIME_GATE 코드 확인 (cte_pipeline.py line 395) / DB 기록 0건 → Mock 시뮬레이터 우회
**T-196 결과**: PRE_SOURCE_FILTER enabled=true / DB 기록 0건, KIS_MOCK 비D6 approved 27건 존재 → Mock 시뮬레이터 우회

---

## 6. T-227 FunnelScore 재교정 현황

- **현재 상태**: 재교정안 A/B/C 도출, CEO 승인 대기
- **최대 FunnelScore**: 0.261 (임계값 0.35/0.40 미달)
- **재교정안 적용 없음** → 기준선 대비 변화 없음

---

## 7. 기준선 비교

| 항목 | 기준선 | 현재 (03-07) | 판정 |
|------|--------|-------------|------|
| 총 거래 건수 | 184건 | 184건 | = |
| 승률 | 1.6% | 1.6% (3/184) | = |
| avg PnL | -0.622% | -0.622% | = |
| FORCED_EOD | 미정 | 60.9% | ❌ 개선 필요 |
| FunnelScore 최대 | 미정 | 0.261 | ❌ 개선 필요 |

**전체 판정**: 기준선 대비 개선 없음 (03-09 장 전 상태)

---

## 8. 보고서 작성

**파일 생성**: `/root/kis-autotrade-v4/report/v41/CUR-V41-0309-TRADING-MONITOR-001-20260309.md`
- 크기: 12,070 bytes
- 생성 시간: 2026-03-07 00:38 KST

---

## 9. project-docs push

```bash
# 복사
cp /root/kis-autotrade-v4/report/v41/CUR-V41-0309-TRADING-MONITOR-001-20260309.md \
   /root/project-docs/kis-autotrade-v4/reports/CUR-V41-0309-TRADING-MONITOR-001-20260309.md

# HANDOVER.md 업데이트 (v10.38, T-234 추가)
# - 헤더: v10.38 — T-234 내용 추가
# - 섹션 2 완료 테이블: T-234 행 추가
# - 버전 이력: v10.38 T-234 행 추가

# git add + commit + push
sudo /usr/bin/git -C /root/project-docs add kis-autotrade-v4/HANDOVER.md \
  kis-autotrade-v4/reports/CUR-V41-0309-TRADING-MONITOR-001-20260309.md
sudo /usr/bin/git -C /root/project-docs commit -m "docs: T-234 03-09 모의매매 사전검증 보고서 push + HANDOVER v10.38 업데이트 (20260307)"
sudo /usr/bin/git -C /root/project-docs push origin master
```

**결과**:
```
[master c83fad1] docs: T-234 03-09 모의매매 사전검증 보고서 push + HANDOVER v10.38 업데이트 (20260307)
 2 files changed, 305 insertions(+), 2 deletions(-)
 create mode 100644 kis-autotrade-v4/reports/CUR-V41-0309-TRADING-MONITOR-001-20260309.md

To github.com:moongoby/project-docs.git
   1ec9065..c83fad1  master -> master
```

---

## 10. HTTP 200 확인

```bash
HTTP_REPORT=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-0309-TRADING-MONITOR-001-20260309.md")
HTTP_HANDOVER=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md")
```

**결과**:
- 보고서 HTTP: **200** ✅
- HANDOVER HTTP: **200** ✅

---

## 11. 최종 결과 요약

### 검증 항목별 PASS/FAIL
| 태스크 | 항목 | 기준 | 현재 값 | 판정 |
|--------|------|------|---------|------|
| T-187 | FORCED_EOD 비율 | < 40% | 60.9% (28/46건) | ❌ FAIL |
| T-187 | SL 손실 D-ORB | < 1.8% | -3.612% | ❌ FAIL |
| T-187 | SL 손실 D4 | < 1.5% | -2.673% | ❌ FAIL |
| T-187 | TP ≥ 1건 | ≥ 1건 | 3건 (+0.424%/+0.372%/+0.199%) | ✅ PASS |
| T-187 | avg PnL (approved exits) | > -0.4% | -0.622% | ❌ FAIL |
| T-189 | FunnelScore 0.28~0.35 통과 | > 0건 | 0건 | ❌ FAIL |
| T-195 | PRE_TIME_GATE 구현 확인 | 코드 존재 | cte_pipeline.py line 395 확인 | ⚠️ PARTIAL |
| T-195 | PRE_TIME_GATE DB 기록 | > 0건 | 0건 (Mock 우회) | ❌ DB없음 |
| T-196 | PRE_SOURCE_FILTER 구현 확인 | 설정 활성 | enabled=true 확인 | ⚠️ PARTIAL |
| T-196 | PRE_SOURCE_FILTER DB 기록 | > 0건 | 0건 (Mock 우회) | ❌ DB없음 |
| T-227 | FunnelScore 재교정 | CEO 승인 | 미적용 (CEO 승인 대기) | ⚠️ PENDING |

### 개선 방향 (후속 지시 도출)
1. **T-240 후보**: Mock 시뮬레이터 T-195 PRE_TIME_GATE 필터 통합
2. **T-241 후보**: T-227 재교정안 CEO 승인 → 즉시 적용 (임계값 0.20 또는 B안)
3. **T-242 후보**: Mock 시뮬레이터 PRE_SOURCE_FILTER 적용 또는 별도 검증
4. **T-243 후보**: ATR SL + 갭보호 로직 개선 (갭/슬리피지 초과 손실 방지)
5. **기본 조건**: 03-09 장 마감 후 실시간 데이터로 재검증 실행

---

## 체크포인트
- [x] 코드 레포 커밋: 코드 변경 없음 (보고서만)
- [x] project-docs 보고서 push 완료: 커밋 c83fad1, HTTP 200 확인
- [x] HANDOVER.md 업데이트: v10.38, 커밋 c83fad1, HTTP 200 확인

---

## 보고서 정보
- 보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-0309-TRADING-MONITOR-001-20260309.md
- 커밋: https://github.com/moongoby/project-docs/commit/c83fad1
- HANDOVER: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md
- HTTP: 200 확인 완료

HANDOVER.md 업데이트 완료: c83fad1
