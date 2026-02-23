# CUR-GO100-HOTFIX-CRITICAL, 2026-02-23
# CUR-GO100-UNIFIED-SAVE-BE, 2026-02-23
# Modified by: CUR-GO100-BUNDLE4C, 2026-02-21
"""
GO100 BASE 오케스트레이터.
UNDERSTAND → DESIGN → BACKTEST → EVALUATE → (OPTIMIZE 루프 ≤5회) → PRESENT + DB 저장.
BUNDLE4C: 분봉 백테스트 우선, 일봉 폴백. AdvancedFilters 연동.
"""
import json
import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.go100.user_utils import get_effective_uid
from .schemas import (
    BaseAgentResponse,
    ConversationMessage,
    EvaluationResult,
    InvestmentStyle,
    OptimizationRecord,
    OrchestrationResult,
    StrategyDesign,
    UserIntent,
)
from .understand_agent import UnderstandAgent
from .design_agent import DesignAgent
from .evaluate_agent import Go100EvaluateAgent
from .optimize_agent import Go100OptimizeAgent
from .llm_client import LLMClient

from backend.app.services.go100.backtest.minute_simulator import Go100MinuteSimulator
from backend.app.services.go100.universe.advanced_filters import Go100AdvancedFilters

logger = logging.getLogger(__name__)

MAX_OPTIMIZE_LOOPS = 5
MAX_MINUTE_STOCKS = 50
MIN_MINUTE_STOCKS = 5

_STYLE_TO_STRATEGY_TYPE = {
    InvestmentStyle.SCALPING: "scalping",
    InvestmentStyle.DAY_TRADING: "daily",
    InvestmentStyle.SWING: "swing",
}


def _to_dict(obj) -> dict:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    return dict(obj)


