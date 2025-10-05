# backend/core/interfaces/connectors.py
"""
Contains the abstract contracts (Protocols) for all external data connectors.

@layer: Backend (Core Interfaces)
@dependencies: [typing, pandas, backend.dtos]
@responsibilities:
    - Defines the universal `IAPIConnector` contract that every external data
      source (CEX, DEX, wallet) must adhere to.
"""
from typing import Protocol, List, Optional, Any, Dict
import pandas as pd
from backend.dtos.market.trade_tick import TradeTick
from backend.dtos.state.portfolio_state import PortfolioState
from backend.dtos.execution.execution_directive import ExecutionDirective

class IAPIConnector(Protocol):
    """
    An interface for any component that can communicate with an external data
    source.

    This protocol is the cornerstone of the system's agnosticism. It ensures
    that high-level services like the `DataCollectionService` or the
    `LiveEnvironment` can interact with any data source (a CEX via REST, a
    DEX via RPC, or a wallet via CSV) in a consistent, standardized way.
    The interface defines the required methods for both historical data
    retrieval and live trading operations.
    """

    # --- Historical Data Acquisition ---

    def get_historical_trades(self,
                              pair: str,
                              since: int,
                              until: Optional[int] = None,
                              limit: Optional[int] = None) -> List[TradeTick]:
        """
        Fetches a list of historical transactions (ticks) from the data source.

        Args:
            pair (str): The trading pair to fetch data for.
            since (int): The UNIX timestamp (nanoseconds) to start fetching from.
            until (Optional[int]): An optional UNIX timestamp (nanoseconds) to
                                   stop fetching at.
            limit (Optional[int]): An optional limit on the number of trades
                                   to return.

        Returns:
            A list of validated TradeTick DTOs.
        """
        ...

    def get_historical_ohlcv(self,
                             pair: str,
                             timeframe: str,
                             since: int,
                             until: Optional[int] = None,
                             limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches historical OHLCV (candlestick) data from the data source.

        Args:
            pair (str): The trading pair.
            timeframe (str): The timeframe identifier (e.g., '15m', '1h').
            since (int): The UNIX timestamp to start fetching from.
            limit (Optional[int]): An optional limit on the number of candles
                                   to return.

        Returns:
            A pandas DataFrame containing OHLCV data, indexed by timestamp.
        """
        ...

    # --- Real-time Portfolio Management ---

    def get_portfolio_state(self) -> PortfolioState:
        """
        Retrieves the complete, current state of the portfolio from the source.
        
        This is crucial for state reconciliation after a restart or disconnect.
        """
        ...

    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Retrieves a list of all currently open (unfilled) orders."""
        ...

    # --- Real-time Order Management ---

    def place_order(self, directive: ExecutionDirective) -> Dict[str, Any]:
        """
        Places a new order on the exchange based on an ExecutionDirective.
        
        Returns:
            A dictionary containing the response from the exchange, typically
            including the new order's ID.
        """
        ...

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancels an open order based on its unique identifier.
        
        Returns:
            A dictionary containing the response from the exchange.
        """
        ...

    # --- Real-time Data Streams ---

    def start_market_data_stream(self, pair: str, callback: Any) -> None:
        """
        Starts the PUBLIC data stream for market-wide transactions and events.
        
        Args:
            pair (str): The trading pair to subscribe to.
            callback (Any): A callable function that will be invoked with each
                          new piece of market data.
        """
        ...

    def stop_market_data_stream(self) -> None:
        """Stops the active PUBLIC market data stream."""
        ...

    def start_user_data_stream(self, callback: Any) -> None:
        """
        Starts the PRIVATE, authenticated data stream for account-specific
        updates (e.g., order fills, balance changes).
        
        Args:
            callback (Any): A callable function that will be invoked with each
                          new user data event.
        """
        ...

    def stop_user_data_stream(self) -> None:
        """Stops the active PRIVATE user data stream."""
        ...
