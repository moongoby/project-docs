# CUR-V41-AI-SCORING-ZSCORE-HOTFIX-001 보고서
> 작성일: 2026-03-01
> 실행: Claude Code (claude-sonnet-4-6)
> 태스크: AI Scorer Z-score 이중 적용 긴급 핫픽스

---

[인계 확인]
직전 완료: CUR-V41-AI-SCORING-INTEGRATION-001
현재 단계: GO100 AI 스코어링 Shadow 모드 (w=0.15)
CEO 지시 적용: D-001(복합 분석), D-007(컨텍스트 패키지)
strategy_cards: 60
open_positions: 14

---

## 1. 문제 요약

`CUR-V41-AI-SCORING-INTEGRATION-001` 보고서에서 삼성전자(005930) `cs_ai=100`,
`mfe_60min_raw=4.87`, `mfe_3d_raw=9.21`로 Bounds 상한에 근접. 분포 왜곡 원인 분석 착수.

---

## 2. 진단 결과 — Case A 확정

### 2-a) feature_stats.json 확인

```
DUAL_FLOW_20D: mean=-0.0000, std=1.0000   ← Z-score된 데이터의 통계 (확정)
CLOSE:         mean=-0.0000, std=1.0000   ← Z-score된 데이터의 통계 (확정)
RSI_14:        mean=-0.0000, std=1.0000   ← Z-score된 데이터의 통계 (확정)
THEME_CYCLE_100B_COUNT: mean=175.07, std=184.64  ← raw (SKIP_ZSCORE_KEYS)
news_frequency_3d:      mean=5.17,   std=16.49   ← raw (int형으로 인해 Z-score 미적용)
```

**판정: mean≈0, std≈1 → Z-score된 Parquet 데이터 기반 통계 → 이중 적용 확정**

### 2-b) Parquet 실제 값 확인

```
CLOSE:         mean=0.0000, std=1.0000  ← 월별 Z-score 저장 확인
DUAL_FLOW_20D: mean=-0.0000, std=1.0000
RSI_14:        mean=-0.0000, std=1.0000
BB_WIDTH:      mean=0.0000, std=1.0000
VOL_20D_AVG:   mean=-0.0000, std=1.0000
THEME_CYCLE_100B_COUNT: mean=175.07 ← raw (SKIP_ZSCORE_KEYS)
```

**Case A 확정**: Parquet에 Z-score된 값 저장 + feature_stats.json이 Z-score된 데이터의 통계

### 2-c) 이중 적용 메커니즘

```
배치 빌드(_zscore_batch_v2):
  raw_CLOSE=75000 → (75000-month_mean)/month_std → z_CLOSE≈0

feature_stats.json 생성 (Integration-001 커밋 e2ac566d):
  "263,450행 파케이 기반 생성" → Z-score된 데이터에서 통계 계산
  → CLOSE: mean=0.0, std=1.0

ai_scorer.py Stage 2 Z-score:
  z = (raw_CLOSE - 0) / 1 = raw_CLOSE = 75000  ← 원시값 그대로 전달
  (모델 기대값: -0.3 ~ +15 범위의 Z-score)
  → 모델이 학습 시 본 적 없는 극단값 수신 → cs_ai=0 or 100 편향
```

---

## 3. 수정 내용

**방법**: 원시 피처 기준 통계를 DB 직접 조회로 재계산하여 feature_stats.json 교체

**대상 데이터**: 대표 500종목 × 9개월 (20250601~20260228)

### 3-a) feature_stats.json 수정 전 vs 후

| 피처 | 이전 mean | 이전 std | 수정 후 mean | 수정 후 std | 비고 |
|------|-----------|----------|-------------|-------------|------|
| CLOSE | 0.0000 | 1.0000 | 66,413.06 | 131,187.52 | 원시 주가 |
| DUAL_FLOW_20D | -0.0000 | 1.0000 | 0.1971 | 0.1509 | 동반수급 비율 |
| RSI_14 | -0.0000 | 1.0000 | 53.5873 | 17.2422 | RSI 원시 |
| BB_WIDTH | 0.0000 | 1.0000 | 10.7716 | 9.8085 | BB 폭 % |
| VOL_20D_AVG | -0.0000 | 1.0000 | 1,306,874 | 4,579,292 | 20일 평균 거래량 |
| TRADE_AMT_20D_AVG | 0.0000 | 1.0000 | 8.29T | 37.2T | 20일 평균 거래대금 |
| PRICE_RETURN_20D | 0.0000 | 1.0000 | 7.5836 | 28.7983 | 20일 수익률 |
| PRICE_RETURN_5D | 0.0000 | 1.0000 | 1.5779 | 8.6772 | 5일 수익률 |
| V_RVOL | 0.0000 | 1.0000 | 1.2434 | 4.1031 | 상대 거래량 |
| PRICE_POSITION_LAG1 | -0.0000 | 1.0000 | 0.4843 | 0.2965 | 전일 종가위치 |
| VWAP_DEVIATION | 0.0000 | 1.0000 | -0.0366 | 1.1564 | VWAP 이격 % |
| VWAP_SUPPORT_COUNT | -0.0000 | 1.0000 | 2.0 (추정) | 3.0 (추정) | 분봉 fallback |
| THEME_CYCLE_100B_COUNT | 175.0701 | 184.6433 | 유지 | 유지 | SKIP_ZSCORE_KEYS |
| news_frequency_3d | 5.1716 | 16.4858 | 유지 | 유지 | raw 저장 |
| REGIME_Q1~Q4, MA_ALIGNMENT 등 | 유지 | 유지 | 유지 | 유지 | 비연속형 |

