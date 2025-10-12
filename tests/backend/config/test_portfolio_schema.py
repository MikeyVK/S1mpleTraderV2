# tests/backend/config/test_portfolio_schema.py
"""
Unit tests for the portfolio_schema.py.

@layer: Tests (Backend/Config/Schemas)
@dependencies: [pytest, pydantic]
@responsibilities:
    - Verify that valid portfolio configurations are successfully parsed
    - Test the layered risk management structure
    - Validate EventAction emergency response configurations
    - Ensure proper default value application
    - Test validation rules for all risk parameters
"""

import pytest
from pydantic import ValidationError

# Import all the portfolio schema models
from backend.config.schemas.portfolio_schema import (
    PortfolioBlueprint,
    RiskPolicy,
    PortfolioRiskConfig,
    StrategyRiskConfig,
    CapitalAllocationConfig,
    EventAction,
    StrategyLink,
)


def test_capital_allocation_config_valid():
    """Test that CapitalAllocationConfig validates correctly with valid data."""
    # Arrange & Act
    config = CapitalAllocationConfig(percentage=50.0, max_quote_amount=25000.0)

    # Assert
    assert config.percentage == 50.0
    assert config.max_quote_amount == 25000.0


def test_capital_allocation_config_defaults():
    """Test that CapitalAllocationConfig applies defaults correctly."""
    # Arrange & Act
    config = CapitalAllocationConfig(percentage=30.0, max_quote_amount=None)

    # Assert
    assert config.percentage == 30.0
    assert config.max_quote_amount is None


def test_capital_allocation_config_validation_errors():
    """Test that CapitalAllocationConfig enforces validation rules."""
    # Test percentage too high
    with pytest.raises(ValidationError):
        CapitalAllocationConfig(percentage=150.0, max_quote_amount=None)  # > 100

    # Test percentage too low
    with pytest.raises(ValidationError):
        CapitalAllocationConfig(percentage=-10.0, max_quote_amount=None)  # < 0

    # Test negative max_quote_amount
    with pytest.raises(ValidationError):
        CapitalAllocationConfig(percentage=50.0, max_quote_amount=-1000.0)


def test_event_action_minimal_configuration():
    """Test EventAction with minimal configuration (all optional fields)."""
    # Arrange & Act
    event_action = EventAction()

    # Assert
    assert event_action.block_new_signals_min is None
    assert event_action.close_strategy_positions is None
    assert event_action.notification_message is None


def test_event_action_validation_rules():
    """Test that EventAction enforces validation rules on numeric fields."""
    # Test negative block time
    with pytest.raises(ValidationError):
        EventAction(block_new_signals_min=-30)

    # Test invalid percentage reduction
    with pytest.raises(ValidationError):
        EventAction(reduce_position_size_pct_strategy=150.0)  # > 100

    with pytest.raises(ValidationError):
        EventAction(reduce_position_size_pct_strategy=-10.0)  # < 0


def test_portfolio_risk_config_valid():
    """Test PortfolioRiskConfig with valid configuration."""
    # Arrange & Act
    risk_config = PortfolioRiskConfig(
        max_total_drawdown_pct=25.0,
        max_position_size_pct_per_strategy=15.0,
        max_correlated_positions=3
    )

    # Assert
    assert risk_config.max_total_drawdown_pct == 25.0
    assert risk_config.max_position_size_pct_per_strategy == 15.0
    assert risk_config.max_correlated_positions == 3


def test_portfolio_risk_config_validation_errors():
    """Test PortfolioRiskConfig validation rule enforcement."""
    # Test drawdown too high
    with pytest.raises(ValidationError):
        PortfolioRiskConfig(
            max_total_drawdown_pct=150.0,  # > 100
            max_position_size_pct_per_strategy=10.0,
            max_correlated_positions=2
        )

    # Test negative position size
    with pytest.raises(ValidationError):
        PortfolioRiskConfig(
            max_total_drawdown_pct=20.0,
            max_position_size_pct_per_strategy=-5.0,  # < 0
            max_correlated_positions=2
        )

    # Test invalid correlated positions
    with pytest.raises(ValidationError):
        PortfolioRiskConfig(
            max_total_drawdown_pct=20.0,
            max_position_size_pct_per_strategy=10.0,
            max_correlated_positions=0  # < 1
        )


