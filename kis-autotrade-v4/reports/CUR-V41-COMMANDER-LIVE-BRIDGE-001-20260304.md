# CUR-V41-COMMANDER-LIVE-BRIDGE-001 — 백억이 군단 V4.1 실백테스트 연동

**작성일시**: 2026-03-04 00:10 KST
**작업자**: Claude Code
**우선순위**: P0
**상태**: 완료 (Step 2~5 구현, Step 1 스킵 — Gemini 키 교체 불필요)

---

## 1. 작업 요약

백억이 군단이 V4.1 실제 DESK2 백테스트를 자율 실행하여 최적 파라미터를 도출하고
CEO 텔레그램으로 보고하는 파이프라인 구축.

---

## 2. 구현 내역

### Step 1 — Gemini API 키 교체 (스킵)

> 대표님 지시: "제미니 키교체는 하지마라" → 스킵

### Step 2 — BacktesterAgent ↔ DESK2 실연동

**수정 파일**: `backend/app/services/go100/agents/agent_backtester.py`

`tool_run_replay_backtest()` 함수를 시뮬레이션→실연동으로 교체.

**변경 전**:
```python
# 랜덤 equity_curve + 가상 trade_log로 시뮬레이션
rng = random.Random(...)
equity_curve = [...]  # _simulated: True
```

**변경 후**:
```python
# desk2_backtest_60d.py --output-json 서브프로세스 실행
cmd = [PYTHON_BIN, BACKTEST_PY,
       "--start", period_start, "--end", period_end,
       "--config", tmp_cfg_name, "--output-json"]
proc = await asyncio.to_thread(subprocess.run, cmd, ...)
raw = json.loads(proc.stdout)  # _real: True
```

**수정 파일**: `scripts/desk2/desk2_backtest_60d.py`

- `run_backtest(start, end, config_path=None)` — config_path 파라미터 추가
- CLI에 `--start`, `--end`, `--config`, `--output-json` 인수 추가
- `--output-json` 지정 시 stdout에 JSON만 출력 (기존 print_report 우회)

반환 필드 매핑:
| desk2_backtest_60d | tool_run_replay_backtest |
|-------------------|------------------------|
| `metrics.profit_factor` | `pf` |
| `metrics.max_dd_pct` | `mdd` (음수 변환) |
| `trades.win_rate` | `win_rate` (÷100) |
| `trades.total` | `total_trades` |
| `capital.return_pct` | `total_return` |

**검증**:
```bash
venv/bin/python3 scripts/desk2/desk2_backtest_60d.py \
  --start 2025-12-01 --end 2026-03-03 --output-json | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ pf:', d['metrics']['profit_factor'])"
```

---

### Step 3 — OptimizerAgent 신규 생성

**신규 파일**: `backend/app/services/go100/agents/agent_optimizer.py`

```
기능:
  - Phase 1: 핵심 3파라미터 Grid Search (4×4×2 = 32조합)
    - exit.trend.stop_pct:     [-3.0, -4.0, -5.0, -7.0]
    - exit.trend.trailing_pct: [10.0, 15.0, 20.0, 30.0]
    - exit.reversal.type:      ["fixed", "trailing"]
  - Phase 2: Phase 1 상위 3개 기반 나머지 4파라미터 확장 탐색
    - exit.reversal.target_pct, exit.reversal.stop_pct
    - signal.b1_min_rsi, regime_filter
  - 각 조합: tool_run_replay_backtest() + tool_validate_robustness()
  - 승인 기준: PF≥1.2, MDD>-15%, trades≥50, WinRate≥35%
  - 복합 점수: pf*0.7 + mdd_bonus*0.3
```

**승인 기준**:
```python
ACCEPTANCE_CRITERIA = {
    "min_pf":       1.2,
    "max_mdd":     -15.0,
    "min_trades":   50,
    "min_win_rate": 0.35,
}
```

**검증**:
```bash
venv/bin/python3 -c "
from backend.app.services.go100.agents.agent_optimizer import OptimizerAgent, _build_grid, PHASE1_PARAMS
print('Phase1 조합:', len(_build_grid(PHASE1_PARAMS)))  # 32
"
# ✅ Phase1 조합: 32
```

---

### Step 4 — config_applier.py 신규 생성

**신규 파일**: `backend/app/services/go100/agents/config_applier.py`

```
기능:
  1. desk2_config.yaml 자동 백업 (config_backups/desk2_config.yaml.bak.YYYYMMDD_HHMMSS)
  2. nested key 경로로 파라미터 적용 ("exit.trend.stop_pct" → config["exit"]["trend"]["stop_pct"])
  3. YAML round-trip 검증
  4. DESK2_AUTO_APPLY=false(기본) → pending 파일 생성 → CEO 승인 대기
     DESK2_AUTO_APPLY=true → desk2_config.yaml 즉시 덮어쓰기
```

