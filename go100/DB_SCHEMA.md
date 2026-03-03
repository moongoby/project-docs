# GO100 데이터베이스 스키마
> 최종 업데이트: 2026-03-03 | 문서 버전: v1.3

## 1. 접속 정보
- DB: kisautotrade
- User: kis_admin
- Host: localhost:5432

## 2. 전체 테이블 목록 + 행수 (2026-03-03 기준, 주요 테이블)

| table_name | row_count | size | 비고 |
|------------|-----------|------|------|
| **go100_news_items** | **2,253,947** | **2,011 MB** | 뉴스/공시 (2020~현재 백필 중) |
| ohlcv_daily | 2,619,583 | 806 MB | 일봉 OHLCV |
| v4_investor_daily | 279,685 | 194 MB | 수급 데이터 |
| go100_gap_calibrator | 108,574 | 33 MB | 갭 캘리브레이터 |
| go100_fundamentals_pit | 30,917 | 5,952 kB | 재무 PIT |
| go100_data_integrity_log | 22,456 | 5,696 kB | 데이터 무결성 로그 |
| go100_delisted_ohlcv | 24,127 | 4,336 kB | 상장폐지 종목 OHLCV |
| go100_fundamentals | 2,720 | 1,904 kB | 기업 재무 |
| go100_sector_price | 7,047 | 1,232 kB | 섹터 가격 |
| v4_market_regime_daily | 1,116 | 552 kB | 시장 레짐 |
| go100_sector_correlation | 1,624 | 536 kB | 섹터 상관관계 |
| go100_strategy_cards | 42 | 296 kB | 전략 카드 |
| go100_global_market | 297 | 216 kB | 글로벌 시장 |
| go100_user_memory | 47 | 200 kB | AI 에이전트 메모리 |
| go100_backtest_runs | 20 | 192 kB | 백테스트 실행 이력 |
| go100_reports | 316 | 168 kB | 보고서 |
| go100_trades | 1 | 104 kB | 체결 이력 |
| go100_orders | 1 | 96 kB | 주문 이력 |
| go100_live_orders | 14 | 96 kB | 실시간 주문 |
| accounts | 7 | — | 계좌 (KIS/키움) |
| strategy_cards (레거시) | 62 | — | V4 레거시 |

## 3. GO100 테이블 상세

### go100_news_items ★ (2026-03-03 신규 문서화)
> KIS OpenAPI `FHKST01011800` 뉴스/공시 수집 데이터

| column_name | data_type | nullable | 설명 |
|-------------|-----------|----------|------|
| id | bigint | NO | PK (auto increment) |
| srno | varchar(30) | NO | 뉴스 일련번호 (UNIQUE) |
| provider_code | varchar(2) | NO | 언론사 코드 (6=연합, A=매경, 2=한경 등) |
| provider_name | varchar(30) | YES | 언론사명 |
| data_date | date | NO | 뉴스 날짜 |
| data_time | time | NO | 뉴스 시각 |
| title | text | NO | 뉴스 제목 |
| category_code | varchar(20) | YES | 카테고리 코드 |
| stock_code1~3 | varchar(12) | YES | 연관 종목 코드 (최대 3개) |
| stock_name1~3 | varchar(40) | YES | 연관 종목명 (최대 3개) |
| is_disclosure | boolean | YES | 공시 여부 (F/G/H/I/N 채널) |
| raw_json | jsonb | YES | API 원본 JSON 전체 |
| collected_at | timestamptz | YES | 수집 시각 |

**인덱스**:
- PK: `id`
- UNIQUE: `srno`
- `idx_go100_news_date`: `data_date DESC`
- `idx_go100_news_stock`: `stock_code1` (not null)
- `idx_go100_news_disclosure`: `(is_disclosure, data_date DESC)` WHERE is_disclosure=true

**수집 현황** (2026-03-03):
- 총 건수: 2,253,947건 (백필 진행 중, 완료 시 ~750만건 예상)
- 범위: 2024-07-15 ~ 2026-03-02 (백필 완료 시 2020-01-02~)
- 공시: 159,467건, 언론사: 26개사
- 크기: 2,011 MB

**수집 체계**:
- 일일: 매 평일 17:10 크론 (`scripts/cron/collect_news_daily.sh`)
- 주간 보정: 매주 일요일 02:00 크론 (`scripts/cron/backfill_news_missing.sh`)
- 과거 백필: `scripts/cron/backfill_news_history.sh` (2020-01-02~)

**뉴스 본문**: KIS OpenAPI 미제공 (404), 키움 REST 미지원 — 제목만 수집 가능

---

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
| 2 | [CEO-EMAIL-GM] | 대표님 |
| 3 | [CEO-EMAIL-NV] | 오병용 |
| 4 | test-signup-cur@test.com | 테스트 |

### legacy users (12건, id/email/name)
| id | email | name |
|----|-------|------|
| 6 | [CEO-EMAIL-GM] | 대표님 |
| 15 | [CEO-EMAIL-NV] | 오병용 |
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
