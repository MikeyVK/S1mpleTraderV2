# plugins/portfolio_monitors/max_drawdown_detector/worker.py
"""
PortfolioMonitor plugin that monitors portfolio and strategy drawdown levels.

This plugin runs parallel to the StrategyEngine and monitors the portfolio
state for drawdown breaches, triggering CriticalEvents as needed.

@layer: Plugin
@dependencies: [backend.core.interfaces, backend.dtos, backend.utils.app_logger]
@responsibilities:
    - Monitors portfolio and strategy performance continuously
    - Detects drawdown breaches against configured thresholds
    - Produces CriticalEvents for the PortfolioSupervisor to handle
    - Integrates with the layered risk management system
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from uuid import uuid4

import pandas as pd
from backend.core.interfaces.worker import CriticalEventDetector
from backend.dtos.execution.critical_event import CriticalEvent
from backend.dtos.state.portfolio_state import PortfolioState
from backend.utils.app_logger import LogEnricher

from .schema import MaxDrawdownDetectorParams


@dataclass
class DrawdownState:
    """Tracks drawdown state for a portfolio or strategy."""

    peak_value: float
    current_value: float
    max_drawdown_pct: float
    last_check_time: pd.Timestamp
    is_breached: bool
    breach_time: Optional[pd.Timestamp] = None


class MaxDrawdownDetector(CriticalEventDetector):
    """
    Monitors portfolio and strategy drawdown levels and triggers emergency responses.

    This PortfolioMonitor plugin operates independently of the StrategyEngine,
    continuously monitoring portfolio state and producing CriticalEvents when
    risk thresholds are breached.
    """

    def __init__(
        self,
        name: str,
        params: MaxDrawdownDetectorParams,
        logger: LogEnricher
    ):
        """Initialize the MaxDrawdownDetector PortfolioMonitor."""
        self.name = name
        self.params = params
        self.logger = logger

        # State tracking for drawdown monitoring
        self._portfolio_state: Optional[DrawdownState] = None
        self._strategy_states: Dict[str, DrawdownState] = {}
        self._last_check_time: Optional[pd.Timestamp] = None

        self.logger.info(
            "Initialized MaxDrawdownDetector with check interval: %s seconds",
            self.params.check_interval_seconds
        )

    def process(
        self,
        routed_trade_plans: List[Any],  # Not used by PortfolioMonitor
        context: Any  # TradingContext - used to access portfolio state
    ) -> List[CriticalEvent]:
        """
        Monitor portfolio state for drawdown breaches.

        This method is called regularly by the PortfolioSupervisor to check
        for risk threshold breaches and return any CriticalEvents that need
        to be handled according to the RiskPolicy.

        Args:
            routed_trade_plans: Not used by PortfolioMonitor plugins
            context: TradingContext containing current portfolio state

        Returns:
            List of CriticalEvents that require immediate attention
        """
        current_time = pd.Timestamp.utcnow()

        # Implement minimum check interval to avoid excessive monitoring
        if (
            self._last_check_time and
            (current_time - self._last_check_time).total_seconds() < self.params.check_interval_seconds
        ):
            return []  # Too soon to check again

        self._last_check_time = current_time
        events_detected = []

        try:
            # Get current portfolio state from context
            portfolio_state = context.portfolio_state

            # Check portfolio-level drawdown
            portfolio_events = self._check_portfolio_drawdown(portfolio_state, current_time)
            events_detected.extend(portfolio_events)

            # Check strategy-level drawdown
            strategy_events = self._check_strategy_drawdowns(portfolio_state, current_time)
            events_detected.extend(strategy_events)

        except Exception as e:
            self.logger.error(
                "Error during drawdown monitoring: %s",
                str(e),
                exc_info=True
            )

        return events_detected

    def _check_portfolio_drawdown(
        self,
        portfolio_state: PortfolioState,
        current_time: pd.Timestamp
    ) -> List[CriticalEvent]:
        """Check portfolio-level drawdown against thresholds."""
        events = []

        # Initialize or update portfolio peak tracking
        current_equity = portfolio_state.equity

        if self._portfolio_state is None:
            # First time - establish baseline
            self._portfolio_state = DrawdownState(
                peak_value=current_equity,
                current_value=current_equity,
                max_drawdown_pct=self.params.portfolio_max_drawdown_pct or 100.0,
                last_check_time=current_time,
                is_breached=False
            )
        
        # Update peak if current equity is higher
        if current_equity > self._portfolio_state.peak_value:
            self._portfolio_state.peak_value = current_equity
            self._portfolio_state.is_breached = False  # Reset breach state
            self._portfolio_state.breach_time = None

        self._portfolio_state.current_value = current_equity
        self._portfolio_state.last_check_time = current_time

        # Calculate current drawdown
        if self._portfolio_state.peak_value > 0:
            drawdown_pct = (
                (self._portfolio_state.peak_value - current_equity) /
                self._portfolio_state.peak_value * 100
            )

            # Check for breach
            if (
                drawdown_pct >= self._portfolio_state.max_drawdown_pct and
                not self._portfolio_state.is_breached
            ):
                self._portfolio_state.is_breached = True
                self._portfolio_state.breach_time = current_time

                events.append(CriticalEvent(
                    correlation_id=uuid4(),
                    event_type="MAX_DRAWDOWN_BREACHED",
                    timestamp=current_time
                ))

                self.logger.warning(
                    "Portfolio maximum drawdown breached: %.2f%% (threshold: %.2f%%)",
                    drawdown_pct,
                    self._portfolio_state.max_drawdown_pct
                )

        return events

    def _check_strategy_drawdowns(
        self,
        portfolio_state: PortfolioState,
        current_time: pd.Timestamp
    ) -> List[CriticalEvent]:
        """Check strategy-level drawdown against thresholds."""
        events = []

        # This is a simplified implementation
        # In a full implementation, you'd track per-strategy performance
        # For now, we'll implement a basic check based on portfolio composition

        total_equity = portfolio_state.equity

        # Example: Check if any strategy allocation exceeds safe limits
        # This would need to be expanded based on actual strategy tracking

        return events

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Return current monitoring status for debugging and UI display."""
        return {
            "plugin_name": self.name,
            "check_interval_seconds": self.params.check_interval_seconds,
            "portfolio_state": {
                "peak_value": self._portfolio_state.peak_value if self._portfolio_state else None,
                "current_value": self._portfolio_state.current_value if self._portfolio_state else None,
                "is_breached": self._portfolio_state.is_breached if self._portfolio_state else False,
                "breach_time": self._portfolio_state.breach_time if self._portfolio_state else None,
            },
            "strategy_count": len(self._strategy_states),
            "last_check": self._last_check_time,
        }