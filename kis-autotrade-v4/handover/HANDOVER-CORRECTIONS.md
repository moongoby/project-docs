# HANDOVER-V51 정정 사항

## DB 관련
| 항목 | 인수인계서 기재 | 실제 확인 | 확인일 |
|------|----------------|----------|--------|
| DB명 | kis_autotrading | **kisautotrade** | 2026-02-14 |
| v4 테이블 수 | 7개 | **16개** | 2026-02-14 |
| v4 테이블 행 수 | 70~71행 | 테이블별 상이 | 2026-02-14 |
| users.username | 존재 전제 | **미존재**, name 컬럼 사용 | 2026-02-13 |
| users.email_verified | 존재 전제 | **미존재**, is_verified 사용 | 2026-02-14 |
| v4_backtest_results | 존재 전제 | **미존재** | 2026-02-14 |
| v4_system_heartbeat.cycle_count | 미존재 가정 | **존재** (cycle_id도 존재) | 2026-02-14 |

## 추가 확인된 v4 테이블 (인수인계서 누락)
v4_bet_history, v4_market_calendar, v4_order_requests, v4_position_extended,
v4_positions, v4_reservations, v4_theme_activity_daily, v4_theme_stock_mapping, v4_vkospi_daily

## ORM 모델 확인
| 클래스 | 파일 | 테이블 |
|--------|------|--------|
| V4Position | models/position.py | v4_positions |
| V4PositionExtended | models/position.py | v4_position_extended |
| SystemStateLog | models/system.py | v4_system_state_log |
| SystemHeartbeat | models/system.py | v4_system_heartbeat |
| MarketRegimeDaily | models/market.py | v4_market_regime_daily |
| MarketCalendar | models/market.py | v4_market_calendar |
| Reservation | models/execution.py | v4_reservations |
