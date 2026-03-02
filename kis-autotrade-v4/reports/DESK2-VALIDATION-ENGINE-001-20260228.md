# DESK2-VALIDATION-ENGINE-001

## 가설 검증 엔진 구축 + Phase 2E 생존자 편향 검증

| 항목 | 내용 |
|------|------|
| 문서ID | DESK2-VALIDATION-ENGINE-001 |
| 날짜 | 2026-02-28 |
| 모델 | Claude Opus 4.6 |
| 우선순위 | P0 (CEO 직접 지시) |

---

## [인계 확인]
- 직전 완료: PHASE2E-001
- 현재 단계: Phase 1+ (발굴 연구)
- CEO 지시 적용: D-001(복합분석), D-002(수급본질/개인포함), D-003(DESK=풀관리), D-007(컨텍스트)
- strategy_cards: 60
- open_positions: 14

---

## Executive Summary

**Phase 2E의 "100% 포착" 결론은 생존자 편향이 확인됨.**

| 핵심 지표 | 값 |
|-----------|-----|
| Pipeline Precision | **6.9%** |
| TARGET (TOP-20 NEW) | 229종목 |
| CONTROL (DESK3 2+ events, non-TOP-20) | **3,109종목** |
| Total DESK3 qualified | 3,338종목 |
| 체크리스트 | **8/8 PASS** |
| 유의미 판별 변수 | **69개** (|AUC-0.5| ≥ 0.05) |
| 추출 변수 총 | 97개 (6개 카테고리) |
| 엔진 모듈 | 5/5 정상 작동 |
| 실행 시간 | 68초 |

**DESK3 이벤트를 2개 이상 경험한 종목 3,338개 중 실제 TOP-20 진입은 229개(6.9%).**
나머지 3,109개는 같은 차트 패턴을 보였지만 급등하지 않았다.
"파이프라인이 100% 포착했다"는 맞지만, "파이프라인이 포착한 종목 중 6.9%만 실제 급등했다"가 완전한 진실.

---

## 검증 체크리스트

| # | 항목 | 결과 | 비고 |
|---|------|------|------|
| 1 | 대조군 포함 | PASS | 3,109종목 |
| 2 | 대조군 비율 ≥ 1× | PASS | 13.58× |
| 3 | 개인수급 변수 포함 (D-002) | PASS | S_INDIVIDUAL_* 7개 변수 |
| 4 | 최근 사이클 기준 | PASS | recent_cycle=True |
| 5 | MA120 계산 충분 | PASS | |
| 6 | 생존자 편향 대응 | PASS | CONTROL = DESK3 충족 비급등 종목 |
| 7 | 3주체 수급 포함 | PASS | 외인/기관/개인 전체 |
| 8 | CEO 지시 준수 | PASS | D-001~D-007 |

---

## TASK 1: 가설 검증 엔진

### 모듈 구성

| 모듈 | 파일 | 기능 | 라인 | 상태 |
|------|------|------|------|------|
| 1 | universe_builder.py | 유니버스 생성 (TARGET+CONTROL) | ~230 | PASS |
| 2 | feature_engine.py | 97 변수 추출 (6 카테고리) | ~520 | PASS |
| 3 | validation_engine.py | AUC, Cohen's d, KS test, 클러스터링, 스코어카드, 풀 시뮬레이션 | ~310 | PASS |
| 4 | report_generator.py | 표준 보고서 + HANDOVER 업데이트 생성 | ~170 | PASS |
| 5 | hypothesis_runner.py | 원스톱 파이프라인 실행기 | ~120 | PASS |

저장 경로: `/root/kis-autotrade-v4/backend/app/services/discovery/`

### 변수 카테고리 (97개)

| 카테고리 | 접두사 | 변수 수 | 주요 변수 |
|----------|--------|---------|----------|
| PRICE | P_ | 20 | MA5~120, 정배열, 52W, BB, ATR, 괴리율 |
| VOLUME | V_ | 15 | MA5/20/60, RVOL, 골든크로스, 폭발, CV |
| SUPPLY | S_ | 20 | 3주체 D-1/5D/20D, 연속매수, 개인스파이크, CMB4 |
| NEWS | N_ | 8 | D-1/7/30, 연속일수, 집중, 히든촉매 |
| EVENT | E*_ | 24 | E1~E12 발생여부 + 발생일 (12×2) |
| CONTEXT | C_ | 10 | L3, W2, X9, 시장국면, 상장일수 |

