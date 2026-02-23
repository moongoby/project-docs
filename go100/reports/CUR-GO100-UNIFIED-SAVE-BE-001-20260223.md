# CUR-GO100-UNIFIED-SAVE-BE 보고서

**작성일:** 2026-02-23  
**작업 지시서:** CUR-GO100-UNIFIED-SAVE-BE  
**목적:** GO100 전략 저장 API 통일 + 백테스트 GO100 연동 + 경로 정리 (백엔드)

---

## 1. 백업

- **경로:** `/tmp/backup_UNIFIED_SAVE_BE_20260223_035257.dump`
- **명령:** `PGPASSWORD='...' pg_dump -h localhost -U kis_admin -d kisautotrade -F c -f /tmp/backup_UNIFIED_SAVE_BE_$(date +%Y%m%d_%H%M%S).dump`

---

## 2. STEP 1 사전 상태 요약

### DB
- **go100_strategy_cards:** 3건 (go100_card_id 13, 14, 15), user_id=3, is_featured=true
- **strategy_cards (user_id=3):** 4건 (card_id 3, 62, 63, 64)
- **strategy_cards (user_id=15, legacy naver):** 0건
- **v4_users:** user_id 1(system), 2(moongoby@gmail.com), 3(moongoby@naver.com), 4(test)
- **legacy users:** id 6=moongoby@gmail.com, id 15=moongoby@naver.com 등
- **go100_strategy_cards 컬럼:** go100_card_id, user_id, account_id, strategy_name, strategy_type, universe_filter, entry_rules, exit_rules, risk_params, strategy_params, allocated_amount, max_stocks, card_status, is_active, is_live, source_type, source_store_card_id, source_user_id, llm_session_id, last_backtest_*, paper_*, disclaimer_*, dedicated_account, created_at, updated_at, is_featured, is_public, featured_order
- **go100_backtest_runs:** 0건

### 코드
- POST /api/go100/strategy-cards: 기존 구현 있음 (go100_strategy_card_service.create_card)
- for-backtest: GET /api/v1/strategy-cards/for-backtest → strategy_card_service.list_cards_for_backtest (기존 strategy_cards만 조회)
- GO100 backtest run: POST /api/go100/backtest/run 이미 존재 (Go100BacktestRequest.go100_card_id)

---

