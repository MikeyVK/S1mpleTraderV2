# backend/config/schemas/platform_schema.py
"""
Contains Pydantic models that define the structure of the platform.yaml file.
This is the foundational contract for the entire application's configuration.

@layer: Backend (Config)
@dependencies: [Pydantic]
@responsibilities:
    - Defines the schema for global, platform-wide settings.
"""

# --- Sub-models ---

from typing import Dict, List, Literal
from pydantic import BaseModel, Field
from backend.core.enums import LogLevel

class PlatformDataConfig(BaseModel):
    """Defines the structure for the 'data' section."""
    source_dir: str = "source_data"

class PortfolioConfig(BaseModel):
    """Defines the structure for the 'portfolio' section."""
    initial_capital: float = 10000.0
    fees_pct: float = 0.001

class LoggingConfig(BaseModel):
    """Defines the structure for the 'logging' section."""
    profile: Literal['developer', 'analysis'] = 'analysis'
    profiles: Dict[str, List[LogLevel]] # Gebruikt de LogLevel Enum

# --- Main model ---

class PlatformConfig(BaseModel):
    """
    The main Pydantic model that validates the entire platform.yaml file.
    It defines only the highest-level, essential configurations.
    """
    language: Literal['en', 'nl'] = 'nl'
    plugins_root_path: str = "plugins" # De enige verantwoordelijkheid t.o.v. plugins

    data: PlatformDataConfig = Field(default_factory=PlatformDataConfig)
    portfolio: PortfolioConfig = Field(default_factory=PortfolioConfig)
