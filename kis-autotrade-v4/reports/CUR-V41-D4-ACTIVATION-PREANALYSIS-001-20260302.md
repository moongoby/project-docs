# CUR-V41-D4-ACTIVATION-PREANALYSIS-001-20260302

**작성일**: 2026-03-02  
**작성자**: Cursor (KIS-V41 Session N)  
**목적**: D4 전략 활성화 사전 분석 — CEO 승인 대기 중 선제 준비  
**상태**: 분석 완료, CEO 승인 + ATR 1.5 적용 후 구현 예정

---

## 1. 배경

ATR_NETRR 1.5 완화 후에도 D4는 여전히 0건 실행됨.  
2가지 구조적 문제 발견:
1. **EQS 분류 오류**: D4가 `PULLBACK`으로 분류되어 있으나 실제로는 `BREAKOUT` 전략
2. **SIGNAL_COMBO 불일치**: SIG5(VP_120_RECOVERY)가 전상종목 특성상 구조적으로 미충족

---

## 2. 버그 #1 — D4 EQS PULLBACK 오분류

### 발견 위치
```
backend/app/services/unified_engine/core/signal_generator.py:354
is_pullback_strategy=strategy_id in ("D2", "D4", "S1")
```

### 문제 분석
- D4 대상: **전일 상한가(+29~32%) 종목** → 당일 고가 포지션(price_position ~0.7~0.9)
- PULLBACK EQS 기준: price_position ≤ 0.30 = 20점 (최적), ≤ 0.50 = 15점 (양호)
- D4 실제 price_position ~0.75~0.90 → PULLBACK 기준 5점 (최저)

### 점수 비교 (price_position=0.80 기준)

| 분류 | price_pos 점수 | EQS 총점 | 게이트 |
|------|--------------|---------|--------|
| PULLBACK (현재) | 5 | 53~60 | REDUCE |
| BREAKOUT (올바른) | 20 | 68~75 | PROCEED |

### price_position 범위별 영향

| price_position | PULLBACK 총점 | PULLBACK 게이트 | BREAKOUT 총점 | BREAKOUT 게이트 |
|----------------|-------------|----------------|-------------|----------------|
| 0.30 | 68 | PROCEED | 58 | REDUCE |
| 0.50 | 63 | REDUCE | 63 | REDUCE |
| 0.60 | 58 | REDUCE | 63 | REDUCE |
| 0.70 | 58 | REDUCE | 68 | **PROCEED** |
| 0.75 | 53 | REDUCE | 68 | **PROCEED** |
| 0.80 | 53 | REDUCE | 68 | **PROCEED** |
| 0.90 | 53 | REDUCE | 68 | **PROCEED** |

→ 전상종목 전형 구간(0.7~0.9): REDUCE → **PROCEED**로 전환

### 수정안
```python
# signal_generator.py:354
# 현재 (잘못됨)
is_pullback_strategy=strategy_id in ("D2", "D4", "S1"),

# 수정 (올바름)
is_pullback_strategy=strategy_id in ("D2", "S1"),  # D4 제거 → BREAKOUT
```

---

## 3. 버그 #2 — D4 SIGNAL_COMBO SIG5 구조적 불충족

### 현재 D4 SIGNAL_COMBO
```
D4 → SIG5(VP_120_RECOVERY) + SIG6(VWAP)  min 2/2 (둘 다 충족 필요)
```

### SIG5 조건
```
vp_current >= vp_ma * 1.2  (현재 VP ≥ 20봉 평균의 120%)
```

### 전상종목에서 SIG5 미충족 이유
- 전상종목은 전일 상한가 → **역사적 VP 평균이 이미 높음**
- 당일 시초가 진입 시점: 갭업 시초 후 장초반 **매도 압력** → VP 감소 경향
- SIG5 충족 시나리오: 거래량 2배 이상 폭발 시에만 → D4 전략 로직과 불일치

### D4에 적합한 신호

| 신호 | 의미 | D4 전상종목 충족률 |
|------|------|-----------------|
| SIG5(VP_120) | 거래량 120% 회복 | **낮음** — 구조적 미충족 |
| SIG3(양봉) | 시가 < 종가 | 중간 — 상승 시 충족 |
| SIG6(VWAP 지지) | 가격 ≥ VWAP | 높음 — 전상종목 시초가 이후 자주 충족 |
| SIG7(반전 캔들) | 하락봉 후 반전 | 중간 — 매도압력 해소 시 |

### 수정안 A (권장)
```python
# D4 SIGNAL_COMBO: SIG5 → SIG3 교체 (1개만 필요)
"D4": [
    SignalName.SIG3_YANGBONG,      # SIG5에서 SIG3으로 교체
    SignalName.SIG6_VWAP_SUPPORT,
],
# SIGNAL_MIN_COUNT = 2 (기존 유지, 2/2 → 1/2 선택 필요 시 min=1 고려)
```

### 수정안 B (완화)
```python
# D4 SIGNAL_COMBO: SIG3 추가, min을 2/3으로 완화
"D4": [
    SignalName.SIG3_YANGBONG,
    SignalName.SIG5_VP_120_RECOVERY,
    SignalName.SIG6_VWAP_SUPPORT,
],
# D4 전용 SIGNAL_MIN_COUNT = 2 (3개 중 2개)
```

---

## 4. 통합 수정 효과 예측

### 수정 전 (현재)
```
D4 차단 구조 (ATR 1.5 적용 후):
├─ SIGNAL_COMBO: 44%  ← SIG5 구조적 미충족
├─ EQS: 28%           ← PULLBACK 오분류로 점수 저하
└─ ATR_NETRR: 26%     ← ATR 1.5 적용으로 해소 예정
실행: 0건
```

### 수정 후 (예상)
```
D4 차단 구조 (ATR 1.5 + EQS 수정 + SIGNAL_COMBO 수정):
├─ SIGNAL_COMBO: ~5%  ← SIG3+SIG6 기준으로 대부분 해소
├─ EQS: ~3%           ← BREAKOUT 분류로 대부분 PROCEED
└─ ATR_NETRR: ~5%     ← ATR 1.5 적용 후 잔여
실행: ~10~20건/242일 예상
```

---

## 5. 구현 우선순위

| 순위 | 항목 | 파일 | 변경 | 성격 |
|------|------|------|------|------|
| 1 | ATR 1.5 적용 | `atr_dynamic_exit.py:42` | `NET_RR_RATIO = 2.0 → 1.5` | **CEO 승인 대기** |
| 2 | D4 EQS 오분류 수정 | `signal_generator.py:354` | `"D4"` 제거 | **버그 수정** |
| 3 | D4 SIGNAL_COMBO 수정 | `cte_pipeline.py:241-243` | SIG5 → SIG3 교체 | 파라미터 변경 |

---

## 6. 다음 세션 작업 지시

```
ATR 1.5 CEO 승인 후:
1. signal_generator.py:354 D4 제거 (BREAKOUT 분류)
2. cte_pipeline.py D4 SIGNAL_COMBO SIG5 → SIG3 교체
3. 테스트 실행: python3 -m pytest tests/ -v
4. D4 리플레이 재검증 (기대: 10~20건/242일)
5. 보고서 작성 후 push
```

---

## 7. 검증 필요 사항

- [ ] D4 BREAKOUT 분류 후 EQS 테스트 케이스 업데이트
- [ ] D4 SIG3+SIG6 SIGNAL_COMBO 백테스트 재실행
- [ ] D2/S1 PULLBACK 분류가 여전히 올바른지 확인
- [ ] 기존 137 테스트 비파괴 검증

---

*보고서 생성: Session N — CEO 승인 대기 중 선제 분석*
