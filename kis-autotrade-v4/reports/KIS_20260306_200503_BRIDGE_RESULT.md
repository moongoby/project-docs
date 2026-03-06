---
project: KIS AutoTrade V4.1
task_id: T-187
completed_at: 2026-03-06 20:23 KST
---

# KIS_20260306_200503_BRIDGE_RESULT

## T-187: 모의매매 승률 1.7% 긴급 진단 — 172건 전수 분석 (실제 184건)

---

## 1. 지시서 확인 결과

**파일**: /root/.genspark/directives/running/KIS_20260306_200503_BRIDGE.md
**내용 요약**:
- ID: T-187, 제목: 모의매매 승률 1.7% 긴급 진단 — 172건 전수 분석
- 우선순위: P0-CRITICAL, 브랜치: phase-2c-command-center
- 현황 확인 지시: 기존 분석 보고서 존재 여부 확인, DB 통계 조회, SL/TP config 확인
- 이미 분석 완료된 경우: 조정안 제시 여부 확인, 미반영 조치 즉시 적용

---

## 2. 현황 확인 단계

### 2-1. 기존 보고서 존재 여부 확인

```bash
ls /root/project-docs/kis-autotrade-v4/reports/*MOCK*20260306* /root/project-docs/kis-autotrade-v4/reports/*VIRTUAL*20260306* /root/project-docs/kis-autotrade-v4/reports/*TRADE*20260306* 2>/dev/null
```

**결과**:
```
/root/project-docs/kis-autotrade-v4/reports/CUR-V41-MOCK-TRADE-DIAGNOSIS-001-20260306.md
/root/project-docs/kis-autotrade-v4/reports/CUR-V41-MOCK-TRADE-DIAGNOSIS-001-20260306.md
/root/project-docs/kis-autotrade-v4/reports/CUR-V41-SELL-FAILED-CLEANUP-AND-MOCK-STATUS-001-20260306.md
---EXIT:2
```
→ **기존 분석 보고서 확인됨**: CUR-V41-MOCK-TRADE-DIAGNOSIS-001-20260306.md

### 2-2. mock_trades DB 현황

```sql
SELECT count(*), count(*) FILTER (WHERE pnl_pct > 0) as wins,
       avg(pnl_pct) as avg_pnl, min(pnl_pct) as worst, max(pnl_pct) as best
FROM v4_mock_trades WHERE created_at >= '2026-03-01';
```

**결과** (sudo psql 방식):
```
 count | wins |         avg_pnl         | worst  | best
-------+------+-------------------------+--------+-------
   184 |    3 | -0.62208695652173913043 | -3.612 | 0.424
(1 row)
```

→ 총 184건 (지시서의 172건보다 많음), 승리 3건, 평균 PnL -0.622%, 최악 -3.612%, 최대 +0.424%

### 2-3. SL/TP 현재 설정값 확인

**파일**: /root/kis-autotrade-v4/backend/app/services/unified_engine/core/exit_manager.py

**확인된 설정 (수정 전)**:
```python
STRATEGY_EXIT_PARAMS = {
    "D2":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    "D2A": {"sl_pct": 0.020, "trail_start": 0.015, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": 30},
    "D2B": {"sl_pct": 0.025, "trail_start": 0.015, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": 60},
    "D4":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},  # T-163: SL 2%→3%
    "D5":  {"sl_pct": 0.025, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    "S1":  {"sl_pct": 0.030, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": None},
    "D6":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    "D7":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    "D-ORB": {"sl_pct": 0.040, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},  # T-163: SL 2.5%→4.0%
}
```

---

## 3. 기존 보고서 분석 내용 검증

### 3-1. 기존 보고서 핵심 내용

**파일 위치**: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-MOCK-TRADE-DIAGNOSIS-001-20260306.md
**Task ID**: T-187 (원본: T-162), 작성일: 2026-03-06

**분석 기간**: 2026-02-28 ~ 2026-03-06

