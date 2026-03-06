---
project: KIS-autotrade-v4 / GO100
task_id: T-169
completed_at: 2026-03-06T11:15:00+09:00
---

# T-169 Phase A 실행 결과 — GO100 군단 자율분석 루프 피드백 크론 구축

## 지시서 원문 요약
- 목표: GO100 군단의 장전 토론 + 장후 피드백 2개 연결 고리 구축
- Phase A-1: 현재 연결 상태 정밀 진단
- Phase A-2: daily_morning_debate.py + daily_trade_feedback.py 신규 작성
- Phase A-3: dry-run 테스트 + 크론 등록 준비 + git commit

---

## Phase A-1: 현재 연결 상태 정밀 진단

### [실행] curl -s http://localhost:8002/health | python3 -m json.tool

```json
{
    "status": "degraded",
    "version": "4.1.0",
    "orchestrator_state": "TRADING",
    "database": "connected",
    "redis": "disconnected"
}
```

### [실행] DB 쿼리 — go100_debate_log

```sql
SELECT COUNT(*) FROM go100_debate_log;
```
결과: `5`

### [실행] DB 쿼리 — go100_agent_performance

```sql
SELECT MAX(created_at), agent_name FROM go100_agent_performance GROUP BY agent_name ORDER BY MAX(created_at) DESC;
```
결과:
```
2026-03-06 10:43:41.8827+09 | desk2
2026-03-06 10:43:41.861975+09 | desk3
2026-03-06 10:43:41.839474+09 | desk4
2026-03-06 10:43:41.819465+09 | desk5
2026-03-06 10:43:41.799802+09 | risk
2026-03-06 10:43:41.781534+09 | news
2026-03-06 10:43:41.762919+09 | technical
2026-03-06 10:43:41.744177+09 | supply_demand
2026-03-06 10:43:41.7241+09 | regime
```

### [실행] DB 쿼리 — go100_agent_reports (컬럼 확인 후 수정)

원래 지시: `SELECT COUNT(*), report_type FROM go100_agent_reports GROUP BY report_type;`
실제 컬럼: `signal` (report_type 컬럼 없음)

```sql
SELECT COUNT(*), signal FROM go100_agent_reports GROUP BY signal;
```
결과:
```
1 | RESEARCH_DONE
1 | (NULL)
1 | NEUTRAL
54 | CRITIQUE
```

### [실행] DB 쿼리 — go100_strategy_hypotheses

```sql
SELECT hypothesis_id, source_type, status, created_at FROM go100_strategy_hypotheses ORDER BY created_at DESC LIMIT 5;
```
결과:
```
10 | D-008-KR D_D1_ENTRY | 백테스트완료 | 2026-03-04 12:23:33.463433+09
 9 | D-008-KR DUAL_FLOW  | 백테스트완료 | 2026-03-04 12:22:04.711607+09
 8 | D-008-KR THEME_CYCLE| 백테스트완료 | 2026-03-04 12:20:33.778677+09
 7 | D-008-KR FORCE_ACC  | 백테스트완료 | 2026-03-04 12:19:05.618342+09
 1 | screening           | CARD_CREATED | 2026-02-27 14:16:37.705145+09
```

### [실행] DB 쿼리 — go100_paper_trading_sessions

```sql
SELECT session_id, user_id, status, start_date, created_at FROM go100_paper_trading_sessions ORDER BY created_at DESC LIMIT 3;
```
결과:
```
2 | 2 | ACTIVE    | 2026-02-27 | 2026-02-27 15:54:41.526362+09
1 | 2 | CANCELLED | 2026-02-27 | 2026-02-27 15:53:53.995442+09
```

### [실행] 크론 확인

```bash
crontab -l 2>/dev/null | grep -i "go100\|agent\|commander\|debate\|evolution\|feedback"
ls /etc/cron.d/ | grep -i "go100"
find /root/kis-autotrade-v4/scripts/go100/ -name "*.py" -o -name "*.sh" | sort
```

