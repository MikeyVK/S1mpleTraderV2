# In bestand: tests/services/test_data_command_service.py
"""
Unit tests for the DataCommandService's interactors.
"""
from unittest.mock import MagicMock, call
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from backend.core.interfaces.connectors import IAPIConnector
from backend.core.interfaces.persistors import IDataPersistor
from backend.assembly.connector_factory import IConnectorFactory
from backend.config.schemas.platform_schema import DataCollectionLimits
from backend.dtos.market.trade_tick import TradeTick
from backend.dtos.commands.fetch_period_command import FetchPeriodCommand
from backend.dtos.commands.synchronization_command import SynchronizationCommand
from backend.dtos.commands.extend_history_command import ExtendHistoryCommand
from backend.dtos.commands.fill_gaps_command import FillGapsCommand
from backend.dtos.market.data_coverage import DataCoverage


# De klasse die we gaan testen
from services.data_command_service import DataCommandService

def test_fetch_period_processes_stream_correctly(mocker: MockerFixture):
    """
    Tests if fetch_period correctly initiates a stream for a bounded
    period and processes the resulting batches.

    Args:
        mocker (MockerFixture): The pytest-mock fixture.
    """
    # Arrange
    PAIR = "BTC/EUR"
    START_DATE = pd.to_datetime("2023-01-01", utc=True)
    END_DATE = pd.to_datetime("2023-01-02", utc=True)
    command = FetchPeriodCommand(pair=PAIR, start_date=START_DATE, end_date=END_DATE)

    mock_persistor = mocker.MagicMock(spec=IDataPersistor)
    mock_persistor.get_last_timestamp.return_value = 0
    mock_logger = mocker.MagicMock()
    mock_limits = DataCollectionLimits(max_history_days=365) # Ruime limiet

    # Mock de connector om een generator terug te geven die 2 batches yield
    batch1 = [TradeTick(price=1.0, volume=1, timestamp=START_DATE, side='buy', order_type='market')]
    batch2 = [TradeTick(price=2.0, volume=2, timestamp=END_DATE, side='buy', order_type='market')]

    def mock_generator():
        yield batch1
        yield batch2

    mock_connector = mocker.MagicMock(spec=IAPIConnector)
    mock_connector.get_historical_trades.return_value = mock_generator()

    mock_factory = mocker.MagicMock(spec=IConnectorFactory)
    mock_factory.get_connector.return_value = mock_connector

    service = DataCommandService(
        persistor=mock_persistor,
        connector=mock_connector,
        logger=mock_logger,
        limits=mock_limits
    )

    # Act
    service.fetch_period(command)

    # Assert
    # 1. Is de juiste connector opgevraagd bij de fabriek?
    mock_factory.get_connector.assert_called_once_with('kraken_public') # Aanname van een default

    # 2. Is de stream correct gestart met de grenzen uit het commando?
    mock_connector.get_historical_trades.assert_called_once_with(
        pair=PAIR,
        since=int(START_DATE.value),
        until=int(END_DATE.value)
    )

    # 3. Zijn BEIDE batches correct opgeslagen door de persistor?
    assert mock_persistor.save_trades.call_count == 2
    expected_calls = [
        mocker.call(pair=PAIR, trades=batch1),
        mocker.call(pair=PAIR, trades=batch2)
    ]
    mock_persistor.save_trades.assert_has_calls(expected_calls)

    # 4. Is de logging correct?
    mock_logger.info.assert_any_call('data_command.fetch_period_start', values={'pair': PAIR})
    mock_logger.info.assert_any_call('data_command.fetch_period_complete', values={'pair': PAIR})

def test_fetch_period_raises_error_if_period_exceeds_max_limit(mocker: MockerFixture):
    """
    Tests that fetch_period correctly validates the requested period against
    the centrally configured safety limit and raises a ValueError if exceeded.
    """
    # --- Arrange ---
    # Stel een strikte limiet in van slechts 30 dagen
    mock_limits = DataCollectionLimits(max_history_days=30)

    # Een request voor 31 dagen aan data, wat de limiet overschrijdt
    start_date_too_far = pd.Timestamp.utcnow() - pd.Timedelta(days=31)
    command = FetchPeriodCommand(
        pair="BTC/EUR",
        start_date=start_date_too_far
    )

    mock_persistor = mocker.MagicMock(spec=IDataPersistor)
    mock_connector = mocker.MagicMock(spec=IAPIConnector)
    mock_logger = mocker.MagicMock()

    # --- Act & Assert ---
    service = DataCommandService(persistor=mock_persistor,
                                 connector_factory=mock_factory,
                                 logger=mock_logger,
                                 limits=mock_limits)

    # We verwachten dat de methode een ValueError gooit met een duidelijke melding
    with pytest.raises(ValueError,
                       match="Requested history of 32 days exceeds the maximum limit of 30 days."):
        service.fetch_period(command=command)

    # Verifieer dat er GEEN calls zijn gedaan naar de connector of persistor
    mock_connector.get_historical_trades.assert_not_called()

