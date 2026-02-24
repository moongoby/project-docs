# Phase3 Track-A: BrokerGateway + Phase3 스케줄러 + 키움 cron

**작업일시**: 2026-02-25 (화) KST  
**작업자**: Cursor AI  
**브랜치**: phase-3-autonomous  
**승인**: 자체승인 (기존 시스템 0 영향, 신규·선택 수정)

---

## 1. 작업 요약

| 항목 | 내용 |
|------|------|
| A-1 | BrokerGateway 퍼사드 구현 (`backend/app/core/broker_gateway.py`) |
| A-2 | Phase 3 스케줄러 main.py lifespan 등록 (이미 등록됨, 로그 메시지 통일) |
| A-3 | 키움 수집 cron 등록 (`/etc/cron.d/kiwoom_data_collection`) |
| A-4 | 체결강도 증분 수집 모드 (`--incremental` / `--full`) |

---

## 2. A-1 BrokerGateway

### 2.1 신규 파일

- **`backend/app/core/broker_gateway.py`**
  - `BrokerGateway(db_pool)`: account_id → 브로커 클라이언트 반환 퍼사드
  - `get_client(account_id)` → BaseBrokerClient (KIS/KIWOOM)
  - `place_order(account_id, stock_code, side, qty, price, order_type)` — 실계좌 시 WARNING 로그
  - `get_balance(account_id)` → dict
  - `list_accounts(user_id, broker_type, is_mock)` → list[dict] (키 제외)
  - `get_account_info(account_id)` → dict (키 제외)
  - 기존 `BrokerFactory`만 호출, `broker_base`/`broker_factory`/`broker_kis_adapter`/`broker_kiwoom_client` **수정 없음**

### 2.2 보조 수정 (Gateway 동작을 위한 최소 변경)

- **`backend/app/services/data_pipeline/kis_api_client.py`**
  - `get_token_by_config_id(config_id)` 추가
  - `KISAPIClient(user_id, is_production, config_id=None)` — `config_id` 지정 시 해당 config 전용
- **`backend/app/services/trading/kis_order_service.py`**
  - `_get_kis_config_by_id(config_id)` 추가
  - `KISOrderService(..., config_id=None)` 추가
  - `_get_token(..., config_id_override=None)` / `_get_credentials(..., config_id_override=None)` — config_id 우선 사용

### 2.3 검수 결과 (코드 레벨)

| 검수 | 결과 |
|------|------|
| BrokerGateway.get_client(1) | KISBrokerAdapter (KIS 모의) ✅ |
| BrokerGateway.get_client(4) | KiwoomBrokerClient (키움 모의) ✅ |
| BrokerGateway.get_client(5) | KiwoomBrokerClient (키움 실거래) ✅ |
| BrokerGateway.list_accounts() | 7건 반환 ✅ |
| place_order | 구현만 함, 실행 금지 준수 |

---

## 3. A-2 Phase 3 스케줄러

- **상태**: main.py lifespan에 이미 Phase 3 스케줄러 등록됨 (`start_phase3_scheduler()`)
- **변경**: 로그 메시지를 `Phase3DataScheduler started`로 Phase2와 통일
- **검수**: go100.service 재시작 시 로그에서 Phase3DataScheduler 초기화 메시지 확인 가능

---

## 4. A-3 키움 수집 cron

- **설치 경로**: `/etc/cron.d/kiwoom_data_collection`
- **원본**: `docs/cron/kiwoom_data_collection.cron` (설치 방법 주석 포함)
- **내용**:
  - 테마: 평일 17:00 — `scripts/collect_kiwoom_theme.py` → `/var/log/kiwoom_theme.log`
  - 체결강도: 평일 16:40 — `scripts/collect_kiwoom_strength.py --incremental --max-stocks 100` → `/var/log/kiwoom_strength.log`
- **검수**: `cat /etc/cron.d/kiwoom_data_collection`, `chmod 644` 적용됨

---

## 5. A-4 체결강도 증분 수집

- **파일**: `scripts/collect_kiwoom_strength.py`
- **추가**:
  - `get_max_recorded_at_per_stock()` — 종목별 MAX(recorded_at) 조회
  - `--incremental`: DB 최신일 이후만 수집 (기본 동작)
  - `--full`: 60일 전체 수집
- **기본 동작**: 증분 (cron 일상용)
- **검수**: `python scripts/collect_kiwoom_strength.py --incremental --max-stocks 2` 실행 시 증분 모드로 수집·INSERT 확인됨

---

## 6. 기존 시스템 영향도

| 구분 | 내용 |
|------|------|
| 영향 | **없음/최소** — BrokerGateway 신규 추가, Phase3는 기존 등록 유지, cron·스크립트는 추가만 |
| 실계좌 주문 | account_id=5,6 실행 금지 유지 (place_order는 구현만, 테스트 미실행) |
| 키움 모의 | account_id=4 테스트는 자체승인 범위 |

---

## 7. 파일 목록

**신규**

- `backend/app/core/broker_gateway.py`
- `docs/cron/kiwoom_data_collection.cron`
- `report/PHASE3-TRACK-A-BROKER-GATEWAY-20260225.md`

**수정**

- `backend/app/main.py` (Phase3 로그 메시지)
- `backend/app/services/data_pipeline/kis_api_client.py` (config_id 지원)
- `backend/app/services/trading/kis_order_service.py` (config_id 지원)
- `scripts/collect_kiwoom_strength.py` (--incremental/--full)

**시스템**

- `/etc/cron.d/kiwoom_data_collection` (cron 설치)

---

## 8. GitHub / project-docs 동기화

- **kis-autotrade-v4**: 브랜치 `phase-3-autonomous`, 커밋 메시지  
  `feat: Phase3 Track-A — BrokerGateway + Phase3 스케줄러 등록 + 키움 cron`
- **project-docs**: `go100/reports/PHASE3-TRACK-A-BROKER-GATEWAY-20260225.md` 복사 후 커밋

---

*실계좌 주문(account_id=5,6) 실행 금지. go100.service 재시작은 Phase3 등록 검증 시 1회만 수행.*
