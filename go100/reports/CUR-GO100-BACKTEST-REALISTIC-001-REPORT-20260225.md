# CUR-GO100-BACKTEST-REALISTIC-001: 백테스트 실거래 정합성 완료 보고서

**작성일**: 2026-02-25
**브랜치**: `feat/CUR-GO100-BACKTEST-REALISTIC-001`
**커밋**: `cc0d4cd7`
**레포**: `kis-autotrade-v4`

---

## 1. 개요

백테스트 시뮬레이터가 종가 100% 체결, 슬리피지 0, 거래량 무제한을 가정하여
실거래와 괴리가 발생하는 문제를 해결하기 위해 슬리피지/비용/체결 현실화 모델을 도입.

**핵심 제약**: `slippage_model="none"` (기본값) 시 기존 백테스트와 100% 동일 결과 보장.

---

## 2. 변경 파일 요약

| 파일 | 변경 유형 | 핵심 내용 |
|------|-----------|-----------|
| `backtest/trading_cost.py` | **신규** | SlippageModel, TradingCostModel, RealisticFillModel, CostAccumulator, build_cost_models() |
| `backtest/simulator.py` | 수정 | cost_model 위임, stock_info_cache, cost_breakdown 반환 |
| `backtest/minute_simulator.py` | 수정 | FEE_RATE/TAX_RATE 제거, cost_model 위임, cost_breakdown 반환 |
| `backtest/partial_exit_simulator.py` | 수정 | FEE_RATE/TAX_RATE 제거, _make_exit에 cost_model 파라미터 |
| `backtest/backtest_service.py` | 수정 | result_detail에 cost_breakdown 포함, DB 6개 신규 컬럼 저장 |

---

## 3. 신규 모델 상세

### 3.1 SlippageModel
| 모드 | 설명 |
|------|------|
| `none` (기본) | 슬리피지 0 — 하위호환 |
| `fixed` | 고정 bp 슬리피지 |
| `tiered` | 시총 순위별 기본 bp + 거래량 대비 주문량 추가 bp |

**tiered 로직**:
- rank 1~100: 5bp, 101~300: 10bp, 301+: 20bp
- 주문량/일거래대금 ≤1%: +0bp, ≤5%: +10bp, >5%: +30bp

### 3.2 TradingCostModel
- 수수료율: 0.015% (기존 동일)
- 매도세: 0.18% (기존 동일)
- `calc_buy_cost()`, `calc_sell_cost()` 위임 메서드

### 3.3 RealisticFillModel
| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `min_trade_amount` | 0 | 최소 거래대금 필터 (0=제한없음) |
| `max_volume_participation` | 1.0 | 최대 거래량 참여율 (1.0=제한없음) |
| `fill_position` | `"close"` | 체결 기준가 (`close` / `vwap_approx`) |

### 3.4 CostAccumulator
- `total_commission`, `total_tax`, `total_slippage` 누적
- `skipped_by_liquidity`, `partial_fills` 카운트
- `to_dict()` → result_detail에 포함

---

## 4. DB 마이그레이션

```sql
ALTER TABLE go100_backtest_runs
  ADD COLUMN IF NOT EXISTS gross_return NUMERIC(10,4),
  ADD COLUMN IF NOT EXISTS total_commission NUMERIC(15,0),
  ADD COLUMN IF NOT EXISTS total_tax NUMERIC(15,0),
  ADD COLUMN IF NOT EXISTS total_slippage NUMERIC(15,0),
  ADD COLUMN IF NOT EXISTS net_return NUMERIC(10,4),
  ADD COLUMN IF NOT EXISTS slippage_model VARCHAR(20) DEFAULT 'none';
```

모든 컬럼 NULLABLE → 기존 행 영향 없음.

---

## 5. 전략 카드 설정

```sql
-- 카드 #13, #14에 realistic 파라미터 설정
UPDATE go100_strategy_cards
SET risk_params = risk_params || '{"slippage_model":"tiered","min_trade_amount":100000000,"max_volume_participation":0.1}'::jsonb
WHERE go100_card_id IN (13, 14);
```

카드 #15는 변경 없음 (하위호환 검증용).

---

## 6. 검증 결과

### 6.1 하위호환 (카드 #15, slippage_model 키 없음)

| 항목 | 결과 |
|------|------|
| run_id | 10 |
| status | COMPLETED |
| total_return | 7.0812% |
| gross_return | 8.7565% |
| total_slippage | **0** |
| total_commission | 23,817 |
| total_tax | 143,712 |
| slippage_model | none |

**슬리피지 0 확인** — 기존 동작과 동일.

### 6.2 Realistic (카드 #14, tiered slippage)

| 항목 | 결과 |
|------|------|
| run_id | 11 |
| status | COMPLETED |
| total_return (net) | 1.2991% |
| gross_return | 1.8012% |
| total_slippage | **32,876** |
| total_commission | 2,456 |
| total_tax | 14,875 |
| slippage_model | tiered |

**gross_return(1.80%) > net_return(1.30%)** 확인 — 슬리피지 차감 정상.

### 6.3 서비스 상태

```
curl http://localhost:8002/health
→ {"status":"ok","version":"4.1.0","orchestrator_state":"IDLE","database":"connected","redis":"connected"}
```

---

## 7. risk_params 설정 가이드

기존 카드에는 아무 키도 추가하지 않으면 `slippage_model="none"` 동작 (하위호환).

realistic 모드 활성화 시 `risk_params`에 아래 키 추가:

```json
{
  "slippage_model": "tiered",
  "min_trade_amount": 100000000,
  "max_volume_participation": 0.1,
  "fill_position": "close"
}
```

| 키 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `slippage_model` | string | `"none"` | `"none"`, `"fixed"`, `"tiered"` |
| `slippage_fixed_bp` | float | 0 | fixed 모드 전용 (bp) |
| `min_trade_amount` | float | 0 | 최소 일거래대금 (원) |
| `max_volume_participation` | float | 1.0 | 최대 거래량 참여율 |
| `fill_position` | string | `"close"` | `"close"` or `"vwap_approx"` |
| `commission_rate` | float | 0.00015 | 수수료율 |
| `sell_tax_rate` | float | 0.0018 | 매도세율 |
