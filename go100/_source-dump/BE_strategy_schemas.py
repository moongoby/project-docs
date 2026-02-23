# CUR-GO100-UNIFIED-SAVE-BE, 2026-02-23
# Modified by: CUR-GO100-CARD-DETAIL-FIX, 2026-02-22
# Modified by: CUR-GO100-PHASE3-CARD-SERVICE, 2026-02-21
"""
GO100 전략 카드 Pydantic 스키마 및 상태 전이 상수.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# --- 전략 카드 생애주기 상태 ---
CARD_STATUS_VALUES = ["IDEA", "DRAFT", "BACKTESTED", "PAPER_LIVE", "LIVE", "PAUSED", "RETIRED"]
SOURCE_TYPE_VALUES = ["SYSTEM", "CUSTOM", "LLM", "SHARED"]
ALLOCATION_TYPE_VALUES = ["EQUAL", "RATIO", "FIXED_AMOUNT", "KELLY"]

# --- 허용 상태 전이 맵 ---
ALLOWED_TRANSITIONS = {
    "IDEA": ["DRAFT", "RETIRED"],
    "DRAFT": ["BACKTESTED", "RETIRED"],
    "BACKTESTED": ["PAPER_LIVE", "DRAFT", "RETIRED"],
    "PAPER_LIVE": ["LIVE", "PAUSED", "RETIRED"],
    "LIVE": ["PAUSED", "RETIRED"],
    "PAUSED": ["LIVE", "RETIRED"],
    "RETIRED": [],
}


# --- DTO ---


class Go100StrategyCardCreate(BaseModel):
    strategy_name: str = Field(..., min_length=1, max_length=200)
    strategy_type: str = Field(default="GO100_AI", max_length=50)
    description: Optional[str] = None
    source_type: Optional[str] = Field(default="CUSTOM", max_length=20)
    universe_filter: Optional[dict[str, Any]] = Field(default_factory=dict)
    entry_rules: Optional[dict[str, Any] | list] = Field(default_factory=list)
    exit_rules: Optional[dict[str, Any] | list] = Field(default_factory=list)
    risk_params: Optional[dict[str, Any]] = Field(default_factory=dict)
    strategy_params: Optional[dict[str, Any]] = Field(default_factory=dict)
    allocation_type: Optional[str] = Field(default="EQUAL", max_length=20)
    allocation_value: Optional[float] = None
    max_stocks: Optional[int] = Field(default=5, ge=1, le=100)
    # CUR-GO100-UNIFIED-SAVE-BE: API 호환용 별칭 (entry_rules/exit_rules/risk_params에 매핑)
    buy_conditions: Optional[dict[str, Any] | list] = None
    sell_conditions: Optional[dict[str, Any] | list] = None
    risk_management: Optional[dict[str, Any]] = None
    indicators: Optional[dict[str, Any]] = None
    parameters: Optional[dict[str, Any]] = None
    stock_codes: Optional[list[str]] = None


class Go100StrategyCardUpdate(BaseModel):
    strategy_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    universe_filter: Optional[dict[str, Any]] = None
    entry_rules: Optional[dict[str, Any] | list] = None
    exit_rules: Optional[dict[str, Any] | list] = None
    risk_params: Optional[dict[str, Any]] = None
    strategy_params: Optional[dict[str, Any]] = None
    allocation_type: Optional[str] = None
    allocation_value: Optional[float] = None
    max_stocks: Optional[int] = Field(None, ge=1, le=100)
    account_id: Optional[int] = None
    is_active: Optional[bool] = None


class Go100StrategyCardResponse(BaseModel):
    go100_card_id: int
    user_id: int
    account_id: Optional[int] = None
    strategy_name: str
    strategy_type: Optional[str] = None
    universe_filter: Optional[dict[str, Any]] = None
    entry_rules: Optional[dict[str, Any] | list] = None
    exit_rules: Optional[dict[str, Any] | list] = None
    risk_params: Optional[dict[str, Any]] = None
    strategy_params: Optional[dict[str, Any]] = None
    allocated_amount: Optional[float] = None
    max_stocks: Optional[int] = None
    card_status: str
    is_active: bool = True
    is_live: bool = False
    source_type: Optional[str] = None
    source_store_card_id: Optional[int] = None
    source_user_id: Optional[int] = None
    llm_session_id: Optional[str] = None
    last_backtest_id: Optional[int] = None
    last_backtest_return: Optional[float] = None
    last_backtest_mdd: Optional[float] = None
    last_backtest_sharpe: Optional[float] = None
    last_backtest_at: Optional[datetime] = None
    paper_total_return: Optional[float] = None
    paper_start_date: Optional[str] = None
    paper_days: Optional[int] = None
    disclaimer_agreed: bool = False
    disclaimer_agreed_at: Optional[datetime] = None
    dedicated_account: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Go100StrategyCardListResponse(BaseModel):
    items: list[Go100StrategyCardResponse]
    total_count: int
    page: int
    page_size: int


class Go100StatusTransitionRequest(BaseModel):
    target_status: str = Field(..., min_length=1)
    disclaimer_agreed: Optional[bool] = None
    account_id: Optional[int] = None


class Go100StoreSubscribeRequest(BaseModel):
    store_card_id: int = Field(..., gt=0)
    account_id: Optional[int] = None


class Go100CardSummary(BaseModel):
    go100_card_id: int
    strategy_name: str
    card_status: str
    source_type: Optional[str] = None
    last_backtest_return: Optional[float] = None
    is_live: bool = False
    created_at: datetime
