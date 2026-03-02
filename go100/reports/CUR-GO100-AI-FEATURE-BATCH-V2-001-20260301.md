# CUR-GO100-AI-FEATURE-BATCH-V2-001

> **GO100 AI Feature Store v2 배치 빌드**
> 작성일: 2026-03-01 | 작성자: Claude Opus 4.6

---

[인계 확인]
직전 완료: CUR-V41-CTE-PIPELINE-INTEGRATE-001
현재 단계: GO100 AI Feature Store v2 배치 빌드
CEO 지시 적용: D-001, D-008
strategy_cards: 42
open_positions: 14

---

## 1. 작업 요약

GO100 AI 백억이 Feature Store를 v1에서 v2로 업그레이드.
Track A (일봉 7피처) + Track B (분봉 2피처) + 뉴스 빈도 + 라벨 다양화 + v1 결함 수정.

### 핵심 결과

| 항목 | v1 | v2 | 변동 |
|------|-----|-----|------|
| 피처 수 | 20 컬럼 | **34 컬럼** | +14 |
| 라벨 수 | 3 (5D/10D/UP) | **6 + valid_label** | +4 |
| NaN 라벨 처리 | 0.0으로 대체 (버그) | **NaN 보존** | 결함 수정 |
| Z-score LABEL_ 제외 | 미적용 (버그) | **LABEL_ 접두사 제외** | 결함 수정 |
| 분봉 데이터 | 미사용 | **v4_ohlcv_minute 72.4M rows** | 신규 |
| 뉴스 데이터 | 미사용 | **go100_news_items 2.1M rows** | 신규 |
| 총 행 수 | 263,450 | **263,450** | 동일 |
| 총 파일 크기 | ~15 MB | **26.24 MB** | +74% |
| 소요 시간 | ~30분 | **29.4분** | 유사 |
| 오류 수 | - | **0** | - |

---

## 2. v1 vs v2 컬럼 비교표

| # | 컬럼명 | v1 | v2 | 변경사항 |
|---|--------|:--:|:--:|----------|
| 1 | ticker | O | O | — |
| 2 | target_date | O | O | — |
| 3 | DUAL_FLOW_20D | O | O | — |
| 4 | SMALL_CAP_QUALITY | O | O | — |
| 5 | THEME_CYCLE_100B_COUNT | O | O | — |
| 6 | THEME_CYCLE_UL_COUNT | O | O | — |
| 7 | REGIME_Q1 | O | O | — |
| 8 | REGIME_Q2 | O | O | — |
| 9 | REGIME_Q3 | O | O | — |
| 10 | REGIME_Q4 | O | O | — |
| 11 | REGIME_SEASON | O | O | — |
| 12 | REGIME_RAW | O | O | — |
| 13 | CLOSE | O | O | — |
| 14 | VOL_20D_AVG | O | O | — |
| 15 | TRADE_AMT_20D_AVG | O | O | — |
| 16 | PRICE_RETURN_20D | O | O | — |
| 17 | PRICE_RETURN_5D | O | O | — |
| 18 | LABEL_RETURN_5D | O | O | **v2: NaN 보존 (v1은 0.0 대체), Z-score 제외** |
| 19 | LABEL_RETURN_10D | O | O | **v2: NaN 보존 (v1은 0.0 대체), Z-score 제외** |
| 20 | LABEL_UP_5D | O | O | **v2: NaN 보존 (v1은 0→0.0→float), Z-score 제외** |
| 21 | SEC_LEADER_FLAG | — | **신규** | 당일 거래대금 상위 3% 섹터 리더 (0/1) |
| 22 | RSI_14 | — | **신규** | 14일 RSI (0~100) |
| 23 | BB_WIDTH | — | **신규** | 볼린저 밴드 폭 (20일, %) |
| 24 | OBV_NEW_HIGH | — | **신규** | OBV 신고가 여부 (0/1) |
| 25 | V_RVOL | — | **신규** | 상대 거래량 (당일/20일 평균) |
| 26 | MA_ALIGNMENT | — | **신규** | 이평선 정배열 (5>20>60→1, 역배열→-1) |
| 27 | PRICE_POSITION_LAG1 | — | **신규** | 전일 종가위치 (close-low)/(high-low) |
| 28 | VWAP_DEVIATION | — | **신규** | 종가의 VWAP 이탈률 (%), 분봉 기반 |
| 29 | VWAP_SUPPORT_COUNT | — | **신규** | 장중 VWAP 지지 횟수, 분봉 기반 |
| 30 | news_frequency_3d | — | **신규** | 최근 3영업일 뉴스 건수 |
| 31 | LABEL_GAP_D1 | — | **신규** | 익일 시가 갭 (%) |
| 32 | LABEL_MFE_60MIN | — | **신규** | 60분 MFE 장중 고가 최대 수익 (%) |
| 33 | LABEL_MFE_3D | — | **신규** | 3거래일 내 고가 기준 MFE (%) |
| 34 | valid_label | — | **신규** | 라벨 유효 플래그 (1=유효, 0=미래 부족) |

