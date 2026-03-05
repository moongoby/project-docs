---
project: kis-autotrade-v4
task_id: T-090 (CUR-V41-STAGE-ENGINE-001)
completed_at: 2026-03-05T11:30:00+09:00
---

# T-090 결과 보고서: Stage 자동 전환 엔진 구현

[인계 확인]
직전 완료: T-088
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002
strategy_cards: 60
open_positions: 14

---

## 실행 지시서 원문

Task ID: 090
제목: Stage 자동 전환 엔진 구현 + HANDOVER v9.5 업데이트
프로젝트: KIS
우선순위: P1
예상 토큰: ~25K
의존: 086 ✅
자체승인: YES

목적: Task086 시뮬레이션의 Stage 전환 조건을 실전 코드로 구현.
      100만원→100억 자동 파일럿 시스템의 핵심 인프라.

Phase 1: Stage 엔진 구현

Step 1-1: backend/app/services/stage_manager.py 생성
  class StageManager:
    - check_upgrade(): 자본 + PF + MDD 조건 확인
    - check_downgrade(): 안전장치 조건 확인
    - get_current_stage(): DB에서 현재 Stage 조회
    - apply_stage_allocation(): Stage별 DESK 배분 적용
    - log_transition(): Stage 변경 이력 기록

Step 1-2: DB 테이블 생성
  v4_stage_history (id, stage_from, stage_to, capital, trigger_reason, created_at)
  v4_stage_config (stage, desk_allocation JSON, active BOOLEAN)

Step 1-3: 크론 연동 — 매일 장마감 후(15:40 KST) Stage 체크
  40 6 * * 1-5 python3 scripts/check_stage_transition.py

Phase 2: HANDOVER v9.5

Step 2-1: Task 084~090 완료 이력 반영
Step 2-2: DESK5 "심층 재설계 진행중" 상태 반영
Step 2-3: Stage 엔진 구조 문서화
Step 2-4: git commit + push

완료 조건:
  StageManager 클래스 구현 + 테스트
  DB 테이블 생성
  크론 등록
  HANDOVER v9.5 업데이트

보고서: CUR-V41-STAGE-ENGINE-001-20260305.md

---

## Phase 1: Stage 엔진 구현 결과

### Step 1-1: `backend/app/services/stage_manager.py` 생성 ✅

**StageManager 클래스** 총 332줄, 6개 메서드 구현:

| 메서드 | 설명 |
|--------|------|
| `check_upgrade()` | 자본+PF+MDD 조건으로 업그레이드 판단 |
| `check_downgrade()` | 안전장치 조건 (자본/PF/MDD 하한) 판단 |
| `get_current_stage()` | DB v4_stage_config에서 활성 Stage 조회 |
| `get_current_capital()` | accounts.total_evaluation + total_deposit 합계 |
| `get_trailing_pf(window)` | 최근 N일 Profit Factor 계산 |
| `get_max_drawdown(window)` | 최근 N일 MDD 계산 |
| `apply_stage_allocation(stage)` | v4_stage_config 활성 Stage 갱신 |
| `log_transition(result)` | v4_stage_history에 전환 이력 INSERT |
| `get_snapshot()` | 현재 Stage 전체 스냅샷 반환 |
| `seed_initial_config()` | 초기 설정 데이터 삽입 |

**Stage 설정 (Task086 Monte Carlo 시뮬레이션 기준)**:

| Stage | 자본 범위 | DESK 배분 |
|-------|-----------|-----------|
| Stage 1 | 1백만 ~ 4천만 | DESK3(70%) + DESK4(30%) |
| Stage 2 | 4천만 ~ 2억 | DESK3(50%) + DESK4(30%) + DESK5(10%) + DESK2(10%) |
| Stage 3 | 2억 ~ 10억 | DESK3(40%) + DESK4(25%) + DESK2(20%) + DESK5(10%) + GO100(5%) |
| Stage 4 | 10억 ~ 100억 | DESK3(30%) + DESK4(20%) + DESK2(20%) + GO100(15%) + DESK5(10%) + BOND(5%) |

**업그레이드 조건 (AND 조건)**:

| 전환 | 자본 조건 | PF 조건 | PF 윈도우 | MDD 상한 |
|------|----------|---------|----------|---------|
| 1→2 | ≥ 40,000,000원 | ≥ 1.5 | 30일 | — |
| 2→3 | ≥ 200,000,000원 | ≥ 1.3 | 60일 | ≤ 15% |
| 3→4 | ≥ 1,000,000,000원 | ≥ 1.2 | 90일 | ≤ 20% |

**다운그레이드 조건 (OR 조건, 안전장치)**:

| 전환 | 자본 조건 | PF 조건 | MDD 조건 |
|------|----------|---------|---------|
| 2→1 | < 30,000,000원 | PF(30d) < 1.0 | — |
| 3→2 | < 150,000,000원 | — | MDD(30d) > 25% |

### Step 1-2: DB 테이블 생성 ✅

마이그레이션 파일: `backend/migrations/056_v4_stage_tables.sql`

**실행 결과** (PGPASSWORD psql -f 056_v4_stage_tables.sql):
```
CREATE TABLE   ← v4_stage_history
CREATE INDEX   ← idx_v4_stage_history_created
CREATE INDEX   ← idx_v4_stage_history_stages
COMMENT
CREATE TABLE   ← v4_stage_config
COMMENT
INSERT 0 4     ← Stage 1~4 초기 데이터 삽입 (Stage 1 active=TRUE)
```

