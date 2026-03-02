# [GO100] AI 백억이 피처 엔지니어링 파이프라인 및 Feature Store 구축 완료 보고서

> 작업일: 2026-03-01
> 작업자: Claude Sonnet 4.6
> 프로젝트: GO100 (go100.newtalk.kr)
> 작업 분류: Phase 4 — AI 학습 데이터 인프라
> 커밋: `88be3e74`

---

## 1. 작업 개요

AI 에이전트 백억이(GO100)가 딥러닝/강화학습 모델 훈련에 즉시 사용할 수 있도록,
Raw DB 데이터를 정제하여 Feature와 Label로 변환하는 **자동화 파이프라인(Feature Store)**을 구축하였다.

D-008-KR 슈퍼개미 전략 변수(P0 우선순위)를 완전 구현하였으며,
5개 샘플 종목에 대한 E2E 테스트를 통과하였다.

---

## 2. 구현 결과

### Task A — Feature Engineering 모듈

**파일:** `backend/app/services/go100/ai/feature_engine.py` (신규)

#### 2-A-1. `SuperAntFactorExtractor` 클래스

| 피처명 | 설명 | 데이터 소스 | 근거 |
|--------|------|-------------|------|
| `DUAL_FLOW_20D` | 최근 20일 기관+외국인 쌍끌이 순매수 비율 (0.0~1.0) | `v4_investor_daily` | 이정윤 / IBD Acc Rating |
| `SMALL_CAP_QUALITY` | 소형주 우량 필터: 시총 700억↓ + 영업이익 흑자 + 자본총계>0 → (0/1) | `stock_fundamentals`, `go100_fundamentals_pit` | 시간여행TV 5대 조건 |
| `THEME_CYCLE_100B_COUNT` | 과거 3년 일 거래대금 100억+ 돌파 횟수 | `ohlcv_daily` | 시간여행TV "고기도 먹어본 놈이" |
| `THEME_CYCLE_UL_COUNT` | 과거 3년 상한가(+29%↑) 발생 횟수 | `ohlcv_daily` (LAG 윈도우) | 홍인기 "상한가도 가본 놈이" |

#### 2-A-2. `MarketRegimeEncoder` 클래스

코스닥 시장 레짐을 남석관 사계절론에 따라 Q1~Q4 One-hot 인코딩:

| DB 레짐값 | 사계절 | 의미 |
|-----------|--------|------|
| `STRONG_TREND_UP` | Q2 (여름) | 공격 ×1.2 |
| `MILD_TREND_UP` | Q2 (여름) | 공격 ×1.2 |
| `SIDEWAYS` | Q1 (봄) | 탐색 |
| `MILD_TREND_DOWN` | Q3 (가을) | 경계 ×0.9 |
| `STRONG_TREND_DOWN` | Q4 (겨울) | 방어 ×0.7 |

반환 키: `REGIME_Q1`, `REGIME_Q2`, `REGIME_Q3`, `REGIME_Q4`, `REGIME_SEASON`, `REGIME_RAW`

#### 2-A-3. 수치형 유틸

| 함수 | 설명 |
|------|------|
| `fill_nan(value, fill=0.0)` | NaN/None/Inf → fill 대체 |
| `zscore_normalize(values)` | 배열 단위 Z-score 정규화 (σ=0이면 전부 0) |
| `normalize_feature_dict(features)` | 딕셔너리 내 수치형 NaN 클리닝 |

---

### Task B — Feature Store 로직

**파일:** `backend/app/services/go100/ai/feature_store.py` (신규)

#### 2-B-1. `FeatureStoreBuilder.build()` 파이프라인

입력: `(db: AsyncSession, ticker: str, target_date: date)`
출력: 20컬럼 딕셔너리 `(Features_X, Label_Y)`

```
Features_X:
  DUAL_FLOW_20D, SMALL_CAP_QUALITY,
  THEME_CYCLE_100B_COUNT, THEME_CYCLE_UL_COUNT,
  REGIME_Q1/Q2/Q3/Q4, REGIME_SEASON, REGIME_RAW,
  CLOSE, VOL_20D_AVG, TRADE_AMT_20D_AVG,
  PRICE_RETURN_20D, PRICE_RETURN_5D

Label_Y:
  LABEL_RETURN_5D   — 기준일 대비 5거래일 후 수익률(%)
  LABEL_RETURN_10D  — 기준일 대비 10거래일 후 수익률(%)
  LABEL_UP_5D       — 5일 후 수익률 > 3% → 1, 아니면 0 (이진 분류)
```

