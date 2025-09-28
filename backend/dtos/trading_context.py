# backend/dtos/trading_context.py
"""
Contains the data class for the TradingContext.

@layer: Backend (DTO)
@dependencies: [pydantic, pandas, backend.core.interfaces]
@responsibilities:
    - Defines a standardized data structure to hold all shared, contextual
      information available during a single run.
"""
from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
import pandas as pd

from backend.core.context_recorder import ContextRecorder

# Gebruik TYPE_CHECKING om de circulaire import tijdens runtime te voorkomen
if TYPE_CHECKING:
    from backend.core.interfaces import Tradable


class TradingContext(BaseModel):
    """
    A container for all shared data available during a single run.
    This object is the single source of truth for the state of the world
    at the time a plugin is executed.

    Attributes:
        enriched_df (pd.DataFrame): The fully enriched DataFrame, containing all
                                    indicator and context columns.
        portfolio (Tradable): A reference to the active portfolio object.
        context_recorder (ContextRecorder): The recorder for logging detailed context.
        structural_context_registry (Dict[str, Any]): A registry for complex,
                                                      non-tabular context data.
    """
    enriched_df: pd.DataFrame
    # --- DE FIX: Gebruik een forward reference (string) voor Tradable ---
    portfolio: "Tradable"
    context_recorder: ContextRecorder
    structural_context_registry: Dict[str, Any] = {}

    def register_structural_data(self, source_plugin: str, data: Any):
        """Allows a plugin to register a complex data structure."""
        self.structural_context_registry[source_plugin] = data

    def get_structural_data(self, source_plugin: str) -> Any | None:
        """Allows a later plugin to retrieve a complex data structure."""
        return self.structural_context_registry.get(source_plugin)

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
