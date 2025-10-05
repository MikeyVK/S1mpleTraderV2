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

from backend.environments.api_connectors.kraken_connector import KrakenAPIConnector
from backend.dtos.market.trade_tick import TradeTick
from backend.config.schemas.connectors.kraken_schema import KrakenAPIConnectorConfig, KrakenAPIRetryConfig

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

MOCK_KRAKEN_ERROR_RESPONSE = {
    "error": ["EQuery:Invalid pair"]
}


def test_get_historical_trades_success(mocker: MockerFixture):
    mock_logger = MagicMock()
    mock_config = KrakenAPIConnectorConfig()
    
    # Mock de eerste call met data, en de tweede zonder nieuwe data
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = MOCK_KRAKEN_SUCCESS_RESPONSE
    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = {
        "error": [], 
        "result": {
            "XXBTZEUR": [["60000.20", "0.05", 1617225601.5678, "s", "l", ""]],
            "last": MOCK_KRAKEN_SUCCESS_RESPONSE["result"]["last"]
        }
    }
    mocker.patch('requests.Session.get', side_effect=[mock_response_page1, mock_response_page2])
    mocker.patch('time.sleep')

    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)
    trades = connector.get_historical_trades(pair="XXBTZEUR", since=0)

    assert len(trades) == 2
    assert trades[0].price == 60000.10
    assert trades[1].price == 60000.20


def test_get_historical_trades_handles_api_error(mocker: MockerFixture):
    mock_logger = MagicMock()
    mock_config = KrakenAPIConnectorConfig()
    
    mocker.patch('requests.Session.get', return_value=MagicMock(json=MagicMock(return_value=MOCK_KRAKEN_ERROR_RESPONSE)))

    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)
    trades = connector.get_historical_trades(pair="INVALIDPAIR", since=0)

    assert trades == []
    # FIX: De assert controleert nu de correcte, specifiekere foutmelding.
    mock_logger.error.assert_called_once_with("Kraken API error for endpoint '/Trades': ['EQuery:Invalid pair']")


def test_get_historical_trades_respects_time_window(mocker: MockerFixture):
    mock_logger = MagicMock()
    mock_config = KrakenAPIConnectorConfig()
    
    SINCE_NS = 1000 * 1_000_000_000
    UNTIL_NS = 3000 * 1_000_000_000

    # Pagina 1 bevat een valide trade en een trade die we al hebben
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = { "error": [], "result": { "XXBTZEUR": [
        ["1000.0", "1.0", 1000.0, "b", "m", ""], 
        ["1500.0", "1.5", 1500.0, "b", "m", ""]
    ], "last": str(1500 * 1_000_000_000) } }
    
    # Pagina 2 bevat een trade NA het venster
    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = { "error": [], "result": { "XXBTZEUR": [["3500.0", "3.5", 3500.0, "s", "l", ""]], "last": str(3500 * 1_000_000_000) } }

    mock_get = mocker.patch('requests.Session.get', side_effect=[mock_response_page1, mock_response_page2])
    mocker.patch('time.sleep')

    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)
    trades = connector.get_historical_trades(pair="XXBTZEUR", since=SINCE_NS, until=UNTIL_NS)

    assert len(trades) == 1
    assert trades[0].price == 1500.0
    assert mock_get.call_count == 2


def test_get_historical_trades_retries_on_network_error(mocker: MockerFixture):
    mock_logger = MagicMock()
    mock_config = KrakenAPIConnectorConfig(retries=KrakenAPIRetryConfig(max_attempts=3, delay_seconds=1))

    mock_success_response = MagicMock()
    mock_success_response.json.return_value = MOCK_KRAKEN_SUCCESS_RESPONSE
    
    mocked_get = mocker.patch('requests.Session.get', side_effect=[
        requests.RequestException("First network error"),
        requests.RequestException("Second network error"),
        mock_success_response,
        MagicMock(json=MagicMock(return_value={"error": [], "result": {"last": MOCK_KRAKEN_SUCCESS_RESPONSE["result"]["last"]}}))
    ])
    mocker.patch('time.sleep')

    connector = KrakenAPIConnector(logger=mock_logger, config=mock_config)
    trades = connector.get_historical_trades(pair="XXBTZEUR", since=0)

    assert mocked_get.call_count == 4
    assert len(trades) == 2
    assert mock_logger.error.call_count == 2
