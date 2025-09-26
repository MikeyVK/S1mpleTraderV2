# tests/backend/assembly/test_dependency_validator.py
"""Unit tests for the DependencyValidator."""

from typing import List, Optional
from pathlib import Path
import pytest
from pytest_mock import MockerFixture

from backend.assembly.dependency_validator import DependencyValidator
from backend.assembly.plugin_registry import PluginRegistry
from backend.config.schemas.plugin_manifest_schema import PluginManifest

# CORRECTIE: Type hints toegevoegd voor duidelijkheid en linter.
def create_mock_manifest(
    name: str,
    dependencies: Optional[List[str]] = None,
    provides: Optional[List[str]] = None
) -> PluginManifest:
    """Creates a mock PluginManifest for testing purposes."""
    return PluginManifest(
        name=name, version="1.0", type="structural_context",
        description="A test plugin.",
        entry_class="Dummy", schema_path="dummy.py", params_class="DummyParams",
        dependencies=dependencies or [],
        provides=provides or []
    )

def test_valid_pipeline_succeeds(mocker: MockerFixture):
    """Tests that a logically correct pipeline validates successfully."""
    # Arrange
    mock_registry = mocker.MagicMock(spec=PluginRegistry)
    mock_registry.get_plugin_data.side_effect = {
        "ema_50": (create_mock_manifest("ema_50", ["close"], ["EMA_50"]), Path("path1")),
        "rsi_14": (create_mock_manifest("rsi_14", ["close"], ["RSI_14"]), Path("path2")),
        "logic": (create_mock_manifest("logic", ["EMA_50", "RSI_14"]), Path("path3"))
    }.get

    validator = DependencyValidator(mock_registry)
    pipeline = ["ema_50", "rsi_14", "logic"]

    # Act & Assert
    assert validator.validate(pipeline) is True

def test_pipeline_with_missing_dependency_fails(mocker: MockerFixture):
    """Tests that a pipeline fails if a dependency is never provided."""
    # Arrange
    mock_registry = mocker.MagicMock(spec=PluginRegistry)
    mock_registry.get_plugin_data.side_effect = {
        "ema_50": (create_mock_manifest("ema_50", ["close"], ["EMA_50"]), Path("path1")),
        "logic": (create_mock_manifest("logic", ["COLUMN_THAT_DOES_NOT_EXIST"]), Path("path2"))
    }.get

    validator = DependencyValidator(mock_registry)
    pipeline = ["ema_50", "logic"]

    # Act & Assert
    error_msg = "Dependency 'COLUMN_THAT_DOES_NOT_EXIST' for plugin 'logic' not met."
    with pytest.raises(ValueError, match=error_msg):
        validator.validate(pipeline)

def test_pipeline_with_incorrect_order_fails(mocker: MockerFixture):
    """Tests that a pipeline fails if dependencies are not met due to wrong order."""
    # Arrange
    mock_registry = mocker.MagicMock(spec=PluginRegistry)
    mock_registry.get_plugin_data.side_effect = {
        "logic": (create_mock_manifest("logic", ["EMA_50"]), Path("path1")),
        "ema_50": (create_mock_manifest("ema_50", ["close"], ["EMA_50"]), Path("path2")),
    }.get

    validator = DependencyValidator(mock_registry)
    pipeline = ["logic", "ema_50"]

    # Act & Assert
    with pytest.raises(ValueError, match="Dependency 'EMA_50' for plugin 'logic' not met."):
        validator.validate(pipeline)
