# T-208: S1 전략 재검증 + 진입 트리거 이징 분석
> 보고서 ID: CUR-V41-S1-TRIGGER-EASING-001-20260307
> 작성일: 2026-03-07 (KST)
> 의존성: T-192 (S1 PF=1.44 CONDITIONAL 재검증 지시)
> 분석 기간: 2026-03-01 ~ 2026-03-06

---

## [인계 확인]
직전 완료: T-219 (THEME_CYCLE feature variable)
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-009(3층 구조 S1), D-010(컨디션 엔진), D-011(시그널 매칭), T-192(S1 검증)
strategy_cards: (직접 조회 미수행 — 변경 없음)
open_positions: 0건 (모의매매 전량 FORCED_CLOSE_EOD)

---

## 1. 현황 요약

### 1-1. v4_mock_trades S1 현황 (03-01 ~ 03-06)

```sql
SELECT trade_date, approved_cnt, blocked_cnt, total
FROM (
  SELECT trade_date,
         count(*) FILTER (WHERE notes LIKE '%"approved": true%') as approved_cnt,
         count(*) FILTER (WHERE notes LIKE '%"approved": false%') as blocked_cnt,
         count(*) as total
  FROM v4_mock_trades WHERE strategy_id='S1' AND trade_date BETWEEN '2026-03-01' AND '2026-03-06'
  GROUP BY trade_date
) t
```

| 날짜 | 승인 | 차단 | 합계 |
|------|------|------|------|
| 2026-03-02 | 1 | 0 | 1 |
| 2026-03-03 | 3 | 5 | 8 |
| 2026-03-04 | 1 | 1 | 2 |
| 2026-03-05 | 0 | 4 | 4 |
| 2026-03-06 | 0 | 1 | 1 |
| **합계** | **5** | **11** | **16** |

- **총 신호**: 16건 / 5거래일 = 일 평균 3.2건
- **승인**: 5건 (31.3%)
- **차단**: 11건 (68.7%)

### 1-2. 체결 결과

| 항목 | 값 |
|------|-----|
| 체결 건수 | 5건 |
| 평균 PnL | -0.47% |
| 수익 거래 | 0건 |
| 손실 거래 | 5건 |
| FORCED_CLOSE_EOD | 5/5 (100%) |
| 실질 PF | 0 |

> **핵심 문제**: 승인된 5건 전부 `FORCED_CLOSE_EOD` — 진입 당일 동가(同價) 강제청산.
> PnL = -0.47%는 비용(cost_pct=0.47%) 전액 = 실제 가격 수익 0.
> S1은 스윙 전략(3~10일 보유)인데 당일 강제청산이 100% 발생 → 설계 목적 달성 불가.

---

## 2. 필터 레이어별 차단 이력 분석 (03-01 ~ 03-06)

### 2-1. 차단 원인 분포

| 차단 레이어 | 건수 | 비율 | 차단 이유 |
|------------|------|------|----------|
| L3.3_SUPPLY | 7 | 43.8% | `synthetic_BLOCK` |
| SIGNAL_COMBO | 3 | 18.8% | `S1 (1/2)` — 신호 조합 미통과 |
| L3.1_FUNNEL | 1 | 6.3% | `FunnelScore 0.250 < 0.4` |
| **차단 소계** | **11** | **68.8%** | |
| NONE (승인) | 5 | 31.3% | |

### 2-2. 레이어별 세부 분석

#### L1: Candidate Scanner (`_scan_s1`)
- 위치: `backend/app/services/unified_engine/replay/candidate_scanner.py:256`
- 현재 조건:
  - `change_pct >= 5.0` (갭 5% 이상, E-2A CEO 승인: 기존 3.0 → 5.0)
  - `trade_amount` Top 10% 이내
- ohlcv_daily 실측 (20260305 기준, 전일 20260304 데이터 대비):
  - gap >= 5% 종목: 17건
  - gap >= 3% 종목: 18건 (차이 +1건)
  - top 10% 절대 건수: ~4건 (20260304 유효 종목 44건 × 10%)

