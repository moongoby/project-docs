# CUR-GO100-P6-1: 리스크 관리 엔진 + Kill Switch

**작성일**: 2026-02-27  
**태스크**: P6-1 리스크 관리 엔진 + Kill Switch 구현  
**상태**: 완료

---

## 인계 확인

| 항목 | 내용 |
|------|------|
| 직전 완료 | Batch 3 (P3-1/2/3), P4-3 30일 모의투자 |
| 현재 단계 | Phase 6 — 실매매 전 안전장치 |
| CEO 지시 적용 | HANDOVER v8, 보고서 push 필수 |
| strategy_cards | 시드 3건 (35/36/37) |
| open_positions | go100_positions / go100_paper_trades 기준 |

---

## 1. 개요

실매매 전 필수 안전장치로 **리스크 관리 엔진**과 **Kill Switch**를 도입하였다.  
모의투자(P4-3)에도 동일 규칙을 적용하여 검증할 수 있도록 연동하였다.

| 기능 | 설명 |
|------|------|
| 매매 전 체크 | check_pre_trade: 킬스위치, 종목당 비중, 섹터 집중, 총 노출 한도 |
| 일일 손익 체크 | check_daily_pnl: 일일 손실 한도 초과 시 WARNING / 자동 킬스위치 옵션 |
| 킬스위치 | activate: 전량 매도 주문 생성, 신규 매수 차단 / deactivate: CEO(user_id=2) 전용 |
| 리스크 현황 | get_risk_status: 노출도, 집중도, 일일 손익, 활성 규칙 |

---

## 2. 구현 내역

### 2.1 DB 마이그레이션 (`backend/migrations/046_go100_risk_engine.sql`)

- **go100_risk_rules**
  - `rule_id`, `user_id`, `rule_type`, `threshold` (JSONB), `is_active`, `triggered_count`, `last_triggered_at`, `created_at`
  - rule_type: `DAILY_LOSS_LIMIT`, `POSITION_SIZE_LIMIT`, `SECTOR_CONCENTRATION`, `TOTAL_EXPOSURE`, `KILL_SWITCH`
  - threshold 예: `{"max_daily_loss_pct": -3.0}`, `{"max_position_pct": 20.0}`, `{"max_sector_pct": 40.0}`

- **go100_risk_events**
  - `event_id`, `user_id`, `rule_id` (FK), `event_type`, `details` (JSONB), `action_taken`, `created_at`
  - event_type: `WARNING`, `BLOCK`, `KILL_SWITCH_ACTIVATED`, `KILL_SWITCH_DEACTIVATED`
  - action_taken: `LOGGED`, `ORDER_BLOCKED`, `ALL_POSITIONS_CLOSED`

- 인덱스: `idx_risk_rules_user`, `idx_risk_events_user`

적용: `sudo -u postgres psql -d kisautotrade -f backend/migrations/046_go100_risk_engine.sql`

### 2.2 리스크 엔진 서비스 (`backend/app/services/go100/risk_engine.py`)

| 함수 | 설명 |
|------|------|
| **check_pre_trade(db, user_id, ticker, quantity, price, side, session_id=None)** | 매매 전 규칙 검사. 위반 시 BLOCK + go100_risk_events 기록, `allowed=False` 반환. 매도(side=SELL)는 검사 제외. |
| **check_daily_pnl(db, user_id)** | 당일 실현+미실현 손익 계산. 일일 손실 한도 규칙 위반 시 WARNING 이벤트 기록. threshold에 `auto_kill_switch: true` 시 자동 킬스위치 활성화. |
| **activate_kill_switch(db, user_id)** | 킬스위치 활성화: go100_risk_events에 KILL_SWITCH_ACTIVATED 기록. 실거래 포지션(go100_positions)에 대해 go100_orders에 시장가 매도 주문 INSERT (PENDING). 페이퍼 30d 세션은 호출 측에서 stop_session 호출 권장. |
| **deactivate_kill_switch(db, user_id)** | CEO(user_id=2) 전용. KILL_SWITCH_DEACTIVATED 이벤트 기록. |
| **get_risk_status(db, user_id, session_id=None)** | 킬스위치 여부, 총평가·현금·포지션가치, 노출비중, 섹터 집중도, 일일 손익, 활성 규칙 목록 반환. session_id 지정 시 30일 모의투자 세션 기준. |
| **setup_default_rules(db, user_id)** | 기본 규칙 3건 생성: 일일 손실 -3%, 종목당 20%, 섹터 40%. 기존 활성 규칙이 있으면 추가하지 않음. |
| **set_risk_rule(db, user_id, rule_type, threshold, is_active=True)** | 규칙 설정/변경. 동일 rule_type 있으면 UPDATE, 없으면 INSERT. |

