---
project: KIS + GO100
task_id: "087"
completed_at: "2026-03-05T10:13:32+09:00"
---

# Task087 BRIDGE RESULT — 내일(3/6) 09:10 자동매수 사전 검증 + TP 발동 모니터링 체계

## 원본 지시서 (KIS_20260305_100434_BRIDGE.md)

```
Task ID: 087 제목: 내일(3/6) 09:10 자동매수 사전 검증 + TP 발동 모니터링 체계 프로젝트: KIS + GO100 우선순위: P0 예상 토큰: ~15K 의존: 없음 (독립, READ-ONLY) 자체승인: YES

목적: 내일 09:10 paper_trading_v3 첫 매수 크론이 실제로 체결되는지 사전 검증. 075의 TP 수정 + 076의 모의투자 수정이 실전 반영되는 첫 날. 실패하면 수익 창출이 또 1일 지연됨.

Phase 1: 사전 검증 (오늘 장 마감 후)

Step 1-1: 크론 스케줄 최종 확인
crontab -l | grep -E "paper_trading|unified_engine|monitor_virtual"

Step 1-2: paper_trading_v3 dry-run 재실행
python3 scripts/go100/run_paper_trading_v3.py --mode buy --dry-run
5종목 scored_pass 확인
CONVICTION_THRESHOLD=0.50 반영 확인
risk rule max_position_pct=20% 통과 확인

Step 1-3: unified_engine action_signal 시간 창 20h 적용 확인
grep "INTERVAL" scripts/run_unified_engine.py | head -5
'20 hours' 확인

Step 1-4: EXIT_PARAMS TP=3% 적용 확인
grep -A 10 "EXIT_PARAMS" scripts/run_unified_engine.py
grep -A 10 "STRATEGY_EXIT_PARAMS" backend/app/services/unified_engine/core/exit_manager.py

Phase 2: 모니터링 자동화

Step 2-1: 내일 09:15 자동 확인 스크립트 생성
Step 2-2: 크론 등록 - 15 0 * * 1-5 python3 scripts/check_morning_execution.py >> logs/morning_check.log 2>&1
Step 2-3: TP 발동 감지 스크립트

완료 조건:
 dry-run 5종목 매수 재확인
 EXIT_PARAMS TP=3% 코드 확인
 모닝 체크 스크립트 + 크론 등록
 TP 감지 스크립트 + 크론 등록

보고서: CUR-V41-MORNING-PRECHECK-001-20260305.md
```

---

## Step 1-1: 크론 스케줄 최종 확인

### 실행 명령
```bash
crontab -l | grep -E "paper_trading|unified_engine|monitor_virtual"
```

### 실제 출력
```
10 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode buy >> /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log 2>&1
15 6 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode sell >> /root/kis-autotrade-v4/logs/paper_trading_v3_sell.log 2>&1
30 7 * * 5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode weekly_review >> /root/kis-autotrade-v4/logs/paper_trading_v3_review.log 2>&1
0 9-15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python scripts/monitor_virtual_run.py periodic >> /root/kis-autotrade-v4/logs/virtual_hourly_report.log 2>&1
```

### 판정
✅ paper_trading_v3 --mode buy: `10 0 * * 1-5` (09:10 KST = 00:10 UTC) 평일 등록됨
✅ paper_trading_v3 --mode sell: `15 6 * * 1-5` (15:15 KST = 06:15 UTC) 평일 등록됨
✅ monitor_virtual_run.py: `0 9-15 * * 1-5` 장중 매시 등록됨

---

## Step 1-2: paper_trading_v3 dry-run 재실행

### 실행 명령
```bash
timeout 60 /root/kis-autotrade-v4/venv/bin/python3 scripts/go100/run_paper_trading_v3.py --mode buy --dry-run
```

### 실행 시작 로그
```
2026-03-05 10:11:18 [INFO] paper_trading_v3 — run_paper_trading_v3 시작: mode=buy dry_run=True date=2026-03-05
2026-03-05 10:11:18 [INFO] paper_trading_v3 — === BUY MODE 시작 [DRY-RUN] ===
```