def test_synchronize_fetches_and_saves_streamed_data(mocker: MockerFixture):
    """
    Tests if synchronize() correctly processes a stream of new data from
    the connector's generator.

    Args:
        mocker (MockerFixture): The pytest-mock fixture.
    """
    # Arrange
    PAIR = "BTC/EUR"
    LAST_KNOWN_TS_NS = 1_000_000_000 * 1000
    command = SynchronizationCommand(pair=PAIR)

    # --- DE FIX: Mock de huidige tijd ---
    # Zorg ervoor dat de veiligheidscheck slaagt door "nu" in de buurt
    # van de laatste bekende timestamp in te stellen.
    MOCK_NOW = pd.to_datetime(LAST_KNOWN_TS_NS + 5000, unit='ns', utc=True)
    mocker.patch('pandas.Timestamp.utcnow', return_value=MOCK_NOW)
    # ------------------------------------

    mock_persistor = mocker.MagicMock(spec=IDataPersistor)
    mock_persistor.get_last_timestamp.return_value = LAST_KNOWN_TS_NS

    # Mock de connector om een generator terug te geven die één batch yield.
    new_trades_batch = [
        TradeTick(
            price=1.0, volume=1,
            timestamp=pd.to_datetime(LAST_KNOWN_TS_NS + 1, unit='ns', utc=True),
            side='buy', order_type='market'
        ),
    ]

    def mock_generator():
        yield new_trades_batch

    mock_connector = mocker.MagicMock(spec=IAPIConnector)
    mock_connector.get_historical_trades.return_value = mock_generator()

    mock_factory = mocker.MagicMock(spec=IConnectorFactory)
    mock_factory.get_connector.return_value = mock_connector

    mock_logger = mocker.MagicMock()
    mock_limits = DataCollectionLimits()

    service = DataCommandService(
        persistor=mock_persistor,
        connector_factory=mock_factory,
        logger=mock_logger,
        limits=mock_limits
    )

    # Act
    service.synchronize(command)

    # Assert (deze blijven hetzelfde)
    mock_persistor.get_last_timestamp.assert_called_once_with(PAIR)
    mock_factory.get_connector.assert_called_once_with('kraken_public')
    mock_connector.get_historical_trades.assert_called_once_with(
        pair=PAIR, since=LAST_KNOWN_TS_NS, until=None
    )
    mock_persistor.save_trades.assert_called_once_with(
        pair=PAIR, trades=new_trades_batch
    )
    mock_logger.info.assert_any_call(
        'data_command.sync_complete',
        values={'pair': PAIR, 'count': 1}
    )

