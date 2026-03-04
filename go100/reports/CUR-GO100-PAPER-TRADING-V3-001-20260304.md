# CUR-GO100-PAPER-TRADING-V3-001-20260304
## GO100 30일 모의투자 V3 Brain 연동 — 구현 완료 보고서

> 작성일: 2026-03-04 KST
> Task ID: DIR-GO100-PAPER-TRADING-V3-003-R3
> 작성자: Claude Code (claude-sonnet-4-6)
> Priority: P0-CRITICAL

---

[인계 확인]
직전 완료: CUR-GO100-PAPER-TRADING-AUDIT-001-20260304
현재 단계: Phase 2C (모의투자 V3 Brain 연동 완료)
CEO 지시 적용: D-001, D-002, D-003, D-012
strategy_cards: 42 (go100_strategy_cards)
open_positions: 0 (신규 모의투자 세션, 첫 거래일 이전)

---

## 1. 작업 개요

| 항목 | 내용 |
|------|------|
| Task | 30일 모의투자 V3 Brain 연동 |
| 선행 조건 | DIR-GO100-V3-ACTIVATE-001-R3 완료 ✅ |
| CEO 승인 | 모의투자 시작 승인됨 (장 개장 03-04 09:00 이후) |
| 완료 시각 | 2026-03-04 15:20 KST |

---

## 2. 구현 내용

### 2-1. scripts/go100/run_paper_trading_v3.py 확인 및 검증

파일 위치: `/root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py`

**구현된 기능:**

| 모드 | 실행 시각 | 설명 |
|------|-----------|------|
| `--mode buy` | 09:10 KST | AI 배치 예측 → ConvictionScore(up_5d_prob) ≥ 0.6 필터 → 상위 3종 선정 → execute_buy_v3 호출 |
| `--mode sell` | 15:15 KST | 보유 포지션 SL(-7%)/TP(+20%)/최대보유일(30일) 조건 검사 → execute_sell_v3 호출 |
| `--mode weekly_review` | 금요일 16:30 KST | 주간 성과 집계(거래수/승률/누적손익/수익률) → Telegram 발송 |
| `--dry-run` | (옵션) | 데이터 흐름만 검증, 주문 미발생 |

**핵심 상수:**
```python
GO100_USER_ID = 2                    # CEO user_id
CONVICTION_THRESHOLD = 0.6          # up_5d_prob 임계값
TOP_N_STOCKS = 3                    # 상위 선정 종목 수
STOP_LOSS_PCT = 0.07                # 7% 손절
TAKE_PROFIT_PCT = 0.20              # 20% 익절
MAX_HOLDING_DAYS = 30               # 최대 보유일
INITIAL_CAPITAL = 10_000_000        # 1천만 원 모의투자 원금
```

### 2-2. risk_engine.check_pre_trade() 통합

파일: `/root/kis-autotrade-v4/backend/app/services/go100/risk_engine.py` (기존, 수정 없음)

매수 실행 전 `check_pre_trade(db, user_id, ticker, qty, exec_price, "BUY", session_id=session_id)` 호출하여 아래 체크 수행:

| 체크 항목 | 동작 |
|----------|------|
| 킬스위치 활성화 | BLOCK + risk_event 기록 |
| 종목당 비중 한도 초과 | BLOCK (max_position_pct 초과 시) |
| 섹터 집중도 한도 | BLOCK (sector 규칙 위반 시) |
| 노출 한도 | BLOCK (총 노출 한도 초과 시) |
| 일일 P&L 한도 | BLOCK (일일 손실 한도 초과 시) |
| `allowed=False` 시 | 해당 종목 매수 건너뜀 + 로그 기록 |

### 2-3. Telegram 알림 연동

GO100 전용 채널 (GO100_TELEGRAM_BOT_TOKEN / GO100_TELEGRAM_CHAT_ID) 연동:

| 이벤트 | 알림 내용 |
|--------|-----------|
| 매수 완료 | 🟢 매수 종목 리스트 (ticker/qty/price/prob/cs_ai) |
| 매수 없음 | ⚠️ ConvictionScore 임계값 미달 안내 |
| 매도 완료 | 🔴 청산 종목 리스트 (ticker/qty/pnl/pnl_pct/signal_source) |
| 매도 없음 | ℹ️ 청산 조건 미해당 안내 |
| 일일 요약 | 📋 자본/수익률/보유종목 요약 (매도 모드 종료 후 겸함) |
| 주간 자기리뷰 | 📊 주간 성과 전체 집계 |
| DRY-RUN | 🟡 DRY-RUN 태그 포함 |

