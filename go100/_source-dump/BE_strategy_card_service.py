# CUR-GO100-PHASE2-STABILIZE STEP3, 2026-02-23 — ISS-002: for-backtest GO100 정렬/strategy_type
# CUR-GO100-HOTFIX-CRITICAL, 2026-02-23 — for-backtest GO100 카드 노출 보장
# CUR-GO100-UNIFIED-SAVE-BE, 2026-02-23
# Modified by: CUR-GO100-MY-STRATEGY-FIX, 2026-02-22
# Modified by: CUR-GO100-CARD-REDESIGN-BE, 2026-02-22
# Modified by: CUR-GO100-FIX-BACKEND, 2026-02-22
"""
Modified by: CUR-GO100-MY-STRATEGY-FIX, 2026-02-22 — tab=my 시 user_id를 v4_users 기준으로 변환(레거시 users.id 호환)
Modified by: CUR-GO100-CARD-REDESIGN-BE, 2026-02-22 — Catalog GO100 전용: tab=all(featured)/my(user), V4.1 strategy_cards 제외
Modified by: CUR-GO100-STRATEGY-CARD-FIX, 2026-02-22 — list_cards_with_system에 go100_strategy_cards 병합
Modified by CUR-BACKTEST-CARD6-TEST, 2026-02-20 — list_cards_for_backtest: 전체 활성 카드 (백테스트 드롭다운용)
CUR-GO100-UNIFIED-SAVE-BE: for-backtest에 go100_strategy_cards 병합, source/go100_card_id
"""

import json
import logging
from typing import Optional, List, Any
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.strategy_card_schemas import (
    StrategyCardCreateRequest,
    StrategyCardUpdateRequest,
    StrategyCardToggleRequest,
    StrategyCardResponse,
    StrategyCardListResponse,
    StrategyCardToggleResponse,
    StrategyCardDeleteResponse,
    StrategyCardDisplay,
    StrategyCardDisplayListResponse,
    StrategyActivateRequest,
)
from backend.app.services.tier_limit_service import (
    check_card_limit,
    check_real_trading_allowed,
)

logger = logging.getLogger("go100.card_service")


class CardServiceError(Exception):
    pass


class CardNotFoundError(CardServiceError):
    pass


class CardOwnershipError(CardServiceError):
    pass


def _parse_desk_id(value) -> Optional[int]:
    """DB desk_id는 varchar(10). int로 파싱 가능하면 반환."""
    if value is None:
        return None
    s = str(value).strip()
    return int(s) if s.isdigit() else None


