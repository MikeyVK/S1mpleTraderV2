# backend/config/schemas/app_schema.py
"""
Contains the final, composed Pydantic model for the application's configuration.

@layer: Backend (Config)
@dependencies: [Pydantic, .platform_schema, .run_schema]
@responsibilities:
    - Merges platform-level and run-level configurations into a single,
      unified AppConfig object.
"""
from typing import Dict, Any, List

from pydantic import BaseModel

# Importeer de specifieke configuratie-onderdelen die we nodig hebben.
from backend.config.schemas.platform_schema import PlatformDataConfig
from backend.config.schemas.run_schema import RunDataConfig
from backend.core.enums import PipelinePhase

class AppConfigData(PlatformDataConfig, RunDataConfig):
    """A merged data configuration containing fields from both platform and run."""

class AppConfig(BaseModel):
    """
    The final, composed configuration object for a run.
    It combines fields from both PlatformConfig and Runrun into a
    single, definitive structure.
    """
    # Velden van PlatformConfig (behalve 'data')
    language: str
    plugins_root_path: str
    portfolio: Dict[str, Any]
    logging: Dict[str, Any]

    # Velden van Runrun (behalve 'data')
    taskboard: Dict[PipelinePhase, List[str]]
    workforce: Dict[str, Any]

    # Het samengevoegde 'data' veld
    data: AppConfigData
