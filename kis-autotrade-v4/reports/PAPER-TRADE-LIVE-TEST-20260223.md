# PAPER-TRADE-LIVE-TEST 보고서 (2026-02-23)

**작업 ID:** PAPER-TRADE-LIVE-TEST  
**실행 일시:** 2026-02-23 14:17 KST (장중)  
**서버:** root@211.188.51.113  
**브랜치:** phase-2c-command-center  
**목적:** 모의계좌(openapivts, 501***) 실매매 1회 사이클 검증

---

## 1. 사전 점검 결과 (Phase A)

| 항목 | 결과 | 비고 |
|------|------|------|
| **시스템 모드** | virtual, is_active=true | `v4_account_config`: id=1, account_type=virtual |
| **API 헬스** | ok | status=ok, database=connected, redis=connected (GET /health) |
| **서비스 상태** | active × 3 | kis-v41-api, kis-v41-monitor, kis-v41-scheduler |
| **모의계좌 잔고 조회** | 실패 | Fernet 초기화 실패(ENCRYPTION_KEY 등 미설정). CLI에서 실행 시 환경 차이. API 서비스는 정상 동작 중 |
| **strategy_cards** | 62건 | 무결성 유지 |
| **v4_positions OPEN** | 5건 | 기존 포지션 유지 (id 49, 51, 53, 55, 61 등) |

---

## 2. 매매 사이클 실행 (Phase B)

- **실행 방법:** API 호출  
  `POST /api/v4/trading/desk3/cycle?dry_run=false`  
  (X-Internal-API-Key 사용, 모의 전용)
- **선택 이유:** DESK3 수익률 +32.23%로 안정적, 지시서 방법 3(DESK3 우선) 준수
- **실행 결과 (HTTP 200):**
  - **picks:** 5건 (지누스 013890, 아가방컴퍼니 013990, 화승인더 006060, 비비안 002070, 경인전자 009140)
  - **signals:** BUY 5건 (동일 종목, desk3_class_d, confidence 0.36~0.62)
  - **orders (API 응답):** [] (빈 배열 — 응답 구조상 주문 목록 미반영)

---

## 3. 주문/체결/포지션 확인 (Phase C)

### 3.1 로그 분석 (journalctl)

- **모의 도메인 확인:**  
  `POST https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash` → **HTTP/1.1 200 OK** (여러 건)
- **에러:**  
  `process_signal BUY error: syntax error at or near ")"`  
  발생 위치: `v4_trade_bridge.py` → `_insert_position()`  
  `LINE 2: ...e, split_phase, remaining_qty, original_desk_id, signal_id))`

### 3.2 DB 조회

| 테이블 | 조건 | 결과 |
|--------|------|------|
| v4_order_requests | created_at >= 2026-02-23 13:00 | 0 rows |
| v4_order_executions | created_at >= 2026-02-23 13:00 | 0 rows |
| v4_positions | 최근 10건 | OPEN 5건 유지 (변동 없음) |

---

## 4. 실패 원인 분석 (Phase D)

- **요약:** KIS 모의 API에는 주문이 성공적으로 전송되었으나, **포지션 INSERT 단계에서 SQL 구문 오류**로 실패하여 주문 후처리(포지션/체결 기록)가 중단됨.
- **원인:**  
  `backend/app/services/trading/v4_trade_bridge.py` 의 `_insert_position()`  
  - `vals` 초기값이 이미 `(... %s)` 형태로 **닫는 괄호를 포함**  
  - `buy_phase`가 None인 분기에서 `vals += ")"` 를 추가하여 **VALUES 절에 괄호 중복**  
  - 생성된 SQL: `VALUES (... ) )` → PostgreSQL `syntax error at or near ")"`
- **영향:**  
  - 주문은 openapivts로 전송·200 OK 수신  
  - 포지션 INSERT 실패 → 트랜잭션/후속 로직 중단 → v4_order_requests / v4_order_executions 미기록, 포지션 미증가

---

## 5. 시그널·주문 요약

| 구분 | 건수 | 상세 |
|------|------|------|
| 시그널 발생 | 5건 | DESK3, 종목: 013890, 013990, 006060, 002070, 009140 |
| 주문 전송 (모의) | 다수 | openapivts 도메인, HTTP 200 (로그 기준) |
| 체결 (DB 기록) | 0건 | 위 SQL 오류로 후처리 미완료 |
| 포지션 신규 | 0건 | INSERT 실패로 변동 없음 |
| 에러 | 있음 | v4_trade_bridge._insert_position SQL syntax error (괄호 중복) |

---

## 6. DB 무결성

- **strategy_cards:** 62건 (변동 없음)  
- **v4_positions OPEN:** 5건 (변동 없음)  
- **기타:** ALTER/DROP/DELETE 없음, v4_positions 직접 수정 없음

---

## 7. 결론 및 권장사항

- **모의 도메인:** openapivts 사용 및 주문 전송 성공 확인됨.  
- **매매 사이클:** 주문 전송까지는 성공, **포지션 INSERT SQL 버그**로 1회 사이클은 “실패”로 정리.  
- **권장:** `v4_trade_bridge._insert_position()` 의 `vals` 괄호 로직 수정 후 재테스트 (코드 수정 시 CEO/지시서 승인 후 진행).

---

*보고서 작성: 2026-02-23. 시크릿 값 미포함.*