#### 핵심 통계 (보고서 Section 1)

| 지표 | 값 |
|---|---|
| 총 기록 건수 | 184건 |
| 차단(rejected) | 138건 (75%) |
| 실제 체결 | 46건 |
| 승리 (pnl > 0) | 3건 |
| 손실 (pnl < 0) | 40건 |
| **전체 승률** | **1.63% (3/184)** |
| 체결 기준 승률 | 6.5% (3/46) |
| 평균 PnL (체결) | -0.622% |
| 최악 손실 | -3.612% |
| 최대 수익 | +0.424% |

#### 일별 현황 (보고서 Section 3-1)

| 날짜 | 총 기록 | 차단 | 체결 | 승 | 패 | 평균PnL | 체결승률 |
|---|---|---|---|---|---|---|---|
| 2026-03-02 | 7 | 3 | 4 | 0 | 4 | -0.470% | 0% |
| 2026-03-03 | 56 | 42 | 14 | 0 | 14 | -0.470% | 0% |
| 2026-03-04 | 34 | 26 | 8 | 0 | 8 | -1.039% | 0% |
| 2026-03-05 | 56 | 38 | 18 | 3 | 12 | -0.631% | 17% |
| 2026-03-06 | 31 | 29 | 2 | 0 | 2 | -0.243% | 0% |
| **합계** | **184** | **138** | **46** | **3** | **40** | **-0.622%** | **6.5%** |

#### 전략별 성과 (보고서 Section 3-2)

| 전략 | 총 기록 | 체결 | 승 | 평균PnL(체결) | 최악 | 최우수 |
|---|---|---|---|---|---|---|
| D5 | 34 | 1 | 0 | 0.000% | 0% | 0% |
| **D6** | 34 | 13 | **2** | -0.433% | -1.879% | +0.424% |
| S1 | 16 | 5 | 0 | -0.470% | -0.47% | -0.47% |
| D2 | 16 | 6 | 0 | -0.470% | -0.47% | -0.47% |
| D7 | 34 | 7 | 0 | -0.691% | -1.801% | -0.015% |
| **D-ORB** | 34 | 12 | **1** | -0.801% | **-3.612%** | +0.199% |
| D4 | 16 | 4 | 0 | -1.021% | -2.673% | -0.470% |

#### 청산 유형별 (보고서 Section 3-3)

| 청산 유형 | 건수 | 비중 | 평균PnL | 승리 |
|---|---|---|---|---|
| **FORCED_CLOSE_EOD** | **28** | **60.9%** | **-0.454%** | **0** |
| TIMEOUT(60min) | 13 | 28.3% | -0.740% | 3 |
| TIMEOUT_NO_PRICE | 3 | 6.5% | 0.000% | 0 |
| SL_HIT | 2 | 4.3% | **-3.143%** | 0 |

#### 세션별 성과 (보고서 Section 3-4)

| 세션 | 총 기록 | 체결 | 승 | 체결 평균PnL |
|---|---|---|---|---|
| **PM** | 40 | 9 | **3** | **-0.213%** |
| NIGHT | 24 | 1 | 0 | -0.015% |
| KIS_MOCK | 112 | 33 | 0 | -0.809% |
| AM | 8 | 3 | 0 | 0.000% |

#### 승리 거래 3건 상세 (보고서 Section 3-6)

| ID | 날짜 | 티커 | 전략 | PnL | 청산사유 | 세션 |
|---|---|---|---|---|---|---|
| 134 | 03-05 | 0005G0 | D6 | **+0.424%** | TIMEOUT@17:14 | PM |
| 138 | 03-05 | 0005G0 | D6 | **+0.372%** | TIMEOUT@17:30 | PM |
| 118 | 03-05 | 0005G0 | D-ORB | **+0.199%** | TIMEOUT@16:46 | PM |

**공통 패턴**: 동일 종목(0005G0) + PM 세션 + TIMEOUT 청산

