# In bestand: tests/services/test_data_query_service.py
"""
Unit tests for the DataQueryService's inquiries.
"""
from unittest.mock import MagicMock
import pandas as pd
from pytest_mock import MockerFixture

# De interfaces die we gaan mocken
from backend.core.interfaces.connectors import IAPIConnector
from backend.core.interfaces.persistors import IDataPersistor

# De DTO's die we nodig hebben voor de commando's en resultaten
from backend.dtos.market.data_coverage import DataCoverage
from backend.dtos.queries.coverage_query import CoverageQuery
from backend.dtos.queries.pairs_query import PairsQuery

# De klasse die we gaan testen (bestaat nog niet in de juiste vorm)
from services.data_query_service import DataQueryService


# --- Mock Helper ---
# Een herbruikbare functie om een mock factory te maken. Dit houdt de tests schoon.
def create_mock_connector_factory(mocker: MockerFixture, connector_name: str, return_value: MagicMock):
    """Creates a mock factory that returns a specific connector mock when asked."""
    factory = mocker.MagicMock()
    # Configureer de mock: als get_connector wordt aangeroepen met 'connector_name',
    # geef dan 'return_value' terug. Anders, geef None terug.
    factory.get_connector.side_effect = lambda name: return_value if name == connector_name else None
    return factory


# --- De Tests ---

def test_get_coverage_calls_persistor_and_returns_data(mocker: MockerFixture):
    """
    Tests if get_coverage correctly calls the persistor's get_data_coverage
    method and returns its data unmodified.
    """
    # Arrange
    PAIR = "BTC/EUR"
    command = CoverageQuery(pair=PAIR)
    mock_coverage_data = [
        DataCoverage(
            start_time=pd.to_datetime("2023-01-01", utc=True),
            end_time=pd.to_datetime("2023-01-02", utc=True),
            trade_count=1000
        )
    ]
    mock_persistor = mocker.MagicMock(spec=IDataPersistor)
    mock_persistor.get_data_coverage.return_value = mock_coverage_data

    # DE FIX: De __init__ van de service verwacht nu ook een connector_factory.
    # We geven een simpele MagicMock mee omdat deze specifieke test die niet gebruikt.
    service = DataQueryService(
        persistor=mock_persistor,
        connector_factory=MagicMock()
    )

    # Act
    result = service.get_coverage(command)

    # Assert
    mock_persistor.get_data_coverage.assert_called_once_with(PAIR)
    assert result == mock_coverage_data


def test_get_pairs_calls_correct_connector_and_returns_data(mocker: MockerFixture):
    """
    Tests if get_pairs uses the factory to get the correct connector and
    returns the available pairs from that connector.
    """
    # Arrange
    EXCHANGE_ID = "kraken_public"
    command = PairsQuery(exchange_id=EXCHANGE_ID)
    mock_pairs_data = ["BTC/EUR", "XRP/EUR"]

    mock_connector = mocker.MagicMock(spec=IAPIConnector)
    mock_connector.get_available_pairs.return_value = mock_pairs_data

    mock_factory = create_mock_connector_factory(mocker, EXCHANGE_ID, mock_connector)

    service = DataQueryService(
        persistor=mocker.MagicMock(spec=IDataPersistor),
        connector_factory=mock_factory
    )

    # Act
    result = service.get_pairs(command)

    # Assert
    mock_factory.get_connector.assert_called_once_with(EXCHANGE_ID)
    mock_connector.get_available_pairs.assert_called_once()
    assert result == mock_pairs_data
