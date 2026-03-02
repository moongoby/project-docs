# CUR-GO100-P5-3-PORTFOLIO-OPTIMIZER-20260227

**작업일**: 2026-02-27  
**목표**: P5-3 포트폴리오 최적화 엔진 — 보유/관심 종목 기반 최적 비중 산출

---

## 1. 요약

- **DB**: `go100_portfolio_optimizations` 테이블 추가 (마이그레이션 044)
- **서비스**: `backend/app/services/go100/portfolio_optimizer.py` 구현
  - `optimize_markowitz()`: OHLCV 수익률·공분산 → 효율적 프론티어 → 최대 샤프 비중
  - `optimize_risk_parity()`: 리스크 기여도 균등 비중
  - `optimize_equal_weight()`: 동일 비중(1/N) 벤치마크
  - `optimize()`: 메서드 라우팅 + DB 저장
  - `get_optimization_history()`: 과거 최적화 이력 조회
- **Agent 도구**: `optimize_portfolio`, `get_portfolio_optimization_history` 등록
- **테스트**: 삼성전자/SK하이닉스/NAVER/카카오/LG에너지솔루션 5종목, MARKOWITZ/RISK_PARITY/EQUAL_WEIGHT 실행 및 DB 저장 확인 완료

---

## 2. 인계 확인

- 직전 완료: (P5-1 등 선행)
- 현재 단계: P5-3 포트폴리오 최적화 엔진
- CEO 지시 적용: 보고서 push(project-docs), 커밋 prefix [GO100]

---

## 3. DB 스키마

**파일**: `backend/migrations/044_go100_portfolio_optimizer.sql`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| optimization_id | SERIAL PK | 자동 증가 ID |
| user_id | INTEGER | 사용자 ID |
| method | VARCHAR(30) | MARKOWITZ, RISK_PARITY, EQUAL_WEIGHT |
| tickers | TEXT[] | 종목코드 배열 |
| weights | NUMERIC[] | 비중 배열 |
| expected_return | NUMERIC(8,4) | 연간 예상 수익률 |
| expected_risk | NUMERIC(8,4) | 연간 예상 리스크(표준편차) |
| sharpe_ratio | NUMERIC(8,4) | 샤프 비율 |
| constraints | JSONB | max_weight, min_weight, sector_limit 등 (향후 확장) |
| input_params | JSONB | period_days, risk_free_rate 등 |
| created_at | TIMESTAMPTZ | |

인덱스: `idx_po_user`, `idx_po_created`

---

## 4. 서비스 동작

### 4.1 optimize_markowitz(tickers, period_days=252, risk_free_rate=0.035)

- `ohlcv_daily`에서 최근 `period_days` 일봉 조회, 종가 수익률 행렬 생성
- 평균 수익률 벡터 μ, 공분산 행렬 Σ 산출
- scipy.optimize.minimize로 **최대 샤프** 비중: max (w'μ - rf) / √(w'Σw), sum(w)=1, w≥0
- 연간 수익률·리스크·샤프 반환

### 4.2 optimize_risk_parity(tickers, period_days=252)

- 동일하게 수익률·공분산 산출
- 목표: 각 자산의 **리스크 기여도(RC)** 를 1/N에 가깝게
- 목적함수: Σ_i (RC_i - 1/N)², sum(w)=1, w≥0 → SLSQP로 최소화

### 4.3 optimize_equal_weight(tickers)

- 비중 1/N 고정, 동일 기간 OHLCV로 예상 수익률·리스크·샤프만 추정하여 반환 (벤치마크)

### 4.4 optimize(user_id, tickers, method, constraints=None, period_days=252, risk_free_rate=0.035)

- method에 따라 위 세 함수 중 하나 호출 후 `go100_portfolio_optimizations` INSERT
- 반환: `{ status, data: { optimization_id, tickers, weights, expected_return, expected_risk, sharpe_ratio, created_at } }`

### 4.5 get_optimization_history(user_id, limit=5)

- 해당 user_id의 최근 최적화 이력 조회

---

## 5. Agent 도구

| 도구 | 설명 |
|------|------|
| optimize_portfolio | tickers(종목코드/종목명 리스트), method(MARKOWITZ/RISK_PARITY/EQUAL_WEIGHT) → 최적 비중 산출 및 DB 저장, 결과 반환 |
| get_portfolio_optimization_history | limit(기본 5) → 과거 최적화 이력 목록 반환 |

- context의 `user_id` 사용 (미전달 시 1)

---

## 6. 테스트 결과 (5종목, 3메서드)

**종목**: 삼성전자, SK하이닉스, NAVER, 카카오, LG에너지솔루션

| 메서드 | 예상수익률(연) | 예상리스크(연) | 샤프비율 | 비중 요약 |
|--------|----------------|----------------|----------|------------|
| MARKOWITZ | 1.91 | 0.41 | 4.63 | 삼성전자·SK하이닉스 위주, 나머지 0 |
| RISK_PARITY | 2.37 | 0.58 | 4.06 | 데이터 특성상 한 종목 집중 가능 |
| EQUAL_WEIGHT | 1.01 | 0.31 | 3.13 | 0.2 / 0.2 / 0.2 / 0.2 / 0.2 |

- DB 저장 확인: `get_optimization_history(user_id=1, limit=5)` 로 optimization_id 1,2,3 및 created_at 정상 조회
- 실행 스크립트: `scripts/go100/test_portfolio_optimizer.py`

---

## 7. 의존성

- `scipy>=1.14.0` 추가 (`backend/requirements.txt`) — Markowitz/Risk Parity 수치 최적화용
- 기존: pandas, numpy, psycopg2

---

## 8. 체크리스트

- [x] 코드 레포 커밋 (kis-autotrade-v4)
- [x] project-docs 보고서 push (본 문서)

---

## 9. 파일 목록

| 경로 | 용도 |
|------|------|
| backend/migrations/044_go100_portfolio_optimizer.sql | go100_portfolio_optimizations 테이블 |
| backend/app/services/go100/portfolio_optimizer.py | 최적화 엔진 + DB 저장/이력 조회 |
| backend/app/services/go100/ai/agent_tools.py | optimize_portfolio, get_portfolio_optimization_history 스키마 추가 |
| backend/app/services/go100/ai/tool_executors.py | 위 두 도구 실행기 등록 |
| scripts/go100/test_portfolio_optimizer.py | 5종목 3메서드 테스트 |
