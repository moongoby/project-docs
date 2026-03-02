# CUR-GO100-DB-PROBE: DB 실제 상태 조사 보고서

작성일: 2026-02-22  
목표: 실제 DB 접속 정보 확인 + 테이블 구조 확인 + 데이터 현황 파악

---

## 1. DB 접속 정보 확인 (실행 결과)

### (a) 백엔드 .env에서 DB 연결 문자열

**backend/.env**  
- DB 관련 항목 없음 (소셜 로그인 키만 존재)

**루트 .env** (`/root/kis-autotrade-v4/.env`):

```
# --- 데이터베이스 ---
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kisautotrade
DB_USER=kis_admin
DB_PASSWORD=[DB-PASSWORD]
DATABASE_URL=[DB_CONNECTION_STRING]
DATABASE_URL_SYNC=[DB_CONNECTION_STRING]
```

### (b) 실제 DB 목록 (`sudo -u postgres psql -c "\l"`)

```
                                                           List of databases
     Name      |   Owner   | Encoding | Locale Provider |   Collate   |    Ctype    | ICU Locale | ICU Rules |    Access privileges    
---------------+-----------+----------+-----------------+-------------+-------------+------------+-----------+-------------------------
 kis_autotrade | kis_admin | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |            |           | =Tc/kis_admin          +
               |           |          |                 |             |             |            |           | kis_admin=CTc/kis_admin
 kisautotrade  | kis_admin | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |            |           | =Tc/kis_admin          +
               |           |          |                 |             |             |            |           | kis_admin=CTc/kis_admin
 postgres      | postgres  | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |            |           | 
 template0     | postgres  | ...
 template1     | postgres  | ...
(5 rows)
```

### (c) 실제 사용자 목록 (`sudo -u postgres psql -c "\du"`)

```
                             List of roles
 Role name |                         Attributes                         
-----------+------------------------------------------------------------
 kis_admin | Create DB
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS
```

---

## 2. DB 실제 접속 정보 (보고 표)

| 항목 | 값 |
|------|-----|
| DB명 | kisautotrade |
| 사용자 | kis_admin (애플리케이션) / postgres (관리) |
| 접속 방법 | `sudo -u postgres psql -d kisautotrade` 또는 `PGPASSWORD='[DB-PASSWORD]' psql -h localhost -U kis_admin -d kisautotrade` |
| .env DATABASE_URL | [DB_CONNECTION_STRING] |

---

## 3. go100_strategy_cards (요약 테이블)

| go100_card_id | strategy_name | card_status | user_id | strategy_type |
|------|------|------|------|------|
| 1 | E2E 포지션사이징 테스트 | LIVE | 1 | CUSTOM |
| 2 | 중형주 RSI 역추세 스윙 | DRAFT | 1 | LLM_GENERATED |
| 3 | 거래량 폭발 신고가 단타 | DRAFT | 1 | LLM_GENERATED |
| 4 | 3분봉 골든크로스 스캘핑 | PAPER_LIVE | 2 | LLM_GENERATED |
| 5 | 데일리 수급 반등 전략 | PAPER_LIVE | 2 | LLM_GENERATED |
| 6 | 단기 스윙 눌림목 전략 | PAPER_LIVE | 2 | LLM_GENERATED |
| 7 | 3분봉 VWAP 스캘핑 | DRAFT | 2 | LLM_GENERATED |
| 8 | 3분봉 스캘핑 골든크로스 | DRAFT | 2 | LLM_GENERATED |
| 9 | 3분봉 VWAP 스캘핑 전략 | DRAFT | 2 | LLM_GENERATED |
| 10 | 코스닥 소형주 3분봉 스캘핑 | BACKTESTED | 2 | LLM_GENERATED |
| 11 | 코스피200 골든크로스 스윙 | BACKTESTED | 2 | LLM_GENERATED |
| 12 | 중형주 섹터모멘텀 눌림목 스윙 | BACKTESTED | 2 | LLM_GENERATED |
| 13 | [스캘핑] 분봉 스캘핑 고변동 대형주 | BACKTESTED | 2 | LLM_GENERATED |
| 14 | [데일리] 대형 우량주 수급 데일리 전략 | BACKTESTED | 2 | LLM_GENERATED |
| 15 | [단기스윙] 섹터모멘텀 외국인수급 스윙 | BACKTESTED | 2 | LLM_GENERATED |

