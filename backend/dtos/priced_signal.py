# backend/dtos/priced_signal.py
"""
Contains the data class for a signal enriched with exit prices.
"""
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
import pandas as pd

class PricedSignal(BaseModel):
    """Represents a signal with absolute stop-loss and take-profit prices.

    This DTO is created by an ExitPlanner. It enriches an ExecutionSignal
    with the initial risk parameters for the trade.

    Attributes:
        correlation_id (uuid.UUID): The unique ID from the source Signal.
        timestamp (pd.Timestamp): The timestamp of the original signal.
        asset (str): The asset to be traded.
        direction (str): The direction of the trade.
        signal_type (str): The name of the original signal generator.
        entry_price (float): The calculated entry price.
        entry_method (str): A label for the entry tactic used.
        sl_price (float): The absolute stop-loss price.
        tp_price (Optional[float]): The absolute take-profit price, if any.
    """
    correlation_id: uuid.UUID
    timestamp: pd.Timestamp
    asset: str
    direction: str
    signal_type: str
    entry_price: float
    entry_method: str
    sl_price: float
    tp_price: Optional[float] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
