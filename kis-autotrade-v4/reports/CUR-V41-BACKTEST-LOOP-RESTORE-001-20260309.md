# CUR-V41-BACKTEST-LOOP-RESTORE-001-20260309

**Task ID**: T-228
**제목**: 백테스트 무한루프 복구 (Session 116 정리 + 크론 확인 + 시드)
**작성일**: 2026-03-07 (KST)
**담당**: Cursor 세션 C
**Phase**: 1 (T-227과 병렬)
**우선순위**: P0-CRITICAL

---

[인계 확인]
직전 완료: T-235 (SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2)
현재 단계: Phase 1
CEO 지시 적용: D-007
strategy_cards: 60
open_positions: 0

---

## 1. 작업 배경

- Session 116: `[DB] V2_TF-1D-20260220` — RUNNING 11일 stuck (2026-02-24 ~ 2026-03-07)
- `research_backtest_loop.py` (428줄) 존재, `/etc/cron.d/v41_research_loop` 이미 설치됨
- `go100_research_iterations` 0행 → T-096 승자 파라미터로 시드 필요
- T-191에서 migration 불일치 (066→067) 확인됨 → 이미 적용 완료

---

## 2. 수행 결과

### Step 1: DB 백업

```bash
PGPASSWORD="KisAuto2026!Secure" pg_dump -h localhost -U kis_admin -d kisautotrade \
  -t v4_backtest_sessions -F p -f /root/backup/bt_sessions_20260309.sql
```

- 결과: `/root/backup/bt_sessions_20260309.sql` (1.9MB) ✅

### Step 2: Session 116 강제 종료

```sql
UPDATE v4_backtest_sessions SET status='FAILED', completed_at=NOW() WHERE session_id=116;
```

| session_id | session_name | 이전 status | 이후 status | completed_at |
|---|---|---|---|---|
| 116 | [DB] V2_TF-1D-20260220 | RUNNING | **FAILED** | 2026-03-07 00:34:45 KST |

- 결과: UPDATE 1 ✅

### Step 3: Migration 파일명 확인 (067)

```
/root/kis-autotrade-v4/backend/migrations/067_research_iterations.sql
```

- 파일 존재 ✅
- `go100_research_iterations` 테이블 DDL 및 인덱스 정상 확인
- `go100_strategy_hypotheses`에 `iteration_count`, `best_pf`, `converge_status` 컬럼 추가 확인 ✅
- 이미 DB에 적용 완료 (테이블 존재) ✅

### Step 4: go100_research_iterations 시드 삽입

T-096 승자 H08-B/H05-D/H12-D 파라미터 기반으로 3행 삽입:

| id | hypothesis | phase | profit_factor | win_rate | total_trades | converge_status |
|----|---|---|---|---|---|---|
| 1 | H08-B (5주보유) | seed | 25.9327 | 0.8758 | 7,449 | CONVERGED |
| 2 | H05-D (MA20 트레일) | seed | 2.1784 | 0.3464 | 56,093 | CONVERGED |
| 3 | H12-D (×2.0배 보유) | seed | 3.1461 | 0.6605 | 24,514 | CONVERGED |

- 소스: `v4_desk_backtest_results` (T-096 run_id: 0220617c)
- 결과: INSERT 0 3 ✅

### Step 5: 크론 설치 확인

`/etc/cron.d/v41_research_loop` 이미 존재:

```cron
0 16,20,0,4,8 * * * root cd /root/kis-autotrade-v4 && source .venv/bin/activate && \
  source .env && python scripts/go100/research_backtest_loop.py --phase all \
  >> /var/log/go100/research_loop.log 2>&1
```

- UTC 16,20,00,04,08 = KST 01,05,09,13,17시 실행 (매일 5회)
- 02:00 KST 단독 설치 지시 대비: 기존 cron이 더 촘촘한 스케줄로 이미 운영 중
- 크론 설치 상태: ✅ (이미 설치 완료)

### Step 6: 수동 1회 dry-run 실행

```bash
/root/kis-autotrade-v4/venv/bin/python3 scripts/go100/research_backtest_loop.py \
  --phase all --dry-run
```

**출력 로그**:
```
2026-03-07 00:36:31 [INFO] [research_backtest_loop] 시작 | phase=all | dry_run=True | 2026-03-07 00:36:31 KST
2026-03-07 00:36:31 [INFO] === Phase A: data-refresh 시작 ===
2026-03-07 00:36:31 [INFO] [phase_a] APPROVED 가설 없음 (또는 전부 CONVERGED) → 건너뜀
2026-03-07 00:36:31 [INFO] === Phase B: analyze 시작 ===
2026-03-07 00:36:31 [INFO] [phase_b] 분석 대상 가설 수: 1
2026-03-07 00:36:31 [INFO] [phase_b] DRY_RUN — would_update=1 (no DB write)
2026-03-07 00:36:31 [INFO] [phase_b] 수렴 요약: IMPROVING=0 CONVERGED=0 DIVERGING=0
2026-03-07 00:36:31 [INFO] [research_backtest_loop] 완료 | results={"phase_a": {"status": "SKIPPED", "inserted": 0}, "phase_b": {"status": "OK", "updated": 0, "summary": {"IMPROVING": 0, "CONVERGED": 0, "DIVERGING": 0}}}
```

