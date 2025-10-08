# tests/backend/environments/api_connectors/test_kraken_connector.py
"""
Unit tests for the KrakenAPIConnector.

@layer: Tests (Backend/Environments/APIConnectors)
@dependencies: [pytest, pytest-mock, requests]
@responsibilities:
    - Verify that the connector correctly calls the Kraken API endpoints.
    - Verify that the connector correctly parses valid API responses into DTOs.
    - Verify that the connector handles API errors and invalid data gracefully.
"""
from unittest.mock import MagicMock, call
from pytest_mock import MockerFixture
import requests

import pandas as pd

from backend.environments.api_connectors.kraken_connector import KrakenAPIConnector
from backend.dtos.market.trade_tick import TradeTick
from backend.config.schemas.connectors.kraken_schema import KrakenPublicConfig, KrakenAPIRetryConfig

MOCK_KRAKEN_SUCCESS_RESPONSE = {
    "error": [],
    "result": {
        "XXBTZEUR": [
            ["60000.10", "0.1", 1617225600.1234, "b", "m", ""],
            ["60000.20", "0.05", 1617225601.5678, "s", "l", ""]
        ],
        "last": "1617225601567800000"
    }
}

MOCK_KRAKEN_OHLCV_SUCCESS_RESPONSE = {
    "error": [],
    "result": {
        "XXBTZEUR": [
            [1617225600, "60000.1", "60005.0", "59990.5", "60002.0", "60001.0", "10.5", 150],
            [1617226500, "60002.1", "60010.0", "60000.0", "60008.0", "60007.0", "12.0", 180],
        ],
        "last": 1617226500
    }
}

MOCK_KRAKEN_ERROR_RESPONSE = {
    "error": ["EQuery:Invalid pair"]
}

def test_get_historical_trades_streams_batches_successfully(mocker: MockerFixture):
    """
    Tests if the generator correctly yields all trade batches until the API is exhausted.
    """
    # Arrange
    mock_logger = MagicMock()
    mock_config = KrakenPublicConfig(type='kraken_public')
    mock_response_page1 = MagicMock(json=lambda: MOCK_KRAKEN_SUCCESS_RESPONSE)
    mock_response_page2 = MagicMock(json=lambda: {
        "error": [], "result": {"last": MOCK_KRAKEN_SUCCESS_RESPONSE["result"]["last"]}
    })
    mocker.patch(
        'requests.Session.get', side_effect=[mock_response_page1, mock_response_page2]
    )
    mocker.patch('time.sleep')
    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)

    # Act
    trades_generator = connector.get_historical_trades(pair="XXBTZEUR", since=0)
    all_trades = [trade for batch in list(trades_generator) for trade in batch]

    # Assert
    assert len(all_trades) == 2
    assert all_trades[0].price == 60000.10
    assert requests.Session.get.call_count == 2

def test_get_historical_trades_handles_api_error(mocker: MockerFixture):
    """
    Tests that the generator produces no items if the API returns an error.
    """
    # Arrange
    mock_logger = MagicMock()
    mock_config = KrakenPublicConfig(type='kraken_public')
    mock_response = MagicMock(json=lambda: MOCK_KRAKEN_ERROR_RESPONSE)
    mocker.patch('requests.Session.get', return_value=mock_response)
    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)

    # Act
    trades_generator = connector.get_historical_trades(pair="INVALIDPAIR", since=0)
    all_trades = list(trades_generator) # Consumeer de (lege) generator

    # Assert
    assert all_trades == [] # De generator zou niets moeten yielden
    mock_logger.error.assert_called_once_with(
        "Kraken API error for endpoint '/Trades': ['EQuery:Invalid pair']"
    )