def test_strategy_risk_config_valid():
    """Test StrategyRiskConfig with complete valid configuration."""
    # Arrange
    capital_alloc = CapitalAllocationConfig(percentage=40.0, max_quote_amount=20000.0)

    # Act
    risk_config = StrategyRiskConfig(
        capital_allocation=capital_alloc,
        max_drawdown_pct=12.0,
        max_position_size_pct=8.0,
        enabled=True
    )

    # Assert
    assert risk_config.capital_allocation.percentage == 40.0
    assert risk_config.capital_allocation.max_quote_amount == 20000.0
    assert risk_config.max_drawdown_pct == 12.0
    assert risk_config.max_position_size_pct == 8.0
    assert risk_config.enabled is True


def test_strategy_risk_config_defaults():
    """Test StrategyRiskConfig default value application."""
    # Arrange
    capital_alloc = CapitalAllocationConfig(percentage=25.0, max_quote_amount=None)

    # Act
    risk_config = StrategyRiskConfig(
        capital_allocation=capital_alloc,
        max_drawdown_pct=10.0,
        max_position_size_pct=5.0
    )

    # Assert
    assert risk_config.enabled is True  # Should default to True


def test_risk_policy_minimal_configuration():
    """Test RiskPolicy with minimal configuration."""
    # Arrange
    portfolio_rules = PortfolioRiskConfig(
        max_total_drawdown_pct=25.0,
        max_position_size_pct_per_strategy=15.0,
        max_correlated_positions=3
    )

    # Act
    risk_policy = RiskPolicy(
        portfolio_rules=portfolio_rules,
        strategy_rules={},
        event_responses={}
    )

    # Assert
    assert risk_policy.portfolio_rules.max_total_drawdown_pct == 25.0
    assert len(risk_policy.strategy_rules) == 0
    assert len(risk_policy.event_responses) == 0


def test_strategy_link_valid_configuration():
    """Test StrategyLink with valid strategy configuration."""
    # Arrange & Act
    strategy_link = StrategyLink(
        strategy_blueprint_path="runs/mss_fvg_strategy.yaml",
        execution_environment_id="backtest_btc_eur"
    )

    # Assert
    assert strategy_link.strategy_blueprint_path == "runs/mss_fvg_strategy.yaml"
    assert strategy_link.execution_environment_id == "backtest_btc_eur"


def test_portfolio_blueprint_minimal_valid():
    """Test PortfolioBlueprint with minimal required configuration."""
    # Arrange
    strategy_link = StrategyLink(
        strategy_blueprint_path="runs/test_strategy.yaml",
        execution_environment_id="test_env"
    )

    portfolio_rules = PortfolioRiskConfig(
        max_total_drawdown_pct=30.0,
        max_position_size_pct_per_strategy=20.0,
        max_correlated_positions=2
    )

    risk_policy = RiskPolicy(
        portfolio_rules=portfolio_rules,
        strategy_rules={},
        event_responses={}
    )

    # Act
    portfolio = PortfolioBlueprint(
        display_name="Test Portfolio",
        description="Minimal test configuration",
        strategies=[strategy_link],
        risk_policy=risk_policy
    )

    # Assert
    assert portfolio.display_name == "Test Portfolio"
    assert len(portfolio.strategies) == 1
    assert portfolio.strategies[0].strategy_blueprint_path == "runs/test_strategy.yaml"
    assert portfolio.risk_policy.portfolio_rules.max_total_drawdown_pct == 30.0


def test_portfolio_blueprint_validation_missing_required():
    """Test PortfolioBlueprint validation for missing required fields."""
    # Test missing display_name
    with pytest.raises(ValidationError):
        # Missing display_name and other required fields
        PortfolioBlueprint(
            description="Missing display name",
            strategies=[],
            risk_policy={}  # Invalid - missing required fields
        )


