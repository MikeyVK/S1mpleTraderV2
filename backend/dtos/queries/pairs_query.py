# In bestand: backend/dtos/queries/pairs_query.py
"""
Contains the Query DTO for requesting available pairs from a connector.

@layer: Backend (DTO/Queries)
@dependencies: [pydantic]
@responsibilities:
    - Defines the data contract for requesting a list of available trading pairs.
"""
from pydantic import BaseModel, Field

class PairsQuery(BaseModel):
    """
    Data contract for a query to retrieve the list of all available trading
    pairs from a specific, named connector instance.
    """
    exchange_id: str = Field(..., description="pairs_query.exchange_id.desc")