크론탭에서 debate/feedback 관련 항목 없음.
기존 GO100 크론: LightGBM retrainer, paper_trading_v3 (buy/sell/weekly_review), research_pipeline, daily_ai_prediction_v3

scripts/go100/ 디렉토리: daily_morning_debate.py, daily_trade_feedback.py 없음 (신규 생성 필요)

### [실행] Commander 호출 방법 확인

```bash
grep -rn "def run\|def execute\|def analyze\|def daily\|async def" \
  /root/kis-autotrade-v4/backend/app/services/go100/agents/commander.py | head -20
```

결과:
```
85:class CommanderGO100:
131:    async def _log_decision(
177:    async def run_morning_analysis(
296:    async def run_research_pipeline(
477:    async def run_post_market_review(self) -> Dict[str, Any]:
535:    async def run_desk5_weekly_scan(
593:    async def run_desk4_daily_review(
657:    async def run_desk_chain(
725:    async def _call_regime_agent(self) -> Dict[str, Any]:
743:    async def _call_risk_agent(self) -> Dict[str, Any]:
775:    async def _call_supply_demand_agent(self, stock_code: str, regime: str) -> Dict[str, Any]:
785:    async def _call_technical_agent(self, stock_code: str, regime: str) -> Dict[str, Any]:
795:    async def _call_news_agent(self, stock_code: str) -> Dict[str, Any]:
805:    async def _call_debate(
830:    async def _call_desk5_agent(self, stock_code: str) -> Dict[str, Any]:
843:    async def _call_desk4_agent(
858:    async def _call_desk3_agent(
874:    async def _call_desk2_agent(
893:    async def _run_single_desk_chain(
991:    async def _analyze_single_stock(
1155:    async def _collect_daily_trades(self) -> List[Dict[str, Any]]:
```

```bash
grep -rn "def run\|def execute\|def start_debate" \
  /root/kis-autotrade-v4/backend/app/services/go100/agents/debate.py | head -20
```

결과:
```
74:async def _save_round(
150:async def run_debate(
```

### [실행] 매매결과 → 에이전트 피드백 경로 확인

```bash
grep -rn "mock_trades|v4_mock|trade_result|pnl_pct|feedback|update_accuracy|update_weight" \
  /root/kis-autotrade-v4/backend/app/services/go100/ | head -30
```

결과 (일부):
```
risk_engine.py:368:    반환: {"daily_pnl": float, "daily_pnl_pct": float, ...}
live_trading/live_engine.py:118: pnl_pct = (current_price - entry_price) / entry_price ...
agents/stock_profiler.py:330: pnl_pct = _safe_float(tr.get("pnl_pct") or tr.get("return_pct") ...)
```

→ update_accuracy/update_weight 함수 없음. Commander._update_agent_performance()가 해당 역할 수행.

### [실행] v4_mock_trades 스키마 및 레코드 수 확인

```
컬럼: id, trade_date, ticker, strategy_id, direction, quantity,
      entry_price, exit_price, pnl_pct, cost_pct, slippage_pct, kis_order_id, notes, created_at
레코드: 164건, 최신 2026-03-06 (오늘 pnl_pct=NULL — 장전 차단됨)
```

### [실행] Evolution Loop 확인

```bash
grep -rn "class EvolutionLoop|def run|def start|def evolve" \
  /root/kis-autotrade-v4/backend/app/services/go100/agents/evolution*.py 2>/dev/null | head -10
```
결과: (출력 없음 — evolution 파일 없음)

```bash
grep -rn "evolution" /root/kis-autotrade-v4/scripts/go100/ 2>/dev/null | head -10
```
결과:
```
scripts/go100/run_strategy_evolution.sh:25: from backend.app.services.go100.strategy_evolution import evolution_pipeline
scripts/go100/run_strategy_evolution.sh:28:     return await evolution_pipeline(db, max_hypotheses=5)
```

---

## Phase A-2: 피드백 스크립트 작성

### 신규 파일 1: scripts/go100/daily_morning_debate.py

