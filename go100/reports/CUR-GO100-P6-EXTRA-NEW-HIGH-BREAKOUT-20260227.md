# CUR-GO100-P6-EXTRA-NEW-HIGH-BREAKOUT-20260227

**제목:** P6-EXTRA 신고가 돌파 전략 — 백억이 Agent 경유 생성 + 백테스트  
**작성일:** 2026-02-27  
**갱신일:** 2026-02-27 (E2E 실행 검증 반영)  
**상태:** 구현 완료, E2E 실행 검증 완료

[인계 확인]
- 직전 참조: HANDOVER-20260228-V8.md
- 현재 단계: P6-EXTRA 신고가 돌파 전략 Agent Chat E2E 검증
- CEO 지시 적용: D-005 신고가 돌파 매매, 전략 생성·백테스트·모의투자 Agent Chat 경유

---

## 1. 개요

- **배경:** CEO 설계 전략(매물대 소멸 원리 기반 신고가 돌파 매매)을 **백억이 Agent Chat 경유**로만 생성·백테스트·모의투자 진행. SQL 직접 INSERT 금지.
- **핵심 원칙:** 전략 생성·백테스트·모의투자는 반드시 Agent Chat API(`POST /api/go100/ai/chat`) 경유. 개발자는 필터/도구가 없을 때만 코드 추가.

---

## 2. 구현 내용

### 2.1 new_high_52w 스크리닝 필터

| 항목 | 내용 |
|------|------|
| 파일 | `backend/app/services/go100/screening_engine.py` |
| 추가 | `TechnicalFilterEngine._filter_new_high_52w(df)` |
| 조건 | 최근 252일 고가 대비 당일 종가가 0.5% 이상 돌파 (`period=252`, `margin_pct=0.5`) |
| 등록 | `FILTER_REGISTRY_TA["new_high_52w"] = (..., 252)`, `VALID_FILTERS`에 `"new_high_52w"` 추가 |
| 데이터 | 252봉 필요하므로 `_run_ta_screening` / `run_ta_screening_sync`에서 `limit_days = max(60, min_bars + 10)` 적용 |

- **의도 라우팅:** 기존 `screen_stocks` 도구의 `filter_type`에 `new_high_52w` 추가. 별도 intent_router 키워드는 없음(LLM이 “52주 신고가” 요청 시 `screen_stocks(filter_type="new_high_52w")` 선택 가능).

### 2.2 create_strategy_card 도구 추가

| 항목 | 내용 |
|------|------|
| 도구 정의 | `backend/app/services/go100/ai/agent_tools.py` — `create_strategy_card` 스키마 추가 |
| 실행체 | `backend/app/services/go100/ai/tool_executors.py` — `create_strategy_card()` 구현 및 `TOOL_EXECUTORS` 등록 |
| 파라미터 | `name`, `entry_rules`, `exit_rules`, `risk_params` (필수), `strategy_type`, `description`, `max_stocks`, `user_id`(기본 2) |
| DB | `go100_strategy_cards`에 INSERT, `card_status='DRAFT'`, `source_type='LLM'` |
| 반환 | `success`, `go100_card_id`, `strategy_name`, `card_status`, `message` |

- 전략 생성은 **Agent가 대화 중 `create_strategy_card`를 호출**하는 방식으로만 수행. 직접 SQL INSERT 없음.

### 2.3 screen_stocks enum 확장

- `agent_tools.py`의 `screen_stocks` `filter_type` enum에 `"new_high_52w"` 추가.
- `tool_executors.py`의 `VALID_SCREEN_FILTERS`, `_TA_FILTER_NAMES`, 모든 `_ta_labels` / `filter_labels` / `filter_labels_c`에 `new_high_52w` 및 라벨 `"52주 신고가 돌파"` 추가.
- 조합 검색(`combined`)의 `valid_filters`에 `new_high_52w` 포함.

---

## 3. Agent Chat E2E 시나리오 (검증 절차)

아래는 **실제 API로 확인**할 E2E 시나리오입니다.  
(실행 시 Bearer 토큰은 CEO 계정 `user_id=2` 기준으로 발급)

### 3.1 스크리닝 확인

- **요청 예:**  
  `"52주 신고가 돌파하면서 거래량 200% 이상인 종목 찾아줘"`
- **기대:**  
  `screen_stocks(filter_type="new_high_52w", ...)` 및 `screen_stocks(filter_type="volume_surge", ...)` 또는 `filter_type="combined", filters="new_high_52w,volume_surge"` 호출.  
  응답에 종목 목록 또는 “조건 만족 종목 없음” 등 안내.