## 3. 수정/생성 파일 목록 및 변경 요약

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/go100/user_utils.py` | **신규.** get_effective_uid(db, jwt_user_id), get_user_email(db, user_id). legacy users.id ↔ v4_users.user_id 매핑 |
| `backend/app/services/go100/strategy/card_service.py` | create_card에서 get_effective_uid 사용, INSERT 시 user_id=effective_uid. buy_conditions/sell_conditions/risk_management/indicators/parameters/stock_codes 별칭 매핑. strategy_type DB 저장. get_card/list_cards/update_card/transition_status/delete_card/subscribe_from_store에서 effective_uid 사용 |
| `backend/app/services/go100/strategy/schemas.py` | Go100StrategyCardCreate에 strategy_type, buy_conditions, sell_conditions, risk_management, indicators, parameters, stock_codes 추가 |
| `backend/app/routers/go100/strategy_router.py` | 헤더 코멘트 CUR-GO100-UNIFIED-SAVE-BE 추가 (POST /strategy-cards 기존 유지) |
| `backend/app/services/go100/ai/base_orchestrator.py` | get_effective_uid import. _auto_strategy_name() 추가 (키워드/전략유형 기반 자동 전략명). _insert_draft_card에서 effective_uid 사용, intent 전달, 자동 전략명 적용. 완료 시 reply에 "전략카드 '{이름}'이(가) 저장되었습니다. 내 전략 탭에서 확인하세요." 추가. OrchestrationResult에 go100_card_id=card_id 설정 |
| `backend/app/services/go100/ai/schemas.py` | OrchestrationResult에 go100_card_id: Optional[int] = None 추가 |
| `backend/app/routers/go100/ai_router.py` | 헤더 코멘트 CUR-GO100-UNIFIED-SAVE-BE 추가 |
| `backend/app/services/strategy_card_service.py` | list_cards_for_backtest: strategy_cards 조회 후 go100_strategy_cards 조회 병합. GO100 행은 StrategyCardResponse(card_id=go100_card_id, account_id=0, source="go100", go100_card_id=id) |
| `backend/app/schemas/strategy_card_schemas.py` | StrategyCardResponse에 source: Optional[str]=None, go100_card_id: Optional[int]=None 추가 (for-backtest 구분용) |
| `backend/app/api/v1/strategy_cards_router.py` | 헤더 코멘트 CUR-GO100-UNIFIED-SAVE-BE 추가 |
| `backend/tests/test_go100_card_service.py` | test_store_subscribe_creates_copy, test_update_card_live_restriction에 get_effective_uid patch 추가 |

---

## 4. effective_uid 유틸리티

- **생성:** `backend/app/services/go100/user_utils.py`
- **함수:** `get_effective_uid(db, jwt_user_id)` → v4_users.user_id 반환 (레거시 users.id면 email로 매핑)
- **사용처:** go100 strategy card_service (create_card, get_card, list_cards, update_card, transition_status, delete_card, subscribe_from_store), base_orchestrator._insert_draft_card

---

## 5. 전략 저장 API

- **엔드포인트:** POST /api/go100/strategy-cards (기존 유지)
- **변경:** create_card 시 JWT user_id를 get_effective_uid로 변환하여 저장. 요청 body에 strategy_type, buy_conditions, sell_conditions, risk_management, indicators, parameters, stock_codes 지원 (entry_rules/exit_rules/risk_params/universe_filter에 매핑).

---

## 6. AI 오케스트레이터

- **자동 전략명:** _auto_strategy_name(design_dict, intent) — intent.target_sectors/target_keywords, risk_params.strategy_type 기반 "GO100 AI - {섹터} {스캘핑|데일리|스윙} 전략" 형식.
- **저장:** _insert_draft_card에서 effective_uid 사용, 자동 전략명 적용.
- **응답:** OrchestrationResult에 go100_card_id 포함, reply_to_user 끝에 저장 안내 문구 추가.

---

## 7. 백테스트 연동

- **for-backtest:** GET /api/v1/strategy-cards/for-backtest 시 strategy_cards + go100_strategy_cards 병합. GO100 카드는 source="go100", go100_card_id 설정. 프론트에서 source가 "go100"이면 POST /api/go100/backtest/run에 go100_card_id로 호출 가능.
- **GO100 백테스트 실행:** POST /api/go100/backtest/run 기존 유지 (Go100BacktestRequest.go100_card_id, start_date, end_date, initial_capital 등).

---

## 8. V4.1 호환성

- POST /api/v1/strategy-cards: 변경 없음 (V4.1 strategy_cards INSERT 유지).
- GET /api/v1/strategy-cards/catalog?tab=v4: list_v4_cards_with_system 호출, strategy_cards + strategies + go100 병합 로직 유지.
- strategy_cards 테이블 구조 변경 없음. go100_* 테이블만 사용.

---

## 9. pytest 결과

- **실행:** `cd /root/kis-autotrade-v4 && .venv/bin/python -m pytest backend/tests/ -v --tb=short`
- **요약:** 183 passed, 9 failed (실패는 LLM/외부 API·universe 이벤트 루프 등 기존 이슈, 본 작업과 무관).
- **GO100 카드 서비스:** test_store_subscribe_creates_copy, test_update_card_live_restriction 포함 통과 (get_effective_uid 패치 적용).

---

## 10. API 검증 (STEP 7-3)

- **서비스:** `sudo systemctl restart go100` 후 `curl -s http://localhost:8002/health` → status ok, database/redis connected.
- **인증 필요 API:** 로그인 후 토큰으로 아래 확인 권장.
  - GET /api/v1/strategy-cards/catalog?tab=all → featured GO100 카드
  - GET /api/v1/strategy-cards/catalog?tab=my → 내 GO100 카드 (effective_uid 기준)
  - GET /api/go100/strategy-cards → 내 GO100 카드 목록
  - GET /api/v1/strategy-cards/for-backtest → V4 + GO100 카드 병합 (source, go100_card_id 포함)
  - POST /api/go100/strategy-cards → body에 strategy_name, strategy_type, buy_conditions 등으로 저장 후 go100_card_id 반환

---

## 11. 컴플라이언스 체크리스트

- [x] go100_* 파일/테이블만 수정 (V4.1 strategy_cards 구조 변경 없음)
- [x] .env/.bak 미커밋
- [x] 수정 파일 상단 헤더 코멘트 # CUR-GO100-UNIFIED-SAVE-BE, 2026-02-23
- [x] V4.1 기능 영향 없음 (catalog tab=v4, POST /api/v1/strategy-cards 유지)
- [ ] 테스트 전략카드 삭제: API로 저장한 테스트 카드는 수동 삭제 권장 (DELETE /api/go100/strategy-cards/{id})

---

## 12. 커밋

- **메시지:** `feat: CUR-GO100-UNIFIED-SAVE-BE - 전략저장 go100 통일 + 백테스트 연동 + AI 자동 전략명`
- **해시:** `d34fb1d5`

---

## 13. 롤백 절차

```bash
sudo systemctl stop go100
cd /root/kis-autotrade-v4
git revert HEAD --no-edit
PGPASSWORD='KisAuto2026!Secure' pg_restore -h localhost -U kis_admin -d kisautotrade --clean --if-exists /tmp/backup_UNIFIED_SAVE_BE_20260223_035257.dump
sudo systemctl start go100
curl -s http://localhost:8002/health
```
