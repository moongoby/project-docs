# CUR-V41-LIVE-TRADING-FULLFLOW-001 — GO100 실매매 전체 흐름 완성

- **작업일**: 2026-03-03
- **커밋**: 66ccd72d (kis-autotrade-v4, phase-2c-command-center)
- **작업 범위**: 백엔드 4파일

---

## 1. 기존 문제점

| # | 문제 | 증상 |
|---|------|------|
| P-1 | 체결가 미확인 | 매수/매도 후 ohlcv_daily 종가를 체결가로 가정 → 실제 체결가와 불일치 |
| P-2 | go100_live_orders 미기록 | live_engine이 주문 후 go100_live_orders에 INSERT 안 함 |
| P-3 | go100_trades 미생성 | 매도 후 손익 기록 없음 |
| P-4 | Kiwoom 체결조회 API 미구현 | broker_kiwoom_client에 체결내역 조회 없음 |
| P-5 | KIS TR_ID 구버전 | VTTC8001R (폐지예정) → VTTC0081R 미변경 |
| P-6 | NXT 지원 없음 | EXCG_ID_DVSN_CD 미적용 |
| P-7 | reconcile stock_code 형식 불일치 | Kiwoom "A001250" vs DB "001250" |

---

## 2. 수정 파일 및 내용

### 2-1. `backend/app/services/go100/live_trading/live_engine.py`

#### 신규 메서드

| 메서드 | 역할 |
|--------|------|
| `_get_executor()` | broker_type(KIS/KIWOOM) + is_mock 반환, KIWOOM 분기 |
| `_poll_fill_price()` | 주문 후 실체결가 폴링 (최대 30초, 5초 간격) |
| `_get_kis_fill_price()` | KIS `get_order_history()` avg_prvs 조회 |
| `_get_kiwoom_fill_price()` | Kiwoom `ka10076` cntr_pric 조회 |
| `_insert_live_order()` | go100_live_orders SUBMITTED INSERT |
| `_update_live_order_filled()` | go100_live_orders FILLED 업데이트 |
| `_insert_trade()` | go100_trades 실체결가 기반 INSERT |

#### 기존 메서드 수정

| 메서드 | 변경 내용 |
|--------|----------|
| `_close_position()` | current_price에 실체결가 저장 추가 |
| `reconcile()` | Kiwoom holdings 직접 조회, `A001250` → `001250` 정규화 |
| BUY/SELL 루프 | 체결가 폴링 → live_orders/trades 자동 기록 연결 |

### 2-2. `backend/app/core/broker_kiwoom_client.py`

**`get_order_history()` 신규 구현**
- API: `ka10076` (체결요청) / POST `/api/dostk/acnt`
- 반환: `order_no`, `stock_code`, `side`, `fill_price(cntr_pric)`, `filled_qty(cntr_qty)`, `ord_tm`
- `stex_tp`: 0=통합(KRX+NXT), 1=KRX, 2=NXT
- 모의투자 도메인 자동 감지 → KRX 강제

### 2-3. `backend/app/services/trading/v4_order_executor.py`

**`get_order_history()` 수정**
- TR_ID: `VTTC8001R` → `VTTC0081R` (모의), `TTTC8001R` → `TTTC0081R` (실전) **신TR_ID**
- 파라미터: `SLL_BUY_DVSN_CD`, `CCLD_DVSN=01`(체결만), `EXCG_ID_DVSN_CD=ALL`(NXT포함)
- 반환: `filled_qty`, `avg_prvs`, `fill_price`, `exchange` 추가

### 2-4. `backend/app/services/trading/kis_order_service.py`

**`get_daily_ccld()` 수정**
- TR_ID 신버전 적용
- `exchange` 파라미터 추가 (KRX/NXT/SOR/ALL, 모의=KRX 강제)
- 반환: `filled_qty`, `avg_prvs`, `fill_price`, `exchange` 추가
- `get_unfilled_orders()` TR_ID 신버전 적용

---

## 3. 완성된 실매매 흐름

```
run_one_day(portfolio_id, db, dry_run=false)
  ↓
1. _get_executor() → (executor, broker_type, is_mock)
   KIS:    V4OrderExecutor(config_id)
   KIWOOM: V4OrderExecutor(config_id) + _place_order_kiwoom() 경유
  ↓
2. [SELL] place_sell_order()
   → _insert_live_order() → go100_live_orders SUBMITTED
   → _poll_fill_price()   → 체결가 API 조회 (최대 30초)
     KIS:    get_order_history() avg_prvs
     KIWOOM: ka10076 cntr_pric
   → _update_live_order_filled() → go100_live_orders FILLED + filled_price
   → _close_position()   → go100_positions CLOSED + current_price=실체결가
   → _insert_trade()     → go100_trades SELL + 실손익
  ↓
3. [BUY] place_buy_order()
   → _insert_live_order() → go100_live_orders SUBMITTED
   → _poll_fill_price()   → 실체결가 확인
   → _update_live_order_filled() → go100_live_orders FILLED
   → _open_position()    → go100_positions OPEN + entry_price=실체결가
   → _insert_trade()     → go100_trades BUY
```

---

## 4. NXT 지원 정리

| 계좌 | NXT 지원 | EXCG_ID_DVSN_CD |
|------|---------|----------------|
| KIS 모의 | ❌ KRX만 | KRX 강제 |
| KIS 실계좌 | ✅ | ALL (KRX+NXT) |
| KIWOOM 모의 | ❌ KRX만 | stex_tp=1 강제 |
| KIWOOM 실계좌 | ✅ | stex_tp=0 (통합) |

---

## 5. 내일 아침 검증 세팅

### dry_run=true (장 전 09:00 이전)
```bash
curl -X POST "http://localhost:8002/api/go100/live-trading/9/run-now?dry_run=true" \
  -H "Authorization: Bearer $TOKEN"
# 확인: go100_live_orders, go100_trades에 DRY- 주문번호로 기록 생성 여부
```

### 실매매 (09:05 이후)
```bash
curl -X POST "http://localhost:8002/api/go100/live-trading/9/run-now?dry_run=false" \
  -H "Authorization: Bearer $TOKEN"
# 확인:
# 1. go100_live_orders: status=FILLED, filled_price 실체결가
# 2. go100_trades: price = 실체결가 (종가 아님)
# 3. go100_positions: entry_price = 실체결가
```

### 체결가 검증 방법
```sql
-- 체결가 일치 여부
SELECT lo.order_id, lo.stock_code, lo.filled_price AS live_order_price,
       t.price AS trades_price, p.entry_price AS position_price
FROM go100_live_orders lo
JOIN go100_trades t ON t.stock_code = lo.stock_code AND DATE(t.traded_at) = CURRENT_DATE
JOIN go100_positions p ON p.stock_code = lo.stock_code AND p.status = 'OPEN'
WHERE lo.user_id = 3 AND DATE(lo.created_at) = CURRENT_DATE AND lo.status = 'FILLED';
```

---

## 6. 검증 결과 (dry_run)

```
dry_run=true 테스트:
  bought=4, errors=0 ✅

go100_live_orders:
  4건 SUBMITTED → FILLED (DRY 주문번호) ✅
  filled_price: 5880, 5930, 15155, 4725 ✅

go100_trades:
  4건 BUY 자동 생성 ✅
  price: 5880, 5930, 15155, 4725 ✅
```

**커밋**: 66ccd72d
**레포**: moongoby/go100, branch: phase-2c-command-center
