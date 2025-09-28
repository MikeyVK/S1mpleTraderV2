# tests/backend/core/test_context_recorder.py
"""Unit tests for the ContextRecorder."""

import uuid
from datetime import datetime
import pandas as pd
from pydantic import BaseModel

from backend.core.context_recorder import ContextRecorder

# --- Test Setup ---

class MockContextObject(BaseModel):
    """Een simpele Pydantic-klasse om een context-object te simuleren."""
    value: int
    label: str

# --- De Test ---

def test_context_recorder_adds_and_serializes_data():
    """
    Tests if the ContextRecorder correctly adds data, serializes the Pydantic
    model, and structures the log correctly.
    """
    # Arrange (De Voorbereiding)
    recorder = ContextRecorder()
    
    test_timestamp = pd.to_datetime("2023-01-01 10:00:00", utc=True)
    test_specialist = "my_test_plugin"
    test_context_obj = MockContextObject(value=123, label="test")
    test_corr_id = uuid.uuid4()

    # Act (De Actie)
    # Voeg de data toe aan de recorder. Dit is de methode die we testen.
    recorder.add_data(
        correlation_id=test_corr_id,
        timestamp=test_timestamp,
        specialist_name=test_specialist,
        context_object=test_context_obj
    )

    # Assert (De Controle)
    # 1. Haal alle data op uit de recorder.
    all_data = recorder.get_all_data()

    # 2. Controleer de structuur.
    assert test_timestamp in all_data, "Timestamp should be the primary key."
    assert test_specialist in all_data[test_timestamp], "Specialist name should be the secondary key."

    # 3. Controleer de inhoud.
    logged_context = all_data[test_timestamp][test_specialist]
    
    # Is het Pydantic-object correct omgezet naar een dictionary?
    assert isinstance(logged_context, dict)
    assert logged_context['value'] == 123
    assert logged_context['label'] == "test"
    
    # Is de correlation_id correct toegevoegd?
    assert 'correlation_id' in logged_context
    assert logged_context['correlation_id'] == str(test_corr_id)
