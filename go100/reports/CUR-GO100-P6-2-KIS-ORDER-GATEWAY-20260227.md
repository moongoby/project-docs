# CUR-GO100-P6-2: KIS API 실주문 게이트웨이 (모의투자 계좌)

**작성일**: 2026-02-27  
**태스크**: P6-2 KIS API 실주문 게이트웨이 — 모의투자 계좌 기반  
**상태**: 완료

---

## 인계 확인

| 항목 | 내용 |
|------|------|
| 직전 완료 | P6-1 리스크 관리 엔진 + Kill Switch |
| 현재 단계 | Phase 6 — 실매매 전 안전장치 |
| CEO 지시 적용 | HANDOVER v9, 보고서 push 필수 |
| strategy_cards | 시드 3건 (35/36/37) |
| open_positions | go100_positions / go100_paper_trades 기준 |

---

## 1. 구현 개요

실매매 직전 단계로 KIS Open API를 통한 주문 게이트웨이를 구현하였다.  
현 단계에서는 **모의투자 계좌만** 사용하며, 실계좌 전환은 CEO 승인 후에만 가능하다.  
모든 매수 주문은 반드시 **risk_engine.check_pre_trade**를 통과해야 한다.

| 기능 | 설명 |
|------|------|
| 토큰 | get_access_token(): Redis go100:kis:token, TTL 23시간 |
| 매수 | execute_buy: 리스크 체크 → KIS order-cash(매수) → go100_live_orders 기록 |
| 매도 | execute_sell: KIS order-cash(매도) → go100_live_orders 기록 |
| 잔고 | get_account_balance: KIS inquire-balance 파싱 |
| 주문상태 | get_order_status: go100_live_orders 조회 |
| Mock | KIS_MOCK=true 시 API 호출 없이 더미 응답 (kis_order_no=MOCK-{timestamp}, FILLED) |

---

## 2. DB 스키마

기존 **go100_live_orders**(마이그레이션 032) 테이블을 사용한다.  
P6-2에서 **side** 컬럼만 추가하여 BUY/SELL 구분.

**마이그레이션 047** (`backend/migrations/047_go100_order_gateway.sql`):

- `ALTER TABLE go100_live_orders ADD COLUMN IF NOT EXISTS side VARCHAR(10);`
- 인덱스: idx_live_orders_user, idx_live_orders_status, idx_live_orders_stock_code

사용 컬럼 매핑:

- ticker → **stock_code**
- kis_order_no → **kis_order_id**
- executed_price / executed_qty / executed_at → **filled_price**, **filled_quantity**, **filled_at**
- error_msg → **error_message**

적용:

```bash
sudo -u postgres psql -d kisautotrade -f backend/migrations/047_go100_order_gateway.sql
```

---

## 3. 서비스 함수 (kis_order_gateway.py)

| 함수 | 설명 |
|------|------|
| **get_access_token()** | .env KIS_APP_KEY/SECRET으로 OAuth tokenP 발급, Redis go100:kis:token 캐싱 (23h). KIS_MOCK=true 시 빈 문자열. |
| **execute_buy(db, user_id, ticker, quantity, price=None, order_type='MARKET')** | 1) check_pre_trade 호출 2) allowed=False → REJECTED INSERT 반환 3) KIS POST order-cash (tr_id VTTC0012U) 4) SUBMITTED/FILLED INSERT. 반환: {status, order_id, kis_order_no, message} |
| **execute_sell(db, user_id, ticker, quantity, price=None, order_type='MARKET')** | KIS POST order-cash 매도 (tr_id VTTC0011U), go100_live_orders INSERT. 반환: {status, order_id, kis_order_no, message} |
| **get_account_balance(db, user_id)** | KIS GET inquire-balance (tr_id VTTC8434R), total_eval, cash, positions 파싱. 반환: {status, data: {total_eval, cash, positions}} |
| **get_order_status(db, user_id, order_id)** | go100_live_orders 조회. 반환: {status, order_id, kis_order_no, order_status, executed_price, executed_qty, executed_at, message} |

