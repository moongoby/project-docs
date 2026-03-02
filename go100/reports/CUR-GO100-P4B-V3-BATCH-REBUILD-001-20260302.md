# Phase 4-B V3 피처 배치 재빌드 보고서

**파일명**: CUR-GO100-P4B-V3-BATCH-REBUILD-001-20260302.md  
**작성일**: 2026-03-02  
**작성자**: [CURSOR-GO100]  
**지시 출처**: DIRECTIVE `CUR-GO100-P4B-V3-BATCH-REBUILD-001` (GO100 지휘관 자체 승인)  
**커밋**: `14da20dd` (kis-autotrade-v4 — V3 배치 스크립트)

---

## 요약

| 항목 | 결과 |
|------|------|
| V3 배치 스크립트 작성 | PASS (`build_feature_store_batch_v3.py`) |
| 1일치 테스트 | PASS (2026-02-27, 498종목, 경고 0건) |
| 1년치 배치 실행 | 진행 중 (PID: 1672851) |
| 예상 총 레코드 | ~250,000~600,000건 (242일 × 500~2500종목) |
| 출력 경로 | `data/go100/features/v3/` |

---

## 1. 배치 스크립트 (`build_feature_store_batch_v3.py`)

### V2 대비 변경 사항

| 구분 | 변경 내용 |
|------|----------|
| 피처 추가 | V3 교차피처 3개 + 신규피처 4개 = 7개 |
| DB 쿼리 추가 | `_fetch_investor_bulk()` — 기관+외인 순매수 5일 데이터 |
| 피처 함수 | `compute_v3_features()` 통합 호출 |
| 출력 경로 | `data/go100/features/v3/ai_dataset_v3_YYYYMM.parquet` |
| Z-score 제외 | V3 이진 피처 추가 (NEW_HIGH_52W_WITH_VOL, D_D1_D2_ENTRY, SEC_LEAD_x_RVOL) |

### 총 피처 수: 30개 (V2 23개 + V3 7개)

---

## 2. 1일치 테스트 결과 (2026-02-27)

```
총 레코드: 498
총 컬럼: 41
소요시간: 14.9초
경고: 0건

V3 피처 통계:
  BB_WIDTH_x_RSI  : mean=-0.0000, std=1.0010, nan=0.0% (z-score 정상)
  SEC_LEAD_x_RVOL : mean=0.0542, std=0.3895, nan=0.0% (5.42% 섹터리더×거래량폭발)
  DUAL_x_Q2       : mean=-0.0000, std=1.0010, nan=0.0% (z-score 정상)
  NEW_HIGH_52W_W  : mean=0.0341, nan=0.0% (3.41% 발생률 — T-001)
  FORCE_ACC_5D    : mean=-0.0000, std=1.0010, nan=0.0% (z-score 정상)
  MKT_SEASON_MONTH: mean=0.0000, std=0.0000, nan=0.0% (2월 단일 sin값)
  D_D1_D2_ENTRY   : mean=0.0703, nan=0.0% (7.03% 발생률)

T-001 NEW_HIGH_52W_WITH_VOL 발생률: 3.41%
```

---

## 3. 1년치 배치 실행 상태

```
실행 시작: 2026-03-02 20:54:38 KST
기간: 2025-03-01 ~ 2026-02-27 (242 거래일)
PID: 1672851
로그: /var/log/go100/v3_batch_build.log

Day 1 (20250304): 2520종목, 분봉:Y, 소요 약 32초
THEME_CYCLE 캐시: 3579종목
```

> **상태**: 진행 중 (백그라운드). 완료 후 CEO에게 별도 보고 예정.

---

## 4. 수정 이력 (버그 수정)

배치 스크립트 작성 중 다음 버그를 수정했습니다:

| 이슈 | 원인 | 수정 |
|------|------|------|
| THEME_CYCLE 'cntUL' 오류 | FILTER 구문 → CASE WHEN으로 변경, 컬럼명 표준화 | `cnt_100b`, `cnt_ul` 사용 |
| investor 컬럼명 오류 | `institution_net_buy` → `institution_net_qty` | DB 실제 컬럼 반영 |
| dual_flow 날짜 오류 | 문자열 date를 그대로 전달 | `target_date` (date 객체) 사용 |
| regime 컬럼명 오류 | `regime_type` → `regime` | v4_market_regime_daily 실제 컬럼 반영 |
| minute data 날짜 오류 | 문자열 → date 객체 변환 | `target_date` (date 객체) 전달 |

---

## 5. 다음 단계

1. **배치 완료 후**: 결과 검증 (`build_v3_result.json`) → 보고
2. **P4-C**: V3 모델 학습 (`train_ai_model_v3.py`)
   - Regime 2분할: Q2 공격형 vs 비Q2 방어형
   - 목표: AUC 0.58+, MFE_60MIN R² 0.65+

---

**참고 문서**: `CUR-GO100-P4-AI-ENHANCE-DESIGN-001-20260302.md`
