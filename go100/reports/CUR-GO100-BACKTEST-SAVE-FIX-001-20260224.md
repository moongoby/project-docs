# CUR-GO100-BACKTEST-SAVE-FIX-001 — 백테스트 DB 저장 + 최적화/AI 연동 개선

**발행:** 2026-02-24  
**우선순위:** P0

## 1. 프론트 백테스트 API 호출 경로

- **확인 결과:** 프론트는 `POST /api/go100/backtest/run` 을 호출함.
- `frontend/src/go100/api/go100Api.ts`: `runBacktest(req)` → `go100Client.post(\`${BASE}/backtest/run\`, req)` (BASE = `/api/go100`).
- 전략 카드 상세의 재백테스트 버튼 등은 `runBacktest` 사용 → GO100 백테스트 API와 일치.

## 2. 백테스트 API 직접 호출 테스트

- **결과:** 로그인 계정 비밀번호 불일치(401)로 토큰 발급 실패. API 직접 호출 미실행.
- **권장:** 서버에서 유효한 계정으로 로그인 후 아래로 1건 실행·DB 확인 권장.
  ```bash
  TOKEN=$(curl -s -X POST http://localhost:8002/api/v1/auth/login ...)
  curl -s -X POST http://localhost:8002/api/go100/backtest/run \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d '{"go100_card_id": 18}'
  # 이후 go100_backtest_runs 최신 5건 조회
  ```
- **go100_backtest_runs:** 코드상 INSERT → UPDATE → `db.commit()` 이 존재하므로, API 성공 시 1건 저장되는 구조임.

## 3. 수정 사항

### 백테스트 DB 저장

- **이미 정상.** `backtest_service.py` 에서 RUNNING INSERT → 시뮬레이션 → COMPLETED UPDATE → 카드 last_backtest_* UPDATE → `await db.commit()` 순서로 처리됨.
- 헤더 주석 추가: `CUR-GO100-BACKTEST-SAVE-FIX-001, 2026-02-24 — DB 저장 검증 (INSERT/UPDATE/commit 유지)`.

### 최적화 DB 기록

- **backtest_optimizer.py:** `_create_opt_run` 이 매 반복에서 호출되며 내부에서 `await self.db.commit()` 수행. `_update_opt_run` 도 commit 수행. 추가 수정 없음.
- 헤더 주석 추가: `CUR-GO100-BACKTEST-SAVE-FIX-001, 2026-02-24 — 최적화 실행 시 DB 기록 보장 검증`.

### 백억이 AI 캐시 재사용

- **base_orchestrator.py:** 24시간 이내 결과 재사용 로직 **추가됨.**
- `_run_backtest()` 진입 시 `go100_backtest_runs` 에서 동일 `go100_card_id`, `status = 'COMPLETED'`, `completed_at > now() - interval '24 hours'` 조건으로 1건 조회.
- 조회 결과가 있으면 `result_detail` JSON 파싱 후 동일 형식의 dict 반환(캐시 히트). 로그: `Using cached backtest run {run_id} for card {card_id}`.
- 없으면 기존대로 분봉/일봉 백테스트 실행(캐시 미스).

## 4. 빌드/배포

- Python compile: **통과**
- pre-commit-check (Python + TypeScript): **통과**
- go100: **active (running)** (배포 후 재시작 완료)

## 5. 배포 후 검증

- 백테스트 실행: 로그인 실패로 **미실행** (수동 검증 권장).
- DB 저장: 코드 경로상 **정상 시 1건 INSERT·UPDATE 후 commit 됨.**

## 6. 백업·브랜치·배포 요약

- 백업: `/root/backups/20260224-backtest-fix/` (tables_backup.sql + backtest_service.py, backtest_router.py, backtest_optimizer.py, base_orchestrator.py)
- 브랜치: `feat/CUR-GO100-BACKTEST-SAVE-FIX-001` → `phase-2c-command-center` 에 병합·푸시 완료
- 변경 파일: `backtest_service.py`, `backtest_optimizer.py`, `base_orchestrator.py`