**CEO D-002 준수: 개인수급 변수 7개 포함**
- S_INDIVIDUAL_D1, S_INDIVIDUAL_CONSEC, S_INDIVIDUAL_5D, S_INDIVIDUAL_20D
- S_INDIVIDUAL_5D_SLOPE, S_INDIVIDUAL_SPIKE, S_3ENTITY_BUY

### 엔진 핵심 기능

1. **validate_checklist**: 8개 필수 항목 자동 검증 (개인수급 누락 시 ERROR 발생)
2. **build_control_desk3_events**: ohlcv_daily 전 종목 스캔 → E7~E11 이벤트 계산 → CONTROL 생성
3. **compare_groups**: AUC + Cohen's d + KS test 자동 계산
4. **build_scorecard**: AUC ≥ threshold 변수 선별 → 상관관계 제거 → 가중합 스코어
5. **recent_cycle=True**: 이벤트를 최근 250거래일 내로 제한 (Phase 2E 교훈 반영)

---

## TASK 2: Phase 2E 생존자 편향 검증

### 검증 설계

```
가설: "DESK3 이벤트(E7~E11) 2+개 경험 종목은 TOP-20 진입 확률이 높다"
반증: "같은 조건 충족했지만 TOP-20 미진입 종목이 14배 더 많다"

TARGET: Phase 2E 229종목 (2026-01-12~02-25 기간 TOP-20 NEW)
CONTROL: 같은 기간 E7~E11 중 2+개 충족 & TOP-20 미진입 → 3,109종목
```

### 핵심 결과: Pipeline Precision = 6.9%

| 지표 | 값 |
|------|-----|
| DESK3 이벤트 2+ 총 종목 | **3,338** |
| 그 중 TOP-20 진입 (TARGET) | 229 (**6.9%**) |
| 그 중 TOP-20 미진입 (CONTROL) | 3,109 (**93.1%**) |

**해석: DESK3 이벤트만으로는 급등을 예측할 수 없다. 100개 종목이 같은 패턴을 보여도 7개만 급등한다.**

### CONTROL 이벤트 분포

| DESK3 이벤트 수 | CONTROL 종목 수 |
|----------------|----------------|
| 2개 | 대다수 |
| 3개 | 중간 |
| 4개 | 소수 |
| 5개 | 극소수 |

### Top 15 판별 변수 (TARGET vs CONTROL)

| 순위 | 변수 | AUC | Cohen's d | 해석 |
|------|------|-----|-----------|------|
| 1 | V_TRADE_AMOUNT | 0.964 | +0.710 | 거래대금 규모 (동시 지표) |
| 2 | P_CHG_5D | 0.957 | +2.061 | 5일 가격변화율 (D-day 효과) |
| 3 | P_BB_POS | 0.946 | +2.356 | BB 밴드 내 위치 (상단돌파) |
| 4 | V_5D_SLOPE | 0.944 | +0.904 | 5일 거래량 추세 (급증) |
| 5 | P_GAP_MA20 | 0.936 | +1.879 | MA20 괴리율 (이격도) |
| 6 | V_RVOL | 0.932 | +1.522 | 상대거래량 (폭발) |
| 7 | N_D1_COUNT | 0.932 | +0.503 | D-1 뉴스 건수 |
| 8 | P_GAP_MA60 | 0.920 | +1.401 | MA60 괴리율 |
| 9 | P_GAP_MA120 | 0.908 | +1.232 | MA120 괴리율 |
| 10 | V_MA5 | 0.901 | +0.602 | 5일 평균 거래량 |
| 11 | P_52W_LOW_PCT | 0.887 | +0.964 | 52W 저가 대비 위치 |
| 12 | P_CHG_20D | 0.886 | +0.927 | 20일 가격변화율 |
| 13 | V_MA20 | 0.861 | +0.550 | 20일 평균 거래량 |
| 14 | P_BB_WIDTH | 0.858 | +1.043 | BB 폭 (변동성) |
| 15 | V_MA60 | 0.851 | +0.466 | 60일 평균 거래량 |

### 판별력 해석 — 핵심 경고

**상위 판별 변수의 대부분은 "동시 지표"(concurrent indicator)이다.**

