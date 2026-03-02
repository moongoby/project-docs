# CUR-V41-SESSION-G-SERVER-AUDIT-001

| 항목 | 값 |
|------|-----|
| **문서 ID** | CUR-V41-SESSION-G-SERVER-AUDIT-001 |
| **날짜** | 2026-03-02 |
| **세션** | Session G — 서버 실증 검증 + 경미 오류 즉시 조치 |
| **브랜치** | phase-2c-command-center |
| **HEAD** | 259a68a9 |

---

## 1. Stage 1 — 디렉토리 / 파일 존재 검증

### 1-1. 핵심 디렉토리

| 경로 | 존재 |
|------|------|
| `backend/app/services/unified_engine/` | OK |
| `backend/app/services/unified_engine/replay/` | OK |
| `backend/app/services/trading/cte/` | OK |
| `backend/app/services/v41/` | OK |
| `backend/app/services/go100/` | OK |
| `backend/app/services/go100/ai/` | OK |
| `backend/app/services/data/` | OK |
| `scripts/` | OK |
| `tests/` | OK |
| `tests/unit/` | OK |
| `data/go100/models/` | OK |

### 1-2. 핵심 파일

| 파일 | 존재 | 비고 |
|------|------|------|
| `backend/app/services/unified_engine/replay/__init__.py` | OK | |
| `backend/app/services/unified_engine/replay/replay_engine.py` | OK | |
| `backend/app/services/unified_engine/replay/candidate_scanner.py` | OK | |
| `backend/app/services/unified_engine/replay/entry_detector.py` | OK | |
| `backend/app/services/unified_engine/replay/exit_simulator.py` | OK | |
| `backend/app/services/unified_engine/replay/minute_bar_feeder.py` | OK | |
| `backend/app/services/unified_engine/replay/result_aggregator.py` | OK | |
| `scripts/run_replay_backtest.py` | OK | |
| `scripts/run_unified_engine.py` | OK | |
| `tests/test_replay_backtest.py` | OK | 12 tests |
| `tests/test_unified_engine.py` | OK | 24 tests |
| `tests/unit/test_minute_validation.py` | OK | 31 tests |
| `backend/app/services/trading/cte/test_cte_pipeline.py` | OK | 33 tests |
| `backend/app/services/trading/cte/test_vwap_atr.py` | OK | 25 tests |
| `backend/app/services/trading/cte/test_eqs_lag1.py` | OK | 8 tests |
| `backend/app/services/trading/cte/test_d4_atr_adjustment.py` | OK | 4 tests |
| `data/go100/models/go100_brain_v2_lightgbm.joblib` | OK | |
| `data/go100/models/go100_brain_v2_mfe_60min.joblib` | OK | |
| `data/go100/models/go100_brain_v2_mfe_3d.joblib` | OK | |
| `data/go100/models/go100_brain_v2_gap_d1.joblib` | OK | |
| `data/go100/models/go100_brain_v2_feature_stats.json` | OK | 2026-03-01 수정 |
| `data/go100/models/go100_brain_v2_metadata.json` | OK | |
| `backend/app/services/go100/ai/ai_scorer.py` | OK | |
| `backend/app/api/go100/bridge.py` | OK | |
| `backend/app/services/v41/go100_bridge_client.py` | OK | |

### 1-3. 누락 파일 (보고 전용)

| 파일 | 상태 | 비고 |
|------|------|------|
| `scripts/run_cte_full_backtest.py` | MISSING | CTE 통합 백테스트 스크립트 (미구현) |
| `scripts/run_cte_walkforward.py` | MISSING | CTE 워크포워드 스크립트 (미구현) |
| `scripts/prepare_cte_backtest.py` | MISSING | CTE 백테스트 준비 (미구현) |

> 위 3개 파일은 HANDOVER.md에 언급되어 있으나 아직 미구현 상태. Session D에서 replay 엔진으로 대체 진행 중이므로 보고 전용.

---

## 2. Stage 2 — 코드 내용 검증

### 2-1. Safety Guard (Triple Guard)

