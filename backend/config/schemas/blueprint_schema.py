# backend/config/schemas/blueprint_schema.py
"""
Contains Pydantic models that define the structure of a run_blueprint.yaml file.
This schema defines how a user composes a strategy from available plugins.

@layer: Backend (Config)
@dependencies: [Pydantic]
@responsibilities:
    - Defines the schema for a single strategy configuration.
    - Validates the assignment of plugins to taskboard phases.
    - Validates the parameter definitions for the used plugins.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

class DataConfig(BaseModel):
    """Defines the data settings specific to this run."""
    trading_pair: str
    timeframe: str

class TaskboardConfig(BaseModel):
    """Defines which plugins are assigned to each phase of the 6-phase funnel."""
    regime_filter: List[str] = Field(default_factory=list)
    structural_context: List[str] = Field(default_factory=list)
    signal_generator: List[str] = Field(default_factory=list)
    signal_refiner: List[str] = Field(default_factory=list)
    trade_constructor: List[str] = Field(default_factory=list)
    portfolio_overlay: List[str] = Field(default_factory=list)

class WorkerDefinition(BaseModel):
    """
    Defines the user-provided parameters for a single plugin.
    The system will validate this 'params' dict against the plugin's own schema.py.
    """
    params: Dict[str, Any] = Field(default_factory=dict)

class RunBlueprint(BaseModel):
    """
    The main Pydantic model that validates a complete run_blueprint.yaml file.
    """
    data: DataConfig
    taskboard: TaskboardConfig
    workforce: Dict[str, WorkerDefinition] = Field(default_factory=dict)
