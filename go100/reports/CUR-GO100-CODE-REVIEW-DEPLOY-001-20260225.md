# CUR-GO100-CODE-REVIEW-DEPLOY-001 — 코드 검수 + 배포 보고서

**작성:** 2026-02-25 KST  
**작업 ID:** CUR-GO100-CODE-REVIEW-DEPLOY-001  
**우선순위:** P0

---

## 1. 검수 결과 요약

### Phase 1 — 백엔드 (5개 파일)

| 파일 | 결과 | 비고 |
|------|------|------|
| goal_engine.py | 통과 | CUR-GO100-GOAL-PIPELINE-001 헤더 있음. _strategy_allocation_by_cagr CAGR 구간별 weight_pct 합계 100%. generate_plan_phases_with_strategies phase_a/phase_b 구조 정상. generate_strategy_intents UserIntent 호환 dict 반환. create_goal required_cagr 시 plan_phases 생성. update_goal allowed 필드만 UPDATE. calculate_required_cagr, classify_risk_appetite, run_monte_carlo 유지. |
| base_orchestrator.py | 통과 | _compute_params_hash: entry_rules, exit_rules, risk_params, universe_filter sort_keys JSON → MD5 12자. _run_backtest WHERE (params_hash IS NULL OR params_hash = :params_hash). run_from_intent → design_agent.design, _run_full_pipeline 시그니처 일치. process_message 로직 유지. |
| prompts.py | 통과 | GOAL_CONTEXT_SECTION, GOAL_REPLY_SECTION 존재. DESIGN_SYSTEM_PROMPT·REPLY_SYSTEM_PROMPT 끝에 부착 확인. |
| ai_router.py | 수정 반영 | openai import 없음. handle_goal_setup 1턴/2턴 분기 정상. 1턴: _generate_three_scenarios, Redis goal_pending TTL 30분, data parsed_goal/required_cagr/scenarios. 2턴: _parse_scenario_selection, create_goal → generate_strategy_intents → run_from_intent. user_id는 current_user["user_id"] 사용(카드 INSERT 시 오케스트레이터에서 get_effective_uid 사용). _format_money 억/만원 포맷. **수정:** current_phase를 integer 컬럼 대응으로 1 사용, created_cards 리스트 구문 수정, Redis fallback 로깅. |
| backtest_service.py | 통과 | _compute_params_hash base_orchestrator와 동일 로직. create_backtest_run INSERT 시 params_hash 컬럼 포함. |

### Phase 2 — 프론트엔드 (3개 파일)

| 파일 | 결과 | 비고 |
|------|------|------|
| GoalScenarioCards.tsx | 통과 | 시나리오 3개 카드(CAGR, 예상금액, 리스크, 성공확률). onSelect → name 전송. GoalScenario 타입. sm:grid-cols-3 반응형. |
| GoalStrategyResult.tsx | 통과 | 생성 전략 카드 목록, /go100/strategies/{card_id} 링크. GoalCreatedCard 타입. (백테스트 요약은 created_cards[].backtest 있으나 UI에는 미표시 — 선택 사항) |
| ChatWidget.tsx | 통과 | Msg에 data?: GoalChatData. sendMessage(overrideText?). 응답 시 data 저장. assistant 하단 GoalScenarioCards(m.data?.scenarios), GoalStrategyResult(m.data?.created_cards). 시나리오 클릭 시 sendMessage(name). 기존 채팅 유지. |

---

## 2. 수정 사항

- **ai_router.py**
  - `update_goal(..., "current_phase": "phase_a")` → `"current_phase": 1` (go100_goals.current_phase가 integer인 경우 대비).
  - `created_cards` LLM 응답 생성 시 리스트 컴프리헨션 구문 수정: `[{"name": c["name"], "card_id": c["card_id"]} for c in created_cards]`.
  - Redis goal_pending 실패 시 conversation_history에서 복원하도록 fallback 및 로깅 보강.
- **커밋:** `fix: CUR-GO100-CODE-REVIEW-DEPLOY-001 - current_phase integer(1), created_cards list fix, Redis fallback` (f317cef9).

---

## 3. 마이그레이션 결과

- **실행 환경:** 코드 검수/빌드는 워크스페이스에서 수행. DB/서비스는 **서버 211.188.51.113**에서 실행 필요.
- **로컬 psql:** Peer authentication 실패로 접속 불가 → **서버에서 아래 명령 실행 필요.**

```bash
# params_hash 컬럼 추가
PGPASSWORD='KisAuto2026!Secure' psql -U kis_admin -d kisautotrade -c "
ALTER TABLE go100_backtest_runs ADD COLUMN IF NOT EXISTS params_hash VARCHAR(12);"

# 확인
PGPASSWORD='KisAuto2026!Secure' psql -U kis_admin -d kisautotrade -c "\d go100_backtest_runs" | grep params_hash

# current_phase 타입 확인
PGPASSWORD='KisAuto2026!Secure' psql -U kis_admin -d kisautotrade -c "
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name='go100_goals' AND column_name='current_phase';"
```

- **current_phase:** 코드상 2턴 완료 시 `update_goal(..., current_phase=1)` 사용으로 integer 컬럼에 대응 완료.

---

## 4. 배포 결과

- **백업:** `/root/backup/code-review-deploy-20260225-103411` (소스 goal/ai/backtest/routers/frontend-go100 복사 완료). DB 데이터 백업은 **서버에서** `pg_dump -t 'go100_*' --data-only` 실행 권장.
- **코드:** branch `phase-2c-command-center`, 최신 pull 후 위 수정 커밋 반영.
- **프론트엔드 빌드:** `npm run build` 성공 (exit_code 0).
- **서비스 재시작:** **서버 211.188.51.113**에서 실행 필요.  
  `systemctl restart go100` → `systemctl restart go100-frontend` (★ kis-v41-* 재시작 금지).
- **헬스체크:** 서버에서  
  `curl -s http://localhost:8002/api/go100/health | python3 -m json.tool`  
  `curl -s http://localhost:3000 | head -5`

---

## 5. E2E 테스트 결과

- **실행 위치:** 서버에서 JWT 로그인 후 1턴/2턴 API 호출 및 DB 조회 필요.
- **1턴:** `POST /api/go100/ai/chat` — message "5천만원으로 3년 안에 3억 만들고 싶어" → `status: "awaiting_selection"`, `data.scenarios` 3개, `data.required_cagr` 약 82%.
- **2턴:** message "공격적" + conversation_history에 1턴 포함 → `data.strategy_card_ids`, `data.goal_id`, `data.created_cards` 확인.
- **DB 확인:** `go100_goals` 최신 3건, `go100_strategy_cards` 최신 5건, `go100_backtest_runs` 최신 5건.

---

## 6. 규칙 준수

- kis-v41-* 서비스 재시작: **하지 않음**
- 실계좌(account_id 5,6) 사용: **하지 않음**
- 백업: **소스 백업 완료** (DB 백업은 서버에서 실행 권장)
- go100_ 접두어 파일/테이블만 수정: **확인**
- 헤더 주석 규칙: **확인**
- pre-commit-check.sh: **통과**
- 보고서 저장: `/root/project-docs/go100/reports/CUR-GO100-CODE-REVIEW-DEPLOY-001-20260225.md`
- 보고서 GitHub push: **다음 단계에서 실행**
