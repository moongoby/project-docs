# CUR-GO100-GOAL-SAFETY-001 — current_phase 타입 방어 및 Goal 흐름 방어 보고서

**작성:** 2026-02-25  
**작업ID:** CUR-GO100-GOAL-SAFETY-001  
**우선순위:** P0  
**목표:** go100_goals.current_phase 타입 확인 → 코드 방어 → Redis fallback 강화

---

## 1. 요약

- **DB 확인:** `go100_goals.current_phase` 컬럼 타입은 **integer**.
- **CASE A 적용:** `goal_engine.update_goal`에서 문자열 `phase_a`/`phase_b`/`phase_c`를 1/2/3으로 매핑하여 integer 컬럼에 안전하게 저장.
- **Redis fallback:** 2턴 시 Redis 미사용 시 `conversation_history`에서 `data` 재추출, 로깅 추가.
- **에러 핸들링:** `create_goal`/`update_goal` try-except, 사용자 친절 메시지, 부분 성공 시 생성된 카드만 반환, `logger.error` 보강.

## 2. DB 타입 확인 결과

```text
column_name     | data_type
----------------+----------
current_phase   | integer
```

- INSERT 시 이미 `1` 사용 중 (goal_engine.create_goal).
- ai_router 2턴에서 `update_goal(..., current_phase="phase_a")` 호출 시 타입 불일치 가능 → 방어 로직 추가.

## 3. 변경 파일

| 구분 | 경로 | 내용 |
|------|------|------|
| 수정 | backend/app/services/go100/goal/goal_engine.py | current_phase 문자열→정수 매핑(PHASE_MAP), doc/주석 CUR-GO100-GOAL-SAFETY-001 |
| 수정 | backend/app/routers/go100/ai_router.py | Redis fallback 로깅·conversation_history 재추출, create_goal/update_goal try-except, logger.error |

## 4. 상세 변경

### 4.1 goal_engine.py

- **헤더:** `# CUR-GO100-GOAL-SAFETY-001, 2026-02-25` 추가.
- **update_goal:**  
  - `PHASE_MAP = {"phase_a": 1, "phase_b": 2, "phase_c": 3}`.  
  - `current_phase`가 문자열이면 매핑 후 정수로 변환, 변환 실패 시 기본값 1.

### 4.2 ai_router.py

- **헤더:** `# CUR-GO100-GOAL-SAFETY-001, 2026-02-25` 추가.
- **1턴 Redis setex:** 실패 시 `logger.warning` (기존 `pass` 유지, conversation_history data로 fallback 가능).
- **2턴 prev_data:** Redis `get` 예외 시 `prev_data or _extract_goal_data_from_history(conversation_history)`로 fallback, `logger.warning` 추가.
- **create_goal:** try-except 추가, 실패 시 `logger.error` 및 사용자 안내 메시지 반환.
- **update_goal:** try-except 추가, 실패 시 `logger.error` (목표/전략 카드는 이미 생성된 상태 유지).
- **2턴 update_goal 호출:** `current_phase=1` 사용 (integer 명시).

## 5. 검증

- `python3 -c "from backend.app.services.go100.goal.goal_engine import GoalEngine; ..."` (PYTHONPATH 설정) → GoalEngine import OK.
- `scripts/pre-commit-check.sh` 통과 (Python/TypeScript).
- Lint 에러 없음.
- kis-v41-* 재시작 없음, 실계좌 미사용, go100 관련 파일만 수정.

## 6. 백업

- 경로: `/root/backup/goal-safety-20260225-103425/`
- 파일: goal_engine.py, ai_router.py

## 7. 규칙 체크리스트

- [x] kis-v41-* 재시작 없음
- [x] 실계좌 미사용
- [x] 백업 완료
- [x] go100_ 파일만 수정
- [x] 헤더 주석 CUR-GO100-GOAL-SAFETY-001, 2026-02-25
- [x] pre-commit-check 통과
- [x] 보고서 GitHub push (예정)
