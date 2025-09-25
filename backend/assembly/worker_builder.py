# backend/assembly/worker_builder.py
"""
Contains the WorkerBuilder, responsible for instantiating a single plugin worker
based on its manifest and user-provided configuration.

@layer: Backend (Assembly)
@dependencies:
    - .plugin_registry: To get the manifest (the "blueprint") for a worker.
    - backend.utils.dynamic_loader: To dynamically import plugin code.
    - backend.utils.app_logger: To create and inject a specific logger for the worker.
@responsibilities:
    - Dynamically loads a worker's code and its Pydantic schema.
    - Validates user-provided parameters against the plugin's schema.
    - Injects dependencies (like a logger) into the worker instance.
    - Returns a fully instantiated and validated worker object.
"""
from typing import Any, Dict, Optional, cast

from pydantic import ValidationError

from backend.assembly.plugin_registry import PluginRegistry
from backend.utils.dynamic_loader import load_class_from_module
from backend.utils.app_logger import LogEnricher


class WorkerBuilder:
    """Constructs a single, validated plugin worker instance."""

    def __init__(self, plugin_registry: PluginRegistry, logger: LogEnricher):
        """Initializes the WorkerBuilder.

        Args:
            plugin_registry (PluginRegistry): The registry containing all discovered plugins.
            logger (LogEnricher): The main logger, used to create child loggers.
        """
        self._registry = plugin_registry
        self._logger = logger

    def build(self, name: str, user_params: Dict[str, Any]) -> Optional[Any]:
        """Builds, validates, and instantiates a single worker.

        This method orchestrates the entire lifecycle of creating a worker, from
        finding its definition to validating user input and injecting dependencies.

        Args:
            name (str): The unique name of the worker to build.
            user_params (Dict[str, Any]): The parameter dictionary from the
                                           run_blueprint's 'workforce' section.

        Returns:
            An instantiated and validated worker object if successful, otherwise None.
        """
        # 1. Vraag Manifest en Pad op
        plugin_data = self._registry.get_plugin_data(name)
        if not plugin_data:
            self._logger.error(f"Cannot build worker: plugin '{name}' not found in registry.")
            return None

        manifest, plugin_path = plugin_data

        try:
            # Converteer het file path (bv. "plugins\\signal_generators\\fvg")
            # naar een Python module path (bv. "plugins.signal_generators.fvg")
            plugin_module_path = ".".join(plugin_path.parts)

            # 2. Dynamisch Laden met expliciete paden
            schema_module_path = f"{plugin_module_path}.{manifest.schema_path.replace('.py', '')}"
            worker_module_path = f"{plugin_module_path}.worker"

            schema_class = load_class_from_module(schema_module_path, manifest.params_class)
            worker_class = load_class_from_module(worker_module_path, manifest.entry_class)

            # 3. Valideer Parameters
            validated_params = schema_class(**user_params)

            # 4. Creëer & Injecteer Logger
            # Haal de onderliggende standaard logger op om een child te maken.
            indent_val = self._logger.extra.get('indent', 0) if self._logger.extra else 0
            current_indent = cast(int, indent_val)
            child_logger = self._logger.logger.getChild(name)
            worker_logger = LogEnricher(
                child_logger,
                indent=current_indent + 1
            )

            # 5. Instantieer de Worker
            worker_instance = worker_class(
                name=name,
                params=validated_params,
                logger=worker_logger
            )

            self._logger.info(f"Successfully built worker '{name}'.")
            return worker_instance

        except (ImportError, AttributeError) as e:
            self._logger.error(
                f"Failed to load code for worker '{name}': {e}"
            )
        except ValidationError as e:
            self._logger.error(
                f"Invalid parameters for worker '{name}':\n{e}"
            )

        return None
