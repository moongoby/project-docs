# Phase 1 — CTE 하드코딩 제거, 전략 카드 기반 전환

**Task ID**: PHASE1-CTE-CARD-PIPELINE
**Date**: 2026-03-27
**Branch**: phase-2c-command-center
**Commit**: ed6fa0ad

[인계 확인]
직전 완료: L6-DAILY-REPORT (19063db5)
현재 단계: Phase 1 — CTE 하드코딩 제거
CEO 지시 적용: D-008, D-009, D-010, D-011
strategy_cards: 7 (DESK)
open_positions: 0

---

## 구현 요약

go100_strategy_cards 테이블에 7개 신규 컬럼 추가 + 7개 DESK 전략 시드 데이터 등록.
CTE 파이프라인 코드에 `evaluate_with_card()`, `evaluate_bounce()`, trigger-tactic matrix 카드 메서드 추가.
통합엔진 `run_unified_engine.py`에 `load_active_strategy_cards()` DB 기반 카드 로딩 함수 추가.

## 검증 체크리스트

### [PASS] 구현 목표
- go100_strategy_cards에 Phase 1 스키마 확장 (card_type, stage_id, bounce_conditions, trigger_tactic, broker_config, data_requirements, metadata) + 7 DESK 전략 시드

### [PASS] 검증 방법
```sql
SELECT go100_card_id, strategy_name, card_type, card_status, stage_id,
       metadata->>'strategy_id' as sid
FROM go100_strategy_cards
WHERE card_status IN ('PAPER_LIVE','LIVE') AND stage_id >= 2 AND is_active = TRUE;
```

### [PASS] 완료 기준
- 7개 DESK 카드 반환: D2, D4, D5, D6, D7, S1, D-ORB
- 모든 카드: card_type='DESK', card_status='PAPER_LIVE', stage_id=2, is_active=TRUE
- trigger_tactic, bounce_conditions JSON 유효

### [N/A] 실패 기준
- 카드 0건 → 마이그레이션 미적용 (해당 없음 — 7건 확인)
- 스키마 컬럼 누락 → 마이그레이션 오류 (해당 없음 — 7컬럼 확인)

### [PASS] 서비스 재시작 확인
```
● go100.service — active (running)
● go100-frontend — active (running)
Backend health: {"status":"ok","version":"4.1.0"}
Frontend: 307 (redirect OK)
```

### [PASS] 에러 로그 0건
- `journalctl -u go100 --since "60s ago"` → 실제 ERROR/Traceback 0건
- (SQL 로그에 `error_message` 컬럼명 포함되나 이는 INFO 레벨 거짓 양성)

---

## 적용된 마이그레이션

| Migration | 내용 | 상태 |
|-----------|------|------|
| 074_go100_strategy_cards_phase1.sql | 7개 신규 컬럼 + 2개 인덱스 | APPLIED |
| 075_go100_strategy_cards_desk7_seed.sql | 7 DESK 전략 시드 데이터 | APPLIED |

## 코드 변경 확인

| 파일 | 메서드 | 확인 |
|------|--------|------|
| cte_pipeline.py:1091 | evaluate_with_card() | OK |
| cte_pipeline.py:1157 | load_trigger_tactic_from_card() | OK |
| bounce_gate.py:591 | evaluate_bounce() | OK |
| bounce_gate.py:703 | _eval_generic_condition() | OK |
| trigger_tactic_matrix.py:312 | get_strategy_mapping_from_card() | OK |
| trigger_tactic_matrix.py:337 | get_primary_cell_from_card() | OK |
| trigger_tactic_matrix.py:365 | is_forbidden_from_card() | OK |
| trigger_tactic_matrix.py:377 | get_match_quality_score_from_card() | OK |
| signal_generator.py:704 | _load_strategy_cards() | OK |
| run_unified_engine.py:142 | load_active_strategy_cards() | OK |
| run_unified_engine.py:1232 | evaluate_with_card() 호출부 | OK |

## DESK 전략 카드 상세

| Card ID | SID | 전략명 | PF | WR | Trigger×Tactic | Bounce Gate |
|---------|-----|--------|----|----|----------------|-------------|
| 67 | D2 | 눌림확인매매 | 2.20 | 39.8% | T4×B2, T5×C3 | D2 (min 2) |
| 68 | D4 | 상한가재테스트 | 2.43 | 28.2% | T2×B2 | D4 (min 2) |
| 69 | D5 | 뉴스갭2차파동 | 4.21 | 60.0% | T5×B2, T4×B3 | D5 (min 2) |
| 70 | D6 | 상한가갭추격EOD | 13.63 | 77.8% | T2×A2 | N/A (EOD) |
| 71 | D7 | 종가배팅EOD | 2.12 | 53.4% | T8×B4, T4×B4 | D7 (min 3) |
| 72 | S1 | 폭발거래량스윙 | 1.44 | 58.7% | T1×B2 | S1 (min 2) |
| 73 | D-ORB | 오프닝레인지 | 2.233 | 58.0% | T5×A3 | N/A |
