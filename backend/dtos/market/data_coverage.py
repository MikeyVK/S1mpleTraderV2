# In bestand: backend/dtos/market/data_coverage.py
"""
Contains the DTO for representing a contiguous block of historical data.

@layer: Backend (DTO/Market)
@dependencies: [pydantic, pandas]
@responsibilities:
    - Defines the standardized data structure for reporting on the availability
      of historical market data in the persistence layer.
"""
from pydantic import BaseModel, ConfigDict, Field
import pandas as pd

class DataCoverage(BaseModel):
    """
    A data contract representing a single, contiguous block of historical data.

    This DTO is returned by the IDataPersistor's get_data_coverage method to
    provide a clear summary of the available data, which can be used to
    validate backtest ranges or identify gaps in the data history.
    """
    start_time: pd.Timestamp = Field(
        ...,
        description="data_coverage.start_time.desc"
    )
    end_time: pd.Timestamp = Field(
        ...,
        description="data_coverage.end_time.desc"
    )
    trade_count: int = Field(
        ...,
        description="data_coverage.trade_count.desc"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)
