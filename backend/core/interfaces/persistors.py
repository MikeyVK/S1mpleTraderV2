# In bestand: backend/core/interfaces/persistors.py
"""
Contains the abstract contracts (Protocols) for all data persistence components.

@layer: Backend (Core Interfaces)
@dependencies: [typing, pandas, backend.dtos]
@responsibilities:
    - Defines the universal `IDataPersistor` contract that every data storage
      mechanism (e.g., Parquet, Database) must adhere to.
"""
from typing import Protocol, List
from backend.dtos.market.trade_tick import TradeTick
from backend.dtos.market.data_coverage import DataCoverage

class IDataPersistor(Protocol):
    """
    An interface for any component that can read from and write to a durable
    data storage.
    """
    def get_last_timestamp(self, pair: str) -> int:
        """
        Retrieves the timestamp (in nanoseconds) of the most recently stored
        trade for a given pair. Returns 0 if no data exists.
        """
        ... # pylint: disable=unnecessary-ellipsis
    def save_trades(self, pair: str, trades: List[TradeTick]) -> None:
        """
        Saves a list of TradeTick DTOs to the persistent storage.
        """
        ... # pylint: disable=unnecessary-ellipsis

    def get_data_coverage(self, pair: str) -> List[DataCoverage]:
        """
        Returns a list of contiguous data blocks available for a given pair.
        """
        ... # pylint: disable=unnecessary-ellipsis
