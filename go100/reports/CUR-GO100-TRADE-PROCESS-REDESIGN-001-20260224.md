# CUR-GO100-TRADE-PROCESS-REDESIGN-001 — 자동매매 프로세스 점검 및 재설계 보고서

**작성:** 2026-02-24  
**우선순위:** P1 (프로세스 재설계)  
**서버:** root@211.188.51.113  
**프로젝트:** /root/kis-autotrade-v4 (branch: phase-2c-command-center → docs/CUR-GO100-TRADE-PROCESS-REDESIGN-001)  
**참조:** [PLANNING](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/PLANNING.md), [API_SPEC](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/API_SPEC.md)

---

## 1. 현재 프로세스 (AS-IS)

### 1.1 전체 흐름

1. **전략 생성** — 백억이(LLM) 또는 직접 생성 → 전략카드 저장 (`go100_strategy_cards`)
2. **카드 저장 시 설정값** — `allocated_amount`, `max_stocks`, `risk_params`, `entry_rules`, `exit_rules`, `strategy_params`, `universe_filter` 등이 카드에 저장됨
3. **카드 토글** — 전략카드 상세 또는 목록에서 `is_active` ON/OFF (API: `PATCH /api/go100/strategy-cards/{card_id}/toggle`)
4. **스케줄 등록** — 사용자가 별도로 **/trade** 페이지에서 "스케줄 등록" 시:
   - 전략 선택(카드 ID 또는 V4.1 카드 ID), 계좌 선택, **투자금·종목수·손절·익절** 등을 다시 입력
   - API: `POST /api/v1/trade/schedules` (body: `strategy_id`, `account_id`, `card_source`(v41|go100), `invest_amount`, `max_stocks`, `stop_loss_pct`, `take_profit_pct` 등)
5. **매매 실행** — `schedule_runner`가 `v4_trade_schedules`를 폴링 → `AutoTradeEngine.run_strategy(TradeSchedule)` 호출 → 신호 생성·주문·기록

### 1.2 단계별 설정값

| 단계 | 설정되는 값 (저장 위치) |
|------|--------------------------|
| 전략 저장 | `go100_strategy_cards`: `allocated_amount`, `max_stocks`, `risk_params`(JSON: stop_loss_pct, take_profit_pct 등), `entry_rules`, `exit_rules`, `strategy_params`, `universe_filter`, `account_id`(선택) |
| 카드 토글 | `go100_strategy_cards.is_active` 만 변경. **스케줄 생성/수정 없음** |
| /trade 스케줄 등록 | `v4_trade_schedules`: `strategy_id`, `account_id`, `card_source`, `invest_amount`, `max_stocks`, `max_per_stock_pct`, `stop_loss_pct`, `take_profit_pct`, `run_interval`, `market_open_only` |

### 1.3 중복 설정값 (카드 vs 스케줄)

| 의미 | 카드 (go100_strategy_cards) | 스케줄 (v4_trade_schedules) |
|------|-----------------------------|----------------------------|
| 투자금 | `allocated_amount` | `invest_amount` |
| 최대 종목 수 | `max_stocks` | `max_stocks` |
| 손절 | `risk_params.stop_loss_pct` (또는 유사 키) | `stop_loss_pct` |
| 익절 | `risk_params.take_profit_pct` (또는 유사 키) | `take_profit_pct` |
| 계좌 | `account_id` (nullable) | `account_id` (필수, 스케줄별) |

---

## 2. 문제점

### 2.1 설정값 중복

- **투자금:** 카드 `allocated_amount` vs 스케줄 `invest_amount` — 사용자가 /trade에서 다시 입력해야 하며, 카드 값이 스케줄에 자동 반영되지 않음.
- **최대 종목 수:** 카드 `max_stocks` vs 스케줄 `max_stocks` — 동일.
- **손절/익절:** 카드 `risk_params` 내 stop_loss/take_profit vs 스케줄 `stop_loss_pct`, `take_profit_pct` — 동일.

### 2.2 활성화 토글의 의미 불명확

