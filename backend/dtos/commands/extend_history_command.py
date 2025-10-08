# In bestand: backend/dtos/commands/extend_history_command.py
"""
Contains the Command DTO for extending the history of an existing data archive.

@layer: Backend (DTO/Commands)
@dependencies: [pydantic]
@responsibilities:
    - Defines the data contract for extending an existing data archive further
      into the past.
"""
from pydantic import BaseModel, Field

class ExtendHistoryCommand(BaseModel):
    """
    Data contract for a command to extend an existing data archive further
    into the past from its oldest known data point.
    """
    pair: str = Field(..., description="extend_history_command.pair.desc")
    period_days: int = Field(..., gt=0, description="extend_history_command.period_days.desc")
