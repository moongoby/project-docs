# CUR-GO100-REALISTIC-COST-001 + CUR-GO100-PIPELINE-SPLIT-001 보고서

**작성일**: 2026-02-25 20:00 KST
**우선순위**: P1
**상태**: **완료**

---

## 1. CUR-GO100-REALISTIC-COST-001: 현실적 거래비용 강제 주입

### 문제

- DESIGN 에이전트가 `risk_params`에 `slippage_model`을 설정하지 않음
- `build_cost_models(risk_params)` 호출 시 기본값 `slippage_model="none"` 적용
- 결과: **모든 AI 생성 전략의 백테스트가 슬리피지 0으로 실행** → 비현실적 수익률

### 해결: Orchestrator 레벨 강제 주입

`_run_full_pipeline()`에서 백테스트 전 `_inject_realistic_costs()` 호출:

| 파라미터 | 값 | 설명 |
|---------|---|------|
| `slippage_model` | `"tiered"` | 시총 순위별 기본 bp + 거래량 참여율 추가 bp |
| `min_trade_amount` | `100,000,000` (1억) | 최소 일거래대금 필터 |
| `max_volume_participation` | `0.05` (5%) | 최대 거래량 참여율 |
| `fill_position` | `"vwap_approx"` | VWAP 근사 체결가 |

**Tiered Slippage BP 구조**:
- 시총 순위 ≤100: 5bp, ≤300: 10bp, >300: 20bp
- 거래량 참여율 ≤1%: +0bp, ≤5%: +10bp, >5%: +30bp

**`setdefault` 사용** → DESIGN 에이전트가 명시적으로 설정한 값은 덮어쓰지 않음.

### 적용 범위

- `process_message()` 경로 (일반 전략 생성) → `_run_full_pipeline()` → 적용
- `run_from_intent()` 경로 (Goal 파이프라인) → `_run_full_pipeline()` → 적용
- **모든 AI 생성 전략에 일괄 적용**

---

## 2. CUR-GO100-PIPELINE-SPLIT-001: Goal 전략생성/백테스트 파이프라인 분리

### 문제

- Goal 2턴에서 DESIGN + DRAFT + BACKTEST + EVALUATE + OPTIMIZE를 모두 순차 실행
- 전략 3~4개 × (백테스트 + 최적화 루프) → 사용자 대기 시간 과다 (수 분)

### 해결: 2단계 분리

**Phase 1 (빠름, ~10초)**: 전략 설계 + DRAFT 저장 → 즉시 사용자에게 반환
- `run_from_intent(design_only=True)` → `_run_full_pipeline(skip_backtest=True)`
- 사용자는 DRAFT 카드 목록 즉시 확인 가능

**Phase 2 (백그라운드)**: `_bg_backtest_cards()` → 각 카드별 `run_backtest_pipeline_for_card()`
- 백테스트 → 평가 → 최적화 루프 (최대 5회) → BACKTESTED 확정
- 카드별 별도 DB 세션으로 안정적 실행
- 완료 시 카드 상태 자동 업데이트: DRAFT → BACKTESTED

### 변경 흐름

```
[기존]
Goal 2턴 → run_from_intent() → DESIGN → DRAFT → BACKTEST → EVALUATE → OPTIMIZE → FINALIZE
                                        (사용자 대기)

[변경]
Goal 2턴 → run_from_intent(design_only=True) → DESIGN → DRAFT → 즉시 반환
                                                          ↓
                                            _bg_backtest_cards() (백그라운드)
                                              ├─ card_1: BACKTEST → EVALUATE → FINALIZE
                                              ├─ card_2: BACKTEST → EVALUATE → FINALIZE
                                              └─ card_3: BACKTEST → EVALUATE → FINALIZE
```

### 새 메서드

| 메서드 | 위치 | 역할 |
|--------|------|------|
| `_inject_realistic_costs()` | `BaseOrchestrator` | tiered slippage + 유동성 필터 주입 |
| `run_backtest_pipeline_for_card()` | `BaseOrchestrator` | 카드 ID로 전략 로드 → 백테스트 파이프라인 |
| `_bg_backtest_cards()` | `ai_router.py` | 카드 목록 순회 백그라운드 백테스트 |

---

## 3. 변경 파일

| 파일 | 변경 | 비고 |
|------|------|------|
| `backend/app/services/go100/ai/base_orchestrator.py` | `_inject_realistic_costs()`, `skip_backtest`, `run_backtest_pipeline_for_card()` | 핵심 |
| `backend/app/routers/go100/ai_router.py` | `design_only=True`, `_bg_backtest_cards()`, 응답 안내 분기 | 핵심 |

## 4. 검증

- Python 문법 검사 통과
- `npx next build` 성공
- `go100.service` + `go100-frontend.service` 재시작 정상 (active/running)
- 코드 레포 커밋 `c6b3abe6` → `feat/CUR-GO100-BACKTEST-REALISTIC-001` 브랜치 푸시 완료
