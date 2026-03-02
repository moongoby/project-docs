# CUR-GO100-P3-1-STRATEGY-EVOLUTION-20260227

**작업일**: 2026-02-27  
**목표**: P3-1 전략 진화 엔진 MVP — 가설 기반 스크리닝 → 전략 카드 자동 생성 파이프라인

---

## 1. 요약

- **DB**: `go100_strategy_hypotheses` 테이블 추가 (마이그레이션 035)
- **서비스**: `backend/app/services/go100/strategy_evolution.py` 구현
  - `generate_hypotheses()`: 스크리닝/시그널 기반 가설 자동 생성 (LLM 연동)
  - `test_hypothesis()`: 과거 6개월 스크리닝 시뮬레이션 + N일 수익률 검증 (승률 60%+, 목표수익률 이상 시 VALIDATED)
  - `create_card_from_hypothesis()`: VALIDATED 가설 → `go100_strategy_cards` INSERT
  - `evolution_pipeline()`: 위 3단계 순차 실행
- **Agent 도구**: `run_strategy_evolution`, `get_hypotheses` 등록 (tool_executors + agent_tools)
- **크론**: 매주 토요일 09:00 실행 스크립트 `scripts/go100/run_strategy_evolution.sh` 추가

---

## 2. DB 스키마

**파일**: `backend/migrations/035_go100_strategy_evolution.sql`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| hypothesis_id | SERIAL PK | 자동 증가 ID |
| source_type | VARCHAR(50) | 'screening', 'signal', 'user_chat', 'event' |
| hypothesis_text | TEXT | 가설 문장 |
| filters | JSONB | `{"filters": ["golden_cross", "volume_surge"]}` |
| target_return | DECIMAL(8,4) | 목표 수익률 (예: 0.05) |
| target_days | INTEGER | 목표 보유 일수 |
| status | VARCHAR(20) | PENDING → TESTING → VALIDATED → CARD_CREATED / REJECTED |
| validation_result | JSONB | 검증 결과 요약 (win_rate, avg_return 등) |
| created_card_id | BIGINT FK | 생성된 전략 카드 ID (go100_strategy_cards.go100_card_id) |
| created_at, updated_at | TIMESTAMPTZ | |

인덱스: `idx_hypothesis_status`, `idx_hypothesis_created_at`

---

## 3. 서비스 동작

### 3.1 generate_hypotheses(db, max_new=5)

- `go100_agent_experience_log`에서 최근 30일 스크리닝 이벤트 조회
- 조건검색 필터 2~3개 조합 추출 (combined 또는 단일+다른 필터)
- 고정 후보 조합 보강: golden_cross+volume_surge, foreign_buy+value_low_per 등
- 각 조합에 대해 LLM 호출로 `hypothesis_text`, `target_return`, `target_days` 생성 후 INSERT
- LLM 미설정 시 가설 0건 생성 (에러 없이 빈 목록 반환)

### 3.2 test_hypothesis(db, hypothesis_id)

- 가설의 `filters`로 현재 시점 스크리닝 실행 (단일/조합)
- 산출된 종목 코드에 대해 과거 6개월 `ohlcv_daily`에서 N일 후 수익률 계산
- 승률 = 수익률 > 0 비율, 평균수익률 = mean(수익률)
- **VALIDATED**: 승률 ≥ 60%, 평균수익률 ≥ target_return, 샘플 수 ≥ 10
- 그 외 **REJECTED**, `validation_result`에 결과 저장

### 3.3 create_card_from_hypothesis(db, hypothesis_id)

- status = VALIDATED 이고 `created_card_id`가 NULL인 경우만 처리
- `go100_strategy_cards`에 INSERT (user_id=1, strategy_type=LLM_GENERATED, source_type=CUSTOM)
- entry_rules: 가설 필터 기반 스크리닝 조건, exit_rules: 보유일수·목표수익률
- 가설의 status → CARD_CREATED, created_card_id 설정 후 커밋

### 3.4 evolution_pipeline(db, max_hypotheses=5)

- `generate_hypotheses` → 각 가설에 `test_hypothesis` → VALIDATED만 `create_card_from_hypothesis`
- 반환: `{generated, validated, cards_created, hypothesis_ids[, error]}`

---

## 4. Agent 도구

| 도구 | 설명 |
|------|------|
| run_strategy_evolution | 전략 진화 파이프라인 실행 (가설 생성 → 검증 → 카드 생성). 동기 컨텍스트에서 async 파이프라인을 스레드로 실행 |
| get_hypotheses | 가설 목록 조회 (status, limit 옵션) |

- **agent_tools.py**: 도구 정의 및 파라미터 추가
- **tool_executors.py**: `get_hypotheses`(psycopg2), `run_strategy_evolution`(AsyncSessionLocal + evolution_pipeline)
- **agent_core.py**: SYSTEM_PROMPT에 전략 진화 도구 안내 추가

Agent Chat에서 "전략 진화 실행해줘" 요청 시 LLM이 `run_strategy_evolution` 호출 가능.

---

## 5. 크론

**스크립트**: `scripts/go100/run_strategy_evolution.sh`  
**등록 예시** (crontab -e):

```text
0 9 * * 6 /root/kis-autotrade-v4/scripts/go100/run_strategy_evolution.sh >> /var/log/go100/strategy_evolution.log 2>&1
```

- 매주 토요일 09:00 실행
- 로그: `/var/log/go100/strategy_evolution.log` (디렉터리 사전 생성 권장)

---

## 6. 테스트 결과

| 항목 | 결과 |
|------|------|
| 마이그레이션 035 실행 | 성공 (CREATE TABLE, INDEX, COMMENT) |
| generate_hypotheses() | LLM 미설정 환경에서 0건 생성(정상), 경험 로그 행 접근 오류 수정 후 동작 |
| test_hypothesis(1) | 골든크로스+거래량급증 가설 → 스크리닝 → 720건 샘플, 승률 42.5%, 평균수익률 0.01% → REJECTED (조건 미충족) |
| create_card_from_hypothesis(1) | 가설을 VALIDATED로 수동 설정 후 실행 → go100_card_id=38 카드 생성, status CARD_CREATED 반영 |
| get_hypotheses() | 전체/status=CARD_CREATED 조회 정상 |
| evolution_pipeline() | 정상 완료 (에러 시 result에 error 키 포함) |

---

## 7. 체크리스트

- [x] 코드 레포 반영 (마이그레이션, 서비스, Agent 도구, 크론 스크립트)
- [x] project-docs 보고서 push (본 문서)

---

## 8. 참고 파일

- `backend/migrations/035_go100_strategy_evolution.sql`
- `backend/app/services/go100/strategy_evolution.py`
- `backend/app/services/go100/ai/tool_executors.py` (run_strategy_evolution, get_hypotheses)
- `backend/app/services/go100/ai/agent_tools.py` (도구 정의)
- `scripts/go100/run_strategy_evolution.sh`
