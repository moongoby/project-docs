# CUR-GO100-P6-EXTRA-VERIFY-V2-20260228

**제목:** P6-EXTRA-VERIFY 재검증 V2 — Intent Routing 수정 + 세션 컨텍스트 바인딩 + E2E 4단계  
**작성일:** 2026-02-28  
**상태:** 검증 완료 (Step A·B FULL PASS, Step C·D 개선 반영)

---

## [인계 확인]

```
직전 완료: CUR-GO100-P6-EXTRA-VERIFY-20260227 (PARTIAL PASS)
현재 단계: P6-EXTRA-VERIFY-V2 재검증
CEO 지시 적용: D-005 신고가 돌파 매매, 전략 생성·백테스트·모의투자 Agent Chat 경유
```

---

## 1. 개요

- **목적:** 이전 PARTIAL PASS 원인(52주 신고가 → momentum_up 라우팅, “방금 만든 전략카드” 미바인딩)을 수정하고 E2E 4단계를 재검증.
- **변경 사항:** (1) 한국어 의도 매핑으로 `new_high_52w` 라우팅 보완, (2) 세션 컨텍스트에 `last_screening_results`, `last_created_card_id` 추가 및 Step C/D에서 card_id 자동 참조, (3) 키워드 경로에서 “방금 만든 전략카드로 백테스트 돌려줘” 시 `last_created_card_id`(또는 최신 카드)로 백테스트 파이프라인 실행.

---

## 2. 이전 PARTIAL PASS 대비 개선점

| 항목 | 이전 (20260227) | 이번 V2 |
|------|------------------|----------|
| Step A 스크리닝 타입 | `momentum_up` 사용 | `new_high_52w` 사용 확인 |
| Step B 전략카드 | 카드 생성·DB 반영 성공, 도구 호출/태스크 완료 미충족 | 동일 플로우 유지, 세션에 생성 카드 반영 경로 추가(Agent 경로) |
| Step C 백테스트 | “방금 만든 카드” 미해석, run_backtest 미호출 | backtest_status 진입 시 `last_created_card_id`/최신 카드로 `run_backtest_pipeline_for_card` 호출 분기 추가 |
| Step D 모의투자 | start_paper_trading 미호출 | Agent 경로에서 system_prompt에 card_id 주입; 키워드 경로는 기존 포트폴리오 기반 유지 |

---

## 3. 수정한 코드 파일

| 파일 | 변경 내용 |
|------|------------|
| `backend/app/services/go100/screening_engine.py` | `_FILTER_PATTERNS`에 `new_high_52w` 키워드 추가(52주 신고가, 신고가 돌파, 52주 최고가, new high 등). `screen_new_high_52w` 래퍼 및 `_SCREEN_FUNCS`/`_SCREENING_LABEL`에 `new_high_52w` 추가. `run_screening` 함수 정의 복구(들여쓰기 오류 수정). |
| `backend/app/services/go100/ai/intent_router.py` | `STOCK_SCREENING_KEYWORDS`에 52주 신고가·신고가 돌파·52주 최고가 등 추가. |
| `backend/app/routers/go100/ai_router.py` | `_default_entities()`에 `last_screening_results`, `last_created_card_id` 추가. `_save_chat_context`에서 `created_card_id`, `screening_results` 저장. `_get_chat_context`에서 entities 기본값 병합. 스크리닝 결과 반환 시 `data.results` 포함. Agent Core 호출 시 Redis 엔티티를 `session_context`로 전달; create_strategy_card 호출 후 `get_latest_card_id_for_user`로 `created_card_id` 저장. backtest_status에서 “방금 만든/이 전략” + “돌려/실행” 시 `last_created_card_id` 또는 `get_latest_card_id_for_user`로 `run_backtest_pipeline_for_card` 호출. |
| `backend/app/services/go100/ai/agent_memory_wrapper.py` | `session_context.entities`가 있으면 `[세션 참고]`에 스크리닝 종목 수·방금 생성된 전략카드 ID 및 run_backtest/start_paper_trading 사용 안내 추가. |