- **공통 유지**: 20개 (v1 전 컬럼 보존)
- **v2 신규**: 14개 (Track A 7 + Track B 2 + 뉴스 1 + 라벨 3 + valid_label 1)
- **v1 삭제**: 0개
- **동작 변경**: 3개 (LABEL_RETURN_5D/10D, LABEL_UP_5D — NaN 보존 + Z-score 제외)

---

## 3. v2 신규 피처 상세

### Track A — 일봉 기반 (7개)

| 피처 | 설명 | 타입 | 소스 |
|------|------|------|------|
| SEC_LEADER_FLAG | 당일 거래대금 상위 3% 섹터 리더 | 0/1 | ohlcv_daily |
| RSI_14 | 14일 RSI | 0~100 | ohlcv_daily |
| BB_WIDTH | 볼린저 밴드 폭 (20일, %) | float | ohlcv_daily |
| OBV_NEW_HIGH | OBV 신고가 여부 | 0/1 | ohlcv_daily |
| V_RVOL | 상대 거래량 (당일/20일 평균) | float | ohlcv_daily |
| MA_ALIGNMENT | 이평선 정배열 (5>20>60→1, 역배열→-1, 혼합→0) | -1/0/1 | ohlcv_daily |
| PRICE_POSITION_LAG1 | 전일 종가위치 (close-low)/(high-low) | 0~1 | ohlcv_daily |

### Track B — 분봉 기반 (2개)

| 피처 | 설명 | 타입 | 소스 |
|------|------|------|------|
| VWAP_DEVIATION | 종가의 VWAP 이탈률 (%) | float | v4_ohlcv_minute |
| VWAP_SUPPORT_COUNT | 장중 VWAP 지지 횟수 | int | v4_ohlcv_minute |

- 분봉 데이터 존재 기간: 2025-02-18 ~ 2026-02-27 (전 기간 커버)
- 분봉 없는 날: 일봉 fallback (typical price 기반 근사)

### 뉴스 (1개)

| 피처 | 설명 | 타입 | 소스 |
|------|------|------|------|
| news_frequency_3d | 최근 3영업일 뉴스 건수 | int | go100_news_items |

- CTE 최적화: stock_code1/2/3 UNION ALL 벌크 SQL

---

## 4. v2 라벨 다양화

### 기존 라벨 (v1 유지, 동작 변경)

| 라벨 | 설명 | NaN 비율 | v2 변경 |
|------|------|----------|---------|
| LABEL_RETURN_5D | 5거래일 후 종가 수익률 (%) | 0.97% | NaN 보존, Z-score 제외 |
| LABEL_RETURN_10D | 10거래일 후 종가 수익률 (%) | 2.52% | NaN 보존, Z-score 제외 |
| LABEL_UP_5D | 5일 후 수익률 > 3% → 1 | 0.97% | NaN 보존, Z-score 제외 |

