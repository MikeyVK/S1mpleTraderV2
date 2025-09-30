# backend/core/__init__.py
"""
Exposes the public API of the Core sub-package, making key components
available for other layers of the application, such as the Service layer
and test suites.

This centralization allows for cleaner imports, as consumers can import
directly from `backend.core` without needing to know the internal
file structure.

@layer: Backend (Core)
"""
__all__ = [
    "StrategyEngine",
    "Portfolio",
    "BaseStrategyWorker",
    "ContextRecorder",
    "BacktestExecutionHandler"
]

from .strategy_engine import StrategyEngine
from .portfolio import Portfolio
from .base_worker import BaseStrategyWorker
from .context_recorder import ContextRecorder
from .execution import BacktestExecutionHandler
