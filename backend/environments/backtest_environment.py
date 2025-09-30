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
# --- CORRECTIE: Importeer de JUISTE, GECENTRALISEERDE interfaces ---
from backend.core.interfaces import BaseEnvironment, Clock, DataSource, Tradable
from backend.core.interfaces.execution import ExecutionHandler
from backend.data.loader import DataLoader
from backend.utils.app_logger import LogEnricher
# --- CORRECTIE: Importeer de CONCRETE handler ---
from backend.core.execution import BacktestExecutionHandler


# --- Sub-component Implementations ---
class CSVDataSource(DataSource):
    """A data source that loads market data from a CSV file."""

    def __init__(self, source_dir: str, trading_pair: str, timeframe: str, logger: LogEnricher):
        self._logger = logger
        base_path = Path(source_dir)
        pair_filename = trading_pair.replace('/', '_')
        filename = f"{pair_filename}_{timeframe}.csv"
        file_path = base_path / filename

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

# --- Main Environment Class ---
class BacktestEnvironment(BaseEnvironment):
    """
    The concrete implementation of a BaseEnvironment for running backtests.
    """
    def __init__(self, app_config: AppConfig, tradable: Tradable):
        """Initializes the environment and constructs its sub-components."""
        self._logger = LogEnricher(logging.getLogger(__name__))

        self._source = CSVDataSource(
            source_dir=app_config.platform.data.source_dir,
            trading_pair=app_config.run.data.trading_pair,
            timeframe=app_config.run.data.timeframe,
            logger=self._logger
        )
        self._clock = SimulatedClock(self._source.get_data())
        self._handler = BacktestExecutionHandler(tradable, self._logger)

    @property
    def source(self) -> DataSource:
        return self._source

    @property
    def clock(self) -> Clock:
        return self._clock

    @property
    def handler(self) -> ExecutionHandler:
        return self._handler
