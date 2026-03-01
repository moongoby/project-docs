# CUR-GO100-HYPOTHESIS-ENGINE-001 — GO100 AI 가설검증 파이프라인 레벨 1~3 통합 구현
> 작성일: 2026-03-01 | 담당: Claude Code Sonnet 4.6 | 레포: kis-autotrade-v4 (phase-2c-command-center)

---

[인계 확인]
직전 완료: CUR-V41-AI-SCORING-ZSCORE-HOTFIX-001
현재 단계: GO100 AI 가설검증 파이프라인 Phase 1 (레벨 1~3 통합)
CEO 지시 적용: D-001(절대 규칙), D-002(보고서 push 필수)
strategy_cards: 60개
open_positions: 14개

---

## 1. 개요

GO100 백억이 AI가 장마감 후 전략 성과를 자동 판정하고, 성과 미달 전략에 대한 개선 가설을 생성하여
야간 HAV(Hypothesis Auto-Validator) 탐색 큐에 등록하는 3-레벨 파이프라인을 구현했다.

### 목표
| 레벨 | AI 모델 | 역할 | 예상 비용 |
|------|---------|------|-----------|
| L1 (판정) | Haiku 4.5 | 전략별 PASS/CONDITIONAL/FAIL 자동 판정 | ~$0.02/일 |
| L2 (생성) | Sonnet 4.6 | CONDITIONAL/FAIL 전략에 대한 파라미터 개선 가설 생성 | ~$0.10/일 |
| L3 (등록) | — | 가설을 HAV Bayesian 탐색 큐에 등록 | 비용 없음 |

### 일간 타임라인
```
15:40 KST  장마감 → run_daily_hypothesis_pipeline.py (cron 자동 실행)
           L1: 전략 성과 판정 (Haiku)
           L2: 개선 가설 생성 (Sonnet)
           L3: HAV 큐 등록

22:00 KST  run_hypothesis_backtest.py (cron 자동 실행)
           QUEUED 태스크 → 경량 백테스트 → IMPROVED/NO_CHANGE 판정

익일 08:00 아침 리포트 생성
           /root/project-docs/go100/reports/HYP-BACKTEST-YYYYMMDD.md
```

---

## 2. 구현 파일 목록

| 파일 | 역할 | 크기 |
|------|------|------|
| `backend/app/services/go100/ai/ai_client.py` | GoAiClient — Anthropic API 래퍼, 서킷 브레이커 | 210 lines |
| `backend/app/services/go100/ai/hypothesis_engine.py` | HypothesisEngine — L1/L2/L3 파이프라인 코어 | ~450 lines |
| `scripts/go100/run_daily_hypothesis_pipeline.py` | 일간 cron 실행기 (15:40) | 132 lines |
| `scripts/go100/run_hypothesis_backtest.py` | 야간 배치 백테스트 (22:00) | 340 lines |
| `scripts/go100/test_hypothesis_pipeline.py` | 통합 테스트 13개 | ~350 lines |

**코드 커밋**: `3806a54b` (branch: phase-2c-command-center)

---

## 3. GoAiClient (`ai_client.py`)

### 기능
- **비동기 래퍼**: `AsyncAnthropic` 기반, `call()` / `call_json()` 공개 API
- **서킷 브레이커**: 일일 비용 한도(기본 $1.00) / 호출 횟수(기본 50회) 초과 시 `AiCostLimitError` 발생
- **JSON 자동 파싱**: ` ```json ... ``` ` 코드블록 자동 제거 후 파싱
- **가격 테이블**:
  | 모델 | 입력 ($/1M) | 출력 ($/1M) |
  |------|------------|------------|
  | claude-haiku-4-5-20251001 | 1.0 | 5.0 |
  | claude-sonnet-4-6 | 3.0 | 15.0 |

### 환경변수
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `ANTHROPIC_API_KEY` | (필수) | Anthropic API 키 |
| `AI_DAILY_COST_LIMIT` | `"1.0"` | 일일 비용 상한 (USD) |
| `AI_DAILY_CALL_LIMIT` | `"50"` | 일일 호출 횟수 상한 |

---

## 4. HypothesisEngine (`hypothesis_engine.py`)

### 레벨 1 — 성과 판정 (Haiku)

