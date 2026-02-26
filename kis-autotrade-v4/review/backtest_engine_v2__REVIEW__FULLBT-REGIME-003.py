# CODE REVIEW REQUEST — CUR-FULLBT-REGIME-003
# 변경: desk_id 루프에 1 추가 (2,3,4,5) → (1,2,3,4,5)
# CEO 승인: 2026-02-24

# Modified by CUR-ENGLINK, 2026-02-21
# Modified by CUR-LOGFIX, 2026-02-21
# Modified by CUR-BTREADY, 2026-02-21
# Modified by: CUR-BT-ENHANCE, 2026-02-21
# Modified by: CC-BT-CAPSAFE, 2026-02-21
# Modified by: CC-DESK2-MINUTE-BT, 2026-02-21
# Modified by: CUR-BT-ALLOC-FIX, 2026-02-21
"""
백테스트 엔진 V2. 분할매수/분할매도/multi-day/승격 구현.
라이브 DESK 전략 반영. ohlcv_daily SELECT-only.
분봉 모드: 일봉 스크리닝 + 분봉 entry/exit 시뮬레이션.
작성: CUR-2026-0220-P1
"""
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import psycopg2

from scripts.backtest.config import (
    FEE_RATE,
    MAX_VOLUME_RATIO,
    SELL_SLIPPAGE_PCT,
    SLIPPAGE_PCT,
    TAX_RATE,
)
from scripts.backtest.signal_generator import (
    BacktestSignalGenerator,
    MarketRegimeFilter,
    Signal,
    StockFlowFilter,
)

logger = logging.getLogger(__name__)