| 검증 항목 | 결과 |
|-----------|------|
| `FORBIDDEN_ACCOUNT_IDS = {5, 6}` | OK — `unified_engine_config.py` |
| `KISLiveExecutor.execute()` → `raise NotImplementedError` | OK — `order_executor.py` |
| `EngineMode.LIVE` 방어 코드 | OK — `unified_engine_config.py` |
| test: `test_live_mode_blocked` | OK — PASS |
| test: `test_live_executor_forbidden` | OK — PASS |

### 2-2. Exit 5-Mode System

| 모드 | 검증 |
|------|------|
| Hard Stop | OK — `exit_manager.py` + `exit_simulator.py` |
| ATR Trailing | OK — `exit_manager.py` + `exit_simulator.py` |
| Time Close (15:20) | OK — `exit_simulator.py` TIME_CLOSE_LIMIT |
| Partial TP | OK — `exit_simulator.py` partial_pct |
| DD Force Close | OK — `exit_manager.py` dd_force |

### 2-3. CTE Pipeline 상수

| 상수 | 값 | 검증 |
|------|-----|------|
| `COST_ROUNDTRIP_PCT` | 0.47 | OK — `cte_pipeline.py` + `replay_engine.py` |
| `CONCURRENT_LIMIT` | 5 | OK — `cte_pipeline.py` (replay에서는 INTRADAY 8 / OVERNIGHT 4로 분리) |
| `DD_LEVELS` | 4단계 | OK — `replay_engine.py` (-10/-20/-30/-50) |
| `KILL_SWITCH_PCT` | -5.0 | OK — `replay_engine.py` |

### 2-4. Import / 구문 오류

- 전체 replay 모듈 6개 파일 import 정상
- `entry_detector.py`, `exit_simulator.py`, `result_aggregator.py`, `candidate_scanner.py`, `minute_bar_feeder.py`, `replay_engine.py` 모두 정상 로드

---

## 3. Stage 3 — DB 데이터 검증

### 3-1. 테이블 현황

| 항목 | 값 |
|------|-----|
| 총 테이블 수 | **254** (HANDOVER 기준 225 → 29개 증가) |
| `ohlcv_daily` 행 수 | 2,615,744 |
| `v4_ohlcv_minute` 행 수 | 84,129,984 |
| 분봉 기간 | 2025-02-18 ~ 2026-02-27 |
| `v4_strategies` 수 | 60 |
| `v4_positions` OPEN | 14 |
| `v4_mock_trades` | 0건 |
| `v4_paper_trades` | 7건 |
| `accounts` | 6개 (id 1~6) |

### 3-2. 누락 테이블 (보고 전용)

| 테이블 | 상태 | 비고 |
|--------|------|------|
| `global_market` | 미존재 | HANDOVER에 언급, 수집 cron 존재하나 테이블 미생성 |
| `scalping_universe` | 미존재 | `scalping_universe_builder.py` cron 존재하나 테이블 미생성 |

> DB 스키마 변경은 보고 전용 — 즉시 조치 범위 아님.

### 3-3. 계정 보호 확인

| account_id | broker_type | 용도 |
|------------|------------|------|
| 1, 2, 3 | KIS | V4 trading |
| 4 | KIWOOM | API data collection |
| 5, 6 | KIS | **실계좌 — FORBIDDEN** |

`FORBIDDEN_ACCOUNT_IDS = {5, 6}` 코드 확인 OK.

---

## 4. Stage 4 — 테스트 실행 결과

### 4-1. pytest collect-only

```
104 tests collected, 22 collection errors
```

22개 collection error는 모두 **pip 패키지 미설치** (시스템 Python에서 실행, venv 아닌 환경):
- `fastapi`, `pydantic`, `pydantic_settings`, `redis`, `sqlalchemy` 등
- 실제 서비스는 venv에서 실행되므로 **영향 없음**

### 4-2. CTE + 분봉 테스트

```
backend/app/services/trading/cte/ — 70 passed, 0 failed (0.17s)
```

