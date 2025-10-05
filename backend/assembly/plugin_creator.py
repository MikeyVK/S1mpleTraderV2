# backend/assembly/plugin_creator.py
"""
Contains the PluginCreator, a service for generating plugin boilerplate code.

@layer: Backend (Assembly)
@dependencies: [pathlib, backend.utils.app_logger]
@responsibilities:
    - Creates the directory structure for a new plugin.
    - Generates all required files from templates (manifest, worker, etc.).
    - Provides a simple interface for creating new plugins.
"""

from pathlib import Path
import shutil
from backend.utils.app_logger import LogEnricher

class PluginCreator:
    """
    A service class responsible for creating the boilerplate structure for a new plugin.
    It uses template files to generate the necessary Python and YAML files.
    """

    def __init__(self, plugins_root: Path, logger: LogEnricher):
        """Initializes the PluginCreator.

        Args:
            plugins_root (Path): The root directory where all plugins are stored.
            logger (LogEnricher): The logger instance, passed via dependency injection.
        """
        self._logger = logger
        self.plugins_root = plugins_root
        self.template_root = Path(__file__).parent / "templates"

        if not self.plugins_root.is_dir():
            self._logger.error(f"Plugins root directory does not exist: {self.plugins_root}")
            raise FileNotFoundError(f"Plugins root directory does not exist: {self.plugins_root}")

        if not self.template_root.is_dir():
            self._logger.error(f"Template directory not found at: {self.template_root}")
            raise FileNotFoundError(f"Template directory not found at: {self.template_root}")

    def create(self, name: str, plugin_type: str) -> bool:
        """Creates a new plugin skeleton from templates.

        Args:
            name (str): The name of the new plugin (e.g., "my_test_plugin").
            plugin_type (str): The type of the plugin (e.g., "signal_generator").

        Returns:
            bool: True if creation was successful, False otherwise.
        """
        plugin_path = self.plugins_root / plugin_type / name
        tests_path = plugin_path / "tests"

        try:
            self._logger.info(f"Creating plugin '{name}' at: {plugin_path}")
            tests_path.mkdir(parents=True, exist_ok=True)

            template_files = {
                "manifest.yaml.tpl": "plugin_manifest.yaml",
                "schema.py.tpl": "schema.py",
                "worker.py.tpl": "worker.py",
                "visualization_schema.py.tpl": "visualization_schema.py",
                "test/test_worker.py.tpl": "tests/test_worker.py"
            }

            for template_name, target_name in template_files.items():
                source_path = self.template_root / template_name
                target_path = plugin_path / target_name

                # TODO: Implement actual template rendering (e.g., with Jinja2)
                # For now, we are just copying the files.
                shutil.copy(source_path, target_path)

            self._logger.info(f"Successfully created plugin '{name}'.")
            return True

        except Exception as e:
            self._logger.error(f"Failed to create plugin '{name}': {e}", exc_info=True)
            if plugin_path.exists():
                shutil.rmtree(plugin_path) # Cleanup partial creation
            return False
