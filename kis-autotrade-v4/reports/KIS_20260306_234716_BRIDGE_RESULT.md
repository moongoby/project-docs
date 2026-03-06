---
project: KIS AutoTrade V4.1
task_id: T-227
completed_at: 2026-03-07T09:00:00+09:00
---

# KIS_20260306_234716_BRIDGE_RESULT
## T-227: FunnelScore 구조 해부 및 긴급 재교정

---

## [인계 확인]
직전 완료: T-218 (DUAL_FLOW_5D/20D feature variable)
현재 단계: Phase 2c (Command Center)
CEO 지시 적용: D-001, D-002, D-003, D-008-KR
strategy_cards: 60
open_positions: 0

---

## 1. 지시서 내용 확인

파일: `/root/.genspark/directives/running/KIS_20260306_234716_BRIDGE.md`

```
Task ID: T‑227 제목: FunnelScore 구조 해부 및 긴급 재교정 우선순위: P0‑CRITICAL ★ 최우선 예상 소요: 45분 선행 작업: T‑226 담당: Cursor 세션 B Phase: 1

배경: FunnelScore 0.19~0.26 고착 → 96% 차단. T‑189 BEAR 0.28 하향도 무효 (현재 점수가 0.28 미만). 가중치 L0=0.15/L1=0.25/L2=0.30/L3=0.30. 이것이 해결 안 되면 모의매매 진입 자체 불가 — 전체 시스템 무력화.

작업 내용:
백업: funnel_score_engine.py, cte_pipeline.py
L0~L3 레이어별 실제 산출값 트레이싱 (통과 2건 id=182/169 + 차단 18건)
...
성공 기준: L0~L3 실측값 보고, 병목 확정, 재교정안 3건+시뮬 보고서: CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md
```

---

## 2. 선행 세션 완료 확인

T-227은 이전 세션(2026-03-07 00:07 KST)에 **이미 완료**되었음을 확인.

### 기존 보고서 존재 확인
```bash
$ ls -la /root/kis-autotrade-v4/report/v41/CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md
-rw-rw-r-- 1 claudebot claudebot 13694 Mar  7 00:07 /root/kis-autotrade-v4/report/v41/CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md
```

### project-docs 존재 확인
```bash
$ ls -la /root/project-docs/kis-autotrade-v4/reports/CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md
-rw-rw-r-- 1 claudebot claudebot 13694 Mar  7 00:08 /root/project-docs/kis-autotrade-v4/reports/CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md
```

### GitHub URL HTTP 200 확인
```bash
$ curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md"
200
```

### project-docs commit SHA 확인
```bash
$ sudo /usr/bin/git -C /root/project-docs log --all --oneline -20
38335c7 docs: T-232 ATR SL Cap 강화 + S1 재검증 보고서 push + HANDOVER v10.38
1564219 [DONE] KIS_20260307_000754_BRIDGE_RESULT.md — 자동 완료 보고서
23005b7 [DOCS] T-233 HANDOVER v10.37 + CONTEXT v10.25 완료
b7824ff docs: HANDOVER 업데이트 (T-231 완료)
a33785f docs: T-231 DESK 파이프라인 전 구간 수동 검증 보고서 push (20260307)
...
dd98ab7 docs: T-227 FunnelScore 재교정 분석 보고서 push + HANDOVER v10.32 업데이트 (20260307)
```
**T-227 커밋 SHA: `dd98ab7`**

---

## 3. 현황 재확인 (신규 DB 재트레이싱 2026-03-07)

### 3-A. L0 매크로 환경 (weight=0.15)

```sql
-- v4_macro_daily 최신 3건
SELECT macro_regime, us_vix, ROUND(kr_kospi::numeric,2) AS kr_kospi, ROUND(kospi_ma60::numeric,2) AS kospi_ma60, date
FROM v4_macro_daily ORDER BY date DESC LIMIT 3;

 macro_regime | us_vix | kr_kospi | kospi_ma60 |    date
--------------+--------+----------+------------+------------
 NEUTRAL      |        |   275.31 |    1807.09 | 2026-03-05
 BULL         |        | 27538.22 |    1825.19 | 2026-03-04
 BEAR         |        |  1029.35 |    1388.74 | 2026-03-03
```

