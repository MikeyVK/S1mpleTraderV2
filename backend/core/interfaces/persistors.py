# backend/core/interfaces/persistors.py
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

class IDataPersistor(Protocol):
    """
    An interface for any component that can read from and write to a durable
    data storage.

    This protocol ensures that high-level services, like the
    `DataCollectionService`, can store and retrieve historical market data
    without needing to know the underlying storage technology (e.g., file
    format or database type).
    """

    def get_last_timestamp(self, pair: str) -> int:
        """
        Retrieves the timestamp of the most recently stored trade for a pair.

        This is crucial for the data collection process to know from which
        point in time it should start fetching new data.

        Args:
            pair (str): The trading pair to check.

        Returns:
            The UNIX timestamp (in nanoseconds) of the last known trade,
            or 0 if no data exists for the pair.
        """
        ...

    def save_trades(self, pair: str, trades: List[TradeTick]) -> None:
        """
        Saves a list of TradeTick DTOs to the persistent storage.

        The implementation should handle appending the new data to the
        existing dataset for the given pair.

        Args:
            pair (str): The trading pair the data belongs to.
            trades (List[TradeTick]): The list of TradeTick DTOs to be saved.
        """
        ...
