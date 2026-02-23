# CUR-GO100-PHASE2-STABILIZE STEP2, 2026-02-23 — ISS-003: 전략 저장 E2E (라우터 예외 로깅)
# CUR-GO100-HOTFIX-IMPORT, 2026-02-23 - get_effective_uid/text import 추가
# CUR-GO100-UNIFIED-SAVE-BE, 2026-02-23
# Modified by: CUR-GO100-MY-STRATEGY-FIX, 2026-02-22
# Modified by: CUR-GO100-CARD-DETAIL-FIX, 2026-02-22
# Modified by: CUR-GO100-FIX-BACKEND, 2026-02-22
# Modified by: CUR-GO100-PHASE3-CARD-SERVICE, 2026-02-21
"""
GO100 전략 카드 API Router.
prefix: /api/go100/strategy-cards, /api/go100/store
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security_middleware import get_current_user
from backend.app.services.go100.strategy import (
    go100_strategy_card_service,
    Go100StrategyCardCreate,
    Go100StrategyCardUpdate,
    Go100StrategyCardResponse,
    Go100StrategyCardListResponse,
    Go100StatusTransitionRequest,
    Go100StoreSubscribeRequest,
)
from backend.app.services.go100.strategy.card_service import (
    NotFoundException,
    BusinessLogicException,
    OwnershipException,
)
from backend.app.services.go100.user_utils import get_effective_uid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/go100/strategy-cards", tags=["GO100 Strategy Cards"])


@router.post("", response_model=Go100StrategyCardResponse, status_code=201)
async def create_card(
    data: Go100StrategyCardCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """새 전략 카드 생성."""
    try:
        return await go100_strategy_card_service.create_card(
            current_user["user_id"], data, db
        )
    except Exception as e:
        if isinstance(e, (NotFoundException, BusinessLogicException, OwnershipException)):
            raise HTTPException(status_code=400, detail=str(e))
        logger.exception("GO100 전략카드 생성 500: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=Go100StrategyCardListResponse)
async def list_cards(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 전략 카드 목록 조회."""
    return await go100_strategy_card_service.list_cards(
        current_user["user_id"], page, page_size, status, source_type, db
    )


@router.get("/{card_id}", response_model=Go100StrategyCardResponse)
async def get_card(
    card_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전략 카드 상세 조회."""
    try:
        return await go100_strategy_card_service.get_card(
            current_user["user_id"], card_id, db
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OwnershipException as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{card_id}", response_model=Go100StrategyCardResponse)
async def update_card(
    card_id: int,
    data: Go100StrategyCardUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전략 카드 수정."""
    try:
        return await go100_strategy_card_service.update_card(
            current_user["user_id"], card_id, data, db
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (BusinessLogicException, OwnershipException) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{card_id}/transition", response_model=Go100StrategyCardResponse)
async def transition_status(
    card_id: int,
    req: Go100StatusTransitionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """상태 전이."""
    try:
        return await go100_strategy_card_service.transition_status(
            current_user["user_id"], card_id, req, db
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (BusinessLogicException, OwnershipException) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{card_id}/toggle")
async def toggle_card_active(
    card_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GO100 전략 카드 활성/비활성 토글. CUR-GO100-HOTFIX-CRITICAL"""
    effective_uid = await get_effective_uid(db, current_user["user_id"])
    result = await db.execute(
        text("""
            UPDATE go100_strategy_cards
            SET is_active = NOT is_active, updated_at = NOW()
            WHERE go100_card_id = :card_id AND user_id = :uid
            RETURNING go100_card_id, strategy_name, is_active
        """),
        {"card_id": card_id, "uid": effective_uid},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="카드를 찾을 수 없습니다")
    await db.commit()
    return {"go100_card_id": row[0], "strategy_name": row[1], "is_active": row[2]}


@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전략 카드 삭제 (soft delete)."""
    try:
        return await go100_strategy_card_service.delete_card(
            current_user["user_id"], card_id, db
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (BusinessLogicException, OwnershipException) as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Store (마켓플레이스): /api/go100/store ---
store_router = APIRouter(prefix="/api/go100", tags=["GO100 Store"])


@store_router.get("/store")
async def list_store(db: AsyncSession = Depends(get_db)):
    """시스템 전략 마켓플레이스 목록."""
    return await go100_strategy_card_service.list_store(db)


@store_router.post("/store/subscribe", response_model=Go100StrategyCardResponse, status_code=201)
async def store_subscribe(
    req: Go100StoreSubscribeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """시스템 전략 구독 (복제)."""
    try:
        return await go100_strategy_card_service.subscribe_from_store(
            current_user["user_id"], req, db
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (BusinessLogicException, OwnershipException) as e:
        raise HTTPException(status_code=400, detail=str(e))