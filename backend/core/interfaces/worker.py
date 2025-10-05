# backend/core/interfaces/worker.py
# pylint: disable=unnecessary-ellipsis
"""
Contains the behavioral contracts (Protocols) for all plugin worker types.
These interfaces are the "constitution" for the S1mpleTrader plugin
ecosystem, ensuring that any component created by a developer will correctly
integrate with the StrategyEngine.
@layer: Backend (Core Interfaces)
@dependencies: [typing, pandas]
@responsibilities:
    - Defines the structural contracts for all types of plugin workers.
    - Enforces the logical data flow of the 9-fase strategy pipeline.
"""
from __future__ import annotations
from typing import (Any, List, Optional, Protocol, TYPE_CHECKING, runtime_checkable)
import pandas as pd

# Use TYPE_CHECKING to prevent circular imports at runtime
if TYPE_CHECKING:
    from backend.dtos.pipeline.signal import Signal
    from backend.dtos.pipeline.entry_signal import EntrySignal
    from backend.dtos.pipeline.risk_defined_signal import RiskDefinedSignal
    from backend.dtos.pipeline.trade_plan import TradePlan
    from backend.dtos.pipeline.routed_trade_plan import RoutedTradePlan
    from backend.dtos.execution.critical_event import CriticalEvent
    from backend.dtos.state.trading_context import TradingContext

# --- Specific Worker Contracts ---

@runtime_checkable
class ContextWorker(Protocol):
    """A contract for a data enrichment worker (Fase 1 & 2)."""
    def __init__(self, name: str, params: Any, logger: Any):
        """Initializes the worker with its name, params, and logger."""
        ...

    def process(self, df: pd.DataFrame, context: "TradingContext") -> pd.DataFrame:
        """Processes the DataFrame to add context."""
        ...

@runtime_checkable
class StrategyWorker(Protocol):
    """A base contract for any worker operating within the main DTO pipeline."""
    def __init__(self, name: str, params: Any, logger: Any):
        """Initializes the worker with its name, params, and logger."""
        ...

# --- Specific Strategy Worker Contracts (The Pipeline) ---

@runtime_checkable
class SignalGenerator(StrategyWorker, Protocol):
    """Fase 3: A contract for a worker that generates trading opportunities."""
    def process(self, context: "TradingContext") -> List["Signal"]:
        """Generates raw Signal DTOs based on the market context."""
        ...

@runtime_checkable
class SignalRefiner(StrategyWorker, Protocol):
    """Fase 4: A contract for a worker that filters raw signals."""
    def process(
        self, signal: "Signal", context: "TradingContext"
    ) -> Optional["Signal"]:
        """Processes a single signal and returns it if valid, otherwise None."""
        ...

@runtime_checkable
class EntryPlanner(StrategyWorker, Protocol):
    """Fase 5: A contract for a worker that defines the entry tactic."""
    def process(
        self, signal: "Signal", context: "TradingContext"
    ) -> Optional["EntrySignal"]:
        """Enriches a Signal with a concrete entry price."""
        ...

@runtime_checkable
class ExitPlanner(StrategyWorker, Protocol):
    """Fase 6: A contract for a worker that defines risk parameters (SL/TP)."""
    def process(
        self, entry_signal: "EntrySignal", context: "TradingContext"
    ) -> Optional["RiskDefinedSignal"]:
        """Enriches an EntrySignal with stop-loss and take-profit prices."""
        ...

@runtime_checkable
class SizePlanner(StrategyWorker, Protocol):
    """Fase 7: A contract for a worker that calculates position size."""
    def process(
        self, risk_defined_signal: "RiskDefinedSignal", context: "TradingContext"
    ) -> Optional["TradePlan"]:
        """Enriches a RiskDefinedSignal with the final position size."""
        ...

@runtime_checkable
class OrderRouter(StrategyWorker, Protocol):
    """Fase 8: A contract for a worker that translates a TradePlan."""
    def process(
        self, trade_plan: "TradePlan", context: "TradingContext"
    ) -> Optional["RoutedTradePlan"]:
        """Enriches a TradePlan with specific order execution instructions."""
        ...

@runtime_checkable
class CriticalEventDetector(StrategyWorker, Protocol):
    """Fase 9: A contract for a worker that scans for systemic events."""
    def process(
        self, routed_trade_plans: List["RoutedTradePlan"], context: "TradingContext"
    ) -> List["CriticalEvent"]:
        """Detects and returns a list of critical events."""
        ...
