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

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Executes a single, robust request to a public Kraken API endpoint,
        including the full retry logic.

        Args:
            endpoint (str): The API endpoint to call (e.g., "/Trades").
            params (Optional[Dict[str, Any]]): A dictionary of query parameters.

        Returns:
            A dictionary with the parsed JSON response on success, or None on failure.
        """
        attempt = 1
        while attempt <= self.config.retries.max_attempts:
            try:
                log_msg = (
                    f"Requesting '{endpoint}' (attempt {attempt}/{self.config.retries.max_attempts})"
                )
                self.logger.info(log_msg)
                response = self.session.get(f"{self.config.base_url}{endpoint}", params=params)
                response.raise_for_status()
                
                data = cast(Dict[str, Any], response.json())
                if data.get('error'):
                    self.logger.error(f"Kraken API error for endpoint '{endpoint}': {data['error']}")
                    return None # API error is a final failure, no retry
                
                return data

            except requests.RequestException as e:
                self.logger.error(f"HTTP Request failed (attempt {attempt}): {e}")
                if attempt == self.config.retries.max_attempts:
                    self.logger.error("Max retries reached. Aborting request.")
                    return None
                time.sleep(self.config.retries.delay_seconds)
                attempt += 1
        return None

    def get_historical_trades(
        self, pair: str, since: int, until: Optional[int] = None, limit: Optional[int] = None
    ) -> List[TradeTick]:
        all_trades: List[TradeTick] = []
        current_since_ns = str(since)

        while True:
            data = self._request("/Trades", params={'pair': pair, 'since': current_since_ns})

            if not data:
                break

            result = cast(Dict[str, Any], data.get('result', {}))
            pair_key = next(iter(result.keys()), None)
            trade_data = cast(List[List[Any]], result.get(pair_key, [])) if pair_key else []

            if not trade_data:
                break
            
            # De 'last' timestamp is de timestamp van de LAATSTE trade in de batch
            last_trade_in_batch_ns = result.get('last')

            for trade in trade_data:
                try:
                    timestamp_obj = pd.to_datetime(float(trade[2]), unit='s', utc=True)
                    trade_timestamp_ns = int(timestamp_obj.value)

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
                except (ValidationError, IndexError, ValueError) as e:
                    self.logger.warning(f"Skipping invalid trade data: {trade}. Error: {e}")
            
            # Waterdichte stop-conditie: als de 'last' niet verandert, stoppen we.
            if last_trade_in_batch_ns == current_since_ns:
                break
            
            current_since_ns = last_trade_in_batch_ns
            time.sleep(1) # Rate limit tussen succesvolle page fetches

        return all_trades
