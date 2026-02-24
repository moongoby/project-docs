# GO100 API 명세
> 최종 업데이트: 2026-02-23 | 문서 버전: v1.0

## 1. 인증
- POST /api/v1/auth/login → access_token (JWT, 24h)
- Header: Authorization: Bearer {token}

## 2. GO100 전략카드 (/api/go100/strategy-cards)
- POST / — 생성
- GET / — 목록
- GET /{id} — 상세
- PUT /{id} — 수정
- DELETE /{id} — 삭제
- PATCH /{id}/toggle — 활성/비활성

## 3. AI 대화 (/api/go100/ai)
- POST /chat — 백억이 대화

## 4. 백테스트 (/api/go100/backtest)
- POST /run — GO100 백테스트

## 5. Catalog (/api/v1/strategy-cards)
- GET /catalog?tab=all|my|v4
- GET /for-backtest

## 6. 기타 GO100 라우터
- /api/go100/portfolios — 포트폴리오
- /api/go100 (store_router) — 스토어
- /api/go100/paper-trading — 모의거래
- /api/go100/live-trading — 실거래
- /api/go100/risk — 리스크
- /api/go100/scheduler — 스케줄러
- /api/go100/optimizer — 최적화

## 7. 헬스체크
- GET /health → {"status":"ok","version":"4.1.0","orchestrator_state":"IDLE","database":"connected","redis":"connected"}

## 8. 자동매매 모달 (/api/go100/trade) — CUR-GO100-TRADE-MODAL-IMPL-001, 2026-02-24
- POST /api/go100/trade/start — 자동매매 시작 (go100_card_id, account_id, invest_amount?, max_stocks?, stop_loss_pct?, take_profit_pct?)
- POST /api/go100/trade/stop — 자동매매 중지 (go100_card_id)
- GET /api/go100/trade/status/{card_id} — 카드별 자동매매 상태
- GET /api/go100/trade/accounts — 활성 계좌 목록

## 9. 알림 시스템 (/api/go100/notifications) — CUR-GO100-NOTIFICATION-SYSTEM-001, 2026-02-24
- GET /api/go100/notifications — 알림 목록 (limit, offset, unread_only, type)
- GET /api/go100/notifications/unread-count — 읽지 않은 수
- PATCH /api/go100/notifications/{id}/read — 단일 읽음
- POST /api/go100/notifications/read-all — 전체 읽음
- GET /api/go100/notifications/stream — SSE 실시간 스트림 (?token=)
- GET /api/go100/notifications/settings — 알림 설정 조회
- PUT /api/go100/notifications/settings — 알림 설정 수정
- POST /api/go100/notifications/push-subscribe — 푸시 구독 등록
- DELETE /api/go100/notifications/push-subscribe — 푸시 구독 해제
- POST /api/go100/notifications/test — 테스트 알림 발송
