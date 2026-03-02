# CUR-GO100-FIX-BACKEND 보고서
작업일: 2026-02-22

## 백업 경로
`/tmp/backup_FIX_BACKEND_20260222_011703.dump`

## 사전 상태
- go100_strategy_cards: 15건
- Cards 13-15 user_id: 2 ([CEO-EMAIL-GM])
- v4_positions OPEN: 5건

## DB 정리 결과
- 삭제: go100_strategy_cards 12건 (go100_card_id 1~12) 및 자식 레코드  
  (go100_trades 3, go100_positions 6, go100_orders 3, go100_portfolio_snapshots 2, go100_risk_disclaimers 1, go100_portfolios 5)
- 잔여: 3건 (go100_card_id 13, 14, 15)

## user_id
- **STEP 4 변경 실행:** `go100_strategy_cards` 3건(go100_card_id 13, 14, 15)의 `user_id`를 3 ([CEO-EMAIL-NV])으로 변경함. 검증: 3건 모두 user_id=3, email=[CEO-EMAIL-NV].

## 코드 수정
- `backend/app/services/strategy_card_service.py`: CUR-GO100-FIX-BACKEND 헤더 추가, list_cards_with_system 내 GO100 블록에서 `last_backtest_mdd`/`last_backtest_sharpe` 조회, `card_id=go100_card_id`, `backtest_return`/`backtest_mdd`/`backtest_sharpe` 전달
- `backend/app/schemas/strategy_card_schemas.py`: StrategyCardDisplay에 `source` 기본값 "v4", `backtest_return`/`backtest_mdd`/`backtest_sharpe` 필드 추가
- `backend/app/routers/go100/strategy_router.py`: CUR-GO100-FIX-BACKEND 헤더 추가

## 테스트 결과
- pytest: 187 passed, 5 failed (실패 5건은 test_universe_engine.py asyncio 이벤트 루프 선행 이슈, 본 수정과 무관)
- health: `{"status":"ok","version":"4.1.0","database":"connected","redis":"connected"}`
- API 검증: `/api/go100/strategy-cards`, `/api/v1/strategy-cards/catalog` 인증 필요(401). 로그인 후 Catalog 호출 시 GO100 카드에 source "go100" 및 card_id(go100_card_id) 포함됨.

## 컴플라이언스 체크
- [x] go100_strategy_cards 3건만 유지
- [x] v4_positions OPEN 5건 유지
- [x] V4.1 핵심 파일 수정 없음/최소화 (go100_* 및 strategy_card 서비스/스키마만)
- [x] .env/.bak 커밋 없음
- [x] 파일 헤더 주석 포함
- [x] DB 스키마 변경 없음

## 커밋 해시
`e6ea2b2e feat: CUR-GO100-FIX-BACKEND - DB 정리 + Catalog GO100 병합 확정`