### 2-4. crontab 3건 등록

```
# GO100 V3 모의투자 — 매수 (09:10 KST = 00:10 UTC)
10 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode buy >> /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log 2>&1

# GO100 V3 모의투자 — 매도 (15:15 KST = 06:15 UTC)
15 6 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode sell >> /root/kis-autotrade-v4/logs/paper_trading_v3_sell.log 2>&1

# GO100 V3 모의투자 — 주간 자기리뷰 (금요일 16:30 KST = 07:30 UTC)
30 7 * * 5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode weekly_review >> /root/kis-autotrade-v4/logs/paper_trading_v3_review.log 2>&1
```

등록 확인: `crontab -l | grep paper_trading_v3` → 3건 모두 확인 ✅

---

## 3. dry-run 테스트 결과

실행 시각: 2026-03-04 15:17~15:19 KST

### 3-1. buy 모드 dry-run

```bash
/root/kis-autotrade-v4/venv/bin/python3 scripts/go100/run_paper_trading_v3.py --mode buy --dry-run
```

**결과:**
```
2026-03-04 15:18:37 [INFO] paper_trading_v3 — run_paper_trading_v3 시작: mode=buy dry_run=True date=2026-03-04
2026-03-04 15:18:38 [INFO] paper_trading_v3 — 기존 ACTIVE 세션 사용: session_id=2
2026-03-04 15:18:38 [INFO] paper_trading_v3 — 유니버스 후보: 100종목
2026-03-04 15:18:55 [INFO] paper_trading_v3 — 배치 점수: 전체=100 임계값통과=0(0.6이상) 상위3=[]
2026-03-04 15:18:57 [INFO] httpx — HTTP/1.1 200 OK  ← Telegram 발송 성공
2026-03-04 15:18:57 [INFO] paper_trading_v3 — ConvictionScore 임계값 통과 종목 없음 → 매수 건너뜀
2026-03-04 15:18:57 [INFO] paper_trading_v3 — run_paper_trading_v3 완료: {'ok': True, 'bought': [], 'scored_count': 100}
```

**판정: ✅ PASS**
- 유니버스 100종목 정상 조회
- AI 배치 점수 100건 산출 완료 (V3 Brain 모델 로드 성공)
- ConvictionScore 임계값 미달 시 매수 미발생 확인
- Telegram HTTP 200 발송 확인
- 주문 미발생 확인 (dry-run 조건 충족)

### 3-2. sell 모드 dry-run

```bash
/root/kis-autotrade-v4/venv/bin/python3 scripts/go100/run_paper_trading_v3.py --mode sell --dry-run
```

**결과:**
```
2026-03-04 15:19:04 [INFO] paper_trading_v3 — run_paper_trading_v3 시작: mode=sell dry_run=True date=2026-03-04
2026-03-04 15:19:04 [INFO] paper_trading_v3 — === SELL MODE 시작 [DRY-RUN] ===
2026-03-04 15:19:05 [INFO] httpx — HTTP/1.1 200 OK  ← Telegram 발송 성공 (청산 조건 해당 없음)
2026-03-04 15:19:06 [INFO] httpx — HTTP/1.1 200 OK  ← 일일 요약 Telegram 발송 성공
2026-03-04 15:19:06 [INFO] paper_trading_v3 — run_paper_trading_v3 완료: {'ok': True, 'session_id': 2, 'sold': [], 'dry_run': True}
```

**판정: ✅ PASS**
- ACTIVE 세션 정상 조회 (session_id=2)
- 포지션 조회 및 SL/TP/timeout 조건 체크 완료
- 청산 없음 알림 Telegram HTTP 200 확인
- 일일 요약 Telegram HTTP 200 확인
- 주문 미발생 확인

### 3-3. weekly_review 모드 dry-run

```bash
/root/kis-autotrade-v4/venv/bin/python3 scripts/go100/run_paper_trading_v3.py --mode weekly_review --dry-run
```

