# CUR-GO100-MARKET-REGIME-001 — 시장 레짐 연동 보고서

**작성:** 2026-02-25  
**작업 ID:** CUR-GO100-MARKET-REGIME-001  
**트랙:** G — GO100 시장 레짐 연동  
**우선순위:** P2  
**브랜치:** feat/CUR-GO100-MARKET-REGIME-001 → phase-2c-command-center

---

## 1. 사전 확인 결과 (지시서 1절)

| 항목 | 결과 | 비고 |
|------|------|------|
| 1-1. RegimeAnalyzer 존재 여부 | **기 반영** | `regime_analyzer.py` 존재, 내용 완전 (CUR-GO100-MARKET-REGIME-001 헤더, get_current_regime / get_regime_context_for_llm / classify_backtest_by_regime 등 구현됨) |
| 1-2. base_orchestrator.py 레짐 컨텍스트 주입 | **기 반영** | `regime_analyzer` import, `get_regime_context_for_llm` 호출, DesignAgent 호출 시 `regime_context` 전달 있음 |
| 1-3. prompts.py 레짐 컨텍스트 플레이스홀더 | **기 반영** | `regime_context`, "시장 레짐 정보" 섹션 존재 |
| 1-4. evaluate_agent.py 레짐별 분석 | **기 반영** | `classify_backtest_by_regime` 호출, `regime_analysis`·weaknesses 반영 있음 |
| 1-5. advanced_filters.py 레짐 소스 | **미반영 → 수정함** | 기존: 자체 계산 + STRONG_BULL/STRONG_BEAR 명칭. v4_market_regime_daily 조회 전환 및 V4.1 명칭 통일 적용 |

---

## 2. 레짐 명칭 통일 결정

- **정본:** V4.1 DB `v4_market_regime_daily` (552건, KOSPI/KOSDAQ).
- **명칭:** STRONG_TREND_UP / MILD_TREND_UP / SIDEWAYS / MILD_TREND_DOWN / STRONG_TREND_DOWN.
- **GO100 통일:** advanced_filters.py 기존 자체 계산 명칭(STRONG_BULL/STRONG_BEAR) → V4.1 명칭으로 매핑·반환 통일.

---

## 3. 수정한 항목 (이번 작업)

### 3.1 변경 파일

| 구분 | 경로 |
|------|------|
| 수정 | backend/app/services/go100/universe/advanced_filters.py |

- **신규 생성:** 없음 (RegimeAnalyzer·base_orchestrator·prompts·evaluate_agent는 기 반영으로 SKIP).
- **DB/프론트/보호 파일:** 변경 없음.

### 3.2 advanced_filters.py 변경 내용

- **헤더:** `# CUR-GO100-MARKET-REGIME-001, 2026-02-25` 추가.
- **get_market_regime():**
  1. **우선:** `v4_market_regime_daily`에서 `market_type='KOSPI'`, `date <= ref_date` 조건으로 최신 1건 조회.  
     반환 시 구 명칭(STRONG_BULL/STRONG_BEAR) → V4.1 명칭(STRONG_TREND_UP/STRONG_TREND_DOWN) 매핑.
  2. **Fallback:** 조회 실패 또는 0건 시 기존 자체 계산 로직(`_get_market_regime_fallback`) 호출.  
     자체 계산 반환 시에도 명칭을 V4.1로 통일(STRONG_BULL→STRONG_TREND_UP, STRONG_BEAR→STRONG_TREND_DOWN).
- **신규:** `_REGIME_V41_MAP`, `_get_market_regime_fallback()` 추가.

---

## 4. SKIP한 항목 및 사유

| 항목 | 사유 |
|------|------|
| RegimeAnalyzer 신규 생성 | 이미 존재·구현 완료 (기 반영) |
| base_orchestrator.py 레짐 주입 | 이미 regime_context 주입·Design 호출 시 전달 반영됨 |
| prompts.py 레짐 블록 | 이미 regime_context·시장 레짐 정보 섹션 있음 |
| evaluate_agent.py 레짐별 분석 | 이미 classify_backtest_by_regime·regime_analysis·weaknesses 반영됨 |

---

## 5. 검증

- **pre-commit-check.sh:** 통과 (Python/TypeScript).
- **Lint:** advanced_filters.py 에러 없음.
- **Import:** 로컬에서 venv 미활성으로 인해 전체 패키지 import 실패 가능. 서버([SERVER-IP])에서 다음 권장:
  - `python3 -c "from backend.app.services.go100.universe.advanced_filters import Go100AdvancedFilters; print('OK')"`
  - `PGPASSWORD='...' psql -U kis_admin -d kisautotrade -c "SELECT COUNT(*), market_type, MAX(date) FROM v4_market_regime_daily GROUP BY market_type;"`
- **서비스 재시작:** kis-v41-* 절대 재시작 금지. go100만 필요 시 `systemctl restart go100`, `curl -s http://localhost:8002/health` 확인.

---

## 6. 커밋 & 병합 (완료)

- **커밋:** `feat: CUR-GO100-MARKET-REGIME-001 - advanced_filters 레짐 소스 v4_market_regime_daily 조회 전환 + V4.1 명칭 (기반영 제외)`  
  - 변경: `backend/app/services/go100/universe/advanced_filters.py` 1파일만.
- **병합:** `phase-2c-command-center`에 `feat/CUR-GO100-MARKET-REGIME-001` merge --no-ff 완료.
- **Push:** `git push origin phase-2c-command-center` 실행 (네트워크 지연 시 서버에서 재시도 권장).

---

## 7. 서비스 상태

- health check는 서버([SERVER-IP])에서 `curl -s http://localhost:8002/health | python3 -m json.tool` 로 확인.
- 보고서 작성 시점에는 로컬에서 go100 프로세스 미실행 가능.

---

## 8. 참고

- **AUDIT:** [CUR-GO100-MARKET-REGIME-AUDIT-001-20260224.md](CUR-GO100-MARKET-REGIME-AUDIT-001-20260224.md) — v4_market_regime_daily 552건, GO100 자체 계산 vs V4.1 명칭 불일치 정리.
- **기 반영된 RegimeAnalyzer·Design/Evaluate 연동:** 이전 작업에서 반영 완료. 본 작업에서는 advanced_filters.py 레짐 소스 전환만 수행.