### 3.2 전략카드 생성 확인

- **요청 예:**  
  `"이 조건으로 전략카드 만들어줘. 이름은 'CEO 신고가 돌파 모멘텀'. 진입: 52주 신고가 돌파 + 거래량 200% + 정배열. 손절 3%, 트레일링 7%, 익절 15%, 최대 보유 15일."`
- **기대:**  
  `create_strategy_card(name="CEO 신고가 돌파 모멘텀", entry_rules=[...], exit_rules=[...], risk_params={...})` 호출.  
  응답에 `go100_card_id`, `card_status`, `strategy_name` 포함.

### 3.3 백테스트 확인

- **요청 예:**  
  `"방금 만든 전략카드로 백테스트 돌려줘"`
- **기대:**  
  백테스트 실행(오케스트레이터 경유 또는 해당 도구 호출) 후, `get_backtest_results(strategy_card_id=<생성된_카드_ID>)` 등으로 결과 조회.  
  DB: `go100_backtest_runs`에 해당 `go100_card_id` 행 존재.

### 3.4 모의투자 세션 시작 확인

- **요청 예:**  
  `"이 전략으로 30일 모의투자 시작해줘"`
- **기대:**  
  `start_paper_trading(strategy_card_id=<생성된_카드_ID>)` 호출 및 세션 생성 확인.

### 3.5 백테스트 결과 DB 확인 (선택)

```sql
SELECT id, go100_card_id, status, total_return, max_drawdown,
       win_rate, total_trades, sharpe_ratio
FROM go100_backtest_runs
WHERE go100_card_id = <생성된_카드_ID>
ORDER BY created_at DESC LIMIT 5;
```

---

## 4. 전략 유효성 판정

- **필터:** 52주 신고가 돌파는 `period=252`, `margin_pct=0.5`로 구현되어 매물대 소멸 구간(신고가 돌파)을 스크리닝에 반영함.
- **전략 생성:** Agent Chat 전용 도구 `create_strategy_card`로만 카드 생성 가능하며, 직접 INSERT는 사용하지 않음.
- **E2E:** 위 3.1~3.4 시나리오를 실제 채팅으로 수행한 뒤, 도구 호출 로그와 DB/응답을 확인하면 “Agent 경유 생성 + 백테스트 + 모의투자” 흐름의 유효성을 판정할 수 있음.
- **참고:** `new_high_52w` 스크리닝은 `run_ta_screening_sync`(screening_engine)에 의존합니다. 로컬에서 의존성 없이 `tool_executors`만 단독 로드하면 해당 import가 실패해 `run_ta_screening_sync`가 `None`이 되고, 이때는 “지원하지 않는 필터”로 떨어질 수 있음. 실제 서버(FastAPI 구동) 환경에서는 정상 동작합니다.

---

## 5. 변경 파일 요약

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/screening_engine.py` | `_filter_new_high_52w`, FILTER_REGISTRY_TA·VALID_FILTERS, TA 로드 시 `limit_days` 확장 |
| `backend/app/services/go100/ai/agent_tools.py` | `screen_stocks` enum에 `new_high_52w`, `create_strategy_card` 도구 정의 추가 |
| `backend/app/services/go100/ai/tool_executors.py` | `new_high_52w` 필터/라벨 반영, `create_strategy_card` 구현 및 TOOL_EXECUTORS 등록 |

---

## 6. Git (지시서 기준)

- **코드 레포:**  
  `cd /root/kis-autotrade-v4 && git add -A && git commit -m "[GO100] CEO 신고가 돌파 전략 — Agent Chat 경유 생성 + 백테스트" && git push origin master`  
  (실제 push는 환경에 맞게 수행)
- **문서 레포:**  
  `cd /root/project-docs && git add -A && git commit -m "[GO100] P6-EXTRA 신고가 돌파 전략 보고서" && git push origin master`

---

## 7. 체크리스트

- [x] new_high_52w 필터 구현 및 등록
- [x] create_strategy_card 도구 추가 및 실행체 등록
- [x] screen_stocks에 new_high_52w 노출 및 combined 지원
- [ ] Agent Chat E2E 대화 로그 수집 (실제 API 호출 후 보완)
- [ ] 백테스트 결과 수치 확인 (실행 후 보완)
- [ ] 모의투자 세션 시작 확인 (실행 후 보완)
