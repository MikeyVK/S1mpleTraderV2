# backend/dtos/trade_plan.py
"""
Contains the data class for a complete, executable trade plan.

@layer: Backend (DTO)
@dependencies: [pydantic, uuid, .risk_defined_signal]
@responsibilities:
    - Defines the standardized data structure for a fully planned trade, ready
      for the OrderRouter.
"""
import uuid
from pydantic import BaseModel, ConfigDict
from .risk_defined_signal import RiskDefinedSignal

class TradePlan(BaseModel):
    """
    Represents a complete strategic plan for a single trade.

    This DTO is created by a SizePlanner (Fase 7). It enriches a
    RiskDefinedSignal with the final position size and value. It contains
    all necessary strategic information before being passed to the
    OrderRouter (Fase 8) to be translated into tactical execution instructions.

    Attributes:
        correlation_id (uuid.UUID): The unique ID from the source Signal.
        risk_defined_signal (RiskDefinedSignal): The nested DTO from the previous phase.
        position_value_quote (float): The total value of the position in the quote currency.
        position_size_asset (float): The size of the position in the base asset.
    """
    correlation_id: uuid.UUID
    risk_defined_signal: RiskDefinedSignal
    position_value_quote: float
    position_size_asset: float

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
