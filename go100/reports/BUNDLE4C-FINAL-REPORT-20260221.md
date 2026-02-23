# BUNDLE4C-FINAL-REPORT-20260221
## GO100 분봉 백테스트 + 분할익절 연동 + 전략 재생성

---

## 1. 백업 정보
| 항목 | 값 |
|------|-----|
| 백업 파일 | `/tmp/backup_BUNDLE4C_20260221_213405.dump` |
| 백업 크기 | 400,476,912 bytes (~382MB) |
| 백업 전 strategy_cards | 59건 |
| 백업 전 v4_positions OPEN | 5건 |

---

## 2. 구현 내역

### 2-1. `base_orchestrator.py` 수정 (단일 파일)

**신규 import**:
- `Go100MinuteSimulator` (분봉+분할익절 통합 백테스트)
- `Go100AdvancedFilters` (고급 종목선정 필터)
- `InvestmentStyle` (전략 유형 매핑)

**신규 상수**:
- `MAX_MINUTE_STOCKS = 50` (분봉 백테스트 종목 상한)
- `MIN_MINUTE_STOCKS = 5` (분봉 모드 진입 최소 종목수)

**신규 헬퍼 메서드 3개 (static)**:
| 메서드 | 설명 |
|--------|------|
| `_detect_strategy_type(strategy, intent)` | 전략 유형 판별: risk_params.strategy_type → intent.investment_style → max_holding_days → 기본 "daily" |
| `_get_bar_interval(strategy_type, strategy)` | 분봉 bar_interval 결정: LLM 명시 → scalping=3, daily=3, swing=5 |
| `_get_strategy_type_tag(strategy_type)` | 카드 이름 태그: scalping→[스캘핑], daily→[데일리], swing→[단기스윙] |

**`_run_backtest()` 재작성** — 분봉 우선, 일봉 폴백:
```
_run_backtest(card_id, strategy, db, user_id, intent=None)
  ├─ strategy_type = _detect_strategy_type(strategy, intent)
  ├─ bar_interval = _get_bar_interval(strategy_type, strategy)
  ├─ 1. Go100AdvancedFilters.build_universe(db, strategy_type, ref_date)
  │    └─ 실패 시 → 빈 리스트 (UniverseEngine 폴백으로 이동)
  ├─ 2. filter_has_minute_data(db, min_days=10) → 교집합
  ├─ 3. 분봉 종목 ≥ MIN_MINUTE_STOCKS(5)?
  │    ├─ YES → Go100MinuteSimulator.run_backtest(db, config, codes[:50])
  │    │         + result에 run_id=0, go100_card_id, backtest_mode="minute" 추가
  │    └─ NO  → _run_backtest_daily() 폴백
  └─ 기간: 최근 60일, bar_interval: strategy_type별
```

**기존 로직 보존**: `_run_backtest_daily()`로 이동. `pre_codes` 파라미터 추가로 AdvancedFilters 결과 재사용 가능.

**`_finalize_card()` 개선**:
- `strategy_type` 파라미터 추가
- 카드 이름에 `[스캘핑]`/`[데일리]`/`[단기스윙]` 접두사 추가
- `NOT LIKE '[%'` 가드로 최적화 루프에서 중복 태그 방지

**`_empty_bt_result()` 확장**: `universe_stats`, `partial_exit_summary`, `backtest_mode`, `strategy_type` 필드 추가.

**`_run_full_pipeline()` 변경**: `intent` 파라미터를 `_run_backtest()`에 전달.

### 2-2. 전략 생성 스크립트
- `scripts/generate_bundle4c_strategies.py` 생성
- API 타임아웃 우회를 위해 직접 Python으로 오케스트레이터 호출
- 3가지 전략(스캘핑/데일리/스윙) 순차 생성

---

## 3. 테스트 결과

