# plugins/structural_context/ema_detector/worker.py
"""
Contains the main logic for the EmaDetector plugin.

@layer: Plugin
@dependencies: [pandas, backend.core.interfaces]
@responsibilities:
    - Implements the ContextWorker interface.
    - Calculates an EMA based on the provided period.
    - Adds the calculated EMA as a new column to the DataFrame.
"""
import pandas as pd

from backend.core.interfaces import ContextWorker
from backend.dtos import TradingContext
from backend.utils.app_logger import LogEnricher

from .schema import EmaDetectorParams


class EmaDetector(ContextWorker):
    """
    A context worker that calculates and adds an EMA column to a DataFrame.
    """

    def __init__(self, name: str, params: EmaDetectorParams, logger: LogEnricher):
        """
        Initializes the EmaDetector.

        Args:
            name (str): The unique name of this worker instance.
            params (EmaDetectorParams): A Pydantic object with validated parameters.
            logger (LogEnricher): The pre-configured logger instance.
        """
        self.name = name
        self.params = params
        self.logger = logger
        self.column_name = f"ema_{self.params.period}"

    # pylint: disable=unused-argument, arguments-differ
    def process(self, df: pd.DataFrame, context: TradingContext) -> pd.DataFrame:
        """
        Calculates the EMA and adds it as a new column to the DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame with OHLCV data.
            context (TradingContext): The trading context (not used by this worker).

        Returns:
            pd.DataFrame: The DataFrame with the new EMA column added.
        """
        if self.column_name in df.columns:
            return df

        self.logger.info(
            "Calculating EMA with period %s...", self.params.period
        )
        df[self.column_name] = df['close'].ewm(
            span=self.params.period,
            adjust=False
        ).mean()

        return df
