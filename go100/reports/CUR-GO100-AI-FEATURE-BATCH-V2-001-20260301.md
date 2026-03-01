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
| 피처 수 | 19 컬럼 | **34 컬럼** | +15 |
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

## 2. v2 신규 피처 상세

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

## 3. v2 라벨 다양화

### 기존 라벨 (v1 유지)

| 라벨 | 설명 | NaN 비율 |
|------|------|----------|
| LABEL_RETURN_5D | 5거래일 후 종가 수익률 (%) | 0.97% |
| LABEL_RETURN_10D | 10거래일 후 종가 수익률 (%) | 2.52% |
| LABEL_UP_5D | 5일 후 수익률 > 3% → 1 | 0.97% |

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

## 4. v1 결함 수정

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

## 5. 검증 결과

### REGIME_SEASON 분포

| 시즌 | 건수 | 비율 | 50% 경고 |
|------|------|------|----------|
| Q1 (봄/탐색) | 82,480 | 31.31% | - |
| Q2 (여름/공격) | 77,565 | 29.44% | - |
| Q3 (가을/경계) | 57,767 | 21.93% | - |
| Q4 (겨울/방어) | 45,638 | 17.32% | - |

**경고 없음** — 모든 시즌 50% 미만, 학습 데이터 균형 양호.

### 피처 NaN 비율

| 카테고리 | NaN 피처 수 | 비고 |
|----------|------------|------|
| 피처 (비라벨) | **0개** | 모든 피처 100% 채움 |
| 라벨 | 6개 (정상) | NaN = 미래 데이터 부족 기간 (정상) |

### valid_label 통계

- **유효**: 260,897건 (99.03%) — 학습 가능
- **무효**: 2,553건 (0.97%) — 기간 말미 자연 누락

---

## 6. 월별 파일 상세

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

## 7. 전체 컬럼 목록 (34개)

```
# 메타 (2)
ticker, target_date

# v1 피처 (9)
DUAL_FLOW_20D, SMALL_CAP_QUALITY,
THEME_CYCLE_100B_COUNT, THEME_CYCLE_UL_COUNT,
REGIME_Q1, REGIME_Q2, REGIME_Q3, REGIME_Q4,
REGIME_SEASON, REGIME_RAW

# v1 가격/기술 피처 (5)
CLOSE, VOL_20D_AVG, TRADE_AMT_20D_AVG,
PRICE_RETURN_20D, PRICE_RETURN_5D

# v2 Track A (7)
SEC_LEADER_FLAG, RSI_14, BB_WIDTH, OBV_NEW_HIGH,
V_RVOL, MA_ALIGNMENT, PRICE_POSITION_LAG1

# v2 Track B (2)
VWAP_DEVIATION, VWAP_SUPPORT_COUNT

# v2 뉴스 (1)
news_frequency_3d

# 라벨 (6 + 1 flag)
LABEL_RETURN_5D, LABEL_RETURN_10D, LABEL_UP_5D,
LABEL_GAP_D1, LABEL_MFE_60MIN, LABEL_MFE_3D,
valid_label
```

---

## 8. 수정 파일 목록

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `backend/app/services/go100/ai/feature_engine.py` | 수정 | Track A/B 계산함수 + news_frequency_3d 벌크 추가 |
| `scripts/go100/build_feature_store_batch_v2.py` | **신규** | v2 배치 빌드 스크립트 (v1 기반 확장) |
| `data/go100/features/v2/*.parquet` | **신규** | v2 파케이 12개 (263,450 rows, 26.24 MB) |
| `data/go100/features/v2/batch_build_v2_result.json` | **신규** | 빌드 결과 + 검증 JSON |

---

## 9. 실행 방법

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