### 3-2. 조정안 제시 여부 확인 (보고서 Section 5)

**✅ 조정안 4개 제시 확인됨**:

- **(a) ATR 기반 동적 SL**: D-ORB SL 4.0%→1.8%, D4 SL 3.0%→1.5%
- **(b) TP 단계 축소**: D6/D-ORB TP 3.0%→1.0%
- **(c) TIMEOUT 연장 + 진입 시간 게이트**: 60분→90분, 14:00 이전 진입 제한
- **(d) KIS_MOCK 소스 D6 전용 허용**: 세션/소스별 전략 차등화

### 3-3. project-docs git 상태 확인

```bash
cd /root/project-docs && git log --oneline -10
```

**결과**:
```
0986343 [DONE] AADS_20260306_200759_BRIDGE_RESULT.md — 자동 완료 보고서
dee92ad [DONE] KIS_20260306_200148_BRIDGE_RESULT.md — 자동 완료 보고서
f57da71 docs: HANDOVER 업데이트 (T-187 완료) v10.22
c5504e6 docs: T-187 CUR-V41-MOCK-TRADE-DIAGNOSIS-001 업데이트 (184건 전수 분석 + T-163 검증)
e0b9d6a [DONE] KIS_20260306_200146_BRIDGE_RESULT.md — 자동 완료 보고서
8cd57bd [DONE] KIS_20260306_195929_BRIDGE_RESULT.md — 자동 완료 보고서
...
```

**판단**: 보고서는 push됨(c5504e6), HANDOVER도 업데이트됨(f57da71)
**단, exit_manager.py 코드 변경은 미반영** → 지시서 "미반영 조치 즉시 적용" 해당

---

## 4. 조정안 코드 적용 (미반영 조치 즉시 적용)

### 4-1. exit_manager.py 수정

**파일**: /root/kis-autotrade-v4/backend/app/services/unified_engine/core/exit_manager.py

**변경 전**:
```python
"D4":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},  # T-163: SL 2%→3%
"D5":  {"sl_pct": 0.025, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
"S1":  {"sl_pct": 0.030, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": None},
"D6":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
"D7":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
"D-ORB": {"sl_pct": 0.040, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},  # T-163: SL 2.5%→4.0%
```

**변경 후**:
```python
"D4":  {"sl_pct": 0.015, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},  # T-187: SL 3%→1.5% (ATR기반, 원래: 0.020; T-163: 0.030)
"D5":  {"sl_pct": 0.025, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
"S1":  {"sl_pct": 0.030, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": None},
"D6":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.010, "timeout_min": 90},  # T-187: TP 3%→1%, TIMEOUT 60→90min
"D7":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
"D-ORB": {"sl_pct": 0.018, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.010, "timeout_min": 90},  # T-187: SL 4%→1.8%(ATR기반), TP 3%→1%, TIMEOUT 60→90min
```

### 4-2. 변경 내역 요약

| 전략 | 파라미터 | 변경 전 | 변경 후 | 근거 |
|---|---|---|---|---|
| D-ORB | sl_pct | 0.040 (4%) | **0.018 (1.8%)** | T-187 조정안(a): ATR 기반 SL 축소 |
| D-ORB | tp_pct | 0.030 (3%) | **0.010 (1%)** | T-187 조정안(b): TP 하향 (수수료 극복 수준) |
| D-ORB | timeout_min | 60 | **90** | T-187 조정안(c): TIMEOUT 연장 |
| D4 | sl_pct | 0.030 (3%) | **0.015 (1.5%)** | T-187 조정안(a): ATR 기반 SL 축소 |
| D6 | tp_pct | 0.030 (3%) | **0.010 (1%)** | T-187 조정안(b): TP 하향 |
| D6 | timeout_min | 60 | **90** | T-187 조정안(c): TIMEOUT 연장 |

### 4-3. 커밋