---

## 4. v4_users (두 계정)

| user_id | email | nickname |
|------|------|
| 3 | [CEO-EMAIL-NV] | 오병용 |
| 2 | [CEO-EMAIL-GM] | 대표님 |

※ v4_users 테이블에는 `username` 컬럼 없음. `nickname` 사용.

---

## 5. users (레거시, 두 계정)

| id | email | name |
|------|------|
| 6 | [CEO-EMAIL-GM] | 대표님 |
| 15 | [CEO-EMAIL-NV] | 오병용 |

---

## 6. 건수 확인

| 항목 | 건수 |
|------|------|
| go100_strategy_cards 전체 | 15 |
| go100_strategy_cards (13, 14, 15) | 3 |
| strategy_cards (V4.1) | 59 |
| v4_positions OPEN | 5 |

---

## 7. 컬럼 구조 (\d 결과 그대로)

### go100_strategy_cards

```
                                                 Table "public.go100_strategy_cards"
        Column        |           Type           | Collation | Nullable |                           Default                           
----------------------+--------------------------+-----------+----------+-------------------------------------------------------------
 go100_card_id        | bigint                   |           | not null | nextval('go100_strategy_cards_go100_card_id_seq'::regclass)
 user_id              | integer                  |           | not null | 
 account_id           | integer                  |           |          | 
 strategy_name        | character varying(200)   |           | not null | 
 strategy_type        | character varying(20)    |           | not null | 'CUSTOM'::character varying
 universe_filter      | jsonb                    |           |          | '{}'::jsonb
 entry_rules          | jsonb                    |           |          | '[]'::jsonb
 exit_rules           | jsonb                    |           |          | '[]'::jsonb
 risk_params          | jsonb                    |           |          | '{}'::jsonb
 strategy_params      | jsonb                    |           |          | '{}'::jsonb
 allocated_amount     | numeric(15,2)            |           |          | 0
 max_stocks           | integer                  |           |          | 5
 card_status          | character varying(20)    |           | not null | 'IDEA'::character varying
 is_active            | boolean                  |           |          | true
 is_live              | boolean                  |           |          | false
 source_type          | character varying(20)    |           |          | 'CUSTOM'::character varying
 source_store_card_id | bigint                   |           |          | 
 source_user_id       | integer                  |           |          | 
 llm_session_id       | character varying(100)   |           |          | 
 last_backtest_id     | bigint                   |           |          | 
 last_backtest_return | numeric(10,4)            |           |          | 
 last_backtest_mdd    | numeric(10,4)            |           |          | 
 last_backtest_sharpe | numeric(10,4)            |           |          | 
 last_backtest_at     | timestamp with time zone |           |          | 
 paper_total_return   | numeric(10,4)            |           |          | 
 paper_start_date     | date                     |           |          | 
 paper_days           | integer                  |           |          | 0
 disclaimer_agreed    | boolean                  |           |          | false
 disclaimer_agreed_at | timestamp with time zone |           |          | 
 dedicated_account    | boolean                  |           |          | false
 created_at           | timestamp with time zone |           |          | now()
 updated_at           | timestamp with time zone |           |          | now()
Indexes:
    "go100_strategy_cards_pkey" PRIMARY KEY, btree (go100_card_id)
    "idx_go100_cards_account" btree (account_id)
    "idx_go100_cards_live" btree (user_id, is_live) WHERE is_live = true
    "idx_go100_cards_source" btree (source_type, source_store_card_id)
    "idx_go100_cards_status" btree (card_status)
    "idx_go100_cards_user" btree (user_id)
Check constraints:
    "go100_strategy_cards_card_status_check" CHECK (card_status::text = ANY (ARRAY['IDEA'::character varying, 'DRAFT'::character varying, 'BACKTESTED'::character varying, 'PAPER_LIVE'::character varying, 'LIVE'::character varying, 'PAUSED'::character varying, 'RETIRED'::character varying]::text[]))
    "go100_strategy_cards_source_type_check" CHECK (source_type::text = ANY (ARRAY['SYSTEM'::character varying, 'CUSTOM'::character varying, 'LLM'::character varying, 'SHARED'::character varying]::text[]))
    "go100_strategy_cards_strategy_type_check" CHECK (strategy_type::text = ANY (ARRAY['CUSTOM'::character varying, 'BUILTIN'::character varying, 'LLM_GENERATED'::character varying, 'SUBSCRIBED'::character varying]::text[]))
Foreign-key constraints:
    "go100_strategy_cards_account_id_fkey" FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    "go100_strategy_cards_user_id_fkey" FOREIGN KEY (user_id) REFERENCES v4_users(user_id)
Referenced by:
    TABLE "go100_backtest_runs" CONSTRAINT "go100_backtest_runs_go100_card_id_fkey" FOREIGN KEY (go100_card_id) REFERENCES go100_strategy_cards(go100_card_id)
    TABLE "go100_fit_analysis" CONSTRAINT "go100_fit_analysis_go100_card_id_fkey" FOREIGN KEY (go100_card_id) REFERENCES go100_strategy_cards(go100_card_id)
    TABLE "go100_portfolios" CONSTRAINT "go100_portfolios_go100_card_id_fkey" FOREIGN KEY (go100_card_id) REFERENCES go100_strategy_cards(go100_card_id)
    TABLE "go100_risk_disclaimers" CONSTRAINT "go100_risk_disclaimers_strategy_card_id_fkey" FOREIGN KEY (strategy_card_id) REFERENCES go100_strategy_cards(go100_card_id)
```

