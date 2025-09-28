# tests/backend/assembly/test_plugin_registry.py
"""Unit tests for the PluginRegistry."""

import yaml
from pathlib import Path
from unittest.mock import MagicMock

from backend.assembly.plugin_registry import PluginRegistry
from backend.config.schemas.platform_schema import PlatformConfig

def test_plugin_registry_discovers_and_validates_plugins(tmp_path: Path):
    """
    Tests if the registry correctly finds valid plugins and ignores invalid ones.
    """
    # Arrange (De Voorbereiding)
    # 1. Maak een tijdelijke, realistische plugin-structuur aan.
    plugins_root = tmp_path / "plugins"
    
    # Een valide plugin
    valid_plugin_path = plugins_root / "structural_context" / "valid_plugin"
    valid_plugin_path.mkdir(parents=True)
    valid_manifest = {
        "name": "valid_plugin", "version": "1.0", "type": "structural_context",
        "description": "A valid test plugin.", "entry_class": "ValidWorker",
        "schema_path": "schema.py", "params_class": "ValidParams"
    }
    with open(valid_plugin_path / "plugin_manifest.yaml", "w") as f:
        yaml.dump(valid_manifest, f)

    # Een plugin met een ongeldig manifest (mist 'type')
    invalid_plugin_path = plugins_root / "structural_context" / "invalid_plugin"
    invalid_plugin_path.mkdir(parents=True)
    invalid_manifest = {"name": "invalid_plugin", "version": "1.0"}
    with open(invalid_plugin_path / "plugin_manifest.yaml", "w") as f:
        yaml.dump(invalid_manifest, f)
        
    # 2. Configureer het systeem om onze tijdelijke map te gebruiken.
    mock_config = MagicMock(spec=PlatformConfig)
    mock_config.plugins_root_path = str(plugins_root)
    mock_logger = MagicMock()

    # Act (De Actie)
    registry = PluginRegistry(platform_config=mock_config, logger=mock_logger)

    # Assert (De Controle)
    all_manifests = registry.get_all_manifests()
    assert len(all_manifests) == 1, "Should only register the one valid plugin."
    assert "valid_plugin" in all_manifests, "The valid plugin should be registered."
    assert "invalid_plugin" not in all_manifests, "The invalid plugin should be ignored."
    
    # Controleer of er een waarschuwing is gelogd voor het ongeldige manifest.
    assert mock_logger.warning.call_count > 0
