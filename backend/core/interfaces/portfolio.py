# backend/core/interfaces/portfolio.py
# pylint: disable=unnecessary-ellipsis
"""
Contains the abstract contract (Protocol) for any component that can manage
and execute trades within the S1mpleTrader ecosystem.

@layer: Backend (Core Interfaces)
"""
from __future__ import annotations
from typing import Protocol, List, Dict, Any, runtime_checkable, TYPE_CHECKING
from uuid import UUID
import pandas as pd

# CORRECTIE: Importeer DTOs alleen binnen een TYPE_CHECKING block
if TYPE_CHECKING:
    from backend.dtos.execution_directive import ExecutionDirective
    from backend.dtos.closed_trade import ClosedTrade

@runtime_checkable
class Tradable(Protocol):
    """
    An interface for any object that can manage a financial state, open
    positions, and a history of closed trades. This contract ensures that
    high-level components like an ExecutionHandler can interact with any
    portfolio implementation in a consistent way.
    """

    @property
    def initial_capital(self) -> float:
        """The starting capital of the portfolio."""
        ...

    @property
    def balance(self) -> float:
        """The current, real-time balance of the portfolio."""
        ...

    @property
    def active_trades(self) -> Dict[UUID, Dict[str, Any]]:
        """A dictionary of all currently open trades."""
        ...

    @property
    def closed_trades(self) -> List["ClosedTrade"]:
        """A list of all closed trades."""
        ...

    def open_trade(self, execution_directive: "ExecutionDirective") -> None:
        """
        Receives a complete trade plan and processes it to open a new
        position, updating the internal state.
        """
        ...

    def process_candle(self, candle: pd.Series) -> None:
        """
        Processes the latest market data candle to check if any active
        trades should be closed based on their SL/TP levels.
        """
        ...
