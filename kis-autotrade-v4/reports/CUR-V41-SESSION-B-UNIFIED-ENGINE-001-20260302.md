# CUR-V41-SESSION-B-UNIFIED-ENGINE-001-20260302

**작성일**: 2026-03-02
**작성자**: Claude Sonnet 4.6 (Session B)
**대상 브랜치**: phase-2c-command-center
**완료 조건 충족**: ✅ 24건 PASS / 기존 31건 유지

---

## 1. 목적 및 배경

V4.1 시스템은 backtest / paper / mock / live 4개 엔진이 각각 별도로 운영되어 왔다. 이로 인해:

- 동일 전략이 모드에 따라 다른 슬리피지·비용 계산을 적용하여 **성능 불일치** 발생
- 모드 전환 시 코드 수정 필요 → **운영 리스크** 증가
- GO100 episodic memory 연동 누락 → **AI 학습 데이터 단절**

CEO 피드백 #1~#5 이행 + GAP 목록(12건) 해소를 위해 **단일 통합엔진** `unified_engine`을 Session B에서 구축하였다.

---

## 2. 구현 완료 항목 (B-1 ~ B-9)

### B-1. 디렉토리 구조 + config.py

```
backend/app/services/unified_engine/
├── __init__.py
├── config.py
├── engine.py
├── go100_integration.py
├── adapters/
│   ├── __init__.py
│   ├── data_source.py
│   ├── order_executor.py
│   └── position_store.py
└── core/
    ├── __init__.py
    ├── exit_manager.py
    ├── pnl_calculator.py
    ├── portfolio_manager.py
    └── signal_generator.py
```

**config.py 주요 상수:**

| 상수 | 값 |
|---|---|
| COST_ROUNDTRIP_PCT | 0.47% |
| SLIPPAGE_FIXED_PCT | 0.13% |
| CONCURRENT_LIMIT | 5 |
| HARD_STOP_PCT | -3.0% |
| FORBIDDEN_ACCOUNT_IDS | {5, 6} |
| STRATEGY_PRIORITY_ORDER | ["D6","D5","D4","D7","D2","S1"] |

**EngineMode**: BACKTEST / VIRTUAL / LIVE
**DataSourceType**: DB / KIS_MOCK
**UnifiedEngineConfig**: `is_backtest`, `is_virtual`, `is_live`, `uses_kis_api`, `validate()` (live 모드 차단)

---

### B-2. adapters/data_source.py

| 클래스 | 설명 |
|---|---|
| `DataSource` (ABC) | `get_candidates()`, `get_minute_bars()`, `get_daily_bars()`, `get_investor_data()`, `get_current_price()` |
| `DBDataSource` | asyncpg → v4_ohlcv_minute, ohlcv_daily, v4_investor_daily |
| `KISMockDataSource` | KIS REST API (openapivts:29443), 토큰 자동 갱신 |
| `KISLiveDataSource` | NotImplementedError (미구현 안전장치) |

---

### B-3. adapters/order_executor.py — SlippageAnalyzer 3계층

CEO 피드백 #3: 슬리피지를 단순 고정값에서 3계층 분석으로 고도화.

| Layer | 메서드 | 계산식 |
|---|---|---|
| Layer 1 | `spread_slippage(bid, ask, price, side)` | (ask-bid)/price × 100 / 2 |
| Layer 2 | `depth_impact_slippage(order_qty, avail_qty, tick_size, price)` | 부족 틱 비율 × tick_size / price × 100 |
| Layer 3 | `network_latency_slippage(latency_ms, vol_per_ms)` | latency × vol_per_ms × 100 |
| Backtest | `statistical_slippage()` | SLIPPAGE_FIXED_PCT (0.13%) |

**실행기:**

| 클래스 | 설명 |
|---|---|
| `VirtualExecutor` | v4_paper_trades INSERT, 백테스트 고정 슬리피지 |
| `KISMockExecutor` | KIS Mock API (VTTC0802U/VTTC0801U) + 측정 슬리피지 |
| `KISLiveExecutor` | 3중 guard → 현재 NotImplementedError |

