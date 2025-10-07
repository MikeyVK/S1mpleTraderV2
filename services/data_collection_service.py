# In bestand: services/data_collection_service.py
"""
Contains the DataCollectionService, responsible for orchestrating the process
of fetching and persisting historical market data.

@layer: Service
@dependencies: [IAPIConnector, IDataPersistor, LogEnricher]
@responsibilities:
    - Implements the incremental update loop for daily synchronization.
    - Implements the history building loop to fetch data backward in time.
"""
from typing import Optional
import pandas as pd

from backend.core.interfaces.connectors import IAPIConnector
from backend.core.interfaces.persistors import IDataPersistor
from backend.dtos.requests.data_sync_request import DataSyncRequest
from backend.dtos.requests.history_build_request import HistoryBuildRequest
from backend.utils.app_logger import LogEnricher


class DataCollectionService:
    """
    Orchestrates the data collection workflow by acting as the "manager"
    between a data source (connector) and a data storage layer (persistor).
    """

    def __init__(
        self,
        persistor: IDataPersistor,
        connector: IAPIConnector,
        logger: LogEnricher
    ):
        """Initializes the DataCollectionService with its dependencies.

        Args:
            persistor (IDataPersistor): The component responsible for data storage.
            connector (IAPIConnector): The component for fetching data from an external source.
            logger (LogEnricher): The application's configured logger instance.
        """
        self._persistor = persistor
        self._connector = connector
        self._logger = logger

    def _fetch_and_save_chunk(self, pair: str, since: int, until: Optional[int] = None) -> int:
        """Private helper to fetch and save a single chunk of trade data.

        Args:
            pair (str): The trading pair to process.
            since (int): The start timestamp (nanoseconds) for the data fetch.
            until (Optional[int]): The end timestamp (nanoseconds) for the data fetch.

        Returns:
            int: The number of new trades that were successfully saved.
        """
        trades_chunk = self._connector.get_historical_trades(
            pair=pair, since=since, until=until
        )

        if not trades_chunk:
            return 0

        self._persistor.save_trades(pair=pair, trades=trades_chunk)
        return len(trades_chunk)

    def collect_for_pair(self, request: DataSyncRequest) -> None:
        """Executes an incremental update loop to sync the latest trades.

        This method is designed for frequent execution to keep the data archive
        up-to-date. It finds the last known trade and fetches everything since.

        Args:
            request (DataSyncRequest): A Pydantic DTO containing the 'pair'
                to synchronize.
        """
        self._logger.info('data_collection.sync_start',
                          values={'pair': request.pair})

        last_timestamp_ns = self._persistor.get_last_timestamp(request.pair)

        saved_count = self._fetch_and_save_chunk(pair=request.pair,
                                                 since=last_timestamp_ns, until=None)

        if saved_count > 0:
            self._logger.info('data_collection.sync_complete',
                              values={'count': saved_count, 'pair': request.pair})
        else:
            self._logger.info('data_collection.no_new_data',
                              values={'pair': request.pair})


    def build_history_for_pair(self, request: HistoryBuildRequest) -> None:
        """Builds a historical archive using a type-safe request object.

        This method works backward in daily chunks from the current moment
        until the specified start_date is reached.

        Args:
            request (HistoryBuildRequest): A Pydantic DTO containing the 'pair'
                and 'start_date' for the history build.
        """
        self._logger.info(
            'data_collection.build_history_start',
            values={'pair': request.pair, 'start_date': request.start_date.strftime('%Y-%m-%d')}
        )

        start_ts = request.start_date.normalize()
        current_day = pd.Timestamp.utcnow().normalize()

        while current_day >= start_ts:
            day_str = current_day.strftime('%Y-%m-%d')
            self._logger.info('data_collection.fetching_chunk',
                              values={'pair': request.pair, 'date': day_str})

            chunk_start_ns = int(current_day.value)

            if current_day == pd.Timestamp.utcnow().normalize():
                chunk_end_ns = int(pd.Timestamp.utcnow().value)
            else:
                next_day_start = current_day + pd.Timedelta(days=1)
                chunk_end_ns = int(next_day_start.value - 1)

            saved_count = self._fetch_and_save_chunk(
                pair=request.pair,
                since=chunk_start_ns,
                until=chunk_end_ns
            )

            if saved_count > 0:
                self._logger.info('data_collection.chunk_saved',
                                  values={'count': saved_count, 'date': day_str})
            else:
                self._logger.info('data_collection.no_data_for_chunk', values={'date': day_str})

            current_day -= pd.Timedelta(days=1)

        self._logger.info('data_collection.build_history_complete', values={'pair': request.pair})
