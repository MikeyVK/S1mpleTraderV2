# In bestand: backend/dtos/commands/fill_gaps_command.py
"""
Contains the Command DTO for a request to fill all gaps in a data archive.

@layer: Backend (DTO/Commands)
@dependencies: [pydantic]
@responsibilities:
    - Defines the data contract for a request to find and fill all gaps in a
      data archive.
"""
from pydantic import BaseModel, Field

class FillGapsCommand(BaseModel):
    """
    Data contract for a command to find and fill all identified gaps in an
    existing historical data archive for a specific pair.
    """
    pair: str = Field(..., description="fill_gaps_command.pair.desc")