---

### B-4. adapters/position_store.py

- `Position` 데이터클래스: `unrealized_pnl_pct` 프로퍼티, `update_price()`
- `PaperStore`: v4_paper_trades (backtest 용)
- `MockStore`: v4_mock_trades (auto-create DDL 포함)
- `LiveStore`: v4_positions **READ ONLY** — `save_entry/save_exit → PermissionError`

---

### B-5. core/signal_generator.py — DCS Grade + CTE 연동

**DCSCalculator** (분봉 데이터 기반 등급):

| 지표 | 가중치 |
|---|---|
| VWAP 위치 | 30점 |
| RSI 30~50 구간 | 25점 |
| 거래량 추세 | 25점 |
| 일봉 MA 정렬 | 20점 |

점수 합계 → A(≥75) / B(≥55) / C(≥35) / D(≥15) / F

**SignalGenerator**: CTE 파이프라인 재사용 + ScoringEngine.compute_final_cs() 연동 + D2A/D2B/D2C 서브타입 분기

---

### B-6. core/exit_manager.py — 5모드 청산 + AI 재평가

CEO 피드백 #4: AI Scorer 재평가 로직 구현.

| Mode | 조건 | 청산 비율 |
|---|---|---|
| MODE_5 FORCE_EXIT | DD Level ≥ 4 | 100% |
| MODE_1 HARD_STOP | unrealized ≤ -3% | 100% |
| MODE_3 TIME_CLOSE | 15:30 이후 | 100% |
| MODE_4 PARTIAL_TP | unrealized ≥ +3% | 50% |
| MODE_2 ATR_TRAILING | peak ≥ +2% + retrace ≥ 10% | 100% |

**AI 재평가 (MODE_2, MODE_3 진입 전):**
- cs_ai ≥ 70 → 청산 보류 + trailing 조임
- cs_ai < 50 → 즉시 청산
- 예외 발생 → **Fail-Open** (None 반환, 기존 룰 유지)

---

### B-7. core/portfolio_manager.py — DD Decelerator + GO100 연동

**DD Decelerator 5레벨:**

| Level | 이름 | 범위 | 배수 |
|---|---|---|---|
| 0 | Normal | > -3% | 1.00 |
| 1 | Caution | -5% ~ -3% | 0.70 |
| 2 | Warning | -8% ~ -5% | 0.50 |
| 3 | Danger | -10% ~ -8% | 0.25 |
| 4 | Halt | ≤ -10% | 0.00 |

**자본 배분:**

| 전략 | 비율 |
|---|---|
| D6, D7 | 25% |
| D-ORB, D5 | 15% |
| D2(A/B/C) | 10% |
| D4, S1 | 5% |

**Kill Switch**: daily_pnl_pct ≤ -2% → 당일 신규 진입 차단
**GO100 연동**: `log_daily_episodic()` → bridge.log_episodic_memory (virtual 일일 완료 시)

---

### B-8. core/pnl_calculator.py

```
net_pnl_pct = gross_pnl_pct - COST_ROUNDTRIP_PCT(0.47%) - slippage_pct
net_pnl_krw = gross_pnl_krw - cost_krw - slippage_krw
```

`PnLResult.is_winner`: net_pnl_pct > 0

---

### B-9. engine.py + go100_integration.py + run_unified_engine.py

**UnifiedEngine 메서드:**

| 메서드 | 기능 |
|---|---|
| `run_premarket()` | 후보 풀 구성, daily 초기화 |
| `run_signal()` | 신호 생성 + CTE 평가 + 진입 |
| `run_monitor()` | 보유 종목 모니터링 + 청산 |
| `run_close()` | 15:30 시간청산 + 일일 정산 |
| `run_full()` | premarket → signal → monitor → close 순차 |

**go100_integration.py**: `save_backtest_run()` + `log_daily_result()` (별도 유틸)

**run_unified_engine.py**: 기존 Session C 코드 유지 + `_run_unified_engine_async()` 추가 → `--mode virtual --data-source db --action full` 경로에서 호출

---

## 3. 테스트 결과

