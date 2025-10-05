# backend/dtos/backtest_result.py
"""
Contains the data class for storing the complete result of a single backtest run.

@layer: Backend (DTO)
@dependencies: [pydantic, pandas]
@responsibilities:
    - Defines the standardized data structure for holding all results from a
      single backtest run, ready for analysis and presentation.
"""
from typing import Dict, Any
from pydantic import BaseModel, ConfigDict
import pandas as pd

class BacktestResult(BaseModel):
    """A container for all results of a single backtest run.

    This object acts as a standardized Data Transfer Object (DTO) that holds
    all the essential, aggregated outputs from a backtest analysis, produced
    by the PerformanceAnalyzer.

    Attributes:
        trades_df (pd.DataFrame): A DataFrame containing all ClosedTrade objects.
        equity_curve (pd.Series): A Series representing the portfolio's equity over time.
        drawdown_curve (pd.Series): A Series representing the portfolio's drawdown.
        metrics (Dict[str, Any]): A dictionary of calculated performance metrics.
        initial_capital (float): The starting capital for the run.
    """
    trades_df: pd.DataFrame
    equity_curve: pd.Series
    drawdown_curve: pd.Series
    metrics: Dict[str, Any]
    initial_capital: float

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
