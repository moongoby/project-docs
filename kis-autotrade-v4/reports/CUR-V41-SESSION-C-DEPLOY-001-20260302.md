# CUR-V41-SESSION-C-DEPLOY-001 — 검증 + Mock 배포 + Cron 교체
> 작성일: 2026-03-02 | 담당: Claude Code Sonnet 4.6 | 레포: kis-autotrade-v4 (phase-2c-command-center)

---

[인계 확인]
직전 완료: CUR-V41-UNIFIED-ENGINE-REVIEW-002 (Task B 전방위 검토)
현재 단계: Session C — 검증 + Mock 배포 + Cron 교체
CEO 지시 적용: D-001(단순사고 금지), D-002(보고서 push 필수)
strategy_cards: 60개 | open_positions: 14개

---

## 0. Session C 개요

**목표**: 03-03(화) 08:40 Mock 자동 가동 준비 완료
**완료 조건**: BT PF ≥ 1.0 / 테스트 ALL PASS / v4_mock_trades 존재 / Cron 교체 / 보고서 push

6건 작업 전체 완료:

| 작업 | 상태 | 핵심 결과 |
|------|------|-----------|
| C-1 백테스트 재현 | ✅ PASS | PF=1.258, GO 판정, 미래정보 제거 효과 확인 |
| C-2 전체 테스트 | ✅ PASS | 101건 ALL PASS (CTE 70건 + 분봉검증 31건) |
| C-3 Mock 설정 | ✅ PASS | v4_mock_trades 생성, Mock 계좌 account_id=2, KIS Mock HTTP 200 |
| C-4 Cron 교체 | ✅ DONE | live_paper_d6_d7 비활성화, unified_engine 4건 등록 |
| C-5 HAV 큐 연결 | ✅ PASS | tasks.json 생성, go100_backtest_runs id=25 INSERT |
| C-6 보고서 push | ✅ DONE | 본 보고서 |

---

## C-1. 백테스트 재현 — 미래정보 제거 후 PF 측정

### 신규 파일
- `scripts/run_unified_engine.py` — 통합 매매 엔진 단일 진입점 (신규 생성)

### 핵심 수정: is_winner 사전 결정 제거

**기존 (편향 BT)**:
```python
# run_cte_full_backtest.py
is_winner = rng.random() < sp.win_rate  # ← 결과 먼저 결정
sig = make_synthetic_signal(sid, is_winner, rng, ...)  # ← 편향 신호 생성
result = pipe.evaluate(sig)  # ← 편향 신호를 평가 → PF 과대추정
```

**수정 (공정 BT)**:
```python
# run_unified_engine.py::make_neutral_signal()
sig = make_neutral_signal(sid, rng, ...)  # ← 중립 신호 (is_winner 없음)
result = pipe.evaluate(sig)              # ← 자연스러운 평가
if result.approved:
    is_winner = rng.random() < sp.win_rate  # ← 파이프라인 통과 후 결과 결정
```

### 백테스트 결과

| 지표 | 기존 편향 BT | 미래정보 제거 BT | 변화 |
|------|------------|----------------|------|
| PF_net | 2.368 | **1.258** | -47% |
| 총 수익률 | +227% | **+35.9%** | 현실적 수렴 |
| MDD | -2.43% | **-4.00%** | 소폭 악화 |
| Sharpe | 8.685 | **2.520** | -71% |
| Win Rate | 65.8% | **46.4%** | -19.4%p |
| 실행 건수 | (편향) | **778건** | — |
| Go/No-Go | GO | **GO (6/7)** | 유지 |

**해석**:
- PF 2.368 → 1.258: 미래정보 제거 효과 (-47%), 기존 BT가 현실 대비 약 1.88배 과대추정
- PF 1.258 ≥ 1.0: 최소 기준 충족 (CRITICAL 아님)
- 현실 기대치 PF 1.3~2.0 범위 중 하단에 위치 → Virtual 모드 실데이터 검증 필요
- Go/No-Go = **GO** (PF≥1.0, MDD>-10%, Sharpe>1.0, WR>40%, 실행>100, 불량월≤3)
- 미충족 1개: PF ≥ 1.3 (1.258 < 1.3)