- `PATCH /api/go100/strategy-cards/{card_id}/toggle`는 **카드의 `is_active`만** 바꿈.
- **스케줄과 연동되지 않음:** 토글 ON 해도 `v4_trade_schedules`에 해당 카드에 대한 행이 없으면 자동매매가 실행되지 않음.
- 따라서 "활성화 = 자동매매 켜기"가 아니라 "카드 플래그만 바꾸기"로 동작함.

### 2.3 V4.1 /trade 페이지와 GO100 프로세스 불일치

- GO100은 **카드 자체가 완결된 전략**(투자금·종목수·손절·익절 포함)인데, 현재는 V4.1과 동일하게 **/trade에서 스케줄을 따로 등록**해야 함.
- 전략카드 상세에서는 "모의거래 시작" → `/go100/paper-trading`, "실거래 현황" → `/go100/live-trading` 링크만 있고, **V4 자동매매 스케줄(schedule_runner 기반)** 을 카드에서 직접 켜는 진입점이 없음.

### 2.4 auto_trade_engine이 읽는 설정값 출처

- **카드에서 읽는 것 (go100일 때):** `_get_strategy_card()` → `strategy_type`, `strategy_params`, `strategy_name` 만 SELECT.  
  (`backend/app/services/auto_trade_engine.py` 519–524행)
- **스케줄에서 읽는 것:** `invest_amount`, `max_stocks`, `max_per_stock_pct`, `stop_loss_pct`, `take_profit_pct` — 모두 **TradeSchedule(즉 v4_trade_schedules)** 에서 옴.  
  (같은 파일 162–166행, 589행, 602–604행 등)
- **결론:** 엔진은 **설정값을 스케줄 기준으로만 사용**하고, 카드의 `allocated_amount`/`max_stocks`/`risk_params`는 **자동매매 실행 시 사용하지 않음**.  
  따라서 GO100 카드만 활성화하고 스케줄을 안 만들면 매매가 되지 않으며, 스케줄을 만들면 그때 입력한 값이 사용됨.

---

## 3. 제안 프로세스 (TO-BE)

### 3.1 목표

- **전략카드 활성화 = 자동매매 시작 프로세스**로 재설계.
- 카드 상세에서 **계좌 선택 → 자동매매 시작/중지** 한 번에 처리.
- 설정값 중복 제거: 카드 값을 기본으로 하고, 필요 시 모달에서만 수정 가능하게.

### 3.2 제안 흐름

1. **전략 생성 → 카드 저장** — 기존과 동일. 모든 설정(투자금, 종목수, 손절/익절 등)은 카드에만 저장.
2. **백테스트** — 기존과 동일. 카드 기준 백테스트 실행.
3. **카드 상세에서 "자동매매 시작" 모달:**
   - **계좌 선택:** 키움 모의/실계좌 등 (사용자 소유 계좌 목록).
   - **설정값 표시/수정:** 카드의 `allocated_amount`, `max_stocks`, `risk_params`(손절/익절)를 **자동 로드**, 필요 시 사용자가 수정 가능.
   - **"시작" 클릭 시:**
     - `go100_strategy_cards.is_active = true`
     - `v4_trade_schedules`에 행 **자동 생성**:  
       `strategy_id=go100_card_id`, `card_source='go100'`, `account_id`=선택 계좌,  
       `invest_amount`/`max_stocks`/`stop_loss_pct`/`take_profit_pct` = 모달에서 확정된 값(기본은 카드 값).
4. **카드 토글 OFF(자동매매 중지):**
   - 해당 카드에 연결된 스케줄(`card_source='go100'` && `strategy_id=go100_card_id`)을 `is_active=false` 로 비활성화.
   - 필요 시 카드 `is_active=false` 로 유지.
5. **/trade 페이지:** V4.1 전용으로 유지. GO100 자동매매는 **카드 상세에서만 시작/중지**하고, /trade 목록에서는 GO100 스케줄을 "카드 기반"으로 표시만 하거나, 필요 시 카드로 이동하는 링크 제공.

### 3.3 요약

