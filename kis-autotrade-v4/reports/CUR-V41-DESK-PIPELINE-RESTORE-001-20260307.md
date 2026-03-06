# CUR-V41-DESK-PIPELINE-RESTORE-001-20260307

## T-202: DESK5→4→3 파이프라인 복원 — 프랙탈 트리거 연결 우선순위 분석

**작성일**: 2026-03-07 (KST 작업 완료)
**태스크**: T-202
**우선순위**: P0-HIGH
**선행**: T-200, T-192
**담당**: Claude Code (claudebot)

---

## [인계 확인]
직전 완료: T-192 (DESK별 전략 성과 주간 리뷰)
현재 단계: Phase 2c-command-center
CEO 지시 적용: D-001, D-002, D-012, D-013, D-014
strategy_cards: 60
open_positions: 0 (DESK4/5 포지션 전무)

---

## 1. 작업 개요

### 배경
T-192 주간 리뷰에서 확인된 주요 문제:
- DESK5 20종목 전부 WATCHING (트리거 0건)
- DESK4 11종목 전부 WATCHING (트리거 0건)
- DESK3→DESK2 승격 파이프라인 0건

D-012(프랙탈 추세추종 아키텍처 v3.0) 기준으로 DESK5 T5-1~T5-3 중 2개 충족 시 매수 신호, DESK4 T4-1~T4-4 중 2개 충족 시 추매/신규 진입이 발생해야 하나 현재 전원 미발동.

### 분석 범위
1. `scripts/desk5/desk5_seed_scanner.py` — DESK5 트리거 (seed 스캔)
2. `backend/app/services/desk_filters/fractal_triggers.py` — T5-1~T5-3, T4-1~T4-4 정의
3. `backend/app/services/fractal_live_connector.py` — 실전 연결
4. `backend/app/services/desk_filters/node_detector_desk4.py` — DESK4 감지
5. `backend/app/services/strategy/desk2_pool_link.py` — DESK3→DESK2 승격
6. `backend/app/services/node_detector_engine.py` — 크론 실행 엔진
7. DB: `v4_desk5_watchlist`, `v4_desk4_watchlist`, `v4_desk3_pool`, `v4_desk2_candidates`, `v4_node_realtime`, `v4_desk_positions`

---

## 2. DB 현재 상태 (2026-03-06 기준)

| 항목 | 현재값 | 비고 |
|------|--------|------|
| v4_desk5_watchlist WATCHING | 20종목 | triggers_met=0, 모든 트리거 false |
| v4_desk4_watchlist WATCHING | 11종목 | current_phase=NULL |
| v4_desk3_pool ACTIVE | 401종목 | 정상 |
| v4_desk_positions DESK5 OPEN | 0건 | 미진입 |
| v4_desk_positions DESK4 OPEN | 0건 | 미진입 |
| v4_node_realtime desk_level=4 | 0행 | 테이블 미적재 |
| v4_node_realtime desk_level=5 | 0행 | 테이블 미적재 |
| v4_desk2_candidates 2026-03-06 | 10건 | DESK3 boost 없음 |

### DESK5 트리거 상세 (20종목 전수)
```
status   | count | t5_1_pass | t5_2_pass | t5_3_pass | triggers_met_2plus
---------+-------+-----------+-----------+-----------+--------------------
WATCHING |    20 |         0 |         0 |         0 |                  0
```
→ **20종목 모두 T5-1=false, T5-2=false, T5-3=false**

---

## 3. 파이프라인 흐름 분석

### 3.1 현재 파이프라인 아키텍처 (2개 계층 분리 구조)

