# GO100 데이터베이스 스키마
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.0

## 1. 접속 정보
- DB: kisautotrade
- User: kis_admin
- Host: localhost:5432

## 2. 전체 테이블 목록 + 행수 (public 스키마, 일부)
| table_name | row_count |
|------------|-----------|
| account_rate_quotas | 7 |
| account_snapshots | 466 |
| accounts | 7 |
| go100_account_reconciliation | 0 |
| go100_backtest_runs | 0 |
| go100_desk_allocation | 2 |
| go100_fit_analysis | 40 |
| go100_orders | 0 |
| go100_portfolio_snapshots | 0 |
| go100_portfolios | 0 |
| go100_positions | 0 |
| go100_risk_disclaimers | 0 |
| go100_strategy_cards | 3 |
| go100_trades | 0 |
| strategy_cards | 62 |
| users | 12 |
| v4_users | 4 |
| v4_positions | 24 |
| ... | (기타 v4_*, backtest, ohlcv 등 100개 이상) |

## 3. GO100 테이블 상세

### go100_strategy_cards
| column_name | data_type | is_nullable | column_default |
|-------------|-----------|-------------|----------------|
| go100_card_id | bigint | NO | nextval(...) |
| user_id | integer | NO | |
| account_id | integer | YES | |
| strategy_name | character varying | NO | |
| strategy_type | character varying | NO | 'CUSTOM' |
| universe_filter | jsonb | YES | '{}' |
| entry_rules | jsonb | YES | '[]' |
| exit_rules | jsonb | YES | '[]' |
| risk_params | jsonb | YES | '{}' |
| strategy_params | jsonb | YES | '{}' |
| allocated_amount | numeric | YES | 0 |
| max_stocks | integer | YES | 5 |
| card_status | character varying | NO | 'IDEA' |
| is_active | boolean | YES | true |
| is_live | boolean | YES | false |
| is_featured | boolean | NO | false |
| is_public | boolean | NO | false |
| featured_order | integer | NO | 0 |
| source_type | character varying | YES | 'CUSTOM' |
| source_store_card_id | bigint | YES | |
| source_user_id | integer | YES | |
| llm_session_id | character varying | YES | |
| last_backtest_id | bigint | YES | |
| last_backtest_return | numeric | YES | |
| last_backtest_mdd | numeric | YES | |
| last_backtest_sharpe | numeric | YES | |
| last_backtest_at | timestamp with time zone | YES | |
| paper_* | (다수) | YES | |
| disclaimer_agreed | boolean | YES | false |
| dedicated_account | boolean | YES | false |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

### go100_backtest_runs
| column_name | data_type | is_nullable | column_default |
|-------------|-----------|-------------|----------------|
| id | bigint | NO | nextval(...) |
| user_id | integer | NO | |
| go100_card_id | bigint | YES | |
| strategy_name | character varying | YES | |
| stock_codes_used | ARRAY | YES | |
| universe_filter_snapshot | jsonb | YES | |
| start_date | date | NO | |
| end_date | date | NO | |
| initial_capital | bigint | YES | 10000000 |
| total_return | numeric | YES | |
| annualized_return | numeric | YES | |
| max_drawdown | sharpe_ratio | win_rate | total_trades | profit_factor | avg_holding_days | (기타) | ...
| status | character varying | YES | 'PENDING' |
| created_at | completed_at | ...

### go100_portfolios, go100_positions, go100_orders, go100_trades
- portfolio_id/user_id/account_id/go100_card_id 기반 실거래·모의거래 포트폴리오 및 주문/포지션/체결 이력.

### go100_account_reconciliation, go100_desk_allocation, go100_fit_analysis, go100_risk_disclaimers
- 계정 정합성, 데스크 배분, 종목 적합도 분석, 리스크 면책 동의.

### go100_strategy_store
- store_card_id, strategy_name, strategy_type, entry_rules, exit_rules, risk_params, strategy_params, desk_id, backtest_compatible, created_at (뷰 또는 스토어용).

## 4. 주요 공유 테이블

### v4_users
| column_name | data_type | is_nullable |
|-------------|-----------|-------------|
| user_id | bigint | NO |
| email | character varying | NO |
| nickname | character varying | NO |
| hashed_password | character varying | NO |
| tier | character varying | NO | 'FREE' |
| is_active | boolean | NO | true |
| last_login_at | timestamp with time zone | YES |
| created_at | updated_at | phone | YES |

### strategy_cards (V4 레거시)
| column_name | data_type |
|-------------|-----------|
| card_id | bigint |
| user_id | bigint |
| account_id | bigint |
| strategy_name | strategy_type | strategy_params | allocated_amount | max_stocks | is_live | is_active | desk_id | entry_rules | exit_rules | risk_params | buy_phases | sell_phases | promotion_rules | demotion_rules | backtest_compatible | priority | version | created_at | updated_at |

### accounts
| column_name | data_type |
|-------------|-----------|
| account_id | bigint |
| user_id | bigint |
| broker_type | account_number | account_alias | is_mock | enc_app_key | enc_app_secret | enc_token | token_expires_at | kis_config_id | daily_order_limit | buy_blocked | is_active | created_at | updated_at |

## 5. 현재 데이터

### go100_strategy_cards (3건)
| go100_card_id | strategy_name | user_id | card_status | is_active | is_featured | is_public | featured_order | created_at |
|---------------|---------------|---------|-------------|-----------+-------------|-----------+----------------+------------|
| 13 | [스캘핑] 분봉 스캘핑 고변동 대형주 | 3 | BACKTESTED | t | t | t | 1 | 2026-02-21 21:39:20+09 |
| 14 | [데일리] 대형 우량주 수급 데일리 전략 | 3 | BACKTESTED | t | t | t | 2 | 2026-02-21 21:47:10+09 |
| 15 | [단기스윙] 섹터모멘텀 외국인수급 스윙 | 3 | BACKTESTED | t | t | t | 3 | 2026-02-21 21:48:21+09 |

### v4_users (4건)
| user_id | email | nickname |
|---------|-------|----------|
| 1 | system@mytrader.ai | SYSTEM_V4_LEGACY |
| 2 | moongoby@gmail.com | 대표님 |
| 3 | moongoby@naver.com | 오병용 |
| 4 | test-signup-cur@test.com | 테스트 |

### legacy users (12건, id/email/name)
| id | email | name |
|----|-------|------|
| 6 | moongoby@gmail.com | 대표님 |
| 15 | moongoby@naver.com | 오병용 |
| ... | (기타 10건) |

### 주요 카운트
| tbl | count |
|-----|-------|
| go100_strategy_cards | 3 |
| strategy_cards | 62 |
| v4_positions_open | 5 |
| go100_backtest_runs | 0 |
| accounts | 7 |

## 6. user_id 매핑 주의
- JWT user_id가 legacy(users.id)일 수 있음.
- get_effective_uid()로 v4_users.user_id 변환 필수.
- legacy 15 → v4 3 (naver), legacy 6 → v4 2 (gmail).