### strategy_cards

```
                                              Table "public.strategy_cards"
       Column        |           Type           | Collation | Nullable |                     Default                     
---------------------+--------------------------+-----------+----------+-------------------------------------------------
 card_id             | bigint                   |           | not null | nextval('strategy_cards_card_id_seq'::regclass)
 user_id             | bigint                   |           | not null | 
 account_id          | bigint                   |           | not null | 
 strategy_name       | character varying(100)   |           | not null | 
 strategy_type       | character varying(30)    |           | not null | 'CUSTOM'::character varying
 strategy_params     | jsonb                    |           | not null | '{}'::jsonb
 allocated_amount    | numeric(15,0)            |           | not null | 0
 max_stocks          | integer                  |           | not null | 5
 is_live             | boolean                  |           | not null | false
 is_active           | boolean                  |           | not null | true
 desk_id             | character varying(10)    |           |          | 
 created_at          | timestamp with time zone |           | not null | now()
 updated_at          | timestamp with time zone |           | not null | now()
 entry_rules         | jsonb                    |           |          | '{}'::jsonb
 exit_rules          | jsonb                    |           |          | '{}'::jsonb
 risk_params         | jsonb                    |           |          | '{}'::jsonb
 buy_phases          | jsonb                    |           |          | '[]'::jsonb
 sell_phases         | jsonb                    |           |          | '[]'::jsonb
 promotion_rules     | jsonb                    |           |          | '{}'::jsonb
 demotion_rules      | jsonb                    |           |          | '{}'::jsonb
 backtest_compatible | boolean                  |           |          | false
 priority            | integer                  |           |          | 0
 version             | integer                  |           |          | 1
Indexes:
    "strategy_cards_pkey" PRIMARY KEY, btree (card_id)
    "idx_strategy_cards_account" btree (account_id)
    "idx_strategy_cards_live" btree (is_live) WHERE is_live = true
    "idx_strategy_cards_user" btree (user_id)
Check constraints:
    "strategy_cards_strategy_type_check" CHECK (strategy_type::text = ANY (ARRAY['BUILTIN'::character varying, 'CUSTOM'::character varying]::text[]))
Foreign-key constraints:
    "strategy_cards_account_id_fkey" FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
    "strategy_cards_user_id_fkey" FOREIGN KEY (user_id) REFERENCES v4_users(user_id) ON DELETE CASCADE
Referenced by:
    TABLE "v4_backtest_runs" CONSTRAINT "v4_backtest_runs_strategy_card_id_fkey" FOREIGN KEY (strategy_card_id) REFERENCES strategy_cards(card_id)
```

### v4_users

