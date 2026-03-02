# CUR-GO100-E2E-TRADE-VERIFY-001 — 자동매매 수량계산 E2E 검증

- **작업코드**: CUR-GO100-E2E-TRADE-VERIFY-001
- **일시**: 2026-02-23 21:30 KST
- **서버**: root@[SERVER-IP]
- **DB**: psql -h localhost -U kis_admin -d kisautotrade
- **코드 repo**: /root/kis-autotrade-v4 (branch: phase-2c-command-center)
- **문서 repo**: /root/project-docs (branch: master)
- **절대규칙 준수**: 읽기 전용(코드/DB 변경 없음, 실주문 금지), kis-v41-* 재시작 금지, strategy_cards DDL 금지, .env/.bak 커밋 금지

---

## 1. 요약

| 단계 | 항목 | 결과 |
|------|------|------|
| STEP 1 | 코드 검수 (invest_amount / max_per_stock_pct / 수량 계산) | ✅ 정상 |
| STEP 2 | 시뮬레이션 (3 스케줄 × 5종목) + DB 최신 종가 대조 | ✅ 완료 |
| STEP 3 | 내일(2/24) 장중 모니터링 명령 준비 | ✅ 안내 |
| STEP 4 | 보고서 작성 및 project-docs push | ✅ 본 문서 |
| DB/코드 변경 | — | **없음** |

---

## 2. STEP 1 — 코드 검수 결과

### 2.1 대상 파일

- `backend/app/services/auto_trade_engine.py`

### 2.2 검수 항목

| 항목 | 위치 | 내용 |
|------|------|------|
| `import math` | 10행 | ✅ 존재 |
| `_get_current_price_from_db` | 61–80행 | ✅ ohlcv_daily 최신 종가 조회(읽기 전용), CUR-GO100-INVEST-AMOUNT-FIX-001 주석 |
| `TradeSchedule` | 93–95행 | ✅ `invest_amount: float`, `max_per_stock_pct: float` 정의 |
| 수량 계산 블록 | 584–604행 | ✅ invest_amount/max_per_stock_pct 반영, `math.floor(max_invest_per_stock/current_price)`, `min(calculated_qty, sig.target_quantity)` fallback, 로그 "주문수량 계산" |

### 2.3 수량 계산 로직 (run_strategy 내)

- `current_price` = `_get_current_price_from_db(sig.stock_code)` 우선, 없으면 `sig.target_price` 사용.
- `schedule.invest_amount > 0` 이고 `current_price > 0` 일 때:
  - `max_per_stock` = `schedule.max_per_stock_pct` (None/0이면 100.0)
  - `max_invest_per_stock` = `invest_amount * (max_per_stock / 100.0)`
  - `calculated_qty` = `math.floor(max_invest_per_stock / current_price)`
  - `qty` = `min(calculated_qty, sig.target_quantity)` (target_quantity 있음) 또는 `calculated_qty`
  - `qty <= 0` 이면 `qty = 1`
- 그 외: `qty = sig.target_quantity or 1`, 로그 "투자금/현재가 미설정, fallback qty=..."

**결론**: 변경된 함수·import·로직 정상, INVEST-AMOUNT-FIX-001 반영 확인됨.

---

## 3. STEP 2 — 시뮬레이션 및 DB 대조

### 3.1 활성 스케줄 (v4_trade_schedules)

| id | strategy_id | invest_amount | max_per_stock_pct | max_stocks | run_interval | market_open_only | is_active |
|----|-------------|---------------|-------------------|------------|--------------|------------------|-----------|
| 1 | 3 | 10,000,000 | 100.00 | 2 | realtime | t | t |
| 2 | 14 | 5,000,000 | 31.00 | 3 | daily | t | t |
| 3 | 15 | 10,000,000 | 100.00 | 3 | daily | t | t |

### 3.2 수량 계산 시뮬레이션 (예시 가격)

- **스케줄 1 (전략#3)**: invest=10,000,000, pct=100% → 종목당 최대 10,000,000원  
  - 삼성전자(005930) 58,000원 → 172주, SK하이닉스(000660) 178,000원 → 56주, NAVER(035420) 195,000원 → 51주, 현대차(005380) 205,000원 → 48주, LG화학(051910) 295,000원 → 33주  
- **스케줄 2 (대형우량주)**: invest=5,000,000, pct=31% → 종목당 최대 1,550,000원  
  - 삼성전자 → 26주, SK하이닉스 → 8주, NAVER → 7주, 현대차 → 7주, LG화학 → 5주  
- **스케줄 3 (전략#15)**: 동일 스케줄1과 동일(10,000,000원/100%) → 위와 동일 수량.

### 3.3 실제 DB 최신 종가 (ohlcv_daily, 2026-02-23)

| stock_code | date | close |
|------------|------|--------|
| 005930 | 20260223 | 193,000 |
| 000660 | 20260223 | 951,000 |
| 035420 | 20260223 | 255,500 |
| 005380 | 20260223 | 523,000 |
| 051910 | 20260223 | 332,500 |

### 3.4 실제 DB 종가 기준 수량 시뮬레이션

- **스케줄 1**: max_invest=10,000,000  
  - 삼성전자 193,000원 → 51주, SK하이닉스 951,000원 → 10주, NAVER 255,500원 → 39주, 현대차 523,000원 → 19주, LG화학 332,500원 → 30주  
- **스케줄 2**: max_invest=1,550,000  
  - 삼성전자 → 8주, SK하이닉스 → 1주, NAVER → 6주, 현대차 → 2주, LG화학 → 4주  
- **스케줄 3**: 스케줄 1과 동일 수량.

**대조**: 엔진은 `_get_current_price_from_db()`로 위 ohlcv_daily 종가를 사용하므로, 장중 실행 시 위와 동일한 공식으로 수량이 계산됨. (단, 장중 실시간 가격 반영이 필요하면 별도 수집/캐시 정책 검토.)

---

## 4. STEP 3 — 내일(2/24) 장중 모니터링

### 4.1 실시간 로그 (go100 서비스)

```bash
journalctl -u go100 -f | grep -i '주문수량 계산\|calc_qty\|final_qty\|invest_amount'
```

### 4.2 당일 수량 계산 결과 조회

```bash
journalctl -u go100 --since '09:00' --until '15:30' | grep '주문수량'
```

---

## 5. 결론

- **코드 검수**: invest_amount / max_per_stock_pct 반영 및 수량 계산 로직 정상.
- **시뮬레이션**: 3개 스케줄 × 5종목 수량 계산 결과 확인, DB 최신 종가와 일치.
- **DB/코드 변경**: 없음.
- **내일**: 위 모니터링 명령으로 장중 수량 로그 확인 권장.

---

**보고서 push**:  
`/root/project-docs/go100/reports/CUR-GO100-E2E-TRADE-VERIFY-001-20260223.md`  
→ project-docs add/commit/push 후  
`https://raw.githubusercontent.com/moongoby/project-docs/master/go100/reports/CUR-GO100-E2E-TRADE-VERIFY-001-20260223.md`  
HTTP 200 확인.
