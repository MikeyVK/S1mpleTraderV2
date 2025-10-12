# backend/config/schemas/portfolio_schema.py
"""
Contains Pydantic models that define the structure of the portfolio.yaml file.

This schema implements the layered risk management architecture, providing
comprehensive configuration for portfolio-wide and strategy-specific risk rules,
along with dynamic event-driven risk responses.

@layer: Backend (Config/Schemas)
@dependencies: [pydantic, typing]
@responsibilities:
    - Defines the complete portfolio configuration structure
    - Implements layered risk management policies
    - Provides dynamic event response configuration
    - Validates strategy links and risk parameters
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# === CAPITAL ALLOCATION CONFIGURATION ===

class CapitalAllocationConfig(BaseModel):
    """
    Defines flexible capital allocation options for a strategy.

    The PortfolioSupervisor will always apply the most restrictive limit
    between percentage and absolute amount.
    """
    percentage: float = Field(
        ...,
        gt=0,
        le=100,
        description="portfolio_schema.capital_allocation.percentage.desc"
    )
    max_quote_amount: Optional[float] = Field(
        None,
        gt=0,
        description="portfolio_schema.capital_allocation.max_quote_amount.desc"
    )


# === EVENT ACTION CONFIGURATION ===

class EventAction(BaseModel):
    """
    Defines the "toolbox" of operational actions available to the PortfolioSupervisor.

    This model provides hard-coded emergency response capabilities that can be
    triggered by CriticalEvents from PortfolioMonitor plugins.
    """

    # --- STRATEGY-LEVEL CONTROLS ---
    block_new_signals_min: Optional[int] = Field(
        default=None,
        ge=0,
        description="portfolio_schema.event_action.block_new_signals_min.desc"
    )

    # --- POSITION CONTROLS (STRATEGY-LEVEL) ---
    close_strategy_positions: Optional[bool] = Field(
        default=None,
        description="portfolio_schema.event_action.close_strategy_positions.desc"
    )
    move_sl_to_breakeven_strategy: Optional[bool] = Field(
        default=None,
        description="portfolio_schema.event_action.move_sl_to_breakeven_strategy.desc"
    )
    reduce_position_size_pct_strategy: Optional[float] = Field(
        default=None,
        gt=0,
        le=100,
        description="portfolio_schema.event_action.reduce_position_size_pct_strategy.desc"
    )

    # --- ORDER CONTROLS (STRATEGY-LEVEL) ---
    cancel_entry_orders_strategy: Optional[bool] = Field(
        default=None,
        description="portfolio_schema.event_action.cancel_entry_orders_strategy.desc"
    )

    # --- PORTFOLIO-LEVEL CONTROLS ---
    close_all_portfolio_positions: Optional[bool] = Field(
        default=None,
        description="portfolio_schema.event_action.close_all_portfolio_positions.desc"
    )
    cancel_all_entry_orders_portfolio: Optional[bool] = Field(
        default=None,
        description="portfolio_schema.event_action.cancel_all_entry_orders_portfolio.desc"
    )

    # --- NOTIFICATIONS ---
    notification_message: Optional[str] = Field(
        default=None,
        description="portfolio_schema.event_action.notification_message.desc"
    )


# === RISK POLICY CONFIGURATION ===

class PortfolioRiskConfig(BaseModel):
    """Defines portfolio-wide risk management rules."""

    max_total_drawdown_pct: float = Field(
        ...,
        gt=0,
        le=100,
        description="portfolio_schema.portfolio_risk.max_total_drawdown_pct.desc"
    )
    max_position_size_pct_per_strategy: float = Field(
        ...,
        gt=0,
        le=100,
        description="portfolio_schema.portfolio_risk.max_position_size_pct_per_strategy.desc"
    )
    max_correlated_positions: int = Field(
        ...,
        ge=1,
        description="portfolio_schema.portfolio_risk.max_correlated_positions.desc"
    )


class StrategyRiskConfig(BaseModel):
    """Defines strategy-specific risk management rules."""

    capital_allocation: CapitalAllocationConfig = Field(
        ...,
        description="portfolio_schema.strategy_risk.capital_allocation.desc"
    )
    max_drawdown_pct: float = Field(
        ...,
        gt=0,
        le=100,
        description="portfolio_schema.strategy_risk.max_drawdown_pct.desc"
    )
    max_position_size_pct: float = Field(
        ...,
        gt=0,
        le=100,
        description="portfolio_schema.strategy_risk.max_position_size_pct.desc"
    )
    enabled: bool = Field(
        default=True,
        description="portfolio_schema.strategy_risk.enabled.desc"
    )


class RiskPolicy(BaseModel):
    """
    Central data structure that bundles all risk management rules.

    This is the heart of the layered risk management system, providing
    a single, comprehensive, and passable object containing all risk policies.
    """

    portfolio_rules: PortfolioRiskConfig = Field(
        ...,
        description="portfolio_schema.risk_policy.portfolio_rules.desc"
    )
    strategy_rules: Dict[str, StrategyRiskConfig] = Field(
        ...,
        description="portfolio_schema.risk_policy.strategy_rules.desc"
    )
    event_responses: Dict[str, EventAction] = Field(
        default_factory=dict,
        description="portfolio_schema.risk_policy.event_responses.desc"
    )


# === STRATEGY LINK CONFIGURATION ===

class StrategyLink(BaseModel):
    """Defines a link between a strategy blueprint and its execution environment."""

    strategy_blueprint_path: str = Field(
        ...,
        description="portfolio_schema.strategy_link.strategy_blueprint_path.desc"
    )
    execution_environment_id: str = Field(
        ...,
        description="portfolio_schema.strategy_link.execution_environment_id.desc"
    )


# === MAIN PORTFOLIO BLUEPRINT ===

class PortfolioBlueprint(BaseModel):
    """
    The main Pydantic model that validates the complete portfolio.yaml file.

    This model implements the complete layered risk management architecture,
    integrating portfolio-wide rules, strategy-specific configurations, and
    dynamic event-driven risk responses.
    """

    display_name: str = Field(
        ...,
        description="portfolio_schema.portfolio_blueprint.display_name.desc"
    )
    description: str = Field(
        ...,
        description="portfolio_schema.portfolio_blueprint.description.desc"
    )
    strategies: List[StrategyLink] = Field(
        ...,
        description="portfolio_schema.portfolio_blueprint.strategies.desc"
    )
    risk_policy: RiskPolicy = Field(
        ...,
        description="portfolio_schema.portfolio_blueprint.risk_policy.desc"
    )
