# backend/dtos/entry_signal.py
"""
Contains the data class for a signal enriched with an entry tactic.

@layer: Backend (DTO)
@dependencies: [pydantic, pandas, uuid]
@responsibilities:
    - Defines the data structure for a signal that has been enriched with
      a concrete entry tactic by an EntryPlanner.
"""
import uuid
from pydantic import BaseModel, ConfigDict
from .signal import Signal

class EntrySignal(BaseModel):
    """Represents a signal with a concrete entry tactic.

    This DTO is created by an EntryPlanner (Fase 5a). It enriches a raw
    Signal DTO with a calculated entry price and a descriptive entry method.
    It serves as the input for the ExitPlanner (Fase 5b).

    Attributes:
        correlation_id (uuid.UUID): The unique ID inherited from the source Signal.
        signal: the original Signal DTO.
        entry_price (float): The calculated entry price for the trade.
    """
    correlation_id: uuid.UUID
    signal: Signal
    entry_price: float

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
