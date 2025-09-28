# tests/backend/assembly/test_worker_builder.py
"""Unit tests for the WorkerBuilder."""

from pathlib import Path
from unittest.mock import MagicMock

from pydantic import BaseModel, ValidationError
from pytest_mock import MockerFixture

from backend.assembly.worker_builder import WorkerBuilder
from backend.assembly.plugin_registry import PluginRegistry

# --- Test Setup: Maak een nep-omgeving ---

class MockParams(BaseModel):
    """Een nep Pydantic-schema voor een plugin."""
    value: int

class MockWorker:
    """Een nep worker-klasse."""
    def __init__(self, name: str, params: MockParams, logger):
        self.name = name
        self.params = params
        self.logger = logger

def test_worker_builder_successfully_builds_worker(mocker: MockerFixture):
    """
    Tests the happy path: building a valid worker with correct parameters.
    """
    # Arrange
    mock_registry = mocker.MagicMock(spec=PluginRegistry)
    mock_logger = mocker.MagicMock()
    
    mock_manifest = mocker.MagicMock(
        params_class="MockParams", entry_class="MockWorker",
        schema_path="schema.py"
    )
    # CORRECTIE: Geef een Path-object terug, geen string.
    mock_registry.get_plugin_data.return_value = (mock_manifest, Path("dummy/path"))
    
    mocker.patch(
        "backend.assembly.worker_builder.load_class_from_module",
        side_effect=[MockParams, MockWorker]
    )
    
    builder = WorkerBuilder(mock_registry, mock_logger)
    
    # Act
    worker_instance = builder.build(name="my_worker", user_params={"value": 123})
    
    # Assert
    assert isinstance(worker_instance, MockWorker)
    assert worker_instance.name == "my_worker"
    assert worker_instance.params.value == 123
    mock_logger.info.assert_called_with("Successfully built worker 'my_worker'.")

def test_worker_builder_fails_on_invalid_params(mocker: MockerFixture):
    """
    Tests if the builder correctly fails when user parameters are invalid.
    """
    # Arrange
    mock_registry = mocker.MagicMock(spec=PluginRegistry)
    mock_logger = mocker.MagicMock()
    
    mock_manifest = mocker.MagicMock(
        params_class="MockParams", entry_class="MockWorker",
        schema_path="schema.py"
    )
    # CORRECTIE: Geef een Path-object terug, geen string.
    mock_registry.get_plugin_data.return_value = (mock_manifest, Path("dummy/path"))

    mocker.patch(
        "backend.assembly.worker_builder.load_class_from_module",
        side_effect=[MockParams, MockWorker]
    )
    
    builder = WorkerBuilder(mock_registry, mock_logger)
    
    # Act
    worker_instance = builder.build(name="my_worker", user_params={"value": "not-an-int"})

    # Assert
    assert worker_instance is None
    mock_logger.error.assert_called_once()
    assert "Invalid parameters for worker 'my_worker'" in mock_logger.error.call_args[0][0]
