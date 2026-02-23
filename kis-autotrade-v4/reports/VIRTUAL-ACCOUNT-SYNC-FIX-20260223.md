# VIRTUAL-ACCOUNT-SYNC-FIX 보고서 (2026-02-23)

**작업 ID:** VIRTUAL-ACCOUNT-SYNC-FIX  
**우선순위:** P0 (장마감 전 잔고 연동 검증)  
**서버:** root@211.188.51.113  
**브랜치:** phase-2c-command-center  

---

## 1. 요약

- **원인:** (1) `.env` 및 `v4_account_config` 계좌 식별값이 앱 모의계좌(5016***-01)와 불일치(5012***). (2) `pre_order_check`가 **config_id=3만** 대상으로 동작해, 앱 기준 계좌 **config_id=1(5016***)** 에서는 잔고 사전확인이 수행되지 않음.
- **조치:** (1) `.env` 모의계좌 env 변수 → 5016***로 수정(백업 후). (2) `v4_account_config` id=1 계좌 필드 → 5016***로 UPDATE. (3) `pre_order_check`를 **모든 모의계좌(virtual)** 에 대해 수행하도록 변경(config_id=1,3,5 공통).
- **kis-v41-api 재시작:** 미실행(규칙 준수). 코드·DB·env 반영 후 **재시작 시** PRE_ORDER_CHECK 및 매매 사이클 재검증 권장.

---

## 2. Phase A — 계좌 식별값 불일치 진단

| 항목 | 결과 (마스킹) |
|------|----------------|
| .env 모의계좌 (AS-IS) | env 모의계좌 변수=5012*** |
| .env 모의계좌 (TO-BE) | 5016*** 반영 완료 |
| v4_account_config id=1 (AS-IS) | account_no 5012*** |
| v4_account_config id=1 (TO-BE) | 5016*** 반영 완료 |
| kis_configs (is_production=false) | id=1,3,5 → 5016***-01 |

- **AccountSyncManager** 잔고조회: `kis_configs`의 계좌·상품코드 필드 사용, `inquire-balance` (VTTC8434R 모의) 호출. `d2_deposit` 및 output2 fallback·psbl-order fallback 로직 확인.

---

## 3. Phase B — KIS 모의 API 토큰·잔고 직접 조회

| 구분 | 결과 |
|------|------|
| .env 기준 토큰 발급 | 403 (유효하지 않은 AppKey — .env 앱키는 별도 용도/만료 추정) |
| **kis_configs config_id=1** (앱 기준 50160697) | 토큰 성공, 예수금 **466,347,229원**, 보유 **7종목** (앱과 일치) |
| kis_configs config_id=3 | 토큰 성공, 예수금 500,035,866원, 보유 3종목 |

- 진단 스크립트: `scripts/diagnose_balance_config3.py` (DB 복호화 경로 사용, 시크릿 마스킹).

---

## 4. 불일치 원인 및 수정 내역

| 원인 | 조치 |
|------|------|
| .env 계좌 식별값 불일치 | `.env.bak.20260223_152012` 백업 후 5016*** 반영 (커밋 없음) |
| v4_account_config id=1 불일치 | account_no 5012*** → 5016*** UPDATE |
| pre_order_check가 config_id=3만 대상 | `v4_trade_bridge.py`: `if config_id == 3` → `if virtual` 로 변경하여 모의계좌(1,3,5) 공통 적용 |

**AS-IS (v4_trade_bridge.py):**
```python
# 계좌잔고 사전 확인 — config_id=3(모의)만 (A2)
if config_id == 3:
    ...
    sync_manager = AccountSyncManager(config_id, conn)
    check_result = await sync_manager.pre_order_check(...)
```

**TO-BE:**
```python
# 계좌잔고 사전 확인 — 모의계좌(config_id=1,3,5) 공통 (VIRTUAL-ACCOUNT-SYNC-FIX)
if virtual:
    ...
    sync_manager = AccountSyncManager(config_id, conn)
    check_result = await sync_manager.pre_order_check(...)
```

---

## 5. 재테스트 (Phase D)

- **kis-v41-api 재시작:** 미실행(절대 규칙).
- **재시작 후 권장 검증:**
  1. 잔고 조회: `python scripts/diagnose_balance_config3.py` (CONFIG_ID=1) → 예수금 466,347,229원, 7종목 확인.
  2. DESK3 매매 사이클: `curl -X POST http://localhost:8003/api/v4/trading/desk3/cycle?dry_run=false` (내부 API 키).
  3. 로그: `journalctl -u kis-v41-api --since "3 min ago" --no-pager | grep -iE "PRE_ORDER|usable|balance" | tail -10`
  4. 포지션: `SELECT id, stock_code, desk_id, status FROM v4_positions ORDER BY id DESC LIMIT 10;`

---

## 6. DB 무결성

| 항목 | 값 |
|------|-----|
| strategy_cards | 64건 |
| v4_positions OPEN | 5건 |
| strategy_cards ALTER/DROP/DELETE | 미실행 |
| v4_positions 직접 수정 | 미실행 |

---

## 7. 시크릿·보안

- 보고서 내 계좌 식별값: 앞 4자리+*** (5016*** 등) 마스킹.
- .env / 앱키·시크릿·토큰 전체 미기재.
- .env 변경분 커밋 금지 유지.

---

## 8. 참고

- **수정 파일:** `backend/app/services/trading/v4_trade_bridge.py`, `.env`, DB `v4_account_config` 1행.
- **진단 스크립트:** `scripts/diagnose_balance_config3.py` (CONFIG_ID 변경하여 1/3/5 각각 잔고 확인 가능).