```
[계층 A] 시드 스캔 (scripts/ → v4_desk5/4_watchlist)
  desk5_seed_scanner.py  → v4_desk5_watchlist (T5-1/2/3 자체 정의)
  desk4_node_scanner.py  → v4_desk4_watchlist (T4-1~4 자체 정의)

[계층 B] 노드 감지 (cron → v4_node_realtime)
  node_detector_engine.py [cron 07:00/07:05/07:10 UTC]
    → node_detector_desk5.py (v4_node_realtime 읽기/쓰기)
    → node_detector_desk4.py (v4_node_realtime 읽기/쓰기)

[계층 C] 실전 연결 (DeskPipeline → fractal_live_connector)
  fractal_live_connector.py
    → fractal_triggers.py (T5-1~3, T4-1~4, T3-1~5)

[계층 D] DESK2 승격 (desk2_pool_link.py)
  apply_desk345_confidence_boost()
    → v4_desk3_pool ACTIVE → v4_desk2_candidates boost
```

**문제: 각 계층이 독립적으로 작동하며 연결고리 부재**

---

## 4. 단절 지점 식별 (4개)

### 🔴 단절점 1: DESK5 크론 ModuleNotFoundError (P0-CRITICAL)

**위치**: `/etc/cron.d/kis-v41-desk` (claudebot crontab)
**크론 설정**:
```
0 7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk5 >> /root/kis-autotrade-v4/logs/node_desk5.log 2>&1
```

**로그 실제 오류**:
```
/root/kis-autotrade-v4/venv/bin/python3: Error while finding module specification for
'backend.app.services.node_detector_engine'
(ModuleNotFoundError: No module named 'backend')
```

**원인**: 크론이 `cd /root/kis-autotrade-v4 &&` 없이 실행 → working directory가 프로젝트 루트 아님 → `backend` 패키지 찾기 실패
**결과**: DESK5 node_detector가 **매일 실패** → `v4_node_realtime`에 DESK5 데이터 적재 없음

---

### 🔴 단절점 2: T5-2 조건 논리 모순 (P0-HIGH)

**위치**: `scripts/desk5/desk5_seed_scanner.py:251~253`
```python
_t5_2_box_days = int(_P5.get("t5_2_box_days", 120))
bars_120 = bars[-_t5_2_box_days:] if len(bars) >= _t5_2_box_days else bars
box_high_120 = max(float(b["high"] or 0) for b in bars_120[:-1]) if len(bars_120) > 1 else 0
t5_2 = (box_high_120 > 0 and close_d1 >= box_high_120)  # 120일 최고가 초과 필요
```

**원인**: T5-2가 `현재가 >= 120일 최고가` 조건인데, DESK5 편입 조건인 **바닥탈출** (`52주저가 +20%`)과 구조적으로 모순.
- 바닥탈출 종목 = 52주 저점에서 반등 중인 종목
- 52주 저점에서 반등 중인 종목이 120일 최고가를 초과할 가능성 = 거의 0

**D-012 fractal_triggers.py의 원래 T5-2 정의**:
```python
def check_t5_2(bars):  # 역배열→정배열 전환
    # 현재봉: MA5 > MA20 > MA60 (정배열)
    # 직전봉: 비정배열
    passed = current_golden and prev_not_golden
```
→ seed_scanner와 fractal_triggers.py의 T5-2 **정의가 완전히 다름**

---

### 🔴 단절점 3: DESK4 데이터 소스 불일치 (P0-HIGH)

**위치**: `node_detector_desk4.py:load_watchlist()`
```python
def load_watchlist(self) -> List[str]:
    cur.execute(
        "SELECT DISTINCT stock_code FROM v4_node_realtime WHERE desk_level = 4"
    )
```

**DB 확인**:
- `v4_node_realtime WHERE desk_level=4` → **0행** (테이블 미적재)
- `v4_desk4_watchlist WHERE status='WATCHING'` → **11종목** (정상)

**원인**: `node_detector_desk4.py`가 `v4_node_realtime`(비어있음)을 읽지만, 실제 DESK4 종목은 `v4_desk4_watchlist`에 있음. 두 테이블 간 동기화 미구현.

**실제 실행 결과** (`logs/node_desk4.log`):
```
DESK4: {'processed': 0, 'starting_signals': 0, 'promote_signals': 0, 'errors': 0}
```
→ stock_codes = [] → 처리 종목 0건

---

### 🟡 단절점 4: desk2_pool_link 크론/엔진 미연결 (P1)