### 실행 완료 로그
```
2026-03-05 10:11:29 [INFO] paper_trading_v3 — [BUY DRY] 000080 qty=100 price=16296 up_5d_prob=0.563 cs_ai=100
2026-03-05 10:11:29 [INFO] paper_trading_v3 — [BUY DRY] 0000H0 qty=100 price=10420 up_5d_prob=0.563 cs_ai=91
2026-03-05 10:11:29 [INFO] paper_trading_v3 — [BUY DRY] 0000Z0 qty=100 price=14900 up_5d_prob=0.563 cs_ai=100
2026-03-05 10:11:30 [INFO] paper_trading_v3 — run_paper_trading_v3 완료: {'ok': True, 'session_id': 2, 'candidates': 100, 'scored_pass': 5, 'bought': [{'ticker': '000020', 'qty': 300, 'price': 5665.659999999999, 'up_5d_prob': 0.5629, 'cs_ai': 99, 'dry_run': True}, {'ticker': '000050', 'qty': 200, 'price': 8658.65, 'up_5d_prob': 0.5629, 'cs_ai': 100, 'dry_run': True}, {'ticker': '000080', 'qty': 100, 'price': 16296.279999999999, 'up_5d_prob': 0.5629, 'cs_ai': 100, 'dry_run': True}, {'ticker': '0000H0', 'qty': 100, 'price': 10420.409999999998, 'up_5d_prob': 0.5629, 'cs_ai': 91, 'dry_run': True}, {'ticker': '0000Z0', 'qty': 100, 'price': 14899.884999999998, 'up_5d_prob': 0.5629, 'cs_ai': 100, 'dry_run': True}], 'dry_run': True}
```

### 파싱 결과
| 항목 | 값 | 판정 |
|------|----|------|
| ok | True | ✅ |
| session_id | 2 | ✅ 활성 세션 |
| candidates | 100 | ✅ 100개 후보 |
| scored_pass | 5 | ✅ 5종목 통과 |
| dry_run | True | ✅ 실제 체결 없음 |

### 매수 예정 종목 (dry-run)
| Ticker | Qty | Price | up_5d_prob | cs_ai |
|--------|-----|-------|-----------|-------|
| 000020 | 300 | 5,665.66 | 0.5629 | 99 |
| 000050 | 200 | 8,658.65 | 0.5629 | 100 |
| 000080 | 100 | 16,296.28 | 0.5629 | 100 |
| 0000H0 | 100 | 10,420.41 | 0.5629 | 91 |
| 0000Z0 | 100 | 14,899.88 | 0.5629 | 100 |

### CONVICTION_THRESHOLD 소스 코드 확인
```python
CONVICTION_THRESHOLD = 0.50         # up_5d_prob 임계값 (Task076: 0.60→0.50, LightGBM 원시확률 최대값 ~0.56으로 0체결 해소)
TOP_N_STOCKS = 5                    # 상위 선정 종목 수 (Task076: 3→5, 종목당 33%→20% 배분, 리스크규칙 max_position_pct=20% 준수)
```

### 판정
✅ 5종목 scored_pass 확인 (candidates: 100 → scored_pass: 5)
✅ CONVICTION_THRESHOLD=0.50 반영 확인 (up_5d_prob=0.5629 ≥ 0.50)
✅ max_position_pct=20% 준수 (TOP_N_STOCKS=5, 종목당 20% 배분)

---

## Step 1-3: unified_engine action_signal 시간 창 20h 적용 확인

### 실행 명령
```bash
grep "INTERVAL" scripts/run_unified_engine.py | head -5
```

### 실제 출력
```
            WHERE tick_time >= NOW() - INTERVAL '20 hours'
                  AND tick_time >= NOW() - INTERVAL '5 minutes'
                      AND captured_at >= NOW() - INTERVAL '5 minutes'
            WHERE t.tick_time >= NOW() - INTERVAL '20 hours'
```

### 판정
✅ `INTERVAL '20 hours'` 확인됨 (action_signal 조회 시간 창)

---

## Step 1-4: EXIT_PARAMS TP=3% 적용 확인

### 실행 명령
```bash
grep -A 10 "EXIT_PARAMS" scripts/run_unified_engine.py
grep -A 10 "STRATEGY_EXIT_PARAMS" backend/app/services/unified_engine/core/exit_manager.py
```

### 결과 — scripts/run_unified_engine.py
```
    # 전략별 TP/SL 파라미터 (exit_manager.py STRATEGY_EXIT_PARAMS와 동기화)
    EXIT_PARAMS = {
        "D2":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
        "D2A": {"sl_pct": 0.020, "tp_pct": None,  "timeout_min": 30},
        "D2B": {"sl_pct": 0.025, "tp_pct": None,  "timeout_min": 60},
        "D4":  {"sl_pct": 0.020, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305: SL 2%, TP 3%
        "D5":  {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
        "S1":  {"sl_pct": 0.030, "tp_pct": None,  "timeout_min": None},
        "D6":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
        "D7":  {"sl_pct": 0.030, "tp_pct": 0.030, "timeout_min": 60},
        "D-ORB": {"sl_pct": 0.025, "tp_pct": 0.030, "timeout_min": 60},
    }
            params = EXIT_PARAMS.get(strategy_id, DEFAULT_EXIT)
            sl_pct = params["sl_pct"]
            tp_pct = params["tp_pct"]
            timeout_min = params["timeout_min"]
```