def _parse_strategy_params(value) -> Optional[dict]:
    """DB jsonb → dict. 이미 dict면 그대로."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    return None


class StrategyCardService:
    """
    전략 카드 CRUD 서비스.
    - 생성: 티어 제한 + 계좌 소유권 확인
    - 토글: is_live on/off, buy_block 확인, 실거래 tier 검증
    - 삭제: soft delete (is_active = false)
    """

    async def _verify_card_ownership(
        self, card_id: int, user_id: int, db: AsyncSession
    ) -> tuple:
        """카드 존재 + 소유권 확인. row 튜플 반환."""
        result = await db.execute(
            text("""
                SELECT card_id, user_id, account_id, strategy_name,
                       allocated_amount, max_stocks, is_live, desk_id,
                       strategy_params, is_active, created_at, updated_at
                FROM strategy_cards
                WHERE card_id = :cid AND is_active = true
            """),
            {"cid": card_id},
        )
        row = result.fetchone()
        if row is None:
            raise CardNotFoundError(f"Card {card_id} not found")
        if row[1] != user_id:
            raise CardOwnershipError(f"Card {card_id} not owned by user {user_id}")
        return row

    def _row_to_response(self, row) -> StrategyCardResponse:
        """DB row → StrategyCardResponse 변환."""
        return StrategyCardResponse(
            card_id=row[0],
            user_id=row[1],
            account_id=row[2],
            strategy_name=row[3],
            allocated_amount=float(row[4]) if row[4] is not None else None,
            max_stocks=row[5] or 5,
            is_live=row[6] or False,
            desk_id=_parse_desk_id(row[7]),
            strategy_params=_parse_strategy_params(row[8]),
            is_active=row[9],
            created_at=row[10],
            updated_at=row[11],
        )

    async def create_card(
        self, user_id: int, req: StrategyCardCreateRequest, db: AsyncSession
    ) -> StrategyCardResponse:
        """전략 카드 생성."""
        acct_result = await db.execute(
            text("SELECT user_id FROM accounts WHERE account_id = :aid AND is_active = true"),
            {"aid": req.account_id},
        )
        acct_row = acct_result.fetchone()
        if not acct_row:
            raise CardServiceError(f"Account {req.account_id} not found")
        if acct_row[0] != user_id:
            raise CardOwnershipError(f"Account {req.account_id} not owned by user {user_id}")

        await check_card_limit(user_id, req.account_id, db)

        if req.is_live:
            await check_real_trading_allowed(user_id, db)

        params_json = json.dumps(req.strategy_params) if req.strategy_params else "{}"
        desk_val = str(req.desk_id) if req.desk_id is not None else None
        allocated = req.allocated_amount if req.allocated_amount is not None else 0
        strategy_type_val = (getattr(req, "strategy_type", None) or "CUSTOM").upper()
        if strategy_type_val not in ("CUSTOM", "BUILTIN"):
            strategy_type_val = "CUSTOM"

        now = datetime.now(timezone.utc)
        result = await db.execute(
            text("""
                INSERT INTO strategy_cards
                    (user_id, account_id, strategy_name, strategy_type, allocated_amount,
                     max_stocks, is_live, desk_id, strategy_params,
                     is_active, created_at, updated_at)
                VALUES
                    (:user_id, :account_id, :strategy_name, :strategy_type, :allocated_amount,
                     :max_stocks, :is_live, :desk_id, CAST(:strategy_params AS jsonb),
                     true, :now, :now)
                RETURNING card_id, user_id, account_id, strategy_name,
                          allocated_amount, max_stocks, is_live, desk_id,
                          strategy_params, is_active, created_at, updated_at
            """),
            {
                "user_id": user_id,
                "account_id": req.account_id,
                "strategy_name": req.strategy_name,
                "strategy_type": strategy_type_val,
                "allocated_amount": allocated,
                "max_stocks": req.max_stocks,
                "is_live": req.is_live,
                "desk_id": desk_val,
                "strategy_params": params_json,
                "now": now,
            },
        )
        row = result.fetchone()
        await db.commit()

        logger.info(
            "Card created: card_id=%s, user=%s, account=%s",
            row[0], user_id, req.account_id,
        )
        return self._row_to_response(row)

    async def get_card(
        self, card_id: int, user_id: int, db: AsyncSession
    ) -> StrategyCardResponse:
        """카드 단건 조회."""
        row = await self._verify_card_ownership(card_id, user_id, db)
        return self._row_to_response(row)

    async def list_cards(
        self, user_id: int, account_id: Optional[int], db: AsyncSession
    ) -> StrategyCardListResponse:
        """카드 목록 조회. account_id 필터 선택적."""
        if account_id:
            result = await db.execute(
                text("""
                    SELECT card_id, user_id, account_id, strategy_name,
                           allocated_amount, max_stocks, is_live, desk_id,
                           strategy_params, is_active, created_at, updated_at
                    FROM strategy_cards
                    WHERE user_id = :uid AND account_id = :aid AND is_active = true
                    ORDER BY card_id
                """),
                {"uid": user_id, "aid": account_id},
            )
        else:
            result = await db.execute(
                text("""
                    SELECT card_id, user_id, account_id, strategy_name,
                           allocated_amount, max_stocks, is_live, desk_id,
                           strategy_params, is_active, created_at, updated_at
                    FROM strategy_cards
                    WHERE user_id = :uid AND is_active = true
                    ORDER BY card_id
                """),
                {"uid": user_id},
            )

        rows = result.fetchall()
        cards = [self._row_to_response(r) for r in rows]
        return StrategyCardListResponse(total=len(cards), cards=cards)

    async def list_cards_for_backtest(self, db: AsyncSession) -> StrategyCardListResponse:
        """백테스트 화면 드롭다운용: strategy_cards + go100_strategy_cards 병합. CUR-GO100-UNIFIED-SAVE-BE"""
        cards: List[StrategyCardResponse] = []
        result = await db.execute(
            text("""
                SELECT card_id, user_id, account_id, strategy_name,
                       allocated_amount, max_stocks, is_live, desk_id,
                       strategy_params, is_active, created_at, updated_at
                FROM strategy_cards
                WHERE is_active = true
                ORDER BY card_id
            """),
        )
        rows = result.fetchall()
        for r in rows:
            resp = self._row_to_response(r)
            cards.append(resp)
        go100_result = await db.execute(
            text("""
                SELECT go100_card_id, user_id, strategy_name, strategy_type,
                       allocated_amount, max_stocks, is_live,
                       strategy_params, created_at, updated_at
                FROM go100_strategy_cards
                WHERE is_active = true
                ORDER BY featured_order ASC NULLS LAST, created_at DESC
            """),
        )
        go100_rows = go100_result.fetchall()
        for r in go100_rows:
            gid, uid, sname, _stype, alloc, max_s, is_live, params, created, updated = r
            cards.append(
                StrategyCardResponse(
                    card_id=gid,
                    user_id=uid,
                    account_id=0,
                    strategy_name=sname or "",
                    allocated_amount=float(alloc) if alloc is not None else None,
                    max_stocks=max_s or 5,
                    is_live=bool(is_live),
                    desk_id=None,
                    strategy_params=_parse_strategy_params(params),
                    is_active=True,
                    created_at=created,
                    updated_at=updated,
                    source="go100",
                    go100_card_id=gid,
                )
            )
        return StrategyCardListResponse(total=len(cards), cards=cards)

    async def update_card(
        self, card_id: int, user_id: int, req: StrategyCardUpdateRequest, db: AsyncSession
    ) -> StrategyCardResponse:
        """카드 수정."""
        await self._verify_card_ownership(card_id, user_id, db)

        updates = []
        params = {"cid": card_id, "now": datetime.now(timezone.utc)}

        if req.strategy_name is not None:
            updates.append("strategy_name = :strategy_name")
            params["strategy_name"] = req.strategy_name
        if req.allocated_amount is not None:
            updates.append("allocated_amount = :allocated_amount")
            params["allocated_amount"] = req.allocated_amount
        if req.max_stocks is not None:
            updates.append("max_stocks = :max_stocks")
            params["max_stocks"] = req.max_stocks
        if req.desk_id is not None:
            updates.append("desk_id = :desk_id")
            params["desk_id"] = str(req.desk_id)
        if req.strategy_params is not None:
            updates.append("strategy_params = CAST(:strategy_params AS jsonb)")
            params["strategy_params"] = json.dumps(req.strategy_params)

        if not updates:
            row = await self._verify_card_ownership(card_id, user_id, db)
            return self._row_to_response(row)

        set_clause = ", ".join(updates + ["updated_at = :now"])
        await db.execute(
            text(f"UPDATE strategy_cards SET {set_clause} WHERE card_id = :cid"),
            params,
        )
        await db.commit()

        logger.info("Card updated: card_id=%s", card_id)
        row = await self._verify_card_ownership(card_id, user_id, db)
        return self._row_to_response(row)

    async def toggle_live(
        self, card_id: int, user_id: int, req: StrategyCardToggleRequest, db: AsyncSession
    ) -> StrategyCardToggleResponse:
        """실거래 on/off 토글."""
        row = await self._verify_card_ownership(card_id, user_id, db)

        if req.is_live:
            await check_real_trading_allowed(user_id, db)
            block_result = await db.execute(
                text("SELECT buy_blocked FROM accounts WHERE account_id = :aid AND is_active = true"),
                {"aid": row[2]},
            )
            block_row = block_result.fetchone()
            if not block_row:
                raise CardServiceError(
                    f"Account {row[2]} not found or inactive"
                )
            if block_row[0]:
                raise CardServiceError(
                    f"Cannot enable live trading: account {row[2]} buy blocked"
                )

        now = datetime.now(timezone.utc)
        await db.execute(
            text("UPDATE strategy_cards SET is_live = :is_live, updated_at = :now WHERE card_id = :cid"),
            {"cid": card_id, "is_live": req.is_live, "now": now},
        )
        await db.commit()

        status = "enabled" if req.is_live else "disabled"
        logger.info("Card toggle: card_id=%s, is_live=%s", card_id, req.is_live)
        return StrategyCardToggleResponse(
            card_id=card_id,
            is_live=req.is_live,
            message=f"Live trading {status}",
        )

    async def delete_card(
        self, card_id: int, user_id: int, db: AsyncSession
    ) -> StrategyCardDeleteResponse:
        """카드 soft delete (is_active = false, is_live = false). is_live=true면 먼저 비활성화 필요."""
        row = await self._verify_card_ownership(card_id, user_id, db)
        if row[6]:  # is_live
            raise CardServiceError("먼저 비활성화한 후 삭제해 주세요.")

        now = datetime.now(timezone.utc)
        await db.execute(
            text("""
                UPDATE strategy_cards
                SET is_active = false, is_live = false, updated_at = :now
                WHERE card_id = :cid
            """),
            {"cid": card_id, "now": now},
        )
        await db.commit()

        logger.info("Card soft-deleted: card_id=%s", card_id)
        return StrategyCardDeleteResponse(card_id=card_id)

    # ─── CUR-STRATEGY-CARDS-MOBILE-v1: 전략 목록(시스템+사용자), 활성 목록, 활성화/비활성화 ───

    def _risk_level_to_int(self, value: Any) -> Optional[int]:
        """risk_level 문자열 → 1~5 정수."""
        if value is None:
            return None
        s = str(value).upper()
        if s in ("LOW", "1"): return 1
        if s in ("MEDIUM", "MED", "2"): return 2
        if s in ("HIGH", "3"): return 3
        if s in ("4"): return 4
        if s in ("5"): return 5
        try:
            v = int(float(value))
            return max(1, min(5, v))
        except (ValueError, TypeError):
            return None

    async def list_cards_with_system(
        self,
        user_id: int,
        account_id: Optional[int],
        db: AsyncSession,
        tab: str = "all",
    ) -> StrategyCardDisplayListResponse:
        """
        전체 전략(tab=all): is_featured=true인 GO100 카드만.
        내 전략(tab=my): 로그인 사용자의 GO100 카드만.
        V4.1 strategy_cards는 GO100 Catalog에서 제외. CUR-GO100-CARD-REDESIGN-BE
        CUR-GO100-MY-STRATEGY-FIX: user_id가 레거시 users.id일 수 있으므로 v4_users.user_id로 변환 후 사용.
        """
        cards: List[StrategyCardDisplay] = []
        # tab=my(또는 fallback) 시 user_id가 레거시 users.id일 수 있으므로 v4_users.user_id로 변환 (CUR-GO100-MY-STRATEGY-FIX)
        effective_uid = user_id
        if tab != "all":
            v4_row = (await db.execute(text("SELECT user_id FROM v4_users WHERE user_id = :uid"), {"uid": user_id})).fetchone()
            if v4_row:
                effective_uid = v4_row[0]
            else:
                leg_row = (await db.execute(
                    text("SELECT vu.user_id FROM v4_users vu INNER JOIN users u ON u.email = vu.email WHERE u.id = :uid"),
                    {"uid": user_id},
                )).fetchone()
                if leg_row:
                    effective_uid = leg_row[0]

        query_go100 = """
            SELECT go100_card_id, user_id, account_id, strategy_name,
                   strategy_type, allocated_amount, max_stocks,
                   card_status, is_live, is_active,
                   strategy_params, entry_rules, exit_rules, risk_params,
                   last_backtest_return, last_backtest_mdd, last_backtest_sharpe,
                   created_at, updated_at, is_featured, featured_order
            FROM go100_strategy_cards
        """
        if tab == "all":
            query = query_go100 + """
                WHERE is_featured = true AND is_active = true
                ORDER BY featured_order ASC, go100_card_id ASC
            """
            result = await db.execute(text(query))
        elif tab == "my":
            query = query_go100 + """
                WHERE user_id = :uid AND is_active = true
                ORDER BY go100_card_id DESC
            """
            result = await db.execute(text(query), {"uid": effective_uid})
        else:
            # fallback: 내 카드
            query = query_go100 + """
                WHERE user_id = :uid AND is_active = true
                ORDER BY go100_card_id DESC
            """
            result = await db.execute(text(query), {"uid": effective_uid})

        rows = result.fetchall()
        for row in rows:
            cards.append(
                StrategyCardDisplay(
                    id=row[0],
                    name=row[3] or "",
                    description=None,
                    type=(row[4] or "LLM_GENERATED"),
                    risk_level=None,
                    expected_return_min=float(row[14]) if row[14] is not None else None,
                    expected_return_max=float(row[14]) if row[14] is not None else None,
                    min_invest_amount=None,
                    is_active=row[9] if row[9] is not None else True,
                    connected_account_id=row[2],
                    performance=None,
                    card_id=row[0],
                    user_id=row[1],
                    account_id=row[2],
                    allocated_amount=float(row[5] or 0),
                    max_stocks=row[6] or 5,
                    is_live=row[8] or False,
                    desk_id=None,
                    strategy_params=_parse_strategy_params(row[10]) if row[10] else None,
                    created_at=row[17],
                    updated_at=row[18],
                    source="go100",
                    backtest_return=float(row[14]) if row[14] is not None else None,
                    backtest_mdd=float(row[15]) if row[15] is not None else None,
                    backtest_sharpe=float(row[16]) if row[16] is not None else None,
                )
            )
        return StrategyCardDisplayListResponse(total=len(cards), cards=cards)

    async def list_v4_cards_with_system(
        self, user_id: int, account_id: Optional[int], db: AsyncSession
    ) -> StrategyCardDisplayListResponse:
        """
        V4.1 전용: strategy_cards + strategies + go100 병합 (기존 로직).
        trading41.newtalk.kr 등 V4.1 대시보드에서 tab=v4 로 호출 시 사용. CUR-GO100-CARD-REDESIGN-BE
        """
        # 1) 사용자 카드 목록 (V4.1 strategy_cards)
        if account_id:
            cards_result = await db.execute(
                text("""
                    SELECT card_id, user_id, account_id, strategy_name,
                           allocated_amount, max_stocks, is_live, desk_id,
                           strategy_params, is_active, created_at, updated_at
                    FROM strategy_cards
                    WHERE user_id = :uid AND account_id = :aid AND is_active = true
                    ORDER BY card_id
                """),
                {"uid": user_id, "aid": account_id},
            )
        else:
            cards_result = await db.execute(
                text("""
                    SELECT card_id, user_id, account_id, strategy_name,
                           allocated_amount, max_stocks, is_live, desk_id,
                           strategy_params, is_active, created_at, updated_at
                    FROM strategy_cards
                    WHERE user_id = :uid AND is_active = true
                    ORDER BY card_id
                """),
                {"uid": user_id},
            )
        card_rows = cards_result.fetchall()
        user_names = {r[3] for r in card_rows}

        # 2) 시스템 전략 (strategies)
        strat_result = await db.execute(
            text("""
                SELECT id, name, description, category, risk_level, avg_return
                FROM strategies
                WHERE is_approved = true
                ORDER BY id
            """),
        )
        strat_rows = strat_result.fetchall()

        # 3) 전략별 최근 수익 (strategy_performance)
        perf_result = await db.execute(
            text("""
                SELECT strategy_id, real_pnl, real_win_rate, trade_date
                FROM strategy_performance
                WHERE trade_date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY strategy_id, trade_date DESC
            """),
        )
        perf_rows = perf_result.fetchall()
        perf_by_id: dict = {}
        for row in perf_rows:
            sid = row[0]
            if sid not in perf_by_id:
                perf_by_id[sid] = {"real_pnl": row[1], "real_win_rate": row[2], "trade_date": str(row[3]) if row[3] else None}

        display_list: List[StrategyCardDisplay] = []

        for row in strat_rows:
            sid, sname, sdesc, scat, srisk, sret = row
            is_active = sname in user_names
            connected = None
            card_id_val = None
            alloc = None
            max_s = None
            is_live_val = None
            desk_val = None
            params = None
            created = None
            updated = None
            for r in card_rows:
                if r[3] == sname:
                    connected = r[2]
                    card_id_val = r[0]
                    alloc = float(r[4]) if r[4] is not None else None
                    max_s = r[5]
                    is_live_val = r[6]
                    desk_val = _parse_desk_id(r[7])
                    params = _parse_strategy_params(r[8])
                    created = r[10]
                    updated = r[11]
                    break

            avg_ret = float(sret) if sret is not None else None
            display_list.append(
                StrategyCardDisplay(
                    id=sid,
                    name=sname or "",
                    description=sdesc,
                    type=scat,
                    risk_level=self._risk_level_to_int(srisk),
                    expected_return_min=avg_ret,
                    expected_return_max=avg_ret,
                    min_invest_amount=1_000_000,
                    is_active=is_active,
                    connected_account_id=connected,
                    performance=perf_by_id.get(str(sid)),
                    card_id=card_id_val,
                    user_id=user_id if is_active else None,
                    account_id=connected,
                    allocated_amount=alloc,
                    max_stocks=max_s,
                    is_live=is_live_val,
                    desk_id=desk_val,
                    strategy_params=params,
                    created_at=created,
                    updated_at=updated,
                )
            )

        # 4) 사용자 카드 중 시스템에 없는 커스텀 전략만 추가
        custom_result = await db.execute(
            text("""
                SELECT card_id, user_id, account_id, strategy_name,
                       allocated_amount, max_stocks, is_live, desk_id,
                       strategy_params, is_active, created_at, updated_at
                FROM strategy_cards
                WHERE user_id = :uid AND is_active = true AND strategy_type = 'CUSTOM'
                ORDER BY card_id
            """),
            {"uid": user_id},
        )
        custom_rows = custom_result.fetchall()
        system_names = {r[1] for r in strat_rows}
        for r in custom_rows:
            if r[3] in system_names:
                continue
            display_list.append(
                StrategyCardDisplay(
                    id=r[0],
                    name=r[3],
                    description=None,
                    type="CUSTOM",
                    risk_level=None,
                    expected_return_min=None,
                    expected_return_max=None,
                    min_invest_amount=None,
                    is_active=True,
                    connected_account_id=r[2],
                    performance=None,
                    card_id=r[0],
                    user_id=r[1],
                    account_id=r[2],
                    allocated_amount=float(r[4]) if r[4] is not None else None,
                    max_stocks=r[5],
                    is_live=r[6],
                    desk_id=_parse_desk_id(r[7]),
                    strategy_params=_parse_strategy_params(r[8]),
                    created_at=r[10],
                    updated_at=r[11],
                )
            )

        # 5) GO100 전략카드 병합
        try:
            go100_result = await db.execute(
                text("""
                    SELECT go100_card_id, user_id, strategy_name, card_status, is_active, is_live,
                           allocated_amount, max_stocks, strategy_params,
                           last_backtest_return, last_backtest_mdd, last_backtest_sharpe,
                           created_at, updated_at
                    FROM go100_strategy_cards
                    WHERE user_id = :uid AND is_active = true
                    ORDER BY updated_at DESC
                """),
                {"uid": user_id},
            )
            go100_rows = go100_result.fetchall()
            for r in go100_rows:
                (go100_card_id, uid, strategy_name, _card_status, is_active_g, is_live_g,
                 alloc, max_s, params, bt_ret, bt_mdd, bt_sharpe, created, updated) = r
                display_list.append(
                    StrategyCardDisplay(
                        id=go100_card_id,
                        name=strategy_name or "",
                        description=None,
                        type="GO100",
                        risk_level=None,
                        expected_return_min=float(bt_ret) if bt_ret is not None else None,
                        expected_return_max=float(bt_ret) if bt_ret is not None else None,
                        min_invest_amount=None,
                        is_active=bool(is_active_g),
                        connected_account_id=None,
                        performance=None,
                        card_id=go100_card_id,
                        user_id=uid,
                        account_id=None,
                        allocated_amount=float(alloc) if alloc is not None else None,
                        max_stocks=max_s,
                        is_live=bool(is_live_g) if is_live_g is not None else False,
                        desk_id=None,
                        strategy_params=_parse_strategy_params(params) if params else None,
                        created_at=created,
                        updated_at=updated,
                        source="go100",
                        backtest_return=float(bt_ret) if bt_ret is not None else None,
                        backtest_mdd=float(bt_mdd) if bt_mdd is not None else None,
                        backtest_sharpe=float(bt_sharpe) if bt_sharpe is not None else None,
                    )
                )
        except Exception as e:
            logging.getLogger(__name__).warning("list_v4_cards_with_system go100 merge skip: %s", e)

        return StrategyCardDisplayListResponse(total=len(display_list), cards=display_list)

    async def list_active_cards(
        self, user_id: int, db: AsyncSession
    ) -> StrategyCardListResponse:
        """내 활성 전략 카드만 (is_active=true)."""
        return await self.list_cards(user_id, None, db)

    async def activate_strategy(
        self, strategy_id: str, user_id: int, req: StrategyActivateRequest, db: AsyncSession
    ) -> StrategyCardResponse:
        """시스템 전략 활성화: strategies에서 SELECT 후 strategy_cards에 INSERT. 레거시 테이블은 SELECT만."""
        strat_result = await db.execute(
            text("SELECT id, name, description, category FROM strategies WHERE id = :sid AND is_approved = true"),
            {"sid": strategy_id},
        )
        strat_row = strat_result.fetchone()
        if not strat_row:
            raise CardNotFoundError(f"Strategy {strategy_id} not found or not approved")

        acct_result = await db.execute(
            text("SELECT user_id FROM accounts WHERE account_id = :aid AND is_active = true"),
            {"aid": req.account_id},
        )
        acct_row = acct_result.fetchone()
        if not acct_row:
            raise CardServiceError(f"Account {req.account_id} not found")
        if acct_row[0] != user_id:
            raise CardOwnershipError(f"Account {req.account_id} not owned by user")

        await check_card_limit(user_id, req.account_id, db)

        params_json = json.dumps(req.settings) if req.settings else "{}"
        now = datetime.now(timezone.utc)
        result = await db.execute(
            text("""
                INSERT INTO strategy_cards
                    (user_id, account_id, strategy_name, strategy_type, allocated_amount,
                     max_stocks, is_live, desk_id, strategy_params, is_active, created_at, updated_at)
                VALUES
                    (:user_id, :account_id, :strategy_name, 'BUILTIN', :allocated_amount,
                     5, false, NULL, CAST(:strategy_params AS jsonb), true, :now, :now)
                RETURNING card_id, user_id, account_id, strategy_name,
                          allocated_amount, max_stocks, is_live, desk_id,
                          strategy_params, is_active, created_at, updated_at
            """),
            {
                "user_id": user_id,
                "account_id": req.account_id,
                "strategy_name": strat_row[1],
                "allocated_amount": req.invest_amount,
                "strategy_params": params_json,
                "now": now,
            },
        )
        row = result.fetchone()
        await db.commit()
        logger.info("Strategy activated: strategy_id=%s -> card_id=%s", strategy_id, row[0])
        return self._row_to_response(row)


strategy_card_service = StrategyCardService()