**위치**: `backend/app/services/strategy/desk2_pool_link.py`
**함수**: `apply_desk345_confidence_boost()` — 정상 구현, 로직 올바름

**grep 결과**:
```bash
grep -rn "apply_desk345_confidence_boost|desk2_pool_link" backend/
→ desk2_pool_link.py 내부 정의만 있음 (호출자 없음)
```

**원인**: 함수가 구현됐지만 어디서도 호출되지 않음:
- `run_unified_engine.py` → 호출 없음
- crontab → 등록 없음
- `pipeline.py` → 호출 없음

**결과**: DESK3 ACTIVE 401종목이 DESK2 후보군에 전혀 반영되지 않음

---

### 🟡 추가 문제: T4-4 섹터 반등 데이터 미전달

**위치**: `fractal_live_connector.py:139-140`
```python
t4_4 = self._ft.check_t4_4(symbol, sector_rebounds or {})
```
`evaluate_desk4_entry()`의 파라미터 기본값: `sector_rebounds: Optional[Dict[str, List[str]]] = None`

**문제**: `sector_rebounds`가 항상 `None` → `{}` → T4-4 항상 False
T4-4는 섹터 반등 데이터를 외부에서 제공해야 하는데, 호출 시 데이터 미제공

---

## 5. DESK5 T5-1~T5-3 조건 충족율 심층 분석

### 현재 DESK5 20종목 트리거 분석 (03-06 데이터 기준)

```
stock_code | total_score | T5-1 | T5-2 | T5-3 | theme_alive_flag
383220(F&F)|    0.6750   |  F   |  F   |  F   | ALIVE
028300(HLB)|    0.6700   |  F   |  F   |  F   | ALIVE
008730(율촌화학)| 0.6700  |  F   |  F   |  F   | ALIVE
... (20종목 전부 동일)
```

### T5-1 미충족 원인 (주봉MA20 돌파 + 거래량 2배)
```python
t5_1 = (w_close > w_ma20        # 이번 주 MA20 돌파
        AND w_prev_close <= w_prev_ma20   # 직전 주 MA20 이하
        AND w_vol_d1 >= w_avg_vol * 2.0)  # 이번 주 거래량 2배
```
**원인**: 3개 동시 충족 조건으로 매우 엄격
- 2월 말~3월 시장: BEAR 레짐 하에서 주봉MA20 신규 돌파 희소
- F&F(383220): 62,800원 (전주 대비 하락, MA20 하방)
- 2배 거래량 동반 신규 돌파 = 사실상 상승 돌파 이벤트 필요

### T5-2 미충족 원인 (120일 박스 상단 돌파)
```
바닥탈출 조건: 52주저가 × 1.20 이상 = 반등 시작 단계
120일 고점 돌파: 120일 최고가 초과 = 상승 돌파 단계
→ 이 두 조건의 동시 충족은 구조적으로 드문 경우
```

### T5-3 미충족 원인 (4 이평 정배열 MA5>MA10>MA20>MA60)
```python
aligned = ma5 and ma10 and ma20 and ma60 and (ma5 >= ma10 >= ma20 >= ma60)
t5_3 = ind.get("t5_3_aligned", False)
```
**원인**: 4개 이평선 완전 정배열은 상승 추세 후반부 신호, 바닥권 종목에 적용하면 진입 타이밍이 대폭 늦어짐

---

## 6. DESK4 T4-1~T4-4 조건 분석

`fractal_triggers.py` 기준:

### T4-1 (MA20 터치 + 양봉)
```python
ma20_touch = cur_low <= ma20 <= cur_high  # 저가 ≤ MA20 ≤ 고가
bullish = cur_close > cur_open             # 종가 > 시가
```
**분석**: 조건 자체는 적절. 단 `v4_node_realtime`이 비어서 처리 대상 종목 자체가 없음

### T4-2 (1파 고점 -15%~-25% 조정 + 거래량 감소)
```python
in_range = 0.15 <= correction_ratio <= 0.25  # 15~25% 조정
vol_decreasing = vol_ma5 < vol_ma20 * 0.8    # 거래량 80% 미만
```
**분석**: 조정 범위 15~25%는 합리적이나, 실제 시장에서 급락 시 -25% 초과하는 경우 많음