#### 2-B-2. `FeatureStoreBuilder.export()` — Parquet / JSONL 저장

- 저장 경로: `data/go100/features/ai_dataset_YYYYMMDD.parquet`
- Parquet 실패 시 `ai_dataset_YYYYMMDD.jsonl` 자동 fallback
- pandas + pyarrow 사용 (pyarrow 23.0.1 설치 완료)

#### 2-B-3. `FeatureStoreBuilder.apply_zscore_batch()` — 배치 Z-score

여러 종목 레코드에 걸쳐 각 연속형 피처의 Z-score 정규화 적용.
One-hot / 카테고리 / 카운트 키는 자동 제외.

---

### Task C — E2E 테스트 스크립트

**파일:** `scripts/go100/test_feature_pipeline.py` (신규)

**실행:**
```bash
.venv/bin/python scripts/go100/test_feature_pipeline.py --date 20260220 --fmt parquet --zscore
```

---

## 3. E2E 테스트 출력 로그 (2026-02-20 기준, 5종목)

### 3-1. Raw 피처 (Z-score 미적용)

```
2026-03-01 13:18:35 [INFO] GO100 Feature Pipeline E2E 테스트 시작
2026-03-01 13:18:35 [INFO] 기준일: 2026-02-20 | 포맷: parquet | Z-score: False
[ 005930 / 삼성전자  ] ✓ DF20D=0.3500 SCQ=0 100B=729 UL=0 SEASON=Q3 CLOSE=190100 R20D=27.16% LBL5D=1
[ 000660 / SK하이닉스 ] ✓ DF20D=0.3500 SCQ=0 100B=729 UL=0 SEASON=Q3 CLOSE=949000 R20D=28.24% LBL5D=1
[ 068270 / 셀트리온  ] ✓ DF20D=0.6000 SCQ=0 100B=729 UL=0 SEASON=Q3 CLOSE=242000 R20D=18.63% LBL5D=0
[ 086520 / 에코프로  ] ✓ DF20D=0.5000 SCQ=0 100B=718 UL=1 SEASON=Q3 CLOSE=171300 R20D=80.13% LBL5D=1
[ 005490 / 포스코홀딩스] ✓ DF20D=0.4000 SCQ=0 100B=729 UL=0 SEASON=Q3 CLOSE=394000 R20D=12.25% LBL5D=1
검증 OK — Parquet rows=5 cols=20 size=12.5KB
E2E 테스트 완료 — PASS
```

### 3-2. Feature Set 요약 테이블 (Raw)

```
=========================================================================================
TICKER   DATE          DF20D  SCQ  100B   UL SEASON    CLOSE    R20D     L5D    L10D  UP5
-----------------------------------------------------------------------------------------
005930   2026-02-20    0.350    0   729    0 Q3       190100   27.16   13.89    0.00    1
000660   2026-02-20    0.350    0   729    0 Q3       949000   28.24   11.80    0.00    1
068270   2026-02-20    0.600    0   729    0 Q3       242000   18.63   -1.45    0.00    0
086520   2026-02-20    0.500    0   718    1 Q3       171300   80.13    8.00    0.00    1
005490   2026-02-20    0.400    0   729    0 Q3       394000   12.25    4.82    0.00    1
=========================================================================================
```

### 3-3. Feature Set 요약 테이블 (배치 Z-score 적용)

```
=========================================================================================
TICKER   DATE          DF20D  SCQ  100B   UL SEASON    CLOSE    R20D     L5D    L10D  UP5
-----------------------------------------------------------------------------------------
005930   2026-02-20   -0.928    0   729    0 Q3           -1   -0.25    1.20    0.00    1
000660   2026-02-20   -0.928    0   729    0 Q3            2   -0.21    0.81    0.00    1
068270   2026-02-20    1.650    0   729    0 Q3           -1   -0.61   -1.64    0.00    0
086520   2026-02-20    0.619    0   718    1 Q3           -1    1.94    0.11    0.00    1
005490   2026-02-20   -0.413    0   729    0 Q3            0   -0.87   -0.48    0.00    1
=========================================================================================
```