def _db_row_to_desk_config(
    entry_rules: Optional[dict],
    exit_rules: Optional[dict],
    risk_params: Optional[dict],
    buy_phases: Optional[list],
    sell_phases: Optional[list],
    promotion_rules: Optional[dict],
    demotion_rules: Optional[dict],
) -> dict:
    """
    strategy_cards JSONB 한 행을 V2_DESK_CONFIGS와 동일한 키 구조로 변환.
    누락 키는 호출부 _merge_with_fallback에서 config.py로 보충.
    """
    cfg: Dict[str, Any] = {}
    if exit_rules and isinstance(exit_rules, dict):
        if "stop_loss_pct" in exit_rules and exit_rules["stop_loss_pct"] is not None:
            cfg["max_loss_pct"] = float(exit_rules["stop_loss_pct"])
        if "trailing_stop_pct" in exit_rules and exit_rules["trailing_stop_pct"] is not None:
            v = float(exit_rules["trailing_stop_pct"])
            cfg["trailing_stop_pct"] = -abs(v) if v > 0 else v
        if "max_hold_days" in exit_rules and exit_rules["max_hold_days"] is not None:
            cfg["max_hold_days"] = int(exit_rules["max_hold_days"])
        if "eod_force_exit" in exit_rules:
            cfg["eod_close"] = bool(exit_rules["eod_force_exit"])
        if "target_profit_pct" in exit_rules and exit_rules["target_profit_pct"] is not None:
            cfg["target_pct"] = float(exit_rules["target_profit_pct"])
    if risk_params and isinstance(risk_params, dict):
        if "max_positions" in risk_params and risk_params["max_positions"] is not None:
            cfg["max_positions"] = int(risk_params["max_positions"])
        if "max_concurrent_positions" in risk_params and risk_params["max_concurrent_positions"] is not None:
            cfg["max_concurrent_positions"] = int(risk_params["max_concurrent_positions"])
        if "max_capital_usage_pct" in risk_params and risk_params["max_capital_usage_pct"] is not None:
            cfg["max_capital_usage_pct"] = float(risk_params["max_capital_usage_pct"])
        if "max_single_position_pct" in risk_params and risk_params["max_single_position_pct"] is not None:
            cfg["max_single_position_pct"] = float(risk_params["max_single_position_pct"])
        if "max_daily_entries" in risk_params and risk_params["max_daily_entries"] is not None:
            cfg["max_daily_entries"] = int(risk_params["max_daily_entries"])
    if promotion_rules and isinstance(promotion_rules, dict):
        if "target_desk" in promotion_rules:
            cfg["promote_to"] = promotion_rules["target_desk"]
        if "condition" in promotion_rules:
            cfg["promote_condition"] = promotion_rules["condition"]
    if buy_phases and isinstance(buy_phases, list):
        phases = []
        for p in buy_phases:
            if not isinstance(p, dict):
                continue
            phase_cfg = dict(p)
            if "trigger" in phase_cfg and "condition" not in phase_cfg:
                phase_cfg["condition"] = phase_cfg["trigger"]
            if "delay_minutes" in phase_cfg and "delay_days" not in phase_cfg:
                phase_cfg["delay_days"] = max(1, phase_cfg["delay_minutes"] // (24 * 60))
            phases.append(phase_cfg)
        if phases:
            cfg["buy_phases"] = phases
    if sell_phases and isinstance(sell_phases, list):
        phases = []
        for p in sell_phases:
            if isinstance(p, dict):
                phases.append(dict(p))
        if phases:
            cfg["sell_phases"] = phases
    return cfg


@dataclass
class DeskFund:
    desk_id: int
    total: float
    available: float


@dataclass
class Position:
    """V2 포지션 — 분할매수/매도 지원. BT-ENGINE-UPGRADE: trough_price(MAE) 추가."""
    stock_code: str
    desk_id: int
    entry_date: date
    entry_price: float
    current_qty: int
    total_invested: float
    buy_phase: int
    sell_phase: int
    peak_price: float
    trough_price: float  # MAE: 최저가 (진입 후)
    days_held: int
    pending_buys: List[Dict[str, Any]] = field(default_factory=list)
    sold_qty: int = 0
    promoted_from: Optional[int] = None
    card_id: Optional[int] = None  # CUR-BTREADY: 전략 카드 추적


def _db_params() -> dict:
    return {
        "dbname": os.environ.get("DB_NAME", "kisautotrade"),
        "user": os.environ.get("DB_USER", "kis_admin"),
        "host": os.environ.get("DB_HOST", "localhost"),
        "password": os.environ.get("DB_PASSWORD", ""),
    }


class BacktestEngineV2:
    def __init__(
        self,
        db_params: dict,
        session_name: str,
        start_date: date,
        end_date: date,
        initial_capital: int,
        signal_generator: Optional[BacktestSignalGenerator] = None,
        timeframe: str = "daily",
        minute_lookback_days: int = 5,
    ):
        self.db_params = db_params or _db_params()
        self.session_name = session_name
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.signal_generator = signal_generator
        self.timeframe = (timeframe or "daily").lower()
        self.minute_lookback_days = minute_lookback_days
        self.session_id: Optional[int] = None
        self.ohlcv_data: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.positions: List[Position] = []
        self.desk_funds: Dict[int, DeskFund] = {}
        self.total_cash: float = 0.0
        self.trades: List[Dict[str, Any]] = []
        self._conn = None
        self.minute_loader = None
        self.minute_indicators = None
        self.minute_evaluator = None
        if self.timeframe == "minute":
            from scripts.backtest.minute_condition_evaluator import MinuteConditionEvaluator
            from scripts.backtest.minute_indicators import MinuteIndicatorCalculator
            self.minute_indicators = MinuteIndicatorCalculator()
            self.minute_evaluator = MinuteConditionEvaluator()

    def _get_connection(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(**self.db_params)
        return self._conn

    def _conn_cursor(self):
        return self._get_connection().cursor()

    def _load_strategy_from_db(
        self, stage: int = 1, desk_strategies: Optional[List[dict]] = None
    ) -> Optional[dict]:
        """
        strategy_cards + v4_desk_strategy_mapping에서 전략 파라미터 로드.
        desk_strategies가 주어지면 해당 card_id만 로드; 없으면 stage 기반 전체 로드.
        DB에 데이터 없으면 None 반환 → 호출부에서 config.py fallback.

        desk_strategies 예: [{"desk_id": 2, "card_id": 6}, ...]

        Returns:
            dict: { desk_id: { "config": {...}, "allocation_pct": N, "strategies": [...] } }
            또는 None (DB 데이터 없음)
        """
        cur = self._conn_cursor()
        if desk_strategies:
            card_ids = [ds["card_id"] for ds in desk_strategies]
            cur.execute(
                """
                SELECT s.desk_id::int AS desk_id, s.card_id, s.strategy_name,
                       s.entry_rules, s.exit_rules, s.risk_params,
                       s.buy_phases, s.sell_phases,
                       s.promotion_rules, s.demotion_rules,
                       COALESCE(m.allocation_pct, 20)::float AS allocation_pct
                FROM strategy_cards s
                LEFT JOIN v4_desk_strategy_mapping m
                  ON s.card_id = m.card_id AND m.stage_id = %s
                WHERE s.card_id = ANY(%s)
                  AND s.backtest_compatible = true
                ORDER BY s.desk_id::int
                """,
                (stage, card_ids),
            )
        else:
            cur.execute(
                """
                SELECT
                    m.desk_id,
                    m.card_id,
                    m.allocation_pct,
                    m.is_active,
                    s.strategy_name,
                    s.entry_rules,
                    s.exit_rules,
                    s.risk_params,
                    s.buy_phases,
                    s.sell_phases,
                    s.promotion_rules,
                    s.demotion_rules
                FROM v4_desk_strategy_mapping m
                JOIN strategy_cards s ON m.card_id = s.card_id
                WHERE m.stage_id = %s
                  AND m.is_active = true
                  AND s.backtest_compatible = true
                ORDER BY m.desk_id, m.allocation_pct DESC, m.card_id
                """,
                (stage,),
            )
        rows = cur.fetchall()
        cur.close()
        if not rows:
            logger.warning("DB에 활성 전략 매핑 없음, config.py fallback")
            return None
        # desk_strategies 분기면 컬럼 순서가 다름 → (desk_id, card_id, alloc, _, name, entry, exit, risk, buy, sell, prom, dem) 12-tuple로 통일
        if desk_strategies:
            rows = [
                (
                    r[0], r[1], r[10], None, r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9],
                )
                for r in rows
            ]
        total_alloc = sum(float(r[2]) for r in rows)
        if not desk_strategies and (total_alloc < 95 or total_alloc > 105):
            logger.warning(
                "DB allocation_pct 합계 %.1f%% (95~105%% 범위 아님)", total_alloc
            )
        by_desk: Dict[int, Dict[str, Any]] = {}
        for r in rows:
            desk_id = int(r[0])
            card_id = int(r[1])
            allocation_pct = float(r[2])
            strategy_name = r[4]
            entry_rules, exit_rules, risk_params = r[5], r[6], r[7]
            buy_phases, sell_phases = r[8], r[9]
            promotion_rules, demotion_rules = r[10], r[11]
            if desk_id not in by_desk:
                config = _db_row_to_desk_config(
                    entry_rules, exit_rules, risk_params,
                    buy_phases, sell_phases, promotion_rules, demotion_rules,
                )
                by_desk[desk_id] = {
                    "config": config,
                    "allocation_pct": allocation_pct,
                    "strategies": [
                        {
                            "card_id": card_id,
                            "name": strategy_name,
                            "allocation_pct": allocation_pct,
                            "entry_rules": entry_rules,
                        }
                    ],
                }
            else:
                by_desk[desk_id]["allocation_pct"] += allocation_pct
                by_desk[desk_id]["strategies"].append(
                    {
                        "card_id": card_id,
                        "name": strategy_name,
                        "allocation_pct": allocation_pct,
                        "entry_rules": entry_rules,
                    }
                )
        return by_desk

    def _merge_with_fallback(self, db_config: dict, desk_id: int) -> dict:
        """
        DB에서 로드한 DESK 설정에 누락 키가 있으면 config.py V2_DESK_CONFIGS에서 보충.
        DB 값 우선, 누락분만 config.py에서 가져옴.
        """
        from scripts.backtest.config import V2_DESK_CONFIGS
        fallback = V2_DESK_CONFIGS.get(desk_id, {})
        return {**fallback, **db_config}

    def _load_ohlcv(self) -> None:
        """ohlcv_daily SELECT-only. 시그널 지표용 lookback(130일) 포함."""
        lookback = timedelta(days=130)
        load_start = self.start_date - lookback
        load_start_s = load_start.strftime("%Y%m%d")
        end_s = self.end_date.strftime("%Y%m%d")
        cur = self._conn_cursor()
        cur.execute(
            """
            SELECT date, stock_code, open, high, low, close, volume
            FROM ohlcv_daily
            WHERE date >= %s AND date <= %s
            ORDER BY date
            """,
            (load_start_s, end_s),
        )
        for row in cur.fetchall():
            dt, code, o, h, l, c, v = row
            if dt not in self.ohlcv_data:
                self.ohlcv_data[dt] = {}
            self.ohlcv_data[dt][code] = {
                "open": float(o or 0),
                "high": float(h or 0),
                "low": float(l or 0),
                "close": float(c or 0),
                "volume": int(v or 0),
            }
        cur.close()
        logger.info(
            "V2 loaded ohlcv_daily: %s ~ %s, %d dates",
            load_start_s, end_s, len(self.ohlcv_data),
        )

    def _load_market_regime_data(self) -> tuple:
        """V-KOSPI + 시장 투자자 수급 로드."""
        conn = self._get_connection()
        cur = conn.cursor()

        vkospi_data = {}
        cur.execute("SELECT date, close, change_rate FROM v4_vkospi_daily ORDER BY date")
        for row in cur.fetchall():
            dt = row[0].strftime("%Y%m%d") if hasattr(row[0], "strftime") else str(row[0]).replace("-", "")
            vkospi_data[dt] = {"close": row[1], "change_rate": row[2]}

        market_investor_data = {}
        cur.execute(
            """
            SELECT trade_date, foreign_net_amount, institution_net_amount
            FROM v4_market_investor_daily
            WHERE market = 'KSP'
            ORDER BY trade_date
            """
        )
        for row in cur.fetchall():
            dt = row[0].strftime("%Y%m%d") if hasattr(row[0], "strftime") else str(row[0]).replace("-", "")
            market_investor_data[dt] = {
                "foreign_net_amount": row[1],
                "institution_net_amount": row[2],
            }

        cur.close()
        logger.info(
            "[FOREST] MarketRegimeFilter 로드 완료 — vkospi: %d건, market_investor: %d건",
            len(vkospi_data), len(market_investor_data),
        )
        if len(vkospi_data) == 0 and len(market_investor_data) == 0:
            logger.warning("[FOREST] vkospi/market_investor 데이터 0건 — 필터 비활성")
        return vkospi_data, market_investor_data

    def _load_investor_data(self, start_date: str, end_date: str) -> dict:
        """종목별 투자자 수급 로드."""
        conn = self._get_connection()
        cur = conn.cursor()

        investor_data = {}
        cur.execute(
            """
            SELECT trade_date, stock_code,
                   foreign_net_qty, institution_net_qty,
                   consecutive_foreign_buy_days, consecutive_institution_buy_days
            FROM v4_investor_daily
            WHERE trade_date >= %s AND trade_date <= %s
            """,
            (start_date, end_date),
        )
        for row in cur.fetchall():
            dt = row[0].strftime("%Y%m%d") if hasattr(row[0], "strftime") else str(row[0]).replace("-", "")
            code = row[1]
            if dt not in investor_data:
                investor_data[dt] = {}
            investor_data[dt][code] = {
                "foreign_net_qty": row[2],
                "institution_net_qty": row[3],
                "consecutive_foreign_buy_days": row[4],
                "consecutive_institution_buy_days": row[5],
            }

        cur.close()
        logger.info(
            "[TREE] StockFlowFilter 로드 완료 — investor: %d건, 기간: %s~%s",
            len(investor_data), start_date, end_date,
        )
        if len(investor_data) == 0:
            logger.warning("[TREE] investor 데이터 0건 — 필터 비활성")
        return investor_data

    def _update_session_status(self, status: str, error_message: Optional[str] = None) -> None:
        """세션 상태 갱신 (실패 시 FAILED 기록)."""
        cur = self._conn_cursor()
        cur.execute(
            """
            UPDATE v4_backtest_sessions
            SET status = %s, completed_at = NOW()
            WHERE session_id = %s
            """,
            (status, self.session_id),
        )
        self._conn.commit()
        cur.close()
        if error_message:
            logger.error("Session %s → %s: %s", self.session_id, status, error_message)

    def _create_session(self, stage: int) -> None:
        cur = self._conn_cursor()
        desk_configs = getattr(self, "desk_configs", None)
        if desk_configs is None:
            from scripts.backtest.config import V2_DESK_CONFIGS
            desk_configs = V2_DESK_CONFIGS
        cur.execute(
            """
            INSERT INTO v4_backtest_sessions
            (session_name, start_date, end_date, initial_capital, stage_config, desk_configs, split_configs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'RUNNING')
            RETURNING session_id
            """,
            (
                self.session_name,
                self.start_date,
                self.end_date,
                self.initial_capital,
                json.dumps({"stage": stage, "engine": "v2"}),
                json.dumps({str(k): v for k, v in desk_configs.items()}),
                json.dumps({}),
            ),
        )
        self.session_id = cur.fetchone()[0]
        self._conn.commit()
        cur.close()

    def _calc_volume_ma(
        self,
        date_str: str,
        ohlcv: Dict[str, Dict[str, Dict[str, Any]]],
        dates: List[str],
        day_data: Dict[str, Dict[str, Any]],
    ) -> None:
        """day_data 내 종목에 volume_ma20 추가 (과거 20일 평균 거래량)."""
        try:
            idx = dates.index(date_str)
        except ValueError:
            idx = len(dates)
        start_idx = max(0, idx - 20)
        for code in list(day_data.keys()):
            vols = []
            for i in range(start_idx, idx):
                d = dates[i]
                row = ohlcv.get(d, {}).get(code, {})
                v = row.get("volume") or 0
                vols.append(int(v))
            day_data[code]["volume_ma20"] = (
                sum(vols) / len(vols) if vols else day_data[code].get("volume") or 0
            )

    def _normalize_exit_reason(self, reason: str) -> Optional[str]:
        """reason을 v4_backtest_trades.exit_reason 허용값 5개 중 하나로 매핑. BUY/비청산용은 None."""
        if not reason:
            return None
        r = (reason or "").strip()
        if r in ("STOP_LOSS", "TRAILING_STOP", "TIME_EXIT", "END_OF_BACKTEST", "EOD_FORCE_EXIT"):
            return r
        if r == "EOD_CLOSE":
            return "EOD_FORCE_EXIT"
        if r == "GAP_DOWN":
            return "STOP_LOSS"
        if r.startswith("SELL_PHASE_") or r.startswith("PROMOTE_"):
            return "TRAILING_STOP"
        return "TRAILING_STOP"

    def _record_trade(
        self,
        pos: Position,
        qty: int,
        price: float,
        trade_date: date,
        reason: str,
        trade_type: str = "SELL",
        *,
        entry_datetime=None,
        exit_datetime=None,
        entry_price=None,
        exit_price=None,
        mfe_pct=None,
        mae_pct=None,
        mfe_price=None,
        mae_price=None,
        regime_at_entry=None,
        indicator_snapshot=None,
        slippage_pct=None,
        commission=None,
        sector=None,
        strategy_name=None,
        entry_volume=None,
        entry_spread_pct=None,
    ) -> None:
        """거래 기록 DB INSERT 및 메모리 저장. BT-ENGINE-UPGRADE: entry/exit datetime, MFE/MAE, strategy_name, commission 등 확장."""
        if trade_type == "BUY":
            amount = qty * price * (1 + FEE_RATE)
            pnl, pnl_pct = None, None
            split_phase = getattr(pos, "buy_phase", 0)
            entry_date = trade_date
            exit_reason = None
            exit_date = None
            hold_days = None
            _entry_price = entry_price if entry_price is not None else price
            _exit_price = None
            _entry_dt = entry_datetime or getattr(self, "_current_minute_time", None)
            _exit_dt = None
            _mfe_pct = _mfe_price = _mae_pct = _mae_price = None
            _commission = commission if commission is not None else round(price * qty * FEE_RATE, 2)
        else:
            amount = qty * price * (1 - FEE_RATE - TAX_RATE) if qty > 0 else 0
            if qty > 0 and pos.entry_price and pos.entry_price > 0:
                pnl = (price - pos.entry_price) * qty
                pnl_pct = (price - pos.entry_price) / pos.entry_price * 100
            else:
                pnl, pnl_pct = None, None
            split_phase = getattr(pos, "sell_phase", 0)
            entry_date = pos.entry_date
            exit_reason = self._normalize_exit_reason(reason)
            exit_date = trade_date
            hold_days = (trade_date - pos.entry_date).days if pos.entry_date else None
            _entry_price = entry_price if entry_price is not None else pos.entry_price
            _exit_price = exit_price if exit_price is not None else price
            _entry_dt = entry_datetime or getattr(self, "_current_minute_time", None)
            _exit_dt = exit_datetime or getattr(self, "_current_minute_time", None)
            peak = getattr(pos, "peak_price", None) or _entry_price
            trough = getattr(pos, "trough_price", None) or _entry_price
            if _entry_price and _entry_price > 0:
                _mfe_price = mfe_price if mfe_price is not None else peak
                _mae_price = mae_price if mae_price is not None else trough
                _mfe_pct = mfe_pct if mfe_pct is not None else round((peak - _entry_price) / _entry_price * 100, 4)
                _mae_pct = mae_pct if mae_pct is not None else round((trough - _entry_price) / _entry_price * 100, 4)
            else:
                _mfe_pct = _mae_pct = _mfe_price = _mae_price = None
            _commission = commission if commission is not None else round(price * qty * FEE_RATE, 2)
        _strategy_name = strategy_name or (getattr(self, "_card_name_map", None) or {}).get(getattr(pos, "card_id", None))
        if _strategy_name and len(_strategy_name) > 100:
            _strategy_name = _strategy_name[:97] + "..."
        ind_snap = json.dumps(indicator_snapshot) if isinstance(indicator_snapshot, dict) else indicator_snapshot
        cur = self._conn_cursor()
        cur.execute(
            """
            INSERT INTO v4_backtest_trades
            (session_id, desk_id, stock_code, trade_date, trade_type, quantity, price, amount, split_phase, transfer_to, pnl, pnl_pct, reason, card_id, exit_reason, entry_date, exit_date, hold_days,
             entry_datetime, exit_datetime, entry_price, exit_price, mfe_pct, mae_pct, mfe_price, mae_price, regime_at_entry, indicator_snapshot, slippage_pct, commission, sector, strategy_name, entry_volume, entry_spread_pct)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                self.session_id,
                pos.desk_id,
                pos.stock_code,
                trade_date,
                trade_type,
                qty,
                round(price, 2),
                int(amount),
                split_phase,
                None,
                int(pnl) if pnl is not None else None,
                round(pnl_pct, 4) if pnl_pct is not None else None,
                reason[:100] if reason else None,
                getattr(pos, "card_id", None),
                exit_reason,
                entry_date,
                exit_date,
                hold_days,
                _entry_dt,
                _exit_dt,
                round(_entry_price, 2) if _entry_price is not None else None,
                round(_exit_price, 2) if _exit_price is not None else None,
                _mfe_pct,
                _mae_pct,
                round(_mfe_price, 2) if _mfe_price is not None else None,
                round(_mae_price, 2) if _mae_price is not None else None,
                regime_at_entry,
                ind_snap,
                slippage_pct,
                _commission,
                sector,
                _strategy_name,
                entry_volume,
                entry_spread_pct,
            ),
        )
        self._conn.commit()
        cur.close()
        self.trades.append({
            "desk_id": pos.desk_id,
            "stock_code": pos.stock_code,
            "trade_date": trade_date,
            "side": trade_type,
            "qty": qty,
            "price": price,
            "reason": reason,
        })

    def _close_position(self, pos: Position, price: float, trade_date: date, reason: str) -> None:
        """포지션 전량 청산."""
        sell_price = price * (1 - SELL_SLIPPAGE_PCT)
        proceeds = pos.current_qty * sell_price * (1 - FEE_RATE - TAX_RATE)
        self.desk_funds[pos.desk_id].available += proceeds
        self._record_trade(pos, pos.current_qty, sell_price, trade_date, reason, trade_type="SELL")
        pos.sold_qty += pos.current_qty
        pos.current_qty = 0

    def _calc_portfolio_value(self, day_data: Dict[str, Dict[str, Any]]) -> float:
        """현재 보유 평가액 (종가 기준)."""
        value = 0.0
        for pos in self.positions:
            if pos.current_qty <= 0:
                continue
            code = pos.stock_code
            if code in day_data:
                value += pos.current_qty * day_data[code].get("close", pos.entry_price)
            else:
                value += pos.current_qty * pos.entry_price
        return value

    def _check_position_safety(
        self,
        desk_id: int,
        stock_code: str,
        buy_amount: float,
        current_date: date,
    ) -> tuple:
        """
        BUY 실행 전 자본 안전장치 검사. CC-BT-CAPSAFE.
        Returns (is_safe: bool, reason: str). 통과 시 (True, ""), 실패 시 (False, "사유").
        체크 순서: max_concurrent → max_capital_usage → max_single_position → max_daily_entries.
        """
        desk_cfg = self.desk_configs.get(desk_id, {})
        desk_fund = self.desk_funds.get(desk_id)
        if not desk_fund or desk_fund.total <= 0:
            return (False, "no desk fund")
        desk_positions = [p for p in self.positions if p.desk_id == desk_id]

        max_concurrent = desk_cfg.get("max_concurrent_positions", 10)
        if len(desk_positions) >= max_concurrent:
            return (
                False,
                "max_concurrent_positions %d/%d" % (len(desk_positions), max_concurrent),
            )

        current_usage = sum(p.total_invested for p in desk_positions)
        cap_pct = desk_cfg.get("max_capital_usage_pct", 80.0)
        usage_pct = (current_usage + buy_amount) / desk_fund.total * 100
        if usage_pct > cap_pct:
            return (
                False,
                "max_capital_usage %.1f%%/%.1f%%" % (usage_pct, cap_pct),
            )

        single_pct = desk_cfg.get("max_single_position_pct", 10.0)
        cap_single = self.initial_capital * single_pct / 100
        if buy_amount > cap_single:
            return (
                False,
                "max_single_position %.0f/%.0f" % (buy_amount, cap_single),
            )

        today_entries = len(
            [p for p in desk_positions if p.entry_date == current_date]
        )
        max_daily = desk_cfg.get("max_daily_entries", 20)
        if today_entries >= max_daily:
            return (
                False,
                "max_daily_entries %d/%d" % (today_entries, max_daily),
            )
        return (True, "")

    def process_pending_buys(
        self,
        trade_date: date,
        date_str: str,
        day_data: Dict[str, Dict[str, Any]],
    ) -> None:
        """예약된 추가 매수 처리."""
        for pos in self.positions:
            if not pos.pending_buys:
                continue
            code = pos.stock_code
            if code not in day_data:
                continue
            desk_cfg = self.desk_configs.get(pos.desk_id, {})
            next_pending = pos.pending_buys[0]
            days_since_entry = (trade_date - pos.entry_date).days
            min_delay = next_pending.get("delay_days") or 1
            delay_range = next_pending.get("delay_days_range")
            if delay_range:
                min_delay = delay_range[0] if delay_range[0] is not None else min_delay
            if days_since_entry < min_delay:
                continue

            should_buy = False
            current_price = day_data[code]["open"]

            if next_pending.get("condition") == "next_day_open":
                should_buy = True
            elif next_pending.get("condition") == "dip_or_confirm":
                pnl_pct = (current_price - pos.entry_price) / pos.entry_price if pos.entry_price else 0
                dip = next_pending.get("dip_pct") or -0.015
                confirm = next_pending.get("confirm_pct") or 0.01
                should_buy = (pnl_pct <= dip) or (pnl_pct >= confirm)
            elif next_pending.get("condition") == "dip_or_time":
                pnl_pct = (current_price - pos.entry_price) / pos.entry_price if pos.entry_price else 0
                dip = next_pending.get("dip_pct") or -0.01
                breakout = next_pending.get("breakout_pct") or 0.02
                max_delay = (next_pending.get("delay_days_range") or [1, 5])[-1] or 5
                should_buy = (
                    (pnl_pct <= dip) or (pnl_pct >= breakout) or (days_since_entry >= max_delay)
                )
            elif next_pending.get("condition") == "weekly":
                should_buy = days_since_entry >= min_delay

            if should_buy:
                buy_price = current_price * (1 + SLIPPAGE_PCT)
                desk_fund = self.desk_funds.get(pos.desk_id)
                if not desk_fund:
                    pos.pending_buys.pop(0)
                    continue
                max_invest = min(desk_fund.available * 0.1, self.total_cash * 0.2)
                invest = max_invest * (next_pending.get("ratio") or 0.5)
                vol_ma = day_data[code].get("volume_ma20", 0)
                vol_limit = int(vol_ma * MAX_VOLUME_RATIO) if vol_ma else 0
                add_qty = min(int(invest / buy_price), vol_limit) if buy_price > 0 else 0
                if add_qty > 0 and invest <= desk_fund.available:
                    cost = add_qty * buy_price * (1 + FEE_RATE)
                    total_qty = pos.current_qty + add_qty
                    pos.entry_price = (
                        pos.entry_price * pos.current_qty + buy_price * add_qty
                    ) / total_qty
                    pos.current_qty = total_qty
                    pos.total_invested += cost
                    pos.buy_phase = next_pending.get("phase") or pos.buy_phase
                    desk_fund.available -= cost
                    self._record_trade(pos, add_qty, buy_price, trade_date, "ADD_BUY", trade_type="BUY")
                pos.pending_buys.pop(0)

    def process_exits(
        self,
        trade_date: date,
        day_data: Dict[str, Dict[str, Any]],
    ) -> List[Position]:
        """보유 포지션 청산 체크 — 분할매도 지원. 제거할 포지션 리스트 반환."""
        positions_to_remove = []

        for pos in self.positions:
            code = pos.stock_code
            if code not in day_data:
                pos.days_held += 1
                continue
            desk_cfg = self.desk_configs.get(pos.desk_id, {})
            day = day_data[code]
            high = day["high"]
            low = day["low"]
            close = day["close"]
            open_p = day["open"]

            pos.days_held += 1
            pos.peak_price = max(pos.peak_price, high)
            pos.trough_price = min(pos.trough_price, low)

            # 1. 갭다운 전량 청산 (DESK2)
            if desk_cfg.get("gap_down_exit_pct") is not None and pos.current_qty > 0:
                prev_close = pos.peak_price
                gap = (open_p - prev_close) / prev_close if prev_close > 0 else 0
                if gap <= desk_cfg["gap_down_exit_pct"] / 100:
                    self._close_position(pos, open_p, trade_date, "GAP_DOWN")
                    positions_to_remove.append(pos)
                    continue

            # 2. 손절 전량 청산
            max_loss = (desk_cfg.get("max_loss_pct") or -10) / 100
            if low <= pos.entry_price * (1 + max_loss) and pos.current_qty > 0:
                exit_price = pos.entry_price * (1 + max_loss)
                self._close_position(pos, exit_price, trade_date, "STOP_LOSS")
                positions_to_remove.append(pos)
                continue

            # 3. 트레일링스탑
            trail_pct = (desk_cfg.get("trailing_stop_pct") or -1) / 100
            trail_price = pos.peak_price * (1 + trail_pct)
            if (
                pos.peak_price > pos.entry_price
                and low <= trail_price
                and pos.current_qty > 0
            ):
                self._close_position(pos, trail_price, trade_date, "TRAILING_STOP")
                positions_to_remove.append(pos)
                continue

            # 4. 분할매도 (phase별)
            sell_phases = desk_cfg.get("sell_phases", [])
            next_sell_phase = pos.sell_phase + 1
            matching_phase = None
            for sp in sell_phases:
                if sp.get("phase") == next_sell_phase:
                    matching_phase = sp
                    break

            if matching_phase and pos.current_qty > 0:
                should_sell = False
                sell_price_used = close
                trigger = matching_phase.get("trigger", "")

                if trigger == "next_day_open" and pos.days_held >= (matching_phase.get("delay_days") or 1):
                    should_sell = True
                    sell_price_used = open_p
                elif trigger.startswith("target_"):
                    target_mult = matching_phase.get("target_mult") or 1.0
                    target_pct = (desk_cfg.get("target_pct") or 5) / 100
                    target_price = pos.entry_price * (1 + target_pct * target_mult)
                    if high >= target_price:
                        should_sell = True
                        sell_price_used = target_price
                elif trigger == "trailing_or_target":
                    target_price = pos.entry_price * (1 + (desk_cfg.get("target_pct") or 5) / 100)
                    if high >= target_price:
                        should_sell = True
                        sell_price_used = target_price
                    elif low <= trail_price and pos.peak_price > pos.entry_price:
                        should_sell = True
                        sell_price_used = trail_price
                elif trigger == "trailing_or_promote":
                    if low <= trail_price and pos.peak_price > pos.entry_price:
                        should_sell = True
                        sell_price_used = trail_price
                elif trigger == "trailing_only":
                    if low <= trail_price and pos.peak_price > pos.entry_price:
                        should_sell = True
                        sell_price_used = trail_price

                if should_sell:
                    sell_ratio = matching_phase.get("ratio") or 0.5
                    sell_qty = int(pos.current_qty * sell_ratio)
                    if sell_qty <= 0:
                        sell_qty = pos.current_qty
                    sell_price_adj = sell_price_used * (1 - SELL_SLIPPAGE_PCT)
                    proceeds = sell_qty * sell_price_adj * (1 - FEE_RATE - TAX_RATE)
                    self.desk_funds[pos.desk_id].available += proceeds
                    pos.current_qty -= sell_qty
                    pos.sold_qty += sell_qty
                    pos.sell_phase = next_sell_phase
                    self._record_trade(
                        pos, sell_qty, sell_price_adj, trade_date,
                        f"SELL_PHASE_{next_sell_phase}",
                        trade_type="SELL",
                    )
                    if pos.current_qty <= 0:
                        positions_to_remove.append(pos)
                        continue

            # 5. 시간 청산
            max_hold = desk_cfg.get("max_hold_days") or 999
            if pos.days_held >= max_hold and pos.current_qty > 0:
                self._close_position(pos, close, trade_date, "TIME_EXIT")
                positions_to_remove.append(pos)

        return positions_to_remove

    def process_promotions(self, trade_date: date) -> None:
        """마지막 매도 phase 잔량을 상위 DESK로 이관."""
        for pos in self.positions:
            desk_cfg = self.desk_configs.get(pos.desk_id, {})
            promote_to = desk_cfg.get("promote_to")
            if not promote_to or pos.current_qty <= 0:
                continue
            sell_phases = desk_cfg.get("sell_phases", [])
            last_phase = max((sp.get("phase") or 0) for sp in sell_phases) if sell_phases else 0
            if pos.sell_phase >= last_phase - 1 and pos.current_qty > 0:
                if pos.peak_price > pos.entry_price * 1.01:
                    old_desk = pos.desk_id
                    pos.desk_id = promote_to
                    pos.sell_phase = 0
                    pos.days_held = 0
                    pos.promoted_from = old_desk
                    pos.pending_buys = []
                    self._record_trade(
                        pos, 0, 0, trade_date,
                        f"PROMOTE_{old_desk}_TO_{promote_to}",
                        trade_type="SELL",
                    )

    def process_new_signals(
        self,
        trade_date: date,
        date_str: str,
        day_data: Dict[str, Dict[str, Any]],
        stage: int,
    ) -> None:
        """신규 시그널 → 1차 매수 + 추가 매수 예약."""
        if not self.signal_generator:
            return
        for desk_id in (1, 2, 3, 4, 5):
            desk_cfg = self.desk_configs.get(desk_id, {})
            if not desk_cfg.get("enabled_in_daily_bt", True):
                continue
            if "entry_days" in desk_cfg:
                day_name = trade_date.strftime("%a").lower()[:3]
                if day_name not in desk_cfg["entry_days"]:
                    continue
            desk_positions = [p for p in self.positions if p.desk_id == desk_id]
            if len(desk_positions) >= desk_cfg.get("max_positions", 10):
                continue

            card_entries = getattr(self, "card_entries_by_desk", None) or {}
            card_entries = card_entries.get(desk_id)
            market_regime = None
            if getattr(self, "market_regime_filter", None):
                market_regime = self.market_regime_filter.get_regime(date_str)
            logger.info(
                "[SIGNAL] generate_signals 호출 — date=%s, desk=%s, card_entries=%s, forest=%s, tree=%s",
                date_str, desk_id,
                "있음(%d카드)" % len(card_entries) if card_entries else "없음",
                "Y" if getattr(self, "market_regime_filter", None) else "N",
                "Y" if getattr(self, "stock_flow_filter", None) else "N",
            )
            signals = self.signal_generator.generate_signals(
                date_str,
                desk_id,
                stage,
                card_entries=card_entries,
                market_regime=market_regime,
                stock_flow_filter=getattr(self, "stock_flow_filter", None),
            )
            logger.info("[SIGNAL] generate_signals 결과 — %d건 시그널 생성", len(signals))
            for sig in signals:
                if any(p.stock_code == sig.stock_code for p in self.positions):
                    continue
                desk_fund = self.desk_funds.get(desk_id)
                if not desk_fund or desk_fund.available <= 0:
                    continue
                if sig.stock_code not in day_data:
                    continue

                if desk_id == 2 and getattr(sig, "signal_strength", 0) >= 80:
                    buy_plan = desk_cfg.get("buy_phase_strong", {}).get("phases", desk_cfg["buy_phases"])
                elif desk_id == 2:
                    buy_plan = desk_cfg.get("buy_phase_normal", {}).get("phases", desk_cfg["buy_phases"])
                else:
                    buy_plan = desk_cfg.get("buy_phases", [])

                if not buy_plan:
                    continue
                phase1 = buy_plan[0]
                open_price = day_data[sig.stock_code]["open"]
                buy_price = open_price * (1 + SLIPPAGE_PCT)
                invest_amount = min(
                    desk_fund.available * 0.1,
                    self.total_cash * 0.2,
                ) * (phase1.get("ratio") or 1.0)
                vol_ma = day_data[sig.stock_code].get("volume_ma20", 0)
                vol_limit = int(vol_ma * MAX_VOLUME_RATIO) if vol_ma else 0
                qty = min(int(invest_amount / buy_price), vol_limit) if buy_price > 0 else 0
                if vol_limit and qty > vol_limit:
                    qty = vol_limit
                if qty <= 0:
                    continue
                actual_cost = qty * buy_price * (1 + FEE_RATE)
                if actual_cost > desk_fund.available:
                    continue
                # CC-BT-CAPSAFE: 자본 안전장치
                safe, skip_reason = self._check_position_safety(
                    desk_id, sig.stock_code, actual_cost, trade_date
                )
                if not safe:
                    logger.info(
                        "SKIP BUY %s: %s",
                        sig.stock_code,
                        skip_reason,
                    )
                    continue

                position = Position(
                    stock_code=sig.stock_code,
                    desk_id=desk_id,
                    entry_date=trade_date,
                    entry_price=buy_price,
                    current_qty=qty,
                    total_invested=actual_cost,
                    buy_phase=1,
                    sell_phase=0,
                    peak_price=day_data[sig.stock_code]["high"],
                    trough_price=day_data[sig.stock_code]["low"],
                    days_held=0,
                    pending_buys=[],
                    sold_qty=0,
                    promoted_from=None,
                    card_id=getattr(sig, "card_id", None),
                )
                for phase_cfg in buy_plan[1:]:
                    position.pending_buys.append({
                        "phase": phase_cfg.get("phase", 2),
                        "ratio": phase_cfg.get("ratio", 0.5),
                        "condition": phase_cfg.get("condition", "time"),
                        "delay_days": phase_cfg.get("delay_days", 1),
                        "delay_days_range": phase_cfg.get("delay_days_range"),
                        "dip_pct": phase_cfg.get("dip_pct"),
                        "confirm_pct": phase_cfg.get("confirm_pct"),
                        "breakout_pct": phase_cfg.get("breakout_pct"),
                        "max_delay_days": phase_cfg.get("max_delay_days"),
                    })
                desk_fund.available -= actual_cost
                self.positions.append(position)
                self._record_trade(position, qty, buy_price, trade_date, "BUY_PHASE_1", trade_type="BUY")

    def process_eod(
        self,
        trade_date: date,
        day_data: Dict[str, Dict[str, Any]],
    ) -> List[Position]:
        """EOD 처리 — eod_close=True DESK만 잔량 청산."""
        positions_to_remove = []
        for pos in self.positions:
            desk_cfg = self.desk_configs.get(pos.desk_id, {})
            if not desk_cfg.get("eod_close", False) or pos.current_qty <= 0:
                continue
            code = pos.stock_code
            if code in day_data:
                close = day_data[code]["close"]
                self._close_position(pos, close, trade_date, "EOD_CLOSE")
                positions_to_remove.append(pos)
        return positions_to_remove

    def _save_daily(
        self,
        trade_date: date,
        portfolio_value: float,
    ) -> None:
        """v4_backtest_daily INSERT."""
        cash = sum(d.available for d in self.desk_funds.values())
        used = sum(
            p.total_invested for p in self.positions
        )  # 간소화: 보유 평가는 portfolio_value로
        total_asset = cash + portfolio_value
        prev_asset = getattr(self, "_prev_total_asset", self.initial_capital)
        daily_pnl = total_asset - prev_asset
        daily_pnl_pct = (daily_pnl / prev_asset * 100) if prev_asset else 0
        cum_pct = (total_asset - self.initial_capital) / self.initial_capital * 100 if self.initial_capital else 0
        self._prev_total_asset = total_asset

        cur = self._conn_cursor()
        cur.execute(
            """
            INSERT INTO v4_backtest_daily
            (session_id, trade_date, total_asset, cash_balance, holding_value, daily_pnl, daily_pnl_pct, cumulative_pct, current_stage, desk_allocation, open_positions, trades_today)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_id, trade_date) DO UPDATE SET
            total_asset = EXCLUDED.total_asset, cash_balance = EXCLUDED.cash_balance,
            holding_value = EXCLUDED.holding_value, daily_pnl = EXCLUDED.daily_pnl,
            daily_pnl_pct = EXCLUDED.daily_pnl_pct, cumulative_pct = EXCLUDED.cumulative_pct,
            current_stage = EXCLUDED.current_stage, desk_allocation = EXCLUDED.desk_allocation,
            open_positions = EXCLUDED.open_positions, trades_today = EXCLUDED.trades_today
            """,
            (
                self.session_id,
                trade_date,
                int(total_asset),
                int(cash),
                int(portfolio_value),
                int(daily_pnl),
                round(daily_pnl_pct, 4),
                round(cum_pct, 4),
                1,
                json.dumps({str(k): {"available": v.available, "total": v.total} for k, v in self.desk_funds.items()}),
                len(self.positions),
                len([t for t in self.trades if t.get("trade_date") == trade_date]),
            ),
        )
        self._conn.commit()
        cur.close()

    def _norm_date_str(self, d: Any) -> str:
        """날짜를 YYYYMMDD 문자열로."""
        if hasattr(d, "strftime"):
            return d.strftime("%Y%m%d")
        s = str(d).replace("-", "")[:8]
        return s if len(s) == 8 else ""

    def _run_daily(self, stage: int) -> int:
        """일봉 백테스트 메인 루프. 기존 동작 100% 동일."""
        dates = sorted(self.ohlcv_data.keys())
        start_s = self.start_date.strftime("%Y%m%d")
        end_s = self.end_date.strftime("%Y%m%d")
        trading_days = sorted(
            [self._norm_date_str(d) for d in dates if start_s <= self._norm_date_str(d) <= end_s]
        )
        for i, date_str in enumerate(trading_days):
            trade_date = datetime.strptime(date_str, "%Y%m%d").date()
            day_data = dict(
                self.ohlcv_data.get(date_str)
                or self.ohlcv_data.get(trade_date)
                or {}
            )
            self._calc_volume_ma(date_str, self.ohlcv_data, dates, day_data)
            self.process_pending_buys(trade_date, date_str, day_data)
            to_remove = self.process_exits(trade_date, day_data)
            for p in to_remove:
                if p in self.positions:
                    self.positions.remove(p)
            self.process_promotions(trade_date)
            self.process_new_signals(trade_date, date_str, day_data, stage)
            to_remove_eod = self.process_eod(trade_date, day_data)
            for p in to_remove_eod:
                if p in self.positions:
                    self.positions.remove(p)
            portfolio_value = self._calc_portfolio_value(day_data)
            self._save_daily(trade_date, portfolio_value)
            if (i + 1) % 10 == 0:
                logger.info(
                    "V2 progress: %s (%d/%d, %.1f%%, positions=%d, trades=%d)",
                    date_str, i + 1, len(trading_days),
                    (i + 1) / len(trading_days) * 100,
                    len(self.positions), len(self.trades),
                )
        if self.positions and trading_days:
            last_day = trading_days[-1]
            last_data = self.ohlcv_data.get(last_day, {})
            for pos in list(self.positions):
                if pos.stock_code in last_data and pos.current_qty > 0:
                    self._close_position(
                        pos,
                        last_data[pos.stock_code]["close"],
                        datetime.strptime(last_day, "%Y%m%d").date(),
                        "END_OF_BACKTEST",
                    )
            self.positions.clear()
        cur = self._conn_cursor()
        cur.execute(
            "UPDATE v4_backtest_sessions SET status = 'COMPLETED', completed_at = NOW() WHERE session_id = %s",
            (self.session_id,),
        )
        self._conn.commit()
        cur.close()
        if self._conn and not self._conn.closed:
            self._conn.close()
        return self.session_id

    def _collect_minute_indicators(self) -> List[str]:
        """분봉 모드에서 필요한 지표 목록 수집."""
        needed = ["vwap", "ma_5", "ma_20", "volume_ma_20"]
        for desk_id, cfg in (self.desk_configs or {}).items():
            me = cfg.get("minute_entry") or {}
            mx = cfg.get("minute_exit") or {}
            if me.get("ma_cross_up") or me.get("ma_cross_down"):
                needed.extend(["ma_5", "ma_20"])
            if me.get("rsi_oversold") or me.get("rsi_overbought"):
                needed.append("rsi_14")
            if me.get("bollinger_lower") or me.get("bollinger_upper"):
                needed.append("bollinger")
            if me.get("volume_surge"):
                needed.append("volume_ma_20")
            if mx.get("vwap_break_below"):
                needed.append("vwap")
            if mx.get("volume_dry"):
                needed.append("volume_ma_20")
        return list(dict.fromkeys(needed))

    def _run_minute(self, stage: int) -> int:
        """분봉 백테스트 메인 루프: 일봉 스크리닝 + 분봉 entry/exit."""
        import pandas as pd
        dates = sorted(self.ohlcv_data.keys())
        start_s = self.start_date.strftime("%Y%m%d")
        end_s = self.end_date.strftime("%Y%m%d")
        trading_dates_str = sorted(
            [self._norm_date_str(d) for d in dates if start_s <= self._norm_date_str(d) <= end_s]
        )
        trading_dates_for_loader = trading_dates_str

        for i, date_str in enumerate(trading_dates_str):
            trade_date = datetime.strptime(date_str, "%Y%m%d").date()
            day_data = dict(self.ohlcv_data.get(date_str) or {})
            if not day_data:
                continue
            self._calc_volume_ma(date_str, self.ohlcv_data, dates, day_data)

            candidates = []
            market_regime = None
            if getattr(self, "market_regime_filter", None):
                market_regime = self.market_regime_filter.get_regime(date_str)
            for desk_id in (1, 2, 3, 4, 5):
                desk_cfg = self.desk_configs.get(desk_id, {})
                if not desk_cfg.get("enabled_in_daily_bt", True):
                    continue
                if desk_cfg.get("timeframe") != "minute" and not desk_cfg.get("minute_entry"):
                    continue
                card_entries = (getattr(self, "card_entries_by_desk", None) or {}).get(desk_id)
                signals = self.signal_generator.generate_signals(
                    date_str, desk_id, stage,
                    card_entries=card_entries,
                    market_regime=market_regime,
                    stock_flow_filter=getattr(self, "stock_flow_filter", None),
                )
                for sig in signals:
                    if sig.stock_code in day_data:
                        candidates.append({
                            "stock_code": sig.stock_code,
                            "desk_id": desk_id,
                            "card_id": getattr(sig, "card_id", None),
                        })

            minute_df = self.minute_loader.load_for_date(trade_date, trading_dates_for_loader)
            if minute_df.empty:
                portfolio_value = self._calc_portfolio_value(day_data)
                self._save_daily(trade_date, portfolio_value)
                continue

            indicators_needed = self._collect_minute_indicators()
            minute_df = self.minute_indicators.calculate_all(minute_df, indicators_needed)
            today_minutes = minute_df[minute_df["datetime"].dt.date == trade_date].copy()
            if today_minutes.empty:
                portfolio_value = self._calc_portfolio_value(day_data)
                self._save_daily(trade_date, portfolio_value)
                continue

            unique_times = sorted(today_minutes["datetime"].unique())
            open_codes = {p.stock_code for p in self.positions}

            for minute_time in unique_times:
                self._current_minute_time = minute_time
                current_slice = today_minutes[today_minutes["datetime"] == minute_time]
                for pos in self.positions:
                    pos.days_held = (trade_date - pos.entry_date).days
                for pos in list(self.positions):
                    code = pos.stock_code
                    row = current_slice[current_slice["stock_code"] == code]
                    if row.empty:
                        continue
                    r = row.iloc[0]
                    pos.peak_price = max(pos.peak_price, float(r.get("high", 0) or 0))
                    pos.trough_price = min(pos.trough_price, float(r.get("low", pos.entry_price) or pos.entry_price))
                    desk_cfg = self.desk_configs.get(pos.desk_id, {})
                    exit_rules = {**desk_cfg, **(desk_cfg.get("minute_exit") or {})}
                    exit_rules.setdefault("stop_loss_pct", desk_cfg.get("max_loss_pct"))
                    exit_rules.setdefault("trailing_stop_pct", desk_cfg.get("trailing_stop_pct"))
                    exit_rules.setdefault("take_profit_pct", desk_cfg.get("target_pct"))
                    triggered, exit_reason, exit_price = self.minute_evaluator.check_exit(
                        r, r, pos, exit_rules
                    )
                    if triggered and exit_price > 0:
                        self._close_position(pos, exit_price, trade_date, exit_reason)
                        self.positions.remove(pos)

                for pos in list(self.positions):
                    d_cfg = self.desk_configs.get(pos.desk_id, {})
                    max_hold = d_cfg.get("max_hold_days", 999)
                    if pos.days_held >= max_hold and pos.current_qty > 0:
                        r = current_slice[current_slice["stock_code"] == pos.stock_code]
                        close_p = r.iloc[0]["close"] if not r.empty else pos.entry_price
                        self._close_position(pos, close_p, trade_date, "TIME_EXIT")
                        self.positions.remove(pos)

                for cand in candidates:
                    code, desk_id, card_id = cand["stock_code"], cand["desk_id"], cand["card_id"]
                    if code in open_codes:
                        continue
                    desk_cfg = self.desk_configs.get(desk_id, {})
                    entry_rules = desk_cfg.get("minute_entry") or {}
                    if not entry_rules:
                        continue
                    row = current_slice[current_slice["stock_code"] == code]
                    if row.empty:
                        continue
                    r = row.iloc[0]
                    stock_indicators = r
                    prev_row = None
                    prev_ind = None
                    prev_same = today_minutes[
                        (today_minutes["stock_code"] == code)
                        & (today_minutes["datetime"] < minute_time)
                    ]
                    if not prev_same.empty:
                        prev_row = prev_same.iloc[-1]
                        prev_ind = prev_row
                    triggered, reason = self.minute_evaluator.check_entry(
                        r, stock_indicators, entry_rules, prev_row, prev_ind
                    )
                    if not triggered:
                        continue
                    safe, skip_reason = self._check_position_safety(
                        desk_id, code,
                        self.initial_capital * 0.1,
                        trade_date,
                    )
                    if not safe:
                        logger.info("SKIP BUY %s (minute): %s", code, skip_reason)
                        continue
                    desk_fund = self.desk_funds.get(desk_id)
                    if not desk_fund or desk_fund.available <= 0:
                        continue
                    buy_price = float(r["close"]) * (1 + SLIPPAGE_PCT)
                    invest = min(desk_fund.available * 0.1, self.total_cash * 0.2)
                    vol_ma = day_data.get(code, {}).get("volume_ma20", 0) or 0
                    vol_limit = int(vol_ma * MAX_VOLUME_RATIO) if vol_ma else 0
                    qty = min(int(invest / buy_price), vol_limit) if buy_price > 0 else 0
                    if qty <= 0:
                        continue
                    cost = qty * buy_price * (1 + FEE_RATE)
                    if cost > desk_fund.available:
                        continue
                    pos = Position(
                        stock_code=code,
                        desk_id=desk_id,
                        entry_date=trade_date,
                        entry_price=buy_price,
                        current_qty=qty,
                        total_invested=cost,
                        buy_phase=1,
                        sell_phase=0,
                        peak_price=float(r.get("high", buy_price)),
                        days_held=0,
                        pending_buys=[],
                        sold_qty=0,
                        promoted_from=None,
                        card_id=card_id,
                    )
                    desk_fund.available -= cost
                    self.positions.append(pos)
                    open_codes.add(code)
                    self._record_trade(pos, qty, buy_price, trade_date, reason or "MINUTE_ENTRY", trade_type="BUY")

            portfolio_value = self._calc_portfolio_value(day_data)
            self._save_daily(trade_date, portfolio_value)
            if (i + 1) % 5 == 0:
                logger.info(
                    "V2 minute progress: %s (%d/%d), positions=%d, trades=%d",
                    date_str, i + 1, len(trading_dates_str), len(self.positions), len(self.trades),
                )

        if self.positions and trading_dates_str:
            last_day = trading_dates_str[-1]
            last_data = self.ohlcv_data.get(last_day, {})
            for pos in list(self.positions):
                if pos.stock_code in last_data and pos.current_qty > 0:
                    self._close_position(
                        pos,
                        last_data[pos.stock_code]["close"],
                        datetime.strptime(last_day, "%Y%m%d").date(),
                        "END_OF_BACKTEST",
                    )
            self.positions.clear()
        cur = self._conn_cursor()
        cur.execute(
            "UPDATE v4_backtest_sessions SET status = 'COMPLETED', completed_at = NOW() WHERE session_id = %s",
            (self.session_id,),
        )
        self._conn.commit()
        cur.close()
        if self.minute_loader:
            self.minute_loader.clear()
        if self._conn and not self._conn.closed:
            self._conn.close()
        return self.session_id

    def run(self, stage: int = 1, desk_strategies: Optional[List[dict]] = None) -> int:
        """V2 백테스트 실행. desk_strategies가 있으면 해당 DESK+card_id만 로드."""
        try:
            self._load_ohlcv()
            db_configs = self._load_strategy_from_db(stage=stage, desk_strategies=desk_strategies)
            if db_configs is not None:
                self.desk_configs = {}
                self.config_source = "DB"
                for desk_id, desk_data in db_configs.items():
                    self.desk_configs[desk_id] = {
                        **self._merge_with_fallback(desk_data["config"], desk_id),
                        "strategies": desk_data.get("strategies", []),
                    }
                self.desk_allocations = {
                    d: data["allocation_pct"] for d, data in db_configs.items()
                }
                logger.info(
                    "전략 파라미터 DB 로드 완료: %d개 DESK, source=strategy_cards+v4_desk_strategy_mapping",
                    len(self.desk_configs),
                )
            else:
                from scripts.backtest.config import V2_DESK_CONFIGS, V2_STAGE_ALLOCATION
                self.desk_configs = V2_DESK_CONFIGS
                self.desk_allocations = V2_STAGE_ALLOCATION.get(stage, V2_STAGE_ALLOCATION.get(1, {}))
                self.config_source = "config.py"
                logger.info("전략 파라미터 config.py fallback 사용")
            for desk_id, cfg in self.desk_configs.items():
                logger.info(
                    "  DESK%d: keys=%s, alloc=%s%%",
                    desk_id, list(cfg.keys()), self.desk_allocations.get(desk_id, 0),
                )
            prefix = "[DB] " if self.config_source == "DB" else "[CFG] "
            if not self.session_name.startswith(("[DB] ", "[CFG] ")):
                self.session_name = prefix + self.session_name
            logger.info("=== BacktestEngineV2 시작 ===")
            logger.info("  config_source: %s", self.config_source)
            logger.info("  stage: %s", stage)
            logger.info("  desk_count: %d", len(self.desk_configs))
            if not self.signal_generator:
                self.signal_generator = BacktestSignalGenerator(self.ohlcv_data)

            self.market_regime_filter = None
            self.stock_flow_filter = None
            try:
                vkospi_data, market_investor_data = self._load_market_regime_data()
                self.market_regime_filter = MarketRegimeFilter(vkospi_data, market_investor_data)
            except Exception as e:
                logger.warning(
                    "Market regime data load failed: %s, continuing without forest filter", e
                )
            try:
                start_s = self.start_date.strftime("%Y%m%d")
                end_s = self.end_date.strftime("%Y%m%d")
                investor_data = self._load_investor_data(start_s, end_s)
                self.stock_flow_filter = StockFlowFilter(investor_data)
            except Exception as e:
                logger.warning(
                    "Investor data load failed: %s, continuing without tree filter", e
                )

            logger.info(
                "[FILTER] market_regime_filter: %s, stock_flow_filter: %s",
                "활성" if self.market_regime_filter else "비활성",
                "활성" if self.stock_flow_filter else "비활성",
            )

            self.card_entries_by_desk = {}
            for desk_id, desk_data in self.desk_configs.items():
                strategies = desk_data.get("strategies", [])
                card_entries = {}
                for strat in strategies:
                    if strat.get("entry_rules"):
                        card_entries[strat["card_id"]] = strat["entry_rules"]
                if card_entries:
                    self.card_entries_by_desk[desk_id] = card_entries
                    first_indicators = list(card_entries.values())[0].get("indicators", [])[:3]
                    logger.info(
                        "[CARD] DESK%d card_entries 로드: %d개 카드, indicators 예시: %s",
                        desk_id, len(card_entries), first_indicators,
                    )

            card_ids = set()
            for desk_data in self.desk_configs.values():
                for strat in desk_data.get("strategies", []):
                    if strat.get("card_id") is not None:
                        card_ids.add(strat["card_id"])
            if card_ids:
                cur = self._conn_cursor()
                cur.execute(
                    "SELECT card_id, strategy_name FROM strategy_cards WHERE card_id = ANY(%s)",
                    (list(card_ids),),
                )
                self._card_name_map = {row[0]: row[1] for row in cur.fetchall()}
                cur.close()
            else:
                self._card_name_map = {}

            self._create_session(stage)
            # allocation_pct 정규화: 사용 desk 합이 100%가 아니면 100%로 맞춰 initial_capital 전액 배정
            total_alloc_pct = sum(self.desk_allocations.values())
            if total_alloc_pct > 0 and abs(total_alloc_pct - 100.0) > 0.01:
                normalize_ratio = 100.0 / total_alloc_pct
                self.desk_allocations = {
                    k: v * normalize_ratio for k, v in self.desk_allocations.items()
                }
                logger.info(
                    "[ALLOC-NORMALIZE] allocation_pct 합 %.2f%% → 100%%로 정규화. desk별: %s",
                    total_alloc_pct,
                    self.desk_allocations,
                )
            allocation = self.desk_allocations
            self.total_cash = float(self.initial_capital)
            self.desk_funds = {}
            for desk_id, pct in allocation.items():
                amt = self.initial_capital * pct / 100
                self.desk_funds[desk_id] = DeskFund(desk_id=desk_id, total=amt, available=amt)
            self.positions = []
            self.trades = []
            self._prev_total_asset = float(self.initial_capital)

            if self.timeframe == "minute":
                from scripts.backtest.minute_data_loader import MinuteDataLoader
                self.minute_loader = MinuteDataLoader(
                    self._get_connection(), self.minute_lookback_days
                )
            if self.timeframe == "daily":
                return self._run_daily(stage)
            if self.timeframe == "minute":
                return self._run_minute(stage)
            return self._run_daily(stage)
        except Exception as e:
            import traceback
            logger.error("V2 Engine fatal error: %s\n%s", e, traceback.format_exc())
            try:
                self._update_session_status("FAILED", error_message=str(e))
            except Exception:
                pass
            if self._conn and not self._conn.closed:
                self._conn.close()
            raise