def test_portfolio_blueprint_validation_invalid_strategy_config():
    """Test PortfolioBlueprint validation for invalid strategy configuration."""
    # Arrange & Act & Assert
    with pytest.raises(ValidationError):
        # Test invalid percentage in strategy rules
        invalid_capital = CapitalAllocationConfig(percentage=150.0, max_quote_amount=None)  # Invalid - > 100

        invalid_strategy_rules = {
            "test_strategy": StrategyRiskConfig(
                capital_allocation=invalid_capital,
                max_drawdown_pct=10.0,
                max_position_size_pct=5.0
            )
        }

        portfolio_rules = PortfolioRiskConfig(
            max_total_drawdown_pct=25.0,
            max_position_size_pct_per_strategy=15.0,
            max_correlated_positions=3
        )

        RiskPolicy(
            portfolio_rules=portfolio_rules,
            strategy_rules=invalid_strategy_rules,
            event_responses={}
        )


def test_portfolio_blueprint_empty_strategies():
    """Test PortfolioBlueprint with empty strategies list."""
    # Arrange
    portfolio_rules = PortfolioRiskConfig(
        max_total_drawdown_pct=25.0,
        max_position_size_pct_per_strategy=15.0,
        max_correlated_positions=3
    )

    risk_policy = RiskPolicy(
        portfolio_rules=portfolio_rules,
        strategy_rules={},
        event_responses={}
    )

    # Act
    portfolio = PortfolioBlueprint(
        display_name="Empty Portfolio",
        description="Portfolio with no strategies",
        strategies=[],  # Empty strategies list
        risk_policy=risk_policy
    )

    # Assert
    assert portfolio.display_name == "Empty Portfolio"
    assert len(portfolio.strategies) == 0
    assert portfolio.risk_policy.portfolio_rules.max_total_drawdown_pct == 25.0


def test_event_responses_with_emergency_actions():
    """Test event responses with emergency action configuration."""
    # Arrange
    portfolio_rules = PortfolioRiskConfig(
        max_total_drawdown_pct=25.0,
        max_position_size_pct_per_strategy=15.0,
        max_correlated_positions=3
    )

    emergency_action = EventAction(
        block_new_signals_min=1440,
        close_all_portfolio_positions=True,
        cancel_all_entry_orders_portfolio=True,
        notification_message="CRITICAL: Portfolio maximum drawdown exceeded"
    )

    strategy_action = EventAction(
        block_new_signals_min=60,
        reduce_position_size_pct_strategy=50.0,
        move_sl_to_breakeven_strategy=True,
        notification_message="WARNING: Strategy exceeded drawdown limit"
    )

    # Act
    risk_policy = RiskPolicy(
        portfolio_rules=portfolio_rules,
        strategy_rules={},
        event_responses={
            "MAX_DRAWDOWN_BREACHED": emergency_action,
            "STRATEGY_DRAWDOWN_EXCEEDED": strategy_action
        }
    )

    # Assert
    assert len(risk_policy.event_responses) == 2
    assert "MAX_DRAWDOWN_BREACHED" in risk_policy.event_responses
    assert "STRATEGY_DRAWDOWN_EXCEEDED" in risk_policy.event_responses

    # Test emergency actions
    max_dd_event = risk_policy.event_responses["MAX_DRAWDOWN_BREACHED"]
    assert max_dd_event.block_new_signals_min == 1440
    assert max_dd_event.close_all_portfolio_positions is True

    # Test strategy actions
    strategy_dd_event = risk_policy.event_responses["STRATEGY_DRAWDOWN_EXCEEDED"]
    assert strategy_dd_event.reduce_position_size_pct_strategy == 50.0
    assert strategy_dd_event.move_sl_to_breakeven_strategy is True