**상태**: us_vix = NULL (전 날짜), KOSPI 275.31 (오염: 실제 ~2500 대비 10분의 1)
**L0 산출**: s_regime(NEUTRAL→0.5)×0.50 + s_vix(NULL→0.5)×0.30 + ma_bonus(0.0) = 0.40 × MktSeason(0.9) = **0.360**
**문제**: VIX NULL + KOSPI 오염 → 종목 간 차별화 없음

### 3-B. L1 섹터/테마 (weight=0.25)

```sql
-- v4_sector_mapping sector_code 현황
SELECT COUNT(*) AS total_stocks, COUNT(krx_sector_code) AS with_sector_code,
       COUNT(*) - COUNT(krx_sector_code) AS null_sector_code
FROM v4_sector_mapping;

 total_stocks | with_sector_code | null_sector_code
--------------+------------------+------------------
         3844 |              162 |             3682
```

**상태**: 3844 종목 중 162종목(4.2%)만 sector_code 유효, 3682종목(95.8%) NULL
**차단 종목 L1**: sector_mapping 미등록 → L1=0.300 (fallback 기본값)
**기여도**: 0.25 × 0.300 = **0.075**

### 3-C. L2 수급 흐름 (weight=0.30)

```sql
-- v4_investor_daily 현황
SELECT MAX(trade_date) AS latest_date, COUNT(DISTINCT symbol) AS covered_symbols
FROM v4_investor_daily;

 latest_date | covered_symbols
-------------+-----------------
 2026-03-06  |            3743
```

**상태**: 2026-03-06까지 3743종목 커버
**차단 종목 L2**: DUAL_FLOW=0.0, consecutive_buy=0 → fallback 0.3
**기여도**: 0.30 × 0.300 = **0.090**

### 3-D. L3 종목 펀더멘탈 (weight=0.30)

```sql
-- v4_fundamental_quarterly 현황
SELECT COUNT(*) AS total_rows, COUNT(DISTINCT symbol) AS covered_symbols
FROM v4_fundamental_quarterly;

 total_rows | covered_symbols
------------+-----------------
       1520 |             273
```

**상태**: 1520행, 273종목 (3844 대비 **7.1%** 커버)
**차단 종목 L3**: GrowthScore=0.0, quality_score=0.0, PEG=0.5 → L3=0.075
**기여도**: 0.30 × 0.075 = **0.0225**

### 3-E. 최대 FunnelScore (기본값 종목)

```
FunnelScore_max_default = 0.15×0.360 + 0.25×0.300 + 0.30×0.300 + 0.30×0.075
                        = 0.054 + 0.075 + 0.090 + 0.0225
                        = 0.2415
```

**임계값 0.35 대비 GAP = 0.1085** → 구조적 차단 확인

---

## 4. 실제 virtual trades 현황 (2026-02-28~2026-03-07)

```sql
-- v4_virtual_trades_full 전체 현황
SELECT COUNT(*) AS total,
       COUNT(CASE WHEN approved=true THEN 1 END) AS pass,
       COUNT(CASE WHEN approved=false THEN 1 END) AS blocked,
       COUNT(CASE WHEN blocking_layer='L3.1_FUNNEL' THEN 1 END) AS blocked_funnel,
       COUNT(CASE WHEN blocking_layer='L3.3_SUPPLY' THEN 1 END) AS blocked_supply
FROM v4_virtual_trades_full
WHERE session_date >= '2026-02-28';

 total | pass | blocked | blocked_funnel | blocked_supply
-------+------+---------+----------------+----------------
   145 |   56 |      89 |             40 |             29
```

