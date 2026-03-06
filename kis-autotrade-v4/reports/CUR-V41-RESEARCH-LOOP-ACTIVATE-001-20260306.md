# CUR-V41-RESEARCH-LOOP-ACTIVATE-001-20260306

**Task ID**: T-199
**제목**: T-185 자율 루프 크론 설치 + 실행 활성화 (Phase C/D)
**우선순위**: P0-HIGH
**날짜**: 2026-03-06
**서버**: 211 (kis-autotrade-v4)

---

## Step A: migration 067 적용 결과

```
psql:/root/kis-autotrade-v4/backend/migrations/067_research_iterations.sql:19:
  NOTICE: relation "go100_research_iterations" already exists, skipping
CREATE TABLE
CREATE INDEX (idx_research_iters_hypothesis)
CREATE INDEX (idx_research_iters_converge)
ALTER TABLE (iteration_count 이미 존재)
ALTER TABLE (best_pf 이미 존재)
ALTER TABLE (converge_status 이미 존재)
→ 테이블 이미 이전 세션에서 생성됨 (IF NOT EXISTS로 안전 통과)
```

## Step B: go100_research_iterations 테이블 검증

```sql
SELECT count(*) FROM go100_research_iterations;
 count
-------
     0
(1 row)
```
→ 테이블 존재 확인, 레코드 0건 (정상 — 아직 루프 미실행)

## Step C: .env 설정 확인

```
GO100_EVOLUTION_LOOP_ENABLED=true
```
→ 이미 true, 변경 불필요

## Step D: 크론 파일 배포

경로: `/etc/cron.d/v41_research_loop`

```
0 16,20,0,4,8 * * * root cd /root/kis-autotrade-v4 && source .venv/bin/activate && source .env && python scripts/go100/research_backtest_loop.py --phase all >> /var/log/go100/research_loop.log 2>&1
30 17 * * 1-5 root cd /root/kis-autotrade-v4 && source .venv/bin/activate && source .env && python scripts/go100/shadow_compare.py >> /var/log/go100/shadow_compare.log 2>&1
```

로그 디렉토리: `/var/log/go100/` (생성 완료)
권한: 644

## Step E: Dry-Run 결과

```
2026-03-06 22:18:02 [INFO] [research_backtest_loop] 시작 | phase=data-refresh | dry_run=True
2026-03-06 22:18:02 [INFO] === Phase A: data-refresh 시작 ===
2026-03-06 22:18:02 [INFO] [phase_a] APPROVED 가설 없음 (또는 전부 CONVERGED) → 건너뜀
2026-03-06 22:18:02 [INFO] [research_backtest_loop] 완료 | results={"phase_a": {"status": "SKIPPED", "inserted": 0}}
```
→ 오류 없이 정상 완료 (APPROVED 가설 없어서 SKIPPED — 정상)

## 최종 상태

| 항목 | 결과 |
|------|------|
| migration 067 | ✅ 적용 완료 |
| go100_research_iterations 테이블 | ✅ 존재 확인 |
| GO100_EVOLUTION_LOOP_ENABLED | ✅ true |
| 크론 파일 배포 | ✅ /etc/cron.d/v41_research_loop |
| dry-run | ✅ 오류 없음 |

## 스케줄

- 매일 16:00, 20:00, 00:00, 04:00, 08:00 → research_backtest_loop.py --phase all
- 평일 17:30 → shadow_compare.py
