# backend/dtos/execution_directive.py
"""
Contains the DTO for a final, flattened execution instruction.

@layer: Backend (DTO)
@dependencies: [pydantic, pandas, uuid]
@responsibilities:
    - Defines the flat, universal contract for an instruction sent to the
      ExecutionHandler.
"""
import uuid
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
import pandas as pd

class ExecutionDirective(BaseModel):
    """
    A flat, final, and universal instruction for the ExecutionHandler.

    This DTO is a flattened representation of a RoutedTradePlan and contains
    all necessary information to execute, manage, and track a trade. It serves
    as the definitive, simple contract between the StrategyEngine's output and
    the execution layer.

    Attributes:
        correlation_id (uuid.UUID): The unique ID from the source Signal.
        signal_type (str): The name of the logic that generated the original signal.
        asset (str): The asset to be traded.
        direction (Literal['long', 'short']): The direction of the trade.
        entry_price (float): The calculated entry price for the trade.
        sl_price (float): The absolute stop-loss price.
        tp_price (Optional[float]): The absolute take-profit price, if any.
        position_value_quote (float): The total value of the position in the quote currency.
        position_size_asset (float): The size of the position in the base asset.
        order_type (Literal['market', 'limit']): The fundamental order type.
        limit_price (Optional[float]): The price for a limit order.
        time_in_force (Literal['GTC', 'IOC', 'FOK']): How long the order remains valid.
        post_only (bool): Flag to ensure the order is a "maker" order.
        execution_strategy (Optional[Literal['twap']]): Label for an algorithmic strategy.
        strategy_params (Optional[Dict[str, Any]]): Parameters for the algorithmic strategy.
        preferred_exchange (Optional[str]): A hint for the ExecutionHandler.
        entry_time (pd.Timestamp): From the original signal.
    """
    # Traceability & Identity
    correlation_id: uuid.UUID
    signal_type: str

    # Core Trade Parameters
    asset: str
    direction: Literal['long', 'short']
    entry_price: float
    sl_price: float
    tp_price: Optional[float]

    # Sizing
    position_value_quote: float
    position_size_asset: float

    # Tactical Execution Instructions
    order_type: Literal['market', 'limit']
    limit_price: Optional[float] = None
    time_in_force: Literal['GTC', 'IOC', 'FOK'] = 'GTC'
    post_only: bool = False
    execution_strategy: Optional[Literal['twap']] = None
    strategy_params: Optional[Dict[str, Any]] = None
    preferred_exchange: Optional[str] = None

    # Timestamps
    entry_time: pd.Timestamp

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