### T4-3 (MA5 지지 + VP ≥ 120)
```python
vp_ok = True  # VP 데이터 없으면 조건 완화
```
**분석**: VP 없으면 자동 통과 → 단독으로는 의미 축소

### T4-4 (동일 섹터 2종목 동반 반등)
```python
t4_4 = self._ft.check_t4_4(symbol, sector_rebounds or {})
# sector_rebounds가 항상 {} → others = [] → count=0 → FAIL
```
**분석**: 데이터 미전달로 항상 False → T4-4 사실상 비활성

---

## 7. DESK3→DESK2 파이프라인 분석

### desk2_pool_link.py 동작 구조 (정상 구현)
```python
def apply_desk345_confidence_boost():
    desk3 = _get_desk3_active(cur)  # v4_desk3_pool status='ACTIVE' → 401종목
    desk4 = _get_desk4_open(cur)    # v4_desk_positions desk_level=4 ACTIVE/PARTIAL → 0건
    desk5 = _get_desk5_open(cur)    # v4_desk_positions desk_level=5 ACTIVE/PARTIAL → 0건

    boost_map: {code: (name, boost)}
    # DESK3 boost = +0.5, DESK4 boost = +0.8, DESK5 boost = +1.0

    # v4_desk2_candidates에 boost 반영 (INSERT or UPDATE)
```

**문제 원인**:
1. 함수 자체는 정상. 하지만 **어디서도 호출되지 않음**
2. `v4_desk_positions`에 DESK4/5 OPEN 포지션 0건 → boost 소스 제한적
3. 크론 등록 없음, `run_unified_engine.py` 내 호출 없음

**현재 desk2_candidates 2026-03-06**:
```
10건 (regular CTE scoring만 반영, DESK3 boost 미적용)
```

---

## 8. 완화안 3개 (코드 수정은 CEO 승인 후)

### 완화안 A: T5-2 조건 교체 — 바닥탈출과 일관성 확보 (P0 권고)

**현재 (seed_scanner T5-2)**:
```python
# 120일 박스상단 돌파 (바닥 종목과 모순)
t5_2 = (close_d1 >= box_high_120)
```

**제안 (fractal_triggers.py의 T5-2 정의로 교체)**:
```python
# 역배열→정배열 전환 (MA5>MA20>MA60, 직전봉은 비정배열)
# 또는 MA60 기울기 상향 + 거래량 1.5배 (현재 2배 → 1.5배로 완화)
t5_2 = (ma60_slope_up and vol_1_5x_ma20)  # 20% 완화
```

**효과**: T5-2 충족 가능 종목 예상 증가율: 현재 0% → 15~20%로 향상

---

### 완화안 B: T5-1 거래량 임계값 완화 + T5-3 정배열 조건 완화 (P1 권고)

**T5-1 완화**:
```python
# 현재: w_vol_d1 >= w_avg_vol * 2.0  (2배)
# 완화: w_vol_d1 >= w_avg_vol * 1.6  (1.6배, 20% 완화)
_t5_1_vol_relaxed = float(_P5.get("t5_1_vol_multiplier", 2.0)) * 0.80
```

**T5-3 완화** (MA5>MA10>MA20>MA60 → MA5>MA20 AND MA20>MA60으로 완화):
```python
# 현재: ma5 >= ma10 >= ma20 >= ma60 (4개 이평 정배열)
# 완화: ma5 >= ma20 AND ma20 >= ma60 (핵심 2개 이평만 확인)
t5_3_relaxed = (ma5 is not None and ma20 is not None and ma60 is not None
                and ma5 >= ma20 >= ma60)
```

**효과**: T5-1+T5-3 동시 충족 가능 종목 비율: 현재 0% → 추정 10~15%

---

### 완화안 C: T4-2 조정 범위 확대 (P1 권고)

**T4-2 완화**:
```python
# 현재: 0.15 <= correction_ratio <= 0.25  (-15% ~ -25%)
# 완화: 0.10 <= correction_ratio <= 0.30  (-10% ~ -30%, 범위 20% 확대)
in_range = 0.10 <= correction_ratio <= 0.30
```

