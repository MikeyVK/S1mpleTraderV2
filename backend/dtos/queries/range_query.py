# In bestand: backend/dtos/queries/range_query.py
"""
Contains the Query DTO for requesting historical data within a specific range.

@layer: Backend (DTO/Queries)
@dependencies: [pydantic, pandas]
@responsibilities:
    - Defines the data contract for requesting raw trade data for a specific pair
      and time period.
"""
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd

class RangeQuery(BaseModel):
    """
    Data contract for a query to retrieve raw trade ticks for a specific
    pair and time range from the data archive.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    pair: str = Field(..., description="range_query.pair.desc")
    start_date: pd.Timestamp = Field(..., description="range_query.start_date.desc")
    end_date: pd.Timestamp = Field(..., description="range_query.end_date.desc")
