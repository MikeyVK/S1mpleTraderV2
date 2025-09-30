# tests/backend/environments/test_backtest_environment.py
"""Unit tests for the BacktestEnvironment."""

import pandas as pd
from pytest_mock import MockerFixture

from backend.environments.backtest_environment import (
    BacktestEnvironment, CSVDataSource, SimulatedClock, BacktestExecutionHandler
)
from backend.core.interfaces import Tradable
from backend.config.schemas.app_schema import AppConfig
from backend.config.schemas.platform_schema import PlatformConfig, PlatformDataConfig
from backend.config.schemas.run_schema import RunBlueprint, RunDataConfig

def test_backtest_environment_initialization(mocker: MockerFixture):
    """
    Tests if the BacktestEnvironment correctly initializes its
    specialized sub-components.
    """
    # Arrange
    mock_df = pd.DataFrame({'close': [1, 2, 3]})
    mocker.patch("backend.data.loader.DataLoader.load", return_value=mock_df)
    mocker.patch("backend.data.loader.DataLoader.__init__", return_value=None)

    # --- DE FIX: Bouw een correcte, geneste mock AppConfig ---
    mock_app_config = mocker.MagicMock(spec=AppConfig)
    mock_app_config.platform = mocker.MagicMock(spec=PlatformConfig)
    mock_app_config.run = mocker.MagicMock(spec=RunBlueprint)

    # Definieer de geneste data-objecten
    mock_app_config.platform.data = mocker.MagicMock(spec=PlatformDataConfig)
    mock_app_config.run.data = mocker.MagicMock(spec=RunDataConfig)

    # Wijs de waarden toe op de juiste, geneste locatie
    mock_app_config.platform.data.source_dir = "mock_data_dir"
    mock_app_config.run.data.trading_pair = "BTC/EUR"
    mock_app_config.run.data.timeframe = "1h"

    mock_portfolio = mocker.MagicMock(spec=Tradable)

    # Act
    environment = BacktestEnvironment(
        app_config=mock_app_config,
        tradable=mock_portfolio
    )

    # Assert
    assert isinstance(environment.source, CSVDataSource)
    assert isinstance(environment.clock, SimulatedClock)
    assert isinstance(environment.handler, BacktestExecutionHandler)
