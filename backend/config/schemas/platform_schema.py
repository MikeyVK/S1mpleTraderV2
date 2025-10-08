# In bestand: backend/config/schemas/platform_schema.py
"""
Contains Pydantic models that define the structure of the platform.yaml file.

This schema defines the global, platform-wide settings and acts as a single
source of truth for the application's core configuration, reflecting the
main architectural layers.

@layer: Backend (Config/Schemas)
@dependencies: [pydantic, backend.core.enums]
"""
from typing import Dict, List, Literal
from pydantic import BaseModel, Field
from backend.core.enums import LogLevel

# --- Sub-models for Logical Grouping ---

class LoggingConfig(BaseModel):
    """Defines the structure for the 'logging' section."""
    profile: Literal['developer', 'analysis'] = Field(
        default='analysis',
        description="platform_config.core.logging.profile.desc"
    )
    profiles: Dict[str, List[LogLevel]] = Field(
        default_factory=dict,
        description="platform_config.core.logging.profiles.desc"
    )

class CoreConfig(BaseModel):
    """Defines core platform settings."""
    language: Literal['en', 'nl'] = Field(
        default='en',
        description="platform_config.core.language.desc"
    )
    plugins_root_path: str = Field(
        default="plugins",
        description="platform_config.core.plugins_root_path.desc"
    )
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

class DataCollectionLimits(BaseModel):
    """Defines safety limits for historical data collection."""
    max_history_days: int = Field(
        default=365 * 5,
        gt=0,
        description="platform_config.services.data_collection.max_history_days.desc"
    )
    warn_history_days: int = Field(
        default=365,
        gt=0,
        description="platform_config.services.data_collection.warn_history_days.desc"
    )

class DataCollectionConfig(BaseModel):
    """Groups all settings related to the DataCollectionService."""
    limits: DataCollectionLimits = Field(default_factory=DataCollectionLimits)

class ServicesConfig(BaseModel):
    """Groups all service-layer configurations."""
    data_collection: DataCollectionConfig = Field(default_factory=DataCollectionConfig)

class DataConfig(BaseModel):
    """Defines settings related to data sources and storage."""
    source_dir: str = Field(
        default="source_data",
        description="platform_config.data.source_dir.desc"
    )

class PortfolioDefaults(BaseModel):
    """Defines the default financial parameters for portfolios."""
    initial_capital: float = Field(
        default=10000.0,
        gt=0,
        description="platform_config.portfolio.defaults.initial_capital.desc"
    )
    fees_pct: float = Field(
        default=0.001,
        ge=0,
        description="platform_config.portfolio.defaults.fees_pct.desc"
    )

class PortfolioConfig(BaseModel):
    """Groups all portfolio-related configurations."""
    defaults: PortfolioDefaults = Field(default_factory=PortfolioDefaults)

# --- Main Platform Configuration Model ---

class PlatformConfig(BaseModel):
    """
    The main Pydantic model that validates the entire platform.yaml file.
    It composes all other configuration models into a logical, hierarchical structure.
    """
    core: CoreConfig = Field(default_factory=CoreConfig)
    services: ServicesConfig = Field(default_factory=ServicesConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    portfolio: PortfolioConfig = Field(default_factory=PortfolioConfig)
