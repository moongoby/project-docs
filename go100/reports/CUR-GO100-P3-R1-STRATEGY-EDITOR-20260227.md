# CUR-GO100-P3-R1-STRATEGY-EDITOR-20260227

**작업일**: 2026-02-27  
**목표**: P3-R1 AI 대화형 전략 편집 플로우 — 사용자가 자연어로 기존 전략카드 조건을 수정하는 2단계(미리보기 → 확인 적용) 구현

---

## 1. 요약

- **DB**: `go100_strategy_edit_history` 테이블 추가 (마이그레이션 038)
- **서비스**: `backend/app/services/go100/strategy_editor_agent.py` 구현
  - `parse_edit_instruction(instruction, current_rules)`: LLM(Tier 2 Claude Sonnet, DESIGN_CHAT) 호출로 수정된 JSON 반환, `field_changed` 및 유효성 검증
  - `apply_edit(db, card_id, instruction, user_id)`: 전략카드 로드 → parse → 이력 INSERT(approved=False) → 미리보기(diff_summary, edit_id) 반환
  - `confirm_strategy_edit(db, edit_id, user_id)`: 해당 이력 approved=True 후 카드 UPDATE
  - `get_edit_diff(before_rules, after_rules, field_changed)`: before/after 비교 텍스트 생성
- **Agent 도구**: `edit_strategy_card`, `confirm_strategy_edit`, `get_strategy_edit_history` 등록 (tool_executors + agent_tools)
- **인텐트**: `strategy_edit` 추가 (intent_router 키워드, C2SC 25개 인텐트, ai_router 키워드 폴백)
- **Agent Core**: 전략 편집 도구 안내 및 `execute_tool`에 `context={"user_id": user_id}` 전달로 편집/확인 시 본인 카드만 처리

---

## 2. DB 스키마

**파일**: `backend/migrations/038_go100_strategy_edit_history.sql`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| edit_id | SERIAL PK | 자동 증가 ID |
| strategy_card_id | BIGINT NOT NULL | 전략카드 ID |
| user_id | INTEGER NOT NULL | 사용자 ID |
| edit_instruction | TEXT NOT NULL | 사용자 자연어 지시 |
| before_rules | JSONB NOT NULL | 변경 전 해당 섹션(entry_rules/exit_rules/risk_params) |
| after_rules | JSONB NOT NULL | 변경 후 해당 섹션 |
| field_changed | VARCHAR(50) NOT NULL | 'entry_rules' \| 'exit_rules' \| 'risk_params' |
| approved | BOOLEAN DEFAULT FALSE | 확인 전 false, 확인 후 true |
| created_at | TIMESTAMPTZ | |

인덱스: `idx_edit_history_card`, `idx_edit_history_user`, `idx_edit_history_approved` (WHERE approved = FALSE)

---

## 3. 서비스 동작

### 3.1 parse_edit_instruction(instruction, current_rules)

- LLMGateway DESIGN_CHAT(Claude Sonnet) 호출.
- 시스템 프롬프트: 전략카드 편집 전문가, 현재 규칙 JSON + 사용자 지시 → `{"field_changed": "entry_rules"|"exit_rules"|"risk_params", "rules": <수정된 JSON>}` 만 반환.
- 응답 파싱 후 `field_changed` 및 `rules` 유효성 검증(배열/객체 등).

### 3.2 apply_edit(db, card_id, instruction, user_id)

- Go100StrategyCardService.get_card로 카드 조회(NotFoundException → ValueError).
- parse_edit_instruction로 수정 규칙 생성.
- `go100_strategy_edit_history`에 before_rules/after_rules/field_changed, approved=FALSE 로 INSERT.
- 반환: edit_id, strategy_card_id, strategy_name, field_changed, diff_summary, after_rules, message(confirm_strategy_edit 안내).

### 3.3 confirm_strategy_edit(db, edit_id, user_id)