### 신규 라벨 (v2)

| 라벨 | 설명 | NaN 비율 |
|------|------|----------|
| LABEL_GAP_D1 | 익일 시가 갭 (%) | 0.19% |
| LABEL_MFE_60MIN | 60분 MFE — 장중 고가 최대 수익 (%) | 0.00% |
| LABEL_MFE_3D | 3거래일 내 고가 기준 MFE (%) | 0.57% |

### valid_label 플래그

| 값 | 의미 | 건수 | 비율 |
|----|------|------|------|
| 1 | 유효 (5거래일 미래 존재) | 260,897 | 99.03% |
| 0 | 무효 (미래 데이터 부족) | 2,553 | 0.97% |

---

## 5. v1 결함 수정

### 결함 1: NaN 라벨 → 0.0 대체 (v1 버그)

**v1 코드** (`_compute_price_features` L436):
```python
def _ret(idx: int) -> float:
    if base_close > 0 and len(future) > idx:
        ...
    return 0.0  # ← 미래 없으면 0.0 (잘못됨)
```

**v2 수정** (`_compute_labels_v2`):
```python
def _ret(idx: int) -> float:
    if len(future) > idx:
        ...
    return float("nan")  # ← NaN 유지 (정확)
```

- **영향**: v1에서 학습 시 기간 말미 데이터가 "수익률 0%" 라벨로 학습됨
- **수정 후**: NaN → valid_label=0 → 학습 시 자동 제외 가능

### 결함 2: LABEL_ 컬럼 Z-score 적용 (v1 버그)

**v1 코드** (`_zscore_batch` L113):
```python
float_keys = [k for k, v in records[0].items()
    if isinstance(v, float) and k not in SKIP_ZSCORE_KEYS]
# LABEL_RETURN_5D 등이 float이므로 Z-score 적용됨 (잘못됨)
```

**v2 수정** (`_zscore_batch_v2`):
```python
float_keys = [k for k, v in records[0].items()
    if isinstance(v, float) and not _should_skip_zscore(k)]
# _should_skip_zscore: LABEL_ 접두사 동적 제외
```

- **영향**: v1에서 라벨이 월별 Z-score로 변환되어 원래 수익률 의미 상실
- **수정 후**: 라벨은 원래 % 값 그대로 유지

---

## 6. REGIME별 Positive Rate 검증

> 강세장 구간의 Positive rate 편향 진단 (valid_label=1 기준, N=260,897)

### 6-1. REGIME_SEASON별 LABEL_UP_5D Positive Rate

| 시즌 | 건수 | LABEL_UP_5D=1 | Positive Rate | 50% 경고 |
|------|------|---------------|---------------|----------|
| Q1 (봄/탐색) | 82,480 | 24,917 | 30.22% | - |
| Q2 (여름/공격) | 77,565 | 20,466 | 26.39% | - |
| Q3 (가을/경계) | 55,214 | 14,714 | 26.65% | - |
| Q4 (겨울/방어) | 45,638 | 17,124 | **37.52%** | - |

**진단**: LABEL_UP_5D 전 시즌 50% 미만 — **경고 없음**. Q4(겨울/방어)가 37.52%로 최고이나 이는 2026-01~02 반등장 영향. 전체적으로 양성률 26~38% 범위로 모델 과적합 리스크 낮음.

### 6-2. REGIME_SEASON별 LABEL_MFE_3D > 3% Positive Rate

| 시즌 | 건수 | MFE_3D > 3% | Positive Rate | 50% 경고 |
|------|------|-------------|---------------|----------|
| Q1 (봄/탐색) | 82,480 | 41,267 | **50.03%** | **WARNING** |
| Q2 (여름/공격) | 77,565 | 36,195 | 46.67% | - |
| Q3 (가을/경계) | 55,214 | 24,294 | 44.00% | - |
| Q4 (겨울/방어) | 45,638 | 24,237 | **53.11%** | **WARNING** |