def test_get_historical_trades_respects_time_window(mocker: MockerFixture):
    """
    Tests that the generator stops yielding when the 'until' timestamp is passed.
    """
    # Arrange
    mock_logger = MagicMock()
    mock_config = KrakenPublicConfig(type='kraken_public')
    SINCE_NS = 1000 * 1_000_000_000
    UNTIL_NS = 2000 * 1_000_000_000

    # API geeft 3 trades terug, waarvan de laatste buiten het 'until' venster valt.
    mock_response_data = { "error": [], "result": { "XXBTZEUR": [
        ["1500.0", "1.5", 1500.0, "b", "m", ""], # Binnen venster
        ["2500.0", "2.5", 2500.0, "s", "l", ""]  # Buiten venster
    ], "last": str(2500 * 1_000_000_000) } }
    mocker.patch('requests.Session.get', return_value=MagicMock(json=lambda: mock_response_data))
    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)

    # Act
    trades_generator = connector.get_historical_trades(
        pair="XXBTZEUR", since=SINCE_NS, until=UNTIL_NS
    )
    all_trades = [trade for batch in trades_generator for trade in batch]

    # Assert
    assert len(all_trades) == 1
    assert all_trades[0].price == 1500.0
    # De API wordt maar één keer aangeroepen, omdat de generator stopt na de eerste batch.
    requests.Session.get.assert_called_once()


def test_get_historical_trades_retries_on_network_error(mocker: MockerFixture):
    """
    Tests that the generator functions correctly after the retry logic succeeds.
    """
    # Arrange
    mock_logger = MagicMock()
    mock_config = KrakenPublicConfig(type='kraken_public',retries=KrakenAPIRetryConfig(max_attempts=3, delay_seconds=1))
    mock_success_response = MagicMock(json=lambda: MOCK_KRAKEN_SUCCESS_RESPONSE)
    # Een lege 'stop' response voor de tweede call
    mock_stop_response = MagicMock(json=lambda: {
        "error": [], "result": {"last": MOCK_KRAKEN_SUCCESS_RESPONSE["result"]["last"]}
    })

    # Mock faalt 2x, slaagt dan 2x.
    mocked_get = mocker.patch('requests.Session.get', side_effect=[
        requests.RequestException("Network error 1"),
        requests.RequestException("Network error 2"),
        mock_success_response,
        mock_stop_response
    ])
    mocker.patch('time.sleep')
    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)

    # Act
    trades_generator = connector.get_historical_trades(pair="XXBTZEUR", since=0)
    all_trades = [trade for batch in trades_generator for trade in batch]

    # Assert
    assert len(all_trades) == 2 # Het eindresultaat is correct
    assert mocked_get.call_count == 4 # 2x fail, 1x success, 1x stop-call
    assert mock_logger.error.call_count == 2 # 2x error gelogd

def test_get_historical_ohlcv_streams_batches_successfully(mocker: MockerFixture):
    """
    Tests if the generator-based get_historical_ohlcv correctly yields all
    DataFrame batches until the API is exhausted.
    """
    # Arrange
    mock_logger = MagicMock()
    mock_config = KrakenPublicConfig(type='kraken_public')

    # Mock de API:
    # Pagina 1: Heeft 2 candles en verwijst naar een 'last' timestamp.
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = MOCK_KRAKEN_OHLCV_SUCCESS_RESPONSE

    # Pagina 2: Geeft aan dat er geen nieuwe data is (stop-signaal).
    # De 'last' is hetzelfde als de 'since' die we zouden meegeven.
    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = {
        "error": [],
        "result": {
            "last": MOCK_KRAKEN_OHLCV_SUCCESS_RESPONSE["result"]["last"]
        }
    }

    mocker.patch(
        'requests.Session.get',
        side_effect=[mock_response_page1, mock_response_page2]
    )
    mocker.patch('time.sleep') # Voorkom wachttijd in de test

    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)

    # Act
    # Roep de generator aan.
    ohlcv_generator = connector.get_historical_ohlcv(
        pair="XXBTZEUR", timeframe="15m", since=0
    )

    # Consumeer de generator: verzamel alle yielded DataFrames in een lijst
    # en voeg ze samen tot één grote DataFrame.
    all_dfs = list(ohlcv_generator)
    final_df = pd.concat(all_dfs) if all_dfs else pd.DataFrame()

    # Assert
    assert not final_df.empty
    assert isinstance(final_df, pd.DataFrame)
    assert len(final_df) == 2 # Totaal aantal candles is correct
    assert list(final_df.columns) == [
        "open", "high", "low", "close", "vwap", "volume", "count"
    ]
    assert isinstance(final_df.index, pd.DatetimeIndex)
    assert final_df.index.name == "timestamp"
    assert final_df.iloc[0]['open'] == 60000.1
    assert final_df.iloc[1]['close'] == 60008.0

    # Controleer of de API twee keer is aangeroepen (1x data, 1x stop-call).
    assert requests.Session.get.call_count == 2