```
                                            Table "public.v4_users"
     Column      |           Type           | Collation | Nullable |                  Default                  
-----------------+--------------------------+-----------+----------+-------------------------------------------
 user_id         | bigint                   |           | not null | nextval('v4_users_user_id_seq'::regclass)
 email           | character varying(255)   |           | not null | 
 nickname        | character varying(50)    |           | not null | 
 hashed_password | character varying(255)   |           | not null | 
 tier            | character varying(20)    |           | not null | 'FREE'::character varying
 is_active       | boolean                  |           | not null | true
 last_login_at   | timestamp with time zone |           |          | 
 created_at      | timestamp with time zone |           | not null | now()
 updated_at      | timestamp with time zone |           | not null | now()
 phone           | character varying(50)    |           |          | 
Indexes:
    "v4_users_pkey" PRIMARY KEY, btree (user_id)
    "idx_v4_users_email" btree (email)
    "v4_users_email_key" UNIQUE CONSTRAINT, btree (email)
Check constraints:
    "v4_users_tier_check" CHECK (tier::text = ANY (ARRAY['FREE'::character varying, 'PRO'::character varying, 'PREMIUM'::character varying]::text[]))
Referenced by: (accounts, go100_portfolios, go100_strategy_cards, strategy_cards, user_sessions, v4_chat_sessions, v4_llm_usage, v4_notification_*, v4_trade_*, v4_user_settings)
```

---

## 8. strategy_card_service.py 상위 100줄

```python
"""
Modified by: CUR-GO100-STRATEGY-CARD-FIX, 2026-02-22 — list_cards_with_system에 go100_strategy_cards 병합
Modified by CUR-J-CRUD-v1, 2026-02-19, Strategy Card CRUD Service
CUR-J-FIX-v1, 2026-02-19, R4 리뷰 WARNING 수정 (W14)
GO100 Phase 4 R4
Created/Modified by CUR-STRATEGY-CARDS-MOBILE-v1, 2026-02-20
Modified by CUR-HOTFIX-ACTIVATE-500-v1, 2026-02-20
Modified by CUR-STRATEGY-CARD-MAPPING-FIX-v1, 2026-02-20 — create_card에 strategy_type 저장 (CUSTOM)
Modified by CUR-STRATEGY-CARD-UI-REDESIGN-v1, 2026-02-20 — delete_card: is_live 시 삭제 불가
Modified by CUR-BACKTEST-CARD6-TEST, 2026-02-20 — list_cards_for_backtest: 전체 활성 카드 (백테스트 드롭다운용)
"""

import json
import logging
from typing import Optional, List, Any
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.strategy_card_schemas import (
    StrategyCardCreateRequest,
    StrategyCardUpdateRequest,
    StrategyCardToggleRequest,
    StrategyCardResponse,
    StrategyCardListResponse,
    StrategyCardToggleResponse,
    StrategyCardDeleteResponse,
    StrategyCardDisplay,
    StrategyCardDisplayListResponse,
    StrategyActivateRequest,
)
from backend.app.services.tier_limit_service import (
    check_card_limit,
    check_real_trading_allowed,
)

logger = logging.getLogger("go100.card_service")


class CardServiceError(Exception):
    pass


class CardNotFoundError(CardServiceError):
    pass


class CardOwnershipError(CardServiceError):
    pass


def _parse_desk_id(value) -> Optional[int]:
    """DB desk_id는 varchar(10). int로 파싱 가능하면 반환."""
    if value is None:
        return None
    s = str(value).strip()
    return int(s) if s.isdigit() else None


def _parse_strategy_params(value) -> Optional[dict]:
    """DB jsonb → dict. 이미 dict면 그대로."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    return None


class StrategyCardService:
    """
    전략 카드 CRUD 서비스.
    - 생성: 티어 제한 + 계좌 소유권 확인
    - 토글: is_live on/off, buy_block 확인, 실거래 tier 검증
    - 삭제: soft delete (is_active = false)
    """

    async def _verify_card_ownership(
        self, card_id: int, user_id: int, db: AsyncSession
    ) -> tuple:
        """카드 존재 + 소유권 확인. row 튜플 반환."""
        result = await db.execute(
            text("""
                SELECT card_id, user_id, account_id, strategy_name,
                       allocated_amount, max_stocks, is_live, desk_id,
                       strategy_params, is_active, created_at, updated_at
                FROM strategy_cards
                WHERE card_id = :cid AND is_active = true
            """),
            {"cid": card_id},
        )
        row = result.fetchone()
        if row is None:
            raise CardNotFoundError(f"Card {card_id} not found")
        if row[1] != user_id:
            raise CardOwnershipError(f"Card {card_id} not owned by user {user_id}")
```

