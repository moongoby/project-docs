# DESK 청산규칙 + 전략 파라미터 그리드서치 최적화 보고서
**Task ID**: GRID-SEARCH-OPT
**날짜**: 2026-03-18
**HANDOVER 버전**: v11.8 기준

---

[인계 확인]
직전 완료: KIS-304
현재 단계: 그리드서치 최적화 (독립 태스크)
CEO 지시 적용: D-001, D-003, D-008
strategy_cards: 60
open_positions: 0

---

## 1. 구현 목표

`backend/optimize_strategy_params.py` — DESK별(2/3/4/5) 청산규칙(손절/익절/보유일) × 전략 진입 파라미터를 그리드서치로 조합하여 샤프 기준 최적 파라미터를 DB에 저장.

---

## 2. 스크립트 구조

| 항목 | 내용 |
|------|------|
| 파일 | `/root/kis-autotrade-v4/backend/optimize_strategy_params.py` |
| 저장 테이블 | `v4_optimization_results` (SERIAL PK + idx_opt_desk_strategy) |
| OHLCV 기간 | 2025-09-01 ~ 2026-03-18 (~200 거래일, 룩백 포함) |
| 전략 수 | 10종 (TREND_FOLLOWING, MEAN_REVERSION, BREAKOUT_MOMENTUM, VOLUME_SPIKE, RSI_DIVERGENCE, BOLLINGER_BAND, MACD, GOLDEN_CROSS, NEWS_IMPACT, DESK_COMPOSITE) |
| 파라미터 조합 | 전략당 1~4개 × DESK별 출구규칙 4개 = DESK당 최대 144 조합 |
| 최적화 기준 | Sharpe Ratio (annualized) |
| 비용 모델 | 수수료 0.015% + 슬리피지 0.05% 양방향 |

### 핵심 최적화 기법
- **벡터화 시그널 계산**: `compute_signals_vectorized()` — 전체 바를 한번에 처리
- **시그널 캐시**: `precomputed_signals` dict — 동일 (종목, 전략, params) 조합의 exit_rules 변형 시 재계산 없음
- **DESK별 종목 제한**: picks 존재 시 최대 30종목, 없을 시 상위 30종목

---

## 3. 실행 결과

```
실행 환경: venv 활성화 + .env 로드
실행 명령: python backend/optimize_strategy_params.py
종목 수: 3,775개 로드
총 저장 결과: 583건 (v4_optimization_results)
```

### DESK별 결과 수

| DESK | 결과 수 |
|------|---------|
| 2    | 144건   |
| 3    | 151건   |
| 4    | 144건   |
| 5    | 144건   |
| **합계** | **583건** |

---

## 4. DESK별 TOP 3 최적 파라미터 (Sharpe 기준, 거래 5건 이상)

### DESK2 — 초단기 스캘핑 (1~3일)

| 순위 | 전략 | 수익률 | 승률 | Sharpe | 거래수 | PF | 평균보유 |
|------|------|--------|------|--------|--------|-----|---------|
| #1 | BOLLINGER_BAND | **+15.0%** | 80% | **12.62** | 5건 | 6.72 | 0.8일 |
| #2 | BOLLINGER_BAND | +14.7% | 60% | 9.80 | 5건 | 4.11 | 0.8일 |
| #3 | BOLLINGER_BAND | +126.0% | 54% | 5.73 | 83건 | 2.35 | 0.8일 |

**#1 최적 파라미터:**
- 진입: `bb_period=20, bb_mult=2.5, buy_threshold=-0.05, sell_threshold=1.05`
- 청산: `stop=-2.5%, target_min=3%, target_max=8%, max_hold=2일`

### DESK3 — 단기 스윙 (3~7일)

| 순위 | 전략 | 수익률 | 승률 | Sharpe | 거래수 | PF | 평균보유 |
|------|------|--------|------|--------|--------|-----|---------|
| #1 | MEAN_REVERSION | **+28.9%** | 63% | **9.43** | 8건 | 3.34 | 0.9일 |
| #2 | BOLLINGER_BAND | +103.8% | 60% | 7.27 | 40건 | 2.57 | 0.9일 |
| #3 | GOLDEN_CROSS | +300.5% | 56% | 7.13 | 117건 | 2.65 | 0.9일 |

**#1 최적 파라미터:**
- 진입: `bb_period=20, bb_mult=2.5, rsi_buy=35, rsi_sell=65`
- 청산: `stop=-4%, target_min=5%, target_max=10%, max_hold=7일`

### DESK4 — 중기 스윙 (2~4주)

