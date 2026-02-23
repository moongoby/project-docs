# CUR-GO100-BUNDLE4B-FIX 최종 보고서
**작업일**: 2026-02-21
**작업자**: Claude (AI)
**커밋 브랜치**: phase-2c-command-center

---

## 1. 근본 원인 분석 (Root Cause)

### Bug 1 (Critical): `user_id=0` 하드코딩
- **위치**: `base_orchestrator.py:_run_backtest()` line 275
- **원인**: `_run_backtest(card_id, strategy, db)` 호출 시 `user_id=0` 기본값 사용
- **결과**: `backtest_service.py`에서 카드 소유자(user_id=2) != 0 → `OwnershipError` → `except`에서 None 반환 → 파이프라인 중단
- **수정**: `user_id` 파라미터를 `_run_full_pipeline` → `_run_backtest`로 전달

### Bug 2: Pydantic 검증 오류 (LLM 응답 타입 불일치)
- **위치**: `understand_agent.py:_validate_intent()`
- **원인**: LLM이 `target_return_pct`를 `[1.5, 3.0]` (list)으로 반환 → `Optional[float]` 검증 실패
- **수정**: `isinstance(raw_pct, list)` → `max(raw_pct)` 변환 + `capital_hint` 타입 안전 처리

### Bug 3: asyncpg 날짜 타입 바인딩 오류
- **위치**: `backtest_service.py` line 87
- **원인**: asyncpg 바이너리 프로토콜은 `CAST(:string AS date)` 불가 → `'str' object has no attribute 'toordinal'`
- **수정**: `req.start_date[:10]`을 Python `datetime.date` 객체로 변환 후 SQL 바인딩

### Bug 4: 백테스트 성능 문제
- **원인**: `BacktestSimulator.run()` → 거래일마다 3,844종목 전체 로드 (O(n_days * n_stocks) DB 쿼리)
- **결과**: 60일 백테스트에 80초+ 소요 → API 타임아웃
- **수정**: 오케스트레이터 전용 고속 인메모리 백테스트 구현 (데이터 1회 로드, pre-index)

---

## 2. 코드 변경 내역

### `backend/app/services/go100/ai/base_orchestrator.py`
- `_run_full_pipeline`: `user_id`를 `_run_backtest`에 전달
- `_run_backtest`: 완전 재작성 → 고속 인메모리 백테스트
  - 거래일 목록 1회 로드
  - UniverseEngine으로 유니버스 1회 선정 (최대 200종목)
  - ohlcv_daily 벌크 로드 + `stock_code`별 dict 인덱싱
  - stop_loss/take_profit/signal 기반 exit + entry 평가
  - 기간: 최근 60일 (MA 계산용 추가 60일 선로드)
- `_empty_bt_result`: 빈 백테스트 결과 헬퍼 추가
- `_finalize_card`: `last_backtest_id` 포함 + 로깅 강화

### `backend/app/services/go100/ai/understand_agent.py`
- `target_return_pct`: list → `max(list)` 변환
- `capital_hint`: try/except float 변환

### `backend/app/services/go100/backtest/backtest_service.py`
- `CAST(:start_date AS date)` → Python `datetime.date` 객체 직접 바인딩
- `from datetime import date as _date_type` 추가

---

## 3. 전략 백테스트 결과 (Cards 10-12)

| 항목 | Card 10 (스캘핑) | Card 11 (데일리) | Card 12 (스윙) |
|------|------------------|------------------|----------------|
| **전략명** | 코스닥 소형주 3분봉 스캘핑 | 코스피200 골든크로스 스윙 | 중형주 섹터모멘텀 눌림목 스윙 |
| **card_status** | BACKTESTED | BACKTESTED | BACKTESTED |
| **총 수익률** | 7.74% | 14.64% | 5.06% |
| **최대 낙폭 (MDD)** | -8.62% | -2.38% | -1.57% |
| **샤프 비율** | 1.93 | 6.68 | 3.34 |
| **승률** | 63.64% | 62.50% | 54.90% |
| **총 거래 수** | 66 | 104 | 51 |
| **평가 점수** | 77.3 | 85.7 | 71.6 |
| **평가 통과** | YES | YES | YES |
| **최적화 루프** | 0 | 0 | 3 |

---

## 4. 파이프라인 실행 흐름 검증

| 단계 | Card 10 | Card 11 | Card 12 |
|------|---------|---------|---------|
| UNDERSTAND | OK | OK | OK |
| DESIGN | OK | OK | OK |
| BACKTEST | OK (66 trades) | OK (104 trades) | loop 0: 0 trades → loop 1: 0 trades → loop 2: 0 trades → loop 3: 51 trades |
| EVALUATE | passed=True, score=77.3 | passed=True, score=85.7 | loop 0-2: failed → loop 3: passed=True, score=71.6 |
| OPTIMIZE | 불필요 (첫 평가 통과) | 불필요 (첫 평가 통과) | 3회 최적화 실행 |
| FINALIZE | BACKTESTED | BACKTESTED | BACKTESTED |
| PRESENT | OK | OK | OK |

Card 12 (스윙)은 3회 최적화 루프를 거쳐 유니버스 필터 완화 + max_stocks 증가 후 통과.

---

## 5. 테스트 결과

```
129 passed in 1.41s
```

- `test_go100_ai.py`: 12 passed
- `test_go100_backtest.py`: 18 passed
- `test_go100_strategy_card.py`: 10 passed
- `test_go100_advanced_filters.py`: 12 passed
- `test_go100_minute_backtest.py`: 16 passed
- `test_go100_paper_trading.py`: 13 passed
- `test_go100_portfolio_service.py`: 8 passed
- `test_go100_position_sizing.py`: 12 passed
- `test_universe_engine_unit.py`: 10 passed
- 기타: live_trading, risk, scheduler 포함

---

## 6. 컴플라이언스 체크리스트

| 항목 | 상태 |
|------|------|
| `.env/.bak` 커밋 여부 | 미포함 |
| `strategy_cards` 59건 | 59건 유지 |
| `v4_positions` OPEN 수 | 5건 유지 |
| 파일 헤더 | `CUR-GO100-BUNDLE4B-FIX, 2026-02-21` |
| DB 스키마 변경 | 없음 |
| 서비스 재시작 | go100 restart (검증용) |
| V4.1 파일 수정 여부 | 없음 |
