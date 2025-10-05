# backend/dtos/routed_trade_plan.py
"""
Contains the DTO that represents a TradePlan decorated with execution tactics.

@layer: Backend (DTO)
@dependencies: [pydantic, uuid, backend.dtos.trade_plan]
@responsibilities:
    - Defines the universal blueprint for how an order should be executed.
"""
import uuid
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from .trade_plan import TradePlan

class RoutedTradePlan(BaseModel):
    """
    The universal blueprint for how an order should be executed.

    This DTO is the output of an OrderRouter plugin (Fase 8). It takes the
    complete strategic intent (the TradePlan) and enriches it with concrete,
    technical execution instructions for the ExecutionHandler. It serves as the
    definitive contract between the strategy layer and the execution layer.

    Attributes:
        correlation_id (uuid.UUID): The unique ID from the source Signal.
        trade_plan (TradePlan): The nested strategic plan to be executed.
        order_type (Literal['market', 'limit']): The fundamental order type.
        limit_price (Optional[float]): The price for a limit order.
        time_in_force (Literal['GTC', 'IOC', 'FOK']): How long the order remains valid.
        post_only (bool): Flag to ensure the order is a "maker" order.
        execution_strategy (Optional[Literal['twap']]): Label for an algorithmic strategy.
        strategy_params (Optional[Dict[str, Any]]): Parameters for the algorithmic strategy.
        preferred_exchange (Optional[str]): A hint for the ExecutionHandler.
    """
    correlation_id: uuid.UUID
    trade_plan: TradePlan

    # --- Tactical Execution Instructions ---
    order_type: Literal['market', 'limit']
    limit_price: Optional[float] = None
    time_in_force: Literal['GTC', 'IOC', 'FOK'] = 'GTC'
    post_only: bool = False
    execution_strategy: Optional[Literal['twap']] = None
    strategy_params: Optional[Dict[str, Any]] = None
    preferred_exchange: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
