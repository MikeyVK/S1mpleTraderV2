# backend/environments/api_connectors/kraken_connector.py
"""
Contains the concrete implementation of an APIConnector for the Kraken exchange.

@layer: Backend (Environment/APIConnectors)
@dependencies: [requests, pydantic, pandas, backend.core.interfaces, backend.dtos]
@responsibilities:
    - Implements the IAPIConnector interface for the Kraken REST API.
    - Fetches raw market data and translates it into application-specific DTOs.
    - Handles API-specific details like pagination, error parsing, and retries.
"""
import time
from typing import cast, List, Dict, Any, Optional
import requests
import pandas as pd
from pydantic import ValidationError

from backend.core.interfaces.connectors import IAPIConnector
from backend.dtos.market.trade_tick import TradeTick
from backend.utils.app_logger import LogEnricher
from backend.config.schemas.connectors.kraken_schema import KrakenAPIConnectorConfig

class KrakenAPIConnector(IAPIConnector):
    """
    A concrete implementation of the IAPIConnector interface that communicates
    with the public Kraken REST API.
    """

    def __init__(self, logger: LogEnricher, config: KrakenAPIConnectorConfig):
        self.logger = logger
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'S1mpleTraderV2'})

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a single, robust request to a public Kraken API endpoint,
        including the full retry logic.
        """
        attempt = 1
        while attempt <= self.config.retries.max_attempts:
            try:
                log_msg = (
                    f"Requesting '{endpoint}' (attempt {attempt}/"
                    f"{self.config.retries.max_attempts})"
                )
                self.logger.info(log_msg)
                response = self.session.get(f"{self.config.base_url}{endpoint}", params=params)
                response.raise_for_status()

                data = cast(Dict[str, Any], response.json())
                if data.get('error'):
                    self.logger.error(
                        f"Kraken API error for endpoint '{endpoint}': {data['error']}"
                    )
                    return {}

                return data

            except requests.RequestException as e:
                self.logger.error(f"HTTP Request failed (attempt {attempt}): {e}")
                if attempt == self.config.retries.max_attempts:
                    self.logger.error("Max retries reached. Aborting request.")
                    return {}
                time.sleep(self.config.retries.delay_seconds)
                attempt += 1
        return {}

    def get_historical_trades(
        self, pair: str, since: int, until: Optional[int] = None, limit: Optional[int] = None
    ) -> List[TradeTick]:
        all_trades: List[TradeTick] = []
        current_since_ns = str(since)

        # Hou de timestamp van de allerlaatste trade bij om duplicaten te voorkomen
        last_processed_timestamp_ns = since

        while True:
            data = self._request("/Trades", params={'pair': pair, 'since': current_since_ns})
            result = cast(Dict[str, Any], data.get('result', {}))

            if not result:
                break

            pair_key = next(iter(result.keys()), None)
            trade_data = cast(List[List[Any]], result.get(pair_key, [])) if pair_key else []

            if not trade_data:
                break

            last_api_timestamp_ns = result.get('last')

            for trade in trade_data:
                try:
                    timestamp_obj = pd.to_datetime(float(trade[2]), unit='s', utc=True)
                    trade_timestamp_ns = int(timestamp_obj.value)

                    # **DE ECHTE FIX: Sla trades over die we al hebben verwerkt.**
                    # Dit is de meest robuuste manier om duplicaten te voorkomen.
                    if trade_timestamp_ns <= last_processed_timestamp_ns:
                        continue

                    if until and trade_timestamp_ns > until:
                        return all_trades

                    side = 'sell' if trade[3] == 's' else 'buy'
                    order_type = 'market' if trade[4] == 'm' else 'limit'
                    tick = TradeTick(
                        price=float(trade[0]), volume=float(trade[1]),
                        timestamp=timestamp_obj, side=side,
                        order_type=order_type, misc=str(trade[5])
                    )
                    all_trades.append(tick)

                    # Update de laatst geziene timestamp
                    last_processed_timestamp_ns = trade_timestamp_ns

                except (ValidationError, IndexError, ValueError) as e:
                    self.logger.warning(f"Skipping invalid trade data: {trade}. Error: {e}")

            if last_api_timestamp_ns == current_since_ns:
                break

            current_since_ns = last_api_timestamp_ns
            time.sleep(1)

        return all_trades

    def get_historical_ohlcv(
        self,
        pair: str,
        timeframe: str,
        since: int,
        until: Optional[int] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetches historical OHLCV (candlestick) data from the data source.
        """
        # Kraken API gebruikt 'interval' voor timeframe. Standaard is 1 minuut.
        # We moeten onze timeframe string (bv. '15m') omzetten naar minuten.
        interval_map = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60, '4h': 240, '1d': 1440,
            '1w': 10080
        }
        interval = interval_map.get(timeframe.lower())

        if interval is None:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}. "
                f"Supported values are: {list(interval_map.keys())}"
            )

        params: Dict[str, Any] = {
            'pair': pair,
            'interval': interval,
            'since': since
        }

        data = self._request("/OHLC", params=params)
        result = cast(Dict[str, Any], data.get('result', {}))

        if not result:
            return pd.DataFrame() # Retourneer een lege DataFrame bij geen resultaat

        pair_key = next(iter(result.keys()), None)
        ohlcv_data = cast(List[List[Any]], result.get(pair_key, [])) if pair_key else []

        if not ohlcv_data:
            return pd.DataFrame()

        # Definieer de kolomnamen volgens de Kraken API documentatie
        columns = ["timestamp", "open", "high", "low", "close", "vwap", "volume", "count"]
        df = pd.DataFrame(ohlcv_data, columns=columns)

        # Converteer data naar de juiste types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
        df.set_index('timestamp', inplace=True)

        numeric_columns = ["open", "high", "low", "close", "vwap", "volume"]
        df[numeric_columns] = df[numeric_columns].astype(float)
        df['count'] = df['count'].astype(int)

        return df
