# CUR-GO100-MARKET-REGIME-001 — 시장 레짐 분류 시스템 보고서

**작성:** 2026-02-25  
**작업:** 시장 레짐 분석기 + Design/Evaluate 레짐 연동  
**트랙:** G — 시장 레짐 분류 시스템  
**우선순위:** P2

---

## 1. 요약

- **RegimeAnalyzer:** `v4_market_regime_daily`(KOSPI 기준) 기반 현재/이력 조회, LLM용 컨텍스트 문자열 생성, 백테스트 거래 레짐별 분류.
- **DESIGN 단계:** DESIGN 전 `get_regime_context_for_llm()` 호출 후, 시스템 프롬프트 끝에 "현재 시장 레짐 정보" 블록 추가. 상승/하락/횡보에 따른 전략 권장 문구 포함.
- **EVALUATE 단계:** 백테스트 `trade_log`를 진입일 기준 레짐별 분류 후 `regime_analysis` 필드로 반환. 특정 레짐에서 승률·평균수익 저조 시 `weaknesses`에 추가.

## 2. 변경 파일

| 구분 | 경로 |
|------|------|
| 신규 | backend/app/services/go100/ai/regime_analyzer.py |
| 수정 | backend/app/services/go100/ai/base_orchestrator.py (레짐 컨텍스트 주입, evaluate 시 regime_analyzer 전달) |
| 수정 | backend/app/services/go100/ai/prompts.py (REGIME_CONTEXT_SECTION 추가) |
| 수정 | backend/app/services/go100/ai/llm_client.py (call_design에 regime_context, system_prompt에 레짐 블록) |
| 수정 | backend/app/services/go100/ai/design_agent.py (design(..., regime_context=) 전달) |
| 수정 | backend/app/services/go100/ai/evaluate_agent.py (regime_analyzer 인자, regime_analysis·weakness 반영) |
| 수정 | backend/app/services/go100/ai/schemas.py (EvaluationResult.regime_analysis 필드) |

- **DB:** 변경 없음. `v4_market_regime_daily` 읽기만 사용.
- **프론트엔드:** 변경 없음.

## 3. RegimeAnalyzer API

| 메서드 | 설명 |
|--------|------|
| `get_current_regime()` | 최신 1건 레짐 (date, regime=BULL/BEAR/SIDEWAYS, confidence, kospi_ret_20d, vkospi) |
| `get_regime_history(days)` | 최근 N일 레짐 이력 |
| `get_regime_context_for_llm()` | LLM 프롬프트용 한글 요약 문자열 |
| `classify_backtest_by_regime(trades)` | trade_log를 진입일 레짐별로 분류 → BULL/BEAR/SIDEWAYS별 trades, win_rate, avg_return |
| `suggest_adjustments(regime, strategy_params)` | 레짐별 파라미터 조정 제안 (BULL: 포지션↑ 손절완화, BEAR: 포지션↓ 손절강화, SIDEWAYS: 표준) |

- V4.1 DB 레짐값(STRONG_TREND_UP, MILD_TREND_UP, SIDEWAYS, MILD_TREND_DOWN, STRONG_TREND_DOWN)은 BULL/BEAR/SIDEWAYS로 매핑하여 사용.

## 4. 검증

- **8-1.** RegimeAnalyzer 단독 로드: `python3 -c "importlib로 regime_analyzer.py 직접 로드"` → OK.
- **8-2.** 레짐 데이터 확인: 서버에서 `SELECT COUNT(*) FROM v4_market_regime_daily;` / `v4_vkospi_daily` 실행 권장.
- **8-3.** 서비스 재시작: **kis-v41-* 절대 재시작 금지.** go100만 필요 시 `systemctl restart go100`, `curl -s http://localhost:8002/health` 확인.
- **8-4.** 채팅 테스트: go100.newtalk.kr에서 "전략 만들어줘" 요청 시 응답에 시장 레짐 관련 문구 포함 여부 확인.

## 5. 커밋 & 병합 (지시서 9절)

```bash
cd /root/kis-autotrade-v4
bash scripts/pre-commit-check.sh
git add backend/app/services/go100/ai/regime_analyzer.py
git add backend/app/services/go100/ai/base_orchestrator.py
git add backend/app/services/go100/ai/prompts.py
git add backend/app/services/go100/ai/llm_client.py
git add backend/app/services/go100/ai/design_agent.py
git add backend/app/services/go100/ai/evaluate_agent.py
git add backend/app/services/go100/ai/schemas.py
git commit -m "feat: CUR-GO100-MARKET-REGIME-001 - 시장레짐 분석기 + Design/Evaluate 레짐 연동"

git checkout phase-2c-command-center
git pull origin phase-2c-command-center
git merge feat/CUR-GO100-MARKET-REGIME-001 --no-ff
git push origin phase-2c-command-center
```

(브랜치 `feat/CUR-GO100-MARKET-REGIME-001`는 지시서 3절에 따라 `phase-2c-command-center`에서 생성 후 위 파일만 커밋.)

## 6. 다음 단계

- 레짐 백필 구간 확대 시 `v4_market_regime_daily` 행 수 증가에 따라 `get_regime_history` 기간 자동 반영.
- KOSDAQ 레짐 병렬 사용 시 `get_current_regime(market_type="KOSDAQ")` 등 파라미터 확장 검토.
