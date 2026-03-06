# T-123 완료보고: DESK5 Fundamental 긴급 재수집

**Task ID**: T-123
**완료일시**: 2026-03-05 19:30 KST
**작업자**: Claude Code (REMOTE_211)
**우선순위**: P1-HIGH

---

## 요약

DESK5 watchlist 20종목의 `v4_fundamental_quarterly` 데이터 0건 문제를 해결.
KIS API(모의투자 서버)가 재무 API를 지원하지 않아 `stock_fundamentals` 테이블에서 fallback 마이그레이션으로 처리.

**결과**: 20종목 200건 삽입 완료 / GrowthScore fallback 0% / NONE 0%

---

## 1. 원인 분석

### 1.1 FundamentalCollector 실패
```
POST https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/finance/financial-ratio
→ HTTP 500: credentials_type Bearer 유효하지 않음
```
- `KIS_BASE_URL=https://openapivts.koreainvestment.com:29443` (모의투자 서버)
- 재무비율 조회 API(FHKST66430100)는 **실전 서버 전용** — 모의투자 미지원

### 1.2 await 호출 오류
- `FundamentalCollector.collect_symbol()`은 동기 함수
- `asyncio.run()` 래핑 제거 후 직접 동기 호출로 수정

---

## 2. 조치 내용

### 2.1 stock_fundamentals → v4_fundamental_quarterly 마이그레이션

```sql
INSERT INTO v4_fundamental_quarterly
  (symbol, fiscal_year, fiscal_quarter, revenue, operating_profit,
   net_income, eps, per, pbr, roe, debt_ratio, created_at)
SELECT symbol, fiscal_year, fiscal_quarter, revenue, operating_profit,
       net_income, eps, per, pbr, roe, debt_ratio, NOW()
FROM stock_fundamentals
WHERE symbol IN (
  'KOSPI:005930','KOSPI:000660','KOSPI:035420',...  -- 20종목
)
ON CONFLICT (symbol, fiscal_year, fiscal_quarter) DO NOTHING;
```

| 항목 | 값 |
|------|----|
| 대상 종목 | 20종목 (DESK5 watchlist 전체) |
| 삽입 건수 | 200건 |
| 종목당 평균 | 10건 (1~11분기) |
| source | stock_fundamentals (기존 수집 데이터) |

### 2.2 GrowthScoreEngine 재분류 결과

```python
engine = GrowthScoreEngine()
for symbol in DESK5_WATCHLIST:
    result = engine.classify_stock(symbol)
    # → AXIS1_EXPECTATION (all 20)
```

| 분류 | 건수 | 비율 |
|------|------|------|
| AXIS1_EXPECTATION | 20 | 100% |
| AXIS2_REBOUND | 0 | 0% |
| AXIS3_CYCLE | 0 | 0% |
| NONE (데이터 없음) | 0 | **0%** ✅ |
| fallback | 0 | **0%** ✅ |

**이전**: 20/20 fallback(score=0.3) → **현재**: 20/20 정식 분류

---

## 3. 한계 및 후속 과제

| 항목 | 상태 |
|------|------|
| 실전 서버 재무 API 연동 | ⚠️ 모의투자 기간 중 불가 — 실전 전환 시 재수집 필요 |
| stock_fundamentals 데이터 최신성 | ℹ️ 마지막 수집일 확인 필요 (일부 구데이터 가능성) |
| FundamentalCollector KIS_BASE_URL 분기 | 📋 TODO: 실전/모의투자 분기 처리 |

---

## 4. 체크리스트

- [x] v4_fundamental_quarterly 200건 삽입 확인
- [x] GrowthScoreEngine NONE 0% 확인
- [x] fallback 비율 0% 확인
- [x] 20종목 모두 AXIS1_EXPECTATION 분류
- [x] 브릿지 pending → archived 처리

---

*보고 완료: 2026-03-05 19:30 KST*