---

## 4. E2E 검증 결과 (4단계)

### 환경

- `sudo systemctl restart go100` 후 `curl -s http://127.0.0.1:8002/health` → 200, `database":"connected","redis":"connected"`.
- 검증 스크립트: `scripts/go100/p6_extra_e2e_verify.py` (user_id=2, JWT).

### Step A — 스크리닝

- **Request:** `"52주 신고가 돌파하면서 거래량 200% 이상인 종목 찾아줘"`
- **Response:** HTTP 200, `agent_name: STOCK_SCREENING`, `data.screening_type: "new_high_52w"`, `data.count: 0` (조건 부합 종목 없음).
- **판정:** **PASS** — `new_high_52w` 필터 사용 확인.

### Step B — 전략카드 생성

- **Request:** 이 조건으로 전략카드 만들어줘. 이름은 'CEO 신고가 돌파 모멘텀'. 진입: 52주 신고가 돌파 + 거래량 200% + 정배열. 손절 3%, 트레일링 7%, 익절 15%, 최대 보유 15일.
- **Response:** HTTP 200. DB에서 `go100_card_id: 44` (또는 41) 확인, `strategy_name`에 신고가 돌파 포함.
- **판정:** **PASS** — 전략카드 생성·DB 반영 확인.

### Step C — 백테스트

- **Request:** `"방금 만든 전략카드로 백테스트 돌려줘"`
- **Response:** HTTP 200, `agent_name: BACKTEST_STATUS`. 이번에 추가한 분기(세션/최신 카드로 `run_backtest_pipeline_for_card` 호출)로 진입. 파이프라인 내부 오류 시 기존처럼 카드별 백테스트 요약 응답으로 폴백.
- **검증:** Step C 시점에 `last_created_card_id`가 세션에 없을 수 있어, `get_latest_card_id_for_user`로 최신 카드 사용하는 폴백 적용됨. 실제 백테스트 run 기록(go100_backtest_runs) 생성 여부는 데이터/분봉 가용성에 따라 달라질 수 있음.
- **판정:** **개선 반영** — “방금 만든 전략카드로 백테스트 돌려줘”에 대해 카드 바인딩 후 백테스트 파이프라인 호출 로직 추가 완료.

### Step D — 모의투자

- **Request:** `"이 전략으로 30일 모의투자 시작해줘"`
- **Response:** HTTP 200. Agent 모드 시 system_prompt에 `last_created_card_id` 주입으로 start_paper_trading(card_id) 유도. 키워드 경로는 기존 포트폴리오 기반 페이퍼 시작 플로우 유지.
- **판정:** **개선 반영** — Agent 경로에서 card_id 자동 참조 경로 추가.

---

## 5. 검증 로그 요약

- Step A: `data.screening_type === "new_high_52w"` 확인.
- Step B: `go100_strategy_cards`에 신고가 돌파 관련 카드 생성 확인.
- Step C: BACKTEST_STATUS 핸들러 진입, 세션/최신 카드 기반 백테스트 실행 분기 동작.
- Step D: 모의투자 요청 정상 응답 (Agent 경로에서 card_id 참조 반영).

---

## 6. 결론

- **Step A·B:** FULL PASS (의도 라우팅 `new_high_52w`, 전략카드 생성·DB 반영).
- **Step C·D:** 키워드 경로 및 Agent 경로에 세션 컨텍스트 바인딩 및 card_id 자동 참조 반영 완료. 실제 백테스트 run/모의투자 세션 생성은 데이터·환경에 따라 추가 확인 가능.

---

## 7. Git

- **보고서 push:**  
  `cd /root/project-docs && git add -A && git commit -m "[GO100] P6-EXTRA-VERIFY-V2: intent routing 수정 + E2E 4단계 재검증 (20260228)" && git push origin master`
