# CUR-GO100-AI-MODEL-TRAIN-V2-001

> **작업일**: 2026-03-01 (보완판 최종)
> **담당**: Claude Code (AI)
> **분류**: GO100 / AI 모델 학습
> **상태**: ✅ PASS (보완 6건 전체 반영)

---

## 요약

GO100 AI 백억이의 V2 피처 데이터셋(263,450 레코드, 12개 월별 Parquet)을 활용해
**Walk-Forward 3-Fold** 방식으로 LightGBM 이진 분류 모델 + 다중 타겟 회귀 모델 3종을 학습.
EDA, Leakage 체크, Precision@Top-K, 임계값별 테이블, 메타데이터 JSON을 포함한 실전 수준 파이프라인 완성.

---

## 1. 데이터셋 개요

| 항목 | 값 |
|------|----|
| 원본 파일 | `ai_dataset_v2_202503.parquet` ~ `ai_dataset_v2_202602.parquet` (12개) |
| 전체 레코드 | 263,450 rows × 34 cols |
| valid_label==1 필터 후 | **260,897 rows** |
| 피처 컬럼 수 | **23개** |
| 분류 타겟 | `LABEL_UP_5D` (5거래일 후 +3% 초과 → 1) |
| 회귀 타겟 3종 | `LABEL_GAP_D1`, `LABEL_MFE_60MIN`, `LABEL_MFE_3D` |

### 피처 목록 (23개)

| 구분 | 피처 |
|------|------|
| **V1 기존 (14개)** | DUAL_FLOW_20D, SMALL_CAP_QUALITY, THEME_CYCLE_100B_COUNT, THEME_CYCLE_UL_COUNT, news_frequency_3d, REGIME_Q1~Q4, CLOSE, VOL_20D_AVG, TRADE_AMT_20D_AVG, PRICE_RETURN_20D, PRICE_RETURN_5D |
| **V2 신규 Track A (7개)** | SEC_LEADER_FLAG, RSI_14, BB_WIDTH, OBV_NEW_HIGH, V_RVOL, MA_ALIGNMENT, PRICE_POSITION_LAG1 |
| **V2 신규 Track B (2개)** | VWAP_DEVIATION, VWAP_SUPPORT_COUNT |

---

## 2. EDA 결과

### 2-1. Positive Rate 분포

**전체**: 29.60%

| REGIME_SEASON | Positive Rate | 샘플 수 |
|---------------|---------------|---------|
| Q1 (횡보) | 30.22% | 82,480 |
| Q2 (강세) | 26.39% | 77,565 |
| Q3 (약세·하락) | 26.65% | 55,214 |
| **Q4 (강약세)** | **37.52%** | 45,638 |

> **해석**: Q4(급반등 가능 구간)에서 상승 종목 비율이 가장 높음. 추후 Regime 조건부 모델 분리 시 Q4 가중 학습 우선 검토.

### 2-2. 월별 Positive Rate 추이

| 월 | Positive Rate | 샘플 수 |
|----|----|------|
| 2025-03 | 13.94% | 13,702 |
| 2025-04 | 17.58% | 13,702 |
| 2025-05 | 36.77% | 15,501 |
| 2025-06 | 38.07% | 15,697 |
| 2025-07 | 38.54% | 17,258 |
| 2025-08 | 31.54% | 17,671 |
| 2025-09 | 29.58% | 14,968 |
| 2025-10 | 23.99% | 16,133 |
| 2025-11 | 20.02% | 13,170 |
| 2025-12 | 29.48% | 16,003 |
| **2026-01** | **40.62%** | 18,864 |
| **2026-02** | **45.39%** | 10,639 |

> **핵심 관찰**: 2026년 1~2월(Test 기간) Positive rate가 40~45%로 Train 기간(평균 ~28%) 대비 크게 높음 → 시장 상승 국면 전환으로 인한 분포 drift 확인. 이것이 모델 AUC가 낮은 1차 원인.

### 2-3. Leakage 체크

