# In bestand: backend/data/persistors/parquet_persistor.py
"""
Contains the concrete implementation of the IDataPersistor interface using
a partitioned Parquet dataset.
"""
from pathlib import Path
from typing import List, Optional

import pandas as pd
import pyarrow as pa  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from backend.core.interfaces.persistors import IDataPersistor
from backend.dtos.market.data_coverage import DataCoverage
from backend.dtos.market.trade_tick import TradeTick


class ParquetPersistor(IDataPersistor):
    """
    An implementation of IDataPersistor that uses a partitioned Parquet dataset,
    optimizing for performance and scalability with large time-series data.
    """

    def __init__(self, data_dir: Path):
        self._data_dir = data_dir
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def _get_dataset_path(self, pair: str) -> Path:
        """Constructs the root directory path for a given trading pair's dataset."""
        return self._data_dir / pair

    def _read_data(self, pair: str) -> Optional[pd.DataFrame]:
        """Reads a partitioned Parquet dataset for a pair into a single DataFrame."""
        dataset_path = self._get_dataset_path(pair)
        if not dataset_path.is_dir():
            return None
        try:
            dataset = pq.ParquetDataset(dataset_path)
            df: pd.DataFrame = dataset.read().to_pandas()  # type: ignore
            return df if not df.empty else None  # type: ignore
        except (IOError, ValueError, pa.ArrowInvalid):  # type: ignore
            return None

    def get_last_timestamp(self, pair: str) -> int:
        """Efficiently retrieves the last timestamp from a partitioned dataset."""
        dataset_path = self._get_dataset_path(pair)
        if not dataset_path.is_dir():
            return 0
        try:
            dataset = pq.ParquetDataset(dataset_path)
            if not dataset.fragments:  # type: ignore
                return 0

            max_ts = max(frag.metadata.schema.field('timestamp').statistics.max for frag in dataset.fragments)  # type: ignore
            return pd.Timestamp(max_ts).value  # type: ignore
        except (IOError, ValueError, pa.ArrowInvalid, KeyError):  # type: ignore
            return 0

    def save_trades(self, pair: str, trades: List[TradeTick]) -> None:
        """Saves trades to a partitioned Parquet dataset by year and month."""
        if not trades:
            return

        dataset_path = self._get_dataset_path(pair)

        new_df = pd.DataFrame([trade.model_dump() for trade in trades])
        if new_df.empty:
            return

        new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], utc=True)
        new_df['year'] = new_df['timestamp'].dt.year
        new_df['month'] = new_df['timestamp'].dt.month

        table = pa.Table.from_pandas(new_df, preserve_index=False)  # type: ignore

        pq.write_to_dataset( # type: ignore
            table,  # type: ignore
            root_path=dataset_path,
            partition_cols=['year', 'month'],
            existing_data_behavior='overwrite_or_ignore'
        )

    def get_data_coverage(self, pair: str) -> List[DataCoverage]:
        """Analyzes the data file and returns a list of contiguous data blocks."""
        df = self._read_data(pair)
        if df is None:
            return []

        df.sort_values(by='timestamp', inplace=True)

        gap_threshold = pd.Timedelta(seconds=60)
        time_diffs = df['timestamp'].diff()
        gap_indices = df.index[time_diffs > gap_threshold].tolist()

        block_starts = df.index[[0] + gap_indices].tolist()
        block_ends = df.index[[i - 1 for i in gap_indices] + [len(df) - 1]].tolist()

        coverage_blocks: List[DataCoverage] = []
        for start_idx, end_idx in zip(block_starts, block_ends):
            block_df = df.loc[start_idx:end_idx]

            coverage_blocks.append(
                DataCoverage(
                    start_time=block_df['timestamp'].iloc[0],
                    end_time=block_df['timestamp'].iloc[-1],
                    trade_count=len(block_df)
                )
            )

        return coverage_blocks