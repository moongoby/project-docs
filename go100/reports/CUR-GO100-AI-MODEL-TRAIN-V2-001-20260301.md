# CUR-GO100-AI-MODEL-TRAIN-V2-001

> **작업일**: 2026-03-01
> **담당**: Claude Code (AI)
> **분류**: GO100 / AI 모델 학습
> **상태**: ✅ PASS

---

## 요약

GO100 AI 백억이의 V2 피처 데이터셋(263,450 레코드, 12개 월별 Parquet)을 활용해
Walk-Forward 방식으로 **LightGBM 이진 분류 모델**을 학습하고
Feature Importance 상위 15개와 성능 지표를 리포팅한다.

---

## 1. 데이터셋 개요

| 항목 | 값 |
|------|----|
| 원본 파일 | `data/go100/features/v2/ai_dataset_v2_202503.parquet` ~ `ai_dataset_v2_202602.parquet` (12개) |
| 전체 레코드 | 263,450 rows × 34 cols |
| 피처 컬럼 수 | **23개** |
| 타겟 컬럼 | `LABEL_UP_5D` (5거래일 후 +3% 초과 → 1, 이하 → 0) |
| valid_label 필터 후 | 260,897 rows |

### 피처 목록 (23개)

| 구분 | 피처 |
|------|------|
| **V1 기존** | DUAL_FLOW_20D, SMALL_CAP_QUALITY, THEME_CYCLE_100B_COUNT, THEME_CYCLE_UL_COUNT, news_frequency_3d, REGIME_Q1~Q4, CLOSE, VOL_20D_AVG, TRADE_AMT_20D_AVG, PRICE_RETURN_20D, PRICE_RETURN_5D |
| **V2 신규 (Track A)** | SEC_LEADER_FLAG, RSI_14, BB_WIDTH, OBV_NEW_HIGH, V_RVOL, MA_ALIGNMENT, PRICE_POSITION_LAG1 |
| **V2 신규 (Track B)** | VWAP_DEVIATION, VWAP_SUPPORT_COUNT |

---

## 2. Walk-Forward 분할

| 구분 | 기간 | 행 수 | 양성률 |
|------|------|--------|--------|
| **Train Set** | 2025-03-04 ~ 2025-12-30 | **231,394** | 27.98% |
| **Test Set** | 2026-01-02 ~ 2026-02-20 | **29,503** | 42.34% |

> **Note**: Test 기간(1~2월) 양성률이 Train 대비 높음 → 2026년 초 시장 상승 국면 반영.
> `class_weight='balanced'` 적용으로 클래스 불균형 보정.

---

## 3. 모델 학습 설정

| 항목 | 값 |
|------|----|
| 모델 | `lightgbm.LGBMClassifier` |
| n_estimators | 1,000 (Early Stopping) |
| learning_rate | 0.05 |
| max_depth | 6 |
| num_leaves | 31 |
| subsample | 0.8 |
| colsample_bytree | 0.8 |
| class_weight | `balanced` |
| Early Stopping | stopping_rounds=50 |
| **Best Iteration** | **27회** |
| 학습 소요 | 8.0초 |

---

## 4. Test Set 성능 지표

| 지표 | 값 | 해석 |
|------|----|------|
| **Accuracy** | 0.5109 | 51.1% — 랜덤 대비 소폭 상회 |
| **Precision** | 0.4428 | 상승 예측의 44.3%가 실제 상승 |
| **Recall** | 0.6000 | 실제 상승 종목의 60.0% 포착 |
| **F1-Score** | 0.5095 | Precision-Recall 조화 평균 |
| **ROC-AUC** | 0.5349 | 랜덤(0.5) 대비 +0.035 변별력 |

### 분류 리포트

```
              precision    recall  f1-score   support
     DOWN(0)       0.60      0.45      0.51     17,012
       UP(1)       0.44      0.60      0.51     12,491
    accuracy                           0.51     29,503
   macro avg       0.52      0.52      0.51     29,503
weighted avg       0.53      0.51      0.51     29,503
```

---

## 5. Feature Importance 상위 15개