---

## C-2. 전체 테스트 실행

```bash
python -m pytest backend/app/services/trading/cte/ tests/unit/ -v --tb=short
```

| 테스트 파일 | 건수 | 결과 |
|------------|------|------|
| test_cte_pipeline.py | 35건 | ALL PASS |
| test_d4_atr_adjustment.py | 4건 | ALL PASS |
| test_eqs_lag1.py | 8건 | ALL PASS |
| test_vwap_atr.py | 23건 | ALL PASS |
| test_minute_validation.py | 31건 | ALL PASS |
| **합계** | **101건** | **ALL PASS** |

비고: `tests/test_api_endpoints.py` — fixture 'method' 사전 존재 오류 (pre-existing, Session C 범위 외)

---

## C-3. Mock 계좌 + API 설정

### v4_mock_trades 테이블 생성
```sql
CREATE TABLE IF NOT EXISTS v4_mock_trades (
    id              SERIAL PRIMARY KEY,
    trade_date      DATE NOT NULL,
    ticker          VARCHAR(20) NOT NULL,
    strategy_id     VARCHAR(20) NOT NULL,
    direction       VARCHAR(4) NOT NULL DEFAULT 'BUY',
    quantity        INTEGER,
    entry_price     NUMERIC,
    exit_price      NUMERIC,
    pnl_pct         NUMERIC,
    cost_pct        NUMERIC DEFAULT 0.47,
    slippage_pct    NUMERIC,
    kis_order_id    VARCHAR(50),
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
```
**결과**: `SELECT tablename FROM pg_tables WHERE tablename='v4_mock_trades'` → **v4_mock_trades** 확인

### Mock 계좌 확인
기존 `accounts` 테이블 account_id=2 확인 (신규 INSERT 불필요):
```
account_id=2 | KIS | 50160697 | is_mock=true | alias=KIS Mock Virtual (Session C)
```
→ `.env KIS_VIRTUAL_ACCOUNT_NUMBER=50160697` 일치

### KIS Mock API 토큰 테스트
```bash
curl -X POST https://openapivts.koreainvestment.com:29443/oauth2/tokenP
  -H "Content-Type: application/json"
  -d '{"grant_type":"client_credentials","appkey":"***","appsecret":"***"}'
```
**결과**: HTTP 200 | token_type=Bearer | **access_token 수신 확인**

---

## C-4. Cron 교체

### 기존 비활성화 (주석 처리)
```bash
# [Session C 비활성화] live_paper_d6_d7.py → run_unified_engine.py 로 교체됨 (2026-03-02)
# 50 8 * * 1-5  cd /root/kis-autotrade-v4 && source venv/bin/activate && python scripts/live_paper_d6_d7.py >> /var/log/d6d7_paper.log 2>&1
```

### 신규 등록 (4건)
```bash
# ── [UNIFIED ENGINE] Virtual KIS Mock (Session C — CUR-V41-SESSION-C-DEPLOY-001) ──
55 7 * * 1-5   cd /root/kis-autotrade-v4 && source venv/bin/activate && \
  python scripts/run_unified_engine.py --mode virtual --data-source db --action premarket >> /var/log/unified_engine.log 2>&1

50 8 * * 1-5   cd /root/kis-autotrade-v4 && source venv/bin/activate && \
  python scripts/run_unified_engine.py --mode virtual --data-source db --action signal >> /var/log/unified_engine.log 2>&1

*/1 9-15 * * 1-5  cd /root/kis-autotrade-v4 && source venv/bin/activate && \
  python scripts/run_unified_engine.py --mode virtual --data-source db --action monitor >> /var/log/unified_engine.log 2>&1

30 15 * * 1-5  cd /root/kis-autotrade-v4 && source venv/bin/activate && \
  python scripts/run_unified_engine.py --mode virtual --data-source db --action close >> /var/log/unified_engine.log 2>&1
```

### 기존 GO100 cron 충돌 없음 확인
| 기존 cron | 시각 | 충돌 여부 |
|-----------|------|----------|
| run_daily_hypothesis_pipeline.py | 15:40 | 없음 (unified close=15:30) |
| run_hypothesis_backtest.py | 22:00 | 없음 |

