# plugins/portfolio_monitors/max_drawdown_detector/schema.py
"""
Configuration schema for the MaxDrawdownDetector PortfolioMonitor plugin.

@layer: Plugin
@dependencies: [pydantic]
@responsibilities:
    - Defines configuration parameters for drawdown monitoring
    - Validates monitoring thresholds and intervals
"""

from typing import Optional
from pydantic import BaseModel, Field


class MaxDrawdownDetectorParams(BaseModel):
    """
    Configuration parameters for the Maximum Drawdown Detector.

    This plugin monitors portfolio and strategy performance for drawdown
    breaches and triggers appropriate risk responses.
    """

    # Monitoring intervals
    check_interval_seconds: int = Field(
        default=60,
        gt=0,
        description="How often to check for drawdown breaches (seconds)"
    )

    # Portfolio-level monitoring (optional - use RiskPolicy if not specified)
    portfolio_max_drawdown_pct: Optional[float] = Field(
        default=None,
        gt=0,
        le=100,
        description="Portfolio-wide maximum drawdown threshold (overrides RiskPolicy if set)"
    )

    # Strategy-level monitoring (optional - use RiskPolicy if not specified)
    strategy_max_drawdown_pct: Optional[float] = Field(
        default=None,
        gt=0,
        le=100,
        description="Strategy-specific maximum drawdown threshold (overrides RiskPolicy if set)"
    )

    # Notification settings
    enable_notifications: bool = Field(
        default=True,
        description="Whether to send notifications when events are triggered"
    )

    # Recovery settings
    auto_reset_after_minutes: int = Field(
        default=1440,  # 24 hours
        gt=0,
        description="Minutes after which blocked strategies are automatically re-enabled"
    )
