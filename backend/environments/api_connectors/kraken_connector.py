# In bestand: backend/environments/api_connectors/kraken_connector.py
"""
Contains the concrete implementation of an APIConnector for the Kraken exchange.

@layer: Backend (Environment/APIConnectors)
@dependencies: [requests, pydantic, pandas, backend.core.interfaces, backend.dtos]
@responsibilities:
    - Implements the IAPIConnector interface for the Kraken REST API.
    - Fetches raw market data and translates it into application-specific DTOs.
    - Handles API-specific details like pagination, error parsing, and retries.
    - Provides historical trade data as a memory-efficient generator.
"""

import time
from typing import cast, List, Dict, Any, Optional, Generator

import pandas as pd
import requests
from pydantic import ValidationError

from backend.config.schemas.connectors.kraken_schema import KrakenPublicConfig
from backend.core.interfaces.connectors import IAPIConnector
from backend.dtos.market.trade_tick import TradeTick
from backend.utils.app_logger import LogEnricher
from backend.dtos.state.portfolio_state import PortfolioState
from backend.dtos.execution.execution_directive import ExecutionDirective

class KrakenAPIConnector(IAPIConnector):
    """
    A concrete implementation of the IAPIConnector that communicates with the
    public Kraken REST API, providing data as efficient streams.
    """

    def __init__(self, logger: LogEnricher, config: KrakenPublicConfig):
        """Initializes the KrakenAPIConnector.

        Args:
            logger: The application's configured logger instance.
            config: A Pydantic object with the validated configuration for
                this connector instance.
        """
        self.logger = logger
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'S1mpleTraderV2'})

        self._adaptive_delay_sec = 0.2  # Start met een snelle 200ms
        self._min_delay_sec = 0.1       # Ga nooit sneller dan 100ms
        self._max_delay_sec = 5.0       # Wacht maximaal 5 seconden

    def _request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executes a single, robust request to a public Kraken API endpoint.

        This method encapsulates the full retry logic. It will attempt a request
        up to `max_attempts` times, with a configured delay between failures.

        Args:
            endpoint: The API endpoint to call (e.g., "/Trades").
            params: A dictionary of query parameters for the request.

        Returns:
            The JSON response from the API as a dictionary, or an empty
            dictionary if the request ultimately fails.
        """
        attempt = 1
        while attempt <= self.config.retries.max_attempts:
            try:
                # Wacht eerst, zodat we de API nooit bestoken.
                time.sleep(self._adaptive_delay_sec)

                response = self.session.get(
                    f"{self.config.base_url}{endpoint}", params=params, timeout=10
                )
                response.raise_for_status()
                data = cast(Dict[str, Any], response.json())
                api_errors = data.get('error', [])

                # --- DE FIX: Luister naar de feedback in de response body ---
                is_rate_limit_error = any(
                    'EGeneral:Too many requests' in str(err) for err in api_errors
                )

                if is_rate_limit_error:
                    # ---- Rate limited! ----
                    # Verhoog de wachttijd aanzienlijk en probeer het opnieuw.
                    self._adaptive_delay_sec = min(
                        self._max_delay_sec, self._adaptive_delay_sec * 1.5 + 0.1
                    )
                    self.logger.warning(
                        "Rate limited by API. Increasing delay to "
                        f"{self._adaptive_delay_sec:.2f}s."
                    )
                    attempt += 1
                    continue # Ga naar de volgende iteratie van de 'while' lus.
                # ------------------------------------------------------------

                if api_errors:
                    # Een andere, niet-herstelbare API fout.
                    self.logger.error(f"Kraken API error for endpoint '/Trades': {api_errors}")
                    return {} # Stop en geef op.

                # ---- Succes! ----
                # Verlaag de wachttijd lichtjes voor de volgende call.
                self._adaptive_delay_sec = max(
                    self._min_delay_sec, self._adaptive_delay_sec * 0.95
                )
                return data

            except requests.RequestException as e:
                # Een netwerkfout (bv. geen internet).
                self.logger.error(f"Network request failed on attempt {attempt}: {e}")
                attempt += 1
                # Wacht langer bij een netwerkfout voordat je het opnieuw probeert.
                time.sleep(self.config.retries.delay_seconds * attempt)

        self.logger.error("Max retries reached. Aborting request.")
        return {}

    def get_historical_trades(
        self, pair: str, since: int, until: Optional[int] = None
    ) -> Generator[List[TradeTick], None, None]:
        """Fetches historical trades as a stream of batches.

        This method acts as a generator, yielding lists of TradeTick DTOs
        as they are received from the API. This allows the calling service
        to process data in chunks, preventing high memory usage for large
        historical fetches. The internal loop handles pagination automatically
        until the API indicates there is no more recent data.

        Args:
            pair: The trading pair to fetch data for (e.g., 'XXBTZEUR').
            since: The start UNIX timestamp (nanoseconds) to fetch from.
            until: An optional end UNIX timestamp (nanoseconds) to stop at.

        Yields:
            A list of validated TradeTick DTOs representing one batch
            of trades from the API.
        """
        current_since_ns = str(since)
        last_processed_timestamp_ns = since

        while True:
            api_data = self._request(
                "/Trades", params={'pair': pair, 'since': current_since_ns}
            )
            result = cast(Dict[str, Any], api_data.get('result', {}))
            if not result:
                break

            pair_key = next(iter(result.keys()), None)

            raw_trades: List[List[Any]] = []
            if pair_key:
                raw_trades = cast(List[List[Any]], result.get(pair_key, []))

            if not raw_trades:
                break
            if not raw_trades:
                break

            last_api_ts = result.get('last')
            batch_to_yield: List[TradeTick] = []

            for trade_data in raw_trades:
                try:
                    ts_obj = pd.to_datetime(float(trade_data[2]), unit='s', utc=True)
                    ts_ns = int(ts_obj.value)

                    if ts_ns <= last_processed_timestamp_ns:
                        continue  # Skip duplicates from API overlap

                    if until and ts_ns > until:
                        if batch_to_yield:
                            yield batch_to_yield
                        return  # Stop the generator completely

                    tick = TradeTick(
                        price=float(trade_data[0]),
                        volume=float(trade_data[1]),
                        timestamp=ts_obj,
                        side='sell' if trade_data[3] == 's' else 'buy',
                        order_type='market' if trade_data[4] == 'm' else 'limit',
                        misc=str(trade_data[5])
                    )
                    batch_to_yield.append(tick)
                    last_processed_timestamp_ns = ts_ns

                except (ValidationError, IndexError, ValueError) as e:
                    self.logger.warning(
                        f"Skipping invalid trade data: {trade_data}. Error: {e}"
                    )

            if batch_to_yield:
                yield batch_to_yield

            # Kraken's stop-criterion for pagination
            if last_api_ts == current_since_ns:
                break

            current_since_ns = last_api_ts

    def get_historical_ohlcv(
        self,
        pair: str,
        timeframe: str,
        since: int,
        until: Optional[int] = None,
    ) -> Generator[pd.DataFrame, None, None]:
        """Fetches historical OHLCV data as a stream of DataFrame batches.

        This method acts as a generator, yielding pandas DataFrames. This
        allows the calling service to process candlestick data in chunks,
        which is memory-efficient for very large historical data requests.
        The internal loop handles pagination by using the 'last' timestamp
        returned by the Kraken API as the 'since' for the next request.

        Args:
            pair: The trading pair to fetch data for (e.g., 'XXBTZEUR').
            timeframe: The timeframe identifier (e.g., '15m', '1h').
            since: The start UNIX timestamp (nanoseconds) to fetch from.
            until: An optional end UNIX timestamp (nanoseconds) to stop at.

        Yields:
            A pandas DataFrame representing one batch of OHLCV data from the
            API, indexed by a UTC timestamp.

        Raises:
            ValueError: If an unsupported timeframe is provided.
        """
        interval_map = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60, '4h': 240,
            '1d': 1440, '1w': 10080
        }
        interval = interval_map.get(timeframe.lower())
        if interval is None:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        current_since_seconds = str(since // 1_000_000_000)

        while True:
            # FIX (Linter): Geef 'params' een expliciet type.
            params: Dict[str, Any] = {
                'pair': pair, 'interval': interval, 'since': current_since_seconds
            }
            api_data = self._request("/OHLC", params=params)
            result = cast(Dict[str, Any], api_data.get('result', {}))
            if not result:
                break

            pair_key = next(iter(result.keys()), None)
            raw_ohlcv: List[List[Any]] = []
            if pair_key:
                raw_ohlcv = cast(List[List[Any]], result.get(pair_key, []))

            last_api_ts_seconds = result.get('last')

            pair_key = next((key for key in result if key != 'last'), None)

            raw_ohlcv: List[List[Any]] = []
            if pair_key:
                raw_ohlcv = cast(List[List[Any]], result.get(pair_key, []))

            if not raw_ohlcv:
                break

            columns = [
                "timestamp", "open", "high", "low", "close", "vwap", "volume", "count"
            ]
            df_batch = pd.DataFrame(raw_ohlcv, columns=columns)

            df_batch['timestamp'] = pd.to_datetime(
                df_batch['timestamp'], unit='s', utc=True
            )
            df_batch.set_index('timestamp', inplace=True)
            numeric_cols = ["open", "high", "low", "close", "vwap", "volume"]
            df_batch[numeric_cols] = df_batch[numeric_cols].astype(float)
            df_batch['count'] = df_batch['count'].astype(int)

            if until:
                # FIX (Linter): Pylance kent .value niet op een generieke Index.
                # We weten dat het een DatetimeIndex is, dus we negeren de waarschuwing.
                df_batch = df_batch[df_batch.index.value <= until] # type: ignore
                if df_batch.empty: # type: ignore
                    return

            if not df_batch.empty: # type: ignore
                yield df_batch

            if until and df_batch.index.max().value >= until: # type: ignore
                return

            if str(last_api_ts_seconds) == current_since_seconds:
                break

            current_since_seconds = str(last_api_ts_seconds)

    def get_available_pairs(self) -> List[str]:
        raise NotImplementedError("get_available_pairs is not implemented for KrakenAPIConnector")

    def get_portfolio_state(self) -> PortfolioState:
        raise NotImplementedError("get_portfolio_state is not implemented for KrakenAPIConnector")

    def get_open_orders(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("get_open_orders is not implemented for KrakenAPIConnector")

    def place_order(self, directive: ExecutionDirective) -> Dict[str, Any]:
        raise NotImplementedError("place_order is not implemented for KrakenAPIConnector")

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        raise NotImplementedError("cancel_order is not implemented for KrakenAPIConnector")

    def start_market_data_stream(self, pair: str, callback: Any) -> None:
        raise NotImplementedError(
            "start_market_data_stream is not implemented for KrakenAPIConnector")

    def stop_market_data_stream(self) -> None:
        raise NotImplementedError(
            "stop_market_data_stream is not implemented for KrakenAPIConnector")

    def start_user_data_stream(self, callback: Any) -> None:
        raise NotImplementedError(
            "start_user_data_stream is not implemented for KrakenAPIConnector")

    def stop_user_data_stream(self) -> None:
        raise NotImplementedError("stop_user_data_stream is not implemented for KrakenAPIConnector")

    def close(self) -> None:
        """Closes the underlying requests.Session to release connections."""
        self.logger.info(
            'kraken_connector.session_closing',
            values={'connector_type': self.config.type}
        )
        self.session.close()
