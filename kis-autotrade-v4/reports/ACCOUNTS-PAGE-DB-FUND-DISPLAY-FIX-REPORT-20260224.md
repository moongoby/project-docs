# 계좌관리 DB/정보 미표시 조치 보고서 (2026-02-24)

## 현상

- **URL**: https://go100.newtalk.kr/accounts (계좌 관리)
- **증상**: 총 자산·총 현금·총 잔고·현금·주식평가 등이 "—", "₩0"으로만 표시되고, 실제 DB/증권사 잔고가 반영되지 않는 것처럼 보임.

## 원인

1. **계좌 목록 API가 잔고 필드를 내려주지 않음**  
   `GET /api/v1/accounts`는 `AccountResponse`만 반환하고,  
   `total_fund`, `available_fund`, `stock_value` 등 **펀드/잔고 필드는 포함하지 않았음**.

2. **프론트는 이미 잔고 필드를 기대**  
   `AccountsSummary`·`AccountCard`는 `total_fund`, `available_fund`, `stock_value`를 사용해  
   총 자산·총 현금·총 잔고·현금·주식평가를 표시하도록 되어 있었으나,  
   백엔드가 해당 필드를 채워 주지 않아 **항상 0/null → "—" 또는 "₩0"**으로만 표시됨.

3. **잔고 저장 위치**  
   `BalanceSyncService`는 KIS 잔고 조회 후 `accounts` 테이블의  
   `total_deposit`(예수금), `total_evaluation`(총평가금액) 컬럼을 갱신하도록 되어 있으나,  
   해당 컬럼이 없을 수 있고, **목록 API에서 이 값을 읽어서 응답에 넣지 않고 있었음**.

---

## 조치 내용

### 1. DB: accounts 잔고 컬럼 보장

- **파일**: `backend/migrations/025_accounts_balance_columns.sql`
- **내용**:  
  - `accounts` 테이블에  
    - `total_deposit` (예수금/현금)  
    - `total_evaluation` (총평가금액)  
    컬럼이 없으면 추가 (기존 DB 호환).
- **적용**: 배포/마이그레이션 시 해당 스크립트 실행 필요.

### 2. 백엔드: 계좌 목록에 잔고·펀드 필드 포함

- **스키마** (`backend/app/schemas/account_schemas.py`)
  - `AccountWithFundResponse`에  
    `stock_value`, `pnl`, `pnl_pct`, `holdings_count`, `strategy_count`, `trades_today` 추가.
  - `AccountListResponse.accounts` 타입을  
    `List[AccountResponse]` → `List[AccountWithFundResponse]`로 변경.

- **계좌 서비스** (`backend/app/services/account_service.py`)
  - `list_accounts`에서:
    - 기존대로 계좌 기본 정보 조회.
    - **추가**:  
      `accounts.total_deposit`, `accounts.total_evaluation` 조회  
      (컬럼 없으면 예외 처리 후 무시, 기존 동작 유지).
    - 계좌별로:
      - `total_fund` = `total_evaluation`
      - `available_fund` = `total_deposit`
      - `stock_value` = `total_evaluation - total_deposit` (0 미만이면 0)
    - 반환 리스트를 `AccountWithFundResponse` 리스트로 구성.

- **라우터** (`backend/app/api/v1/accounts_router.py`)
  - V4 계좌 + 레거시 계좌 병합 시,  
    레거시 항목을 `AccountWithFundResponse`로 변환해  
    응답 모델(`AccountListResponse`)과 타입 일치.

### 3. 동작 요약

| 데이터           | 출처                          | 비고 |
|------------------|-------------------------------|------|
| 총 자산/총 잔고  | `accounts.total_evaluation`   | 잔고 동기화 후 반영 |
| 총 현금/현금     | `accounts.total_deposit`      | 동일 |
| 주식 평가        | `total_evaluation - total_deposit` | 동일 |
| 수익/수익률      | 미구현 (현재 null)            | 추후 확장 가능 |

- `total_deposit`, `total_evaluation` 컬럼이 **아직 없는 DB**에서는  
  잔고 조회 쿼리를 시도했다가 실패하면 무시하고,  
  계좌 목록은 기존처럼 잔고 없이 반환 (총 자산/현금은 계속 "—").
- **마이그레이션 025 적용 + 잔고 동기화**가 이루어지면  
  계좌관리 페이지에 해당 계좌들의 잔고/총평가가 표시됨.

---

## 적용 순서

1. **마이그레이션 실행**  
   `backend/migrations/025_accounts_balance_columns.sql` 실행하여  
   `accounts`에 `total_deposit`, `total_evaluation` 존재하도록 함.

2. **백엔드 배포**  
   위 스키마·서비스·라우터 변경이 포함된 버전 배포.

3. **잔고 동기화**  
   - 계좌관리에서 계좌별 **잔고 동기화** 실행  
     (또는 기존 `BalanceSyncService` 스케줄/수동 실행)  
   - KIS API 잔고 조회 → `accounts.total_deposit`, `total_evaluation` 갱신.

4. **화면 확인**  
   `/accounts` 새로고침 후  
   총 자산·총 현금·총 잔고·현금·주식평가가 동기화된 값으로 표시되는지 확인.

---

## 변경 파일 목록

- `backend/migrations/025_accounts_balance_columns.sql` (신규)
- `backend/app/schemas/account_schemas.py` (AccountWithFundResponse 확장, AccountListResponse 타입 변경)
- `backend/app/services/account_service.py` (list_accounts 잔고 조회·매핑)
- `backend/app/api/v1/accounts_router.py` (레거시 계좌를 AccountWithFundResponse로 병합)

---

## 참고

- **보유종목 수·연결전략 수·거래 건수** 등은  
  현재 목록 API에서 별도 집계하지 않으며,  
  필요 시 추후 쿼리 확장으로 추가 가능.
- 레거시(kis_configs) 계좌는 잔고 컬럼이 없으므로  
  계속 `total_fund`/`available_fund`/`stock_value` 없이 표시됨.
