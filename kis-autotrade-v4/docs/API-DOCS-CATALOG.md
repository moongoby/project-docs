# API 문서 카탈로그
> 최종 갱신: 2026-02-23
> 서버 경로: /root/kis-autotrade-v4/docs/api/

## 1. 문서 보관 원칙
- API 문서 원본(xlsx, pdf)은 **서버 로컬에만 보관** (용량 문제로 Git에 올리지 않음)
- 이 카탈로그 파일만 project-docs에 등록하여 어떤 문서가 있는지 인계 가능하게 함
- 원본 필요 시 서버 `/root/kis-autotrade-v4/docs/api/`에서 직접 확인

## 2. KIS (한국투자증권) API 문서

### 서버 경로: /root/kis-autotrade-v4/docs/api/kisapi/

| # | 파일명 | 크기 | 내용 요약 | 주요 시트/섹션 |
|---|--------|------|----------|---------------|
| 1 | [국내주식] 기본시세.xlsx | 121K | 종목 현재가, 체결가, 호가, 일/주/월봉, 분봉, 시간외 시세 등 기본 시세 조회 API | API 목록, 주식현재가 시세(FHKST01010100), 주식현재가 시세2, 국내주식기간별시세(일_주_월_년), 주식당일/일별분봉조회 |
| 2 | [국내주식] 순위분석.xlsx | 118K | 거래량·등락률·시가총액·호가잔량·체결강도·공매도 등 순위 API | API 목록, 거래량순위, 국내주식 등락률 순위, 국내주식 시가총액 상위 등 |
| 3 | [국내주식] 시세분석.xlsx | 120K | 일/주/월봉, 투자자별 매매동향, 프로그램매매, 신용잔고·공매도 추이 등 | API 목록, 종목조건검색, 관심종목, 종목별 투자자매매동향(일별), 국내주식 신용잔고 일별추이 등 |
| 4 | [국내주식] 실시간시세.xlsx | 92K | 웹소켓 실시간 체결/호가/예상체결/회원사/장운영정보 (KRX·통합·NXT) | API 목록, 국내주식 실시간체결가(KRX), 실시간호가(KRX), 실시간체결통보 등 |
| 5 | [국내주식] 업종_기타.xlsx | 88K | 업종 현재·일자별·시간별 지수, 분봉, 휴장일, VI 현황, 금리 등 | API 목록, 국내업종 현재지수, 일자별지수, 국내휴장일조회 등 |
| 6 | [국내주식] 종목정보.xlsx | 146K | 종목 마스터, 재무(대차대조표/손익계산서/재무비율), 배당·예탁원일정, 투자의견 등 | API 목록, 상품기본조회, 주식기본조회, 국내주식 재무비율, 예탁원정보(배당일정) 등 |
| 7 | [국내주식] 주문_계좌.xlsx | 122K | 매수/매도 주문(현금·신용), 정정취소, 잔고조회, 예수금, 미체결, 예약주문 등 | API 목록, 주식주문(현금) TTTC0012U/0011U, 주식잔고조회 TTTC8434R, 주식정정취소 TTTC0013U 등 |
| 8 | OAuth인증.xlsx | 14K | 토큰 발급/폐기, Hashkey, 실시간 웹소켓 접속키 발급 | API 목록, 접근토큰발급(P), 접근토큰폐기(P), Hashkey, 실시간 접속키 발급 |

### V4.1에서 사용 중인 KIS API (코드 매핑)

