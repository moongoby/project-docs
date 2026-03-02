# Phase 4-A 피처 엔지니어링 완료 보고서

**파일명**: CUR-GO100-P4A-FEATURE-ENG-001-20260302.md  
**작성일**: 2026-03-02  
**작성자**: [CURSOR-GO100]  
**지시 출처**: DIRECTIVE `CUR-GO100-P4A-FEATURE-AND-PAPER-PREP-001` (GO100 지휘관 자체 승인)  
**커밋**: `08c433e5` (kis-autotrade-v4 레포)

---

## 요약

| 항목 | 결과 |
|------|------|
| 교차 피처 구현 | PASS (3개) |
| 신규 단일 피처 구현 | PASS (4개) |
| V3 통합 계산 함수 | PASS |
| 기존 V2 피처 회귀 테스트 | PASS |
| feature_store.py 목록 업데이트 | PASS (23 → 30개) |
| 코드 커밋 | `08c433e5` |

---

## 1. 구현 내용

### 1.1 교차 피처 3개 (`compute_cross_features`)

| 피처명 | 계산식 | 가설 |
|--------|--------|------|
| `BB_WIDTH_x_RSI` | BB_WIDTH × (100 - RSI_14) / 100 | 볼린저 수축 + RSI 과매도 복합 → 반등 신호 |
| `SEC_LEAD_x_RVOL` | SEC_LEADER_FLAG × V_RVOL | 섹터 대장주 + 거래량 폭발 = 섹터 회전 신호 |
| `DUAL_x_Q2` | DUAL_FLOW_20D × REGIME_Q2 | 상승장에서의 수급 신호가 더 신뢰할 수 있음 |

### 1.2 신규 단일 피처 4개

| 피처명 | 계산 방법 | CEO Directive |
|--------|---------|---------------|
| `NEW_HIGH_52W_WITH_VOL` | 52주 신고가 돌파 AND 거래량 ≥ 20일 평균 × 2.0 | **T-001** 직접 구현 |
| `FORCE_ACC_5D` | (기관+외인 5일 순매수) / (시총 추정치) × 100 | D-001 복합계 |
| `MKT_SEASON_MONTH` | sin(2π × (month-1) / 12) | D-001 다시점 분석 |
| `D_D1_D2_ENTRY` | 2일 연속 장대양봉 (몸통 ≥ 시가 × 1.03) | D-001 패턴 분석 |

### 1.3 통합 함수

```python
# compute_v3_features() — 7개 V3 피처 통합 계산
result = compute_v3_features(track_a, regime, ohlcv_rows, investor_rows, target_date, dual_flow_20d)
# 반환: 7개 피처 딕셔너리
```

---

## 2. 테스트 결과

### 2.1 V3 피처 계산 테스트

```
교차피처: {'BB_WIDTH_x_RSI': 5.525, 'SEC_LEAD_x_RVOL': 2.5, 'DUAL_x_Q2': 0.75}
NEW_HIGH_52W_WITH_VOL: 0.0 (dummy 데이터: 신고가 미달)
FORCE_ACC_5D: 0.005816
MKT_SEASON_MONTH (2월): 0.5
D_D1_D2_ENTRY: 0.0
V3 피처 수: 7
PASS: V3 피처 계산 정상
```

### 2.2 기존 V2 피처 회귀 테스트

```
Track A 결과 키: ['SEC_LEADER_FLAG', 'RSI_14', 'BB_WIDTH', 'OBV_NEW_HIGH', 'V_RVOL', 'MA_ALIGNMENT', 'PRICE_POSITION_LAG1']
PASS: Track A 회귀 테스트
V3 총 피처 수: 30
PASS: V3 피처 목록 30개 확인
PASS: MarketRegimeEncoder 임포트 정상
PASS: SuperAntFactorExtractor 임포트 정상
전체 회귀 테스트 PASS
```

---

## 3. 피처 목록 업데이트

`feature_store.py`에 `V3_FEATURE_COLS` 상수 추가:

| 카테고리 | 피처 수 | 피처명 |
|---------|---------|-------|
| V1 (수급/재무/레짐) | 10개 | DUAL_FLOW_20D, SMALL_CAP_QUALITY, THEME_CYCLE_*, REGIME_Q1~Q4 |
| V1 (가격/거래량) | 5개 | CLOSE, VOL_20D_AVG, TRADE_AMT_20D_AVG, PRICE_RETURN_20D, PRICE_RETURN_5D |
| V2 Track A (일봉) | 7개 | SEC_LEADER_FLAG, RSI_14, BB_WIDTH, OBV_NEW_HIGH, V_RVOL, MA_ALIGNMENT, PRICE_POSITION_LAG1 |
| V2 Track B (분봉) | 2개 | VWAP_DEVIATION, VWAP_SUPPORT_COUNT |
| V2 뉴스 | 1개 | news_frequency_3d |
| **V3 교차 피처** | **3개** | BB_WIDTH_x_RSI, SEC_LEAD_x_RVOL, DUAL_x_Q2 |
| **V3 신규 피처** | **4개** | NEW_HIGH_52W_WITH_VOL, FORCE_ACC_5D, MKT_SEASON_MONTH, D_D1_D2_ENTRY |
| **합계** | **30개** | |

---

## 4. 수정 파일

| 파일 | 변경 내용 |
|------|---------|
| `backend/app/services/go100/ai/feature_engine.py` | V3 피처 함수 7개 추가 (274줄) |
| `backend/app/services/go100/ai/feature_store.py` | V3_FEATURE_COLS 정의, compute_v3_features 임포트 |

---

## 5. 다음 단계 (CEO 승인 후)

1. **배치 재빌드**: `build_feature_store_batch_v3.py` 작성 → 1년치 V3 피처 데이터셋 생성
2. **V3 모델 학습**: `train_ai_model_v3.py` — Regime 2분할 모델 (Q2 공격형 / 비Q2 방어형)
3. **Walk-Forward 검증**: AUC 0.58+ OR MFE_60MIN R² 0.65+ 목표

**참고 문서**: `CUR-GO100-P4-AI-ENHANCE-DESIGN-001-20260302.md`