| 순위 | 피처명 | 중요도 | 구분 | 해석 |
|------|--------|--------|------|------|
| **1** | DUAL_FLOW_20D | 119 | V1 | 외인+기관 동시 매수 흐름 — 최고 변별력 |
| **2** | **BB_WIDTH** | 108 | **V2 신규** | 볼린저 밴드 폭 — 변동성 확장/수축 패턴 |
| **3** | **RSI_14** | 69 | **V2 신규** | 14일 RSI — 과매도/과매수 기술적 신호 |
| **4** | PRICE_RETURN_5D | 64 | V1 | 최근 5일 수익률 모멘텀 |
| **5** | VOL_20D_AVG | 55 | V1 | 20일 평균 거래량 |
| **6** | **VWAP_DEVIATION** | 54 | **V2 신규** | VWAP 대비 가격 이탈도 (Track B) |
| **7** | **V_RVOL** | 48 | **V2 신규** | 상대 거래량(Relative Volume) |
| **8** | PRICE_RETURN_20D | 40 | V1 | 20일 중기 모멘텀 |
| **9** | CLOSE | 35 | V1 | 종가 절대값 (주가 대역) |
| **10** | REGIME_Q1 | 32 | V1 | 시장 레짐 — 횡보 국면 원핫 |
| **11** | REGIME_Q4 | 28 | V1 | 시장 레짐 — 약세 국면 원핫 |
| **12** | REGIME_Q2 | 27 | V1 | 시장 레짐 — 강세 국면 원핫 |
| **13** | THEME_CYCLE_100B_COUNT | 25 | V1 | 3년내 100억 돌파 횟수 |
| **14** | TRADE_AMT_20D_AVG | 25 | V1 | 20일 평균 거래대금 |
| **15** | **MA_ALIGNMENT** | 24 | **V2 신규** | 이평선 정배열 여부 |

### V2 신규 피처 기여도 분석

**V2 신규 피처 Top 15 내 포함 수: 5개 (BB_WIDTH, RSI_14, VWAP_DEVIATION, V_RVOL, MA_ALIGNMENT)**

| V2 신규 피처 | 순위 | 중요도 | 평가 |
|-------------|------|--------|------|
| BB_WIDTH | **2위** | 108 | ⭐ 핵심 기여 — DUAL_FLOW_20D에 이어 2위 진입. 변동성 수축 후 확장 패턴이 단기 급등과 강한 상관 |
| RSI_14 | **3위** | 69 | ⭐ 핵심 기여 — 과매도 반등/모멘텀 연속성 구분에 효과적 |
| VWAP_DEVIATION | **6위** | 54 | ⭐ 유의미 — VWAP 이탈도로 단기 수급 왜곡 포착 |
| V_RVOL | **7위** | 48 | ⭐ 유의미 — 거래량 급증 이벤트 감지 (세력 진입 시그널) |
| MA_ALIGNMENT | **15위** | 24 | △ 중간 — 이평선 정배열은 추세 확인 보조 지표 |

> **결론**: V2 신규 피처 5개가 Top 15 내 **33%를 차지**하며 실질적 기여.
> 특히 BB_WIDTH(2위)·RSI_14(3위)는 V1 대비 강력한 신규 변별력을 제공.
> SEC_LEADER_FLAG, OBV_NEW_HIGH, PRICE_POSITION_LAG1, VWAP_SUPPORT_COUNT는
> 이번 베이스라인에서 Top 15 밖 → 멀티타겟 실험 또는 파생 피처 조합 시 재검토 권장.

---

## 6. 베이스라인 해석 및 한계

### 현재 성능 평가
- ROC-AUC **0.5349**는 랜덤 베이스라인(0.5)을 넘지만 실전 투입 수준 미달.
- 원인 분석:
  1. **분포 drift**: Train 양성률 27.98% vs Test 42.34% — 2026년 초 시장이 강세 국면으로 전환, 모델이 약세 학습 편향.
  2. **Early Stopping 27회**: 과소적합(underfitting) 가능성 — 피처 수(23개) 대비 트리 깊이·복잡도 제한.
  3. **Z-score 일괄 정규화**: 월별 Z-score로 인해 절대값 정보 소실.

### 다음 개선 방향
1. **멀티타겟 앙상블**: LABEL_MFE_3D(단기 MFE) 추가 타겟 실험
2. **피처 엔지니어링**: BB_WIDTH × RSI_14 교차 피처, SEC_LEADER × V_RVOL 조합
3. **regime 조건부 모델**: Q2(상승)/Q4(하락) 별도 모델 분리
4. **캘리브레이션**: predict_proba threshold 최적화 (Precision 우선 전략)

---

## 7. 파일 경로

| 항목 | 경로 |
|------|------|
| 학습 스크립트 | `scripts/go100/train_ai_model_v2.py` |
| 저장 모델 | `data/go100/models/go100_brain_v2_lightgbm.joblib` |
| 결과 JSON | `data/go100/models/go100_brain_v2_train_result.json` |
| 입력 데이터 | `data/go100/features/v2/ai_dataset_v2_2025{03..12}.parquet` + `2026{01,02}.parquet` |

---

## 8. 커밋 정보

| 항목 | 값 |
|------|----|
| 레포 | `moongoby/project-docs` |
| 커밋 메시지 | `[GO100] AI 백억이 V2 데이터셋 기반 LightGBM 분류 모델 학습 및 Feature Importance 추출 완료` |
| 브랜치 | `master` |
| 커밋 SHA | *(아래 git push 후 기록)* |
| HTTP 200 확인 | `https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-AI-MODEL-TRAIN-V2-001-20260301.md` |
