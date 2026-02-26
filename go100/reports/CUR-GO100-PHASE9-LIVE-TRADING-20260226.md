# CUR-GO100-PHASE9-LIVE-TRADING (2026-02-26)

## 목표

페이퍼 트레이딩 검증 완료 후 KIS API 실매매 연동.  
7단계 안전장치 + 사용자 확인 필수.

## 구현 내용

- **DB**: `go100_live_trading_config`, `go100_live_orders`, `go100_live_daily_summary` 테이블 추가 (마이그레이션 `032_go100_live_trading_config.sql`).
- **live_trading 엔진** (`backend/app/services/go100/ai/live_trading.py`):
  - `check_live_eligibility(user_id, db)` — 페이퍼 14일·승률 40%·목표·포트폴리오 존재 여부 검사.
  - `run_safety_check(user_id, order, db)` — 7단계 안전 검사.
  - `submit_order(user_id, order, db)` — 안전 검사 후 PENDING 저장 또는 즉시 KIS 제출.
  - `confirm_order(user_id, order_id, db)` — PENDING → KIS API 주문 → SUBMITTED.
  - `check_filled_orders(user_id, db)` — KIS 당일 체결 조회 후 SUBMITTED → FILLED 갱신.
  - `update_daily_summary(user_id, db)` — 일일 매매 집계 UPSERT.
  - `emergency_stop(user_id, db)` — is_enabled=FALSE, 미체결 전부 취소.
  - `format_live_status(user_id, db)` — 실매매 현황 텍스트·구조 반환.
- **KIS API**: 기존 V4 `KISOrderService(account_mode="real")` 재사용. `place_buy_order`, `place_sell_order`, `cancel_order`, `get_daily_ccld`(당일 체결 조회 추가) 사용.
- **인텐트**: `live_start`, `live_status`, `live_stop`, `live_enable` 추가.  
  - live_start: "실매매 시작하고 싶어" → 적격성 검사 → config 생성(is_enabled=False) → "활성화해줘" 안내.  
  - live_enable: "활성화해줘", "실매매 켜줘" → is_enabled=TRUE.  
  - live_status: "실매매 현황", "오늘 매매" → format_live_status.  
  - live_stop: "매매 중단", "긴급 정지" → emergency_stop.
- **portfolio_status**: 실매매 활성 시 "🔴 실매매 운영 중" 블록 추가.

## 안전장치 7단계

1. 실매매 활성화 여부 (is_enabled)
2. 거래시간 (09:05~15:20)
3. 1건 주문 금액 한도 (기본 100만원)
4. 일일 주문 금액 한도 (기본 500만원)
5. 일일 주문 건수 한도 (기본 10건)
6. 일일 손실률 한도 (circuit breaker, 기본 3%)
7. 종목 보유 한도 (선택, 현재 통과 처리)

## 검증 결과

- 마이그레이션 적용: `go100_live_trading_config`, `go100_live_orders`, `go100_live_daily_summary` 테이블 생성·인덱스 확인.
- `live_trading` 모듈 import 및 8함수 로드 정상.
- 인텐트 라우팅: "실매매 시작하고 싶어" → live_start, "실매매 현황" → live_status, "매매 중단해줘" → live_stop, "활성화해줘" → live_enable.
- go100 서비스 재시작 후 정상 active.