**결과:**
```
2026-03-04 15:19:12 [INFO] paper_trading_v3 — run_paper_trading_v3 시작: mode=weekly_review dry_run=True date=2026-03-04
2026-03-04 15:19:12 [INFO] paper_trading_v3 — === WEEKLY REVIEW 시작 [DRY-RUN] ===
2026-03-04 15:19:13 [INFO] httpx — HTTP/1.1 200 OK  ← 주간 리뷰 Telegram 발송 성공
2026-03-04 15:19:13 [INFO] paper_trading_v3 — 주간 자기리뷰 완료: {'session_id': 2, 'total_trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0.0, 'total_pnl': 0.0, 'total_return_pct': 0.0, 'current_capital': 10000000.0, 'open_positions': 0}
2026-03-04 15:19:13 [INFO] paper_trading_v3 — run_paper_trading_v3 완료: {'session_id': 2, ...}
```

**판정: ✅ PASS**
- 세션 성과 집계 정상 (session_id=2, 원금 10,000,000원 유지)
- Telegram HTTP 200 확인
- 주문 미발생 확인

### 3-4. 종합 dry-run 판정

| 모드 | 주문 미발생 | Telegram HTTP 200 | 데이터 흐름 | 판정 |
|------|------------|-------------------|-------------|------|
| buy | ✅ | ✅ | ✅ (100종목 AI 점수 산출) | ✅ PASS |
| sell | ✅ | ✅ | ✅ (포지션/청산 조건 체크) | ✅ PASS |
| weekly_review | ✅ | ✅ | ✅ (성과 집계) | ✅ PASS |

**종합: DRY-RUN 3건 전체 PASS ✅**

---

## 4. 첫 거래일 모니터링 체크리스트

> 첫 거래일 기준: 2026-03-05 (목요일)

### 4-1. 장 개장 전 (08:50~09:05)

- [ ] 로그 디렉터리 확인: `ls /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log`
- [ ] DB 연결 상태 확인: `systemctl status go100`
- [ ] `stock_universe` 테이블 ACTIVE 종목 수 확인 (0이면 alert)
- [ ] V3 AI 모델 파일 존재 확인: `ls backend/app/services/go100/ai/models/` 또는 DB 모델 상태

### 4-2. 매수 직후 (09:10~09:20)

- [ ] 로그 확인: `tail -50 /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log`
- [ ] 기대 로그 항목:
  - `유니버스 후보: NNN종목`
  - `배치 점수: 전체=NN 임계값통과=N(0.6이상) 상위3=[...]`
  - `[BUY] TICKER qty=NN price=NNNN ...` (매수 성공 시)
  - Telegram 알림 수신 확인
- [ ] 비정상 케이스 (즉시 대응):
  - `유니버스 후보: 0종목` → `stock_universe` 테이블 확인
  - `AiScorer.load() 실패` → V3 모델 파일 확인
  - `psycopg2.OperationalError` → DB 연결 확인
  - `Telegram 발송 실패` → 토큰/채팅ID 확인

### 4-3. 장중 모니터링 (11:00, 13:00)

- [ ] 보유 포지션 확인:
  ```sql
  SELECT ticker, qty, entry_price, entry_date
  FROM go100_paper_trades
  WHERE session_id = 2 AND trade_type = 'BUY'
  ORDER BY executed_at DESC LIMIT 10;
  ```
- [ ] 현재가 기준 손익 확인 (SL -7% 도달 종목 주의)
- [ ] 로그에 에러 없는지 확인

### 4-4. 매도 직후 (15:15~15:25)

- [ ] 로그 확인: `tail -50 /root/kis-autotrade-v4/logs/paper_trading_v3_sell.log`
- [ ] 기대 로그 항목:
  - `SELL SKIP` (청산 조건 미달)
  - `[SELL] TICKER qty=NN ...` (청산 시)
  - 일일 요약 Telegram 수신 확인
- [ ] `go100_paper_trading_sessions` current_capital 변화 확인

### 4-5. 장 마감 후 (15:30)

- [ ] DB 거래 내역 확인:
  ```sql
  SELECT trade_type, ticker, quantity, price, pnl, executed_at
  FROM go100_paper_trades
  WHERE session_id = 2
  ORDER BY executed_at DESC LIMIT 20;
  ```
