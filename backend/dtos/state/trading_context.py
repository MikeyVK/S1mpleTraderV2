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

from typing import Any, Dict, TYPE_CHECKING

import pandas as pd
from pydantic import BaseModel, ConfigDict, PrivateAttr

from backend.core.context_recorder import ContextRecorder

# Use TYPE_CHECKING to avoid runtime circular imports.
if TYPE_CHECKING:
    from backend.core.interfaces import Tradable

def _new_struct_registry() -> Dict[str, Any]:
    """Typed factory for the structural context registry."""
    return {}

class TradingContext(BaseModel):
    """Container for all shared data available during a single run.

    This object represents the single source of truth for contextual data made
    available to plugins at the time of execution.

    Attributes:
        enriched_df: Fully enriched DataFrame, containing all indicator and context columns.
        portfolio: Reference to the active portfolio object.
        context_recorder: Recorder used to persist detailed context for inspection.
    """

    enriched_df: pd.DataFrame
    portfolio: "Tradable"  # Forward reference to avoid runtime import cycles.
    context_recorder: ContextRecorder

    # Runtime-only registry for complex, non-tabular context data.
    # Not part of the model schema / validation / serialization.
    _structural_context_registry: Dict[str, Any] = PrivateAttr(
        default_factory=_new_struct_registry
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # --- Public API -------------------------------------------------------

    def register_structural_data(self, source_plugin: str, data: Any) -> None:
        """Register a complex, non-tabular data structure for later retrieval.

        Args:
            source_plugin: Identifier of the producing plugin.
            data: Arbitrary, non-tabular structure to store.
        """
        self._structural_context_registry[source_plugin] = data

    def get_structural_data(self, source_plugin: str, default: Any | None = None) -> Any | None:
        """Retrieve previously registered complex data by plugin identifier.

        Args:
            source_plugin: Identifier of the producing plugin.
            default: Value returned if no entry exists (defaults to None).

        Returns:
            The stored data for the given plugin identifier, or `default` if not present.
        """
        return self._structural_context_registry.get(source_plugin, default)

    def has_structural_data(self, source_plugin: str) -> bool:
        """Check whether complex data was registered for the given plugin.

        Args:
            source_plugin: Identifier of the producing plugin.

        Returns:
            True if data is present, False otherwise.
        """
        return source_plugin in self._structural_context_registry
