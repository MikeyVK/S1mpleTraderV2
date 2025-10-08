# backend/dtos/__init__.py
"""
Exposes the public API of the DTOs sub-package.

This file centralizes all DTO imports, allowing other parts of the
application to import any DTO directly from `backend.dtos` without
needing to know the specific internal file structure.

@layer: Backend (DTO)
"""
__all__ = [
    # commands
    "FetchPeriodCommand",
    "FillGapsCommand",
    "ExtendHistoryCommand",
    "SynchronizationCommand",
    # queries
    "PairsQuery",
    "CoverageQuery",
    "RangeQuery",
    # pipeline
    "Signal",
    "EntrySignal",
    "RiskDefinedSignal",
    "TradePlan",
    "RoutedTradePlan",
    # execution
    "CriticalEvent",
    "ExecutionDirective",
    # market
    "TradeTick",
    "DataCoverage",
    # state
    "PortfolioState",
    "TradingContext",
    # results
    "EngineCycleResult",
    "ClosedTrade",
    "BacktestResult",
]

from .commands import *
from .queries import *
from .pipeline import *
from .execution import *
from .market import *
from .state import *
from .results import *
