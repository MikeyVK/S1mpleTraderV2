# backend/config/schemas/app_schema.py
"""
Contains the final, composed Pydantic model for a complete application run.

@layer: Backend (Config)
@dependencies: [Pydantic, .platform_schema, .run_schema]
@responsibilities:
    - Composes platform-level and run-level configurations into a single,
      unified, and immutable AppConfig object.
"""
from pydantic import BaseModel
from .platform_schema import PlatformConfig
from .run_schema import RunBlueprint

class AppConfig(BaseModel):
    """
    The final, composed configuration object for a run. It explicitly
    combines platform-wide settings (PlatformConfig) with the blueprint for a
    specific run (RunBlueprint), creating a single source of truth.
    """
    platform: PlatformConfig
    run: RunBlueprint