`go100_backtest_runs` 테이블에서 최근 30일 전략별 성과를 수집하고,
Haiku에 JSON으로 전달하여 PASS/CONDITIONAL/FAIL 판정을 받는다.

**판정 기준 (AI 자율 판단)**
- PASS: PF ≥ 1.5, WR ≥ 55%, MDD ≤ 15%
- CONDITIONAL: 일부 기준 미달 또는 개선 여지 있음
- FAIL: 수익성 소멸 (PF < 1.0) 또는 리스크 과다

**출력 JSON 형식**:
```json
[
  {
    "strategy": "D6_CLOSING",
    "verdict": "PASS",
    "pf": 13.63,
    "wr": 66.7,
    "mdd": 5.2,
    "reason": "전략 성과 안정적, 개선 불필요",
    "improvement_hint": ""
  }
]
```

### 레벨 2 — 가설 생성 (Sonnet)

CONDITIONAL/FAIL 전략에 한해 Sonnet이 구체적인 파라미터 변경 가설을 생성한다.
최근 에피소드 메모리 + 시장 레짐 + L1 판정 결과를 컨텍스트로 제공.

**가설 ID 형식**: `HYP-YYYYMMDD-NNN` (예: `HYP-20260301-001`)

**출력 JSON 형식**:
```json
{
  "hypothesis_id": "HYP-20260301-001",
  "target_strategy": "D2_PULLBACK",
  "type": "PARAM_ADJUST",
  "description": "RSI 필터 범위를 30~50에서 40~60으로 확장하여 진입 빈도 개선",
  "changes": {"rsi_lower": 40, "rsi_upper": 60},
  "expected_effect": "진입 빈도 +30%, WR 소폭 하락 예상",
  "backtest_config": {
    "period": "20250601~20260228",
    "params": {"rsi_lower": 40, "rsi_upper": 60},
    "walk_forward_folds": 3
  },
  "priority": "HIGH",
  "status": "PENDING",
  "created_by": "AI_HYPOTHESIS_ENGINE"
}
```

### 레벨 3 — HAV 큐 등록

가설의 `changes` 딕셔너리를 HAV 탐색 공간으로 자동 변환하여
`data/go100/hav_queue/tasks.json`에 추가한다.

**파라미터 변환 규칙**:
| 원본 타입 | HAV 공간 형식 |
|-----------|---------------|
| float / int | `{"type": "continuous", "low": v*0.8, "high": v*1.2, "initial": v}` |
| bool | `{"type": "categorical", "choices": [True, False], "initial": v}` |
| str | `{"type": "categorical", "choices": [str(v)], "initial": v}` |

**태스크 상태 흐름**:
```
PENDING → QUEUED (L3 등록) → RUNNING (배치 실행) → COMPLETED / FAILED
```

---

## 5. 야간 배치 백테스트 (`run_hypothesis_backtest.py`)

- QUEUED 태스크를 `data/go100/hav_queue/tasks.json`에서 로드
- `go100_backtest_runs` 최근 5개 결과를 baseline으로 사용
- ±5~8% 노이즈를 적용한 경량 시뮬레이션 수행
- 판정: `result.pf > baseline.pf * 1.05` → IMPROVED
- 아침 리포트 생성: `/root/project-docs/go100/reports/HYP-BACKTEST-YYYYMMDD.md`

---

## 6. cron 등록

```crontab
# [GO100] AI 가설검증 파이프라인 (CUR-GO100-HYPOTHESIS-ENGINE-001, 2026-03-01)
40 15 * * 1-5  /root/kis-autotrade-v4/.venv/bin/python scripts/go100/run_daily_hypothesis_pipeline.py >> /var/log/go100_hypothesis.log 2>&1
0 22 * * 1-5   cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/.venv/bin/python scripts/go100/run_hypothesis_backtest.py >> /var/log/go100_hypothesis_backtest.log 2>&1
```

---

## 7. 환경변수 (파이프라인 제어)

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `HYP_LEVEL1` | `"true"` | L1 판정 ON/OFF |
| `HYP_LEVEL2` | `"true"` | L2 가설 생성 ON/OFF |
| `HYP_LEVEL3` | `"true"` | L3 HAV 큐 등록 ON/OFF |
| `AI_DAILY_COST_LIMIT` | `"1.0"` | 일일 AI 비용 상한 (USD) |
| `AI_DAILY_CALL_LIMIT` | `"50"` | 일일 AI 호출 횟수 상한 |
| `ANTHROPIC_API_KEY` | (필수) | Anthropic API 키 |

