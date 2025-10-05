# backend/dtos/common.py
"""
Bevat de meest basale, herbruikbare DTO's die op meerdere plekken worden gebruikt.

@layer: Backend (DTO)
@dependencies: [pydantic, pandas]
@responsibilities:
    - Definieert de gestandaardiseerde datastructuur voor een enkele transactie (tick).
"""
from __future__ import annotations
from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class TradeTick(BaseModel):
    """
    Een enkele, daadwerkelijk uitgevoerde transactie (Time & Sales),
    gemodelleerd naar de Kraken REST API 'Trades' response.
    """
    model_config = {"arbitrary_types_allowed": True}

    price: float = Field(..., description="De prijs van de transactie.")
    volume: float = Field(
        ..., description="De omvang (volume) van de transactie."
    )
    timestamp: pd.Timestamp = Field(
        ..., description="De exacte UTC timestamp van de transactie."
    )
    side: Literal['buy', 'sell'] = Field(
        ..., description="De kant van de agressor ('buy' of 'sell')."
    )
    order_type: Literal['market', 'limit'] = Field(
        ..., description="Het type order van de agressor ('market' of 'limit')."
    )
    misc: str = Field(
        "", description="Diverse aanvullende informatie van de API."
    )

    @field_validator('timestamp', mode='before')
    @classmethod
    def convert_unix_to_timestamp(cls, v: Any) -> pd.Timestamp:
        """Converteert een UNIX timestamp (in seconden) naar een Pandas Timestamp."""
        if isinstance(v, (int, float)):
            return pd.to_datetime(v, unit='s', utc=True)
        return v