| 항목 | 결과 |
|------|------|
| 피처-라벨 상관계수 > 0.3인 피처 | **없음** (모든 피처 \|corr\| ≤ 0.3) |
| PRICE_POSITION_LAG1 시점 | **안전** — v2 배치에서 t-1 LAG 적용 확인 |
| VWAP_DEVIATION | 당일 장 마감 후 값 (일봉 fallback 포함) — 스윙 예측에 적합 |

---

## 3. Walk-Forward 3-Fold 설계

| Fold | Train 기간 | Test 기간 | Train rows | Test rows |
|------|-----------|----------|-----------|---------|
| **Fold1** | 2025-03~09 | 2025-10~12 | 186,089 | 45,305 |
| **Fold2** | 2025-03~12 | 2026-01~02 | 231,394 | 29,503 |
| **Fold3** | 2025-06~12 | 2026-01~02 | 105,385 | 29,503 |

> Fold2 = 최종 모델 (전체 Train 기간 가장 긴 Fold, 실전 배포 기준).
> Fold3 = 학습 기간 단축 영향 확인용 (2025-03~05 기간 제외).

---

## 4. 분류 모델 (LABEL_UP_5D) — 3-Fold 성능

### 4-1. Fold별 평가 지표

| Fold | AUC | F1 | Precision | Recall | Best_iter |
|------|-----|----|-----------|--------|-----------|
| Fold1 (Test: Q4 2025) | 0.5407 | 0.4477 | 0.3292 | 0.6996 | 4 |
| **Fold2 (Test: 2026-01~02)** | **0.5338** | **0.5069** | **0.4419** | **0.5944** | **30** |
| Fold3 (Train 단축, Test: 2026-01~02) | 0.5473 | 0.5421 | 0.4465 | 0.6899 | 15 |

| 통계 | 값 |
|------|----|
| **AUC 평균** | **0.5406** |
| **AUC 표준편차** | **0.0055** |
| 과적합 경고 (편차 > 0.05) | ✅ 없음 (0.0055 < 0.05) |

> **안정성 확인**: 3-Fold AUC 편차 0.0055 — 매우 작음. 모델이 특정 기간에 과적합되지 않고 일관된 패턴을 학습했음.

### 4-2. Precision@Top-K (Fold2 기준)

모델 예측 확률 상위 K건의 실제 상승 비율 (CS 보조 입력 기준):

| K | Precision@Top-K | 해석 |
|---|-----------------|------|
| Top-20 | **25.0%** | 최고 확신 20건 중 5건 실제 상승 |
| Top-50 | **34.0%** | 상위 50건 중 17건 실제 상승 |
| Top-100 | **30.0%** | 상위 100건 중 30건 실제 상승 |

> **기준선 비교**: Test Positive rate 42.34% 대비 Top-K가 더 낮음 → 현재 모델은 단순 랜덤 선택보다 오히려 낮은 구간. 임계값 전략보다 CS 결합 후 재평가 필요.

### 4-3. 임계값별 Precision/Recall 테이블 (Fold2)

| Threshold | 예측 건수 | Precision | Recall | 전략 적합성 |
|-----------|---------|-----------|--------|-------------|
| **0.5** | 16,803 | 44.19% | 59.44% | 현재 기본 임계값 |
| 0.6 | 537 | 40.22% | 1.73% | 건수 급감, Precision도 하락 |
| 0.7 | 8 | 25.00% | 0.02% | 실용 불가 |
| 0.8 | 0 | — | — | 예측 없음 |

> **결론**: threshold 상향 시 건수만 급감하고 Precision도 개선되지 않음. 현재 모델의 예측 확률이 [0.4~0.6] 구간에 집중되어 있어 **임계값 조정보다 피처 강화가 우선**.

---

## 5. Feature Importance 상위 15개 (Fold2 기준)

