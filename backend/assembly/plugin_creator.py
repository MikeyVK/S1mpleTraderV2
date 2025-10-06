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
        """Initializes the PluginCreator."""
        self._logger = logger
        self.plugins_root = plugins_root
        # Het pad naar de templates is relatief aan DIT bestand
        self.template_root = Path(__file__).parent / "templates"

        if not self.plugins_root.is_dir():
            self._logger.error(f"Plugins root directory does not exist: {self.plugins_root}")
            raise FileNotFoundError(f"Plugins root directory does not exist: {self.plugins_root}")

        if not self.template_root.is_dir():
            self._logger.error(f"Template directory not found at: {self.template_root}")
            raise FileNotFoundError(f"Template directory not found at: {self.template_root}")

    def create(self, name: str, plugin_type: str) -> bool:
        """Creates a new plugin skeleton from templates."""
        plugin_path = self.plugins_root / plugin_type / name
        tests_path = plugin_path / "tests"

        try:
            self._logger.info(f"Creating plugin '{name}' at: {plugin_path}")
            tests_path.mkdir(parents=True, exist_ok=True)

            # Gecorrigeerde paden voor de template bestanden
            template_files = {
                "manifest.yaml.tpl": plugin_path / "manifest.yaml",
                "schema.py.tpl": plugin_path / "schema.py",
                "worker.py.tpl": plugin_path / "worker.py",
                "context_schema.py.tpl": plugin_path / "context_schema.py",
                "test/test_worker.py.tpl": tests_path / "test_worker.py"
            }

            for template_name, target_path in template_files.items():
                source_path = self.template_root / template_name
                
                if not source_path.is_file():
                    self._logger.error(f"Template file not found: {source_path}")
                    raise FileNotFoundError(f"Template file not found: {source_path}")

                shutil.copy(source_path, target_path)

            self._logger.info(f"Successfully created plugin '{name}'.")
            return True

        except Exception as e:
            self._logger.error(f"Failed to create plugin '{name}': {e}", exc_info=True)
            if plugin_path.exists():
                shutil.rmtree(plugin_path) # Cleanup partial creation
            return False
