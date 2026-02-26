# CUR-GO100-PHASE7-E2-ONBOARDING (2026-02-26)

## 목표
신규 사용자가 처음 접속했을 때 **목표 설정 → 전략 생성 → 페이퍼 시작**까지 자연스럽게 안내하는 온보딩 플로우.

## 구현 요약

### 1. 온보딩 상태 추적
- **Redis 키**: `go100:onboard:{user_id}` → `{"step": 1~6, "started_at": "..."}`
- **TTL**: 24시간
- **단계**: 1=welcome, 2=goal_setup, 3=strategy_create, 4=backtest_run, 5=paper_start, 6=complete

### 2. 신규 사용자 판별
- **조건**: `go100_goals` 0건 **and** `go100_strategy_cards` 0건
- **위치**: `backend/app/services/go100/ai/data_queries.py` → `is_new_go100_user(user_id, db)`

### 3. 첫 대화 시 환영 메시지
- **위치**: `ai_router.ai_chat()` 상단 (인텐트 분류 전)
- 신규 사용자이고 onboard step이 0 또는 없으면 → step 1 저장 후 `WELCOME_MESSAGE` 반환

### 4. 단계별 안내 메시지
| 완료 이벤트 | 다음 step | 추가 메시지 |
|------------|-----------|-------------|
| 목표 설정 2턴 (전략 카드 있음) | 4 | AFTER_STRATEGY (백테스트 해줘) |
| 목표 설정 2턴 (카드 없음) | 3 | AFTER_GOAL (전략 만들어줘) |
| 전략 생성 완료 (step 3인 경우) | 4 | AFTER_STRATEGY |
| 백테스트 완료 (`_bg_backtest_cards`) | 5 | (Redis만, 다음 채팅 시 활용 가능) |
| 페이퍼 트레이딩 시작 API | 6 | (Redis만, ONBOARDING_COMPLETE 문구는 다음 채팅 등에서 활용 가능) |

### 5. 변경/추가 파일
- `backend/app/services/go100/ai/data_queries.py`: `is_new_go100_user()` 추가
- `backend/app/services/go100/onboarding.py`: **신규** — `get_onboard_state`, `set_onboard_step`
- `backend/app/routers/go100/ai_router.py`: 온보딩 상수·첫 대화 환영·goal/strategy/backtest 완료 시 step 및 안내 메시지
- `backend/app/routers/go100/paper_trading_router.py`: `POST /start` 성공 시 `set_onboard_step(user_id, 6)` 호출

### 6. 검증
- 신규 사용자(목표 0건, 카드 0건)가 "안녕" 등 첫 메시지 전송 → 환영 메시지 + 목표 설정 안내
- 목표 설정 후(2턴 완료) → Goal 결과 + "전략 만들어줘" 또는 "백테스트 해줘" 안내 (카드 생성 여부에 따라)
- 전략 생성 완료 시(온보딩 step 3) → "백테스트 해줘" 안내
- 백테스트 백그라운드 완료 → Redis step 5
- 페이퍼 시작 API 호출 → Redis step 6

## Git
- kis-autotrade-v4: `feat(go100): Phase 7 E-2 사용자 온보딩 플로우`
- project-docs: `docs(go100): Phase 7 E-2 온보딩 플로우 보고서`
