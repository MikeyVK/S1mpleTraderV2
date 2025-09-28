# backend/dtos/__init__.py
"""
Exposes the public API of the DTOs sub-package.

This file centralizes all DTO imports, allowing other parts of the
application to import any DTO directly from `backend.dtos` without
needing to know the specific internal file structure.

@layer: Backend (DTO)
"""
__all__ = [
    "Signal",
    "EntrySignal",
    "RiskDefinedSignal",
    "TradePlan",
    "ClosedTrade",
    "TradingContext",
    "BacktestResult",
]

from .signal import Signal
from .entry_signal import EntrySignal
from .risk_defined_signal import RiskDefinedSignal
from .trade_plan import TradePlan
from .closed_trade import ClosedTrade
from .trading_context import TradingContext
from .backtest_result import BacktestResult