**추가 T4-1 완화** (MA20 터치 기준 확장):
```python
# 현재: cur_low <= ma20 <= cur_high (정확한 캔들 내 터치)
# 완화: cur_close >= ma20 * 0.97 (MA20 3% 이내 접근도 포함)
ma20_touch_relaxed = cur_close >= ma20 * 0.97
```

**효과**: T4 조건 충족 종목: 현재 0% → 추정 8~12%

---

## 9. 파이프라인 복원 우선순위 액션 목록

### P0-IMMEDIATE (코드/설정 수정, CEO 승인 불필요한 버그 수정)

| 번호 | 액션 | 파일 | 예상 효과 |
|------|------|------|-----------|
| FIX-001 | DESK5 크론에 `cd /root/kis-autotrade-v4 &&` 추가 | crontab | ModuleNotFoundError 해소, DESK5 노드 감지 정상화 |
| FIX-002 | node_detector_desk4.py load_watchlist 소스 변경: v4_node_realtime → v4_desk4_watchlist | node_detector_desk4.py | DESK4 11종목 처리 시작 |

### P1-CEO 승인 필요 (트리거 조건 변경)

| 번호 | 액션 | 완화안 | 기대 효과 |
|------|------|--------|-----------|
| REL-001 | T5-2 조건: 120일 박스 돌파 → MA60 기울기 상향 + 거래량 1.5배 | 완화안 A | T5-2 미발동 해소 |
| REL-002 | T5-1 거래량: 2.0배 → 1.6배 완화 | 완화안 B | T5-1 충족 범위 확대 |
| REL-003 | T5-3 정배열: 4개 이평 → 2개 이평(MA5>MA20>MA60) | 완화안 B | T5-3 충족 종목 증가 |
| REL-004 | T4-2 조정 범위: -15~25% → -10~30% | 완화안 C | T4-2 충족 범위 확대 |

### P1-PIPELINE 연결 (크론 등록, CEO 승인 불필요)

| 번호 | 액션 | 방법 | 기대 효과 |
|------|------|------|-----------|
| PIPE-001 | desk2_pool_link 크론 등록: 08:51 KST, 장전 DESK3→DESK2 boost | crontab 추가 | DESK3 401종목 DESK2 후보군 반영 시작 |
| PIPE-002 | sector_rebounds 데이터 T4-4에 주입 | fractal_live_connector 호출부 수정 | T4-4 실질 평가 활성화 |

---

## 10. 분석 스크립트 실행 결과 (03-06 데이터)

### DESK5 20종목 트리거별 통과율
```
T5-1 (주봉MA20돌파+거래량2배): 0/20 = 0%
T5-2 (120일박스상단돌파):      0/20 = 0%  ← 바닥탈출 종목에 모순 조건
T5-3 (4이평정배열):            0/20 = 0%  ← 바닥권 종목에 후행 지표
triggers_met >= 2:             0/20 = 0%
```

### DESK4 11종목 처리율
```
node_detector_desk4 처리: 0/11 = 0%  ← v4_node_realtime 미적재
```

### DESK3→DESK2 승격
```
desk2_pool_link 호출: 0회  ← 크론/엔진 미연결
DESK3 ACTIVE 401종목 desk2_candidates 반영: 0건
```

---

## 11. 핵심 발견 요약

| 순위 | 단절점 | 파일 | 심각도 |
|------|--------|------|--------|
| 1 | DESK5 크론 ModuleNotFoundError (cd 없음) | crontab:0 7 * * 1-5 | 🔴 CRITICAL |
| 2 | T5-2 조건이 바닥탈출 조건과 논리적 모순 | desk5_seed_scanner.py:251-253 | 🔴 CRITICAL |
| 3 | DESK4 node_detector가 빈 테이블(v4_node_realtime) 읽음 | node_detector_desk4.py:175-183 | 🔴 HIGH |
| 4 | desk2_pool_link 크론/엔진 미연결 | 크론 미등록 | 🟡 MEDIUM |
| 5 | T4-4 sector_rebounds 데이터 미전달 | fractal_live_connector.py:139 | 🟡 MEDIUM |
| 6 | v4_desk_positions DESK4/5 OPEN 포지션 0건 | DB 상태 | ℹ️ INFO (FIX-001/002 선행 필요) |