---

## 9. strategy_cards_router.py (V1) 상위 100줄

```python
"""
Modified by CUR-J-CRUD-v1, 2026-02-19, Strategy Card CRUD API Router
Modified by CUR-HOTFIX-STRATEGY-NAMEERROR-v1, CUR-HOTFIX-ACTIVATE-500-v1, 2026-02-20
Modified by CUR-STRATEGY-CARD-UI-REDESIGN-v1, 2026-02-20 — delete_card CardServiceError 처리
Modified by CUR-BACKTEST-CARD6-TEST, 2026-02-20 — GET /for-backtest: 백테스트용 전체 활성 카드
GO100 Phase 4 R4
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security_middleware import get_current_user
from backend.app.schemas.strategy_card_schemas import (
    StrategyCardCreateRequest,
    StrategyCardUpdateRequest,
    StrategyCardToggleRequest,
    StrategyCardResponse,
    StrategyCardListResponse,
    StrategyCardDisplayListResponse,
    StrategyCardToggleResponse,
    StrategyCardDeleteResponse,
    StrategyActivateRequest,
)
from backend.app.services.strategy_card_service import (
    strategy_card_service,
    CardNotFoundError,
    CardOwnershipError,
    CardServiceError,
)
from backend.app.services.tier_limit_service import (
    CardLimitExceededError,
    RealTradingNotAllowedError,
    TierLimitError,
)

logger = logging.getLogger("go100.cards_router")

router = APIRouter(prefix="/strategy-cards", tags=["Strategy Cards"])


@router.post("", response_model=StrategyCardResponse, status_code=201)
async def create_card(
    req: StrategyCardCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ...

@router.get("", response_model=StrategyCardListResponse)
async def list_cards(...): ...

@router.get("/for-backtest", response_model=StrategyCardListResponse)
async def list_cards_for_backtest(...): ...

@router.get("/catalog", response_model=StrategyCardDisplayListResponse)
async def list_catalog(
    account_id: Optional[int] = Query(None, description="계좌 필터 (선택)"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """시스템 전략 + 사용자 카드 통합 목록 (모바일용). CUR-STRATEGY-CARDS-MOBILE-v1"""
    return await strategy_card_service.list_cards_with_system(
        current_user["user_id"], account_id, db
    )

@router.get("/active", response_model=StrategyCardListResponse)
async def list_active_cards(...): ...
```

---

## 10. go100_strategy_cards 전체 데이터 (SELECT * 요약)

- 15건 모두 존재. user_id=1 인 카드 3건(1,2,3), user_id=2 인 카드 12건(4~15).
- 카드 13, 14, 15: 모두 user_id=2, card_status=BACKTESTED, strategy_type=LLM_GENERATED.
- 전체 행(raw) 출력은 jsonb 컬럼이 길어 생략. 필요 시 아래로 직접 조회:

```sql
SELECT * FROM go100_strategy_cards ORDER BY go100_card_id;
```

---

## 요약 (백엔드/프론트 지시서 작성용)

| 항목 | 내용 |
|------|------|
| DB | kisautotrade (루트 .env와 일치) |
| 사용자 테이블 | v4_users (user_id bigint, email, nickname). 레거시 users(id, email, name) 별도 존재 |
| 전략 카드 | **go100_strategy_cards**: GO100용, 15건, card_status/strategy_type 등 풀 스펙. **strategy_cards**: V4.1 대시/CRUD용, 59건, card_id/user_id/account_id/desk_id 등 |
| Catalog API | `GET /strategy-cards/catalog` → `list_cards_with_system()` (시스템 전략 + 사용자 카드 통합). 서비스는 strategy_cards 기반 + go100_strategy_cards 병합 처리 |
| 두 계정 | [CEO-EMAIL-NV] → v4_users.user_id=3 (오병용), [CEO-EMAIL-GM] → v4_users.user_id=2 (대표님) |

※ 코드/DB 변경 없음. 조사만 수행함.