**반환**:
```json
{
  "status": "PENDING_CEO_APPROVAL",
  "backup": "/root/.../config_backups/desk2_config.yaml.bak.20260304_001000",
  "pending_path": "/root/.../config_backups/pending_config_20260304_001000.yaml",
  "params": {"exit.trend.stop_pct": -5.0, ...}
}
```

**백업 디렉토리**: `scripts/desk2/config_backups/` (신규 생성)

---

### Step 5 — commander.py 파이프라인 추가 + 크론 등록

**수정 파일**: `backend/app/services/go100/agents/commander.py`

`CommanderGO100` 클래스에 3개 메서드 추가:

| 메서드 | 역할 |
|--------|------|
| `run_optimization_pipeline(period_start, period_end)` | 전체 파이프라인 실행 |
| `_save_optimization_result(opt_result)` | go100_agent_reports DB 저장 |
| `_format_optimization_report(opt_result)` | CEO 텔레그램 보고 포맷 |
| `_send_telegram_report(text_msg)` | 텔레그램 발송 |

**전체 흐름**:
```
run_optimization_pipeline()
  ↓
OptimizerAgent.run_optimization()
  ├── Phase1: 32조합 × tool_run_replay_backtest()
  └── Phase2: 상위3 기반 확장 탐색
  ↓
_save_optimization_result() → go100_agent_reports
  ↓
_send_telegram_report() → CEO 텔레그램
  ↓
apply_optimized_config() → PENDING or APPLIED
```

**`__init__.py` 업데이트**: `OptimizerAgent`, `apply_optimized_config` export 추가

**크론 등록** (`crontab -e`):
```cron
# ── [LIVE-BRIDGE-001] DESK2 자율 최적화 (평일 장마감 후 16:30)
30 16 * * 1-5 cd /root/kis-autotrade-v4 && ... python3 -c "
  import asyncio
  from backend.app.services.go100.agents.commander import CommanderGO100
  asyncio.run(CommanderGO100().run_optimization_pipeline())
" >> logs/cron/desk2_optimizer_$(date +%Y%m%d).log 2>&1
```

---

## 3. 변경 파일 목록

| 파일 | 유형 | 내용 |
|------|------|------|
| `scripts/desk2/desk2_backtest_60d.py` | 수정 | `config_path` 파라미터 + `--output-json` CLI 플래그 |
| `backend/app/services/go100/agents/agent_backtester.py` | 수정 | `tool_run_replay_backtest` 실연동 교체 |
| `backend/app/services/go100/agents/agent_optimizer.py` | 신규 | DESK2 파라미터 Grid Search 에이전트 |
| `backend/app/services/go100/agents/config_applier.py` | 신규 | 최적 파라미터 안전 적용 + 백업 |
| `backend/app/services/go100/agents/commander.py` | 수정 | `run_optimization_pipeline()` 외 3개 메서드 추가 |
| `backend/app/services/go100/agents/__init__.py` | 수정 | `OptimizerAgent`, `apply_optimized_config` export |
| `scripts/desk2/config_backups/` | 신규 | config 백업 디렉토리 |

---

## 4. 검증 결과

```
✅ Step 3,4: import OK
✅ Step 5: CommanderGO100 메서드 확인 (run_optimization_pipeline, _format_optimization_report, _send_telegram_report)
✅ Step 3: Phase1 grid = 32조합
✅ Step 4: desk2_config.yaml 읽기 OK
✅ Step 2: desk2_backtest_60d.py --output-json 플래그 확인
=== ALL CHECKS PASSED ===
```

---

## 5. 파이프라인 실행 예상 시간

| 단계 | 조합수 | 1회 백테스트 | 소요 |
|------|--------|-------------|------|
| Phase 1 | 32조합 | ~30초 | ~16분 |
| Phase 2 | 최대 48조합 | ~30초 | ~24분 |
| **전체** | **~80조합** | — | **~40분** |

---

## 6. 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DESK2_AUTO_APPLY` | `false` | `true`로 변경 시 CEO 승인 없이 즉시 적용 |
| `OPTIMIZER_BT_INTERVAL` | `0.5` | 백테스트 간 대기 시간(초) |

---

## 7. 향후 작업

| 항목 | 우선순위 |
|------|---------|
| Gemini API 키 교체 (별도 발급 필요) | P1 |
| 실제 파이프라인 첫 실행 결과 확인 (평일 16:30) | P1 |
| Walk-Forward 검증 강화 (OOS 30% 실분봉 검증) | P2 |
| Phase 1+2 결과 DB 누적 → 장기 트렌드 분석 | P2 |