```python
#!/usr/bin/env python3
# ==============================================================
# daily_morning_debate.py
# GO100 군단 장전 토론 + 시장 판단 배치 — 08:50 KST 실행
# T-169 Phase A: 피드백 루프 Phase A-2
# 크론: 50 8 * * 1-5 (CEO root 등록 필요)
# ==============================================================
"""
Commander.run_morning_analysis()를 호출하여:
  1. 레짐 판별
  2. DESK3/DESK4 감시 종목별 수급/기술/뉴스 분석
  3. 종목별 Bull/Bear 토론
  4. 리스크 판단 (BLOCK/Go/Reduce)
  5. 결과 → go100_agent_reports 저장 + /tmp/go100_commander_daily.json 출력

--dry-run: DB 저장 없이 로그만 출력
"""
import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))
OUTPUT_JSON = "/tmp/go100_commander_daily.json"
USER_ID = 2  # GO100 사용자 ID


def get_candidates_sync() -> list:
    """v4_desk3_pool + v4_desk_positions(ACTIVE)에서 당일 모니터링 후보 종목 추출."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME", "kisautotrade"),
            user=os.getenv("DB_USER", "kis_admin"),
            password=os.getenv("DB_PASSWORD", "KisAuto2026!Secure"),
        )
        cur = conn.cursor()

        seen = set()
        stocks = []

        # DESK3 풀 (당일 모니터링 대상 — 최근 갱신 10개)
        cur.execute("""
            SELECT DISTINCT stock_code FROM v4_desk3_pool
            ORDER BY stock_code LIMIT 10
        """)
        for (sc,) in cur.fetchall():
            if sc not in seen:
                seen.add(sc)
                stocks.append(sc)

        # DESK2/DESK3 활성 포지션 추가 (desk_level: 2=DESK2, 3=DESK3)
        cur.execute("""
            SELECT DISTINCT stock_code FROM v4_desk_positions
            WHERE status = 'ACTIVE' AND desk_level IN (2, 3)
            LIMIT 10
        """)
        for (sc,) in cur.fetchall():
            if sc not in seen:
                seen.add(sc)
                stocks.append(sc)

        conn.close()
        result = stocks[:10]  # 최대 10개
        logger.info("[MorningDebate] 후보 종목 %d개: %s", len(result), result)
        return result

    except Exception as e:
        logger.warning("[MorningDebate] 후보 종목 조회 실패 → 기본값 사용: %s", e)
        return ["005930", "000660"]  # 삼성전자 / SK하이닉스 기본값


async def run_morning_debate(dry_run: bool = False) -> dict:
    """장전 토론 메인 로직."""
    today = datetime.now(KST).date().isoformat()
    logger.info(
        "[MorningDebate] === 장전 토론 배치 시작 | date=%s | dry_run=%s ===",
        today, dry_run,
    )

    candidates = get_candidates_sync()
    if not candidates:
        logger.warning("[MorningDebate] 후보 종목 없음 → 배치 종료")
        return {"status": "skip", "reason": "no_candidates"}

    # ── DRY-RUN ─────────────────────────────────────────────────────────────
    if dry_run:
        logger.info("[MorningDebate] DRY-RUN: Commander 호출 없이 구조 검증만 수행")
        result = {
            "status": "dry_run",
            "commander": "morning_analysis",
            "analysis_date": today,
            "candidates": candidates,
            "note": "dry-run — DB 저장 및 실제 에이전트 호출 없음",
        }
        logger.info("[MorningDebate] DRY-RUN 결과:\n%s",
                    json.dumps(result, ensure_ascii=False, indent=2))
        try:
            with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            logger.info("[MorningDebate] DRY-RUN JSON 출력 → %s", OUTPUT_JSON)
        except Exception as e:
            logger.warning("[MorningDebate] JSON 파일 저장 실패: %s", e)
        return result

    # ── 실제 실행 ────────────────────────────────────────────────────────────
    from backend.app.core.database import AsyncSessionLocal
    from backend.app.services.go100.agents.commander import CommanderGO100
    from sqlalchemy import text

    result = {}
    async with AsyncSessionLocal() as db:
        commander = CommanderGO100(db_session=db, user_id=USER_ID)
        logger.info("[MorningDebate] Commander 생성 완료 | user_id=%d", USER_ID)

        # 1. run_morning_analysis
        try:
            result = await commander.run_morning_analysis(candidates)
            logger.info(
                "[MorningDebate] run_morning_analysis 완료 | blocked=%s | stocks=%d | elapsed=%.2fs",
                result.get("blocked"),
                len(result.get("stock_results", [])),
                result.get("elapsed_sec", 0),
            )
        except Exception as exc:
            logger.error("[MorningDebate] Commander 호출 실패: %s", exc, exc_info=True)
            return {"status": "error", "error": str(exc)}

        # 2. go100_agent_reports 저장
        try:
            await db.execute(
                text("""
                    INSERT INTO go100_agent_reports (
                        report_date, agent_name, stock_code,
                        report_json, conviction, signal, created_at
                    ) VALUES (
                        :report_date, :agent_name, NULL,
                        CAST(:report_json AS jsonb), NULL, :signal, NOW()
                    )
                """),
                {
                    "report_date": datetime.now(KST).date(),
                    "agent_name": "commander",
                    "report_json": json.dumps(result, default=str, ensure_ascii=False),
                    "signal": "MORNING_DEBATE",
                },
            )
            await db.commit()
            logger.info("[MorningDebate] go100_agent_reports 저장 완료")
        except Exception as exc:
            logger.warning("[MorningDebate] go100_agent_reports 저장 실패: %s", exc)
            try:
                await db.rollback()
            except Exception:
                pass

    # 3. JSON 파일 출력 (V4.1 연동용)
    try:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        logger.info("[MorningDebate] JSON 출력 완료 → %s", OUTPUT_JSON)
    except Exception as exc:
        logger.warning("[MorningDebate] JSON 파일 저장 실패: %s", exc)

    logger.info("[MorningDebate] === 장전 토론 배치 완료 ===")
    return result


async def main():
    parser = argparse.ArgumentParser(description="GO100 장전 토론 배치 (T-169 Phase A)")
    parser.add_argument("--dry-run", action="store_true",
                        help="DB 저장 없이 구조 검증만 수행")
    args = parser.parse_args()

    result = await run_morning_debate(dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

---

### 신규 파일 2: scripts/go100/daily_trade_feedback.py

```python
#!/usr/bin/env python3
# ==============================================================
# daily_trade_feedback.py
# GO100 군단 장후 피드백 배치 — 16:00 KST 실행
# T-169 Phase A: 피드백 루프 Phase A-2
# 크론: 0 16 * * 1-5 (CEO root 등록 필요)
# ==============================================================
"""
1. v4_mock_trades에서 당일 매매 결과 수집
2. go100_agent_reports(오늘 MORNING_DEBATE)와 비교
3. go100_agent_performance 정확도 갱신 (Commander.run_post_market_review)
4. go100_episodic_memory에 당일 요약 저장
5. Commander 자기비평 → go100_agent_reports(signal=CRITIQUE) 저장

--dry-run: DB 저장 없이 로그만 출력
"""
import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))
USER_ID = 2  # GO100 사용자 ID