### 결과 — backend/app/services/unified_engine/core/exit_manager.py
```
    STRATEGY_EXIT_PARAMS = {
        "D2":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
        "D2A": {"sl_pct": 0.020, "trail_start": 0.015, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": 30},
        "D2B": {"sl_pct": 0.025, "trail_start": 0.015, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": 60},
        "D4":  {"sl_pct": 0.020, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},  # CEO-APPROVAL-20260305: SL 2%, TP 3%
        "D5":  {"sl_pct": 0.025, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
        "S1":  {"sl_pct": 0.030, "trail_start": 0.020, "trail_retrace": 0.10, "tp_pct": None, "timeout_min": None},
        "D6":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
        "D7":  {"sl_pct": 0.030, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
        "D-ORB": {"sl_pct": 0.025, "trail_start": 0.030, "trail_retrace": 0.10, "tp_pct": 0.030, "timeout_min": 60},
    }
        return self.STRATEGY_EXIT_PARAMS.get(strategy_id, self.DEFAULT_EXIT_PARAMS)
```

### 판정
✅ TP=3% (0.030): D2, D4, D5, D6, D7, D-ORB 전략 모두 적용
✅ run_unified_engine.py ↔ exit_manager.py 동기화 확인
✅ CEO-APPROVAL-20260305 주석으로 이력 명확

---

## Step 2-1: check_morning_execution.py 생성

### 파일 경로
`/root/kis-autotrade-v4/scripts/check_morning_execution.py`

### 파일 내용 (전체)
```python
"""
09:15 실행: paper_trading_v3_buy.log 확인
- 'bought' 키워드 있으면 → 텔레그램 성공 알림
- 없으면 → 텔레그램 긴급 알림 + 원인 로그 첨부

Task087: 내일(3/6) 09:10 자동매수 사전 검증 + TP 발동 모니터링 체계
"""
import os
import re
import datetime
import logging

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("check_morning_execution")

# ─── 설정 ─────────────────────────────────────────────────────────────────────
LOG_PATH = "/root/kis-autotrade-v4/logs/paper_trading_v3_buy.log"
GO100_TELEGRAM_BOT_TOKEN = os.environ.get("GO100_TELEGRAM_BOT_TOKEN", "").strip()
GO100_TELEGRAM_CHAT_ID = os.environ.get("GO100_TELEGRAM_CHAT_ID", "").strip()


def _send_telegram(text: str) -> None:
    """GO100 전용 Telegram 채널로 동기 발송."""
    token = GO100_TELEGRAM_BOT_TOKEN
    chat_id = GO100_TELEGRAM_CHAT_ID
    if not token or not chat_id:
        logger.warning("Telegram not configured (GO100_TELEGRAM_BOT_TOKEN / GO100_TELEGRAM_CHAT_ID)")
        print(f"[TELEGRAM NOT CONFIGURED] {text}")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4096],
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
        if resp.status_code != 200:
            logger.warning("Telegram 발송 실패 status=%s body=%s", resp.status_code, resp.text[:200])
    except Exception as e:
        logger.warning("Telegram 발송 예외: %s", e)


def get_today_log_lines() -> list[str]:
    """오늘 날짜 로그만 추출 (최근 500줄 기준)."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            lines = f.readlines()
        return [l for l in lines[-500:] if today in l]
    except Exception as e:
        logger.warning("로그 읽기 실패: %s", e)
        return []


def main() -> None:
    today = datetime.date.today().strftime("%Y-%m-%d")
    logger.info("=== 모닝 체크 시작: %s ===", today)

    lines = get_today_log_lines()

    bought_lines = [l for l in lines if "bought" in l.lower() or "[BUY DRY]" in l or "[BUY]" in l]
    error_lines = [l for l in lines if "error" in l.lower() or "exception" in l.lower() or "failed" in l.lower()]

    result_line = next((l for l in lines if "run_paper_trading_v3 완료" in l), None)

    if result_line and "bought" in result_line:
        m_pass = re.search(r"'scored_pass':\s*(\d+)", result_line)
        m_bought = re.search(r"'bought':\s*\[(.+?)\]", result_line, re.DOTALL)
        scored_pass = m_pass.group(1) if m_pass else "?"
        bought_tickers = re.findall(r"'ticker':\s*'([^']+)'", result_line) if m_bought else []
        tickers_str = ", ".join(bought_tickers) if bought_tickers else "(파싱 불가)"

        msg = (
            f"✅ <b>GO100 V3 모닝 매수 성공</b> ({today})\n"
            f"scored_pass: {scored_pass}종목\n"
            f"매수 종목: {tickers_str}\n"
            f"상세: paper_trading_v3_buy.log 참조"
        )
        logger.info("매수 성공 확인: scored_pass=%s, tickers=%s", scored_pass, tickers_str)
        _send_telegram(msg)
    else:
        recent_errors = "\n".join(error_lines[-5:]) if error_lines else "(에러 로그 없음)"
        recent_log = "\n".join(lines[-10:]) if lines else "(오늘 로그 없음)"

        msg = (
            f"🚨 <b>GO100 V3 모닝 매수 미확인</b> ({today})\n"
            f"paper_trading_v3_buy.log 에서 'bought' 키워드를 찾을 수 없습니다.\n\n"
            f"<b>[최근 에러]</b>\n<pre>{recent_errors[:500]}</pre>\n\n"
            f"<b>[최근 로그]</b>\n<pre>{recent_log[:800]}</pre>"
        )
        logger.warning("매수 미확인! error_lines=%d, log_lines=%d", len(error_lines), len(lines))
        _send_telegram(msg)


if __name__ == "__main__":
    main()
```

