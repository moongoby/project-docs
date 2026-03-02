# CUR-V41-FUND-WEIGHT-AND-CARD-MIGRATE-001 보고서

## 기본 정보
- 작업일: 2026-02-23 17:30 KST
- 서버: root@[SERVER-IP]
- CEO 지시: DESK별 비중 확인 + GO100 테스트 카드 이동

---

## PART A: Fund Commander 비중 설정 현황

### A-1 Fund Commander 소스
- `backend/app/services/fund/` 디렉터리 없음. 비중/배분 로직은 **trading** 서비스에 구현됨.

### DESK별 비중 배정 방식
- **v4_risk_manager.py**: DESK별 기본값(Stage 무관)  
  - DESK 1: allocation_pct 15%, max_positions 2  
  - DESK 2: 35%, 6  
  - DESK 3: 30%, 5  
  - DESK 4: 15%, 3  
  - DESK 5: 5%, 2  
- **v4_desk_fund** 테이블: `allocation_pct`, `allocated_amount`, `max_positions`, `daily_loss_limit` 저장.  
  `v4_pipeline_orchestrator`에서 DESK 설정 조회 시 위 컬럼 사용.
- **compound_engine.py**: Stage별 `calculate_allocation(stage)`로 DESK별 allocation_pct/allocated_amount 갱신 후 v4_desk_fund에 반영.
- **v4_trade_bridge**: `allocation_pct`로 투자 가능 금액 계산 (`alloc_cash = cash * allocation_pct`).
- 단일 종목 최대 비중: pipeline_orchestrator에서 `max_single_amount` 등으로 제한(기본 10% 언급).

### 사용자 설정 반영 방식
- **v4_compat**: `us.allocation_pct`(사용자 설정) 사용.
- **strategy_cards**: 카드 단위 `allocated_amount` 컬럼 보유.
- **go100**: `get_desk_allocation`, 카드별 `card_allocations` 등으로 사용자 배분 반영.

### strategy_cards 비중 관련 컬럼
- `allocated_amount` (numeric), `max_stocks` (integer). 비중%는 DESK/사용자 설정 쪽에서 처리.

### DB DESK/비중 관련 테이블
- go100_desk_allocation, v4_desk_fund, v4_desk_strategy_mapping, strategy_allocations, v4_fund_lending, v4_fund_pool_snapshot, v4_scoring_weights, vw_fund_ledger 등.

### 중복 매수 현황 (A-7)
- **v4_positions** 기준: 동일 **ticker**로 여러 **desk_id**에 보유한 OPEN 포지션 **0건** (중복 매수 없음).

---

## PART B: GO100 테스트 카드 이동

### 삭제 대상 (card_id > 62)
| card_id | strategy_name | desk_id | user_id | is_active |
|--------|----------------|---------|---------|-----------|
| 63 | 제시해주신 조건들을 바탕으로... | (empty) | 3 | t |
| 64 | ㅊㅊㅊ | (empty) | 3 | t |
| 65 | E2E-TEST-CARD | (empty) | 3 | t |
| 66 | E2E-TEST | (empty) | 3 | t |
| 67 | E2E-TEST-V1-CARD | 3 | 3 | t |

(총 5건 삭제)

### 안전 확인
- **v4_positions** 참조: **0건** (card_id > 62 참조 없음).
- **v4_backtest_trades** 참조: **0건** (또는 해당 테이블/컬럼 없음).

### 실행 결과
- **삭제 전** strategy_cards: 65건.
- **삭제** 조건: `DELETE FROM strategy_cards WHERE card_id > 62` (CEO 승인 반영, 실제 PK는 `card_id` 사용).
- **삭제 후** strategy_cards: **60건**. max(card_id) = **62**.
- **go100_strategy_cards**: 6건 유지 (변동 없음).
- **v4_positions OPEN**: 5건 유지.

### 참고 (스키마)
- `strategy_cards` PK는 **card_id** (id 아님). 원본 스크립트의 `id > 62`는 `card_id > 62`로 실행함.
- 목표 "62건 복원"은 삭제 대상 3건(63,64,65) 가정 시 62건. 실제로는 card_id > 62가 5건(63~67)이라 5건 삭제 후 **60건**이 됨.

---

## DB 무결성
| 항목 | 결과 |
|------|------|
| strategy_cards | 60건 |
| v4_positions OPEN | 5건 |
| go100_strategy_cards | 6건 |

- 백업: `/tmp/backup_strategy_cards_before_cleanup_*.dump` 생성 완료.

---

## GitHub URL
- 보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/FUND-WEIGHT-CARD-MIGRATE-001-20260223.md