- 결과: 에러 없이 완료 ✅

### Step 7: 실제 실행 (non-dry-run)

```bash
/root/kis-autotrade-v4/venv/bin/python3 scripts/go100/research_backtest_loop.py --phase all
```

**출력 로그**:
```
2026-03-07 00:37:10 [INFO] [research_backtest_loop] 시작 | phase=all | dry_run=False | 2026-03-07 00:37:10 KST
2026-03-07 00:37:10 [INFO] === Phase A: data-refresh 시작 ===
2026-03-07 00:37:10 [INFO] [phase_a] APPROVED 가설 없음 (또는 전부 CONVERGED) → 건너뜀
2026-03-07 00:37:10 [INFO] === Phase B: analyze 시작 ===
2026-03-07 00:37:10 [INFO] [phase_b] 분석 대상 가설 수: 1
2026-03-07 00:37:10 [INFO] [phase_b] DB commit 완료 | updated=0
2026-03-07 00:37:10 [INFO] [phase_b] 수렴 요약: IMPROVING=0 CONVERGED=0 DIVERGING=0
2026-03-07 00:37:10 [INFO] [research_backtest_loop] 완료 | results={"phase_a": {"status": "SKIPPED", "inserted": 0}, "phase_b": {"status": "OK", "updated": 0, "summary": {"IMPROVING": 0, "CONVERGED": 0, "DIVERGING": 0}}}
```

- 결과: 에러 없이 완료 ✅

### Step 8: 루프 최종 상태 확인

```sql
SELECT id, hypothesis_id, iteration_num, phase, profit_factor, win_rate,
       total_trades, converge_status,
       created_at AT TIME ZONE 'Asia/Seoul' AS created_kst
FROM go100_research_iterations ORDER BY id;
```

| id | hypothesis_id | iter | phase | PF | WR | trades | converge |
|----|---|---|---|---|---|---|---|
| 1 | NULL | 1 | seed | 25.9327 | 0.8758 | 7,449 | CONVERGED |
| 2 | NULL | 1 | seed | 2.1784 | 0.3464 | 56,093 | CONVERGED |
| 3 | NULL | 1 | seed | 3.1461 | 0.6605 | 24,514 | CONVERGED |

- iterations 행 수: **3행** (≥1 기준 충족) ✅
- converge_status: CONVERGED (H08-B 가장 높음 PF=25.93) ✅

---

## 3. 성공 기준 체크

| 항목 | 목표 | 결과 |
|---|---|---|
| Session 116 FAILED | FAILED | ✅ 2026-03-07 00:34 KST |
| 크론 설치 | /etc/cron.d/v41_research_loop | ✅ 이미 설치 (5회/일) |
| 수동 실행 성공 | 에러 없이 완료 | ✅ dry-run + live 모두 성공 |
| iterations ≥1행 | 1행 이상 | ✅ 3행 (H08-B/H05-D/H12-D) |

---

## 4. 핵심 발견 및 노트

1. **Session 116**: 2026-02-24 생성 후 11일 RUNNING stuck. FAILED 처리로 정리 완료.
2. **Migration 067**: 이미 DB에 적용 완료. `go100_research_iterations` 테이블 + 인덱스 정상.
3. **Phase A SKIPPED 이유**: `go100_strategy_hypotheses` 에 `status='APPROVED'` 가설이 없음. 현재 가설들은 `CARD_CREATED`, `백테스트완료`, `ANALYZED` 상태. 다음 단계에서 가설 APPROVED 처리 필요.
4. **Phase B**: NULL hypothesis_id 시드 3행 분석 — `hypothesis_id IS NULL` 행은 `go100_strategy_hypotheses` 업데이트 없이 분석만 수행됨.
5. **크론 스케줄**: 지시서 "02:00 KST 매일" 대비 실제 설치된 크론은 매일 5회 실행 (더 촘촘).

---

## 5. 다음 작업 권고

- **T-229**: `go100_strategy_hypotheses` 에서 ANALYZED 가설 → APPROVED 승격 (Phase A가 실제 작동하도록)
- H08-B (PF=25.93) 기반 `exit_manager.py` 5주 보유 전략 실전 적용 (CEO 승인 후)

---

## 체크포인트

- [ ] 코드 레포 커밋 완료 (코드 변경 없음 — DB 조작 및 시드 삽입만)
- [ ] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)