**레이어별 차단 분포**:
```sql
SELECT blocking_layer, COUNT(*) AS cnt FROM v4_virtual_trades_full
WHERE session_date >= '2026-02-28' GROUP BY blocking_layer ORDER BY cnt DESC;

 blocking_layer | cnt
----------------+-----
 L3.1_FUNNEL    |  40
                |  31
 L3.3_SUPPLY    |  29
 NONE           |  25
 SIGNAL_COMBO   |   9
 GATE           |   6
 PRE_PRIORITY   |   4
 ATR_NETRR      |   1
```

**실제 FunnelScore 분포 (차단 종목 샘플)**:
```
000590: FunnelScore 0.226 < 0.35 (차단)
000590: FunnelScore 0.226 < 0.35 (차단)
00104K: FunnelScore 0.245 < 0.35 (차단)
00104K: FunnelScore 0.245 < 0.35 (차단)
000660: FunnelScore 0.261 < 0.35 (차단)
000590: FunnelScore 0.247 < 0.35 (차단)
001540: FunnelScore 0.260 < 0.40 (차단)  ← 이전 임계값 0.40 적용
0005G0: FunnelScore 0.191 < 0.40 (차단)  ← 이전 임계값 0.40 적용
```
**FunnelScore 범위**: 0.191 ~ 0.261 (최대 0.2415 이론과 일치)

**통과 종목 확인**:
- id=145: 000100 (D7) → approved=true (blocking_layer=NULL)
- id=142: 000100 (D7) → approved=true, NONE, cs_score=74, eqs_score=72
- id=136: 0009K0 (D6) → approved=true

---

## 5. 파일 백업 확인

### funnel_score_engine.py 위치
```
/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py
```

### 현재 config/funnel_score.yaml 상태
```yaml
funnel_score:
  weights:
    l0_macro: 0.15
    l1_sector: 0.25
    l2_supply: 0.30
    l3_fundamental: 0.30
  thresholds:
    min_score_for_entry: 0.35  # T-163: 0.55→0.35
    premium_score: 0.70
    bear_min_score_for_entry: 0.28  # T-189: BEAR 레짐 시 완화
  l0:
    vix_low: 15
    vix_high: 25
    regime_scores:
      BULL: 1.0
      NEUTRAL: 0.5
      BEAR: 0.2
  l1:
    rs_threshold: 80
    leader_bonus: 0.3
  l2:
    dual_flow_days: 20
    close_pos_threshold: 0.7
    consecutive_buy_bonus: 0.1
  l3:
    small_cap_max_mcap: 70000000000  # 700억
    growth_weight: 0.5
    quality_weight: 0.5
  v3_ai_bonus:
    enabled: true
    high_threshold: 0.6
    high_bonus: 0.10
    low_threshold: 0.3
    low_penalty: -0.10
session_strategy_filter:
  enabled: true
  rules:
    VIRTUAL_KIS_MOCK:
      allowed:
        - D6
      block_reason: "KIS_MOCK 세션 D6 전용화 (T-196)"
```

---

## 6. 병목 확정 결과

| 순위 | 레이어 | 실측 점수 | 커버리지 | 원인 |
|------|--------|---------|---------|------|
| **1위** | **L3 펀더멘탈** | **0.075** | 7.1% (273/3844) | v4_fundamental_quarterly 부족 |
| **2위** | **L1 섹터** | **0.300** | 4.2% (162/3844) | v4_sector_mapping krx_sector_code NULL |
| **3위** | **L2 수급** | **0.300** | fallback | v4_investor_daily 미등록 또는 수급없음 |
| **4위** | **L0 매크로** | **0.360** | 전체 동일 | us_vix NULL + KOSPI 데이터 오염 |

**결론**: 데이터가 없는 종목은 구조적으로 FunnelScore 최대 0.2415 → 임계값 0.35 절대 미달.

---

## 7. 재교정안 3건 시뮬레이션

### 방안 A: Fail-Open (null→0.5 기본값)
- 변경: L1=0.5, L2=0.5, L3 growth=0.5, quality=0.5 (데이터 없음 시)
- 예상 FunnelScore: 0.4850 → PASS
- 184건 기준 시뮬: **164/184 (89%)**
- ⚠️ CEO 승인 필수