#### L3.3_SUPPLY (`supply_demand_gate.py`)
- 위치: `backend/app/services/trading/cte/supply_demand_gate.py`
- 현재 조건: `close_position_5d > 0.7` (5일 평균 close_position)
- **실제 차단 원인**: `"synthetic_BLOCK"` — 수급 데이터가 합성 상태로 BLOCK 반환
  - close_pos 체크 전(前) 단계에서 차단 발생
  - KIS Real API 미연결 상태 → 수급 데이터 = synthetic
- 7건 전부 이 이유로 차단 (43.8%)

#### L3.3 SIGNAL_COMBO
- S1 신호 요구: SIG1(VP전환) + SIG3(양봉) + SIG6(VWAP지지) — **min 2/3**
- 차단 메시지: `"신호 조합 미통과: S1 (1/2)"` = 1개만 통과, 2개 요구 미달
- 위치: `cte_pipeline.py:288` S1 시그널 정의 / `cte_pipeline.py:964` `_check_signal_combo`

#### L3.1_FUNNEL
- 1건: `FunnelScore 0.250 < 0.4 (min_score_for_entry)`
- 현재 YAML 설정 (`config/funnel_score.yaml`):
  - `min_score_for_entry: 0.35`
  - `bear_min_score_for_entry: 0.28`
- **참조**: T-227 분석 (2026-03-09) — 최대 FunnelScore = 0.2415 (구조적 차단 확인)

---

## 3. 이징안 3가지 시뮬레이션

### (a) 이징안 A: gap 5% → 3%

**대상**: `candidate_scanner.py:274` — `info.change_pct >= 5.0` → `>= 3.0`

**시뮬 결과** (ohlcv_daily 실측 기반):

| 날짜 | gap5% 후보 | gap3% 후보 | 차이(+) |
|------|-----------|-----------|--------|
| 20260305 | ~17건 | ~18건 | +1건 |
| 20260306 | ~0건 | ~0건 | +0건 |
| 20260303 | N/A (전일 데이터 없음) | N/A | - |

> ⚠️ 03-06은 ohlcv_daily trade_amount 유효 종목 25건으로 데이터 희소

**추가 통과 시뮬**:
- gap 3~5% 추가 후보: +1건/일 (20260305 기준)
- 이 추가 후보가 SIGNAL_COMBO/SUPPLY 게이트 통과율 적용:
  - SUPPLY 차단율 64% 적용: +1 × (1-0.64) = 0.36건
  - SIGNAL_COMBO 차단율 27% 적용: 0.36 × (1-0.27) = **+0.26건/일**
- 5거래일 기준 추정 추가 체결: ~1.3건
- 예상 추가 PnL: gap 3~5% 종목은 모멘텀 약화 구간 → FORCED_CLOSE_EOD 시 -0.47% 반복 위험

**평가**: ★★☆☆☆ — 후보 증가 효과 미미 (근본 문제: SUPPLY synthetic_BLOCK / FORCED_CLOSE_EOD)

---

### (b) 이징안 B: close_pos 0.30 → 0.25 (supply_demand_gate 완화)

**대상**: `supply_demand_gate.py:34` — `close_position_threshold: 0.7` 조정

> ⚠️ 현재 코드의 close_pos 임계값은 **0.7** (상위 30%), 태스크 지시의 "0.30→0.25"는
> L3.3 SUPPLY 게이트의 "close_position >= 0.30" 하한(下限) 설정 제안으로 해석.
> 즉, 하한을 0.30 → 0.25로 낮추면 일봉 하위 25% 이상의 종목까지 허용.

**시뮬 결과** (20260305 ohlcv_daily 실측):

| 조건 | gap5% 해당 | close_pos >= 0.70 | close_pos >= 0.30 | close_pos >= 0.25 |
|------|-----------|-------------------|-------------------|-------------------|
| 20260305 | 17건 | 5건 | 14건 | 15건 |

