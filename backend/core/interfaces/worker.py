# backend/core/interfaces/worker.py
"""
Contains the behavioral contracts (Protocols) for all plugin worker types.

@layer: Backend (Core Interfaces)
@dependencies: [typing, pandas, backend.dtos]
@responsibilities:
    - Defines the structural contracts for all types of plugin workers.
"""
from __future__ import annotations

from typing import (Any, List, Optional, Protocol,
                    TYPE_CHECKING)
import pandas as pd

if TYPE_CHECKING:
    from backend.dtos import (Signal, EntrySignal, RiskDefinedSignal,
                              TradePlan, TradingContext)

# --- Base Contract for All Workers ---

class BaseWorkerProtocol(Protocol):
    """The base behavioral contract for any plugin worker."""
    def process(self, *args: Any, **kwargs: Any) -> Any:
        """The main entry point method for the worker's logic."""
        ...

# --- Specific Worker Contracts ---

class ContextWorker(BaseWorkerProtocol):
    """A protocol defining the contract for a data enrichment worker (Fase 1 & 2)."""
    def process(self, df: pd.DataFrame, context: 'TradingContext') -> pd.DataFrame:
        ...

class SignalGenerator(BaseWorkerProtocol):
    """A protocol defining the contract for a signal generation worker (Fase 3)."""
    def process(self, context: 'TradingContext') -> List['Signal']:
        ...

class SignalRefiner(BaseWorkerProtocol):
    """A protocol defining the contract for a signal refinement worker (Fase 4)."""
    def process(self, signal: 'Signal', context: 'TradingContext') -> Optional['Signal']:
        ...

class EntryPlanner(BaseWorkerProtocol):
    """A protocol defining the contract for an entry planning worker (Fase 5a)."""
    def process(self, signal: 'Signal', context: 'TradingContext') -> Optional['EntrySignal']:
        ...

class ExitPlanner(BaseWorkerProtocol):
    """A protocol defining the contract for an exit planning worker (Fase 5b)."""
    def process(self, signal: 'EntrySignal',
                context: 'TradingContext') -> Optional['RiskDefinedSignal']:
        ...

class SizePlanner(BaseWorkerProtocol):
    """A protocol defining the contract for a size planning worker (Fase 5c)."""
    def process(self, signal: 'RiskDefinedSignal',
                context: 'TradingContext') -> Optional['TradePlan']:
        ...

class PortfolioOverlay(BaseWorkerProtocol):
    """A protocol defining the contract for a portfolio overlay worker (Fase 6)."""
    def process(self, trade_plan: 'TradePlan', context: 'TradingContext') -> Optional['TradePlan']:
        ...