### 3-1. 기존 테스트 (129건 전체 PASS)
```
backend/tests/test_go100_advanced_filters.py    15 PASSED
backend/tests/test_go100_ai_agents.py           12 PASSED
backend/tests/test_go100_backtest.py            10 PASSED
backend/tests/test_go100_card_service.py        11 PASSED
backend/tests/test_go100_evaluate_optimize.py    9 PASSED
backend/tests/test_go100_live_trading.py        13 PASSED
backend/tests/test_go100_minute_backtest.py     15 PASSED
backend/tests/test_go100_paper_trading.py       12 PASSED
backend/tests/test_go100_portfolio_service.py    8 PASSED
backend/tests/test_go100_position_sizing.py     12 PASSED
backend/tests/test_universe_engine_unit.py      10 PASSED
────────────────────────────────────────────
합계                                           129 PASSED (1.46s)
```

### 3-2. 전략 생성 결과 (E2E 검증)
| 전략 | card_id | 수익률 | MDD | 거래수 | Sharpe | 점수 | Pass | 모드 |
|------|---------|--------|-----|--------|--------|------|------|------|
| [스캘핑] 분봉 스캘핑 고변동 대형주 | 13 | -3.82% | -4.70% | 98 | -3.95 | 44.1 | No | minute |
| [데일리] 대형 우량주 수급 데일리 전략 | 14 | +6.31% | -0.91% | 40 | 6.55 | 80.1 | Yes | minute |
| [단기스윙] 섹터모멘텀 외국인수급 스윙 | 15 | +15.19% | -2.50% | 110 | 5.68 | 85.9 | Yes | daily |

**분석**:
- 스캘핑(card 13): 분봉 백테스트 실행됨. AdvancedFilters 351종목 → 분봉보유 351종목 → 50종목 제한. 스캘핑 특성상 단기 손절 빈발(-3.82%). 최적화 5회 루프 실행 후 최선 결과 사용.
- 데일리(card 14): 분봉 백테스트 성공. AdvancedFilters → 분봉보유 교집합 적용. Sharpe 6.55, 1회차 통과.
- 단기스윙(card 15): AdvancedFilters swing 파이프라인에서 `filter_sector_momentum`이 `v4_stock_sector` 테이블 데이터 부족으로 0종목 반환 → 일봉 폴백. UniverseEngine으로 200종목 선정, 수익률 +15.19%.

---

## 4. DB 변경사항
| 테이블 | 변경 | 상세 |
|--------|------|------|
| go100_strategy_cards | INSERT 3건 | card_id 13~15, card_status=BACKTESTED |
| strategy_cards | 변경 없음 | 59건 유지 |
| v4_positions | 변경 없음 | OPEN 5건 유지 |

---

## 5. 서비스 상태
| 서비스 | 상태 |
|--------|------|
| go100 (8002) | active |
| kis-v41-api (8003) | 미확인 (재시작 불필요) |
| kis-v41-scheduler | 미확인 (재시작 불필요) |

---

## 6. 변경 파일 목록
| 파일 | 변경 유형 |
|------|-----------|
| `backend/app/services/go100/ai/base_orchestrator.py` | **수정** — 분봉 백테스트 우선, 일봉 폴백, AdvancedFilters 연동, 유형 태그 |
| `scripts/generate_bundle4c_strategies.py` | **신규** — 전략 생성 스크립트 |

---

## 7. 컴플라이언스 체크리스트

| 항목 | 상태 |
|------|------|
| `.env/.bak` 커밋여부 | 미포함 확인 |
| `strategy_cards` 59건 | 59건 유지 |
| `v4_positions` OPEN 수 | 5건 유지 |
| 파일헤더 | `# Modified by: CUR-GO100-BUNDLE4C, 2026-02-21` |
| DB 스키마 변경 | 없음 |
| 서비스 재시작 | go100 active (재시작 불필요, systemd 권한 없음) |
| V4.1 파일 수정 여부 | 없음 |

---

## 8. 알려진 이슈
- **swing AdvancedFilters 0종목**: `filter_sector_momentum`에서 `v4_stock_sector` 테이블 데이터 부족으로 교집합 0. → 일봉 UniverseEngine 폴백 정상 작동. v4_stock_sector 데이터 보강 필요.
- **스캘핑 전략 수익률 음수**: 스캘핑 특성상 잦은 손절. LLM 최적화 5회 후에도 목표 미달. 분봉 데이터 범위(2개월) 한계. 실전에서는 3개월+ 데이터로 재검증 필요.
