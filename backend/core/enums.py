# backend/core/enums.py
"""
Contains application-wide enumerations to provide type-safety and a single
source of truth for specific sets of values.

@layer: Core
@version: 2.0 (V2 Architecture Aligned)
"""
from enum import Enum

class LogLevel(str, Enum):
    """Defines all valid logging levels, including custom ones."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SETUP = "SETUP"
    MATCH = "MATCH"
    FILTER = "FILTER"
    POLICY = "POLICY"
    RESULT = "RESULT"
    TRADE = "TRADE"

# === V2 ARCHITECTURE: WORKER TYPES (ROLES) ===

class WorkerType(str, Enum):
    """
    The 4 fundamental worker categories in the V2 architecture.
    
    Each represents a distinct functional role in the trading system:
    - CONTEXT_WORKER: Enriches raw market data with analytical context
    - ANALYSIS_WORKER: Generates non-deterministic analytical trade proposals
    - MONITOR_WORKER: Observes state and publishes strategic events
    - EXECUTION_WORKER: Performs deterministic, rule-based actions
    """
    CONTEXT_WORKER = "context_worker"
    ANALYSIS_WORKER = "analysis_worker"
    MONITOR_WORKER = "monitor_worker"
    EXECUTION_WORKER = "execution_worker"

# === V2 ARCHITECTURE: PIPELINE PHASES ===

class ContextPhase(str, Enum):
    """
    Phases within the Context pipeline (managed by ContextOperator).
    
    These phases enrich raw market data with analytical context before
    the analytical pipeline begins.
    """
    REGIME_CONTEXT = "regime_context"
    STRUCTURAL_CONTEXT = "structural_context"

class AnalysisPhase(str, Enum):
    """
    Phases within the Analysis pipeline (managed by AnalysisOperator).
    
    These phases transform enriched context into actionable trade plans
    through a sequential, procedural funnel.
    """
    SIGNAL_GENERATION = "signal_generation"
    SIGNAL_REFINEMENT = "signal_refinement"
    ENTRY_PLANNING = "entry_planning"
    EXIT_PLANNING = "exit_planning"
    SIZE_PLANNING = "size_planning"
    ORDER_ROUTING = "order_routing"

# === EXECUTION ENVIRONMENTS ===

class EnvironmentType(str, Enum):
    """
    The three execution environment types.
    
    Defines the operational "world" in which a strategy can run:
    - BACKTEST: Historical simulation using archived data
    - PAPER: Live market data with simulated execution
    - LIVE: Real trading with actual capital
    """
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"

# === V1 COMPATIBILITY (DEPRECATED) ===

class PipelinePhase(str, Enum):
    """
    DEPRECATED: V1 phase-based pipeline enum.
    
    This enum is kept for backward compatibility with existing code.
    New code should use WorkerType for plugin categorization and
    ContextPhase/AnalysisPhase for pipeline phase specification.
    
    Will be removed in a future version.
    """
    REGIME_FILTER = "regime_filter"
    STRUCTURAL_CONTEXT = "structural_context"
    SIGNAL_GENERATOR = "signal_generator"
    SIGNAL_REFINER = "signal_refiner"
    ENTRY_PLANNER = "entry_planner"
    EXIT_PLANNER = "exit_planner"
    SIZE_PLANNER = "size_planner"
    ORDER_ROUTER = "order_router"
    CRITICAL_EVENT_DETECTOR = "critical_event_detector"
