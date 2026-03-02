# CUR-GO100-BROKER-GATEWAY-001 작업 보고서

**작성일**: 2026-02-25 (KST)  
**작업 ID**: CUR-GO100-BROKER-GATEWAY-001  
**우선순위**: P0  
**브랜치**: feat/CUR-GO100-BROKER-GATEWAY-001 → phase-2c-command-center  
**서버**: root@[SERVER-IP]  

---

## 1. 작업 요약

- **BrokerGateway**: account_id 기준 브로커(KIS/KIWOOM) 클라이언트 퍼사드 정비 및 `place_order(account_id, order_params: dict)` API 추가.
- **Phase 3 스케줄러**: 16:25 KST 체결강도 증분 수집(`collect_kiwoom_strength.py --incremental`) 작업 등록.
- **키움 cron**: `/etc/cron.d/kiwoom_data_collection` 신규 등록(테마 17:00, 체결강도 16:40, 프로그램매매 16:30).
- **collect_kiwoom_strength.py**: 작업 헤더 및 `--incremental` 옵션 명시 보강.
- **kis-v41-*** 서비스 재시작 없음. DB 스키마/프론트엔드 변경 없음.

---

## 2. 변경 파일 목록

| 구분 | 경로 | 내용 |
|------|------|------|
| 수정 | `backend/app/core/broker_gateway.py` | CUR-GO100-BROKER-GATEWAY-001 헤더, `place_order(account_id, order_params)` 및 `_place_order_impl` 정리 |
| 수정 | `backend/app/services/phase3_data_scheduler.py` | 16:25 체결강도 증분 수집 추가, `_run_kiwoom_strength_incremental()` |
| 수정 | `backend/app/services/data/program_trades_collector.py` | `if __name__ == "__main__"` 진입점 추가(cron `-m` 실행용) |
| 수정 | `scripts/collect_kiwoom_strength.py` | CUR-GO100-BROKER-GATEWAY-001 헤더 및 `--incremental` 설명 보강 |
| 신규 | `/etc/cron.d/kiwoom_data_collection` | 키움 데이터 수집 cron (시스템 파일, 리포 미포함) |

---

## 3. BrokerGateway 클래스 설명

- **위치**: `backend/app/core/broker_gateway.py`
- **역할**: `accounts` 테이블의 `account_id` → `broker_type`(KIS/KIWOOM) 매핑 후, 기존 `BrokerFactory`로 클라이언트 생성·캐시(`dict[int, BaseBrokerClient]`, TTL 없음).
- **주요 메서드**:
  - `get_client(account_id)` → `BaseBrokerClient` (캐시 또는 신규 생성)
  - `place_order(account_id, order_params: dict)` → `dict` (success, order_no, message, raw_response)
  - `get_balance(account_id)` → 잔고 dict
  - `list_accounts(user_id=None)` → 활성 계좌 목록(민감정보 제외)
  - `get_account_info(account_id)` → 단건 계좌 정보(민감정보 제외)
- **주의**: `broker_factory.py`, `kiwoom_broker_client.py`, KIS 어댑터는 수정하지 않음(Additive-Only).

---

## 4. Cron 등록 내용

**파일**: `/etc/cron.d/kiwoom_data_collection`

| 스케줄 | 설명 | 명령 |
|--------|------|------|
| 0 17 * * 1-5 | 테마 데이터 | `scripts/collect_kiwoom_theme.py` |
| 40 16 * * 1-5 | 체결강도 증분 | `scripts/collect_kiwoom_strength.py --incremental` |
| 30 16 * * 1-5 | 프로그램매매 | `python -m backend.app.services.data.program_trades_collector` |

- `PYTHONPATH=/root/kis-autotrade-v4`, `.venv/bin/python` 사용.
- 로그: `/var/log/kiwoom_theme.log`, `kiwoom_strength.log`, `kiwoom_program.log`.

---

## 5. accounts 테이블 현황 (7계좌)

| account_id | user_id | broker_type | account_number | is_mock | is_active |
|------------|---------|-------------|----------------|---------|-----------|
| 1 | 1 | KIS | 50160711 | t | t |
| 2 | 2 | KIS | 50160697 | t | t |
| 3 | 2 | KIS | 50000000-02 | t | t |
| 4 | 3 | KIWOOM | 81201280 | t | t |
| 5 | 3 | KIWOOM | 52568156 | f | t |
| 6 | 3 | KIWOOM | 63109343 | f | t |
| 7 | 3 | KIS | 74032243 | f | t |

- account_id 4: 키움 모의, 5·6: 키움 실계좌, 1·2·3: KIS, 7: KIS 실계좌.

---

## 6. 검증 결과

- **BrokerGateway import**: `python -c "from backend.app.core.broker_gateway import BrokerGateway"` → OK.
- **cron 파일**: `/etc/cron.d/kiwoom_data_collection` 내용·문법 확인 완료.
- **go100 서비스**: `systemctl restart go100` 후 `status` active, `curl localhost:8002/health` → status ok, database/redis connected.
- **kis-v41-***: 재시작 없음.

---

## 7. 영향 범위

- **영향**: GO100/자동매매에서 account_id 기준 브로커 호출 시 BrokerGateway 사용 가능. Phase3 스케줄러·키움 cron으로 장마감 후 데이터 수집 자동화.
- **미변경**: DB 스키마, 프론트엔드, auto_trade_engine.py, kis-v41-* 서비스.
