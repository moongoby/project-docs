# PAPER-TRADE-SETUP 보고서

**작성일**: 2026-02-23  
**서버**: root@211.188.51.113  
**프로젝트**: /root/kis-autotrade-v4  
**브랜치**: phase-2c-command-center  
**우선순위**: P0 (장중 — 15:30 장마감 전 테스트 목표)

---

## 1. 모의계좌 현황

### 1.1 환경변수 확인 (키만, 값 마스킹)

| 구분 | 환경변수 키 |
|------|-------------|
| 모의/API | KIS_BASE_URL, KIS_VIRTUAL_* (인증·계좌 관련 4종), KIS_ACCOUNT_MODE, MOCK_CONFIG_ID, KIS_MOCK_RATE_LIMIT |

- **KIS_ACCOUNT_MODE**: virtual 쪽으로 설정됨 (값 마스킹).
- **KIS_BASE_URL**: 모의투자 도메인 사용 중 (`openapivts`).

### 1.2 계좌 가용 현황 (마스킹)

| 구분 | Acnt 앞3자리 | Key 존재 | Secret 존재 | API 도메인 | 상태 |
|------|--------------|----------|--------------|------------|------|
| 실전 | (미등록) | Y | Y | openapi | 비활성 — v4_account_config에 real 행 없음, 실전 번호 미설정 |
| 모의1 | 501*** | Y | Y | openapivts | 활성 — v4_account_config 1건, is_active=true |

- **현재 API 도메인**: 모의 (`openapivts`).
- **실전 계좌**: .env에 REAL용 키는 있으나 실전 번호는 미설정이며 DB v4_account_config에는 real 행이 없음. 따라서 **실전 주문 불가·미사용** 상태.

---

## 2. 설정 방법 요약

### 2.1 모의/실전 분기

- **config.py**: `kis_is_virtual: bool = True` (기본 모의).
- **account_mode.py**: `kis_configs`의 `is_production` 또는 config_id(3=모의, 4=실)로 모의/실 구분. `BASE_URL_VIRTUAL` / `BASE_URL_REAL`, tr_id 접두사 VTTC/TTTC 전환.
- **v4_admin.py**: `POST /switch-account-mode`로 `v4_account_config`의 `is_active` 전환. `account_type`: `virtual` | `real`. **실전 사용 시** `v4_account_config`에 `account_type='real'` 행 등록 필요.

### 2.2 현재 시스템 설정

- **실계좌/모의계좌 구분**: `.env`의 `KIS_ACCOUNT_MODE` 및 `KIS_BASE_URL`, DB `v4_account_config.is_active`로 결정.
- **모의로 전환**: 이미 모의 사용 중. 실전에서 모의로 돌리려면 `POST /switch-account-mode`에 `{"account_type": "virtual"}` 호출 (관리자 인증 필요). `.env`의 `KIS_BASE_URL`을 `openapivts`로 맞추는 것도 필요.

---

## 3. 분봉 수집 현황

| trade_date | 건수 |
|------------|------|
| 2026-02-20 | 36,894 |
| 2026-02-21 | (미조회 — 쿼리 범위 02-20~) |
| 2026-02-22 | (미조회) |
| 2026-02-23 | **0** (당일 데이터 없음) |

- **당일(02-23) 분봉**: **없음**. `v4_ohlcv_minute`에 `trade_date = '2026-02-23'` 0건.
- CONTEXT 기준 kis-v41-minute-collector 월요일 장전 inactive → 당일 수집 여부는 서비스 가동 및 수집 로그 확인 필요.

---

## 4. DESK별 자금 배분 방안

### 4.1 코드 위치

- **Fund Commander**: `backend/app/services/brain/fund_commander.py`  
  - `get_effective_allocation(regime, total_capital)`로 비율 산출, `base_amount = total_capital * allocation[desk_id] / 100`.
- **자금 풀**: `backend/app/services/execution/fund_pool.py`  
  - `FundPool.initialize(user_id, total_capital, initial_capital, regime)`  
  - `_calculate_desk_limits_static(total_capital, fund_mode, regime)` → 레짐·자금규모에 따른 DESK별 한도.
- **레짐/규모**: `backend/app/core/desk_config.py`  
  - `get_effective_allocation(regime, total_capital)`  
  - `ROCKET_MODE_THRESHOLD = 1_000_000`: 총자금 ≤100만 시 DESK4·5 배분 0, DESK2·3으로 재분배.

### 4.2 DESK별 100만원 × 5 = 500만원 테스트

- **총 500만원**으로 테스트하려면: `total_capital = 5_000_000` (또는 `initial_capital` 500만)으로 FundPool/스냅샷이 초기화되도록 하면 됨.
- 실제 값은 **v4_fund_pool_snapshot**의 `total_capital` 및 파이프라인/팩토리에서의 초기화 지점에서 설정됨 (`legacy_adapter`: `v4_fund_pool_snapshot.total_capital` 또는 기본 10_000_000).
- “DESK별 100만원”을 **고정 100만원**으로 쓰려면: 현재 구조는 비율 배분이므로, 총자금 500만원이면 레짐에 따라 DESK당 금액이 비율로 나뉨. DESK당 정확히 100만원 고정은 설정/코드 확장 필요 (예: desk별 cap override).

---

## 5. 모의계좌 잔고 확인 API

- **코드만 확인**: KIS 모의투자 잔고/계좌조회 API는 `kis_api_registry.py` 및 주문/계좌 관련 서비스에서 tr_id·도메인 분기 지원. 실제 잔고 API 호출은 **CEO 승인 후** 진행할 것.

---

## 6. CEO 결정 필요 사항

1. **당일(02-23) 분봉 없음**: minute-collector 가동 및 당일 수집 실행 여부 확인 후, 필요 시 수집 재개.
2. **실전 계좌 미등록**: 모의만 사용 중이면 유지. 실전 전환 시 v4_account_config에 real 행 추가 및 실전 계좌 번호 설정 필요.
3. **DESK별 100만원 고정**: 현재는 총자금 기준 비율 배분. DESK당 정확히 100만원 고정이 필요하면 자금 배분 로직(설정/DB) 확장 검토.
4. **모의 1회 매매 사이클 검증**: 장마감 전 실행 시, 모의 계좌·동일 도메인(openapivts)으로만 주문되도록 확인된 상태. 실제 주문 실행은 CEO 승인 후 진행.

---

## 7. DB 무결성

| 항목 | 기준 | 확인값 |
|------|------|--------|
| strategy_cards | 62건 | 62 |
| v4_positions OPEN | 5건 | 5 |

- strategy_cards ALTER/DROP/DELETE 금지, v4_positions 직접 수정 금지 준수.

---

## 8. 참고

- **절대 규칙 준수**: kis-v41-api/monitor/scheduler 재시작 금지, .env/.bak 커밋 금지, 실계좌 주문 금지(모의만 사용).
- **보고서 동기화**: `bash /root/project-docs/scripts/publish_report.sh PAPER-TRADE-SETUP`, `bash /root/project-docs/scripts/sync_kis.sh`.
