# backend/core/context_recorder.py
"""
Contains the ContextRecorder, a class that acts as a central in-memory database
for storing contextual data produced by various strategy components during a run.

@layer: Backend (Core)
@dependencies: [pydantic, pandas, uuid]
@responsibilities:
    - Provides a single, unified interface for plugins to log contextual data.
    - Stores data in a structured way, indexed by timestamp and plugin name.
    - Serializes Pydantic models into JSON-compatible dictionaries for storage.
"""
import uuid
from typing import Any, Dict
import pandas as pd
from pydantic import BaseModel

class ContextRecorder:
    """A central, in-memory database for recording contextual data from specialists."""

    def __init__(self):
        """Initializes the ContextRecorder with an empty data log."""
        self._data_log: Dict[pd.Timestamp, Dict[str, Any]] = {}

    def add_data(
        self,
        correlation_id: uuid.UUID,
        timestamp: pd.Timestamp,
        specialist_name: str,
        context_object: BaseModel
    ):
        """
        Records a Pydantic context object from a specialist at a specific timestamp.

        The object is immediately serialized to a JSON-compatible dictionary to ensure
        immutability and prevent downstream side effects.

        Args:
            correlation_id (uuid.UUID): The unique ID of the trade lifecycle.
            timestamp (pd.Timestamp): The timestamp of the event to log.
            specialist_name (str): The name of the component logging the data.
            context_object (BaseModel): The Pydantic model with the context data.
        """
        if timestamp not in self._data_log:
            self._data_log[timestamp] = {}

        # Gebruik model_dump() om direct een dictionary te krijgen
        serializable_context = context_object.model_dump()

        # We voegen de correlation_id toe aan de gelogde data voor traceability
        serializable_context['correlation_id'] = str(correlation_id)

        self._data_log[timestamp][specialist_name] = serializable_context

    def get_all_data(self) -> Dict[pd.Timestamp, Dict[str, Any]]:
        """
        Returns the complete, raw data log.

        Returns:
            The nested dictionary containing all recorded context data.
        """
        return self._data_log