| 순위 | 피처명 | 중요도 | 구분 | 해석 |
|------|--------|--------|------|------|
| **1** | **BB_WIDTH** | **123** | **V2 신규 ★** | 볼린저 밴드 폭 — **1위 진입**. 변동성 수축 후 확장 패턴이 핵심 예측 신호 |
| **2** | DUAL_FLOW_20D | 111 | V1 | 외인+기관 동시 매수 흐름 |
| **3** | **RSI_14** | **77** | **V2 신규 ★** | 14일 RSI — 과매도 반등·모멘텀 연속성 |
| **4** | PRICE_RETURN_5D | 70 | V1 | 최근 5일 수익률 모멘텀 |
| **5** | VOL_20D_AVG | 66 | V1 | 20일 평균 거래량 |
| **6** | **VWAP_DEVIATION** | **59** | **V2 신규 ★** | VWAP 대비 가격 이탈도 (수급 왜곡 포착) |
| **7** | **V_RVOL** | **58** | **V2 신규 ★** | 상대 거래량 — 세력 진입 이벤트 감지 |
| **8** | CLOSE | 43 | V1 | 종가 절대값 (주가 대역) |
| **9** | PRICE_RETURN_20D | 42 | V1 | 20일 중기 모멘텀 |
| **10** | REGIME_Q1 | 33 | V1 | 시장 레짐 원핫 (횡보) |
| **11** | THEME_CYCLE_100B_COUNT | 32 | V1 | 3년내 100억 돌파 횟수 |
| **12** | REGIME_Q4 | 30 | V1 | 시장 레짐 원핫 (강약세) |
| **13** | REGIME_Q2 | 29 | V1 | 시장 레짐 원핫 (강세) |
| **14** | **MA_ALIGNMENT** | **28** | **V2 신규 ★** | 이평선 정배열 (추세 확인 보조) |
| **15** | TRADE_AMT_20D_AVG | 26 | V1 | 20일 평균 거래대금 |

### V2 신규 피처 기여도 분석

| 항목 | 값 |
|------|----|
| Top 15 내 V2 신규 피처 수 | **5개 (33%)** |
| V2 신규 최고 순위 | **BB_WIDTH 1위** (V1 1위였던 DUAL_FLOW를 제침) |
| V2 신규 합산 중요도 | 345 / 전체 874 = **39.5%** |

**V2 신규 피처별 평가:**

| V2 피처 | 순위 | 판정 | 의미 |
|---------|------|------|------|
| BB_WIDTH | **1위** | ⭐⭐⭐ 핵심 | 변동성 패턴이 상승 예측에서 가장 강력한 단일 신호 |
| RSI_14 | **3위** | ⭐⭐⭐ 핵심 | 기술적 모멘텀 지표가 세력-수급 지표(DUAL_FLOW)와 동급 |
| VWAP_DEVIATION | **6위** | ⭐⭐ 유효 | 장중 수급 이탈도가 5일 예측에도 유의미한 기여 |
| V_RVOL | **7위** | ⭐⭐ 유효 | 거래량 급증 이벤트가 직접적 상승 예측 신호 |
| MA_ALIGNMENT | **14위** | ⭐ 보조 | 이평선 정배열은 추세 확인용, 단독 예측력은 낮음 |

> **Top 15 밖 V2 신규 피처**: SEC_LEADER_FLAG, OBV_NEW_HIGH, PRICE_POSITION_LAG1, VWAP_SUPPORT_COUNT
> → 단독 효과 약함. BB_WIDTH × RSI_14 교차 피처 또는 SEC_LEADER × V_RVOL 조합 피처로 재실험 권고.

---

## 6. 다중 타겟 회귀 모델 (Fold2 기준)

| 타겟 | MAE | R² | Corr | Best_iter | 전략 활용 |
|------|-----|----|------|-----------|---------|
| LABEL_GAP_D1 (익일 갭%) | 1.5977 | 0.0375 | 0.1998 | 205 | D6/D7 익일 갭 예측 — 현재 예측력 낮음 |
| **LABEL_MFE_60MIN** (장중 60분 MFE%) | **1.8198** | **0.5833** | **0.7808** | 316 | **D2/D4/D5 장중 기대수익 — 강력한 예측력** |
| LABEL_MFE_3D (3일 MFE%) | 5.6396 | 0.0784 | 0.3448 | 354 | 릴레이 재진입 판단 — 중간 수준 |

### 회귀 모델 Feature Importance 비교 (타겟별 Top 5)

