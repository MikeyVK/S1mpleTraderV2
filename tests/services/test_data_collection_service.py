# In bestand: tests/services/test_data_collection_service.py
"""
Unit tests for the DataCollectionService.
...
"""
from unittest.mock import MagicMock, call # Zorg dat 'call' is geïmporteerd
import pandas as pd
from pytest_mock import MockerFixture

from backend.core.interfaces.connectors import IAPIConnector
from backend.core.interfaces.persistors import IDataPersistor
from services.data_collection_service import DataCollectionService
from backend.dtos.market.trade_tick import TradeTick
from backend.dtos.requests.history_build_request import HistoryBuildRequest
from backend.dtos.requests.data_sync_request import DataSyncRequest

def test_collection_service_fetches_and_saves_new_trades(mocker: MockerFixture):
    """
    Tests the core incremental update loop using a type-safe request object.
    """
    # --- Arrange ---
    PAIR = "BTC/EUR"
    LAST_KNOWN_TIMESTAMP_NS = int(pd.to_datetime("2023-01-01 10:00:00", utc=True).value)

    # Maak het nieuwe request object aan
    request = DataSyncRequest(pair=PAIR)

    mock_persistor = mocker.MagicMock(spec=IDataPersistor)
    mock_connector = mocker.MagicMock(spec=IAPIConnector)
    mock_logger = mocker.MagicMock()

    mock_persistor.get_last_timestamp.return_value = LAST_KNOWN_TIMESTAMP_NS

    new_trades = [
        TradeTick(price=1.1, volume=5.0, timestamp=pd.to_datetime("2023-01-01 10:01:00", utc=True), side='sell', order_type='limit'),
    ]
    mock_connector.get_historical_trades.return_value = new_trades

    # --- Act ---
    collection_service = DataCollectionService(
        persistor=mock_persistor,
        connector=mock_connector,
        logger=mock_logger
    )
    # Roep de methode aan met het DTO
    collection_service.collect_for_pair(request=request)

    # --- Assert ---
    mock_persistor.get_last_timestamp.assert_called_once_with(request.pair)

    mock_connector.get_historical_trades.assert_called_once_with(
        pair=request.pair,
        since=LAST_KNOWN_TIMESTAMP_NS,
        until=None
    )

    mock_persistor.save_trades.assert_called_once_with(
        pair=request.pair,
        trades=new_trades
    )

    mock_logger.info.assert_called_with(
        'data_collection.sync_complete',
        values={'count': 1, 'pair': request.pair}
    )

def test_build_history_works_backward_in_chunks(mocker: MockerFixture):
    """
    Tests if the history building method works backward in daily chunks,
    using a type-safe request object.
    """
    # --- Arrange ---
    PAIR = "XRP/EUR"
    START_DATE_TS = pd.to_datetime("2025-10-04", utc=True)

    # Maak het request object aan, zoals de API-laag dat zou doen
    request = HistoryBuildRequest(pair=PAIR, start_date=START_DATE_TS)

    MOCK_NOW = pd.to_datetime("2025-10-06 15:00:00", utc=True)
    mocker.patch('pandas.Timestamp.utcnow', return_value=MOCK_NOW)

    mock_persistor = mocker.MagicMock(spec=IDataPersistor)
    mock_connector = mocker.MagicMock(spec=IAPIConnector)
    mock_logger = mocker.MagicMock()

    trades_today = [TradeTick(price=0.55, volume=100, timestamp=MOCK_NOW - pd.Timedelta(hours=5), side='buy', order_type='market')]
    trades_yesterday = [TradeTick(price=0.54, volume=200, timestamp=MOCK_NOW - pd.Timedelta(days=1), side='buy', order_type='market')]
    trades_day_before = [TradeTick(price=0.53, volume=300, timestamp=MOCK_NOW - pd.Timedelta(days=2), side='buy', order_type='market')]

    def get_trades_side_effect(pair, since, until, limit=None):
        if since == int(pd.to_datetime("2025-10-06 00:00:00", utc=True).value): return trades_today
        if since == int(pd.to_datetime("2025-10-05 00:00:00", utc=True).value): return trades_yesterday
        if since == int(pd.to_datetime("2025-10-04 00:00:00", utc=True).value): return trades_day_before
        return []
    mock_connector.get_historical_trades.side_effect = get_trades_side_effect

    # --- Act ---
    collection_service = DataCollectionService(persistor=mock_persistor, connector=mock_connector, logger=mock_logger)
    # Roep de methode aan met het DTO-object
    collection_service.build_history_for_pair(request=request)

    # --- Assert ---
    # De assertions blijven grotendeels hetzelfde, maar gebruiken nu de data uit het request-object
    assert mock_connector.get_historical_trades.call_count == 3
    calls = mock_connector.get_historical_trades.call_args_list
    assert calls[0] == call(pair=request.pair, since=int(pd.to_datetime("2025-10-06 00:00:00", utc=True).value), until=int(MOCK_NOW.value))
    assert calls[1] == call(pair=request.pair, since=int(pd.to_datetime("2025-10-05 00:00:00", utc=True).value), until=int(pd.to_datetime("2025-10-05 23:59:59.999999999", utc=True).value))
    assert calls[2] == call(pair=request.pair, since=int(pd.to_datetime("2025-10-04 00:00:00", utc=True).value), until=int(pd.to_datetime("2025-10-04 23:59:59.999999999", utc=True).value))

    assert mock_persistor.save_trades.call_count == 3
    save_calls = mock_persistor.save_trades.call_args_list
    assert save_calls[0] == call(pair=request.pair, trades=trades_today)
    assert save_calls[1] == call(pair=request.pair, trades=trades_yesterday)
    assert save_calls[2] == call(pair=request.pair, trades=trades_day_before)
