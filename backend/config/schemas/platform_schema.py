# backend/config/schemas/platform_schema.py
"""
Contains Pydantic models that define the structure of the platform.yaml file.
This is the foundational contract for the entire application's configuration.

@layer: Backend (Config)
@dependencies: [Pydantic]
@responsibilities:
    - Defines the schema for global, platform-wide settings.
"""

from typing import Literal
from pydantic import BaseModel, Field

class DataConfig(BaseModel):
    """Defines the structure for the 'data' section."""
    source_dir: str = "source_data"

class PortfolioConfig(BaseModel):
    """Defines the structure for the 'portfolio' section."""
    initial_capital: float = 10000.0

class PlatformConfig(BaseModel):
    """
    The main Pydantic model that validates the entire platform.yaml file.
    It defines only the highest-level, essential configurations.
    """
    language: Literal['en', 'nl'] = 'nl'
    plugins_root_path: str = "plugins" # De enige verantwoordelijkheid t.o.v. plugins

    data: DataConfig = Field(default_factory=DataConfig)
    portfolio: PortfolioConfig = Field(default_factory=PortfolioConfig)
