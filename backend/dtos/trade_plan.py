# backend/dtos/trade_plan.py
"""
Contains the data class for a complete, executable trade plan.

@layer: Backend (DTO)
@dependencies: [pydantic, pandas, uuid]
@responsibilities:
    - Defines the standardized data structure for a fully planned trade, ready
      for execution.
"""
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
import pandas as pd

class TradePlan(BaseModel):
    """Represents a complete, executable plan for a single trade.

    This DTO is created by a SizePlanner (Fase 5c). It enriches a
    RiskDefinedSignal with the final position size and value, calculated
    based on portfolio risk rules. It is the final, concrete plan before
    being sent to the PortfolioOverlay (Fase 6) for a last check.

    Attributes:
        correlation_id (uuid.UUID): The unique ID from the source Signal.
        entry_time (pd.Timestamp): The timestamp of the original signal.
        asset (str): The asset to be traded.
        direction (str): The direction of the trade ('long' or 'short').
        signal_type (str): The name of the original signal generator.
        entry_price (float): The calculated entry price for the trade.
        sl_price (float): The absolute stop-loss price.
        tp_price (Optional[float]): The absolute take-profit price, if any.
        position_value_eur (float): The total value of the position in EUR.
        position_size_asset (float): The size of the position in the base asset.
    """
    correlation_id: uuid.UUID
    entry_time: pd.Timestamp
    asset: str
    direction: str
    signal_type: str
    entry_price: float
    sl_price: float
    tp_price: Optional[float] = None
    position_value_eur: float
    position_size_asset: float

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
