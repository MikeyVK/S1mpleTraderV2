# In bestand: backend/dtos/queries/coverage_query.py
"""
Contains the Query DTO for a data coverage request.

@layer: Backend (DTO/Queries)
@dependencies: [pydantic]
@responsibilities:
    - Defines the data contract for requesting a data coverage map for a pair.
"""
from pydantic import BaseModel, Field

class CoverageQuery(BaseModel):
    """
    Data contract for a query to retrieve the data coverage map for a
    specific trading pair from the archive.
    """
    pair: str = Field(..., description="coverage_query.pair.desc")
