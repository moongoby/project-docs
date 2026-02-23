# CUR-GO100-PHASE2-STABILIZE STEP2, 2026-02-23 — ISS-003: get_effective_uid fallback, INSERT 전 로깅, logger.exception
# CUR-GO100-HOTFIX-CRITICAL, 2026-02-23
# CUR-GO100-UNIFIED-SAVE-BE, 2026-02-23
# Modified by: CUR-GO100-MY-STRATEGY-FIX, 2026-02-22 — list_cards 시 user_id를 v4_users 기준으로 변환(레거시 호환)
# Modified by: CUR-GO100-CARD-DETAIL-FIX, 2026-02-22
# Modified by: CUR-GO100-PHASE3-CARD-SERVICE, 2026-02-21
"""
GO100 전략 카드 CRUD 및 상태 전이 서비스.
DB: go100_strategy_cards, go100_strategy_store VIEW.
V4.1 strategy_cards / strategy_card_service.py 미수정.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from backend.app.services.go100.user_utils import get_effective_uid
from backend.app.services.go100.strategy.schemas import (
    ALLOWED_TRANSITIONS,
    Go100StrategyCardCreate,
    Go100StrategyCardUpdate,
    Go100StrategyCardResponse,
    Go100StrategyCardListResponse,
    Go100StatusTransitionRequest,
    Go100StoreSubscribeRequest,
)


# --- 예외 ---
class NotFoundException(Exception):
    """카드 미존재 또는 접근 불가."""
    pass


class BusinessLogicException(Exception):
    """상태 전이 불가, 수정 불가 등 비즈니스 규칙 위반."""
    pass


class OwnershipException(Exception):
    """다른 사용자 카드 접근 시도."""
    pass


def _row_to_response(row: Any) -> Go100StrategyCardResponse:
    m = row._mapping if hasattr(row, "_mapping") else row
    return Go100StrategyCardResponse(
        go100_card_id=m["go100_card_id"],
        user_id=m["user_id"],
        account_id=m["account_id"],
        strategy_name=m["strategy_name"],
        strategy_type=m.get("strategy_type"),
        universe_filter=m.get("universe_filter"),
        entry_rules=m.get("entry_rules"),
        exit_rules=m.get("exit_rules"),
        risk_params=m.get("risk_params"),
        strategy_params=m.get("strategy_params"),
        allocated_amount=float(m["allocated_amount"]) if m.get("allocated_amount") is not None else None,
        max_stocks=m.get("max_stocks"),
        card_status=m["card_status"],
        is_active=m.get("is_active", True),
        is_live=m.get("is_live", False),
        source_type=m.get("source_type"),
        source_store_card_id=m.get("source_store_card_id"),
        source_user_id=m.get("source_user_id"),
        llm_session_id=m.get("llm_session_id"),
        last_backtest_id=m.get("last_backtest_id"),
        last_backtest_return=float(m["last_backtest_return"]) if m.get("last_backtest_return") is not None else None,
        last_backtest_mdd=float(m["last_backtest_mdd"]) if m.get("last_backtest_mdd") is not None else None,
        last_backtest_sharpe=float(m["last_backtest_sharpe"]) if m.get("last_backtest_sharpe") is not None else None,
        last_backtest_at=m.get("last_backtest_at"),
        paper_total_return=float(m["paper_total_return"]) if m.get("paper_total_return") is not None else None,
        paper_start_date=str(m["paper_start_date"]) if m.get("paper_start_date") is not None else None,
        paper_days=m.get("paper_days"),
        disclaimer_agreed=m.get("disclaimer_agreed", False),
        disclaimer_agreed_at=m.get("disclaimer_agreed_at"),
        dedicated_account=m.get("dedicated_account", False),
        created_at=m["created_at"],
        updated_at=m["updated_at"],
    )


def _source_type_to_db(source_type: Optional[str]) -> str:
    """API source_type -> DB source_type (SYSTEM, CUSTOM, LLM, SHARED). 기획서 기준 통일."""
    if not source_type or source_type == "CUSTOM":
        return "CUSTOM"
    if source_type in ("SYSTEM", "LLM", "SHARED"):
        return source_type
    return "CUSTOM"


class Go100StrategyCardService:
    """GO100 전략 카드 CRUD 및 상태 전이."""

    async def create_card(
        self,
        user_id: int,
        data: Go100StrategyCardCreate,
        db: AsyncSession,
    ) -> Go100StrategyCardResponse:
        try:
            effective_uid = await get_effective_uid(db, user_id)
        except Exception as e:
            logger.warning("GO100 전략카드 get_effective_uid 실패, JWT user_id 사용: %s", e)
            effective_uid = user_id
        now = datetime.now(timezone.utc)
        strategy_name = (data.strategy_name or "").strip() or f"GO100 AI 전략 - {now.strftime('%m/%d %H:%M')}"
        uf = data.universe_filter if data.universe_filter is not None else {}
        if isinstance(uf, dict) and data.stock_codes:
            uf = {**uf, "stock_codes": data.stock_codes}
        elif data.stock_codes and not uf:
            uf = {"stock_codes": data.stock_codes}
        card_status = "IDEA" if (uf == {} or uf is None) else "DRAFT"
        source_type_db = _source_type_to_db(data.source_type or "CUSTOM")
        entry_rules = data.entry_rules if data.entry_rules is not None else []
        if data.buy_conditions is not None and entry_rules == []:
            entry_rules = data.buy_conditions if isinstance(data.buy_conditions, list) else [data.buy_conditions]
        exit_rules = data.exit_rules if data.exit_rules is not None else []
        if data.sell_conditions is not None and exit_rules == []:
            exit_rules = data.sell_conditions if isinstance(data.sell_conditions, list) else [data.sell_conditions]
        risk_params = data.risk_params if data.risk_params is not None else {}
        if data.risk_management is not None and risk_params == {}:
            risk_params = data.risk_management
        strategy_params = data.strategy_params if data.strategy_params is not None else {}
        if data.indicators is not None or data.parameters is not None:
            strategy_params = {**strategy_params, "indicators": data.indicators or {}, "parameters": data.parameters or {}}
        if isinstance(entry_rules, dict):
            entry_rules = [entry_rules]
        if isinstance(exit_rules, dict):
            exit_rules = [exit_rules]
        strategy_type_db = (data.strategy_type or "GO100_AI").strip() or "GO100_AI"
        insert_params = {
            "user_id": effective_uid,
            "strategy_name": strategy_name,
            "strategy_type": strategy_type_db,
            "universe_filter": json.dumps(uf if isinstance(uf, dict) else {}),
            "entry_rules": json.dumps(entry_rules),
            "exit_rules": json.dumps(exit_rules),
            "risk_params": json.dumps(risk_params),
            "strategy_params": json.dumps(strategy_params),
            "max_stocks": data.max_stocks or 5,
            "card_status": card_status,
            "source_type": source_type_db,
            "now": now,
        }
        logger.info("GO100 카드 INSERT 직전: %s", insert_params)
        try:
            result = await db.execute(
                text("""
                    INSERT INTO go100_strategy_cards (
                        user_id, strategy_name, strategy_type, universe_filter,
                        entry_rules, exit_rules, risk_params, strategy_params,
                        max_stocks, card_status, source_type, created_at, updated_at
                    ) VALUES (
                        :user_id, :strategy_name, :strategy_type, :universe_filter::jsonb,
                        :entry_rules::jsonb, :exit_rules::jsonb, :risk_params::jsonb, :strategy_params::jsonb,
                        :max_stocks, :card_status, :source_type, :now, :now
                    )
                    RETURNING go100_card_id, user_id, account_id, strategy_name, strategy_type,
                        universe_filter, entry_rules, exit_rules, risk_params, strategy_params,
                        allocated_amount, max_stocks, card_status, is_active, is_live,
                        source_type, source_store_card_id, source_user_id, llm_session_id,
                        last_backtest_id, last_backtest_return, last_backtest_mdd, last_backtest_sharpe, last_backtest_at,
                        paper_total_return, paper_start_date, paper_days,
                        disclaimer_agreed, disclaimer_agreed_at, dedicated_account,
                        created_at, updated_at
                """),
                insert_params,
            )
            row = result.mappings().first()
            await db.commit()
            return _row_to_response(row)
        except Exception as e:
            logger.exception("GO100 카드 생성 실패: %s", e)
            await db.rollback()
            raise

    async def get_card(
        self,
        user_id: int,
        card_id: int,
        db: AsyncSession,
    ) -> Go100StrategyCardResponse:
        effective_uid = await get_effective_uid(db, user_id)
        result = await db.execute(
            text("""
                SELECT go100_card_id, user_id, account_id, strategy_name, strategy_type,
                    universe_filter, entry_rules, exit_rules, risk_params, strategy_params,
                    allocated_amount, max_stocks, card_status, is_active, is_live,
                    source_type, source_store_card_id, source_user_id, llm_session_id,
                    last_backtest_id, last_backtest_return, last_backtest_mdd, last_backtest_sharpe, last_backtest_at,
                    paper_total_return, paper_start_date, paper_days,
                    disclaimer_agreed, disclaimer_agreed_at, dedicated_account,
                    created_at, updated_at
                FROM go100_strategy_cards
                WHERE go100_card_id = :card_id
                  AND (user_id = :user_id OR is_featured = true)
                  AND is_active = true
            """),
            {"card_id": card_id, "user_id": effective_uid},
        )
        row = result.mappings().first()
        if not row:
            raise NotFoundException("카드를 찾을 수 없거나 접근 권한이 없습니다.")
        return _row_to_response(row)

    async def list_cards(
        self,
        user_id: int,
        page: int,
        page_size: int,
        status: Optional[str],
        source_type: Optional[str],
        db: AsyncSession,
    ) -> Go100StrategyCardListResponse:
        effective_uid = await get_effective_uid(db, user_id)
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        offset = (page - 1) * page_size
        conditions = ["user_id = :user_id", "is_active = true"]
        params: dict[str, Any] = {"user_id": effective_uid, "limit": page_size, "offset": offset}
        if status:
            conditions.append("card_status = :status")
            params["status"] = status
        if source_type:
            st = _source_type_to_db(source_type)
            conditions.append("source_type = :source_type")
            params["source_type"] = st
        where = " AND ".join(conditions)
        count_result = await db.execute(
            text(f"SELECT COUNT(*) AS cnt FROM go100_strategy_cards WHERE {where}"),
            {k: v for k, v in params.items() if k not in ("limit", "offset")},
        )
        total_count = count_result.scalar() or 0
        result = await db.execute(
            text(f"""
                SELECT go100_card_id, user_id, account_id, strategy_name, strategy_type,
                    universe_filter, entry_rules, exit_rules, risk_params, strategy_params,
                    allocated_amount, max_stocks, card_status, is_active, is_live,
                    source_type, source_store_card_id, source_user_id, llm_session_id,
                    last_backtest_id, last_backtest_return, last_backtest_mdd, last_backtest_sharpe, last_backtest_at,
                    paper_total_return, paper_start_date, paper_days,
                    disclaimer_agreed, disclaimer_agreed_at, dedicated_account,
                    created_at, updated_at
                FROM go100_strategy_cards
                WHERE {where}
                ORDER BY updated_at DESC
                LIMIT :limit OFFSET :offset
            """),
            params,
        )
        rows = result.mappings().all()
        items = [_row_to_response(r) for r in rows]
        return Go100StrategyCardListResponse(
            items=items,
            total_count=total_count,
            page=page,
            page_size=page_size,
        )

    async def update_card(
        self,
        user_id: int,
        card_id: int,
        data: Go100StrategyCardUpdate,
        db: AsyncSession,
    ) -> Go100StrategyCardResponse:
        effective_uid = await get_effective_uid(db, user_id)
        card = await self.get_card(user_id, card_id, db)
        if card.card_status == "RETIRED":
            raise BusinessLogicException("RETIRED 상태의 카드는 수정할 수 없습니다.")
        live_restricted = card.card_status == "LIVE"
        if live_restricted and data.strategy_name is not None:
            raise BusinessLogicException("LIVE 상태에서는 strategy_name 변경이 불가합니다. risk_params, exit_rules만 수정 가능합니다.")
        if live_restricted and (data.universe_filter is not None or data.entry_rules is not None or data.strategy_params is not None):
            raise BusinessLogicException("LIVE 상태에서는 risk_params, exit_rules만 수정 가능합니다.")
        now = datetime.now(timezone.utc)
        updates = ["updated_at = :now"]
        params: dict[str, Any] = {"card_id": card_id, "user_id": effective_uid, "now": now}
        if data.strategy_name is not None and not live_restricted:
            updates.append("strategy_name = :strategy_name")
            params["strategy_name"] = data.strategy_name
        if data.universe_filter is not None and not live_restricted:
            updates.append("universe_filter = :universe_filter::jsonb")
            params["universe_filter"] = json.dumps(data.universe_filter)
        if data.entry_rules is not None and not live_restricted:
            updates.append("entry_rules = :entry_rules::jsonb")
            params["entry_rules"] = json.dumps(data.entry_rules if isinstance(data.entry_rules, (list, dict)) else [])
        if data.exit_rules is not None:
            updates.append("exit_rules = :exit_rules::jsonb")
            params["exit_rules"] = json.dumps(data.exit_rules if isinstance(data.exit_rules, (list, dict)) else [])
        if data.risk_params is not None:
            updates.append("risk_params = :risk_params::jsonb")
            params["risk_params"] = json.dumps(data.risk_params)
        if data.strategy_params is not None and not live_restricted:
            updates.append("strategy_params = :strategy_params::jsonb")
            params["strategy_params"] = json.dumps(data.strategy_params)
        if data.max_stocks is not None:
            updates.append("max_stocks = :max_stocks")
            params["max_stocks"] = data.max_stocks
        if data.account_id is not None:
            updates.append("account_id = :account_id")
            params["account_id"] = data.account_id
        if data.is_active is not None:
            if card.user_id != effective_uid:
                raise OwnershipException("다른 사용자 카드의 활성/비활성은 변경할 수 없습니다.")
            updates.append("is_active = :is_active")
            params["is_active"] = data.is_active
        if len(updates) <= 1:
            return card
        await db.execute(
            text(f"""
                UPDATE go100_strategy_cards
                SET {", ".join(updates)}
                WHERE go100_card_id = :card_id AND user_id = :user_id
            """),
            params,
        )
        await db.commit()
        return await self.get_card(user_id, card_id, db)

    async def transition_status(
        self,
        user_id: int,
        card_id: int,
        req: Go100StatusTransitionRequest,
        db: AsyncSession,
    ) -> Go100StrategyCardResponse:
        card = await self.get_card(user_id, card_id, db)
        current = card.card_status
        target = req.target_status.strip().upper()
        allowed = ALLOWED_TRANSITIONS.get(current, [])
        if target not in allowed:
            raise BusinessLogicException(
                f"상태 전이 불가: {current} -> {target}. 허용: {allowed}"
            )
        if current == "DRAFT" and target == "BACKTESTED":
            if not card.last_backtest_id:
                raise BusinessLogicException("DRAFT -> BACKTESTED 전이는 1회 이상 백테스트 후 가능합니다 (last_backtest_id 필요).")
        if current == "BACKTESTED" and target == "PAPER_LIVE":
            if not card.account_id:
                raise BusinessLogicException("BACKTESTED -> PAPER_LIVE 전이는 account_id 설정 및 PAPER 포트폴리오가 필요합니다.")
            port_result = await db.execute(
                text("""
                    SELECT 1 FROM go100_portfolios
                    WHERE go100_card_id = :card_id AND is_paper = true AND status = 'ACTIVE'
                    LIMIT 1
                """),
                {"card_id": card_id},
            )
            if not port_result.scalar():
                raise BusinessLogicException("PAPER 포트폴리오가 없습니다. 먼저 모의 포트폴리오를 생성하세요.")
        if target == "LIVE":
            if req.disclaimer_agreed is not True:
                raise BusinessLogicException("실매매(LIVE) 전환 시 disclaimer_agreed=true 필요합니다.")
            if not card.dedicated_account:
                pass
        effective_uid = await get_effective_uid(db, user_id)
        now = datetime.now(timezone.utc)
        is_live = target == "LIVE"
        await db.execute(
            text("""
                UPDATE go100_strategy_cards
                SET card_status = :target, is_live = :is_live, updated_at = :now
                WHERE go100_card_id = :card_id AND user_id = :user_id
            """),
            {"card_id": card_id, "user_id": effective_uid, "target": target, "is_live": is_live, "now": now},
        )
        if target == "LIVE" and req.disclaimer_agreed:
            await db.execute(
                text("""
                    UPDATE go100_strategy_cards
                    SET disclaimer_agreed = true, disclaimer_agreed_at = :now
                    WHERE go100_card_id = :card_id AND user_id = :user_id
                """),
                {"card_id": card_id, "user_id": effective_uid, "now": now},
            )
        await db.commit()
        return await self.get_card(user_id, card_id, db)

    async def delete_card(
        self,
        user_id: int,
        card_id: int,
        db: AsyncSession,
    ) -> dict:
        card = await self.get_card(user_id, card_id, db)
        if card.card_status == "LIVE":
            raise BusinessLogicException("LIVE 상태 카드는 삭제할 수 없습니다. 먼저 PAUSED 또는 RETIRED로 전환하세요.")
        open_result = await db.execute(
            text("""
                SELECT 1 FROM go100_positions p
                JOIN go100_portfolios f ON f.portfolio_id = p.portfolio_id
                WHERE f.go100_card_id = :card_id AND p.status = 'OPEN'
                LIMIT 1
            """),
            {"card_id": card_id},
        )
        if open_result.scalar():
            raise BusinessLogicException("OPEN 포지션이 있는 카드는 삭제할 수 없습니다. 포지션 청산 후 진행하세요.")
        effective_uid = await get_effective_uid(db, user_id)
        now = datetime.now(timezone.utc)
        await db.execute(
            text("""
                UPDATE go100_strategy_cards
                SET is_active = false, card_status = 'RETIRED', updated_at = :now
                WHERE go100_card_id = :card_id AND user_id = :user_id
            """),
            {"card_id": card_id, "user_id": effective_uid, "now": now},
        )
        await db.commit()
        return {"message": "삭제 완료", "card_id": card_id}

    async def subscribe_from_store(
        self,
        user_id: int,
        req: Go100StoreSubscribeRequest,
        db: AsyncSession,
    ) -> Go100StrategyCardResponse:
        effective_uid = await get_effective_uid(db, user_id)
        store_result = await db.execute(
            text("""
                SELECT store_card_id, strategy_name, strategy_type, entry_rules, exit_rules, risk_params, strategy_params
                FROM go100_strategy_store
                WHERE store_card_id = :sid
            """),
            {"sid": req.store_card_id},
        )
        row = store_result.mappings().first()
        if not row:
            raise NotFoundException("마켓플레이스에서 해당 전략을 찾을 수 없습니다.")
        now = datetime.now(timezone.utc)
        name = (row["strategy_name"] or "") + " (복제)"
        result = await db.execute(
            text("""
                INSERT INTO go100_strategy_cards (
                    user_id, strategy_name, strategy_type, universe_filter,
                    entry_rules, exit_rules, risk_params, strategy_params,
                    max_stocks, card_status, source_type, source_store_card_id, created_at, updated_at
                ) VALUES (
                    :user_id, :strategy_name, 'SUBSCRIBED', '{}',
                    COALESCE(:entry_rules::jsonb, '[]'), COALESCE(:exit_rules::jsonb, '[]'),
                    COALESCE(:risk_params::jsonb, '{}'), COALESCE(:strategy_params::jsonb, '{}'),
                    5, 'DRAFT', 'SYSTEM', :store_card_id, :now, :now
                )
                RETURNING go100_card_id, user_id, account_id, strategy_name, strategy_type,
                    universe_filter, entry_rules, exit_rules, risk_params, strategy_params,
                    allocated_amount, max_stocks, card_status, is_active, is_live,
                    source_type, source_store_card_id, source_user_id, llm_session_id,
                    last_backtest_id, last_backtest_return, last_backtest_mdd, last_backtest_sharpe, last_backtest_at,
                    paper_total_return, paper_start_date, paper_days,
                    disclaimer_agreed, disclaimer_agreed_at, dedicated_account,
                    created_at, updated_at
            """),
            {
                "user_id": effective_uid,
                "strategy_name": name,
                "entry_rules": json.dumps(row.get("entry_rules") or []),
                "exit_rules": json.dumps(row.get("exit_rules") or []),
                "risk_params": json.dumps(row.get("risk_params") or {}),
                "strategy_params": json.dumps(row.get("strategy_params") or {}),
                "store_card_id": req.store_card_id,
                "now": now,
            },
        )
        inserted = result.mappings().first()
        await db.commit()
        return _row_to_response(inserted)

    async def list_store(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            text("SELECT store_card_id, strategy_name, strategy_type, entry_rules, exit_rules, risk_params, strategy_params, desk_id, backtest_compatible, created_at FROM go100_strategy_store ORDER BY store_card_id")
        )
        rows = result.mappings().all()
        return [dict(r) for r in rows]


go100_strategy_card_service = Go100StrategyCardService()