**v4_stage_config 검증**:
```
 stage | active |                                      desk_allocation
-------+--------+-------------------------------------------------------------------------------------------
     1 | t      | {"DESK3": 0.70, "DESK4": 0.30}
     2 | f      | {"DESK2": 0.10, "DESK3": 0.50, "DESK4": 0.30, "DESK5": 0.10}
     3 | f      | {"DESK2": 0.20, "DESK3": 0.40, "DESK4": 0.25, "DESK5": 0.10, "GO100": 0.05}
     4 | f      | {"BOND": 0.05, "DESK2": 0.20, "DESK3": 0.30, "DESK4": 0.20, "DESK5": 0.10, "GO100": 0.15}
(4 rows)
```

### Step 1-3: 크론 등록 ✅

파일: `scripts/check_stage_transition.py`

실행 흐름:
1. `sm.check_upgrade()` → 업그레이드 조건 체크
2. (업그레이드 없는 경우) `sm.check_downgrade()` → 다운그레이드 조건 체크
3. 전환 발생 시: `sm.log_transition()` + `sm.apply_stage_allocation()` + 텔레그램 알림
4. 전환 없는 경우: 일일 현황 텔레그램 보고

크론 등록:
```cron
# [KIS TASK-090] Stage 전환 체크 — 15:40 KST (06:40 UTC) 평일
40 6 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_stage_transition.py >> /root/kis-autotrade-v4/logs/stage_transition.log 2>&1
```

등록 확인:
```
crontab -l | grep TASK-090
# [KIS TASK-090] Stage 전환 체크 — 15:40 KST (06:40 UTC) 평일
```

---

## Phase 2: 기능 테스트 결과

```python
# 테스트 실행:
# /root/kis-autotrade-v4/venv/bin/python3 -c "from backend.app.services.stage_manager import StageManager; ..."

현재 Stage: 1
현재 자본: 1,489,649,101원   ← accounts(total_evaluation + total_deposit) 합계
PF(30d): 0.0                ← 최근 30일 CLOSED 포지션 없음 (정상)
MDD(30d): 0.00%

업그레이드 체크:
  triggered=False
  reason=자본 1,489,649,101원 ≥ 40,000,000원 | PF(30d) 0.000 < 1.5
  → 자본 조건 충족, PF 미축적으로 업그레이드 보류 (의도된 동작)

다운그레이드 체크:
  triggered=False
  reason=Stage 1: 다운그레이드 불가 (최소 Stage)

스냅샷:
  stage=1, capital=1,489,649,101, pf=0.0, mdd=0.00%
  allocation={'DESK3': 0.7, 'DESK4': 0.3}

ALL PASS
```

**컬럼명 수정**: 최초 `total_eval_amt` → 실제 컬럼 `total_evaluation + total_deposit` 으로 수정. 자본 조회 정상 동작.

---

## 생성/수정 파일 목록

| 파일 | 상태 | 내용 |
|------|------|------|
| `backend/app/services/stage_manager.py` | **신규 생성** | StageManager 클래스 (332줄) |
| `backend/migrations/056_v4_stage_tables.sql` | **신규 생성** | v4_stage_history + v4_stage_config DB 마이그레이션 |
| `scripts/check_stage_transition.py` | **신규 생성** | 일일 15:40 크론 실행 스크립트 |
| crontab | **수정** | `40 6 * * 1-5` 크론 항목 추가 |
| `report/v41/CUR-V41-STAGE-ENGINE-001-20260305.md` | **신규 생성** | 본 보고서 |

---

## 완료 조건 체크

- [x] StageManager 클래스 구현 (`backend/app/services/stage_manager.py`)
- [x] StageManager 테스트 실행 (`ALL PASS`)
- [x] DB 테이블 생성 (`v4_stage_history` + `v4_stage_config`, 4행 초기 데이터)
- [x] 크론 등록 (`40 6 * * 1-5`)
- [ ] HANDOVER v9.5 업데이트 (root 권한 필요 → done_watcher 경유 처리)

---

## HANDOVER v9.5 업데이트 내용 (project-docs push 요청)

### 섹션 2 "완료된 작업" 추가 행:
```
| **T-090 Stage 자동 전환 엔진** | 03-05 | — | — | **Stage 엔진 구현**: StageManager 클래스(check_upgrade/check_downgrade/apply_stage_allocation/log_transition), v4_stage_history+v4_stage_config 마이그레이션 실행, 크론 40 6 * * 1-5 등록, 현재 자본 14.9억/Stage1(PF 미축적) |
```

### 섹션 3 "진행 중 작업" 갱신:
- "DESK5 심층 재설계" 상태: **진행중** (현행 유지)

### 섹션 5 "핵심 발견" 추가:
- Stage 엔진: 현재 자본 14.9억원이지만 Stage 1 유지 (PF 30일 데이터 미축적 — 정상 보수 설계)
- Stage 업그레이드는 자본 + 실증 PF + MDD 세 가지 모두 충족해야 가능

### 버전 이력 추가:
```
| v9.5 | 2026-03-05 | Claude Code (Sonnet4.6) | T-090 Stage 자동 전환 엔진: StageManager 구현+056 마이그레이션+크론 등록 |
```

---

## 다음 단계

1. **PF 데이터 축적**: 실거래 데이터가 쌓이면 Stage 2 업그레이드 자동 판단
2. **DESK5 심층 재설계**: Stage 2 활성화 시 DESK5(10%) 운용 준비
3. **T-091**: HANDOVER v9.5 최종 업데이트 + project-docs push 확인

---

**보고서 경로**: /root/kis-autotrade-v4/report/v41/CUR-V41-STAGE-ENGINE-001-20260305.md
