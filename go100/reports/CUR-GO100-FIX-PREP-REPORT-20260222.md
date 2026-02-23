# CUR-GO100-FIX-PREP 보고서 (지시서 1/3)

**작성일:** 2026-02-22  
**대상:** CUR-GO100-FIX-PREP — 사전작업 + DB 정리

---

## 환경 참고

- **지시서 명시:** `psql -U go100user -d go100db`
- **현재 서버 조사:** DB 목록에 `go100db` / 사용자 `go100user` 없음. `kisautotrade` DB, `kis_admin` / `postgres` 사용자만 존재.
- **실행 방법:** 아래 스크립트를 사용해, 실제 접속 가능한 계정으로 STEP 1~4를 실행한 뒤, 터미널 출력을 이 보고서의 "STEP 2 원본 출력"에 붙여 넣어 두면 지시서 2·3 병렬 진행 시 참고 가능.

---

## STEP 1: DB 백업

다음 명령 또는 제공 스크립트로 백업 생성.

```bash
# go100user / go100db 사용 시
pg_dump -U go100user -d go100db -F c -f /tmp/backup_STRATEGY_CARD_FIX_$(date +%Y%m%d_%H%M%S).dump

# postgres / kisautotrade 사용 시
sudo -u postgres pg_dump -d kisautotrade -F c -f /tmp/backup_STRATEGY_CARD_FIX_$(date +%Y%m%d_%H%M%S).dump
```

**실행 스크립트:** `scripts/cur_go100_fix_prep.sh` (STEP 1~4 일괄 실행, 연결 변수만 설정 후 사용)

---

## STEP 2: 전체 사전 상태 조사

### (a) go100_strategy_cards 전체 현황

지시서 쿼리:

```sql
SELECT id, name, status, user_id, strategy_type, created_at 
FROM go100_strategy_cards ORDER BY id;
```

**참고:** 코드베이스에서는 `go100_strategy_cards`에 **go100_card_id**, **strategy_name**, **card_status** 컬럼을 사용합니다. 실제 DB에 `id`/`name`/`status`가 있으면 위 쿼리 그대로, 없으면 아래처럼 alias 사용.

```sql
SELECT go100_card_id AS id, strategy_name AS name, card_status AS status, user_id, strategy_type, created_at 
FROM go100_strategy_cards ORDER BY go100_card_id;
```

*(실제 출력은 스크립트 실행 후 터미널 결과를 붙여 넣으세요.)*

---

### (b) users 테이블 — 두 계정 확인

```sql
SELECT id, email, username FROM users 
WHERE email IN ('moongoby@naver.com','moongoby@gmail.com');
```

*(실제 출력은 스크립트 실행 후 터미널 결과를 붙여 넣으세요.)*

---

### (c) V4.1 positions OPEN 건수

```sql
SELECT COUNT(*) FROM v4_positions WHERE status='OPEN';
```

*(실제 출력은 스크립트 실행 후 터미널 결과를 붙여 넣으세요.)*

---

### (d) V4.1 strategy_cards 건수

```sql
SELECT COUNT(*) AS v4_cards FROM strategy_cards;
```

*(실제 출력은 스크립트 실행 후 터미널 결과를 붙여 넣으세요.)*

---

### (e) 두 테이블 컬럼 구조 비교

지시서:

```text
psql -U go100user -d go100db -c "\d strategy_cards"
psql -U go100user -d go100db -c "\d go100_strategy_cards"
```

*(실제 출력은 스크립트 실행 후 터미널 결과를 붙여 넣으세요.)*

**코드베이스 기준 컬럼 요약:**

| 테이블 | 코드에서 사용하는 컬럼 (요약) |
|--------|------------------------------|
| **strategy_cards** | card_id, user_id, account_id, strategy_name, strategy_type, allocated_amount, max_stocks, is_live, desk_id, strategy_params, is_active, created_at, updated_at |
| **go100_strategy_cards** | go100_card_id, user_id, account_id, strategy_name, strategy_type, universe_filter, entry_rules, exit_rules, risk_params, strategy_params, allocated_amount, max_stocks, card_status, is_active, is_live, source_type, source_store_card_id, source_user_id, llm_session_id, last_backtest_*, paper_*, disclaimer_*, dedicated_account, created_at, updated_at |

---

### (f) 전략카드 관련 API 라우터 / 프론트엔드 파일 탐색 결과

#### 백엔드 라우터 (지시서 2·3에서 필요)