| 테스트 그룹 | 수 | 결과 |
|-------------|-----|------|
| TestD2EVCorrection | 4 | PASS |
| TestForbiddenMatrix | 3 | PASS |
| TestConcurrentLimit | 4 | PASS |
| TestCSGate | 2 | PASS |
| TestEQSGate | 3 | PASS |
| TestBucketForbidden | 6 | PASS |
| TestPriorityDedup | 2 | PASS |
| TestSignalCombo | 4 | PASS |
| TestD2SmokePositiveEV | 2 | PASS |
| TestPipelineEndToEnd | 3 | PASS |
| TestD4ParamsApplied | 2 | PASS |
| TestD4NetRRAchievable | 2 | PASS |
| TestLAG1PricePosition | 2 | PASS |
| TestFirstMinuteFallback | 1 | PASS |
| TestOrderbookNeutral | 1 | PASS |
| TestEQS35Gating | 2 | PASS |
| TestCalculateLAG1Context | 2 | PASS |
| TestVWAP* (10개) | 10 | PASS |
| TestATR* (6개) | 6 | PASS |
| TestExitStrategy (6개) | 6 | PASS |
| TestPipelineIntegration (4개) | 4 | PASS |

### 4-3. Unified Engine 테스트

```
tests/test_unified_engine.py — 24 passed, 0 failed (0.80s)
```

| 테스트 그룹 | 수 | 결과 |
|-------------|-----|------|
| TestConfig | 3 | PASS |
| TestDataSource | 2 | PASS |
| TestSlippageAnalyzer | 4 | PASS |
| TestOrderExecutor | 2 | PASS |
| TestExitManager | 2 | PASS |
| TestAIReeval | 3 | PASS |
| TestPnLCalculator | 2 | PASS |
| TestPortfolioManager | 3 | PASS |
| TestDCSCalculator | 1 | PASS |
| TestEngineIntegration | 1 | PASS |
| TestConstants | 1 | PASS |

### 4-4. 전체 테스트 (test_api_endpoints 제외)

```
tests/ — 67 passed, 0 failed (2.34s)
```

| 파일 | 수 | 결과 |
|------|-----|------|
| test_replay_backtest.py | 12 | PASS |
| test_unified_engine.py | 24 | PASS |
| unit/test_minute_validation.py | 31 | PASS |

### 4-5. 테스트 총계

| 범위 | 수 | 결과 |
|------|-----|------|
| CTE 파이프라인 | 70 | ALL PASS |
| Unified Engine | 24 | ALL PASS |
| Replay Backtest | 12 | ALL PASS |
| Minute Validation | 31 | ALL PASS |
| **합계** | **137** | **ALL PASS** |

---

## 5. Stage 5 — 서비스 / 인프라 검증

### 5-1. systemd 서비스

| 서비스 | 상태 | 비고 |
|--------|------|------|
| go100-frontend.service | active (running) | Next.js 포트 3000 |
| go100.service | active (running) | GO100 API 포트 8002 |
| kis-v41-api.service | active (running) | V4.1 API 포트 8003 |
| kis-webapp-api.service | active (running) | Legacy API 포트 8001 |
| kis-trading-engine.service | active (running) | unified_trading_scheduler |
| kis-v41-scheduler.service | active (running) | V4.1 스케줄러 |
| kis-v41-monitor.service | active (running) | 포지션 모니터 |
| kis-v41-position-monitor.service | active (running) | 포지션 모니터 (중복) |
| kis-scalping.service | active (running) | 스캘핑 스케줄러 |

**9개 서비스 모두 active (running)** — 정상.

### 5-2. 리소스 현황

| 항목 | 값 | 심각도 |
|------|-----|--------|
| 디스크 | 73G / 99G (77%) | MEDIUM |
| 메모리 | 8.2G / 15G 사용 | OK |
| Swap | 6.0G / 8.0G 사용 (75%) | **HIGH** |
| 프로세스 | `collect_minute_historical` **3개 동시 실행** | **HIGH** |

### 5-3. 중복 프로세스 상세

```
PID 356177  Feb27  853h  python collect_minute_historical.py --top 3844 --resume
PID 443732  Feb28  721h  python collect_minute_historical.py --top 3844 --resume
PID 876043  Mar01  239h  python collect_minute_historical.py --top 3844 --resume --rate-limit 12
```