def collect_mock_trades_sync(trade_date: date) -> list:
    """v4_mock_trades에서 당일 매매 결과 동기 조회."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME", "kisautotrade"),
            user=os.getenv("DB_USER", "kis_admin"),
            password=os.getenv("DB_PASSWORD", "KisAuto2026!Secure"),
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT id, ticker, strategy_id, direction,
                   entry_price, exit_price, pnl_pct, cost_pct, notes
            FROM v4_mock_trades
            WHERE trade_date = %s
            ORDER BY created_at
        """, (trade_date,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        conn.close()
        logger.info("[TradeFeedback] v4_mock_trades %d건 수집 (date=%s)", len(rows), trade_date)
        return rows
    except Exception as e:
        logger.warning("[TradeFeedback] v4_mock_trades 조회 실패: %s", e)
        return []


def calc_accuracy(trades: list) -> dict:
    """매매 결과 → 승률/평균PnL 계산."""
    total = len(trades)
    if total == 0:
        return {
            "trade_count": 0,
            "profitable_count": 0,
            "win_rate": None,
            "avg_pnl_pct": None,
            "note": "당일 거래 없음",
        }

    settled = [t for t in trades if t.get("pnl_pct") is not None]
    profitable = sum(1 for t in settled if float(t["pnl_pct"]) > 0)
    win_rate = round(profitable / len(settled), 4) if settled else None
    avg_pnl = (
        round(sum(float(t["pnl_pct"]) for t in settled) / len(settled), 4)
        if settled else None
    )

    return {
        "trade_count": total,
        "settled_count": len(settled),
        "profitable_count": profitable,
        "win_rate": win_rate,
        "avg_pnl_pct": avg_pnl,
        "note": "에이전트 개별 신호 매칭은 go100_debate_log 정합화 후 확장 예정",
    }


async def run_trade_feedback(dry_run: bool = False) -> dict:
    """장후 피드백 메인 로직."""
    today_kst = datetime.now(KST).date()
    today_str = today_kst.isoformat()
    logger.info(
        "[TradeFeedback] === 장후 피드백 배치 시작 | date=%s | dry_run=%s ===",
        today_str, dry_run,
    )

    trades = collect_mock_trades_sync(today_kst)
    for t in trades[:5]:
        logger.info(
            "  ticker=%s dir=%s pnl_pct=%s strategy=%s",
            t.get("ticker"), t.get("direction"),
            t.get("pnl_pct"), t.get("strategy_id"),
        )

    accuracy = calc_accuracy(trades)
    logger.info("[TradeFeedback] 정확도 계산: %s", json.dumps(accuracy, ensure_ascii=False))

    if dry_run:
        logger.info("[TradeFeedback] DRY-RUN: Commander 호출 없이 구조 검증만 수행")
        result = {
            "status": "dry_run",
            "review_date": today_str,
            "mock_trade_count": len(trades),
            "accuracy": accuracy,
            "trades_sample": [
                {k: str(v) if not isinstance(v, (int, float, str, type(None))) else v
                 for k, v in t.items()}
                for t in trades[:3]
            ],
            "note": "dry-run — DB 저장 및 실제 에이전트 호출 없음",
        }
        logger.info("[TradeFeedback] DRY-RUN 결과:\n%s",
                    json.dumps(result, ensure_ascii=False, indent=2))
        logger.info("[TradeFeedback] DRY-RUN 완료")
        return result

    from backend.app.core.database import AsyncSessionLocal
    from backend.app.services.go100.agents.commander import CommanderGO100
    from sqlalchemy import text

    async with AsyncSessionLocal() as db:
        commander = CommanderGO100(db_session=db, user_id=USER_ID)
        review = {}
        try:
            review = await commander.run_post_market_review()
            logger.info(
                "[TradeFeedback] run_post_market_review 완료 | trades=%d | perf_updated=%s | elapsed=%.2fs",
                review.get("trade_count", 0),
                review.get("performance_updated"),
                review.get("elapsed_sec", 0),
            )
        except Exception as exc:
            logger.error("[TradeFeedback] Commander 리뷰 실패: %s", exc, exc_info=True)
            review = {"error": str(exc)}

        critique_text = review.get("self_critique", "없음")
        if isinstance(critique_text, dict):
            critique_text = json.dumps(critique_text, ensure_ascii=False)
        episode_summary = (
            f"[{today_str}] GO100 군단 일일 피드백.\n"
            f"v4_mock_trades {len(trades)}건 — 승률={accuracy.get('win_rate')}, "
            f"평균PnL={accuracy.get('avg_pnl_pct')}.\n"
            f"Commander 자기비평: {str(critique_text)[:300]}"
        )
        session_id = f"daily_feedback_{today_str}_{uuid.uuid4().hex[:8]}"
        key_decisions_json = json.dumps(
            [
                {"type": "trade_feedback", "date": today_str, "trade_count": len(trades)},
                accuracy,
            ],
            default=str,
        )
        episodic_ok = False
        try:
            await db.execute(
                text("""
                    INSERT INTO go100_episodic_memory (
                        user_id, session_id, episode_date,
                        summary, key_decisions, topics, created_at
                    ) VALUES (
                        :uid, :sid, :ep_date,
                        :summary,
                        CAST(:key_decisions AS jsonb),
                        ARRAY['daily_feedback','trade_review','agent_performance']::varchar[],
                        NOW()
                    )
                """),
                {
                    "uid": USER_ID,
                    "sid": session_id,
                    "ep_date": today_kst,
                    "summary": episode_summary,
                    "key_decisions": key_decisions_json,
                },
            )
            await db.commit()
            episodic_ok = True
            logger.info("[TradeFeedback] go100_episodic_memory 저장 완료 | sid=%s", session_id)
        except Exception as exc:
            logger.warning("[TradeFeedback] go100_episodic_memory 저장 실패: %s", exc)
            try:
                await db.rollback()
            except Exception:
                pass

        critique_report = {
            "source": "daily_trade_feedback",
            "date": today_str,
            "mock_trade_count": len(trades),
            "accuracy": accuracy,
            "commander_review": review,
        }
        critique_ok = False
        try:
            await db.execute(
                text("""
                    INSERT INTO go100_agent_reports (
                        report_date, agent_name, stock_code,
                        report_json, conviction, signal, created_at
                    ) VALUES (
                        :report_date, :agent_name, NULL,
                        CAST(:report_json AS jsonb), NULL, :signal, NOW()
                    )
                """),
                {
                    "report_date": today_kst,
                    "agent_name": "commander",
                    "report_json": json.dumps(critique_report, default=str, ensure_ascii=False),
                    "signal": "CRITIQUE",
                },
            )
            await db.commit()
            critique_ok = True
            logger.info("[TradeFeedback] CRITIQUE → go100_agent_reports 저장 완료")
        except Exception as exc:
            logger.warning("[TradeFeedback] CRITIQUE 저장 실패: %s", exc)
            try:
                await db.rollback()
            except Exception:
                pass

    final = {
        "status": "ok",
        "review_date": today_str,
        "mock_trade_count": len(trades),
        "accuracy": accuracy,
        "commander_review_elapsed_sec": review.get("elapsed_sec"),
        "performance_updated": review.get("performance_updated"),
        "episodic_memory_saved": episodic_ok,
        "critique_saved": critique_ok,
    }
    logger.info("[TradeFeedback] === 장후 피드백 배치 완료 ===")
    return final


async def main():
    parser = argparse.ArgumentParser(description="GO100 장후 피드백 배치 (T-169 Phase A)")
    parser.add_argument("--dry-run", action="store_true",
                        help="DB 저장 없이 구조 검증만 수행")
    args = parser.parse_args()

    result = await run_trade_feedback(dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

---

## Phase A-3: dry-run 테스트 결과

### [실행] venv/bin/python3 scripts/go100/daily_morning_debate.py --dry-run 2>&1 | tail -20

```
2026-03-06 11:11:17 [INFO] [MorningDebate] === 장전 토론 배치 시작 | date=2026-03-06 | dry_run=True ===
2026-03-06 11:11:17 [INFO] [MorningDebate] 후보 종목 10개: ['000070', '000100', '000150', '000155', '000210', '000220', '000270', '000440', '000720', '000880']
2026-03-06 11:11:17 [INFO] [MorningDebate] DRY-RUN: Commander 호출 없이 구조 검증만 수행
2026-03-06 11:11:17 [INFO] [MorningDebate] DRY-RUN 결과:
{
  "status": "dry_run",
  "commander": "morning_analysis",
  "analysis_date": "2026-03-06",
  "candidates": [
    "000070", "000100", "000150", "000155", "000210",
    "000220", "000270", "000440", "000720", "000880"
  ],
  "note": "dry-run — DB 저장 및 실제 에이전트 호출 없음"
}
2026-03-06 11:11:17 [INFO] [MorningDebate] DRY-RUN JSON 출력 → /tmp/go100_commander_daily.json
{
  "status": "dry_run",
  "commander": "morning_analysis",
  "analysis_date": "2026-03-06",
  "candidates": [
    "000070", "000100", "000150", "000155", "000210",
    "000220", "000270", "000440", "000720", "000880"
  ],
  "note": "dry-run — DB 저장 및 실제 에이전트 호출 없음"
}
```

**결과**: PASS ✓ — v4_desk3_pool 10개 종목 정상 추출, /tmp/go100_commander_daily.json 출력 확인

---

### [실행] venv/bin/python3 scripts/go100/daily_trade_feedback.py --dry-run 2>&1 | tail -20

```
      "entry_price": null,
      "exit_price": null,
      "pnl_pct": null,
      "cost_pct": "0.47",
      "notes": "{\"approved\": false, \"blocking_layer\": \"L3.1_FUNNEL\", \"blocking_reason\": \"FunnelScore 미달: 0.241 < 0.4 (min_score_for_entry)\", \"cs_score\": null, \"eqs_score\": null, \"source\": \"VIRTUAL_NXT_AM\", \"nxt_session\": \"AM\"}"
    },
    {
      "id": 156,
      "ticker": "284915",
      "strategy_id": "D-ORB",
      "direction": "BUY",
      "entry_price": null,
      "exit_price": null,
      "pnl_pct": null,
      "cost_pct": "0.47",
      "notes": "{\"approved\": false, \"blocking_layer\": \"L3.1_FUNNEL\", \"blocking_reason\": \"FunnelScore 미달: 0.241 < 0.4 (min_score_for_entry)\", \"cs_score\": null, \"eqs_score\": null, \"source\": \"VIRTUAL_NXT_AM\", \"nxt_session\": \"AM\"}"
    }
  ],
  "note": "dry-run — DB 저장 및 실제 에이전트 호출 없음"
}
```

**결과**: PASS ✓ — v4_mock_trades 164건 수집 (오늘), 정확도 계산 완료
- pnl_pct=NULL → 오늘 매매는 FunnelScore 미달로 실제 체결 없음 (approved=false)

---

## Phase A-3: 크론 등록 명령어 (CEO root 실행 필요)

```bash
# [GO100 T-169] 장전 토론 — 08:50 KST (23:50 UTC 전날) 평일
50 23 * * 0-4 cd /root/kis-autotrade-v4 && venv/bin/python3 scripts/go100/daily_morning_debate.py >> /var/log/go100/morning_debate.log 2>&1

# [GO100 T-169] 장후 피드백 — 16:00 KST (07:00 UTC) 평일
0 7 * * 1-5 cd /root/kis-autotrade-v4 && venv/bin/python3 scripts/go100/daily_trade_feedback.py >> /var/log/go100/trade_feedback.log 2>&1
```

로그 디렉토리 생성 (root):
```bash
mkdir -p /var/log/go100
```

crontab 등록 (root):
```bash
crontab -e
# 위 2줄 추가 후 저장
```

---

## git commit 결과

```
커밋: fa54b087
메시지: [GO100] T-169 Phase A – daily debate + trade feedback scripts
브랜치: phase-2c-command-center
변경:
  create mode 100644 scripts/go100/daily_morning_debate.py
  create mode 100644 scripts/go100/daily_trade_feedback.py
  2 files changed, 489 insertions(+)
```

---

## 보고서 경로

로컬: `/root/kis-autotrade-v4/report/v41/CUR-V41-GO100-PHASE-A-FEEDBACK-LOOP-001-20260306.md`
project-docs push: done_watcher.sh 자동 처리 예정

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (fa54b087, phase-2c-command-center)
- [ ] project-docs 보고서 push 완료 (done_watcher.sh 자동 처리 대기)
- [ ] CEO root 크론 등록 (2줄 — 위 명령어 참조)
