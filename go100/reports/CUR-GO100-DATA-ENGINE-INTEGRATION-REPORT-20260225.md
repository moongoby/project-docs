# CUR-GO100-DATA-ENGINE-INTEGRATION: 데이터 수집 자동화 + 엔진 연동 보고서

**작성일**: 2026-02-25
**브랜치**: `feat/CUR-GO100-DATA-ENGINE-INTEGRATION`
**커밋**: `0cf5a2b6`

---

## 1. 개요

기존에 수집만 되고 활용되지 않던 데이터를 엔진에 연동하고,
수동 수집이던 핵심 데이터를 자동 크론으로 전환.

---

## 2. P1 — 자동 수집 크론 등록

| 스크립트 | 크론 | 데이터 | 비고 |
|----------|------|--------|------|
| `collect_investor_daily.sh` | 평일 16:50 | v4_investor_daily (외국인/기관 수급) | 기존 수동 → 자동, 상위 500종목 |
| `collect_credit_balance.sh` | 평일 16:45 | v4_credit_balance (신용/공매도 잔고) | KIS 랭킹 30건 |

## 3. P1 — 거래정지 종목 백테스트 진입 차단

- `simulator.py`: volume=0 또는 close=0 종목 진입 스킵
- `minute_simulator.py`: 동일 로직 적용
- 기존 `filter_exclude_suspended`는 유니버스 단계에서 작동, 이번 수정은 백테스트 시뮬레이션 단계 2중 차단

---

## 4. P2 — 신규 필터 5종 (advanced_filters.py)

| # | 필터 | 데이터 소스 | 기능 |
|---|------|-----------|------|
| 13 | `filter_credit_short` | v4_credit_balance | 신용잔고율/공매도잔고율 과열 종목 제외 |
| 14 | `filter_by_theme` | v4_theme_master/stock | 특정 테마 소속 종목 선별 (이름 또는 코드) |
| 15 | `filter_trade_strength` | v4_trade_strength_history | 체결강도 ≥ 기준값 종목 (매수세 우위) |
| 16 | `filter_program_trading` | v4_program_trades | 프로그램매매 순매수/순매도 필터 |
| 17 | `filter_supply_demand` | 복합 (수급+강도+신용) | 수급 강도 복합 필터 (교집합) |

### 파이프라인 반영

- **daily 전략**: `filter_credit_short` 추가 (신용과열 제외)
- **swing 전략**: `filter_credit_short` 추가 (신용과열 제외)

---

## 5. P3 — AI DESIGN 프롬프트 업데이트

`ADVANCED_FILTER_SPEC` (prompts.py):
- 12개 → **17개** 필터로 확장
- 신규 필터 활용 가이드 추가:
  - 테마 전략: `filter_by_theme(theme_name="2차전지")`
  - 수급 모멘텀: `filter_supply_demand(foreign_consecutive_days=5, min_strength=105)`
  - 프로그램 추종: `filter_program_trading(min_net_amount=1000000000, direction="buy")`

---

## 6. 수집 스케줄 전체 현황

| 시간 | 스크립트 | 데이터 |
|------|---------|--------|
| 16:30 | collect_program_trades.sh | v4_program_trades (프로그램매매) |
| 16:35 | collect_strength_daily.sh | v4_trade_strength_history (체결강도) |
| **16:45** | **collect_credit_balance.sh** | **v4_credit_balance (신용/공매도)** |
| **16:50** | **collect_investor_daily.sh** | **v4_investor_daily (수급)** |
| 17:00 | collect_theme.sh | v4_theme_master/stock (테마) |
| 18:00 | collect_ohlcv_daily.py | ohlcv_daily (일봉) |
| 18:30 | collect_vkospi_alt.py | VKOSPI |
| 18:40 | collect_market_investor.py | v4_market_investor_daily (시장수급) |
| 19:00 | collect_stock_universe.py | stock_universe (종목마스터) |

---

## 7. 데이터 활용 매트릭스 (변경 후)

| 데이터 | 백테스트 | 유니버스 필터 | AI 전략생성 | 수집 |
|--------|---------|-------------|------------|------|
| ohlcv_daily | **사용** | **사용** | 간접 | 자동 |
| stock_universe | **사용** | **사용** | 간접 | 자동 |
| v4_investor_daily | - | **사용** | **사용** | **자동 (신규)** |
| v4_credit_balance | - | **사용 (신규)** | **사용 (신규)** | **자동 (신규)** |
| v4_theme_master/stock | - | **사용 (신규)** | **사용 (신규)** | 자동 |
| v4_trade_strength | - | **사용 (신규)** | **사용 (신규)** | 자동 |
| v4_program_trades | - | **사용 (신규)** | **사용 (신규)** | 자동 |

---

## 8. 서비스 상태

```
curl http://localhost:8002/health
→ {"status":"ok","version":"4.1.0","database":"connected","redis":"connected"}
```