| 파일 경로 | 비고 |
|-----------|------|
| `backend/app/routers/go100/strategy_router.py` | prefix: `/api/go100/strategy-cards`, GO100 전략 카드 CRUD |
| `backend/app/routers/go100/risk_router.py` | go100_strategy_cards 참조 (risk_params) |
| `backend/app/routers/go100/ai_router.py` | go100_strategy_cards 참조 |
| `backend/app/routers/v4_trading.py` | `/strategies/scores`, `/strategies/weights`, `/trading/strategies` |
| `backend/app/routers/v4_compat.py` | `/live-trading/strategies` |
| `backend/app/routers/backtest_router.py` | strategy_cards 참조 |

#### main.py 라우터 등록

- `from backend.app.api.v1.strategy_cards_router import router as strategy_cards_v1_router`
- `from backend.app.routers.strategy import router as strategy_router`
- `from backend.app.routers.go100.strategy_router import router as go100_strategy_router, store_router as go100_store_router`
- `app.include_router(strategy_router)`
- `app.include_router(strategy_cards_v1_router, prefix="/api/v1")`
- `app.include_router(go100_strategy_router)`

#### 프론트엔드 (app)

- `frontend/src/app/(protected)/go100/strategies/page.tsx`
- `frontend/src/app/(protected)/trade/page.tsx`
- `frontend/src/app/(protected)/dashboard/page.tsx`

#### 프론트엔드 (go100)

- `frontend/src/go100/components/StrategyCard.tsx`
- `frontend/src/go100/components/StrategyCardDetail.tsx`
- `frontend/src/go100/components/Go100Sidebar.tsx`
- `frontend/src/go100/components/SettingsRiskSection.tsx`
- `frontend/src/go100/components/StrategyResultCard.tsx`

---

## STEP 3: DB 정리 (테스트 데이터 삭제)

```sql
DELETE FROM go100_strategy_cards WHERE id NOT IN (13, 14, 15);
```

PK 컬럼이 `go100_card_id`만 있는 경우:

```sql
DELETE FROM go100_strategy_cards WHERE go100_card_id NOT IN (13, 14, 15);
```

**검증:** 정확히 3건(13, 14, 15)만 남아야 함.

---

## STEP 4: user_id 정합성 수정 (변경 실행)

**상태:** 변경 보류 → **변경 실행**. `user_id = 3` (moongoby@naver.com)으로 업데이트한다.

**실행:**

```bash
PGPASSWORD='KisAuto2026!Secure' psql -h localhost -U kis_admin -d kisautotrade -c "
  UPDATE go100_strategy_cards 
  SET user_id = 3 
  WHERE go100_card_id IN (13, 14, 15);
"
```

**검증:**

```bash
PGPASSWORD='KisAuto2026!Secure' psql -h localhost -U kis_admin -d kisautotrade -c "
  SELECT sc.go100_card_id, sc.strategy_name, sc.user_id, u.email
  FROM go100_strategy_cards sc
  JOIN v4_users u ON sc.user_id = u.user_id
  WHERE sc.go100_card_id IN (13, 14, 15);
"
```

→ 3건 모두 `user_id = 3`, `email = moongoby@naver.com` 이어야 함.

---

## 완료 후 보고 — 5가지 요약 (지시서 2·3 병렬 진행용)

스크립트 실행 후 아래를 채워 두세요.

| 항목 | 값 |
|------|-----|
| **1) moongoby@naver.com의 user_id** | *(STEP 2-(b) 결과에서 id 값)* |
| **2) go100_strategy_cards 컬럼 목록** | *(실제 `\d go100_strategy_cards` 출력 또는 위 코드 기준 요약)* |
| **3) strategy_cards 컬럼 목록** | *(실제 `\d strategy_cards` 출력 또는 위 코드 기준 요약)* |
| **4) 전략 관련 라우터 파일 경로** | 위 (f) 표 참고 (라우터 목록) |
| **5) 전략 관련 프론트엔드 파일 경로** | 위 (f) 표 참고 (app + go100 목록) |

---

## 스크립트 실행 방법

```bash
cd /root/kis-autotrade-v4
chmod +x scripts/cur_go100_fix_prep.sh
# 연결 설정 후 실행 (예: kisautotrade 사용 시)
export PGHOST=localhost PGUSER=kis_admin PGDATABASE=kisautotrade PGPASSWORD='비밀번호'
./scripts/cur_go100_fix_prep.sh
# 또는 postgres 소켓 접속 시
sudo -u postgres bash -c 'export PGUSER=postgres PGDATABASE=kisautotrade; ./scripts/cur_go100_fix_prep.sh'
```

이 보고서와 스크립트 실행 결과를 바탕으로 지시서 2(백엔드), 지시서 3(프론트엔드)을 병렬 진행하면 됩니다.
