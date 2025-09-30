# backend/dtos/risk_defined_signal.py
"""
Contains the data class for a signal enriched with exit prices (risk definition).

@layer: Backend (DTO)
@dependencies: [pydantic, uuid]
@responsibilities:
    - Defines the data structure for a signal that has been enriched with
      absolute stop-loss and take-profit prices by an ExitPlanner.
"""
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .entry_signal import EntrySignal

class RiskDefinedSignal(BaseModel):
    """Represents a signal with its risk parameters fully defined.

    This DTO is created by an ExitPlanner (Fase 5b). It enriches an
    EntrySignal with the absolute stop-loss and (optional) take-profit prices.
    It serves as the direct input for the SizePlanner (Fase 5c), providing all
    necessary information to calculate position size based on risk.

    Attributes:
        correlation_id (uuid.UUID): The unique ID from the source Signal.
        entry_signal: the original EntrySignal DTO.
        sl_price (float): The absolute stop-loss price, defining the risk boundary.
        tp_price (Optional[float]): The absolute take-profit price, if any.
    """
    correlation_id: uuid.UUID
    entry_signal: EntrySignal
    sl_price: float
    tp_price: Optional[float] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
