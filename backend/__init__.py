# backend/__init__.py
"""
Exposes the public API of the Backend package.
"""
__all__ = [
    # from .core
    "StrategyEngine",
    "Portfolio",
    "BaseStrategyWorker",
    "ContextRecorder",
    # from .dtos
    "Signal",
    "EntrySignal",
    "RiskDefinedSignal",
    "TradePlan",
    "RoutedTradePlan",
    "CriticalEvent",
    "ExecutionDirective",
    "EngineCycleResult",
    "ClosedTrade",
    "TradingContext",
    "BacktestResult",
    "DataCoverage",
    "TradeTick",
    "DataSyncRequest",
    "HistoryBuildRequest",
    # from .core
    # from .environments
    "BacktestEnvironment",
#    "LiveEnvironment",
#    "PaperEnvironment",
    # from .assembly
    "ContextBuilder",
    "DependencyValidator",
    "PluginRegistry",
    "WorkerBuilder",
]

from .core import (
    StrategyEngine,
    Portfolio,
    BaseStrategyWorker,
    ContextRecorder,
)
from .dtos import (
    Signal,
    EntrySignal,
    RiskDefinedSignal,
    TradePlan,
    RoutedTradePlan,
    CriticalEvent,
    ExecutionDirective,
    EngineCycleResult,
    ClosedTrade,
    TradingContext,
    BacktestResult,
    DataCoverage,
    TradeTick,
    DataSyncRequest,
    HistoryBuildRequest,
)
from .environments import (
    BacktestEnvironment,
#    LiveEnvironment,
#    PaperEnvironment,
)
from .assembly import (
    ContextBuilder,
    DependencyValidator,
    PluginRegistry,
    WorkerBuilder,
)
