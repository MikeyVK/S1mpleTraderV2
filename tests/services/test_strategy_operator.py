# tests/services/test_strategy_operator.py
"""
Unit tests for the refactored StrategyOperator service.
"""
from pytest_mock import MockerFixture

# De klasse die we gaan testen
from services.strategy_operator import StrategyOperator

# De klassen die we gaan mocken
from backend.config.schemas.app_schema import AppConfig

def test_strategy_operator_run_orchestration(mocker: MockerFixture):
    """
    Tests if the main `run` method correctly calls the private helper
    methods in the correct order, confirming its role as a pure orchestrator.
    """
    # --- Arrange ---
    # Mock the private helper methods that contain the actual logic
    mock_prepare_components = mocker.patch(
        'services.strategy_operator.StrategyOperator._prepare_components'
    )
    mock_prepare_data = mocker.patch('services.strategy_operator.StrategyOperator._prepare_data')
    mock_run_cycle = mocker.patch(
        'services.strategy_operator.StrategyOperator._run_operational_cycle'
    )

    # Create dummy config and logger for instantiation
    mock_app_config = mocker.MagicMock(spec=AppConfig)
    mock_logger = mocker.MagicMock()

    # --- Act ---
    operator = StrategyOperator(app_config=mock_app_config, logger=mock_logger)
    operator.run()

    # --- Assert ---
    # Verify that the main orchestration methods were called exactly once
    mock_prepare_components.assert_called_once()
    mock_prepare_data.assert_called_once()
    mock_run_cycle.assert_called_once()