- **카드 활성화 = 스케줄 자동 생성 + 매매 시작**
- **카드 비활성화 = 스케줄 비활성화 + 매매 중지**
- **설정값:** 카드 1원천, 모달에서 선택적 수정 후 스케줄에 반영

---

## 4. 필요한 변경 사항 (구현 범위)

### 4.1 Backend

- **전략카드 "자동매매 시작" API (신규):**
  - 입력: `go100_card_id`, `account_id`, (선택) `invest_amount`, `max_stocks`, `stop_loss_pct`, `take_profit_pct` 등 오버라이드.
  - 처리: 카드에서 기본값 로드 → 없으면 요청값, 없으면 기본 상수 사용 → `go100_strategy_cards.is_active = true` 갱신, `v4_trade_schedules`에 `card_source='go100'` 행 INSERT.
- **토글 OFF 연동:**
  - `PATCH /api/go100/strategy-cards/{card_id}/toggle` 에서 `is_active`를 false로 바꿀 때,  
    `v4_trade_schedules`에서 `card_source='go100' AND strategy_id=:card_id` 인 행을 `is_active=false` 로 UPDATE.

### 4.2 Frontend

- **전략카드 상세 페이지** (`/go100/strategies/[id]`):
  - "자동매매 시작" 버튼 및 **모달 컴포넌트** 추가.
  - 모달: 계좌 선택(드롭다운), 투자금/종목수/손절/익절 표시 및 수정 필드(카드 값 기본), "시작" 버튼 → 위 신규 API 호출.
- **토글 OFF:** 기존 토글 유지. 백엔드에서 스케줄 비활성화 연동 후, 프론트는 토글만 호출하면 됨.

### 4.3 auto_trade_engine

- **card_source='go100'일 때:**  
  현재처럼 스케줄의 `invest_amount`, `max_stocks`, `stop_loss_pct`, `take_profit_pct`를 사용하면 됨.  
  **시작 모달**에서 카드 값으로 스케줄을 만들므로, 엔진은 기존 로직 유지해도 됨.
- (선택) 카드에서 직접 읽어서 스케줄 값이 비어 있을 때만 카드 값 fallback 하도록 확장 가능 — 1차는 스케줄만 사용해도 무방.

---

## 5. DB 변경 필요 여부

### 5.1 go100_strategy_cards

- **account_id:** 이미 존재 (`backend/migrations/020_go100_tables.sql`, `account_id INTEGER REFERENCES accounts(account_id)`).
- **allocated_amount, max_stocks, risk_params:** 이미 존재.  
- **추가 컬럼:** 없어도 됨. 자동매매 시작 시 선택한 계좌는 스케줄의 `account_id`에 저장하면 됨.  
  (카드에 "마지막 사용 계좌"를 남기려면 선택적으로 `account_id` 업데이트 가능.)

### 5.2 v4_trade_schedules

- **card_source:** 코드상 이미 사용 중 (`trade_router.py` INSERT/SELECT). 마이그레이션에 컬럼이 없다면 `ALTER TABLE v4_trade_schedules ADD COLUMN IF NOT EXISTS card_source VARCHAR(10) DEFAULT 'v41'` 등으로 추가 필요.
- **연동 방식:**  
  - GO100 카드에서 "시작" 시: `strategy_id = go100_card_id`, `card_source = 'go100'` 으로 INSERT.  
  - 토글 OFF 시: `card_source='go100' AND strategy_id=:go100_card_id` 인 행만 `is_active=false` 로 UPDATE.  
  - 한 카드당 활성 스케줄 1개로 제한할지, 계좌별로 여러 개 허용할지는 기획에 따라 결정 (1카드 1계좌 1스케줄이면 단순).

---

## 6. 영향 범위

### 6.1 기존 V4.1 /trade 프로세스

- **영향 없음.**  
  - /trade 페이지의 스케줄 등록/수정/삭제 API와 목록은 그대로 두고, `card_source='v41'` 또는 기존 스케줄만 다루면 됨.  
  - GO100 전용 "자동매매 시작"은 카드 상세에서만 새 API를 타도록 하면 됨.

