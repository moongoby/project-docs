# CUR-GO100-P2-1: Experience Log DB 구현 — 경험 축적 시스템

**작성일**: 2026-02-27  
**태스크**: P2-1 Experience Log DB  
**선행 조건**: P1-1 완료 (GO100_AGENT_MODE=true), DB_SCHEMA.md 반영

---

## 1. 요약

- **목표**: `go100_agent_experience_log` 테이블 생성 및 백테스트/스크리닝 완료 시 자동 기록 Hook 구현
- **테이블명**: 기존 `go100_experience_log`는 트레이드 단위 상세 로그용 별도 스키마로 존재하여, P2-1 에이전트 경험 로그용으로 **`go100_agent_experience_log`** 신규 생성

---

## 2. 구현 내역

### 2.1 테이블 생성 (1단계)

**파일**: `backend/migrations/034_go100_experience_log.sql`

```sql
CREATE TABLE IF NOT EXISTS go100_agent_experience_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- BACKTEST | PAPER_TRADE | LIVE_TRADE | SCREENING | ANALYSIS
    context JSONB DEFAULT '{}',       -- regime, vkospi, market_cap, sector, cross_signals
    action JSONB DEFAULT '{}',        -- stock_code, direction, strategy_type, filter_used
    outcome JSONB DEFAULT '{}',      -- return_pct, pnl, holding_days, max_drawdown
    confidence FLOAT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_exp_event ON go100_agent_experience_log(event_type);
CREATE INDEX IF NOT EXISTS idx_agent_exp_user_date ON go100_agent_experience_log(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_agent_exp_context ON go100_agent_experience_log USING GIN(context);
```

- **인덱스**: `event_type`, `(user_id, created_at)`, GIN(`context`)  
- **실행**: `psql -h localhost -U kis_admin -d kisautotrade -f backend/migrations/034_go100_experience_log.sql` → 성공

### 2.2 기록 서비스 (2단계)

**파일**: `backend/app/services/go100/memory/experience_logger.py`

| 항목 | 내용 |
|------|------|
| **동작 조건** | `GO100_AGENT_MODE=true` 일 때만 INSERT, 아니면 no-op |
| **공통** | `log(db, user_id, event_type, context, action, outcome, confidence, notes)` → `go100_agent_experience_log`에 삽입 후 commit |
| **BACKTEST** | `log_backtest(db, user_id, run_id, go100_card_id, strategy_name, result, start_date, end_date)` — action에 run_id/card/기간, outcome에 수익률·MDD·거래수 등 |
| **SCREENING** | `log_screening(db, user_id, screening_type, filter_used, results_count, query_time_ms, extra)` — action에 필터/타입, outcome에 건수·소요시간 |

- `event_type` 검증: `BACKTEST`, `PAPER_TRADE`, `LIVE_TRADE`, `SCREENING`, `ANALYSIS` 만 허용  
- JSONB 필드: `context` / `action` / `outcome` 는 dict 또는 JSON 문자열로 전달 가능, 내부에서 `_ensure_dict`로 정규화

### 2.3 백테스트 완료 시 자동 기록 Hook (3단계)

**파일**: `backend/app/services/go100/backtest/backtest_service.py`

- `execute_backtest()` 내부: DB commit 및 알림 발송 후, `log_backtest()` 호출
- 전달 값: `user_id`, `run_id`, `req.go100_card_id`, `row["strategy_name"]`, `result`(시뮬레이터 결과), `req.start_date`, `req.end_date`
- 예외 시 로그만 남기고 백테스트 응답에는 영향 없음

### 2.4 스크리닝 실행 시 자동 기록 Hook (4단계)

**파일**: `backend/app/services/go100/screening_engine.py`, `backend/app/routers/go100/ai_router.py`

- **screening_engine**
  - `run_screening(..., user_id: Optional[int] = None)` 인자 추가
  - `theme` / `combined` / 단일 필터 / fallback 각 분기에서 결과 반환 직전에 `_experience_log_screening()` 호출
  - `_experience_log_screening()`: `log_screening()` 래퍼, 예외 시 `logger.debug` 만 남김
- **ai_router**
  - `_handle_stock_screening(message, db, user_id=current_user["user_id"])` 로 변경하여 `user_id` 전달
  - 스크리닝 호출부: `run_screening(db, screening_type, extra, user_id=current_user["user_id"])`

---

## 3. 검증

- 마이그레이션 실행: **성공**
- 검증 쿼리 (신규 테이블 기준):

```sql
SELECT COUNT(*) FROM go100_agent_experience_log;
-- 0 (초기 상태)

SELECT event_type, COUNT(*) FROM go100_agent_experience_log GROUP BY event_type;
-- (0 rows)
```

- **동작 확인 방법**
  - `GO100_AGENT_MODE=true` 로 백테스트 완료 → `event_type='BACKTEST'` 1건 증가
  - 동일 환경에서 스크리닝 실행 → `event_type='SCREENING'` 1건 증가  
  - `GO100_AGENT_MODE=false` 시 두 경우 모두 INSERT 없음 (카운트 변화 없음)

---

## 4. 파일 변경 목록

| 파일 | 변경 내용 |
|------|-----------|
| `backend/migrations/034_go100_experience_log.sql` | 신규 (go100_agent_experience_log 테이블 + 인덱스 3개) |
| `backend/app/services/go100/memory/experience_logger.py` | 신규 (log, log_backtest, log_screening) |
| `backend/app/services/go100/backtest/backtest_service.py` | execute_backtest 내 log_backtest 호출 추가 |
| `backend/app/services/go100/screening_engine.py` | run_screening에 user_id 추가, _experience_log_screening 호출 |
| `backend/app/routers/go100/ai_router.py` | _handle_stock_screening에 user_id 인자 및 run_screening에 user_id 전달 |

---

## 5. 참고

- **기존 go100_experience_log**: 트레이드/백테스트 상세용 별도 스키마(source, strategy_card_id, stock_code, entry_date 등). P2-1 에이전트 경험 로그와 분리하여 **go100_agent_experience_log** 사용.
- **DB_SCHEMA.md**: 필요 시 `go100_agent_experience_log` 테이블 설명 추가 권장.
- **PAPER_TRADE / LIVE_TRADE / ANALYSIS**: 테이블·로거는 지원, 호출부는 추후 해당 플로우 구현 시 연동 가능.
