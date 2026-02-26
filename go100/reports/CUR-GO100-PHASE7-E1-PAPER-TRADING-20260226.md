# CUR-GO100-PHASE7-E1-PAPER-TRADING 보고서 (2026-02-26)

## 목표
백테스트 → 실매매 사이의 **페이퍼 트레이딩** 단계 구현. 가상 자금으로 전략을 실제 시장 데이터에 실시간 적용하여 실전 성과를 검증. 실계좌 연동 없이 매매 시뮬레이션만 수행.

## 완료 항목

### 1. DB 스키마 (4개 테이블)
- **go100_paper_accounts**: 페이퍼 계좌 (user_id, portfolio_id, initial_capital, current_cash, current_value, status)
- **go100_paper_orders**: 페이퍼 주문 (account_id, card_id, stock_code, order_type, quantity, target_price, filled_price, status=PENDING/FILLED)
- **go100_paper_positions**: 페이퍼 포지션 (account_id, card_id, stock_code, quantity, avg_price, current_price, unrealized_pnl, status=OPEN/CLOSED)
- **go100_paper_snapshots**: 일일 스냅샷 (account_id, snapshot_date, total_value, cash, daily_pnl, cumulative_pnl_pct, drawdown_pct, peak_value)

마이그레이션: `backend/migrations/012_go100_paper_trading.sql`

### 2. 신규 모듈 `backend/app/services/go100/ai/paper_trading.py`
| 함수 | 설명 |
|------|------|
| `create_paper_account(user_id, portfolio_id, capital, db)` | 페이퍼 계좌 생성 → account_id |
| `run_daily_signals(account_id, db)` | 전략 카드 entry_rules/exit_rules 적용, 신호 생성 후 PENDING 주문 INSERT |
| `fill_orders(account_id, db)` | PENDING 주문 당일 시가 기준 체결 (슬리피지 0.1%, 수수료/세금 반영) |
| `update_positions(account_id, db)` | 보유 포지션 종가 기준 시가평가, current_value 갱신 |
| `take_snapshot(account_id, db)` | 일일 스냅샷 저장 (peak_value, drawdown_pct) |
| `get_paper_performance(account_id, days, db)` | 성과 조회 (수익률, MDD, 승률, KOSPI 대비, daily_snapshots) |
| `get_paper_positions(account_id, db)` | 보유 현황 (종목별 손익, 보유일) |

### 3. 크론 스크립트 `scripts/go100/paper_trading_daily.py`
- 매일 장마감 후: ACTIVE 페이퍼 계좌 조회 → `fill_orders` → `run_daily_signals` → `update_positions` → `take_snapshot`
- 실행: `.venv/bin/python scripts/go100/paper_trading_daily.py` (전체) 또는 `--account-id 1` (단일)
- 크론 예시: `10 16 * * 1-5` (16:10, 월~금)

### 4. ai_router 연동
- **인텐트**: paper_start, paper_status, paper_pause (C2SC + 키워드)
- **키워드**: "페이퍼 시작"/"가상매매 시작" → paper_start, "페이퍼 현황"/"가상매매 성과" → paper_status, "페이퍼 중단" → paper_pause
- **portfolio_status**: ACTIVE 페이퍼 계좌 있으면 "💰 페이퍼 트레이딩 (운영 N일차)" 블록 자동 표시
- **모닝 브리핑**: 페이퍼 PENDING 주문이 있으면 "⚡ 오늘 매매 신호: OO 매수, OO 익절" 추가

### 5. 검증
- `012_go100_paper_trading.sql` 적용 완료
- `paper_trading_daily.py` 실행 시 "No ACTIVE paper accounts to process" 정상 동작
- create_paper_account / get_paper_performance / get_paper_positions 단위 동작 (포트폴리오 없는 유저는 스킵)

## 기술 요약
- **신호 생성**: go100_portfolio_allocations + go100_strategy_cards의 entry_rules/exit_rules/risk_params, SignalEvaluator + ohlcv_daily
- **체결**: 시가 기준 + 슬리피지 0.1% + 매수 수수료 0.015% + 매도 수수료 0.015% + 세금 0.18%
- **스냅샷**: UNIQUE(account_id, snapshot_date) ON CONFLICT DO UPDATE

## Git
- kis-autotrade-v4: phase-2c-command-center 브랜치 커밋
- project-docs: master 브랜치 보고서 커밋