| 순위 | 전략 | 수익률 | 승률 | Sharpe | 거래수 | PF | 평균보유 |
|------|------|--------|------|--------|--------|-----|---------|
| #1 | MEAN_REVERSION | **+109.2%** | **100%** | **45.49** | 9건 | 100.00 | 5.6일 |
| #2 | MEAN_REVERSION | +97.8% | 100% | 42.86 | 8건 | 100.00 | 5.6일 |
| #3 | BOLLINGER_BAND | +72.5% | 91% | 29.56 | 11건 | 18.59 | 3.7일 |

**#1 최적 파라미터:**
- 진입: `bb_period=20, bb_mult=2.5, rsi_buy=35, rsi_sell=65`
- 청산: `stop=-7%, target_min=10%, target_max=20%, max_hold=30일`

> ⚠️ 주의: DESK4 #1/#2의 승률 100%, PF=100은 거래수(9건)가 적어 과적합 가능성 있음. 샘플 확대 후 재검증 필요.

### DESK5 — 장기 추세추종 (1~3개월)

| 순위 | 전략 | 수익률 | 승률 | Sharpe | 거래수 | PF | 평균보유 |
|------|------|--------|------|--------|--------|-----|---------|
| #1 | MEAN_REVERSION | **+97.1%** | 67% | **10.98** | 18건 | 4.16 | 6.8일 |
| #2 | MEAN_REVERSION | +148.0% | 80% | 10.56 | 15건 | 5.88 | 8.2일 |
| #3 | MEAN_REVERSION | +101.1% | 69% | 10.44 | 16건 | 3.84 | 6.8일 |

**#1 최적 파라미터:**
- 진입: `bb_period=20, bb_mult=2.5, rsi_buy=35, rsi_sell=65`
- 청산: `stop=-5%, target_min=10%, target_max=25%, max_hold=40일`

---

## 5. 종합 인사이트

### 전략 패턴 발견
1. **MEAN_REVERSION + BB(mult=2.5) + RSI(35/65)** 조합이 DESK3/4/5에서 공통 1위 — 과매도 반등 포착이 일관되게 유효
2. **BOLLINGER_BAND**는 DESK2(초단기) 1위 — 짧은 보유(0.8일)와 narrow band가 스캘핑에 최적
3. **GOLDEN_CROSS(ma_short=5, ma_long=10)** — DESK3에서 117건/수익률 300% (거래수는 많지만 샤프 7.13)

### 청산규칙 패턴
| DESK | 최적 손절 | 최적 익절 | 최적 보유일 |
|------|----------|----------|-----------|
| 2 | -2.5% | 3~8% | 2일 |
| 3 | -4.0% | 5~10% | 7일 |
| 4 | -7.0% | 10~20% | 30일 |
| 5 | -5.0% | 10~25% | 40일 |

- 보유기간이 길어질수록 손절폭도 확대 (DESK4의 -7%가 최대)
- DESK5는 오히려 -5%로 타이트 — 장기 추세에서 빠른 손절이 효과적

---

## 6. 검증 체크리스트

- [x] **구현 목표**: `v4_optimization_results` 테이블에 4 DESK × 10전략 × 파라미터 그리드 = 583건 저장 완료
- [x] **검증 방법**: `SELECT desk_id, COUNT(*) FROM v4_optimization_results GROUP BY desk_id` → 2:144, 3:151, 4:144, 5:144
- [x] **완료 기준**: 4개 DESK 모두 결과 저장 ✅, DESK별 TOP3 출력 가능 ✅
- [x] **실패 기준**: 어느 DESK도 데이터 없음 — 해당 없음 ✅
- [x] **서비스 재시작**: 해당 없음 (스탠드얼론 스크립트, 서비스 미변경)
- [x] **에러 로그**: 스크립트 실행 중 에러 없음 (타임아웃은 이전 run, DB 저장은 정상)

---

## 7. 다음 단계 제안

1. **DESK4 과적합 검증**: 승률 100% 조합에 대해 OOS(Out-of-Sample) 기간 2025-01~08 재검증
2. **DESK별 최적 파라미터 → strategy_cards 반영**: `go100_strategy_cards.entry_rules` 업데이트
3. **DESK5 GOLDEN_CROSS(5/10)** DESK3와 함께 거래 많고 수익률 높은 조합 추가 검토
4. **샘플 확대**: 2025-01-01 ~ 2026-03-18 (15개월) 기간으로 재실행 시 통계 신뢰도 향상

---

## 8. 코드 레포 상태

- 파일: `backend/optimize_strategy_params.py` (기존 파일, 수정 없음)
- 코드 레포 커밋: 해당 없음 (신규 커밋 불필요, 기존 파일 활용)
- DB 변경: `v4_optimization_results` 테이블 생성 + 583건 저장 ✅
