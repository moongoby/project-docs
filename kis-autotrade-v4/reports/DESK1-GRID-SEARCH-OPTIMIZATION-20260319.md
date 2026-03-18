# DESK1 그리드서치 최적화 결과 보고서

**작업 ID**: DESK1-GRID-SEARCH-OPTIMIZATION  
**날짜**: 2026-03-19  
**작성자**: Claude Sonnet 4.6

---

[인계 확인]  
직전 완료: GRID-SEARCH-OPTIMIZATION (2026-03-18)  
현재 단계: Phase 2C  
CEO 지시 적용: D-001, D-003  
strategy_cards: N/A  
open_positions: N/A  

---

## 1. 작업 요약

DESK1 종목(100개)에 대해 10개 전략 × 파라미터 그리드 × DESK1 전용 exit rules(4종) = 144 조합 백테스트 실행.  
결과를 `v4_optimization_results` 테이블 (desk_id=1)에 저장 완료.

---

## 2. 실행 환경

- **스크립트**: `scripts/run_desk1_gridsearch.py` (기존 파일 재활용)
- **데이터**: `ohlcv_daily` 2025-09-01 ~ 2026-03-19, 종목 3,775개
- **DESK1 종목**: `v4_pick_reasons WHERE desk='DESK1' AND is_active=true` → 100개
- **DESK1 Exit Rules** (초단기 전용):
  1. stop=-1.5%, target=2.0~5.0%, hold=1일
  2. stop=-1.0%, target=1.5~3.0%, hold=1일
  3. stop=-2.0%, target=2.5~6.0%, hold=2일
  4. stop=-1.5%, target=2.0~4.0%, hold=2일

---

## 3. 검증 체크리스트

| 항목 | 결과 |
|------|------|
| 구현 목표 | DESK1 종목 10개 전략 그리드서치 실행 후 v4_optimization_results(desk_id=1) 저장 |
| 검증 방법 | `SELECT COUNT(*) FROM v4_optimization_results WHERE desk_id=1` |
| 완료 기준 | desk_id=1 rows > 0, 10개 전략 모두 포함 |
| 실패 기준 | 0건 또는 에러 발생 |
| 서비스 재시작 확인 | N/A (서비스 재시작 없음 - 스크립트 직접 실행) |
| 에러 로그 | 0건 (전 조합 정상 완료) |

---

## 4. 실행 결과

### 4.1 조합 현황

| 항목 | 수치 |
|------|------|
| 테스트 조합 수 | 144건 |
| DB INSERT 성공 | 144건 (total_trades ≥ 3 모두 통과) |
| DESK1 총 누적 결과 | **606건** |
| 커버된 전략 수 | 10개 (전 전략 완료) |

### 4.2 전략별 최고 성능 (샤프 기준)

| 순위 | 전략 | 최고 샤프 | 최고 승률 | 최고 PF | 비고 |
|------|------|----------|---------|--------|------|
| 1 | BOLLINGER_BAND | **17.50** | 77.78% | 8.34 | ★ 최우수 |
| 2 | MEAN_REVERSION | 9.30 | 62.07% | 4.06 | |
| 3 | RSI_DIVERGENCE | 8.15 | 58.06% | 3.46 | |
| 4 | GOLDEN_CROSS | 2.72 | 46.14% | 1.48 | |
| 5 | DESK_COMPOSITE | 1.64 | 45.51% | 1.36 | |
| 6 | TREND_FOLLOWING | 0.91 | 43.30% | 1.14 | |
| 7 | MACD | 0.47 | 44.94% | 1.07 | |
| 8 | NEWS_IMPACT | 0.10 | 41.63% | 1.03 | |
| 9 | BREAKOUT_MOMENTUM | -0.25 | 40.04% | 0.94 | 적합하지 않음 |
| 10 | VOLUME_SPIKE | -0.32 | 39.35% | 0.93 | 적합하지 않음 |

### 4.3 DESK1 최적 파라미터 (종합 1위)

```
전략: BOLLINGER_BAND
진입 파라미터:
  - bb_period: 20
  - bb_mult: 2.5
  - buy_threshold: -0.05 (밴드 아래 5% 이탈 시 매수)
  - sell_threshold: 1.05 (밴드 위 5% 돌파 시 매도)
청산 규칙:
  - stop: -2.0%
  - target_min: 2.5%
  - target_max: 6.0%
  - max_hold_days: 2

결과: 수익률 62.5% | 승률 78% | 샤프 17.50 | PF 8.34 | 거래 18건 | 평균 보유 0.44일
```

---

## 5. 분석 및 시사점

### DESK1 적합 전략 (PF ≥ 1.3)
- **BOLLINGER_BAND**: 초과 밴드 이탈 후 회귀 패턴. 초단기(0.4일 보유)로 DESK1에 최적
- **MEAN_REVERSION**: BB + RSI 복합 조건. 적은 거래로 높은 정밀도
- **RSI_DIVERGENCE**: RSI 과매도(20~30) 역추세. 안정적 성과

### DESK1 부적합 전략 (PF < 1.0)
- **BREAKOUT_MOMENTUM**: 돌파 후 추격 전략 → DESK1 초단기에는 진입 타이밍 지연으로 손실
- **VOLUME_SPIKE**: 급등 후 추격 → 단기 소진 패턴으로 손절 빈번
- **NEWS_IMPACT**: 뉴스 기반 급등 종목 → 1-2일 보유로는 모멘텀 미소진

### DESK1 전략 특성
- 초단기(1-2일) exit rule에서 BOLLINGER_BAND > MEAN_REVERSION > RSI 계열이 공통적으로 우수
- 추세추종 계열(TREND_FOLLOWING, GOLDEN_CROSS)은 승률은 낮으나 PF > 1.0으로 유효
- 평균 보유일 0.44일 → 당일 또는 익일 청산 패턴 확인

---

## 6. 다음 단계 권고

1. DESK1 최적 전략 TOP3(BOLLINGER_BAND, MEAN_REVERSION, RSI_DIVERGENCE)를 전략 카드화 검토
2. exit_rules stop=-2.0%, target=2.5~6.0%, hold=2일 → DESK1 공통 청산 규칙으로 채택 고려
3. 거래 건수가 18~29건으로 적음 → 백테스트 기간 연장 또는 종목 풀 확대 권고

---

## 7. DB 검증

```sql
-- DESK별 결과 수
SELECT desk_id, COUNT(*), COUNT(DISTINCT strategy_name)
FROM v4_optimization_results
GROUP BY desk_id ORDER BY desk_id;

-- 결과:
-- desk_id=1: 606건, 10전략
-- desk_id=2: 288건, 10전략
-- desk_id=3: 288건, 10전략
-- desk_id=4: 288건, 10전략
-- desk_id=5: 288건, 10전략
```

---

HANDOVER.md 업데이트: 별도 커밋 예정