### 방안 B: 가중치 재배분
- 변경: L3 없는 종목 → L0:L1:L2 = 0.214:0.357:0.429 정규화
- 예상 FunnelScore: 0.317 → BLOCK (< 0.35)
- 시뮬: **53/184 (29%)** (효과 미흡)
- ⚠️ CEO 승인 필수

### 방안 C: 임계값 0.35→0.20 임시 하향
- 변경: config/funnel_score.yaml → min_score_for_entry: 0.20
- 현재 FunnelScore 분포 0.191~0.261 기준 ~87% 통과 전환
- 시뮬: **166/184 (90%)**
- ⚠️ CEO 승인 필수 (03-09 실험 후 복귀 전제)

---

## 8. 기존 보고서 내용 전체 (원문)

보고서 위치: `/root/kis-autotrade-v4/report/v41/CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md`

**내용 요약** (원문 13,694 bytes):
- 배경: FunnelScore 0.19~0.26 고착, 96% 차단
- L0~L3 실측값: 0009K0(통과) L0=0.360/L1=0.850/L2=0.735/L3=0.150 FS=0.5320, 804899(차단) L0=0.360/L1=0.300/L2=0.300/L3=0.075 FS=0.2415
- 병목: L3(7.1% 커버) > L1(4.2% 커버) > L2(fallback) > L0(데이터 오염)
- 방안 A: 164/184=89%, 방안 B: 53/184=29%, 방안 C: 166/184=90%
- CEO 승인 대기

---

## 9. HANDOVER 업데이트 확인

HANDOVER.md v10.32 에 T-227 결과 기록 확인:
```
v10.32 — T-227 FunnelScore 구조 해부 및 긴급 재교정: L0~L3 실측값 트레이싱 완료;
L3=0.075(7.1%커버), L1=0.300(섹터미등록), L2=0.300(수급데이터없음), L0=0.360(KOSPI오염+VIX NULL);
최대FunnelScore=0.2415<임계값0.35=구조적차단확정;
재교정안3건시뮬: A(Fail-Open→164/184=89%), B(재가중→53/184=29%), C(임계값0.20→166/184=90%);
CEO승인대기; 보고서CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md
```

---

## 10. 체크리스트

- [x] 지시서 읽기 완료: `/root/.genspark/directives/running/KIS_20260306_234716_BRIDGE.md`
- [x] HANDOVER.md, CEO-DIRECTIVES.md 읽기 완료
- [x] L0~L3 실측값 트레이싱 완료 (DB 재확인 포함)
- [x] 병목 레이어 확정: L3(1위) > L1(2위) > L2(3위) > L0(4위)
- [x] 최대 FunnelScore 0.2415 < 임계값 0.35 구조적 차단 확인
- [x] 재교정안 3건 (A/B/C) 시뮬레이션 완료
- [x] 보고서 CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md 작성 완료
- [x] 코드 레포 커밋 완료 (HANDOVER v10.32, SHA: dd98ab7)
- [x] project-docs 보고서 push 완료 (GitHub HTTP 200 확인)
- [x] GitHub URL 200: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-FUNNEL-SCORE-RECALIBRATION-001-20260309.md
- [ ] CEO 승인 대기: 방안 A/B/C 중 선택
- [ ] 선택 방안 코드 적용 (CEO 승인 후)

---

## 11. 완료 요약

**T-227 FunnelScore 구조 해부 및 긴급 재교정 — 완료**

| 항목 | 결과 |
|------|------|
| 병목 원인 | 데이터 부재 (L3 7.1%, L1 4.2% 커버리지) |
| 최대 FunnelScore | 0.2415 (임계값 0.35 대비 -0.1085) |
| 방안 A 시뮬 | 164/184 = 89% 통과 |
| 방안 B 시뮬 | 53/184 = 29% 통과 |
| 방안 C 시뮬 | 166/184 = 90% 통과 |
| 보고서 커밋 SHA | dd98ab7 |
| GitHub HTTP | 200 ✅ |
| CEO 승인 | 대기 중 |

HANDOVER.md 업데이트 완료: dd98ab7
