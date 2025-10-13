# tests/backend/core/test_enums.py
"""
Comprehensive unit tests for the backend/core/enums.py module.

@layer: Tests (Backend/Core)
@dependencies: [pytest]
@responsibilities:
    - Verify all enum values are correctly defined
    - Test enum string representations
    - Validate enum membership checks
    - Ensure enum immutability
"""
import pytest

from backend.core.enums import (
    LogLevel,
    WorkerType,
    ContextPhase,
    AnalysisPhase,
    EnvironmentType
)


# === LogLevel Tests ===

def test_log_level_standard_values():
    """Test that all standard log levels are defined correctly."""
    assert LogLevel.DEBUG == "DEBUG"
    assert LogLevel.INFO == "INFO"
    assert LogLevel.WARNING == "WARNING"
    assert LogLevel.ERROR == "ERROR"
    assert LogLevel.CRITICAL == "CRITICAL"


def test_log_level_custom_values():
    """Test that all custom log levels are defined correctly."""
    assert LogLevel.SETUP == "SETUP"
    assert LogLevel.MATCH == "MATCH"
    assert LogLevel.FILTER == "FILTER"
    assert LogLevel.POLICY == "POLICY"
    assert LogLevel.RESULT == "RESULT"
    assert LogLevel.TRADE == "TRADE"


def test_log_level_membership():
    """Test that log level membership checks work correctly."""
    assert "DEBUG" in [level.value for level in LogLevel]
    assert "TRADE" in [level.value for level in LogLevel]
    assert "INVALID" not in [level.value for level in LogLevel]


# === WorkerType Tests ===

def test_worker_type_all_categories():
    """Test that all four worker categories are defined correctly."""
    assert WorkerType.CONTEXT_WORKER == "context_worker"
    assert WorkerType.ANALYSIS_WORKER == "analysis_worker"
    assert WorkerType.MONITOR_WORKER == "monitor_worker"
    assert WorkerType.EXECUTION_WORKER == "execution_worker"


def test_worker_type_count():
    """Test that exactly 4 worker types exist."""
    assert len(list(WorkerType)) == 4


def test_worker_type_membership():
    """Test worker type membership checks."""
    assert "context_worker" in [wt.value for wt in WorkerType]
    assert "analysis_worker" in [wt.value for wt in WorkerType]
    assert "invalid_worker" not in [wt.value for wt in WorkerType]


# === ContextPhase Tests ===

def test_context_phase_all_phases():
    """Test that all context phases are defined correctly."""
    assert ContextPhase.REGIME_CONTEXT == "regime_context"
    assert ContextPhase.STRUCTURAL_CONTEXT == "structural_context"


def test_context_phase_count():
    """Test that exactly 2 context phases exist."""
    assert len(list(ContextPhase)) == 2


# === AnalysisPhase Tests ===

def test_analysis_phase_all_phases():
    """Test that all analysis phases are defined correctly."""
    assert AnalysisPhase.SIGNAL_GENERATION == "signal_generation"
    assert AnalysisPhase.SIGNAL_REFINEMENT == "signal_refinement"
    assert AnalysisPhase.ENTRY_PLANNING == "entry_planning"
    assert AnalysisPhase.EXIT_PLANNING == "exit_planning"
    assert AnalysisPhase.SIZE_PLANNING == "size_planning"
    assert AnalysisPhase.ORDER_ROUTING == "order_routing"


def test_analysis_phase_count():
    """Test that exactly 6 analysis phases exist."""
    assert len(list(AnalysisPhase)) == 6


def test_analysis_phase_order():
    """Test that analysis phases are in the correct sequential order."""
    phases = list(AnalysisPhase)
    assert phases[0] == AnalysisPhase.SIGNAL_GENERATION
    assert phases[1] == AnalysisPhase.SIGNAL_REFINEMENT
    assert phases[2] == AnalysisPhase.ENTRY_PLANNING
    assert phases[3] == AnalysisPhase.EXIT_PLANNING
    assert phases[4] == AnalysisPhase.SIZE_PLANNING
    assert phases[5] == AnalysisPhase.ORDER_ROUTING


# === EnvironmentType Tests ===

def test_environment_type_all_types():
    """Test that all environment types are defined correctly."""
    assert EnvironmentType.BACKTEST == "backtest"
    assert EnvironmentType.PAPER == "paper"
    assert EnvironmentType.LIVE == "live"


def test_environment_type_count():
    """Test that exactly 3 environment types exist."""
    assert len(list(EnvironmentType)) == 3


def test_environment_type_membership():
    """Test environment type membership checks."""
    assert "backtest" in [et.value for et in EnvironmentType]
    assert "live" in [et.value for et in EnvironmentType]
    assert "simulation" not in [et.value for et in EnvironmentType]


# === Cross-Enum Tests ===

def test_enum_string_representation():
    """Test that enum values can be used as strings."""
    worker_type = WorkerType.CONTEXT_WORKER
    assert worker_type.value == "context_worker"
    assert str(worker_type.value) == "context_worker"


def test_enum_comparison():
    """Test that enum values can be compared."""
    assert WorkerType.CONTEXT_WORKER == WorkerType.CONTEXT_WORKER
    assert WorkerType.CONTEXT_WORKER != WorkerType.ANALYSIS_WORKER


def test_enum_immutability():
    """Test that enum values cannot be modified."""
    with pytest.raises(AttributeError):
        WorkerType.CONTEXT_WORKER = "modified_value"
