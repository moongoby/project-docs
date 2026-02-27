# CUR-GO100-P5-1-SELF-REVIEW — P5-1 AI 자기리뷰 시스템

**일시:** 2026-02-27  
**작업 ID:** CUR-GO100-P5-1-SELF-REVIEW (P5-1)  
**목적:** 백억이가 주간/월간 단위로 추천 성과, 전략 카드 승률, 사용자 경험 로그를 자체 분석하여 개선안을 도출하는 시스템 구현

---

## 1. 요약

- **DB:** `go100_agent_self_review` 테이블 추가 (마이그레이션 043).
- **서비스:** `backend/app/services/go100/self_review_engine.py` — 기간 데이터 수집, 전략 성과 분석, LLM 개선안 도출, 리뷰 저장/조회.
- **Cron:** 매주 일요일 10:00 `run_self_review.sh` 실행 (로그: `/var/log/go100/self_review.log`).
- **Agent Tools:** `get_self_review(period='WEEKLY')`, `run_self_review()` 추가.
- **테스트:** `scripts/go100/test_self_review.py` — collect_period_data(최근 7일), generate_review, DB 저장 확인 통과.

---

## 2. 구현 범위

### 2.1 DB (backend/migrations/043_go100_self_review.sql)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| review_id | SERIAL PRIMARY KEY | 리뷰 ID |
| review_period | VARCHAR(20) | WEEKLY, MONTHLY |
| period_start, period_end | DATE | 리뷰 기간 |
| total_recommendations | INTEGER | 총 추천 건수 |
| successful_recommendations | INTEGER | 성공 추천 건수 |
| accuracy_rate | NUMERIC(5,2) | 정확률(%) |
| strategy_performance | JSONB | 전략카드별 성과 |
| user_feedback_summary | JSONB | 사용자 피드백 요약 |
| improvement_suggestions | JSONB | AI 개선안 |
| model_used | VARCHAR(50) | 사용 LLM 모델 |
| raw_analysis | TEXT | LLM 원문 |
| created_at | TIMESTAMPTZ | 생성 시각 |

- 인덱스: `(period_start, period_end)`, `(created_at DESC)`.

### 2.2 서비스 (self_review_engine.py)

| 함수 | 설명 |
|------|------|
| `collect_period_data(start_date, end_date)` | go100_backtest_runs, go100_paper_trades(선택), go100_agent_experience_log 집계. paper_trades 테이블 없으면 빈 목록 반환. |
| `analyze_strategy_performance(period_data)` | 전략카드별 승률, MDD, 평균수익률 산출. |
| `generate_review(period='WEEKLY')` | 수집 → 분석 → LLM(design_chat, Tier 2 Claude Sonnet) 개선안 요청 → go100_agent_self_review 저장. LLM 미설정 시 기본 통계 문구만 저장. |
| `get_latest_review(period=None)` | 최신 리뷰 1건 조회. period 지정 시 해당 주기만. |

- **WEEKLY:** 전주 월요일~일요일. **MONTHLY:** 전월 1일~말일.
- LLM 라우트: `RequestType.DESIGN_CHAT` (claude-sonnet-4-6 등).

### 2.3 Cron

- **스크립트:** `/root/kis-autotrade-v4/scripts/go100/run_self_review.sh`
- **등록 예시:** `0 10 * * 0 /root/kis-autotrade-v4/scripts/go100/run_self_review.sh >> /var/log/go100/self_review.log 2>&1`
- 매주 일요일 10:00 주간 리뷰 자동 생성.

### 2.4 Agent Tools

| 도구 | 설명 |
|------|------|
| `get_self_review(period='WEEKLY')` | 최신 자기리뷰 결과 조회. |
| `run_self_review()` | 즉시 주간 자기리뷰 실행 후 결과 반환. |

- 등록 위치: `agent_tools.py` (AGENT_TOOLS), `tool_executors.py` (TOOL_EXECUTORS).

### 2.5 테스트

- **스크립트:** `scripts/go100/test_self_review.py`
- **검증:**  
  1) `collect_period_data` — 최근 7일 backtest_runs / paper_trades / experience_log 수집.  
  2) `generate_review(period='WEEKLY')` — LLM 미설정 시에도 기본 통계 기반 리뷰 저장.  
  3) `get_latest_review` — DB 저장 행 존재 확인.

---

## 3. 생성/수정 파일

| 경로 | 유형 |
|------|------|
| backend/migrations/043_go100_self_review.sql | 신규 |
| backend/app/services/go100/self_review_engine.py | 신규 |
| backend/app/services/go100/ai/agent_tools.py | 수정 (get_self_review, run_self_review 추가) |
| backend/app/services/go100/ai/tool_executors.py | 수정 (get_self_review, run_self_review 실행체 및 TOOL_EXECUTORS 등록) |
| scripts/go100/run_self_review.sh | 신규 |
| scripts/go100/test_self_review.py | 신규 |

---

## 4. 비고

- **go100_paper_trades:** 마이그레이션 041 미적용 환경에서는 해당 테이블 조회를 건너뛰고 빈 목록으로 처리 (별도 연결에서 try/except).
- **LLM:** ANTHROPIC_API_KEY 설정 시 design_chat(Claude Sonnet)로 개선안 생성; 미설정 시 `improvement_suggestions`에 안내 문구만 저장.

---

## 5. 체크리스트

- [x] 코드 레포 반영 (kis-autotrade-v4)
- [ ] project-docs 보고서 push (본 문서)