---

## 12. diff 포함 수정안 (CEO 승인 대기)

### diff-001: DESK5 크론 수정 (버그 수정, 즉시 적용 가능)
```diff
- 0 7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk5 >> /root/kis-autotrade-v4/logs/node_desk5.log 2>&1
+ 0 7 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk5 >> /root/kis-autotrade-v4/logs/node_desk5.log 2>&1
```

### diff-002: node_detector_desk4.py load_watchlist 소스 변경
```diff
# node_detector_desk4.py:175
def load_watchlist(self) -> List[str]:
    try:
        conn = _db_connect()
        cur = conn.cursor()
-       cur.execute(
-           "SELECT DISTINCT stock_code FROM v4_node_realtime WHERE desk_level = 4"
-       )
+       cur.execute(
+           "SELECT DISTINCT stock_code FROM v4_desk4_watchlist WHERE status = 'WATCHING'"
+       )
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]
```

### diff-003: desk5_seed_scanner.py T5-2 조건 교체 (CEO 승인 후)
```diff
# scripts/desk5/desk5_seed_scanner.py:249-253
- # ── T5-2: N일박스상단돌파 ──
- _t5_2_box_days = int(_P5.get("t5_2_box_days", 120))
- bars_120 = bars[-_t5_2_box_days:] if len(bars) >= _t5_2_box_days else bars
- box_high_120 = max(float(b["high"] or 0) for b in bars_120[:-1]) if len(bars_120) > 1 else 0
- t5_2 = (box_high_120 > 0 and close_d1 >= box_high_120)
+ # ── T5-2: MA60 기울기 상향 + 거래량 1.5배 (fractal_triggers.py T5-1 정의 기반 완화) ──
+ _t5_2_vol_mult = float(_P5.get("t5_2_vol_multiplier", 1.5))
+ ma60_d1_val = _ma(closes, 60)
+ ma60_d6 = _ma(closes[:-5], 60) if len(closes) >= 65 else None
+ ma60_slope_up_flag = (ma60_d1_val and ma60_d6 and ma60_d1_val > ma60_d6)
+ vol_ma20_prev = _ma(volumes[:-1], 20) if len(volumes) >= 21 else None
+ t5_2 = (ma60_slope_up_flag and vol_ma20_prev and
+          volumes[-1] >= vol_ma20_prev * _t5_2_vol_mult)
```

### diff-004: desk2_pool_link 크론 등록 (즉시 적용 가능)
```
# 추가할 크론 (08:51 KST = 23:51 UTC 전날)
51 23 * * 0-4 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -c "
from backend.app.services.strategy.desk2_pool_link import apply_desk345_confidence_boost
r = apply_desk345_confidence_boost(); print(r)
" >> /root/kis-autotrade-v4/logs/desk2_pool_link.log 2>&1
```

---

## 13. 성공 기준 검증

| 기준 | 현재 상태 | 분석 완료 |
|------|-----------|-----------|
| 미발동 원인 규명 | DESK5: T5-2 논리 모순 + 크론 오류 / DESK4: 데이터 소스 불일치 | ✅ |
| 완화안 3개 이상 제시 | 완화안 A/B/C (T5-2 교체, T5-1 완화, T4-2 범위 확대) | ✅ |
| 파이프라인 단절 지점 식별 | 4개 단절점 + diff 포함 | ✅ |
| 코드 수정 CEO 승인 대기 | diff-001/002(즉시), diff-003(승인필요) | ✅ |

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK-PIPELINE-RESTORE-001-20260307.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DESK-PIPELINE-RESTORE-001-20260307.md
- 커밋: (push 후 기재)
- HTTP 확인: (push 후 기재)
- HANDOVER 업데이트: 완료
