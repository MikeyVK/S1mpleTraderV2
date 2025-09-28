# backend/dtos/closed_trade.py
"""
Contains the data class for a closed trade, representing a completed transaction.

@layer: Backend (DTO)
@dependencies: [pydantic, pandas, uuid]
@responsibilities:
    - Defines the standardized data structure for a trade that has been fully
      executed and resulted in a profit or loss.
"""
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
import pandas as pd

class ClosedTrade(BaseModel):
    """Represents the final, recorded result of a single completed trade.

    This DTO is created by the Portfolio after a position is closed. It serves
    as the definitive, historical record for performance analysis and reporting.
    It contains all information from the original TradePlan, enriched with the
    actual exit details and the resulting profit or loss.

    Attributes:
        correlation_id (uuid.UUID): The unique ID linking this record to its
                                    full context log. Inherited from the TradePlan.
        entry_time (pd.Timestamp): The timestamp when the trade was opened.
        exit_time (pd.Timestamp): The timestamp when the trade was closed.
        asset (str): The asset that was traded.
        direction (str): The direction of the trade ('long' or 'short').
        signal_type (str): The name of the logic that generated the original signal.
        entry_price (float): The actual entry price.
        exit_price (float): The actual exit price.
        sl_price (float): The original stop-loss price from the TradePlan.
        tp_price (Optional[float]): The original take-profit price, if any.
        position_value_eur (float): The initial value of the position.
        position_size_asset (float): The size of the position.
        pnl_eur (float): The net profit or loss of the trade in EUR, after fees.
    """
    correlation_id: uuid.UUID
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    asset: str
    direction: str
    signal_type: str
    entry_price: float
    exit_price: float
    sl_price: float
    tp_price: Optional[float] = None
    position_value_eur: float
    position_size_asset: float
    pnl_eur: float

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
