# plugins/portfolio_monitors/max_drawdown_detector/tests/test_worker.py
"""
Unit tests for the MaxDrawdownDetector PortfolioMonitor plugin.

@layer: Plugin
@dependencies: [pytest, pandas, backend.dtos]
@responsibilities:
    - Tests that the PortfolioMonitor correctly detects drawdown breaches
    - Validates CriticalEvent generation
    - Ensures proper state tracking and reset behavior
"""

import time
from unittest.mock import MagicMock
import pandas as pd

from ..worker import MaxDrawdownDetector, DrawdownState
from ..schema import MaxDrawdownDetectorParams
from backend.dtos.execution.critical_event import CriticalEvent
from backend.dtos.state.portfolio_state import PortfolioState


class TestMaxDrawdownDetector:
    """Test suite for the MaxDrawdownDetector PortfolioMonitor plugin."""

    def test_initialization_with_default_parameters(self):
        """Test that the plugin initializes correctly with default parameters."""
        # Arrange
        params = MaxDrawdownDetectorParams()
        logger = MagicMock()

        # Act
        detector = MaxDrawdownDetector(
            name="test_detector",
            params=params,
            logger=logger
        )

        # Assert
        assert detector.name == "test_detector"
        assert detector.params.check_interval_seconds == 60
        assert detector.params.enable_notifications is True
        assert detector._portfolio_state is None
        assert detector._last_check_time is None

    def test_portfolio_drawdown_detection_breach(self):
        """Test that portfolio drawdown breaches are correctly detected."""
        # Arrange
        params = MaxDrawdownDetectorParams(
            check_interval_seconds=1,
            portfolio_max_drawdown_pct=10.0
        )
        logger = MagicMock()
        detector = MaxDrawdownDetector(name="test_detector", params=params, logger=logger)

        # Establish initial peak
        portfolio_state_peak = PortfolioState(equity=10000.0, available_cash=10000.0, total_exposure_quote=0.0, open_positions=[], open_orders=[])
        mock_context_peak = MagicMock()
        mock_context_peak.portfolio_state = portfolio_state_peak
        detector.process([], mock_context_peak)

        time.sleep(1)

        # Create mock portfolio state with drawdown breach
        portfolio_state_drawdown = PortfolioState(
            equity=9000.0,
            available_cash=9000.0,
            total_exposure_quote=0.0,
            open_positions=[],
            open_orders=[]
        )

        mock_context_drawdown = MagicMock()
        mock_context_drawdown.portfolio_state = portfolio_state_drawdown

        # Act
        events = detector.process([], mock_context_drawdown)

        # Assert
        assert len(events) == 1
        assert isinstance(events[0], CriticalEvent)
        assert events[0].event_type == "MAX_DRAWDOWN_BREACHED"

    def test_portfolio_drawdown_no_breach(self):
        """Test that no events are generated when drawdown is within limits."""
        # Arrange
        params = MaxDrawdownDetectorParams(
            check_interval_seconds=1,
            portfolio_max_drawdown_pct=15.0
        )
        logger = MagicMock()
        detector = MaxDrawdownDetector(name="test_detector", params=params, logger=logger)

        # Establish initial peak
        portfolio_state_peak = PortfolioState(equity=10000.0, available_cash=10000.0, total_exposure_quote=0.0, open_positions=[], open_orders=[])
        mock_context_peak = MagicMock()
        mock_context_peak.portfolio_state = portfolio_state_peak
        detector.process([], mock_context_peak)

        time.sleep(1)

        # Create portfolio state with acceptable drawdown
        portfolio_state_drawdown = PortfolioState(
            equity=9000.0,
            available_cash=9000.0,
            total_exposure_quote=0.0,
            open_positions=[],
            open_orders=[]
        )

        mock_context_drawdown = MagicMock()
        mock_context_drawdown.portfolio_state = portfolio_state_drawdown

        # Act
        events = detector.process([], mock_context_drawdown)

        # Assert
        assert len(events) == 0

    def test_minimum_check_interval_enforced(self):
        """Test that the minimum check interval is properly enforced."""
        # Arrange
        params = MaxDrawdownDetectorParams(check_interval_seconds=2, portfolio_max_drawdown_pct=20.0)
        logger = MagicMock()
        detector = MaxDrawdownDetector(name="test_detector", params=params, logger=logger)

        # Establish peak and first check time
        portfolio_state_peak = PortfolioState(equity=10000.0, available_cash=10000.0, total_exposure_quote=0.0, open_positions=[], open_orders=[])
        mock_context_peak = MagicMock()
        mock_context_peak.portfolio_state = portfolio_state_peak
        detector.process([], mock_context_peak)

        # Drawdown state that should trigger event
        portfolio_state_drawdown = PortfolioState(equity=5000.0, available_cash=5000.0, total_exposure_quote=0.0, open_positions=[], open_orders=[])
        mock_context_drawdown = MagicMock()
        mock_context_drawdown.portfolio_state = portfolio_state_drawdown

        # Act
        time.sleep(1)
        events1 = detector.process([], mock_context_drawdown) # Should not trigger, too soon
        time.sleep(2)
        events2 = detector.process([], mock_context_drawdown) # Should trigger

        # Assert
        assert len(events1) == 0
        assert len(events2) == 1

    def test_monitoring_status_report(self):
        """Test that the monitoring status is correctly reported."""
        # Arrange
        params = MaxDrawdownDetectorParams()
        logger = MagicMock()
        detector = MaxDrawdownDetector(name="test_detector", params=params, logger=logger)

        # Act
        status = detector.get_monitoring_status()

        # Assert
        assert status["plugin_name"] == "test_detector"
        assert status["check_interval_seconds"] == 60

    def test_peak_value_updates_correctly(self):
        """Test that peak values are updated when equity increases."""
        # Arrange
        params = MaxDrawdownDetectorParams(check_interval_seconds=1)
        logger = MagicMock()
        detector = MaxDrawdownDetector(name="test_detector", params=params, logger=logger)

        # First, establish a peak
        portfolio_state1 = PortfolioState(equity=10000.0, available_cash=10000.0, total_exposure_quote=0.0, open_positions=[], open_orders=[])
        mock_context1 = MagicMock()
        mock_context1.portfolio_state = portfolio_state1
        detector.process([], mock_context1)

        time.sleep(1)

        # Now test with higher equity
        portfolio_state2 = PortfolioState(equity=11000.0, available_cash=11000.0, total_exposure_quote=0.0, open_positions=[], open_orders=[])
        mock_context2 = MagicMock()
        mock_context2.portfolio_state = portfolio_state2
        detector.process([], mock_context2)

        # Assert
        status = detector.get_monitoring_status()
        assert status["portfolio_state"]["peak_value"] == 11000.0