# In bestand: tests/backend/data/test_parquet_persistor.py
"""
Unit tests for the ParquetPersistor implementation.

@layer: Tests (Backend/Data)
@dependencies: [pytest, pandas, pyarrow]
@responsibilities:
    - Verify that trades are correctly saved to a Parquet file.
    - Verify that the last timestamp is correctly retrieved from an existing file.
    - Verify that the component handles non-existent files gracefully.
"""
from pathlib import Path
import pandas as pd
import pytest

from backend.dtos.market.trade_tick import TradeTick
# De klasse die we gaan testen (bestaat nog niet)
from backend.data.persistors.parquet_persistor import ParquetPersistor
from backend.dtos.market.data_coverage import DataCoverage

@pytest.fixture
def sample_trades() -> list[TradeTick]:
    """Provides a list of sample TradeTick DTOs for testing."""
    return [
        TradeTick(price=1.0, volume=10.0, timestamp=pd.to_datetime("2023-01-01 10:00:00", utc=True), side='buy', order_type='market'),
        TradeTick(price=1.1, volume=5.0, timestamp=pd.to_datetime("2023-01-01 10:01:00", utc=True), side='sell', order_type='limit'),
        TradeTick(price=1.2, volume=12.0, timestamp=pd.to_datetime("2023-01-01 10:02:00", utc=True), side='buy', order_type='market'),
    ]

def test_save_trades_and_get_first_and_last_timestamp(tmp_path: Path, sample_trades: list[TradeTick]):
    """
    Tests the core workflow: saving trades and then retrieving the first
    and last timestamps.
    """
    # Arrange
    data_dir = tmp_path
    pair = "BTC_EUR"
    persistor = ParquetPersistor(data_dir=data_dir)
    
    # Test 1: get_first_timestamp en get_last_timestamp voor een niet-bestaande dataset
    assert persistor.get_first_timestamp(pair) == 0, "Should return 0 for first_timestamp if no dataset exists."
    assert persistor.get_last_timestamp(pair) == 0, "Should return 0 for last_timestamp if no dataset exists."

    # Test 2: save_trades
    persistor.save_trades(pair, sample_trades)
    
    expected_dataset_path = data_dir / pair
    assert expected_dataset_path.is_dir(), "Parquet dataset directory should be created."
    
    # Test 3: get_first_timestamp en get_last_timestamp voor een bestaande dataset
    first_ts_ns = sample_trades[0].timestamp.value
    last_ts_ns = sample_trades[-1].timestamp.value

    assert persistor.get_first_timestamp(pair) == first_ts_ns, "Should return the earliest timestamp."
    assert persistor.get_last_timestamp(pair) == last_ts_ns, "Should return the latest timestamp."

def test_get_data_coverage_for_non_existent_file(tmp_path: Path):
    """
    Tests that get_data_coverage returns an empty list for a non-existent pair.
    """
    # Arrange
    persistor = ParquetPersistor(data_dir=tmp_path)

    # Act
    coverage = persistor.get_data_coverage("NON_EXISTENT_PAIR")

    # Assert
    assert coverage == []

def test_get_data_coverage_for_single_block(tmp_path: Path, sample_trades: list[TradeTick]):
    """
    Tests that get_data_coverage correctly identifies a single contiguous block.
    """
    # Arrange
    pair = "BTC_EUR"
    persistor = ParquetPersistor(data_dir=tmp_path)
    persistor.save_trades(pair, sample_trades)

    # Act
    coverage = persistor.get_data_coverage(pair)

    # Assert
    assert len(coverage) == 1
    assert isinstance(coverage[0], DataCoverage)
    assert coverage[0].start_time == sample_trades[0].timestamp
    assert coverage[0].end_time == sample_trades[-1].timestamp
    assert coverage[0].trade_count == len(sample_trades)

def test_get_data_coverage_with_gap(tmp_path: Path):
    """
    Tests that get_data_coverage correctly identifies two separate blocks of data.
    """
    # Arrange
    pair = "ETH_EUR"
    persistor = ParquetPersistor(data_dir=tmp_path)

    trades_part1 = [
        TradeTick(price=1.0, volume=10.0, timestamp=pd.to_datetime("2023-01-01 10:00:00", utc=True), side='buy', order_type='market'),
        TradeTick(price=1.1, volume=5.0, timestamp=pd.to_datetime("2023-01-01 10:01:00", utc=True), side='sell', order_type='limit'),
    ]
    
    # Een "gat" in de data van meer dan een minuut
    trades_part2 = [
        TradeTick(price=1.2, volume=12.0, timestamp=pd.to_datetime("2023-01-01 10:03:00", utc=True), side='buy', order_type='market'),
        TradeTick(price=1.3, volume=8.0, timestamp=pd.to_datetime("2023-01-01 10:04:00", utc=True), side='sell', order_type='limit'),
    ]
    
    persistor.save_trades(pair, trades_part1 + trades_part2)

    # Act
    coverage = persistor.get_data_coverage(pair)

    # Assert
    assert len(coverage) == 2, "Should detect two separate blocks of data."
    
    # Controleer Block 1
    assert coverage[0].start_time == trades_part1[0].timestamp
    assert coverage[0].end_time == trades_part1[-1].timestamp
    assert coverage[0].trade_count == 2
    
    # Controleer Block 2
    assert coverage[1].start_time == trades_part2[0].timestamp
    assert coverage[1].end_time == trades_part2[-1].timestamp
    assert coverage[1].trade_count == 2