class BaseOrchestrator:
    """
    전체 파이프라인 오케스트레이터.
    db=None → UNDERSTAND + DESIGN만 실행 (Phase 5 호환).
    db 있음 → 전체 파이프라인 (Phase 6).
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        understand_agent: Optional[UnderstandAgent] = None,
        design_agent: Optional[DesignAgent] = None,
        evaluate_agent: Optional[Go100EvaluateAgent] = None,
        optimize_agent: Optional[Go100OptimizeAgent] = None,
    ) -> None:
        self.llm_client     = llm_client     or LLMClient()
        self.understand_agent = understand_agent or UnderstandAgent(self.llm_client)
        self.design_agent   = design_agent   or DesignAgent(self.llm_client)
        self.evaluate_agent = evaluate_agent or Go100EvaluateAgent(self.llm_client)
        self.optimize_agent = optimize_agent or Go100OptimizeAgent(self.llm_client)

    async def process_message(
        self,
        user_id: int,
        user_message: str,
        conversation_history: Optional[list[ConversationMessage]] = None,
        db: Optional[AsyncSession] = None,
        risk_tolerance: str = "medium",
    ) -> BaseAgentResponse:
        """사용자 메시지 처리 → OrchestrationResult (또는 BaseAgentResponse)."""
        if conversation_history is None:
            conversation_history = []

        # ── 1. UNDERSTAND ──
        hist = [{"role": m.role, "content": m.content} for m in conversation_history]
        intent = await self.understand_agent.analyze(user_message, hist)

        # ── 2. 추가 정보 필요 ──
        if intent.needs_clarification:
            reply = await self.llm_client.call_reply({
                "action": "clarify",
                "intent": _to_dict(intent),
                "questions": intent.clarification_questions or [],
            })
            return OrchestrationResult(
                agent_name="UNDERSTAND",
                reply_to_user=reply,
                user_intent=intent,
                needs_more_info=True,
                status="needs_clarification",
            )

        # ── 3. DESIGN ──
        design = await self.design_agent.design(intent, user_message)
        design_dict = _to_dict(design)

        # ── 4. DB 없으면 DESIGN까지만 반환 (Phase 5 호환) ──
        if db is None:
            reply = await self.llm_client.call_reply({
                "action": "present_design",
                "intent": _to_dict(intent),
                "design": design_dict,
            })
            return BaseAgentResponse(
                agent_name="DESIGN",
                reply_to_user=reply,
                user_intent=intent,
                strategy_design=design,
                needs_more_info=False,
            )

        # ── 5. 전체 파이프라인 (Phase 6) ──
        return await self._run_full_pipeline(
            user_id=user_id,
            intent=intent,
            design=design,
            design_dict=design_dict,
            db=db,
            risk_tolerance=risk_tolerance,
            user_message=user_message,
        )

    async def _run_full_pipeline(
        self,
        user_id: int,
        intent: UserIntent,
        design: StrategyDesign,
        design_dict: dict,
        db: AsyncSession,
        risk_tolerance: str,
        user_message: str,
    ) -> OrchestrationResult:
        """BACKTEST → EVALUATE → OPTIMIZE 루프 → DB 저장."""

        # ── 5-a. DRAFT 카드 DB INSERT ──
        card_id = await self._insert_draft_card(user_id, design_dict, db, intent=intent)
        if card_id is None:
            # DB 저장 실패 시 DESIGN까지만
            reply = await self.llm_client.call_reply({
                "action": "present_design",
                "intent": _to_dict(intent),
                "design": design_dict,
            })
            return OrchestrationResult(
                agent_name="DESIGN",
                reply_to_user=reply,
                user_intent=intent,
                strategy_design=design,
                status="completed",
                error="카드 저장 실패, 전략 설계만 반환합니다.",
            )

        current_strategy = design_dict
        optimization_history: list[OptimizationRecord] = []
        best_result: Optional[dict] = None
        best_evaluation: Optional[EvaluationResult] = None
        best_score: float = -1.0

        # ── 5-b. BACKTEST → EVALUATE → OPTIMIZE 루프 ──
        for loop in range(MAX_OPTIMIZE_LOOPS + 1):
            # 백테스트 실행 (분봉 우선 → 일봉 폴백)
            bt_result = await self._run_backtest(card_id, current_strategy, db, user_id, intent=intent)
            if bt_result is None:
                logger.warning("PIPELINE: 백테스트 실패 (loop=%d)", loop)
                break

            # 평가
            evaluation = await self.evaluate_agent.evaluate(bt_result, risk_tolerance)
            logger.info(
                "PIPELINE loop=%d | passed=%s | score=%.1f",
                loop, evaluation.passed, evaluation.score,
            )

            # 최선 결과 추적
            if evaluation.score > best_score:
                best_score      = evaluation.score
                best_result     = bt_result
                best_evaluation = evaluation

            if evaluation.passed:
                break

            if loop >= MAX_OPTIMIZE_LOOPS:
                logger.info("PIPELINE: 최대 %d회 루프 소진 → 최선 결과 사용", MAX_OPTIMIZE_LOOPS)
                break

            # 최적화
            opt_record = await self.optimize_agent.optimize(
                strategy=current_strategy,
                evaluation=evaluation,
                risk_tolerance=risk_tolerance,
                iteration=loop + 1,
                previous_records=optimization_history,
            )
            optimization_history.append(opt_record)
            current_strategy = opt_record.optimized_strategy

            # 카드 파라미터 업데이트
            await self._update_card_params(card_id, current_strategy, db)

        # ── 5-c. 카드 BACKTESTED 상태로 확정 ──
        if best_result and best_evaluation:
            strategy_type = self._detect_strategy_type(current_strategy, intent)
            await self._finalize_card(card_id, best_result, best_evaluation, db, strategy_type)
        else:
            # 백테스트 결과 없으면 DRAFT 유지
            logger.warning("PIPELINE: 최종 백테스트 결과 없음 → DRAFT 유지 (card_id=%d)", card_id)

        # ── 5-d. 사용자 응답 생성 ──
        passed = best_evaluation.passed if best_evaluation else False
        loop_count = len(optimization_history)
        reply = await self.llm_client.call_reply({
            "action": "present_full_result",
            "intent": _to_dict(intent),
            "design": design_dict,
            "passed": passed,
            "score": best_score,
            "optimization_loops": loop_count,
            "warning": "" if passed else f"5회 최적화 후에도 목표 미달 (최고 점수 {best_score:.0f}점)",
        })
        strategy_name_saved = (current_strategy or design_dict).get("strategy_name") or "전략"
        save_message = f"\n\n전략카드 '{strategy_name_saved}'이(가) 저장되었습니다. 내 전략 탭에서 확인하세요."
        reply = (reply or "") + save_message

        return OrchestrationResult(
            agent_name="ORCHESTRATOR",
            reply_to_user=reply,
            user_intent=intent,
            strategy_design=design,
            status="completed",
            strategy_card_id=card_id,
            go100_card_id=card_id,
            backtest_result=best_result,
            evaluation=best_evaluation,
            optimization_history=optimization_history,
        )

    # ── 전략 유형 판별 헬퍼 ──

    @staticmethod
    def _detect_strategy_type(strategy: dict, intent: Optional[UserIntent] = None) -> str:
        """전략 유형 판별: risk_params.strategy_type → intent.investment_style → max_holding_days."""
        rp = strategy.get("risk_params") or {}
        # 1순위: LLM이 명시한 strategy_type
        st = rp.get("strategy_type")
        if st in ("scalping", "daily", "swing"):
            return st
        # 2순위: UserIntent.investment_style
        if intent is not None:
            mapped = _STYLE_TO_STRATEGY_TYPE.get(intent.investment_style)
            if mapped:
                return mapped
        # 3순위: max_holding_days
        mhd = rp.get("max_holding_days")
        if mhd is not None:
            mhd = int(mhd)
            if mhd <= 1:
                return "scalping"
            if mhd <= 5:
                return "daily"
            return "swing"
        return "daily"

    @staticmethod
    def _get_bar_interval(strategy_type: str, strategy: dict) -> int:
        """분봉 bar_interval: LLM 명시 → 기본값."""
        rp = strategy.get("risk_params") or {}
        bi = rp.get("bar_interval")
        if bi is not None:
            return max(1, int(bi))
        return {"scalping": 3, "daily": 3, "swing": 5}.get(strategy_type, 3)

    @staticmethod
    def _get_strategy_type_tag(strategy_type: str) -> str:
        return {"scalping": "[스캘핑]", "daily": "[데일리]", "swing": "[단기스윙]"}.get(strategy_type, "[데일리]")

    def _auto_strategy_name(self, design_dict: dict, intent: Optional[UserIntent] = None) -> str:
        """AI 대화 맥락 기반 자동 전략명. GO100 AI - {키워드} 전략 형식."""
        name = design_dict.get("strategy_name") or ""
        if name and name.strip() and name != "LLM 전략":
            return name.strip()
        sector = ""
        if intent and getattr(intent, "target_sectors", None) and intent.target_sectors:
            sector = (intent.target_sectors[0] or "").strip()
        if not sector and intent and getattr(intent, "target_keywords", None) and intent.target_keywords:
            sector = (intent.target_keywords[0] or "").strip()
        if not sector:
            sector = "AI"
        strategy_type = "일봉"
        rp = design_dict.get("risk_params") or {}
        if rp.get("strategy_type") in ("scalping", "daily", "swing"):
            strategy_type = {"scalping": "스캘핑", "daily": "데일리", "swing": "스윙"}.get(rp["strategy_type"], strategy_type)
        return f"GO100 AI - {sector} {strategy_type} 전략"

    # ── DB 헬퍼 ──

    async def _insert_draft_card(
        self, user_id: int, design_dict: dict, db: AsyncSession, intent: Optional[UserIntent] = None
    ) -> Optional[int]:
        """go100_strategy_cards에 DRAFT 카드 INSERT. 실패 시 None. user_id는 effective_uid로 변환."""
        try:
            effective_uid = await get_effective_uid(db, user_id)
            name = self._auto_strategy_name(design_dict, intent)
            if not name or not str(name).strip():
                name = "GO100 AI - LLM 전략"
            name = str(name).strip()[:200]
            result = await db.execute(
                text("""
                    INSERT INTO go100_strategy_cards (
                        user_id, strategy_name, strategy_type, source_type,
                        universe_filter, entry_rules, exit_rules, risk_params,
                        max_stocks, card_status, is_active
                    ) VALUES (
                        :user_id, :name, 'LLM_GENERATED', 'LLM',
                        CAST(:uf AS jsonb), CAST(:er AS jsonb),
                        CAST(:xr AS jsonb), CAST(:rp AS jsonb),
                        :max_stocks, 'DRAFT', true
                    )
                    RETURNING go100_card_id
                """),
                {
                    "user_id":    effective_uid,
                    "name":       name,
                    "uf":         json.dumps(design_dict.get("universe_filter") or {}),
                    "er":         json.dumps(design_dict.get("entry_rules") or []),
                    "xr":         json.dumps(design_dict.get("exit_rules") or []),
                    "rp":         json.dumps(design_dict.get("risk_params") or {}),
                    "max_stocks": design_dict.get("max_stocks", 5),
                },
            )
            await db.commit()
            card_id = result.scalar_one()
            logger.info("PIPELINE: DRAFT 카드 생성 (card_id=%d)", card_id)
            return card_id
        except Exception as e:
            logger.error("PIPELINE: 카드 INSERT 실패: %s", e, exc_info=True)
            await db.rollback()
            return None

    # ── 백테스트 (분봉 우선 → 일봉 폴백) ──

    async def _run_backtest(
        self,
        card_id: int,
        strategy: dict,
        db: AsyncSession,
        user_id: int = 0,
        intent: Optional[UserIntent] = None,
    ) -> Optional[dict]:
        """
        분봉 백테스트 우선 실행, 분봉 데이터 부족 시 일봉 폴백.
        BUNDLE4C: AdvancedFilters → MinuteSimulator → 분할익절 통합.
        """
        try:
            strategy_type = self._detect_strategy_type(strategy, intent)
            bar_interval = self._get_bar_interval(strategy_type, strategy)

            end_dt = date.today() - timedelta(days=1)
            start_dt = end_dt - timedelta(days=60)

            # 1. AdvancedFilters로 유니버스 구성 (실패 시 UniverseEngine 폴백)
            adv_codes = await self._build_advanced_universe(db, strategy_type, end_dt)

            # 2. 분봉 데이터 보유 종목 교집합
            minute_codes: list[str] = []
            if adv_codes:
                try:
                    adv_filters = Go100AdvancedFilters()
                    all_minute = await adv_filters.filter_has_minute_data(db, min_days=10)
                    minute_codes = [c for c in adv_codes if c in set(all_minute)]
                    logger.info(
                        "PIPELINE: AdvancedFilters %d종목 → 분봉보유 %d종목 (card_id=%d, type=%s)",
                        len(adv_codes), len(minute_codes), card_id, strategy_type,
                    )
                except Exception as e:
                    logger.warning("PIPELINE: 분봉 필터 실패: %s", e)

            # 3. 분봉 종목 충분하면 MinuteSimulator, 아니면 일봉 폴백
            if len(minute_codes) >= MIN_MINUTE_STOCKS:
                codes_for_minute = minute_codes[:MAX_MINUTE_STOCKS]
                result = await self._run_backtest_minute(
                    card_id, strategy, db, codes_for_minute, start_dt, end_dt, bar_interval,
                )
                if result is not None:
                    result["run_id"] = 0
                    result["go100_card_id"] = card_id
                    result["backtest_mode"] = "minute"
                    result["strategy_type"] = strategy_type
                    logger.info(
                        "PIPELINE: 분봉 백테스트 완료 (card_id=%d, trades=%d, return=%.2f%%, mdd=%.2f%%, mode=minute)",
                        card_id, result.get("total_trades", 0),
                        result.get("total_return", 0), result.get("max_drawdown", 0),
                    )
                    return result
                logger.warning("PIPELINE: 분봉 백테스트 실패 → 일봉 폴백 (card_id=%d)", card_id)

            # 4. 일봉 폴백
            pre_codes = adv_codes if adv_codes else None
            result = await self._run_backtest_daily(card_id, strategy, db, user_id, pre_codes=pre_codes)
            if result is not None:
                result["backtest_mode"] = "daily"
                result["strategy_type"] = strategy_type
            return result

        except Exception as e:
            logger.error("PIPELINE: 백테스트 실패 (card_id=%d): %s", card_id, e)
            return None

    async def _build_advanced_universe(
        self, db: AsyncSession, strategy_type: str, ref_date: date
    ) -> list[str]:
        """AdvancedFilters.build_universe 호출, 실패 시 빈 리스트."""
        try:
            adv_filters = Go100AdvancedFilters()
            codes = await adv_filters.build_universe(db, strategy_type, ref_date=ref_date)
            logger.info("PIPELINE: AdvancedFilters.build_universe → %d종목 (type=%s)", len(codes), strategy_type)
            return codes
        except Exception as e:
            logger.warning("PIPELINE: AdvancedFilters 실패 → UniverseEngine 폴백: %s", e)
            return []

    async def _run_backtest_minute(
        self,
        card_id: int,
        strategy: dict,
        db: AsyncSession,
        codes: list[str],
        start_dt: date,
        end_dt: date,
        bar_interval: int,
    ) -> Optional[dict]:
        """Go100MinuteSimulator를 사용한 분봉+분할익절 백테스트."""
        try:
            sim = Go100MinuteSimulator()
            result = await sim.run_backtest(
                db=db,
                strategy_config=strategy,
                universe_codes=codes,
                start_date=start_dt,
                end_date=end_dt,
                initial_capital=10_000_000.0,
                bar_interval=bar_interval,
            )
            return result
        except Exception as e:
            logger.error("PIPELINE: MinuteSimulator 실패 (card_id=%d): %s", card_id, e)
            return None

    async def _run_backtest_daily(
        self,
        card_id: int,
        strategy: dict,
        db: AsyncSession,
        user_id: int = 0,
        pre_codes: Optional[list[str]] = None,
    ) -> Optional[dict]:
        """
        오케스트레이터 전용 고속 일봉 백테스트.
        pre_codes 제공 시 UniverseEngine 스킵.
        """
        import pandas as pd
        from backend.app.services.go100.backtest.signal_evaluator import SignalEvaluator
        from backend.app.services.go100.backtest.simulator import (
            calc_performance_metrics, calc_fee, calc_tax_sell,
        )
        from backend.app.services.go100.universe.engine import UniverseEngine

        try:
            risk_params = strategy.get("risk_params") or {}
            entry_rules = strategy.get("entry_rules") or []
            exit_rules = strategy.get("exit_rules") or []
            max_stocks = int(risk_params.get("max_stocks") or 5)
            max_position_pct = float(risk_params.get("max_position_pct") or 20) / 100
            initial_capital = 10_000_000.0

            end_dt = date.today() - timedelta(days=1)
            start_dt = end_dt - timedelta(days=60)
            load_start = start_dt - timedelta(days=60)

            # 1. 거래일 목록
            r = await db.execute(
                text("SELECT DISTINCT date FROM ohlcv_daily WHERE date >= :s AND date <= :e ORDER BY date"),
                {"s": load_start.strftime("%Y%m%d"), "e": end_dt.strftime("%Y%m%d")},
            )
            all_dates = [row[0] for row in r.fetchall()]
            trade_dates = [d for d in all_dates if d >= start_dt.strftime("%Y%m%d")]
            if not trade_dates:
                return self._empty_bt_result(card_id)

            # 2. 유니버스 선택
            if pre_codes:
                codes = pre_codes[:200]
                logger.info("PIPELINE: 사전 유니버스 %d종목 사용 (card_id=%d)", len(codes), card_id)
            else:
                universe_filter = strategy.get("universe_filter") or {}
                engine = UniverseEngine()
                candidates = await engine.select_stocks(universe_filter, end_dt, db)
                codes = [c.code for c in candidates][:200]
            if not codes:
                return self._empty_bt_result(card_id)
            logger.info("PIPELINE: 일봉 유니버스 %d종목 (card_id=%d)", len(codes), card_id)

            # 3. 일봉 데이터 한 번 로드
            r = await db.execute(
                text("""
                    SELECT stock_code, date, open, high, low, close, volume
                    FROM ohlcv_daily
                    WHERE stock_code = ANY(:codes) AND date >= :s AND date <= :e
                    ORDER BY stock_code, date
                """),
                {"codes": codes, "s": load_start.strftime("%Y%m%d"), "e": end_dt.strftime("%Y%m%d")},
            )
            rows = r.fetchall()
            if not rows:
                return self._empty_bt_result(card_id)

            ohlcv_df = pd.DataFrame(rows, columns=["stock_code", "date", "open", "high", "low", "close", "volume"])
            for col in ("open", "high", "low", "close", "volume"):
                ohlcv_df[col] = pd.to_numeric(ohlcv_df[col], errors="coerce").fillna(0)

            evaluator = SignalEvaluator()
            capital = initial_capital
            positions: dict[str, dict] = {}
            trade_log: list[dict] = []
            equity_curve: list[dict] = []

            grouped = {}
            for sc in codes:
                sub = ohlcv_df[ohlcv_df["stock_code"] == sc].copy()
                if not sub.empty:
                    grouped[sc] = sub.set_index("date")

            stop_loss = float(risk_params.get("stop_loss_pct") or risk_params.get("max_loss_per_trade") or 5)
            take_profit = float(risk_params.get("take_profit_pct") or 10)

            # 4. 일별 시뮬레이션
            for day_ymd in trade_dates:
                day_str = f"{day_ymd[:4]}-{day_ymd[4:6]}-{day_ymd[6:]}"

                # exit 평가
                for sc in list(positions.keys()):
                    pos = positions[sc]
                    sc_data = grouped.get(sc)
                    if sc_data is None or day_ymd not in sc_data.index:
                        continue
                    close = float(sc_data.loc[day_ymd, "close"])
                    if close <= 0:
                        continue
                    ret_pct = (close / pos["entry_price"] - 1) * 100

                    should_exit = ret_pct <= -stop_loss or ret_pct >= take_profit
                    if not should_exit:
                        try:
                            exit_ok, _ = evaluator.evaluate_exit(sc, day_str, ohlcv_df, pos, exit_rules)
                            should_exit = exit_ok
                        except Exception:
                            pass

                    if should_exit:
                        sell_amount = close * pos["quantity"]
                        fee = calc_fee(sell_amount)
                        tax = calc_tax_sell(sell_amount)
                        capital += sell_amount - fee - tax
                        trade_log.append({
                            "stock_code": sc, "entry_date": pos["entry_date"],
                            "exit_date": day_str, "entry_price": pos["entry_price"],
                            "exit_price": close, "quantity": pos["quantity"],
                            "return_pct": round(ret_pct, 2),
                            "exit_reason": "stop_loss" if ret_pct <= -stop_loss else
                                           "take_profit" if ret_pct >= take_profit else "signal",
                        })
                        del positions[sc]

                # entry 평가
                if len(positions) < max_stocks:
                    for sc in codes:
                        if sc in positions or len(positions) >= max_stocks:
                            continue
                        sc_data = grouped.get(sc)
                        if sc_data is None or day_ymd not in sc_data.index:
                            continue
                        if not evaluator.evaluate_entry(sc, day_str, ohlcv_df, entry_rules):
                            continue
                        close = float(sc_data.loc[day_ymd, "close"])
                        if close <= 0:
                            continue
                        alloc = min(capital * max_position_pct, capital / max(1, max_stocks - len(positions)))
                        qty = int(alloc // close)
                        if qty <= 0:
                            continue
                        buy_amount = close * qty
                        fee = calc_fee(buy_amount)
                        capital -= buy_amount + fee
                        positions[sc] = {
                            "entry_price": close, "quantity": qty,
                            "entry_date": day_str,
                        }

                # equity 계산
                pos_eval = 0.0
                for sc, p in positions.items():
                    sc_data = grouped.get(sc)
                    if sc_data is not None and day_ymd in sc_data.index:
                        pos_eval += float(sc_data.loc[day_ymd, "close"]) * p["quantity"]
                equity_curve.append({"date": day_str, "equity": round(capital + pos_eval, 2)})

            # 5. 잔여 포지션 강제 청산
            for sc in list(positions.keys()):
                pos = positions[sc]
                sub = ohlcv_df[ohlcv_df["stock_code"] == sc]
                if sub.empty:
                    continue
                close = float(sub.iloc[-1]["close"])
                ret_pct = (close / pos["entry_price"] - 1) * 100
                sell_amount = close * pos["quantity"]
                capital += sell_amount - calc_fee(sell_amount) - calc_tax_sell(sell_amount)
                trade_log.append({
                    "stock_code": sc, "entry_date": pos["entry_date"],
                    "exit_date": trade_dates[-1][:4] + "-" + trade_dates[-1][4:6] + "-" + trade_dates[-1][6:],
                    "entry_price": pos["entry_price"], "exit_price": close,
                    "quantity": pos["quantity"], "return_pct": round(ret_pct, 2),
                    "exit_reason": "end_of_backtest",
                })

            metrics = calc_performance_metrics(equity_curve, trade_log, initial_capital)
            metrics["equity_curve"] = equity_curve[-30:]
            metrics["trade_log"] = trade_log
            metrics["run_id"] = 0
            metrics["go100_card_id"] = card_id

            logger.info(
                "PIPELINE: 일봉 백테스트 완료 (card_id=%d, trades=%d, return=%.2f%%, mdd=%.2f%%, mode=daily)",
                card_id, metrics["total_trades"], metrics["total_return"], metrics["max_drawdown"],
            )
            return metrics
        except Exception as e:
            logger.error("PIPELINE: 일봉 백테스트 실패 (card_id=%d, user_id=%d): %s", card_id, user_id, e)
            return None

    def _empty_bt_result(self, card_id: int) -> dict:
        return {
            "total_return": 0.0, "annual_return": 0.0, "max_drawdown": 0.0,
            "sharpe_ratio": 0.0, "win_rate": 0.0, "total_trades": 0,
            "profit_trades": 0, "loss_trades": 0, "avg_holding_days": 0.0,
            "equity_curve": [], "trade_log": [], "run_id": 0,
            "go100_card_id": card_id,
            "universe_stats": {}, "partial_exit_summary": {},
            "backtest_mode": "none", "strategy_type": "daily",
        }

    async def _update_card_params(
        self, card_id: int, strategy: dict, db: AsyncSession
    ) -> None:
        """최적화된 파라미터로 카드 UPDATE."""
        try:
            await db.execute(
                text("""
                    UPDATE go100_strategy_cards
                    SET universe_filter = CAST(:uf AS jsonb),
                        entry_rules     = CAST(:er AS jsonb),
                        exit_rules      = CAST(:xr AS jsonb),
                        risk_params     = CAST(:rp AS jsonb),
                        max_stocks      = :max_stocks,
                        updated_at      = now()
                    WHERE go100_card_id = :cid
                """),
                {
                    "uf":         json.dumps(strategy.get("universe_filter") or {}),
                    "er":         json.dumps(strategy.get("entry_rules") or []),
                    "xr":         json.dumps(strategy.get("exit_rules") or []),
                    "rp":         json.dumps(strategy.get("risk_params") or {}),
                    "max_stocks": strategy.get("max_stocks", 5),
                    "cid":        card_id,
                },
            )
            await db.commit()
        except Exception as e:
            logger.error("PIPELINE: 카드 UPDATE 실패: %s", e)
            await db.rollback()

    async def _finalize_card(
        self,
        card_id: int,
        backtest_result: dict,
        evaluation: EvaluationResult,
        db: AsyncSession,
        strategy_type: str = "daily",
    ) -> None:
        """카드 상태를 BACKTESTED로 업데이트 + 백테스트 결과 기록 + 유형 태그."""
        try:
            run_id = backtest_result.get("run_id")
            tag = self._get_strategy_type_tag(strategy_type)
            await db.execute(
                text("""
                    UPDATE go100_strategy_cards
                    SET card_status          = 'BACKTESTED',
                        last_backtest_id     = :run_id,
                        last_backtest_return = :ret,
                        last_backtest_mdd    = :mdd,
                        last_backtest_sharpe = :sharpe,
                        last_backtest_at     = now(),
                        strategy_name = CASE
                            WHEN strategy_name NOT LIKE '[%' THEN :tag || ' ' || strategy_name
                            ELSE strategy_name
                        END,
                        updated_at           = now()
                    WHERE go100_card_id = :cid
                """),
                {
                    "run_id": run_id,
                    "ret":    backtest_result.get("total_return"),
                    "mdd":    backtest_result.get("max_drawdown"),
                    "sharpe": backtest_result.get("sharpe_ratio"),
                    "tag":    tag,
                    "cid":    card_id,
                },
            )
            await db.commit()
            logger.info(
                "PIPELINE: 카드 BACKTESTED 확정 (card_id=%d, run_id=%s, score=%.1f, return=%.2f%%, mdd=%.2f%%, type=%s)",
                card_id, run_id, evaluation.score,
                float(backtest_result.get("total_return", 0)),
                float(backtest_result.get("max_drawdown", 0)),
                strategy_type,
            )
        except Exception as e:
            logger.error("PIPELINE: 카드 FINALIZE 실패: %s", e)
            await db.rollback()
