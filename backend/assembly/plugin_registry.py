# backend/assembly/plugin_registry.py
"""
Contains the PluginRegistry, responsible for discovering, validating, and indexing
all available plugins within the ecosystem.

@layer: Backend (Assembly)
@dependencies: [Pydantic, PyYAML, backend.config.schemas]
@responsibilities:
    - Scans plugin directories for manifests.
    - Validates manifest schemas against the PluginManifest contract.
    - Builds and maintains the central in-memory plugin registry.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml

from pydantic import ValidationError
from backend.config.schemas.platform_schema import PlatformConfig
from backend.config.schemas.plugin_manifest_schema import PluginManifest
from backend.utils.app_logger import LogEnricher

class PluginRegistry:
    """
    Discovers all valid plugins and holds their manifest data in an
    in-memory dictionary for fast retrieval by other components.
    """

    def __init__(self, platform_config: PlatformConfig, logger: LogEnricher):
        """
        Initializes the registry by scanning and validating all plugins.

        Args:
            platform_config (PlatformConfig): The validated platform configuration object.
            logger (LogEnricher): The logger instance.
        """
        self._logger = logger
        self._plugins_root_path = Path(platform_config.plugins_root_path)
        self._registry: Dict[str, Tuple[PluginManifest, Path]] = {}

        self._scan_and_register_plugins()

    def _scan_and_register_plugins(self):
        """
        Scans the plugin directory, validates each manifest, and populates the registry.
        """
        self._logger.info(f"Scanning for plugins in '{self._plugins_root_path}'...")

        if not self._plugins_root_path.is_dir():
            self._logger.error(f"Plugin root path '{self._plugins_root_path}' not found.")
            return

        for manifest_path in self._plugins_root_path.rglob("plugin_manifest.yaml"):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = yaml.safe_load(f)

                # Valideer de data tegen ons Pydantic-contract
                manifest = PluginManifest(**manifest_data)

                # Controleer op dubbele namen
                plugin_name = manifest.identification.name

                # Controleer op dubbele namen
                if plugin_name in self._registry:
                    self._logger.warning(
                        f"Duplicate plugin name '{plugin_name}' found at '{manifest_path}'. "
                        "Skipping."
                    )
                    continue

                # Voeg de gevalideerde manifest toe aan de registry
                plugin_directory = manifest_path.parent
                self._registry[plugin_name] = (manifest, plugin_directory)

            except yaml.YAMLError as e:
                self._logger.warning(f"Could not parse manifest at '{manifest_path}': {e}")
            except ValidationError as e:
                self._logger.warning(f"Invalid manifest at '{manifest_path}':\n{e}")

        self._logger.info(
            f"Scan complete. Found and registered {len(self._registry)} valid plugins."
        )

    def get_plugin_data(self, plugin_name: str) -> Optional[Tuple[PluginManifest, Path]]:
        """
        Retrieves the validated manifest for a single plugin by its unique name.

        Args:
            plugin_name (str): The unique name of the plugin.

        Returns:
            Optional[PluginManifest]: The Pydantic model of the manifest, or None if not found.
        """
        return self._registry.get(plugin_name)

    def get_all_manifests(self) -> Dict[str, PluginManifest]:
        """
        Returns the entire registry of validated plugin manifests.

        Returns:
            Dict[str, PluginManifest]: A dictionary of all registered plugins.
        """
        return {name: data[0] for name, data in self._registry.items()}