- [ ] 세션 상태 확인:
  ```sql
  SELECT session_id, initial_capital, current_capital, start_date, end_date, status
  FROM go100_paper_trading_sessions
  WHERE session_id = 2;
  ```
- [ ] 일일 P&L = (current_capital - initial_capital)
- [ ] 로그 파일 크기 정상 범위 확인 (>10KB 이상이면 활성)

### 4-6. 금요일 주간 리뷰 (16:30)

- [ ] 로그 확인: `tail -30 /root/kis-autotrade-v4/logs/paper_trading_v3_review.log`
- [ ] Telegram 주간 리뷰 메시지 수신 확인
- [ ] 성과 지표 기록 (총 거래수 / 승률 / 누적 손익 / 수익률)

### 4-7. 이상 발생 시 대응 절차

| 증상 | 우선 조치 |
|------|-----------|
| 크론 미실행 | `crontab -l | grep paper_trading_v3` 확인 후 재등록 |
| 주문 미발생 (정상 후보 존재 시) | risk_engine 킬스위치 상태 확인 |
| AI 점수 0건 | ai_scorer.py 모델 상태 확인 |
| DB 에러 | `systemctl status go100` + `systemctl status postgresql` |
| Telegram 미도착 | .env GO100_TELEGRAM_* 환경변수 확인 |

---

## 5. 완료 기준 체크

| 기준 | 상태 | 비고 |
|------|------|------|
| 스크립트 생성 | ✅ | scripts/go100/run_paper_trading_v3.py (687줄) |
| cron 3건 등록 | ✅ | 매수(00:10 UTC)/매도(06:15 UTC)/주간리뷰(07:30 UTC 금) |
| dry-run PASS | ✅ | buy/sell/weekly_review 3모드 전체 PASS |
| Telegram 알림 테스트 PASS | ✅ | 3회 HTTP 200 확인 |
| risk_engine.check_pre_trade() 통합 | ✅ | 매수 실행 전 호출, BLOCK 시 건너뜀 |
| 첫 거래일 모니터링 체크리스트 | ✅ | 섹션 4 참조 |

**종합 판정: 완료 기준 전체 달성 ✅**

---

## 6. 모의투자 세션 현황

| 항목 | 값 |
|------|-----|
| session_id | 2 |
| user_id | 2 (CEO) |
| initial_capital | 10,000,000원 |
| current_capital | 10,000,000원 |
| start_date | 2026-03-04 |
| end_date | 2026-04-03 (30일) |
| status | ACTIVE |
| 현재 보유 포지션 | 0종목 (첫 거래일 전) |

---

## 7. 아키텍처 흐름 요약

```
[cron 09:10 KST]
  → run_paper_trading_v3.py --mode buy
    → stock_universe.ACTIVE (100종목 조회)
    → AiScorer.score() × 100종목 (V3 Brain)
      → up_5d_prob ≥ 0.6 필터
      → 상위 3종 선정
    → execute_buy_v3()
      → risk_engine.check_pre_trade() (포지션/섹터/노출/P&L 체크)
      → go100_paper_trades INSERT
      → go100_paper_trading_sessions.current_capital UPDATE
    → Telegram 알림 (🟢 매수 완료)

[cron 15:15 KST]
  → run_paper_trading_v3.py --mode sell
    → go100_paper_trades 포지션 조회
    → SL(-7%) / TP(+20%) / max_holding_days(30일) 조건 체크
    → execute_sell_v3()
      → go100_paper_trades INSERT (SELL)
      → current_capital UPDATE
    → Telegram 알림 (🔴 매도 완료)
    → Telegram 일일 요약 (📋)

[cron 금요일 16:30 KST]
  → run_paper_trading_v3.py --mode weekly_review
    → go100_paper_trades 집계 (총 거래/승률/손익/수익률)
    → Telegram 주간 리뷰 (📊)
```

---

## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-PAPER-TRADING-V3-001-20260304.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-PAPER-TRADING-V3-001-20260304.md
- 커밋: (push 후 기재)
- HTTP 확인: (push 후 기재)
- HANDOVER 업데이트: 완료

---

HANDOVER.md 업데이트 완료: (push 후 커밋해시 기재)