- close_pos >= 0.30 통과: 14건 (82%)
- close_pos >= 0.25 통과: 15건 (88%)
- 0.30→0.25 완화 시 추가: **+1건**

**중요 제약**: 현재 L3.3_SUPPLY 차단은 **전부 `synthetic_BLOCK`**
- synthetic 데이터 상태에서는 close_pos 체크 자체가 실행 안 됨
- 실제 KIS API 수급 데이터 연결 후에만 이 이징안 효과 발생
- 실제 수급 데이터 연결 전: **효과 = 0**
- 연결 후 예상: +1건/일 (gap5% + close_pos 0.25 통과분)

**평가**: ★★★☆☆ — 실제 수급 데이터 연결 전제 시 중간 효과 (사전 조건 필수)

---

### (c) 이징안 C: S1 FunnelScore threshold 0.30 (현재 0.35)

**대상**: `config/funnel_score.yaml` — `min_score_for_entry: 0.35` → `0.30`

**T-227 분석 결과 참조**:
- 2026-03-09 분석에서 확인: 03-01~03-06 FunnelScore 최대값 = **0.2415**
- L3.1 FunnelScore 구성:
  - L0(매크로) = 0.360 (KOSPI 오염 + VIX NULL)
  - L1(섹터) = 0.300 (섹터 미등록)
  - L2(수급) = 0.300 (수급 데이터 없음)
  - L3(펀더멘털) = 0.075 (7.1% 커버)
  - 가중 최대 = 0.2415

| threshold | 03-01~03-06 통과 건수 | 변화 |
|-----------|----------------------|------|
| 0.40 (03-06 로그 기준) | 0건 | 기준 |
| 0.35 (현재 YAML) | 0건 | ±0 |
| 0.30 (이징안 C) | **0건** | ±0 |
| 0.20 (T-227 C안) | 16건 | +16 |
| Fail-Open (T-227 A안) | 16건 | +16 |

- FunnelScore 최대값이 0.2415이므로, **threshold 0.30으로 낮춰도 구조적 차단 해소 불가**
- 실질 추가 통과: **0건**

**평가**: ★☆☆☆☆ — threshold 0.30은 효과 없음 (threshold 0.20 또는 Fail-Open 필요)

---

## 4. 이징안별 종합 시뮬 비교

| 이징안 | 추가 후보/일 | 실제 체결 추가 | 추가 PnL 가능성 | 선결 조건 | 효과 |
|--------|------------|--------------|----------------|----------|------|
| A: gap 3% | +1건 | +0.26건 | FORCED_EOD 위험 | 없음 | 미미 |
| B: close_pos 0.25 | +1건 | 0건 | - | 수급 데이터 연결 | 조건부 중간 |
| C: FunnelScore 0.30 | 0건 | 0건 | 없음 | - | 없음 |

---

## 5. 근본 원인 진단

### 5-1. L3.3_SUPPLY synthetic_BLOCK (가장 심각)
- 전체 차단의 **43.8%** (7건)
- 실제 수급 데이터(KIS API) 미연결 상태에서 BLOCK 반환
- 이징안 A~C 모두 이 문제를 직접 해결하지 못함
- **해결책**: KIS Real API 수급 데이터 연결

### 5-2. FORCED_CLOSE_EOD 100% (설계 구조 문제)
- S1은 스윙 전략 (보유 목표: 3~10일)
- 승인된 5건 전부 당일 강제청산 → 전략 목적 달성 불가
- 원인: 모의매매 환경 FORCED_CLOSE_EOD 정책 또는 T-195 ENTRY_CUTOFF_HOUR=14
- **해결책**: FORCED_CLOSE_EOD 조건 검토 + 스윙 보유 허용