def test_extend_history_works_backward_from_oldest_point(mocker: MockerFixture):
    """
    Tests if extend_history correctly initiates a stream backward in time
    from the oldest known data point and saves the result.

    Args:
        mocker (MockerFixture): The pytest-mock fixture.
    """
    # Arrange
    PAIR = "ETH/EUR"
    OLDEST_KNOWN_TS = pd.to_datetime("2023-01-15", utc=True)
    DAYS_TO_EXTEND = 5
    command = ExtendHistoryCommand(pair=PAIR, period_days=DAYS_TO_EXTEND)

    # Mock de persistor om onze "oudste" datum terug te geven
    mock_persistor = mocker.MagicMock(spec=IDataPersistor)
    mock_persistor.get_first_timestamp.return_value = int(OLDEST_KNOWN_TS.value)

    # Mock de connector om een generator met een test-batch terug te geven
    new_trades_batch = [
        TradeTick(price=1.0, volume=1, timestamp=OLDEST_KNOWN_TS - pd.Timedelta(days=1), side='buy', order_type='market')
    ]
    def mock_generator():
        yield new_trades_batch
    mock_connector = mocker.MagicMock(spec=IAPIConnector)
    mock_connector.get_historical_trades.return_value = mock_generator()

    mock_factory = mocker.MagicMock(spec=IConnectorFactory)
    mock_factory.get_connector.return_value = mock_connector
   
    mock_logger = mocker.MagicMock()
    # Mock limits om de ValueError te vermijden in de (niet geteste) helpers
    mock_limits = DataCollectionLimits(max_history_days=365)
    
    service = DataCommandService(
        persistor=mock_persistor,
        connector_factory=mock_factory,
        logger=mock_logger,
        limits=mock_limits
    )

    # Act
    service.extend_history(command)

    # Assert
    # 1. Is de oudste timestamp correct opgevraagd?
    mock_persistor.get_first_timestamp.assert_called_once_with(PAIR)
    mock_factory.get_connector.assert_called_once_with('kraken_public')

    # 2. Is de connector aangeroepen met de correcte, terugberekende periode?
    expected_until_ns = int(OLDEST_KNOWN_TS.value) - 1
    expected_start_date = pd.to_datetime(expected_until_ns, unit='ns', utc=True) - pd.Timedelta(days=DAYS_TO_EXTEND)
    expected_since_ns = int(expected_start_date.value)

    mock_connector.get_historical_trades.assert_called_once_with(
        pair=PAIR,
        since=expected_since_ns,
        until=expected_until_ns
    )

    # 3. Is de batch uit de stream correct opgeslagen?
    mock_persistor.save_trades.assert_called_once_with(pair=PAIR, trades=new_trades_batch)

    # 4. Is de gebruiker correct geïnformeerd?
    mock_logger.info.assert_any_call('data_command.extend_history_complete', values={'pair': PAIR})

def test_fill_gaps_fetches_only_missing_data(mocker: MockerFixture):
    """
    Tests if fill_gaps correctly identifies a gap between data blocks and
    fetches only the data required to fill that gap.

    Args:
        mocker (MockerFixture): The pytest-mock fixture.
    """
    # Arrange
    PAIR = "XRP/EUR"
    command = FillGapsCommand(pair=PAIR)

    # Simuleer een datakaart met een gat van 1 minuut
    block1_end = pd.to_datetime("2023-01-01 10:00:00", utc=True)
    block2_start = pd.to_datetime("2023-01-01 10:01:00", utc=True)

    coverage_map = [
        DataCoverage(
            start_time=pd.to_datetime("2023-01-01 09:00:00", utc=True),
            end_time=block1_end,
            trade_count=100
        ),
        DataCoverage(
            start_time=block2_start,
            end_time=pd.to_datetime("2023-01-01 11:00:00", utc=True),
            trade_count=100
        ),
    ]

    mock_persistor = mocker.MagicMock(spec=IDataPersistor)
    mock_persistor.get_data_coverage.return_value = coverage_map

    # De trades die precies in het gat vallen
    missing_trades_batch = [
        TradeTick(price=0.5, volume=1000, timestamp=block1_end + pd.Timedelta(seconds=30), side='buy', order_type='market')
    ]
    def mock_generator():
        yield missing_trades_batch
    mock_connector = mocker.MagicMock(spec=IAPIConnector)
    mock_connector.get_historical_trades.return_value = mock_generator()

    mock_factory = mocker.MagicMock(spec=IConnectorFactory)
    mock_factory.get_connector.return_value = mock_connector

    mock_logger = mocker.MagicMock()
    service = DataCommandService(
        persistor=mock_persistor,
        connector_factory=mock_factory,
        logger=mock_logger,
        limits=mocker.MagicMock() # Niet van toepassing voor deze test
    )

    # Act
    service.fill_gaps(command)

    # Assert
    # 1. Is de datakaart correct opgevraagd?
    mock_persistor.get_data_coverage.assert_called_once_with(PAIR)
    
    mock_factory.get_connector.assert_called_once_with('kraken_public')

    # 2. Is de connector aangeroepen met de PRECIEZE grenzen van het gat?
    expected_since_ns = int(block1_end.value) + 1
    expected_until_ns = int(block2_start.value) - 1

    mock_connector.get_historical_trades.assert_called_once_with(
        pair=PAIR,
        since=expected_since_ns,
        until=expected_until_ns
    )

    # 3. Is de data voor het gat correct opgeslagen?
    mock_persistor.save_trades.assert_called_once_with(
        pair=PAIR, trades=missing_trades_batch
    )

    # 4. Is de logging correct?
    mock_logger.info.assert_any_call('data_command.fill_gaps_complete', values={'pair': PAIR, 'gaps_filled': 1})
