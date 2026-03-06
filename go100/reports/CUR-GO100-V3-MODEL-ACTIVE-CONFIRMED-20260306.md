---
project: go100
task_id: GO100-V3-STATUS-CHECK
completed_at: 2026-03-06 11:10 KST
status: completed
title: "GO100 V3 모델 정상 가동 확인"
author: Claude Code (Sonnet 4.6) / root
---

# ✅ GO100 V3 모델 정상 가동 확인 (2026-03-06)

> 점검일시: 2026-03-06 10:50~11:10 KST
> 결론: **V3 모델 정상 활성 및 실시간 예측 작동 중**

---

## 가동 상태 요약

| 항목 | 상태 |
|------|------|
| V3 모델 활성 플래그 (`active`) | ✅ `true` |
| 모델 파일 로드 (`_models_loaded`) | ✅ `True` |
| 예측 엔진 활성 (`_is_active`) | ✅ `True` |
| bridge/score API 응답 | ✅ `200 OK / model_version: v3` |
| go100 서비스 (port 8002) | ✅ active (running) |

---

## 모델 구성

- **훈련 완료**: 2026-03-02 22:18 KST
- **활성화**: 2026-03-03 (CEO 승인: DIR-GO100-V3-ACTIVATE-001-R3)
- **학습 데이터**: 307,608건 (2025-03 ~ 2026-02, 12개 파티션)
- **특성 수**: 30개 (V3 신규 7개 포함)
- **검증 방식**: Walk-Forward 3-Fold

---

## 분류기 성능 (AUC)

| 모델 | AUC | V2 대비 |
|------|-----|---------|
| unified (통합) | 0.5656 | +0.0250 ↑ |
| **Q2_aggressive** | **0.6092** | 최우수 |
| nonQ2_defensive | 0.5588 | +0.0182 ↑ |

> V2 baseline AUC: 0.5406 — V3 전 모델 상회 확인

---

## 실시간 예측 테스트 결과

**테스트 종목: 005930 삼성전자 (Q2 레짐)**

```json
{
  "status": "ok",
  "ticker": "005930",
  "cs_ai": 81,
  "up_5d_prob": 0.4797,
  "mfe_60min_raw": 3.652,
  "mfe_3d_raw": 9.3028,
  "gap_d1_raw": 0.5744,
  "model_version": "v3",
  "elapsed_ms": 1726
}
```

---

## 레짐별 EDA

| 레짐 | 양성 비율 | 샘플 수 |
|------|---------|---------|
| Q1 | 27.59% | 99,906 |
| **Q2** | 26.97% | 144,522 |
| Q3 | 41.47% | 45,083 |
| Q4 | 28.96% | 15,550 |

---

## 모델 파일 목록

| 파일 | 크기 |
|------|------|
| clf_unified.joblib | 82 KB |
| clf_q2_aggressive.joblib | 88 KB |
| clf_nonq2_defensive.joblib | 39 KB |
| reg_mfe_60min_unified.joblib | 1.5 MB |
| reg_mfe_3d_unified.joblib | 980 KB |
| reg_gap_d1_unified.joblib | 281 KB |

---

## 결론

GO100 V3 모델은 **2026-03-03 활성화 이후 현재(03-06)까지 정상 가동 중**입니다.
bridge/score API를 통해 실시간 예측이 정상 수행되며, V2 대비 AUC 성능 향상이 확인됩니다.
추가 조치 없이 현행 운영 지속 권장합니다.
