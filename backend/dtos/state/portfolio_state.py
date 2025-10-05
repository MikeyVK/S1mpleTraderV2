# backend/dtos/portfolio_state.py
"""
Contains the DTO for a snapshot of the portfolio's financial state.

@layer: Backend (DTO)
@dependencies: [pydantic]
@responsibilities:
    - Defines the standardized, read-only data structure that represents the
      financial state of a portfolio at a specific moment in time.
    - Defines the specific data contracts for open positions and open orders.
"""
from __future__ import annotations
from uuid import UUID
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
import pandas as pd

class OpenPosition(BaseModel):
    """
    A data contract for a single, currently open position.
    """
    model_config = {"arbitrary_types_allowed": True}

    correlation_id: UUID = Field(..., description="open_position.correlation_id.desc")
    asset: str = Field(..., description="open_position.asset.desc")
    direction: Literal['long', 'short'] = Field(..., description="open_position.direction.desc")
    entry_price: float = Field(..., description="open_position.entry_price.desc")
    position_size_asset: float = Field(..., description="open_position.position_size_asset.desc")
    entry_timestamp: pd.Timestamp = Field(..., description="open_position.entry_timestamp.desc")


class OpenOrder(BaseModel):
    """
    A data contract for a single, currently open (unfilled) order.
    """
    order_id: str = Field(..., description="open_order.order_id.desc")
    asset: str = Field(..., description="open_order.asset.desc")
    side: Literal['buy', 'sell'] = Field(..., description="open_order.side.desc")
    order_type: Literal['limit',
                        'market',
                        'stop_loss',
                        'take_profit'] = Field(..., description="open_order.order_type.desc")
    amount: float = Field(..., description="open_order.amount.desc")
    price: Optional[float] = Field(None, description="open_order.price.desc")


class PortfolioState(BaseModel):
    """
    A read-only snapshot of the financial state of the portfolio.

    This DTO is used to pass the current financial reality to various
    components, such as the StrategyEngine, without exposing the full
    Portfolio object. This ensures that the state can be read but not
    modified, adhering to a clear data flow.
    """
    equity: float = Field(
        ...,
        description="portfolio_state.equity.desc"
    )
    available_cash: float = Field(
        ...,
        description="portfolio_state.available_cash.desc"
    )
    total_exposure_quote: float = Field(
        ...,
        description="portfolio_state.total_exposure_quote.desc"
    )
    open_positions: List[OpenPosition] = Field( # type: ignore
        default_factory=list,
        description="portfolio_state.open_positions.desc"
    )
    open_orders: List[OpenOrder] = Field( # type: ignore
        default_factory=list,
        description="portfolio_state.open_orders.desc"
    )

# Pylance Suppression Note for 'future Me':
# The Pylance linter may incorrectly flag the 'default_factory=list' lines
# below as a 'reportUnknownVariableType' error. This is a known false
# positive. Using 'default_factory=list' is the idiomatic and correct
# Pydantic approach for providing a mutable default (an empty list).
# The '# type: ignore' comment is intentionally used here to suppress this
# specific, non-critical linter warning while maintaining the functionally
# superior implementatio
