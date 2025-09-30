# backend/core/enums.py
"""
Contains application-wide enumerations to provide type-safety and a single
source of truth for specific sets of values.

@layer: Core
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

class PipelinePhase(str, Enum):
    """Defines the valid phases of the 6-phase strategy funnel."""
    REGIME_FILTER = "regime_filter"
    STRUCTURAL_CONTEXT = "structural_context"
    SIGNAL_GENERATOR = "signal_generator"
    SIGNAL_REFINER = "signal_refiner"
    ENTRY_PLANNER = "entry_planner"
    EXIT_PLANNER = "exit_planner"
    SIZE_PLANNER = "size_planner"
    ORDER_ROUTER = "order_router"
    CRITICAL_EVENT_DETECTOR = "critical_event_detector"