### 신규 테스트 (24건)

```
tests/test_unified_engine.py — 24 PASSED in 0.76s
```

| 클래스 | 건수 | 결과 |
|---|---|---|
| TestConfig (3모드) | 3 | ✅ ALL PASS |
| TestDataSource | 2 | ✅ ALL PASS |
| TestSlippageAnalyzer (3계층) | 4 | ✅ ALL PASS |
| TestOrderExecutor | 2 | ✅ ALL PASS |
| TestExitManager | 2 | ✅ ALL PASS |
| TestAIReeval (hold/exit/fail-open) | 3 | ✅ ALL PASS |
| TestPnLCalculator | 2 | ✅ ALL PASS |
| TestPortfolioManager | 3 | ✅ ALL PASS |
| TestDCSCalculator | 1 | ✅ ALL PASS |
| TestEngineIntegration | 1 | ✅ ALL PASS |
| TestConstants | 1 | ✅ ALL PASS |

### 기존 테스트 (31건)

```
tests/ (--ignore=test_unified_engine.py,test_api_endpoints.py) — 31 PASSED in 2.53s
```

> `test_api_endpoints.py`: Session B 이전부터 broken (fixture 문제), 이번 작업과 무관.

---

## 4. GAP 해소 현황

| GAP | 내용 | 상태 |
|---|---|---|
| GAP-01 | SystemOrchestrator 이중화 | ✅ 별도 프로세스 + engine_type='unified' heartbeat |
| GAP-02 | ScoringEngine 단절 | ✅ compute_final_cs() 연동 |
| GAP-03 | D2 서브타입 분기 | ✅ D2A/D2B/D2C 구현 (D2C=BOOKED→D2A fallback) |
| GAP-04 | 실계좌 3중 guard | ✅ KISLiveExecutor + FORBIDDEN_ACCOUNT_IDS |
| GAP-05 | DCS Grade 연동 | ✅ DCSCalculator 구현 |
| GAP-06 | 실시간 청산 없음 | ✅ ExitManager 5모드 |
| GAP-07 | 슬리피지 단순 고정값 | ✅ SlippageAnalyzer 3계층 |
| GAP-08 | AI 재평가 없음 | ✅ _ai_reevaluate() + Fail-Open |
| GAP-09 | DD Decelerator | ✅ 5레벨 구현 |
| GAP-10 | Kill Switch | ✅ daily ≤ -2% |
| GAP-11 | v4_mock_trades 없음 | ✅ _ensure_mock_table() 자동 생성 |
| GAP-12 | GO100 연동 누락 | ✅ episodic_memory + backtest_runs |

---

## 5. CEO 피드백 이행 확인

| 피드백 | 내용 | 이행 |
|---|---|---|
| #1 | 3모드 통합 (backtest/virtual/live) | ✅ EngineMode enum |
| #2 | virtual: db/kis-mock 선택 | ✅ DataSourceType + --data-source 플래그 |
| #3 | SlippageAnalyzer 3계층 | ✅ spread/depth/latency |
| #4 | AI Scorer 재평가 at exit | ✅ _ai_reevaluate() Fail-Open |
| #5 | virtual 일일 → GO100 연동 | ✅ log_daily_episodic() |

---

## 6. CLI 사용법

```bash
# Virtual 모드 — DB 데이터소스 — 전체 실행
python scripts/run_unified_engine.py \
    --mode virtual \
    --data-source db \
    --action full

# Backtest 모드 — 날짜 지정
python scripts/run_unified_engine.py \
    --mode backtest \
    --start-date 2026-01-01 \
    --end-date 2026-01-31 \
    --action full
```

---

## 7. 다음 단계 (Session C 이후)

- [ ] `--mode live` 실구현 (KISLiveExecutor 완성, 실계좌 승인 프로세스)
- [ ] DCS Grade → CTE cs_dcs 필드 실측 검증
- [ ] BacktestRunner 날짜 루프 최적화 (현재 1일씩 순차)
- [ ] v4_unified_trades 테이블 도입 (모드별 분리 → 통합 스키마)
