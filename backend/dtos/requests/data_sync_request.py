# In bestand: backend/dtos/requests/data_sync_request.py
"""
Contains the DTO for a data synchronization request.

@layer: Backend (DTO/Requests)
@dependencies: [pydantic]
@responsibilities:
    - Defines the standardized data structure for initiating an incremental
      data synchronization process for a single pair.
"""
from pydantic import BaseModel, Field

class DataSyncRequest(BaseModel):
    """
    A data contract for initiating an incremental data synchronization.
    Ensures the service layer receives a validated, type-safe request.
    """
    pair: str = Field(
        ...,
        description="data_sync_request.pair.desc"
    )
