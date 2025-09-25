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
