# CUR-GO100-OPTIMIZER-CORE-FIX-001 — Optimizer 코어 수정 보고서

**작성:** 2026-02-25  
**작업 ID:** CUR-GO100-OPTIMIZER-CORE-FIX-001  
**브랜치:** fix/CUR-GO100-OPTIMIZER-CORE-FIX-001 → phase-2c-command-center  
**우선순위:** P0

---

## 1. 사전확인 결과 (SKIP 판단)

| # | 항목 | 결과 | 비고 |
|---|------|------|------|
| 1 | BacktestOptimizer에서 OpenAI 직접 호출 | `model="gpt-4o"`, `self.llm.chat.completions.create` 존재 | **수정 대상** |
| 2 | LLMGateway 사용 여부 | `llm_client` 인자만 있고 Gateway 미사용 | **수정 대상** |
| 3 | 캐시 키 로직 | 24시간 + completed_at 조건 존재 | 기반영 확인 |
| 4 | 캐시 조건에 파라미터 해시 | 없음 (entry_rules, exit_rules 등 미반영) | **수정 대상** |
| 5 | LLMGateway 구조 | `app/core/llm_gateway.py`, RequestType.DESIGN_CHAT 등 | 기반영 확인 |
| 6 | .env LLM 설정 | (마스킹 권장으로 생략) | 기반영 확인 |

**SKIP 항목:** 없음. 전 항목 적용 완료.

---

## 2. P0-4: BacktestOptimizer LLMGateway 통합

### 제거한 것
- **ai_router.py:** `import openai`, `openai.AsyncOpenAI(api_key=...)` 제거.
- **backtest_optimizer.py:** `self.llm.chat.completions.create(model="gpt-4o", response_format={"type": "json_object"}, ...)` 제거. (OpenAI 직접 호출 0건)

### 추가·연결한 것
- **backtest_optimizer.py:**
  - `from backend.app.core.llm_gateway import LLMGateway`
  - `from backend.app.core.llm_models import LLMRequest, LLMResponse, RequestType`
  - `_extract_json()` 로컬 함수 추가 (```json ... ``` 또는 `{...}` 추출).
  - `_analyze_with_llm` 내부: `LLMGateway.get_instance()` → `LLMRequest(request_type=RequestType.DESIGN_CHAT, messages=..., system_prompt=..., temperature=0.3, max_tokens=4096)` → `gateway.send(request)` → `_extract_json(response.content)`.
  - ANALYSIS_PROMPT 끝에 한 줄 추가: "응답은 반드시 ```json ... ``` 블록으로만 작성하세요." (품질 유지, JSON 블록 추출 호환).
- **ai_router.py:** `BacktestOptimizer(..., llm_client=None)` — LLM은 옵티마이저 내부에서 Gateway 사용.

### 검증
- `grep -c "AsyncOpenAI\|from openai" backtest_optimizer.py` → **0**
- `grep -c "LLMGateway\|llm_gateway\|LLMClient\|llm_client" backtest_optimizer.py` → **1 이상** (LLMGateway 사용 확인)
- `python3 -c "from backend.app.services.go100.optimizer.backtest_optimizer import BacktestOptimizer; print('OK')"` → **OK** (venv 기준)

---

## 3. P0-5: 24시간 캐시 키 보정

### 선택: **옵션 A (캐시 키에 파라미터 해시 추가)**

**이유:**  
- 옵션 B(최적화 루프 중 force_run=True)는 “항상 새로 실행”이라 24시간 캐시 이점을 못 씀.  
- 옵션 A는 동일 카드·동일 파라미터일 때만 캐시 재사용하여, 최적화 루프에서 파라미터가 바뀔 때마다 올바르게 새 백테스트 실행 가능.

### 구현 내용
- **base_orchestrator.py:**
  - `_compute_params_hash(card_params)` 추가: `entry_rules`, `exit_rules`, `risk_params`, `universe_filter` 정렬 JSON → MD5 앞 12자.
  - `_run_backtest` 캐시 조회: `WHERE ... AND (params_hash IS NULL OR params_hash = :params_hash)` 추가. 기존 레코드(params_hash NULL)도 계속 매칭.
- **backtest_service.py:**
  - `_compute_params_hash(card_params)` 동일 로직 추가.
  - `create_backtest_run` INSERT 시 카드 row 기준으로 `params_hash` 계산 후 `params_hash` 컬럼에 저장.
- **마이그레이션:** `028_go100_backtest_runs_params_hash.sql`  
  - `ALTER TABLE go100_backtest_runs ADD COLUMN IF NOT EXISTS params_hash VARCHAR(12);`

### DB ALTER 실행 여부
- **서버([SERVER-IP])에서 수동 실행 필요.**  
  - 로컬 검증 시 Peer 인증으로 psql 접속 불가.  
  - 배포 후 다음 실행 권장:  
    `PGPASSWORD='...' psql -U kis_admin -d kisautotrade -f backend/migrations/028_go100_backtest_runs_params_hash.sql`

---

## 4. 변경 파일 목록

| 파일 | 작업 | 비고 |
|------|------|------|
| backend/app/services/go100/optimizer/backtest_optimizer.py | 수정 | OpenAI 제거, LLMGateway 통합, _extract_json |
| backend/app/services/go100/ai/base_orchestrator.py | 수정 | _compute_params_hash, 캐시 조회에 params_hash 반영 |
| backend/app/routers/go100/ai_router.py | 수정 | openai 제거, llm_client=None |
| backend/app/services/go100/backtest/backtest_service.py | 수정 | _compute_params_hash, INSERT 시 params_hash 저장 |
| backend/migrations/028_go100_backtest_runs_params_hash.sql | 신규 | params_hash 컬럼 추가 |

---

## 5. 검증 요약

- **Python import:** `BacktestOptimizer`, `BaseOrchestrator` venv 기준 정상.
- **OpenAI 직접 호출 grep:** backtest_optimizer.py 내 0건.
- **LLMGateway 사용 grep:** backtest_optimizer.py 내 1 이상.
- **params_hash / force_run grep:** base_orchestrator.py 내 params_hash 사용 확인.
- **pre-commit-check.sh:** 통과 (Python/TypeScript).
- **헬스체크:** 서버 환경에 따라 `systemctl restart go100` 후 `curl -s http://localhost:8002/health` 수동 확인 권장.

---

## 6. 커밋 및 머지

- **커밋:** `fix: CUR-GO100-OPTIMIZER-CORE-FIX-001 - LLMGateway 통합 + 캐시키 보정`
- **머지:** fix/CUR-GO100-OPTIMIZER-CORE-FIX-001 → phase-2c-command-center (--no-ff)
- **푸시:** origin phase-2c-command-center 완료

---

## 7. 참고

- 백업: `/root/backup/optimizer-fix-20260225-094622`
- 기술명세: BAEKEOGI-TECH-SPEC.md §5, §7
- 인계서: HANDOVER-20260225-V3 §10 (BacktestOptimizer GPT-4o 하드코딩, 24시간 캐시 버그)
