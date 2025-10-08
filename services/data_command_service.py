# In bestand: services/data_command_service.py
"""
Contains the DataCommandService, responsible for orchestrating actions
that create, update, or backfill historical market data.

This service acts as the "Interactor" or "Command" layer for data persistence.

@layer: Service
@dependencies: [IAPIConnector, IDataPersistor, LogEnricher, DataCollectionLimits]
"""
from typing import Generator, List
import pandas as pd

from backend.core.interfaces.connectors import IAPIConnector
from backend.core.interfaces.persistors import IDataPersistor
from backend.assembly.connector_factory import IConnectorFactory
from backend.config.schemas.platform_schema import DataCollectionLimits
from backend.dtos.commands import (
    FetchPeriodCommand,
    SynchronizationCommand,
    ExtendHistoryCommand,
    FillGapsCommand
)
from backend.dtos.market.trade_tick import TradeTick
from backend.utils.app_logger import LogEnricher


class DataCommandService:
    """Orchestrates write-actions for the historical data archive."""

    def __init__(
        self,
        persistor: IDataPersistor,
        connector_factory: IConnectorFactory,
        limits: DataCollectionLimits,
        logger: LogEnricher
    ):
        """Initializes the DataCommandService."""
        self._persistor = persistor
        self._connector_factory = connector_factory
        self._limits = limits
        self._logger = logger


    def _get_connector(self, name: str = 'kraken_public') -> IAPIConnector:
        """Helper to get a connector from the factory and handle errors."""
        connector = self._connector_factory.get_connector(name)
        if not connector:
            raise ValueError(f"Failed to get connector '{name}' from factory.")
        return connector

    # --- Private "Motor" ---

    def _process_stream(
        self, pair: str, trades_generator: Generator[List[TradeTick], None, None]
    ) -> int:
        """Processes a stream of trade batches from a generator and saves them.

        This is the central DRY helper for all write operations. It iterates
        over a generator that yields batches of trades, saves each batch
        immediately to the persistence layer, and keeps track of the total
        count of saved trades. This ensures a memory-efficient receive-store
        cycle.

        Args:
            pair: The trading pair being processed.
            trades_generator: A generator yielding lists of TradeTick DTOs.

        Returns:
            The total number of trades processed and saved.
        """
        total_saved_count = 0
        for trades_batch in trades_generator:
            if trades_batch:
                self._persistor.save_trades(pair=pair, trades=trades_batch)
                batch_count = len(trades_batch)
                total_saved_count += batch_count
                self._logger.info(
                    'data_command.chunk_saved_stream',
                    values={'count': batch_count}
                )
        return total_saved_count

    # --- Public "Interactors" (Command Handlers) ---

    def fetch_period(self, command: FetchPeriodCommand) -> None:
        """Fetches a specific, bounded period of historical data idempotently.

        This method is robust against interruptions. Before fetching, it checks
        for the latest existing data point. If the fetch operation is restarted,
        it will automatically resume from the last saved data point, preventing
        duplicate downloads and saving time.

        It validates the requested period against platform limits and then
        initiates a memory-efficient stream of data from the connector,
        processing each batch as it arrives.

        Args:
            command: A DTO containing the 'pair', 'start_date', and optional
                'end_date'.

        Raises:
            ValueError: If the requested date range exceeds the configured
                maximum limit.
        """
        self._logger.info(
            'data_command.fetch_period_start',
            values={'pair': command.pair}
        )
        end_date = command.end_date or pd.Timestamp.utcnow()
        start_date = command.start_date

        # Central validation
        requested_days = (end_date.normalize() - start_date.normalize()).days + 1
        if requested_days > self._limits.max_history_days:
            raise ValueError(
                f"Requested history of {requested_days} days exceeds the "
                f"maximum limit of {self._limits.max_history_days} days."
            )

        last_known_ts_ns = self._persistor.get_last_timestamp(command.pair)
        start_date_ns = int(start_date.value)

        effective_since_ns = max(start_date_ns, last_known_ts_ns)

        trades_generator = self._connector.get_historical_trades(
            pair=command.pair,
            since=effective_since_ns,  # Gebruik het slimme startpunt
            until=int(end_date.value)
        )
        self._process_stream(command.pair, trades_generator)

        self._logger.info(
            'data_command.fetch_period_complete',
            values={'pair': command.pair}
        )

    def synchronize(self, command: SynchronizationCommand) -> None:
        """Synchronizes the data archive with all trades since the last known timestamp.
        
        [... docstring blijft hetzelfde ...]
        """
        self._logger.info(
            'data_command.sync_start',
            values={'pair': command.pair}
        )

        last_ts_ns = self._persistor.get_last_timestamp(command.pair)

        if last_ts_ns == 0:
            self._logger.warning(
                'data_command.sync_failed_no_data',
                values={'pair': command.pair}
            )
            return

        last_ts_date = pd.to_datetime(last_ts_ns, unit='ns', utc=True)
        days_since_last_trade = (pd.Timestamp.utcnow() - last_ts_date).days
        if days_since_last_trade > self._limits.max_history_days:
            raise ValueError(
                f"Archive for pair '{command.pair}' is {days_since_last_trade} "
                f"days old, which exceeds the sync limit of "
                f"{self._limits.max_history_days} days. "
                f"Please use 'fetch_period' to fill the large gap."
            )

        trades_generator = self._connector.get_historical_trades(
            pair=command.pair,
            since=last_ts_ns,
            until=None
        )

        saved_count = self._process_stream(command.pair, trades_generator)

        if saved_count > 0:
            self._logger.info(
                'data_command.sync_complete',
                values={'pair': command.pair, 'count': saved_count}
            )
        else:
            self._logger.info(
                'data_command.archive_is_up_to_date',
                values={'pair': command.pair}
            )

    def extend_history(self, command: ExtendHistoryCommand) -> None:
        """Extends an existing data archive further back in time.

        This method finds the oldest known data point in the archive for a
        given pair and then fetches a specified number of preceding days
        of historical data. It delegates the actual fetching to a generator
        and processes the data via the central `_process_stream` helper,
        ensuring a memory-efficient operation.

        Args:
            command (ExtendHistoryCommand): A DTO containing the trading pair
                and the number of days to extend the history by.
        """
        self._logger.info(
            'data_command.extend_history_start',
            values={'pair': command.pair, 'days': command.period_days}
        )

        oldest_ts_ns = self._persistor.get_first_timestamp(command.pair)

        if oldest_ts_ns == 0:
            self._logger.warning(
                'data_command.extend_failed_no_data',
                values={'pair': command.pair}
            )
            return

        until_ns = oldest_ts_ns - 1
        start_ts = pd.to_datetime(until_ns, unit='ns',
                                  utc=True) - pd.Timedelta(days=command.period_days)
        since_ns = int(start_ts.value)

        self._logger.info(
            'data_command.extending_period',
            values={
                'pair': command.pair,
                'start': start_ts.strftime('%Y-%m-%d'),
                'end': pd.to_datetime(until_ns, unit='ns', utc=True).strftime('%Y-%m-%d')
            }
        )

        trades_generator = self._connector.get_historical_trades(
            pair=command.pair,
            since=since_ns,
            until=until_ns
        )

        self._process_stream(command.pair, trades_generator)

        self._logger.info(
            'data_command.extend_history_complete',
            values={'pair': command.pair}
        )

    def fill_gaps(self, command: FillGapsCommand) -> None:
        """Finds and fills all gaps in an existing data archive.

        This method retrieves a "coverage map" from the data persistor, which
        outlines all contiguous blocks of available data. It then iterates
        through this map, identifies any time periods between the blocks
        (gaps), and initiates a data stream from the connector to fetch only
        the missing data for each gap.

        Args:
            command (FillGapsCommand): A DTO containing the trading pair for
                which to fill data gaps.
        """
        self._logger.info(
            'data_command.fill_gaps_start',
            values={'pair': command.pair}
        )

        coverage_map = self._persistor.get_data_coverage(command.pair)

        # Sorteer de blokken op starttijd voor de zekerheid.
        coverage_map.sort(key=lambda block: block.start_time)

        if len(coverage_map) < 2:
            self._logger.info(
                'data_command.no_gaps_found',
                values={'pair': command.pair}
            )
            return

        gaps_filled = 0
        # Itereer tot de voorlaatste blok om gaten tussen blokken te vinden.
        for i in range(len(coverage_map) - 1):
            block_a = coverage_map[i]
            block_b = coverage_map[i+1]

            gap_start_ns = int(block_a.end_time.value) + 1
            gap_end_ns = int(block_b.start_time.value) - 1

            # Controleer of er daadwerkelijk een gat is.
            if gap_start_ns >= gap_end_ns:
                continue

            gaps_filled += 1
            self._logger.info(
                'data_command.gap_found',
                values={
                    'pair': command.pair,
                    'start': pd.to_datetime(gap_start_ns, unit='ns', utc=True),
                    'end': pd.to_datetime(gap_end_ns, unit='ns', utc=True)
                }
            )

            trades_generator = self._connector.get_historical_trades(
                pair=command.pair,
                since=gap_start_ns,
                until=gap_end_ns
            )

            self._process_stream(command.pair, trades_generator)

        self._logger.info(
            'data_command.fill_gaps_complete',
            values={'pair': command.pair, 'gaps_filled': gaps_filled}
        )