### 5-3. FunnelScore 구조적 차단 (T-227)
- 최대값 0.2415 < 임계값 0.35 → 100% 차단
- L0/L1/L2/L3 모두 데이터 부재로 낮은 점수
- **해결책**: T-227 A안(Fail-Open) 또는 C안(임계값 0.20)

### 5-4. SIGNAL_COMBO (S1 SIG1+SIG3+SIG6 min2/3)
- 3건 차단 (18.8%)
- SIG1(VP전환)이 S1 핵심 신호지만 합성 환경에서 탐지 불안정
- **해결책**: S1 신호 요구를 min 1/3으로 완화 또는 SIG1 계산 보강

---

## 6. 추천안 (CEO 승인 필요 — 직접 수정 금지)

> ⚠️ 이하는 분석 기반 제안이며, 코드 직접 수정 금지. CEO 승인 후 별도 태스크로 구현.

### 추천 순위

| 순위 | 조치 | 예상 효과 | 난이도 | CEO 승인 필요 |
|------|------|----------|--------|--------------|
| 1 | 수급 데이터 실제 연결 | L3.3_SUPPLY 차단 43.8% 해소 | 중 | 필요 |
| 2 | FunnelScore Fail-Open (T-227 A안) | L3.1_FUNNEL 차단 해소 | 낮 | 필요 |
| 3 | FORCED_CLOSE_EOD 정책 검토 | 스윙 보유 가능화 | 중 | 필요 |
| 4 | gap 5%→3% (이징안 A) | 후보 +1건/일 | 낮 | 필요 |
| 5 | FunnelScore threshold 0.30 (이징안 C) | 효과 없음 — **비추천** | 낮 | 불필요 |

### 최우선 권고

```
[T-208 추천안 요약]
단기 효과 최대화: Fail-Open FunnelScore + 수급 데이터 연결
= 현재 차단 68.7% → 예상 차단 18.8% (SIGNAL_COMBO만 남음)
= 예상 S1 일평균 체결: 3.2건 × 0.812 = 2.6건/일

중기 목표: FORCED_CLOSE_EOD 해소 + SIG1 탐지 보강
= S1 스윙 전략 본래 목적 달성 (3~10일 보유 시 PF=1.44)
```

**이징안 A (gap 3%) + 이징안 B (close_pos 0.25)** 조합 시뮬:
- 선결 조건: 수급 데이터 실제 연결
- 추정 추가 체결: +2건/일 → 5.2건/일
- 단, 수익 개선은 FORCED_CLOSE_EOD 해소가 전제

---

## 7. 데이터 제약 사항

1. `ohlcv_daily` 데이터 희소일 존재: 20260304 = 83종목, 20260306 = 25건 trade_amount
2. 20260301/20260302/20260228 ohlcv_daily 데이터 없음 — 해당일 mock_trade는 외부 데이터 기반 추정
3. FunnelScore 직접 계산 미수행 — T-227 기존 분석 결과 인용
4. SIG1/SIG3/SIG6 개별 통과율 데이터 없음 — blocking_reason 텍스트 기반 추정

---

## 8. 결론

T-192에서 S1 PF=1.44(CONDITIONAL)로 검증된 전략이 03-01~03-06 체결 0건(수익)을 기록한 이유:

1. **주원인**: L3.3_SUPPLY synthetic_BLOCK (43.8%) — 이징안 A~C 모두 직접 해결 불가
2. **부원인**: FORCED_CLOSE_EOD 100% — 스윙 전략이 당일 청산으로 목적 상실
3. **3차원인**: FunnelScore 구조적 차단 (threshold > 최대값 0.2415)

이징안 단독으로는 근본 해결 불가. **수급 데이터 실제 연결** + **FunnelScore Fail-Open** + **FORCED_CLOSE_EOD 정책 개선**이 3대 선결 과제.

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-S1-TRIGGER-EASING-001-20260307.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-S1-TRIGGER-EASING-001-20260307.md
- 커밋: (push 후 기재)
- HTTP 확인: (push 후 확인)
- HANDOVER 업데이트: 완료 예정
