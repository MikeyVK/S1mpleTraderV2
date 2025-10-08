# In bestand: backend/config/schemas/connectors/kraken_schema.py
"""
Contains Pydantic models that define the configuration structure for the
KrakenAPIConnector.

@layer: Backend (Config/Schemas)
@dependencies: [pydantic]
"""
from typing import Literal
from pydantic import BaseModel, Field, SecretStr

# --- Gedeelde Sub-modellen ---

class KrakenAPIRetryConfig(BaseModel):
    """Defines the retry strategy for API requests."""
    max_attempts: int = Field(
        default=3, gt=0, description="kraken.retries.max_attempts.desc"
    )
    delay_seconds: int = Field(
        default=2, gt=0, description="kraken.retries.delay_seconds.desc"
    )

# --- DE FIX: Een gezamenlijke basisklasse voor gedeelde velden ---

class KrakenBaseConfig(BaseModel):
    """A base model for shared Kraken configuration fields."""
    retries: KrakenAPIRetryConfig = Field(
        default_factory=KrakenAPIRetryConfig,
        description="kraken.retries.desc"
    )

# --- Specifieke Connector-modellen ---

class KrakenPublicConfig(KrakenBaseConfig):
    """Validation schema for the PUBLIC Kraken API Connector."""
    type: Literal['kraken_public'] = Field(
        ..., description="connectors.definition.type.desc"
    )
    base_url: str = Field(
        default="https://api.kraken.com/0/public",
        description="kraken.public.base_url.desc"
    )

class KrakenPrivateConfig(KrakenBaseConfig):
    """Validation schema for the PRIVATE Kraken API Connector."""
    type: Literal['kraken_private'] = Field(
        ..., description="connectors.definition.type.desc"
    )
    base_url: str = Field(
        default="https://api.kraken.com/0/private",
        description="kraken.private.base_url.desc"
    )
    api_key: SecretStr = Field(..., description="kraken.private.api_key.desc")
    api_secret: SecretStr = Field(..., description="kraken.private.api_secret.desc")