**진단**: LABEL_MFE_3D > 3% 기준으로 Q1(50.03%)과 Q4(53.11%)에서 50% 초과 경고 발생.
- Q1(봄): 50.03%로 경계선. SIDEWAYS 레짐에서 3일 내 3% 돌파가 빈번 — 변동성이 높은 탐색기 특성.
- Q4(겨울): 53.11%. 2026-01~02 반등장이 Q4로 분류되면서 MFE가 높게 나옴.
- **조치 권고**: MFE_3D 라벨로 학습 시 REGIME 피처를 반드시 포함하여 시즌별 기저율 차이를 모델이 학습하도록 할 것. 또는 REGIME-stratified sampling 적용 검토.

---

## 7. 월별 Positive Rate 추이

> 강세장 과적합 위험 진단: 2025-03~04(시장 활황, 행 수 최다)와 하반기 비교

| 월 | 행 수 | UP_5D Pos% | MFE_3D>3% Pos% | GAP_D1 평균 | 비고 |
|----|-------|-----------|----------------|-------------|------|
| 2025-03 | 48,025 | **15.90%** | 36.38% | -0.046% | 시장 조정기, 최저 양성률 |
| 2025-04 | 55,149 | 34.56% | 48.11% | +0.210% | 행 수 최다, 활황기 |
| 2025-05 | 22,835 | 31.67% | 49.70% | +0.361% | |
| 2025-06 | 14,323 | 32.66% | **56.51%** | +0.506% | MFE 고점 |
| 2025-07 | 16,379 | 23.77% | 42.27% | +0.214% | 하락 전환 |
| 2025-08 | 13,561 | 23.86% | 42.70% | +0.177% | |
| 2025-09 | 15,817 | 32.97% | 48.23% | +0.400% | 반등 |
| 2025-10 | 14,048 | 34.33% | **56.87%** | +0.438% | MFE 최고 |
| 2025-11 | 15,254 | 27.92% | 51.48% | +0.215% | |
| 2025-12 | 16,003 | 29.48% | 48.78% | +0.314% | |
| 2026-01 | 18,864 | **40.62%** | **60.74%** | +0.412% | 연초 강세 |
| 2026-02 | 10,639 | **45.39%** | **66.67%** | +0.633% | 최근월 최고 양성률 |

### 편향 진단

**LABEL_UP_5D**:
- 범위: 15.90% (2025-03) ~ 45.39% (2026-02) — **2.85배 차이**
- 2025-03이 극단적으로 낮은 이유: 이 시기 시장 조정(행 수 48,025로 최다이나 양성률 최저)
- 2026-01~02 최근 2개월이 40%+ — **최근 편향(recency bias) 주의 필요**

**LABEL_MFE_3D>3%**:
- 범위: 36.38% (2025-03) ~ 66.67% (2026-02) — **1.83배 차이**
- 2025하반기(42~57%)와 2026-01~02(60~67%) 간 뚜렷한 격차
- **조치 권고**: 학습 시 시간 가중치(time-weighted) 또는 월별 stratified sampling 적용 검토. 특히 2026-02 데이터(10,639건, 전체 4%)가 양성률 66.67%로 과대 영향을 줄 수 있으므로 holdout 분리 권장.

**GAP_D1 평균**:
- 2025-03만 음수(-0.046%), 나머지 전부 양수(+0.177~+0.633%)
- **갭 상승 편향 존재** — GAP_D1 라벨 학습 시 시장 국면 보정 필요

---

## 8. 검증 결과

### 피처 NaN 비율

| 카테고리 | NaN 피처 수 | 비고 |
|----------|------------|------|
| 피처 (비라벨) | **0개** | 모든 피처 100% 채움 |
| 라벨 | 6개 (정상) | NaN = 미래 데이터 부족 기간 (정상) |