def test_portfolio_blueprint_real_world_example():
    """Test PortfolioBlueprint with a realistic, complex configuration."""
    # Arrange - Build component objects step by step
    btc_strategy = StrategyLink(
        strategy_blueprint_path="runs/mss_fvg_strategy.yaml",
        execution_environment_id="backtest_btc_eur"
    )

    eth_strategy = StrategyLink(
        strategy_blueprint_path="runs/eth_mean_reversion.yaml",
        execution_environment_id="backtest_eth_eur"
    )

    disabled_strategy = StrategyLink(
        strategy_blueprint_path="runs/multi_timeframe_momentum.yaml",
        execution_environment_id="backtest_multi_asset"
    )

    # Strategy-specific risk rules (single source of truth)
    btc_risk = StrategyRiskConfig(
        capital_allocation=CapitalAllocationConfig(percentage=50.0, max_quote_amount=25000.0),
        max_drawdown_pct=15.0,
        max_position_size_pct=10.0,
        enabled=True
    )

    eth_risk = StrategyRiskConfig(
        capital_allocation=CapitalAllocationConfig(percentage=30.0, max_quote_amount=None),
        max_drawdown_pct=12.0,
        max_position_size_pct=8.0,
        enabled=True
    )

    disabled_risk = StrategyRiskConfig(
        capital_allocation=CapitalAllocationConfig(percentage=20.0, max_quote_amount=10000.0),
        max_drawdown_pct=10.0,
        max_position_size_pct=5.0,
        enabled=False
    )

    portfolio_rules = PortfolioRiskConfig(
        max_total_drawdown_pct=25.0,
        max_position_size_pct_per_strategy=15.0,
        max_correlated_positions=3
    )

    emergency_action = EventAction(
        block_new_signals_min=1440,
        close_all_portfolio_positions=True,
        cancel_all_entry_orders_portfolio=True,
        notification_message="EMERGENCY: Maximum drawdown breached. All positions closed."
    )

    strategy_action = EventAction(
        block_new_signals_min=60,
        reduce_position_size_pct_strategy=50.0,
        move_sl_to_breakeven_strategy=True,
        notification_message="WARNING: Strategy exceeded maximum drawdown."
    )

    risk_policy = RiskPolicy(
        portfolio_rules=portfolio_rules,
        strategy_rules={
            "mss_fvg_strategy": btc_risk,
            "eth_mean_reversion": eth_risk,
            "multi_timeframe_momentum": disabled_risk
        },
        event_responses={
            "MAX_DRAWDOWN_BREACHED": emergency_action,
            "STRATEGY_DRAWDOWN_EXCEEDED": strategy_action
        }
    )

    # Act
    portfolio = PortfolioBlueprint(
        display_name="Main Trading Portfolio",
        description="Primary portfolio for EUR-based crypto trading strategies with comprehensive risk management",
        strategies=[btc_strategy, eth_strategy, disabled_strategy],
        risk_policy=risk_policy
    )

    # Assert basic structure
    assert portfolio.display_name == "Main Trading Portfolio"
    assert len(portfolio.strategies) == 3

    # Assert strategy links (no risk config here - that's in RiskPolicy)
    btc_strategy_found = next(s for s in portfolio.strategies if "btc" in s.execution_environment_id)
    assert btc_strategy_found.strategy_blueprint_path == "runs/mss_fvg_strategy.yaml"
    assert btc_strategy_found.execution_environment_id == "backtest_btc_eur"

    # Assert disabled strategy
    disabled_strategy_found = next(s for s in portfolio.strategies if "multi_timeframe" in s.strategy_blueprint_path)
    assert disabled_strategy_found.strategy_blueprint_path == "runs/multi_timeframe_momentum.yaml"

    # Assert risk policy (single source of truth)
    assert portfolio.risk_policy.portfolio_rules.max_total_drawdown_pct == 25.0
    assert len(portfolio.risk_policy.strategy_rules) == 3
    assert len(portfolio.risk_policy.event_responses) == 2

    # Assert strategy-specific risk rules are in the RiskPolicy
    assert "mss_fvg_strategy" in portfolio.risk_policy.strategy_rules
    btc_risk_from_policy = portfolio.risk_policy.strategy_rules["mss_fvg_strategy"]
    assert btc_risk_from_policy.capital_allocation.percentage == 50.0
    assert btc_risk_from_policy.capital_allocation.max_quote_amount == 25000.0
    assert btc_risk_from_policy.enabled is True

    # Assert disabled strategy risk config is in RiskPolicy
    disabled_risk_from_policy = portfolio.risk_policy.strategy_rules["multi_timeframe_momentum"]
    assert disabled_risk_from_policy.enabled is False

    # Assert event responses
    emergency_response = portfolio.risk_policy.event_responses["MAX_DRAWDOWN_BREACHED"]
    assert emergency_response.block_new_signals_min == 1440
    assert emergency_response.close_all_portfolio_positions is True