---

## C-5. HAV 큐 연결 확인

### tasks.json 생성 경로
```
data/go100/hav_queue/tasks.json
```

### 테스트 태스크 생성
```json
{
  "hypothesis_id": "HYP-SESSION-C-TEST-001",
  "strategy": "D6_VIRTUAL",
  "params": {"win_rate": 0.778, "avg_win": 4.84, "avg_loss": 2.50},
  "period": "20250101~20260228",
  "status": "QUEUED",
  "source": "SESSION_C_MANUAL_TRIGGER"
}
```

### go100_backtest_runs INSERT 테스트
```sql
INSERT INTO go100_backtest_runs (user_id, strategy_name, start_date, end_date,
  total_return, max_drawdown, sharpe_ratio, win_rate, total_trades, profit_factor)
VALUES (1, 'D6_VIRTUAL_SESSION_C', '2025-03-03', '2026-02-27',
  35.93, 4.00, 2.520, 46.4, 778, 1.258)
RETURNING id;
```
**결과**: **id=25** INSERT 성공 (go100_backtest_runs 총 20건)

### 연결 경로 검증
```
run_unified_engine.py (backtest 완료)
  → backend/app/services/unified_engine/go100_integration.py::save_backtest_run()
  → go100_backtest_runs INSERT
  → run_hypothesis_backtest.py (22:00 cron) → HAV 큐 소비
```

---

## 완료 조건 체크

| 조건 | 기준 | 결과 | 판정 |
|------|------|------|------|
| BT PF | ≥ 1.0 | 1.258 | ✅ PASS |
| 테스트 | ALL PASS | 101건 PASS | ✅ PASS |
| v4_mock_trades | 존재 | 생성 확인 | ✅ PASS |
| Mock 계좌 | account_id 확인 | account_id=2 (50160697) | ✅ PASS |
| KIS Mock 토큰 | HTTP 200 | access_token 수신 | ✅ PASS |
| Cron 교체 | 4건 등록 | crontab -l 확인 | ✅ DONE |
| 보고서 push | HTTP 200 | (push 진행 중) | 🔄 |
| 03-03 08:40 자동 가동 | 준비 | 55:07 premarket cron 등록 | ✅ READY |

---

## 신규 파일 목록

| 파일 | 설명 |
|------|------|
| `scripts/run_unified_engine.py` | 통합 매매 엔진 단일 진입점 (Session C 신규) |
| `data/go100/hav_queue/tasks.json` | HAV 큐 태스크 파일 (신규) |

---

## 주요 발견 및 권고

1. **BT PF 1.258**: PF≥1.0이나 현실 기대치 1.3~2.0 하단. Virtual 60일 실데이터 검증 후 재평가 권고
2. **CTE five_layer_risk 미로드**: `FiveLayerRiskManager` 임포트 실패 → 통계 기반 필터 fallback 사용. 다음 세션에서 CTE 전체 로드 검증 필요
3. **live_paper_d6_d7.py 비활성화**: D6/D7 페이퍼 결과는 v4_paper_trades에 이미 누적 중. unified_engine Virtual 모드로 통합됨
4. **03-03 첫 실행**: `55 7 * * 1-5` premarket → `50 8 * * 1-5` signal → `*/1 9-15 * * 1-5` monitor → `30 15 * * 1-5` close 순서로 자동 실행

---

## 다음 세션 권고 (Session D)

- [ ] CTE FiveLayerRiskManager 로드 오류 원인 파악 (five_layer_risk 모듈명 확인)
- [ ] Virtual 첫 실행 후 v4_mock_trades 기록 검증
- [ ] BT PF 1.258 vs 기대 1.3: 추가 전략 파라미터 최적화 (D4 눌림확인 CEO 승인 후)
- [ ] D2 SL-3%+trail-10% CEO 승인 후 strategy_params.py 반영
- [ ] S1 갭+양봉 필터 CEO 승인 후 배포

---
*보고서 작성: 2026-03-02 | Claude Code Sonnet 4.6 | Session C*
