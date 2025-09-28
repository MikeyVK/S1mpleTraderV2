# backend/environments/backtest_environment.py
"""
Contains the BacktestEnvironment and its specialized sub-components, providing
a complete, isolated world for running historical strategy tests.

@layer: Backend (Environment)
@dependencies: [pandas, backend.core.interfaces, backend.data.loader]
@responsibilities:
    - Implements the BaseEnvironment interface for backtesting.
    - Orchestrates the creation of CSV-based data sources, simulated clocks,
      and backtest execution handlers.
"""
import logging
from pathlib import Path
from typing import Generator, Tuple

import pandas as pd

from backend.config.schemas.app_schema import AppConfig
from backend.core.interfaces import (BaseEnvironment, Clock, DataSource,
                                     ExecutionHandler, Tradable)
from backend.data.loader import DataLoader
from backend.dtos.trade_plan import TradePlan
from backend.utils.app_logger import LogEnricher


# --- Sub-component Implementations ---

class CSVDataSource(DataSource):
    """A data source that loads market data from a CSV file."""

    def __init__(self, app_config: AppConfig, logger: LogEnricher):
        self._logger = logger
        # Pad naar data wordt afgeleid uit de AppConfig
        source_dir = Path(app_config.data.source_dir)
        pair_filename = app_config.data.trading_pair.replace('/', '_')
        filename = f"{pair_filename}_{app_config.data.timeframe}.csv"
        file_path = source_dir / filename
        self._data_loader = DataLoader(str(file_path), self._logger)
        self._data: pd.DataFrame = pd.DataFrame()

    def get_data(self) -> pd.DataFrame:
        """Loads data if not already loaded, then returns it."""
        if self._data.empty:
            self._data = self._data_loader.load()
        return self._data


class SimulatedClock(Clock):
    """A clock that simulates the passage of time by iterating over a DataFrame."""

    def __init__(self, df: pd.DataFrame):
        self._df = df

    def tick(self) -> Generator[Tuple[pd.Timestamp, pd.Series], None, None]:
        """Yields each row of the DataFrame as a moment in time."""
        for timestamp, row in self._df.iterrows():
            assert isinstance(timestamp, pd.Timestamp)
            yield timestamp, row


class BacktestExecutionHandler(ExecutionHandler):
    """An execution handler that simulates trades against a Tradable object."""

    def __init__(self, tradable: Tradable):
        self._tradable = tradable

    def execute_trade(self, trade: TradePlan):
        """Passes the trade plan to the tradable object for simulated execution."""
        self._tradable.open_trade(trade)


# --- Main Environment Class ---

class BacktestEnvironment(BaseEnvironment):
    """
    The concrete implementation of a BaseEnvironment for running backtests.
    """

    def __init__(self, app_config: AppConfig, tradable: Tradable):
        """Initializes the environment and constructs its sub-components."""
        self._logger = LogEnricher(logging.getLogger(__name__))

        # Bouw de gespecialiseerde componenten voor een backtest.
        self._source = CSVDataSource(app_config, self._logger)
        # De Clock heeft de data van de Source nodig.
        self._clock = SimulatedClock(self._source.get_data())
        self._handler = BacktestExecutionHandler(tradable)

    @property
    def source(self) -> DataSource:
        """The data source for this environment."""
        return self._source

    @property
    def clock(self) -> Clock:
        """The clock that controls time in this environment."""
        return self._clock

    @property
    def handler(self) -> ExecutionHandler:
        """The execution handler for this environment."""
        return self._handler
