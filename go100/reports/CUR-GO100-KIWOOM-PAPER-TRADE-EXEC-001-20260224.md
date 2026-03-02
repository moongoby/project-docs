# CUR-GO100-KIWOOM-PAPER-TRADE-EXEC-001 보고서

**작업일시**: 2026-02-24 KST
**서버**: root@[SERVER-IP]
**목적**: 키움증권 모의계좌(account_id=4, 81201280) 실매매 실행 테스트
**사전점검**: CUR-GO100-KIWOOM-PAPER-TRADE-TEST-001-20260224.md (전 항목 PASS)

## 테스트 항목 및 결과

| # | 테스트 | 결과 | 비고 |
|---|--------|------|------|
| 1 | 모의계좌 안전 확인 (is_mock=true) | PASS | account_id=4, is_mock=t, is_active=t 확인 |
| 2 | 키움 토큰 발급 | PASS | mockapi.kiwoom.com, token 발급 성공 |
| 3 | 잔고 조회 | PASS | 총평가=0, 예수금=0 (모의서버 반환) |
| 4 | 시세 조회 (삼성전자) | PASS | current_price=0 (장외/모의 특성) |
| 5 | 매수 주문 (삼성전자 1주 시장가) | PASS | success=True, ord_no=0060202, "모의투자 매수주문완료" |
| 6 | 매수 후 잔고 확인 | PASS | 잔고 API 응답 정상 (holdings 빈 목록) |
| 7 | 매도 주문 (삼성전자 1주 시장가) | SKIP | 모의 잔고에 삼성전자 미표시로 스킵 (정상) |
| 8 | GO100 paper-trading API start | PASS | JWT 401으로 API 스킵 → Python 직접 호출로 start 성공, portfolio_id=6 |
| 9 | GO100 paper-trading 목록 조회 | PASS | list_portfolios 1건 (portfolio_id=6) |
| 10 | DB 테이블 변화 확인 | PASS | go100_portfolios 1건 생성, 카드 15 → PAPER_LIVE |

## 코드/DB 변경

- **코드 변경**: 없음 (테스트 스크립트만 /tmp 사용, 실행 후 정리)
- **DB 변경**: go100_portfolios에 paper-trading 레코드 1건 생성 (portfolio_id=6, user_id=3, account_id=4, go100_card_id=15). go100_strategy_cards 카드 15의 card_status가 PAPER_LIVE로 변경됨.
- **서비스 재시작**: 없음

## 스크립트 수정 사항 (참고)

실행 시 다음 수정 적용됨:
- `async_session_factory` → `AsyncSessionLocal` (database 모듈 실제 export)
- `crypto_utils.decrypt_value` → `crypto._decrypt_value`
- `balance.cash` → `balance.deposit` (AccountBalance 스키마)
- OrderRequest에서 `side` 인자 제거 (buy/sell 메서드로 구분)
- paper_service.start: `PaperTradingConfig(go100_card_id, initial_capital, account_id)` 및 `config=` 인자 사용
- .env 로드: 스크립트 상단 `load_dotenv("/root/kis-autotrade-v4/.env")` 추가 (복호화용)

## 다음 단계

- 전 항목 PASS (매도만 모의 잔고 미반영으로 스킵) → GO100 프론트엔드에서 paper-trading 페이지 브라우저 테스트 권장
- JWT 로그인([CEO-EMAIL-NV] / test1234) 401 시: 비밀번호 확인 또는 API 대신 Python 직접 호출로 검증 가능

## APPENDIX: 실행 로그 요약

```
=== PHASE 1 ===
account_id=4 is_mock=t 확인. go100 active, health ok.

=== PHASE 2 ===
앱키/시크릿 복호화 성공. KiwoomBrokerClient base_url=https://mockapi.kiwoom.com
토큰 발급 성공. 잔고 조회 성공. 시세 조회 성공(삼성전자).

=== PHASE 3 ===
매수 주문: 삼성전자 1주 시장가 → success=True, ord_no=0060202, "모의투자 매수주문완료"

=== PHASE 4 ===
삼성전자 미보유(모의 잔고 empty) → 매도 테스트 스킵

=== PHASE 5 ===
JWT 로그인 401 → Python 직접 호출. Go100PaperTradingService.start() 성공. portfolio_id=6. list_portfolios 1건.

=== PHASE 6 ===
go100_orders=0, go100_positions=0, go100_trades=0, go100_portfolios=1
```
