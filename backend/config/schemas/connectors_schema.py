# In bestand: backend/config/schemas/connectors_schema.py
"""
Contains Pydantic models that define the structure of the connectors.yaml file.
This schema is the single source of truth for defining and validating all
API connector configurations used by the platform.

@layer: Backend (Config/Schemas)
@dependencies: [pydantic, .connectors.kraken_schema]
"""
from typing import Dict, Union, Annotated
from pydantic import Field, RootModel

from backend.config.schemas.connectors.kraken_schema import (
    KrakenPublicConfig,
    KrakenPrivateConfig,
)

AnyConnectorConfig = Annotated[
    Union[KrakenPublicConfig, KrakenPrivateConfig],
    Field(discriminator="type"),
]

class ConnectorsConfig(RootModel[Dict[str, AnyConnectorConfig]]):
    """
    The root model for the entire connectors.yaml file. It represents a
    dictionary where each key is a unique, user-defined name for a connector
    instance, and the value is its validated configuration.
    """
    root: Dict[str, AnyConnectorConfig]
