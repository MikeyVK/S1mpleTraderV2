# backend/assembly/dependency_validator.py
"""
Contains the DependencyValidator, responsible for ensuring the integrity
of a context pipeline before execution.

@layer: Backend (Assembly)
@dependencies: [.plugin_registry]
@responsibilities:
    - Validates that the data dependencies of each plugin in a sequence are met
      by the outputs of the preceding plugins.
"""
from typing import List
from backend.assembly.plugin_registry import PluginRegistry

class DependencyValidator:
    """Validates the dataflow integrity of a context worker pipeline."""

    def __init__(self, plugin_registry: PluginRegistry):
        """Initializes the DependencyValidator.

        Args:
            plugin_registry (PluginRegistry): The registry to fetch manifests from.
        """
        self._registry = plugin_registry

    def validate(self, context_pipeline: List[str]) -> bool:
        """
        Validates a sequential pipeline of context workers.

        It checks if the `dependencies` of each worker are satisfied by the
        initial `DataFrame` columns or the `provides` of the workers that
        run before it.

        Args:
            context_pipeline (List[str]): An ordered list of context worker names.

        Returns:
            True if the pipeline is valid.

        Raises:
            ValueError: If a dependency is not met, with a descriptive error.
        """
        # Start met de basiskolommen die altijd aanwezig zijn in de ruwe DataFrame.
        available_columns = {"open", "high", "low", "close", "volume"}

        for plugin_name in context_pipeline:
            plugin_data = self._registry.get_plugin_data(plugin_name)
            if not plugin_data:
                raise ValueError(f"Plugin '{plugin_name}' not found in registry.")

            manifest, _ = plugin_data

            # <<< CORRECTIE DEEL 1: Itereer over de 'requires' lijst >>>
            # Controleer de dependencies van de huidige plugin.
            if manifest.dependencies and manifest.dependencies.requires:
                for dep in manifest.dependencies.requires:
                    if dep not in available_columns:
                        raise ValueError(
                            f"Dependency '{dep}' for plugin '{plugin_name}' not met. "
                            f"Available columns: {sorted(list(available_columns))}"
                        )

            # <<< CORRECTIE DEEL 2: Update met de 'provides' lijst >>>
            # Voeg de output van deze plugin toe aan de set van beschikbare kolommen.
            if manifest.dependencies and manifest.dependencies.provides:
                available_columns.update(manifest.dependencies.provides)

        return True
