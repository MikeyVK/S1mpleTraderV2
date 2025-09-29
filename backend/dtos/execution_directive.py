# backend/dtos/execution_directive.py
"""
Contains the DTOs that represent the final, executable output of the
StrategyEngine. An ExecutionDirective is a command for the ExecutionHandler.

@layer: Backend (DTO)
"""
from typing import Literal, Union
from pydantic import BaseModel, Field
import pandas as pd

from .trade_plan import TradePlan


# --- Base Directive ---

class BaseDirective(BaseModel):
    """A base model for all execution directives."""
    pass


# --- Concrete Directive Types ---

class SingleTradeDirective(BaseDirective):
    """
    The most common directive: execute a single, complete trade plan.
    This is the direct output for most strategies.
    """
    directive_type: Literal['single_trade']
    trade_plan: TradePlan


class CancelAllDirective(BaseDirective):
    """
    A directive to cancel all open orders for a specific asset
    (useful for live trading).
    """
    directive_type: Literal['cancel_all']
    asset: str


# --- Discriminated Union ---
# This type allows a variable to be one of the specified directive types.
# The 'directive_type' field is used by Pydantic to automatically determine
# which model to use for validation.
ExecutionDirective = Union[
    SingleTradeDirective,
    CancelAllDirective
]