### 라벨별 NaN 상세

| 라벨 | NaN 건수 | NaN 비율 | 사유 |
|------|----------|----------|------|
| LABEL_RETURN_5D | 2,553 | 0.97% | 기간 말미 5거래일 미래 부족 |
| LABEL_RETURN_10D | 6,647 | 2.52% | 기간 말미 10거래일 미래 부족 |
| LABEL_UP_5D | 2,553 | 0.97% | LABEL_RETURN_5D와 동일 |
| LABEL_GAP_D1 | 499 | 0.19% | 기간 최종일(20260227) 익일 없음 |
| LABEL_MFE_60MIN | 0 | 0.00% | 당일 데이터로 계산 (미래 불필요) |
| LABEL_MFE_3D | 1,511 | 0.57% | 기간 말미 3거래일 미래 부족 |

### valid_label 통계

- **유효**: 260,897건 (99.03%) — 학습 가능
- **무효**: 2,553건 (0.97%) — 기간 말미 자연 누락

---

## 9. 월별 파일 상세

| 월 | 파일명 | Rows | MB |
|----|--------|------|----|
| 202503 | ai_dataset_v2_202503.parquet | 48,025 | 4.33 |
| 202504 | ai_dataset_v2_202504.parquet | 55,149 | 4.96 |
| 202505 | ai_dataset_v2_202505.parquet | 22,835 | 2.31 |
| 202506 | ai_dataset_v2_202506.parquet | 14,323 | 1.57 |
| 202507 | ai_dataset_v2_202507.parquet | 16,379 | 1.66 |
| 202508 | ai_dataset_v2_202508.parquet | 13,561 | 1.44 |
| 202509 | ai_dataset_v2_202509.parquet | 15,817 | 1.70 |
| 202510 | ai_dataset_v2_202510.parquet | 14,048 | 1.54 |
| 202511 | ai_dataset_v2_202511.parquet | 15,254 | 1.66 |
| 202512 | ai_dataset_v2_202512.parquet | 16,003 | 1.70 |
| 202601 | ai_dataset_v2_202601.parquet | 18,864 | 2.01 |
| 202602 | ai_dataset_v2_202602.parquet | 13,192 | 1.36 |
| **합계** | **12 파일** | **263,450** | **26.24** |

---

## 10. 수정 파일 목록

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `backend/app/services/go100/ai/feature_engine.py` | 수정 | Track A/B 계산함수 + news_frequency_3d 벌크 추가 |
| `scripts/go100/build_feature_store_batch_v2.py` | **신규** | v2 배치 빌드 스크립트 (v1 기반 확장) |
| `data/go100/features/v2/*.parquet` | **신규** | v2 Parquet 12개 (263,450 rows, 26.24 MB) |
| `data/go100/features/v2/batch_build_v2_result.json` | **신규** | 빌드 결과 + 검증 JSON |

---

## 11. 실행 방법

```bash
# 전체 빌드 (기본: 2025-03-01 ~ 2026-02-28)
.venv/bin/python scripts/go100/build_feature_store_batch_v2.py

# 기간/파라미터 지정
.venv/bin/python scripts/go100/build_feature_store_batch_v2.py \
    --start 20250301 --end 20260228 \
    --min-amount 5000000000 --semaphore 40

# 결과 확인
cat data/go100/features/v2/batch_build_v2_result.json | python -m json.tool
```

---

## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-AI-FEATURE-BATCH-V2-001-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-AI-FEATURE-BATCH-V2-001-20260301.md
- 코드 레포 커밋: `bc87f209` (kis-autotrade-v4, branch: phase-2c-command-center)
- 문서 레포 커밋: `d25706a` (project-docs, branch: master)
- HTTP 확인: 200
- HANDOVER 업데이트: 완료 (v4.6, d25706a)
