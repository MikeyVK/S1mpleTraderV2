# tests/backend/assembly/test_plugin_creator.py
"""
Unit tests for the PluginCreator service.

@layer: Tests (Backend/Assembly)
@dependencies: [pytest, unittest.mock, backend.assembly.plugin_creator]
@responsibilities:
    - Verify that the plugin skeleton is generated correctly.
    - Ensure all required files are created in the specified location.
    - Confirm that the creator handles file system operations gracefully.
"""

from pathlib import Path
from unittest.mock import MagicMock

from backend.assembly.plugin_creator import PluginCreator

def test_plugin_creator_generates_correct_skeleton(tmp_path: Path):
    """Tests if the create method successfully generates all required files.

    This test uses a mock logger to isolate the PluginCreator from the actual
    logging infrastructure and verifies that appropriate log messages are called.
    
    Args:
        tmp_path (Path): A temporary directory path provided by the pytest fixture.
    """
    # Arrange
    plugins_root = tmp_path
    plugin_name = "my_test_plugin"
    plugin_type = "signal_generator"
    base_path = plugins_root / plugin_type / plugin_name

    expected_files = [
        base_path / "plugin_manifest.yaml",
        base_path / "schema.py",
        base_path / "worker.py",
        base_path / "visualization_schema.py",
        base_path / "tests/test_worker.py",
    ]

    # Maak een mock object aan voor de LogEnricher
    mock_logger = MagicMock()

    # Injecteer de mock logger in de PluginCreator
    creator = PluginCreator(plugins_root=plugins_root, logger=mock_logger)

    # Act
    success = creator.create(name=plugin_name, plugin_type=plugin_type)

    # Assert
    assert success is True
    assert (base_path / "tests").is_dir()
    for file_path in expected_files:
        assert file_path.is_file(), f"File not found: {file_path}"

    # Verifieer dat de logger correct is gebruikt
    mock_logger.info.assert_any_call(f"Creating plugin '{plugin_name}' at: {base_path}")
    mock_logger.info.assert_any_call(f"Successfully created plugin '{plugin_name}'.")
    mock_logger.error.assert_not_called()