- V_TRADE_AMOUNT (AUC 0.964): D-day에 거래대금이 폭발하기 때문 → 예측 아닌 확인
- P_CHG_5D (AUC 0.957): D-day 직전 5일간 이미 급등 중 → 시세 반영
- V_RVOL (AUC 0.932): 거래량 폭발은 급등의 원인이 아닌 동반현상

이는 D-1(D-day 전날) 기준으로 피처를 추출했기 때문.
TARGET은 "내일 급등할 종목의 전날" → 이미 움직임이 시작됨.
CONTROL은 "아무 날의 전날" → 특별한 움직임 없음.

**선행 지표(leading indicator)로 사용 가능한 변수:**

| 변수 | AUC | 유형 | 선행성 |
|------|-----|------|--------|
| N_D1_COUNT | 0.932 | 뉴스 | D-1 뉴스 = 선행 가능 |
| V_MA60 | 0.851 | 거래량 장기 | 장기 축적 |
| P_52W_LOW_PCT | 0.887 | 가격 위치 | 구조적 위치 |
| P_BB_WIDTH | 0.858 | 변동성 | 준비 상태 |

### TYPE별 분석

| TYPE | 종목수 | V_TRADE AUC | P_CHG_5D AUC | 특이사항 |
|------|--------|-------------|-------------|----------|
| TYPE-A Slow Build | 130 | 0.988 | 0.965 | 거래대금 판별력 최고 |
| TYPE-B Mid Turn | 24 | 0.970 | 0.937 | 소수 그룹, 판별 양호 |
| TYPE-C Short Trigger | 148 | 0.939 | 0.950 | 가격변화 판별력 높음 |
| TYPE-D Sudden | 156 | 0.965 | 0.959 | 전반적 판별력 균일 |

**모든 TYPE에서 CONTROL 대비 판별력 높음** — 단, "동시 지표" 편향 주의.

### Precision 향상 필터 후보

| 필터 | 조건 | TARGET 통과율 | CONTROL 통과율 |
|------|------|-------------|-------------|
| V_TRADE_AMOUNT | > 55.7B | 75% | 4% |
| P_CHG_5D | > 14.9% | 75% | 3% |
| P_BB_POS | > 103.8 | 75% | 3% |
| V_5D_SLOPE | > 263K | 75% | 4% |
| P_GAP_MA20 | > 17.3% | 75% | 3% |

**필터 적용 시 Precision: ~50%까지 향상 가능 (TARGET 75% × 필터 효과)**
단, 이 필터들도 "동시 지표"이므로 **D-2~D-5 기준 선행 필터**로 전환 필요.

---

## TASK 3: 엔진 테스트 보고

### 모듈별 실행 결과

| 모듈 | 상태 | 실행 내용 | 비고 |
|------|------|----------|------|
| universe_builder | PASS | TARGET=229, CONTROL=3,109 생성 | DESK3 이벤트 스캔 21초 |
| feature_engine | PASS | 3,567 entries × 97 variables | 벌크 로드 45초 |
| validation_engine | PASS | 체크리스트 8/8, 그룹비교, 스코어카드 | 비교분석 2초 |
| report_generator | PASS | 보고서 생성 | 자동화 |
| hypothesis_runner | PASS | 전체 파이프라인 정상 | 총 68초 |

### validate_checklist 8개 항목

| # | 항목 | 결과 |
|---|------|------|
| 1 | 대조군 존재 | PASS (3,109) |
| 2 | 대조군 비율 ≥ 1× | PASS (13.58×) |
| 3 | 개인수급 포함 (D-002) | PASS (7 변수) |
| 4 | 최근 사이클 기준 | PASS |
| 5 | MA120 계산 충분 | PASS |
| 6 | 생존자 편향 대응 | PASS |
| 7 | 3주체 수급 | PASS |
| 8 | CEO 지시 준수 | PASS |

### 실행 통계

| 지표 | 값 |
|------|-----|
| 총 변수 수 | 97 |
| 유니버스 크기 | 3,338 (TARGET 229 + CONTROL 3,109) |
| OHLCV 로드 | 1,079,900 rows (CONTROL 스캔), 추가 벌크 로드 |
| 실행 시간 | 68초 |
| 에러 | 0건 |

### 엔진 개선 필요 사항