### 판정
✅ 파일 생성 완료: `/root/kis-autotrade-v4/scripts/check_morning_execution.py`

---

## Step 2-2: 모닝 체크 크론 등록

### 크론 등록 명령
```bash
# /tmp/crontab_current.txt 에 아래 줄 추가 후 crontab 등록
# [KIS TASK-087] 모닝 매수 체결 확인 — 09:15 KST (00:15 UTC) 평일
15 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_morning_execution.py >> /root/kis-autotrade-v4/logs/morning_check.log 2>&1
```

### 등록 후 확인
```
crontab -l | grep -E "check_morning|check_tp"
```
출력:
```
15 0 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_morning_execution.py >> /root/kis-autotrade-v4/logs/morning_check.log 2>&1
0 0-7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_tp_execution.py >> /root/kis-autotrade-v4/logs/tp_check.log 2>&1
```

### 판정
✅ 크론 등록 완료 (`crontab 등록 성공` 출력 확인)

---

## Step 2-3: check_tp_execution.py 생성 + 크론 등록

### 파일 경로
`/root/kis-autotrade-v4/scripts/check_tp_execution.py`

### 파일 내용 (전체)
```python
"""
매 시간 실행: v4_mock_trades에서 pnl_pct > 0 확인
- TP 발동 시 → 텔레그램 보고

Task087: 내일(3/6) 09:10 자동매수 사전 검증 + TP 발동 모니터링 체계
"""
import os
import datetime
import logging

import httpx
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("check_tp_execution")

# ─── 설정 ─────────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "kisautotrade",
    "user": "kis_admin",
    "password": "KisAuto2026!Secure",
}
GO100_TELEGRAM_BOT_TOKEN = os.environ.get("GO100_TELEGRAM_BOT_TOKEN", "").strip()
GO100_TELEGRAM_CHAT_ID = os.environ.get("GO100_TELEGRAM_CHAT_ID", "").strip()

SENT_LOG = "/root/kis-autotrade-v4/logs/tp_check_sent.log"


def _send_telegram(text: str) -> None:
    """GO100 전용 Telegram 채널로 동기 발송."""
    token = GO100_TELEGRAM_BOT_TOKEN
    chat_id = GO100_TELEGRAM_CHAT_ID
    if not token or not chat_id:
        logger.warning("Telegram not configured")
        print(f"[TELEGRAM NOT CONFIGURED] {text}")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4096],
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
        if resp.status_code != 200:
            logger.warning("Telegram 발송 실패 status=%s body=%s", resp.status_code, resp.text[:200])
    except Exception as e:
        logger.warning("Telegram 발송 예외: %s", e)


def load_sent_ids() -> set:
    today = datetime.date.today().isoformat()
    if not os.path.exists(SENT_LOG):
        return set()
    try:
        with open(SENT_LOG, encoding="utf-8") as f:
            return {
                line.strip().split("|")[1]
                for line in f
                if line.strip().startswith(today)
            }
    except Exception:
        return set()


def record_sent(trade_id: str) -> None:
    today = datetime.date.today().isoformat()
    try:
        with open(SENT_LOG, "a", encoding="utf-8") as f:
            f.write(f"{today}|{trade_id}\n")
    except Exception as e:
        logger.warning("sent_log 기록 실패: %s", e)


def check_tp_trades() -> list[dict]:
    """오늘 청산(closed)된 수익 거래 조회."""
    today = datetime.date.today().isoformat()
    query = """
        SELECT
            id::text,
            ticker,
            strategy_id,
            entry_price,
            exit_price,
            pnl_pct,
            exit_reason,
            exit_time
        FROM v4_mock_trades
        WHERE
            status = 'closed'
            AND exit_time::date = %s
            AND (exit_reason = 'TP' OR pnl_pct >= 0.028)
        ORDER BY exit_time DESC
        LIMIT 20
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute(query, (today,))
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
        conn.close()
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        logger.error("DB 조회 실패: %s", e)
        return []


def main() -> None:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    logger.info("=== TP 발동 체크: %s ===", now)

    sent_ids = load_sent_ids()
    tp_trades = check_tp_trades()

    new_trades = [t for t in tp_trades if t["id"] not in sent_ids]
    if not new_trades:
        logger.info("신규 TP 발동 없음 (총 조회: %d건, 이미 보고: %d건)", len(tp_trades), len(sent_ids))
        return

    for trade in new_trades:
        pnl_pct = trade["pnl_pct"] or 0
        entry = trade["entry_price"] or 0
        exit_p = trade["exit_price"] or 0
        reason = trade["exit_reason"] or "?"
        exit_time = str(trade["exit_time"] or "")[:16]
        pnl_display = f"{pnl_pct * 100:.2f}%"

        msg = (
            f"🎯 <b>GO100 TP 발동!</b> ({exit_time})\n"
            f"종목: <b>{trade['ticker']}</b> [{trade['strategy_id']}]\n"
            f"수익률: <b>{pnl_display}</b> ({reason})\n"
            f"매수가: {entry:,.0f} → 매도가: {exit_p:,.0f}"
        )
        logger.info("TP 발동: %s %s pnl=%s reason=%s", trade["ticker"], trade["strategy_id"], pnl_display, reason)
        _send_telegram(msg)
        record_sent(trade["id"])


if __name__ == "__main__":
    main()
```

