# backend/config/schemas/run_schema.py
"""
Contains Pydantic models that define the structure of a run_schema.yaml file.
This schema defines how a user composes a strategy from available plugins.

@layer: Backend (Config)
@dependencies: [Pydantic]
@responsibilities:
    - Defines the schema for a single strategy configuration.
    - Validates the assignment of plugins to taskboard phases.
    - Validates the parameter definitions for the used plugins.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, RootModel
from backend.core.enums import PipelinePhase

class RunDataConfig(BaseModel):
    """Defines the data settings specific to this run."""
    trading_pair: str
    timeframe: str

class TaskboardConfig(RootModel[Dict[PipelinePhase, List[str]]]):
    """
    Defines which plugins are assigned to each phase.
    This is a flexible dictionary where keys must be valid PipelinePhase members.
    By inheriting from RootModel, this class instance acts directly as a dictionary.
    """

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
    data: RunDataConfig
    taskboard: TaskboardConfig
    workforce: Dict[str, WorkerDefinition] = Field(default_factory=dict)