1. **feature_engine의 D-day 기준점 변경 옵션**: 현재 D-1만 지원 → D-5, D-10 등 offset 지원 필요 (선행 지표 분석용)
2. **X9 (섹터 동반상승) 구현**: 현재 placeholder → 섹터 매핑 테이블 필요
3. **시가총액 구간**: 현재 placeholder → market_cap 데이터 필요
4. **중복 엔트리 방지**: universe 내 TARGET과 NEW 그룹 중복 → 비교 시 중복 제거 로직 추가
5. **병렬 처리**: 3,000+ 종목 피처 추출 시 멀티프로세싱 적용 검토

---

## 결론 및 권장안

### 1. Phase 2E "100% 포착" 수정

| 항목 | Phase 2E 결론 | 검증 후 수정 |
|------|-------------|------------|
| DESK3 포착률 | 100% (229/229) | 맞음 (recall 100%) |
| Pipeline Precision | 미측정 | **6.9%** (229/3,338) |
| 실전 의미 | "모든 NEW를 포착 가능" | "NEW를 포착하지만 93%는 false positive" |

### 2. 실전 파이프라인 권장안

**DESK3 이벤트만으로는 파이프라인 가동 불가** (precision 6.9%).
추가 필터 또는 2단계 검증 필요:

1. **1단계 (DESK3 풀)**: DESK3 이벤트 2+ → 풀 진입 (최대 3,000+종목)
2. **2단계 (필터링)**: 선행 지표 기반 축소 → 목표 50~100종목
   - N_D1_COUNT (뉴스 건수): 선행 가능
   - V_MA60 (장기 거래량): 구조적 준비
   - P_BB_WIDTH (BB 폭): 변동성 상태
   - S_FOREIGN_5D + S_INSTITUTION_5D (수급 축적): D-002 핵심
3. **3단계 (실시간 트리거)**: 당일 거래량 폭발 + 가격 이격 감지 → 전략카드 진입

### 3. 다음 단계

1. **D-5 기준 피처 비교**: feature_engine에 offset 파라미터 추가 → D-5 기준으로 TARGET vs CONTROL 재비교
   → "5일 전에 판별 가능한 선행 변수"만 추출
2. **L3+X9 결합**: Phase 2B에서 확인된 L3+X9(AUC 0.851)와 DESK3 이벤트 결합 시 precision 변화 측정
3. **DESK3 이벤트 수 threshold 상향**: 2개 → 3개, 4개로 올릴 때 precision/recall 트레이드오프 측정
4. **기획서 v3.1 업데이트**: precision 6.9%를 DESIGN-SPEC에 반영, 2단계 필터링 설계 추가

---

## 데이터 및 스크립트

| 파일 | 설명 |
|------|------|
| `backend/app/services/discovery/universe_builder.py` | 모듈 1: 유니버스 빌더 |
| `backend/app/services/discovery/feature_engine.py` | 모듈 2: 피처 엔진 (97 변수) |
| `backend/app/services/discovery/validation_engine.py` | 모듈 3: 검증 엔진 |
| `backend/app/services/discovery/report_generator.py` | 모듈 4: 보고서 생성기 |
| `backend/app/services/discovery/hypothesis_runner.py` | 모듈 5: 가설 검증 실행기 |
| `/tmp/validation_engine_task2.py` | TASK 2 실행 스크립트 |
| `/tmp/validation_engine_task2_results.json` | TASK 2 결과 JSON |

---

## 한계 및 주의사항

1. **동시 지표 편향**: 상위 판별 변수 대부분이 D-1 기준으로 이미 급등 시작 후의 지표. D-5~D-10 기준 재분석 필요
2. **CONTROL 날짜 편향**: CONTROL 종목의 기준일을 기간 중간점으로 설정. TARGET과 동일한 날짜 매칭이 이상적
3. **X9, 시가총액**: 섹터 데이터 및 시가총액 데이터 미보유로 placeholder 처리
4. **TOP-20 정의**: go100_top600 테이블 미존재. Phase 1 JSON 파일에서 TOP-20 이력 로드
5. **CONTROL 범위**: E7~E11 중 2+개를 "임의의 날"에 충족하면 CONTROL로 편입. 보다 엄격한 "D-day 직전 30일 내 충족" 조건으로 제한 시 CONTROL 감소 가능

---

*Generated by Validation Engine — 2026-02-28*

HANDOVER.md 업데이트 완료: 43bca05
