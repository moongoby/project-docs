# NXT 사용자 프로세스 실매매 보고서 — CUR-NXT-USER-PROCESS-LIVE-001

**작업 ID:** CUR-NXT-USER-PROCESS-LIVE-001  
**일시:** 2026-02-24 10:29 ~ 11:06 KST  
**서버:** root@211.188.51.113 (kis-autotrade-v4)  
**브랜치:** phase-2c-command-center  
**매매 방식:** 사용자 프로세스 (V4.1 REST API 엔드포인트 경유)

---

## 1. 요약

- **목표:** 사용자 프로세스(POST /api/v4/orders)를 통해 NXT 1주 매수→매도 실매매 실행 및 체결 증빙 확보
- **결과:** 사용자 API 경유 NXT 매수 요청까지 성공. KIS API 응답 `[EGW02004] 실전투자 TR 이 아닙니다`로 **실제 체결 미발생**. 매도 미진행.
- **검증된 사항:**  
  - POST /api/v4/orders 호출 → v4_order_requests INSERT → KIS credentials 조회 → KIS 주문 API 호출까지 정상 경로 동작  
  - 요청 body에 `exchange: "NXT"` 지원 추가 및 적용 완료  
  - 주문 취소 시 `exchange` 쿼리 파라미터 지원 추가 (DELETE /api/v4/orders/{id}?exchange=NXT)

---

## 2. API 엔드포인트

| Method | URL | 비고 |
|--------|-----|------|
| POST | `/api/v4/orders` | 주문 생성. Body: ticker, side, order_type, quantity, price(지정가 시), exchange(기본 KRX, NXT/SOR 지원) |
| DELETE | `/api/v4/orders/{order_id}?exchange=KRX` | 주문 취소. exchange 쿼리 파라미터 (NXT 주문 취소 시 exchange=NXT) |
| GET | `/api/v4/orders/pending` | 미체결 목록 |
| GET | `/api/v4/orders/{order_id}` | 주문 상태 조회 |

- **인증:** `Authorization: Bearer <JWT>`, `X-Internal-API-Key: <INTERNAL_API_KEY>` (v4 경로 필수)
- **JWT:** users 테이블 user_id (sub 클레임). config_id=4 계좌는 user_id=27에 연결됨.

---

## 3. 수행 내역

### 3.1 STEP 0 — 사전 확인

- **KST:** 2026-02-24 10:34 (화요일, 정규장 09:00~15:30)
- **서비스:** kis-v41-api, kis-v41-monitor, kis-v41-scheduler, kis-v41-position-monitor 모두 active. `/health` OK.
- **DB 스냅샷 (사전):**  
  - strategy_cards: 60  
  - v4_positions OPEN: 11  
  - 오늘 order_requests: 0  
  - 오늘 v4_trades: 0  
- **DB 백업:** `/tmp/backup_NXT_USER_PROCESS_20260224_103442.dump` 생성 완료
- **엔드포인트 확인:** POST/DELETE/GET /api/v4/orders (routers/v4_orders.py). Body 스키마에 `exchange` 추가하여 NXT 지원.

### 3.2 STEP 1–2 — .env 백업, 실계좌 전환, API 재시작

- `.env.bak.pre-nxt-user-202602241038` 백업 완료
- `KIS_ACCOUNT_MODE=real` 전환
- kis-v41-api 1회 재시작. health OK. (재시작 1/2)

### 3.3 STEP 3–4 — 토큰·잔고·현재가

- **JWT:** user_id=27용 `create_access_token`(core.auth)으로 발급. API 호출 시 사용.
- **잔고 조회:** KISOrderService.get_balance(user_id=27) 실행 시 서비스 내부 `pchs_avg_pric` int 변환 오류 발생 (별도 이슈).
- **NXT 현재가:** 절차서의 `KISMarketService`(market_div J/NX) 경로 미존재. 시세는 기존 market API 또는 지정가 4000원으로 가정하고 주문 요청.

### 3.4 STEP 5 — 사용자 프로세스 NXT 매수 (1주)

- **요청:**  
  - POST /api/v4/orders  
  - Body: ticker=056190, side=BUY, order_type=LIMIT, quantity=1, price=4000, exchange=NXT  
  - Header: Bearer (user_id=27), X-Internal-API-Key  
- **1차:** `No active KIS config for user_id=27` → kis_config 조회 실패.  
- **대응:** KISOrderService._get_token 내 `_get_kis_config(user_id, prefer_production)` 실패 시 `_get_kis_config(user_id, None)` fallback 추가 후 API 2회차 재시작 (재시작 2/2 소진).
- **2차 이후:** v4_order_requests INSERT 성공 후 KIS API 호출까지 진행.  
  - **KIS 응답:** `[EGW02004] 실전투자 TR 이 아닙니다.`  
  - **의미:** 실전 투자용 TR이 아니라는 브로커 측 제한. 체결 없음.
- **v4_order_requests:** 당일 3건 (id 72, 73, 74) — 모두 ticker=056190, side=BUY, status=FAILED.

### 3.5 STEP 6 — 매도

- 매수 체결이 없었으므로 매도 미진행.

### 3.6 STEP 7–8 — .env 복원, DB 정합성

- `.env`를 백업본으로 복원 후 `KIS_ACCOUNT_MODE=virtual`로 설정.
- API 재시작 한도(2회) 소진으로 재시작 없음. 서비스는 모두 active 유지.
- **DB 정합성 (사후):**  
  - strategy_cards: 60 (사전과 동일)  
  - v4_positions OPEN: 11 (사전과 동일)  
  - 오늘 order_requests: 3 (테스트 요청 3건)  
  - 오늘 v4_trades: 0  
  - v4_order_requests 최근: id 72,73,74 — 056190 BUY, 모두 FAILED.

---

## 4. 코드 변경 요약

- **backend/app/schemas/order.py**  
  - `OrderCreateRequest`에 `exchange: str = "KRX"` (pattern: KRX|NXT|SOR) 추가.
- **backend/app/services/trading/kis_order_service.py**  
  - `OrderRequest`에 `exchange: str = "KRX"` 추가.  
  - `KisOrderService.create_order`에서 `place_buy_order`/`place_sell_order`에 `exchange` 전달.  
  - `cancel_order`에 `exchange` 인자 추가, KIS `cancel_order`에 전달.  
  - `_get_token`: `_get_kis_config(user_id, prefer)` 실패 시 `_get_kis_config(user_id, None)` fallback 추가.
- **backend/app/routers/v4_orders.py**  
  - `create_order`: body.exchange → OrderRequest.exchange.  
  - `cancel_order`: 쿼리 파라미터 `exchange` (기본 KRX) 추가.

---

## 5. 체결 증빙·P&L

- **매수/매도 체결:** 없음 (KIS EGW02004 오류).  
- **주문번호·체결가·수수료·세금·realized P&L:** 해당 없음.

---

## 6. 참고 사항

- **v4_orders 테이블:** 본 프로젝트 DB에는 없음. 체결 이력은 v4_order_requests, v4_trades 등으로 관리.
- **config_id=4:** kis_configs.id=4, user_id=27, is_production=true. 실전 계좌이나 KIS 측에서 해당 계정/앱에 대해 실전 TR 허용이 안 된 상태로 판단됨.
- **다음 실매매 시:** KIS 실전투자 TR 신청·승인 상태 확인 후 동일 API로 재시도 권장.

---

**보고서 작성일:** 2026-02-24  
**작성:** CUR-NXT-USER-PROCESS-LIVE-001 절차에 따른 실행 결과