**수정 파일**: `data/go100/models/go100_brain_v2_feature_stats.json`
**백업**: `data/go100/models/go100_brain_v2_feature_stats.json.bak_20260301`

---

## 4. 검증 결과

### 4-a) 3종목 재스코어링 (수정 전 vs 수정 후)

| 종목 | 수정 전 cs_ai | 수정 후 cs_ai | mfe_60min | mfe_3d | gap_d1 | up_5d |
|------|-------------|-------------|-----------|--------|--------|-------|
| 삼성전자(005930) | 100 | **65** | 2.0851 | 9.8837 | -0.2863 | 0.5172 |
| SK하이닉스(000660) | 100 | **61** | 1.7107 | 10.2478 | -0.1020 | 0.5212 |
| NAVER(035420) | 100 | **45** | 1.3686 | 7.2344 | 0.3262 | 0.5673 |

**핵심 개선**:
- cs_ai 분포 정상화: 전부 100 → 45~65 (종목별 차이 발생)
- mfe_60min_raw: 4.87% → 1.37~2.09% (합리적 범위)
- 종목별 차별화 확인 (20점 격차)

### 4-b) 통합 테스트

```
.venv/bin/python scripts/v41/test_ai_scoring_bridge.py

Ran 7 tests in 3.318s
OK — 7/7 PASS

[PASS] 시나리오 1: 3종목 정상 스코어링 완료 (325ms)
[PASS] 시나리오 2: 분봉 부재 Fallback 정상 — cs_ai=65
[PASS] 시나리오 3: 모델 손상 시 ScoreUnavailableError 정상
[PASS] 시나리오 3: ScoringEngine Fail-Open → rule_cs=65.0
[PASS] 시나리오 4: 타임아웃 Fail-Open → final_cs=55
[PASS] 시나리오 5: /score/batch 포맷 검증
[PASS] 시나리오 5: 배치 partial — 성공 8건, 실패 2건
```

### 4-c) cs_ai 분포 정상화 확인

- **수정 전**: 전 종목 cs_ai=100 (극단 쏠림)
- **수정 후**: 45~65 범위, 종목별 차별화 정상
- Bounds 상한(100) 근접 문제 해소

---

## 5. 잔여 이슈 및 Step B 계획

### 잔여 이슈 (Step B 대상)
1. **mfe_3d 고편향**: SK하이닉스 mfe_3d=10.25% (bounds 상한 근접)
   - 원인: 월별 Z-score vs 전역 Z-score 근사 차이
   - Step B: 5거래일 실측 후 캘리브레이션
2. **VWAP_SUPPORT_COUNT**: 추정값(mean=2, std=3) 사용 중
   - Step B: 분봉 데이터 수집 후 실측 통계 교체
3. **SMALL_CAP_QUALITY**: 실시간에서 기본값 0, 학습 분포 mean=-0.9756
   - Step B: fundamentals 조회 추가 검토

### Step B 강화 조건 (5거래일 실측 후)
- cs_ai 분포 캘리브레이션 (P25/P50/P75 모니터링)
- 예측-실적 상관 분석 (mfe_60min 예측 vs 실제)
- 글로벌 Z-score 파라미터 주기적 업데이트 (월 1회)

---

## 6. 커밋 정보

- **레포**: kis-autotrade-v4 (branch: phase-2c-command-center)
- **커밋**: `799e33ee`
- **메시지**: `[HOTFIX] AI Scorer Z-score 이중 적용 수정 – feature_stats.json 원시 피처 기준 재생성`
- **변경 파일**: `data/go100/models/go100_brain_v2_feature_stats.json`

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (SHA: 799e33ee, kis-autotrade-v4)
- [x] project-docs 보고서 push 완료 (SHA: fe4289d, GitHub raw URL HTTP 200 확인)

---

HANDOVER.md 업데이트 완료: fe4289d
GitHub: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-AI-SCORING-ZSCORE-HOTFIX-001-20260301.md
