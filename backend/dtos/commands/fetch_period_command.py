# In bestand: backend/dtos/commands/fetch_period_command.py
"""
Contains the Command DTO for fetching a specific historical data period.

@layer: Backend (DTO/Commands)
@dependencies: [pydantic, pandas]
@responsibilities:
    - Defines the data contract for fetching a new, specific period of historical data.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd

class FetchPeriodCommand(BaseModel):
    """
    Data contract for a command to fetch a specific, bounded period of
    historical data. This is typically used to build a new archive or
    manually add a large, specific historical block.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    pair: str = Field(..., description="fetch_period_command.pair.desc")
    start_date: pd.Timestamp = Field(..., description="fetch_period_command.start_date.desc")
    end_date: Optional[pd.Timestamp] = Field(None, description="fetch_period_command.end_date.desc")