### 크론 등록
```
# [KIS TASK-087] TP 발동 감지 — 매시 정각 09:00-16:00 KST (00:00-07:00 UTC) 평일
0 0-7 * * 1-5 /root/kis-autotrade-v4/venv/bin/python3 /root/kis-autotrade-v4/scripts/check_tp_execution.py >> /root/kis-autotrade-v4/logs/tp_check.log 2>&1
```

### 판정
✅ 파일 생성 완료: `/root/kis-autotrade-v4/scripts/check_tp_execution.py`
✅ 크론 등록 완료 (매시 정각 00:00-07:00 UTC = 09:00-16:00 KST)

---

## 완료 조건 최종 점검

| 항목 | 결과 | 판정 |
|------|------|------|
| dry-run 5종목 매수 재확인 | candidates:100 → scored_pass:5, 5 tickers 정상 | ✅ |
| EXIT_PARAMS TP=3% 코드 확인 | D2/D4/D5/D6/D7/D-ORB 모두 tp_pct=0.030 | ✅ |
| 모닝 체크 스크립트 생성 | check_morning_execution.py 생성 | ✅ |
| 모닝 체크 크론 등록 | 15 0 * * 1-5 (09:15 KST) | ✅ |
| TP 감지 스크립트 생성 | check_tp_execution.py 생성 | ✅ |
| TP 감지 크론 등록 | 0 0-7 * * 1-5 (09:00-16:00 KST) | ✅ |

---

## 생성 파일 목록

| 파일 | 크기 | 비고 |
|------|------|------|
| `/root/kis-autotrade-v4/scripts/check_morning_execution.py` | ~2.5KB | 09:15 모닝 체결 확인 |
| `/root/kis-autotrade-v4/scripts/check_tp_execution.py` | ~2.8KB | 매시 TP 발동 감지 |
| `/root/kis-autotrade-v4/report/v41/CUR-V41-MORNING-PRECHECK-001-20260305.md` | ~4KB | 태스크 보고서 |

---

## 내일(3/6) 모니터링 일정

| 시각 (KST) | 이벤트 | 모니터링 방법 |
|------------|--------|------------|
| 09:10 | paper_trading_v3 buy 크론 실행 | paper_trading_v3_buy.log |
| 09:15 | check_morning_execution.py 실행 → 텔레그램 | morning_check.log |
| 09:00-16:00 매시 | check_tp_execution.py 실행 | tp_check.log |
| 15:15 | paper_trading_v3 sell 크론 실행 | paper_trading_v3_sell.log |

---

Task087 완료.
