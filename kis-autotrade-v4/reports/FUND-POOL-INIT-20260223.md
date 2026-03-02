# FUND-POOL-INIT 작업 보고서

**날짜**: 2026-02-23  
**작업 ID**: FUND-POOL-INIT  
**우선순위**: P0 (장마감 전 매매 사이클 검증)  
**서버**: root@[SERVER-IP]  
**프로젝트**: /root/kis-autotrade-v4  

---

## 1. 목적

- 모의계좌 펀드풀 초기화 (가용잔액 0 → 500만원 기록)
- TRADE-BRIDGE-FIX 반영 후 모의 매매 1회 사이클 실행
- 주문→체결→포지션 생성 흐름 검증

---

## 2. Phase A — 펀드풀 테이블 구조 확인

- **테이블**: `v4_fund_pool_snapshot`
- **컬럼**: `id`, `user_id`(NOT NULL), `total_capital`, `available`, `reserved`, `invested`, `desk1_used`~`desk5_used`, `fund_mode`, `created_at`
- **사전 상태**: 0건
- **코드 참조**: `FundPool.to_snapshot()`, `legacy_adapter`(total_capital 조회), `fund_rebalancer`(INSERT)

---

## 3. Phase B — 펀드풀 초기화 INSERT

**실행 SQL** (INSERT만, 규칙 준수):

```sql
INSERT INTO v4_fund_pool_snapshot
  (user_id, total_capital, available, reserved, invested,
   desk1_used, desk2_used, desk3_used, desk4_used, desk5_used,
   fund_mode, created_at)
VALUES
  (1, 5000000, 5000000, 0, 0,
   0, 0, 0, 0, 0,
   'ROCKET', NOW());
```

**결과**: `INSERT 0 1` 성공

**검증**:

| id | user_id | total_capital | available | reserved | invested | fund_mode | created_at |
|----|---------|---------------|------------|----------|----------|-----------|-------------|
| 1  | 1       | 5,000,000     | 5,000,000  | 0        | 0        | ROCKET    | 2026-02-23 14:50:17+09 |

---

## 4. Phase C — 모의 매매 재테스트

**실행**: DESK3 1사이클 (config_id=3 모의, dry_run=false)

```text
PYTHONPATH=/root/kis-autotrade-v4/backend python -c "
  ... V4PipelineOrchestrator(config_id=3, dry_run=False).run_desk3_cycle()
"
```

**결과 요약**:

| 항목 | 결과 |
|------|------|
| 시그널 | 5건 생성 (CLASS-D picks 기반) |
| 주문 | 0건 (전부 PRE_ORDER_CHECK에서 거부) |
| 포지션 신규 | 0건 |
| PRE_ORDER_CHECK | 필요금액 약 780만~970만원, **가용=0** → 잔액 부족으로 매수 거부 |

**거부 사유**: `AccountSyncManager.pre_order_check()`에서 `usable = min(actual_cash, v41_available)` 사용. 모의계좌 KIS API `d2_deposit`(actual_cash)=0, 해당 user의 `v4_desk_fund` SUM(available_amount) 또는 actual_cash가 0이라 사용가능=0.

**참고**: `v4_fund_pool_snapshot` INSERT는 대시보드/레거시 통계용 total_capital 소스로 사용됨. 매수 직전 잔액 검사는 **KIS 잔고 + v4_desk_fund** 기준이라, 스냅샷만으로는 주문 승인 불가.

---

## 5. DB 무결성

| 항목 | 값 |
|------|-----|
| strategy_cards | 62건 (변경 없음) |
| v4_positions OPEN | 5건 (직접 수정 없음) |
| v4_fund_pool_snapshot | 1건 (INSERT만) |
| v4_order_requests (14:40 이후) | 0건 (주문 미체결로 신규 행 없음) |
| SQL syntax error | 없음 |

---

## 6. 규칙 준수

- kis-v41-api 재시작 없음
- strategy_cards ALTER/DROP/DELETE 없음
- v4_positions 직접 수정 없음
- .env/.bak 커밋 없음
- 모의계좌(config_id=3)만 사용, 실계좌 주문 없음
- v4_fund_pool_snapshot INSERT만 수행

---

## 7. 결론 및 권장

- **펀드풀 초기화**: 500만원 스냅샷 INSERT 완료.
- **매매 사이클**: 시그널·픽 생성까지 정상, 주문은 PRE_ORDER_CHECK(잔액 부족)로 전건 거부.
- **추가 조치 권장**: 모의계좌에서 실제 주문까지 검증하려면 (1) 한투 모의투자 예수금 입금 또는 (2) `pre_order_check`에서 v4_fund_pool_snapshot 최신 available을 보조 소스로 사용하는 정책 검토가 필요함.

---

*작성: Cursor FUND-POOL-INIT 지시서 기준*
