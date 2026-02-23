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
