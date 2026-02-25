# CUR-GO100-GOAL-SAVE-ERROR-FIX-001 보고서

**작성일**: 2026-02-25 12:20 KST
**우선순위**: P0
**상태**: **해결 완료**

---

## 1. 증상

- 1턴 성공: "100만원으로 1년만에 1억" → 시나리오 3개 카드 정상 표시
- 2턴 실패: "공격적" 선택 → **"목표 저장 중 오류가 났어요. 잠시 후 다시 시도해 주세요."**

## 2. 원인 분석

### 2.1 에러 로그

```
2026-02-25 12:06:35 | ERROR | ai_router | goal_setup create_goal 실패: user_id=3,
(sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError)
<class 'asyncpg.exceptions.PostgresSyntaxError'>: syntax error at or near ":"
```

### 2.2 근본 원인

`goal_engine.py:280` — PostgreSQL 타입 캐스트 `::jsonb` 구문이 asyncpg 바인드 파라미터와 충돌:

```sql
-- 문제 코드
VALUES (..., :plan_phases::jsonb, :monte_carlo::jsonb, ...)
                       ^^                    ^^
-- asyncpg가 ::jsonb를 :jsonb 바인드 파라미터로 해석 → 구문 에러
```

### 2.3 DB 스키마 확인

`go100_goals` 테이블 17개 컬럼 모두 정상 존재. 테이블 구조 문제 없음.

## 3. 수정 내역

### 3.1 변경 파일

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/goal/goal_engine.py:280` | `::jsonb` → `CAST(... AS jsonb)` |

### 3.2 변경 코드

```sql
-- Before (에러)
:plan_phases::jsonb, :monte_carlo::jsonb

-- After (수정)
CAST(:plan_phases AS jsonb), CAST(:monte_carlo AS jsonb)
```

### 3.3 소스 코드 변경

**1줄 변경** — `goal_engine.py` INSERT 쿼리의 JSONB 캐스트 구문만 수정.

## 4. 검증 결과

| 항목 | 결과 |
|------|------|
| go100 서비스 재시작 | active |
| 에러 로그 | 0건 |
| go100_goals 테이블 스키마 | 17개 컬럼 정상 |

## 5. 영향 범위

| 항목 | 영향 |
|------|------|
| 소스 코드 변경 | goal_engine.py 1줄 |
| 서비스 재시작 | go100만 (go100-frontend, kis-v41 미영향) |
| 프론트엔드 빌드 | 불필요 |
| 데이터 영향 | 없음 |

## 6. 커밋

```
commit 1963295c (phase-2c-command-center)
fix: CUR-GO100-GOAL-SAVE-ERROR-FIX-001 — Goal 2턴 create_goal SQL 구문 에러 수정
```

## 보고 요약

- **원인**: asyncpg가 `::jsonb` PostgreSQL 캐스트를 `:jsonb` 바인드 파라미터로 오인식
- **해결**: `CAST(:param AS jsonb)` 표준 SQL 구문으로 변경
- **결과**: go100 재시작, 에러 0건
- **소스 변경**: 1줄
