# backend/core/interfaces/engine.py
"""
Contains the behavioral contracts (ABCs) for the core strategy execution engine.

@layer: Backend (Core Interfaces)
@dependencies: [abc, typing, backend.dtos]
@responsibilities:
    - Defines the abstract contract for any component that can execute the
      signal-driven portion of a strategy.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.core.interfaces import Clock
    from backend.dtos import TradingContext, EngineCycleResult

class BaseStrategyEngine(ABC):
    """
    Abstract contract for a Strategy Engine.

    This interface defines the "motor" that drives the core trading logic.
    It is designed to be a pure, high-performance generator of TradePlans,
    completely decoupled from the environment in which it operates.
    """
    def __init__(self, active_workers: Dict[str, Any]):
        """Initializes the engine with its pre-built "toolbox" of workers."""
        ...

    @abstractmethod
    def run(self,
            trading_context: 'TradingContext',
            clock: 'Clock') -> Generator['EngineCycleResult', None, None]:
        """
        Starts the main event loop and yields approved TradePlans.

        Args:
            trading_context (TradingContext): The shared context object.
            clock (Clock): The clock that controls the flow of time.

        Yields:
            TradePlan: A fully validated and approved trade plan, ready for execution.
        """
        ...