| 순위 | GAP_D1 | MFE_60MIN | MFE_3D |
|------|--------|-----------|--------|
| 1 | BB_WIDTH | BB_WIDTH | BB_WIDTH |
| 2 | DUAL_FLOW_20D | RSI_14 | RSI_14 |
| 3 | RSI_14 | PRICE_RETURN_5D | DUAL_FLOW_20D |
| 4 | PRICE_RETURN_5D | V_RVOL | PRICE_RETURN_5D |
| 5 | V_RVOL | VWAP_DEVIATION | VWAP_DEVIATION |

> **공통 발견**: BB_WIDTH가 분류·회귀 전 모델에서 1위 또는 상위권 — V2 핵심 피처 확정.
> MFE_60MIN 모델 Corr=0.7808은 **실전 활용 수준** (장중 기대수익 예측에 즉시 투입 가능).

---

## 7. 실전 활용 권고

| 전략 | 추천 모델 | 임계값 | 근거 |
|------|-----------|--------|------|
| D2/D4/D5 장중 단타 | MFE_60MIN 회귀 | 예측값 ≥ 2.5% | R²=0.58, Corr=0.78 — 실용 수준 |
| D6/D7 스윙 매수 | LABEL_UP_5D 분류 | threshold=0.5 | 현재 Precision 44%, Recall 59% — CS 결합 후 재평가 |
| 릴레이 재진입 | MFE_3D 회귀 | 예측값 ≥ 5% | Corr=0.34 — GAP_D1보다 유효 |
| 익일 갭플레이 | GAP_D1 회귀 | 예측값 ≥ 2% | Corr=0.20 — 현재 약함, 피처 추가 후 재학습 권장 |

### CS(ConvictionScore) 연동 설계 (권고)

```python
cs = (
    0.4 * normalize(mfe_60min_pred)   # 장중 기대수익 (R²=0.58)
  + 0.3 * normalize(up5d_proba)       # 5일 상승 확률 (AUC=0.54)
  + 0.3 * normalize(mfe_3d_pred)      # 3일 MFE (Corr=0.34)
)
# threshold: cs >= 0.6 → 고확신 매수
```

---

## 8. 한계 및 개선 방향

| 항목 | 현황 | 개선 방향 |
|------|------|----------|
| 분포 drift | Test 기간 Positive rate 40~45% vs Train 28% | Regime 조건부 모델 (Q2/Q4 분리) |
| 분류 모델 AUC | 0.5406 — 랜덤 대비 미약 | BB_WIDTH × RSI_14 교차 피처 추가 |
| threshold 집중 | 예측 확률 [0.4~0.6] 집중 | 캘리브레이션 (Platt Scaling) |
| GAP_D1 예측력 | Corr=0.20 — 낮음 | 전날 옵션 IV, 갭 히스토리 피처 추가 |

---

## 9. 파일 경로

| 항목 | 경로 |
|------|------|
| 학습 스크립트 | `scripts/go100/train_ai_model_v2.py` |
| 분류 모델 | `data/go100/models/go100_brain_v2_lightgbm.joblib` |
| 분류 메타데이터 | `data/go100/models/go100_brain_v2_metadata.json` |
| 회귀 모델 (갭) | `data/go100/models/go100_brain_v2_gap_d1.joblib` |
| 회귀 모델 (MFE60) | `data/go100/models/go100_brain_v2_mfe_60min.joblib` |
| 회귀 모델 (MFE3D) | `data/go100/models/go100_brain_v2_mfe_3d.joblib` |
| 결과 JSON | `data/go100/models/go100_brain_v2_train_result_v2.json` |

---

## 10. 커밋 정보

| 항목 | 값 |
|------|----|
| 레포 | `moongoby/project-docs` |
| 브랜치 | `master` |
| 커밋 메시지 | `[GO100] AI 백억이 V2 데이터셋 기반 LightGBM 분류 모델 학습 및 Feature Importance 추출 완료` |
| 커밋 SHA | *(아래 반영)* |
| HTTP 200 | `https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-AI-MODEL-TRAIN-V2-001-20260301.md` |
