# PAPER-TRADE-FINAL-TEST 최종 검증 보고서

**작업 ID:** PAPER-TRADE-FINAL-TEST  
**일시:** 2026-02-23 15:35 KST (장마감 후, CEO 승인 완료)  
**서버:** root@211.188.51.113  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  
**우선순위:** P0 (모의매매 1회 사이클 최종 검증)

---

## 1. 재시작 결과

| 항목 | 결과 |
|------|------|
| kis-v41-api 재시작 | **OK** (15:37:08 KST) |
| health check | **OK** `{"status":"ok","database":"connected","redis":"connected"}` |
| kis-v41-monitor / kis-v41-scheduler | 재시작 없음 (지시서 준수) |

---

## 2. 잔고 연동 (Phase C)

- **진단 스크립트:** `CONFIG_ID=1 python scripts/diagnose_balance_config3.py`
- **계좌:** config_id=1, account_masked: 5016***, product: 01
- **예수금(d2_deposit):** 466,347,229원
- **보유 종목:** 7종목 (진단 출력 5종목: 대한제당, 한화투자증권, 삼영, 삼성전자, 한온시스템 등)
- **판정:** 잔고 연동 **정상** (진단 스크립트 기준)

---

## 3. 매매 사이클 결과 (Phase D)

- **API 호출:** `POST /api/v4/trading/desk3/cycle?dry_run=false` → **HTTP 200**
- **시그널:** 5건 BUY (지누스 013890, 아가방컴퍼니 013990, 화승인더 006060, 비비안 002070, 경인전자 009140)
- **주문 전송:** PRE_ORDER_CHECK에서 전원 **매수 거부** → 실제 주문 0건
- **체결:** 0건
- **포지션 INSERT:** 0건 (매수 미실행으로 해당 없음)

### 3.1 PRE_ORDER_CHECK 로그 (usable 값)

- 모든 시그널에 대해 **가용=0** 기록.
- 예: `[PRE_ORDER_CHECK] 매수 거부: 013890 필요=9677960, 가용=0, 사유=잔액 부족 (필요: 9677960, 사용가능: 0)`
- **판정:** PRE_ORDER_CHECK **usable = 0** 지속 → **목표 미달**

### 3.2 기타 로그

- **KIS 잔고 조회:** inquire-balance CANO=50160697(모의) **200 OK** 다수
- **토큰:** 구간 중 403 "접근토큰 발급 잠시 후 다시 시도하세요(1분당 1회)" 발생 후, 이후 토큰 재발급 200 OK
- **order-cash:** 200 OK 2건 (EXIT-DISPATCHER 쪽 매도 등 다른 경로로 추정)
- **insert_position / position created:** 로그 없음
- **에러:** 토큰 재시도 초과 2회, split_transfer_engine 토큰 실패 1회 (위 403 이슈와 동일)

---

## 4. DB 결과 (Phase E)

| 항목 | 값 |
|------|-----|
| strategy_cards | **65** (사전 65, 변동 없음) |
| v4_positions OPEN | **5** (ID 49, 51, 53, 55, 61) |
| v4_positions 신규 OPEN | **0건** |
| v4_order_requests (15분 이내) | **0건** |
| v4_order_executions (15분 이내) | **0건** |

- **DB 무결성:** strategy_cards ALTER/DROP/DELETE 없음, v4_positions 직접 수정 없음.

---

## 5. 성공/실패 판정

| 기준 | 결과 |
|------|------|
| PRE_ORDER_CHECK usable > 0 | ❌ usable=0 |
| v4_order_requests 신규 1건 이상 | ❌ 0건 |
| v4_positions 신규 OPEN 1건 이상 | ❌ 0건 |
| openapivts 주문 전송 200 OK (매수) | ❌ 매수 주문 미전송 |
| _insert_position SQL 에러 없음 | ✅ 해당 구간 미진입 |
| strategy_cards 건수 변동 없음 | ✅ 65 유지 |

**매매 사이클 최종 판정:** **실패** (잔액 인식 미반영으로 매수 전원 거부)

---

## 6. 원인 추정

- **usable = min(actual_cash, v41_available)** (AccountSyncManager.pre_order_check)
- **v4_desk_fund:** user_id=1 합계 **380,150,633원** → v41_available ≠ 0
- 따라서 **actual_cash(d2_deposit)** 가 0으로 반환된 것으로 추정.
- 파이프라인/오케스트레이터에서 사용하는 **AccountSyncManager의 config_id** 및 **fetch_account_balance()** 호출 경로·응답 파싱(모의 output2 예수금 0 처리 및 psbl-order fallback 적용 여부) 확인 필요.

---

## 7. CEO 승인 이력

- **kis-v41-api 재시작:** 15:35 KST CEO 승인 완료, 15:37:08 KST 1회 재시작 실행.
- kis-v41-monitor, kis-v41-scheduler 재시작 없음.

---

## 8. 후속 조치 권장

1. **usable=0 지속:** 파이프라인에서 사용하는 AccountSyncManager 인스턴스의 config_id 확인 및, 해당 config로 fetch_account_balance() 호출 시 d2_deposit 파싱·fallback(psbl-order) 동작 검증.
2. **.env / v4_account_config:** 모의계좌(5016***) 일치 여부 재확인.
3. **토큰 403:** 1분당 1회 제한; 장중 동시 토큰 요청 억제 또는 단일 토큰 캐시 사용 검토.
4. **재테스트:** 위 수정 후 API 1회 재시작(CEO 승인 시) → 동일 DESK3 cycle 재실행 후 PRE_ORDER_CHECK usable 및 주문/포지션 재확인.

---

## 9. Phase G — 완료 체크리스트

| 항목 | 결과 |
|------|------|
| kis-v41-api 재시작 | OK |
| health check | OK |
| 잔고 인식 (진단 스크립트) | 예수금 466,347,229원 |
| PRE_ORDER_CHECK usable | 0원 (목표 미달) |
| 시그널 | 5건 |
| 주문 (매수) | 0건 |
| 포지션 신규 | 0건 |
| strategy_cards | 65건 |
| v4_positions OPEN | 5건 |
| 매매 사이클 최종 판정 | **실패** |

**Git 동기화 확인**

- 소스: https://github.com/moongoby/kis-autotrade-v4/tree/phase-2c-command-center
- 보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/PAPER-TRADE-FINAL-TEST-20260223.md
- sync_kis.sh 실행: (발행 후 실행 결과로 기입)
