# In bestand: backend/dtos/requests/history_build_request.py
"""
Contains the DTO for a history build request.

@layer: Backend (DTO/Requests)
@dependencies: [pydantic, pandas]
@responsibilities:
    - Defines the standardized data structure for initiating a history build process.
"""
from pydantic import BaseModel, ConfigDict, Field
import pandas as pd

class HistoryBuildRequest(BaseModel):
    """
    A data contract for initiating a historical data build process.
    This ensures that the service layer receives a validated, type-safe request.
    """
    pair: str = Field(
        ...,
        description="history_build_request.pair.desc"
    )
    start_date: pd.Timestamp = Field(
        ...,
        description="history_build_request.start_date.desc"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)