| API 카테고리 | TR_ID/엔드포인트 예시 | 사용 파일 | 용도 |
|-------------|----------------------|----------|------|
| OAuth 토큰 | POST /oauth2/tokenP | token_manager.py, kis_order_service.py, v4_order_executor.py, balance_sync_service.py, position_monitor.py | 토큰 발급/갱신 |
| 주문 매수 | TTTC0012U / VTTC0012U | kis_order_service.py, v4_order_executor.py, kis_api_registry.py | 현금 매수 |
| 주문 매도 | TTTC0011U / VTTC0011U | kis_order_service.py, v4_order_executor.py, kis_api_registry.py | 현금 매도 |
| 주문 취소/정정 | TTTC0013U / VTTC0013U | kis_order_service.py, v4_order_executor.py | 정정·취소 |
| 잔고 조회 | TTTC8434R / VTTC8434R | account_sync_manager.py, balance_sync_service.py, kis_order_service.py, v4_order_executor.py | 포지션/잔고 조회 |
| 매수가능 조회 | TTTC8908R / VTTC8908R | account_sync_manager.py, v4_order_executor.py, kis_api_registry.py | 매수가능 수량 |
| 미체결 조회 | TTTC8001R / VTTC8001R | kis_order_service.py, v4_order_executor.py | 일별 주문체결 조회 |
| 현재가 시세 | FHKST01010100 | position_monitor.py, broker_kis_adapter.py, market_data_service.py, fundamental_collector.py, orderbook_collector 근접 | 주식현재가 시세 |
| 호가/예상체결 | FHKST01010200 | orderbook_collector.py, kis_api_registry.py | 호가 조회 |
| 일봉 | FHKST03010100 | ohlcv_collector.py, collect_ohlcv_daily.py, kis_api_registry.py | 국내주식기간별시세(일봉) |
| 분봉 | FHKST03010230 | collector_minute.py, collector_minute_ohlcv.py, kis_api_registry.py | 주식일별분봉조회 |
| 투자자 매매 | FHKST01010900 | investor_collector.py, kis_api_registry.py | 종목별 투자자 매매동향 |
| 회원사 매매 | FHKST01010600 | broker_trades_collector.py, kis_api_registry.py | 거래원(증권사)별 매매 |
| 신용잔고 | FHKST17010000 | credit_balance_collector.py | 신용잔고 상위 |

## 3. 키움증권 API 문서

### 서버 경로: /root/kis-autotrade-v4/docs/api/

| # | 파일명 | 크기 | 내용 요약 |
|---|--------|------|----------|
| 1 | 키움 REST API 문서.pdf | 15M | 키움 REST API 전체 (OAuth, 주문, 잔고, 시세, 차트, 테마/섹터/ETF/ELW 등) |

### V4.1에서 사용 중인 키움 API (코드 매핑)

| API 카테고리 | 엔드포인트 / api_id | 사용 파일 | 용도 |
|-------------|---------------------|----------|------|
| OAuth 토큰 | POST /oauth2/token | token_manager.py, broker_kiwoom_client.py | 토큰 발급 |
| 주문 매수 | POST /api/dostk/ordr (kt10000) | broker_kiwoom_client.py | 매수 |
| 주문 매도 | POST /api/dostk/ordr (kt10001) | broker_kiwoom_client.py | 매도 |
| 잔고 조회 | GET /api/dostk/acnt | broker_kiwoom_client.py | 잔고조회 |
| 차트 | /api/dostk/chart | broker_kiwoom_client.py, kiwoom_chart_collector.py, tick_data_collector.py | 차트 데이터 |
| 기타 | /api/dostk/mrkcond, theme, sect, etf, elw, condition-search, program-trades, strength 등 | broker_kiwoom_client.py, theme_detail_collector.py, condition_search_collector.py, program_trades_collector.py, trade_strength_collector.py | 시장/테마/조건검색 등 |

## 4. 기타 문서

| # | 파일명 | 내용 |
|---|--------|------|
| 1 | README.md | docs/api 폴더 설명 (kis-autotrade-v4/docs/api/README.md) |
| 2 | kisapi/README.md | KIS API 엑셀 복사·관리 방법 |

## 5. KIS vs 키움 API 비교 요약

| 항목 | KIS (한국투자증권) | 키움증권 |
|------|-------------------|---------|
| 토큰 발급 URL | POST /oauth2/tokenP | POST /oauth2/token |
| 모의 API 도메인 | openapivts.koreainvestment.com | mockapi.kiwoom.com |
| 실전 API 도메인 | openapi.koreainvestment.com | (KIWOOM_IS_PRODUCTION) |
| 인증 파라미터 | appkey + appsecret | appkey + secretkey |
| 토큰 유효기간 | 24시간 | 24시간 |
| RPS 제한 | 초당 20건 | 전체 5건, 계좌당 1.67건 |
| 주문 엔드포인트 | /uapi/domestic-stock/v1/trading/order-cash | /api/dostk/ordr |
| 잔고 엔드포인트 | /uapi/domestic-stock/v1/trading/inquire-balance | /api/dostk/acnt |
| 앱키 저장 | .env (KIS_APP_KEY) + DB (kis_configs) | DB (accounts.enc_app_key, Fernet 암호화) |
| Redis 토큰 키 | token:kis:{config_id} | token:kiwoom:kiwoom:{account_id} |

## 6. 문서 갱신 이력
| 날짜 | 내용 |
|------|------|
| 2026-02-23 | 최초 카탈로그 작성 (CUR-API-DOCS-CATALOG-001) |