**설정 (.env)**  
- KIS_APP_KEY, KIS_APP_SECRET, KIS_ACCOUNT_NO, KIS_ACCOUNT_PROD_CODE(기본 01), KIS_BASE_URL(모의: https://openapivts.koreainvestment.com:29443)  
- KIS_MOCK=true 이면 API 호출 없이 더미 응답 (executed_price는 ohlcv_daily 종가 사용)

**주의사항**  
- 모의 tr_id: 매수 VTTC0012U, 매도 VTTC0011U, 잔고 VTTC8434R. 실계좌 tr_id(TTTC0012U 등)는 코드에 주석으로만 정의.  
- 모든 API 호출 try/except, 에러 시 error_message 기록.  
- 헤더: authorization, appkey, appsecret, Content-Type, tr_id, custtype='P'.

---

## 4. Agent 도구

**agent_tools.py** 에 추가된 도구 3개:

- **execute_buy**: ticker(필수), quantity(필수), price(선택), order_type(선택, 기본 MARKET)
- **execute_sell**: ticker(필수), quantity(필수), price(선택), order_type(선택, 기본 MARKET)
- **get_account_balance**: 파라미터 없음

**tool_executors.py** 에서 execute_buy, execute_sell, get_account_balance 실행 함수 및 TOOL_EXECUTORS 등록.  
user_id는 context에서 전달되며 기본값 2(CEO).

---

## 5. 테스트 결과

**스크립트**: `scripts/go100/test_kis_order_gateway.py`

실행 (프로젝트 루트):

```bash
.venv/bin/python3 scripts/go100/test_kis_order_gateway.py
# 또는 KIS API 키 없을 때
KIS_MOCK=true .venv/bin/python3 scripts/go100/test_kis_order_gateway.py
```

| 단계 | 내용 | 결과 |
|------|------|------|
| 1 | KIS 토큰 발급 (또는 Mock 스킵) | KIS_MOCK=true 시 스킵 |
| 2 | 모의투자 잔고 조회 | status ok, total_eval/cash/positions 반환 |
| 3 | 삼성전자(005930) 1주 시장가 매수 | status FILLED, order_id/kis_order_no 확인 |
| 4 | 주문 상태 조회 | order_status FILLED, executed_price/qty 확인 |
| 5 | 삼성전자 1주 시장가 매도 | status FILLED |
| 6 | 킬스위치 활성화 후 매수 시도 | risk_engine.activate_kill_switch 호출 시 asyncpg `:details::jsonb` 바인딩 오류 (기존 risk_engine 이슈). REJECTED 검증은 수동 또는 risk_engine 수정 후 가능 |
| 7 | 킬스위치 해제 | 정상 |
| 8 | go100_live_orders SELECT | BUY/SELL, kis_order_id, filled_price, filled_quantity 등 확인 |

Mock 모드에서 1~5, 7~8 단계 통과. 킬스위치 연동(6)은 risk_engine의 asyncpg SQL 바인딩 수정 후 재검증 권장.

---

## 6. 파일 목록

| 경로 | 변경 |
|------|------|
| backend/migrations/047_go100_order_gateway.sql | 신규 (side 컬럼 + 인덱스) |
| backend/app/services/go100/kis_order_gateway.py | 신규 |
| backend/app/services/go100/ai/agent_tools.py | execute_buy, execute_sell, get_account_balance 도구 추가 |
| backend/app/services/go100/ai/tool_executors.py | 위 3개 실행 함수 및 TOOL_EXECUTORS 등록 |
| scripts/go100/test_kis_order_gateway.py | 신규 |

---

## 7. 체크리스트

- [x] 코드 레포(kis-autotrade-v4) 반영
- [x] project-docs 보고서 push (본 문서)
- [ ] HANDOVER.md 업데이트 (필요 시)

---

**보고서 끝.**
