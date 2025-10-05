# backend/config/schemas/connectors/kraken_schema.py
"""
Contains Pydantic models that define the configuration structure for the
KrakenAPIConnector.

@layer: Backend (Config/Schemas)
@dependencies: [pydantic]
@responsibilities:
    - Defines and validates all configuration parameters specific to the
      KrakenAPIConnector.
"""
from pydantic import BaseModel, Field

class KrakenAPIRetryConfig(BaseModel):
    """Defines the retry strategy for API requests."""
    max_attempts: int = Field(
        default=3,
        gt=0,
        description="kraken_connector_config.retries.max_attempts.desc"
    )
    delay_seconds: int = Field(
        default=2,
        gt=0,
        description="kraken_connector_config.retries.delay_seconds.desc"
    )

class KrakenAPIConnectorConfig(BaseModel):
    """
    The main Pydantic model that validates the configuration for the
    KrakenAPIConnector.
    """
    base_url: str = Field(
        default="https://api.kraken.com/0/public",
        description="kraken_connector_config.base_url.desc"
    )
    retries: KrakenAPIRetryConfig = Field(
        default_factory=KrakenAPIRetryConfig,
        description="kraken_connector_config.retries.desc"
    )