- 포트폴리오/포지션 컨텍스트: `session_id`가 있으면 go100_paper_trading_sessions + go100_paper_trades 기반, 없으면 go100_portfolios + go100_positions 기반.
- 킬스위치 활성 여부: go100_risk_events에서 해당 user_id의 최신 event_type이 KILL_SWITCH_ACTIVATED이면 활성.

### 2.3 Agent Tools (3개)

- **get_risk_status(session_id=None)**  
  현재 리스크 현황. 킬스위치, 노출도, 일일 손익, 활성 규칙 등.

- **activate_kill_switch()**  
  긴급 킬스위치 활성화. 전량 매도 주문 생성, 신규 매수 차단.

- **set_risk_rule(rule_type, threshold, is_active=True)**  
  리스크 규칙 설정/변경. rule_type: DAILY_LOSS_LIMIT, POSITION_SIZE_LIMIT, SECTOR_CONCENTRATION, TOTAL_EXPOSURE.

추가 위치: `backend/app/services/go100/ai/agent_tools.py` (AGENT_TOOLS), `tool_executors.py` (함수 + TOOL_EXECUTORS).

### 2.4 Paper Trading 연동

- **paper_trading_engine_30d.run_daily_check**
  - 매수 후보에 대해 `_insert_trade(BUY)` 직전에 `risk_engine.check_pre_trade(db, user_id, ticker, qty, exec_price, "BUY", session_id=session_id)` 호출.
  - `allowed=False`이면 해당 매수 건너뛰고 로그 출력.

### 2.5 테스트 스크립트

- **scripts/go100/test_risk_engine_p6_1.py**
  - setup_default_rules(user_id=2)
  - get_risk_status
  - check_pre_trade (한도 내 허용, 한도 초과 BLOCK)
  - activate_kill_switch → is_kill_switch_active 확인 → check_pre_trade 매수 BLOCK
  - deactivate_kill_switch (CEO만 가능)
  - go100_risk_events 최근 5건 조회

실행: 프로젝트 venv 활성화 후  
`python3 scripts/go100/test_risk_engine_p6_1.py`

---

## 3. 검증 요약

| 항목 | 결과 |
|------|------|
| 마이그레이션 046 적용 | CREATE TABLE / INDEX 정상 |
| 기본 규칙 세트 생성 | setup_default_rules(user_id=2) 정상 |
| check_pre_trade | 킬스위치 시 BLOCK, 규칙 위반 시 BLOCK + risk_event 기록 |
| 킬스위치 활성/해제 | KILL_SWITCH_ACTIVATED / KILL_SWITCH_DEACTIVATED 이벤트 기록 확인 |
| 모의투자 run_daily_check | 매수 전 check_pre_trade 연동 완료 (위반 시 해당 매수 스킵) |

---

## 4. 파일 변경 목록

| 경로 | 변경 |
|------|------|
| backend/migrations/046_go100_risk_engine.sql | 신규 |
| backend/app/services/go100/risk_engine.py | 신규 |
| backend/app/services/go100/paper_trading_engine_30d.py | risk_check_pre_trade import 및 매수 전 호출 추가 |
| backend/app/services/go100/ai/agent_tools.py | get_risk_status, activate_kill_switch, set_risk_rule 도구 정의 추가 |
| backend/app/services/go100/ai/tool_executors.py | 위 3개 실행 함수 및 TOOL_EXECUTORS 등록 |
| scripts/go100/test_risk_engine_p6_1.py | 신규 검증 스크립트 |

---

## 5. 체크리스트

- [x] 코드 레포(kis-autotrade-v4) 반영
- [ ] project-docs 보고서 push (본 문서)
- [ ] HANDOVER.md 업데이트 (완료 시)

---

**보고서 끝.**
