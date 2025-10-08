# In bestand: backend/dtos/commands/synchronization_command.py
"""
Contains the Command DTO for a data synchronization action.

@layer: Backend (DTO/Commands)
@dependencies: [pydantic]
@responsibilities:
    - Defines the data contract for initiating an incremental data synchronization.
"""
from pydantic import BaseModel, Field

class SynchronizationCommand(BaseModel):
    """
    Data contract for a command to synchronize a data archive with the
    latest trades since the last known data point.
    """
    pair: str = Field(..., description="synchronization_command.pair.desc")