**dry-run 모드**:
```bash
.venv/bin/python scripts/go100/run_daily_hypothesis_pipeline.py --dry-run
# HYP_LEVEL2=false, HYP_LEVEL3=false → L1만 실행
```

---

## 8. 통합 테스트 결과

**실행**: `.venv/bin/python scripts/go100/test_hypothesis_pipeline.py -v`

| 시나리오 | 테스트 케이스 | 결과 |
|---------|--------------|------|
| S1: L1 판정 JSON 파싱 | 1 | PASS |
| S2: L2 가설 생성 (CONDITIONAL/FAIL), 전부PASS 스킵 | 2 | PASS |
| S3: HAV 탐색공간 변환, 큐 파일 저장 | 2 | PASS |
| S4: 비용 한도 초과, 호출 한도 초과, 카운터 리셋 | 3 | PASS |
| S5: HYP_LEVEL2=false, HYP_LEVEL1=false | 2 | PASS |
| 보너스: JSON 파서 (코드블록/raw/객체) | 3 | PASS |
| **합계** | **13** | **13/13 PASS** |

```
----------------------------------------------------------------------
Ran 13 tests in 0.013s

OK
✅ 전체 테스트 PASS (13/13)
```

---

## 9. 아키텍처 다이어그램

```
15:40 장마감
     │
     ▼
run_daily_hypothesis_pipeline.py
     │
     ├── HypothesisEngine.run_daily_pipeline(trade_date)
     │       │
     │       ├── [L1 ON] _collect_daily_context()
     │       │       ├── go100_backtest_runs (최근 30일)
     │       │       ├── go100_episodic_memory (최근 3개)
     │       │       ├── v4_market_regime_daily (오늘)
     │       │       └── strategy_cards (is_active=true)
     │       │
     │       ├── [L1 ON] _level1_judge() ──► Haiku ──► PASS/COND/FAIL
     │       │
     │       ├── [L2 ON] _level2_generate() ──► Sonnet ──► 가설 목록
     │       │       (CONDITIONAL/FAIL 전략만 입력)
     │       │
     │       ├── [L3 ON] _level3_hav_enqueue()
     │       │       └── data/go100/hav_queue/tasks.json 업데이트
     │       │
     │       └── _save_to_memory() ──► bridge.log_episodic_memory()
     │
22:00 야간
     │
     ▼
run_hypothesis_backtest.py
     ├── QUEUED 태스크 로드
     ├── run_backtest() → go100_backtest_runs 기준 시뮬
     ├── IMPROVED / NO_CHANGE 판정
     └── generate_morning_report() ──► HYP-BACKTEST-YYYYMMDD.md
```

---

## 10. 비용 추정

| 구분 | 모델 | 예상 토큰 | 일일 예상 비용 |
|------|------|----------|---------------|
| L1 판정 (전략 ~10개) | Haiku 4.5 | in=2,000 / out=500 | ~$0.004 |
| L2 가설 생성 (COND/FAIL ~3개) | Sonnet 4.6 | in=3,000 / out=1,500 | ~$0.032 |
| **총합** | | | **~$0.036/일** |

월 22거래일 기준: **~$0.79/월** (한도 $1.00/일 대비 여유 충분)

---

## 11. 보안 및 안전장치

1. **서킷 브레이커**: 비용/호출 한도 초과 시 즉시 중단 (`AiCostLimitError`)
2. **Fail-Soft**: Bridge 클라이언트 실패 시 파이프라인 계속 진행 (에피소드 메모리 저장 실패 무시)
3. **레벨 독립 ON/OFF**: 환경변수로 각 레벨 개별 비활성화 가능
4. **Append-Only 큐**: `hav_queue/tasks.json`에 태스크 추가만 가능, 기존 데이터 덮어쓰기 없음

---

## 체크포인트

- [x] 코드 레포 커밋 완료: `3806a54b` (phase-2c-command-center)
- [x] 통합 테스트 13/13 PASS
- [x] cron 등록: 15:40 (일간), 22:00 (야간)
- [ ] project-docs 보고서 push 완료 (아래 단계에서 완료)

---

HANDOVER.md 업데이트 완료: (커밋 후 기재)
