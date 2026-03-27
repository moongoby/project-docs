# Phase 1 — CTE 하드코딩 제거, 전략 카드 기반 전환 RESULT

[인계 확인]
직전 완료: ed6fa0ad feat(unified): Phase 1 — CTE 하드코딩 제거, 전략 카드 기반 전환
현재 단계: Phase 1 완료 (CTE Pipeline → Strategy Card 기반 전환)
CEO 지시 적용: D-009, D-010, D-011
strategy_cards: 7 DESK cards (67-73)
open_positions: N/A (PAPER_LIVE stage)

## 구현 요약

커밋 `ed6fa0ad` (2026-03-27 16:15)에서 Phase 1 전체 구현 완료.

### 변경 파일 (7개, +1,150 lines)
| 파일 | 변경 내용 |
|------|-----------|
| `cte_pipeline.py` | `evaluate_with_card()`, `load_trigger_tactic_from_card()` 추가 |
| `bounce_gate.py` | `evaluate_bounce()` 제네릭 메서드 (gate_type 기반 디스패치) |
| `trigger_tactic_matrix.py` | 4개 카드 기반 메서드 (`get_strategy_mapping_from_card` 등) |
| `signal_generator.py` | `_load_strategy_cards()` async DB 로드 |
| `run_unified_engine.py` | 카드 기반 전략 우선순위 + fallback |
| `074_go100_strategy_cards_phase1.sql` | 스키마 확장 (7 columns) |
| `075_go100_strategy_cards_desk7_seed.sql` | DESK 7전략 시드 데이터 |

### DB 시드 데이터 (7 DESK 전략)
| card_id | 전략명 | card_status | stage_id | trigger_tactic | bounce_conditions | metadata |
|---------|--------|-------------|----------|---------------|------------------|----------|
| 67 | DESK_D2_눌림확인매매 | PAPER_LIVE | 2 | ✓ | ✓ | ✓ |
| 68 | DESK_D4_상한가재테스트 | PAPER_LIVE | 2 | ✓ | ✓ | ✓ |
| 69 | DESK_D5_뉴스갭2차파동 | PAPER_LIVE | 2 | ✓ | ✓ | ✓ |
| 70 | DESK_D6_상한가갭추격EOD | PAPER_LIVE | 2 | ✓ | ✓ | ✓ |
| 71 | DESK_D7_종가배팅EOD | PAPER_LIVE | 2 | ✓ | ✓ | ✓ |
| 72 | DESK_S1_폭발거래량스윙 | PAPER_LIVE | 2 | ✓ | ✓ | ✓ |
| 73 | DESK_D_ORB_오프닝레인지 | PAPER_LIVE | 2 | ✓ | ✓ | ✓ |

---

## 검증 체크리스트

### ✅ 구현 목표
CTE 파이프라인의 하드코딩된 전략 매핑을 go100_strategy_cards 테이블 기반으로 전환

### ✅ 검증 방법
```bash
# 1. Python import 검증
python3 -c "
import sys; sys.path.insert(0, 'backend')
from app.services.trading.cte.cte_pipeline import CTEPipeline
p = CTEPipeline()
assert hasattr(p, 'evaluate_with_card')
assert hasattr(p, 'load_trigger_tactic_from_card')
print('OK')
"

# 2. DB 시드 데이터 검증
psql -h localhost -U kis_admin -d kisautotrade -c \
  "SELECT count(*) FROM go100_strategy_cards WHERE card_type='DESK' AND card_status='PAPER_LIVE' AND stage_id=2 AND trigger_tactic IS NOT NULL;"

# 3. 서비스 상태
systemctl is-active go100 go100-frontend
curl -s http://localhost:8002/health
```

### ✅ 완료 기준
- [x] CTEPipeline.evaluate_with_card() 메서드 존재 및 import 성공
- [x] BounceConfirmationGate.evaluate_bounce() 제네릭 메서드 존재
- [x] TriggerTacticMatrix 4개 카드 기반 메서드 존재
- [x] SignalGenerator._load_strategy_cards() async 로드 메서드 존재
- [x] go100_strategy_cards 테이블에 7개 Phase 1 columns 추가됨
- [x] 7개 DESK 전략 시드 데이터 (trigger_tactic, bounce_conditions, metadata 모두 채워짐)
- [x] 기존 하드코딩 로직 fallback 보존

### ✅ 실패 기준 (해당 없음)
- [ ] ~~evaluate_with_card import 실패~~ → PASS
- [ ] ~~DESK 시드 데이터 0건~~ → 7건 확인
- [ ] ~~서비스 시작 실패~~ → 두 서비스 모두 active

### ✅ 서비스 재시작 확인
```
systemctl is-active go100 → active
systemctl is-active go100-frontend → active
Backend: http://localhost:8002/health → {"status":"ok","version":"4.1.0","orchestrator_state":"IDLE","database":"connected","redis":"connected"}
Frontend: http://localhost:3000/go100 → 307 (redirect to login, normal)
```

### ✅ 에러 로그 0건
```
journalctl -u go100 --since "60s ago" | grep -i error → 0건
journalctl -u go100-frontend --since "60s ago" | grep -i error → 0건
```

### ✅ 라이브 DB 검증 (2026-03-27 16:40 KST)
```
=== DESK Strategy Cards ===
  ID=67 | DESK_D2_눌림확인매매 | type=DESK | status=PAPER_LIVE | stage=2 | trigger=True | bounce=True
  ID=68 | DESK_D4_상한가재테스트 | type=DESK | status=PAPER_LIVE | stage=2 | trigger=True | bounce=True
  ID=69 | DESK_D5_뉴스갭2차파동 | type=DESK | status=PAPER_LIVE | stage=2 | trigger=True | bounce=True
  ID=70 | DESK_D6_상한가갭추격EOD | type=DESK | status=PAPER_LIVE | stage=2 | trigger=True | bounce=True
  ID=71 | DESK_D7_종가배팅EOD | type=DESK | status=PAPER_LIVE | stage=2 | trigger=True | bounce=True
  ID=72 | DESK_S1_폭발거래량스윙 | type=DESK | status=PAPER_LIVE | stage=2 | trigger=True | bounce=True
  ID=73 | DESK_D_ORB_오프닝레인지 | type=DESK | status=PAPER_LIVE | stage=2 | trigger=True | bounce=True
Total cards: 61
```

### ✅ Python Import 검증 (2026-03-27 16:40 KST)
```
CTEPipeline import OK — evaluate_with_card() method present
BounceConfirmationGate import OK — evaluate_bounce() method present
TriggerTacticMatrix import OK — 4 card-based methods present
SignalGenerator import OK — _load_strategy_cards() method present
```

---

## 아키텍처 요약

```
go100_strategy_cards (DB)
  ├── trigger_tactic (JSONB) → TriggerTacticMatrix.get_*_from_card()
  ├── bounce_conditions (JSONB) → BounceConfirmationGate.evaluate_bounce()
  └── metadata (JSONB) → run_unified_engine.strategy_cards_to_priority_order()
                           ↓
CTEPipeline.evaluate_with_card(signal, strategy_card)
  → load_trigger_tactic_from_card(card) → signal.trigger/tactic 주입
  → evaluate(signal) → 기존 L1~L5 파이프라인 실행
  → PipelineResult (strategy_card_id, card_type 포함)
```

Fallback: 카드 로드 실패 시 기존 하드코딩 PRIORITY_ORDER 사용.
