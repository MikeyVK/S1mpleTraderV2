# In bestand: tests/backend/assembly/test_plugin_registry.py

import yaml
from pathlib import Path
from unittest.mock import MagicMock

from backend.assembly.plugin_registry import PluginRegistry
from backend.config.schemas.platform_schema import PlatformConfig

def test_plugin_registry_discovers_and_validates_plugins(tmp_path: Path):
    """
    Tests if the registry correctly finds valid plugins and ignores invalid ones.
    """
    # Arrange
    plugins_root = tmp_path / "plugins"
    
    # Een valide plugin (nu met de correcte, geneste YAML-structuur)
    valid_plugin_path = plugins_root / "structural_context" / "valid_plugin"
    valid_plugin_path.mkdir(parents=True)
    valid_manifest = {
        "core_identity": {
            "apiVersion": "s1mpletrader.io/v1",
            "kind": "PluginManifest"
        },
        "identification": {
            "name": "valid_plugin",
            "display_name": "Valid Plugin",
            "type": "structural_context",
            "version": "1.0.0",
            "description": "A valid test plugin.",
            "author": "Test Author"
        },
        "dependencies": {"requires": [], "provides": []},
        "permissions": {"network_access": [], "filesystem_access": []}
    }
    with open(valid_plugin_path / "plugin_manifest.yaml", "w") as f:
        yaml.dump(valid_manifest, f)

    # Een plugin met een ongeldig manifest (mist 'identification')
    invalid_plugin_path = plugins_root / "structural_context" / "invalid_plugin"
    invalid_plugin_path.mkdir(parents=True)
    invalid_manifest = {
        "core_identity": {
            "apiVersion": "s1mpletrader.io/v1",
            "kind": "PluginManifest"
        }
    }
    with open(invalid_plugin_path / "plugin_manifest.yaml", "w") as f:
        yaml.dump(invalid_manifest, f)
        
    mock_config = MagicMock(spec=PlatformConfig)
    mock_config.plugins_root_path = str(plugins_root)
    mock_logger = MagicMock()

    # Act
    registry = PluginRegistry(platform_config=mock_config, logger=mock_logger)

    # Assert
    all_manifests = registry.get_all_manifests()
    assert len(all_manifests) == 1, "Should only register the one valid plugin."
    assert "valid_plugin" in all_manifests, "The valid plugin should be registered."
    assert "invalid_plugin" not in all_manifests, "The invalid plugin should be ignored."
    assert mock_logger.warning.call_count > 0, "A warning should be logged for the invalid manifest."