### 3-4. 피처 해석 (2026-02-20 시장 맥락)

| 항목 | 관찰 | 해석 |
|------|------|------|
| REGIME_SEASON | Q3 (가을/경계) | 코스닥 MILD_TREND_DOWN — 남석관 경계 구간 |
| DUAL_FLOW_20D | 0.35~0.60 | 셀트리온(0.60)이 기관·외국인 동반 매수 가장 강함 |
| SMALL_CAP_QUALITY | 전종목 0 | 대형주(시총 700억 초과) — 소형주 필터 미해당 |
| THEME_CYCLE_100B_COUNT | 718~729회 | 3년간 거의 매일 100억 초과 거래 = 유동성 최상급 |
| THEME_CYCLE_UL_COUNT | 에코프로만 1회 | 에코프로 과거 상한가 이력 있음 (테마 반복성 O) |
| PRICE_RETURN_20D | 에코프로 80.13% | 20일 최강 상승 — 급등 주도주 |
| LABEL_UP_5D | 에코프로·삼성전자·하이닉스·포스코 = 1 | 5일 후 +3%↑ 달성 (셀트리온만 0) |
| LABEL_RETURN_10D | 전종목 0.00 | DB 미래 데이터가 2026-02-27까지만 존재 → 10D 라벨 결측 |

---

## 4. 파일 목록

| 파일 | 유형 | 크기 |
|------|------|------|
| `backend/app/services/go100/ai/feature_engine.py` | 신규 | ~230줄 |
| `backend/app/services/go100/ai/feature_store.py` | 신규 | ~260줄 |
| `scripts/go100/test_feature_pipeline.py` | 신규 | ~160줄 |
| `data/go100/features/ai_dataset_20260220.parquet` | 생성 | 12.5KB (5rows × 20cols) |

---

## 5. 기술 스택

- Python 3.12 + asyncio
- SQLAlchemy 2.0 (AsyncSession)
- pandas 3.0.1 + pyarrow 23.0.1 (Parquet I/O)
- numpy 2.2.6 (Z-score 계산)
- PostgreSQL 16 (`kisautotrade` DB)

---

## 6. 다음 단계 (P1 구현 예정)

| 우선순위 | 피처 | 설명 |
|----------|------|------|
| P1 | `MKT_SEASON` 가중치 | Q2 ×1.2, Q4 ×0.7 DESK2 배분 연동 |
| P1 | `FORCE_ACC` (세력 매집) | 120일선 수렴도 + 급등봉 횟수 |
| P1 | `D_D1_D2_ENTRY` | 홍인기 장대양봉 타점 |
| P2 | `BJ_SCORE` | 배진한 5원칙 정량화 (100점) |
| P2 | `KJH_CYCLE` | 김정환 매출·영업이익 5년 우상향 |
| 확장 | 다중 날짜 배치 빌드 | 과거 1년치 학습 데이터셋 자동 생성 크론 |

---

## [REPORT-001] 검증 체크리스트

| 항목 | 결과 |
|------|------|
| 코드 레포 커밋 | ✓ SHA: `88be3e74` |
| 커밋 메시지 prefix | ✓ `[GO100]` |
| feature_engine.py 생성 | ✓ `backend/app/services/go100/ai/feature_engine.py` |
| feature_store.py 생성 | ✓ `backend/app/services/go100/ai/feature_store.py` |
| test_feature_pipeline.py 생성 | ✓ `scripts/go100/test_feature_pipeline.py` |
| E2E 테스트 결과 | ✓ PASS (5/5 종목) |
| Parquet 저장 | ✓ `data/go100/features/ai_dataset_20260220.parquet` (12.5KB) |
| D-008-KR P0 변수 구현 | ✓ DUAL_FLOW_20D, SMALL_CAP_QUALITY, THEME_CYCLE |
| 문서 레포 보고서 저장 | ✓ `go100/reports/CUR-GO100-AI-FEATURE-PIPELINE-001-20260301.md` |
| 문서 레포 커밋+푸시 | → 진행 중 |
| HTTP 200 확인 (go100.newtalk.kr) | N/A (신규 라우터 미등록 — AI 내부 모듈) |
| HANDOVER.md 업데이트 | → 진행 중 |
| V4.1 파일 수정 여부 | ✗ (없음 — 서비스 경계 준수) |