### 6.2 go100/paper-trading, go100/live-trading

- **역할 정리:**  
  - **paper-trading / live-trading:** GO100 전용 **모의/실거래 포트폴리오·포지션·주문** 관리 (별도 엔진/테이블: go100_portfolios, go100_positions 등).  
  - **v4_trade_schedules + schedule_runner:** V4 공통 **자동매매 스케줄 실행** (전략 신호 → 주문 → v4_trade_executions 등).  
- **관계:**  
  - 카드에서 "자동매매 시작"하면 **스케줄**이 생성되고, 이 스케줄은 **V4 자동매매 엔진**을 통해 실행됨.  
  - paper-trading/live-trading 페이지는 "GO100 전용 포트폴리오/실행 이력" 보기용으로 유지하고,  
    "자동매매 시작" 모달은 **어느 계좌를 쓸지(모의/실계좌)** 만 선택하게 하면 됨.  
  - 즉, 같은 카드를 "모의계좌로 자동매매" vs "실계좌로 자동매매"로 각각 스케줄을 두는 것은 구현 선택 사항.

### 6.3 정리

- V4.1 /trade: 변경 없음.  
- GO100: 카드 상세에서 자동매매 시작/중지로 일원화, 설정값 중복 제거.  
- paper-trading / live-trading: 기존 역할 유지, 자동매매 시작 모달과는 "계좌 선택"으로만 연계 가능.

---

## 7. 진단 시 실행한 명령 (참고)

- **DB:** 서버(211.188.51.113)에서 직접 실행 시 아래로 스키마/데이터 확인 가능.  
  (로컬에서 Peer 인증 등으로 접속 불가 시, 보고서는 코드·마이그레이션 기준으로 작성됨.)

```bash
# 1-1. go100_strategy_cards 설정값 컬럼
PGPASSWORD='KisAuto2026!Secure' psql -U kis_admin -d kisautotrade -c "
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name='go100_strategy_cards'
AND column_name IN ('allocated_amount','max_stocks','risk_params','entry_rules','exit_rules','is_active','is_live','card_status','strategy_params','universe_filter')
ORDER BY ordinal_position"

# 1-2. 카드 데이터 샘플
PGPASSWORD='KisAuto2026!Secure' psql -U kis_admin -d kisautotrade -c "
SELECT go100_card_id, strategy_name, card_status, is_active, is_live,
       allocated_amount, max_stocks, risk_params::text,
       length(entry_rules::text) AS entry_rules_len, length(exit_rules::text) AS exit_rules_len
FROM go100_strategy_cards ORDER BY go100_card_id LIMIT 5"

# 1-3. v4_trade_schedules 스키마
PGPASSWORD='KisAuto2026!Secure' psql -U kis_admin -d kisautotrade -c "
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name='v4_trade_schedules'
ORDER BY ordinal_position"

# 1-4. 스케줄 최근 5건
PGPASSWORD='KisAuto2026!Secure' psql -U kis_admin -d kisautotrade -c "
SELECT * FROM v4_trade_schedules ORDER BY created_at DESC LIMIT 5"
```

- **코드:**  
  - 토글: `backend/app/routers/go100/strategy_router.py` (PATCH toggle, 스케줄 연동 없음).  
  - 스케줄 생성: `backend/app/api/v1/trade_router.py` (POST /schedules, card_source 지원).  
  - 엔진: `backend/app/services/auto_trade_engine.py` (_get_strategy_card, run_strategy — 스케줄 기준 설정값 사용).  
  - 프론트: `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx` (토글·백테스트·모의/실거래 링크), `frontend/src/app/(protected)/trade/page.tsx` + `ScheduleForm.tsx` (투자금/종목수/손절/익절 입력).

---

## 8. 다음 단계

- 이 보고서는 **프로세스 점검 및 설계**만 포함합니다.  
- **코드 구현**은 대표님 확인 후 별도 지시서(예: CUR-GO100-TRADE-MODAL-IMPL-001)로 진행하는 것을 권장합니다.