- 해당 edit_id + user_id 로 이력 조회, approved면 이미 적용 메시지 반환.
- go100_strategy_cards 해당 카드의 field_changed 컬럼을 after_rules로 UPDATE.
- go100_strategy_edit_history.approved = TRUE 후 커밋.

### 3.4 get_edit_diff(before_rules, after_rules, field_changed)

- entry_rules/exit_rules: 리스트 항목별/키별 diff 라인 생성.
- risk_params: 키별 diff.
- 예: `entry_rules[0].params.fast: 5 → 10`

---

## 4. Agent 도구

| 도구 | 설명 |
|------|------|
| edit_strategy_card | 자연어 지시로 전략카드 수정(확인 전 미리보기 반환). card_id, instruction 필수. |
| confirm_strategy_edit | 수정 미리보기 확인 후 전략카드에 반영. edit_id 필수. |
| get_strategy_edit_history | 전략카드 수정 이력 조회. card_id(선택), limit. |

- **agent_tools.py**: 위 3개 도구 정의 및 파라미터 추가.
- **tool_executors.py**: edit_strategy_card/confirm_strategy_edit는 AsyncSessionLocal + strategy_editor_agent 비동기 실행(스레드 풀), get_strategy_edit_history는 psycopg2 동기.
- **agent_core.py**: SYSTEM_PROMPT에 전략 편집 도구 안내 추가, execute_tool 호출 시 context={"user_id": user_id} 전달.

---

## 5. 인텐트 연동

- **intent_router.py**: STRATEGY_EDIT_KEYWORDS 추가(바꿔줘, 수정, 손절, 익절, 골든크로스 기간, 카드, 적용해줘 등). stock_screening 다음 우선순위로 strategy_edit 반환.
- **ai_router.py**: C2SC_VALID_INTENTS에 "strategy_edit" 추가, _C2SC_BASE_PROMPT 인텐트 목록에 "strategy_edit - 기존 전략카드 조건 수정" 예시 추가, _keyword_classify용 _KEYWORDS에 strategy_edit 추가.
- strategy_edit 인텐트는 별도 전용 핸들러 없이 기존 Agent Core로 fall-through → LLM이 edit_strategy_card / confirm_strategy_edit / get_strategy_edit_history 호출.

---

## 6. 테스트 결과

| 항목 | 결과 |
|------|------|
| 마이그레이션 038 실행 | 성공 (CREATE TABLE, INDEX 3개, COMMENT) |
| edit_strategy_card(35, "") | 빈 지시 시 "편집 지시가 비어 있습니다." 반환 |
| edit_strategy_card(99999, "손절 -5%") | 존재하지 않는 카드 시 "전략 카드 #99999를 찾을 수 없거나 접근 권한이 없습니다." 반환 |
| get_strategy_edit_history(card_id=35, limit=5) | 정상 반환 (history: [], count: 0) |
| execute_tool(..., context={"user_id": 3}) | context 병합 동작 확인 |

(실제 LLM을 이용한 "골든크로스 5/20을 10/30으로 변경" → 미리보기 → confirm 적용은 API 키 설정 환경에서 수동 검증 권장.)

---

## 7. 체크리스트

- [x] 코드 레포 반영 (마이그레이션 038, strategy_editor_agent, 도구 3개, intent_router, ai_router, agent_core)
- [x] project-docs 보고서 push (본 문서)

---

## 8. 참고 파일

- `backend/migrations/038_go100_strategy_edit_history.sql`
- `backend/app/services/go100/strategy_editor_agent.py`
- `backend/app/services/go100/ai/tool_executors.py` (edit_strategy_card, confirm_strategy_edit, get_strategy_edit_history)
- `backend/app/services/go100/ai/agent_tools.py` (전략 편집 도구 정의)
- `backend/app/services/go100/ai/agent_core.py` (SYSTEM_PROMPT, execute_tool context)
- `backend/app/services/go100/ai/intent_router.py` (STRATEGY_EDIT_KEYWORDS)
- `backend/app/routers/go100/ai_router.py` (C2SC_VALID_INTENTS, _C2SC_BASE_PROMPT, _KEYWORDS)