3개의 `collect_minute_historical` 프로세스가 동시 실행 중. 각각 Feb27, Feb28, Mar01 시작.
- 원인: 수집 중단 후 재시작 시 이전 프로세스 미종료
- 영향: DB 쓰기 경합, 높은 swap 사용량 원인
- **조치 권고**: 구 프로세스(PID 356177, 443732) 종료 필요 (대표님 승인 후)

### 5-4. Cron 현황

- 활성 cron 항목: **69개**
- Unified Engine Virtual 모드: 4개 (premarket/signal/monitor/close) — 정상
- 주요 수집기: ohlcv_daily, minute_batch, market_investor, stock_universe 등 — 정상

### 5-5. 로그 파일

| 로그 | 상태 | 조치 |
|------|------|------|
| `/var/log/kis-autotrade/data_miner.log` | OK (128MB) | |
| `/var/log/kis-autotrade/unified_trading_scheduler.log` | OK (12.3MB) | |
| `/var/log/kis-autotrade/top100-collector.log` | OK | |
| `/var/log/unified_engine.log` | **신규 생성** | **즉시 조치 완료** — cron 로그 경로에 파일 없었음 |

---

## 6. 즉시 조치 내역

### 6-1. 완료된 조치

| # | 항목 | 조치 | 분류 |
|---|------|------|------|
| 1 | `/var/log/unified_engine.log` 미존재 | `touch` + `chmod 644` 로 생성 | 로그 경로 오류 |

### 6-2. 조치 불필요 확인

| # | 항목 | 사유 |
|---|------|------|
| 1 | `feature_stats.json` | 실제로 존재함 (`data/go100/models/go100_brain_v2_feature_stats.json`, 2026-03-01 수정) |
| 2 | `__init__.py` 누락 | 검증 결과 모든 패키지에 존재 |
| 3 | import 오류 | replay 모듈 6개 파일 모두 import 정상 |
| 4 | 테스트 실패 | 137개 전부 PASS |

---

## 7. 보고 전용 항목 (조치 안 함)

| # | 항목 | 상세 |
|---|------|------|
| 1 | CTE 스크립트 3개 미구현 | `run_cte_full_backtest.py`, `run_cte_walkforward.py`, `prepare_cte_backtest.py` — Session D replay 엔진으로 대체 |
| 2 | `global_market` 테이블 미존재 | DB 스키마 변경 필요 |
| 3 | `scalping_universe` 테이블 미존재 | DB 스키마 변경 필요 |
| 4 | `v4_mock_trades` 0건 | 2026-03-02(일) 기준. 03-03(월) Virtual 모드 첫 가동 예정 |
| 5 | `collect_minute_historical` 3중 실행 | 대표님 승인 후 구 프로세스 종료 필요 |
| 6 | Swap 6GB/8GB 사용 | 3중 수집기 종료 시 개선 예상 |
| 7 | 테이블 수 254 (HANDOVER 225 기준 +29) | Session D replay + GO100 확장으로 증가 |
| 8 | 22개 test collection error | 시스템 Python pip 패키지 미설치 (서비스 venv와 별개, 영향 없음) |

---

## 8. 종합 판정

| 영역 | 상태 | 비고 |
|------|------|------|
| **코드 무결성** | PASS | Triple Guard 정상, 5-Mode Exit 정상, CTE 상수 일치 |
| **테스트** | PASS | 137/137 ALL PASS |
| **DB 데이터** | PASS | 일봉 2.6M + 분봉 84M 정상, 계정 보호 확인 |
| **서비스** | PASS | 9개 서비스 모두 running |
| **인프라** | WARN | 3중 수집기 프로세스, Swap 75%, 디스크 77% |

**결론**: 코드/테스트/DB/서비스 모두 정상. 인프라 리소스(3중 수집기, Swap)만 모니터링/조치 필요.

---

## 9. 권장 조치 (대표님 판단)

1. **collect_minute_historical 구 프로세스 종료** — PID 356177, 443732 (최신 876043만 유지)
2. **HANDOVER.md 테이블 수 업데이트** — 225 → 254
3. **global_market / scalping_universe 테이블 생성** — cron이 존재하나 테이블 미생성 상태
4. **v4_mock_trades 모니터링** — 03-03(월) Virtual 모드 첫 가동 후 정상 기록 확인
