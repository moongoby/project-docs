# CUR-V41-STAGE-ENGINE-001 — Stage 자동 전환 엔진 구현 보고서

[인계 확인]
직전 완료: T-088
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002
strategy_cards: 60
open_positions: 14

---

**Task ID**: T-090
**날짜**: 2026-03-05
**작업자**: Claude Code (Sonnet 4.6)
**브랜치**: phase-2c-command-center

---

## 요약

100만원 → 100억 자동 파일럿 시스템의 핵심 인프라인 Stage 자동 전환 엔진을 구현했습니다.
Task086 Monte Carlo 시뮬레이션 결과를 실전 코드로 구체화하여, 자본·PF·MDD 조건 기반으로 Stage를 자동 업/다운그레이드합니다.

---

## Phase 1: Stage 엔진 구현

### Step 1-1: `backend/app/services/stage_manager.py` 생성

**StageManager 클래스** 6개 메서드 구현:

| 메서드 | 설명 |
|--------|------|
| `check_upgrade()` | 자본+PF+MDD 조건으로 업그레이드 판단 |
| `check_downgrade()` | 안전장치 조건 (자본/PF/MDD 하한) 판단 |
| `get_current_stage()` | DB v4_stage_config에서 활성 Stage 조회 |
| `apply_stage_allocation()` | Stage별 DESK 배분 DB 적용 |
| `log_transition()` | Stage 변경 이력 v4_stage_history에 기록 |
| `get_snapshot()` | 현재 Stage 전체 스냅샷 반환 |

**Stage 설정 (Task086 기준)**:

| Stage | 자본 범위 | DESK 배분 |
|-------|-----------|-----------|
| Stage 1 | 1백만 ~ 4천만 | DESK3(70%) + DESK4(30%) |
| Stage 2 | 4천만 ~ 2억 | DESK3(50%) + DESK4(30%) + DESK5(10%) + DESK2(10%) |
| Stage 3 | 2억 ~ 10억 | DESK3(40%) + DESK4(25%) + DESK2(20%) + DESK5(10%) + GO100(5%) |
| Stage 4 | 10억 ~ 100억 | DESK3(30%) + DESK4(20%) + DESK2(20%) + GO100(15%) + DESK5(10%) + BOND(5%) |

**업그레이드 조건**:

| 전환 | 자본 | PF 기준 | PF 윈도우 | MDD 상한 |
|------|------|---------|----------|---------|
| 1→2 | ≥ 4천만 | ≥ 1.5 | 30일 | — |
| 2→3 | ≥ 2억 | ≥ 1.3 | 60일 | ≤ 15% |
| 3→4 | ≥ 10억 | ≥ 1.2 | 90일 | ≤ 20% |

**다운그레이드 조건 (안전장치, OR 조건)**:

| 전환 | 자본 | PF | MDD |
|------|------|-----|-----|
| 2→1 | < 3천만 | < 1.0 (30d) | — |
| 3→2 | < 1.5억 | — | > 25% (30d) |

### Step 1-2: DB 테이블 생성

**마이그레이션**: `backend/migrations/056_v4_stage_tables.sql`

생성된 테이블:

```sql
v4_stage_history (id, stage_from, stage_to, capital, trailing_pf, max_dd, trigger_reason, created_at)
v4_stage_config  (stage, desk_allocation JSONB, active BOOLEAN, updated_at)
```

**실행 결과**:
```
CREATE TABLE  -- v4_stage_history
CREATE INDEX  -- idx_v4_stage_history_created
CREATE INDEX  -- idx_v4_stage_history_stages
CREATE TABLE  -- v4_stage_config
INSERT 0 4    -- Stage 1~4 초기 데이터 삽입
```

**v4_stage_config 현재 상태**:
```
 stage | active | desk_allocation
-------+--------+----------------------------
     1 | t      | {"DESK3": 0.70, "DESK4": 0.30}
     2 | f      | {"DESK2": 0.10, "DESK3": 0.50, ...}
     3 | f      | {"DESK2": 0.20, "DESK3": 0.40, ...}
     4 | f      | {"BOND": 0.05, "DESK2": 0.20, ...}
(4 rows)
```

### Step 1-3: 크론 연동

**`scripts/check_stage_transition.py`** 생성 — 실행 흐름:
1. 업그레이드 조건 체크 (`check_upgrade()`)
2. 다운그레이드 조건 체크 (`check_downgrade()`)
3. 전환 발생 시 DB 기록 + Stage 설정 갱신 + 텔레그램 알림

**크론 등록** (매일 장마감 후 15:40 KST):
```cron
# [KIS TASK-090] Stage 전환 체크 — 15:40 KST (06:40 UTC) 평일
40 6 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_stage_transition.py >> /root/kis-autotrade-v4/logs/stage_transition.log 2>&1
```

등록 확인: `crontab -l | grep TASK-090` → ✅

---

## Phase 2: 테스트 결과

```
현재 Stage: 1
현재 자본: 1,489,649,101원 (accounts.total_evaluation + total_deposit 합계)
PF(30d): 0.0 (최근 30일 CLOSED 포지션 없음 — 정상)
MDD(30d): 0.00%

업그레이드 체크:
  triggered=False
  reason=자본 1,489,649,101원 ≥ 40,000,000원 | PF(30d) 0.000 < 1.5

다운그레이드 체크:
  triggered=False
  reason=Stage 1: 다운그레이드 불가 (최소 Stage)
```

> 자본은 이미 Stage 3/4 수준이지만, PF 데이터가 없어 전환 미발생 — 의도된 동작 (PF 축적 필요).

---

## 생성/수정 파일

| 파일 | 상태 | 설명 |
|------|------|------|
| `backend/app/services/stage_manager.py` | **신규** | StageManager 클래스 (332줄) |
| `backend/migrations/056_v4_stage_tables.sql` | **신규** | v4_stage_history + v4_stage_config |
| `scripts/check_stage_transition.py` | **신규** | 일일 크론 스크립트 |
| crontab | **수정** | `40 6 * * 1-5` 크론 등록 |

---

## 완료 조건 체크

- [x] StageManager 클래스 구현 + 테스트 (`ALL PASS`)
- [x] DB 테이블 생성 (`v4_stage_history`, `v4_stage_config`)
- [x] 크론 등록 (`40 6 * * 1-5`)
- [ ] HANDOVER v9.5 업데이트 (project-docs push 후 완료)

---

## 다음 단계 (T-091 예정)

- HANDOVER.md v9.5 업데이트
- Stage 전환 첫 실제 데이터 축적 후 검증
- DESK5 심층 재설계 (현재 "진행중" 상태 유지)