```bash
git add backend/app/services/unified_engine/core/exit_manager.py
git commit -m "[V4.1] fix: T-187 진단 기반 SL/TP/timeout 조정 적용 (exit_manager.py)

- D-ORB: SL 4.0%→1.8%(ATR기반), TP 3%→1%, TIMEOUT 60→90min
- D4:    SL 3.0%→1.5%(ATR기반), TP/TIMEOUT 유지
- D6:    TP 3%→1%, TIMEOUT 60→90min

T-187 전수 분석 결과 (184건, 승률 1.63%):
  - FORCED_CLOSE_EOD 28건(61%) 수수료만 손실 → TIMEOUT 90min으로 완충
  - SL 2건 avg -3.14% 최대 손실 → ATR기반 SL 축소
  - TP 3% 달성 0건 → 1%로 하향하여 수익 확보 가능성 향상

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

**결과**:
```
[phase-2c-command-center 854466b8] [V4.1] fix: T-187 진단 기반 SL/TP/timeout 조정 적용 (exit_manager.py)
 1 file changed, 3 insertions(+), 3 deletions(-)
```

---

## 5. HANDOVER.md 업데이트

### 5-1. 변경 내용

- 헤더 버전: v10.20 → v10.23 (T-187 BRIDGE 코드 적용 완료)
- T-187 완료 행에 커밋 해시 854466b8 추가 및 BRIDGE 코드 적용 내용 반영

### 5-2. 커밋 및 push

```bash
sudo /usr/bin/git -C /root/project-docs add kis-autotrade-v4/HANDOVER.md
sudo /usr/bin/git -C /root/project-docs commit -m "docs: HANDOVER 업데이트 (T-187 BRIDGE 코드 적용 완료) v10.23"
sudo /usr/bin/git -C /root/project-docs push origin master
```

**결과**:
```
[master fb840be] docs: HANDOVER 업데이트 (T-187 BRIDGE 코드 적용 완료) v10.23
 1 file changed, 2 insertions(+), 2 deletions(-)
To github.com:moongoby/project-docs.git
   8b4156b..fb840be  master -> master
```

---

## 6. GitHub URL 확인

```bash
curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md"
curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-MOCK-TRADE-DIAGNOSIS-001-20260306.md"
```

**결과**: `200` / `200` → **모두 정상 확인**

---

## 7. 추가 개선사항 (T-187 보고서 Section 6 기존 식별 사항)

| 사항 | 상태 | 비고 |
|---|---|---|
| FunnelScore 코드 0.40 잔존 제거 | 미적용 | cte_pipeline.py L490-492 수정 필요 (별도 태스크) |
| D5 전략 비활성 검토 | 미적용 | 34기록/1건 체결/PnL=0%, 전략 조건 재검토 필요 |
| 3/6 체결 극단 감소 원인 조사 | 미적용 | 31건 기록/29건 차단, FunnelScore 0.35/0.40 혼용 |
| KIS_MOCK 소스 D6 전용 허용 (조정안 d) | 미적용 | cte_pipeline.py 소스별 전략 매핑 필요 (복잡) |
| TIMEOUT 90min + 14:00 진입 게이트 | 부분 적용 | TIMEOUT 90min만 적용, 진입 게이트는 cte_pipeline.py 수정 필요 |

---

## 8. 체크포인트

- [x] 현황 확인: 기존 보고서 CUR-V41-MOCK-TRADE-DIAGNOSIS-001-20260306.md 존재 확인
- [x] 분석 결론 검증: 184건 전수 분석 완료, 조정안 4개(a~d) 확인
- [x] 미반영 조치 즉시 적용: exit_manager.py SL/TP/timeout 변경 커밋 854466b8
- [x] 코드 레포 커밋 완료: branch=phase-2c-command-center, commit=854466b8
- [x] HANDOVER.md 업데이트 완료: v10.23, commit=fb840be
- [x] project-docs push 완료: GitHub raw URL 200 확인

HANDOVER.md 업데이트 완료: fb840be
