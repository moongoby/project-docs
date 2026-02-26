# CUR-GO100-PHASE5-C1-GOAL-ENGINE 구현 보고

**작업일**: 2026-02-26  
**목표**: 백억이 V2 핵심 — 사용자 자산 목표 역설계 Goal Engine

---

## 1. 요약

- **신규 파일**: `backend/app/services/go100/ai/goal_engine.py`  
  - `parse_goal(message)` — 자연어 목표 파싱 (한국어 금액·기간)
  - `calculate_required_cagr(initial, target, years)` — 필요 연복리수익률
  - `assess_risk_profile(cagr)` — 위험도 평가 (conservative / moderate / aggressive / very_aggressive)
  - `generate_scenarios(initial, target, years, risk_profile)` — 낙관/기본/비관 3시나리오
  - `recommend_strategies(risk_profile, initial)` — 위험도별 전략 조합 추천
  - `format_goal_response(goal_data)` — 사용자용 목표 분석 포맷
  - `save_goal(user_id, goal_data, db)` — go100_goals 저장 후 goal_id 반환

- **DB**: `go100_goals` 스키마 확장  
  - `scenarios` (JSONB), `recommended_strategies` (JSONB) 추가

- **goal_setup 핸들러**: 1턴에서 신규 Goal Engine 전면 사용  
  - 파싱 실패 시 "시작 자산, 목표 자산, 기간을 알려주세요" 재질문  
  - 성공 시 3시나리오 + 전략 조합 제안, Redis에 goal_data 임시 저장  
  - "1번"/"이대로 진행" 선택 시 기존 create_goal + 전략 자동 생성, 이후 scenarios/recommended_strategies UPDATE

---

## 2. DB 스키마

```sql
ALTER TABLE go100_goals ADD COLUMN IF NOT EXISTS scenarios JSONB;
ALTER TABLE go100_goals ADD COLUMN IF NOT EXISTS recommended_strategies JSONB;
```

- 기존 컬럼(initial_capital, target_capital, target_years, required_cagr, risk_appetite, status) 유지
- go100_* 테이블만 변경, ADD COLUMN IF NOT EXISTS로 안전 적용

---

## 3. 검증 시나리오

| 시나리오 | 입력 예 | 기대 |
|----------|---------|------|
| 안정적 목표 | "1억으로 5년 안에 1.5억 만들고 싶어" | CAGR 약 8.4%, conservative, 3시나리오 |
| 공격적 목표 | "5천만원으로 3년 안에 3억" | CAGR 약 82%, very_aggressive, 경고 포함 |
| 선택 | "1번으로 진행해줘" | 전략 조합 생성, go100_goals 저장 |
| 불완전 입력 | "돈 좀 벌고 싶어" | "시작 자산, 목표 자산, 기간을 알려주세요" 재질문 |

단위 검증(venv 내):

- `parse_goal("1억으로 5년 안에 1.5억 만들고 싶어")` → initial 1억, target 1.5억, years 5, CAGR 8.45%, conservative
- `parse_goal("5천만원으로 3년 안에 3억")` → initial 5천만, target 3억, years 3, CAGR 81.71%, very_aggressive
- `parse_goal("돈 좀 벌고 싶어")` → None

---

## 4. 테스트 방법

```bash
# 서비스 재시작
systemctl restart go100

# (TOKEN은 실제 인증 토큰으로 교체)
# 테스트 1: 안정적 목표
curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"1억으로 5년 안에 1.5억 만들고 싶어"}'

# 테스트 2: 공격적 목표
curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"5천만원으로 3년 안에 3억"}'

# 테스트 3: 선택
curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"1번으로 진행해줘"}'

# 테스트 4: 불완전 입력
curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"돈 좀 벌고 싶어"}'

# DB 확인
sudo -u postgres psql -d kisautotrade -c "
SELECT goal_id, initial_capital, target_capital, target_years, required_cagr, risk_appetite, status
FROM go100_goals ORDER BY created_at DESC LIMIT 5;
"
```

---

## 5. Git

- **kis-autotrade-v4**: `feat(go100): Phase 5 C-1 Goal Engine — 자산 목표 역설계 엔진` (branch: phase-2c-command-center)
- **project-docs**: `docs(go100): Phase 5 C-1 Goal Engine 보고서` (branch: master)

---

## 6. 참고

- 기존 `backend/app/services/go100/goal/goal_engine.py`(GoalEngine)는 2턴의 create_goal, generate_strategy_intents, update_goal 등에서 그대로 사용
- 1턴만 `backend/app/services/go100/ai/goal_engine.py`(파싱·CAGR·위험도·3시나리오·전략 추천·포맷)로 교체
- 시나리오 선택 시 "1번"/"이대로 진행" → Redis에 저장된 risk_profile로 진행
