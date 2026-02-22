# BUNDLE4D — 종목×전략 적합도 매트릭스 + 타이밍 최적화 최종 보고서

**작업 ID**: CUR-GO100-BUNDLE4D
**작업일**: 2026-02-21
**브랜치**: phase-2c-command-center

---

## 1. 백업 정보

- DDL 전 strategy_cards: **59건** (불변)
- DDL 전 v4_positions OPEN: **5건** (불변)
- 신규 테이블 2개 생성 (기존 테이블 무수정)

---

## 2. 구현 내역

### 2.1 신규 파일 (7개)

| # | 파일 | 용도 | LOC |
|---|------|------|-----|
| 1 | `backend/migrations/024_go100_bundle4d_optimizer.sql` | DDL: go100_fit_analysis, go100_desk_allocation | 30 |
| 2 | `backend/app/services/go100/optimizer/__init__.py` | 패키지 init + exports | 22 |
| 3 | `backend/app/services/go100/optimizer/schemas.py` | Pydantic 모델 8개 | 93 |
| 4 | `backend/app/services/go100/optimizer/fit_engine.py` | **핵심**: 종목별 백테스트, fit_score, profit_factor, entry timing | 370 |
| 5 | `backend/app/services/go100/optimizer/optimizer_service.py` | 서비스 퍼사드: fit + exit optimize + desk allocation | 310 |
| 6 | `backend/app/routers/go100/optimizer_router.py` | API 5개 엔드포인트 | 85 |
| 7 | `backend/tests/test_go100_optimizer.py` | 12개 단위 테스트 | 210 |

### 2.2 수정 파일 (1개)

| # | 파일 | 변경 내용 |
|---|------|----------|
| M | `backend/app/main.py` | optimizer_router import + include_router 추가 (2줄) |

### 2.3 분석 스크립트

| 파일 | 용도 |
|------|------|
| `scripts/run_bundle4d_analysis.py` | CEO 3전략 적합도+최적화+배분 직접 실행 |

---

## 3. 핵심 기능

### 3.1 종목×전략 적합도 분석 (FitEngine)

- 유니버스 자동 구성: AdvancedFilters → UniverseEngine 폴백
- 일봉 OHLCV **bulk SELECT 1회** → stock_code별 dict 인덱싱
- 종목당 인메모리 백테스트 (SignalEvaluator 재사용)
- **fit_score** 6지표 가중합:
  - return(×0.25) + win_rate(×0.15) + profit_factor(×0.20) + mdd(×0.15) + sharpe(×0.15) + trades(×0.10)
- 진입 타이밍 요일별 분석 (승률, 평균수익)
- 결과 go100_fit_analysis 테이블 저장

### 3.2 청산 파라미터 최적화 (ExitOptimizer)

- 전략 유형별 그리드:
  - scalping: 4×4×3×2 = **96 조합**
  - daily: 3×4×3×3 = **108 조합**
  - swing: 3×4×3×3 = **108 조합**
- 랭킹: `sharpe×0.4 + profit_factor×0.3 + return/100×0.3`
- 현재 파라미터 대비 개선률 산출

### 3.3 멀티 데스크 자금 배분 (DeskAllocator)

- 양수 Sharpe 비율 가중 배분 (음수 → 0%)
- 종목 중복 해소: fit_score 최고 카드에 할당
- go100_desk_allocation 테이블 저장

---

## 4. API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/go100/optimizer/fit-analysis` | 적합도 분석 실행 |
| GET | `/api/go100/optimizer/fit-analysis/{card_id}` | 저장된 결과 조회 |
| POST | `/api/go100/optimizer/exit-optimize` | 청산 파라미터 최적화 |
| POST | `/api/go100/optimizer/desk-allocation` | 멀티 데스크 배분 |
| GET | `/api/go100/optimizer/desk-allocation/{id}` | 저장된 배분 조회 |

---

## 5. CEO 3전략 분석 결과

### Card 13: [스캘핑] 분봉 스캘핑 고변동 대형주

- 테스트 종목: 200개
- **TOP 1**: 033240 자화전자 (fit=78.73, ret=49.76%, wr=51.5%, pf=2.53, mdd=-21.16%, sharpe=3.52, trades=33)
- 양수 수익 종목: 1/200 (0.5%) — 스캘핑 전략 특성상 진입 조건이 매우 엄격

### Card 14: [데일리] 대형 우량주 수급 데일리 전략

- 테스트 종목: 42개
- **TOP 1**: 095340 ISC (fit=78.90, ret=44.69%, wr=55.6%, pf=2.13, mdd=-17.47%, sharpe=3.65, trades=27)

### Card 15: [단기스윙] 섹터모멘텀 외국인수급 스윙

- 테스트 종목: 0개 (v4_stock_sector 데이터 부족으로 유니버스 구성 실패 → 기존 BUNDLE4C 이슈와 동일)

### 청산 최적화 (Card 13 스캘핑)

- 96 조합 테스트 완료
- 최적: SL=1.0%, TP=1.5%, TS=1.0% (score=0.316)

### 멀티 데스크 배분 (3천만 자본)

| Card | 전략 | Sharpe | 비중 | 배분액 |
|------|------|--------|------|--------|
| 13 | 스캘핑 | 3.5232 | 49.1% | 14,738,956원 |
| 14 | 데일리 | 3.6480 | 50.9% | 15,261,044원 |
| 15 | 스윙 | 0.0000 | 0.0% | 0원 |

- 중복 종목: 2개 (해소 완료)
- 활성 카드: 2/3, 고유 종목: 18개

---

## 6. 테스트 결과

```
141 passed in 1.63s
```

- 기존 GO100 테스트: 129건 PASSED
- 신규 Optimizer 테스트: 12건 PASSED
- 합계: **141/141 PASSED**

---

## 7. DB 변경사항

### 신규 테이블

| 테이블 | 컬럼 수 | 용도 |
|--------|---------|------|
| go100_fit_analysis | 17 | 종목별 적합도 분석 결과 |
| go100_desk_allocation | 8 | 멀티 데스크 자금 배분 |

### 신규 인덱스

| 인덱스 | 대상 |
|--------|------|
| idx_go100_fit_card | go100_fit_analysis(go100_card_id, fit_score DESC) |

### 기존 테이블 변경: 없음

---

## 8. 서비스 상태

| 서비스 | 상태 |
|--------|------|
| go100 (8002) | active, health OK |
| go100 프론트 (3000) | — |
| strategy_cards | 59건 (불변) |
| v4_positions OPEN | 5건 (불변) |

---

## 9. 컴플라이언스 체크리스트

| 항목 | 상태 |
|------|------|
| .env/.bak 커밋여부 | **미포함** |
| strategy_cards 59건 | **59건 유지** |
| v4_positions OPEN수 | **5건 유지** |
| 파일헤더 | **CUR-GO100-BUNDLE4D 명시** |
| DB스키마변경 | **신규 2테이블 + 1인덱스 (기존 무수정)** |
| 서비스재시작 | **go100 재시작 불필요 (active 상태)** |
| V4.1파일수정여부 | **미수정** |
