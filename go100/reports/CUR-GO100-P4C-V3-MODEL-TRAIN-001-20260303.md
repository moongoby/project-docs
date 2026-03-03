# CUR-GO100-P4C-V3-MODEL-TRAIN-001-20260303

**작성**: CURSOR-GO100  
**일시**: 2026-03-02 22:35 KST  
**연관 지시**: CUR-GO100-P4C-V3-MODEL-TRAIN-001  
**목적**: GO100 V3 LightGBM 모델 학습 결과 보고

---

## 1. 실행 요약

| 항목 | 값 |
|------|-----|
| 실행 스크립트 | scripts/go100/train_ai_model_v3.py |
| 학습 시작 | 2026-03-02 22:15 KST |
| 학습 완료 | 2026-03-02 22:34 KST |
| 소요 시간 | 19분 |
| 입력 데이터 | 305,061 rows × 30 features (valid_label==1) |
| CEO 에스컬레이션 | **없음** |

---

## 2. 분류 모델 결과 (LABEL_UP_5D, Walk-Forward 3-Fold)

| Regime 분할 | AUC Mean | AUC Std | 과적합 여부 | V2 대비 |
|------------|---------|---------|----------|--------|
| **통합 모델** | **0.5656** | 0.0289 | 없음 | **+0.0250 ✓** |
| **Q2 공격형** | **0.6092** | 0.0041 | 없음 | N/A (신규) |
| **비Q2 방어형** | **0.5588** | 0.0111 | 없음 | N/A (신규) |

- **V2 기준선 (0.5406)** 대비 통합 모델 +2.5% 개선
- Q2 공격형 AUC **0.6092**: 목표 0.58 초과 **달성 ✓**

---

## 3. 회귀 모델 결과 (통합, Fold2 기준)

| 타겟 | MAE | R² | Corr | 목표 달성 |
|------|-----|-----|------|---------|
| LABEL_MFE_60MIN | 1.8010 | 0.5920 | 0.7859 | ⚠️ (목표 0.65 미달) |
| LABEL_MFE_3D | 5.6269 | 0.0844 | 0.3442 | 낮음 |
| LABEL_GAP_D1 | 1.6193 | 0.0206 | 0.1667 | 낮음 |

**참고**: MFE_60MIN R²=0.5920는 목표(0.65) 미달이나 V2 대비 향상 예상 (V2 MFE_60MIN R² 미기록). 60분 이후 수익은 다양한 외부 요인에 의해 결정되어 예측 난이도가 높음.

---

## 4. Feature Importance Top 15 (통합 분류, Fold2)

| 순위 | 피처명 | 중요도 | V3신규 |
|------|-------|-------|-------|
| 1 | DUAL_FLOW_20D | 61 | |
| 2 | PRICE_RETURN_5D | 59 | |
| 3 | REGIME_Q1 | 49 | |
| 4 | RSI_14 | 49 | |
| 5 | BB_WIDTH | 49 | |
| **6** | **DUAL_x_Q2** | **44** | **★** |
| **7** | **BB_WIDTH_x_RSI** | **43** | **★** |
| **8** | **FORCE_ACC_5D** | **32** | **★** |
| 9 | PRICE_RETURN_20D | 30 | |
| 10 | VOL_20D_AVG | 29 | |
| 11 | VWAP_DEVIATION | 24 | |
| 12 | REGIME_Q2 | 22 | |
| 13 | REGIME_Q3 | 21 | |
| 14 | MA_ALIGNMENT | 21 | |
| 15 | CLOSE | 20 | |

**V3 신규 피처 Top 15 진입: 3개 (DUAL_x_Q2 6위, BB_WIDTH_x_RSI 7위, FORCE_ACC_5D 8위)**

---

## 5. V2 vs V3 성능 비교표

| 항목 | V2 | V3 통합 | V3 Q2공격형 | 비고 |
|------|-----|---------|-----------|------|
| AUC (Walk-Forward 평균) | 0.5406 | 0.5656 | 0.6092 | +0.0250 / +0.0686 개선 |
| AUC Std | N/A | 0.0289 | 0.0041 | Q2모델 안정적 |
| 피처 수 | 23개 | 30개 | 30개 | +7개 |
| Regime 분할 | 없음 | 통합 | Q2전용 | 신규 |
| V3 신규피처 Top15 | - | 3개 | 3개 | DUAL_x_Q2 등 |

---

## 6. 저장 모델 목록

| 파일명 | 용도 |
|--------|------|
| go100_brain_v3_clf_unified.joblib | 통합 분류 (기본) |
| go100_brain_v3_clf_q2_aggressive.joblib | Q2 공격형 분류 |
| go100_brain_v3_clf_nonq2_defensive.joblib | 비Q2 방어형 분류 |
| go100_brain_v3_reg_mfe_60min_unified.joblib | MFE_60MIN 회귀 |
| go100_brain_v3_reg_mfe_3d_unified.joblib | MFE_3D 회귀 |
| go100_brain_v3_reg_gap_d1_unified.joblib | GAP_D1 회귀 |
| go100_brain_v3_train_result.json | 학습 결과 메타데이터 |

**저장 경로**: data/go100/models/v3/  
**활성화 플래그**: 전체 `active: False` — CEO 승인 후 전환 예정

---

## 7. CEO 판단 필요 사항

### 7-1. V3 모델 활성화 여부
- **V3 통합 AUC 0.5656** > V2 기준선 0.5406 → V3 활성화 권장
- **Q2 공격형 AUC 0.6092** → 목표(0.58) 초과, 즉시 활성화 검토 가능
- 현재 모든 모델 `active: False` (롤백 안전)
- CEO 승인 시: 각 모델 metadata.json의 `active: True` 변경 → go100 서비스 재시작

### 7-2. MFE_60MIN R² 0.5920 (목표 0.65 미달)
- 회귀 모델 추가 튜닝 여부 CEO 판단 요청
- 옵션: (a) 현재 R² 유지 운용 (b) 하이퍼파라미터 튜닝 추가 진행

---

## 8. 다음 단계

1. CEO V3 모델 활성화 승인
2. go100 서비스 재시작 및 V3 모델 적용 확인
3. 30일 모의투자 시작 (2026-03-03 장 개장 09:00)
4. Telegram 봇 토큰 설정 (GO100_TELEGRAM_BOT_TOKEN)

---

**커밋**: kis-autotrade-v4 `21af802d` (train_ai_model_v3.py)  
**학습 로그**: /var/log/go100/v3_train_run.log
