# GO100 DB 스키마
> 자동 생성일: 2026-02-23

go100_ 접두사 테이블 + 공유 테이블 구조입니다.
상세는 [전체 스키마](../kis-autotrade-v4/docs/DB-SCHEMA.md) 참조.

- **accounts**: 7 rows, 144 kB
- **go100_account_reconciliation**: 0 rows, 32 kB
- **go100_backtest_runs**: 0 rows, 80 kB
- **go100_desk_allocation**: 2 rows, 32 kB
- **go100_fit_analysis**: 40 rows, 80 kB
- **go100_orders**: 0 rows, 80 kB
- **go100_portfolio_snapshots**: 0 rows, 56 kB
- **go100_portfolios**: 0 rows, 56 kB
- **go100_positions**: 0 rows, 72 kB
- **go100_risk_disclaimers**: 0 rows, 64 kB
- **go100_strategy_cards**: 6 rows, 224 kB
- **go100_trades**: 0 rows, 88 kB
- **index_daily**: 1467 rows, 400 kB
- **strategy_cards**: 60 rows, 312 kB
- **users**: 12 rows, 80 kB
- **v4_users**: 6 rows, 96 kB

## 알림 시스템 테이블 (CUR-GO100-NOTIFICATION-SYSTEM-001, 2026-02-24)

### go100_notifications
- id BIGSERIAL PK, user_id INTEGER NOT NULL, type VARCHAR(50) NOT NULL
- title VARCHAR(200), message TEXT, data JSONB, priority VARCHAR(10) DEFAULT 'NORMAL'
- is_read BOOLEAN DEFAULT FALSE, is_email_sent BOOLEAN, is_push_sent BOOLEAN
- channel VARCHAR(20) DEFAULT 'IN_APP', created_at TIMESTAMPTZ, read_at TIMESTAMPTZ
- INDEX: (user_id, is_read, created_at), (user_id, type), (created_at)

### go100_notification_settings
- id BIGSERIAL PK, user_id INTEGER NOT NULL UNIQUE
- in_app_enabled, email_enabled, push_enabled BOOLEAN
- trade_executed, stop_loss_triggered, take_profit_triggered, backtest_completed, optimize_completed, daily_summary, scheduler_error, system_alert BOOLEAN
- email_override VARCHAR(200), created_at, updated_at TIMESTAMPTZ

### go100_push_subscriptions
- id BIGSERIAL PK, user_id INTEGER NOT NULL
- endpoint TEXT, p256dh TEXT, auth TEXT
- user_agent VARCHAR(500), is_active BOOLEAN DEFAULT TRUE
- UNIQUE(user_id, endpoint)