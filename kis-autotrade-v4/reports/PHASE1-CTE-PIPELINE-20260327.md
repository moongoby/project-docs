# Phase 1 — CTE 하드코딩 제거, 전략 카드 기반 전환 RESULT

**Date:** 2026-03-27
**Task-ID:** PHASE1-CTE-PIPELINE
**Branch:** phase-2c-command-center

[인계 확인]
직전 완료: L6-DAILY-REPORT (19063db5)
현재 단계: Phase 1 — Unified Pipeline Master Plan
CEO 지시 적용: D-009 (3-layer pyramid), D-010 (DESK2 multi-condition), D-011 (signal matching)
strategy_cards: 60 + 7 DESK = 67 active
open_positions: 0

---

## 구현 요약

CTE 파이프라인의 하드코딩된 전략 매핑을 DB 기반 전략 카드(go100_strategy_cards)로 전환.
7개 DESK 전략(D2/D4/D5/D6/D7/S1/D-ORB)을 bounce_conditions, trigger_tactic JSON과 함께 등록.

### 변경 파일

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/trading/cte/cte_pipeline.py` | `evaluate_with_card()`, `load_trigger_tactic_from_card()` 추가 |
| `backend/app/services/trading/cte/bounce_gate.py` | `evaluate_bounce()` 범용 메서드 추가 |
| `backend/app/services/unified_engine/core/signal_generator.py` | `_load_strategy_cards()` DB 로드 + pool 주입 |
| `scripts/run_unified_engine.py` | `load_active_strategy_cards()` 함수 + `simulate_day_neutral(conn)` 카드 기반 전환 |
| `backend/migrations/074_go100_strategy_cards_phase1.sql` | 7개 JSONB 컬럼 + 2개 인덱스 추가 |
| `backend/migrations/075_go100_strategy_cards_desk7_seed.sql` | 7개 DESK 카드 시드 데이터 |

### DB 스키마 변경 (Migration 074)

| 컬럼 | 타입 | 용도 |
|------|------|------|
| card_type | VARCHAR(20) | DESK/HYPOTHESIS/MANUAL/IMPORTED |
| stage_id | INTEGER(1-4) | 1=BT, 2=가상매매, 3=모의계좌, 4=실계좌 |
| bounce_conditions | JSONB | 반등확인 게이트 조건 |
| trigger_tactic | JSONB | 트리거×전술 매핑 |
| broker_config | JSONB | 증권사별 설정 |
| data_requirements | JSONB | 필요 데이터 소스 |
| metadata | JSONB | 전략ID, PF, 승률 등 메타정보 |

### DESK 카드 등록 현황 (Migration 075)

| Card ID | Strategy | PF | Win Rate | Trigger×Tactic |
|---------|----------|-----|----------|----------------|
| 67 | DESK_D2_눌림확인매매 | 2.20 | 39.8% | T4×B2, T5×C3 |
| 68 | DESK_D4_상한가재테스트 | 2.43 | 28.2% | T2×B2 |
| 69 | DESK_D5_뉴스갭2차파동 | 4.21 | 60.0% | T5×B2, T4×B3 |
| 70 | DESK_D6_상한가갭추격EOD | 13.63 | 77.8% | T2×A2 |
| 71 | DESK_D7_종가배팅EOD | 2.12 | 53.4% | T8×B4, T4×B4 |
| 72 | DESK_S1_폭발거래량스윙 | 1.44 | 58.7% | T1×B2 |
| 73 | DESK_D_ORB_오프닝레인지 | 2.233 | 58.0% | T5×A3 |

---

## 검증 체크리스트

- [x] 구현 목표: CTE 파이프라인 하드코딩 제거, go100_strategy_cards 기반 전략 카드 전환
- [x] 검증 방법:
  - DB: `SELECT * FROM go100_strategy_cards WHERE card_type='DESK'` → 7행
  - Python: `CTEPipeline.evaluate_with_card()`, `load_trigger_tactic_from_card()` 존재 확인
  - Health: `curl http://localhost:8002/health` → `{"status":"ok"}`
- [x] 완료 기준: 7개 DESK 카드 등록, evaluate_with_card 메서드 동작, 서비스 정상 기동
- [x] 실패 기준: DESK 카드 0개, 서비스 기동 실패, ERROR 로그 발생
- [x] 서비스 재시작 확인: `systemctl status go100` → active (running) since 2026-03-27 16:42:56 KST
- [x] 에러 로그 0건: `journalctl -u go100 --since "60s ago" | grep "| ERROR"` → 0건

### 상세 검증 결과

```
# DB 검증
go100_card_id | strategy_name           | card_type | card_status | stage_id | tt_count | gate_type
67            | DESK_D2_눌림확인매매    | DESK      | PAPER_LIVE  | 2        | 2        | D2
68            | DESK_D4_상한가재테스트  | DESK      | PAPER_LIVE  | 2        | 1        | D4
69            | DESK_D5_뉴스갭2차파동   | DESK      | PAPER_LIVE  | 2        | 2        | D5
70            | DESK_D6_상한가갭추격EOD | DESK      | PAPER_LIVE  | 2        | 1        | (EOD)
71            | DESK_D7_종가배팅EOD     | DESK      | PAPER_LIVE  | 2        | 2        | D7
72            | DESK_S1_폭발거래량스윙  | DESK      | PAPER_LIVE  | 2        | 1        | S1
73            | DESK_D_ORB_오프닝레인지 | DESK      | PAPER_LIVE  | 2        | 1        | (ORB)

# Health 검증
{"status":"ok","version":"4.1.0","orchestrator_state":"PRE_MARKET","database":"connected","redis":"connected"}
Frontend HTTP: 307 (redirect to auth → OK)

# Code 검증
CTEPipeline.evaluate_with_card: OK
CTEPipeline.load_trigger_tactic_from_card: OK
BounceConfirmationGate.evaluate_bounce: OK
SignalGenerator._load_strategy_cards: OK (898 chars)
SignalGenerator.__init__ pool injection: OK
run_unified_engine.load_active_strategy_cards: OK
```

---

## 아키텍처 변경점

### Before (하드코딩)
```
trigger_tactic_matrix.py STRATEGY_CTE_MAPPING
  → "D2": [(T4, B2), (T5, C3)]  # 코드에 고정
  → cte_pipeline.evaluate(signal)  # 전략별 분기
```

### After (카드 기반)
```
go100_strategy_cards (DB)
  → load_active_strategy_cards() / _load_strategy_cards()
  → cte_pipeline.evaluate_with_card(signal, card)
    ├─ card['trigger_tactic'] → trigger/tactic 주입
    ├─ card['bounce_conditions'] → bounce gate 주입
    └─ evaluate() (기존 5-layer 파이프라인 동일)
```

### Fallback
- DB 미연결 또는 card 미등록 시 → 기존 STRATEGY_CTE_MAPPING 하드코딩 유지 (안전)

---

## 다음 단계 (Phase 2)

1. evaluate_bounce() 범용화 완성 (현재 D2~D7+S1별 check_*_gate() → 카드 조건 기반)
2. Commander Gate (L3.4) 활성화
3. 가설 카드(HYPOTHESIS) → DESK 승격 파이프라인
4. Stage 2→3→4 자동 승격 로직
