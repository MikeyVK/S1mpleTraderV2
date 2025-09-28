# tests/backend/environments/test_backtest_environment.py
"""Unit tests for the BacktestEnvironment."""

import pandas as pd
from pytest_mock import MockerFixture

from backend.environments.backtest_environment import (
    BacktestEnvironment,
    CSVDataSource,
    SimulatedClock,
    BacktestExecutionHandler
)
from backend.core.interfaces import Tradable
from backend.config.schemas.app_schema import AppConfig

def test_backtest_environment_initialization(mocker: MockerFixture):
    """
    Tests if the BacktestEnvironment correctly initializes its
    specialized sub-components.
    """
    # Arrange (De Voorbereiding)
    # 1. Maak een nep-DataFrame, want de DataSource heeft dit nodig.
    mock_df = pd.DataFrame({'close': [1, 2, 3]})

    # 2. Instrueer de mocker om de echte DataLoader te vervangen.
    mocker.patch(
        "backend.environments.backtest_environment.DataLoader.load",
        return_value=mock_df
    )
    mocker.patch("backend.data.loader.DataLoader.__init__", return_value=None)

    # 3. Maak een gedetailleerde nep-configuratie.
    mock_app_config = mocker.MagicMock(spec=AppConfig)
    
    # --- DE CRUCIALE CORRECTIE ---
    # a. Maak eerst een "nep-gereedschapskist" (een lege mock voor het .data attribuut)
    mock_data_object = mocker.MagicMock()
    # b. GEEF de aannemer zijn gereedschapskist
    mock_app_config.data = mock_data_object
    # c. NU kunnen we de aannemer opdrachten geven over het gereedschap
    mock_app_config.data.source_dir = "mock_data_dir"
    mock_app_config.data.trading_pair = "BTC/EUR"
    mock_app_config.data.timeframe = "1h"

    # 4. Maak een nep-portfolio.
    mock_portfolio = mocker.MagicMock(spec=Tradable)

    # Act (De Actie)
    environment = BacktestEnvironment(
        app_config=mock_app_config,
        tradable=mock_portfolio
    )

    # Assert (De Controle)
    assert isinstance(environment.source, CSVDataSource)
    assert isinstance(environment.clock, SimulatedClock)
    assert isinstance(environment.handler, BacktestExecutionHandler)
