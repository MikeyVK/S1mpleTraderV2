# In bestand: tests/services/test_data_query_service.py
"""
Unit tests for the DataQueryService's inquiries.
"""
from unittest.mock import MagicMock
import pandas as pd
from pytest_mock import MockerFixture

# De interfaces die we gaan mocken
from backend.core.interfaces.persistors import IDataPersistor

# De DTO's die we nodig hebben voor de commando's en resultaten
from backend.dtos.market.data_coverage import DataCoverage
from backend.dtos.queries.coverage_query import CoverageQuery

# De klasse die we gaan testen (bestaat nog niet in de juiste vorm)
from services.data_query_service import DataQueryService




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
        persistor=mock_persistor
    )

    # Act
    result = service.get_coverage(command)

    # Assert
    mock_persistor.get_data_coverage.assert_called_once_with(PAIR)
    assert result == mock_coverage_data


